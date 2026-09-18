"""Local-only timed review interface. References and model identities are never served."""
import html, json, secrets, sys, urllib.parse
from http.server import BaseHTTPRequestHandler, HTTPServer
from experiment import BASE, read, write, now, assert_frozen, active_seconds

def escape(x):return html.escape(str(x))
def response_display(record,raw):
    obj=record.get('response')
    return json.dumps(obj,ensure_ascii=False,indent=2) if obj is not None else raw
def material(base,item,record,pathway,reveal=False):
    inp=read(base/f"inputs/{item['case_id']}.json")
    parts=['<h2>Scenario</h2>']+['<p>'+escape(s).replace('\n','<br>')+'</p>' for s in inp['scenario']]
    parts+=['<h2>Task</h2><p>'+escape(inp['requested_task'])+'</p>','<h2>Policy evidence</h2><pre>'+escape('\n'.join(inp['source_locators'])+'\n'+inp['source_excerpt'])+'</pre>']
    if item['pathway']=='controlled':parts+=['<h2>Control decision</h2><p>'+escape(pathway['decision'])+'</p><pre>'+escape(json.dumps(pathway['trace'],ensure_ascii=False,indent=2))+'</pre>']
    hidden=item['pathway']=='controlled' and pathway['decision'] in ['block','route'] and not reveal
    if hidden:parts+=['<p>The withheld answer is hidden. Inspecting it must be logged using the button below.</p>']
    else:
        key=next(k for k in read(base/'private/identity_key.json') if k['run_id']==item['run_id'])
        text=response_display(record,(base/key['raw_txt']).read_text()) if record['record_status']=='RECEIVED' else 'No response available.'
        parts+=['<h2>Original response</h2><pre>'+escape(text)+'</pre>']
    return ''.join(parts)

class Session:
    def __init__(self,base=BASE):
        self.base=base;assert_frozen(base)
        self.assign=read(base/'private/timing_assignment.json')
        self.records={r['run_id']:r for r in read(base/'private/imported_primary.json')}
        self.pathways={(r['run_id'],r['pathway']):r for r in read(base/'private/pathways.json')}
        self.file=base/'timing/session.json';self.state=read(self.file) if self.file.exists() else {'items':{},'events':[]}
        for r in self.state['items'].values():
            if r.get('phase') in ['decision','finalization']:
                r['restart_interruption']=True
        self.save()
    def save(self):write(self.file,self.state)
    def current(self):return next((x for x in self.assign if self.state['items'].get(x['timing_id'],{}).get('phase')!='complete'),None)
    def event(self,action,form):
        item=self.current()
        if item is None:raise ValueError('All timed items completed')
        tid=item['timing_id'];r=self.state['items'].setdefault(tid,{'phase':'not_started','inspect_override':False,'pauses':[],'prior_exposure':'UNKNOWN'})
        t=now()
        if action=='start':
            if r['phase']!='not_started':raise ValueError('Already started')
            r.update(phase='decision',clock1_start=t,prior_exposure=form.get('exposure','UNKNOWN'))
        elif action=='inspect':
            if r['phase']!='decision' or r.get('pause_start'):raise ValueError('Inspect during active decision phase only')
            if item['pathway']!='controlled' or self.pathways[(item['run_id'],item['pathway'])]['decision'] not in ['block','route']:raise ValueError('This answer is not withheld')
            r['inspect_override']=True;r['inspect_at']=t
        elif action=='pause':
            if r['phase'] not in ['decision','finalization'] or r.get('pause_start'):raise ValueError('Cannot pause now')
            if not form.get('reason','').strip():raise ValueError('Pause reason required')
            r['pause_start']=t;r['pause_reason']=form['reason']
        elif action=='resume':
            if not r.get('pause_start'):raise ValueError('Not paused')
            r['pauses'].append({'phase':r['phase'],'start':r.pop('pause_start'),'finish':t,'reason':r.pop('pause_reason')})
        elif action=='decide':
            if r['phase']!='decision' or r.get('pause_start'):raise ValueError('Decision phase must be active')
            if form.get('decision') not in ['accept','minor_edit','major_edit','reject','escalate','accept_gate']:raise ValueError('Choose a decision')
            r.update(phase='between_clocks',clock1_finish=t,decision=form['decision'],decision_reason=form.get('reason',''))
        elif action=='finalize_start':
            if r['phase']!='between_clocks':raise ValueError('Record decision first')
            r.update(phase='finalization',clock2_start=t)
        elif action in ['finish','no_work']:
            if action=='finish' and (r['phase']!='finalization' or r.get('pause_start')):raise ValueError('Finalization must be active')
            if action=='no_work' and r['phase']!='between_clocks':raise ValueError('Record decision first')
            if not form.get('product','').strip():raise ValueError('Usable answer or justified disposition required')
            r['final_product']=form['product'];r['completion_status']=form.get('completion_status','justified_disposition')
            if action=='no_work':r['clock2_seconds']=0;r['no_further_work_explicit']=True
            else:
                r['clock2_finish']=t;r['clock2_seconds']=active_seconds(r['clock2_start'],t,[(p['start'],p['finish']) for p in r['pauses'] if p['phase']=='finalization'])
            r['clock1_seconds']=active_seconds(r['clock1_start'],r['clock1_finish'],[(p['start'],p['finish']) for p in r['pauses'] if p['phase']=='decision'])
            r['phase']='complete';r['completed_at']=t
        else:raise ValueError('Unknown action')
        self.state['events'].append({'timing_id':tid,'action':action,'at':t});self.save()
    def page(self,token):
        item=self.current()
        if item is None:return '<h1>All 24 timed items recorded</h1><p>Tell Codex to prepare masked content scoring. Do not open the identity key.</p>'
        tid=item['timing_id'];r=self.state['items'].get(tid,{'phase':'not_started'})
        head=f'<h1>Timed handling {tid}</h1><p>Phase: {escape(r["phase"])}. Times are logged automatically in seconds. Pause for interruptions. Refresh does not restart the clock.</p>'
        def button(action,label):return f'<button name="action" value="{action}">{label}</button>'
        form='<form method="post"><input type="hidden" name="token" value="'+token+'">'
        if r['phase']=='not_started':
            return head+form+'<p>Did you previously read this answer during generation or receipt checking?</p><select name="exposure"><option>UNKNOWN</option><option>YES</option><option>NO</option></select>'+button('start','Show materials and start Clock 1')+'</form>'
        if r.get('restart_interruption'):head+='<p>Session restarted during this item. This interruption is recorded; timing requires review and must not be represented as uninterrupted.</p>'
        if r.get('pause_start'):return head+form+'<p>Paused. Materials hidden while paused.</p>'+button('resume','Resume')+'</form>'
        body=material(self.base,item,self.records[item['run_id']],self.pathways[(item['run_id'],item['pathway'])],r.get('inspect_override',False))
        if r['phase']=='decision':
            if item['pathway']=='controlled' and self.pathways[(item['run_id'],item['pathway'])]['decision'] in ['block','route'] and not r.get('inspect_override'):form+=button('inspect','Inspect withheld answer and log exposure')
            form+='<p>Decision</p><select name="decision"><option value="">Choose</option>'+''.join(f'<option>{d}</option>' for d in ['accept','minor_edit','major_edit','reject','escalate','accept_gate'])+'</select><p>Brief reason or pause reason</p><textarea name="reason"></textarea>'+button('decide','Commit decision and stop Clock 1')+button('pause','Pause Clock 1')
        elif r['phase']=='between_clocks':
            form+='<p>Clock 1 stopped. Start Clock 2 before editing or preparing a final disposition.</p>'+button('finalize_start','Start Clock 2')+'<p>Only if no further work is needed, record the accepted answer or justified disposition below.</p><textarea name="product"></textarea>'+button('no_work','Record no further work with Clock 2 equal to zero')
        else:
            form+='<p>Final usable answer or justified disposition</p><textarea name="product" rows="12"></textarea><select name="completion_status"><option>usable_answer</option><option>justified_disposition</option><option>unresolved</option></select><p>Pause reason if needed</p><textarea name="reason"></textarea>'+button('finish','Save final product and stop Clock 2')+button('pause','Pause Clock 2')
        return head+body+form+'</form>'

def run():
    session=Session();token=secrets.token_urlsafe(24)
    class Handler(BaseHTTPRequestHandler):
        def log_message(self,*args):pass
        def do_GET(self):
            if self.path!='/':self.send_error(404);return
            text='<!doctype html><meta charset="utf-8"><title>Timed assessment review</title><style>body{max-width:880px;margin:35px auto;font:17px/1.5 Arial;color:#18262e;padding:20px}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:15px/1.5 Arial}textarea{display:block;width:100%;min-height:75px;background:#fff8d8}button,select{font:16px Arial;padding:12px;margin:8px}h2{margin-top:28px}</style>'+session.page(token)
            b=text.encode();self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.send_header('Cache-Control','no-store');self.end_headers();self.wfile.write(b)
        def do_POST(self):
            length=int(self.headers.get('Content-Length','0'))
            if length>200000:self.send_error(413);return
            form={k:v[-1] for k,v in urllib.parse.parse_qs(self.rfile.read(length).decode(),keep_blank_values=True).items()}
            if form.get('token')!=token:self.send_error(403);return
            try:session.event(form.get('action'),form)
            except ValueError as e:self.send_error(400,str(e));return
            self.send_response(303);self.send_header('Location','/');self.end_headers()
    server=HTTPServer(('127.0.0.1',8765),Handler)
    print('Open http://127.0.0.1:8765 locally. No model calls are made. Ctrl-C stops the server.')
    server.serve_forever()
if __name__=='__main__':run()

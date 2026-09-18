"""Masked scoring preparation and lossless Word form extraction."""
import argparse,html,json,zipfile,xml.etree.ElementTree as ET
from pathlib import Path
from experiment import BASE,read,write,assert_frozen,digest,now

def prepare(base=BASE,repeat=False):
    assert_frozen(base)
    timing=read(base/'timing/session.json')
    if sum(r.get('phase')=='complete' for r in timing['items'].values())!=24:raise ValueError('Complete all timed items before formal content scoring')
    records={r['run_id']:r for r in read(base/'private/imported_primary.json')};key=read(base/'private/identity_key.json')
    targets=set(read(base/'private/repeat_assignment.json')) if repeat else None
    if repeat:
        lock=read(base/'scoring/score_lock.json')
        if digest(base/'scoring/researcher_scores.json')!=lock['sha256']:raise ValueError('Locked initial scores changed')
        from datetime import datetime,timezone
        first={r['masked_id']:r for r in read(base/'scoring/researcher_scores.json')}
        for mid in targets:
            if not first[mid].get('scored_at'):raise ValueError('Initial score time missing for '+mid)
            if (datetime.now(timezone.utc)-datetime.fromisoformat(first[mid]['scored_at'])).total_seconds()<86400:raise ValueError('24-hour repeat interval not yet met for '+mid)
    output=[]
    for k in key:
        mid=k['masked_id'];cid=k['case_id']
        if targets is not None and mid not in targets:continue
        c=read(base/f'references/{cid}.json');inp=read(base/f'inputs/{cid}.json');r=records[k['run_id']]
        output.append({'masked_id':mid,'case_id':cid,'status':'PENDING','scored_at':None,'severity':None,'acceptable':None,'failure_classes':[],'criteria':[{'criterion':x['criterion'],'judgment':None,'response_evidence':'','reason':''} for x in c['scoring_checks']],'reference_challenge':'','prior_timing_exposure':any(t['run_id']==k['run_id'] for t in read(base/'private/timing_assignment.json'))})
        material={'masked_id':mid,'case':inp,'original_response':r['response'] if r['response'] is not None else (base/k['raw_txt']).read_text(),'reference':c,'record_status':r['record_status'],'quarantine':r.get('quarantine')}
        folder=base/'scoring'/('repeat_materials' if repeat else 'materials');write(folder/f'{mid}.json',material)
        # Reading copy does not contain other scores, identities, gate fields or model paths.
        esc=lambda x:html.escape(str(x))
        body=f'<h1>Response {mid} — {cid}</h1>'
        for title,value in [('Scenario','\n\n'.join(inp['scenario'])),('Task',inp['requested_task']),('Policy evidence',inp['source_excerpt']),('Original response',material['original_response']),('Reference',c['reference_response']),('Scoring criteria',c['scoring_checks']),('Acceptable variants',c['acceptable_variants'])]:
            body+=f'<h2>{title}</h2><pre>'+esc(value if isinstance(value,str) else json.dumps(value,ensure_ascii=False,indent=2))+'</pre>'
        (folder/f'{mid}.html').write_text('<!doctype html><meta charset="utf-8"><style>body{max-width:850px;margin:40px auto;font:17px/1.5 Arial}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:16px/1.5 Arial}</style>'+body)
        form=f'# Response {mid} — Case {cid}\n\n[Read case, original answer, policy evidence and reference]({mid}.html)\n\nActual scoring completed at (date, time and timezone):\nStatus (SCORED / MISSING / CANNOT_JUDGE):\n\n'
        for criterion in c['scoring_checks']:
            form+=f"## Criterion {criterion['criterion']}\n\n{criterion['pass_criteria']}\n\nJudgment (Correct / Incorrect / Incomplete / Cannot judge):\nResponse evidence and brief reason:\n\n"
        form+='## Overall\n\nSeverity (None / Minor / Major / Critical / Cannot judge):\nAcceptable (Yes / No / Cannot judge):\nSource or reference concern:\nOther comments:\n'
        (folder/f'{mid}_review.md').write_text(form)
    target=base/'scoring'/('repeat_scores.json' if repeat else 'researcher_scores.json')
    if target.exists():raise ValueError('Score file exists; never overwrite human entries')
    write(target,output)
    (base/'scoring'/('REPEAT_INDEX.md' if repeat else 'SCORING_INDEX.md')).write_text('# Masked scoring order\n\nUse the criteria and severity guide from the reviewer manual. Record judgments in the linked review files; Codex will synchronize them. Do not open private keys or control files.\n\n'+'\n'.join(f"- [{r['masked_id']}]({'repeat_materials' if repeat else 'materials'}/{r['masked_id']}_review.md)" for r in output))

def extract_docx(path,output):
    """Extract original form values without adjudicating or rewriting reviewer text."""
    ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'};w='{'+ns['w']+'}'
    with zipfile.ZipFile(path) as z:root=ET.fromstring(z.read('word/document.xml'))
    fields=[]
    for control in root.findall('.//w:sdt',ns):
        tag=control.find('w:sdtPr/w:tag',ns)
        if tag is None:continue
        texts=control.findall('.//w:sdtContent//w:t',ns)
        fields.append({'tag':tag.get(w+'val'),'value_verbatim':'\n'.join(t.text or '' for t in texts)})
    write(output,{'source_path':str(path),'source_sha256':digest(path),'extracted_at':now(),'fields':fields,'status':'VERBATIM_EXTRACTION_NOT_ADJUDICATED'})
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('command',choices=['prepare','repeat','extract']);p.add_argument('--docx');p.add_argument('--out');args=p.parse_args()
    if args.command=='extract':extract_docx(Path(args.docx),Path(args.out))
    else:prepare(repeat=args.command=='repeat')

"""Offline AI-judge ingestion. No network, paid calls, human-score reads or model identity joins.
Default is validation-only. --write preserves raw files and writes parsed records, with hash checks.
"""
from pathlib import Path
import argparse,json,re,hashlib
from datetime import datetime,timezone

def digest(data):return hashlib.sha256(data).hexdigest()
def extract(raw):
    txt=raw.strip()
    fenced=re.fullmatch(r'```(?:json)?\s*\n?(.*?)\n?```',txt,re.S|re.I)
    if fenced:txt=fenced.group(1)
    def pairs(items):
        out={}
        for k,v in items:
            if k in out:raise ValueError('Duplicate JSON key: '+k)
            out[k]=v
        return out
    obj=json.loads(txt,object_pairs_hook=pairs,parse_constant=lambda x:(_ for _ in ()).throw(ValueError('Invalid JSON constant')))
    return obj,bool(fenced)

def validate(obj,row):
    errors=[]
    def require(ok,msg):
        if not ok:errors.append(msg)
    if not isinstance(obj,dict):return ['Reply must be one JSON object']
    require(set(obj)=={'judge_id','case_id','status','criteria','severity','acceptable','overall_reason','reference_concern'},'Unexpected or missing top-level fields')
    require(obj.get('judge_id')==row['judge_id'],'Judge ID mismatch');require(obj.get('case_id')==row['case_id'],'Case ID mismatch')
    require(obj.get('status') in ['SCORED','CANNOT_JUDGE'],'Invalid status')
    require(obj.get('severity') in ['None','Minor','Major','Critical','Cannot judge'],'Invalid severity')
    require(obj.get('acceptable') in ['Yes','No','Cannot judge'],'Invalid acceptability')
    require(isinstance(obj.get('overall_reason'),str) and bool(obj.get('overall_reason','').strip()),'Overall reason missing')
    cs=obj.get('criteria');ids=[];unresolved=False
    if not isinstance(cs,list):errors.append('criteria must be a list');cs=[]
    for c in cs:
        if not isinstance(c,dict):errors.append('Criterion must be an object');continue
        require(set(c)=={'criterion','judgment','response_evidence','source_basis','reason'},'Unexpected or missing criterion fields')
        v=c.get('criterion');require(type(v) is int,'Criterion ID must be integer');ids.append(v)
        require(c.get('judgment') in ['Correct','Incorrect','Incomplete','Cannot judge'],'Invalid criterion judgment')
        unresolved |= c.get('judgment')=='Cannot judge'
        require(c.get('response_evidence') is None or isinstance(c.get('response_evidence'),str),'Evidence must be text or null')
        for k in ['source_basis','reason']:require(isinstance(c.get(k),str) and bool(c.get(k,'').strip()),'Missing '+k)
    require(len(ids)==len(row['criteria_ids']) and all(type(i) is int for i in ids) and sorted(ids)==sorted(row['criteria_ids']),'Criterion IDs must match once each')
    rc=obj.get('reference_concern')
    if not isinstance(rc,dict):errors.append('reference_concern must be object')
    else:
        require(set(rc)=={'present','detail','prevents_overall_judgment'},'Reference-concern fields mismatch')
        require(type(rc.get('present')) is bool and type(rc.get('prevents_overall_judgment')) is bool,'Reference-concern flags must be Boolean')
        require(isinstance(rc.get('detail'),str),'Reference concern detail must be text')
        if rc.get('present'):require(bool(rc.get('detail','').strip()),'Explain the reference concern')
        if rc.get('prevents_overall_judgment'):require(rc.get('present') is True and obj.get('status')=='CANNOT_JUDGE','Blocking reference concern requires unresolved overall status')
    if obj.get('status')=='CANNOT_JUDGE':require(obj.get('severity')=='Cannot judge' and obj.get('acceptable')=='Cannot judge','Unresolved overall status requires unresolved overall labels')
    if obj.get('status')=='SCORED':require(obj.get('severity')!='Cannot judge' and obj.get('acceptable')!='Cannot judge','SCORED cannot use unresolved overall labels')
    if obj.get('acceptable')=='Yes':require(obj.get('severity') in ['None','Minor'] and not unresolved,'Yes conflicts with serious or unresolved judgment')
    if obj.get('severity') in ['Major','Critical']:require(obj.get('acceptable')=='No','Serious error requires No')
    return errors

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--package',type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument('--write',action='store_true');args=ap.parse_args();p=args.package
    rows=json.loads((p/'protocol/COLLECTION_MANIFEST.json').read_text());counts={'empty':0,'valid':0,'invalid':0};report=[]
    for row in rows:
        rawpath=p/row['raw_path'];raw=rawpath.read_bytes()
        if not raw.strip():counts['empty']+=1;continue
        prompt=(p/row['prompt_path']).read_bytes()
        if digest(prompt)!=row['prompt_sha256']:raise SystemExit('Prompt changed: '+row['judge_id'])
        errors=[];obj=None;fenced=False
        try:obj,fenced=extract(raw.decode('utf-8-sig'));errors=validate(obj,row)
        except (ValueError,TypeError,UnicodeDecodeError) as e:errors=[str(e)]
        warnings=[]
        if not errors:
            txt=prompt.decode();payload=json.loads(txt.split('BEGIN EVALUATION PAYLOAD\n',1)[1].rsplit('\nEND EVALUATION PAYLOAD',1)[0]);response=payload['original_response']
            strings=[]
            def collect(x):
                if isinstance(x,str):strings.append(x)
                elif isinstance(x,dict):
                    for v in x.values():collect(v)
                elif isinstance(x,list):
                    for v in x:collect(v)
            collect(response);norm=lambda x:re.sub(r'\s+',' ',x).strip()
            for c in obj['criteria']:
                ev=c['response_evidence']
                if ev and not any(norm(ev) in norm(t) for t in strings):warnings.append('Criterion '+str(c['criterion'])+': evidence quote is not a contiguous match; inspect without rewriting raw output.')
        status='VALIDATED_STRUCTURE' if not errors else 'INVALID_OUTPUT';counts['valid' if not errors else 'invalid']+=1
        report.append({'judge_id':row['judge_id'],'record_status':status,'errors':errors,'warnings':warnings,'raw_sha256':digest(raw),'outer_code_fence_removed':fenced})
        if args.write:
            out=p/row['parsed_path'];old=json.loads(out.read_text())
            if old.get('record_status')!='PENDING_COLLECTION' and old.get('raw_sha256')!=digest(raw):raise SystemExit('Previously processed raw changed: '+row['judge_id']+'. Preserve new attempt separately.')
            record={'judge_id':row['judge_id'],'case_id':row['case_id'],'record_status':status,'processed_at':datetime.now(timezone.utc).isoformat(),'raw_sha256':digest(raw),'prompt_sha256':row['prompt_sha256'],'judgment':obj,'validation_errors':errors,'warnings':warnings,'outer_code_fence_removed':fenced,'note':'Structure validation is not verification of substantive correctness. Actual model/settings come from collection records, not this reply.'}
            out.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'mode':'WRITE' if args.write else 'CHECK_ONLY','counts':counts,'records_with_issues':[{'judge_id':r['judge_id'],'errors':r['errors'],'warnings':r['warnings']} for r in report if r['errors'] or r['warnings']]},indent=2))
    if args.write:
        stamp=datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ');(p/'qa'/f'ingest_{stamp}.json').write_text(json.dumps({'counts':counts,'records':report},indent=2)+'\n')
if __name__=='__main__':main()

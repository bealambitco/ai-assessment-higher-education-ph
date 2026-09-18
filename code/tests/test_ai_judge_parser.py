import unittest,copy,json,sys,pathlib
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parents[1]/'extensions'/'ai_judge'))  # repository layout (2026-09-18)
from process_outputs import extract,validate
class Tests(unittest.TestCase):
 def setUp(self):
  self.row={'judge_id':'TEST','case_id':'PRACTICE','criteria_ids':[1]}
  self.obj={'judge_id':'TEST','case_id':'PRACTICE','status':'SCORED','criteria':[{'criterion':1,'judgment':'Correct','response_evidence':'Synthetic quote','source_basis':'Synthetic policy clause','reason':'Synthetic fixture only'}],'severity':'None','acceptable':'Yes','overall_reason':'Synthetic fixture only','reference_concern':{'present':False,'detail':'','prevents_overall_judgment':False}}
 def test_valid(self):self.assertEqual(validate(self.obj,self.row),[])
 def test_fence(self):self.assertEqual(extract('```json\n'+json.dumps(self.obj)+'\n```'),(self.obj,True))
 def test_duplicates(self):
  with self.assertRaises(ValueError):extract('{"a":1,"a":2}')
 def test_prose(self):
  with self.assertRaises(ValueError):extract('Here is the answer '+json.dumps(self.obj))
 def test_wrong_id(self):self.obj['judge_id']='WRONG';self.assertTrue(validate(self.obj,self.row))
 def test_missing_criterion(self):self.obj['criteria']=[];self.assertTrue(validate(self.obj,self.row))
 def test_serious_yes(self):self.obj['severity']='Major';self.assertTrue(validate(self.obj,self.row))
 def test_unresolved_yes(self):self.obj['criteria'][0]['judgment']='Cannot judge';self.assertTrue(validate(self.obj,self.row))
 def test_valid_unresolved(self):
  self.obj.update(status='CANNOT_JUDGE',severity='Cannot judge',acceptable='Cannot judge');self.obj['criteria'][0]['judgment']='Cannot judge';self.assertEqual(validate(self.obj,self.row),[])
 def test_schema_extra(self):self.obj['model']='invented';self.assertTrue(validate(self.obj,self.row))
 def test_blocking_concern(self):self.obj['reference_concern']={'present':True,'detail':'Ambiguous source','prevents_overall_judgment':True};self.assertTrue(validate(self.obj,self.row))
 def test_false_boolean_id(self):self.obj['criteria'][0]['criterion']=True;self.assertTrue(validate(self.obj,self.row))
if __name__=='__main__':unittest.main()

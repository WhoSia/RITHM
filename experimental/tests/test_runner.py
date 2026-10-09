import json, os, pathlib, subprocess, sys, tempfile, time, unittest
RUNNER=pathlib.Path(__file__).resolve().parents[1]/'resilient_parallel.py'
def call(*args):return subprocess.run([sys.executable,str(RUNNER),*map(str,args)],capture_output=True,text=True)
class RunnerTests(unittest.TestCase):
 def setUp(self):self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name)
 def tearDown(self):self.tmp.cleanup()
 def prep(self,name,script):
  r=call('prepare','--root',self.root,'--name',name,'--cwd',self.root,'--',sys.executable,'-c',script)
  self.assertEqual(r.returncode,0,r.stderr)
 def state(self,name):return json.loads((self.root/name/'status.json').read_text())
 def settle(self,name):
  for _ in range(400):
   x=self.state(name)
   if x['state'] in ('SUCCEEDED','FAILED'):return x
   time.sleep(.02)
  self.fail('worker completion timeout')
 def test_success_no_retry(self):
  self.prep('a',"from pathlib import Path;Path('counter').open('a').write('x')")
  self.assertEqual(call('dispatch','--root',self.root).returncode,0)
  self.assertEqual(self.settle('a')['state'],'SUCCEEDED')
  self.assertEqual(call('dispatch','--root',self.root).returncode,0)
  self.assertEqual((self.root/'counter').read_text(),'x')
 def test_nonzero_no_retry(self):
  self.prep('a','import sys;sys.exit(7)')
  self.assertEqual(call('dispatch','--root',self.root).returncode,0)
  self.assertEqual(self.settle('a')['returncode'],7)
  self.assertEqual(call('dispatch','--root',self.root).returncode,0)
  self.assertEqual(self.state('a')['returncode'],7)
 def test_unknown_capacity_hold(self):
  self.prep('a','pass');self.prep('b','pass')
  (self.root/'a'/'status.json').write_text('{"state":"UNKNOWN"}')
  self.assertEqual(call('dispatch','--root',self.root,'--max-parallel',1).returncode,0)
  self.assertEqual(self.state('b')['state'],'PLANNED')
 def test_invalid_name(self):
  self.assertNotEqual(call('prepare','--root',self.root,'--name','../unsafe','--cwd',self.root,'--',sys.executable,'-c','pass').returncode,0)
 def test_launching_no_retry(self):
  self.prep('a','pass');(self.root/'a'/'status.json').write_text('{"state":"LAUNCHING"}')
  self.assertEqual(call('dispatch','--root',self.root).returncode,0)
  self.assertEqual(self.state('a')['state'],'LAUNCHING')
 def test_controller_returns_worker_completes(self):
  self.prep('a','import time;time.sleep(.15)')
  self.assertEqual(call('dispatch','--root',self.root).returncode,0)
  self.assertEqual(self.settle('a')['state'],'SUCCEEDED')
 def test_abrupt_worker_death_no_retry(self):
  self.prep('a','import time;time.sleep(30)')
  self.assertEqual(call('dispatch','--root',self.root).returncode,0)
  for _ in range(200):
   if self.state('a')['state']=='RUNNING':break
   time.sleep(.02)
  else:self.fail('worker not running')
  try:os.kill(self.state('a')['worker_pid'],9)
  except ProcessLookupError:pass
  time.sleep(.1)
  self.assertEqual(call('dispatch','--root',self.root).returncode,0)
  self.assertEqual(self.state('a')['state'],'RUNNING')
if __name__=='__main__':unittest.main()

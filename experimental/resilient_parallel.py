#!/usr/bin/env python3
"""Disposable local-job runner prototype; NOT an authorized RITHM scientific executor."""
import argparse, fcntl, json, os, subprocess, sys, time
from pathlib import Path

STATES={'PLANNED','LAUNCHING','RUNNING','SUCCEEDED','FAILED','UNKNOWN'}
def write_atomic(p,obj):
 tmp=p.with_suffix('.tmp')
 with tmp.open('x') as f:
  json.dump(obj,f,indent=2,sort_keys=True);f.write('\n');f.flush();os.fsync(f.fileno())
 os.replace(tmp,p)
def load(p):return json.loads(p.read_text())
def status_path(job):return job/'status.json'
def worker(job):
 status=status_path(job)
 try:
  spec=load(job/'spec.json')
  before=load(status)
  if before['state']!='LAUNCHING':raise RuntimeError('NO_LAUNCH_INTENT')
  before.update(state='RUNNING',worker_pid=os.getpid(),started_at=time.time())
  write_atomic(status,before)
  with (job/'stdout.log').open('xb') as out,(job/'stderr.log').open('xb') as err:
   rc=subprocess.call(spec['argv'],cwd=spec['cwd'],stdin=subprocess.DEVNULL,stdout=out,stderr=err)
  before.update(state='SUCCEEDED' if rc==0 else 'FAILED',returncode=rc,finished_at=time.time())
  write_atomic(status,before)
 except BaseException as e:
  prior=load(status) if status.exists() else {}
  prior.update(state='FAILED',worker_error=repr(e),finished_at=time.time())
  write_atomic(status,prior)
  raise
def controller(root,max_parallel):
 if max_parallel<1:raise ValueError('max_parallel must be >=1')
 if not root.is_dir():raise ValueError('EXISTING_ISOLATED_ROOT_REQUIRED')
 lockfd=os.open(root/'.dispatcher.lock',os.O_RDWR|os.O_CREAT,0o600)
 try:fcntl.flock(lockfd,fcntl.LOCK_EX|fcntl.LOCK_NB)
 except BlockingIOError:raise RuntimeError('CONCURRENT_DISPATCHER_REFUSED')
 jobs=sorted(p for p in root.iterdir() if p.is_dir() and (p/'spec.json').exists())
 counts={}
 for job in jobs:
  state=load(status_path(job))['state']
  if state not in STATES:raise ValueError('UNKNOWN_STATE')
  counts[state]=counts.get(state,0)+1
 print('BEFORE',counts,flush=True)
 active=sum(load(status_path(j))['state'] in ('LAUNCHING','RUNNING','UNKNOWN') for j in jobs)
 for job in jobs:
  if active>=max_parallel:break
  if load(status_path(job))['state']!='PLANNED':continue
  record={'state':'LAUNCHING','controller_pid':os.getpid(),'claimed_at':time.time()}
  write_atomic(status_path(job),record)
  with (job/'launcher.log').open('xb') as output:
   proc=subprocess.Popen([sys.executable,str(Path(__file__).resolve()),'worker','--job',str(job)],
      stdin=subprocess.DEVNULL,stdout=output,stderr=subprocess.STDOUT,
      start_new_session=True,cwd=job)
  print('LAUNCHED',job.name,'PID',proc.pid,flush=True)
  active+=1
 print('ACTIVE_OR_UNRESOLVED',active,flush=True)
def prepare(root,name,argv,cwd):
 if argv and argv[0]=='--':argv=argv[1:]
 if not argv:raise ValueError('empty command')
 if not root.is_dir():raise ValueError('existing isolated root required')
 if name in ('','.','..') or '/' in name or '\\' in name:raise ValueError('invalid job name')
 job=root/name;job.mkdir(mode=0o700,exist_ok=False)
 write_atomic(job/'spec.json',{'argv':argv,'cwd':str(cwd.resolve())})
 write_atomic(status_path(job),{'state':'PLANNED','created_at':time.time()})
 print('PREPARED',name)
if __name__=='__main__':
 p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
 a=sub.add_parser('prepare');a.add_argument('--root',type=Path,required=True);a.add_argument('--name',required=True);a.add_argument('--cwd',type=Path,required=True);a.add_argument('argv',nargs='+')
 a=sub.add_parser('dispatch');a.add_argument('--root',type=Path,required=True);a.add_argument('--max-parallel',type=int,default=1)
 a=sub.add_parser('worker');a.add_argument('--job',type=Path,required=True)
 a=p.parse_args()
 if a.cmd=='prepare':prepare(a.root,a.name,a.argv,a.cwd)
 elif a.cmd=='dispatch':controller(a.root,a.max_parallel)
 else:worker(a.job)

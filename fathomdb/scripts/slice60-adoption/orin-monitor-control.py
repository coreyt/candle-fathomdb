import ast,os,pathlib,signal,subprocess,sys
P=pathlib.Path(__file__).resolve().parent
names={'proc','actors','owned_rss'}
def functions(path):
 tree=ast.parse(path.read_text());return [x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in names]
adoption=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else P/'run_orin.py'
actor=pathlib.Path(sys.argv[2]).resolve() if len(sys.argv)>2 else P.parent/'slice60-installed/run_orin.py'
a=functions(adoption);b=functions(actor)
for name in ('proc','owned_rss'):
 x=next(n for n in a if n.name==name);y=next(n for n in b if n.name==name);assert ast.dump(x,include_attributes=False)==ast.dump(y,include_attributes=False)
real=subprocess.Popen
class Interrupting:
 def __init__(self,*args,**kwargs):
  self.child=real([sys.executable,'-c','import time;time.sleep(30)']);self.pid=self.child.pid;self.returncode=None;created.append(self)
 def communicate(self,timeout=None):raise KeyboardInterrupt('synthetic interruption')
 def poll(self):return self.child.poll()
 def terminate(self):return self.child.terminate()
 def kill(self):return self.child.kill()
 def wait(self,timeout=None):
  value=self.child.wait(timeout=timeout);self.returncode=value;return value
class Sp:
 PIPE=subprocess.PIPE;TimeoutExpired=subprocess.TimeoutExpired;Popen=Interrupting
created=[];ns={'os':os,'pathlib':pathlib,'subprocess':Sp,'last_fuser':None,'last_details':{},'last_fuser_rss':None};exec(compile(ast.Module(body=b,type_ignores=[]),str(actor),'exec'),ns)
try:ns['actors']()
except KeyboardInterrupt:pass
else:raise AssertionError('interruption not propagated')
assert len(created)==1 and created[0].child.poll() is not None
print('PASS interrupted fuser helper terminated and reaped')
ns['last_fuser']=-1;ns['last_fuser_rss']=123;ns['last_details']={}
p=real([sys.executable,'-c','import subprocess,sys,time; p=subprocess.Popen([sys.executable,"-c","import time;time.sleep(30)"]);print(p.pid,flush=True);time.sleep(30)'],stdout=subprocess.PIPE,text=True,start_new_session=True)
try:
 child=int(p.stdout.readline());main=ns['proc'](p.pid);other=ns['proc'](child);assert main['SID']==main['PGID']==p.pid and other['SID']==other['PGID']==p.pid
 ns['last_details']={str(child):other};total,rows=ns['owned_rss'](p.pid,main['start_ticks'],[child,child]);assert len(rows)==2 and total==sum(x['rss'] for x in rows.values())+123
 print('PASS real leader and helper RSS summed by distinct TGID; duplicate deduplicated')
 try:ns['owned_rss'](p.pid,'wrong-start',[child])
 except RuntimeError:print('PASS PID birth mismatch rejected')
 else:raise AssertionError('wrong birth accepted')
 ns['last_details']={'99999999':{'error':'gone'}}
 try:ns['owned_rss'](p.pid,main['start_ticks'],[99999999])
 except RuntimeError:print('PASS unknown GPU peer rejected')
 else:raise AssertionError('unknown peer accepted')
finally:
 try:os.killpg(p.pid,signal.SIGTERM)
 except ProcessLookupError:pass
 p.wait(timeout=5)

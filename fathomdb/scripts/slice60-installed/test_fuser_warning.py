import ast,os,pathlib,re,sys
root=pathlib.Path(__file__).resolve().parent
source=pathlib.Path(sys.argv[1]).resolve() if len(sys.argv)>1 else root/'run_orin_actor.py'
tree=ast.parse(source.read_text());selected=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name in ('classify_fuser_stderr','proc','owned_rss')]
assert {x.name for x in selected}=={'classify_fuser_stderr','proc','owned_rss'},'the warning classifier must exist'
ns={'os':os,'pathlib':pathlib,'re':re,'last_fuser':-1,'last_fuser_rss':None,'last_details':{}};exec(compile(ast.Module(body=selected,type_ignores=[]),str(source),'exec'),ns)
actual=''.join(f'Cannot stat file /proc/2919024/fd/{fd}: Permission denied\n' for fd in range(4,37))
captured=root/'orin-adoption-session-original.log'
if captured.exists():assert captured.read_text().split('AssertionError: ',1)[1].strip()==actual.strip()
warnings=ns['classify_fuser_stderr'](actual);assert len(warnings)==33 and all(x['pid']==2919024 for x in warnings),warnings
assert ns['classify_fuser_stderr']('/dev/nvhost-gpu: /dev/nvmap:\n')==[]
for invalid in ['permission denied','Cannot stat file /dev/nvmap: Permission denied','fuser: unexpected failure','Cannot stat file /proc/abc/fd/1: Permission denied']:
 try:ns['classify_fuser_stderr'](invalid)
 except RuntimeError:pass
 else:raise AssertionError('unexpected stderr accepted: '+invalid)
ns['last_details']={'99999999':{'error':'gone'}}
try:ns['owned_rss'](os.getpid(),'unused',[99999999])
except RuntimeError as e:assert 'unknown GPU peer' in str(e)
else:raise AssertionError('unknown observed peer accepted')
print('PASS actual 33 warnings recorded; headings accepted; unrelated stderr and unknown observed peer rejected')

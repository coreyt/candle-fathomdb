import ctypes,fcntl,hashlib,json,os,pathlib,re,shutil,signal,subprocess,time
from campaign import configuration, validate_child
CAMPAIGN, ARMS, SESSION_START = configuration()
if not __debug__:raise RuntimeError('optimized Python is not supported')
if os.environ.get('AGENT_LONG')!='1':raise RuntimeError('set AGENT_LONG=1 for the approved qualification')
B=pathlib.Path(os.environ['SLICE60_ROOT']).resolve();UUID=os.environ['FATHOMDB_GPU_UUID'];O=pathlib.Path(os.environ.get('FATHOMDB_ACTOR_OUTPUT',str(B/'terra-installed-actors-evidence'))).resolve();L=pathlib.Path(os.environ['FATHOMDB_GPU_LOCK']);LOCK_INODE=int(os.environ['FATHOMDB_GPU_LOCK_INODE']);CORE=pathlib.Path(__file__).resolve().parent
if not O.is_relative_to(B):raise RuntimeError('output must be under SLICE60_ROOT')
# Jetson process APIs returned NVML_NOT_SUPPORTED. fuser can only observe
# accessible /proc entries, so this is an observed-peer guard, not host-wide proof.
def classify_fuser_stderr(stderr):
 warnings=[]
 for raw in stderr.splitlines():
  line=raw.strip()
  if not line:continue
  m=re.fullmatch(r'Cannot stat file /proc/([0-9]+)/fd/([0-9]+): Permission denied',line)
  if m:warnings.append({'pid':int(m.group(1)),'fd':int(m.group(2))});continue
  if re.fullmatch(r'(?:/dev/nvhost-gpu:|/dev/nvmap:)(?:\s*(?:/dev/nvhost-gpu:|/dev/nvmap:))*',line):continue
  raise RuntimeError('unexpected fuser stderr: '+line)
 return warnings
last_fuser=None;last_details={};last_fuser_rss=None
def proc(pid):
 status=pathlib.Path(f'/proc/{pid}/status').read_text();fields={x.split(':',1)[0]:x.split(':',1)[1].strip() for x in status.splitlines() if ':' in x};stat=pathlib.Path(f'/proc/{pid}/stat').read_text();tail=stat[stat.rfind(')')+2:].split()
 return {'Name':fields.get('Name'),'Tgid':int(fields['Tgid']),'PPid':int(fields['PPid']),'PGID':os.getpgid(pid),'SID':os.getsid(pid),'start_ticks':tail[19],'rss':int(fields.get('VmRSS','0 kB').split()[0])*1024}
def actors():
 global last_fuser,last_details,last_fuser_rss
 f=None;last_fuser=None;last_fuser_rss=None;last_details={}
 try:
  env=os.environ.copy();env['LC_ALL']='C'
  f=subprocess.Popen(['/usr/bin/fuser','/dev/nvhost-gpu','/dev/nvmap'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env);last_fuser=f.pid
  try:last_fuser_rss=proc(f.pid)['rss']
  except (OSError,KeyError,IndexError):pass
  stdout,stderr=f.communicate(timeout=2)
 finally:
  if f is not None:
   if f.poll() is None:
    try:f.terminate()
    except ProcessLookupError:pass
    try:f.wait(timeout=5)
    except subprocess.TimeoutExpired:
     try:f.kill()
     except ProcessLookupError:pass
     f.wait()
   else:f.wait()
 record={'helper_pid':last_fuser,'returncode':f.returncode,'stderr':stderr,'stdout':stdout,'locale':'C'}
 try:
  if f.returncode not in (0,1):raise RuntimeError(f'unexpected fuser exit {f.returncode}')
  record['visibility_warnings']=classify_fuser_stderr(stderr)
 except BaseException as exc:
  record['error']=repr(exc)
  with (O/'fuser-observations.jsonl').open('a') as evidence:evidence.write(json.dumps(record)+'\n')
  raise
 with (O/'fuser-observations.jsonl').open('a') as evidence:evidence.write(json.dumps(record)+'\n')
 ids=sorted(set(int(x) for x in stdout.split()))
 for pid in ids:
  try:last_details[str(pid)]=proc(pid)
  except (OSError,KeyError,IndexError) as e:last_details[str(pid)]={'error':repr(e)}
 return ids
def owned_rss(leader,birth,ids):
 tgids={leader}
 for pid in ids:
  if pid==last_fuser:continue
  d=last_details.get(str(pid),{})
  if pid==leader or d.get('Tgid')==leader or d.get('PGID')==leader:
   if 'Tgid' not in d:raise RuntimeError(f'cannot identify owned GPU PID {pid}: {d}')
   tgids.add(d['Tgid'])
  else:raise RuntimeError(f'unknown GPU peer {pid}: {d}')
 result={}
 for tgid in sorted(tgids):
  first=proc(tgid);second=proc(tgid)
  if first['Tgid']!=tgid or first['PGID']!=leader or first['SID']!=leader or first['start_ticks']!=second['start_ticks'] or second['PGID']!=leader or second['SID']!=leader:raise RuntimeError(f'changed owned process identity {tgid}')
  if tgid==leader and first['start_ticks']!=birth:raise RuntimeError('child PID reused')
  result[str(tgid)]=first
 return sum(x['rss'] for x in result.values())+(last_fuser_rss or 0),result
def mem():
 return {k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in pathlib.Path('/proc/meminfo').read_text().splitlines())}
def resource(start=False):
 m=mem();d=shutil.disk_usage(B).free
 return {'available':m['MemAvailable'],'swap':m['SwapFree'],'gpu_free':None,'gpu_used':None,'disk':d,'ok':m['MemAvailable']>=(12 if start else 8)*2**30 and m['SwapFree']>=(2 if start else 1)*2**30 and d>=(32 if start else 16)*2**30}
def rss(pid):
 try:
  for line in pathlib.Path(f'/proc/{pid}/status').read_text().splitlines():
   if line.startswith('VmRSS:'):return int(line.split()[1])*1024
 except FileNotFoundError:pass
 return 0


def run(arm,mode):
 language='python'
 name=f'{language}-{arm}-{mode}';capture=O/f'{language}-{arm}-{CAMPAIGN}-database'
 if time.monotonic()-SESSION_START>=1800 or not resource()['ok'] or actors():raise RuntimeError(name+' failed precheck')
 cache=O/f'cache-{name}';cache.mkdir()
 env=os.environ.copy()
 for k in ['CUDA_FORCE_PTX_JIT','CUDA_DISABLE_PTX_JIT','CUDA_FORCE_JIT','CUDA_DISABLE_JIT','CUDA_CACHE_DISABLE','CUDA_CACHE_MAXSIZE','CUDA_MODULE_LOADING','FATHOMDB_RERANKER_CACHE','FATHOMDB_POOL_MODE']:env.pop(k,None)
 env.update(CUDA_VISIBLE_DEVICES=UUID,FATHOMDB_SELECTED_UUID=UUID,FATHOMDB_COORDINATED_RESET=mode,FATHOMDB_REQUIRE_LIVE='1',FATHOMDB_EMBED_DEVICE='cuda:0',FATHOMDB_RERANK_DEVICE='cuda:0',XDG_CACHE_HOME=str(B/'model-cache'),HF_HUB_OFFLINE='1',CUDA_CACHE_PATH=str(cache),FATHOMDB_CAPTURE_DIR=str(capture))
 record=next(x for x in json.loads((B/'evidence/python-installed-identities.json').read_text()) if x['arm']==arm)
 native=pathlib.Path(record['module']);native_sha=hashlib.sha256(native.read_bytes()).hexdigest();assert native_sha==record['sha256'] and hashlib.sha256(pathlib.Path(record['wheel']).read_bytes()).hexdigest()==record['wheel_sha256']
 cmd=[str(B/'installed'/arm/'python/bin/python'),'-I',str(CORE/'coordinate.py')]
 p=None;reason=None;error=None;count=0;last=None;gap=0;saw=False;started=time.monotonic();deadline=started
 with (O/(name+'.log')).open('w') as log,(O/(name+'.samples.jsonl')).open('w') as samples:
  log.write('COMMAND '+repr(cmd)+'\nENV '+repr({k:env.get(k) for k in ['CUDA_VISIBLE_DEVICES','FATHOMDB_SELECTED_UUID','FATHOMDB_COORDINATED_RESET','FATHOMDB_REQUIRE_LIVE','FATHOMDB_EMBED_DEVICE','FATHOMDB_RERANK_DEVICE','XDG_CACHE_HOME','CUDA_CACHE_PATH','FATHOMDB_CAPTURE_DIR','FATHOMDB_PACKAGE_DIR','FATHOMDB_NATIVE_PACKAGE','FATHOMDB_RESET_ACTOR','FATHOMDB_RESET_ACTOR_SHA256']})+'\n');log.flush()
  try:
   p=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);birth=pathlib.Path(f'/proc/{p.pid}/stat').read_text().split()[21]
   while p.poll() is None:
    now=time.monotonic();gap=max(gap,now-last if last else 0);last=now;r=resource();a=actors();total,owned=owned_rss(p.pid,birth,a);r.update(pid=p.pid,start_ticks=birth,rss=total,owned_processes=owned,fuser_rss=last_fuser_rss,elapsed=now-started,actors=a,fuser_pid=last_fuser,actor_details=dict(last_details));samples.write(json.dumps(r)+'\n');samples.flush();count+=1;saw|=p.pid in a
    if not r['ok'] or r['rss']>16*2**30 or r['elapsed']>120 or now-session>1800:reason='guard';break
    deadline+=.02;time.sleep(max(0,deadline-time.monotonic()))
  except BaseException as e:error=repr(e);raise
  finally:
   if p is not None:
    if p.poll() is None:
     try:os.killpg(p.pid,signal.SIGTERM)
     except OSError:pass
     try:p.wait(timeout=5)
     except subprocess.TimeoutExpired:
      try:os.killpg(p.pid,signal.SIGKILL)
      except OSError:pass
      p.wait()
    else:p.wait()
   gap=max(gap,time.monotonic()-last if last else time.monotonic()-started)
   try:log.write(f'\nEXIT {p.returncode if p else None} GUARD {reason} ERROR {error} SAMPLES {count} MAX_GAP {gap:.6f} SAW_ACTOR {saw}\n');log.flush()
   except OSError:pass
 text=(O/(name+'.log')).read_text()
 if not p or p.returncode or reason or not count or not saw or gap>.1:raise RuntimeError(name+' failed, see log')
 validate_child(text,mode,native_sha,UUID,private=True)
 print(name,'PASS',native_sha,'gap',gap,flush=True)

models=json.loads((B/'evidence/model-cache-identity.json').read_text())
for f in models['files']:
 q=B/'model-cache/fathomdb'/f['file'];assert q.stat().st_size==f['bytes'] and hashlib.sha256(q.read_bytes()).hexdigest()==f['sha256']
O.mkdir();(O/'source-sha256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p)+'\n' for p in [CORE/'campaign.py',CORE/'coordinate.py']))
with L.open('rb') as lock:
 assert os.fstat(lock.fileno()).st_ino==LOCK_INODE;fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);session=SESSION_START;pre=resource(True);(O/'preflight.json').write_text(json.dumps({'campaign':CAMPAIGN,'arms':ARMS,'shared_venue_started_monotonic':SESSION_START,'action':os.environ.get('FATHOMDB_RESET_ACTION'),'owner_ruling':os.environ.get('FATHOMDB_RESET_AUTHORIZATION'),'resources':pre,'actors':actors(),'gpu_total_used':'unavailable','peer_visibility':'unprivileged fuser observed-only; NVML process APIs unsupported'}));assert pre['ok'] and not actors()
 for arm in ARMS:
  run(arm,CAMPAIGN);run(arm,'recover')
 (O/'completed.json').write_text(json.dumps({'elapsed':time.monotonic()-session,'resources':resource(),'actors':actors()}))

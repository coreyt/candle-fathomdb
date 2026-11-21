import ctypes,fcntl,hashlib,json,os,pathlib,shutil,signal,subprocess,time
from campaign import configuration, validate_child, bind_case
CAMPAIGN, ARMS, SESSION_START = configuration()
if not __debug__:raise RuntimeError('optimized Python is not supported')
if os.environ.get('AGENT_LONG')!='1':raise RuntimeError('set AGENT_LONG=1 for the approved qualification')
B=pathlib.Path(os.environ['SLICE60_ROOT']).resolve();UUID=os.environ['FATHOMDB_GPU_UUID'];O=pathlib.Path(os.environ.get('FATHOMDB_ACTOR_OUTPUT',str(B/'terra-installed-actors-evidence'))).resolve();L=pathlib.Path(os.environ['FATHOMDB_GPU_LOCK']);LOCK_INODE=int(os.environ['FATHOMDB_GPU_LOCK_INODE']);CORE=pathlib.Path(__file__).resolve().parent;NODE=pathlib.Path(os.environ['FATHOMDB_NODE']);NODE_VERSION=os.environ['FATHOMDB_NODE_VERSION'];ACTOR=pathlib.Path(os.environ['FATHOMDB_RESET_ACTOR']);ACTOR_SHA=os.environ['FATHOMDB_RESET_ACTOR_SHA256']
if not O.is_relative_to(B):raise RuntimeError('output must be under SLICE60_ROOT')
nv=ctypes.CDLL('libnvidia-ml.so.1')
def ck(v):
 if v:raise RuntimeError(f'NVML {v}')
ck(nv.nvmlInit_v2());handle=ctypes.c_void_p();ck(nv.nvmlDeviceGetHandleByUUID(UUID.encode(),ctypes.byref(handle)))
class Memory(ctypes.Structure):_fields_=[('total',ctypes.c_ulonglong),('free',ctypes.c_ulonglong),('used',ctypes.c_ulonglong)]
class Process(ctypes.Structure):_fields_=[('pid',ctypes.c_uint),('used',ctypes.c_ulonglong),('gpu_instance',ctypes.c_uint),('compute_instance',ctypes.c_uint)]
assert ctypes.sizeof(Process)==24
def gpu():
 m=Memory();ck(nv.nvmlDeviceGetMemoryInfo(handle,ctypes.byref(m)));return m
def actors():
 result=[]
 for query in [nv.nvmlDeviceGetComputeRunningProcesses_v3,nv.nvmlDeviceGetGraphicsRunningProcesses_v3]:
  a=(Process*256)();n=ctypes.c_uint(256);ck(query(handle,ctypes.byref(n),a));result.extend(a[i].pid for i in range(n.value))
 return sorted(set(result))
def mem():
 return {k:int(v.split()[0])*1024 for k,v in (line.split(':',1) for line in pathlib.Path('/proc/meminfo').read_text().splitlines())}
def resource(start=False):
 m=mem();g=gpu();d=shutil.disk_usage(B).free
 ram_rule=CAMPAIGN=='healthy' or os.environ.get('FATHOMDB_FAULT_RESOURCE_RULE')=='r580-ram40-24-swap-report'
 return {'available':m['MemAvailable'],'swap':m['SwapFree'],'gpu_free':g.free,'gpu_used':g.used,'disk':d,'ok':m['MemAvailable']>=((40 if start else 24) if ram_rule else (12 if start else 8))*2**30 and (ram_rule or m['SwapFree']>=(2 if start else 1)*2**30) and d>=(32 if start else 16)*2**30 and (not start or g.free>=8*2**30)}
def rss(pid):
 try:
  for line in pathlib.Path(f'/proc/{pid}/status').read_text().splitlines():
   if line.startswith('VmRSS:'):return int(line.split()[1])*1024
 except FileNotFoundError:pass
 return 0


def run(arm,language,mode,prepare_only=False):
 name=f'{language}-{arm}-{mode}';capture=O/f'{language}-{arm}-{CAMPAIGN}-database'
 if time.monotonic()-SESSION_START>=1800 or not resource()['ok'] or actors():raise RuntimeError(name+' failed precheck')
 cache=O/f'cache-{name}'
 if not prepare_only:cache.mkdir()
 env=os.environ.copy()
 for k in ['CUDA_FORCE_PTX_JIT','CUDA_DISABLE_PTX_JIT','CUDA_FORCE_JIT','CUDA_DISABLE_JIT','CUDA_CACHE_DISABLE','CUDA_CACHE_MAXSIZE','CUDA_MODULE_LOADING','FATHOMDB_RERANKER_CACHE','FATHOMDB_POOL_MODE']:env.pop(k,None)
 env.update(CUDA_VISIBLE_DEVICES=UUID,FATHOMDB_SELECTED_UUID=UUID,FATHOMDB_COORDINATED_RESET=mode,FATHOMDB_REQUIRE_LIVE='1',FATHOMDB_EMBED_DEVICE='cuda:0',FATHOMDB_RERANK_DEVICE='cuda:0',XDG_CACHE_HOME=str(B/'model-cache'),HF_HUB_OFFLINE='1',CUDA_CACHE_PATH=str(cache),FATHOMDB_CAPTURE_DIR=str(capture))
 if language=='python':
  native=B/'installed'/arm/'python/lib/python3.12/site-packages/fathomdb/_fathomdb.abi3.so';cmd=[str(B/'installed'/arm/'python/bin/python'),'-I',str(CORE/'coordinate.py')]
 else:
  pkg=B/'installed'/arm/'node/node_modules/fathomdb';native=pkg.parent/'fathomdb-linux-x64-gnu/fathomdb.linux-x64-gnu.node';env.update(FATHOMDB_PACKAGE_DIR=str(pkg),FATHOMDB_NATIVE_PACKAGE='fathomdb-linux-x64-gnu',FATHOMDB_RESET_ACTOR=str(ACTOR),FATHOMDB_RESET_ACTOR_SHA256=ACTOR_SHA);cmd=[str(NODE),'--expose-gc',str(CORE/'coordinate.mjs')]
 native_sha=hashlib.sha256(native.read_bytes()).hexdigest()
 if language=='python':
  record=next(x for x in json.loads((B/'evidence/python-installed-identities.json').read_text()) if x['arm']==arm);assert pathlib.Path(record['module']).resolve()==native.resolve() and native_sha==record['sha256']
 else:assert native_sha==hashlib.sha256((B/'artifacts'/arm/'node/fathomdb.linux-x64-gnu.node').read_bytes()).hexdigest()
 bind_case(f'{language}/{CAMPAIGN}/{mode}',{'argv':cmd,'executable_sha256':hashlib.sha256(pathlib.Path(cmd[0]).read_bytes()).hexdigest(),'native_sha256':native_sha,'coordinator_sha256':hashlib.sha256(pathlib.Path(cmd[-1]).read_bytes()).hexdigest(),'actor_sha256':env.get('FATHOMDB_RESET_ACTOR_SHA256'),'capture_dir':str(capture)})
 if prepare_only:return
 p=None;reason=None;error=None;count=0;last=None;gap=0;saw=False;started=time.monotonic();deadline=started
 with (O/(name+'.log')).open('w') as log,(O/(name+'.samples.jsonl')).open('w') as samples:
  log.write('COMMAND '+repr(cmd)+'\nENV '+repr({k:env.get(k) for k in ['CUDA_VISIBLE_DEVICES','FATHOMDB_SELECTED_UUID','FATHOMDB_COORDINATED_RESET','FATHOMDB_REQUIRE_LIVE','FATHOMDB_EMBED_DEVICE','FATHOMDB_RERANK_DEVICE','XDG_CACHE_HOME','CUDA_CACHE_PATH','FATHOMDB_CAPTURE_DIR','FATHOMDB_PACKAGE_DIR','FATHOMDB_NATIVE_PACKAGE','FATHOMDB_RESET_ACTOR','FATHOMDB_RESET_ACTOR_SHA256']})+'\n');log.flush()
  try:
   p=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True);birth=pathlib.Path(f'/proc/{p.pid}/stat').read_text().split()[21]
   while p.poll() is None:
    now=time.monotonic();gap=max(gap,now-last if last else 0);last=now;r=resource();a=actors();r.update(pid=p.pid,start_ticks=birth,rss=rss(p.pid),elapsed=now-started,actors=a);samples.write(json.dumps(r)+'\n');samples.flush();count+=1;saw|=p.pid in a
    if not r['ok'] or r['rss']>16*2**30 or r['gpu_used']>8*2**30 or r['elapsed']>120 or now-session>1800 or any(x!=p.pid for x in a):reason='guard';break
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
 validate_child(text,mode,native_sha,UUID,private=False)
 print(name,'PASS',native_sha,'gap',gap,flush=True)

if __name__=='__main__':
 assert subprocess.check_output([str(NODE),'--version'],text=True).strip()==NODE_VERSION
 assert hashlib.sha256(ACTOR.read_bytes()).hexdigest()==ACTOR_SHA
 O.mkdir();(O/'source-sha256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p)+'\n' for p in [CORE/'campaign.py',CORE/'coordinate.py',CORE/'coordinate.mjs',ACTOR,NODE.resolve()]))
 with L.open('rb') as lock:
  assert os.fstat(lock.fileno()).st_ino==LOCK_INODE;fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);session=SESSION_START;pre=resource(True);(O/'preflight.json').write_text(json.dumps({'campaign':CAMPAIGN,'arms':ARMS,'shared_venue_started_monotonic':SESSION_START,'action':os.environ.get('FATHOMDB_RESET_ACTION'),'owner_ruling':os.environ.get('FATHOMDB_RESET_AUTHORIZATION'),'fault_resource_rule':os.environ.get('FATHOMDB_FAULT_RESOURCE_RULE','original'),'orin_fault_visibility':os.environ.get('FATHOMDB_ORIN_FAULT_VISIBILITY'),'resources':pre,'actors':actors()}));assert pre['ok'] and not actors()
  if CAMPAIGN!='healthy':
   for language in ['python','node']:
    for arm in ARMS:
     run(arm,language,CAMPAIGN,prepare_only=True);run(arm,language,'recover',prepare_only=True)
  for language in ['python','node']:
   for arm in ARMS:
    run(arm,language,CAMPAIGN);run(arm,language,'recover')
  (O/'completed.json').write_text(json.dumps({'elapsed':time.monotonic()-session,'resources':resource(),'actors':actors()}))

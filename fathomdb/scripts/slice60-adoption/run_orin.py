import ctypes,fcntl,hashlib,json,os,pathlib,shutil,signal,statistics,subprocess,time
if not __debug__:raise RuntimeError('optimized Python is not supported for protocol guards')
if os.environ.get('AGENT_LONG')!='1':raise RuntimeError('set AGENT_LONG=1 for the explicitly approved long run')
B=pathlib.Path(os.environ['SLICE60_ROOT']).resolve();P=pathlib.Path(__file__).resolve().parent;O=pathlib.Path(os.environ.get('FATHOMDB_COST_OUTPUT',str(B/'terra-adoption-evidence'))).resolve();UUID=os.environ['FATHOMDB_GPU_UUID'];LOCK=pathlib.Path(os.environ['FATHOMDB_GPU_LOCK']);LOCK_INODE=int(os.environ['FATHOMDB_GPU_LOCK_INODE']);ORDER='ABBAABBAAB'
if not O.is_relative_to(B):raise RuntimeError('output must be within SLICE60_ROOT')
assert ORDER.count('A')==ORDER.count('B')==5
# Jetson process APIs returned NVML_NOT_SUPPORTED. fuser can only observe
# accessible /proc entries, so this is an observed-peer guard, not host-wide proof.
last_fuser=None;last_details={};last_fuser_rss=None
def proc(pid):
 status=pathlib.Path(f'/proc/{pid}/status').read_text();fields={x.split(':',1)[0]:x.split(':',1)[1].strip() for x in status.splitlines() if ':' in x};stat=pathlib.Path(f'/proc/{pid}/stat').read_text();tail=stat[stat.rfind(')')+2:].split()
 return {'Name':fields.get('Name'),'Tgid':int(fields['Tgid']),'PPid':int(fields['PPid']),'PGID':os.getpgid(pid),'SID':os.getsid(pid),'start_ticks':tail[19],'rss':int(fields.get('VmRSS','0 kB').split()[0])*1024}
def actors():
 global last_fuser,last_details,last_fuser_rss
 f=None;last_fuser=None;last_fuser_rss=None;last_details={}
 try:
  f=subprocess.Popen(['/usr/bin/fuser','/dev/nvhost-gpu','/dev/nvmap'],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True);last_fuser=f.pid
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
 assert f.returncode in (0,1),(f.returncode,stderr);assert 'Permission denied' not in stderr,stderr
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
def run_one(arm,workload,condition,index,cache,prewarm=False):
 name=f'{workload}-{condition}-{index:02d}-{arm}'
 if not resource()['ok'] or actors():raise RuntimeError(f'{name} precheck failed')
 env=os.environ.copy()
 for k in ['CUDA_FORCE_PTX_JIT','CUDA_DISABLE_PTX_JIT','CUDA_FORCE_JIT','CUDA_DISABLE_JIT','CUDA_CACHE_DISABLE','CUDA_CACHE_MAXSIZE','CUDA_MODULE_LOADING','FATHOMDB_COORDINATED_RESET','FATHOMDB_RERANKER_CACHE','FATHOMDB_POOL_MODE']:env.pop(k,None)
 env.update(CUDA_VISIBLE_DEVICES=UUID,FATHOMDB_GPU_UUID=UUID,CUDA_CACHE_PATH=str(cache),FATHOMDB_EMBED_DEVICE='cuda:0',FATHOMDB_RERANK_DEVICE='cuda:0',XDG_CACHE_HOME=str(B/'model-cache'),HF_HUB_OFFLINE='1',FATHOMDB_COST_WORKLOAD=workload,FATHOMDB_COST_PREWARM='1' if prewarm else '0',FATHOMDB_COST_DB=str(O/(name+'.fdb')))
 cmd=[str(B/'installed'/arm.lower()/'python/bin/python'),'-I',str(P/'worker.py')]
 with (O/(name+'.log')).open('w') as log,(O/(name+'.samples.jsonl')).open('w') as samples:
  log.write('COMMAND '+repr(cmd)+'\nENV '+repr({k:env.get(k) for k in ['CUDA_VISIBLE_DEVICES','CUDA_CACHE_PATH','CUDA_FORCE_PTX_JIT','CUDA_DISABLE_PTX_JIT','CUDA_FORCE_JIT','CUDA_DISABLE_JIT','CUDA_CACHE_DISABLE','CUDA_CACHE_MAXSIZE','CUDA_MODULE_LOADING','FATHOMDB_RERANKER_CACHE','FATHOMDB_POOL_MODE','FATHOMDB_EMBED_DEVICE','FATHOMDB_RERANK_DEVICE','XDG_CACHE_HOME','FATHOMDB_COST_WORKLOAD','FATHOMDB_COST_PREWARM','FATHOMDB_COST_DB']})+'\n');log.flush()
  started=time.monotonic_ns();p=None;last=None;gap=0;deadline=time.monotonic();saw=False;reason=None;sample_count=0;rc=None;error=None
  try:
   p=subprocess.Popen(cmd,env=env,stdout=log,stderr=subprocess.STDOUT,start_new_session=True)
   birth=pathlib.Path(f'/proc/{p.pid}/stat').read_text().split()[21]
   while p.poll() is None:
    now=time.monotonic();gap=max(gap,now-last if last else 0);last=now
    r=resource();a=actors();total,owned=owned_rss(p.pid,birth,a);r.update(pid=p.pid,start_ticks=birth,elapsed_ns=time.monotonic_ns()-started,rss=total,owned_processes=owned,fuser_rss=last_fuser_rss,actors=a,fuser_pid=last_fuser,actor_details=dict(last_details));samples.write(json.dumps(r)+'\n');samples.flush();sample_count+=1;saw|=p.pid in a
    if not r['ok'] or r['rss']>16*2**30 or r['elapsed_ns']>120*10**9 or now-session>1800:
     reason='guard';break
    deadline+=.02;time.sleep(max(0,deadline-time.monotonic()))
  except BaseException as exc:
   error=f'{type(exc).__name__}: {exc}'
   raise
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
    rc=p.returncode
   gap=max(gap,time.monotonic()-last if last else (time.monotonic_ns()-started)/1e9)
   try:log.write(f'\nEXIT {rc} GUARD {reason} MAX_SAMPLE_GAP_SECONDS {gap:.6f} SAW_GPU_ACTOR {saw} SAMPLES {sample_count} ERROR {error!r}\n');log.flush()
   except OSError:pass
 text=(O/(name+'.log')).read_text();lines=[x[7:] for x in text.splitlines() if x.startswith('RESULT ')]
 if rc or reason or not saw or not sample_count or gap>.1 or len(lines)!=1:raise RuntimeError(f'{name} invalid; inspect preserved log')
 result=json.loads(lines[0]);first=[x.split(' ',1)[1] for x in text.splitlines() if x.startswith('FIRST_VALID ')];native=[x.split(' ',1)[1] for x in text.splitlines() if x.startswith('NATIVE_MODULE ')];assert len(first)==1 and int(first[0])==result['first_valid_ns'] and len(native)==1 and pathlib.Path(native[0]).resolve()==pathlib.Path(next(x['module'] for x in identities if x['arm']==arm.lower())).resolve();assert result['workload']==workload and result['prewarm']==prewarm and result['close'] and len(result['durations_ns'])==(0 if prewarm else 20)
 result.update(arm=arm,condition=condition,index=index,startup_ns=result['first_valid_ns']-started,max_sample_gap=gap)
 assert result['startup_ns']>0
 return result
O.mkdir();identities=json.loads((B/'evidence/python-installed-identities.json').read_text())
for identity in identities:
 for field,expected in [('module','sha256'),('wheel','wheel_sha256')]:assert hashlib.sha256(pathlib.Path(identity[field]).read_bytes()).hexdigest()==identity[expected]
models=json.loads((B/'evidence/model-cache-identity.json').read_text())
for f in models['files']:
 p=B/'model-cache/fathomdb'/f['file'];assert p.stat().st_size==f['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
(O/'identities.json').write_text(json.dumps({'wheels':identities,'models':models,'worker_sha256':hashlib.sha256((P/'worker.py').read_bytes()).hexdigest()},indent=2))
with LOCK.open('rb') as lock:
 assert os.fstat(lock.fileno()).st_ino==LOCK_INODE;fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);session=time.monotonic();pre=resource(True);(O/'preflight.json').write_text(json.dumps({'resource':pre,'actors':actors(),'lock_inode':LOCK_INODE,'gpu_total_used':'unavailable','peer_visibility':'unprivileged fuser observed-only; NVML process APIs unsupported'}));assert pre['ok'] and not actors()
 results=[]
 for workload in ['embed','rerank']:
  for condition in ['cold','warm']:
   if condition=='warm':
    for arm in ['A','B']:
     cache=O/f'cache-{workload}-warm-{arm}';cache.mkdir();results.append(run_one(arm,workload,'prewarm',0,cache,True))
   for i,arm in enumerate(ORDER,1):
    cache=O/f'cache-{workload}-cold-{i:02d}-{arm}' if condition=='cold' else O/f'cache-{workload}-warm-{arm}'
    if condition=='cold':cache.mkdir()
    r=run_one(arm,workload,condition,i,cache);results.append(r);print(workload,condition,i,arm,r['startup_ns'],r['median_steady_ns'],flush=True)
    (O/'results.json').write_text(json.dumps(results,indent=2))
 (O/'completed.json').write_text(json.dumps({'elapsed':time.monotonic()-session,'final':resource(),'actors':actors()},indent=2))

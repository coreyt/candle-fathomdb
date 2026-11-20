import gc,json,math,os,statistics,time
from pathlib import Path
from fathomdb import Engine,rerank
import fathomdb._fathomdb as native
print("NATIVE_MODULE",os.path.realpath(native.__file__),flush=True)
kind=os.environ['FATHOMDB_COST_WORKLOAD'];prewarm=os.environ.get('FATHOMDB_COST_PREWARM')=='1'
inputs=['the quick brown fox','','a longer paragraph with multiple sentences. Some commas, periods, etc.']
query='What is the capital of France?'
passages=['Paris.','Paris is the capital and most populous city of France.','France is a country in Western Europe; its capital and largest city is Paris, a major global center for art, fashion, and culture.']
rows=[{'id':i+1,'body':body,'score':1.0} for i,body in enumerate(passages)]
engine=None
if kind=='embed':
 engine=Engine.open(os.environ['FATHOMDB_COST_DB'],use_default_embedder=True)
 resolution=engine.open_report().embedder_device_resolution
 assert resolution and resolution.effective_device.kind=='cuda' and resolution.selected_cuda_uuid==os.environ['FATHOMDB_GPU_UUID']
 def workload():
  for value in inputs:
   v=engine.embed(value);assert len(v)==384 and abs(math.sqrt(sum(x*x for x in v))-1)<1e-5
elif kind=='rerank':
 def workload():
  result=rerank(query,rows,3);assert len(result)==3 and {v['id'] for v in result}=={1,2,3} and all(v['ce_score'] is not None and math.isfinite(v['ce_score']) for v in result)
else:raise AssertionError(kind)
workload();first=time.monotonic_ns();print('FIRST_VALID',first,flush=True)
durations=[]
if not prewarm:
 for _ in range(20):
  start=time.monotonic_ns();workload();durations.append(time.monotonic_ns()-start)
 assert len(durations)==20
if engine is not None:engine.close()
gc.collect()
print('RESULT '+json.dumps({'workload':kind,'first_valid_ns':first,'durations_ns':durations,'median_steady_ns':statistics.median(durations) if durations else None,'close':True,'prewarm':prewarm},sort_keys=True),flush=True)

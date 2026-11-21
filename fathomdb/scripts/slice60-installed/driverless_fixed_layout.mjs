import assert from 'node:assert/strict';
import { Engine, EmbedDevicePolicyError } from '/consumer/node_modules/fathomdb/dist/index.js';
const db='/tmp/node-driverless.fdb';
if(process.env.TEST_MODE==='forced'){
 try{await Engine.open(db,{useDefaultEmbedder:true});throw Error('forced CUDA unexpectedly succeeded');}
 catch(e){assert(e instanceof EmbedDevicePolicyError,e);assert.equal(e.ordinal,0);assert.equal(e.kind,'no_visible_cuda_device');console.log('forced-cuda-typed-refusal',e.kind,e.ordinal);}
}else{
 let engine=await Engine.open(db,{useDefaultEmbedder:true});assert.equal(engine.openReport().embedderDeviceResolution.effectiveDevice.kind,'cpu');
 const inputs=['the cat sat on the mat','a cat is on a mat','quantum mechanics dictates the behaviour of subatomic particles'];const vectors=[];
 for(const x of inputs){const v=await engine.embed(x);assert.equal(v.length,384);assert(Math.abs(Math.sqrt(v.reduce((a,b)=>a+b*b,0))-1)<1e-5);vectors.push(v);}
 const dot=(a,b)=>a.reduce((v,x,i)=>v+x*b[i],0),near=dot(vectors[0],vectors[1]);assert(near-dot(vectors[0],vectors[2])>.15&&near-dot(vectors[1],vectors[2])>.15);
 await engine.write([{kind:'doc',body:'Paris is the capital of France.',sourceId:'node-paris'},{kind:'doc',body:'France has its capital in Paris.',sourceId:'node-france'}]);await engine.drain(30000);
 const result=await engine.search('What is the capital of France?',undefined,2,undefined,undefined,undefined,undefined,{limit:2});assert.equal(result.results.length,2);assert(result.results.every(x=>x.ceScore!==null&&Number.isFinite(x.ceScore)));
 await engine.close();engine=await Engine.open(db,{useDefaultEmbedder:true});const saved=await engine.searchTextOnly('Paris');assert(saved.results.some(x=>x.body.includes('Paris')));await engine.close();console.log('driverless-node cpu dim=384 rerank=2 persisted-reopen close=ok');
}

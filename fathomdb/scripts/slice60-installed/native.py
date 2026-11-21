"""Bound direct native qualification children with the existing venue monitor."""
import fcntl
import hashlib
import importlib
import json
import os
import pathlib
import platform
import re
import signal
import subprocess
import time
from campaign import bind_case
from check_cli_database import db_facts, verify_integrity

if not __debug__ or os.environ.get('AGENT_LONG') != '1':
    raise RuntimeError('explicit nonoptimized qualification required')
venue = importlib.import_module('run_orin' if platform.machine() == 'aarch64' else 'run')
SUBJECT = os.environ['FATHOMDB_NATIVE_SUBJECT']
SELECTORS = {
    'product-model': 'candle_bge::completed_model_tests::completed_models_preserve_healthy_or_coordinated_loss_drop_contract',
    'clone': 'prechecked_clone_checks_uuid_before_original_body',
    'oom': 'cuda_pool_policy::ordinary_oom_tests::gpu_ordinary_oom_preserves_generation_allocator_cleanup_and_retry',
}
if SUBJECT not in (*SELECTORS, 'registry', 'cli'):
    raise RuntimeError('unknown native subject')
if venue.CAMPAIGN != 'healthy' and (SUBJECT not in ('product-model', 'clone') or SUBJECT == 'clone' and venue.CAMPAIGN != 'reset-drop'):
    raise RuntimeError('fault subject/mode outside the reviewed action')


def binary(name, digest):
    path = pathlib.Path(os.environ[name]).resolve()
    assert path.is_absolute() and path.is_file() and os.access(path, os.X_OK)
    assert path.stat().st_uid == os.getuid()
    assert hashlib.sha256(path.read_bytes()).hexdigest() == os.environ[digest]
    return str(path)


def command(path, subject):
    if subject in SELECTORS:
        return [path, '--ignored', '--exact', SELECTORS[subject], '--nocapture', '--test-threads=1']
    if subject == 'registry':
        return [path]
    action = os.environ['FATHOMDB_CLI_ACTION']
    assert action in ('gpu', 'reranker-gpu', 'check-integrity', 'dump-row-counts')
    argv = [path, 'doctor', action]
    if action in ('check-integrity', 'dump-row-counts'):
        db = pathlib.Path(os.environ['FATHOMDB_CLI_DATABASE']).resolve()
        assert db.is_relative_to(venue.B) and db.is_file()
        argv.append(str(db))
    return argv+['--json']


def verdict(subject, mode, stdout, stderr):
    text = stdout+'\n'+stderr
    losses = [json.loads(x[len('fathomdb-cuda-context-lost '):]) for x in stderr.splitlines() if x.startswith('fathomdb-cuda-context-lost ')]
    if subject in SELECTORS:
        assert re.search(r'test result: ok\. 1 passed; 0 failed; 0 ignored;', text)
    if subject == 'product-model':
        ready = re.findall(r'completed-models: ready .*uuid=([^ ]+) context_id=([0-9]+)', text)
        assert len(ready) == 1 and ready[0][0] == venue.UUID
        assert text.count('completed-models: models-dropped mode='+mode) == 1
        if mode != 'healthy':
            assert len(losses) == 1 and str(losses[0]['recorded_context_id']) == ready[0][1]
            assert text.count('completed-models: process-primary-reset-returned mode='+mode) == 1
            if mode == 'reset-refuse':
                assert text.count('completed-models: typed-single-batch-rerank-refusal32 ') == 1
        else:
            assert not losses
    elif subject == 'clone':
        assert text.count('prechecked-clone: identity-before-construction uuid='+venue.UUID+' visible-devices=1') == 1
        assert text.count('tensor-last-clone: ready completed-construction synchronized live-bytes>=8388608 mode='+mode) == 1
        assert text.count('tensor-last-clone: final-clone-context-pool-anchor-dropped mode='+mode) == 1
        assert not losses
        if mode == 'reset':
            assert text.count('tensor-last-clone: process-primary-reset-returned') == 1
    elif subject == 'oom':
        for marker in ('ordinary-oom observed allocator=', 'native_status=2', 'ordinary-oom cleanup ', 'ordinary-oom retry-and-drop-complete '):
            assert text.count(marker) == 1
        assert not losses
    elif subject == 'registry':
        assert text.count('registry-consumer actual-cuda-name=') == 1
        assert text.count('registry-consumer mode=cuda known-output=[1.0, 4.0, 9.0, 16.0] post-drop') == 1
        assert not losses
    else:
        value = json.loads(stdout)
        assert isinstance(value, dict) and value
        if os.environ['FATHOMDB_CLI_ACTION']=='check-integrity':verify_integrity(value,db_facts(os.environ['FATHOMDB_CLI_DATABASE']))
        if os.environ['FATHOMDB_CLI_ACTION'] in ('gpu', 'reranker-gpu'):
            assert value['cuda_compiled']
            if os.environ['FATHOMDB_CLI_ACTION']=='gpu':assert value['status'] == 'selected_cuda'
            assert value['effective_device'] == 'cuda:0' and value['selected_uuid'] == venue.UUID
        assert not losses


def case_binding(path, subject, mode):
    return {'argv':command(path,subject),'executable_sha256':hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest(),'subject':subject,'mode':mode}


def run(path, subject, mode, label):
    assert time.monotonic()-venue.SESSION_START < 1800
    argv = command(path, subject)
    database_before=db_facts(os.environ['FATHOMDB_CLI_DATABASE']) if subject=='cli' and os.environ['FATHOMDB_CLI_ACTION'] in ('check-integrity','dump-row-counts') else None
    expected_exit=65 if subject=='cli' and os.environ['FATHOMDB_CLI_ACTION']=='check-integrity' else 0
    bind_case(label,case_binding(path,subject,mode))
    env = os.environ.copy()
    for key in ('CUDA_FORCE_PTX_JIT', 'CUDA_DISABLE_PTX_JIT', 'CUDA_FORCE_JIT', 'CUDA_DISABLE_JIT', 'FATHOMDB_POOL_MODE', 'FATHOMDB_POOL_MAXSIZE', 'FATHOMDB_POOL_RELEASE_THRESHOLD'):
        env.pop(key, None)
    cache = venue.O/('cache-'+label); cache.mkdir()
    env.update(CUDA_VISIBLE_DEVICES=venue.UUID, FATHOMDB_SELECTED_UUID=venue.UUID, FATHOMDB_REQUIRE_LIVE='1', FATHOMDB_COORDINATED_RESET=mode, FATHOMDB_EMBED_DEVICE='cuda:0', FATHOMDB_RERANK_DEVICE='cuda:0', FATHOMDB_CONSUMER_DEVICE='cuda', XDG_CACHE_HOME=str(venue.B/'model-cache'), HF_HUB_OFFLINE='1', CUDA_CACHE_PATH=str(cache))
    (venue.O/(label+'.subject.json')).write_text(json.dumps({'subject':subject,'mode':mode,'argv':argv,'binary_sha256':hashlib.sha256(pathlib.Path(path).read_bytes()).hexdigest(),'env':{k:env[k] for k in ('CUDA_VISIBLE_DEVICES','FATHOMDB_SELECTED_UUID','FATHOMDB_REQUIRE_LIVE','FATHOMDB_COORDINATED_RESET','FATHOMDB_EMBED_DEVICE','FATHOMDB_RERANK_DEVICE','XDG_CACHE_HOME')},'shared_start':venue.SESSION_START,'action':env.get('FATHOMDB_RESET_ACTION'),'owner_ruling':env.get('FATHOMDB_RESET_AUTHORIZATION'),'fault_resource_rule':env.get('FATHOMDB_FAULT_RESOURCE_RULE','original'),'orin_fault_visibility':env.get('FATHOMDB_ORIN_FAULT_VISIBILITY')},indent=2)+'\n')
    p=None; reason=None; samples=0; saw=False; last=None; gap=0; start=time.monotonic();tick=start
    try:
        with (venue.O/(label+'.stdout.log')).open('w') as stdout, (venue.O/(label+'.stderr.log')).open('w') as stderr, (venue.O/(label+'.samples.jsonl')).open('w') as output:
            if not venue.resource()['ok'] or venue.actors():raise RuntimeError('changed pre-child resource/peer condition')
            p=subprocess.Popen(argv,env=env,stdout=stdout,stderr=stderr,start_new_session=True)
            try:birth=pathlib.Path(f'/proc/{p.pid}/stat').read_text().split()[21]
            except FileNotFoundError:
                if subject!='cli' or p.poll() is None:raise
                birth='already-exited-unobserved'
            while p.poll() is None:
                now=time.monotonic();gap=max(gap,now-last if last else 0);last=now
                sample=venue.resource();actors=venue.actors();saw |= p.pid in actors
                if hasattr(venue,'ordinary_owned_rss'):
                    rss, owned=venue.ordinary_owned_rss(p.pid,birth,actors)
                    sample.update(owned_processes=owned,actor_details=dict(venue.last_details))
                else:
                    rss=venue.rss(p.pid)
                    if any(x!=p.pid for x in actors):raise RuntimeError('unknown native GPU peer')
                sample.update(pid=p.pid,start_ticks=birth,rss=rss,actors=actors,elapsed=now-start)
                output.write(json.dumps(sample)+'\n');output.flush();samples+=1
                if not sample['ok'] or rss>16*2**30 or sample.get('gpu_used') is not None and sample['gpu_used']>8*2**30 or now-start>120 or now-venue.SESSION_START>1800:
                    reason='resource/deadline guard';break
                tick+=.02;time.sleep(max(0,tick-time.monotonic()))
    finally:
        if p is not None:
            if p.poll() is None:
                try:os.killpg(p.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:os.killpg(p.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    p.wait()
            else:p.wait()
        gap=max(gap,time.monotonic()-last if last else time.monotonic()-start)
        (venue.O/(label+'.result.json')).write_text(json.dumps({'actual_exit':p.returncode if p else None,'guard':reason,'samples':samples,'max_gap_seconds':gap if samples else None,'observed_main_gpu_actor':saw,'sampling_claim':'sampled native child' if samples else 'short CLI diagnostic; no sampled body/peak/PID credit'},indent=2)+'\n')
    assert p is not None and p.returncode==expected_exit and reason is None and time.monotonic()-start<=120
    assert subject=='cli' and samples==0 or samples and gap<=.1
    assert saw or subject=='cli'
    if not venue.resource()['ok'] or any(pid!=p.pid for pid in venue.actors()):raise RuntimeError('post-child resource/peer condition changed')
    verdict(subject,mode,(venue.O/(label+'.stdout.log')).read_text(),(venue.O/(label+'.stderr.log')).read_text())
    if database_before is not None:assert db_facts(os.environ['FATHOMDB_CLI_DATABASE'])==database_before


if __name__ == '__main__':
    executable=binary('FATHOMDB_NATIVE_BINARY','FATHOMDB_NATIVE_BINARY_SHA256')
    recovery=None
    if venue.CAMPAIGN!='healthy':
        recovery=binary('FATHOMDB_NATIVE_RECOVERY_BINARY','FATHOMDB_NATIVE_RECOVERY_BINARY_SHA256')
    venue.O.mkdir()
    sources=[pathlib.Path(__file__),pathlib.Path(venue.__file__),pathlib.Path(__file__).with_name('campaign.py'),pathlib.Path(__file__).with_name('check_cli_database.py')]
    (venue.O/'source-sha256.txt').write_text(''.join(hashlib.sha256(p.read_bytes()).hexdigest()+'  '+str(p)+'\n' for p in sources))
    with venue.L.open('rb') as lock:
        assert os.fstat(lock.fileno()).st_ino==venue.LOCK_INODE
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        venue.session=venue.SESSION_START;pre=venue.resource(True);actors=venue.actors()
        (venue.O/'preflight.json').write_text(json.dumps({'resources':pre,'actors':actors,'venue':platform.machine(),'peer_visibility':'Orin observed-only; x86 NVML compute+graphics','gpu_total_bytes':'unavailable on Orin'},indent=2)+'\n')
        assert pre['ok'] and not actors
        mode='reset' if SUBJECT=='clone' and venue.CAMPAIGN!='healthy' else venue.CAMPAIGN
        if recovery:
            bind_case(SUBJECT+'-'+mode,case_binding(executable,SUBJECT,mode))
            bind_case('fresh-process-model-recovery-for-'+SUBJECT+'-'+venue.CAMPAIGN,case_binding(recovery,'product-model','healthy'))
        run(executable,SUBJECT,mode,SUBJECT+'-'+mode)
        if recovery:
            run(recovery,'product-model','healthy','fresh-process-model-recovery-for-'+SUBJECT+'-'+venue.CAMPAIGN)
        (venue.O/'completed.json').write_text(json.dumps({'elapsed':time.monotonic()-venue.SESSION_START,'actors':venue.actors(),'resources':venue.resource()},indent=2)+'\n')

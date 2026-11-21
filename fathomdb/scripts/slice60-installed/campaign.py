"""Select a bounded installed-child campaign and validate its actual output."""
import hashlib
import json
import os
import platform
import pathlib
import re
import time


ACTION = None

def configuration(default_arms=('a', 'b')):
    global ACTION
    ACTION = None
    mode = os.environ.get('FATHOMDB_COORDINATED_CAMPAIGN', 'healthy')
    if mode not in ('healthy', 'reset-refuse', 'reset-drop'):
        raise RuntimeError('unknown coordinated campaign')
    arms = os.environ.get('FATHOMDB_ARTIFACT_ARMS', ','.join(default_arms)).split(',')
    if not arms or len(set(arms)) != len(arms) or any(x not in ('a', 'b', 'final') for x in arms):
        raise RuntimeError('explicit distinct a/b/final artifact arms required')
    now = time.monotonic()
    start = float(os.environ.get('FATHOMDB_VENUE_STARTED_MONOTONIC', str(now)))
    if not 0 <= now-start < 1800:
        raise RuntimeError('shared venue deadline expired or in the future')
    if mode != 'healthy':
        if arms != ['final'] or not re.fullmatch(r'seq-[0-9]+', os.environ.get('FATHOMDB_RESET_AUTHORIZATION', '')):
            raise RuntimeError('fault requires final PTX0 subjects and explicit owner ruling')
        if os.environ.get('FATHOMDB_RESET_ACTION') != 'slice60-process-primary-v1' or 'FATHOMDB_VENUE_STARTED_MONOTONIC' not in os.environ:
            raise RuntimeError('fault requires reviewed action and shared venue clock')
        rule = os.environ.get('FATHOMDB_FAULT_RESOURCE_RULE', 'original')
        if rule not in ('original', 'r580-ram40-24-swap-report') or rule != 'original' and platform.machine() != 'x86_64':
            raise RuntimeError('unknown fault resource protocol')
        if platform.machine() == 'aarch64' and os.environ.get('FATHOMDB_ORIN_FAULT_VISIBILITY') != 'observed-only-total-gpu-unavailable':
            raise RuntimeError('explicit owner disposition of Orin fault visibility required')
        if rule == 'r580-ram40-24-swap-report' and (platform.node() != 'windchill3' or os.environ.get('FATHOMDB_GPU_UUID') != 'GPU-5f9cfc90-2be1-06a7-ce39-5a6d294b209b'):
            raise RuntimeError('R580 alternative belongs only to the selected 3090 venue')
        path = pathlib.Path(os.environ['FATHOMDB_RESET_ACTION_FILE']).resolve()
        if not path.is_relative_to(pathlib.Path(os.environ['SLICE60_ROOT']).resolve()):
            raise RuntimeError('action file must be in owned task storage')
        payload = path.read_bytes()
        if hashlib.sha256(payload).hexdigest() != os.environ['FATHOMDB_RESET_ACTION_SHA256']:
            raise RuntimeError('reviewed action digest mismatch')
        ACTION = json.loads(payload)
        expected = {'action':'slice60-process-primary-v1','host':platform.node(),'arch':platform.machine(),
                    'uuid':os.environ['FATHOMDB_GPU_UUID'],'resource_rule':rule,
                    'visibility_rule':os.environ.get('FATHOMDB_ORIN_FAULT_VISIBILITY','nvml-compute-graphics'),
                    'lock':str(pathlib.Path(os.environ['FATHOMDB_GPU_LOCK']).resolve()),
                    'lock_inode':int(os.environ['FATHOMDB_GPU_LOCK_INODE'])}
        if ACTION['venue'] != expected:
            raise RuntimeError('reviewed action venue/resource/visibility mismatch')
    return mode, arms, start


def bind_case(key, actual):
    if ACTION is not None and ACTION['cases'].get(key) != actual:
        raise RuntimeError('case differs from reviewed immutable action: '+key)


def validate_child(text, mode, native_sha, uuid, private=False):
    def row(marker):
        lines = [x[len(marker):] for x in text.splitlines() if x.startswith(marker)]
        assert len(lines) == 1, (marker, len(lines))
        return lines[0]
    prefix = 'fathomdb-cuda-context-lost '
    losses = [json.loads(x[len(prefix):]) for x in text.splitlines() if x.startswith(prefix)]
    if mode == 'recover':
        assert text.count('INSTALLED-COORDINATE fresh-process-recovery post-drop') == 1
        assert not losses
        return
    assert mode in ('healthy', 'reset-refuse', 'reset-drop')
    ready = json.loads(row('INSTALLED-COORDINATE READY '))
    post = json.loads(row('INSTALLED-COORDINATE POST-DROP '))
    assert ready['native_sha256'] == native_sha and ready['mode'] == mode and post['mode'] == mode
    coordinated = row('INSTALLED-COORDINATE coordinated ')
    before, after = ready['pool'], post['pool']
    identifier = ready.get('context_id', before.get('context_id'))
    if coordinated.startswith('{'):
        actor = json.loads(coordinated)
        assert actor['uuid'] == uuid and actor['mode'] == mode and actor['balanced_release'] is True
        assert re.fullmatch(r'[1-9][0-9]*', str(actor['context_id']))
        if identifier is not None:
            assert str(actor['context_id']) == str(identifier)
        else:
            identifier = actor['context_id']
    else:
        assert coordinated == mode and ready['uuid'] == uuid
    if private:
        assert before['status'] == 'private'
    if before['status'] == 'private':
        assert int(before['live_models_after']) == 3
        assert int(before['configured_max_size_bytes']) == 3 << 30
        assert int(before['used_current_bytes']) <= 3 << 30
        assert after['context_id'] == before['context_id'] and after['pool_id'] == before['pool_id']
        assert int(after['live_models_after']) == 2
        assert after['status'] == ('private' if mode == 'healthy' else 'lost')
        if mode != 'healthy':
            assert after['used_current_bytes'] is None and after['reserved_current_bytes'] is None
    if mode == 'healthy':
        assert not losses
    else:
        assert len(losses) == 1 and str(losses[0]['recorded_context_id']) == str(identifier)
    marker = 'INSTALLED-COORDINATE typed-refusal32 '
    if mode == 'reset-refuse':
        cause = json.loads(row(marker))
        assert str(cause[0]) == str(identifier)
        assert str(losses[0]['current_context_id']) == str(cause[1])
        assert losses[0]['driver_error'] == cause[2]
    else:
        assert marker not in text

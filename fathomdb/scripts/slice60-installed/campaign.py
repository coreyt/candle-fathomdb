"""Select a bounded installed-child campaign and validate its actual output."""
import json
import os
import re
import time


def configuration(default_arms=('a', 'b')):
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
    return mode, arms, start


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

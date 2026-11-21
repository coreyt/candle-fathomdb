"""Replay a retained owned-helper exit transition through the actual monitor call."""
import ast
import copy
import errno
import json
import pathlib
import sys
import unittest

FIXTURE = json.loads(pathlib.Path(sys.argv.pop(1)).read_text())
ROOT = pathlib.Path(__file__).resolve().parent


def monitor(filename):
    tree = ast.parse((ROOT/filename).read_text())
    names = {'owned_rss', 'ordinary_owned_rss'}
    functions = [x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name in names]
    run = next(x for x in tree.body if isinstance(x, ast.FunctionDef) and x.name == 'run')
    calls = [x for x in ast.walk(run) if isinstance(x, ast.Call) and isinstance(x.func, ast.Name) and x.func.id in names]
    assert len(calls) == 1
    namespace = dict(CAMPAIGN='healthy', last_fuser=None, last_fuser_rss=0)
    state = {}
    def proc(pid):
        if str(pid) not in state:
            raise FileNotFoundError(errno.ENOENT, 'No such file', f'/proc/{pid}/status')
        return copy.deepcopy(state[str(pid)])
    namespace['proc'] = proc
    exec(compile(ast.fix_missing_locations(ast.Module(body=functions, type_ignores=[])), filename, 'exec'), namespace)
    sample = FIXTURE['earlier_matching_samples'][-1]
    state.update(copy.deepcopy(sample['owned_processes']))
    namespace['last_details'] = copy.deepcopy(sample['actor_details'])
    function = namespace[calls[0].func.id]
    function(FIXTURE['leader'], sample['start_ticks'], [FIXTURE['peer']])
    return namespace, state, function, sample


class ExitedHelper(unittest.TestCase):
    def test_previously_verified_helper_enoent_is_historical_not_current_ownership(self):
        for filename in ['run_orin.py', 'run_orin_node.py']:
            with self.subTest(filename=filename):
                ns, state, call, sample = monitor(filename)
                del state[str(FIXTURE['peer'])]
                ns['last_details'] = {str(FIXTURE['peer']): {'error': 'FileNotFoundError(2, No such file)'}}
                rss, current = call(FIXTURE['leader'], sample['start_ticks'], [FIXTURE['peer']])
                self.assertEqual(set(current), {str(FIXTURE['leader'])})
                self.assertEqual(rss, state[str(FIXTURE['leader'])]['rss'])
                detail = ns['last_details'][str(FIXTURE['peer'])]
                self.assertNotIn('Tgid', detail)
                self.assertEqual(detail['exited_owned_history']['start_ticks'], '55939735')

    def test_live_pid_reuse_is_refused(self):
        for filename in ['run_orin.py', 'run_orin_node.py']:
            with self.subTest(filename=filename):
                ns, state, call, sample = monitor(filename)
                state[str(FIXTURE['peer'])]['start_ticks'] = '55939736'
                ns['last_details'] = {str(FIXTURE['peer']): copy.deepcopy(state[str(FIXTURE['peer'])])}
                with self.assertRaises(RuntimeError):
                    call(FIXTURE['leader'], sample['start_ticks'], [FIXTURE['peer']])

    def test_unseen_gone_pid_and_fault_mode_still_refuse(self):
        for filename in ['run_orin.py', 'run_orin_node.py']:
            for fault in [False, True]:
                with self.subTest(filename=filename, fault=fault):
                    ns, state, call, sample = monitor(filename)
                    if fault:
                        ns['CAMPAIGN'] = 'reset-drop'
                        peer = FIXTURE['peer']
                        del state[str(peer)]
                    else:
                        peer = FIXTURE['peer']+100
                    ns['last_details'] = {str(peer): {'error': 'FileNotFoundError(2, No such file)'}}
                    with self.assertRaises(RuntimeError):
                        call(FIXTURE['leader'], sample['start_ticks'], [peer])


if __name__ == '__main__':
    unittest.main()

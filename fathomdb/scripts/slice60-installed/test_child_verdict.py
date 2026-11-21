"""Exercise the actual launchers' output verdict without a CUDA operation."""
import ast
import importlib
import json
import pathlib
import sys
import tempfile
import types
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))


def output(mode):
    pool = dict(status='private', context_id='42', pool_id='7', live_models_after=3,
                configured_max_size_bytes=3 << 30, used_current_bytes=10)
    post = dict(pool, status='lost' if mode != 'healthy' else 'private', live_models_after=2)
    if mode != 'healthy':
        post.update(used_current_bytes=None, reserved_current_bytes=None)
    rows = ['INSTALLED-COORDINATE READY '+json.dumps(dict(mode=mode, uuid='GPU-test', context_id='42', pool=pool, native_sha256='abc')),
            'INSTALLED-COORDINATE coordinated '+json.dumps(dict(mode=mode, uuid='GPU-test', context_id='42', balanced_release=True)),
            'INSTALLED-COORDINATE POST-DROP '+json.dumps(dict(mode=mode, pool=post))]
    if mode != 'healthy':
        rows += ['fathomdb-cuda-context-lost '+json.dumps(dict(recorded_context_id=42, current_context_id=None, driver_error='CUDA_ERROR_INVALID_CONTEXT'))]
    if mode == 'reset-refuse':
        rows += ['INSTALLED-COORDINATE typed-refusal32 '+json.dumps(['42', None, 'CUDA_ERROR_INVALID_CONTEXT'])]
    return '\n'.join(rows)+'\n'


def verdict(path, mode, text):
    tree = ast.parse(path.read_text())
    run = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'run')
    start = next(i for i, n in enumerate(run.body) if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == 'text' for x in n.targets))
    imports = [n for n in tree.body if isinstance(n, (ast.Import, ast.ImportFrom))]
    namespace = dict(mode=mode, native_sha='abc', name='test', UUID='GPU-test', p=types.SimpleNamespace(returncode=0), count=1, saw=True, gap=.02, reason=None, PRIVATE=True)
    exec(compile(ast.fix_missing_locations(ast.Module(body=imports, type_ignores=[])), str(path), 'exec'), namespace)
    with tempfile.TemporaryDirectory() as folder:
        namespace['O'] = pathlib.Path(folder)
        (pathlib.Path(folder)/'test.log').write_text(text)
        body = ast.Module(body=run.body[start:], type_ignores=[])
        exec(compile(ast.fix_missing_locations(body), str(path), 'exec'), namespace)


class ChildVerdict(unittest.TestCase):
    def test_fault_outputs_are_not_misclassified_as_recovery(self):
        for filename in ['run.py', 'run_orin.py', 'run_orin_node.py']:
            for mode in ['reset-refuse', 'reset-drop']:
                with self.subTest(filename=filename, mode=mode):
                    verdict(ROOT/filename, mode, output(mode))

    def test_x86_node_without_private_observer_uses_actor_identity(self):
        rows = output('healthy').splitlines()
        for i in [0, 2]:
            marker, value = rows[i].split(' ', 2)[1:]
            item = json.loads(value)
            item['pool'] = dict(status='not_built', context_id=None)
            if i == 0:
                item.pop('context_id')
                item.pop('uuid')
            rows[i] = 'INSTALLED-COORDINATE '+marker+' '+json.dumps(item)
        verdict(ROOT/'run.py', 'healthy', '\n'.join(rows)+'\n')

    def test_duplicate_or_wrong_identity_snapshot_refuses(self):
        for filename in ['run.py', 'run_orin.py', 'run_orin_node.py']:
            for text in [output('reset-drop')+output('reset-drop').splitlines()[-1]+'\n', output('reset-drop').replace('"recorded_context_id": 42', '"recorded_context_id": 43')]:
                with self.subTest(filename=filename):
                    with self.assertRaises((AssertionError, RuntimeError)):
                        verdict(ROOT/filename, 'reset-drop', text)


if __name__ == '__main__':
    unittest.main()

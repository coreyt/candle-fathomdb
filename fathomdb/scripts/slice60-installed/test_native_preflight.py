"""Check real launcher selection without permitting any qualification child."""
import ast
import fcntl
import hashlib
import json
import os
import pathlib
import platform
import re
import signal
import subprocess
import sys
import tempfile
import time
import types
import unittest
from unittest.mock import patch
import campaign

SOURCE=pathlib.Path(__file__).with_name('native.py')
TREE=ast.parse(SOURCE.read_text())
FUNCTIONS=[x for x in TREE.body if isinstance(x,ast.FunctionDef)]
SELECTORS=ast.literal_eval(next(x.value for x in TREE.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='SELECTORS' for t in x.targets)))
MAIN=next(x for x in TREE.body if isinstance(x,ast.If) and isinstance(x.test,ast.Compare) and isinstance(x.test.left,ast.Name) and x.test.left.id=='__name__')


def namespace(root,mode='healthy'):
    venue=types.SimpleNamespace(O=root/'output',B=root,UUID='GPU-selected',SESSION_START=time.monotonic(),CAMPAIGN=mode,resource=lambda *args:{'ok':True,'gpu_used':0},actors=lambda:[],rss=lambda pid:0,__file__=str(SOURCE.with_name('run.py')))
    ns={k:globals()[k] for k in ['fcntl','hashlib','json','os','pathlib','platform','re','signal','subprocess','time']}
    ns.update(venue=venue,SELECTORS=SELECTORS,SUBJECT='product-model',__file__=str(SOURCE),bind_case=campaign.bind_case)
    exec(compile(ast.Module(body=FUNCTIONS,type_ignores=[]),str(SOURCE),'exec'),ns)
    return ns,venue


class NativePreflight(unittest.TestCase):
    def tearDown(self):campaign.ACTION=None

    def test_missing_or_wrong_recovery_case_never_starts_fault(self):
        for wrong in [False,True]:
            with self.subTest(wrong_recovery_sha=wrong),tempfile.TemporaryDirectory() as folder:
                root=pathlib.Path(folder);ns,venue=namespace(root,'reset-drop')
                executable=root/'binary';executable.write_text('qualification fixture; never execute');executable.chmod(0o755)
                digest=hashlib.sha256(executable.read_bytes()).hexdigest()
                venue.L=root/'lease';venue.L.touch();venue.LOCK_INODE=venue.L.stat().st_ino
                args=ns['command'](str(executable),'product-model')
                fault={'argv':args,'executable_sha256':digest,'subject':'product-model','mode':'reset-drop'}
                cases={'product-model-reset-drop':fault}
                if wrong:cases['fresh-process-model-recovery-for-product-model-reset-drop']=dict(fault,mode='healthy',executable_sha256='0'*64)
                campaign.ACTION={'cases':cases}
                env={'FATHOMDB_NATIVE_BINARY':str(executable),'FATHOMDB_NATIVE_BINARY_SHA256':digest,'FATHOMDB_NATIVE_RECOVERY_BINARY':str(executable),'FATHOMDB_NATIVE_RECOVERY_BINARY_SHA256':digest}
                with patch.dict(os.environ,env),patch.object(subprocess,'Popen',side_effect=AssertionError('fault child must not start')) as popen:
                    with self.assertRaises(RuntimeError):exec(compile(ast.Module(body=MAIN.body,type_ignores=[]),str(SOURCE),'exec'),ns)
                    popen.assert_not_called()

    def test_each_sdk_prebinds_recovery_before_any_child(self):
        for filename in ['run.py','run_orin.py','run_orin_node.py']:
            for wrong in [False,True]:
                with self.subTest(filename=filename,wrong_recovery_sha=wrong),tempfile.TemporaryDirectory() as folder:
                    root=pathlib.Path(folder);ns,venue=namespace(root,'reset-drop');venue.O.mkdir()
                    def put(name):
                        path=root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b'ABI metadata fixture; never load');return path
                    interpreter=put('installed/final/python/bin/python')
                    module=put('installed/final/python/lib/python3.12/site-packages/fathomdb/_fathomdb.abi3.so')
                    wheel=put('fixture.whl');node=put('node');actor=put('actor.node')
                    digest=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
                    identity=[{'arm':'final','module':str(module),'sha256':digest(module),'wheel':str(wheel),'wheel_sha256':digest(wheel)}]
                    record=put('evidence/python-installed-identities.json');record.write_text(json.dumps(identity))
                    for name in ['installed/final/node/node_modules/fathomdb-linux-x64-gnu/fathomdb.linux-x64-gnu.node','artifacts/final/node/fathomdb.linux-x64-gnu.node','installed/final/node/node_modules/fathomdb-linux-arm64-gnu-tegra/fathomdb.linux-arm64-gnu.node','final/node/native/fathomdb.linux-arm64-gnu.node']:put(name)
                    language='node' if filename=='run_orin_node.py' else 'python'
                    coordinator=SOURCE.with_name('coordinate.mjs' if language=='node' else 'coordinate.py')
                    argv=[str(node),'--expose-gc',str(coordinator)] if language=='node' else [str(interpreter),'-I',str(coordinator)]
                    case={'argv':argv,'executable_sha256':digest(node if language=='node' else interpreter),'native_sha256':digest(module),'coordinator_sha256':digest(coordinator),'actor_sha256':digest(actor) if language=='node' else None,'capture_dir':str(venue.O/(language+'-final-reset-drop-database'))}
                    cases={language+'/reset-drop/reset-drop':case}
                    if wrong:cases[language+'/reset-drop/recover']=dict(case,native_sha256='0'*64)
                    campaign.ACTION={'cases':cases}
                    ns.update(B=root,O=venue.O,UUID=venue.UUID,SESSION_START=time.monotonic(),CAMPAIGN='reset-drop',ARMS=['final'],CORE=SOURCE.parent,NODE=node,ACTOR=actor,ACTOR_SHA=digest(actor),resource=lambda *args:{'ok':True},actors=lambda:[],bind_case=campaign.bind_case)
                    tree=ast.parse(SOURCE.with_name(filename).read_text())
                    functions=[x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name=='run']
                    guards=[x for x in ast.walk(tree) if isinstance(x,ast.If) and any(isinstance(c,ast.Call) and any(k.arg=='prepare_only' for k in c.keywords) for c in ast.walk(x))]
                    guard=min(guards,key=lambda x:len(list(ast.walk(x))))
                    exec(compile(ast.Module(body=functions,type_ignores=[]),filename,'exec'),ns)
                    with patch.dict(os.environ,{},clear=True),patch.object(subprocess,'Popen',side_effect=AssertionError('SDK fault child must not start')) as popen:
                        with self.assertRaises(RuntimeError):exec(compile(ast.Module(body=[guard],type_ignores=[]),filename,'exec'),ns)
                        popen.assert_not_called()

    def test_changed_floors_or_observed_peer_refuse_before_child(self):
        for peer in [False,True]:
            with self.subTest(peer=peer),tempfile.TemporaryDirectory() as folder:
                root=pathlib.Path(folder);ns,venue=namespace(root);venue.O.mkdir()
                venue.resource=lambda *args:{'ok':peer,'gpu_used':0}
                venue.actors=lambda:[123] if peer else []
                executable=root/'binary';executable.write_text('never execute');executable.chmod(0o755)
                with patch.object(subprocess,'Popen',side_effect=AssertionError('precheck must precede child')) as popen:
                    with self.assertRaises(RuntimeError):ns['run'](str(executable),'product-model','healthy','changed-precondition')
                    popen.assert_not_called()

    def test_already_exited_short_cli_uses_real_exit_and_json(self):
        with tempfile.TemporaryDirectory() as folder:
            root=pathlib.Path(folder);ns,venue=namespace(root);venue.O.mkdir()
            executable=root/'short-cli';executable.write_text('#!'+sys.executable+'\nimport json\nprint(json.dumps('+repr({'cuda_compiled':True,'status':'selected_cuda','effective_device':'cuda:0','selected_uuid':'GPU-selected'})+'))\n');executable.chmod(0o755)
            original=subprocess.Popen
            def completed(*args,**kwargs):
                p=original(*args,**kwargs);p.wait(timeout=5);return p
            with patch.dict(os.environ,{'FATHOMDB_CLI_ACTION':'gpu'}),patch.object(subprocess,'Popen',side_effect=completed):
                ns['run'](str(executable),'cli','healthy','short-cli')
            record=json.loads((venue.O/'short-cli.result.json').read_text())
            self.assertEqual(record['actual_exit'],0)
            self.assertEqual(record['samples'],0)

    def test_reranker_schema_has_no_status_field(self):
        with tempfile.TemporaryDirectory() as folder:
            ns,_=namespace(pathlib.Path(folder))
            value={'cuda_compiled':True,'effective_device':'cuda:0','selected_uuid':'GPU-selected'}
            with patch.dict(os.environ,{'FATHOMDB_CLI_ACTION':'reranker-gpu'}):ns['verdict']('cli','healthy',json.dumps(value),'')


if __name__=='__main__':unittest.main()

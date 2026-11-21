"""Check direct-child verdicts without CUDA or a database substitute."""
import ast
import json
import pathlib
import re
import types
import unittest

ROOT=pathlib.Path(__file__).resolve().parent
TREE=ast.parse((ROOT/'native.py').read_text())
NS={'json':json,'re':re,'venue':types.SimpleNamespace(UUID='GPU-selected'),'SELECTORS':{'product-model':'model','clone':'clone','oom':'oom'}}
exec(compile(ast.Module(body=[x for x in TREE.body if isinstance(x,ast.FunctionDef) and x.name=='verdict'],type_ignores=[]),'native.py','exec'),NS)
CHECK=NS['verdict']
STATS='test result: ok. 1 passed; 0 failed; 0 ignored; 0 measured; 1 filtered out; finished in 0.01s\n'
MODEL='completed-models: ready synchronized model-count=2 mode=reset-drop uuid=GPU-selected context_id=42 pool=private\ncompleted-models: process-primary-reset-returned mode=reset-drop\ncompleted-models: models-dropped mode=reset-drop\n'+STATS
LOSS='fathomdb-cuda-context-lost '+json.dumps({'recorded_context_id':42})+'\n'


class NativeVerdict(unittest.TestCase):
    def test_product_fault_needs_single_matching_snapshot_and_normal_test(self):
        CHECK('product-model','reset-drop',MODEL,LOSS)
        for stdout,stderr in [(MODEL,''),(MODEL,LOSS+LOSS),(MODEL,LOSS.replace('42','43')),(MODEL.replace('1 passed','0 passed'),LOSS)]:
            with self.subTest(stdout=stdout,stderr=stderr),self.assertRaises(AssertionError):
                CHECK('product-model','reset-drop',stdout,stderr)

    def test_clone_requires_prechecked_uuid_ready_and_actual_final_owner(self):
        output='prechecked-clone: identity-before-construction uuid=GPU-selected visible-devices=1\ntensor-last-clone: ready completed-construction synchronized live-bytes>=8388608 mode=healthy\ntensor-last-clone: final-clone-context-pool-anchor-dropped mode=healthy\n'+STATS
        CHECK('clone','healthy',output,'')
        for value in [output.replace('GPU-selected','GPU-other'),output.replace('tensor-last-clone: ready','absent'),output.replace('final-clone-context-pool-anchor-dropped','absent')]:
            with self.subTest(value=value),self.assertRaises(AssertionError):CHECK('clone','healthy',value,'')

    def test_oom_needs_cleanup_same_child_retry_and_no_loss(self):
        output='ordinary-oom observed allocator=Private native_status=2\nordinary-oom cleanup before=0 cleaned=0\nordinary-oom retry-and-drop-complete allocator=Private generation=42\n'+STATS
        CHECK('oom','healthy',output,'')
        with self.assertRaises(AssertionError):CHECK('oom','healthy',output.replace('retry-and-drop-complete','absent'),'')
        with self.assertRaises(AssertionError):CHECK('oom','healthy',output,LOSS)


if __name__=='__main__':unittest.main()

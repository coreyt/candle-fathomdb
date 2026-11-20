"""Changed declared headers must invalidate both actual generated branches."""
import os
import unittest
from kernel_build_fixture import result


@unittest.skipUnless(os.environ.get("FATHOMDB_KERNEL_SOURCE_ARCHIVE"), "explicit real CUDA compiler fixture")
class KernelHeaderRebuild(unittest.TestCase):
    def test_header_edit_recompiles_ptx_and_static_moe(self):
        root, _, changed = result()
        ptx = [args for args in changed if "--ptx" in args]
        static = [args for args in changed if "-c" in args and any(str(a).endswith("moe_wmma.cu") for a in args)]
        with self.subTest(branch="PTX"):
            self.assertTrue(ptx, f"header edit reused stale PTX: {root}")
        with self.subTest(branch="static MoE"):
            self.assertTrue(static, f"header edit reused stale static MoE: {root}")

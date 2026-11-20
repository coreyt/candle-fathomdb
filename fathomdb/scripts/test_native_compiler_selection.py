"""Native images must use the compiler selected by the actual PTX builder."""
import os
import unittest
from kernel_build_fixture import result


@unittest.skipUnless(os.environ.get("FATHOMDB_KERNEL_SOURCE_ARCHIVE"), "explicit real CUDA compiler fixture")
class NativeCompilerSelection(unittest.TestCase):
    def test_native_and_ptx_use_the_same_detected_nvcc(self):
        root, initial, _ = result()
        self.assertTrue(any("--ptx" in args for args in initial), root)
        native = [args for args in initial if "--fatbin" in args]
        self.assertEqual(len(native), 11, f"native images bypassed the selected real compiler: {root}")

# Slice60 qualification tools

These tools belong to the owning fork and are excluded from its crate archives.
Source review covers their exact bytes. Raw logs/artifacts remain in selected
owned scratch; passing source review is not runtime or public delivery proof.

- `test_native_compiler_selection.py`, `test_kernel_header_rebuild.py` and
  `kernel_build_fixture.py`: actual forwarding nvcc/compiler and declared-header
  RED/GREEN controls; reuse one saved fixture result via
  `FATHOMDB_KERNEL_REBUILD_RESULT`, never regenerate an oracle.
- [Adoption runner and ABI controls](slice60-adoption/README.md): exact installed
  artifact identities, ABBA/cache/workload protocol, process/resource ownership,
  current24-byte NVML ABI and two-row synthetic stride RED/GREEN. This monitors
  compute and graphics APIs; old compute-only receipts are not graphics proofs.
- [Installed completed-child callers](slice60-installed/README.md): actual
  completed/drained Python/Node owners, healthy actor controls, separately held
  reset/refusal/drop and fresh-process persisted-DB recovery. No reset authority
  is conveyed by these scripts or their review.
- `measure_slice60_artifact_sizes.py --root DIR`: exact linked/archive identity
  and every corresponding2x raw/compressed byte limit. Python linked bytes are
  the wheel member; join its SHA to the actual installed module receipt.
- `measure_slice60_kernel_builds.py --source DIR --output NEWDIR`: explicit
  `AGENT_LONG=1`, CUDA toolkit/compiler/cap and owned Cargo cache; same immutable
  normalized kernel source/lock, two empty targets, two workers, offline locked
  release builds and3x clean Cargo wall-clock criterion. Keep Cargo HTML unit
  timings for dependency preparation versus custom build separately.

The prospective product criteria/tolerances live in FathomDB Slice60 design.
Record all neutral/adverse outcomes and preserve PTX default on any miss or
inconclusive row. Do not tune hosts, rewrite logs, relax cadence/thresholds or
replay an unchanged campaign for a better result.

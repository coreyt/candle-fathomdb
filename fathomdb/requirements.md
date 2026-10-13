# candle-fathomdb requirements, design decisions and tests (FK1)

- Branch: `fathomdb/0.8.28-cudarc-fork`, base `859b8ea1`.
- Plan: `fathomdb/plan.md` revision 3. This file finalizes plan § 4 (the
  requirements), § 5 (decisions DK-1…DK-4) and § 6 (the exact tests and
  commands). The delta is small, so requirements, design and test plan are
  one document with one review, R-FK-PLAN.
- cudarc commit pinned: **`C` = `b777f8d94eedca8334e9331cf520d554b22544b7`** (`b777f8d`). Every
  `<C>` below means that full 40-character sha. `C` passed R-FC-VERIFY on
  2026-10-12 (cudarc fork `fathomdb/review.md`).
- Evidence collected for FK1 is summarized in the "Evidence" lines; the
  research notes are not committed.

## 1. Scope

In scope: K7 (Candle depends on `cudarc-fathomdb` at `C`), the CK-AC-02
private-pool test, any build fix the new cudarc needs (each RED first), the
item record in `FATHOMDB.md`, and qualification at the resulting commit `K`.
K8 (registry dependency, 0.10.4) waits for the owner's publication of
`cudarc-fathomdb` 0.19.10 (plan FK5).

Out of scope: rebasing onto upstream 0.11 (DK-1), SASS embedding (DK-3), a
pool-backed cuBLAS workspace (DK-4), any Candle API change, and a renamed
`candle-kernels` crate (FathomDB Slice 31 plan Q2: `candle-kernels` stays a
git dependency of FathomDB, so K4 and K6 reach FathomDB through its git
patch, not through the registry crates).

## 2. Hosts, cells and guards

| Cell | Host | GPU (index under `CUDA_DEVICE_ORDER=PCI_BUS_ID`) | Driver | Toolkit and build |
| --- | --- | --- | --- | --- |
| K-G1 | `windchill3` | RTX 3090, sm_86 (`CUDA_VISIBLE_DEVICES=0`) | 580.178.04 | `/usr/local/cuda` → 12.6; `CUDARC_CUDA_VERSION=12060`, `CUDA_COMPUTE_CAP=86` |
| K-G2 | GCP lab VM: Spot T4, then on-demand T4, then L4 | T4, sm_75 (L4: sm_89) | branch 580, installed on the VM | CUDA 13.0 toolkit from NVIDIA's apt repository, on the VM; `CUDARC_CUDA_VERSION=13000`, `CUDA_COMPUTE_CAP=75` (L4: 89) |
| K-G3 | Orin (`10.83.10.13`), JetPack 6 | Orin, sm_87 | L4T R36 | 12.6; `CUDARC_CUDA_VERSION=12060`, `CUDA_COMPUTE_CAP=87` |
| K-G4 | RTX 3090 | — | R590+ | 13.1–13.4: UNMEASURED (owner rulings Q4, Q11) |
| K-G5 | Orin, JetPack 7.2.x | — | — | 13.x: UNMEASURED (owner ruling Q5) |

Guards, recorded in every `windchill3` receipt before and after the run:
`nvidia-smi --query-gpu=driver_version --format=csv,noheader` gives
580.178.04 on every line, and `readlink -f /usr/local/cuda` gives the 12.6
directory. Nothing is installed, updated or removed on `windchill3`; the
Quadro K620 (index 2) is never a test device.

K-G2 rules (owner, 2026-10-12): the K-G2 session is approved (one VM, at most
2 hours, destroyed after the run; Spot first, then on-demand T4, then L4).
A Spot VM is used for test and verification only, never for development,
because a preemption loses its disk: the VM receives a source bundle of the
commit under test and returns receipts; no code is written there. The
receipt names the GPU, so a T4 or L4 result is never reported as an RTX 3090
result. The VM installs only driver branch 580 (the `windchill3` branch;
the GCP pilot installed 580.178.04, the `windchill3` version) and the CUDA
13.0 toolkit (`cuda-toolkit-13-0`), so the cell answers the K-G2 question:
Candle built with the 13.0 toolkit runs on a 580 driver. The receipt records
`nvidia-smi` and `nvcc --version`; a 580 point release other than 580.178.04
is recorded, not hidden. The `859b8ea1` control runs in the same VM
session, after the runs at `K`.

Expected on sm_75 (T4, and the x86 release build at
`CUDA_COMPUTE_CAP=75`): `ones_gpu` fails, because the BF16 and F8 fill
kernels are built only for sm_80 and later (`candle-kernels/src/fill.cu`,
`#if __CUDA_ARCH__ >= 800`); the 2026-10-12 T4 build trial saw exactly this
(FathomDB Slice 31 plan § 15 Q13). It must fail equally at the control.
On an L4 (sm_89) it is expected to pass. The `__hmax_nan` guard in
`candle-kernels/src/compatibility.cuh:10` is true for a 13.0 build below
sm_75, which 13.x cannot target, so it is not a risk here.

## 3. Requirements and acceptance criteria

FathomDB REQ31 IDs are in brackets.

### CK-REQ-01 One cudarc [REQ31-07]

`[workspace.dependencies]` declares
`cudarc = { package = "cudarc-fathomdb", git = "https://github.com/coreyt/cudarc.git", rev = "<C>", features = [<unchanged>], default-features = false }`.
The dependency name stays `cudarc`, so Candle source, feature expressions
such as `cudarc/cudnn`, and the re-export `candle_core::cuda::cudarc` are
unchanged. The feature list is unchanged; the fork's marker feature
`fathomdb-private-pool` is not enabled, because the package name already
fails closed against an unpatched cudarc.

**CK-AC-01:**

1. `cargo tree -p candle-core-fathomdb --features cuda -e normal --prefix none | grep -E '^cudarc-fathomdb v' | sort -u`
   prints exactly one line,
   `cudarc-fathomdb v0.19.10 (https://github.com/coreyt/cudarc.git?rev=<C>#b777f8d9)`
   (Cargo prints the fragment as 8 hex characters).
2. `cargo tree -p candle-core-fathomdb --features cuda -e normal --prefix none | grep -E '^cudarc v'`
   prints nothing. The exit status of `cargo tree -i cudarc` is not used:
   the lock file still lists registry `cudarc` packages for the optional
   chains below, so that command exits 0 with "nothing to print".
3. The same two commands with `-p candle-nn-fathomdb` and
   `-p candle-transformers-fathomdb`.

Two optional chains are outside CK-AC-01, because neither feature is
enabled by FathomDB: `candle-ug` (feature `ug`; `ug-cuda` → registry
`cudarc 0.17.8`) and `flash-attn` (`candle-transformers-fathomdb/flash-attn`
→ registry `candle-flash-attn 0.10.2` → registry `candle-core 0.10.2` →
registry `cudarc`). Both appear in the lock file only.

### CK-REQ-02 Private-pool contexts [REQ31-02, REQ31-10]

A Candle device built with `Device::new_cuda_from_context` from a context
made by `CudaContext::new_with_mem_pool` allocates its tensors from that
private pool, returns them to it, and leaves the device's default and
current pools untouched.

**CK-AC-02:** test `device_on_a_private_pool_context_allocates_from_that_pool`
in the new integration-test binary `candle-core/tests/cuda_private_pool.rs`
(§ 5.2), RED at `859b8ea1` (compile failure: registry `cudarc ^0.19.4`,
which resolves to 0.19.10 today, has no pool API) and GREEN at `K`, in
K-G1 and K-G3 (k = 3 each) and in K-G2. R-FK-CODE runs mutation checks:
with `Device::new_cuda(0)` in place of the pool-backed device the test must
fail (at the stream-context assertion, or at `>= 16 MiB` when that assertion
is removed); with a transient 8 MiB default-pool allocation while the
private-pool tensors are live, it must fail at the default pool's
`USED_MEM_HIGH` assertion.

### CK-REQ-03 Delta minimal [REQ31-06]

Only K7, the CK-AC-02 test and any build fix are added. No Candle API
change.

**CK-AC-03:** `git diff --stat 859b8ea1..K -- . ':(exclude)fathomdb' ':(exclude)FATHOMDB.md'`
lists only `Cargo.toml`, `candle-core/tests/cuda_private_pool.rs`, and any
build-fix file; `status.md` justifies each build-fix file. The existing
public items of `candle-core`, `candle-nn` and `candle-transformers` are
unchanged (reviewer reads the diff).

### CK-REQ-04 Static CUDART held [REQ-068]

K4's linkage is unchanged by K7.

**CK-AC-04:** on the K-G1 and K-G3 builds at `K`, for the `candle-core`
test binaries `cuda_private_pool-*`, `cuda_from_context-*` and the
`candle_core-*` lib test binary, and on the `859b8ea1` control builds for
`cuda_from_context-*` and the lib test binary (the control has no
`cuda_private_pool`):

1. `readelf -d <binary>` lists no `NEEDED` entry matching the forbidden
   pattern of FathomDB's `scripts/release/inspect-cuda-artifacts.py`
   (`FORBIDDEN_LIBRARY`: `libcuda`, `libcudart`, `libcublas`, `libcublasLt`,
   `libcurand`, `libcufft`, `libcusolver`, `libcusparse`, `libnvrtc`,
   `libnvjitlink`, `libnvidia-ml`, `libnvml`);
2. `nm -C --defined-only <binary> | grep -c ' cudaGetDeviceCount'` is at
   least 1 (static CUDART is linked in);
3. each control binary gives the same result as its `K` counterpart, and
   `cuda_private_pool` at `K` gives the same result as `cuda_from_context`
   at `K`.

FathomDB's own artifact inspector runs on real wheels and NAPI tarballs at
FathomDB W6; this criterion is the fork-side check.

### CK-REQ-05 CUDA toolkits [REQ31-03]

Candle builds and passes its CUDA tests with the 12.6 toolkit on RTX 3090
and Orin, and with the 13.0 toolkit on a driver-580 GCP T4 (or L4).

**CK-AC-05:** receipts K-G1, K-G2 and K-G3 (§ 5.3), each with every test
failure classified as equal to the `859b8ea1` control on the same host, or
as a defect.

### CK-REQ-06 Items documented [REQ31-06]

**CK-AC-06:** `FATHOMDB.md` lists K1–K8 with commits, upstream status (PR
and issue numbers, upstream file and line) and removal path.

### CK-REQ-07 Publication [REQ31-08]

Version 0.10.4 depends on registry `cudarc-fathomdb` 0.19.10, published from
`C`. K8 is a new code commit, so it is re-qualified before publication.

**CK-AC-07:** at `K8`: K-G1 and K-G3 pass against registry
`cudarc-fathomdb` 0.19.10, CK-AC-01 and CK-AC-04 hold, and
`cargo publish --dry-run` passes for `candle-core-fathomdb`,
`candle-nn-fathomdb` and `candle-transformers-fathomdb` in that order.
Recorded; R-FK-PUB reviews them. (FK5; not part of FK2–FK3.)

### CK-REQ-08 Process and safety [REQ31-11, REQ31-12]

**CK-AC-08:**

1. `status.md` records the RED and GREEN shas; the reviewer re-runs each RED.
2. `review.md` lists each review with model `opus`.
3. No upstream PR, issue or push (plan § 1).
4. The commit-class check passes:
   `git log --format='%h %(trailers:key=Fork-Class,valueonly)' --name-only 859b8ea1..HEAD`
   shows exactly one class per commit; `D` commits touch only `fathomdb/`
   and `FATHOMDB.md`, and no other commit touches them. Each commit's
   `Fork-Class:` trailer sits in the same final paragraph as its
   `Claude-Session:` trailer (a blank line between them makes git ignore
   the class; cudarc R-FC-VERIFY F2).
5. The `windchill3` guard lines are equal before and after every cell.

Classes of the FK2 commits: the RED commit adding
`candle-core/tests/cuda_private_pool.rs` is `L` (a fork-only test of the
fork's dependency); the K7 commit is `P`.

## 4. Design decisions

### DK-1 Base: stay on 0.10.2 (owner, 2026-10-12)

Decision: the fork stays on upstream `0.10.2` (`7c7a8c57`) for FathomDB
0.8.28. A FathomDB todo records the rebase.

Evidence:

- Upstream `0.11.0` (`31f35b14`, 2026-06-26) is 67 commits after `0.10.2`;
  `upstream/main` (`c68b2499`, 2026-10-02) is 65 more. `0.11.0` requires
  `cudarc ^0.19.8`; only `main` requires `^0.19.10` (`e6838306`, #3998).
  Upstream publishes no release notes for these tags.
- The CUDA backend from `0.10.2` to `0.11.0` changes 25 files, +10871/−76
  (`git diff --shortstat 7c7a8c57 0.11.0 -- candle-core/src/cuda_backend candle-kernels candle-core/Cargo.toml Cargo.toml`):
  MMQ/MMVQ GGUF kernels compiled into `libmoe.a` (3 → 15 `.cu` files),
  a CUDA-graph host-to-device cache, a kernel parameter cache, and #3565,
  which makes `BackendDevice::new` use `per_thread_stream()`.
- Applying `7c7a8c57..859b8ea1` onto `0.11.0` conflicts in `Cargo.toml`,
  `candle-core/Cargo.toml` and `candle-core/src/cuda_backend/device.rs`
  (`git merge-tree`). The `device.rs` conflict is semantic: the fork's
  `from_context` uses `default_stream()`.
- None of the Candle APIs FathomDB uses changed in `0.11.0`. On `main`,
  `BertModel::load` adds the `bert` prefix itself, which FathomDB's reranker
  would need to check.
- A rebase gains Slice 31 nothing and adds three re-qualification surfaces:
  static CUDART with the larger `libmoe.a`, new kernels, and stream choice.

Todo for FathomDB (ledger): rebase the Candle fork onto the next upstream
tag that requires `cudarc ^0.19.10`, with these inputs: the three-file
conflict list, the `from_context` stream choice, K4 re-qualification with
the larger `libmoe.a`, the BERT prefix check, and the removal of
`candle-ug` on `main`.

### DK-2 Dependency form: name `cudarc-fathomdb` directly

Decision: Candle's workspace names `cudarc-fathomdb` directly (CK-REQ-01),
by git URL and full `rev` during development and by registry version at K8.

Evidence (Cargo 1.95.0, offline probes; Cargo reference,
"Overriding dependencies" and "Specifying dependencies"):

- `[patch]` matches by package name. A patch
  `cudarc = { package = "<other name>", ... }` is reported as "not used in
  the crate graph", so a patch cannot redirect Candle's `cudarc` to
  `cudarc-fathomdb`.
- `[patch]` is read only from the workspace root and applies transitively,
  so a Candle-side patch would not reach FathomDB.
- The same URL string and full 40-character `rev` on both sides give one
  package. An 8-character `rev` on one side gives two packages and an
  ambiguous `cargo tree -i`.
- A crates-io dependency on a name absent from the registry, supplied by
  `[patch.crates-io]`, resolves, offline and online (R-FK-PLAN measured
  `cudarc-fathomdb = "0.19.10"`, absent from crates.io, patched to a git
  source: `cargo generate-lockfile` succeeds and the tree shows the git
  node).
- crates.io rejects git dependencies, so K8 switches to the registry
  version.

For FathomDB's D-11 (FathomDB decides): the embedder can declare
`cudarc = { package = "cudarc-fathomdb", version = "0.19.10" }` with a root
`[patch.crates-io] cudarc-fathomdb = { git = "https://github.com/coreyt/cudarc.git", rev = "<C>" }`,
the same form FathomDB uses for the Candle fork today. FathomDB's
single-cudarc guard catches a split source.

### DK-3 SASS embedding: no change in Slice 31

Decision: no SASS embedding. A FathomDB todo records it.

Evidence:

- `candle-kernels/build.rs` builds the 11 general kernel files as PTX only
  (cudaforge `nvcc --ptx`; 0.1.5 in FathomDB's lock, 0.1.6 in a fresh
  fork lock), embedded with `include_str!` and loaded
  with `cuModuleLoadData`, so the driver JIT-compiles them. FathomDB's x86
  release builds `CUDA_COMPUTE_CAP=75` (9.2 MiB of PTX, `.target sm_75`),
  which the RTX 3090 runs by JIT. The MoE kernels in `libmoe.a` are
  single-arch SASS with no PTX; FathomDB's models use no MoE kernel.
- Embedding SASS needs a fatbin build and `include_bytes!` loading, which
  changes `candle-kernels`' public `Module` type. That breaks CK-REQ-03.
- Whether 13.1+ SASS runs on driver 580 cannot be measured on the allowed
  hosts (Q4, Q5, Q6), and 13.0 PTX already runs on 580.

Todo for FathomDB (ledger): a fatbin build (SASS sm_75/86/87 plus PTX) for
`candle-kernels`, to allow 13.1+ toolkits on R580. Prerequisites: NVIDIA's
statement on SASS under minor-version compatibility, and a host with a 13.1+
toolkit.

### DK-4 cuBLAS workspace: no Candle change

Decision: Candle creates its cuBLAS handle exactly as today.

Evidence:

- Candle creates one `CudaBlas` and one `CudaRng` per device
  (`candle-core/src/cuda_backend/device.rs:40, 274, 275`). Nothing calls
  `cublasSetWorkspace` in the fork, `0.11.0` or `main`. No Candle crate
  constructs `CudaBlasLT`.
- `CudaBlas::set_workspace` does not exist at `C`, because the cudarc fork
  does not carry upstream cudarc PR #595 (cudarc fork D-F3).

Input to FathomDB D-14, memory outside the private pool: the cuBLAS
workspace, cuRAND generator state, the module load and JIT of the embedded
PTX, and `libmoe.a`'s CUDART registration. Measured by R-FK-PLAN on RTX
3090 with a pool-backed Candle device: the default pool's used and
reserved counters stayed 0 through device construction, a 512×512 F32
`matmul` and `Tensor::rand`, while the private pool held only tensor bytes
(2 MiB after the `matmul`, 0 after drop). The cuBLAS workspace and cuRAND
state therefore come from no memory pool. FathomDB measures memory outside
the pool as the process's device memory (`nvidia-smi
--query-compute-apps=pid,used_memory`, or a `cuMemGetInfo` change on a
discrete GPU; `VmRSS` on Orin, where `cuMemGetInfo` is not a release
signal), and keeps the default-pool counters as a leak check only.
Revisit when #595 lands.

## 5. Tests and commands

### 5.1 Builds

Every build uses its own `CARGO_TARGET_DIR` per source tree and
`CUDA_COMPUTE_CAP` (the commit under test and the `859b8ea1` control are
separate trees). The fork tracks no lock file, so:

1. Build `K` first; its fresh `Cargo.lock` is the cell's lock.
2. Copy that lock into the control tree before building it, so that Cargo
   re-resolves only what differs (the `cudarc` source).
3. The receipt records `sha256sum` of both locks, `diff` of the two locks,
   and `cargo tree -p candle-core-fathomdb --features cuda -e normal` for
   both.
4. The receipt records which CUDA library files the T1 run opened
   (`LD_DEBUG=files`, filtered to `libcuda`, `libcublas`, `libcublasLt`,
   `libcurand` and `libnvrtc`), because cudarc item 9 (built-major
   library loading) decides which files Candle opens.

K4's `build.rs` finds the static CUDA runtime only through `CUDA_PATH`,
so every cell sets it.

### 5.2 CK-AC-02 test design

File `candle-core/tests/cuda_private_pool.rs`, `#![cfg(feature = "cuda")]`,
one `#[test]` so that the pool counters it reads belong to one test in one
process. It uses only `candle_core` public API and the re-exported
`candle_core::cuda::cudarc`, never a separate cudarc dependency.

1. Ordinal 0. The command pins the GPU with `CUDA_VISIBLE_DEVICES`.
2. Create `CudaMemPool::create(0, &MemPoolProps { max_size: 0, release_threshold: 0 })`
   in an `Arc`. The pool is uncapped: on Tegra only about a third of a
   capped pool's `maxSize` is usable, and an uncapped pool plus the default
   pool stay within the roughly four uncapped pools a Tegra process can
   hold.
3. Read the device's default pool and current pool handles
   (`result::device::get_default_mem_pool`, `result::device::get_mem_pool`).
4. Build `CudaContext::new_with_mem_pool(0, pool.clone())` and
   `Device::new_cuda_from_context(ctx.clone())`. Assert
   `ctx.alloc_mode() == AllocMode::Private`,
   `Arc::ptr_eq(ctx.mem_pool().unwrap(), &pool)`, and that the device's
   stream belongs to `ctx`.
5. Baseline after construction: assert `pool.used_current() == 0`; record
   the default pool's `USED_MEM_CURRENT`.
6. Allocate an 8 MiB `F32` tensor and one element-wise result, then
   `device.synchronize()`. Assert `pool.used_current() >= 16 MiB` and
   `pool.reserved_current() >= pool.used_current()`. No `matmul` (cuBLAS
   workspace, DK-4).
7. Drop both tensors and synchronize. Assert `pool.used_current() == 0`.
8. Assert the default and current pool handles equal step 3, and the
   default pool's `USED_MEM_CURRENT` (also checked while the tensors are
   live, in step 6) and `USED_MEM_HIGH` equal their step 5 values.

`cuMemGetInfo` is not used (it is not a release signal on Tegra).

### 5.3 Cells

Environments (all cells also set `CUDA_DEVICE_ORDER=PCI_BUS_ID`):

| Cell | Environment |
| --- | --- |
| K-G1 | `PATH=/usr/local/cuda/bin:$PATH CUDA_PATH=/usr/local/cuda CUDARC_CUDA_VERSION=12060 CUDA_COMPUTE_CAP=86 CUDA_VISIBLE_DEVICES=0` |
| K-G1 at 75 | the same with `CUDA_COMPUTE_CAP=75` (the FathomDB x86 release setting, `scripts/release/cuda-artifact-contract.sh:71` on `release/0.8.28`) |
| K-G2 | `PATH=/usr/local/cuda-13.0/bin:$PATH CUDA_PATH=/usr/local/cuda-13.0 LD_LIBRARY_PATH=/usr/local/cuda-13.0/lib64 CUDARC_CUDA_VERSION=13000 CUDA_COMPUTE_CAP=75 CUDA_VISIBLE_DEVICES=0` (`CUDA_COMPUTE_CAP=89` on L4) |
| K-G3 | `PATH=/usr/local/cuda/bin:$PATH CUDA_PATH=/usr/local/cuda CUDARC_CUDA_VERSION=12060 CUDA_COMPUTE_CAP=87 CUDA_VISIBLE_DEVICES=0` (`/usr/local/cuda` is 12.6 on JetPack 6) |

| Run | Command | At `K` | At `859b8ea1` |
| --- | --- | --- | --- |
| T1 | `cargo test -p candle-core-fathomdb --features cuda --test cuda_private_pool` | k = 3 (K-G1, K-G3), k = 1 (K-G1 at 75, K-G2) | RED: compile failure, recorded (K-G1) |
| T2 | `cargo test -p candle-core-fathomdb --features cuda --test cuda_from_context` | k = 1 (every cell, and K-G1 at 75) | k = 1 |
| T3 | `cargo test -p candle-core-fathomdb --features cuda` (lib and every test binary) | k = 1 | k = 1 (control) |
| T4 | `cargo test -p candle-nn-fathomdb --features cuda` | k = 1 | k = 1 (control) |
| T5 | K-G3 only: `cargo test -p candle-core-fathomdb --test aarch64_linux_cpu` (no `cuda` feature) | k = 1 | k = 1 |
| T6 | CK-AC-01 commands | at `K` | — |
| T7 | CK-AC-04 checks, K-G1 and K-G3 | at `K` | control |
| T8 | `cargo check -p candle-transformers-fathomdb --features cuda` (FathomDB uses its BERT models) | every cell | — |

At 75 the BF16 tests are expected to fail (§ 2); K-G1 at 75 runs T1 and T2
only.

A T3 or T4 failure at `K` is accepted only when the same test fails the same
way at `859b8ea1` on the same host; it is listed in the receipt. Any other
failure is a defect and blocks R-FK-VERIFY.

### 5.4 Re-qualification

Plan § 7 applies. A `fathomdb/`- or `FATHOMDB.md`-only commit needs nothing.

## 6. Owner rulings recorded here

| Date | Ruling |
| --- | --- |
| 2026-10-12 | DK-1: stay on the 0.10.2 base for 0.8.28. |
| 2026-10-12 | K-G2 runs on a GCP VM (driver 580, CUDA 13.0 toolkit on the VM), not on `windchill3`; the `windchill3` CUDA 13.0 runfile is not downloaded. |
| 2026-10-12 | Spot VMs are for test and verification only, never development. |

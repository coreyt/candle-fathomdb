# candle-fathomdb fork plan: Candle on cudarc-fathomdb

- Repository: `coreyt/candle-fathomdb` (a GitHub fork of `huggingface/candle`)
- Branch: `fathomdb/0.8.28-cudarc-fork`, cut from `859b8ea1` (the fork's
  current FathomDB line, published as the `*-fathomdb` 0.10.3 crates plus
  one build-script commit)
- Owner: Corey Thompson. Consumer: FathomDB 0.8.28 Slice 31
  (`fathomadb/fathomdb`, `dev/plans/0.8.28/features/slice-31/plan.md` on
  `release/0.8.28`).
- Companion: the cudarc fork plan, `coreyt/cudarc` branch `fathomdb/0.19.10`,
  `fathomdb/plan.md`.
- Status: plan revision 1 (2026-10-11), written with FathomDB Slice 31 plan
  revision 8. Reviewed by R-FK-PLAN (§ 8) before any fork code is written.

This directory (`fathomdb/`) is this fork's own engineering record. The
Candle work for Slice 31 is planned, specified, test-planned, coded (test
first), reviewed and qualified here. FathomDB tracks it and consumes the
result. It does not re-run Candle's own tests.

## 1. Fork policy (every branch of `coreyt/candle-fathomdb`)

The cudarc fork plan § 1 applies here unchanged, with these names:

- **Remotes:** `origin` is `coreyt/candle-fathomdb`. `upstream` is
  `huggingface/candle`, fetch only, with its push URL set to
  `DISABLED-never-push-upstream`.
- **Branches:** `main` mirrors upstream and carries no fork commit.
  FathomDB lines are `fathomdb/<FathomDB release>-<topic>`, and are never
  rewritten or force-pushed.
- **No pull requests or issues.** Never run `gh pr create`, `gh issue
  create` or `gh repo set-default` in a clone, and never open a PR from the
  web UI. GitHub defaults a fork's PR base to `huggingface/candle`.
- **Commit classes** (`Fork-Class:` trailer):

  | Class | Meaning |
  | --- | --- |
  | `U` | upstream-shaped code |
  | `L` | local-only code |
  | `P` | packaging and versions |
  | `D` | `fathomdb/` and `FATHOMDB.md` only |

  A `D` commit touches nothing else, and no other commit touches those
  paths. The published crates live in subdirectories, so neither path is
  packaged.
- **Pins name code commits.** Receipts follow as `D` commits naming the
  qualified commit.
- **Host safety:** owner rulings Q4, Q5 and Q6, exactly as cudarc fork plan
  § 1.6.

Existing branches (all ancestors of `859b8ea1`, so every pinned commit stays
reachable from this branch) are left as they are:

- `fathomdb-aarch64`;
- `fathomdb-cuda-dynamic-loading-20260811`;
- `fix/tegra-static-cudart-release` and `llm/driverless-cudart-linkage`
  (both `1aefdd00`, which FathomDB `main` and `release/0.8.27` pin);
- `fathomdb/0.8.28-cuda-from-context` (`859b8ea1`).

Deleting any of them is an owner decision outside this plan.

## 2. Starting state (verified 2026-10-11)

| Fact | Evidence |
| --- | --- |
| Base: upstream tag `0.10.2` (`7c7a8c57`) + 10 fork commits, 10 files, +139/−41 | `git log 7c7a8c57..859b8ea1` |
| Workspace depends on `cudarc = { version = "0.19.4", features = [std, cublas, cublaslt, curand, driver, nvrtc, f16, f8, …] }`; `candle-core` enables it through feature `cuda` | `Cargo.toml:43`; `candle-core/Cargo.toml:19,50` |
| `candle-kernels` does not depend on cudarc (it builds PTX with `cudaforge`) and stays a git dependency of FathomDB, because static CUDART is required (FathomDB ADR-0.8.25 driverless CUDA runtime linkage, decision index row 52, REQ-068) | `candle-kernels/Cargo.toml`; FathomDB Slice 31 plan § 15 Q2 |
| Upstream `main` is 0.11.0 on `cudarc = "0.19.8"`; fork `main` (`6e823a43`) is 59 commits behind it | `git rev-list --count 6e823a43..upstream/main` |
| GitHub Actions enabled; upstream workflows (`rust-ci.yml`, `ci_cuda.yaml`, …) need a GPU runner for CUDA, which the fork does not have | `gh api …/actions/permissions`; `.github/workflows/` |
| No item table or engineering record exists on the fork yet | tree at `859b8ea1` |

## 3. Items on this branch (recorded in `FATHOMDB.md`, written in FK1)

Existing items are documented retroactively. Upstream status and removal path
are researched in FK1, not assumed here.

| # | Commits | Item | Class |
| --- | --- | --- | --- |
| K1 | `61f1590c`, `25368139` | Packaging as `candle-core-fathomdb`, `candle-nn-fathomdb`, `candle-transformers-fathomdb`, CPU-safe defaults; 0.10.3 versions | `P` |
| K2 | `2e24bc12` | CPU f16 fallback scoped to Linux aarch64, with test | `L` |
| K3 | `5719d90e` | NVIDIA driver libraries loaded dynamically (cudarc `dynamic-loading`) | `L` |
| K4 | `20ca927b`, `cf02edbc`, `1aefdd00` | Static CUDA runtime: CPU artifacts load without `libcudart`; locate it by target; keep it in shared artifacts | `L` |
| K5 | `73e267d0`, `5b74532e` | `CudaDevice::from_context` and `Device::new_cuda_from_context`, with test | `U` |
| K6 | `859b8ea1` | Kernel build script reruns when `CUDA_PATH` changes | `U` |
| K7 | new (FK2) | Depend on `cudarc-fathomdb` (crate name `cudarc`) instead of registry `cudarc` | `P` |
| K8 | new (FK5) | 0.10.4 versions; registry `cudarc-fathomdb` 0.19.10 | `P` |

## 4. Requirements (draft; finalized in FK1 as `fathomdb/requirements.md`)

FathomDB REQ31 IDs are in brackets.

| Requirement | Acceptance criteria |
| --- | --- |
| **CK-REQ-01 One cudarc** [REQ31-07]. The workspace depends on `cudarc = { package = "cudarc-fathomdb", git = "https://github.com/coreyt/cudarc", rev = <C> }`, where `<C>` is the cudarc commit qualified by R-FC-VERIFY and the same commit FathomDB pins. The Rust crate name stays `cudarc`, and features are unchanged. | **CK-AC-01:** `cargo tree -i cudarc-fathomdb -e normal --features cuda` shows one node at `<C>`; `cargo tree -i cudarc` shows no registry `cudarc` 0.19 node. |
| **CK-REQ-02 Private-pool contexts** [REQ31-02, REQ31-10]. A Candle device built with `Device::new_cuda_from_context` from a context created by `CudaContext::new_with_mem_pool` allocates from that private pool and leaves the device's default pool untouched. | **CK-AC-02:** a new test, failing first (RED) on `859b8ea1` because the API does not exist there, then passing: tensor allocation raises the pool's `used_cur`, drop + sync returns it to 0, and the default-pool handle is unchanged. Passes on RTX 3090 (12.6) and Orin (12.6). |
| **CK-REQ-03 Delta minimal** [REQ31-06]. Only K7 and any build fix are added; no Candle API change beyond what K7 needs. | **CK-AC-03:** `git diff 859b8ea1..<K>` outside `fathomdb/` and `FATHOMDB.md` is limited to manifests, the lockfile and any build fix, each justified in `status.md`. |
| **CK-REQ-04 Static CUDART held** [REQ-068]. K4 behaviour unchanged. | **CK-AC-04:** the shared-artifact check used by FathomDB's CUDA release contract passes against an FK3 build: no `libcudart.so` dependency, and static CUDART retained. The exact check is named in FK1. |
| **CK-REQ-05 CUDA toolkits** [REQ31-03]. Builds and passes Candle CUDA tests with the 12.6 toolkit (RTX 3090, Orin), and with the 13.0 toolkit on RTX 3090 if the owner approves its download. 13.1+ runtime is UNMEASURED on driver 580 because Candle's kernels are PTX (Q4). | **CK-AC-05:** receipts K-G1, K-G2, K-G3 (§ 6). |
| **CK-REQ-06 Items documented** [REQ31-06]. | **CK-AC-06:** `FATHOMDB.md` lists K1–K8 with upstream status and removal path. |
| **CK-REQ-07 Publication** [REQ31-08]. Version 0.10.4 depends on registry `cudarc-fathomdb` 0.19.10. | **CK-AC-07:** `cargo publish --dry-run` for each of the three crates at the R-FK-PUB commit, in dependency order, recorded. |
| **CK-REQ-08 Process and safety** [REQ31-11, REQ31-12]. | **CK-AC-08:** `status.md` red and green shas, each red re-run by the reviewer; `review.md` lists each review with model `opus`; no upstream PR or push; guard logs unchanged. |

## 5. Design decisions (FK1 writes them into `fathomdb/requirements.md` § Design; R-FK-PLAN)

The delta is small, so requirements, design and test plan are one document
with one review (R-FK-PLAN). The cudarc fork has separate reviews because
it carries the pool.

- **DK-1 Base.** Stay on the 0.10.2 base for FathomDB 0.8.28, or rebase onto
  upstream 0.11.x (cudarc 0.19.8)? Record the evidence: the upstream diff
  in the CUDA backend, the effect on K1–K6, and FathomDB's pinned 0.10.x
  API use. Recommendation to test: stay on 0.10.2 for Slice 31, and open a
  FathomDB todo for an 0.11 rebase.
- **DK-2 Dependency form** during development (git rev) and at publication
  (registry version). Record why the dependency names `cudarc-fathomdb`
  directly instead of using a `[patch]` entry, citing Cargo's documented
  rules for patching with a renamed package (verify; do not assume).
- **DK-3 SASS embedding** (FathomDB D-8). Would embedding sm_86/sm_87 SASS
  next to PTX in `candle-kernels` let 13.x builds run on driver 580? What
  would it cost in build time, artifact size and static CUDART? Decide with
  evidence, without assuming; it is not required for Slice 31.
- **DK-4 cuBLAS workspace** (FathomDB D-14). Does Candle need a hook for
  `cublasSetWorkspace` from the pool? Decide with the cudarc fork's D-14
  input. Default: no Candle change in Slice 31.

## 6. Tests and GPU cells (receipts in `fathomdb/qualification/`)

| # | Host | Toolkit / build | Needs | Tests |
| --- | --- | --- | --- | --- |
| K-G1 | `windchill3` RTX 3090, driver 580 | 12.6, `CUDARC_CUDA_VERSION=12060` | present | `cargo test -p candle-core-fathomdb --features cuda` (incl. `cuda_from_context`, CK-AC-02), `-p candle-nn-fathomdb --features cuda`; CK-AC-04 check |
| K-G2 | same | user-local 13.0, `CUDA_PATH=$HOME/opt/cuda-13.0`, `CUDARC_CUDA_VERSION=13000` | owner-approved download | same tests; UNMEASURED by owner decision if declined |
| K-G3 | Orin, JetPack 6 | 12.6, `CUDA_COMPUTE_CAP=87`, `CUDARC_CUDA_VERSION=12060` | present | same tests; `aarch64_linux_cpu` |
| K-G4 | RTX 3090 | 13.1–13.4 | R615 driver (never — Q4) | UNMEASURED |
| K-G5 | Orin, JetPack 7.2.x | 13.2/13.4 | reflash (Q5) | UNMEASURED |

The exact commands and the test list are written in FK1. Every run records
the host guard (cudarc fork plan § 1.6) and pins `CUDA_VISIBLE_DEVICES`.

## 7. Re-qualification

| Change | Re-run |
| --- | --- |
| cudarc pin `<C>` moves (any cudarc code change) | K-G1, K-G3, K-G2 if 13.0 is installed; CK-AC-01 |
| `candle-kernels/build.rs` | all cells; CK-AC-04 |
| `fathomdb/` or `FATHOMDB.md` only | nothing |

## 8. Work packages and reviews

The FathomDB Slice 31 main thread writes documents and creates branches. One
`implementer` subagent at a time writes code in
`/home/coreyt/projects/fathomdb-forks/candle-fathomdb`. Reviews are
independent Opus subagents, as in the cudarc fork plan § 9, recorded in
`fathomdb/review.md`.

| WP | Content | Review | Blocks |
| --- | --- | --- | --- |
| FK0 | Main thread: branch from `859b8ea1`, upstream push disabled, this plan | R-FK-PLAN part 1 (with FathomDB R0-rev8) | FK1 |
| FK1 | Main thread, after the cudarc fork's R-FC-DES (it uses the pool API): `requirements.md` (requirements, DK-1…DK-4 decisions, exact test list and commands); `FATHOMDB.md` K1–K8 with upstream status and removal paths (research subagent) | R-FK-PLAN | FK2 |
| FK2 | Implementer, after the cudarc fork's R-FC-VERIFY: RED test for CK-AC-02 (fails on `859b8ea1`), then K7 pinning `<C>` (GREEN); any CUDA 13.0 build fix RED first | R-FK-CODE | FK3 |
| FK3 | Main thread: K-G1, K-G2, K-G3 receipts | R-FK-VERIFY (CK-AC-01…06, 08) | FathomDB R-PIN for the Candle commit |
| FK4 | (repeat FK2–FK3 if `<C>` moves; § 7) | — | — |
| FK5 | Implementer, after the owner publishes `cudarc-fathomdb` 0.19.10: K8 (registry dependency, 0.10.4); dry runs | R-FK-PUB (formerly FathomDB R-CODE-2b), then owner R-PUB | owner `cargo publish` of the three crates |

## 9. What FathomDB consumes

- the qualified Candle code commit `<K>`, and the cudarc commit `<C>` it
  pins;
- R-FK-CODE and R-FK-VERIFY with no open finding;
- receipts K-G1 and K-G3, plus K-G2 or its owner-decision UNMEASURED;
- after publication, the three 0.10.4 crates built from the R-FK-PUB commit.

## 10. Risks

- **Two cudarc nodes** if any Candle crate keeps a registry `cudarc` edge
  (CK-AC-01).
- **Upstream drift** (0.11.0, 59 commits): DK-1.
- **Static CUDART regression** from a manifest change (CK-AC-04).
- **Accidental upstream PR or push** (§ 1).

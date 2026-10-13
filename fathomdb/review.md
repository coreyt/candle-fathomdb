# candle-fathomdb reviews

Every review is an independent Opus subagent, read-only (plan § 8).

## R-FK-PLAN part 1 (served by FathomDB R0-rev8), 2026-10-11

- Model: `opus` (Claude Opus), high effort, general-purpose, read-only.
- Reviewed: `fathomdb/plan.md` revision 1 at `37bc0b4e`, together with
  FathomDB Slice 31 plan revision 8 (`4a33e887e`) and the cudarc fork plan
  (`74a1665`).
- Verdict: APPROVE-WITH-FIXES. All findings below are fixed in plan
  revision 2; none was deferred.

| Finding | Defect (short) | Disposition in revision 2 |
| --- | --- | --- |
| M4 | git source form not pinned; short vs full `rev` would make two `cudarc-fathomdb` packages | identical URL string and full 40-character `rev` mandated; DK-2 confirms patch resolution before publication |
| M5 | K8 (registry dependency, 0.10.4) was never re-qualified | CK-AC-07 re-qualifies `K8` (K-G1, K-G3, CK-AC-01, CK-AC-04); publication from `K8`; re-qualification row |
| M6 | DK-4 cited a cudarc D-14 that does not exist; DK-3 cited FathomDB D-8 | DK-4 takes cudarc D-2, D-7, D-F3 (PR #595); DK-3 cites cudarc D-8 |
| M8 | upstream Candle is on cudarc 0.19.10, not 0.19.8 | fact corrected; DK-1 reframed (a rebase matches the cudarc fork's base) |
| L2 | wrong `candle-core/Cargo.toml` lines | `:22,60` |
| L4 | class check had no base or command | `859b8ea1..HEAD`, command given; 10 earlier commits classified in § 3 |
| L5 | CK-AC-03 excluded the new test; no lockfile is tracked | test file allowed; receipts record `Cargo.lock` SHA-256 and `cargo tree` |
| L6 | `cargo tree` commands wrong at a virtual workspace root | `-p candle-core-fathomdb`; "did not match" is the expected pass |
| L13 | re-qualification rows missing | rows for source/tests, manifests and K8 |

## R-FK-PLAN (FK1), 2026-10-12

- Model: `opus` (Claude Opus), general-purpose, read-only; it built the
  § 5.2 test in scratch against cudarc `b777f8d` and ran it on RTX 3090
  index 0 (k = 3, pass), and probed CK-AC-01, CK-AC-04 and DK-4.
- Reviewed: `requirements.md`, `FATHOMDB.md` and plan revision 3 at
  `362fc4f2`.
- Verdict: APPROVE-WITH-FIXES (1 High, 6 Medium, 10 Low). All fixed in the
  next commit except M6, which is FathomDB's.

| Finding | Defect (short) | Disposition |
| --- | --- | --- |
| H1 | CK-AC-01 item 2 exits 0 ("nothing to print") because the lock lists registry `cudarc` for optional chains; item 1's fragment is 8 hex characters | CK-AC-01 reads the normal tree (`--prefix none`, `grep '^cudarc v'` empty) and expects `#b777f8d9`; plan § 4 updated; supersedes part-1 L6's "did not match" wording |
| M1 | cell environments lacked `CUDA_PATH` (K4 needs it), `PATH` to `nvcc`, and K-G3's `CUDARC_CUDA_VERSION` | full environment per cell in § 5.3 |
| M2 | control comparison under-specified: no `cuda_private_pool` at the control; independent lock resolution (`^0.19.4` resolves to 0.19.10; cudaforge 0.1.6) | K's lock copied into the control tree, lock diff recorded (§ 5.1); CK-AC-04 compares like binaries; RED rationale and DK-3 version text corrected |
| M3 | K-G1 did not test the x86 release setting `CUDA_COMPUTE_CAP=75` | "K-G1 at 75" runs T1 and T2 |
| M4 | K-G2 silent on the known sm_75 `ones_gpu` failure, the control's session, and the driver version | § 2: `ones_gpu` expected on sm_75 (equal at control), control in the same VM session, driver and `nvcc` recorded |
| M5 | DK-4's default-pool measurement reads 0: cuBLAS workspace and cuRAND state use no pool (measured) | DK-4 records the measurement; D-14 input is per-process device memory (VmRSS on Orin), default-pool counters as a leak check only |
| M6 | FathomDB Slice 31 plan revision 13 still assumes a `windchill3` 13.0 download and says 0.11.0 is on cudarc 0.19.10 | FathomDB's: open for plan revision 14 (recorded in `status.md`) |
| L1 | classes of the FK2 commits unstated | RED test `L`, K7 `P`; `FATHOMDB.md` row K7t |
| L2 | `flash-attn` chain to registry `cudarc` not listed | listed out of scope with `candle-ug` |
| L3 | DK-1 diff stat not reproducible | command given |
| L4 | DK-2 online case now measured | DK-2 updated |
| L5 | CK-AC-04 on K-G1 only | K-G1 and K-G3 |
| L6 | CK-AC-02 has no mutation check | R-FK-CODE runs it with `Device::new_cuda(0)`; must fail at `>= 16 MiB` |
| L7 | plan § 2 date of `c68b2499` | "committed 2026-10-02, fetched 2026-10-12" |
| L8 | `__hmax_nan` guard | noted as no risk for 13.x (§ 2) |
| L9 | loaded CUDA library files not recorded | § 5.1 item 4 (`LD_DEBUG=files`) |
| L10 | no candle-transformers row | T8 `cargo check` |

## R-FK-CODE (FK2), 2026-10-12

- Model: `opus` (Claude Opus), general-purpose, read-only; it re-ran RED at
  `d4ffdf58` and GREEN at `0d6fa138` on RTX 3090 index 0, ran four
  mutations, and checked CK-AC-01, CK-AC-03 and CK-AC-08 at `5572b27f`.
- Verdict: APPROVE-WITH-FIXES (1 Medium, 4 Low).

| Finding | Defect (short) | Disposition |
| --- | --- | --- |
| M1 | default pool checked only after the tensors are dropped; a transient default-pool allocation (mutation m4) passed | fixed at `853324fc` (`L`): default `USED_MEM_CURRENT` checked while the tensors are live and `USED_MEM_HIGH` unchanged at the end; m4 passed the old test and fails the new one at the `USED_MEM_HIGH` assertion; m1 fails; GREEN 3/3 |
| L1 | the literal `Device::new_cuda(0)` mutation fails at the stream-context assertion, not `>= 16 MiB` | `requirements.md` CK-AC-02 and § 5.2 step 8 reworded |
| L2 | SAFETY comment tied the default pool to the primary context | fixed at `853324fc` |
| L3 | explicit `result::init()` redundant | kept: harmless, and the handles are read before any context exists |
| L4 | `cargo fmt` differs in fork code (`device.rs:721`, K5; `aarch64_linux_cpu.rs:7`, K2); clippy `collapsible_match` at `npy.rs:121` (upstream) | not changed: CK-REQ-03 limits this line's delta to K7, its test and build fixes, and both diffs are formatting only in code published as 0.10.3; recorded for the next fork line |

## R-FK-CODE re-check (`853324fc`), 2026-10-12

- Model: `opus` (Claude Opus), general-purpose, read-only; six scratch
  trees, each with its own target directory, on RTX 3090 index 0.
- Verdict: APPROVE. Mutations: a transient default-pool allocation passes
  the old test and fails the new one at `USED_MEM_HIGH`; a held one fails
  at the live `USED_MEM_CURRENT` check; the plain-device mutation fails at
  `>= 16 MiB`; GREEN 3/3. The `USED_MEM_HIGH` assertion is judged sound on
  discrete and Tegra (per-process pools; baseline read after
  construction). Class check over `859b8ea1..4ee4fcea` passes; L1–L4
  dispositions judged fair.
- N1 (wording of § 5.2 step 5 and CK-AC-02): fixed in the commit recording
  this review.

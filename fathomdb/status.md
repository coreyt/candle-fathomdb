# candle-fathomdb status: `fathomdb/0.8.28-cudarc-fork`

Newest entries last. Shas are verified from git.

## FK0 (2026-10-11)

- Branch cut from `859b8ea1`; upstream push URL disabled; plan revision 1
  at `37bc0b4e`, revision 2 at `7e55a579` (R-FK-PLAN part 1, recorded in
  `review.md`).

## FK1 (2026-10-12)

- Owner rulings: DK-1 stay on the 0.10.2 base; K-G2 on a GCP VM with driver
  branch 580 and the CUDA 13.0 toolkit (Spot is test-only, never
  development).
- Written: `requirements.md` (requirements, decisions DK-1…DK-4, tests and
  commands), `FATHOMDB.md` (items K1–K8), plan revision 3 (fact corrections
  and K-G2 venue).
- cudarc commit to pin: `C` = `b777f8d94eedca8334e9331cf520d554b22544b7`
  (cudarc R-FC-VERIFY APPROVE-WITH-NOTES, 2026-10-12).
- R-FK-PLAN (Opus): APPROVE-WITH-FIXES at `362fc4f2`; fixes in the next
  commit (`review.md`).
- Open for FathomDB (R-FK-PLAN M6): Slice 31 plan revision 14 must point
  AC31-03b's 13.0 Candle evidence at K-G2 on GCP, rule where FathomDB's
  13.0 workspace build (T-WS-BUILD) runs, and correct § 14 (0.11.0 is on
  cudarc 0.19.8).
- Next: FK2 (implementer: RED test, then K7).

## FK2 (2026-10-12)

| Step | Commit | Class | Evidence |
| --- | --- | --- | --- |
| RED | `d4ffdf58` | `L` | `cargo test -p candle-core-fathomdb --features cuda --test cuda_private_pool --no-run` fails: E0432 `AllocMode`, `CudaMemPool`, `MemPoolProps` not in `driver`; E0599 no `new_with_mem_pool` (registry cudarc 0.19.10) |
| GREEN (K7) | `0d6fa138` | `P` | root `Cargo.toml` line 43 only; RTX 3090 index 0, K-G1 environment: `cuda_private_pool` 3/3 pass, `cuda_from_context` pass; CK-AC-01 one `cudarc-fathomdb` node `#b777f8d9`, no `cudarc v` line, for all three crates |

- No build fix needed. Guard 580.178.04 ×3 and `/usr/local/cuda-12.6`
  before and after.
- Pre-existing, not from FK2: `cargo fmt --check` differs at
  `candle-core/src/cuda_backend/device.rs:721` (K5) and
  `candle-core/tests/aarch64_linux_cpu.rs:7` (K2); clippy 0.1.95
  `collapsible_match` at `candle-core/src/npy.rs:121` (upstream). The new
  test is clean under rustfmt and clippy `-D warnings`.
- R-FK-CODE (Opus): APPROVE-WITH-FIXES; M1 fixed test-first at
  `853324fc` (`L`); see `review.md`.
- Implementer note: one shared `CARGO_TARGET_DIR` reused a stale test
  binary for mutated and real trees (same hash); those runs were discarded
  and re-run after touching the source. Cells use one target directory
  per tree (`scripts/run-cell.sh`).
- Code commit to qualify: `K` = `853324fc2b9f813eedceb75bef660a06a413ff5b`.
- R-FK-CODE re-check: APPROVE (`review.md`).

## FK3 (2026-10-12/13)

| Cell | Host | Result at `K` = `853324fc` | Receipt |
| --- | --- | --- | --- |
| K-G1 | `windchill3` RTX 3090, 580.178.04, 12.6, cc 86 | pass; T3 297/0/0 (control 296/0/0) | `qualification/2026-10-12-K-G1-K-G3-853324fc.md` |
| K-G1 at 75 | same, cc 75 | pass (T1, T2) | same |
| K-G3 | Orin, JetPack 6, 12.6, cc 87 | pass; T3 298/0/0 (control 297/0/0) | same |
| K-G2 | GCP Spot T4, 580.178.04, CUDA 13.0 toolkit, cc 75 | pass; T3 296/1/0, the one failure `ones_gpu` (sm_75, expected), equal at control | `qualification/2026-10-12-K-G2-853324fc.md` |

- GCP session: VM `fdb-lab-kg2-1` created 00:06:20Z, deleted 00:25:14Z;
  no lab VM remains.
- R-FK-VERIFY (Opus): APPROVE-WITH-FIXES; F1, F2 fixed (`review.md`).

## State: QUALIFIED (2026-10-13)

- **`K` = `853324fc2b9f813eedceb75bef660a06a413ff5b`** pins cudarc
  **`C` = `b777f8d94eedca8334e9331cf520d554b22544b7`**. Commits after `K`
  on this branch are class `D` only.
- For FathomDB R-PIN (plan § 9): pin `C` and `K` with the identical URL
  strings and full revs; receipts K-G1, K-G2 and K-G3 in
  `qualification/`; R-FK-CODE and R-FK-VERIFY have no open finding.
- Carry to FathomDB: the cc 75 x86 release build has no BF16 or F8 kernels
  on any GPU (F2); W6 artifact smoke on a host with only `libcuda.so.1`
  (F5); Slice 31 plan revision 14 (R-FK-PLAN M6); DK-1 and DK-3 todos;
  DK-4 measurement method for D-14.
- Remaining here: FK5 (K8, 0.10.4 on registry `cudarc-fathomdb` 0.19.10),
  after the owner publishes `cudarc-fathomdb`.

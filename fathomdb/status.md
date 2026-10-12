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
- Next: R-FK-CODE (Opus).

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

## Carried to FathomDB (2026-10-13)

- R-FK-PLAN M6: fixed in Slice 31 plan revision 14 (`80ae2a18e` on
  `release/0.8.28`); no Candle-side item is open.
- F2 (no BF16/F8 in the cc 75 x86 build): FathomDB plan D-11 and todos
  ledger caveat `TC-30847709`. F5 (`libcuda.so.1`-only smoke): a T-CUDA
  row in plan § 7, run in W6. DK-1 rebase: todo `TC-509dc8a6`; DK-3
  multi-architecture kernels: `TC-323f15b0`; DK-4 measurement method:
  plan D-14 and `TC-283d4f3a`.
- The Orin cell directory `~/fathomdb-forks/candle-cells` was deleted
  after checking that `qualification/2026-10-12-K-G3-853324fc.log` holds
  every test-result, summary, lock, CK-AC-01, CK-AC-04 and loaded-library
  line of the raw cell output.
- Remaining here: FK5, after the owner publishes `cudarc-fathomdb`.

## FK5 K8 (class P) (2026-10-13)

| Step | Commit | Class | Evidence |
| --- | --- | --- | --- |
| K8 | `cd64715e` | `P` | no RED: packaging and manifests only (root `Cargo.toml` lines 31, 37, 39, 43; `version` in the three crate manifests); re-qualified by CK-AC-07 |

- `K8` = `cd64715ead4f86470b195a9010c4f60f7a4c0833`. Registry
  `cudarc-fathomdb` 0.19.10 is published from `C` =
  `b777f8d94eedca8334e9331cf520d554b22544b7`. The cudarc feature list and
  `default-features = false` are unchanged; `candle-kernels` stays path +
  `0.10.2` (not published by the fork; FathomDB patches it by git, Q2).
- Local checks at `K8`, `windchill3`, Cargo 1.95.0, separate
  `CARGO_TARGET_DIR`, no GPU used:
  - `cargo generate-lockfile`: exit 0. `Cargo.lock` is untracked and
    gitignored (`.gitignore:10`); `git status` clean.
    `sha256sum Cargo.lock` =
    `085e38af2fbfde7c617a57bd57e04a1c86fe1f125fcdfef693d5982beca96c3f`.
  - Lock: `cudarc-fathomdb` 0.19.10,
    `source = "registry+https://github.com/rust-lang/crates.io-index"`,
    checksum `8780d2fe…caf2`. Two registry `cudarc` entries, on the
    optional chains named under CK-AC-01 only: `cudarc 0.17.8` (`ug-cuda`
    0.5.0 → `candle-ug`) and `cudarc 0.19.10` (registry `candle-core`
    0.10.2 → `candle-flash-attn` 0.10.2).
  - CK-AC-01 analog, for each of `candle-core-fathomdb`,
    `candle-nn-fathomdb`, `candle-transformers-fathomdb`:
    `cargo tree -p <crate> --features cuda -e normal --prefix none | grep -E '^cudarc(-fathomdb)? v' | sort -u`
    prints exactly `cudarc-fathomdb v0.19.10` (no git source); no
    `cudarc v` line.
  - `CUDA_PATH=/usr/local/cuda CUDARC_CUDA_VERSION=12060 CUDA_COMPUTE_CAP=86 cargo check -p candle-core-fathomdb --features cuda`:
    exit 0 (`candle-kernels` built 11 PTX and 3 kernels).
  - `cargo publish --dry-run -p candle-core-fathomdb -p candle-nn-fathomdb -p candle-transformers-fathomdb`:
    exit 0; packaged, verified (CPU default) and aborted upload in that
    order. Later crates resolved the unpublished 0.10.4 of earlier ones.

    | Crate | Files | `.crate` SHA-256 |
    | --- | --- | --- |
    | `candle-core-fathomdb-0.10.4` | 108 | `d2daf84a7e6b0c9145c8132cd2313fd6e270cd3f62a2d8749190627a4f3151be` |
    | `candle-nn-fathomdb-0.10.4` | 46 | `cf38982ebafc5d93bb6d34906f52f6a62cf636d6875635e5bffdb6e9b253c5bd` |
    | `candle-transformers-fathomdb-0.10.4` | 210 | `5fe23dbe5493347b2a1662e954271f6737456280c388f2ab14a0d8f4a8eb6261` |

  - Packaged `candle-core-fathomdb` `Cargo.toml`: `[dependencies.cudarc]`
    `version = "0.19.10"`, `package = "cudarc-fathomdb"`, optional,
    `default-features = false`, same features, no `git`;
    `[dependencies.candle-kernels]` `version = "0.10.2"` (registry),
    optional. `.cargo_vcs_info.json` names `K8`. `candle-nn-fathomdb` and
    `candle-transformers-fathomdb` depend on `candle-core-fathomdb` and
    `candle-nn-fathomdb` `0.10.4`.
  - CK-AC-08 item 4 over `859b8ea1..HEAD`: one class per commit; `D`
    commits touch only `fathomdb/` and `FATHOMDB.md`; `K8` touches only the
    four manifests.
- Open for CK-AC-07: K-G1 and K-G3 against registry `cudarc-fathomdb`
  0.19.10 and CK-AC-04 at `K8` (GPU cells, not run here); then R-FK-PUB.

### CK-AC-07 GPU cells at `K8` (2026-10-13)

- K-G1 (RTX 3090, 12.6) and K-G3 (Orin, 12.6) at
  `cd64715ead4f86470b195a9010c4f60f7a4c0833`, control `K = 853324fc`: every
  run equals the control and the 2026-10-12 counts (T3 297 and 298 passed,
  T4 50/0/2, T1 1/0/0 ×3, T5 on the Orin 1/0/0). CK-AC-01: one registry
  `cudarc-fathomdb v0.19.10` node per crate. CK-AC-04: 0 forbidden
  `NEEDED`, static CUDART present. K8 lock `085e38af…` on both hosts.
  Receipt `qualification/2026-10-13-CK-AC-07-cd64715e.md`.
- `windchill3` guard equal before and after (580.178.04; `/usr/local/cuda`
  → 12.6).
- `FATHOMDB.md` usage example now names 0.10.4.
- **Next:** R-FK-PUB (Opus), then the owner-approved publish of the three
  crates in dependency order (FathomDB steward ledger seq-320).

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

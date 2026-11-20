# Installed completed-child qualification

These are qualification-only callers of installed FathomDB artifacts. They do
not add a product API and are not packaged in Candle crates. Actual reset modes
remain held until a separate concrete owner disposition; a healthy run is not
reset evidence. Actor design is in product Slice60 design, and actor C source is
`dev/tools/slice60_cuda_reset_actor.c` in the FathomDB source candidate.

Run Python with the exact installed candidate interpreter:
`python -I fathomdb/scripts/slice60-installed/coordinate.py`.
Run Node with the exact installed candidate runtime and explicit GC:
`node --expose-gc fathomdb/scripts/slice60-installed/coordinate.mjs`.

Required environment: `FATHOMDB_REQUIRE_LIVE=1`, `FATHOMDB_COORDINATED_RESET`
(`healthy`, separately authorized `reset-refuse`/`reset-drop`, or fresh-process
`recover`), `FATHOMDB_CAPTURE_DIR` (one owned synthetic DB directory),
`FATHOMDB_EMBED_DEVICE=cuda:0`, `FATHOMDB_RERANK_DEVICE=cuda:0`,
`CUDA_VISIBLE_DEVICES` and `FATHOMDB_SELECTED_UUID` equal the selected UUID.
Node additionally requires `FATHOMDB_PACKAGE_DIR` (installed thin package),
`FATHOMDB_NATIVE_PACKAGE` (installed platform package), `FATHOMDB_RESET_ACTOR`
and its exact `FATHOMDB_RESET_ACTOR_SHA256`. Pin model/cache, actor, package and
native identities in the external launcher. No credentials or user DB is used.

The outer launcher must hold the existing venue lease, verify host/device and
resource floors, constrain ready child time to120s/session30min, monitor owned
PID/RSS/GPU usage and require exactly one READY/coordinated/POST-DROP marker
(or recovery marker), actual exit0 and no missing body. All constructors and
operations return; both drains complete and producers stay frozen before the
actor synchronizes every primary-context stream. On Orin the private model
count is3 before close and2 after (finite initialized CLS/reranker globals).
Those globals remain until process exit: no module-release or zero opaque
residue claim. The independent owning final-clone test proves actual final
owner destruction. Every fault case needs a separate fresh healthy process
that reopens that exact DB and verifies both authored source IDs/bodies.
Missing GPU, timeout, signal, absent marker or skipped body never counts PASS.
Keep raw logs/samples outside the checkout. Never run actual reset as an
ordinary smoke or use this tool for same-process CUDA recovery.


`run.py` is the reviewed3090-only healthy/recovery launcher. It requires
`AGENT_LONG=1`, `SLICE60_ROOT`, `FATHOMDB_GPU_UUID`, `FATHOMDB_GPU_LOCK`,
`FATHOMDB_GPU_LOCK_INODE`, `FATHOMDB_NODE`, `FATHOMDB_NODE_VERSION`,
`FATHOMDB_RESET_ACTOR` and `FATHOMDB_RESET_ACTOR_SHA256`; optional
`FATHOMDB_ACTOR_OUTPUT` is a new directory under the owned root. Its sibling
coordinate scripts are the exact child bodies. It cannot select a reset mode.
Its40/24GiB RAM floors and installed x64 platform package are local3090 scope,
not an Orin protocol. Before running, independently retain/recheck actual
R580.178.04 driver, host primary CUDA12.6.68, artifact build receipts (Python
manylinux CUDA12.6.3 is a distinct compiler receipt), and all six pinned model
hashes. The launcher does not itself establish driver/toolkit equality. Logs
must bind that preflight to exact launcher/child/actor/package hashes.

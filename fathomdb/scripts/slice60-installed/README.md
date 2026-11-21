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


`run_orin_node.py` is the reviewed healthy-only Node25.9 Tegra A variant.
It uses the same observed-only fuser classification/owned-RSS functions as
`run_orin.py`, plus exact Node version, installed-versus-built Tegra native
hash and separately compiled reviewed actor hash. Configure the same Orin
root/UUID/lock/inode/output and Node/actor parameters; no reset mode exists.
Its raw results retain actual source/pin attribution and visibility limits.

`driverless_fixed_layout.mjs` retains the exact earlier x86 driverless SDK
worker used inside a network-none container: mount the installed package tree
at `/consumer/node_modules`, provide pinned model cache and explicit device
policy, and run fresh containers with `TEST_MODE=cpu` or `forced`. The DB is
`/tmp/node-driverless.fdb` in that fresh container. Its historical hash is
retained; it is not the maintained Tegra linkage/import verdict and a failed
Tegra thin import cannot be relabeled as this SDK lifecycle passing. For Tegra
use the existing FathomDB `scripts/release/smoke/tegra_node_driverless_probe.sh`
and verdict with their exact declared negative-selection/addon-import scope.

The launchers default to `FATHOMDB_COORDINATED_CAMPAIGN=healthy` and accept
`FATHOMDB_ARTIFACT_ARMS=final` for the frozen PTX0 artifact. Fault campaigns
`reset-refuse` and `reset-drop` require final-only subjects, an explicit
`FATHOMDB_RESET_AUTHORIZATION=seq-N` owner-ruling label,
`FATHOMDB_RESET_ACTION=slice60-process-primary-v1`, and one shared
`FATHOMDB_VENUE_STARTED_MONOTONIC` across every child in that venue session.
These environment checks select a reviewed action; they do not grant permission.
Actual resets remain held until the owner separately authorizes the exact
subjects, actor, fault resource/visibility limits and commands. Seq410 covers
healthy work only. Faults use original fault floors, not the healthy-only3090
RAM amendment. Each campaign/language has a separate DB and immediate fresh
same-DB recovery. The cumulative venue deadline is30minutes.

The pre-action bridge checks selected UUID before retaining and available
private context ID before binding/resetting. Installed Orin children require
exactly3live owners, the default3GiB cap and USED≤cap before the action.
`campaign.py` validates distinct healthy/recovery/fault markers, exactly one
identity-matched native loss snapshot for a fault, and cached typed-refusal cause.
The x86 Node observer may be unavailable; then the bridge's validated context ID
supplies identity. Run CPU verdict controls with
`python3 fathomdb/scripts/slice60-installed/test_child_verdict.py`.
Initial actual launcher verdicts rejected six valid fault-output bodies as
recovery; the repaired verdict passes those cases and rejects duplicate/wrong-ID
snapshots. The synthetic driver-ABI wrong-UUID/context RED/GREEN controls live
in the product's `dev/tools/tests/test_slice60_cuda_reset_actor.py`; they perform
no hardware reset and establish no physical-driver survival claim.

Ordinary Orin monitoring additionally retains full verified `nvidia-smi` helper
identity only within one leader PID/birth. A helper that is then independently
confirmed ENOENT is recorded as `exited_owned_history`, with current ownership
unproven, and contributes no current RSS. Unseen PIDs, live reuse/changed birth,
parent/group/session mismatch and other errors still abort. The strict fault
monitor does not use this ordinary-only refinement. This does not prove peer
absence. The original final-Python session remains NOTPASS before model READY,
with recovery NOTRUN; the stopped adoption campaign is never replayed.
Replay the retained raw transition with `python3
fathomdb/scripts/slice60-installed/test_exited_helper.py <fixture.json>`.
The raw fixture SHA256 is
`29af8c8d80af59524dba7c82b962adbbb59c905fb7409a4a6ff20c8427d805f8`;
logs remain in task evidence. Two actual previous-monitor ENOENT errors and two
live-reuse failures preceded the repair; all3 CPU controls now pass. Independent
source review also exercised exit between actor lookup and RSS read. No hardware
reset occurred in these controls.

`native.py` reuses the same x86/Orin monitor functions through normal imports;
SDK launcher entry points still run only when invoked as programs. Native subjects
are fixed selectors: `product-model`, `clone`, `oom`, `registry`, or the existing
read-only CLI `gpu`, `reranker-gpu`, `check-integrity`, `dump-row-counts` actions.
Set `FATHOMDB_NATIVE_SUBJECT`, the exact `FATHOMDB_NATIVE_BINARY` and its
`FATHOMDB_NATIVE_BINARY_SHA256`, plus the same venue/root/output/lease variables.
There is no arbitrary shell/argv route. Rust selectors require1passed/0failed/
0ignored. Normal short CLI diagnostics may finish before a sample; their records
then make no body-sampling, peak-resource or PID claim. Their actual exit/JSON
and before/after floors/observed peers remain checked. CLI diagnostics never
count as model forwarding. Compare two real read-only DB outputs with the
independent SQLite oracle using `check_cli_database.py --database <SDK-db>
--integrity <run1-json> <run2-json> --counts <run1-json> <run2-json>
--integrity-results <run1-result> <run2-result> --counts-results <run1-result>
<run2-result>`; it requires the two authored source IDs/bodies and all five
public canonical table counts. For these just-written fixtures it independently
requires the current dirty FTS sanitation certificate and no root, dependency
closure or erasure-request debt. Physical/semantic checks must be clean; logical
output must be the one exact documented redacted retained-terms diagnosis and
actual exit65. Counts must exit0. Any other finding, cause, phase, redaction or
exit is rejected. Rows/counts/debt facts are checked before and after the CLI.
The initial all-clean/exit0 assumption failed on the actual retained old-subject
DB and remains preserved; accepted ADR0.8.27 CH1 plus parent contract direction
corrected this isolated oracle. No recovery, erasure, mutation, wait or replay
is used to manufacture a clean result.

Fault campaigns additionally require `FATHOMDB_RESET_ACTION_FILE` and its
`FATHOMDB_RESET_ACTION_SHA256`: one immutable reviewed JSON candidate for the
venue, containing its action/host/arch/UUID/resource/visibility/lock/inode and
exact case dictionaries. Every fault AND mandatory fresh recovery case is bound
before the first fault child can start, and rechecked at launch. SDK bindings
include argv, interpreter/native/coordinator/actor hashes and per-case DB path;
native bindings include exact fixed-selector argv, binary hash, subject/mode.
Native faults require the separate healthy model recovery binary and digest.
The owner ruling label and matching action digest are selection checks, not an
authorization grant. One shared venue start applies to all SDK/native cases.

The default fault floors remain original. The optional
`FATHOMDB_FAULT_RESOURCE_RULE=r580-ram40-24-swap-report` is restricted to
windchill3/the selected3090 and remains HELD unless a later fault ruling names
it: RAM40/24GiB start/stop, swap reported without a floor, unchanged observed
8GiB GPU/16GiB owned RSS,8GiB GPU-free start, disk32/16GiB and120s/30min bounds.
Orin faults require explicit future owner acceptance of
`FATHOMDB_ORIN_FAULT_VISIBILITY=observed-only-total-gpu-unavailable`; original
memory/swap/disk floors and strict unknown-peer refusal remain, with no absolute
peer absence or hard total-device8GiB claim. Ordinary approval covers neither.

Source review found native recovery binding order, pre-child peer/floor recheck,
reranker diagnostic schema and already-exited short CLI races before execution.
`test_native_preflight.py` first produced4semantic failures and2errors, then
passed all5controls, including all3SDK prebindings and forbidden Popen on missing
or mismatched recovery. `test_native_verdict.py` and `test_campaign.py` exercise
case output and immutable action/venue selection without a GPU or database mock.

`test_cli_oracle.py --database <actual-SDK-db> --integrity <retained-json>` checks
the actual diagnosis/raw DB, wrong cause/phase/redaction refusal, duplicate or
symlink/hardlink evidence aliases and optimized-execution refusal. The main
oracle requires distinct real report/result paths for the two executions and
refuses `python -O`; native receipt source hashes include the exact oracle.

Final authority/results: seq411 authorized seven3090 faults plus seven fresh
recoveries; all passed. Its original SDK metadata prebinding refusal was fixed
only for the unused Python actor hash and fresh output paths; passed native
cases were not repeated. The initial default-OOM8GiB monitor stopped a real
25,159,598,080-byte transient acquisition before an OOM result. The owner then
explicitly requested one full-card24GiB retry: unchanged test/method returned
native2, Default/typedNone, cleanup0/0 and same-generation retry, exit0. The
isolated monitor/source digest and original failure remain in evidence.
The maintained optional OOM-only guard requires that explicit seq411/known3090
reference; other model/reset limits stay8GiB and ARM ordinary OOM stays8GiB.
Seq412 subsequently authorized Orin release verification and the selected seven
faults plus seven recoveries; all passed with the actual3GiB private pool.
Orin peer visibility remains observed-only and total device bytes unavailable.
No passing suite was repeated for these metadata or monitor changes.

# Slice 60 Orin installed qualification

`run_orin.py` is the Orin-specific outer launcher for the unchanged sibling
`worker.py`. Run only with approved Orin lease and `AGENT_LONG=1`. Configure
`SLICE60_ROOT`, `FATHOMDB_GPU_UUID`, `FATHOMDB_GPU_LOCK`,
`FATHOMDB_GPU_LOCK_INODE`, and `FATHOMDB_COST_OUTPUT` as for the x86 runner.
The root supplies the two installed wheel identities and pinned model identity
receipts. A/B, ABBAABBAAB, separate empty cold caches, per-arm/workload
prewarmed caches, input/output oracles, 20 repeated operations, timing and
result outputs match the reviewed x86 runner.

The Orin monitor uses existing lock inode and fuser over `/dev/nvhost-gpu` and
`/dev/nvmap`; samples retain helper PID and live reported PID names, Tgid,
PPid, process group and start ticks. Unknown observed actors fail the run;
only the child and its process group or the fuser helper are accepted. This
is an observed-peer guard: unprivileged `/proc` access can be denied, and
Orin's NVML process queries returned NOT_SUPPORTED. It does not establish
host-wide absence of other actors. GPU total bytes are unavailable; samples
record null instead of a measured ceiling. Host/RSS floors and timeout guards
follow the reviewed Orin plan. Each sample sums RSS of unique observed owned
TGIDs in the child process group with verified start time, group and session;
the fuser helper RSS is sampled separately when available. Model pool cap/usage evidence comes from
separate completed-child controls, not this unchanged measurement worker.

The original leased UUID/mask diagnostic source and original failures remain
with their raw evidence; they are not adoption or fault executions. The selected
UUID and supported mask are established before the measured run. Historical
unknown-PID and sudo-password outcomes remain unresolved/NOT PASS.

`../slice60-installed/run_orin.py` launches only healthy and fresh-process recovery Python
actors from sibling `coordinate.py` for both installed arms. Configure
`SLICE60_ROOT`, `FATHOMDB_GPU_UUID`, `FATHOMDB_GPU_LOCK`,
`FATHOMDB_GPU_LOCK_INODE` and `FATHOMDB_ACTOR_OUTPUT`; output must be a new
directory under the root. It verifies the three-to-two private model counts,
matching pool and context, configured cap and used bytes in the completed
child. It uses the same observed-only fuser guard and host limits. Neither
launcher provides a real reset mode.


Run `python3 orin-monitor-control.py` for the CPU-only real process-group/
helper cleanup and ownership-accounting control; it does not call CUDA. It
compares both committed variants' ownership functions, tests interrupted helper
reaping, unique TGID RSS accounting and wrong-birth/unknown-peer rejection.


The0.8.30 adoption campaign stopped at its eighth child on a visibility error
and136.911ms sample gap; it is inconclusive and native defaults are not adopted.
The measured runner remains unchanged. Do not replay/retime its unrun cells.
The ordinary healthy actor alone records exact proc-FD EACCES visibility warnings
without treating them as positively observed GPU peers; all other errors and
actual unknown observed actors still fail. Its `fuser-observations.jsonl` keeps
raw stdout/stderr/status/helper and warning IDs. Run
`python3 ../slice60-installed/test_fuser_warning.py ../slice60-installed/run_orin.py`
for the captured-warning/unknown-peer regression. `orin-monitor-control.py`
compares shared proc/RSS logic and exercises the updated ordinary actor's real
helper interruption/reap, TGID accounting and wrong-owner rejection. This does
not reinterpret the stopped campaign or assert host-wide peer absence.

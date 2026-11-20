# Slice 60 installed Python adoption measurement

`run.py` measures the reviewed installed A/PTX and B/native wheels on one
exclusive CUDA device. It requires `AGENT_LONG=1`; run only after source,
artifact, model identities, venue and resource authority are approved. The
source root and selected lock are explicit; `FATHOMDB_COST_OUTPUT` must name a
new directory under `SLICE60_ROOT`. Run Python without optimization; the harness
refuses `-O` so its assertions cannot be disabled. No reset or publication is performed.

```sh
AGENT_LONG=1 \
SLICE60_ROOT=/path/to/owned/qualification \
FATHOMDB_GPU_UUID=GPU-... \
FATHOMDB_GPU_LOCK=/path/to/existing/lock \
FATHOMDB_GPU_LOCK_INODE=123 \
FATHOMDB_COST_OUTPUT=/path/to/new/evidence \
python3 run.py
```

The root supplies `installed/{a,b}/python`, `evidence/python-installed-identities.json`,
`evidence/model-cache-identity.json`, and `model-cache/fathomdb`. The identity
receipts bind module, wheel and model bytes. Each workload (embedding and
standalone reranking) runs separate cold and warm ABBAABBAAB sequences. Cold
processes receive new empty CUDA caches; warm arms each get their own cache,
prewarmed by a separate process. Each measured child validates first output,
then runs 20 validated operations and reports the median. Startup is the
monotonic interval from parent Popen to the child's first validated output.
The worker records the actual imported native module path.

The evidence directory contains identity and preflight receipts, each command,
environment, raw output and exit, sampled resources, PID/start-time and GPU
actor records, per-process JSON results and a final receipt. An error aborts
without erasing partial evidence. GPU peer checks include NVML compute and
graphics lists; sample gaps over 100 ms, resource bounds and missing PID or
output markers fail the run. No forced JIT mode is used. Each venue and each
workload independently retains the plan's >=10% median cold first-valid-output
improvement and <=5% median steady-latency regression limits; warm results
remain reported separately. Build time and artifact sizes need their own
matched receipts and limits. A failed or missing row is inconclusive for
adoption, not a passing result.

`nvml-abi-fixture.c` uses the installed CUDA 12.6 `nvml.h` to print structure
size and field offsets and emit two synthetic records. Compile with
`cc -std=c11 -Wall -Wextra -Werror -I/path/to/cuda/include nvml-abi-fixture.c -o /tmp/nvml-abi-fixture`;
then run `python3 nvml-abi-check.py /tmp/nvml-abi-fixture` to verify both
the historical incorrect stride and corrected two-record decoding.

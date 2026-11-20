# Slice60 Candle migration and kernel design

Status: PROPOSED; input trio2ee39305a78ed1463ff913f71dcd3d45ecbfd84f;
kernels182ceab0547348993b6dbec4b1aed610dcc8b23f; cudarc343b04fa.
FathomDB release0.8.30 seq409 commissions the whole fork work. This amendment
supersedes the old0.8.28 no-rebase/no-native scope only for Slice60. Historical
requirements/qualification remain evidence with their original subjects.
Direct Astra-medium reviews plan/design; direct Sol6.2-high reviews code;
direct Terra verifies actual affected tests/artifacts independently.

## Needs and source design

Consumers need maintained source without sacrificing private allocator,
driverless mapping, baseline ARM CPU safety or .29 typed loss/drop behavior.
Select published upstream Candle0.11.1 source
59f8e903ca80a32ea7f8514b39748fc979e69e82, authenticated by registry
candle-core0.11.1 .cargo_vcs_info.json. Current upstream main1a49dc27 is a
comparison only. Keep unpublished fork0.12.0 package names, trimmed workspace
and CPU-safe defaults; kernels become0.11.1 source with qualified local deltas.
Use exact qualified cudarc0.20.0. No publication/new dtype/backend or cutile
adoption. Upstream removed ug; selected graph must lose its old cudarc0.17.8
edge. Existing-context public constructor remains necessary and must keep its
existing default-stream semantics rather than silently using new per-thread
stream behavior. Raw F32 helper retains its checked borrowed BLAS guard before
pointer guards and handle check immediately before unchanged raw GEMM.

| Delta | Disposition / falsifiable requirement |
| --- | --- |
| K1 | Retain trio rename, library identity, trimmed workspace/default-empty. |
| K2 | Retain LinuxARM gemm no-F16 and typed F16 matmul refusal; new upstreamNEON work is not proof of fullfp16 baseline portability. |
| K3 | Retain dynamic-loading; upstream0.11.1 dynamic-linking still violates driverless load. |
| K4/K6 | Retain static whole-archive CUDART, CUDA_PATH target search/rerun and header/source rebuild inputs; no forbidden NVIDIA DT_NEEDED. |
| K5 | Retain existing-context constructor with tracked private pool/default stream and owning cuda_from_context tests. |
| K7/K7t | Retain renamed exact cudarc and actual private-pool isolation/accounting test. Marker absence must not alter any allocator or product tegra-pool. |
| K8/K9 | Replace old publication assumptions with exact unpublished Git cohort; match kernel source, package graph and downstream normalized graph. |
| .29 raw F32 | Preserve admitted checked handle boundary and exact dimensions/strides/F32 compute/algo; healthy output and lost-token refusal controls execute real helper. |

Upstream zip9.1.3 defaults-disabled and tokenizer0.23.1/fancy-regex are selected
upstream requirements, not a general dependency sweep. Inspect actual product
model use/safetensors and authored token-ID/model oracles. Product direct
tokenizer remains independently pinned unless a required compatibility fix is
demonstrated. No generated oracle, model byte change or retrospective tolerance.

## Kernel image treatment

Selected family set is all11 existing module IDs: Affine, Binary, Cast, Conv,
Fill, Indexing, Quantized, Reduce, Sort, Ternary, Unary. Same-source baseline
keeps existing PTX. Treatment uses CUDA12.6 nvcc --fatbin with explicit gencode
rows: x86 native75+86 and compute75PTX; Tegra native87+compute87PTX. Use one
build-only CANDLE_CUDA_NATIVE switch to compare identical source/features;
no public product runtime configuration. Retain PTX text for existing API and
inspection; Module exposes optional binary image; owning Candle cache loads it
through Ptx::from_binary, otherwise existing PTX. NVIDIA chooses native or PTX
within the image. Existing typed errors propagate without retry/fallback after
loss. User custom PTX remains unchanged. Source build tracks the switch/headers.

Native86 may include>=80 BF16/F8 symbols while PTX75 lacks them; product remains
F32 and no new dtype support is claimed. Native75 has inspection only, no
selected hardware. MoE/static quantized archive remains explicitly native-only
for its build target; it is outside selected F32 product paths, carries no PTX
fallback and receives no inferred newer-device support. Inspect its actual bytes.

Prospective adoption: all correctness/lifetime/refusal controls pass; five
interleaved fresh processes per arm in ABBAABBAAB order; same driver/toolkit/
model/input/features. Empty owned cache cold and isolated prewarmed cache warm.
Median cold startup through first validated output improves>=10% on both
selected venues; median20-operation steady latency regresses<=5%; clean kernel
build wall time<=3x; compressed and unpacked linked bytes<=2x. Record old source
comparison separately, actual wall times/bytes and all adverse/neutral results.
Failed/inconclusive criteria retain PTX product default, no posterior tuning.
JIT-associated cost is cold-minus-warm, not a perfect causal JIT timer.

## TDD and qualification

Semantic native RED: real known-output F32 controls under CUDA_DISABLE_PTX_JIT=1
fail on actual PTX-only baseline, then pass image candidate; do not count compile
failure, missing GPU or inspection as RED. PTX arm sets CUDA_FORCE_PTX_JIT=1
and unsets disable, native arm sets disable=1 and unsets force. Execute small
hand-authored exact integer F32 arithmetic/reduction/matmul outputs plus actual
BGE/rerank on selected product consumers. Preserve existing human-set model
tolerances; CPU/GPU byte equality is retired. Inspect every image SASS/PTX
target/ISA/family symbol, trace linked packaged artifacts to exact sources.
Any new behavior defect receives own semantic RED before minimal GREEN;
passing migrated controls are preservation, never retroactive RED.

Run actual cuda_private_pool test (context identity, private USED/RESERVED,
default/current pool unchanged, healthy last-owner release), cuda_from_context,
checked raw F32 helper, aarch64_linux_cpu plus affected core/nn CPU tests.
Cudarc owning suites are qualified there, not copied here. Product tests own
BGE/reranker/engine/drop and installedPython/Node/CLI proof, including driverless
CPU/auto/forced refusal and fresh-process persisted reopen. CPU seams cannot
close original Orin reset defect; actual positive successor retains history.

Venue/protocol: exclusive existing locks;3090 UUID
GPU-5f9cfc90-2be1-06a7-ce39-5a6d294b209b on R580.178.04/CUDA12.6;
AGXOrin64 at10.83.10.13 JetPack6/CUDA12.6. NeverK620/host reset/driver or
primary-toolkit changes. Healthy source/native work is selected; real fault
children remain held until concrete product source/protocol/actor/artifacts and
venue/resource authority are reviewed and supplied by parent. Product design
selects120s ready-child/30min venue/8GiB device/16GiB ownedRSS, quiescent
completed construction, typed refusals/close/last-clone markers/normal exit0 and
fresh-process recovery, with no overlapping same-process CUDA participant.

Commit classes remain D only fathomdb/ and top-level FATHOMDB.md, P packaging/version manifests, U upstream-shaped
code/tests, L local driverless/ARM/image integration. Each code commit names
its actual tests/RED/GREEN where applicable. Qualified code pin precedes D
receipts; a common code pin may serve trio and kernels only after complete
source identity proof. StandaloneSDK independent patch/mirror proof is product
owned. No upstream writes/PR/issues/default change, publication, forcepush,
shared mutable native module/target/venv or ambient checkout edits.

## Consolidated FIX-1 selections

Candle Fork-Class:D owns both fathomdb/ and top-level FATHOMDB.md (historical
plan1); these files are not packaged. This differs from cudarc's P inventory.
Keep upstream graph-cache enable_cuda_graph_htod_cache/TLS CudaSlice ownership
inactive: no selected product caller. Any future caller needs loss-ownership
review. Portable root/archive/standalone graphs bind kernels0.11.1 to actual
qualified code and coalesce logical file/HTTPS/trio/kernel identities together
only when proven; existing split is not presumed gone.

All11 module images are inspected; actual native/PTX output launches selected
for Fill(fill_f32:ones4), Affine(affine_f32:[1,2,3,4]×2+1=[3,5,7,9]),
Binary(badd_f32:opposite ordered1..4 sum=[5;4]), Cast(cast_u32_f32:1..4),
Indexing(is_u32_f32:indices3,1 ->4,2), Reduce(fast_sum_f32:sum1..4=10),
Unary(existing F32 square symbol:[1,4,9,16]). Owning tests resolve actual
module/function then launch/read exact output; no-skip native86/87 controls.
Conv/Quantized/Sort/Ternary, native75 and MoE remain inspected-only with no
new runtime claim. RED isolates actual Fill module load on a healthy GPU with
JIT disabled; matched healthy PTX Fill proves device/library preconditions.
An sm90-only/no-PTX owned fixture must return actual NO_BINARY_FOR_GPU on86/87;
valid Fill plus absent symbol must return NOT_FOUND without launch. Product
consumes these real statuses through its actual classifier/policy seams,
checking Incompatible vs ProbeFailed and auto report vs forced typed refusal.
No global JIT variable alone attributes failure. Existing product BGE EU-4
384dimensions/unitnorm<1e-5/cat-vs-finance cosinegap>0.15, reranker
cpu_gpu_logits_close abs<1e-2 and batch/perpair abs<1e-3 remain unchanged.
Validate loader HF revision/file hashes and reranker revision/three digests
against actual caches before any model trials; no generated model oracle.

Apply cold>=10% benefit and steady<=5% regression separately to embedding
(EU-4 three unitnorm inputs) AND reranking(existing cpu_gpu_logits_close query/
passages), both venues, no cherry-picking. Release profiles and same-source
lock/features/model bytes; actual adoption runs have neither JIT force nor
disable. ABBAABBAAB is independent per workload/venue/cold-or-warm condition.
Cold cache new per process; warm cache independently primed per arm. Fixed20
steady calls; clean build empty target per arm/same dependency cache/fixedjobs.
Build<=3x. Every linkedPython native/wheel, Node native/platform tarball andCLI
executable/archive raw/compressed size<=2x with identical compression options.
Retain all attempts and non-adoption when any criterion fails/inconclusive.

Retain seq376 frozen pre-loss finite native live set until restart, known
count/byte ceiling and no growth over32 refused calls. Opaque native host
bytes have no hard bound;16GiBRSS is only a session stop. Native counters after
loss unavailable/cached only. Owning spies prove native zero-dispatch/handle
counts; real children prove typed single/batch/rerank refusal/same firstcause,
no-forward detection, distinct lastclone, known model counts/passive resource
samples, normalclose/drop exit0 and fresh-process recovery. No post-loss native
pool inspection or inference that close reclaimed opaque library residue.

cuda_private_pool proves tensor release/isolation, not final pool destruction.
Separate cudarc owning cleanup_healthy_last_owner_holds_admission_through_one_native_destroy
and cleanup_known_loss_disarms_last_pool_owner_without_native_destroy count1
versus0 actual dispatcher calls and preserve balanced primary release. Native
destroy_with_outstanding_allocations_is_deferred retains its independent256MiB
survival/release/RSS oracle. Add positive final-owner Candle child: Weak pool/
context/tensor owners, declared clone-drop order, healthy pre-drop USED baseline,
WeakNone only at actual final owner, no cleanup loss, post-drop marker/exit0;
never query destroyed raw handle. Product finite ordinaryOOM controls require
status2/typed exact failure, healthy USED release and successful4MiB retry on
SAME generation/token/allocator. Do not infer real-reset proof from CPU seams.
Original expectedSIGSEGV history remains unexecuted; seq377 live faults remain
HELD pending concrete reviewed productcommands/artifacts/actor/authority.

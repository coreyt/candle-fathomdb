# candle-fathomdb: differences from upstream Candle

This is FathomDB's fork of [Candle](https://github.com/huggingface/candle),
not the upstream crates. The selected source is published Candle0.11.1 commit
`59f8e903ca80a32ea7f8514b39748fc979e69e82`. Upstream main is comparison only.
Licence/authorship remain MIT OR Apache-2.0 with original attribution.
The owner repository is [coreyt/candle-fathomdb](https://github.com/coreyt/candle-fathomdb).
Owning requirements/design/tests/results live in `fathomdb/slice60.md`;
that directory and this inventory are not packaged.

## Current candidate and delivery

Candle core/nn/transformers and the renamed kernel package are0.13.0
candidates; Rust library names remain `candle_core`, `candle_nn`,
`candle_transformers`, `candle_kernels`. They use exact cudarc-fathomdb0.21.0.
Old registry trio0.12.0 at2ee39305 and cudarc0.20.0 at343b04fa are already
published and immutable. New versions are not published by this preparation.
Historical product Slice31 Q2 kept kernels Git-only; a successor registry
kernel identity requires the parent's concrete owner disposition. Exact Git
qualification, normalized-package staging and public-registry proof are
separate. Root patches do not propagate to downstream workspaces.

```toml
[dependencies]
candle-core = { package = "candle-core-fathomdb", version = "=0.13.0" }
```

## Retained delta inventory

Classes: U upstream-shaped code, L local code, P packaging, D owning docs.
Comparisons below use selected upstream0.11.1; old qualification subjects retain
only their original scope. No upstream writes or proposals are commissioned.

| Delta | Current disposition and reason | Class | Removal condition |
| --- | --- | --- | --- |
| K1 | Retain renamed trio/library identities, three-member workspace and empty defaults; upstream packages are different identities. | P | All other required fork deltas become upstream or unnecessary. |
| K2 | Retain Linux AArch64 gemm without F16 plus typed unsupported CPU F16 matmul; upstream NEON changes do not prove baseline fullfp16 safety. | L | Runtime-safe upstream F16 selection or retirement of this CPU baseline. |
| K3 | Retain cudarc dynamic-loading; upstream0.11.1 still selects dynamic-linking. | L | Upstream driverless lazy loading satisfies the actual installed contract. |
| K4 | Retain whole-archive cudart_static, dl/rt/pthread/stdC++ and CUDA_PATH target library search. Renamed kernel package owns these bytes. | L | Upstream meets complete static-linkage and driverless runtime proof. |
| K5 | Retain public existing-context constructors and default-stream semantics; upstream constructor remains private. | U | Public upstream existing-context API preserves caller allocator/lifetime semantics. |
| K6 | Retain CUDA_PATH/source/header/switch reruns, shared CudaToolkit compiler discovery and exact cudaforge0.1.6 with src watches on PTX AND static builders. | U/L | Upstream implements the complete selected build-input contract. |
| K7 | Retain exact cudarc-fathomdb0.21 edge and unchanged selected implementation features; pool primitives do not depend on the removed no-op marker. Upstream ug is removed. | P | Upstream provides the required pool and tracked-lifetime contracts. |
| K7t | Retain actual private-pool isolation/accounting test; add bounded OOM retry and distinct final tensor/context/pool ownership witnesses. | L | K7 is no longer needed and equivalent owning qualification exists upstream. |
| K8 | Fresh0.13 cohort with exact dependency edges replaces immutable old0.12 registry assumptions; no publication claim. | P | Coherent matching delivery is superseded or fork identity retired. |
| K9 | Kernel and trio use one qualified source cohort instead of old182ceab0 kernel bytes with newer trio. Independent root/archive/SDK/package graphs must prove identity. | P | A fully equivalent upstream dependency graph needs no fork kernel. |
| .29 F32 | Retain checked borrowed BLAS admission before pointer guards and checked handle before unchanged F32 GEMM arguments. | L | Equivalent upstream loss/provenance/cleanup behavior is independently proved. |
| Native candidate | Optional image bytes and the ordinary production cache loader add bounded SASS/PTX treatment; product default stays PTX pending prospective measured criteria. | L | Qualified upstream images/load path replace this treatment, or treatment is rejected. |

## Interface and qualification limits

`Module::image(&self) -> Option<&'static [u8]>` returns immutable embedded
fatbinary bytes only for an enabled candidate build. `None` means use the
existing PTX text. Module IDs/index/PTX/custom-PTX behavior remain unchanged.
The production module cache uses this same loader; native errors propagate
without a new retry or recovery path. Build target rows and refusal cases are
in `candle-kernels/README.md` and the owning design.

The upstream graph-HTOD TLS cache stays inactive: no selected FathomDB caller
invokes its guard API. Future enablement requires its own loss/ownership review.
New upstream dtype/quantized/backend code is not new FathomDB product support.
MoE remains native-only for its selected build architecture, without PTX and
outside selected F32 model paths. SBSA linkage is unqualified; ARM here means
the selected JetPack/Tegra venue. Clean targets are required when changing
NVCC/host compiler/toolkit inputs not identified by the upstream cache.
Real reset survival requires separately authorized positive native children;
CPU seams and healthy drop tests cannot close the original Orin defect.

# candle-fathomdb: differences from upstream Candle

`candle-core-fathomdb`, `candle-nn-fathomdb` and `candle-transformers-fathomdb`
are FathomDB's fork of [Candle](https://github.com/huggingface/candle). They
are not the upstream crates. This file lists everything the fork changes, so
that a consumer can see what differs from upstream and when each change can
go away.

- **Base:** upstream tag `0.10.2`, commit `7c7a8c57`.
- **Source:** [coreyt/candle-fathomdb](https://github.com/coreyt/candle-fathomdb),
  branch `fathomdb/0.8.28-cudarc-fork`. The plan, requirements and status
  records are in that branch's `fathomdb/` directory. Neither that directory
  nor this file is inside a published crate.
- **Licence and authorship:** unchanged from upstream (MIT OR Apache-2.0).

## How to depend on it

The packages are renamed; the library names are still `candle_core`,
`candle_nn` and `candle_transformers`:

```toml
[dependencies]
candle-core = { package = "candle-core-fathomdb", version = "0.10.3" }
```

`candle-kernels` is **not** renamed or published by the fork. The registry
crates depend on upstream `candle-kernels` 0.10.2, which links
`libcudart.so` dynamically. Items K4 and K6 reach a build only when the
workspace patches `candle-kernels` to this fork's git source, as FathomDB
does.

## Items

Class: `U` upstream-shaped code, proposable upstream; `L` local-only code;
`P` packaging. Upstream status checked on 2026-10-12 against tag `0.11.0`
(`31f35b14`) and `main` (`c68b2499`).

| # | Commits | Item | Class | Upstream status | Removal path |
| --- | --- | --- | --- | --- | --- |
| K1 | `61f1590c`, `25368139` | Packages renamed to `candle-{core,nn,transformers}-fathomdb` with library names unchanged; workspace trimmed to those three crates; CPU-safe defaults; 0.10.3 versions (`25368139` is the release that ships K5) | `P` | fork-only by nature | drop when FathomDB uses upstream `candle-*` crates, which needs every other item upstreamed or unneeded |
| K2 | `2e24bc12` (begun in `61f1590c`) | On Linux AArch64 only, `gemm` is built without its f16 backend, which emits `fullfp16` instructions; CPU F16 matmul there returns `UnsupportedDTypeForOp`; test `candle-core/tests/aarch64_linux_cpu.rs` | `L` | not upstream: `candle-core/Cargo.toml:21` on `main` uses default `gemm` features; no PR or issue found (closed #494 is related only) | drop if `gemm` detects `fullfp16` at run time, or FathomDB drops its Linux AArch64 CPU baseline |
| K3 | `5719d90e` | cudarc feature `dynamic-loading` instead of `dynamic-linking`: NVIDIA libraries are opened at run time, so CPU use needs no NVIDIA library | `L` | not upstream: `Cargo.toml:60` (`0.11.0`) and `:58` (`main`) use `dynamic-linking`; issues #3208 and #3900 open; PRs #3209 and #3373 closed unmerged 2026-10-08; PR #3916 open; the `ug` blocker was removed on `main` by #3954 | drop when an upstream release ships `dynamic-loading` |
| K4 | `20ca927b`, `cf02edbc`, `1aefdd00` | `candle-kernels/build.rs` links `cudart_static` (whole archive, plus `dl`, `rt`, `pthread`) instead of `libcudart.so`, and searches `$CUDA_PATH/targets/{x86_64,aarch64}-linux/lib`; `candle-kernels` is taken from the workspace path | `L` | not upstream: `candle-kernels/build.rs:70` (`0.11.0`) and `:78` (`main`) link `dylib=cudart`; issue #3900 open; PRs #3891 and #3916 open | drop when an upstream release's default CUDA build does not link `libcudart.so` |
| K5 | `73e267d0`, `5b74532e` | Public `CudaDevice::from_context` (on the context's default stream) and `Device::new_cuda_from_context`, with tests: a caller-made context, such as one on a private memory pool, backs a Candle device | `U` | no public equivalent: upstream has a private `from_context_and_stream` (`cuda_backend/device.rs:393` on `0.11.0`, #3565); open PR #3777 would make it public (issue #1751). Upstream `BackendDevice::new` now uses `per_thread_stream()` | drop when an upstream release has a public constructor from an existing context |
| K6 | `859b8ea1` | Kernel build script reruns when `CUDA_PATH` changes | `U` | not upstream; no PR or issue | drop with K4 |
| K7 | `0d6fa138` | Depends on `cudarc-fathomdb` (FathomDB's cudarc fork, which adds a private memory pool) at a qualified commit, as `cudarc = { package = "cudarc-fathomdb", git, rev }`; the crate name stays `cudarc` and the features are unchanged | `P` | not applicable: upstream uses registry `cudarc` (0.19.8 on `0.11.0`, 0.19.10 on `main`) | drop when upstream cudarc ships an equivalent private-pool API in a release Candle uses, or FathomDB no longer needs private pools |
| K7t | `d4ffdf58`, `853324fc` | Test `candle-core/tests/cuda_private_pool.rs`: a device built on a private-pool context allocates from that pool and leaves the default pool untouched | `L` | not applicable: tests K7's dependency | drop with K7 |
| K8 | FK5 | 0.10.4 versions, depending on registry `cudarc-fathomdb` 0.19.10 | `P` | not applicable | drop with K7 and K1 |

## Notes

- **MoE kernels.** `libmoe.a` holds SASS for the single architecture named
  by `CUDA_COMPUTE_CAP` at build time, with no PTX, so its kernels run only
  on that architecture. The other kernels are PTX and JIT-compile on newer
  GPUs.
- **SBSA.** K4 maps every AArch64 target to `targets/aarch64-linux`, the
  Jetson layout. NVIDIA's server-ARM toolkits use `targets/sbsa-linux`;
  FathomDB has no SBSA target, and this is not tested.

# candle-kernels-fathomdb

CUDA kernels for FathomDB's Candle fork, derived from upstream Candle0.11.1.
The package keeps the Rust library name `candle_kernels`. Some implementations
come from the [dfdx crate](https://github.com/coreylowman/dfdx).

This fork links the CUDA runtime statically while driver discovery stays lazy.
The default build retains PTX. `Module::image()` returns an optional immutable
fatbinary; a `None` result means callers use the existing `Module::ptx()`.
`CANDLE_CUDA_NATIVE=1` is a build candidate, requiring explicit
`CUDA_COMPUTE_CAP=75` for Linux x86_64 (native75/86 plus PTX75), or `87` for
Linux Tegra AArch64 (native87 plus PTX87). Other candidate targets refuse.
No additional dtype or backend support follows from image availability.

The separate MoE archive is native-only for the selected build architecture;
it has no PTX fallback. It is outside FathomDB's selected F32 model paths.
The build uses exact cudaforge0.1.6 and watches shared headers for both PTX and
static outputs. Use a clean target when changing `NVCC`, `NVCC_CCBIN` or toolkit
headers: the upstream incremental cache does not identify those toolchains.
Qualification and registry publication are separate; see the repository's
`fathomdb/slice60.md` for the candidate scope and actual results.

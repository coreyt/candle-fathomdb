use cudaforge::{KernelBuilder, Result};
use std::env;
use std::path::{Path, PathBuf};
use std::process::Command;

const CUTILE_FEATURE: &str = "CARGO_FEATURE_CUTILE";

fn main() -> Result<()> {
    println!("cargo::rerun-if-changed=build.rs");
    println!("cargo::rerun-if-changed=src");
    println!("cargo::rerun-if-changed=src/compatibility.cuh");
    println!("cargo::rerun-if-changed=src/cuda_utils.cuh");
    println!("cargo::rerun-if-changed=src/binary_op_macros.cuh");
    // CUDA_PATH selects the cudart_static search path below; without this a
    // build first run without it keeps failing to link after it is set.
    println!("cargo::rerun-if-env-changed=CUDA_PATH");

    // Build for PTX
    let out_dir = PathBuf::from(env::var("OUT_DIR").unwrap());
    let ptx_path = out_dir.join("ptx.rs");
    let bindings = KernelBuilder::new()
        .source_dir("src") // Scan src/ for .cu files
        .exclude(&["moe_*.cu", "mmvq_gguf.cu", "mmq_*.cu"]) // Exclude statically compiled kernels from ptx build
        .arg("--expt-relaxed-constexpr")
        .arg("-std=c++17")
        .arg("-O3")
        .build_ptx()?;

    bindings.write(&ptx_path)?;
    build_images(&out_dir)?;

    let mut moe_sources = vec![
        "src/moe/moe_gguf.cu",
        "src/moe/moe_wmma.cu",
        "src/moe/moe_wmma_gguf.cu",
        "src/mmvq_gguf.cu",
        "src/mmq_gguf/mmq_quantize.cu",
        "src/mmq_gguf/mmq_instance_q4_0.cu",
        "src/mmq_gguf/mmq_instance_q4_1.cu",
        "src/mmq_gguf/mmq_instance_q5_0.cu",
        "src/mmq_gguf/mmq_instance_q5_1.cu",
        "src/mmq_gguf/mmq_instance_q8_0.cu",
        "src/mmq_gguf/mmq_instance_q2_k.cu",
        "src/mmq_gguf/mmq_instance_q3_k.cu",
        "src/mmq_gguf/mmq_instance_q4_k.cu",
        "src/mmq_gguf/mmq_instance_q5_k.cu",
        "src/mmq_gguf/mmq_instance_q6_k.cu",
    ];
    if env::var_os(CUTILE_FEATURE).is_some() {
        moe_sources.push("src/moe/moe_align.cu");
    }

    let mut moe_builder = KernelBuilder::default()
        .source_files(moe_sources)
        .arg("--expt-relaxed-constexpr")
        .arg("-std=c++17")
        .arg("-O3");

    // Disable bf16 WMMA kernels on GPUs older than sm_80 (Ampere).
    // bf16 WMMA fragments require compute capability >= 8.0.
    let compute_cap = cudaforge::detect_compute_cap()
        .map(|arch| arch.base())
        .unwrap_or(80);
    if compute_cap < 80 {
        moe_builder = moe_builder.arg("-DNO_BF16_KERNEL");
    }

    let mut is_target_msvc = false;
    if let Ok(target) = std::env::var("TARGET") {
        if target.contains("msvc") {
            is_target_msvc = true;
            moe_builder = moe_builder.arg("-D_USE_MATH_DEFINES");
        }
    }

    if !is_target_msvc {
        moe_builder = moe_builder.arg("-Xcompiler").arg("-fPIC");
    }

    moe_builder.build_lib(out_dir.join("libmoe.a"))?;
    println!("cargo:rustc-link-search={}", out_dir.display());
    println!("cargo:rustc-link-lib=moe");
    // A CUDA-capable Candle consumer must still map its module and execute the
    // CPU path on a host without a CUDA runtime. Dynamic libcudart makes the
    // ELF loader reject the module before its runtime device policy can choose
    // CPU. Link the runtime statically; CUDA driver discovery remains in
    // cudarc's dynamic-loading path and begins only when CUDA is selected.
    if let Ok(cuda_path) = env::var("CUDA_PATH") {
        let target = env::var("TARGET").unwrap_or_default();
        let cuda_target = if target.contains("aarch64") {
            "aarch64-linux"
        } else {
            "x86_64-linux"
        };
        println!("cargo:rustc-link-search=native={cuda_path}/targets/{cuda_target}/lib");
    }
    println!("cargo:rustc-link-lib=static:+whole-archive=cudart_static");
    if !is_target_msvc {
        // Dependencies required by CUDA's static runtime on Linux.
        println!("cargo:rustc-link-lib=dl");
        println!("cargo:rustc-link-lib=rt");
        println!("cargo:rustc-link-lib=pthread");
    }
    if !is_target_msvc {
        println!("cargo:rustc-link-lib=stdc++");
    }
    Ok(())
}

fn build_images(out_dir: &Path) -> Result<()> {
    println!("cargo::rerun-if-env-changed=CANDLE_CUDA_NATIVE");
    let enabled = match env::var("CANDLE_CUDA_NATIVE").as_deref() {
        Err(env::VarError::NotPresent) | Ok("0") => false,
        Ok("1") => true,
        _ => return Err(std::io::Error::other("CANDLE_CUDA_NATIVE must be 0 or 1").into()),
    };
    let families = [
        "affine",
        "binary",
        "cast",
        "conv",
        "fill",
        "indexing",
        "quantized",
        "reduce",
        "sort",
        "ternary",
        "unary",
    ];
    let mut bindings = String::new();
    if enabled {
        let target = env::var("TARGET").unwrap_or_default();
        let (floor, native): (&str, &[&str]) = if target == "x86_64-unknown-linux-gnu" {
            ("75", &["75", "86"])
        } else if target == "aarch64-unknown-linux-gnu" {
            ("87", &["87"])
        } else {
            return Err(std::io::Error::other(
                "native images qualify only Linux x86_64 and Tegra AArch64 targets",
            )
            .into());
        };
        if env::var("CUDA_COMPUTE_CAP").as_deref() != Ok(floor) {
            return Err(std::io::Error::other(format!(
                "native image target requires explicit CUDA_COMPUTE_CAP={floor}"
            ))
            .into());
        }
        let nvcc = env::var_os("NVCC")
            .map(PathBuf::from)
            .or_else(|| env::var_os("CUDA_PATH").map(|root| PathBuf::from(root).join("bin/nvcc")))
            .unwrap_or_else(|| PathBuf::from("nvcc"));
        for chunk in families.chunks(2) {
            std::thread::scope(|scope| {
                let jobs: Vec<_> = chunk
                    .iter()
                    .map(|family| {
                        let nvcc = &nvcc;
                        scope.spawn(move || -> Result<()> {
                            let output = out_dir.join(format!("{family}.fatbin"));
                            let mut command = Command::new(nvcc);
                            command.args([
                                "--fatbin",
                                "--expt-relaxed-constexpr",
                                "-std=c++17",
                                "-O3",
                                "--default-stream",
                                "per-thread",
                            ]);
                            for arch in native {
                                command.arg(format!(
                                    "--generate-code=arch=compute_{arch},code=sm_{arch}"
                                ));
                            }
                            command.arg(format!(
                                "--generate-code=arch=compute_{floor},code=compute_{floor}"
                            ));
                            if let Some(ccbin) = env::var_os("NVCC_CCBIN") {
                                command
                                    .arg("-allow-unsupported-compiler")
                                    .arg("-ccbin")
                                    .arg(ccbin);
                            }
                            let status = command
                                .arg(format!("src/{family}.cu"))
                                .arg("-o")
                                .arg(&output)
                                .status()?;
                            if !status.success() {
                                return Err(std::io::Error::other(format!(
                                    "native image compilation failed for {family}: {status}"
                                ))
                                .into());
                            }
                            Ok(())
                        })
                    })
                    .collect();
                for job in jobs {
                    job.join().map_err(|_| {
                        std::io::Error::other("native image compiler thread panicked")
                    })??;
                }
                Ok::<_, cudaforge::Error>(())
            })?;
        }
    }
    for family in families {
        let name = family.to_uppercase();
        if enabled {
            bindings.push_str(&format!(
                "pub const {name}: Option<&[u8]> = Some(include_bytes!({:?}));\n",
                out_dir.join(format!("{family}.fatbin"))
            ));
        } else {
            bindings.push_str(&format!("pub const {name}: Option<&[u8]> = None;\n"));
        }
    }
    std::fs::write(out_dir.join("images.rs"), bindings)?;
    Ok(())
}

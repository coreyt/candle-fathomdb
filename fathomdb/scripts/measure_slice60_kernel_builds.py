#!/usr/bin/env python3
"""Measure two clean release kernel builds; never runs a GPU.

AGENT_LONG=1 CARGO_HOME=<owned cache> CUDA_PATH=<selected toolkit>
CUDA_COMPUTE_CAP=75 (x86) or87 (Orin), NVCC_CCBIN/CC/CXX selected beforehand:
python3 fathomdb/scripts/measure_slice60_kernel_builds.py --source <normalized kernel package> --output <new owned dir>
Both arms use one immutable source/lock/toolchain/cache and two build workers.
Logs are unaltered; Cargo HTML timings retain dependency versus custom-build
units. A=PTX,B=native. A missed3x ceiling reports non-adoption, not new tuning.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


def identity(source):
    paths = [source / "Cargo.toml", source / "Cargo.lock", source / "build.rs", *sorted((source / "src").rglob("*"))]
    return {str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file()}


def main():
    if not __debug__ or os.environ.get("AGENT_LONG") != "1":
        raise RuntimeError("explicit AGENT_LONG=1 and assertions enabled required")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    source = args.source.resolve()
    for name in ("CARGO_HOME", "CUDA_PATH", "CUDA_COMPUTE_CAP", "NVCC_CCBIN", "CC", "CXX"):
        if not os.environ.get(name):
            raise RuntimeError(f"explicit {name} required")
    original = identity(source)
    args.output.mkdir(parents=True, exist_ok=False)
    results = {}
    for arm, native in (("a", "0"), ("b", "1")):
        target = args.output / (arm + "-target")
        env = dict(os.environ, CARGO_TARGET_DIR=str(target.resolve()), CANDLE_CUDA_NATIVE=native,
                   CARGO_BUILD_JOBS="2", CUDAFORGE_THREADS="2", CUDA_VISIBLE_DEVICES="-1")
        command = ["cargo", "+1.95.0", "build", "--offline", "--locked", "--release", "--timings"]
        start = time.monotonic()
        with (args.output / (arm + ".log")).open("w") as log:
            result = subprocess.run(command, cwd=source, env=env, stdout=log, stderr=subprocess.STDOUT)
        results[arm] = {"exit": result.returncode, "wall_seconds": time.monotonic() - start,
                        "command": command, "target": str(target), "cargo_timings": str(target / "cargo-timings/cargo-timing.html")}
        if identity(source) != original:
            raise RuntimeError("kernel source/lock changed during measured build")
        (args.output / "results.json").write_text(json.dumps({"source": str(source), "identity": original, "arms": results}, indent=2) + "\n")
        if result.returncode:
            return result.returncode
    ratio = results["b"]["wall_seconds"] / results["a"]["wall_seconds"]
    complete = {"source": str(source), "identity": original, "arms": results, "ratio": ratio,
                "passes_build_criterion": ratio <= 3, "criterion": "clean same-source native kernel build <=3x PTX"}
    (args.output / "results.json").write_text(json.dumps(complete, indent=2) + "\n")
    print(json.dumps(complete, indent=2))
    return 0 if ratio <= 3 else 1


if __name__ == "__main__":
    raise SystemExit(main())

"""Build the actual kernel crate twice through a real compiler observer."""
import json
import os
from pathlib import Path
import subprocess
import tarfile
import tempfile
import tomllib

_RESULT = None


def result():
    global _RESULT
    if _RESULT is not None:
        return _RESULT
    existing = os.environ.get("FATHOMDB_KERNEL_REBUILD_RESULT")
    if existing:
        root = Path(existing)
        logs = [[json.loads(line) for line in (root / (phase + "-nvcc.jsonl")).read_text().splitlines()] for phase in ("initial", "header-change")]
        _RESULT = (root, logs[0], logs[1])
        return _RESULT
    archive = Path(os.environ["FATHOMDB_KERNEL_SOURCE_ARCHIVE"])
    scratch = Path(os.environ["FATHOMDB_KERNEL_REBUILD_SCRATCH"])
    scratch.mkdir(parents=True, exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="kernel-rebuild-", dir=scratch))
    source = root / "source"
    source.mkdir()
    with tarfile.open(archive) as bundle:
        bundle.extractall(source, filter="data")
    kernel = source / "candle-kernels"
    (kernel / "Cargo.lock").write_bytes((source / "Cargo.lock").read_bytes())
    binary = root / "bin"
    binary.mkdir()
    compiler = binary / "nvcc"
    compiler.write_text("#!/usr/bin/python3\nimport json,os,sys\n"
        "with open(os.environ['FATHOMDB_NVCC_LOG'],'a') as output: output.write(json.dumps(sys.argv[1:])+'\\n')\n"
        "os.execv('/usr/local/cuda-12.6/bin/nvcc',['/usr/local/cuda-12.6/bin/nvcc',*sys.argv[1:]])\n")
    compiler.chmod(0o755)
    env = dict(os.environ, PATH=str(binary) + os.pathsep + os.environ["PATH"],
        CUDA_PATH="/usr/local/cuda-12.6", CUDA_HOME="/usr/local/cuda-12.6",
        CUDA_COMPUTE_CAP="75", CANDLE_CUDA_NATIVE="1", CUDA_VISIBLE_DEVICES="-1",
        CUDAFORGE_THREADS="2", CARGO_BUILD_JOBS="2", CARGO_TARGET_DIR=str(root / "target"),
        TMPDIR=str(scratch))
    env.pop("NVCC", None)
    version = next(p["version"] for p in tomllib.loads((source / "Cargo.lock").read_text())["package"] if p["name"] == "cudaforge")
    with (root / "lock-prepare.log").open("wb") as output:
        subprocess.run(["cargo", "+1.95.0", "update", "--offline", "--manifest-path", str(kernel / "Cargo.toml"), "-p", "cudaforge", "--precise", version], env=env, stdout=output, stderr=subprocess.STDOUT, check=True)
    command = ["cargo", "+1.95.0", "build", "--manifest-path", str(kernel / "Cargo.toml"), "--locked"]
    logs = []
    for phase in ("initial", "header-change"):
        if phase == "header-change":
            for header in (kernel / "src/cuda_utils.cuh", kernel / "src/moe/moe_utils.cuh"):
                with header.open("a") as output:
                    output.write("\n// qualification: changed declared shared header input\n")
        log = root / (phase + "-nvcc.jsonl")
        env["FATHOMDB_NVCC_LOG"] = str(log)
        with (root / (phase + "-build.log")).open("wb") as output:
            subprocess.run(command, cwd=source, env=env, stdout=output, stderr=subprocess.STDOUT, check=True)
        logs.append([json.loads(line) for line in log.read_text().splitlines()])
    _RESULT = (root, logs[0], logs[1])
    print(f"real compiler rebuild fixture: {root}", flush=True)
    return _RESULT

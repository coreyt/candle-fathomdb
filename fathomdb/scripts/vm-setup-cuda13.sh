#!/usr/bin/env bash
# fathomdb/scripts/vm-setup-cuda13.sh — prepares a FathomDB GCP lab VM for
# cell K-G2 (requirements.md § 2), after `scripts/gcp-cuda-lab.sh driver
# --driver 580` has installed the driver. Runs on the VM only, never on
# windchill3: it installs CUDA 13.0 toolkit packages from NVIDIA's Ubuntu
# 24.04 repository (toolkit pieces only, no driver meta-package) into
# /usr/local/cuda-13.0, and a stable Rust toolchain.
set -euo pipefail
export DEBIAN_FRONTEND=noninteractive

if [ ! -x /usr/local/cuda-13.0/bin/nvcc ]; then
  if [ ! -e /usr/share/keyrings/cuda-archive-keyring.gpg ]; then
    keyring_dir="$(mktemp -d)"
    curl -fsSL -o "$keyring_dir/cuda-keyring.deb" \
      https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i "$keyring_dir/cuda-keyring.deb"
  fi
  sudo apt-get update -q
  sudo apt-get install -yq --no-install-recommends build-essential pkg-config git curl \
    cuda-nvcc-13-0 cuda-cudart-dev-13-0 cuda-nvrtc-dev-13-0 cuda-cccl-13-0 \
    libcublas-dev-13-0 libcurand-dev-13-0
fi
if [ ! -x "$HOME/.cargo/bin/rustup" ]; then
  curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --profile minimal --default-toolchain stable
fi
"$HOME/.cargo/bin/rustc" --version
/usr/local/cuda-13.0/bin/nvcc --version | tail -1
nvidia-smi --query-gpu=name,driver_version,compute_cap --format=csv,noheader
dpkg -l | awk '/^ii/ && $2 ~ /nvidia|cuda/ {print $2, $3}'

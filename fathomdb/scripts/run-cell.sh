#!/usr/bin/env bash
# fathomdb/scripts/run-cell.sh — runs one Candle fork qualification cell
# (requirements.md § 5) on the current host and writes its receipt files.
#
#   run-cell.sh --cell K-G1|K-G1-75|K-G2|K-G3 --repo <git dir or bundle>
#               --k <sha> --control <sha> --out <dir>
#               --cuda-root <dir> --cuda-version 12060|13000 --cc <75|86|87|89>
#               [--t1-runs N] [--only-t1-t2]
#
# Both commits are extracted with `git archive` into <out>/src-{k,control};
# each has its own target directory. K is built first and its Cargo.lock is
# copied into the control tree (§ 5.1). Test failures do not stop the cell:
# every run's exit status goes into <out>/summary.tsv and its output into
# <out>/<run>.log, and the receipt classifies them afterwards.
set -uo pipefail

CELL="" REPO="" K="" CONTROL="" OUT="" CUDA_ROOT="" CUDA_VERSION="" CC=""
T1_RUNS=3 ONLY_T1_T2=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --cell) CELL="$2"; shift 2 ;;
    --repo) REPO="$2"; shift 2 ;;
    --k) K="$2"; shift 2 ;;
    --control) CONTROL="$2"; shift 2 ;;
    --out) OUT="$2"; shift 2 ;;
    --cuda-root) CUDA_ROOT="$2"; shift 2 ;;
    --cuda-version) CUDA_VERSION="$2"; shift 2 ;;
    --cc) CC="$2"; shift 2 ;;
    --t1-runs) T1_RUNS="$2"; shift 2 ;;
    --only-t1-t2) ONLY_T1_T2=1; shift ;;
    *) printf 'run-cell: unknown option %s\n' "$1" >&2; exit 2 ;;
  esac
done
die() { printf 'run-cell: %s\n' "$*" >&2; exit 2; }
for v in CELL REPO K CONTROL OUT CUDA_ROOT CUDA_VERSION CC; do
  [ -n "${!v}" ] || die "--$(echo "$v" | tr 'A-Z_' 'a-z-') is required"
done
[[ "$K" =~ ^[0-9a-f]{40}$ && "$CONTROL" =~ ^[0-9a-f]{40}$ ]] || die "--k and --control must be full 40-character shas"
[ -x "$CUDA_ROOT/bin/nvcc" ] || die "no nvcc under $CUDA_ROOT"
[ ! -e "$OUT" ] || die "$OUT exists; use a new directory per run"
mkdir -p "$OUT"
OUT="$(cd "$OUT" && pwd)"

export CUDA_DEVICE_ORDER=PCI_BUS_ID CUDA_VISIBLE_DEVICES=0
export PATH="$CUDA_ROOT/bin:$PATH" CUDA_PATH="$CUDA_ROOT"
export CUDARC_CUDA_VERSION="$CUDA_VERSION" CUDA_COMPUTE_CAP="$CC"
if [ -d "$CUDA_ROOT/lib64" ]; then export LD_LIBRARY_PATH="$CUDA_ROOT/lib64${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"; fi

SUMMARY="$OUT/summary.tsv"
printf 'run\tsource\texit\n' > "$SUMMARY"
note() { printf '%s\n' "$*" | tee -a "$OUT/cell.log"; }
newest_test_binary() { # newest_test_binary <deps dir> <stem>: the newest executable <stem>-<hash>
  local f best=""
  for f in "$1/$2"-*; do
    [ -f "$f" ] && [ -x "$f" ] || continue
    if [ -z "$best" ] || [ "$f" -nt "$best" ]; then best="$f"; fi
  done
  printf '%s' "$best"
}

host_facts() {
  {
    echo "== $1 $(date -u +%FT%TZ)"
    echo "host: $(hostname) $(uname -srm)"
    nvidia-smi --query-gpu=index,name,pci.bus_id,driver_version,compute_cap --format=csv,noheader 2>&1 \
      || echo "nvidia-smi unavailable"
    [ -r /etc/nv_tegra_release ] && head -1 /etc/nv_tegra_release
    echo "readlink -f /usr/local/cuda: $(readlink -f /usr/local/cuda 2>&1)"
    echo "nvcc: $(nvcc --version | tail -1)"
    echo "cargo: $(cargo --version)"
    env | grep -E '^(CUDA_|CUDARC_|LD_LIBRARY_PATH=)' | sort
  } >> "$OUT/host.txt"
}

run() { # run <name> <source dir> <command...>
  local name="$1" src="$2"; shift 2
  note "-- $name ($src): $*"
  (cd "$OUT/src-$src" && CARGO_TARGET_DIR="$OUT/target-$src" "$@") > "$OUT/$name.log" 2>&1
  local rc=$?
  printf '%s\t%s\t%s\n' "$name" "$src" "$rc" >> "$SUMMARY"
  note "   exit $rc"
  return 0
}

host_facts start
for side in k control; do
  sha="$K"; [ "$side" = control ] && sha="$CONTROL"
  mkdir -p "$OUT/src-$side"
  git --git-dir="$REPO" archive "$sha" | tar -x -C "$OUT/src-$side" || die "git archive $sha failed"
  echo "$sha" > "$OUT/src-$side/.cell-sha"
done

CORE=(-p candle-core-fathomdb --features cuda)

# K first: its fresh lock is the cell's lock.
run build-k k cargo test "${CORE[@]}" --no-run
cp "$OUT/src-k/Cargo.lock" "$OUT/src-control/Cargo.lock"
run build-control control cargo test "${CORE[@]}" --no-run
sha256sum "$OUT/src-k/Cargo.lock" "$OUT/src-control/Cargo.lock" > "$OUT/locks.sha256"
diff "$OUT/src-k/Cargo.lock" "$OUT/src-control/Cargo.lock" > "$OUT/locks.diff"
for side in k control; do
  (cd "$OUT/src-$side" && CARGO_TARGET_DIR="$OUT/target-$side" \
    cargo tree "${CORE[@]}" -e normal) > "$OUT/tree-$side.txt" 2>&1
done

for i in $(seq 1 "$T1_RUNS"); do
  run "T1-k-$i" k cargo test "${CORE[@]}" --test cuda_private_pool
done
# Which CUDA library files the T1 test opened (cudarc item 9).
bin="$(newest_test_binary "$OUT/target-k/debug/deps" cuda_private_pool)"
if [ -n "$bin" ]; then
  LD_DEBUG=files "$bin" > "$OUT/T1-ld-debug.log" 2>&1
  grep -oE 'file=[^ ;]*(libcuda|libcublas|libcublasLt|libcurand|libnvrtc)[^ ;]*' "$OUT/T1-ld-debug.log" \
    | sort -u > "$OUT/T1-loaded-libraries.txt"
fi
run T2-k k cargo test "${CORE[@]}" --test cuda_from_context
run T2-control control cargo test "${CORE[@]}" --test cuda_from_context

if [ "$ONLY_T1_T2" = 0 ]; then
  run T3-k k cargo test "${CORE[@]}" --no-fail-fast
  run T3-control control cargo test "${CORE[@]}" --no-fail-fast
  run T4-k k cargo test -p candle-nn-fathomdb --features cuda --no-fail-fast
  run T4-control control cargo test -p candle-nn-fathomdb --features cuda --no-fail-fast
  if [ "$(uname -m)" = aarch64 ]; then
    run T5-k k cargo test -p candle-core-fathomdb --test aarch64_linux_cpu
    run T5-control control cargo test -p candle-core-fathomdb --test aarch64_linux_cpu
  fi
  for crate in candle-core-fathomdb candle-nn-fathomdb candle-transformers-fathomdb; do
    (cd "$OUT/src-k" && CARGO_TARGET_DIR="$OUT/target-k" \
      cargo tree -p "$crate" --features cuda -e normal --prefix none) > "$OUT/T6-$crate.txt" 2>&1
    {
      echo "== $crate"
      echo "cudarc-fathomdb lines:"; grep -E '^cudarc-fathomdb v' "$OUT/T6-$crate.txt" | sort -u
      echo "cudarc lines (expected none):"; grep -E '^cudarc v' "$OUT/T6-$crate.txt" | sort -u
    } >> "$OUT/T6-ck-ac-01.txt"
  done
  # CK-AC-04: no forbidden NEEDED entry; static CUDART linked in.
  forbidden='^lib(cuda|cudart|cublas(lt)?|curand|cufft|cusolver|cusparse|nvrtc|nvjitlink|nvidia-ml|nvml)([._-]|$)'
  for side in k control; do
    for stem in cuda_private_pool cuda_from_context candle_core; do
      b="$(newest_test_binary "$OUT/target-$side/debug/deps" "$stem")"
      [ -n "$b" ] || { echo "$side $stem absent" >> "$OUT/T7-ck-ac-04.txt"; continue; }
      needed="$(readelf -d "$b" | sed -n 's/.*Shared library: \[\(.*\)\]/\1/p')"
      bad="$(printf '%s\n' "$needed" | grep -ciE "$forbidden")"
      cudart="$(nm -C --defined-only "$b" | grep -c ' cudaGetDeviceCount')"
      echo "$side $stem forbidden_needed=$bad cudaGetDeviceCount_defined=$cudart needed=[$(printf '%s' "$needed" | tr '\n' ' ')]" >> "$OUT/T7-ck-ac-04.txt"
    done
  done
  run T8-k k cargo check -p candle-transformers-fathomdb --features cuda
fi
host_facts end
note "cell $CELL done; summary in $SUMMARY"

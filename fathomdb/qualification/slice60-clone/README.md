# Prechecked final-owner clone qualifier

This out-of-package target consumes final Candle952e/Cudarc3509 public code.
`original.rs` is the exact952e `candle-core/tests/cuda_reset_lifecycle.rs` file,
SHA256 `cfb032c7d45b64ea0e2208f5ce3718c385696761223bfe2993ebc20426d37fc6`.
The build verifies that trusted digest and removes only its first two module
header lines so the remaining original function bytes can be included. The
additional test checks driver initialization, exactly one visible device and
ordinal0's actual selected UUID before the unchanged original body constructs
any context, pool, model or tensor. It retains no context in the prelude.

Build with explicit CUDA12.6/cap75 or87/PTX0, `cargo +1.95.0 test --locked
--manifest-path fathomdb/qualification/slice60-clone/Cargo.toml --no-run`.
Only the guarded selector is qualified:
`<exact-binary> --ignored --exact prechecked_clone_checks_uuid_before_original_body
--nocapture --test-threads=1`. Require exactly1passed/0failed/0ignored and its
prechecked identity, READY and final-owner markers. Never run the generated
original test selector directly for this claim. Bind source, lock, graph and
binary hashes. Healthy mode is ordinary qualification; reset remains held for
the exact owner action, selected resource/visibility protocol and fresh-process
model recovery. No source/package pin or shipping artifact is changed.

`test_identity.py --binary <exact-binary>` is a synthetic driver-ABI negative
control, not a product RED or hardware-reset proof. It exports the actual
CUDA12.6 `cuDeviceGetUuid` entry used by the final fork and requires only init,
count, device and UUID trace entries before a mismatched UUID refuses. Initial
fixture setup exposed only `.so.1`/the v2 symbol and did not reach the intended
UUID guard; those failures are not RED. The corrected `.so`/v1 ABI control passes.

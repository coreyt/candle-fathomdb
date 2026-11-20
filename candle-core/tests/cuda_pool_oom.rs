//! Ordinary private-pool exhaustion remains retryable on the same generation.
#![cfg(feature = "cuda")]
use candle_core::cuda::cudarc::driver::{
    sys::CUresult, CudaContext, CudaMemPool, MemPoolProps, PrimaryContextLifetime,
};
use candle_core::{DType, Device, Tensor};
use std::sync::Arc;

#[test]
#[ignore = "requires an explicit exclusive CUDA lease and bounded private-pool venue"]
fn private_pool_oom_releases_healthy_tensor_and_retries_same_generation() -> candle_core::Result<()>
{
    assert_eq!(std::env::var("FATHOMDB_REQUIRE_LIVE").as_deref(), Ok("1"));
    let w = candle_core::Error::wrap;
    let lifetime = PrimaryContextLifetime::new(0).map_err(w)?;
    let id = lifetime.recorded_id();
    let pool = Arc::new(
        CudaMemPool::create_tracked(
            lifetime.clone(),
            &MemPoolProps {
                max_size: 96 << 20,
                release_threshold: 0,
            },
        )
        .map_err(w)?,
    );
    let context =
        CudaContext::new_with_mem_pool_tracked(lifetime.clone(), pool.clone()).map_err(w)?;
    let stream = context.default_stream();
    let device = Device::new_cuda_from_context(context)?;
    let tensor = Tensor::ones(2 << 20, DType::F32, &device)?;
    device.synchronize()?;
    assert!(pool.used_current().map_err(w)? >= 8 << 20);
    let error = stream
        .alloc_zeros::<u8>(128 << 20)
        .expect_err("request exceeds finite96MiB pool");
    assert_eq!(error.0, CUresult::CUDA_ERROR_OUT_OF_MEMORY);
    assert!(
        lifetime.loss().is_none(),
        "ordinary OOM must not poison the generation"
    );
    drop(tensor);
    device.synchronize()?;
    assert_eq!(pool.used_current().map_err(w)?, 0);
    let retry = stream.alloc_zeros::<u8>(4 << 20).map_err(w)?;
    assert_eq!(stream.clone_dtoh(&retry).map_err(w)?.len(), 4 << 20);
    assert_eq!(lifetime.recorded_id(), id);
    assert!(lifetime.loss().is_none());
    drop(retry);
    device.synchronize()?;
    assert_eq!(pool.used_current().map_err(w)?, 0);
    drop(device);
    drop(stream);
    drop(pool);
    assert!(lifetime.loss().is_none());
    drop(lifetime);
    println!(
        "private-pool-oom: actual-status2 healthy-release same-generation4MiB-retry post-drop"
    );
    Ok(())
}

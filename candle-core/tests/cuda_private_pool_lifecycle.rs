//! Final-owner preservation for an actual tracked private-pool Candle device.
#![cfg(feature = "cuda")]

use candle_core::cuda::cudarc::driver::{
    CudaContext, CudaMemPool, MemPoolProps, PrimaryContextLifetime,
};
use candle_core::{DType, Device, Tensor};
use std::sync::Arc;

#[test]
#[ignore = "requires an explicit exclusive CUDA lease and qualification artifacts"]
fn healthy_last_tensor_clone_releases_context_and_final_private_pool_owner(
) -> candle_core::Result<()> {
    assert_eq!(std::env::var("FATHOMDB_REQUIRE_LIVE").as_deref(), Ok("1"));
    let w = candle_core::Error::wrap;
    let lifetime = PrimaryContextLifetime::new(0).map_err(w)?;
    let weak_lifetime = Arc::downgrade(&lifetime);
    let observer = CudaContext::new_tracked(lifetime.clone()).map_err(w)?;
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
    let weak_pool = Arc::downgrade(&pool);
    let context =
        CudaContext::new_with_mem_pool_tracked(lifetime.clone(), pool.clone()).map_err(w)?;
    let weak_context = Arc::downgrade(&context);
    let device = Device::new_cuda_from_context(context.clone())?;
    let tensor = Arc::new(Tensor::ones(2 << 20, DType::F32, &device)?);
    let clone = Arc::new((*tensor).clone());
    let weak_tensor = Arc::downgrade(&tensor);
    let weak_clone = Arc::downgrade(&clone);
    device.synchronize()?;
    assert!(pool.used_current().map_err(w)? >= 8 << 20);
    assert_eq!(clone.narrow(0, 0, 4)?.to_vec1::<f32>()?, [1_f32; 4]);
    drop(device);
    drop(context);
    assert!(weak_context.upgrade().is_some());
    drop(tensor);
    assert!(weak_tensor.upgrade().is_none());
    assert!(weak_context.upgrade().is_some());
    assert!(weak_clone.upgrade().is_some());
    drop(clone);
    assert!(weak_clone.upgrade().is_none());
    assert!(weak_context.upgrade().is_none());
    observer.synchronize().map_err(w)?;
    assert_eq!(pool.used_current().map_err(w)?, 0);
    pool.trim_to(0).map_err(w)?;
    observer.synchronize().map_err(w)?;
    assert_eq!(pool.reserved_current().map_err(w)?, 0);
    assert_eq!(Arc::strong_count(&pool), 1);
    drop(pool);
    assert!(weak_pool.upgrade().is_none());
    assert!(lifetime.loss().is_none(), "healthy native cleanup failed");
    drop(observer);
    drop(lifetime);
    assert!(weak_lifetime.upgrade().is_none());
    println!("private-pool-lifecycle: final-tensor-context-pool-anchor-dropped");
    Ok(())
}

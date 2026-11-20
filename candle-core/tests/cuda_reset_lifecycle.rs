//! Positive successor controls; real resets require separate venue authorization.
#![cfg(feature = "cuda")]
use candle_core::cuda::cudarc::driver::{
    result, sys, CudaContext, CudaMemPool, MemPoolProps, PrimaryContextLifetime,
};
use candle_core::{DType, Device, Tensor};
use std::sync::Arc;

#[test]
#[ignore = "explicit leased healthy control; real reset mode separately held"]
fn completed_tensor_last_clone_drops_with_a_distinct_final_owner_witness() -> candle_core::Result<()>
{
    assert_eq!(std::env::var("FATHOMDB_REQUIRE_LIVE").as_deref(), Ok("1"));
    let mode = std::env::var("FATHOMDB_COORDINATED_RESET")
        .expect("select healthy or separately authorized reset");
    assert!(matches!(mode.as_str(), "healthy" | "reset"));
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
    let original = Tensor::ones(2 << 20, DType::F32, &device)?;
    let clone = Arc::new(original.clone());
    let weak_clone = Arc::downgrade(&clone);
    assert_eq!(original.narrow(0, 0, 4)?.to_vec1::<f32>()?, [1.; 4]);
    device.synchronize()?;
    assert!(pool.used_current().map_err(w)? >= 8 << 20);
    println!("tensor-last-clone: ready completed-construction synchronized live-bytes>=8388608 mode={mode}");
    if mode == "reset" {
        let ordinal = result::device::get(0).map_err(w)?;
        // This sole test thread owns every participant. All construction and
        // submitted work completed above; no other CUDA module runs in child.
        unsafe { sys::cuDevicePrimaryCtxReset_v2(ordinal) }
            .result()
            .map_err(w)?;
        println!("tensor-last-clone: process-primary-reset-returned");
    }
    // No operation or forward after reset: final-owner cleanup must discover it.
    drop(device);
    drop(context);
    drop(original);
    assert!(weak_context.upgrade().is_some());
    assert!(weak_clone.upgrade().is_some());
    drop(clone);
    assert!(weak_clone.upgrade().is_none());
    assert!(weak_context.upgrade().is_none());
    if mode == "reset" {
        assert!(
            lifetime.loss().is_some(),
            "cleanup must discover reset without a forward"
        );
    } else {
        observer.synchronize().map_err(w)?;
        assert_eq!(pool.used_current().map_err(w)?, 0);
        pool.trim_to(0).map_err(w)?;
        assert_eq!(pool.reserved_current().map_err(w)?, 0);
        assert!(lifetime.loss().is_none());
    }
    drop(pool);
    assert!(weak_pool.upgrade().is_none());
    drop(observer);
    drop(lifetime);
    assert!(weak_lifetime.upgrade().is_none());
    println!("tensor-last-clone: final-clone-context-pool-anchor-dropped mode={mode}");
    Ok(())
}

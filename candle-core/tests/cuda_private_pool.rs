//! A device built on a context with a private memory pool allocates its
//! tensors from that pool and returns them to it, leaving the device's default
//! and current pools untouched (FathomDB 0.8.28 private memory pool).
#![cfg(feature = "cuda")]

use candle_core::cuda::cudarc::driver::{
    result, sys, AllocMode, CudaContext, CudaMemPool, MemPoolProps,
};
use candle_core::{DType, Device, Tensor};
use std::sync::Arc;

const MIB: u64 = 1024 * 1024;

fn default_pool_used_current(pool: sys::CUmemoryPool) -> candle_core::Result<u64> {
    let mut used: u64 = 0;
    // SAFETY: `pool` is the device's default pool, which lives as long as the
    // primary context, and USED_MEM_CURRENT writes one u64 to `used`.
    unsafe {
        result::mem_pool::get_attribute(
            pool,
            sys::CUmemPool_attribute::CU_MEMPOOL_ATTR_USED_MEM_CURRENT,
            (&mut used as *mut u64).cast(),
        )
    }
    .map_err(candle_core::Error::wrap)?;
    Ok(used)
}

#[test]
fn device_on_a_private_pool_context_allocates_from_that_pool() -> candle_core::Result<()> {
    let w = candle_core::Error::wrap;
    let pool = Arc::new(
        CudaMemPool::create(
            0,
            &MemPoolProps {
                max_size: 0,
                release_threshold: 0,
            },
        )
        .map_err(w)?,
    );

    result::init().map_err(w)?;
    let cu_device = result::device::get(0).map_err(w)?;
    // SAFETY: the driver is initialized and `cu_device` is a valid device handle.
    let default_before = unsafe { result::device::get_default_mem_pool(cu_device) }.map_err(w)?;
    // SAFETY: as above.
    let current_before = unsafe { result::device::get_mem_pool(cu_device) }.map_err(w)?;

    let ctx = CudaContext::new_with_mem_pool(0, pool.clone()).map_err(w)?;
    let device = Device::new_cuda_from_context(ctx.clone())?;
    assert_eq!(ctx.alloc_mode(), AllocMode::Private);
    assert!(Arc::ptr_eq(ctx.mem_pool().unwrap(), &pool));
    assert!(Arc::ptr_eq(
        device.as_cuda_device()?.cuda_stream().context(),
        &ctx
    ));

    assert_eq!(pool.used_current().map_err(w)?, 0);
    let default_used_before = default_pool_used_current(default_before)?;

    let elements = (8 * MIB / 4) as usize;
    let t = Tensor::zeros(elements, DType::F32, &device)?;
    let u = (&t + 1.0)?;
    device.synchronize()?;
    let used = pool.used_current().map_err(w)?;
    assert!(used >= 16 * MIB, "private pool used {used} bytes");
    assert!(pool.reserved_current().map_err(w)? >= used);

    drop(u);
    drop(t);
    device.synchronize()?;
    assert_eq!(pool.used_current().map_err(w)?, 0);

    // SAFETY: as above.
    let default_after = unsafe { result::device::get_default_mem_pool(cu_device) }.map_err(w)?;
    // SAFETY: as above.
    let current_after = unsafe { result::device::get_mem_pool(cu_device) }.map_err(w)?;
    assert_eq!(default_after, default_before);
    assert_eq!(current_after, current_before);
    assert_eq!(
        default_pool_used_current(default_before)?,
        default_used_before
    );
    Ok(())
}

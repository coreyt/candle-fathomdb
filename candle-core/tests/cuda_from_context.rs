//! A device built on an existing cudarc context uses that context, so the
//! caller chooses its allocator (FathomDB 0.8.28 private memory pool).
#![cfg(feature = "cuda")]

use candle_core::cuda::cudarc::driver::CudaContext;
use candle_core::{DType, Device, Tensor};
use std::sync::Arc;

#[test]
fn device_from_context_runs_on_that_context() -> candle_core::Result<()> {
    let ctx = CudaContext::new(0).map_err(candle_core::Error::wrap)?;
    let device = Device::new_cuda_from_context(ctx.clone())?;
    let cuda = device.as_cuda_device()?;
    assert!(Arc::ptr_eq(cuda.cuda_stream().context(), &ctx));
    let ones = Tensor::ones(4, DType::F32, &device)?;
    assert_eq!(ones.to_vec1::<f32>()?, vec![1.0; 4]);
    Ok(())
}

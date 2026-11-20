//! Known-output controls for the actual Candle module loader.
#![cfg(feature = "cuda")]

use candle_core::cuda::cudarc::driver::{CudaContext, LaunchConfig, PushKernelArg};
use candle_core::cuda::kernels;
use candle_core::{DType, Device, Tensor};

#[test]
fn fill_f32_module_loads_and_executes_with_exact_output() -> candle_core::Result<()> {
    assert_eq!(std::env::var("FATHOMDB_REQUIRE_LIVE").as_deref(), Ok("1"));
    let context = CudaContext::new(0).map_err(candle_core::Error::wrap)?;
    println!(
        "image-control device={} family=Fill symbol=fill_f32 phase=context-ready",
        context.name().map_err(candle_core::Error::wrap)?
    );
    let device = Device::new_cuda_from_context(context)?;
    let cuda = device.as_cuda_device()?;
    println!("image-control family=Fill symbol=fill_f32 phase=module-load");
    let function = cuda.get_or_load_func("fill_f32", &kernels::FILL)?;
    let stream = cuda.cuda_stream();
    let mut output = stream
        .alloc_zeros::<f32>(4)
        .map_err(candle_core::Error::wrap)?;
    let value = 1_f32;
    let length = 4_usize;
    // SAFETY: fill_f32 writes four F32 elements to the live owning output;
    // scalar argument types and launch bounds match the selected CUDA source.
    unsafe {
        function
            .builder()
            .arg(&mut output)
            .arg(&value)
            .arg(&length)
            .launch(LaunchConfig::for_num_elems(4))
    }
    .map_err(candle_core::Error::wrap)?;
    assert_eq!(
        stream
            .clone_dtoh(&output)
            .map_err(candle_core::Error::wrap)?,
        [1_f32; 4]
    );
    println!("image-control family=Fill symbol=fill_f32 phase=output-validated");
    Ok(())
}

#[test]
fn f32_module_families_execute_authored_operations() -> candle_core::Result<()> {
    assert_eq!(std::env::var("FATHOMDB_REQUIRE_LIVE").as_deref(), Ok("1"));
    let device = Device::new_cuda(0)?;
    let cuda = device.as_cuda_device()?;
    let input = Tensor::new(&[1_f32, 2., 3., 4.], &device)?;
    for (name, module) in [
        ("affine_f32", &kernels::AFFINE),
        ("badd_f32", &kernels::BINARY),
        ("cast_u32_f32", &kernels::CAST),
        ("is_u32_f32", &kernels::INDEXING),
        ("fast_sum_f32", &kernels::REDUCE),
        ("usqr_f32", &kernels::UNARY),
    ] {
        cuda.get_or_load_func(name, module)?;
    }
    assert_eq!(input.affine(2., 1.)?.to_vec1::<f32>()?, [3., 5., 7., 9.]);
    let reverse = Tensor::new(&[4_f32, 3., 2., 1.], &device)?;
    assert_eq!((&input + &reverse)?.to_vec1::<f32>()?, [5_f32; 4]);
    let ids = Tensor::new(&[1_u32, 2, 3, 4], &device)?;
    assert_eq!(
        ids.to_dtype(DType::F32)?.to_vec1::<f32>()?,
        [1., 2., 3., 4.]
    );
    let indices = Tensor::new(&[3_u32, 1], &device)?;
    assert_eq!(input.index_select(&indices, 0)?.to_vec1::<f32>()?, [4., 2.]);
    assert_eq!(input.sum_all()?.to_scalar::<f32>()?, 10.);
    assert_eq!(input.sqr()?.to_vec1::<f32>()?, [1., 4., 9., 16.]);
    println!("image-control six-families-output-validated");
    Ok(())
}

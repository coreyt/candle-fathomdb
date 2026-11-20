use super::{kernels, load_kernel_module};
use cudarc::driver::{CudaContext, LaunchConfig, PushKernelArg};

#[test]
fn owning_loader_executes_seven_authored_f32_kernel_results() -> crate::Result<()> {
    assert_eq!(std::env::var("FATHOMDB_REQUIRE_LIVE").as_deref(), Ok("1"));
    let w = crate::Error::wrap;
    let context = CudaContext::new(0).map_err(w)?;
    let stream = context.default_stream();
    println!(
        "owning-image-control device={} phase=context-ready",
        context.name().map_err(w)?
    );
    let load = |name: &str, module: &kernels::Module| {
        println!("owning-image-control symbol={name} phase=module-load");
        load_kernel_module(&context, module)?
            .load_function(name)
            .map_err(w)
    };
    let n = 4_usize;
    let dims = 1_usize;
    let info = stream.clone_htod(&[4_usize, 1, 1]).map_err(w)?;
    let input = stream.clone_htod(&[1_f32, 2., 3., 4.]).map_err(w)?;
    let mut output = stream.alloc_zeros::<f32>(4).map_err(w)?;
    let cfg = LaunchConfig::for_num_elems(4);

    let function = load("fill_f32", &kernels::FILL)?;
    let one = 1_f32;
    // SAFETY: every launch below uses the exact selected CUDA source argument
    // types, live owning buffers and bounds; each result is copied back before
    // the buffers are reused or dropped.
    unsafe {
        function
            .builder()
            .arg(&mut output)
            .arg(&one)
            .arg(&n)
            .launch(cfg)
    }
    .map_err(w)?;
    assert_eq!(stream.clone_dtoh(&output).map_err(w)?, [1_f32; 4]);
    println!("owning-image-control symbol=fill_f32 phase=output-validated");

    let function = load("affine_f32", &kernels::AFFINE)?;
    let two = 2_f32;
    unsafe {
        function
            .builder()
            .arg(&n)
            .arg(&dims)
            .arg(&info)
            .arg(&input)
            .arg(&mut output)
            .arg(&two)
            .arg(&one)
            .launch(cfg)
    }
    .map_err(w)?;
    assert_eq!(stream.clone_dtoh(&output).map_err(w)?, [3., 5., 7., 9.]);
    println!("owning-image-control symbol=affine_f32 phase=output-validated");

    let function = load("badd_f32", &kernels::BINARY)?;
    let reverse = stream.clone_htod(&[4_f32, 3., 2., 1.]).map_err(w)?;
    unsafe {
        function
            .builder()
            .arg(&n)
            .arg(&dims)
            .arg(&info)
            .arg(&input)
            .arg(&reverse)
            .arg(&mut output)
            .launch(cfg)
    }
    .map_err(w)?;
    assert_eq!(stream.clone_dtoh(&output).map_err(w)?, [5_f32; 4]);
    println!("owning-image-control symbol=badd_f32 phase=output-validated");

    let function = load("cast_u32_f32", &kernels::CAST)?;
    let integers = stream.clone_htod(&[1_u32, 2, 3, 4]).map_err(w)?;
    unsafe {
        function
            .builder()
            .arg(&n)
            .arg(&dims)
            .arg(&info)
            .arg(&integers)
            .arg(&mut output)
            .launch(cfg)
    }
    .map_err(w)?;
    assert_eq!(stream.clone_dtoh(&output).map_err(w)?, [1., 2., 3., 4.]);
    println!("owning-image-control symbol=cast_u32_f32 phase=output-validated");

    let function = load("is_u32_f32", &kernels::INDEXING)?;
    let indices = stream.clone_htod(&[3_u32, 1]).map_err(w)?;
    let mut selected = stream.alloc_zeros::<f32>(2).map_err(w)?;
    let count = 2_usize;
    let width = 1_usize;
    unsafe {
        function
            .builder()
            .arg(&count)
            .arg(&dims)
            .arg(&info)
            .arg(&indices)
            .arg(&input)
            .arg(&mut selected)
            .arg(&width)
            .arg(&n)
            .arg(&count)
            .arg(&width)
            .launch(cfg)
    }
    .map_err(w)?;
    assert_eq!(stream.clone_dtoh(&selected).map_err(w)?, [4., 2.]);
    println!("owning-image-control symbol=is_u32_f32 phase=output-validated");

    let function = load("fast_sum_f32", &kernels::REDUCE)?;
    let mut sum = stream.alloc_zeros::<f32>(1).map_err(w)?;
    unsafe {
        function
            .builder()
            .arg(&n)
            .arg(&n)
            .arg(&dims)
            .arg(&info)
            .arg(&input)
            .arg(&mut sum)
            .launch(cfg)
    }
    .map_err(w)?;
    assert_eq!(stream.clone_dtoh(&sum).map_err(w)?, [10.]);
    println!("owning-image-control symbol=fast_sum_f32 phase=output-validated");

    let function = load("usqr_f32", &kernels::UNARY)?;
    unsafe {
        function
            .builder()
            .arg(&n)
            .arg(&dims)
            .arg(&info)
            .arg(&input)
            .arg(&mut output)
            .launch(cfg)
    }
    .map_err(w)?;
    assert_eq!(stream.clone_dtoh(&output).map_err(w)?, [1., 4., 9., 16.]);
    println!("owning-image-control symbol=usqr_f32 phase=output-validated");
    Ok(())
}

#[test]
fn loadable_module_missing_requested_function_is_typed_not_found() -> crate::Result<()> {
    assert_eq!(std::env::var("FATHOMDB_REQUIRE_LIVE").as_deref(), Ok("1"));
    let context = CudaContext::new(0).map_err(crate::Error::wrap)?;
    let module = load_kernel_module(&context, &kernels::FILL)?;
    let error = module
        .load_function("fathomdb_deliberately_absent_function")
        .unwrap_err();
    assert_eq!(error.0, cudarc::driver::sys::CUresult::CUDA_ERROR_NOT_FOUND);
    println!(
        "owning-image-control missing-symbol-status={}",
        error.0 as u32
    );
    Ok(())
}

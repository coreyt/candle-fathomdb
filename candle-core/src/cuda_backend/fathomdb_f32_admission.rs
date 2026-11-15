use super::gemm_strided_batched_f32;
use cudarc::{
    cublas::{result::CublasError, sys, CudaBlas, GemmConfig, StridedBatchedConfig},
    driver::{
        sys::CUresult, CudaContext, CudaSlice, CudaStream, DriverError, PrimaryContextLifetime,
    },
};
use std::sync::Arc;

struct Fixture {
    lifetime: Arc<PrimaryContextLifetime>,
    context: Arc<CudaContext>,
    stream: Arc<CudaStream>,
    blas: CudaBlas,
    a: CudaSlice<f32>,
    b: CudaSlice<f32>,
    c: CudaSlice<f32>,
}

fn fixture() -> crate::Result<Fixture> {
    let lifetime = PrimaryContextLifetime::new(0).map_err(crate::Error::wrap)?;
    let context = CudaContext::new_tracked(lifetime.clone()).map_err(crate::Error::wrap)?;
    let stream = context.default_stream();
    let blas = CudaBlas::new(stream.clone()).map_err(crate::Error::wrap)?;
    let a = stream
        .clone_htod(&[1f32, 3., 2., 4.])
        .map_err(crate::Error::wrap)?;
    let b = stream
        .clone_htod(&[5f32, 7., 6., 8.])
        .map_err(crate::Error::wrap)?;
    let c = stream.alloc_zeros::<f32>(4).map_err(crate::Error::wrap)?;
    stream.synchronize().map_err(crate::Error::wrap)?;
    assert!(!context.is_managing_stream_synchronization());
    Ok(Fixture {
        lifetime,
        context,
        stream,
        blas,
        a,
        b,
        c,
    })
}

fn config() -> StridedBatchedConfig<f32> {
    StridedBatchedConfig {
        gemm: GemmConfig {
            transa: sys::cublasOperation_t::CUBLAS_OP_N,
            transb: sys::cublasOperation_t::CUBLAS_OP_N,
            m: 2,
            n: 2,
            k: 2,
            alpha: 1.,
            lda: 2,
            ldb: 2,
            beta: 0.,
            ldc: 2,
        },
        batch_size: 1,
        stride_a: 4,
        stride_b: 4,
        stride_c: 4,
    }
}

#[test]
fn healthy_f32_helper_preserves_existing_numerical_result() -> crate::Result<()> {
    let mut fixture = fixture()?;
    unsafe {
        gemm_strided_batched_f32(
            &fixture.blas,
            config(),
            &fixture.a.as_view(),
            &fixture.b.as_view(),
            &mut fixture.c,
        )
    }
    .map_err(crate::Error::wrap)?;
    // These integer inputs/results are exact under the existing F32/TF32 choices.
    assert_eq!(
        fixture
            .stream
            .clone_dtoh(&fixture.c)
            .map_err(crate::Error::wrap)?,
        [19., 43., 22., 50.]
    );
    assert!(fixture.lifetime.loss().is_none());
    Ok(())
}

#[test]
fn f32_helper_refuses_known_token_loss_before_raw_blas() -> crate::Result<()> {
    let mut fixture = fixture()?;
    // This injects a cached refusal while native CUDA stays healthy; it is not a reset.
    fixture
        .context
        .record_err::<()>(Err(DriverError(CUresult::CUDA_ERROR_CONTEXT_IS_DESTROYED)));
    let first = fixture
        .lifetime
        .loss()
        .expect("the public token-loss seam must be established");

    let result = unsafe {
        gemm_strided_batched_f32(
            &fixture.blas,
            config(),
            &fixture.a.as_view(),
            &fixture.b.as_view(),
            &mut fixture.c,
        )
    };

    assert_eq!(
        result,
        Err(CublasError::Driver(DriverError(
            CUresult::CUDA_ERROR_CONTEXT_IS_DESTROYED
        )))
    );
    assert_eq!(fixture.lifetime.loss(), Some(first));
    Ok(())
}

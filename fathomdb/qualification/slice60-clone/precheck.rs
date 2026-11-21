#[test]
#[ignore = "exclusive leased qualification; reset mode requires separate exact owner action"]
fn prechecked_clone_checks_uuid_before_original_body() -> candle_core::Result<()> {
    let w = candle_core::Error::wrap;
    result::init().map_err(w)?;
    assert_eq!(
        result::device::get_count().map_err(w)?,
        1,
        "exactly one selected visible device"
    );
    let device = result::device::get(0).map_err(w)?;
    let hex: String = result::device::get_uuid(device)
        .map_err(w)?
        .bytes
        .iter()
        .map(|byte| format!("{:02x}", *byte as u8))
        .collect();
    let uuid = format!(
        "GPU-{}-{}-{}-{}-{}",
        &hex[..8],
        &hex[8..12],
        &hex[12..16],
        &hex[16..20],
        &hex[20..]
    );
    assert_eq!(
        std::env::var("FATHOMDB_SELECTED_UUID").as_deref(),
        Ok(uuid.as_str())
    );
    println!("prechecked-clone: identity-before-construction uuid={uuid} visible-devices=1");
    completed_tensor_last_clone_drops_with_a_distinct_final_owner_witness()
}

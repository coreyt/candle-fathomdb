use std::{env, fs, path::PathBuf, process::Command};
fn main() {
    for path in ["original.rs", "precheck.rs"] {
        println!("cargo:rerun-if-changed={path}");
    }
    let digest = Command::new("/usr/bin/sha256sum")
        .arg("original.rs")
        .output()
        .unwrap();
    assert!(digest.status.success());
    assert_eq!(
        String::from_utf8(digest.stdout)
            .unwrap()
            .split_whitespace()
            .next(),
        Some("cfb032c7d45b64ea0e2208f5ce3718c385696761223bfe2993ebc20426d37fc6")
    );
    let original = fs::read_to_string("original.rs").unwrap();
    let body = original.strip_prefix("//! Positive successor controls; real resets require separate venue authorization.\n#![cfg(feature = \"cuda\")]\n").unwrap();
    // Only module headers are removed for include!: every original test-body
    // byte and assertion remains unchanged in the generated compilation unit.
    let generated = format!("{body}\n{}", fs::read_to_string("precheck.rs").unwrap());
    fs::write(
        PathBuf::from(env::var_os("OUT_DIR").unwrap()).join("qualified.rs"),
        generated,
    )
    .unwrap();
}

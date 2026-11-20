#!/usr/bin/env python3
"""Compare the preselected Slice60 linked/package size ceiling (no GPU).

Run: python3 fathomdb/scripts/measure_slice60_artifact_sizes.py --root DIR
DIR contains artifacts/{a,b}/{python,node,cli}; JSON goes to stdout.
A is same-source PTX and B native images. Missing/mismatched archives fail;
ratios above the prospectively selected 2x ceiling report non-adoption.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import zipfile


def sha(data):
    return hashlib.sha256(data).hexdigest()


def inspect(root, arm):
    base = root / "artifacts" / arm
    wheel, = (base / "python").glob("*.whl")
    node = base / "node/fathomdb.linux-x64-gnu.node"
    # The Tegra package retains the same archive-entry shape with arm64 triple.
    if not node.exists():
        node, = (base / "node").glob("*.node")
    node_package, = (base / "node").glob("*.tgz")
    cli = base / "cli/fathomdb"
    cli_package, = (base / "cli").glob("*.tar.gz")
    with zipfile.ZipFile(wheel) as archive:
        python_entry, = [x for x in archive.infolist() if x.filename.endswith(".so")]
        python_native = archive.read(python_entry)
    with tarfile.open(node_package) as archive:
        entry, = [x for x in archive.getmembers() if x.name.endswith(".node")]
        packed_node = archive.extractfile(entry).read()
    if sha(packed_node) != sha(node.read_bytes()):
        raise ValueError("Node archive does not contain its measured linked artifact")
    with tarfile.open(cli_package) as archive:
        entry, = [x for x in archive.getmembers() if x.isfile() and Path(x.name).name == "fathomdb"]
        packed_cli = archive.extractfile(entry).read()
    if sha(packed_cli) != sha(cli.read_bytes()):
        raise ValueError("CLI archive does not contain its measured executable")
    paths = {"python_wheel": wheel, "node_native": node, "node_package": node_package,
             "cli_native": cli, "cli_package": cli_package}
    result = {name: {"bytes": path.stat().st_size, "sha256": sha(path.read_bytes()), "path": str(path)}
              for name, path in paths.items()}
    result["python_native"] = {"bytes": len(python_native), "sha256": sha(python_native), "entry": python_entry.filename}
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    args = parser.parse_args()
    arms = {arm: inspect(args.root, arm) for arm in ("a", "b")}
    ratios = {name: arms["b"][name]["bytes"] / arms["a"][name]["bytes"] for name in arms["a"]}
    result = {"criterion": "each corresponding raw/compressed artifact <=2x same-source PTX baseline",
              "arms": arms, "ratios": ratios, "passes_size_criterion": all(x <= 2 for x in ratios.values()),
              "scope": "size only; not startup/steady/build correctness or public delivery"}
    print(json.dumps(result, indent=2))
    return 0 if result["passes_size_criterion"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

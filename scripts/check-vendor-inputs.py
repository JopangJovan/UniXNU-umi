#!/usr/bin/env python3
"""Check private UMI XBL inputs against the firmware source manifest."""
import argparse
import hashlib
from pathlib import Path
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--uefi", type=Path, default=Path(__file__).resolve().parents[2] / "uefi-umi")
args = parser.parse_args()
manifest = args.uefi / "Platforms/Xiaomi/umiPkg/vendor-inputs.sha256"
errors = []
count = 0
for line in manifest.read_text().splitlines():
    expected, relative = line.split("  ", 1)
    path = args.uefi / "Binaries/umi" / relative
    if not path.is_file():
        errors.append(f"missing: {relative}")
    elif hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        errors.append(f"hash mismatch: {relative}")
    count += 1
if errors:
    raise SystemExit("\n".join(errors))
print(f"PASS: {count} UMI vendor inputs match the firmware manifest")

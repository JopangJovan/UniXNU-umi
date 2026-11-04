#!/usr/bin/env python3
"""Build the UniXNU EFI handoff test for temporary fastboot boot; never flashes."""
import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tomllib
DEVICE = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--unixnu", type=Path, default=DEVICE.parent / "UniXNU")
parser.add_argument("--uefi", type=Path, default=DEVICE.parent / "uefi-umi")
parser.add_argument("--dtb", type=Path, required=True, help="Stock UMI firmware DTB")
args = parser.parse_args()
unixnu, uefi = args.unixnu.resolve(), args.uefi.resolve()
board = tomllib.loads((DEVICE / "board.toml").read_text())
work = unixnu / "out/umi" / board["board"]["os_profile"] / "umi"

def run(*command):
    subprocess.run([str(x) for x in command], cwd=unixnu, check=True)

run(DEVICE / "scripts/check-vendor-inputs.py", "--uefi", uefi)
run(unixnu / "unixnu", "defconfig", "umi_defconfig", "-D", DEVICE)
for step in ["firmware", "package"]:
    run(unixnu / "unixnu", step, "-D", DEVICE, "--uefi", uefi, "--edk2", uefi / "Mu_Basecore")
smoke = work / "smoke"
payload = smoke / "root/EFI/UniXNU"
(payload / "Payloads").mkdir(parents=True, exist_ok=True)
shutil.copy2(work / "package/Build/Out/AARCH64-DEBUG/HelloPayload.efi", payload / "Payloads/HelloPayload.efi")
(payload / "unixnu.toml").write_text('''version = 1

[boot]
timeout = 5
default = "umi-hello"

[ui]
title = "UniXNU — Xiaomi Mi 10"

[[entry]]
id = "umi-hello"
title = "UMI firmware handoff test"
type = "efi"
path = "Payloads/HelloPayload.efi"
args = "plain pause"

[[entry]]
id = "restart"
title = "Restart"
type = "action"
action = "reset"
''')
image = smoke / "umi-smoke.fat"
with image.open("wb") as f:
    f.truncate(32 * 1024 * 1024)
run("mformat", "-i", image, "::")
run("mcopy", "-s", "-i", image, smoke / "root/EFI", "::/")
output = smoke / "umi-unixnu-smoke.img"
run(unixnu / "unixnu", "bootimg", "-D", DEVICE, "--uefi", uefi,
    "--dtb", args.dtb.resolve(), "--ramdisk", image, "-o", output)
print(f"Ready for temporary test: fastboot boot {output}")

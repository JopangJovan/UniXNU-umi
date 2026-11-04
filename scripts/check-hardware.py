#!/usr/bin/env python3
"""Compile the UMI hardware tree and verify its platform handoff bindings."""
import argparse
import hashlib
import json
from pathlib import Path
import struct
import subprocess
import sys
import tempfile
import tomllib

DEVICE = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--unixnu", type=Path, default=DEVICE.parent / "UniXNU")
parser.add_argument("--soc", type=Path, default=DEVICE.parent / "UniXNU-sm8250-common")
parser.add_argument("--stock-dtb", type=Path)
args = parser.parse_args()
sys.path.insert(0, str(args.unixnu / "scripts"))
from unixnu.devicetree import read_fdt, registers, generate
from unixnu.profiles import merge

def find(tree, name):
    return next(n for n in tree.walk() if n.name == name)

with tempfile.TemporaryDirectory(prefix="unixnu-umi-check-") as tmp:
    dtb = Path(tmp) / "umi.dtb"
    subprocess.run(["dtc", "-I", "dts", "-O", "dtb", "-i", str(args.soc / "dts"),
                    "-o", str(dtb), str(DEVICE / "dts/board.dts")], check=True)
    tree = read_fdt(dtb.read_bytes())
    cpus = find(tree, "cpus")
    affinity = [registers(n)[0][0] for n in cpus.children]
    assert affinity == list(range(0, 0x800, 0x100)), affinity
    assert sum(n.enabled() for n in cpus.children) == 1
    assert cpus.scalar("timebase-frequency") == 19200000
    assert registers(find(tree, "interrupt-controller@17a00000")) == [(0x17a00000, 0x10000), (0x17a60000, 0x100000)]
    assert find(tree, "psci").strings("method") == ["smc"]
    bank = registers(find(tree, "memory@c0000000"))[0]
    assert bank == (0xc0000000, 0xc0000000)
    board = tomllib.loads((DEVICE / "board.toml").read_text())
    profile = args.unixnu / "profiles/os" / board["board"]["os_profile"] / "profile.toml"
    config = merge(tomllib.loads(profile.read_text()), board)
    # Synthetic identity for host conversion only; never package this as a device identity.
    adt = generate(dtb, config, unique_chip_id="0123456789abcdef")
    assert adt
    result = {"result": "PASS", "enabled_cpus": 1, "timer_hz": 19200000,
              "gic": "v3", "psci": "smc", "adt_conversion": "PASS", "device_boot": "not tested"}
    if args.stock_dtb:
        stock = read_fdt(args.stock_dtb.read_bytes())
        assert [registers(n)[0][0] for n in find(stock, "cpus").children if n.strings("device_type") == ["cpu"]] == affinity
        assert registers(find(stock, "interrupt-controller@17a00000")) == registers(find(tree, "interrupt-controller@17a00000"))
        assert find(stock, "psci").strings("method") == ["smc"]
        assert find(stock, "timer").scalar("clock-frequency") == 19200000
        stock_memory = next(n for n in stock.children if n.strings("device_type") == ["memory"])
        assert bank in registers(stock_memory)
        result["stock_dtb_sha256"] = hashlib.sha256(args.stock_dtb.read_bytes()).hexdigest()
    print(json.dumps(result, indent=2))

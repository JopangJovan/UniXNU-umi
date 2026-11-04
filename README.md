# UniXNU for Xiaomi Mi 10 (UMI)

Fresh standalone UniXNU port for SM8250 / Adreno 650. This is an early bring-up, not a usable iOS release. HakiOS is not the boot or kernel runtime.

## Repositories

- [UniXNU framework](https://github.com/JopangJovan/UniXNU)
- [UMI UEFI](https://github.com/JopangJovan/Mu-Silicium)
- [DarwinBoot](https://github.com/JopangJovan/DarwinBoot)
- [SM8250 platform](https://github.com/JopangJovan/UniXNU-sm8250-common)

## Current bring-up

The upstream iPadOS 17.7.11 arm64 profile is selected. One boot CPU, GICv3, timer and PSCI are described. The hardware DTS compiles and converts to ADT. UMI DEBUG firmware and a temporary Android boot image build successfully. The reduced UEFI reaches the UniXNU menu on hardware. The XNU kernel builds and prelinks; its device handoff is not yet verified.

Native UFS, touch, Adreno 650, audio, Wi-Fi, Bluetooth, battery and brightness still require adaptation to UniXNU's ABI. The existing HakiOS port is hardware reference material only. arm64e is not enabled without per-core PAC qualification.

## Local setup

Keep sibling checkouts `UniXNU`, `UniXNU-sm8250-common`, `UniXNU-umi`, and `uefi-umi`. Use the pinned SoC feed, or copy `local.toml.example` to `local.toml` during platform development. Store extracted firmware only in the local UEFI checkout.

From UniXNU: `./unixnu defconfig umi_defconfig -D ../UniXNU-umi`, then `./unixnu status --json`. `scripts/check-hardware.py --stock-dtb /path/to/umi.dtb` checks the hardware description against stock input.

See `BRINGUP.md`, `porting.toml` and `reports/` for evidence and remaining work. Use `adb reboot bootloader` to enter stock fastboot. Initial tests use `fastboot boot`; do not flash incomplete bring-up images.

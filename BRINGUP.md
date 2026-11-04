# UMI standalone bring-up

## Implemented and host-checked

- SM8250 topology, GICv3, timer and PSCI in the shared SoC repository.
- UMI board enables one CPU; ADT uses the stock contiguous 0xc0000000+0xc0000000 bank.
- Stock resource comparison and ADT generation pass (`reports/hardware-check.json`).
- Standalone UMI DEBUG FD embeds UniXNU, DarwinBoot, FAT and initrd BlockIO.
- Board-local SEC preserves incoming x0 in the expected HOB. Shared firmware SEC templates are untouched.
- Android boot-image packer validates shim, FD, DTB and payload. The smoke image contains the upstream HelloPayload EFI application.

## Verification commands

From ../UniXNU:

```sh
./unixnu defconfig umi_defconfig -D ../UniXNU-umi
./unixnu status --json
../UniXNU-umi/scripts/check-hardware.py --stock-dtb /path/to/umi.dtb
./unixnu firmware
./unixnu package
./unixnu bootimg --ramdisk /path/to/umi-smoke.fat
```

The hardware and firmware build reports are committed; bulky local compiler logs are under the UniXNU output tree. The reduced firmware reaches the UniXNU menu on UMI (user observation). FAT initrd discovery and the HelloPayload EFI application launch succeed (RESULT PASS 0 passed 0 failed, with no optional checks requested). XNU handoff is not verified.

## Remaining sequence

1. Test UniXNU menu and smoke EFI payload via temporary fastboot boot.
2. Linux toolchain setup and Darwin 23 XNU build/prelink now pass; test its handoff after the EFI payload.
3. Matching iPadOS 17.7.11 kernelcache and static trust input were obtained; OS root and persistent Data still need integration.
4. Verify early kernel handoff, timer and owned-memory window; then enable secondary CPUs.
5. Adapt storage/root and framebuffer before touch and GPU.
6. Port UMI peripherals individually; the working HakiOS drivers are hardware references only.

Use `adb reboot bootloader`, never `adb reboot fastboot`. Initial bring-up uses temporary boot images; no partition flashing. Do not use synthetic host-test identity values for an OS payload.

The initial all-module firmware restarted after a sleep-callback warning. Removing storage and DSP loading modules allowed the menu to appear; the exact failing module has not been isolated.

## Reproduce the firmware test

`scripts/build-smoke.py --dtb /path/to/umi.dtb` verifies local firmware hashes, builds firmware/package and packs the FAT payload. It prints a `fastboot boot` command and never flashes or boots automatically.

CI runs host device-tree and porting-record checks only; OS image packaging is not advertised before storage/root integration is complete.

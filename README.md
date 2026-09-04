# TECNO MegaPad 11 (T1101)

OrangeFox / TWRP device tree for Android 12.1. Board is mt6789
(Helio G99, also sold as MT8781), kernel 5.10.237 android12-5.10 GKI,
firmware T1101-M1101ABCD-U-OP-260410V1046.

There is no dedicated recovery partition on this device. Recovery is
packed into vendor_boot, the stock boot.img stays untouched (KernelSU
etc. keep working). Only vendor_boot.img gets built and flashed.

## what works

tested on my unit:

| feature | state |
|---|---|
| boot | yes |
| touch | yes, patched module |
| adb | yes, adb only (no mtp) |
| charging / battery | yes |
| decrypt /data | yes, pin prompt |
| backup & restore | yes |
| themes | yes |
| otg mouse & keyboard | yes |
| otg usb storage | yes, read and write |

## building

with the common OrangeFox builder:

- manifest branch: 12.1
- device tree: this repo
- device path: device/tecno/T1101
- device name: T1101
- build target: vendorboot

or locally:

```
lunch fox_T1101-eng
mka adbd vendorbootimage
```

twrp builds the same way with twrp_T1101-eng.

## flashing

```
fastboot flash vendor_boot vendor_boot.img
fastboot reboot recovery
```

flashing from inside recovery works too: Install -> image -> vendor_boot,
then Reboot -> Recovery. Rollback is just flashing the stock
vendor_boot.img the same way.

## notes

- transsion kernel modules refuse to work in recovery boot mode. two
  small patches undo this: tools/patch_adaptive_ts.py (touch) and
  tools/patch_tran_otg.py (otg power). both are idempotent.
- otg is handled by /vendor/firmware/otgd.sh, started from
  init.recovery.mt6789.rc. it needs its seclabel line, dont remove it.
- after an ota that bumps the kernel, pull the new modules from the
  stock vendor_boot (tools/unpack_vendor_boot.py), re-apply the two
  patches and rebuild. otherwise insmod fails and the device bootloops.
  check with: python3 tools/check_fw_match.py boot.img
- some usb sticks (smi controllers) fail their first enumerate. if a
  stick does not show up after a few seconds, replug it once.
- otg and adb share the single usb-c port. adb comes back when you
  replug the pc cable.

## thanks

LineageOS device tree template, negroweed's infinix XPad tree,
OrangeFox and TWRP teams.

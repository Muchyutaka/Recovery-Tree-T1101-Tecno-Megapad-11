Tecno Megapad 11 T1101 Device tree — TWRP **and** OrangeFox (`twrp_T1101-eng` / `fox_T1101-eng`)

> ✅ **Status: VERIFIED READY — build & flash.** The tree was validated against the
> user's own stock `260410V1046` dump: all 207 modules, `modules.load*`, the DTB
> (md5 `b2149d4f…`), `fstab.mt6789` and the vendor cmdline are byte-identical to
> stock. The device kernel (`…gf82f7360927e-ab14119954`) accepts the modules'
> vermagic (`…g9d8141349139-dirty`) — same kernel version + KMI; the stock
> firmware pairs them exactly the same way. Full story:
> [`BOOTLOOP_ANALYSIS.md`](BOOTLOOP_ANALYSIS.md).
> Flash **only `vendor_boot`** — never a `boot.img` built from a CI kernel.

> ⚠️ **Status:** fixed after bootloop analysis — see
> [`BOOTLOOP_ANALYSIS.md`](BOOTLOOP_ANALYSIS.md) before building/flashing.
> Key points: this tree now carries **T1101 stock `vendor_boot` modules
> (kernel 5.10.237-android12-9-g9d8141349139-dirty)**, `fstab.mt6789`, and
> `init.recovery.mt6789.rc` (`ro.hardware = mt6789`). The modules must match the
> kernel of the firmware on your device (`adb shell cat /proc/version`), and you
> must flash **only `vendor_boot`** — never a `boot.img` from a GKI CI kernel.
>
> **OrangeFox:** `lunch fox_T1101-eng && mka adbd vendorbootimage`
> (CI recipe in [`ci/orangefox_build.yml`](ci/orangefox_build.yml) — copy it to
> `.github/workflows/` to enable one-click builds).
> Flash the resulting `vendor_boot.img` only.

Basic   | Spec Sheet
-------:|:-------------------------
CPU     | Octa-core (2x2.2 GHz Cortex-A76 & 6x2.0 GHz Cortex-A55)
Chipset | MediaTek Helio G99 (MT8781)
GPU     | Mali-G57 MC2
Memory  | 8 GB RAM
Shipped Android Version | 14
Storage | 128/256 GB
Display | 1200 x 1920 pixels, 11.0 inches

<img width="1920" height="1050" alt="1000027022" src="https://github.com/user-attachments/assets/511643d9-b0fd-4349-b288-4f750b2966b1" />

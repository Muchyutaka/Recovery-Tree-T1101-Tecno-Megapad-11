Recovery device tree for the **Tecno MegaPad 11 (T1101)**, tested building **OrangeFox Recovery**.

**Known bugs:** None I think idk

## Flashing Instructions

1. Enable **OEM unlocking** in Developer Options, then unlock the bootloader:
   ```
   fastboot flashing unlock
   ```
2. Disable `vbmeta` verification, if you haven't already.
3. Reboot to system and complete initial setup.
4. Reboot back into fastboot mode.
5. Flash the recovery image to the `vendor_boot` partition:
   ```
   fastboot flash vendor_boot customrecoveryfilename.img
   ```

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

## Credits

- [aospdtgen](https://github.com/aospdtgen/aospdtgen)
- [negroweed](https://github.com/negroweed) — Infinix XPAD (X1101) TWRP tree
- The OrangeFox and TWRP teams

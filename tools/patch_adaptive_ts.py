#!/usr/bin/env python3
"""
patch_adaptive_ts.py — neutralize the boot-mode gate in Transsion adaptive-ts.ko

Root cause of dead touch in custom recovery on TECNO T1101 (mt8781):
  adaptive-ts.ko init_module() (tpd_device_init, src line 717) calls the
  platform-ops boot-mode getter = mtk_get_boot_mode() @ .text+0x6c50:

      mtk_get_boot_mode():
          np = of_find_node_by_path("/chosen")
          prop = of_get_property(np, "atag,boot")     # u32 written by LK
          raw = value; if raw > 9 -> 0
          if (1 << raw) & 0x52  -> return 2           # META/FACTORY-ish: load
          if (1 << raw) & 0x304 -> print "bootmode=%d don't load touch !"
                                    return 1          # raw 2 = RECOVERY, 8, 9
          return 0                                    # NORMAL

  init_module() then does:  if (mode & ~2) -> "bootmode don't load touch !"
  and NEVER registers the "tran-tpd" platform driver -> tpd_probe never runs
  -> supplier list never parsed -> chipone_icnl9951r never probed -> no touch.
  On a normal Android boot this returns 0 and everything works (stock dmesg:
  "tpd_device_init 717: boot driver mode 0 load touch !").

Fix: replace the first two instructions of mtk_get_boot_mode with
      movz w0, #0        ; 0x52800000
      ret                ; 0xD65F03C0
  so the framework always behaves exactly like a normal boot. This is the
  value the function returns on every working stock boot, so behaviour is
  unchanged for normal mode; it only stops the recovery-mode refusal.
  KCFI/CFI type-id words live outside the function body and are untouched.

Usage:  python3 tools/patch_adaptive_ts.py [path/to/adaptive-ts.ko]
Idempotent; verifies expected original bytes before patching.
"""
import hashlib
import sys
import os

DEFAULT = os.path.join(os.path.dirname(__file__), "..",
                       "recovery", "root", "lib", "modules", "adaptive-ts.ko")

TEXT_SH_OFFSET = 0x1000          # .text sh_offset in this module
FUNC_OFF = 0x6C50                # mtk_get_boot_mode offset in .text
FILE_OFF = TEXT_SH_OFFSET + FUNC_OFF

ORIG = bytes.fromhex("3f2303d55e8600f8")   # paciasp ; str x30,[x18],#8
PATCH = bytes.fromhex("00008052c0035fd6")  # movz w0,#0 ; ret


def main(path):
    with open(path, "rb") as f:
        data = f.read()
    cur = data[FILE_OFF:FILE_OFF + 8]
    if cur == PATCH:
        print(f"[+] already patched ({hashlib.md5(data).hexdigest()})")
        return 0
    if cur != ORIG:
        print(f"[!] unexpected bytes at {FILE_OFF:#x}: {cur.hex()}")
        print("    refusing to patch (module differs from known build)")
        return 1
    data = data[:FILE_OFF] + PATCH + data[FILE_OFF + 8:]
    with open(path, "wb") as f:
        f.write(data)
    print(f"[+] patched mtk_get_boot_mode @ file {FILE_OFF:#x}: "
          f"{ORIG.hex()} -> {PATCH.hex()}")
    print(f"[+] new md5: {hashlib.md5(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT))

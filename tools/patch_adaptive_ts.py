#!/usr/bin/env python3
"""
patch adaptive-ts.ko so the touch driver loads in recovery.

mtk_get_boot_mode() returns non zero on recovery boots and the module
then skips the whole touch setup ("bootmode don't load touch !"). patch
it to always return 0, same as a normal boot.

usage: python3 tools/patch_adaptive_ts.py [adaptive-ts.ko]
idempotent, checks the original bytes first.
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

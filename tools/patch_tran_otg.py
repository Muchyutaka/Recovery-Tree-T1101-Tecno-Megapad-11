#!/usr/bin/env python3
"""
patch tran_otg.ko so otg vbus can be enabled from userspace in recovery.

store_OTG_CTL() ignores writes unless a "plug in" flag is set, and that
flag never gets set in recovery. the probe also stores the mtk boot mode
and tran_otg_enable_vbus() does nothing on recovery boots.

two patches:
  1. make the skip branch in store_OTG_CTL unconditional
  2. nop the boot mode store so recovery counts as a normal boot

usage: python3 tools/patch_tran_otg.py [tran_otg.ko]
idempotent, checks the original bytes first.
"""
import hashlib
import sys
import os

DEFAULT = os.path.join(os.path.dirname(__file__), "..",
                       "recovery", "root", "lib", "modules", "tran_otg.ko")

TEXT_SH_OFFSET = 0x1000          # .text sh_offset in this module

PATCHES = [
    # (name, .text offset, original bytes, patched bytes)
    ("plug gate (store_OTG_CTL)", 0x1BBC,
     bytes.fromhex("c4020035"),   # cbnz w4, #0x1c14
     bytes.fromhex("16000014")),  # b    #0x1c14
    ("boot-mode store (atag,boot -> info->boot_mode)", 0x0FC4,
     bytes.fromhex("886e02b9"),   # str w8, [x20, #0x26c]
     bytes.fromhex("1f2003d5")),  # nop
]


def main(path):
    with open(path, "rb") as f:
        data = f.read()
    changed = False
    for name, off, orig, patch in PATCHES:
        fo = TEXT_SH_OFFSET + off
        cur = data[fo:fo + len(orig)]
        if cur == patch:
            print(f"[+] already patched: {name}")
            continue
        if cur != orig:
            print(f"[!] unexpected bytes for {name} at {fo:#x}: {cur.hex()}")
            print("    refusing to patch (module differs from known build)")
            return 1
        data = data[:fo] + patch + data[fo + len(orig):]
        changed = True
        print(f"[+] patched {name} @ file {fo:#x}: {orig.hex()} -> {patch.hex()}")
    if changed:
        with open(path, "wb") as f:
            f.write(data)
    print(f"[+] md5: {hashlib.md5(data).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else DEFAULT))

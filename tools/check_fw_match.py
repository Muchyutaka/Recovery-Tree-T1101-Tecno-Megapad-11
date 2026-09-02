#!/usr/bin/env python3
"""Verify that this tree's kernel modules match a stock T1101 boot.img.

The recovery in this tree is a vendor_boot ramdisk: the device keeps its STOCK
kernel (boot.img), so every module under recovery/root/lib/modules must carry
exactly the same kernel release (vermagic) as that boot.img. If it doesn't,
insmod fails for all modules and the device bootloops (see BOOTLOOP_ANALYSIS.md).

Usage:
  python3 tools/check_fw_match.py <stock_boot.img>            # from your firmware
  python3 tools/check_fw_match.py <Image|Image.gz>            # extracted kernel
  # ...or skip images entirely and just compare by hand:
  #   adb shell cat /proc_version   (device)   vs  vermagic printed below

Exit codes: 0 = match, 1 = mismatch, 2 = could not determine kernel version.
No dependencies beyond Python 3 (gzip kernels are handled internally).
"""

import glob
import os
import re
import sys
import zlib

HERE = os.path.dirname(os.path.abspath(__file__))
MODULES_DIR = os.path.join(HERE, "..", "recovery", "root", "lib", "modules")

BANNER_RE = re.compile(rb"Linux version [ -~]{10,300}")
VERMAGIC_RE = re.compile(rb"vermagic=(\S+)")


def kernel_banners(path):
    """Return 'Linux version ...' strings found in a boot image / kernel blob.

    Handles uncompressed Images (plain text banner) and gzip-compressed
    Image.gz (as used on MT6789 GKI boots), including concatenated streams.
    """
    data = open(path, "rb").read()
    found = set()
    for m in BANNER_RE.finditer(data):
        found.add(m.group().decode())
    off = 0
    while True:
        off = data.find(b"\x1f\x8b\x08", off)
        if off < 0:
            break
        try:
            dec = zlib.decompressobj(16 + zlib.MAX_WBITS)
            out = dec.decompress(data[off:])
            for m in BANNER_RE.finditer(out):
                found.add(m.group().decode())
        except Exception:
            pass
        off += 1
    return found


def module_vermagics():
    """Map module filename -> vermagic for every .ko in this tree."""
    out = {}
    for mod in sorted(glob.glob(os.path.join(MODULES_DIR, "*.ko"))):
        m = VERMAGIC_RE.search(open(mod, "rb").read())
        if m:
            out[os.path.basename(mod)] = m.group(1).decode()
    return out


def main(argv):
    mods = module_vermagics()
    if not mods:
        print("ERROR: no modules with vermagic found in", MODULES_DIR)
        return 2
    unique = sorted(set(mods.values()))
    print(f"Tree modules       : {len(mods)} .ko")
    for v in unique:
        n = sum(1 for x in mods.values() if x == v)
        print(f"  vermagic         : {v}  ({n} modules)")

    if len(argv) < 2:
        print("\nNo image given. Compare the vermagic above with:")
        print("  adb shell cat /proc_version")
        print("The release (3rd field after 'Linux version') must be IDENTICAL.")
        return 2

    banners = set()
    for path in argv[1:]:
        banners |= kernel_banners(path)
    if not banners:
        print(f"\nERROR: no 'Linux version' banner found in {argv[1:]}")
        return 2

    releases = set()
    for b in banners:
        rel = b.split()[2] if len(b.split()) > 2 else "?"
        releases.add(rel)
        print(f"\nStock kernel       : {b}")
        print(f"  kernel release   : {rel}")

    if len(releases) > 1:
        print("\nWARNING: multiple kernel releases found; using all for comparison.")
    verdict = []
    for rel in releases:
        ok = rel in unique
        note = "OK - exact vermagic match"
        if not ok:
            # GKI + CONFIG_MODVERSIONS kernels (like this device's) tolerate a
            # different localversion suffix within the SAME kernel version and
            # KMI: the stock 260410V1046 firmware itself runs kernel
            # 5.10.237-android12-9-00014-gf82f7360927e-ab14119954 with modules
            # vermagic 5.10.237-android12-9-g9d8141349139-dirty. Symbol CRCs
            # (modversions) are what actually gate loading.
            def base(rel):
                m = re.match(r"(\d+\.\d+\.\d+)-(android\d+-\d+)", rel)
                return m.groups() if m else None
            rb, tb = base(rel), [base(v) for v in unique]
            if rb and any(rb == t for t in tb):
                ok = True
                note = ("OK - same kernel version + KMI as modules; localversion "
                        "skew is tolerated by this GKI/modversions kernel "
                        "(stock firmware pairs them the same way)")
            else:
                note = ("MISMATCH - different kernel version/KMI; modversion CRCs "
                        "will not resolve -> modules rejected -> BOOTLOOP")
        verdict.append(ok)
        print(f"\nmatch('{rel}')      : {note}")
    return 0 if all(verdict) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))

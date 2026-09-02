#!/usr/bin/env python3
"""Unpack an Android vendor_boot (v3/v4) image with an LZ4-legacy ramdisk.

Usage: python3 tools/unpack_vendor_boot.py <vendor_boot.img> <out_dir>
Extracts: all concatenated cpio archives + the DTB blob. Pure python.
"""
import os
import struct
import sys


def lz4_block_decompress(src):
    dst = bytearray()
    i, n = 0, len(src)
    while i < n:
        token = src[i]; i += 1
        lit_len = token >> 4
        if lit_len == 15:
            while True:
                b = src[i]; i += 1; lit_len += b
                if b != 255: break
        dst += src[i:i + lit_len]; i += lit_len
        if i >= n: break
        offset = src[i] | (src[i + 1] << 8); i += 2
        match_len = token & 0xF
        if match_len == 15:
            while True:
                b = src[i]; i += 1; match_len += b
                if b != 255: break
        match_len += 4
        start = len(dst) - offset
        if match_len <= offset:
            dst += dst[start:start + match_len]
        else:
            for j in range(match_len):
                dst.append(dst[start + j])
    return bytes(dst)


def lz4_legacy(data):
    assert data[:4] == b"\x02\x21\x4c\x18", "not lz4-legacy"
    off, out = 4, bytearray()
    while off + 4 <= len(data):
        csize, = struct.unpack("<I", data[off:off + 4])
        if csize == 0 or csize > len(data) - off - 4:
            break
        out += lz4_block_decompress(data[off + 4:off + 4 + csize])
        off += 4 + csize
    return bytes(out)


def extract_cpio_all(cpio, dest):
    pos, idx = 0, 0
    while pos + 110 <= len(cpio) and cpio[pos:pos + 6] in (b"070701", b"070702"):
        while pos + 110 <= len(cpio):
            if cpio[pos:pos + 6] not in (b"070701", b"070702"):
                break
            f = lambda k: int(cpio[pos + 6 + 8 * k:pos + 14 + 8 * k], 16)
            mode, filesize, namesize = f(1), f(6), f(11)
            name = cpio[pos + 110:pos + 110 + namesize - 1].decode("utf-8", "replace")
            data_off = (pos + 110 + namesize + 3) & ~3
            edata = cpio[data_off:data_off + filesize]
            pos = (data_off + filesize + 3) & ~3
            if name == "TRAILER!!!":
                break
            path = os.path.join(dest, name)
            if mode & 0o170000 == 0o040000:
                os.makedirs(path, exist_ok=True)
            elif mode & 0o170000 == 0o120000:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                if os.path.lexists(path): os.unlink(path)
                os.symlink(edata.decode("utf-8", "replace"), path)
            else:
                os.makedirs(os.path.dirname(path), exist_ok=True)
                with open(path, "wb") as fh: fh.write(edata)
        while pos < len(cpio) and cpio[pos:pos + 1] == b"\0":
            pos += 1
        idx += 1
    return idx


def main(path, out):
    d = open(path, "rb").read()
    assert d[:8] == b"VNDRBOOT"
    vrsz, = struct.unpack("<I", d[24:28])
    page = 4096
    cpio = lz4_legacy(d[page:page + vrsz])
    print(f"ramdisk {vrsz} -> {len(cpio)} bytes")
    n = extract_cpio_all(cpio, out)
    print(f"extracted {n} cpio archive(s) to {out}")
    # DTB: first FDT magic after the ramdisk area
    off = d.find(b"\xd0\x0d\xfe\xed", page + vrsz)
    if off > 0:
        total, = struct.unpack(">I", d[off + 4:off + 8])
        with open(f"{out}/__dtb.img", "wb") as fh: fh.write(d[off:off + total])
        print(f"dtb: {total} bytes @ {off}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

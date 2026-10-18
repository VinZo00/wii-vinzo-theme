"""Parser minimale BRLYT: materiali (colori TEV) e pannelli (colori vertici)."""
import struct


def sections(data):
    magic, bom, ver, size, hdr, n = struct.unpack_from(">4sHHIHH", data, 0)
    assert magic == b"RLYT", magic
    off = hdr
    for _ in range(n):
        kind, ln = struct.unpack_from(">4sI", data, off)
        yield kind.decode(), off, ln
        off += ln


def parse(data):
    textures, materials, panes = [], [], []
    for kind, off, ln in sections(data):
        if kind == "txl1":
            n = struct.unpack_from(">H", data, off + 8)[0]
            base = off + 12
            for i in range(n):
                no = struct.unpack_from(">I", data, base + i * 8)[0]
                end = data.index(b"\0", base + no)
                textures.append(data[base + no:end].decode())
        elif kind == "mat1":
            n = struct.unpack_from(">H", data, off + 8)[0]
            for i in range(n):
                mo = off + struct.unpack_from(">I", data, off + 12 + i * 4)[0]
                name = data[mo:mo + 20].split(b"\0")[0].decode()
                c1 = struct.unpack_from(">4h", data, mo + 0x14)
                c2 = struct.unpack_from(">4h", data, mo + 0x1C)
                c3 = struct.unpack_from(">4h", data, mo + 0x24)
                k = [struct.unpack_from(">4B", data, mo + 0x2C + j * 4) for j in range(4)]
                flags = struct.unpack_from(">I", data, mo + 0x3C)[0]
                ntex = flags & 0xF
                tex = [struct.unpack_from(">H", data, mo + 0x40 + j * 4)[0] for j in range(ntex)]
                materials.append(dict(name=name, off=mo, c1=c1, c2=c2, c3=c3, k=k, flags=flags, tex=[textures[t] for t in tex]))
        elif kind in ("pic1", "pan1", "txt1", "wnd1", "bnd1"):
            name = data[off + 0x0C:off + 0x1C].split(b"\0")[0].decode()
            alpha = data[off + 0x0A]
            sx, sy = struct.unpack_from(">ff", data, off + 0x40)
            w, h = struct.unpack_from(">ff", data, off + 0x44)
            p = dict(kind=kind, name=name, off=off, alpha=alpha, size=(w, h))
            if kind == "pic1":
                p["vc"] = [struct.unpack_from(">4B", data, off + 0x4C + j * 4) for j in range(4)]
                p["mat"] = struct.unpack_from(">H", data, off + 0x5C)[0]
            if kind == "txt1":
                p["mat"] = struct.unpack_from(">H", data, off + 0x50)[0]
                p["top"] = struct.unpack_from(">4B", data, off + 0x5C)
                p["bot"] = struct.unpack_from(">4B", data, off + 0x60)
            if kind == "wnd1":
                p["wnd_off"] = off + 0x4C
            panes.append(p)
    return textures, materials, panes

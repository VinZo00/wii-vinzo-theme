"""Elenca le animazioni di colore (RLMC/RLVC) nei brlan di un archivio."""
import os, sys, struct
sys.path.insert(0, os.path.dirname(__file__))
import u8


def parse_brlan(data):
    """Ritorna lista di (pane, tag, target, [(frame, value, slope, offset_value)])."""
    assert data[:4] == b"RLAN"
    off = struct.unpack_from(">H", data, 0xC)[0]
    assert data[off:off + 4] == b"pai1"
    pai = off
    n_entries = struct.unpack_from(">H", data, pai + 0x0E)[0]
    ent_off = struct.unpack_from(">I", data, pai + 0x10)[0]
    n_tex = struct.unpack_from(">H", data, pai + 0x0C)[0]
    res = []
    for e in range(n_entries):
        eo = pai + struct.unpack_from(">I", data, pai + ent_off + e * 4)[0]
        name = data[eo:eo + 20].split(b"\0")[0].decode()
        ntags = data[eo + 20]
        for t in range(ntags):
            to = eo + struct.unpack_from(">I", data, eo + 24 + t * 4)[0]
            tag = data[to:to + 4].decode()
            nent = data[to + 4]
            for k in range(nent):
                ko = to + struct.unpack_from(">I", data, to + 8 + k * 4)[0]
                idx, target, dtype = data[ko], data[ko + 1], data[ko + 2]
                nkeys = struct.unpack_from(">H", data, ko + 4)[0]
                key_off = ko + struct.unpack_from(">I", data, ko + 8)[0]
                keys = []
                for j in range(nkeys):
                    if dtype == 2:
                        f, v, s = struct.unpack_from(">fff", data, key_off + j * 12)
                        keys.append((f, v, s, key_off + j * 12 + 4))
                    else:
                        f, v = struct.unpack_from(">fH", data, key_off + j * 8)
                        keys.append((f, v, None, None))
                res.append((name, tag, idx, target, keys))
    return res


if __name__ == "__main__":
    for path, d, c in u8.parse(open(sys.argv[1], "rb").read()):
        if d or not path.endswith(".brlan"):
            continue
        for name, tag, idx, target, keys in parse_brlan(c):
            if tag in ("RLMC", "RLVC"):
                vals = sorted({round(k[1]) for k in keys})
                print(f"{path:45s} {name:18s} {tag} t={target:2d} {vals}")

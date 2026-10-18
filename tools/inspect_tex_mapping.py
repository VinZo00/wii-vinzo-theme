"""Mostra texcoord dei pannelli e TexSRT/wrap dei materiali per un brlyt."""
import os, sys, struct
sys.path.insert(0, os.path.dirname(__file__))
import u8, brlyt

arc, lyt, prefixes = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
data = next(c for p, d, c in u8.parse(open(arc, "rb").read()) if p.endswith(lyt))
tex, mats, panes = brlyt.parse(data)
for p in panes:
    if p["kind"] != "pic1" or not p["name"].startswith(tuple(prefixes)):
        continue
    off = p["off"]
    ncoord = data[off + 0x5E]
    coords = [struct.unpack_from(">8f", data, off + 0x60 + i * 32) for i in range(ncoord)]
    tx, ty = struct.unpack_from(">ff", data, off + 0x2C)
    m = mats[p["mat"]]
    mo = m["off"]; flags = m["flags"]
    ntex = flags & 0xF; nsrt = (flags >> 4) & 0xF; ngen = (flags >> 8) & 0xF
    wraps = [struct.unpack_from(">HBB", data, mo + 0x40 + i * 4) for i in range(ntex)]
    so = mo + 0x40 + ntex * 4
    srts = [struct.unpack_from(">5f", data, so + i * 20) for i in range(nsrt)]
    print(f"{p['name']:12s} pos=({tx:.0f},{ty:.0f}) size={p['size']} mat={m['name']} tex={m['tex']}")
    print(f"   wraps={wraps} srt={[tuple(round(v, 3) for v in s) for s in srts]} gens={ngen} flags={flags:#x}")
    for c in coords:
        print("   uv", tuple(round(v, 3) for v in c))

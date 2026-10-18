"""Confronta un csm di riferimento con il base: texture e materiali cambiati."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import u8, lz77, tpl, brlyt

arc_dir, csm = sys.argv[1], sys.argv[2]
names = sys.argv[3:]
ref = {p: c for p, d, c in u8.parse(open(csm, "rb").read()) if not d}
for name in names:
    other = ref["layout/common/" + name]
    other = lz77.decompress(other) if other[:4] == b"LZ77" else other
    base = {p: c for p, d, c in u8.parse(open(os.path.join(arc_dir, name + ".arc"), "rb").read()) if not d}
    oth = {p: c for p, d, c in u8.parse(other) if not d}
    print("==", name, "files base", len(base), "ref", len(oth), "solo ref:", set(oth) - set(base), "solo base:", set(base) - set(oth))
    for p in sorted(base):
        if p not in oth or oth[p] == base[p]:
            continue
        if p.endswith(".tpl"):
            a = tpl.images(base[p])[0]; b = tpl.images(oth[p])[0]
            print(f"  TPL {p}: {a['w']}x{a['h']} {tpl.FMT[a['fmt']]} -> {b['w']}x{b['h']} {tpl.FMT[b['fmt']]}")
        elif p.endswith(".brlyt"):
            ma = brlyt.parse(base[p])[1]; mb = brlyt.parse(oth[p])[1]
            for x, y in zip(ma, mb):
                if (x["c1"], x["c2"], x["c3"], x["k"]) != (y["c1"], y["c2"], y["c3"], y["k"]):
                    print(f"  MAT {p} {x['name']}: c1 {x['c1']}->{y['c1']} c2 {x['c2']}->{y['c2']}")
            if len(base[p]) != len(oth[p]):
                print("  BRLYT size changed", p, len(base[p]), len(oth[p]))
        else:
            print("  ALTRO", p, len(base[p]), len(oth[p]))

import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import u8, brlyt

arc = sys.argv[1]
for path, d, c in u8.parse(open(arc, "rb").read()):
    if d:
        continue
    if not path.endswith(".brlyt"):
        print("   file", path, len(c))
        continue
    tex, mats, panes = brlyt.parse(c)
    print("==", path)
    for i, m in enumerate(mats):
        print(f"  M{i:<3} {m['name']:20s} c1={m['c1']} c2={m['c2']} c3={m['c3']} k={m['k'][0]} tex={m['tex']}")
    for p in panes:
        extra = ""
        if "vc" in p:
            extra = f"mat={mats[p['mat']]['name']} vc={p['vc']}"
        if "top" in p:
            extra = f"mat={mats[p['mat']]['name']} top={p['top']} bot={p['bot']}"
        print(f"  {p['kind']} {p['name']:16s} a={p['alpha']} size={tuple(round(v) for v in p['size'])} {extra}")

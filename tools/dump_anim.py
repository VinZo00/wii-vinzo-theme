"""Mostra tutte le animazioni (tag, target, chiavi) di un brlan in un archivio."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import u8
from find_anim_colors import parse_brlan

arc, name = sys.argv[1], sys.argv[2]
filt = sys.argv[3].split(",") if len(sys.argv) > 3 else None
for path, d, c in u8.parse(open(arc, "rb").read()):
    if d or not path.endswith(name):
        continue
    print("==", path)
    for pane, tag, idx, target, keys in parse_brlan(c):
        if filt and not pane.startswith(tuple(filt)):
            continue
        ks = [(round(k[0]), round(k[1], 2)) for k in keys][:6]
        print(f"  {pane:16s} {tag} idx={idx} t={target:2d} {ks}{' ...' if len(keys) > 6 else ''}")

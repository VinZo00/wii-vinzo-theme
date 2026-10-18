"""Verifica strutturale del csm rispetto al base app."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
import u8, lz77, tpl, brlyt
from find_anim_colors import parse_brlan

base_app, csm_path, out_dir = sys.argv[1:4]
base = u8.parse(open(base_app, "rb").read())
csm = u8.parse(open(csm_path, "rb").read())
errors = []
assert [(p, d) for p, d, _ in base] == [(p, d) for p, d, _ in csm], "struttura base diversa"
changed = 0
for (p, d, a), (_, _, b) in zip(base, csm):
    if d or a == b:
        continue
    changed += 1
    if b[:4] != b"LZ77":
        errors.append(f"{p}: modificato ma non LZ77"); continue
    arc = lz77.decompress(b)
    from subprocess import run
    orig_arc = None
    ents = u8.parse(arc)
    n_tpl = n_lyt = n_lan = 0
    for q, dd, c in ents:
        if dd:
            continue
        try:
            if q.endswith(".tpl"):
                for im in tpl.images(c):
                    img = tpl.decode(c, im)
                    assert im["offset"] + im["size"] <= len(c)
                n_tpl += 1
                if "BackPic" in q:
                    Image.fromarray(img, "RGBA").save(os.path.join(out_dir, "verifica_BackPic.png"))
            elif q.endswith(".brlyt"):
                brlyt.parse(c); n_lyt += 1
            elif q.endswith(".brlan"):
                parse_brlan(c); n_lan += 1
        except Exception as e:
            errors.append(f"{p}:{q}: {e!r}")
    print(f"{p}: {len(arc)} byte, {n_tpl} tpl, {n_lyt} brlyt, {n_lan} brlan OK")
print("file modificati:", changed)
print("ERRORI:" if errors else "Nessun errore", *errors, sep="\n")

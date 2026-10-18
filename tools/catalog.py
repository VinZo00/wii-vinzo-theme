"""Cataloga le texture di tutti gli archivi .arc decompressi e salva le anteprime PNG."""
import os, sys, collections
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image
import u8, tpl

arc_dir, png_dir = sys.argv[1], sys.argv[2]
stats = collections.Counter()
rows = []
for fn in sorted(os.listdir(arc_dir)):
    if not fn.endswith(".arc"):
        continue
    arc = fn[:-4]
    for path, is_dir, content in u8.parse(open(os.path.join(arc_dir, fn), "rb").read()):
        if is_dir or not path.endswith(".tpl"):
            continue
        for k, im in enumerate(tpl.images(content)):
            name = tpl.FMT.get(im["fmt"], im["fmt"])
            stats[name] += 1
            try:
                img = tpl.decode(content, im)
            except NotImplementedError:
                rows.append(f"{arc}\t{path}\t{im['w']}x{im['h']}\t{name}\tNON SUPPORTATO")
                continue
            ok = ""
            if im["fmt"] != 14:
                ok = "rt" if tpl.encode(img, im["fmt"]) == content[im["offset"]:im["offset"] + im["size"]] else "RT-DIFF"
            else:
                again = tpl.decode(tpl.replace(content, im, img), im)
                ok = "cmpr-err=%.1f" % np.abs(again.astype(int) - img.astype(int)).mean()
            out = os.path.join(png_dir, arc, path.replace("/", "__") + (f"_{k}" if k else "") + ".png")
            os.makedirs(os.path.dirname(out), exist_ok=True)
            Image.fromarray(img, "RGBA").save(out)
            rows.append(f"{arc}\t{path}\t{im['w']}x{im['h']}\t{name}\t{ok}")
open(os.path.join(png_dir, "catalog.tsv"), "w").write("\n".join(rows))
print(stats)
print(len(rows), "texture")
print("\n".join(r for r in rows if "DIFF" in r or "NON" in r))

"""Estrae gli archivi modificati di un csm (LZ77) in .arc e PNG delle texture cambiate."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
from PIL import Image
import u8, lz77, tpl

csm, base_arc_dir, out_arc, out_png = sys.argv[1:5]
os.makedirs(out_arc, exist_ok=True)
for p, d, c in u8.parse(open(csm, "rb").read()):
    if d or not p.endswith(".ash") or c[:4] != b"LZ77":
        continue
    name = ("eng_" if "/eng/" in p else "") + os.path.basename(p)
    arc = lz77.decompress(c)
    open(os.path.join(out_arc, name + ".arc"), "wb").write(arc)
    base = {q: x for q, dd, x in u8.parse(open(os.path.join(base_arc_dir, name + ".arc"), "rb").read()) if not dd}
    for q, dd, x in u8.parse(arc):
        if dd or not q.endswith(".tpl") or base.get(q) == x:
            continue
        im = tpl.images(x)[0]
        try:
            img = tpl.decode(x, im)
        except NotImplementedError:
            continue
        dst = os.path.join(out_png, name, q.replace("/", "__") + ".png")
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        Image.fromarray(img, "RGBA").save(dst)
print("ok")

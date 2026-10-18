"""Simulazione approssimata del menu principale (geometria misurata dalle foto della TV)."""
import sys
from PIL import Image, ImageDraw

bg_path, out = sys.argv[1], sys.argv[2]
SW, SH = 1400, 788
bg = Image.open(bg_path).convert("RGB")
pane_w, pane_h = 1260, 540
x0 = 127
bgs = bg.resize((pane_w, pane_h), Image.LANCZOS)
scr = Image.new("RGB", (SW, SH), (10, 8, 14))
for k in (-1, 0, 1):
    scr.paste(bgs, (x0 + k * pane_w, 0))
d = ImageDraw.Draw(scr, "RGBA")
cols = [(120, 395), (410, 685), (700, 975), (990, 1265)]
rows = [(55, 200), (215, 360), (375, 520)]
for (a, b) in cols:
    for (c, e) in rows:
        d.rounded_rectangle((a, c, b, e), 18, fill=(225, 225, 230, 255), outline=(224, 64, 251, 255), width=3)
for (c, e) in rows:  # slot della pagina successiva a destra
    d.rounded_rectangle((1290, c, 1565, e), 18, fill=(20, 15, 26, 255), outline=(224, 64, 251, 255), width=3)
d.rectangle((0, 545, SW, SH), fill=(28, 21, 36, 255))
d.line((0, 545, SW, 545), fill=(224, 64, 251, 255), width=4)
scr.save(out)

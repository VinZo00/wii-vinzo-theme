"""Foglio affiancato: per ogni texture, base | riferimento (etichetta sopra)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont

base_dir, ref_dir, out = sys.argv[1:4]
font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 13)
CELL = 140
files = sorted(os.listdir(ref_dir)) if os.path.isdir(ref_dir) else sorted(os.listdir(base_dir))
cols = 3
rows = (len(files) + cols - 1) // cols
W = cols * (2 * CELL + 30)
sheet = Image.new("RGB", (W, rows * (CELL + 24)), (70, 70, 70))
dr = ImageDraw.Draw(sheet)


def tile(path):
    im = Image.open(path).convert("RGBA")
    im.thumbnail((CELL - 4, CELL - 4))
    bg = Image.new("RGBA", im.size, (40, 40, 40, 255))
    d = ImageDraw.Draw(bg)
    for y in range(0, im.size[1], 6):
        for x in range(0, im.size[0], 6):
            if (x // 6 + y // 6) % 2:
                d.rectangle((x, y, x + 5, y + 5), fill=(110, 40, 110, 255))
    bg.alpha_composite(im)
    return bg.convert("RGB")


for i, f in enumerate(files):
    x = (i % cols) * (2 * CELL + 30)
    y = (i // cols) * (CELL + 24)
    dr.text((x + 4, y + 2), f.replace("arc__timg__", "").replace(".tpl.png", ""), font=font, fill=(255, 255, 160))
    for j, d in enumerate((base_dir, ref_dir)):
        p = os.path.join(d, f)
        if os.path.exists(p):
            sheet.paste(tile(p), (x + 4 + j * (CELL + 4), y + 20))
sheet.save(out)
print("ok")

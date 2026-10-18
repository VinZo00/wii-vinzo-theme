"""Crea un foglio di anteprima per ogni archivio (texture su scacchiera con nome)."""
import os, sys
from PIL import Image, ImageDraw, ImageFont

png_dir, out_dir = sys.argv[1], sys.argv[2]
only = sys.argv[3:] or None
os.makedirs(out_dir, exist_ok=True)
font = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 11)
CELL = 150
for arc in sorted(os.listdir(png_dir)):
    d = os.path.join(png_dir, arc)
    if not os.path.isdir(d) or (only and arc not in only):
        continue
    files = sorted(os.listdir(d))
    cols = 8
    rows = (len(files) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * CELL, rows * (CELL + 28)), (60, 60, 60))
    dr = ImageDraw.Draw(sheet)
    for i, f in enumerate(files):
        im = Image.open(os.path.join(d, f)).convert("RGBA")
        full = im.size
        im.thumbnail((CELL - 6, CELL - 6))
        x, y = (i % cols) * CELL, (i // cols) * (CELL + 28)
        chk = Image.new("RGBA", im.size, (0, 0, 0, 255))
        cd = ImageDraw.Draw(chk)
        for yy in range(0, im.size[1], 8):
            for xx in range(0, im.size[0], 8):
                if (xx // 8 + yy // 8) % 2:
                    cd.rectangle((xx, yy, xx + 7, yy + 7), fill=(255, 0, 255, 255))
        chk.alpha_composite(im)
        sheet.paste(chk.convert("RGB"), (x + 3, y + 3))
        label = f.replace("arc__timg__", "").replace(".tpl.png", "")
        dr.text((x + 3, y + CELL), label[:24], font=font, fill=(255, 255, 255))
        dr.text((x + 3, y + CELL + 13), f"{full[0]}x{full[1]}", font=font, fill=(180, 180, 180))
    sheet.save(os.path.join(out_dir, arc.replace(".ash", "") + ".png"))
print("ok")

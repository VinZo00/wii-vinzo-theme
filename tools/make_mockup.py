"""Anteprima concettuale di un tema Material Dark per il menu Wii (16:9)."""
import sys
from PIL import Image, ImageDraw, ImageFilter, ImageFont

BG_PATH, OUT_PATH = sys.argv[1], sys.argv[2]
W, H = 1280, 720
ACCENT = (224, 64, 251)       # Material Purple A200, preso dallo sfondo
CARD = (30, 22, 34, 215)
CARD_EMPTY = (255, 255, 255, 18)
TEXT = (240, 240, 245)
MUTED = (170, 160, 180)
F = "C:/Windows/Fonts/"
font = lambda name, size: ImageFont.truetype(F + name, size)

# Sfondo: wallpaper ritagliato a 16:9 e leggermente sfocato
bg = Image.open(BG_PATH).convert("RGB")
bw, bh = bg.size
crop_h = int(bw * H / W)
top = max(0, (bh - crop_h) // 2)
bg = bg.crop((0, top, bw, top + min(crop_h, bh))).resize((W, H), Image.LANCZOS)
bg = bg.filter(ImageFilter.GaussianBlur(2)).convert("RGBA")

layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
d = ImageDraw.Draw(layer)
shadow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
sd = ImageDraw.Draw(shadow)

# Griglia canali 4x3
cols, rows = 4, 3
mx, my, gap = 120, 70, 22
cw = (W - 2 * mx - gap * (cols - 1)) // cols
ch = 128
channels = {
    0: ("Disco", "disc"), 1: ("Mii", "mii"), 2: ("Foto", "photo"),
    3: ("Wii Shop", "shop"), 4: ("Homebrew", "hbc"), 5: ("USB Loader GX", "gx"),
    6: ("Nintendont", "gc"),
}
for i in range(cols * rows):
    r, c = divmod(i, cols)
    x = mx + c * (cw + gap)
    y = my + r * (ch + gap)
    box = (x, y, x + cw, y + ch)
    if i in channels:
        sd.rounded_rectangle((x + 2, y + 6, x + cw + 2, y + ch + 8), 18, fill=(0, 0, 0, 140))
        d.rounded_rectangle(box, 18, fill=CARD)
        d.rounded_rectangle((x, y, x + cw, y + 5), 3, fill=ACCENT + (255,))
        cx, cy = x + cw // 2, y + ch // 2 - 10
        name, kind = channels[i]
        if kind == "disc":
            d.ellipse((cx - 28, cy - 28, cx + 28, cy + 28), outline=TEXT, width=4)
            d.ellipse((cx - 7, cy - 7, cx + 7, cy + 7), outline=TEXT, width=3)
        elif kind == "mii":
            d.ellipse((cx - 14, cy - 30, cx + 14, cy - 2), fill=TEXT)
            d.pieslice((cx - 28, cy + 2, cx + 28, cy + 50), 180, 360, fill=TEXT)
        elif kind == "photo":
            d.rounded_rectangle((cx - 32, cy - 22, cx + 32, cy + 24), 6, outline=TEXT, width=4)
            d.polygon([(cx - 24, cy + 16), (cx - 6, cy - 6), (cx + 8, cy + 10), (cx + 16, cy + 2), (cx + 26, cy + 16)], fill=ACCENT)
        elif kind == "shop":
            d.rounded_rectangle((cx - 26, cy - 12, cx + 26, cy + 26), 5, fill=TEXT)
            d.arc((cx - 14, cy - 30, cx + 14, cy - 2), 180, 360, fill=TEXT, width=4)
        elif kind == "hbc":
            d.rounded_rectangle((cx - 30, cy - 22, cx + 30, cy + 24), 10, outline=ACCENT, width=4)
            d.text((cx, cy + 1), "HBC", font=font("segoeuib.ttf", 20), fill=TEXT, anchor="mm")
        elif kind == "gx":
            d.text((cx, cy), "GX", font=font("segoeuib.ttf", 40), fill=ACCENT, anchor="mm")
        elif kind == "gc":
            d.rounded_rectangle((cx - 26, cy - 26, cx + 26, cy + 26), 12, outline=TEXT, width=4)
            d.rounded_rectangle((cx - 10, cy - 10, cx + 10, cy + 10), 4, fill=ACCENT)
        d.text((cx, y + ch - 20), name, font=font("seguisb.ttf", 15), fill=MUTED, anchor="mm")
    else:
        d.rounded_rectangle(box, 18, fill=CARD_EMPTY, outline=(255, 255, 255, 30), width=1)

# Frecce pagina
for side in (-1, 1):
    cx = W // 2 + side * (W // 2 - 55)
    cy = my + (rows * (ch + gap)) // 2 - 10
    d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), fill=(30, 22, 34, 200))
    d.line([(cx - 4 * side, cy - 9), (cx + 5 * side, cy), (cx - 4 * side, cy + 9)], fill=TEXT, width=4, joint="curve")

# Barra inferiore
bar_top = H - 150
sd.rectangle((0, bar_top - 8, W, H), fill=(0, 0, 0, 120))
d.rectangle((0, bar_top, W, H), fill=(18, 14, 22, 235))
d.rectangle((0, bar_top, W, bar_top + 3), fill=ACCENT + (255,))
# Pulsante Wii
d.ellipse((50, bar_top + 30, 140, bar_top + 120), fill=(36, 28, 42, 255), outline=ACCENT, width=3)
d.text((95, bar_top + 75), "Wii", font=font("segoeuib.ttf", 26), fill=TEXT, anchor="mm")
# Pulsante bacheca
d.ellipse((W - 140, bar_top + 30, W - 50, bar_top + 120), fill=(36, 28, 42, 255), outline=ACCENT, width=3)
ex, ey = W - 95, bar_top + 75
d.rounded_rectangle((ex - 22, ey - 15, ex + 22, ey + 15), 3, outline=TEXT, width=3)
d.line([(ex - 20, ey - 12), (ex, ey + 3), (ex + 20, ey - 12)], fill=TEXT, width=3)
# Orologio e data
d.text((W // 2, bar_top + 62), "21:47", font=font("segoeuil.ttf", 58), fill=TEXT, anchor="mm")
d.text((W // 2, bar_top + 112), "dom 18/10", font=font("segoeui.ttf", 20), fill=MUTED, anchor="mm")
# Firma
sig_font = font("segoeui.ttf", 15)
sig_bold = font("segoeuib.ttf", 15)
sx, sy = 168, H - 26
d.text((sx, sy), "Mod by ", font=sig_font, fill=MUTED + (200,), anchor="lm")
d.text((sx + d.textlength("Mod by ", font=sig_font), sy), "VinZo", font=sig_bold, fill=ACCENT + (255,), anchor="lm")

shadow = shadow.filter(ImageFilter.GaussianBlur(8))
out = Image.alpha_composite(Image.alpha_composite(bg, shadow), layer)

# Cursore (mano stilizzata)
cd = ImageDraw.Draw(out)
px, py = 760, 300
cd.polygon([(px, py), (px + 30, py + 26), (px + 14, py + 28), (px + 22, py + 46), (px + 14, py + 50), (px + 6, py + 32), (px - 4, py + 42)],
           fill=(255, 255, 255, 255), outline=(40, 10, 50, 255))

out.convert("RGB").save(OUT_PATH, quality=92)
print("ok", OUT_PATH)

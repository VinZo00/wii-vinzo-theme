"""Genera il tema "vinzo" per USB Loader GX partendo dal tema PREDEFINITO del loader.

Base: immagini in data/images del sorgente ufficiale (github.com/wiidev/usbloadergx, GPLv3) e il
modello completo delle chiavi Default.them.
- pulsanti principali (Wii, impostazioni, HBC, SD, spegni, +) ridisegnati come nel menu Wii
- altre immagini: azzurri -> viola; pannelli chiari -> scuri; testi/contorni scuri -> chiari;
  loghi ufficiali, controller, copertine di default e logo GX restano come sono
- sfondi e anteprime: dall'immagine della barra del tema del menu (assets/barra.jpg)
- .them: il msgid è la CHIAVE cercata dal loader e non va mai cambiato; i colori vanno nel msgstr
Uso: python gx_theme.py <Default.them> <cartella_immagini> <barra.jpg> <cartella_uscita>
"""
import math, os, re, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFont

THEM, IMG_DIR, BAR_IMAGE, OUT = sys.argv[1:5]
NAME = "vinzo"
F = "C:/Windows/Fonts/"

ACCENT = (224, 64, 251)
ACCENT_DARK = (150, 40, 170)
ACCENT_HUE = 292 / 360.0
CARD = (36, 28, 42)
CARD_HOVER = (58, 44, 70)
CARD_LIGHT = (70, 58, 80)
WHITE = (240, 240, 245)
MUTED = (200, 190, 210)

# Non si toccano: loghi di classificazione, controller, copertine/dischi di default, logo GX
KEEP = re.compile(r"^(esrb_|pegi_|cero_|norating|wiimote\d?\.|Wiimote\d|nunchuk|classiccontroller|gcncontroller|"
                  r"balanceboard|guitar|drums|dancepad|microphone|motionplus|wheel|zapper|nintendods|wiispeak|"
                  r"nocover|nodisc|gxlogo)", re.I)
# Sostituiti con l'immagine della barra
BACKGROUNDS = {"background.png": ("4:3", (640, 480)), "wbackground.png": ("16:9", (640, 480)),
               "credits_bg.png": ("4:3", (640, 480)), "theme_preview_480p.png": ("16:9", (640, 480)),
               "theme_preview.png": ("square", (250, 250))}
CURSORS = re.compile(r"^r?player\d_(point|grab)", re.I)
ALWAYS_PANEL = re.compile(r"^(keyboard_|tooltip_)", re.I)  # piccoli ma con testo sopra: vanno scuriti


# ---------- pulsanti disegnati (stile menu Wii VinZo, più piccoli dei cerchi pieni di azurenight) ----------

SS = 4


def round_button(size, icon, hover, diameter=0.72):
    w, h = size
    im = Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    r = min(w, h) * diameter / 2 * SS
    cx, cy = w * SS / 2, h * SS / 2
    ring = (3.5 if hover else 2.5) * SS
    d.ellipse((cx - r, cy - r, cx + r, cy + r), fill=ACCENT + (255,))
    d.ellipse((cx - r + ring, cy - r + ring, cx + r - ring, cy + r - ring), fill=(CARD_HOVER if hover else CARD) + (255,))
    icon(d, cx, cy, r * 0.55)
    return im.resize((w, h), Image.LANCZOS)


def i_text(txt, scale=1.0):
    def f(d, cx, cy, s):
        font = ImageFont.truetype(F + "segoeuib.ttf", int(s * 1.05 * scale))
        d.text((cx, cy + s * 0.05), txt, font=font, fill=WHITE + (255,), anchor="mm")
    return f


def i_gear(d, cx, cy, s):
    teeth = 8
    for k in range(teeth):
        a = 2 * math.pi * k / teeth
        x, y = cx + math.cos(a) * s * 0.85, cy + math.sin(a) * s * 0.85
        d.ellipse((x - s * 0.2, y - s * 0.2, x + s * 0.2, y + s * 0.2), fill=WHITE + (255,))
    d.ellipse((cx - s * 0.75, cy - s * 0.75, cx + s * 0.75, cy + s * 0.75), fill=WHITE + (255,))
    d.ellipse((cx - s * 0.32, cy - s * 0.32, cx + s * 0.32, cy + s * 0.32), fill=CARD + (255,))


def i_power(d, cx, cy, s):
    w = max(2, int(s * 0.2))
    d.arc((cx - s * 0.8, cy - s * 0.75, cx + s * 0.8, cy + s * 0.85), 300, 240, fill=WHITE + (255,), width=w)
    d.line((cx, cy - s * 0.95, cx, cy - s * 0.05), fill=WHITE + (255,), width=w)


def i_plus(d, cx, cy, s):
    t = s * 0.14
    d.rounded_rectangle((cx - s * 0.7, cy - t, cx + s * 0.7, cy + t), t, fill=WHITE + (255,))
    d.rounded_rectangle((cx - t, cy - s * 0.7, cx + t, cy + s * 0.7), t, fill=WHITE + (255,))


def i_sd(d, cx, cy, s):
    w, h = s * 1.1, s * 1.4
    x0, y0 = cx - w / 2, cy - h / 2
    d.polygon([(x0 + w * 0.3, y0), (x0 + w, y0), (x0 + w, y0 + h), (x0, y0 + h), (x0, y0 + w * 0.3)],
              fill=WHITE + (255,))
    font = ImageFont.truetype(F + "segoeuib.ttf", int(s * 0.5))
    d.text((cx, cy + h * 0.18), "SD", font=font, fill=CARD + (255,), anchor="mm")


BUTTONS = {
    "menu_button": i_text("Wii"), "settings_button": i_gear, "browser": i_text("H", 1.3),
    "sdcard": i_sd, "wiimote_poweroff": i_power, "button_install": i_plus,
}


def drawn_button(fn, size):
    base = fn[:-4]
    hover = base.endswith("_over")
    key = base[:-5] if hover else base
    if key not in BUTTONS:
        return None
    return round_button(size, BUTTONS[key], hover)


# ---------- ricolorazione ----------

def rgb_to_hsv(a):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    mx = a.max(-1); mn = a.min(-1); df = mx - mn
    h = np.zeros_like(mx)
    m = df > 1e-6
    rr = m & (mx == r); gg = m & (mx == g) & ~rr; bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / df[rr]) % 6
    h[gg] = (b - r)[gg] / df[gg] + 2
    h[bb] = (r - g)[bb] / df[bb] + 4
    h = h / 6.0
    s = np.where(mx > 1e-6, df / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def hsv_to_rgb(h, s, v):
    i = np.floor(h * 6).astype(int) % 6
    f = h * 6 - np.floor(h * 6)
    p = v * (1 - s); q = v * (1 - f * s); t = v * (1 - (1 - f) * s)
    out = np.zeros(h.shape + (3,), np.float32)
    for k, (a, b, c) in enumerate([(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]):
        m = i == k
        out[m] = np.stack([a[m], b[m], c[m]], -1)
    return out


LIGHT_ONLY = {"settings_background.png"}  # fondo nero con linguette bianche: scurire solo il chiaro


def recolor(img, darken, invert_dark=True):
    a = np.asarray(img.convert("RGBA"), dtype=np.float32) / 255.0
    rgb, alpha = a[..., :3], a[..., 3:]
    h, s, v = rgb_to_hsv(rgb)
    out = rgb.copy()
    blue = (h > 170 / 360) & (h < 250 / 360) & (s > 0.2)
    out[blue] = hsv_to_rgb(np.full(blue.sum(), ACCENT_HUE, np.float32), s[blue], v[blue])
    if darken:
        neutral = (s < 0.18) & ~blue
        light = neutral & (v > 0.55)
        t = ((1 - v[light]) / 0.45)[:, None]  # 0 = bianco, 1 = grigio medio
        out[light] = (np.array(CARD) / 255.0) * (1 - t) + (np.array(CARD_LIGHT) / 255.0) * t
        if invert_dark:
            dark = neutral & (v < 0.3)  # testi/contorni scuri sui pannelli chiari -> chiari
            out[dark] = np.array(WHITE) / 255.0 * (0.75 + v[dark][:, None])
    res = np.concatenate([np.clip(out, 0, 1), alpha], -1)
    return Image.fromarray((res * 255).astype(np.uint8), "RGBA")


def should_darken(fn, im):
    """Scurisce solo i pannelli chiari: grandi (o tasti/tooltip) e con media luminosa."""
    if CURSORS.match(fn):
        return False
    if max(im.size) < 96 and not ALWAYS_PANEL.match(fn):
        return False
    a = np.asarray(im.convert("RGBA"), dtype=np.float32) / 255.0
    opaque = a[..., 3] > 0.5
    if not opaque.any():
        return False
    lum = (a[..., :3] @ np.array([0.299, 0.587, 0.114], np.float32))[opaque]
    return float(lum.mean()) > 0.55


def background(kind, size):
    src = Image.open(BAR_IMAGE).convert("RGB")
    sw, sh = src.size
    if kind == "4:3":
        cw = int(sh * 4 / 3)
        src = src.crop(((sw - cw) // 2, 0, (sw - cw) // 2 + cw, sh))
    elif kind == "square":
        src = src.crop(((sw - sh) // 2, 0, (sw - sh) // 2 + sh, sh))
    return src.resize(size, Image.LANCZOS).convert("RGBA")


# ---------- .them ----------

def color_rule(desc, r, g, b, a):
    d = desc.lower()
    h, s, v = rgb_to_hsv(np.array([[r, g, b]], np.float32) / 255.0)
    h, s, v = float(h[0]), float(s[0]), float(v[0])
    if "edge tev color 1" in d:
        return ACCENT_DARK + (a,)
    if "edge tev color 2" in d:
        return ACCENT + (a,)
    if "frame color" in d:
        return CARD_LIGHT + (a,)
    if 170 / 360 < h < 250 / 360 and s > 0.2:
        return ACCENT + (a,)
    if s < 0.18 and ("text" in d or "clock" in d or d.endswith("info color") or "count color" in d):
        return WHITE + (a,)
    return (r, g, b, a)


def convert_them(text):
    """Il msgid resta identico (è la chiave); il colore convertito va sempre nel msgstr."""
    log = []

    def repl(m):
        r, g, b, a = (int(m.group(i)) for i in range(1, 5))
        desc = m.group(5)
        nc = color_rule(desc, r, g, b, a)
        log.append(f"{desc}: {(r, g, b, a)} -> {nc}")
        return m.group(0).split("\n")[0] + '\nmsgstr "r={} g={} b={} a={}"'.format(*nc)
    text = re.sub(r'msgid "r=(\d+) g=(\d+) b=(\d+) a=(\d+) - ([^"]*)"\r?\nmsgstr "[^"]*"', repl, text)
    for key, val in (("Theme-Title", "VinZo Material Dark"), ("Image-Folder", NAME),
                     ("Last-Themer", "VinZo"), ("Theme-Team", "VinZo"), ("Theme-Version", "2")):
        text = re.sub(rf'"{key}: [^"\\]*', f'"{key}: {val}', text)
    return text, log


def main():
    out_img = os.path.join(OUT, NAME)
    os.makedirs(out_img, exist_ok=True)
    counts = {"pulsante": 0, "sfondo": 0, "invariata": 0, "ricolorata": 0, "scurita": 0}
    for fn in sorted(os.listdir(IMG_DIR)):
        if not fn.lower().endswith(".png") or fn in BACKGROUNDS:
            continue
        im = Image.open(os.path.join(IMG_DIR, fn))
        btn = drawn_button(fn, im.size)
        if btn is not None:
            im = btn; counts["pulsante"] += 1
        elif KEEP.match(fn):
            counts["invariata"] += 1
        elif fn in LIGHT_ONLY:
            im = recolor(im, True, invert_dark=False); counts["scurita"] += 1
        else:
            darken = should_darken(fn, im)
            im = recolor(im, darken)
            counts["scurita" if darken else "ricolorata"] += 1
        im.save(os.path.join(out_img, fn))
    for fn, (kind, size) in BACKGROUNDS.items():
        background(kind, size).save(os.path.join(out_img, fn)); counts["sfondo"] += 1
    with open(THEM, encoding="utf-8", errors="surrogateescape") as f:
        t, log = convert_them(f.read())
    with open(os.path.join(OUT, NAME + ".them"), "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write(t)
    print("ok", counts, f"{len(log)} colori nel .them")
    print("\n".join(log))


main()

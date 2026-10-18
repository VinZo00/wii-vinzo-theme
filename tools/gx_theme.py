"""Genera il tema "vinzo" per USB Loader GX partendo da un tema esistente (azurenight).

- immagini: azzurri -> viola dell'accento; pannelli/pulsanti chiari -> scuri (stile VinZo);
  testi scuri sui pannelli -> chiari; loghi ufficiali, controller e copertine restano come sono
- sfondi: dall'immagine della barra del tema del menu (assets/barra.jpg)
- .them: colori convertiti con le stesse regole
Uso: python gx_theme.py <tema.them> <cartella_immagini> <barra.jpg> <cartella_uscita>
"""
import os, re, sys
import numpy as np
from PIL import Image

THEM, IMG_DIR, BAR_IMAGE, OUT = sys.argv[1:5]
NAME = "vinzo"

ACCENT = (224, 64, 251)
ACCENT_HUE = 292 / 360.0
CARD = (36, 28, 42)
CARD_LIGHT = (70, 58, 80)
WHITE = (240, 240, 245)

# Non si toccano: loghi di classificazione, controller, copertine/dischi di default, logo GX
KEEP = re.compile(r"^(esrb_|pegi_|cero_|norating|wiimote|Wiimote\d|nunchuk|classiccontroller|gcncontroller|"
                  r"balanceboard|guitar|drums|dancepad|microphone|motionplus|wheel|zapper|nintendods|wiispeak|"
                  r"nocover|nodisc|gxlogo)", re.I)
# Sostituiti con l'immagine della barra
BACKGROUNDS = {"background.png": "4:3", "wbackground.png": "16:9", "credits_bg.png": "4:3",
               "theme_preview_480p.png": "16:9", "theme_preview.png": "square"}


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


def recolor(img, darken):
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
        dark = neutral & (v < 0.3)  # testi/contorni scuri sui pannelli chiari -> chiari
        out[dark] = np.array(WHITE) / 255.0 * (0.75 + v[dark][:, None])
    res = np.concatenate([np.clip(out, 0, 1), alpha], -1)
    return Image.fromarray((res * 255).astype(np.uint8), "RGBA")


CURSORS = re.compile(r"^r?player\d_(point|grab)", re.I)
ALWAYS_PANEL = re.compile(r"^(keyboard_|tooltip_)", re.I)  # piccoli ma con testo sopra: vanno scuriti


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


def color_rule(desc, r, g, b, a):
    d = desc.lower()
    h, s, v = rgb_to_hsv(np.array([[r, g, b]], np.float32) / 255.0)
    h, s, v = float(h[0]), float(s[0]), float(v[0])
    if 170 / 360 < h < 250 / 360 and s > 0.2:
        return ACCENT + (a,)
    if "text" in d or "clock" in d or "color" == d.strip():
        if s < 0.18:
            return WHITE + (a,)
    if "frame color" in d and s < 0.18:
        return CARD_LIGHT + (a,)
    if "edge tev color 1" in d:
        return (150, 40, 170, a)
    if "edge tev color 2" in d:
        return ACCENT + (a,)
    return (r, g, b, a)


def convert_them(text):
    # Formato: msgid "<valore predefinito> - <descrizione>" / msgstr "<valore del tema>" (vuoto = predefinito).
    # Si convertono entrambi, usando la descrizione del msgid anche per il msgstr che lo segue.
    def repl(m):
        r, g, b, a = (int(m.group(i)) for i in range(1, 5))
        desc = m.group(5)
        nr, ng, nb, na = color_rule(desc, r, g, b, a)
        out = f'msgid "r={nr} g={ng} b={nb} a={na} - {desc}"\nmsgstr "'
        if m.group(6):
            sr, sg, sb, sa = (int(x) for x in re.findall(r"\d+", m.group(6)))
            out += "r={} g={} b={} a={}".format(*color_rule(desc, sr, sg, sb, sa))
        return out + '"'
    text = re.sub(r'msgid "r=(\d+) g=(\d+) b=(\d+) a=(\d+) - ([^"]*)"\r?\nmsgstr "(r=\d+ g=\d+ b=\d+ a=\d+)?"',
                  repl, text)
    text = re.sub(r'"Theme-Title: [^"\\]*', '"Theme-Title: VinZo Material Dark', text)
    text = re.sub(r'"Image-Folder: [^"\\]*', f'"Image-Folder: {NAME}', text)
    text = re.sub(r'"Last-Themer: [^"\\]*', '"Last-Themer: VinZo', text)
    return text


def main():
    out_img = os.path.join(OUT, NAME)
    os.makedirs(out_img, exist_ok=True)
    counts = {"sfondo": 0, "invariata": 0, "ricolorata": 0, "scurita": 0, "altro": 0}
    for fn in sorted(os.listdir(IMG_DIR)):
        src = os.path.join(IMG_DIR, fn)
        dst = os.path.join(out_img, fn)
        if not fn.lower().endswith(".png"):
            if fn.lower().endswith(".them"):
                with open(src, encoding="utf-8", errors="surrogateescape") as f:
                    t = convert_them(f.read())
                with open(dst, "w", encoding="utf-8", errors="surrogateescape") as f:
                    f.write(t)
            else:
                with open(src, "rb") as f, open(dst, "wb") as g:
                    g.write(f.read())
            counts["altro"] += 1
            continue
        im = Image.open(src)
        if fn in BACKGROUNDS:
            im = background(BACKGROUNDS[fn], im.size); counts["sfondo"] += 1
        elif KEEP.match(fn):
            counts["invariata"] += 1
        else:
            darken = should_darken(fn, im)
            im = recolor(im, darken)
            counts["scurita" if darken else "ricolorata"] += 1
        im.save(dst)
    with open(THEM, encoding="utf-8", errors="surrogateescape") as f:
        t = convert_them(f.read())
    with open(os.path.join(OUT, NAME + ".them"), "w", encoding="utf-8", errors="surrogateescape") as f:
        f.write(t)
    print("ok", counts)


main()

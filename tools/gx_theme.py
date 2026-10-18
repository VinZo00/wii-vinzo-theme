"""Genera il tema "vinzo" per USB Loader GX: tema PREDEFINITO del loader + colori e sfondi VinZo.

Base: immagini data/images e chiavi .them del sorgente della STESSA versione installata
(USB Loader GX 4.0 r1283, github.com/wiidev/usbloadergx, GPLv3).
- Disposizione, pannelli e pulsanti restano quelli predefiniti. I pannelli restano CHIARI perché
  molti testi del loader hanno il nero scritto nel codice (es. pulsanti di Impostazioni, gameinfo):
  su un pannello scuro sarebbero illeggibili.
- Colori: tutti gli azzurri delle immagini -> viola dell'accento (stessa saturazione e luminosità).
- Sfondi: lo sfondo predefinito (foglio a righe + barra curva in basso) ricolorato come il tema del
  menu Wii: foglio viola scurissimo, barra scura con le onde di assets/barra.jpg, linea viola.
- .them: il msgid è la CHIAVE (non va mai cambiato), i valori vanno nel msgstr.
Uso: python gx_theme.py <Default_r1283.them> <cartella_immagini> <barra.jpg> <cartella_uscita>
"""
import os, re, sys
import numpy as np
from PIL import Image

THEM, IMG_DIR, BAR_IMAGE, OUT = sys.argv[1:5]
NAME = "vinzo"

ACCENT = (224, 64, 251)
ACCENT_HUE = 292 / 360.0
FLAT_BG = (16, 12, 22)
BAR = (28, 21, 36)
WHITE = (240, 240, 245)

# Non si toccano: loghi di classificazione, controller, copertine/dischi di default, logo GX
KEEP = re.compile(r"^(esrb_|pegi_|cero_|norating|wiimote\d?\.|Wiimote\d|nunchuk|classiccontroller|gcncontroller|"
                  r"balanceboard|guitar|drums|dancepad|microphone|motionplus|wheel|zapper|nintendods|wiispeak|"
                  r"nocover|nodisc|gxlogo)", re.I)
BACKGROUNDS = ("background.png", "wbackground.png")


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


def blue_mask(h, s):
    return (h > 170 / 360) & (h < 250 / 360) & (s > 0.2)


def recolor(img):
    """Solo gli azzurri diventano viola; il resto dell'immagine resta identico."""
    a = np.asarray(img.convert("RGBA"), dtype=np.float32) / 255.0
    rgb, alpha = a[..., :3], a[..., 3:]
    h, s, v = rgb_to_hsv(rgb)
    out = rgb.copy()
    m = blue_mask(h, s)
    out[m] = hsv_to_rgb(np.full(m.sum(), ACCENT_HUE, np.float32), s[m], v[m])
    res = np.concatenate([np.clip(out, 0, 1), alpha], -1)
    return Image.fromarray((res * 255).astype(np.uint8), "RGBA")


def themed_background(img, waves):
    """Sfondo predefinito ricolorato: foglio -> FLAT_BG (righe tenui), barra -> BAR + onde, linea -> viola."""
    a = np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0
    h, s, v = rgb_to_hsv(a)
    line = blue_mask(h, s)
    lum = a @ np.array([0.299, 0.587, 0.114], np.float32)
    H, W = lum.shape
    # Foglio in alto: le righe hanno luminosità ~0.92-0.95; la barra in basso è più scura (~0.75-0.85)
    sheet = (lum > 0.885) & ~line
    # tutto ciò che sta sotto la linea della barra, colonna per colonna, è barra
    below = np.zeros_like(sheet)
    for x in range(W):
        ys = np.where(line[:, x])[0]
        if len(ys):
            below[ys.max() + 1:, x] = True
    sheet &= ~below
    bar = ~sheet & ~line
    out = np.zeros_like(a)
    # foglio: tinta piatta con le righe originali appena percettibili
    out[sheet] = np.array(FLAT_BG) / 255.0 + (lum[sheet, None] - 0.93) * 0.25
    # barra: colore scuro con i rilievi originali (pillole, ombre) mantenuti come variazioni leggere
    rel = (lum[bar] - 0.80)[:, None]
    out[bar] = np.array(BAR) / 255.0 + rel * 0.35
    # onde viola (immagine della barra del tema) schiarite sopra la barra
    wv = np.asarray(waves.convert("RGB").resize((W, H), Image.LANCZOS), dtype=np.float32) / 255.0
    out[bar] = 1 - (1 - out[bar]) * (1 - wv[bar])  # fusione "screen"
    out[line] = hsv_to_rgb(np.full(line.sum(), ACCENT_HUE, np.float32), s[line], v[line])
    return Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8), "RGB").convert("RGBA")


def preview(bg, size):
    w, h = size
    return bg.convert("RGB").resize(size, Image.LANCZOS).convert("RGBA") if w / h != 1 else \
        bg.convert("RGB").crop(((bg.width - bg.height) // 2, 0, (bg.width + bg.height) // 2, bg.height)).resize(size).convert("RGBA")


def color_rule(desc, r, g, b, a):
    d = desc.lower()
    h, s, v = rgb_to_hsv(np.array([[r, g, b]], np.float32) / 255.0)
    if blue_mask(h, s)[0]:
        return ACCENT + (a,)
    if "clock" in d:  # l'orologio è disegnato sul foglio scuro
        return WHITE + (a,)
    return None  # resta il valore predefinito


def convert_them(text):
    """Il msgid resta identico (è la chiave); solo i colori cambiati vanno nel msgstr."""
    log = []

    def repl(m):
        r, g, b, a = (int(m.group(i)) for i in range(1, 5))
        desc = m.group(5)
        nc = color_rule(desc, r, g, b, a)
        if nc is None:
            return m.group(0)
        log.append(f"{desc}: {(r, g, b, a)} -> {nc}")
        return m.group(0).split("\n")[0] + '\nmsgstr "r={} g={} b={} a={}"'.format(*nc)
    text = re.sub(r'msgid "r=(\d+) g=(\d+) b=(\d+) a=(\d+) - ([^"]*)"\r?\nmsgstr "[^"]*"', repl, text)
    for key, val in (("Theme-Title", "VinZo Material Dark"), ("Image-Folder", NAME),
                     ("Last-Themer", "VinZo"), ("Theme-Team", "VinZo"), ("Theme-Version", "3")):
        text = re.sub(rf'"{key}: [^"\\]*', f'"{key}: {val}', text)
    return text, log


def main():
    out_img = os.path.join(OUT, NAME)
    os.makedirs(out_img, exist_ok=True)
    waves = Image.open(BAR_IMAGE)
    counts = {"sfondo": 0, "invariata": 0, "ricolorata": 0}
    for fn in sorted(os.listdir(IMG_DIR)):
        if not fn.lower().endswith(".png"):
            continue
        im = Image.open(os.path.join(IMG_DIR, fn))
        if fn in BACKGROUNDS:
            im = themed_background(im, waves); counts["sfondo"] += 1
        elif KEEP.match(fn):
            counts["invariata"] += 1
            continue  # identica al predefinito: non serve copiarla
        else:
            im = recolor(im); counts["ricolorata"] += 1
        im.save(os.path.join(out_img, fn))
    wide = Image.open(os.path.join(out_img, "wbackground.png"))
    preview(wide, (640, 480)).save(os.path.join(out_img, "theme_preview_480p.png"))
    preview(wide, (250, 250)).save(os.path.join(out_img, "theme_preview.png"))
    with open(THEM, encoding="utf-8", errors="surrogateescape") as f:
        t, log = convert_them(f.read())
    with open(os.path.join(OUT, NAME + ".them"), "w", encoding="utf-8", errors="surrogateescape", newline="\n") as f:
        f.write(t)
    print("ok", counts, f"{len(log)} colori nel .them")
    print("\n".join(log))


main()

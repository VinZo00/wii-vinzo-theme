"""Genera il tema "VinZo" per l'Homebrew Channel (theme.zip + app per installarlo).

Tutte le immagini sono disegnate qui, nello stile del tema del menu Wii (vedi palette in
build_vinzo.py). Dimensioni dei file: quelle del tema HBC "Material Dark" v1.4.
Uso: python hbc_theme.py <barra.jpg> <font_regular.ttf> <font_medium.ttf> <cartella_uscita>
"""
import io, math, os, sys, zipfile
from PIL import Image, ImageDraw, ImageFont

BAR_IMAGE, FONT_REG, FONT_MED, OUT = sys.argv[1:5]

ACCENT = (224, 64, 251)
ACCENT_LIGHT = (234, 128, 252)
BG = (16, 12, 22)
CARD = (36, 28, 42)
CARD_HOVER = (58, 44, 70)
WHITE = (240, 240, 245)
MUTED = (200, 190, 210)
RED = (255, 82, 82)
AMBER = (255, 179, 0)
F = "C:/Windows/Fonts/"
SS = 4  # supersampling


def canvas(w, h):
    return Image.new("RGBA", (w * SS, h * SS), (0, 0, 0, 0))


def done(img, w, h):
    return img.resize((w, h), Image.LANCZOS)


def card(w, h, fill, radius=8, outline=None, width=0, accent_bar=False):
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    s = SS
    d.rounded_rectangle((s, s, w * s - s - 1, h * s - s - 1), radius * s, fill=fill + (255,),
                        outline=(outline + (255,)) if outline else None, width=width * s)
    if accent_bar:
        d.rounded_rectangle((s, s, 6 * s, h * s - s - 1), 3 * s, fill=ACCENT + (255,))
    return done(im, w, h)


def pill(w, h, fill, outline=None, width=2):
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    s = SS
    r = (h - 4) * s / 2
    d.rounded_rectangle((2 * s, 2 * s, w * s - 2 * s - 1, h * s - 2 * s - 1), r, fill=fill + (255,),
                        outline=(outline + (255,)) if outline else None, width=width * s)
    return done(im, w, h)


def round_arrow(direction, hover):
    w = h = 64
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    s = SS
    c = 32 * s
    r = 24 * s
    d.ellipse((c - r, c - r, c + r, c + r), fill=(CARD_HOVER if hover else CARD) + (255,),
              outline=ACCENT + (255,), width=3 * s)
    k = 7 * s
    pts = [(c - k / 2 * direction, c - k), (c + k / 2 * direction, c), (c - k / 2 * direction, c + k)]
    d.line(pts, fill=WHITE + (255,), width=4 * s, joint="curve")
    return done(im, w, h)


def chevron(up):
    w, h = 32, 8
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    s = SS
    pts = [(10 * s, 6 * s), (16 * s, 2 * s), (22 * s, 6 * s)] if up else [(10 * s, 2 * s), (16 * s, 6 * s), (22 * s, 2 * s)]
    d.line(pts, fill=WHITE + (255,), width=2 * s, joint="curve")
    return done(im, w, h)


def dlg_icon(kind):
    w = h = 32
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    s = SS
    font = ImageFont.truetype(F + "segoeuib.ttf", 20 * s)
    if kind == "warning":
        d.polygon([(16 * s, 3 * s), (30 * s, 28 * s), (2 * s, 28 * s)], fill=AMBER + (255,))
        d.text((16 * s, 19 * s), "!", font=ImageFont.truetype(F + "segoeuib.ttf", 16 * s), fill=BG + (255,), anchor="mm")
    else:
        color, ch = {"confirm": (ACCENT, "?"), "error": (RED, "!"), "info": (ACCENT, "i")}[kind]
        d.ellipse((2 * s, 2 * s, 30 * s, 30 * s), fill=color + (255,))
        d.text((16 * s, 16 * s), ch, font=font, fill=WHITE + (255,), anchor="mm")
    return done(im, w, h)


def icon_network(active):
    w = h = 32
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    s = SS
    col = (WHITE if active else (110, 100, 120)) + (255,)
    cx, cy = 16 * s, 26 * s
    for r in (6, 13, 20):
        d.arc((cx - r * s, cy - r * s, cx + r * s, cy + r * s), 225, 315, fill=col, width=3 * s)
    d.ellipse((cx - 2 * s, cy - 2 * s, cx + 2 * s, cy + 2 * s), fill=col)
    return done(im, w, h)


def icon_usb(active):
    w = h = 32
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    s = SS
    col = (WHITE if active else (110, 100, 120)) + (255,)
    d.line((16 * s, 4 * s, 16 * s, 28 * s), fill=col, width=3 * s)
    d.polygon([(16 * s, 2 * s), (12 * s, 8 * s), (20 * s, 8 * s)], fill=col)
    d.line((16 * s, 20 * s, 9 * s, 14 * s, 9 * s, 11 * s), fill=col, width=2 * s)
    d.line((16 * s, 17 * s, 23 * s, 12 * s, 23 * s, 9 * s), fill=col, width=2 * s)
    d.ellipse((7 * s, 8 * s, 11 * s, 12 * s), fill=col)
    d.rectangle((21 * s, 6 * s, 25 * s, 10 * s), fill=col)
    d.ellipse((13 * s, 25 * s, 19 * s, 31 * s), fill=col)
    return done(im, w, h)


def throbber():
    w = h = 64
    im = canvas(w, h)
    d = ImageDraw.Draw(im)
    s = SS
    d.ellipse((6 * s, 6 * s, 58 * s, 58 * s), fill=CARD + (230,))
    d.arc((16 * s, 16 * s, 48 * s, 48 * s), 0, 280, fill=ACCENT + (255,), width=4 * s)
    return done(im, w, h)


def progress():
    w, h = 400, 112
    im = card(w, h, CARD, radius=10)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((20, 84, 380, 90), 3, fill=(70, 56, 82, 255))
    return im


def dialog_background():
    w, h = 520, 360
    im = card(w, h, CARD, radius=12)
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((12, 1, w - 13, 5), 2, fill=ACCENT + (255,))
    return im


def app_icon(bar):
    w, h = 128, 48
    src = bar.convert("RGB")
    sw, sh = src.size
    crop = src.crop((0, int(sh * 0.62), sw, sh)).resize((w, h), Image.LANCZOS).convert("RGBA")
    d = ImageDraw.Draw(crop)
    d.text((8, 24), "VinZo", font=ImageFont.truetype(F + "segoeuib.ttf", 20), fill=WHITE + (255,), anchor="lm")
    return crop


def backgrounds(bar):
    src = bar.convert("RGB")
    wide = src.resize((852, 480), Image.LANCZOS)
    sw, sh = src.size
    cw = int(sh * 4 / 3)
    normal = src.crop(((sw - cw) // 2, 0, (sw - cw) // 2 + cw, sh)).resize((640, 480), Image.LANCZOS)
    return normal, wide


THEME_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<theme version="1.0">
    <description>VinZo Material Dark</description>
    <font>
        <file>Roboto-Regular.ttf</file>
        <size>14</size>
        <color><red>{w[0]}</red><green>{w[1]}</green><blue>{w[2]}</blue><alpha>255</alpha></color>
    </font>
    <font target="button">
        <file>Roboto-Medium.ttf</file>
        <color><red>{w[0]}</red><green>{w[1]}</green><blue>{w[2]}</blue><alpha>255</alpha></color>
    </font>
    <font target="button_desel">
        <file>Roboto-Medium.ttf</file>
        <color><red>{m[0]}</red><green>{m[1]}</green><blue>{m[2]}</blue><alpha>160</alpha></color>
    </font>
    <font target="dlgtitle">
        <file>Roboto-Medium.ttf</file>
        <size>20</size>
        <color><red>{al[0]}</red><green>{al[1]}</green><blue>{al[2]}</blue><alpha>255</alpha></color>
    </font>
    <font target="appname">
        <file>Roboto-Medium.ttf</file>
        <size>18</size>
    </font>
    <font target="appdesc">
        <size>14</size>
        <color><red>{m[0]}</red><green>{m[1]}</green><blue>{m[2]}</blue><alpha>200</alpha></color>
    </font>
    <font_color>
        <red>{w[0]}</red><green>{w[1]}</green><blue>{w[2]}</blue><alpha>230</alpha>
    </font_color>
    <progress_gradient>
        <upper_left><red>{a[0]}</red><green>{a[1]}</green><blue>{a[2]}</blue><alpha>255</alpha></upper_left>
        <upper_right><red>{al[0]}</red><green>{al[1]}</green><blue>{al[2]}</blue><alpha>255</alpha></upper_right>
        <lower_left><red>{a[0]}</red><green>{a[1]}</green><blue>{a[2]}</blue><alpha>255</alpha></lower_left>
        <lower_right><red>{al[0]}</red><green>{al[1]}</green><blue>{al[2]}</blue><alpha>255</alpha></lower_right>
    </progress_gradient>
</theme>
""".format(w=WHITE, m=MUTED, a=ACCENT, al=ACCENT_LIGHT)

META_XML = """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<app version="1">
    <name>VinZo Theme (HBC)</name>
    <coder>VinZo</coder>
    <version>1.0</version>
    <short_description>Tema Material Dark viola - mod by VinZo</short_description>
    <long_description>Tema per l'Homebrew Channel coordinato con il tema del menu Wii "Material Dark - Mod by VinZo". Apri questa app dall'Homebrew Channel e conferma per installare il tema.</long_description>
</app>
"""


def main():
    bar = Image.open(BAR_IMAGE)
    normal, wide = backgrounds(bar)
    files = {
        "background.png": normal,
        "background_wide.png": wide,
        "apps_list.png": card(432, 64, CARD, radius=8),
        "apps_list_hover.png": card(432, 64, CARD_HOVER, radius=8, outline=ACCENT, width=2, accent_bar=True),
        "apps_grid.png": card(144, 64, CARD, radius=8),
        "apps_grid_hover.png": card(144, 64, CARD_HOVER, radius=8, outline=ACCENT, width=2),
        "apps_next.png": round_arrow(+1, False),
        "apps_next_hover.png": round_arrow(+1, True),
        "apps_previous.png": round_arrow(-1, False),
        "apps_previous_hover.png": round_arrow(-1, True),
        "button.png": pill(340, 48, CARD, ACCENT),
        "button_focus.png": pill(340, 48, ACCENT),
        "button_small.png": pill(200, 48, CARD, ACCENT),
        "button_small_focus.png": pill(200, 48, ACCENT),
        "button_tiny.png": pill(132, 48, CARD, ACCENT),
        "button_tiny_focus.png": pill(132, 48, ACCENT),
        "dialog_background.png": dialog_background(),
        "dlg_confirm.png": dlg_icon("confirm"),
        "dlg_error.png": dlg_icon("error"),
        "dlg_info.png": dlg_icon("info"),
        "dlg_warning.png": dlg_icon("warning"),
        "icon_network.png": icon_network(False),
        "icon_network_active.png": icon_network(True),
        "icon_usbgecko.png": icon_usb(False),
        "icon_usbgecko_active.png": icon_usb(True),
        "throbber.png": throbber(),
        "progress.png": progress(),
        "content_arrow_down.png": chevron(False),
        "content_arrow_up.png": chevron(True),
        "bubble1.png": Image.new("RGBA", (64, 64), (0, 0, 0, 0)),
        "bubble2.png": Image.new("RGBA", (64, 64), (0, 0, 0, 0)),
        "bubble3.png": Image.new("RGBA", (64, 64), (0, 0, 0, 0)),
        "icon.png": app_icon(bar),
    }
    app_dir = os.path.join(OUT, "apps", "HBCtheme_VinZo")
    prev_dir = os.path.join(OUT, "anteprima")
    os.makedirs(app_dir, exist_ok=True)
    os.makedirs(prev_dir, exist_ok=True)
    with zipfile.ZipFile(os.path.join(app_dir, "theme.zip"), "w", zipfile.ZIP_DEFLATED) as z:
        z.write(FONT_REG, "Roboto-Regular.ttf")
        z.write(FONT_MED, "Roboto-Medium.ttf")
        z.writestr("theme.xml", THEME_XML)
        for name, im in files.items():
            buf = io.BytesIO()
            im.save(buf, "PNG", optimize=True)
            z.writestr(name, buf.getvalue())
            im.save(os.path.join(prev_dir, name))
    files["icon.png"].save(os.path.join(app_dir, "icon.png"))
    with open(os.path.join(app_dir, "meta.xml"), "w", encoding="utf-8") as f:
        f.write(META_XML)
    print("ok", app_dir, len(files), "immagini")


main()

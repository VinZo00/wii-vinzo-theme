"""Costruisce il tema "Material Dark – Mod by VinZo" (.csm) dal base app 4.3E."""
import os, sys, struct
sys.path.insert(0, os.path.dirname(__file__))
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import u8, lz77, tpl, brlyt
from find_anim_colors import parse_brlan

BASE_APP, ARC_DIR, WALLPAPER, OUT_CSM, PREVIEW_DIR = sys.argv[1:6]

ACCENT = (224, 64, 251)
ACCENT_DARK = (150, 40, 170)
BAR = ((20, 15, 26), (28, 21, 36))      # c1/c2 della barra inferiore
SLOT = ((24, 19, 30), (46, 36, 56))     # slot vuoti (statico scuro)
CARD = (36, 28, 42)
WHITE = (240, 240, 245)
MUTED = (200, 190, 210)
F = "C:/Windows/Fonts/"

os.makedirs(PREVIEW_DIR, exist_ok=True)


# ---------- materiali BRLYT ----------

def set_color(buf, off, rgba):
    struct.pack_into(">4h", buf, off, *rgba)


def edit_materials(data, rules):
    """rules(name, c1, c2, c3) -> (c1, c2, c3) oppure None. Ritorna bytes modificati e log."""
    buf = bytearray(data)
    log = []
    _, mats, _ = brlyt.parse(data)
    for m in mats:
        res = rules(m["name"], m["c1"], m["c2"], m["c3"])
        if res is None:
            continue
        for i, (old, new) in enumerate(zip((m["c1"], m["c2"], m["c3"]), res)):
            if new is not None and tuple(new) != tuple(old):
                set_color(buf, m["off"] + 0x14 + i * 8, new)
                log.append(f"{m['name']} c{i + 1} {old} -> {tuple(new)}")
    return bytes(buf), log


def is_wii_blue(c):
    r, g, b = c[:3]
    return b >= 150 and r <= 100 and b - r >= 80 and g >= 100


def blue_to_accent(c):
    if not is_wii_blue(c):
        return None
    k = max(c[:3]) / 237.0
    return tuple(min(255, round(v * k)) for v in ACCENT) + (c[3],)


def generic_rule(name, c1, c2, c3):
    out = [blue_to_accent(c) for c in (c1, c2, c3)]
    return out if any(out) else None


BG_PANES = [f"Picture_0{i}" for i in range(5)] + [f"BaseMask{i}" for i in range(5)]


def chansel_rule(name, c1, c2, c3):
    base = generic_rule(name, c1, c2, c3) or [None, None, None]
    if name in BG_PANES and c2[:3] == (245, 245, 245):  # solo quelli di my_IplTop_a, non my_TVMask_a
        # TEV: lerp(C0, C1, texture) -> con nero/bianco mostra la texture (lo sfondo) così com'è
        return [(0, 0, 0, c1[3]), (255, 255, 255, c2[3]), None]
    if name.startswith(("Picture_", "board")) and c2[:3] == (245, 245, 245):
        # usano anche my_TVSheet_b (ora lo sfondo): c1 == c2 rende il colore costante
        return [BAR[1] + (c1[3],), BAR[1] + (c2[3],), None]
    if name.startswith("Edge"):
        return [ACCENT_DARK + (c1[3],), ACCENT + (c2[3],), None]
    if name.startswith("Shade") and c2[:3] == (60, 70, 80):
        return [(0, 0, 0, 0), (0, 0, 0, 170), None]
    if name in ("Clock0", "Clock1", "Clock2", "Clock3", "ClockTen", "AM_PM", "AM_PM_R"):
        return [WHITE + (c1[3],), WHITE + (c2[3],), None]
    if name == "Ch0":
        return [SLOT[0] + (255,), SLOT[1] + (255,), None]
    if name == "Ch1":  # come azurenight, verificato sulla console
        return [(0, 0, 0, 0), (0, 0, 0, 255), None]
    return base


def chanttl_rule(name, c1, c2, c3):
    if name == "Base0":
        return [BAR[0] + (c1[3],), BAR[1] + (c2[3],), None]
    if name.startswith(("BtnA", "BtnB")) and name[4:5].isdigit() and not name.endswith("_Shade"):
        return [(30, 22, 36, c1[3]), (52, 40, 62, c2[3]), None]
    if name.startswith(("BtnA_Ac", "BtnB_Ac")):
        return [ACCENT + (c1[3],), ACCENT + (c2[3],), None]
    if name in ("T_BtnA", "T_BtnB"):
        return [WHITE + (c1[3],), WHITE + (c2[3],), None]
    return generic_rule(name, c1, c2, c3)


def set_uv(data, pane_names, uv_index, uv):
    """Imposta un set di coordinate texture (4 angoli) dei pannelli indicati."""
    buf = bytearray(data)
    _, _, panes = brlyt.parse(data)
    log = []
    for p in panes:
        if p["kind"] == "pic1" and p["name"] in pane_names:
            n = buf[p["off"] + 0x5E]
            assert uv_index < n, (p["name"], n)
            o = p["off"] + 0x60 + uv_index * 32
            old = struct.unpack_from(">8f", buf, o)
            struct.pack_into(">8f", buf, o, *uv)
            log.append(f"{p['name']} uv{uv_index} {tuple(round(v, 2) for v in old)} -> {uv}")
    return bytes(buf), log


def board_rule(name, c1, c2, c3):
    if name.startswith("TopBack_"):
        return [(0, 0, 0, 0), None, None]
    if name.startswith("T_Day_"):
        return [MUTED + (c1[3],), MUTED + (c2[3],), None]
    return generic_rule(name, c1, c2, c3)


def cmnbtn_rule(name, c1, c2, c3):
    if name == "BbsMark0":
        return [WHITE + (c1[3],), WHITE + (c2[3],), None]
    return generic_rule(name, c1, c2, c3)


def cursor_rule(name, c1, c2, c3):
    if name in ("P1_Cat", "P1_Def"):  # non le ombre P1_CatS / P1_DefS
        return [ACCENT + (c1[3],), None, None]
    return None


# ---------- texture ----------

def make_tpl(orig, img, fmt):
    """Nuovo TPL a immagine singola, con wrap/filtri copiati dall'originale."""
    im0 = tpl.images(orig)[0]
    hdr = bytearray(orig[im0["hdr_off"]:im0["hdr_off"] + 0x24])
    h, w = img.shape[:2]
    data_off = 0x40
    struct.pack_into(">HHII", hdr, 0, h, w, fmt, data_off)
    out = bytearray(struct.pack(">III", 0x0020AF30, 1, 0x0C))
    out += struct.pack(">II", 0x14, 0)
    out += hdr
    out += b"\0" * (data_off - len(out))
    out += tpl.encode(img, fmt)
    return bytes(out)


def same_tpl(orig, img):
    """Sostituisce l'immagine mantenendo formato e dimensioni."""
    return tpl.replace(orig, tpl.images(orig)[0], img)


def supersample(size, draw_fn, ss=4):
    big = Image.new("RGBA", (size[0] * ss, size[1] * ss), (0, 0, 0, 0))
    draw_fn(ImageDraw.Draw(big), ss)
    return big.resize(size, Image.LANCZOS)


def circle_button(size, inset, icon_fn, ring=3.0):
    def draw(d, s):
        x0 = inset * s; x1 = (size - inset) * s - 1
        d.ellipse((x0, x0, x1, x1), fill=ACCENT + (255,))
        r = ring * s
        d.ellipse((x0 + r, x0 + r, x1 - r, x1 - r), fill=CARD + (255,))
        icon_fn(d, s, size * s / 2)
    return supersample((size, size), draw)


def icon_wii(d, s, c):
    f = ImageFont.truetype(F + "segoeuib.ttf", int(25 * s))
    d.text((c, c + 1 * s), "Wii", font=f, fill=WHITE + (255,), anchor="mm")


def icon_plus(d, s, c):
    L, T = 15 * s, 3.5 * s
    d.rounded_rectangle((c - L, c - T, c + L, c + T), T, fill=WHITE + (255,))
    d.rounded_rectangle((c - T, c - L, c + T, c + L), T, fill=WHITE + (255,))


def icon_minus(d, s, c):
    L, T = 15 * s, 3.5 * s
    d.rounded_rectangle((c - L, c - T, c + L, c + T), T, fill=WHITE + (255,))


def icon_none(d, s, c):
    pass


def icon_calendar(d, s, c):
    w, h = 26 * s, 22 * s
    x0, y0 = c - w / 2, c - h / 2 + 2 * s
    d.rounded_rectangle((x0, y0, x0 + w, y0 + h), 3 * s, outline=WHITE + (255,), width=int(2.5 * s))
    d.rectangle((x0, y0, x0 + w, y0 + 6 * s), fill=WHITE + (255,))
    for gy in range(2):
        for gx in range(3):
            cx = x0 + (gx + 1) * w / 4; cy = y0 + 11 * s + gy * 6 * s
            d.ellipse((cx - 1.8 * s, cy - 1.8 * s, cx + 1.8 * s, cy + 1.8 * s), fill=WHITE + (255,))
    for gx in (1, 3):
        cx = x0 + gx * w / 4
        d.rounded_rectangle((cx - 1.5 * s, y0 - 4 * s, cx + 1.5 * s, y0 + 2 * s), s, fill=WHITE + (255,))


def icon_pencil(d, s, c):
    import math
    ang = math.radians(-45)
    ux, uy = math.cos(ang), math.sin(ang)
    px, py = -uy, ux
    L, T = 13 * s, 4 * s
    tip = (c - ux * L, c - uy * L)
    a = (c - ux * (L - 7 * s) + px * T, c - uy * (L - 7 * s) + py * T)
    b = (c - ux * (L - 7 * s) - px * T, c - uy * (L - 7 * s) - py * T)
    e1 = (c + ux * L + px * T, c + uy * L + py * T)
    e2 = (c + ux * L - px * T, c + uy * L - py * T)
    d.polygon([tip, a, e1, e2, b], fill=WHITE + (255,))
    d.line([(c + ux * (L - 5 * s) + px * T, c + uy * (L - 5 * s) + py * T),
            (c + ux * (L - 5 * s) - px * T, c + uy * (L - 5 * s) - py * T)], fill=CARD + (255,), width=int(1.5 * s))


def arrow(size, direction, bbox_w=24, bbox_h=44):
    def draw(d, s):
        cx, cy = size * s / 2, size * s / 2
        hw, hh = bbox_w * s / 2, bbox_h * s / 2
        if direction > 0:
            pts = [(cx - hw, cy - hh), (cx + hw, cy), (cx - hw, cy + hh)]
        else:
            pts = [(cx + hw, cy - hh), (cx - hw, cy), (cx + hw, cy + hh)]
        d.polygon(pts, fill=ACCENT + (255,))
    return supersample((size, size), draw)


def clock_digit(ch, ref):
    """Cifra sottile (Segoe UI Light) adattata al riquadro della cifra originale."""
    ys, xs = np.where(ref[..., 0] > 40)
    top, bottom = ys.min(), ys.max()
    S = 8
    big = Image.new("L", (48 * S, 48 * S), 0)
    d = ImageDraw.Draw(big)
    size = 300
    f = ImageFont.truetype(F + "segoeuil.ttf", size)
    l, t, r, b = d.textbbox((0, 0), "0", font=f)
    scale = (bottom - top + 1) * S / (b - t)
    f = ImageFont.truetype(F + "segoeuil.ttf", int(size * scale))
    l, t, r, b = d.textbbox((0, 0), "0", font=f)
    y = top * S - t
    if ch == ":":
        rad = 2.6 * S
        for cy in ((top + bottom) / 2 - 7, (top + bottom) / 2 + 7):
            d.ellipse((24 * S - rad, cy * S - rad, 24 * S + rad, cy * S + rad), fill=255)
    else:
        w = d.textlength(ch, font=f)
        d.text((24 * S - w / 2, y), ch, font=f, fill=255)
    small = np.array(big.resize((48, 48), Image.LANCZOS))
    return np.stack([small, small, small, np.full_like(small, 255)], -1)


def wallpaper_tex(path, out_w=544, out_h=408):
    src = Image.open(path).convert("RGB")
    W16, H16 = 1088, 612
    sw, sh = src.size
    if sw / sh > W16 / H16:
        nw = int(sh * W16 / H16); src = src.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
    else:
        nh = int(sw * H16 / W16); src = src.crop((0, (sh - nh) // 2, sw, (sh - nh) // 2 + nh))
    canvas = src.resize((W16, H16), Image.LANCZOS).convert("RGBA")
    d = ImageDraw.Draw(canvas)
    f1 = ImageFont.truetype(F + "segoeui.ttf", 22)
    f2 = ImageFont.truetype(F + "segoeuib.ttf", 22)
    x = W16 - 40; y = 30
    w2 = d.textlength("VinZo", font=f2)
    d.text((x - w2, y), "VinZo", font=f2, fill=ACCENT + (255,), anchor="lm")
    d.text((x - w2 - 2, y), "Mod by ", font=f1, fill=MUTED + (220,), anchor="rm")
    canvas.convert("RGB").save(os.path.join(PREVIEW_DIR, "sfondo_16x9.png"))
    tex = canvas.resize((out_w, out_h), Image.LANCZOS)
    return np.array(tex.convert("RGBA"))


def menu_bg_tex(path, out_w=512, out_h=256):
    """Sfondo del menu principale.

    Ogni pagina di canali ha la sua copia dello sfondo e le pagine sono affiancate: lo schermo
    mostra a sinistra la fine dell'immagine della pagina precedente e a destra la fine di quella
    corrente (misurato dalle foto: l'ultimo ~9% della larghezza). Quindi l'immagine deve essere
    continua tra bordo destro e sinistro, e la firma va nell'ultimo 8% a destra.
    """
    W, H = 1216, 512  # proporzioni fisiche del pannello 512x288 su TV 16:9
    src = Image.open(path).convert("RGB")
    sw, sh = src.size
    if sw / sh > W / H:
        nw = int(sh * W / H); src = src.crop(((sw - nw) // 2, 0, (sw - nw) // 2 + nw, sh))
    else:
        nh = int(sw * H / W); src = src.crop((0, 0, sw, nh))  # parte alta: le onde viola
    a = np.asarray(src.resize((W, H), Image.LANCZOS), dtype=np.float32) / 255.0
    # Raccordo senza cucitura: al centro l'immagine, ai bordi la stessa spostata di mezza larghezza
    b = np.roll(a, W // 2, axis=1)
    m = (np.abs(np.arange(W) - W / 2) / (W / 2)) ** 2
    img = a * (1 - m[None, :, None]) + b * m[None, :, None]
    # Più luce sulle onde: lo sfondo si vede solo nei margini e tra le schede
    img = np.clip(img ** 0.7 * 1.15, 0, 1)
    canvas = Image.fromarray((img * 255).astype(np.uint8), "RGB").convert("RGBA")
    d = ImageDraw.Draw(canvas)
    # In alto, sopra la prima riga di schede (a destra le schede della pagina dopo partono da ~y 50)
    f1 = ImageFont.truetype(F + "segoeui.ttf", 17)
    f2 = ImageFont.truetype(F + "segoeuib.ttf", 21)
    cx = int(W * 0.955)
    d.text((cx, 14), "Mod by", font=f1, fill=MUTED + (235,), anchor="mm")
    d.text((cx, 34), "VinZo", font=f2, fill=ACCENT + (255,), anchor="mm")
    canvas.convert("RGB").save(os.path.join(PREVIEW_DIR, "sfondo_menu.png"))
    return np.array(canvas.resize((out_w, out_h), Image.LANCZOS))


# ---------- archivi ----------

def load_arc(name):
    return u8.parse(open(os.path.join(ARC_DIR, name + ".arc"), "rb").read())


def save_preview(arc, path, img):
    Image.fromarray(img, "RGBA").save(os.path.join(PREVIEW_DIR, f"{arc}__{os.path.basename(path)}.png"))


def set_wrap(data, mat_names, tex_name, wrap_s, wrap_t):
    """Imposta il wrap (0=clamp, 1=repeat, 2=mirror) della texture tex_name nei materiali indicati."""
    buf = bytearray(data)
    textures, mats, _ = brlyt.parse(data)
    log = []
    for m in mats:
        if m["name"] not in mat_names:
            continue
        for i in range(m["flags"] & 0xF):
            o = m["off"] + 0x40 + i * 4
            ti, ws, wt = struct.unpack_from(">HBB", buf, o)
            if textures[ti] == tex_name and (ws, wt) != (wrap_s, wrap_t):
                struct.pack_into(">HBB", buf, o, ti, wrap_s, wrap_t)
                log.append(f"{m['name']} wrap {tex_name} ({ws},{wt}) -> ({wrap_s},{wrap_t})")
    return bytes(buf), log


ANIM_SLOTS = {4: 0, 8: 1, 12: 2}  # RLMC: target 4-7 = c1, 8-11 = c2, 12-15 = c3 (RGBA)


def patch_anim_colors(data, rule, static):
    """Applica la stessa regola dei materiali ai colori animati (RLMC), che altrimenti
    riporterebbero i colori originali durante le animazioni."""
    buf = bytearray(data)
    log = []
    groups = {}
    for name, tag, idx, target, keys in parse_brlan(data):
        if tag != "RLMC" or name not in static:
            continue
        base = target - target % 4
        if base not in ANIM_SLOTS or target % 4 == 3:
            continue
        for frame, value, slope, voff in keys:
            if voff is None:
                continue
            groups.setdefault((name, base, frame), {})[target % 4] = (value, voff)
    for (name, base, frame), ch in groups.items():
        slot = ANIM_SLOTS[base]
        cols = [list(c) for c in static[name]]
        for k, (v, _) in ch.items():
            cols[slot][k] = round(v)
        res = rule(name, *[tuple(c) for c in cols])
        if not res or res[slot] is None:
            continue
        for k, (v, voff) in ch.items():
            nv = float(res[slot][k])
            if nv != v:
                struct.pack_into(">f", buf, voff, nv)
                log.append(f"anim {name} c{slot + 1}[{'RGB'[k]}] frame {frame:.0f}: {v:.0f} -> {nv:.0f}")
    return bytes(buf), log


def process(arc_name, rule, tex_fn, lyt_fn=None):
    entries = load_arc(arc_name)
    static = {}
    for path, is_dir, content in entries:
        if not is_dir and path.endswith(".brlyt"):
            for m in brlyt.parse(content)[1]:
                static.setdefault(m["name"], (m["c1"], m["c2"], m["c3"]))
    out = []
    log = []
    for path, is_dir, content in entries:
        if not is_dir and path.endswith(".brlan"):
            content, l = patch_anim_colors(content, rule, static)
            log += [f"  {path}: {x}" for x in l]
        if not is_dir and path.endswith(".brlyt"):
            content, l = edit_materials(content, rule)
            log += [f"  {path}: {x}" for x in l]
            if lyt_fn:
                content, l = lyt_fn(path, content)
                log += [f"  {path}: {x}" for x in l]
        elif not is_dir and path.endswith(".tpl"):
            new = tex_fn(path, content)
            if new is not None:
                log.append(f"  {path}: texture sostituita ({len(content)} -> {len(new)} byte)")
                content = new
        out.append((path, is_dir, content))
    return u8.build(out), log


FULL_UV = (0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 1.0, 1.0)


def chansel_lyt(path, content):
    if not path.endswith("my_IplTop_a.brlyt"):
        return content, []
    # Lo sfondo era una riga ripetuta 36 volte: ora l'immagine copre il pannello una volta sola.
    # Picture_xx e BaseMask generano la coordinata della texture sfondo dal set UV 1 (TEX1).
    bg = [f"Picture_0{i}" for i in range(5)] + [f"BaseMask{i}" for i in range(5)]
    content, l1 = set_uv(content, bg, 1, FULL_UV)
    content, l2 = set_wrap(content, bg, "my_TVSheet_b.tpl", 0, 0)
    return content, l1 + l2


def board_lyt(path, content):
    if not path.endswith("my_IplTop_c.brlyt"):
        return content, []
    # Lo sfondo della bacheca era una striscia 8px ripetuta 38 volte in orizzontale
    names = ["TopBack_a", "TopBack_b", "TopBack_c"]
    content, l1 = set_uv(content, names, 0, FULL_UV)
    content, l2 = set_wrap(content, names, "my_BackPic_a.tpl", 0, 0)
    return content, l1 + l2


def chansel_tex(path, content):
    name = os.path.basename(path)[:-4]
    if name == "my_TVSheet_b":
        # Dimensioni potenza di 2: le texture ripetute (wrap REPEAT) le richiedono su GX
        img = menu_bg_tex(WALLPAPER, 512, 256)
        save_preview("chanSel", path, img)
        return make_tpl(content, img, 4)  # RGB565, sfondo opaco
    digits = {f"my_Clock_a{i}": str(i) for i in range(10)}
    digits["my_Clock_ab"] = ":"
    if name in digits:
        ref = tpl.decode(content, tpl.images(content)[0])
        img = clock_digit(digits[name], ref if name != "my_Clock_ab" else tpl.decode(*_ref_zero()))
        save_preview("chanSel", path, img)
        return same_tpl(content, img)
    return None


_zero_cache = {}


def _ref_zero():
    if not _zero_cache:
        for p, d, c in load_arc("chanSel.ash"):
            if p.endswith("my_Clock_a0.tpl"):
                _zero_cache["v"] = (c, tpl.images(c)[0])
    return _zero_cache["v"]


def cmnbtn_tex(path, content):
    name = os.path.basename(path)[:-4]
    art = {
        "my_TopBtn_c": lambda: circle_button(80, 4, icon_wii),
        "my_TopBtn_b": lambda: circle_button(80, 4, icon_wii),
        "my_TopBtn_a": lambda: circle_button(80, 2.5, icon_none),
        "my_TopBtn_d": lambda: circle_button(64, 1.5, icon_calendar, ring=2.5),
        "my_TopBtn_e": lambda: circle_button(64, 1.5, icon_pencil, ring=2.5),
        "my_ComBtn_a": lambda: circle_button(80, 1.5, icon_plus),
        "my_ComBtn_b": lambda: circle_button(80, 1.5, icon_minus),
        "my_arw_a": lambda: arrow(64, +1),
        "my_arw_b": lambda: arrow(64, -1),
    }
    if name not in art:
        return None
    img = np.array(art[name]().convert("RGBA"))
    save_preview("cmnBtn", path, img)
    return make_tpl(content, img, 5)  # RGB5A3, come azurenight


def board_tex(path, content):
    if os.path.basename(path) == "my_BackPic_a.tpl":
        img = wallpaper_tex(WALLPAPER, 512, 512)
        save_preview("board", path, img)
        # CMPR (4 bit/pixel): +~100 KB di memoria come azurenight, invece di +430 KB con RGB5A3
        return make_tpl(content, img, 14)
    return None


def no_tex(path, content):
    return None


JOBS = [
    ("chanSel.ash", chansel_rule, chansel_tex, chansel_lyt),
    ("cmnBtn.ash", cmnbtn_rule, cmnbtn_tex, None),
    ("board.ash", board_rule, board_tex, board_lyt),
    ("cursor.ash", cursor_rule, no_tex, None),
    ("chanTtl.ash", chanttl_rule, no_tex, None),
]

new_arcs = {}
for arc_name, rule, tex_fn, lyt_fn in JOBS:
    arc, log = process(arc_name, rule, tex_fn, lyt_fn)
    new_arcs["layout/common/" + arc_name] = lz77.compress(arc)
    print(f"== {arc_name}: {len(arc)} byte decompressi, {len(new_arcs['layout/common/' + arc_name])} compressi, {len(log)} modifiche")
    print("\n".join(log))

base = u8.parse(open(BASE_APP, "rb").read())
replaced = 0
out = []
for path, is_dir, content in base:
    if path in new_arcs:
        content = new_arcs[path]; replaced += 1
    out.append((path, is_dir, content))
assert replaced == len(new_arcs), (replaced, len(new_arcs))
csm = u8.build(out)
open(OUT_CSM, "wb").write(csm)
print("csm scritto:", OUT_CSM, len(csm), "byte")

"""Anteprima della schermata principale di USB Loader GX: sfondo + pulsanti nelle posizioni
predefinite di r1283 (coordinate 4:3 del codice: GameBrowseMenu.cpp)."""
import os, sys
from PIL import Image

d, out = sys.argv[1], sys.argv[2]
scr = Image.open(os.path.join(d, "background.png")).convert("RGBA")
for name, (x, y) in {"button_install.png": (16, 355), "settings_button.png": (64, 371), "sdcard.png": (160, 395),
                     "browser.png": (410, 405), "menu_button.png": (489, 371), "wiimote_poweroff.png": (576, 355)}.items():
    p = os.path.join(d, name)
    if os.path.exists(p):
        scr.alpha_composite(Image.open(p).convert("RGBA"), (x, y))
scr.resize((1280, 960), Image.LANCZOS).convert("RGB").save(out)

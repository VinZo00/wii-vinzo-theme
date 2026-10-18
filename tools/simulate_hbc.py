"""Anteprima approssimata della lista app dell'Homebrew Channel con il tema generato."""
import os, sys
from PIL import Image, ImageDraw, ImageFont

d_in, out = sys.argv[1], sys.argv[2]
L = lambda n: Image.open(os.path.join(d_in, n)).convert("RGBA")
scr = L("background_wide.png")
d = ImageDraw.Draw(scr)
f1 = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 18)
f2 = ImageFont.truetype("C:/Windows/Fonts/segoeui.ttf", 14)
apps = [("USB Loader GX", "Loader di giochi da USB"), ("Nintendont", "GameCube su Wii"),
        ("csm-installer", "Installa temi del menu Wii"), ("VinZo Theme (HBC)", "Tema Material Dark viola")]
x0 = (852 - 432) // 2
for i, (n, desc) in enumerate(apps):
    y = 70 + i * 72
    scr.alpha_composite(L("apps_list_hover.png" if i == 1 else "apps_list.png"), (x0, y))
    d.text((x0 + 24, y + 20), n, font=f1, fill=(240, 240, 245))
    d.text((x0 + 24, y + 42), desc, font=f2, fill=(200, 190, 210))
scr.alpha_composite(L("apps_previous.png"), (x0 - 80, 190))
scr.alpha_composite(L("apps_next_hover.png"), (x0 + 432 + 16, 190))
scr.alpha_composite(L("icon_network_active.png"), (40, 430))
scr.alpha_composite(L("icon_usbgecko.png"), (80, 430))
scr.convert("RGB").save(out)

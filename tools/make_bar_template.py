"""Crea il modello 1920x1080 per l'immagine della barra inferiore (misure prese dalle foto della TV).

L'immagine copre tutto lo schermo (texture my_BackPic_a di board.ash): nel menu principale si vede
solo sotto la curva della barra, nella bacheca dei messaggi si vede intera.
"""
import sys
from PIL import Image, ImageDraw, ImageFont

out = sys.argv[1]
W, H = 1920, 1080
F = "C:/Windows/Fonts/"
img = Image.new("RGBA", (W, H), (40, 40, 48, 255))
d = ImageDraw.Draw(img, "RGBA")
fs = ImageFont.truetype(F + "segoeui.ttf", 26)
fb = ImageFont.truetype(F + "segoeuib.ttf", 30)


def X(f): return int(f * W)
def Y(f): return int(f * H)


# zona coperta dalla griglia dei canali nel menu (visibile solo nella bacheca)
d.rectangle((0, 0, W, Y(0.716)), fill=(70, 70, 80, 255))
d.text((W // 2, Y(0.33)), "Coperto dai canali nel menu principale\n(visibile solo nella bacheca messaggi)",
       font=fb, fill=(200, 200, 210), anchor="mm", align="center")
# parte centrale rialzata della barra (colore pieno del tema, con l'orologio): non si vede l'immagine
pts = [(X(0.23), Y(0.716))]
for i in range(41):
    t = i / 40
    x = 0.23 + t * 0.57
    if x < 0.37:
        y = 0.716 + (0.827 - 0.716) * ((x - 0.23) / 0.14)
    elif x <= 0.69:
        y = 0.827
    else:
        y = 0.827 - (0.827 - 0.716) * ((x - 0.69) / 0.11)
    pts.append((X(x), Y(y)))
d.polygon(pts, fill=(70, 70, 80, 255))
d.line(pts, fill=(224, 64, 251, 255), width=5)
d.line([(0, Y(0.716)), (X(0.23), Y(0.716))], fill=(224, 64, 251, 255), width=5)
d.line([(X(0.80), Y(0.716)), (W, Y(0.716))], fill=(224, 64, 251, 255), width=5)
d.text((X(0.51), Y(0.766)), "orologio (colore pieno)", font=fs, fill=(220, 220, 230), anchor="mm")

# elementi sopra l'immagine
def circle(cx, cy, r, label):
    d.ellipse((X(cx) - r, Y(cy) - r, X(cx) + r, Y(cy) + r), outline=(255, 255, 255, 230), width=4)
    d.text((X(cx), Y(cy)), label, font=fs, fill=(255, 255, 255), anchor="mm")


circle(0.116, 0.84, 84, "Wii")
circle(0.878, 0.84, 86, "Posta")
d.rectangle((X(0.224) - 30, Y(0.87) - 38, X(0.224) + 30, Y(0.87) + 38), outline=(255, 255, 255, 230), width=3)
d.text((X(0.224), Y(0.87)), "SD", font=fs, fill=(255, 255, 255), anchor="mm")
d.text((X(0.495), Y(0.88)), "Data (es. Do 18/10)", font=fb, fill=(255, 255, 255), anchor="mm")
# posto consigliato per la firma
d.rectangle((X(0.40), Y(0.935), X(0.60), Y(0.985)), outline=(224, 64, 251, 255), width=3)
d.text((X(0.50), Y(0.96)), "Mod by VinZo (qui)", font=fs, fill=(224, 64, 251), anchor="mm")
d.text((20, Y(0.725)), "zona visibile della barra: sotto la linea viola", font=fs, fill=(255, 255, 255), anchor="lt")
img.convert("RGB").save(out)

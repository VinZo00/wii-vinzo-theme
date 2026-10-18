"""Estrae dal sorgente di USB Loader GX tutte le chiavi del tema (thInt/thColor/thAlign/thFloat)
e scrive un modello .them completo per QUELLA versione del loader (msgstr vuoti = valori di fabbrica).
Uso: python gx_keys.py <cartella_source> <uscita.them>
"""
import os, re, sys

SRC, OUT = sys.argv[1:3]
pat = re.compile(r'th(?:Int|Color|Align|Float)\("((?:[^"\\]|\\.)*)"\)')
keys = []
for root, _, files in os.walk(SRC):
    for fn in sorted(files):
        if not fn.endswith((".cpp", ".c", ".h")):
            continue
        with open(os.path.join(root, fn), encoding="utf-8", errors="replace") as f:
            for k in pat.findall(f.read()):
                if k not in keys:
                    keys.append(k)
header = '''# USB Loader GX theme source file.
# ONLY the value before the '-' char needs to be entered in msgstr ""
# It is important that the image folder is defined for the images to load.
msgid ""
msgstr ""
"Project-Id-Version: USB Loader GX\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=utf-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Theme-Title: Example\\n"
"Image-Folder: Example\\n"
"Last-Themer: Example\\n"
"Theme-Team: Example\\n"
"Theme-Version: Example\\n"

'''
with open(OUT, "w", encoding="utf-8", newline="\n") as f:
    f.write(header)
    for k in keys:
        f.write(f'msgid "{k}"\nmsgstr ""\n\n')
print(len(keys), "chiavi")

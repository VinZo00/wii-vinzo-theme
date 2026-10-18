"""Estrae tutti i file del base app in una cartella."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import u8

app, out = sys.argv[1], sys.argv[2]
for path, is_dir, content in u8.parse(open(app, "rb").read()):
    if is_dir or not path:
        continue
    dst = os.path.join(out, path.replace("/", os.sep))
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "wb") as f:
        f.write(content)
print("ok")

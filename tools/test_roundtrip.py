"""Verifica che u8.build e lz77 ricostruiscano esattamente/correttamente i dati originali."""
import os, sys
sys.path.insert(0, os.path.dirname(__file__))
import u8, lz77

base_app, arc_dir = sys.argv[1], sys.argv[2]
data = open(base_app, "rb").read()
rebuilt = u8.build(u8.parse(data))
print("base.app identico:", rebuilt == data, len(rebuilt), len(data))
if rebuilt != data:
    i = next(i for i in range(min(len(data), len(rebuilt))) if data[i] != rebuilt[i])
    print("prima differenza a", hex(i))
for fn in ("chanSel.ash.arc", "cmnBtn.ash.arc", "board.ash.arc", "cursor.ash.arc"):
    a = open(os.path.join(arc_dir, fn), "rb").read()
    r = u8.build(u8.parse(a))
    ok_struct = [(p, d, c) for p, d, c in u8.parse(r)] == [(p, d, c) for p, d, c in u8.parse(a)]
    comp = lz77.compress(a)
    print(fn, "identico:", r == a, "contenuto uguale:", ok_struct, "lz77 ok:", lz77.decompress(comp) == a, f"{len(a)} -> {len(comp)}")

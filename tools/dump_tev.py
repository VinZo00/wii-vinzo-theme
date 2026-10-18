"""Decodifica le sezioni opzionali di un materiale BRLYT (TEV stages, blend, ecc.)."""
import os, sys, struct
sys.path.insert(0, os.path.dirname(__file__))
import u8, brlyt

CC = ["CPREV", "APREV", "C0", "A0", "C1", "A1", "C2", "A2", "TEXC", "TEXA", "RASC", "RASA", "ONE", "HALF", "KONST", "ZERO"]
CA = ["APREV", "A0", "A1", "A2", "TEXA", "RASA", "KONST", "ZERO"]

arc, lyt, names = sys.argv[1], sys.argv[2], sys.argv[3].split(",")
data = next(c for p, d, c in u8.parse(open(arc, "rb").read()) if p.endswith(lyt))
_, mats, _ = brlyt.parse(data)
for m in mats:
    if m["name"] not in names:
        continue
    f = m["flags"]
    o = m["off"] + 0x40
    ntex, nsrt, ngen = f & 0xF, (f >> 4) & 0xF, (f >> 8) & 0xF
    o += ntex * 4 + nsrt * 20 + ngen * 4
    print("==", m["name"], hex(f))
    if f >> 25 & 1:
        print("  chanCtrl", data[o:o + 4].hex()); o += 4
    if f >> 27 & 1:
        print("  matColor", tuple(data[o:o + 4])); o += 4
    if f >> 12 & 1:
        print("  swap", data[o:o + 4].hex()); o += 4
    o += ((f >> 13) & 3) * 12
    o += ((f >> 15) & 7) * 4
    nst = (f >> 18) & 0x1F
    for i in range(nst):
        st = data[o:o + 16]
        c_ab, c_cd, c_op, c_out = st[4], st[5], st[6], st[7]
        a_ab, a_cd, a_op, a_out = st[8], st[9], st[10], st[11]
        col = [CC[c_ab & 15], CC[c_ab >> 4], CC[c_cd & 15], CC[c_cd >> 4]]
        alp = [CA[a_ab & 7], CA[(a_ab >> 4) & 7], CA[a_cd & 7], CA[(a_cd >> 4) & 7]]
        print(f"  stage{i} raw={st.hex()} texcoord={st[0]} color a,b,c,d={col} alpha a,b,c,d={alp}")
        o += 16
    if f >> 23 & 1:
        print("  alphaCmp", data[o:o + 4].hex()); o += 4
    if f >> 24 & 1:
        print("  blend", data[o:o + 4].hex()); o += 4

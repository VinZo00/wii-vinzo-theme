"""Sblocca tutto (personaggi, veicoli, Mirror, coppe) nel salvataggio di Mario Kart Wii (rksys.dat).

Formato: https://mkwiiki.org/wiki/Rksys.dat
- 4 licenze RKPD (0x8CC0 byte) a 0x08, 0x8CC8, 0x11988, 0x1A648
- byte di sblocco 0x30..0x37 di ogni licenza: tutti a 0xFF (l'ordine dei bit non è documentato;
  i bit "riservati" non sono usati dal gioco)
- CRC-32 (zlib) dei dati 0..0x27FFC, salvato big-endian a 0x27FFC
I dati dei Grand Prix (coppe/stelle) NON vengono modificati.
Uso: python mkw_unlock.py <rksys.dat originale> <rksys.dat in uscita>
"""
import struct, sys, zlib

SRC, DST = sys.argv[1:3]
LICENSES = (0x08, 0x8CC8, 0x11988, 0x1A648)
CRC_OFF = 0x27FFC

d = bytearray(open(SRC, "rb").read())
assert len(d) == 0x2BC000 and d[:4] == b"RKSD", "non è un rksys.dat di Mario Kart Wii"
assert struct.unpack_from(">I", d, CRC_OFF)[0] == zlib.crc32(d[:CRC_OFF]) & 0xFFFFFFFF, "CRC originale non valido"
for i, off in enumerate(LICENSES):
    if d[off:off + 4] != b"RKPD":
        print(f"licenza {i}: assente, saltata")
        continue
    name = d[off + 0x14:off + 0x28].decode("utf-16-be", "replace").split("\0")[0]
    old = bytes(d[off + 0x30:off + 0x38])
    d[off + 0x30:off + 0x38] = b"\xff" * 8
    print(f"licenza {i} ({name}): sblocchi {old.hex()} -> {'ff' * 8}")
struct.pack_into(">I", d, CRC_OFF, zlib.crc32(d[:CRC_OFF]) & 0xFFFFFFFF)
assert struct.unpack_from(">I", d, CRC_OFF)[0] == zlib.crc32(d[:CRC_OFF]) & 0xFFFFFFFF
orig = open(SRC, "rb").read()
diff = [i for i in range(len(d)) if d[i] != orig[i]]
print(f"byte cambiati: {len(diff)} (da {hex(diff[0])} a {hex(diff[-1])})")
open(DST, "wb").write(d)
print("scritto", DST)

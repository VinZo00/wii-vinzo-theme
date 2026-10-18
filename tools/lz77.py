"""LZ77 tipo 0x10 (Nintendo), con header opzionale 'LZ77'."""
import struct


def decompress(data):
    off = 4 if data[:4] == b"LZ77" else 0
    hdr = struct.unpack_from("<I", data, off)[0]
    assert hdr & 0xFF == 0x10, hex(hdr & 0xFF)
    size = hdr >> 8
    src = off + 4
    out = bytearray()
    while len(out) < size:
        flags = data[src]; src += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                b1, b2 = data[src], data[src + 1]; src += 2
                length = (b1 >> 4) + 3
                disp = ((b1 & 0xF) << 8 | b2) + 1
                for _ in range(length):
                    out.append(out[-disp])
            else:
                out.append(data[src]); src += 1
    return bytes(out)


def compress(data, header=True):
    """Compressore greedy con hash chain: output compatibile 0x10."""
    n = len(data)
    out = bytearray(b"LZ77" if header else b"")
    out += struct.pack("<I", (n << 8) | 0x10)
    head = {}
    prev = [-1] * n
    i = 0
    def insert(p):
        if p + 3 <= n:
            k = data[p:p + 3]
            prev[p] = head.get(k, -1)
            head[k] = p
    while i < n:
        flag_pos = len(out); out.append(0); flags = 0
        for bit in range(8):
            if i >= n:
                break
            best_len, best_d = 0, 0
            if i + 3 <= n:
                cand = head.get(data[i:i + 3], -1)
                tries = 0
                maxl = min(18, n - i)
                while cand >= 0 and i - cand <= 4096 and tries < 64:
                    d = i - cand
                    if d >= 2:  # evita disp=1, come il compressore Nintendo "VRAM-safe"
                        l = 0
                        while l < maxl and data[cand + l] == data[i + l]:
                            l += 1
                        if l > best_len:
                            best_len, best_d = l, d
                            if l == maxl:
                                break
                    cand = prev[cand]; tries += 1
            if best_len >= 3:
                flags |= 0x80 >> bit
                dd = best_d - 1
                out.append(((best_len - 3) << 4) | (dd >> 8)); out.append(dd & 0xFF)
                for p in range(i, i + best_len):
                    insert(p)
                i += best_len
            else:
                out.append(data[i]); insert(i); i += 1
        out[flag_pos] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)

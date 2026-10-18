"""Decodifica/codifica texture TPL (GameCube/Wii) con numpy."""
import struct
import numpy as np

FMT = {0: "I4", 1: "I8", 2: "IA4", 3: "IA8", 4: "RGB565", 5: "RGB5A3", 6: "RGBA32", 8: "C4", 9: "C8", 10: "C14X2", 14: "CMPR"}
BLOCK = {0: (8, 8, 4), 1: (8, 4, 8), 2: (8, 4, 8), 3: (4, 4, 16), 4: (4, 4, 16), 5: (4, 4, 16), 6: (4, 4, 32), 14: (8, 8, 4)}


def images(data):
    """Ritorna lista di dict con w,h,fmt,offset,size,hdr_off,pal_off."""
    magic, n, table = struct.unpack_from(">III", data, 0)
    assert magic == 0x0020AF30
    out = []
    for i in range(n):
        hdr, pal = struct.unpack_from(">II", data, table + i * 8)
        h, w, fmt, off = struct.unpack_from(">HHII", data, hdr)
        out.append(dict(w=w, h=h, fmt=fmt, offset=off, size=data_size(w, h, fmt), hdr_off=hdr, pal_off=pal))
    return out


def data_size(w, h, fmt):
    bw, bh, bpp = BLOCK[fmt]
    pw = (w + bw - 1) // bw * bw
    ph = (h + bh - 1) // bh * bh
    return pw * ph * bpp // 8


def _tiles(w, h, bw, bh):
    """Ordine dei pixel nei blocchi: ritorna (ys, xs) per ogni pixel nel flusso."""
    pw = (w + bw - 1) // bw * bw
    ph = (h + bh - 1) // bh * bh
    by, bx, iy, ix = np.meshgrid(np.arange(ph // bh), np.arange(pw // bw), np.arange(bh), np.arange(bw), indexing="ij")
    return (by * bh + iy).ravel(), (bx * bw + ix).ravel(), pw, ph


def _scatter(vals, w, h, bw, bh, ch):
    ys, xs, pw, ph = _tiles(w, h, bw, bh)
    img = np.zeros((ph, pw, ch), np.uint8)
    img[ys, xs] = vals
    return img[:h, :w]


def _gather(img, bw, bh):
    h, w = img.shape[:2]
    ys, xs, pw, ph = _tiles(w, h, bw, bh)
    pad = np.zeros((ph, pw) + img.shape[2:], img.dtype)
    pad[:h, :w] = img
    if ph > h:
        pad[h:, :w] = img[h - 1:h]
    if pw > w:
        pad[:, w:] = pad[:, w - 1:w]
    return pad[ys, xs]


def decode(data, im):
    w, h, fmt = im["w"], im["h"], im["fmt"]
    raw = np.frombuffer(data, np.uint8, im["size"], im["offset"])
    if fmt == 0:
        v = np.empty(raw.size * 2, np.uint8); v[0::2] = raw >> 4; v[1::2] = raw & 15; v = v * 17
        rgba = np.stack([v, v, v, np.full_like(v, 255)], 1)
        return _scatter(rgba, w, h, 8, 8, 4)
    if fmt == 1:
        rgba = np.stack([raw, raw, raw, np.full_like(raw, 255)], 1)
        return _scatter(rgba, w, h, 8, 4, 4)
    if fmt == 2:
        a = (raw >> 4) * 17; i = (raw & 15) * 17
        return _scatter(np.stack([i, i, i, a], 1).astype(np.uint8), w, h, 8, 4, 4)
    if fmt == 3:
        a = raw[0::2]; i = raw[1::2]
        return _scatter(np.stack([i, i, i, a], 1), w, h, 4, 4, 4)
    if fmt == 4:
        p = raw.view(">u2").astype(np.uint32)
        r = (p >> 11) & 31; g = (p >> 5) & 63; b = p & 31
        rgba = np.stack([r * 255 // 31, g * 255 // 63, b * 255 // 31, np.full_like(r, 255)], 1).astype(np.uint8)
        return _scatter(rgba, w, h, 4, 4, 4)
    if fmt == 5:
        p = raw.view(">u2").astype(np.uint32)
        opaque = (p & 0x8000) != 0
        r = np.where(opaque, ((p >> 10) & 31) * 255 // 31, ((p >> 8) & 15) * 17)
        g = np.where(opaque, ((p >> 5) & 31) * 255 // 31, ((p >> 4) & 15) * 17)
        b = np.where(opaque, (p & 31) * 255 // 31, (p & 15) * 17)
        a = np.where(opaque, 255, ((p >> 12) & 7) * 255 // 7)
        return _scatter(np.stack([r, g, b, a], 1).astype(np.uint8), w, h, 4, 4, 4)
    if fmt == 6:
        blocks = raw.reshape(-1, 64)
        ar = blocks[:, :32].reshape(-1, 16, 2); gb = blocks[:, 32:].reshape(-1, 16, 2)
        rgba = np.stack([ar[..., 1], gb[..., 0], gb[..., 1], ar[..., 0]], -1).reshape(-1, 4)
        return _scatter(rgba, w, h, 4, 4, 4)
    if fmt == 14:
        return _decode_cmpr(raw, w, h)
    raise NotImplementedError(FMT.get(fmt, fmt))


def _565(c):
    c = c.astype(np.int32)
    return np.stack([((c >> 11) & 31) * 255 // 31, ((c >> 5) & 63) * 255 // 63, (c & 31) * 255 // 31], -1)


def _decode_cmpr(raw, w, h):
    sub = raw.reshape(-1, 8)  # sottoblocchi 4x4 in ordine: per blocco 8x8 -> 4 sottoblocchi
    c0 = sub[:, 0].astype(np.uint16) << 8 | sub[:, 1]
    c1 = sub[:, 2].astype(np.uint16) << 8 | sub[:, 3]
    a, b = _565(c0), _565(c1)
    gt = (c0 > c1)[:, None]
    p2 = np.where(gt, (2 * a + b) // 3, (a + b) // 2)
    p3 = np.where(gt, (a + 2 * b) // 3, 0)
    pal = np.stack([a, b, p2, p3], 1)  # n,4,3
    alpha = np.stack([np.full(len(sub), 255), np.full(len(sub), 255), np.full(len(sub), 255), np.where(gt[:, 0], 255, 0)], 1)
    bits = sub[:, 4:8]
    idx = np.stack([(bits >> s) & 3 for s in (6, 4, 2, 0)], -1).reshape(-1, 16)  # riga per riga
    rgb = np.take_along_axis(pal, idx[..., None].repeat(3, -1), 1)
    al = np.take_along_axis(alpha, idx, 1)
    px = np.concatenate([rgb, al[..., None]], -1).astype(np.uint8).reshape(-1, 4, 4, 4)  # sub, y, x, c
    pw = (w + 7) // 8 * 8; ph = (h + 7) // 8 * 8
    nbx = pw // 8
    img = np.zeros((ph, pw, 4), np.uint8)
    for k in range(px.shape[0]):
        blk, s = divmod(k, 4)
        by, bx = divmod(blk, nbx)
        y = by * 8 + (s // 2) * 4; x = bx * 8 + (s % 2) * 4
        img[y:y + 4, x:x + 4] = px[k]
    return img[:h, :w]


def encode(img, fmt):
    """img: HxWx4 uint8 -> bytes nel formato richiesto."""
    h, w = img.shape[:2]
    if fmt == 14:
        return _encode_cmpr(img)
    bw, bh, _ = BLOCK[fmt]
    p = _gather(img, bw, bh).astype(np.int32)
    r, g, b, a = p[:, 0], p[:, 1], p[:, 2], p[:, 3]
    lum = (r * 299 + g * 587 + b * 114 + 500) // 1000
    if fmt == 0:
        v = (lum * 15 + 127) // 255
        return ((v[0::2] << 4) | v[1::2]).astype(np.uint8).tobytes()
    if fmt == 1:
        return lum.astype(np.uint8).tobytes()
    if fmt == 2:
        return ((((a * 15 + 127) // 255) << 4) | ((lum * 15 + 127) // 255)).astype(np.uint8).tobytes()
    if fmt == 3:
        return np.stack([a, lum], 1).astype(np.uint8).tobytes()
    if fmt == 4:
        v = ((r * 31 + 127) // 255) << 11 | ((g * 63 + 127) // 255) << 5 | ((b * 31 + 127) // 255)
        return v.astype(">u2").tobytes()
    if fmt == 5:
        op = ((r * 31 + 127) // 255) << 10 | ((g * 31 + 127) // 255) << 5 | ((b * 31 + 127) // 255) | 0x8000
        tr = ((a * 7 + 127) // 255) << 12 | ((r * 15 + 127) // 255) << 8 | ((g * 15 + 127) // 255) << 4 | ((b * 15 + 127) // 255)
        return np.where(a >= 255, op, tr).astype(">u2").tobytes()
    if fmt == 6:
        blk = p.reshape(-1, 16, 4).astype(np.uint8)
        ar = np.stack([blk[..., 3], blk[..., 0]], -1).reshape(-1, 32)
        gb = np.stack([blk[..., 1], blk[..., 2]], -1).reshape(-1, 32)
        return np.concatenate([ar, gb], 1).tobytes()
    raise NotImplementedError(FMT.get(fmt, fmt))


def _to565(c):
    c = np.clip(c, 0, 255).astype(np.int32)
    return ((c[..., 0] * 31 + 127) // 255) << 11 | ((c[..., 1] * 63 + 127) // 255) << 5 | ((c[..., 2] * 31 + 127) // 255)


def _encode_cmpr(img):
    h, w = img.shape[:2]
    pw = (w + 7) // 8 * 8; ph = (h + 7) // 8 * 8
    pad = np.zeros((ph, pw, 4), np.uint8)
    pad[:h, :w] = img
    if ph > h: pad[h:, :w] = img[h - 1:h]
    if pw > w: pad[:, w:] = pad[:, w - 1:w]
    out = bytearray()
    for by in range(0, ph, 8):
        for bx in range(0, pw, 8):
            for s in range(4):
                y = by + (s // 2) * 4; x = bx + (s % 2) * 4
                out += _cmpr_sub(pad[y:y + 4, x:x + 4].reshape(16, 4).astype(np.float32))
    return bytes(out)


def _cmpr_sub(px):
    rgb, a = px[:, :3], px[:, 3]
    transp = a < 128
    use = ~transp
    if not use.any():
        return struct.pack(">HHI", 0, 0, 0xFFFFFFFF)
    pts = rgb[use]
    mean = pts.mean(0)
    cov = np.cov((pts - mean).T) if len(pts) > 1 else np.eye(3)
    axis = np.linalg.eigh(cov)[1][:, -1] if np.ptp(pts, 0).any() else np.array([1.0, 0, 0])
    proj = (pts - mean) @ axis
    e0 = mean + axis * proj.max(); e1 = mean + axis * proj.min()
    c0, c1 = int(_to565(e0)), int(_to565(e1))
    if transp.any():
        if c0 > c1: c0, c1 = c1, c0
        a_, b_ = _565(np.array(c0)), _565(np.array(c1))
        pal = np.array([a_, b_, (a_ + b_) // 2], np.float32)
        idx = np.argmin(((rgb[:, None, :] - pal[None]) ** 2).sum(-1), 1)
        idx[transp] = 3
    else:
        if c0 == c1:
            idx = np.zeros(16, int)
        else:
            if c0 < c1: c0, c1 = c1, c0
            a_, b_ = _565(np.array(c0)), _565(np.array(c1))
            pal = np.array([a_, b_, (2 * a_ + b_) // 3, (a_ + 2 * b_) // 3], np.float32)
            idx = np.argmin(((rgb[:, None, :] - pal[None]) ** 2).sum(-1), 1)
    bits = 0
    for i in idx:
        bits = (bits << 2) | int(i)
    return struct.pack(">HHI", c0, c1, bits)


def replace(data, im, img):
    """Ritorna nuovi bytes del TPL con l'immagine sostituita (stessa dimensione e formato)."""
    enc = encode(img, im["fmt"])
    assert len(enc) == im["size"], (len(enc), im["size"])
    buf = bytearray(data)
    buf[im["offset"]:im["offset"] + im["size"]] = enc
    return bytes(buf)

"""Lettura e scrittura di archivi U8 (Nintendo)."""
import struct

MAGIC = 0x55AA382D


def parse(data):
    """Ritorna lista di (path, is_dir, bytes|None) in ordine di nodo."""
    magic, root_off, hdr_size, data_off = struct.unpack_from(">IIII", data, 0)
    assert magic == MAGIC, "non è un U8"
    def node(i):
        return struct.unpack_from(">III", data, root_off + i * 12)
    _, _, total = node(0)
    nodes = [node(i) for i in range(total)]
    str_base = root_off + total * 12
    def name(off):
        end = data.index(b"\0", str_base + off)
        return data[str_base + off:end].decode("latin-1")
    out = []
    stack = []  # (dir_path, end_index)
    for i, (tn, a, b) in enumerate(nodes):
        typ = tn >> 24
        nm = name(tn & 0xFFFFFF)
        while stack and i >= stack[-1][1]:
            stack.pop()
        parent = stack[-1][0] if stack else ""
        path = (parent + "/" + nm) if parent else nm
        if i == 0:
            out.append(("", True, None))
            stack.append(("", b))
        elif typ == 1:
            out.append((path, True, None))
            stack.append((path, b))
        else:
            out.append((path, False, bytes(data[a:a + b])))
    return out


def build(entries):
    """entries: lista come da parse(), stesso ordine. Ricostruisce l'archivio."""
    # nomi e struttura
    names = b""
    name_offs = []
    for path, _, _ in entries:
        name_offs.append(len(names))
        names += path.rsplit("/", 1)[-1].encode("latin-1") + b"\0"
    total = len(entries)
    # parent index e fine directory
    paths = [p for p, _, _ in entries]
    dir_index = {"": 0}
    for i, (p, d, _) in enumerate(entries):
        if d:
            dir_index[p] = i
    def parent_of(p):
        return p.rsplit("/", 1)[0] if "/" in p else ""
    def dir_end(i):
        p = paths[i]
        j = i + 1
        while j < total and (p == "" or paths[j].startswith(p + "/")):
            j += 1
        return j
    hdr_size = total * 12 + len(names)
    root_off = 0x20
    data_off = (root_off + hdr_size + 0x3F) & ~0x3F
    blob = bytearray()
    node_bytes = bytearray()
    for i, (p, d, content) in enumerate(entries):
        if d:
            par = 0 if i == 0 else dir_index[parent_of(p)]
            node_bytes += struct.pack(">III", (1 << 24) | name_offs[i], par, dir_end(i))
        else:
            off = data_off + len(blob)
            node_bytes += struct.pack(">III", name_offs[i], off, len(content))
            blob += content
            blob += b"\0" * ((-len(blob)) % 0x20)
    out = bytearray(struct.pack(">IIII", MAGIC, root_off, hdr_size, data_off))
    out += b"\0" * 16
    out += node_bytes + names
    out += b"\0" * (data_off - len(out))
    out += blob
    return bytes(out)

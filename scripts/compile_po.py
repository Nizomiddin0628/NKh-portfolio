#!/usr/bin/env python3
"""po -> mo kompilyatori (gettext o'rnatilmagan mashinalar uchun).

Odatda `python manage.py compilemessages` ishlatiladi, lekin u tizimda
GNU gettext bo'lishini talab qiladi. Bu skript o'sha ishni sof Python'da
bajaradi:

    python scripts/compile_po.py
"""
import array
import os
import re
import struct
import sys

PO_ENTRY = re.compile(r'^(msgid|msgstr)\s+"(.*)"$')


def unescape(text: str) -> str:
    return (text.replace(r"\n", "\n").replace(r"\t", "\t")
                .replace(r"\"", '"').replace(r"\\", "\\"))


def parse_po(path):
    entries, mode = {}, None
    buf = {"msgid": "", "msgstr": ""}

    def flush():
        if buf["msgid"] is not None and buf["msgstr"]:
            entries[buf["msgid"]] = buf["msgstr"]

    with open(path, encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            match = PO_ENTRY.match(line)
            if match:
                kind, value = match.groups()
                if kind == "msgid":
                    flush()
                    buf["msgid"], buf["msgstr"] = unescape(value), ""
                else:
                    buf["msgstr"] = unescape(value)
                mode = kind
            elif line.startswith('"') and mode:
                buf[mode] += unescape(line[1:-1])
    flush()
    return entries


def write_mo(entries, path):
    """GNU .mo binar formatini yozadi."""
    items = sorted((k.encode("utf-8"), v.encode("utf-8")) for k, v in entries.items())
    keystart = 7 * 4 + 16 * len(items)
    valuestart = keystart + sum(len(k) + 1 for k, _ in items)

    koffsets, voffsets, kbuf, vbuf = [], [], b"", b""
    offset = 0
    for key, _ in items:
        koffsets.append((len(key), keystart + offset))
        kbuf += key + b"\x00"
        offset += len(key) + 1
    offset = 0
    for _, value in items:
        voffsets.append((len(value), valuestart + offset))
        vbuf += value + b"\x00"
        offset += len(value) + 1

    output = struct.pack("Iiiiiii", 0x950412DE, 0, len(items), 7 * 4,
                         7 * 4 + len(items) * 8, 0, 0)
    output += array.array("i", [x for pair in koffsets for x in pair]).tobytes()
    output += array.array("i", [x for pair in voffsets for x in pair]).tobytes()
    output += kbuf + vbuf

    with open(path, "wb") as fh:
        fh.write(output)


def main():
    base = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "locale")
    count = 0
    for root, _dirs, files in os.walk(base):
        for name in files:
            if not name.endswith(".po"):
                continue
            po = os.path.join(root, name)
            mo = po[:-3] + ".mo"
            entries = parse_po(po)
            entries.setdefault("", "Content-Type: text/plain; charset=UTF-8\n")
            write_mo(entries, mo)
            print(f"  {os.path.relpath(po, base)} -> {len(entries) - 1} strings")
            count += 1
    print(f"Compiled {count} catalogue(s).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

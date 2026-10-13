# -*- coding: utf-8 -*-
"""Minimal stdlib PDF text extractor with ToUnicode CMap support.

v3: processes EVERY decompressed stream that contains text-showing ops
(page content streams and Form XObjects alike), global font-name map,
literal + hex strings, Tf/Tm/Td line handling.
Usage: python extract_pdf_text_min.py <in.pdf> <out.txt>
"""
import sys, re, zlib

OBJ_RE = re.compile(rb'(\d+)\s+0\s+obj(.*?)endobj', re.S)
STREAM_RE = re.compile(rb'stream\r?\n?(.*?)endstream', re.S)

TOKEN_RE = re.compile(
    rb'(?P<font>/([\w\-#]+)\s+[\d.]+\s+Tf)'
    rb'|(?P<break>Tm\b|Td\b|TD\b|T\*\b|ET\b|BT\b)'
    rb'|(?P<arr>\[[^\[\]]*\]\s*TJ)'
    rb'|(?P<lit>\(((?:[^()\\]|\\.)*)\)\s*(?:Tj|\'|\"))'
    rb'|(?P<hex><([0-9A-Fa-f\s]+)>\s*(?:Tj|\'|\"))')

INNER_RE = re.compile(
    rb'\(((?:[^()\\]|\\.)*)\)|<([0-9A-Fa-f\s]+)>|(-?\d+(?:\.\d+)?)')


def inflate(data):
    data = data.strip(b'\r\n')
    try:
        return zlib.decompress(data)
    except Exception:
        try:
            return zlib.decompressobj(-15).decompress(data)
        except Exception:
            return b''


def hex_to_text(h):
    b = bytes.fromhex(h.decode('ascii'))
    if len(b) % 2 == 0 and b:
        try:
            return b.decode('utf-16-be')
        except Exception:
            pass
    return b.decode('latin-1')


def parse_cmap(body):
    st = STREAM_RE.search(body)
    if not st:
        return {}, 1
    data = inflate(st.group(1))
    if not data:
        return {}, 1
    mapping, width = {}, 1
    for blk in re.findall(rb'beginbfchar(.*?)endbfchar', data, re.S):
        for src, dst in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            mapping[int(src, 16)] = hex_to_text(dst)
            width = max(width, len(src) // 2)
    for blk in re.findall(rb'beginbfrange(.*?)endbfrange', data, re.S):
        for lo, hi, dst in re.findall(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>', blk):
            lo_i, hi_i, d = int(lo, 16), int(hi, 16), hex_to_text(dst)
            width = max(width, len(lo) // 2)
            if hi_i - lo_i > 65000:
                continue
            for k in range(lo_i, hi_i + 1):
                mapping[k] = chr(ord(d[0]) + (k - lo_i)) if len(d) == 1 else d
        for m in re.finditer(rb'<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*\[(.*?)\]', blk, re.S):
            lo_i, hi_i = int(m.group(1), 16), int(m.group(2), 16)
            for i, v in enumerate(re.findall(rb'<([0-9A-Fa-f]+)>', m.group(3))):
                if lo_i + i <= hi_i:
                    mapping[lo_i + i] = hex_to_text(v)
    return mapping, width


def unescape(s):
    out, i = bytearray(), 0
    esc = {0x6E: b'\n', 0x72: b'\r', 0x74: b'\t', 0x62: b'\x08',
           0x66: b'\x0c', 0x28: b'(', 0x29: b')', 0x5C: b'\\'}
    while i < len(s):
        c = s[i]
        if c == 0x5C and i + 1 < len(s):
            n = s[i + 1]
            if n in esc:
                out += esc[n]
                i += 2
                continue
            m = re.match(rb'([0-7]{1,3})', s[i + 1:])
            if m:
                out.append(int(m.group(1), 8) & 0xFF)
                i += 1 + len(m.group(1))
                continue
        out.append(c)
        i += 1
    return bytes(out)


def decode_bytes(b, cmap, width):
    if not cmap:
        return b.decode('latin-1', 'replace')
    txt, i = [], 0
    while i < len(b):
        if width == 2 and i + 1 < len(b):
            code = (b[i] << 8) | b[i + 1]
            i += 2
        else:
            code = b[i]
            i += 1
        txt.append(cmap.get(code, cmap.get(code & 0xFF, '')))
    return ''.join(txt)


def extract(pdf_path, out_path):
    raw = open(pdf_path, 'rb').read()
    objs = {int(n): body for n, body in OBJ_RE.findall(raw)}

    # global font-name -> font object; font object -> (cmap, width)
    fonts = {}
    for body in objs.values():
        for blk in re.findall(rb'/Font\s*<<(.*?)>>', body, re.S):
            for name, ref in re.findall(rb'/([\w\-#]+)\s+(\d+)\s+0\s+R', blk):
                fonts[name.decode()] = int(ref)
    fmaps = {}
    for num, body in objs.items():
        if b'/ToUnicode' in body:
            tu = re.search(rb'/ToUnicode\s+(\d+)\s+0\s+R', body)
            if tu and int(tu.group(1)) in objs:
                fmaps[num] = parse_cmap(objs[int(tu.group(1))])

    lines, n_text_streams = [], 0
    for num in sorted(objs):
        body = objs[num]
        if b'stream' not in body:
            continue
        st = STREAM_RE.search(body)
        if not st:
            continue
        data = inflate(st.group(1))
        if not data or not (b'Tj' in data or b'TJ' in data):
            continue
        n_text_streams += 1
        cur = (-1, {}, 1)
        for m in TOKEN_RE.finditer(data):
            if m.group('font'):
                fname = m.group(2).decode()
                fnum = fonts.get(fname, -1)
                cur = (fnum,) + fmaps.get(fnum, ({}, 1))
            elif m.group('break'):
                lines.append('\x00BR')
            elif m.group('arr'):
                # TJ array: decode every string inside, big kerning numbers -> space
                for im in INNER_RE.finditer(m.group('arr')):
                    if im.group(1) is not None:
                        txt = decode_bytes(unescape(im.group(1)), cur[1], cur[2])
                        if txt:
                            lines.append(txt)
                    elif im.group(2) is not None:
                        hexs = re.sub(rb'\s', b'', im.group(2))
                        if len(hexs) % 2:
                            hexs += b'0'
                        txt = decode_bytes(bytes.fromhex(hexs.decode('ascii')), cur[1], cur[2])
                        if txt:
                            lines.append(txt)
                    else:
                        try:
                            if abs(float(im.group(3))) >= 80:
                                lines.append(' ')
                        except (TypeError, ValueError):
                            pass
            elif m.group('lit') is not None:
                mm = re.match(rb'\(((?:[^()\\]|\\.)*)\)', m.group('lit'))
                if not mm:
                    continue
                txt = decode_bytes(unescape(mm.group(1)), cur[1], cur[2])
                if txt:
                    lines.append(txt)
            elif m.group('hex') is not None:
                mm = re.search(rb'<([0-9A-Fa-f\s]*)>', m.group('hex'))
                if not mm:
                    continue
                hexs = re.sub(rb'[^0-9A-Fa-f]', b'', mm.group(1))
                if len(hexs) % 2:
                    hexs += b'0'
                txt = decode_bytes(bytes.fromhex(hexs.decode('ascii')), cur[1], cur[2])
                if txt:
                    lines.append(txt)

    text, buf = [], []
    for part in lines:
        if part == '\x00BR':
            if buf:
                text.append(''.join(buf).strip())
                buf = []
        else:
            buf.append(part)
    if buf:
        text.append(''.join(buf).strip())
    joined = '\n'.join(t for t in text if t)
    joined = re.sub(r'\n{3,}', '\n\n', joined)
    open(out_path, 'w', encoding='utf-8').write(joined)
    letters = sum(c.isalpha() for c in joined)
    print(f'{out_path}: {len(joined)} chars; alpha={letters / max(1, len(joined)):.3f}; '
          f'text-streams={n_text_streams}; fonts={len(fonts)}; tounicode={len(fmaps)}')


if __name__ == '__main__':
    extract(sys.argv[1], sys.argv[2])

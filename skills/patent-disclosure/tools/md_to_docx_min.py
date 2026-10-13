# -*- coding: utf-8 -*-
"""Convert a markdown patent-style document to .docx with stdlib only (DSH offline).

Layout conventions (patent-draft style, mirrors a Chinese application draft):
  # title            -> centered, 黑体 18pt
  ## / ### / ####    -> bold 黑体 16 / 14 / 12pt
  $$formula$$        -> centered formula paragraph, no first-line indent
  normal paragraph   -> 宋体 10.5pt, justified, first-line indent 2 chars
  - list item        -> no first-line indent, hanging indent
  | pipe table |     -> bordered table (first row bold)
  ![caption](x.png)  -> centered embedded image + centered caption line

Inline markers: **bold**, _{subscript}, ^{superscript}.
Images are embedded as word/media/imageN.png with a document rels part;
only stdlib is used (PNG size parsed from the IHDR chunk).
"""
import sys, re, zipfile, struct
from pathlib import Path
from xml.sax.saxutils import escape

NS_W = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'
NS_R = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'
NS_WP = 'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'
NS_A = 'http://schemas.openxmlformats.org/drawingml/2006/main'
NS_PIC = 'http://schemas.openxmlformats.org/drawingml/2006/picture'
REL_NS = 'http://schemas.openxmlformats.org/package/2006/relationships'
REL_IMAGE = 'http://schemas.openxmlformats.org/officeDocument/2006/relationships/image'

MAX_W_EMU = 5_400_000   # 15 cm content width
MAX_H_EMU = 7_200_000   # 20 cm content height
EMU_PER_PX = 9525       # 96 dpi

CONTENT_TYPES = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Default Extension="png" ContentType="image/png"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>'''

RELS = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="%s">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>''' % REL_NS

BORDER = ('<w:tblBorders>'
          '<w:top w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
          '<w:left w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
          '<w:bottom w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
          '<w:right w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
          '<w:insideH w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
          '<w:insideV w:val="single" w:sz="4" w:space="0" w:color="000000"/>'
          '</w:tblBorders>')

TOKEN = re.compile(r'(\*\*.+?\*\*|_\{[^}]*\}|\^\{[^}]*\})')
IMAGE_RE = re.compile(r'^!\[(.*?)\]\((.+?)\)\s*$')


def png_size(path):
    """Return (width_px, height_px) from a PNG IHDR chunk."""
    with open(path, 'rb') as f:
        head = f.read(33)
    if head[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError(f'not a PNG: {path}')
    w, h = struct.unpack('>II', head[16:24])
    return w, h


def runs(text, size, bold_all=False, font='宋体'):
    out = []
    for tok in TOKEN.split(text):
        if not tok:
            continue
        bold, vert, body = bold_all, None, tok
        if tok.startswith('**') and tok.endswith('**') and len(tok) > 4:
            bold, body = True, tok[2:-2]
        elif tok.startswith('_{') and tok.endswith('}'):
            vert, body = 'subscript', tok[2:-1]
        elif tok.startswith('^{') and tok.endswith('}'):
            vert, body = 'superscript', tok[2:-1]
        if not body:
            continue
        rpr = f'<w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="{font}"/>'
        if bold:
            rpr += '<w:b/><w:bCs/>'
        rpr += f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>'
        if vert:
            rpr += f'<w:vertAlign w:val="{vert}"/>'
        rpr += '</w:rPr>'
        out.append(f'<w:r>{rpr}<w:t xml:space="preserve">{escape(body)}</w:t></w:r>')
    return ''.join(out)


def para(text, size=21, bold_all=False, font='宋体', align='both',
         indent=None, space_after=100, space_before=0):
    ppr = '<w:pPr>'
    if align:
        ppr += f'<w:jc w:val="{align}"/>'
    if indent:
        ppr += f'<w:ind w:firstLine="{indent}"/>'
    ppr += (f'<w:spacing w:before="{space_before}" w:after="{space_after}" '
            'w:line="300" w:lineRule="auto"/>')
    ppr += '</w:pPr>'
    return f'<w:p>{ppr}{runs(text, size, bold_all, font)}</w:p>'


def image_para(rid, cx, cy, pic_id):
    return (
        '<w:p><w:pPr><w:jc w:val="center"/>'
        '<w:spacing w:before="60" w:after="40" w:line="240" w:lineRule="auto"/></w:pPr>'
        '<w:r><w:drawing><wp:inline distT="0" distB="0" distL="0" distR="0">'
        f'<wp:extent cx="{cx}" cy="{cy}"/>'
        f'<wp:docPr id="{pic_id}" name="Picture {pic_id}"/>'
        f'<a:graphic><a:graphicData uri="{NS_PIC}">'
        f'<pic:pic><pic:nvPicPr><pic:cNvPr id="{pic_id}" name="image{pic_id}.png"/>'
        '<pic:cNvPicPr/></pic:nvPicPr>'
        f'<pic:blipFill><a:blip r:embed="{rid}"/><a:stretch><a:fillRect/></a:stretch></pic:blipFill>'
        '<pic:spPr><a:xfrm><a:off x="0" y="0"/>'
        f'<a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
        '<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></pic:spPr>'
        '</pic:pic></a:graphicData></a:graphic></wp:inline></w:drawing></w:r></w:p>')


def table(rows):
    ncols = max(len(r) for r in rows)
    width = int(9000 / ncols)
    grid = ''.join(f'<w:gridCol w:w="{width}"/>' for _ in range(ncols))
    xml = f'<w:tbl><w:tblPr><w:tblW w:w="9000" w:type="dxa"/>{BORDER}</w:tblPr><w:tblGrid>{grid}</w:tblGrid>'
    for ri, row in enumerate(rows):
        cells = ''
        for ci in range(ncols):
            cell = row[ci] if ci < len(row) else ''
            cells += (f'<w:tc><w:tcPr><w:tcW w:w="{width}" w:type="dxa"/></w:tcPr>'
                      + para(cell, 20, bold_all=(ri == 0), align='left', space_after=0) + '</w:tc>')
        xml += f'<w:tr>{cells}</w:tr>'
    xml += '</w:tbl>' + para('', space_after=80)
    return xml


def convert(md_path, docx_path):
    md_path = Path(md_path)
    body, media, warns = [], [], []
    lines = md_path.read_text(encoding='utf-8').split('\n')
    i = 0
    while i < len(lines):
        raw = lines[i].rstrip()
        line = raw.strip()
        m_img = IMAGE_RE.match(line)
        if m_img:
            caption, rel = m_img.group(1), m_img.group(2).strip().strip('<>')
            path = Path(rel)
            if not path.is_absolute():
                path = (md_path.parent / rel).resolve()
            if path.exists():
                try:
                    w_px, h_px = png_size(path)
                except Exception as exc:
                    warns.append(f'{rel}: {exc}')
                    i += 1
                    continue
                cx, cy = w_px * EMU_PER_PX, h_px * EMU_PER_PX
                scale = min(1.0, MAX_W_EMU / cx, MAX_H_EMU / cy)
                cx, cy = int(cx * scale), int(cy * scale)
                media.append((path, f'rId{100 + len(media)}'))
                body.append(image_para(f'rId{100 + len(media) - 1}', cx, cy, len(media)))
                if caption:
                    body.append(para(caption, 20, align='center', space_after=160))
            else:
                warns.append(f'图片不存在: {path}')
            i += 1
            continue
        if line.startswith('|') and i + 1 < len(lines) and re.match(r'^\|[\s:\-|]+\|$', lines[i + 1].strip()):
            rows = [[c.strip() for c in line.strip('|').split('|')]]
            i += 2
            while i < len(lines) and lines[i].strip().startswith('|'):
                rows.append([c.strip() for c in lines[i].strip().strip('|').split('|')])
                i += 1
            body.append(table(rows))
            continue
        if line == '' or line == '---':
            i += 1
            continue
        if line.startswith('$$') and line.endswith('$$') and len(line) > 4:
            body.append(para(line[2:-2].strip(), 21, align='center', space_after=120, space_before=60))
            i += 1
            continue
        m = re.match(r'^(#{1,4})\s+(.*)$', line)
        if m:
            lvl, txt = len(m.group(1)), m.group(2).strip()
            if lvl == 1:
                body.append(para(txt, 36, bold_all=True, font='黑体', align='center', space_after=260))
            elif lvl == 2:
                body.append(para(txt, 30, bold_all=True, font='黑体', align='left', space_before=180, space_after=140))
            elif lvl == 3:
                body.append(para(txt, 24, bold_all=True, font='黑体', align='left', space_before=120, space_after=110))
            else:
                body.append(para(txt, 21, bold_all=True, font='黑体', align='left', space_after=100))
            i += 1
            continue
        if re.match(r'^[-*]\s+', line) or re.match(r'^\d+\.\s+', line):
            body.append(para(re.sub(r'^[-*]\s+', '', line), 21, align='both', indent=None, space_after=80))
            i += 1
            continue
        body.append(para(line, 21, indent=420))
        i += 1

    sect = ('<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
            '<w:pgMar w:top="1440" w:right="1418" w:bottom="1440" w:left="1587" '
            'w:header="851" w:footer="992" w:gutter="0"/></w:sectPr>')
    ns = (f'xmlns:w="{NS_W}" xmlns:r="{NS_R}" xmlns:wp="{NS_WP}" '
          f'xmlns:a="{NS_A}" xmlns:pic="{NS_PIC}"')
    doc = (f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           f'<w:document {ns}><w:body>{"".join(body)}{sect}</w:body></w:document>')

    with zipfile.ZipFile(docx_path, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr('[Content_Types].xml', CONTENT_TYPES)
        z.writestr('_rels/.rels', RELS)
        z.writestr('word/document.xml', doc)
        if media:
            rels = ''.join(
                f'<Relationship Id="{rid}" Type="{REL_IMAGE}" Target="media/{p.name}"/>'
                for p, rid in media)
            z.writestr('word/_rels/document.xml.rels',
                       '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
                       f'<Relationships xmlns="{REL_NS}">{rels}</Relationships>')
            for p, _ in media:
                z.writestr(f'word/media/{p.name}', p.read_bytes())
    print(f'{docx_path}: blocks={len(body)}, images={len(media)}, xml={len(doc)} chars')
    for w in warns:
        print(f'WARNING: {w}')


if __name__ == '__main__':
    convert(sys.argv[1], sys.argv[2])

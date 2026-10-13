# -*- coding: utf-8 -*-
"""Extract ordered text (paragraphs + tables) from .docx using stdlib only."""
import sys, zipfile, re
import xml.etree.ElementTree as ET

NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}

def para_text(p):
    parts = []
    for node in p.iter():
        tag = node.tag.split('}')[-1]
        if tag == 't' and node.text:
            parts.append(node.text)
        elif tag in ('br', 'cr'):
            parts.append('\n')
        elif tag == 'tab':
            parts.append('\t')
    return ''.join(parts)

def extract(path, out_path):
    z = zipfile.ZipFile(path)
    xml_bytes = z.read('word/document.xml')
    root = ET.fromstring(xml_bytes)
    body = root.find('w:body', NS)
    lines = []
    for child in body:
        tag = child.tag.split('}')[-1]
        if tag == 'p':
            t = para_text(child).strip()
            if t:
                lines.append(t)
        elif tag == 'tbl':
            lines.append('【表格开始】')
            for row in child.findall('w:tr', NS):
                cells = []
                for tc in row.findall('w:tc', NS):
                    cell_parts = []
                    for p in tc.findall('w:p', NS):
                        pt = para_text(p).strip()
                        if pt:
                            cell_parts.append(pt)
                    cells.append(' / '.join(cell_parts))
                lines.append(' | '.join(cells))
            lines.append('【表格结束】')
    text = '\n'.join(lines)
    with open(out_path, 'w', encoding='utf-8') as f:
        f.write(text)
    print(f'{out_path}: {len(text)} chars, {len(lines)} lines')

if __name__ == '__main__':
    extract(sys.argv[1], sys.argv[2])

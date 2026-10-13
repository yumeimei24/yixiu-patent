# -*- coding: utf-8 -*-
"""Programmatic figure review for patent drawings (substitute for eyeballing).

Checks, per drawing in a paper2patent figure-spec JSON:
  1. the SVG exists and contains every node label and edge label from the spec;
  2. no text inside the figure looks like a figure number (图1 …) — forbidden on the sheet;
  3. the PNG exists, is a real PNG, is not blank, and reports size / grayscale range;
  4. flags SVG text whose font-size is too small (< 8 pt equivalent at 1:1) as a warning.

Usage:
    python verify_figures.py <spec.json> <figure_dir> <prefix> [--json-out report.json]

Exit code 1 if any error-level problem is found. This tool cannot judge aesthetics,
overlaps or arrow directions — a human must still look at the PNGs.
"""
import argparse
import json
import re
import struct
import sys
from pathlib import Path
from xml.sax.saxutils import unescape

TEXT_RE = re.compile(r'<text[^>]*>(.*?)</text>', re.S)
FONTSIZE_RE = re.compile(r'font-size\s*[:=]\s*"?([\d.]+)')
FIGNUM_RE = re.compile(r'图\s*\d')


def png_info(path):
    raw = path.read_bytes()
    if raw[:8] != b'\x89PNG\r\n\x1a\n':
        return None
    w, h = struct.unpack('>II', raw[16:24])
    return {'bytes': len(raw), 'width': w, 'height': h}


def svg_texts(path):
    svg = path.read_text(encoding='utf-8', errors='replace')
    out = []
    for raw in TEXT_RE.findall(svg):
        txt = unescape(re.sub(r'<[^>]+>', '', raw)).strip()
        if txt:
            out.append(txt)
    return svg, out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('spec')
    ap.add_argument('figdir')
    ap.add_argument('prefix')
    ap.add_argument('--json-out')
    args = ap.parse_args()

    spec = json.loads(Path(args.spec).read_text(encoding='utf-8'))
    figdir = Path(args.figdir)
    rows, errors, warnings = [], [], []

    for d in spec.get('drawings', []):
        no = d.get('figure_no')
        stem = f'{args.prefix}_图{no}'
        svg_path, png_path = figdir / f'{stem}.svg', figdir / f'{stem}.png'
        row = {'figure': no, 'title': d.get('title', ''), 'nodes': len(d.get('nodes', [])),
               'edges': len(d.get('edges', []))}

        if not svg_path.exists():
            errors.append(f'图{no}: SVG 缺失 {svg_path}')
            row['svg'] = 'missing'
        else:
            _, texts = svg_texts(svg_path)
            # 引擎会把长标签换行拆成多个 text 元素，比对前去掉全部空白
            joined = re.sub(r'\s+', '', ''.join(texts))
            missing = [n['label'] for n in d.get('nodes', [])
                       if n.get('label') and re.sub(r'\s+', '', n['label']) not in joined]
            edge_labels = [e['label'] for e in d.get('edges', [])
                           if isinstance(e, dict) and e.get('label')]
            missing_edges = [lb for lb in edge_labels
                             if re.sub(r'\s+', '', lb) not in joined]
            if missing:
                errors.append(f'图{no}: SVG 缺少节点标签 {missing}')
            if missing_edges:
                warnings.append(f'图{no}: SVG 缺少边标签 {missing_edges}')
            bad = [t for t in texts if FIGNUM_RE.search(t)]
            if bad:
                errors.append(f'图{no}: 图内出现图号字样 {bad}')
            small = [t for t in texts if (m := FONTSIZE_RE.search(t)) and float(m.group(1)) < 8]
            if small:
                warnings.append(f'图{no}: 字号偏小 {small[:3]}')
            row.update({'svg': 'ok', 'svg_texts': len(texts),
                        'missing_labels': missing, 'missing_edge_labels': missing_edges})

        info = png_info(png_path) if png_path.exists() else None
        if not info:
            errors.append(f'图{no}: PNG 缺失或非法 {png_path}')
            row['png'] = 'missing'
        else:
            try:
                import numpy as np
                from PIL import Image
                im = Image.open(png_path)
                lo, hi = im.convert('L').getextrema()
                arr = np.asarray(im.convert('L'))
                dark = float((arr < 128).mean())
                row.update({'png': 'ok', 'size': f'{im.width}x{im.height}', 'mode': im.mode,
                            'range': [lo, hi], 'ink_ratio': round(dark, 4)})
                if lo == hi:
                    errors.append(f'图{no}: PNG 全白或全黑（空白图）')
                if not (0.002 <= dark <= 0.35):
                    warnings.append(f'图{no}: 着墨比例 {dark:.3f} 异常，请人工目视')
            except ImportError:
                row.update({'png': 'ok', 'size': f"{info['width']}x{info['height']}"})
                warnings.append('未安装 Pillow，跳过像素级检查')
        rows.append(row)

    for r in rows:
        print(f"图{r['figure']}: nodes={r['nodes']} edges={r['edges']} svg={r.get('svg')} "
              f"png={r.get('png')} {r.get('size','')} {r.get('mode','')} "
              f"range={r.get('range','')} ink={r.get('ink_ratio','')}")
    for w in warnings:
        print(f'WARNING: {w}')
    for e in errors:
        print(f'ERROR: {e}')
    print(f'checked {len(rows)} figures: {len(errors)} errors, {len(warnings)} warnings '
          f'(aesthetic review by a human is still required)')
    if args.json_out:
        Path(args.json_out).write_text(
            json.dumps({'figures': rows, 'errors': errors, 'warnings': warnings},
                       ensure_ascii=False, indent=2), encoding='utf-8')
    return 1 if errors else 0


if __name__ == '__main__':
    sys.exit(main())

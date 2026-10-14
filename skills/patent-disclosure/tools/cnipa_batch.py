#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""CNIPA 公布公告站批量检索，输出 UTF-8 摘要（规避 Windows GBK 控制台截断）。

用法：
    python tools/cnipa_batch.py 关键词1 关键词2 关键词3
输出：
    cnipa_summary.txt  —— 人读摘要（关键词 / 公开号 / 标题 / 摘要前 220 字）
    cnipa_hits.json    —— 结构化结果，便于二次筛选

约定：
    * 公布站首页对多词按"同时包含"（AND）理解，词多且专时极易 0 条，**每个参数建议只给一个词或极短短语**；
    * 每个词各起一次浏览器会话，逐词检索后按公开号合并；
    * 需要整句一次提交或落盘结果页 HTML 时，改用 cnipa_epub_crawler.py。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cnipa_epub_crawler import search_epub_keyword  # noqa: E402


def _field(hit, name, default=''):
    if isinstance(hit, dict):
        return hit.get(name, default)
    return getattr(hit, name, default)


def main(argv=None):
    terms = argv if argv is not None else sys.argv[1:]
    if not terms:
        print(__doc__.strip(), file=sys.stderr)
        return 2
    out, lines, total = {}, [], 0
    for term in terms:
        try:
            _html, hits = search_epub_keyword(term)
        except Exception as exc:  # 单组失败不影响其它组
            hits = []
            lines.append(f'== {term} :: ERROR {type(exc).__name__}: {exc}')
        rows = []
        for h in hits:
            row = {k: _field(h, k) for k in ('title', 'pub_number', 'link', 'abstract')}
            rows.append(row)
            lines.append(f"  {row['pub_number']} | {row['title']}")
            abstract = (row.get('abstract') or '').replace('\n', ' ')
            lines.append(f"      {abstract[:220]}")
        out[term] = rows
        total += len(rows)
        lines.insert(len(lines) - 2 * len(rows), f'== {term} :: {len(rows)} hits')
    base = os.getcwd()
    with open(os.path.join(base, 'cnipa_hits.json'), 'w', encoding='utf-8') as fh:
        json.dump(out, fh, ensure_ascii=False, indent=1)
    with open(os.path.join(base, 'cnipa_summary.txt'), 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(lines) + '\n')
    print(f'terms={len(terms)} hits={total} -> cnipa_summary.txt / cnipa_hits.json')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())

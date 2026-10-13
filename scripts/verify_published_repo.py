#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Verify a published repo against the local folder it was published from.

Checks: repo metadata, commit authors (email/name exposure), file-by-file git blob
SHA-1 equality, missing/extra files, and accidental leakage (tokens, outputs/,
caches, generated figures).

Usage:
    python scripts/verify_published_repo.py yumeimei24/yixiu-patent yixiu-patent [branch]
"""
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path

API = 'https://api.github.com'
SKIP_DIRS = {'.git', '__pycache__', 'out', '.venv', 'venv'}


def get(path, raw=False):
    req = urllib.request.Request(API + path if not path.startswith('http') else path,
                                 headers={'User-Agent': 'verify/1.0',
                                          'Accept': 'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = resp.read()
    return data if raw else json.loads(data.decode('utf-8'))


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def local_files(root: Path):
    out = {}
    for p in sorted(root.rglob('*')):
        if p.is_dir() or any(part in SKIP_DIRS for part in p.parts):
            continue
        if p.suffix in ('.pyc', '.pyo'):
            continue
        out[p.relative_to(root).as_posix()] = p
    return out


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        return 2
    repo, localdir = sys.argv[1], Path(sys.argv[2])
    branch = sys.argv[3] if len(sys.argv) > 3 else None

    info = get(f'/repos/{repo}')
    branch = branch or info['default_branch']
    print(f"repo      : {info['full_name']}  ({'private' if info['private'] else 'public'})")
    print(f"url       : {info['html_url']}")
    print(f"branch    : {branch}   license: {(info.get('license') or {}).get('spdx_id')}")
    print(f"size      : {info['size']} KiB   pushed: {info['pushed_at']}")

    print('\n-- commits (author exposure) --')
    for c in get(f'/repos/{repo}/commits?per_page=5'):
        a = c['commit']['author']
        print(f"  {c['sha'][:8]}  {a['date']}  name={a['name']!r}  email={a['email']!r}")
        print(f"            msg: {c['commit']['message'].splitlines()[0][:90]}")

    tree = get(f'/repos/{repo}/git/trees/{branch}?recursive=1')['tree']
    remote = {e['path']: e['sha'] for e in tree if e['type'] == 'blob'}
    local = local_files(localdir)
    print(f'\n-- files -- remote {len(remote)}, local {len(local)}')

    missing = sorted(set(local) - set(remote))
    extra = sorted(set(remote) - set(local))
    differs = []
    for path in sorted(set(local) & set(remote)):
        if git_blob_sha1(local[path].read_bytes()) != remote[path]:
            differs.append(path)

    for label, items in (('MISSING on remote', missing), ('EXTRA on remote', extra),
                         ('DIFFERS (content)', differs)):
        print(f'  {label}: {len(items)}')
        for p in items[:20]:
            print(f'     - {p}')

    print('\n-- leakage scan (remote paths) --')
    suspicious = [p for p in remote if any(k in p.lower() for k in
                  ('token', 'secret', 'credential', '.env', 'outputs/', 'gh_token',
                   '__pycache__', '.pyc', 'examples/out'))]
    print(f'  suspicious paths: {len(suspicious)}')
    for p in suspicious[:20]:
        print(f'     ! {p}')

    ok = not (missing or extra or differs or suspicious)
    print(f"\nRESULT: {'OK — remote matches local exactly, no leakage' if ok else 'PROBLEMS FOUND (see above)'}")
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())

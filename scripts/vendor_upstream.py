#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vendor or verify upstream skill files over HTTPS (stdlib only).

Why this exists: on some locked-down Windows hosts, `git`, `curl` and
`Invoke-WebRequest` have no egress while `python`/`urllib` does. This helper walks a
repo with the GitHub contents API, downloads the files you list, and verifies each
blob's SHA-1 so a truncated or proxy-mangled response cannot pass silently.

Usage:
    python scripts/vendor_upstream.py list   <owner/repo> <ref> [path-prefix ...]
    python scripts/vendor_upstream.py fetch  <owner/repo> <ref> <outdir> [path-prefix ...]
    python scripts/vendor_upstream.py check  <owner/repo> <ref> <localdir> [path-prefix ...]

Notes:
  * `list`  prints "<path>\t<size>\t<sha1>" for every blob under the prefixes.
  * `fetch` writes files, skipping any whose size already matches upstream, and prints
    a comparison table. Files you have modified locally will be reported, not clobbered,
    unless you pass --force.
  * `check` re-hashes local files against upstream git blob SHAs (git blob SHA-1 =
    sha1(b"blob %d\\0" % len(data) + data)), so it works without git installed.
  * Rate limits: unauthenticated GitHub API allows ~60 requests/hour. Export
    GITHUB_TOKEN to raise it.
"""
import base64
import hashlib
import json
import os
import sys
import urllib.request
from pathlib import Path

API = 'https://api.github.com/repos/{repo}/contents/{path}?ref={ref}'


def get_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': 'vendor-upstream/1.0'})
    token = os.environ.get('GITHUB_TOKEN')
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))


def walk(repo, ref, prefix=''):
    """Depth-first listing of blobs; recurses into subdirectories."""
    url = API.format(repo=repo, path=prefix, ref=ref)
    try:
        entries = get_json(url)
    except urllib.error.HTTPError as exc:  # noqa: PERF203 - report and continue
        print(f'  ! {prefix or "/"}: HTTP {exc.code}', file=sys.stderr)
        return []
    if isinstance(entries, dict):                     # a single file
        entries = [entries]
    out = []
    for e in entries:
        if e['type'] == 'dir':
            out += walk(repo, ref, e['path'])
        elif e['type'] == 'file':
            out.append(e)
    return out


def blob_files(repo, ref, prefixes):
    files = {}
    for p in prefixes or ['']:
        for e in walk(repo, ref, p):
            files[e['path']] = e
    return files


def git_blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b'blob %d\0' % len(data) + data).hexdigest()


def blob_bytes(repo, ref, path):
    d = get_json(API.format(repo=repo, path=path, ref=ref))
    return base64.b64decode(d['content']), d['sha']


def main(argv):
    if len(argv) < 4:
        print(__doc__)
        return 2
    mode, repo, ref = argv[1], argv[2], argv[3]
    args = [a for a in argv[4:] if not a.startswith('--')]
    force = '--force' in argv

    if mode == 'list':
        files = blob_files(repo, ref, args)
        for path, e in sorted(files.items()):
            print(f"{path}\t{e['size']}\t{e['sha']}")
        print(f'-- {len(files)} files')
        return 0

    if mode == 'fetch':
        if not args:
            print('fetch needs an output directory', file=sys.stderr)
            return 2
        outdir, prefixes = Path(args[0]), args[1:]
        files = blob_files(repo, ref, prefixes)
        same = changed = added = 0
        for path, e in sorted(files.items()):
            target = outdir / path
            target.parent.mkdir(parents=True, exist_ok=True)
            if target.exists() and target.stat().st_size == e['size'] and not force:
                same += 1
                continue
            data, sha = blob_bytes(repo, ref, path)
            if git_blob_sha1(data) != sha:
                print(f'  ! SHA-1 mismatch, skipped: {path}', file=sys.stderr)
                continue
            state = 'updated' if target.exists() else 'added'
            target.write_bytes(data)
            if state == 'updated':
                changed += 1
            else:
                added += 1
            print(f'  {state}: {path} ({len(data)} B)')
        print(f'-- {added} added, {changed} updated, {same} unchanged (size match), {len(files)} total')
        return 0

    if mode == 'check':
        if not args:
            print('check needs the local directory', file=sys.stderr)
            return 2
        localdir, prefixes = Path(args[0]), args[1:]
        files = blob_files(repo, ref, prefixes)
        missing, differs, ok = [], [], 0
        for path, e in sorted(files.items()):
            target = localdir / path
            if not target.exists():
                missing.append(path)
                continue
            if git_blob_sha1(target.read_bytes()) == e['sha']:
                ok += 1
            else:
                differs.append(path)
        print(f'identical: {ok}')
        for p in differs:
            print(f'differs (locally modified): {p}')
        for p in missing:
            print(f'missing: {p}')
        return 0

    print(f'unknown mode: {mode}', file=sys.stderr)
    return 2


if __name__ == '__main__':
    sys.exit(main(sys.argv))

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Install / update the yixiu-patent skills from the published GitHub repo.

Downloads the repo tarball (single request, stdlib only), extracts `skills/*`, and
installs each skill into the local agent skill directory. Existing directories are
backed up to an archive directory first, so nothing is lost. Use it both for the
first install and for later updates:

    python scripts/sync_yixiu_skills.py
    python scripts/sync_yixiu_skills.py --repo yumeimei24/yixiu-patent --branch main \
        --skills-dir ".dsh/skills" --retire patent-skills

Notes:
  * public repo -> anonymous download works; export GITHUB_TOKEN for a private repo.
  * extraction is path-traversal checked.
"""
import argparse
import io
import json
import os
import shutil
import sys
import tarfile
import time
import urllib.request
from pathlib import Path

TARBALL = 'https://codeload.github.com/{repo}/tar.gz/refs/heads/{branch}'


def download(repo, branch, token=None):
    url = TARBALL.format(repo=repo, branch=branch)
    req = urllib.request.Request(url, headers={'User-Agent': 'sync-yixiu/1.0'})
    if token:
        req.add_header('Authorization', f'Bearer {token}')
    with urllib.request.urlopen(req, timeout=120) as resp:
        return resp.read()


def extract_skills(blob, skills_dir_out: Path):
    """Extract <root>/skills/<name>/... into skills_dir_out/<name>/..."""
    written = []
    with tarfile.open(fileobj=io.BytesIO(blob), mode='r:gz') as tar:
        for member in tar.getmembers():
            parts = Path(member.name).parts
            if len(parts) < 3 or parts[1] != 'skills':
                continue
            rel = Path(*parts[2:])                       # <skill>/...
            target = (skills_dir_out / rel).resolve()
            if not str(target).startswith(str(skills_dir_out.resolve())):
                raise SystemExit(f'unsafe path in tarball: {member.name}')
            if member.isdir():
                target.mkdir(parents=True, exist_ok=True)
                continue
            target.parent.mkdir(parents=True, exist_ok=True)
            src = tar.extractfile(member)
            if src is None:
                continue
            target.write_bytes(src.read())
            written.append(rel.as_posix())
    return written


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--repo', default='yumeimei24/yixiu-patent')
    ap.add_argument('--branch', default='main')
    ap.add_argument('--skills-dir', default=r'.dsh/skills')
    ap.add_argument('--archive-dir', default=r'.dsh/skills-archive')
    ap.add_argument('--retire', action='append', default=[],
                    help='existing skill dir to move into the archive (repeatable)')
    args = ap.parse_args()

    root = Path.cwd()
    skills_dir = root / args.skills_dir
    archive = root / args.archive_dir
    staging = root / '.dsh' / '_yixiu_staging'
    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    print(f'downloading {args.repo}@{args.branch} ...')
    blob = download(args.repo, args.branch, os.environ.get('GITHUB_TOKEN'))
    print(f'  tarball: {len(blob) / 1024:.1f} KiB')
    written = extract_skills(blob, staging)
    skills = sorted({p.split('/')[0] for p in written})
    print(f'  skills in package: {skills} ({len(written)} files)')

    stamp = time.strftime('%Y%m%d%H%M%S')
    skills_dir.mkdir(parents=True, exist_ok=True)
    archive.mkdir(parents=True, exist_ok=True)

    installed = []
    for name in skills:
        src = staging / name
        dst = skills_dir / name
        if dst.exists():
            back = archive / f'{name}_{stamp}'
            shutil.move(str(dst), str(back))
            print(f'  backed up existing {name} -> {back.relative_to(root)}')
        shutil.copytree(src, dst)
        n = sum(1 for _ in dst.rglob('*') if _.is_file())
        installed.append((name, n))
        print(f'  installed {name} ({n} files)')

    for name in args.retire:
        old = skills_dir / name
        if old.exists():
            back = archive / f'{name}_{stamp}'
            shutil.move(str(old), str(back))
            print(f'  retired {name} -> {back.relative_to(root)}')

    shutil.rmtree(staging)
    manifest = {
        'repo': args.repo, 'branch': args.branch, 'synced_at': stamp,
        'skills': [{'name': n, 'files': c} for n, c in installed],
        'retired': args.retire,
    }
    (skills_dir / '.yixiu-manifest.json').write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8', newline='\n')
    print('manifest written: .dsh/skills/.yixiu-manifest.json')
    return 0


if __name__ == '__main__':
    sys.exit(main())

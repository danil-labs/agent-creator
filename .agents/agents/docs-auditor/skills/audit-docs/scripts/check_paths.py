#!/usr/bin/env python
"""Lists repository paths cited by Markdown files that do not exist.

Usage:
    python check_paths.py --root <repository> [file.md ...]

Without files, it checks every *.md under the root (skipping .git and
node_modules). A cited path is a backticked token that looks like a path, or
the target of a relative Markdown link. It is resolved against the file's own
folder and against the root. Exit status: 1 if any path is missing.
Standard library only.
"""
import argparse
import os
import re
import sys

TICK = re.compile(r'`([^`\s]+)`')
LINK = re.compile(r'\]\(([^)\s]+)(?:\s+"[^"]*")?\)')
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})')
SKIP_DIRS = {'.git', 'node_modules', '.venv', 'venv', '__pycache__', 'target', 'dist'}


def candidate(token):
    token = token.split('#', 1)[0].rstrip('.,:;)')
    if not token or token.startswith(('http:', 'https:', 'mailto:', 'www.', '@', '/', '~', '$', '-')):
        return None
    if any(c in token for c in '<>*{}|…'):
        return None
    if '/' not in token:
        return None
    if not (token.endswith('/') or re.search(r'\.[A-Za-z0-9]+$', token) or token.startswith('.')):
        return None
    return token


def cited(path):
    in_fence = False
    with open(path, encoding='utf-8-sig', errors='replace') as f:
        for number, line in enumerate(f, 1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            for token in TICK.findall(line) + LINK.findall(line):
                c = candidate(token)
                if c:
                    yield number, c


def markdown_files(root):
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = sorted(d for d in dirnames if d not in SKIP_DIRS)
        for name in sorted(filenames):
            if name.lower().endswith('.md'):
                yield os.path.join(dirpath, name)


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description='Lists cited paths that do not exist')
    p.add_argument('--root', default='.', help='repository root')
    p.add_argument('files', nargs='*', help='Markdown files; default: all under the root')
    a = p.parse_args()

    root = os.path.abspath(a.root)
    files = [os.path.abspath(f) for f in a.files] or list(markdown_files(root))
    missing = 0
    for path in files:
        base = os.path.dirname(path)
        for number, token in cited(path):
            if not (os.path.exists(os.path.join(base, token)) or os.path.exists(os.path.join(root, token))):
                missing += 1
                print(f'{os.path.relpath(path, root)}:{number}  {token}')
    print(f'{missing} missing path(s) in {len(files)} file(s)', file=sys.stderr)
    return 1 if missing else 0


if __name__ == '__main__':
    sys.exit(main())

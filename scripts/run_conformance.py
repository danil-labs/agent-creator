#!/usr/bin/env python
"""Runs the conformance corpus (conformance/cases/) against a reader of the format.

Usage:
    python scripts/run_conformance.py                          # against scripts/validate_agent.py
    python scripts/run_conformance.py --profile format         # only the cases a harness must pass
    python scripts/run_conformance.py --command "<reader>"     # against another implementation
    python scripts/run_conformance.py --case 011               # only the cases whose folder starts with 011

A reader under test is a command that accepts `--root <dir>`, the case's extra
arguments (for example `--strict`) and `--json`, and prints the report described
in conformance/README.md. For each agent, the verdict and the multiset of codes
must match expected.json exactly.

Exit status: 0 when every selected case passes, 1 otherwise.
Standard library only.
"""
import argparse
import json
import os
import shlex
import subprocess
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
CASES = os.path.join(REPO, 'conformance', 'cases')


def run_case(command, case_dir, expected):
    args = command + ['--root', os.path.join(case_dir, 'input')] + expected.get('args', []) + ['--json']
    proc = subprocess.run(args, capture_output=True, text=True, encoding='utf-8')
    try:
        report = json.loads(proc.stdout)
    except json.JSONDecodeError:
        return [f'the reader did not print JSON (exit {proc.returncode}): {proc.stderr.strip() or proc.stdout.strip()}']

    problems = []
    got = {a['name']: a for a in report.get('agents', [])}
    want = expected['agents']
    for name in sorted(set(want) - set(got)):
        problems.append(f'{name}: expected in the report, missing')
    for name in sorted(set(got) - set(want)):
        problems.append(f'{name}: in the report, not expected')
    for name in sorted(set(want) & set(got)):
        w, g = want[name], got[name]
        if w['verdict'] != g.get('verdict'):
            problems.append(f'{name}: verdict {g.get("verdict")!r}, expected {w["verdict"]!r}')
        got_codes = Counter(d['code'] for d in g.get('diagnostics', []))
        want_codes = Counter(w['codes'])
        if got_codes != want_codes:
            extra = sorted((got_codes - want_codes).elements())
            missing = sorted((want_codes - got_codes).elements())
            detail = []
            if missing:
                detail.append('missing ' + ', '.join(missing))
            if extra:
                detail.append('unexpected ' + ', '.join(extra))
            problems.append(f'{name}: codes differ: {"; ".join(detail)}')
    failed = any(a.get('verdict') == 'fail' for a in report.get('agents', []))
    if proc.returncode != (1 if failed else 0):
        problems.append(f'exit status {proc.returncode}, expected {1 if failed else 0}')
    return problems


def main():
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description='Runs the conformance corpus against a reader')
    p.add_argument('--command', help='reader to test; defaults to scripts/validate_agent.py')
    p.add_argument('--profile', choices=['format', 'authoring', 'all'], default='all',
                   help='format: what every harness must match; authoring: validator lint; all: both')
    p.add_argument('--case', help='only run cases whose folder name starts with this prefix')
    a = p.parse_args()

    command = shlex.split(a.command, posix=os.name != 'nt') if a.command else \
        [sys.executable, os.path.join(HERE, 'validate_agent.py')]
    cases = sorted(d for d in os.listdir(CASES) if os.path.isdir(os.path.join(CASES, d)))
    if a.case:
        cases = [c for c in cases if c.startswith(a.case)]

    passed = failed = skipped = 0
    for case in cases:
        case_dir = os.path.join(CASES, case)
        with open(os.path.join(case_dir, 'expected.json'), encoding='utf-8') as f:
            expected = json.load(f)
        if a.profile != 'all' and expected.get('profile', 'format') != a.profile:
            skipped += 1
            continue
        problems = run_case(command, case_dir, expected)
        if problems:
            failed += 1
            print(f'FAIL  {case}')
            for problem in problems:
                print(f'      {problem}')
        else:
            passed += 1
            print(f'ok    {case}')
    print(f'\n{passed + failed} cases: {passed} passed, {failed} failed' + (f', {skipped} skipped (profile)' if skipped else ''))
    return 1 if failed or not passed else 0


if __name__ == '__main__':
    sys.exit(main())

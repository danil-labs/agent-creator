#!/usr/bin/env python
"""Validates a repository's agents against SPEC.md.

Usage:
    python scripts/validate_agent.py --root <repository>     # reads <repository>/.agents/agents/
    python scripts/validate_agent.py --agents <folder>       # reads <folder>/<name>/agent.md
    python scripts/validate_agent.py ... --no-paths          # does not check that cited paths exist

Exits with 1 if there is any ERROR. WARNINGs do not change the exit code.
Uses the standard library only.
"""
import argparse
import os
import re
import sys

NAME = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
MAX_NAME = 60
RESERVED = {'con', 'prn', 'aux', 'nul'} | {f'com{i}' for i in range(1, 10)} | {f'lpt{i}' for i in range(1, 10)}
FIELDS = {'name', 'description'}
TOLERATED_FIELDS = {'tools', 'model'}

# Sections an agent should have. Each accepts several headings, in English or in Spanish.
SECTIONS = [
    ('What you work with', re.compile(r'^(what you \w+ with|the contracts you check|files|con qu[eé]\b)', re.I)),
    ('How you work', re.compile(r'^(how you (?!report)\w+|what you look for|c[oó]mo (?!reportas)\w+)', re.I)),
    ('Where you stop', re.compile(r'^(where you stop|how far you go|how you hand off|hasta d[oó]nde llegas)', re.I)),
    ('What you report', re.compile(r'^(what you report|how you report|qu[eé] reportas)', re.I)),
    ('What you have learned', re.compile(r'^(what you have learned|lo que has aprendido)', re.I)),
]

PATH = re.compile(r'`([^`\s]+)`')
MENTION = re.compile(r'(?<![\w.@])@([a-z0-9]+(?:-[a-z0-9]+)*)')


def read(path):
    with open(path, encoding='utf-8-sig') as f:
        return f.read().replace('\r\n', '\n')


def frontmatter(text):
    """Returns (fields, body), or (None, text) if there is no frontmatter."""
    if not text.startswith('---\n'):
        return None, text
    end = text.find('\n---', 4)
    if end == -1:
        return None, text
    block, body = text[4:end], text[end + 4:].lstrip('\n')
    fields, key = {}, None
    for line in block.split('\n'):
        m = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            fields[key] = '' if value in ('>', '|', '>-', '|-') else value.strip('"\'')
        elif key and (line.startswith(' ') or line.startswith('\t')):
            fields[key] = (fields[key] + ' ' + line.strip()).strip()
    return fields, body


def looks_like_path(token):
    token = token.rstrip('.,:;)')
    if not token or token[0] in '@/' or token.startswith(('http', 'www.')):
        return None
    if any(c in token for c in '<>*{}…|') or '/' not in token:
        return None
    if not (token.endswith('/') or re.search(r'\.[A-Za-z0-9]+$', token) or token.startswith('.')):
        return None
    return token


def validate_name(name, folder, findings):
    if not name:
        findings.append('ERROR: `name` is missing from the frontmatter')
        return
    if not NAME.match(name):
        findings.append(f'ERROR: `name: {name}` is not ASCII kebab-case (lowercase letters, digits and single hyphens)')
    if len(name) > MAX_NAME:
        findings.append(f'ERROR: `name` has {len(name)} characters; the maximum is {MAX_NAME}')
    if name in RESERVED:
        findings.append(f'ERROR: `{name}` is a reserved name on Windows')
    if name != folder:
        findings.append(f'ERROR: `name: {name}` does not match its folder `{folder}/`')


def validate_skills(agent_dir, findings):
    skills_dir = os.path.join(agent_dir, 'skills')
    if not os.path.isdir(skills_dir):
        return
    for skill in sorted(os.listdir(skills_dir)):
        skill_dir = os.path.join(skills_dir, skill)
        if not os.path.isdir(skill_dir):
            continue
        skill_file = os.path.join(skill_dir, 'SKILL.md')
        if not os.path.isfile(skill_file):
            findings.append(f'ERROR: the skill `skills/{skill}/` has no SKILL.md')
            continue
        fields, _ = frontmatter(read(skill_file))
        if fields is None:
            findings.append(f'ERROR: `skills/{skill}/SKILL.md` has no frontmatter')
            continue
        if fields.get('name') != skill:
            findings.append(f'ERROR: `skills/{skill}/SKILL.md` declares `name: {fields.get("name")}`, which differs from its folder')
        if not fields.get('description'):
            findings.append(f'ERROR: `skills/{skill}/SKILL.md` has no `description`')


def validate_agent(agent_dir, root, declared, check_paths):
    folder = os.path.basename(agent_dir)
    agent_file = os.path.join(agent_dir, 'agent.md')
    findings = []
    if not os.path.isfile(agent_file):
        return [f'ERROR: `{folder}/` has no agent.md']
    fields, body = frontmatter(read(agent_file))
    if fields is None:
        return ['ERROR: agent.md does not start with frontmatter (---)']

    validate_name(fields.get('name', ''), folder, findings)
    description = fields.get('description', '')
    if not description:
        findings.append('ERROR: `description` is missing: say when the agent is used and what it does not do')
    elif len(description) > 1024:
        findings.append(f'WARNING: the description has {len(description)} characters; more than 1024 is usually the method, not the when')
    for field in fields:
        if field in TOLERATED_FIELDS:
            findings.append(f'WARNING: `{field}` ties the agent to a CLI; the spec recommends omitting it')
        elif field not in FIELDS:
            findings.append(f'ERROR: `{field}` is not a frontmatter field; only `name` and `description`')

    if not body.strip():
        findings.append('ERROR: the body is empty; without instructions the agent is a name without judgment')
        return findings

    headings = [l.lstrip('#').strip() for l in body.split('\n') if re.match(r'^#{2,3} ', l)]
    for section_name, pattern in SECTIONS:
        if not any(pattern.match(h) for h in headings):
            findings.append(f'WARNING: there is no «{section_name}» section')

    first = next((l for l in body.split('\n') if l.strip()), '')
    if first.startswith('#'):
        findings.append('WARNING: the body does not start with the role: one or two sentences on what you do and what you do not')

    for mention in sorted(set(MENTION.findall(body))):
        if mention not in declared:
            findings.append(f'ERROR: `@{mention}` is not a declared agent')

    if check_paths:
        seen = set()
        for token in PATH.findall(body):
            path = looks_like_path(token)
            if not path or path in seen:
                continue
            seen.add(path)
            if not (os.path.exists(os.path.join(root, path)) or os.path.exists(os.path.join(agent_dir, path))):
                findings.append(f'ERROR: the path `{path}` does not exist')

    validate_skills(agent_dir, findings)
    return findings


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description='Validates agents against SPEC.md')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--root', help='repository root; reads <root>/.agents/agents/')
    g.add_argument('--agents', help='folder that contains <name>/agent.md')
    p.add_argument('--no-paths', action='store_true', help='do not check that cited paths exist')
    a = p.parse_args()

    root = os.path.abspath(a.root or '.')
    agents_dir = os.path.join(root, '.agents', 'agents') if a.root else os.path.abspath(a.agents)
    if not os.path.isdir(agents_dir):
        print(f'ERROR: {agents_dir} does not exist')
        return 1

    agents = sorted(d for d in os.listdir(agents_dir) if os.path.isdir(os.path.join(agents_dir, d)))
    declared = set(agents)
    total_errors = 0
    for name in agents:
        findings = validate_agent(os.path.join(agents_dir, name), root, declared, not a.no_paths)
        errors = [f for f in findings if f.startswith('ERROR')]
        total_errors += len(errors)
        print(f'{"OK   " if not errors else "FAIL "} {name}')
        for f in findings:
            print(f'      {f}')
    print(f'\n{len(agents)} agents, {total_errors} errors')
    return 1 if total_errors else 0


if __name__ == '__main__':
    sys.exit(main())

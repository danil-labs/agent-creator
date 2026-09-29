#!/usr/bin/env python
"""Validates the agents declared in a repository against SPEC.md (Agent Declaration Format v1).

Usage:
    python scripts/validate_agent.py --root <repository>     # reads <repository>/.agents/agents/
    python scripts/validate_agent.py --agents <folder>       # reads <folder>/<name>/agent.md
    python scripts/validate_agent.py ... --no-paths          # does not check that cited paths exist
    python scripts/validate_agent.py ... --strict            # warnings count as errors (use it to publish)
    python scripts/validate_agent.py ... --json              # machine-readable report on stdout

Exit status: 0 when no agent fails, 1 when at least one does, 2 on a usage error.
Every diagnostic carries a stable code (E_*, W_*, I_*); SPEC.md § 13 lists them.
Standard library only, Python 3.9 or later.
"""
import argparse
import hashlib
import json
import os
import re
import sys

VALIDATOR_VERSION = '1.0.0'
SPEC_VERSION = 1

NAME = re.compile(r'^[a-z0-9]+(-[a-z0-9]+)*$')
MAX_NAME = 60
MAX_DESCRIPTION = 1024
RESERVED = {'con', 'prn', 'aux', 'nul'} | {f'com{i}' for i in range(1, 10)} | {f'lpt{i}' for i in range(1, 10)}
FRONTMATTER_FIELDS = {'name', 'description'}
CLI_FIELDS = {'tools', 'model'}

MANIFEST = 'agent.json'
ROOT_FIELDS = {'$schema', 'specVersion', 'id', 'scope', 'version', 'memory', 'skills',
               'permissions', 'requires', 'extensions'}
PROMPT_FIELDS = {'name', 'description'}
SCOPES = {'repository', 'shared'}
REACHES = {'project', 'agent'}
CEILINGS = {'read-only', 'ask', 'auto'}
TOOLS = {'read', 'edit', 'execute', 'web', 'delegate'}
ACCESS = {'read', 'write'}
LOCATION_KEYS = {'path', 'dir', 'directory', 'file', 'url', 'uri', 'endpoint', 'host', 'server',
                 'command', 'cmd', 'args', 'env', 'token', 'key', 'secret', 'password', 'credentials'}
ID = re.compile(r'^[A-Za-z0-9][A-Za-z0-9._-]{7,127}$')
SLOT = NAME
HOST = re.compile(r'^(\*\.)?([a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?\.)*[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$')
SEMVER = re.compile(
    r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
    r'(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
    r'(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$')
EXTENSION = re.compile(r'^[a-z0-9]+([.-][a-z0-9]+)*$')
MOVING_REF = re.compile(r'/(main|master|HEAD|latest)/')

# Sections an agent should have. Each accepts several headings, in English or in Spanish.
SECTIONS = [
    ('What you work with', re.compile(r'^(what you \w+ with|the contracts you check|files|con qu[eé]\b)', re.I)),
    ('How you work', re.compile(r'^(how you (?!report)\w+|what you look for|c[oó]mo (?!reportas)\w+)', re.I)),
    ('Where you stop', re.compile(r'^(where you stop|how far you go|how you hand off|hasta d[oó]nde llegas)', re.I)),
    ('What you report', re.compile(r'^(what you report|how you report|qu[eé] reportas)', re.I)),
    ('What you have learned', re.compile(r'^(what you have learned|lo que has aprendido)', re.I)),
]

CODE_SPAN = re.compile(r'(`+)(.+?)\1')
FENCE = re.compile(r'^ {0,3}(`{3,}|~{3,})')
PATH = re.compile(r'`([^`\s]+)`')
MENTION = re.compile(r'(?<![\w.@/`])@([a-z0-9]+(?:-[a-z0-9]+)*)(?![\w@-])')


class Diagnostic:
    def __init__(self, code, message, file=None, line=None, column=None, path=None):
        self.code, self.message = code, message
        self.file, self.line, self.column, self.path = file, line, column, path

    def level(self, strict):
        if self.code.startswith('E_'):
            return 'error'
        if self.code.startswith('W_'):
            return 'error' if strict else 'warning'
        return 'info'

    def where(self):
        if not self.file:
            return ''
        out = self.file
        if self.line:
            out += f':{self.line}'
            if self.column:
                out += f':{self.column}'
        return out

    def as_dict(self, strict):
        d = {'code': self.code, 'level': self.level(strict), 'message': self.message}
        for k in ('file', 'line', 'column', 'path'):
            v = getattr(self, k)
            if v is not None:
                d[k] = v
        return d


class DecodeError(Exception):
    pass


def read_text(path):
    """UTF-8 with or without BOM; CRLF and CR become LF."""
    with open(path, 'rb') as f:
        raw = f.read()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError as e:
        raise DecodeError(f'is not valid UTF-8 (byte {e.start})')
    return text.replace('\r\n', '\n').replace('\r', '\n')


# ---------------------------------------------------------------- agent.md

def frontmatter(text):
    """Returns (fields, body, body_first_line), or (None, text, 1) if there is no frontmatter."""
    if not text.startswith('---\n'):
        return None, text, 1
    end = text.find('\n---', 3)
    if end == -1:
        return None, text, 1
    after = text.find('\n', end + 4)
    block = text[4:end]
    rest = '' if after == -1 else text[after + 1:]
    stripped = rest.lstrip('\n')
    first_line = text[:len(text) - len(stripped)].count('\n') + 1
    fields, key = {}, None
    for line in block.split('\n'):
        m = re.match(r'^([A-Za-z_][\w-]*):\s*(.*)$', line)
        if m:
            key, value = m.group(1), m.group(2).strip()
            fields[key] = '' if value in ('>', '|', '>-', '|-', '>+', '|+') else value.strip('"\'')
        elif key and (line.startswith(' ') or line.startswith('\t')):
            fields[key] = (fields[key] + ' ' + line.strip()).strip()
    return fields, stripped, first_line


def prose_lines(body):
    """Yields (offset, line) with fenced code blocks removed and code spans blanked.

    A mention inside code is code, not a handoff: `@theme` in a CSS note must not
    be read as an agent (SPEC § 5).
    """
    fence = None
    for offset, line in enumerate(body.split('\n')):
        m = FENCE.match(line)
        if fence:
            if m and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) and not line.strip()[len(m.group(1)):].strip():
                fence = None
            continue
        if m:
            fence = m.group(1)
            continue
        yield offset, CODE_SPAN.sub(lambda s: ' ' * len(s.group(0)), line)


def looks_like_path(token):
    token = token.rstrip('.,:;)')
    if not token or token[0] in '@/~' or token.startswith(('http', 'www.')):
        return None
    if any(c in token for c in '<>*{}…|$') or '/' not in token:
        return None
    if not (token.endswith('/') or re.search(r'\.[A-Za-z0-9]+$', token) or token.startswith('.')):
        return None
    return token


def validate_name(name, folder, out):
    f = 'agent.md'
    if not name:
        out.append(Diagnostic('E_NAME_MISSING', '`name` is missing from the frontmatter', f))
        return
    if not NAME.match(name):
        out.append(Diagnostic('E_NAME_FORMAT', f'`name: {name}` is not ASCII kebab-case (lowercase letters, digits and single hyphens)', f))
    if len(name) > MAX_NAME:
        out.append(Diagnostic('E_NAME_LENGTH', f'`name` has {len(name)} characters; the maximum is {MAX_NAME}', f))
    if name in RESERVED:
        out.append(Diagnostic('E_NAME_RESERVED', f'`{name}` is a reserved file name on Windows', f))
    if name != folder:
        out.append(Diagnostic('E_NAME_FOLDER_MISMATCH', f'`name: {name}` does not match its folder `{folder}/`', f))


def validate_own_skills(agent_dir, out):
    skills_dir = os.path.join(agent_dir, 'skills')
    if not os.path.isdir(skills_dir):
        return
    for skill in sorted(os.listdir(skills_dir)):
        skill_dir = os.path.join(skills_dir, skill)
        if not os.path.isdir(skill_dir):
            continue
        rel = f'skills/{skill}/SKILL.md'
        skill_file = os.path.join(skill_dir, 'SKILL.md')
        if not os.path.isfile(skill_file):
            out.append(Diagnostic('E_SKILL_MD_MISSING', f'the skill `skills/{skill}/` has no SKILL.md', f'skills/{skill}/'))
            continue
        try:
            fields, _, _ = frontmatter(read_text(skill_file))
        except DecodeError as e:
            out.append(Diagnostic('E_ENCODING', f'`{rel}` {e}', rel))
            continue
        if fields is None:
            out.append(Diagnostic('E_SKILL_FRONTMATTER_MISSING', f'`{rel}` does not start with frontmatter (---)', rel))
            continue
        if fields.get('name') != skill:
            out.append(Diagnostic('E_SKILL_NAME_MISMATCH', f'`{rel}` declares `name: {fields.get("name")}`, which differs from its folder', rel))
        if not fields.get('description'):
            out.append(Diagnostic('E_SKILL_DESCRIPTION_MISSING', f'`{rel}` has no `description`', rel))


def validate_prompt(agent_dir, root, declared, check_paths, out):
    """Validates agent.md. Returns the name it declares, or None."""
    folder = os.path.basename(agent_dir)
    f = 'agent.md'
    try:
        text = read_text(os.path.join(agent_dir, f))
    except DecodeError as e:
        out.append(Diagnostic('E_ENCODING', f'agent.md {e}', f))
        return None
    fields, body, first_line = frontmatter(text)
    if fields is None:
        out.append(Diagnostic('E_FRONTMATTER_MISSING', 'agent.md does not start with a closed frontmatter block (---)', f, 1))
        return None

    name = fields.get('name', '')
    validate_name(name, folder, out)
    description = fields.get('description', '')
    if not description:
        out.append(Diagnostic('E_DESCRIPTION_MISSING', '`description` is missing: say when the agent is used and what it does not do', f))
    elif len(description) > MAX_DESCRIPTION:
        out.append(Diagnostic('W_DESCRIPTION_LONG', f'the description has {len(description)} characters; more than {MAX_DESCRIPTION} is usually the method, not the when', f))
    for field in fields:
        if field in CLI_FIELDS:
            out.append(Diagnostic('W_FRONTMATTER_CLI_FIELD', f'`{field}` binds the agent to one CLI; declare portable limits in agent.json `permissions`', f, path=field))
        elif field not in FRONTMATTER_FIELDS:
            out.append(Diagnostic('W_FRONTMATTER_UNKNOWN_FIELD', f'`{field}` is not a field of this format; it is ignored', f, path=field))

    if not body.strip():
        out.append(Diagnostic('E_BODY_EMPTY', 'the body is empty; without instructions the agent is a name without judgment', f))
        return name

    lines = body.split('\n')
    headings = [l.lstrip('#').strip() for l in lines if re.match(r'^#{2,3} ', l)]
    for section, pattern in SECTIONS:
        if not any(pattern.match(h) for h in headings):
            out.append(Diagnostic('W_SECTION_MISSING', f'there is no «{section}» section', f, path=section))
    first = next((l for l in lines if l.strip()), '')
    if first.startswith('#'):
        out.append(Diagnostic('W_ROLE_MISSING', 'the body does not start with the role: one or two sentences on what you do and what you do not', f))

    reported = set()
    for offset, line in prose_lines(body):
        for m in MENTION.finditer(line):
            mention = m.group(1)
            if mention not in declared and mention not in reported:
                reported.add(mention)
                out.append(Diagnostic('E_MENTION_UNDECLARED', f'`@{mention}` is not a declared agent', f, first_line + offset, m.start() + 1, mention))

    if check_paths:
        seen = set()
        for offset, line in enumerate(lines):
            for token in PATH.findall(line):
                path = looks_like_path(token)
                if not path or path in seen:
                    continue
                seen.add(path)
                if not (os.path.exists(os.path.join(root, path)) or os.path.exists(os.path.join(agent_dir, path))):
                    out.append(Diagnostic('E_PATH_NOT_FOUND', f'the path `{path}` does not exist', f, first_line + offset, path=path))

    validate_own_skills(agent_dir, out)
    return name


# ---------------------------------------------------------------- agent.json

class Manifest:
    def __init__(self):
        self.data = None
        self.duplicates = []


def load_manifest(path, out):
    f = MANIFEST
    m = Manifest()
    try:
        text = read_text(path)
    except DecodeError as e:
        out.append(Diagnostic('E_ENCODING', f'agent.json {e}', f))
        return m

    def pairs(items):
        seen = {}
        for k, v in items:
            if k in seen:
                m.duplicates.append(k)
            seen[k] = v
        return seen

    def constant(name):
        raise ValueError(f'`{name}` is not JSON')

    try:
        m.data = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except json.JSONDecodeError as e:
        out.append(Diagnostic('E_MANIFEST_PARSE', f'agent.json is not valid JSON: {e.msg}', f, e.lineno, e.colno))
        return m
    except ValueError as e:
        out.append(Diagnostic('E_MANIFEST_PARSE', f'agent.json is not valid JSON: {e}', f))
        return m
    for key in sorted(set(m.duplicates)):
        out.append(Diagnostic('E_MANIFEST_DUPLICATE_KEY', f'the key `{key}` appears more than once; JSON readers disagree on which one wins', f, path=key))
    if not isinstance(m.data, dict):
        out.append(Diagnostic('E_MANIFEST_NOT_OBJECT', 'agent.json must be a JSON object', f))
        m.data = None
    return m


def is_int(v):
    return isinstance(v, int) and not isinstance(v, bool)


def looks_like_location(value):
    return isinstance(value, str) and (any(c in value for c in '/\\:~') or '..' in value or value.startswith('.'))


class Checker:
    def __init__(self, out):
        self.out = out

    def diag(self, code, message, path):
        self.out.append(Diagnostic(code, message, MANIFEST, path=path))

    def typed(self, value, kind, path):
        ok = {'string': lambda v: isinstance(v, str),
              'object': lambda v: isinstance(v, dict),
              'array': lambda v: isinstance(v, list),
              'integer': is_int}[kind](value)
        if not ok:
            self.diag('E_FIELD_TYPE', f'`{path}` must be of type {kind}', path)
        return ok

    def unknown(self, obj, known, path, location_error=False):
        for key in obj:
            if key in known:
                continue
            sub = f'{path}.{key}'
            if location_error and key in LOCATION_KEYS:
                self.diag('E_LOCATION_DECLARED', f'`{sub}` declares a location; the repository names a slot and the environment resolves it', sub)
            else:
                self.diag('W_UNKNOWN_FIELD', f'`{sub}` is not a field of spec version {SPEC_VERSION}; it is ignored', sub)

    def reason(self, item, path):
        why = item.get('why')
        if why is None:
            self.diag('E_FIELD_MISSING', f'`{path}.why` is required: the person who approves the request reads it', f'{path}.why')
            return False
        if not isinstance(why, str) or not why.strip():
            self.diag('E_FIELD_TYPE', f'`{path}.why` must be a non-empty string', f'{path}.why')
            return False
        return True

    def requested(self, path, what):
        self.diag('I_REQUESTED_NOT_GRANTED', f'`{path}` requests {what}: requested, not granted. Only the person can grant it', path)


def validate_manifest(data, agent_name, root, check_paths, out):
    c = Checker(out)

    if 'specVersion' not in data:
        c.diag('E_SPEC_VERSION_MISSING', '`specVersion` is required', 'specVersion')
        return
    sv = data['specVersion']
    if not is_int(sv) or sv < 1:
        c.diag('E_SPEC_VERSION_INVALID', '`specVersion` must be a positive integer: the major version of the spec', 'specVersion')
        return
    if sv > SPEC_VERSION:
        c.diag('E_SPEC_VERSION_UNSUPPORTED', f'`specVersion: {sv}` is newer than this reader supports ({SPEC_VERSION}); the agent is not loaded', 'specVersion')
        return

    for key in data:
        if key in PROMPT_FIELDS:
            c.diag('W_DUPLICATED_FIELD', f'`{key}` belongs to agent.md; the manifest does not repeat it', key)
        elif key not in ROOT_FIELDS:
            c.diag('W_UNKNOWN_FIELD', f'`{key}` is not a field of spec version {SPEC_VERSION}; it is ignored', key)
    if 'name' in data and agent_name is not None and data['name'] != agent_name:
        c.diag('E_NAME_MISMATCH', f'`name: {data["name"]!r}` in agent.json differs from `{agent_name}` in agent.md', 'name')

    if '$schema' in data and c.typed(data['$schema'], 'string', '$schema'):
        if MOVING_REF.search(data['$schema']):
            c.diag('W_SCHEMA_NOT_PINNED', '`$schema` points to a moving branch; point it to a version tag such as `v1`', '$schema')

    if 'id' in data and c.typed(data['id'], 'string', 'id'):
        if not ID.match(data['id']):
            c.diag('E_ID_INVALID', '`id` must be 8 to 128 characters: letters, digits, `.`, `_` and `-`, starting with a letter or digit', 'id')

    if 'scope' not in data:
        c.diag('E_SCOPE_MISSING', '`scope` is required when agent.json exists: `repository` or `shared`', 'scope')
    elif data['scope'] not in SCOPES:
        c.diag('E_SCOPE_INVALID', f'`scope` must be `repository` or `shared`, not {data["scope"]!r}', 'scope')

    if 'version' in data and c.typed(data['version'], 'string', 'version'):
        if not SEMVER.match(data['version']):
            c.diag('E_VERSION_INVALID', f'`version: {data["version"]!r}` is not a Semantic Versioning 2.0.0 version', 'version')

    if 'memory' in data and c.typed(data['memory'], 'object', 'memory'):
        memory = data['memory']
        c.unknown(memory, {'reach', 'store'}, 'memory', location_error=True)
        if 'reach' in memory and memory['reach'] not in REACHES:
            c.diag('E_MEMORY_REACH_INVALID', '`memory.reach` must be `project` or `agent`', 'memory.reach')
        if 'store' in memory:
            store = memory['store']
            if isinstance(store, str):
                if store == 'local':
                    pass
                elif looks_like_location(store):
                    c.diag('E_LOCATION_DECLARED', f'`memory.store` is a location ({store!r}); the repository names a slot and the environment resolves it', 'memory.store')
                else:
                    c.diag('E_MEMORY_STORE_INVALID', '`memory.store` must be `"local"` or `{ "slot": "<name>" }`', 'memory.store')
            elif isinstance(store, dict):
                c.unknown(store, {'slot'}, 'memory.store', location_error=True)
                slot = store.get('slot')
                if slot is None:
                    c.diag('E_FIELD_MISSING', '`memory.store.slot` is required', 'memory.store.slot')
                elif looks_like_location(slot):
                    c.diag('E_LOCATION_DECLARED', f'`memory.store.slot` is a location ({slot!r}); a slot is a name', 'memory.store.slot')
                elif not isinstance(slot, str) or not SLOT.match(slot):
                    c.diag('E_MEMORY_STORE_INVALID', '`memory.store.slot` must be a kebab-case name', 'memory.store.slot')
                elif not any(d.code == 'E_LOCATION_DECLARED' and (d.path or '').startswith('memory.store') for d in out):
                    c.requested('memory.store', f'external memory in slot `{slot}`')
            else:
                c.diag('E_MEMORY_STORE_INVALID', '`memory.store` must be `"local"` or `{ "slot": "<name>" }`', 'memory.store')

    if 'skills' in data and c.typed(data['skills'], 'array', 'skills'):
        for i, entry in enumerate(data['skills']):
            p = f'skills[{i}]'
            if not c.typed(entry, 'string', p):
                continue
            norm = os.path.normpath(entry.replace('\\', '/'))
            if os.path.isabs(entry) or entry.startswith(('/', '\\')) or re.match(r'^[A-Za-z]:', entry) \
                    or norm == '..' or norm.startswith('..' + os.sep):
                c.diag('E_PATH_ESCAPE', f'`{entry}` leaves the repository; skills are repository-relative paths', p)
                continue
            full = os.path.realpath(os.path.join(root, norm))
            if not (full == os.path.realpath(root) or full.startswith(os.path.realpath(root) + os.sep)):
                c.diag('E_PATH_ESCAPE', f'`{entry}` resolves outside the repository', p)
                continue
            if check_paths and not os.path.isfile(os.path.join(full, 'SKILL.md')):
                c.diag('E_SKILL_NOT_FOUND', f'`{entry}` has no SKILL.md', p)

    if 'permissions' in data and c.typed(data['permissions'], 'object', 'permissions'):
        perms = data['permissions']
        c.unknown(perms, {'ceiling', 'tools'}, 'permissions')
        if 'ceiling' in perms and perms['ceiling'] not in CEILINGS:
            c.diag('E_PERMISSION_CEILING_INVALID', '`permissions.ceiling` must be `read-only`, `ask` or `auto`', 'permissions.ceiling')
        if 'tools' in perms and c.typed(perms['tools'], 'array', 'permissions.tools'):
            for i, tool in enumerate(perms['tools']):
                p = f'permissions.tools[{i}]'
                if c.typed(tool, 'string', p) and tool not in TOOLS:
                    c.diag('W_UNKNOWN_TOOL', f'`{tool}` is not a tool class of spec version {SPEC_VERSION}; it grants nothing', p)

    if 'requires' in data and c.typed(data['requires'], 'object', 'requires'):
        req = data['requires']
        c.unknown(req, {'mcp', 'network', 'tools'}, 'requires')
        if 'mcp' in req and c.typed(req['mcp'], 'array', 'requires.mcp'):
            for i, item in enumerate(req['mcp']):
                p = f'requires.mcp[{i}]'
                if not c.typed(item, 'object', p):
                    continue
                before = len(out)
                c.unknown(item, {'slot', 'access', 'why'}, p, location_error=True)
                slot = item.get('slot')
                if slot is None:
                    c.diag('E_FIELD_MISSING', f'`{p}.slot` is required', f'{p}.slot')
                elif looks_like_location(slot):
                    c.diag('E_LOCATION_DECLARED', f'`{p}.slot` is a location ({slot!r}); a slot is a name', f'{p}.slot')
                elif not isinstance(slot, str) or not SLOT.match(slot):
                    c.diag('E_FIELD_VALUE', f'`{p}.slot` must be a kebab-case name', f'{p}.slot')
                if 'access' not in item:
                    c.diag('E_FIELD_MISSING', f'`{p}.access` is required: `read` or `write`', f'{p}.access')
                elif item['access'] not in ACCESS:
                    c.diag('E_FIELD_VALUE', f'`{p}.access` must be `read` or `write`', f'{p}.access')
                c.reason(item, p)
                if not any(d.code.startswith('E_') for d in out[before:]):
                    c.requested(p, f'the MCP server in slot `{slot}` with {item["access"]} access')
        if 'network' in req and c.typed(req['network'], 'array', 'requires.network'):
            for i, item in enumerate(req['network']):
                p = f'requires.network[{i}]'
                if not c.typed(item, 'object', p):
                    continue
                before = len(out)
                c.unknown(item, {'host', 'why'}, p)
                host = item.get('host')
                if host is None:
                    c.diag('E_FIELD_MISSING', f'`{p}.host` is required', f'{p}.host')
                elif not isinstance(host, str) or not HOST.match(host):
                    c.diag('E_FIELD_VALUE', f'`{p}.host` must be a host name, without scheme, port or path', f'{p}.host')
                c.reason(item, p)
                if not any(d.code.startswith('E_') for d in out[before:]):
                    c.requested(p, f'network access to `{host}`')
        if 'tools' in req and c.typed(req['tools'], 'array', 'requires.tools'):
            for i, item in enumerate(req['tools']):
                p = f'requires.tools[{i}]'
                if not c.typed(item, 'object', p):
                    continue
                before = len(out)
                c.unknown(item, {'name', 'why'}, p, location_error=True)
                tool = item.get('name')
                if tool is None:
                    c.diag('E_FIELD_MISSING', f'`{p}.name` is required', f'{p}.name')
                elif looks_like_location(tool):
                    c.diag('E_LOCATION_DECLARED', f'`{p}.name` is a location ({tool!r}); name the program, not where it lives', f'{p}.name')
                elif not isinstance(tool, str) or not tool.strip():
                    c.diag('E_FIELD_VALUE', f'`{p}.name` must be a non-empty string', f'{p}.name')
                c.reason(item, p)
                if not any(d.code.startswith('E_') for d in out[before:]):
                    c.requested(p, f'the tool `{tool}`')

    if 'extensions' in data and c.typed(data['extensions'], 'object', 'extensions'):
        for key, ext in data['extensions'].items():
            p = f'extensions.{key}'
            if not EXTENSION.match(key):
                c.diag('E_EXTENSION_NAME_INVALID', f'`{key}` is not a valid extension namespace (lowercase, digits, `.` and `-`)', p)
                continue
            if not c.typed(ext, 'object', p):
                continue
            if 'version' not in ext:
                c.diag('W_EXTENSION_VERSION_MISSING', f'`{p}.version` is missing; every extension carries its own version', f'{p}.version')
            elif not is_int(ext['version']) or ext['version'] < 1:
                c.diag('E_EXTENSION_VERSION_INVALID', f'`{p}.version` must be a positive integer', f'{p}.version')


# ---------------------------------------------------------------- agents

def digest(agent_dir):
    """sha256 over the agent folder, as defined in SPEC § 10.3."""
    entries = []
    for dirpath, dirnames, filenames in os.walk(agent_dir):
        dirnames[:] = sorted(d for d in dirnames if not os.path.islink(os.path.join(dirpath, d)))
        for name in filenames:
            full = os.path.join(dirpath, name)
            if os.path.islink(full) or not os.path.isfile(full):
                continue
            rel = os.path.relpath(full, agent_dir).replace(os.sep, '/')
            with open(full, 'rb') as f:
                entries.append((rel.encode('utf-8'), hashlib.sha256(f.read()).hexdigest()))
    listing = ''.join(f'{h}  {rel.decode("utf-8")}\n' for rel, h in sorted(entries))
    return 'sha256:' + hashlib.sha256(listing.encode('utf-8')).hexdigest()


def validate_agent(agent_dir, root, declared, check_paths):
    """Returns (diagnostics, manifest dict or None)."""
    out = []
    has_md = os.path.isfile(os.path.join(agent_dir, 'agent.md'))
    has_json = os.path.isfile(os.path.join(agent_dir, MANIFEST))
    if not has_md:
        what = 'agent.json without agent.md: the manifest describes an agent that does not exist' if has_json else 'the folder has no agent.md'
        out.append(Diagnostic('E_AGENT_MD_MISSING', what, 'agent.md'))
        return out, None
    name = validate_prompt(agent_dir, root, declared, check_paths, out)
    if not has_json:
        out.append(Diagnostic('I_NO_MANIFEST', 'no agent.json: scope is undeclared, the reading tool decides (SPEC § 11.3)', MANIFEST))
        return out, None
    manifest = load_manifest(os.path.join(agent_dir, MANIFEST), out)
    if manifest.data is not None and not manifest.duplicates:
        validate_manifest(manifest.data, name, root, check_paths, out)
    return out, manifest.data


def validate_all(agents_dir, root, check_paths):
    folders = sorted(d for d in os.listdir(agents_dir)
                     if os.path.isdir(os.path.join(agents_dir, d)) and not d.startswith('.'))
    declared = {d for d in folders if os.path.isfile(os.path.join(agents_dir, d, 'agent.md'))}
    results = []
    for folder in folders:
        agent_dir = os.path.join(agents_dir, folder)
        diags, manifest = validate_agent(agent_dir, root, declared, check_paths)
        results.append({'name': folder, 'dir': agent_dir, 'diagnostics': diags, 'manifest': manifest})

    ids = {}
    for r in results:
        m = r['manifest']
        if isinstance(m, dict) and isinstance(m.get('id'), str) and ID.match(m['id']):
            ids.setdefault(m['id'], []).append(r)
    for agent_id, owners in ids.items():
        if len(owners) > 1:
            names = ', '.join(o['name'] for o in owners)
            for o in owners:
                o['diagnostics'].append(Diagnostic('E_ID_DUPLICATE', f'`id: {agent_id}` is shared by {names}; a copied agent needs a new id', MANIFEST, path='id'))
    return results


def report(results, strict, rel_to):
    agents, totals = [], {'error': 0, 'warning': 0, 'info': 0}
    for r in results:
        diags = [d.as_dict(strict) for d in r['diagnostics']]
        for d in diags:
            totals[d['level']] += 1
        failed = any(d['level'] == 'error' for d in diags)
        agents.append({
            'name': r['name'],
            'path': os.path.relpath(r['dir'], rel_to).replace(os.sep, '/'),
            'verdict': 'fail' if failed else 'pass',
            'manifest': isinstance(r['manifest'], dict),
            'scope': r['manifest'].get('scope') if isinstance(r['manifest'], dict) else None,
            'digest': digest(r['dir']),
            'diagnostics': diags,
        })
    return {
        'validator': VALIDATOR_VERSION,
        'specVersion': SPEC_VERSION,
        'strict': strict,
        'agents': agents,
        'summary': {
            'agents': len(agents),
            'passed': sum(a['verdict'] == 'pass' for a in agents),
            'failed': sum(a['verdict'] == 'fail' for a in agents),
            'errors': totals['error'],
            'warnings': totals['warning'],
            'info': totals['info'],
        },
    }


def print_human(rep):
    for a in rep['agents']:
        print(f'{"PASS" if a["verdict"] == "pass" else "FAIL"}  {a["name"]}')
        for d in a['diagnostics']:
            where = d.get('file', '')
            if 'line' in d:
                where += f':{d["line"]}' + (f':{d["column"]}' if 'column' in d else '')
            print(f'      {d["level"]:<7} {d["code"]:<28} {where + "  " if where else ""}{d["message"]}')
    s = rep['summary']
    mode = ' (strict: warnings count as errors)' if rep['strict'] else ''
    print(f'\n{s["agents"]} agents: {s["passed"]} passed, {s["failed"]} failed; '
          f'{s["errors"]} errors, {s["warnings"]} warnings, {s["info"]} info{mode}')


def main(argv=None):
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, 'reconfigure'):
            stream.reconfigure(encoding='utf-8')
    p = argparse.ArgumentParser(description='Validates agents against the Agent Declaration Format (SPEC.md)')
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument('--root', help='repository root; reads <root>/.agents/agents/')
    g.add_argument('--agents', help='folder that contains <name>/agent.md')
    p.add_argument('--no-paths', action='store_true', help='do not check that cited paths and skills exist')
    p.add_argument('--strict', action='store_true', help='warnings count as errors; use it before publishing')
    p.add_argument('--json', action='store_true', help='print a machine-readable report')
    p.add_argument('--version', action='version', version=f'validate_agent {VALIDATOR_VERSION} (spec {SPEC_VERSION})')
    a = p.parse_args(argv)

    root = os.path.abspath(a.root or '.')
    agents_dir = os.path.join(root, '.agents', 'agents') if a.root else os.path.abspath(a.agents)
    if not os.path.isdir(agents_dir):
        if a.json:
            print(json.dumps({'validator': VALIDATOR_VERSION, 'error': f'{agents_dir} does not exist'}))
        else:
            print(f'ERROR: {agents_dir} does not exist', file=sys.stderr)
        return 2

    results = validate_all(agents_dir, root, not a.no_paths)
    rep = report(results, a.strict, root)
    if a.json:
        print(json.dumps(rep, indent=2, ensure_ascii=False))
    else:
        print_human(rep)
    return 1 if rep['summary']['failed'] else 0


if __name__ == '__main__':
    sys.exit(main())

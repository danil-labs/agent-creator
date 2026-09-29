# Agent Declaration Format — Specification

**Version 1** (`specVersion: 1`) · Status: stable · Schema:
[`schema/agent.v1.json`](schema/agent.v1.json) · Conformance corpus:
[`conformance/`](conformance/)

This document defines how an AI agent is declared in a repository: a folder
with a prompt (`agent.md`), an optional manifest (`agent.json`) and optional
skills of its own. It defines what a file must contain, and what a tool that
reads it must do.

The format belongs to no tool. A repository that follows it works with any CLI
that reads Markdown prompts, and every rule here holds without any particular
harness. Tool-specific settings live in `extensions.<tool>` (§ 7.12).

The [guide](GUIDE.md) explains how to design good agents. Every rule in this
document says why it exists, or points to the section of the guide that does.

## Contents

1. [Conventions and terms](#1-conventions-and-terms)
2. [Layout](#2-layout)
3. [agent.md: the frontmatter](#3-agentmd-the-frontmatter)
4. [agent.md: the body](#4-agentmd-the-body)
5. [Mentions and handoffs](#5-mentions-and-handoffs)
6. [Skills and tools](#6-skills-and-tools)
7. [agent.json: the manifest](#7-agentjson-the-manifest)
8. [The three classes of fields](#8-the-three-classes-of-fields)
9. [Versioning and compatibility](#9-versioning-and-compatibility)
10. [Identity and memory](#10-identity-and-memory)
11. [Scope and import](#11-scope-and-import)
12. [Harness conformance](#12-harness-conformance)
13. [Diagnostic codes](#13-diagnostic-codes)
14. [Non-goals](#14-non-goals)
15. [Known limits](#15-known-limits)
- [Appendix A: a complete example](#appendix-a-a-complete-example)
- [Appendix B: extension namespaces](#appendix-b-extension-namespaces)

## 1. Conventions and terms

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**,
**RECOMMENDED**, **MAY** and **OPTIONAL** are to be interpreted as described in
[BCP 14](https://www.rfc-editor.org/info/bcp14) (RFC 2119, RFC 8174) when, and
only when, they appear in bold capitals.

| Term | Meaning |
|---|---|
| **Agent** | A named role: who does a job, with which files, where it stops and whom it hands the result to. One folder under `.agents/agents/` |
| **Skill** | A method: how one thing is done. A folder with a `SKILL.md`, as defined by [Agent Skills](https://agentskills.io) |
| **Repository** | The version-controlled tree that declares the agents |
| **Source** | A repository that another project reads agents from |
| **Consumer** | The project that reads agents from a source |
| **Reader** | Any program that reads this format: a validator, a CLI, a harness |
| **Harness** | A reader that runs agents: it launches a CLI with the agent's prompt and applies the manifest |
| **Launcher** | Whoever starts a run of the agent: a person, or another agent |
| **Environment** | The boundary a harness uses to keep one client's or organization's material apart from another's, such as a workspace. Memory never crosses it |
| **Person** | The human who operates the harness and approves what it grants |

A **diagnostic** is a finding a reader reports, identified by a stable code
(§ 13). Prefixes give the level: `E_` error, `W_` warning, `I_` information.

## 2. Layout

```
<repository>/
  .agents/agents/
    <name>/
      agent.md                  REQUIRED  the prompt: frontmatter and instructions
      agent.json                OPTIONAL  the manifest: scope, identity, memory, limits, requests
      skills/                   OPTIONAL  skills only this agent uses
        <skill>/
          SKILL.md              REQUIRED for each skill, per Agent Skills
          scripts/              OPTIONAL  code the skill runs
          references/           OPTIONAL  documents the skill opens when it needs them
          assets/               OPTIONAL  templates and static files
```

- An agent **MUST** be a folder under `.agents/agents/` containing `agent.md`.
  *Why:* one folder per agent keeps the prompt, the manifest and the agent's
  skills together, so they are versioned, reviewed, hashed (§ 10.3) and
  exported (§ 11) as one unit.
- `.agents/agents/` is the neutral location: it belongs to no CLI. A reader that
  drives several CLIs **SHOULD** read it for all of them. *Why:* the same agent
  must behave the same whichever CLI a person uses.
- A CLI's own folder, `<dir>/agents/<name>.md` (for example
  `.claude/agents/story-reviewer.md` for Claude Code subagents), holds the same
  `agent.md` format as one loose file. A reader **MAY** read it. A loose file
  has no manifest and no skills of its own. If a team publishes the same agent
  in both places, one copy **SHOULD** be generated from the other. *Why:* two
  hand-edited copies drift at the first edit ([GUIDE § 15](GUIDE.md#15-why-each-rule-exists)).
- `agent.json` **MUST NOT** exist without `agent.md` (`E_AGENT_MD_MISSING`).
  *Why:* the prompt is the agent; a manifest alone describes nothing that can
  run.
- Nothing else in the folder has a meaning defined by this specification. Other
  files are part of the agent's content and of its digest (§ 10.3).

## 3. agent.md: the frontmatter

`agent.md` starts with a YAML frontmatter block delimited by `---` lines,
followed by the body.

```yaml
---
name: story-reviewer
description: Reviews user stories that are already written and rules on whether they can be built. Use it when asked to review a story, and when @story-writer hands one off. Read-only.
---
```

| Field | Presence | Rule |
|---|---|---|
| `name` | **REQUIRED** | See § 3.1 |
| `description` | **REQUIRED** | See § 3.2 |
| `tools` | tolerated | A CLI-specific tool list. Readers warn (`W_FRONTMATTER_CLI_FIELD`) |
| `model` | tolerated | A CLI-specific model id. Readers warn (`W_FRONTMATTER_CLI_FIELD`) |
| anything else | not defined | Readers warn and ignore it (`W_FRONTMATTER_UNKNOWN_FIELD`) |

This frontmatter is compatible with Claude Code subagents: the same file works
as `.claude/agents/<name>.md`.

- The file **MUST** be UTF-8, with or without a byte order mark. Readers
  **MUST** accept LF and CRLF line endings. *Why:* Windows editors write BOM and
  CRLF by default; a reader that rejects them rejects agents that work
  everywhere else.
- A reader **MUST NOT** reject an agent because of an unknown frontmatter
  field; it **SHOULD** warn. *Why:* CLIs add their own fields (`color`,
  `permissionMode`, …). A reader that rejects them breaks agents written for
  that CLI; a reader that ignores them silently hides a field the author
  thought was applied.
- `tools` and `model` **SHOULD NOT** be used. *Why:* both are written in one
  CLI's vocabulary and bind the agent to it. Portable limits go in
  `agent.json` `permissions` (§ 7.10). A harness **MAY** pass them through to
  the CLI that understands them; it **MUST NOT** treat them as a grant.
- No frontmatter field says which CLI runs the agent. *Why:* which binary runs
  it is decided by the person, with the accounts they have. An agent that only
  works with one CLI is personal configuration, not a project agent.

### 3.1 The name

- It **MUST** be ASCII kebab-case: lowercase letters, digits and single
  hyphens, matching `^[a-z0-9]+(-[a-z0-9]+)*$`, at most 60 characters
  (`E_NAME_FORMAT`, `E_NAME_LENGTH`).
- It **MUST** equal its folder name (`E_NAME_FOLDER_MISMATCH`).
- It **MUST NOT** be a reserved Windows device name: `con`, `prn`, `aux`,
  `nul`, `com1`–`com9`, `lpt1`–`lpt9` (`E_NAME_RESERVED`).
- It **MUST** be unique among the agents a reader loads from one repository.

*Why:* the name is what people type to delegate (`@name`) and what a folder is
called on every file system. Kebab-case ASCII is the one form that survives
case-insensitive file systems, URLs and shells unchanged, and it is the same
rule Agent Skills uses for skill names.

The name **SHOULD** be written in the team's language: `story-writer` and
`redactor-de-historias` are equally valid. Renaming an agent changes its
identity unless it declares an `id` (§ 10.1).

### 3.2 The description

- It **MUST** be present and non-empty (`E_DESCRIPTION_MISSING`).
- It **SHOULD** say what the agent does, when to use it (the phrases people use
  and the handoffs that trigger it), and what it does not do.
- It **SHOULD** stay under 1024 characters (`W_DESCRIPTION_LONG`). *Why:* a
  longer description is usually the method, which belongs in the body or a
  skill ([GUIDE § 3](GUIDE.md#3-the-name-and-the-description)).

The description is shown to whoever chooses an agent and sent to the CLI. It
does not route: see § 14.

## 4. agent.md: the body

The body is the agent's instructions. It is sent to the model as written.

- The body **MUST NOT** be empty (`E_BODY_EMPTY`). *Why:* without instructions
  an agent is a name with no criteria, and a task title already gives you that.
- It **SHOULD** start with the role: one or two sentences in the second person
  saying what the agent does and what it does not do (`W_ROLE_MISSING`).
- It **SHOULD** contain these sections, in this order (`W_SECTION_MISSING`).
  Readers accept the English headings below and their variants; the validator
  also accepts Spanish ones.

| Section | Heading | What it holds |
|---|---|---|
| Role | *(no heading, at the top)* | What you do and what you do **not** do |
| What you work with | `## What you work with` | The real files by path, in a "File · What for" table, and what does not exist |
| How you work | `## How you work` (or `How you review`, `How you plan`, …) | Concrete steps and the criterion that decides each one |
| Where you stop | `## Where you stop` | When you are done, whom you hand off to, and what the message carries |
| What you report | `## What you report` | The exact shape of the output |
| What you have learned | `## What you have learned` | Real lessons of the role, and the memory rule |

*Why these six:* each one answers a question a model otherwise guesses — scope,
inputs, method, boundary, output and improvement. The reasons are in
[GUIDE § 4](GUIDE.md#4-the-body-part-by-part).

- Every repository path the body cites between backticks **MUST** exist,
  relative to the repository root or to the agent's folder
  (`E_PATH_NOT_FOUND`). *Why:* an agent told to open a file that does not
  exist invents its content. When something the role would look for does not
  exist, the body **SHOULD** say so.
- A **shared** agent (§ 11) **SHOULD** cite its own files relative to its folder
  (`skills/<skill>/SKILL.md`), not from the repository root. *Why:* in the
  consumer the agent's folder is not at `.agents/agents/<name>/` of the
  consumer's root; a harness resolves agent-relative paths against the agent's
  folder (§ 12, H14).
- The body **SHOULD** be written in the language the team's models follow best.
  What a person reads on screen belongs to the harness's interface, not to the
  body.

## 5. Mentions and handoffs

An agent hands work to another by naming it: `@story-reviewer`.

- A **mention** is `@` followed by an agent name, in prose. Text inside code
  — an inline code span or a fenced code block — is never a mention. *Why:*
  code quotes other languages, and many of them use `@`: `` `@theme` `` is a CSS
  directive, not an agent. Reading code as prose turns valid agents into
  failures.
- A mention **MUST** name an agent declared in the same repository
  (`E_MENTION_UNDECLARED`). *Why:* a handoff to an agent that does not exist is
  lost work that looks delivered.
- Handoffs **SHOULD** be written as bare mentions, outside code, so readers can
  check them.
- The receiving agent does not see the sender's conversation. A handoff message
  **SHOULD** carry what is handed over, where its current version lives, what
  changed and what is still open ([GUIDE § 5](GUIDE.md#5-handoffs)).
- There is no router and no orchestrator in this format. Whoever delegates —
  a person or an agent — names the receiver.

## 6. Skills and tools

### 6.1 The agent's own skills

- A skill that only one agent uses **SHOULD** live inside that agent, in
  `<name>/skills/<skill>/`. One used by several agents **SHOULD** live outside
  any agent, in the repository's skills folder.
- Each skill folder **MUST** contain a `SKILL.md` (`E_SKILL_MD_MISSING`) with
  frontmatter (`E_SKILL_FRONTMATTER_MISSING`) whose `name` equals the folder
  name (`E_SKILL_NAME_MISMATCH`) and whose `description` is non-empty
  (`E_SKILL_DESCRIPTION_MISSING`).
- Everything else about a skill — `license`, `compatibility`, `metadata`,
  `allowed-tools`, `scripts/`, `references/`, `assets/` — is defined by the
  [Agent Skills specification](https://agentskills.io/specification), and a
  reader of this format **MUST NOT** redefine it. *Why:* a skill must work the
  same whether it is loaded by an agent or on its own.
- An agent's own skills are declared by placement: they are not listed in
  `agent.json`.
- A harness **SHOULD** announce an agent's own skills only in runs of that
  agent. *Why:* they are its method, not the repository's.
- The body **SHOULD** cite each skill by path under "What you work with".
  *Why:* a session that does not run as the agent — or a CLI that does not
  announce skills — can still open the method. When the specialist skills of a
  real team were moved inside one agent without being cited, a session lost
  them halfway through the work ([GUIDE § 15](GUIDE.md#15-why-each-rule-exists)).

### 6.2 Skills outside the agent

Skills from the repository's shared skills folder are listed in `agent.json`
`skills` (§ 7.9). A harness **SHOULD** announce them in the agent's runs, as it
does with its own skills.

### 6.3 What `allowed-tools` and `permissions.tools` do

Two fields talk about tools, at two levels, and they combine by intersection:

- A skill's `allowed-tools` (Agent Skills) pre-approves tools for that skill.
- An agent's `permissions.tools` (§ 7.10) is an allow-list of tool classes for
  the whole run.

Neither grants anything the launcher does not have (§ 8). While a skill runs
inside an agent, the tools available are those the launcher has, restricted by
the agent's `permissions`, restricted again by the skill's `allowed-tools`.
*Why:* a method loaded by a read-only agent must not become a way to write.

## 7. agent.json: the manifest

`agent.json` is optional. It declares what the prompt cannot: whether the agent
is exported, its stable identity, its memory, its limits and what it requests.

### 7.1 File rules

- It **MUST** be a JSON object ([RFC 8259](https://www.rfc-editor.org/rfc/rfc8259))
  encoded in UTF-8, with or without a byte order mark, with LF or CRLF line
  endings (`E_MANIFEST_PARSE`, `E_MANIFEST_NOT_OBJECT`, `E_ENCODING`).
- It **MUST NOT** repeat a key within one object (`E_MANIFEST_DUPLICATE_KEY`).
  *Why:* JSON parsers disagree on which duplicate wins, so two readers would see
  two different agents.
- It **MUST NOT** contain comments or trailing commas. *Why:* those are JSON5 or
  JSONC, and a strict JSON reader rejects them.
- The root is reserved to this specification. Tool-specific settings go under
  `extensions` (§ 7.12).

[`schema/agent.v1.json`](schema/agent.v1.json) describes the shape of a
manifest that passes strict mode (§ 9.3). It allows unknown root fields,
because readers warn about them rather than reject them. A schema cannot check
what spans files —a duplicate `id`, a `name` that differs from `agent.md`, a
skill that does not exist— nor tell a warning from an error, so readers apply
the codes in § 13, not the schema's verdict.

### 7.2 Fields at a glance

| Field | Type | Presence | Class (§ 8) |
|---|---|---|---|
| `$schema` | string (URI) | OPTIONAL | descriptive |
| `specVersion` | integer | **REQUIRED** | — |
| `scope` | `"repository"` \| `"shared"` | **REQUIRED** | descriptive |
| `id` | string | OPTIONAL | descriptive |
| `version` | string (SemVer 2.0.0) | OPTIONAL | descriptive |
| `memory` | object | OPTIONAL | `reach`: descriptive · `store: {slot}`: widening |
| `skills` | array of strings | OPTIONAL | descriptive |
| `permissions` | object | OPTIONAL | narrowing |
| `requires` | object | OPTIONAL | widening |
| `extensions` | object | OPTIONAL | opaque (§ 7.12) |

`name` and `description` are **not** manifest fields (§ 7.13).

A field present with the wrong JSON type is an error (`E_FIELD_TYPE`); a
required nested field that is missing is `E_FIELD_MISSING`; a nested value
outside its allowed set is `E_FIELD_VALUE`, unless a more specific code is
listed.

### 7.3 `specVersion`

The major version of this specification that the manifest follows.

- **REQUIRED** (`E_SPEC_VERSION_MISSING`). A positive integer
  (`E_SPEC_VERSION_INVALID`). For this document, `1`.
- A reader that does not support the value **MUST NOT** load the agent, and
  **MUST** say so (`E_SPEC_VERSION_UNSUPPORTED`). *Why:* a later major version
  may add narrowing fields. Running the agent with only its `agent.md` would
  run it with fewer limits than its author declared.

*Why an integer:* within a major version every change is additive (§ 9), so a
minor number would make no reader do anything differently. A string such as
`"1.10"` also invites comparing versions as text.

```json
"specVersion": 1
```

### 7.4 `$schema`

- OPTIONAL. A URI of the JSON Schema of this version, for editors.
- It is informative: a reader **MUST NOT** decide anything from it, and
  validation **MUST** work without network access. *Why:* the manifest must be
  readable offline, and a URL cannot be compared like a version number.
- It **SHOULD** point to a version tag, not to a branch (`W_SCHEMA_NOT_PINNED`).
  *Why:* a schema on `main` moves, and an editor would validate a v1 manifest
  against whatever `main` says today.

```json
"$schema": "https://raw.githubusercontent.com/danil-labs/agent-creator/v1/schema/agent.v1.json"
```

### 7.5 `scope`

Whether the agent is exported when its repository is used as a source.

- **REQUIRED** when `agent.json` exists (`E_SCOPE_MISSING`). One of
  `"repository"` or `"shared"` (`E_SCOPE_INVALID`).
- `repository`: the agent is used inside its own repository only.
- `shared`: the agent is also offered to consumers that use this repository as
  a source.

*Why required:* guessing is wrong in both directions. A default of `shared`
leaks internal agents — a project's own release manager — into every consumer.
A default of `repository` makes agents that consumers already use disappear
without an error. The rules for import are in § 11.

```json
"scope": "shared"
```

### 7.6 `id`

A stable identifier of the agent, independent of its name.

- OPTIONAL. A string of 8 to 128 characters matching
  `^[A-Za-z0-9][A-Za-z0-9._-]{7,127}$` (`E_ID_INVALID`).
- It **MUST** be unique among the agents of the repository (`E_ID_DUPLICATE`).
  *Why:* copying a folder to start a new agent copies its `id`, and two agents
  with one `id` would share one memory.
- It **SHOULD** be generated once, by the tool that creates the agent, as a
  random UUID (version 4) or ULID. It **MUST NOT** change after the agent is
  first used, and **MUST NOT** be reused for another agent.
- A reader **MUST NOT** add or change an `id` while reading. Generating it is an
  authoring action, written to the repository by the person or the authoring
  tool and reviewed like any other change. *Why:* a reader that writes into
  someone's working tree leaves a diff nobody asked for (§ 12, H11).

*Why it exists:* memory is keyed by identity (§ 10). Without an `id`, identity
is the name, so renaming an agent orphans what it learned. With an `id`, the
agent can be renamed and keep its memory.

```json
"id": "3f2b8c1e-9a47-4d2e-b6a0-5c7d1e8f9a20"
```

### 7.7 `version`

- OPTIONAL. A [Semantic Versioning 2.0.0](https://semver.org) string
  (`E_VERSION_INVALID`).
- It is descriptive. A reader **MAY** show it; it **MUST NOT** decide anything
  from it — not whether to update, not which memory to use. *Why:* nothing
  forces an author to bump it, so it can lie. What identifies what ran is the
  source commit plus the agent's digest (§ 10.3), which cannot.
- Publishing a version with a git tag `agents/<name>/v<version>` is
  RECOMMENDED for shared agents ([GUIDE § 11](GUIDE.md#11-designing-a-shared-agent)).

```json
"version": "1.2.0"
```

### 7.8 `memory`

Where what the agent learns lives. The rules are in § 10.

| Key | Type | Default | Values |
|---|---|---|---|
| `reach` | string | `"project"` | `"project"`: one memory per project. `"agent"`: one memory for the agent across the projects of one environment (`E_MEMORY_REACH_INVALID`) |
| `store` | string or object | `"local"` | `"local"`: the harness's own storage. `{ "slot": "<name>" }`: an external store the environment binds (`E_MEMORY_STORE_INVALID`) |

- A `slot` **MUST** be a kebab-case name.
- The manifest **MUST NOT** declare a location: no path, URL, command, host or
  secret, in any key (`E_LOCATION_DECLARED`). *Why:* the repository is
  material a person did not write. A manifest that could say where memory lives
  could point it at `~/.ssh`, or send what the agent learns to a server of the
  author's choosing. The repository names a slot; the environment decides what
  the slot is.
- `store: { "slot": … }` is a widening request (§ 8): readers report it as
  requested, not granted (`I_REQUESTED_NOT_GRANTED`).

```json
"memory": { "reach": "agent", "store": { "slot": "team-memory" } }
```

### 7.9 `skills`

Skills outside the agent's folder that the agent uses.

- OPTIONAL. An array of repository-relative paths to skill folders, with `/` as
  separator.
- Each path **MUST** stay inside the repository: no absolute paths, no drive
  letters, no `..` that leaves the root (`E_PATH_ESCAPE`). *Why:* a manifest
  must not make a reader open files outside the material it was given.
- Each path **MUST** contain a `SKILL.md` (`E_SKILL_NOT_FOUND`).
- The agent's own skills (§ 6.1) are not listed.

```json
"skills": ["skills/create-agent"]
```

### 7.10 `permissions`

Limits the agent runs under. Every key here is narrowing (§ 8): it can only
remove capabilities.

| Key | Type | Values |
|---|---|---|
| `ceiling` | string | `"read-only"`: no file edits and no command execution. `"ask"`: every edit and every execution needs approval. `"auto"`: no ceiling beyond the launcher's (`E_PERMISSION_CEILING_INVALID`) |
| `tools` | array of strings | An allow-list of tool classes: `read` (read and search files), `edit` (create and modify files), `execute` (run commands), `web` (fetch and search the web), `delegate` (start other agents) |

- An unknown tool class **MUST** be ignored, with a warning (`W_UNKNOWN_TOOL`).
  *Why:* in an allow-list, ignoring a value can only remove capabilities, so a
  manifest written for a later minor revision stays safe in an older reader.
- A harness maps these classes to the tools of the CLI it drives.

```json
"permissions": { "ceiling": "read-only", "tools": ["read"] }
```

### 7.11 `requires`

What the agent needs beyond what a launcher usually has. Every entry is a
widening request (§ 8): readers report it (`I_REQUESTED_NOT_GRANTED`) and
never grant it from the repository.

| Key | Entry | Rules |
|---|---|---|
| `mcp` | `{ "slot", "access", "why" }` | `slot`: kebab-case name the environment binds to an MCP server. `access`: `"read"` or `"write"`. All three REQUIRED |
| `network` | `{ "host", "why" }` | `host`: a host name, without scheme, port or path; `*.` allowed as a prefix. Both REQUIRED |
| `tools` | `{ "name", "why" }` | `name`: a program or capability the agent needs, such as `gh`; not a path. Both REQUIRED |

- Every entry **MUST** carry a non-empty `why` (`E_FIELD_MISSING`). *Why:* the
  person approving the request decides with it; a request without a reason is
  either denied blind or granted blind.
- An MCP entry **MUST NOT** carry a command, URL or credential
  (`E_LOCATION_DECLARED`). *Why:* the same as for memory: which program runs is
  the environment's decision, not the repository's.

```json
"requires": {
  "mcp": [{ "slot": "issue-tracker", "access": "read", "why": "Reads the issues linked from a story" }],
  "network": [{ "host": "registry.npmjs.org", "why": "Checks the latest version of a package" }],
  "tools": [{ "name": "gh", "why": "Opens the pull request with the result" }]
}
```

### 7.12 `extensions`

Tool-specific settings, one block per tool.

- OPTIONAL. An object whose keys are tool namespaces: lowercase letters and
  digits, with `.` or `-` as separators (`E_EXTENSION_NAME_INVALID`).
- Each block **MUST** be an object and **SHOULD** carry its own `version`, a
  positive integer (`W_EXTENSION_VERSION_MISSING`,
  `E_EXTENSION_VERSION_INVALID`). *Why:* each tool evolves its block on its own
  schedule; without its own version a tool cannot change its block without
  breaking older copies of itself.
- Everything inside a block other than `version` is opaque to this
  specification: a reader **MUST NOT** report diagnostics about another tool's
  block. *Why:* one rule for all tools keeps the standard from having to know
  any of them.
- A tool reading its own block **MUST** apply § 8 to it: a field in an extension
  that widens is a request, never a grant. *Why:* otherwise `extensions` would
  be the way around every rule in this document.
- A tool's settings at the root instead of under `extensions` are unknown
  fields (§ 9.2).

```json
"extensions": { "terminus": { "version": 1 } }
```

### 7.13 `name` and `description`

They belong to `agent.md`, and the manifest **SHOULD NOT** repeat them
(`W_DUPLICATED_FIELD`). If `name` appears and differs from the name in
`agent.md`, the agent fails (`E_NAME_MISMATCH`). *Why:* the name already lives
in two places, the folder and the frontmatter. A third copy drifts, and a
reader that trusted the manifest would bind to a different agent than the one
that runs.

## 8. The three classes of fields

A manifest is written by whoever wrote the repository, and read on the machine
of whoever runs it. Those are often different people. So a harness treats each
field according to what it can do.

| Class | Fields | What a harness does |
|---|---|---|
| **Descriptive** | `$schema`, `scope`, `id`, `version`, `skills`, `memory.reach` | Shows it, and uses it to identify, list and load the agent. It grants nothing |
| **Narrowing** | `permissions.ceiling`, `permissions.tools` | Intersects it with what the launcher has. The effective limit is the most restrictive of the two |
| **Widening** | `requires.mcp`, `requires.network`, `requires.tools`, `memory.store: { slot }` | Never grants it from the repository. It is a request the person approves, bound to the source and to the agent's digest |

- A narrowing field **MUST NOT** widen anything. If the launcher runs read-only
  and the agent declares `ceiling: "auto"`, the run is read-only.
- A harness that cannot enforce a narrowing field **MUST NOT** run the agent as
  if it could: it **MUST** either refuse to run it or tell the person which
  limit is not enforced. *Why:* a limit that people read and nobody enforces is
  worse than no limit.
- A widening request **MUST NOT** be granted because of anything in the
  repository. Approval **MUST** be stored outside the repository and bound to
  the source identity and the agent's digest (§ 10.3); when the digest changes,
  approval **MUST** be asked again. *Why:* anyone who can push to the source
  could otherwise grant themselves access on every consumer's machine.
- A field whose class a reader does not know is not applied (§ 9).

## 9. Versioning and compatibility

### 9.1 What changes within a major version

- Within `specVersion: 1`, the specification only adds: new optional fields, new
  enumeration values where § 7 says unknown values are ignored, new diagnostic
  codes. It never removes a field, changes a type, or makes an optional field
  required.
- A change that is not additive **MUST** increase `specVersion` and publish a new
  schema file (`schema/agent.v2.json`) and tag (`v2`).
- Released revisions are listed in [`CHANGELOG.md`](CHANGELOG.md).

*Why:* a harness released today will read manifests written next year. It can
only do that safely if everything it does not know is either ignorable or
behind a version number it can check.

### 9.2 What a reader does with what it does not know

| It finds… | It does |
|---|---|
| An unknown field at the root of `agent.json` | Loads the agent and warns (`W_UNKNOWN_FIELD`) |
| An unknown key inside `memory`, `permissions` or `requires` | Loads the agent, ignores the key and warns (`W_UNKNOWN_FIELD`); a key that declares a location is `E_LOCATION_DECLARED` |
| An unknown tool class in `permissions.tools` | Ignores it and warns (`W_UNKNOWN_TOOL`) |
| An unknown frontmatter field | Loads the agent, ignores it and warns (`W_FRONTMATTER_UNKNOWN_FIELD`) |
| Another tool's extension block | Ignores it without a diagnostic |
| A `specVersion` it does not support | Does not load the agent, and says so (`E_SPEC_VERSION_UNSUPPORTED`) |

*Why warn and not reject:* a new optional field must not switch off agents in
every older reader. *Why warn and not ignore:* a field the author thinks is
applied and the reader silently drops is the hardest defect to find.

### 9.3 Reading and publishing

A reader works in one of two modes:

- **Reading** (the default): warnings do not fail an agent.
- **Strict** (`--strict` in the reference validator): every warning fails the
  agent. Repositories **SHOULD** validate in strict mode before publishing a
  shared agent. *Why:* when reading, a new field must not break an old reader;
  when publishing, an unknown field is almost always a typo.

## 10. Identity and memory

### 10.1 Who the agent is

An agent's **identity** is the pair *(source identity, agent key)*:

- The **source identity** is how the harness identifies the repository the agent
  comes from: for the consumer's own repository, the project; for a source, the
  harness's stable identifier of that source (for example, its canonical
  remote URL).
- The **agent key** is the `id` when the manifest declares one, and the `name`
  otherwise.

A harness **MUST NOT** include the commit, the digest or `version` in the
identity. *Why:* each update would then create a new agent and orphan its
memory.

Renaming an agent that declares an `id` keeps its identity. Renaming one
without an `id` creates a new agent; a harness **MAY** offer to migrate the old
memory, as an explicit action.

### 10.2 What ran

What ran is identified by the source identity, the commit (when the source is
a git repository) and the agent's digest. A harness **SHOULD** record these
three with every run. *Why:* `version` can lie; a hash cannot.

### 10.3 The agent digest

The digest of an agent folder is computed as follows:

1. List every regular file under the agent folder, recursively. Symbolic links
   are not followed and not listed.
2. For each file, take its path relative to the agent folder with `/` as
   separator, and the lowercase hexadecimal SHA-256 of its bytes.
3. Sort the entries by the UTF-8 bytes of the path.
4. Join them as lines of the form `<hash><two spaces><path><LF>`.
5. The digest is `sha256:` followed by the lowercase hexadecimal SHA-256 of that
   text, encoded as UTF-8.

A harness **SHOULD** compute it from the content as committed — for git, the
blobs — rather than from a checkout. *Why:* checkout line-ending conversion
changes the bytes, and the same commit would get two digests on two machines.
The reference validator reports it in `--json` output.

### 10.4 Where memory lives

| `memory.reach` | One memory per | Never crosses |
|---|---|---|
| `project` (default) | agent identity × project | the project |
| `agent` | agent identity × environment | the environment |

- With `reach: "agent"`, what the agent learns in the projects of one
  environment is gathered in one memory. A harness **MUST NOT** share it across
  environments. *Why:* the environment is the client boundary. Whether what an
  agent learned with one client may be used for another is not something a
  field in a repository gets to decide.
- The repository **MUST NOT** contain the memory. Memory is not part of the
  digest, and updating an agent **MUST NOT** modify its memory.
- Changing `reach` in a later version of the agent **MUST NOT** move or delete
  existing memory. Migration is an explicit action.

### 10.5 External memory

- `store: "local"` (default) is the harness's own storage.
- `store: { "slot": "<name>" }` asks for an external store. The environment
  binds the slot to a provider and its credentials; the repository only names
  it (§ 7.8).
- If the slot is not bound, is not approved, or the store fails, the agent
  **MUST** run without agent memory and **MUST** say so in the run. It **MUST
  NOT** fall back to local memory. *Why:* a silent fallback splits one memory
  into two stores that each hold half of what the agent learned, and nothing
  shows it.

What belongs in each kind of memory, and what never goes in either, is in
[GUIDE § 12](GUIDE.md#12-designing-memory).

## 11. Scope and import

### 11.1 In its own repository

A harness loads every agent declared in the repository it works on, whatever
its `scope`.

### 11.2 From a source

When a project uses another repository as a source of agents:

- A harness **MUST** offer only the source's agents with `scope: "shared"`.
- It **MUST NOT** make a `repository` agent disappear silently: it **SHOULD**
  list it as not exported, with the reason. *Why:* an agent that vanishes gets
  debugged as a broken one.
- A shared agent's paths and skills resolve against its source, at the same
  commit, never against the consumer (§ 12, H14).
- Name collisions **MUST** be resolved deterministically and shown. It is
  RECOMMENDED that the consumer's own agent win over an imported one, and that
  between two sources the project's declared source order decide. The agent
  that loses **SHOULD** be listed as shadowed, with the winner. *Why:* an order
  nobody sees decides which agent runs.

### 11.3 Agents without a manifest

Agents without `agent.json` have no declared scope. What a harness does with
them from a source is the harness's decision. It is RECOMMENDED to treat them
as legacy: import them as before, labelled "scope not declared". Readers
report `I_NO_MANIFEST`. *Why:* repositories declared agents before this
manifest existed, and consumers use them today; excluding them by default would
remove working agents without an error.

## 12. Harness conformance

A harness that claims conformance to this specification **MUST**:

| # | Requirement | Section |
|---|---|---|
| H1 | Load an agent from `agent.md` alone | § 2, § 11.3 |
| H2 | Accept UTF-8 with or without BOM, and CRLF, in `agent.md` and `agent.json` | § 3, § 7.1 |
| H3 | Warn about unknown fields and load the agent; never reject it for them | § 9.2 |
| H4 | Not load an agent whose `specVersion` it does not support, and say why | § 7.3 |
| H5 | Ignore other tools' extension blocks; apply § 8 to its own | § 7.12 |
| H6 | Show every agent that fails to load, with its diagnostic code. Never drop one silently | § 11.2 |
| H7 | Never grant a widening field from the repository; store approval outside it, bound to source and digest; ask again when the digest changes | § 8 |
| H8 | Intersect narrowing fields with the launcher's permissions, and refuse or warn when it cannot enforce one | § 8 |
| H9 | Key memory by identity; never share it across environments; when external memory fails, run without memory and say so | § 10 |
| H10 | Export only `shared` agents from a source; resolve collisions deterministically and show them | § 11 |
| H11 | Not write into the repository while reading it: no generated `id`, no lock file, no rewritten manifest | § 7.6 |
| H12 | Record source identity, commit and digest with each run | § 10.2 |
| H13 | Treat code spans and fenced blocks as code, never as mentions, wherever it reads mentions | § 5 |
| H14 | Resolve an agent's relative paths against its own folder and repository at the commit that ran, and tell the agent where its folder is | § 4, § 11.2 |
| H15 | Pass the `format` profile of the conformance corpus, and state the corpus version it passes | § 13 |

A harness **MAY** store locks, approvals and memory however it chooses, as long
as none of it is written into the repository.

## 13. Diagnostic codes

Codes are stable within a major version: a code is never renamed or given
another meaning. New codes may be added. A reader **SHOULD** report these codes
exactly; the messages are free text.

The **profile** says who must reproduce a code:

- `format`: every reader, including harnesses. These codes decide whether an
  agent loads.
- `authoring`: validators. These check the quality of the prompt and the
  consistency of the repository.

The conformance corpus (`conformance/`) marks each case with its profile.
`python scripts/run_conformance.py --profile format --command "<reader>"` tests
another implementation against it.

| Code | Level | Profile | Meaning | § |
|---|---|---|---|---|
| `E_AGENT_MD_MISSING` | error | format | The folder, or an `agent.json`, has no `agent.md` | 2 |
| `E_ENCODING` | error | format | A file is not UTF-8 | 3, 7.1 |
| `E_FRONTMATTER_MISSING` | error | format | `agent.md` does not start with a closed frontmatter block | 3 |
| `E_NAME_MISSING` | error | format | No `name` in the frontmatter | 3.1 |
| `E_NAME_FORMAT` | error | format | `name` is not ASCII kebab-case | 3.1 |
| `E_NAME_LENGTH` | error | format | `name` is longer than 60 characters | 3.1 |
| `E_NAME_RESERVED` | error | format | `name` is a reserved Windows device name | 3.1 |
| `E_NAME_FOLDER_MISMATCH` | error | format | `name` differs from the folder | 3.1 |
| `E_DESCRIPTION_MISSING` | error | format | No `description` | 3.2 |
| `E_BODY_EMPTY` | error | format | The body is empty | 4 |
| `E_SKILL_MD_MISSING` | error | format | An own skill folder has no `SKILL.md` | 6.1 |
| `E_SKILL_FRONTMATTER_MISSING` | error | format | An own skill's `SKILL.md` has no frontmatter | 6.1 |
| `E_SKILL_NAME_MISMATCH` | error | format | An own skill's `name` differs from its folder | 6.1 |
| `E_SKILL_DESCRIPTION_MISSING` | error | format | An own skill has no `description` | 6.1 |
| `E_MANIFEST_PARSE` | error | format | `agent.json` is not valid JSON | 7.1 |
| `E_MANIFEST_NOT_OBJECT` | error | format | `agent.json` is not an object | 7.1 |
| `E_MANIFEST_DUPLICATE_KEY` | error | format | A key is repeated | 7.1 |
| `E_FIELD_TYPE` | error | format | A field has the wrong JSON type | 7.2 |
| `E_FIELD_MISSING` | error | format | A required nested field is missing | 7.2 |
| `E_FIELD_VALUE` | error | format | A nested value is outside its allowed set | 7.2 |
| `E_SPEC_VERSION_MISSING` | error | format | No `specVersion` | 7.3 |
| `E_SPEC_VERSION_INVALID` | error | format | `specVersion` is not a positive integer | 7.3 |
| `E_SPEC_VERSION_UNSUPPORTED` | error | format | `specVersion` is newer than the reader supports | 7.3 |
| `E_SCOPE_MISSING` | error | format | A manifest without `scope` | 7.5 |
| `E_SCOPE_INVALID` | error | format | `scope` is not `repository` or `shared` | 7.5 |
| `E_ID_INVALID` | error | format | `id` does not match its pattern | 7.6 |
| `E_ID_DUPLICATE` | error | format | Two agents of one repository share an `id` | 7.6 |
| `E_VERSION_INVALID` | error | format | `version` is not SemVer 2.0.0 | 7.7 |
| `E_MEMORY_REACH_INVALID` | error | format | `memory.reach` is not `project` or `agent` | 7.8 |
| `E_MEMORY_STORE_INVALID` | error | format | `memory.store` is neither `"local"` nor `{ "slot" }` | 7.8 |
| `E_LOCATION_DECLARED` | error | format | The manifest declares a path, URL, command or secret for memory or a request | 7.8, 7.11 |
| `E_PATH_ESCAPE` | error | format | A path in `skills` leaves the repository | 7.9 |
| `E_SKILL_NOT_FOUND` | error | format | A path in `skills` has no `SKILL.md` | 7.9 |
| `E_PERMISSION_CEILING_INVALID` | error | format | `permissions.ceiling` is not a known value | 7.10 |
| `E_EXTENSION_NAME_INVALID` | error | format | An extension namespace has invalid characters | 7.12 |
| `E_EXTENSION_VERSION_INVALID` | error | format | An extension's `version` is not a positive integer | 7.12 |
| `E_NAME_MISMATCH` | error | format | `name` in the manifest differs from `agent.md` | 7.13 |
| `E_MENTION_UNDECLARED` | error | authoring | A mention names an agent that is not declared | 5 |
| `E_PATH_NOT_FOUND` | error | authoring | A path cited in the body does not exist | 4 |
| `W_FRONTMATTER_CLI_FIELD` | warning | format | `tools` or `model` in the frontmatter | 3 |
| `W_FRONTMATTER_UNKNOWN_FIELD` | warning | format | An unknown frontmatter field | 3 |
| `W_UNKNOWN_FIELD` | warning | format | An unknown manifest field | 9.2 |
| `W_UNKNOWN_TOOL` | warning | format | An unknown tool class in `permissions.tools` | 7.10 |
| `W_DUPLICATED_FIELD` | warning | format | `name` or `description` repeated in the manifest | 7.13 |
| `W_EXTENSION_VERSION_MISSING` | warning | format | An extension block without `version` | 7.12 |
| `W_DESCRIPTION_LONG` | warning | authoring | The description is longer than 1024 characters | 3.2 |
| `W_ROLE_MISSING` | warning | authoring | The body does not start with the role | 4 |
| `W_SECTION_MISSING` | warning | authoring | A recommended section is missing | 4 |
| `W_SCHEMA_NOT_PINNED` | warning | authoring | `$schema` points to a moving branch | 7.4 |
| `I_NO_MANIFEST` | info | format | No `agent.json`: scope is undeclared | 11.3 |
| `I_REQUESTED_NOT_GRANTED` | info | format | A widening request: requested, not granted | 8 |

## 14. Non-goals

These are out of version 1 on purpose. Each can be added later without breaking
anything, if someone names the behavior it would change; removing a field from
a published major version cannot be undone.

- **`kind` or any category field.** No reader behaves differently by category,
  and a field without behavior cannot be tested — a validator could only check
  that the value is in a list somebody has to maintain.
- **A declared database.** No reader can check that a schema, a migration and
  an access rule agree with an agent, and it would be one more store holding
  project state. Agents keep state in memory (§ 10) and in the repository's own
  files.
- **An agent registry.** A repository is already addressable, versioned and
  reviewable. A registry adds a server and an owner before anyone has shown what
  it would fix.
- **Signatures.** Integrity is covered by commit plus digest, and approval is
  bound to the digest (§ 8). Who may push to a repository is the hosting
  platform's access control, not a field in it.
- **Routing by `description`.** Choosing an agent by matching a request against
  descriptions guesses, and a wrong guess runs the wrong agent with the wrong
  limits. People and agents name the receiver (§ 5).
- **A `handoffs` list.** The body's mentions already declare handoffs, and
  readers check them. A second list would drift from the body.
- **Lock files and approval records.** Where a harness keeps them is the
  harness's decision; they never live in the repository (§ 12, H11).
- **Model and provider selection.** A model id belongs to one provider; which
  model runs is the person's decision.

## 15. Known limits

- **Instructions enter once.** A CLI reads the prompt when the run starts. After
  a context compaction in a long run, the agent may lose them, and nothing
  warns about it. Short, concrete prompts hold up better.
- **Two runs of one agent do not see each other.** What they share is memory,
  not state.
- **Nothing enforces the body.** A reader can check that sections and paths
  exist, not that the model follows them.
- **Older harnesses ignore `agent.json`.** A harness written before this
  manifest loads the agent from `agent.md` alone, including `repository`
  agents from a source. The manifest cannot force an older reader to apply it.

## Appendix A: a complete example

```
.agents/agents/story-reviewer/
  agent.md
  agent.json
```

```json
{
  "$schema": "https://raw.githubusercontent.com/danil-labs/agent-creator/v1/schema/agent.v1.json",
  "specVersion": 1,
  "id": "6f0d2a4e-8b1c-4e7a-9c3d-2b5f7e9a1c40",
  "scope": "shared",
  "version": "1.2.0",
  "memory": { "reach": "agent", "store": "local" },
  "permissions": { "ceiling": "read-only", "tools": ["read"] },
  "requires": {
    "mcp": [{ "slot": "issue-tracker", "access": "read", "why": "Reads the issues linked from the stories under review" }]
  },
  "extensions": { "terminus": { "version": 1 } }
}
```

What a conforming harness does with it, in a consumer project: offers the
agent, because it is `shared`; runs it read-only whatever the launcher has,
with only the read tools; keeps one memory for it across the projects of the
environment, keyed by its source and `id`; shows the MCP request as requested,
not granted, until the person approves it for this source and this digest;
and passes `extensions.terminus` to Terminus only.

## Appendix B: extension namespaces

Namespaces known to be in use. The fields of each block are defined by its
tool, not by this specification. To add one, open a pull request with the
namespace, the tool and where its block is documented.

| Namespace | Tool |
|---|---|
| `terminus` | [Terminus](https://github.com/danil-labs), a desktop harness for coding CLIs |

# agent-creator

This repository publishes the Agent Declaration Format: the specification
(`SPEC.md`), its JSON Schema, a conformance corpus, a reference validator, a
design guide, a template, examples and a skill. Changes here change what every
reader of the format must do, so they are held to the rules below.

## Commands

All three must pass before a change is merged. They need Python 3.9 or later
and nothing else. CI runs them on Linux and Windows
(`.github/workflows/validate.yml`).

```bash
python scripts/validate_agent.py --agents examples --no-paths   # the examples
python scripts/validate_agent.py --root . --strict              # this repository's own agents
python scripts/run_conformance.py                               # the corpus
```

## Rules

- **Everything is in English.** The format is global; a Spanish heading is
  accepted by the validator, but this repository is written in English.
- **Every rule in `SPEC.md` says why it exists**, or points to the section of
  `GUIDE.md` that does. A rule without a reason cannot be judged when someone
  proposes to change it.
- **A change to the format comes with a conformance case** that fails without
  it. `SPEC.md`, `schema/agent.v1.json`, `scripts/validate_agent.py` and
  `conformance/` change in the same pull request; one without the others is
  how two readers start to disagree.
- **Within `specVersion: 1`, only additions.** No field is removed, renamed or
  retyped, and no optional field becomes required (`SPEC.md` § 9). A breaking
  change is `specVersion: 2`, with its own schema file and tag.
- **Diagnostic codes never change meaning.** New codes may be added; existing
  ones are never renamed or reused.
- **The validator and the runner use the standard library only.** Anyone must
  be able to run them with a plain Python install.
- **`$schema` URLs point to the `v1` tag**, never to `main`.
- **No real client data**: no names of companies, people, products or
  providers in examples, cases or lessons. Describe the structure, not the
  content.
- **Files in `conformance/cases/011-bom-crlf/` and `conformance/cases/015-not-utf8/` are stored
  byte for byte.** Don't open and re-save them in an editor that normalizes
  encodings or line endings.

## Agents

| Agent | Scope | What it does | Skills |
|---|---|---|---|
| `docs-writer` | shared | Writes and updates documentation for agents, after measuring the repository | `measure-repository` (own) |
| `agent-designer` | shared | Designs agents with this format and runs the validator | `create-agent` (repository) |
| `docs-auditor` | shared | Reviews documentation against the code; read and run only | `audit-docs` (own) |

Their flows live in each `agent.md`, under `.agents/agents/`.

## Where each thing is documented

| File | What it answers |
|---|---|
| `README.md` | What the format is, what it makes possible, and how to start |
| `SPEC.md` | What a declaration must contain and what a reader must do |
| `GUIDE.md` | How to design good agents, teams, shared agents and memory, and why each rule exists |
| `conformance/README.md` | How the corpus is laid out and how to test a reader against it |
| `CONTRIBUTING.md` | How to propose a field or a rule |
| `CHANGELOG.md` | What changed in each release |

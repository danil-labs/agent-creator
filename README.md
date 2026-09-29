# Agent Declaration Format

[![Validate](https://github.com/danil-labs/agent-creator/actions/workflows/validate.yml/badge.svg)](https://github.com/danil-labs/agent-creator/actions/workflows/validate.yml)
[![Spec: v1](https://img.shields.io/badge/spec-v1-informational.svg)](SPEC.md)
[![Conformance: 48 cases](https://img.shields.io/badge/conformance-48%20cases-success.svg)](conformance/)

**An open format for declaring AI agents in a repository**, so that everyone on
a team —with whichever coding CLI they use— gets the same roles, the same
boundaries and the same limits.

An agent is a folder: a Markdown prompt that any CLI can read, an optional JSON
manifest that says what the prompt cannot, and the skills the agent brings. It
is versioned and reviewed by pull request, like code. It is to agents what
[Agent Skills](https://agentskills.io) is to methods.

```
.agents/agents/story-reviewer/
  agent.md          the prompt: name, description and instructions
  agent.json        optional: scope, identity, memory, limits and requests
  skills/           optional: the methods only this agent uses
```

The format belongs to no tool. It needs no runtime, no registry and no server.
A tool-specific setting lives in its own namespace, `extensions.<tool>`, and
every other tool ignores it.

## Agent, skill and AGENTS.md

Three things that are easy to confuse, and each has its place:

| | What it is | Where it lives | Example |
|---|---|---|---|
| **`AGENTS.md`** | The repository's rules. They apply to everyone | The repository root | "No real customer data, ever" |
| **Skill** | A method: how one thing is done, step by step | `skills/<name>/SKILL.md` | How to write a user story |
| **Agent** | A role: who does a job, with which files, where it stops, and whom it hands off to | `.agents/agents/<name>/` | The story writer, who writes stories and hands them to the reviewer |

The agent does not repeat the method: it loads the skill. When the method
changes, it changes in the skill, and every agent that uses it gets the change.

## What declaring agents makes possible

**A team, not a prompt.** A product lead that defines the problem, a writer that
produces, a reviewer that only reads, an architect that is the only one who
writes the technical documentation. Each one knows what it owns and what it
does not. Two agents never write the same file, so they never write it two
different ways.

**Handoffs that carry everything.** An agent names the next one —
`@story-reviewer`— and the message carries what is handed over, where it lives
and what is still open. The receiving agent doesn't see the conversation, and
the format is designed around that.

**Memory that survives a rename.** An agent can declare a stable `id`.
Whatever it learns is keyed by that `id`, not by its name, so renaming
`reviewer` to `story-reviewer` keeps every lesson. Memory never lives in the
repository, and it never crosses from one client's environment to another's.

**Agents shared across repositories.** Mark an agent `"scope": "shared"`, and
any project that uses your repository as a source can run it —with the
agent's own skills, resolved against your repository at the commit that ran.
Internal agents (`"scope": "repository"`) stay internal.

**Non-technical people using expert agents.** A team keeps its agents in one
meta-repository: the reviewer of contracts, the writer of release notes, the
auditor of documentation. Anyone opens a project that uses it as a source and
works with those agents by name, without writing a prompt. The limits come
with them: a reviewer declared read-only stays read-only, whoever runs it.

**Safe by construction.** A manifest is written by whoever wrote the
repository and read on the machine of whoever runs it. So fields that *narrow*
—a read-only ceiling, a tool allow-list— always apply, and fields that *widen*
—an MCP server, network access, an external memory— are requests a person
approves, never grants. A repository cannot name a path, URL, command or secret.

## Quick start

1. **Decide whether you need an agent or a skill**
   ([GUIDE § 1](GUIDE.md#1-agent-or-skill)). Usually it is a skill.
2. **Copy the template** into your repository:

   ```bash
   mkdir -p .agents/agents/<name>
   cp template/agent.md .agents/agents/<name>/agent.md
   cp template/agent.json .agents/agents/<name>/agent.json   # optional
   ```

3. **Fill it in** following [`SPEC.md`](SPEC.md) and the [guide](GUIDE.md).
   The smallest manifest is:

   ```json
   {
     "$schema": "https://raw.githubusercontent.com/danil-labs/agent-creator/v1/schema/agent.v1.json",
     "specVersion": 1,
     "scope": "repository"
   }
   ```

4. **Validate** (Python 3.9+, standard library only):

   ```bash
   python scripts/validate_agent.py --root <your-repository>
   python scripts/validate_agent.py --root <your-repository> --strict   # before publishing
   python scripts/validate_agent.py --root <your-repository> --json     # for CI and tools
   ```

5. **Try it on a real case** before calling it done
   ([GUIDE § 13](GUIDE.md#13-testing-it)).

Working with a coding agent? Give it the
[`create-agent`](skills/create-agent/SKILL.md) skill and ask it for the agent:
it follows the same path, writes the manifest and runs the validator.

## Compatibility

- **Claude Code.** `agent.md` uses the subagent frontmatter (`name`,
  `description`), so the same file works as `.claude/agents/<name>.md`.
- **Any CLI that reads Markdown prompts.** The body is plain instructions.
  Nothing in the format names a CLI or a model.
- **Agent Skills.** An agent's skills are Agent Skills, unchanged —
  `allowed-tools`, `scripts/`, `references/`, `assets/` and all.
- **Harnesses.** A tool that runs agents implements
  [SPEC § 12](SPEC.md#12-harness-conformance) and passes the `format` profile of
  the [conformance corpus](conformance/). [Terminus](https://github.com/danil-labs)
  is one such harness; its settings live in `extensions.terminus`, and nothing
  in the format depends on it.

## What is in this repository

```
SPEC.md                          the normative specification, version 1
GUIDE.md                         how to design an agent, a team, a shared agent and its memory
schema/agent.v1.json             JSON Schema (2020-12) of agent.json
conformance/                     the corpus every reader is measured against
scripts/validate_agent.py        the reference validator: stable codes, --strict, --json
scripts/run_conformance.py       runs the corpus against the validator or any other reader
template/                        agent.md and agent.json to start from
examples/                        a small team: a lead, a writer, a reviewer and an architect
skills/create-agent/             the skill that walks a coding agent through creating one
.agents/agents/                  this repository's own agents, shared and validated in strict mode
AGENTS.md                        the rules for working on this repository
CONTRIBUTING.md                  how to propose a field or a rule
CHANGELOG.md                     what changed in each release
```

### This repository's own agents

They are real, `shared`, and pass `--strict`. Use this repository as a source
and they work on yours:

| Agent | What it does |
|---|---|
| [`docs-writer`](.agents/agents/docs-writer/agent.md) | Writes and updates a project's documentation for agents —`AGENTS.md`, architecture, decisions— after measuring the repository |
| [`agent-designer`](.agents/agents/agent-designer/agent.md) | Designs a project's agents with this format and runs the validator until it passes |
| [`docs-auditor`](.agents/agents/docs-auditor/agent.md) | Reviews documentation against the code: dead paths, commands that don't run, promises the code doesn't keep |

## Contributing

Proposals are welcome, especially from people building harnesses. A new field
enters the format when it names a problem that shows today, the behavior a
reader changes because of it, and a conformance case that fails without it.
[`CONTRIBUTING.md`](CONTRIBUTING.md) describes the process, and the
[field proposal form](.github/ISSUE_TEMPLATE/field-proposal.yml) asks for
exactly that.

## Where it comes from

From a team that declared six agents for a real project and a harness that runs
them across several CLIs. The rules came out of what failed along the way, and
each one says why it exists ([GUIDE § 15](GUIDE.md#15-why-each-rule-exists)).

## License

No license has been chosen yet.

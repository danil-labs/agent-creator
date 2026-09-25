# agent-creator

How to declare agents in a repository so that anyone on the team, with whichever
coding CLI they use, gets the same working criteria.

An **agent** is a named role: who does which work, with which files, where it
stops, and whom it hands the result to. It lives in a versioned file and is
reviewed by pull request, like code.

This repository is the agent counterpart of the skill-creator repositories: a
spec, a design guide, a template, a worked example team, a skill that walks a
coding agent through creating one, and a validator.

## Agent, skill and AGENTS.md are not the same thing

| | What it is | Where it lives | Example |
|---|---|---|---|
| **`AGENTS.md`** | The repository's rules. They apply to everyone | The repository root | "No real customer data, ever" |
| **Skill** | A method: how one thing is done, step by step | `skills/<name>/SKILL.md` | How to write a user story |
| **Agent** | A role: who does it, with which criteria, and whom they hand off to | `.agents/agents/<name>/agent.md` | The story writer, who writes stories and hands them to the reviewer |

The agent does not repeat the method: it loads the skill. When the method
changes, it changes in the skill, and every agent that uses it gets the change.

## What is in this repository

```
README.md                         this file
SPEC.md                           the format: folder, frontmatter, name, body, own skills, memory
GUIDE.md                          how to design one agent, and a team of agents that do not overlap
template/agent.md                 the template to start from
examples/                         a small, complete team: a producer, a reviewer and an artifact owner
skills/create-agent/SKILL.md      the skill that guides the creation of an agent, step by step
scripts/validate_agent.py         the validator: format, name, sections, paths and handoffs
```

## Quick start

1. Read [`GUIDE.md`](GUIDE.md) § 1 to decide whether what you want is an agent
   or a skill.
2. Copy [`template/agent.md`](template/agent.md) to
   `.agents/agents/<name>/agent.md` in your repository.
3. Fill it in following [`SPEC.md`](SPEC.md) and the guide.
4. Validate it (Python 3, standard library only):

   ```bash
   python scripts/validate_agent.py --root <your-repository>
   ```

5. Try it on a real case before calling it done (`GUIDE.md` § 9).

If you work with a coding agent, give it the
[`skills/create-agent/`](skills/create-agent/SKILL.md) skill and ask it for the
agent: it follows the same path and runs the validator at the end.

## Where it comes from

From a team that declared six agents for a real project: a product lead, a story
writer and a story reviewer, a scrum master, an architect and a tech lead. The
rules here came out of what failed along the way, and each one says why it
exists.

The format is plain Markdown with YAML frontmatter. It is the one
[Terminus](https://github.com/danil-labs) reads for every CLI it drives, and it
is compatible with Claude Code subagents. [`SPEC.md`](SPEC.md) § 9 describes
how a harness is expected to read it.

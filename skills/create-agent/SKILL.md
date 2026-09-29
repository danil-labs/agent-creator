---
name: create-agent
description: Guide to create or fix an agent declared in a repository (.agents/agents/<name>/agent.md and its optional agent.json), end to end: whether it should be an agent or a skill, its boundary, the name and description, the body, the handoffs, the report, what it learns, the manifest (scope, id, memory, limits and requests), validation, and a test with a real case. Use it when asked to create, write, review or fix an agent, a subagent or a role; to turn a prompt that keeps being repeated into an agent; to prepare an agent for use in other repositories; or to assemble a team of agents that do not step on each other.
---

# create-agent

Takes an agent from the idea to a validated and tested declaration: an
`agent.md` and, when it needs one, an `agent.json`. The format is in `SPEC.md`
and the reason behind each rule is in `GUIDE.md`, at the root of the
agent-creator repository. This skill gives the order.

## Inputs

- The work the agent is going to do, with a real example.
- The agents that already exist in the repository (`.agents/agents/` and each
  CLI's own agent folder): without them the boundary cannot be drawn.
- The skills that already exist, inside and outside the agents.
- Whether the agent will be used by other repositories.

If the real example is missing, ask for it. An agent designed without a real case
is designed for the imagined case.

## Steps

1. **Decide whether it is an agent.** Use the table in `GUIDE.md` § 1. If what is
   missing is a method, it is a skill; if it is a rule for everyone, it is a line
   in `AGENTS.md`. Say so and stop if it is not an agent.
2. **Draw the boundary.** Write first what it does not do and whose job that is.
   Check the existing agents: nobody else should write where this one writes. If
   it collides with another, propose the boundary and ask before continuing.
3. **Name and description.** The name is the role, in ASCII kebab-case and in
   the team's language. The description says what it does, when to use it, and
   what it does not do.
4. **The method.** If a skill already exists, cite it by path. If not, write it
   separately before the agent, following the Agent Skills format. If only this
   agent uses it, it goes in the agent's `skills/` folder; if several do, it
   goes in the repository's skills folder and each agent lists it in its
   manifest's `skills`. Before moving an existing skill inside an agent, find out
   who else uses it.
5. **The body**, from `template/agent.md`:
   - the role in one or two sentences, with what it is not;
   - «What you work with», with real paths and what does not exist;
   - «How you work», with steps and criteria;
   - «Where you stop», with each handoff as a bare `@name` —never between
     backticks— and what the message carries;
   - «What you report», with the exact shape, and the verdict derived from rules
     if it rules on something;
   - «What you have learned», with real lessons or empty, and the memory rule.
6. **The manifest**, from `template/agent.json`, when the agent needs any of
   what `GUIDE.md` § 9 lists. Decide each field on purpose:
   - `scope`: `shared` if the job holds in any project, `repository` otherwise.
     Required once the file exists.
   - `id`: generate a new one, never copy it —
     `python -c "import uuid; print(uuid.uuid4())"`. You generate it now, once;
     no reader ever writes it.
   - `memory.reach`: `agent` if its heuristics hold across projects, `project`
     otherwise. `store` stays `local` unless the team has an external memory
     slot.
   - `permissions`: the narrowest ceiling and tool classes the role allows. A
     reviewer is `read-only` with `["read"]`.
   - `requires`: only what the role cannot work without, each with a `why` a
     person can approve. Never a path, URL, command or secret: name a slot.
   - For a shared agent: a `version`, and its own files cited relative to its
     folder (`GUIDE.md` § 11).
7. **The other agents.** If the new one receives or hands off work, update the
   `agent.md` on the other side of the handoff, and the agents table in the
   repository's `AGENTS.md`.
8. **Validate:**

   ```bash
   python scripts/validate_agent.py --root <repository>
   python scripts/validate_agent.py --root <repository> --strict   # shared agents, before publishing
   ```

   Fix every error. Each warning is either fixed or justified in your report.
   Codes are listed in `SPEC.md` § 13.
9. **Test with the real case.** Check three things: whether it stayed inside its
   boundary, whether the handoff carried what was needed, and whether the report
   had the declared shape. Whatever fails goes to the agent, or to the skill if it
   belongs to the method.

## Output

- `.agents/agents/<name>/agent.md`, validated, and `agent.json` if it needed one.
- The new or moved skills, if they were needed.
- The `agent.md` files on the other side of each handoff, updated.
- The validator's output.
- One line per boundary and manifest decision you made —scope, memory reach,
  limits, requests— so the person can confirm it.

**It is done when** the validator passes (in strict mode for shared agents), the
real case stayed inside the boundary, and no other agent writes where this one
writes.

## What not to do

- **Do not write an agent for what is a method.** That is a skill.
- **Do not copy the method into the agent.** It diverges on the first edit.
- **Do not invent paths, commands or lessons** to make the file look complete.
- **Do not add fields to the frontmatter.** `tools` and `model` tie the agent to
  a CLI; portable limits go in `agent.json` `permissions`.
- **Do not repeat `name` or `description` in `agent.json`.**
- **Do not copy an `id`.** Two agents with one `id` share one memory.
- **Do not put locations or secrets in the manifest.** The environment binds
  slots.
- **Do not give it a personality or motivational text.** They do not change any
  decision.

---
name: create-agent
description: Guide to create or fix an agent declared in a repository (.agents/agents/<name>/agent.md), end to end: whether it should be an agent or a skill, its boundary, the name and description, the body, the handoffs with other agents, the report, what it learns, validation, and a test with a real case. Use it when asked to create, write, review, or fix an agent, a subagent, or a role; to turn a prompt that keeps being repeated into an agent; or to assemble a team of agents that do not step on each other.
---

# create-agent

Takes an agent from the idea to a validated and tested `agent.md`. The format is
in `SPEC.md` and the reason behind each rule is in `GUIDE.md`, at the root of this
repository. This skill gives the order.

## Inputs

- The work the agent is going to do, with a real example.
- The agents that already exist in the repository (`.agents/agents/`): without
  them the boundary cannot be drawn.
- The skills that already exist, inside and outside the agents.

If the real example is missing, ask for it. An agent designed without a real case
is designed for the imagined case.

## Steps

1. **Decide whether it is an agent.** Use the table in `GUIDE.md` § 1. If what is
   missing is a method, it is a skill; if it is a rule for everyone, it is a line
   in `AGENTS.md`. Say so and stop if it is not an agent.
2. **Draw the boundary.** Write first what it does not do and whose job that is.
   Check the existing agents: nobody else should write where this one writes. If
   it collides with another, propose the boundary and ask before continuing.
3. **Name and description.** The name is the role, in ASCII `kebab-case` and in
   the team's language. The description says what it does, when to use it, and
   what it does not do.
4. **The method.** If a skill already exists, cite it by path. If not, write it
   separately before the agent. If only this agent uses it, it goes in its
   `skills/` folder. Before moving an existing skill inside an agent, find out who
   else uses it.
5. **The body**, with the template (`template/agent.md`):
   - the role in one or two sentences, with what it is not;
   - «What you work with», with real paths and what does not exist;
   - «How you work», with steps and criteria;
   - «Where you stop», with each handoff by `@name` and what the message carries;
   - «What you report», with the exact shape, and the verdict derived from rules
     if it rules on something;
   - «What you have learned», with real lessons or empty, and the memory rule.
6. **The other agents.** If the new one receives or hands off work, update the
   `agent.md` on the other side of the handoff, and the agents table in the
   repository's `AGENTS.md`.
7. **Validate:**

   ```bash
   python scripts/validate_agent.py --root <repository>
   ```

   Fix every `ERROR`. Each `WARNING` is either fixed or justified.
8. **Test with the real case.** Check three things: whether it stayed inside its
   boundary, whether the handoff carried what was needed, and whether the report
   had the declared shape. Whatever fails goes to the agent, or to the skill if it
   belongs to the method.

## Output

- `.agents/agents/<name>/agent.md`, validated.
- The new or moved skills, if they were needed.
- The `agent.md` files on the other side of each handoff, updated.
- One line per boundary decision you made, so the person can confirm it.

**It is done when** the validator passes, the real case stayed inside the
boundary, and no other agent writes where this one writes.

## What not to do

- **Do not write an agent for what is a method.** That is a skill.
- **Do not copy the method into the agent.** It diverges on the first edit.
- **Do not invent paths, commands, or lessons** to make the file look complete.
- **Do not add fields to the frontmatter.** `tools` and `model` tie the agent to
  a CLI.
- **Do not give it a personality or motivational text.** They do not change any
  decision.

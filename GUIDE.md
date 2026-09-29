# Guide to designing agents

The [specification](SPEC.md) says what shape an agent has. This guide says how
to write one that is useful, how to put together a team of agents that don't
step on each other, and how to design agents that other repositories can use.

## Contents

1. [Agent or skill?](#1-agent-or-skill)
2. [The boundary](#2-the-boundary)
3. [The name and the description](#3-the-name-and-the-description)
4. [The body, part by part](#4-the-body-part-by-part)
5. [Handoffs](#5-handoffs)
6. [The report](#6-the-report)
7. [What it learns](#7-what-it-learns)
8. [A team of agents](#8-a-team-of-agents)
9. [The manifest](#9-the-manifest)
10. [Limits and requests](#10-limits-and-requests)
11. [Designing a shared agent](#11-designing-a-shared-agent)
12. [Designing memory](#12-designing-memory)
13. [Testing it](#13-testing-it)
14. [What doesn't belong in an agent](#14-what-doesnt-belong-in-an-agent)
15. [Why each rule exists](#15-why-each-rule-exists)
- [Checklist](#checklist)

## 1. Agent or skill?

Before you write, decide what is missing. Most of the time, what is missing is
a skill.

| If what is missing is… | Write… |
|---|---|
| A procedure: how something is done, step by step | A **skill** |
| A rule that applies to the whole repository | A line in **`AGENTS.md`** |
| Someone who does a job with their own judgment, knows where they stop and who they hand off to | An **agent** |
| A second pair of eyes with judgment different from the producer's | A reviewer **agent**, separate from the producer |

The sign that you need an agent is that the work has an **owner and a
boundary**: someone does it, someone else receives it, and what one does the
other must not do.

An agent without a skill is usually a long prompt. An agent that repeats its
skill drifts away from it at the first edit.

## 2. The boundary

The first thing you write for an agent is what it does **not** do.

- **One sentence for the role, with its negation.** "You write the stories. You
  don't rule on whether they are ready, you don't plan them and you don't design
  the solution." The negation names whose job it is: "—that belongs to
  @story-reviewer—".
- **One writer per artifact.** If two agents can write to the same document, at
  some point they write it differently. Decide who owns each thing (a directory,
  a type of document, a table) and have the others ask the owner.
- **The reviewer only reads.** If the reviewer corrects, there is no review
  anymore: what you get is a second writer without judgment of its own. Declare
  it in the manifest too: `"permissions": { "ceiling": "read-only" }` (§ 10).
- **Nobody decides what isn't theirs.** An agent does not approve a person's
  gate, does not decide priority unless it owns the plan, and does not close a
  technical decision unless it is the architect. It flags it and passes it to
  whoever does.

## 3. The name and the description

**The name** is the role, not the person or the tool: `story-reviewer`, not
`reviewer-gpt` or `ana`. It is ASCII kebab-case and in the team's language.

**The description** says when to hand it something. It has three parts:

1. What it does, in one sentence.
2. When to use it: the phrases people use to ask for it and the handoffs that
   trigger it ("…and when @story-writer delivers a story").
3. What it doesn't do, if it could be confused with another agent ("Read-only.",
   "Does not write stories.").

```yaml
description: Facilitates sprint-based delivery —kick-off, planning, daily, refinement, review and retro— with a log of impediments and risks. Use it when asked to plan or close a sprint, prepare a ceremony or find out whether something is done, and when @story-reviewer approves a story. Does not write or review stories.
```

## 4. The body, part by part

### What you work with

A «File · What for» table with **real paths**. Each row says what the file is
opened for, not what it contains.

```markdown
| File | What for |
|---|---|
| `skills/user-stories/SKILL.md` | The method. Read it in full before the first story of the session |
| `docs/architecture/decisions/` | The `status:` of each decision. One in `BLOCKED` blocks the stories that depend on it |
```

Then, what does **not** exist, stated as such: "There is no impediment log in
the repository: it gets agreed on at the kick-off. In the meantime, you deliver
them in the conversation." An agent that doesn't know something is missing
makes it up.

Cite your skills by path even if the harness announces them to you: that way
the agent finds them in any CLI.

### How you work

Numbered steps, each with its criterion. What sets a good agent apart is the
judgment, not the list:

- Bad: "Review the story carefully."
- Good: "Start with the package index, not with the first story. Compare the
  inventory against the pages before reading the detail: a story in the index
  with no page is already a finding."

If the method is already in a skill, don't copy it: say "with your skill X" and
write here only what belongs to the role and not to the method.

### Where you stop

When you are done and who you hand off to. See § 5.

### What you report

The exact shape of the output. See § 6.

### What you have learned

What the role learned through use. See § 7.

## 5. Handoffs

- **Name the next agent with `@`, in prose**, and say what you pass on in each
  case:

  ```markdown
  - **Changes requested** or **rejected** → to @story-writer, with the findings as they are.
  - **Approved** → to @scrum-master, with the story, the verdict and the traffic light.
  ```

  Write the mention bare, not between backticks. Code is code: the validator
  ignores anything inside backticks, so `` `@theme` `` in a CSS note is never
  read as an agent — and neither is a handoff you put in code.
- **The message carries everything.** The other agent doesn't see your
  conversation. Say what you are passing on, where the current version lives,
  what changed since last time and what you left open.
- **Loops are between two.** If the reviewer sends a story back, the loop is
  between the writer and the reviewer. The planner stays out of it: it receives
  the story once it comes out approved.
- **Nobody skips a step.** If the writer delivered straight to the planner, the
  review would exist on paper and not in the flow.
- **What requires a person's decision gets asked to the person.** An agent does
  not settle a business question "because the answer seems obvious".

## 6. The report

- **Verdict first.** Whoever reads the report decides from the first line.
- **The verdict comes from rules, not from an impression.** If the agent
  rules on something, define classes of finding and derive the verdict from
  them:

  | Verdict | When |
  |---|---|
  | rejected | There is at least one blocking finding |
  | changes requested | No blockers, but at least one inconsistency or something undefined |
  | approved | Only minor findings remain, and they are listed anyway |

- **Each finding says what is wrong, where and why.** A finding without a
  location can't be fixed; one without a reason is an opinion. Drop it.
- **Say what you didn't review.** Pages you didn't get to, versions you didn't
  confirm. A report that keeps quiet about what it didn't see looks more
  complete than it is.
- **Don't invent findings to look thorough.** If it's fine, say so in one line.

## 7. What it learns

«What you have learned» is the section that makes an agent improve with use.

- **Start with real lessons or leave it empty.** A lesson made up so the section
  doesn't look empty teaches something false. If the project has already hit a
  problem the role must avoid, that is the first line.
- **One line per lesson, with the why.** "A filled-in template is not a
  sufficient story: the ones in the first epic had every section and still
  couldn't be built."
- **If the lesson changes the method, it goes into the skill.** That way every
  agent that uses it gets it.
- **Close with the memory rule:** the role's heuristics go to the agent's
  memory, project facts go to the project's memory, and none of it is written
  into the repository as a log. § 12 explains how to design that memory.

## 8. A team of agents

A team works when every job has an owner and every handoff has a receiver. This
is what the team in the [examples](examples/) looks like:

```
product-lead ──problem statement──► story-writer ──story──► story-reviewer
                                         ▲                        │
                                         └──── changes requested ─┤
                                                                  │ approved
                                                                  ▼
                                                              architect

The architect is the only one who writes to the technical documentation. The
writer and the reviewer flag it when a story clashes with a contract.
```

Rules for putting it together:

1. **An ownership table before the agents.** Which artifact belongs to whom, and
   who only reads.
2. **The shared method is read by path, not copied.** The reviewer reviews with
   the writer's skill: if the method changes, it changes for both.
3. **A skill used by only one agent lives inside it.** One used by several lives
   outside, and each agent that uses it lists it in its manifest's `skills`.
   Before moving a skill inside an agent, check who else uses it (see § 15).
4. **No agent repeats another's rules.** If two agents say the same thing, after
   the first edit they say different things.
5. **The repository's `AGENTS.md` lists the agents in a table**, with what each
   one does, its scope and which skills it brings. It doesn't describe their
   flows: that lives in each `agent.md`.

## 9. The manifest

`agent.md` is enough for an agent to work. Add `agent.json` when you need to
say something the prompt cannot:

| You need to… | Field |
|---|---|
| Say whether other repositories may use this agent | `scope` |
| Rename the agent later without losing what it learned | `id` |
| Keep one memory for the agent across projects | `memory.reach: "agent"` |
| Make it read-only, or limit its tools, in every CLI | `permissions` |
| Declare that it needs an MCP server, network access or a program | `requires` |
| Configure one specific tool | `extensions.<tool>` |

Start small. The smallest manifest is two fields:

```json
{
  "$schema": "https://raw.githubusercontent.com/danil-labs/agent-creator/v1/schema/agent.v1.json",
  "specVersion": 1,
  "scope": "repository"
}
```

Practical rules:

- **Once a manifest exists, `scope` is required.** Decide it on purpose: is this
  agent about *this* project (`repository`), or is its job useful in any project
  (`shared`)? A release manager for your app is `repository`; a reviewer of user
  stories is `shared`.
- **Generate the `id` when you create the agent, and never touch it again.**
  `python -c "import uuid; print(uuid.uuid4())"` is enough. If you copy a folder
  to start a new agent, generate a new one: the validator fails two agents with
  the same `id` (`E_ID_DUPLICATE`), because they would share a memory.
- **Don't repeat `name` or `description`.** They live in `agent.md`.
- **Point `$schema` to the `v1` tag, not to `main`.** Editors use it to
  autocomplete; readers ignore it.
- **Tool settings go in `extensions.<tool>`, with their own `version`.** Never
  at the root: the root belongs to the standard.

## 10. Limits and requests

A manifest is read on the machine of whoever runs the agent, who is often not
whoever wrote it. So the format splits fields by what they can do
([SPEC § 8](SPEC.md#8-the-three-classes-of-fields)):

- **Limits narrow, and they always apply.** `permissions.ceiling` and
  `permissions.tools` can only take capabilities away. Declare them wherever
  the role allows it: a reviewer is `read-only` with `["read"]`; an agent that
  runs checks but must not edit has `["read", "execute"]`. A harness intersects
  them with the launcher's permissions, so a limit never hurts a launcher that
  already has less.
- **Requests widen, and they never apply by themselves.** `requires` and an
  external memory slot are requests the person approves, per source and per
  version of the agent. Write every `why` for that person: "Reads the issues
  linked from a story" gets approved; "needed" gets denied.
- **Never write a location.** No paths, URLs, commands or tokens. Name a slot
  (`"slot": "issue-tracker"`) and let each environment bind it to its own
  server. This is also what makes a shared agent portable: each consumer binds
  the slot to what it has.
- **Ask for the least.** `"access": "read"` unless the role writes. Every
  request you add is one more approval between a new consumer and a working
  agent.

## 11. Designing a shared agent

A shared agent (`"scope": "shared"`) runs in repositories you have never seen.
Design it for that.

- **Its job holds in any project.** "Review user stories against the definition
  of ready" is shared; "review stories for the payments epic" is not. If the
  body needs to know this project's facts, it is a `repository` agent.
- **Everything it needs travels with it.** Put its skills inside its folder and
  cite them relative to it: `skills/review/SKILL.md`, not
  `.agents/agents/story-reviewer/skills/review/SKILL.md`. In a consumer, the
  agent's folder lives wherever the harness keeps the source, and a harness
  resolves agent-relative paths against it. A skill from the source's shared
  skills folder goes in `skills`; the harness resolves it against the source.
- **Paths to the consumer's files are placeholders, not facts.** Say "the
  project's `AGENTS.md`" or "`<docs>/decisions/`", and tell the agent to look
  and to say what it did not find.
- **Handoffs name roles the consumer is expected to have.** A shared reviewer
  handing to @story-writer works where there is a story writer. Say what to do
  when the receiver does not exist: "if there is no @story-writer, return the
  ruling to whoever asked".
- **Version it for people.** Bump `version` following SemVer when behavior
  changes, and tag the commit `agents/<name>/v<version>`. Harnesses don't
  decide anything from the number — they identify what ran by commit and
  digest — but people read it when they approve an update.
- **Validate with `--strict` before publishing.** An unknown field that is a
  warning for readers is almost always a typo for the author.

## 12. Designing memory

An agent learns in four places, and each thing goes to exactly one of them:

| What it learned | Where it goes |
|---|---|
| Something that changes how it does its job **in this repository** | A line under «What you have learned», in its `agent.md`, by pull request |
| A heuristic of its role that holds in any project | Its agent memory |
| A fact about this project: a decision, a convention, where something lives | The project memory |
| Something that changes the **method** | The skill, not the agent |

The manifest decides where the agent memory lives:

- **`reach: "project"` (the default)** keeps one agent memory per project. Pick
  it for `repository` agents, and for shared agents whose heuristics depend on
  the project they learned them in.
- **`reach: "agent"`** gathers what the agent learns across all the projects of
  one environment into one memory. Pick it for shared agents whose heuristics
  are about the role: "a story that names no error case is always *undefined*".
  It never crosses environments: what an agent learns with one client is not
  available to another.
- **Give the agent an `id`** if its memory matters. Memory is keyed by source
  and `id` (or name, without one); with an `id`, renaming the agent keeps it.
- **`store: "local"` (the default)** keeps memory in the harness. Use
  `{ "slot": "<name>" }` only when a team really shares an external memory
  service. If the slot is missing or down, the agent runs without memory and
  says so. It never falls back to local memory, because that would split one
  memory into two halves.

What never goes into agent memory: client facts (they belong to the project
memory), secrets, and anything that is really a change to the method.

## 13. Testing it

1. **Run the validator.** It checks the frontmatter, the name, the sections,
   the manifest, that paths exist and that every mention is a declared agent:

   ```bash
   python scripts/validate_agent.py --root <your-repository>
   python scripts/validate_agent.py --root <your-repository> --strict   # before publishing
   ```

2. **Give it a real case**, not one made up so it comes out right. For a
   reviewer: a package a person has already reviewed, and compare findings.
3. **Look at three things in the response:** whether it stayed within its
   boundary, whether the handoff carried everything needed and whether the
   report had the shape its `agent.md` specifies.
4. **What failed goes into «What you have learned»**, or into the skill if it
   belongs to the method.

If you are writing a reader of the format rather than an agent, run the
conformance corpus against it: `python scripts/run_conformance.py --profile
format --command "<your reader>"` ([`conformance/`](conformance/README.md)).

## 14. What doesn't belong in an agent

- **Motivational text or invented personality.** "You are a passionate
  expert…" doesn't change any decision.
- **Generic lists.** "Be clear, be concise, be precise" applies to everything
  and guides nothing.
- **Paths or commands that don't exist.** The agent will go looking for them.
- **Instructions that contradict each other or overlap with another agent's.**
- **Extra frontmatter fields.** Each one ties the agent to a CLI. Portable
  limits go in `agent.json`.
- **The full method.** It goes in the skill.
- **Project state that goes stale:** "there are 36 open questions today".
  Tomorrow it's false. Say where to look it up.
- **Locations and secrets in the manifest.** Name a slot.

## 15. Why each rule exists

These rules came out of what failed in real projects and in the design of this
format.

| Rule | What happened |
|---|---|
| Check who uses a skill before moving it inside an agent | The specialist skills were moved into the writer agent. A session that was writing stories without running as that agent lost them halfway through the work and offered to continue "in the role, without the skill". That is exactly what the method forbids: a validation written without loading the area's skill comes out made up |
| Cite skills by path | Same reason: with the path, any session can open the skill, even if the harness doesn't announce it |
| Old copies keep teaching what was already deleted | A checkout on an old branch kept offering a skill that had been removed as obsolete. The source of agents and skills is the current branch |
| One writer per artifact | After the calculation changed from one model to another, four documents kept assuming the old one, with no warning. Nobody owned bringing them up to date |
| The reviewer uses the producer's skill, without a copy | The review of an epic found gaps in stories written with the skill. With two copies of the method nobody would know which one was wrong |
| The verdict comes from classes of finding | A verdict based on impression changes from one reviewer to another on the same story |
| The handoff message carries everything | The receiving agent doesn't see the conversation. A "review US-06" without where it lives or what changed forces it to ask |
| Real lessons or nothing | An invented lesson stays written down as truth and the next session applies it |
| The repository is not a log | The status, contradiction and lessons-learned logs went stale and contradicted the documents they summarized |
| Code is never a mention | The previous validator read `` `@theme` ``, a CSS directive in a note, as a handoff to an undeclared agent, and failed two agents that the harness loaded fine. Two readers of one file disagreed, and the one people didn't see was wrong |
| Unknown fields warn, in every reader | One reader rejected unknown frontmatter fields and another ignored them silently. The same file passed in one and failed in the other |
| `scope` is required once there is a manifest | Defaulting to `shared` leaks a project's internal agents into every consumer; defaulting to `repository` makes agents consumers already use disappear without an error |
| What ran is commit plus digest, not `version` | A version number nobody is forced to bump can lie; a hash of the folder cannot |
| Memory never falls back silently | A silent fallback from an external store to local memory leaves half of what the agent learned in each place, and nothing shows it |
| The repository names slots, never locations | A manifest that could name a path or URL for memory could point it at a credentials folder, or at a server of the author's choosing |

## Checklist

- [ ] It is an agent, not a skill or an `AGENTS.md` rule.
- [ ] The name is the role, in ASCII kebab-case, same as its folder.
- [ ] The description says what it does, when to use it and what it doesn't do.
- [ ] The frontmatter has only `name` and `description`.
- [ ] The role fits in one or two sentences and says what it doesn't do.
- [ ] Every cited path exists, or the text says it doesn't exist.
- [ ] The method is in a skill, cited by path, and not copied into the body.
- [ ] Every handoff names the receiver with a bare `@name` and says what the message carries.
- [ ] No other agent writes to what this one writes.
- [ ] The report has a fixed shape, and the verdict comes from rules.
- [ ] «What you have learned» has only real lessons, and the memory rule.
- [ ] If it has a manifest: `scope` is decided on purpose, the `id` is new, and there are no locations or secrets.
- [ ] Limits are declared wherever the role allows them; every request has a `why`.
- [ ] If it is shared: its files travel with it, cited relative to its folder, and it passes `--strict`.
- [ ] The validator passes.
- [ ] It was tested with a real case.

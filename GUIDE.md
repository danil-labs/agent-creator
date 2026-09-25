# Guide to creating agents

The [specification](SPEC.md) says what shape an agent has. This guide says how
to write one that is useful, and how to put together a team of agents that
don't step on each other.

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
  the solution." The negation names whose job it is: `—that belongs to @story-reviewer—`.
- **One writer per artifact.** If two agents can write to the same document, at
  some point they write it differently. Decide who owns each thing (a directory,
  a type of document, a table) and have the others ask the owner.
- **The reviewer only reads.** If the reviewer corrects, there is no review
  anymore: what you get is a second writer without judgment of its own.
- **Nobody decides what isn't theirs.** An agent does not approve a person's
  gate, does not decide priority unless it owns the plan, and does not close a
  technical decision unless it is the architect. It flags it and passes it to
  whoever does.

## 3. The name and the description

**The name** is the role, not the person or the tool: `story-reviewer`, not
`reviewer-gpt` or `ana`. It is ASCII `kebab-case` and in the team's language.

**The description** says when to hand it something. It has three parts:

1. What it does, in one sentence.
2. When to use it: the phrases people use to ask for it and the handoffs that
   trigger it ("…and when `@story-writer` delivers a story").
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
| `.agents/agents/story-writer/skills/user-stories/SKILL.md` | The method. Read it in full before the first story of the session |
| `architecture/01-decisions/` | The `status:` of each decision. One in `BLOCKED` blocks the stories that depend on it |
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

- **Name the next agent with `@`**, and say what you pass on in each case:

  ```markdown
  - **Changes requested** or **rejected** → to `@story-writer`, with the findings as they are.
  - **Approved** → to `@scrum-master`, with the story, the verdict and the traffic light.
  ```

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
  into the repository as a log.

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
   outside. Before moving a skill inside an agent, check who else uses it (see
   § 11).
4. **No agent repeats another's rules.** If two agents say the same thing, after
   the first edit they say different things.
5. **The repository's `AGENTS.md` lists the agents in a table**, with what each
   one does and which skills it brings. It doesn't describe their flows: that
   lives in each `agent.md`.

## 9. Testing it

1. **Run the validator.** It checks the frontmatter, the name, the sections,
   that the paths exist and that every `@` is a declared agent:

   ```bash
   python scripts/validate_agent.py --root <your-repository>
   ```

2. **Give it a real case**, not one made up so it comes out right. For a
   reviewer: a package a person has already reviewed, and compare findings.
3. **Look at three things in the response:** whether it stayed within its
   boundary, whether the handoff carried everything needed and whether the
   report had the shape its `agent.md` specifies.
4. **What failed goes into «What you have learned»**, or into the skill if it
   belongs to the method.

## 10. What doesn't belong in an agent

- **Motivational text or invented personality.** "You are a passionate
  expert…" doesn't change any decision.
- **Generic lists.** "Be clear, be concise, be precise" applies to everything
  and guides nothing.
- **Paths or commands that don't exist.** The agent will go looking for them.
- **Instructions that contradict each other or overlap with another agent's.**
- **Extra frontmatter fields.** Each one ties the agent to a CLI.
- **The full method.** It goes in the skill.
- **Project state that goes stale:** "there are 36 open questions today".
  Tomorrow it's false. Say where to look it up.

## 11. Why each rule exists

These rules came out of what failed in a real project.

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

## Checklist

- [ ] It is an agent, not a skill or an `AGENTS.md` rule.
- [ ] The name is the role, in ASCII `kebab-case`, same as its folder.
- [ ] The description says what it does, when to use it and what it doesn't do.
- [ ] The frontmatter has only `name` and `description`.
- [ ] The role fits in one or two sentences and says what it doesn't do.
- [ ] Every cited path exists, or the text says it doesn't exist.
- [ ] The method is in a skill, cited by path, and not copied into the body.
- [ ] Every handoff names the receiver with `@` and says what the message carries.
- [ ] No other agent writes to what this one writes.
- [ ] The report has a fixed shape, and the verdict comes from rules.
- [ ] «What you have learned» has only real lessons, and the memory rule.
- [ ] The validator passes.
- [ ] It was tested with a real case.

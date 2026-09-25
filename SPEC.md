# Specification

The format of an agent declared in a repository. What this document says
**must** is what the validator checks; what it says **should** is judgment, and
the [guide](GUIDE.md) explains why.

## 1. Where it lives

```
<repository>/
  .agents/agents/
    <name>/
      agent.md                  the agent: frontmatter + instructions
      skills/                   optional: the skills only this agent uses
        <skill>/
          SKILL.md
          references/           what the skill opens when it needs it
          templates/            the templates it fills in
```

- Each agent **must** be a folder with its name and, inside it, its `agent.md`.
- `.agents/agents/` is the neutral folder: it belongs to no CLI. A harness that
  drives several CLIs reads it for all of them.
- Each CLI also has its own folder with the same shape, `<dir>/agents/`, where
  `<dir>` is that CLI's configuration folder (`.claude`, `.codex`, …). Claude
  Code reads its subagents from `.claude/agents/<name>.md`, one loose file per
  agent, in the same format. If your team also runs a CLI without a harness in
  front, publish the same agent there too. If you keep two copies they drift:
  generate one from the other or point one at the other; never edit them
  separately.
- The loose form, `<dir>/agents/<name>.md`, is still readable because it is the
  one CLIs write into their own folders. To declare an agent for the project,
  use the folder form.

## 2. The name

- It **must** be ASCII `kebab-case`: lowercase letters, digits and single
  hyphens, no leading or trailing hyphen, no `--`, 60 characters at most.
- It **must** match its folder name.
- It **must** be unique in the repository. When a name is repeated, the neutral
  folder wins over a CLI's own folder: if the CLI's folder won, the same name
  the project declares for everyone would be bound to one CLI without the shared
  declaration saying so, and the difference would only show up when someone
  switched accounts.
- It **should** be written in the team's language. `story-writer` passes the
  validator just as `redactor-de-historias` does.
- Renaming an agent does **not** rename what it already signed: it is a new
  agent.

## 3. The frontmatter

```yaml
---
name: story-reviewer
description: Reviews stories that are already written and rules whether they can be built — approved, with changes, or rejected — with every finding located and justified. Use it when someone asks to review a story or a batch, or when @story-writer hands one over. It only reads.
---
```

| Field | | What it decides |
|---|---|---|
| `name` | **must** | The stable identifier. It is what people write to delegate (`@name`) and what stays signed on what the agent produces |
| `description` | **must** | When work is handed to it, and what it does not do. The person choosing an agent reads it, and so does the CLI |
| `tools` | should not | The allowed tools, in one specific CLI's names. It binds the agent to that CLI |
| `model` | should not | The model it runs with. A model id belongs to one provider, so it also binds the agent to one CLI |

- The frontmatter **must** have `name` and `description`. Any other field is a
  validation error, except `tools` and `model`, which the validator accepts with
  a warning.
- **No field says which CLI it runs with.** An agent that only works with one
  CLI is not a project agent: it is personal configuration. Which binary runs it
  is decided by the person opening the task, with the accounts they have.
- **Nothing in the frontmatter is a permission.** An agent cannot grant itself
  anything the task it runs in does not have. A harness may pass `tools` and
  `model` through to the CLI that understands them; it does not enforce them
  itself.
- **The `description` does not route.** Nobody picks an agent by matching text
  against it. It is shown to whoever chooses, and sent to the CLI.

## 4. The body

The body is the instructions, and it goes to the model as is. It **must**
exist: without a body, an agent is a name with no criteria, and a task title
already gives you that.

It **should** have these parts, in this order. The validator checks that the
headings are present; section names may be in English or in Spanish.

| Part | Heading | What it holds |
|---|---|---|
| Role | *(no heading, at the top)* | One or two sentences in the second person: what you do and what you do **not** do |
| What you work with | `## What you work with` | The real files by path, in a "File · What for" table. What does not exist is stated as such |
| How you work | `## How you work` (or `How you review`, `How you plan`…) | Concrete steps and decision criteria |
| Where you stop | `## Where you stop` | When you are done, whom you hand off to with `@name`, and what the message carries |
| What you report | `## What you report` | The exact shape of the output |
| What you have learned | `## What you have learned` | Real lessons of the role, which grow with use, and the memory rule |

- Every path the body cites **must** exist in the repository, or say that it
  does not.
- Every `@name` the body mentions **must** be a declared agent.
- The body **should** be written in the language the models you use follow
  best. For most teams that is English, even when the team's own documents are
  not. What a person reads on screen belongs to the harness's interface, not to
  the body.

## 5. The agent's skills

- A skill that **only** one agent uses lives inside it, in
  `<name>/skills/<skill>/`. One that several agents use lives outside, in the
  repository's skills folder.
- Each skill **must** have its `SKILL.md` with `name` and `description` in the
  frontmatter, and its `name` **must** match its folder.
- A harness announces an agent's own skills **only in turns that run as that
  agent**. A session that does not run as the agent does not see them.
- That is why the body **should** cite its skills by path under "What you work
  with". That way the agent finds them even when the harness does not announce
  them, and anyone can read them.
- Another agent can read an agent's skill by path, without copying it. That is
  the right move when two agents measure against the same rule, such as the one
  who writes and the one who reviews.

## 6. How they talk to each other

- An agent writes to another with `@name`. The answer comes back to where it was
  called from.
- **The other agent does not see the conversation.** A handoff message **must**
  carry everything the other one needs: what, where it lives, and what is
  expected.
- Nobody routes by `description`. An agent is named; it is not guessed.
- There is no orchestrator. Whoever hands out work is the person or the agent
  that delegates.

## 7. Memory

An agent learns in four places, and each thing goes to exactly one of them:

| What it learned | Where it goes |
|---|---|
| Something that changes how it does its job **in this repository** | A line under "What you have learned", inside its `agent.md`, by pull request |
| A heuristic of its role that holds in any project | Its agent memory folder (in Terminus, `projects/<id>/agents/<name>/memory/`) |
| A fact about this project: a decision, a convention, where something lives | The project memory |
| Something that changes the **method** | The skill, not the agent |

None of that is written as notes or a log inside the repository's documents.
The repository is the source, not a notebook.

## 8. Known limits

- **An agent's instructions enter once**, when the task starts. In a long task,
  a context compaction can make the agent lose them midway, and nothing warns
  about it. A short, concrete `agent.md` holds up better.
- **`tools` and `model` are not validated.** Each CLI decides what to do with a
  value it does not recognize.
- **Two tasks of the same agent do not see each other.** What they share is the
  memory, not the state.

## 9. How a harness reads this

This section describes what a harness that drives several CLIs is expected to
do with these files. It is written from Terminus, which reads this format today;
another harness may differ, and where it does, the agent file should not have
to change.

- **Discovery.** It reads `.agents/agents/` and each CLI's own `<dir>/agents/`,
  in both the folder form and the loose form, from the material the task can
  reach.
- **Precedence.** When the same name is declared twice, the neutral folder wins
  (§ 2). An agent a person creates privately, outside the repository, loses to
  the repository's one with the same name, because that one was reviewed. The
  winner is shown, not silently applied: an agent replaced without a word is
  diagnosed as a broken one.
- **Errors are shown, not swallowed.** A declaration that cannot be read
  (broken frontmatter, repeated `name`) appears in the list with its error. An
  agent that silently disappears gets debugged at the wrong place.
- **The harness does not write the declaration.** The file is edited in the
  repository and reviewed by pull request. A tool that writes its own
  configuration into someone's working tree leaves a diff nobody asked for.
- **Permissions come from the task, not the agent.** An agent launched by
  another agent runs with at most the launcher's permissions, and the launcher
  answers its permission requests; everything else is answered by the person.

# The sections of an AGENTS.md

Each section answers one question an agent would otherwise guess. Leave out a
section the project has nothing for; never fill one with generic advice.

| Section | The question it answers | What it must contain |
|---|---|---|
| What this is | What does this repository do, for whom? | Two or three sentences. Link to the README for more |
| Commands | How do I build, test and check this, and which command is the gate? | Each command as measured, with the platform it was measured on. The gate first |
| Layout | Where does each thing live, and what must I not edit? | The top-level folders, one line each. Generated and vendored folders marked |
| Rules | What must always or never happen here? | One rule per line, each with why or with what enforces it |
| Traps | What fails without looking like a failure? | Each trap with its symptom, so an agent recognizes it |
| Agents | Who does what? | The declared agents: name, scope, what each does, which skills it brings. Their flows live in each `agent.md` |
| Where things are documented | Which document answers which question? | A table of the governing documents |

## An area AGENTS.md

A folder gets its own `AGENTS.md` when it has rules or commands the rest of the
repository does not: a different language, a different test command, a
contract with another system. It states only what differs from the root, and
links to the root for the rest.

## Style

- Main point first. Short sentences. One term per concept.
- Facts, requirements, decisions, assumptions and recommendations are
  distinguishable in the sentence.
- What was not verified says so, and states the worst case.

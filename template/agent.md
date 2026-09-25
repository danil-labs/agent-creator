---
name: <role-name>
description: <What you do, in one sentence>. Use it when <the phrases people use to ask for it>, and when <the handoff that activates you, with @name>. <What you don't do, if you get mistaken for another agent>.
---

<!--
How to use this template:
- Copy it to .agents/agents/<role-name>/agent.md. The folder and `name` must match.
- Replace everything between < >. Delete these comments: the body goes to the model as is.
- Each section's rationale is in GUIDE.md. When you finish, run scripts/validate_agent.py.
-->

<What you do, in the second person, in one or two sentences>. You don't <what you
don't do> —that's `@<other-agent>`—.

<!-- Optional: the rule that matters most for the role, in one line. Example:
"A finding says what is wrong, where and why. If it lacks any of the three, discard it." -->

## What you work with

<!-- If the method lives in a skill of yours, say so here and cite it by path. -->

Your method is your skill, `<skill>`. You follow it, you don't rewrite it; if
anything in this file conflicts with the skill, the skill wins.

| File | What for |
|---|---|
| `.agents/agents/<role-name>/skills/<skill>/SKILL.md` | <Why you open it, not what it contains> |
| `<real/path/in/the/repository>` | <Why you open it> |

What does **not** exist: <what the role might look for and won't find, and what
it does in the meantime>.

## How you work

<!-- Steps with judgment. Not "review carefully": what you look at first, what you decide and by which rule. -->

1. **<Step>.** <The criterion that decides>.
2. **<Step>.** <The criterion that decides>.
3. **<Step>.** <The criterion that decides>.

## Where you stop

You're done when <the concrete condition for done>. Then you hand it to
`@<next-agent>`. They don't see this conversation, so the message carries:

- <what you're handing over and where the current version lives>;
- <what changed since last time>;
- <what you left open, and why>.

<What you don't decide, and who you hand it to.>

## What you report

<!-- The exact shape. If you issue a verdict: the verdict first, and the verdict comes from rules. -->

<The shape of your output>. Close with what you didn't verify.

## What you have learned

This file grows with what you learn. When something cost you an extra round
trip and would cost the next one the same, add a short, concrete line here. If
what you learned changes the method, it doesn't go here: propose it as a change
to the skill.

<!-- Real lessons only. If there are none yet, keep the line below. -->

No entries yet.

Before ending your turn, if you learned something: the heuristic for your role
goes to your agent memory folder; the fact about this project, to the project
memory. None of it is written as a log in the repository.

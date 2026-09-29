---
name: measure-repository
description: Measures a repository before documenting it for agents —layout, languages, the commands that build, test and lint it and whether they run, the rules the code and CI enforce, and the decisions already taken— and records each measurement so the document can cite it. Use it before writing or updating AGENTS.md, an architecture overview or decision records, and whenever a document must state a command, a path or a rule.
---

# measure-repository

A document for agents is only as good as its least-checked line: an agent
follows a wrong command as faithfully as a right one. This skill turns "I think
the tests run with X" into "`X` exited 0 on Linux at commit `abc123`".

## Inputs

- The repository, checked out at the commit you are documenting.
- The existing agent-facing documents, if any: `AGENTS.md` at the root and in
  areas, `CLAUDE.md`, `README.md`, architecture and decision folders.
- The platform you are on. Measurements are per platform.

## Steps

1. **Record where you stand.** Commit hash, branch, platform, and the versions
   of the toolchains you will run (`node --version`, `python --version`, …).
   Every measurement below is valid for that tuple only.
2. **Map the layout.** Top-level folders and what each holds, the languages by
   file count, the entry points. Note generated or vendored folders: agents
   must not edit them.
3. **Find the real commands.** Read, in this order: CI workflows, build files
   (`package.json` scripts, `Makefile`, `pyproject.toml`, `Cargo.toml`, …),
   then the README. CI is what the project actually runs; a README can be
   stale.
4. **Run each command you intend to document.** Record the exit status and how
   long it took. A command that fails is documented as failing, with the error,
   or not documented. A command you must not run —deploy, publish, anything
   destructive or that needs credentials you don't have— is recorded as not
   run, with the reason.
5. **Find what enforces each rule.** For every rule you intend to write ("no
   `console.log`", "every module has a test"), find the lint rule, CI check or
   test that enforces it. A rule nothing enforces is written as a convention.
6. **Rebuild the decisions.** Existing decision records first; then the history
   (`git log` of the files that embody a choice) for decisions nobody wrote
   down. Record each with what it chose, what it discarded and where it is
   enforced. A choice you cannot trace to a decision is an open question.
7. **Write the measurement log** in your answer, not in the repository:

   ```
   commit abc1234 · Linux x86_64 · node 22.4.0 · python 3.12.6
   pnpm install            exit 0   41 s
   pnpm test               exit 1   12 s   2 failing: src/api/users.test.ts
   pnpm deploy             not run  needs production credentials
   ```

8. **Write the document** from the log, with the outline in
   `references/agents-md-outline.md` and decision records with
   `assets/decision-record.md`. Anything not in the log is marked unverified.

## Output

- The measurement log, in the conversation.
- The documents, where every command, path and rule traces to a line of the
  log or is marked unverified.

## What not to do

- **Do not document a command you did not run** as if it worked.
- **Do not generalize a measurement across platforms.** A green run on macOS
  says nothing about Windows.
- **Do not copy rules from another document.** Link to it.
- **Do not write the measurement log into the repository.** It goes stale the
  next commit.

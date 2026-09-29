---
name: audit-docs
description: Audits documentation against the code it describes —dead paths, commands that don't run, rules nothing enforces— and classifies each finding so the verdict follows from rules. Use it to review AGENTS.md, READMEs, architecture notes, decision records or agent declarations before agents rely on them.
allowed-tools: Read Grep Glob Bash
---

# audit-docs

Documentation fails agents in three ways, and each needs a different check: it
names something that isn't there, it gives a command that doesn't work, or it
promises something the code doesn't do. This skill runs the three checks in
order of cost.

## Inputs

- The documents under review, at a known commit.
- A checkout of the repository at that commit.

## Steps

1. **Dead paths.** Run the script over the documents:

   ```bash
   python scripts/check_paths.py --root <repository> <file.md> [<file.md> …]
   ```

   It prints one line per cited path that does not exist —backticked paths and
   relative Markdown links— with file and line, and exits 1 if there is any.
   Paths with placeholders (`<name>`, `*`, `{}`) and URLs are skipped. Review
   each hit: a path the document itself says does not exist is not a finding.
2. **Commands.** Collect every command the documents give (code blocks and
   inline code that starts with a known program). Run each from the
   repository root. Record `command · platform · exit status`. Don't run what
   deploys, publishes, deletes or needs credentials; list it as not run.
3. **Promises.** For each rule or guarantee in the text, find what makes it
   true: a test, a lint rule, a CI step, a code path. Cite it by file and line.
   A promise with nothing behind it is a contradiction if the code does
   otherwise, and unverifiable if you can't tell.
4. **Agent declarations**, if the repository has `.agents/agents/`: run the
   agent-creator validator in strict mode and take its codes as findings.
5. **Classify** each finding as blocker, contradiction, unverifiable or minor,
   and derive the verdict from the classes, as the agent that uses this skill
   defines it.

## Output

The report, with the verdict first, the findings from blocker to minor, and
what was not run or checked.

## What not to do

- **Do not fix** what you find. The report is the deliverable.
- **Do not report a command as passing** unless you ran it and it exited 0.
- **Do not generalize across platforms.**

---
status: DECIDED            # PROPOSED | DECIDED | BLOCKED | SUPERSEDED
date: YYYY-MM-DD
decided-by: <role or team, never a personal name unless the project already records them>
supersedes: <number, or none>
---

# <NNNN>. <The decision, as a sentence: "Memory never falls back to local storage">

## Context

<The defect or need that forced a choice. Concrete: what failed, where, how it showed.>

## Decision

<What was chosen, in one paragraph.>

## Alternatives discarded

- **<Alternative>.** <Why not: what it would have broken or cost.>

## Consequences

- <What becomes easy.>
- <What becomes expensive, and who pays for it.>

## Where it is enforced

<The test, lint rule, CI check or code path that keeps this decision true. If nothing enforces it, say so.>

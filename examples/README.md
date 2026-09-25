# Examples

A small, complete team for a software project: four agents that hand work to
each other without stepping on each other. Each one shows a pattern.

| Agent | The pattern it shows |
|---|---|
| [`product-lead`](product-lead/agent.md) | **The entry point.** Turns a topic into a problem with an owner, decides what doesn't get built, and distributes the work |
| [`story-writer`](story-writer/agent.md) | **The producer.** Works with its own skill, hands off for review, and fixes what comes back |
| [`story-reviewer`](story-reviewer/agent.md) | **The reviewer.** Only reads, measures with the producer's skill without copying it, and derives the verdict from classes of finding |
| [`architect`](architect/agent.md) | **The sole owner of an artifact.** It is the only one that writes to the technical documentation; the others ask it to |

## How they hand off work

```
product-lead ──statement──► story-writer ──story──► story-reviewer
                                 ▲                        │
                                 └── changes requested ───┤
                                                          │ approved
                                                          ▼
                                                      architect
```

## What is illustrative and what isn't

The paths they cite (`docs/architecture/…`, each agent's skills) belong to a
hypothetical project: in your repository they are yours, and they have to
exist. What does hold as is is the shape: the boundary, the file tables, the
handoffs, the report, and the learned section.

To validate the examples without checking those paths:

```bash
python scripts/validate_agent.py --agents examples --no-paths
```

In the examples, «What you have learned» starts empty on purpose: in a real
agent, that section starts with real lessons from the project or doesn't start
at all.

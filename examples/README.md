# Examples

A small, complete team for a software project: four agents that hand work to
each other without stepping on each other. Each one shows a pattern in its
prompt (`agent.md`) and one in its manifest (`agent.json`).

| Agent | Scope | The pattern its prompt shows | The pattern its manifest shows |
|---|---|---|---|
| [`product-lead`](product-lead/agent.md) | `repository` | **The entry point.** Turns a topic into a problem with an owner, decides what doesn't get built, and distributes the work | The smallest useful manifest: scope, identity and project memory |
| [`story-writer`](story-writer/agent.md) | `shared` | **The producer.** Works with a method it shares with the reviewer, hands off for review, and fixes what comes back | A shared agent: a version, a repository skill in `skills`, memory across projects, and an `ask` ceiling |
| [`story-reviewer`](story-reviewer/agent.md) | `shared` | **The reviewer.** Only reads, measures with the producer's method without copying it, and derives the verdict from classes of finding | A read-only ceiling, and a widening request that stays requested until a person grants it |
| [`architect`](architect/agent.md) | `repository` | **The sole owner of an artifact.** It is the only one that writes to the technical documentation; the others ask it to | A tool-specific block under `extensions`, with its own version |

## How they hand off work

```
product-lead ──statement──► story-writer ──story──► story-reviewer
                                 ▲                        │
                                 └── changes requested ───┤
                                                          │ approved
                                                          ▼
                                                      architect
```

The writer and the reviewer are `shared`: their job holds in any project, so
other repositories can import them. They say what to do when the consumer has
no @product-lead or @architect ([GUIDE § 11](../GUIDE.md#11-designing-a-shared-agent)).

## What is illustrative and what isn't

The paths they cite (`docs/architecture/…`, `skills/user-stories/…`, each
agent's own skills) belong to a hypothetical project: in your repository they
are yours, and they have to exist. What does hold as is is the shape: the
boundary, the file tables, the handoffs, the report, the learned section and
the manifests. The `id` values are examples: generate your own.

To validate the examples without checking those paths:

```bash
python scripts/validate_agent.py --agents examples --no-paths
```

In the examples, «What you have learned» starts empty on purpose: in a real
agent, that section starts with real lessons from the project or doesn't start
at all. For agents that are real, see [`.agents/agents/`](../.agents/agents/).

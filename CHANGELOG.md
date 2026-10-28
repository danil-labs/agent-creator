# Changelog

All notable changes to the Agent Declaration Format and its tools. The format
follows the versioning rules in [`SPEC.md` § 9](SPEC.md#9-versioning-and-compatibility);
the validator follows [Semantic Versioning](https://semver.org).

## [Unreleased]

### Added

- `mcp`, a tool class in `permissions.tools` for the tools of MCP servers
  (`SPEC.md` § 7.10). With `tools` present and without `mcp`, no MCP tool is
  exposed, not even an approved `requires.mcp` server's; under `read-only`,
  only servers approved with `access: "read"`; under `ask`, every call needs
  approval. An older reader ignores the class with `W_UNKNOWN_TOOL`, which only
  removes tools. Conformance case `076-tool-class-mcp`.
- `SPEC.md` § 10.6: the memory of an agent that cannot edit. It still reads
  its memory, never writes it by editing files, and may use a memory tool its
  harness offers. H9 says so.

### Changed

- The `story-reviewer` example 1.1.0 lists `mcp` in `permissions.tools`, so
  the issue tracker it requests can be used once approved. Appendix A of
  `SPEC.md` does the same.

- The `create-agent` skill closes only when the validator passes with
  `--strict`, for every agent it creates, reviews or fixes, shared or not.
  Before, strict mode was required only for shared agents, and a warning could
  be justified instead of fixed.
- `agent-designer` 1.1.0 follows the same rule, and `GUIDE.md` § 13 and its
  checklist ask for `--strict` before calling any agent done. The format and
  `SPEC.md` § 9.3 do not change.
- The `create-agent` skill names `SPEC.md`, `GUIDE.md`, `template/` and
  `scripts/validate_agent.py` relative to its own folder, where they are
  delivered next to `SKILL.md`, with `../..` as the fallback inside this
  repository. An agent no longer has to find the agent-creator repository.

## [1.0.0] — Unreleased

The first versioned release of the format: `specVersion: 1`.

### Added

- `agent.json`, an optional manifest next to `agent.md`, with `specVersion`,
  `scope`, `id`, `version`, `memory`, `skills`, `permissions`, `requires` and
  `extensions` (`SPEC.md` § 7).
- The three classes of fields —descriptive, narrowing, widening— and how a
  harness treats each (`SPEC.md` § 8).
- Identity and memory: the agent key, the agent digest, `memory.reach` and
  external stores by slot (`SPEC.md` § 10).
- Scope and import rules for agents used from another repository
  (`SPEC.md` § 11).
- Harness conformance requirements H1–H15 (`SPEC.md` § 12) and stable
  diagnostic codes with profiles (`SPEC.md` § 13).
- Non-goals for version 1 (`SPEC.md` § 14).
- `schema/agent.v1.json`, the JSON Schema (2020-12) of the manifest.
- `conformance/`, a corpus of 48 cases, and `scripts/run_conformance.py`, which
  runs it against the reference validator or any other reader.
- Validator: manifest validation, `--strict`, `--json`, stable codes and the
  agent digest.
- `template/agent.json`, and a manifest for each example.
- This repository's own shared agents: `docs-writer`, `agent-designer` and
  `docs-auditor`, with their skills.
- `GUIDE.md` sections on the manifest, limits and requests, shared agents and
  memory.
- `CONTRIBUTING.md`, `AGENTS.md`, CI and a field proposal form.

### Changed

- An unknown frontmatter field is now a warning, not an error, so that the
  validator and harnesses reach the same verdict on the same file.
- Mentions inside code spans and fenced code blocks are no longer read as
  handoffs. `` `@theme` `` between backticks used to fail an agent as an
  undeclared mention.
- The examples write handoffs as bare mentions, and the writer and the reviewer
  share one repository-level skill instead of the reviewer reading the
  writer's.
- Skill templates live in `assets/`, as in Agent Skills.

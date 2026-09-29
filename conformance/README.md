# Conformance corpus

The cases every reader of the Agent Declaration Format is measured against.
The corpus, not any one implementation, is the reference: when the validator in
this repository and another reader disagree, the case decides, and a case that
turns out to be wrong is fixed here, by pull request.

## Running it

```bash
python scripts/run_conformance.py                              # the reference validator, all cases
python scripts/run_conformance.py --profile format --command "<reader>"   # another reader
python scripts/run_conformance.py --case 011                   # one case
```

A reader under test is a command that accepts `--root <dir>`, the case's extra
arguments and `--json`, and prints the report described below. Harnesses
**MUST** pass the `format` profile ([SPEC § 12](../SPEC.md#12-harness-conformance));
the `authoring` profile covers checks only validators make.

## Layout of a case

```
cases/<NNN>-<slug>/
  expected.json          the verdict and the codes
  input/                 a repository root
    .agents/agents/<name>/agent.md
    .agents/agents/<name>/agent.json
    …                    any other file the case needs
```

`expected.json`:

```json
{
  "description": "What the case proves, and why the rule exists.",
  "profile": "format",
  "args": ["--strict"],
  "agents": {
    "a": { "verdict": "fail", "codes": ["W_UNKNOWN_FIELD"] }
  }
}
```

- `profile`: `format` or `authoring` ([SPEC § 13](../SPEC.md#13-diagnostic-codes)).
- `args`: OPTIONAL extra arguments for the reader.
- `agents`: every agent folder in the input, with its `verdict` (`pass` or
  `fail`) and the exact multiset of diagnostic codes, in any order.

A reader passes a case when, for every agent, its verdict and its codes match
exactly, no agent is missing or extra, and its exit status is 1 if any agent
fails and 0 otherwise. Messages, lines and columns are not compared.

## The report a reader prints

```json
{
  "validator": "1.0.0",
  "specVersion": 1,
  "strict": false,
  "agents": [
    {
      "name": "a",
      "path": ".agents/agents/a",
      "verdict": "pass",
      "manifest": true,
      "scope": "shared",
      "digest": "sha256:…",
      "diagnostics": [
        { "code": "I_REQUESTED_NOT_GRANTED", "level": "info", "message": "…", "file": "agent.json", "path": "requires.mcp[0]" }
      ]
    }
  ],
  "summary": { "agents": 1, "passed": 1, "failed": 0, "errors": 0, "warnings": 0, "info": 1 }
}
```

Only `agents[].name`, `agents[].verdict` and `agents[].diagnostics[].code` are
compared. The other fields are what the reference validator prints; other
readers **SHOULD** print them too.

## The cases

| Range | What it covers |
|---|---|
| `00x` | Loading: an agent with only `agent.md`, the smallest and the fullest manifest |
| `01x` | Files: broken JSON, BOM and CRLF, duplicate keys, non-objects, a manifest without a prompt, encodings |
| `02x` | Versioning: future and malformed `specVersion`, unknown fields, strict mode, `$schema` on a branch |
| `03x` | Extensions: opaque blocks, missing versions, tool blocks at the root |
| `04x` | The prompt: `name` repeated in the manifest, frontmatter fields, name and folder |
| `05x` | Scope |
| `06x` | Mentions and paths: code is never a mention (`@theme` between backticks), undeclared mentions, e-mail addresses, dead paths, sections |
| `07x` | Narrowing and widening: requests reported as requested, not granted; requests without a reason or with a command; ceilings and tool classes |
| `08x` | Memory: stores that are paths or URLs, invalid reach and store |
| `09x` | Identity: duplicate and invalid `id`, invalid `version` |
| `10x` | Skills: paths that leave the repository, missing skills, own skills |

Files in `cases/011-bom-crlf/` and `cases/015-not-utf8/` are stored byte for
byte (`-text` in `.gitattributes`): a checkout that converted them would test
nothing.

## Adding a case

Every change to the format comes with at least one case that fails without the
change ([CONTRIBUTING](../CONTRIBUTING.md#proposing-a-field-or-a-rule)). Number
it in the range of the section it covers, describe in `description` what it
proves and why, and run the corpus.

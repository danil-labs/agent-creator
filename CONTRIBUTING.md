# Contributing

Thank you for helping. This repository defines a format that other tools
implement, so a change here is a change to every reader. The process is built
around one question: **what does a reader do differently because of this
change, and how do we prove it?**

## Kinds of contribution

| Contribution | How |
|---|---|
| A typo, a broken link, a clearer sentence | Open a pull request directly |
| A bug in the validator or the runner | Open an issue with the input and the output, or a pull request with a conformance case that shows it |
| A disagreement between a reader and the corpus | Open an issue. If the case is wrong, the fix is to the case |
| A new field, a new value, or a new rule | Follow [Proposing a field or a rule](#proposing-a-field-or-a-rule) |
| A new extension namespace | A pull request adding a row to `SPEC.md` Appendix B: the namespace, the tool and where its block is documented |
| A new example or agent | A pull request; it must pass the validator, in strict mode if it is under `.agents/agents/` |

## Proposing a field or a rule

Open an issue with the [field proposal form](.github/ISSUE_TEMPLATE/field-proposal.yml).
A proposal needs three things. Without all three it stays open until it has
them.

1. **The problem.** A defect that shows today, in a real repository or a real
   harness: what goes wrong, for whom, and how it shows. "It would be nice to
   have" is not a problem. A field that nobody's behavior depends on is not
   added —that is why `kind` is not in version 1 (`SPEC.md` § 14).
2. **The behavior that changes.** What a reader does differently when the field
   is present, and what it does when it is absent. Say which class the field
   belongs to (`SPEC.md` § 8):
   - *descriptive* — shown and used to identify, grants nothing;
   - *narrowing* — intersected with the launcher's permissions;
   - *widening* — a request a person approves, never granted from the
     repository.

   If you can't say what an older reader does when it meets the field, the
   proposal is not ready: within `specVersion: 1`, an older reader must stay
   safe by ignoring it with a warning (`SPEC.md` § 9).
3. **The proof in the corpus.** At least one conformance case that fails
   without the change and passes with it, with its `expected.json`. For a
   widening field, also a case that shows it reported as requested, not
   granted.

## The pull request

A change to the format touches, in one pull request:

- `SPEC.md` — the rule, with its *Why*, and the codes it adds to § 13;
- `schema/agent.v1.json` — the shape;
- `scripts/validate_agent.py` — the check, with a stable code;
- `conformance/cases/` — the cases;
- `GUIDE.md` — how to use it, if authors need to know;
- `CHANGELOG.md` — under *Unreleased*.

Before opening it, run:

```bash
python scripts/validate_agent.py --agents examples --no-paths
python scripts/validate_agent.py --root . --strict
python scripts/run_conformance.py
```

All three must pass. CI runs them on Linux and Windows.

## Code

- Python 3.9 or later, standard library only.
- A new diagnostic gets a new code: `E_` for errors, `W_` for warnings, `I_` for
  information. Codes are never renamed or reused.
- Messages say what is wrong and what to do. They are free text; readers compare
  codes, never messages.

## Writing

- English, plain and concrete: main point first, short sentences, one term per
  concept.
- Normative text uses the BCP 14 keywords in bold capitals, and each rule says
  why it exists.
- No real client data: describe structures, not contents.

## Releases

Maintainers tag releases. Within version 1 the tag `v1` moves to the latest
additive release, and each release also gets its own tag (`v1.1.0`). Schema URLs
point to `v1`.

## License

By contributing, you agree that your contribution is licensed under the
[Apache License 2.0](LICENSE).

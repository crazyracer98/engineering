# FR-0001. Cover every rule and domain row with learning content

## Status

Accepted. Implemented in v1.1.0 (2026-10-27); see "Outcome" below.

## Description

The learning content under `data/learn/` shall cover the taxonomy, and the
repository shall report any gap per scope:

1. Every rule (P1 to P83) has a rule example in `rules/<cat>.yaml`.
2. Every row of `data/domains.yaml` has a domain example in
   `domains/<branch>.yaml`.
3. Every rule of category X appears in the `rules` of at least 2 questions in
   `quiz/x.yaml`.
4. Every conflict rule (K1 to K8) appears in the `rules` of at least 1
   question in `quiz/conflicts.yaml`.
5. Cases are not required. A rule with no verified source has no case, and
   that is not a gap.

The default `taxonomy check` validates the content that exists and does not
require coverage, so it passes while the files are empty stubs. Coverage is a
separate report, run per scope:

```sh
uv run python -m taxonomy.validate --learn-coverage              # all scopes
uv run python -m taxonomy.validate --learn-coverage --scope a    # category a..i
uv run python -m taxonomy.validate --learn-coverage --scope k    # conflict quiz
uv run python -m taxonomy.validate --learn-coverage --scope civil  # one domains/ branch slug
```

It prints one line per gap, then `learn coverage (scope S): N gap(s)`, and
exits 0 when there are none, 1 when there are gaps and 2 for an unknown
scope. A category scope covers that category's rule examples and its quiz.
Branch slugs are listed in [`data/README.md`](../../data/README.md).

## Source

The learning-hub plan (hybrid rigor: examples for every rule and domain row,
cases only where a verified source exists) and
[ADR 0008](../adrs/0008-learning-hub-in-the-dataset-repo.md).

## Acceptance criteria

- With the stubs, `taxonomy check` exits 0 and the coverage report lists a gap
  for each of the 83 rules, 130 domain rows and 8 conflict rules.
- A scope with complete content reports `0 gap(s)` and exits 0.
- A rule with one question in its category quiz is reported as a gap.
- An unknown scope exits 2 and names the valid scopes.
- Tested in `tests/test_learn_checks.py` (`test_coverage_*`).

## Outcome

At v1.1.0 the report shows `learn coverage (all scopes): 0 gap(s)`:

- 83 rule examples, 67 of them with a management variant.
- 130 domain examples across the 20 branches.
- 193 questions.
- 27 cases covering 44 rules, with 198 quotes (cases stay optional; 39 rules
  have none).

How case quotes are verified: each quote is copied from the raw source text
(fetched directly, not through a summarising tool) and must score 1.0
against it. `taxonomy verify-sources` checks them under the key
`<case id>#<n>`, and `--cases-only` runs just those. At release all 198
matched. Nine of them (GAO Patriot, Senate Target) match only from cache,
because the origin returns 403 and the archive rate-limits.

When two case items documented the same incident, they were merged into one
case: one id, the union of rules and lessons and the quotes, the first
source slug kept. That gives one "Real case" block per incident and one
registry entry per URL, and keeps "at most one case per rule" true.

Open follow-ups: #29, #30, #32 and #34.

# data/

The taxonomy itself, and its single source of truth (ADR 0003). Every
published output (`publication/`, the site, the paper) is rendered from
these files; nothing downstream is edited by hand. Each file has a JSON
Schema in [`../schema/`](../schema/).

| File | Holds |
|---|---|
| `meta.yaml` | title, edition (= release tag), master rule, reading guide, known exceptions, section prose and table layout |
| `categories.yaml` | categories A–I and the rule order in each |
| `rules.yaml` | the 83 rules (P1 to P83; the class U, R or C is a field) with checks, relations, evidence, sources and management form |
| `conflicts.yaml` | the conflict rules and the rules each one mentions |
| `sources.yaml` | the source registry: one entry per URL, primary or secondary |
| `quotes.yaml` | verbatim direct quotes and the rules they support |
| `domains.yaml` | the domain index and the domains checked without a row |
| `glossary.yaml` | one meaning per term |
| `rigor_matrix.yaml` | which rules apply in which consequence × uncertainty cell |
| `method.yaml` | method and limits, as prose blocks |
| `history.yaml` | released editions and the old-to-new ID map |

## `learn/`

The learning hub's content ([ADR 0008](../docs/adrs/0008-learning-hub-in-the-dataset-repo.md)),
validated by `taxonomy check` against the rules, domains and sources above.
Schemas: `../schema/learn-*.schema.json`. Rendered on the site only.

| Path | Holds |
|---|---|
| `learn/rules/<cat>.yaml` | `a` to `i`: one illustrative example per rule of the category (`management` exactly when the rule has a management form) |
| `learn/domains/<branch>.yaml` | one example per `domains.yaml` row of the branch (table below) |
| `learn/quiz/<cat>.yaml` | `a` to `i`: select-all-that-apply questions (IDs `q-a-01`); `quiz/conflicts.yaml` holds the conflict-rule questions (IDs `q-k-01`, `rules` name K IDs) |
| `learn/cases/<n>.yaml` | `1` to `3`: real, sourced cases, at most one per rule |
| `learn/sources/<n>.yaml` | `1` to `3`: the cases' sources, merged into the registry; slugs start with `case-` and each needs `author` |

Branch file names are the branch heading in lower case with each run of other
characters turned into `-` (`taxonomy.load.branch_slug`): `civil`,
`mechanical`, `materials`, `electrical`, `chemical`, `nuclear`, `mining`,
`biomedical`, `agricultural`, `industrial`, `computing`, `cross-cutting`, and
for the management branches `management-governance-and-assurance`,
`management-strategy-and-decisions`, `management-portfolio-programme-and-project`,
`management-product-and-innovation`, `management-operations-quality-and-supply`,
`management-risk-resilience-and-legal`, `management-people-and-organization`
and `management-finance`.

Examples are illustrative, not evidence; only a case with a registered source
is evidence. Check gaps per scope with
`uv run python -m taxonomy.validate --learn-coverage [--scope a..i|k|<branch>]`
([FR-0001](../docs/frs/FR-0001-learning-coverage.md)); `taxonomy check` does
not require coverage.

## Do

- Edit the taxonomy here, then run `uv run taxonomy check` and
  `uv run taxonomy build`.
- Cite sources in prose only as Pandoc citations, `[@slug]`.
- Add a new source to `sources.yaml` under a new slug matching
  `^[a-z0-9]+(-[a-z0-9]+)*$`.
- Give every source an `author` list of CSL-JSON names: `{family, given}` for a person, `{literal}` for an organization or
  collective (the issuing body of a standard or regulation, `Wikipedia contributors`); never a guessed person.
- Bump `meta.edition` and add a `history.yaml` entry per
  [`docs/methodology.md`](../docs/methodology.md) "Versioning".

## Don't

- Rename a slug or a rule ID; both are frozen once published.
- Regenerate this directory with `sources/import/import_v9.py --write`; that
  discards every edit made since the import.

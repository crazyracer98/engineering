# data/

The taxonomy itself, and its single source of truth (ADR 0003). Every
published output (`publication/`, the site, the paper) is rendered from
these files; nothing downstream is edited by hand. Each file has a JSON
Schema in [`../schema/`](../schema/).

| File | Holds |
|---|---|
| `meta.yaml` | title, edition (= release tag), master rule, reading guide, known exceptions, section prose and table layout |
| `categories.yaml` | categories A–I and the rule order in each |
| `rules.yaml` | the U, R and C rules with checks, relations, evidence, sources and management form |
| `conflicts.yaml` | the K-rules and the rules each one mentions |
| `sources.yaml` | the source registry: one entry per URL, primary or secondary |
| `quotes.yaml` | verbatim direct quotes and the rules they support |
| `domains.yaml` | the domain index and the domains checked without a row |
| `glossary.yaml` | one meaning per term |
| `rigor_matrix.yaml` | which rules apply in which consequence × uncertainty cell |
| `method.yaml` | method and limits, as prose blocks |
| `history.yaml` | released editions and the old-to-new ID map |

## Do

- Edit the taxonomy here, then run `uv run taxonomy check` and
  `uv run taxonomy build`.
- Cite sources in prose only as Pandoc citations, `[@slug]`.
- Add a new source to `sources.yaml` under a new slug matching
  `^[a-z0-9]+(-[a-z0-9]+)*$`.
- Bump `meta.edition` and add a `history.yaml` entry per
  [`docs/methodology.md`](../docs/methodology.md) "Versioning".

## Don't

- Rename a slug or a rule ID; both are frozen once published.
- Regenerate this directory with `sources/import/import_v9.py --write`; that
  discards every edit made since the import.

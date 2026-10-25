# 0003. Keep the taxonomy in a structured dataset as the single source of truth

## Status

Accepted

## Context

The taxonomy exists as two hand-written files: the edition-9 Markdown
(83 rules, management forms, a source registry, direct quotes, method and
limits) and an older edition-6 YAML twin (67 rules). The two had drifted
apart, and edition 9 had no machine-readable twin at all. The repository
must publish the same content three ways (split Markdown, a Material for
MkDocs site and a Pandoc/Typst PDF paper; ADR 0002) and check it
automatically: IDs unique, relations resolve, every rule has a primary
source, every citation resolves, and so on. Text kept in more than one
place drifts, and checks on prose tables need fragile parsing.

The alternatives considered:

- **Markdown as the source.** It is the most readable form and is what
  edition 9 already is. But every check and every other output would have
  to parse wide Markdown tables, links would repeat each source's title
  and URL in up to six places, and the paper needs per-rule cards rather
  than tables.
- **The edition-6 YAML as it is.** It already had a rule schema, but it
  lacks everything added in editions 7 to 9 (16 rules, four conflict
  rules, management forms, the primary/secondary registry, quotes, method
  and limits), stores sources as bare URLs, and its wording differs from
  edition 9 in places.

## Decision

We will keep the taxonomy in `data/*.yaml`, one file per concern, each
with a JSON Schema in `schema/`. It is seeded from the edition-6 field set
and filled from the edition-9 Markdown, whose wording wins wherever the two
disagree. Sources live once in `data/sources.yaml` under a slug, and all
prose cites them as Pandoc citations (`[@slug]`). Every generated output
(`publication/`, the site, the paper) is rendered from `data/`, and nothing
is edited downstream of it.

The one-shot importer `sources/import/import_v9.py` produced the first
`data/` and is kept only for reproducibility. After the import, changes are
made in `data/` by hand or by the `taxonomy-research` workflow, and the
importer is not run again.

## Consequences

- One edit updates every output, and integrity checks run on structured
  data, not on parsed prose.
- Reproducing the edition-9 Markdown byte for byte needs presentation data
  beside the content: section intros, table headers, per-use link titles
  (`source_titles`), verbatim cell overrides (`*_text`) where a cell does
  not follow its structured pattern, and a few layout quirks. These live in
  `data/meta.yaml` and the override fields, so the data is less minimal
  than a pure content model.
- Contributors edit YAML instead of a readable document and must run the
  build to see the result. Round-trip YAML (ADR 0002) keeps their key order
  and comments.
- The two files in `sources/import/` become frozen provenance. Rerunning the
  importer would overwrite later edits in `data/`.

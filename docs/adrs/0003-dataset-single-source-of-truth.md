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
`data/`. Once wave 1 merges, it is frozen and kept only as a provenance
record of how `data/` was first produced. Changes are then made in `data/`
by hand or by the `taxonomy-research` workflow, never by rerunning the
importer. By default the importer only compares its output with `data/`
(`--check`, exit 1 on any difference). After the first hand edit that
difference is expected, and it doesn't mean `data/` is wrong. Only an
explicit `--write` overwrites `data/`.

Source slugs are frozen after the import. The importer asserts that every
slug matches `^[a-z0-9]+(-[a-z0-9]+)*$` and is unique. Prose, the paper and
other registries cite those slugs, so renaming one is a breaking change.

The integrity checks include "every rule has at least one primary source".
Its only exceptions are the rules listed with a reason in
`meta.known_exceptions`, which in 1.0.0 is just C15 (Brooks's law, whose
primary source is a book that isn't online).

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
- The two files in `sources/import/` and the importer become frozen
  provenance. `import_v9.py --check` will drift from `data/` as the dataset
  evolves. `--write` would discard every edit made since the import, so it
  is for reproducing the original import only.

## G1 delta (2026-10-25)

At gate G1 the user accepted the import and decided that edition 9's own
inconsistencies are fixed in `data/` before 1.0.0. From then on edition 9
is no longer the oracle. The round-trip test against
`sources/import/engineering-best-practices.md` is retired, and
`import_v9.py --check` is expected to diverge. `taxonomy build --check`
stays: `publication/` must still equal what `data/` renders.

The accepted delta from edition 9 to 1.0.0 is 45 diff hunks in the
single-file Markdown. Besides the version line ("Version 9" becomes
"Version 1.0.0"), it contains:

- **(a) Primary sources first.** Edition 9's section 1 says "each rule lists
  its primary sources first", but 16 rules didn't. The `sources` of U6, U8,
  U18, U20, U21, U25, U27, U28, U29, U31, U32, U35, U38, U46, R1 and C11,
  and the management `sources` of R4, are reordered so that primary
  sources come first. Each kind keeps its relative order.
- **(b) Scope.** "Section 10 states every rule in management form" becomes
  "67 of the 83 rules". The other 16 (U47–U58, R9, C14–C16) come from
  management sources.
- **(c) Section-11 pointer.** "ISO catalogue pages listed in section 7"
  becomes "listed in sections 4 and 10; for C10, the ASME page in
  section 9".
- **(d) Inverses.** 122 inverses were missing: 121 `strengthened_by` and
  1 `checked_by`. R2 gains `strengthens` R1 to match R1's
  `strengthened_by` R2. No new relation types were added: `depends_on` and
  `scaled_by` stay one-way. Every `related` map is normalized: keys follow
  `relation_types` order, and IDs run U before R before C, then by number.
- **(e) Symmetric conflicts.** The other side of 8 one-sided
  `conflicts_with` relations is added: U35–U23, U32/U33/C10–U49,
  U8/U9–U50, U51–U55 and R1–C15. The qualifier "when people are added for
  redundancy (add early, not late)" is on both C15 and R1.
- **(f) Paid-only "strong" ratings.** The ratings of rules U40, C10 and C13,
  and of the management forms of U16, U39, R3, C1 and C12, stay "strong",
  because the scale rates institutional requirement. Each of these 8
  evidence notes gains "standard text is paid; only the official summary
  was read", and section 12's Limits gains a line naming them.
- **Source URLs.** The hosts of `staw-knee-deep-big-muddy` and
  `sackett-zhang-berry-lievens-revisiting` are lowercased to
  `www.gwern.net`. The paths are unchanged.

`related_text` overrides are kept only where a cell carries text that isn't
a rule ID: U47, U49, U50, U55, C15 and R1. NFR-0001's `override-agreement`
check keeps them in step with `related`. The checks `inverse-complete`,
`conflicts-symmetric`, `related-order` and `sources-primary-first` keep
the delta from regressing.

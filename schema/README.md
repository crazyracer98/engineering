# schema/

One JSON Schema (draft 2020-12) per data file:
`<name>.schema.json` validates `../data/<name>.yaml`.
`sources.schema.json` also validates the other source registries
(`paper/references-extra.yaml`, `docs/methodology-references.yaml`).
Each field's `description` says what it holds.

The learning hub has four more schemas, `learn-<kind>.schema.json`, each
validating every file in `../data/learn/<dir>/`: `learn-rules` (`rules/`),
`learn-domains` (`domains/`), `learn-quiz` (`quiz/`) and `learn-cases`
(`cases/`). `../data/learn/sources/*.yaml` use `sources.schema.json`. The
schemas fix the shape; `taxonomy check` adds the references to the live rules,
domains and registry (see
[NFR-0001](../docs/nfrs/NFR-0001-dataset-integrity.md)).

Optional override fields keep the published Markdown reproducible byte for
byte from the structured data (round-trip fidelity):

- per-use link titles: `source_titles`, `reference_titles`;
- verbatim cells: the `*_text` fields (for example `related_text`,
  `evidence_text`, `sources_text`, `rules_text`) and `rule_label`, used
  when a cell does not follow its field's pattern;
- layout: `meta.sections`, `meta.tables`, `meta.layout_quirks`.

A renderer prints an override in place of the generated text when the
override is present.

## Do

- Change a schema in the same commit as the data it describes, and version
  the change by the data-format rows of
  [`docs/methodology.md`](../docs/methodology.md) "Versioning". Removing or
  renaming a field or vocabulary value is a major change; adding one is a
  minor change.

## Don't

- Loosen a schema to make invalid data pass; fix the data instead.

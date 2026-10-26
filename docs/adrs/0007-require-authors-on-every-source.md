# 0007. Require an author on every source

## Status

Accepted

## Context

The paper cites in IEEE numeric style ([ADR 0002](0002-publication-toolchain.md)),
and the release ships the registries as CSL-JSON. Authorless entries render
badly in the bibliography and hamper readers who look a source up by author.
The source schema first required only slug, title, URL, kind and paid, so
authors were missing from all 233 dataset sources and from the paper and
methodology registries.

## Decision

We will require an `author` field on every source in all three registries
(`data/sources.yaml`, `paper/references-extra.yaml`,
`docs/methodology-references.yaml`), as a list of CSL name objects: a person
is `{family, given}`, an organization is `{literal}`. The schema description
states the rules for filling it:

- Standards, regulations and guidance name the issuing body.
- A copy hosted elsewhere names the original authors, not the host.
- Wikipedia is `{literal: Wikipedia contributors}`.
- Never a guessed person: where none can be determined, name the publisher.

## Alternatives considered

- **Optional field.** Cheap, but gaps would persist unnoticed and the
  bibliography would stay uneven.
- **Fill only the paper's sources.** The same sources appear in the
  dataset and the CSL-JSON, so two standards of attribution would coexist.

## Consequences

- Adding a source now takes a bibliographic lookup. A schema failure makes
  the omission visible.
- The authors were set from bibliographic knowledge, not checked against
  each page, so some may be wrong; follow-up issue #24 tracks verifying them.

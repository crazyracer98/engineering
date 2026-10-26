# 0008. Keep the learning hub in the dataset repository

## Status

Accepted

## Context

The site is reference material: a reader can look a rule up but cannot learn
it or test what they know. The learning hub adds worked examples for every
rule and every domain row, real cases, and quizzes. Where the content lives
and how it is checked had to be decided:

- **Separate repository.** Content could live apart from the taxonomy. But
  it names rules, domains and sources, so it would drift from them unless a
  cross-repository check pinned it. Diátaxis treats tutorials and reference
  as parts of one documentation set (https://diataxis.fr/).
- **Quiz tooling.** The `mkdocs-quiz` plugin (https://github.com/ewels/mkdocs-quiz)
  would be a third-party MkDocs plugin. Zensical runs none
  (https://zensical.org/compatibility/plugins/), and issue #9 requires the
  migration to Zensical before 2027-05-05.
- **Rigor.** Every claim in the paper rests on a source. Illustrative
  examples have no source, and real incidents need one, so the hub has to say
  which is which.
- **Release.** [ADR 0004](0004-edition-equals-release-version.md) makes the
  edition equal the release version.

## Decision

We will keep the learning content in this repository, under `data/learn/`,
as data with its own JSON Schemas (`schema/learn-*.schema.json`), under
[ADR 0003](0003-dataset-single-source-of-truth.md): `taxonomy check`
validates it against the live rules, domains and source registry, and the
site is rendered from it.

- **Layout.** `rules/<cat>.yaml` (rule examples), `domains/<branch>.yaml`
  (one file per `domains.yaml` branch), `quiz/<cat>.yaml` and
  `quiz/conflicts.yaml` (questions), `cases/<n>.yaml` and `sources/<n>.yaml`
  (cases and their sources, which `load_registry` merges into the registry).
- **Hybrid rigor.** Illustrative examples cover every rule and every domain
  row and are labeled illustrative, not evidence. Real cases exist only where
  a verified source exists. Case sources need `author`
  ([ADR 0007](0007-require-authors-on-every-source.md)) and case quotes are
  verified like rule quotes
  ([ADR 0006](0006-verify-quotes-against-sources.md)).
- **Own quiz engine.** Questions are multi-select with exact-match scoring and
  per-option feedback. The site renders them to plain HTML, and a small
  vanilla-JS file adds checking, scoring and progress in `localStorage`. There
  is no new dependency, no server and no account.
- **Same edition.** The content ships in the same repository and release as
  the taxonomy. It is a backward-compatible addition, so it is the minor
  edition 1.1.0 under ADR 0004; later example or quiz fixes are patches.
- **Site only.** The PDF, the single-file Markdown and the YAML release asset
  do not change.
- **Coverage is opt-in.** The default checks validate what exists; the
  completeness requirements are the report of
  [FR-0001](../frs/FR-0001-learning-coverage.md).

## Alternatives considered

- **A separate learning repository.** Rejected: it drifts from the rules, and
  two releases would have to be kept in step.
- **The `mkdocs-quiz` plugin.** Rejected: it would not survive the move to
  Zensical.
- **Real cases for every rule.** Rejected: many rules have no verified
  source, and an invented case is worse than none.

## Consequences

- The dataset repository gains a content area that is larger than the
  taxonomy's prose, with its own schemas and checks. A rule rename or removal
  now fails `taxonomy check` until the examples and questions are updated.
- The answer key is in the page source. That is accepted for self-assessment.
- The quiz engine is code this repository maintains, and it needs its own
  accessibility requirement and tests.
- Cases add sources, so the source registry grows and `taxonomy verify-sources`
  has to cover case quotes.

# 0001. License prose and data under CC BY-SA 4.0, code under GPL-3.0

## Status

Accepted

## Context

The repository holds two kinds of work: a taxonomy (structured data, generated
Markdown, a paper, documentation) and the code that validates and publishes it.
The template ships GPL-3.0, which is written for software and is a poor fit for
prose and data. Creative Commons recommends against using its licenses for
software, and GPL is not designed for text. The taxonomy should stay open and
reusable, with improvements shared back.

## Decision

We will license prose and data under CC BY-SA 4.0 and code under GPL-3.0.
CC BY-SA 4.0 covers `data/`, `publication/`, `paper/` (except `paper/csl/`,
which carries CC BY-SA 3.0 in its own notice), `docs/`, `sources/` (except
`sources/import/import_v9.py`, a script) and the site content. GPL-3.0 covers
`src/`, `tests/`, `schema/`, scripts, workflows, configuration and everything
else. `LICENSE` stays GPL-3.0; `LICENSE-CC-BY-SA-4.0` holds the verbatim legal
code. The root `README.md` maps paths to licenses.

## Consequences

Each content type has a license written for it, and both are share-alike, so
derived taxonomies and derived code stay open. Contributors must know which
license applies to a path; the README table is the single reference. Mixing
the two in one file is avoided. `paper/csl/` under CC BY-SA 3.0 is an upstream
constraint and is noted separately. Reusers combining the dataset with
GPL code must check compatibility themselves.

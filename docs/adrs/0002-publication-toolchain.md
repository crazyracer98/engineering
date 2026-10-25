# 0002. Build publications with Pandoc, Typst and Material for MkDocs

## Status

Accepted

## Context

One dataset must generate split Markdown docs, a documentation site and a PDF
paper, reproducibly in CI and the devcontainer, without a separate installer
for binaries. The tools must be installable from the Python lockfile.

## Decision

We will use:

- Pandoc via `pypandoc-binary` 1.17, which bundles Pandoc 3.9, so no binary
  installer script is needed.
- Typst via the `typst` PyPI package 0.15, producing PDF/A-2b through
  `pdf_standards`.
- Material for MkDocs 9.8 for the site, despite it being in maintenance mode
  (end of life 2027-05-05). Zensical, its successor, is still alpha. We will
  open a migration issue at release. Builds set `NO_MKDOCS_2_WARNING=1`.
- `ruamel.yaml` in round-trip mode, never `typ="safe"`, which sorts keys and
  would reorder the dataset.
- IEEE numeric citations with an explicit `--csl` file.

Sources:

- https://pypi.org/pypi/pypandoc-binary/json
- https://pypi.org/pypi/typst/json
- https://pandoc.org/MANUAL.html
- https://squidfunk.github.io/mkdocs-material/changelog/
- https://yaml.dev/doc/ruamel.yaml/
- https://zensical.org/compatibility/

## Consequences

Everything installs from `uv.lock`; CI needs no system packages. The site
generator has a known end of life and a migration is owed before 2027-05-05.
Pandoc and Typst versions move only with their wheels. Round-trip YAML is
slower and its API is less obvious than safe mode, but it preserves key order
and comments.

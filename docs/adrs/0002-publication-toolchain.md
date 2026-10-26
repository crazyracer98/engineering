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

## Amendment (2026-10-26): release wiring, site citations, Zensical

Decisions made while building the release path, added without changing the
Decision above.

- **Zensical.** The migration issue is
  [#9](https://github.com/crazyracer98/engineering/issues/9), due before
  2027-05-05.
- **`uv` on the release runner.** `release.yml` is owned by the template
  and calls a Makefile contract (`docs/TEMPLATE.md`), so each target is the
  instance's job. Its `build` job runs on a bare runner with no `uv`, so the
  `Makefile` uses `uv` from `PATH` when present and otherwise installs the
  version pinned in `.devcontainer/Dockerfile` (`UV_VERSION`), with Astral's
  versioned standalone installer, into `build/.tools/uv`. Editing
  `release.yml` was rejected: the next template sync would overwrite it.
  Source: https://docs.astral.sh/uv/getting-started/installation/
- **Pages deploys after a release.** `release.yml` creates the release with
  `GITHUB_TOKEN`, and GitHub starts no workflow runs for events that token
  creates, except `workflow_dispatch` and `repository_dispatch`, so
  `release: published` never fires for it. `pages.yml` therefore also
  triggers on `workflow_run` for the `Release` workflow (when it succeeded;
  it deploys the latest published release) and on `workflow_dispatch` with a
  `tag` input, which deploys that tag (a re-deploy). Without a tag, dispatch
  builds a preview only. `release: published` stays for releases people
  make. Sources:
  https://docs.github.com/en/actions/security-for-github-actions/security-guides/automatic-token-authentication#using-the-github_token-in-a-workflow,
  https://docs.github.com/en/actions/writing-workflows/choosing-when-your-workflow-runs/events-that-trigger-workflows#workflow_run
- **Citations on the site.** The methodology and history pages cite as
  numbered `[n]` links to a per-page reference list, matching the paper's
  numeric citations. The generated Markdown keeps its title links.

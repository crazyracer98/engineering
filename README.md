# Engineering best practices

> [!NOTE]
> This repository is vibe coded with [Claude](https://claude.com/product/claude-code).

A cross-domain engineering best-practices taxonomy at research-paper
quality. One structured dataset (`data/`) generates split Markdown docs
(`publication/`), a Material for MkDocs site and a Pandoc/Typst PDF paper,
with automated integrity checks. The repository also records the
generalized method that produced the taxonomy.

Author: crazyracer98, with Claude. See [`docs/TEMPLATE.md`](docs/TEMPLATE.md)
for the repository scaffold (devcontainer, CI, checks, release contract,
template sync) inherited from
[`craftainer/template-base`](https://github.com/craftainer/template-base).

## Usage

Read the [site](https://crazyracer98.github.io/engineering/) or download
the [PDF paper](https://github.com/crazyracer98/engineering/releases/latest/download/engineering-best-practices.pdf).
Learn the rules with worked examples and real cases in the
[Learn section](https://crazyracer98.github.io/engineering/learn/), then test
yourself in the [Quiz section](https://crazyracer98.github.io/engineering/quiz/).
Each release also attaches `engineering-best-practices.md`,
`engineering-best-practices.yaml` and `references.json` (CSL-JSON).

Build everything locally (needs [`uv`](https://docs.astral.sh/uv/); Pandoc
and Typst come from PyPI):

```sh
uv sync --locked
uv run taxonomy check                         # dataset integrity checks
uv run taxonomy build                         # data/ -> publication/
uv run taxonomy site --out build/site         # the site
uv run taxonomy paper --out build/paper.pdf   # the PDF and build/references.json
make build release-assets                     # all of it; release files land in dist/
```

## How to cite

Cite the release you used: replace the edition and year below with the
edition (see `data/meta.yaml`) and release year you read.

```bibtex
@misc{engineering-best-practices,
  author       = {crazyracer98 and Claude},
  title        = {Engineering Best Practices --- Cross-Domain Taxonomy},
  year         = {2026},
  edition      = {1.0.0},
  howpublished = {\url{https://github.com/crazyracer98/engineering}},
}
```

> crazyracer98, with Claude, *Engineering Best Practices --- Cross-Domain
> Taxonomy*, edition 1.0.0, 2026. [Online]. Available:
> https://github.com/crazyracer98/engineering

## License

Prose and data are CC BY-SA 4.0; code and everything else is GPL-3.0.
| Paths | License |
|---|---|
| This repo's own prose and data: `docs/methodology.md`, `docs/history.md`, `docs/adrs/[0-9]*`, `docs/nfrs/NFR-*`, `data/`, `publication/`, `paper/` (except `paper/csl/`, CC BY-SA 3.0 per its own notice), `sources/` (except `sources/import/import_v9.py`, a script), and the generated site and PDF | [CC BY-SA 4.0](LICENSE-CC-BY-SA-4.0) |
| `src/`, `tests/`, `schema/`, scripts, workflows, configuration, the template-synced files under `docs/` (`docs/TEMPLATE.md`, directory `README.md`s, `template.md` files), and everything else | [GPL-3.0](LICENSE) |

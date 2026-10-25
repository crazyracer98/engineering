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

## License

Prose and data are CC BY-SA 4.0; code and everything else is GPL-3.0.
Paths marked (planned) don't exist yet.

| Paths | License |
|---|---|
| This repo's own prose and data: `docs/methodology.md`, `docs/history.md`, `docs/adrs/[0-9]*`, `docs/nfrs/NFR-*`, `data/`, `publication/`, `paper/` (except `paper/csl/`, CC BY-SA 3.0 per its own notice), `sources/` (except `sources/import/import_v9.py`, a script), and the generated site and PDF (planned) | [CC BY-SA 4.0](LICENSE-CC-BY-SA-4.0) |
| `src/`, `tests/`, `schema/`, scripts, workflows, configuration, the template-synced files under `docs/` (`docs/TEMPLATE.md`, directory `README.md`s, `template.md` files), and everything else | [GPL-3.0](LICENSE) |

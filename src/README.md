# src/

The `taxonomy` Python package: validation, checks and generators that
turn the dataset in `../data/` into the published docs, site and paper.
Built with `uv_build` from `../pyproject.toml`; the console script
`taxonomy` is `taxonomy.cli:main`.

## Modules

- `model.py`: typed views (`TypedDict`s, `Dataset`) and shared constants.
- `load.py`: `find_root`, `load_dataset(root)`, `load_registry(root)` (merges
  `data/sources.yaml`, `paper/references-extra.yaml` and
  `docs/methodology-references.yaml` into `slug -> Source`) and
  `load_registry_files(root)`.
- `ids.py`: rule-ID matching for any prefix in `meta.id_prefixes`
  (`id_key`, `id_finder`, `link_ids`, which links every ID of a range).
- `validate.py`: the integrity checks of
  [NFR-0001](../docs/nfrs/NFR-0001-dataset-integrity.md); `run_checks(root)`
  returns `Finding`s.
- `render_markdown.py`: `resolve_citations(text, registry, titles=None)`
  (turns `[@a]`, `[@a; @b]` and `[@a, p. 3]` into `[title](url)` links),
  `render_single(ds, registry)` and `render_chapters(ds, registry)`.
- `render_yaml.py`: `render_yaml(ds, registry)`, the flattened YAML.
- `build.py`: `generate`, `stale` and `write` for `../publication/`.
- `render_paper.py`: `build(out: Path, root: Path | None = None) -> None` builds
  the PDF paper (Pandoc with citeproc, then Typst) and `references.json` next
  to it; `write_csl_json(root, out)`. See [`../paper/README.md`](../paper/README.md).
- `render_site.py`: `build(out: Path, root: Path | None = None) -> None` builds
  the Material for MkDocs site (`assemble(root)` stages the pages; `../mkdocs.yml`).
- `verify_sources.py`: `run(...)` behind `taxonomy verify-sources`: fetches
  each quote's source (cache, origin, `via`, Internet Archive), extracts
  the text and checks the quote appears in it; see `../sources/README.md`.
- `cli.py`: `taxonomy check | build [--check] | site --out DIR | paper --out FILE | verify-sources`.

## Do

- Keep code typed; `mypy --strict` runs on this directory.
- Regenerate with `uv run taxonomy build` after any change to `../data/` or to
  a renderer, and commit `../publication/`; the `taxonomy-generated` hook
  fails otherwise.
- Load YAML with the round-trip loader (`ruamel.yaml` `YAML()`), never
  `typ="safe"` (ADR 0002).

## Don't

- Put dataset content here; it belongs in `../data/`.
- Edit `../publication/` by hand; it is generated.

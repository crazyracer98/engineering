# Zensical migration spike

Findings of a spike for issue
[#9](https://github.com/crazyracer98/engineering/issues/9): can the site build
on Zensical, the successor to Material for MkDocs, before Material's fixes end
on 2027-05-05 ([ADR 0002](adrs/0002-publication-toolchain.md))? The spike
changes nothing by default: MkDocs stays the builder, and Zensical is an
opt-in path.

## How to run the spike build

```sh
uv sync --locked --extra zensical
uv run taxonomy build
TAXONOMY_SITE_ENGINE=zensical uv run taxonomy site --out build/site-zensical
```

`render_site.build(out, root, engine="zensical")` does the same from Python.
The `zensical` extra in `pyproject.toml` pins `zensical==0.0.73` (released
2026-10-26, PyPI classifier `Development Status :: 3 - Alpha`, Python 3.11 to
3.14). `tests/test_render_site.py::test_zensical_build_matches_the_mkdocs_pages`
builds a fixture site both ways and runs only where the extra is installed. No
CI job was added: the default lane does not install the extra, and a
non-blocking job would need `--extra zensical` in `pages.yml` for little
gain over that test.

## What works

Zensical built the unmodified `mkdocs.yml` (Material theme, `palette`,
`features`, `search`, `toc`, `attr_list`, `tables`, `admonition`,
`md_in_html`, `extra_css`, `extra_javascript` with `type: module`, `nav`,
`validation:`) with `zensical build --strict` in about 2 s, "No issues found".
Compared with the MkDocs build of the same generated tree
(`build/site-src`, 58 pages):

| Aspect | MkDocs 1.6 + Material 9.8 | Zensical 0.0.73 |
|---|---|---|
| Pages | 58 HTML files | the same 58, none missing or extra |
| Nav links on the home page | all present | all present (only the logo link `.` differs) |
| Search | `search/search_index.json` (lunr), 340 entries | `search.json`, 340 entries, search UI markup present |
| Palette toggle | three states, labels as configured | the same three labels, `data-md-component="palette"` present |
| `quiz.js` | `<script type="module">` | `<script type="module">`, after the non-module theme bundle |
| `document$` | exposed by the theme bundle | exposed too (`window.document$` in the bundle), so `site-assets/quiz.js` takes its `document$.subscribe` branch; the fallback is not needed |
| Static quiz forms (`quiz/a`) | 16 `fieldset`, 16 `legend`, 16 `aria-describedby`, 16 `.hint` | identical counts |
| `md_in_html` and `attr_list` (`learn/a`, `07-rules`) | `id="p1"` present, 9 and 10 permalinks | the same ids and permalink counts |
| Downloads links | four release links | identical |
| Strict mode | exits 1 on warnings | exits 1 on warnings |
| Other files | `sitemap.xml`, `sitemap.xml.gz`, source maps | `sitemap.xml` only |

Heading ids differ only by the theme's skip-link and toc anchors (`__toc` in
MkDocs, `__skip` in Zensical); no author-set anchor (`#p1`, `#p56`) differs.

Strict mode and the `validation:` block work: with a missing page, a missing
anchor and a missing target injected, Zensical reported "page does not exist"
(twice) and "anchor does not exist" and aborted with `3 issues found` /
`RuntimeError: Aborted because --strict flag is set`. MkDocs reported four
warnings for the same input because it also flags the absolute link
`/abs/x` (`absolute_links: warn`); Zensical did not.

## What breaks or differs

1. **No `-d` / `--site-dir`.** `zensical build` takes only `-f`, `-c/--clean`
   and `-s/--strict`. The output directory comes from `site_dir` in the config,
   resolved against the config file. `render_site.py` therefore writes a derived
   copy of `mkdocs.yml` (`build/zensical-spike.yml`) with `site_dir` set.
2. **`site_dir` must be inside the project root.** An output under a temp
   directory fails with `Error: site_dir must be within project root`. The
   spike builds into `build/zensical-out` and copies the result to `--out`.
3. **Absolute paths crash.** A derived config with absolute `docs_dir` and
   `site_dir` died with a Rust panic: `thread '<unnamed>' panicked at
   crates/zensical/src/workflow.rs:698:10: invariant:
   Id(Format(Path(RootDir)))` and `pyo3_runtime.PanicException`. The spike writes
   both relative to the config file. The spike did not isolate which of the two
   triggers it.
4. **Search backend changes.** `search/search_index.json` becomes
   `search.json`; anything linking to or testing the old path breaks. Search
   behaviour in a browser (ranking, highlighting) was not exercised.
5. **No `sitemap.xml.gz`** and no source maps. No consumer in this repo.
6. **Strict-mode parity gap:** absolute links are not reported.
7. **Alpha status.** `0.0.x` releases roughly weekly, and the CLI help lists
   only `build`, `new` and `serve`. Documentation pages (compatibility, setup)
   describe `mkdocs.yml` support as covering "almost all settings", and say
   plugin coverage is incomplete.
8. **Not checked:** rendering in a browser (the quiz script running, dark mode
   switching, search results), the `classic` theme variant (the build used the
   default variant; Zensical's compatibility page says `classic` preserves
   Material's look), and Pages deployment. The Material-specific class
   names that `site-assets/quiz.css` relies on were not diffed in a browser.

## Effort estimate for the full migration

About 1 to 2 working days, plus one visual check pass, if Zensical is stable
enough by early 2027:

- Make Zensical the engine in `render_site.py` and drop the `mkdocs` /
  `mkdocs-material` dependencies, `NO_MKDOCS_2_WARNING` and the `-d` handling
  (half a day; the derived-config trick can go if `site_dir` is set to
  `build/site` and the CLI default is kept).
- Update `pages.yml`, `Makefile` and README wording; replace the
  `test_real_build_strict` and fixture build assertions that name MkDocs
  (half a day).
- Browser check of the quiz, dark mode, search and the `classic` variant
  (half a day), and a decision on whether to move `mkdocs.yml` to
  `zensical.toml`.

## Recommended migration plan outline

1. Re-run this spike on the then-current Zensical release in Q1 2027; check the
   open issues for `site_dir`, absolute paths and strict-mode parity.
2. Decide the config format: keep `mkdocs.yml` (works today) or convert to
   `zensical.toml` (the native format).
3. One PR: switch the default engine, remove MkDocs dependencies, update CI and
   docs, and record a new ADR superseding the Material part of
   [ADR 0002](adrs/0002-publication-toolchain.md).
4. Deploy a preview with `workflow_dispatch` on `pages.yml` and check the
   quiz, search, dark mode and Downloads links in a browser before the release
   that ships the change.
5. Finish before 2027-05-05, when Material for MkDocs fixes end. If Zensical is
   still unstable by March 2027, stay on Material: it keeps working, only
   without fixes.

## Sources

- https://zensical.org/compatibility/
- https://zensical.org/docs/setup/basics/
- https://pypi.org/pypi/zensical/json
- Observed output of `zensical build --help` and the builds above.

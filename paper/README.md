# paper/

Inputs of the PDF paper. `taxonomy.render_paper` assembles them with the
generated taxonomy; the licence is CC BY-SA 4.0 (`csl/` excepted, see
[`csl/README.md`](csl/README.md)).

## Build

```sh
uv run taxonomy paper --out build/paper.pdf
```

Writes `build/paper.pdf` (PDF/A-2b, A4) and `build/references.json` (the
CSL-JSON of every source). The intermediate `build/paper.md` (Pandoc Markdown)
and `build/paper.typ` (Pandoc's Typst output) stay next to them and are
gitignored. Pipeline: assemble Markdown, then Pandoc with `--citeproc
--csl paper/csl/ieee.csl` to Typst, then `typst.compile` with Typst's bundled
fonts only, `pdf_standards=["a-2b"]` and a timestamp derived from
`data/meta.yaml`'s `date`, so the output is reproducible. The build fails on any
Pandoc warning (for example `citeproc: citation ... not found`) and on any Typst
warning or error.

## Hand-written and generated

| Part | Source |
|---|---|
| Title block, keywords, licence | `metadata.yaml` (its `edition` must equal `data/meta.yaml`'s, or the build fails) |
| Abstract, 1 Introduction, 2 Related work, 6 Discussion, 7 Conclusion | `sections/*.md` (hand-written) |
| 3 Method | `docs/methodology.md`; the `## Phase` headings become 3.x, and each `> **Applied in this taxonomy:**` blockquote becomes a raw-Typst `#appliedbox[...]` box |
| 4 The taxonomy: how to read, master rule, overview, rigor matrix, rules (one card each) | generated from `data/` |
| 5 Conflict rules (cards) and analogy map | generated from `data/` |
| Appendices A glossary, B domain index, C management forms, D quotes (placeholder quotes skipped), E limits and source quality | generated from `data/` |
| References | citeproc |
| Layout (A4, numbered headings, repeating table headers, PDF metadata, cards) | `template.typ`, a Pandoc template (not plain Typst) |
| `references-extra.yaml` | paper-only sources, same shape as `data/sources.yaml` |

References in dataset prose to edition-9 section numbers ("section 6") are
rewritten to the paper's own ("Section 4.4", "Appendix E").

## Citations

- Cite as `[@slug]`, `[@a; @b]` or `[@slug, p. 3]`. The slug must exist in
  `data/sources.yaml`, `references-extra.yaml` or
  `docs/methodology-references.yaml`; slugs and URLs are unique across the three.
- Never write links for sources by hand; citeproc numbers them (IEEE) and
  builds the reference list from cited sources only.
- The dataset's per-use title overrides (`source_titles`, `sources_text`) are
  for the Markdown output only; the paper cites each source as `[@slug]`.
- CSL types: `article-journal` for known journal hosts, `book` when the notes
  give an ISBN, `report` for a PDF, `webpage` otherwise.

# tests/

`pytest` tests for `../src/taxonomy/`, run by the `pytest` prek hook.

- `conftest.py`: the `repo` fixture copies `data/`, `schema/`, `paper/`,
  `docs/`, `publication/` and `sources/` into a temp directory; `edit`
  changes a YAML file there.
- `test_checks.py`: one seeded violation per integrity check
  ([NFR-0001](../docs/nfrs/NFR-0001-dataset-integrity.md)), each asserting the
  check fails with a clear message, plus the clean-dataset test.
- `test_ids.py`: the edition-9 -> P1-P83 map (`sources/import/id-map.yaml`),
  category order, prefix-generic ID matching and linking (a range keeps its
  text, both ends linked), and the class coming from the `class` field.
- `test_publication.py`: `publication/` freshness, chapters, the flattened
  YAML, citation resolution and numbering, and the CLI. There is no round trip against the
  edition-9 Markdown any more (ADR 0003, "G1 delta").
- `test_render_site.py`: the assembled site tree and a real `--strict` MkDocs build.
- `test_render_paper.py`: CSL-JSON, the assembled paper Markdown, Pandoc
  failure on a missing citation, and one real PDF build marked `slow`
  (registered in `conftest.py`; a few seconds, so it runs in the default
  `pytest`; deselect it with `-m "not slow"`).
- `test_verify_sources.py`: `taxonomy verify-sources` offline (fake transport and
  clock; fixtures in `fixtures/verify/`, authored here, never third-party text).
- `js/quiz-core.test.js`: `node --test` unit tests for the quiz core in `../site-assets/quiz-core.js`
  (scoring, seeded drawing, progress storage that never throws;
  [NFR-0002](../docs/nfrs/NFR-0002-quiz-accessibility.md)), run by the `js-tests` prek hook.

## Do

- Add tests next to the behavior they cover, typed like `src/`.
- When you add a check to `validate.CHECKS`, add its seeded test and its row in
  the NFR.

## Don't

- Edit `../sources/import/` fixtures; those are verbatim provenance.
- Seed violations into the real `data/`; use the `repo` fixture.

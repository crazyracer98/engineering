# tests/

`pytest` tests for `../src/taxonomy/`, run by the `pytest` prek hook.

- `conftest.py`: the `repo` fixture copies `data/`, `schema/`, `paper/`,
  `docs/`, `publication/` and `sources/` into a temp directory; `edit`
  changes a YAML file there.
- `test_checks.py`: one seeded violation per integrity check
  ([NFR-0001](../docs/nfrs/NFR-0001-dataset-integrity.md)), each asserting the
  check fails with a clear message, plus the clean-dataset test.
- `test_publication.py`: the round trip against the edition-9 Markdown (only
  the version line may differ), `publication/` freshness, chapters, the
  flattened YAML, citation resolution and the CLI.
- `test_verify_sources.py`: `taxonomy verify-sources` offline (fake transport and
  clock; fixtures in `fixtures/verify/`, authored here, never third-party text).

## Do

- Add tests next to the behavior they cover, typed like `src/`.
- When you add a check to `validate.CHECKS`, add its seeded test and its row in
  the NFR.

## Don't

- Edit `../sources/import/` fixtures; those are verbatim provenance.
- Seed violations into the real `data/`; use the `repo` fixture.

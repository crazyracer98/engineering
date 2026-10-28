# sources/

Provenance for the taxonomy: material it was derived from.

- `import/` holds the two original inputs, verbatim and byte-identical.
  `engineering-best-practices.md` is edition 9, whose content is
  authoritative. `engineering-best-practices.yaml` is an older edition-6
  export (67 rules), used only as the schema seed. Neither is the source
  of truth: `data/` is (ADR 0003).
- `import/import_v9.py` is the importer that produced the first `data/`
  from those two inputs. It is now a frozen provenance record. By default
  (`--check`) it regenerates the import in memory and compares it with
  `data/` (exit 1 on any difference, which is expected once `data/` has
  been edited by hand). Only `--write` overwrites `data/`.

- `import/id-map.yaml` maps each of the 83 edition-9 rule IDs (U1–U58,
  R1–R9, C1–C16) to the opaque ID it has in 1.0.0 (P1–P83, numbered in
  category order, then the order of edition 9's section 7). It is provenance
  only: 1.0.0 is the first version, so `data/history.yaml` `id_map` stays
  empty. `import/rekey_d4.py` is the one-off script that computed the map and
  renamed the IDs; it refuses to run again. The importer and the two
  inputs keep the edition-9 IDs.

## Source verification

`uv run taxonomy verify-sources` fetches each quote's source and checks that
the quoted passages (the double-quoted parts of `data/quotes.yaml` `text`)
appear in it, after normalizing case, typographic quotes and dashes, soft
hyphens, hyphenated line breaks and whitespace, with PDF text extraction.
Placeholder rows are skipped; `...` / `[...]` split a passage into parts that
must match in order. Per source it tries the cache, the origin `url`,
`via.url`, then the Internet Archive snapshot closest to 2026-10-14
(reported as "verified via archive").

- Fetched text is never committed. It is cached under `build/source-cache/`
  (git-ignored; in CI via `actions/cache`), with conditional requests, a
  per-host delay of at least 2 s and an identifying User-Agent.
- `verification.json` is the committed manifest: per quote the URL, final
  URL, method (`origin | via | archive`), fetch date, SHA-256 of the fetched
  bytes, result and score, plus `quote_sha256` (SHA-256 of the normalized
  quote text) and `checked` (the UTC date of the run that verified the quote: the date
  part of its fetch date, or the run's date when nothing was fetched). Entries
  keep the value of the run that wrote them. No text. Only `--update-manifest`
  writes it.
- Every run reports manifest entries out of step with the current quotes:
  `stale` (the quote text no longer matches `quote_sha256`, or the entry has
  none: re-verify needed) and `orphaned` (the quote ID no longer exists or is a
  placeholder; `--update-manifest` prunes it). Both are only reported.
- Results: `matched`; `not-found` / `near-miss (score)` fail the run (exit 1);
  `blocked`, `gone`, `timeout`, `unreadable` and `paid` (paid source whose
  fetched page lacks the quote) are only reported (exit 0). A passage with no
  scorable part (under 4 letters or digits per part) is `no-quote`, never
  `matched`. `--only` / `--explain` with an unknown ID exit 2 and name it.
- When a fetched page lacks a passage the archive snapshot is tried before a failure is
  reported; private-use glyphs (bullets) are ignored. Quote marks (single, double, straight, curly) compare equal, and in PDF text a
  footnote marker glued to a word ("command12") is dropped.
- `--offline` uses only the cache; `--only Q12,Q13` limits the run;
  `--report FILE` writes the Markdown report; `--explain Q4,Q32` prints the best-matching
  source window per passage to stdout only.
- `.github/workflows/verify-sources.yml` runs it weekly, on demand and on PRs
  touching `data/quotes.yaml` or `data/sources.yaml`, and keeps one
  "Source verification: unverifiable sources" issue (label
  `source-verification`) up to date, closing it when all sources check out.

## Don't

- Edit the files in `import/`; changing a byte breaks their provenance.
- Run `import/import_v9.py --write` to change the taxonomy; edit `data/`
  instead (`--write` discards every edit made since the import).

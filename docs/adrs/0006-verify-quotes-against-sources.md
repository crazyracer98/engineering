# 0006. Verify quotes against their sources, report-only for unfetchable ones

## Status

Accepted

## Context

`data/quotes.yaml` holds verbatim passages, each tied to a source. A reader
trusts a quote only if the source really says it, and sources move, vanish,
get paywalled or block bots. Checking by hand does not scale to the 233
sources, and the third-party text must not be committed to a repository
that is itself published under CC BY-SA 4.0 ([ADR 0001](0001-license-prose-cc-by-sa-code-gpl.md)).

## Decision

We will fetch each quote's source and check that the quoted passages appear
in it (`taxonomy verify-sources`, run by `.github/workflows/verify-sources.yml`
weekly, on demand and on PRs that touch `data/quotes.yaml` or
`data/sources.yaml`). Text is normalized before comparing (whitespace,
typographic quotes and dashes, hyphenation, line breaks, private-use glyphs),
and PDFs go through text extraction.

- **Cache.** Fetched text is cached, never committed: under `build/` locally
  and in the GitHub Actions cache in CI, keyed by URL and ETag, with
  conditional requests, per-host rate limiting and an identifying
  User-Agent. The repository commits only a manifest (URL, fetch date, final
  URL, SHA-256 of the bytes, result), so no third-party text enters it.
- **Fallback.** If the origin is blocked or gone, or lacks the passage, the
  recorded alternative copy (`via`) is tried, then the Internet Archive
  snapshot closest to the date the quotes were checked (2026-10-14), reported
  as "verified via archive". The manifest records the fetch that produced
  the verdict.
- **Strictness.** A passage missing from a source that was fetched fails the
  job. A failure to fetch (blocked, gone, timeout, unreadable, paid) is only
  reported, and one tracking issue is opened or updated.

## Alternatives considered

- **Commit the fetched text.** Makes the check offline and reproducible, but
  republishes third-party text, which the licenses do not cover.
- **Fail on every unreachable source.** Honest, but bot-blocking and
  paywalls would keep CI red for reasons no contributor can fix, and the
  check would be switched off.
- **Check only when the data changes.** Misses link rot, which is the
  common failure, hence the weekly run.

## Consequences

- A wrong or altered quote is caught without trusting the contributor.
- A source that is blocked, gone or paid stays unverified, visibly, in the
  tracking issue. Replacing gone sources is research work, done in a
  `taxonomy-research` round.
- Matching is heuristic. Near-misses need a human reading; `--explain`
  prints the best-matching excerpt locally, uncommitted, for that.
- The job depends on external sites and the Internet Archive, so it is
  separate from `taxonomy check` and never gates a release.

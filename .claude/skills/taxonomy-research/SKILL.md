---
name: taxonomy-research
description: Run one methodology round on this taxonomy - sweep sources, decide each finding (new rule, change, supports only, null result), record verbatim quotes, bump the edition and add a history entry. Use when asked to "run a research round", "add a rule", "update the taxonomy", "check new sources", "upgrade sources" or "review the classification".
---

# Taxonomy research round

Runs one round of the method in [`docs/methodology.md`](../../../docs/methodology.md)
on this repo's dataset in `data/`. Read that page first; this skill is the
procedure, not a copy of the method. `data/README.md` says what each file
holds. The finding-record template is
[`references/finding-record.md`](references/finding-record.md).

Ground rules, from the methodology's cross-cutting principles:

- Edit `data/` directly. Never re-run `sources/import/import_v9.py --write`:
  it is a frozen provenance record and discards every edit made since.
  Its `--check` diverges from `data/` by design since gate G1.
- Never edit `publication/` by hand; `taxonomy build` regenerates it.
- Rule IDs and source slugs are frozen once published.
- Cite sources in prose only as Pandoc citations, `[@slug]`.
- Don't invent history. The first edition is 1.0.0; there is nothing before it.

## 1. Pick the phase

Ask the user, or infer from the request, which phase this round runs.
Phases 0 to 2 are done for 1.0.0, so a round is normally phase 3, 5 or 6.
Phase 4 is the checks that end every round.

| Request | Phase |
|---|---|
| Look for missing practices, new domains, new sources | 3, saturate coverage |
| Re-examine classes, counterexamples, evidence ratings | 5, classification review |
| Replace secondary sources with primary ones, re-check quotes | 6, source upgrade |
| A framing question (scope, unit, master rule) | 0, then say it may need a major bump |

Write down the scope of the round (which sub-fields, rules or sources)
before searching, so a later reader can tell what was and wasn't covered.

## 2. Sweep

Search the chosen scope: standards, regulations, professional bodies and
original papers first. For a wide sweep across many sources, hand off to
`anthropic-skills:deep-research` and give it the scope, the existing source
slugs (so it skips what is in `data/sources.yaml`) and the null-result
reporting you need (what was searched, how deep, what was not fetchable).
Treat its report as a lead list, not as evidence: open each source and
quote it yourself.

## 3. Decide every finding

Give each finding exactly one decision (use the record template):

| Decision | Effect on `data/` |
|---|---|
| **new rule** | Add to `rules.yaml` (next free ID in its prefix, sentence pattern, check, violation, evidence, sources), list it in its category in `categories.yaml`, add related/domain/conflict links as needed |
| **change** | Edit the existing rule (IF, wording, class, strength, evidence); keep its ID |
| **supports only** | Add the source and quote to the existing rule's `sources`/`quotes`; nothing else changes |
| **null result** | No rule change. Record the reason: searched and nothing found (with depth), source not fetchable, or out of scope |

Null results are kept in the round's notes: the PR description for the
round (a list of what was searched and why each lead was dropped), and, if
a domain was checked without a row, also in `domains.yaml`
`checked_without_row` with its `reason`. The one-line `summary` of the
`history.yaml` entry says how many rules were added or changed and that
null results are in the PR; it is not the place for the full list.

Don't let a "change" pass as "supports only" to finish a round early.
Saturation (phase 3) means a full loop over the uncovered sub-fields gave
no "new" and no "change"; one empty loop over favourite sub-fields isn't
that.

## 4. Record sources, quotes and judgments

- **Sources** go in `data/sources.yaml`: a new unique slug matching
  `^[a-z0-9]+(-[a-z0-9]+)*$`, a URL that isn't already in the file (search
  first), `kind: primary` or `secondary`, publisher, year, `paid`,
  `accessed` (today) and notes. Primary means the standard, regulation,
  paper or body that originated the practice. A secondary source is never
  relabelled primary because it is well known. If only a summary of a paid
  document was read, say so in `notes`.
- **Quotes** go in `data/quotes.yaml`: `text` copied verbatim from the page
  you opened (not from a summary or a search snippet), a `locator`
  (section, page or clause), the `source` slug and the rule IDs. Check
  each quote against the page again before committing.
- **Judgments** (a classification, a transfer of a rule to another domain,
  a resolution of a conflict, an evidence rating) are labelled as the
  author's assessment in the text, as elsewhere in the dataset. Never
  raise an evidence rating quietly after a source swap; say why.
- Anything not checked, not fetchable or resting on a weak source is
  written into the dataset's limits (`method.yaml`), not left in notes.

## 5. Per-phase checklist

**Phase 3, saturate coverage.** Pick the sub-fields with few or no rules;
search each; compare against an outside exhaustive list; decide every
finding; loop again. Exit: a full loop over the uncovered sub-fields yields
no new and no change. Failure modes: stopping after one empty loop; a
shallow search recorded as a null result (always record depth); skipping
the outside list.

**Phase 5, classification review.** Re-check each touched rule's class
(U, R, C), every conditional rule's counterexample and the checklist
(five to nine items). Exit: every rule has a class, every conditional rule
has a counterexample, checklists are five to nine items. Failure modes:
taking an adoption gap for a counterexample; an unfalsifiable criterion;
a counterexample that is one odd system; changing IDs (that is a major
bump and needs `id_map` entries).

**Phase 6, source upgrade.** Replace secondary sources with primary ones,
re-check every touched quote. Exit: every rule has a primary source or is
on the exceptions list with a reason, every quote is checked, every limit
is written down. Failure modes: a quote taken from a summary and
attributed to the original; quietly raising evidence; hiding paid or
unavailable documents.

**Phase 4, checks (every round).** Next section. Failure modes: checking
only formatting; editing generated output; accepting an unexplained
difference silently.

(Phases 0 to 2 are framing, collecting and standardising; a round that
reopens them is a redesign, so confirm with the user first.)

## 6. Check and build

```
uv run taxonomy check        # dataset integrity (NFR-0001): schemas, references, relation inverses, counts
uv run taxonomy build        # regenerates publication/
uv run taxonomy build --check  # confirms publication/ is up to date
```

Fix findings in `data/`, never by loosening a check. Commit the
regenerated `publication/` together with the `data/` change.

## 7. Bump the edition

Pick the highest part that applies (methodology "Versioning"):

| Change | Part |
|---|---|
| A rule removed, or a rule ID changed | major |
| A field, column, vocabulary value, relation type or strength keyword removed or renamed | major |
| A rule added, or a rule's meaning changed | minor |
| A field, column, vocabulary value, relation type or strength keyword added | minor |
| Wording or source fixes, or rewording without a change of meaning | patch |

Then:

1. Set `edition` in `data/meta.yaml` (and `date`).
2. Add an entry at the top of `editions` in `data/history.yaml`, newest
   first: `edition`, `date`, `summary`. On a major bump that moves IDs,
   add `id_map` entries (`old`, `new`, `edition`).
3. Add the matching section under "Later editions" in `docs/history.md`.
4. Re-run `uv run taxonomy check` and `uv run taxonomy build`.

Tell the user that the next release must produce exactly this version:
`release.yml` with `release_type: full` and the `bump` (`major`, `minor` or
`patch`) that takes the latest tag to `meta.edition`. The tag equals
`meta.edition`; if they differ, the round isn't finished. Don't run the
release; it is the user's call.

## 8. Finish

```
git add -A
prek run --all-files --hook-stage manual
```

Show the output tail. Report, in the PR description: the scope and phase,
every finding with its decision, the null results with reasons and search
depth, the author's judgments, and the version with its bump reason.

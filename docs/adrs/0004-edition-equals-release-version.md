# 0004. Make the edition equal to the SemVer release version

## Status

Accepted

## Context

The taxonomy is published as a dataset, a set of Markdown files, a site and a
PDF. Readers cite it and compare versions, so a version number must say what
changed. A separate edition counter next to the release tag would let the two
drift: a release could ship edition text that names another version.

The imported text calls itself "Version 9", a working label from before the
repository existed. The user decided that no history before the repository is
available, so the first published version is `1.0.0`.

## Decision

We will use the SemVer release tag (https://semver.org/spec/v2.0.0.html) as
the edition. `meta.edition` in `data/meta.yaml` always equals the tag that
ships it, with the tag written `v<edition>`, and `1.0.0` is the first edition.
The header line of the generated Markdown reads
`Version <edition> · <date> · <counts>`, built from `meta.edition`,
`meta.date` and the counts of rules, conflict rules and categories.

A change to the dataset bumps the edition as follows.

Rule-level changes:

- **Major:** a rule is removed or a rule ID changes.
- **Minor:** a rule is added or the meaning of a rule changes.
- **Patch:** wording or source fixes that leave the meaning unchanged.

Data-format changes follow SemVer's compatibility rule (items 7 and 8 of the
specification):

- **Major:** a field, table column, vocabulary value, relation type or
  strength keyword is removed or renamed.
- **Minor:** one is added.
- **Patch:** wording changes with no change of meaning.

Each bump adds an entry to `data/history.yaml`. When one change is of several
kinds, the highest bump applies.

## Consequences

- One number identifies the dataset, the files in `publication/`, the site,
  the PDF and the release. Citing "version 1.2.0" is unambiguous.
- Someone releasing must change `meta.edition` first. The release lane checks
  that the tag equals `meta.edition`.
- A removed or renumbered rule forces a major bump even when the edit is small.
  That is the intended price of stable IDs.
- Judging "meaning changed" against "wording fixed" is a human call and is not
  checked by `taxonomy check`.
- Earlier working labels (such as "Version 9") are not versions of this
  scheme and are not recorded in the history.

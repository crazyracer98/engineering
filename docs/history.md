# History

## 1.0.0 (first edition)

Version 1.0.0 is the first published edition of this taxonomy. There is no
earlier edition and no earlier published history. This page does not
reconstruct one.

The content of 1.0.0 is dated 2026-10-14. It contains:

- 83 rules (P1 to P83): 58 universal (U), 9 risk-scaled (R) and 16 conditional (C);
- 8 conflict rules (K1 to K8);
- 9 categories (A to I), each with one question in the quick view.

The imported source document is headed "Version 9". That was its
pre-publication working label. It is not a published edition number: 1.0.0 is
the first published edition, and there are no published earlier editions.

The imported source also numbers its rules by class (U1, R1, C1). Before
1.0.0 they were renamed to opaque IDs, P1 to P83, in category order; this is
not an edition change. `sources/import/id-map.yaml` maps each edition-9 ID to
its 1.0.0 ID, and `data/history.yaml` `id_map` stays empty.

The numbers are the counts in the imported Markdown source
(`sources/import/engineering-best-practices.md`), which is the starting
point of the dataset in `data/`.

[The methodology](methodology.md) shows how its method was applied to this
content in the "Applied in this taxonomy" boxes of that page.
Those boxes describe what the 1.0.0 content shows and say where it does not
show how a step was done.

## Later editions

Later editions are numbered by SemVer, and the version equals the release
tag (see "Versioning" in [the methodology](methodology.md)). Each one is
recorded in two places: `data/history.yaml` (the machine-readable record,
including the map from old rule IDs to new ones) and a new section at the top
of the list of editions on this page (newest first).

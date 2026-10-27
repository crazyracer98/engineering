# History

## 1.1.0 (learning hub)

Version 1.1.0 adds a way to learn the rules, not only look them up. It is a
minor edition under ADR 0004: it adds content and changes no rule, no rule ID
and no field of the dataset. It is dated 2026-10-27.

The new content is on the site only:

- a worked example for each of the 83 rules, with a management variant for
  the 67 rules that have a management form;
- one example for each of the 130 domain rows;
- 27 real cases that cover 44 rules, with 198 verbatim quotes from their
  sources;
- 193 multi-select quiz questions, in a quiz for each of the 9 categories, a
  quiz on the 8 conflict rules and a mixed test of 10 random questions.

Examples are illustrative and are not evidence. Case quotes are checked
against their sources the same way as rule quotes (ADR 0006), using
`verify_sources`. The examples, cases and questions are data in `data/learn/`
(ADR 0008).

The paper, the single-file Markdown and the YAML release asset are
unchanged. Learning content may be added to them in a later minor edition.

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

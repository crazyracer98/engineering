# History

## 1.1.1 (source fixes)

Version 1.1.1 fixes sources. It is a patch edition under ADR 0004: no rule,
rule ID, rule text or field of the dataset changes. It is dated 2026-10-27.

- Two secondary sources had gone (HTTP 404, no archive snapshot) and are
  replaced. The legal-hold trigger (Q56, management form of P83) is now quoted
  from the Sedona Conference Commentary on Legal Holds, Second Edition (2019)
  itself, a primary source, instead of a law-firm article about it. The
  hierarchy of controls in ISO 45001 clause 8.1.2 (Q40, management form of
  P38) is quoted from an Auditor Training Online article that reproduces the
  clause; it stays secondary, because the ISO text is paid. Both quotes were
  re-taken verbatim from the new sources and verified.
- The UCSD lecture notes on von Neumann's probabilistic logics (a P45 source)
  could not be reached and have no archive snapshot. They are replaced by von
  Neumann's own 1952 Caltech lectures.
- Authors that had been set from memory were checked against each work's
  record page and recorded in the source notes. One was wrong: the PMI
  article on the origins of CPM is by Kelley, Walker and Sayer, not Kelley
  alone. Romero's given name is completed from the OSTI record (Vicente
  Jose). The others were confirmed. That PMI article is also no longer
  marked paid: its page carries the full text without a login.
- The National Academies report on accident precursors (a P82 source) now
  links to its committee summary chapter, which describes near misses before
  major accidents and the normalization of deviance. The old link led to an
  unrelated chapter of the same volume, on inherently safer design.
- Dead links are fixed. The Jargon File is linked over http, because its
  https address has no valid certificate. The OECD procurement toolbox page
  and the Nowlan & Heap report are linked as Internet Archive copies, because
  their hosts are gone or fail TLS. The three FDA pages are live; they only
  turn automated link checkers away, so their links are unchanged.

The three replaced sources are removed from the registry, because every
registered source must be cited (`taxonomy check`); their slugs are not reused,
and the notes of the sources that replace them name them.

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

The paper, the single-file Markdown and the YAML release asset carry no
learning content; only their edition number and date change. Learning content
may be added to them in a later minor edition.

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

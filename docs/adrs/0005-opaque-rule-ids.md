# 0005. Identify rules by opaque IDs P1–P83

## Status

Accepted

## Context

The imported text keyed rules by class: U (universal), R (rule from a
regulated domain) and C (conflict-resolution) plus a number. An ID that
encodes the class carries meaning that can change. If a rule is reclassified,
or the categories are reorganized, its ID is wrong or must change, and an ID
change is a major bump ([ADR 0004](0004-edition-equals-release-version.md)).
Readers cite rules by ID, and the IDs appear in prose, anchors and the
relations between rules, so they must stay valid across editions.

The decision came late, after the dataset was imported and checked but before
1.0.0, when nothing had been published, so renaming cost nothing for readers.

## Decision

We will identify the 83 rules by the opaque IDs **P1–P83**, numbered in
category order (A to I), then in section-7 order within each category. Class
and category are fields of the rule, shown next to the ID; code takes the
class from the `class` field and never from the ID's letter. The conflict
rules keep K1–K8 and quotes keep Q, so a prefix still tells the kinds of
entry apart in prose. Anchors read `#p12`.

A new rule takes the next free P number. Stable IDs win over category order
for rules added later, so adding a rule never renumbers another.

In prose, two adjacent IDs stay separate. A run of three or more is written
as a range, and the renderers keep it as written and link both ends instead
of expanding it. The first rename expanded every range; the user reversed
that at review so the text stays as written.

The edition-9 to 1.0.0 mapping is provenance, not edition history. It lives in
`sources/import/id-map.yaml`, and `data/history.yaml` `id_map` stays empty,
because 1.0.0 is the first version ([ADR 0004](0004-edition-equals-release-version.md)).

Sources:

- https://www.w3.org/Provider/Style/URI

## Alternatives considered

- **Keep U/R/C prefixes.** Familiar to anyone who read the source text, but
  the ID would assert a class that is a judgment and may be revised.
- **Number rules within a category (A1, B3).** The same problem: moving a
  rule between categories would change its ID.
- **Slug-style names.** Self-describing, but long to cite and they tempt
  renaming when the wording is refined.

## Consequences

- Reclassifying a rule or restructuring the categories never changes an ID,
  so the major-bump price of ADR 0004 is only paid for real removals.
- An ID says nothing about the rule. Readers must look at the class and
  category fields, which the generated outputs print beside it.
- Citations of the pre-publication labels (U1, R1, C1) resolve only through
  `sources/import/id-map.yaml`.
- After the first release, category order and ID order drift apart as rules
  are added. This is accepted.

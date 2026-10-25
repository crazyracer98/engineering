# Discussion {#sec-discussion}

## What the taxonomy is, and what it is not {#sec-disc-scope}

The taxonomy is a structured synthesis of published practice. Its claim is
narrow: each rule states a practice that published sources support, under a
stated condition, with a stated reason, a check and a typical violation. It
does not claim that following a rule has a measured effect in every domain
the rule applies to, and its evidence ratings do not measure such an effect.
As Section 2 notes, the rating "strong" means that a standard, code,
regulation or professional body requires the practice. In GRADE's terms it
is closer to the authority behind a recommendation than to the quality of
the evidence for an effect, and GRADE warns against mixing the two
[@guyatt-2008-grade]. Readers who need an effect estimate for a rule should
go to the primary sources listed on its card, not to its rating.

The same caution applies to applicability. The classification test asks
whether a rule *can* apply, and a domain without the practice is treated as
an adoption gap, not a counterexample. That choice is what lets the
universal rules apply across all 130 domains, but it also means that a rule
is asserted to apply in many domains where no source from that domain was
found. The assertion is a reasoned extrapolation, and it is the author's
judgment.

## Open limits {#sec-disc-limits}

The limits below are recorded with the sources and carried into the
appendices. They are stated here because they bound what the results can
support.

**Secondary-only support.** Every rule has at least one primary source
except C15 (late work and added people, Brooks's law). Its support is the
Jargon File and a trade article, because the primary source is a 1975
book that is not online. In the management forms, three rules (C7, U13 and
U27) rest on secondary pages for their management form only; the rules
themselves have primary engineering sources. The integrity checks treat C15
as a declared exception, so it cannot be forgotten.

**Paid standards.** The texts of the ISO standards, PRINCE2 and PMBOK are
paid. For these, the taxonomy quotes only official summaries, press releases
or secondary pages, and says so where it does. The same holds for this
paper's use of ISO/IEC/IEEE 15288:2023 and the INCOSE handbook
[@iso-iec-ieee-15288-2023; @incose-se-handbook-5]. Anyone quoting a
requirement for an audit should check the original text first.

**Copies and partial texts.** Several primary texts were read through
copies that reproduce them word for word, and the sources name both the
copy and the original. A few primary texts could not be retrieved in full,
so a recital, an abstract or a summary is quoted instead; the appendices
list each case. One numerical table (the resource-margin phase values cited
for U25) comes from a garbled extraction and is marked to be checked before
it is quoted.

**Contested evidence.** Four rules carry a stated caveat. Goal setting
(U55) is contested by Deming's rejection of numerical goals, and conflict
rule K8 resolves the tension rather than hiding it. Guided change (U58)
rests on a practitioner model with limited empirical testing. Decision
speed by reversibility (U50) rests on a chief executive's letter, not on
research. Part of U57 (feedback should focus on the task) is the author's
summary of the cited authors' theory.

**Cross-reference-only transfers.** Six rules (R5, U30, U44, C13, U33 and
U37) have no management source; their management form is a transfer by
analogy and is the author's judgment. The table of domains checked without a
separate row likewise lists, for each such domain, the rules that apply by
cross-reference; that column is the author's judgment, not a sourced
finding.

**Classification and conflict rules.** The class of each rule (U, R or C)
is the author's judgment against the test, and the counterexamples named by
the conditional rules are reasoned, not sourced. The conflict rules K1–K8
are the author's synthesis unless their basis names a source.

**Standard editions.** Standards change under a taxonomy that cites them.
The editions were checked on 2026-10-14: ISO 9001:2015 is withdrawn and ISO
9001:2026 was published on 16 September 2026, with a planned three-year
transition; ISO 14001:2015 is withdrawn and replaced by ISO 14001:2026; ISO
22301:2019, ISO 21502:2020, ISO 30401:2018 and ISO 45001:2018 are current but
marked to be revised; ISO 30414:2018 is withdrawn, and the catalogue page of
its 2025 successor was not checked. Any later change to these standards can
change a source, a quote or an evidence rating.

## Threats to validity {#sec-disc-threats}

**Coverage and selection.** The list of domains and the sweep of each were
carried out by the author, not under a registered search protocol. The
method stops when a loop over uncovered domains yields only confirmations
and null results, which is a form of saturation. Saturation is "essentially
a predictive statement about the unobserved based on the observed"
[@saunders-2018-saturation], so a stopped search is evidence that new rules
have become rare, not proof that none remain. The sources are also biased
toward what is freely available online and written in English, and paid
standards, which carry much of the codified practice in several domains,
could be read only through their summaries.

**Single-rater judgments.** The classification, the evidence ratings, the
counterexamples, the management transfers and the conflict resolutions were
made by one author. No second rater classified the rules independently, so
no agreement statistic exists. The classification test is stated precisely
enough to be repeated, which makes such a check possible, but it has not
been done.

**Checklist size.** The nine-question quick view rests on a practitioner's
rule of thumb that five to nine items is "the limit of working memory"
[@mann-checklist-manifesto-notes]. The cognitive literature puts the limit
lower: Cowan's review argues for "A single, central capacity limit averaging
about four chunks" [@cowan-2001-magical-number-four]. The quick view is a
navigation aid with one question per category, and each question bundles
several checks. Whether nine such questions work as a checklist under time
pressure is untested. The checklist evidence itself is mixed: the WHO study
found lower death and complication rates after introduction
[@haynes-2009-surgical-checklist], and the Ontario study of mandatory
adoption found no significant reduction [@urbach-2014-ontario-checklists].

**Domain of the examples.** Every rule carries one worked example from
software and infrastructure operations, so that the rules can be compared
side by side. This makes the examples uniform, but it may also make rules
that fit that domain read more naturally than rules that do not. The
examples illustrate the rules; they are not evidence for them.

**Tool assistance.** As the author line states, the taxonomy and this paper
were produced with an AI assistant. The main risk this adds is a misquoted
or misattributed source. The method addresses it by requiring every quote
to be verbatim and checked against the linked page, with a locator, and by
labeling every judgment as the author's. The quotes in this paper were
checked against their sources on 2026-10-25, with one exception: the
INCOSE criteria in Section 2 are quoted as recorded with the taxonomy's
sources, because the document's server refused a re-check.

**Decay of links and sources.** Web pages move and standards are revised.
The dataset records an access date only for the sources behind the direct
quotes (56 of its 233 sources, all checked on 2026-10-14), and a scheduled
link check runs over the published text, but a citation that was valid when
it was checked may not stay valid.

## Future work {#sec-disc-future}

The method is designed to be run again. Further saturation rounds over the
domains checked without a separate row, and over domains not yet listed,
would test whether the rule set is as close to complete as the stopping rule
suggests. Each round would ship as a new edition under semantic versioning:
a major version when a rule is removed or an ID changes, a minor version
when a rule is added or its meaning changes, and a patch for wording or
source fixes.

The rules themselves call for empirical work that this paper does not do.
Three studies follow directly from its limits: an inter-rater study of the
classification test, in which independent raters classify the rules and
their agreement is measured; a rating of the evidence for each rule's effect
on a GRADE-like scale [@guyatt-2008-grade], kept separate from the current
endorsement rating; and field use of the nine-question quick view in
design or project reviews, comparing what reviews find with and without it.
Expert review by practitioners in the domains that contributed few rules
(for example mining, nuclear and agricultural engineering, with one domain
row each) would test the cross-reference transfers.

Some limits can be closed by better sources rather than new research: a
primary source for C15, the full texts of the paid standards for the rules
that quote only their summaries, and the documents that could not be
retrieved in full. Finally, the method itself can be tested by applying it
to another field where practices have to be gathered from many sources into
checkable rules, and comparing the result with that field's existing
guidance.

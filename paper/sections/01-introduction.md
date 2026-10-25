# Introduction {#sec-introduction}

Every engineering discipline accumulates practices that its practitioners
regard as good: design margins in structural and mechanical engineering,
redundancy in power systems and aerospace, independent checking of drawings
and calculations, checklists in aviation and surgery, change review in
software operations. Many of these practices recur, under different names,
in disciplines that rarely cite each other. A structural engineer's factor of
safety, a project manager's schedule buffer and a site reliability engineer's
capacity headroom all keep capacity above expected load. The knowledge is
published, but it is published per domain, in handbooks, codes, standards and
incident reports that each assume their own vocabulary and their own class of
system.

Systems engineering has the strongest claim to a cross-domain view, and it
has produced two kinds of general guidance. Process standards and handbooks
describe *what processes* an organization runs across a system's life cycle
[@iso-iec-ieee-15288-2023; @nasa-se-handbook-rev2; @incose-se-handbook-5].
Principles describe *what is true* of systems engineering in general, and
are deliberately kept apart from instructions: INCOSE's criteria require a
principle to "Transcend life cycle", "Transcend system type" and "Transcend
context", and to "Not be how-to statements" [@incose-se-principles].[^quotes]
SEBoK states the same criteria and adds that "SE in application is specific
to stakeholder needs, solution space, resulting system solution(s), and
context throughout the system life cycle" [@sebok-se-principles]. Between
these two levels sits the layer that practitioners most often reach for and
that is least often written down across domains: *practices*, actions that
can be checked, stated with the condition under which they apply and the
reason they work.

[^quotes]: The INCOSE wording is quoted as recorded in the taxonomy's method
section, which checked it against the linked document on 2026-10-14. A
re-check while this paper was written was refused by the server (HTTP 403);
see Section 6.

This paper presents a taxonomy of that layer. It states 83 engineering
practices as rules in one fixed sentence pattern, IF a condition holds, THEN
take an action, BECAUSE of a stated reason, and it adds a check and a typical
violation to each rule, so that a reviewer can tell whether the rule was
followed. Eight further conflict rules (K1–K8) decide between rules that pull
in opposite directions, for example adding redundant parts against keeping a
design simple. The rules fall into 9 categories that follow the life cycle of
an engineered system: who is responsible, what is known and decided, how the
system is designed, protected and given capacity, how it is checked, changed
and operated, and how the organization learns. Each category is condensed
into one question, so the taxonomy can be used as a nine-item checklist as
well as a reference.

The taxonomy makes four contributions.

1. **A classification of practices by applicability.** Each rule is
   universal (U, 58 rules), risk-scaled (R, 9 rules) or conditional (C, 16
   rules). The test is a falsification question derived from the INCOSE and
   SEBoK criteria above: is there a common class of engineered systems in
   which the rule's condition can never be true during the whole life cycle?
   A conditional rule must name such a system as its counterexample. The test
   asks whether a rule *can* apply, not whether a domain already practices
   it, so a domain that lacks a practice has an adoption gap, not a
   counterexample. The classification of each rule is the author's judgment
   against this test, and the counterexamples are reasoned, not sourced.
2. **One scaling rule for all others.** A master rule scales the rigor of
   every rule to the consequence of failure times the uncertainty, and keeps
   reducing risk until the cost of the next reduction is grossly
   disproportionate to its benefit (ALARP). A two-by-two rigor matrix states
   which rules apply in which cell and what level of independent checking is
   required there. The results map the same idea onto its management
   names: tailoring, risk appetite and irreversibility.
3. **Coverage of the organization as well as the system.** Every engineered
   system is designed, built and operated by an organization, so rules about
   decisions, delegation, selection, feedback and change belong in the same
   taxonomy. The rules were collected from 130 domains in 20 branches, 12 of
   them engineering branches and 8 management branches, and every rule is
   also stated in management form, for teams, projects and organizations.
4. **Explicit evidence and source quality per rule.** Every rule lists its
   sources, primary sources first, with an evidence rating and verbatim
   quotes where a quote decides the rating. All but one rule (C15, Brooks's
   law) rest on at least one primary source. The evidence ratings are the
   author's assessment, and the paper reports the limits of the source base
   openly instead of averaging them away.

The taxonomy is a synthesis of published practice. It does not test any rule
empirically, and a rule's presence in it means that published sources
support the practice, not that its effect has been measured across the
domains it is said to apply to. The paper also does not replace any
domain's codes or standards; one rule (C1) states explicitly that codes are a
minimum to meet, not a ceiling.

Beyond the content, the paper describes the method that produced the
taxonomy, stated generally enough to be reused in other fields: frame the
scope and scales, collect, standardize, saturate coverage, move to a single
machine-checked source, review the classification critically, and upgrade
the sources. The taxonomy is released as a versioned dataset from which the
tables, the rule cards and this paper's results are generated, with
automated integrity checks. This paper describes version 1.0.0, and the
release version is the edition number of the taxonomy.

The rest of the paper is organized as follows. Section 2 places the taxonomy
among systems engineering principles, process standards and handbooks,
checklist research, and evidence grading. Section 3 describes the method.
Sections 4 and 5 present the generated taxonomy: the master rule, the
overview and quick view, the rigor matrix, and each rule as a card. Section 6 discusses
the open limits, threats to validity and future work, and Section 7
concludes. The appendices hold the glossary, the domain index, the
management form of each rule, the direct quotes and the limits recorded with
the sources.

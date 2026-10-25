# Related work {#sec-related-work}

The taxonomy draws on four bodies of work: statements of systems engineering
principles, process standards and handbooks that organize engineering
practice, research on checklists, and methods for grading and reporting
evidence. This section summarizes each and states where the taxonomy
follows it and where it departs from it.

## Systems engineering principles {#sec-rw-principles}

INCOSE's Systems Engineering Principles work, led by Watson and colleagues,
sets criteria that a statement must meet to count as a systems engineering
principle. Among them, a principle must "Transcend life cycle", "Transcend
system type" and "Transcend context", and must "Not be how-to statements"
[@incose-se-principles]. The same document describes heuristics as guidance
"emerging from practice in a given context or area" [@incose-se-principles].
(The INCOSE wording here is as recorded in the taxonomy's method section; see
the note in Section 1.)
SEBoK's article on the topic gives a matching list of criteria: a principle
"transcends a particular lifecycle model or phase", "transcends system
types", "transcends a system context", "is not a 'how to' statement" and "is
supported by literature or widely accepted by the community"
[@sebok-se-principles]. SEBoK also frames heuristics and principles as stages
of one development: "A key moment in their evolution occurs with gaining
insight into why they work, at which point they become principles"
[@sebok-se-principles]. It reports that INCOSE's principles working group
"developed 15 principles and 3 hypotheses", and its first listed principle is
that "SE in application is specific to stakeholder needs, solution space,
resulting system solution(s), and context throughout the system life cycle"
[@sebok-se-principles].

The taxonomy takes two things from this work. First, it adopts the three
transcendence criteria as the basis of its classification test: a universal
rule must hold across life cycle, system type and context, and a conditional
rule is one for which a common class of systems exists where its condition
never arises. Second, it follows SEBoK's point that application is specific
to context, by letting one master rule set how strictly every universal rule
is applied. It departs from the principles work on purpose in one respect.
Its rules are actions with checks, which the "not how-to" criterion
excludes, so its universal rules are universal *practices*, not principles
in the INCOSE sense. In the terms of SEBoK's evolution, the rules sit closer
to heuristics that have been given an explicit condition and reason (the
author's reading, not a claim made by SEBoK).

## Process standards, handbooks and bodies of knowledge {#sec-rw-standards}

ISO/IEC/IEEE 15288:2023 "establishes a common framework of process
descriptions for describing the life cycle of systems created by humans",
and applies to "one-of-a-kind systems, mass-produced systems, and
customised, adaptable systems" [@iso-iec-ieee-15288-2023, abstract]. Its
abstract also states that it "does not prescribe a specific system life
cycle model, development methodology, method, modelling approach or
technique" [@iso-iec-ieee-15288-2023, abstract]. The standard's text is paid,
and this paper relies only on the official abstract. The INCOSE Systems
Engineering Handbook, in its fifth edition, describes itself through its
publisher as describing "the state-of-the-good-practice of systems
engineering" and as an elaboration of the life cycle processes of
ISO/IEC/IEEE 15288:2023 [@incose-se-handbook-5]; it is also paid and was not
read for this paper.

The NASA Systems Engineering Handbook (NASA/SP-2016-6105 Rev2) is the
best-known freely available handbook of this kind. It "describes systems
engineering best practices that should be incorporated in the development
and implementation of large and small NASA programs and projects"
[@nasa-se-handbook-rev2, p. 1], aims "to communicate principles of good
practice as well as alternative approaches rather than specify a particular
way to accomplish a task", and states that it "is not intended in any way to
be a directive" [@nasa-se-handbook-rev2, p. viii]. It treats adaptation to a
project as part of the method: tailoring and customization "are essential
systems engineering tools that are an accepted and expected part of
establishing the proper SE NPR requirements for a program or project"
[@nasa-se-handbook-rev2, sec. 3.11.1].

Bodies of knowledge play a similar role within one discipline. The SWEBOK
Guide, version 4.0, "reflects the current state of generally accepted,
consensus-driven knowledge" in software engineering and is organized in 18
knowledge areas [@swebok-v4].

These works organize practice by *process* (15288, the INCOSE handbook),
by *project life cycle* within one agency (NASA), or by *knowledge area*
within one discipline (SWEBOK). The taxonomy organizes it by *practice*
across disciplines, and states each practice with the condition under which
it applies, a check and a violation. The two approaches complement each
other: a process standard says which processes to run, and the taxonomy
says what a reviewer should expect to see done inside them, whatever the
domain. Its master rule plays the role that tailoring plays in the NASA
handbook, but it is stated once for all rules instead of per requirement. To
the author's knowledge, none of the works above states cross-domain
practices as conditional rules that each name a counterexample system; this
is the author's assessment of the works cited here, not the result of a
systematic search.

## Checklist research {#sec-rw-checklists}

Checklists are both one of the taxonomy's rules (U32) and the format of its
quick view, so the evidence on them matters twice. Gawande's *The Checklist
Manifesto* made the case for short checklists across aviation, construction
and medicine [@gawande-2009-checklist-manifesto]. Notes on the book record
its rule of thumb for checklist length: "A rule of thumb some use is to keep
it to between five and nine items, which is the limit of working memory"
[@mann-checklist-manifesto-notes]. The taxonomy uses this rule of thumb to
justify a quick view of nine questions, one per category.

The most cited evidence for checklists in safety-critical work is the WHO
Surgical Safety Checklist study. Haynes and colleagues introduced a 19-item
checklist in eight hospitals in eight cities and compared patients before
and after its introduction: "The rate of death was 1.5% before the checklist
was introduced and declined to 0.8% afterward (P=0.003)", and inpatient
complications fell from 11.0% to 7.0% [@haynes-2009-surgical-checklist].
The authors concluded that implementation "was associated with concomitant
reductions in the rates of death and complications"
[@haynes-2009-surgical-checklist]. The design was a before-and-after
comparison, not a randomized trial. A later population-level study of
mandatory adoption in Ontario, covering 101 hospitals, found that
implementation "was not associated with significant reductions in operative
mortality or complications" [@urbach-2014-ontario-checklists]. The
taxonomy lists both studies among the sources for U32, and rates U32's
evidence as moderate, not strong.

The five-to-nine range itself rests on older and contested ground. Miller's
1956 paper gave the field the phrase "the magical number seven, plus or
minus two" [@miller-1956-magical-number-seven]. Cowan's later review argues
that Miller's number "was meant more as a rough estimate and a rhetorical
device than as a real capacity limit", and that "A single, central capacity
limit averaging about four chunks is implicated"
[@cowan-2001-magical-number-four]. The taxonomy keeps nine questions because
a quick view needs one entry per category and because Gawande presents the
range as a practitioner's rule of thumb, not as a cognitive law. Section 6
returns to this.

## Evidence grading and reporting {#sec-rw-evidence}

GRADE is the most widely adopted system for rating evidence in clinical
guidelines. Its starting point is that "Guidelines are inconsistent in how
they rate the quality of evidence and the strength of recommendations"
[@guyatt-2008-grade, abstract]. It rates the quality of evidence on four
levels, from high ("Further research is very unlikely to change our
confidence in the estimate of effect") to very low ("Any estimate of effect
is very uncertain") [@guyatt-2008-grade, Box 2], and it lets observational
studies "start with a 'low quality' rating" that can be moved up or down
[@guyatt-2008-grade]. Two of its points bear directly on this taxonomy. It
keeps the quality of evidence apart from the strength of a recommendation:
"High quality evidence doesn't necessarily imply strong recommendations, and
strong recommendations can arise from low quality evidence"
[@guyatt-2008-grade]. And it warns that "Systems that classify 'expert
opinion' as a category of evidence also create confusion"
[@guyatt-2008-grade].

The taxonomy separates the two dimensions GRADE separates, but it does so
with coarser scales. Its RFC 2119 keywords (MUST, SHOULD) carry the strength
of a rule, and its evidence rating carries the support for it. That rating,
however, measures something different from GRADE's quality of evidence:
"strong" means that a standard, code, regulation or professional body
requires the practice, and "moderate" means widespread practice with
published guidance. It is a rating of institutional endorsement, not of
confidence in a measured effect. That is the author's characterization of
the taxonomy's own scale, and it is the main reason the paper calls the
taxonomy a synthesis rather than an evidence review.

Two reporting conventions from systematic reviews shaped the method.
PRISMA 2020 asks reviews to report the selection process "from the number
of records identified in the search to the number of studies included in the
review, ideally using a flow diagram", and to cite studies that "might
appear to meet the inclusion criteria, but which were excluded, and explain
why they were excluded" [@page-2021-prisma, items 16a--16b]. The
taxonomy borrows the second idea in a lighter form: domains that were
searched without producing a rule are listed with a reason, instead of being
left out. It does not follow PRISMA's search protocol, and it is not a
systematic review. The method's stopping rule borrows the idea of
saturation from qualitative research. Saunders and colleagues note that
saturation is "commonly taken to indicate that, on the basis of the data
that have been collected or analysed hitherto, further data collection
and/or analysis are unnecessary", and caution that it is "essentially a
predictive statement about the unobserved based on the observed"
[@saunders-2018-saturation]. That caution applies here as well (Section 6).

Finally, the taxonomy's split between primary and secondary sources follows
common academic practice. It keeps encyclopedia links only as secondary
sources, in line with Wikipedia's own guidance that "Wikipedia is not a
reliable source for academic writing or research"
[@wikipedia-academic-use].

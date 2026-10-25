# Methodology

This page describes a method for turning widely scattered practices into a
set of rules that can be checked. It applies to any field where good practice
is spread over many sources: standards, regulations, papers, handbooks and
practitioner writing. It was used to build this taxonomy of engineering and
management practices. Each phase below has its inputs, steps, outputs, exit
criteria and failure modes, and a box that shows how this taxonomy applied
it.

**What the boxes can and cannot say.** The boxes describe only what the
content of edition 1.0.0 shows (the rules, the glossary, the sections on
method and limits, the source tables). Where the content does not show how a
step was carried out, the box says so. Statements marked "author's judgment"
are the author's own assessment, not a sourced finding. The history of the
editions is in [history.md](history.md).

The phases run in order, but phases 3 to 6 can repeat. A later phase often
sends work back to an earlier one: a classification review (phase 5) may
reveal a gap that needs another coverage loop (phase 3).

## Cross-cutting principles

Four principles apply to every phase.

1. **Verbatim quotes.** Wherever a rule's rating depends on what a source
   says, the source's words are quoted exactly, with a locator, and checked
   against the page they came from. Paraphrase is never presented as a quote.
2. **Labeled judgments.** Where the author decides something that no source
   decides (a classification, a transfer of a rule to another domain, a
   resolution of a conflict), the text says so. Evidence strength is likewise
   "the author's assessment".
3. **Open limits.** What was not checked, could not be fetched, or rests on
   a weak source is written down in the same document as the rules, not kept
   in private notes.
4. **Format stability across editions.** Rule IDs, the sentence pattern, the
   column set and the vocabularies do not change between editions unless the
   version number says so (see "Versioning").

## Phase 0: Frame

Fix the frame before collecting anything, so that later findings can be
judged against it.

**Inputs:** the field and a reason for the work (who will use the result).

**Steps:**

1. Set the scope: which fields count, and which are out of scope.
2. Define the unit: one *practice*, meaning an action someone takes, as
   opposed to a principle or a goal.
3. Choose the sentence pattern every unit will use (for example
   IF / THEN / BECAUSE).
4. State a master rule hypothesis: the one idea that is expected to organize
   the rest (for example "scale rigor to consequence and uncertainty").
5. Define the source quality scale (what counts as primary and what as
   secondary) and the evidence scale (what separates strong from moderate
   from weak).

**Outputs:** a short frame document with the five items above.

**Exit criteria:** another person could take a candidate practice and decide,
using only the frame, whether it is in scope, which sentence it becomes, and
how its sources would be rated.

**Failure modes:**

- A unit that mixes practices and principles, so rules cannot be checked.
- A source scale defined after the sources were seen, which fits the scale
  to the sources.
- A master rule that is treated as a result instead of a hypothesis.

> **Applied in this taxonomy:** The content shows the frame in its first
> section and in the master rule. The unit is a practice with an action.
> Section 12 says the rules "are practices with actions", and it explains
> why they are therefore not principles in the INCOSE sense, since INCOSE
> says a principle must not be a how-to statement
> [@incose-se-principles]. The sentence pattern is IF / THEN / BECAUSE. The
> master rule is two lines: scale the rigor of every rule to consequence of
> failure times uncertainty, and keep reducing risk until the next reduction
> is grossly disproportionate to the benefit (ALARP). Source quality is
> defined as primary (a standard, regulation, regulator or professional-body
> document, original paper or report, or a word-for-word copy of one) or
> secondary (an encyclopedia, blog, vendor or trade page, aggregator or news
> article). Evidence strength has three values: strong, moderate and weak.
> The scope is "systems and the organizations that build them". The content
> does not show whether the frame was written before the first collection or
> adjusted afterwards.

## Phase 1: Collect

**Inputs:** the frame from phase 0.

**Steps:**

1. List the sub-fields of the scope (in this taxonomy: engineering
   branches and management domains).
2. Sweep each sub-field for widely cited practices, using standards,
   regulations, professional bodies and original papers first.
3. Split what you find into *universal* practices (the condition is true, or
   the trigger occurs, in every system in scope) and *field-specific*
   practices (the condition holds only in some systems).
4. Rewrite each practice as a conditional rule in the sentence pattern. The
   IF part states exactly when the rule applies.
5. Draft the organizing master rule from the practices found, and compare it
   with the hypothesis from phase 0.

**Outputs:** a list of conditional rules with their first sources, grouped by
sub-field, and a draft master rule.

**Exit criteria:** every sub-field of the scope has been swept at least once,
and every practice found is either a rule or has a recorded reason for being
left out.

**Failure modes:**

- Sweeping only the sub-fields the author knows.
- Copying a practice's wording without stating its IF condition, so that a
  field-specific practice looks universal.
- Treating the number of sources that repeat a practice as proof that it is
  correct.

> **Applied in this taxonomy:** The content shows the sub-fields in the
> domain index (section 4): eleven engineering groups, from civil to
> computing, plus a cross-cutting group, and eight management groups
> (governance and assurance; strategy and decisions; portfolio, programme
> and project; product and innovation; operations, quality and supply; risk,
> resilience and legal; people and organization; finance). Every rule has a
> source domain and a class: universal (U, 58 rules), risk-scaled (R, 9) or
> conditional (C, 16). The content also shows the rule that decides which
> management practices are included: they are included "when they change how
> a system is designed, checked, changed or operated, or how the people who
> build it are organized, selected, given feedback and led through change".
> The content does not show how many sweeps were made per sub-field or in
> which order.

## Phase 2: Standardize

**Inputs:** the rule list from phase 1.

**Steps:**

1. Apply the fixed sentence pattern to every rule. Use one name per rule for
   scanning.
2. Write a glossary. Give each term exactly one meaning, and list the terms
   people confuse with it (for example verification and validation).
3. Fix strength keywords. Use an existing convention rather than inventing
   one.
4. Give each rule a check (what an auditor looks at) and a violation (what
   breaking the rule looks like).
5. Define relations between rules with a closed vocabulary, and make
   inverse pairs explicit.
6. Rate evidence for each rule using the scale from phase 0.
7. Build a rigor matrix: a table that says which rules apply in which cell
   of the master rule's dimensions.
8. Keep a machine-readable twin of the human-readable document.

**Outputs:** a rule table with one row per rule and the same columns
throughout, a glossary, a relation vocabulary and a rigor matrix.

**Exit criteria:** two people applying the same rule to the same situation
reach the same verdict on "applies" and "violated" in most cases, and no term
appears with two meanings.

**Failure modes:**

- Synonyms: two words for one meaning, so a reader assumes two concepts.
- Relations that carry no decision, so the graph is decoration.
- A machine-readable twin that is edited by hand and drifts from the
  document (phase 4 addresses this).

> **Applied in this taxonomy:** The content shows each item.
> The pattern is IF / THEN / BECAUSE, and the table also carries a check, a
> violation, a software or infrastructure example and a source domain.
> Strength keywords follow the meanings of RFC 2119 [@rfc-2119]: MUST means
> required, and SHOULD means expected. The rule that not following a SHOULD
> needs a written reason is this taxonomy's own convention (the author's), not
> part of RFC 2119.
> The glossary (section 5) states that each term has exactly one meaning
> and no other word is used for it, and it has a third column for what a term
> is not the same as: for example verification versus validation, defect
> versus failure, redundancy versus diversity, and hold point versus witness
> point. Relations use five keywords: depends on, strengthens (inverse:
> strengthened by), conflicts with, checks (inverse: checked by) and scaled
> by. Evidence strength is "the author's assessment" (strong, moderate,
> weak), and the content notes that no rule is rated weak, only parts of
> rules. The rigor matrix (section 6) is a two-by-two of consequence and
> uncertainty with checker levels (peer or external). The machine-readable
> twin was a YAML file at the time of the import; the content does not show
> how it was kept in step with the document before phase 4.

## Phase 3: Saturate coverage

Collection is never complete after one pass. Phase 3 repeats search loops
until new loops stop producing new rules.

**Inputs:** the standardized rule set and the sub-field list.

**Steps:**

1. Pick the sub-fields that have no or few rules.
2. Search each one for practices not yet in the set.
3. Check the sub-field list against an outside exhaustive list (for example
   a published list of engineering branches or of management domains), so
   that gaps are found by comparison, not by the author's memory.
4. Give each finding exactly one decision:
   - **new:** a rule is added;
   - **change:** an existing rule is changed (its IF, its wording or its
     class);
   - **supports only:** the finding is a further source for an existing rule
     and changes nothing else.
5. Record null results with the reason: the domain was searched and nothing
   was found, a source could not be fetched, or the domain is out of scope.
   This follows the idea of flow reporting in systematic reviews, which
   records how many items were identified, screened and excluded and why
   [@page-2021-prisma]. The analogy is to the reporting of exclusions, not
   to the review protocol; this method does not claim to be a systematic
   review.
6. Start another loop. Stop when a loop produces only "supports only" and
   null results.

**Outputs:** more rules, a longer source list, and a record of what was
searched without result.

**Exit criteria (saturation):** a full loop over the uncovered sub-fields
yields no "new" and no "change" decision. The stopping rule is borrowed in
spirit from theoretical saturation in qualitative research, where data
collection stops when new data no longer adds to the categories
[@saunders-2018-saturation]. This is an analogy: the units here are rules
and not interview codes, and the stopping rule is checked against an outside
list, which qualitative research does not usually have. Whether the
analogy fits is the author's judgment.

**Failure modes:**

- Stopping saturation too early: one empty loop over the sub-fields the
  author likes best.
- Counting a null result because the search was shallow, not because the
  practice does not exist. Always record how deep the search went.
- Letting a "change" decision pass as "supports only" to reach the stop
  condition.
- Skipping the outside list, so unknown gaps stay unknown.

> **Applied in this taxonomy:** The content shows the null results as the
> section "Checked without a separate row" (in section 4). It lists domains
> that produced no sourced rule, each with a reason and the rules that apply
> anyway by cross-reference. Reasons in the content include "searched; no
> source found for a distinct principle", "the source ... could not be
> fetched; not included", "not researched separately", "umbrella terms that
> combine other branches" and "out of scope". The content states that the
> last column of that table "is the author's judgment, not a sourced
> finding". The "Limits" part of section 12 lists what was not fetched in
> full. The content does **not** show how many loops were run, which outside
> list was used for comparison, how many findings received each of the three
> decisions, or what the final loop produced. It also does not state that a
> saturation stop was reached. Those facts are not claimed here.

## Phase 4: Single source and automated checks

Before the set becomes large, make one copy of it the source of truth and
generate everything else from it.

**Inputs:** the standardized and saturated rule set, held in a structured
form.

**Steps:**

1. Choose one structured dataset as the only place where rules, sources,
   quotes and relations are edited.
2. Generate the human-readable documents, the site, the paper and any export
   from that dataset. Never edit a generated file.
3. Write automated checks for every invariant that a reader would otherwise
   have to trust.
4. Run the checks on every change, and fail the build if a generated file is
   out of date.

**Outputs:** a validated dataset, generated documents that match it, and a
check suite.

**Exit criteria:** the checks pass, and regenerating from the dataset
reproduces the published documents exactly.

**Failure modes:**

- Checking only what is easy to check (formatting) and not what matters
  (resolving references, relation inverses).
- Editing generated output "just this once".
- Importing a document into data and accepting every difference silently.
  A difference between the imported document and its regenerated form is a
  finding, and it goes to the maintainer.

> **Applied in this taxonomy (this repository):** In this repository, `data/`
> is the single source of truth and `publication/` is generated from it.
> `taxonomy check` validates the dataset and `taxonomy build --check` fails
> if a generated file is out of date. The checks are:
>
> - rule IDs are unique, every related rule exists, every rule appears in at
>   least one domain, every source is used and every rendered table has a
>   consistent shape;
> - relation inverses agree (strengthens and strengthened by; checks and
>   checked by);
> - every rule has at least one primary source unless it is listed in
>   `meta.known_exceptions` with a reason (today only C15);
> - every C-rule names a counterexample, and every K-rule names two or more
>   existing rules;
> - category membership matches each rule's category;
> - the quick-view question count is between 5 and 9;
> - every entry in `history.id_map` points at an existing ID;
> - every citation key in data or prose resolves to a defined source;
> - the generated files under `publication/` are up to date.
>
> The content of 1.0.0 shows the effect of such checks in its own
> statements (for example the single listed exception for C15) but does not
> show when the checks were introduced; the checks above are those of this
> repository.

## Phase 5: Critical classification review

Review how rules were sorted, not what they say.

**Inputs:** the rule set from phase 4.

**Steps:**

1. Adopt a published criterion for what should count as universal. Prefer
   one from a recognized body in the field.
2. Turn the criterion into a falsification question: a question whose
   answer "yes" shows that a rule does *not* meet the criterion.
3. Tell **applicability** apart from **adoption**. The question asks whether
   a rule can apply in a domain, not whether the domain already follows it.
   A domain that has not adopted a practice has an adoption gap, which is
   not a counterexample.
4. Sort every rule into classes (universal, risk-scaled, conditional). For
   each conditional rule, name a counterexample: a common class of systems
   where the condition can never hold.
5. Consolidate: merge rules that cannot be told apart by check or violation,
   and split rules that hold two different checks.
6. Keep the entry checklist at five to nine items. This size is a design
   choice that rests on the working-memory literature [@miller-1956-magical-number-seven]
   and later work that estimates the limit lower [@cowan-2001-magical-number-four];
   which figure applies to a given checklist is the author's judgment.
   For the case for short checklists in practice, see
   [@haynes-2009-surgical-checklist; @gawande-2009-checklist-manifesto].
7. Publish the map from old IDs to new IDs, so that references to the old
   IDs keep working.

**Outputs:** a classified rule set with counterexamples, a short checklist
and an old-to-new ID map.

**Exit criteria:** every rule has a class, every conditional rule has a
counterexample, and the checklist has five to nine items.

**Failure modes:**

- Taking an adoption gap for a counterexample, which turns universal rules
  into conditional ones.
- A criterion that cannot be falsified, so every rule passes.
- A counterexample that is a single odd system and not a common class.
- Changing IDs without a map.

> **Applied in this taxonomy:** The content shows the criterion in sections 1
> and 12. INCOSE requires a systems engineering principle to "Transcend life
> cycle", "Transcend system type" and "Transcend context"
> [@incose-se-principles]. SEBoK adds that the application of principles is
> specific to stakeholders and context [@sebok-se-principles]. The content
> turns this into a classification test: "Is there a common class of
> engineered systems in which this condition can never be true during the
> whole life cycle?" If no, the rule is universal (U), or risk-scaled (R) if
> only the strength of the need varies with risk. If yes, it is conditional
> (C). The content states that the test asks whether a rule can apply, not
> whether a domain already practices it: "A domain without the practice has
> an adoption gap; that is not a counterexample". Each C-rule names a
> counterexample, and C15 (late work and added people) shows the pattern: its
> counterexample is work that can be split into independent parts without
> communication, such as harvesting a field. The content states that the
> classification of each rule "is the author's judgment against the test in
> section 1" and that the counterexamples "are reasoned, not sourced". The
> nine quick-view questions (section 3), one per category, implement the
> five-to-nine checklist size, and the content cites Mann's notes on Gawande's book
> [@mann-checklist-manifesto-notes], not Gawande directly, for the limit of
> working memory. The
> content does not show a consolidation step, the number of rules before and
> after classification, or an old-to-new ID map.

## Phase 6: Source upgrade

Raise the quality of the evidence under the rules.

**Inputs:** the classified rule set and its source list.

**Steps:**

1. Classify every source as primary or secondary using the scale from
   phase 0.
2. For each rule that rests only on secondary sources, look for a primary
   source and swap it in. Keep the secondary source as a pointer if it is
   useful to readers.
3. Check every quote against the page it is linked to. Record the date of
   the check. If the linked page is a copy, name the original.
4. Record faithful copies: a primary text read through another site.
5. Record every changed rating, and the reason.
6. Record what could not be done: a paid text, a book that is not online, a
   page that could not be fetched. Rules that still rest on secondary
   sources go into a named exceptions list, with a reason.

**Outputs:** a source table with kind (primary or secondary) per source, a
quote table, a list of faithful copies and a list of exceptions.

**Exit criteria:** every rule has at least one primary source or is on the
exceptions list with a reason, every quote has been checked, and every
limit is written down.

**Failure modes:**

- A secondary source relabeled primary because it is well known.
- A quote taken from a summary and attributed to the original.
- Quietly raising an evidence rating after a source swap.
- Hiding paid or unavailable documents. Say that only an official summary
  was read.

> **Applied in this taxonomy:** The content shows this phase in sections 9,
> 11 and 12. Each rule lists its primary sources first. Section 11 states
> that quotes "were checked against the linked page on 2026-10-14" and that
> where the linked page is a copy, the original is named. Section 12 lists
> the faithful copies: NIST via CSF Tools, IMO SOLAS via imorules.com, The
> Joint Commission via KFF, the Rio Declaration via the World Bank ICSID
> archive, Hoare's lecture via worrydream.com, Edmondson via MIT, Staw and
> Sackett via gwern.net, Campbell via a 2011 journal reprint, § 239 HGB via
> dejure.org and Regulation (EU) No 537/2014 via charteredaccountants.ie. It
> states that every rule has at least one primary source except C15, whose
> primary source (Brooks's 1975 book) is not online. The limits include paid
> documents (ISO standards, PRINCE2, PMBOK), texts that could not be fetched
> in full, rules with a cross-reference-only transfer (R5, U30, U44, C13, U33
> and U37), and contested evidence (U55, contested by Deming; K8 resolves the
> conflict). The content explains why Wikipedia is kept only as a secondary
> link, quoting its own statement that it "is not a reliable source for
> academic writing or research" [@wikipedia-academic-use]. The content does
> not show which ratings changed during upgrade, nor how many secondary
> sources were swapped for primary ones.

## Conflicts between rules

Rules from different sources can pull in opposite directions. The method
handles this with a separate class of rule, not by silently ranking them.

A **conflict rule** (K) names the rules that conflict, states which one
wins under which condition, gives the reason, and gives an example. It
needs two or more existing rules. Its basis column says whether a source
decides the conflict or whether the resolution is the author's synthesis.

> **Applied in this taxonomy:** The content has eight conflict rules (K1 to
> K8). Examples: K3 resolves the tension between tolerating variation (U30)
> and rejecting bad input (C5) by placing the boundary at the specification.
> K5 scales review depth by reversibility and consequence. K7 separates
> honest errors (handled without blame) from deliberate violations (handled
> by a fair disciplinary procedure). K1 has the Basis "sourced (see U7, U25, R1)".
> K2, K4 and K7 read "author's synthesis; no single source", and K3, K5, K6
> and K8 read "author's synthesis from" named sources. The content states
> that K1 to K8 are the author's synthesis unless their Basis column names a
> source, so the author's judgment is visible in the table.

## Versioning

From now on the taxonomy is versioned with Semantic Versioning, and the
version number is the release tag.

| Change | Version part |
|---|---|
| A rule is removed, or an ID changes | major |
| A rule is added, or the meaning of a rule changes | minor |
| Wording or source fixes that do not change a rule's meaning | patch |
| A field, column, vocabulary value, relation type or strength keyword is removed or renamed | major |
| A field, column, vocabulary value, relation type or strength keyword is added | minor |
| Rewording without a change of meaning | patch |

The data-format rows follow the compatibility rule of Semantic Versioning
[@semver-2-0-0]: a change that breaks existing users of the format is major,
and a backward-compatible addition is minor. Mapping "existing users" onto
readers and tools of the dataset is the author's judgment.

Every edition adds a section to [history.md](history.md) and an entry to
`data/history.yaml`, including the old-to-new ID map when a major change
moves IDs. Edition 1.0.0 is the first edition.

## Running a round

A future round (a coverage loop, a source upgrade or a review) is run with
the `taxonomy-research` skill, which is not yet written. Until it exists,
follow the phases above by hand, record every finding with one of the three
decisions of phase 3, and finish with the version bump from "Versioning".
The checks of phase 4 must pass before a round counts as done.

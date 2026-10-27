# Engineering Best Practices — Cross-Domain Taxonomy

Version 1.1.1 · 2026-10-27 · 83 rules (58 universal, 9 risk-scaled, 16 conditional) and 8 conflict rules in 9 categories

## Contents

1. How to read the rules
2. Master rule
3. Taxonomy overview
4. Domain index (engineering and management domains, their rules and references)
5. Glossary
6. Rigor matrix
7. Rules by category (A–I)
8. Conflict rules
9. Sources by rule
10. Management form of each rule
11. Direct quotes
12. Method and limits

## 1. How to read the rules

- **Sentence structure:** every rule reads as **IF** \[condition\], **THEN** \[action\], **BECAUSE** \[reason\].
- **Rule classes.** The IF field does a different job in each class:
  - **U = universal.** The condition is true, or the trigger occurs, in every engineered system. IF is either "always" or a trigger such as "a failure has happened". Every system applies these rules; the master rule scales how strictly.
  - **R = risk-scaled.** The rule applies only above a consequence or uncertainty threshold. The rigor matrix (section 6) says where.
  - **C = conditional.** The rule applies only when the system has a property that a common class of systems lacks. IF names that property. Each conditional rule names a counterexample system.
  - **K = conflict rule.** It decides between rules that pull in opposite directions.
- **Classification test:** "Is there a common class of engineered systems in which this condition can never be true during the whole life cycle?" No → U (or R, if only the strength of the need varies with risk). Yes → C.
- **Applicability, not adoption:** the test asks whether a rule *can* apply, not whether a domain already practices it. A domain without the practice has an adoption gap; that is not a counterexample. Rules therefore apply across domains by cross-reference, even where no source from that domain exists.
- **IDs:** each rule has a stable, opaque ID (P1–P83, numbered in category order) that carries no meaning. Its class (U, R or C) and its category are shown next to it. A new rule gets the next free number. Conflict rules are K1–K8.
- **Strength keywords** follow RFC 2119:
  - **MUST** = required. Not following it is a violation. A MUST rule applies whenever its IF-condition is true, in every cell of the rigor matrix.
  - **SHOULD** = expected. Not following it requires a written reason.
- **Relation keywords** in the RELATED column:
  - **depends on** = this rule needs the other rule to work.
  - **strengthens** = this rule makes the other rule more effective. **strengthened by** is the inverse.
  - **conflicts with** = following both rules fully pulls in opposite directions. Section 8 resolves conflicts.
  - **checks** = this rule provides the check for the other rule. **checked by** is the inverse.
  - **scaled by** = the other rule sets how strictly this rule is applied.
- **Source quality:** a **primary** source is a standard, a regulation, a document of a regulator or professional body, an original paper or report, or a word-for-word copy of one. A **secondary** source is an encyclopedia, a blog, a vendor or trade page, a topic aggregator or a news article. Each rule lists its primary sources first. The Evidence column marks rules that still rest on "secondary only" sources. Wikipedia itself says it "is not a reliable source for academic writing or research", so it is kept only as a secondary link.
- **Evidence strength** is the author's assessment:
  - **strong** = required by a standard, code, regulation or professional body.
  - **moderate** = widespread practice with published guidance.
  - **weak** = mostly anecdotal. No rule is rated weak; only parts of rules are (see notes).
- **Source domain** names the engineering field, or the management domain, where the rule was found. The software/infra example shows the same rule in platform engineering. Section 4 lists every domain with its rules and references.
- **Rule names** are short labels for scanning. The IF / THEN / BECAUSE text is the rule itself.
- **Scope: systems and the organizations that build them.** Every engineered system is designed, built and operated by an organization. Rules whose source domain is "management" govern that organization (decisions, delegation, people, change). Section 10 states 67 of the 83 rules in management form, for teams, projects and organizations; the other 16 (P5–P8, P18–P21, P35, P43, P52, P53, P62, P63, P69, P79) come from management sources.

## 2. Master rule

1. Scale the rigor of every rule to (consequence of failure) × (uncertainty).
2. Keep reducing risk until the cost of the next reduction is grossly disproportionate to the benefit (ALARP).

| Risk region | Required action |
| --- | --- |
| unacceptable | risk must be reduced, whatever the cost |
| tolerable | reduce risk while it is reasonably practicable (ALARP) |
| negligible | no further reduction is required |

In management, the same idea has three established names:

| Engineering term | Management term | Source |
| --- | --- | --- |
| scale the rigor | **tailoring**: adapt the method to the size, risk and context of the work | PRINCE2 principle 7 "Tailor to suit the project"; PMBOK Guide 8th edition "Tailor for your context" |
| boundary between the unacceptable and the tolerable region | **risk appetite**: the amount and type of risk the governing body accepts in pursuit of its objectives | COSO ERM 2017, principle 7 "Defines Risk Appetite" |
| consequence | impact on people, money, legal position, reputation and objectives; **irreversibility** raises the consequence | ISO 31000:2018; Amazon 2015 shareholder letter (one-way doors) |

## 3. Taxonomy overview

The categories follow the lifecycle of an engineered system: who is responsible (A), what is known and decided (B), how it is designed (C–E), how it is checked (F), changed (G) and operated (H), and how the organization learns (I).

### Quick view: nine questions

A checklist works best with five to nine items, so the taxonomy can be used as one question per category. Each question leads to the rules of its category.

| Category | Question |
| --- | --- |
| A. Responsibility | Who can be harmed, is the work within our competence, can people speak up without fear or a conflict of interest, and who can stop it? |
| B. Knowledge and decisions | Are requirements and goals measurable, decisions recorded and sized by reversibility, stop criteria set in advance, and models, data, evidence and indicators trustworthy? |
| C. Design | How can each part fail or interact badly, and is the design as simple as the requirements allow? |
| D. Protection | Is the hazard removed at the source, and if not, which independent controls contain it, and can one person cause and hide harm alone? |
| E. Capacity and continuity | How much margin is there, how much work is in progress, and what happens when the load exceeds the capacity? |
| F. Verification and review | Who checked the work, and was it tested the way it will be operated? |
| G. Change | Is each change reviewed, explained to the people affected, made in small steps, and isolated from the people working on it? |
| H. Operation and maintenance | Will we notice a problem before harm, and can people act on what they see? |
| I. Learning | Do we preserve evidence, investigate anomalies, and change the system afterwards? |

### Analogy map: engineering object → management object

The left column is the engineering term used in this taxonomy. The right column is the thing that plays the same role in an organization.

| Engineering | Management | Same role |
| --- | --- | --- |
| system | organization, team, project, process | the thing that must deliver a function |
| load | demand, workload, number of requests | what the system must carry |
| margin | reserve: schedule buffer, budget contingency, spare capacity of people | capacity above the expected load |
| redundancy (N-1) | deputy, successor, second supplier | survives the loss of one element |
| fail-safe state | default decision, fallback authority | the harmless state after a failure |
| emergency stop (andon) | speak-up channel, stop-the-line right | the person nearest to a problem can stop work |
| checker | reviewer, internal audit, external auditor | a person other than the author checks the work |
| alert | exception report to the next management level | a signal that needs action now |
| alarm fatigue | report overload | too many signals → all signals are ignored |
| commissioning | acceptance plus benefits review | checks that the whole works for the owner |
| postmortem | after-action review | learning after an event |
| isolation (lockout/tagout) | protected iteration (for example the Sprint Goal) | nobody changes the work while people work on it |
| control loop oscillation | reorganization churn, priority churn | switching back and forth around a target |
| bottleneck | constraint (theory of constraints) | the part that limits total output |
| bullwhip effect | bullwhip effect (same term) | each stage amplifies the variation it sees |
| provenance | supplier due diligence | knowing where a part comes from |
| compartment | ring-fenced unit: separate legal entity, budget or team | a failure that cannot spread |
| exact constraint (one owner per property) | single point of accountability, unity of command | each property or decision has exactly one owner |

### Rules per category

- **A. Responsibility** — Duties toward people, the environment and the work itself.
  - P1 Public safety first (MUST)
  - P2 Work within competence (MUST)
  - P3 Sustainability (SHOULD)
  - P4 Stop authority (SHOULD)
  - P5 Psychological safety (SHOULD)
  - P6 Conflict-of-interest disclosure (MUST)
  - P7 Commander's intent (SHOULD)
  - P8 Fair process (SHOULD)
- **B. Knowledge and decisions** — How requirements, decisions, models and evidence are recorded and trusted.
  - P9 Measurable requirements (MUST)
  - P10 Decision records (SHOULD)
  - P11 Trustworthy evidence (SHOULD)
  - P12 Model validity (SHOULD)
  - P13 Automated reproducible results (SHOULD)
  - P14 Provenance (SHOULD)
  - P15 Precaution (SHOULD)
  - P16 Set-based design (SHOULD)
  - P17 Technology maturity (SHOULD)
  - P18 Decision speed by reversibility (SHOULD)
  - P19 Indicators are not targets (SHOULD)
  - P20 Stop criteria set in advance (SHOULD)
  - P21 Specific, challenging goals with feedback (SHOULD)
- **C. Design** — How to shape a design before it is built, so that it fails less.
  - P22 Failure and interaction analysis (SHOULD)
  - P23 Simplicity and modularity (SHOULD)
  - P24 Lifecycle and decommissioning (SHOULD)
  - P25 Human factors (SHOULD)
  - P26 Design for testability (SHOULD)
  - P27 Robustness (SHOULD)
  - P28 Accumulated degradation (SHOULD)
  - P29 Compatibility (SHOULD)
  - P30 Exact constraint (SHOULD)
  - P31 Design by selection (SHOULD)
  - P32 End-to-end (SHOULD)
  - P33 Strict interfaces (SHOULD)
  - P34 Weakest-link scaling (SHOULD)
  - P35 Structure follows the intended system (SHOULD)
- **D. Protection** — Controls that prevent harm, or contain it when it happens.
  - P36 Least privilege (MUST)
  - P37 Fail-safe (MUST)
  - P38 Hierarchy of controls (SHOULD)
  - P39 Error-proofing (SHOULD)
  - P40 Defense in depth (SHOULD)
  - P41 Compartments (SHOULD)
  - P42 Two-person rule (SHOULD)
  - P43 Segregation of duties (MUST)
- **E. Capacity and continuity** — How the system keeps working under high load and partial failure.
  - P44 Margin (SHOULD)
  - P45 Redundancy (N-1) (SHOULD)
  - P46 Diversity (SHOULD)
  - P47 Graceful degradation (SHOULD)
  - P48 Damping (SHOULD)
  - P49 Induced demand (SHOULD)
  - P50 Bottleneck first (SHOULD)
  - P51 Shared demand signal (SHOULD)
  - P52 Limit work in progress (SHOULD)
  - P53 Late work and added people (SHOULD)
- **F. Verification and review** — How to prove that the work is correct.
  - P54 Verification and validation (MUST)
  - P55 Find defects early (SHOULD)
  - P56 Independent checker (MUST)
  - P57 Test as you operate (SHOULD)
  - P58 Comparable measurement (SHOULD)
  - P59 Traceability (MUST)
  - P60 Codes as minimum (MUST)
  - P61 Qualified procedure and person (SHOULD)
  - P62 Structured selection of people (SHOULD)
  - P63 Feedback on the task (SHOULD)
- **G. Change** — How to change the system safely.
  - P64 Versioning and change review (MUST)
  - P65 Small verified steps (SHOULD)
  - P66 Isolation before work (MUST)
  - P67 Critical path (SHOULD)
  - P68 Observational method (SHOULD)
  - P69 Guided change (SHOULD)
- **H. Operation and maintenance** — How to run, watch and maintain the system.
  - P70 Monitoring in operation (SHOULD)
  - P71 Checklists (SHOULD)
  - P72 Critical control points (SHOULD)
  - P73 Response faster than harm (SHOULD)
  - P74 Maintenance by failure pattern (SHOULD)
  - P75 Actionable alerts (SHOULD)
  - P76 Sterile critical phase (SHOULD)
  - P77 Data as a dependency (SHOULD)
  - P78 Asset inventory (SHOULD)
  - P79 Span of control (SHOULD)
- **I. Learning** — How to learn from failures and anomalies.
  - P80 Blameless root cause analysis (SHOULD)
  - P81 Plan-Do-Check-Act (SHOULD)
  - P82 Investigate anomalies (SHOULD)
  - P83 Preserve evidence (SHOULD)
- **K. Conflict rules** — K1, K2, K3, K4, K5, K6, K7, K8

## 4. Domain index

Each row names an engineering domain, the rules **found** in it, and the references that support those rules. A rule can appear under several domains. "Supports" in the rule list means the domain confirms an existing rule but added nothing new.

**Found is not the same as applicable.** All universal rules apply to every domain in this index, the risk-scaled rules apply wherever the rigor matrix requires them, and the conditional rules apply wherever their condition is true. That holds even where the domain has no published practice yet (adoption gap).

130 domains in 20 branches (12 engineering branches, 8 management branches).

### Civil

| Domain | Rules | References |
| --- | --- | --- |
| Structural and building | P56 Independent checker | [EPCLand: Checking of design](https://epcland.com/checking-of-design-engineering-checklist/) |
| Geotechnical | P68 Observational method | [ICE: The observational method](https://knowledgehub.ice.org.uk/cpd/delivery-exc/observational-method/) |
| Coastal and hydraulic | P44 Margin | [Wikipedia: Return period](https://en.wikipedia.org/wiki/Return_period) |
| Offshore and decommissioning | P24 Lifecycle and decommissioning; P10 Decision records | [JPT: Engineering for decommissioning](https://jpt.spe.org/engineering-decommissioning-during-project-design-reduces-costs) [SPE: Design for decommissioning (basis of design)](https://onepetro.org/spe/general-information/1423/Design-for-decommissioning) |
| Construction management | P67 Critical path; P65 Small verified steps | [Wikipedia: Critical path method](https://en.wikipedia.org/wiki/Critical_path_method) [Quality Engineers Guide: Hold point and witness point](https://www.qualityengineersguide.com/what-is-witness-point-and-hold-point) |
| Transportation | P49 Induced demand; P39 Error-proofing | [Wikipedia: Induced demand](https://en.wikipedia.org/wiki/Induced_demand) [FHWA: Zero deaths and the Safe System approach](https://highways.dot.gov/safety/zero-deaths) |
| Environmental and water | P15 Precaution; P40 Defense in depth (supports) | [Wikipedia: Precautionary principle](https://en.wikipedia.org/wiki/Precautionary_principle) [Wikipedia: Multi-barrier approach](https://en.wikipedia.org/wiki/Multi-barrier_approach) |
| Railway operations | P71 Checklists | [Wikipedia: Pointing and calling](https://en.wikipedia.org/wiki/Pointing_and_calling) |
| Building services | P54 Verification and validation | [Wikipedia: Building commissioning](https://en.wikipedia.org/wiki/Building_commissioning) |
| Municipal and infrastructure asset management | P78 Asset inventory | [Wikipedia: Asset management (incl. ISO 55000)](https://en.wikipedia.org/wiki/Asset_management) |
| Geological | P68 Observational method (supports) | [Wikipedia: Geological engineering](https://en.wikipedia.org/wiki/Geological_engineering) |

### Mechanical

| Domain | Rules | References |
| --- | --- | --- |
| Machine and pressure vessel design | P44 Margin; P60 Codes as minimum | [Univ. of Portland: Fail-safe designs and factor of safety](https://faculty.up.edu/lulay/MEStudentPage/failsafe.pdf) |
| Technical drawing | P56 Independent checker | [LibreTexts: Peer review in design](https://eng.libretexts.org/Courses/Western_Technical_College/Inventor_Parametric_Design:_Level_1_%28Bahl%29/01:_Technical_Drawings/1.02:_Peer_Review_Process_and_Markup_Drawings/1.2.01:_The_Role_of_Peer_Review_in_Engineering_Design) |
| Aerospace design | P23 Simplicity and modularity; P24 Lifecycle and decommissioning; P45 Redundancy (N-1); P17 Technology maturity | [Grokipedia: KISS principle](https://grokipedia.com/page/KISS_principle) [NASA: Design for maintenance](https://ntrs.nasa.gov/api/citations/20240004739/downloads/Design%20for%20Maintenance%20DoD%20HFE%20TAG%2076%20041724.pdf) [ScienceDirect: Fail-safe design](https://www.sciencedirect.com/topics/materials-science/fail-safe-design) [Wikipedia: Technology readiness level](https://en.wikipedia.org/wiki/Technology_readiness_level) |
| Aerospace testing | P57 Test as you operate; P65 Small verified steps; P82 Investigate anomalies | [Aerospace Corp: Test Like You Fly Process Guide](https://aerospace.org/sites/default/files/2024-06/TOR-2014-02537-REV%20A%20-%20The%20Test%20Like%20You%20Fly%20Process%20Guide%20for%20Space,%20Launch,%20and%20Ground%20Systems.pdf) [Flight Test Fact: The build-up approach](https://flighttestfact.com/the-build-up-approach/) [Wikipedia: Normalization of deviance](https://en.wikipedia.org/wiki/Normalization_of_deviance) |
| Aviation operations and maintenance | P37 Fail-safe; P74 Maintenance by failure pattern; P76 Sterile critical phase | [PatSnap: Fail-safe design](https://eureka.patsnap.com/article/what-is-a-fail-safe-design-principles-and-best-practices) [Wikipedia: Reliability-centered maintenance](https://en.wikipedia.org/wiki/Reliability-centered_maintenance) [Wikipedia: Sterile flight deck rule](https://en.wikipedia.org/wiki/Sterile_flight_deck_rule) |
| Automotive | P46 Diversity; P59 Traceability; P22 Failure and interaction analysis | [arXiv: Safety design in autonomous vehicles](https://arxiv.org/pdf/2412.08862) [Stell: Requirements traceability](https://stell-engineering.com/blog/what-is-requirement-traceability) [Swift Navigation: What is SOTIF (ISO 21448)?](https://www.swiftnav.com/glossary/what-is-safety-of-the-intended-functionality-sotif) |
| Naval architecture | P41 Compartments | [Wikipedia: Compartment (ship)](https://en.wikipedia.org/wiki/Compartment_%28ship%29) |
| Elevators | P37 Fail-safe | [PatSnap: Fail-safe design](https://eureka.patsnap.com/article/what-is-a-fail-safe-design-principles-and-best-practices) |
| Control engineering and machinery | P48 Damping; P4 Stop authority | [Wikipedia: Deadband](https://en.wikipedia.org/wiki/Deadband) [ISO 13850:2015 Emergency stop function (sample)](https://cdn.standards.iteh.ai/samples/59970/06ad76004ab746ff90b82cf44a8b0752/ISO-13850-2015.pdf) |
| Acoustic | P38 Hierarchy of controls; P27 Robustness (supports) | [OSHA Technical Manual: Noise](https://www.osha.gov/otm/section-3-health-hazards/chapter-5) [Wikipedia: Mechanical resonance](https://en.wikipedia.org/wiki/Mechanical_resonance) |
| Space systems | P44 Margin; P33 Strict interfaces | [NASA GSFC-STD-1000 Rev H (resource margins)](https://standards.nasa.gov/sites/default/files/standards/GSFC/H/0/GSFC-STD-1000RevH_Approved.pdf) [Wikipedia: Mars Climate Orbiter](https://en.wikipedia.org/wiki/Mars_Climate_Orbiter) |
| Optomechanical and precision engineering | P30 Exact constraint | [Wikipedia: Kinematic coupling (exact constraint)](https://en.wikipedia.org/wiki/Kinematic_coupling) |
| Energy engineering | P3 Sustainability (supports); P49 Induced demand (supports) | [ENEFIRST: What is Energy Efficiency First?](https://enefirst.eu/definitions/) |

### Materials

| Domain | Rules | References |
| --- | --- | --- |
| Fatigue and corrosion | P28 Accumulated degradation; P29 Compatibility | [Wikipedia: Fatigue (material)](https://en.wikipedia.org/wiki/Fatigue_%28material%29) [Wermac: Corrosion allowance](https://www.wermac.org/materials/corrosion_allowance.html) [Wikipedia: Galvanic corrosion](https://en.wikipedia.org/wiki/Galvanic_corrosion) |
| Forensic engineering | P83 Preserve evidence | [PHMSA: Metallurgical Laboratory Failure Examination Protocol](https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/docs/incident-reporting/accident-investigation-division/70066/metallurgical-laboratory-failure-examination-protocol.pdf) [Wikipedia: Forensic engineering](https://en.wikipedia.org/wiki/Forensic_engineering) |
| Welding | P61 Qualified procedure and person | [Wikipedia: Welding Procedure Specification](https://en.wikipedia.org/wiki/Welding_Procedure_Specification) |
| Ceramics and brittle materials | P34 Weakest-link scaling | [Wikipedia: Weibull modulus](https://en.wikipedia.org/wiki/Weibull_modulus) [Wikipedia: Size effect on structural strength](https://en.wikipedia.org/wiki/Size_effect_on_structural_strength) |
| Metallurgical | P14 Provenance | [Wikipedia: Mill test report](https://en.wikipedia.org/wiki/Mill_test_report) |
| Electronic materials | P28 Accumulated degradation (supports) | [Wikipedia: Electromigration](https://en.wikipedia.org/wiki/Electromigration) |
| Polymers | P28 Accumulated degradation (supports) | [Wikipedia: Creep (deformation)](https://en.wikipedia.org/wiki/Creep_%28deformation%29) |
| Nanotechnology | P15 Precaution (supports) | [Wikipedia: Regulation of nanotechnology](https://en.wikipedia.org/wiki/Regulation_of_nanotechnology) |

### Electrical

| Domain | Rules | References |
| --- | --- | --- |
| Electronics | P45 Redundancy (N-1); P44 Margin (supports) | [USPTO: Materials-based failure analysis in electronic devices](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8285522) [Wikipedia: Derating](https://en.wikipedia.org/wiki/Derating) |
| Power grids | P45 Redundancy (N-1); P47 Graceful degradation | [SINTEF: N-1 isn't always enough](https://blog.sintef.com/sintefenergy/energy-systems/electricity-supply-security-n-1-isnt-always-enough/) [Wikipedia: Load shedding](https://en.wikipedia.org/wiki/Load_shedding) |
| Telecom and network | P32 End-to-end; P33 Strict interfaces | [Wikipedia: End-to-end principle](https://en.wikipedia.org/wiki/End-to-end_principle) [Wikipedia: Robustness principle (incl. RFC 9413 critique)](https://en.wikipedia.org/wiki/Robustness_principle) |
| Computer engineering | P26 Design for testability; P50 Bottleneck first (supports) | [Wikipedia: Design for testing](https://en.wikipedia.org/wiki/Design_for_testing) [Wikipedia: Amdahl's law](https://en.wikipedia.org/wiki/Amdahl%27s_law) |
| Broadcast | P70 Monitoring in operation | [TV Technology: Confidence monitors](https://www.tvtechnology.com/opinions/confidence-monitors) |
| Microwave | P33 Strict interfaces (supports) | [Wikipedia: Impedance matching](https://en.wikipedia.org/wiki/Impedance_matching) |
| Optical (laser safety) | Master rule (supports) | [Wikipedia: Laser safety](https://en.wikipedia.org/wiki/Laser_safety) |

### Chemical

| Domain | Rules | References |
| --- | --- | --- |
| Chemical process safety | P64 Versioning and change review; P38 Hierarchy of controls | [OSHA 29 CFR 1910.119 (management of change)](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.119) [Wikipedia: Inherent safety](https://en.wikipedia.org/wiki/Inherent_safety) |
| Oil and gas | P40 Defense in depth | [JPT: Robust well barrier and well integrity management](https://jpt.spe.org/robust-well-barrier-and-well-integrity-management) |
| Food safety | P72 Critical control points | [FDA: HACCP Principles & Application Guidelines](https://www.fda.gov/food/hazard-analysis-critical-control-point-haccp/haccp-principles-application-guidelines) |
| Pharma and clinical trials | P11 Trustworthy evidence | [FDA: Electronic Source Data guidance (ALCOA)](https://www.fda.gov/media/85183/download) |
| Textile | P58 Comparable measurement | [ISO 139:2005 Textiles - standard atmospheres (sample)](https://cdn.standards.iteh.ai/samples/35179/19d75d1dcdd147d4b630728954acc86d/ISO-139-2005.pdf) [Chiuvention: Why fabric test results vary with weather](https://chiuvention.com/blog/why-fabric-test-results-vary-with-weather-solved-by-a-temperature-and-humidity-chamber) |
| Electrochemical (batteries) | P41 Compartments (supports) | [NASA: Can cell-to-cell thermal runaway propagation be prevented?](https://ntrs.nasa.gov/archive/nasa/casi.ntrs.nasa.gov/20140012758.pdf) |
| Molecular and biomolecular engineering | P31 Design by selection; P81 Plan-Do-Check-Act (supports) | [Wikipedia: Directed evolution](https://en.wikipedia.org/wiki/Directed_evolution) [Molecular Devices: Design-build-test-learn cycle](https://www.moleculardevices.com/applications/synthetic-biology/dbtl-approach) |

### Nuclear

| Domain | Rules | References |
| --- | --- | --- |
| Nuclear | P24 Lifecycle and decommissioning; P37 Fail-safe; P42 Two-person rule | [IAEA: Decommissioning by design](https://www.iaea.org/bulletin/decommissioning-by-design-how-advanced-reactors-are-designed-with-disposal-in-mind) [PatSnap: Fail-safe design](https://eureka.patsnap.com/article/what-is-a-fail-safe-design-principles-and-best-practices) [Wikipedia: Two-man rule](https://en.wikipedia.org/wiki/Two-man_rule) |

### Mining

| Domain | Rules | References |
| --- | --- | --- |
| Mining | P72 Critical control points | [Mining Weekly: ICMM critical control management guide](https://www.miningweekly.com/article/icmm-updates-critical-control-management-guide-to-strengthen-mining-safety-2026-04-29) |

### Biomedical

| Domain | Rules | References |
| --- | --- | --- |
| Medical devices and human factors | P25 Human factors; P59 Traceability | [MD+DI: Human factors engineering](https://www.mddionline.com/design-engineering/making-the-most-of-human-factors-usability-engineering) [egtechnology: Usability example](https://www.egtechnology.co.uk/human-factors-and-usability-engineering-a-must-or-a-good-to-have-part-1/) [Stell: Requirements traceability](https://stell-engineering.com/blog/what-is-requirement-traceability) |
| Surgery | P71 Checklists | [ScienceDaily: WHO surgical checklist study (2009)](https://www.sciencedaily.com/releases/2009/01/090114172304.htm) [ICES: Ontario checklist study (2014)](https://www.ices.on.ca/news-releases/study-shows-introduction-of-surgical-safety-checklists-in-ontario-have-not-reduced-post-operative-mortality-or-complications/) |
| Clinical engineering | P75 Actionable alerts | [Wikipedia: Alarm fatigue](https://en.wikipedia.org/wiki/Alarm_fatigue) |
| Bioinformatics | P13 Automated reproducible results | [Sandve et al.: Ten Simple Rules for Reproducible Computational Research](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003285) |
| Biomaterials | P29 Compatibility | [Wikipedia: Biocompatibility](https://en.wikipedia.org/wiki/Biocompatibility) |
| Biomechanics | P25 Human factors | [Wikipedia: Anthropometry](https://en.wikipedia.org/wiki/Anthropometry) |
| Medical imaging (radiation protection) | Master rule (supports) | [Wikipedia: ALARP / ALARA](https://en.wikipedia.org/wiki/ALARP) |
| Neural engineering | P72 Critical control points (supports) | [Wikipedia: Shannon criteria](https://en.wikipedia.org/wiki/Shannon_criteria) |

### Agricultural

| Domain | Rules | References |
| --- | --- | --- |
| Agricultural and biosystems | P27 Robustness (supports) | [PMC: Engineering approach for sustainable biological systems](https://pmc.ncbi.nlm.nih.gov/articles/PMC2610168/) |

### Industrial

| Domain | Rules | References |
| --- | --- | --- |
| Manufacturing | P4 Stop authority; P39 Error-proofing | [Wikipedia: Andon (manufacturing)](https://en.wikipedia.org/wiki/Andon_%28manufacturing%29) [UserSolutions: Poka-yoke](https://usersolutions.com/blog/poka-yoke-error-proofing) |
| Quality engineering | P81 Plan-Do-Check-Act; P27 Robustness | [ISO Central: PDCA](https://isocentral.org/resources/what-is-plan-do-check-act) [Penn State: Taguchi's Robust Design Method](https://www.me.psu.edu/simpson/courses/ie466/ie466.robust.handout.pdf) |
| Occupational and industrial safety | P38 Hierarchy of controls; P66 Isolation before work | [CDC/NIOSH: Hierarchy of controls](https://www.cdc.gov/niosh/hierarchy-of-controls/about/index.html) [OSHA: Control of hazardous energy (lockout/tagout)](https://www.osha.gov/control-hazardous-energy) |
| Fire protection | P73 Response faster than harm | [Fire Risk Assessment Network: ASET and RSET](https://fire-risk-assessment-network.com/blog/aset-rset/) |
| Industrial engineering and operations research | P50 Bottleneck first; P44 Margin | [Wikipedia: Theory of constraints](https://en.wikipedia.org/wiki/Theory_of_constraints) [Linda Green: Queueing theory and modeling](https://business.columbia.edu/sites/default/files-efs/pubfiles/5474/queueing%20theory%20and%20modeling.pdf) |
| Supply chain engineering | P51 Shared demand signal | [Wikipedia: Bullwhip effect](https://en.wikipedia.org/wiki/Bullwhip_effect) [Lee, Padmanabhan, Whang: Information Distortion in a Supply Chain (Management Science 1997)](https://courses.ie.bilkent.edu.tr/ie102/wp-content/uploads/sites/12/2019/02/Lee-Padmanabhan-Whang-1997-MS.pdf) |

### Computing

| Domain | Rules | References |
| --- | --- | --- |
| Software engineering | P55 Find defects early; P23 Simplicity and modularity; P10 Decision records | [arXiv: Revisiting cost-to-fix](https://arxiv.org/pdf/1609.04886) [Grokipedia: KISS principle](https://grokipedia.com/page/KISS_principle) [adr.github.io: Architectural Decision Records](https://adr.github.io/) |
| Security engineering | P36 Least privilege; P40 Defense in depth | [Jamf: NIST definition of least privilege](https://www.jamf.com/blog/zero-trust-vs-least-privilege/) [ScienceDirect: Least privilege and defense in depth](https://www.sciencedirect.com/topics/computer-science/principle-of-least-privilege) [Palo Alto Networks: Defense in depth](https://www.paloaltonetworks.com/cyberpedia/what-is-defense-in-depth) |
| Site reliability engineering | P80 Blameless root cause analysis; P70 Monitoring in operation | [Google SRE: Postmortem culture](https://sre.google/workbook/postmortem-culture/) [Google SRE: Monitoring distributed systems](https://sre.google/sre-book/monitoring-distributed-systems/) |
| Simulation and computational engineering | P12 Model validity | [Wikipedia: V&V of computer simulation models](https://en.wikipedia.org/wiki/Verification_and_validation_of_computer_simulation_models) |
| Data and ML engineering | P77 Data as a dependency | [Sculley et al.: Hidden Technical Debt in ML Systems (NeurIPS 2015)](https://proceedings.neurips.cc/paper_files/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf) [Wikipedia: Concept drift](https://en.wikipedia.org/wiki/Concept_drift) |
| Quantum engineering and computing theory | P45 Redundancy (N-1) | [Wikipedia: Quantum error correction](https://en.wikipedia.org/wiki/Quantum_error_correction) [von Neumann: Lectures on Probabilistic Logics and the Synthesis of Reliable Organisms from Unreliable Components (Caltech, 1952)](https://static.ias.edu/pitp/archive/2012files/Probabilistic_Logics.pdf) |

### Cross-cutting

| Domain | Rules | References |
| --- | --- | --- |
| Professional ethics | P1 Public safety first; P2 Work within competence; P3 Sustainability; P6 Conflict-of-interest disclosure | [NSPE Ethics Reference Guide](https://www.nspe.org/sites/default/files/resources/pdfs/Ethics/EthicsReferenceGuide.pdf) [NSPE: Sustainability and the PE's obligations](https://www.nspe.org/career-growth/pe-magazine/winter-2023/sustainability-the-pe-s-obligations) |
| Systems engineering | P9 Measurable requirements; P54 Verification and validation; P59 Traceability | [FDOT Systems Engineering 100](https://wbt.dot.state.fl.us/ois/ITS-SystemsEngineering100/SystemsEngineeringPt2-m2-TRANSCRIPT.pdf) [arXiv: V&V in Systems of Systems](https://arxiv.org/pdf/1311.3626) [Stell: Requirements traceability](https://stell-engineering.com/blog/what-is-requirement-traceability) |
| Configuration management | P64 Versioning and change review | [arXiv: Controls and machine protection](https://arxiv.org/pdf/1608.02836) [arXiv: Agentic Configuration Management](https://arxiv.org/pdf/2608.11166) |
| Reliability and safety engineering | P22 Failure and interaction analysis | [EBSCO: FMEA](https://www.ebsco.com/research-starters/social-sciences-and-humanities/failure-mode-and-effects-analysis-fmea) [BMJ Qual Saf / PMC: FMEA outputs - are they valid?](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3405478/) [Leveson & Thomas: STPA Handbook](https://www.flighttestsafety.org/images/STPA_Handbook.pdf) |
| Accident research | P82 Investigate anomalies | [Wikipedia: Normalization of deviance](https://en.wikipedia.org/wiki/Normalization_of_deviance) [National Academies: Accident precursor analysis](https://www.nationalacademies.org/read/11061/chapter/2) |
| Metrology | P58 Comparable measurement | [Wikipedia: Measurement uncertainty](https://en.wikipedia.org/wiki/Measurement_uncertainty) [Wikipedia: Metrological traceability](https://en.wikipedia.org/wiki/Metrological_traceability) |
| Risk regulation (UK HSE) | Master rule | [Primatech: ALARP principle](https://www.primatech.com/technical/alarp-principle) |
| Design engineering | P16 Set-based design | [Sobek, Ward, Liker: Toyota's Principles of Set-Based Concurrent Engineering](https://www.gapimprove.org/_files/ugd/cd8b34_2d04bd540ca04019986c3ba54ae8631e.pdf?index=true) |
| Engineering physics | P12 Model validity | [Wikipedia: Fermi problem](https://en.wikipedia.org/wiki/Fermi_problem) |

### Management: Governance and assurance

| Domain | Rules | References |
| --- | --- | --- |
| Corporate governance | P6 Conflict-of-interest disclosure; P56 Independent checker (supports) | [G20/OECD Principles of Corporate Governance 2023](https://legalinstruments.oecd.org/public/doc/322/322.en.pdf) [ISO 37000:2021 Governance of organizations (catalogue page)](https://www.iso.org/standard/65036.html) |
| Internal audit and assurance | P40 Defense in depth; P56 Independent checker | [IIA: The Three Lines Model (2020)](https://www.theiia.org/globalassets/documents/resources/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense-july-2020/three-lines-model-updated-english.pdf) |
| Statutory audit | P56 Independent checker | [Regulation (EU) No 537/2014, Article 17 (text copy)](https://www.charteredaccountants.ie/chariotindex/text/ec_2014_537/17.html) |
| Internal control | P43 Segregation of duties; P42 Two-person rule | [NIST CSRC Glossary: separation of duty (SP 800-192)](https://csrc.nist.gov/glossary/term/separation_of_duty) |
| Compliance management | P60 Codes as minimum; P59 Traceability | [ISO 37301:2021 Compliance management systems (catalogue page)](https://www.iso.org/standard/75080.html) |
| Whistleblowing and speak-up | P4 Stop authority | [Directive (EU) 2019/1937 (EUR-Lex)](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L1937) |
| Anti-bribery | P6 Conflict-of-interest disclosure (supports) | [ISO 37001 Anti-bribery management systems (catalogue page)](https://www.iso.org/standard/37001) |

### Management: Strategy and decisions

| Domain | Rules | References |
| --- | --- | --- |
| Enterprise risk management | Master rule; P16 Set-based design; P22 Failure and interaction analysis | [COSO: ERM — Integrating with Strategy and Performance, Executive Summary (2017)](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf) [ISO 31000:2018 Risk management (catalogue page)](https://www.iso.org/standard/65694.html) |
| Decision making | P18 Decision speed by reversibility | [Amazon 2015 letter to shareholders (SEC filing)](https://www.sec.gov/Archives/edgar/data/1018724/000119312516530910/d168744dex991.htm) |
| Red teaming and challenge | P56 Independent checker; P46 Diversity | [UK MoD: Red Teaming Handbook, 3rd ed. (2021)](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1027158/20210625-Red_Teaming_Handbook.pdf) |
| Military command and control | P7 Commander's intent; P2 Work within competence | [US Army ADP 6-0 Mission Command (2019)](https://irp.fas.org/doddir/army/adp6_0.pdf) |
| Pre-mortem risk identification | P22 Failure and interaction analysis | [Klein: Performing a Project Premortem (HBR 2007)](https://hbr.org/2007/09/performing-a-project-premortem) |

### Management: Portfolio, programme and project

| Domain | Rules | References |
| --- | --- | --- |
| Project management | P67 Critical path; P65 Small verified steps; P75 Actionable alerts; P20 Stop criteria set in advance; Master rule (tailoring) | [ISO 21502:2020 Guidance on project management (catalogue page)](https://www.iso.org/standard/74947.html) [PMI: PMBOK Guide 8th edition](https://www.pmi.org/standards/pmbok/about) [Purple Griffon: PRINCE2 7th edition principles](https://purplegriffon.com/blog/prince2-7th-edition-principles) |
| Portfolio management | P20 Stop criteria set in advance (supports); P22 (portfolio view) | [ISO 21504:2022 Guidance on portfolio management (catalogue page)](https://www.iso.org/standard/82867.html) |
| Forecasting of large projects | P12 Model validity | [Flyvbjerg: From Nobel Prize to Project Management (2006)](https://arxiv.org/pdf/1302.3642) |
| Agile and Scrum | P66 Isolation before work; P81 Plan-Do-Check-Act; P23 Simplicity; P28 Accumulated degradation | [Principles behind the Agile Manifesto](https://agilemanifesto.org/principles) [The Scrum Guide (2020)](https://scrumguides.org/scrum-guide.html) |
| Software delivery management | P65 Small verified steps | [DORA: Working in small batches](https://dora.dev/capabilities/working-in-small-batches/) |
| Software project staffing | P53 Late work and added people | [The Jargon File: Brooks's Law](http://www.catb.org/jargon/html/B/Brookss-Law.html) |

### Management: Product and innovation

| Domain | Rules | References |
| --- | --- | --- |
| Experimentation | P31 Design by selection | [Kohavi & Thomke: The Surprising Power of Online Experiments (HBR 2017)](https://web-docs.stern.nyu.edu/executive/The%20Surprising%20Power%20of%20Online%20Experiments.pdf) |
| Innovation management | P17 Technology maturity (supports) | [ISO 56001:2024 Innovation management system (catalogue page)](https://www.iso.org/standard/79278.html) |

### Management: Operations, quality and supply

| Domain | Rules | References |
| --- | --- | --- |
| Quality management | P81 Plan-Do-Check-Act; P1 Public safety first (ethics); P39 Error-proofing; P19 Indicators are not targets (supports) | [ISO: ISO 9001:2026 launch (16 Sep 2026)](https://www.iso.org/news/2026/09/ISO9001-2026) [The W. Edwards Deming Institute: 14 Points](https://deming.org/explore/fourteen-points/) |
| Lean production | P4 Stop authority | [Toyota: Toyota Production System (jidoka)](https://global.toyota/en/company/vision-and-philosophy/production-system/) |
| Operations and queueing | P52 Limit work in progress; P44 Margin | [Little: Little's Law as Viewed on Its 50th Anniversary (reprint)](https://projectproduction.org/journal/reprint-littles-law-as-viewed-on-its-50th-anniversary/) |
| Supply chain management | P51 Shared demand signal | [Lee, Padmanabhan, Whang: Information Distortion in a Supply Chain (Management Science 1997)](https://courses.ie.bilkent.edu.tr/ie102/wp-content/uploads/sites/12/2019/02/Lee-Padmanabhan-Whang-1997-MS.pdf) |
| Procurement | P6 Conflict-of-interest disclosure; P3 Sustainability | [OECD Recommendation on Public Procurement: Integrity](https://web.archive.org/web/20240518154901/https://search.oecd.org/governance/procurement/toolbox/principlestools/integrity/) [ISO 20400:2017 Sustainable procurement (catalogue page)](https://www.iso.org/standard/63026.html) |
| Responsible supply chains | P14 Provenance | [OECD Due Diligence Guidance for Responsible Business Conduct (2018)](https://www.oecd.org/en/publications/oecd-due-diligence-guidance-for-responsible-business-conduct_15f5f4b3-en.html) |
| Asset management | P78 Asset inventory | [ISO 55000:2024 Asset management (catalogue page)](https://www.iso.org/standard/83053.html) |
| IT service management | P64 Versioning and change review; P33 Strict interfaces | [ISO/IEC 20000-1:2018 Service management (catalogue page)](https://www.iso.org/standard/70636.html) |

### Management: Risk, resilience and legal

| Domain | Rules | References |
| --- | --- | --- |
| Business continuity | P73 Response faster than harm; P47 Graceful degradation | [BCI Good Practice Guidelines 2018 (with ISO 22301:2019 definitions)](https://www.thebci.org/static/cf455e45-b2c2-4a44-b77da7c99fd6df77/BCI-GPG-2018-Edition.pdf) [ISO 22301:2019 (catalogue page)](https://www.iso.org/standard/75106.html) |
| Incident and crisis management | P30 Exact constraint (unity of command); P79 Span of control; P76 Sterile critical phase; P37 Fail-safe (transfer of command) | [FEMA: National Incident Management System, 3rd ed. (2017)](https://training.fema.gov:443/EMIWeb/IS/IS700b/Handouts/National_Incident_Management%20System_Third%20Edition_October_2017.pdf) [ISO 22361:2022 Crisis management (catalogue page)](https://www.iso.org/standard/50267.html) |
| Information security management | P36 Least privilege; P78 Asset inventory | [ISO/IEC 27001:2022 (catalogue page)](https://www.iso.org/standard/27001) |
| Data protection | P36 Least privilege; P24 Lifecycle and decommissioning; P11 Trustworthy evidence | [GDPR Article 5 (text copy)](https://gdpr-info.eu/art-5-gdpr/) |
| Records management and accounting | P11 Trustworthy evidence | [§ 239 HGB (text copy, dejure.org)](https://dejure.org/gesetze/HGB/239.html) [ISO 15489-1:2016 Records management (catalogue page)](https://www.iso.org/standard/62542.html) |
| Litigation and investigations | P83 Preserve evidence | [The Sedona Conference: Commentary on Legal Holds, Second Edition: The Trigger & The Process (2019)](https://www.thesedonaconference.org/sites/default/files/publications/Commentary%20on%20Legal%20Holds.pdf) |
| Occupational health and safety | P38 Hierarchy of controls | [ISO 45001:2018 (catalogue page)](https://www.iso.org/standard/63787.html) [Auditor Training Online: ISO 45001 Clause 8.1.2, Eliminating hazards and reducing OH&S risks](https://blog.auditortrainingonline.com/blog/iso-45001-clause-8-1-2) |
| Environmental management | P3 Sustainability | [ISO 14001:2015, withdrawn, replaced by ISO 14001:2026 (catalogue page)](https://www.iso.org/standard/60857.html) |
| Organizational accident research | P82 Investigate anomalies | [Columbia Accident Investigation Board report, Vol. 1 (2003), summary](https://www.globalsecurity.org/space/library/report/2003/caib-report_vol-1_august2003.htm) |

### Management: People and organization

| Domain | Rules | References |
| --- | --- | --- |
| Team leadership | P5 Psychological safety; P25 Human factors (role clarity) | [Edmondson: Psychological Safety and Learning Behavior in Work Teams (ASQ 1999)](https://web.mit.edu/curhan/www/docs/Articles/15341_Readings/Group_Performance/Edmondson%20Psychological%20safety.pdf) [Google re:Work: Understand team effectiveness](https://rework.withgoogle.com/intl/en/guides/understand-team-effectiveness) |
| Personnel selection | P62 Structured selection of people | [Sackett et al.: Revisiting meta-analytic estimates of validity in personnel selection (J. Appl. Psychol.)](https://www.gwern.net/doc/statistics/meta-analysis/2021-sackett.pdf) |
| Performance feedback | P63 Feedback on the task | [Kluger & DeNisi: The effects of feedback interventions on performance (Psychol. Bull. 1996)](https://cris.huji.ac.il/en/publications/the-effects-of-feedback-interventions-on-performance-a-historical/) |
| Goals and performance measurement | P21 Specific, challenging goals with feedback; P19 Indicators are not targets; P9 Measurable requirements | [Locke & Latham: Building a practically useful theory of goal setting (Am. Psychol. 2002)](https://goal-lab.psych.umn.edu/orgpsych/2020/readings/5.%20Motivation/Locke%20&%20Latham%20(2002).pdf) [Wikipedia: Campbell's law](https://en.wikipedia.org/wiki/Campbell%27s_law) |
| Working time and health | P28 Accumulated degradation | [WHO/ILO: Long working hours increasing deaths (2021)](https://www.who.int/news/item/17-05-2021-long-working-hours-increasing-deaths-from-heart-disease-and-stroke-who-ilo) [Pencavel: The Productivity of Working Hours (IZA DP 8129, 2014)](https://docs.iza.org/dp8129.pdf) |
| Work design and focus | P76 Sterile critical phase | [Mark, Gudith, Klocke: The cost of interrupted work (CHI 2008)](https://www.interruptions.net/literature/Mark-CHI08.pdf) |
| Succession and human capital | P45 Redundancy (N-1); P58 Comparable measurement | [ISO TC 260: People power (ISO 30414, ISO/TS 30433)](https://committee.iso.org/news/ref2689.html) |
| Knowledge management | P45 Redundancy (supports); P10 Decision records (supports) | [ISO 30401:2018 Knowledge management systems (catalogue page)](https://www.iso.org/standard/68683.html) |
| Change management | P69 Guided change | [Kotter: Leading Change — Why Transformation Efforts Fail (HBR 1995)](https://fcm.ucsf.edu/sites/g/files/tkssra17611/files/Kotter_WhyTransformationEffortsFail.pdf) |
| Organizational justice | P8 Fair process | [Kim & Mauborgne: Fair Process (HBR 1997)](https://ieanea.org/wp-content/uploads/2019/05/FairProcessArticle.pdf) |
| Organization design | P35 Structure follows the intended system; P79 Span of control | [Conway: How Do Committees Invent? (1968)](https://www.melconway.com/Home/Committees_Paper.html) |
| Escalation of commitment | P20 Stop criteria set in advance | [Staw: Knee-deep in the big muddy (1976)](https://www.gwern.net/doc/psychology/cognitive-bias/sunk-cost/1976-staw.pdf) |

### Management: Finance

| Domain | Rules | References |
| --- | --- | --- |
| Accounting and bookkeeping | P11 Trustworthy evidence | [§ 239 HGB (text copy, dejure.org)](https://dejure.org/gesetze/HGB/239.html) |
| Payments and treasury | P42 Two-person rule; P43 Segregation of duties | [NIST CSRC Glossary: separation of duty](https://csrc.nist.gov/glossary/term/separation_of_duty) |
| Budgeting | P49 Induced demand | [Parkinson: Parkinson's Law (The Economist, 1955; text copy)](https://doc.cat-v.org/economics/parkinsons-law) |

### Checked without a separate row

These domains produced no sourced rule. The last column shows which rules apply anyway by cross-reference, in addition to all universal rules. This column is the author's judgment, not a sourced finding.

| Domain | Reason | Applicable by cross-reference (besides all universal rules) |
| --- | --- | --- |
| Regenerative medicine | searched; no source found for a distinct principle | P59 (regulated), P15 (irreversible harm), P17 (new technology), P61 (results that cannot be fully inspected) |
| Composite materials | the source for barely visible impact damage could not be fetched; not included | P61 (hidden damage that inspection cannot fully find) |
| Computational materials | the checked source has no statement on model validation; P12 covers model validity | P31 (weak models), P77 (data-driven models) |
| Material characterization | the checked source has no statement on calibration; P58 covers it | universal rules only; P58 is the central one |
| Sports engineering | no distinct principle found; equipment safety standards fit P60 | P60 (equipment standards exist) |
| Thermal engineering | the checked source states only that heat must be managed for reliability; covered by P44 (derating) and P28 | P48 (thermal control loops) |
| Surface engineering, industrial plant, power plant, project, information, facilities | not researched separately; they overlap covered domains (P28, P24, P45, P74, P67, P77) | plants: P45, P59, P48, P78; information: P33, P77; project: universal rules only |
| Applied engineering, electromechanics, mechatronics | umbrella terms that combine other branches | P33 (data interfaces), P48 (control loops) |
| Geomatics | only the units and reference-frame principle (P33) applies; no geomatics-specific source | P33 (data interfaces), P77 (data-driven results) |
| Explosives and military engineering | out of scope beyond organizational practice (P42 two-person rule) | not assessed (out of scope) |
| Sales and marketing management | not researched separately | P19 (sales quotas are gamed), P31 (experiments), P51 (share sell-through data) |
| Customer service management | not researched separately | P47 (triage under overload), P75 (escalation only on exception), P52 (queue length) |
| Facility management (ISO 41001), energy management (ISO 50001) | catalogue pages not checked | P78, P74, P3 |
| Treasury, tax, legal departments | covered by finance and compliance rows | P43, P42, P60, P59 |
| Public administration | covered by procurement, governance and records rows | P6, P11, P60, P59 |
| Non-profit management | no distinct principle found | universal rules and the rules from management sources only |
| Self-management and time management | out of scope (one person, see section 1) | P76 and P52 apply to one person as advice, not as organizational rules |

## 5. Glossary

Each term has exactly one meaning in this taxonomy. No other word is used for the same meaning.

| Term | Meaning | Not the same as / opposite |
| --- | --- | --- |
| error | a human action or omission that differs from the intended action | defect, failure |
| defect | a flaw in the product, caused by an error | error, failure |
| failure | the product does not perform its required function | defect (a defect can exist without causing a failure) |
| anomaly | behavior that differs from what was expected, with or without harm | failure (an anomaly can happen without a failure) |
| requirement | a measurable statement of what the product must do | a wish or goal without a measure |
| verification | checking that the product was built as the requirements specify ("built right") | validation |
| validation | checking that the product fulfills its intended purpose ("right thing built") | verification |
| domain of applicability | the range of conditions for which a model has been validated | the range in which a model produces an answer |
| consequence | the harm caused if a failure happens | likelihood |
| uncertainty | how poorly the loads, inputs or conditions are known | consequence |
| margin | capacity above the expected load | redundancy, robustness |
| robustness | the result changes little when inputs vary within the specification | margin; strictness (rejecting input outside the specification, P33) |
| fatigue | damage from repeated loads that builds up over time | overload (one load above the limit) |
| oscillation | a control loop switching back and forth around its target | opposite: stable control |
| constraint (bottleneck) | the part of a system that limits its total output | any slow part |
| critical path | the longest chain of dependent tasks | the most important tasks |
| hold point | a check that work cannot pass until it is approved | witness point (work continues while the check is observed) |
| drift | a change in real-world data that makes a model less accurate | a defect in the model |
| measurement uncertainty | the spread of values that could reasonably be attributed to a measured quantity | error (the difference from the true value) |
| chain of custody | a record of who held a piece of evidence, and when | ownership |
| actionable alert | an alert that requires a defined human action now | an informational message |
| commissioning | testing that all parts work together against the owner's requirements before handover | testing each part alone |
| provenance | the documented origin, batch and certificate of a part | a part's current location |
| exact constraint | each property is set by exactly one mechanism | opposite: over-constraint (several mechanisms set the same property) |
| weakest link | the single part whose failure makes the whole system fail | the average part |
| set-based design | keeping several alternatives open and eliminating weak ones as evidence arrives | opposite: point-based design (choosing one option early) |
| cliff effect | output stays perfect until it collapses suddenly | gradual degradation |
| redundancy | a second copy of a part that takes over when the first copy fails | diversity |
| diversity | copies that are built differently, so one cause cannot fail all of them | redundancy |
| compartment | an isolated part of the system that contains a failure | opposite: shared failure domain |
| graceful degradation | losing lower-priority functions while critical functions keep running | opposite: cascading failure |
| safe state | a predefined state that causes no harm | normal operating state |
| isolation | disconnecting a part from all inputs and energy, and locking that state | switching off (anyone can switch it on again) |
| control | a measure that reduces risk | a check (a check detects; a control reduces) |
| critical control point | a process step where control is essential to prevent a hazard | every process step |
| critical limit | a minimum or maximum value that must be kept at a critical control point | a target value |
| checker | a person, other than the author, who reviews work | the author |
| universal rule (U) | a rule whose condition is true, or whose trigger occurs, in every engineered system; its intensity scales with the master rule | a rule that applies everywhere at full strength |
| risk-scaled rule (R) | a rule that applies only above a consequence or uncertainty threshold set by the rigor matrix | conditional rule |
| conditional rule (C) | a rule that applies only when the system has a property that a common class of systems lacks | risk-scaled rule |
| trigger | an event that happens in the life of every system, such as a failure, a change or a decision | scope condition (a property only some systems have) |
| psychological safety | a shared belief that the team is safe for interpersonal risk taking | comfort or low standards (a team can be safe and demanding) |
| conflict of interest | a personal interest that could influence, or appear to influence, a person's judgment | a disagreement about a decision |
| commander's intent | the purpose, the desired end state and the constraints of a task | a plan or a step list (the method) |
| reversible decision (two-way door) | a decision whose effects can be undone at low cost | **opposite:** irreversible decision (one-way door) |
| indicator | a measure that shows how a process or system behaves | target (a value someone is rewarded for reaching) |
| stop criterion | evidence, written before a project starts, that ends the project when it occurs | a milestone (marks progress, does not decide continuation) |
| escalation of commitment | adding resources to a failing course of action because of earlier investment | persistence based on new evidence |
| segregation of duties | splitting a process so that no single person controls all its steps | two-person rule (two people at one moment of action, P42) |
| work in progress (WIP) | work items that have started and are not finished | backlog (work not started) |
| lead time | time from the start of a work item to its finish | effort (working hours spent on it) |
| span of control | the number of people one person directly directs | the size of the whole unit |
| unity of command | each person reports to exactly one person for a given task | **opposite:** dual reporting for the same task |
| engineering organization | two or more people who design, build or operate a system together | a one-person business (rules on delegation, segregation and teams cannot apply to it) |
| manager | a person who is accountable for the work of other people | the governing body (which oversees managers) |
| governing body | the group that holds management accountable (board, supervisory board, steering committee) | management |
| accountable | answers for the result and makes the final decision; exactly one person per objective | responsible (does the work; can be several people) |
| objective | a measurable statement of what must be achieved, by when | a goal without a measure ("be the best") |
| tolerance | the permitted deviation from a plan (time, cost, scope, quality, risk) before a decision moves up one level | a target value |
| exception | a forecast or actual breach of a tolerance | a routine status report |
| risk appetite | the amount and type of risk the governing body accepts to achieve its objectives | risk capacity (the maximum risk the organization can survive) |
| fair process | engaging people, explaining the decision, and stating new expectations | consensus (fair process is "not decision by consensus") |
| reference class | a set of past, similar projects with known outcomes | the current project's own plan (inside view) |
| stage gate | a decision point at which an initiative is continued, changed or stopped | a status meeting (no stop decision) |
| business case | the documented reason to start and continue an initiative | the project plan |
| verification (management) | checking that the deliverable meets the agreed specification ("doing things right") | validation |
| validation (management) | checking that the deliverable creates the intended benefit ("doing the right things") | verification |
| after-action review | a non-punitive discussion of what happened, why, and how to improve | **opposite:** a critique that looks for a person to blame |
| maximum tolerable period of disruption (MTPD) | the time after which the impact of not resuming an activity becomes unacceptable | recovery time objective |
| recovery time objective (RTO) | the time within which an activity must resume at a minimum acceptable capacity; set inside the MTPD | MTPD |
| legal hold | an instruction to preserve documents and data because litigation or an investigation is reasonably anticipated | normal retention (documents may be deleted on schedule) |
| key person | a person whose sudden absence would stop a critical function | a senior person (seniority is not the test) |
| red team | an independent group that applies structured critical thinking to a plan before the decision | internal audit (checks after the fact) |

## 6. Rigor matrix

Find the cell that matches your system. Universal rules apply in every cell; the master rule scales how strictly. Conditional rules apply in every cell where their condition is true. Risk-scaled rules apply only in the cells listed. MUST rules apply whenever their IF-condition is true.

|  | **Low uncertainty** | **High uncertainty** |
| --- | --- | --- |
| **Low consequence** | all universal rules, conditional rules whose condition is true. Checker level: peer (P56). | all universal rules, conditional rules whose condition is true, P16, P31, P68. Checker level: peer (P56). |
| **High consequence** | all universal rules, conditional rules whose condition is true, P42, P43, P45, P46, P59. Checker level: external (P56). | all universal rules, conditional rules whose condition is true, all risk-scaled rules. Checker level: external (P56). |

## 7. Rules by category

### A. Responsibility

Duties toward people, the environment and the work itself.

| ID | Name | Strength | IF (condition) | THEN (action) | BECAUSE (reason) | Example (software/infra) |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Public safety first | MUST | always | put public safety above cost, schedule and convenience | failures harm people outside the project | block a release that leaks user data |
| P2 | Work within competence | MUST | always | work only within your competence, and involve an expert outside it | error rates rise outside known areas | a security engineer reviews an IAM design |
| P3 | Sustainability | SHOULD | always | reduce environmental impact and resource use across the whole lifecycle | NSPE canon 1 includes sustainable development | scale idle environments to zero |
| P4 | Stop authority | SHOULD | anyone finds a problem that could cause harm | let that person stop the work without needing permission and without being blamed; the stop must always be available, must override all other functions, and resetting it must not restart the system | the person nearest to a problem sees it first | a deploy freeze that overrides Argo CD auto-sync; lifting the freeze requires an explicit sync |
| P5 | Psychological safety | SHOULD | people work together on a system | make it safe to report errors, ask questions and disagree: leaders ask for input, thank people for bad news, and never punish an honest report | psychological safety enables learning behavior, which drives team performance; problems that people hide cannot be fixed | the first person to report a broken pipeline is thanked, not blamed; the team lead names their own mistake in the retrospective |
| P6 | Conflict-of-interest disclosure | MUST | a person decides on, reviews or advises on work in which they have a personal interest | disclose the interest and step out of the decision or review | a personal interest biases judgment and destroys trust in the decision | an engineer who holds shares in a monitoring vendor leaves its evaluation |
| P7 | Commander's intent | SHOULD | you delegate a task | state the purpose, the desired end state and the constraints, and leave the method to the people who do the work (mission orders) | plans meet changing conditions; people who know the purpose can act correctly without new orders | an epic states "why", "done when" and "must not", not a list of kubectl steps |
| P8 | Fair process | SHOULD | a decision affects people | engage them (ask for input and challenge), explain the final decision and its reasons, and state the new expectations clearly; this is not consensus | people accept and carry out decisions they disagree with when the process was fair | before changing the on-call model, the team is asked, then told the decision, the reasons and the new rules |

| ID | Class (why) | HOW TO CHECK | VIOLATION (opposite of the rule) | RELATED | Evidence | Source domain |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | universal (U), category A: true for every system | every release gate contains a safety and security sign-off item | shipping a known safety defect to meet a deadline | strengthens P37, P38; strengthened by P4 | strong | all (professional ethics) |
| P2 | universal (U), category A: true for every system | each design has a named checker with expertise in its domain | approving work in a domain you do not know | strengthens P56; strengthened by P6, P62 | strong | all (professional ethics) |
| P3 | universal (U), category A: true for every system | resource use is measured and reviewed | unused resources running all the time | depends on P24; strengthened by P24, P49 | moderate | all (professional ethics) |
| P4 | universal (U), category A: trigger that occurs in the life cycle of every system | the stop mechanism exists, works in every operating mode, does not restart on reset, and every use is reviewed without blame | a release continues while a known problem is still being discussed | depends on P80; strengthens P1, P82; strengthened by P5 | strong (emergency stop is standardized in ISO 13850) | manufacturing (Toyota andon), machinery (emergency stop) |
| P5 | universal (U), category A: every system is built or operated by people who work together | a regular anonymous survey item on safety to speak up; the number of reported near misses does not fall after an incident | punishing the person who reported a problem | strengthens P80, P82, P4; strengthened by P63; conflicts with accountability (see K7) | strong (peer-reviewed field study; Google study of 180 teams) | management (team leadership) |
| P6 | universal (U), category A: trigger that occurs in the life cycle of every system (every system has suppliers, reviewers and decision-makers) | a register of declared interests exists and is checked before each vendor selection, design review and approval | a reviewer approves a design that uses a product of a company they own | strengthens P2, P43, P56 | strong (NSPE Code of Ethics II.4.a; G20/OECD Principles II.F.2) | professional ethics, management (corporate governance) |
| P7 | universal (U), category A: every engineering organization delegates work | each delegated task or epic states purpose, end state and constraints | a step list with no purpose; work stops when the plan no longer fits | depends on P2; conflicts with P71, P72, P61 (see K6) | strong (US Army doctrine ADP 6-0) | management (military command and control) |
| P8 | universal (U), category A: every engineering organization makes decisions that affect people | for each decision that changes people's work: an input round, a written explanation and stated expectations exist | announcing a reorganization without reasons | strengthens P64, P69 | moderate (management research; practitioner article) | management (organizational justice) |

### B. Knowledge and decisions

How requirements, decisions, models and evidence are recorded and trusted.

| ID | Name | Strength | IF (condition) | THEN (action) | BECAUSE (reason) | Example (software/infra) |
| --- | --- | --- | --- | --- | --- | --- |
| P9 | Measurable requirements | MUST | always | write each requirement as measurable, and link it to a user need | an unmeasurable requirement cannot be verified | "p95 latency \< 200 ms", linked to a ticket |
| P10 | Decision records | SHOULD | you make a significant design decision | record the decision, why you made it, and which alternatives you rejected | without the reason, later teams cannot judge whether the decision still holds | Architecture Decision Record (ADR) in the repository |
| P11 | Trustworthy evidence | SHOULD | a record is used as evidence (test result, approval, measurement) | make it attributable, legible, recorded at the time, original and accurate; changes must keep the original entry visible and record who, when and why | evidence that can be changed silently proves nothing | signed commits, immutable audit logs, CI results stored with the commit SHA |
| P12 | Model validity | SHOULD | a decision depends on a model, simulation or estimate | validate the model for its intended use, use it only inside the range it was validated for (domain of applicability), and check each result against an independent rough estimate (order of magnitude) | a model is only trustworthy inside its validated range | a load test on 3 nodes does not prove behavior on 50 nodes |
| P13 | Automated reproducible results | SHOULD | a result must be reproducible | produce it only through automated, recorded steps, with versions of data, code and tools | manual steps are error-prone and cannot be reproduced | infrastructure changed only through pipelines; no manual kubectl edits; pinned tool versions |
| P14 | Provenance | SHOULD | parts or materials come from suppliers | trace each part to its origin, batch and certificate (provenance) | without provenance you cannot prove quality, or find all affected parts when a defect is found | signed images with build provenance and SBOM; deployment by pinned digest |
| P15 | Precaution | SHOULD | a possible harm is serious or irreversible, and the evidence is incomplete | take proportionate, cost-effective protective measures without waiting for full proof | irreversible harm cannot be undone once the proof arrives | take a snapshot and stop writes when data corruption is suspected, before the root cause is proven |
| P16 | Set-based design | SHOULD | uncertainty is high early in a design | develop several alternatives in parallel, eliminate weak ones as evidence arrives, and commit only after feasibility is shown (set-based design; opposite: point-based design) | committing early to one option risks expensive rework when it fails | prototype two ingress controllers until load tests decide |
| P17 | Technology maturity | SHOULD | the design depends on a technology that is new to the team or the industry | assess how mature the technology is, and keep immature technology out of critical paths | immature technology carries unknown failures | CNCF sandbox project vs. graduated project for a core platform component |
| P18 | Decision speed by reversibility | SHOULD | you make a decision | classify it as reversible (two-way door) or irreversible (one-way door); make reversible decisions quickly at the lowest competent level, and irreversible decisions slowly, with consultation and review | heavy process on reversible decisions causes slowness and too little experimentation; light process on irreversible decisions causes lasting harm | a new linter rule: the team decides today; deleting a production database or changing the cloud provider: P42, red team, ADR |
| P19 | Indicators are not targets | SHOULD | a measure is used to reward, rank or punish people | expect it to be gamed: pair it with a counter-measure, compare it with direct observation, and change it when it drifts from the real objective | the more a quantitative indicator is used for decisions, the more it is corrupted and the more it distorts the process it measures (Campbell's law) | deployment frequency is paired with change failure rate; MTTR is not a bonus target |
| P20 | Stop criteria set in advance | SHOULD | you start a project or prototype with an uncertain outcome | write down, before starting, the evidence and the decision points (gates) at which it stops, and let someone who did not start it make the continue-or-stop decision | people who are responsible for an earlier decision commit the most resources to it after negative results (escalation of commitment) | a service-mesh pilot stops if p99 latency rises by more than 5 ms after 4 weeks; the architecture board, not the sponsor, decides |
| P21 | Specific, challenging goals with feedback | SHOULD | you set goals for people or teams | set few, specific and challenging goals, give regular feedback on progress toward them, and for new or complex tasks set learning goals first | specific, difficult goals lead to higher performance than "do your best", and goals plus feedback work better than goals alone | "cut median build time from 12 to 6 minutes this quarter", with a weekly chart; for a new technology: "run three spikes and document what we learned" |

| ID | Class (why) | HOW TO CHECK | VIOLATION (opposite of the rule) | RELATED | Evidence | Source domain |
| --- | --- | --- | --- | --- | --- | --- |
| P9 | universal (U), category B: true for every system | every requirement has an acceptance criterion and a link to a user need | "the system shall be fast" | strengthens P54, P59; strengthened by P21 | moderate | systems engineering |
| P10 | universal (U), category B: trigger that occurs in the life cycle of every system | each significant decision has a record with its reason and the rejected alternatives | nobody knows why the system is built this way | strengthens P64, P80; strengthened by P16, P18, P20 | moderate | software (ADR), civil and offshore (basis of design) |
| P11 | universal (U), category B: trigger that occurs in the life cycle of every system | a sample of records shows author, time and full change history | editing a test report after the fact without a trace | strengthens P59, P64; strengthened by P13, P14 | strong (required in regulated domains) | pharma and clinical trials (ALCOA) |
| P12 | universal (U), category B: every design decision rests on a model or an estimate | each model used for a decision states its validated range, and the decision lies inside that range | extrapolating a benchmark far beyond the tested load | depends on P54; strengthens P44; strengthened by P34, P58, P77 | moderate | simulation and computational engineering, engineering physics (Fermi estimates) |
| P13 | universal (U), category B: every engineering result must be checkable by someone else (P56) | each result can be regenerated from recorded inputs and versions with one command | a report built by copying numbers by hand | depends on P64; strengthens P11 | moderate | bioinformatics (reproducible computational research) |
| P14 | universal (U), category B: almost every system uses parts or software from suppliers | for each deployed artifact, origin, build and certificate can be shown | running an unsigned image from an unknown registry | strengthens P11, P78 | moderate | metallurgical engineering (mill test certificates) |
| P15 | risk-scaled (R), category B: only for serious or irreversible harm with incomplete evidence | for each serious or irreversible risk with incomplete evidence, a record states which protective measure was taken, or why none was | writes continue while the team waits for proof of data corruption | strengthens P37, P82; strengthened by P18 | moderate (contested: critics call it vague and say strong versions block beneficial technology; this rule uses the weak, proportionate version) | environmental engineering (precautionary principle) |
| P16 | risk-scaled (R), category B: only where uncertainty is high early; for a repeat design, one option is enough | early design records list the alternatives kept and the evidence that eliminated each rejected one | choosing one design at the start and discovering at the end that it cannot meet a requirement | depends on P58; strengthens P10, P17; strengthened by P20 | moderate | design engineering (Toyota set-based concurrent engineering) |
| P17 | conditional (C), category B: counterexample: a system built only from proven technology | each technology in a critical path has a recorded maturity assessment | adopting an untested tool for the production control plane without an assessment | depends on P10; strengthens P22; strengthened by P16, P20 | strong (standardized as ISO 16290:2013; NASA defines TRL 1 to 9) | aerospace (NASA TRL), EU, DoD |
| P18 | universal (U), category B: trigger that occurs in the life cycle of every system | each decision record (P10) states the class (reversible or irreversible) and the matching process | a three-week approval for a reversible tool trial; a lock-in contract signed in one meeting | strengthens P10, P15, P42; conflicts with P56, P64 (see K5) | moderate (practitioner source: a CEO's shareholder letter; consistent with P15 and P42) | management (decision making) |
| P19 | universal (U), category B: every system and every team whose performance is measured (P70, P58) | each rewarded indicator has a counter-indicator and a yearly review of whether it still tracks the objective | ticket count as the only measure of on-call quality | strengthens P58, P70, P82; conflicts with P21 | strong (Campbell; the same pattern is known as Goodhart's law) | management (performance measurement) |
| P20 | universal (U), category B: trigger that occurs in the life cycle of every system (every system starts as a project) | each project and prototype has written stop criteria and gate dates, and gate decisions are made by someone other than the sponsor | "we have invested too much to stop now" | strengthens P10, P16, P17, P65 | strong (experimental research, Staw 1976; PRINCE2 "continued business justification") | management (project management, organizational psychology) |
| P21 | universal (U), category B: every engineering organization sets goals | each goal has a measure, a deadline and a progress chart; new or complex work has learning goals | "do your best" as the only goal; goals without progress feedback | strengthens P9; strengthened by P63; conflicts with P19 (see K8) | strong (experimental and field research summarized in the paper); contested by Deming points 11 and 12, who rejects management by numerical goals | management (goals and motivation (goal-setting theory)) |

### C. Design

How to shape a design before it is built, so that it fails less.

| ID | Name | Strength | IF (condition) | THEN (action) | BECAUSE (reason) | Example (software/infra) |
| --- | --- | --- | --- | --- | --- | --- |
| P22 | Failure and interaction analysis | SHOULD | always | before you build, list how each part can fail, how parts that have not failed can interact unsafely, and how the system can cause harm while working as designed (insufficient design or foreseeable misuse) | a known failure or interaction can be designed against | "what happens if the registry is down?" and "what if two controllers fight over the same resource?" |
| P23 | Simplicity and modularity | SHOULD | always | choose the simplest design that meets the requirements, and split it into modules | every added part adds a way to fail | one Helm chart per app, not one chart for all |
| P24 | Lifecycle and decommissioning | SHOULD | always | plan operation, maintenance and decommissioning at design time | early design decisions fix most end-of-life costs | define how to delete a cluster and its data before creating it |
| P25 | Human factors | SHOULD | a person uses or operates the system | design the interface for the real user in the real environment, including stress, and for the full range of users, not an average user | a poor interface causes errors | a runbook that works at 3 a.m.; unambiguous CLI output |
| P26 | Design for testability | SHOULD | always | build ways to set and observe the internal state of each part into the design, so that it can be tested | a state you cannot set or observe cannot be tested | health and readiness endpoints, dry-run modes, feature flags for testing, debug endpoints |
| P27 | Robustness | SHOULD | always | design so that the result changes little when inputs vary (robustness) | removing every cause of variation costs more than tolerating it | retries with jitter, idempotent operations, tolerance for clock drift |
| P28 | Accumulated degradation | SHOULD | always | design for the damage that builds up over the whole design life, not only for the single largest load | repeated loads far below the maximum load cause failure, and the damage does not recover | soak tests over days, not only peak tests; disk wear; leaks that grow with uptime |
| P29 | Compatibility | SHOULD | parts of different kinds touch or interact | verify that they are compatible with each other in the real environment, and separate them where they are not | incompatible parts damage each other, even when each part is good on its own | tested compatibility matrix for Kubernetes, CNI and CSI versions; separate node pools for incompatible kernel modules |
| P30 | Exact constraint | SHOULD | several mechanisms can set the same property | constrain each property exactly once, with one owner (exact constraint) | over-constraint makes parts fight each other and deform the system | either the HPA or the GitOps manifest owns the replica count, not both; one source of truth per configuration value |
| P31 | Design by selection | SHOULD | no model is good enough to design the solution analytically | generate many variants, test them, keep the best, and repeat (design by selection) | selection by test finds good solutions without knowing exactly how they work | A/B tests, fuzzing, parameter search for autoscaler settings |
| P32 | End-to-end | SHOULD | a function (integrity, security, deduplication) can only be fully correct with knowledge at the end points | implement it at the end points; add it in lower layers only to improve performance | lower layers cannot guarantee the function and would burden every user | mTLS between services instead of relying only on network encryption; checksums on backups at the application level |
| P33 | Strict interfaces | SHOULD | components exchange data over an interface | send strictly according to the specification, reject and report input that violates it instead of silently accepting it, and state units, time zone and reference frames explicitly in every interface | silently tolerated defects become permanent unofficial standards and security holes, and unstated units get misread | schema validation in CI; fail on unknown fields; field names like latency_ms; timestamps in UTC with offset |
| P34 | Weakest-link scaling | SHOULD | a system grows in size or in number of parts | expect rare failures to become frequent, and design and test for the target scale | the larger the system, the more likely it contains a critical weak part (weakest link) | at 1,000 nodes, a node failure that happens once in 1,000 days per node happens every day |
| P35 | Structure follows the intended system | SHOULD | an organization designs a system with several components | design team boundaries and communication paths to match the component structure you want, and change them when the intended structure changes | organizations produce designs that copy their own communication structure (Conway's law) | one team per bounded context; the platform team owns the platform API, not parts of each product's code |

| ID | Class (why) | HOW TO CHECK | VIOLATION (opposite of the rule) | RELATED | Evidence | Source domain |
| --- | --- | --- | --- | --- | --- | --- |
| P22 | universal (U), category C: true for every system | a list of failure modes and unsafe interactions exists per component and is reviewed | the first failure analysis happens after an incident | strengthens P37, P38, P41, P44, P45, P46; strengthened by P17, P29, P55 | moderate (method widely used; RPN scoring criticized) | reliability and safety (FMEA, STPA), automotive (SOTIF) |
| P23 | universal (U), category C: true for every system | each component has one stated purpose, and no part is unused | adding features for imagined future needs | strengthened by P24, P30, P35; conflicts with P40, P41, P44, P45, P46, P47 | moderate | aerospace (Lockheed Skunk Works), software |
| P24 | universal (U), category C: true for every system | each design document has a maintenance and a decommissioning section | orphaned resources that nobody can safely remove | strengthens P3, P23; strengthened by P78 | moderate | nuclear, offshore, aerospace |
| P25 | universal (U), category C: trigger that occurs in the life cycle of every system | critical tasks are tested with real users or operators | blaming users for errors that the interface invites | depends on P80; strengthens P39; strengthened by P71, P76 | moderate (strong in medical devices) | human factors, medical devices, biomechanics (anthropometry) |
| P26 | universal (U), category C: true for every system | each component has documented test access to set and observe its key states | a component that can only be tested in production | strengthens P54, P57, P70 | moderate | computer engineering (design for testing) |
| P27 | universal (U), category C: every system meets variation in its inputs | tests with varied inputs (latency, clock drift, message order) show stable results | a system that works only when timing is exact | depends on P22; strengthens P44; conflicts with P33 | moderate | manufacturing quality (Taguchi), agricultural engineering |
| P28 | universal (U), category C: every system that is used more than once degrades over time | an endurance (soak) test runs for a period that represents real use, and the growth of leaks, wear or fragmentation is measured | only a short peak test, then failure after weeks of normal load | depends on P22; strengthens P74 | moderate | materials, mechanical, piping (fatigue, corrosion allowance) |
| P29 | universal (U), category C: every system with parts of different kinds has interactions between them | each interacting pair of components is on a tested compatibility list | upgrading one component and breaking another that was never tested with it | strengthens P22, P33 | moderate | materials (galvanic corrosion), biomaterials (biocompatibility) |
| P30 | universal (U), category C: over-constraint can occur in any system with more than one control mechanism | each managed field has exactly one owner | Argo CD and the HPA both set the replica count and keep reverting each other | strengthens P23, P64; strengthened by P35, P79 | moderate | optomechanical and precision engineering (kinematic coupling) |
| P31 | risk-scaled (R), category C: only where models are too weak for analytical design | each selection round has a defined test and records which variants were kept | choosing a configuration by opinion when it could be tested | depends on P58; strengthens P81 | moderate (directed evolution received the 2018 Nobel Prize in Chemistry) | molecular and biomolecular engineering (directed evolution, DBTL) |
| P32 | conditional (C), category C: counterexample: a system without communication between end points (a passive structure) | for each end-to-end property (integrity, authentication, exactly-once), the end points verify it themselves | trusting the network to deliver data correctly without a check in the application | strengthens P40 | moderate | network engineering (Saltzer, Reed, Clark 1984) |
| P33 | conditional (C), category C: counterexample: a system without data interfaces (a passive structure) | every interface has a machine-checked schema, and invalid input is rejected and logged | silently ignoring unknown or malformed fields | strengthens P39, P82; strengthened by P29, P35; conflicts with P27 | moderate (disputed: Postel's original principle says to accept liberally; RFC 9413 argues against it) | network protocol engineering (Postel, RFC 9413), space systems (Mars Climate Orbiter units) |
| P34 | conditional (C), category C: counterexample: a system of fixed, small size | failure rates are estimated per component and multiplied by the planned scale | assuming that a failure never seen in a 3-node test will not happen at 300 nodes | strengthens P12, P45 | strong (ASTM C1683: "The larger the specimen or component, the weaker it is likely to be"; standard text is paid; only the official summary was read) | ceramics and brittle materials (Weibull statistics, size effect) |
| P35 | conditional (C), category C: counterexample: a system built by one person, or by one small team that communicates as one unit | each major component boundary has one owning team, and cross-team dependencies are counted | one component maintained by four teams that never talk to each other | strengthens P23, P30, P33 | moderate (widely observed; one original paper) | management (organization design), software engineering |

### D. Protection

Controls that prevent harm, or contain it when it happens.

| ID | Name | Strength | IF (condition) | THEN (action) | BECAUSE (reason) | Example (software/infra) |
| --- | --- | --- | --- | --- | --- | --- |
| P36 | Least privilege | MUST | always | give each person, service and process only the minimum access its function needs | minimum access limits the damage when one part is compromised | Kubernetes RBAC scoped to one namespace |
| P37 | Fail-safe | MUST | always | define a safe state, and design failure to move there (fail-safe; opposite: fail-dangerous) | an uncontrolled failure causes the most harm | admission webhook rejects requests when it errors (fail-closed; opposite: fail-open) |
| P38 | Hierarchy of controls | SHOULD | a risk is found | use the highest possible control level: 1 eliminate; 2 minimize, substitute or moderate; 3 engineering control; 4 administrative control; 5 protective equipment; and act first at the source, then along the path, then at the receiver | higher control levels do not depend on human behavior, and a cause removed at the source cannot spread | 1 remove the port → 2 store less data / safer library / lower rate limit → 3 policy engine → 4 runbook → 5 "be careful"; noisy neighbor: limit the source → separate node pool → client timeouts |
| P39 | Error-proofing | SHOULD | a person can make the same error repeatedly | make the error impossible; if that is not possible, make the error visible immediately; if that is not possible either, limit its consequence so that it is survivable | errors are certain, defects are not | branch protection and required CI checks (impossible); a dry-run diff (visible); soft delete with a restore window (survivable) |
| P40 | Defense in depth | SHOULD | always | use several independent and verified control layers (defense in depth) | every single control fails at some point | RBAC + network policy + admission policy + runtime isolation |
| P41 | Compartments | SHOULD | always | divide the system into isolated compartments, so that one damaged compartment does not take down the whole system | a failure that cannot spread stays small | separate cloud accounts per environment, namespace quotas, cell-based architecture, bulkhead pattern |
| P42 | Two-person rule | SHOULD | an action is critical and cannot be undone | require two authorized people at the moment of action (two-person rule) | one person can make an error or act with bad intent, and nobody stops it | break-glass production access and deletion of production data need a second approver, live |
| P43 | Segregation of duties | MUST | a process handles money, assets, access rights or records, and the possible loss is above the acceptable risk | split the process so that no single person can request, approve, execute and record the same transaction; where the team is too small, add a compensating control (a later independent review) | a person who controls every step can cause an error or fraud and hide it | the engineer who requests production access cannot approve it; nobody can grant themselves admin rights and also delete the audit log |

| ID | Class (why) | HOW TO CHECK | VIOLATION (opposite of the rule) | RELATED | Evidence | Source domain |
| --- | --- | --- | --- | --- | --- | --- |
| P36 | universal (U), category D: true for every system | no role holds a permission that was unused for a set period | a CI pipeline with cluster-admin rights | strengthens P38, P40; strengthened by P78 | strong | security engineering (NIST) |
| P37 | universal (U), category D: every part can fail ("everything fails all the time") | failure injection shows that the system reaches the defined safe state | undefined behavior when a dependency is lost | depends on P22; strengthened by P1, P15, P22 | strong | nuclear, elevators, aviation |
| P38 | universal (U), category D: every system has risks; the trigger occurs in every life cycle | for each risk, a record states why a higher control level, or a control closer to the source, was not possible | a warning in the README as the only control | depends on P24; strengthens P39; strengthened by P1, P22, P36 | strong | occupational and chemical process safety (NIOSH, Kletz), acoustic engineering (source-path-receiver) |
| P39 | universal (U), category D: every system is built, operated or maintained by people | each repeated error from postmortems has a technical guard at the highest possible level | a "please remember to..." announcement as the only fix | depends on P80; strengthened by P25, P33, P38, P55, P66 | moderate | manufacturing (poka-yoke), transportation (Safe System) |
| P40 | universal (U), category D: every single control fails at some point; the number of layers scales with the master rule | each critical asset has at least two independent control layers, and each layer is verified | relying only on the perimeter firewall | depends on P36; strengthened by P32, P36, P41, P43; conflicts with P23 | moderate | security, oil and gas (well barriers), drinking water (multi-barrier) |
| P41 | universal (U), category D: every system with more than one part can spread a failure; how strict the compartments are scales with the master rule | a failure test in one compartment leaves all other compartments working | one shared database for all tenants and all environments | strengthens P40, P45; strengthened by P22; conflicts with P23 | strong | naval architecture (watertight compartments) |
| P42 | risk-scaled (R), category D: only for critical, irreversible actions; the cost is a second person who must be available | the system enforces a second approval for each listed critical action | one administrator can delete the production database alone | depends on P36; strengthens P56; strengthened by P18, P43 | strong (NIST SP 800-53 control AC-3(2) "Dual Authorization") | nuclear, banking, aviation (two-person rule) |
| P43 | risk-scaled (R), category D: required above the acceptable risk (master rule); in a very small team, compensating controls replace full segregation | a matrix of incompatible roles exists, and an access review finds nobody holding two incompatible roles | one person can create a cloud account, grant themselves admin and delete the audit log | depends on P36; strengthens P40, P42, P56; strengthened by P6 | strong (NIST SP 800-192 definition; internal control frameworks) | management (internal control), security engineering |

### E. Capacity and continuity

How the system keeps working under high load and partial failure.

| ID | Name | Strength | IF (condition) | THEN (action) | BECAUSE (reason) | Example (software/infra) |
| --- | --- | --- | --- | --- | --- | --- |
| P44 | Margin | SHOULD | always | design capacity above the expected load (margin), state the design load as a probability per time period, keep queued resources well below 100 % utilization, and set the margin by design maturity: larger early, smaller as uncertainty falls | real load exceeds estimated load, and delay rises sharply as utilization approaches 100 % | capacity for the 1-in-100-day traffic peak plus 30 % headroom; worker pools sized for \< 70 % average utilization |
| P45 | Redundancy (N-1) | SHOULD | one failure must not stop the function | add redundancy, so that the function survives the loss of any single element (N-1), and make sure each copy and the switch-over mechanism are reliable enough for the redundancy to help | one copy is a single point of failure | nodes in several availability zones |
| P46 | Diversity | SHOULD | one cause can hit all copies at once | make the copies different (diversity) | identical copies fail together | two different DNS providers |
| P47 | Graceful degradation | SHOULD | demand can exceed capacity | define in advance which lower-priority functions switch off first, so that critical functions keep running (graceful degradation; opposite: cascading failure) | uncontrolled overload makes the whole system collapse | PriorityClasses with preemption, rate limiting, switching off recommendations to keep checkout running |
| P48 | Damping | SHOULD | a control loop reacts automatically to measurements | add a deadband, delay or cooldown, so that the loop does not switch back and forth (oscillation; opposite: stable control) | repeated on-off cycles waste resources and destabilize the system | HPA stabilization window; failover hysteresis; circuit breaker cooldown |
| P49 | Induced demand | SHOULD | you add capacity to relieve congestion | expect demand to grow into the new capacity, and also manage demand (quotas, priorities, pricing) | added capacity lowers the cost of use, which increases use | a larger cluster fills up again; faster CI leads to more CI runs |
| P50 | Bottleneck first | SHOULD | you want more throughput | find the constraint (bottleneck) and improve it first | improving other parts does not increase output | speeding up lint does nothing if integration tests or the review queue are the bottleneck |
| P51 | Shared demand signal | SHOULD | several stages pass demand signals along a chain | share the real end demand with every stage, instead of letting each stage react only to the stage below it | each stage amplifies the variation it sees, so swings grow upstream (bullwhip effect) | upstream services scale on front-end traffic, not only on their own delayed queue length |
| P52 | Limit work in progress | SHOULD | a team or system handles a flow of work items | set a limit on the number of items in progress, and finish items before starting new ones | at a given throughput, average lead time is proportional to average work in progress (Little's law), so more parallel work means longer waiting for every item | at most 4 epics in progress per team; at most N concurrent rollouts per cluster |
| P53 | Late work and added people | SHOULD | work is late, and it needs coordination and learning | do not expect added people to recover the schedule soon; cut or move scope first, and add people early, only where the work can be split | new people need training and add communication paths, which at first lowers the output of the existing team (Brooks's law) | two weeks before a cluster-migration deadline, scope is cut; new engineers join the next migration from its start |

| ID | Class (why) | HOW TO CHECK | VIOLATION (opposite of the rule) | RELATED | Evidence | Source domain |
| --- | --- | --- | --- | --- | --- | --- |
| P44 | universal (U), category E: every system has uncertain loads and inputs ("all models are wrong"); the size of the margin scales with the master rule | a load test shows capacity ≥ the stated design load × the chosen factor, and queue delay stays within the target at that load | sizing exactly to the average load | strengthened by P12, P22, P27, P49, P50, P52; conflicts with P23; checked by P70 | strong (the phase values of GSFC-STD-1000 come from a garbled table extraction; check the original before quoting them) | mechanical, civil, coastal (factor of safety, return period), operations research (queueing), space systems (margins by phase), electronics (derating) |
| P45 | risk-scaled (R), category E: only where the function must survive single failures; a system that may stop briefly (a development environment) does not need it | removing any single element in a test keeps the function running | a single replica of a critical service | strengthened by P22, P41, P46, P34; conflicts with P23; conflicts with P53 when people are added for redundancy (add early, not late) | strong (N-1 ignores how likely an outage is and how large the affected area is; use the master rule for those. Error correction helps only when component error rates are below a threshold (quantum threshold theorem)) | aerospace, electronics, power grids, quantum engineering, computing theory (von Neumann) |
| P46 | risk-scaled (R), category E: only where redundancy is required and a common cause is credible | the shared dependencies of redundant copies are listed, and each one is justified | all replicas depend on the same expiring certificate | depends on P45; strengthens P45; strengthened by P22; conflicts with P23 | moderate | automotive (autonomous vehicles) |
| P47 | conditional (C), category E: counterexample: a system with a fixed, known load (an embedded controller) | an overload test shows that low-priority functions stop first and critical functions keep running | all functions slow down together until everything fails | depends on P44; strengthened by P48; conflicts with P23 | moderate | power grids (load shedding) |
| P48 | conditional (C), category E: counterexample: a system without automatic control loops | each automatic control loop has a documented deadband, delay or cooldown, and a test shows no repeated switching | an autoscaler that scales up and down every minute | depends on P70; strengthens P47; strengthened by P51 | moderate | control engineering |
| P49 | conditional (C), category E: counterexample: a system without a shared, congested resource | each capacity increase comes with a forecast of demand growth and a demand control (quota, priority or price) | doubling the cluster size and being full again a month later | depends on P70; strengthens P3, P44; strengthened by P51 | moderate | transportation (induced demand) |
| P50 | conditional (C), category E: counterexample: a system without a throughput goal (a monument) | before an improvement for throughput, the current constraint is measured and named | optimizing a fast step while work piles up in front of a slow step | depends on P70; strengthens P44; strengthened by P52 | moderate | industrial engineering (theory of constraints) |
| P51 | conditional (C), category E: counterexample: a single-stage system | each stage in a chain can see the end demand signal | each service autoscaler reacts only to its own queue, and the swings grow along the chain | depends on P70; strengthens P48, P49 | moderate | supply chain engineering (bullwhip effect) |
| P52 | universal (U), category E: every system that is built, changed or operated has a flow of work (changes, tickets, requests) | a visible WIP limit exists, and lead time and WIP are tracked | everything is "in progress" and nothing is finished | depends on P70; strengthens P44, P50 | strong for the relation (mathematical theorem); moderate for the practice | management (operations management, queueing theory) |
| P53 | conditional (C), category E: counterexample: work that can be split into independent parts without communication (for example harvesting a field) | before people are added to late work, a record states the expected training and coordination cost | adding five engineers to a migration two weeks before its deadline | strengthens P67; conflicts with P45 when people are added for redundancy (add early, not late) | moderate; **secondary only** (the book is not online; Brooks himself calls the law an outrageous oversimplification) | management (software project management) |

### F. Verification and review

How to prove that the work is correct.

| ID | Name | Strength | IF (condition) | THEN (action) | BECAUSE (reason) | Example (software/infra) |
| --- | --- | --- | --- | --- | --- | --- |
| P54 | Verification and validation | MUST | always | do verification AND validation, and before handover test that all parts work together against the owner's requirements (commissioning) | passing one does not mean passing the other, and parts that pass alone can fail together | CI tests pass = verification; user acceptance = validation; end-to-end test of a new platform with DNS, certificates, monitoring and backup |
| P55 | Find defects early | SHOULD | always | find and fix defects at the earliest possible stage | the cost of a fix rises at each later stage | lint and tests run in CI before merge |
| P56 | Independent checker | MUST | always | have a checker review the work, and raise the checker's independence with the consequence of failure: self → peer → external organization | authors do not see their own errors, and shared assumptions hide shared errors | required PR approval; external penetration test for high-consequence systems |
| P57 | Test as you operate | SHOULD | a test must show that the system is ready | run the test in the same configuration and conditions as real operation, and test again after every repair | systems that passed every test have failed in operation because operation differed from the test | staging uses the same image digest and Helm values as production |
| P58 | Comparable measurement | SHOULD | measurements are used to compare or decide | measure under stated, controlled reference conditions, report the uncertainty with every result, and calibrate instruments regularly against traceable references | uncontrolled conditions change results, and a result without its uncertainty is incomplete | benchmarks on the same instance type with fixed load and warm-up; report the spread over several runs |
| P59 | Traceability | MUST | the system is safety-critical or regulated | link every requirement in both directions to design and test | standards require proof of complete coverage | requirement ↔ code ↔ test ID in the ticket system |
| P60 | Codes as minimum | MUST | a code or standard exists | meet it as the minimum, then apply the other rules | a code is a minimum, not a maximum | CIS Benchmark for Kubernetes |
| P61 | Qualified procedure and person | SHOULD | the quality of a result cannot be fully checked afterwards | prove the procedure by a test before using it, and qualify each person who performs it | a defect that inspection cannot find must be prevented by a proven procedure and a qualified person | a restore procedure proven by a real restore; only engineers who did a restore drill run production restores |
| P62 | Structured selection of people | SHOULD | you select a person for a job or a promotion | use structured, job-related interviews (the same questions for each candidate, answers rated on scales anchored to job requirements), and add work samples or job-knowledge tests | structured interviews predict job performance better than any other common method (mean validity .42, compared with .19 for unstructured interviews) | every platform-engineer candidate answers the same 6 questions and does the same debugging exercise; two raters score independently |
| P63 | Feedback on the task | SHOULD | you give feedback on a person's or a team's performance | focus the feedback on the task and on how to improve it, not on the person's character or ranking, and check afterwards whether performance improved | feedback improves performance on average, but in over one third of cases it decreased performance | "the runbook missed the rollback step; add it and test it" instead of "you are careless" |

| ID | Class (why) | HOW TO CHECK | VIOLATION (opposite of the rule) | RELATED | Evidence | Source domain |
| --- | --- | --- | --- | --- | --- | --- |
| P54 | universal (U), category F: true for every system | both a test result and a stakeholder acceptance exist | declaring the work done because tests pass | depends on P9; strengthened by P9, P26 | strong | systems engineering, building services (commissioning) |
| P55 | universal (U), category F: true for every system | each check runs at the first stage where it can run | finding defects only in production | strengthens P22, P39; strengthened by P57 | moderate (direction strong; the '10x per stage' factor is weak) | software engineering |
| P56 | universal (U), category F: true for every system | every change has a checker who is not the author, and the checker's independence matches the rigor matrix | the author merges their own change | depends on P2; strengthened by P2, P6, P42, P43, P62; conflicts with P18 | strong | technical drawing (checker in the title block), civil and structural (independent checking) |
| P57 | universal (U), category F: trigger that occurs in the life cycle of every system | the differences between the test setup and real operation are listed, and each one is justified | testing a different build than the one that is deployed | depends on P54; strengthens P55; strengthened by P26, P58, P61 | moderate | aerospace (Test Like You Fly) |
| P58 | universal (U), category F: every engineering decision uses measurements | each benchmark or test report states its reference conditions and the spread or uncertainty of the result | comparing two single benchmark runs from different machines | strengthens P12, P57; strengthened by P19 | strong (standardized in ISO 139 and the GUM; standard text is paid; only the official summary was read) | textile testing (ISO 139), metrology (GUM, traceability) |
| P59 | risk-scaled (R), category F: required by safety standards for safety-critical or regulated systems; costly elsewhere | a traceability report shows no requirement without a test and no test without a requirement | tests that link to no requirement | depends on P9; strengthened by P9, P11 | strong | aerospace, automotive, medical (DO-178C, ISO 26262, IEC 62304) |
| P60 | conditional (C), category F: counterexample: novel technology for which no code exists yet | a compliance scan passes | treating compliance as proof of safety | depends on P2 | strong | pressure vessels (codes and standards) |
| P61 | conditional (C), category F: counterexample: results that can be fully inspected afterwards (a dimension check on a simple part) | each such procedure has a test record, and each performer has a qualification record | a backup procedure that was never restored | depends on P2; strengthens P57, P71; strengthened by P62; conflicts with P7 | strong (required for welding by ASME Section IX; standard text is paid; only the official summary was read) | welding (WPS, PQR, welder qualification) |
| P62 | universal (U), category F: every engineering organization selects people (trigger) | interview guides with fixed questions and rating scales exist and are used; raters score independently before discussion | "culture fit" chat with different questions for each candidate | strengthens P2, P56, P61 | strong (meta-analysis, Journal of Applied Psychology) | management (personnel selection) |
| P63 | universal (U), category F: every engineering organization gives feedback | feedback records name a task and an improvement; the effect is checked at the next review | feedback that compares people or judges character | strengthens P5, P21 | strong for the finding (meta-analysis); the "focus on the task" part rests on the authors' feedback intervention theory and is the author's summary, not a quote | management (performance feedback) |

### G. Change

How to change the system safely.

| ID | Name | Strength | IF (condition) | THEN (action) | BECAUSE (reason) | Example (software/infra) |
| --- | --- | --- | --- | --- | --- | --- |
| P64 | Versioning and change review | MUST | always | version every artifact; before each change, review its technical basis, its safety impact and the procedures it affects, approve it, and inform the affected people before go-live | an unknown version makes failures unreproducible, and an unreviewed change brings in unknown hazards | GitOps: every change is a reviewed pull request; the runbook is updated in the same pull request |
| P65 | Small verified steps | SHOULD | a change carries risk | make the change in small steps, check the result of each step before the next one, and define each check as a hold point (work stops until the check is approved) or a witness point (work continues while the check is observed) | small steps limit how much harm one wrong step can do | canary rollout at 1 % → 10 % → 100 %, with a manual approval gate (hold point) before 100 % |
| P66 | Isolation before work | MUST | people work on a part of the system | isolate that part from all inputs and energy, and lock the isolation so that nobody can restart it unexpectedly | an unexpected restart during work injures people or destroys the work | cordon and drain the node; pause Argo CD auto-sync before manual maintenance |
| P67 | Critical path | SHOULD | work consists of tasks that depend on each other | identify the longest chain of dependent tasks (critical path) and protect it first | a delay on the critical path delays everything; other tasks have slack | in a cluster migration, data sync and DNS cutover are critical; documentation has slack |
| P68 | Observational method | SHOULD | key properties can only be measured during construction or operation | design for the most probable conditions, monitor the real values, and plan trigger levels and backup actions in advance | measuring the real values is more reliable than guessing them in advance | Argo Rollouts analysis that rolls back automatically when the error rate exceeds a trigger level |
| P69 | Guided change | SHOULD | you change how many people work (a reorganization, a new process, a new tool for everyone) | make the need visible, form a group that leads the change, communicate the vision far more often than seems necessary, remove obstacles, plan early visible wins, and continue until the new way is part of daily routine | "skipping steps creates only the illusion of speed" (Kotter); changes declared finished too early fall back | migration to the new CI system: reasons shared, a pilot team, weekly updates, old system switched off only when all teams use the new one |

| ID | Class (why) | HOW TO CHECK | VIOLATION (opposite of the rule) | RELATED | Evidence | Source domain |
| --- | --- | --- | --- | --- | --- | --- |
| P64 | universal (U), category G: true for every system | every change record shows basis, impact review and approval, and the deployed state matches an approved commit | a manual change in production (drift) | strengthens P80; strengthened by P8, P10, P11, P30; conflicts with P18 | strong | all (configuration management), chemical process safety (management of change) |
| P65 | universal (U), category G: trigger that occurs in the life cycle of every system | each risky rollout has defined steps, and each check between steps is marked as hold point or witness point | switching all traffic at once | depends on P70; strengthens P68; strengthened by P20, P67, P69 | moderate | flight testing (build-up approach), construction management (hold points) |
| P66 | universal (U), category G: every system is maintained by people | each maintenance procedure starts with an isolation step and ends with a release step | auto-sync overwrites a manual fix in the middle of an incident | strengthens P39 | strong | industrial safety (lockout/tagout) |
| P67 | universal (U), category G: every project has tasks that depend on each other | each multi-step project plan marks its critical path and the slack of the other tasks | speeding up tasks that have slack while the critical path slips | strengthens P65; strengthened by P53 | moderate | construction management (critical path method) |
| P68 | risk-scaled (R), category G: only where key properties stay uncertain until construction or operation | each monitored value has a trigger level and a planned backup action | discovering at go-live that there is no rollback plan | depends on P65, P70; strengthened by P65, P72 | moderate | geotechnical (observational method) |
| P69 | universal (U), category G: every engineering organization changes how its people work (trigger) | each large change has a written reason, a named leading group, a communication plan, defined early wins and an end criterion ("the old way is switched off") | announcing a change by email and declaring it done | depends on P8, P64; strengthens P65; strengthened by P8 | moderate (practitioner model from case experience; the eight steps have limited empirical testing) | management (change management) |

### H. Operation and maintenance

How to run, watch and maintain the system.

| ID | Name | Strength | IF (condition) | THEN (action) | BECAUSE (reason) | Example (software/infra) |
| --- | --- | --- | --- | --- | --- | --- |
| P70 | Monitoring in operation | SHOULD | the system is in operation | measure its behavior in real use, and alert on symptoms that users feel; where the output stays perfect until a sudden collapse (cliff effect), also monitor the remaining margin | tests before release cannot cover all real conditions, and some systems show no symptom until they fail completely | alerts on latency, traffic, errors and saturation; certificate days left, disk headroom, error budget |
| P71 | Checklists | SHOULD | a critical procedure is rare, complex or done under time pressure | use a short checklist, and confirm each item by pointing at it and saying its status aloud | memory fails under stress | cluster upgrade checklist, incident commander checklist; read out cluster context and namespace before each destructive command |
| P72 | Critical control points | SHOULD | a repeated process has a few steps where control is essential | define those critical control points, rank them by consequence rather than by how often incidents happen, and give each one a limit, monitoring, a predefined corrective action, a record and regular verification in practice | tight control at the essential steps works better than loose control at every step | image-signature admission gate; SLO limit on the payment path with automatic rollback |
| P73 | Response faster than harm | SHOULD | harm develops over time after a fault starts | make sure the time to detect + alert + respond + recover is shorter than the time until harm, with a margin | a response that arrives after the harm is no response | an alert fires when the disk will be full in 4 h, and on-call response takes \< 30 min |
| P74 | Maintenance by failure pattern | SHOULD | you plan maintenance | choose the maintenance method by how each part actually fails: replace on a schedule only what wears out with age, and monitor the condition of everything else | most failures are not linked to age, so scheduled replacement does not prevent them | rotate certificates on a schedule (age-related); alert on disk usage (condition-based); no "just in case" pod restarts |
| P75 | Actionable alerts | SHOULD | a system raises alerts to people | make every alert actionable, and remove or change alerts that nobody acts on | many non-actionable alerts make people ignore all alerts, including the important ones (alert fatigue) | page only on symptoms that need action now; review alert noise every month |
| P76 | Sterile critical phase | SHOULD | work is in a critical phase (cutover, deployment, incident) | allow only the activity and communication that the critical phase needs | distraction during critical phases causes errors | incident channel limited to the response; no unrelated changes during a cutover window |
| P77 | Data as a dependency | SHOULD | behavior depends on data or learned models | version and validate the data like code, monitor for drift, and retrain or re-evaluate when the world changes | data dependencies cost more than code dependencies, and predictions get worse over time | versioned evaluation set for code-review prompts; alerts on shifts in the input distribution |
| P78 | Asset inventory | SHOULD | you operate many assets | keep a complete inventory of all assets, with owner, condition and lifecycle stage | you cannot maintain, secure or decommission what you do not know you have | inventory of clusters, accounts, certificates and images with owners; SBOM per image |
| P79 | Span of control | SHOULD | one person directs other people during operation (incident, cutover, commissioning) | keep the number of people one person directs in a manageable range (guideline: about five), and add group leads above that | a person can coordinate only a limited number of people, and an overloaded coordinator misses actions | an incident commander with 12 responders appoints two group leads (communication, mitigation) |

| ID | Class (why) | HOW TO CHECK | VIOLATION (opposite of the rule) | RELATED | Evidence | Source domain |
| --- | --- | --- | --- | --- | --- | --- |
| P70 | universal (U), category H: trigger that occurs in the life cycle of every system | each service has dashboards and alerts for user-facing symptoms | learning about an outage from users | strengthens P80, P81, P82; strengthened by P19, P26, P75, P77; checks P44, P73 | moderate | site reliability engineering, broadcast (confidence monitoring) |
| P71 | universal (U), category H: every system has rare or critical procedures (restore, upgrade, decommissioning) | each critical procedure has a checklist that is used and is updated after postmortems | an upgrade done from memory | strengthens P25; strengthened by P61, P76, P79; conflicts with P7 | moderate (mixed results: large effect in 8 pilot hospitals, no significant effect in 101 Ontario hospitals) | surgery, railway (pointing and calling) |
| P72 | universal (U), category H: every system is built or operated through repeated processes | each critical control point has a limit, monitoring, a corrective action, records and a recent verification that it works | monitoring everything equally, with no defined limits | depends on P22; strengthens P68; conflicts with P7 | strong | food safety (HACCP), mining (critical control management) |
| P73 | universal (U), category H: every operated system has harms that develop over time (wear, filling, drift) | for each main hazard, the measured detection-plus-response time is shorter than the time until harm | an alert that fires only when the disk is already full | depends on P70; strengthened by P75; conflicts with P83; checked by P70 | moderate | fire protection (ASET > RSET) |
| P74 | universal (U), category H: every system needs maintenance (see P24) | each maintenance task states which failure pattern it addresses | scheduled restarts that hide a memory leak | depends on P22, P70; strengthened by P28, P78 | moderate | aviation maintenance (RCM) |
| P75 | universal (U), category H: every operated system is monitored (P70), and monitoring raises alerts | each alert has an owner and a runbook action, and the share of alerts with no action is measured and kept low | an alert channel with hundreds of messages per day that nobody reads | strengthens P70, P73, P82 | strong (The Joint Commission: "between 85 and 99 percent of alarm signals do not require clinical intervention") | clinical engineering, rail dispatch (alarm fatigue) |
| P76 | universal (U), category H: every project has critical phases (cutover, commissioning, launch) | critical phases are defined, and their communication rules are written down and used | side discussions and parallel deployments during an incident | strengthens P25, P71; strengthened by P79 | strong (FAA regulation since 1981) | aviation (sterile flight deck) |
| P77 | conditional (C), category H: counterexample: a system whose behavior does not depend on data or learned models | data and models have versions, inputs are validated, and drift is monitored with an alert | a model or prompt that silently gets worse over months | depends on P64; strengthens P12, P70 | moderate | data and ML engineering |
| P78 | conditional (C), category H: counterexample: a single, small asset | an automated discovery compares the real assets with the inventory and finds no unknown assets | a forgotten test cluster with public access | strengthens P24, P36, P74; strengthened by P14 | moderate | municipal and infrastructure engineering (asset management, ISO 55000) |
| P79 | conditional (C), category H: counterexample: a system operated by one person or by fully automated control | each incident record lists the roles and the number of people each lead directed; values above the guideline have a reason | one incident commander directly coordinating 20 people in one channel | strengthens P30, P71, P76 | strong for incident management (US federal doctrine NIMS: 1:5 as guideline) | management (incident management) |

### I. Learning

How to learn from failures and anomalies.

| ID | Name | Strength | IF (condition) | THEN (action) | BECAUSE (reason) | Example (software/infra) |
| --- | --- | --- | --- | --- | --- | --- |
| P80 | Blameless root cause analysis | SHOULD | a failure has happened | find the root cause in the system, not a person to blame | blame makes people hide information | blameless postmortem with 5 Whys |
| P81 | Plan-Do-Check-Act | SHOULD | always | repeat the cycle Plan → Do → Check → Act | improvement is a cycle, not a single event | retrospective after each sprint |
| P82 | Investigate anomalies | SHOULD | the system behaves differently from what was expected, even if nobody was harmed | record the anomaly and investigate it before you accept it as normal | ignored warning signs come before major accidents | a flaky test, or an alert that everyone silences |
| P83 | Preserve evidence | SHOULD | a failure has happened | document and preserve the as-found state before you repair or restart anything, and record who handled the evidence (chain of custody) | a repair destroys the evidence needed to find the cause | capture logs, heap dump and disk snapshot before restarting a pod or rolling back |

| ID | Class (why) | HOW TO CHECK | VIOLATION (opposite of the rule) | RELATED | Evidence | Source domain |
| --- | --- | --- | --- | --- | --- | --- |
| P80 | universal (U), category I: trigger that occurs in the life cycle of every system | each failure above a set severity has a postmortem with system-level actions | "operator error" as the final root cause | depends on P64; strengthens P81; strengthened by P5, P10, P64, P70, P82, P83 | moderate | site reliability engineering |
| P81 | universal (U), category I: true for every system | actions from earlier cycles are tracked until they are completed | the same failure happens again with no process change | depends on P70, P80; strengthened by P31, P70, P80 | strong | quality management (ISO 9001) |
| P82 | universal (U), category I: trigger that occurs in the life cycle of every system | each anomaly has a ticket with a decision: fix it, or accept it with a written reason | silencing an alert permanently without an investigation | depends on P4, P70; strengthens P80; strengthened by P4, P5, P15, P19, P33, P70, P75 | moderate | aerospace, accident research (normalization of deviance) |
| P83 | universal (U), category I: trigger that occurs in the life cycle of every system | each incident record lists the evidence captured before the first repair action | restarting the service first and finding no logs afterwards | depends on P11; strengthens P80; conflicts with P73 | strong (required in regulated failure investigation (PHMSA protocol)) | forensic engineering |

## 8. Conflict rules

| ID | IF (condition) | THEN (action) | BECAUSE (reason) | Example (software/infra) | Basis |
| --- | --- | --- | --- | --- | --- |
| K1 | a rule that adds parts (P44, P45, P46, P40, P41, P47) conflicts with P23 (fewer parts) | add those parts only as far as the master rule and the rigor matrix require | both adding and removing parts change failure risk | multi-AZ for production, single-AZ for development | sourced (see P23, P44, P45) |
| K2 | a fix is needed faster than P64 (change review) and P65 (small steps) allow, because of P73 (time until harm) | use a predefined emergency change path with a shorter review, and do the full review afterwards | skipping review without a plan removes every check at the moment of highest stress | a hotfix path with one approver and a mandatory postmortem within 48 h | author's synthesis; no single source |
| K3 | P27 (tolerate variation) seems to conflict with P33 (reject bad input) | tolerate variation within the specification (P27); reject and report input outside the specification (P33) | both rules aim at stable behavior; they differ only in where the boundary lies | accept any valid timestamp format the schema allows; reject a timestamp field that is missing | author's synthesis from Taguchi and RFC 9413 |
| K4 | preserving evidence (P83) would delay recovery beyond the time until harm (P73) | capture evidence automatically and fast; if harm is imminent, restore service first and keep whatever the automation captured | both the evidence and the service matter, and automation makes the trade-off small | crash dumps and log shipping run before every automatic restart | author's synthesis; no single source |
| K5 | P18 (decide reversible decisions fast) conflicts with P64 (change review) and P56 (independent checker) | scale the review depth with reversibility and consequence: reversible and low consequence → peer review or self-check; irreversible or high consequence → full review, P42 and an external checker | both slowness and unreviewed irreversible harm are failures | a new dashboard: the team decides; deleting historical audit logs: two approvers and a legal review | author's synthesis from the Amazon 2015 letter and the master rule |
| K6 | P7 (leave the method to the people doing the work) conflicts with P71 (checklists), P72 (critical control points) and P61 (qualified procedure) | prescribe the method only at critical control points, in qualified or regulated procedures, and where the rigor matrix requires it; everywhere else give intent and constraints | prescribed methods everywhere stop initiative; free methods at critical points remove proven protections | "use the restore checklist" (prescribed); "improve developer onboarding" (intent only) | author's synthesis from ADP 6-0 and P61 |
| K7 | P5 (psychological safety) and P80 (blameless analysis) seem to conflict with accountability (P2, P6, P43, legal duties) | treat honest errors and system weaknesses without blame; treat deliberate violations, reckless behavior and fraud through a defined, fair disciplinary procedure | blame for honest errors hides information; no consequence for deliberate violations destroys trust and controls | a wrong command during an incident → blameless postmortem; bypassing the two-person rule on purpose → disciplinary procedure | author's synthesis; no single source |
| K8 | P21 (specific, challenging goals) conflicts with P19 (indicators are gamed) and with Deming's rejection of numerical goals | use goals for direction and learning; do not tie pay or ranking mechanically to one indicator; pair every target with a counter-indicator | goals raise performance, but a single rewarded number distorts the work | the team goal "halve build time" has a guard "test coverage does not drop"; bonuses are not calculated from the build time | author's synthesis from Locke & Latham, Campbell and Deming |

## 9. Sources by rule

| Rule | Sources |
| --- | --- |
| Master rule | [Primatech: ALARP principle](https://www.primatech.com/technical/alarp-principle) |
| P1 | [NSPE Ethics Reference Guide](https://www.nspe.org/sites/default/files/resources/pdfs/Ethics/EthicsReferenceGuide.pdf) |
| P2 | [NSPE Ethics Reference Guide](https://www.nspe.org/sites/default/files/resources/pdfs/Ethics/EthicsReferenceGuide.pdf) |
| P3 | [NSPE: Sustainability and the PE's obligations](https://www.nspe.org/career-growth/pe-magazine/winter-2023/sustainability-the-pe-s-obligations) |
| P4 | [ISO 13850:2015 Emergency stop function (sample)](https://cdn.standards.iteh.ai/samples/59970/06ad76004ab746ff90b82cf44a8b0752/ISO-13850-2015.pdf); [Directive (EU) 2019/1937 (EUR-Lex)](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L1937); [Wikipedia: Andon (manufacturing)](https://en.wikipedia.org/wiki/Andon_%28manufacturing%29) |
| P5 | [Edmondson: Psychological Safety and Learning Behavior in Work Teams (ASQ 1999, copy)](https://web.mit.edu/curhan/www/docs/Articles/15341_Readings/Group_Performance/Edmondson%20Psychological%20safety.pdf); [Google re:Work: Understand team effectiveness](https://rework.withgoogle.com/intl/en/guides/understand-team-effectiveness) |
| P6 | [NSPE Ethics Reference Guide](https://www.nspe.org/sites/default/files/resources/pdfs/Ethics/EthicsReferenceGuide.pdf); [G20/OECD Principles of Corporate Governance 2023](https://legalinstruments.oecd.org/public/doc/322/322.en.pdf) |
| P7 | [US Army ADP 6-0 Mission Command (2019)](https://irp.fas.org/doddir/army/adp6_0.pdf) |
| P8 | [Kim & Mauborgne: Fair Process (HBR 1997, copy)](https://ieanea.org/wp-content/uploads/2019/05/FairProcessArticle.pdf) |
| P9 | [FDOT Systems Engineering 100](https://wbt.dot.state.fl.us/ois/ITS-SystemsEngineering100/SystemsEngineeringPt2-m2-TRANSCRIPT.pdf) |
| P10 | [SPE: Design for decommissioning (basis of design)](https://onepetro.org/spe/general-information/1423/Design-for-decommissioning); [adr.github.io: Architectural Decision Records](https://adr.github.io/) |
| P11 | [FDA: Electronic Source Data guidance (ALCOA)](https://www.fda.gov/media/85183/download); [§ 239 HGB (text copy, dejure.org)](https://dejure.org/gesetze/HGB/239.html) |
| P12 | [OSTI: A Perspective on Model Validation and Validated Models (keynote)](https://www.osti.gov/servlets/purl/1109271); [Flyvbjerg: From Nobel Prize to Project Management (2006)](https://arxiv.org/pdf/1302.3642); [Wikipedia: V&V of computer simulation models](https://en.wikipedia.org/wiki/Verification_and_validation_of_computer_simulation_models); [Wikipedia: Fermi problem](https://en.wikipedia.org/wiki/Fermi_problem); [Wikipedia: All models are wrong (Box & Draper 1987)](https://en.wikipedia.org/wiki/All_models_are_wrong) |
| P13 | [Sandve et al.: Ten Simple Rules for Reproducible Computational Research](https://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1003285) |
| P14 | [SLSA v1.0: Provenance](https://slsa.dev/spec/v1.0/provenance); [Wikipedia: Mill test report](https://en.wikipedia.org/wiki/Mill_test_report) |
| P15 | [UN: Rio Declaration on Environment and Development (1992)](https://icsid.worldbank.org/sites/default/files/parties_publications/C8394/Respondent%27s%20documents/RL%20-%20Legal%20Authorities/RL-0150-ENG%201992-06-13.pdf); [Wikipedia: Precautionary principle](https://en.wikipedia.org/wiki/Precautionary_principle) |
| P16 | [Sobek, Ward, Liker: Toyota's Principles of Set-Based Concurrent Engineering](https://www.gapimprove.org/_files/ugd/cd8b34_2d04bd540ca04019986c3ba54ae8631e.pdf?index=true) |
| P17 | [NASA: Technology Readiness Levels](https://www.nasa.gov/directorates/somd/space-communications-navigation-program/technology-readiness-levels/); [Wikipedia: Technology readiness level](https://en.wikipedia.org/wiki/Technology_readiness_level) |
| P18 | [Amazon 2015 letter to shareholders (SEC filing)](https://www.sec.gov/Archives/edgar/data/1018724/000119312516530910/d168744dex991.htm) |
| P19 | [Campbell: Assessing the Impact of Planned Social Change (reprint, J. MultiDisciplinary Evaluation 2011; original 1976/1979)](https://jmde.journals.publicknowledgeproject.org/index.php/jmde_1/article/view/297); [Wikipedia: Campbell's law](https://en.wikipedia.org/wiki/Campbell%27s_law) |
| P20 | [Staw: Knee-deep in the big muddy (1976, copy)](https://www.gwern.net/doc/psychology/cognitive-bias/sunk-cost/1976-staw.pdf); [Purple Griffon: PRINCE2 7th edition principles](https://purplegriffon.com/blog/prince2-7th-edition-principles) |
| P21 | [Locke & Latham: Building a practically useful theory of goal setting (Am. Psychol. 2002, copy)](https://goal-lab.psych.umn.edu/orgpsych/2020/readings/5.%20Motivation/Locke%20&%20Latham%20(2002).pdf); [The W. Edwards Deming Institute: 14 Points](https://deming.org/explore/fourteen-points/) |
| P22 | [BMJ Qual Saf / PMC: FMEA outputs - are they valid?](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3405478/); [Leveson & Thomas: STPA Handbook](https://www.flighttestsafety.org/images/STPA_Handbook.pdf); [EBSCO: FMEA](https://www.ebsco.com/research-starters/social-sciences-and-humanities/failure-mode-and-effects-analysis-fmea); [Swift Navigation: What is SOTIF (ISO 21448)?](https://www.swiftnav.com/glossary/what-is-safety-of-the-intended-functionality-sotif) |
| P23 | [Hoare: The Emperor's Old Clothes, Turing Award lecture (CACM 1981)](https://worrydream.com/refs/Hoare_1981_-_The_Emperors_Old_Clothes.pdf); [Grokipedia: KISS principle](https://grokipedia.com/page/KISS_principle) |
| P24 | [IAEA: Decommissioning by design](https://www.iaea.org/bulletin/decommissioning-by-design-how-advanced-reactors-are-designed-with-disposal-in-mind); [NASA: Design for maintenance](https://ntrs.nasa.gov/api/citations/20240004739/downloads/Design%20for%20Maintenance%20DoD%20HFE%20TAG%2076%20041724.pdf); [JPT: Engineering for decommissioning](https://jpt.spe.org/engineering-decommissioning-during-project-design-reduces-costs) |
| P25 | [FDA: Applying Human Factors and Usability Engineering to Medical Devices (guidance)](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/applying-human-factors-and-usability-engineering-medical-devices); [MD+DI: Human factors engineering](https://www.mddionline.com/design-engineering/making-the-most-of-human-factors-usability-engineering); [egtechnology: Usability example](https://www.egtechnology.co.uk/human-factors-and-usability-engineering-a-must-or-a-good-to-have-part-1/); [Wikipedia: Anthropometry](https://en.wikipedia.org/wiki/Anthropometry) |
| P26 | [IEEE 1149.1: Test Access Port and Boundary-Scan Architecture](https://standards.ieee.org/ieee/1149.1/4484/); [Wikipedia: Design for testing](https://en.wikipedia.org/wiki/Design_for_testing) |
| P27 | [Penn State: Taguchi's Robust Design Method](https://www.me.psu.edu/simpson/courses/ie466/ie466.robust.handout.pdf); [PMC: Engineering approach for sustainable biological systems](https://pmc.ncbi.nlm.nih.gov/articles/PMC2610168/) |
| P28 | [FAA AC 25.1309-1A: System Design and Analysis (fail-safe design concept)](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_25.1309-1A.pdf); [WHO/ILO: Long working hours increasing deaths (2021)](https://www.who.int/news/item/17-05-2021-long-working-hours-increasing-deaths-from-heart-disease-and-stroke-who-ilo); [Pencavel: The Productivity of Working Hours (IZA DP 8129, 2014)](https://docs.iza.org/dp8129.pdf); [Wikipedia: Fatigue (material)](https://en.wikipedia.org/wiki/Fatigue_%28material%29); [Wermac: Corrosion allowance](https://www.wermac.org/materials/corrosion_allowance.html) |
| P29 | [MIL-STD-889D: Dissimilar metals, galvanic compatibility (2021)](https://corrdesa.com/wp-content/uploads/2024/04/MIL-STD-889D-2021-Release.pdf); [ISO 10993-1: Biological evaluation of medical devices](https://www.iso.org/standard/44908.html); [Wikipedia: Galvanic corrosion](https://en.wikipedia.org/wiki/Galvanic_corrosion); [Wikipedia: Biocompatibility](https://en.wikipedia.org/wiki/Biocompatibility) |
| P30 | [Slocum: Kinematic couplings, a review of design principles and applications (MIT)](https://web.mit.edu/2.70/Reading%20Materials/Kinematic%20coupling%20review%20article.pdf); [FEMA: National Incident Management System, 3rd ed. (2017)](https://training.fema.gov:443/EMIWeb/IS/IS700b/Handouts/National_Incident_Management%20System_Third%20Edition_October_2017.pdf); [Wikipedia: Kinematic coupling (exact constraint)](https://en.wikipedia.org/wiki/Kinematic_coupling) |
| P31 | [Nobel Prize in Chemistry 2018: press release](https://www.nobelprize.org/prizes/chemistry/2018/press-release/); [Wikipedia: Directed evolution](https://en.wikipedia.org/wiki/Directed_evolution); [Molecular Devices: Design-build-test-learn cycle](https://www.moleculardevices.com/applications/synthetic-biology/dbtl-approach) |
| P32 | [Saltzer, Reed, Clark: End-to-End Arguments in System Design (1984)](https://web.mit.edu/Saltzer/www/publications/endtoend/endtoend.pdf); [Wikipedia: End-to-end principle](https://en.wikipedia.org/wiki/End-to-end_principle) |
| P33 | [RFC 9413: Maintaining Robust Protocols (2023)](https://www.rfc-editor.org/rfc/rfc9413.html); [NASA: Mars Climate Orbiter Mishap Investigation Board, Phase I Report (1999)](https://discovery.larc.nasa.gov/PDF_FILES/MCO_report_2.pdf); [Wikipedia: Robustness principle (incl. RFC 9413 critique)](https://en.wikipedia.org/wiki/Robustness_principle); [Wikipedia: Mars Climate Orbiter](https://en.wikipedia.org/wiki/Mars_Climate_Orbiter) |
| P34 | [ASTM C1683: Size Scaling of Tensile Strengths Using Weibull Statistics for Advanced Ceramics](https://store.astm.org/c1683-10r24.html); [Wikipedia: Weibull modulus](https://en.wikipedia.org/wiki/Weibull_modulus); [Wikipedia: Size effect on structural strength](https://en.wikipedia.org/wiki/Size_effect_on_structural_strength) |
| P35 | [Conway: How Do Committees Invent? (1968)](https://www.melconway.com/Home/Committees_Paper.html) |
| P36 | [NIST CSRC Glossary: least privilege (CNSSI 4009, SP 800-53 Rev. 5)](https://csrc.nist.gov/glossary/term/least_privilege); [Jamf: NIST definition of least privilege](https://www.jamf.com/blog/zero-trust-vs-least-privilege/) |
| P37 | [FAA AC 25.1309-1A: System Design and Analysis (fail-safe design concept)](https://www.faa.gov/documentLibrary/media/Advisory_Circular/AC_25.1309-1A.pdf); [PatSnap: Fail-safe design](https://eureka.patsnap.com/article/what-is-a-fail-safe-design-principles-and-best-practices); [The Next Web: Werner Vogels, "Everything fails all the time"](https://thenextweb.com/news/werner-vogels-everything-fails-all-the-time) |
| P38 | [CDC/NIOSH: Hierarchy of controls](https://www.cdc.gov/niosh/hierarchy-of-controls/about/index.html); [OSHA Technical Manual: Noise](https://www.osha.gov/otm/section-3-health-hazards/chapter-5); [Wikipedia: Inherent safety](https://en.wikipedia.org/wiki/Inherent_safety) |
| P39 | [FHWA: Zero deaths and the Safe System approach](https://highways.dot.gov/safety/zero-deaths); [UserSolutions: Poka-yoke](https://usersolutions.com/blog/poka-yoke-error-proofing) |
| P40 | [JPT: Robust well barrier and well integrity management](https://jpt.spe.org/robust-well-barrier-and-well-integrity-management); [ScienceDirect: Least privilege and defense in depth](https://www.sciencedirect.com/topics/computer-science/principle-of-least-privilege); [Palo Alto Networks: Defense in depth](https://www.paloaltonetworks.com/cyberpedia/what-is-defense-in-depth); [Wikipedia: Multi-barrier approach](https://en.wikipedia.org/wiki/Multi-barrier_approach) |
| P41 | [IMO SOLAS Chapter II-1, subdivision and stability (text via imorules.com)](https://www.imorules.com/solas/02_chapter_II-1.html); [Wikipedia: Compartment (ship)](https://en.wikipedia.org/wiki/Compartment_%28ship%29) |
| P42 | [NIST SP 800-53 Rev. 5, AC-3(2) Dual Authorization (text via CSF Tools)](https://csf.tools/reference/nist-sp-800-53/r5/ac/ac-3/ac-3-2/); [Wikipedia: Two-man rule](https://en.wikipedia.org/wiki/Two-man_rule) |
| P43 | [NIST CSRC Glossary: separation of duty (SP 800-192)](https://csrc.nist.gov/glossary/term/separation_of_duty) |
| P44 | [Univ. of Portland: Fail-safe designs and factor of safety](https://faculty.up.edu/lulay/MEStudentPage/failsafe.pdf); [Linda Green: Queueing theory and modeling](https://business.columbia.edu/sites/default/files-efs/pubfiles/5474/queueing%20theory%20and%20modeling.pdf); [NASA GSFC-STD-1000 Rev H (resource margins)](https://standards.nasa.gov/sites/default/files/standards/GSFC/H/0/GSFC-STD-1000RevH_Approved.pdf); [Little: Little's Law as Viewed on Its 50th Anniversary (Operations Research 2011, reprint)](https://projectproduction.org/journal/reprint-littles-law-as-viewed-on-its-50th-anniversary/); [Wikipedia: Return period](https://en.wikipedia.org/wiki/Return_period); [Wikipedia: Derating](https://en.wikipedia.org/wiki/Derating); [Wikipedia: All models are wrong (Box & Draper 1987)](https://en.wikipedia.org/wiki/All_models_are_wrong) |
| P45 | [USPTO: Materials-based failure analysis in electronic devices](https://image-ppubs.uspto.gov/dirsearch-public/print/downloadPdf/8285522); [von Neumann: Lectures on Probabilistic Logics and the Synthesis of Reliable Organisms from Unreliable Components (Caltech, 1952)](https://static.ias.edu/pitp/archive/2012files/Probabilistic_Logics.pdf); [ScienceDirect: Fail-safe design](https://www.sciencedirect.com/topics/materials-science/fail-safe-design); [SINTEF: N-1 isn't always enough](https://blog.sintef.com/sintefenergy/energy-systems/electricity-supply-security-n-1-isnt-always-enough/); [Wikipedia: Quantum error correction](https://en.wikipedia.org/wiki/Quantum_error_correction) |
| P46 | [arXiv: Safety design in autonomous vehicles](https://arxiv.org/pdf/2412.08862) |
| P47 | [NERC PRC-006-5: Automatic Underfrequency Load Shedding](https://www.nerc.com/globalassets/standards/reliability-standards/prc/prc-006-5.pdf); [Wikipedia: Load shedding](https://en.wikipedia.org/wiki/Load_shedding) |
| P48 | [Åström & Murray: Feedback Systems, section 1.5 On-Off Control](https://introcontrol.mit.edu/_static/fall21/extras/Feedback%20Systems%20Murray.pdf); [Wikipedia: Deadband](https://en.wikipedia.org/wiki/Deadband) |
| P49 | [Duranton & Turner: The Fundamental Law of Road Congestion (AER 2011)](https://www.aeaweb.org/articles?id=10.1257/aer.101.6.2616); [Wikipedia: Induced demand](https://en.wikipedia.org/wiki/Induced_demand) |
| P50 | [Theory of Constraints Institute: Five Focusing Steps](https://www.tocinstitute.org/five-focusing-steps.html); [Wikipedia: Theory of constraints](https://en.wikipedia.org/wiki/Theory_of_constraints) |
| P51 | [MIT Sloan Management Review: The Bullwhip Effect in Supply Chains](https://sloanreview.mit.edu/article/the-bullwhip-effect-in-supply-chains/); [Lee, Padmanabhan, Whang: Information Distortion in a Supply Chain (Management Science 1997)](https://courses.ie.bilkent.edu.tr/ie102/wp-content/uploads/sites/12/2019/02/Lee-Padmanabhan-Whang-1997-MS.pdf); [Wikipedia: Bullwhip effect](https://en.wikipedia.org/wiki/Bullwhip_effect) |
| P52 | [Little: Little's Law as Viewed on Its 50th Anniversary (Operations Research 2011, reprint)](https://projectproduction.org/journal/reprint-littles-law-as-viewed-on-its-50th-anniversary/) |
| P53 | [Reinertsen: Is it always a bad idea to add resources to a late project? (Electronic Design 2000)](https://www.electronicdesign.com/archive/article/21760483/is-it-always-a-bad-idea-to-add-resources-to-a-late-project); [The Jargon File: Brooks's Law](http://www.catb.org/jargon/html/B/Brookss-Law.html) |
| P54 | [arXiv: V&V in Systems of Systems](https://arxiv.org/pdf/1311.3626); [Wikipedia: Building commissioning](https://en.wikipedia.org/wiki/Building_commissioning) |
| P55 | [arXiv: Revisiting cost-to-fix](https://arxiv.org/pdf/1609.04886) |
| P56 | [Singapore: Building Control (Accredited Checkers and Accredited Checking Organisations) Regulations](https://sso.agc.gov.sg/SL/BCA1989-RG2?DocDate=20121130); [IIA: The Three Lines Model (2020)](https://www.theiia.org/globalassets/documents/resources/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense-july-2020/three-lines-model-updated-english.pdf); [Regulation (EU) No 537/2014, Article 17 (text copy)](https://www.charteredaccountants.ie/chariotindex/text/ec_2014_537/17.html); [UK MoD: Red Teaming Handbook, 3rd ed. (2021)](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1027158/20210625-Red_Teaming_Handbook.pdf); [LibreTexts: Peer review in design](https://eng.libretexts.org/Courses/Western_Technical_College/Inventor_Parametric_Design:_Level_1_%28Bahl%29/01:_Technical_Drawings/1.02:_Peer_Review_Process_and_Markup_Drawings/1.2.01:_The_Role_of_Peer_Review_in_Engineering_Design); [EPCLand: Checking of design](https://epcland.com/checking-of-design-engineering-checklist/) |
| P57 | [Aerospace Corp: Test Like You Fly Process Guide](https://aerospace.org/sites/default/files/2024-06/TOR-2014-02537-REV%20A%20-%20The%20Test%20Like%20You%20Fly%20Process%20Guide%20for%20Space,%20Launch,%20and%20Ground%20Systems.pdf) |
| P58 | [ISO 139:2005 Textiles - standard atmospheres (sample)](https://cdn.standards.iteh.ai/samples/35179/19d75d1dcdd147d4b630728954acc86d/ISO-139-2005.pdf); [Chiuvention: Why fabric test results vary with weather](https://chiuvention.com/blog/why-fabric-test-results-vary-with-weather-solved-by-a-temperature-and-humidity-chamber); [Wikipedia: Measurement uncertainty](https://en.wikipedia.org/wiki/Measurement_uncertainty); [Wikipedia: Metrological traceability](https://en.wikipedia.org/wiki/Metrological_traceability) |
| P59 | [NASA Software Engineering Handbook: SWE-052 Bidirectional Traceability (NPR 7150.2)](https://swehb.nasa.gov/spaces/SWEHBVC/pages/50888903/SWE-052+-+Bidirectional+Traceability?showComments=true&showCommentArea=true); [Stell: Requirements traceability](https://stell-engineering.com/blog/what-is-requirement-traceability) |
| P60 | [Univ. of Portland: Fail-safe designs and factor of safety](https://faculty.up.edu/lulay/MEStudentPage/failsafe.pdf) |
| P61 | [ASME BPVC Section IX: Welding, Brazing and Fusing Qualifications](https://www.asme.org/codes-standards/find-codes-standards/bpvc-ix-bpvc-section-ix-welding-brazing-fusing-qualifications); [Wikipedia: Welding Procedure Specification](https://en.wikipedia.org/wiki/Welding_Procedure_Specification) |
| P62 | [Sackett, Zhang, Berry, Lievens: Revisiting meta-analytic estimates of validity in personnel selection (J. Appl. Psychol., copy)](https://www.gwern.net/doc/statistics/meta-analysis/2021-sackett.pdf) |
| P63 | [Kluger & DeNisi: The effects of feedback interventions on performance (Psychol. Bull. 1996)](https://cris.huji.ac.il/en/publications/the-effects-of-feedback-interventions-on-performance-a-historical/) |
| P64 | [arXiv: Controls and machine protection](https://arxiv.org/pdf/1608.02836); [arXiv: Agentic Configuration Management](https://arxiv.org/pdf/2608.11166); [OSHA 29 CFR 1910.119 (management of change)](https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.119) |
| P65 | [Google SRE Workbook: Canarying Releases](https://sre.google/workbook/canarying-releases/); [Flight Test Fact: The build-up approach](https://flighttestfact.com/the-build-up-approach/); [Quality Engineers Guide: Hold point and witness point](https://www.qualityengineersguide.com/what-is-witness-point-and-hold-point) |
| P66 | [OSHA: Control of hazardous energy (lockout/tagout)](https://www.osha.gov/control-hazardous-energy) |
| P67 | [Kelley: The Origins of CPM, a Personal History (PMI)](https://www.pmi.org/learning/library/origins-cpm-personal-history-3762); [Wikipedia: Critical path method](https://en.wikipedia.org/wiki/Critical_path_method) |
| P68 | [ICE: The observational method](https://knowledgehub.ice.org.uk/cpd/delivery-exc/observational-method/) |
| P69 | [Kotter: Leading Change — Why Transformation Efforts Fail (HBR 1995, copy)](https://fcm.ucsf.edu/sites/g/files/tkssra17611/files/Kotter_WhyTransformationEffortsFail.pdf) |
| P70 | [Google SRE: Monitoring distributed systems](https://sre.google/sre-book/monitoring-distributed-systems/); [TV Technology: Confidence monitors](https://www.tvtechnology.com/opinions/confidence-monitors) |
| P71 | [ICES: Ontario checklist study (2014)](https://www.ices.on.ca/news-releases/study-shows-introduction-of-surgical-safety-checklists-in-ontario-have-not-reduced-post-operative-mortality-or-complications/); [ScienceDaily: WHO surgical checklist study (2009)](https://www.sciencedaily.com/releases/2009/01/090114172304.htm); [Wikipedia: Pointing and calling](https://en.wikipedia.org/wiki/Pointing_and_calling) |
| P72 | [FDA: HACCP Principles & Application Guidelines](https://www.fda.gov/food/hazard-analysis-critical-control-point-haccp/haccp-principles-application-guidelines); [Mining Weekly: ICMM critical control management guide](https://www.miningweekly.com/article/icmm-updates-critical-control-management-guide-to-strengthen-mining-safety-2026-04-29) |
| P73 | [Cooper: Estimating Safe Available Egress Time from Fires (NBSIR 80-2172, 1981)](https://nvlpubs.nist.gov/nistpubs/Legacy/IR/nbsir80-2172.pdf); [BCI Good Practice Guidelines 2018 (with ISO 22301:2019 definitions)](https://www.thebci.org/static/cf455e45-b2c2-4a44-b77da7c99fd6df77/BCI-GPG-2018-Edition.pdf); [Fire Risk Assessment Network: ASET and RSET](https://fire-risk-assessment-network.com/blog/aset-rset/) |
| P74 | [Nowlan & Heap: Reliability-Centered Maintenance (1978)](https://web.archive.org/web/20240905171929/https://www.omdec.com/wikifiles/nowlanHeap.pdf); [Wikipedia: Reliability-centered maintenance](https://en.wikipedia.org/wiki/Reliability-centered_maintenance) |
| P75 | [The Joint Commission: Sentinel Event Alert 50, Medical device alarm safety (2013)](https://www.kff.org/wp-content/uploads/sites/2/2013/04/sea_50_alarms_4_5_13_final1.pdf); [Wikipedia: Alarm fatigue](https://en.wikipedia.org/wiki/Alarm_fatigue) |
| P76 | [eCFR: 14 CFR 121.542, Flight crewmember duties](https://www.ecfr.gov/current/title-14/chapter-I/subchapter-G/part-121/subpart-T/section-121.542); [Wikipedia: Sterile flight deck rule](https://en.wikipedia.org/wiki/Sterile_flight_deck_rule) |
| P77 | [Sculley et al.: Hidden Technical Debt in ML Systems (NeurIPS 2015)](https://proceedings.neurips.cc/paper_files/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf); [Wikipedia: Concept drift](https://en.wikipedia.org/wiki/Concept_drift) |
| P78 | [CIS Control 1: Inventory and Control of Enterprise Assets](https://www.cisecurity.org/controls/inventory-and-control-of-enterprise-assets); [Wikipedia: Asset management (incl. ISO 55000)](https://en.wikipedia.org/wiki/Asset_management) |
| P79 | [FEMA: National Incident Management System, 3rd ed. (2017)](https://training.fema.gov:443/EMIWeb/IS/IS700b/Handouts/National_Incident_Management%20System_Third%20Edition_October_2017.pdf) |
| P80 | [Google SRE: Postmortem culture](https://sre.google/workbook/postmortem-culture/) |
| P81 | [ASQ: PDCA Cycle](https://asq.org/quality-resources/pdca-cycle); [ISO Central: PDCA](https://isocentral.org/resources/what-is-plan-do-check-act) |
| P82 | [National Academies: Accident precursor analysis](https://www.nationalacademies.org/read/11061/chapter/2); [Wikipedia: Normalization of deviance](https://en.wikipedia.org/wiki/Normalization_of_deviance) |
| P83 | [PHMSA: Metallurgical Laboratory Failure Examination Protocol](https://www.phmsa.dot.gov/sites/phmsa.dot.gov/files/docs/incident-reporting/accident-investigation-division/70066/metallurgical-laboratory-failure-examination-protocol.pdf); [Wikipedia: Forensic engineering](https://en.wikipedia.org/wiki/Forensic_engineering) |


## 10. Management form of each rule

Each row states what a rule means when the "system" is an organization, a team, a project or a process. The IF / THEN / BECAUSE text in section 7 stays valid. Rules P5–P8, P18–P21, P35, P43, P52, P53, P62, P63, P69, P79 come from management sources and are already written for organizations; they are not repeated here. "Cross-reference only" in the Sources column means no management source was found; the transfer is the author's judgment (adoption gap, see section 1).
### A. Responsibility

| ID | Rule name | Management name | THEN (management form) | Example (platform team / organization) | Sources (management) | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| P1 | Public safety first | Duty of care and ethics first | put the safety, health and legal rights of people (customers, the public, the own people) above cost, schedule and convenience | the manager stops a launch that would process personal data without a legal basis | [ISO 9001:2026 launch: "ethical behaviour"](https://www.iso.org/news/2026/09/ISO9001-2026); [ISO 45001:2018](https://www.iso.org/standard/63787.html) | strong |
| P2 | Work within competence | Competence management | give work only to people competent for it, and train them or add an expert otherwise | a team lead without labour-law knowledge asks HR before changing on-call rules | [COSO ERM principle 5](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf); [ADP 6-0: principle "Competence"](https://irp.fas.org/doddir/army/adp6_0.pdf) | strong |
| P3 | Sustainability | Environmental and social sustainability | include environmental and social impact in decisions across the whole life cycle, including procurement | cloud cost and energy reports reviewed with the budget | [ISO 14001:2026 (via 2015 page)](https://www.iso.org/standard/60857.html); [ISO 20400:2017](https://www.iso.org/standard/63026.html); [PMBOK 8: "integrate sustainability"](https://www.pmi.org/standards/pmbok/about) | strong (standard text is paid; only the official summary was read) |
| P4 | Stop authority | Speak-up and stop-the-line | let every person raise a concern or stop work without permission and without retaliation; provide a confidential reporting channel and follow up every report | any engineer may pause a release; an anonymous channel exists for legal and ethical concerns | [Directive (EU) 2019/1937, Art. 8(3) and recital 88](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L1937); [Deming point 8](https://deming.org/explore/fourteen-points/); [Toyota: jidoka](https://global.toyota/en/company/vision-and-philosophy/production-system/) | strong (EU law: internal channels required for private entities with 50 or more workers) |

### B. Knowledge and decisions

| ID | Rule name | Management name | THEN (management form) | Example | Sources (management) | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| P9 | Measurable requirements | Measurable objectives | write each objective with a measure, a target, a deadline and one owner, and link it to a customer or stakeholder need | "reduce median time to provision a namespace from 3 days to 1 hour by Q2", owner named | [NIMS: management by objectives](https://training.fema.gov:443/EMIWeb/IS/IS700b/Handouts/National_Incident_Management%20System_Third%20Edition_October_2017.pdf); [Locke & Latham 2002](https://goal-lab.psych.umn.edu/orgpsych/2020/readings/5.%20Motivation/Locke%20&%20Latham%20(2002).pdf) | strong |
| P10 | Decision records | Decision log | record each significant management decision with its reason, the alternatives considered and the owner | a decision log entry: "move to a shared on-call rotation; rejected: per-team rotation, because…" | [COSO ERM principle 8 "Evaluates Alternative Strategies"](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf); [ISO 30401:2018](https://www.iso.org/standard/68683.html) (supports) | moderate |
| P11 | Trustworthy evidence | Proper bookkeeping and records | keep business records so that no change hides the original entry, and so that the organization can demonstrate compliance | budget changes are new entries with author and date, not overwrites | [§ 239(3) HGB](https://dejure.org/gesetze/HGB/239.html); [GDPR Art. 5(2)](https://gdpr-info.eu/art-5-gdpr/); [ISO 15489-1:2016](https://www.iso.org/standard/62542.html) | strong (German law for bookkeeping) |
| P12 | Model validity | Forecast validity (outside view) | check each estimate or business case against the real outcomes of a reference class of similar past projects, not only against the own plan | the migration estimate is compared with the last five migrations, which overran by 40 % on average | [Flyvbjerg 2006](https://arxiv.org/pdf/1302.3642) | strong (peer-reviewed) |
| P13 | Automated reproducible results | Reproducible reporting | produce management figures (KPIs, budgets, forecasts) through automated, documented steps from named data sources | the DORA dashboard is generated from pipeline data, not from a hand-edited spreadsheet | [COSO ERM principle 18 "Leverages Information Systems"](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf) | moderate |
| P14 | Provenance | Supplier due diligence | know each supplier and the risks in its own supply chain, and act on what you find | a SaaS vendor's sub-processors and their data locations are known before signing | [OECD Due Diligence Guidance (2018)](https://www.oecd.org/en/publications/oecd-due-diligence-guidance-for-responsible-business-conduct_15f5f4b3-en.html) | strong (OECD guidance; national supply-chain laws exist) |
| P15 | Precaution | Precautionary management action | when serious or irreversible harm is credible but unproven, take a proportionate protective step now | payments to a supplier are paused while a fraud warning is checked | cross-reference only | moderate |
| P16 | Set-based design | Keep strategic options open | evaluate several strategies or options in parallel and drop weak ones as evidence arrives | two vendors run a paid pilot before one contract is signed | [COSO ERM principle 8](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf) | moderate |
| P17 | Technology maturity | Maturity of new tools, vendors and methods | assess the maturity of a new tool, vendor or management method before it carries a critical process | a start-up vendor is not chosen for the payroll process without an exit plan | [ISO 56001:2024](https://www.iso.org/standard/79278.html) (supports) | moderate |

### C. Design (organization and process design)

| ID | Rule name | Management name | THEN (management form) | Example | Sources (management) | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| P22 | Failure and interaction analysis | Pre-mortem and portfolio risk view | before starting, assume the initiative has failed and list the reasons; also list how parallel initiatives can interfere with each other | a pre-mortem before a cluster migration finds that two teams plan the same freeze window | [Klein 2007 (HBR)](https://hbr.org/2007/09/performing-a-project-premortem); [COSO ERM principles 10 and 14](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf) | moderate |
| P23 | Simplicity and modularity | Simple structures, few priorities | use the fewest layers, rules, meetings and priorities that meet the objective; stop work that is not needed | one team backlog with one ranked list, not three parallel priority lists | [Agile principle 10](https://agilemanifesto.org/principles) | moderate |
| P24 | Lifecycle and decommissioning | Plan the exit at the start | when starting a contract, project, product, data collection or role, plan how it ends: exit clause, closure, sunset, deletion, handover | every vendor contract has an exit and data-return clause; personal data has a deletion date | [GDPR Art. 5(1)(e) storage limitation](https://gdpr-info.eu/art-5-gdpr/) | strong (law for personal data) |
| P25 | Human factors | Work designed for real people | design roles, processes and tools for real people under real conditions: clear roles, plans and goals, and a workload people can carry | each team member can name their role and the team's current goal | [Google re:Work: "Structure and clarity"](https://rework.withgoogle.com/intl/en/guides/understand-team-effectiveness) | moderate |
| P26 | Design for testability | Auditable processes | design each process so that its controls leave evidence that a reviewer can sample | access approvals are stored as tickets that an auditor can sample | [IIA Three Lines principle 4](https://www.theiia.org/globalassets/documents/resources/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense-july-2020/three-lines-model-updated-english.pdf) (supports) | moderate |
| P27 | Robustness | Robust plans | make plans that still work when assumptions vary within a credible range | the roadmap still delivers its top objective if one engineer leaves | cross-reference only | moderate |
| P28 | Accumulated degradation | Sustainable pace | limit sustained overtime and track debt that builds up slowly (overtime, deferred maintenance, technical debt) | on-call load and overtime are reviewed monthly; no one works above 48 h per week as a pattern | [WHO/ILO 2021](https://www.who.int/news/item/17-05-2021-long-working-hours-increasing-deaths-from-heart-disease-and-stroke-who-ilo); [Pencavel 2014](https://docs.iza.org/dp8129.pdf); [Agile principle 8](https://agilemanifesto.org/principles) | strong |
| P29 | Compatibility | Compatibility of teams, processes and cultures | before merging teams, organizations or processes, check that they are compatible, and plan the integration of the differences | before two platform teams merge, their on-call rules and release processes are compared | cross-reference only | moderate |
| P30 | Exact constraint | Single point of accountability, unity of command | give each objective, decision, risk and process exactly one accountable owner; each person reports to one person for a given task | one product owner per backlog; one incident commander per incident | [NIMS: "Unity of command means that each individual only reports to one person."](https://training.fema.gov:443/EMIWeb/IS/IS700b/Handouts/National_Incident_Management%20System_Third%20Edition_October_2017.pdf); [PRINCE2 principle 3](https://purplegriffon.com/blog/prince2-7th-edition-principles) | strong (US federal doctrine) |
| P31 | Design by selection | Controlled experiments | where you cannot predict which option works, test variants with real users, keep the best, repeat | two onboarding flows for the developer portal are A/B-tested | [Kohavi & Thomke 2017](https://web-docs.stern.nyu.edu/executive/The%20Surprising%20Power%20of%20Online%20Experiments.pdf) | strong |
| P32 | End-to-end | End-to-end ownership of the customer outcome | let the unit closest to the customer verify that the customer outcome is reached, instead of trusting each department's local result | the platform team measures time-to-first-deploy for product teams, not only its own ticket times | [Deming point 9](https://deming.org/explore/fourteen-points/) | moderate |
| P33 | Strict interfaces | Explicit agreements between units | state what each unit delivers to the next (contract, service level, definition of ready) and return incomplete handovers instead of silently fixing them | a request without a cost centre is returned, not guessed | [ISO/IEC 20000-1:2018](https://www.iso.org/standard/70636.html) (supports) | moderate |
| P34 | Weakest-link scaling | Rare events become frequent with size | as the organization grows, expect rare events (fraud, misconduct, key-person loss) to happen regularly, and scale controls with size | at 500 people, a once-per-500-person-years event happens about every year | cross-reference only | moderate |

### D. Protection

| ID | Rule name | Management name | THEN (management form) | Example | Sources (management) | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| P36 | Least privilege | Need-to-know and limits of authority | give each person only the information, data and decision authority their role needs; set written limits of authority | spending authority of team leads limited to an amount; personal data visible only to HR | [GDPR Art. 5(1)(c) data minimisation](https://gdpr-info.eu/art-5-gdpr/) | strong (law for personal data) |
| P37 | Fail-safe | Default decisions and fallback authority | define in advance what happens when a decision-maker is absent or a plan fails: deputy, default option, transfer of command | if the change approver is absent, the default is "no change", not "change without approval" | [NIMS: "Establishment and Transfer of Command"](https://training.fema.gov:443/EMIWeb/IS/IS700b/Handouts/National_Incident_Management%20System_Third%20Edition_October_2017.pdf) | moderate |
| P38 | Hierarchy of controls | Hierarchy of controls for management risks | eliminate the risky activity, then substitute, then use system-enforced controls, then policies and training, and personal care last | instead of a policy "do not share credentials", remove shared accounts | [ISO 45001 clause 8.1.2 (secondary text)](https://blog.auditortrainingonline.com/blog/iso-45001-clause-8-1-2) | strong (required in ISO 45001) |
| P39 | Error-proofing | Build quality into the process | make the error impossible in the process (system checks, mandatory fields) instead of relying on later inspection | the purchase system refuses an order without a contract number | [Deming point 3](https://deming.org/explore/fourteen-points/) | moderate |
| P40 | Defense in depth | Three lines | use independent lines: first line (management owns risk), second line (risk, compliance, security functions), third line (independent internal audit) | the platform team owns access risk, security monitors it, internal audit tests both | [IIA Three Lines Model (2020)](https://www.theiia.org/globalassets/documents/resources/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense-july-2020/three-lines-model-updated-english.pdf) | strong |
| P41 | Compartments | Ring-fencing | separate units, budgets or legal entities so that a failure in one does not spread to all | a risky new product runs with its own budget and stop criteria | [NIMS: "Modular Organization"](https://training.fema.gov:443/EMIWeb/IS/IS700b/Handouts/National_Incident_Management%20System_Third%20Edition_October_2017.pdf) | moderate |
| P42 | Two-person rule | Four-eyes principle at the moment of action | require two authorized people for critical, irreversible management actions (large payments, contract signature, dismissal) | a payment above a threshold needs two signatures | [NIST: separation of duty](https://csrc.nist.gov/glossary/term/separation_of_duty) (supports); see P43 | strong |

### E. Capacity and continuity

| ID | Rule name | Management name | THEN (management form) | Example | Sources (management) | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| P44 | Margin | Reserves and slack | keep schedule buffers, budget contingency and free capacity of people; do not plan people near 100 % utilization | the team plans 70 % of its capacity and keeps 30 % for unplanned work | [Little's law](https://projectproduction.org/journal/reprint-littles-law-as-viewed-on-its-50th-anniversary/) (with P52) | strong |
| P45 | Redundancy (N-1) | Deputies and succession | make every critical function survive the loss of one person: named deputy, trained successor, documented knowledge | each on-call skill is held by at least two people | [ISO/TS 30433 succession metrics (via ISO TC 260)](https://committee.iso.org/news/ref2689.html) | moderate |
| P46 | Diversity | Diverse suppliers and diverse views | avoid a common cause hitting all copies: suppliers in different regions; decision input from people with different views | two cloud regions from different providers for the status page; a red team from another department | [UK MoD Red Teaming Handbook](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1027158/20210625-Red_Teaming_Handbook.pdf) | moderate |
| P47 | Graceful degradation | Prioritization and triage under overload | decide in advance which work stops first when demand exceeds capacity, and which activities must resume at a minimum capacity | under overload, feature requests stop first; incident response and security patches continue | [ISO 22301:2019 RTO definition (via BCI GPG)](https://www.thebci.org/static/cf455e45-b2c2-4a44-b77da7c99fd6df77/BCI-GPG-2018-Edition.pdf) | strong |
| P48 | Damping | Stable management cadence | change priorities, structures and plans on a fixed cadence, not on every new signal | priorities change at sprint boundaries, not daily | [Scrum Guide: "No changes are made that would endanger the Sprint Goal"](https://scrumguides.org/scrum-guide.html) | moderate |
| P49 | Induced demand | Parkinson's law | expect work and spending to grow into added time or budget; manage demand as well as capacity | a larger budget is given with an explicit scope, not "more of the same" | [Parkinson 1955 (text copy)](https://doc.cat-v.org/economics/parkinsons-law) | moderate (the original is a satirical essay; the general claim is weak, the budget case is widely observed) |
| P50 | Bottleneck first | Constraint first | find the step that limits output (often an approval, a meeting or a specialist) and improve it first | the security review queue is the constraint, so review capacity is added there first | section 9 (theory of constraints) | moderate |
| P51 | Shared demand signal | Share real end demand | give every stage of a chain the real end demand, not only the order of the next stage | the platform team sees product teams' roadmaps, not only tickets | [Lee, Padmanabhan, Whang 1997](https://courses.ie.bilkent.edu.tr/ie102/wp-content/uploads/sites/12/2019/02/Lee-Padmanabhan-Whang-1997-MS.pdf) | strong |

### F. Verification and review

| ID | Rule name | Management name | THEN (management form) | Example | Sources (management) | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| P54 | Verification and validation | Acceptance and benefits review | check that deliverables meet the specification (verification) and that the intended benefit is reached (validation); keep the business case valid during the whole initiative | the developer portal is accepted against its spec, and six months later adoption is measured | [PRINCE2 principle 1 "Ensure continued business justification"](https://purplegriffon.com/blog/prince2-7th-edition-principles) | moderate |
| P55 | Find defects early | Early review of plans | review plans and business cases before money and people are committed | a one-page proposal is reviewed before a quarter of work is planned | [Deming point 3](https://deming.org/explore/fourteen-points/) | moderate |
| P56 | Independent checker | Independent assurance, scaled to consequence | raise the checker's independence with consequence: peer review → independent second or third line → external audit; rotate long-serving external auditors | a team lead's budget is checked by finance; the company's accounts by an external auditor | [IIA principle 5](https://www.theiia.org/globalassets/documents/resources/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense-july-2020/three-lines-model-updated-english.pdf); [EU 537/2014 Art. 17](https://www.charteredaccountants.ie/chariotindex/text/ec_2014_537/17.html); [UK MoD Red Teaming Handbook](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1027158/20210625-Red_Teaming_Handbook.pdf) | strong (EU law for public-interest entities) |
| P57 | Test as you operate | Pilots and exercises under real conditions | test new processes, plans and organizations in real conditions before full rollout, and exercise continuity plans | a new on-call model is piloted with one team for one month; the continuity plan is exercised once a year | [ISO 22301:2019](https://www.iso.org/standard/75106.html) (supports) | moderate |
| P58 | Comparable measurement | Comparable indicators | define each indicator once (formula, period, population, data source), and show its normal variation before comparing teams or periods | lead time is measured the same way for all teams before teams are compared | [ISO/TS 30433: "comparable measures" (via ISO TC 260)](https://committee.iso.org/news/ref2689.html) | moderate |
| P59 | Traceability | Obligation-to-control traceability | in regulated areas, link each legal or contractual obligation to a control and to a test of that control | each GDPR obligation in the register points to an owner, a control and an audit test | [ISO 37301:2021](https://www.iso.org/standard/75080.html) | strong (regulated areas; standard text is paid; only the official summary was read) |
| P60 | Codes as minimum | Compliance as the floor | meet laws and standards as a minimum, then apply the other rules | working-time law is the minimum; P5 and P28 go further | [ISO 37301:2021](https://www.iso.org/standard/75080.html) | strong (standard text is paid; only the official summary was read) |
| P61 | Qualified procedure and person | Qualified roles | where a result cannot be fully checked afterwards (hiring, audit, investigation, negotiation), use a proven procedure and trained people | only trained interviewers run structured interviews (P62) | [EU 537/2014 (approved statutory auditors)](https://www.charteredaccountants.ie/chariotindex/text/ec_2014_537/17.html) (supports) | strong (statutory audit) |

### G. Change

| ID | Rule name | Management name | THEN (management form) | Example | Sources (management) | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| P64 | Versioning and change review | Document control and management of change | version policies, processes and organization charts; review each change for its effects before it takes effect, and inform the people affected | the on-call policy is versioned in git and changed only by reviewed pull request | [ISO/IEC 20000-1:2018](https://www.iso.org/standard/70636.html); [COSO ERM principle 15 "Assesses Substantial Change"](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf) | strong |
| P65 | Small verified steps | Iterative delivery and management stages | deliver and decide in small steps, and decide at the end of each stage whether to continue | a reorganization is piloted in one department before it rolls out | [DORA: small batches](https://dora.dev/capabilities/working-in-small-batches/); [PRINCE2 principle 4 "Manage by stages"](https://purplegriffon.com/blog/prince2-7th-edition-principles) | strong |
| P66 | Isolation before work | Protected iteration | while a team works on a committed goal, protect it from unplanned changes; only the accountable owner may cancel the goal | new requests wait for the next sprint unless the Product Owner cancels the sprint | [Scrum Guide 2020](https://scrumguides.org/scrum-guide.html) | moderate |
| P67 | Critical path | Critical path | identify the longest chain of dependent tasks and protect it first | in an office move, network installation is critical; furniture has slack | section 9 (critical path method); [ISO 21502:2020](https://www.iso.org/standard/74947.html) | strong (standard text is paid; only the official summary was read) |
| P68 | Observational method | Tolerances with pre-planned responses | where outcomes stay uncertain until execution, set tolerances and planned responses in advance, monitor, and escalate when a tolerance will be breached | if the migration exceeds its time tolerance by 10 %, the steering group decides on scope | [Scrum: inspection and adaptation](https://scrumguides.org/scrum-guide.html); [PRINCE2 principle 5 "Manage by exception"](https://purplegriffon.com/blog/prince2-7th-edition-principles) | moderate |

### H. Operation and maintenance

| ID | Rule name | Management name | THEN (management form) | Example | Sources (management) | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| P70 | Monitoring in operation | Performance monitoring and going to see | track leading and lagging indicators, and regularly go to the place where the work happens | the manager joins an on-call shift each quarter, besides reading the dashboard | [COSO ERM principle 16 "Reviews Risk and Performance"](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf); [Wikipedia: Genchi Genbutsu](https://en.wikipedia.org/wiki/Genchi_Genbutsu) | moderate |
| P71 | Checklists | Checklists for rare management procedures | use checklists for rare, complex or time-critical procedures: onboarding, offboarding, month-end close, the first hour of a crisis | offboarding checklist: access removal, knowledge handover, equipment return | section 9 (surgery, rail); [NIMS: incident action plans](https://training.fema.gov:443/EMIWeb/IS/IS700b/Handouts/National_Incident_Management%20System_Third%20Edition_October_2017.pdf) | moderate |
| P72 | Critical control points | Key controls | identify the few controls that prevent material loss or misstatement, give each a limit, an owner, monitoring and a test | access recertification for production is a key control, tested every quarter | cross-reference only | moderate |
| P73 | Response faster than harm | Recovery inside the tolerable disruption | set the recovery time objective of each critical activity inside its maximum tolerable period of disruption | payroll must resume within 3 days; the tolerable maximum is 5 days | [ISO 22301 definitions (via BCI GPG)](https://www.thebci.org/static/cf455e45-b2c2-4a44-b77da7c99fd6df77/BCI-GPG-2018-Edition.pdf) | strong |
| P74 | Maintenance by failure pattern | Review frequency by risk | set the frequency of audits, reviews and recertifications by how each control actually fails, not one fixed cycle for everything | high-risk access every quarter, low-risk tools once a year | cross-reference only | moderate |
| P75 | Actionable alerts | Management by exception | report to the next management level only when a tolerance is forecast to be breached; remove reports that lead to no action | weekly status shows only items outside tolerance | [PRINCE2 principle 5](https://purplegriffon.com/blog/prince2-7th-edition-principles) | moderate |
| P76 | Sterile critical phase | Focus time and crisis discipline | protect blocks of uninterrupted work; during a crisis, limit communication to the response | no meetings on Tuesday and Thursday mornings; one crisis channel with one commander | [Mark et al. 2008](https://www.interruptions.net/literature/Mark-CHI08.pdf); [NIMS: "Integrated Communications"](https://training.fema.gov:443/EMIWeb/IS/IS700b/Handouts/National_Incident_Management%20System_Third%20Edition_October_2017.pdf) | moderate |
| P77 | Data as a dependency | Data governance for decisions | where decisions depend on data or models, version the definitions, check data quality and watch for drift | the headcount figure in the board report and in HR have the same definition | [COSO ERM principle 18](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf) | moderate |
| P78 | Asset inventory | Registers of assets, contracts, information and records | keep complete registers with an owner, condition and life-cycle stage | a contract register with end dates and notice periods | [ISO 55000:2024](https://www.iso.org/standard/83053.html); [ISO/IEC 27001:2022](https://www.iso.org/standard/27001); [ISO 15489-1:2016](https://www.iso.org/standard/62542.html) | strong (standard text is paid; only the official summary was read) |

### I. Learning

| ID | Rule name | Management name | THEN (management form) | Example | Sources (management) | Evidence |
| --- | --- | --- | --- | --- | --- | --- |
| P80 | Blameless root cause analysis | After-action review | after an event, discuss without blame what happened, why, and how to improve | after a failed reorganization: an AAR with all affected teams | [US Army: Foundations of the After Action Review Process (DTIC)](https://apps.dtic.mil/sti/pdfs/ADA368651.pdf); [Deming point 8](https://deming.org/explore/fourteen-points/) | strong (doctrine) |
| P81 | Plan-Do-Check-Act | Regular reflection and adjustment | run the improvement cycle at fixed intervals and track actions to completion | a retrospective at the end of every sprint and quarter | [Agile principle 12](https://agilemanifesto.org/principles); [ISO 9001:2026](https://www.iso.org/news/2026/09/ISO9001-2026) | strong |
| P82 | Investigate anomalies | Weak signals and near misses | record and investigate deviations even when nothing went wrong, before they become normal | three projects in a row miss their deadline by two weeks → investigated as a pattern | [CAIB report summary](https://www.globalsecurity.org/space/library/report/2003/caib-report_vol-1_august2003.htm) | strong |
| P83 | Preserve evidence | Legal hold | when litigation or an investigation is reasonably anticipated, stop routine deletion and preserve the relevant records | after a complaint about a dismissal, the related emails and chat channels are preserved | [Sedona Commentary on Legal Holds, Guideline 1](https://www.thesedonaconference.org/sites/default/files/publications/Commentary%20on%20Legal%20Holds.pdf) | strong (US litigation duty) |

## 11. Direct quotes

Rule quotes were checked against the linked page on 2026-10-14 and case quotes on 2026-10-27. "…" marks text left out. Where the linked page is a copy, the original is named. Quotes for the engineering sources of rules P1–P4, P9–P17, P22–P34, P36–P42, P44–P51, P54–P61, P64–P68, P70–P78 and P80–P83 are given in the rule tables where they decide the evidence rating (for example P75, P34).

### Master rule

| Rule | Sources | Direct quote |
| --- | --- | --- |
| Master rule (risk appetite) | [COSO ERM Executive Summary (2017)](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf) | "The organization defines risk appetite in the context of creating, preserving, and realizing value." (principle 7) |
| Master rule (tailoring) | [PMI: PMBOK Guide 8th edition](https://www.pmi.org/standards/pmbok/about); [Purple Griffon: PRINCE2 7th edition principles](https://purplegriffon.com/blog/prince2-7th-edition-principles) | PMBOK 8: "Tailor for your context" — "Learn how to adapt practices, tools, and techniques to fit your team, organization, and environment." PRINCE2 principle 7: "Tailor to suit the project" (principle name) |
| Master rule (irreversibility) | [Amazon 2015 letter to shareholders](https://www.sec.gov/Archives/edgar/data/1018724/000119312516530910/d168744dex991.htm) | see P18 |

### Rules from management sources

| Rule | Sources (primary first) | Direct quote |
| --- | --- | --- |
| P7 | [US Army ADP 6-0 Mission Command (2019)](https://irp.fas.org/doddir/army/adp6_0.pdf) | Commander's intent: "a clear and concise expression of the purpose of the operation and the desired military end state" (para 1-45). "Mission orders are directives that emphasize to subordinates the results to be attained, not how they are to achieve them." (para 1-53). Principles: "Competence. Mutual trust. Shared understanding. Commander's intent. Mission orders. Disciplined initiative. Risk acceptance." (para 1-26) |
| P5 | [Edmondson 1999, Administrative Science Quarterly (copy)](https://web.mit.edu/curhan/www/docs/Articles/15341_Readings/Group_Performance/Edmondson%20Psychological%20safety.pdf); [Google re:Work: Understand team effectiveness](https://rework.withgoogle.com/intl/en/guides/understand-team-effectiveness) | Edmondson: team psychological safety is "a shared belief that the team is safe for interpersonal risk taking"; "learning behavior mediates between team psychological safety and team performance." Google: five dynamics "In order of importance": "Psychological safety", "Dependability", "Structure and clarity", "Meaning", "Impact" (180 teams studied) |
| P6 | [G20/OECD Principles of Corporate Governance 2023](https://legalinstruments.oecd.org/public/doc/322/322.en.pdf); [OECD Recommendation on Public Procurement: Integrity](https://web.archive.org/web/20240518154901/https://search.oecd.org/governance/procurement/toolbox/principlestools/integrity/); [ISO 37001 (catalogue page)](https://www.iso.org/standard/37001) | OECD II.F.2: "Members of the board and key executives should be required to disclose to the board whether they, directly, indirectly" … "have a material interest in any transaction or matter directly affecting the corporation." OECD procurement risk: "Mismanagement of conflict of interest in the public service and in post-public employment" |
| P8 | [Kim & Mauborgne: Fair Process (HBR 1997, copy)](https://ieanea.org/wp-content/uploads/2019/05/FairProcessArticle.pdf) | "Engagement—involving individuals in decisions by inviting their input and encouraging them to challenge one another's ideas." "Explanation—clarifying the thinking behind a final decision." "Expectation clarity—stating the new rules of the game, including performance standards…" "Notice that fair process is not decision by consensus." |
| P18 | [Amazon 2015 letter to shareholders (SEC filing)](https://www.sec.gov/Archives/edgar/data/1018724/000119312516530910/d168744dex991.htm) | "Some decisions are consequential and irreversible or nearly irreversible – one-way doors –" "these decisions must be made methodically, carefully, slowly, with great deliberation and consultation." "Type 2 decisions can and should be made quickly by high judgment individuals or small groups." "The end result of this is slowness, unthoughtful risk aversion, failure to experiment sufficiently, and consequently diminished invention." |
| P21 | [Locke & Latham 2002, American Psychologist (copy)](https://goal-lab.psych.umn.edu/orgpsych/2020/readings/5.%20Motivation/Locke%20&%20Latham%20(2002).pdf); dissent: [Deming 14 Points](https://deming.org/explore/fourteen-points/) | "We found that specific, difficult goals consistently led to higher performance than urging people to do their best." "the combination of goals plus feedback is more effective than goals alone" "on tasks that are complex for people, learning goals can be superior to performance goals". Deming 11(b): "Eliminate management by objective. Eliminate management by numbers, numerical goals. Substitute leadership." |
| P19 | [Campbell 1979, Evaluation and Program Planning 2(1): 67–90, doi:10.1016/0149-7189(79)90048-X](https://doi.org/10.1016/0149-7189(79)90048-X); [Wikipedia: Campbell's law](https://en.wikipedia.org/wiki/Campbell%27s_law) (secondary, quote checked here) | "The more any quantitative social indicator is used for social decision-making, the more subject it will be to corruption pressures and the more apt it will be to distort and corrupt the social processes it is intended to monitor." |
| P20 | [Staw 1976, Organizational Behavior and Human Performance (copy)](https://www.gwern.net/doc/psychology/cognitive-bias/sunk-cost/1976-staw.pdf); [Purple Griffon: PRINCE2 principles](https://purplegriffon.com/blog/prince2-7th-edition-principles) | Staw: "Results showed that persons committed the greatest amount of resources to a previously chosen course of action when they were personally responsible for negative consequences." PRINCE2 (blog wording): "a principle that must persistently endure scrutiny throughout the project's entire lifecycle" |
| P35 | [Conway: How Do Committees Invent? (1968)](https://www.melconway.com/Home/Committees_Paper.html) | organizations which design systems are "constrained to produce designs which are copies of the communication structures of these organizations." "Ways must be found to reward design managers for keeping their organizations lean and flexible." |
| P79 | [FEMA: NIMS 3rd edition (2017)](https://training.fema.gov:443/EMIWeb/IS/IS700b/Handouts/National_Incident_Management%20System_Third%20Edition_October_2017.pdf) | "The optimal span of control for incident management is one supervisor to five subordinates;" "effective incident management frequently necessitates ratios significantly different from this." "The 1:5 ratio is a guideline, and incident personnel use their best judgment" |
| P43 | [NIST CSRC Glossary: separation of duty (from NIST SP 800-192)](https://csrc.nist.gov/glossary/term/separation_of_duty) | Separation of duty "refers to the principle that no user should be given enough privileges to misuse the system on their own." |
| P52 | [Little: Little's Law as Viewed on Its 50th Anniversary (Operations Research 2011, reprint)](https://projectproduction.org/journal/reprint-littles-law-as-viewed-on-its-50th-anniversary/) | "the average number of items in a queuing system, denoted L, equals the average arrival rate of items to the system" … "multiplied by the average waiting time of an item in the system". "Note that if λ is prespecified, the only way to reduce inventory (L) is to find a way to reduce average wait/item (W)." |
| P53 | [The Jargon File: Brooks's Law](http://www.catb.org/jargon/html/B/Brookss-Law.html) (secondary only; primary: Brooks, *The Mythical Man-Month*, 1975, book, not online) | "Adding manpower to a late software project makes it later" |
| P62 | [Sackett, Zhang, Berry, Lievens: Revisiting meta-analytic estimates of validity in personnel selection, Journal of Applied Psychology, doi:10.1037/apl0000994 (copy)](https://www.gwern.net/doc/statistics/meta-analysis/2021-sackett.pdf) | "Structured interviews emerged as the top-ranked selection procedure." "producing mean validity estimates of .42 for structured interviews and .19 for unstructured interviews." |
| P63 | [Kluger & DeNisi 1996, Psychological Bulletin 119(2), doi:10.1037/0033-2909.119.2.254 (abstract page)](https://cris.huji.ac.il/en/publications/the-effects-of-feedback-interventions-on-performance-a-historical/) | FIs "improved performance on average (d =.41)" but "over 1/3 of the FIs decreased performance." |
| P69 | [Kotter: Leading Change — Why Transformation Efforts Fail (HBR 1995, copy)](https://fcm.ucsf.edu/sites/g/files/tkssra17611/files/Kotter_WhyTransformationEffortsFail.pdf) | "Error 4: Undercommunicating the Vision by a Factor of Ten"; "Error 7: Declaring Victory Too Soon"; "the change process goes through a series of phases"; "Skipping steps creates only the illusion of speed" |
| P6 (engineering) | [NSPE Ethics Reference Guide](https://www.nspe.org/sites/default/files/resources/pdfs/Ethics/EthicsReferenceGuide.pdf) | II.4.a: "Engineers shall disclose all known or potential conflicts of interest that could influence or appear to influence their judgment or the quality of their services." |
| P53 (nuance) | [Reinertsen: Is it always a bad idea to add resources to a late project? (Electronic Design 2000)](https://www.electronicdesign.com/archive/article/21760483/is-it-always-a-bad-idea-to-add-resources-to-a-late-project) | Brooks: "Oversimplifying outrageously, we state Brooks' Law...." Reinertsen: "add extra resources as early as possible. The later you add them, the lower the payoff." |

### Management sources for the other rules

| Rule | Sources | Direct quote |
| --- | --- | --- |
| P1 | [ISO: ISO 9001:2026 launch](https://www.iso.org/news/2026/09/ISO9001-2026) | the update "places greater emphasis on leadership, a culture of quality and ethical behaviour." |
| P2 | [ADP 6-0](https://irp.fas.org/doddir/army/adp6_0.pdf); [COSO ERM](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf) | ADP 6-0 principle: "Competence." COSO principle 5: "Attracts, Develops, and Retains Capable Individuals" |
| P3 | [PMI: PMBOK Guide 8](https://www.pmi.org/standards/pmbok/about); [ISO 20400](https://www.iso.org/standard/63026.html); [ISO 14001 (catalogue)](https://www.iso.org/standard/60857.html) | PMBOK 8 principles: "Adopt a holistic view, focus on value, embed quality, lead accountably, integrate sustainability, and build empowered teams." |
| P4 | [Directive (EU) 2019/1937](https://eur-lex.europa.eu/legal-content/EN/TXT/HTML/?uri=CELEX:32019L1937); [Deming](https://deming.org/explore/fourteen-points/); [Toyota](https://global.toyota/en/company/vision-and-philosophy/production-system/) | Art. 8(3): "Paragraph 1 shall apply to legal entities in the private sector with 50 or more workers." Recital 88: "A clear legal prohibition of retaliation would have an important dissuasive effect". Deming 8: "Drive out fear, so that everyone may work effectively for the company." Toyota: "the operator can stop the line by pulling the stop cord themselves" |
| P9 | [NIMS](https://training.fema.gov:443/EMIWeb/IS/IS700b/Handouts/National_Incident_Management%20System_Third%20Edition_October_2017.pdf) | "The Incident Commander or Unified Command establishes objectives that drive incident operations." |
| P10 | [COSO ERM](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf) | principle 8: "Evaluates Alternative Strategies" |
| P11 | [§ 239 HGB (dejure.org)](https://dejure.org/gesetze/HGB/239.html); [GDPR Art. 5](https://gdpr-info.eu/art-5-gdpr/) | § 239(3) HGB: "Eine Eintragung oder eine Aufzeichnung darf nicht in einer Weise verändert werden, daß der ursprüngliche Inhalt nicht mehr feststellbar ist." (An entry or record must not be changed in a way that makes the original content no longer determinable.) GDPR 5(2): "The controller shall be responsible for, and be able to demonstrate compliance with, paragraph 1" |
| P12 | [Flyvbjerg 2006](https://arxiv.org/pdf/1302.3642) | step 1: "Identification of a relevant reference class of past, similar projects." "inaccuracy in cost forecasts in constant prices is on average 44.7% for rail, 33.8% for bridges and tunnels," "and 20.4% for roads." |
| P13, P16, P77, P70 (part), P64 (part) | [COSO ERM](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf) | principle names: 18 "Leverages Information Systems"; 8 "Evaluates Alternative Strategies"; 16 "Reviews Risk and Performance"; 15 "Assesses Substantial Change" |
| P14 | [OECD Due Diligence Guidance](https://www.oecd.org/en/publications/oecd-due-diligence-guidance-for-responsible-business-conduct_15f5f4b3-en.html) | "This Guidance helps businesses to understand and implement due diligence for responsible business conduct." |
| P22 | [Klein: Performing a Project Premortem (HBR 2007)](https://hbr.org/2007/09/performing-a-project-premortem); [COSO ERM](https://www.coso.org/_files/ugd/3059fc_61ea5985b03c4293960642fdce408eaa.pdf) | Klein: "In a premortem, team members assume that the project they are planning has just failed—as so many do—" and "generate plausible reasons for its demise." COSO principle 14: "Develops Portfolio View" |
| P23 | [Agile principles](https://agilemanifesto.org/principles) | "Simplicity--the art of maximizing the amount of work not done--is essential." |
| P24, P36 | [GDPR Art. 5](https://gdpr-info.eu/art-5-gdpr/) | 5(1)(e): "kept in a form which permits identification of data subjects for no longer than is necessary" 5(1)(c): "adequate, relevant and limited to what is necessary in relation to the purposes for which they are processed" |
| P25 | [Google re:Work](https://rework.withgoogle.com/intl/en/guides/understand-team-effectiveness) | dynamic 3: "Structure and clarity" |
| P28 | [WHO/ILO 2021](https://www.who.int/news/item/17-05-2021-long-working-hours-increasing-deaths-from-heart-disease-and-stroke-who-ilo); [Pencavel 2014](https://docs.iza.org/dp8129.pdf); [Agile principles](https://agilemanifesto.org/principles) | WHO/ILO: "working 55 or more hours per week is associated with an estimated 35% higher risk of a stroke" and "a 17% higher risk of dying from ischemic heart disease, compared to working 35-40 hours a week". Pencavel: "below an hours threshold, output is proportional to hours;" "above a threshold, output rises at a decreasing rate as hours increase." Agile 8: "The sponsors, developers, and users should be able to maintain a constant pace indefinitely." |
| P30, P37, P41, P76, P71 | [NIMS](https://training.fema.gov:443/EMIWeb/IS/IS700b/Handouts/National_Incident_Management%20System_Third%20Edition_October_2017.pdf) | "Unity of command means that each individual only reports to one person." Management characteristics include "Modular Organization", "Integrated Communications", "Establishment and Transfer of Command". "IAPs represent concise, coherent means of capturing and communicating incident objectives, tactics, and assignments" |
| P31 | [Kohavi & Thomke 2017](https://web-docs.stern.nyu.edu/executive/The%20Surprising%20Power%20of%20Online%20Experiments.pdf) | "At Google and Bing, only about 10% to 20% of experiments generate positive results." At Microsoft, "one-third prove effective, one-third have neutral results, and one-third have negative results." |
| P32, P39, P55 | [Deming 14 Points](https://deming.org/explore/fourteen-points/) | 9: "Break down barriers between departments." 3: "Cease dependence on inspection to achieve quality." "Eliminate the need for inspection on a mass basis by building quality into the product in the first place." |
| P38 | [Auditor Training Online: ISO 45001 clause 8.1.2](https://blog.auditortrainingonline.com/blog/iso-45001-clause-8-1-2) (secondary; ISO text is paid) | "The organization shall establish, implement and maintain a process(es) for the elimination of hazards and reduction of OH&S risks using the following hierarchy of controls: a) eliminate the hazard; b) substitute with less hazardous processes, operations, materials or equipment; c) use engineering controls and reorganization of work; d) use administrative controls, including training; e) use adequate personal protective equipment." (clause 8.1.2 as reproduced in the article) |
| P40, P56, P26 | [IIA Three Lines Model (2020)](https://www.theiia.org/globalassets/documents/resources/the-iias-three-lines-model-an-update-of-the-three-lines-of-defense-july-2020/three-lines-model-updated-english.pdf) | "However, responsibility for managing risk remains a part of first line roles and within the scope of management." "Internal audit's independence from the responsibilities of management is critical to its objectivity, authority, and credibility." "It achieves this through the competent application of systematic and disciplined processes, expertise, and insight." |
| P56 (external) | [EU 537/2014 Art. 17](https://www.charteredaccountants.ie/chariotindex/text/ec_2014_537/17.html) | "…nor this in combination with any renewed engagements therewith shall exceed a maximum duration of 10 years." "The key audit partners responsible for carrying out a statutory audit shall cease their participation" "in the statutory audit of the audited entity not later than seven years from the date of their appointment." |
| P56 (red team), P46 | [UK MoD Red Teaming Handbook](https://assets.publishing.service.gov.uk/government/uploads/system/uploads/attachment_data/file/1027158/20210625-Red_Teaming_Handbook.pdf) | red teaming is "the independent application of a range of structured, creative and critical thinking techniques" "to assist the end user make a better-informed decision or produce a more robust product." |
| P45, P58 | [ISO TC 260: People power](https://committee.iso.org/news/ref2689.html) | ISO/TS 30433 "describes the elements of succession planning metrics and provides comparable measures to report on them." |
| P44, P52 | [Little 2011 (reprint)](https://projectproduction.org/journal/reprint-littles-law-as-viewed-on-its-50th-anniversary/) | see P52 |
| P47, P73 | [BCI GPG 2018 with ISO 22301:2019 definitions](https://www.thebci.org/static/cf455e45-b2c2-4a44-b77da7c99fd6df77/BCI-GPG-2018-Edition.pdf) | MTPD: "the time frame within which the impacts of not resuming activities would become unacceptable to the organization". RTO: "prioritized time frames as set within the time identified in MTPD" "for resuming disrupted activities at a specified minimum acceptable capacity" |
| P48, P66 | [Scrum Guide 2020](https://scrumguides.org/scrum-guide.html) | "No changes are made that would endanger the Sprint Goal;" "Only the Product Owner has the authority to cancel the Sprint." |
| P49 | [Parkinson 1955 (text copy; original in The Economist, November 1955)](https://doc.cat-v.org/economics/parkinsons-law) | "It is a commonplace observation that work expands so as to fill the time available for its completion." |
| P51 | [Lee, Padmanabhan, Whang 1997](https://courses.ie.bilkent.edu.tr/ie102/wp-content/uploads/sites/12/2019/02/Lee-Padmanabhan-Whang-1997-MS.pdf) | "Sell-through data and information on inventory status at downstream nodes are keys to improving channel coordination" |
| P54, P65, P68, P75, P30 | [Purple Griffon: PRINCE2 7th edition principles](https://purplegriffon.com/blog/prince2-7th-edition-principles) (secondary; the official manual is paid) | principle names: "Ensure continued business justification", "Manage by stages", "Manage by exception", "Define roles, responsibilities, and relationships". On exceptions: "These exceptions are promptly escalated to the subsequent management tier" |
| P65 | [DORA: Working in small batches](https://dora.dev/capabilities/working-in-small-batches/) | "Working in small batches is an essential principle in any discipline where feedback loops are important," "or you want to learn quickly from your decisions." |
| P76 | [Mark, Gudith, Klocke 2008](https://www.interruptions.net/literature/Mark-CHI08.pdf) | "people compensate for interruptions by working faster" "experiencing more stress, higher frustration, time pressure and effort" |
| P80 | [US Army: Foundations of the AAR Process (DTIC), quoting TC 25-20 (1993)](https://apps.dtic.mil/sti/pdfs/ADA368651.pdf) | an AAR "is a professional discussion of an event, focused on performance standards," that "enables soldiers to discover for themselves what happened, why it happened, and how to sustain strengths and improve on weaknesses". Table 3: "Minimizing 'finger-pointing'" |
| P81 | [Agile principles](https://agilemanifesto.org/principles); [Scrum Guide](https://scrumguides.org/scrum-guide.html) | Agile 12: "At regular intervals, the team reflects on how to become more effective, then tunes and adjusts its behavior accordingly." Scrum: "transparency, inspection, and adaptation" |
| P82 | [CAIB report summary](https://www.globalsecurity.org/space/library/report/2003/caib-report_vol-1_august2003.htm) | "the NASA organizational culture had as much to do with the accident as the foam that struck the Orbiter on ascent." |
| P83 | [Sedona Commentary on Legal Holds, 2nd ed.](https://www.thesedonaconference.org/sites/default/files/publications/Commentary%20on%20Legal%20Holds.pdf) | Guideline 1: "A reasonable anticipation of litigation arises when an organization is on notice of a credible probability that it will become involved in litigation, seriously contemplates initiating litigation, or when it takes specific actions to commence litigation." |
| P70 (go and see) | [Wikipedia: Genchi Genbutsu](https://en.wikipedia.org/wiki/Genchi_Genbutsu) (secondary only) | no quote checked |
| P15, P27, P29, P34, P72, P74 | cross-reference only | no management source found |
| P50, P67 | section 9 sources (theory of constraints, critical path method); [ISO 21502:2020](https://www.iso.org/standard/74947.html) | no new quote |
| P17, P33, P61, P59, P60, P78, P57 | ISO catalogue pages listed in sections 4 and 10; for P61, the ASME page in section 9 | catalogue pages give titles and summaries only; no requirement text quoted |

## 12. Method and limits

### Method

INCOSE requires a systems engineering principle to "Transcend life cycle", "Transcend system type" and "Transcend context". It describes heuristics as guidance "emerging from practice in a given context or area". SEBoK adds that the application of principles is specific to stakeholders and context. This taxonomy follows that split: universal rules transcend system type and context, and the master rule adapts how strictly they apply; conditional rules are context-specific; risk-scaled rules are universal in principle but needed only above a risk threshold.

- **Adoption gaps are not counterexamples.** A rule that a domain does not practice yet still applies there by cross-reference (see section 4).
- **Practices, not principles:** INCOSE says principles must "Not be how-to statements". The rules here are practices with actions, so the universal rules are universal practices, not principles in the INCOSE sense.
- **Size:** 83 rules are too many for a checklist. A checklist works best with five to nine items, "the limit of working memory" (Gawande, via book notes); section 3 therefore offers nine questions, one per category.
- **Supporting quotes:** "all models are wrong, but some are useful" (Box and Draper, 1987) supports P44 and P12; "everything fails all the time" (Werner Vogels) supports P37.
- **Selection of management rules:** management rules are included when they change how a system is designed, checked, changed or operated, or how the people who build it are organized, selected, given feedback and led through change.

### Source quality

- Every rule has at least one primary source, except **P53** (secondary only; the primary source, Brooks's 1975 book, is not online).
- Some primary texts were read through faithful copies: NIST via CSF Tools, IMO SOLAS via imorules.com, The Joint Commission via KFF, the Rio Declaration via the World Bank ICSID archive, Hoare's lecture via worrydream.com, Edmondson via MIT, Staw and Sackett via gwern.net, Campbell via a 2011 journal reprint (the quote itself was checked on Wikipedia), § 239 HGB via dejure.org, Regulation (EU) No 537/2014 via charteredaccountants.ie.
- Cooper's report states the safety condition (P73) as required egress time "equal to or less than" available time. For ASME Section IX (P61), the official page confirms procedure qualification; the qualification of individual welders is supported only by the secondary source.
- The phase values of GSFC-STD-1000 (P44) come from a garbled table extraction; check the original before quoting them.
- P18 rests on a CEO's letter, not on research. K1–K8 are the author's synthesis unless their Basis column names a source.

### Limits

- **Current standard editions (checked 2026-10-14).** ISO 9001:2015 is withdrawn; ISO 9001:2026 was published on 16 September 2026, and the CQI describes a planned three-year transition. ISO 14001:2015 is withdrawn and replaced by ISO 14001:2026. ISO 22301:2019, ISO 21502:2020, ISO 30401:2018 and ISO 45001:2018 are current but marked "to be revised". ISO 30414:2018 is withdrawn (a 2025 edition exists; its catalogue page was not checked).
- **Paid documents.** The texts of ISO standards, PRINCE2 and PMBOK are paid. This taxonomy quotes only official summaries, press releases or secondary pages for them, and says so. Check the original before quoting a requirement in an audit.
- **Strong on a summary only.** Rules P58, P61 and P34, and the management forms of P3, P67, P59, P60 and P78, are rated strong on a paid standard: the standard text is paid; only the official summary was read. The rating reflects that the standard requires the practice, which its official summary confirms.
- **Not fetched in full.** The text of Article 19 (prohibition of retaliation) of Directive (EU) 2019/1937 could not be retrieved; recital 88 is quoted instead. The OECD Due Diligence Guidance PDF could not be retrieved; only its abstract is quoted. The HBR article by Klein was only available as a summary.
- **Secondary only.** Rule P53 (Brooks's law) rests on the Jargon File and a trade article; the primary source is a book that is not online. In section 10, the management forms of P49 (a copy of Parkinson's essay that could not be compared with The Economist's archive), P70 (go and see) and P38 (ISO 45001 clause text) rest on secondary pages; the rules themselves have primary engineering sources in section 9.
- **Cross-reference only.** P15, P27, P29, P34, P72 and P74 have no management source. The transfer is the author's judgment.
- **Contested evidence.** P21 is contested by Deming (K8 resolves the conflict). P69 (Kotter) is a practitioner model with limited empirical testing. P18 rests on a CEO's letter, not on research. The "focus on the task" part of P63 is the author's summary of the authors' theory.
- **Classification:** the classification of each rule is the author's judgment against the test in section 1. The counterexamples are reasoned, not sourced.

### Method sources

- [INCOSE: Systems Engineering Principles (Watson et al.)](https://www.incose.org/wp-content/uploads/legacy/professional-development-portal/pdp-pdf-non-webinar-documents/systems_engineering_principles_book_v12_watson.pdf)
- [SEBoK: Systems Engineering Principles](https://sebokwiki.org/wiki/Systems_Engineering_Principles)
- [Wikipedia: Academic use](https://en.wikipedia.org/wiki/Wikipedia:Academic_use)
- [Graham Mann: Notes on The Checklist Manifesto](https://grahammann.net/book-notes/the-checklist-manifesto-atul-gawande)

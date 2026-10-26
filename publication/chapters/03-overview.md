# 3. Taxonomy overview

The categories follow the lifecycle of an engineered system: who is responsible (A), what is known and decided (B), how it is designed (C–E), how it is checked (F), changed (G) and operated (H), and how the organization learns (I).

## Quick view: nine questions

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

## Analogy map: engineering object → management object

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

## Rules per category

- **A. Responsibility** — Duties toward people, the environment and the work itself.
  - [P1](07-rules.md#p1) Public safety first (MUST)
  - [P2](07-rules.md#p2) Work within competence (MUST)
  - [P3](07-rules.md#p3) Sustainability (SHOULD)
  - [P4](07-rules.md#p4) Stop authority (SHOULD)
  - [P5](07-rules.md#p5) Psychological safety (SHOULD)
  - [P6](07-rules.md#p6) Conflict-of-interest disclosure (MUST)
  - [P7](07-rules.md#p7) Commander's intent (SHOULD)
  - [P8](07-rules.md#p8) Fair process (SHOULD)
- **B. Knowledge and decisions** — How requirements, decisions, models and evidence are recorded and trusted.
  - [P9](07-rules.md#p9) Measurable requirements (MUST)
  - [P10](07-rules.md#p10) Decision records (SHOULD)
  - [P11](07-rules.md#p11) Trustworthy evidence (SHOULD)
  - [P12](07-rules.md#p12) Model validity (SHOULD)
  - [P13](07-rules.md#p13) Automated reproducible results (SHOULD)
  - [P14](07-rules.md#p14) Provenance (SHOULD)
  - [P15](07-rules.md#p15) Precaution (SHOULD)
  - [P16](07-rules.md#p16) Set-based design (SHOULD)
  - [P17](07-rules.md#p17) Technology maturity (SHOULD)
  - [P18](07-rules.md#p18) Decision speed by reversibility (SHOULD)
  - [P19](07-rules.md#p19) Indicators are not targets (SHOULD)
  - [P20](07-rules.md#p20) Stop criteria set in advance (SHOULD)
  - [P21](07-rules.md#p21) Specific, challenging goals with feedback (SHOULD)
- **C. Design** — How to shape a design before it is built, so that it fails less.
  - [P22](07-rules.md#p22) Failure and interaction analysis (SHOULD)
  - [P23](07-rules.md#p23) Simplicity and modularity (SHOULD)
  - [P24](07-rules.md#p24) Lifecycle and decommissioning (SHOULD)
  - [P25](07-rules.md#p25) Human factors (SHOULD)
  - [P26](07-rules.md#p26) Design for testability (SHOULD)
  - [P27](07-rules.md#p27) Robustness (SHOULD)
  - [P28](07-rules.md#p28) Accumulated degradation (SHOULD)
  - [P29](07-rules.md#p29) Compatibility (SHOULD)
  - [P30](07-rules.md#p30) Exact constraint (SHOULD)
  - [P31](07-rules.md#p31) Design by selection (SHOULD)
  - [P32](07-rules.md#p32) End-to-end (SHOULD)
  - [P33](07-rules.md#p33) Strict interfaces (SHOULD)
  - [P34](07-rules.md#p34) Weakest-link scaling (SHOULD)
  - [P35](07-rules.md#p35) Structure follows the intended system (SHOULD)
- **D. Protection** — Controls that prevent harm, or contain it when it happens.
  - [P36](07-rules.md#p36) Least privilege (MUST)
  - [P37](07-rules.md#p37) Fail-safe (MUST)
  - [P38](07-rules.md#p38) Hierarchy of controls (SHOULD)
  - [P39](07-rules.md#p39) Error-proofing (SHOULD)
  - [P40](07-rules.md#p40) Defense in depth (SHOULD)
  - [P41](07-rules.md#p41) Compartments (SHOULD)
  - [P42](07-rules.md#p42) Two-person rule (SHOULD)
  - [P43](07-rules.md#p43) Segregation of duties (MUST)
- **E. Capacity and continuity** — How the system keeps working under high load and partial failure.
  - [P44](07-rules.md#p44) Margin (SHOULD)
  - [P45](07-rules.md#p45) Redundancy (N-1) (SHOULD)
  - [P46](07-rules.md#p46) Diversity (SHOULD)
  - [P47](07-rules.md#p47) Graceful degradation (SHOULD)
  - [P48](07-rules.md#p48) Damping (SHOULD)
  - [P49](07-rules.md#p49) Induced demand (SHOULD)
  - [P50](07-rules.md#p50) Bottleneck first (SHOULD)
  - [P51](07-rules.md#p51) Shared demand signal (SHOULD)
  - [P52](07-rules.md#p52) Limit work in progress (SHOULD)
  - [P53](07-rules.md#p53) Late work and added people (SHOULD)
- **F. Verification and review** — How to prove that the work is correct.
  - [P54](07-rules.md#p54) Verification and validation (MUST)
  - [P55](07-rules.md#p55) Find defects early (SHOULD)
  - [P56](07-rules.md#p56) Independent checker (MUST)
  - [P57](07-rules.md#p57) Test as you operate (SHOULD)
  - [P58](07-rules.md#p58) Comparable measurement (SHOULD)
  - [P59](07-rules.md#p59) Traceability (MUST)
  - [P60](07-rules.md#p60) Codes as minimum (MUST)
  - [P61](07-rules.md#p61) Qualified procedure and person (SHOULD)
  - [P62](07-rules.md#p62) Structured selection of people (SHOULD)
  - [P63](07-rules.md#p63) Feedback on the task (SHOULD)
- **G. Change** — How to change the system safely.
  - [P64](07-rules.md#p64) Versioning and change review (MUST)
  - [P65](07-rules.md#p65) Small verified steps (SHOULD)
  - [P66](07-rules.md#p66) Isolation before work (MUST)
  - [P67](07-rules.md#p67) Critical path (SHOULD)
  - [P68](07-rules.md#p68) Observational method (SHOULD)
  - [P69](07-rules.md#p69) Guided change (SHOULD)
- **H. Operation and maintenance** — How to run, watch and maintain the system.
  - [P70](07-rules.md#p70) Monitoring in operation (SHOULD)
  - [P71](07-rules.md#p71) Checklists (SHOULD)
  - [P72](07-rules.md#p72) Critical control points (SHOULD)
  - [P73](07-rules.md#p73) Response faster than harm (SHOULD)
  - [P74](07-rules.md#p74) Maintenance by failure pattern (SHOULD)
  - [P75](07-rules.md#p75) Actionable alerts (SHOULD)
  - [P76](07-rules.md#p76) Sterile critical phase (SHOULD)
  - [P77](07-rules.md#p77) Data as a dependency (SHOULD)
  - [P78](07-rules.md#p78) Asset inventory (SHOULD)
  - [P79](07-rules.md#p79) Span of control (SHOULD)
- **I. Learning** — How to learn from failures and anomalies.
  - [P80](07-rules.md#p80) Blameless root cause analysis (SHOULD)
  - [P81](07-rules.md#p81) Plan-Do-Check-Act (SHOULD)
  - [P82](07-rules.md#p82) Investigate anomalies (SHOULD)
  - [P83](07-rules.md#p83) Preserve evidence (SHOULD)
- **K. Conflict rules** — [K1](08-conflicts.md#k1), [K2](08-conflicts.md#k2), [K3](08-conflicts.md#k3), [K4](08-conflicts.md#k4), [K5](08-conflicts.md#k5), [K6](08-conflicts.md#k6), [K7](08-conflicts.md#k7), [K8](08-conflicts.md#k8)

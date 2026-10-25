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

The left column is the engineering term used in this file. The right column is the thing that plays the same role in an organization.

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
  - [U1](07-rules.md#u1) Public safety first (MUST)
  - [U2](07-rules.md#u2) Work within competence (MUST)
  - [U16](07-rules.md#u16) Sustainability (SHOULD)
  - [U20](07-rules.md#u20) Stop authority (SHOULD)
  - [U47](07-rules.md#u47) Psychological safety (SHOULD)
  - [U48](07-rules.md#u48) Conflict-of-interest disclosure (MUST)
  - [U49](07-rules.md#u49) Commander's intent (SHOULD)
  - [U54](07-rules.md#u54) Fair process (SHOULD)
- **B. Knowledge and decisions** — How requirements, decisions, models and evidence are recorded and trusted.
  - [U3](07-rules.md#u3) Measurable requirements (MUST)
  - [U21](07-rules.md#u21) Decision records (SHOULD)
  - [U22](07-rules.md#u22) Trustworthy evidence (SHOULD)
  - [U31](07-rules.md#u31) Model validity (SHOULD)
  - [U43](07-rules.md#u43) Automated reproducible results (SHOULD)
  - [U45](07-rules.md#u45) Provenance (SHOULD)
  - [R5](07-rules.md#r5) Precaution (SHOULD)
  - [R8](07-rules.md#r8) Set-based design (SHOULD)
  - [C2](07-rules.md#c2) Technology maturity (SHOULD)
  - [U50](07-rules.md#u50) Decision speed by reversibility (SHOULD)
  - [U51](07-rules.md#u51) Indicators are not targets (SHOULD)
  - [U52](07-rules.md#u52) Stop criteria set in advance (SHOULD)
  - [U55](07-rules.md#u55) Specific, challenging goals with feedback (SHOULD)
- **C. Design** — How to shape a design before it is built, so that it fails less.
  - [U6](07-rules.md#u6) Failure and interaction analysis (SHOULD)
  - [U7](07-rules.md#u7) Simplicity and modularity (SHOULD)
  - [U14](07-rules.md#u14) Lifecycle and decommissioning (SHOULD)
  - [U15](07-rules.md#u15) Human factors (SHOULD)
  - [U24](07-rules.md#u24) Design for testability (SHOULD)
  - [U30](07-rules.md#u30) Robustness (SHOULD)
  - [U38](07-rules.md#u38) Accumulated degradation (SHOULD)
  - [U44](07-rules.md#u44) Compatibility (SHOULD)
  - [U46](07-rules.md#u46) Exact constraint (SHOULD)
  - [R7](07-rules.md#r7) Design by selection (SHOULD)
  - [C4](07-rules.md#c4) End-to-end (SHOULD)
  - [C5](07-rules.md#c5) Strict interfaces (SHOULD)
  - [C13](07-rules.md#c13) Weakest-link scaling (SHOULD)
  - [C14](07-rules.md#c14) Structure follows the intended system (SHOULD)
- **D. Protection** — Controls that prevent harm, or contain it when it happens.
  - [U12](07-rules.md#u12) Least privilege (MUST)
  - [U26](07-rules.md#u26) Fail-safe (MUST)
  - [U27](07-rules.md#u27) Hierarchy of controls (SHOULD)
  - [U28](07-rules.md#u28) Error-proofing (SHOULD)
  - [U29](07-rules.md#u29) Defense in depth (SHOULD)
  - [U34](07-rules.md#u34) Compartments (SHOULD)
  - [R6](07-rules.md#r6) Two-person rule (SHOULD)
  - [R9](07-rules.md#r9) Segregation of duties (MUST)
- **E. Capacity and continuity** — How the system keeps working under high load and partial failure.
  - [U25](07-rules.md#u25) Margin (SHOULD)
  - [R1](07-rules.md#r1) Redundancy (N-1) (SHOULD)
  - [R2](07-rules.md#r2) Diversity (SHOULD)
  - [C3](07-rules.md#c3) Graceful degradation (SHOULD)
  - [C6](07-rules.md#c6) Damping (SHOULD)
  - [C7](07-rules.md#c7) Induced demand (SHOULD)
  - [C8](07-rules.md#c8) Bottleneck first (SHOULD)
  - [C11](07-rules.md#c11) Shared demand signal (SHOULD)
  - [U53](07-rules.md#u53) Limit work in progress (SHOULD)
  - [C15](07-rules.md#c15) Late work and added people (SHOULD)
- **F. Verification and review** — How to prove that the work is correct.
  - [U4](07-rules.md#u4) Verification and validation (MUST)
  - [U5](07-rules.md#u5) Find defects early (SHOULD)
  - [U8](07-rules.md#u8) Independent checker (MUST)
  - [U17](07-rules.md#u17) Test as you operate (SHOULD)
  - [U40](07-rules.md#u40) Comparable measurement (SHOULD)
  - [R3](07-rules.md#r3) Traceability (MUST)
  - [C1](07-rules.md#c1) Codes as minimum (MUST)
  - [C10](07-rules.md#c10) Qualified procedure and person (SHOULD)
  - [U56](07-rules.md#u56) Structured selection of people (SHOULD)
  - [U57](07-rules.md#u57) Feedback on the task (SHOULD)
- **G. Change** — How to change the system safely.
  - [U9](07-rules.md#u9) Versioning and change review (MUST)
  - [U19](07-rules.md#u19) Small verified steps (SHOULD)
  - [U36](07-rules.md#u36) Isolation before work (MUST)
  - [U39](07-rules.md#u39) Critical path (SHOULD)
  - [R4](07-rules.md#r4) Observational method (SHOULD)
  - [U58](07-rules.md#u58) Guided change (SHOULD)
- **H. Operation and maintenance** — How to run, watch and maintain the system.
  - [U13](07-rules.md#u13) Monitoring in operation (SHOULD)
  - [U32](07-rules.md#u32) Checklists (SHOULD)
  - [U33](07-rules.md#u33) Critical control points (SHOULD)
  - [U35](07-rules.md#u35) Response faster than harm (SHOULD)
  - [U37](07-rules.md#u37) Maintenance by failure pattern (SHOULD)
  - [U41](07-rules.md#u41) Actionable alerts (SHOULD)
  - [U42](07-rules.md#u42) Sterile critical phase (SHOULD)
  - [C9](07-rules.md#c9) Data as a dependency (SHOULD)
  - [C12](07-rules.md#c12) Asset inventory (SHOULD)
  - [C16](07-rules.md#c16) Span of control (SHOULD)
- **I. Learning** — How to learn from failures and anomalies.
  - [U10](07-rules.md#u10) Blameless root cause analysis (SHOULD)
  - [U11](07-rules.md#u11) Plan-Do-Check-Act (SHOULD)
  - [U18](07-rules.md#u18) Investigate anomalies (SHOULD)
  - [U23](07-rules.md#u23) Preserve evidence (SHOULD)
- **K. Conflict rules** — [K1](08-conflicts.md#k1), [K2](08-conflicts.md#k2), [K3](08-conflicts.md#k3), [K4](08-conflicts.md#k4), [K5](08-conflicts.md#k5), [K6](08-conflicts.md#k6), [K7](08-conflicts.md#k7), [K8](08-conflicts.md#k8)

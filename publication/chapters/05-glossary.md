# 5. Glossary

Each term has exactly one meaning in this file. No other word is used for the same meaning.

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
| robustness | the result changes little when inputs vary within the specification | margin; strictness (rejecting input outside the specification, [C5](07-rules.md#c5)) |
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
| segregation of duties | splitting a process so that no single person controls all its steps | two-person rule (two people at one moment of action, [R6](07-rules.md#r6)) |
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

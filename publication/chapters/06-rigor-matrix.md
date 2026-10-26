# 6. Rigor matrix

Find the cell that matches your system. Universal rules apply in every cell; the master rule scales how strictly. Conditional rules apply in every cell where their condition is true. Risk-scaled rules apply only in the cells listed. MUST rules apply whenever their IF-condition is true.

|  | **Low uncertainty** | **High uncertainty** |
| --- | --- | --- |
| **Low consequence** | all universal rules, conditional rules whose condition is true. Checker level: peer ([P56](07-rules.md#p56)). | all universal rules, conditional rules whose condition is true, [P16](07-rules.md#p16), [P31](07-rules.md#p31), [P68](07-rules.md#p68). Checker level: peer ([P56](07-rules.md#p56)). |
| **High consequence** | all universal rules, conditional rules whose condition is true, [P42](07-rules.md#p42), [P43](07-rules.md#p43), [P45](07-rules.md#p45), [P46](07-rules.md#p46), [P59](07-rules.md#p59). Checker level: external ([P56](07-rules.md#p56)). | all universal rules, conditional rules whose condition is true, all risk-scaled rules. Checker level: external ([P56](07-rules.md#p56)). |

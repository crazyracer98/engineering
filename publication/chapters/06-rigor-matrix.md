# 6. Rigor matrix

Find the cell that matches your system. U-rules apply in every cell; the master rule scales how strictly. C-rules apply in every cell where their condition is true. R-rules apply only in the cells listed. MUST rules apply whenever their IF-condition is true.

|  | **Low uncertainty** | **High uncertainty** |
| --- | --- | --- |
| **Low consequence** | all U-rules, C-rules whose condition is true. Checker level: peer ([U8](07-rules.md#u8)). | all U-rules, C-rules whose condition is true, [R4](07-rules.md#r4), [R7](07-rules.md#r7), [R8](07-rules.md#r8). Checker level: peer ([U8](07-rules.md#u8)). |
| **High consequence** | all U-rules, C-rules whose condition is true, [R1](07-rules.md#r1), [R2](07-rules.md#r2), [R3](07-rules.md#r3), [R6](07-rules.md#r6), [R9](07-rules.md#r9). Checker level: external ([U8](07-rules.md#u8)). | all U-rules, C-rules whose condition is true, all R-rules. Checker level: external ([U8](07-rules.md#u8)). |

# Method

Write the four scores as U00,U10,U01,U11. The interaction contrast is Gamma=U11-U10-U01+U00. Let a=U10-U00 and b=U01-U00 be the isolated gains. The joint gain is J=U11-U00, and the identity J=a+b+Gamma is exact on the declared score scale.

The chapter-defined positive interaction amount is E=max(0,Gamma). It suppresses negative interaction for that specific amount convention but does not erase the signed contrast. Report both. The signed ratio Gamma/J exists when J is nonzero. Its interpretation as a cooperation fraction requires J>0, a>=0, b>=0, and Gamma>=0. Under those conditions the exact decomposition guarantees a ratio between zero and one.

An additive contrast depends on the score scale. A nonlinear transformation can change it, even when intact rankings remain unchanged. Equal budgets support one condition of a matched ablation; unequal budgets confound component status with resource exposure. Neither condition alone proves an internal mechanism or warrants a universal ranking of emergence.

Supply the four scores and four budgets in the documented order. The code checks vector lengths and finite numeric domains, calculates isolated contributions, signed contrast, positive amount, joint gain, and both ratio variants. The fraction field is unavailable when its domain conditions fail.

Two figures show the observed cells and the additive decomposition. The decomposition includes the baseline and contributions, so read its table order carefully. In the changed case the intact configuration receives twice the budget while all scores remain the same. The arithmetic is unchanged; the matched-comparison conclusion changes. This is deliberate: a diagnostic should expose an invalid inference even when the calculator can still evaluate a formula.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.

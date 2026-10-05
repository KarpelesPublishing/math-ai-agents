# Use cases

## Worked example

The default review-release value is -1-0.9+0.9^2(8)+0.9^3(2)=6.038. It completes in three steps within the five-step deadline. Archive gives value 1.

The changed interruption permits only two steps of review-release. Its value becomes -1-0.9=-1.9, completion is false, and no continuation is added. Archive still completes and remains worth 1, so it becomes the preferred executed value. The reversal comes from lost access to the option's terminal benefit, not a change in the release payoff.

## Changed assumption

An option label can conceal an unsafe initiation assumption. If review requires a current document version, a generic initiation flag is insufficient for deployment until that predicate is tied to observed state. Likewise, the returned termination flag is a supplied trace fact, not an automatically verified effect.

Another failure is to discount continuation by one macro step regardless of duration. That exaggerates long options when gamma is below one. The transfer case exposes the difference directly.

An interruption contract should state what remains durable, whether the option can resume, and which action is safe next. This notebook stops at the prefix and does not invent recovery. A partial option can create cost or state change even when its workflow completion flag is false. Preserve that consequence in a larger trace model.

## New inputs

In the transfer case, inspect executes two steps with rewards 0 and 4. At gamma=0.5, its local reward is 2 and its continuation contributes 0.5^2(8)=2, for total value 4. The disabled option executes zero steps despite its attractive nominal reward.

To apply this to your own system, extract primitive duration and reward timing from a compatible declared workflow. Keep initiation, termination, interruption, and deadline conditions explicit. If durations vary, analyze separate traces or extend the model with a documented distribution. Do not replace measured completion with a skill's descriptive name.

## Acceptance invariants

- Default value is 6.038.
- Interruption removes continuation and reverses best option.
- False initiation yields zero executed steps.

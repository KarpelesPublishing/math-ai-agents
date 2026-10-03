# Use cases

## Worked example

At one remaining decision, cash gives 2 and prepare gives -1, so cash wins. At two remaining decisions, preparation gives -1+6=5, while cash still gives 2. With three decisions the value remains 5 because done adds no reward.

The policy table therefore changes at draft when the remaining horizon crosses from one to two. The changed case returns cash at the start with value 2. This is a horizon-driven reversal, not inconsistent arithmetic. A controller that ignores its deadline can select preparation and then run out of opportunities before collecting the release reward.

## Changed assumption

A planning result can be internally exact and operationally wrong because its state model omits a precondition. If release needs current approval, ready must encode that approval or the action set must check it. Reward optimism cannot create a missing permission.

Another failure comes from treating a finite model policy as robust to unknown transition changes. The Bellman recursion uses the supplied kernel at every stage. A tool outage, stale memory, or different counterparty changes that kernel and can reverse action rankings. Model auditing belongs beside planning, not after an inconvenient outcome.

Finally, terminal values can hide unsupported future optimism. With a short horizon, a large terminal estimate may dominate the apparent plan. Report whether terminal continuation is zero, a measured estimate, or a judgment, and inspect sensitivity before acting.

## New inputs

The transfer problem discounts future reward by 0.5. Taking one now gives value 1. Waiting and collecting 4 next step gives 0+0.5(4)=2, so later wins with two decisions remaining. With one remaining decision, waiting gives zero and now wins.

For local use, begin with a state model small enough to inspect. Include deadline, authority, or tool status when they affect future choices. Export the policy stage corresponding to the actual remaining horizon, together with its alternatives and transition assumptions. A policy for three remaining steps is not automatically valid after one step has already been spent.

## Acceptance invariants

- Draft policy switches cash to prepare between horizons 1 and 2.
- Done value remains zero.
- Unknown next states are rejected.

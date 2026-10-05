# Use cases

## Worked example

Default review load is 4(0.5)=2, below service rate 3. Mean sojourn is 1/(3-2)=1 time unit. Routine is authorized and below the agent risk limit, so it can proceed autonomously. Release requires delegation but has human authority and a received review, with deadline 2 exceeding the mean diagnostic, so it passes the declared release contract.

Sensitive lacks a received review and requires a packet. With delegated fraction 0.9, review load becomes 3.6, exceeding capacity. The stationary mean is unavailable and delegated release is blocked by the capacity plan. Routine remains autonomous. Review capacity did not change the underlying authority predicate.

The mean-versus-deadline flag is a planning diagnostic, not a probability of meeting the deadline. If the M/M/1 first-come-first-served assumption held exactly, sojourn time would be exponential with rate 3-2=1, so with deadline 2 the chance of meeting it would be 1-exp(-2), about 0.865, even though the mean 1 is below 2. This probability is a hand calculation, not a field the lab reports.

## Changed assumption

Delegation can fail when it becomes an automatic escape from uncertainty without a capacity model. Sending every doubtful task to a fixed reviewer raises arrival load and can make the queue unstable. The sensitivity curve shows that even stable load near capacity creates large mean delays.

A queue calculation can also be overread. M/M/1 assumes Poisson arrivals, exponential service, one reviewer, and stationary rates. Real review teams may batch work, prioritize cases, or have correlated arrivals. A single mean cannot prove deadline compliance or determine an actual task's elapsed review time.

Authority remains independent. A review receipt from someone without the required permission cannot authorize release. Conversely, the method's mean-time flag is not evidence that an already received review was late. Preserve actual timestamps for empirical deadline checks and use this output as a capacity-design diagnostic.

## New inputs

The transfer review load is 1 with service rate 2, so mean sojourn is 1. The task deadline is 0.5, below that planning mean. Despite human authority and a declared receipt, the simplified capacity contract does not approve release. This flags the planning mismatch rather than asserting the actual receipt arrived after 0.5.

As a next step, draft a handoff packet containing current state, missing authority, risk, observations, proposed action, and deadline. Do not send it automatically from this computation. Measure real arrival and service patterns before adopting the queue law, and preserve review timestamps when evaluating individual deadline outcomes.

## Acceptance invariants

- Default mean is 1 under stable load.
- Overcapacity mean is unavailable.
- Missing review receipt blocks delegated release.

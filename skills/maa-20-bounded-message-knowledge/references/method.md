# Method

Each round has two potential delivery bits: request delivery and acknowledgement delivery. An acknowledgement exists only when that round's request arrives. With R rounds, the enumeration contains 2^(2R) constructed bit worlds. Their weights multiply independent delivery or drop probabilities.

A party's view contains its local sends, received messages, and round ticks. Two worlds are indistinguishable to that party when these views match. Alice knows delivery in a world if every positive-probability world with her view contains at least one received request. Bob knows Alice received an acknowledgement only if every world with his view contains that acknowledgement receipt.

Agreement compares Alice's acknowledgement-based commit with Bob's request-based commit. Disagreement occurs when Bob received some request but Alice received no acknowledgement. With drop probability d, its probability after R rounds is [1-(1-d)^2]^R-d^R. The first term means no successful request/ack pair; the second removes worlds where no request arrived at all. This is a bounded protocol calculation under a specific independent-drop law.

Supply a round budget and message-drop probability. The code enumerates bit histories, builds local views, and retains only positive-probability worlds for knowledge tests. Excluding impossible worlds matters at d=0 or d=1, where the declared probability model itself rules out certain histories.

The metrics report world counts, agreement, Alice's delivery knowledge, Bob's acknowledgement-receipt knowledge, and Bob-only commitment. The chart uses request rounds on the horizontal axis and agreement probability on the vertical axis. Compare its analytic values with the enumerated final metric. In the changed case set drops to zero; predict how the possible-world set shrinks before rerunning. The transfer case checks a longer budget at a different loss probability.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.

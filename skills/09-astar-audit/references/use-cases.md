# Use cases

## Worked example

The default shortest route is S,B,G with cost 2+1=3. The heuristic matches true remaining distances and is both admissible and consistent. A* expands toward B and reaches the cheaper goal.

In the changed case h(B)=10 exceeds B's true remaining cost 1. The A branch looks cheaper to the queue, so the first popped goal follows S,A,G and costs 5. The exact graph optimum remains 3. The algorithm has not disproved A*; the supplied heuristic violated the condition needed for its optimality guarantee. The audit makes that violation visible beside the result.

## Changed assumption

An inadmissible heuristic can still return an optimal path on some graphs. That coincidence does not validate its contract. Conversely, a zero heuristic can be perfectly valid while offering no guidance beyond uniform-cost search. Evaluate correctness conditions separately from observed expansion savings.

The full-graph diagnostic itself has a cost and requires knowledge that may not exist in an open-ended planning problem. Do not claim the audit certifies an unknown environment. Its scope is the supplied finite graph and its declared edges.

A path can also be cheaper in edge units while more expensive in wall time, authority, or tool use. If those quantities matter, encode a justified cost model or report them separately. Adding incompatible units into one number without a valuation rule makes an apparently optimal path meaningless.

## New inputs

The transfer graph uses a zero heuristic. A* becomes uniform-cost search and finds source,middle,target with cost 4 instead of the direct cost 7. This is a useful baseline: correctness does not depend on a sophisticated heuristic.

For reader data, preserve directed costs and distinguish unavailable edges from expensive edges. If you propose a heuristic, explain why it is a lower bound or label it as an unguaranteed guide. Compare its returned path with a small exact case and account for computation expense. Use graph reachability first when the main question is permission rather than cheapest continuation.

## Acceptance invariants

- Default path cost equals exact 3.
- Misleading heuristic returns 5 with audit failure.
- Negative edge costs are rejected.

# Method

A\* orders queued states by f(n)=g(n)+h(n), where g is the best discovered path cost from the start and h estimates remaining cost. An admissible heuristic satisfies h(n)<=d\*(n,goal). A consistent heuristic satisfies h(u)<=c(u,v)+h(v) for every edge and h(goal)=0.

With nonnegative costs and an admissible heuristic, a search that reopens improved states can stop when the goal is popped and recover an optimal path. The chapter's worked graphs assume strictly positive edge costs; this finite-graph implementation also accepts zero-cost edges. That is a deliberate, valid widening: a state is queued again only when its g strictly improves, so the search terminates on a finite graph even with zero-cost cycles, and with an admissible heuristic the first popped goal is still optimal. The chapter's statements that rely on a positive-cost step are not claimed for zero-cost edges. Consistency is a stronger local condition that simplifies the behavior of expanded states. The implementation permits reopening by inserting a state again whenever its best g improves; obsolete queue entries are skipped.

The audit computes exact remaining costs using Dijkstra's algorithm on reversed edges. This is feasible because the teaching graph is fully known. It does not mean a deployed search gets an optimal heuristic for free. Path cost, expansion count, and declared heuristic expense are separate metrics with separate units. A faster search can still consume more total compute if each heuristic call is expensive.

Register nodes and nonnegative weighted directed edges. Give every node a finite nonnegative heuristic. The function first calculates exact graph distances for diagnostic comparison, then runs A* using the supplied values. It records each expanded node's g and f, reconstructs the first popped goal path, and counts heuristic calls.

The plot shows the g cost of successive expansions. It is a search-order trace, not a monotonic convergence curve. Consult the returned path cost and exact optimal cost together. In the changed case only B's heuristic rises. Predict which goal will be popped first and whether the admissibility check will pass. Keep the separate heuristic-total-cost metric when comparing implementations.

## Apply this to an agent

Represent the agent's candidate plans as routes with explicit costs. Check whether a heuristic can overlook a cheaper plan, and include the cost of computing the heuristic. A good-looking estimate is not a certificate of admissibility.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.

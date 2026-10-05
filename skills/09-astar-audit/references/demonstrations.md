# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C09-D01: Following the search one selection at a time

What does the search record, select and update at each step, and where does a recorded cost get corrected?

**Source section:** The trace, worked

**Application:** When an agent reaches the same state by two sequences of tool calls, keep one best cost for that state and update it only when a strictly cheaper sequence appears. The record is then a trustworthy upper bound.

**Assumptions:** Edge costs are fixed, known and positive, and a repeated vertex is the same state however it was reached. That fails when the cost of a step depends on the history, for example a deadline or a tool whose price changes with use. The bookkeeping graph names no goal in the chapter; B is taken as the goal here so that the trace ends.

**Declared default controls:**

```json
{
  "trace": "fig91",
  "step": 1
}
```

**Supported values:**

- `trace`: ['fig91', 'zero', 'flow']
- `step`: [1, 2, 3, 4]

**Evidence:** constructed teaching example

Constructed example: the chapter's four-vertex trace (edge costs 3, 7, 2 and 3, where 7 becomes 6), its two-route zero-estimate table and its research workflow (costs 1, 2, 4; estimates 2, 1, 1, 0), each checked against the laboratory's A* function.

## C09-D02: One overestimate can hide the cheaper route

How far can the estimate at one vertex exceed its true remaining cost before the search returns the dearer route, and which vertices does the exact f single out?

**Source section:** The condition that makes it correct

**Application:** Before describing a search as optimal, ask whether any estimate in it can exceed the true remaining cost. One high estimate on the wrong branch is enough to lose the best route. The notebook's default and changed cases are the second and fourth levels of the notebook graph (estimates 1 and 10 at B), and its transfer case is the first level of the transfer graph.

**Assumptions:** The graphs, costs and queue rules are fixed as stated. A broken Equation (9.3) can still return the best route, as the middle levels show, and on other graphs the threshold would differ. Ties in score are broken by smaller cost so far, then by label. Only one vertex's estimate is varied; the others keep the case's values.

**Declared default controls:**

```json
{
  "case": "tworoute",
  "level": 1
}
```

**Supported values:**

- `case`: ['tworoute', 'notebook', 'transfer']
- `level`: [0, 1, 2, 3]

**Evidence:** constructed teaching example

Constructed example: the chapter's two-route graph (costs 1, 9, 1, 24), the laboratory notebook's default and changed graph (heuristic at B 1 and 10) and transfer graph (zero estimates), with other estimate levels defined for this reader; every search is also run through the laboratory's A* function.

## C09-D03: An estimate must not contradict itself

How far may the estimate fall across an edge before it breaks the consistency condition?

**Source section:** The condition that makes it efficient

**Application:** When two estimates are produced separately for neighbouring states, compare their difference with the cost of the step between them. A difference larger than the step is a sign that the estimator disagrees with itself.

**Assumptions:** Only the local fragment is drawn: no goal routes are shown, so it cannot tell you whether either estimate is admissible, which route is best, or whether a vertex will be reopened. A consistent estimate can still be wrong about the remaining cost; it only cannot be wrong in a self-contradicting way.

**Declared default controls:**

```json
{
  "h_upper": 1,
  "h_start": 7
}
```

**Supported values:**

- `h_upper`: [1, 2, 5, 8]
- `h_start`: [8, 7, 6]

**Evidence:** constructed teaching example

Constructed example: the chapter's consistency fragment (start estimate 8, edges costing 6 and 3, estimates 1 and 5), with the start's estimate and the upper estimate varied; the consistency flag is also checked with the laboratory's A* function.

## C09-D04: What an estimate buys and what it costs

How many expansions does an estimate save compared with guessing zero, and does that pay once computing the estimate costs time?

**Source section:** When the estimate costs more than the vertex

**Application:** Price the estimate in the same unit as the step it is meant to avoid. If scoring a candidate takes a model call, compare it with the tool call, and consider scoring candidates in batches or only when the choice is close.

**Assumptions:** Constant costs per call, and expansion counts that come from these small graphs, not from measurement. Queue work, storage and batching are left out. The 200 ms figure and the 900 ms estimate are the chapter's constructed example; 100 and 400 ms are values chosen for this reader. Theorem 2 compares algorithms with the same information, no ties and a consistent estimate.

**Declared default controls:**

```json
{
  "graph": "notebook",
  "price": 900
}
```

**Supported values:**

- `graph`: ['notebook', 'tworoute', 'workflow']
- `price`: [0, 100, 400, 900]

**Evidence:** constructed teaching example

Constructed example: the chapter's constructed agent latencies (a 200 ms tool call, a 900 ms estimate) applied to the notebook graph, the chapter's two-route graph and its research workflow, with expansions counted by the chapter's queue rules and checked against the laboratory's A* function.

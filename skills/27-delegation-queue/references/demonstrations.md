# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C27-D01: Defer by comparing correctness, then price the deadline

If the model is 0.78 sure, when should the case go to an expert instead, and does the expert's accuracy alone settle it once the answer has to arrive in time?

**Source section:** A value comparison, not a confidence threshold

**Application:** A single confidence threshold such as 0.80, below which everything is sent to review, is justified only if the destination's correctness and timeliness are the same for all the cases it covers. Otherwise ask how likely the actual destination is to be right on this kind of case, how likely it is to answer in time, and compare with acting.

**Assumptions:** Zero-one loss for Equation (27.2), one expert, and a known expert probability for this case type. The classifier's confidence is assumed calibrated. The utilities, fee and fallback value come from the workbench's constructed problem and are applied here to all four cases for comparison. The expert's accuracy is conditional on a timely reply and is not a permanent rating; if the probability is only a rough average, or the packet omits the evidence the expert needs, the comparison is no better than its inputs.

**Declared default controls:**

```json
{
  "case": "chapter",
  "timely": 1.0
}
```

**Supported values:**

- `case`: ['chapter', 'general', 'bench', 'tie']
- `timely`: [1.0, 0.6, 0.7142857142857143]

**Evidence:** constructed teaching example

Constructed example: the chapter's two cases (model 0.78, expert 0.95 or 0.60) and the workbench's timely-return problem (acting 0.80, utilities 10 and -10, fee 1, fallback 2).

## C27-D02: Four routes, but only the authorized ones can run

Which routes are in the authorized set, which of them has the highest net value, and what removes a route?

**Source section:** Queue economics: what timely review is worth

**Application:** Write the table for a consequential action: one row per route, each with its payoff, delay cost and fallback, and next to each row the grant that authorizes it and the precondition it needs. Then keep only the rows that are actually permitted. A delegation row also needs a named destination, a deadline and a fallback; without them it is not a route.

**Assumptions:** Utilities, fraud probability, review error rates (detect fraud 0.94, wrongly reject 0.02) and response probabilities are the chapter's constructed values, and all four routes are costed on one scale. Real stakes may not fit one scale; a hard boundary may belong in the authorized set rather than in a cost. Changing any stated probability can change the winner. The reviewer accuracy here is held fixed, although in practice it can change with workload.

**Declared default controls:**

```json
{
  "hold_cost": 2,
  "status": "all"
}
```

**Supported values:**

- `hold_cost`: [2, 4, 5]
- `status`: ['all', 'holdno', 'unavail', 'stopped']

**Evidence:** constructed teaching example

Constructed example: the book's own route-value table for the pending transfer (values -1, 1.164, 2 and 4.438), with the hold cost and the authority status varied.

## C27-D03: Delegating more can make review slower than the deadline

How does sending a larger share of tasks to one reviewer change the mean time in review, and which tasks can then be released?

**Source section:** Queue economics: what timely review is worth

**Application:** Before promising a review deadline, compare the planned review load with the reviewer's capacity. A rule such as delegate everything doubtful can overload the one route that was supposed to supply safety. Keep a route ledger per destination, with case type, deadline, packet completeness, response state and final action, so a failure can be placed: a bad recommendation, a wrong destination, a late answer or an unowned escalation.

**Assumptions:** The M/M/1 model: one reviewer, independent random (Poisson) arrivals at a steady rate, exponentially distributed service times with a steady rate, and a long-run mean. Other service-time shapes give a different formula. Batching, priorities, correlated arrivals or a changing reviewer break the model. A mean does not promise that any single case meets its deadline, and the laboratory's deadline test is a planning diagnostic, not a probability. The faster reviewer is defined for this reader.

**Declared default controls:**

```json
{
  "case": "default",
  "delegation_fraction": 0.5
}
```

**Supported values:**

- `case`: ['default', 'fast', 'transfer']
- `delegation_fraction`: [0.5, 0.7, 0.9, 1.0]

**Evidence:** constructed teaching example

Constructed example: the notebook's default, changed and transfer cases and the chapter's queue example (4 tasks per hour, a reviewer finishing 3 per hour), computed with the laboratory's review-queue function, plus one faster reviewer defined for the reader.

## C27-D04: Waiting needs an observation worth its delay and a fallback everywhere

When is it right to wait for a confirmation instead of acting now, and what if one state reachable by the deadline has no authorized fallback?

**Source section:** Waiting is not hiding

**Application:** When an agent says it will wait, ask four things: which fact would change the action, who supplies it, by when, and what happens if it never comes. If any answer is missing, there is no waiting action, only delay. If the observation source has become unavailable, move to the declared fallback instead of waiting under a plan that assumes its arrival.

**Assumptions:** One observation and the chapter's constructed values (9, -1, delay cost 2). VOI is read here as the gain over releasing now, a simple special case of the Chapter 8 idea. The four reachable states are the ones the chapter lists; a real case can have more. Equation (27.4) is a necessary test: passing it does not make waiting the best route.

**Declared default controls:**

```json
{
  "arrival_probability": 0.5,
  "gap": "none"
}
```

**Supported values:**

- `arrival_probability`: [0.2, 0.5, 0.8]
- `gap`: ['none', 'late', 'changed', 'failed']

**Evidence:** constructed teaching example

Constructed example: the chapter's wait route (value 9 on arrival, -1 at the fallback, delay cost 2) with the arrival probability and the missing-fallback state varied.

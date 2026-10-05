# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C21-D01: A free link: better, worse or unchanged

When a zero-latency link is added, why does the stable pattern of choices differ from the best one, and how does that depend on demand?

**Source section:** A free connection changes what best means

**Application:** Before adding a shared shortcut such as a common reviewer, a shared tool or a fast lane, ask what everyone will do once it exists, not whether one case could finish faster against yesterday's traffic.

**Assumptions:** One unit-scale network with linear congestible edges, many small travellers who each pick the cheapest route, and a total-delay objective. It does not say that any real shortcut, tool or team behaves this way. In this construction the paradox disappears once demand is large enough to make the outer routes as slow as the middle route (the two totals tie at demand 2); this is a result of the reader's computation, not a statement of the chapter.

**Declared default controls:**

```json
{
  "demand": 1,
  "network": "link"
}
```

**Supported values:**

- `demand`: [0.5, 1, 1.5, 2]
- `network`: ['link', 'nolink']

**Evidence:** constructed teaching example

Constructed example: the chapter's one-unit network with demand varied, with and without the link; equilibrium and optimum are computed with the laboratory's congestion function.

## C21-D02: How bad can it get with linear delays

Across every demand, how large can the ratio of equilibrium delay to optimal delay be when every delay is linear, and where does the gap come from?

**Source section:** What linear bound says, and what it does not

**Application:** When someone quotes a worst-case ratio for a queue or workflow, first check that its delays really are linear over the range of load the team will see. A ratio proved for one class of delay says nothing outside that class.

**Assumptions:** The same one-unit network with the middle link given a constant delay. The bound applies because every delay stays linear. The chapter notes that if delays are only continuous and nondecreasing, the ratio can be unbounded; thresholds, retry storms and sudden queue growth may not have the linear form, in which case the 4/3 figure is not guaranteed.

**Declared default controls:**

```json
{
  "overhead": 0
}
```

**Supported values:**

- `overhead`: [0, 0.25, 0.5, 1]

**Evidence:** constructed teaching example

Constructed example: the chapter's network with a middle-link delay defined for this reader; ratios and flows are computed with the laboratory's congestion function.

## C21-D03: Charging for the delay you export

If every congestible edge charges its own delay plus the delay the traveller adds for others, where does the equilibrium land, and how does a toll on the link alone compare?

**Source section:** Prices that make group target locally legible

**Application:** In a shared workflow, the charge might be a rising budget for a busy shared tool, a queue-aware scheduler or a concurrency limit. The common property is that a local choice receives a signal about the shared resource it uses.

**Assumptions:** Linear delays, a total-delay objective, and a charge that is paid but not counted as physical delay. A real signal can be late, noisy, gameable or attached to the wrong boundary, and the objective may omit fairness or safety. The chapter treats the construction as proof that one gap can be closed under stated conditions, not as a general policy answer.

**Declared default controls:**

```json
{
  "rule": "marginal",
  "demand": 1
}
```

**Supported values:**

- `rule`: ['none', 'marginal', 'toll', 'toll49']
- `demand`: [1, 0.75, 0.5]

**Evidence:** constructed teaching example

Constructed example: the chapter's network and its marginal-cost charge at the laboratory's default demand 1, a changed toll and the transfer demand 0.5; the no-charge and toll cases use the laboratory's congestion function, and the marginal-cost flows are derived here and checked against the laboratory's optimum.

## C21-D04: Capacity is a comparison, not a cure

How does the cost of selfish routing at rate r compare with the best routing that must carry extra traffic?

**Source section:** Capacity is a comparison, not a cure

**Application:** In a staffing meeting, separate delay caused by too little throughput from delay caused by a rule that steers work into one stage. More capacity can lower delay at a given flow, but it can also make a stage attractive to more work and shift the equilibrium again.

**Assumptions:** The chapter's linear network and the rates r = 0.5, 0.75 and 1. The guarantee is a bound over all networks in its class, and this network does not come close to it, so the picture shows the comparison, not tightness. It says nothing about adding capacity to a real system, where demand responds.

**Declared default controls:**

```json
{
  "rate": 1,
  "extra": 0.5
}
```

**Supported values:**

- `rate`: [0.5, 0.75, 1]
- `extra`: [0.25, 0.5, 1]

**Evidence:** constructed teaching example

Constructed example: the chapter's network at rates defined for this reader; all costs are computed with the laboratory's congestion function.

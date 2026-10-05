# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C05-D01: Six assemblies around one frozen model

If the model never changes, how can six assemblies of it succeed at different rates, and what does the budget have to do with it?

**Source section:** The fair experiment

**Application:** When someone says an agent is better because it has memory or tools, ask which later decision reads their output. A component that sits on no path from the model's output to the outcome contributes exactly zero.

**Assumptions:** At most two model calls, a tool that is either granted or denied, and the response laws above, which hold in every row. The six bars are assembly comparisons, not a matched factorial design: row 5 also adds recurrence, so the rows do not identify a memory and tool interaction. The rejection rule matters: if denial sends the run to a second blind call, row 6 equals row 4, not row 1. Nothing here says deployed effect sizes look like these. The one-call state is the chapter's own rule (a request on the last call terminates) applied to a smaller budget.

**Declared default controls:**

```json
{
  "request": 0.4,
  "rejection": "stop",
  "calls": 2
}
```

**Supported values:**

- `request`: [0.2, 0.4, 0.6]
- `rejection`: ['stop', 'blind']
- `calls`: [2, 1]

**Evidence:** constructed teaching example

Constructed example: the chapter's six-assembly experiment; the default 0.40 request probability gives the book's values 0.30, 0.42 and 0.61.

## C05-D02: A fixed chooser, a different tool, a different system

If the chooser's probabilities never change, can changing only the tool change where the system spends its time?

**Source section:** The law the model does not contain

**Application:** When a model is blamed or credited for a change in behavior, ask which factor changed. Here the chooser rows are identical in the default and changed systems, so every difference in the curves is a consequence of the tool, not of the model.

**Assumptions:** Two states, two proposals, no permission or budget coordinate, and a tool law that depends on the state only through the proposal. If the next state also depends on something the state leaves out, such as a memory version, the composite kernel is not a valid description and more transitions will not repair it.

**Declared default controls:**

```json
{
  "system": "default",
  "transitions": 2
}
```

**Supported values:**

- `system`: ['default', 'changed', 'transfer']
- `transitions`: [1, 2, 3, 30]

**Evidence:** constructed teaching example

Constructed example: the laboratory's default chooser and tool matrices, the changed tool, and the notebook's transfer case (identity chooser, tool rows [0.7, 0.3] and [0.4, 0.6], start half in each state), computed with its composite-kernel function.

## C05-D03: What an observation is worth, and what a memory may drop

How many bits does the tool's report deliver, does delivering them change the outcome, and what happens if the memory drops the report?

**Source section:** What an observation is worth

**Application:** For every piece of information a system collects, name the decision it changes. If no decision changes, the collection is decoration, however many bits it carries. Before a summary replaces a record, check that the states it merges send the same probabilities into the same classes.

**Assumptions:** One hidden bit with equal prior, a symmetric tool, and the informed response law held at the book's values for every accuracy. That includes 0.50, where the report carries no information but the declared law still responds to it, because the law is held fixed by construction. Mutual information is symmetric and not causal, and it measures uncertainty removed, not usefulness. Dropping the report entirely is the extreme case of a lossy memory; a partial summary would sit between the two connected rows.

**Declared default controls:**

```json
{
  "accuracy": 0.9,
  "reaches": "stops"
}
```

**Supported values:**

- `accuracy`: [0.5, 0.75, 0.9, 1.0]
- `reaches`: ['stops', 'dropped', 'reaches']

**Evidence:** constructed teaching example

Constructed example: the chapter's tool with accuracy 0.90 (about 0.531 bits) and the blind and informed response laws it declares; other accuracies are values defined for the reader.

## C05-D04: Recurrence multiplies

If every step is very likely to succeed, how long a task can still survive, and what if the steps share a cause?

**Source section:** Recurrence multiplies

**Application:** Before promising a long unattended task, ask what the per-step success is after the controller's own detection and recovery, not for the model's average accuracy on isolated questions.

**Assumptions:** Constant conditional success and independent retries that use the same budget coordinate (each retry costs budget the chain here does not track). If failures share a cause, such as bad evidence, a retry fails for the same reason and q improves less than shown. The shared-cause line is one constructed joint law with the same marginals, not a model of any real agent. Marginal step accuracies alone do not justify this product.

**Declared default controls:**

```json
{
  "case": "p99",
  "handling": "none"
}
```

**Supported values:**

- `case`: ['p95', 'p99', 'p999', 'transfer']
- `handling`: ['none', 'retry', 'shared']

**Evidence:** constructed teaching example

Constructed example: the chapter's compounding values (0.99 over 40 steps is 0.669, 0.95 is 0.129) and half-success horizons (about 14, 69 and 693 steps), computed with the laboratory's chain function; the retry rule is a construction defined for the reader, and the transfer case is the notebook's (rates 0.9, 0.8, 0.7).

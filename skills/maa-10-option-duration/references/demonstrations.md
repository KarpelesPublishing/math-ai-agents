# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C10-D01: An option has three parts

Where may an option start, how long does it run once it has started, and what does a blocked start earn?

**Source section:** A skill is not a label

**Application:** Before calling a workflow a reusable skill, write down all three: where it may begin, what it does at each step, and what event hands control back. A workflow with a name but no stated stopping rule has not yet been defined as an option.

**Assumptions:** A row of 8 start states, one record checked per step, and a missing approval that is met at a fixed number of records remaining. A start state at or below the stop level runs to the end, so durations need not rise steadily with x. Real options act on richer state, and their stopping may depend on what they see. The start rules and stop levels here are declared examples, not rules from the chapter.

**Declared default controls:**

```json
{
  "min_records": 1,
  "stop_at": 0
}
```

**Supported values:**

- `min_records`: [1, 4, 7]
- `stop_at`: [0, 2, 4]

**Evidence:** constructed teaching example

Constructed example: a record-checking option defined for this reader to illustrate the three parts in Equation (10.1).

## C10-D02: Discount by the steps the option really took

How much does the value rise when the continuation after an option is discounted as if it took one step?

**Source section:** Value when duration varies

**Application:** When comparing a one-step action with a multi-step skill, put both on the same clock. A skill that takes five steps to return should not get the continuation value of one that returns immediately.

**Assumptions:** The duration is known and the option always reaches its end. Rewards are paid at primitive steps and the first is undiscounted. The discount is per step, not per minute: wall-clock time needs its own model. Steps after the second pay 0 here, a constructed choice to make the duration vary.

**Declared default controls:**

```json
{
  "case": "chapter",
  "duration": 2,
  "gamma": 0.9
}
```

**Supported values:**

- `case`: ['chapter', 'transfer']
- `duration`: [2, 3, 4]
- `gamma`: [0.5, 0.9]

**Evidence:** constructed teaching example

Constructed example: the chapter's worked numbers (rewards 2 and 3, continuation 10, discount 0.9, also its Exercise 1) and the workbook transfer case (rewards 0 and 4, continuation 8, discount 0.5), with the duration and discount varied, computed with the laboratory's option function.

## C10-D03: Release time is not release cost

If one activity runs beside the others, how can the release be early while the cost stays the same, and what does a stale verification add?

**Source section:** A release workflow has two totals

**Application:** When a controller says a workflow is cheap or fast, ask which total is meant. A plan can be fast by running work side by side; running it in sequence is slower but, in this example, costs the same.

**Assumptions:** Fixed durations and costs with no waiting for tools, no failures and no shared resource between the parallel activities. The sequential schedule and the revalidation (3 minutes, 7 credits) are variations added here, not in the chapter. The chapter's own case is a 4 minute audit in parallel with an unchanged source. Real durations vary and credits may depend on the order of work.

**Declared default controls:**

```json
{
  "audit_minutes": 4,
  "mode": "parallel",
  "source": "same"
}
```

**Supported values:**

- `audit_minutes`: [4, 6, 8]
- `mode`: ['parallel', 'after']
- `source`: ['same', 'changed']

**Evidence:** constructed teaching example

Constructed example: the chapter's release workflow (Equation 10.3, 6 minutes and 16 credits) with the audit length and the schedule varied; the stale completion follows the chapter's v17 and v18 account, and its revalidation cost is defined for this reader.

## C10-D04: An interrupted option is scored here without continuation

If an option is stopped early, how much of its value survives, can the preferred option change, and what does an option that cannot start earn?

**Source section:** Interruption changes what completion means

**Application:** A parent controller should treat an interrupted skill as a different outcome from a finished one and plan from the state it actually reached, with a stated cancellation or recovery step.

**Assumptions:** Rewards, durations and the interruption point are given, not random. The chapter warns that an interruption can leave effects behind (spend, writes) and that cancellation needs an acknowledgement. This calculation shows only the value of the executed steps (the reached state is valued at 0 by stipulation) and says nothing about how to clean up.

**Declared default controls:**

```json
{
  "case": "none",
  "gamma": 0.9
}
```

**Supported values:**

- `case`: ['none', 'two', 'one', 'transfer']
- `gamma`: [0.9, 0.5]

**Evidence:** constructed teaching example

Constructed example: the laboratory's review-release and archive options, using the laboratory's example values (6.038 complete, -1.9 interrupted after 2 steps, at discount 0.9), a second discount, and the workbook transfer case (inspect worth 4 at discount 0.5, a disabled option worth 0), computed with the laboratory's option function.

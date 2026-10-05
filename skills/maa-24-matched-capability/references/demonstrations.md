# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C24-D01: Observations, denominators and estimands

What do these observations support, and which quantities change when the sample size, the pairing or the target mixture changes while the records stay the same?

**Source section:** The matched question is not the same question twice

**Application:** Before reporting that a procedure improved, report each denominator, the number of matched pairs, the interval and the target mixture, so a reader can tell a real discrepancy from a thin sample, a missing cell or a changed population.

**Assumptions:** The two-bank interval needs independent samples with adequately populated pass and fail counts and does not cover choosing the largest gap after inspecting many models. The paired standard error and the Wilson intervals need independent representative pairs or runs, which repeated runs of the same task may violate; identifiers declare pairing, not randomization. The aged-benchmark mixture is the chapter's declared construction, not a measured contamination effect.

**Declared default controls:**

```json
{
  "case": "book",
  "reading": "scores"
}
```

**Supported values:**

- `case`: ['book', 'lab', 'transfer', 'aged']
- `reading`: ['scores', 'gap', 'weights']

**Evidence:** constructed teaching example

Constructed example: the book's teaching counts (320 and 292 passes out of 400, not GSM1k measurements), the laboratory's default, changed and transfer record cases evaluated with the laboratory's own function, and the chapter's constructed aged-benchmark mixture (0.4 unfamiliar, 1.0 exposed, 20 percent exposed).

## C24-D02: An onset belongs to its threshold

If a score rises gradually with scale, how much does the reported onset of a capability depend on the chosen threshold and on which sizes were tested?

**Source section:** Scale profiles and extraction profiles are different maps

**Application:** When someone reports that an ability appears at a certain size, ask for the continuous curve, the threshold, and the onset at two or three nearby thresholds. If the onset moves a lot, say the onset is threshold-sensitive.

**Assumptions:** One constructed curve of eight ordered members under one stable protocol, with no sampling noise on g. A crossing is an operational record, not a certified phase transition. Real scores carry uncertainty that could move a crossing by itself.

**Declared default controls:**

```json
{
  "threshold": 0.5,
  "tested": "all"
}
```

**Supported values:**

- `threshold`: [0.3, 0.5, 0.6, 0.7]
- `tested`: ['all', 'odd', 'even']

**Evidence:** constructed teaching example

Constructed example: eight family scores defined for this reader (0.04, 0.09, 0.17, 0.30, 0.46, 0.58, 0.66, 0.71), not a measured scale profile.

## C24-D03: A lower frontier is evidence, not a ceiling

If several configurations are tested, what can we claim for the best one after paying for having looked at all of them?

**Source section:** A frontier is lower evidence, not a final ceiling

**Application:** If a program tries several prompts, tools or budgets, report how many were tried and use a margin that pays for the search, instead of presenting the highest score as if it were the only planned comparison.

**Assumptions:** The margin used here is one way to build the joint bound: a one-sided Hoeffding deviation for independent tasks scored between 0 and 1, with the failure budget split equally by a union bound. Other designs give other margins. If tasks are dependent, the independence-based margin is no longer justified (and may be too small under positive dependence).

**Declared default controls:**

```json
{
  "tasks": 400,
  "tested": 4
}
```

**Supported values:**

- `tasks`: [100, 400, 1600]
- `tested`: [2, 3, 4]

**Evidence:** constructed teaching example

Constructed example: four configuration success rates (0.60, 0.68, 0.72, 0.74) defined for this reader, not results for any real system.

## C24-D04: Same average, different reliability

If two banks of tasks both average 0.50 per run, do they give the same chance that repeated runs succeed, and what do the observed runs of one task give?

**Source section:** The same average can describe different reliability

**Application:** When a report gives one average success rate and then claims reliability over repeated runs, ask for the task-level repeat results. The pooled average cannot answer a question about repetition.

**Assumptions:** Two constructed tasks, equal weights, runs independent given the task and a frozen procedure. It fails when runs share a cached error, quota or evaluator fault, and it says nothing about a selector that must choose among the runs before the answer is known. The subset fractions are unbiased only under independent, identically distributed trials for that fixed task; otherwise they are descriptive fractions of the bank, and if fewer than k runs exist the subset metric is unavailable.

**Declared default controls:**

```json
{
  "bank": "0.20",
  "runs": 2
}
```

**Supported values:**

- `bank`: ['0.50', '0.20', '0.10', 'recorded']
- `runs`: [2, 3]

**Evidence:** constructed teaching example

Constructed example: the chapter's two-task construction (0.2 and 0.8, mean 0.5) with other spreads and run counts added for this reader, and the recorded bank of three successes and one failure from Mathematical Workbench E.5, part 3.

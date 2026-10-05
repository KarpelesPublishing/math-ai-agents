# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C25-D01: A canary is monitored evidence, and its rules come first

If an accepted version enters a limited release, when does it roll back, and what changes if the rule is chosen after the numbers are seen?

**Source section:** Acceptance is a constrained release decision

**Application:** Before a canary starts, write the monitoring cadence, population, metric, alert threshold, maximum duration, decision after an alert, and the fallback route. A canary is monitored evidence after acceptance, not a cheap second chance to pass the guard.

**Assumptions:** One constructed cost metric, eight periods, one trigger type. The chapter also names a safety violation, a verifier failure, a decline in a monitored outcome and a missing authority condition as triggers; each needs its own pre-declared rule. A pre-declared boundary protects against moving the rule after the outcomes, but it does not by itself stop leakage through redesign, metric changes or holdout peeking, and a valid sequential procedure is a separate matter.

**Declared default controls:**

```json
{
  "trace": "creeping",
  "rule": "declared",
  "fallback": "restore"
}
```

**Supported values:**

- `trace`: ['steady', 'creeping', 'spike']
- `rule`: ['declared', 'after']
- `fallback`: ['restore', 'hold']

**Evidence:** constructed teaching example

Constructed example: canary cost traces, an eight-period duration and a cost limit with margin defined for this reader around the chapter's rollback and monitoring rules.

## C25-D02: Development chooses, the guard checks one frozen pick

Once development has picked a winner, what does a separate guard set decide, and what breaks if the guard picks or is reused?

**Source section:** Development can choose a candidate; it cannot certify one

**Application:** Write down which candidate is frozen, and the threshold, before anyone opens guard outcomes. Report guard numbers for the frozen candidate only, and treat any guard that has informed a redesign as development data.

**Assumptions:** Two or four paired cases with binary outcomes, as in the laboratory's teaching cases, so the gain can only be a multiple of 0.25 or 0.5 and the gate is a teaching device. A threshold is a rule, not a confidence statement. The reuse flag records what you declare, not the true history, and the threshold is only meaningful if fixed before guard access. A tie in guard gain leaves the development pick in place.

**Declared default controls:**

```json
{
  "case": "default",
  "guard": "clean",
  "chooser": "development"
}
```

**Supported values:**

- `case`: ['default', 'changed', 'transfer']
- `guard`: ['clean', 'reused']
- `chooser`: ['development', 'guard']

**Evidence:** constructed teaching example

Constructed example: the laboratory's default, changed and transfer teaching cases, computed with its own gate function.

## C25-D03: How little a guard promises, and how it wears out

How likely is a candidate with no true benefit to clear a guard threshold, and which guard decisions does that number still cover after a guard result reaches the designer?

**Source section:** A guard becomes development evidence when it is consulted repeatedly

**Application:** Set a guard query budget before use. Count how many candidates will be tested, size the guard so the total stays small, and retire the guard for release evidence once its results start steering redesign. Track who has seen which outcomes, not whether the bank file changed.

**Assumptions:** The chapter's constructed conditions: every counted candidate is fixed before guard access, outcomes lie in [-1, 1], and outcomes are independent across cases. Shared tool state or a common evaluator can break independence. The exact tail uses one convenient distribution, plus or minus 1 with equal chance; it is not a real agent. The guard is evidence for one version, one task population and one evaluation protocol, and a shift in the task distribution changes what a clean result describes.

**Declared default controls:**

```json
{
  "guard_cases": 200,
  "decisions": 10,
  "redesign": "never"
}
```

**Supported values:**

- `guard_cases`: [50, 200, 400]
- `decisions`: [3, 10]
- `redesign`: ['never', 'after2']

**Evidence:** constructed teaching example

Constructed example: the chapter's own 200-case, 0.25 threshold, ten-decision values and its three-query ledger, with other sizes and the redesign state defined for this reader.

## C25-D04: Acceptance needs four passes, not a high score

Can a large guard uplift make up for a cost that is over the limit, a missing permission or an untested rollback?

**Source section:** Acceptance is a constrained release decision

**Application:** Write a release record with four lines: uplift against its threshold, cost against its limit minus margin, the named authority holder and scope, and the tested rollback route. Name the owner for each, for example the workflow owner for the guard result and the incident owner for rollback alerts. A missing line blocks release.

**Assumptions:** Constructed values for one candidate, with uplift and cost already estimated on a clean guard (see Demonstration 3 for what that requires). The laboratory's gate in Demonstration 2 checks only the uplift threshold and the reuse flag, so cost, authority and rollback are computed directly here. A passing record permits a limited canary; it does not show that the change is safe at scale.

**Declared default controls:**

```json
{
  "uplift": 0.45,
  "others": "all"
}
```

**Supported values:**

- `uplift`: [0.2, 0.25, 0.45]
- `others`: ['all', 'cost', 'authority', 'rollback']

**Evidence:** constructed teaching example

Constructed example: the chapter's threshold 0.25 with cost limit, margin and candidate values defined for this reader; the authority case follows the workbench's revised third candidate.

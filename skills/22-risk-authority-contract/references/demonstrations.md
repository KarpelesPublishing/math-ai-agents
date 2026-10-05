# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C22-D01: A penalty hides an exchange rate

With the same two policies, when does a fixed penalty choose a policy that a cost limit would remove?

**Source section:** Fixed penalties make a hidden exchange rate

**Application:** When a team reports that a penalty setting keeps cost down, ask whether cost is a preference with a defensible exchange rate or a limit. If it is a limit, state it as a limit and check each policy against it.

**Assumptions:** One step, two policies, one cost, and expected values read as the whole story. Each flip point belongs to its two policies and reward scale, not to any other problem. Mixing assumes the choice of policy is made once before the episode so rewards and costs mix linearly; it does not make a forbidden action permitted. Even the constrained choice says nothing about a single bad episode or a hazard the cost leaves out.

**Declared default controls:**

```json
{
  "case": "table",
  "penalty": 2
}
```

**Supported values:**

- `case`: ['table', 'workbench', 'transfer']
- `penalty`: [2, 4, 6, 100]

**Evidence:** constructed teaching example

Constructed example: the chapter's own two-policy table, Mathematical Workbench problem VI.1 (Careful 7 and 0.5, Aggressive 11 and 2) and the laboratory's transfer case (act and wait, limit 0, multiplier 100). The transfer case is also evaluated with the laboratory's risk and authority function; the other two have costs above 1 and are computed directly.

## C22-D02: A bound permits excess, so leave a margin

How much can the modeled cost exceed the limit after one update, how large a step does a margin allow, and when does the margin cover it?

**Source section:** A constraint is not a promise

**Application:** Before citing the proposition to justify a safety margin, compute the allowance for your own step size, discount and advantage, and set the margin from that number rather than from habit.

**Assumptions:** The bound concerns one ideal update inside the modeled problem; it is not a statement about a training run, a sampled update or a changed deployment. The values here are constructed. The lower row applies the bound with the ceiling in the role of the limit (d replaced by d minus the margin), which is this reader's illustration of the margin idea. The target (what the optimizer asks for), the bound (what the theorem permits) and observed behavior (what an experiment records) are three different things; this figure shows the first two only.

**Declared default controls:**

```json
{
  "step": 0.005,
  "discount": 0.85,
  "margin": 0.5
}
```

**Supported values:**

- `step`: [0.005, 0.02]
- `discount`: [0.5, 0.85, 0.9]
- `margin`: [0.5, 1.0]

**Evidence:** constructed teaching example

Constructed example: the chapter's bound evaluated with values defined for this reader (limit 10, advantage 0.1, margins 0.5 and 1.0).

## C22-D03: Two other risk contracts: a tail and a budget

For a rare bad episode, how far apart are mean cost and tail severity, and how does a risk budget shrink as charged actions spend it?

**Source section:** Other risk contracts

**Application:** If one rare, severe episode is the worry, a limit on mean cost can look small while the tail measure is large. State which one the limit is about, and why. For a bounded horizon, keep a running budget and refuse a charged action that exceeds what remains.

**Assumptions:** A single two-outcome lottery and four charges defined for the reader. CVaR asks for average severity in a declared upper tail, not a promise that no episode is bad. The budget rule prevents one action from exceeding the remaining authority; it does not prove the charges are calibrated, independent, complete or safe beyond the declared horizon.

**Declared default controls:**

```json
{
  "alpha": 0.99,
  "budget": 0.1
}
```

**Supported values:**

- `alpha`: [0.9, 0.95, 0.99, 0.995]
- `budget`: [0.05, 0.1, 0.2]

**Evidence:** constructed teaching example

Constructed example: the chapter's lottery (cost 100 with probability 0.01, else 0) with other tail levels, and a four-decision budget whose charges are defined for this reader.

## C22-D04: Authority first, risk limit second, reward last

Which actions may be considered at all, which of those has the best reward, and what happens when one route to the actuator skips the check?

**Source section:** Authority is an operating envelope

**Application:** For an agent that can call tools, list each action with its permission and risk, remove what is not permitted, then rank the rest. Keep an explicit abstain row, provided abstain is authorized and its risk is within the limit, so the set is never empty. Confirm that every route to the actuator passes the gate.

**Assumptions:** Rewards, risks and permissions are supplied values; nothing here estimates risk. An expected-risk limit is a statement about an average, so an action with risk 0.05 can still end badly. A large enough penalty can mimic a gate in one case and fail in the next. In the bypass states the unchecked route is assumed to run the controller's own penalty pick; that is this reader's illustration of the chapter's complete-mediation requirement.

**Declared default controls:**

```json
{
  "limit": 0.1,
  "penalty": 5,
  "route": "checked"
}
```

**Supported values:**

- `limit`: [0, 0.1, 0.25]
- `penalty`: [5, 25]
- `route`: ['checked', 'bypass']

**Evidence:** constructed teaching example

Constructed example: the laboratory's four-action example, evaluated with the laboratory's risk and authority function. The four rewards, risks and permissions are not taken from the chapter, whose section supports only the distinction between an objective and a gate. The bypass is defined for this reader.

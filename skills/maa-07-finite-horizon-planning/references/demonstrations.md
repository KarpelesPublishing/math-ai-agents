# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C07-D01: What a discount does to a distant reward

How much is a reward of 100 worth now if it arrives many steps from now, and what sets the planning scale?

**Source section:** What discounting does to a number

**Application:** Before choosing a discount factor, compute what it does to the delayed benefit you care about. A factor that makes a useful verification or retrieval worth almost nothing will make the controller skip it.

**Assumptions:** One delayed reward of fixed size, a constant discount factor, and rewards that arrive on a regular step count. The factors 0.9, 0.95 and 0.99 come from the chapter's text and 0.5 from its discussion of a short horizon. Reading gamma as a survival probability needs a separate assumption of independent continuation; time preference does not.

**Declared default controls:**

```json
{
  "gamma": 0.9,
  "steps": 10
}
```

**Supported values:**

- `gamma`: [0.5, 0.9, 0.95, 0.99]
- `steps`: [10, 50, 100]

**Evidence:** constructed teaching example

Constructed example: the chapter's discount arithmetic for a reward of 100 (factors 0.9, 0.95 and 0.99 at ten, fifty and a hundred steps), with gamma 0.5 from the chapter's horizon discussion.

## C07-D02: Three states, computed backward

Verifying costs something now. Can it still be the better first move, and at what cost does it stop being so?

**Source section:** Three states, computed backward

**Application:** When a check, a retrieval or a clarifying question looks like pure cost, write the value of the state it leads to and compare. The break-even cost and the break-even discount tell you how expensive the check can be, and how heavily the future may be discounted, before skipping it is right.

**Assumptions:** Three states, one verification opportunity, deterministic movement into the verified state, and expected payoffs standing in for the release gamble. Real verification can fail or be unavailable. Equation (7.3) only prices a policy it is handed; choosing the better one needs the extra comparison of Equation (7.4). The workbench scenarios put the release probabilities 0.80 and 0.95 on a payoff of 100.

**Declared default controls:**

```json
{
  "scenario": "book",
  "stage": 0
}
```

**Supported values:**

- `scenario`: ['book', 'tie', 'wb1', 'wb3']
- `stage`: [0, 1, 2]

**Evidence:** constructed teaching example

Constructed example: the book's three-state controller (release values 85 and 97, verification cost 5; the break-even cost 12 and the break-even discount 0.9278 are derived from it as 97 - 85 and 90/97, not stated in the chapter) and the original workbench problems II.1 and II.3 (80, 95, cost 6, discount 0.90 and 0.75), computed with the laboratory's backward induction.

## C07-D03: How many decisions are left can change the answer

When does it pay to spend a step investing in a later payoff instead of taking a smaller payoff now?

**Source section:** Horizons, and why agents have short ones

**Application:** A policy computed for three remaining steps can be wrong once steps have been spent (in the cash or prepare model at discount 1, preparing is right with two or three decisions left but wrong with one). Store the policy for each remaining horizon, and expect information-gathering moves to disappear near the end of a budget.

**Assumptions:** A fully observed three-state model with certain transitions, rewards fixed in advance, and a stopping state that pays zero. The optimum holds inside this model only; an outage or a missing permission that the model omits can reverse the ranking. Ties are reported as ties.

**Declared default controls:**

```json
{
  "model": "prep",
  "horizon": 2,
  "discount": 1.0
}
```

**Supported values:**

- `model`: ['prep', 'wait']
- `horizon`: [1, 2, 3]
- `discount`: [1.0, 0.5]

**Evidence:** constructed teaching example

Constructed example: the laboratory notebook's cash, prepare and release values (2, -1, 6) for the default and changed cases, and its transfer values (now 1, later 0, collect 4), computed with the laboratory's backward induction.

## C07-D04: A residual bounds the error of a value guess

If you only check how far a candidate value function is from its own one-step lookahead, what do you learn about its distance from the best values?

**Source section:** Where the reward comes from

**Application:** When values are learned or approximated, the residual can be computed without knowing V*. A small residual with a discount well below 1 is a certificate about the declared model, not about the world the model describes.

**Assumptions:** A finite model with bounded rewards and 0 <= gamma < 1. The three-state controller here (verification cost 5, verified release 97, unverified release 85) is constructed, and a discount below 90/97 = 0.928 (here 0.90) changes which start action is best compared with the chapter's undiscounted case. A small residual against a wrong model still guides a bad action.

**Declared default controls:**

```json
{
  "discount": 0.95,
  "stage": 0
}
```

**Supported values:**

- `discount`: [0.9, 0.95, 0.99, 1.0]
- `stage`: [0, 1, 2]

**Evidence:** constructed teaching example

Constructed example: the book's three-state controller values with discount factors defined for the reader; best values computed with the laboratory's backward induction and each lookahead step computed with the laboratory's one-step backward update.

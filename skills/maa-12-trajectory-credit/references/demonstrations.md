# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C12-D01: One run, three update rules, pass by pass

When a run pays only at its last step, which state estimates move, and how far does the news travel on each pass under each rule?

**Source section:** The two rules on one trajectory

**Application:** When a long run ends in success or failure, an update that touches every visited state is a statement about the returns that followed those states under the policy that was run. It is not an itemised receipt for each action, and the one-step rule's zero errors do not say the early steps were unimportant.

**Assumptions:** States visited once each in a fixed order, one sequential pass repeated on the same trajectory, and values and step sizes declared for each run (the notebook's draft, review, done run, its truncated variant and its a, b, c, d run, and the book's four-action run). Different starting estimates, discounts or replay orders change which states move. Repeating one trajectory is a teaching device, not a training set.

**Declared default controls:**

```json
{
  "case": "book",
  "passes_done": 1
}
```

**Supported values:**

- `case`: ['book', 'default', 'changed', 'transfer']
- `passes_done`: [1, 2, 3]

**Evidence:** constructed teaching example

Constructed example: the book's four-action trajectory (estimates 0.5, step size 0.1, final reward 1) and the laboratory's default, changed and transfer cases (draft, review, done; truncated; a, b, c, d), computed with the laboratory's trajectory-credit function and repeated pass by pass.

## C12-D02: Eight episodes, two answers about state A

Why do the two rules agree about state B but disagree about state A, which was seen only once?

**Source section:** Eight episodes, two answers

**Application:** When a state is rare but its successor is common, ask whether the stated process really sends the rare state to that successor. If so, the successor-based answer pools more evidence; if not, it imports a mistake.

**Assumptions:** The process is stipulated: A always goes to B with no reward, and B pays at random. Eight observations do not prove that. The one-step answer is better only if that process is real and the successor's value is reliable. The outcome rule is not wrong about the data; it fits them exactly.

**Declared default controls:**

```json
{
  "ones_in_b_only": 6,
  "a_final": 0
}
```

**Supported values:**

- `ones_in_b_only`: [3, 6, 7]
- `a_final`: [0, 1]

**Evidence:** constructed teaching example

Constructed example: the book's eight-episode construction (six ones among the seven B-only episodes, the A episode ending at 0), with those counts varied.

## C12-D03: One dial between the two rules

How does the blending parameter lambda divide weight between short lookahead targets and the complete return, and what does it do to prediction on a random walk?

**Source section:** The family between the two rules

**Application:** When a method is described as temporal-difference (TD) learning with a lambda setting, read it as a choice of target mixture: how much to trust the agent's own estimates relative to what actually happened. For a fixed policy and a prediction target, it changes the estimator, not the objective.

**Assumptions:** The weights are for a single episode that terminates after n transitions, with terminal value zero. The right panel is a constructed experiment: 100 training sets of 10 walks drawn with a fixed seed, a table of five values, and, for the single presentation, a step size chosen from a grid at each lambda. It reproduces the shape of the chapter's experiment, not Sutton's published numbers, and it does not say which lambda is best for any other problem.

**Declared default controls:**

```json
{
  "lam": 0.9,
  "protocol": "repeated"
}
```

**Supported values:**

- `lam`: [0, 0.3, 0.9, 1]
- `protocol`: ['repeated', 'once']

**Evidence:** constructed teaching example

Constructed example: the weights of Equation (12.4) for the book's eight-transition case (Figure 12.4) and the chapter's random-walk chain (Figure 12.2), with seeded walks and lambda values defined for this reader.

## C12-D04: A positive error for a useless search, and a value that switches the action

Can the one-step error be positive after a search that cost something and returned nothing useful, and when does an updated value change the next action?

**Source section:** When a learned value changes the next action

**Application:** When reading a log of TD errors from an agent, do not treat a positive error as praise for the call just made, or a negative one as blame. Credit for a particular call needs a comparison with what would have happened without it, which these updates do not provide.

**Assumptions:** One transition with the reward and estimates set by hand, as in the chapter's example, and a model at x that is known while the continuation value is learned. Estimates here are declared numbers, not fitted values; one reward of 1 may overstate the continuation policy's mean, so the switch is an improvement in the estimated comparison, and its real return still needs evaluation.

**Declared default controls:**

```json
{
  "successor": 0.5,
  "alpha": 0.8
}
```

**Supported values:**

- `successor`: [0.1, 0.5, 0.8]
- `alpha`: [0.3, 0.4, 0.5, 0.8]

**Evidence:** constructed teaching example

Constructed example: the book's first search (reward -0.02, estimates 0.20 before and 0.50 or 0.10 after) and its finish-or-inspect example (finish 0.6, inspect cost 0.1, estimate 0.5, step size 0.8); other successor estimates and step sizes are defined for this reader; both updates are checked against the laboratory's trajectory-credit function.

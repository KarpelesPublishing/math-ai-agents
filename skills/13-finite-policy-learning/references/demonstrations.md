# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C13-D01: What one episode records: return-to-go and the action mask

What return is each step credited with, and which tokens of an episode receive training loss?

**Source section:** What one training episode contains

**Application:** When a training log reports one number per episode, ask which return it is, and when a loss is reported, ask which tokens it covers. A comparison needs the same definition on both sides.

**Assumptions:** A short episode with fixed rewards and no randomness, and one gradient computation for the mask. Real trajectories include many tokens, and only the policy's own actions receive credit. The release task values are constructed for this reader; the log probabilities -0.4 and -1.2 are the chapter's.

**Declared default controls:**

```json
{
  "stream": "release",
  "gamma": 1.0,
  "tool_mask": 0
}
```

**Supported values:**

- `stream`: ['release', 'exercise']
- `gamma`: [1.0, 0.9, 0.5]
- `tool_mask`: [0, 1]

**Evidence:** constructed teaching example

Constructed example: the chapter's own exercise (rewards 1 and 2), the chapter's mask unit test (log probabilities -0.4 and -1.2) and a three-step release task with the book's retrieval cost 0.05, defined for this reader.

## C13-D02: Retrieve or answer: the gradient of one choice and what a baseline changes

If a policy retrieves with probability p = sigma(phi), what is the expected learning signal, and what does a baseline do to its noise?

**Source section:** Retrieve or answer

**Application:** With a logistic parameterization, a policy that is already nearly sure of its choice receives almost no learning signal, even if the other choice is better. A training log should show action frequencies, not only an average reward.

**Assumptions:** One decision with two actions, a fixed environment and exact expectations over the four outcomes. The expectation-zero argument requires the stated conditioning and action independence. The success values 0.55 and 0.80 and the cost 0.05 are the book's constructed numbers.

**Declared default controls:**

```json
{
  "phi": 0,
  "baseline": "none"
}
```

**Supported values:**

- `phi`: [-2, 0, 1, 3]
- `baseline`: ['none', 'expected', 'action']

**Evidence:** constructed teaching example

Constructed example: the chapter's retrieve-or-answer values 0.55, 0.80 and the cost 0.05; the baselines are defined for this reader from the chapter's Figure 13.2 discussion.

## C13-D03: A verifier can teach the wrong success

If the verifier rewards the action that the task does not need, does more training help or hurt the task?

**Source section:** A verifier can teach the wrong success

**Application:** Before calling a rising reward curve an improvement, compute what the policy would score under a check that the reward model does not share, such as an outside audit of the outcome, and keep the evaluation sample separate from training.

**Assumptions:** One-step choice, a fixed learning rate (0.08, or 0.1 in the transfer case), and two seeds. Rewards are fixed numbers, so the story case uses the chapter's expected scores rather than noisy draws. Real tasks have many steps. The seeds show that a run is a sample; they are not an estimate of how often it happens elsewhere.

**Declared default controls:**

```json
{
  "scenario": "default",
  "length": "case"
}
```

**Supported values:**

- `scenario`: ['default', 'changed', 'transfer', 'story']
- `length`: ['short', 'case', 'long']

**Evidence:** constructed teaching example

Constructed example: the laboratory's default, changed and transfer training cases, and the chapter's noisy-verifier numbers (0.9, 0.3, 0.55, 0.80, 0.05, shortcut 0.95) as fixed expected scores, run by the laboratory's training function.

## C13-D04: Reward shaping: what cancels and what does not

Which parts of a shaped return survive the cancellation, and when can an end potential change which route ranks first?

**Source section:** When the reward arrives in pieces

**Application:** If a team adds a bonus for visiting a useful intermediate state, check where the potential ends up. A bonus that vanishes at the end is bookkeeping; a bonus that remains at some end states is a new objective.

**Assumptions:** No discount, a fixed starting state and exact expected returns. The potential is a function of state, as Equation (13.3) requires. The values 0.55, 0.80, 0.05 and 0.4 are the book's constructed numbers; the other potentials are defined for this reader.

**Declared default controls:**

```json
{
  "evidence_potential": 0.4,
  "retrieve_end_potential": 0.0,
  "direct_end_potential": 0.0
}
```

**Supported values:**

- `evidence_potential`: [0.4, 1.0]
- `retrieve_end_potential`: [0.0, 0.2]
- `direct_end_potential`: [0.0, 0.2, 0.3]

**Evidence:** constructed teaching example

Constructed example: the chapter's release construction (potential 0 at start and end, 0.4 after retrieval) with the book's 0.55, 0.80 and 0.05 and its 0.30 bonus; other potentials defined for this reader.

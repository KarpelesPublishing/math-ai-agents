# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C08-D01: The belief update, one stage at a time

How does a belief change when an action is taken and a report arrives, and which part of the change is prediction and which is correction?

**Source section:** The update, worked

**Application:** Whenever a tool result leaves several explanations open, write down the possibilities, the chance the action moved each one, and the chance each would have produced the report. The three steps then give the new weights without rereading the whole history.

**Assumptions:** The corridor, its deterministic goal report and the move probabilities are the chapter's; the notebook cases are constructed. The model is only as good as the move and report probabilities supplied to it; if the real world differs, the update is exact for the wrong world.

**Declared default controls:**

```json
{
  "case": "move1",
  "stage": 2
}
```

**Supported values:**

- `case`: ['move1', 'move2', 'default', 'transfer']
- `stage`: [0, 1, 2]

**Evidence:** constructed teaching example

Constructed example: the chapter's corridor update (the book's own values for one and two moves at slip chance 0.1) and the laboratory notebook's default and transfer cases, computed with the laboratory's belief function.

## C08-D02: The same report under different instruments

If an instrument says pass, how far does the belief move, and what decides that: the report or the instrument model?

**Source section:** Where the observation kernel comes from

**Application:** Before trusting a pass, a green check or a found-nothing result, ask how often the bad state produces the same output. That one comparison decides whether the report can carry a decision.

**Assumptions:** Two states, one report, and instrument probabilities that are teaching assumptions, not measurements of any runner or sensor. Correct arithmetic cannot repair a wrong likelihood. Repeated reports would need a model of how they depend on each other; rerunning the same broken or cached instrument does not automatically supply independent evidence.

**Declared default controls:**

```json
{
  "kernel": "run03",
  "prior": 0.5
}
```

**Supported values:**

- `kernel`: ['run03', 'run30', 'sensor', 'aliased']
- `prior`: [0.2, 0.5, 0.8]

**Evidence:** constructed teaching example

Constructed example: the chapter's test-runner teaching assumptions (true-positive 1, false-positive 0.03 and 0.30, prior 0.5, giving 0.9709 and 0.7692) and the laboratory notebook's default and changed observation rows, with priors 0.2 and 0.8 defined for this reader.

## C08-D03: A belief is valued by its best plan

If every plan is a straight line in the belief, what does the belief's value look like, and how can two equal memories give different values?

**Source section:** Where an agent's belief actually lives

**Application:** When shrinking a summary or a memory, list the histories it merges and check whether the best allowed action agrees across each merged group. Equal size says nothing; what the retained bit distinguishes is what matters.

**Assumptions:** A stipulated toy task: four equally likely histories, authorization fixed between observation and action, and release permitted only with an authoritative authorization record. The detour value 97 is stipulated, not derived. This shows decision sufficiency for one task, not that short summaries are better in general, and the finite-horizon vector form does not make planning cheap.

**Declared default controls:**

```json
{
  "setting": "alpha",
  "case": 1
}
```

**Supported values:**

- `setting`: ['alpha', 'auth', 'fmt', 'detour']
- `case`: [0, 1, 2]

**Evidence:** constructed teaching example

Constructed example: the chapter's alpha-vector pair, its four-history document-release table with the book's stipulated utilities (+4, -12 and 0) and its three-move detour (100, cost 3, value 97), with the break-even belief 0.97 derived from them; maxima checked with the laboratory's expected-reward function.

## C08-D04: A look pays only near the threshold

For which beliefs can a report change the decision, and is the change worth its price?

**Source section:** The condition that makes a look worthless

**Application:** Before paying for a check, ask whether any answer it could give would change what you do. If not, its value is 0 however reassuring it sounds. If so, compare the value with the price of the check.

**Assumptions:** One report, one decision afterward, a fixed price for looking, and the stipulated rewards and rates. The band describes beliefs, not how often cases land in it. Real tools can fail in ways the rates do not describe, and checking takes time that a single price may not capture. The price 1.0 for the chapter's tool is defined for this reader.

**Declared default controls:**

```json
{
  "case": "tool",
  "price": "free"
}
```

**Supported values:**

- `case`: ['tool', 'default', 'changed', 'transfer']
- `price`: ['free', 'case', 'even']

**Evidence:** constructed teaching example

Constructed example: the chapter's verification-tool instance (rewards 10, -40 and 0; pass 0.90 and fail 0.85; value 3.0 at prior 0.6), and the laboratory notebook's default, changed and transfer cases, computed with the laboratory's belief function; the price 1.0 is defined for this reader.

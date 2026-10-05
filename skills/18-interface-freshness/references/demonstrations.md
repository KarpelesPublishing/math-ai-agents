# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C18-D01: One command, two layouts, three interfaces

If the controller is unsure which layout is current, what does each kind of command do, and what does a permission check change?

**Source section:** The interface belongs in the transition law

**Application:** Before trusting a command, write down what it realizes under every layout you consider possible, and which of those realizations a current check would block. Compare interfaces with the task, the document, the authority and the deadline held fixed.

**Assumptions:** Two layouts, each with a deterministic realized operation that leads to one next state, and complete mediation when the check is on. The beliefs are probabilities in a constructed model, not measured accuracies of any visual model. The semantic request is taken to resolve v2 correctly; a mislabeled or ambiguous control would break that, and a transactional request can fail because its precondition expired even when a person would accept the newer version. If an unmediated route to the service exists, the check does not apply.

**Declared default controls:**

```json
{
  "interface": "coordinate",
  "belief_layout1": 0.8,
  "permission_check": "off"
}
```

**Supported values:**

- `interface`: ['coordinate', 'semantic', 'transactional']
- `belief_layout1`: [0.6, 0.8]
- `permission_check`: ['off', 'on']

**Evidence:** constructed teaching example

Constructed example: the chapter's two-layout console with its 0.8 and 0.2 beliefs and chapter exercise 1's 0.6 and 0.4; the three interfaces are the chapter's, with issuance and target correctness computed by the laboratory's interface calculation.

## C18-D02: What survives when the screen is uncertain

Which commands stay authorized in every layout the controller still considers possible, which state removes the rest, and which observation restores them?

**Source section:** A belief over screens

**Application:** When a decision is removed by a state you think unlikely, the record shows which state removed it and which observation (a fresh screenshot, a metadata read) could narrow the support and restore it. Reading can often be permitted over a broader set of states than releasing, which is why it stays available.

**Assumptions:** The true layout must lie inside the counted support, and the authorization sets must be specified correctly; if either fails, the intersection guarantees nothing. The sets here are constructed, and the construction is conservative: it is not a substitute for the service's own current permission check. A read only helps if it is current and correct.

**Declared default controls:**

```json
{
  "belief_layout2": 0.01,
  "observation": "none"
}
```

**Supported values:**

- `belief_layout2`: [0.0, 0.01, 0.5, 1.0]
- `observation`: ['none', 'layout1', 'layout2']

**Evidence:** constructed teaching example

Constructed example: the chapter's two-layout case, with authorization sets defined for this reader and belief weights chosen for illustration.

## C18-D03: How long a picture stays useful

Given its age, its saved version and the current permission, which interface may act, and how fast does a coordinate go stale if changes arrive at a steady rate?

**Source section:** How long a picture stays useful

**Application:** Choose a maximum observation age by deciding what chance of an invalidating change you will accept, then refresh the observation or bind the command to a state version before that age is reached, and check current permission at issuance, not from memory.

**Assumptions:** The table and the curve are independent: the table uses the case's observation age, the curve uses the chosen delay. In the default and changed cases the coordinate target is called delete, the notebook's name for the wrong object (v3 in Demonstration 1). Constant-rate, memoryless changes, and a clear definition of which changes invalidate the binding. Real interfaces can update periodically, in bursts, or in response to the agent's own actions, and a rate taken from quiet periods can mislead. The rates and limits here are teaching inputs. Semantic resolution can itself be wrong, and a click receipt is not an effect receipt.

**Declared default controls:**

```json
{
  "scenario": "default",
  "delay": 30
}
```

**Supported values:**

- `scenario`: ['default', 'changed', 'transfer']
- `delay`: [5, 10, 15, 30]

**Evidence:** constructed teaching example

Constructed example: the notebook's default case (age 1 against a limit of 2, layout-1 against layout-2, rate 0.02), changed case (age 3) and transfer case (permission false, rate 0.05), computed with the laboratory's interface function, and the chapter's delays of 5 and 30 seconds with chapter exercise 2's 15; the delay of 10 seconds is defined for this reader.

## C18-D04: The price of another look

When does one more observation before the click earn its cost?

**Source section:** The price of another look

**Application:** Do not buy information because uncertainty exists. Price the wrong-target branch under the interface you actually have, and look again only when that expected loss is larger than the cost of looking.

**Assumptions:** The look is perfect, execution follows at once, and the loss lumps delay, retries and side effects into one number. A denied attempt can also use up a rate limit, lock an account or reveal information; if so the loss of 3 is too small. A deadline can raise the cost of looking. The number 2 is not a general price for visual safety.

**Declared default controls:**

```json
{
  "wrong_loss": 40,
  "wrong_chance": 0.1,
  "look_cost": 2
}
```

**Supported values:**

- `wrong_loss`: [40, 3]
- `wrong_chance`: [0.0, 0.1, 0.2]
- `look_cost`: [1, 2]

**Evidence:** constructed teaching example

Constructed example: the chapter's 0.1 chance of a wrong target, loss of 40 or 3 and observation cost of 2, chapter exercise 3's look costing 1 with a 0.2 chance, and the chapter's third interface with chance 0.

# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C06-D01: Three actions, one rule, and where the order flips

If the probabilities stay fixed, which value change flips the winner or the order, and by how much does each action's score depend on it?

**Source section:** The decision rule

**Application:** Before trusting an automated choice, write the table: one row per action, including asking for evidence and handing the decision to a person. Then check whether a change in a value you are unsure of changes the winner.

**Assumptions:** One decision, two mutually exclusive outcomes per action (one for review and abstaining), and utilities on one shared scale. The probabilities and utilities are constructed teaching values from Table 6.1 and the notebook, not estimates for any real controller. The 'made worse' failure values are the book's -400 and the notebook's -100; the transfer value -24 is defined for this reader as double the supplied value. Expected utility compares actions; it does not say whose values the numbers represent, and a large negative utility is not the same as a hard permission boundary.

**Declared default controls:**

```json
{
  "table": "book",
  "worse": "asis"
}
```

**Supported values:**

- `table`: ['book', 'lab', 'transfer']
- `worse`: ['asis', 'worse']

**Evidence:** constructed teaching example

Constructed example: the book's Table 6.1 values, and the notebook's default, changed and transfer decision cases, computed with the laboratory's expected-utility function.

## C06-D02: Elicit one number: the price of an hour

Between releasing now and requesting evidence, what single number decides the choice, and what if the support probability is itself shaky?

**Source section:** Eliciting one number

**Application:** When a decision depends on a value nobody has written down, compute the threshold at which the decision flips and ask the person responsible which side they are on. That question is answerable; asking what an outcome is worth in the abstract usually is not. Then vary each shaky input across the range anyone would defend and report whether the choice changes.

**Assumptions:** Two actions, utilities on the Table 6.1 scale, and delay priced additively. The 0.85, 0.90 and 0.97 support probabilities are constructed, and the range 0.80 to 0.90 is an illustrative uncertainty defined for this reader. A tie is reported as a tie, because Equation (6.3) does not break ties. A range of scores is not a probability distribution over the support.

**Declared default controls:**

```json
{
  "hour_cost": 5,
  "support": "p85"
}
```

**Supported values:**

- `hour_cost`: [0, 5, 12, 15]
- `support`: ['p85', 'p90', 'range']

**Evidence:** constructed teaching example

Constructed example: the book's Table 6.1 values, computed with the laboratory's expected-utility function; the hour prices 0 and 15 and the support range are defined for this reader.

## C06-D03: Risk is the shape of the utility curve

How much mean payoff would an agent give up to replace a gamble with a sure amount, and what if the gamble's mean payoff has no limit?

**Source section:** A worked certainty equivalent

**Application:** When a team says a system should be cautious, ask for the curve or for one certainty equivalent. A stated gap such as 25 on a 50 mean can be checked and argued about; the word cautious cannot.

**Assumptions:** Constructed payoffs and probabilities. The square-root and square curves are illustrations of bending down and bending up, not elicited preferences. One certainty equivalent is consistent with risk aversion but does not prove the whole curve is concave. The certainty equivalent is a guaranteed payoff under the declared utility, not an observed willingness to pay. The sure 40 in the interpretation is only a comparison value.

**Declared default controls:**

```json
{
  "shape": "sqrt",
  "gamble": "half"
}
```

**Supported values:**

- `shape`: ['sqrt', 'linear', 'square']
- `gamble`: ['half', 'eighty', 'petersburg']

**Evidence:** constructed teaching example

Constructed example: the chapter's worked certainty equivalent (100 or 0 with equal chance), one changed probability and the chapter's unbounded gamble with a square-root utility (1 + sqrt(2), about 2.414, and a certainty equivalent of about 5.83).

## C06-D04: Declining is an action with a price

How does the value placed on declining decide how many cases an agent answers and how often it is wrong?

**Source section:** The cost of declining, measured

**Application:** When a system reports an error rate, ask for its coverage and for the value it assigns to declining. Two error rates at different coverage describe different services, and the price of declining is what chose between them.

**Assumptions:** One hundred constructed cases whose confidences are spread evenly from 0.5025 to 0.9975 and assumed to be calibrated, so a case with confidence p is correct with probability p. Real confidence scores need not be calibrated; the error rates shown are expected values under that assumption, not observed rates. Because the confidences are spread evenly, the risk and coverage curve is a straight line, and a real system's curve would take its shape from its real confidences.

**Declared default controls:**

```json
{
  "wrong": -4,
  "decline": 0
}
```

**Supported values:**

- `wrong`: [-1, -4, -9]
- `decline`: [-1, -0.5, 0]

**Evidence:** constructed teaching example

Constructed example: 100 calibrated cases defined for this reader; each answer or decline choice is computed with the laboratory's expected-utility function.

# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C20-D01: One more message, one more level

After a few messages have been delivered, how many levels of mutual knowledge exist, who blocks the next one, and what makes a fact common knowledge?

**Source section:** Stage three: finite depth has a boundary

**Application:** When a log shows request, reply and confirmation, write down who saw each message. The deepest level of mutual knowledge the exchange supports, for the fact that message 1 was delivered in a chain where each message is sent only after the previous one arrived, is one less than the number of messages delivered, and the next level depends on a message nobody can confirm. Before counting acknowledgements, list the facts every participant can observe and knows the others observe.

**Assumptions:** One chain of messages in which each is sent only after the previous one arrived, and a message lost is not signalled to its sender. Other message patterns, a shared clock, or a signal when a message is lost would change which runs look the same. The level count depends on the choice of F; a fact both parties already knew would start higher. A public clock still needs a shared reading of time and a rule tying time to action.

**Declared default controls:**

```json
{
  "delivered": 2,
  "fact": "message"
}
```

**Supported values:**

- `delivered`: [1, 2, 3, 4]
- `fact`: ['message', 'clock']

**Evidence:** constructed teaching example

Constructed example: a chain of messages defined for this reader to follow the chapter's two-division story, with who-knows-what computed from the runs and a public clock defined as a contrasting fact.

## C20-D02: A rule that trusts the last message

Can a rule that tells each division to attack after receiving enough messages be safe and ever attack?

**Source section:** Stage four: why last message cannot save attack

**Application:** Test a handoff specification by asking what happens if the last message is lost. If the outcome changes for one party only, the specification has hidden a final delivery that nobody can observe.

**Assumptions:** A threshold rule over three messages that are sent in sequence and can each be lost. A rule that uses a public clock or a shared record is outside this model. A rule that accepts some chance of mismatch makes a different promise from the one tested here.

**Declared default controls:**

```json
{
  "a_needs": 1,
  "b_needs": 2
}
```

**Supported values:**

- `a_needs`: [1, 2]
- `b_needs`: [1, 2, 3]

**Evidence:** constructed teaching example

Constructed example: the chapter's three-message table (acknowledgement then confirmation), with the needed numbers of received messages varied.

## C20-D03: Escrow with a deadline

If two private decisions can strand a token, what does an escrow state with a deadline guarantee, and what does it give up?

**Source section:** Stage seven: building agent protocols that fail safely

**Application:** For a handoff that moves an external effect, put the irreversible act behind one authority with a deadline and a named condition, and state the fallback, instead of making two private acknowledgements trigger it.

**Assumptions:** A constructed token and three messages in sequence. The authority is reliable, its rule and deadline are known to both parties, and the named condition is a declared input, not a message. Real systems must also say who observes the condition, how clock skew is handled and what happens if the authority is unreachable.

**Declared default controls:**

```json
{
  "delivered": 2,
  "policy": "private"
}
```

**Supported values:**

- `delivered`: [0, 1, 2, 3]
- `policy`: ['private', 'escrow_seen', 'escrow_unseen']

**Evidence:** constructed teaching example

Constructed example: the chapter's two-agent resource transfer with an escrow state and deadline (Figure 20.4), with the three-message rule of Demonstration 2 used for the private decisions.

## C20-D04: High chance of agreement, no knowledge of it

If parties usually end up committing together, do they know that they will?

**Source section:** Stage eight: consensus begins with a shared event model

**Application:** A report that two components usually agree is not a guarantee that either can act on the agreement. Ask what each party can observe, and whether the gap between agreeing and knowing it matters for the action.

**Assumptions:** A fixed number of rounds with synchronized ticks, independent drops, and Alice and Bob each acting on one local trigger. Real systems can crash or reorder messages. At drop probability 0 the model rules out loss by assumption; that is a statement about the model, not evidence that a channel cannot fail. This does not prove the theorem; it shows the two quantities differ.

**Declared default controls:**

```json
{
  "rounds": 2,
  "drop": 0.3
}
```

**Supported values:**

- `rounds`: [1, 2, 3, 4]
- `drop`: [0, 0.3, 0.5]

**Evidence:** constructed teaching example

Constructed example: the laboratory's bounded request-and-reply model with the notebook's default (2 rounds, 0.3), changed (2 rounds, 0) and transfer (3 rounds, 0.5) cases, computed with the laboratory's own function.

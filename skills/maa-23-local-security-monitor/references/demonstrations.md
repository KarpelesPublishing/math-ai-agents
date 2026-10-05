# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C23-D01: A child can never hold more than its parent

If hostile text asks a delegated step for an effect, what stops it: the capability the child holds, or the source of the request's authority?

**Source section:** Data may inform; control may direct

**Application:** When you give a sub-task to a tool-using helper, list the effects it needs and hand over only those, and type the parameters so that a destination, recipient or amount cannot come from untrusted text. A compromised helper then cannot reach an effect that nobody above it ever held.

**Assumptions:** The capability sets are the chapter's constructed trace, not a real deployment. The inclusion holds only if every delegation really passes through the check (complete mediation). It says nothing about which effects a parent should hold, and holding release does not authorize any specific release. Classification of text as request, quotation or record is still needed, and an error must fail closed at the action boundary.

**Declared default controls:**

```json
{
  "request": "upload",
  "grant": "chapter"
}
```

**Supported values:**

- `request`: ['extract', 'upload', 'link', 'secret']
- `grant`: ['chapter', 'browser', 'narrow']

**Evidence:** constructed teaching example

Constructed example: the capability sets are the chapter's malicious-source trace and its three adversarial traces (a page, a calendar entry, a document); the two checks are computed with the laboratory's own security monitor, whose authority sources are user, system and untrusted data.

## C23-D02: The monitor moves only on observed events

If authorization is checked once when the plan is made, what goes wrong when the world changes before the effect?

**Source section:** A monitor's memory only advances from observed events

**Application:** Re-check authority at three moments: when an action is proposed, when any material parameter changes, and immediately before the effect. Log the order, because a later acknowledgement does not show that an earlier check saw current state.

**Assumptions:** Two time steps and one approval, constructed for teaching. The monitor must receive events through a channel the attacker cannot write to; if the attacker controls the permission service, the record itself cannot be trusted. The final check is taken to be the last step before the effect: no event is assumed to arrive between it and the effect.

**Declared default controls:**

```json
{
  "scenario": "revoked",
  "check": "entry"
}
```

**Supported values:**

- `scenario`: ['approved', 'claim', 'revoked', 'replaced']
- `check`: ['entry', 'recheck']

**Evidence:** constructed teaching example

Constructed example: the four event sequences are defined for the reader from the chapter's discussion of revocation, replacement and unobserved claims.

## C23-D03: Release needs the exact triple, from a real event

The injected sentence says to publish. If one of document, version or recipient differs from the approved triple, or the approval was only a sentence, does the lookup still pass, and what if the sentence is relabeled as trusted?

**Source section:** Publish needs identity, version, recipient, and current approval

**Application:** Bind an approval to every field that defines the effect (what, which revision, to whom) and record it only from an authenticated approval event. Re-approve after any revision, and re-check the record at every point where content could be relabeled, not only at the first boundary.

**Assumptions:** One approved triple, constructed from the book's trace. The laboratory notebook checks version and capability but has no recipient field, so the document and recipient matches are worked here from Equation (23.3) alone. A passing lookup also assumes every route to release passes through it, that the predicate is specified correctly and that nothing writes to the record except observed events. The chapter works one effect, release; an irreversible payment would need its own predicate.

**Declared default controls:**

```json
{
  "changed": "version",
  "source": "event"
}
```

**Supported values:**

- `changed`: ['none', 'document', 'version', 'recipient']
- `source`: ['event', 'sentence', 'laundered']

**Evidence:** constructed teaching example

Constructed example: the approved triple and the attempted releases are the chapter's own release trace and its stale-approval and laundering exercises; the Q2-report case is defined for the reader.

## C23-D04: Risk is the worst member; two scores are not one

If nine attacks are blocked and one is not, what single exposure number does a declared family report, and why must task completion and security violations be reported separately?

**Source section:** A security case needs a declared adversary

**Application:** When reporting security, name the attack family first and report the worst member for each enforcement mechanism, then report utility and attack success as two numbers. Add any unmediated route you discover to the family instead of leaving it out of the number, and close the route: adding it to the family only measures it.

**Assumptions:** A threat-model measure, not an empirical security rate and not a proof. It presumes complete mediation and a correctly specified predicate. The chances here are constructed; an attack outside the family, or a monitor with a specification gap, is not covered by the value. The traces are the laboratory's fictitious events; checking a trace does not enforce a real tool boundary.

**Declared default controls:**

```json
{
  "trace": "default",
  "family": "three",
  "deputy": 0.6
}
```

**Supported values:**

- `trace`: ['default', 'changed', 'transfer']
- `family`: ['three', 'four']
- `deputy`: [0.1, 0.6]

**Evidence:** constructed teaching example

Constructed example: the three attack names are the chapter's declared family and the retry path is its unmediated-call example; every chance is defined for the reader. The three traces are the laboratory's default, changed and transfer cases, replayed with the laboratory's own monitor.

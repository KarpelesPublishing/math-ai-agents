# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C15-D01: Records chosen under a token budget

Which records does a limited budget buy once expired and superseded records are screened out, and how does the price of a token change the answer?

**Source section:** Retrieval is an action under budget

**Application:** When a context window is limited, give each candidate record a stated value for the decision at hand and a cost, screen out what is expired or superseded, then keep the set with the best total instead of the closest wording.

**Assumptions:** Values are declared by the designer and add up across records, which overcounts two records that repeat the same fact. The chapter example values the old approval 0 because it is superseded; the thread summary and its value 3 are defined for this reader, and the laboratory cases use their own declared values. A net value of exactly 0 is a tie and is reported as one.

**Declared default controls:**

```json
{
  "case": "chapter",
  "lam": 1
}
```

**Supported values:**

- `case`: ['chapter', 'default', 'changed', 'transfer']
- `lam`: [0, 1, 2]

**Evidence:** constructed teaching example

Constructed example: the chapter's revocation (2 tokens, value 8) and irrelevant note (value 0), plus the laboratory's default, changed and transfer cases for the memory-budget function; the thread summary and the old approval's value are defined for this reader, and every selection is computed with the laboratory's function.

## C15-D02: How much can a summary lose?

If a summary scores each action within epsilon of the full history, how much value can following it lose, and when does that claim stop applying?

**Source section:** Compression that preserves action

**Application:** Before replacing a long history with a short summary, check whether the summary errs only in its scores, or whether it has changed which actions are permitted. Only the first case is covered by the bound.

**Assumptions:** The bound needs a shared way of valuing what comes after the decision and covers only actions both versions list, including the full-history best. The laboratory's cases are one supplied comparison each, so preserving one decision vector does not prove that every future task is preserved. Worst-case errors are placed by hand to show the limit; they are not a claim about any real summary.

**Declared default controls:**

```json
{
  "summary": "worst",
  "epsilon": 1
}
```

**Supported values:**

- `summary`: ['worst', 'dropped', 'default', 'changed']
- `epsilon`: [1, 2, 3]

**Evidence:** constructed teaching example

Constructed example: action values 10, 6 and 3 and an unauthorized release worth -50 are defined for this reader; the 2 epsilon bound is the chapter's, and the laboratory's default and changed compression cases (full values 4 and 6, summary values 3 and 5, then 6 and 5) are checked with its compression comparison.

## C15-D03: Stale approval is not support

When an old approval is the most similar record, and deletion may reach only some views, which retrieval policy still blocks an unauthorized release?

**Source section:** Stale approval is not support

**Application:** Test a memory component by what the controller does next, not only by whether the retrieved text reads well, and query derived views as well as the source store after a deletion.

**Assumptions:** Room for one record, the book's three similarity scores for the approval and the note, and a revocation valued 8 against 0 for the others. The index copy of the approval is assumed to keep the approval's wording and so its similarity; the 0.99 revocation similarity and the note's recency are defined for this reader. Recency fails if the newest record is not the authority, and the decision-aware rule is only as good as the declared values and the authority lookup. 'Correct' means consistent with the chapter's rule that a revoked release must not go ahead.

**Declared default controls:**

```json
{
  "revocation_similarity": 0.72,
  "authority": "reachable",
  "deletion": "none"
}
```

**Supported values:**

- `revocation_similarity`: [0.72, 0.99]
- `authority`: ['reachable', 'unreachable']
- `deletion`: ['none', 'store', 'all']

**Evidence:** constructed teaching example

Constructed example: the chapter's similarities 0.98, 0.72 and 0.80 and its values 8 and 0; the other revocation similarity, the unreachable case and the deletion states are defined for this reader, computed with the laboratory's memory-budget function.

## C15-D04: A record that may no longer be current

How likely must a record be to still be current before it is worth its tokens?

**Source section:** Exercises

**Application:** Record who wrote an item, when it was seen, and when it expires, so the controller can estimate how likely it is to be current and charge retrieval accordingly.

**Assumptions:** One record, valued 8 if current and 0 if invalid, with no partial credit. The probability p is assumed to come from the record's fields; an honest estimate of it is the hard part and is not shown here. A record that can authorize an action should need a much higher p than this simple price implies.

**Declared default controls:**

```json
{
  "p_current": 0.6,
  "lam": 1
}
```

**Supported values:**

- `p_current`: [0.25, 0.5, 0.6, 0.8]
- `lam`: [1, 2, 4]

**Evidence:** constructed teaching example

Constructed example: the chapter's Exercise 1 values (value 8, one token, probability 0.6, λ = 1); the other probabilities and token prices are defined for this reader.

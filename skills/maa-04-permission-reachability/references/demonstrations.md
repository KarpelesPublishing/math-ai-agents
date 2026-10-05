# Chapter demonstrations



These four calculations are shared with the notebook and illustrated reader. Read the source section and assumptions before choosing a state.

## C04-D01: A permission deletes a move, and the path with it

If one permission is removed, which states can the controller still reach, and does the goal survive?

**Source section:** Permission is a filter, not an opinion

**Application:** When a task fails every time, list the states and moves, mark which moves the controller has a grant for, and search from the real start state before tuning prompts. A missing grant shows up in the list of states and moves; a prompt cannot add it.

**Assumptions:** Grants are frozen at analysis time, each arrow stands for a mechanism that really exists, and states are coarse labels. Reachable does not mean likely, cheap or safe, and it does not show that an action happened. If a label hides a distinction the system depends on, such as which evidence a draft holds, the drawn path can be one the real controller does not have.

**Declared default controls:**

```json
{
  "denied": "none"
}
```

**Supported values:**

- `denied`: ['none', 'review_release', 'draft_review', 'transfer']

**Evidence:** constructed teaching example

Constructed example: the laboratory's four-state document workflow (draft, review, release, archive), whose denied review to release case is the notebook's changed case, and the notebook's transfer workflow (queued, approved, sent). Counts come from the laboratory's reachability function.

## C04-D02: A finite drawing is not the threshold

At edge probabilities below, at and above the threshold, what does one sampled tree show, and how does that differ from the infinite tree?

**Source section:** How many edges are enough

**Application:** When someone shows one picture of a small random graph as evidence of a regime, ask for the probability law and the depth. A drawing can look connected below a threshold and broken above it; the threshold describes the law, not the drawing.

**Assumptions:** A binary tree with independent open edges and a depth of 4. The four draws are fixed random draws, picked from seeds 0 to 59 so that they differ; they are not a measurement. The threshold 1/2 belongs to this graph shape, and real tool failures often share causes, which breaks independence.

**Declared default controls:**

```json
{
  "edge_probability": 0.5,
  "sample": 1
}
```

**Supported values:**

- `edge_probability`: [0.3, 0.5, 0.7]
- `sample`: [1, 2, 3, 4]

**Evidence:** constructed teaching example

Constructed example: the chapter's finite samples of an independent binary tree below, at and above the branching threshold (Figure 4.3), here with edge probabilities 0.3, 0.5 and 0.7 and four fixed draws defined for this reader.

## C04-D03: Possible, expected and completed are three numbers

In a small tree, how different are the chance that a path exists, the expected number of open descendants and the chance that a committed controller finishes?

**Source section:** Reachability, expected descendants, and completion

**Application:** When someone reports that a search or a tool graph has many possible paths, ask which number they mean: that a route exists, how many are open on average, or how often the actual controller completes one. Each needs different information.

**Assumptions:** Independent open edges and depth two. An exhaustive search can realize the existence probability only if it can test every needed edge, revisit branching states and afford the budget; those are extra assumptions. The three-child case applies the chapter's reasoning to a new child count; it is not a number from the book.

**Declared default controls:**

```json
{
  "children": 2,
  "edge_probability": 0.6
}
```

**Supported values:**

- `children`: [2, 3]
- `edge_probability`: [0.4, 0.6, 0.8]

**Evidence:** constructed teaching example

Constructed example: the chapter's binary tree of depth two with p = 0.6 (expected count 1.44, existence 0.753984, committed run 0.36), with p and the child count varied by the same formulas.

## C04-D04: Four rates make one edge, and failure logs cannot tell rare from missing

How does tightening one stage, the grant, change the edge probability, the threshold test, the growth of descendants and what a long run of identical failures shows?

**Source section:** The permission graph, with numbers

**Application:** Before a safety review tightens a grant, write the four rates and compute where d x p lands against the threshold. A change that looks like a modest percentage can move the model across 1/d, and repeating a chain of steps multiplies the loss. When the logs show only failures, inspect the grants and the transition rules: the pattern of failures alone cannot establish that no path exists.

**Assumptions:** Constructed rates, an idealized binary tree with independent edges, and a controller that follows one chain. The product gives smooth finite-horizon sensitivity, not a discontinuity; the threshold concerns the infinite-depth model only. Real tools may share failure causes, and real graphs merge or loop. Treating each run as an independent chain with success p^T is a constructed simplification.

**Declared default controls:**

```json
{
  "grant": 0.9,
  "steps": 3
}
```

**Supported values:**

- `grant`: [0.9, 0.7, 0.4, 0.0]
- `steps`: [3, 10, 20]

**Evidence:** constructed teaching example

Constructed example: the chapter's rates (0.95, 0.98, 0.80), its grant rates of 0.90 and 0.40 and its depth-twenty ratio (0.90 / 0.40)^20, about 11.057 million; the grant rates 0.70 and 0 and the chain lengths 3 and 10 are values defined for this reader.

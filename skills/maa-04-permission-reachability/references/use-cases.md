# Use cases

## Worked example

The default goal is reachable through draft, review, release. All four nodes are reachable because archive is also available directly from draft. The review-to-draft loop does not change the shortest path and does not prevent the search from terminating.

In the changed case, the raw path still exists but the authorized path is empty. Release is absent from the allowed distance map. Draft, review, and archive remain reachable, so the reachable count falls from four to three. The controller has lost an authority bridge, not a linguistic ability to mention release. A useful report names that missing edge and the authority required to restore it.

## Changed assumption

Reachability is necessary for many workflow goals but is not sufficient for completion. An edge might represent a probabilistic tool action, an expensive operation, or a choice the policy never selects. Those conditions need a transition model and policy analysis rather than a plain graph. Likewise, permission can change between observation and action, invalidating the frozen snapshot.

An unsafe inference is to interpret a path containing an unallowed edge as permission to execute it. The raw graph is a diagnostic comparison, not an alternate authority source. The transfer case makes this explicit: the final edge exists, but the controller cannot reach the state from which it becomes available.

Graph design also matters. If the node label hides document version or review status, the graph can claim a path that the real state machine forbids. Include the relevant state boundary before treating reachability as an operational result.

## New inputs

The transfer workflow starts queued and requires approval before sending. The queued-to-approved edge is denied, so neither approved nor sent is reachable from the start under current permissions. A permitted approved-to-sent edge cannot help until its initiation state is reached.

For local use, map concrete tool preconditions and current authority into nodes and edges. Distinguish a terminal refusal from an accidental dead end. After computing a path, export its ordered states and the frozen permission contract. Use a separate execution trace to establish whether the actions happened, and recheck authority at the action boundary when permissions can change.

## Acceptance invariants

- Default authorized path has two edges.
- Denied bridge removes only authorized goal reachability.
- Cycles terminate through visited-state tracking.

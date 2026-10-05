# Method

Let G=(V,E) be a directed graph of declared states and action interfaces. Permission filtering forms E_allowed={e in E: allowed(e)=true}. A goal is reachable when some finite directed path from the start ends at it. Breadth-first search discovers the minimum number of edges needed to reach each node in an unweighted graph.

The algorithm maintains a queue and a distance map. The start has distance zero. Each previously unseen neighbor receives its predecessor's distance plus one and enters the queue. Recording predecessors reconstructs one shortest path to the goal. A visited set prevents a cycle from making the search loop forever.

A reachable sink is a discovered node with no outgoing permitted edge. It can represent successful termination, a dead end, or an intentional refusal state; the graph alone does not tell you which. The cumulative depth figure counts how many allowed nodes can be reached within each maximum path length. Removing a bridge can disconnect a goal even when the raw graph remains connected.

Register every node, then supply directed edges with exact boolean permission flags. The start and goal must be registered, and every edge endpoint must be known. The function runs breadth-first search on the raw adjacency map and on the permission-filtered map, returning reachable counts and paths separately.

The chart places maximum path length on the horizontal axis and cumulative reachable-node count on the vertical axis. It describes possibilities under the current graph. For the changed case, remove permission from the review-to-release edge. Predict the goal result before running the function. Inspect the returned sink list and distance map to understand where the permitted workflow can end. This is more useful than reporting only a yes/no path flag.

## Apply this to an agent

Model the controller, tools and permitted effects as a directed graph. Ask whether release is reachable through currently authorized edges. Reachability describes a possible route; a separate execution record must establish that the route was followed.

For worked interpretation and changed assumptions, read [use cases](use-cases.md).

## Limits

- This is a local calculation under declared inputs, not an empirical claim about a deployed agent.
- Read the returned assumptions and limitations before applying the numerical result.

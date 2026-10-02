"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);nodes=[name(n) for n in data["nodes"]];start=name(data["start"]);goal=name(data["goal"])
    if len(set(nodes))!=len(nodes) or start not in nodes or goal not in nodes:raise ValueError("invalid node registry")
    graph=defaultdict(list);reverse=defaultdict(list)
    for e in data["edges"]:
        a,b=e["from"],e["to"];c=num(e["cost"],"edge cost",0)
        if a not in nodes or b not in nodes:raise ValueError("unknown node")
        graph[a].append((b,c));reverse[b].append((a,c))
    h={n:num(data["heuristic"][n],"heuristic",0) for n in nodes};hc=num(data.get("heuristic_cost",0),"heuristic cost",0)
    exact={goal:0};q=[(0,goal)]
    while q:
        cost,a=heapq.heappop(q)
        if cost!=exact[a]:continue
        for b,c in reverse[a]:
            if cost+c<exact.get(b,math.inf):exact[b]=cost+c;heapq.heappush(q,(cost+c,b))
    admissible=all(h[n]<=exact.get(n,math.inf)+1e-12 for n in nodes)
    consistent=all(h[a]<=c+h[b]+1e-12 for a in nodes for b,c in graph[a]) and h[goal]==0
    best={start:0};parent={};q=[(h[start],0,start)];expanded=[];calls=1;path=[];goal_cost=None
    while q:
        f,cost,a=heapq.heappop(q)
        if cost!=best[a]:continue
        expanded.append({"node":a,"g":cost,"f":f})
        if a==goal:
            goal_cost=cost;path=[a]
            while a!=start:a=parent[a];path.append(a)
            path.reverse();break
        for b,c in graph[a]:
            if cost+c<best.get(b,math.inf):best[b]=cost+c;parent[b]=a;calls+=1;heapq.heappush(q,(cost+c+h[b],cost+c,b))
    return result({"path":path,"path_cost":goal_cost,"optimal_cost":exact.get(start),"admissible":admissible,"consistent":consistent,"expansions":len(expanded),"heuristic_calls":calls,"heuristic_total_cost":calls*hc},[series("expanded path cost",[r["g"] for r in expanded],x_label="expansion index",y_label="edge cost units")],"A* stops at the first popped goal and reopens improved states. The exact reverse shortest-path check detects misleading supplied heuristics.",["Finite graph with nonnegative edge costs.","Heuristic costs are separate from path costs."],["An inadmissible heuristic can return a suboptimal goal.","Full-graph heuristic auditing can cost more than the search itself."],expanded)

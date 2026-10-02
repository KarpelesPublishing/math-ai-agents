"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data); nodes=[name(n) for n in data["nodes"]]
    if len(set(nodes))!=len(nodes):raise ValueError("unique nodes required")
    start=name(data["start"]);goal=name(data["goal"])
    if start not in nodes or goal not in nodes:raise ValueError("start and goal must be registered")
    raw=defaultdict(list);allowed=defaultdict(list)
    for e in data["edges"]:
        a,b=name(e["from"]),name(e["to"])
        if a not in nodes or b not in nodes:raise ValueError("unknown edge node")
        raw[a].append(b)
        if flag(e["allowed"]):allowed[a].append(b)
    def bfs(graph):
        dist={start:0};prev={};q=deque([start])
        while q:
            a=q.popleft()
            for b in graph[a]:
                if b not in dist:dist[b]=dist[a]+1;prev[b]=a;q.append(b)
        path=[]
        if goal in dist:
            b=goal;path=[b]
            while b!=start:b=prev[b];path.append(b)
            path.reverse()
        return dist,path
    rd,rp=bfs(raw);ad,ap=bfs(allowed)
    return result({"raw_reachable":goal in rd,"authorized_reachable":goal in ad,"authorized_path":ap,"raw_count":len(rd),"authorized_count":len(ad),"reachable_sinks":[n for n in ad if not allowed[n]]},[series("reachable nodes by path depth",[sum(v<=h for v in ad.values()) for h in range(len(nodes))],x_label="maximum path length",y_label="reachable node count")],"A path is a sequence of permitted possibilities. It does not establish that any action occurred.",["Permissions are frozen at analysis time.","Directed edges describe actual supported interfaces."],["Dynamic permission changes and hidden preconditions require a richer state graph."],{"raw_path":rp,"authorized_distances":ad})

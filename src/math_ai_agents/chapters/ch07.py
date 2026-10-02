"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);H=count(data["horizon"],hi=200);g=num(data["discount"],"discount",0,1);states=data["states"]
    if not states:raise ValueError("states required")
    keys=list(states);V={s:num(states[s].get("terminal",0)) for s in keys};values=[V.copy()];policies=[]
    for h in range(1,H+1):
        nextv={};policy={}
        for s,info in states.items():
            qs={}
            for a in info["actions"]:
                ps=probs(a["probabilities"]);dest=a["next_states"]
                if len(dest)!=len(ps) or any(t not in states for t in dest):raise ValueError("invalid next states")
                qs[name(a["name"])]=num(a["reward"])+g*sum(p*V[t] for p,t in zip(ps,dest))
            if not qs:raise ValueError("state requires at least one action")
            policy[s]=max(qs,key=qs.get);nextv[s]=qs[policy[s]]
        V=nextv;values.append(V.copy());policies.append(policy)
    start=name(data["start"])
    if start not in states:raise ValueError("unknown start")
    return result({"start_value":V[start],"policy_by_remaining_steps":policies,"values_by_remaining_steps":values},[series("optimal start value",[v[start] for v in values],x_label="remaining decisions",y_label="discounted reward")],"Backward induction compares the immediate reward with the discounted value of the next state at each remaining horizon.",["Finite fully observed state model.","Terminal values and discount are declared.","Stopping is represented by an explicit action and terminal state."],["The computed policy is optimal only inside the supplied finite model."])

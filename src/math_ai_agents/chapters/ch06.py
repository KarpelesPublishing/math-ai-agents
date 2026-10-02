"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data)
    actions=data["actions"]
    if not actions: raise ValueError("at least one action required")
    rows=[]
    for a in actions:
        ps=probs(a["probabilities"]); us=vector(a["utilities"])
        cost=num(a.get("cost",0),"cost",0)
        rows.append({"action":name(a["name"]),"expected_utility":dot(ps,us)-cost,"expected_loss":-dot(ps,us)+cost,"cost":cost})
    if len({r["action"] for r in rows})!=len(rows): raise ValueError("action names must be unique")
    winner=max(rows,key=lambda r:r["expected_utility"])
    # First action's first-outcome utility versus the best alternative.
    a=actions[0]; alt=max((r["expected_utility"] for r in rows[1:]),default=None)
    p=a["probabilities"][0]
    threshold=None if alt is None or p==0 else (alt+a.get("cost",0)-sum(p*u for p,u in zip(a["probabilities"][1:],a["utilities"][1:])))/p
    xs=[i/20 for i in range(21)]; sensitivity=[]
    if len(a["probabilities"])==2:
        sensitivity=[x*a["utilities"][0]+(1-x)*a["utilities"][1]-a.get("cost",0) for x in xs]
    curves=[series("expected utility",[r["expected_utility"] for r in rows],x_label="action",y_label="utility units",x_ticklabels=[r["action"] for r in rows])]
    if sensitivity:curves.append(series("first action probability sensitivity",sensitivity,xs,"first-outcome probability","utility units"))
    return result({"selected_action":winner["action"],"expected_utility":winner["expected_utility"],"break_even_first_utility":threshold},curves,"The selected action maximizes the declared expected utility, including any abstention row.",["Utilities and probabilities are supplied judgments.","One decision, mutually exclusive outcomes per action."],["No objective valuation or calibrated probability is inferred."],rows)

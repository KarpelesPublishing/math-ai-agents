"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);p=num(data["candidate_success"],"candidate success",0,1);q=num(data["selector_accuracy"],"selector accuracy",0,1);cost=num(data["sample_cost"],"sample cost",0);lat=num(data["sample_latency"],"sample latency",0);verify=num(data["selector_cost"],"selector cost",0);vlat=num(data["selector_latency"],"selector latency",0);deadline=num(data["deadline"],"deadline",0);budget=num(data["budget"],"budget",0);shared=flag(data["shared_error"]);rows=[]
    for n in data["sample_counts"]:
        n=count(n,"samples",1,1000);coverage=p if shared else 1-(1-p)**n;selected=p if n==1 else coverage*q;expense=n*cost+(verify if n>1 else 0);duration=n*lat+(vlat if n>1 else 0);feasible=expense<=budget and duration<=deadline
        rows.append({"samples":n,"coverage":coverage,"selected_success":selected,"cost":expense,"latency":duration,"feasible":feasible})
    if not rows:raise ValueError("allocations required")
    feasible=[r for r in rows if r["feasible"]];best=max(feasible,key=lambda r:(r["selected_success"],-r["cost"])) if feasible else None
    return result({"selected_allocation":best,"allocations":rows,"shared_error":shared},[series("oracle candidate coverage",[r["coverage"] for r in rows],[r["samples"] for r in rows],"samples","success probability"),series("selector completion",[r["selected_success"] for r in rows],[r["samples"] for r in rows],"samples","success probability")],"Candidate coverage and selected success are different quantities. A correlated shared failure prevents independent-sampling gains; deadlines can remove the largest allocation.",["Selector succeeds with probability q conditional on at least one correct candidate.","One candidate bypasses the selector.","Latency is serial and all candidates have the same declared marginal success."],["Selector accuracy can depend on candidate quality in real workflows.","More samples do not establish correctness when errors or verifier agreement are shared."],rows)

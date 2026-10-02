"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);limit=num(data["risk_limit"],"risk limit",0,1);penalty=num(data["risk_penalty"],"risk penalty",0);rows=[]
    for a in data["actions"]:
        reward=num(a["reward"]);risk=num(a["risk"],"risk",0,1);authorized=flag(a["authorized"])
        rows.append({"name":name(a["name"]),"reward":reward,"risk":risk,"authorized":authorized,"risk_feasible":risk<=limit,"penalized_value":reward-penalty*risk})
    if not rows:raise ValueError("actions required")
    feasible=[r for r in rows if r["authorized"] and r["risk_feasible"]];authorized=[r for r in rows if r["authorized"]]
    return result({"unconstrained_penalty_choice":max(rows,key=lambda r:r["penalized_value"])["name"],"authorized_penalty_choice":max(authorized,key=lambda r:r["penalized_value"])["name"] if authorized else None,"constrained_choice":max(feasible,key=lambda r:r["reward"])["name"] if feasible else None,"feasible_count":len(feasible)},[series("reward by action",[r["reward"] for r in rows],y_label="reward units"),series("risk by action",[r["risk"] for r in rows],y_label="expected adverse-event probability")],"A finite penalty can favor a forbidden or over-limit action. Authorization filters the action set; an expected-risk constraint filters authorized alternatives again.",["Risks are supplied expected probabilities for the same adverse event.","Authorization is a current hard predicate."],["Expected risk does not establish pathwise safety.","Missing feasible actions requires abstention or a new authorized alternative."],rows)

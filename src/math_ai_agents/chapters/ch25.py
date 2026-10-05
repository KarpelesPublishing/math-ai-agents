"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);candidates=data["candidates"];delta=num(data["minimum_guard_gain"],"minimum guard gain");contaminated=flag(data["guard_reused"]);base=[float(v) if type(v) is bool else num(v,"baseline outcomes",0,1) for v in data["baseline_guard"]]
    if not base:raise ValueError("baseline guard must be nonempty")
    if any(v not in (0,1) for v in base):raise ValueError("guard outcomes must be binary")
    rows=[]
    for c in candidates:
        dev=[float(v) if type(v) is bool else num(v,"development",0,1) for v in c["development"]];guard=[float(v) if type(v) is bool else num(v,"guard",0,1) for v in c["guard"]]
        if not dev:raise ValueError("development must be nonempty")
        if len(guard)!=len(base) or any(v not in (0,1) for v in dev+guard):raise ValueError("matched binary guard and binary development required")
        rows.append({"name":name(c["name"]),"development_rate":sum(dev)/len(dev),"guard_rate":sum(guard)/len(guard),"guard_gain":sum(a-b for a,b in zip(guard,base))/len(base)})
    if not rows:raise ValueError("candidates required")
    selected=max(rows,key=lambda r:r["development_rate"]);accepted=selected["guard_gain"]>=delta and not contaminated
    return result({"selected_candidate":selected["name"],"selected_guard_gain":selected["guard_gain"],"release_accepted":accepted,"guard_contaminated":contaminated,"baseline_guard_rate":sum(base)/len(base)},[series("development selection",[r["development_rate"] for r in rows],y_label="success fraction"),series("guard gains",[r["guard_gain"] for r in rows],y_label="candidate minus baseline")],"Development selects one candidate. Only that frozen candidate is checked against the declared guard threshold, and a reused guard invalidates the clean-release claim.",["Guard rows are paired with baseline by their position.","Acceptance threshold is declared before observing guard outcomes.","Guard is reserved for this single decision."],["Passing a finite gate is not certification or a confidence guarantee.","Reporting every candidate's guard result requires keeping those results out of future selection."],rows)

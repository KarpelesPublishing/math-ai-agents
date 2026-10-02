"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data); records=data["records"]
    if not records: raise ValueError("records required")
    groups=defaultdict(list); pairs=defaultdict(dict);seen=set()
    for r in records:
        proc=name(r["procedure"]);task=name(r["task"]);run=name(r["run"]); success=flag(r["success"])
        k=(proc,task,run)
        if k in seen:raise ValueError("duplicate procedure/task/run observation")
        seen.add(k);groups[proc].append(r);pairs[(task,run)][proc]=success
        num(r.get("cost",0),"cost",0);flag(r.get("exposed",False),"exposed")
    summaries={}
    for p,rs in groups.items():
        n=len(rs);s=sum(r["success"] for r in rs);ex=[r for r in rs if r.get("exposed",False)]
        summaries[p]={"n":n,"successes":s,"rate":s/n,"wilson_interval_iid":wilson(s,n),"mean_cost":sum(r["cost"] for r in rs)/n if all("cost" in r for r in rs) else None,"cost_observed_n":sum("cost" in r for r in rs),"exposed_n":len(ex),"exposed_rate":sum(r["success"] for r in ex)/len(ex) if ex else None}
    baseline=name(data["baseline"]);candidate=name(data["candidate"])
    if baseline not in groups or candidate not in groups or baseline==candidate: raise ValueError("two observed distinct procedures required")
    diffs=[int(ps[candidate])-int(ps[baseline]) for ps in pairs.values() if baseline in ps and candidate in ps]
    n=len(diffs);delta=sum(diffs)/n if n else None
    se=math.sqrt(sum((v-delta)**2 for v in diffs)/(n-1)/n) if n>1 else None
    weights=data.get("task_weights"); mixture={}
    if weights is not None:
        probs(list(weights.values()),"task weights")
        for p,rs in groups.items():
            rates={t:[r["success"] for r in rs if r["task"]==t] for t in weights if weights[t]>0}
            mixture[p]=sum(weights[t]*sum(v)/len(v) for t,v in rates.items()) if all(rates.values()) else None
    return result({"procedures":summaries,"matched_n":n,"matched_difference":delta,"matched_standard_error_iid_pairs":se,"task_mixture_rates":mixture,"trajectory_success_estimate":None},[series("observed success rates",[v["rate"] for v in summaries.values()],y_label="success fraction"),series("matched candidate minus baseline",diffs,y_label="paired difference") if diffs else series("observed run counts",[v["n"] for v in summaries.values()],y_label="run count")],"Rates use observed runs. Matched differences use only common task/run identifiers; missing pairs stay unavailable. A stepwise trajectory law is not identified.",["Identifiers declare pairing, not randomization.","Intervals require independent representative Bernoulli sampling; repeated-task dependence can invalidate them.","Task weights refer to the named target mixture."],["Observed exposure subsets need not represent the target population.","No causal effect or long-run guarantee follows from an average."],{"matched_differences":diffs,"procedure_order":list(summaries)})

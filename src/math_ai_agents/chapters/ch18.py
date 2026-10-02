"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);age=num(data["observation_age"],"observation age",0);maxage=num(data["max_age"],"max age",0);obs=name(data["observed_version"]);current=name(data["current_version"]);permission=flag(data["current_permission"]);ack=flag(data["effect_confirmed"]);coordinate=name(data["coordinate_target"]);semantic=name(data["semantic_target"]);wanted=name(data["wanted_target"])
    fresh=age<=maxage;rows=[];extra={}
    if "change_rate" in data:
        rate=num(data["change_rate"],"change rate",0);delays=vector(data.get("delays",[]),"delays",0) if data.get("delays") else []
        extra={"change_rate":rate,"freshness_probability_at_age":math.exp(-rate*age),"freshness_probability_at_max_age":math.exp(-rate*maxage),"freshness_by_delay":[{"delay":d,"freshness_probability":math.exp(-rate*d)} for d in delays]}
    elif "delays" in data:raise ValueError("delays require change_rate")
    for method,target,versionok in [("coordinate",coordinate,True),("semantic",semantic,True),("version-bound",semantic,obs==current)]:
        issued=fresh and permission and versionok;correct=target==wanted;completed=issued and correct and ack
        rows.append({"method":method,"fresh":fresh,"version_matches":versionok,"authorized":permission,"issued":issued,"correct_target":correct,"confirmed_completion":completed})
    return result({"methods":rows,"stale_observation":not fresh,"layout_changed":obs!=current,**extra},[series("issued action",[int(r["issued"]) for r in rows],y_label="issued flag"),series("authorized confirmed completion",[int(r["confirmed_completion"]) for r in rows],y_label="completion flag")],"Coordinates name a location; semantic targets name an object; a version-bound action also refuses a changed observation boundary. Current permission is checked at issuance.",["Targets and current permission are supplied observations.","Freshness uses the declared age limit.","If change_rate is supplied, Fresh(delay)=exp(-change_rate*delay) assumes invalidating changes arrive at a constant rate; it is reported beside, and does not replace, the age-limit rule."],["Semantic resolution can itself be wrong.","A click or issued request is not confirmation of its effect."],rows)

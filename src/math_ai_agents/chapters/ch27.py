"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);arrival=num(data["arrival_rate"],"arrival rate",0);service=num(data["service_rate"],"service rate",0.000001);fraction=num(data["delegation_fraction"],"delegation fraction",0,1);effective=arrival*fraction;stable=effective<service;wait=1/(service-effective) if stable else None;rows=[]
    for t in data["tasks"]:
        authority=flag(t["agent_authorized"]);risk=num(t["risk"],"risk",0,1);limit=num(data["agent_risk_limit"],"risk limit",0,1);deadline=num(t["deadline"],"deadline",0);human=flag(t["human_authorized"]);receipt=flag(t["review_received"])
        needs=not authority or risk>limit;late=needs and (not stable or wait>deadline);released=(not needs and authority) or (needs and human and receipt and not late)
        rows.append({"task":name(t["name"]),"delegation_required":needs,"queue_mean_exceeds_deadline":late,"released":released,"review_packet_required":needs and not receipt})
    if not rows:raise ValueError("tasks required")
    loads=[service*i/100 for i in range(100)];times=[1/(service-v) for v in loads]
    return result({"effective_review_arrival_rate":effective,"queue_stable":stable,"mean_review_sojourn":wait,"tasks":rows,"released_count":sum(r["released"] for r in rows)},[series("review queue sensitivity",times,loads,"review arrivals per time unit","mean review time")],"Delegation moves work into a limited review service. Missing authority remains a release blocker even when expected review capacity is adequate.",["M/M/1 review queue with Poisson arrivals, exponential service, one reviewer.","Arrival and service rates use the same time unit.","Deadline test uses mean queue sojourn as a diagnostic, not a per-task prediction."],["A queue mean does not prove any individual deadline will be met.","A human review receipt grants only the supplied current authority."] ,rows)

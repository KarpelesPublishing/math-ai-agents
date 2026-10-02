"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);g=num(data["discount"],"discount",0,1);deadline=count(data["deadline"],"deadline",0,1000);start=num(data.get("start_time",0),"start time",0)
    interrupt=data.get("interrupt_after")
    if interrupt is not None:interrupt=count(interrupt,"interrupt after",0,1000)
    options=data["options"]
    if not options:raise ValueError("options required")
    rows=[]
    for o in options:
        rewards=vector(o["rewards"]);duration=len(rewards);eligible=flag(o["initiation"]);terminated=flag(o["terminated"])
        execute=min(duration,max(0,int(deadline-start)),duration if interrupt is None else interrupt) if eligible else 0
        complete=eligible and execute==duration and terminated
        value=sum(g**t*r for t,r in enumerate(rewards[:execute]))+(g**duration*num(o.get("continuation_value",0)) if complete else 0)
        rows.append({"name":name(o["name"]),"duration":duration,"initiated":eligible,"executed":execute,"complete":complete,"value":value,"continuation_discount":g**duration if complete else 0})
    return result({"options":rows,"best_executed_value":max((r for r in rows if r["initiated"]),key=lambda r:r["value"],default={"name":None})["name"],"completed_options":sum(r["complete"] for r in rows)},[series("option value",[r["value"] for r in rows],y_label="discounted reward"),series("executed duration",[r["executed"] for r in rows],y_label="primitive steps")],"An option receives continuation value only after its declared termination. A deadline or interruption can leave locally useful work without workflow completion.",["Rewards occur at primitive time offsets beginning at zero.","Continuation discount uses the full option duration.","Initiation and termination predicates are declared for this state."],["The finite reward trace is not a learned option policy.","An interrupted option needs a recovery contract before reuse."],rows)

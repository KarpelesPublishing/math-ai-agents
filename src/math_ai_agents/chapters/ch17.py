"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data)
    idem=flag(data["idempotent"]); effects=0; confirmed=False; keys={}; trace=[]; unresolved=False; operation_payload=None
    for e in data["events"]:
        kind=e["kind"]
        if kind=="request":
            key=name(e["key"]); payload=name(e["payload"]);
            if operation_payload is not None and payload != operation_payload: raise ValueError("Trace must describe one logical payload; analyze separate operations separately")
            operation_payload=payload
            happened=flag(e["effect"]); ack=flag(e["ack"])
            if key in keys and keys[key]!=payload: raise ValueError("idempotency key reused for different payload")
            duplicate=idem and key in keys
            if happened and not duplicate:effects+=1;keys[key]=payload
            if ack and not happened and not duplicate: raise ValueError("acknowledgement cannot confirm absent effect")
            confirmed=confirmed or ack;unresolved=False if ack else unresolved or (happened and not ack)
        elif kind=="verify":
            seen=flag(e["observed_effect"])
            if seen and effects==0: raise ValueError("verification conflicts with effect ledger")
            confirmed=confirmed or seen
            if seen:unresolved=False
        else:raise ValueError("unknown event kind")
        trace.append({"kind":kind,"effects":effects,"confirmed":confirmed})
    if not trace: raise ValueError("trace must be nonempty")
    verify=num(data["verify_cost"],"verification cost",0);retry=num(data["retry_cost"],"retry cost",0)
    prior=num(data["effect_probability"],"probability",0,1); harm=num(data["duplicate_cost"],"duplicate cost",0)
    retry_expected=retry+(0 if idem else prior*harm)
    return result({"effects":effects,"duplicate_effects":max(0,effects-1),"confirmed":confirmed,"unresolved":unresolved,"verification_cost":verify,"retry_expected_cost":retry_expected,"preferred_next_step":"stop" if confirmed and not unresolved else ("verify" if verify<retry_expected else "retry")},[series("cumulative effects",[r["effects"] for r in trace],x_label="event index",y_label="effect count"),series("confirmation",[int(r["confirmed"]) for r in trace],x_label="event index",y_label="confirmed flag")],"The ledger distinguishes a real effect from receipt of its acknowledgement. Retry pricing is conditional on the supplied unresolved-effect probability.",["Trace effect flags describe actual local events.","Idempotence requires stored key and payload equality.","Verification is assumed perfect for the cost comparison."],["No remote effect or eventual completion guarantee is inferred.","The comparison prices one next step, not an entire recovery policy."],trace)

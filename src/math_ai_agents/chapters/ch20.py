"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);rounds=count(data["rounds"],"rounds",1,6);drop=num(data["drop_probability"],"drop probability",0,1);rows=[]
    # Each round sends a request, followed by an acknowledgement if received.
    for bits in itertools.product((False,True),repeat=2*rounds):
        weight=math.prod((1-drop if b else drop) for b in bits);alice=[];bob=[];received=False;ackseen=False
        for t in range(rounds):
            req,ack=bits[2*t:2*t+2];alice.append("send")
            if req:received=True;bob.append("request")
            if req and ack:ackseen=True;alice.append("ack")
            bob.append("tick");alice.append("tick")
        rows.append({"probability":weight,"alice_view":tuple(alice),"bob_view":tuple(bob),"received":received,"ack_seen":ackseen})
    possible=[r for r in rows if r["probability"]>0];av=defaultdict(list);bv=defaultdict(list)
    for r in possible:av[r["alice_view"]].append(r);bv[r["bob_view"]].append(r)
    agreement=0;aliceknows=0;bobknows=0;unsafe=0
    for r in possible:
        ak=all(w["received"] for w in av[r["alice_view"]]);bk=all(w["ack_seen"] for w in bv[r["bob_view"]]);pa=r["ack_seen"];pb=r["received"];p=r["probability"]
        agreement+=p*(pa==pb);aliceknows+=p*ak;bobknows+=p*bk;unsafe+=p*(pb and not pa)
    return result({"enumerated_worlds":len(rows),"possible_worlds":len(possible),"agreement_probability":agreement,"alice_knows_delivery_probability":aliceknows,"bob_knows_ack_receipt_probability":bobknows,"bob_commits_without_alice_probability":unsafe},[series("agreement across retry budget",[1-((1-(1-drop)**2)**r-drop**r) for r in range(1,rounds+1)],list(range(1,rounds+1)),"request rounds","agreement probability")],"Alice commits after an acknowledgement; Bob commits after a request. Local knowledge is checked over indistinguishable positive-probability bounded histories.",["Independent drops per message opportunity.","Bob does not observe whether his acknowledgement arrived.","The model contains a fixed bounded number of rounds."],["Finite agreement probability is not common knowledge or an asynchronous consensus theorem.","No hidden timeout, failure detector, or extra receipt is assumed."])

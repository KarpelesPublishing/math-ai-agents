"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);budget=count(data["budget"],"budget",0,10000);now=num(data["now"],"now",0);version=name(data["current_version"]);records=data["records"]
    if len(records)>20:raise ValueError("exact retrieval limited to 20 records")
    valid=[];stale=[];rows=[]
    for r in records:
        tokens=count(r["tokens"],"tokens",1,10000);value=num(r["decision_value"],"decision value",0);stamp=num(r["timestamp"],"timestamp",0);ttl=num(r["ttl"],"ttl",0);authority=flag(r["authority"])
        if stamp>now:raise ValueError("record timestamp is in the future")
        fresh=now-stamp<=ttl;authok=not authority or name(r["version"])==version
        row={"id":name(r["id"]),"tokens":tokens,"value":value,"fresh":fresh,"authority_valid":authok};rows.append(row)
        (valid if fresh and authok else stale).append(row)
    frontier=[0.0]*(budget+1);choices=[[] for _ in range(budget+1)]
    for record in valid:
        for b in range(budget,record["tokens"]-1,-1):
            previous=b-record["tokens"];value=frontier[previous]+record["value"]
            if value>frontier[b]:frontier[b]=value;choices[b]=choices[previous]+[record]
    best=choices[budget];bestvalue=frontier[budget]
    original=vector(data["original_action_values"]);compressed=vector(data["compressed_action_values"])
    if len(original)!=len(compressed):raise ValueError("compression action vectors must match")
    old=max(range(len(original)),key=lambda i:original[i]);new=max(range(len(compressed)),key=lambda i:compressed[i])
    return result({"retrieved_ids":[r["id"] for r in best],"retrieval_value":bestvalue,"tokens_used":sum(r["tokens"] for r in best),"excluded_ids":[r["id"] for r in stale],"compression_preserves_action":old==new,"original_action":old,"compressed_action":new},[series("retrieval budget frontier",frontier,x_label="token budget",y_label="declared decision value")],"Retrieval optimizes declared decision value among records that satisfy freshness and version-bound authority checks. Compression is checked by the action it preserves.",["Record values are additive and supplied, not inferred from text similarity.","Exact finite subset search; no semantic embedding model."],["Preserving one decision vector does not prove sufficiency for every future task.","Retrieval relevance is not authority."] ,rows)

"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);P=[probs(r) for r in data["true_transition"]];Q=[probs(r) for r in data["model_transition"]];r=vector(data["rewards"],"rewards",0);k=len(r)
    if len(P)!=k or len(Q)!=k or any(len(row)!=k for row in P+Q):raise ValueError("square kernels and rewards must align")
    g=num(data["discount"],"discount",0,0.9999);H=count(data["horizon"],hi=1000);R=max(r);eps=max(0.5*sum(abs(a-b) for a,b in zip(p,q)) for p,q in zip(P,Q));v=[0]*k;w=[0]*k;errors=[];bounds=[]
    for h in range(1,H+1):
        v=[r[i]+g*dot(P[i],v) for i in range(k)];w=[r[i]+g*dot(Q[i],w) for i in range(k)]
        errors.append(max(abs(a-b) for a,b in zip(v,w)));bounds.append(R*eps*h*(h-1)/2)
    discounted=g*eps*R/(1-g)**2
    return result({"uniform_tv_error":eps,"true_values":v,"model_values":w,"max_finite_value_error":errors[-1],"discounted_infinite_bound":discounted,"finite_horizon_bound":bounds[-1]},[series("actual finite-horizon value error",errors,list(range(1,H+1)),"reward horizon","reward units"),series("finite-horizon bound",bounds,list(range(1,H+1)),"reward horizon","reward units")],"Both kernels share the same immediate reward vector under one fixed policy. The uniform total-variation error controls the conditional bound; the actual finite error can be much smaller.",["Fixed policy absorbed into each transition matrix.","Common expected immediate reward in [0,R].", "Finite calculation has zero terminal continuation; discounted bound assumes gamma below one."],["A bound is not a measured planning error.","This state-value bound alone does not certify an action ranking.","Reward-model error would require an additional term."])

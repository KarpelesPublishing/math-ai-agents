"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);states=[name(s) for s in data["states"]];rs=vector(data["rewards"]);g=num(data["discount"],"discount",0,1);a=num(data["learning_rate"],"learning rate",0,1);lam=num(data["lambda"],"lambda",0,1);terminal=flag(data["terminal"])
    if len(states)!=len(rs)+1:raise ValueError("trajectory requires one more state than rewards")
    initial={s:num(data["values"][s]) for s in set(states)};boot=0 if terminal else initial[states[-1]]
    returns=[0]*len(rs);G=boot
    for t in range(len(rs)-1,-1,-1):G=rs[t]+g*G;returns[t]=G
    mc=initial.copy();td=initial.copy();trace=initial.copy();elig={s:0 for s in initial};deltas=[]
    for t,r in enumerate(rs):
        s,n=states[t:t+2];mc[s]+=a*(returns[t]-mc[s]);nexttd=0 if terminal and t==len(rs)-1 else td[n];delta=r+g*nexttd-td[s];td[s]+=a*delta
        nexttr=0 if terminal and t==len(rs)-1 else trace[n];err=r+g*nexttr-trace[s];elig[s]+=1
        for key in elig:trace[key]+=a*err*elig[key];elig[key]*=g*lam
        deltas.append(err)
    return result({"returns":returns,"monte_carlo_values":mc,"td_zero_values":td,"td_lambda_values":trace,"bootstrap_value":boot},[series("return targets",returns,x_label="trajectory transition",y_label="discounted reward"),series("TD trace errors",deltas,x_label="trajectory transition",y_label="TD error")],"All three estimators see the same rewards. A truncated trajectory retains its supplied final bootstrap value; a terminal trajectory sets that continuation to zero.",["One sequential pass with accumulating eligibility traces.","Initial values, discount, step size, and terminal status are declared."],["This finite update does not demonstrate convergence.","Bootstrapping trades dependence on later observations for dependence on current estimates."])

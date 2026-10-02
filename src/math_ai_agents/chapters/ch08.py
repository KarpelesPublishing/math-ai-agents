"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);b=probs(data["belief"]);P=[probs(r) for r in data["transition"]];O=[probs(r) for r in data["observation"]];k=len(b)
    if len(P)!=k or any(len(r)!=k for r in P) or len(O)!=k or len({len(r) for r in O})!=1:raise ValueError("kernel dimensions incompatible")
    rewards=[vector(r) for r in data["action_rewards"]]
    if not rewards or any(len(r)!=k for r in rewards):raise ValueError("action rewards dimensions incompatible")
    pred=[sum(b[i]*P[i][j] for i in range(k)) for j in range(k)];obs=count(data["observed"],"observed",0,len(O[0])-1)
    obsprob=[sum(pred[s]*O[s][o] for s in range(k)) for o in range(len(O[0]))]
    if obsprob[obs]==0:raise ValueError("observation impossible under supplied model")
    posterior=[pred[s]*O[s][obs]/obsprob[obs] for s in range(k)]
    now=max(dot(pred,r) for r in rewards);future=0
    for o,po in enumerate(obsprob):
        if po:future+=po*max(dot([pred[s]*O[s][o]/po for s in range(k)],r) for r in rewards)
    cost=num(data["observation_cost"],"observation cost",0)
    return result({"predictive_belief":pred,"posterior":posterior,"observed_probability":obsprob[obs],"act_now_value":now,"observe_then_act_value":future-cost,"gross_value_of_information":future-now,"net_value_of_information":future-now-cost,"posterior_action":max(range(len(rewards)),key=lambda a:dot(posterior,rewards[a]))},[series("prior and posterior first state",[b[0],pred[0],posterior[0]],y_label="belief probability"),series("observation value versus cost",[future-now-c for c in [0,cost,2*cost]],x=[0,cost,2*cost],x_label="observation cost",y_label="net information value")],"Bayes' rule updates the belief, while information value averages optimal later decisions over all possible observations.",["Transition precedes observation.","Information arrives before one decision.","Observation incurs the declared cost."],["A likely observation is not necessarily useful; identical observation rows give no information."])

"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);rewards=vector(data["rewards"]);success=vector(data["success_probabilities"],"success probabilities",0,1);pot=vector(data["terminal_potentials"]);k=len(rewards)
    if len(success)!=k or len(pot)!=k:raise ValueError("action vectors must align")
    episodes=count(data["episodes"],hi=10000);seeds=data["seeds"]
    if not seeds:raise ValueError("seeds required")
    lr=num(data["learning_rate"],"learning rate",0,1);g=num(data["discount"],"discount",0,1);curves=[];runs=[]
    shaped_all=[r+g*v for r,v in zip(rewards,pot)]
    for seed in seeds:
        rng=random.Random(count(seed,"seed",0,2**32-1));logits=[0]*k;history=[]
        for t in range(episodes):
            z=max(logits);weights=[math.exp(v-z) for v in logits];p=[v/sum(weights) for v in weights];u=rng.random();cum=0;chosen=k-1
            for i,pi in enumerate(p):
                cum+=pi
                if u<cum:chosen=i;break
            shaped=shaped_all[chosen];baseline=dot(p,shaped_all)
            for i in range(k):logits[i]+=lr*(shaped-baseline)*(int(i==chosen)-p[i])
            z=max(logits);ws=[math.exp(v-z) for v in logits];p=[v/sum(ws) for v in ws];history.append(dot(p,shaped_all))
        external=dot(p,success);evalrng=random.Random(seed+1000003);n=count(data.get("evaluation_runs",100),hi=10000);evalwins=0
        for _ in range(n):
            u=evalrng.random();cum=0;chosen=k-1
            for i,pi in enumerate(p):
                cum+=pi
                if u<cum:chosen=i;break
            evalwins+=evalrng.random()<success[chosen]
        runs.append({"seed":seed,"policy":p,"expected_training_reward":dot(p,rewards),"expected_shaped_reward":dot(p,shaped_all),"expected_external_success":external,"independent_evaluation_rate":evalwins/n,"evaluation_n":n})
        curves.append(series("shaped training reward seed "+str(seed),history,x_label="episode",y_label="expected shaped reward (trained on)"))
    return result({"runs":runs,"policy_invariant_shaping_condition":all(v==0 for v in pot),"verifier_optimal_action":max(range(k),key=lambda i:rewards[i]),"shaped_rewards":shaped_all,"shaped_optimal_action":max(range(k),key=lambda i:shaped_all[i]),"training_objective_conflicts_with_task":max(range(k),key=lambda i:shaped_all[i])!=max(range(k),key=lambda i:success[i]),"task_optimal_action":max(range(k),key=lambda i:success[i])},curves,"REINFORCE updates softmax logits from sampled actions and a baseline, using the shaped reward (verifier reward plus discount times terminal potential). verifier_optimal_action ranks the unshaped rewards, shaped_optimal_action ranks the rewards actually trained on, and expected_training_reward is the unshaped expectation while expected_shaped_reward is the trained one. Independent evaluation uses a separate seeded stream and external success probabilities.",["One-step finite policy; rewards are deterministic after each chosen action.","Potential shaping is gamma times the supplied terminal potential with zero initial potential.","Zero terminal potential preserves the episodic objective."],["Nonzero terminal potentials can change the objective.","Verifier reward improvement need not improve external task success.","Constructed success probabilities are not learned from actual deployments."],runs)

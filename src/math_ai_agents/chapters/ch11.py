"""Local, declared-input chapter experiment. No external services."""
from ._shared import *


def evaluate(data):
    check_tree(data);means=vector(data["means"],"means",0,1);T=count(data["rounds"],hi=10000);seed=count(data["seed"],"seed",0,2**32-1);cost=num(data["pull_cost"],"pull cost",0);rows={};curves=[]
    for policy in ("greedy","ucb","thompson"):
        rng=random.Random(seed);counts=[0]*len(means);wins=[0]*len(means);regret=0;history=[];earned=0
        for t in range(T):
            if 0 in counts:a=counts.index(0)
            elif policy=="greedy":a=max(range(len(means)),key=lambda a:wins[a]/counts[a])
            elif policy=="ucb":a=max(range(len(means)),key=lambda a:wins[a]/counts[a]+math.sqrt(2*math.log(t)/counts[a]))
            else:a=max(range(len(means)),key=lambda a:rng.betavariate(wins[a]+1,counts[a]-wins[a]+1))
            reward=int(rng.random()<means[a]);counts[a]+=1;wins[a]+=reward;earned+=reward-cost;regret+=max(means)-means[a];history.append(regret)
        posterior=[(wins[a]+1)/(counts[a]+2) for a in range(len(means))];now=max(posterior);voi=[]
        for a in range(len(means)):
            chance=posterior[a];after_success=posterior[:];after_failure=posterior[:]
            after_success[a]=(wins[a]+2)/(counts[a]+3);after_failure[a]=(wins[a]+1)/(counts[a]+3)
            voi.append(chance*max(after_success)+(1-chance)*max(after_failure)-now)
        rows[policy]={"counts":counts,"successes":wins,"cumulative_pseudo_regret":regret,"net_observed_reward":earned,"posterior_means":posterior,"one_pull_gross_information_value":voi,"one_pull_net_information_value":[v-cost for v in voi]}
        curves.append(series(policy+" pseudo-regret",history,x_label="round",y_label="expected reward shortfall"))
    return result({"policies":rows,"oracle_mean":max(means),"seed":seed},curves,"Pseudo-regret uses known constructed means, whereas realized reward comes from seeded Bernoulli draws. Posterior sampling draws a belief; it does not certify an arm.",["Stationary independent Bernoulli rewards within each arm.","All policies initialize each arm once when the budget permits.","Thompson sampling uses independent Beta(1,1) priors."],["Known means are a teaching oracle, usually unavailable in deployed logs.","One seed is not a policy-performance estimate.","Information value is not identical to cumulative regret."],rows)

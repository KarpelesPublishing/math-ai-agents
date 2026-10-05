"""Task mixtures, repeated-run probabilities, and observed subset counts."""
from __future__ import annotations
from math import comb
from agent_probe_common import cli, probability, positive_integer

def mixture(probabilities,k):
    k=positive_integer(k)
    ps=[probability(p) for p in probabilities]
    if not ps or k<1:
        raise ValueError('at least one task and a positive repetition count required')
    mean=sum(ps)/len(ps)
    return {'single_run_mean':mean,'all_success':sum(p**k for p in ps)/len(ps),
            'at_least_one':sum(1-(1-p)**k for p in ps)/len(ps),
            'power_of_mean':mean**k,'coverage_using_mean':1-(1-mean)**k}

def observed_subsets(runs,k):
    k=positive_integer(k)
    if any(type(v) is not bool for v in runs) or k<1:
        raise ValueError('Boolean outcomes and positive repetition count required')
    n,c=len(runs),sum(runs)
    if n<k:
        return {'trials':n,'successes':c,'all_success':None,'at_least_one':None}
    return {'trials':n,'successes':c,'all_success':comb(c,k)/comb(n,k),
            'at_least_one':1-comb(n-c,k)/comb(n,k)}

def evaluate(data):
    """Exact IID-within-task construction; sample subset fractions remain descriptive."""
    k=positive_integer(data['repetitions'])
    exposure=probability(data['exposed_fraction'])
    unseen=probability(data['unfamiliar_success'])
    return {'equal_weight_population_mixture':mixture(data['task_probabilities'],k),
            'observed_bank':observed_subsets(data['observed_runs'],k),
            'exposure_construction':{'unfamiliar_success':unseen,'mixture_success':exposure+(1-exposure)*unseen}}

if __name__ == '__main__':
    cli(evaluate)

"""REINFORCE for a two-action constructed policy, with independent evaluation."""
from __future__ import annotations
import math
import random
from agent_probe_common import cli, probability, nonnegative, positive_integer

def sigmoid(phi):
    if phi >= 0:
        return 1 / (1 + math.exp(-phi))
    e = math.exp(phi)
    return e / (1 + e)

def expected(p, cost=0.05):
    p = probability(p)
    cost = nonnegative(cost)
    return {'external_success': 0.55 + 0.25*p, 'external_utility': 0.55 + (0.25-cost)*p,
            'verifier_value': 0.63 + (0.15-cost)*p, 'expected_cost': cost*p}

def potential_return(rewards, potentials, gamma):
    if len(potentials) != len(rewards) + 1 or not 0 <= gamma <= 1:
        raise ValueError('one potential per visited state and a valid discount required')
    original = sum(gamma**t*r for t,r in enumerate(rewards))
    shaped = sum(gamma**t*(r + gamma*potentials[t+1]-potentials[t]) for t,r in enumerate(rewards))
    return original, shaped, original-potentials[0]+gamma**len(rewards)*potentials[-1]

def train(seed, episodes, rate, reward_rule):
    episodes = positive_integer(episodes)
    rate = nonnegative(rate)
    if episodes <= 0 or rate <= 0 or reward_rule not in {'external', 'verifier', 'avoid_retrieval'}:
        raise ValueError('positive episodes/rate and a named reward rule required')
    rng = random.Random(seed)
    phi = 0.0
    for _ in range(episodes):
        p = sigmoid(phi)
        retrieve = int(rng.random() < p)
        correct = rng.random() < (0.80 if retrieve else 0.55)
        if reward_rule == 'verifier':
            score = float(rng.random() < (0.9 if correct else 0.3))
        else:
            score = float(correct)
        score -= 0.05*retrieve
        if reward_rule == 'avoid_retrieval':
            score += 0.30*(1-retrieve)
        # Only the selected policy action receives the log-probability gradient.
        phi += rate*(retrieve-p)*score
    return sigmoid(phi)

def sample_evaluation(p, seed, trials):
    p = probability(p)
    trials = positive_integer(trials)
    if trials <= 0:
        raise ValueError('positive evaluation trial count required')
    rng = random.Random(seed)
    correct = retrievals = 0
    for _ in range(trials):
        retrieve = rng.random() < p
        retrievals += retrieve
        correct += rng.random() < (0.80 if retrieve else 0.55)
    return {'trials':trials, 'successes':correct, 'external_success_estimate':correct/trials,
            'total_retrieval_cost':0.05*retrievals}

def evaluate(data):
    """Update a finite policy; report exact expectations apart from sampled outcomes."""
    seed = int(data['training_seed'])
    eval_seed = int(data['evaluation_seed'])
    if seed == eval_seed:
        raise ValueError('use separate training and evaluation seeds')
    results = []
    for rule in ('external','verifier','avoid_retrieval'):
        p = train(seed, positive_integer(data['episodes']), nonnegative(data['learning_rate']), rule)
        results.append({'reward_rule':rule, 'retrieve_probability':p, 'exact_population_quantities':expected(p),
                        'held_out_sample':sample_evaluation(p,eval_seed,positive_integer(data['evaluation_trials']))})
    return {'frozen_baseline':expected(0.5), 'trained':results,
            'shortcut':{'external_success':0,'verifier_value':0.95},
            'potential_example':potential_return([0,1],[0,0.4,0],1)}

if __name__ == '__main__':
    cli(evaluate)

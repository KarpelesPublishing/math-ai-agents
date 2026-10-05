"""Costs per success, feasibility and a finite Pareto frontier."""
from __future__ import annotations
from agent_probe_common import cli, probability, nonnegative, boolean

def cost_per_success(costs, completions):
    if len(costs) != len(completions) or any(c < 0 for c in costs):
        raise ValueError('matching runs and nonnegative costs required')
    if any(type(v) is not bool for v in completions):
        raise ValueError('completion flags must be Boolean')
    costs = [nonnegative(c) for c in costs]
    successes = sum(completions)
    return sum(costs)/successes if successes else None

def dominates(a,b):
    return (a['success'] >= b['success'] and a['cost'] <= b['cost'] and a['latency'] <= b['latency']
            and (a['success'] > b['success'] or a['cost'] < b['cost'] or a['latency'] < b['latency']))

def evaluate(data):
    """Use declared population inputs; never infer authority from a reward penalty."""
    rows=[]
    threshold=probability(data['minimum_success'])
    deadline=nonnegative(data['deadline'])
    for original in data['procedures']:
        row=dict(original)
        row['success']=probability(row['success'])
        row['cost']=nonnegative(row['cost'])
        row['latency']=nonnegative(row['latency'])
        row['authorized']=boolean(row['authorized'])
        row['population_cost_per_success']=row['cost']/row['success'] if row['success'] else None
        row['feasible']=row['success']>=threshold and row['latency']<=deadline and row['authorized']
        rows.append(row)
    return {'procedures':rows, 'pareto_frontier':[r['name'] for r in rows if r['authorized'] and
            not any(q['authorized'] and dominates(q,r) for q in rows)],
            'zero_success_example':{'total_cost':5,'successes':0,'ratio':cost_per_success([2,3],[False,False])}}

if __name__ == '__main__':
    cli(evaluate)

"""Dependency schedules and a common-cause failure construction."""
from __future__ import annotations
from agent_probe_common import cli, probability, nonnegative, positive_integer

def failures(shared, individual):
    shared, individual = probability(shared), probability(individual)
    marginal = shared + (1-shared)*individual
    joint = shared + (1-shared)*individual**2
    return {'marginal_failure':marginal,'joint_failure':joint,'product_of_marginals':marginal**2}

def capability_handoff(parent, requested):
    return sorted(set(parent).intersection(requested))

def evaluate(data):
    """Compare total work and elapsed time under explicit independence/capacity assumptions."""
    duration = nonnegative(data['check_duration'])
    overhead = nonnegative(data['dispatch_and_combine_duration'])
    capacity = positive_integer(data['service_capacity'])
    if min(duration,overhead) < 0 or capacity < 1:
        raise ValueError('nonnegative durations and positive capacity required')
    return {'timing_boundary':'Evidence checks and supervisor dispatch/combine only; final verification duration is excluded. Total work costs include final verification.',
            'serial':{'elapsed':2*duration,'total_work_cost':5},
            'team':{'elapsed':(duration if capacity>=2 else 2*duration)+overhead,'total_work_cost':8},
            'shared_source':failures(data['shared_failure'],data['individual_failure']),
            'independent_source':failures(0,data['individual_failure']),
            'child_capabilities':capability_handoff(data['parent_capabilities'],data['requested_capabilities'])}

if __name__ == '__main__':
    cli(evaluate)

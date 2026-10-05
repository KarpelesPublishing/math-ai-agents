"""A command's target depends on layout; permission constrains its effect."""
from __future__ import annotations
from agent_probe_common import cli, boolean

def execute(case):
    mediated = boolean(case['mediated'])
    dropped_ack = boolean(case.get('dropped_acknowledgement', False))
    layout = case['current_layout']
    if len(set(layout)) != len(layout):
        raise ValueError('document identifiers must be unique within a layout')
    target = case['intended_document']
    mode = case['interface']
    if mode not in {'coordinate', 'semantic', 'transactional'}:
        raise ValueError('unknown interface')
    if mode == 'coordinate':
        row = case['observed_layout'].index(target)
        reached = layout[row] if row < len(layout) else None
    else:
        reached = target if target in layout else None
    allowed = reached in case['approved_documents']
    stale_token = mode == 'transactional' and case['observed_version'] != case['current_version']
    if reached is None or stale_token or (mediated and not allowed):
        effect, outcome = None, 'denied'
    else:
        effect = reached
        outcome = 'pending' if dropped_ack else 'confirmed'
    return {'intended_document': target, 'reached_document': reached, 'effect_document': effect,
            'outcome': outcome, 'authorized_completion': bool(effect == target and allowed and outcome == 'confirmed'),
            'unauthorized_effect': bool(effect is not None and not allowed),
            'effect_confirmation_available': outcome == 'confirmed'}

def evaluate(data):
    """Compare known layouts. No visual model or production service is measured."""
    return [execute(case) for case in data['cases']]

if __name__ == '__main__':
    cli(evaluate)

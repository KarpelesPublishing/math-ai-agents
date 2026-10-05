"""Shared input/output for offline, constructed mathematical probes."""
from __future__ import annotations
import argparse
import json
import math
from pathlib import Path

def boolean(value):
    if type(value) is not bool:
        raise ValueError('authority and completion flags must be Boolean')
    return value

def nonnegative(value):
    if isinstance(value, bool):
        raise ValueError('finite nonnegative numeric value required')
    value = float(value)
    if not math.isfinite(value) or value < 0:
        raise ValueError('finite nonnegative numeric value required')
    return value

def positive_integer(value):
    if type(value) is not int or value < 1:
        raise ValueError('positive integer required')
    return value

def probability(value):
    value = nonnegative(value)
    if not 0 <= value <= 1:
        raise ValueError('probability must lie in [0, 1]')
    return value

def cli(evaluate):
    parser = argparse.ArgumentParser(description=evaluate.__doc__)
    parser.add_argument('--manifest', type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.manifest.read_text())
    print(json.dumps({'kind': 'constructed demonstration', 'result': evaluate(data)}, indent=2, allow_nan=False))

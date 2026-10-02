#!/usr/bin/env python3
"""Deterministic constructed document-release simulator."""
from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class Run:
    outcome: str
    authorized_completion: bool
    proposal: str
    actual_effect: str
    total_cost: int
    recovery_time: int
    remaining_budget: int
    fault_log: tuple[str, ...]


def belief_after(observation: str) -> str:
    """Small declared belief update used only by constructed tests."""
    return {"signed_approval": "approved", "document_changed": "stale", "dropped_ack": "unknown"}[observation]


def release_with(*, version: str, approval_for: str, fault: str | None = None, policy: str = "fixed", seed: int = 0) -> Run:
    """Run one declared release policy; seed is recorded, not inferred."""
    proposal = f"release:{version}"
    faults = tuple(x for x in (fault,) if x)
    budget = 10
    if fault in {"private_data", "malicious_instruction", "stale_memory", "invalid_evidence"}:
        return Run("abstained", False, proposal, "none", 0, 0, budget, faults)
    if fault == "document_changed":
        return Run("abstained", False, proposal, "restart_required", 2, 0, budget - 2, faults)
    if approval_for != version:
        return Run("abstained", False, proposal, "none", 2, 0, budget - 2, faults)
    if fault == "duplicate_request":
        return Run("duplicate_effect", False, proposal, f"released:{version}:twice", 8, 0, budget - 8, faults)
    if fault == "late_cancellation":
        return Run("recovered", False, proposal, f"released:{version};rolled_back", 6, 1, budget - 6, faults)
    if fault == "dropped_acknowledgement":
        return Run("abstained", False, proposal, "pending", 2, 0, budget - 2, faults)
    if fault == "review_delay":
        return Run("deadline_miss", False, proposal, "none", 2, 0, budget - 2, faults)
    if policy not in {"fixed", "trained"}:
        raise ValueError("policy must be fixed or trained")
    return Run("authorized_release", True, proposal, f"released:{version}", 5, 0, budget - 5, faults)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text())
    runs = [asdict(release_with(**case)) for case in manifest["runs"]]
    print(json.dumps({"seed": manifest["seed"], "runs": runs}, indent=2))


if __name__ == "__main__":
    main()

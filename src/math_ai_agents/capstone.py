"""One fictitious release process with matched baseline and guarded runs."""
from __future__ import annotations
from collections import Counter
import math
import random
from .core import analyze

DEFAULTS = {
    "seed": 41, "runs": 300, "step_success": 0.98, "steps": 10,
    "shared_failure": 0.04, "stale_layout_probability": 0.20,
    "injection_probability": 0.10, "dropped_ack_probability": 0.15,
    "approved_probability": 0.85, "review_available_probability": 0.70,
    "review_delay": 2.0, "deadline": 6.0, "budget": 8.0,
    "verification_cost": 1.0, "review_cost": 1.0,
}


def simulate(data=None):
    d = dict(DEFAULTS if data is None else data)
    missing = set(DEFAULTS) - set(d)
    if missing:
        raise ValueError("Missing capstone fields: " + ", ".join(sorted(missing)))
    for key in ("runs", "steps"):
        if type(d[key]) is not int or not 1 <= d[key] <= 10000:
            raise ValueError(key + " must be an integer between 1 and 10000.")
    if type(d["seed"]) is not int:
        raise ValueError("seed must be an integer.")
    for key in ("step_success", "shared_failure", "stale_layout_probability", "injection_probability", "dropped_ack_probability", "approved_probability", "review_available_probability"):
        if isinstance(d[key], bool) or not isinstance(d[key], (int, float)) or not math.isfinite(d[key]) or not 0 <= d[key] <= 1:
            raise ValueError(key + " must be a probability in [0,1].")
    for key in ("review_delay", "deadline", "budget", "verification_cost", "review_cost"):
        if isinstance(d[key], bool) or not isinstance(d[key], (int, float)) or not math.isfinite(d[key]) or d[key] < 0:
            raise ValueError(key + " must be finite and nonnegative.")
    rng = random.Random(d["seed"])
    records, traces = [], []
    for trial in range(d["runs"]):
        # All environmental draws happen before either policy runs.
        world = {"shared_bad": rng.random() < d["shared_failure"],
                 "steps_ok": all(rng.random() < d["step_success"] for _ in range(d["steps"])),
                 "stale": rng.random() < d["stale_layout_probability"],
                 "injected": rng.random() < d["injection_probability"],
                 "ack_lost": rng.random() < d["dropped_ack_probability"],
                 "approved": rng.random() < d["approved_probability"],
                 "review_available": rng.random() < d["review_available_probability"]}
        for policy in ("baseline", "guarded"):
            guarded = policy == "guarded"
            time_used, cost, effects, confirmed, authorized, correct = 0.0, 0.0, 0, False, world["approved"], False
            trace = [{"stage": "contract", "target": "v2", "approval_current": authorized, "chapter": 22}]
            outcome = "not_attempted"

            def spend(amount, duration):
                nonlocal cost, time_used
                if cost + amount > d["budget"] or time_used + duration > d["deadline"]:
                    return False
                cost += amount; time_used += duration
                return True

            if world["shared_bad"] or not world["steps_ok"]:
                outcome = "preparation_failure"
            elif not spend(1.0, 1.0):
                outcome = "budget_or_deadline"
            elif guarded and world["injected"]:
                outcome = "untrusted_instruction_blocked"
                trace.append({"stage": "monitor", "decision": "block", "chapter": 23})
            else:
                target = "unapproved-v3" if (world["stale"] or world["injected"]) and not guarded else "v2"
                trace.append({"stage": "interface", "target": target, "refreshed": guarded, "chapter": 18})
                if guarded and not authorized:
                    trace.append({"stage": "handoff", "owner": "authorized local reviewer", "chapter": 27})
                    if not world["review_available"]:
                        outcome = "review_unavailable"
                    elif not spend(d["review_cost"], d["review_delay"]):
                        outcome = "review_timeout_or_budget"
                    else:
                        # This fictional reviewer has authority and approves v2.
                        authorized = True
                        trace.append({"stage": "approval", "version": "v2", "chapter": 22})
                if outcome == "not_attempted":
                    if not spend(1.0, 1.0):
                        outcome = "budget_or_deadline"
                    elif guarded and (target != "v2" or not authorized):
                        outcome = "permission_denied"
                    else:
                        effects = 1
                        correct = target == "v2"
                        trace.append({"stage": "effect", "target": target, "chapter": 17})
                        if not world["ack_lost"]:
                            confirmed = True
                            outcome = "confirmed"
                        elif guarded:
                            if spend(d["verification_cost"], 1.0):
                                confirmed = True
                                outcome = "verified_after_lost_ack"
                                trace.append({"stage": "verify", "observed_effect": True, "chapter": 17})
                            else:
                                outcome = "pending_effect"
                        else:
                            if spend(1.0, 1.0):
                                effects += 1
                                confirmed = True
                                outcome = "duplicate_effect"
                            else:
                                outcome = "pending_effect"
            success = bool(effects == 1 and correct and authorized and confirmed)
            unauthorized = bool(effects and (not correct or not authorized))
            record = {"task": "constructed-release", "run": str(trial), "procedure": policy,
                      "success": success, "cost": cost, "exposed": False,
                      "unauthorized_effect": unauthorized, "effects": effects, "confirmed": confirmed,
                      "elapsed": time_used, "outcome": outcome}
            records.append(record)
            if trial < 5:
                traces.append({"run": trial, "policy": policy, "world": world, "trace": trace, "terminal": record})
    evaluation = analyze(24, {"records": records, "baseline": "baseline", "candidate": "guarded"})
    summaries = {}
    for policy in ("baseline", "guarded"):
        rows = [r for r in records if r["procedure"] == policy]
        summaries[policy] = {"runs": len(rows), "authorized_confirmed_completions": sum(r["success"] for r in rows),
                             "unauthorized_effects": sum(r["unauthorized_effect"] for r in rows),
                             "duplicate_effects": sum(max(0, r["effects"] - 1) for r in rows),
                             "mean_cost": sum(r["cost"] for r in rows) / len(rows),
                             "outcomes": dict(Counter(r["outcome"] for r in rows))}
    xs = list(range(1, d["steps"] + 1))
    return {"inputs": d, "evidence_kind": "constructed matched simulation; no deployed model or service measured",
            "metrics": summaries, "records": records, "sample_traces": traces, "evaluation": evaluation,
            "series": [{"label": "Independent preparation steps conditional on no shared failure", "x": xs,
                        "y": [d["step_success"] ** n for n in xs], "x_label": "Preparation steps", "y_label": "All-step success probability"},
                       {"label": "Authorized and confirmed terminal completion", "x": [0, 1],
                        "y": [summaries[p]["authorized_confirmed_completions"] / d["runs"] for p in ("baseline", "guarded")],
                        "x_label": "Policy index: 0 baseline, 1 guarded", "y_label": "Observed constructed-run fraction"}],
            "interpretation": "Baseline and guarded procedures face matched environmental draws. Guarding changes how those draws become actions, permissions, receipts and terminal outcomes.",
            "assumptions": ["Conditional independent preparation steps; one common-cause failure variable.", "Guard refresh is perfect and detects the modeled untrusted instruction.", "Verification observes the true effect.", "The available fictional reviewer has authority and always approves the intended v2."],
            "limitations": ["These choices are declared simulation laws, not learned models or deployment estimates.", "Policy comparisons include different guards, retrieval freshness and review paths; they do not isolate any single mechanism.", "The paired summary's sampling assumptions refer only to the constructed generator.", "Authority checks are executable rules here; a plotted zero does not certify a real service."]}

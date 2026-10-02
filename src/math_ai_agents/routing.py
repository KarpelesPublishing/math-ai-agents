"""Routing suggestions are inspectable; chapter execution stays explicit."""
from __future__ import annotations

import re
from .core import available_chapters, chapter_content, analyze

WORKFLOWS = {
    "reliability": [5, 17, 24],
    "compute-budget": [6, 16, 27],
    "memory-improvement": [2, 15, 24, 25],
    "safe-release": [4, 17, 18, 22, 23, 27],
}

ALIASES = {
    1: ["score jump", "thresholded score", "thresholding", "measurement cliff"],
    2: ["ablation", "four-cell", "four cell", "interaction contrast"],
    3: ["forecast", "prediction leakage", "predict emergence", "held-out forecast"],
    4: ["reachability", "permission graph", "reachable action", "missing bridge"],
    5: ["trajectory", "step success", "composite kernel", "frozen model", "long-run reliability"],
    6: ["utility", "utilities", "stakes", "abstain", "abstention", "compare actions", "value a decision"],
    7: ["bellman", "finite horizon", "future value", "dynamic programming", "backward induction"],
    8: ["belief update", "bayes", "partial observation", "aliased observation", "belief state"],
    9: ["a*", "astar", "admissible heuristic", "search frontier", "shortest path"],
    10: ["option duration", "hierarchical action", "skill termination", "interrupt a skill", "variable-duration"],
    11: ["bandit", "ucb", "thompson", "regret", "exploration"],
    12: ["temporal difference", "td update", "eligibility trace", "credit assignment", "monte carlo return"],
    13: ["reinforce", "policy gradient", "reward shaping", "train a policy", "verifier reward"],
    14: ["model error", "transition error", "world model", "simulation bound", "total variation"],
    15: ["retrieval", "memory compression", "stale memory", "memory budget", "retention"],
    16: ["selector", "candidate allocation", "sampling budget", "compute allocation", "best-of"],
    17: ["lost acknowledgement", "lost acknowledgment", "lost receipt", "lost reply", "dropped ack", "retry", "idempotence", "idempotency", "verify an effect"],
    18: ["coordinate", "screenshot", "button moved", "observation freshness", "screen layout"],
    19: ["cross-play", "cross play", "partner transfer", "self-play", "counterparty"],
    20: ["consensus", "common knowledge", "message drop", "handoff receipt", "acknowledgement protocol"],
    21: ["braess", "congestion", "toll", "institution", "routing incentives"],
    22: ["risk constraint", "hard authorization", "safety penalty", "operating envelope", "risk contract"],
    23: ["prompt injection", "untrusted instruction", "capability monitor", "data control", "malicious source"],
    24: ["matched comparison", "paired runs", "paired task-run", "matched task", "paired task", "confidence interval", "success rate", "task mixture", "exposure bias"],
    25: ["guard contamination", "development guard", "improvement acceptance", "reused holdout", "accept a candidate"],
    26: ["oracle coverage", "candidate bank", "conditional ceiling", "saturation forecast", "deployment filter"],
    27: ["delegation", "review deadline", "human review", "review queue", "reviewer unavailable", "handoff utility"],
}


# Single words common in everyday speech; alone they do not justify a method suggestion.
WEAK_PHRASES = {"forecast", "coordinate", "utility", "utilities", "stakes", "toll", "institution", "retention", "retrieval", "consensus", "delegation", "trajectory", "abstain"}


def suggest(request: str) -> dict:
    if not isinstance(request, str) or not request.strip():
        raise ValueError("Describe a mathematical question or choose a chapter.")
    query = request.lower()
    if "trust" in query and "memory" in query and not any(p in query for p in ("stale", "compression", "retrieval", "approval")):
        return {"status": "ambiguous", "chapters": [15, 23, 24, 27],
                "reason": "Trust may refer to freshness/authority, adversarial data, measured effectiveness or reviewer authority. Ask which result is needed."}
    explicit = [int(n) for n in re.findall(r"\bchapter\s+(\d+)\b", query)]
    if explicit:
        if any(n not in available_chapters() for n in explicit):
            return {"status": "unsupported", "chapters": [], "reason": "That chapter is absent from this book."}
        return {"status": "ready", "chapters": list(dict.fromkeys(explicit)), "reason": "Explicit chapter request."}
    for name, chapters in WORKFLOWS.items():
        if name.replace("-", " ") in query or name in query:
            return {"status": "workflow", "workflow": name, "chapters": chapters,
                    "reason": "Named workflow; each method still needs compatible declared inputs."}
    ranked = []
    for chapter in available_chapters():
        content = chapter_content(chapter)
        phrases = list(dict.fromkeys(content.get("routes", []) + ALIASES.get(chapter, [])))
        matches = [p for p in phrases if re.search(r"(?<!\w)" + re.escape(p.lower()) + r"(?!\w)", query)]
        if matches:
            ranked.append((sum(len(p.split()) + 1 for p in matches), chapter, matches))
    ranked.sort(key=lambda r: (-r[0], r[1]))
    if not ranked:
        return {"status": "needs-context", "chapters": [],
                "reason": "No reliable phrase match. The master skill should choose by the mathematical task, or ask which outcome you need."}
    if ranked[0][0] <= 2 and set(ranked[0][2]) <= WEAK_PHRASES:
        # A lone generic word (for example "forecast" in a weather question) is not evidence of fit.
        return {"status": "weak-match", "chapters": [r[1] for r in ranked[:3]],
                "reason": "Only a single generic word matched. Treat this as low confidence; ask which mathematical outcome is needed before running a method.",
                "matches": [{"chapter": r[1], "phrases": r[2]} for r in ranked[:3]]}
    tied = len(ranked) > 1 and ranked[0][0] == ranked[1][0]
    return {"status": "ambiguous" if tied else "suggestion", "chapters": [r[1] for r in ranked[:3]],
            "reason": "Phrase-based suggestions; the assistant must verify the intended estimand and input contract.",
            "matches": [{"chapter": r[1], "phrases": r[2]} for r in ranked[:3]]}


def workflow(name: str, inputs: dict | None = None) -> dict:
    if name not in WORKFLOWS:
        raise ValueError("Choose reliability, compute-budget, memory-improvement or safe-release.")
    if inputs is not None and not isinstance(inputs, dict):
        raise ValueError("Workflow inputs must map chapter numbers to complete chapter JSON objects.")
    reports = []
    for chapter in WORKFLOWS[name]:
        if inputs is not None and str(chapter) not in inputs:
            raise ValueError(f"Missing inputs for Chapter {chapter}. No example is silently substituted.")
        reports.append(analyze(chapter, None if inputs is None else inputs[str(chapter)]))
    return {"workflow": name, "mode": "constructed demonstrations" if inputs is None else "supplied chapter inputs",
            "reports": reports,
            "composition_boundary": "Methods are reported separately. Their outputs are not interchangeable scores or a joint causal estimate. Check task, units, population, budget and authority before using them together."}

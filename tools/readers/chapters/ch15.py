"""Chapter 15 reader: What an Agent Should Remember.

Four demonstrations built on Equation (15.1), the chapter's budgeted retrieval
rule, and on the chapter's inline results (8 - 2 = 6, the 2 epsilon regret
bound, and the Exercise 1 value 0.6 x 8 + 0.4 x 0 = 4.8).

D01  Equation (15.1) with the freshness and version checks of the laboratory's
     memory-budget function (math_ai_agents.chapters.ch15.evaluate): the chapter
     example and the laboratory's default, changed and transfer cases.
D02  The 2 epsilon regret bound, its premise, the laboratory's default and
     changed compression cases, and a summary that dropped a revocation.
D03  Stale approval under three retrieval policies, with deletion that reaches
     only some views and the two reports (recall and decision).
D04  Exercise 1: a record that may no longer be current, priced in tokens.

Every number is a constructed teaching value.
"""
import itertools
import math

from math_ai_agents.chapters.ch15 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

EQ_RETRIEVAL = (
    r"R^\star\in\arg\max_{R:\,\sum_{m\in R}c(m)\le B}"
    r"\left\{\operatorname E[\text{decision value}\mid R]-\lambda\sum_{m\in R}c(m)\right\}"
)
EQ_REGRET = r"2\varepsilon"
EQ_EXERCISE = r"0.6\times 8+0.4\times 0=4.8"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


def g(x):
    """Compact number for prose: 1.0 -> 1, 1.5 -> 1.5."""
    return f"{float(x):g}"


# ---------------------------------------------------------------------------
# Demonstration 1: Equation (15.1), records chosen under a budget
# ---------------------------------------------------------------------------

# Each record: (name, tokens, decision value, timestamp, ttl, authority flag, version).
# The chapter example: the revocation (2 tokens, value 8) and the irrelevant note (2 tokens, value 0)
# are the book's; the old approval has value 0 because a superseded approval cannot support a present
# release, and the thread summary (value 3) is defined for this reader.
LAB_RECORDS = [
    ("review-v2", 4, 8.0, 9, 3, True, "v2"),
    ("summary", 2, 3.0, 8, 5, False, "v1"),
    ("old-review", 1, 100.0, 9, 3, True, "v1"),
]
CASES = {
    "chapter": {
        "heading": "Chapter example", "budget": 2, "now": 10, "version": "v2",
        "records": [
            ("Current revocation", 2, 8.0, 9, 3, True, "v2"),
            ("Thread summary", 2, 3.0, 8, 5, False, "v2"),
            ("Old approval", 2, 0.0, 9, 3, True, "v1"),
            ("Irrelevant note", 2, 0.0, 9, 3, False, "v2"),
        ],
    },
    "default": {"heading": "Default case", "budget": 6, "now": 10, "version": "v2", "records": LAB_RECORDS},
    "changed": {"heading": "Changed case (budget 2)", "budget": 2, "now": 10, "version": "v2", "records": LAB_RECORDS},
    "transfer": {
        "heading": "Transfer case", "budget": 3, "now": 20, "version": "doc-C",
        "records": [
            ("expired", 1, 10.0, 10, 2, False, "doc-C"),
            ("current", 3, 4.0, 19, 3, True, "doc-C"),
        ],
    },
}


def eligibility(case, rec):
    """Freshness and version-bound authority, the two checks the laboratory applies before any value is counted."""
    name, tokens, value, stamp, ttl, authority, version = rec
    age = case["now"] - stamp
    if age > ttl:
        return f"excluded: expired (age {age} > ttl {ttl})"
    if authority and version != case["version"]:
        return f"excluded: stale authority ({version}, current {case['version']})"
    return None


def best_sets(case, lam):
    """All subsets of the eligible records that maximize total net value within the budget (direct enumeration)."""
    eligible = [r for r in case["records"] if eligibility(case, r) is None]
    scored = []
    for mask in range(1 << len(eligible)):
        subset = [eligible[i] for i in range(len(eligible)) if mask >> i & 1]
        tokens = sum(r[1] for r in subset)
        if tokens > case["budget"]:
            continue
        scored.append((sum(r[2] - lam * r[1] for r in subset), tuple(r[0] for r in subset), tokens))
    top = max(s[0] for s in scored)
    winners = [s for s in scored if abs(s[0] - top) <= 1e-9]
    winners.sort(key=lambda s: (len(s[1]), s[2], s[1]))
    return top, winners


def lab_retrieval(case, lam):
    """The laboratory's exact selection, fed the net values."""
    records = [{"id": r[0], "tokens": r[1], "decision_value": max(r[2] - lam * r[1], 0.0), "timestamp": r[3],
                "ttl": r[4], "authority": r[5], "version": r[6]} for r in case["records"]]
    out = evaluate({"budget": case["budget"], "now": case["now"], "current_version": case["version"], "records": records,
                    "original_action_values": [1, 0], "compressed_action_values": [1, 0]})
    return out["metrics"]["retrieval_value"], out["metrics"]["excluded_ids"], out["metrics"]["retrieved_ids"]


def budget_picture(case="chapter", lam=1):
    c = CASES[case]
    lam = float(lam)
    budget = c["budget"]
    records = c["records"]
    top, winners = best_sets(c, lam)
    lab_value, lab_excluded, lab_ids = lab_retrieval(c, lam)
    excluded = [r[0] for r in records if eligibility(c, r)]
    if not math.isclose(lab_value, max(top, 0.0), abs_tol=1e-9) or lab_excluded != excluded:
        raise AssertionError("laboratory selection disagrees with direct enumeration of Equation (15.1)")
    chosen_names = set(winners[0][1])
    tie = len(winners) > 1
    nets = {r[0]: r[2] - lam * r[1] for r in records}

    fig, ax = new_figure(height=4.3)
    ys = list(range(len(records)))[::-1]
    for y, rec in zip(ys, records):
        name, tokens, value = rec[0], rec[1], rec[2]
        reason = eligibility(c, rec)
        net = nets[name]
        if reason:
            ax.barh(y, 0, height=0.56, color="white")
            ax.plot([0], [y], "|", color=PALETTE["grey"], markersize=22, markeredgewidth=3)
            ax.text(0.4, y, reason, va="center", ha="left", fontsize=10.5, color=PALETTE["terracotta"])
            continue
        if name in chosen_names:
            ax.barh(y, net, height=0.56, color=PALETTE["teal"])
            note = "chosen"
        else:
            ax.barh(y, net, height=0.56, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1)
            if any(name in w[1] for w in winners):
                note = "tie, optional"
            elif abs(net) <= 1e-9:
                note = "left out: adds 0"
            elif net > 0:
                note = "left out: no room"
            else:
                note = "left out"
        if abs(net) <= 1e-9:
            ax.plot([0], [y], "|", color=PALETTE["grey"], markersize=22, markeredgewidth=3)
        ax.text(max(net, 0) + 0.3, y, f"{fmt(net, 1)} {note}", va="center", ha="left", fontsize=10.5, color=PALETTE["ink"])
    ax.axvline(0, color=PALETTE["ink"], linewidth=1)
    ax.set_yticks(ys, [f"{r[0]}\n({r[1]} token{'s' if r[1] != 1 else ''}, value {g(r[2])})" for r in records])
    elig_nets = [nets[r[0]] for r in records if not eligibility(c, r)]
    lowest = min(min(elig_nets), 0)
    highest = max(elig_nets)
    ax.set_xlim(min(-2.5, lowest - 1.5), max(14, highest + 6))
    ax.set_ylim(-0.6, len(records) - 0.4)
    ax.set_xlabel("Net value = decision value - \u03bb x tokens (constructed units)")
    ax.set_ylabel("Record")
    ax.set_title(f"{c['heading']}: B = {budget} tokens, \u03bb = {g(lam)} per token", fontsize=11.5)
    ax.grid(axis="y", alpha=0)

    used = winners[0][2]
    shown = ", ".join(winners[0][1]) if winners[0][1] else "no record"
    metrics = {
        "Chosen by Equation (15.1)": shown + (" (tie)" if tie else ""),
        "Total net value": fmt(top, 1),
        "Tokens used": f"{used} of {budget}",
        "Excluded before scoring": ", ".join(excluded) if excluded else "none",
        "Best sets": str(len(winners)),
    }
    parts = []
    for rec in records:
        if eligibility(c, rec):
            parts.append(f"{rec[0]} {eligibility(c, rec)}")
        else:
            parts.append(f"{rec[0]} {g(rec[2])} - {g(lam)} x {rec[1]} = {fmt(nets[rec[0]], 1)}")
    sums = "Net value = decision value - lambda x tokens. " + "; ".join(parts) + "."
    if tie:
        sets = ["{" + ", ".join(w[1]) + "}" if w[1] else "{nothing}" for w in winners]
        options = f"{sets[0]} and {sets[1]} both" if len(sets) == 2 else " or ".join(sets) + " all"
        verdict = (f"A record with net value exactly 0 changes nothing, so {options} total {fmt(top, 1)}. "
                   "Equation (15.1) returns every one of them as a maximizer and does not choose; "
                   "a stated rule such as fewest tokens does. The figure shows the smallest set.")
    elif winners[0][1]:
        verdict = f"Equation (15.1) keeps {shown}, for a total of {fmt(top, 1)} using {used} of {budget} tokens."
    else:
        too_big = [r for r in records if not eligibility(c, r) and nets[r[0]] >= -1e-9 and r[1] > budget]
        fits = [r for r in records if not eligibility(c, r) and r[1] <= budget]
        if too_big:
            big = " and ".join(f"{r[0]} ({r[1]} token{'s' if r[1] != 1 else ''})" for r in too_big)
            if len(fits) == 1:
                rest = f"{fits[0][0]}, the only record that fits, has negative net value"
            elif fits:
                rest = "every record that fits has negative net value"
            else:
                rest = "no other eligible record fits"
            verdict = (f"{big} {'does' if len(too_big) == 1 else 'do'} not fit the budget of {budget}, and {rest}, "
                       "so Equation (15.1) keeps nothing.")
        else:
            verdict = "Every eligible record costs more than it is worth, so Equation (15.1) keeps nothing."
    extra = ""
    if not tie:
        skipped = [r[0] for r in records if not eligibility(c, r) and nets[r[0]] > 1e-9 and r[0] not in chosen_names]
        if skipped:
            extra = f" {skipped[0]} has net value {fmt(nets[skipped[0]], 1)} but would push the total past the budget."
    stale = [r for r in records if eligibility(c, r) and r[2] > 0]
    if stale:
        s0 = stale[0]
        extra += (f" {s0[0]} is excluded although its declared value is {g(s0[2])}"
                  + (" and its timestamp is fresh" if c["now"] - s0[3] <= s0[4] else "")
                  + ": a high value cannot buy back an expired or superseded record.")
    interpretation = f"{c['heading']}. {sums} {verdict}{extra}"
    steps = [
        f"Check each record first: it must be fresh (age at most ttl) and any authority record must match version {c['version']}.",
        ("Excluded: " + "; ".join(f"{r[0]} ({eligibility(c, r)[10:]})" for r in records if eligibility(c, r)) + ".") if excluded
        else "No record is excluded by freshness or version.",
        "Net values: " + "; ".join(f"{r[0]} {g(r[2])} - {g(lam)} x {r[1]} = {fmt(nets[r[0]], 1)}" for r in records if not eligibility(c, r)) + ".",
        f"Best set within {budget} tokens: {shown}, total {fmt(top, 1)}, {used} tokens.",
    ]
    alt = (f"{c['heading']}. Horizontal bars of net value for {len(records)} records at budget {budget} and lambda {g(lam)}; "
           f"chosen: {shown}; excluded before scoring: {', '.join(excluded) if excluded else 'none'}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# ---------------------------------------------------------------------------
# Demonstration 2: compression and the 2 epsilon bound
# ---------------------------------------------------------------------------

UNAUTHORIZED = -50.0   # true value of releasing after a revocation (constructed)

SUMMARIES = {
    "worst": {"actions": ["Release", "Ask owner", "Abstain"], "full": [10.0, 6.0, 3.0], "heading": "Errors placed against the best action"},
    "dropped": {"actions": ["Release", "Ask owner", "Abstain"], "full": [UNAUTHORIZED, 6.0, 3.0], "approx": [10.0, 6.0, 3.0],
                "heading": "Summary dropped the revocation"},
    "default": {"actions": ["Action 0", "Action 1"], "full": [4.0, 6.0], "approx": [3.0, 5.0], "heading": "Default case"},
    "changed": {"actions": ["Action 0", "Action 1"], "full": [4.0, 6.0], "approx": [6.0, 5.0], "heading": "Changed case"},
}


def lab_preserved(full, summary):
    out = evaluate({"budget": 1, "now": 1, "current_version": "v", "records": [
        {"id": "r", "tokens": 1, "decision_value": 0, "timestamp": 0, "ttl": 1, "authority": False, "version": "v"}],
        "original_action_values": list(full), "compressed_action_values": list(summary)})
    return out["metrics"]["compression_preserves_action"]


def compression_picture(epsilon=1, summary="worst"):
    eps = float(epsilon)
    sc = SUMMARIES[summary]
    actions = sc["actions"]
    full = list(sc["full"])
    if summary == "worst":
        approx = [full[0] - eps, full[1] + eps, full[2]]
    else:
        approx = list(sc["approx"])
    same_actions = summary != "dropped"
    max_error = max(abs(a - f) for a, f in zip(approx, full))  # for the dropped summary, release is drawn as -50
    premise = same_actions and max_error <= eps + 1e-9
    best_full = max(full)
    top = max(approx)
    picks = [i for i, v in enumerate(approx) if abs(v - top) <= 1e-9]
    regrets = [best_full - full[i] for i in picks]
    tie = len(picks) > 1
    limit = 2 * eps
    if not tie and lab_preserved(full, approx) != (picks[0] == full.index(best_full)):
        raise AssertionError("laboratory action check disagrees with the direct comparison")

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    x = list(range(len(actions)))
    w = 0.38
    left.bar([i - w / 2 for i in x], full, w, color=PALETTE["navy"])
    left.bar([i + w / 2 for i in x], approx, w, color="white", edgecolor=PALETTE["teal"], hatch="///", linewidth=1.2)
    for i in x:
        left.text(i - w / 2, full[i] + (0.8 if full[i] >= 0 else -0.8), fmt(full[i], 1), ha="center",
                  va="bottom" if full[i] >= 0 else "top", fontsize=10.5, color=PALETTE["navy"])
        left.text(i + w / 2, approx[i] + (0.8 if approx[i] >= 0 else -0.8), fmt(approx[i], 1), ha="center",
                  va="bottom" if approx[i] >= 0 else "top", fontsize=10.5, color=PALETTE["teal"])
    left.axhline(0, color=PALETTE["ink"], linewidth=1)
    left.set_xticks(x, actions)
    left.set_ylim(-62 if summary == "dropped" else -4, 17)
    left.set_xlabel("Action (dark: full history, hatched: summary)")
    left.set_ylabel("Estimated value of the action")
    left.set_title(sc["heading"], fontsize=11.5)
    left.grid(axis="x", alpha=0)

    reg_show = max(regrets)
    right.barh([1], [reg_show], height=0.5, color=PALETTE["terracotta"])
    right.barh([0], [limit], height=0.5, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.2)
    top_x = max(reg_show, limit) + 0.001
    right.set_xlim(0, max(top_x * 1.3, 7.0) + (0 if summary != "dropped" else 6))
    right.set_yticks([1, 0], ["Regret of\nsummary action", "Limit 2\u03b5"])
    right.set_ylim(-0.6, 1.6)
    for yv, val, nm in ((1, reg_show, "regret"), (0, limit, "limit")):
        txt = fmt(val, 1) if not (nm == "regret" and tie) else f"0.0 or {fmt(reg_show, 1)} (tie)"
        right.text(val + 0.15 * (right.get_xlim()[1] / 10), yv, txt, va="center", ha="left", fontsize=10.5, color=PALETTE["ink"])
    right.set_xlabel("Value lost by following the summary")
    right.set_ylabel("Quantity")
    if not same_actions:
        title = f"\u03b5 = {g(eps)}: premise fails (action sets differ)"
    elif premise:
        title = f"\u03b5 = {g(eps)}: every error is at most \u03b5"
    else:
        title = f"\u03b5 = {g(eps)}: premise fails (error {fmt(max_error, 1)} > \u03b5)"
    right.set_title(title, fontsize=11.5)
    right.grid(axis="y", alpha=0)

    names = [actions[i] for i in picks]
    chosen = " or ".join(names) + (" (tie)" if tie else "")
    regret_text = f"0.0 or {fmt(reg_show, 1)}" if tie else fmt(regrets[0], 1)
    if not same_actions:
        claim = "does not apply (action sets differ)"
    elif not premise:
        claim = f"does not apply (error {fmt(max_error, 1)} exceeds epsilon)"
    else:
        claim = "holds: regret within the limit" if reg_show <= limit + 1e-9 else "violated"
    metrics = {
        "Largest error of the summary": fmt(max_error, 1),
        "Claimed epsilon": g(eps),
        "Summary follows": chosen,
        "Regret of that action": regret_text,
        "Limit 2\u03b5": fmt(limit, 1),
        "2\u03b5 claim": claim,
    }
    if summary == "worst":
        s0, s1 = approx[0], approx[1]
        calc = (f"Summary scores: release {fmt(full[0], 0)} - {g(eps)} = {fmt(s0, 1)}, ask owner "
                f"{fmt(full[1], 0)} + {g(eps)} = {fmt(s1, 1)}, abstain {fmt(full[2], 0)}.")
        if tie:
            tail = (f" The two top scores tie, so the summary may follow either one. If it follows ask owner, regret = "
                    f"{fmt(best_full, 0)} - {fmt(full[1], 0)} = {fmt(reg_show, 1)}, which equals the limit 2 x {g(eps)} = "
                    f"{fmt(limit, 1)}: the bound can be reached.")
        elif regrets[0] > 1e-9:
            tail = (f" It follows ask owner, so regret = {fmt(best_full, 0)} - {fmt(full[1], 0)} = {fmt(regrets[0], 1)}, "
                    f"within the limit 2 x {g(eps)} = {fmt(limit, 1)}.")
        else:
            tail = (f" It still follows release, so regret = {fmt(best_full, 0)} - {fmt(best_full, 0)} = {fmt(0, 1)}, "
                    f"far inside the limit 2 x {g(eps)} = {fmt(limit, 1)}.")
        interpretation = (calc + tail + " Every error here is at most epsilon on actions both versions list, which is what "
                          "the bound requires.")
    elif summary == "dropped":
        interpretation = (f"The full history holds a revocation, so releasing now is not permitted; this reader draws that as a "
                          f"value of {fmt(UNAUTHORIZED, 0)}, a loss of {fmt(-UNAUTHORIZED, 0)}. The summary "
                          f"kept only the old approval and still scores release at {fmt(10, 0)}, an error of "
                          f"{fmt(10, 0)} - ({fmt(UNAUTHORIZED, 0)}) = {fmt(10 - UNAUTHORIZED, 0)}, far above "
                          f"epsilon = {g(eps)}. It follows release, so regret = {fmt(best_full, 0)} - ({fmt(UNAUTHORIZED, 0)}) = "
                          f"{fmt(regrets[0], 0)}. The two versions disagree about which actions are permitted, so no 2 epsilon "
                          f"claim applies: the bound needs every error on shared actions to be at most epsilon, and release is not "
                          f"a permitted action in the full history. Changing epsilon moves only the limit bar here; the error "
                          f"{fmt(10 - UNAUTHORIZED, 0)} and the regret {fmt(regrets[0], 0)} stay the same. "
                          "The remedy is to query current authority or abstain.")
    else:
        e0 = abs(approx[0] - full[0])
        e1 = abs(approx[1] - full[1])
        err_text = (f"Errors: |{fmt(approx[0], 0)} - {fmt(full[0], 0)}| = {fmt(e0, 0)} and |{fmt(approx[1], 0)} - {fmt(full[1], 0)}| = {fmt(e1, 0)}, "
                    f"so the largest error is {fmt(max_error, 0)}.")
        if regrets[0] <= 1e-9:
            follow = (f" Both versions prefer Action 1, so regret = {fmt(best_full, 0)} - {fmt(best_full, 0)} = {fmt(0, 1)} and the action is preserved.")
        else:
            follow = (f" The summary now prefers Action 0 ({fmt(approx[0], 0)} > {fmt(approx[1], 0)}), so regret = {fmt(best_full, 0)} - {fmt(full[0], 0)} = "
                      f"{fmt(regrets[0], 1)}, the action is not preserved.")
        if premise:
            judge = (f" With epsilon {g(eps)} the premise holds, and regret {fmt(reg_show, 1)} is within 2 x {g(eps)} = {fmt(limit, 1)}.")
        else:
            judge = (f" With epsilon {g(eps)} the premise fails (error {fmt(max_error, 0)} > {g(eps)}), so the 2 epsilon claim is silent even "
                     f"though the numbers here happen to give regret {fmt(reg_show, 1)} against 2 x {g(eps)} = {fmt(limit, 1)}.")
        interpretation = (err_text + follow + judge + " That flag concerns this supplied comparison; it does not show that every future task "
                          "is preserved.")
    steps = [
        "Full-history values: " + ", ".join(f"{a} {fmt(v, 0)}" for a, v in zip(actions, full)) + ".",
        "Summary values: " + ", ".join(f"{a} {fmt(v, 1)}" for a, v in zip(actions, approx)) + ".",
        (f"Largest error on shared actions: {fmt(max_error, 1)}; claimed epsilon {g(eps)}; premise {'holds' if premise else 'fails'}."
         if same_actions else f"The error drawn for release is {fmt(max_error, 0)}, but the two versions list different permitted actions, so the premise fails."),
        f"The summary follows {chosen}.",
        f"Regret = best full value {fmt(best_full, 0)} minus the full value of that action = {regret_text}.",
        f"Limit 2 x {g(eps)} = {fmt(limit, 1)}; claim: {claim}.",
    ]
    alt = (f"{sc['heading']}. Left, bars of full-history and summary values for {len(actions)} actions. Right, the regret of the "
           f"summary's action, {regret_text}, against the limit 2 epsilon, {fmt(limit, 1)}, with epsilon {g(eps)}; the claim {claim}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# ---------------------------------------------------------------------------
# Demonstration 3: stale approval under three retrieval policies
# ---------------------------------------------------------------------------

VALUE = {"approval": 0.0, "note": 0.0, "revocation": 8.0}
TOKENS = 2
LAMBDA = 1.0
SLOT_MARKERS = {"Recency only": ("o", PALETTE["navy"]), "Similarity only": ("s", PALETTE["terracotta"]),
                "Decision aware": ("D", PALETTE["teal"])}
COLUMN_LABELS = {
    "none": "Old approval\n(in the store)",
    "store": "Old approval\n(copy kept in\nsummary index)",
    "all": "Old approval\n(deleted from\nevery view)",
}
SIMILARITY = {"approval": 0.98, "note": 0.80}


def outcome_of(kind):
    return {
        "approval": "Unauthorized release",
        "revocation": "Release blocked (correct)",
        "note": "Irrelevant recollection",
        None: "Abstain (correct)",
    }[kind]


def stale_picture(revocation_similarity=0.72, authority="reachable", deletion="none"):
    reachable = authority == "reachable"
    present = {"approval": deletion != "all", "note": True, "revocation": reachable}
    order = ["approval", "note", "revocation"]   # oldest to newest
    sim = {"approval": SIMILARITY["approval"], "note": SIMILARITY["note"], "revocation": float(revocation_similarity)}
    available = [k for k in order if present[k]]
    recency = available[-1]
    similarity = max(available, key=lambda k: sim[k])
    nets = {k: VALUE[k] - LAMBDA * TOKENS for k in available}
    best = max(nets.values())
    decision = max(nets, key=nets.get) if best > 1e-9 else None
    lab_value, _ = lab_retrieval_value_one(nets)
    if not math.isclose(lab_value, max(best, 0.0), abs_tol=1e-9):
        raise AssertionError("laboratory selection disagrees with the net values")
    picks = {"Recency only": recency, "Similarity only": similarity, "Decision aware": decision}

    fig, ax = new_figure(height=4.6)
    columns = order + [None]
    col_x = {k: i for i, k in enumerate(columns)}
    if deletion == "all":
        ax.axvspan(-0.38, 0.38, facecolor="#eef1f2", edgecolor=PALETTE["light"], hatch="///", linewidth=0)
    if not reachable:
        ax.axvspan(1.62, 2.38, facecolor="#eef1f2", edgecolor=PALETTE["light"], hatch="///", linewidth=0)
        ax.text(2, 2.62, "not reachable", ha="center", va="center", fontsize=10.5, color=PALETTE["grey"])
    rows = {"Recency only": 2, "Similarity only": 1, "Decision aware": 0}
    for policy, kind in picks.items():
        marker, color = SLOT_MARKERS[policy]
        xx, yy = col_x[kind], rows[policy]
        ax.plot([xx], [yy], marker, color=color, markersize=12, markeredgecolor=PALETTE["ink"])
        ax.annotate(outcome_of(kind).replace(" (correct)", "\n(correct)").replace("Unauthorized ", "Unauthorized\n").replace("Irrelevant ", "Irrelevant\n"),
                    (xx, yy), xytext=(0, -16), textcoords="offset points", ha="center", va="top", fontsize=10.5, color=PALETTE["ink"])
    sim_text = {k: (fmt(sim[k], 2) if present[k] else ("deleted" if k == "approval" else "unreachable")) for k in order}
    # A missing record gets the bare word on its own line, so neighbouring tick labels cannot run together.
    sim_line = {k: (f"similarity {sim_text[k]}" if present[k] else sim_text[k]) for k in order}
    ax.set_xticks(range(4), [f"{COLUMN_LABELS[deletion]}\n{sim_line['approval']}",
                             f"Irrelevant\nnote\n{sim_line['note']}",
                             f"Current\nrevocation\n{sim_line['revocation']}", "No record\nretrieved"])
    ax.set_yticks([2, 1, 0], ["Recency only", "Similarity only", "Decision aware"])
    ax.set_xlim(-0.75, 3.75)
    ax.set_ylim(-0.95, 2.85)
    ax.set_xlabel("Record, oldest to newest (room for one record)")
    ax.set_ylabel("Retrieval policy")
    ax.set_title("What each policy retrieves, and what follows", fontsize=11.5)

    metrics = {
        "Recency only": f"{outcome_of(recency)}",
        "Similarity only": f"{outcome_of(similarity)}",
        "Decision aware": outcome_of(decision),
    }
    rank = sorted(available, key=lambda k: -sim[k])
    names = {"approval": "old approval" if deletion == "none" else "old approval (index copy)", "note": "note", "revocation": "revocation"}
    nets_text = "; ".join(f"{names[k]} {g(VALUE[k])} - {g(LAMBDA)} x {TOKENS} = {signed(VALUE[k] - LAMBDA * TOKENS, 1)}" for k in order if present[k])
    top_pair = (f"{fmt(sim[rank[0]], 2)} > {fmt(sim[rank[1]], 2)}" if len(rank) > 1
                else f"{fmt(sim[rank[0]], 2)}, the only candidate left")
    recall_ok = {"approval": "accurate when it was written", "revocation": "accurate and current", "note": "irrelevant to the request"}
    ledger = (f"Two reports for Similarity only: the recall report says the retrieved {names[similarity]} is {recall_ok[similarity]}; "
              f"the decision report says: {outcome_of(similarity).lower()}.")
    if reachable:
        tail = (f"Decision aware retrieves the revocation, the only record with positive net value, and blocks the release. "
                f"Similarity only follows the highest score ({names[rank[0]]}, {top_pair}).")
    else:
        tail = (f"The revocation cannot be reached, so with these stipulated values no remaining record has positive net value "
                f"and Equation (15.1) keeps nothing. The chapter's rule for a controller that cannot query current authority is to "
                f"abstain instead of trusting stale wording. Similarity only follows the "
                f"highest score ({names[rank[0]]}, {top_pair}).")
    if deletion == "store":
        extra = (" The approval was deleted from the visible store, but a summary index still holds a copy with the same wording, so "
                 "absence from one view shows nothing about the others and the copy competes like the original.")
    elif deletion == "all":

        extra = (f" The approval was deleted from every view, so it cannot be retrieved; "
                 + ("the remaining policies now face only the note and the revocation" if reachable else "only the note is left to retrieve")
                 + ", and deletion did not replace the decision rule.")
    else:
        extra = ""
    interpretation = (f"Net value with lambda = 1 and 2 tokens per record: {nets_text}. {tail}{extra} Recency only retrieves the "
                      f"newest record it can reach, {names[recency]}. {ledger}")
    steps = [
        f"Candidates: " + ", ".join(f"{names[k]} (similarity {fmt(sim[k], 2)})" for k in available) + ".",
        f"Net values: {nets_text}.",
        f"Decision aware keeps the record with positive net value: {outcome_of(decision).lower()}.",
        f"Similarity only keeps the closest wording, {names[similarity]} ({fmt(sim[similarity], 2)}): {outcome_of(similarity).lower()}.",
        f"Recency only keeps the newest reachable record, {names[recency]}: {outcome_of(recency).lower()}.",
        ledger,
    ]
    alt = (f"A grid of three retrieval policies against four columns: the old approval ({COLUMN_LABELS[deletion].replace(chr(10), ' ')}), the note, "
           f"the revocation and no record. Recency only: {outcome_of(recency)}. Similarity only: {outcome_of(similarity)}. "
           f"Decision aware: {outcome_of(decision)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


def lab_retrieval_value_one(nets):
    records = [{"id": n, "tokens": TOKENS, "decision_value": max(v, 0.0), "timestamp": 9, "ttl": 3,
                "authority": False, "version": "v2"} for n, v in nets.items()]
    out = evaluate({"budget": TOKENS, "now": 10, "current_version": "v2", "records": records,
                    "original_action_values": [1, 0], "compressed_action_values": [1, 0]})
    return out["metrics"]["retrieval_value"], out["metrics"]["retrieved_ids"]


# ---------------------------------------------------------------------------
# Demonstration 4: a record that may no longer be current
# ---------------------------------------------------------------------------

RECORD_VALUE = 8.0   # Exercise 1: value if current, 0 if invalid
RECORD_TOKENS = 1


def lifecycle_picture(p_current=0.6, lam=1):
    p, lam = float(p_current), float(lam)
    expected = p * RECORD_VALUE + (1 - p) * 0.0
    cost = lam * RECORD_TOKENS
    net = expected - cost
    break_even = cost / RECORD_VALUE

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    bars = [expected, cost, net]
    colors = [PALETTE["teal"], "white", PALETTE["navy"] if net > 1e-9 else "white"]
    for i, (v, c) in enumerate(zip(bars, colors)):
        if c == "white":
            left.bar(i, v, 0.6, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.2)
        else:
            left.bar(i, v, 0.6, color=c)
        if abs(v) <= 1e-9:
            left.plot([i], [0], "_", color=PALETTE["grey"], markersize=46, markeredgewidth=3)
        left.text(i, v + (0.3 if v >= 0 else -0.3), fmt(v, 1), ha="center", va="bottom" if v >= 0 else "top",
                  fontsize=10.5, color=PALETTE["ink"])
    left.axhline(0, color=PALETTE["ink"], linewidth=1)
    left.set_xticks(range(3), ["Expected\nvalue", "Token\ncost", "Net\nvalue"])
    left.set_ylim(-4.8, 8.2)
    left.set_xlabel("Quantity (constructed units)")
    left.set_ylabel("Value of retrieving the record")
    left.set_title(f"p = {g(p)}, \u03bb = {g(lam)}", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    ps = [i / 50 for i in range(51)]
    for other, col in ((1.0, PALETTE["navy"]), (2.0, PALETTE["olive"]), (4.0, PALETTE["terracotta"])):
        selected = math.isclose(other, lam)
        right.plot(ps, [RECORD_VALUE * q - other * RECORD_TOKENS for q in ps], "-", color=col,
                   linewidth=2.6 if selected else 1.1, alpha=1 if selected else 0.55)
        label_point(right, 1.0, RECORD_VALUE - other * RECORD_TOKENS, f"\u03bb = {g(other)}", color=col, dx=-4, dy=5, ha="right")
    right.axhline(0, color=PALETTE["ink"], linewidth=1)
    right.axvline(break_even, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    right.plot([p], [net], "o", color=PALETTE["ink"], markersize=9, zorder=5)
    label_point(right, break_even, -4.1, f"break-even p = {fmt(break_even, 3)}", dx=5, dy=0, va="bottom").set_bbox(BOX)
    right.set_xlim(0, 1.02)
    right.set_ylim(-4.8, 8.2)
    right.set_xlabel("Probability p that the record is still current")
    right.set_ylabel("Net value of retrieving it")
    right.set_title("Retrieve when the line is above zero", fontsize=11.5)

    if abs(net) <= 1e-9:
        verdict = ("The net value is exactly 0: retrieving the record or leaving it out gives the same total, so "
                   "Equation (15.1) does not break this tie.")
        chosen = "tie"
    elif net > 0:
        verdict = f"The net value is positive, so the record is worth retrieving (p is above the break-even {fmt(break_even, 3)})."
        chosen = "Retrieve"
    else:
        verdict = f"The net value is negative, so leave the record out (p is below the break-even {fmt(break_even, 3)})."
        chosen = "Leave out"
    metrics = {
        "Expected value": fmt(expected, 2),
        "Token cost": fmt(cost, 2),
        "Net value": fmt(net, 2),
        "Break-even p": fmt(break_even, 3),
        "Decision": chosen,
    }
    interpretation = (f"Expected value = {fmt(p, 2)} x 8 + {fmt(1 - p, 2)} x 0 = {fmt(expected, 2)}. Net value = "
                      f"{fmt(expected, 2)} - {g(lam)} x {RECORD_TOKENS} = {fmt(net, 2)}. Break-even p = {g(lam)} x 1 / 8 = "
                      f"{fmt(break_even, 3)}. {verdict} In this model a record is worth 8 only while it is current, so a deleted, expired or "
                      f"superseded one has p = 0: its expected value is 0 x 8 + 1 x 0 = 0 and its net value is {signed(-cost, 2)}: the life-cycle fields exist to "
                      "move p, and the rule then does the rest.")
    steps = [
        f"A current record is worth {fmt(RECORD_VALUE, 0)} and an invalid one 0; it costs {RECORD_TOKENS} token at lambda {g(lam)}.",
        f"Expected value = p x 8 + (1 - p) x 0 = {fmt(p, 2)} x 8 + {fmt(1 - p, 2)} x 0 = {fmt(expected, 2)}.",
        f"Token cost = lambda x tokens = {g(lam)} x {RECORD_TOKENS} = {fmt(cost, 2)}.",
        f"Net value = {fmt(expected, 2)} - {fmt(cost, 2)} = {fmt(net, 2)}.",
        f"Break-even p = cost / value = {fmt(cost, 2)} / 8 = {fmt(break_even, 3)}; decision: {chosen}.",
    ]
    alt = (f"Left, three bars: expected value {fmt(expected, 1)}, token cost {fmt(cost, 1)} and net value {fmt(net, 1)} at p {g(p)} and "
           f"lambda {g(lam)}. Right, net value against p for lambda 1, 2 and 4, with a dashed break-even line at p {fmt(break_even, 3)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 15,
    "title": "What an Agent Should Remember: Retrieval, Compression, and Experience",
    "subtitle": "A memory earns its place by improving a later decision, and a similar old sentence is not current authority.",
    "summary": (
        "These four demonstrations follow the chapter's release controller. It has a small budget for what it may bring "
        "back into view: a current revocation, an old approval, a summary and an irrelevant note. They show which records a "
        "budget buys once expired and superseded records are screened out, what a summary can lose and when the bound stops "
        "applying, why wording similarity and incomplete deletion cannot stand in for authority, and when a record that may "
        "no longer be current is worth its tokens. Every number is a constructed teaching value."
    ),
    "ask_skill": {
        "prompt": (
            "Use budget 6, current time 10 and current version v2, with three records: review-v2 (4 tokens, value 8, written at 9, "
            "lifetime 3, authority, version v2), summary (2 tokens, value 3, written at 8, lifetime 5, no authority) and old-review "
            "(1 token, value 100, written at 9, lifetime 3, authority, version v1). Which records are retrieved, which are excluded "
            "and why, and what does a fresh timestamp fail to prove?"
        )
    },
    "demos": [
        {
            "id": "C15-D01",
            "title": "Records chosen under a token budget",
            "question": "Which records does a limited budget buy once expired and superseded records are screened out, and how does the price of a token change the answer?",
            "equations": [EQ_RETRIEVAL],
            "symbols": (
                "R is the set of records brought into view, m one record, c(m) its size in tokens, and B the token budget. "
                "The expected decision value is how much R improves the present decision, in declared units. \u03bb "
                "(lambda) is the price of one token in those same units. Net value of a record is its decision value minus "
                "\u03bb times its tokens. The arg max picks the set with the largest total. Before any value is counted, a record must be "
                "fresh (its age is at most its time to live) and, if it carries authority, bound to the current version."
            ),
            "prediction": "In the default case with \u03bb = 0 (budget 6), which records are retrieved?",
            "prediction_options": [
                "old-review alone, because its value is 100",
                "review-v2 and summary, for a total of 11",
                "all three records",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "old-review is excluded: its authority belongs to v1, and a fresh timestamp does not repair that. review-v2 (4 tokens, 8) and summary (2 tokens, 3) fill the budget of 6 for a value of 11.",
                "incorrect": "old-review carries authority for v1 but the current version is v2, so it is excluded before its value of 100 is counted. review-v2 and summary fit exactly and total 8 + 3 = 11. Choose the default case and \u03bb = 0.",
            },
            "misconception": {
                "title": "Retrieve the most similar or most valuable-looking text",
                "text": (
                    "The chapter says the memory problem is not to retrieve the most similar text, and that embedding similarity is a "
                    "selection score, not a probability of truth or utility. A high declared value on a superseded record does not "
                    "survive the freshness and version checks."
                ),
            },
            "scope_note": {
                "text": (
                    "The context-budget and stale-approval numbers are stipulated for teaching rather than drawn from a deployed system."
                ),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "Each eligible record gets a net value: what it adds to the decision minus what its tokens cost. Equation (15.1) "
                "looks for the set of records, no larger than the budget, with the greatest total net value. A record "
                "with negative net value is left out even when room remains, and a useful record can be left out because "
                "the budget is spent. Records that are expired or tied to an old version are excluded before any value is counted. "
                "Similarity to the request is not part of the calculation."
            ),
            "application": (
                "When a context window is limited, give each candidate record a stated value for the decision at hand "
                "and a cost, screen out what is expired or superseded, then keep the set with the best total instead of the closest wording."
            ),
            "assumptions": (
                "Values are declared by the designer and add up across records, which overcounts two records that repeat "
                "the same fact. The chapter example values the old approval 0 because it is superseded; the thread summary and its value 3 "
                "are defined for this reader, and the laboratory cases use their own declared values. A net value of exactly 0 is a tie and "
                "is reported as one."
            ),
            "check": "In the transfer case (budget 3, now 20, current version doc-C), which record is retrieved, and what is the total value at \u03bb = 0?",
            "answer": "expired (value 10, written at 10, lifetime 2) is excluded because its age 20 - 10 = 10 exceeds 2. current (3 tokens, value 4) is fresh and bound to doc-C, so it is retrieved for a total of 4.",
            "provenance": (
                "Constructed example: the chapter's revocation (2 tokens, value 8) and irrelevant note (value 0), plus the laboratory's "
                "default, changed and transfer cases for the memory-budget function; the thread summary and the old approval's value are "
                "defined for this reader, and every selection is computed with the laboratory's function."
            ),
            "source_section": "Retrieval is an action under budget",
            "source_anchor": "retrieval-is-an-action-under-budget",
            "controls": [
                {"key": "case", "label": "Case", "values": ["chapter", "default", "changed", "transfer"], "default": "chapter",
                 "value_labels": ["Chapter example: budget 2", "Default case: budget 6", "Changed case: budget 2", "Transfer case: budget 3, expired record"]},
                {"key": "lam", "label": "Price of a token, lambda (value units per token)", "values": [0, 1, 2], "default": 1},
            ],
            "function": "budget_picture",
        },
        {
            "id": "C15-D02",
            "title": "How much can a summary lose?",
            "question": "If a summary scores each action within epsilon of the full history, how much value can following it lose, and when does that claim stop applying?",
            "equations": [EQ_REGRET],
            "symbols": (
                "\u03b5 (epsilon) is the largest error the summary is claimed to make on any action that both the summary and the full "
                "history list. Regret is the value of the best action under the full history minus the full-history value "
                "of the action the summary picks. The equation block shows the limit: the chapter's claim is that this regret is "
                "at most 2 epsilon when the conditions below hold. Values are in declared units."
            ),
            "prediction": "In the changed case (full values 4 and 6, summary values 6 and 5) with \u03b5 = 2, does the summary keep the best action, and is the 2\u03b5 claim satisfied?",
            "prediction_options": [
                "It keeps Action 1 and the regret is 0",
                "It switches to Action 0, with regret 2 inside the limit 4",
                "It switches to Action 0 and the claim is violated",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "The summary prefers Action 0 (6 > 5), so the regret is 6 - 4 = 2, and the largest error is 2, so the premise holds and 2 is within 2 x 2 = 4.",
                "incorrect": "Summary values 6 and 5 prefer Action 0, whose full value is 4, so the regret is 6 - 4 = 2. The largest error is 2, so the premise holds with \u03b5 = 2 and 2 is within the limit 2 x 2 = 4. Select the changed case and \u03b5 = 2.",
            },
            "misconception": {
                "title": "The 2\u03b5 bound covers a summary that dropped a revocation",
                "text": (
                    "The chapter says that if the full history has approval but the summary omits a new revocation, the action sets differ and "
                    "no 2\u03b5 claim applies: query the authoritative external state or choose abstention."
                ),
            },
            "scope_note": {
                "text": (
                    "The compression section's 2\u03b5 bound presumes a shared continuation convention and covers only common feasible actions, "
                    "not actions a summary omits entirely; no particular retrieval system is shown to satisfy it here."
                ),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "The summary may undercount the best action by epsilon and overcount a rival by epsilon, so a rival can "
                "match or overtake only when the gap is at most 2 epsilon. That is why the regret cannot exceed 2 epsilon, provided every "
                "error really is at most epsilon: if the largest error is bigger than the claimed epsilon, the premise fails and the claim is silent. "
                "The argument also needs both versions to list the same permitted actions. Switch to the summary that dropped a revocation: "
                "the full history no longer permits release (drawn here as a value of -50) while the summary still scores it 10, "
                "so the guarantee has nothing to say."
            ),
            "application": (
                "Before replacing a long history with a short summary, check whether the summary errs only in its scores, "
                "or whether it has changed which actions are permitted. Only the first case is covered by the bound."
            ),
            "assumptions": (
                "The bound needs a shared way of valuing what comes after the decision and covers only actions both "
                "versions list, including the full-history best. The laboratory's cases are one supplied comparison each, so preserving "
                "one decision vector does not prove that every future task is preserved. Worst-case errors are placed by hand to show "
                "the limit; they are not a claim about any real summary."
            ),
            "check": "If epsilon is 2.5 and the worst-case errors are applied to scores 10 and 6, what are the summary's two scores and the largest possible regret?",
            "answer": "The scores are 10 - 2.5 = 7.5 and 6 + 2.5 = 8.5, so the summary follows the second action, with regret 10 - 6 = 4, within the limit 2 x 2.5 = 5.",
            "provenance": (
                "Constructed example: action values 10, 6 and 3 and an unauthorized release worth -50 are defined for "
                "this reader; the 2 epsilon bound is the chapter's, and the laboratory's default and changed compression cases (full values 4 and 6, "
                "summary values 3 and 5, then 6 and 5) are checked with its compression comparison."
            ),
            "source_section": "Compression that preserves action",
            "source_anchor": "compression-that-preserves-action",
            "controls": [
                {"key": "summary", "label": "What the summary did", "values": ["worst", "dropped", "default", "changed"], "default": "worst",
                 "value_labels": ["Errors placed against the best action", "Dropped the revocation", "Default case: values 3, 5", "Changed case: values 6, 5"]},
                {"key": "epsilon", "label": "Claimed summary error epsilon", "values": [1, 2, 3], "default": 1},
            ],
            "function": "compression_picture",
        },
        {
            "id": "C15-D03",
            "title": "Stale approval is not support",
            "question": "When an old approval is the most similar record, and deletion may reach only some views, which retrieval policy still blocks an unauthorized release?",
            "equations": [EQ_RETRIEVAL],
            "symbols": (
                "Similarity is a score for how closely a record's wording matches the request; it is not a probability of "
                "truth. Recency means the newest record. Decision aware means choosing the record with the best net value "
                "in Equation (15.1), here with room for one record of 2 tokens and \u03bb = 1 per token. A view is any place a record's content "
                "can survive: the visible store, a selection index, a derived summary, a cache, the model context or a downstream copy."
            ),
            "prediction": "Delete the old approval from the visible store only (a summary index keeps a copy of the same wording). Which policy still releases without permission?",
            "prediction_options": [
                "Recency only",
                "Similarity only, because the copy still has similarity 0.98",
                "None, because the approval was deleted",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "The copy keeps the same wording and so the same similarity, 0.98, which is the highest. Absence from one view says nothing about the others.",
                "incorrect": "Deleting from the visible store leaves the summary index's copy, whose wording and similarity (0.98) are unchanged, so Similarity only still retrieves it. Choose deletion from the store only.",
            },
            "misconception": {
                "title": "Recalling every sentence means the decision is right, and a deleted record is gone",
                "text": (
                    "The chapter says a high recall score with unauthorized release is a memory-system failure even if every retrieved sentence was "
                    "historically accurate, and that absence from one query result is not evidence that later agents cannot use a deleted record."
                ),
            },
            "scope_note": {
                "text": (
                    "The deletion-aware index and conflict-resolution rule appear only as named requirements; building either is left to the implementer."
                ),
                "source_section": "What this does not settle",
            },
            "stepper": "deletion",
            "explanation": (
                "The old approval reads closest to the request, so a similarity ranking retrieves it and releases without "
                "permission, even though every retrieved sentence was accurate when written. Recency retrieves the newest record. The "
                "decision-aware rule gives the revocation net value 8 - 2 = 6 and the others 0 - 2, so it keeps the revocation; if the "
                "revocation cannot be reached, nothing has positive net value and the controller abstains. Deletion that reaches only the "
                "visible store leaves derived copies competing; deletion from every view removes the approval but does not choose among the rest."
            ),
            "application": (
                "Test a memory component by what the controller does next, not only by whether the retrieved text reads "
                "well, and query derived views as well as the source store after a deletion."
            ),
            "assumptions": (
                "Room for one record, the book's three similarity scores for the approval and the note, and a revocation "
                "valued 8 against 0 for the others. The index copy of the approval is assumed to keep the approval's wording and so its similarity; "
                "the 0.99 revocation similarity and the note's recency are defined for this reader. Recency fails if the newest record is not the "
                "authority, and the decision-aware rule is only as good as the declared values and the authority lookup. 'Correct' means "
                "consistent with the chapter's rule that a revoked release must not go ahead."
            ),
            "check": "A new record has value 5 and 2 tokens, with \u03bb = 3. What is its net value, and is it retrieved?",
            "answer": "5 - 3 x 2 = (-1). The net value is negative, so Equation (15.1) leaves it out.",
            "provenance": (
                "Constructed example: the chapter's similarities 0.98, 0.72 and 0.80 and its values 8 and 0; the other revocation similarity, "
                "the unreachable case and the deletion states are defined for this reader, computed with the "
                "laboratory's memory-budget function."
            ),
            "source_section": "Stale approval is not support",
            "source_anchor": "stale-approval-is-not-support",
            "controls": [
                {"key": "revocation_similarity", "label": "Similarity of the current revocation", "values": [0.72, 0.99], "default": 0.72},
                {"key": "authority", "label": "Can the current authority be reached?", "values": ["reachable", "unreachable"], "default": "reachable",
                 "value_labels": ["Yes", "No, the lookup fails"]},
                {"key": "deletion", "label": "How far deletion of the old approval reached", "values": ["none", "store", "all"], "default": "none",
                 "value_labels": ["Not deleted", "Visible store only (a summary index keeps a copy)", "Every view"]},
            ],
            "function": "stale_picture",
        },
        {
            "id": "C15-D04",
            "title": "A record that may no longer be current",
            "question": "How likely must a record be to still be current before it is worth its tokens?",
            "equations": [EQ_EXERCISE],
            "symbols": (
                "p is the probability that the record is still current. A current record is worth 8 decision-value units "
                "and an invalid one is worth 0. The record costs 1 token, and \u03bb (lambda) is the price of a token in the "
                "same units. The expected value is p x 8 + (1 - p) x 0, and the net value subtracts \u03bb times the tokens."
            ),
            "prediction": "At \u03bb = 4, where does the net value cross zero? That value of p is the break-even probability.",
            "prediction_options": ["p = 0.25", "p = 0.5", "p = 0.8"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "The net value is p x 8 - 4 x 1, which is zero at p = 4 / 8 = 0.5.",
                "incorrect": "Net value = 8p - 4, which is zero at p = 4 / 8 = 0.5. Set \u03bb to 4 and read the break-even line.",
            },
            "misconception": {
                "title": "Durable authority is as safe as durable knowledge",
                "text": (
                    "The chapter says broad durable knowledge may be useful but broad durable authority is dangerous: the more a record can "
                    "authorize, the shorter its expiry and the stronger its required provenance should be."
                ),
            },
            "explanation": (
                "A record's status, expiry and version tell a controller how likely the record is to still hold. That "
                "probability scales its value: at p = 0.6 the expected value is 4.8, and one token at \u03bb = 1 leaves a net of "
                "3.8. The same record at a higher token price needs a higher p, and in this model, where a record is worth 8 only while it is current, a deleted or expired record has p = 0 "
                "and cannot pay for itself."
            ),
            "application": (
                "Record who wrote an item, when it was seen, and when it expires, so the controller can estimate how "
                "likely it is to be current and charge retrieval accordingly."
            ),
            "assumptions": (
                "One record, valued 8 if current and 0 if invalid, with no partial credit. The probability p is assumed "
                "to come from the record's fields; an honest estimate of it is the hard part and is not shown here. "
                "A record that can authorize an action should need a much higher p than this simple price implies."
            ),
            "check": "A record is worth 10 if current and 0 if invalid, costs 2 tokens, with \u03bb = 1 and p = 0.3. What is its net value?",
            "answer": "Expected value 0.3 x 10 + 0.7 x 0 = 3.0; net 3.0 - 1 x 2 = 1.0. It is positive, so retrieve it (break-even p = 2 / 10 = 0.2).",
            "provenance": (
                "Constructed example: the chapter's Exercise 1 values (value 8, one token, probability 0.6, \u03bb = 1); the "
                "other probabilities and token prices are defined for this reader."
            ),
            "source_section": "Exercises",
            "source_anchor": "exercises",
            "controls": [
                {"key": "p_current", "label": "Probability the record is still current, p", "values": [0.25, 0.5, 0.6, 0.8], "default": 0.6},
                {"key": "lam", "label": "Price of a token, lambda", "values": [1, 2, 4], "default": 1},
            ],
            "function": "lifecycle_picture",
        },
    ],
}

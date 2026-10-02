"""Chapter 15 reader: What an Agent Should Remember.

Four demonstrations built on Equation (15.1), the chapter's budgeted retrieval
rule, and on the chapter's inline results (8 - 2 = 6, the 2 epsilon regret
bound, and the Exercise 1 value 0.6 x 8 + 0.4 x 0 = 4.8). Demonstrations 1 to 3
call the laboratory's own memory-budget function
(math_ai_agents.chapters.ch15.evaluate) and assert that it agrees with the
reader's direct calculation. Every number is a constructed teaching value.
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

# (name, tokens, decision value). The revocation (2 tokens, value 8) and the
# irrelevant note (2 tokens, value 0) are the book's example. The old approval
# has value 0 because a superseded approval cannot support a present release;
# the thread summary (value 3) is a value defined for this reader.
RECORDS = [
    ("Current revocation", 2, 8.0),
    ("Thread summary", 2, 3.0),
    ("Old approval", 2, 0.0),
    ("Irrelevant note", 2, 0.0),
]


def best_sets(lam, budget):
    """All subsets that maximize total net value within the budget, by direct enumeration."""
    scored = []
    for mask in range(1 << len(RECORDS)):
        subset = [RECORDS[i] for i in range(len(RECORDS)) if mask >> i & 1]
        tokens = sum(r[1] for r in subset)
        if tokens > budget:
            continue
        scored.append((sum(r[2] - lam * r[1] for r in subset), tuple(r[0] for r in subset), tokens))
    top = max(s[0] for s in scored)
    winners = [s for s in scored if abs(s[0] - top) <= 1e-9]
    winners.sort(key=lambda s: (len(s[1]), s[2], s[1]))
    return top, winners


def lab_retrieval_value(lam, budget):
    """The laboratory's exact selection, fed the net values; the old approval is bound to an older version."""
    records = []
    for name, tokens, value in RECORDS:
        old = name == "Old approval"
        records.append({
            "id": name, "tokens": tokens, "decision_value": max(value - lam * tokens, 0.0),
            "timestamp": 9, "ttl": 3, "authority": name in ("Current revocation", "Old approval"),
            "version": "v1" if old else "v2",
        })
    out = evaluate({"budget": budget, "now": 10, "current_version": "v2", "records": records,
                    "original_action_values": [1, 0], "compressed_action_values": [1, 0]})
    return out["metrics"]["retrieval_value"], out["metrics"]["excluded_ids"]


def budget_picture(lam=1, budget=2):
    lam, budget = float(lam), int(budget)
    top, winners = best_sets(lam, budget)
    lab_value, lab_excluded = lab_retrieval_value(lam, budget)
    if not math.isclose(lab_value, top, abs_tol=1e-9) or lab_excluded != ["Old approval"]:
        raise AssertionError("laboratory selection disagrees with direct enumeration of Equation (15.1)")
    chosen_names = set(winners[0][1])
    tie = len(winners) > 1
    nets = {name: value - lam * tokens for name, tokens, value in RECORDS}

    fig, ax = new_figure(height=4.2)
    ys = list(range(len(RECORDS)))[::-1]
    for y, (name, tokens, value) in zip(ys, RECORDS):
        net = nets[name]
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
        x_text = max(net, 0) + 0.3
        ax.text(x_text, y, f"{fmt(net, 1)} {note}", va="center", ha="left", fontsize=10.5, color=PALETTE["ink"])
    ax.axvline(0, color=PALETTE["ink"], linewidth=1)
    ax.set_yticks(ys, [f"{n}\n({t} tokens, value {g(v)})" for n, t, v in RECORDS])
    ax.set_xlim(-9.5, 12)
    ax.set_ylim(-0.6, len(RECORDS) - 0.4)
    ax.set_xlabel("Net value = decision value - \u03bb x tokens (constructed units)")
    ax.set_ylabel("Record")
    ax.set_title(f"Budget B = {budget} tokens, \u03bb = {g(lam)} per token", fontsize=11.5)
    ax.grid(axis="y", alpha=0)

    used = winners[0][2]
    shown = ", ".join(winners[0][1]) if winners[0][1] else "no record"
    metrics = {
        "Chosen by Equation (15.1)": shown + (" (tie)" if tie else ""),
        "Total net value": fmt(top, 1),
        "Tokens used": f"{used} of {budget}",
        "Best sets": str(len(winners)),
    }
    parts = [f"{n.lower() if n != 'Current revocation' else 'revocation'} {g(v)} - {g(lam)} x {t} = {fmt(nets[n], 1)}"
             for n, t, v in RECORDS]
    sums = "Net value = decision value - lambda x tokens: " + "; ".join(parts) + "."
    if tie:
        options = " or ".join("{" + ", ".join(w[1]) + "}" if w[1] else "{nothing}" for w in winners)
        verdict = (f"A record with net value exactly 0 changes nothing, so {options} all total {fmt(top, 1)}. "
                   "Equation (15.1) returns every one of them as a maximizer and does not choose; "
                   "a stated rule such as fewest tokens does. The figure shows the smallest set.")
    elif winners[0][1]:
        verdict = f"Equation (15.1) keeps {shown}, for a total of {fmt(top, 1)} using {used} of {budget} tokens."
    else:
        verdict = "Every record costs more than it is worth, so Equation (15.1) keeps nothing."
    extra = ""
    if not tie:
        skipped = [n for n in nets if nets[n] > 1e-9 and n not in chosen_names]
        if skipped:
            extra = f" {skipped[0]} has net value {fmt(nets[skipped[0]], 1)} but would push the total past the budget."
    interpretation = (f"{sums} {verdict}{extra} Wording similarity never enters: the old approval may read closest to "
                      "the request, but its decision value is 0 once it is superseded, so it can only lose.")
    return fig, metrics, interpretation


# ---------------------------------------------------------------------------
# Demonstration 2: compression and the 2 epsilon bound
# ---------------------------------------------------------------------------

ACTIONS = ["Release", "Ask owner", "Abstain"]
FULL_VALUES = [10.0, 6.0, 3.0]          # full history, no revocation (constructed)
UNAUTHORIZED = -50.0                     # true value of releasing after a revocation (constructed)


def lab_preserved(full, summary):
    out = evaluate({"budget": 1, "now": 1, "current_version": "v", "records": [
        {"id": "r", "tokens": 1, "decision_value": 0, "timestamp": 0, "ttl": 1, "authority": False, "version": "v"}],
        "original_action_values": list(full), "compressed_action_values": list(summary)})
    return out["metrics"]["compression_preserves_action"]


def compression_picture(epsilon=1, summary="worst"):
    eps = float(epsilon)
    if summary == "worst":
        full = list(FULL_VALUES)
        approx = [full[0] - eps, full[1] + eps, full[2]]
        bound_applies = True
    else:
        # Full history holds a revocation: releasing is no longer permitted and is worth UNAUTHORIZED.
        full = [UNAUTHORIZED, FULL_VALUES[1], FULL_VALUES[2]]
        approx = [FULL_VALUES[0], FULL_VALUES[1], FULL_VALUES[2]]
        bound_applies = False
    best_full = max(full)
    top = max(approx)
    picks = [i for i, v in enumerate(approx) if abs(v - top) <= 1e-9]
    regrets = [best_full - full[i] for i in picks]
    tie = len(picks) > 1
    limit = 2 * eps
    max_error = max(abs(a - f) for a, f in zip(approx, full))
    if not tie and lab_preserved(full, approx) != (picks[0] == full.index(best_full)):
        raise AssertionError("laboratory action check disagrees with the direct comparison")

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    x = list(range(len(ACTIONS)))
    w = 0.38
    left.bar([i - w / 2 for i in x], full, w, color=PALETTE["navy"])
    left.bar([i + w / 2 for i in x], approx, w, color="white", edgecolor=PALETTE["teal"], hatch="///", linewidth=1.2)
    for i in x:
        left.text(i - w / 2, full[i] + (0.8 if full[i] >= 0 else -0.8), fmt(full[i], 1), ha="center",
                  va="bottom" if full[i] >= 0 else "top", fontsize=10.5, color=PALETTE["navy"])
        left.text(i + w / 2, approx[i] + (0.8 if approx[i] >= 0 else -0.8), fmt(approx[i], 1), ha="center",
                  va="bottom" if approx[i] >= 0 else "top", fontsize=10.5, color=PALETTE["teal"])
    left.axhline(0, color=PALETTE["ink"], linewidth=1)
    left.set_xticks(x, ACTIONS)
    left.set_ylim(-62 if not bound_applies else -4, 17)
    left.set_xlabel("Action (dark: full history, hatched: summary)")
    left.set_ylabel("Estimated value of the action")
    left.set_title("Full history against its summary", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    reg_show = max(regrets)
    right.barh([1], [reg_show], height=0.5, color=PALETTE["terracotta"])
    right.barh([0], [limit], height=0.5, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.2)
    top_x = max(reg_show, limit) * 1.0 + 0.001
    right.set_xlim(0, max(top_x * 1.18, 6.5) + (0 if bound_applies else 12))
    right.set_yticks([1, 0], ["Regret of\nsummary action", "Limit 2\u03b5"])
    right.set_ylim(-0.6, 1.6)
    for yv, val, nm in ((1, reg_show, "regret"), (0, limit, "limit")):
        txt = fmt(val, 1) if not (nm == "regret" and tie) else f"0.0 or {fmt(reg_show, 1)} (tie)"
        right.text(val + 0.15 * (right.get_xlim()[1] / 10), yv, txt, va="center", ha="left", fontsize=10.5, color=PALETTE["ink"])
    right.set_xlabel("Value lost by following the summary")
    right.set_ylabel("Quantity")
    right.set_title(f"\u03b5 = {g(eps)}", fontsize=11.5)
    right.grid(axis="y", alpha=0)

    names = [ACTIONS[i] for i in picks]
    chosen = " or ".join(names) + (" (tie)" if tie else "")
    metrics = {
        "Largest error of the summary": fmt(max_error, 1),
        "Summary follows": chosen,
        "Regret of that action": (f"0.0 or {fmt(reg_show, 1)}" if tie else fmt(regrets[0], 1)),
        "Limit 2\u03b5": fmt(limit, 1),
        "Bound applies": "yes" if bound_applies else "no",
    }
    if bound_applies:
        s0, s1 = approx[0], approx[1]
        calc = (f"Summary scores: release {fmt(FULL_VALUES[0], 0)} - {g(eps)} = {fmt(s0, 1)}, ask owner "
                f"{fmt(FULL_VALUES[1], 0)} + {g(eps)} = {fmt(s1, 1)}, abstain {fmt(FULL_VALUES[2], 0)}.")
        if tie:
            tail = (f" The two top scores tie, so the summary may follow either one. If it follows ask owner, regret = "
                    f"{fmt(best_full, 0)} - {fmt(FULL_VALUES[1], 0)} = {fmt(reg_show, 1)}, which equals the limit 2 x {g(eps)} = "
                    f"{fmt(limit, 1)}: the bound can be reached.")
        elif regrets[0] > 1e-9:
            tail = (f" It follows ask owner, so regret = {fmt(best_full, 0)} - {fmt(FULL_VALUES[1], 0)} = {fmt(regrets[0], 1)}, "
                    f"within the limit 2 x {g(eps)} = {fmt(limit, 1)}.")
        else:
            tail = (f" It still follows release, so regret = {fmt(best_full, 0)} - {fmt(best_full, 0)} = {fmt(0, 1)}, "
                    f"far inside the limit 2 x {g(eps)} = {fmt(limit, 1)}.")
        interpretation = (calc + tail + " Every error here is at most epsilon on actions both versions list, which is what "
                          "the bound requires.")
    else:
        interpretation = (f"The full history holds a revocation, so releasing now is not permitted; this reader draws that as a "
                          f"value of {fmt(UNAUTHORIZED, 0)}, a loss of {fmt(-UNAUTHORIZED, 0)}. The summary "
                          f"kept only the old approval and still scores release at {fmt(FULL_VALUES[0], 0)}, an error of "
                          f"{fmt(FULL_VALUES[0], 0)} - ({fmt(UNAUTHORIZED, 0)}) = {fmt(FULL_VALUES[0] - UNAUTHORIZED, 0)}, far above "
                          f"epsilon = {g(eps)}. It follows release, so regret = {fmt(best_full, 0)} - ({fmt(UNAUTHORIZED, 0)}) = "
                          f"{fmt(regrets[0], 0)}. The two versions disagree about which actions are permitted, so no 2 epsilon "
                          f"claim applies: the bound needs every error on shared actions to be at most epsilon, and release is not "
                          f"a permitted action in the full history. Changing epsilon moves only the limit bar here; the error "
                          f"{fmt(FULL_VALUES[0] - UNAUTHORIZED, 0)} and the regret {fmt(regrets[0], 0)} stay the same. "
                          "The remedy is to query current authority or abstain.")
    return fig, metrics, interpretation


# ---------------------------------------------------------------------------
# Demonstration 3: stale approval under three retrieval policies
# ---------------------------------------------------------------------------

ORDER = ["Old approval", "Irrelevant note", "Current revocation"]   # oldest to newest
VALUE = {"Old approval": 0.0, "Irrelevant note": 0.0, "Current revocation": 8.0}
TOKENS = 2
LAMBDA = 1.0
SLOT_MARKERS = {"Recency only": ("o", PALETTE["navy"]), "Similarity only": ("s", PALETTE["terracotta"]),
                "Decision aware": ("D", PALETTE["teal"])}


def outcome_of(record):
    return {
        "Old approval": "Unauthorized release",
        "Current revocation": "Release blocked (correct)",
        "Irrelevant note": "Irrelevant recollection",
        None: "Abstain (correct)",
    }[record]


def stale_picture(revocation_similarity=0.72, authority="reachable"):
    sim = {"Old approval": 0.98, "Irrelevant note": 0.80, "Current revocation": float(revocation_similarity)}
    reachable = authority == "reachable"
    available = [n for n in ORDER if reachable or n != "Current revocation"]
    recency = available[-1]
    similarity = max(available, key=lambda n: sim[n])
    nets = {n: VALUE[n] - LAMBDA * TOKENS for n in available}
    best = max(nets.values())
    decision = max(nets, key=nets.get) if best > 1e-9 else None
    lab_value, _ = lab_retrieval_value_one(nets)
    if not math.isclose(lab_value, max(best, 0.0), abs_tol=1e-9):
        raise AssertionError("laboratory selection disagrees with the net values")
    picks = {"Recency only": recency, "Similarity only": similarity, "Decision aware": decision}

    fig, ax = new_figure(height=4.4)
    columns = ORDER + [None]
    col_x = {name: i for i, name in enumerate(columns)}
    if not reachable:
        ax.axvspan(1.62, 2.38, facecolor="#eef1f2", edgecolor=PALETTE["light"], hatch="///", linewidth=0)
        ax.text(2, 2.62, "not reachable", ha="center", va="center", fontsize=10.5, color=PALETTE["grey"])
    rows = {"Recency only": 2, "Similarity only": 1, "Decision aware": 0}
    for policy, record in picks.items():
        marker, color = SLOT_MARKERS[policy]
        xx, yy = col_x[record], rows[policy]
        ax.plot([xx], [yy], marker, color=color, markersize=12, markeredgecolor=PALETTE["ink"])
        ax.annotate(outcome_of(record).replace(" (correct)", "\n(correct)").replace("Unauthorized ", "Unauthorized\n").replace("Irrelevant ", "Irrelevant\n"), (xx, yy), xytext=(0, -16), textcoords="offset points",
                    ha="center", va="top", fontsize=10.5, color=PALETTE["ink"])
    ax.set_xticks(range(4), [f"{n.replace(' ', chr(10), 1)}\nsimilarity {fmt(sim[n], 2)}" for n in ORDER] + ["No record\nretrieved"])
    ax.set_yticks([2, 1, 0], ["Recency only", "Similarity only", "Decision aware"])
    ax.set_xlim(-0.75, 3.75)
    ax.set_ylim(-0.95, 2.85)
    ax.set_xlabel("Record, oldest to newest (room for one record)")
    ax.set_ylabel("Retrieval policy")
    ax.set_title("What each policy retrieves, and what follows", fontsize=11.5)

    metrics = {
        "Recency only": f"{recency}: {outcome_of(recency)}",
        "Similarity only": f"{similarity}: {outcome_of(similarity)}",
        "Decision aware": (f"{decision}: " if decision else "") + outcome_of(decision),
    }
    rank = sorted(available, key=lambda n: -sim[n])
    nets_text = "; ".join(
        f"{label} {g(VALUE[n])} - {g(LAMBDA)} x {TOKENS} = {signed(VALUE[n] - LAMBDA * TOKENS, 1)}"
        for label, n in (("revocation", "Current revocation"), ("old approval", "Old approval"), ("note", "Irrelevant note"))
        if n in available)
    top_pair = f"{fmt(sim[rank[0]], 2)} > {fmt(sim[rank[1]], 2)}"
    if reachable:
        tail = (f"Decision aware retrieves the revocation, the only record with positive net value, and blocks the release. "
                f"Similarity only follows the highest score ({rank[0].lower()}, {top_pair}).")
    else:
        tail = (f"The revocation cannot be reached, so no remaining record has positive net value and Equation (15.1) keeps "
                f"nothing: the controller abstains instead of trusting stale wording. Similarity only still follows the "
                f"highest score ({rank[0].lower()}, {top_pair}).")
    interpretation = (f"Net value with lambda = 1 and 2 tokens per record: {nets_text}. {tail} Recency only retrieves the "
                      f"newest record it can reach, {recency.lower()}. Which record is most similar is a fact about wording; "
                      "which record is current authority is a different fact.")
    return fig, metrics, interpretation


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
    for other, style, col in ((1.0, "-", PALETTE["navy"]), (4.0, "-", PALETTE["terracotta"])):
        selected = math.isclose(other, lam)
        right.plot(ps, [RECORD_VALUE * q - other * RECORD_TOKENS for q in ps], style, color=col,
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
    return fig, metrics, interpretation


CHAPTER = {
    "number": 15,
    "title": "What an Agent Should Remember: Retrieval, Compression, and Experience",
    "subtitle": "A memory earns its place by improving a later decision, and a similar old sentence is not current authority.",
    "summary": (
        "These four demonstrations follow the chapter's release controller. It has a small budget for what it may bring "
        "back into view: a current revocation, an old approval, a summary and an irrelevant note. Each demonstration "
        "changes one declared value and shows which record is kept, what a summary can lose, and why wording similarity "
        "cannot stand in for authority."
    ),
    "demos": [
        {
            "id": "C15-D01",
            "title": "Records chosen under a token budget",
            "question": "Which records does a limited budget buy, and how does the price of a token change the answer?",
            "equations": [EQ_RETRIEVAL],
            "symbols": (
                "R is the set of records brought into view, m one record, c(m) its size in tokens, and B the token budget. "
                "The expected decision value is how much R improves the present decision, in declared units. \u03bb "
                "(lambda) is the price of one token in those same units. Net value of a record is its decision value minus "
                "\u03bb times its tokens. The arg max picks the set with the largest total."
            ),
            "prediction": "With a budget of 2 and \u03bb = 1, which record is chosen? Raise \u03bb to 4. Does the revocation still win, and what does the equation say?",
            "explanation": (
                "Each record gets a net value: what it adds to the decision minus what its tokens cost. Equation (15.1) "
                "looks for the set of records, no larger than the budget, with the greatest total net value. A record "
                "with negative net value is left out even when room remains, and a useful record can be left out because "
                "the budget is spent. Similarity to the request is not part of the calculation."
            ),
            "application": (
                "When a context window is limited, give each candidate record a stated value for the decision at hand "
                "and a cost, then keep the set with the best total instead of the closest wording."
            ),
            "assumptions": (
                "Values are declared by the designer and add up across records, which overcounts two records that repeat "
                "the same fact. The old approval is valued 0 because it is superseded; if that were wrong, so would the "
                "choice be. The thread summary and its value 3 are defined for this reader; the revocation and note "
                "values are the book's. A net value of exactly 0 is a tie and is reported as one."
            ),
            "check": "With a budget of 2 and \u03bb = 2, what is the net value of the revocation and of the thread summary, and which is chosen?",
            "answer": "Revocation 8 - 2 x 2 = 4 and summary 3 - 2 x 2 = (-1). Only the revocation has positive net value, so it alone is chosen.",
            "provenance": (
                "Constructed example: the revocation (2 tokens, value 8) and the irrelevant note (value 0) are the "
                "chapter's numbers; the thread summary and the old approval's value are defined for this reader, "
                "computed with the laboratory's memory-budget function."
            ),
            "source_section": "Retrieval is an action under budget",
            "source_anchor": "retrieval-is-an-action-under-budget",
            "controls": [
                {"key": "lam", "label": "Price of a token, lambda (value units per token)", "values": [1, 1.5, 2, 4], "default": 1},
                {"key": "budget", "label": "Token budget B", "values": [2, 4], "default": 2},
            ],
            "function": "budget_picture",
        },
        {
            "id": "C15-D02",
            "title": "How much can a summary lose?",
            "question": "If a summary scores each action within epsilon of the full history, how much value can following it lose?",
            "equations": [EQ_REGRET],
            "symbols": (
                "\u03b5 (epsilon) is the largest error the summary makes on any action that both the summary and the full "
                "history list. Regret is the value of the best action under the full history minus the full-history value "
                "of the action the summary picks. The equation block shows the limit: the chapter's claim is that this regret is "
                "at most 2 epsilon when the conditions below hold. Values are in declared units."
            ),
            "prediction": "Make epsilon 3 with errors in the worst direction. Does the summary still follow release? How large is the regret compared with 2 times epsilon?",
            "explanation": (
                "The summary may undercount the best action by epsilon and overcount a rival by epsilon, so a rival can "
                "match or overtake only when the gap is at most 2 epsilon. That is why the regret cannot exceed 2 epsilon. The "
                "argument needs both versions to list the same permitted actions. Switch to the summary that dropped a revocation: "
                "the full history no longer permits release (drawn here as a value of -50) while the summary still scores it 10, "
                "so the guarantee has nothing to say."
            ),
            "application": (
                "Before replacing a long history with a short summary, check whether the summary errs only in its scores, "
                "or whether it has changed which actions are permitted. Only the first case is covered by the bound."
            ),
            "assumptions": (
                "The bound needs a shared way of valuing what comes after the decision and covers only actions both "
                "versions list, including the full-history best. Here the worst-case errors are placed by hand to show "
                "the limit; they are not a claim about any real summary. When the summary tie breaks the other way the "
                "regret can reach the limit exactly."
            ),
            "check": "If epsilon is 2.5 and the worst-case errors are applied to scores 10 and 6, what are the summary's two scores and the largest possible regret?",
            "answer": "The scores are 10 - 2.5 = 7.5 and 6 + 2.5 = 8.5, so the summary follows the second action, with regret 10 - 6 = 4, within the limit 2 x 2.5 = 5.",
            "provenance": (
                "Constructed example: action values 10, 6 and 3 and an unauthorized release worth -50 are defined for "
                "this reader; the 2 epsilon bound is the chapter's, and the action check calls the laboratory's "
                "compression comparison."
            ),
            "source_section": "Compression that preserves action",
            "source_anchor": "compression-that-preserves-action",
            "controls": [
                {"key": "epsilon", "label": "Summary error epsilon", "values": [0.5, 1, 2, 3], "default": 1},
                {"key": "summary", "label": "What the summary did", "values": ["worst", "dropped"], "default": "worst",
                 "value_labels": ["Scores off by epsilon, same actions", "Dropped the revocation"]},
            ],
            "function": "compression_picture",
        },
        {
            "id": "C15-D03",
            "title": "Stale approval is not support",
            "question": "When an old approval is the most similar record, which retrieval policy still blocks an unauthorized release?",
            "equations": [EQ_RETRIEVAL],
            "symbols": (
                "Similarity is a score for how closely a record's wording matches the request; it is not a probability of "
                "truth. Recency means the newest record. Decision aware means choosing the record with the best net value "
                "in Equation (15.1), here with room for one record of 2 tokens and \u03bb = 1 per token."
            ),
            "prediction": "Raise the revocation's similarity to 0.99. Which policy changes its answer? Then make the revocation unreachable. What does each policy do?",
            "explanation": (
                "The old approval reads closest to the request, so a similarity ranking retrieves it and releases without "
                "permission. Recency retrieves the newest record. The decision-aware rule gives the revocation net value "
                "8 - 2 = 6 and the others 0 - 2, so it keeps the revocation; if the revocation cannot be reached, nothing has "
                "positive net value and the controller abstains."
            ),
            "application": (
                "Test a memory component by what the controller does next, not only by whether the retrieved text reads "
                "well: a release controller can recall every sentence and still release without permission."
            ),
            "assumptions": (
                "Room for one record, the book's three similarity scores for the approval and the note, and a revocation "
                "valued 8 against 0 for the others. Recency fails if the newest record is not the authority, and the "
                "decision-aware rule is only as good as the declared values and the authority lookup. 'Correct' means "
                "consistent with the chapter's rule that a revoked release must not go ahead. The note is taken to be newer than the old "
                "approval; this ordering is defined for this reader and is not in the chapter, which says only that the revocation is later."
            ),
            "check": "A new record has value 5 and 2 tokens, with \u03bb = 3. What is its net value, and is it retrieved?",
            "answer": "5 - 3 x 2 = (-1). The net value is negative, so Equation (15.1) leaves it out.",
            "provenance": (
                "Constructed example: the chapter's similarities 0.98, 0.72 and 0.80 and its values 8 and 0; the two other "
                "revocation similarities and the unreachable case are defined for this reader, computed with the "
                "laboratory's memory-budget function."
            ),
            "source_section": "Stale approval is not support",
            "source_anchor": "stale-approval-is-not-support",
            "controls": [
                {"key": "revocation_similarity", "label": "Similarity of the current revocation", "values": [0.72, 0.9, 0.99], "default": 0.72},
                {"key": "authority", "label": "Can the current authority be reached?", "values": ["reachable", "unreachable"], "default": "reachable",
                 "value_labels": ["Yes", "No, the lookup fails"]},
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
            "prediction": "At \u03bb = 4, find the value of p where retrieving the record stops being worth it. Then predict the net value at p = 0.6.",
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
            "source_section": "A record needs a life cycle",
            "source_anchor": "a-record-needs-a-life-cycle",
            "controls": [
                {"key": "p_current", "label": "Probability the record is still current, p", "values": [0.25, 0.5, 0.6, 0.8], "default": 0.6},
                {"key": "lam", "label": "Price of a token, lambda", "values": [1, 4], "default": 1},
            ],
            "function": "lifecycle_picture",
        },
    ],
}

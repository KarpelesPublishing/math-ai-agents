"""Chapter 6 reader: The Price of a Choice.

Four demonstrations built on Equations (6.1) to (6.4). Demonstrations 1, 2
and 4 call the laboratory's own expected-utility function
(math_ai_agents.chapters.ch06.evaluate), so the reader, the notebook and the
chapter skill agree; Demonstration 1 includes the notebook's default, changed
and transfer cases next to the book's Table 6.1. Every number is a
constructed teaching value; the values in Demonstrations 1 and 2 are the
book's Table 6.1 values unless a state says otherwise.
"""
import math

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from math_ai_agents.chapters.ch06 import evaluate
from readerkit import PALETTE, argmax_set, fmt, label_point, new_figure, signed

SUPPORTED = 100.0  # utility of a supported release (Table 6.1 scale)
HOUR_COST = 5.0    # book's elicited price of an hour of delay
DAY_COST = 40.0    # book's elicited price of a day of delay
SUPPORT = {"Release now": 0.85, "Request evidence": 0.97, "Escalate to a person": 0.995}

EQ_ORDER = r"y_1 \succ y_2 \iff u(y_1) > u(y_2)"
EQ_EU = r"\operatorname{EU}(a)=\sum_{y}p(y\mid a)\,u(y)"
EQ_ARGMAX = r"a^{\star}=\arg\max_{a\in\mathcal{A}}\operatorname{EU}(a)"
EQ_CE = r"u(\operatorname{CE})=\operatorname{E}\!\left[u(Y)\right]"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


def g(x):
    """Number for a written calculation: up to six significant digits, no trailing zeros."""
    text = f"{float(x):.6g}"
    return "0" if text == "-0" else text


def gs(x):
    """Like g, with negatives in parentheses for written sums."""
    text = g(x)
    return f"({text})" if text.startswith("-") else text


def release_actions(unsupported, day_cost, hour_cost=HOUR_COST, release_support=0.85):
    """Table 6.1 rows in the laboratory's input format (delay cost charged once per action)."""
    support = dict(SUPPORT, **{"Release now": release_support})
    costs = {"Release now": 0.0, "Request evidence": float(hour_cost), "Escalate to a person": float(day_cost)}
    return [
        {"name": name, "probabilities": [p, 1 - p], "utilities": [SUPPORTED, float(unsupported)], "cost": costs[name]}
        for name, p in support.items()
    ]


def lab_scores(actions):
    """Expected utility of each action, computed by the laboratory's evaluate()."""
    out = evaluate({"actions": actions})
    return {row["action"]: row["expected_utility"] for row in out["tables"]}


def written_eu(action):
    """EU of one action as a written sum, with the action's own numbers."""
    ps, us = action["probabilities"], action["utilities"]
    terms = " + ".join(f"{g(p)} x {gs(u)}" for p, u in zip(ps, us))
    value = sum(p * u for p, u in zip(ps, us)) - action["cost"]
    cost = f" - {g(action['cost'])}" if action["cost"] else ""
    return f"EU({action['name']}) = {terms}{cost} = {fmt(value, 1)}"


# Demonstration 1: three actions, one rule, and where the order flips

TABLES = {
    "book": {"name": "Table 6.1", "fail": "unsupported release", "range": (-500.0, 0.0), "asis": 0.0, "worse": -400.0},
    "lab": {"name": "notebook default", "fail": "failed release", "range": (-150.0, 0.0), "asis": -50.0, "worse": -100.0},
    "transfer": {"name": "notebook transfer", "fail": "failed retry", "range": (-40.0, 0.0), "asis": -12.0, "worse": -24.0},
}


def table_actions(table, u):
    if table == "book":
        return release_actions(u, DAY_COST)
    if table == "lab":
        return [
            {"name": "Release", "probabilities": [0.9, 0.1], "utilities": [10.0, float(u)], "cost": 0.0},
            {"name": "Review", "probabilities": [1.0], "utilities": [2.0], "cost": 0.0},
            {"name": "Abstain", "probabilities": [1.0], "utilities": [0.0], "cost": 0.0},
        ]
    return [
        {"name": "Retry", "probabilities": [0.7, 0.3], "utilities": [8.0, float(u)], "cost": 1.0},
        {"name": "Escalate", "probabilities": [1.0], "utilities": [1.0], "cost": 0.0},
    ]


def line_of(action):
    """EU as a function of the failure utility u: c + s u (s is the chance of the failure outcome)."""
    ps, us = action["probabilities"], action["utilities"]
    if len(ps) == 2:
        return ps[0] * us[0] - action["cost"], ps[1]
    return us[0] - action["cost"], 0.0


def table_picture(table="book", worse="asis"):
    spec = TABLES[table]
    u = spec["worse"] if worse == "worse" else spec["asis"]
    actions = table_actions(table, u)
    scores = lab_scores(actions)
    winners = argmax_set(scores)
    names = [a["name"] for a in actions]
    lines = {a["name"]: line_of(a) for a in actions}
    lo, hi = spec["range"]

    fig, (left, right) = new_figure(ncols=2, height=4.4)
    y = np.arange(len(actions))[::-1]
    extents = [0.0]
    for yi, a in zip(y, actions):
        ps, us = a["probabilities"], a["utilities"]
        gain = ps[0] * us[0]
        fail = ps[1] * us[1] if len(ps) == 2 else 0.0
        left.barh(yi + 0.17, gain, height=0.3, color=PALETTE["teal"])
        if len(ps) == 2:
            left.barh(yi - 0.17, fail, left=gain, height=0.3, color=PALETTE["terracotta"])
        if a["cost"]:
            left.barh(yi - 0.17, -a["cost"], left=gain + fail, height=0.3, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=0.8)
        net = scores[a["name"]]
        left.plot([net], [yi], "D", color=PALETTE["ink"], markersize=8, zorder=5)
        extents += [gain, gain + fail, net]
    top = max(extents)
    for yi, a in zip(y, actions):
        net = scores[a["name"]]
        tag = " (tied highest)" if a["name"] in winners and len(winners) > 1 else (" (highest)" if a["name"] in winners else "")
        left.text(top + 0.03 * (top - min(extents) + 1), yi, f"{fmt(net, 1)}{tag}", va="center", fontsize=11, color=PALETTE["ink"])
    span = top - min(extents)
    left.set_xlim(min(extents) - 0.05 * span, top + 0.62 * span)
    left.set_yticks(y, names)
    left.set_xlabel("Utility points: probability x utility, then delay cost")
    left.set_ylabel("Action")
    left.set_title(f"{spec['name'].capitalize()}: {spec['fail']} worth {fmt(u, 0)}", fontsize=11.5)
    left.grid(axis="y", alpha=0)
    fig.legend(handles=[
        Patch(facecolor=PALETTE["teal"], label="supported part"), Patch(facecolor=PALETTE["terracotta"], label="failure part"),
        Patch(facecolor="white", edgecolor=PALETTE["grey"], hatch="///", label="delay cost"),
        Line2D([0], [0], marker="D", color="none", markerfacecolor=PALETTE["ink"], markeredgecolor=PALETTE["ink"], label="expected utility"),
    ], loc="outside lower center", ncol=4, fontsize=10.5, frameon=False)

    grid = np.linspace(lo, hi, 201)
    colors = [PALETTE["navy"], PALETTE["teal"], PALETTE["gold"]]
    for color, a in zip(colors, actions):
        c, s = lines[a["name"]]
        right.plot(grid, c + s * grid, color=color, linewidth=2.4 if a["name"] in winners else 1.6)
        right.plot([u], [c + s * u], "o", color=color, markersize=8, zorder=5)
    right.axvline(u, color=PALETTE["grey"], linestyle="dashed", linewidth=1.2)
    ys = [lines[n][0] + lines[n][1] * x for n in names for x in (lo, hi)]
    pad = 0.18 * (max(ys) - min(ys))
    right.set_ylim(min(ys) - pad, max(ys) + pad)
    # Name each line at its right-hand end, nudged apart by rank so the names never meet.
    ends = sorted(names, key=lambda n: lines[n][0] + lines[n][1] * hi)
    for rank, n in enumerate(ends):
        c, s_ = lines[n]
        if table == "book" and n == "Release now":
            # Its right-hand end sits 7 points below the evidence line's, so a label there would stack on top of the evidence label;
            # name it partway along, on the empty side below the rising line.
            x_mid = lo + 0.4 * (hi - lo)
            label_point(right, x_mid, c + s_ * x_mid, n, color=colors[names.index(n)], dx=6, dy=-6, ha="left", va="top").set_bbox(BOX)
            continue
        label_point(right, hi, c + s_ * hi, n, color=colors[names.index(n)], dx=-6,
                    dy=(-8 if rank == 0 else 8) if len(ends) > 1 else 8, ha="right", va="top" if rank == 0 else "bottom").set_bbox(BOX)
    crossings = []
    for i in range(len(actions)):
        for j in range(i + 1, len(actions)):
            ci, si = lines[names[i]]
            cj, sj = lines[names[j]]
            if abs(si - sj) < 1e-12:
                continue
            ux = (cj - ci) / (si - sj)
            if lo < ux < hi:
                crossings.append((ux, names[i], names[j], ci, si, cj, sj))
    crossings.sort()
    for ux, a_, b_, ci, si, cj, sj in crossings:
        right.plot([ux], [ci + si * ux], "o", markerfacecolor="white", markeredgecolor=PALETTE["ink"], markersize=7, zorder=6)
        if table == "book":
            label_point(right, ux, ci + si * ux, f"tie at {fmt(ux, 1)}", color=PALETTE["ink"], dx=6, dy=8, ha="left", va="bottom").set_bbox(BOX)
        else:
            label_point(right, ux, ci + si * ux, f"tie at {fmt(ux, 1)}", color=PALETTE["ink"], dx=-6, dy=8, ha="right", va="bottom").set_bbox(BOX)
    right.set_xlim(lo, hi)
    right.set_xlabel(f"Utility of the {spec['fail']}")
    right.set_ylabel("Expected utility")
    right.set_title("Where the order of actions flips", fontsize=11.5)

    metrics = {n: fmt(scores[n], 1) for n in names}
    metrics["Chosen by Equation (6.3)"] = " and ".join(winners) + (" (tie)" if len(winners) > 1 else "")
    if crossings:
        metrics["Utility at which two actions tie"] = ", ".join(f"{a} and {b} at {fmt(ux, 1)}" for ux, a, b, *_ in crossings)
    else:
        metrics["Utility at which two actions tie"] = "none in the plotted range"
    sums = ". ".join(written_eu(a) for a in actions)
    if len(winners) > 1:
        verdict = (f"{' and '.join(winners)} tie at {fmt(scores[winners[0]], 1)}. Equation (6.3) returns both as maximizers; "
                   "the rule alone does not choose between them, so a person or a stated tie-breaking rule must.")
    else:
        verdict = f"{winners[0]} has the highest expected utility, so Equation (6.3) selects it."
    ranking = sorted(names, key=lambda n: -scores[n])
    cross_text = ""
    for ux, a, b, ci, si, cj, sj in crossings[:2]:
        cross_text += (f" {a} and {b} tie when {g(ci)} + {g(si)} u = {g(cj)} + {g(sj)} u, so u = {gs(cj - ci)} / {g(si - sj)} = {fmt(ux, 1)}"
                       if (si - sj) > 0 else
                       f" {a} and {b} tie when {g(ci)} + {g(si)} u = {g(cj)} + {g(sj)} u, so u = {gs(ci - cj)} / {g(sj - si)} = {fmt(ux, 1)}")
        cross_text += "."
    tie_note = (" A plain maximum in code, as in the laboratory function, returns the first maximizer in the order given, "
                "which is a convention and not a choice.") if len(winners) > 1 else ""
    interpretation = (f"{sums}. {verdict} Order from highest to lowest: {', '.join(ranking)}.{cross_text}{tie_note} "
                      "The probabilities never changed; only the declared values did.")
    steps = []
    if table == "book" and worse == "asis":
        steps = [
            "Hour price: indifferent between 0.85 now and 0.90 after an hour, so an hour costs (0.90 - 0.85) x 100 = 5.",
            "Day price: indifferent between 0.50 now and 0.90 after a day, so a day costs (0.90 - 0.50) x 100 = 40.",
            "Evidence against release: (0.97 - 0.85) x 100 - 5 = 12 - 5 = 7 units above.",
            "Escalation against release: (0.995 - 0.85) x 100 - 40 = 14.5 - 40 = (-25.5), 25.5 units below.",
            "Evidence against escalation: 7 - (-25.5) = 32.5, the same as 92.0 - 59.5 = 32.5 from the table.",
        ]
    else:
        steps = [written_eu(a) + "." for a in actions]
        steps.append(verdict)
    alt = (f"Left: for each action a gain bar, a failure bar, any hatched delay cost and a diamond at its expected utility ({spec['name']}, failure "
           f"worth {fmt(u, 0)}). Right: expected utility of each action against the utility of the failure outcome, with the current value "
           f"marked and each tie point circled.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: eliciting one number, and a probability that is shaky

SUPPORT_RANGE = {"p85": (0.85, 0.85), "p90": (0.90, 0.90), "range": (0.80, 0.90)}


def hour_price_picture(hour_cost=5, support="p85"):
    lo_s, hi_s = SUPPORT_RANGE[support]
    ranged = lo_s != hi_s
    scores_lo = lab_scores(release_actions(0, DAY_COST, hour_cost=hour_cost, release_support=lo_s)[:2])
    scores_hi = lab_scores(release_actions(0, DAY_COST, hour_cost=hour_cost, release_support=hi_s)[:2])
    evidence = scores_lo["Request evidence"]
    rel_lo, rel_hi = scores_lo["Release now"], scores_hi["Release now"]
    be_hi = SUPPORT["Request evidence"] * SUPPORTED - lo_s * SUPPORTED   # break-even at the lower support
    be_lo = SUPPORT["Request evidence"] * SUPPORTED - hi_s * SUPPORTED
    h = np.linspace(0, 20, 81)
    fig, ax = new_figure(height=4.1)
    if ranged:
        ax.fill_between(h, rel_lo, rel_hi, color=PALETTE["navy"], alpha=0.25, linewidth=0)
        ax.axvspan(be_lo, be_hi, color=PALETTE["grey"], alpha=0.18, linewidth=0)
    else:
        ax.plot(h, np.full_like(h, rel_lo), color=PALETTE["navy"])
        ax.axvline(be_lo, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    ax.plot(h, SUPPORT["Request evidence"] * SUPPORTED - h, color=PALETTE["teal"])
    ax.plot([hour_cost], [evidence], "o", color=PALETTE["teal"], markersize=8)
    if not ranged:
        ax.plot([hour_cost], [rel_lo], "o", color=PALETTE["navy"], markersize=8)
    label_point(ax, 20, rel_hi, "Release now, support 0.80 to 0.90" if ranged else "Release now", color=PALETTE["navy"], dx=-4, dy=6, ha="right")
    label_point(ax, 20, SUPPORT["Request evidence"] * SUPPORTED - 20, "Request evidence", color=PALETTE["teal"], dx=-4, dy=-8, ha="right", va="top")
    if ranged:
        label_point(ax, be_lo, 72, f"break-even {fmt(be_lo, 1)} to {fmt(be_hi, 1)}", color=PALETTE["ink"], dx=-5, dy=0, ha="right", va="center")
    else:
        label_point(ax, be_lo, 72, f"break-even {fmt(be_lo, 1)}", color=PALETTE["ink"], dx=5, dy=0, va="center")
    label_point(ax, 0.2, 99.5, "evidence wins to the left", color=PALETTE["teal"], dx=0, dy=0, va="top")
    ax.set_xlim(0, 20)
    ax.set_ylim(70, 100)
    ax.set_xlabel("Price of one hour of delay (utility points)")
    ax.set_ylabel("Expected utility")
    sup_text = "0.80 to 0.90" if ranged else fmt(lo_s, 2)
    ax.set_title(f"Hour priced at {fmt(hour_cost, 0)}; release support {sup_text}", fontsize=11.5)

    release_text = f"{fmt(rel_lo, 1)} to {fmt(rel_hi, 1)}" if ranged else fmt(rel_lo, 1)
    be_text = f"{fmt(be_lo, 1)} to {fmt(be_hi, 1)}" if ranged else fmt(be_lo, 1)
    if ranged:
        if evidence > rel_hi + 1e-9:
            chosen = "Request evidence (whole range)"
            verdict = (f"Request evidence scores 97.0 - {fmt(hour_cost, 0)} = {fmt(evidence, 1)}, above even the best release "
                       f"({fmt(rel_hi, 1)}), so the decision is robust to the shaky support probability and it can proceed.")
            short = f"Evidence {fmt(evidence, 1)} is above the whole release range, so the choice is robust."
        elif evidence < rel_lo - 1e-9:
            chosen = "Release now (whole range)"
            verdict = (f"Request evidence scores {fmt(evidence, 1)}, below even the worst release ({fmt(rel_lo, 1)}), so releasing now wins "
                       "across the whole range.")
            short = f"Evidence {fmt(evidence, 1)} is below the whole release range, so releasing now wins."
        else:
            chosen = "not robust: depends on the support probability"
            tie_support = evidence / SUPPORTED
            verdict = (f"Request evidence scores 97.0 - {fmt(hour_cost, 0)} = {fmt(evidence, 1)}, inside the release range {release_text}, so the "
                       f"ranges overlap and the choice depends on the support probability: they tie at {fmt(evidence, 1)} / 100 = {fmt(tie_support, 2)}. "
                       "That is the exact question a person has to settle, or a way to sharpen the estimate.")
            short = (f"Evidence {fmt(evidence, 1)} is inside {release_text}: not robust; they tie at support {fmt(tie_support, 2)}.")
    else:
        if math.isclose(evidence, rel_lo, abs_tol=1e-9):
            verdict = ("The two actions tie exactly, so Equation (6.3) has two maximizers and the price of an hour "
                       "sits on the threshold. The person who owns the values has to say which side they are on.")
            chosen = "tie"
        elif evidence > rel_lo:
            verdict = f"Request evidence wins because {fmt(hour_cost, 0)} is below the break-even price."
            chosen = "Request evidence"
        else:
            verdict = f"Release now wins because {fmt(hour_cost, 0)} is above the break-even price."
            chosen = "Release now"
    if not ranged:
        short = verdict
    if hour_cost == 0:
        short += " With an hour priced at 0, evidence dominates outright."
        verdict += (f" With no delay cost whatever, the evidence action scores 97.0 against at most {fmt(rel_hi, 1)}, so it dominates outright "
                    "and no opinion about the value of an hour changes the ranking.")
    metrics = {
        "Release now": release_text,
        "Request evidence": fmt(evidence, 1),
        "Break-even hour price": be_text,
        "Chosen": chosen,
    }
    if ranged:
        calc = (f"Break-even price = 0.97 x 100 - s x 100 runs from 97.0 - 90.0 = {fmt(be_lo, 1)} at s = 0.90 to 97.0 - 80.0 = {fmt(be_hi, 1)} at s = 0.80 points per hour. "
                f"Release now scores 0.80 x 100 = {fmt(rel_lo, 1)} to 0.90 x 100 = {fmt(rel_hi, 1)}.")
    else:
        calc = (f"Break-even price = 0.97 x 100 - {fmt(lo_s, 2)} x 100 = 97.0 - {fmt(lo_s * SUPPORTED, 1)} = {fmt(be_lo, 1)} points per hour. "
                f"Release now scores {fmt(lo_s, 2)} x 100 = {fmt(rel_lo, 1)}.")
    interpretation = (f"{calc} At {fmt(hour_cost, 0)} points, request evidence scores 97.0 - {fmt(hour_cost, 0)} = {fmt(evidence, 1)}. {verdict} "
                      "Only one question needs an answer from a person: is an hour worth more or less than the break-even price?")
    steps = [
        f"Request evidence: 0.97 x 100 - {fmt(hour_cost, 0)} = {fmt(evidence, 1)}.",
        (f"Release now: s x 100 for s from 0.80 to 0.90 = {fmt(rel_lo, 1)} to {fmt(rel_hi, 1)}." if ranged else f"Release now: {fmt(lo_s, 2)} x 100 = {fmt(rel_lo, 1)}."),
        (f"Break-even hour price: 97.0 - s x 100 = {fmt(be_lo, 1)} to {fmt(be_hi, 1)}." if ranged else f"Break-even hour price: 97.0 - {fmt(lo_s * SUPPORTED, 1)} = {fmt(be_lo, 1)}."),
        short,
    ]
    alt = (f"Expected utility against the price of an hour of delay: a falling line for requesting evidence and "
           f"{'a shaded band from 80 to 90' if ranged else 'a flat line at ' + fmt(rel_lo, 1)} for releasing now; "
           f"the break-even is {be_text} points and the current price {fmt(hour_cost, 0)} is marked.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: risk is the shape of the utility curve

SHAPES = {
    "sqrt": ("square root", lambda x: np.sqrt(x), lambda u: u ** 2, "sqrt"),
    "linear": ("straight line", lambda x: x, lambda u: u, ""),
    "square": ("square", lambda x: x ** 2, lambda u: np.sqrt(u), "square"),
}
SURE = 40.0  # a sure payoff used only to show that the curves disagree about a comparison


def st_petersburg_picture(shape):
    name, u, inverse, _ = SHAPES[shape]
    n = np.arange(1, 21)
    terms = 2.0 ** (-n) * u(2.0 ** n)
    partial = np.cumsum(terms)
    fig, ax = new_figure(height=4.3)
    colors = {"sqrt": PALETTE["teal"], "linear": PALETTE["navy"], "square": PALETTE["gold"]}
    for key in ("sqrt", "linear", "square"):
        _, uk, _, _ = SHAPES[key]
        curve = np.cumsum(2.0 ** (-n) * uk(2.0 ** n))
        ax.plot(n, curve, color=colors[key], alpha=1.0 if key == shape else 0.45, linewidth=2.6 if key == shape else 1.6,
                marker="o", markersize=4.5 if key == shape else 3)
    ax.set_yscale("log")
    ax.set_ylim(0.5, 4e6)
    ax.set_xlim(0.5, 22.5)
    ax.set_xlabel("Number of terms of the gamble added (payoff 2^k with probability 2^(-k))")
    ax.set_ylabel("Expected utility so far (log scale)")
    ax.set_xticks([1, 5, 10, 15, 20])
    labels = {"sqrt": "square root", "linear": "straight line", "square": "square"}
    ax.legend([Line2D([0], [0], color=colors[k], alpha=1.0 if k == shape else 0.45, linewidth=2.6 if k == shape else 1.6, marker="o", markersize=4)
               for k in ("sqrt", "linear", "square")],
              [labels[k] + (" (chosen)" if k == shape else "") for k in ("sqrt", "linear", "square")], loc="upper left", fontsize=10.5, frameon=False)
    ax.set_title(f"Unbounded mean payoff, utility shape: {name}", fontsize=11.5)
    after20 = float(partial[-1])
    converges = shape == "sqrt"
    limit = 1 + math.sqrt(2)
    ce = limit ** 2
    metrics = {
        "Mean payoff": "unbounded (each term adds 1, so the sum grows without limit)",
        "Expected utility of the first 20 terms": fmt(after20, 3) if shape == "sqrt" else (fmt(after20, 0)),
        "Expected utility, all terms": fmt(limit, 3) if converges else "unbounded (the series grows without limit)",
        "Certainty equivalent": fmt(ce, 2) if converges else "undefined (no finite sure payoff matches)",
    }
    r = 1 / math.sqrt(2)
    if shape == "sqrt":
        calc = (f"Each term is 2^(-k) x sqrt(2^k) = {fmt(r, 4)}^k, so the sum is {fmt(r, 4)} / (1 - {fmt(r, 4)}) = {fmt(limit, 3)} = 1 + sqrt(2). "
                f"The certainty equivalent is {fmt(limit, 3)} x {fmt(limit, 3)} = {fmt(ce, 2)} = 3 + 2 sqrt(2), "
                "a finite sure payoff although the mean payoff is unbounded.")
        steps = [
            "Payoff 2^k with probability 2^(-k), k = 1, 2, 3, ...; each term adds 1 to the mean payoff, so the mean is unbounded.",
            f"With u = sqrt, a term is 2^(-k) x sqrt(2^k) = {fmt(r, 4)}^k.",
            f"The geometric series sums to {fmt(r, 4)} / (1 - {fmt(r, 4)}) = {fmt(limit, 3)}.",
            f"Certainty equivalent = {fmt(limit, 3)}^2 = {fmt(ce, 2)} payoff units under this declared utility.",
        ]
    elif shape == "linear":
        calc = (f"Each term is 2^(-k) x 2^k = 1, so the first 20 terms add 1 + 1 + ... + 1 = {fmt(after20, 0)} (20 terms) and the sum has no limit: "
                "with a straight-line utility the expected utility is unbounded and no finite sure payoff has the same value.")
        steps = [
            "Payoff 2^k with probability 2^(-k); with u = payoff a term is 2^(-k) x 2^k = 1.",
            f"The first 20 terms sum to 1 + 1 + ... + 1 = {fmt(after20, 0)}.",
            "The partial sums grow without bound, so the expected utility does not exist as a number.",
        ]
    else:
        calc = (f"Each term is 2^(-k) x (2^k)^2 = 2^k, so the first 20 terms add 2 + 4 + 8 + ... + 2^20 = {fmt(after20, 0)} (20 terms) and the sum has no limit: "
                "the expected utility is unbounded and the series does not converge.")
        steps = [
            "Payoff 2^k with probability 2^(-k); with u = payoff squared a term is 2^(-k) x 4^k = 2^k.",
            f"The first 20 terms sum to 2 + 4 + 8 + ... + 2^20 = {fmt(after20, 0)}.",
            "The partial sums double with every term, so the expected utility does not exist as a number.",
        ]
    note = ("Slower growth alone is not enough to ensure convergence; this particular series supplies the check for the square root, and it fails for the other two curves."
            if converges else "Whether the utility average exists has to be checked for each curve; here it does not.")
    interpretation = f"{calc} {note}"
    alt = (f"Expected utility of the first terms of an unbounded gamble on a log scale for three curves; the {name} curve is highlighted. "
           f"{'It levels off near 2.414.' if converges else 'It keeps rising without limit.'}")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


def certainty_picture(shape="sqrt", gamble="half"):
    if gamble == "petersburg":
        return st_petersburg_picture(shape)
    name, u, inverse, _ = SHAPES[shape]
    q = {"half": 0.5, "eighty": 0.8}[gamble]
    top = 100.0
    expected_payoff = q * top
    expected_utility = q * float(u(top)) + (1 - q) * float(u(0.0))
    ce = float(inverse(expected_utility))
    gap = expected_payoff - ce
    x = np.linspace(0, top, 201)
    scale = float(u(top))
    fig, ax = new_figure(height=4.3)
    ax.plot(x, u(x) / scale, color=PALETTE["teal"])
    ax.plot([0, top], [0, 1], linestyle=":", color=PALETTE["grey"], linewidth=1.4)
    level = expected_utility / scale
    ax.plot([min(ce, expected_payoff), max(ce, expected_payoff)], [level, level], linestyle="dashed", color=PALETTE["gold"], linewidth=1.6)
    ax.plot([expected_payoff], [level], "s", color=PALETTE["navy"], markersize=8)
    ax.plot([ce], [level], "o", color=PALETTE["terracotta"], markersize=8)
    # Labels carry no background box, so they never erase part of a curve; they sit on the empty side of it.
    # A bending-down curve lies above the dotted diagonal, a bending-up curve below it.
    down = shape == "sqrt"
    if math.isclose(ce, expected_payoff, abs_tol=1e-9):
        label_point(ax, ce, level, f"certainty equivalent\n= mean = {fmt(ce, 1)}", color=PALETTE["ink"], dx=-4, dy=14,
                    ha="right", va="bottom")
    elif down:
        label_point(ax, ce, level, f"certainty\nequivalent {fmt(ce, 1)}", color=PALETTE["terracotta"], dx=max(0, 30 - ce), dy=14,
                    ha="right", va="bottom")
        label_point(ax, expected_payoff, level, f"mean payoff {fmt(expected_payoff, 1)}", color=PALETTE["navy"], dx=0, dy=-14,
                    ha="left", va="top")
    else:
        label_point(ax, ce, level, f"certainty\nequivalent {fmt(ce, 1)}", color=PALETTE["terracotta"], dx=-4, dy=-14,
                    ha="left", va="top")
        label_point(ax, expected_payoff, level, f"mean payoff {fmt(expected_payoff, 1)}", color=PALETTE["navy"], dx=-4, dy=14,
                    ha="right", va="bottom")
    ax.set_xlim(0, 112)
    ax.set_xticks(range(0, 101, 20))
    ax.set_ylim(-0.03, 1.08)
    ax.set_xlabel("Payoff (constructed units)")
    ax.set_ylabel("Utility, rescaled so u(0) = 0 and u(100) = 1")
    ax.set_title(f"Utility shape: {name}; gamble pays 100 with probability {fmt(q, 1)}", fontsize=11.5)
    if shape == "sqrt":
        calc = (f"E[u] = {fmt(q, 1)} x sqrt(100) + {fmt(1 - q, 1)} x sqrt(0) = {fmt(expected_utility, 1)}, "
                f"so CE = {fmt(expected_utility, 1)} x {fmt(expected_utility, 1)} = {fmt(ce, 1)}")
    elif shape == "linear":
        calc = (f"E[u] = {fmt(q, 1)} x 100 + {fmt(1 - q, 1)} x 0 = {fmt(expected_utility, 1)}, so CE = {fmt(ce, 1)}")
    else:
        calc = (f"E[u] = {fmt(q, 1)} x 100 x 100 + {fmt(1 - q, 1)} x 0 = {fmt(expected_utility, 0)}, "
                f"so CE = sqrt({fmt(expected_utility, 0)}) = {fmt(ce, 2)}")
    if gap > 1e-9:
        meaning = (f"The agent would trade the gamble for a guaranteed {fmt(ce, 1)}, giving up {fmt(gap, 1)} of mean payoff "
                   "to remove the variance. That gap is the price of avoiding risk under this curve.")
    elif gap < -1e-9:
        meaning = (f"The certainty equivalent is above the mean, so the gap {fmt(gap, 2)} is negative: this upward-bending "
                   "curve values the gamble more than its average, which is what seeking risk means here.")
    else:
        meaning = "The gap is zero: a straight-line utility is indifferent to risk."
    sure_wins = ce < SURE
    sure_text = (f" Every curve here ranks payoffs the same way, more being better (Equation (6.1)), yet they disagree about this gamble: "
                 f"a sure {fmt(SURE, 0)} beats it exactly when CE < {fmt(SURE, 0)}, and CE = {fmt(ce, 1)}, so "
                 f"{'the sure ' + fmt(SURE, 0) + ' is preferred' if sure_wins else 'the gamble is preferred'}.")
    metrics = {
        "Mean payoff": fmt(expected_payoff, 1),
        "E[u(Y)] for this curve (not comparable across curves)": fmt(expected_utility, 2),
        "Certainty equivalent": fmt(ce, 2),
        "Mean minus certainty equivalent": fmt(gap, 2),
        f"A sure {fmt(SURE, 0)} against the gamble": "sure payoff preferred" if sure_wins else "gamble preferred",
    }
    interpretation = (f"Mean payoff = {fmt(q, 1)} x 100 = {fmt(expected_payoff, 1)}. {calc}. Mean minus certainty "
                      f"equivalent = {fmt(expected_payoff, 1)} - {fmt(ce, 2)} = {fmt(gap, 2)}. {meaning}{sure_text}")
    steps = [
        f"Mean payoff = {fmt(q, 1)} x 100 + {fmt(1 - q, 1)} x 0 = {fmt(expected_payoff, 1)}.",
        f"{calc}.",
        f"Mean minus certainty equivalent = {fmt(expected_payoff, 1)} - {fmt(ce, 2)} = {fmt(gap, 2)}.",
        f"A sure {fmt(SURE, 0)} is preferred when CE < {fmt(SURE, 0)}: CE = {fmt(ce, 1)}, so "
        f"{'the sure payoff' if sure_wins else 'the gamble'} wins.",
    ]
    alt = (f"A {name} utility curve against payoff with the mean payoff {fmt(expected_payoff, 1)} and the certainty equivalent {fmt(ce, 1)} "
           f"marked on one dashed level; a dotted diagonal shows a straight line for comparison.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: declining is an action with a price

CASES = 100
CONFIDENCE = 0.5 + 0.005 * (np.arange(CASES) + 0.5)  # constructed: 0.5025, 0.5075, ..., 0.9975


def lab_answers(p, wrong, decline):
    """The laboratory's evaluate() chooses between answering and declining for one case."""
    actions = [
        {"name": "answer", "probabilities": [float(p), 1 - float(p)], "utilities": [1.0, float(wrong)], "cost": 0},
        {"name": "decline", "probabilities": [1.0], "utilities": [float(decline)], "cost": 0},
    ]
    return evaluate({"actions": actions})["metrics"]["selected_action"] == "answer"


def coverage_picture(wrong=-4, decline=0):
    wrong, decline = float(wrong), float(decline)
    threshold = (decline - wrong) / (1 - wrong)
    answered = np.array([lab_answers(p, wrong, decline) for p in CONFIDENCE])
    closed_form = CONFIDENCE > threshold
    if not np.array_equal(answered, closed_form):
        raise AssertionError("laboratory decision disagrees with the closed-form threshold")
    n = int(answered.sum())
    coverage = n / CASES
    risk = float(np.mean(1 - CONFIDENCE[answered])) if n else None
    per_case = float(np.mean(np.where(answered, CONFIDENCE + (1 - CONFIDENCE) * wrong, decline)))
    order = np.argsort(-CONFIDENCE)
    k = np.arange(1, CASES + 1)
    curve_cov = k / CASES
    curve_risk = np.cumsum(1 - CONFIDENCE[order]) / k

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    p = np.linspace(0.5, 1, 101)
    left.plot(p, p + (1 - p) * wrong, color=PALETTE["teal"])
    left.plot(p, np.full_like(p, decline), color=PALETTE["terracotta"])
    label_point(left, 0.9, 0.9 + 0.1 * wrong, "answer", color=PALETTE["teal"], dx=-8, dy=6, ha="right")
    label_point(left, 1.0, decline, "decline", color=PALETTE["terracotta"], dx=-4, dy=-6, ha="right", va="top")
    if 0.5 <= threshold <= 1:
        left.axvline(threshold, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
        near_left = threshold < 0.6
        label_point(left, threshold, wrong * 0.5 + 0.25, f"t = {fmt(threshold, 2)}", dx=5 if near_left else -5, dy=0,
                    ha="left" if near_left else "right", va="center")
    else:
        label_point(left, 0.75, wrong * 0.5 + 0.25, f"t = {fmt(threshold, 2)} is below every case", dx=0, dy=0, ha="center", va="center")
    left.set_xlabel("Confidence p that the answer is correct")
    left.set_ylabel("Expected utility of the case")
    left.set_ylim(min(wrong * 0.5 - 0.3, decline - 0.3), 1.15)
    left.set_title("Answer when its expected utility is higher", fontsize=11.5)

    right.plot(curve_cov, curve_risk, color=PALETTE["navy"])
    right.plot([1.0], [curve_risk[-1]], "s", color=PALETTE["grey"], markersize=7)
    if n:
        right.plot([coverage], [risk], "o", color=PALETTE["teal"], markersize=9)
    if n == CASES:
        label_point(right, 1.0, curve_risk[-1], f"chosen: answer all, error {fmt(curve_risk[-1], 3)}", color=PALETTE["teal"], dx=-6, dy=8, ha="right")
    else:
        label_point(right, 1.0, curve_risk[-1], f"answer all: error {fmt(curve_risk[-1], 3)}", color=PALETTE["grey"], dx=-6, dy=8, ha="right")
        if n:
            label_point(right, coverage, risk, f"chosen\ncoverage {fmt(coverage, 2)}, error {fmt(risk, 3)}", color=PALETTE["teal"],
                        dx=6 if coverage < 0.5 else -6, dy=-10, ha="left" if coverage < 0.5 else "right", va="top",
                        ).set_bbox({"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9})
    right.set_xlim(0, 1.04)
    right.set_ylim(0, 0.3)
    right.set_xlabel("Coverage (share of the 100 cases answered)")
    right.set_ylabel("Expected error rate among answered cases")
    right.set_title("Risk against coverage", fontsize=11.5)

    risk_text = fmt(risk, 3) if risk is not None else "undefined (no case is answered)"
    metrics = {
        "Answer threshold t": fmt(threshold, 2),
        "Cases answered": f"{n} of {CASES}",
        "Coverage": fmt(coverage, 2),
        "Expected error rate when answering": risk_text,
        "Expected utility per case": fmt(per_case, 3),
    }
    calc = (f"Answer when p x 1 + (1 - p) x {signed(wrong, 0)} > {signed(decline, 1)}, that is when p > t = "
            f"({fmt(decline, 1)} - {signed(wrong, 0)}) / (1 - {signed(wrong, 0)}) = {fmt(decline - wrong, 1)} / {fmt(1 - wrong, 0)} = {fmt(threshold, 2)}.")
    if n == CASES:
        detail = (f" Every constructed case has p above {fmt(threshold, 2)}, so coverage is 1.00 and the expected error rate is "
                  f"1 - (0.5025 + 0.9975) / 2 = {fmt(risk, 3)}.")
        detail_step = f"All 100 cases clear t: coverage 1.00, error 1 - (0.5025 + 0.9975) / 2 = {fmt(risk, 3)}."
    elif n:
        lo = CONFIDENCE[answered].min()
        detail = (f" The {n} cases from p = {lo:.4f} to 0.9975 are answered, so coverage = {n}/100 = {fmt(coverage, 2)} and their "
                  f"expected error rate is 1 - ({lo:.4f} + 0.9975) / 2 = {risk_text}.")
        detail_step = f"{n} cases (p from {lo:.4f} to 0.9975) are answered: coverage {n}/100 = {fmt(coverage, 2)}, error 1 - ({lo:.4f} + 0.9975) / 2 = {risk_text}."
    else:
        detail = " No case clears the threshold, so coverage is 0 and the error rate among answered cases is undefined."
        detail_step = "No case clears t: coverage is 0 and the error rate is undefined."
    interpretation = (calc + detail + " A more expensive wrong answer raises t and lowers coverage; a more expensive "
                      "decline lowers t and raises coverage. The value attached to declining picks the point on the curve.")
    steps = [
        f"Answer: p x 1 + (1 - p) x {signed(wrong, 0)}; decline: {signed(decline, 1)} for certain.",
        f"Threshold t = ({fmt(decline, 1)} - {signed(wrong, 0)}) / (1 - {signed(wrong, 0)}) = {fmt(threshold, 2)}.",
        detail_step,
    ]
    alt = (f"Left: expected utility of answering and of declining against confidence, with the threshold {fmt(threshold, 2)} marked. "
           f"Right: expected error rate against coverage with the chosen point at coverage {fmt(coverage, 2)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 6,
    "title": "The Price of a Choice",
    "subtitle": "Probabilities say what an action is likely to lead to; utilities say what those outcomes are worth. A decision needs both.",
    "summary": (
        "These four demonstrations follow the chapter's document controller. It must choose among releasing a report now, "
        "requesting more evidence, and escalating to a person. Each demonstration changes one declared value and shows "
        "which comparison moves and which stays fixed, including the notebook's own decision cases, a probability that is only known "
        "within a range, and a gamble whose mean payoff has no limit."
    ),
    "ask_skill": {
        "prompt": (
            "Help me write a decision table for my controller: one row per action, including asking for evidence and escalating, with the "
            "probabilities and the utilities in separate columns. Compute the expected utility of each action, then find the one value "
            "whose plausible change would reverse the winner."
        ),
    },
    "demos": [
        {
            "id": "C06-D01",
            "title": "Three actions, one rule, and where the order flips",
            "question": "If the probabilities stay fixed, which value change flips the winner or the order, and by how much does each action's score depend on it?",
            "equations": [EQ_EU, EQ_ARGMAX],
            "symbols": (
                "a is an action, y an outcome (a supported release or its failure), p(y | a) the probability of outcome y "
                "under action a, and u(y) its declared utility. In Table 6.1 a supported release is worth 100 and delay subtracts the same "
                "amount from every outcome, which is the same as subtracting it once from the average because the "
                "probabilities add to one. The arg max picks the action with the largest EU(a), the expected utility of action a. In the right panel u "
                "is the utility of the failure outcome, the one value that changes along the horizontal axis. In the notebook default, review is worth 2 "
                "and abstaining 0 for certain; in the transfer case retry pays 8 or the failure value at cost 1 and escalating pays 1."
            ),
            "prediction": "In the book's table, make an unsupported release worth -400 instead of 0 (day of delay 40). Which action loses the most, and does the winner change?",
            "prediction_options": [
                "Release now loses most (85 to 25); evidence still wins, and escalation overtakes release",
                "Request evidence loses most and escalation wins",
                "Nothing changes, because the probabilities did not move",
            ],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "Release now falls from 85.0 to 25.0, evidence from 92.0 to 80.0 and escalation from 59.5 to 57.5, so evidence still wins and escalation passes release.",
                "incorrect": "Choose the book table and 'Made worse': release now falls by 60 (85.0 to 25.0), evidence by 12 and escalation by 2, so evidence still wins and escalation passes release even though no probability moved.",
            },
            "explanation": (
                "Each action's expected utility multiplies each outcome's worth by its probability and adds the products, then Equation (6.3) takes the "
                "largest. The left bars show the two columns meeting: a gain part, a failure part and any delay cost. The probabilities never move in this "
                "demonstration; only the value of a failure does, and the right panel shows each action's expected utility as a straight line in that value. "
                "Where two lines cross, the order flips, which is the one question a person has to answer. In the notebook's transfer case the two actions tie "
                "exactly, so the rule alone does not choose."
            ),
            "application": (
                "Before trusting an automated choice, write the table: one row per action, including asking for evidence and "
                "handing the decision to a person. Then check whether a change in a value you are unsure of changes the winner."
            ),
            "assumptions": (
                "One decision, two mutually exclusive outcomes per action (one for review and abstaining), and utilities on one shared scale. The probabilities "
                "and utilities are constructed teaching values from Table 6.1 and the notebook, not estimates for any real controller. The 'made worse' failure "
                "values are the book's -400 and the notebook's -100; the transfer value -24 is defined for this reader as double the supplied value. "
                "Expected utility compares actions; it does not say whose values the numbers represent, and a large negative utility is not the same as a hard permission boundary."
            ),
            "check": "In the book's table with an unsupported release worth -400 and a day costing 40, what does releasing now score?",
            "answer": "0.85 x 100 + 0.15 x (-400) = 85 - 60 = 25. Requesting evidence scores 92 - 12 = 80, so it still wins, and escalation (57.5) now beats releasing now.",
            "provenance": "Constructed example: the book's Table 6.1 values, and the notebook's default, changed and transfer decision cases, computed with the laboratory's expected-utility function.",
            "source_section": "The decision rule",
            "source_anchor": "the-decision-rule",
            "misconception": {
                "title": "Folding belief into worth",
                "text": (
                    "The probability column and the value column come from different places. An agent that treats a low-probability outcome as low-value, or a "
                    "catastrophic outcome as merely unlikely, has folded belief into worth; here the probabilities do not move while the value of a failure alone "
                    "changes the order."
                ),
            },
            "scope_note": {
                "text": (
                    "All values in Table 6.1 are constructed for teaching. Nothing here says where a utility function should come from, only what follows once one exists."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "table", "label": "Decision table", "values": ["book", "lab", "transfer"], "default": "book",
                 "value_labels": ["Book Table 6.1: release, evidence, escalate", "Notebook default: release, review, abstain",
                                  "Notebook transfer: retry or escalate"]},
                {"key": "worse", "label": "Value of the failure outcome", "values": ["asis", "worse"], "default": "asis",
                 "value_labels": ["As supplied (0, -50 or -12)", "Made worse (-400, -100 or -24)"]},
            ],
            "function": "table_picture",
        },
        {
            "id": "C06-D02",
            "title": "Elicit one number: the price of an hour",
            "question": "Between releasing now and requesting evidence, what single number decides the choice, and what if the support probability is itself shaky?",
            "equations": [EQ_ARGMAX, EQ_EU],
            "symbols": (
                "EU(a) is the expected utility of action a. Releasing now succeeds with the chosen support probability; "
                "requesting evidence succeeds with probability 0.97 but costs one hour, priced in utility points. An "
                "unsupported release is worth 0 and a supported one 100. 'Range' means the support probability is only known to lie between 0.80 and 0.90, "
                "so releasing now has a range of expected utilities, 80 to 90, instead of one number."
            ),
            "prediction": "With release support 0.85, if an hour of delay is worth exactly 12 points, does Equation (6.3) choose releasing now, requesting evidence, or neither because they tie?",
            "prediction_options": ["Releasing now", "Requesting evidence", "Neither: they tie exactly at 85.0"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "Request evidence scores 97 - 12 = 85 and releasing now scores 0.85 x 100 = 85: an exact tie, which Equation (6.3) does not break.",
                "incorrect": "Set the hour price to 12 with release support 0.85: request evidence scores 97 - 12 = 85 and releasing now 85, an exact tie that the rule does not break.",
            },
            "explanation": (
                "Requesting evidence scores 97 minus the price of an hour; releasing now scores 100 times its support "
                "probability. The lines cross at the break-even price. A person does not need to state a whole utility "
                "function, only which side of that one threshold they are on. When the support probability is shaky, release now has a range of "
                "scores: if the evidence line sits above the whole range, or below it, the decision is robust and the analysis can stop; if it sits inside, "
                "the analysis has located the question a person has to settle."
            ),
            "application": (
                "When a decision depends on a value nobody has written down, compute the threshold at which the decision "
                "flips and ask the person responsible which side they are on. That question is answerable; asking what an "
                "outcome is worth in the abstract usually is not. Then vary each shaky input across the range anyone would defend and report whether the choice changes."
            ),
            "assumptions": (
                "Two actions, utilities on the Table 6.1 scale, and delay priced additively. The 0.85, 0.90 and 0.97 support "
                "probabilities are constructed, and the range 0.80 to 0.90 is an illustrative uncertainty defined for this reader. A tie is reported as a tie, "
                "because Equation (6.3) does not break ties. A range of scores is not a probability distribution over the support."
            ),
            "check": "If releasing now had support probability 0.90, what hour price would make the two actions tie?",
            "answer": "97 - 90 = 7 points. Below 7 requesting evidence wins; above 7 releasing now wins.",
            "provenance": "Constructed example: the book's Table 6.1 values, computed with the laboratory's expected-utility function; the hour prices 0 and 15 and the support range are defined for this reader.",
            "source_section": "Eliciting one number",
            "source_anchor": "eliciting-one-number",
            "misconception": {
                "title": "Asking people what outcomes are worth",
                "text": (
                    "Do not ask people what outcomes are worth. Compute the threshold at which the decision changes, then ask which side of it they are on: "
                    "the first question is unanswerable and the second is ordinary."
                ),
            },
            "scope_note": {
                "text": (
                    "Two agents can hold the same probability with very different confidence, and Equation (6.2) cannot tell them apart, because a "
                    "probability enters the average as a weight and carries no record of how it was obtained."
                ),
                "source_section": "When the probability itself is shaky",
            },
            "controls": [
                {"key": "hour_cost", "label": "Price of an hour of delay", "values": [0, 5, 12, 15], "default": 5},
                {"key": "support", "label": "Support probability when releasing now", "values": ["p85", "p90", "range"], "default": "p85",
                 "value_labels": ["0.85", "0.90", "Shaky: anywhere from 0.80 to 0.90"]},
            ],
            "function": "hour_price_picture",
        },
        {
            "id": "C06-D03",
            "title": "Risk is the shape of the utility curve",
            "question": "How much mean payoff would an agent give up to replace a gamble with a sure amount, and what if the gamble's mean payoff has no limit?",
            "equations": [EQ_CE, EQ_EU, EQ_ORDER],
            "symbols": (
                "Y is the payoff of a gamble that pays 100 with the chosen probability and 0 otherwise, or, in the last gamble, 2^k with probability 2^(-k) for "
                "k = 1, 2, 3 and so on. u is the utility curve, E[u(Y)] its probability-weighted average, and CE the certainty equivalent: the sure payoff "
                "whose utility equals that average. The plot rescales utility to run from 0 to 1, which does not move CE. Equation (6.1) says only that "
                "a larger payoff gets a larger utility; all three curves do that."
            ),
            "prediction": "For a curve that bends down, is the certainty equivalent above or below the mean payoff of 50?",
            "prediction_options": ["Below the mean: 25", "Equal to the mean: 50", "Above the mean: 70.7"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "With a square-root utility E[u] = 0.5 x 10 = 5, so CE = 25: the agent gives up 25 of mean payoff to remove the variance.",
                "incorrect": "Choose the square-root curve with the gamble that pays 100 half the time: E[u] = 5, so CE = 25, below the mean of 50. The straight line gives 50 and the square gives about 70.7.",
            },
            "explanation": (
                "Average the utilities, not the payoffs, then ask which sure payoff has that utility. A curve that bends "
                "down puts the certainty equivalent below the mean; a straight line puts it at the mean; a curve that bends "
                "up puts it above. The gap is a number in payoff units, not a temperament. All three curves agree on the order of payoffs, so Equation (6.1) cannot "
                "tell them apart; they disagree about gambles. The unbounded gamble shows the average must be checked: with the square-root curve the series converges "
                "to 1 + sqrt(2) and the certainty equivalent is finite, while for the other curves it does not converge."
            ),
            "application": (
                "When a team says a system should be cautious, ask for the curve or for one certainty equivalent. A stated "
                "gap such as 25 on a 50 mean can be checked and argued about; the word cautious cannot."
            ),
            "assumptions": (
                "Constructed payoffs and probabilities. The square-root and square curves "
                "are illustrations of bending down and bending up, not elicited preferences. One certainty equivalent is "
                "consistent with risk aversion but does not prove the whole curve is concave. The certainty equivalent is a guaranteed payoff under the declared "
                "utility, not an observed willingness to pay. The sure 40 in the interpretation is only a comparison value."
            ),
            "check": "With a square-root utility and a gamble paying 100 with probability 0.8, what is the certainty equivalent?",
            "answer": "E[u] = 0.8 x 10 = 8, so CE = 8 x 8 = 64, which is 16 below the mean payoff of 80.",
            "provenance": "Constructed example: the chapter's worked certainty equivalent (100 or 0 with equal chance), one changed probability and the chapter's unbounded gamble with a square-root utility (1 + sqrt(2), about 2.414, and a certainty equivalent of about 5.83).",
            "source_section": "A worked certainty equivalent",
            "source_anchor": "a-worked-certainty-equivalent",
            "misconception": {
                "title": "Pricing a gamble by its mean payoff",
                "text": (
                    "An unbounded expected payoff does not determine the gamble's utility, so the game is not worth any finite price; and one certainty-equivalent "
                    "comparison is consistent with risk aversion but does not establish global concavity."
                ),
            },
            "scope_note": {
                "text": (
                    "The representation in Equation (6.1) requires complete and transitive comparisons, and real preferences violate both. A cycle such as "
                    "speed over accuracy, accuracy over cost and cost over speed cannot be summarized by any ranking."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "shape", "label": "Utility curve", "values": ["sqrt", "linear", "square"], "default": "sqrt",
                 "value_labels": ["Bends down: square root", "Straight line", "Bends up: square"]},
                {"key": "gamble", "label": "Gamble", "values": ["half", "eighty", "petersburg"], "default": "half",
                 "value_labels": ["Pays 100 with probability 0.5", "Pays 100 with probability 0.8", "Pays 2^k with probability 2^(-k), without limit"]},
            ],
            "function": "certainty_picture",
        },
        {
            "id": "C06-D04",
            "title": "Declining is an action with a price",
            "question": "How does the value placed on declining decide how many cases an agent answers and how often it is wrong?",
            "equations": [EQ_ARGMAX, EQ_EU],
            "symbols": (
                "For each case the agent compares two actions. Answer: utility 1 if correct, w (the chosen wrong-answer "
                "utility) if not, with p the probability the answer is correct. Decline: d (the chosen utility of declining) for certain. "
                "Coverage is the share of cases answered, and the error rate is measured only over answered cases."
            ),
            "prediction": "Make a wrong answer cost 9 instead of 4. Does coverage go up or down, and what happens to the error rate?",
            "prediction_options": [
                "Coverage falls to 0.20 and the error rate falls to 0.050",
                "Coverage rises and the error rate rises",
                "Coverage stays at 0.40",
            ],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "The threshold rises from 0.80 to 0.90, so 20 cases are answered instead of 40 and the error rate among them falls from 0.100 to 0.050.",
                "incorrect": "Compare wrong answer -4 with -9 at declining 0: the threshold goes from 0.80 to 0.90, so coverage falls from 0.40 to 0.20 and the error rate from 0.100 to 0.050.",
            },
            "explanation": (
                "Answering wins when p x 1 + (1 - p) x w exceeds the value of declining d, which happens when p is above "
                "the threshold t = (d - w) / (1 - w). Each threshold picks one point on the risk and coverage curve, so the same agent "
                "can be reported at very different error rates depending on the price of declining. Raising the cost of declining raises coverage; lowering it hands more away."
            ),
            "application": (
                "When a system reports an error rate, ask for its coverage and for the value it assigns to declining. Two "
                "error rates at different coverage describe different services, and the price of declining is what chose between them."
            ),
            "assumptions": (
                "One hundred constructed cases whose confidences are spread evenly from 0.5025 to 0.9975 and assumed to be "
                "calibrated, so a case with confidence p is correct with probability p. Real confidence scores need not be "
                "calibrated; the error rates shown are expected values under that assumption, not observed rates. Because the confidences are "
                "spread evenly, the risk and coverage curve is a straight line, and a real system's curve would take its shape from its real confidences."
            ),
            "check": "With a wrong answer worth -4 and declining worth 0, what is the answer threshold t?",
            "answer": "t = (0 - (-4)) / (1 - (-4)) = 4 / 5 = 0.80, so only the 40 cases with p above 0.80 are answered.",
            "provenance": "Constructed example: 100 calibrated cases defined for this reader; each answer or decline choice is computed with the laboratory's expected-utility function.",
            "source_section": "The cost of declining, measured",
            "source_anchor": "the-cost-of-declining-measured",
            "misconception": {
                "title": "Reading one accuracy figure as the whole product",
                "text": (
                    "A system reported as ninety percent accurate has one point on the risk and coverage curve. The same system might reach ninety-eight percent "
                    "accuracy at sixty percent coverage, which is a different product with different economics, and the single number conceals which one was built."
                ),
            },
            "scope_note": {
                "text": (
                    "Equation (6.2) takes one utility function, but real deployments have several parties with different stakes, and no mathematics in this chapter "
                    "combines them. Whatever function a system acts on is somebody's, and the question of whose is answerable by reading the numbers."
                ),
                "source_section": "Whose utility",
            },
            "controls": [
                {"key": "wrong", "label": "Utility of a wrong answer", "values": [-1, -4, -9], "default": -4},
                {"key": "decline", "label": "Utility of declining", "values": [-1, -0.5, 0], "default": 0},
            ],
            "function": "coverage_picture",
        },
    ],
}

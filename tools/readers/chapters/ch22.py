"""Chapter 22 reader: Safe Enough to Act.

Four demonstrations built on Equations (22.1) to (22.5). Demonstration 1 uses
the chapter's own two-policy table. Demonstration 2 evaluates the one-update
bound and the tightened target with values defined for the reader.
Demonstration 3 evaluates the tail measure for the chapter's constructed
lottery. Demonstration 4 calls the laboratory's own function
(math_ai_agents.chapters.ch22.evaluate) on the laboratory's four-action
example, so the reader, the notebook and the chapter skill agree. Every
number is a constructed teaching value.
"""
import math
from fractions import Fraction

import numpy as np

from math_ai_agents.chapters.ch22 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}

EQ_CONSTRAINT = (
    r"\begin{aligned}\text{maximize}_{\pi}\quad & \operatorname{Ret}^{\pi}\\"
    r"\text{subject to}\quad & \operatorname{Cost}_i^{\pi}\le d_i \quad \text{for every declared } i.\end{aligned}"
)
EQ_SCORE = (
    r"\operatorname{Score}_{\lambda_{\mathrm{safe}}}(\pi)"
    r"=\operatorname{Ret}^{\pi}-\lambda_{\mathrm{safe}}\operatorname{Cost}_1^{\pi}."
)
EQ_BOUND = (
    r"\operatorname{Cost}_i^{\pi_{k+1}}\le d_i+\frac{\sqrt{2\delta}\,\gamma\,\epsilon_i}{(1-\gamma)^2}."
)
EQ_MARGIN = r"\operatorname{Cost}_i^{\pi}\le d_i-\varepsilon_{\mathrm{safe}},\qquad \varepsilon_{\mathrm{safe}}>0."
EQ_CVAR = (
    r"\operatorname{CVaR}_{\alpha}(C)= \inf_{z\in\mathbb R}"
    r"\left[z+\frac{1}{1-\alpha}\,\mathbb E[(C-z)_+]\right]."
)


def num(x, digits=2):
    """Plain number text without trailing zeros, for written sums."""
    text = fmt(x, digits)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


# Demonstration 1: a fixed penalty against a constraint (the chapter's two-policy table)

POLICIES = {"Careful": (8.0, 0.5), "Aggressive": (12.0, 1.5)}  # (expected reward, expected cost)


def penalty_picture(penalty=2, limit=1):
    lam, d = float(penalty), float(limit)
    scores = {n: r - lam * c for n, (r, c) in POLICIES.items()}
    careful, aggressive = scores["Careful"], scores["Aggressive"]
    breakeven = (POLICIES["Aggressive"][0] - POLICIES["Careful"][0]) / (POLICIES["Aggressive"][1] - POLICIES["Careful"][1])
    tie = math.isclose(careful, aggressive, abs_tol=1e-9)
    penalty_pick = "tie (Careful and Aggressive)" if tie else ("Careful" if careful > aggressive else "Aggressive")
    feasible = [n for n, (_, c) in POLICIES.items() if c <= d + 1e-12]
    constrained = max(feasible, key=lambda n: POLICIES[n][0]) if feasible else None

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    grid = np.linspace(0, 8, 81)
    left.plot(grid, 8 - 0.5 * grid, color=PALETTE["navy"], linewidth=2)
    left.plot(grid, 12 - 1.5 * grid, color=PALETTE["terracotta"], linewidth=2, linestyle="dashed")
    left.axvline(breakeven, color=PALETTE["grey"], linestyle="dotted", linewidth=1.4)
    left.plot([lam], [careful], "o", color=PALETTE["navy"], markersize=8)
    left.plot([lam], [aggressive], "s", color=PALETTE["terracotta"], markersize=9, markerfacecolor="white", markeredgewidth=2)
    label_point(left, 0, 12, "Aggressive", color=PALETTE["terracotta"], dx=6, dy=4, ha="left").set_bbox(BOX)
    label_point(left, 8, 4, "Careful", color=PALETTE["navy"], dx=-4, dy=6, ha="right").set_bbox(BOX)
    label_point(left, breakeven, 13.4, f"tie at {num(breakeven)}", color=PALETTE["ink"], dx=5, dy=0, ha="left", va="top")
    left.set_xlim(0, 8)
    left.set_ylim(0, 13.6)
    left.set_xlabel("Penalty multiplier (reward units per cost unit)")
    left.set_ylabel("Blended score: reward minus penalty x cost")
    left.set_title(f"Penalty rule, multiplier {num(lam)}", fontsize=11.5)

    right.axvspan(d, 3.0, facecolor="white", edgecolor=PALETTE["grey"], hatch="///", alpha=0.5, linewidth=0)
    right.axvline(d, color=PALETTE["ink"], linestyle="dashed", linewidth=1.6)
    label_point(right, d, 5.3, f"limit {num(d)}", color=PALETTE["ink"], dx=5, dy=0, ha="left", va="bottom").set_bbox(BOX)
    for name, (r, c) in POLICIES.items():
        eligible = name in feasible
        marker = "o" if name == "Careful" else "s"
        color = PALETTE["navy"] if name == "Careful" else PALETTE["terracotta"]
        right.plot([c], [r], marker, color=color, markersize=10, markerfacecolor=color if eligible else "white", markeredgewidth=2)
        status = "chosen" if name == constrained else ("eligible" if eligible else "over the limit")
        label_point(right, c, r, f"{name}\n{status}", color=color, dx=0, dy=-10 if name == "Careful" else 10,
                    ha="center", va="top" if name == "Careful" else "bottom").set_bbox(BOX)
    right.set_xlim(0, 3.0)
    right.set_ylim(5, 14.5)
    right.set_xlabel("Expected cost")
    right.set_ylabel("Expected reward")
    right.set_title(f"Constraint rule, limit {num(d)}", fontsize=11.5)

    metrics = {
        "Careful score": fmt(careful, 1),
        "Aggressive score": fmt(aggressive, 1),
        "Penalty rule picks": penalty_pick,
        "Policies within the limit": " and ".join(feasible) if feasible else "none",
        "Constraint rule picks": constrained if constrained else "undefined (no policy meets the limit)",
        "Penalty at which the penalty rule flips": fmt(breakeven, 1),
    }
    sums = (f"Careful: 8 - {num(lam)} x 0.5 = {fmt(careful, 1)}. Aggressive: 12 - {num(lam)} x 1.5 = {fmt(aggressive, 1)}. "
            f"Flip point: (12 - 8) / (1.5 - 0.5) = 4 / 1 = {fmt(breakeven, 1)}.")
    if tie:
        rule = "The two blended scores tie, so the penalty rule alone does not choose (on the left plot the two markers coincide)."
    else:
        rule = f"The penalty rule picks {penalty_pick}."
    if constrained is None:
        gate = f"No policy has cost at most {num(d)}, so the constraint rule has no eligible policy and a person must add an alternative or stop."
    elif len(feasible) == 2:
        gate = f"Both costs (0.5 and 1.5) are at most {num(d)}, so both are eligible and the higher reward, 12 against 8, wins: {constrained}."
    else:
        gate = f"Aggressive costs 1.5, above the limit {num(d)}, so it is removed whatever it earns; the constraint rule picks {constrained}."
    interpretation = f"{sums} {rule} {gate} The two rules read the same returns and answer different questions."
    return fig, metrics, interpretation


# Demonstration 2: the one-update bound and the tightened internal target

LIMIT_D = 10.0       # deployment limit d (constructed)
EPS_ADV = 0.1        # largest constraint advantage epsilon (constructed)
MARGIN = 0.5         # safety margin (constructed)


def allowance(step, discount, advantage=EPS_ADV):
    return math.sqrt(2 * step) * discount * advantage / (1 - discount) ** 2


def bound_picture(step=0.005, discount=0.85):
    delta, g = float(step), float(discount)
    root = math.sqrt(2 * delta)
    extra = allowance(delta, g)
    ceiling = LIMIT_D - MARGIN
    end_limit = LIMIT_D + extra
    end_ceiling = ceiling + extra
    covers = extra < MARGIN - 1e-12
    exact = math.isclose(extra, MARGIN, abs_tol=1e-12)

    fig, ax = new_figure(height=4.3)
    rows = [(1.0, LIMIT_D, end_limit, "Optimizer aims\nat the limit"), (0.0, ceiling, end_ceiling, "Optimizer aims\nat the ceiling")]
    for y, start, end, _ in rows:
        inside = max(min(end, LIMIT_D) - start, 0.0)
        outside = end - start - inside
        if inside > 0:
            ax.barh(y, inside, left=start, height=0.3, color=PALETTE["teal"])
        if outside > 1e-12:
            ax.barh(y, outside, left=start + inside, height=0.3, color="white", edgecolor=PALETTE["terracotta"], hatch="///", linewidth=1.2)
        ax.plot([start], [y], "o", color=PALETTE["ink"], markersize=8)
        over = end - LIMIT_D
        verdict = f"over the limit by {fmt(over, 2)}" if over > 1e-12 else ("exactly at the limit" if abs(over) <= 1e-12 else "within the limit")
        # Labels sit to the right of the dashed limit line so the line is never hidden behind a label box.
        label_point(ax, LIMIT_D, y, f"worst case {fmt(end, 2)}\n{verdict}", color=PALETTE["ink"], dx=7, dy=14, ha="left").set_bbox(BOX)
    ax.axvline(LIMIT_D, color=PALETTE["ink"], linestyle="dashed", linewidth=1.6)
    ax.axvline(ceiling, color=PALETTE["gold"], linestyle="dotted", linewidth=1.8)
    label_point(ax, LIMIT_D, 2.35, f"limit d = {fmt(LIMIT_D, 1)}", color=PALETTE["ink"], dx=5, dy=0, ha="left", va="top").set_bbox(BOX)
    label_point(ax, ceiling, -0.85, f"ceiling = {fmt(ceiling, 1)}", color=PALETTE["gold"], dx=5, dy=0, ha="left", va="bottom").set_bbox(BOX)
    ax.set_yticks([1.0, 0.0], [r[3] for r in rows])
    ax.set_xlim(9.0, 11.4)
    ax.set_ylim(-0.9, 2.4)
    ax.set_xlabel("Modeled cost return (constructed units; hatched part is above the limit)")
    ax.set_ylabel("Cost level the optimizer aims at")
    ax.set_title(f"One update: step size {num(delta, 3)}, discount {num(g)}", fontsize=11.5)
    ax.grid(axis="y", alpha=0)

    metrics = {
        "Allowance above the aimed level": fmt(extra, 3),
        "Worst case when aiming at the limit": fmt(end_limit, 3),
        "Ceiling d minus margin": fmt(ceiling, 1),
        "Worst case when aiming at the ceiling": fmt(end_ceiling, 3),
        "Margin covers the allowance": "exactly (equal)" if exact else ("yes" if covers else "no"),
    }
    calc = (f"Allowance = sqrt(2 x {num(delta, 3)}) x {num(g)} x {num(EPS_ADV)} / (1 - {num(g)})^2 = {fmt(root, 2)} x {num(g)} x "
            f"{num(EPS_ADV)} / {fmt((1 - g) ** 2, 4)} = {fmt(extra, 3)}. Aiming at the limit: {fmt(LIMIT_D, 1)} + {fmt(extra, 3)} = {fmt(end_limit, 3)}. "
            f"Aiming at the ceiling, which means the bound is applied with the ceiling in place of d: {fmt(ceiling, 1)} + {fmt(extra, 3)} = {fmt(end_ceiling, 3)}.")
    if exact:
        tail = f"The allowance equals the margin {fmt(MARGIN, 1)}, so the worst case lands exactly on the limit, with nothing to spare."
    elif covers:
        tail = f"The allowance is below the margin {fmt(MARGIN, 1)}, so the modeled worst case stays within d."
    else:
        tail = f"The allowance is above the margin {fmt(MARGIN, 1)}, so even aiming at the ceiling can still overshoot d in the model by {fmt(end_ceiling - LIMIT_D, 3)}."
    interpretation = (f"{calc} {tail} A bigger step or a longer horizon (discount nearer 1) enlarges the allowance; "
                      "the bound permits excess, it does not rule it out. The lower row is this reader's illustration of a margin, not a result of the chapter.")
    return fig, metrics, interpretation


# Demonstration 3: mean cost against a tail measure (the chapter's lottery C = 100 with probability p)

WORST = 100.0
YMAX_CVAR = 230


def cvar_value(alpha, p):
    """Equation (22.5) for the two-point lottery C = 100 with probability p, else 0 (exact fractions)."""
    a, q = Fraction(str(alpha)), Fraction(str(p))
    tail = 1 - a
    corner_zero = 100 * q / tail   # objective at z = 0
    corner_top = Fraction(100)     # objective at z = 100
    value = min(corner_zero, corner_top)
    return float(value), float(corner_zero), float(corner_top), float(tail), corner_zero == corner_top


def objective(z, alpha, p):
    tail = 1 - alpha
    return z + (p * np.maximum(WORST - z, 0) + (1 - p) * np.maximum(0 - z, 0)) / tail


def cvar_picture(alpha=0.99, p=0.01):
    alpha, p = float(alpha), float(p)
    cvar, at_zero, at_top, tail, flat = cvar_value(alpha, p)
    mean = WORST * p
    z = np.linspace(-10, 110, 241)
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    tail_f = float(1 - Fraction(str(alpha)))
    left.plot(z, objective(z, float(Fraction(str(alpha))), p), color=PALETTE["navy"], linewidth=2)
    if flat:
        left.plot([0, WORST], [cvar, cvar], color=PALETTE["gold"], linewidth=5, solid_capstyle="butt")
        label_point(left, 50, cvar, "flat minimum for every z from 0 to 100", color=PALETTE["gold"], dx=0, dy=12, ha="center").set_bbox(BOX)
    else:
        zmin = 0.0 if at_zero < at_top else WORST
        left.plot([zmin], [cvar], "o", color=PALETTE["gold"], markersize=10)
        # Below the minimum point: the curve lies above its own minimum, so the label never covers the line.
        label_point(left, zmin, cvar, f"minimum {fmt(cvar, 1)} at z = {fmt(zmin, 0)}", color=PALETTE["gold"],
                    dx=8 if zmin == 0.0 else -8, dy=-8, ha="left" if zmin == 0.0 else "right", va="top").set_bbox(BOX)
    left.set_xlim(-10, 110)
    left.set_ylim(-30, YMAX_CVAR)
    left.set_yticks([0, 50, 100, 150, 200])
    left.set_xlabel("Cutoff z (cost units)")
    left.set_ylabel("Objective inside Equation (22.5)")
    left.set_title(f"Search over cutoffs, tail share {num(tail_f, 3)}", fontsize=11.5)

    names = ["Mean\ncost", "Tail average\n(CVaR)", "Worst\noutcome"]
    values = [mean, cvar, WORST]
    right.bar(range(3), values, color=[PALETTE["light"], PALETTE["teal"], "white"], edgecolor=PALETTE["ink"],
              hatch=[None, None, "///"], linewidth=1.2, width=0.6)
    for i, v in enumerate(values):
        label_point(right, i, v, fmt(v, 1), color=PALETTE["ink"], dx=0, dy=4, ha="center")
    right.set_xticks(range(3), names)
    right.set_ylim(0, 125)
    right.set_xlabel("Measure of episode cost")
    right.set_ylabel("Cost (constructed units)")
    right.set_title(f"Chance of the bad episode {num(p, 3)}", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    if flat:
        position = f"Both corners give {fmt(at_zero, 1)}, so the minimum is flat and CVaR is {fmt(cvar, 1)}: the tail is exactly the bad episode."
    elif at_zero < at_top:
        position = (f"The smaller corner is z = 0 with {fmt(at_zero, 1)}, so CVaR is {fmt(cvar, 1)}: the tail ({num(tail_f, 3)}) is wider than "
                    f"the bad episode ({num(p, 3)}), so zeros dilute the average.")
    else:
        position = (f"The smaller corner is z = 100 with {fmt(at_top, 1)}, so CVaR is {fmt(cvar, 1)}: the tail ({num(tail_f, 3)}) lies "
                    f"inside the bad episodes ({num(p, 3)}), so it averages the worst outcome alone.")
    metrics = {
        "Mean cost": fmt(mean, 1),
        "Chance of the bad episode": fmt(p, 3).rstrip("0").rstrip("."),
        "Tail share 1 minus alpha": fmt(tail_f, 3).rstrip("0").rstrip("."),
        "Tail average (CVaR)": fmt(cvar, 1),
    }
    curve = objective(z, float(Fraction(str(alpha))), p)
    curve_top, z_top = float(np.max(curve)), float(z[int(np.argmax(curve))])
    cut = (f"The curve rises above the top of the left plot (the axis stops at {YMAX_CVAR}; the curve reaches {fmt(curve_top, 0)} at z = {fmt(z_top, 0)})."
           if curve_top > YMAX_CVAR else f"The whole curve fits inside the left plot (its highest plotted value is {fmt(curve_top, 0)}).")
    interpretation = (
        f"Mean cost = {num(p, 3)} x 100 + {num(1 - p, 3)} x 0 = {fmt(mean, 1)}. Tail share = 1 - {num(alpha, 3)} = {num(tail_f, 3)}. "
        f"Objective at z = 0: 0 + {fmt(mean, 1)} / {num(tail_f, 3)} = {fmt(at_zero, 1)}; at z = 100: 100 + 0 / {num(tail_f, 3)} = {fmt(at_top, 1)}. "
        f"{position} {cut} A tail measure and a mean answer different questions about the same lottery."
    )
    return fig, metrics, interpretation


# Demonstration 4: authority, risk limit and penalty on the laboratory's four-action example

ACTIONS = [
    {"name": "fast-release", "reward": 10, "risk": 0.3, "authorized": False},
    {"name": "reviewed-release", "reward": 5, "risk": 0.05, "authorized": True},
    {"name": "risky-authorized", "reward": 8, "risk": 0.2, "authorized": True},
    {"name": "abstain", "reward": 0, "risk": 0, "authorized": True},
]


def gate_picture(limit=0.1, penalty=5):
    out = evaluate({"risk_limit": float(limit), "risk_penalty": float(penalty), "actions": [dict(a) for a in ACTIONS]})
    rows = out["tables"]
    m = out["metrics"]
    limit, penalty = float(limit), float(penalty)
    constrained = m["constrained_choice"]
    top = m["unconstrained_penalty_choice"]
    authorized_pick = m["authorized_penalty_choice"]

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.axvspan(limit, 0.4, facecolor="white", edgecolor=PALETTE["grey"], hatch="///", alpha=0.5, linewidth=0)
    left.axvline(limit, color=PALETTE["ink"], linestyle="dashed", linewidth=1.6)
    offsets = {"fast-release": (-8, 4, "right", "bottom"), "reviewed-release": (8, -2, "left", "top"),
               "risky-authorized": (-8, 4, "right", "bottom"), "abstain": (8, 6, "left", "bottom")}
    for r in rows:
        color = PALETTE["teal"] if r["name"] == constrained else (PALETTE["navy"] if r["authorized"] else PALETTE["terracotta"])
        marker = "o" if r["authorized"] else "X"
        left.plot([r["risk"]], [r["reward"]], marker, color=color, markersize=10,
                  markerfacecolor=color if (r["authorized"] and r["risk_feasible"]) else "white", markeredgewidth=2)
        dx, dy, ha, va = offsets[r["name"]]
        tag = ("not authorized" if not r["authorized"] else ("over the limit" if not r["risk_feasible"] else
                                                           ("chosen" if r["name"] == constrained else "eligible")))
        label_point(left, r["risk"], r["reward"], f"{r['name']}\n{tag}", color=color, dx=dx, dy=dy, ha=ha, va=va).set_bbox(BOX)
    label_point(left, limit, 12.6, f"limit {num(limit, 2)}", color=PALETTE["ink"], dx=5, dy=0, ha="left", va="top").set_bbox(BOX)
    left.set_xlim(-0.02, 0.4)
    left.set_ylim(-1.5, 12.8)
    left.set_xlabel("Expected adverse-event probability")
    left.set_ylabel("Reward")
    left.set_title(f"Eligible: authorized and risk at most {num(limit, 2)}", fontsize=11.5)

    names = [r["name"] for r in rows]
    y = np.arange(len(rows))[::-1]
    for yi, r in zip(y, rows):
        if not r["authorized"]:
            right.barh(yi, r["penalized_value"], height=0.55, color="white", edgecolor=PALETTE["terracotta"], hatch="xxx", linewidth=1.2)
        elif not r["risk_feasible"]:
            right.barh(yi, r["penalized_value"], height=0.55, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.2)
        else:
            right.barh(yi, r["penalized_value"], height=0.55, color=PALETTE["teal"])
        picks = []
        if r["name"] == top:
            picks.append("penalty pick")
        if r["name"] == constrained:
            picks.append("constraint pick")
        text = fmt(r["penalized_value"], 2) + (("  " + " and ".join(picks)) if picks else "")
        right.text(max(r["penalized_value"], 0) + 0.2, yi, text, va="center", fontsize=10.5, color=PALETTE["ink"])
    right.set_yticks(y, names)
    right.set_xlim(0, 14.5)
    right.set_xlabel(f"Reward minus {num(penalty)} x risk (cross hatch: not authorized; slash hatch: over the limit)")
    right.set_ylabel("Action")
    right.set_title(f"Penalty {num(penalty)}: blended score of each action", fontsize=11.5)
    right.grid(axis="y", alpha=0)

    removed_authority = [r["name"] for r in rows if not r["authorized"]]
    removed_risk = [r["name"] for r in rows if r["authorized"] and not r["risk_feasible"]]
    metrics = {
        "Penalty pick over all rows": top,
        "Penalty pick among authorized rows": authorized_pick,
        "Constraint pick": constrained if constrained else "undefined (no row is eligible)",
        "Eligible actions": f"{m['feasible_count']} of {len(rows)}",
        "Removed by authority": ", ".join(removed_authority) if removed_authority else "none",
        "Removed by the risk limit": ", ".join(removed_risk) if removed_risk else "none",
    }
    by_name = {r["name"]: r for r in rows}
    sums = "; ".join(f"{n}: {num(by_name[n]['reward'])} - {num(penalty)} x {num(by_name[n]['risk'], 2)} = {fmt(by_name[n]['penalized_value'], 2)}" for n in names)
    eligible = [r for r in rows if r["authorized"] and r["risk_feasible"]]
    elig_text = ", ".join(f"{r['name']} (reward {num(r['reward'])})" for r in eligible)
    if constrained is None:
        verdict = "No action is both authorized and within the limit, so there is no constrained choice and the controller must abstain or ask for a new alternative."
    else:
        verdict = f"Eligible rows are {elig_text}; the highest reward among them is {constrained}."
    forbidden = (" Fast-release is not authorized, so no limit or penalty makes it eligible." if "fast-release" in removed_authority else "")
    interpretation = f"{sums}. The penalty rule picks {top} from all rows, without asking about authority. {verdict}{forbidden}"
    return fig, metrics, interpretation


CHAPTER = {
    "number": 22,
    "title": "Safe Enough to Act",
    "subtitle": "A high reward does not make an action permitted: keep task return, measured cost and authority as separate records.",
    "summary": (
        "These four demonstrations follow the chapter from the choice between a fixed penalty and a declared limit, through "
        "what a one-update bound does and does not promise and a tail measure of cost, to a gate that decides which actions "
        "may be considered at all. Each one changes a declared value and shows which rule reacts and which does not."
    ),
    "demos": [
        {
            "id": "C22-D01",
            "title": "A penalty hides an exchange rate",
            "question": "With the same two policies, when does a fixed penalty choose a policy that a cost limit would remove?",
            "equations": [EQ_SCORE, EQ_CONSTRAINT],
            "symbols": (
                "Ret is the expected reward of a policy and Cost its expected measured cost. The multiplier lambda_safe is the "
                "exchange rate: how many reward units one cost unit is worth. d_1 is the declared cost limit. Careful earns 8 "
                "at cost 0.5; Aggressive earns 12 at cost 1.5. The penalty rule picks the larger blended score; the "
                "constraint rule keeps only policies with cost at most the limit, then picks the larger reward."
            ),
            "prediction": "Keep the limit at 1 and raise the multiplier through 2, 4 and 6. Between which two of these multipliers does the penalty rule's pick change, what happens exactly at the flip point, and does the constraint rule ever switch?",
            "explanation": (
                "Each policy's score falls with the multiplier at the rate of its own cost, so Aggressive, which has more cost, "
                "loses ground faster. The lines cross where the reward gap (4) equals the cost gap (1) times the multiplier, "
                "which is a multiplier of 4. The constraint rule never uses the multiplier: it reads only the cost limit."
            ),
            "application": (
                "When a team reports that a penalty setting keeps cost down, ask whether cost is a preference with a "
                "defensible exchange rate or a limit. If it is a limit, state it as a limit and check each policy against it."
            ),
            "assumptions": (
                "One step, two policies, one cost, and expected values read as the whole story. The flip point of 4 belongs to "
                "these two policies and this reward scale, not to any other problem. Even the constrained choice says nothing "
                "about a single bad episode or a hazard the cost leaves out."
            ),
            "check": "Work this one by hand (3 is not one of the offered multipliers). With the limit at 1 and the multiplier at 3, which policy does the penalty rule pick, and which does the constraint rule pick?",
            "answer": (
                "Careful: 8 - 3 x 0.5 = 6.5. Aggressive: 12 - 3 x 1.5 = 7.5. The penalty rule picks Aggressive. Its cost 1.5 is "
                "above the limit 1, so the constraint rule picks Careful (cost 0.5, reward 8)."
            ),
            "provenance": "Constructed example: the chapter's own two-policy table (Careful 8 and 0.5, Aggressive 12 and 1.5), with the limit and multiplier varied.",
            "source_section": "Fixed penalties make a hidden exchange rate",
            "source_anchor": "fixed-penalties-make-a-hidden-exchange-rate",
            "controls": [
                {"key": "penalty", "label": "Penalty multiplier", "values": [2, 4, 6], "default": 2},
                {"key": "limit", "label": "Cost limit", "values": [1, 2], "default": 1},
            ],
            "function": "penalty_picture",
        },
        {
            "id": "C22-D02",
            "title": "A bound permits excess, so leave a margin",
            "question": "How much can the modeled cost exceed the limit after one update, and when does a margin cover it?",
            "equations": [EQ_BOUND, EQ_MARGIN],
            "symbols": (
                "d is the cost limit (10 here). delta is the step-size parameter of one update, which the chapter ties to a KL-divergence trust region. gamma is the discount factor. "
                "epsilon is the largest absolute expected constraint advantage over states (0.1 here). The fraction after d is the "
                "allowance, the most the bound lets the cost return rise above d. The margin, written epsilon_safe in the chapter "
                "(0.5 here), is room reserved below d, so the optimizer aims at the ceiling d minus margin."
            ),
            "prediction": "At discount 0.85, will a step size of 0.005 fit inside the margin of 0.5? What about 0.02?",
            "explanation": (
                "The allowance is sqrt(2 delta) times gamma times epsilon, divided by (1 - gamma) squared. A larger step "
                "raises it in proportion to the square root of the step, and a discount nearer 1 blows it up through the squared denominator. The margin is a "
                "separate choice: it only helps when it is at least as large as the allowance."
            ),
            "application": (
                "Before citing the proposition to justify a safety margin, compute the allowance for your own step size, "
                "discount and advantage, and set the margin from that number rather than from habit."
            ),
            "assumptions": (
                "The bound concerns one ideal update inside the modeled problem; it is not a statement about a training run, "
                "a sampled update or a changed deployment. The values here are constructed. The lower row applies the bound "
                "with the ceiling in the role of the limit (d replaced by d minus the margin), which is this reader's illustration of the margin idea."
            ),
            "check": "Work this one by hand (0.9 is not one of the offered discounts). With step size 0.005, discount 0.9 and advantage 0.1, what is the allowance, and does a margin of 0.5 cover it?",
            "answer": "sqrt(2 x 0.005) = 0.1, so 0.1 x 0.9 x 0.1 / (1 - 0.9)^2 = 0.009 / 0.01 = 0.9. That is above 0.5, so the margin does not cover it.",
            "provenance": "Constructed example: the chapter's bound evaluated with values defined for this reader (limit 10, advantage 0.1, margin 0.5).",
            "source_section": "A constraint is not a promise",
            "source_anchor": "a-constraint-is-not-a-promise",
            "controls": [
                {"key": "step", "label": "Step size delta", "values": [0.005, 0.02], "default": 0.005},
                {"key": "discount", "label": "Discount factor gamma", "values": [0.5, 0.8, 0.85], "default": 0.85},
            ],
            "function": "bound_picture",
        },
        {
            "id": "C22-D03",
            "title": "Mean cost against a tail measure",
            "question": "For a rare bad episode, how different are the mean cost and the average of the worst tail?",
            "equations": [EQ_CVAR],
            "symbols": (
                "C is the cost of one episode: 100 with the chosen probability, otherwise 0. alpha sets the tail: the worst "
                "share 1 - alpha of episodes. z is a cutoff. (C - z)+ means the amount by which C exceeds z, or 0. CVaR is "
                "the smallest value the bracket takes as z varies, which equals the average cost over the worst 1 - alpha share."
            ),
            "prediction": "For a bad episode with probability 0.01, which of the offered tail levels give a tail average of 100, and which gives 10?",
            "explanation": (
                "For this lottery the bracket is a bent line in z, so its smallest value sits at z = 0 or z = 100. At z = 0 "
                "it equals the mean divided by the tail share; at z = 100 it equals 100. CVaR is the smaller of the two, "
                "so a tail wider than the bad episode dilutes it with zeros."
            ),
            "application": (
                "If one rare, severe episode is the worry, a limit on mean cost can look small while the tail measure is large. "
                "State which one the limit is about, and why."
            ),
            "assumptions": (
                "A single two-outcome lottery defined for the reader. Neither measure covers a hazard that the cost variable "
                "leaves out, and a tail measure still says nothing about which individual episode is bad."
            ),
            "check": "Work this one by hand (0.02 and 0.97 are not offered). A bad episode costs 100 with probability 0.02. What is CVaR at alpha 0.97?",
            "answer": "Tail share = 1 - 0.97 = 0.03. At z = 0 the bracket is 2 / 0.03 = 66.67; at z = 100 it is 100. The smaller is 66.67, so CVaR is 66.67 while the mean cost is 2.",
            "provenance": "Constructed example: the chapter's lottery (cost 100 with probability 0.01, else 0, tail level 0.99) with other probabilities and tail levels.",
            "source_section": "Other risk contracts",
            "source_anchor": "other-risk-contracts",
            "controls": [
                {"key": "alpha", "label": "Tail level alpha", "values": [0.9, 0.95, 0.99, 0.995], "default": 0.99},
                {"key": "p", "label": "Probability of the bad episode", "values": [0.01, 0.05], "default": 0.01},
            ],
            "function": "cvar_picture",
        },
        {
            "id": "C22-D04",
            "title": "Authority first, risk limit second, reward last",
            "question": "Which actions may be considered at all, and which of those has the best reward?",
            "equations": [EQ_CONSTRAINT, EQ_SCORE],
            "symbols": (
                "Each action has a reward, an expected adverse-event probability (risk) and a yes or no current permission. "
                "The risk limit is the largest probability allowed. The penalty is the reward deducted per unit of risk. "
                "The gate keeps only actions that are authorized and within the risk limit; the constraint pick is the "
                "highest reward among those. In the displayed equations, Ret is the reward, Cost is the risk, d_i is the risk limit and "
                "lambda_safe is the penalty, with each action standing in for a policy pi. Authority, the yes or no permission, is an "
                "extra condition that the equations do not show."
            ),
            "prediction": "Raise the risk limit from 0.1 to 0.25. Does fast-release become eligible? Which action does the constraint rule now pick?",
            "explanation": (
                "The penalty rule scores every row by reward minus penalty times risk, so a high-reward forbidden row can win. "
                "The gate removes rows before any score is used: authority is a yes or no condition, so no limit or penalty "
                "setting grants it. A looser risk limit can bring back an over-limit row but never a forbidden one."
            ),
            "application": (
                "For an agent that can call tools, list each action with its permission and risk, remove what is not permitted, "
                "then rank the rest. Keep an explicit abstain row, provided abstain is authorized and its risk is within the limit, so the set is never empty."
            ),
            "assumptions": (
                "Rewards, risks and permissions are supplied values; nothing here estimates risk. An expected-risk limit is a statement "
                "about an average, so an action with risk 0.05 can still end badly. A large enough penalty can mimic a "
                "gate in one case and fail in the next."
            ),
            "check": "Work this one by hand (0.2 is not an offered limit). With the risk limit at 0.2 and the penalty at 5, which action does the constraint rule pick, and is fast-release eligible?",
            "answer": (
                "Eligible rows are authorized with risk at most 0.2: reviewed-release (0.05), risky-authorized (0.2, which meets the "
                "limit exactly) and abstain (0). Rewards 5, 8 and 0, so risky-authorized wins. Fast-release is not authorized, so it stays out."
            ),
            "provenance": "Constructed example: the laboratory's four-action example, evaluated with the laboratory's risk and authority function. The four rewards, risks and permissions are not taken from the chapter, whose section supports only the distinction between an objective and a gate.",
            "source_section": "Authority is an operating envelope",
            "source_anchor": "authority-is-an-operating-envelope",
            "controls": [
                {"key": "limit", "label": "Risk limit", "values": [0, 0.1, 0.25], "default": 0.1},
                {"key": "penalty", "label": "Penalty per unit of risk", "values": [5, 25], "default": 5},
            ],
            "function": "gate_picture",
        },
    ],
}

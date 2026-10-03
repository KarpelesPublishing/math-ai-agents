"""Chapter 22 reader: Safe Enough to Act.

Four demonstrations built on Equations (22.1) to (22.6).

Demonstration 1 puts the chapter's two-policy table, the Mathematical
Workbench problem VI.1 and the laboratory's transfer case on one reward-cost
plane (Figure 22.2) and compares a fixed penalty with a cost limit. The
transfer case is also evaluated with the laboratory's own function
(math_ai_agents.chapters.ch22.evaluate); the table and the workbench case have
expected costs above 1, outside the laboratory function's probability domain,
so they are computed directly. Demonstration 2 evaluates the one-update bound,
the tightened target and the trust-region size with values defined for the
reader. Demonstration 3 shows the chapter's tail measure and a finite-horizon
risk budget, Equations (22.5) and (22.6). Demonstration 4 calls the
laboratory function on the four-action example (default and changed cases)
and adds a bypass of the check. Every number is a constructed teaching value.
"""
import math
from fractions import Fraction

import numpy as np

from math_ai_agents.chapters.ch22 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure

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
EQ_BUDGET = r"b_{t+1}=b_t-\widehat r_t(a_t),\qquad b_0=B,\qquad \widehat r_t(a_t)\le b_t."


def num(x, digits=2):
    """Plain number text without trailing zeros, for written sums."""
    text = fmt(x, digits)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def sg(x, digits=2):
    """Number text with a negative in parentheses, for written sums."""
    return f"({num(x, digits)})" if x < 0 else num(x, digits)


# Demonstration 1: a fixed penalty against a cost limit, on the reward-cost plane (Figure 22.2)

CASES = {
    "table": {"label": "The chapter's table", "limit": Fraction(1),
              "policies": [("Careful", Fraction(8), Fraction(1, 2)), ("Aggressive", Fraction(12), Fraction(3, 2))],
              "xlim": (0, 2.2), "ylim": (5.5, 14.5),
              "offsets": {"Careful": (0, -12, "center", "top"), "Aggressive": (0, 12, "center", "bottom")}},
    "workbench": {"label": "Workbench VI.1", "limit": Fraction(1),
                  "policies": [("Careful", Fraction(7), Fraction(1, 2)), ("Aggressive", Fraction(11), Fraction(2))],
                  "xlim": (0, 2.6), "ylim": (4.5, 12.5),
                  "offsets": {"Careful": (0, -12, "center", "top"), "Aggressive": (0, 12, "center", "bottom")}},
    "transfer": {"label": "The laboratory's transfer case", "limit": Fraction(0),
                 "policies": [("act", Fraction(20), Fraction(1, 100)), ("wait", Fraction(-1), Fraction(0))],
                 "xlim": (-0.004, 0.02), "ylim": (-5, 24),
                 "offsets": {"act": (-10, -2, "right", "top"), "wait": (10, 6, "left", "bottom")}},
}


def lab_check_transfer(lam, limit, policies):
    """The laboratory's own function on the two transfer rows (costs are probabilities there)."""
    rows = [{"name": n, "reward": float(r), "risk": float(c), "authorized": True} for n, r, c in policies]
    out = evaluate({"risk_limit": float(limit), "risk_penalty": float(lam), "actions": rows})
    return out["metrics"]["unconstrained_penalty_choice"], out["metrics"]["constrained_choice"]


def penalty_picture(case="table", penalty=2):
    spec = CASES[case]
    lam = Fraction(str(penalty))
    d = spec["limit"]
    pol = spec["policies"]
    scores = {n: r - lam * c for n, r, c in pol}
    names = [n for n, _, _ in pol]
    best = max(scores.values())
    tied = [n for n in names if scores[n] == best]
    penalty_pick = f"tie ({' and '.join(tied)})" if len(tied) > 1 else tied[0]
    feasible = [n for n, _, c in pol if c <= d]
    constrained = max(feasible, key=lambda n: next(r for m, r, _ in pol if m == n)) if feasible else None
    low = min(pol, key=lambda p: p[2])
    high = max(pol, key=lambda p: p[2])
    flip = (high[1] - low[1]) / (high[2] - low[2])
    if case == "transfer":
        lab_pick, lab_con = lab_check_transfer(lam, d, pol)
        if len(tied) == 1 and lab_pick != tied[0]:
            raise AssertionError("laboratory function disagrees on the penalty pick")
        if lab_con != constrained:
            raise AssertionError("laboratory function disagrees on the constrained pick")
    # Randomising between the two policies (workbench VI.1): cost and reward mix linearly.
    if high[2] <= d:
        mix_p = Fraction(1) if high[1] > low[1] else Fraction(0)
    else:
        mix_p = (d - low[2]) / (high[2] - low[2]) if low[2] <= d else None
    mix_reward = low[1] + mix_p * (high[1] - low[1]) if mix_p is not None else None

    fig, (left, right) = new_figure(ncols=2, height=4.4)
    x0, x1 = spec["xlim"]
    y0, y1 = spec["ylim"]
    left.axvspan(float(d), x1, facecolor="white", edgecolor=PALETTE["grey"], hatch="///", alpha=0.5, linewidth=0)
    left.axvline(float(d), color=PALETTE["ink"], linestyle="dashed", linewidth=1.6)
    left.plot([float(low[2]), float(high[2])], [float(low[1]), float(high[1])], color=PALETTE["grey"], linestyle="dotted", linewidth=1.4)
    for n, r, c in pol:
        eligible = n in feasible
        color = PALETTE["navy"] if n == low[0] else PALETTE["terracotta"]
        marker = "o" if n == low[0] else "s"
        left.plot([float(c)], [float(r)], marker, color=color, markersize=10, markerfacecolor=color if eligible else "white", markeredgewidth=2, zorder=4)
        status = "chosen" if n == constrained else ("eligible" if eligible else "over the limit")
        dx, dy, ha, va = spec["offsets"][n]
        left.annotate(f"{n}\n{status}", (float(c), float(r)), xytext=(dx, dy), textcoords="offset points", fontsize=10.5,
                      color=color, ha=ha, va=va, bbox=BOX, zorder=5)
    if mix_p is not None and 0 < mix_p < 1:
        left.plot([float(d)], [float(mix_reward)], "D", color=PALETTE["gold"], markersize=9, zorder=4)
        left.annotate(f"best mix {mix_p.numerator}/{mix_p.denominator}\nreward {fmt(float(mix_reward), 2)}\n(workbench reading)", (float(d), float(mix_reward)),
                      xytext=(10, -4), textcoords="offset points", fontsize=10.5, color=PALETTE["gold"], ha="left", va="top", bbox=BOX, zorder=5)
    left.set_xlim(x0, x1)
    left.set_ylim(y0, y1)
    left.set_xlabel("Expected cost")
    left.set_ylabel("Expected reward")
    left.set_title(f"Constraint rule, limit {num(float(d), 2)}", fontsize=11.5)

    vals = [float(scores[n]) for n in names]
    lo, hi = min(vals + [0.0]), max(vals + [0.0])
    ypos = [1, 0]
    for y, n in zip(ypos, names):
        v = float(scores[n])
        color = PALETTE["navy"] if n == low[0] else PALETTE["terracotta"]
        right.barh(y, v, height=0.5, color=color if n in tied else "white", edgecolor=color, hatch=None if n in tied else "///", linewidth=1.4)
        text = fmt(v, 2) + ("  penalty pick" if n in tied and len(tied) == 1 else ("  tie" if n in tied else ""))
        if v >= 0:
            right.text(v + 0.02 * (hi - lo), y, text, va="center", ha="left", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
        else:
            right.text(v - 0.02 * (hi - lo), y, text, va="center", ha="right", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
    right.axvline(0, color=PALETTE["ink"], linewidth=1)
    right.set_yticks(ypos, names)
    span = hi - lo
    right.set_xlim(lo - (0.6 * span if lo < 0 else 0.04 * span), hi + (1.0 * span if hi > 0 else 0.05 * span))
    right.set_ylim(-0.6, 1.6)
    right.set_xlabel("Blended score: reward minus multiplier x cost")
    right.set_ylabel("Policy")
    right.set_title(f"Penalty rule, multiplier {num(float(lam), 2)}", fontsize=11.5)
    right.grid(axis="y", alpha=0)

    sums = "; ".join(f"{n}: {num(float(r))} - {num(float(lam))} x {num(float(c), 3)} = {fmt(float(scores[n]), 2)}" for n, r, c in pol)
    flip_text = f"({num(float(high[1]))} - {sg(float(low[1]))}) / ({num(float(high[2]))} - {num(float(low[2]))}) = {num(float(high[1] - low[1]))} / {num(float(high[2] - low[2]), 3)}"
    if len(tied) > 1:
        rule = f"The two blended scores tie, so the penalty rule alone does not choose (the multiplier equals the flip point {num(float(flip), 2)})."
    else:
        rule = f"The penalty rule picks {penalty_pick}; the flip point is {flip_text} = {num(float(flip), 2)}, and a multiplier above it favors {low[0]}."
    if constrained is None:
        gate = f"No policy has cost at most {num(float(d), 2)}, so the constraint rule has no eligible policy."
    elif len(feasible) == 2:
        gate = f"Both costs are at most {num(float(d), 2)}, so both are eligible and the higher reward wins: {constrained}."
    else:
        over = [n for n in names if n not in feasible][0]
        cost_over = next(c for n, _, c in pol if n == over)
        gate = (f"{over} costs {num(float(cost_over), 3)}, above the limit {num(float(d), 2)}, so it is removed whatever it earns; "
                f"the constraint rule picks {constrained}.")
    if mix_p is None:
        mix = "No mixture of the two policies meets the limit."
    elif mix_p == 0 and high[2] > d:
        mix = (f"Randomising does not help: {high[0]} alone costs {num(float(high[2]), 3)}, above the limit, so any positive chance of it breaks the limit "
               f"(expected cost {num(float(low[2]), 3)} + p x {num(float(high[2] - low[2]), 3)} must stay at most {num(float(d), 2)}, so p = 0).")
    elif mix_p == 1:
        mix = "Both policies meet the limit, so the best mixture is the higher-reward policy alone."
    else:
        mix = (f"If randomising is allowed, expected cost {num(float(low[2]), 3)} + p x {num(float(high[2] - low[2]), 3)} must stay at most {num(float(d), 2)}, "
               f"so p = {mix_p.numerator}/{mix_p.denominator} and the reward is {num(float(low[1]))} + {mix_p.numerator}/{mix_p.denominator} x {num(float(high[1] - low[1]))} = {fmt(float(mix_reward), 2)}.")
    interpretation = f"{sums}. {rule} {gate} {mix} The two rules read the same returns and answer different questions."
    metrics = {
        f"{names[0]} score": fmt(float(scores[names[0]]), 2),
        f"{names[1]} score": fmt(float(scores[names[1]]), 2),
        "Penalty rule picks": penalty_pick,
        "Policies within the limit": " and ".join(feasible) if feasible else "none",
        "Constraint rule picks": constrained if constrained else "undefined (no policy meets the limit)",
        "Multiplier at which the penalty rule flips": num(float(flip), 2),
        "Best randomised mix": (("" if case == "workbench" else "workbench reading, outside the policy family: ") + (f"probability {mix_p.numerator} of {high[0]}" if mix_p.denominator == 1 else f"probability {mix_p.numerator}/{mix_p.denominator} of {high[0]}") + f", reward {fmt(float(mix_reward), 2)}" if mix_p is not None else "undefined (no mixture meets the limit)"),
    }
    steps = [
        f"Score of {pol[0][0]}: {num(float(pol[0][1]))} - {num(float(lam))} x {num(float(pol[0][2]), 3)} = {fmt(float(scores[pol[0][0]]), 2)}.",
        f"Score of {pol[1][0]}: {num(float(pol[1][1]))} - {num(float(lam))} x {num(float(pol[1][2]), 3)} = {fmt(float(scores[pol[1][0]]), 2)}.",
        f"Penalty rule: {'a tie' if len(tied) > 1 else penalty_pick + ' has the larger score'}.",
        f"Flip multiplier = {flip_text} = {num(float(flip), 2)}.",
        f"Limit d = {num(float(d), 2)}: policies with cost at most d are {' and '.join(feasible) if feasible else 'none'}.",
        f"Constraint rule: {constrained if constrained else 'no eligible policy'}.",
    ]
    alt = (f"Left: a reward against cost plane with the two policies and a dashed cost limit at {num(float(d), 2)}; "
           f"constraint rule picks {constrained if constrained else 'nothing'}. Right: bars of blended score at multiplier {num(float(lam), 2)}; "
           f"penalty rule picks {penalty_pick}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: the one-update bound, the tightened internal target and the trust-region size

LIMIT_D = 10.0       # deployment limit d (constructed)
EPS_ADV = 0.1        # largest constraint advantage epsilon (constructed)


def allowance(step, discount, advantage=EPS_ADV):
    return math.sqrt(2 * step) * discount * advantage / (1 - discount) ** 2


def largest_step(margin, discount, advantage=EPS_ADV):
    """Step size delta at which the allowance equals the margin (solve sqrt(2 delta) g e / (1-g)^2 = m)."""
    root = margin * (1 - discount) ** 2 / (discount * advantage)
    return root * root / 2


DELTA_PLOT = 0.03


def bound_picture(step=0.005, discount=0.85, margin=0.5):
    delta, g, m = float(step), float(discount), float(margin)
    root = math.sqrt(2 * delta)
    extra = allowance(delta, g)
    ceiling = LIMIT_D - m
    end_limit = LIMIT_D + extra
    end_ceiling = ceiling + extra
    covers = extra < m - 1e-12
    exact = math.isclose(extra, m, abs_tol=1e-12)
    dmax = largest_step(m, g)

    fig, (left, right) = new_figure(ncols=2, height=4.4)
    rows = [(1.0, LIMIT_D, end_limit), (0.0, ceiling, end_ceiling)]
    for y, start, end in rows:
        inside = max(min(end, LIMIT_D) - start, 0.0)
        outside = end - start - inside
        if inside > 0:
            left.barh(y, inside, left=start, height=0.3, color=PALETTE["teal"])
        if outside > 1e-12:
            left.barh(y, outside, left=start + inside, height=0.3, color="white", edgecolor=PALETTE["terracotta"], hatch="///", linewidth=1.2)
        left.plot([start], [y], "o", color=PALETTE["ink"], markersize=8)
        over = end - LIMIT_D
        verdict = f"over by {fmt(over, 2)}" if over > 1e-12 else ("exactly at limit" if abs(over) <= 1e-12 else "within limit")
        label_point(left, end, y, f"{fmt(end, 2)}\n{verdict}", color=PALETTE["ink"], dx=0, dy=16, ha="center", va="bottom").set_bbox(BOX)
    left.axvline(LIMIT_D, color=PALETTE["ink"], linestyle="dashed", linewidth=1.6)
    left.axvline(ceiling, color=PALETTE["gold"], linestyle="dotted", linewidth=1.8)
    label_point(left, LIMIT_D, 2.55, f"limit {fmt(LIMIT_D, 0)}", color=PALETTE["ink"], dx=4, dy=0, ha="left", va="top").set_bbox(BOX)
    label_point(left, ceiling, -0.85, f"ceiling {fmt(ceiling, 1)}", color=PALETTE["gold"], dx=-4, dy=0, ha="right", va="bottom").set_bbox(BOX)
    left.set_yticks([1.0, 0.0], ["Aim at\nthe limit", "Aim at\nthe ceiling"])
    left.set_xlim(7.6, 12.4)
    left.set_ylim(-0.9, 2.6)
    left.set_xlabel("Worst modeled cost return (hatched: above the limit)")
    left.set_ylabel("Cost level the optimizer aims at")
    left.set_title(f"One update at step {num(delta, 3)}", fontsize=11.5)
    left.grid(axis="y", alpha=0)

    grid = np.linspace(0, DELTA_PLOT, 121)
    curve = np.sqrt(2 * grid) * g * EPS_ADV / (1 - g) ** 2
    right.plot(grid, curve, color=PALETTE["navy"], linewidth=2)
    right.axhline(m, color=PALETTE["gold"], linestyle="dotted", linewidth=1.8)
    label_point(right, DELTA_PLOT, m, f"margin {fmt(m, 1)}", color=PALETTE["gold"], dx=-4, dy=4, ha="right", va="bottom").set_bbox(BOX)
    right.plot([delta], [extra], "o", color=PALETTE["terracotta"], markersize=9, zorder=4)
    right.plot([delta, delta], [0, extra], color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.2)
    low_curve = extra < 0.45
    label_point(right, delta, extra, f"step {fmt(delta, 3)}\nallowance {fmt(extra, 3)}", color=PALETTE["terracotta"],
                dx=8 if delta < 0.015 else -8, dy=10 if low_curve else (-6 if delta < 0.015 else 8),
                ha="left" if delta < 0.015 else "right", va="bottom" if (low_curve or delta >= 0.015) else "top").set_bbox(BOX)
    if dmax <= DELTA_PLOT:
        right.axvline(dmax, color=PALETTE["teal"], linestyle="dotted", linewidth=1.8)
        label_point(right, dmax, 2.35, f"covered up to {fmt(dmax, 4)}", color=PALETTE["teal"], dx=4 if dmax < 0.015 else -4, dy=0,
                    ha="left" if dmax < 0.015 else "right", va="top").set_bbox(BOX)
    else:
        label_point(right, DELTA_PLOT, 2.35, "every step shown is covered", color=PALETTE["teal"], dx=-4, dy=0,
                    ha="right", va="top").set_bbox(BOX)
    right.set_xlim(0, DELTA_PLOT)
    right.set_ylim(0, 2.45)
    right.set_xlabel("Step size delta (trust-region size)")
    right.set_ylabel("Allowance above the aimed level")
    right.set_title(f"Allowance, discount {num(g)}", fontsize=11.5)

    metrics = {
        "Allowance above the aimed level": fmt(extra, 3),
        "Worst case when aiming at the limit": fmt(end_limit, 3),
        "Ceiling d minus margin": fmt(ceiling, 1),
        "Worst case when aiming at the ceiling": fmt(end_ceiling, 3),
        "Margin covers the allowance": "exactly (equal)" if exact else ("yes" if covers else "no"),
        "Largest step the margin covers": fmt(dmax, 4),
    }
    calc = (f"Allowance = sqrt(2 x {num(delta, 3)}) x {num(g)} x {num(EPS_ADV)} / (1 - {num(g)})^2 = {fmt(root, 2)} x {num(g)} x "
            f"{num(EPS_ADV)} / {fmt((1 - g) ** 2, 4)} = {fmt(extra, 3)}. Aiming at the limit: {fmt(LIMIT_D, 1)} + {fmt(extra, 3)} = {fmt(end_limit, 3)}. "
            f"Aiming at the ceiling, which means the bound is applied with the ceiling in place of d: {fmt(ceiling, 1)} + {fmt(extra, 3)} = {fmt(end_ceiling, 3)}.")
    if exact:
        tail = f"The allowance equals the margin {fmt(m, 1)}, so the worst case lands exactly on the limit, with nothing to spare."
    elif covers:
        tail = f"The allowance is below the margin {fmt(m, 1)}, so the modeled worst case stays within d."
    else:
        tail = f"The allowance is above the margin {fmt(m, 1)}, so even aiming at the ceiling can still overshoot d in the model by {fmt(end_ceiling - LIMIT_D, 3)}."
    reach = (f"Setting the allowance equal to the margin gives a largest covered step of (({fmt(m, 1)} x {fmt((1 - g) ** 2, 4)}) / ({num(g)} x {num(EPS_ADV)}))^2 / 2 = "
             f"{fmt(dmax, 4)}" + ("; the plot stops at 0.03, so every step shown is covered." if dmax > DELTA_PLOT else "."))
    interpretation = (f"{calc} {tail} {reach} A bigger step or a longer horizon (discount nearer 1) enlarges the allowance; "
                      "the bound permits excess, it does not rule it out. The lower row is this reader's illustration of a margin, not a result of the chapter.")
    steps = [
        f"Root: sqrt(2 x {num(delta, 3)}) = {fmt(root, 3)}.",
        f"Allowance = {fmt(root, 3)} x {num(g)} x {num(EPS_ADV)} / {fmt((1 - g) ** 2, 4)} = {fmt(extra, 3)}.",
        f"Aim at the limit: {fmt(LIMIT_D, 1)} + {fmt(extra, 3)} = {fmt(end_limit, 3)}.",
        f"Ceiling = {fmt(LIMIT_D, 1)} - {fmt(m, 1)} = {fmt(ceiling, 1)}; worst case {fmt(ceiling, 1)} + {fmt(extra, 3)} = {fmt(end_ceiling, 3)}.",
        f"Margin {fmt(m, 1)} against allowance {fmt(extra, 3)}: " + ("exactly equal." if exact else ("covered." if covers else "not covered.")),
        f"Largest covered step = {fmt(dmax, 4)}.",
    ]
    alt = (f"Left: two bars from the aimed cost level to the worst modeled cost; aiming at the limit ends at {fmt(end_limit, 2)} and aiming at the ceiling "
           f"at {fmt(end_ceiling, 2)}. Right: the allowance rising with step size for discount {num(g)}, with the margin {fmt(m, 1)} as a horizontal line and "
           f"the marker at step {fmt(delta, 3)} with allowance {fmt(extra, 3)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: two other risk contracts, a tail measure (22.5) and a finite-horizon risk budget (22.6)

WORST = 100.0
YMAX_CVAR = 230
P_BAD = Fraction(1, 100)         # the chapter's lottery: cost 100 with probability .01, else 0
CHARGES = [4, 5, 3, 5]           # proposed risk charges at four decisions, in hundredths (constructed for the reader)


def cvar_value(alpha, p=P_BAD):
    """Equation (22.5) for the two-point lottery C = 100 with probability p, else 0 (exact fractions)."""
    a, q = Fraction(str(alpha)), Fraction(p)
    tail = 1 - a
    corner_zero = 100 * q / tail   # objective at z = 0
    corner_top = Fraction(100)     # objective at z = 100
    value = min(corner_zero, corner_top)
    return float(value), float(corner_zero), float(corner_top), float(tail), corner_zero == corner_top


def objective(z, alpha, p):
    tail = 1 - alpha
    return z + (p * np.maximum(WORST - z, 0) + (1 - p) * np.maximum(0 - z, 0)) / tail


def ledger(budget_hundredths):
    """Equation (22.6) run on the proposed charges: accept a charge only if it fits the remaining budget."""
    b = budget_hundredths
    rows = []
    for t, r in enumerate(CHARGES, start=1):
        ok = r <= b
        rows.append({"t": t, "before": b, "charge": r, "accepted": ok})
        if ok:
            b -= r
    return rows, b


def risk_contracts_picture(alpha=0.99, budget=0.1):
    alpha_f, p = float(alpha), float(P_BAD)
    cvar, at_zero, at_top, tail, flat = cvar_value(alpha)
    mean = WORST * p
    tail_f = float(1 - Fraction(str(alpha)))
    B = round(float(budget) * 100)
    rows, left_over = ledger(B)
    fig, (left, right) = new_figure(ncols=2, height=4.4)
    z = np.linspace(-10, 110, 241)
    curve = objective(z, alpha_f, p)
    left.plot(z, curve, color=PALETTE["navy"], linewidth=2)
    left.axhline(WORST, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.3)
    left.axhline(mean, color=PALETTE["grey"], linestyle="dotted", linewidth=1.5)
    label_point(left, 30, WORST, "worst outcome 100", color=PALETTE["terracotta"], dx=0, dy=5, ha="center", va="bottom").set_bbox(BOX)
    label_point(left, 108, mean, f"mean cost {fmt(mean, 1)}", color=PALETTE["grey"], dx=0, dy=4, ha="right", va="bottom").set_bbox(BOX)
    if flat:
        left.plot([0, WORST], [cvar, cvar], color=PALETTE["gold"], linewidth=5, solid_capstyle="butt")
        note = f"gold: CVaR = {fmt(cvar, 1)}, flat for z from 0 to 100"
    else:
        zmin = 0.0 if at_zero < at_top else WORST
        left.plot([zmin], [cvar], "o", color=PALETTE["gold"], markersize=10, zorder=4)
        note = f"gold: CVaR = {fmt(cvar, 1)}, minimum at z = {fmt(zmin, 0)}"
    left.text(0.98, 0.97, note, transform=left.transAxes, fontsize=10.5, color=PALETTE["gold"], ha="right", va="top", bbox=BOX, zorder=5)
    left.set_xlim(-10, 110)
    left.set_ylim(-30, YMAX_CVAR)
    left.set_yticks([0, 50, 100, 150, 200])
    left.set_xlabel("Cutoff z (cost units)")
    left.set_ylabel("Objective inside Equation (22.5)")
    left.set_title(f"Tail measure, alpha {num(alpha_f, 3)}", fontsize=11.5)

    xs = np.arange(len(rows))
    for x, r in zip(xs, rows):
        right.bar(x - 0.18, r["before"] / 100, width=0.34, color=PALETTE["teal"])
        right.bar(x + 0.18, r["charge"] / 100, width=0.34, color=PALETTE["gold"] if r["accepted"] else "white",
                  edgecolor=PALETTE["gold"] if r["accepted"] else PALETTE["terracotta"], hatch=None if r["accepted"] else "///", linewidth=1.3)
    right.set_xticks(xs, [f"t = {r['t']}\n{'charged' if r['accepted'] else 'refused'}" for r in rows])
    right.set_ylim(0, max(0.24, B / 100 + 0.03))
    right.set_xlabel("Decision (teal: budget left before it; gold or hatched: proposed charge)")
    right.set_ylabel("Budget units")
    right.set_title(f"Risk budget B = {fmt(B / 100, 2)}", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    if flat:
        position = f"Both corners give {fmt(at_zero, 1)}, so the minimum is flat and CVaR is {fmt(cvar, 1)}: the tail is exactly the bad episode."
    elif at_zero < at_top:
        position = (f"The smaller corner is z = 0 with {fmt(at_zero, 1)}, so CVaR is {fmt(cvar, 1)}: the tail ({num(tail_f, 3)}) is wider than "
                    f"the bad episode ({num(p, 3)}), so zeros dilute the average.")
    else:
        position = (f"The smaller corner is z = 100 with {fmt(at_top, 1)}, so CVaR is {fmt(cvar, 1)}: the tail ({num(tail_f, 3)}) lies "
                    f"inside the bad episodes ({num(p, 3)}), so it averages the worst outcome alone.")
    curve_top, z_top = float(np.max(curve)), float(z[int(np.argmax(curve))])
    cut = (f"The curve rises above the top of the left plot (the axis stops at {YMAX_CVAR}; the curve reaches {fmt(curve_top, 0)} at z = {fmt(z_top, 0)})."
           if curve_top > YMAX_CVAR else f"The whole curve fits inside the left plot (its highest plotted value is {fmt(curve_top, 0)}).")
    chain = []
    b = B
    for r in rows:
        if r["accepted"]:
            chain.append(f"t = {r['t']}: {fmt(r['charge'] / 100, 2)} <= {fmt(r['before'] / 100, 2)}, charged, b = {fmt(r['before'] / 100, 2)} - {fmt(r['charge'] / 100, 2)} = {fmt((r['before'] - r['charge']) / 100, 2)}")
        else:
            chain.append(f"t = {r['t']}: {fmt(r['charge'] / 100, 2)} > {fmt(r['before'] / 100, 2)}, refused, b stays {fmt(r['before'] / 100, 2)}")
    spent = sum(r["charge"] for r in rows if r["accepted"])
    refused = sum(1 for r in rows if not r["accepted"])
    interpretation = (
        f"Mean cost = {num(p, 3)} x 100 + {num(1 - p, 3)} x 0 = {fmt(mean, 1)}. Tail share = 1 - {num(alpha_f, 3)} = {num(tail_f, 3)}. "
        f"Objective at z = 0: 0 + {fmt(mean, 1)} / {num(tail_f, 3)} = {fmt(at_zero, 1)}; at z = 100: 100 + 0 / {num(tail_f, 3)} = {fmt(at_top, 1)}. "
        f"{position} {cut} Budget B = {fmt(B / 100, 2)}, with a refused action replaced by a fallback that charges 0: " + "; ".join(chain) +
        f". Spent {fmt(spent / 100, 2)} of {fmt(B / 100, 2)}, left {fmt(left_over / 100, 2)}."
    )
    metrics = {
        "Mean cost": fmt(mean, 1),
        "Tail share 1 minus alpha": num(tail_f, 3),
        "Tail average (CVaR)": fmt(cvar, 1),
        "Budget B": fmt(B / 100, 2),
        "Charges accepted": f"{len(rows) - refused} of {len(rows)}",
        "Budget left at the end": fmt(left_over / 100, 2),
    }
    steps = [
        f"Mean cost = {num(p, 3)} x 100 = {fmt(mean, 1)}; tail share = {num(tail_f, 3)}.",
        f"Cutoff z = 0 gives {fmt(mean, 1)} / {num(tail_f, 3)} = {fmt(at_zero, 1)}; z = 100 gives {fmt(at_top, 1)}.",
        f"CVaR is the smaller corner: {fmt(cvar, 1)}.",
    ] + [f"Budget {c}." for c in chain[:4]] + [f"Left at the end: {fmt(left_over / 100, 2)}."]
    steps = steps[:8]
    alt = (f"Left: the objective of Equation 22.5 against the cutoff, with its minimum (CVaR {fmt(cvar, 1)}), the mean cost {fmt(mean, 1)} and the worst outcome 100 marked. "
           f"Right: four decisions with budget B {fmt(B / 100, 2)}; {len(rows) - refused} charges are accepted and {refused} refused, leaving {fmt(left_over / 100, 2)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: authority, risk limit and penalty on the laboratory's four-action example, with a bypass

ACTIONS = [
    {"name": "fast-release", "reward": 10, "risk": 0.3, "authorized": False},
    {"name": "reviewed-release", "reward": 5, "risk": 0.05, "authorized": True},
    {"name": "risky-authorized", "reward": 8, "risk": 0.2, "authorized": True},
    {"name": "abstain", "reward": 0, "risk": 0, "authorized": True},
]


def gate_picture(limit=0.1, penalty=5, route="checked"):
    out = evaluate({"risk_limit": float(limit), "risk_penalty": float(penalty), "actions": [dict(a) for a in ACTIONS]})
    rows = out["tables"]
    m = out["metrics"]
    limit, penalty = float(limit), float(penalty)
    constrained = m["constrained_choice"]
    values = {r["name"]: r["penalized_value"] for r in rows}
    best = max(values.values())
    tied = [n for n in values if abs(values[n] - best) < 1e-9]
    top = tied[0] if len(tied) == 1 else f"tie ({' and '.join(tied)})"
    authorized_pick = m["authorized_penalty_choice"]
    bypass = route == "bypass"
    executed = (tied[0] if bypass else constrained)  # a bypass runs the controller's own top row unchecked
    executed_text = executed if executed else "none (no eligible row)"

    fig, (left, right) = new_figure(ncols=2, height=4.4)
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
        if r["name"] in tied:
            picks.append("penalty pick" if len(tied) == 1 else "penalty tie")
        if r["name"] == constrained:
            picks.append(f"gate pick, reward {num(r['reward'])}")
        if executed is not None and r["name"] == executed and bypass:
            picks.append("runs unchecked")
        text = fmt(r["penalized_value"], 2) + (("  " + picks[0]) if len(picks) == 1 else ("\n" + "\n".join(picks) if picks else ""))
        v = r["penalized_value"]
        if v >= 0:
            right.text(v + 0.2, yi, text, va="center", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
        else:
            right.text(0.2, yi, text, va="center", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
    right.set_yticks(y, names)
    lowest = min(0.0, min(values.values()))
    right.set_xlim(lowest - 1.0, max(max(values.values()), 2.0) * 2.6)
    right.axvline(0, color=PALETTE["ink"], linewidth=1)
    right.set_xlabel(f"Reward minus {num(penalty)} x risk (cross hatch: not authorized; slash hatch: over the limit)")
    right.set_ylabel("Action")
    mode = "a bypass skips the check" if bypass else "every route is checked"
    right.set_title(f"Penalty {num(penalty)}; {mode}", fontsize=11.5)
    right.grid(axis="y", alpha=0)

    removed_authority = [r["name"] for r in rows if not r["authorized"]]
    removed_risk = [r["name"] for r in rows if r["authorized"] and not r["risk_feasible"]]
    metrics = {
        "Penalty pick over all rows": top,
        "Penalty pick among authorized rows": authorized_pick,
        "Gate pick (authority, then limit, then reward)": constrained if constrained else "undefined (no row is eligible)",
        "Eligible actions": f"{m['feasible_count']} of {len(rows)}",
        "Removed by authority": ", ".join(removed_authority) if removed_authority else "none",
        "Removed by the risk limit": ", ".join(removed_risk) if removed_risk else "none",
        "Row that executes": executed_text,
    }
    by_name = {r["name"]: r for r in rows}
    sums = "; ".join(f"{n}: {num(by_name[n]['reward'])} - {num(penalty)} x {num(by_name[n]['risk'], 2)} = {fmt(by_name[n]['penalized_value'], 2)}" for n in names)
    eligible = [r for r in rows if r["authorized"] and r["risk_feasible"]]
    elig_text = ", ".join(f"{r['name']} (reward {num(r['reward'])})" for r in eligible)
    if constrained is None:
        verdict = "No action is both authorized and within the limit, so there is no gate pick and the controller must abstain or ask for a new alternative."
    else:
        verdict = f"Eligible rows are {elig_text}; the highest reward among them is {constrained}."
    forbidden = (" Fast-release is not authorized, so no limit or penalty makes it eligible." if "fast-release" in removed_authority else "")
    if bypass:
        gap = (f" A bypass lets the controller's own top row, {executed}, reach the actuator without the check, so the gate pick above constrains nothing on that route."
               + (" Here the penalty row is also an eligible row, so this state looks safe even though the check was skipped." if executed in [r["name"] for r in eligible] else
                  " Here that row is not eligible, so the unchecked route executes what the gate would have refused."))
    else:
        gap = f" Every route passes the check, so the row that executes is the gate pick, {executed_text}."
    interpretation = f"{sums}. The penalty rule picks {top} from all rows, without asking about authority. {verdict}{forbidden}{gap}"
    steps = [
        "Score every row: reward - penalty x risk (the sums above).",
        f"Penalty rule over all rows: {top}.",
        f"Authority removes: {', '.join(removed_authority) if removed_authority else 'nothing'}.",
        f"Risk limit {num(limit, 2)} then removes: {', '.join(removed_risk) if removed_risk else 'nothing'}.",
        f"Highest reward among the {len(eligible)} eligible rows: {constrained if constrained else 'none'}.",
        f"Row that executes: {executed_text}.",
    ]
    alt = (f"Left: reward against risk for four actions with a dashed risk limit at {num(limit, 2)}; the gate picks {constrained if constrained else 'nothing'}. "
           f"Right: blended score of each action at penalty {num(penalty)}; the penalty rule picks {top}. Route: {mode}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 22,
    "title": "Safe Enough to Act",
    "subtitle": "A high reward does not make an action permitted: keep task return, measured cost and authority as separate records.",
    "summary": (
        "These four demonstrations follow the chapter from the choice between a fixed penalty and a declared limit, through "
        "what a one-update bound and a margin do and do not promise, to a tail measure, a spending budget and a gate that decides which "
        "actions may be considered at all. Each one changes a declared value and shows which rule reacts and which does not."
    ),
    "ask_skill": {
        "prompt": ("I have a list of actions, each with a reward, an expected adverse-event probability and a yes or no permission, "
                   "plus a risk limit and a penalty. Show which actions authority removes, which the risk limit removes, "
                   "what a penalty rule would have chosen instead, and what to do if nothing is left."),
    },
    "demos": [
        {
            "id": "C22-D01",
            "title": "A penalty hides an exchange rate",
            "question": "With the same two policies, when does a fixed penalty choose a policy that a cost limit would remove?",
            "equations": [EQ_SCORE, EQ_CONSTRAINT],
            "symbols": (
                "Ret is the expected reward of a policy and Cost its expected measured cost. The multiplier lambda_safe is the "
                "exchange rate: how many reward units one cost unit is worth. d_1 is the declared cost limit. The penalty rule picks the "
                "larger blended score; the constraint rule keeps only policies with cost at most the limit, then picks the larger reward. "
                "The chapter's table has Careful at reward 8 and cost 0.5, Aggressive at 12 and 1.5, limit 1. Workbench VI.1 has Careful at 7 and 0.5, "
                "Aggressive at 11 and 2, limit 1. The laboratory's transfer case has act at reward 20 and cost 0.01, wait at -1 and 0, limit 0. "
                "The best mix is the largest chance of the costlier policy that keeps expected cost within the limit, if randomising once before the "
                "episode is allowed (the workbench's reading)."
            ),
            "prediction": "In the chapter's table with limit 1, raise the multiplier through 2, 4 and 6. What does the penalty rule do, and does the constraint rule ever switch?",
            "prediction_options": [
                "The penalty rule picks Aggressive at 2, ties at 4 and picks Careful at 6; the constraint rule always picks Careful",
                "The penalty rule picks Careful at every multiplier",
                "The penalty rule picks Aggressive at every multiplier, so it always agrees with the constraint rule",
            ],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "The two scores cross where the reward gap 4 equals the cost gap 1 times the multiplier, at 4. The constraint rule never reads the multiplier. Switch the penalty control to see it.",
                "incorrect": "The scores 8 - 0.5 x m and 12 - 1.5 x m cross at m = 4, so the penalty rule changes its pick at the flip point while the constraint rule, which reads only the limit, stays on Careful. Switch the penalty control to see it.",
            },
            "explanation": (
                "Each policy's score falls with the multiplier at the rate of its own cost, so the policy with more cost loses ground faster. "
                "The lines cross at the reward gap divided by the cost gap. The constraint rule never uses the multiplier: it draws a boundary in the reward-cost plane "
                "and only policies on the allowed side are eligible, as in Figure 22.2. In the transfer case the multiplier would have to reach 2100 before the "
                "penalty rule gave up act, although act already breaks a limit of 0."
            ),
            "application": (
                "When a team reports that a penalty setting keeps cost down, ask whether cost is a preference with a "
                "defensible exchange rate or a limit. If it is a limit, state it as a limit and check each policy against it."
            ),
            "assumptions": (
                "One step, two policies, one cost, and expected values read as the whole story. Each flip point belongs to its two policies and reward scale, "
                "not to any other problem. Mixing assumes the choice of policy is made once before the episode so rewards and costs mix linearly; it does not "
                "make a forbidden action permitted. Even the constrained choice says nothing about a single bad episode or a hazard the cost leaves out."
            ),
            "misconception": {
                "title": "A large enough penalty works as a limit",
                "text": ("The chapter warns against presenting a fixed penalty as a satisfaction guarantee for a limit it was never designed to enforce. "
                         "In the transfer case at multiplier 100 the penalty rule still picks act: 20 - 100 x 0.01 = 19.00 beats -1.00, although act's cost 0.01 breaks the limit 0."),
            },
            "check": "Work this one by hand (3 is not an offered multiplier). In workbench VI.1 with the limit at 1 and the multiplier at 3, which policy does the penalty rule pick, and which does the constraint rule pick?",
            "answer": (
                "Careful: 7 - 3 x 0.5 = 5.5. Aggressive: 11 - 3 x 2 = 5. The penalty rule picks Careful (the flip point is 4 / 1.5 = 2.67, and 3 is above it). "
                "Aggressive costs 2, above the limit 1, so the constraint rule picks Careful too: here the two rules agree."
            ),
            "provenance": ("Constructed example: the chapter's own two-policy table, Mathematical Workbench problem VI.1 (Careful 7 and 0.5, Aggressive 11 and 2) and the laboratory's transfer case "
                           "(act and wait, limit 0, multiplier 100). The transfer case is also evaluated with the laboratory's risk and authority function; the other two have costs above 1 and are computed directly."),
            "source_section": "Fixed penalties make a hidden exchange rate",
            "source_anchor": "fixed-penalties-make-a-hidden-exchange-rate",
            "controls": [
                {"key": "case", "label": "Policies and limit", "values": ["table", "workbench", "transfer"], "default": "table",
                 "value_labels": ["Chapter table (limit 1)", "Workbench VI.1 (limit 1)", "Laboratory transfer (limit 0)"]},
                {"key": "penalty", "label": "Penalty multiplier", "values": [2, 4, 6, 100], "default": 2},
            ],
            "function": "penalty_picture",
        },
        {
            "id": "C22-D02",
            "title": "A bound permits excess, so leave a margin",
            "question": "How much can the modeled cost exceed the limit after one update, how large a step does a margin allow, and when does the margin cover it?",
            "equations": [EQ_BOUND, EQ_MARGIN],
            "symbols": (
                "d is the cost limit (10 here). delta is the step-size parameter of one update, the trust-region size measured by a KL-divergence condition. gamma is the discount factor. "
                "epsilon is the largest absolute expected constraint advantage over states (0.1 here). The fraction after d is the "
                "allowance, the most the bound lets the cost return rise above d. The margin, written epsilon_safe in the chapter, is room reserved below d "
                "(0.5 or 1.0 here), so the optimizer aims at the ceiling d minus margin."
            ),
            "prediction": "At discount 0.85 and margin 0.5, will a step size of 0.005 fit inside the margin? What about 0.02?",
            "prediction_options": [
                "Both fit inside the margin",
                "0.005 fits (allowance 0.378) and 0.02 does not (0.756)",
                "Neither fits",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Quadrupling the step only doubles the allowance, because it grows with sqrt(2 delta): 0.378 then 0.756, against a margin of 0.5. Switch the step control to see it.",
                "incorrect": "Compute sqrt(2 x 0.005) x 0.85 x 0.1 / 0.0225 = 0.378, which is under 0.5, and twice that, 0.756, for a step of 0.02, which is over 0.5. Switch the step control to see it.",
            },
            "explanation": (
                "The allowance is sqrt(2 delta) times gamma times epsilon, divided by (1 - gamma) squared. A larger trust region lets the update treat its local picture as informative "
                "farther away, which raises the allowance in proportion to the square root of the step, and a discount nearer 1 blows it up through the squared denominator. "
                "The margin is a separate choice: it only helps when it is at least as large as the allowance, and the right-hand curve shows the largest step it covers."
            ),
            "application": (
                "Before citing the proposition to justify a safety margin, compute the allowance for your own step size, "
                "discount and advantage, and set the margin from that number rather than from habit."
            ),
            "assumptions": (
                "The bound concerns one ideal update inside the modeled problem; it is not a statement about a training run, "
                "a sampled update or a changed deployment. The values here are constructed. The lower row applies the bound "
                "with the ceiling in the role of the limit (d replaced by d minus the margin), which is this reader's illustration of the margin idea. "
                "The target (what the optimizer asks for), the bound (what the theorem permits) and observed behavior (what an experiment records) are three different things; "
                "this figure shows the first two only."
            ),
            "misconception": {
                "title": "Constrained means the cost stays below the limit",
                "text": ("Proposition 2 gives a bound on how far above the limit the new cost return may be, not a promise that it is below the limit. "
                         "The right side of Equation (22.3) is d plus a nonnegative allowance, so aiming at the limit always leaves a positive modeled overshoot."),
            },
            "scope_note": {
                "text": ("CPO's one-update result does not prove that a whole training run, or an altered deployment, satisfies a constraint. "
                         "A clear optimization claim can grant limited authority only within the threat model, measurement, margin and update assumptions that make it true."),
                "source_section": "What this does not settle",
            },
            "check": "Work this one by hand, using the control for the margin. With step size 0.005, discount 0.9 and advantage 0.1, what is the allowance, and does a margin of 0.5 cover it? What about a margin of 1.0?",
            "answer": ("sqrt(2 x 0.005) = 0.1, so 0.1 x 0.9 x 0.1 / (1 - 0.9)^2 = 0.009 / 0.01 = 0.9. That is above 0.5, so a margin of 0.5 does not cover it, "
                       "and below 1.0, so a margin of 1.0 does."),
            "provenance": "Constructed example: the chapter's bound evaluated with values defined for this reader (limit 10, advantage 0.1, margins 0.5 and 1.0).",
            "source_section": "A constraint is not a promise",
            "source_anchor": "a-constraint-is-not-a-promise",
            "controls": [
                {"key": "step", "label": "Step size delta", "values": [0.005, 0.02], "default": 0.005},
                {"key": "discount", "label": "Discount factor gamma", "values": [0.5, 0.85, 0.9], "default": 0.85},
                {"key": "margin", "label": "Safety margin", "values": [0.5, 1.0], "default": 0.5},
            ],
            "function": "bound_picture",
        },
        {
            "id": "C22-D03",
            "title": "Two other risk contracts: a tail and a budget",
            "question": "For a rare bad episode, how far apart are mean cost and tail severity, and how does a risk budget shrink as charged actions spend it?",
            "equations": [EQ_CVAR, EQ_BUDGET],
            "symbols": (
                "C is the cost of one episode: 100 with probability 0.01, otherwise 0 (the chapter's lottery). alpha sets the tail: the worst "
                "share 1 - alpha of episodes. z is a cutoff, and (C - z)+ is the amount by which C exceeds z, or 0. CVaR is "
                "the smallest value the bracket takes as z varies, which equals the average cost over the worst 1 - alpha share. "
                "In the budget, B is the stated cumulative risk budget, b_t what remains before decision t, and r-hat the declared conservative charge of the chosen action; "
                "the four charges 0.04, 0.05, 0.03 and 0.05 are values defined for the reader, and a refused action is replaced by a fallback that charges 0."
            ),
            "prediction": "For a bad episode with probability 0.01, is the tail average larger at alpha 0.9 or at alpha 0.99?",
            "prediction_options": ["Larger at alpha 0.9", "Larger at alpha 0.99 (100 against 10)", "The same at both"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "At 0.99 the tail is exactly the bad episodes, so it averages 100. At 0.9 the tail is ten times wider than the bad episodes, so zeros dilute it: 1.0 / 0.1 = 10. Switch the alpha control to see it.",
                "incorrect": "At alpha 0.9 the worst 10 percent of episodes holds the 1 percent bad ones and nine parts zeros, so the average is 1.0 / 0.1 = 10; at 0.99 it is 100. Switch the alpha control to see it.",
            },
            "explanation": (
                "For this lottery the bracket is a bent line in z, so its smallest value sits at z = 0 or z = 100. At z = 0 "
                "it equals the mean divided by the tail share; at z = 100 it equals 100. CVaR is the smaller of the two, "
                "so a tail wider than the bad episode dilutes it with zeros. The budget is a different contract: it is an accounting state that falls by each charge, "
                "and a charge larger than what remains cannot be taken, even when a smaller one proposed later still fits."
            ),
            "application": (
                "If one rare, severe episode is the worry, a limit on mean cost can look small while the tail measure is large. "
                "State which one the limit is about, and why. For a bounded horizon, keep a running budget and refuse a charged action that exceeds what remains."
            ),
            "assumptions": (
                "A single two-outcome lottery and four charges defined for the reader. CVaR asks for average severity in a declared upper tail, not a promise that no episode is bad. "
                "The budget rule prevents one action from exceeding the remaining authority; it does not prove the charges are calibrated, independent, complete or safe beyond the declared horizon."
            ),
            "misconception": {
                "title": "A tail measure promises that no episode is bad",
                "text": ("The chapter says CVaR asks for average severity in a declared upper tail, not a promise that no episode is bad, and that none of the measures covers a hazard the cost variable omits. "
                         "Here CVaR is 100 at alpha 0.99, yet the worst episode still happens with probability 0.01."),
            },
            "scope_note": {
                "text": ("Expected auxiliary-cost constraints are not sufficient for every safety problem: a rare catastrophic outcome, a distribution shift, an unobserved state, "
                         "a human authorization boundary or an adversarial interaction may require a different risk measure, monitoring system, physical safeguard or refusal rule."),
                "source_section": "What this does not settle",
            },
            "check": "Work this one by hand (a budget of 0.08 is not offered). With budget 0.08 and the charges 0.04, 0.05, 0.03, 0.05 proposed in order, which are charged and what is left? And a bad episode costs 100 with probability 0.02: what is CVaR at alpha 0.97?",
            "answer": ("Budget: 0.04 <= 0.08 is charged, leaving 0.04; 0.05 > 0.04 is refused; 0.03 <= 0.04 is charged, leaving 0.01; 0.05 > 0.01 is refused. Left 0.01. "
                       "CVaR: tail share 0.03; at z = 0 the bracket is 2 / 0.03 = 66.67, at z = 100 it is 100, so CVaR is 66.67 while the mean cost is 2."),
            "provenance": "Constructed example: the chapter's lottery (cost 100 with probability 0.01, else 0) with other tail levels, and a four-decision budget whose charges are defined for this reader.",
            "source_section": "Other risk contracts",
            "source_anchor": "other-risk-contracts",
            "controls": [
                {"key": "alpha", "label": "Tail level alpha", "values": [0.9, 0.95, 0.99, 0.995], "default": 0.99},
                {"key": "budget", "label": "Risk budget B", "values": [0.05, 0.1, 0.2], "default": 0.1},
            ],
            "function": "risk_contracts_picture",
        },
        {
            "id": "C22-D04",
            "title": "Authority first, risk limit second, reward last",
            "question": "Which actions may be considered at all, which of those has the best reward, and what happens when one route to the actuator skips the check?",
            "equations": [EQ_CONSTRAINT, EQ_SCORE],
            "symbols": (
                "Each action has a reward, an expected adverse-event probability (risk) and a yes or no current permission. "
                "The risk limit is the largest probability allowed. The penalty is the reward deducted per unit of risk. "
                "The gate keeps only actions that are authorized and within the risk limit; the gate pick is the "
                "highest reward among those. In the displayed equations, Ret is the reward, Cost is the risk, d_i is the risk limit and "
                "lambda_safe is the penalty, with each action standing in for a policy pi. Authority, the yes or no permission, is an "
                "extra condition that the equations do not show. A bypass is a route to the actuator that does not pass the check."
            ),
            "prediction": "Raise the risk limit from 0.1 to 0.25. Does fast-release become eligible? Which action does the gate now pick?",
            "prediction_options": [
                "Fast-release becomes eligible and wins",
                "Risky-authorized becomes the gate pick; fast-release stays out",
                "Reviewed-release stays the gate pick",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Risky-authorized has risk 0.2, within 0.25, and reward 8, so it wins the eligible rows. Fast-release is not authorized, so no limit admits it. Switch the risk limit control to see it.",
                "incorrect": "Risk 0.2 is within the new limit 0.25, so risky-authorized (reward 8) joins the eligible rows and beats reviewed-release (5). Fast-release is not authorized, so a looser limit cannot admit it. Switch the risk limit control to see it.",
            },
            "explanation": (
                "The penalty rule scores every row by reward minus penalty times risk, so a high-reward forbidden row can win. "
                "The gate removes rows before any score is used: authority is a yes or no condition, so no limit or penalty "
                "setting grants it. A looser risk limit can bring back an over-limit row but never a forbidden one. A gate only constrains routes that pass through it: "
                "with a bypass, the check exists but the unauthorized row can still run."
            ),
            "application": (
                "For an agent that can call tools, list each action with its permission and risk, remove what is not permitted, "
                "then rank the rest. Keep an explicit abstain row, provided abstain is authorized and its risk is within the limit, so the set is never empty. "
                "Confirm that every route to the actuator passes the gate."
            ),
            "assumptions": (
                "Rewards, risks and permissions are supplied values; nothing here estimates risk. An expected-risk limit is a statement "
                "about an average, so an action with risk 0.05 can still end badly. A large enough penalty can mimic a "
                "gate in one case and fail in the next. In the bypass states the unchecked route is assumed to run the controller's own penalty pick; "
                "that is this reader's illustration of the chapter's complete-mediation requirement."
            ),
            "misconception": {
                "title": "A system with only an objective has a gate",
                "text": ("The chapter separates a safety objective, which changes how outcomes are ranked (Equation 22.2), from a safety gate, which decides whether an action path may proceed at all. "
                         "Confusion begins when a system that has only an objective is described as though it had a gate."),
            },
            "scope_note": {
                "text": ("Expected auxiliary-cost constraints are not sufficient for every safety problem: a rare catastrophic outcome, a distribution shift, an unobserved state, "
                         "a human authorization boundary or an adversarial interaction may require a different risk measure, monitoring system, physical safeguard or refusal rule."),
                "source_section": "What this does not settle",
            },
            "check": "Work this one by hand (0.2 is not an offered limit). With the risk limit at 0.2 and the penalty at 5, which action does the gate pick, and is fast-release eligible?",
            "answer": (
                "Eligible rows are authorized with risk at most 0.2: reviewed-release (0.05), risky-authorized (0.2, which meets the "
                "limit exactly) and abstain (0). Rewards 5, 8 and 0, so risky-authorized wins. Fast-release is not authorized, so it stays out."
            ),
            "provenance": "Constructed example: the laboratory's four-action example, evaluated with the laboratory's risk and authority function. The four rewards, risks and permissions are not taken from the chapter, whose section supports only the distinction between an objective and a gate. The bypass is defined for this reader.",
            "source_section": "Authority is an operating envelope",
            "source_anchor": "authority-is-an-operating-envelope",
            "controls": [
                {"key": "limit", "label": "Risk limit", "values": [0, 0.1, 0.25], "default": 0.1},
                {"key": "penalty", "label": "Penalty per unit of risk", "values": [5, 25], "default": 5},
                {"key": "route", "label": "Routes to the actuator", "values": ["checked", "bypass"], "default": "checked",
                 "value_labels": ["Every route passes the check", "One route skips the check"]},
            ],
            "function": "gate_picture",
        },
    ],
}

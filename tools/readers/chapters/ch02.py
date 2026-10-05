"""Chapter 2 reader: How to Measure Emergence.

Deepened (group 1): D01 now carries the book's four-cell cases, the workbench pair I.1 and I.3, a budget
and a score-scale lens and the amount-and-share conditions; D03 walks the maple-river route (Figure 2.1)
and shows a leaking removal control.

Four demonstrations built on Equations (2.1) to (2.3). Demonstrations 1, 2
and 3 call the laboratory's own four-cell function
(math_ai_agents.chapters.ch02.evaluate), so the reader, the notebook and the
chapter skill agree. Demonstration 4 adds the chapter's remark about how
measurement error accumulates in the contrast. Every number is a constructed
teaching value; the values in Demonstrations 1 to 3 include the book's
Table 2.1 and the book's second (negative) worked example.
"""
import math

from matplotlib.patches import Rectangle

from math_ai_agents.chapters.ch02 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

EQ_GAMMA = r"\Gamma(p;i)=U(\{\theta,p,i\})-U(\{\theta,p\})-U(\{\theta,i\})+U(\{\theta\})"
EQ_SPLIT = (
    r"\begin{aligned}U(\{\theta,p,i\})-U(\{\theta\})&=\bigl[U(\{\theta,p\})-U(\{\theta\})\bigr]\\"
    r"&\quad+\bigl[U(\{\theta,i\})-U(\{\theta\})\bigr]+\Gamma(p;i).\end{aligned}"
)
EQ_RHO = r"\rho_\Gamma=\frac{\Gamma(p;i)}{U(\{\theta,p,i\})-U(\{\theta\})}"

TOL = 1e-9
BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


def lab_four_cells(neither, p_only, i_only, both, budgets=(10, 10, 10, 10)):
    """Interaction contrast, joint gain and signed ratio from the laboratory's own function."""
    out = evaluate({"scores": [neither, p_only, i_only, both], "budgets": list(budgets)})["metrics"]
    return out["interaction"], out["joint_gain"], out["signed_share"], out["fraction_share"]


def sign_word(gamma):
    if abs(gamma) <= TOL:
        return "zero"
    return "positive" if gamma > 0 else "negative"


def draw_grid(ax, neither, p_only, i_only, both, digits=2):
    """The four cells as a two by two grid; the cell with both operations is outlined."""
    cells = [
        (0, 0, "neither", neither, "#eef2f3"),
        (1, 0, "i only", i_only, "#dde7ea"),
        (0, 1, "p only", p_only, "#dde7ea"),
        (1, 1, "both", both, "#c6dadd"),
    ]
    for x, y, name, score, color in cells:
        ax.add_patch(
            Rectangle(
                (x - 0.5, y - 0.5), 1, 1, facecolor=color,
                edgecolor=PALETTE["teal"] if name == "both" else PALETTE["grey"],
                linewidth=3.0 if name == "both" else 1.2,
            )
        )
        ax.text(x, y + 0.13, name, ha="center", va="center", fontsize=11, color=PALETTE["ink"])
        ax.text(x, y - 0.13, fmt(score, digits), ha="center", va="center", fontsize=14, color=PALETTE["ink"], fontweight="bold")
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    ax.set_xticks([0, 1], ["off", "on"])
    ax.set_yticks([0, 1], ["off", "on"])
    ax.set_aspect("equal")
    ax.grid(False)
    ax.set_xlabel("Operation i (uses the clue)")
    ax.set_ylabel("Operation p (prepares the clue)")




# Demonstration 1: four cells, the book's cases, a budget lens and a score-scale lens

CASES = {
    "table": ("Table 2.1", (0.20, 0.30, 0.25, 0.80)),
    "additive": ("both at the additive 0.35", (0.20, 0.30, 0.25, 0.35)),
    "second": ("second example", (0.20, 0.55, 0.50, 0.70)),
    "workbench": ("workbench I.1 and I.3", (0.40, 0.52, 0.49, 0.58)),
}
WORKBENCH_DOUBLED = 0.73  # workbench I.1: the joint cell that received twice the resource allowance


def cube(x):
    return x ** 3


def fraction_reasons(gamma, joint, gain_p, gain_i):
    reasons = []
    if joint <= TOL:
        reasons.append("the joint gain is not positive")
    if gain_p < -TOL or gain_i < -TOL:
        reasons.append("an isolated gain is negative")
    if gamma < -TOL:
        reasons.append("the interaction contrast is negative")
    return reasons


def four_cells_picture(case="table", run="matched"):
    name, cells = CASES[case]
    neither, p_only, i_only, both = cells
    if case == "workbench" and run == "doubled":
        both = WORKBENCH_DOUBLED
    budgets = (10, 10, 10, 20) if run == "doubled" else (10, 10, 10, 10)
    digits = 2
    if run == "cubed":
        neither, p_only, i_only, both = (cube(v) for v in (neither, p_only, i_only, both))
        digits = 3
    gamma, joint, _, _ = lab_four_cells(neither, p_only, i_only, both, budgets)
    if abs(gamma) <= TOL:
        gamma = 0.0
    gain_p, gain_i = p_only - neither, i_only - neither
    additive = neither + gain_p + gain_i
    if abs(gamma - (both - additive)) > 1e-9:
        raise AssertionError("laboratory contrast disagrees with the written sum")
    matched = budgets[0] == budgets[3]
    reasons = fraction_reasons(gamma, joint, gain_p, gain_i)
    ratio = gamma / joint if joint > TOL else None

    fig, (grid, water) = new_figure(ncols=2, height=4.3)
    draw_grid(grid, neither, p_only, i_only, both, digits)
    grid.set_title("The four measured scores" + ("" if matched else " (joint run: 2x budget)"), fontsize=11.5)

    steps = [
        ("neither", 0.0, neither, PALETTE["grey"], None),
        ("gain\nfrom p", neither, p_only, PALETTE["navy"], None),
        ("gain\nfrom i", p_only, p_only + gain_i, PALETTE["navy"], None),
        ("Gamma", additive, both, PALETTE["gold"], "///" if gamma < -TOL else None),
        ("both", 0.0, both, PALETTE["teal"], None),
    ]
    for k, (label, start, end, color, hatch) in enumerate(steps):
        water.bar(k, end - start, bottom=start, color=color, width=0.62, hatch=hatch,
                  edgecolor="white" if hatch is None else PALETTE["ink"], linewidth=1.0)
        top = max(start, end)
        if label == "Gamma":
            text = fmt(gamma, digits) if gamma < -TOL else ("+" + fmt(gamma, digits) if gamma > TOL else fmt(0, digits))
        elif label.startswith("gain"):
            text = "+" + fmt(end - start, digits)
        else:
            text = fmt(end, digits)
        water.annotate(text, (k, top), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                       fontsize=10.5, color=PALETTE["ink"])
    water.plot([2.31, 2.69], [additive, additive], color=PALETTE["ink"], linestyle="dashed", linewidth=1.2)
    water.set_xticks(range(5), ["neither", "gain\nfrom p", "gain\nfrom i", "$\\Gamma$", "both"])
    water.set_xlim(-0.6, 4.6)
    water.set_ylim(0, 1.0)
    water.set_xlabel("Build the joint score step by step")
    water.set_ylabel("Score U (higher is better)" if run != "cubed" else "Cubed score (higher is better)")
    water.set_title("Gamma is what the two gains leave over", fontsize=11.5)

    reading = sign_word(gamma)
    metrics = {
        "Joint gain (both minus neither)": fmt(joint, digits),
        "Additive prediction": fmt(additive, digits),
        "Interaction contrast Gamma": fmt(gamma, digits),
        "Sign of Gamma": reading,
        "Ratio Gamma / joint gain": fmt(ratio, 2) if ratio is not None else "undefined (the joint gain is zero)",
        "Valid as a fraction": "yes" if not reasons else "no (" + "; ".join(reasons) + ")",
        "Budgets matched": "yes" if matched else "no (the joint run had twice the allowance)",
    }
    sc = lambda x: signed(x, digits)
    calc = (f"Gamma = {sc(both)} - {sc(p_only)} - {sc(i_only)} + {sc(neither)} = {sc(gamma)}. "
            f"The additive prediction is {sc(p_only)} + {sc(i_only)} - {sc(neither)} = {sc(additive)}, "
            f"and the pair scored {sc(both)}. Joint gain = {sc(both)} - {sc(neither)} = {sc(joint)}.")
    if reading == "positive":
        meaning = (f"Gamma is positive: the pair delivers {sc(gamma)} more than the two isolated gains "
                   f"({sc(gain_p)} + {sc(gain_i)} = {sc(gain_p + gain_i)}) predict, on this task and score only.")
    elif reading == "zero":
        meaning = ("Gamma is zero: the joint gain is exactly the sum of the two isolated gains. The pair may still score "
                   "well and both operations may help, but there is no extra pairwise contribution to assign.")
    else:
        meaning = (f"Gamma is negative: the joint gain {sc(joint)} is smaller than the isolated gains add up to "
                   f"({sc(gain_p + gain_i)}). Overlapping benefits, saturation or interference could each cause "
                   "that, and the four numbers alone do not say which.")
    if ratio is None:
        share = "The ratio would divide by a zero joint gain, so it is undefined."
    elif not reasons:
        share = (f"Ratio = {sc(gamma)} / {sc(joint)} = {fmt(ratio, 2)}; the three conditions hold, so it is a fraction between 0 and 1.")
    else:
        share = (f"Ratio = {sc(gamma)} / {sc(joint)} = {sc(ratio)}: a signed diagnostic, not a fraction of cooperation, "
                 f"because {' and '.join(reasons)}.")
    if run == "doubled":
        budget = ("The joint run had twice the allowance of the other three (20 against 10), so the four cells are not matched "
                  "and the contrast does not compare the components under equal resources.")
        if case == "workbench":
            budget += " A matched rerun (the other run in this control) gives the joint score 0.58 instead of 0.73."
        else:
            budget += (" This case has no doubled-run score, so only the budget flag changes: the four scores, Gamma and the ratio "
                       "are the same as in the matched run.")
    elif run == "cubed":
        budget = ("Each score was cubed first, a nonlinear change of scale defined for this reader. The chapter warns that such a "
                  "change can alter the contrast, including its sign, so the scale has to be declared.")
        o_neither, o_p, o_i, o_both = cells
        orig = o_both - o_p - o_i + o_neither
        if abs(orig) <= TOL:
            budget += f" Here it does: on the original scores Gamma is exactly 0.00, and after cubing it is {gamma:.3f}."
        elif (orig < 0) != (gamma < 0):
            budget += (f" Here it does: on the original scores Gamma is {orig:.2f}, and after cubing it is "
                       f"{gamma:+.3f}, so the sign flips.")
    else:
        budget = "All four budgets are equal, so the four cells are a matched comparison; they still do not identify a mechanism."
    budget_short = {"doubled": "Budgets: 10, 10, 10 and 20, so the cells are not matched; the contrast is not a comparison under equal resources.",
                    "cubed": "Each score cubed first: a nonlinear change of scale can change the contrast, including its sign.",
                    "matched": "All four budgets are equal: a matched comparison, which still does not identify a mechanism."}[run]
    interpretation = f"{calc} {meaning} {share} {budget}"
    worked = [
        f"Isolated gains: p = {sc(p_only)} - {sc(neither)} = {sc(gain_p)}; i = {sc(i_only)} - {sc(neither)} = {sc(gain_i)}.",
        f"Joint gain = {sc(both)} - {sc(neither)} = {sc(joint)}.",
        f"Gamma = {sc(both)} - {sc(p_only)} - {sc(i_only)} + {sc(neither)} = {sc(gamma)}.",
        f"Equation (2.2) check: {sc(gain_p)} + {sc(gain_i)} + {sc(gamma)} = {sc(gain_p + gain_i + gamma)}, the joint gain.",
        share,
        budget_short,
    ]
    alt = (f"Left, a two by two grid of the four scores neither {sc(neither)}, p only {sc(p_only)}, i only {sc(i_only)}, both {sc(both)}. "
           f"Right, a step chart building the joint score from the neither score, the two gains and Gamma = {sc(gamma)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 2

SYSTEM_A = (0.20, 0.30, 0.25, 0.80)


def system_b(baseline):
    """Second constructed system: both single scores sit just above its baseline; the pair scores 0.80."""
    return (baseline, baseline + 0.02, baseline + 0.01, 0.80)


def baseline_picture(baseline_b=0.70, method="four"):
    baseline_b = float(baseline_b)
    systems = {"System A": SYSTEM_A, "System B": system_b(baseline_b)}
    four, three = {}, {}
    for name, (u00, u10, u01, u11) in systems.items():
        gamma, _, _, _ = lab_four_cells(u00, u10, u01, u11)
        four[name] = gamma
        three[name] = u11 - u10 - u01
        if abs(three[name] - (gamma - u00)) > 1e-9:
            raise AssertionError("three-cell remainder should equal Gamma minus the baseline")
    est = four if method == "four" else three

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    names = list(systems)
    for k, name in enumerate(names):
        u00, _, _, u11 = systems[name]
        y = 1 - k
        left.barh(y, u00, color="#c4d0dc", height=0.5, edgecolor=PALETTE["grey"], linewidth=1.0)
        left.barh(y, u11 - u00, left=u00, color=PALETTE["teal"], height=0.5, edgecolor="white")
        if u00 >= 0.12:
            left.text(u00 / 2, y, f"neither\n{fmt(u00, 2)}", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"])
        else:
            left.text(u00 / 2, y, fmt(u00, 2), ha="center", va="center", fontsize=10.5, color=PALETTE["ink"])
        if u11 - u00 >= 0.2:
            left.text(u00 + (u11 - u00) / 2, y, f"added\n{fmt(u11 - u00, 2)}", ha="center", va="center", fontsize=10.5, color="white")
        else:
            left.text(u11 + 0.015, y, f"added\n{fmt(u11 - u00, 2)}", ha="left", va="center", fontsize=10.5, color=PALETTE["ink"])
    left.set_yticks([1, 0], names)
    left.set_xlim(0, 1.0)
    left.set_ylim(-0.5, 1.5)
    left.set_xlabel("Intact score with both operations (both systems reach 0.80)")
    left.set_ylabel("System")
    left.set_title("Same total, different starting point", fontsize=11.5)
    left.grid(axis="y", alpha=0)

    label_text = "Four-cell Gamma" if method == "four" else "Three cells: both - p - i"
    right_names = ["A", "B"]
    vals = [est[n] for n in names]
    colors = [PALETTE["teal"] if method == "four" else PALETTE["terracotta"]] * 2
    hatch = None if method == "four" else "///"
    right.bar(range(2), vals, color=colors, width=0.55, hatch=hatch,
              edgecolor="white" if hatch is None else PALETTE["ink"], linewidth=1.0)
    for k, v in enumerate(vals):
        right.annotate(fmt(v, 2), (k, v), xytext=(0, 5 if v >= 0 else -5), textcoords="offset points", ha="center",
                       va="bottom" if v >= 0 else "top", fontsize=10.5, color=PALETTE["ink"])
    right.axhline(0, color=PALETTE["ink"], linewidth=1.0)
    right.set_xticks(range(2), [f"System {n}" for n in right_names])
    right.set_xlim(-0.6, 1.6)
    right.set_ylim(-0.85, 0.65)
    right.set_xlabel(label_text)
    right.set_ylabel("Estimated contribution of the pair")
    right.set_title("The estimate each method reports", fontsize=11.5)

    u00b, u10b, u01b, u11b = systems["System B"]
    metrics = {
        "System A baseline": fmt(SYSTEM_A[0], 2),
        "System B baseline": fmt(u00b, 2),
        "System A, four-cell Gamma": fmt(four["System A"], 2),
        "System B, four-cell Gamma": fmt(four["System B"], 2),
        "System A, three cells": fmt(three["System A"], 2),
        "System B, three cells": fmt(three["System B"], 2),
    }
    gb = four["System B"]
    four_calc = (f"System A: Gamma = 0.80 - 0.30 - 0.25 + 0.20 = {fmt(four['System A'], 2)}. System B: Gamma = "
                 f"0.80 - {fmt(u10b, 2)} - {fmt(u01b, 2)} + {fmt(u00b, 2)} = {fmt(gb, 2)}.")
    three_calc = (f"System A: 0.80 - 0.30 - 0.25 = {fmt(three['System A'], 2)}. System B: 0.80 - {fmt(u10b, 2)} - "
                  f"{fmt(u01b, 2)} = {fmt(three['System B'], 2)}.")
    if method == "four":
        ga = four["System A"]
        if abs(gb - ga) <= 1e-9:
            compare = "equal to"
        else:
            compare = "smaller than" if gb < ga else "larger than"
        text = (f"{four_calc} Both systems score 0.80, but B starts at {fmt(u00b, 2)} and A at 0.20, so B's pair adds "
                f"0.80 - {fmt(u00b, 2)} = {fmt(0.80 - u00b, 2)} of improvement against {fmt(0.80 - SYSTEM_A[0], 2)} for A. "
                f"B's contrast {fmt(gb, 2)} is {compare} A's {fmt(ga, 2)}. Check: "
                f"{fmt(gb, 2)} is the joint gain {fmt(0.80 - u00b, 2)} minus the isolated gains 0.02 + 0.01 = 0.03. "
                "Look at the baseline before comparing contrasts.")
    else:
        text = (f"{three_calc} Leaving out the neither score subtracts the baseline twice, so this remainder is Gamma minus "
                f"the baseline: A gives {fmt(four['System A'], 2)} - 0.20 = {fmt(three['System A'], 2)}, and B gives "
                f"{fmt(gb, 2)} - {fmt(u00b, 2)} = {fmt(three['System B'], 2)}. The number drifts with the baseline "
                "instead of measuring the pair, which is why the fourth cell is measured.")
    worked = [
        f"System A: Gamma = 0.80 - 0.30 - 0.25 + 0.20 = {fmt(four['System A'], 2)}.",
        f"System B: baseline {fmt(u00b, 2)}, singles {fmt(u10b, 2)} and {fmt(u01b, 2)}; Gamma = 0.80 - {fmt(u10b, 2)} - {fmt(u01b, 2)} + {fmt(u00b, 2)} = {fmt(gb, 2)}.",
        f"Three cells, leaving out the baseline: A = 0.80 - 0.30 - 0.25 = {fmt(three['System A'], 2)}; B = 0.80 - {fmt(u10b, 2)} - {fmt(u01b, 2)} = {fmt(three['System B'], 2)}.",
        f"Each three-cell number is Gamma minus the baseline: A {fmt(four['System A'], 2)} - 0.20 = {fmt(three['System A'], 2)}; B {fmt(gb, 2)} - {fmt(u00b, 2)} = {fmt(three['System B'], 2)}.",
    ]
    alt = (f"Left, two bars both reaching 0.80, system A from a baseline of 0.20 and system B from a baseline of {fmt(u00b, 2)}. "
           f"Right, the estimate each method reports: {label_text} gives {fmt(vals[0], 2)} for A and {fmt(vals[1], 2)} for B.")
    return fig, metrics, text, {"alt": alt, "steps": worked}




# Demonstration 3: the maple-river route and a removal control that leaks

BASE_CELLS = {"neither": 0.20, "p": 0.30, "i": 0.25, "both": 0.80}  # Table 2.1
CELL_NAMES = {"neither": "neither", "p": "p only", "i": "i only", "both": "both"}
CELL_ORDER = ["neither", "p", "i", "both"]


def leaky_cells(leak):
    """p-disabled cells borrow a share `leak` of the matching p-enabled cell (a model defined for this reader)."""
    b = BASE_CELLS
    return {
        "neither": b["neither"] + leak * (b["p"] - b["neither"]),
        "p": b["p"],
        "i": b["i"] + leak * (b["both"] - b["i"]),
        "both": b["both"],
    }


def route_picture(cell="both", leak=0.0):
    leak = float(leak)
    cells = leaky_cells(leak)
    gamma, joint, _, _ = lab_four_cells(cells["neither"], cells["p"], cells["i"], cells["both"])
    if abs(gamma) <= TOL:
        gamma = 0.0
    clean_gamma, _, _, _ = lab_four_cells(*(BASE_CELLS[k] for k in CELL_ORDER))
    if abs(gamma - clean_gamma * (1 - leak)) > 1e-9:
        raise AssertionError("leaky contrast should equal the clean contrast times (1 - leak)")
    p_on = cell in ("p", "both")
    i_on = cell in ("i", "both")

    fig, (route, curve) = new_figure(ncols=2, height=4.6)
    route.axis("off")
    route.set_xlim(0, 1)
    route.set_ylim(0, 1)
    route.set_title("Figure 2.1 route, cell: " + CELL_NAMES[cell], fontsize=11.5)
    tokens = [(0.08, "maple"), (0.30, "river"), (0.52, "..."), (0.70, "maple"), (0.92, "river?")]
    for x, word in tokens:
        route.text(x, 0.52, word, ha="center", va="center", fontsize=11.5, color=PALETTE["ink"],
                   bbox={"boxstyle": "round,pad=0.3", "fc": "#eef2f3", "ec": PALETTE["grey"]})
    p_color = PALETTE["gold"] if p_on else PALETTE["grey"]
    i_color = PALETTE["teal"] if i_on else PALETTE["grey"]
    route.annotate("", xy=(0.10, 0.62), xytext=(0.28, 0.62),
                   arrowprops={"arrowstyle": "->", "color": p_color, "lw": 2.4 if p_on else 1.4,
                               "linestyle": "-" if p_on else "dashed", "connectionstyle": "arc3,rad=-0.5"})
    route.annotate("", xy=(0.32, 0.42), xytext=(0.68, 0.42),
                   arrowprops={"arrowstyle": "->", "color": i_color, "lw": 2.4 if i_on else 1.4,
                               "linestyle": "-" if i_on else "dashed", "connectionstyle": "arc3,rad=0.35"})
    route.text(0.19, 0.84, "P tags river" if p_on else "P replaced by its control", ha="center", va="center",
               fontsize=10.5, color=p_color, fontweight="bold")
    route.text(0.50, 0.22, "I looks back for the tag" if i_on else "I replaced by its control", ha="center", va="center",
               fontsize=10.5, color=i_color, fontweight="bold")
    if cell == "both":
        outcome = "I finds the tag and promotes river."
    elif cell == "p":
        outcome = "The tag is written but nothing reads it."
    elif cell == "i":
        outcome = ("I searches for a tag that was never written." if leak == 0
                   else f"I finds a tag that leaked through: {fmt(leak, 2)} of P's influence survives.")
    else:
        outcome = ("No route at all." if leak == 0 else f"No route, but {fmt(leak, 2)} of P's influence survives in the pattern.")
    route.text(0.5, 0.07, wrap_text(outcome, 46) + f"\nMeasured score: {fmt(cells[cell], 3)}", ha="center", va="center",
               fontsize=10.5, color=PALETTE["ink"])

    lams = [0.0, 0.5, 1.0]
    xs = [i / 100 for i in range(101)]
    curve.plot(xs, [clean_gamma * (1 - x) for x in xs], color=PALETTE["gold"], linewidth=2)
    curve.axhline(0, color=PALETTE["ink"], linewidth=1.0, linestyle="dashed")
    for lam in lams:
        curve.plot([lam], [clean_gamma * (1 - lam)], "o", markersize=11 if abs(lam - leak) < 1e-9 else 6,
                   color=PALETTE["teal"] if abs(lam - leak) < 1e-9 else "white", markeredgecolor=PALETTE["ink"], markeredgewidth=1.3)
    label_point(curve, leak, gamma, f"Gamma = {fmt(gamma, 3)}", color=PALETTE["ink"], dx=-10 if leak > 0.7 else 10, dy=12,
                ha="right" if leak > 0.7 else "left", va="bottom").set_bbox(BOX)
    curve.set_xlim(-0.05, 1.05)
    curve.set_ylim(-0.08, 0.55)
    curve.set_xlabel("Share of p's influence that survives the control")
    curve.set_ylabel("Measured contrast Gamma")
    curve.set_title("A leaking control erases the contrast", fontsize=11.5)

    metrics = {
        "Selected cell": CELL_NAMES[cell],
        "Score of the selected cell": fmt(cells[cell], 3),
        "Influence of p that survives": fmt(leak, 2),
        "Neither / p only / i only / both": ", ".join(fmt(cells[k], 3) for k in CELL_ORDER),
        "Measured Gamma": fmt(gamma, 3),
        "Clean-control Gamma": fmt(clean_gamma, 2),
    }
    i_calc = f"i only = 0.25 + {fmt(leak, 2)} x (0.80 - 0.25) = {fmt(cells['i'], 3)}"
    n_calc = f"neither = 0.20 + {fmt(leak, 2)} x (0.30 - 0.20) = {fmt(cells['neither'], 3)}"
    g_calc = (f"Gamma = 0.80 - 0.30 - {fmt(cells['i'], 3)} + {fmt(cells['neither'], 3)} = {fmt(gamma, 3)}, "
              f"which is 0.45 x (1 - {fmt(leak, 2)}) = {fmt(0.45 * (1 - leak), 3)}")
    interpretation = (f"Cell {CELL_NAMES[cell]}: {outcome} Its measured score is {fmt(cells[cell], 3)}. With {fmt(leak, 2)} of p's "
                      f"influence surviving the control on the cells where p is off, {n_calc}, and {i_calc}. {g_calc}. "
                      + ("The control is clean, so the contrast is the Table 2.1 value 0.45." if leak == 0 else
                         "Equation (2.2) still balances exactly, but the number no longer measures the pair: validity lives in the controls, never in the algebra."))
    worked = [
        f"Selected cell: {CELL_NAMES[cell]}. P is {'on' if p_on else 'off'} and I is {'on' if i_on else 'off'}.",
        outcome,
        f"Cells with p off borrow {fmt(leak, 2)} of p's effect: {n_calc}.",
        f"{i_calc}.",
        f"Gamma = 0.80 - 0.30 - {fmt(cells['i'], 3)} + {fmt(cells['neither'], 3)} = {fmt(gamma, 3)}.",
        f"Check: 0.45 x (1 - {fmt(leak, 2)}) = {fmt(0.45 * (1 - leak), 3)}.",
    ]
    alt = (f"Left, the tokens maple, river, maple with arrows for the two operations; the {CELL_NAMES[cell]} cell scores {fmt(cells[cell], 3)}. "
           f"Right, a falling line of the measured contrast against the share of p's influence that survives, now at Gamma = {fmt(gamma, 3)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


def wrap_text(text, width):
    words, lines, line = text.split(), [], ""
    for w in words:
        if line and len(line) + 1 + len(w) > width:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    if line:
        lines.append(line)
    return "\n".join(lines)


# Demonstration 4: trials, and a search over many pairs

SIGMA = 0.4          # constructed per-trial spread of a score
Z = 1.96             # normal approximation, two-sided 95 percent
CONTRAST_BASE = (0.20, 0.30, 0.25)  # neither, p only, i only (Table 2.1)
HEADS = 384
PAIRS_MANY = HEADS * (HEADS - 1) // 2  # 73,536, the chapter's "roughly seventy thousand"


def noise_picture(trials=100, true_contrast=0.15, pairs=1):
    n = int(trials)
    pairs = int(pairs)
    true_contrast = float(true_contrast)
    cells = (*CONTRAST_BASE, CONTRAST_BASE[1] + CONTRAST_BASE[2] - CONTRAST_BASE[0] + true_contrast)
    gamma, _, _, _ = lab_four_cells(*cells)
    if abs(gamma - true_contrast) > 1e-9:
        raise AssertionError("constructed cells should reproduce the chosen contrast")
    se_cell = SIGMA / math.sqrt(n)
    se_gamma = math.sqrt(4 * se_cell ** 2)
    se_diff = math.sqrt(2 * se_cell ** 2)
    half_gamma, half_diff = Z * se_gamma, Z * se_diff
    lo, hi = gamma - half_gamma, gamma + half_gamma
    clears = lo > 0
    chance = pairs * 0.025

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    ses = [se_cell, se_diff, se_gamma]
    names = ["one\ncell", "difference of\ntwo intact scores", "interaction\ncontrast"]
    cols = [PALETTE["grey"], PALETTE["navy"], PALETTE["gold"]]
    left.bar(range(3), ses, color=cols, width=0.6, edgecolor="white")
    for k, v in enumerate(ses):
        left.annotate(fmt(v, 3), (k, v), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                      fontsize=10.5, color=PALETTE["ink"])
    left.set_xticks(range(3), names)
    left.set_ylim(0, 0.098)
    left.set_xlabel("Quantity being measured")
    left.set_ylabel("Standard error (score units)")
    left.set_title(f"{n} trials per cell", fontsize=11.5)

    rows = [(1, "Gamma", gamma, half_gamma, PALETTE["gold"]),
            (0, "same-size difference\nof two intact scores", gamma, half_diff, PALETTE["navy"])]
    for y, _, centre, half, color in rows:
        right.errorbar([centre], [y], xerr=[half], fmt="o", color=color, capsize=6, linewidth=2.2, markersize=8)
        includes = centre - half <= 0
        label_point(right, 0.68, y, "interval includes 0" if includes else "interval excludes 0",
                    color=PALETTE["terracotta"] if includes else PALETTE["teal"], dx=0, dy=11, ha="right")
    right.axvline(0, color=PALETTE["ink"], linewidth=1.2, linestyle="dashed")
    right.set_yticks([1, 0], ["Gamma", "same-size difference\nof two intact scores"])
    right.set_ylim(-0.6, 1.7)
    right.set_xlim(-0.35, 0.7)
    right.set_xlabel("Estimated amount, with interval of 1.96 standard errors")
    right.set_ylabel("Quantity")
    right.set_title(f"A true amount of {fmt(true_contrast, 2)}", fontsize=11.5)
    if pairs > 1:
        label_point(right, 0.68, -0.45, f"{pairs:,} pairs searched; if none were real,\nabout {chance:,.0f} would clear zero on the positive side", color=PALETTE["terracotta"],
                    dx=0, dy=0, ha="right", va="center").set_bbox(BOX)
    else:
        label_point(right, 0.68, -0.45, "one pair, named before measuring", color=PALETTE["teal"], dx=0, dy=0, ha="right", va="center").set_bbox(BOX)

    metrics = {
        "Standard error of one cell": fmt(se_cell, 3),
        "Standard error of Gamma": fmt(se_gamma, 3),
        "Standard error of a difference of two intact scores": fmt(se_diff, 3),
        "Interval for Gamma": f"{fmt(lo, 3)} to {fmt(hi, 3)}",
        "Smallest Gamma that clears zero": fmt(half_gamma, 3),
        "Interval excludes zero": "yes" if clears else "no",
        "Pairs searched": f"{pairs:,}",
        "Chance clears among pairs with no real contrast": f"about {chance:,.2f} of {pairs:,}" if pairs == 1 else f"about {chance:,.0f} of {pairs:,}",
    }
    calc = (
        f"One cell: 0.4 / sqrt({n}) = {fmt(se_cell, 3)}. Gamma adds four independent cells, so its variance is "
        f"4 x {fmt(se_cell, 3)}^2 and its standard error is 2 x {fmt(se_cell, 3)} = {fmt(se_gamma, 3)}, against "
        f"sqrt(2) x {fmt(se_cell, 3)} = {fmt(se_diff, 3)} for a difference of two intact scores. "
        f"Interval: {fmt(gamma, 2)} - 1.96 x {fmt(se_gamma, 3)} = {fmt(lo, 3)} up to {fmt(gamma, 2)} + 1.96 x "
        f"{fmt(se_gamma, 3)} = {fmt(hi, 3)}."
    )
    if clears:
        verdict = (f" The lower end {fmt(lo, 3)} is above zero, so the interval for Gamma excludes zero at this size. "
                   f"Gamma must exceed 1.96 x {fmt(se_gamma, 3)} = {fmt(half_gamma, 3)} to clear zero here.")
    else:
        diff_lo = fmt(gamma - half_diff, 3)
        if gamma - half_diff > 0:
            diff_text = f", even though a same-size difference of intact scores (lower end {diff_lo}) is resolved."
        else:
            diff_text = f", and a same-size difference of intact scores (lower end {diff_lo}) is also unresolved."
        verdict = (f" The lower end {fmt(lo, 3)} is not above zero, so a contrast of {fmt(true_contrast, 2)} is not clear of "
                   f"zero here{diff_text}")
    if pairs == 1:
        search = " One pair named in advance: a pair with no real contrast would have its interval wholly above zero about 1 x 0.025 = 0.025 of the time. A two-sided 95 percent interval excludes zero in either direction about 0.05 of the time."
    else:
        search = (f" Searching {pairs:,} pairs ({HEADS} x {HEADS - 1} / 2 = {pairs:,}, the chapter's roughly seventy thousand): "
                  f"if none had a real contrast, about {pairs:,} x 0.025 = {chance:,.1f} would have an interval wholly above zero by chance, "
                  "so a striking positive pair found by search needs an analysis that accounts for the search before it supports a real interaction.")
    worked = [
        f"One cell: 0.4 / sqrt({n}) = {fmt(se_cell, 3)}.",
        f"Gamma has four independent cells: 2 x {fmt(se_cell, 3)} = {fmt(se_gamma, 3)}.",
        f"Interval half-width = 1.96 x {fmt(se_gamma, 3)} = {fmt(half_gamma, 3)}.",
        f"Interval for Gamma = {fmt(gamma, 2)} +/- {fmt(half_gamma, 3)}, from {fmt(lo, 3)} to {fmt(hi, 3)}.",
        f"Pairs searched: {pairs:,}; positive chance clears with no real contrast = {pairs:,} x 0.025 = {chance:,.2f}.",
    ]
    alt = (f"Left, standard errors for one cell, a difference of two intact scores and the interaction contrast at {n} trials per cell. "
           f"Right, intervals around a true amount of {fmt(true_contrast, 2)}; the Gamma interval runs from {fmt(lo, 3)} to {fmt(hi, 3)}.")
    return fig, metrics, calc + verdict + search, {"alt": alt, "steps": worked}


CHAPTER = {
    "number": 2,
    "title": "How to Measure Emergence",
    "subtitle": "A total score cannot say what two components add together. Four matched measurements can.",
    "summary": (
        "These four demonstrations follow the chapter's instrument: the interaction contrast built from four matched "
        "scores. The first reads the book's cases, the workbench pair and two ways the same four numbers can mislead; the "
        "second shows why the neither cell matters; the third walks the maple-river route and a removal control that leaks; "
        "the fourth asks how many trials the contrast needs and what a search over many pairs does."
    ),
    "ask_skill": {
        "prompt": ("Four matched scores are neither 0.40, p only 0.52, i only 0.49 and both 0.73. Compute the interaction contrast "
                   "and its share of the joint gain, and tell me whether the share is valid. Then recompute with the joint score "
                   "0.58 after a matched rerun."),
    },
    "demos": [
        {
            "id": "C02-D01",
            "title": "Four cells, one contrast",
            "question": "Given the four scores for neither, p only, i only and both, how much did the pair add beyond its two isolated gains, and when may that be read as a share?",
            "equations": [EQ_GAMMA, EQ_SPLIT, EQ_RHO],
            "symbols": (
                "U is a score where higher is better. In U({theta, ...}), theta is the frozen model and the braces list the "
                "enabled components. U({theta}) is the system with neither operation, U({theta, p}) with "
                "only the operation p that prepares a clue, U({theta, i}) with only the operation i that uses the clue, "
                "and U({theta, p, i}) with both. Gamma is the interaction contrast. The ratio rho divides Gamma by the joint "
                "gain (both minus neither); it is a fraction between 0 and 1 only with a positive joint gain, nonnegative "
                "isolated gains and a nonnegative Gamma. A budget is the resource allowance of one cell, in the units of the "
                "reader (10 for each cell unless the joint run is doubled to 20)."
            ),
            "prediction": (
                "Choose the case with both operations at the additive 0.35 (singles 0.30 and 0.25, neither 0.20). Before you read the "
                "numbers, predict whether Gamma is positive, zero or negative."
            ),
            "prediction_options": ["Positive", "Zero", "Negative"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "0.35 - 0.30 - 0.25 + 0.20 = 0: the joint gain 0.15 is exactly the two isolated gains 0.10 + 0.05.",
                "incorrect": "Choose the case 'Additive: 0.20, 0.30, 0.25, 0.35': the joint gain 0.15 equals 0.10 + 0.05, so Gamma is exactly zero.",
            },
            "explanation": (
                "Equation (2.1) takes the score with both operations and subtracts what each operation reaches alone. That "
                "removes the neither score twice, so it is added back once. What is left is the part of the joint score "
                "that the two separate scores cannot explain. The steps on the right build the joint score in that order, "
                "and the bar for Gamma starts where the additive prediction ends. The run control shows two ways the same four "
                "numbers can mislead: a joint run with a bigger budget, and a different score scale."
            ),
            "application": (
                "When a team reports that two components together beat each alone, ask for the neither score, compute Gamma, "
                "check that the budgets match and say which scale the scores are on. Only then can anyone say whether the pair is "
                "better than its parts or merely the sum of them."
            ),
            "assumptions": (
                "Everything except the two switched operations is held fixed: the same model, task distribution, scoring "
                "rule and removal controls. The scores are constructed teaching values and stipulated means, not noisy estimates. "
                "If the four conditions quietly differ in other ways, the arithmetic still balances but the number answers a "
                "different question. Cubing the scores is a change of scale defined for this reader."
            ),
            "check": "In the second example the singles are 0.55 and 0.50 and both operations score 0.70. What is Gamma, and may the ratio be called a fraction?",
            "answer": (
                "0.70 - 0.55 - 0.50 + 0.20 = (-0.15). The joint gain is 0.70 - 0.20 = 0.50, so the ratio is (-0.15) / 0.50 = (-0.30), "
                "a signed diagnostic and not a fraction because Gamma is negative. The pair has the highest score of the four cells yet "
                "scores 0.70 rather than the additive 0.85."
            ),
            "provenance": (
                "Constructed example: the baseline 0.20 and Table 2.1 scores, the second (negative) example and the workbench pair "
                "I.1 and I.3 (0.40, 0.52, 0.49 with the joint score 0.73 under a doubled allowance and 0.58 after a matched rerun) are the "
                "book's own constructed numbers; the additive case is the book's additive prediction 0.35. Computed with the laboratory's four-cell function."
            ),
            "source_section": "Why all four cells",
            "source_anchor": "why-all-four-cells",
            "controls": [
                {"key": "case", "label": "Four-cell scores", "values": ["table", "additive", "second", "workbench"], "default": "table",
                 "value_labels": ["Table 2.1: 0.20, 0.30, 0.25, 0.80", "Additive: 0.20, 0.30, 0.25, 0.35",
                                  "Second example: 0.20, 0.55, 0.50, 0.70", "Workbench I.1 and I.3: 0.40, 0.52, 0.49, 0.58"]},
                {"key": "run", "label": "Run and scale", "values": ["matched", "doubled", "cubed"], "default": "matched",
                 "value_labels": ["Matched budgets", "Joint run had twice the allowance", "Matched, scores cubed first"]},
            ],
            "function": "four_cells_picture",
            "misconception": {
                "title": "The highest score means the pair cooperates",
                "text": ("In the chapter's negative example the pair has the best number in the table, 0.70, which a leaderboard would report, "
                         "yet its improvement is smaller than the additive reference predicts. Only the four-cell comparison shows it."),
            },
            "scope_note": {
                "text": ("A positive value identifies a positive additive interaction on the declared score scale, without identifying its mechanism."),
                "source_section": "What this does not settle",
            },
        },
        {
            "id": "C02-D02",
            "title": "Why the neither cell matters",
            "question": "Two systems both score 0.80 with the pair on. Can their contrasts differ, and what goes wrong if the neither score is skipped?",
            "equations": [EQ_GAMMA, EQ_SPLIT],
            "symbols": (
                "System A has baseline 0.20 and single-operation scores 0.30 and 0.25. System B has the chosen baseline, and "
                "each single-operation score sits 0.02 and 0.01 above it. The baseline is the neither score, U({theta}), where "
                "theta is the frozen model. An intact score is the score with both operations on. The three-cell "
                "remainder means the score with both minus the two single scores, leaving out the neither score."
            ),
            "prediction": (
                "With System B's baseline at 0.70, is its four-cell contrast larger or smaller than A's 0.45? Then switch to "
                "three cells: what sign does B's estimate take?"
            ),
            "prediction_options": ["Larger than 0.45", "Smaller than 0.45", "Equal to 0.45"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "0.80 - 0.72 - 0.71 + 0.70 = 0.07, far below 0.45: B's baseline already supplies most of its intact score. With three cells, 0.80 - 0.72 - 0.71 = (-0.63), negative.",
                "incorrect": "Keep baseline 0.70 and four cells: Gamma is 0.80 - 0.72 - 0.71 + 0.70 = 0.07, smaller than A's 0.45. With three cells, 0.80 - 0.72 - 0.71 = (-0.63), negative.",
            },
            "explanation": (
                "Both single-operation scores already contain the baseline, so a system that starts high has little room "
                "left to credit to the pair. Equation (2.1) adds the baseline back once, which keeps ordinary competence "
                "from counting as cooperation. Without that term the remainder equals Gamma minus the baseline, so it moves "
                "with the baseline rather than with the pair."
            ),
            "application": (
                "When comparing two systems with the same headline score, put the baseline next to the contrast. A large "
                "intact score with a high baseline can hide a small contribution from the pair."
            ),
            "assumptions": (
                "The same score scale and the same controls for both systems. System A and the 0.70 case of System B are "
                "the book's Figure 2.3 values; the other baselines are defined for this reader. A smaller contrast does not "
                "make a system worse: the choice between systems also depends on reliability and cost."
            ),
            "check": "System B has baseline 0.50, so its singles are 0.52 and 0.51 and the pair scores 0.80. What are its four-cell and three-cell numbers?",
            "answer": (
                "Four cells: 0.80 - 0.52 - 0.51 + 0.50 = 0.27. Three cells: 0.80 - 0.52 - 0.51 = (-0.23), which is 0.27 - 0.50. "
                "The three-cell number is negative only because the baseline was removed twice."
            ),
            "provenance": (
                "Constructed example: System A and System B at baseline 0.70 are the book's Figure 2.3 values; the other "
                "baselines are defined for this reader. Computed with the laboratory's four-cell function."
            ),
            "source_section": "Why all four cells",
            "source_anchor": "why-all-four-cells",
            "controls": [
                {"key": "baseline_b", "label": "Baseline of System B (neither score)", "values": [0.30, 0.50, 0.70], "default": 0.70,
                 "value_labels": ["0.30", "0.50", "0.70"]},
                {"key": "method", "label": "Estimate of the pair's contribution", "values": ["four", "three"], "default": "four",
                 "value_labels": ["Four cells, Equation (2.1)", "Three cells (neither score left out)"]},
            ],
            "function": "baseline_picture",
            "misconception": {
                "title": "Equal intact scores mean equal cooperation",
                "text": ("The chapter's Figure 2.3 gives two systems the same intact score 0.80 with contrasts 0.45 and 0.07; "
                         "the baselines, 0.20 and 0.70, differ."),
            },
            "scope_note": {
                "text": ("Neither interaction magnitude is a score to maximize. Choosing between the two systems should depend on "
                         "marginal benefit, reliability, and cost under the intended use."),
                "source_section": "Neither interaction magnitude is a score to maximize",
            },
        },
        {
            "id": "C02-D03",
            "title": "The maple-river route and a leaking removal control",
            "question": "What do the two operations do in the maple-river route, and what happens to the contrast when the control for p still lets p's influence through?",
            "equations": [EQ_GAMMA, EQ_SPLIT],
            "symbols": (
                "P is the earlier operation that tags river as following maple; I is the later operation that looks back for the tag at "
                "the second maple. p and i are the book's names for these two declared operations. The four cells switch each one on or "
                "replace it by its control. The surviving share is the part of p's influence that still reaches the later operation "
                "through the control, for example through a reused attention pattern; the cells with p off then score that share of the way "
                "toward the matching cell with p on. It is a leak model defined for this reader: the chapter says only that the influence survives."
            ),
            "prediction": "If all of p's influence survives the control (share 1), what is the measured Gamma?",
            "prediction_options": ["0.45, as in Table 2.1", "0.225, half of it", "0.00", "Negative"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "With the whole influence leaking, the p-off cells score like the p-on cells: i only 0.80 and neither 0.30, so Gamma = 0.80 - 0.30 - 0.80 + 0.30 = 0.",
                "incorrect": "Set the surviving share to 1.00: the i-only cell reads 0.80 and the neither cell 0.30, so Gamma = 0.80 - 0.30 - 0.80 + 0.30 = 0.",
            },
            "explanation": (
                "In the route of Figure 2.1 neither operation is the task: a tag nobody reads predicts nothing, and a search for a tag never written "
                "finds nothing. Only the cell with both promotes river. A faithful control for p removes the tag, so the i-only cell scores low. A "
                "pattern-preserving ablation reuses the attention pattern that p helped create, so part of p's influence survives inside it and it "
                "cannot serve as a clean condition with p disabled. In the leak model defined here, the p-off cells then score too high, the contrast "
                "shrinks in proportion, and at full leakage it vanishes while Equation (2.2) still balances."
            ),
            "application": (
                "Before running the four cells, write down what replaces each operation and test that the replacement really removes the "
                "information under test. Declare the control and use the same one in all four cells."
            ),
            "assumptions": (
                "Table 2.1's four scores are taken as the clean-control values. The leak model, a straight mix between the clean cell and the matching "
                "p-on cell, is defined for this reader and is not a measurement. The chapter says zero, mean and resampled removal give three "
                "different numbers and none is the true one; this demonstration does not model them."
            ),
            "check": "With half of p's influence surviving, what do the neither and i-only cells read, and what is Gamma?",
            "answer": (
                "Neither: 0.20 + 0.5 x (0.30 - 0.20) = 0.25. I only: 0.25 + 0.5 x (0.80 - 0.25) = 0.525. Gamma = 0.80 - 0.30 - 0.525 + 0.25 = 0.225, "
                "which is 0.45 x (1 - 0.5)."
            ),
            "provenance": (
                "Constructed example: the four scores are the book's Table 2.1 and the route is the chapter's maple river example of Figure 2.1; "
                "the surviving-share model is defined for this reader."
            ),
            "source_section": "What the experiment has to hold still",
            "source_anchor": "what-the-experiment-has-to-hold-still",
            "controls": [
                {"key": "cell", "label": "Cell shown", "values": ["neither", "p", "i", "both"], "default": "neither",
                 "value_labels": ["Neither operation", "p only", "i only", "Both operations"]},
                {"key": "leak", "label": "Share of p's influence that survives the control", "values": [0.0, 0.5, 1.0], "default": 0.0,
                 "value_labels": ["0 (clean control)", "0.50", "1.00 (everything survives)"]},
            ],
            "function": "route_picture",
            "stepper": "cell",
            "misconception": {
                "title": "An easier ablation answers the cooperation question",
                "text": ("The chapter says an easier ablation answers a different question, whether a component's output matters once the rest of the "
                         "computation is fixed, and that the second one silently answering for the first is the most common way a cooperation claim goes wrong."),
            },
            "scope_note": {
                "text": ("The contrast is defined for one pair on one task under one protocol; it is silent about every other route in the model."),
                "source_section": "What this does not settle",
            },
        },
        {
            "id": "C02-D04",
            "title": "Is the contrast clearly different from zero?",
            "question": "How many trials per cell does it take before a contrast of 0.05 or 0.15 is clearly different from zero, and what does searching many pairs do?",
            "equations": [EQ_GAMMA],
            "symbols": (
                "n is the number of trials in each of the four cells. An intact score is the score with both operations on, "
                "and theta in Equation (2.1) is the frozen model. The per-trial spread of a score is set to 0.4 for "
                "every cell. A standard error is the typical size of the error in a measured average: 0.4 divided by "
                "the square root of n for one cell. The illustrated interval is centred on the true amount and extends 1.96 standard errors each way. "
                "For an observed estimate with no real contrast, this interval is wholly above zero about 0.025 of the time, and excludes zero in either "
                "direction about 0.05 of the time. The chapter's model with 384 attention heads has 384 x 383 / 2 = 73,536 pairs."
            ),
            "prediction": "At 400 trials per cell, does a true contrast of 0.05 stand clear of zero? What about 0.15?",
            "prediction_options": ["Both clear zero", "0.15 clears zero, 0.05 does not", "Neither clears zero"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "At 400 trials the standard error of Gamma is 2 x 0.4 / 20 = 0.04, so the half-width is 0.078: 0.15 clears it and 0.05 does not.",
                "incorrect": "Set trials to 400 and compare: Gamma's half-width is 1.96 x 0.04 = 0.078, so 0.15 clears zero and 0.05 does not.",
            },
            "explanation": (
                "Equation (2.1) adds and subtracts four measured cells. If their errors are independent, their variances "
                "add, so the standard error of Gamma is twice that of one cell, against about 1.4 times for the difference "
                "of two intact scores. The same sample can therefore resolve a gap between intact scores while leaving a contrast "
                "of that size unresolved; a true amount of 0.15 at 100 trials shows it. Examining many pairs adds a second problem: some will clear zero by chance alone."
            ),
            "application": (
                "Before running a four-cell comparison, decide the smallest contrast that matters and size the trials so "
                "that its interval would exclude zero. Name the pair before measuring it and report the contrast with an interval, not alone."
            ),
            "assumptions": (
                "Independent cells with equal spread, a normal approximation and a spread of 0.4 defined for this reader. "
                "The interval shown is centred on the true amount; a real run would scatter around it. Cells measured on the "
                "same prompts are correlated, which changes the factor of 2 but not the lesson. The expected count of positive chance clears adds "
                "the null chance 0.025 across pairs; that expectation does not require independent pairs. Dependence between pairs changes the "
                "variability of the count and the probability of at least one chance clear."
            ),
            "check": "With 1600 trials per cell, what is the smallest contrast whose interval excludes zero?",
            "answer": (
                "One cell: 0.4 / sqrt(1600) = 0.010. Gamma: 2 x 0.010 = 0.020. Smallest contrast = 1.96 x 0.020 = 0.039, "
                "so 0.05 clears zero and 0.03 does not."
            ),
            "provenance": (
                "Constructed example: the spread 0.4, the trial counts and the true contrasts are values defined for this "
                "reader; the cells use Table 2.1 for the three lower scores. The factor of 2 and the 384 heads with roughly seventy thousand pairs are the chapter's own."
            ),
            "source_section": "What the experiment has to hold still",
            "source_anchor": "what-the-experiment-has-to-hold-still",
            "controls": [
                {"key": "trials", "label": "Trials per cell", "values": [100, 400, 1600], "default": 100},
                {"key": "true_contrast", "label": "True interaction contrast", "values": [0.05, 0.15], "default": 0.15,
                 "value_labels": ["0.05", "0.15"]},
                {"key": "pairs", "label": "Pairs examined", "values": [1, PAIRS_MANY], "default": 1,
                 "value_labels": ["One pair, named in advance", "73,536 pairs (384 heads), searched"]},
            ],
            "function": "noise_picture",
            "misconception": {
                "title": "A striking pair found by search is a finding about the model",
                "text": ("The chapter warns that examining thousands of candidates can produce a striking contrast by chance. A positive pair found "
                         "by search needs an analysis that accounts for that search before it supports a claim about a real interaction."),
            },
            "scope_note": {
                "text": ("A contrast is a single measurement of a single pair on a single task. Systems have many pairs."),
                "source_section": "What one measurement cannot do",
            },
        },
    ],
}

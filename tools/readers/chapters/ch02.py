"""Chapter 2 reader: How to Measure Emergence.

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


def lab_four_cells(neither, p_only, i_only, both):
    """Interaction contrast, joint gain and signed ratio from the laboratory's own function."""
    out = evaluate({"scores": [neither, p_only, i_only, both], "budgets": [10, 10, 10, 10]})["metrics"]
    return out["interaction"], out["joint_gain"], out["signed_share"], out["fraction_share"]


def sign_word(gamma):
    if abs(gamma) <= TOL:
        return "zero"
    return "positive" if gamma > 0 else "negative"


def draw_grid(ax, neither, p_only, i_only, both):
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
        ax.text(x, y - 0.13, fmt(score, 2), ha="center", va="center", fontsize=14, color=PALETTE["ink"], fontweight="bold")
    ax.set_xlim(-0.5, 1.5)
    ax.set_ylim(-0.5, 1.5)
    ax.set_xticks([0, 1], ["off", "on"])
    ax.set_yticks([0, 1], ["off", "on"])
    ax.set_aspect("equal")
    ax.grid(False)
    ax.set_xlabel("Operation i (uses the clue)")
    ax.set_ylabel("Operation p (prepares the clue)")


# Demonstration 1

SINGLES = {"table": (0.30, 0.25), "second": (0.55, 0.50)}
NEITHER = 0.20


def four_cells_picture(both=0.80, singles="table"):
    p_only, i_only = SINGLES[singles]
    both = float(both)
    gamma, joint, _, _ = lab_four_cells(NEITHER, p_only, i_only, both)
    gain_p, gain_i = p_only - NEITHER, i_only - NEITHER
    additive = NEITHER + gain_p + gain_i
    if abs(gamma - (both - additive)) > 1e-9:
        raise AssertionError("laboratory contrast disagrees with the written sum")

    fig, (grid, water) = new_figure(ncols=2, height=4.3)
    draw_grid(grid, NEITHER, p_only, i_only, both)
    grid.set_title("The four measured scores", fontsize=11.5)

    steps = [
        ("neither", 0.0, NEITHER, PALETTE["grey"], None),
        ("gain\nfrom p", NEITHER, p_only, PALETTE["navy"], None),
        ("gain\nfrom i", p_only, p_only + gain_i, PALETTE["navy"], None),
        ("Gamma", additive, both, PALETTE["gold"], "///" if gamma < -TOL else None),
        ("both", 0.0, both, PALETTE["teal"], None),
    ]
    for k, (name, start, end, color, hatch) in enumerate(steps):
        water.bar(k, end - start, bottom=start, color=color, width=0.62, hatch=hatch,
                  edgecolor="white" if hatch is None else PALETTE["ink"], linewidth=1.0)
        top = max(start, end)
        if name == "Gamma":
            text = fmt(gamma, 2) if gamma < -TOL else ("+" + fmt(gamma, 2) if gamma > TOL else "0.00")
        elif name.startswith("gain"):
            text = "+" + fmt(end - start, 2)
        else:
            text = fmt(end, 2)
        water.annotate(text, (k, top), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom",
                       fontsize=10.5, color=PALETTE["ink"])
    water.plot([2.31, 2.69], [additive, additive], color=PALETTE["ink"], linestyle="dashed", linewidth=1.2)
    water.set_xticks(range(5), ["neither", "gain\nfrom p", "gain\nfrom i", "$\\Gamma$", "both"])
    water.set_xlim(-0.6, 4.6)
    water.set_ylim(0, 1.0)
    water.set_xlabel("Build the joint score step by step")
    water.set_ylabel("Score U (higher is better)")
    water.set_title("Gamma is what the two gains leave over", fontsize=11.5)

    reading = sign_word(gamma)
    metrics = {
        "Joint gain (both minus neither)": fmt(joint, 2),
        "Additive prediction": fmt(additive, 2),
        "Interaction contrast Gamma": fmt(gamma, 2),
        "Sign of Gamma": reading,
    }
    calc = (
        f"Gamma = {fmt(both, 2)} - {fmt(p_only, 2)} - {fmt(i_only, 2)} + {fmt(NEITHER, 2)} = {fmt(gamma, 2)}. "
        f"The additive prediction is {fmt(p_only, 2)} + {fmt(i_only, 2)} - {fmt(NEITHER, 2)} = {fmt(additive, 2)}, "
        f"and the pair scored {fmt(both, 2)}."
    )
    if reading == "positive":
        meaning = (f"Gamma is positive: the pair delivers {fmt(gamma, 2)} more than the two isolated gains "
                   f"({fmt(gain_p, 2)} + {fmt(gain_i, 2)} = {fmt(gain_p + gain_i, 2)}) predict. "
                   "That is the chapter's local sense of measured emergence, on this task and score only.")
    elif reading == "zero":
        meaning = ("Gamma is zero: the joint gain is exactly the sum of the two isolated gains. The pair may still score "
                   "well and both operations may help, but there is no extra pairwise contribution to assign.")
    else:
        meaning = (f"Gamma is negative: the joint gain {fmt(joint, 2)} is smaller than the isolated gains add up to "
                   f"({fmt(gain_p + gain_i, 2)}). Overlapping benefits, saturation or interference could each cause "
                   "that, and the four numbers alone do not say which.")
    return fig, metrics, calc + " " + meaning


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
    return fig, metrics, text


# Demonstration 3

SCENARIOS = {
    "table": ("Table 2.1", (0.20, 0.30, 0.25, 0.80)),
    "small": ("small gain", (0.50, 0.50, 0.50, 0.52)),
    "negative": ("negative", (0.20, 0.55, 0.50, 0.70)),
    "zero": ("zero gain", (0.50, 0.60, 0.50, 0.50)),
}


def share_state(cells):
    """Contrast, joint gain, ratio (None when undefined) and the fraction conditions, from the laboratory function."""
    gamma, joint, signed_share, fraction = lab_four_cells(*cells)
    gain_p, gain_i = cells[1] - cells[0], cells[2] - cells[0]
    reasons = []
    if joint <= TOL:
        reasons.append("the joint gain is not positive")
    if gain_p < -TOL or gain_i < -TOL:
        reasons.append("an isolated gain is negative")
    if gamma < -TOL:
        reasons.append("the interaction contrast is negative")
    return gamma, joint, signed_share, fraction, gain_p, gain_i, reasons


def share_picture(experiment="table"):
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    name, cells = SCENARIOS[experiment]
    gamma, joint, ratio, fraction, gain_p, gain_i, reasons = share_state(cells)
    if (fraction is None) != bool(reasons):
        raise AssertionError("laboratory fraction domain disagrees with the chapter's three conditions")

    bars = [("gain\nfrom p", gain_p, PALETTE["navy"]), ("gain\nfrom i", gain_i, PALETTE["navy"]),
            ("$\\Gamma$", gamma, PALETTE["gold"]), ("joint\ngain", joint, PALETTE["teal"])]
    for k, (label, v, color) in enumerate(bars):
        negative = v < -TOL
        left.bar(k, v, color=color, width=0.6, hatch="///" if negative else None,
                 edgecolor=PALETTE["ink"] if negative else "white", linewidth=1.0)
        text = fmt(v, 2) if v < -TOL else ("+" + fmt(v, 2) if v > TOL else "0.00")
        left.annotate(text, (k, v), xytext=(0, -5 if negative else 4), textcoords="offset points", ha="center",
                      va="top" if negative else "bottom", fontsize=10.5, color=PALETTE["ink"])
    left.axhline(0, color=PALETTE["ink"], linewidth=1.0)
    left.set_xticks(range(4), [b[0] for b in bars])
    left.set_xlim(-0.6, 3.6)
    values = [b[1] for b in bars]
    left.set_ylim(min(0.0, min(values)) * 1.6 - 0.01, max(values) * 1.25 + 0.01)
    left.set_xlabel("Pieces of Equation (2.2)")
    left.set_ylabel("Score units")
    left.set_title(f"{name[0].upper()}{name[1:]}: amount and total", fontsize=11.5)

    right.axhspan(0, 1, color="#d6e6e4", alpha=0.9)
    right.text(-0.42, 0.2, "valid fraction\nrange 0 to 1", ha="left", va="center", fontsize=10.5, color=PALETTE["teal"])
    keys = list(SCENARIOS)
    short = [SCENARIOS[k][0].replace(" ", "\n", 1) if len(SCENARIOS[k][0]) > 9 else SCENARIOS[k][0] for k in keys]
    for k, key in enumerate(keys):
        _, c = SCENARIOS[key]
        _, jn, r, _, _, _, _ = share_state(c)
        if r is None:
            continue
        chosen = key == experiment
        right.plot([k], [r], "o", markersize=11 if chosen else 7, color=PALETTE["teal"] if chosen else "none",
                   markeredgecolor=PALETTE["ink"], markeredgewidth=1.4)
        if chosen:
            label_point(right, k, r, f"{fmt(r, 2)}", color=PALETTE["ink"], dx=0, dy=-18 if r > 0.9 else 12, ha="center",
                        va="top" if r > 0.9 else "bottom")
    if ratio is None:
        zk = keys.index(experiment)
        label_point(right, zk, -0.3, "undefined:\nno joint gain", color=PALETTE["terracotta"], dx=0, dy=0, ha="center", va="center")
    right.axhline(0, color=PALETTE["ink"], linewidth=0.8)
    right.set_xticks(range(4), short)
    right.set_xlim(-0.5, 3.5)
    right.set_ylim(-0.6, 1.3)
    right.set_xlabel("Constructed experiment (chosen one filled)")
    right.set_ylabel("Ratio Gamma / joint gain")
    right.set_title("Where each ratio falls", fontsize=11.5)

    metrics = {
        "Interaction contrast (amount)": fmt(gamma, 2),
        "Joint gain": fmt(joint, 2),
        "Ratio Gamma / joint gain": fmt(ratio, 2) if ratio is not None else "undefined (the joint gain is zero)",
        "Valid as a fraction": "yes" if not reasons else "no (" + "; ".join(reasons) + ")",
    }
    u00, u10, u01, u11 = cells
    gamma_calc = f"Gamma = {fmt(u11, 2)} - {fmt(u10, 2)} - {fmt(u01, 2)} + {fmt(u00, 2)} = {fmt(gamma, 2)}"
    gain_calc = f"joint gain = {fmt(u11, 2)} - {fmt(u00, 2)} = {fmt(joint, 2)}"
    if ratio is None:
        tail = (f"The ratio would be {fmt(gamma, 2)} / {fmt(joint, 2)}, a division by zero, so it is undefined and not "
                "replaced by 0. Report the signed amount and say the ratio does not exist here.")
    elif not reasons:
        tail = (f"Ratio = {fmt(gamma, 2)} / {fmt(joint, 2)} = {fmt(ratio, 2)}. The three conditions hold (positive joint gain, "
                "nonnegative isolated gains, nonnegative contrast), so it is a fraction between 0 and 1.")
        if joint < 0.05:
            tail += (f" The amount is only {fmt(gamma, 2)} score units, so a share of {fmt(ratio, 2)} says little on its own; "
                     "report the amount beside it.")
    else:
        tail = (f"Ratio = {fmt(gamma, 2)} / {fmt(joint, 2)} = {fmt(ratio, 2)}. It is a fine signed diagnostic, but "
                f"not a fraction of cooperation because {' and '.join(reasons)}.")
    return fig, metrics, f"{gamma_calc}; {gain_calc}. {tail}"


# Demonstration 4

SIGMA = 0.4          # constructed per-trial spread of a score
Z = 1.96             # normal approximation, two-sided 95 percent
CONTRAST_BASE = (0.20, 0.30, 0.25)  # neither, p only, i only (Table 2.1)


def noise_picture(trials=100, true_contrast=0.15):
    n = int(trials)
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

    smallest = half_gamma
    metrics = {
        "Standard error of one cell": fmt(se_cell, 3),
        "Standard error of Gamma": fmt(se_gamma, 3),
        "Standard error of a difference of two intact scores": fmt(se_diff, 3),
        "Interval for Gamma": f"{fmt(lo, 3)} to {fmt(hi, 3)}",
        "Smallest Gamma that clears zero": fmt(smallest, 3),
        "Interval excludes zero": "yes" if clears else "no",
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
                   f"Gamma must exceed 1.96 x {fmt(se_gamma, 3)} = {fmt(smallest, 3)} to clear zero here.")
    else:
        diff_lo = fmt(gamma - half_diff, 3)
        if gamma - half_diff > 0:
            diff_text = f", even though a same-size difference of intact scores (lower end {diff_lo}) is resolved."
        else:
            diff_text = f", and a same-size difference of intact scores (lower end {diff_lo}) is also unresolved."
        verdict = (f" The lower end {fmt(lo, 3)} is not above zero, so a contrast of {fmt(true_contrast, 2)} is not clear of "
                   f"zero here{diff_text}")
    return fig, metrics, calc + verdict


CHAPTER = {
    "number": 2,
    "title": "How to Measure Emergence",
    "subtitle": "A total score cannot say what two components add together. Four matched measurements can.",
    "summary": (
        "These four demonstrations follow the chapter's instrument: the interaction contrast built from four matched "
        "scores. Each one changes a declared score or a declared protocol value and shows which quantity moves, "
        "which stays fixed, and when the number stops meaning what it appears to mean."
    ),
    "demos": [
        {
            "id": "C02-D01",
            "title": "Four cells, one contrast",
            "question": "Given the four scores for neither, p only, i only and both, how much did the pair add beyond its two isolated gains?",
            "equations": [EQ_GAMMA],
            "symbols": (
                "U is a score where higher is better. In U({theta, ...}), theta is the frozen model and the braces list the "
                "enabled components. U({theta}) is the system with neither operation, U({theta, p}) with "
                "only the operation p that prepares a clue, U({theta, i}) with only the operation i that uses the clue, "
                "and U({theta, p, i}) with both. Gamma is the interaction contrast. All values are on one declared score "
                "scale from 0 to 1."
            ),
            "prediction": (
                "Keep the isolated scores of Table 2.1 and set the score with both operations to 0.35. Before you read the "
                "numbers, predict whether Gamma is positive, zero or negative."
            ),
            "explanation": (
                "Equation (2.1) takes the score with both operations and subtracts what each operation reaches alone. That "
                "removes the neither score twice, so it is added back once. What is left is the part of the joint score "
                "that the two separate scores cannot explain. The steps on the right build the joint score in that order, "
                "and the bar for Gamma starts where the additive prediction ends."
            ),
            "application": (
                "When a team reports that two components together beat each alone, ask for the neither score and then "
                "compute Gamma. Only then can anyone say whether the pair is better than its parts or merely the sum of them."
            ),
            "assumptions": (
                "Everything except the two switched operations is held fixed: the same model, task distribution, scoring "
                "rule and removal controls. The scores here are constructed teaching values. If the four conditions quietly "
                "differ in other ways, the arithmetic still balances but the number answers a different question."
            ),
            "check": "In the second example the singles are 0.55 and 0.50 and both operations score 0.70. What is Gamma?",
            "answer": (
                "0.70 - 0.55 - 0.50 + 0.20 = (-0.15). The pair has the highest score of the four cells, yet its gain is "
                "0.50 against 0.65 predicted by adding the isolated gains (0.35 + 0.30), so it scores 0.70 rather than the "
                "additive 0.85."
            ),
            "provenance": (
                "Constructed example: the baseline 0.20 and Table 2.1 scores are the book's worked numbers; the second "
                "example at 0.70 is the book's negative example; the other both-operations scores are values defined "
                "for this reader. Computed with the laboratory's four-cell function."
            ),
            "source_section": "Writing the four cells",
            "source_anchor": "writing-the-four-cells",
            "controls": [
                {"key": "both", "label": "Score with both operations on", "values": [0.35, 0.60, 0.70, 0.80], "default": 0.80,
                 "value_labels": ["0.35", "0.60", "0.70", "0.80"]},
                {"key": "singles", "label": "Scores with one operation on", "values": ["table", "second"], "default": "table",
                 "value_labels": ["p only 0.30, i only 0.25 (Table 2.1)", "p only 0.55, i only 0.50 (second example)"]},
            ],
            "function": "four_cells_picture",
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
        },
        {
            "id": "C02-D03",
            "title": "Amount and share",
            "question": "When may the ratio of the contrast to the joint gain be read as a share, and what is reported when it may not?",
            "equations": [EQ_RHO, EQ_SPLIT],
            "symbols": (
                "Gamma is the interaction contrast from Equation (2.1); theta in the equations is the frozen model. The joint gain is the score with both operations "
                "minus the neither score. The isolated gains are each single-operation score minus the neither score. "
                "The ratio rho divides Gamma by the joint gain. A fraction of cooperation needs a positive joint gain, "
                "nonnegative isolated gains and a nonnegative Gamma."
            ),
            "prediction": "Choose the negative experiment. The ratio is a number; will the chapter let you call it a fraction?",
            "explanation": (
                "By Equation (2.2) the joint gain is the two isolated gains plus Gamma. If all three pieces are nonnegative "
                "and the total is positive, Gamma cannot exceed the total, so the ratio lies between 0 and 1. Outside those "
                "conditions the ratio is still arithmetic, but it is a signed diagnostic, and with a joint gain of zero it "
                "does not exist."
            ),
            "application": (
                "Report the amount and the ratio together. A small amount that makes up all of a small gain and a large "
                "amount that makes up a modest slice of a large gain are different findings."
            ),
            "assumptions": (
                "The ratio is an additive decomposition on one declared score scale, not a causal attribution of a mechanism. "
                "The four experiments here are constructed: Table 2.1 and the negative example are the book's; the small gain "
                "and the zero gain experiments are defined for this reader. A different score scale can change Gamma and "
                "its ratio."
            ),
            "check": "Scores are neither 0.40, p only 0.50, i only 0.60 and both 0.90. What are Gamma, the joint gain and the ratio, and is the ratio a valid share?",
            "answer": (
                "Gamma = 0.90 - 0.50 - 0.60 + 0.40 = 0.20. Joint gain = 0.90 - 0.40 = 0.50. Ratio = 0.20 / 0.50 = 0.40, and "
                "the three conditions hold, so it is a valid share."
            ),
            "provenance": (
                "Constructed example: Table 2.1 and the negative example are the book's worked numbers; the small gain and "
                "zero gain experiments are values defined for this reader. Computed with the laboratory's four-cell function."
            ),
            "source_section": "Amount and share",
            "source_anchor": "amount-and-share",
            "controls": [
                {"key": "experiment", "label": "Constructed experiment", "values": ["table", "small", "negative", "zero"],
                 "default": "table",
                 "value_labels": ["Table 2.1 (ratio 0.75)", "Small gain (amount 0.02)", "Negative example (ratio -0.30)",
                                  "Zero joint gain (ratio undefined)"]},
            ],
            "function": "share_picture",
        },
        {
            "id": "C02-D04",
            "title": "Is the contrast clearly different from zero?",
            "question": "How many trials per cell does it take before a contrast of 0.05 or 0.15 is clearly different from zero?",
            "equations": [EQ_GAMMA],
            "symbols": (
                "n is the number of trials in each of the four cells. An intact score is the score with both operations on, "
                "and theta in Equation (2.1) is the frozen model. The per-trial spread of a score is set to 0.4 for "
                "every cell. A standard error is the typical size of the error in a measured average: 0.4 divided by "
                "the square root of n for one cell. The interval is the true amount plus or minus 1.96 standard errors."
            ),
            "prediction": "At 400 trials per cell, does a true contrast of 0.05 stand clear of zero? What about 0.15?",
            "explanation": (
                "Equation (2.1) adds and subtracts four measured cells. If their errors are independent, their variances "
                "add, so the standard error of Gamma is twice that of one cell, against about 1.4 times for the difference "
                "of two intact scores. The same sample can therefore resolve a gap between intact scores while leaving a contrast "
                "of that size unresolved: compare the two intervals at 100 trials and a true amount of 0.15."
            ),
            "application": (
                "Before running a four-cell comparison, decide the smallest contrast that matters and size the trials so "
                "that its interval would exclude zero. Report the contrast with an interval, not alone."
            ),
            "assumptions": (
                "Independent cells with equal spread, a normal approximation and a spread of 0.4 defined for this reader. "
                "The interval shown is centred on the true amount; a real run would scatter around it. Cells measured on the "
                "same prompts are correlated, which changes the factor of 2 but not the lesson."
            ),
            "check": "With 1600 trials per cell, what is the smallest contrast whose interval excludes zero?",
            "answer": (
                "One cell: 0.4 / sqrt(1600) = 0.010. Gamma: 2 x 0.010 = 0.020. Smallest contrast = 1.96 x 0.020 = 0.039, "
                "so 0.05 clears zero and 0.03 does not."
            ),
            "provenance": (
                "Constructed example: the spread 0.4, the trial counts and the true contrasts are values defined for this "
                "reader; the cells use Table 2.1 for the three lower scores. The factor of 2 is the chapter's remark about "
                "four equal-variance cells."
            ),
            "source_section": "What the experiment has to hold still",
            "source_anchor": "what-the-experiment-has-to-hold-still",
            "controls": [
                {"key": "trials", "label": "Trials per cell", "values": [100, 400, 1600, 6400], "default": 100},
                {"key": "true_contrast", "label": "True interaction contrast", "values": [0.05, 0.15], "default": 0.15,
                 "value_labels": ["0.05", "0.15"]},
            ],
            "function": "noise_picture",
        },
    ],
}

"""Chapter 26 reader: How Much More Could the System Become?

Four demonstrations built on Equations (26.1) to (26.3) and the chapter's
constructed fixed-generator saturation curve.

Demonstration 1 evaluates Equation (26.1) on finite pools of ten programs per
task, starting from the chapter's worked pool (2 passing, subsets of 3) and
adding two constructed four-task banks that differ only in how concentrated the
passes are (the chapter's temperature point). It shows the exact pool value
beside the independent-draw plug-in. Demonstration 2 calls the laboratory's own
bank-ceiling function (math_ai_agents.chapters.ch26.evaluate) on the notebook's
default, changed and transfer cases and places each lost task on the ladder
from generation to selection to deployment (Equation 26.2). Demonstration 3
locates a coverage and selection pair against the Sel = Cov line (Equation
26.3), using the chapter's reported percentages as given and two constructed
pairs. Demonstration 4 fits the chapter's three constructed coverage points
with three curve families and compares the room a larger bank could add with
the room left below the ceiling. Nothing here is a measurement.
"""
import math

import numpy as np
from matplotlib.patches import Rectangle

from math_ai_agents.chapters.ch26 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

EQ_COVERAGE = (
    r"\widehat{\operatorname{Cov}}_{\mathcal K}(k)= \frac{1}{|\mathcal K|}\sum_{i\in\mathcal K}"
    r"\left(1 - \frac{\binom{n_i-c_i}{k}}{\binom{n_i}{k}}\right),\qquad 1\le k\le \min_{i\in\mathcal K}n_i"
)
EQ_CEILING = r"\operatorname{Sel}(k) \le \operatorname{Cov}(k)"
EQ_GAP = r"\operatorname{Cov}(k)-\operatorname{Sel}(k) \ge 0"
EQ_EXP = r"A - B e^{-k/\tau}"
EQ_HYP = r"A - B/(k+h)"
EQ_POW = r"A - B k^{-a}"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
GREY = "#e6eaee"


# Demonstration 1: a bank is a finite object; the pool depends on the sampling rule

N_POOL = 10  # n, the chapter's worked pool size, used for every task here
POOLS = {
    "chapter": {"name": "the chapter's worked pool", "counts": [2]},
    "low": {"name": "a low-temperature bank", "counts": [8, 8, 0, 0]},
    "high": {"name": "a high-temperature bank", "counts": [3, 3, 2, 2]},
}


def task_cov(c, k, n=N_POOL):
    return 1 - math.comb(n - c, k) / math.comb(n, k)


def task_plug(c, k, n=N_POOL):
    return 1 - (1 - c / n) ** k


def groups_of(counts):
    out = []
    for c in counts:
        for g in out:
            if g[0] == c:
                g[1] += 1
                break
        else:
            out.append([c, 1])
    return out


def mean_text(parts, total, digits):
    """Written weighted mean: (a x v1 + b x v2) / total = value."""
    value = sum(a * v for a, v in parts) / total
    body = " + ".join(f"{a} x {fmt(v, digits)}" for a, v in parts)
    return f"({body}) / {total} = {fmt(value, digits)}", value


def bank_picture(pool="chapter", subset=3):
    counts, k, n = POOLS[pool]["counts"], int(subset), N_POOL
    t = len(counts)
    covs = [task_cov(c, k) for c in counts]
    plugs = [task_plug(c, k) for c in counts]
    cov, plug = sum(covs) / t, sum(plugs) / t
    sel = sum(c / n for c in counts) / t     # a selector with no correctness signal succeeds at the pass share
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    for i, (c, v, p) in enumerate(zip(counts, covs, plugs)):
        left.bar(i, v, color=PALETTE["teal"], edgecolor="white", width=0.6)
        left.plot([i], [p], "D", color=PALETTE["gold"], markersize=9, markeredgecolor="white", zorder=5)
        left.text(i, max(v, p) + 0.04, fmt(v, 3), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.set_xticks(range(t), [f"Task {i + 1}\nc = {c}" for i, c in enumerate(counts)])
    left.set_xlim(-0.6, t - 0.4)
    left.set_ylim(0, 1.2)
    left.set_xlabel(f"Task and its passing programs c (of n = {n})")
    left.set_ylabel(f"Coverage at k = {k}")
    left.set_title(f"Bars: exact pool; diamonds: independent-draw", fontsize=11.5)
    names = ["Exact pool\ncoverage", "Independent-\ndraw formula", "Selector with\nno signal"]
    values = [cov, plug, sel]
    cols = [PALETTE["teal"], PALETTE["gold"], PALETTE["navy"]]
    hats = ["", "///", "..."]
    for i, (v, col, hat) in enumerate(zip(values, cols, hats)):
        right.bar(i, v, color=col, hatch=hat, edgecolor="white", width=0.62)
        right.text(i, v + 0.03, fmt(v, 3), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    right.set_xticks(range(3), names)
    right.set_xlim(-0.6, 2.6)
    right.set_ylim(0, 1.15)
    right.set_xlabel("Average over the bank's tasks")
    right.set_ylabel("Probability of success")
    right.set_title(f"Three different numbers at k = {k}", fontsize=11.5)

    gs = groups_of(counts)
    cov_lines = "; ".join(
        f"c = {c}: 1 - C({n - c},{k}) / C({n},{k}) = 1 - {math.comb(n - c, k)} / {math.comb(n, k)} = {fmt(task_cov(c, k), 4)}"
        for c, _ in gs)
    cov_mean, _ = mean_text([(m_, task_cov(c, k)) for c, m_ in gs], t, 4)
    sel_mean, _ = mean_text([(m_, c / n) for c, m_ in gs], t, 2)
    plug_mean, _ = mean_text([(m_, task_plug(c, k)) for c, m_ in gs], t, 4)
    metrics = {
        "Tasks in the bank": str(t),
        "Passing programs per task (of 10)": ", ".join(str(c) for c in counts),
        f"Exact coverage at k = {k}": fmt(cov, 4),
        "Independent-draw formula": fmt(plug, 4),
        "No-signal selector success": fmt(sel, 3),
        "Coverage not collected by that selector": fmt(cov - sel, 4),
    }
    if t == 1:
        total, failing = math.comb(n, k), math.comb(n - counts[0], k)
        interpretation = (
            f"Coverage = 1 - C({n - counts[0]},{k}) / C({n},{k}) = 1 - {failing} / {total} = {fmt(cov, 4)}, so "
            f"{total - failing} of the {total} subsets hold at least one pass. A selector that picks one program of the subset "
            f"with no correctness signal succeeds with probability {counts[0]} / {n} = {fmt(sel, 2)}, which leaves "
            f"{fmt(cov, 4)} - {fmt(sel, 2)} = {fmt(cov - sel, 4)} uncollected. Putting the single-program rate "
            f"{fmt(counts[0] / n, 2)} into an independent-draw formula gives 1 - (1 - {fmt(counts[0] / n, 2)})^{k} = {fmt(plug, 4)}, "
            "a different quantity that does not equal the exact fixed-pool value" + (" except at k = 1." if k == 1 else ".")
        )
        comp = ", ".join(f"{j} passes: {math.comb(counts[0], j) * math.comb(n - counts[0], k - j)}"
                         for j in range(min(counts[0], k) + 1))
        steps = [f"One task, n = {n} programs, c = {counts[0]} pass, subsets of size k = {k}: C({n},{k}) = {total} subsets.",
                 f"Subsets by number of passes: {comp}.",
                 f"Subsets with no pass: C({n - counts[0]},{k}) = {failing}.",
                 f"Coverage = 1 - {failing} / {total} = {fmt(cov, 4)}.",
                 f"No-signal selector: c / n = {counts[0]} / {n} = {fmt(sel, 2)}; uncollected {fmt(cov, 4)} - {fmt(sel, 2)} = {fmt(cov - sel, 4)}.",
                 f"Independent-draw formula: 1 - (1 - {fmt(counts[0] / n, 2)})^{k} = {fmt(plug, 4)}."]
    else:
        trend = ""
        if k == 1:
            trend = " At k = 1 the exact value, the independent-draw value and the no-signal selector all equal the average pass share."
        plug_note = ("which differs from the exact mean" if plug_mean != cov_mean
                     else "which matches the exact mean to four decimals here, so the two print the same although they are different quantities")
        interpretation = (
            f"Equation (26.1) averages the per-task coverage. Per task, {cov_lines}. Mean = {cov_mean}. A selector with no signal "
            f"succeeds at the average pass share, {sel_mean}, leaving {fmt(cov, 4)} - {fmt(sel, 3)} = {fmt(cov - sel, 4)}. The "
            f"independent-draw formula averages 1 - (1 - c / {n})^{k} to {plug_mean}, {plug_note}.{trend}"
        )
        steps = [f"Bank of {t} tasks, n = {n} programs each; passing counts c = {', '.join(str(c) for c in counts)}.",
                 f"Per-task coverage at k = {k}: " + "; ".join(f"c = {c}: {fmt(task_cov(c, k), 4)}" for c, _ in gs) + ".",
                 f"Mean coverage = {cov_mean}.",
                 f"No-signal selector = average pass share = {sel_mean}.",
                 f"Independent-draw formula, per task then averaged: {plug_mean}.",
                 f"Exact minus independent-draw = {fmt(cov, 4)} - {fmt(plug, 4)} = {signed(cov - plug, 4)}."]
    alt = (f"Left, coverage at k = {k} for each of {t} task{'s' if t > 1 else ''} as bars with independent-draw diamonds. Right, three bars "
           f"for the bank average: exact {fmt(cov, 3)}, independent-draw {fmt(plug, 3)} and a no-signal selector {fmt(sel, 3)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: coverage is a ceiling, and the ladder shows where success is lost

T, F = True, False
BANKS = {
    "diag": {"matrix": [[T, F, F], [F, T, F], [F, F, T]], "weights": [0.2, 0.3, 0.5], "default_sel": [0, 0, 0],
             "oracle_sel": [0, 1, 2], "denied": [T, T, F], "indep": 0.4, "name": "three specialists"},
    "prefix": {"matrix": [[T, F, F], [F, T, F]], "weights": [0.2, 0.3, 0.5], "default_sel": [0, 0, 0],
               "oracle_sel": [0, 1, 0], "denied": [T, T, F], "indep": 0.4, "name": "first two specialists"},
    "xfer": {"matrix": [[T, T], [T, F]], "weights": [0.5, 0.5], "default_sel": [1, 1],
             "oracle_sel": [0, 0], "denied": [T, F], "indep": 0.6, "name": "two candidates, two tasks"},
}
STATUS = {"delivered": "delivered", "missed": "missed by selector", "absent": "absent from bank", "denied": "denied at deployment"}
SHORT = {"delivered": "delivered", "missed": "missed", "absent": "absent", "denied": "denied"}


def lab_ceiling(bank, selector, deploy):
    b = BANKS[bank]
    chosen = b["default_sel"] if selector == "notebook" else b["oracle_sel"]
    allowed = [T] * len(b["weights"]) if deploy == "all" else b["denied"]
    out = evaluate({"success_matrix": b["matrix"], "task_weights": b["weights"], "selected_candidates": chosen,
                    "deployment_allowed": allowed, "independent_candidate_success": b["indep"]})
    return b, chosen, allowed, out


def written_sum(weights, flags):
    return " + ".join(f"{fmt(w, 1)} x {int(f)}" for w, f in zip(weights, flags))


def ladder_picture(bank="diag", selector="notebook", deploy="all"):
    b, chosen, allowed, out = lab_ceiling(bank, selector, deploy)
    matrix, weights = b["matrix"], b["weights"]
    m, nt = len(matrix), len(weights)
    lab = out["metrics"]
    cov, sel, dep = lab["bank_oracle_coverage"], lab["actual_selection_success"], lab["deployment_success"]
    if sel > cov + 1e-12 or dep > sel + 1e-12:
        raise AssertionError("ladder order broken")
    covered = lab["oracle_task_flags"]
    won = lab["selection_task_flags"]
    shipped = lab["deployment_task_flags"]
    where = []
    for t in range(nt):
        if not covered[t]:
            where.append("absent")
        elif not won[t]:
            where.append("missed")
        elif not shipped[t]:
            where.append("denied")
        else:
            where.append("delivered")
    prefix = out["series"][0]["y"]

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    for i in range(m):
        for t in range(nt):
            ok = matrix[i][t]
            is_chosen = chosen[t] == i
            left.add_patch(Rectangle((t, m - 1 - i), 1, 1, facecolor="#cfe5e3" if ok else "white",
                                     edgecolor=PALETTE["ink"] if is_chosen else PALETTE["light"],
                                     linewidth=3 if is_chosen else 1, hatch=None if ok else "///"))
            left.text(t + 0.5, m - 1 - i + 0.5, ("pass" if ok else "fail") + (", chosen" if is_chosen else ""), ha="center",
                      va="center", fontsize=10.5, color=PALETTE["ink"]).set_bbox(
                {"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.85})
    left.set_xlim(0, nt)
    left.set_ylim(0, m)
    left.set_xticks([t + 0.5 for t in range(nt)],
                    [f"Task {t + 1}, weight {fmt(weights[t], 1)}\n{SHORT[where[t]]}" for t in range(nt)])
    left.set_yticks([m - 1 - i + 0.5 for i in range(m)], [f"Candidate {i + 1}" for i in range(m)])
    left.set_xlabel("Task, its share of the task distribution, and where it stands")
    left.set_ylabel("Candidate in the bank")
    left.set_title("Bank and the selector's choice", fontsize=11.5)
    left.grid(False)

    vals = [cov, sel, dep]
    cols = [PALETTE["teal"], PALETTE["navy"], PALETTE["gold"]]
    for i, (v, col) in enumerate(zip(vals, cols)):
        right.bar(i, v, color=col, width=0.6, edgecolor="white")
        right.text(i, (vals[i - 1] if i and vals[i - 1] - v > 1e-12 else v) + 0.02, fmt(v, 2), ha="center", va="bottom",
                   fontsize=11, color=PALETTE["ink"])
        if i and vals[i - 1] - v > 1e-12:
            right.bar(i, vals[i - 1] - v, bottom=v, color="white", edgecolor=PALETTE["grey"], hatch="///", width=0.6, linewidth=1)
    right.axhline(cov, color=PALETTE["grey"], linestyle="dashed", linewidth=1.2)
    right.set_xticks(range(3), ["Oracle\ncoverage Cov", "Actual\nselection Sel", "Deployed\n(allowed tasks)"])
    right.set_xlim(-0.6, 2.6)
    right.set_ylim(0, 1.2)
    right.set_xlabel("Rung of the ladder (hatched: lost at that rung)")
    right.set_ylabel("Task-weighted success")
    right.set_title("Each rung can only lose success", fontsize=11.5)

    metrics = {
        "Bank": f"{m} candidate{'s' if m > 1 else ''}, {b['name']}",
        "Oracle coverage Cov": fmt(cov, 2),
        "Actual selection Sel": fmt(sel, 2),
        "Deployed success": fmt(dep, 2),
        "Lost to selection (Cov minus Sel)": fmt(cov - sel, 2),
        "Lost to deployment (Sel minus deployed)": fmt(sel - dep, 2),
        "Coverage as candidates are added": " / ".join(fmt(v, 2) for v in prefix),
        "Where each task stands": ", ".join(f"task {t + 1} {STATUS[w]}" for t, w in enumerate(where)),
    }
    who = ("takes the candidate the notebook case chooses, " + str(", ".join(str(c + 1) for c in chosen)) + " by task"
           if selector == "notebook" else "sees the pass labels and takes a passing candidate when one exists")
    deploy_text = "every task is allowed to deploy" if deploy == "all" else (
        "the tasks marked denied may not deploy: " + ", ".join(f"task {t + 1}" for t in range(nt) if not allowed[t]))
    absent = [t + 1 for t in range(nt) if where[t] == "absent"]
    note = (f" Task {absent[0]} has no passing candidate in this bank, so it adds nothing to Cov whatever the selector does; that loss "
            "sits upstream, in generation." if absent else "")
    interpretation = (
        f"Cov = {written_sum(weights, covered)} = {fmt(cov, 2)}. The selector {who}, so Sel = {written_sum(weights, won)} = {fmt(sel, 2)}. "
        f"Deployed = {written_sum(weights, shipped)} = {fmt(dep, 2)} because {deploy_text}. Cov - Sel = {fmt(cov, 2)} - {fmt(sel, 2)} = "
        f"{fmt(cov - sel, 2)} is lost to selection and Sel - deployed = {fmt(sel, 2)} - {fmt(dep, 2)} = {fmt(sel - dep, 2)} to deployment."
        f"{note}"
    )
    steps = [f"Weights {', '.join(fmt(w, 1) for w in weights)}; a task is covered if any candidate in the bank passes it.",
             f"Cov = {written_sum(weights, covered)} = {fmt(cov, 2)}.",
             f"Selector choices by task: {', '.join(str(c + 1) for c in chosen)}; Sel = {written_sum(weights, won)} = {fmt(sel, 2)}.",
             f"Deployed = {written_sum(weights, shipped)} = {fmt(dep, 2)}.",
             f"Ladder: {fmt(cov, 2)} then {fmt(sel, 2)} then {fmt(dep, 2)}; no rung is higher than the one before it.",
             "Where each task stands: " + ", ".join(f"{t + 1} {SHORT[w]}" for t, w in enumerate(where)) + "."]
    alt = (f"Left, a grid of candidates by tasks marking passes and the chosen candidate, with each task labeled "
           f"{', '.join(SHORT[w] for w in where)}. Right, a descending ladder of three bars: Cov {fmt(cov, 2)}, Sel {fmt(sel, 2)}, "
           f"deployed {fmt(dep, 2)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: where a coverage and selection pair sits, and what the gap points at

POINTS = {
    "codexs": {"name": "Codex-S, mean log-probability", "sel": 44.5, "cov": 77.5, "digits": 1},
    "codex12": {"name": "Codex-12B, one sample against pass@100", "sel": 28.81, "cov": 72.31, "digits": 2},
    "near": {"name": "constructed: selector near the ceiling", "sel": 78.0, "cov": 80.0, "digits": 1},
    "low": {"name": "constructed: low ceiling", "sel": 15.0, "cov": 20.0, "digits": 1},
}


def gap_picture(point="codexs", share=0.5):
    p = POINTS[point]
    d = p["digits"]
    sel, cov, share = p["sel"], p["cov"], float(share)
    gap = cov - sel
    gain = share * gap
    after = sel + gain
    left_over = cov - after
    fig, ax = new_figure(height=4.3)
    ax.fill([0, 0, 100], [0, 100, 100], facecolor="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=0)
    ax.plot([0, 100], [0, 100], color=PALETTE["ink"], linewidth=1.8)
    ax.plot([cov], [sel], "o", color=PALETTE["teal"], markersize=11, zorder=5)
    if gain > 1e-12:
        ax.plot([cov, cov], [sel, after], color=PALETTE["gold"], linewidth=3, zorder=4)
        ax.plot([cov], [after], "o", markerfacecolor="white", markeredgecolor=PALETTE["gold"], markeredgewidth=2, markersize=11, zorder=5)
    ax.plot([cov, cov], [after, cov], color=PALETTE["grey"], linewidth=1.6, linestyle="dashed")
    label_point(ax, cov, sel, f"Sel {fmt(sel, d)}", color=PALETTE["teal"], dx=-10, dy=-4, ha="right", va="top").set_bbox(BOX)
    if gain > 1e-12:
        label_point(ax, cov, after, f"after {fmt(after, d)}", color=PALETTE["gold"], dx=-10, dy=0, ha="right", va="center").set_bbox(BOX)
    label_point(ax, 98, 98, "Sel = Cov: the ceiling", color=PALETTE["ink"], dx=-6, dy=-8, ha="right", va="top").set_bbox(BOX)
    ax.text(0.03, 0.97, "hatched: Sel above Cov,\nnot possible", transform=ax.transAxes, ha="left", va="top", fontsize=10.5,
            color=PALETTE["grey"], bbox=BOX)
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_xlabel("Oracle coverage Cov (percent of problems)")
    ax.set_ylabel("Selected success Sel (percent)")
    ax.set_title(f"{p['name']}: gap {fmt(gap, d)} points", fontsize=11.5)

    metrics = {
        "Point": p["name"],
        "Cov (ceiling, percent)": fmt(cov, d),
        "Sel (delivered, percent)": fmt(sel, d),
        "Gap Cov minus Sel (points)": fmt(gap, d),
        "Gap as a share of the ceiling": fmt(gap / cov, 2),
        "Hypothetical share collected": fmt(share, 2),
        "New selected success": fmt(after, d),
        "Gap that remains": fmt(left_over, d),
    }
    if point == "codexs":
        reading = (f" The chapter reports 37.7 for a single Codex-S sample, so mean log-probability gained {fmt(sel, 1)} - 37.7 = "
                   f"{fmt(sel - 37.7, 1)} over one sample and left {fmt(gap, 1)} points of the test-selected result uncollected. "
                   "A wide gap points at validation, ranking or the evidence interface.")
    elif point == "codex12":
        reading = (f" Read naively, {fmt(cov, 2)} / {fmt(sel, 2)} = {fmt(cov / sel, 2)} suggests about two and a half times the capability. "
                   "The chapter's narrower claim: the larger number measures a declared generator under an oracle condition. Here the "
                   "lower point is one sample, not a ranking rule, so the gap is shown for scale and is not a same-bank selector gap.")
    elif point == "near":
        reading = (f" The gap {fmt(gap, 1)} is small beside the ceiling {fmt(cov, 1)}, so on this setup a more elaborate ranker has "
                   "little left to collect; the chapter points to candidate diversity, context, a permitted tool or the task decomposition. "
                   "This pair is constructed to show that case.")
    else:
        reading = (f" The ceiling itself is only {fmt(cov, 1)}, so even a perfect selector would not solve much; the chapter points to "
                   "the generator, its context, its tools or the task representation. This pair is constructed to show that case.")
    eq_clause = ", which is not negative" if point == "codex12" else ", which is not negative, as Equation (26.3) says"
    interpretation = (
        f"Gap = Cov - Sel = {fmt(cov, d)} - {fmt(sel, d)} = {fmt(gap, d)} points{eq_clause}. "
        f"If a new selector collected a hypothetical share {fmt(share, 2)} of it, success would be {fmt(sel, d)} + {fmt(share, 2)} x "
        f"{fmt(gap, d)} = {fmt(after, d)}, leaving {fmt(cov, d)} - {fmt(after, d)} = {fmt(left_over, d)} points.{reading} The share is a "
        "planning what-if: it becomes a result only when a selector is built and measured on the same bank, tasks and evaluator."
    )
    steps = [f"Ceiling Cov = {fmt(cov, d)} and delivered Sel = {fmt(sel, d)}, both in percent.",
             f"Gap = {fmt(cov, d)} - {fmt(sel, d)} = {fmt(gap, d)} points, and Sel stays on or below the line Sel = Cov.",
             f"Hypothetical gain = {fmt(share, 2)} x {fmt(gap, d)} = {fmt(gain, d)}.",
             f"New Sel = {fmt(sel, d)} + {fmt(gain, d)} = {fmt(after, d)}.",
             f"Gap that remains = {fmt(cov, d)} - {fmt(after, d)} = {fmt(left_over, d)}."]
    alt = (f"A square plot of selected success against oracle coverage with the line Sel = Cov and the region above it hatched. "
           f"The point sits at coverage {fmt(cov, d)} and selection {fmt(sel, d)}; a vertical segment shows the gap"
           + (f" and a hollow marker at {fmt(after, d)} shows the hypothetical share collected." if gain > 1e-12 else "."))
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: a saturation forecast depends on the family

OBS = [(10.0, 0.40), (25.0, 0.55), (50.0, 0.63)]
RATIO = (OBS[1][1] - OBS[0][1]) / (OBS[2][1] - OBS[1][1])  # 0.15 / 0.08 = 1.875


def _bisect(f, lo, hi):
    for _ in range(200):
        mid = (lo + hi) / 2
        if (f(lo) - RATIO) * (f(mid) - RATIO) <= 0:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def _fit(shape):
    """Exact three-point fit. Returns (shape parameter, B, A, curve)."""
    (k1, c1), (k2, c2), (k3, c3) = OBS
    if shape == "exp":
        basis = lambda k, p: math.exp(-k / p)
        ratio = lambda p: (basis(k1, p) - basis(k2, p)) / (basis(k2, p) - basis(k3, p))
        p = _bisect(ratio, 1.0, 400.0)
    elif shape == "hyp":
        basis = lambda k, p: 1 / (k + p)
        ratio = lambda p: (basis(k1, p) - basis(k2, p)) / (basis(k2, p) - basis(k3, p))
        p = _bisect(ratio, 0.01, 200.0)
    else:
        basis = lambda k, p: k ** (-p)
        ratio = lambda p: (basis(k1, p) - basis(k2, p)) / (basis(k2, p) - basis(k3, p))
        p = _bisect(ratio, 0.01, 3.0)
    b = (c2 - c1) / (basis(k1, p) - basis(k2, p))
    a = c3 + b * basis(k3, p)
    return p, b, a, (lambda k: a - b * basis(k, p))


DASHES = {"exp": (0, (4, 2)), "hyp": (0, (1, 1.5)), "pow": (0, (6, 2, 1, 2))}
FAMILIES = {
    "exp": ("Exponential approach", "tau", "e"),
    "hyp": ("Hyperbolic approach", "h", ""),
    "pow": ("Power-law approach", "a", ""),
}
HORIZON = 1000.0
SEL_AT_50 = {"near": 0.60, "far": 0.30}   # hypothetical selected success at k = 50, defined for this reader


def saturation_picture(family="exp", selector="far"):
    fits = {key: _fit(key) for key in FAMILIES}
    p, b, a, curve = fits[family]
    ks = np.geomspace(5, HORIZON, 90)
    ends = sorted(FAMILIES, key=lambda key: fits[key][3](HORIZON))
    RANK_SHIFT = {key: shift for key, shift in zip(ends, (-7, 0, 7))}
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    for key, (name, _, _) in FAMILIES.items():
        pk, bk, ak, ck = fits[key]
        chosen = key == family
        col = PALETTE["teal"] if chosen else PALETTE["grey"]
        style = "solid" if chosen else DASHES[key]
        left.plot(ks, [ck(k) for k in ks], color=col, linewidth=2.6 if chosen else 1.4, linestyle=style)
        label_point(left, HORIZON * 1.08, ck(HORIZON), name.split()[0].lower(), color=col, dx=0, dy=RANK_SHIFT[key], ha="left", va="center")
        left.axhline(ak, color=col, linewidth=1.2 if chosen else 0.8, linestyle="dotted")
        label_point(left, 5.3, ak, f"{name.split()[0].lower()} limit {fmt(ak, 2)}", color=PALETTE["teal"] if chosen else PALETTE["grey"],
                    dx=0, dy=4, ha="left", va="bottom")
    left.plot([k for k, _ in OBS], [c for _, c in OBS], "o", color=PALETTE["ink"], markersize=9, zorder=5)
    for k, c in OBS:
        label_point(left, k, c, f"({fmt(k, 0)}, {fmt(c, 2)})", color=PALETTE["ink"], dx=6, dy=-8, ha="left", va="top").set_bbox(BOX)
    left.set_xscale("log")
    left.set_xlim(5, HORIZON * 6)
    left.set_ylim(0.2, 0.97)
    left.set_xlabel("Candidates per task, k (log scale)")
    left.set_ylabel("Coverage")
    left.set_title(f"{FAMILIES[family][0]} through three points", fontsize=11.5)

    cov50 = OBS[2][1]
    c100 = curve(100.0)
    grow = c100 - cov50
    sel50 = SEL_AT_50[selector]
    room = cov50 - sel50
    bigger_bank = grow > room + 1e-12
    for i, (v, col, hat) in enumerate(((grow, PALETTE["teal"], ""), (room, PALETTE["navy"], "///"))):
        right.bar(i, v, color=col, hatch=hat, edgecolor="white", width=0.6)
        right.text(i, v + 0.015 * max(grow, room), fmt(v, 3), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    right.set_xticks([0, 1], ["Larger bank:\n50 to 100\ncandidates", f"Better selector\nat k = 50\n(Sel {fmt(sel50, 2)})"])
    right.set_xlim(-0.6, 1.6)
    right.set_ylim(0, max(grow, room) * 1.25 + 0.02)
    right.set_xlabel("Next destination for effort (hypothetical Sel)")
    right.set_ylabel("Room (coverage points)")
    right.set_title("Larger room: " + ("a larger bank" if bigger_bank else "a better selector"), fontsize=11.5)

    asymptotes = {key: fits[key][2] for key in FAMILIES}
    spread = max(asymptotes.values()) - min(asymptotes.values())
    metrics = {
        "Family": FAMILIES[family][0],
        f"Shape parameter ({FAMILIES[family][1]})": fmt(p, 2 if family != "exp" else 1),
        "Projected limit A": fmt(a, 3),
        "Curve at k = 100": fmt(c100, 3),
        "Limits of all three families": " / ".join(fmt(asymptotes[k], 2) for k in ("exp", "hyp", "pow")),
        "Spread of the limits (points)": fmt(100 * spread, 0),
        "Room from a larger bank (50 to 100)": fmt(grow, 3),
        "Room below the ceiling at k = 50": fmt(room, 3),
    }
    if family == "exp":
        calc = f"A = 0.63 + B x e^(-50/{fmt(p, 1)}) = 0.63 + {fmt(b, 3)} x {fmt(math.exp(-50 / p), 4)} = {fmt(a, 3)}"
    elif family == "hyp":
        calc = f"A = 0.63 + B / (50 + h) = 0.63 + {fmt(b, 3)} / (50 + {fmt(p, 2)}) = {fmt(a, 3)}"
    else:
        calc = f"A = 0.63 + B x 50^(-a) = 0.63 + {fmt(b, 3)} x {fmt(50 ** (-p), 4)} = {fmt(a, 3)}"
    wins = {}
    for key in FAMILIES:
        fk = fits[key][3]
        wins[key] = (fk(100.0) - cov50) > room + 1e-12
    if all(wins.values()):
        verdict = "all three families agree that a larger bank has the larger room at this selector value"
    elif not any(wins.values()):
        verdict = "all three families agree that the selector has the larger room at this selector value"
    else:
        bank_names = ", ".join(FAMILIES[k][0].split()[0].lower() for k in FAMILIES if wins[k])
        sel_names = ", ".join(FAMILIES[k][0].split()[0].lower() for k in FAMILIES if not wins[k])
        verdict = (f"the families disagree at this selector value: a larger bank has the larger room under the {bank_names} curve, "
                   f"the selector under the {sel_names} curve")
    interpretation = (
        f"{calc}. The three families all pass through 0.40, 0.55 and 0.63, yet their limits are {fmt(asymptotes['exp'], 2)}, "
        f"{fmt(asymptotes['hyp'], 2)} and {fmt(asymptotes['pow'], 2)}, a spread of {fmt(asymptotes['pow'], 2)} - "
        f"{fmt(asymptotes['exp'], 2)} = {fmt(spread, 2)}. Stopping question: this curve reads {fmt(c100, 3)} at k = 100, so doubling "
        f"the bank adds {fmt(c100, 3)} - {fmt(cov50, 2)} = {fmt(grow, 3)}. With a hypothetical selected success of {fmt(sel50, 2)} at "
        f"k = 50, room below the ceiling is {fmt(cov50, 2)} - {fmt(sel50, 2)} = {fmt(room, 3)}; {verdict}. The observed range cannot "
        "choose among the families, so the limit and the growth are forecasts that depend on the family, not observed results."
    )
    steps = [f"Observed coverage: 0.40 at k = 10, 0.55 at k = 25, 0.63 at k = 50.",
             f"{FAMILIES[family][0]} fitted exactly through them: shape {FAMILIES[family][1]} = {fmt(p, 2 if family != 'exp' else 1)}.",
             f"{calc}.",
             f"Curve at k = 100 is {fmt(c100, 3)}, so a larger bank adds {fmt(c100, 3)} - {fmt(cov50, 2)} = {fmt(grow, 3)}.",
             f"Room below the ceiling at k = 50: {fmt(cov50, 2)} - {fmt(sel50, 2)} = {fmt(room, 3)} (Sel is a hypothetical value).",
             "Compare the two rooms, then price latency and work before choosing; the comparison does not decide by itself."]
    alt = (f"Left, three curves fitted through the same three points on a log axis, with the {FAMILIES[family][0].lower()} highlighted and "
           f"limits near 0.65, 0.74 and 0.86. Right, two bars: room from doubling the bank to 100, {fmt(grow, 3)}, and room below the "
           f"ceiling for a selector at {fmt(sel50, 2)}, {fmt(room, 3)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 26,
    "title": "How Much More Could the System Become?",
    "subtitle": "A finite bank of candidates sets a conditional ceiling, and the gap to what a selector actually returns is an engineering question, not a forecast.",
    "summary": (
        "These four demonstrations follow the chapter's staged argument. A bank of candidates is a finite object with an exact "
        "coverage calculation that moves with the sampling rule. Coverage is a ceiling that no selector can pass, and success is "
        "lost at each rung from the bank to deployment. The gap below the ceiling points at an engineering question, and a curve "
        "fitted to a few points projects a limit that depends on the curve you pick."
    ),
    "ask_skill": {
        "prompt": (
            "Here is my candidate-by-task success matrix, my task weights, the candidate each task's selector chose, and which "
            "tasks may deploy. Compute oracle coverage, actual selection success and deployed success, tell me for each task "
            "whether the loss is in generation, selection or deployment, and say what I should build next."
        ),
    },
    "demos": [
        {
            "id": "C26-D01",
            "title": "A bank is a finite object, and its pool depends on how it was sampled",
            "question": "For fixed pools of ten programs per task, how often does a random subset contain a pass, how does that differ from an independent-draw guess, and how does the sampling rule change the answer?",
            "equations": [EQ_COVERAGE],
            "symbols": (
                "n is the number of programs generated for a task (10 here) and c the number that pass its tests. k is the size "
                "of the subset considered. C(n, k) counts the ways to choose k of n programs. The fraction C(n - c, k) / C(n, k) "
                "is the share of subsets with no pass, so one minus it is the chance a subset holds at least one pass. Equation "
                "(26.1) averages this over the tasks. The independent-draw formula is 1 - (1 - c / n)^k, which treats every pick "
                "as a fresh draw. The low and high temperature banks are constructed: low concentrates passes on a few tasks, "
                "high spreads them."
            ),
            "prediction": "With 2 passing programs among 10 and subsets of size 3, is the exact coverage above or below the independent-draw value 0.488?",
            "prediction_options": ["Above 0.488", "Below 0.488", "Equal to 0.488"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "Exact coverage is 1 - 56 / 120 = 0.533, above the independent-draw 0.488; they agree only at k = 1.",
                "incorrect": "Exact coverage is 1 - C(8,3) / C(10,3) = 1 - 56 / 120 = 0.533, while 1 - (1 - 0.20)^3 = 0.488. The two differ; step the subset size down to 1 to see them meet.",
            },
            "explanation": (
                "Count the subsets with no pass, divide by all subsets, and subtract from one. This is exact for the fixed pool, "
                "because subsets are drawn without replacement from programs that already exist. The independent-draw formula "
                "treats every pick as a fresh draw with the pool's pass rate, which is a different statistical question. A selector "
                "with no correctness signal succeeds only at the pass share c / n. The chapter's temperature point shows in the two "
                "banks: the concentrated bank is better at k = 1, the dispersed bank overtakes it as k grows, so the ceiling is not a "
                "property of the weights alone."
            ),
            "application": (
                "When a report gives a pass@k number, ask for the pool size n, the per-task pass counts, the subset size k and the "
                "sampling settings. Without them you cannot tell an exact pool calculation from an extrapolation, or compare two "
                "banks made at different temperatures."
            ),
            "assumptions": (
                "Pools of ten programs, labels fixed by the declared tests, subsets chosen uniformly without replacement. The two "
                "four-task banks are constructed to show the direction the chapter reports for temperature; they are not measurements. "
                "The result says nothing about programs outside the pool, other prompts or adaptive retries. If the ten programs repeat "
                "one wrong approach the labels are strongly correlated, and the pool still has exactly this coverage but little useful "
                "variety. The chapter's pools of 200 programs per task are too large for a pencil check and are not shown."
            ),
            "check": "If only 1 of the 10 programs passes and k = 4, what is the exact coverage?",
            "answer": "1 - C(9,4) / C(10,4) = 1 - 126 / 210 = 0.40, which equals k / n = 4 / 10.",
            "provenance": "Constructed example: the book's ten-candidate worked subset calculation (2 passing, size 3) and two constructed four-task banks that differ in how concentrated the passes are.",
            "source_section": "Stage two: a bank is a finite object",
            "source_anchor": "stage-two-a-bank-is-a-finite-object",
            "stepper": "subset",
            "misconception": {
                "title": "Pass@k is pass@1 pushed through independent draws",
                "text": (
                    "The chapter says the calculation is not one direct sequence of k trials and not an independent-draw extrapolation "
                    "from pass@1. Estimating pass@k as one minus one minus the empirical pass@1, raised to k, is biased; the finite-pool "
                    "combinatorial form is the exact subset probability."
                ),
            },
            "controls": [
                {"key": "pool", "label": "Bank of ten-program pools", "values": ["chapter", "low", "high"], "default": "chapter",
                 "value_labels": ["Chapter's worked pool (one task, 2 passing)", "Low temperature (passes 8, 8, 0, 0)", "High temperature (passes 3, 3, 2, 2)"]},
                {"key": "subset", "label": "Subset size k", "values": [1, 3, 5, 8], "default": 3},
            ],
            "function": "bank_picture",
        },
        {
            "id": "C26-D02",
            "title": "Coverage is a ceiling, and each rung can only lose success",
            "question": "Can any selector return a correct candidate more often than the bank contains one, and where does each task's success get lost on the way to deployment?",
            "equations": [EQ_CEILING],
            "symbols": (
                "Cov is oracle coverage: the weighted share of tasks for which at least one candidate in the bank passes. Sel is the "
                "weighted share of tasks for which the selector's chosen candidate passes. Deployed is the weighted share of tasks "
                "whose selected candidate passes and which are allowed to deploy. The weights are the task distribution. An oracle "
                "selector is shown the pass labels; the notebook selector is not."
            ),
            "prediction": "In the notebook's default case (three specialists, selector always takes candidate 1, every task deployable), what are Cov, Sel and deployed?",
            "prediction_options": ["1.00, 0.20, 0.20", "1.00, 1.00, 1.00", "0.20, 0.20, 0.20"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "Every task has a passing specialist (Cov = 1.00) but candidate 1 solves only the weight-0.2 task, so Sel = 0.20 and deployed = 0.20.",
                "incorrect": "Each task has a passing specialist, so Cov = 0.2 + 0.3 + 0.5 = 1.00. Always taking candidate 1 solves only the task of weight 0.2, so Sel = 0.20, and all tasks may deploy, so deployed = 0.20.",
            },
            "explanation": (
                "For each task the ceiling is 1 if any candidate passes and 0 otherwise, and a chosen candidate can pass only if one "
                "exists. So task by task the selector cannot exceed the ceiling, and the weighted sums keep that order. Deployment "
                "can only remove tasks again. A failed task therefore sits at one rung: absent from the bank (generation), present but "
                "missed (selection), or selected and passing but denied (deployment). Each calls for a different next step."
            ),
            "application": (
                "Before buying a better ranker, compute coverage on the bank you already have. If coverage is low, the generator, "
                "its context or its tools are the limit. Keep permission filtering out of correctness labels so a denied correct answer "
                "is not counted as a model error."
            ),
            "assumptions": (
                "Small constructed banks with fixed task weights and pass labels from one evaluator. The oracle selector uses information "
                "a deployed system may not have. The ceiling holds only for this bank and evaluator; a new candidate or a different "
                "evaluator changes the object being bounded. Adding a candidate cannot lower coverage, because a covered task stays covered."
            ),
            "check": "If only the heavy task (weight 0.5) were solved by anything in the bank, what is the largest Sel any selector could reach?",
            "answer": "Cov = 0.2 x 0 + 0.3 x 0 + 0.5 x 1 = 0.5, so Sel is at most 0.5 for every selector.",
            "provenance": "Constructed example: the laboratory's default, changed and transfer banks, computed with the laboratory's own bank-ceiling function, plus a two-candidate prefix of the default bank.",
            "source_section": "Stage three: oracle coverage is an information ceiling",
            "source_anchor": "stage-three-oracle-coverage-is-an-information-ceiling",
            "misconception": {
                "title": "High coverage proves the deployed selector can recover the answer",
                "text": (
                    "The chapter says no high coverage number proves that a deployed selector can recover the available answer, and no "
                    "stronger reranker can fully repair a generator whose bounded banks rarely contain a correct answer. Both mistakes "
                    "are blocked by the inequality Sel <= Cov."
                ),
            },
            "controls": [
                {"key": "bank", "label": "Bank", "values": ["diag", "prefix", "xfer"], "default": "diag",
                 "value_labels": ["Three specialists (notebook default)", "First two specialists only", "Two candidates, two tasks (notebook transfer)"]},
                {"key": "selector", "label": "Selector", "values": ["notebook", "oracle"], "default": "notebook",
                 "value_labels": ["The notebook case's selector", "Oracle: sees the pass labels"]},
                {"key": "deploy", "label": "Deployment permission", "values": ["all", "denied"], "default": "all",
                 "value_labels": ["Every task allowed", "The notebook's denied tasks"]},
            ],
            "function": "ladder_picture",
        },
        {
            "id": "C26-D03",
            "title": "What actual selection leaves behind",
            "question": "Where does a coverage and selection pair sit against the ceiling, how large is the gap, and what does the gap point at?",
            "equations": [EQ_GAP],
            "symbols": (
                "Cov(k) is the success when the oracle (the unit tests) chooses among k candidates and Sel(k) the success of the "
                "practical rule, both in percent of problems solved. The gap Cov minus Sel is measured in percentage points and cannot "
                "be negative. The share collected is a hypothetical fraction of that gap that a new selector might win back. Codex-S "
                "and Codex-12B figures are the chapter's reported percentages, used as given."
            ),
            "prediction": "Starting from Codex-S with mean log-probability selection (44.5 against 77.5), what success would collecting half the gap give?",
            "prediction_options": ["49.5", "55.0", "61.0", "77.5"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "The gap is 77.5 - 44.5 = 33.0, half is 16.5, and 44.5 + 16.5 = 61.0, still below the ceiling and only a hypothesis.",
                "incorrect": "The gap is 77.5 - 44.5 = 33.0 points. Half of it is 16.5, so success would be 44.5 + 16.5 = 61.0. Set the share control to 0.5 to see it.",
            },
            "explanation": (
                "The chapter reports one experiment with 100 candidates per problem: 37.7 percent for a single sample, 44.5 percent "
                "for choosing by mean log-probability, and 77.5 percent when unit tests choose. Subtract the practical rule from the "
                "unit-test result to get the gap. No selector can sit above the line Sel = Cov. Its distance below the line is what "
                "needs explaining: a large gap points at selection or evidence, a gap near zero or a low ceiling points back at "
                "generation, context, tools or budget."
            ),
            "application": (
                "Report delivered selection and the same-bank unit-test result side by side. Ask what part of the gap a practical "
                "intervention could collect under the deployment contract, then compare that gain with cost, latency, error, safety "
                "risk and permissions."
            ),
            "assumptions": (
                "The Codex percentages are the chapter's reported figures for one experiment, used as given and not re-measured, and "
                "they hold only for that generator, bank and tests. The collected share is a planning what-if with no data behind it. "
                "The two constructed pairs exist only to show the other two readings. Collecting any of the gap needs evidence available "
                "before the outcome is known, which a deployment may not have."
            ),
            "check": "A practical selector reaches 50.0 percent against 77.5 for unit tests. A new verifier is hoped to collect 40 percent of the gap. What is the new success?",
            "answer": "Gap = 77.5 - 50.0 = 27.5. New success = 50.0 + 0.4 x 27.5 = 61.0, a hypothesis until measured.",
            "provenance": "Constructed example: the chapter's reported Codex percentages used as given, two constructed coverage and selection pairs, and a hypothetical collected share defined for this reader.",
            "source_section": "Stage four: what actual selection leaves behind",
            "source_anchor": "stage-four-what-actual-selection-leaves-behind",
            "misconception": {
                "title": "The oracle number is a forecast of the product score",
                "text": (
                    "The chapter warns against calling the best offline score a roadmap forecast, and against describing the assistant as a "
                    "77.5-percent system before one exists under the deployment contract. The condition is the result."
                ),
            },
            "scope_note": {
                "text": (
                    "A finite candidate bank can set a ceiling for selectors with declared information, and the gap to actual selection "
                    "identifies an engineering question rather than an achieved capability. The chapter does not show that an "
                    "oracle-conditioned score transfers to deployment."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "point", "label": "Coverage and selection pair", "values": ["codexs", "codex12", "near", "low"], "default": "codexs",
                 "value_labels": ["Codex-S, mean log-probability (44.5 of 77.5)", "Codex-12B, one sample against pass@100 (28.81, 72.31)",
                                  "Constructed: selector near the ceiling", "Constructed: low ceiling"]},
                {"key": "share", "label": "Hypothetical share of the gap collected", "values": [0, 0.5, 1.0], "default": 0.5,
                 "value_labels": ["0", "0.5", "1.0"]},
            ],
            "function": "gap_picture",
        },
        {
            "id": "C26-D04",
            "title": "A saturation forecast depends on the curve",
            "question": "If three observed coverage points are fitted by three different curves, do they agree about the limit, and about whether a larger bank or a better selector has more room?",
            "equations": [EQ_EXP, EQ_HYP, EQ_POW],
            "symbols": (
                "k is the number of candidates per task and the curve value is coverage. A is the limit the curve approaches. The three formulas, in order, are the "
                "exponential, hyperbolic and power-law families, and e is Euler's number (about 2.718). A, B and the shape number "
                "(tau, h or a) are all fitted so that each curve passes exactly through the three observed points "
                "(10, 0.40), (25, 0.55) and (50, 0.63). Sel at k = 50 is a hypothetical selected success defined for this reader, "
                "0.60 or 0.30."
            ),
            "prediction": "All three curves hit the same three points. Which family projects the highest limit?",
            "prediction_options": ["Exponential", "Hyperbolic", "Power law"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "The power-law family projects about 0.86, against about 0.74 for the hyperbolic and 0.65 for the exponential.",
                "incorrect": "The limits are about 0.65 (exponential), 0.74 (hyperbolic) and 0.86 (power law). Switch the highlighted family to compare.",
            },
            "explanation": (
                "Three points fix three numbers, so every family fits them with no error. Beyond the observed range the families "
                "separate, and their limits come out near 0.65, 0.74 and 0.86. The data cannot say which family is right, so the "
                "limit reflects the choice of curve. The same holds for the stopping question: how much a larger bank adds depends on "
                "the family, and the room below the ceiling depends on how far the selector is from it."
            ),
            "application": (
                "Use a saturation curve to plan capacity inside a stated budget, and report the fitted family with it. When generation "
                "adds little coverage while selection stays far below coverage, the next increment of budget has two destinations: more "
                "candidates or a better way to judge the ones already present. Do not read the limit as a bound on what a changed prompt, "
                "tool or generator could reach."
            ),
            "assumptions": (
                "The chapter's constructed fixed-generator saturation curve: three made-up coverage points on one declared task "
                "bank. With more points or a physical reason for one family, the choice could narrow, but this example has neither. "
                "A changed generator, selector or task distribution gives a different curve, so no limit here is a bound on an open design space. "
                "The selected success values are hypothetical, and the comparison of rooms does not price latency, cost or work."
            ),
            "check": "Two fits agree on all three points but project limits of 0.65 and 0.86. By how much do they differ?",
            "answer": "0.86 - 0.65 = 0.21, a spread of 21 points that the three observed points cannot resolve.",
            "provenance": "Constructed example: the chapter's constructed coverage points (0.40, 0.55, 0.63 at 10, 25, 50 samples) fitted exactly by three curve families, with a hypothetical selected success defined for this reader.",
            "source_section": "A saturation forecast",
            "source_anchor": "a-saturation-forecast",
            "misconception": {
                "title": "A curve that fits every point has found the limit",
                "text": (
                    "The chapter says every curve fits the observed points, the projections spread over more than twenty points, and three "
                    "points cannot choose among families. The asymptote is a forecast that depends on the fitted family, not an observed result."
                ),
            },
            "scope_note": {
                "text": (
                    "This chapter does not identify a model's maximum capability, predict gains from unlimited compute or tools, or prove "
                    "that an oracle-conditioned score transfers to deployment."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "family", "label": "Highlighted curve family", "values": ["exp", "hyp", "pow"], "default": "exp",
                 "value_labels": ["Exponential approach", "Hyperbolic approach", "Power-law approach"]},
                {"key": "selector", "label": "Hypothetical selected success at k = 50", "values": ["near", "far"], "default": "far",
                 "value_labels": ["0.60 (selector near the ceiling)", "0.30 (selector far below it)"]},
            ],
            "function": "saturation_picture",
        },
    ],
}

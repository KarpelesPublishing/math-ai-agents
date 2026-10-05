"""Chapter 24 reader: How Much Capability Have We Extracted?

Four demonstrations.

Demonstration 1 follows one score through four sets of observations: the
book's constructed two-bank example (320 and 292 passes out of 400), the
laboratory's paired procedure records (default and changed task weights), the
laboratory's transfer records (no overlap between procedures) and the
chapter's constructed aged-benchmark mixture. The record cases are computed
with the laboratory's own function (math_ai_agents.chapters.ch24.evaluate);
the two-bank and mixture cases are closed forms, because the laboratory
function is a paired, record-level computation. Demonstration 2 shows how the
reported onset of a capability moves with the threshold and with which family
members were tested. Demonstration 3 builds a simultaneous lower frontier with a
union-bound Hoeffding margin. Demonstration 4 shows that a mean success rate does
not fix repeated-run reliability, on the chapter's two-task construction and on the
workbench's recorded bank of three successes and one failure. All numbers are constructed
teaching values.
"""
import math
from decimal import ROUND_HALF_UP, Decimal

import numpy as np
from matplotlib.patches import Rectangle

from math_ai_agents.chapters.ch24 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure


def half_up(x, digits=3):
    """Round half up on the decimal value, so two equal gaps never print as 0.023 and 0.022."""
    q = Decimal(1).scaleb(-digits)
    return str(Decimal(repr(round(x, 10))).quantize(q, rounding=ROUND_HALF_UP))


Z95 = 1.96  # large-sample two-sided 95 percent normal multiplier used in the chapter

EQ_AVERAGE = (
    r"\widehat U_{\mathcal V}(S)"
    r"= \frac{1}{N_{\mathrm{eval}}}\sum_{j=1}^{N_{\mathrm{eval}}} u_j."
)
EQ_MATCH = (
    r"\Delta_{\mathrm{match}}(\theta)"
    r"= \widehat U_{\mathcal V_{\mathrm{bench}}}(\{\theta\})"
    r"- \widehat U_{\mathcal V_{\mathrm{match}}}(\{\theta\})."
)
EQ_ONSET = r"\operatorname{Onset}_{\zeta}= \inf\{m: g(m)\ge \zeta\}."
EQ_FRONTIER = (
    r"\Pr\!\left[\forall \xi\in\mathcal C:"
    r"\operatorname{Lower}^{\mathrm{sim}}_{\alpha_{\mathrm{tail}}}(\xi)"
    r"\le U_{\mathcal V}(S_\xi)\right]\ge 1-\alpha_{\mathrm{tail}},"
    r"\qquad"
    r"\operatorname{LCF}_{\alpha_{\mathrm{tail}}}(\mathcal C)"
    r"=\max_{\xi\in\mathcal C}\operatorname{Lower}^{\mathrm{sim}}_{\alpha_{\mathrm{tail}}}(\xi)."
)
EQ_ATLEAST = r"1-(1-.9)^3=.999"
EQ_ALL = r".9^3=.729"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


def num(x, digits=2):
    text = fmt(x, digits)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


# Demonstration 1: observations, denominators and estimands

BENCH_PASSES, MATCH_PASSES, BANK = 320, 292, 400   # the chapter's constructed counts (400 tasks per bank)
SIZES = (100, 400, 1600)                           # same proportions, other bank sizes

DEFAULT_RECORDS = [
    {"procedure": "base", "task": "easy", "run": "0", "success": True, "cost": 1, "exposed": False},
    {"procedure": "base", "task": "hard", "run": "1", "success": False, "cost": 1, "exposed": True},
    {"procedure": "base", "task": "easy", "run": "2", "success": True, "cost": 1, "exposed": False},
    {"procedure": "base", "task": "hard", "run": "3", "success": False, "cost": 1, "exposed": True},
    {"procedure": "new", "task": "easy", "run": "0", "success": True, "cost": 2, "exposed": False},
    {"procedure": "new", "task": "hard", "run": "1", "success": True, "cost": 2, "exposed": True},
    {"procedure": "new", "task": "easy", "run": "2", "success": True, "cost": 2, "exposed": False},
    {"procedure": "new", "task": "hard", "run": "3", "success": False, "cost": 2, "exposed": True},
]
TRANSFER_RECORDS = [
    {"procedure": "old", "task": "alpha", "run": "one", "success": True, "cost": 1},
    {"procedure": "proposal", "task": "beta", "run": "two", "success": False, "cost": 3},
]
AGED_UNFAMILIAR, AGED_EXPOSED, AGED_SHARE = 0.4, 1.0, 0.2   # the chapter's aged-benchmark mixture

CASES = {
    "book": "Two independent banks (the chapter's table)",
    "lab": "Paired records, default and changed weights",
    "transfer": "Records with no overlap (transfer)",
    "aged": "An aged benchmark (constructed mixture)",
}
READINGS = {
    "scores": "Scores and their denominators",
    "gap": "The difference between two scores",
    "weights": "Re-weighting to a target",
}


def lab_eval(records, baseline, candidate, weights):
    return evaluate({"baseline": baseline, "candidate": candidate, "records": [dict(r) for r in records], "task_weights": dict(weights)})


def wald(p, n):
    half = Z95 * math.sqrt(p * (1 - p) / n)
    return p - half, p + half


def gap_row(n):
    pb, pm = round(0.80 * n) / n, round(0.73 * n) / n
    se = math.sqrt(pb * (1 - pb) / n + pm * (1 - pm) / n)
    d = pb - pm
    return pb, pm, d, se, d - Z95 * se, d + Z95 * se


def _finish(fig, metrics, interpretation, steps, alt):
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


def undefined_axes(ax, x_label, y_label, message):
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.text(0.5, 0.5, message, ha="center", va="center", fontsize=11.5, color=PALETTE["ink"], bbox=BOX, wrap=False)
    ax.grid(alpha=0)


def book_scores():
    n = BANK
    pb, pm = BENCH_PASSES / n, MATCH_PASSES / n
    fig, ax = new_figure(height=4.3)
    for i, (name, p, color, hatch, passes) in enumerate([("Benchmark", pb, PALETTE["navy"], "", BENCH_PASSES), ("Matched", pm, PALETTE["terracotta"], "//", MATCH_PASSES)]):
        a, b = wald(p, n)
        ax.bar(i, p, width=0.55, color=color, hatch=hatch, edgecolor="white" if not hatch else PALETTE["ink"], linewidth=1)
        ax.errorbar(i, p, yerr=[[p - a], [b - p]], color=PALETTE["ink"], capsize=6, linewidth=1.6)
        label_point(ax, i, b, f"{fmt(p, 2)}", color=PALETTE["ink"], dx=0, dy=4, ha="center")
    ax.set_xticks([0, 1], [f"Benchmark\n{BENCH_PASSES} of {n}", f"Matched\n{MATCH_PASSES} of {n}"])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Task bank (passes of independent tasks)")
    ax.set_ylabel("Pass proportion, with its own 95% interval")
    ax.set_title("Two independent banks of 400 tasks", fontsize=11.5)
    ha, hm = Z95 * math.sqrt(pb * (1 - pb) / n), Z95 * math.sqrt(pm * (1 - pm) / n)
    metrics = {"Benchmark score": fmt(pb, 2), "Matched score": fmt(pm, 2), "Tasks in each bank": str(n),
               "Half-width, benchmark": fmt(ha, 4), "Half-width, matched": fmt(hm, 4)}
    interp = (f"Benchmark = (1 / {n}) x {BENCH_PASSES} = {fmt(pb, 2)}; matched = (1 / {n}) x {MATCH_PASSES} = {fmt(pm, 2)}, the average of the scored outcomes in each bank (Equation 24.1). "
              f"Half-widths: 1.96 x sqrt({fmt(pb, 2)} x {fmt(1 - pb, 2)} / {n}) = {fmt(ha, 4)} and 1.96 x sqrt({fmt(pm, 2)} x {fmt(1 - pm, 2)} / {n}) = {fmt(hm, 4)}. "
              "Each score is only meaningful with its denominator and its contract.")
    steps = [f"Benchmark: {BENCH_PASSES} passes of {n} tasks, so {BENCH_PASSES} / {n} = {fmt(pb, 2)}.",
             f"Matched: {MATCH_PASSES} passes of {n} tasks, so {MATCH_PASSES} / {n} = {fmt(pm, 2)}.",
             f"Benchmark half-width = 1.96 x sqrt({fmt(pb, 2)} x {fmt(1 - pb, 2)} / {n}) = {fmt(ha, 4)}.",
             f"Matched half-width = 1.96 x sqrt({fmt(pm, 2)} x {fmt(1 - pm, 2)} / {n}) = {fmt(hm, 4)}."]
    alt = f"Two bars, benchmark {fmt(pb, 2)} and matched {fmt(pm, 2)}, each with a 95 percent interval, from 400 independent tasks per bank."
    return _finish(fig, metrics, interp, steps, alt)


def book_gap():
    rows = [gap_row(n) for n in SIZES]
    fig, ax = new_figure(height=4.3)
    ax.axvline(0, color=PALETTE["grey"], linestyle="dashed", linewidth=1.6)
    for i, (n, (pb, pm, d, se, lo, hi)) in enumerate(zip(SIZES, rows)):
        y = len(SIZES) - 1 - i
        color = PALETTE["teal"] if n == BANK else PALETTE["navy"]
        ax.errorbar([d], [y], xerr=[[d - lo], [hi - d]], fmt="o", color=color, capsize=7, markersize=9 if n == BANK else 7, linewidth=2.4 if n == BANK else 1.6)
        label_point(ax, hi, y, f"[{fmt(lo, 3)}, {fmt(hi, 3)}]", color=color, dx=6, dy=0, ha="left", va="center").set_bbox(BOX)
    ax.set_yticks(range(len(SIZES)), [f"{n} tasks\nper bank" for n in SIZES][::-1])
    ax.set_xlim(-0.14, 0.4)
    ax.set_ylim(-0.6, len(SIZES) - 0.4)
    ax.set_xlabel("Benchmark minus matched pass proportion (the gap, with a 95% interval)")
    ax.set_ylabel("Bank size")
    ax.set_title("The same 0.07 gap at three sample sizes", fontsize=11.5)
    ax.grid(axis="y", alpha=0)
    pb, pm, d, se, lo, hi = rows[1]
    excludes = [(r[4] > 0 or r[5] < 0) for r in rows]
    metrics = {
        "Gap (Equation 24.2)": fmt(d, 3),
        "Standard error at 100 tasks": fmt(rows[0][3], 5),
        "Standard error at 400 tasks": fmt(rows[1][3], 5),
        "Standard error at 1600 tasks": fmt(rows[2][3], 5),
        "95% interval at 400 tasks": f"[{fmt(lo, 5)}, {fmt(hi, 5)}]",
        "Interval excludes zero at 100, 400, 1600": ", ".join("yes" if e else "no" for e in excludes),
    }
    parts = []
    for n, r in zip(SIZES, rows):
        parts.append(f"n = {n}: sqrt(0.80 x 0.20 / {n} + 0.73 x 0.27 / {n}) = {fmt(r[3], 5)}")
    interp = (f"Gap = {fmt(rows[1][0], 2)} - {fmt(rows[1][1], 2)} = {fmt(d, 2)} at every size. Standard errors: " + "; ".join(parts) + ". "
              f"At 400 tasks the interval is {fmt(d, 2)} +/- 1.96 x {fmt(se, 5)} = [{fmt(lo, 5)}, {fmt(hi, 5)}], which excludes zero; at 100 tasks it is [{fmt(rows[0][4], 3)}, {fmt(rows[0][5], 3)}], which includes zero. "
              "Quadrupling the tasks per bank halves the standard error. Excluding zero does not say why the banks differ.")
    steps = [f"The gap is 0.80 - 0.73 = 0.07 at every size.",
             f"100 tasks: SE = {fmt(rows[0][3], 5)}, interval [{fmt(rows[0][4], 3)}, {fmt(rows[0][5], 3)}].",
             f"400 tasks: SE = {fmt(rows[1][3], 5)}, interval [{fmt(rows[1][4], 5)}, {fmt(rows[1][5], 5)}].",
             f"1600 tasks: SE = {fmt(rows[2][3], 5)}, interval [{fmt(rows[2][4], 3)}, {fmt(rows[2][5], 3)}]."]
    alt = "A gap of 0.07 with its 95 percent interval at 100, 400 and 1600 tasks per bank; the interval includes zero at 100 and excludes it at 400 and 1600."
    return _finish(fig, metrics, interp, steps, alt)


def book_weights():
    fig, ax = new_figure(height=4.3)
    undefined_axes(ax, "Task type", "Success rate by task type", "undefined: the two banks are independent samples\nwith no per-task cells to re-weight")
    ax.set_title("Nothing to re-weight", fontsize=11.5)
    metrics = {"Task-weighted score": "undefined (the banks have no task labels)", "Bank sizes": "400 and 400"}
    interp = ("The chapter's table records only passes out of independent tasks: 320 / 400 = 0.80 and 292 / 400 = 0.73, with no task type attached to each pass. "
              "A target mixture needs a rate per task type, so there is nothing to re-weight and the value is undefined here; switch to the record cases to see re-weighting.")
    steps = ["The table has passes and totals per bank: 320 of 400 and 292 of 400.",
             "A mixture needs a rate for each task type, and the table has none.",
             "So the re-weighted score is undefined, not zero."]
    alt = "An empty panel saying the two independent banks have no per-task cells, so a task-weighted score is undefined."
    return _finish(fig, metrics, interp, steps, alt)


def lab_scores():
    out = lab_eval(DEFAULT_RECORDS, "base", "new", {"easy": 0.5, "hard": 0.5})
    procs = out["metrics"]["procedures"]
    fig, ax = new_figure(height=4.3)
    groups = [("All runs", "rate", "n"), ("Exposed runs only", "exposed_rate", "exposed_n")]
    colors = {"base": PALETTE["navy"], "new": PALETTE["terracotta"]}
    hatches = {"base": "", "new": "//"}
    for g, (title, key, nkey) in enumerate(groups):
        for j, name in enumerate(("base", "new")):
            x = g * 3 + j * 1.0
            p = procs[name][key]
            ax.bar(x, p, width=0.8, color=colors[name], hatch=hatches[name], edgecolor="white" if not hatches[name] else PALETTE["ink"], linewidth=1)
            if key == "rate":
                lo, hi = procs[name]["wilson_interval_iid"]
                ax.errorbar(x, p, yerr=[[p - lo], [hi - p]], color=PALETTE["ink"], capsize=5, linewidth=1.5)
                top = hi
            else:
                top = p
            s = procs[name]["successes"] if key == "rate" else round(p * procs[name][nkey])
            label_point(ax, x, top, f"{s} of {procs[name][nkey]}", color=PALETTE["ink"], dx=0, dy=4, ha="center").set_bbox(BOX)
    ax.set_xticks([0.5, 3.5], ["All runs\n(Wilson interval)", "Exposed runs only\n(a subset)"])
    ax.set_xlim(-0.7, 4.7)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel("Denominator (navy: base, hatched: new)")
    ax.set_ylabel("Success rate")
    ax.set_title("Each rate carries its own denominator", fontsize=11.5)
    b, nw = procs["base"], procs["new"]
    metrics = {
        "Base score (all runs)": fmt(b["rate"], 2), "New score (all runs)": fmt(nw["rate"], 2),
        "Base 95% Wilson interval": f"[{fmt(b['wilson_interval_iid'][0], 3)}, {fmt(b['wilson_interval_iid'][1], 3)}]",
        "New 95% Wilson interval": f"[{fmt(nw['wilson_interval_iid'][0], 3)}, {fmt(nw['wilson_interval_iid'][1], 3)}]",
        "Exposed rate, base and new": f"{fmt(b['exposed_rate'], 2)} of {b['exposed_n']} and {fmt(nw['exposed_rate'], 2)} of {nw['exposed_n']}",
    }
    interp = (f"Base = {b['successes']} / {b['n']} = {fmt(b['rate'], 2)}; new = {nw['successes']} / {nw['n']} = {fmt(nw['rate'], 2)} (Equation 24.1 on each procedure's runs). "
              f"Exposed runs are the two hard runs of each procedure: base {round(b['exposed_rate'] * b['exposed_n'])} / {b['exposed_n']} = {fmt(b['exposed_rate'], 2)}, "
              f"new {round(nw['exposed_rate'] * nw['exposed_n'])} / {nw['exposed_n']} = {fmt(nw['exposed_rate'], 2)}. The exposed rate has a different denominator and describes only that subset. "
              "The intervals assume independent, representative runs, which four runs on two tasks cannot establish.")
    steps = ["Base succeeds on 2 of 4 runs: 2 / 4 = 0.50.", "New succeeds on 3 of 4 runs: 3 / 4 = 0.75.",
             "Exposed runs are the two hard runs of each procedure: base 0 / 2 = 0.00, new 1 / 2 = 0.50.",
             "Intervals are Wilson intervals under independent sampling, reported by the laboratory."]
    alt = "Bars for base and new: all-runs rates 0.50 and 0.75 with Wilson intervals, and exposed-subset rates 0.00 and 0.50 with two runs each."
    return _finish(fig, metrics, interp, steps, alt)


def lab_gap():
    out = lab_eval(DEFAULT_RECORDS, "base", "new", {"easy": 0.5, "hard": 0.5})
    m = out["metrics"]
    diffs = out["tables"]["matched_differences"]
    keys = ["easy/0", "hard/1", "easy/2", "hard/3"]
    delta, se = m["matched_difference"], m["matched_standard_error_iid_pairs"]
    fig, ax = new_figure(height=4.3)
    ax.axhspan(delta - se, delta + se, color=PALETTE["light"], alpha=0.55)
    ax.axhline(delta, color=PALETTE["teal"], linestyle="dashed", linewidth=1.6)
    ax.axhline(0, color=PALETTE["grey"], linewidth=1)
    for i, d in enumerate(diffs):
        ax.plot([i, i], [0, d], color=PALETTE["navy"], linewidth=2.2)
        ax.plot([i], [d], "o", color=PALETTE["navy"], markersize=10)
    label_point(ax, 3.4, delta, f"mean {fmt(delta, 2)}", color=PALETTE["teal"], dx=0, dy=4, ha="right", va="bottom").set_bbox(BOX)
    label_point(ax, 3.4, delta + se, f"shaded: one standard error, {fmt(se, 2)}", color=PALETTE["grey"], dx=0, dy=4, ha="right", va="bottom").set_bbox(BOX)
    ax.set_xticks(range(4), keys)
    ax.set_xlim(-0.5, 3.5)
    ax.set_ylim(-0.25, 1.25)
    ax.set_yticks([0, 1])
    ax.set_xlabel("Task / run pair (declared identifiers, not randomization)")
    ax.set_ylabel("New minus base on that pair")
    ax.set_title("Four matched pairs", fontsize=11.5)
    mean_diff = sum(diffs) / len(diffs)
    dev = sum((d - mean_diff) ** 2 for d in diffs)
    metrics = {"Matched pairs": str(m["matched_n"]), "Paired differences": ", ".join(str(d) for d in diffs),
               "Matched difference": fmt(delta, 2), "Standard error (independent pairs)": fmt(se, 2)}
    interp = (f"Paired differences are {', '.join(str(d) for d in diffs)}. Mean = (0 + 1 + 0 + 0) / 4 = {fmt(mean_diff, 2)}. "
              f"Sum of squared deviations = 3 x (0 - 0.25)^2 + (1 - 0.25)^2 = {fmt(dev, 2)}, variance = {fmt(dev, 2)} / 3 = {fmt(dev / 3, 2)}, "
              f"standard error = sqrt({fmt(dev / 3, 2)} / 4) = {fmt(se, 2)}. Only the pairs both procedures attempted enter, and matching identifiers alone does not make the comparison randomized or causal.")
    steps = ["All four task/run keys were attempted by both procedures, so there are 4 matched pairs.",
             "Differences (new minus base): 0, 1, 0, 0.", "Mean = (0 + 1 + 0 + 0) / 4 = 0.25.",
             f"Sum of squared deviations = 3 x (0 - 0.25)^2 + (1 - 0.25)^2 = {fmt(dev, 2)}.",
             f"Standard error = sqrt(({fmt(dev, 2)} / 3) / 4) = {fmt(se, 2)}."]
    alt = "Four paired differences, three zeros and one 1, with their mean 0.25 and a band of one standard error 0.25."
    return _finish(fig, metrics, interp, steps, alt)


def lab_weights():
    equal = lab_eval(DEFAULT_RECORDS, "base", "new", {"easy": 0.5, "hard": 0.5})["metrics"]["task_mixture_rates"]
    heavy = lab_eval(DEFAULT_RECORDS, "base", "new", {"easy": 0.1, "hard": 0.9})["metrics"]["task_mixture_rates"]
    task_rates = {"easy": {"base": 1.0, "new": 1.0}, "hard": {"base": 0.0, "new": 0.5}}
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    colors = {"base": PALETTE["navy"], "new": PALETTE["terracotta"]}
    hatches = {"base": "", "new": "//"}
    for g, task in enumerate(("easy", "hard")):
        for j, name in enumerate(("base", "new")):
            x = g * 3 + j
            v = task_rates[task][name]
            left.bar(x, v, width=0.8, color=colors[name], hatch=hatches[name], edgecolor="white" if not hatches[name] else PALETTE["ink"], linewidth=1)
            label_point(left, x, v, fmt(v, 2), color=PALETTE["ink"], dx=0, dy=4, ha="center")
    left.set_xticks([0.5, 3.5], ["Easy tasks\n(2 runs each)", "Hard tasks\n(2 runs each)"])
    left.set_xlim(-0.7, 4.7)
    left.set_ylim(0, 1.2)
    left.set_xlabel("Task type (navy: base, hatched: new)")
    left.set_ylabel("Observed success rate")
    left.set_title("Observations: they never change", fontsize=11.5)
    for g, (title, mix) in enumerate((("Equal weights\n0.5 easy, 0.5 hard", equal), ("Hard-heavy\n0.1 easy, 0.9 hard", heavy))):
        for j, name in enumerate(("base", "new")):
            x = g * 3 + j
            v = mix[name]
            right.bar(x, v, width=0.8, color=colors[name], hatch=hatches[name], edgecolor="white" if not hatches[name] else PALETTE["ink"], linewidth=1)
            label_point(right, x, v, fmt(v, 2), color=PALETTE["ink"], dx=0, dy=4, ha="center")
    right.set_xticks([0.5, 3.5], ["Equal weights\n0.5 and 0.5", "Hard-heavy\n0.1 and 0.9"])
    right.set_xlim(-0.7, 4.7)
    right.set_ylim(0, 1.2)
    right.set_xlabel("Target mixture (easy weight, hard weight)")
    right.set_ylabel("Mixture-weighted success rate")
    right.set_title("Estimand: it changes", fontsize=11.5)
    metrics = {"Base and new, equal weights": f"{fmt(equal['base'], 2)} and {fmt(equal['new'], 2)}",
               "Base and new, hard-heavy": f"{fmt(heavy['base'], 2)} and {fmt(heavy['new'], 2)}",
               "Base and new on hard tasks": "0.00 and 0.50", "Records changed": "none"}
    interp = (f"Easy rates are 1 and 1; hard rates are 0 and 0.5. Equal weights: base 0.5 x 1 + 0.5 x 0 = {fmt(equal['base'], 2)}, new 0.5 x 1 + 0.5 x 0.5 = {fmt(equal['new'], 2)}. "
              f"Hard-heavy weights: base 0.1 x 1 + 0.9 x 0 = {fmt(heavy['base'], 2)}, new 0.1 x 1 + 0.9 x 0.5 = {fmt(heavy['new'], 2)}. "
              "The observations did not change; the estimand did, and the weights name the target population.")
    steps = ["Task rates: easy 1 and 1; hard 0 and 0.5 (base and new).",
             "Equal weights: base 0.5 x 1 + 0.5 x 0 = 0.50; new 0.5 x 1 + 0.5 x 0.5 = 0.75.",
             "Hard-heavy: base 0.1 x 1 + 0.9 x 0 = 0.10; new 0.1 x 1 + 0.9 x 0.5 = 0.55.",
             "Same rows, different weights: the estimand changed, not the data."]
    alt = "Left: observed success by task type, easy 1 and 1, hard 0 and 0.5. Right: mixture scores 0.50 and 0.75 under equal weights and 0.10 and 0.55 under hard-heavy weights."
    return _finish(fig, metrics, interp, steps, alt)


def transfer_scores():
    out = lab_eval(TRANSFER_RECORDS, "old", "proposal", {"alpha": 0.5, "beta": 0.5})
    procs = out["metrics"]["procedures"]
    fig, ax = new_figure(height=4.3)
    for i, (name, color, hatch) in enumerate([("old", PALETTE["navy"], ""), ("proposal", PALETTE["terracotta"], "//")]):
        p = procs[name]["rate"]
        lo, hi = procs[name]["wilson_interval_iid"]
        ax.bar(i, p, width=0.55, color=color, hatch=hatch, edgecolor="white" if not hatch else PALETTE["ink"], linewidth=1)
        ax.errorbar(i, p, yerr=[[p - lo], [hi - p]], color=PALETTE["ink"], capsize=6, linewidth=1.6)
        label_point(ax, i, hi, f"{procs[name]['successes']} of {procs[name]['n']}", color=PALETTE["ink"], dx=0, dy=4, ha="center").set_bbox(BOX)
    ax.set_xticks([0, 1], ["old\n(alpha only)", "proposal\n(beta only)"])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 1.2)
    ax.set_xlabel("Procedure (one run each)")
    ax.set_ylabel("Observed success rate, with Wilson interval")
    ax.set_title("A rate from one run is wide open", fontsize=11.5)
    z2 = 1.959963984540054 ** 2
    center = (1 + z2 / 2) / (1 + z2)
    metrics = {"Old score": f"{fmt(procs['old']['rate'], 2)} (1 of 1)", "Proposal score": f"{fmt(procs['proposal']['rate'], 2)} (0 of 1)",
               "Old Wilson interval": f"[{fmt(procs['old']['wilson_interval_iid'][0], 3)}, {fmt(procs['old']['wilson_interval_iid'][1], 3)}]",
               "Proposal Wilson interval": f"[{fmt(procs['proposal']['wilson_interval_iid'][0], 3)}, {fmt(procs['proposal']['wilson_interval_iid'][1], 3)}]"}
    interp = (f"Old = 1 / 1 = 1.00 and proposal = 0 / 1 = 0.00, so the raw rates exist. With one run each the denominators are thin: the Wilson center for old is "
              f"(1 + 3.84 / 2) / (1 + 3.84) = {fmt(center, 2)}, giving the wide interval [{fmt(procs['old']['wilson_interval_iid'][0], 3)}, 1.000]. "
              "The raw rates are not an estimate of improvement, because the two procedures never attempted the same task.")
    steps = ["Old attempted alpha once and succeeded: 1 / 1 = 1.00.", "Proposal attempted beta once and failed: 0 / 1 = 0.00.",
             f"Wilson center for old = (1 + 3.84 / 2) / (1 + 3.84) = {fmt(center, 2)}.",
             "The two rates describe different tasks, so their difference is not a comparison."]
    alt = "Two bars, old at 1.00 and proposal at 0.00, each from one run, with wide Wilson intervals."
    return _finish(fig, metrics, interp, steps, alt)


def _grid(ax, columns, observed, x_label, y_label, title):
    rows = ["old", "proposal"]
    for r, row in enumerate(rows[::-1]):
        for c, col in enumerate(columns):
            seen = observed[(row, col)]
            ax.add_patch(Rectangle(
                (c + 0.04, r + 0.06), 0.92, 0.88, facecolor="#cfe3e4" if seen else "white",
                edgecolor=PALETTE["teal"] if seen else PALETTE["terracotta"], linewidth=1.4, hatch=None if seen else "///"))
            ax.text(c + 0.5, r + 0.5, "observed" if seen else "missing", ha="center", va="center", fontsize=11, color=PALETTE["ink"], bbox=None if seen else BOX)
    ax.set_xlim(0, len(columns))
    ax.set_ylim(0, 2)
    ax.set_xticks([c + 0.5 for c in range(len(columns))], columns)
    ax.set_yticks([0.5, 1.5], rows[::-1])
    ax.set_xlabel(x_label)
    ax.set_ylabel(y_label)
    ax.set_title(title, fontsize=11.5)
    ax.grid(alpha=0)


def transfer_gap():
    columns = ["alpha / one", "beta / two"]
    observed = {("old", "alpha / one"): True, ("old", "beta / two"): False, ("proposal", "alpha / one"): False, ("proposal", "beta / two"): True}
    out = lab_eval(TRANSFER_RECORDS, "old", "proposal", {"alpha": 0.5, "beta": 0.5})
    if out["metrics"]["matched_n"] != 0:
        raise AssertionError("transfer records should have no matched pair")
    fig, ax = new_figure(height=4.3)
    _grid(ax, columns, observed, "Task / run pair", "Procedure", "No pair was attempted by both")
    metrics = {"Matched pairs": "0", "Matched difference": "undefined (no task/run pair was attempted by both procedures)",
               "Standard error": "undefined (needs at least 2 matched pairs)"}
    interp = ("Matched pairs = (old and proposal both observed) 0 + 0 = 0: alpha / one was run only by old and beta / two only by proposal. "
              "The mean of zero paired differences is 0 / 0, which has no value, so the matched difference and its standard error are undefined, not zero. "
              "Returning 0 would falsely imply no difference, and borrowing another procedure's outcome would fabricate evidence.")
    steps = ["Old observed alpha / one; proposal observed beta / two.", "A matched pair needs both procedures on the same task and run: 0 + 0 = 0 pairs.",
             "The matched difference is a mean over 0 pairs, so it is undefined.", "Next step: run both procedures on the missing cells."]
    alt = "A grid of two procedures and two task/run pairs; old has only alpha / one and proposal only beta / two, so no column has both."
    return _finish(fig, metrics, interp, steps, alt)


def transfer_weights():
    columns = ["alpha", "beta"]
    observed = {("old", "alpha"): True, ("old", "beta"): False, ("proposal", "alpha"): False, ("proposal", "beta"): True}
    out = lab_eval(TRANSFER_RECORDS, "old", "proposal", {"alpha": 0.5, "beta": 0.5})
    if any(v is not None for v in out["metrics"]["task_mixture_rates"].values()):
        raise AssertionError("transfer mixture should be unavailable")
    fig, ax = new_figure(height=4.3)
    _grid(ax, columns, observed, "Task with positive target weight (0.5 each)", "Procedure", "Cells a 50/50 mixture needs")
    metrics = {"Cells needed": "4 (2 procedures x 2 tasks)", "Cells observed": "2", "Mixture score, old": "undefined (beta never observed)",
               "Mixture score, proposal": "undefined (alpha never observed)"}
    interp = ("A 50/50 mixture over alpha and beta needs a rate for every positively weighted task and procedure: 2 x 2 = 4 cells. Observed cells = 1 + 1 = 2 of 4. "
              "Old has no beta cell and proposal has no alpha cell, so both mixture scores are undefined. The useful next step is a measurement request for the missing cells (old on beta, proposal on alpha).")
    steps = ["Target weights: alpha 0.5, beta 0.5, so both tasks are needed for each procedure.", "Cells needed: 2 procedures x 2 tasks = 4.",
             "Cells observed: 1 + 1 = 2 of 4.", "Old lacks beta and proposal lacks alpha, so neither mixture can be estimated."]
    alt = "A grid of two procedures and two tasks with two cells missing: old on beta and proposal on alpha."
    return _finish(fig, metrics, interp, steps, alt)


def aged_scores():
    s = AGED_SHARE
    agg = s * AGED_EXPOSED + (1 - s) * AGED_UNFAMILIAR
    fig, ax = new_figure(height=4.3)
    vals = [AGED_UNFAMILIAR, AGED_EXPOSED, agg]
    colors = [PALETTE["navy"], PALETTE["gold"], PALETTE["terracotta"]]
    hatches = ["", "..", "//"]
    for i, (v, c, h) in enumerate(zip(vals, colors, hatches)):
        ax.bar(i, v, width=0.6, color=c if not h else "white", edgecolor=c if h else "white", hatch=h, linewidth=1.4)
        label_point(ax, i, v, fmt(v, 2), color=PALETTE["ink"], dx=0, dy=4, ha="center")
    ax.set_xticks(range(3), ["Unfamiliar\ntasks (80%)", "Exposed\ntasks (20%)", "Logged\naggregate"])
    ax.set_xlim(-0.6, 2.6)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel("Which tasks the success rate is about")
    ax.set_ylabel("Success rate")
    ax.set_title("One number mixes two populations", fontsize=11.5)
    metrics = {"Unfamiliar-task success": "0.40", "Exposed-task success": "1.00", "Exposed share": "20%", "Aggregate success": fmt(agg, 2)}
    interp = (f"Aggregate = 0.2 x 1 + 0.8 x 0.4 = {fmt(0.2 * 1 + 0.8 * 0.4, 2)}. The rate on unfamiliar tasks is 0.40; the aggregate hides it behind a mixture. "
              "A rising aggregate score alone cannot identify a gain on unfamiliar tasks.")
    steps = ["Unfamiliar-task success is 0.4 and exposed-task success is 1.", "Exposed tasks are 20 percent of the evaluation, unfamiliar ones 80 percent.",
             f"Aggregate = 0.2 x 1 + 0.8 x 0.4 = {fmt(agg, 2)}."]
    alt = "Three bars: unfamiliar tasks 0.40, exposed tasks 1.00 and the logged aggregate 0.52."
    return _finish(fig, metrics, interp, steps, alt)


def aged_gap():
    s = AGED_SHARE
    agg = s * AGED_EXPOSED + (1 - s) * AGED_UNFAMILIAR
    diff = agg - AGED_UNFAMILIAR
    fig, ax = new_figure(height=4.3)
    ax.bar(0, AGED_UNFAMILIAR, width=0.5, color=PALETTE["navy"])
    ax.bar(0, diff, bottom=AGED_UNFAMILIAR, width=0.5, color="white", edgecolor=PALETTE["terracotta"], hatch="///", linewidth=1.4)
    label_point(ax, 0, AGED_UNFAMILIAR / 2, "0.40 on\nunfamiliar tasks", color="white", dx=0, dy=0, ha="center", va="center")
    label_point(ax, 0.3, AGED_UNFAMILIAR + diff / 2, f"+ {fmt(diff, 2)}: added\nby the mixture alone", color=PALETTE["terracotta"], dx=4, dy=0, ha="left", va="center").set_bbox(BOX)
    label_point(ax, 0, agg, f"aggregate {fmt(agg, 2)}", color=PALETTE["ink"], dx=0, dy=6, ha="center")
    ax.set_xticks([0], ["Logged aggregate"])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 0.8)
    ax.set_xlabel("The number a report would show")
    ax.set_ylabel("Success rate")
    ax.set_title("The 12-point lift is declared, not measured", fontsize=11.5)
    metrics = {"Aggregate": fmt(agg, 2), "Unfamiliar-task success": "0.40", "Difference": fmt(diff, 2), "Difference in points": f"{round(diff * 100)}"}
    interp = (f"Difference = {fmt(agg, 2)} - 0.40 = {fmt(diff, 2)}, which equals the exposed share times the gap between exposed and unfamiliar success: 0.2 x (1 - 0.4) = {fmt(0.2 * 0.6, 2)}. "
              "The twelve-point difference comes entirely from the declared mixture. It is not a measured contamination effect in any real audit.")
    steps = [f"Aggregate = {fmt(agg, 2)}; unfamiliar-task success = 0.40.", f"Difference = {fmt(agg, 2)} - 0.40 = {fmt(diff, 2)}.",
             "Check: exposed share x (exposed - unfamiliar) = 0.2 x (1 - 0.4) = 0.12.", "No unfamiliar-task skill changed."]
    alt = "One stacked bar: 0.40 on unfamiliar tasks plus a hatched 0.12 added by the mixture, totalling 0.52."
    return _finish(fig, metrics, interp, steps, alt)


def aged_weights():
    shares = np.linspace(0, 1, 101)
    line = AGED_UNFAMILIAR + (AGED_EXPOSED - AGED_UNFAMILIAR) * shares
    fig, ax = new_figure(height=4.3)
    ax.plot(shares, line, color=PALETTE["navy"], linewidth=2.2)
    ax.axhline(AGED_UNFAMILIAR, color=PALETTE["grey"], linestyle="dotted", linewidth=1.6)
    label_point(ax, 1.0, AGED_UNFAMILIAR, "unfamiliar-task success 0.40", color=PALETTE["grey"], dx=0, dy=-4, ha="right", va="top").set_bbox(BOX)
    for x, tag, dx, dy, ha, va in ((0.0, "no exposed tasks", 8, -8, "left", "top"), (AGED_SHARE, "chapter: 20% exposed", 10, -8, "left", "top")):
        y = AGED_UNFAMILIAR + 0.6 * x
        ax.plot([x], [y], "o", color=PALETTE["terracotta"], markersize=9, zorder=4)
        label_point(ax, x, y, f"{tag}\n{fmt(y, 2)}", color=PALETTE["terracotta"], dx=dx, dy=dy, ha=ha, va=va).set_bbox(BOX)
    ax.set_xlim(0, 1)
    ax.set_ylim(0.3, 1.05)
    ax.set_xlabel("Exposed share of the evaluation")
    ax.set_ylabel("Aggregate success rate")
    ax.set_title("The aggregate rises with exposure alone", fontsize=11.5)
    agg = AGED_UNFAMILIAR + 0.6 * AGED_SHARE
    metrics = {"Aggregate at 0% exposed": "0.40", "Aggregate at 20% exposed": fmt(agg, 2), "Aggregate at 50% exposed": fmt(AGED_UNFAMILIAR + 0.6 * 0.5, 2),
               "Unfamiliar-task skill": "unchanged at 0.40"}
    interp = (f"Aggregate(s) = s x 1 + (1 - s) x 0.4 = 0.4 + 0.6 s. At s = 0: 0.4 + 0.6 x 0 = 0.40. At s = 0.2: 0.4 + 0.6 x 0.2 = {fmt(agg, 2)}. At s = 0.5: 0.4 + 0.6 x 0.5 = {fmt(0.4 + 0.3, 2)}. "
              "The unfamiliar-task rate never moved: only the declared mixture did, so a rising aggregate cannot identify a gain on unfamiliar work.")
    steps = ["Aggregate = s x 1 + (1 - s) x 0.4 = 0.4 + 0.6 s.", "At s = 0 the aggregate is 0.4 x 1 = 0.40.", f"At s = 0.2: 0.4 + 0.6 x 0.2 = {fmt(agg, 2)}.",
             "The unfamiliar-task success stayed at 0.4 throughout."]
    alt = "A rising line of aggregate success against exposed share, from 0.40 at no exposure to 0.52 at the chapter's 20 percent, over a flat dotted line at 0.40."
    return _finish(fig, metrics, interp, steps, alt)


DISPATCH = {
    ("book", "scores"): book_scores, ("book", "gap"): book_gap, ("book", "weights"): book_weights,
    ("lab", "scores"): lab_scores, ("lab", "gap"): lab_gap, ("lab", "weights"): lab_weights,
    ("transfer", "scores"): transfer_scores, ("transfer", "gap"): transfer_gap, ("transfer", "weights"): transfer_weights,
    ("aged", "scores"): aged_scores, ("aged", "gap"): aged_gap, ("aged", "weights"): aged_weights,
}


def observations_picture(case="book", reading="scores"):
    return DISPATCH[(case, reading)]()


# Demonstration 2: onset depends on the threshold and on which members were tested

MEMBERS = [1, 2, 3, 4, 5, 6, 7, 8]
G_HUNDREDTHS = [4, 9, 17, 30, 46, 58, 66, 71]  # constructed continuous scores, in hundredths
TESTED_SETS = {"all": MEMBERS, "odd": [1, 3, 5, 7], "even": [2, 4, 6, 8]}


def onset_picture(threshold=0.5, tested="all"):
    z = round(float(threshold) * 100)
    members = TESTED_SETS[tested]
    scores = {m: g for m, g in zip(MEMBERS, G_HUNDREDTHS)}
    reached = [m for m in members if scores[m] >= z]
    onset = reached[0] if reached else None

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.plot(MEMBERS, [g / 100 for g in G_HUNDREDTHS], "o", markerfacecolor="white", markeredgecolor=PALETTE["grey"], markersize=8)
    left.plot(members, [scores[m] / 100 for m in members], "o-", color=PALETTE["navy"], markersize=8)
    left.axhline(z / 100, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.6)
    label_point(left, 1, z / 100, f"threshold {fmt(z / 100, 2)}", color=PALETTE["terracotta"], dx=0, dy=6, ha="left").set_bbox(BOX)
    if onset is not None:
        left.axvline(onset, color=PALETTE["teal"], linestyle="dotted", linewidth=2)
        label_point(left, onset, 0.0, f"onset m = {onset}", color=PALETTE["teal"], dx=-5 if onset > 4 else 5, dy=4,
                    ha="right" if onset > 4 else "left").set_bbox(BOX)
    else:
        label_point(left, 4.5, 0.8, f"no tested member reaches {fmt(z / 100, 2)}", color=PALETTE["teal"], dx=0, dy=0,
                    ha="center", va="center").set_bbox(BOX)
    left.set_xlim(0.5, 8.5)
    left.set_ylim(-0.03, 0.85)
    left.set_xticks(MEMBERS)
    left.set_xlabel("Family member m (declared scale order; hollow = not tested)")
    left.set_ylabel("Continuous score g(m)")
    left.set_title("The score rises gradually", fontsize=11.5)

    flags = [1 if scores[m] >= z else 0 for m in members]
    right.bar(members, flags, width=0.6, color=[PALETTE["teal"] if f else "white" for f in flags],
              edgecolor=PALETTE["ink"], hatch="//", linewidth=1)
    for m, f in zip(members, flags):
        if not f:
            right.text(m, 0.04, "0", ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    right.set_xlim(0.5, 8.5)
    right.set_ylim(0, 1.25)
    right.set_xticks(MEMBERS)
    right.set_yticks([0, 1])
    if onset is not None:
        label_point(right, 4.5, 1.12, f"first pass at m = {onset}", color=PALETTE["teal"], dx=0, dy=0, ha="center", va="center")
    else:
        label_point(right, 4.5, 1.12, "no member passes", color=PALETTE["teal"], dx=0, dy=0, ha="center", va="center")
    right.set_xlabel("Family member m (blank: not tested)")
    right.set_ylabel("Pass indicator (1 if g(m) reaches threshold)")
    right.set_title("The pass indicator jumps", fontsize=11.5)

    full_onset = next((m for m in MEMBERS if scores[m] >= z), None)
    if onset is not None:
        margin = scores[onset] - z
        before = [m for m in members if m < onset]
        step = (f" The member before it in this tested set is m = {before[-1]} with g = {fmt(scores[before[-1]] / 100, 2)}, "
                f"{fmt((z - scores[before[-1]]) / 100, 2)} short of the threshold." if before else "")
        calc = (f"Smallest tested m with g(m) >= {fmt(z / 100, 2)} is m = {onset}, where g({onset}) = "
                f"{fmt(scores[onset] / 100, 2)}; margin = {fmt(scores[onset] / 100, 2)} - {fmt(z / 100, 2)} = {fmt(margin / 100, 2)}.{step} ")
        if tested == "all":
            verdict = ("The score curve rises gradually; only the declared threshold turns it into a pass. A different threshold "
                       "or a sparser tested set can move this onset.")
        elif full_onset == onset:
            verdict = (f"The score curve rises gradually; only the declared threshold turns it into a pass. Testing only these "
                       f"members leaves the onset at m = {onset}, the same as with all eight members.")
        else:
            verdict = (f"The score curve rises gradually; only the declared threshold turns it into a pass. Testing only these "
                       f"members moves the onset from m = {full_onset} (all eight tested) to m = {onset}.")
        shown = f"m = {onset}"
    else:
        best = max(scores[m] for m in members)
        calc = (f"The largest tested score is {fmt(best / 100, 2)}, and {fmt(best / 100, 2)} - {fmt(z / 100, 2)} = "
                f"{fmt((best - z) / 100, 2)} is below zero, so no tested member reaches the threshold. ")
        if tested == "all":
            verdict = "The set whose smallest element would be the onset is empty."
        else:
            verdict = (f"The set whose smallest element would be the onset is empty among the tested members, so Equation (24.3) has no value there. "
                       f"That means untested, not never: member {full_onset} was skipped and does reach {fmt(scores[full_onset] / 100, 2)}.")
        shown = f"undefined (no tested member reaches {fmt(z / 100, 2)})"
    interpretation = calc + verdict
    metrics = {
        "Threshold": fmt(z / 100, 2),
        "Members tested": ", ".join(str(m) for m in members),
        "Onset": shown,
        "Highest tested score": fmt(max(scores[m] for m in members) / 100, 2),
        "Onset with all eight tested": f"m = {full_onset}" if full_onset else "undefined",
    }
    steps = [
        f"Threshold zeta = {fmt(z / 100, 2)}; tested members: {', '.join(str(m) for m in members)}.",
        "Scores of the tested members: " + ", ".join(f"g({m}) = {fmt(scores[m] / 100, 2)}" for m in members) + ".",
        (f"The first tested member with g(m) >= zeta is m = {onset}." if onset is not None else "No tested member has g(m) >= zeta, so the set is empty."),
        (f"With all eight members the onset would be m = {full_onset}." if full_onset else "Even with all eight members no member reaches zeta."),
    ]
    alt = (f"Left: a rising score curve over eight family members with a threshold line at {fmt(z / 100, 2)}; "
           f"{'onset at member ' + str(onset) if onset is not None else 'no tested member reaches it'}. Right: pass indicators that jump from 0 to 1 at the onset.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: a simultaneous lower frontier over the tested set

CONFIGS = [
    ("Direct prompt", 0.60),
    ("Retrieval", 0.68),
    ("Retrieval and tools", 0.72),
    ("Tools and selector", 0.74),
]
ALPHA = 0.05


def hoeffding_margin(n, k, alpha=ALPHA):
    """One-sided Hoeffding deviation, split across k configurations by a union bound."""
    return math.sqrt(math.log(k / alpha) / (2 * n))


def frontier_picture(tasks=400, tested=4):
    n, k = int(tasks), int(tested)
    chosen = CONFIGS[:k]
    t = hoeffding_margin(n, k)
    t_single = hoeffding_margin(n, 1)
    lowers = {name: rate - t for name, rate in chosen}
    best_name = max(lowers, key=lowers.get)
    lcf = lowers[best_name]

    fig, ax = new_figure(height=4.3)
    rows = list(range(k, 0, -1))
    for y, (name, rate) in zip(rows, chosen):
        lower = lowers[name]
        ax.barh(y, lower, height=0.56, color=PALETTE["teal"])
        ax.barh(y, rate - lower, left=lower, height=0.56, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1)
        ax.text(0.015, y, f"lower {fmt(lower, 2)}", va="center", ha="left", fontsize=11, color="white")
        # If the dashed LCF line would cross the label, start the label just right of the line instead.
        x_est = rate + 0.012
        if x_est - 0.01 < lcf < x_est + 0.2:
            x_est = lcf + 0.012
        ax.text(x_est, y, f"est. {fmt(rate, 2)}", va="center", ha="left", fontsize=11, color=PALETTE["ink"],
                zorder=5, bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.95})
    ax.barh(0, 1.0, height=0.56, color="white", edgecolor=PALETTE["grey"], hatch="..", linewidth=1, linestyle="dashed")
    ax.text(0.02, 0, "untested: no evidence", va="center", ha="left", fontsize=11, color=PALETTE["ink"],
            bbox={"boxstyle": "round,pad=0.25", "fc": "white", "ec": "none", "alpha": 0.95})
    ax.axvline(lcf, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.8)
    top = k + 1.3
    label_point(ax, lcf, top - 0.45, f"LCF = {fmt(lcf, 2)}", color=PALETTE["terracotta"], dx=-5 if lcf > 0.5 else 5, dy=0,
                ha="right" if lcf > 0.5 else "left", va="center").set_bbox(BOX)
    ax.set_yticks(rows + [0], [name for name, _ in chosen] + ["Other configurations"])
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.6, top)
    ax.set_xlabel("Success proportion (solid = supported lower bound, hatched = gap to the estimate)")
    ax.set_ylabel("Configuration")
    ax.set_title(f"{n} tasks per configuration; {k} configurations tested", fontsize=11.5)
    ax.grid(axis="y", alpha=0)

    untested = [name for name, _ in CONFIGS[k:]]
    note = (f" The configurations {', '.join(untested)} were never run, so they sit outside the frontier even though the list "
            "names them." if untested else "")
    metrics = {
        "Configurations tested": str(k),
        "Simultaneous margin t": fmt(t, 3),
        "Margin if one configuration were tested alone": fmt(t_single, 3),
        "Frontier value (LCF)": fmt(lcf, 3),
        "Configuration that sets it": best_name,
    }
    best_rate = dict(chosen)[best_name]
    interpretation = (
        f"Margin t = sqrt(ln({k}/{fmt(ALPHA, 2)}) / (2 x {n})) = sqrt({fmt(math.log(k / ALPHA), 3)} / {2 * n}) = {fmt(t, 3)}. "
        f"Lower bound for {best_name} = {fmt(best_rate, 2)} - {fmt(t, 3)} = {fmt(lcf, 3)}, the largest of the {k} jointly "
        f"supported bounds, so LCF = {fmt(lcf, 3)}. Testing one configuration alone would use "
        f"sqrt(ln(1/{fmt(ALPHA, 2)}) / (2 x {n})) = {fmt(t_single, 3)}; the extra {fmt(t - t_single, 3)} is the price of "
        f"having looked at {k}.{note} The frontier is evidence of what was achieved, not a ceiling."
    )
    steps = [
        f"Each configuration gets alpha / {k} = {fmt(ALPHA / k, 4)} of the failure budget.",
        f"Margin t = sqrt(ln({k}/{fmt(ALPHA, 2)}) / (2 x {n})) = {fmt(t, 3)}.",
        f"Lower bounds: " + ", ".join(f"{name} {fmt(rate, 2)} - {fmt(t, 3)} = {fmt(rate - t, 3)}" for name, rate in chosen) + ".",
        f"LCF is the largest lower bound, {fmt(lcf, 3)}, set by {best_name}.",
    ]
    alt = (f"Horizontal bars for {k} tested configurations, each with a solid lower bound and a hatched gap to its estimate, a dashed frontier line at {fmt(lcf, 2)}, "
           "and a dotted bar marking the untested configurations as no evidence.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: the same average, different repeated-run reliability

PAIRS = {"0.50": (0.5, 0.5), "0.20": (0.2, 0.8), "0.10": (0.1, 0.9)}
BANK_RUNS = (3, 4)  # a recorded bank: 3 successes in 4 runs of one task


def reliability_picture(bank="0.20", runs=2):
    k = int(runs)
    recorded = bank == "recorded"
    if recorded:
        c, n = BANK_RUNS
        mean = c / n
        true_all = math.comb(c, k) / math.comb(n, k)
        true_any = 1 - math.comb(n - c, k) / math.comb(n, k)
        title = f"Recorded bank: {c} successes in {n} runs of one task; plug-in rate {fmt(mean, 2)}"
        left_labels = ["Subset\nfractions", "Plug-in\nformula", "Subset\nfractions", "Plug-in\nformula"]
        x_label = "How the number is computed (hatched = plug-in from the observed rate)"
    else:
        lo_p, hi_p = PAIRS[bank]
        mean = (lo_p + hi_p) / 2
        true_all = (lo_p ** k + hi_p ** k) / 2
        true_any = ((1 - (1 - lo_p) ** k) + (1 - (1 - hi_p) ** k)) / 2
        title = f"Two tasks at {fmt(lo_p, 2)} and {fmt(hi_p, 2)}; mean single-run rate {fmt(mean, 2)}"
        left_labels = ["Average\nof tasks", "Mean rate\nformula", "Average\nof tasks", "Mean rate\nformula"]
        x_label = "How the number is computed (hatched = uses only the mean single-run rate)"
    naive_all = mean ** k
    naive_any = 1 - (1 - mean) ** k

    fig, ax = new_figure(height=4.3)
    xs = [0, 1, 2.8, 3.8]
    values = [true_all, naive_all, true_any, naive_any]
    colors = [PALETTE["navy"], PALETTE["navy"], PALETTE["teal"], PALETTE["teal"]]
    hatches = ["", "//", "", "//"]
    for x, v, c_, h in zip(xs, values, colors, hatches):
        ax.bar(x, v, width=0.7, color="white" if h else c_, edgecolor=c_ if h else "white", hatch=h, linewidth=1.4)
        label_point(ax, x, v, half_up(v, 3), color=PALETTE["ink"], dx=0, dy=4, ha="center")
    ax.set_xticks(xs, left_labels)
    ax.set_xlim(-0.6, 4.4)
    ax.set_ylim(0, 1.3)
    ax.grid(axis="x", alpha=0)
    label_point(ax, 0.5, 1.22, f"all {k} runs succeed", color=PALETTE["navy"], dx=0, dy=0, ha="center", va="center")
    label_point(ax, 3.3, 1.22, "at least one succeeds", color=PALETTE["teal"], dx=0, dy=0, ha="center", va="center")
    ax.set_xlabel(x_label)
    ax.set_ylabel("Probability" if not recorded else "Probability or fraction of subsets")
    ax.set_title(title, fontsize=11.5)

    gap_all = true_all - naive_all
    gap_any = naive_any - true_any
    power = "Squaring the mean rate" if k == 2 else f"Raising the mean rate to the power {k}"
    if recorded:
        verdict = (f"The subset fractions are descriptive counts of this recorded bank (and unbiased estimators of the task's probabilities only if the runs are independent resets of a "
                   f"frozen procedure); the plug-in formulas treat the observed rate {fmt(mean, 2)} as if it were the true rate. {power} gives {half_up(naive_all, 3)} against the subset fraction {half_up(true_all, 3)}.")
        calc = (f"All {k} runs: C({BANK_RUNS[0]},{k}) / C({BANK_RUNS[1]},{k}) = {math.comb(BANK_RUNS[0], k)} / {math.comb(BANK_RUNS[1], k)} = {half_up(true_all, 3)}, while {fmt(mean, 2)}^{k} = {half_up(naive_all, 3)}. "
                f"At least one: 1 - C(1,{k}) / C(4,{k}) = 1 - {math.comb(1, k)} / {math.comb(4, k)} = {half_up(true_any, 3)}, while 1 - (1 - {fmt(mean, 2)})^{k} = {half_up(naive_any, 3)}. ")
    else:
        lo_p, hi_p = PAIRS[bank]
        if abs(gap_all) < 1e-9:
            verdict = ("Both tasks have the same success rate, so there is no spread between tasks and the mean-rate formulas "
                       "agree with the task-by-task averages. The two methods only differ when tasks differ.")
        else:
            verdict = (f"{power} misses by {half_up(gap_all)} for all-runs success (it understates) and the "
                       f"coverage-style formula misses by {half_up(gap_any)} for at-least-one success (it overstates). "
                       "The task is drawn once and then repeated, which is the dependence the mean rate hides.")
        calc = (f"All {k} runs: ({fmt(lo_p, 2)}^{k} + {fmt(hi_p, 2)}^{k}) / 2 = ({fmt(lo_p ** k, 4)} + {fmt(hi_p ** k, 4)}) / 2 = "
                f"{half_up(true_all, 3)}, while {fmt(mean, 2)}^{k} = {half_up(naive_all, 3)}. At least one: "
                f"((1 - {fmt(1 - lo_p, 2)}^{k}) + (1 - {fmt(1 - hi_p, 2)}^{k})) / 2 = "
                f"({fmt(1 - (1 - lo_p) ** k, 4)} + {fmt(1 - (1 - hi_p) ** k, 4)}) / 2 = {half_up(true_any, 3)}, while "
                f"1 - (1 - {fmt(mean, 2)})^{k} = {half_up(naive_any, 3)}. ")
    interpretation = calc + verdict
    if recorded:
        metrics = {
            "Observed success rate": fmt(mean, 2),
            "All runs, subset fraction": half_up(true_all, 3),
            "All runs, plug-in formula": half_up(naive_all, 3),
            "At least one, subset fraction": half_up(true_any, 3),
            "At least one, plug-in formula": half_up(naive_any, 3),
        }
    else:
        metrics = {
            "Mean single-run success": fmt(mean, 2),
            "All runs, average of tasks": half_up(true_all, 3),
            "All runs, mean-rate formula": half_up(naive_all, 3),
            "At least one, average of tasks": half_up(true_any, 3),
            "At least one, mean-rate formula": half_up(naive_any, 3),
        }
    if recorded:
        steps = [f"Observed bank: {BANK_RUNS[0]} successes in {BANK_RUNS[1]} runs, so k-run subsets number C(4,{k}) = {math.comb(4, k)}.",
                 f"Subsets with only successes: C(3,{k}) = {math.comb(3, k)}, fraction {math.comb(3, k)} / {math.comb(4, k)} = {half_up(true_all, 3)}.",
                 f"Subsets with at least one success: {math.comb(4, k)} - C(1,{k}) = {math.comb(4, k) - math.comb(1, k)}, fraction {half_up(true_any, 3)}.",
                 f"Plug-in: {fmt(mean, 2)}^{k} = {half_up(naive_all, 3)} and 1 - (1 - {fmt(mean, 2)})^{k} = {half_up(naive_any, 3)}."]
    else:
        steps = [f"Task rates {fmt(lo_p, 2)} and {fmt(hi_p, 2)}; mean single-run rate {fmt(mean, 2)}.",
                 f"All {k} runs per task: {fmt(lo_p, 2)}^{k} = {fmt(lo_p ** k, 4)} and {fmt(hi_p, 2)}^{k} = {fmt(hi_p ** k, 4)}; average {half_up(true_all, 3)}.",
                 f"At least one in {k} runs: {fmt(1 - (1 - lo_p) ** k, 4)} and {fmt(1 - (1 - hi_p) ** k, 4)}; average {half_up(true_any, 3)}.",
                 f"Mean-rate formulas: {fmt(mean, 2)}^{k} = {half_up(naive_all, 3)} and 1 - (1 - {fmt(mean, 2)})^{k} = {half_up(naive_any, 3)}."]
    alt = (f"Four bars: all {k} runs succeed {half_up(true_all, 3)} against the {'plug-in' if recorded else 'mean-rate'} value {half_up(naive_all, 3)}, and at least one succeeds {half_up(true_any, 3)} against {half_up(naive_any, 3)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 24,
    "title": "How Much Capability Have We Extracted?",
    "subtitle": "A score describes a system, a task sample and a measurement procedure together, and it needs its boundary to be read.",
    "summary": (
        "These four demonstrations follow the chapter's rule that a number travels with its contract. They show how one score depends on its denominator, "
        "its sampling and its target mixture, how a reported onset depends on a threshold, what a best tested configuration can claim after paying for the search, "
        "and why a mean success rate does not fix repeated-run reliability. Every number is a constructed teaching value."
    ),
    "ask_skill": {
        "prompt": ("I have a table of procedure, task and run records with success flags, plus an optional target mixture over tasks. "
                   "Report each procedure's observed rate with its denominator, the matched difference and its standard error, the target-mixture rates, "
                   "and say which quantities are unavailable and what comparison I would need to run to fill the gap."),
    },
    "demos": [
        {
            "id": "C24-D01",
            "title": "Observations, denominators and estimands",
            "question": "What do these observations support, and which quantities change when the sample size, the pairing or the target mixture changes while the records stay the same?",
            "equations": [EQ_AVERAGE, EQ_MATCH],
            "symbols": (
                "A score is the average of the scored outcomes u_j over N_eval evaluation instances (Equation 24.1), for one named system, task draw, scoring rule and contract V. "
                "Delta_match is the benchmark pass proportion minus the matched-bank pass proportion for the same fixed model. The two-bank case has independent tasks, so the standard error of the gap is "
                "sqrt(p1(1 - p1)/n + p2(1 - p2)/n) and the 95% interval is the gap plus or minus 1.96 standard errors. The record cases come from the laboratory's paired design: a procedure's rate is its successes over its own runs, "
                "a matched difference uses only task/run pairs both procedures attempted, and a target mixture weights task-specific rates and needs every positively weighted task observed. "
                "The aged-benchmark case mixes success on unfamiliar tasks (0.4) with success on exposed tasks (1.0) at an exposed share of 20 percent."
            ),
            "prediction": "In the two-bank case on 'The difference between two scores', the same 0.07 gap is shown at 100, 400 and 1600 tasks per bank. At 100 tasks does the interval include zero?",
            "prediction_options": [
                "Yes: at 100 tasks the interval is about 0.07 plus or minus 0.117, so it includes zero",
                "No: a gap of 0.07 always excludes zero",
                "It cannot be said without the cause of the gap",
            ],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "The standard error at 100 tasks is sqrt(0.80 x 0.20 / 100 + 0.73 x 0.27 / 100) = 0.0598, so the interval is 0.07 plus or minus 1.96 x 0.0598 = 0.117, which includes zero. Choose the two-bank case and the difference reading to see all three sizes.",
                "incorrect": "Whether a gap excludes zero depends on the sample size, not only on the gap: at 100 tasks the standard error is 0.0598 and 1.96 x 0.0598 = 0.117 exceeds 0.07, so the interval includes zero. Choose the two-bank case and the difference reading to see all three sizes.",
            },
            "explanation": (
                "Every score is an average over a stated denominator, so the first thing to read is what was counted. A gap between two independent banks has noise that adds, and that noise falls with the number of tasks. "
                "When the records are paired, only the pairs both procedures attempted enter the difference, and when records do not overlap the matched difference does not exist. "
                "A target mixture changes the estimand without touching a single observation, and a mixture with exposed tasks can raise the aggregate without any gain on unfamiliar tasks."
            ),
            "application": (
                "Before reporting that a procedure improved, report each denominator, the number of matched pairs, the interval and the target mixture, "
                "so a reader can tell a real discrepancy from a thin sample, a missing cell or a changed population."
            ),
            "assumptions": (
                "The two-bank interval needs independent samples with adequately populated pass and fail counts and does not cover choosing the largest gap after inspecting many models. "
                "The paired standard error and the Wilson intervals need independent representative pairs or runs, which repeated runs of the same task may violate; identifiers declare pairing, not randomization. "
                "The aged-benchmark mixture is the chapter's declared construction, not a measured contamination effect."
            ),
            "misconception": {
                "title": "An interval that excludes zero identifies contamination",
                "text": ("The chapter says the interval excludes zero under its sampling model but does not identify contamination, memorization, changed reasoning or an unmatched task feature as the cause. "
                         "Matching observed features is not randomized assignment of training exposure."),
            },
            "scope_note": {
                "text": ("A matched held-out set can strengthen one comparison while leaving unmeasured task differences, selection effects and transfer limits open. "
                         "The bounded conclusion is that an evaluation supports claims about the declared system, protocol, sample and task distribution that produced its score."),
                "source_section": "What this does not settle",
            },
            "check": "Work this one by hand (800 tasks per bank is not shown). Benchmark 0.80 and matched 0.73 on 800 tasks each: what is the standard error of the gap, and does the interval exclude zero? And what is the aged benchmark's aggregate if 50 percent of its tasks were exposed?",
            "answer": (
                "SE = sqrt(0.80 x 0.20 / 800 + 0.73 x 0.27 / 800) = sqrt(0.0002 + 0.000246) = sqrt(0.000446) = 0.0211, between the 400-task value 0.0299 and the 1600-task value 0.0149, "
                "so the interval 0.07 plus or minus 1.96 x 0.0211 = [0.029, 0.111] excludes zero. "
                "At a 50 percent exposed share the aggregate is 0.5 x 1 + 0.5 x 0.4 = 0.70, which is 0.30 above the unfamiliar-task rate of 0.40."
            ),
            "provenance": ("Constructed example: the book's teaching counts (320 and 292 passes out of 400, not GSM1k measurements), the laboratory's default, changed and transfer record cases "
                           "evaluated with the laboratory's own function, and the chapter's constructed aged-benchmark mixture (0.4 unfamiliar, 1.0 exposed, 20 percent exposed)."),
            "source_section": "The matched question is not the same question twice",
            "source_anchor": "the-matched-question-is-not-the-same-question-twice",
            "controls": [
                {"key": "case", "label": "Observations", "values": list(CASES), "default": "book", "value_labels": list(CASES.values())},
                {"key": "reading", "label": "What to read off", "values": list(READINGS), "default": "scores", "value_labels": list(READINGS.values())},
            ],
            "function": "observations_picture",
        },
        {
            "id": "C24-D02",
            "title": "An onset belongs to its threshold",
            "question": "If a score rises gradually with scale, how much does the reported onset of a capability depend on the chosen threshold and on which sizes were tested?",
            "equations": [EQ_ONSET],
            "symbols": (
                "m numbers the members of a model family in their declared scale order. g(m) is a continuous score under one "
                "fixed protocol. zeta is the threshold. Onset is the smallest m whose score reaches zeta; inf means the smallest "
                "such value in the tested set. If the set is empty there is no onset."
            ),
            "prediction": "At threshold 0.70 with only members 1, 3, 5 and 7 tested, is there an onset?",
            "prediction_options": ["Yes, at m = 7", "Yes, at m = 8", "No: no tested member reaches 0.70, so the onset is undefined"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "g(7) = 0.66 is below 0.70 and member 8, which reaches 0.71, was not tested, so the set is empty: untested, not never. Choose threshold 0.7 and the odd members to see it.",
                "incorrect": "Among members 1, 3, 5 and 7 the largest score is g(7) = 0.66, below 0.70, and member 8 (0.71) was not tested, so no tested member passes and the onset is undefined. Choose threshold 0.7 and the odd members to see it.",
            },
            "explanation": (
                "The score curve is smooth, but a pass indicator turns on at the first member that reaches the threshold. "
                "Raising the threshold moves that crossing to the right. Testing fewer members can move it further, and can "
                "remove it from the tested set altogether. The onset is a property of the curve, the threshold and the sampling "
                "of sizes together."
            ),
            "application": (
                "When someone reports that an ability appears at a certain size, ask for the continuous curve, the threshold, and the "
                "onset at two or three nearby thresholds. If the onset moves a lot, say the onset is threshold-sensitive."
            ),
            "assumptions": (
                "One constructed curve of eight ordered members under one stable protocol, with no sampling noise on g. "
                "A crossing is an operational record, not a certified phase transition. Real scores carry uncertainty that could "
                "move a crossing by itself."
            ),
            "misconception": {
                "title": "The onset is a phase transition in the system",
                "text": ("The chapter says Equation (24.3) cannot certify a phase transition: it records an operational crossing that depends on the threshold, the metric, the family order and the protocol, "
                         "and practical importance does not make the threshold a law of nature."),
            },
            "scope_note": {
                "text": ("The chapter leaves a model's maximum capability, a universal measure of reasoning and a complete cause of any benchmark gap open. "
                         "A tested set leaves untested prompts, tools, budgets, selectors and future model states open."),
                "source_section": "What this does not settle",
            },
            "check": "With all eight members tested, what is the onset at threshold 0.60? And with only the even members tested?",
            "answer": ("g(6) = 0.58 is below 0.60 and g(7) = 0.66 is at or above it, with margin 0.66 - 0.60 = 0.06, so the onset is m = 7. "
                       "With only members 2, 4, 6 and 8 tested the first score at or above 0.60 is g(8) = 0.71, so the onset moves to m = 8."),
            "provenance": "Constructed example: eight family scores defined for this reader (0.04, 0.09, 0.17, 0.30, 0.46, 0.58, 0.66, 0.71), not a measured scale profile.",
            "source_section": "Scale profiles and extraction profiles are different maps",
            "source_anchor": "scale-profiles-and-extraction-profiles-are-different-maps",
            "controls": [
                {"key": "threshold", "label": "Threshold zeta", "values": [0.3, 0.5, 0.6, 0.7], "default": 0.5},
                {"key": "tested", "label": "Family members tested", "values": ["all", "odd", "even"], "default": "all",
                 "value_labels": ["All eight members", "Only members 1, 3, 5, 7", "Only members 2, 4, 6, 8"]},
            ],
            "function": "onset_picture",
        },
        {
            "id": "C24-D03",
            "title": "A lower frontier is evidence, not a ceiling",
            "question": "If several configurations are tested, what can we claim for the best one after paying for having looked at all of them?",
            "equations": [EQ_FRONTIER],
            "symbols": (
                "C is the finite set of tested configurations, xi one of them, and U its true success rate under the stated "
                "contract. Lower is a bound from a joint procedure that holds for every configuration at once with probability "
                "at least 1 minus alpha. LCF is the largest of those bounds. Here alpha is 0.05 and n is the number of tasks "
                "per configuration. In Equation (24.4), V is the declared evaluation contract (task distribution, evaluation unit, scoring rule, component partition, "
                "information and action interfaces, budget, horizon and baseline), S_xi is the set of components enabled in configuration xi, and Lower^sim is instantiated here as the observed rate minus "
                "the margin t."
            ),
            "prediction": "Keep 400 tasks but test only the first two configurations. Does the margin t shrink or grow compared with testing four?",
            "prediction_options": ["It shrinks, because fewer configurations share the failure budget", "It grows", "It stays the same"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "With two configurations the failure budget is split two ways, t = sqrt(ln(2 / 0.05) / 800) = 0.068, against 0.074 for four. Switch the configurations control to see it.",
                "incorrect": "The budget alpha is split across the tested configurations, so fewer configurations means a smaller margin: sqrt(ln(2 / 0.05) / 800) = 0.068 against 0.074 for four. Switch the configurations control to see it.",
            },
            "explanation": (
                "Each configuration's lower bound is its observed rate minus a margin. To make all bounds hold together, "
                "the allowed failure probability is split across the tested configurations, which widens the margin. The frontier "
                "is the largest of those lower bounds. Configurations that were not tested do not appear in the maximum."
            ),
            "application": (
                "If a program tries several prompts, tools or budgets, report how many were tried and use a margin that "
                "pays for the search, instead of presenting the highest score as if it were the only planned comparison."
            ),
            "assumptions": (
                "The margin used here is one way to build the joint bound: a one-sided Hoeffding deviation for independent "
                "tasks scored between 0 and 1, with the failure budget split equally by a union bound. Other designs give "
                "other margins. If tasks are dependent, the independence-based margin is no longer justified (and may be too small under positive dependence)."
            ),
            "misconception": {
                "title": "The best tested score is the system's maximum",
                "text": ("The chapter calls the frontier a lower frontier: the best tested result is evidence that at least that much was extracted under one tested configuration, "
                         "and it leaves a finite tested set open to better untested configurations."),
            },
            "scope_note": {
                "text": ("A tested lower frontier leaves untested prompts, tools, budgets, selectors and future model states open. "
                         "An evaluation supports claims about the declared system, protocol, sample and task distribution that produced its score."),
                "source_section": "What this does not settle",
            },
            "check": "With 1600 tasks and four configurations tested at alpha 0.05, what is the margin t, and what is the frontier for a best estimate of 0.74?",
            "answer": "t = sqrt(ln(4/0.05) / (2 x 1600)) = sqrt(4.382 / 3200) = 0.037, so LCF = 0.74 - 0.037 = 0.703.",
            "provenance": "Constructed example: four configuration success rates (0.60, 0.68, 0.72, 0.74) defined for this reader, not results for any real system.",
            "source_section": "A frontier is lower evidence, not a final ceiling",
            "source_anchor": "a-frontier-is-lower-evidence-not-a-final-ceiling",
            "controls": [
                {"key": "tasks", "label": "Tasks per configuration", "values": [100, 400, 1600], "default": 400},
                {"key": "tested", "label": "Configurations tested", "values": [2, 3, 4], "default": 4},
            ],
            "function": "frontier_picture",
        },
        {
            "id": "C24-D04",
            "title": "Same average, different reliability",
            "question": "If two banks of tasks both average 0.50 per run, do they give the same chance that repeated runs succeed, and what do the observed runs of one task give?",
            "equations": [EQ_ATLEAST, EQ_ALL],
            "symbols": (
                "The bank has two equally weighted tasks with single-run success probabilities p1 and p2. Runs are "
                "independent given the task. k is the number of runs. The chapter writes the single-task cases for one run "
                "probability 0.9 and three runs: success at least once, 1 - (1 - p)^k, and success on all runs, p^k. "
                "This demonstration applies each to each task, averages, and compares with applying it to the mean rate. "
                "The recorded bank is one task with 4 observed runs and 3 successes: a k-run subset contains only successes with fraction C(3,k) / C(4,k) and at least one success with fraction "
                "1 - C(1,k) / C(4,k), where C(n,k) counts the ways to choose k of n runs."
            ),
            "prediction": "With tasks at 0.20 and 0.80 and two runs, is the true chance that both runs succeed above or below 0.25, the square of the 0.50 mean?",
            "prediction_options": ["Above: 0.34", "Below: 0.16", "Equal to 0.25"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "(0.2^2 + 0.8^2) / 2 = (0.04 + 0.64) / 2 = 0.34, above 0.5^2 = 0.25, because the task is drawn once and repeated, so the easy task is weighted by its square. Choose the 0.20 and 0.80 bank with 2 runs to see it.",
                "incorrect": "Average the task-level chances: (0.04 + 0.64) / 2 = 0.34, which is above the square of the mean, 0.25. Choose the 0.20 and 0.80 bank with 2 runs to see it.",
            },
            "explanation": (
                "The task is drawn once and then repeated, so the runs share the task's difficulty. Averaging p^k over tasks "
                "weights the easy task heavily, giving more than the mean squared. Averaging 1 - (1 - p)^k over tasks gives "
                "less than the mean-rate formula. The gap grows with the spread between tasks and vanishes when the tasks "
                "are the same. For a recorded bank the subset fractions count the observed runs directly, and they differ from plugging the observed rate into the formulas."
            ),
            "application": (
                "When a report gives one average success rate and then claims reliability over repeated runs, ask for the "
                "task-level repeat results. The pooled average cannot answer a question about repetition."
            ),
            "assumptions": (
                "Two constructed tasks, equal weights, runs independent given the task and a frozen procedure. It fails when "
                "runs share a cached error, quota or evaluator fault, and it says nothing about a selector that must choose "
                "among the runs before the answer is known. The subset fractions are unbiased only under independent, identically distributed trials for that fixed task; otherwise they are descriptive fractions of the bank, "
                "and if fewer than k runs exist the subset metric is unavailable."
            ),
            "misconception": {
                "title": "Squaring the mean success rate gives repeated-run reliability",
                "text": ("The chapter says raising an average success rate to a power assumes away the variation that repetition is meant to expose: squaring the mean gives 0.25 where the task-first average gives 0.34, "
                         "and applying coverage to the mean gives 0.75 where the task-first average gives 0.66."),
            },
            "scope_note": {
                "text": ("The chapter leaves a model's maximum capability, a universal measure of reasoning and a complete cause of any benchmark gap open. "
                         "The bounded conclusion is that an evaluation supports claims about the declared system, protocol, sample and task distribution that produced its score."),
                "source_section": "What this does not settle",
            },
            "check": "Tasks at 0.10 and 0.90, three runs: what is the true chance that all three succeed, and the mean-rate value? And for a recorded bank of 3 successes in 4 runs, what fraction of two-run subsets contains only successes?",
            "answer": "(0.1^3 + 0.9^3)/2 = (0.001 + 0.729)/2 = 0.365, against 0.5^3 = 0.125. Recorded bank: C(3,2) / C(4,2) = 3 / 6 = 0.5 of the two-run subsets contain only successes, and all 6 contain at least one success.",
            "provenance": "Constructed example: the chapter's two-task construction (0.2 and 0.8, mean 0.5) with other spreads and run counts added for this reader, and the recorded bank of three successes and one failure from Mathematical Workbench E.5, part 3.",
            "source_section": "The same average can describe different reliability",
            "source_anchor": "the-same-average-can-describe-different-reliability",
            "controls": [
                {"key": "bank", "label": "Bank of tasks", "values": ["0.50", "0.20", "0.10", "recorded"], "default": "0.20",
                 "value_labels": ["Two tasks at 0.50 and 0.50", "Two tasks at 0.20 and 0.80 (the chapter's)", "Two tasks at 0.10 and 0.90",
                                  "Recorded runs: 3 successes in 4"]},
                {"key": "runs", "label": "Runs per task (subset size for the recorded bank)", "values": [2, 3], "default": 2},
            ],
            "function": "reliability_picture",
        },
    ],
}

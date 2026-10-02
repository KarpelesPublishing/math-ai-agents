"""Chapter 24 reader: How Much Capability Have We Extracted?

Four demonstrations. Demonstration 1 uses the book's own constructed two-bank
example (320 and 292 passes out of 400) and varies the sample size and the
matched-bank pass proportion. Demonstration 2 shows how the reported onset of a
capability moves with the threshold and with which family members were tested.
Demonstration 3 builds a simultaneous lower frontier with a union-bound
Hoeffding margin. Demonstration 4 shows that a mean success rate does not fix
repeated-run reliability. All numbers are constructed teaching values.
The laboratory's own chapter function is a paired, record-level computation, so
these four pictures compute their closed forms directly.
"""
import math
from decimal import ROUND_HALF_UP, Decimal

import numpy as np

from readerkit import PALETTE, fmt, label_point, new_figure

def half_up(x, digits=3):
    """Round half up on the decimal value, so two equal gaps never print as 0.023 and 0.022."""
    q = Decimal(1).scaleb(-digits)
    return str(Decimal(repr(round(x, 10))).quantize(q, rounding=ROUND_HALF_UP))


Z95 = 1.96  # large-sample two-sided 95 percent normal multiplier used in the chapter

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


# Demonstration 1: the matched difference and its sampling uncertainty

BENCH_RATE = 0.80


def wald_interval(p, n):
    half = Z95 * math.sqrt(p * (1 - p) / n)
    return p - half, p + half


def matched_banks_picture(tasks=400, matched_rate=0.73):
    n = int(tasks)
    passes_bench = round(BENCH_RATE * n)
    passes_match = round(float(matched_rate) * n)
    p_b, p_m = passes_bench / n, passes_match / n
    delta = p_b - p_m
    var = p_b * (1 - p_b) / n + p_m * (1 - p_m) / n
    se = math.sqrt(var)
    lo, hi = delta - Z95 * se, delta + Z95 * se
    excludes_zero = lo > 0 or hi < 0

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    bars = [("Benchmark", p_b, PALETTE["navy"], ""), ("Matched", p_m, PALETTE["terracotta"], "//")]
    for i, (name, p, color, hatch) in enumerate(bars):
        a, b = wald_interval(p, n)
        left.bar(i, p, width=0.55, color=color, hatch=hatch, edgecolor="white" if not hatch else PALETTE["ink"], linewidth=1)
        left.errorbar(i, p, yerr=[[p - a], [b - p]], color=PALETTE["ink"], capsize=6, linewidth=1.6)
        label_point(left, i, b, f"{fmt(p, 2)}", color=PALETTE["ink"], dx=0, dy=4, ha="center")
    left.set_xticks([0, 1], [f"Benchmark\n{passes_bench} of {n}", f"Matched\n{passes_match} of {n}"])
    left.set_xlim(-0.6, 1.6)
    left.set_ylim(0, 1.05)
    left.set_xlabel("Task bank (passes of independent tasks)")
    left.set_ylabel("Pass proportion, with its own 95% interval")
    left.set_title("Two independent banks", fontsize=11.5)

    right.axvline(0, color=PALETTE["grey"], linestyle="dashed", linewidth=1.6)
    right.errorbar([delta], [0], xerr=[[delta - lo], [hi - delta]], fmt="o", color=PALETTE["teal"], capsize=8,
                   markersize=9, linewidth=2.2)
    label_point(right, delta, 0, f"gap {fmt(delta, 3)}", color=PALETTE["teal"], dx=0, dy=12, ha="center").set_bbox(BOX)
    label_point(right, delta, 0, f"[{fmt(lo, 3)}, {fmt(hi, 3)}]", color=PALETTE["teal"], dx=0, dy=-14, ha="center",
                va="top").set_bbox(BOX)
    label_point(right, 0, 0.9, "no gap", color=PALETTE["grey"], dx=4, dy=0, ha="left", va="center")
    right.set_xlim(-0.2, 0.3)
    right.set_ylim(-1, 1)
    right.set_yticks([])
    right.set_xlabel("Benchmark minus matched pass proportion")
    right.set_ylabel("This comparison (one estimate)")
    right.set_title("Gap and 95% interval", fontsize=11.5)

    if excludes_zero:
        verdict = ("The interval excludes zero under this sampling model. It still does not say why the banks differ.")
        reading = "excludes zero"
    else:
        verdict = ("The interval includes zero, so with this many tasks the gap cannot be told apart from sampling noise. "
                   "That is a statement about precision, not a finding that the banks agree.")
        reading = "includes zero"
    metrics = {
        "Benchmark pass proportion": fmt(p_b, 2),
        "Matched pass proportion": fmt(p_m, 2),
        "Gap (Equation 24.2)": fmt(delta, 3),
        "Standard error of the gap": fmt(se, 5),
        "95% interval": f"[{fmt(lo, 5)}, {fmt(hi, 5)}]",
        "Interval and zero": reading,
    }
    interpretation = (
        f"Gap = {passes_bench}/{n} - {passes_match}/{n} = {fmt(p_b, 2)} - {fmt(p_m, 2)} = {fmt(delta, 2)}. "
        f"Standard error = sqrt({fmt(p_b, 2)} x {fmt(1 - p_b, 2)}/{n} + {fmt(p_m, 2)} x {fmt(1 - p_m, 2)}/{n}) = "
        f"sqrt({fmt(var, 6)}) = {fmt(se, 5)}. Interval = {fmt(delta, 2)} +/- 1.96 x {fmt(se, 5)} = "
        f"[{fmt(lo, 5)}, {fmt(hi, 5)}]. {verdict} Quadrupling the tasks per bank halves the standard error."
    )
    return fig, metrics, interpretation


# Demonstration 2: onset depends on the threshold and on which members were tested

MEMBERS = [1, 2, 3, 4, 5, 6, 7, 8]
G_HUNDREDTHS = [4, 9, 17, 30, 46, 58, 66, 71]  # constructed continuous scores, in hundredths


def onset_picture(threshold=0.5, tested="all"):
    z = round(float(threshold) * 100)
    members = MEMBERS if tested == "all" else [1, 3, 5, 7]
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
        else:
            full_onset = next((m for m in MEMBERS if scores[m] >= z), None)
            if full_onset == onset:
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
        verdict = ("The set whose smallest element would be the onset is empty, so Equation (24.3) has no value among the "
                   "tested members. That means untested, not never: member 8 was skipped and does reach 0.71.")
        if tested == "all":
            verdict = "The set whose smallest element would be the onset is empty."
        shown = undefined_text(z)
    interpretation = calc + verdict
    metrics = {
        "Threshold": fmt(z / 100, 2),
        "Members tested": ", ".join(str(m) for m in members),
        "Onset": shown,
        "Highest tested score": fmt(max(scores[m] for m in members) / 100, 2),
    }
    return fig, metrics, interpretation


def undefined_text(z):
    return f"undefined (no tested member reaches {fmt(z / 100, 2)})"


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
    return fig, metrics, interpretation


# Demonstration 4: the same average, different repeated-run reliability

PAIRS = {"0.50": (0.5, 0.5), "0.35": (0.35, 0.65), "0.20": (0.2, 0.8), "0.10": (0.1, 0.9)}


def reliability_picture(spread="0.20", runs=2):
    lo_p, hi_p = PAIRS[spread]
    k = int(runs)
    mean = (lo_p + hi_p) / 2
    true_all = (lo_p ** k + hi_p ** k) / 2
    naive_all = mean ** k
    true_any = ((1 - (1 - lo_p) ** k) + (1 - (1 - hi_p) ** k)) / 2
    naive_any = 1 - (1 - mean) ** k

    fig, ax = new_figure(height=4.3)
    xs = [0, 1, 2.8, 3.8]
    values = [true_all, naive_all, true_any, naive_any]
    colors = [PALETTE["navy"], PALETTE["navy"], PALETTE["teal"], PALETTE["teal"]]
    hatches = ["", "//", "", "//"]
    for x, v, c, h in zip(xs, values, colors, hatches):
        ax.bar(x, v, width=0.7, color="white" if h else c, edgecolor=c if h else "white", hatch=h, linewidth=1.4)
        label_point(ax, x, v, fmt(v, 3), color=PALETTE["ink"], dx=0, dy=4, ha="center")
    ax.set_xticks(xs, ["Average\nof tasks", "Mean rate\nformula", "Average\nof tasks", "Mean rate\nformula"])
    ax.set_xlim(-0.6, 4.4)
    ax.set_ylim(0, 1.15)
    ax.grid(axis="x", alpha=0)
    label_point(ax, 0.5, 1.07, f"all {k} runs succeed", color=PALETTE["navy"], dx=0, dy=0, ha="center", va="center")
    label_point(ax, 3.3, 1.07, "at least one succeeds", color=PALETTE["teal"], dx=0, dy=0, ha="center", va="center")
    ax.set_xlabel("How the number is computed (hatched = uses only the mean single-run rate)")
    ax.set_ylabel("Probability")
    ax.set_title(f"Two tasks at {fmt(lo_p, 2)} and {fmt(hi_p, 2)}; mean single-run rate {fmt(mean, 2)}", fontsize=11.5)

    gap_all = true_all - naive_all
    gap_any = naive_any - true_any
    if abs(gap_all) < 1e-9:
        verdict = ("Both tasks have the same success rate, so there is no spread between tasks and the mean-rate formulas "
                   "agree with the task-by-task averages. The two methods only differ when tasks differ.")
    else:
        power = "Squaring the mean rate" if k == 2 else f"Raising the mean rate to the power {k}"
        verdict = (f"{power} misses by {half_up(gap_all)} for all-runs success (it understates) and the "
                   f"coverage-style formula misses by {half_up(gap_any)} for at-least-one success (it overstates). "
                   "The task is drawn once and then repeated, which is the dependence the mean rate hides.")
    metrics = {
        "Mean single-run success": fmt(mean, 2),
        "All runs, average of tasks": fmt(true_all, 3),
        "All runs, mean-rate formula": fmt(naive_all, 3),
        "At least one, average of tasks": fmt(true_any, 3),
        "At least one, mean-rate formula": fmt(naive_any, 3),
    }
    interpretation = (
        f"All {k} runs: ({fmt(lo_p, 2)}^{k} + {fmt(hi_p, 2)}^{k}) / 2 = ({fmt(lo_p ** k, 4)} + {fmt(hi_p ** k, 4)}) / 2 = "
        f"{fmt(true_all, 3)}, while {fmt(mean, 2)}^{k} = {fmt(naive_all, 3)}. At least one: "
        f"((1 - {fmt(1 - lo_p, 2)}^{k}) + (1 - {fmt(1 - hi_p, 2)}^{k})) / 2 = "
        f"({fmt(1 - (1 - lo_p) ** k, 4)} + {fmt(1 - (1 - hi_p) ** k, 4)}) / 2 = {fmt(true_any, 3)}, while "
        f"1 - (1 - {fmt(mean, 2)})^{k} = {fmt(naive_any, 3)}. {verdict}"
    )
    return fig, metrics, interpretation


CHAPTER = {
    "number": 24,
    "title": "How Much Capability Have We Extracted?",
    "subtitle": "A score describes a system, a task sample and a measurement procedure together, and it needs its boundary to be read.",
    "summary": (
        "These four demonstrations follow the chapter's rule that a number travels with its contract. They separate a score "
        "gap from its sampling uncertainty, show how a reported onset depends on a threshold, price the search behind a best "
        "tested configuration, and show why a mean success rate does not fix repeated-run reliability. Every number is a "
        "constructed teaching value."
    ),
    "demos": [
        {
            "id": "C24-D01",
            "title": "A score gap and its uncertainty",
            "question": "A benchmark and a matched bank give different pass proportions. How large must the sample be before the gap means more than sampling noise?",
            "equations": [EQ_MATCH],
            "symbols": (
                "Delta_match is the benchmark pass proportion minus the matched-bank pass proportion for the same fixed model. "
                "Each bank holds the chosen number of independent tasks (the sample size n). The standard error of the gap is "
                "the square root of p1(1 - p1)/n + p2(1 - p2)/n, where p1 and p2 are the two pass proportions. The 95% "
                "interval is the gap plus or minus 1.96 standard errors. In Equation (24.2), the hat on U marks a pass proportion "
                "estimated from a bank (the average of its scored outcomes), V_bench and V_match are the benchmark and matched "
                "banks, and theta is the fixed model, so p1 is U-hat for the benchmark bank and p2 is U-hat for the matched bank."
            ),
            "prediction": "Keep 0.73 on the matched bank and use 100 tasks per bank instead of 400. Will the interval for the gap still exclude zero?",
            "explanation": (
                "Equation (24.2) is a subtraction of two estimated scores. Each score carries sampling noise that shrinks as the "
                "number of tasks grows, and the noise of the two independent banks adds. With the default 0.73 on the matched bank, the same "
                "0.07 gap has an interval that excludes zero at 400 tasks and includes zero at 100. Neither case says what caused the gap."
            ),
            "application": (
                "Before reporting that a model scores lower on a fresh matched bank, report the number of tasks in each bank and "
                "the interval, so a reader can tell a real discrepancy from a thin sample."
            ),
            "assumptions": (
                "Two independent samples with adequately populated pass and fail counts, so the normal approximation is fair. "
                "It does not cover choosing the largest gap after inspecting many models, and it cannot separate contamination "
                "from an unmatched task feature. A paired design would need joint outcomes."
            ),
            "check": "Benchmark 0.80 and matched 0.73 on 1600 tasks each: what is the standard error of the gap?",
            "answer": (
                "sqrt(0.80 x 0.20/1600 + 0.73 x 0.27/1600) = sqrt(0.0001 + 0.000123) = sqrt(0.000223) = 0.0149, "
                "half the 400-task value of 0.0299."
            ),
            "provenance": "Constructed example: the book's teaching counts (320 and 292 passes out of 400, not GSM1k measurements), with the sample size and matched proportion varied.",
            "source_section": "The matched question is not the same question twice",
            "source_anchor": "the-matched-question-is-not-the-same-question-twice",
            "controls": [
                {"key": "tasks", "label": "Independent tasks per bank", "values": [100, 400, 1600], "default": 400},
                {"key": "matched_rate", "label": "Pass proportion on the matched bank", "values": [0.73, 0.78], "default": 0.73},
            ],
            "function": "matched_banks_picture",
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
            "prediction": "At threshold 0.70, which family member is the onset when all eight are tested, and what happens when only the odd members are tested?",
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
            "check": "With all eight members tested, what is the onset at threshold 0.60?",
            "answer": "g(6) = 0.58 is below 0.60 and g(7) = 0.66 is at or above it, with margin 0.66 - 0.60 = 0.06, so the onset is m = 7.",
            "provenance": "Constructed example: eight family scores defined for this reader (0.04, 0.09, 0.17, 0.30, 0.46, 0.58, 0.66, 0.71), not a measured scale profile.",
            "source_section": "Scale profiles and extraction profiles are different maps",
            "source_anchor": "scale-profiles-and-extraction-profiles-are-different-maps",
            "controls": [
                {"key": "threshold", "label": "Threshold zeta", "values": [0.3, 0.5, 0.6, 0.7], "default": 0.5},
                {"key": "tested", "label": "Family members tested", "values": ["all", "odd"], "default": "all",
                 "value_labels": ["All eight members", "Only members 1, 3, 5, 7"]},
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
                "per configuration. In Equation (24.4), V is the declared evaluation contract (task bank, scoring rule and budget), "
                "S_xi is the set of components enabled in configuration xi, and Lower^sim is instantiated here as the observed rate minus "
                "the margin t."
            ),
            "prediction": "Keep 400 tasks but test only the first two configurations. Does the margin t shrink or grow, and does the best configuration change?",
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
            "check": "With 1600 tasks and four configurations tested at alpha 0.05, what is the margin t, and what is the frontier for a best estimate of 0.74?",
            "answer": "t = sqrt(ln(4/0.05) / (2 x 1600)) = sqrt(4.382 / 3200) = 0.037, so LCF = 0.74 - 0.037 = 0.703.",
            "provenance": "Constructed example: four configuration success rates (0.60, 0.68, 0.72, 0.74) defined for this reader, not results for any real system.",
            "source_section": "A frontier is lower evidence, not a final ceiling",
            "source_anchor": "a-frontier-is-lower-evidence-not-a-final-ceiling",
            "controls": [
                {"key": "tasks", "label": "Tasks per configuration", "values": [100, 400, 1600], "default": 400},
                {"key": "tested", "label": "Configurations tested", "values": [2, 4], "default": 4},
            ],
            "function": "frontier_picture",
        },
        {
            "id": "C24-D04",
            "title": "Same average, different reliability",
            "question": "If two banks of tasks both average 0.50 per run, do they give the same chance that repeated runs succeed?",
            "equations": [EQ_ATLEAST, EQ_ALL],
            "symbols": (
                "The bank has two equally weighted tasks with single-run success probabilities p1 and p2. Runs are "
                "independent given the task. k is the number of runs. The chapter writes the single-task cases for one run "
                "probability 0.9 and three runs: success at least once, 1 - (1 - p)^k, and success on all runs, p^k. "
                "This demonstration applies each to each task, averages, and compares with applying it to the mean rate."
            ),
            "prediction": "With tasks at 0.20 and 0.80 and two runs, is the true chance that both runs succeed above or below 0.25, the square of the 0.50 mean?",
            "explanation": (
                "The task is drawn once and then repeated, so the runs share the task's difficulty. Averaging p^k over tasks "
                "weights the easy task heavily, giving more than the mean squared. Averaging 1 - (1 - p)^k over tasks gives "
                "less than the mean-rate formula. The gap grows with the spread between tasks and vanishes when the tasks "
                "are the same."
            ),
            "application": (
                "When a report gives one average success rate and then claims reliability over repeated runs, ask for the "
                "task-level repeat results. The pooled average cannot answer a question about repetition."
            ),
            "assumptions": (
                "Two constructed tasks, equal weights, runs independent given the task and a frozen procedure. It fails when "
                "runs share a cached error, quota or evaluator fault, and it says nothing about a selector that must choose "
                "among the runs before the answer is known."
            ),
            "check": "Tasks at 0.10 and 0.90, three runs: what is the true chance that all three succeed, and the mean-rate value?",
            "answer": "(0.1^3 + 0.9^3)/2 = (0.001 + 0.729)/2 = 0.365, against 0.5^3 = 0.125.",
            "provenance": "Constructed example: the chapter's two-task construction (0.2 and 0.8, mean 0.5) with other spreads and run counts added for this reader.",
            "source_section": "The same average can describe different reliability",
            "source_anchor": "the-same-average-can-describe-different-reliability",
            "controls": [
                {"key": "spread", "label": "Two task success rates", "values": ["0.50", "0.35", "0.20", "0.10"], "default": "0.20",
                 "value_labels": ["0.50 and 0.50", "0.35 and 0.65", "0.20 and 0.80", "0.10 and 0.90"]},
                {"key": "runs", "label": "Runs per task", "values": [2, 3], "default": 2},
            ],
            "function": "reliability_picture",
        },
    ],
}

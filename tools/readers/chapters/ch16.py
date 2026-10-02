"""Chapter 16 reader: Thought as Search.

Four demonstrations built on Equations (16.1) to (16.5). Demonstration 2 calls
the laboratory's own allocation function (math_ai_agents.chapters.ch16.evaluate)
so the reader, the notebook and the chapter skill agree. Demonstrations 1, 3 and
4 compute the chapter's closed forms directly; Demonstration 3 uses the book's
own sixty-unit construction and Demonstration 4 the book's three constructed
procedures. Every number is a constructed teaching value.
"""
import math

import numpy as np

from math_ai_agents.chapters.ch16 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure

EQ_COV = r"\operatorname{Cov}(k) = 1 - (1-p)^{k}"
EQ_BLIND = r"\operatorname{Sel}(k) = \mathrm{E}\!\left[\frac{m}{k}\right] = p"
EQ_SEL = r"\operatorname{Sel}(k) = \operatorname{Cov}(k)\cdot \pi(k) + \big(1-\operatorname{Cov}(k)\big)\cdot 0"
EQ_GAIN = r"\operatorname{Cov}(k+1) - \operatorname{Cov}(k) = p\,(1-p)^{k}"
EQ_COST = (r"\widehat c_{\mathrm{success}} = \frac{\sum_{i=1}^{N}c_i}"
           r"{\sum_{i=1}^{N}\mathbf 1\{\text{authorized confirmed completion in run }i\}}")

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


def g(x):
    """Four decimals, or scientific notation when that would print as zero."""
    return fmt(x, 4) if x >= 1e-4 else f"{x:.1e}"


def coverage(p, k):
    return 1.0 - (1.0 - p) ** k


# Demonstration 1: coverage against a blind selector

def coverage_picture(p=0.2, k=10):
    p = float(p)
    k = int(k)
    cov = coverage(p, k)
    gain = p * (1 - p) ** k
    ks = np.arange(1, 101)
    fig, (left, right) = new_figure(ncols=2, height=4.3)

    left.plot(ks, coverage(p, ks), color=PALETTE["teal"], linewidth=2)
    left.plot([1, 100], [p, p], color=PALETTE["terracotta"], linestyle="dashed", linewidth=2)
    left.plot([k], [cov], "o", color=PALETTE["teal"], markersize=9)
    left.plot([k], [p], "s", color=PALETTE["terracotta"], markersize=8)
    left.vlines(k, p, cov, color=PALETTE["grey"], linestyle=":", linewidth=1.5)
    label_point(left, 100, p, "blind selection = p", color=PALETTE["terracotta"], dx=-4, dy=7, ha="right", va="bottom")
    side_right = k > 50
    label_point(left, k, cov, f"coverage {fmt(cov, 2)} at k = {k}", color=PALETTE["teal"], dx=-8 if side_right else 8,
                dy=-34 if side_right else -9, ha="right" if side_right else "left", va="top").set_bbox(BOX)
    left.set_xlim(0, 104)
    left.set_ylim(0, 1.08)
    left.set_xlabel("Samples drawn, k")
    left.set_ylabel("Chance the answer is correct")
    left.set_title(f"Candidate present vs candidate delivered (p = {fmt(p, 2)})", fontsize=11.5)

    gains = p * (1 - p) ** (ks - 1)
    right.semilogy(ks, gains, color=PALETTE["navy"], linewidth=2)
    if gain >= 1e-6:
        right.plot([k + 1], [gain], "o", color=PALETTE["navy"], markersize=9)
        # beyond sample 40 the curve runs down to the point from the upper left, so the label goes below it
        label_point(right, k + 1, gain, f"sample {k + 1} adds {g(gain)}", color=PALETTE["ink"],
                    dx=-8 if k + 1 > 40 else 8, dy=-12 if k + 1 > 40 else 8, ha="right" if k + 1 > 40 else "left",
                    va="top" if k + 1 > 40 else "bottom").set_bbox(BOX)
    else:
        # the value is far below the axis floor: say so at the floor, in plain decimals, with an arrow down
        right.annotate(f"sample {k + 1} adds about\n{gain:.12f},\nbelow the axis floor", (k + 1, 1e-6), xytext=(100, 5e-6),
                       textcoords="data", ha="right", va="bottom", color=PALETTE["ink"], fontsize=10.5,
                       arrowprops={"arrowstyle": "->", "color": PALETTE["ink"], "linewidth": 1.2})
    right.set_xlim(0, 104)
    right.set_ylim(1e-6, 1)
    right.set_xlabel("Sample number")
    right.set_ylabel("Added coverage from that sample (log scale)")
    right.set_title("Each extra sample buys less", fontsize=11.5)

    metrics = {
        "Coverage Cov(k)": fmt(cov, 4),
        "Blind selection Sel(k)": fmt(p, 2),
        "Gap a selector could close": fmt(cov - p, 4),
        f"Gain from sample {k + 1}": g(gain),
    }
    miss = (1 - p) ** k
    interpretation = (
        f"Cov({k}) = 1 - (1 - {fmt(p, 2)})^{k} = 1 - {g(miss)} = {fmt(cov, 4)}. A blind selector returns "
        f"one sample at random, so it delivers p = {fmt(p, 2)} however large k is. The gap a selector could close is "
        f"{fmt(cov, 4)} - {fmt(p, 2)} = {fmt(cov - p, 4)}. The next sample adds {fmt(p, 2)} x (1 - {fmt(p, 2)})^{k} = "
        f"{fmt(p, 2)} x {g(miss)} = {g(gain)}."
    )
    if gain >= 1e-4:
        interpretation += (f" That equals Cov({k + 1}) - Cov({k}) = {fmt(coverage(p, k + 1), 4)} - {fmt(cov, 4)} = "
                           f"{fmt(coverage(p, k + 1) - cov, 4)}.")
    return fig, metrics, interpretation


# Demonstration 2: the selector's measured success, computed by the laboratory

COUNTS = list(range(1, 21))
P_LAB = 0.4  # the notebook's default candidate success
MARK_N = 5   # the notebook's worked case


def lab_rows(selector, shared):
    # Under one shared failure a bank holds a correct sample only when every sample is correct, so
    # the selector's top pick is correct with chance 1 whatever its quality: the laboratory is
    # called with a perfect selector for that state and the selector control is not used.
    data = {
        "candidate_success": P_LAB, "selector_accuracy": 1.0 if shared else float(selector),
        "sample_cost": 1, "sample_latency": 1, "selector_cost": 1, "selector_latency": 1,
        "deadline": 1000, "budget": 1000, "shared_error": bool(shared), "sample_counts": COUNTS,
    }
    return evaluate(data)["tables"]


def selector_picture(selector=0.9, dependence="independent"):
    shared = dependence == "shared"
    rows = lab_rows(selector, shared)
    n = np.array([r["samples"] for r in rows])
    cov = np.array([r["coverage"] for r in rows])
    sel = np.array([r["selected_success"] for r in rows])
    row = next(r for r in rows if r["samples"] == MARK_N)
    fig, ax = new_figure(height=4.3)
    ax.plot(n, cov, color=PALETTE["teal"], linewidth=2.2)
    ax.plot(n, sel, color=PALETTE["navy"], linewidth=2.2, marker="o", markersize=4)
    ax.plot([1, 20], [P_LAB, P_LAB], color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.8)
    ax.plot([MARK_N], [row["selected_success"]], "D", color=PALETTE["navy"], markersize=9)
    ax.plot([MARK_N], [row["coverage"]], "o", color=PALETTE["teal"], markersize=9)
    groups = []
    for key, value, color, text in (("cov", cov[-1], PALETTE["teal"], "coverage"),
                                    ("sel", sel[-1], PALETTE["navy"], "selection"),
                                    ("blind", P_LAB, PALETTE["terracotta"], "blind selection")):
        for grp in groups:
            if math.isclose(grp["y"], value, abs_tol=1e-9):
                grp["texts"].append(text)
                break
        else:
            groups.append({"y": value, "color": color, "texts": [text]})
    groups.sort(key=lambda grp: -grp["y"])
    for i, grp in enumerate(groups):
        above_gap = groups[i - 1]["y"] - grp["y"] if i > 0 else 9.0
        below = grp["y"] > 0.93
        if i + 1 < len(groups) and grp["y"] - groups[i + 1]["y"] < 0.12:
            below = False
        elif i > 0 and above_gap < 0.12:
            below = True
        label_point(ax, 20, grp["y"], " = ".join(grp["texts"]), color=grp["color"], dx=-4,
                    dy=-8 if below else 8, ha="right", va="top" if below else "bottom").set_bbox(BOX)
    ax.axvline(MARK_N, color=PALETTE["grey"], linestyle=":", linewidth=1.3)
    label_point(ax, MARK_N, 0.02, f"k = {MARK_N}", color=PALETTE["ink"], dx=4, dy=0, ha="left", va="bottom")
    ax.set_xticks([1, 5, 10, 15, 20])
    ax.set_xlim(0.5, 20.5)
    ax.set_ylim(0, 1.08)
    ax.set_xlabel("Samples drawn, k (one sample skips the selector)")
    ax.set_ylabel("Chance of a correct delivered answer")
    kind = "samples share one failure" if shared else "samples are independent"
    if shared:
        ax.set_title(f"p = {fmt(P_LAB, 2)}; {kind} (selector setting not used)", fontsize=11.5)
    else:
        ax.set_title(f"p = {fmt(P_LAB, 2)}, selector success {fmt(selector, 2)}; {kind}", fontsize=11.5)

    metrics = {
        f"Coverage at k = {MARK_N}": fmt(row["coverage"], 4),
        f"Selected success at k = {MARK_N}": fmt(row["selected_success"], 4),
        "Blind selection": fmt(P_LAB, 2),
        "Selected minus blind": fmt(row["selected_success"] - P_LAB, 4),
    }
    q = float(selector)
    if shared:
        calc = (f"Samples share one failure, so a correct answer is present with chance p whatever k is: Cov({MARK_N}) = "
                f"{fmt(P_LAB, 2)}. A bank that holds a correct sample holds only correct samples, so any pick from it is "
                f"correct and the selector's success is 1 whatever its quality. Sel({MARK_N}) = {fmt(P_LAB, 2)} x 1 + "
                f"(1 - {fmt(P_LAB, 2)}) x 0 = {fmt(row['selected_success'], 4)}. The selector setting ({fmt(q, 2)}) is not used.")
        meaning = (f"Extra samples do not raise coverage here and a selector adds nothing, so one sample ({fmt(P_LAB, 2)}) "
                   "is exactly as good as five. The independence assumed in Equation (16.1) is what is missing.")
    else:
        calc = (f"Cov({MARK_N}) = 1 - (1 - {fmt(P_LAB, 2)})^{MARK_N} = 1 - {fmt((1 - P_LAB) ** MARK_N, 5)} = "
                f"{fmt(row['coverage'], 5)}. Sel({MARK_N}) = {fmt(row['coverage'], 5)} x {fmt(q, 2)} + "
                f"(1 - {fmt(row['coverage'], 5)}) x 0 = {fmt(row['selected_success'], 4)}.")
        if row["selected_success"] > P_LAB + 1e-9:
            meaning = (f"Five samples with this selector beat the blind {fmt(P_LAB, 2)} by "
                       f"{fmt(row['selected_success'] - P_LAB, 4)}. The gap needs both: samples to put a correct answer in the "
                       "bank, and a selector to find it.")
        else:
            meaning = (f"Five samples with this selector deliver {fmt(row['selected_success'], 4)}, no better than the blind "
                       f"{fmt(P_LAB, 2)}. Coverage is high but the selector fails to turn it into delivery.")
    dips = [r for r in rows if r["samples"] > 1 and r["selected_success"] < P_LAB - 1e-9]
    if dips and not shared:
        first = dips[0]
        meaning += (f" For small banks the selector can cost more than it earns: at k = {first['samples']} selection is "
                    f"Cov({first['samples']}) x {fmt(q, 2)} = {fmt(first['coverage'], 2)} x {fmt(q, 2)} = "
                    f"{fmt(first['selected_success'], 2)}, below the blind {fmt(P_LAB, 2)}.")
    interpretation = f"{calc} {meaning}"
    return fig, metrics, interpretation


# Demonstration 3: the book's sixty-unit budget

PI_CASES = {"book": (0.73, 0.785), "strong": (0.95, 0.95), "weak": (0.50, 0.50), "worse": (0.15, 0.15)}
P_SHORT = 0.20


def allocation_picture(selector="book", long_p=0.35):
    long_p = float(long_p)
    pi3, pi4 = PI_CASES[selector]
    cov3 = coverage(P_SHORT, 48)
    cov4 = coverage(long_p, 12)
    cov1 = coverage(long_p, 15)
    cov2 = coverage(P_SHORT, 60)
    units = [15 * 4, 60 * 1, 48 * 1 + 48 * 0.25, 12 * 4 + 12 * 0.25]  # 60, 60, 60, 51 of the 60 available
    rows = [
        ("1. All on length", "15 long samples, no selector, 60 units", long_p, cov1, True),
        ("2. All on volume", "60 short samples, no selector, 60 units", P_SHORT, cov2, True),
        ("3. Volume + selector", "48 short samples + checks, 60 units", cov3 * pi3, cov3, False),
        ("4. Length + selector", "12 long samples + checks, 51 units", cov4 * pi4, cov4, False),
    ]
    fig, ax = new_figure(height=4.5)
    ys = np.arange(4)[::-1]
    best = max(r[2] for r in rows)
    for y, (name, detail, delivered, cov, blind) in zip(ys, rows):
        color = PALETTE["teal"] if math.isclose(delivered, best, abs_tol=1e-9) else "#8fa3b8"
        ax.barh(y, delivered, height=0.4, color=color, edgecolor=PALETTE["ink"], linewidth=1.0,
                hatch="///" if blind else None)
        ax.plot([cov], [y], "D", color="white", markeredgecolor=PALETTE["ink"], markeredgewidth=1.6, markersize=9)
        ax.plot([delivered, cov], [y, y], color=PALETTE["grey"], linestyle=":", linewidth=1.3, zorder=0)
        tag = " (highest)" if math.isclose(delivered, best, abs_tol=1e-9) else ""
        ax.text(0.01, y + 0.27, f"delivered {fmt(delivered, 2)}{tag}, coverage {fmt(cov, 3)}", va="bottom", ha="left",
                fontsize=10.5, color=PALETTE["ink"])
    ax.set_yticks(ys, [f"{r[0]}\n{fmt(u, 0)} of 60 units used" for r, u in zip(rows, units)])
    ax.set_xlim(0, 1.05)
    ax.set_ylim(-0.5, 3.75)
    ax.set_xlabel("Chance of a correct delivered answer (bar)\ndiamond marks coverage; hatched = blind selection")
    ax.set_ylabel("Allocation of 60 units")
    ax.set_title(f"Long reasoning p = {fmt(long_p, 2)}, short p = 0.20\nselector success {pi3:g} (3) and {pi4:g} (4)",
                 fontsize=11.5)
    ax.grid(axis="y", alpha=0)

    gap_blind = max(rows[0][2], rows[1][2])
    gap_sel = min(rows[2][2], rows[3][2])
    metrics = {rows[i][0][3:]: fmt(rows[i][2], 3) for i in range(4)}
    metrics["Best allocation"] = " and ".join(r[0][3:] for r in rows if math.isclose(r[2], best, abs_tol=1e-9))
    calc = (f"Allocation 1: blind, so Sel = p = {fmt(long_p, 2)}. Allocation 2: Sel = p = 0.20. "
            f"Allocation 3: Cov(48) = 1 - 0.8^48 = {fmt(cov3, 5)}, so Sel = {fmt(cov3, 5)} x {pi3:g} = {fmt(cov3 * pi3, 3)}. "
            f"Allocation 4: Cov(12) = 1 - {fmt(1 - long_p, 2)}^12 = {fmt(cov4, 4)}, so Sel = {fmt(cov4, 4)} x {pi4:g} = "
            f"{fmt(cov4 * pi4, 3)}. Spending: allocation 4 uses 12 x 4 + 12 x 0.25 = {fmt(units[3], 0)} units and leaves "
            f"{fmt(60 - units[3], 0)} unspent; the other three use all 60.")
    if gap_sel > gap_blind + 1e-9:
        verdict = (f"Both selector allocations beat both blind ones: the worse selector allocation ({fmt(gap_sel, 3)}) is above the "
                   f"better blind one ({fmt(gap_blind, 3)}).")
    elif cov3 * pi3 < P_SHORT - 1e-9 or cov4 * pi4 < long_p - 1e-9:
        below = (cov3 * pi3 < P_SHORT - 1e-9) + (cov4 * pi4 < long_p - 1e-9)
        which = ("Both selector allocations fall below their blind counterparts" if below == 2
                 else "One selector allocation falls below its blind counterpart")
        verdict = ("A selector that ranks correct answers below wrong ones does worse than picking at random. "
                   f"{which}, so paying for the check is a loss.")
    else:
        verdict = ("The selector allocations no longer clear both blind ones by much, so the choice between "
                   "length and volume matters about as much as having a selector.")
    interpretation = f"{calc} {verdict}"
    return fig, metrics, interpretation


# Demonstration 4: cost per success under a deadline

PROCEDURES = [
    # name, cost per attempted task, completion rate, response seconds
    ("A", 1.0, 0.60, 1.0),
    ("B", 1.5, 0.80, 2.0),
    ("C", 2.0, 0.85, 5.0),
]
ATTEMPTS = 100
FAILURE_LOSS = 20.0


def cost_picture(deadline=10, required=0.75):
    deadline = float(deadline)
    required = float(required)
    names = [r[0] for r in PROCEDURES]
    per_success = {}
    ok = {}
    combined = {}
    for name, cost, rate, seconds in PROCEDURES:
        total = ATTEMPTS * cost
        successes = ATTEMPTS * rate
        per_success[name] = total / successes
        ok[name] = rate >= required - 1e-12 and seconds <= deadline + 1e-12
        combined[name] = cost + (1 - rate) * FAILURE_LOSS
    feasible = [n for n in names if ok[n]]
    cheapest = min(feasible, key=lambda n: per_success[n]) if feasible else None
    lowest_loss = min(feasible, key=lambda n: combined[n]) if feasible else None
    overall = min(names, key=lambda n: per_success[n])

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    top = max(per_success.values())
    for i, name in enumerate(names):
        left.bar(i, per_success[name], width=0.55, color=PALETTE["teal"] if ok[name] else "white",
                 edgecolor=PALETTE["ink"] if ok[name] else PALETTE["grey"], hatch=None if ok[name] else "///", linewidth=1.2)
        left.text(i, per_success[name] + 0.05, fmt(per_success[name], 2), ha="center", va="bottom", fontsize=10.5,
                  color=PALETTE["ink"])
        left.text(i, 0.08, "feasible" if ok[name] else "not feasible", ha="center", va="bottom", fontsize=10.5,
                  color="white" if ok[name] else PALETTE["ink"],
                  bbox=None if ok[name] else {"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.9})
    left.set_xticks(range(3), [f"Procedure {n}" for n in names])
    left.set_ylim(0, top + 0.5)
    left.set_xlabel("Procedure (hatched = misses a requirement)")
    left.set_ylabel("Cost per authorized success")
    left.set_title("Equation (16.5) for each procedure", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    right.fill_between([0, deadline], required, 1.0, color="#dcebea", alpha=0.9, zorder=0)
    right.axvline(deadline, color=PALETTE["grey"], linestyle="dashed", linewidth=1.5)
    right.axhline(required, color=PALETTE["grey"], linestyle="dashed", linewidth=1.5)
    for name, cost, rate, seconds in PROCEDURES:
        right.plot([seconds], [rate], "o" if ok[name] else "X", color=PALETTE["teal"] if ok[name] else PALETTE["terracotta"],
                   markersize=10, markeredgecolor=PALETTE["ink"])
        label_point(right, seconds, rate, name, color=PALETTE["ink"], dx=10, dy=0, ha="left", va="center").set_bbox(BOX)
    label_point(right, deadline, 0.45, f"deadline {fmt(deadline, 0)} s", color=PALETTE["ink"], dx=-4, dy=0, ha="right",
                va="center").set_bbox(BOX)
    label_point(right, 0.1, required, f"need {fmt(required, 2)}", color=PALETTE["ink"], dx=0, dy=5, ha="left").set_bbox(BOX)
    right.set_xlim(0, 11)
    right.set_ylim(0.4, 1.0)
    right.set_xlabel("Response time (seconds)")
    right.set_ylabel("Completion rate (shaded: feasible)")
    right.set_title("Feasible region", fontsize=11.5)

    none = "undefined (no procedure is feasible)"
    metrics = {
        "Cost per success A": fmt(per_success["A"], 2),
        "Cost per success B": fmt(per_success["B"], 2),
        "Cost per success C": fmt(per_success["C"], 2),
        "Feasible procedures": ", ".join(feasible) if feasible else "none",
        "Cheapest per success overall": overall,
        "Cheapest per success among feasible": cheapest if cheapest else none,
        "Lowest cost plus failure loss (20 per failure)": lowest_loss if lowest_loss else none,
    }
    calc = (f"Over {ATTEMPTS} attempts, Equation (16.5) gives A: 100 x 1 / (100 x 0.60) = 100 / 60 = {fmt(per_success['A'], 4)}; "
            f"B: 150 / 80 = {fmt(per_success['B'], 4)}; C: 200 / 85 = {fmt(per_success['C'], 4)}.")
    if feasible:
        extra = (f" With a {fmt(deadline, 0)} second deadline and at least {fmt(required, 2)} completion, the feasible set is "
                 f"{', '.join(feasible)}; the lowest cost per success among them is {cheapest}"
                 f"{'' if overall == cheapest else f' (the lowest of all three is {overall}, which is not feasible)'}. Adding a loss of 20 per failure, "
                 f"cost plus failure loss = cost + (1 - rate) x 20 gives A: 1 + 0.40 x 20 = {fmt(combined['A'], 1)}, "
                 f"B: 1.5 + 0.20 x 20 = {fmt(combined['B'], 1)}, C: 2 + 0.15 x 20 = {fmt(combined['C'], 1)}, "
                 f"so {lowest_loss} is lowest among the feasible.")
    else:
        extra = (f" With a {fmt(deadline, 0)} second deadline and at least {fmt(required, 2)} completion, no procedure "
                 "qualifies: the ones fast enough complete too few tasks and the ones that complete enough are too slow, "
                 "so there is no cheapest feasible procedure and the ratio alone cannot choose one.")
    interpretation = calc + extra
    return fig, metrics, interpretation


CHAPTER = {
    "number": 16,
    "title": "Thought as Search",
    "subtitle": "A correct answer can sit in the bank of candidates and still fail to reach the user; the selector decides.",
    "summary": (
        "These four demonstrations separate three things the chapter keeps apart: whether a correct candidate exists "
        "(coverage), whether the system returns it (selection), and what each costs. They follow the chapter's order: "
        "what sampling buys, what a selector must earn, how a fixed budget is split, and what a completed task costs."
    ),
    "demos": [
        {
            "id": "C16-D01",
            "title": "Sampling fills the bank, but a blind pick ignores it",
            "question": "How many samples does it take to have a correct answer somewhere, and what does a random pick from them deliver?",
            "equations": [EQ_COV, EQ_BLIND, EQ_GAIN],
            "symbols": (
                "p is the chance that one sample is correct. k is the number of samples drawn, assumed independent. "
                "Cov(k) is coverage: the chance at least one of the k samples is correct. Sel(k) is the chance the returned "
                "sample is correct; with no way to rank, the system returns one at random. m is the number of correct "
                "samples among the k. The right panel shows the extra coverage bought by sample number k + 1."
            ),
            "prediction": "At p = 0.05, will ten samples put a correct answer in the bank more than half the time? What will a random pick from those ten deliver?",
            "explanation": (
                "Coverage is one minus the chance that every sample is wrong, so it climbs fastest over the first few "
                "samples, faster for larger p, and flattens as k grows. The blind pick returns a correct sample with probability p on average, whatever k is, because the "
                "k in the fraction m / k cancels. The gap between the two lines is the most a selector could ever add, and "
                "the right panel shows the added coverage from each sample shrinking geometrically."
            ),
            "application": (
                "Before buying more samples for a task, ask what picks among them. If the answer is nothing, the extra "
                "samples raise the number of correct candidates but not the number delivered."
            ),
            "assumptions": (
                "Samples are independent and share one correctness chance p. That fails when samples copy a shared "
                "plan or a shared mistake, and then coverage stops rising well before the curve says it should. "
                "The values of p are constructed; they do not describe any real model."
            ),
            "check": "At p = 0.2, what is the coverage of five samples, and what does a blind pick from them deliver?",
            "answer": "Cov(5) = 1 - 0.8^5 = 1 - 0.32768 = 0.6723. A blind pick delivers p = 0.2, so 0.4723 of coverage is not delivered.",
            "provenance": "Constructed example: the chapter's p = 0.2 and p = 0.05 arithmetic (coverage 0.89 and 0.99 at 10 and 20 samples, 0.40 and 0.99 at 10 and 100), computed directly from the equations.",
            "source_section": "What sampling buys",
            "source_anchor": "what-sampling-buys",
            "controls": [
                {"key": "p", "label": "Chance one sample is correct (p)", "values": [0.05, 0.2], "default": 0.2},
                {"key": "k", "label": "Samples drawn (k)", "values": [5, 10, 20, 100], "default": 10},
            ],
            "function": "coverage_picture",
        },
        {
            "id": "C16-D02",
            "title": "The selector turns coverage into delivery",
            "question": "How much of the coverage reaches the user when the selector succeeds only part of the time, and what if the samples are not independent?",
            "equations": [EQ_SEL, EQ_COV, EQ_BLIND],
            "symbols": (
                "p is the chance one sample is correct (0.40 here). Cov(k) is the chance a correct sample is in the bank. "
                "The selector success shown is the chance the selector ranks a correct sample first when the bank holds one; "
                "the book calls it pi(k), and here it is held constant for banks of two or more. With one sample there is "
                "nothing to rank. Sel(k) is the chance the returned answer is correct. Blind selection returns p. If the samples "
                "share one failure, a bank that holds a correct sample holds only correct samples, so the selector is "
                "certain to pick a correct one and its setting is not used."
            ),
            "prediction": "With independent samples and a selector that succeeds 0.5 of the time when a correct sample exists, will five samples beat a blind pick of 0.40?",
            "explanation": (
                "Equation (16.3) multiplies two chances: a correct sample must be present, and the selector must find it. "
                "A perfect selector (1.0) delivers the whole coverage; a weaker one delivers a fraction. If the samples share "
                "one failure, coverage stays at p however many are drawn, and a bank that holds a correct sample holds only "
                "correct ones, so the selector adds nothing."
            ),
            "application": (
                "Report coverage and delivery as separate numbers on the same tasks. If coverage is high and delivery low, "
                "work on the selector; if coverage itself is low, no selector can help."
            ),
            "assumptions": (
                "A constant selector success is a constructed simplification. The book stresses that a real selector's success "
                "must be measured on banks of the size and kind in use, because it depends on ties, on the number of correct "
                "answers and on dependence. The shared-failure state is an extreme case chosen to show the boundary; there the selector setting has no effect."
            ),
            "check": "With independent samples, p = 0.4 and selector success 0.75, what is Sel(3)?",
            "answer": "Cov(3) = 1 - 0.6^3 = 0.784, so Sel(3) = 0.784 x 0.75 = 0.588, which beats the blind 0.40 by 0.188.",
            "provenance": "Constructed example: the laboratory's sample-allocation function with its default p = 0.4 and five-sample case, with selector success and sample dependence varied.",
            "source_section": "The selector needs its own measured success rate",
            "source_anchor": "the-selector-needs-its-own-measured-success-rate",
            "controls": [
                {"key": "selector", "label": "Selector success when a correct sample exists", "values": [0.5, 0.75, 0.9, 1.0], "default": 0.9},
                {"key": "dependence", "label": "How the samples fail", "values": ["independent", "shared"], "default": "independent",
                 "value_labels": ["Independent errors", "One shared failure"]},
            ],
            "function": "selector_picture",
        },
        {
            "id": "C16-D03",
            "title": "Length, volume or a selector: spending sixty units",
            "question": "With 60 units of compute, does it matter more to think longer, to sample more, or to pay for a selector?",
            "equations": [EQ_SEL, EQ_BLIND, EQ_COV],
            "symbols": (
                "One unit is one short generation. A long reasoning chain costs 4 units and raises the chance one sample is "
                "correct from 0.20 to the chosen value. Checking a sample with the selector costs a quarter of a unit. Cov is "
                "coverage, Sel the chance the returned answer is correct, and the selector success pi is the chance it ranks "
                "a correct sample first. Bars show Sel; diamonds show Cov."
            ),
            "prediction": "Using the book's selector values, which two allocations come out highest, and does the choice between length and volume move the answer more than adding a selector?",
            "explanation": (
                "Without a selector, Equation (16.2) says delivery is just p, so fifteen long samples deliver the long-chain p "
                "and sixty short samples deliver 0.20, however many samples were paid for. With a selector, Equation (16.3) "
                "multiplies a coverage near one by the selector success, so the selector's quality sets the result."
            ),
            "application": (
                "When splitting a fixed budget, price every lever in one unit and compute delivery for each combination. "
                "Do the arithmetic before arguing about whether longer reasoning or more samples is the better lever."
            ),
            "assumptions": (
                "The costs, the two p values and the selector successes are constructed; the book states them to show the "
                "ordering, not as results for any real system. Selector success is held constant across bank sizes here. "
                "A selector that ranks correct answers below wrong ones, as in the 0.15 state, can do worse than not selecting."
            ),
            "check": "Short samples cost 1 unit and long ones 4. With 20 short samples verified at 0.25 each, how many units are used, and what is Sel if pi = 0.6 and p = 0.2?",
            "answer": "Units: 20 x 1 + 20 x 0.25 = 25. Cov(20) = 1 - 0.8^20 = 1 - 0.0115 = 0.9885, so Sel = 0.9885 x 0.6 = 0.593.",
            "provenance": "Constructed example: the chapter's sixty-unit construction (Figure 16.3), including its stipulated selector values 0.73 and 0.785, with the other selector values and the long-chain p defined for this reader.",
            "source_section": "Three levers, one budget",
            "source_anchor": "three-levers-one-budget",
            "controls": [
                {"key": "selector", "label": "Selector success (allocations 3 and 4)", "values": ["book", "strong", "weak", "worse"], "default": "book",
                 "value_labels": ["Book values: 0.73 and 0.785", "Strong: 0.95 for both", "Weak: 0.50 for both", "Worse than random: 0.15 for both"]},
                {"key": "long_p", "label": "Chance one long-reasoning sample is correct", "values": [0.35, 0.25], "default": 0.35},
            ],
            "function": "allocation_picture",
        },
        {
            "id": "C16-D04",
            "title": "What a completed task costs, and who is allowed to be slow",
            "question": "Which procedure is cheapest per authorized success once a completion floor and a deadline rule some out?",
            "equations": [EQ_COST],
            "symbols": (
                "N is the number of attempted tasks (100 here). The cost of run i, written c with subscript i in the equation, "
                "counts failed attempts too. The indicator in the denominator is 1 when run i ended in an authorized, confirmed "
                "completion and 0 otherwise, so the denominator counts those runs. Cost per success is total cost "
                "divided by that count. Completion rate is the share of attempts that succeed; response time is seconds to "
                "answer. A failed task is also given a loss of 20 in one metric."
            ),
            "prediction": "With a 3 second deadline and a completion floor of 0.75, which procedure is the only feasible one? Is it also the lowest of the three cost-per-success values?",
            "explanation": (
                "Equation (16.5) divides everything spent by the number of real successes, so cheap procedures that fail often "
                "can still look cheap per success while missing the owner's requirements. A deadline and a completion floor "
                "are separate constraints and remove procedures before any ratio is compared. If none remains, the ratio does "
                "not choose for the owner."
            ),
            "application": (
                "When reporting an efficiency ratio, count every attempt's cost, count only runs that met the declared "
                "completion contract, and state the constraints the ratio does not capture."
            ),
            "assumptions": (
                "Three constructed procedures with known costs, completion rates and response times. Real rates must be "
                "estimated on matching tasks, and a ratio from a small sample is a different object from the underlying rate. "
                "With zero successes Equation (16.5) is undefined; it is not replaced by a printable number."
            ),
            "check": "A procedure costs 3 per attempt and completes 0.5 of 100 attempts. What is its cost per success?",
            "answer": "Total cost 100 x 3 = 300 and successes 100 x 0.5 = 50, so 300 / 50 = 6 per success.",
            "provenance": "Constructed example: the chapter's three procedures (costs 1, 1.5, 2; completion 60, 80, 85 percent; response 1, 2, 5 seconds; failure loss 20), with the deadline and completion floor varied. The loss for A is computed by the same rule. The costs and completion rates come from the section named above; the response times, deadlines and the loss of 20 per failure come from the next section, \"Waiting changes the allocation\".",
            "source_section": "What the budget actually buys",
            "source_anchor": "what-the-budget-actually-buys",
            "controls": [
                {"key": "deadline", "label": "Deadline (seconds)", "values": [3, 10], "default": 10},
                {"key": "required", "label": "Minimum completion rate required", "values": [0.5, 0.75, 0.82], "default": 0.75},
            ],
            "function": "cost_picture",
        },
    ],
}

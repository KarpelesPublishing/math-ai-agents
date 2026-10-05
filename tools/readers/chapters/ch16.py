"""Chapter 16 reader: Thought as Search.

Four demonstrations built on Equations (16.1) to (16.5).

Demonstration 1 draws coverage and the blind pick from the chapter's closed forms and adds the
chapter's overconfidence mechanism (a thin bank on the problems where p is near zero).
Demonstration 2 calls the laboratory's own allocation function
(math_ai_agents.chapters.ch16.evaluate) for the notebook's default, changed (shared failure) and
transfer cases and for the workbook's no-feasible-allocation question, so the reader, the notebook and
the chapter skill agree. Demonstration 3 uses the book's own sixty-unit construction and Demonstration 4
the book's three constructed procedures and the two observed attempts of workbench problem E.4.
Every number is a constructed teaching value.
"""
import math

import numpy as np

from math_ai_agents.chapters.ch16 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, undefined

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


def g6(x):
    """Six decimals for an intermediate value that is multiplied again by hand."""
    return fmt(x, 6) if x >= 1e-6 else f"{x:.1e}"


def coverage(p, k):
    return 1.0 - (1.0 - p) ** k


# Demonstration 1: coverage against a blind selector, and a thin bank

SPREAD_LABELS = {
    "shared": "Every problem has the same p (Equation 16.1)",
    "thin": "Overconfident: half the problems at 2p, half at 0 (same average p)",
}


def bank_coverage(p, k, spread):
    """Average coverage over the problems. 'thin': half the problems have chance 2p, half have 0."""
    if spread == "shared":
        return coverage(p, k)
    return 0.5 * coverage(2 * p, k) + 0.5 * 0.0


def sample_gain(p, j, spread):
    """Coverage added by sample number j (Equation 16.4 applied to each half of the problems)."""
    if spread == "shared":
        return p * (1 - p) ** (j - 1)
    return 0.5 * (2 * p) * (1 - 2 * p) ** (j - 1)


def coverage_picture(spread="shared", p=0.2, k=10):
    p = float(p)
    k = int(k)
    thin = spread == "thin"
    cov = bank_coverage(p, k, spread)
    cov_shared = coverage(p, k)
    gain = sample_gain(p, k + 1, spread)
    ks = np.arange(1, 101)
    fig, (left, right) = new_figure(ncols=2, height=4.3)

    cov_u = np.array([bank_coverage(p, int(x), "shared") for x in ks])
    cov_t = np.array([bank_coverage(p, int(x), "thin") for x in ks])
    left.plot(ks, cov_u, color=PALETTE["teal"], linewidth=2.6 if not thin else 1.6, alpha=1.0 if not thin else 0.7)
    left.plot(ks, cov_t, color=PALETTE["navy"], linewidth=2.6 if thin else 1.6, linestyle="dashed",
              alpha=1.0 if thin else 0.7)
    left.plot([1, 100], [p, p], color=PALETTE["terracotta"], linestyle="dotted", linewidth=2)
    chosen_color = PALETTE["navy"] if thin else PALETTE["teal"]
    left.plot([k], [cov], "o", color=chosen_color, markersize=9)
    left.plot([k], [p], "s", color=PALETTE["terracotta"], markersize=8)
    left.vlines(k, p, cov, color=PALETTE["grey"], linestyle=":", linewidth=1.5)
    label_point(left, 100, p, "blind pick = p", color=PALETTE["terracotta"], dx=-4, dy=7, ha="right", va="bottom").set_bbox(BOX)
    label_point(left, 55, float(bank_coverage(p, 55, "shared")), "shared p", color=PALETTE["teal"], dx=0, dy=8,
                ha="center", va="bottom").set_bbox(BOX)
    label_point(left, 55, float(bank_coverage(p, 55, "thin")), "thin bank", color=PALETTE["navy"], dx=0, dy=-9,
                ha="center", va="top").set_bbox(BOX)
    left.set_xlim(0, 104)
    left.set_ylim(0, 1.1)
    left.set_xlabel("Samples drawn, k")
    left.set_ylabel("Chance the bank holds a correct answer")
    left.set_title(f"Coverage at k = {k} is {fmt(cov, 2)} (average p = {fmt(p, 2)})", fontsize=11.5)

    gains_u = p * (1 - p) ** (ks - 1)
    gains_t = p * (1 - 2 * p) ** (ks - 1)
    right.semilogy(ks, gains_u, color=PALETTE["teal"], linewidth=2.6 if not thin else 1.6, alpha=1.0 if not thin else 0.7)
    right.semilogy(ks, np.maximum(gains_t, 1e-30), color=PALETTE["navy"], linewidth=2.6 if thin else 1.6, linestyle="dashed",
                   alpha=1.0 if thin else 0.7)
    if gain >= 1e-5:
        right.plot([k + 1], [gain], "o", color=chosen_color, markersize=9)
        label_point(right, k + 1, gain, f"sample {k + 1} adds {g(gain)}", color=PALETTE["ink"],
                    dx=-8 if k + 1 > 40 else 8, dy=-12 if k + 1 > 40 else 8, ha="right" if k + 1 > 40 else "left",
                    va="top" if k + 1 > 40 else "bottom").set_bbox(BOX)
    else:
        right.annotate(f"sample {k + 1} adds about\n{gain:.1e},\nbelow the axis floor", (k + 1, 1e-6), xytext=(100, 5e-6),
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
        "Coverage at 20 samples": fmt(bank_coverage(p, 20, spread), 4),
        "Gain from sample 5": g(sample_gain(p, 5, spread)),
        "Gain from sample 20": g(sample_gain(p, 20, spread)),
    }
    miss = (1 - p) ** k
    if not thin:
        interpretation = (
            f"Cov({k}) = 1 - (1 - {fmt(p, 2)})^{k} = 1 - {g(miss)} = {fmt(cov, 4)}. A blind selector returns "
            f"one sample at random, so it delivers p = {fmt(p, 2)} however large k is. The gap a selector could close is "
            f"{fmt(cov, 4)} - {fmt(p, 2)} = {fmt(cov - p, 4)}. The next sample adds {fmt(p, 2)} x (1 - {fmt(p, 2)})^{k} = "
            f"{fmt(p, 2)} x {g(miss)} = {g(gain)}."
        )
        if gain >= 1e-4:
            interpretation += (f" That equals Cov({k + 1}) - Cov({k}) = {fmt(coverage(p, k + 1), 4)} - {fmt(cov, 4)} = "
                               f"{fmt(coverage(p, k + 1) - cov, 4)}.")
        steps = [
            f"Chance one sample is wrong: 1 - p = 1 - {fmt(p, 2)} = {fmt(1 - p, 2)}.",
            f"All {k} samples wrong: {fmt(1 - p, 2)}^{k} = {g(miss)}.",
            f"Coverage Cov({k}) = 1 - {g(miss)} = {fmt(cov, 4)}.",
            f"A blind pick delivers p = {fmt(p, 2)} whatever k is (Equation 16.2: the k in m / k cancels).",
            f"Gap a selector could close: {fmt(cov, 4)} - {fmt(p, 2)} = {fmt(cov - p, 4)}.",
            f"Sample {k + 1} adds p x (1 - p)^{k} = {fmt(p, 2)} x {g(miss)} = {g(gain)}.",
        ]
        alt = (f"Left: coverage rises from {fmt(p, 2)} at one sample to {fmt(cov, 2)} at {k}, far above the flat blind line at "
               f"{fmt(p, 2)}. Right: added coverage per sample falls geometrically, {g(gain)} at sample {k + 1}.")
    else:
        hi = 2 * p
        miss_hi = (1 - hi) ** k
        cov_hi = coverage(hi, k)
        interpretation = (
            f"Half the problems have chance 2p = {fmt(hi, 2)} per sample and half have 0, so the average chance is "
            f"0.5 x {fmt(hi, 2)} + 0.5 x 0 = {fmt(p, 2)}, the same p as before. Cov({k}) = 0.5 x (1 - {fmt(1 - hi, 2)}^{k}) + 0.5 x 0 = "
            f"0.5 x {g6(cov_hi)} = {fmt(cov, 4)}, against {fmt(cov_shared, 4)} when every problem shares p = {fmt(p, 2)}. "
            f"A blind pick still delivers {fmt(p, 2)}. The next sample adds 0.5 x {fmt(hi, 2)} x {fmt(1 - hi, 2)}^{k} = "
            f"{g(gain)}. The single-sample chance did not change; the bank on the problems at 0 never fills."
        )
        steps = [
            f"Half the problems have chance 2p = {fmt(hi, 2)} per sample, half have 0.",
            f"Average chance of one sample: 0.5 x {fmt(hi, 2)} + 0.5 x 0 = {fmt(p, 2)} = p.",
            f"On the half at {fmt(hi, 2)}: all {k} wrong is {fmt(1 - hi, 2)}^{k} = {g6(miss_hi)}, so coverage there is {g6(cov_hi)}.",
            f"Cov({k}) = 0.5 x {g6(cov_hi)} + 0.5 x 0 = {fmt(cov, 4)}.",
            f"With every problem at p, Cov({k}) = 1 - {fmt(1 - p, 2)}^{k} = {fmt(cov_shared, 4)}.",
            f"Blind pick: still {fmt(p, 2)}. Sample {k + 1} adds 0.5 x {fmt(hi, 2)} x {fmt(1 - hi, 2)}^{k} = {g(gain)}.",
        ]
        alt = (f"Left: the thin-bank coverage curve levels off near 0.5 while the shared-p curve climbs toward 1; at k = {k} they are "
               f"{fmt(cov, 2)} and {fmt(cov_shared, 2)}, with the blind line flat at {fmt(p, 2)}. Right: the added coverage per sample "
               f"for the thin bank falls faster, {g(gain)} at sample {k + 1}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: the selector's measured success, computed by the laboratory

CURVE_COUNTS = list(range(1, 21))

CASES = {
    # the notebook's default, its changed case (one shared failure), its transfer case, and the workbook's
    # question about an allocation set in which nothing is feasible
    "default": {"candidate_success": 0.4, "sample_cost": 1, "sample_latency": 1, "selector_cost": 1,
                "selector_latency": 1, "deadline": 6, "budget": 6, "shared_error": False, "sample_counts": [1, 2, 3, 5]},
    "shared": {"candidate_success": 0.4, "sample_cost": 1, "sample_latency": 1, "selector_cost": 1,
               "selector_latency": 1, "deadline": 6, "budget": 6, "shared_error": True, "sample_counts": [1, 2, 3, 5]},
    "transfer": {"candidate_success": 0.7, "sample_cost": 2, "sample_latency": 1, "selector_cost": 3,
                 "selector_latency": 2, "deadline": 3, "budget": 6, "shared_error": False, "sample_counts": [1, 2, 4]},
    "none": {"candidate_success": 0.4, "sample_cost": 1, "sample_latency": 1, "selector_cost": 1,
             "selector_latency": 1, "deadline": 6, "budget": 0.5, "shared_error": False, "sample_counts": [1, 2, 3, 5]},
}


def lab_run(setting, selector, counts=None):
    data = dict(CASES[setting], selector_accuracy=float(selector))
    if counts is not None:
        data["sample_counts"] = counts
        data["budget"] = 1000
        data["deadline"] = 1000
    return evaluate(data)


def selector_picture(setting="default", selector=0.9):
    case = CASES[setting]
    p = case["candidate_success"]
    q = float(selector)
    shared = case["shared_error"]
    out = lab_run(setting, q)
    rows = out["tables"]
    chosen = out["metrics"]["selected_allocation"]
    curve = lab_run(setting, q, CURVE_COUNTS)["tables"]
    n = np.array([r["samples"] for r in curve])
    cov = np.array([r["coverage"] for r in curve])
    sel = np.array([r["selected_success"] for r in curve])
    fig, (left, right) = new_figure(ncols=2, height=4.4)

    left.plot(n, cov, color=PALETTE["teal"], linewidth=2.2)
    left.plot(n, sel, color=PALETTE["navy"], linewidth=2.2, marker="o", markersize=4)
    left.plot([1, 20], [p, p], color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.8)
    if chosen:
        mark = chosen["samples"]
        left.plot([mark], [chosen["selected_success"]], "D", color=PALETTE["navy"], markersize=9)
        left.plot([mark], [chosen["coverage"]], "o", color=PALETTE["teal"], markersize=9)
        left.axvline(mark, color=PALETTE["grey"], linestyle=":", linewidth=1.3)
        label_point(left, mark, 0.02, f"chosen n = {mark}", color=PALETTE["ink"], dx=4, dy=0, ha="left", va="bottom")
    groups = []
    for value, color, text in ((cov[-1], PALETTE["teal"], "coverage"), (sel[-1], PALETTE["navy"], "selection"),
                               (p, PALETTE["terracotta"], "blind pick")):
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
        label_point(left, 20, grp["y"], " = ".join(grp["texts"]), color=grp["color"], dx=-4,
                    dy=-8 if below else 8, ha="right", va="top" if below else "bottom").set_bbox(BOX)
    left.set_xticks([1, 5, 10, 15, 20])
    left.set_xlim(0.5, 20.5)
    left.set_ylim(0, 1.1)
    left.set_xlabel("Samples drawn, k (one sample skips the selector)")
    left.set_ylabel("Chance of a correct delivered answer")
    kind = "shared failure" if shared else f"independent, selector {fmt(q, 2)}"
    left.set_title(f"p = {fmt(p, 2)}, {kind}", fontsize=11.5)

    xs = np.arange(len(rows))
    for x, r in zip(xs, rows):
        is_chosen = chosen is not None and r["samples"] == chosen["samples"]
        ok = r["feasible"]
        right.bar(x, r["selected_success"], width=0.6, color=PALETTE["teal"] if ok else "white",
                  edgecolor=PALETTE["ink"] if ok else PALETTE["grey"], hatch=None if ok else "///",
                  linewidth=2.4 if is_chosen else 1.2)
        text = fmt(r["selected_success"], 3) + ("\nchosen" if is_chosen else ("" if ok else "\nover limit"))
        right.text(x, r["selected_success"] + 0.02, text, ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"],
                   bbox=BOX, zorder=6)
    right.plot([-0.5, len(rows) - 0.5], [p, p], color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.6)
    right.set_xticks(xs, [f"n = {r['samples']}\ncost {r['cost']:g}, {r['latency']:g} s" for r in rows])
    right.set_xlim(-0.6, len(rows) - 0.4)
    right.set_ylim(0, 1.25)
    right.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    right.set_xlabel("Allocation (hatched = over the budget or the deadline)")
    right.set_ylabel("Chance of a correct delivered answer")
    right.set_title(f"Limits: budget {case['budget']:g}, deadline {case['deadline']:g} s", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    feasible_rows = [r for r in rows if r["feasible"]]
    big = rows[-1]
    metrics = {
        "Feasible allocations": ", ".join(f"n = {r['samples']}" for r in feasible_rows) if feasible_rows else "none",
        "Chosen allocation": f"n = {chosen['samples']}" if chosen else undefined("no allocation is feasible"),
        "Coverage of the chosen allocation": fmt(chosen["coverage"], 4) if chosen else undefined("no allocation is feasible"),
        "Selected success of the chosen allocation": fmt(chosen["selected_success"], 4) if chosen else undefined("no allocation is feasible"),
        "Blind selection": fmt(p, 2),
        f"Coverage minus delivery at n = {big['samples']}" + ("" if big["feasible"] else " (over a limit)"):
            fmt(big["coverage"] - big["selected_success"], 4),
    }

    sc, sl, dl, bd = case["selector_cost"], case["selector_latency"], case["deadline"], case["budget"]
    c1, l1 = case["sample_cost"], case["sample_latency"]

    def row_text(r):
        k = r["samples"]
        if k == 1:
            return (f"n = 1: cost 1 x {c1:g} = {r['cost']:g}, time 1 x {l1:g} = {r['latency']:g} (no selector)")
        return (f"n = {k}: cost {k} x {c1:g} + {sc:g} = {r['cost']:g}, time {k} x {l1:g} + {sl:g} = {r['latency']:g}")

    def why_not(r):
        bits = []
        if r["cost"] > bd + 1e-12:
            bits.append(f"cost {r['cost']:g} > {bd:g}")
        if r["latency"] > dl + 1e-12:
            bits.append(f"time {r['latency']:g} > {dl:g}")
        return " and ".join(bits)

    if chosen:
        k = chosen["samples"]
        if k == 1:
            calc = (f"One sample skips the selector, so Sel(1) = p = {fmt(p, 2)}; {row_text(chosen)}, inside the budget {bd:g} and the deadline {dl:g} s.")
        elif shared:
            calc = (f"Samples share one failure, so Cov({k}) = p = {fmt(p, 2)} whatever k is. A bank that holds a correct sample holds "
                    f"only correct samples, so Sel({k}) = {fmt(p, 2)} x 1 + (1 - {fmt(p, 2)}) x 0 = {fmt(chosen['selected_success'], 4)}; "
                    f"the selector setting {fmt(q, 2)} is not used.")
        else:
            calc = (f"Cov({k}) = 1 - (1 - {fmt(p, 2)})^{k} = 1 - {fmt((1 - p) ** k, 5)} = {fmt(chosen['coverage'], 5)}. "
                    f"Sel({k}) = {fmt(chosen['coverage'], 5)} x {fmt(q, 2)} + (1 - {fmt(chosen['coverage'], 5)}) x 0 = "
                    f"{fmt(chosen['selected_success'], 4)}; {row_text(chosen)}.")
    else:
        calc = (f"The cheapest row, {row_text(rows[0])}, already exceeds the budget {bd:g} ({r_cost(rows[0])} > {bd:g}).")
    others = [r for r in rows if (chosen and r["samples"] != chosen["samples"]) or (not chosen and r is not rows[0])]
    notes = []
    for r in others:
        if not r["feasible"]:
            notes.append(f"{row_text(r)} is out ({why_not(r)})")
        else:
            notes.append(f"n = {r['samples']} is feasible with Sel = {fmt(r['selected_success'], 4)} and cost {r['cost']:g}")
    if notes:
        calc += " Other rows: " + "; ".join(notes) + "."
    if chosen and shared and chosen["samples"] == 1:
        calc += (f" Every feasible row delivers {fmt(p, 2)}, so the rule that ties go to the lower cost picks n = 1.")
    if not chosen:
        late = any(r["latency"] > dl + 1e-12 for r in rows)
        diag = ("No allocation is feasible, so nothing can be delivered and the generator-or-selector question does not arise: "
                + ("the budget and the deadline are the constraint." if late else
                   f"the budget is the constraint (every row meets the {dl:g} s deadline)."))
    else:
        k = chosen["samples"]
        cov_c, sel_c = chosen["coverage"], chosen["selected_success"]
        gap = cov_c - sel_c
        larger_out = [r for r in rows if not r["feasible"] and r["samples"] > k]
        if larger_out:
            names = ", ".join(f"n = {r['samples']}" for r in larger_out)
            diag = (f"The chosen n = {k} has coverage {fmt(cov_c, 3)} and delivery {fmt(sel_c, 3)}. The larger banks ({names}) are over the "
                    "budget or the deadline, so they cannot run: the deadline or budget is the constraint, and a better selector "
                    "cannot be used on a bank that does not fit.")
        elif math.isclose(cov_c, sel_c, abs_tol=1e-9):
            if cov_c <= 0.5:
                diag = (f"At the chosen n = {k}, coverage {fmt(cov_c, 3)} equals delivery {fmt(sel_c, 3)}: nothing is left for a selector "
                        "to add and coverage itself is low, so the generator is the constraint (compare the chapter's coverage 0.45 and delivery 0.43).")
            else:
                diag = (f"At the chosen n = {k}, coverage {fmt(cov_c, 3)} equals delivery {fmt(sel_c, 3)}: nothing is left for a selector "
                        "to add and coverage is already high, so neither the selector nor the generator is holding the result back.")
        elif sel_c / cov_c <= 0.5 + 1e-9:
            diag = (f"At the chosen n = {k}, coverage {fmt(cov_c, 3)} is far above delivery {fmt(sel_c, 3)}, "
                    f"which is at most half of it (a gap of {fmt(gap, 3)}): the selector is the constraint (compare the chapter's "
                    "coverage 0.95 and delivery 0.40).")
        else:
            diag = (f"At the chosen n = {k}, coverage is {fmt(cov_c, 3)} and delivery {fmt(sel_c, 3)}, a gap of "
                    f"{fmt(gap, 3)}: the selector still costs part of the coverage, but delivery is more than half of it, so neither factor alone explains the shortfall.")
    interpretation = f"{calc} {diag}"

    steps = []
    if chosen:
        k = chosen["samples"]
        if k == 1:
            steps.append(f"One sample skips the selector: Sel(1) = p = {fmt(p, 2)}.")
        elif shared:
            steps.append(f"Shared failure: Cov({k}) = p = {fmt(p, 2)}, and the selector adds nothing, so Sel({k}) = {fmt(chosen['selected_success'], 4)}.")
        else:
            steps.append(f"Coverage: Cov({k}) = 1 - (1 - {fmt(p, 2)})^{k} = {fmt(chosen['coverage'], 5)}.")
            steps.append(f"Delivery: Sel({k}) = {fmt(chosen['coverage'], 5)} x {fmt(q, 2)} = {fmt(chosen['selected_success'], 4)}.")
        steps.append(row_text(chosen) + f"; budget {bd:g}, deadline {dl:g} s.")
    else:
        steps.append(f"Budget {bd:g}, deadline {dl:g}.")
    for r in others:
        steps.append(row_text(r) + (f": out, {why_not(r)}." if not r["feasible"] else f": feasible, Sel = {fmt(r['selected_success'], 4)}."))
    steps.append("Rule: highest selected success among the feasible rows; ties go to lower cost." if chosen
                 else "No row is feasible, so no allocation is chosen: revise the limits or abstain.")
    steps = steps[:8]
    alt = ("Left: coverage and selected success against samples drawn, with the flat blind line at "
           f"{fmt(p, 2)}. Right: bars of selected success for each allocation, hatched when over a limit"
           + (f"; the chosen allocation is n = {chosen['samples']}." if chosen else "; none is chosen because every allocation is over a limit."))
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


def r_cost(row):
    return f"{row['cost']:g}"


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
    next_gain = long_p * (1 - long_p) ** 12
    calc = (f"Allocation 1: blind, so Sel = p = {fmt(long_p, 2)}. Allocation 2: Sel = p = 0.20. "
            f"Allocation 3: Cov(48) = 1 - 0.8^48 = {fmt(cov3, 5)}, so Sel = {fmt(cov3, 5)} x {pi3:g} = {fmt(cov3 * pi3, 3)}. "
            f"Allocation 4: Cov(12) = 1 - {fmt(1 - long_p, 2)}^12 = {fmt(cov4, 4)}, so Sel = {fmt(cov4, 4)} x {pi4:g} = "
            f"{fmt(cov4 * pi4, 3)}. Spending: allocation 4 uses 12 x 4 + 12 x 0.25 = {fmt(units[3], 0)} units and leaves "
            f"{fmt(60 - units[3], 0)} unspent; the other three use all 60. A thirteenth long sample would add "
            f"{fmt(long_p, 2)} x {fmt(1 - long_p, 2)}^12 = {fmt(next_gain, 4)} to coverage (Equation 16.4), small next to the "
            f"{fmt(cov4, 4)} already held.")
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
    steps = [
        f"Allocation 1: 15 long samples, blind: Sel = p = {fmt(long_p, 2)}.",
        "Allocation 2: 60 short samples, blind: Sel = p = 0.20.",
        f"Allocation 3: Cov(48) = 1 - 0.8^48 = {fmt(cov3, 5)}; Sel = {fmt(cov3, 5)} x {pi3:g} = {fmt(cov3 * pi3, 3)}.",
        f"Allocation 4: Cov(12) = 1 - {fmt(1 - long_p, 2)}^12 = {fmt(cov4, 4)}; Sel = {fmt(cov4, 4)} x {pi4:g} = {fmt(cov4 * pi4, 3)}.",
        f"Units: allocation 4 uses 12 x 4 + 12 x 0.25 = {fmt(units[3], 0)} of 60, leaving {fmt(60 - units[3], 0)}.",
        f"A thirteenth long sample adds {fmt(long_p, 2)} x {fmt(1 - long_p, 2)}^12 = {fmt(next_gain, 4)} (Equation 16.4).",
        f"Highest delivered: {metrics['Best allocation']}.",
    ]
    alt = (f"Four horizontal bars of delivered success: all on length {fmt(long_p, 2)}, all on volume 0.20, volume with a selector "
           f"{fmt(cov3 * pi3, 2)}, length with a selector {fmt(cov4 * pi4, 2)}; diamonds mark coverage. The highest is "
           f"{metrics['Best allocation']}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: cost per success under a deadline

PROCEDURES = [
    # name, cost per attempted task, completion rate, response seconds
    ("A", 1.0, 0.60, 1.0),
    ("B", 1.5, 0.80, 2.0),
    ("C", 2.0, 0.85, 5.0),
]
ATTEMPTS = 100
FAILURE_LOSS = 20.0
OBSERVED_COSTS = (2.0, 3.0)  # workbench E.4 step 4: two attempts, neither succeeds


def observed_picture():
    total = sum(OBSERVED_COSTS)
    successes = 0
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.bar([0, 1, 2], [OBSERVED_COSTS[0], OBSERVED_COSTS[1], total],
             color=["#8fa3b8", "#8fa3b8", PALETTE["navy"]], width=0.6, edgecolor=PALETTE["ink"])
    for x, v in zip((0, 1, 2), (OBSERVED_COSTS[0], OBSERVED_COSTS[1], total)):
        left.text(x, v + 0.12, fmt(v, 1), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.set_xticks([0, 1, 2], ["Attempt 1", "Attempt 2", "Total cost"])
    left.set_ylim(0, 6.2)
    left.set_xlabel("Observed attempt (both failed)")
    left.set_ylabel("Cost (monetary units)")
    left.set_title("Equation (16.5) numerator: every attempt counts", fontsize=11.5)
    left.grid(axis="x", alpha=0)
    right.bar([0], [successes], width=0.5, color="white", edgecolor=PALETTE["terracotta"], hatch="///")
    right.text(0, 0.35, "0 authorized\nconfirmed completions", ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
    right.text(0, 2.1, f"{fmt(total, 0)} / 0\nis undefined", ha="center", va="center", fontsize=12.5, color=PALETTE["terracotta"],
               bbox=BOX)
    right.set_xlim(-0.8, 0.8)
    right.set_ylim(0, 3.2)
    right.set_xticks([0], ["Completions"])
    right.set_xlabel("Equation (16.5) denominator")
    right.set_ylabel("Runs that met the completion contract")
    right.set_title("A ratio with a missing denominator", fontsize=11.5)
    right.grid(axis="x", alpha=0)
    metrics = {
        "Attempts": "2",
        "Total cost": fmt(total, 1),
        "Authorized confirmed completions": "0",
        "Cost per success": undefined("no run succeeded"),
    }
    interpretation = (
        f"Total cost = {fmt(OBSERVED_COSTS[0], 0)} + {fmt(OBSERVED_COSTS[1], 0)} = {fmt(total, 0)}. Completions = 0 + 0 = 0. "
        f"Equation (16.5) would divide {fmt(total, 0)} by 0, which is undefined, so the report is the attempted-task count (2), "
        f"the total cost ({fmt(total, 0)}) and the missing denominator. Replacing the 0 by 1 would print {fmt(total, 0)} / 1 = "
        f"{fmt(total, 0)} but would change the metric. These two observed attempts describe the sample, not the population "
        "ratios of procedures A, B and C."
    )
    steps = [
        f"Add every attempt's cost, failures included: {fmt(OBSERVED_COSTS[0], 0)} + {fmt(OBSERVED_COSTS[1], 0)} = {fmt(total, 0)}.",
        "Count the runs that met the completion contract: 0 + 0 = 0.",
        f"Equation (16.5): {fmt(total, 0)} / 0 has no value.",
        "Report the attempted-task count, the total cost and the missing denominator; do not substitute a printable number.",
    ]
    alt = ("Left: two failed attempts costing 2 and 3, and their total 5. Right: an empty bar for completions with the note that "
           "5 divided by 0 is undefined.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


def cost_picture(deadline=10, required=0.75, evidence="declared"):
    if evidence == "observed":
        return observed_picture()
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
        label_point(right, seconds, rate, f"{name} (cost {cost:g})", color=PALETTE["ink"], dx=10, dy=0, ha="left", va="center").set_bbox(BOX)
    label_point(right, deadline, 0.45, f"deadline {fmt(deadline, 0)} s", color=PALETTE["ink"], dx=-4, dy=0, ha="right",
                va="center").set_bbox(BOX)
    label_point(right, 0.1, required, f"need {fmt(required, 2)}", color=PALETTE["ink"], dx=0, dy=5, ha="left").set_bbox(BOX)
    right.set_xlim(0, 11.5)
    right.set_ylim(0.4, 1.0)
    right.set_xlabel("Response time (seconds)")
    right.set_ylabel("Completion rate (shaded: feasible)")
    right.set_title("Feasible region (no point beats another on all three)", fontsize=11.5)

    none = undefined("no procedure is feasible")
    metrics = {
        "Cost per success A": fmt(per_success["A"], 2),
        "Cost per success B": fmt(per_success["B"], 2),
        "Cost per success C": fmt(per_success["C"], 2),
        "Feasible procedures": ", ".join(feasible) if feasible else "none",
        "Cheapest per success overall": overall,
        "Cheapest per success among feasible": cheapest if cheapest else none,
        "Lowest cost plus failure loss (20 per failure)": lowest_loss if lowest_loss else none,
        "Procedures on the Pareto frontier": "A, B, C",
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
    frontier = (" No procedure is at least as good as another on completion, cost and time at once (A is cheapest and fastest, "
                "C completes most), so all three stay on the Pareto frontier; the frontier does not pick one for this deadline.")
    interpretation = calc + extra + frontier
    steps = [
        f"A: total cost 100 x 1 = 100, successes 100 x 0.60 = 60, so 100 / 60 = {fmt(per_success['A'], 4)}.",
        f"B: total cost 100 x 1.5 = 150, successes 100 x 0.80 = 80, so 150 / 80 = {fmt(per_success['B'], 4)}.",
        f"C: total cost 100 x 2 = 200, successes 100 x 0.85 = 85, so 200 / 85 = {fmt(per_success['C'], 4)}.",
        f"Feasible needs completion at least {fmt(required, 2)} and time at most {fmt(deadline, 0)} s: "
        f"{', '.join(feasible) if feasible else 'none'}.",
    ]
    if feasible:
        steps.append(f"Cheapest per success among the feasible: {cheapest} ({fmt(per_success[cheapest], 4)}).")
        steps.append(f"With a loss of 20 per failure: A {fmt(combined['A'], 1)}, B {fmt(combined['B'], 1)}, C {fmt(combined['C'], 1)}; "
                     f"lowest among the feasible is {lowest_loss}.")
    else:
        steps.append("No procedure is feasible, so no cheapest feasible procedure is defined.")
    alt = (f"Left: cost per success bars for A, B and C ({fmt(per_success['A'], 2)}, {fmt(per_success['B'], 2)}, "
           f"{fmt(per_success['C'], 2)}), hatched when a requirement is missed. Right: completion rate against response time with the "
           f"shaded feasible region for a {fmt(deadline, 0)} second deadline and a floor of {fmt(required, 2)}; feasible: "
           f"{', '.join(feasible) if feasible else 'none'}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 16,
    "title": "Thought as Search",
    "subtitle": "A correct answer can sit in the bank of candidates and still fail to reach the user; the selector decides.",
    "summary": (
        "These four demonstrations separate three things the chapter keeps apart: whether a correct candidate exists "
        "(coverage), whether the system returns it (selection), and what each costs. They follow the chapter's order: "
        "what sampling buys (and how a thin bank hides behind an unchanged single-answer chance), what a selector must earn "
        "(the notebook's default, shared-failure and transfer cases), how a fixed budget is split, and what a completed task costs."
    ),
    "ask_skill": {
        "prompt": (
            "Run the sample-allocation probe on candidate success 0.7, selector accuracy 0.5, sample cost 2, sample latency 1, "
            "selector cost 3, selector latency 2, a deadline of 3 and a budget of 6 for sample counts 1, 2 and 4, with independent "
            "errors. Show coverage, selected success, cost, latency and feasibility for every row, tell me which allocation is "
            "chosen, and say whether the generator or the selector is the constraint."
        )
    },
    "demos": [
        {
            "id": "C16-D01",
            "title": "Sampling fills the bank, but a blind pick ignores it",
            "question": "How many samples does it take to have a correct answer somewhere, what does a random pick from them deliver, and what if the chance is concentrated on a few problems?",
            "equations": [EQ_COV, EQ_BLIND, EQ_GAIN],
            "symbols": (
                "p is the chance that one sample is correct. k is the number of samples drawn, assumed independent. "
                "Cov(k) is coverage: the chance at least one of the k samples is correct. Sel(k) is the chance the returned "
                "sample is correct; with no way to rank, the system returns one at random. m is the number of correct "
                "samples among the k. The right panel shows the extra coverage bought by sample number k + 1. In the overconfident "
                "setting, half the problems have chance 2p per sample and half have chance 0, so the average is still p."
            ),
            "prediction": "At p = 0.05 with every problem sharing p, how likely is it that ten samples hold a correct answer?",
            "prediction_options": ["Below 0.10 (no better than one sample)", "About 0.40", "Above 0.90"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Cov(10) = 1 - 0.95^10 = 1 - 0.5987 = 0.4013, the chapter's 0.40. A blind pick from those ten still delivers only p = 0.05.",
                "incorrect": "Cov(10) = 1 - 0.95^10 = 1 - 0.5987 = 0.4013, about 0.40: far above one sample (0.05) but far below 0.90. Choose the shared setting, p = 0.05 and k = 10 to see it.",
            },
            "misconception": {
                "title": "More samples deliver a better answer",
                "text": (
                    "The chapter's exact result is that with a blind selector, drawing a hundred samples delivers precisely what drawing "
                    "one delivers, at a hundred times the cost: the k in m / k cancels. Move k from 10 to 100: coverage rises, the blind "
                    "pick stays at p."
                ),
            },
            "scope_note": {
                "text": (
                    "The chapter's results come from an unrefereed preprint reporting on its authors' own models on one dataset, and the "
                    "thirty-fold figure is their comparison rather than an established rate. Equation (16.1) assumes independent samples, "
                    "which an implementation must verify rather than assume. The verifier's discrimination is measured against "
                    "final-answer correctness, and the authors record the false positives that produces. Chapter 26 takes up what "
                    "coverage can and cannot bound."
                ),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "Coverage is one minus the chance that every sample is wrong, so it climbs fastest over the first few "
                "samples, faster for larger p, and flattens as k grows. The blind pick returns a correct sample with probability p on "
                "average, whatever k is, because the k in the fraction m / k cancels. The gap between the two lines is the most a "
                "selector could ever add, and the right panel shows the added coverage from each sample shrinking geometrically. "
                "Choose the overconfident setting to see the chapter's mechanism: the average chance of one sample is unchanged, so "
                "the single answer looks as good, but chance concentrated on some problems and absent on others leaves a thin bank "
                "whose coverage stops rising long before Equation (16.1) says."
            ),
            "application": (
                "Before buying more samples for a task, ask what picks among them. If the answer is nothing, the extra "
                "samples raise the number of correct candidates but not the number delivered. Measure bank coverage directly, by "
                "sampling repeated banks under one declared procedure, rather than inferring it from p."
            ),
            "assumptions": (
                "Within each problem, samples are independent and share one correctness chance. The overconfident setting is a "
                "constructed illustration of the chapter's statement that p can be near zero for many problems, not a model of any "
                "training run; the chapter's Figure 16.1 is schematic and compares different sampling procedures, so it does not "
                "isolate candidate count as the cause. The values of p are constructed; they do not describe any real model."
            ),
            "check": "At p = 0.2 with every problem sharing p, what is the coverage of five samples, and what does a blind pick from them deliver?",
            "answer": "Cov(5) = 1 - 0.8^5 = 1 - 0.32768 = 0.6723. A blind pick delivers p = 0.2, so 0.4723 of coverage is not delivered.",
            "provenance": "Constructed example: the chapter's p = 0.2, 0.05 and 0.3 arithmetic (coverage 0.89 and 0.99 at 10 and 20 samples for p = 0.2, 0.40 and 0.99 at 10 and 100 for p = 0.05, gains 0.30, 0.07 and under 0.001 at samples 1, 5 and 20 for p = 0.3), computed directly from the equations; the overconfident setting is defined for this reader.",
            "source_section": "What sampling buys",
            "source_anchor": "what-sampling-buys",
            "controls": [
                {"key": "spread", "label": "How the chance is spread over problems", "values": ["shared", "thin"], "default": "shared",
                 "value_labels": list(SPREAD_LABELS.values())},
                {"key": "p", "label": "Average chance one sample is correct (p)", "values": [0.05, 0.2, 0.3], "default": 0.2},
                {"key": "k", "label": "Samples drawn (k)", "values": [10, 100], "default": 10},
            ],
            "function": "coverage_picture",
        },
        {
            "id": "C16-D02",
            "title": "The selector turns coverage into delivery",
            "question": "How much of the coverage reaches the user under a budget and a deadline, and what changes when the samples share one failure or the limits are tight?",
            "equations": [EQ_SEL, EQ_COV, EQ_BLIND],
            "symbols": (
                "p is the chance one sample is correct. Cov(k) is the chance a correct sample is in the bank. "
                "The selector success shown is the chance the selector ranks a correct sample first when the bank holds one; "
                "the book calls it pi(k), and here it is held constant for banks of two or more. With one sample there is "
                "nothing to rank. Sel(k) is the chance the returned answer is correct. Blind selection returns p. Cost of n samples "
                "is n times the sample cost plus the selector cost (no selector cost for one sample); time is n times the sample "
                "time plus the selector time. If the samples share one failure, a bank that holds a correct sample holds only "
                "correct samples, so the selector is certain to pick a correct one and its setting is not used."
            ),
            "prediction": "With independent samples and a selector that succeeds 0.5 of the time when a correct sample exists, will five samples beat a blind pick of 0.40?",
            "prediction_options": ["Five samples beat 0.40", "Five samples fall below 0.40", "Exactly 0.40"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "Sel(5) = 0.92224 x 0.5 = 0.4611, above 0.40 by 0.0611. Two samples would give 0.64 x 0.5 = 0.32, below the blind line: a weak selector can cost more than it earns for small banks.",
                "incorrect": "Sel(5) = 0.92224 x 0.5 = 0.4611, which is above 0.40. Choose the notebook default setting and selector 0.5 to see it; at two samples the same selector gives 0.64 x 0.5 = 0.32, below the blind line.",
            },
            "misconception": {
                "title": "A selector that ranks well pairwise delivers well",
                "text": (
                    "The chapter keeps the pairwise chance d, that a selector scores one correct sample above one wrong one, apart from "
                    "the measured top-rank success pi(k) of a bank. Ties, dependence and the number of correct candidates affect pi(k); "
                    "d alone does not determine it. Here pi is a setting, which is why each state asks what the delivered number is, "
                    "not how well the selector compares two answers."
                ),
            },
            "explanation": (
                "Equation (16.3) multiplies two chances: a correct sample must be present, and the selector must find it. "
                "A perfect selector (1.0) delivers the whole coverage; a weaker one delivers a fraction. If the samples share "
                "one failure, coverage stays at p however many are drawn, and a bank that holds a correct sample holds only "
                "correct ones, so the selector adds nothing. The right panel adds the resources: an allocation that is over the "
                "budget or the deadline stays visible but cannot be chosen, even when its coverage is the highest, and the "
                "gap between coverage and delivery tells which part, the generator or the selector, is holding the result back."
            ),
            "application": (
                "Report coverage and delivery as separate numbers on the same tasks. If coverage is high and delivery low, "
                "work on the selector; if coverage itself is low, no selector can help. Keep infeasible rows in the record, as "
                "the companion's probe does, and say when none is feasible instead of exceeding a hard limit."
            ),
            "assumptions": (
                "A constant selector success is a constructed simplification. The book stresses that a real selector's success "
                "must be measured on banks of the size and kind in use, because it depends on ties, on the number of correct "
                "answers and on dependence. The shared-failure state is an extreme case chosen to show the boundary; there the selector setting has no effect. "
                "Time is serial and the costs are constructed. The rule that a shared failure makes selection equal coverage is the laboratory's and the workbook's convention; the chapter itself states only that dependence breaks Equation (16.1). The no-feasible state uses a budget of 0.5, defined for this reader."
            ),
            "check": "With independent samples, p = 0.4 and selector success 0.75, what is Sel(3)?",
            "answer": "Cov(3) = 1 - 0.6^3 = 0.784, so Sel(3) = 0.784 x 0.75 = 0.588, which beats the blind 0.40 by 0.188.",
            "provenance": "Constructed example: the laboratory's sample-allocation function with the notebook's default (p = 0.4, selector 0.9, counts 1, 2, 3 and 5, limits 6 and 6), changed (one shared failure) and transfer cases (p = 0.7, selector 0.5, costs 2 and 3, limits 3 and 6, counts 1, 2 and 4), and the workbook's question about an allocation set with no feasible row (a budget of 0.5, defined for this reader).",
            "source_section": "The selector needs its own measured success rate",
            "source_anchor": "the-selector-needs-its-own-measured-success-rate",
            "controls": [
                {"key": "setting", "label": "Case and limits", "values": ["default", "shared", "transfer", "none"], "default": "default",
                 "value_labels": ["Notebook default: p 0.4, limits 6 and 6", "Changed: the samples share one failure",
                                  "Transfer: p 0.7, dearer samples, limits 3 s and 6", "No allocation feasible: budget 0.5"]},
                {"key": "selector", "label": "Selector success when a correct sample exists", "values": [0.5, 0.9, 1.0], "default": 0.9},
            ],
            "function": "selector_picture",
        },
        {
            "id": "C16-D03",
            "title": "Length, volume or a selector: spending sixty units",
            "question": "With 60 units of compute, does it matter more to think longer, to sample more, or to pay for a selector?",
            "equations": [EQ_SEL, EQ_BLIND, EQ_COV, EQ_GAIN],
            "symbols": (
                "One unit is one short generation. A long reasoning chain costs 4 units and raises the chance one sample is "
                "correct from 0.20 to the chosen value. Checking a sample with the selector costs a quarter of a unit. Cov is "
                "coverage, Sel the chance the returned answer is correct, and the selector success pi is the chance it ranks "
                "a correct sample first. Bars show Sel; diamonds show Cov."
            ),
            "prediction": "Using the book's selector values, which allocation comes out highest?",
            "prediction_options": ["1. All on length", "2. All on volume", "3. Volume with a selector", "4. Length with a selector"],
            "prediction_answer": 3,
            "prediction_feedback": {
                "correct": "Length with a selector: Cov(12) = 0.9943 and Sel = 0.9943 x 0.785 = 0.781, just above volume with a selector (0.99998 x 0.73 = 0.730). Both beat the two blind allocations (0.35 and 0.20).",
                "incorrect": "Length with a selector is highest: 0.9943 x 0.785 = 0.781, against 0.730 for volume with a selector and 0.35 and 0.20 for the two blind allocations. Choose the book values to see the four bars.",
            },
            "misconception": {
                "title": "Without a good selector, think less",
                "text": (
                    "The chapter says the selection argument is not saying that a system without a good selector should think less. "
                    "Longer reasoning raises p directly, which raises delivery under blind selection too (Sel = p). Compare allocation 1 "
                    "(0.35) with allocation 2 (0.20): length helped with no selector at all. What blind selection denies is that "
                    "drawing more samples helps."
                ),
            },
            "explanation": (
                "Without a selector, Equation (16.2) says delivery is just p, so fifteen long samples deliver the long-chain p "
                "and sixty short samples deliver 0.20, however many samples were paid for. With a selector, Equation (16.3) "
                "multiplies a coverage near one by the selector success, so the selector's quality sets the result. Once coverage "
                "is near one, Equation (16.4) says another sample adds almost nothing, which is why, at the chapter's 0.35, the nine units left over by "
                "allocation 4 are not best spent on more samples."
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
            "provenance": "Constructed example: the chapter's sixty-unit construction (Figure 16.3), including its stipulated selector values 0.73 and 0.785, with the other selector values and the second long-chain p defined for this reader.",
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
            "question": "Which procedure is cheapest per authorized success once a completion floor and a deadline rule some out, and what does the ratio do when nothing succeeds?",
            "equations": [EQ_COST],
            "symbols": (
                "N is the number of attempted tasks (100 here). The cost of run i, written c with subscript i in the equation, "
                "counts failed attempts too. The indicator in the denominator is 1 when run i ended in an authorized, confirmed "
                "completion and 0 otherwise, so the denominator counts those runs. Cost per success is total cost "
                "divided by that count. Completion rate is the share of attempts that succeed; response time is seconds to "
                "answer. A failed task is also given a loss of 20 in one metric. The Pareto frontier keeps the procedures that no other "
                "procedure beats on completion, cost and time at once."
            ),
            "prediction": "With a 3 second deadline and a completion floor of 0.75, which procedure is the only feasible one?",
            "prediction_options": ["A", "B", "C", "None is feasible"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "B: its completion 0.80 meets the floor 0.75 and its 2 seconds meet the 3 second deadline. A completes only 0.60 and C takes 5 seconds. A has the lowest cost per success (1.6667) yet is not feasible.",
                "incorrect": "Only B is feasible: 0.80 is at least 0.75 and 2 s is at most 3 s. A completes 0.60, below the floor, and C takes 5 s, past the deadline. Choose a 3 second deadline and a floor of 0.75 to see it.",
            },
            "misconception": {
                "title": "The lowest cost per success picks the procedure",
                "text": (
                    "The chapter notes that A has the lowest cost per success and the lowest completion rate, and that the ratio alone "
                    "cannot tell an owner who requires at least 75 percent completion which procedure to use: under that requirement, "
                    "A is inadmissible. Among the three declared procedures the lowest ratio is always A, even when A is not feasible."
                ),
            },
            "explanation": (
                "Equation (16.5) divides everything spent by the number of real successes, so cheap procedures that fail often "
                "can still look cheap per success while missing the owner's requirements. A deadline and a completion floor "
                "are separate constraints and remove procedures before any ratio is compared. If none remains, the ratio does "
                "not choose for the owner. The ratio also needs a denominator: with two observed attempts and no success, "
                "Equation (16.5) has no value, and a printable replacement would change the metric."
            ),
            "application": (
                "When reporting an efficiency ratio, count every attempt's cost, count only runs that met the declared "
                "completion contract, and state the constraints the ratio does not capture. Report a zero denominator as "
                "undefined, with the attempted-task count and the total cost."
            ),
            "assumptions": (
                "Three constructed procedures with known costs, completion rates and response times. Real rates must be "
                "estimated on matching tasks, and a ratio from a small sample is a different object from the underlying rate. "
                "The two observed attempts describe a sample, not the population ratios. The Pareto statement is about the three "
                "procedures as stated; it does not pick one for a particular deadline or authority contract."
            ),
            "check": "A procedure costs 3 per attempt and completes 0.5 of 100 attempts. What is its cost per success?",
            "answer": "Total cost 100 x 3 = 300 and successes 100 x 0.5 = 50, so 300 / 50 = 6 per success.",
            "provenance": "Constructed example: the chapter's three procedures (costs 1, 1.5, 2; completion 60, 80, 85 percent; response 1, 2, 5 seconds; failure loss 20) and workbench problem E.4 (two attempts costing 2 and 3, neither successful), with the deadline and completion floor varied. The costs and completion rates come from the section named above; the response times, deadlines and the loss of 20 per failure come from the section \"Waiting changes the allocation\".",
            "source_section": "What the budget actually buys",
            "source_anchor": "what-the-budget-actually-buys",
            "controls": [
                {"key": "deadline", "label": "Deadline (seconds, declared rates only)", "values": [3, 10], "default": 10},
                {"key": "required", "label": "Minimum completion rate required (declared rates only)", "values": [0.5, 0.75, 0.82], "default": 0.75},
                {"key": "evidence", "label": "What the ratio is computed from", "values": ["declared", "observed"], "default": "declared",
                 "value_labels": ["The three procedures' declared rates", "Two observed attempts, neither succeeded"]},
            ],
            "function": "cost_picture",
        },
    ],
}

"""Chapter 26 reader: How Much More Could the System Become?

Four demonstrations built on Equations (26.1) to (26.3) and the chapter's
constructed fixed-generator saturation curve. Demonstration 2 calls the
laboratory's own bank-ceiling function
(math_ai_agents.chapters.ch26.evaluate), so the reader, the notebook and the
chapter skill agree. Demonstration 1 uses the book's ten-candidate worked
subset calculation as its default state. Demonstration 3 uses the three
percentages the chapter reports for one published experiment, as given, and
adds one hypothetical share defined for this reader. Demonstration 4 uses the
chapter's three constructed coverage points. Nothing here is a measurement.
"""
import math

import numpy as np
from matplotlib.patches import Rectangle

from math_ai_agents.chapters.ch26 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure

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


# Demonstration 1: a bank is a finite object

POOL = 10  # n, the book's worked pool size


def subset_counts(n, c, k):
    """Number of size-k subsets holding exactly j passing programs, j = 0..min(c, k)."""
    return [math.comb(c, j) * math.comb(n - c, k - j) for j in range(min(c, k) + 1)]


def finite_pool_picture(passing=2, subset=3):
    n, c, k = POOL, int(passing), int(subset)
    total = math.comb(n, k)
    counts = subset_counts(n, c, k)
    failing = math.comb(n - c, k)
    coverage = 1 - failing / total
    independent = 1 - (1 - c / n) ** k
    uniform = c / n  # a selector with no correctness signal succeeds with the pass share
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    js = np.arange(len(counts))
    colors = [PALETTE["terracotta"]] + [PALETTE["teal"]] * (len(counts) - 1)
    hatches = ["xx"] + [""] * (len(counts) - 1)
    for j, v, col, hat in zip(js, counts, colors, hatches):
        left.bar(j, v, color=col, hatch=hat, edgecolor="white", width=0.62)
        left.text(j, v + total * 0.015, str(v), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.set_xticks(js, ["0 (fails)"] + [str(j) for j in js[1:]])
    left.set_xlim(-0.6, len(counts) - 0.4)
    left.set_ylim(0, max(counts) * 1.18)
    left.set_xlabel("Passing programs inside the subset")
    left.set_ylabel(f"Number of subsets (of {total})")
    left.set_title(f"All size-{k} subsets of {n} programs, {c} passing", fontsize=11.5)
    names = ["Exact pool\ncoverage", "Independent-\ndraw formula", "Selector with\nno signal"]
    values = [coverage, independent, uniform]
    cols = [PALETTE["teal"], PALETTE["gold"], PALETTE["navy"]]
    hats = ["", "///", "..."]
    for i, (v, col, hat) in enumerate(zip(values, cols, hats)):
        right.bar(i, v, color=col, hatch=hat, edgecolor="white", width=0.62)
        right.text(i, v + 0.02, fmt(v, 3), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    right.set_xticks(range(3), names)
    right.set_xlim(-0.6, 2.6)
    right.set_ylim(0, 1.15)
    right.set_xlabel("Quantity for this one fixed pool")
    right.set_ylabel("Probability of success")
    right.set_title("Three different numbers", fontsize=11.5)
    metrics = {
        "Subsets in total": str(total),
        "Subsets with no pass": str(failing),
        "Finite-pool coverage": fmt(coverage, 4),
        "Independent-draw formula": fmt(independent, 4),
        "No-signal selector success": fmt(uniform, 2),
        "Coverage not collected by that selector": fmt(coverage - uniform, 4),
    }
    interpretation = (
        f"Coverage = 1 - C({n - c},{k}) / C({n},{k}) = 1 - {failing} / {total} = {fmt(coverage, 4)}, so "
        f"{total - failing} of the {total} subsets hold at least one pass. A selector that picks one program of the "
        f"subset with no correctness signal succeeds with probability {c} / {n} = {fmt(uniform, 2)}, which leaves "
        f"{fmt(coverage, 4)} - {fmt(uniform, 2)} = {fmt(coverage - uniform, 4)} uncollected. Putting the single-program rate "
        f"{fmt(c / n, 2)} into an independent-draw formula gives 1 - (1 - {fmt(c / n, 2)})^{k} = {fmt(independent, 4)}, "
        "a different quantity that does not equal the exact fixed-pool value."
    )
    return fig, metrics, interpretation


# Demonstration 2: oracle coverage is an information ceiling (laboratory function)

BANK = [[True, False, False], [False, True, False], [False, False, True]]
WEIGHTS = [0.2, 0.3, 0.5]


def lab_ceiling(bank_size, selector):
    matrix = BANK[:bank_size]
    if selector == "first":
        chosen = [0, 0, 0]
    else:
        chosen = [next((i for i in range(bank_size) if matrix[i][t]), 0) for t in range(3)]
    out = evaluate({
        "success_matrix": matrix, "task_weights": WEIGHTS, "selected_candidates": chosen,
        "deployment_allowed": [True, True, True], "independent_candidate_success": 0.4,
    })
    return matrix, chosen, out["metrics"]


def written_sum(flags):
    return " + ".join(f"{fmt(w, 1)} x {int(f)}" for w, f in zip(WEIGHTS, flags))


def ceiling_picture(bank_size=3, selector="first"):
    m = int(bank_size)
    matrix, chosen, lab = lab_ceiling(m, selector)
    cov, sel = lab["bank_oracle_coverage"], lab["actual_selection_success"]
    if sel > cov + 1e-12:
        raise AssertionError("selection exceeded oracle coverage")
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    for i in range(m):
        for t in range(3):
            ok = matrix[i][t]
            is_chosen = chosen[t] == i
            left.add_patch(Rectangle((t, m - 1 - i), 1, 1, facecolor="#cfe5e3" if ok else "white",
                                     edgecolor=PALETTE["ink"] if is_chosen else PALETTE["light"],
                                     linewidth=3 if is_chosen else 1,
                                     hatch=None if ok else "///"))
            word = "pass" if ok else "fail"
            text = word + (", chosen" if is_chosen else "")
            left.text(t + 0.5, m - 1 - i + 0.5, text, ha="center", va="center", fontsize=10.5, color=PALETTE["ink"]).set_bbox(
                {"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.85})
    left.set_xlim(0, 3)
    left.set_ylim(0, m)
    left.set_xticks([0.5, 1.5, 2.5], [f"Task {t + 1}\nweight {fmt(WEIGHTS[t], 1)}" for t in range(3)])
    left.set_yticks([m - 1 - i + 0.5 for i in range(m)], [f"Candidate {i + 1}" for i in range(m)])
    left.set_xlabel("Task and its share of the task distribution")
    left.set_ylabel("Candidate in the bank")
    left.set_title("Bank and the selector's choice", fontsize=11.5)
    left.grid(False)
    right.bar(0, cov, color=PALETTE["teal"], width=0.6, edgecolor="white")
    right.bar(1, sel, color=PALETTE["navy"], width=0.6, edgecolor="white")
    if cov - sel > 1e-12:
        right.bar(1, cov - sel, bottom=sel, color="white", edgecolor=PALETTE["grey"], hatch="///", width=0.6, linewidth=1)
        right.text(1, cov + 0.02, f"gap {fmt(cov - sel, 2)}", ha="center", va="bottom", fontsize=11, color=PALETTE["grey"])
        right.text(1, sel / 2 if sel > 0.12 else sel + 0.02, fmt(sel, 2), ha="center", va="center" if sel > 0.12 else "bottom",
                   fontsize=11, color="white" if sel > 0.12 else PALETTE["ink"])
    else:
        right.text(1, sel + 0.02, fmt(sel, 2), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    right.text(0, cov + 0.02, fmt(cov, 2), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    right.axhline(cov, color=PALETTE["grey"], linestyle="dashed", linewidth=1.2)
    right.set_xticks([0, 1], ["Oracle coverage\nCov", "Actual selection\nSel"])
    right.set_xlim(-0.6, 1.6)
    right.set_ylim(0, 1.18)
    right.set_xlabel("Quantity (dashed line is the ceiling)")
    right.set_ylabel("Task-weighted success")
    right.set_title("Sel can reach Cov but not pass it", fontsize=11.5)
    covered = [any(matrix[i][t] for i in range(m)) for t in range(3)]
    won = [matrix[chosen[t]][t] for t in range(3)]
    who = "always takes candidate 1" if selector == "first" else "sees the pass labels and takes a passing candidate when one exists"
    metrics = {
        "Bank size": str(m),
        "Oracle coverage Cov": fmt(cov, 2),
        "Actual selection Sel": fmt(sel, 2),
        "Cov minus Sel": fmt(cov - sel, 2),
        "Tasks with a passing candidate": f"{sum(covered)} of 3",
    }
    uncovered = 3 - sum(covered)
    no_pass = ("" if uncovered == 0 else
               " A task with no passing candidate in the bank adds nothing to Cov, whatever the selector does.")
    verdict = ("Sel equals Cov here, so this selector collects the whole ceiling." if abs(cov - sel) < 1e-12
               else "Sel is below Cov, so the bank holds successes this selector does not return.")
    interpretation = (
        f"With {m} candidate{'s' if m > 1 else ''} in the bank, Cov = {written_sum(covered)} = {fmt(cov, 2)}. The selector {who}, so "
        f"Sel = {written_sum(won)} = {fmt(sel, 2)}. Cov - Sel = {fmt(cov, 2)} - {fmt(sel, 2)} = {fmt(cov - sel, 2)}. {verdict}{no_pass}"
    )
    return fig, metrics, interpretation


# Demonstration 3: what actual selection leaves behind

REPORTED = {"Single sample": 37.7, "Mean log-probability": 44.5, "Unit-test selection": 77.5}
START_ROWS = {"single": "Single sample", "logprob": "Mean log-probability"}


def gap_picture(start="logprob", share=0.5):
    name = START_ROWS[start]
    base, ceiling = REPORTED[name], REPORTED["Unit-test selection"]
    share = float(share)
    gap = ceiling - base
    gain = share * gap
    after = base + gain
    left_over = ceiling - after
    fig, ax = new_figure(height=4.1)
    names = list(REPORTED)
    ys = {n: len(names) - 1 - i for i, n in enumerate(names)}
    for n in names:
        y, v = ys[n], REPORTED[n]
        col = PALETTE["teal"] if n == name else ("#8fa3b8" if n != "Unit-test selection" else PALETTE["navy"])
        ax.barh(y, v, height=0.56, color=col, edgecolor="white")
        if n == name:
            if gain > 1e-12:
                ax.barh(y, gain, left=v, height=0.56, color="white", edgecolor=PALETTE["gold"], hatch="///", linewidth=1.2)
            if left_over > 1e-12:
                ax.barh(y, left_over, left=after, height=0.56, color="white", edgecolor=PALETTE["grey"], linestyle="dashed", linewidth=1.2)
            tail = f"{fmt(v, 1)}" if gain < 1e-12 else f"{fmt(v, 1)} to {fmt(after, 1 if abs(after * 10 - round(after * 10)) < 1e-9 else 2)}"
            ax.text(ceiling + 1.5, y, tail, va="center", fontsize=11, color=PALETTE["ink"])
        else:
            ax.text(max(v, ceiling if n == "Unit-test selection" else 0) + 1.5, y, fmt(v, 1), va="center", fontsize=11, color=PALETTE["ink"])
    ax.axvline(ceiling, color=PALETTE["grey"], linestyle="dotted", linewidth=1.4)
    ax.set_yticks([ys[n] for n in names], names)
    ax.set_xlim(0, 118)
    ax.set_xticks([0, 20, 40, 60, 80, 100])
    ax.set_ylim(-0.6, len(names) - 0.4)
    ax.set_xlabel("Problems solved (percent; dotted line is unit-test selection)")
    ax.set_ylabel("Rule (bank of 100; single = one draw)")
    key = []
    if gain > 1e-12:
        key.append("hatched: hypothetical gain")
    if left_over > 1e-12:
        key.append("dashed outline: gap that remains")
    ax.set_title(f"Gap from {name.lower()}" + (";\n" + "; ".join(key) if key else ""), fontsize=11.5)
    ax.grid(axis="y", alpha=0)
    # Show two decimals when a one-decimal rounding would make the written subtraction false.
    d = 1 if all(abs(x * 10 - round(x * 10)) < 1e-9 for x in (after, left_over)) else 2
    metrics = {
        "Selection rule": name,
        "Delivered by the rule": fmt(base, 1),
        "Unit-test selection (reference)": fmt(ceiling, 1),
        "Gap Cov minus Sel (points)": fmt(gap, 1),
        "Hypothetical share collected": fmt(share, 2),
        "New selected success": fmt(after, d),
        "Gap that remains": fmt(left_over, d),
    }
    if start == "single":
        scale = ("A single sample is one draw with no ranking, so this gap compares one sample with unit-test selection over "
                 "100 candidates. It is shown for scale and is not the same-bank gap of a ranking rule in Equation (26.3). ")
    else:
        scale = "which is not negative, as Equation (26.3) says. "
    interpretation = (
        f"Gap = {fmt(ceiling, 1)} - {fmt(base, 1)} = {fmt(gap, 1)} points" + (", " if start != "single" else ". ") + scale +
        f"If a new selector collected a hypothetical share {fmt(share, 2)} of it, success would be {fmt(base, 1)} + "
        f"{fmt(share, 2)} x {fmt(gap, 1)} = {fmt(after, d)}, leaving {fmt(ceiling, 1)} - {fmt(after, d)} = {fmt(left_over, d)} points. "
        "The collected share is a what-if for planning, not a result: it becomes a result only when a selector is built and "
        "measured on the same bank, tasks and evaluator."
    )
    return fig, metrics, interpretation


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


def saturation_picture(family="exp", horizon=100):
    horizon = float(horizon)
    fits = {key: _fit(key) for key in FAMILIES}
    p, b, a, curve = fits[family]
    ks = np.geomspace(5, horizon, 160)
    ends = sorted(FAMILIES, key=lambda key: fits[key][3](horizon))
    RANK_SHIFT = {key: shift for key, shift in zip(ends, (-7, 0, 7))}
    fig, ax = new_figure(height=4.3)
    for key, (name, _, _) in FAMILIES.items():
        pk, bk, ak, ck = fits[key]
        chosen = key == family
        col = PALETTE["teal"] if chosen else PALETTE["grey"]
        style = "solid" if chosen else DASHES[key]
        ax.plot(ks, [ck(k) for k in ks], color=col, linewidth=2.6 if chosen else 1.4, linestyle=style)
        label_point(ax, horizon * 1.06, ck(horizon), name.split()[0].lower(), color=col, dx=0, dy=RANK_SHIFT[key], ha="left", va="center")
        ax.axhline(ak, color=col, linewidth=1.2 if chosen else 0.8, linestyle="dotted")
        label_point(ax, 5.3, ak, f"{name.split()[0].lower()} limit {fmt(ak, 2)}", color=PALETTE["teal"] if chosen else PALETTE["grey"],
                    dx=0, dy=4, ha="left", va="bottom")
    ax.plot([k for k, _ in OBS], [c for _, c in OBS], "o", color=PALETTE["ink"], markersize=9, zorder=5)
    for k, c in OBS:
        label_point(ax, k, c, f"({fmt(k, 0)}, {fmt(c, 2)})", color=PALETTE["ink"], dx=6, dy=-8, ha="left", va="top").set_bbox(BOX)
    ax.set_xscale("log")
    ax.set_xlim(5, horizon * 3.2)
    ax.set_ylim(0.2, 0.97)
    ax.set_xlabel("Candidates per task, k (log scale; dots are the three observed points)")
    ax.set_ylabel("Coverage")
    ax.set_title(f"{FAMILIES[family][0]} fitted exactly through three points", fontsize=11.5)
    asymptotes = {key: fits[key][2] for key in FAMILIES}
    spread = max(asymptotes.values()) - min(asymptotes.values())
    at_h = curve(horizon)
    metrics = {
        "Family": FAMILIES[family][0],
        f"Shape parameter ({FAMILIES[family][1]})": fmt(p, 2 if family != "exp" else 1),
        "Projected limit A": fmt(a, 3),
        f"Curve at k = {fmt(horizon, 0)}": fmt(at_h, 3),
        "Limits of all three families": " / ".join(fmt(asymptotes[k], 2) for k in ("exp", "hyp", "pow")),
        "Spread of the limits (points)": fmt(100 * spread, 0),
    }
    if family == "exp":
        calc = f"A = 0.63 + B x e^(-50/{fmt(p, 1)}) = 0.63 + {fmt(b, 3)} x {fmt(math.exp(-50 / p), 4)} = {fmt(a, 3)}"
    elif family == "hyp":
        calc = f"A = 0.63 + B / (50 + h) = 0.63 + {fmt(b, 3)} / (50 + {fmt(p, 2)}) = {fmt(a, 3)}"
    else:
        calc = f"A = 0.63 + B x 50^(-a) = 0.63 + {fmt(b, 3)} x {fmt(50 ** (-p), 4)} = {fmt(a, 3)}"
    interpretation = (
        f"{calc}. At k = {fmt(horizon, 0)} this curve reads {fmt(at_h, 3)}. The three families all pass through "
        f"0.40, 0.55 and 0.63, yet their limits are {fmt(asymptotes['exp'], 2)}, {fmt(asymptotes['hyp'], 2)} and "
        f"{fmt(asymptotes['pow'], 2)}, a spread of {fmt(asymptotes['pow'], 2)} - {fmt(asymptotes['exp'], 2)} = {fmt(spread, 2)}. "
        "The observed range cannot choose among them, so the limit is a forecast that depends on the family, not an observed result."
    )
    return fig, metrics, interpretation


CHAPTER = {
    "number": 26,
    "title": "How Much More Could the System Become?",
    "subtitle": "A finite bank of candidates sets a conditional ceiling, and the gap to what a selector actually returns is an engineering question, not a forecast.",
    "summary": (
        "These four demonstrations follow the chapter's staged argument. A bank of candidates is a finite object with an exact "
        "coverage calculation. Coverage is a ceiling that no selector can pass, and the gap below it shows what selection still "
        "leaves behind. A curve fitted to a few points projects a limit that depends on the curve you pick."
    ),
    "demos": [
        {
            "id": "C26-D01",
            "title": "A bank is a finite object",
            "question": "For one fixed pool of ten programs, how often does a random subset contain a pass, and how does that differ from an independent-draw guess?",
            "equations": [EQ_COVERAGE],
            "symbols": (
                "n is the number of programs generated for one task (10 here) and c the number that pass its tests. k is the size "
                "of the subset considered. C(n, k) counts the ways to choose k of n programs. The fraction C(n - c, k) / C(n, k) "
                "is the share of subsets with no pass, so one minus it is the chance a subset holds at least one pass. The "
                "full equation averages this over tasks; this demonstration shows one task."
            ),
            "prediction": "With 2 passing programs among 10 and subsets of size 3, is the exact coverage above or below the independent-draw value 0.488?",
            "explanation": (
                "Count the subsets with no pass, divide by all subsets, and subtract from one. This is exact for the fixed pool, "
                "because subsets are drawn without replacement from programs that already exist. The independent-draw formula "
                "treats every pick as a fresh draw with the pool's pass rate, which is a different statistical question. A "
                "selector with no correctness signal succeeds only at the pass share c / n."
            ),
            "application": (
                "When a report gives a pass@k (coverage at k) number, ask for the pool size n, the per-task pass counts and the subset "
                "size k. Without them you cannot tell whether the number is an exact pool calculation or an extrapolation."
            ),
            "assumptions": (
                "One task, one pool of ten programs, labels fixed by the declared tests, subsets chosen uniformly without "
                "replacement. The result says nothing about programs outside the pool, other prompts or temperatures, or "
                "adaptive retries. If the ten programs repeat one wrong approach, the labels may be strongly correlated, and "
                "the pool still has exactly this coverage but little useful variety."
            ),
            "check": "If only 1 of the 10 programs passes and k = 4, what is the exact coverage?",
            "answer": "1 - C(9,4) / C(10,4) = 1 - 126 / 210 = 0.40, which equals k / n = 4 / 10.",
            "provenance": "Constructed example: the book's ten-candidate worked subset calculation (2 passing, size 3) with the passing count and subset size varied.",
            "source_section": "Stage two: a bank is a finite object",
            "source_anchor": "stage-two-a-bank-is-a-finite-object",
            "controls": [
                {"key": "passing", "label": "Passing programs in the pool of 10", "values": [1, 2, 3, 4], "default": 2},
                {"key": "subset", "label": "Subset size k", "values": [3, 5], "default": 3},
            ],
            "function": "finite_pool_picture",
        },
        {
            "id": "C26-D02",
            "title": "Coverage is a ceiling for selection",
            "question": "Can any selector return a correct candidate more often than the bank contains one?",
            "equations": [EQ_CEILING],
            "symbols": (
                "Cov is oracle coverage: the weighted share of tasks for which at least one candidate in the bank passes. Sel is the "
                "weighted share of tasks for which the selector's chosen candidate passes. The weights are the task distribution "
                "(0.2, 0.3, 0.5). An oracle selector is shown the pass labels; a plain selector is not."
            ),
            "prediction": "With all three candidates in the bank, does the selector that always takes candidate 1 reach the ceiling? What is its Sel?",
            "explanation": (
                "For each task the ceiling is 1 if any candidate passes and 0 otherwise, and a chosen candidate can pass only if one "
                "exists. So task by task the selector's result cannot exceed the ceiling, and the weighted sums keep that order. "
                "Shrinking the bank lowers the ceiling itself, because a task with no passing candidate cannot be rescued by selection."
            ),
            "application": (
                "Before buying a better ranker, compute coverage on the bank you already have. If coverage is low, the "
                "generator, its context or its tools are the limit, and a stronger selector cannot fix that."
            ),
            "assumptions": (
                "A three-task bank with one specialist candidate per task, fixed task weights, and pass labels from one evaluator. "
                "The oracle selector uses information a deployed system may not have. The ceiling holds only for this bank and "
                "evaluator; a new candidate or a different evaluator changes the object being bounded."
            ),
            "check": "If only the heavy task (weight 0.5) were solved by anything in the bank, what is the largest Sel any selector could reach?",
            "answer": "Cov = 0.2 x 0 + 0.3 x 0 + 0.5 x 1 = 0.5, so Sel is at most 0.5 for every selector.",
            "provenance": "Constructed example: the laboratory's three-task candidate bank, computed with the laboratory's own bank-ceiling function.",
            "source_section": "Stage three: oracle coverage is an information ceiling",
            "source_anchor": "stage-three-oracle-coverage-is-an-information-ceiling",
            "controls": [
                {"key": "bank_size", "label": "Candidates in the bank", "values": [1, 2, 3], "default": 3},
                {"key": "selector", "label": "Selector", "values": ["first", "oracle"], "default": "first",
                 "value_labels": ["Always takes candidate 1", "Oracle: sees the pass labels"]},
            ],
            "function": "ceiling_picture",
        },
        {
            "id": "C26-D03",
            "title": "What actual selection leaves behind",
            "question": "How large is the gap between a practical selection rule and selection by unit tests, and what would a partial fix be worth?",
            "equations": [EQ_GAP],
            "symbols": (
                "Cov(k) is the success when the unit tests choose among k candidates and Sel(k) the success of the practical rule, "
                "both in percent of problems solved. The gap Cov minus Sel is measured in percentage points. The share collected "
                "is a hypothetical fraction of that gap that a new selector might win back."
            ),
            "prediction": "Starting from mean log-probability selection, how many points of the gap would collect half of it?",
            "explanation": (
                "The chapter reports one experiment with 100 candidates per problem: 37.7 percent for a single sample, 44.5 percent "
                "for choosing by mean log-probability, and 77.5 percent when unit tests choose. Subtract the practical rule from the "
                "unit-test result to get the gap, which cannot be negative. A hypothetical share of that gap shows how much room a "
                "better selector could address, without claiming it will."
            ),
            "application": (
                "Report delivered selection and the same-bank unit-test result side by side. A large gap points at validation or "
                "evidence; a small gap points back at generation or budget."
            ),
            "assumptions": (
                "The three percentages are the chapter's reported figures for one experiment, used as given and not re-measured here, "
                "and they hold only for that generator, bank and tests. The collected share is a planning what-if with no data behind "
                "it. Collecting any of the gap needs evidence available before the outcome is known, which a deployment may not have."
            ),
            "check": "A practical selector reaches 50.0 percent against 77.5 for unit tests. A new verifier is hoped to collect 40 percent of the gap. What is the new success?",
            "answer": "Gap = 77.5 - 50.0 = 27.5. New success = 50.0 + 0.4 x 27.5 = 61.0, a hypothesis until measured.",
            "provenance": "Constructed example: the chapter's reported Codex-S percentages used as given; the collected share is a hypothetical value defined for this reader.",
            "source_section": "Stage four: what actual selection leaves behind",
            "source_anchor": "stage-four-what-actual-selection-leaves-behind",
            "controls": [
                {"key": "start", "label": "Practical selection rule", "values": ["single", "logprob"], "default": "logprob",
                 "value_labels": ["Single sample (37.7, one draw, shown for scale)", "Mean log-probability (44.5)"]},
                {"key": "share", "label": "Hypothetical share of the gap collected", "values": [0, 0.25, 0.5, 1.0], "default": 0.5,
                 "value_labels": ["0", "0.25", "0.5", "1.0"]},
            ],
            "function": "gap_picture",
        },
        {
            "id": "C26-D04",
            "title": "A saturation forecast depends on the curve",
            "question": "If three observed coverage points are fitted by three different curves, do they agree about the limit?",
            "equations": [EQ_EXP, EQ_HYP, EQ_POW],
            "symbols": (
                "k is the number of candidates per task and the curve value is coverage. A is the limit the curve approaches. The three formulas, in order, are the "
                "exponential, hyperbolic and power-law families, and e is Euler's number (about 2.718). A, B and the shape number "
                "(tau, h or a) are all fitted so that each curve passes exactly through the three observed points "
                "(10, 0.40), (25, 0.55) and (50, 0.63). Each family has its own formula for how fast coverage approaches A."
            ),
            "prediction": "All three curves hit the same three points. Which family projects the highest limit?",
            "explanation": (
                "Three points fix three numbers, so every family fits them with no error. Beyond the observed range the families "
                "separate, and their limits come out near 0.65, 0.74 and 0.86. The data cannot say which family is right, so the "
                "limit reflects the choice of curve."
            ),
            "application": (
                "Use a saturation curve to plan capacity inside a stated budget, and report the fitted family with it. Do not read "
                "its limit as a bound on what a changed prompt, tool or generator could reach."
            ),
            "assumptions": (
                "The chapter's constructed fixed-generator saturation curve: three made-up coverage points on one declared task "
                "bank. With more points or a physical reason for one family, the choice could narrow, but this example has neither. "
                "A changed generator, selector or task distribution gives a different curve, so no limit here is a bound on an open design space."
            ),
            "check": "Two fits agree on all three points but project limits of 0.65 and 0.86. By how much do they differ?",
            "answer": "0.86 - 0.65 = 0.21, a spread of 21 points that the three observed points cannot resolve.",
            "provenance": "Constructed example: the chapter's constructed coverage points (0.40, 0.55, 0.63 at 10, 25, 50 samples) fitted exactly by three curve families.",
            "source_section": "A saturation forecast",
            "source_anchor": "a-saturation-forecast",
            "controls": [
                {"key": "family", "label": "Highlighted curve family", "values": ["exp", "hyp", "pow"], "default": "exp",
                 "value_labels": ["Exponential approach", "Hyperbolic approach", "Power-law approach"]},
                {"key": "horizon", "label": "Plot out to k =", "values": [100, 1000], "default": 100},
            ],
            "function": "saturation_picture",
        },
    ],
}

"""Chapter 1 reader: When a Score Becomes a Skill.

Four demonstrations built on Equations (1.2) to (1.4) and the chapter's
elasticity remark. Demonstration 1 calls the laboratory's own threshold
function (math_ai_agents.chapters.ch01.evaluate), so the reader, the notebook
and the chapter skill agree. Demonstrations 2 to 4 are computed directly from
the chapter's arithmetic. Every number is a constructed teaching value; the
probabilities 0.45, 0.35 and 0.20 in Demonstration 2 and the per-token values
in Demonstrations 3 and 4 are the book's own worked numbers.
"""
import math

import numpy as np
from matplotlib.ticker import NullFormatter

from math_ai_agents.chapters.ch01 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}

EQ_SCORE = r"\widehat U_{\mathcal V}(\{\theta\})=\frac{1}{n}\sum_{i=1}^{n}\mathbf{1}\{\operatorname{eval}_\tau(\hat z_i)=1\}"
EQ_PIPELINE = (r"K_\theta(z\mid c)\longrightarrow\hat z=\operatorname{dec}\bigl(K_\theta(\cdot\mid c)\bigr)"
               r"\longrightarrow y=\operatorname{eval}_\tau(\hat z,c)")
EQ_POWER = r"U=q^{n},\qquad\text{so}\qquad\log U = n\log q"
EQ_SLOPE = r"nq^{n-1}"


# Demonstration 1: the same scores under a moving cutoff

DATASETS = {
    "gradual": {"scales": [1, 2, 3, 4, 5], "scores": [0.42, 0.46, 0.49, 0.52, 0.56],
                "name": "five checkpoints, gradual rise", "xlabel": "Checkpoint scale (constructed units)"},
    "steep": {"scales": [10, 20, 40, 80], "scores": [0.1, 0.3, 0.6, 0.8],
              "name": "four checkpoints, larger total rise", "xlabel": "Checkpoint scale (constructed units)"},
}


CUTOFF_OPTIONS = (0.45, 0.5, 0.55, 0.6)


def first_pass_at(scales, scores, cutoff):
    """First scale whose score reaches the cutoff, using the laboratory's own threshold function."""
    flags = evaluate({"scales": scales, "scores": scores, "threshold": float(cutoff)})["metrics"]["thresholded_scores"]
    return next((scales[i] for i, f in enumerate(flags) if f), None)


def cutoff_picture(dataset="gradual", cutoff=0.5):
    data = DATASETS[dataset]
    scales, scores = data["scales"], data["scores"]
    out = evaluate({"scales": scales, "scores": scores, "threshold": float(cutoff)})
    flags = out["metrics"]["thresholded_scores"]
    crossings = out["metrics"]["crossing_count"]
    slopes = [(scores[i] - scores[i - 1]) / (scales[i] - scales[i - 1]) for i in range(1, len(scores))]
    biggest = int(np.argmax(slopes)) + 1
    rises = [scores[i] - scores[i - 1] for i in range(1, len(scores))]
    largest_rise = max(rises)
    first = next((scales[i] for i, f in enumerate(flags) if f), None)

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.plot(scales, scores, "-o", color=PALETTE["teal"], markersize=7)
    left.axhline(cutoff, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.6)
    lo, hi = (0.35, 0.65) if dataset == "gradual" else (0.0, 0.9)
    left.set_ylim(lo, hi)
    pad = (scales[-1] - scales[0]) * 0.04
    left.set_xlim(scales[0] - pad, scales[-1] + pad)
    label_point(left, scales[0] - pad, cutoff, f"cutoff {fmt(cutoff, 2)}", color=PALETTE["terracotta"], dx=4, dy=4 if dataset == "gradual" else 4, ha="left").set_bbox(BOX)
    # Keep the "graded score" label off the dashed cutoff line: below the second point unless the line runs through
    # that band, and then above and left of the third point.
    band = 30 * (hi - lo) / 250
    if scores[1] - band <= cutoff <= scores[1] + 0.005:
        label_point(left, scales[2], scores[2], "graded score", color=PALETTE["teal"], dx=-8, dy=10, ha="right", va="bottom").set_bbox(BOX)
    else:
        label_point(left, scales[1], scores[1], "graded score", color=PALETTE["teal"], dx=8, dy=-12, ha="left", va="top").set_bbox(BOX)
    left.set_xticks(scales)
    right_ticks = scales
    left.set_xlabel(data["xlabel"])
    left.set_ylabel("Graded score")
    left.set_title("What the model produced", fontsize=11.5)

    passed = [i for i, f in enumerate(flags) if f]
    failed = [i for i, f in enumerate(flags) if not f]
    right.step(scales, flags, where="post", color=PALETTE["grey"], linewidth=1.2, alpha=0.6)
    right.plot([scales[i] for i in passed], [1] * len(passed), "s", color=PALETTE["navy"], markersize=9)
    right.plot([scales[i] for i in failed], [0] * len(failed), "o", markerfacecolor="white", markeredgecolor=PALETTE["grey"], markeredgewidth=1.8, markersize=9)
    right.set_yticks([0, 1], ["fail (0)", "pass (1)"])
    right.set_ylim(-0.25, 1.3)
    right.set_xticks(scales)
    right.set_xlim(scales[0] - pad, scales[-1] + pad)
    if first is None:
        label_point(right, (scales[0] + scales[-1]) / 2, 0, "no checkpoint passes", color=PALETTE["ink"], dx=0, dy=14, ha="center").set_bbox(BOX)
    else:
        label_point(right, first, 1, f"first pass at scale {first}", color=PALETTE["navy"], dx=-8 if first > scales[1] else 8, dy=12, ha="right" if first > scales[1] else "left").set_bbox(BOX)
    right.set_xlabel(data["xlabel"])
    right.set_ylabel("Reported verdict")
    right.set_title("What the cutoff reports", fontsize=11.5)

    pass_text = "".join(str(f) for f in flags)
    steps = ", ".join(f"{fmt(s, 2)} {'>=' if f else '<'} {fmt(cutoff, 2)} gives {f}" for s, f in zip(scores, flags))
    total = " + ".join(str(f) for f in flags)
    j = biggest
    slope_calc = (f"({fmt(scores[j], 2)} - {fmt(scores[j - 1], 2)}) / ({scales[j]} - {scales[j - 1]}) = {fmt(slopes[j - 1], 3)}")
    idx = flags.index(1) if 1 in flags else None
    if first is None:
        verdict = ("The cutoff sits above every score, so the verdict never leaves fail and the reported curve is flat. "
                   "No jump appears because no score reaches the line; the graded scores are still rising.")
        first_text = "undefined (no checkpoint passes)"
    elif idx == 0:
        verdict = "Every checkpoint passes, so the verdict never changes; the graded scores still rise."
        first_text = str(first)
    else:
        step_size = scores[idx] - scores[idx - 1]
        if math.isclose(step_size, largest_rise, abs_tol=1e-9):
            size_note = "the largest rise between neighbouring checkpoints in this set"
        else:
            size_note = f"against {fmt(largest_rise, 2)} for the largest rise between neighbouring checkpoints in this set"
        verdict = (f"The verdict jumps from fail to pass once, between scale {scales[idx - 1]} and scale {first}, "
                   f"where the graded score moved by {fmt(step_size, 2)}, {size_note}.")
        first_text = str(first)
    firsts = {first_pass_at(scales, scores, c) for c in CUTOFF_OPTIONS}
    if len(firsts) > 1:
        closing = ("Move the cutoff and the place where the skill seems to arrive moves with it, while the scores stay put.")
    else:
        only = next(iter(firsts))
        where = "no checkpoint" if only is None else f"scale {only}"
        closing = (f"Every cutoff offered here ({fmt(CUTOFF_OPTIONS[0], 2)} to {fmt(CUTOFF_OPTIONS[-1], 2)}) gives the same first "
                   f"pass, {where}, so this score set does not show the effect")
        far = first_pass_at(scales, scores, 0.7)
        if far != only and far is not None:
            closing += f"; a cutoff of 0.70 would move the first pass to scale {far}."
        else:
            closing += "."
    interpretation = (f"Verdicts at cutoff {fmt(cutoff, 2)} ({steps}). Passes = {total} = {sum(flags)} of {len(flags)}. "
                      f"The steepest graded step is {slope_calc} score per scale unit. {verdict} {closing}")
    metrics = {
        "Verdicts": pass_text,
        "Checkpoints passing": f"{sum(flags)} of {len(flags)}",
        "Verdict changes between checkpoints": str(crossings),
        "First passing scale": first_text,
        "Steepest graded step": f"{fmt(slopes[j - 1], 3)} per scale unit",
    }
    return fig, metrics, interpretation


# Demonstration 2: three places a change can enter

LAW = [("answer A", 0.45), ("answer B", 0.35), ("ask for evidence", 0.20)]
EVALUATORS = {
    "only_a": ("accepts only A", {"answer A"}),
    "evidence": ("rewards asking for evidence", {"ask for evidence"}),
    "a_or_b": ("accepts A or B", {"answer A", "answer B"}),
}


def pipeline_picture(decoder="greedy", evaluator="only_a"):
    label, accepted = EVALUATORS[evaluator]
    probs = [p for _, p in LAW]
    names = [n for n, _ in LAW]
    best = int(np.argmax(probs))
    weights = [1.0 if i == best else 0.0 for i in range(3)] if decoder == "greedy" else probs
    verdicts = [1 if n in accepted else 0 for n in names]
    contrib = [w * v for w, v in zip(weights, verdicts)]
    score = sum(contrib)

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    short = ["answer\nA", "answer\nB", "ask for\nevidence"]
    x = np.arange(3)
    for i in range(3):
        ok = verdicts[i] == 1
        left.bar(x[i], probs[i], width=0.62, color=PALETTE["teal"] if ok else "white",
                 edgecolor=PALETTE["teal"] if ok else PALETTE["grey"], hatch=None if ok else "///", linewidth=1.3)
        left.text(x[i], probs[i] + 0.02, f"{fmt(probs[i], 2)}\n{'judged success' if ok else 'judged failure'}", ha="center", va="bottom",
                  fontsize=10.5, color=PALETTE["ink"])
        if decoder == "greedy" and i == best:
            left.text(x[i], probs[i] / 2, "returned by\ngreedy", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"],
                      bbox=BOX)
    left.set_xticks(x, short)
    left.set_ylim(0, 0.72)
    left.set_xlim(-0.6, 2.6)
    left.set_xlabel("Response")
    left.set_ylabel("Probability under the model")
    left.set_title("Model law (identical in every state)", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    for i in range(3):
        right.bar(x[i], contrib[i], width=0.62, color=PALETTE["navy"] if contrib[i] > 0 else "white",
                  edgecolor=PALETTE["navy"] if contrib[i] > 0 else PALETTE["grey"], hatch=None if contrib[i] > 0 else "///", linewidth=1.3)
        right.text(x[i], contrib[i] + 0.03, fmt(contrib[i], 2), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
    right.set_xticks(x, short)
    right.set_ylim(0, 1.3)
    right.set_xlim(-0.6, 2.6)
    right.set_xlabel("Response")
    right.set_ylabel("Share of the score")
    if decoder == "greedy":
        right.set_title(f"Greedy decoding: score {fmt(score, 2)}", fontsize=11.5)
    else:
        right.set_title(f"One sampled draw: expected score {fmt(score, 2)}", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    wtxt = " + ".join(f"{fmt(w, 2)} x {v}" for w, v in zip(weights, verdicts))
    if decoder == "greedy":
        dec_sentence = f"Greedy decoding returns {names[best]}, the response with the largest probability ({fmt(probs[best], 2)})."
        output = names[best]
    else:
        dec_sentence = "One sampled draw returns A, B or a request for evidence with probabilities 0.45, 0.35 and 0.20."
        output = "A, B or evidence by chance"
    score_word = "Score" if decoder == "greedy" else "Expected score"
    interpretation = (f"{dec_sentence} The evaluator {label}. {score_word} = {wtxt} = {fmt(score, 2)}. "
                      "The probabilities 0.45, 0.35 and 0.20 are the same in all six states. Only the rule that picks an output "
                      "and the rule that judges it changed, and the reported number moved with them.")
    metrics = {
        "Model law (A, B, evidence)": "0.45, 0.35, 0.20",
        "Output returned": output,
        "Evaluator": label,
        "Expected score": fmt(score, 2),
    }
    return fig, metrics, interpretation


# Demonstration 3: exact match manufactures a cliff

STEPS = {"low": (0.90, 0.95, "0.90 to 0.95"), "high": (0.95, 0.99, "0.95 to 0.99")}


def digits_for(x):
    return 6 if x < 0.001 else 4


def exact_match(q, n):
    return q ** n


def cliff_picture(length=40, step="low"):
    q0, q1, _ = STEPS[step]
    n = int(length)
    u0, u1 = exact_match(q0, n), exact_match(q1, n)
    ratio = u1 / u0
    qs = np.linspace(0.85, 1.0, 301)
    us = qs ** n

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.plot(qs, us, color=PALETTE["teal"])
    left.plot([q0], [u0], "o", color=PALETTE["terracotta"], markersize=8)
    left.plot([q1], [u1], "s", color=PALETTE["navy"], markersize=8)
    left.set_xlim(0.85, 1.0)
    left.set_ylim(-0.04, 1.08)
    left.text(0.03, 0.96, f"\u25cf q = {fmt(q0, 2)}: U = {fmt(u0, digits_for(u0))}", transform=left.transAxes, ha="left", va="top",
              fontsize=10.5, color=PALETTE["terracotta"], bbox=BOX)
    left.text(0.03, 0.86, f"\u25a0 q = {fmt(q1, 2)}: U = {fmt(u1, digits_for(u1))}", transform=left.transAxes, ha="left", va="top",
              fontsize=10.5, color=PALETTE["navy"], bbox=BOX)
    left.set_xlabel("Per-token success probability q")
    left.set_ylabel("Exact-match score U")
    left.set_title(f"Target of {n} tokens: U = q^{n}", fontsize=11.5)

    right.plot(qs, us, color=PALETTE["teal"])
    right.plot([q0], [u0], "o", color=PALETTE["terracotta"], markersize=8)
    right.plot([q1], [u1], "s", color=PALETTE["navy"], markersize=8)
    right.set_yscale("log")
    right.set_xlim(0.85, 1.0)
    right.set_ylim(us.min() / 3, 1.15)
    if us.min() > 0.05:
        # A short target never leaves the top decade: label plain probabilities, never values above one.
        right.set_yticks([0.2, 0.3, 0.5, 1.0], ["0.2", "0.3", "0.5", "1"])
        right.yaxis.set_minor_formatter(NullFormatter())
    right.set_xlabel("Per-token success probability q")
    right.set_ylabel("Exact-match score U (log scale)")
    right.set_title("Same curve, logarithmic axis", fontsize=11.5)
    right.text(0.97, 0.05, f"\u25cf to \u25a0: factor {fmt(ratio, 1)}", transform=right.transAxes, ha="right", va="bottom",
               fontsize=10.5, color=PALETTE["ink"], bbox=BOX)

    metrics = {
        f"Score at q = {fmt(q0, 2)}": fmt(u0, digits_for(u0)),
        f"Score at q = {fmt(q1, 2)}": fmt(u1, digits_for(u1)),
        "Gain per token": f"{fmt((q1 - q0) * 100, 0)} percentage points",
        "Gain in task score": f"a factor of {fmt(ratio, 1)}",
        "Expected passes in 100 trials": f"{fmt(100 * u0, 1)} then {fmt(100 * u1, 1)}",
    }
    e0, e1 = 100 * u0, 100 * u1
    if max(e0, e1) < 1:
        trials = (f"Over 100 trials the expected passes are {fmt(e0, 1)} then {fmt(e1, 1)}, both under one, so the observed counts "
                  "would be small and hard to tell apart, and a flat observed curve here is not proof that nothing improved.")
    elif e1 - e0 >= 5:
        trials = (f"Over 100 trials the expected passes are {fmt(e0, 1)} then {fmt(e1, 1)}, which differ by {fmt(e1 - e0, 1)}, "
                  "so the improvement is not hidden by low scores.")
    else:
        trials = (f"Over 100 trials the expected passes are {fmt(e0, 1)} then {fmt(e1, 1)}, which differ by only "
                  f"{fmt(e1 - e0, 1)}, so 100 trials may not separate the two models.")
    interpretation = (f"{fmt(q0, 2)}^{n} = {fmt(u0, digits_for(u0))} and {fmt(q1, 2)}^{n} = {fmt(u1, digits_for(u1))}, so the ratio is "
                      f"{fmt(u1, digits_for(u1))} / {fmt(u0, digits_for(u0))} = {fmt(ratio, 1)}. The model gained "
                      f"{fmt((q1 - q0) * 100, 0)} points per token, yet the exact-match score changed by a factor of {fmt(ratio, 1)}. "
                      "The scores are rounded for display and the ratio is computed from the unrounded values. "
                      f"A short target amplifies a gain less than a long target does. {trials}")
    return fig, metrics, interpretation


# Demonstration 4: elasticity of the score with respect to q

Q_START = 0.90


def elasticity_picture(length=40, rise=0.01):
    n = int(length)
    r = float(rise)
    q0 = Q_START
    q1 = q0 * (1 + r)
    u0, u1 = q0 ** n, q1 ** n
    exact = u1 / u0 - 1
    first_order = n * r
    slope0 = n * q0 ** (n - 1)
    slope1 = n * q1 ** (n - 1)
    qs = np.linspace(0.85, 1.0, 301)
    slopes = n * qs ** (n - 1)

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.plot(qs, slopes, color=PALETTE["teal"])
    left.axhline(1.0, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    left.plot([q0], [slope0], "o", color=PALETTE["terracotta"], markersize=8, label=f"start, q = {fmt(q0, 2)}")
    left.plot([q1], [slope1], "s", color=PALETTE["navy"], markersize=8, label=f"after the rise, q = {fmt(q1, 3)}")
    left.set_yscale("log")
    left.set_xlim(0.85, 1.0)
    ymin = min(slopes.min(), 1.0) / 3
    ymax = max(slopes.max(), 1.0) * 6
    left.set_ylim(ymin, ymax)
    if (1.0 / n) ** (1.0 / (n - 1)) > 0.93:
        label_point(left, 0.85, 1.0, "slope = 1", color=PALETTE["grey"], dx=4, dy=4, ha="left").set_bbox(BOX)
    else:
        label_point(left, 1.0, 1.0, "slope = 1", color=PALETTE["grey"], dx=-4, dy=-4, ha="right", va="top").set_bbox(BOX)
    label_point(left, q0, slope0, f"q = {fmt(q0, 2)}: {fmt(slope0, 3 if slope0 < 10 else 1)}", color=PALETTE["terracotta"], dx=8, dy=-12, ha="left", va="top").set_bbox(BOX)
    left.set_xlabel("Per-token success probability q")
    left.set_ylabel("Absolute slope n q^(n-1) (log scale)")
    left.set_title(f"Slope of the score, target of {n} tokens", fontsize=11.5)
    left.legend(loc="upper left", fontsize=10.5, frameon=True, framealpha=0.9)

    right.bar([0], [first_order * 100], width=0.6, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.3)
    right.bar([1], [exact * 100], width=0.6, color=PALETTE["navy"])
    top = max(first_order, exact) * 100
    right.text(0, first_order * 100 + top * 0.03, f"{fmt(first_order * 100, 0)}%", ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
    right.text(1, exact * 100 + top * 0.03, f"{fmt(exact * 100, 0)}%", ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
    right.set_xticks([0, 1], ["first-order\nn x rise", "exact\nchange in U"])
    right.set_ylim(0, top * 1.25)
    right.set_xlim(-0.6, 1.6)
    right.set_xlabel(f"Estimate of the gain in U when q rises by {fmt(r * 100, 0)}%")
    right.set_ylabel("Relative gain in task score (percent)")
    right.set_title("Rule of thumb against exact", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    gap = abs(exact - first_order) / exact
    if slope0 < 1:
        slope_note = (f"The absolute slope at q = {fmt(q0, 2)} is {fmt(slope0, 3)}, below one, so a one-point gain in q buys "
                      "less than one point of score; the relative gain is still large because the score itself is tiny.")
    else:
        slope_note = (f"The absolute slope at q = {fmt(q0, 2)} is {fmt(slope0, 2)}, above one, so here the score gains more "
                      "than one point for each point gained per token.")
    extra = fmt(exact * 100 - first_order * 100, 1)
    shown = f"{fmt(first_order * 100, 0)}% against {fmt(exact * 100, 0)}%"
    if gap <= 0.1:
        fit = (f"The first-order estimate is within 10 percent of the exact gain ({shown}): with n x rise = "
               f"{fmt(first_order, 2)}, compounding adds only {extra} percentage points.")
    else:
        fit = (f"The first-order estimate is more than 10 percent below the exact gain ({shown}): with n x rise = "
               f"{fmt(first_order, 2)}, compounding adds {extra} percentage points that the rule leaves out, because the "
               "rise is applied n times.")
    interpretation = (f"New q = {fmt(q0, 2)} x (1 + {fmt(r, 2)}) = {fmt(q1, 3)}. First-order estimate: n x rise = {n} x {fmt(r, 2)} = "
                      f"{fmt(first_order, 2)}, or {fmt(first_order * 100, 0)}%. Exact: {fmt(q1, 3)}^{n} / {fmt(q0, 2)}^{n} - 1 = "
                      f"{fmt(u1, digits_for(u1))} / {fmt(u0, digits_for(u0))} - 1 = {fmt(exact, 2)}, or {fmt(exact * 100, 0)}% "
                      f"(scores are rounded for display; the exact gain uses the unrounded values). "
                      f"{fit} {slope_note}")
    metrics = {
        "Starting score": fmt(u0, digits_for(u0)),
        "Score after the rise": fmt(u1, digits_for(u1)),
        "First-order gain (n x rise)": f"{fmt(first_order * 100, 0)}%",
        "Exact gain": f"{fmt(exact * 100, 0)}%",
        "Absolute slope at start": fmt(slope0, 3),
    }
    return fig, metrics, interpretation


CHAPTER = {
    "number": 1,
    "title": "When a Score Becomes a Skill",
    "subtitle": "A reported capability depends on the model and also on the rule that reads its outputs, so a jump on a chart can come from the ruler.",
    "summary": (
        "These four demonstrations follow the chapter's argument about measurement. The first moves a pass line over fixed "
        "scores, the second changes the rules around an unchanged model, and the last two show how raising a probability to "
        "the power of a target length turns small gains into large ones."
    ),
    "demos": [
        {
            "id": "C01-D01",
            "title": "The same scores, a moving cutoff",
            "question": "If no score changes, can moving the pass line move the place where a skill seems to arrive?",
            "equations": [EQ_SCORE],
            "symbols": (
                "z-hat_i is the output generated for prompt i and n is the number of items being scored. eval_tau(z-hat_i) is "
                "the evaluator's verdict for that output, 1 for success and 0 for failure, and tau is its cutoff. The hat on U "
                "marks an estimate: the average verdict. U with subscript V is the score under a declared evaluation contract V "
                "(task, scoring rule and evaluator settings, fixed in advance); theta is the model's parameters, and the braces "
                "list the enabled components, here only the frozen model. In this demonstration each item is a checkpoint with a "
                "graded score between 0 and 1, and the evaluator passes it when the score reaches the cutoff. A score exactly "
                "equal to the cutoff passes. A verdict change is a pair of neighbouring checkpoints where one fails and the "
                "other passes."
            ),
            "prediction": "With the gradual scores, move the cutoff from 0.50 to 0.55. At which checkpoint does the first pass appear?",
            "explanation": (
                "The graded scores on the left never change. The verdicts on the right come from comparing each score with "
                "the cutoff, as in the indicator inside Equation (1.2). A smooth rise therefore produces a sudden verdict "
                "wherever it crosses the line, and a different line puts the sudden change at a different checkpoint."
            ),
            "application": (
                "When a dashboard turns green, ask for the underlying graded scores and the cutoff behind the colour. If moving "
                "the cutoff a little moves the date of arrival, the date describes the cutoff as much as the system."
            ),
            "assumptions": (
                "The same task, output boundary and environment at every checkpoint, and scores that are exact rather than "
                "noisy estimates. Five or four constructed points cannot show whether the true curve is smooth between them. "
                "A genuinely sharp change inside the model would also produce a jump, and this picture cannot rule that out."
            ),
            "check": "With the larger-rise scores (0.1, 0.3, 0.6, 0.8 at scales 10, 20, 40, 80) and a cutoff of 0.70, which checkpoints pass, and what is the first graded step?",
            "answer": "Only the last one: 0.8 >= 0.7, while 0.6 < 0.7. The first step is (0.3 - 0.1) / (20 - 10) = 0.02 score per scale unit.",
            "provenance": "Constructed example: the five scores and the larger-rise four-score set are the laboratory's declared inputs for this chapter, computed with its threshold function.",
            "source_section": "What did change",
            "source_anchor": "what-did-change",
            "controls": [
                {"key": "dataset", "label": "Score set", "values": ["gradual", "steep"], "default": "gradual",
                 "value_labels": ["Gradual rise, five checkpoints", "Larger rise, four checkpoints (scales double)"]},
                {"key": "cutoff", "label": "Pass cutoff", "values": [0.45, 0.5, 0.55, 0.6], "default": 0.5},
            ],
            "function": "cutoff_picture",
        },
        {
            "id": "C01-D02",
            "title": "Three places a change can enter",
            "question": "If the model's probabilities never change, how much can the reported score move?",
            "equations": [EQ_PIPELINE],
            "symbols": (
                "K_theta(z | c) is the model's probability for output z given context c. dec picks one output from that law: "
                "greedy decoding takes the most probable one, sampling draws one at random according to the probabilities. "
                "eval_tau judges the chosen output, 1 for success and 0 for failure. The expected score adds up, over the "
                "responses, the chance the decoder returns each one times its verdict."
            ),
            "prediction": "Keep greedy decoding and switch the evaluator from accepting only A to rewarding a request for evidence. What happens to the score?",
            "explanation": (
                "Equation (1.3) joins three stages by two arrows: the model's law, the decoder and the evaluator. The left panel "
                "is the first stage and is frozen. The decoder decides which response is returned, and the evaluator decides "
                "which responses count. The score in the right panel combines the two, so it cannot say which stage moved."
            ),
            "application": (
                "When two reports of the same model disagree, ask which stage differs: the decoding settings or the scoring rule. "
                "Report the stage that changed, not only the final number."
            ),
            "assumptions": (
                "One prompt, three possible responses and one attempt. The probabilities are the chapter's constructed values, "
                "not measurements. Real decoders and evaluators have more settings, and several can differ at the same time."
            ),
            "check": "Suppose the model law were 0.30, 0.30 and 0.40 for A, B and evidence, and the evaluator rewards evidence. What do greedy decoding and one sampled draw score?",
            "answer": "Greedy returns evidence, the largest at 0.40, so it scores 1. One draw scores 0.30 x 0 + 0.30 x 0 + 0.40 x 1 = 0.40.",
            "provenance": "Constructed example: the chapter's constructed distribution of 0.45, 0.35 and 0.20 over three responses.",
            "source_section": "Three places a change can enter",
            "source_anchor": "three-places-a-change-can-enter",
            "controls": [
                {"key": "decoder", "label": "Decoding rule", "values": ["greedy", "sample"], "default": "greedy",
                 "value_labels": ["Greedy (most probable)", "One sampled draw"]},
                {"key": "evaluator", "label": "Evaluator", "values": ["only_a", "evidence", "a_or_b"], "default": "only_a",
                 "value_labels": ["Accepts only A", "Rewards asking for evidence", "Accepts A or B"]},
            ],
            "function": "pipeline_picture",
        },
        {
            "id": "C01-D03",
            "title": "How exact match manufactures a cliff",
            "question": "How much does a small gain per token change an exact-match score, and how does target length decide it?",
            "equations": [EQ_POWER],
            "symbols": (
                "q is the probability that one token is right, n is the number of tokens in the target, and U is the exact-match "
                "score: the probability that all n tokens are right, assuming tokens succeed independently. The logarithm form says "
                "the length n multiplies the per-token gain."
            ),
            "prediction": "For a target of 40 tokens, how many times larger is the score at q = 0.95 than at q = 0.90?",
            "explanation": (
                "Equation (1.4) multiplies q by itself n times, so a short target amplifies a gain less than a long target does, and "
                "a long target can amplify it enormously. The two panels draw the same curve on a linear and a logarithmic axis. On the logarithmic axis the "
                "vertical gap between the markers is the log of the ratio, which is n times the log of the per-token ratio."
            ),
            "application": (
                "Before reading a flat region at the start of a benchmark curve as no progress, compute what the score would be "
                "if per-token quality had improved smoothly. Then decide whether the benchmark can resolve those small values."
            ),
            "assumptions": (
                "Tokens succeed independently and each has the same probability q. Real text violates this, so the mechanism is "
                "robust but the exact factors are constructed. The expected passes in 100 trials are expected counts, not observed results."
            ),
            "check": "A coding assistant gets each line right with probability 0.90. What is the chance a 20-line function is entirely right, and how does it change at 0.99 per line?",
            "answer": "0.90^20 = 0.1216, about one in eight. 0.99^20 = 0.8179, about four in five, a factor of 0.8179 / 0.1216 = 6.7 from a nine-point gain per line.",
            "provenance": "Constructed example: the per-token values 0.90, 0.95 and 0.99 and the target lengths of Table 1.1, computed from Equation (1.4).",
            "source_section": "Why exact match manufactures a cliff",
            "source_anchor": "why-exact-match-manufactures-a-cliff",
            "controls": [
                {"key": "length", "label": "Target length n (tokens)", "values": [5, 20, 40, 100], "default": 40},
                {"key": "step", "label": "Per-token gain", "values": ["low", "high"], "default": "low",
                 "value_labels": ["q from 0.90 to 0.95", "q from 0.95 to 0.99"]},
            ],
            "function": "cliff_picture",
        },
        {
            "id": "C01-D04",
            "title": "Elasticity and slope of the exact-match score",
            "question": "Does a small relative gain in q raise the score by about n times as much, and does the slope tell the same story?",
            "equations": [EQ_POWER, EQ_SLOPE],
            "symbols": (
                "U = q^n as before, with q the per-token success probability and n the target length. The absolute slope n q^(n-1), "
                "the derivative dU/dq, is how many points of score one extra point of q buys. The elasticity is the relative change in U divided by "
                "the relative change in q, which the chapter says equals n. The rise is the relative increase in q, here "
                "starting from q = 0.90."
            ),
            "prediction": "At n = 40 and a rise of 1%, roughly how large is the relative gain in U? Is it close to the exact value?",
            "explanation": (
                "The chapter says a small relative increase in q produces about n times that relative increase in U. The right panel "
                "compares that rule of thumb with the exact change. The left panel shows the absolute slope, which can be well "
                "below one while the relative gain is large, because the score being multiplied is tiny."
            ),
            "application": (
                "Use the first-order rule to estimate how much a reliability fix per step will matter for a long chain, then check "
                "it exactly before quoting it, because the rule fails once n times the rise is no longer small."
            ),
            "assumptions": (
                "Independent steps with equal probability q, as the chapter states; the calculation applies to tokens, proof steps "
                "or tool calls only when that model applies. The first-order rule is a small-change approximation, and the panel "
                "shows where it stops working."
            ),
            "check": "With n = 20 and q rising 1% from 0.90 to 0.909, what does the first-order rule predict for the relative gain in U, and what is the exact gain?",
            "answer": "First order: 20 x 0.01 = 0.20, or 20%. Exact: 1.01^20 - 1 = 0.2202, or 22%. The two are close because n x rise is small.",
            "provenance": "Constructed example: starting value q = 0.90 and the chapter's target lengths, computed from U = q^n and its slope.",
            "source_section": "Why scale can make a model feel different",
            "source_anchor": "why-scale-can-make-a-model-feel-different",
            "controls": [
                {"key": "length", "label": "Target length n (steps)", "values": [5, 20, 40, 100], "default": 40},
                {"key": "rise", "label": "Relative rise in q", "values": [0.01, 0.05], "default": 0.01,
                 "value_labels": ["1% (0.90 to 0.909)", "5% (0.90 to 0.945)"]},
            ],
            "function": "elasticity_picture",
        },
    ],
}

"""Chapter 1 reader: When a Score Becomes a Skill.

Four demonstrations built on Equations (1.1) to (1.4), the chapter's elasticity
remark, Figure 1.2 and the six-question emergence audit. Demonstration 1 calls
the laboratory's own threshold function (math_ai_agents.chapters.ch01.evaluate),
so the reader, the notebook and the chapter skill agree. The others are computed
directly from the chapter's arithmetic. Every number is a constructed teaching
value; the probabilities 0.45, 0.35 and 0.20 in Demonstration 2, the twenty
attempts at probability 0.20 and the per-token values in Demonstration 3 are the
book's own worked numbers.
"""
import math

import numpy as np
from matplotlib.ticker import FuncFormatter, NullFormatter

from math_ai_agents.chapters.ch01 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}

EQ_LAW = r"K_\theta(z\mid c)=\Pr_\theta(Z=z\mid C=c)"
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

CUTOFF_OPTIONS = (0.5, 0.55, 0.6, 0.7)


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
    lo, hi = (0.35, 0.78) if dataset == "gradual" else (0.0, 0.9)
    left.set_ylim(lo, hi)
    pad = (scales[-1] - scales[0]) * 0.04
    left.set_xlim(scales[0] - pad, scales[-1] + pad)
    label_point(left, scales[0] - pad, cutoff, f"cutoff {fmt(cutoff, 2)}", color=PALETTE["terracotta"], dx=4, dy=4, ha="left").set_bbox(BOX)
    # Keep the "graded score" label off the dashed cutoff line: below the second point unless the line runs through
    # that band, and then above and left of the third point.
    band = 30 * (hi - lo) / 250
    if scores[1] - band <= cutoff <= scores[1] + 0.005:
        label_point(left, scales[2], scores[2], "graded score", color=PALETTE["teal"], dx=-8, dy=10, ha="right", va="bottom").set_bbox(BOX)
    else:
        label_point(left, scales[1], scores[1], "graded score", color=PALETTE["teal"], dx=8, dy=-12, ha="left", va="top").set_bbox(BOX)
    left.set_xticks(scales)
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
    comparisons = ", ".join(f"{fmt(s, 2)} {'>=' if f else '<'} {fmt(cutoff, 2)} gives {f}" for s, f in zip(scores, flags))
    total = " + ".join(str(f) for f in flags)
    j = biggest
    slope_calc = f"({fmt(scores[j], 2)} - {fmt(scores[j - 1], 2)}) / ({scales[j]} - {scales[j - 1]}) = {fmt(slopes[j - 1], 3)}"
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
            size_note = "the largest rise in score between neighbouring checkpoints in this set"
        else:
            size_note = f"against {fmt(largest_rise, 2)} for the largest rise in score between neighbouring checkpoints in this set"
        verdict = (f"The verdict jumps from fail to pass once, between scale {scales[idx - 1]} and scale {first}, "
                   f"where the graded score moved by {fmt(step_size, 2)}, {size_note}.")
        first_text = str(first)
    listing = ", ".join(f"{fmt(c, 2)} gives {'no pass' if (f := first_pass_at(scales, scores, c)) is None else 'scale ' + str(f)}"
                        for c in CUTOFF_OPTIONS)
    closing = (f"First pass for each cutoff offered on this score set: {listing}. The scores never moved; only the line did. "
               "The first-pass date moves only when the line passes over the score that first clears it; "
               "while the line stays inside a gap between scores, the date stays put.")
    interpretation = (f"Verdicts at cutoff {fmt(cutoff, 2)} ({comparisons}). Passes = {total} = {sum(flags)} of {len(flags)}. "
                      f"The largest rise per scale unit is {slope_calc} score per scale unit. {verdict} {closing}")
    metrics = {
        "Verdicts": pass_text,
        "Checkpoints passing": f"{sum(flags)} of {len(flags)}",
        "Verdict changes between checkpoints": str(crossings),
        "First passing scale": first_text,
        "Largest rise per scale unit": f"{fmt(slopes[j - 1], 3)} per scale unit",
    }
    worked = [
        "Graded scores at scales " + ", ".join(str(s) for s in scales) + ": " + ", ".join(fmt(s, 2) for s in scores) + ".",
        f"Cutoff = {fmt(cutoff, 2)}. A score passes when it is at least the cutoff; equality passes.",
        f"Verdicts: {comparisons}.",
        f"Passes = {total} = {sum(flags)} of {len(flags)}.",
        f"Largest rise per scale unit = {slope_calc} score per scale unit.",
        ("First pass: none, the cutoff is above every score." if first is None else f"First pass at scale {first}."),
    ]
    alt = (f"Left, graded scores rising across {len(scores)} checkpoints with a dashed cutoff line at {fmt(cutoff, 2)}. "
           f"Right, the verdicts {pass_text}, " + ("with no checkpoint passing." if first is None else f"first passing at scale {first}."))
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 2: three places a change can enter, plus the loop

LAWS = {"chapter": (0.45, 0.35, 0.20), "flat": (0.30, 0.30, 0.40)}
NAMES = ["answer A", "answer B", "ask for evidence"]
EVALUATORS = {
    "only_a": ("accepts only A", {"answer A"}),
    "evidence": ("rewards asking for evidence", {"ask for evidence"}),
}
ATTEMPTS = 20


def small(x):
    """Decimals that keep tiny probabilities visible in a written calculation."""
    return fmt(x, 6 if x < 0.0005 else 4)


def pipeline_picture(decoder="greedy", evaluator="only_a", law="chapter"):
    label, accepted = EVALUATORS[evaluator]
    probs = list(LAWS[law])
    best = int(np.argmax(probs))
    verdicts = [1 if n in accepted else 0 for n in NAMES]
    p_accept = sum(p for p, v in zip(probs, verdicts) if v)
    law_text = ", ".join(fmt(p, 2) for p in probs)

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
            left.text(x[i], probs[i] / 2, "returned by\ngreedy", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
    left.set_xticks(x, short)
    left.set_ylim(0, 0.72)
    left.set_xlim(-0.6, 2.6)
    left.set_xlabel("Response")
    left.set_ylabel("Probability under the model")
    left.set_title("Model law, Equation (1.1)", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    if decoder == "attempts":
        ks = np.arange(1, ATTEMPTS + 1)
        curve = 1 - (1 - p_accept) ** ks
        score = 1 - (1 - p_accept) ** ATTEMPTS
        right.plot(ks, curve, "-o", color=PALETTE["navy"], markersize=4.5)
        right.set_xlim(0.5, ATTEMPTS + 0.5)
        right.set_ylim(0, 1.18)
        right.set_xticks([1, 5, 10, 15, 20])
        label_point(right, 1, curve[0], f"one attempt: {fmt(curve[0], 2)}", color=PALETTE["ink"], dx=8, dy=8, ha="left", va="bottom").set_bbox(BOX)
        label_point(right, ATTEMPTS, curve[-1], f"20 attempts: {fmt(score, 2)}", color=PALETTE["navy"], dx=-6, dy=-14, ha="right", va="top").set_bbox(BOX)
        right.set_xlabel("Number of attempts allowed")
        right.set_ylabel("Chance that some attempt is judged a success")
        right.set_title(f"Twenty attempts, any one may pass: {fmt(score, 2)}", fontsize=11.5)
        weights = None
    else:
        weights = [1.0 if i == best else 0.0 for i in range(3)] if decoder == "greedy" else probs
        contrib = [w * v for w, v in zip(weights, verdicts)]
        score = sum(contrib)
        for i in range(3):
            right.bar(x[i], contrib[i], width=0.62, color=PALETTE["navy"] if contrib[i] > 0 else "white",
                      edgecolor=PALETTE["navy"] if contrib[i] > 0 else PALETTE["grey"], hatch=None if contrib[i] > 0 else "///", linewidth=1.3)
            right.text(x[i], contrib[i] + 0.03, fmt(contrib[i], 2), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        right.set_xticks(x, short)
        right.set_ylim(0, 1.3)
        right.set_xlim(-0.6, 2.6)
        right.set_xlabel("Response")
        right.set_ylabel("Share of the score")
        right.grid(axis="x", alpha=0)
        if decoder == "greedy":
            right.set_title(f"Greedy decoding: score {fmt(score, 2)}", fontsize=11.5)
        else:
            right.set_title(f"One sampled draw: expected score {fmt(score, 2)}", fontsize=11.5)

    if decoder == "greedy":
        dec_sentence = f"Greedy decoding returns {NAMES[best]}, the response with the largest probability ({fmt(probs[best], 2)})."
        output = NAMES[best]
        wtxt = " + ".join(f"{fmt(w, 2)} x {v}" for w, v in zip(weights, verdicts))
        calc = f"Score = {wtxt} = {fmt(score, 2)}."
    elif decoder == "sample":
        dec_sentence = f"One sampled draw returns A, B or a request for evidence with probabilities {law_text}."
        output = "A, B or evidence by chance"
        wtxt = " + ".join(f"{fmt(w, 2)} x {v}" for w, v in zip(weights, verdicts))
        calc = f"Expected score = {wtxt} = {fmt(score, 2)}."
    else:
        dec_sentence = (f"The controller may try up to {ATTEMPTS} independent attempts and counts a success if any attempt passes; "
                        f"one attempt passes with probability {fmt(p_accept, 2)}, the total probability of the responses this evaluator accepts.")
        output = "up to 20 independent draws"
        calc = (f"Score = 1 - (1 - {fmt(p_accept, 2)})^{ATTEMPTS} = 1 - {small((1 - p_accept) ** ATTEMPTS)} = {small(score)}.")
    if decoder == "attempts":
        tail = ("The model law is the same in every state. The loop around the model, a decision made outside the network, "
                "changed what the same law is worth.")
    else:
        tail = (f"The model law ({law_text}) is the same for every decoder and evaluator choice in this law setting. "
                "Only the rule that picks an output and the rule that judges it changed, and the reported number moved with them.")
    interpretation = f"{dec_sentence} The evaluator {label}. {calc} {tail}"
    score_key = "Score" if decoder != "sample" else "Expected score"
    metrics = {
        "Model law (A, B, evidence)": law_text,
        "Output returned": output,
        "Evaluator": label,
        score_key: fmt(score, 2),
    }
    verdict_text = ", ".join(f"{n} {v}" for n, v in zip(["A", "B", "evidence"], verdicts))
    worked = [
        f"Model law for A, B, evidence: {law_text}. It does not change with the decoder or the evaluator.",
        dec_sentence,
        f"The evaluator {label}: verdicts {verdict_text}.",
        calc,
    ]
    alt = (f"Left, bars for the model law {law_text} marking which responses are judged successes. "
           + ("Right, the chance that some attempt passes rising from one attempt to twenty attempts."
              if decoder == "attempts" else f"Right, the share of the score each response contributes, total {fmt(score, 2)}."))
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 3: exact match manufactures a cliff

STEPS = {"low": (0.90, 0.95), "high": (0.95, 0.99), "wide": (0.90, 0.99)}
LENGTHS = (5, 20, 40, 100)
CURVE_COLORS = {5: PALETTE["olive"], 20: PALETTE["gold"], 40: PALETTE["teal"], 100: PALETTE["terracotta"]}


def digits_for(x):
    return 6 if x < 0.001 else 4


def factor_formatter(v, _):
    return f"{v:g}"


def cliff_picture(length=40, step="low"):
    q0, q1 = STEPS[step]
    n = int(length)
    u0, u1 = q0 ** n, q1 ** n
    ratio = u1 / u0
    qs = np.linspace(0.85, 1.0, 301)
    rise = round(q1 / q0 - 1, 4)
    first_order = 1 + n * rise
    slope0 = n * q0 ** (n - 1)
    slope1 = n * q1 ** (n - 1)
    avg_slope = (u1 - u0) / (q1 - q0)
    log_ratio = n * math.log(q1 / q0)

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    for m in LENGTHS:
        chosen = m == n
        left.plot(qs, qs ** m, color=CURVE_COLORS[m], linewidth=2.8 if chosen else 1.2, alpha=1 if chosen else 0.55,
                  label=f"n = {m}" + (" (selected)" if chosen else ""))
    left.plot([q0], [u0], "o", color=PALETTE["ink"], markersize=8, zorder=5)
    left.plot([q1], [u1], "s", color=PALETTE["ink"], markersize=8, zorder=5)
    left.set_xlim(0.85, 1.0)
    left.set_ylim(-0.04, 1.08)
    low_first = u0 < 0.12
    label_point(left, q0, u0, f"U = {fmt(u0, digits_for(u0))}", color=PALETTE["ink"], dx=0 if low_first else 6, dy=10 if low_first else -10,
                ha="center" if low_first else "left", va="bottom" if low_first else "top").set_bbox(BOX)
    if u1 < 0.12:
        end = dict(dx=8, dy=10, ha="left", va="bottom")
    elif u1 > 0.5:
        end = dict(dx=-8, dy=-12, ha="right", va="top")
    else:
        end = dict(dx=-8, dy=10, ha="right", va="bottom")
    label_point(left, q1, u1, f"U = {fmt(u1, digits_for(u1))}", color=PALETTE["ink"], **end).set_bbox(BOX)
    left.set_xlabel("Per-token success probability q")
    left.set_ylabel("Exact-match score U = q^n")
    left.set_title("Four target lengths, one marked step", fontsize=11.5)
    left.legend(loc="upper left", fontsize=10.5, frameon=True, framealpha=0.9)

    right.bar([0], [first_order], width=0.6, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.3)
    right.bar([1], [ratio], width=0.6, color=PALETTE["navy"])
    right.set_yscale("log")
    top = max(first_order, ratio)
    right.set_ylim(0.8, top * 4)
    pool = (1, 10, 100, 1000, 10000, 100000) if top > 100 else (1, 2, 3, 5, 10, 20, 30, 50, 100)
    ticks = [t for t in pool if 0.8 <= t <= top * 4]
    right.set_yticks(ticks)
    right.yaxis.set_major_formatter(FuncFormatter(factor_formatter))
    right.yaxis.set_minor_formatter(NullFormatter())
    right.text(0, first_order * 1.15, f"{fmt(first_order, 1)}x", ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
    right.text(1, ratio * 1.15, f"{fmt(ratio, 1)}x", ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
    right.set_xticks([0, 1], ["first-order\n1 + n x rise", "exact\nU1 / U0"])
    right.set_xlim(-0.6, 1.6)
    right.set_xlabel(f"Score multiple when q goes from {fmt(q0, 2)} to {fmt(q1, 2)}")
    right.set_ylabel("Multiple of the starting score (log scale)")
    right.set_title("Rule of thumb against exact", fontsize=11.5)
    right.grid(axis="x", alpha=0)

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
    log_text = (f"In logarithms the gap is n x ln({fmt(q1, 2)} / {fmt(q0, 2)}) = {n} x {fmt(math.log(q1 / q0), 4)} = {fmt(n * round(math.log(q1 / q0), 4), 2)}, "
                f"so the length multiplies the per-token gain.")
    gap = abs(ratio - first_order) / ratio
    if gap <= 0.1:
        fit = (f"First-order rule: 1 + n x rise = 1 + {n} x {fmt(rise, 4)} = {fmt(first_order, 2)}, within 10 percent of the exact "
               f"{fmt(ratio, 2)}, because n x rise = {fmt(n * rise, 2)} is small.")
    else:
        fit = (f"First-order rule: 1 + n x rise = 1 + {n} x {fmt(rise, 4)} = {fmt(first_order, 2)}, more than 10 percent away from the "
               f"exact {fmt(ratio, 2)}: with n x rise = {fmt(n * rise, 2)} the rise is applied {n} times and compounds.")
    slope_note = (f"The absolute slope at q = {fmt(q0, 2)} is n x q^(n - 1) = {n} x {fmt(q0, 2)}^{n - 1} = {fmt(slope0, 3)}"
                  + (", below one, so at the starting q a one-point gain in q buys less than one point of score even though the relative gain is large."
                     if slope0 < 1 else ", above one.")
                  + f" The slope at q = {fmt(q1, 2)} is {fmt(slope1, 3)}, and over the whole step the average slope is {fmt(avg_slope, 3)}.")
    interpretation = (f"{fmt(q0, 2)}^{n} = {fmt(u0, digits_for(u0))} and {fmt(q1, 2)}^{n} = {fmt(u1, digits_for(u1))}, so the ratio is "
                      f"{fmt(u1, digits_for(u1))} / {fmt(u0, digits_for(u0))} = {fmt(ratio, 1)}. The model gained "
                      f"{fmt((q1 - q0) * 100, 0)} points per token, yet the exact-match score changed by a factor of {fmt(ratio, 1)}. "
                      "The scores are rounded for display and the ratio is computed from the unrounded values. "
                      f"A short target amplifies a gain less than a long target does. {log_text} {fit} {slope_note} {trials}")
    metrics = {
        f"Score at q = {fmt(q0, 2)}": fmt(u0, digits_for(u0)),
        f"Score at q = {fmt(q1, 2)}": fmt(u1, digits_for(u1)),
        "Gain per token": f"{fmt((q1 - q0) * 100, 0)} percentage points",
        "Gain in task score": f"a factor of {fmt(ratio, 1)}",
        "First-order multiple (1 + n x rise)": fmt(first_order, 2),
        "Absolute slope at start": fmt(slope0, 3),
        "Expected passes in 100 trials": f"{fmt(e0, 1)} then {fmt(e1, 1)}",
    }
    worked = [
        f"Target length n = {n}; per-token success goes from q = {fmt(q0, 2)} to q = {fmt(q1, 2)}.",
        f"Start: U0 = {fmt(q0, 2)}^{n} = {fmt(u0, digits_for(u0))}.",
        f"End: U1 = {fmt(q1, 2)}^{n} = {fmt(u1, digits_for(u1))}.",
        f"Ratio = {fmt(u1, digits_for(u1))} / {fmt(u0, digits_for(u0))} = {fmt(ratio, 1)}, from the unrounded values.",
        f"Logarithms: n x ln({fmt(q1, 2)} / {fmt(q0, 2)}) = {n} x {fmt(math.log(q1 / q0), 4)} = {fmt(n * round(math.log(q1 / q0), 4), 2)}.",
        f"Relative rise in q = {fmt(q1, 2)} / {fmt(q0, 2)} - 1 = {fmt(rise, 4)}.",
        f"First-order multiple = 1 + {n} x {fmt(rise, 4)} = {fmt(first_order, 2)}, against the exact {fmt(ratio, 2)}.",
    ]
    alt = (f"Left, four curves of U = q^n for n = 5, 20, 40 and 100 with the curve for n = {n} drawn thick and its two marked "
           f"points at q = {fmt(q0, 2)} and q = {fmt(q1, 2)}. Right, a log-scale bar chart comparing the first-order multiple "
           f"{fmt(first_order, 1)} with the exact multiple {fmt(ratio, 1)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 4: audit a claim before attributing it

DECLARATIONS = [
    ("model family", "are the members comparable at all?"),
    ("scale axis", "parameters, compute, or achieved loss?"),
    ("metric and baseline", "does the cliff belong to the model or the ruler?"),
    ("predictor class", "unpredictable by whom, fitting what?"),
    ("tolerance", "how large a miss counts as a miss?"),
]
UNFIXED = {"none": None, "axis": 1, "metric": 2, "predictor": 3}
DISPUTES = {
    1: "Du and colleagues changed this row (pretraining loss instead of parameter count) and the cliff relocated.",
    2: "Schaeffer and colleagues changed this row (the measure) and the cliff softened.",
    3: "Two careful readers can study one chart and disagree, each of them right.",
}
AUDIT_ROWS = ["Components", "Coupling", "State", "Observable", "Nonlinear", "Counterfactual"]
CLAIMS = {
    "rescoring": {
        "name": "Re-scored arithmetic outputs",
        "rows": ["a frozen model and an evaluator", "a parser and a threshold", "the fixed set of outputs, which never changed",
                 "exact-match accuracy", "the threshold itself", "run: keep everything fixed, swap the metric for a graded one"],
        "verdict": "The curve flattened, so the cliff is assigned to the readout, on the strength of an executed intervention.",
        "short": "assigned to the readout",
    },
    "benchmark": {
        "name": "Larger model on a reasoning benchmark",
        "rows": ["one model and one evaluator", "the same parser", None, None, None,
                 "none available: no matched smaller system differing in exactly one thing"],
        "verdict": "The audit returns no verdict, which is the correct output.",
        "short": "no verdict",
    },
}


def wrap(text, width):
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


def audit_picture(unfixed="none", claim="rescoring"):
    from matplotlib.patches import Rectangle

    k = 0 if UNFIXED[unfixed] is None else 1
    fixed_count = 5 - k
    info = CLAIMS[claim]
    answered = sum(1 for r in info["rows"] if r is not None)

    fig, (left, right) = new_figure(ncols=2, height=5.4)
    for ax in (left, right):
        ax.axis("off")
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
    left.set_title("What a claim must declare (Figure 1.2)", fontsize=11.5)
    row_h = 0.15
    for i, (name, question) in enumerate(DECLARATIONS):
        y = 0.97 - (i + 1) * row_h
        is_open = UNFIXED[unfixed] == i
        color = PALETTE["terracotta"] if is_open else PALETTE["teal"]
        left.add_patch(Rectangle((0.0, y + 0.015), 0.025, row_h - 0.03, color=color, transform=left.transData))
        left.text(0.05, y + row_h - 0.03, name, ha="left", va="top", fontsize=11.5, fontweight="bold", color=PALETTE["ink"])
        left.text(0.05, y + row_h - 0.075, question, ha="left", va="top", fontsize=10.5, color=PALETTE["ink"])
        left.text(0.99, y + row_h - 0.03, "OPEN" if is_open else "fixed", ha="right", va="top", fontsize=10.5, fontweight="bold", color=color)
    if k:
        note = wrap(DISPUTES[UNFIXED[unfixed]], 52)
        head = f"Not checkable yet: {DECLARATIONS[UNFIXED[unfixed]][0]} is open."
    else:
        note = "Suppose all five are fixed: the claim would then be testable against a declared predictor and tolerance."
        note = wrap(note, 52)
        head = "Checkable in principle, if all five are fixed."
    left.text(0.0, 0.2, head, ha="left", va="top", fontsize=11.5, fontweight="bold", color=PALETTE["ink"])
    left.text(0.0, 0.155, note, ha="left", va="top", fontsize=10.5, color=PALETTE["ink"])

    right.set_title(f"Six-question audit: {info['name'].lower()}", fontsize=11.5)
    row_h = 0.125
    for i, (q, a) in enumerate(zip(AUDIT_ROWS, info["rows"])):
        y = 0.97 - (i + 1) * row_h
        right.text(0.0, y + row_h - 0.01, q, ha="left", va="top", fontsize=11.5, fontweight="bold", color=PALETTE["ink"])
        if a is None:
            right.text(0.0, y + row_h - 0.05, "not stated in the chapter", ha="left", va="top", fontsize=10.5, style="italic", color=PALETTE["grey"])
        else:
            right.text(0.0, y + row_h - 0.05, wrap(a, 54), ha="left", va="top", fontsize=10.5, color=PALETTE["ink"], linespacing=1.15)
    right.text(0.0, 0.2, "Verdict", ha="left", va="top", fontsize=11.5, fontweight="bold", color=PALETTE["navy"])
    right.text(0.0, 0.155, wrap(info["verdict"], 54), ha="left", va="top", fontsize=10.5, color=PALETTE["navy"])

    unfixed_text = "none" if not k else DECLARATIONS[UNFIXED[unfixed]][0]
    interpretation = (f"Declarations fixed = 5 - {k} = {fixed_count} of 5; open: {unfixed_text}. "
                      + ("The claim is checkable only once all five are fixed; here all five are supposed fixed, so it would be checkable in principle." if not k else
                         "The claim is checkable only once all five are fixed, and one is still open. " + DISPUTES[UNFIXED[unfixed]])
                      + f" Audit rows the chapter answers for this claim = 6 - {6 - answered} = {answered} of 6. {info['verdict']}"
                      + (" Being checkable in principle does not produce a verdict here, because the counterfactual row has no matched smaller system." if claim == "benchmark" else ""))
    metrics = {
        "Declarations fixed (assumed)": f"{fixed_count} of 5",
        "Open declaration": unfixed_text,
        "Checkable in principle": "yes" if not k else "no",
        "Audit rows answered": f"{answered} of 6",
        "Audit verdict": info["short"],
    }
    worked = [
        "Figure 1.2 lists five declarations: model family, scale axis, metric and baseline, predictor class, tolerance.",
        f"Open declarations: {k}. Fixed = 5 - {k} = {fixed_count}.",
        "The claim is checkable only when all five are fixed." + (" Here all five are supposed fixed, so it would be." if not k else " It is not."),
        f"The audit asks six questions of the claim: {', '.join(r.lower() for r in AUDIT_ROWS)}.",
        f"Rows the chapter answers for '{info['name'].lower()}': 6 - {6 - answered} = {answered}.",
        info["verdict"],
    ]
    alt = (f"Left, five declarations with {'all marked fixed' if not k else unfixed_text + ' marked open'}. Right, the six audit rows for "
           f"{info['name'].lower()} and the verdict: {info['short']}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


CHAPTER = {
    "number": 1,
    "title": "When a Score Becomes a Skill",
    "subtitle": "A reported capability depends on the model and also on the rule that reads its outputs, so a jump on a chart can come from the ruler.",
    "summary": (
        "These four demonstrations follow the chapter's argument about measurement. The first moves a pass line over fixed "
        "scores, the second changes the rules and the loop around an unchanged model, the third shows how raising a probability "
        "to the power of a target length turns small gains into large ones, and the fourth audits a claim before anyone "
        "attributes it to the model."
    ),
    "ask_skill": {
        "prompt": ("Audit this sudden benchmark score. Scales 10, 20, 40, 80; graded scores 0.1, 0.3, 0.6, 0.8; pass cutoff 0.7. "
                   "Does the jump in the thresholded curve come from the scoring rule, and which cutoffs would move it?"),
    },
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
            "prediction_options": ["Scale 3", "Scale 4 (unchanged)", "Scale 5", "No checkpoint passes"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "The scores did not move. Only the 0.52 at scale 4 now falls short of 0.55, so the first pass is the 0.56 at scale 5.",
                "incorrect": "Change the cutoff control from 0.50 to 0.55 on the gradual set: 0.52 < 0.55 fails at scale 4, and 0.56 >= 0.55 passes at scale 5.",
            },
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
            "provenance": "Constructed example: the five scores and the larger-rise four-score set with its cutoff of 0.70 are the laboratory's declared inputs for this chapter (default and transfer cases), computed with its threshold function; the other cutoffs are values defined for the reader.",
            "source_section": "What did change",
            "source_anchor": "what-did-change",
            "controls": [
                {"key": "dataset", "label": "Score set", "values": ["gradual", "steep"], "default": "gradual",
                 "value_labels": ["Gradual rise, five checkpoints", "Larger rise, four checkpoints (scales double)"]},
                {"key": "cutoff", "label": "Pass cutoff", "values": [0.5, 0.55, 0.6, 0.7], "default": 0.5},
            ],
            "function": "cutoff_picture",
            "misconception": {
                "title": "A score that crosses a pass line is a new internal state",
                "text": ("The chapter warns that a curve that looks sudden is not a discontinuity and a score that crosses a pass line is not "
                         "a new internal state. Here every graded score is identical in every state; only the line moves."),
            },
            "scope_note": {
                "text": ("The re-scoring result covers the evaluations Schaeffer and colleagues examined, not every reported curve. "
                         "These constructed points cannot show whether a true curve between them is smooth or sharp."),
                "source_section": "What this does not settle",
            },
        },
        {
            "id": "C01-D02",
            "title": "Three places a change can enter, and the loop",
            "question": "If the model's probabilities never change, how much can the reported score move?",
            "equations": [EQ_LAW, EQ_PIPELINE],
            "symbols": (
                "K_theta(z | c) is the model's probability for output z given context c, Equation (1.1): the whole law over responses, "
                "frozen in this demonstration. dec picks one output from that law: greedy decoding takes the most probable one, sampling "
                "draws one at random according to the probabilities. eval_tau judges the chosen output, 1 for success and 0 for failure. "
                "The expected score adds up, over the responses, the chance the decoder returns each one times its verdict. With twenty "
                "attempts, an attempt succeeds with the total probability of the accepted responses and the score is the chance that "
                "at least one of twenty independent attempts succeeds."
            ),
            "prediction": "Keep greedy decoding on the chapter's law and switch the evaluator from accepting only A to rewarding a request for evidence. What happens to the score?",
            "prediction_options": ["It stays at 1.00", "It falls to 0.00", "It becomes 0.20", "It becomes 0.45"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Greedy still returns A (0.45), and an evaluator that rewards only evidence judges A a failure, so the score is 0.00.",
                "incorrect": "Greedy returns A whatever the evaluator is. Change the evaluator control to rewards asking for evidence: A is judged a failure, so the score is 0.00.",
            },
            "explanation": (
                "Equation (1.3) joins three stages by two arrows: the model's law, the decoder and the evaluator. The left panel "
                "is the first stage, Equation (1.1), and is frozen. The decoder decides which response is returned, and the evaluator "
                "decides which responses count. The score in the right panel combines the two, so it cannot say which stage moved. "
                "Allowing twenty attempts adds the loop: the chance that some attempt passes climbs toward one with the law untouched."
            ),
            "application": (
                "When two reports of the same model disagree, ask which stage differs: the decoding settings, the scoring rule or the "
                "number of attempts. Report the stage that changed, not only the final number."
            ),
            "assumptions": (
                "One prompt, three possible responses and independent attempts. The probabilities 0.45, 0.35 and 0.20 and the twenty "
                "attempts are the chapter's constructed values; the flat law 0.30, 0.30, 0.40 is a value defined for the reader. "
                "Real decoders and evaluators have more settings, attempts can be correlated, and several settings can differ at once."
            ),
            "check": "Suppose the model law were 0.30, 0.30 and 0.40 for A, B and evidence, and the evaluator rewards evidence. What do greedy decoding and one sampled draw score?",
            "answer": "Greedy returns evidence, the largest at 0.40, so it scores 1. One draw scores 0.30 x 0 + 0.30 x 0 + 0.40 x 1 = 0.40.",
            "provenance": "Constructed example: the chapter's constructed distribution of 0.45, 0.35 and 0.20 over three responses and its twenty-attempt budget at probability 0.20; the second law is defined for the reader.",
            "source_section": "Three places a change can enter",
            "source_anchor": "three-places-a-change-can-enter",
            "controls": [
                {"key": "decoder", "label": "Decoding rule", "values": ["greedy", "sample", "attempts"], "default": "greedy",
                 "value_labels": ["Greedy (most probable)", "One sampled draw", "Twenty attempts, any may pass"]},
                {"key": "evaluator", "label": "Evaluator", "values": ["only_a", "evidence"], "default": "only_a",
                 "value_labels": ["Accepts only A", "Rewards asking for evidence"]},
                {"key": "law", "label": "Model law (A, B, evidence)", "values": ["chapter", "flat"], "default": "chapter",
                 "value_labels": ["Chapter: 0.45, 0.35, 0.20", "Defined for the reader: 0.30, 0.30, 0.40"]},
            ],
            "function": "pipeline_picture",
            "misconception": {
                "title": "The model solved it",
                "text": ("The model is the component that produces the visible text, so it collects the credit for a result several "
                         "components produced together. Here the law is fixed and the reported score still ranges from 0.00 to 1.00."),
            },
        },
        {
            "id": "C01-D03",
            "title": "How exact match manufactures a cliff",
            "question": "How much does a small gain per token change an exact-match score, and how does target length decide it?",
            "equations": [EQ_POWER, EQ_SLOPE],
            "symbols": (
                "q is the probability that one token is right, n is the number of tokens in the target, and U is the exact-match "
                "score: the probability that all n tokens are right, assuming tokens succeed independently. The logarithm form says "
                "the length n multiplies the per-token gain. The relative rise is q1 / q0 - 1. The first-order multiple 1 + n x rise "
                "is the chapter's elasticity remark: a small relative increase in q raises U by about n times as much. The absolute "
                "slope n q^(n-1) is the derivative dU/dq, how many points of score one extra point of q buys."
            ),
            "prediction": "For a target of 40 tokens, how many times larger is the score at q = 0.95 than at q = 0.90?",
            "prediction_options": ["About 1.05 times (the per-token ratio)", "About 5 times", "About 9 times", "About 40 times"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "0.95^40 / 0.90^40 = 0.1285 / 0.0148 = 8.7, about 9 times, from a gain of five points per token.",
                "incorrect": "Compute 0.95^40 = 0.1285 and 0.90^40 = 0.0148 (or set length 40 and the 0.90 to 0.95 step): the ratio is 8.7, about 9 times.",
            },
            "explanation": (
                "Equation (1.4) multiplies q by itself n times, so a short target amplifies a gain less than a long target does, and "
                "a long target can amplify it enormously. The left panel draws the four target lengths of Figure 1.4, with the "
                "selected one thick. The right panel compares the exact multiple with the first-order rule: the rule is close while "
                "n times the rise is small and fails once the rise is applied many times. The absolute slope can stay below one while the relative gain is large."
            ),
            "application": (
                "Before reading a flat region at the start of a benchmark curve as no progress, compute what the score would be "
                "if per-token quality had improved smoothly. Then decide whether the benchmark can resolve those small values."
            ),
            "assumptions": (
                "Tokens succeed independently and each has the same probability q. Real text violates this, so the mechanism is "
                "robust but the exact factors are constructed. The expected passes in 100 trials are expected counts, not observed "
                "results, and the first-order rule is a small-change approximation."
            ),
            "check": "A coding assistant gets each line right with probability 0.90. What is the chance a 20-line function is entirely right, and how does it change at 0.99 per line?",
            "answer": "0.90^20 = 0.1216, about one in eight. 0.99^20 = 0.8179, about four in five, a factor of 0.8179 / 0.1216 = 6.7 from a nine-point gain per line.",
            "provenance": "Constructed example: the per-token values 0.90, 0.95 and 0.99 and the target lengths of Table 1.1, computed from Equation (1.4); the coding-assistant case is the chapter's twenty-line example. The budget of 100 trials behind the expected-passes readout is a value defined for the reader.",
            "source_section": "Why exact match manufactures a cliff",
            "source_anchor": "why-exact-match-manufactures-a-cliff",
            "controls": [
                {"key": "length", "label": "Target length n (tokens)", "values": [5, 20, 40, 100], "default": 40},
                {"key": "step", "label": "Per-token gain", "values": ["low", "high", "wide"], "default": "low",
                 "value_labels": ["q from 0.90 to 0.95", "q from 0.95 to 0.99", "q from 0.90 to 0.99"]},
            ],
            "function": "cliff_picture",
            "misconception": {
                "title": "A flat observed curve means nothing was happening",
                "text": ("The chapter says a flat observed region need not mean nothing was happening, and gives the success probabilities "
                         "0.000027 and 0.005921 at n = 100 for q = 0.90 and 0.95. For a budget of 100 trials, a number defined for the reader, "
                         "the expected passes are 0.0 then 0.6, both under one."),
            },
            "scope_note": {
                "text": ("Equation (1.4) assumes tokens succeed independently, which real text violates; the mechanism is robust, the "
                         "exact factors are constructed."),
                "source_section": "What this does not settle",
            },
        },
        {
            "id": "C01-D04",
            "title": "Audit a claim before attributing it",
            "question": "Which declarations must be fixed before an emergence claim can be tested, and what does the six-question audit say about two claims?",
            "equations": [EQ_SCORE, EQ_PIPELINE],
            "symbols": (
                "The five declarations of Figure 1.2 are the model family, the scale axis, the metric with its baseline, the class of "
                "predictors and the tolerance. A claim is checkable only once all five are fixed. The six audit questions are: what are "
                "the components, what couples them, what is the state, what is the observable, what is nonlinear, and what is the "
                "counterfactual. U with the braces of Equation (1.2) is the score of the system built from the enabled components, and "
                "the arrows of Equation (1.3) are the couplings between stages."
            ),
            "prediction": "Leave the scale axis open and fix the other four declarations. Is the emergence claim checkable?",
            "prediction_options": ["Yes, four of five is enough", "No, all five must be fixed"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "The chapter says a claim is checkable only once all five are fixed, and an open row leaves a dispute that no chart can settle.",
                "incorrect": "Set the declaration control to Scale axis: the figure marks it open, and the chapter says a claim is checkable only once all five are fixed.",
            },
            "explanation": (
                "The left panel is Figure 1.2: each declaration beside the question it settles. Leaving a row open leaves its dispute alive, "
                "as in the published disagreements about the scale axis and the metric. The right panel applies the six audit questions. "
                "For the re-scored outputs a counterfactual was executed, so the audit assigns the cliff to the readout; for a bare "
                "comparison of two different models there is no matched counterfactual, so the correct output is no verdict."
            ),
            "application": (
                "Before crediting the model for a capability, write down the five declarations and the six audit answers. A blank "
                "counterfactual row means the claim has not been tested, whatever the chart shows."
            ),
            "assumptions": (
                "The audit rows are the chapter's own worked answers; for the second claim the chapter answers only the components, "
                "the coupling and the counterfactual, and this demonstration leaves the other rows blank rather than invent them. "
                "Only one declaration is opened at a time here, and the model family and tolerance rows are not offered as the open one."
            ),
            "check": "In the larger-model comparison, which audit row decides that no verdict is possible, and why?",
            "answer": "The counterfactual row: there is no matched smaller system differing in exactly one thing, because the two models differ in parameters, data and training recipe. 3 rows answered of 6, and the missing one is the one that decides.",
            "provenance": "Constructed example: the five declarations of Figure 1.2 and the two worked audits of the chapter's emergence audit section, shown as the chapter states them.",
            "source_section": "An emergence audit",
            "source_anchor": "an-emergence-audit",
            "controls": [
                {"key": "unfixed", "label": "Declaration left open", "values": ["none", "axis", "metric", "predictor"], "default": "none",
                 "value_labels": ["None (suppose all five fixed)", "Scale axis", "Metric and baseline", "Predictor class"]},
                {"key": "claim", "label": "Claim audited", "values": ["rescoring", "benchmark"], "default": "rescoring",
                 "value_labels": ["Re-scored arithmetic outputs", "Larger model on a reasoning benchmark"]},
            ],
            "function": "audit_picture",
            "misconception": {
                "title": "The most visible component earns the credit",
                "text": ("The chapter names the common error: a system-level success is attributed to the most visible component, almost "
                         "always the language model, even though the agent can supply the state, the loop, the permissions and the consequences."),
            },
            "scope_note": {
                "text": ("The three-condition definition of emergence is a working tool for this book rather than a settled position in the field."),
                "source_section": "What this does not settle",
            },
        },
    ],
}

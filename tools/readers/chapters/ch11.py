"""Chapter 11 reader: The Mathematics of Curiosity.

Four demonstrations built on Equations (11.1) to (11.4). Demonstration 1 draws
the accumulated regret of one seeded run of the laboratory's own upper-confidence
policy (math_ai_agents.chapters.ch11.evaluate) next to the closed-form regret of
the two rules that do not work. The other demonstrations compute the chapter's
table and worked prices directly. Every number is a constructed teaching value;
the values in Demonstrations 2 and 4 are the book's own worked numbers.
"""
import math
from functools import lru_cache

import numpy as np

from math_ai_agents.chapters.ch11 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

EQ_REGRET = r"\operatorname{Reg}(T)=T\mu^{\star}-\operatorname{E}\!\left[\sum_{t=0}^{T-1}\mu_{a_t}\right]"
EQ_UCB = r"a_t=\arg\max_{a\in\mathcal{A}}\left(\hat\mu_a+c\sqrt{\frac{\ln t}{N_t(a)}}\right)"
EQ_GAIN = r"\operatorname{Gain}(O)=I(Y;O)=H(Y)-H(Y\mid O)"
EQ_VOI = r"\operatorname{VOI}(O)=\operatorname{E}_{O}\!\left[\max_{a}\operatorname{EU}(a\mid O)\right]-\max_{a}\operatorname{EU}(a)"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


def big(x, digits=1):
    """Number with thousands separators and fixed decimals, ASCII only (1,200.0)."""
    return f"{float(x):,.{digits}f}"


def count_text(x):
    """Integer with thousands separators, ASCII only."""
    return f"{int(round(x)):,}"


# Demonstration 1: regret of three allocation rules

MEAN_A = 0.78
SEED = 11


@lru_cache(maxsize=None)
def lab_ucb_regret(mean_b):
    """Accumulated pseudo-regret of one seeded run of the laboratory's UCB policy, 10,000 rounds."""
    out = evaluate({"means": [MEAN_A, mean_b], "rounds": 10000, "seed": SEED, "pull_cost": 0})
    series = next(s for s in out["series"] if s["label"].startswith("ucb"))
    return tuple(series["y"])


def regret_picture(horizon=1000, mean_b=0.9):
    horizon = int(horizon)
    gap = mean_b - MEAN_A
    trapped = gap * horizon
    rotation = gap * horizon / 2
    ucb_curve = np.array(lab_ucb_regret(float(mean_b))[:horizon])
    ucb_end = float(ucb_curve[-1])
    t = np.arange(1, horizon + 1)

    fig, ax = new_figure(height=4.3)
    ax.plot(t, gap * t, color=PALETTE["terracotta"], linewidth=2)
    ax.plot(t, gap * t / 2, color=PALETTE["gold"], linewidth=2, linestyle="dashed")
    keep = np.unique(np.append(np.arange(0, horizon, max(1, horizon // 300)), horizon - 1))  # thin the drawn points, keep the last
    ax.plot(t[keep], ucb_curve[keep], color=PALETTE["teal"], linewidth=2, linestyle="dotted")
    ax.plot([horizon], [trapped], "o", color=PALETTE["terracotta"], markersize=8)
    ax.plot([horizon], [rotation], "s", color=PALETTE["gold"], markersize=8)
    ax.plot([horizon], [ucb_end], "^", color=PALETTE["teal"], markersize=9)
    label_point(ax, horizon * 0.5, gap * horizon * 0.5, "always the current best", color=PALETTE["terracotta"], dx=-4, dy=6, ha="right").set_bbox(BOX)
    label_point(ax, horizon * 0.78, gap * horizon * 0.39, "rotate evenly", color=PALETTE["gold"], dx=-4, dy=6, ha="right").set_bbox(BOX)
    y_mid = float(ucb_curve[horizon // 2])
    room_below = y_mid > 0.09 * gap * horizon * 1.12  # enough space under the curve for the label
    y_anchor = y_mid if room_below else float(ucb_curve[horizon // 2:int(horizon * 0.95)].max())
    label_point(ax, horizon * 0.5, y_anchor, "one run of the optimistic rule", color=PALETTE["teal"], dx=4, dy=-8 if room_below else 8,
                ha="left", va="top" if room_below else "bottom")
    ax.set_xlim(0, horizon * 1.04)
    ax.set_ylim(0, gap * horizon * 1.12)
    ax.set_xlabel("Task number")
    ax.set_ylabel("Accumulated regret (successes forgone)")
    ax.set_title(f"Tool A succeeds {fmt(MEAN_A, 2)}, tool B {fmt(mean_b, 2)}, run of {count_text(horizon)} tasks", fontsize=11.5)

    metrics = {
        "Best mean": fmt(mean_b, 2),
        "Gap per task": fmt(gap, 2),
        "Always the current best": fmt(trapped, 1),
        "Rotate evenly": fmt(rotation, 1),
        "One seeded run of the optimistic rule": fmt(ucb_end, 1),
    }
    interpretation = (
        f"Always taking tool A: regret = {count_text(horizon)} x {fmt(mean_b, 2)} - {count_text(horizon)} x {fmt(MEAN_A, 2)} = {big(trapped)}. "
        f"Rotating evenly: regret = {count_text(horizon)} x {fmt(mean_b, 2)} - ({count_text(horizon / 2)} x {fmt(MEAN_A, 2)} + "
        f"{count_text(horizon / 2)} x {fmt(mean_b, 2)}) = {big(rotation)}. Both grow in proportion to the run: ten times the tasks, ten times "
        f"the regret. The dotted curve is one constructed run of an optimistic rule with a fixed seed. It ended this run at {big(ucb_end)}, "
        f"below both lines and about {fmt(100 * ucb_end / rotation, 0)} percent of the rotate-evenly total. It is a single run, not a guarantee or a measurement of any real system."
    )
    return fig, metrics, interpretation


# Demonstration 2: ten constructed pulls under the upper-confidence index

def reward(arm, pulls_so_far):
    """Deterministic teaching rewards: A returns 1, 0, 1, 0, ...; B returns 0, 1, 0, 1, ..."""
    return (1 - pulls_so_far % 2) if arm == 0 else (pulls_so_far % 2)


def trace(c, last_pull):
    """Replay the chapter's deterministic trace with confidence coefficient c up to pull number last_pull.

    Returns the record of the decision made at pull number last_pull.
    """
    counts = [0, 0]
    sums = [0.0, 0.0]
    record = None
    for pull in range(1, last_pull + 1):
        t = pull - 1  # completed pulls
        means = [sums[a] / counts[a] if counts[a] else None for a in (0, 1)]
        if 0 in counts:
            bonuses = [None, None]
            indices = [None, None]
            selected = counts.index(0)
        else:
            bonuses = [c * math.sqrt(math.log(t) / counts[a]) for a in (0, 1)]
            indices = [means[a] + bonuses[a] for a in (0, 1)]
            selected = 0 if indices[0] >= indices[1] - 1e-9 else 1  # exact ties go to A (alphabetical)
        r = reward(selected, counts[selected])
        record = {"pull": pull, "t": t, "counts": tuple(counts), "means": means, "bonuses": bonuses,
                  "indices": indices, "selected": selected, "reward": r}
        counts[selected] += 1
        sums[selected] += r
    return record


def ucb_picture(pull=4, c=math.sqrt(2)):
    rec = trace(float(c), int(pull))
    names = ["A", "B"]
    fig, ax = new_figure(height=4.3)
    top = max(rec["indices"])
    for a in (0, 1):
        color = PALETTE["navy"] if a == 0 else PALETTE["olive"]
        ax.bar(a, rec["means"][a], width=0.55, color=color)
        ax.bar(a, rec["bonuses"][a], bottom=rec["means"][a], width=0.55, color="white", edgecolor=color, hatch="///", linewidth=1.4)
        chosen = " (selected)" if a == rec["selected"] else ""
        ax.text(a, rec["indices"][a] + 0.05, f"index {fmt(rec['indices'][a], 3)}{chosen}", ha="center", va="bottom",
                fontsize=11, color=PALETTE["ink"], bbox=BOX)
        if rec["means"][a] > 0.15:
            ax.text(a, rec["means"][a] / 2, f"mean\n{fmt(rec['means'][a], 3)}", ha="center", va="center", fontsize=11, color="white")
        else:  # a mean too small to hold a label inside its bar is still printed, at the baseline
            ax.text(a, 0.02, f"mean {fmt(rec['means'][a], 3)}", ha="center", va="bottom", fontsize=10.5,
                    color=PALETTE["ink"], bbox=BOX)
        ax.text(a, rec["means"][a] + rec["bonuses"][a] / 2, f"bonus\n{fmt(rec['bonuses'][a], 3)}", ha="center", va="center", fontsize=11,
                color=PALETTE["ink"], bbox=BOX)
    ax.set_xticks([0, 1], [f"Tool {n}: {rec['counts'][i]} {'pull' if rec['counts'][i] == 1 else 'pulls'}" for i, n in enumerate(names)])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, top + 0.45)
    ax.set_xlabel("Retrieval tool and how often it has been pulled")
    ax.set_ylabel("Index = mean + bonus (hatched part)")
    ax.grid(axis="x", alpha=0)
    ax.set_title(f"Pull {rec['pull']}, {rec['t']} pulls completed, c = {fmt(c, 3)}", fontsize=11.5)

    chosen_name = names[rec["selected"]]
    metrics = {
        "Counts A, B": f"{rec['counts'][0]}, {rec['counts'][1]}",
        "Index A": fmt(rec["indices"][0], 3),
        "Index B": fmt(rec["indices"][1], 3),
        "Selected": chosen_name,
        "Reward seen after the pull": str(rec["reward"]),
    }
    lnt = math.log(rec["t"])
    sums = []
    for a in (0, 1):
        sums.append(f"{names[a]}: bonus = {fmt(c, 3)} x sqrt({fmt(lnt, 3)} / {rec['counts'][a]}) = {fmt(rec['bonuses'][a], 3)}, "
                    f"index = {fmt(rec['means'][a], 3)} + {fmt(rec['bonuses'][a], 3)} = {fmt(rec['indices'][a], 3)}")
    other = 1 - rec["selected"]
    gap = rec["indices"][rec["selected"]] - rec["indices"][other]
    if abs(gap) < 1e-9:
        verdict = f"The indices tie exactly, so the rule's alphabetical tie-break selects {chosen_name}."
    else:
        verdict = (f"Tool {chosen_name} has the larger index by {fmt(gap, 3)}, so Equation (11.2) selects it. "
                   f"Its pull number {rec['pull']} then returns {rec['reward']}.")
    interpretation = (f"With {rec['t']} completed pulls, ln {rec['t']} = {fmt(lnt, 3)}. " + ". ".join(sums) + f". {verdict} "
                      "A tool with few pulls keeps a large bonus even when its mean is low.")
    return fig, metrics, interpretation


# Demonstration 3: information gain is not decision value

SUPPORTED_VALUE = 100.0   # release utility when every claim is supported (unsupported release is worth 0)
EVIDENCE_VALUE = 92.0     # request evidence: 0.97 x 100 - 5, the book's score


def entropy(p):
    """Binary entropy in bits; 0 at the ends."""
    if p <= 0 or p >= 1:
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def check_outcomes(prior, accuracy):
    """Symmetric check of a claim: joint probabilities and release scores for each possible report."""
    rows = []
    for report in ("supported", "unsupported"):
        if report == "supported":
            p_report = prior * accuracy + (1 - prior) * (1 - accuracy)
            joint_supported = prior * accuracy
        else:
            p_report = prior * (1 - accuracy) + (1 - prior) * accuracy
            joint_supported = prior * (1 - accuracy)
        posterior = joint_supported / p_report
        rows.append({"report": report, "p": p_report, "joint": joint_supported, "posterior": posterior,
                     "release": SUPPORTED_VALUE * posterior})
    return rows


def gain_value_picture(accuracy=0.85, prior=0.85):
    rows = check_outcomes(prior, accuracy)
    h_before = entropy(prior)
    h_after = sum(r["p"] * entropy(r["posterior"]) for r in rows)
    gain = h_before - h_after
    best_now = max(SUPPORTED_VALUE * prior, EVIDENCE_VALUE)
    best_after = sum(max(SUPPORTED_VALUE * r["joint"], EVIDENCE_VALUE * r["p"]) for r in rows)
    voi = best_after - best_now
    changes = any((r["release"] > EVIDENCE_VALUE) != (SUPPORTED_VALUE * prior > EVIDENCE_VALUE) for r in rows)

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.bar([0, 1], [h_before, h_after], width=0.55, color=[PALETTE["grey"], PALETTE["teal"]])
    left.bar([1], [gain], bottom=[h_after], width=0.55, color="white", edgecolor=PALETTE["teal"], hatch="///", linewidth=1.4)
    left.text(0, h_before + 0.02, f"{fmt(h_before, 3)}", ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.text(1, h_before + 0.02, f"{fmt(h_after, 3)}\ngain {fmt(gain, 3)}", ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.set_xticks([0, 1], ["Before the check", "After the check"])
    left.set_xlim(-0.6, 1.6)
    left.set_ylim(0, 1.3)
    left.set_xlabel("Uncertainty about the claim (hatched part is removed)")
    left.set_ylabel("Entropy in bits")
    left.set_title("Uncertainty resolved", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    xs = [0, 1]
    colors = [PALETTE["teal"] if r["release"] > EVIDENCE_VALUE else PALETTE["navy"] for r in rows]
    right.bar(xs, [r["release"] for r in rows], width=0.55, color="white", edgecolor=colors, hatch="..", linewidth=1.4)
    right.axhline(EVIDENCE_VALUE, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.8)
    right.axhline(SUPPORTED_VALUE * prior, color=PALETTE["grey"], linestyle="dotted", linewidth=1.4)
    for x, r in zip(xs, rows):
        verdict = "release" if r["release"] > EVIDENCE_VALUE else "request evidence"
        right.text(x, 14, f"{fmt(r['release'], 1)}\n{verdict}", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
    no_check_above = SUPPORTED_VALUE * prior > EVIDENCE_VALUE
    label_point(right, 1.4, EVIDENCE_VALUE, "evidence 92.0", color=PALETTE["terracotta"], dx=0, dy=-4 if no_check_above else 4, ha="left",
                va="top" if no_check_above else "bottom")
    label_point(right, 1.4, SUPPORTED_VALUE * prior, f"no check {fmt(SUPPORTED_VALUE * prior, 1)}", color=PALETTE["grey"], dx=0,
                dy=4 if no_check_above else -4, ha="left", va="bottom" if no_check_above else "top")
    right.set_xticks(xs, ["Check says\nsupported", "Check says\nunsupported"])
    right.set_xlim(-0.6, 2.55)
    right.set_ylim(0, 110)
    right.set_xlabel("What the check reports (bar is the release score)")
    right.set_ylabel("Expected utility of releasing")
    right.set_title("Does the best action change?", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    metrics = {
        "Uncertainty before, H(Y)": f"{fmt(h_before, 3)} bits",
        "Uncertainty after, H(Y | O)": f"{fmt(h_after, 3)} bits",
        "Information gain I(Y; O)": f"{fmt(gain, 3)} bits",
        "Decision value VOI": fmt(voi, 2),
        "Best action changes": "yes" if changes else "no",
    }
    parts = []
    for r in rows:
        parts.append(f"{r['report']} report: max(100 x {fmt(r['joint'], 4)}, 92 x {fmt(r['p'], 4)}) = "
                     f"max({fmt(SUPPORTED_VALUE * r['joint'], 2)}, {fmt(EVIDENCE_VALUE * r['p'], 2)}) = "
                     f"{fmt(max(SUPPORTED_VALUE * r['joint'], EVIDENCE_VALUE * r['p']), 2)}")
    if changes:
        meaning = "The report moves the best action in at least one case, so the check is worth something before its cost."
    else:
        meaning = ("Both reports leave the same action on top, so the decision value is exactly zero even though the check "
                   f"removed {fmt(gain, 3)} bits of uncertainty. Information gain and decision value are different quantities.")
    interpretation = (
        f"Best action without the check = max(100 x {fmt(prior, 2)}, 92) = max({fmt(SUPPORTED_VALUE * prior, 2)}, 92.00) = {fmt(best_now, 2)}. "
        + "; ".join(parts) + f". VOI = {fmt(best_after, 2)} - {fmt(best_now, 2)} = {fmt(voi, 2)}. " + meaning
    )
    return fig, metrics, interpretation


# Demonstration 4: a worked price for one observation (the book's classifier)

P_FLAG = 1 / 3
RELEASE_FLAG = 75.0
RELEASE_CLEAR = 90.0


def classifier_picture(shift=10, call_cost=0):
    shift = float(shift)
    call_cost = float(call_cost)
    release_flag = RELEASE_FLAG + shift
    release_clear = RELEASE_CLEAR + shift
    release_before = P_FLAG * release_flag + (1 - P_FLAG) * release_clear
    best_before = max(release_before, EVIDENCE_VALUE)
    best_flag = max(release_flag, EVIDENCE_VALUE)
    best_clear = max(release_clear, EVIDENCE_VALUE)
    best_after = P_FLAG * best_flag + (1 - P_FLAG) * best_clear
    voi = best_after - best_before
    net = voi - call_cost

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    groups = [("after flag\n(prob 1/3)", release_flag), ("after clear\n(prob 2/3)", release_clear), ("before\nobserving", release_before)]
    width = 0.36
    for i, (name, rel) in enumerate(groups):
        win_release = rel > EVIDENCE_VALUE
        left.bar(i - width / 2, rel, width=width, color=PALETTE["navy"] if win_release else "white", edgecolor=PALETTE["navy"], linewidth=1.4, hatch="" if win_release else "//")
        left.bar(i + width / 2, EVIDENCE_VALUE, width=width, color=PALETTE["teal"] if not win_release else "white", edgecolor=PALETTE["teal"], linewidth=1.4, hatch="" if not win_release else "..")
        left.text(i - width / 2, rel + 0.8, fmt(rel, 1), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        left.text(i + width / 2, EVIDENCE_VALUE + 0.8, "92.0", ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        left.text(i, 14, "release\nwins" if win_release else "evidence\nwins", ha="center", va="center", fontsize=10.5, color="white" if False else PALETTE["ink"], bbox=BOX)
    left.set_xticks(range(3), [g[0] for g in groups])
    left.set_ylim(0, 118)
    left.set_xlim(-0.6, 2.6)
    left.set_xlabel("When the choice is made (left bar release, right bar evidence)")
    left.set_ylabel("Expected utility")
    left.set_title("Best action under each result", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    bars = [("Gross value", voi, PALETTE["teal"], ""), ("Net of call cost", net, PALETTE["gold"], "///")]
    for i, (name, value, color, hatch) in enumerate(bars):
        right.bar(i, value, width=0.55, color="white", edgecolor=color, hatch=hatch, linewidth=1.6)
        right.text(i, value + (0.12 if value >= 0 else -0.12), fmt(value, 3), ha="center", va="bottom" if value >= 0 else "top", fontsize=11, color=PALETTE["ink"])
    right.axhline(0, color=PALETTE["ink"], linewidth=1)
    right.set_xticks([0, 1], [b[0] for b in bars])
    right.set_xlim(-0.6, 1.6)
    right.set_ylim(-2.9, 3.0)
    right.set_xlabel(f"Call cost charged: {fmt(call_cost, 1)}")
    right.set_ylabel("Value of the observation (utility points)")
    right.set_title("What the call is worth", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    if abs(net) < 1e-9 and call_cost > 0:
        verdict = "Net value is exactly zero, so buying the call and skipping it tie; Equation (11.4) alone does not choose."
        buy = "tie"
    elif net > 0:
        verdict = f"Net value is positive, so the call is worth buying for this one decision."
        buy = "yes"
    elif voi < 1e-9:
        verdict = "Gross value is zero: the same action wins after either result, so no price makes the call worth buying."
        buy = "no"
    else:
        verdict = "The call costs more than it can return for this decision, so it is not worth buying."
        buy = "no"
    metrics = {
        "Release now, no observation": fmt(release_before, 3),
        "Best action without the call": fmt(best_before, 3),
        "Best expected utility with the call": fmt(best_after, 3),
        "Gross value": fmt(voi, 3),
        "Net value": fmt(net, 3),
        "Worth buying": buy,
    }
    interpretation = (
        f"Release scores {fmt(release_flag, 0)} after flag and {fmt(release_clear, 0)} after clear, so before observing it scores "
        f"1/3 x {fmt(release_flag, 0)} + 2/3 x {fmt(release_clear, 0)} = {fmt(release_before, 3)} against 92 for requesting evidence. "
        f"With the call the best choices are {fmt(best_flag, 0)} after flag and {fmt(best_clear, 0)} after clear, so "
        f"1/3 x {fmt(best_flag, 0)} + 2/3 x {fmt(best_clear, 0)} = {fmt(best_after, 3)}. Gross value = {fmt(best_after, 3)} - {fmt(best_before, 3)} "
        f"= {fmt(voi, 3)}; net value = {fmt(voi, 3)} - {fmt(call_cost, 1)} = {fmt(net, 3)}. {verdict} "
        "The classifier itself never changed between states; only the decision it feeds did."
    )
    return fig, metrics, interpretation


CHAPTER = {
    "number": 11,
    "title": "The Mathematics of Curiosity",
    "subtitle": "Choosing a tool decides which evidence you get about it. Curiosity becomes a costed allocation rule, and information is worth only what it can change.",
    "summary": (
        "These four demonstrations follow the chapter's document controller and its two retrieval tools. First the cost of "
        "never looking again is measured as regret, then an optimistic rule is traced pull by pull, then information gain is "
        "separated from decision value, and finally one observation is priced."
    ),
    "demos": [
        {
            "id": "C11-D01",
            "title": "Regret: what never looking again costs",
            "question": "How fast does the shortfall against an all-knowing agent grow under the rules that always exploit, always rotate, or explore with optimism?",
            "equations": [EQ_REGRET],
            "symbols": (
                "T is the number of tasks. mu-star is the success probability of the best tool. mu of a_t is the success probability "
                "of the tool chosen at task t, and E is the average over luck. Regret is the total successes forgone compared with "
                "always using the best tool. Tool A succeeds 0.78 of the time, tool B 0.90 or 0.84."
            ),
            "prediction": "Go from 1,000 tasks to 10,000 tasks. By what factor does the regret of always taking tool A grow, and does the dotted curve grow by more or less than that factor?",
            "explanation": (
                "Taking the worse tool every time forgoes the gap between the means on every task, so regret is the gap times T, a "
                "straight line. Rotating evenly forgoes the gap on half the tasks, a straight line half as steep. The optimistic "
                "rule keeps trying the thin-record tool only while it is still uncertain, so its regret flattens relative to the lines. The dotted curve is one seeded run, so its growth factor varies with the "
                "state (about 3.6 for tool B at 0.90, about 6.5 at 0.84, from 1,000 to 10,000 tasks); in both it is below 10."
            ),
            "application": (
                "When a team reports a success rate for a deployed agent, ask how much of its action set it has sampled recently. "
                "Regret itself needs the true means, which a deployed agent does not have, so this is the question that can be asked. "
                "An agent that took one action thousands of times and the alternatives twice may have stopped measuring."
            ),
            "assumptions": (
                "Two tools with fixed success probabilities, independent outcomes, and a trapped agent that uses tool A from the first task "
                "and never re-tries the other tool. The dotted curve is one seeded run of expected shortfall (the gap on each task, given the "
                "tool chosen, not realized failures), so it wobbles and is not an expected value; the chapter's guarantee is about an "
                "expectation under stated conditions. Real tools change over time, which this model does not cover."
            ),
            "check": "If tool A succeeds 0.78 and tool B 0.90, how much regret does an agent that rotates evenly build up over 500 tasks?",
            "answer": "Half the tasks go to A and cost 0.12 each: 250 x 0.12 = 30. Equivalently 500 x 0.90 - (250 x 0.78 + 250 x 0.90) = 450 - 420 = 30.",
            "provenance": "Constructed example: the book's invented success rates 0.78 and 0.90 and its 1,000-task comparison; the 0.84 case and the seeded run are defined for this reader and computed with the laboratory's bandit function.",
            "source_section": "What is actually being lost",
            "source_anchor": "what-is-actually-being-lost",
            "controls": [
                {"key": "horizon", "label": "Number of tasks", "values": [200, 1000, 5000, 10000], "default": 1000},
                {"key": "mean_b", "label": "Success probability of tool B", "values": [0.9, 0.84], "default": 0.9},
            ],
            "function": "regret_picture",
        },
        {
            "id": "C11-D02",
            "title": "Optimism: ten constructed pulls",
            "question": "Why does a tool with a poor record and few pulls get called again, and what changes that?",
            "equations": [EQ_UCB],
            "symbols": (
                "t is the number of completed pulls. N_t(a) is how many of those pulls went to tool a. mu-hat of a is tool a's average reward so far. "
                "c is the confidence coefficient; the book uses the square root of two, about 1.414, for rewards between 0 and 1. ln is the natural logarithm. "
                "The index is the mean plus the bonus c x sqrt(ln t / N_t(a)), and the tool with the larger index is called."
            ),
            "prediction": "Set the pull number to 5 with c = 1.414 (square root of 2, the default coefficient). Tool B has a mean of 0.000 and tool A has 0.667. Does the rule call A or B?",
            "explanation": (
                "The bonus grows slowly with the clock and shrinks as a tool is pulled, so a tool that is left alone gains bonus until it wins "
                "a call. Tool B's mean is the lower number almost throughout, yet its bonus lets it be selected whenever its index passes A's. "
                "A smaller c shrinks every bonus, so the same sequence of rewards leads to different choices."
            ),
            "application": (
                "When a controller must choose among components with thin records, an index of this shape gives a written reason for each "
                "call, which can be audited, instead of a vague claim that the system is curious."
            ),
            "assumptions": (
                "The rewards are the book's invented alternating sequence (A returns 1, 0, 1, 0, and so on; B returns 0, 1, 0, 1), not a "
                "test of the stochastic guarantee. Each tool is pulled once first, ties go to A, and the bonus uses unrounded values. Changing c "
                "changes the rule; the book's guarantee is stated for c equal to the square root of two with rewards in [0, 1]."
            ),
            "check": "At pull 3 the counts are 1 and 1 after 2 completed pulls and tool B has a mean of 0. With c = 1.414, what is B's bonus?",
            "answer": "ln 2 = 0.693, so the bonus is 1.414 x sqrt(0.693 / 1) = 1.414 x 0.8326 = 1.177 (rounded), the same as A's because both have been pulled once.",
            "provenance": "Constructed example: the chapter's ten-pull table with c equal to the square root of two (invented teaching rewards); the c = 0.5 case is defined for this reader.",
            "source_section": "A proved rule and ten constructed pulls",
            "source_anchor": "a-proved-rule-and-ten-constructed-pulls",
            "controls": [
                {"key": "pull", "label": "Pull number", "values": [3, 4, 5, 10], "default": 4},
                {"key": "c", "label": "Confidence coefficient c", "values": [math.sqrt(2), 0.5], "default": math.sqrt(2),
                 "value_labels": ["square root of 2 (about 1.414)", "0.5"]},
            ],
            "function": "ucb_picture",
        },
        {
            "id": "C11-D03",
            "title": "Information gain is not decision value",
            "question": "Can a check remove uncertainty about a claim and still be worth exactly nothing?",
            "equations": [EQ_GAIN, EQ_VOI],
            "symbols": (
                "Y is the proposition the decision turns on: every claim in the draft is supported. O is the report of a check. H is entropy in bits, "
                "a measure of uncertainty (1 bit for a fair coin, 0 when certain). I(Y; O) is the uncertainty about Y that O removes. VOI is the "
                "decision value: the average best expected utility with the report, minus the best without it. Releasing scores 100 if supported and 0 if not; "
                "requesting evidence scores 92."
            ),
            "prediction": "With prior 0.85 and a check that is right 0.60 of the time, does the check remove uncertainty, and does it change what the agent does?",
            "explanation": (
                "Entropy falls whenever the report is correlated with the claim, so the gain is positive. The value in Equation (11.4) is positive only if some report "
                "pushes the release score across the fixed value 92 of the alternative. When the reports leave the release score on the same side of 92 as the no-check score, "
                "the same action wins either way and VOI is zero, as at accuracy 0.60 with prior 0.85. Where that line falls depends on the prior: "
                "accuracy 0.70 is enough at prior 0.85 but not at prior 0.97."
            ),
            "application": (
                "Before paying for a check, write down which action follows each possible report. If it is the same action every time, the check is "
                "decoration, however interesting its output."
            ),
            "assumptions": (
                "A symmetric check (equally accurate on supported and unsupported claims), a single decision between releasing and requesting evidence, and a "
                "belief that the stated prior and accuracy are correct. Accuracy and prior here are constructed; a real check may be biased in one direction, which this "
                "model does not cover."
            ),
            "check": "With prior 0.85 and a check that is right 0.70 of the time, a report of unsupported leaves the release score at 70.8. Does that report change the action?",
            "answer": "P(supported and report unsupported) = 0.85 x 0.30 = 0.255 and P(report unsupported) = 0.36, so the release score is 100 x 0.255 / 0.36 = 70.8. That is below 92, which is also the action chosen before the check, so this report changes nothing; only the supported report (score 92.97) does.",
            "provenance": "Constructed example: the book's release score 85 and evidence score 92 (Table 6.1 values); the checks and their accuracies are defined for this reader.",
            "source_section": "Uncertainty is not the same as value",
            "source_anchor": "uncertainty-is-not-the-same-as-value",
            "controls": [
                {"key": "accuracy", "label": "How often the check is right", "values": [0.6, 0.7, 0.85, 0.95], "default": 0.85},
                {"key": "prior", "label": "Prior chance the claims are supported", "values": [0.85, 0.97], "default": 0.85},
            ],
            "function": "gain_value_picture",
        },
        {
            "id": "C11-D04",
            "title": "A worked price for one observation",
            "question": "How much is one call to a classifier worth, and how can the same classifier be worth zero in one decision and something in another?",
            "equations": [EQ_VOI],
            "symbols": (
                "A classifier reports flag with probability one third and clear with probability two thirds. Releasing scores 75 after flag and 90 after clear, plus the shift "
                "you choose; requesting evidence scores 92 either way. VOI is the average best score with the report minus the best score without it. The call cost "
                "is subtracted to give the net value."
            ),
            "prediction": "Add 10 to the release scores. Does the classifier become worth buying at a call cost of 2?",
            "explanation": (
                "With no shift, evidence wins under both reports and the value is exactly zero. A shift of 10 pushes the release score above 92 after clear but not after flag, "
                "so the best action now depends on the report. From a shift of 10 on, releasing already beats requesting evidence before observing (95 at shift 10), so the call can only "
                "rescue the flag branch. At a shift of 15 that branch still scores 90 against 92, so the call adds only 1/3 x (92 - 90) = 0.667."
            ),
            "application": (
                "Price a verification step against the specific decision it feeds. The same step, with the same accuracy and cost, can be a bargain for one decision and "
                "worthless for another."
            ),
            "assumptions": (
                "One decision, one observation, a coherent probability model, and a gross value that ignores any later decisions the observation could also inform. "
                "The conditional release scores are the book's constructed values; a real classifier's scores would have to be estimated, and a wrong estimate can flip the verdict."
            ),
            "check": "With a shift of 5, what is the gross value, and is the call worth buying at cost 2?",
            "answer": "Release scores 80 after flag and 95 after clear, and 90 before. With the call: 1/3 x 92 + 2/3 x 95 = 94.0, so gross value = 94 - 92 = 2.0. Net = 2 - 2 = 0, a tie.",
            "provenance": "Constructed example: the book's worked classifier (flag one third, release scores 75 and 90, evidence 92, shift 10 giving 7/3); the other shifts and costs are defined for this reader.",
            "source_section": "A worked price for one observation",
            "source_anchor": "a-worked-price-for-one-observation",
            "controls": [
                {"key": "shift", "label": "Added to both release scores", "values": [0, 5, 10, 15], "default": 10},
                {"key": "call_cost", "label": "Cost of the call", "values": [0, 2], "default": 0},
            ],
            "function": "classifier_picture",
        },
    ],
}

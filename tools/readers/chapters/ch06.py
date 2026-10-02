"""Chapter 6 reader: The Price of a Choice.

Four demonstrations built on Equations (6.2) to (6.4). Demonstrations 1, 2
and 4 call the laboratory's own expected-utility function
(math_ai_agents.chapters.ch06.evaluate), so the reader, the notebook and the
chapter skill agree. Every number is a constructed teaching value; the
values in Demonstrations 1 and 2 are the book's Table 6.1 values.
"""
import math

import numpy as np

from math_ai_agents.chapters.ch06 import evaluate
from readerkit import PALETTE, argmax_set, fmt, label_point, new_figure, signed

SUPPORTED = 100.0  # utility of a supported release (Table 6.1 scale)
HOUR_COST = 5.0    # book's elicited price of an hour of delay
SUPPORT = {"Release now": 0.85, "Request evidence": 0.97, "Escalate to a person": 0.995}

EQ_EU = r"\operatorname{EU}(a)=\sum_{y}p(y\mid a)\,u(y)"
EQ_ARGMAX = r"a^{\star}=\arg\max_{a\in\mathcal{A}}\operatorname{EU}(a)"
EQ_CE = r"u(\operatorname{CE})=\operatorname{E}\!\left[u(Y)\right]"


def release_actions(unsupported, day_cost, hour_cost=HOUR_COST, release_support=0.85):
    """Table 6.1 rows in the laboratory's input format (delay cost charged once per action)."""
    support = dict(SUPPORT, **{"Release now": release_support})
    costs = {"Release now": 0.0, "Request evidence": float(hour_cost), "Escalate to a person": float(day_cost)}
    return [
        {"name": name, "probabilities": [p, 1 - p], "utilities": [SUPPORTED, float(unsupported)], "cost": costs[name]}
        for name, p in support.items()
    ]


def lab_scores(actions):
    """Expected utility of each action, computed by the laboratory's evaluate()."""
    out = evaluate({"actions": actions})
    return {row["action"]: row["expected_utility"] for row in out["tables"]}


def written_eu(action):
    p, q = action["probabilities"]
    u1, u2 = action["utilities"]
    value = p * u1 + q * u2 - action["cost"]
    return (f"{action['name']}: {fmt(p, 3).rstrip('0')} x {fmt(u1, 0)} + {fmt(q, 3).rstrip('0')} x {signed(u2, 0)}"
            f" - {fmt(action['cost'], 0)} = {fmt(value, 1)}")


# Demonstration 1

def three_actions_picture(unsupported=0, day_cost=40):
    actions = release_actions(unsupported, day_cost)
    scores = lab_scores(actions)
    winners = argmax_set(scores)
    names = list(scores)
    fig, ax = new_figure(height=3.9)
    y = np.arange(len(names))[::-1]
    low = min(0.0, min(scores.values()) - 10)
    for yi, a in zip(y, actions):
        name = a["name"]
        before = scores[name] + a["cost"]
        color = PALETTE["teal"] if name in winners else "#8fa3b8"
        ax.barh(yi, scores[name] - low, left=low, height=0.56, color=color)
        if a["cost"] > 0:
            ax.barh(yi, a["cost"], left=scores[name], height=0.56, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1)
        tag = " (tied highest)" if name in winners and len(winners) > 1 else (" (highest)" if name in winners else "")
        ax.text(max(before, scores[name]) + 1.5, yi, f"{fmt(scores[name], 1)}{tag}", va="center", fontsize=11, color=PALETTE["ink"])
    ax.set_yticks(y, names)
    ax.set_xlim(low, 150)
    ax.set_xlabel("Expected utility (constructed units; hatched part is the delay cost)")
    ax.set_ylabel("Action")
    ax.set_title(f"Unsupported release worth {fmt(unsupported, 0)}, a day of delay costs {fmt(day_cost, 0)}", fontsize=11.5)
    ax.grid(axis="y", alpha=0)
    metrics = {name: fmt(scores[name], 1) for name in names}
    metrics["Chosen by Equation (6.3)"] = " and ".join(winners) + (" (tie)" if len(winners) > 1 else "")
    sums = ". ".join(written_eu(a) for a in actions)
    if len(winners) > 1:
        verdict = (f"{' and '.join(winners)} tie at {fmt(scores[winners[0]], 1)}. Equation (6.3) returns both as maximizers; "
                   "the rule alone does not choose between them, so a person or a stated tie-breaking rule must.")
    else:
        verdict = f"{winners[0]} has the highest expected utility, so Equation (6.3) selects it."
    ranking = sorted(names, key=lambda n: -scores[n])
    interpretation = (f"{sums}. {verdict} Order from highest to lowest: {', '.join(ranking)}. "
                      "The support probabilities never changed; only the declared values did.")
    return fig, metrics, interpretation


# Demonstration 2

def hour_price_picture(hour_cost=5, release_support=0.85):
    actions = release_actions(0, 40, hour_cost=hour_cost, release_support=release_support)[:2]
    scores = lab_scores(actions)
    release, evidence = scores["Release now"], scores["Request evidence"]
    break_even = SUPPORT["Request evidence"] * SUPPORTED - release_support * SUPPORTED
    h = np.linspace(0, 20, 81)
    fig, ax = new_figure(height=4.1)
    ax.plot(h, np.full_like(h, release_support * SUPPORTED), color=PALETTE["navy"])
    ax.plot(h, SUPPORT["Request evidence"] * SUPPORTED - h, color=PALETTE["teal"])
    ax.axvline(break_even, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    ax.plot([hour_cost], [evidence], "o", color=PALETTE["teal"], markersize=8)
    ax.plot([hour_cost], [release], "o", color=PALETTE["navy"], markersize=8)
    label_point(ax, 20, release_support * SUPPORTED, "Release now", color=PALETTE["navy"], dx=-4, dy=6, ha="right")
    label_point(ax, 20, SUPPORT["Request evidence"] * SUPPORTED - 20, "Request evidence", color=PALETTE["teal"], dx=-4, dy=-8, ha="right", va="top")
    label_point(ax, break_even, 72, f"break-even {fmt(break_even, 1)}", color=PALETTE["ink"], dx=5, dy=0, va="center")
    label_point(ax, 0.2, 99.5, "evidence wins to the left", color=PALETTE["teal"], dx=0, dy=0, va="top")
    ax.set_xlim(0, 20)
    ax.set_ylim(70, 100)
    ax.set_xlabel("Price of one hour of delay (utility points)")
    ax.set_ylabel("Expected utility")
    ax.set_title(f"Hour priced at {fmt(hour_cost, 0)}; release support {fmt(release_support, 2)}", fontsize=11.5)
    if math.isclose(evidence, release, abs_tol=1e-9):
        verdict = ("The two actions tie exactly, so Equation (6.3) has two maximizers and the price of an hour "
                   "sits on the threshold. The person who owns the values has to say which side they are on.")
        chosen = "tie"
    elif evidence > release:
        verdict = f"Request evidence wins because {fmt(hour_cost, 0)} is below the break-even price."
        chosen = "Request evidence"
    else:
        verdict = f"Release now wins because {fmt(hour_cost, 0)} is above the break-even price."
        chosen = "Release now"
    metrics = {
        "Release now": fmt(release, 1),
        "Request evidence": fmt(evidence, 1),
        "Break-even hour price": fmt(break_even, 1),
        "Chosen": chosen,
    }
    interpretation = (
        f"Break-even price = 0.97 x 100 - {fmt(release_support, 2)} x 100 = 97.0 - {fmt(release_support * SUPPORTED, 1)}"
        f" = {fmt(break_even, 1)} points per hour. At {fmt(hour_cost, 0)} points, request evidence scores 97.0 - "
        f"{fmt(hour_cost, 0)} = {fmt(evidence, 1)} against {fmt(release, 1)} for releasing now. {verdict} "
        "Only one question needs an answer from a person: is an hour worth more or less than the break-even price?"
    )
    return fig, metrics, interpretation


# Demonstration 3

SHAPES = {
    "sqrt": ("square root", lambda x: np.sqrt(x), lambda u: u ** 2, "sqrt"),
    "linear": ("straight line", lambda x: x, lambda u: u, ""),
    "square": ("square", lambda x: x ** 2, lambda u: np.sqrt(u), "square"),
}


def certainty_picture(shape="sqrt", win_probability=0.5):
    name, u, inverse, _ = SHAPES[shape]
    q = float(win_probability)
    top = 100.0
    expected_payoff = q * top
    expected_utility = q * float(u(top)) + (1 - q) * float(u(0.0))
    ce = float(inverse(expected_utility))
    gap = expected_payoff - ce
    x = np.linspace(0, top, 201)
    scale = float(u(top))
    fig, ax = new_figure(height=4.3)
    ax.plot(x, u(x) / scale, color=PALETTE["teal"])
    ax.plot([0, top], [0, 1], linestyle=":", color=PALETTE["grey"], linewidth=1.4)
    level = expected_utility / scale
    ax.plot([min(ce, expected_payoff), max(ce, expected_payoff)], [level, level], linestyle="dashed", color=PALETTE["gold"], linewidth=1.6)
    ax.plot([expected_payoff], [level], "s", color=PALETTE["navy"], markersize=8)
    ax.plot([ce], [level], "o", color=PALETTE["terracotta"], markersize=8)
    # Labels carry no background box, so they never erase part of a curve; they sit on the empty side of it.
    # A bending-down curve lies above the dotted diagonal, a bending-up curve below it.
    down = shape == "sqrt"
    if math.isclose(ce, expected_payoff, abs_tol=1e-9):
        label_point(ax, ce, level, f"certainty equivalent\n= mean = {fmt(ce, 1)}", color=PALETTE["ink"], dx=-4, dy=14,
                    ha="right", va="bottom")
    elif down:
        label_point(ax, ce, level, f"certainty\nequivalent {fmt(ce, 1)}", color=PALETTE["terracotta"], dx=max(0, 30 - ce), dy=14,
                    ha="right", va="bottom")
        label_point(ax, expected_payoff, level, f"mean payoff {fmt(expected_payoff, 1)}", color=PALETTE["navy"], dx=0, dy=-14,
                    ha="left", va="top")
    else:
        label_point(ax, ce, level, f"certainty\nequivalent {fmt(ce, 1)}", color=PALETTE["terracotta"], dx=-4, dy=-14,
                    ha="left", va="top")
        label_point(ax, expected_payoff, level, f"mean payoff {fmt(expected_payoff, 1)}", color=PALETTE["navy"], dx=-4, dy=14,
                    ha="right", va="bottom")
    ax.set_xlim(0, 112)
    ax.set_xticks(range(0, 101, 20))
    ax.set_ylim(-0.03, 1.08)
    ax.set_xlabel("Payoff (constructed units)")
    ax.set_ylabel("Utility, rescaled so u(0) = 0 and u(100) = 1")
    ax.set_title(f"Utility shape: {name}; gamble pays 100 with probability {fmt(q, 1)}", fontsize=11.5)
    if shape == "sqrt":
        calc = (f"E[u] = {fmt(q, 1)} x sqrt(100) + {fmt(1 - q, 1)} x sqrt(0) = {fmt(expected_utility, 1)}, "
                f"so CE = {fmt(expected_utility, 1)} x {fmt(expected_utility, 1)} = {fmt(ce, 1)}")
    elif shape == "linear":
        calc = (f"E[u] = {fmt(q, 1)} x 100 + {fmt(1 - q, 1)} x 0 = {fmt(expected_utility, 1)}, so CE = {fmt(ce, 1)}")
    else:
        calc = (f"E[u] = {fmt(q, 1)} x 100 x 100 + {fmt(1 - q, 1)} x 0 = {fmt(expected_utility, 0)}, "
                f"so CE = sqrt({fmt(expected_utility, 0)}) = {fmt(ce, 2)}")
    if gap > 1e-9:
        meaning = (f"The agent would trade the gamble for a guaranteed {fmt(ce, 1)}, giving up {fmt(gap, 1)} of mean payoff "
                   "to remove the variance. That gap is the price of avoiding risk under this curve.")
    elif gap < -1e-9:
        meaning = (f"The certainty equivalent is above the mean, so the gap {fmt(gap, 2)} is negative: this upward-bending "
                   "curve values the gamble more than its average, which is what seeking risk means here.")
    else:
        meaning = "The gap is zero: a straight-line utility is indifferent to risk."
    metrics = {
        "Mean payoff": fmt(expected_payoff, 1),
        "E[u(Y)] for this curve (not comparable across curves)": fmt(expected_utility, 2),
        "Certainty equivalent": fmt(ce, 2),
        "Mean minus certainty equivalent": fmt(gap, 2),
    }
    interpretation = (f"Mean payoff = {fmt(q, 1)} x 100 = {fmt(expected_payoff, 1)}. {calc}. Mean minus certainty "
                      f"equivalent = {fmt(expected_payoff, 1)} - {fmt(ce, 2)} = {fmt(gap, 2)}. {meaning}")
    return fig, metrics, interpretation


# Demonstration 4

CASES = 100
CONFIDENCE = 0.5 + 0.005 * (np.arange(CASES) + 0.5)  # constructed: 0.5025, 0.5075, ..., 0.9975


def lab_answers(p, wrong, decline):
    """The laboratory's evaluate() chooses between answering and declining for one case."""
    actions = [
        {"name": "answer", "probabilities": [float(p), 1 - float(p)], "utilities": [1.0, float(wrong)], "cost": 0},
        {"name": "decline", "probabilities": [1.0], "utilities": [float(decline)], "cost": 0},
    ]
    return evaluate({"actions": actions})["metrics"]["selected_action"] == "answer"


def coverage_picture(wrong=-4, decline=0):
    wrong, decline = float(wrong), float(decline)
    threshold = (decline - wrong) / (1 - wrong)
    answered = np.array([lab_answers(p, wrong, decline) for p in CONFIDENCE])
    closed_form = CONFIDENCE > threshold
    if not np.array_equal(answered, closed_form):
        raise AssertionError("laboratory decision disagrees with the closed-form threshold")
    n = int(answered.sum())
    coverage = n / CASES
    risk = float(np.mean(1 - CONFIDENCE[answered])) if n else None
    per_case = float(np.mean(np.where(answered, CONFIDENCE + (1 - CONFIDENCE) * wrong, decline)))
    order = np.argsort(-CONFIDENCE)
    k = np.arange(1, CASES + 1)
    curve_cov = k / CASES
    curve_risk = np.cumsum(1 - CONFIDENCE[order]) / k

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    p = np.linspace(0.5, 1, 101)
    left.plot(p, p + (1 - p) * wrong, color=PALETTE["teal"])
    left.plot(p, np.full_like(p, decline), color=PALETTE["terracotta"])
    label_point(left, 0.9, 0.9 + 0.1 * wrong, "answer", color=PALETTE["teal"], dx=-8, dy=6, ha="right")
    label_point(left, 1.0, decline, "decline", color=PALETTE["terracotta"], dx=-4, dy=-6, ha="right", va="top")
    if 0.5 <= threshold <= 1:
        left.axvline(threshold, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
        near_left = threshold < 0.6
        label_point(left, threshold, wrong * 0.5 + 0.25, f"t = {fmt(threshold, 2)}", dx=5 if near_left else -5, dy=0,
                    ha="left" if near_left else "right", va="center")
    else:
        label_point(left, 0.75, wrong * 0.5 + 0.25, f"t = {fmt(threshold, 2)} is below every case", dx=0, dy=0, ha="center", va="center")
    left.set_xlabel("Confidence p that the answer is correct")
    left.set_ylabel("Expected utility of the case")
    left.set_ylim(min(wrong * 0.5 - 0.3, decline - 0.3), 1.15)
    left.set_title("Answer when its expected utility is higher", fontsize=11.5)

    right.plot(curve_cov, curve_risk, color=PALETTE["navy"])
    right.plot([1.0], [curve_risk[-1]], "s", color=PALETTE["grey"], markersize=7)
    if n:
        right.plot([coverage], [risk], "o", color=PALETTE["teal"], markersize=9)
    if n == CASES:
        label_point(right, 1.0, curve_risk[-1], f"chosen: answer all, error {fmt(curve_risk[-1], 3)}", color=PALETTE["teal"], dx=-6, dy=8, ha="right")
    else:
        label_point(right, 1.0, curve_risk[-1], f"answer all: error {fmt(curve_risk[-1], 3)}", color=PALETTE["grey"], dx=-6, dy=8, ha="right")
        if n:
            label_point(right, coverage, risk, f"chosen\ncoverage {fmt(coverage, 2)}, error {fmt(risk, 3)}", color=PALETTE["teal"],
                        dx=6 if coverage < 0.5 else -6, dy=-10, ha="left" if coverage < 0.5 else "right", va="top",
                        ).set_bbox({"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9})
    right.set_xlim(0, 1.04)
    right.set_ylim(0, 0.3)
    right.set_xlabel("Coverage (share of the 100 cases answered)")
    right.set_ylabel("Expected error rate among answered cases")
    right.set_title("Risk against coverage", fontsize=11.5)

    risk_text = fmt(risk, 3) if risk is not None else "undefined (no case is answered)"
    metrics = {
        "Answer threshold t": fmt(threshold, 2),
        "Cases answered": f"{n} of {CASES}",
        "Coverage": fmt(coverage, 2),
        "Expected error rate when answering": risk_text,
        "Expected utility per case": fmt(per_case, 3),
    }
    calc = (f"Answer when p x 1 + (1 - p) x {signed(wrong, 0)} > {signed(decline, 1)}, that is when p > t = "
            f"({fmt(decline, 1)} - {signed(wrong, 0)}) / (1 - {signed(wrong, 0)}) = {fmt(decline - wrong, 1)} / {fmt(1 - wrong, 0)} = {fmt(threshold, 2)}.")
    if n == CASES:
        detail = (f" Every constructed case has p above {fmt(threshold, 2)}, so coverage is 1.00 and the expected error rate is "
                  f"1 - (0.5025 + 0.9975) / 2 = {fmt(risk, 3)}.")
    elif n:
        lo = CONFIDENCE[answered].min()
        detail = (f" The {n} cases from p = {lo:.4f} to 0.9975 are answered, so coverage = {n}/100 = {fmt(coverage, 2)} and their "
                  f"expected error rate is 1 - ({lo:.4f} + 0.9975) / 2 = {risk_text}.")
    else:
        detail = " No case clears the threshold, so coverage is 0 and the error rate among answered cases is undefined."
    interpretation = (calc + detail + " A more expensive wrong answer raises t and lowers coverage; a more expensive "
                      "decline lowers t and raises coverage. The value attached to declining picks the point on the curve.")
    return fig, metrics, interpretation


CHAPTER = {
    "number": 6,
    "title": "The Price of a Choice",
    "subtitle": "Probabilities say what an action is likely to lead to; utilities say what those outcomes are worth. A decision needs both.",
    "summary": (
        "These four demonstrations follow the chapter's document controller. It must choose among releasing a report now, "
        "requesting more evidence, and escalating to a person. Each demonstration changes one declared value and shows "
        "which comparison moves and which stays fixed."
    ),
    "demos": [
        {
            "id": "C06-D01",
            "title": "Three actions, one rule",
            "question": "If the probabilities stay fixed, can changing what an unsupported release is worth change which action wins?",
            "equations": [EQ_EU, EQ_ARGMAX],
            "symbols": (
                "a is an action, y an outcome (supported or unsupported release), p(y | a) the probability of outcome y "
                "under action a, and u(y) its declared utility. A supported release is worth 100. Delay subtracts the same "
                "amount from every outcome, which is the same as subtracting it once from the average because the "
                "probabilities add to one. The arg max picks the action with the largest EU(a), the expected utility of action a."
            ),
            "prediction": "Make an unsupported release worth -400 instead of 0. Which action loses the most, and does the winner change?",
            "explanation": (
                "Each action's expected utility multiplies each outcome's worth by its probability and adds the products, "
                "then Equation (6.3) takes the largest. The probabilities here are the book's Table 6.1 values and never "
                "move in this demonstration. Only the value of an unsupported release and the price of a day of delay change."
            ),
            "application": (
                "Before trusting an automated choice, write the table: one row per action, including asking for evidence and "
                "handing the decision to a person. Then check whether a change in a value you are unsure of changes the winner."
            ),
            "assumptions": (
                "One decision, two mutually exclusive outcomes per action, and utilities on one shared scale. The probabilities "
                "and utilities are constructed teaching values from Table 6.1, not estimates for any real controller. "
                "Expected utility compares actions; it does not say whose values the numbers represent."
            ),
            "check": "With an unsupported release worth -400 and a day costing 40, what does releasing now score?",
            "answer": "0.85 x 100 + 0.15 x (-400) = 85 - 60 = 25. Requesting evidence scores 92 - 12 = 80, so it still wins, and escalation (57.5) now beats releasing now.",
            "provenance": "Constructed example: the book's Table 6.1 values, computed with the laboratory's expected-utility function.",
            "source_section": "The decision rule",
            "source_anchor": "the-decision-rule",
            "controls": [
                {"key": "unsupported", "label": "Utility of an unsupported release", "values": [0, -100, -400], "default": 0},
                {"key": "day_cost", "label": "Cost of a day of delay (escalation)", "values": [10, 40], "default": 40},
            ],
            "function": "three_actions_picture",
        },
        {
            "id": "C06-D02",
            "title": "Elicit one number: the price of an hour",
            "question": "Between releasing now and requesting evidence, what single number decides the choice?",
            "equations": [EQ_ARGMAX],
            "symbols": (
                "EU(a) is the expected utility of action a. Releasing now succeeds with the chosen support probability; "
                "requesting evidence succeeds with probability 0.97 but costs one hour, priced in utility points. An "
                "unsupported release is worth 0 and a supported one 100."
            ),
            "prediction": "With release support 0.85, if an hour of delay is worth exactly 12 points, does Equation (6.3) choose releasing now, requesting evidence, or neither because they tie?",
            "explanation": (
                "Requesting evidence scores 97 minus the price of an hour; releasing now scores 100 times its support "
                "probability. The lines cross at the break-even price. A person does not need to state a whole utility "
                "function, only which side of that one threshold they are on."
            ),
            "application": (
                "When a decision depends on a value nobody has written down, compute the threshold at which the decision "
                "flips and ask the person responsible which side they are on. That question is answerable; asking what an "
                "outcome is worth in the abstract usually is not."
            ),
            "assumptions": (
                "Two actions, utilities on the Table 6.1 scale, and delay priced additively. The 0.85, 0.90 and 0.97 support "
                "probabilities are constructed. A tie is reported as a tie, because Equation (6.3) does not break ties."
            ),
            "check": "If releasing now had support probability 0.90, what hour price would make the two actions tie?",
            "answer": "97 - 90 = 7 points. Below 7 requesting evidence wins; above 7 releasing now wins.",
            "provenance": "Constructed example: the book's Table 6.1 values, computed with the laboratory's expected-utility function.",
            "source_section": "Eliciting one number",
            "source_anchor": "eliciting-one-number",
            "controls": [
                {"key": "hour_cost", "label": "Price of an hour of delay", "values": [3, 5, 12, 15], "default": 5},
                {"key": "release_support", "label": "Support probability when releasing now", "values": [0.85, 0.9], "default": 0.85},
            ],
            "function": "hour_price_picture",
        },
        {
            "id": "C06-D03",
            "title": "Risk is the shape of the utility curve",
            "question": "How much mean payoff would an agent give up to replace a gamble with a sure amount?",
            "equations": [EQ_CE, EQ_EU],
            "symbols": (
                "Y is the payoff of a gamble that pays 100 with the chosen probability and 0 otherwise. u is the utility "
                "curve, E[u(Y)] its probability-weighted average, and CE the certainty equivalent: the sure payoff whose "
                "utility equals that average. The plot rescales utility to run from 0 to 1, which does not move CE."
            ),
            "prediction": "For a curve that bends down, is the certainty equivalent above or below the mean payoff of 50?",
            "explanation": (
                "Average the utilities, not the payoffs, then ask which sure payoff has that utility. A curve that bends "
                "down puts the certainty equivalent below the mean; a straight line puts it at the mean; a curve that bends "
                "up puts it above. The gap is a number in payoff units, not a temperament."
            ),
            "application": (
                "When a team says a system should be cautious, ask for the curve or for one certainty equivalent. A stated "
                "gap such as 25 on a 50 mean can be checked and argued about; the word cautious cannot."
            ),
            "assumptions": (
                "A single two-outcome gamble with constructed payoffs and probabilities. The square-root and square curves "
                "are illustrations of bending down and bending up, not elicited preferences. One certainty equivalent is "
                "consistent with risk aversion but does not prove the whole curve is concave."
            ),
            "check": "With a square-root utility and a gamble paying 100 with probability 0.8, what is the certainty equivalent?",
            "answer": "E[u] = 0.8 x 10 = 8, so CE = 8 x 8 = 64, which is 16 below the mean payoff of 80.",
            "provenance": "Constructed example: the chapter's worked certainty equivalent (100 or 0 with equal chance) and one changed probability.",
            "source_section": "A worked certainty equivalent",
            "source_anchor": "a-worked-certainty-equivalent",
            "controls": [
                {"key": "shape", "label": "Utility curve", "values": ["sqrt", "linear", "square"], "default": "sqrt",
                 "value_labels": ["Bends down: square root", "Straight line", "Bends up: square"]},
                {"key": "win_probability", "label": "Probability the gamble pays 100", "values": [0.5, 0.8], "default": 0.5},
            ],
            "function": "certainty_picture",
        },
        {
            "id": "C06-D04",
            "title": "Declining is an action with a price",
            "question": "How does the value placed on declining decide how many cases an agent answers and how often it is wrong?",
            "equations": [EQ_ARGMAX, EQ_EU],
            "symbols": (
                "For each case the agent compares two actions. Answer: utility 1 if correct, w (the chosen wrong-answer "
                "utility) if not, with p the probability the answer is correct. Decline: d (the chosen utility of declining) for certain. "
                "Coverage is the share of cases answered, and the error rate is measured only over answered cases."
            ),
            "prediction": "Make a wrong answer cost 9 instead of 4. Does coverage go up or down, and what happens to the error rate?",
            "explanation": (
                "Answering wins when p x 1 + (1 - p) x w exceeds the value of declining d, which happens when p is above "
                "the threshold t = (d - w) / (1 - w). Each threshold picks one point on the risk and coverage curve, so the same agent "
                "can be reported at very different error rates depending on the price of declining."
            ),
            "application": (
                "When a system reports an error rate, ask for its coverage and for the value it assigns to declining. Two "
                "error rates at different coverage describe different services, and the price of declining is what chose between them."
            ),
            "assumptions": (
                "One hundred constructed cases whose confidences are spread evenly from 0.5025 to 0.9975 and assumed to be "
                "calibrated, so a case with confidence p is correct with probability p. Real confidence scores need not be "
                "calibrated; the error rates shown are expected values under that assumption, not observed rates."
            ),
            "check": "With a wrong answer worth -4 and declining worth 0, what is the answer threshold t?",
            "answer": "t = (0 - (-4)) / (1 - (-4)) = 4 / 5 = 0.80, so only the 40 cases with p above 0.80 are answered.",
            "provenance": "Constructed example: 100 calibrated cases defined for this reader; each answer or decline choice is computed with the laboratory's expected-utility function.",
            "source_section": "The cost of declining, measured",
            "source_anchor": "the-cost-of-declining-measured",
            "controls": [
                {"key": "wrong", "label": "Utility of a wrong answer", "values": [-1, -4, -9], "default": -4},
                {"key": "decline", "label": "Utility of declining", "values": [-0.5, 0], "default": 0},
            ],
            "function": "coverage_picture",
        },
    ],
}

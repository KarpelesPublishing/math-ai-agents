"""Chapter 12 reader: Credit for Consequences.

Four demonstrations built on Equations (12.1) to (12.4). Demonstration 1 calls
the laboratory's own trajectory-credit function
(math_ai_agents.chapters.ch12.evaluate) for the outcome-rule and one-step-rule
updates, and Demonstration 4 checks its TD error against the same function, so
the reader, the notebook and the chapter skill agree. Demonstration 2 runs the
two rules in batch form on the book's eight-episode construction and checks the
result against the closed form. Every number is a constructed teaching value;
the values in Demonstrations 1, 2 and 4 are the book's own worked numbers.
"""
import math

import numpy as np

from math_ai_agents.chapters.ch12 import evaluate
from readerkit import PALETTE, fmt, new_figure, signed

EQ_OUTCOME = r"\hat V_{t+1}(x_t) = \hat V_t(x_t) + \alpha\big[\operatorname{Ret}_t - \hat V_t(x_t)\big]."
EQ_DELTA = r"\delta_t = r_t + \gamma\,\hat V_t(x_{t+1}) - \hat V_t(x_t)."
EQ_TD = r"\hat V_{t+1}(x_t) = \hat V_t(x_t) + \alpha\,\delta_t."
EQ_LAMBDA = (
    r"\operatorname{Ret}^{\lambda}_t = (1-\lambda)\sum_{k=1}^{N-t-1}\lambda^{\,k-1}"
    r"\Big[\textstyle\sum_{j=0}^{k-1}\gamma^{\,j} r_{t+j} + \gamma^{\,k}\hat V_t(x_{t+k})\Big] "
    r"+ \lambda^{N-t-1}\operatorname{Ret}_t."
)

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


def lab_one_pass(states, rewards, values, alpha, discount=1, terminal=True, lam=0):
    """The laboratory's single sequential pass; returns its three value maps and TD errors."""
    out = evaluate({
        "states": states, "rewards": rewards, "discount": discount, "learning_rate": alpha,
        "lambda": lam, "terminal": terminal, "values": values,
    })
    return out["metrics"], out["series"][1]["y"]


# Demonstration 1

def one_trajectory_picture(alpha=0.1, final_reward=1):
    alpha, final_reward = float(alpha), float(final_reward)
    states = ["state 1", "state 2", "state 3", "state 4", "end"]
    values = {s: 0.5 for s in states[:4]}
    values["end"] = 0.0
    metrics_lab, deltas = lab_one_pass(states, [0, 0, 0, final_reward], values, alpha)
    outcome = [metrics_lab["monte_carlo_values"][s] for s in states[:4]]
    onestep = [metrics_lab["td_zero_values"][s] for s in states[:4]]
    x = np.arange(4)
    fig, ax = new_figure(height=4.2)
    ax.axhline(0.5, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    ax.bar(x - 0.2, outcome, width=0.38, color="white", edgecolor=PALETTE["navy"], hatch="///", linewidth=1.3)
    ax.bar(x + 0.2, onestep, width=0.38, color=PALETTE["teal"])
    for xi, o, t in zip(x, outcome, onestep):
        ax.text(xi - 0.2, o + 0.02, fmt(o, 3), ha="center", va="bottom", fontsize=10.5, color=PALETTE["navy"]).set_bbox(BOX)
        ax.text(xi + 0.2, t + 0.02, fmt(t, 3), ha="center", va="bottom", fontsize=10.5, color=PALETTE["teal"]).set_bbox(BOX)
    ax.set_xticks(x, ["state 1", "state 2", "state 3", "state 4"])
    ax.set_ylim(0, 1.15)
    ax.set_xlim(-0.6, 3.6)
    ax.text(-0.55, 1.1, "hatched = outcome rule; solid = one-step rule; dashed line = start, 0.5", ha="left", va="top", fontsize=10.5, color=PALETTE["ink"]).set_bbox(BOX)
    ax.set_xlabel("State visited on the run (first to fourth)")
    ax.set_ylabel("Estimate after one run")
    ax.set_title(f"Step size {fmt(alpha, 1)}, the run pays {fmt(final_reward, 0)} at the end", fontsize=11.5)
    moved_onestep = sum(1 for v in onestep if abs(v - 0.5) > 1e-12)
    moved_outcome = sum(1 for v in outcome if abs(v - 0.5) > 1e-12)
    metrics = {
        "Outcome rule, each of the 4 states": fmt(outcome[0], 3),
        "One-step rule, states 1 to 3": fmt(onestep[0], 3),
        "One-step rule, state 4": fmt(onestep[3], 3),
        "States moved (outcome / one-step)": f"{moved_outcome} / {moved_onestep}",
    }
    if abs(final_reward - 0.5) < 1e-12:
        verdict = "Here the final reward equals the estimates, so every error is zero and neither rule moves anything."
    else:
        direction = "raises" if final_reward > 0.5 else "lowers"
        verdict = (f"The outcome rule {direction} all four identical predictions in one pass; the one-step rule {direction} only "
                   "state 4 and leaves states 1 to 3 for later runs. Neither movement says which action deserved the result.")
    interpretation = (
        f"Outcome rule, every state: 0.5 + {fmt(alpha, 1)} x ({fmt(final_reward, 0)} - 0.5) = {fmt(outcome[0], 3)}. "
        f"One-step error at state 4: delta = {fmt(final_reward, 0)} + 0 - 0.5 = {fmt(deltas[3], 1)}, so state 4 becomes "
        f"0.5 + {fmt(alpha, 1)} x {signed(deltas[3], 1)} = {fmt(onestep[3], 3)}. The first three errors are 0 + 0.5 - 0.5 = 0. {verdict}"
    )
    return fig, metrics, interpretation


# Demonstration 2

def batch_values(ones_in_b_only, a_final):
    """Batch form of both rules on the eight episodes; returns (A, B) for each rule.

    Episode 1: A then B, no reward, then B ends with reward a_final. Seven more
    episodes start in B and end at once with rewards: ones_in_b_only ones, then zeros.
    """
    b_rewards = [float(a_final)] + [1.0] * ones_in_b_only + [0.0] * (7 - ones_in_b_only)
    # Outcome rule: each state moves toward the mean of the returns that followed it.
    out_b = sum(b_rewards) / 8
    out_a = float(a_final)
    # One-step rule: repeated batch presentation of every transition, small step size.
    va = vb = 0.5
    step = 0.05
    for _ in range(6000):
        da = vb - va                            # the one A to B transition: reward 0
        db = sum(r - vb for r in b_rewards) / 8  # B's eight transitions into the end (value 0)
        va, vb = va + step * da, vb + step * db
    return (out_a, out_b), (va, vb)


def eight_episodes_picture(ones_in_b_only=6, a_final=0):
    k, a = int(ones_in_b_only), int(a_final)
    (out_a, out_b), (td_a, td_b) = batch_values(k, a)
    b_true = (k + a) / 8
    if not (math.isclose(td_b, b_true, abs_tol=1e-6) and math.isclose(td_a, b_true, abs_tol=1e-6)
            and math.isclose(out_b, b_true, abs_tol=1e-12)):
        raise AssertionError("batch result disagrees with the closed form")
    td_a, td_b = b_true, b_true  # exact limits (the iteration above confirms them)
    gap = abs(td_a - out_a)
    fig, ax = new_figure(height=4.2)
    x = np.array([0, 1])
    ax.bar(x - 0.2, [out_a, out_b], width=0.38, color="white", edgecolor=PALETTE["navy"], hatch="///", linewidth=1.3)
    ax.bar(x + 0.2, [td_a, td_b], width=0.38, color=PALETTE["teal"])
    for xi, o, t in zip(x, [out_a, out_b], [td_a, td_b]):
        ax.text(xi - 0.2, o + 0.02, fmt(o, 3), ha="center", va="bottom", fontsize=10.5, color=PALETTE["navy"])
        ax.text(xi + 0.2, t + 0.02, fmt(t, 3), ha="center", va="bottom", fontsize=10.5, color=PALETTE["teal"])
    ax.set_xticks(x, ["Value of A (seen once)", "Value of B (seen 8 times)"])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 1.25)
    ax.text(-0.55, 1.2, "hatched = outcome rule; solid = one-step rule", ha="left", va="top", fontsize=10.5, color=PALETTE["ink"]).set_bbox(BOX)
    ax.set_xlabel("State")
    ax.set_ylabel("Value each rule settles on")
    ax.set_title(f"Seven B-only episodes with {k} paying 1; the A episode ends with {a}", fontsize=11.5)
    metrics = {
        "Value of B (both rules)": fmt(b_true, 3),
        "Value of A, outcome rule": fmt(out_a, 3),
        "Value of A, one-step rule": fmt(td_a, 3),
        "Disagreement about A": fmt(gap, 3),
    }
    if gap < 1e-12:
        verdict = "The one episode that passed through A happened to end at B's average, so the two rules agree about A."
    else:
        verdict = (f"The outcome rule fits the single A episode exactly (error 0) but is {fmt(gap, 3)} away from B's value; "
                   "the one-step rule gives A the value of its successor B, using the seven episodes that never contained A.")
    interpretation = (
        f"B's returns are {k} + {a} ones in 8 visits, so B = ({k} + {a}) / 8 = {fmt(b_true, 3)} under either rule. "
        f"The outcome rule gives A the one return it saw: {a}. The one-step rule gives A = 0 + B = {fmt(td_a, 3)}. "
        f"Disagreement about A = |{fmt(td_a, 3)} - {fmt(out_a, 3)}| = {fmt(gap, 3)}. {verdict}"
    )
    return fig, metrics, interpretation


# Demonstration 3

def lambda_weights(lam, remaining):
    """Equation (12.4) weights: (1 - lam) lam^(k-1) for k = 1..n-1, then lam^(n-1) on the full return."""
    n = int(remaining)
    w = [(1 - lam) * lam ** (k - 1) for k in range(1, n)]
    w.append(lam ** (n - 1))
    return w


def lambda_picture(lam=0.9, remaining=8):
    lam, n = float(lam), int(remaining)
    w = lambda_weights(lam, n)
    total = sum(w)
    fig, ax = new_figure(height=4.2)
    ks = np.arange(1, n + 1)
    ax.bar(ks[:-1], w[:-1], width=0.62, color=PALETTE["teal"])
    ax.bar([n], [w[-1]], width=0.62, color="white", edgecolor=PALETTE["terracotta"], hatch="///", linewidth=1.3)
    for k, v in zip(ks, w):
        if v >= 0.0005 or k == n:  # the full-return bar is always labelled, even when its weight is tiny or zero
            text = "0" if v == 0 else ("<0.001" if v < 0.0005 else fmt(v, 3))
            ax.text(k, v + 0.015, text, ha="center", va="bottom", fontsize=10.5,
                    color=PALETTE["terracotta"] if k == n else PALETTE["teal"])
    ax.set_xticks(ks, [str(k) if k < n else f"{k}\nfull return" for k in ks])
    ax.set_xlim(0.4, n + 0.6)
    ax.set_ylim(0, 1.12)
    ax.set_xlabel("Target k (k-step lookahead; the last bar is the complete return)")
    ax.set_ylabel("Weight in the lambda target")
    ax.set_title(f"Lambda = {fmt(lam, 1)}, {n} transitions remaining", fontsize=11.5)
    terminal = w[-1]
    boot = total - terminal
    metrics = {
        "Weight on the one-step target": fmt(w[0], 4),
        "Weight on the full return": fmt(terminal, 4),
        "Weight on the other lookahead targets": fmt(boot - w[0], 4),
        "Weights add to": fmt(total, 4),
    }
    if lam == 0:
        note = "At lambda = 0 all weight sits on the one-step target, which is the target inside Equation (12.2)."
    elif lam == 1:
        note = "At lambda = 1 all weight sits on the complete return, which is the target in Equation (12.1)."
    else:
        note = "Raising lambda moves weight from the short targets toward the complete return, but the weights always add to one."
    interpretation = (
        f"First weight = 1 - {fmt(lam, 1)} = {fmt(w[0], 4)}. Full-return weight = {fmt(lam, 1)}^{n - 1} = {fmt(terminal, 4)}. "
        f"Check: lookahead weights add to 1 - {fmt(lam, 1)}^{n - 1} = {fmt(1 - terminal, 4)}, and {fmt(1 - terminal, 4)} + "
        f"{fmt(terminal, 4)} = {fmt(total, 4)}. {note}"
    )
    return fig, metrics, interpretation


# Demonstration 4

REWARD = -0.02  # the book's cost of the first, unhelpful search


def td_error_picture(prior=0.2, successor=0.5):
    prior, successor = float(prior), float(successor)
    metrics_lab, deltas = lab_one_pass(["before", "after"], [REWARD], {"before": prior, "after": successor},
                                       0.5, terminal=False)
    delta = deltas[0]
    if not math.isclose(delta, REWARD + successor - prior, abs_tol=1e-12):
        raise AssertionError("laboratory TD error disagrees with Equation (12.2)")
    parts = [REWARD, successor, -prior, delta]
    names = ["reward r", "successor\nestimate", "minus own\nestimate", "error delta"]
    colors = [PALETTE["gold"], PALETTE["navy"], PALETTE["grey"], PALETTE["terracotta"]]
    fig, ax = new_figure(height=4.2)
    for i, (v, c) in enumerate(zip(parts, colors)):
        ax.bar(i, v, width=0.6, color=c if i < 3 else "white", edgecolor=c, hatch=None if i < 3 else "///", linewidth=1.3)
        if v >= 0:
            ax.annotate(fmt(v, 2), (i, v), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        else:
            ax.annotate(fmt(v, 2), (i, v), xytext=(0, -4), textcoords="offset points", ha="center", va="top", fontsize=10.5, color=PALETTE["ink"])
    ax.axhline(0, color=PALETTE["ink"], linewidth=1)
    ax.set_xticks(range(4), names)
    ax.set_ylim(-0.85, 1.0)
    ax.set_xlim(-0.6, 3.6)
    ax.set_xlabel("Terms of Equation (12.2), then their sum")
    ax.set_ylabel("Size of term (constructed units)")
    ax.set_title(f"Estimate before the search {fmt(prior, 2)}, after {fmt(successor, 2)}", fontsize=11.5)
    break_even = prior - REWARD
    if abs(delta) < 1e-12:
        verdict = "The error is exactly zero: the reward and the new estimate together match the old estimate, so nothing is repaired."
        sign = "zero"
    elif delta > 0:
        verdict = (f"Suppose the search itself was unhelpful. The error is still positive, because the estimate after it "
                   f"is higher than the estimate before it by more than the cost of {fmt(-REWARD, 2)}, so the forecast for the "
                   "earlier state is raised.")
        sign = "positive"
    else:
        if successor >= prior - 1e-12:
            cause = (f"The estimate after the search did not rise enough to cover the cost of {fmt(-REWARD, 2)}, "
                     "so the earlier state's forecast is lowered slightly.")
        else:
            cause = ("The estimate after the search is lower than the estimate before it, and the cost adds to the gap, "
                     "so the earlier state's forecast is lowered.")
        verdict = f"The error is negative. {cause} This is a repair of a prediction, not a verdict on the search."
        sign = "negative"
    metrics = {
        "TD error delta": fmt(delta, 2),
        "Sign": sign,
        "Successor estimate that gives zero": fmt(break_even, 2),
    }
    interpretation = (
        f"delta = {signed(REWARD, 2)} + {fmt(successor, 2)} - {fmt(prior, 2)} = {fmt(delta, 2)}. The error is zero at a successor "
        f"estimate of {fmt(prior, 2)} - {signed(REWARD, 2)} = {fmt(break_even, 2)}; above that it is positive, below it negative. {verdict} "
        "The sign depends on the two predictions as well as on the observed reward."
    )
    return fig, metrics, interpretation


CHAPTER = {
    "number": 12,
    "title": "Credit for Consequences",
    "subtitle": "Predictions of future return can be repaired from the final outcome or from the next prediction. Neither repair says which action caused the outcome.",
    "summary": (
        "These four demonstrations follow the chapter's progression: one short trajectory under two update rules, the "
        "eight-episode construction on which they disagree, the dial that blends them, and a tool-call example where the "
        "sign of the error depends on predictions rather than on blame. Each demonstration changes one or two declared "
        "values and shows what moves."
    ),
    "demos": [
        {
            "id": "C12-D01",
            "title": "Four steps, one reward, two update rules",
            "question": "When a run pays 1 only at its last step, which state estimates move, and by how much, under each rule?",
            "equations": [EQ_OUTCOME, EQ_DELTA, EQ_TD],
            "symbols": (
                "V-hat is the current estimate of a state's future return. Ret is the return that actually followed the state "
                "(here the final reward, with no discounting). alpha is the step size, the fraction of the gap that is kept. "
                "r is the immediate reward, gamma is the discount factor (1 here, so nothing is discounted), x_t is the state "
                "visited at step t, and delta is the one-step error: the reward plus the next state's estimate minus "
                "the state's own estimate. The end of the run has value 0."
            ),
            "prediction": "With step size 0.5 and a final reward of 1, how many of the four estimates change under the outcome rule, and how many under the one-step rule?",
            "explanation": (
                "The outcome rule waits for the end and then moves every visited estimate toward the return that followed it. "
                "The one-step rule uses the reward plus the next estimate as its target. With every estimate at 0.5 and "
                "zero reward before the last step, the first three errors are exactly zero, so only the last state moves on "
                "this run. A failed run lowers the predictions in the same pattern."
            ),
            "application": (
                "When a long run ends in success or failure, an update that touches every visited state is a statement about "
                "the returns that followed those states under the policy that was run. It is not an itemised receipt for "
                "each action, and the one-step rule's zero errors do not say the early steps were unimportant."
            ),
            "assumptions": (
                "Four states visited once each, all estimates at 0.5, no discounting, one sequential pass, and no repeated "
                "state. The first three one-step errors vanish by arithmetic because the starting estimates are all equal. "
                "Different starting estimates, discounts or replay orders change which states move."
            ),
            "check": "Set step size 0.3 to compare. With step size 0.3 and a final reward of 1, what does the outcome rule give each of the four states, and what does the one-step rule give state 4?",
            "answer": "Outcome rule: 0.5 + 0.3 x (1 - 0.5) = 0.65 for every state. One-step rule: the error at state 4 is 1 + 0 - 0.5 = 0.5, so state 4 becomes 0.5 + 0.3 x 0.5 = 0.65 and states 1 to 3 stay at 0.5.",
            "provenance": "Constructed example: the book's four-action trajectory (estimates 0.5, step size 0.1, final reward 1), computed with the laboratory's trajectory-credit function, with step size and final reward varied.",
            "source_section": "The two rules on one trajectory",
            "source_anchor": "the-two-rules-on-one-trajectory",
            "controls": [
                {"key": "alpha", "label": "Step size alpha", "values": [0.1, 0.3, 0.5], "default": 0.1},
                {"key": "final_reward", "label": "Reward paid at the last step", "values": [1, 0], "default": 1,
                 "value_labels": ["1 (the run succeeds)", "0 (the run fails)"]},
            ],
            "function": "one_trajectory_picture",
        },
        {
            "id": "C12-D02",
            "title": "Eight episodes, two answers about state A",
            "question": "Why do the two rules agree about state B but disagree about state A, which was seen only once?",
            "equations": [EQ_OUTCOME, EQ_DELTA, EQ_TD],
            "symbols": (
                "A and B are the two states. Each episode ends with a reward when it reaches the end. The outcome rule sets a "
                "state to the average return that followed its visits. The one-step rule sets a state to the reward plus the "
                "estimate of the state that followed it. No discounting (gamma is 1). x_t is the state at step t and V-hat its "
                "estimate. Values are what each rule settles on when it is run "
                "in batch form, repeatedly over the same eight episodes with a small step size."
            ),
            "prediction": "With six of the seven B-only episodes paying 1 and the A episode ending at 0, what does each rule say A is worth?",
            "explanation": (
                "B is visited eight times, so both rules average its eight returns. A is visited once, followed by B with no "
                "reward. The outcome rule copies that single return. The one-step rule says A is worth whatever B is worth, "
                "and so it borrows the evidence from the seven episodes that never contained A."
            ),
            "application": (
                "When a state is rare but its successor is common, ask whether the stated process really sends the rare state "
                "to that successor. If so, the successor-based answer pools more evidence; if not, it imports a mistake."
            ),
            "assumptions": (
                "The process is stipulated: A always goes to B with no reward, and B pays at random. Eight observations do not "
                "prove that. The one-step answer is better only if that process is real and the successor's value is "
                "reliable. The outcome rule is not wrong about the data; it fits them exactly."
            ),
            "check": "Set 3 episodes to compare. Suppose three of the seven B-only episodes pay 1 and the A episode ends at 0. What is B, and how far is the outcome rule's value for A from the one-step rule's?",
            "answer": "B = (3 + 0) / 8 = 0.375. The outcome rule gives A = 0, the one-step rule gives A = 0.375, so they differ by 0.375.",
            "provenance": "Constructed example: the book's eight-episode construction (six ones among the seven B-only episodes, the A episode ending at 0), with those counts varied.",
            "source_section": "Eight episodes, two answers",
            "source_anchor": "eight-episodes-two-answers",
            "controls": [
                {"key": "ones_in_b_only", "label": "B-only episodes that pay 1 (out of 7)", "values": [3, 6, 7], "default": 6},
                {"key": "a_final", "label": "Reward at the end of the one A episode", "values": [0, 1], "default": 0},
            ],
            "function": "eight_episodes_picture",
        },
        {
            "id": "C12-D03",
            "title": "One dial between the two rules",
            "question": "How does the blending parameter lambda divide weight between short lookahead targets and the complete return?",
            "equations": [EQ_LAMBDA],
            "symbols": (
                "lambda is the blending parameter between 0 and 1. A k-step target adds the next k rewards to the estimate k "
                "steps ahead. N is the number of transitions in the whole episode and t the current step, so n = N - t "
                "is the number of transitions left; j counts the rewards inside a target, and gamma is the discount "
                "factor (the weights do not depend on it). With n transitions left, the first n - 1 targets get weight (1 - lambda) x lambda^(k-1) and "
                "the complete return gets the remaining weight, lambda^(n-1). The weights always add to 1. It is not the "
                "step size and not the discount factor."
            ),
            "prediction": "With 8 transitions remaining and lambda = 0.9, does the complete return or the one-step target get more weight?",
            "explanation": (
                "Each extra step of lookahead is weighted lambda times the one before it, so small lambda piles weight on the "
                "one-step target and large lambda spreads it out. Whatever weight the lookahead targets leave over goes to the "
                "complete return, so the two opening rules are the two ends of the dial."
            ),
            "application": (
                "When a method is described as temporal-difference (TD) learning with a lambda setting, read it as a choice of target mixture: how much to "
                "trust the agent's own estimates relative to what actually happened. For a fixed policy and a prediction target, it "
                "changes the estimator, not the objective."
            ),
            "assumptions": (
                "A single episode that terminates after n transitions, with terminal value zero. The figure shows target weights "
                "only; it says nothing about which lambda gives the best predictions, which depends on the problem and on how "
                "the training data are presented."
            ),
            "check": "Set lambda 0.3 and 4 transitions to compare. With 4 transitions remaining and lambda = 0.3, what weight does the complete return get, and what does the first target get?",
            "answer": "Complete return: 0.3^3 = 0.027. First target: 1 - 0.3 = 0.7. The other two weights are 0.21 and 0.063, and 0.7 + 0.21 + 0.063 + 0.027 = 1.",
            "provenance": "Constructed example: the weights of Equation (12.4) for the book's eight-transition case (Figure 12.4) and a four-transition case, at lambda values defined for this reader.",
            "source_section": "The family between the two rules",
            "source_anchor": "the-family-between-the-two-rules",
            "controls": [
                {"key": "lam", "label": "Blending parameter lambda", "values": [0, 0.3, 0.9, 1], "default": 0.9},
                {"key": "remaining", "label": "Transitions remaining", "values": [4, 8], "default": 8},
            ],
            "function": "lambda_picture",
        },
        {
            "id": "C12-D04",
            "title": "A positive error for a useless search",
            "question": "Can the one-step error be positive after a search that cost something and returned nothing useful?",
            "equations": [EQ_DELTA],
            "symbols": (
                "r is the reward for the call, here a cost of 0.02 (reward -0.02). The discount factor gamma is 1. The prior estimate is the "
                "agent's forecast of future return before the search; the successor estimate is its forecast after the "
                "search. delta is the reward plus the successor estimate minus the prior estimate; it is the "
                "temporal-difference (TD) error."
            ),
            "prediction": "With the prior estimate at 0.20, which of these successor estimates give a positive error: 0.10, 0.20, 0.50 or 0.80?",
            "explanation": (
                "The error compares the old forecast with the observed reward plus the new forecast. A cost of 0.02 makes the "
                "reward slightly negative, but the sign is set by the two estimates. The error is positive "
                "whenever the new estimate exceeds the old one by more than the cost."
            ),
            "application": (
                "When reading a log of TD errors from an agent, do not treat a positive error as praise for the call just made, "
                "or a negative one as blame. Credit for a particular call needs a comparison with what would have happened "
                "without it, which these updates do not provide."
            ),
            "assumptions": (
                "One transition with the reward and estimates set by hand, as in the chapter's example. Estimates here are "
                "declared numbers, not fitted values, and the example does not show that the first search was useless in fact."
            ),
            "check": "With a prior estimate of 0.60 and a successor estimate of 0.50, what is the error for a reward of -0.02, and which direction does the earlier estimate move?",
            "answer": "delta = -0.02 + 0.50 - 0.60 = -0.12, which is negative, so the earlier estimate is lowered.",
            "provenance": "Constructed example: the book's first search (reward -0.02, estimates 0.20 before and 0.50 or 0.10 after), with the prior estimate and the successor estimate varied; the error is checked against the laboratory's trajectory-credit function.",
            "source_section": "Credit across a tool trajectory",
            "source_anchor": "credit-across-a-tool-trajectory",
            "controls": [
                {"key": "prior", "label": "Estimate before the search", "values": [0.2, 0.6], "default": 0.2},
                {"key": "successor", "label": "Estimate after the search", "values": [0.1, 0.2, 0.5, 0.8], "default": 0.5},
            ],
            "function": "td_error_picture",
        },
    ],
}

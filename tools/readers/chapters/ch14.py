"""Chapter 14 reader: Building a World Inside.

Four demonstrations built on Equations (14.1) to (14.4). Demonstrations 1, 2
and 4 call the laboratory's own transition-model function
(math_ai_agents.chapters.ch14.evaluate), so the reader, the notebook and the
chapter skill agree. Every number is a constructed teaching value; the
worked numbers in Demonstration 4 are the chapter's own (Figure 14.2 and the
priced twenty-step plan).
"""
from fractions import Fraction
import math

import numpy as np

from math_ai_agents.chapters.ch14 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

# Equations copied from the chapter with the tag dropped.
EQ_EPS = r"\epsilon \;=\; \max_{x,a}\; \tfrac{1}{2}\sum_{x'}\big|\hat P(x'\mid x,a) - P(x'\mid x,a)\big|."
EQ_BOUND = r"\big|\hat V^{\pi}(x) - V^{\pi}(x)\big| \;\le\; \frac{\gamma\,\epsilon\,R}{(1-\gamma)^2}."
EQ_GAP = r"\Delta(x) \;=\; \max_{a}Q^{\pi}(x,a) \;-\; \max_{a \neq a^{*}}Q^{\pi}(x,a)."
EQ_HSTAR = (r"H^{*} \;=\; \max\Big\{ H \in \mathbb{Z}_{>0} \;:\; H \leq H_{\max},\;"
            r"R\,\epsilon\,H(H-1) \;<\; \Delta \Big\}.")

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}

# The laboratory's default pair of kernels (content/ch14.json): two states, one fixed policy.
TRUE_KERNEL = [[0.9, 0.1], [0.2, 0.8]]


def lab_run(shift0, shift1, rewards=(0.0, 1.0), discount=0.9, horizon=1):
    """The laboratory's evaluate() on the default true kernel and a model kernel that moves
    shift0 of probability in state 1's row and shift1 in state 2's row."""
    model = [[0.9 - shift0, 0.1 + shift0], [0.2 + shift1, 0.8 - shift1]]
    return evaluate({"true_transition": TRUE_KERNEL, "model_transition": model, "rewards": list(rewards),
                     "discount": discount, "horizon": horizon})


def uniform_error(eps):
    """Laboratory epsilon for a model whose worst row is off by eps."""
    return lab_run(eps, eps)["metrics"]["uniform_tv_error"]


# Demonstration 1

def worst_row_picture(error_state_1=0.02, error_state_2=0.02):
    out = lab_run(error_state_1, error_state_2)
    eps = out["metrics"]["uniform_tv_error"]
    rows = [error_state_1, error_state_2]
    mean = sum(rows) / 2
    fig, ax = new_figure(height=4.1)
    names = ["State 1", "State 2"]
    colors = [PALETTE["navy"], PALETTE["teal"]]
    hatches = ["", "//"]
    for i, v in enumerate(rows):
        ax.bar(i, v, width=0.5, color=colors[i], hatch=hatches[i], edgecolor="white")
        ax.text(i, v + 0.008, fmt(v, 2), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    ax.hlines(eps, -0.6, 1.4, color=PALETTE["terracotta"], linewidth=2)
    equal = math.isclose(eps, mean, abs_tol=1e-12)
    if equal:
        label_point(ax, 1.4, eps, f"max = mean = {fmt(eps, 2)}", color=PALETTE["terracotta"], dx=5, dy=0, va="center")
    else:
        ax.hlines(mean, -0.6, 1.4, color=PALETTE["grey"], linewidth=1.6, linestyle="dashed")
        label_point(ax, 1.4, eps, f"max = {fmt(eps, 2)}  (epsilon)", color=PALETTE["terracotta"], dx=5, dy=0, va="center")
        label_point(ax, 1.4, mean, f"mean = {fmt(mean, 2)}", color=PALETTE["grey"], dx=5, dy=0, va="center")
    ax.set_xticks([0, 1], names)
    ax.set_xlim(-0.6, 2.8)
    ax.set_ylim(0, 0.36)
    ax.set_xlabel("State of the constructed two-state world")
    ax.set_ylabel("One-step error of the model's next-state row")
    ax.set_title(f"Row errors {fmt(error_state_1, 2)} and {fmt(error_state_2, 2)}", fontsize=11.5)
    ax.grid(axis="x", alpha=0)
    # Hand calculation: state 2's row, true (0.2, 0.8), model (0.2 + d, 0.8 - d).
    d = error_state_2
    row_calc = (f"State 2: 1/2 x (|{fmt(0.2 + d, 2)} - 0.20| + |{fmt(0.8 - d, 2)} - 0.80|) = "
                f"1/2 x ({fmt(d, 2)} + {fmt(d, 2)}) = {fmt(d, 2)}.")
    if equal:
        verdict = ("Both rows are off by the same amount, so the largest error and the average error coincide. "
                   "Make one state much worse and they separate.")
    else:
        verdict = (f"Equation (14.1) reports the largest row error, {fmt(eps, 2)}, not the average {fmt(mean, 2)}. "
                   f"An average of ({fmt(error_state_1, 2)} + {fmt(error_state_2, 2)}) / 2 = {fmt(mean, 2)} would "
                   f"understate the damage at the worst state by {fmt(eps - mean, 2)}, and an optimizer will go to that state.")
    metrics = {
        "Error in state 1": fmt(error_state_1, 2),
        "Error in state 2": fmt(error_state_2, 2),
        "Epsilon (largest row error)": fmt(eps, 2),
        "Average row error": fmt(mean, 2),
    }
    interpretation = (f"State 1: 1/2 x (|{fmt(0.9 - error_state_1, 2)} - 0.90| + |{fmt(0.1 + error_state_1, 2)} - 0.10|) = "
                      f"1/2 x ({fmt(error_state_1, 2)} + {fmt(error_state_1, 2)}) = {fmt(error_state_1, 2)}. {row_calc} "
                      f"Epsilon = max({fmt(error_state_1, 2)}, {fmt(error_state_2, 2)}) = {fmt(eps, 2)}. {verdict}")
    return fig, metrics, interpretation


# Demonstration 2

GAMMA_GRID = np.linspace(0.5, 0.995, 120)


def compounding_picture(discount=0.9, error=0.01):
    gamma, eps, reward = float(discount), float(error), 1.0
    # The laboratory computes the discounted bound from its own kernels (TV = eps, R = 1).
    lab_bound = lab_run(eps, eps, discount=gamma)["metrics"]["discounted_infinite_bound"]
    bound = gamma * eps * reward / (1 - gamma) ** 2
    if not math.isclose(bound, lab_bound, rel_tol=1e-9):
        raise AssertionError("laboratory bound disagrees with Equation (14.2)")
    scale = reward / (1 - gamma)
    horizon = 1 / (1 - gamma)
    curve = GAMMA_GRID * eps * reward / (1 - GAMMA_GRID) ** 2
    value_scale = reward / (1 - GAMMA_GRID)
    fig, ax = new_figure(height=4.3)
    ax.plot(GAMMA_GRID, value_scale, color=PALETTE["grey"], linestyle="dashed", linewidth=1.8)
    ax.plot(GAMMA_GRID, curve, color=PALETTE["terracotta"], linewidth=2.2)
    ax.axvline(gamma, color=PALETTE["light"], linewidth=1.2)
    ax.plot([gamma], [bound], "o", color=PALETTE["terracotta"], markersize=9)
    ax.plot([gamma], [scale], "s", color=PALETTE["grey"], markersize=8)
    ax.set_yscale("log")
    ax.set_xlim(0.47, 1.0)
    ax.set_ylim(0.01, 3000)
    label_point(ax, 0.52, curve[2], f"value-error bound (error {fmt(eps, 2)})", color=PALETTE["terracotta"], dx=0, dy=8, ha="left").set_bbox(BOX)
    label_point(ax, 0.52, value_scale[2], "largest possible value, R/(1-gamma)", color=PALETTE["grey"], dx=0, dy=7, ha="left").set_bbox(BOX)
    ax.set_xlabel("Discount factor gamma (constructed values)")
    ax.set_ylabel("Reward units (R = 1), log scale")
    ax.set_title(f"gamma = {fmt(gamma, 2)}: bound {fmt(bound, 2)} against value scale {fmt(scale, 1)}", fontsize=11.5)
    ratio = bound / scale
    if bound >= scale:
        verdict = (f"The bound ({fmt(bound, 2)}) is at least as large as the largest value the agent could ever collect "
                   f"({fmt(scale, 1)}), so it says nothing about this model.")
    elif ratio > 0.5:
        verdict = (f"The bound is {fmt(ratio * 100, 0)} percent of the largest possible value ({fmt(scale, 1)}), "
                   "so it allows an error that is almost the whole range: close to useless.")
    else:
        verdict = (f"The bound is {fmt(ratio * 100, 0)} percent of the largest possible value ({fmt(scale, 1)}), "
                   "so it still carries information at this horizon.")
    metrics = {
        "Effective horizon 1/(1-gamma)": fmt(horizon, 1),
        "Bound gamma x error x R / (1-gamma)^2": fmt(bound, 2),
        "Largest possible value R/(1-gamma)": fmt(scale, 1),
        "Bound as a share of that value": fmt(ratio, 3),
    }
    interpretation = (
        f"Bound = {fmt(gamma, 2)} x {fmt(eps, 2)} x 1 / (1 - {fmt(gamma, 2)})^2 = {fmt(gamma * eps, 4)} / "
        f"{fmt((1 - gamma) ** 2, 4)} = {fmt(bound, 2)}. The largest possible value is 1 / (1 - {fmt(gamma, 2)}) = {fmt(scale, 1)}. "
        f"{verdict} The factor 1/(1-gamma) appears twice in the bound: once as the number of steps that matter, "
        "once as the value those steps can displace."
    )
    return fig, metrics, interpretation


# Demonstration 3

TRUE_Q = {"Plan A": 0.9, "Plan B": 0.6, "Plan C": 0.2}  # constructed action values; gap = 0.9 - 0.6


def ranking_picture(error=0.05, pattern="shared"):
    delta = float(error)
    names = list(TRUE_Q)
    true = np.array([TRUE_Q[n] for n in names])
    if pattern == "shared":
        model = true + delta
        pattern_text = "the same offset added to every action value"
    else:
        model = true.copy()
        model[0] -= delta
        model[1] += delta
        pattern_text = "the best action is marked down and the runner-up marked up by the error"
    gap = float(true[0] - true[1])
    model_gap = float(model[0] - model[1])
    twice = 2 * delta
    certified = Fraction(str(delta)) * 2 < Fraction(str(round(gap, 12)))
    top = float(model.max())
    winners = [n for n, v in zip(names, model) if math.isclose(v, top, abs_tol=1e-9)]
    if len(winners) > 1:
        choice = " and ".join(winners) + " (tie)"
    else:
        choice = winners[0]
    fig, ax = new_figure(height=4.3)
    x = np.arange(len(names))
    w = 0.36
    ax.bar(x - w / 2, true, width=w, color=PALETTE["navy"], edgecolor="white")
    ax.bar(x + w / 2, model, width=w, color="white", edgecolor=PALETTE["terracotta"], hatch="///", linewidth=1.4)
    for xi, t, m in zip(x, true, model):
        ax.text(xi - w / 2, t + 0.02, f"true\n{fmt(t, 2)}", ha="center", va="bottom", fontsize=10.5, color=PALETTE["navy"])
        ax.text(xi + w / 2, m + 0.02, f"model\n{fmt(m, 2)}", ha="center", va="bottom", fontsize=10.5, color=PALETTE["terracotta"])
    ax.set_xticks(x, names)
    ax.set_ylim(0, 1.5)
    ax.set_xlim(-0.6, 2.6)
    ax.set_xlabel("Action at one state (constructed)")
    ax.set_ylabel("Action value Q (constructed units)")
    ax.set_title(f"Error {fmt(delta, 2)}; true gap {fmt(gap, 2)}; model picks {choice}", fontsize=11.5)
    ax.grid(axis="x", alpha=0)
    if len(winners) > 1:
        verdict = (f"The model scores Plan A and Plan B equally at {fmt(top, 2)}. The model's own gap is 0 (a tie), so the ranking is not "
                   "preserved: 2 x error equals the gap exactly, and the strict test 2 x error < gap fails at equality.")
    elif winners[0] == "Plan A":
        if certified:
            verdict = (f"The model still picks Plan A. The guarantee holds: 2 x {fmt(delta, 2)} = {fmt(twice, 2)} is below the gap {fmt(gap, 2)}.")
        else:
            verdict = (f"The model still picks Plan A, but the guarantee does not cover this case: 2 x {fmt(delta, 2)} = {fmt(twice, 2)} is not "
                       f"below the gap {fmt(gap, 2)}. A shared offset moves every value together, so no ordering changes.")
    else:
        verdict = (f"The model now picks {winners[0]} over Plan A. The error is {fmt(delta, 2)} per action and 2 x {fmt(delta, 2)} = {fmt(twice, 2)} "
                   f"exceeds the gap {fmt(gap, 2)}, so the certificate cannot hold and here the ranking really reversed.")
    metrics = {
        "True gap (Equation 14.3)": fmt(gap, 2),
        "Action-value error": fmt(delta, 2),
        "Twice the error": fmt(twice, 2),
        "Guarantee 2 x error < gap holds": "yes" if certified else "no",
        "Model's choice": choice,
        "Model's own gap": fmt(model_gap, 2),
    }
    interpretation = (
        f"Gap = 0.90 - 0.60 = {fmt(gap, 2)}. Twice the error = 2 x {fmt(delta, 2)} = {fmt(twice, 2)}. "
        f"Error pattern: {pattern_text}. Model values: Plan A {fmt(model[0], 2)}, Plan B {fmt(model[1], 2)}, Plan C {fmt(model[2], 2)}, "
        f"so the model's own gap is {fmt(model[0], 2)} - {fmt(model[1], 2)} = {fmt(model_gap, 2)}. {verdict}"
    )
    return fig, metrics, interpretation


# Demonstration 4

H_MAX = 9  # declared planning cap for this reader


def lhs(reward, eps, h):
    """R x eps x H x (H - 1), exactly."""
    return Fraction(str(reward)) * Fraction(str(eps)) * h * (h - 1)


def certified_horizon(reward, eps, gap, h_max=H_MAX):
    best = None
    for h in range(1, h_max + 1):
        if lhs(reward, eps, h) < Fraction(str(gap)):
            best = h
    return best


SCENARIOS = {
    "r1": (1.0, 0.5),    # R = 1 with the action gap 0.5 of Figure 14.2
    "r10": (10.0, 2.0),  # the chapter's priced twenty-step plan: R = 10, gap about 2
}


def horizon_picture(scenario="r1", error=0.02):
    reward, gap = SCENARIOS[scenario]
    eps = float(error)
    h_star = certified_horizon(reward, eps, gap)
    # The laboratory's finite-horizon bound R x eps x H(H-1)/2, doubled, is the left side of Equation (14.4).
    series = lab_run(eps, eps, rewards=(0.0, reward), discount=0.9, horizon=H_MAX)["series"][1]["y"]
    hs = np.arange(1, H_MAX + 1)
    values = np.array([2 * b for b in series])
    exact = np.array([float(lhs(reward, eps, int(h))) for h in hs])
    if not np.allclose(values, exact, rtol=1e-9, atol=1e-12):
        raise AssertionError("laboratory bound disagrees with R x eps x H(H-1)")
    passed = np.array([lhs(reward, eps, int(h)) < Fraction(str(gap)) for h in hs])
    fig, ax = new_figure(height=4.3)
    first_fail_value = float(lhs(reward, eps, h_star + 1)) if h_star < H_MAX else 0.0
    top = max(3.2 * gap, 1.5 * first_fail_value)  # the first failing horizon is always drawn
    ax.axhline(gap, color=PALETTE["gold"], linewidth=2)
    shown = exact <= 0.70 * top  # keep markers clear of the top edge and the note
    ax.plot(hs[passed & shown], exact[passed & shown], "o", color=PALETTE["teal"], markersize=9)
    ax.plot(hs[~passed & shown], exact[~passed & shown], "X", color=PALETTE["terracotta"], markersize=9)
    ax.plot(hs[shown], exact[shown], color=PALETTE["light"], linewidth=1.2, zorder=0)
    if h_star < H_MAX:
        ax.vlines(h_star + 0.5, 0, 0.70 * top, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    label_point(ax, 0.6, gap, f"action gap {fmt(gap, 1)}", color=PALETTE["gold"], dx=0, dy=6, ha="left").set_bbox(BOX)
    hidden = [int(h) for h in hs[~shown]]
    note = "circle: certified; cross: not certified"
    if h_star < H_MAX:
        note += "\ndashed line: after the last certified horizon"
    if hidden:
        span = f"H = {hidden[0]}" if len(hidden) == 1 else f"H = {hidden[0]} to {hidden[-1]}"
        note += f"\nnot drawn, above the plot: {span}"
    label_point(ax, 0.6, 0.99 * top, note, color=PALETTE["ink"], dx=0, dy=0, ha="left", va="top")
    label_point(ax, h_star, exact[h_star - 1], f"H* = {h_star}", color=PALETTE["teal"], dx=0, dy=-12, ha="center", va="top").set_bbox(BOX)
    ax.set_xlim(0.5, H_MAX + 0.5)
    ax.set_ylim(0, top)
    ax.set_xticks(hs)
    ax.set_xlabel(f"Horizon H, in rewards (planning cap {H_MAX})")
    ax.set_ylabel("R x epsilon x H(H-1), twice the error bound")
    ax.set_title(f"R = {fmt(reward, 0)}, epsilon = {fmt(eps, 2)}, gap = {fmt(gap, 1)}", fontsize=11.5)
    at_star = lhs(reward, eps, h_star)
    calc = (f"At H = {h_star}: {fmt(reward, 0)} x {fmt(eps, 2)} x {h_star} x {h_star - 1} = {fmt(float(at_star), 2)}, below the gap {fmt(gap, 1)}.")
    if h_star < H_MAX:
        nxt = lhs(reward, eps, h_star + 1)
        equal = nxt == Fraction(str(gap))
        calc += (f" At H = {h_star + 1}: {fmt(reward, 0)} x {fmt(eps, 2)} x {h_star + 1} x {h_star} = {fmt(float(nxt), 2)}, ")
        calc += ("equal to the gap, and the test is strict, so it fails by equality." if equal else f"not below the gap {fmt(gap, 1)}.")
        tail = (f" The certificate covers {h_star} rewards. Its failure at {h_star + 1} is inconclusive: it does not "
                "show that the ranking reverses, only that this guarantee stops.")
        first_fail = str(h_star + 1)
    else:
        tail = f" No horizon up to the declared cap of {H_MAX} fails, so the cap, not the certificate, ends the search."
        first_fail = "none up to the cap"
    metrics = {
        "Certified horizon H*": str(h_star),
        "First horizon that fails": first_fail,
        f"R x epsilon x H(H-1) at H* = {h_star}": fmt(float(at_star), 2),
        "Action gap": fmt(gap, 1),
    }
    return fig, metrics, calc + tail


CHAPTER = {
    "number": 14,
    "title": "Building a World Inside",
    "subtitle": "An agent that plans inside a learned model scores well only as far as the model's error stays smaller than what the decision can tolerate.",
    "summary": (
        "These four demonstrations follow the chapter's finite certificate for a learned transition model. First one number "
        "for how wrong the model is, then how that error compounds over a horizon, then why the gap between the best and "
        "second-best action decides whether a ranking survives, and finally the number of imagined steps those pieces certify. "
        "All worlds, errors and gaps are constructed teaching values."
    ),
    "demos": [
        {
            "id": "C14-D01",
            "title": "One number for how wrong a model is",
            "question": "A model is wrong by different amounts in different states. Which single number does the chapter use, and why not the average?",
            "equations": [EQ_EPS],
            "symbols": (
                "P(x' | x, a) is the true probability of moving to state x' from state x after action a; the hat marks the model's "
                "estimate. The sum adds up how much the two distributions disagree over all next states, the one half turns that "
                "into the largest probability the model has put in the wrong place, and the max takes the worst state and action. "
                "Epsilon is that worst case. The constructed world has two states and one fixed behaviour, so each state has one row."
            ),
            "prediction": "Set state 1's error to 0.02 and state 2's to 0.30. Is epsilon the average of the two, or something else?",
            "explanation": (
                "For each row, the disagreement is half the sum of the absolute probability differences. When the model moves "
                "probability d from one next state to the other, that is half of d plus d, which is d. Equation (14.1) then takes the "
                "largest row. The reason is that an agent optimizing against the model will steer toward the worst row, so the average "
                "describes a model sampled at random, not a model searched."
            ),
            "application": (
                "When someone reports that a model is accurate on average, ask for its worst state and action. A model that is "
                "excellent on most of the space and badly wrong in one place has a large epsilon, and that place is where a planner goes."
            ),
            "assumptions": (
                "Two states, a single fixed behaviour, and exact knowledge of both the true and the model probabilities, which a real "
                "deployment rarely has. The kernels are the laboratory's constructed defaults with the model rows shifted by the chosen "
                "error. The chapter also notes that logged prediction error is only a labelled proxy for epsilon, never epsilon itself."
            ),
            "check": "True row (0.5, 0.3, 0.2), model row (0.4, 0.4, 0.2). What is that row's error, and what is epsilon if every other row is exact?",
            "answer": "1/2 x (|0.4 - 0.5| + |0.4 - 0.3| + |0.2 - 0.2|) = 1/2 x (0.1 + 0.1 + 0) = 0.10. With every other row exact, epsilon is the maximum, 0.10.",
            "provenance": "Constructed example: the laboratory's default two-state kernels (rows 0.90, 0.10 and 0.20, 0.80) with model rows shifted by the chosen error, computed with the laboratory's transition-model function.",
            "source_section": "The object being learned",
            "source_anchor": "the-object-being-learned",
            "controls": [
                {"key": "error_state_1", "label": "Model error in state 1's row", "values": [0.02, 0.1], "default": 0.02},
                {"key": "error_state_2", "label": "Model error in state 2's row", "values": [0.02, 0.1, 0.3], "default": 0.02},
            ],
            "function": "worst_row_picture",
        },
        {
            "id": "C14-D02",
            "title": "One step of error, compounded",
            "question": "How large can the value error become when a small one-step error is compounded over a long effective horizon?",
            "equations": [EQ_BOUND],
            "symbols": (
                "V(x) is the true value of state x under a fixed behaviour, and V-hat(x) the value the model computes. Gamma is the "
                "discount factor between 0 and 1, epsilon the one-step error from Equation (14.1), and R the largest immediate reward "
                "(set to 1 here). The value scale R/(1-gamma) is the most any run could collect. 1/(1-gamma) is the effective number of "
                "steps the agent cares about."
            ),
            "prediction": "Keep the error at 0.01 and raise gamma from 0.9 to 0.99. Does the bound grow by about 10 times, or by about 100?",
            "explanation": (
                "The bound multiplies gamma, epsilon and R, then divides by (1 - gamma) squared. One factor of 1/(1-gamma) counts the steps that "
                "matter, and the second counts that a mistake at each step displaces everything after it. Raising gamma from 0.9 to 0.99 "
                "makes the denominator 100 times smaller, so the bound grows about 110 times (0.9 to 99 at an error of 0.01) while the value scale grows by only 10."
            ),
            "application": (
                "Before trusting a long imagined rollout, divide the bound by the largest possible value. If the share is near or above 1, "
                "the guarantee has nothing to say, and the remedy is to look at the world sooner rather than to polish the model."
            ),
            "assumptions": (
                "The bound needs a fixed behaviour, the same expected immediate reward in model and world, rewards in [0, R], and error at most "
                "epsilon for every state and action that behaviour reaches. It is a worst case: it is tight for adversarial models, which is what an optimizer produces, but "
                "the chapter also notes that it is often loose, so a model can do far better than the bound permits. A single number "
                "can also hide where the model is bad."
            ),
            "check": "With gamma = 0.8, epsilon = 0.05 and R = 1, what is the bound, and what is the largest possible value?",
            "answer": "Bound = 0.8 x 0.05 / (1 - 0.8)^2 = 0.04 / 0.04 = 1.0. The largest possible value is 1 / 0.2 = 5, so the bound is a fifth of the range.",
            "provenance": "Constructed example: the chapter's discounted bound with R = 1; the 0.99 and 0.01 pair is the chapter's own worked illustration, the other values are defined for this reader, and each bound is checked against the laboratory's transition-model function.",
            "source_section": "What one step of error becomes",
            "source_anchor": "what-one-step-of-error-becomes",
            "controls": [
                {"key": "discount", "label": "Discount factor gamma", "values": [0.5, 0.9, 0.95, 0.99], "default": 0.9},
                {"key": "error", "label": "One-step error epsilon", "values": [0.01, 0.02], "default": 0.01},
            ],
            "function": "compounding_picture",
        },
        {
            "id": "C14-D03",
            "title": "The action gap decides whether a ranking survives",
            "question": "A model can be wrong about every action value and still choose correctly, or be nearly right and choose wrongly. What decides which?",
            "equations": [EQ_GAP],
            "symbols": (
                "Q(x, a) is the true value of taking action a at state x and then following the fixed behaviour. Delta is the gap between the "
                "best action's value and the runner-up's (a* is a best action; if several actions tie for the maximum, the gap is defined as zero). "
                "The model's value of each action is allowed to be off by at most the chosen error, which is the chapter's delta. "
                "The model keeps the true ranking whenever twice that error is smaller than the gap: 2 delta < Delta."
            ),
            "prediction": "With a shared offset of 0.25 added to every value, does the model still pick Plan A? Then switch to the adversarial pattern at 0.25.",
            "explanation": (
                "A shared offset moves every value together, so the ordering is untouched however large the offset is. An adversarial error "
                "marks the best action down and the runner-up up, each by the error, so the two meet when twice the error equals the gap. "
                "At exactly that point the model sees a tie, and the strict test cannot certify the ranking."
            ),
            "application": (
                "Judge a planning model against the decision it serves, not against a single accuracy figure. Ask how large the gap is "
                "between the best option and the next one, then compare twice the value error to it, in the same units."
            ),
            "assumptions": (
                "One state, three actions, and a uniform bound on the action-value error. The chapter adds that this bound is an extra "
                "assumption: Equation (14.2) bounds state values and does not supply it. The values here are constructed. The test 2 x error < gap "
                "is sufficient, not necessary, so a failed test leaves the ranking undecided rather than wrong, as the shared-offset states show."
            ),
            "check": "True values 0.9 and 0.6, adversarial error 0.12. Which action does the model pick, and does the certificate hold?",
            "answer": "Model values: 0.9 - 0.12 = 0.78 and 0.6 + 0.12 = 0.72, so the model still picks Plan A. Twice the error is 0.24, below the gap 0.30, so the certificate holds.",
            "provenance": "Constructed example: three action values (0.9, 0.6, 0.2) defined for this reader, with error patterns that illustrate the chapter's ranking argument; the chapter's cost-by-1.3 example is the same idea with a shared error.",
            "source_section": "The number that actually matters",
            "source_anchor": "the-number-that-actually-matters",
            "controls": [
                {"key": "error", "label": "Action-value error", "values": [0.05, 0.15, 0.25], "default": 0.05},
                {"key": "pattern", "label": "Error pattern", "values": ["shared", "adversarial"], "default": "shared",
                 "value_labels": ["Shared offset on every action", "Adversarial: best down, runner-up up"]},
            ],
            "function": "ranking_picture",
        },
        {
            "id": "C14-D04",
            "title": "How many imagined steps are certified",
            "question": "Given the model error, the reward range and the action gap, how many steps ahead can the certificate vouch for?",
            "equations": [EQ_HSTAR],
            "symbols": (
                "H is the number of rewards the agent plans over, H-max the declared planning cap (9 here), and H-star the largest H that passes. "
                "R is the largest immediate reward, epsilon the uniform one-step error from Equation (14.1), and Delta the lower bound on the action "
                "gap from Equation (14.3). The left side R x epsilon x H(H-1) is twice the finite-horizon action-value error bound R x epsilon x H(H-1)/2."
            ),
            "prediction": "With R = 10 and a gap of 2, cut the error by 8 times, from 0.08 to 0.01. Does the certified horizon grow by 8 times, or by far less?",
            "explanation": (
                "Twice the error bound grows with H times H-1, so each extra step costs more than the last. The certificate keeps the largest H "
                "for which that quantity is still strictly below the gap. Because H(H-1) grows like H squared, the horizon scales roughly with "
                "the square root of gap over R x epsilon: for long horizons, cutting the error by 8 times raises it by about 2.8 times, not 8. Here the whole numbers are small, so 0.08 to 0.01 moves H-star from 2 to 4."
            ),
            "application": (
                "Use the certified horizon to set how many steps an agent commits to before it observes the world again. Plan that many, "
                "execute a few, look, and replan, rather than emitting a long plan against an error nobody measured."
            ),
            "assumptions": (
                "A finite covered domain, equal expected immediate rewards in model and world, the same initial state and fixed behaviour, "
                "uniform error epsilon, zero terminal continuation and a declared gap. The R = 10 case uses the chapter's priced plan, where "
                "a logged prediction miss rate is declared a conservative proxy for epsilon, which is not the same thing. A failed test is "
                "inconclusive, not proof of a wrong decision, and the inputs are usually not measured."
            ),
            "check": "With R = 1, epsilon = 0.04 and a gap of 0.5, what is the certified horizon?",
            "answer": "R x epsilon x H(H-1) = 0.04 x H(H-1). At H = 4 it is 0.04 x 12 = 0.48, below 0.5. At H = 5 it is 0.04 x 20 = 0.80, which is not. H-star = 4.",
            "provenance": "Constructed example: the chapter's Figure 14.2 case (R = 1, gap 0.5, epsilon 0.02) and its priced twenty-step plan (R = 10, gap 2, epsilon 0.08 and 0.01); the 0.02 case with R = 10 and the 0.01 case with R = 1 are defined for this reader, and each curve is checked against the laboratory's finite-horizon bound.",
            "source_section": "How many steps a model is good for",
            "source_anchor": "how-many-steps-a-model-is-good-for",
            "controls": [
                {"key": "scenario", "label": "Reward range and action gap", "values": ["r1", "r10"], "default": "r1",
                 "value_labels": ["R = 1, gap 0.5 (Figure 14.2)", "R = 10, gap 2 (priced plan)"]},
                {"key": "error", "label": "One-step error epsilon", "values": [0.01, 0.02, 0.08], "default": 0.02},
            ],
            "function": "horizon_picture",
        },
    ],
}

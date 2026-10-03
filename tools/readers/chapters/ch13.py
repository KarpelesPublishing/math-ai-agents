"""Chapter 13 reader: Learning to Choose.

Four demonstrations built on Equations (13.1) to (13.4) and the chapter's
retrieve-or-answer construction.

D01  Eq 13.1: return-to-go and the action mask (the chapter's -0.4 unit test).
D02  Eq 13.2: the gradient of one choice, with an exact baseline-variance
     comparison (Figure 13.2) computed by enumerating the four outcomes.
D03  Training on a verifier: the laboratory's own training function
     (math_ai_agents.chapters.ch13.evaluate) runs the notebook's default,
     changed and transfer cases and the chapter's noisy-verifier story with
     the shortcut tool, so the reader, the notebook and the chapter skill agree.
D04  Eqs 13.3 and 13.4: what shaping cancels and what a terminal potential keeps.

Every number is a constructed teaching value; the book's own values (0.55,
0.80, 0.05, 0.4, 0.9, 0.3, 0.95, -0.4, -1.2) and the laboratory's case values
are named in each provenance.
"""
import math

import numpy as np

from math_ai_agents.chapters.ch13 import evaluate
from readerkit import PALETTE, fmt, is_tie, label_point, new_figure

EQ_TRAJECTORY = (
    r"\tau=(o_0,a_0,r_0,o_1,a_1,r_1,\ldots,o_T),"
    r"\qquad G_t=\sum_{k=t}^{T-1}\gamma^{k-t}r_k."
)
EQ_MASK = r"-[(1)(-0.4)+(0)(-1.2)]=0.4"
EQ_GRADIENT = (
    r"\nabla_\phi J(\phi)=\operatorname E_{\tau\sim\pi_\phi}\!\left["
    r"\sum_{t=0}^{T-1}\gamma^t\nabla_\phi\log \pi_\phi(a_t\mid o_t)\,G_t"
    r"\right]."
)
EQ_ZERO = r"\sum_a\pi_\phi(a\mid o)\nabla_\phi\log \pi_\phi(a\mid o)=0"
EQ_SHAPED = r"r'_t=r_t+\gamma\operatorname{Pot}(x_{t+1})-\operatorname{Pot}(x_t)."
EQ_TELESCOPE = r"G'_0=G_0-\operatorname{Pot}(x_0)+\gamma^T\operatorname{Pot}(x_T)."

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}

DIRECT_SUCCESS = 0.55    # book: direct answer, true-success probability
RETRIEVE_SUCCESS = 0.80  # book: retrieve then answer, true-success probability
RETRIEVAL_COST = 0.05    # book: retrieval cost on the same utility scale
NET_RETRIEVE = RETRIEVE_SUCCESS - RETRIEVAL_COST  # 0.75, book value

MASK_ACTION_LOGP = -0.4  # book: sampled retrieve action
MASK_TOOL_LOGP = -1.2    # book: observed tool text


def sigmoid(z):
    return 1.0 / (1.0 + math.exp(-z))


def num(x, digits=2):
    """Decimal text without trailing zeros past the first decimal, for written sums."""
    text = fmt(x, digits)
    if "." in text:
        text = text.rstrip("0")
        if text.endswith("."):
            text += "0"
    return text


def snum(x, digits=2):
    text = num(x, digits)
    return f"({text})" if text.startswith("-") else text


def join_sum(terms):
    """'a + b + c' with negative terms in parentheses."""
    return " + ".join(terms)


# Demonstration 1: return-to-go and the action mask

STREAMS = {
    "release": ("release task", [-RETRIEVAL_COST, 0.0, 1.0],
                ["t=0 retrieve", "t=1 draft", "t=2 release"]),
    "exercise": ("exercise", [1.0, 2.0], ["t=0", "t=1"]),
}


def return_to_go(rewards, gamma):
    """G_t = sum over k >= t of gamma^(k - t) r_k, computed by direct summation."""
    T = len(rewards)
    return [sum(gamma ** (k - t) * rewards[k] for k in range(t, T)) for t in range(T)]


def written_return(rewards, gamma, t):
    parts = []
    for k in range(t, len(rewards)):
        weight = gamma ** (k - t)
        parts.append(f"{num(weight, 3)} x {snum(rewards[k])}" if k > t else f"{snum(rewards[k])}")
    value = return_to_go(rewards, gamma)[t]
    return f"G_{t} = " + " + ".join(parts) + f" = {fmt(value, 3)}"


def return_picture(stream="release", gamma=1.0, tool_mask=0):
    gamma = float(gamma)
    mask = int(tool_mask)
    label, rewards, ticks = STREAMS[stream]
    G = return_to_go(rewards, gamma)
    T = len(rewards)
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    x = np.arange(T)
    w = 0.36
    left.bar(x - w / 2, rewards, w, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.1,
             label="reward r_t")
    left.bar(x + w / 2, G, w, color=PALETTE["teal"], label="return-to-go G_t")
    top = max(max(G), max(rewards))
    for xi, r, g in zip(x, rewards, G):
        left.text(xi - w / 2, max(r, 0) + 0.04 * top, fmt(r, 2), ha="center", va="bottom", fontsize=10.5,
                  color=PALETTE["ink"])
        left.text(xi + w / 2, max(g, 0) + 0.04 * top, fmt(g, 3), ha="center", va="bottom", fontsize=10.5,
                  color=PALETTE["teal"])
    left.set_xticks(x, ticks)
    left.set_ylim(min(0, min(rewards)) - 0.05 * top, top * 1.9)
    left.set_xlabel("Step in the episode")
    left.set_ylabel("Reward or return-to-go (constructed units)")
    left.set_title(f"{label.capitalize()}, gamma = {fmt(gamma, 1)}", fontsize=11.5)
    left.legend(loc="upper left", fontsize=10.5, ncol=1, frameon=True)
    left.grid(axis="x", alpha=0)
    # Right panel: the masked token loss from the chapter's unit test.
    terms = [-1 * MASK_ACTION_LOGP, -mask * MASK_TOOL_LOGP]
    loss = terms[0] + terms[1]
    colors = [PALETTE["teal"], PALETTE["terracotta"] if mask else PALETTE["grey"]]
    right.bar([0, 1], terms, 0.55, color=colors, linewidth=0)
    right.text(0, terms[0] + 0.05, f"{fmt(terms[0], 1)}\nmask 1", ha="center", va="bottom", fontsize=10.5,
               color=PALETTE["ink"])
    right.text(1, terms[1] + 0.05, f"{fmt(terms[1], 1)}\nmask {mask}", ha="center", va="bottom", fontsize=10.5,
               color=PALETTE["ink"])
    right.set_xticks([0, 1], ["Retrieve action\n(policy sampled)", "Tool reply text\n(observed only)"])
    right.set_xlim(-0.6, 1.6)
    right.set_ylim(0, 1.75)
    right.set_xlabel("Token (log probability -0.4 and -1.2)")
    right.set_ylabel("Loss term: -mask x log probability")
    right.set_title(f"Selected-token loss = {fmt(loss, 1)}", fontsize=11.5)
    right.grid(axis="x", alpha=0)
    metrics = {f"G_{t}": fmt(G[t], 3) for t in range(T)}
    metrics["Sum of rewards, no discount"] = fmt(sum(rewards), 3)
    metrics["Weight on the last reward in G_0"] = fmt(gamma ** (T - 1), 3)
    metrics["Selected-token loss"] = fmt(loss, 1)
    sums = ". ".join(written_return(rewards, gamma, t) for t in range(T))
    shrink = sum(rewards) - G[0]
    if gamma == 1.0:
        meaning = "With gamma = 1 nothing is discounted, so G_0 equals the plain sum of the rewards."
    else:
        meaning = (f"Discounting lowers G_0 by {fmt(shrink, 3)} compared with the plain sum {fmt(sum(rewards), 3)}, "
                   f"because the last reward is weighted by gamma^{T - 1} = {fmt(gamma ** (T - 1), 3)}.")
    loss_calc = f"-[(1)(-0.4)+({mask})(-1.2)] = {fmt(loss, 1)}"
    if mask:
        mask_text = (f"Loss = {loss_calc}: the loss now also pushes up the probability of a tool reply the policy did not "
                     "generate, and nothing in the number warns about it.")
    else:
        mask_text = f"Loss = {loss_calc}: only the policy's own retrieve action receives token loss."
    interpretation = f"{sums}. {meaning} G_t only adds rewards from step t onward. {mask_text}"
    steps = [f"Rewards are {', '.join(f'r_{t} = {snum(r)}' for t, r in enumerate(rewards))}."]
    last = T - 1
    steps.append(f"The last step has nothing after it: G_{last} = r_{last} = {fmt(G[last], 3)}.")
    for t in range(T - 2, -1, -1):
        steps.append(f"G_{t} = r_{t} + gamma x G_{t + 1} = {snum(rewards[t])} + {num(gamma, 1)} x {snum(G[t + 1], 3)} = {fmt(G[t], 3)}.")
    steps.append(f"Masked loss: -[(1)(-0.4) + ({mask})(-1.2)] = {fmt(loss, 1)}.")
    alt = (f"Left, bars of reward and return-to-go for the {label} at gamma {fmt(gamma, 1)}, G_0 = {fmt(G[0], 3)}. "
           f"Right, the two token loss terms, 0.4 for the retrieve action and "
           f"{fmt(terms[1], 1)} for the tool text with mask {mask}, total loss {fmt(loss, 1)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: the gradient of one choice and the baseline

OUTCOMES = [  # (action, label, success, probability weight within the action, return)
    ("answer", "answer\nfails", 0.0, 1 - DIRECT_SUCCESS, 0.0),
    ("answer", "answer\nwins", 1.0, DIRECT_SUCCESS, 1.0),
    ("retrieve", "retrieve\nfails", 0.0, 1 - RETRIEVE_SUCCESS, -RETRIEVAL_COST),
    ("retrieve", "retrieve\nwins", 1.0, RETRIEVE_SUCCESS, 1.0 - RETRIEVAL_COST),
]
BASELINES = {
    "none": "no baseline",
    "expected": "expected return b",
    "action": "return of the sampled action",
}


def estimator_table(phi, baseline):
    """Exact one-step estimator g = score x (G - b) over the four outcomes (action, success)."""
    p = sigmoid(phi)
    v = p * NET_RETRIEVE + (1 - p) * DIRECT_SUCCESS
    rows = []
    for action, label, _, weight, ret in OUTCOMES:
        prob = (p if action == "retrieve" else 1 - p) * weight
        score = (1 - p) if action == "retrieve" else -p
        if baseline == "none":
            b = 0.0
        elif baseline == "expected":
            b = v
        else:
            b = NET_RETRIEVE if action == "retrieve" else DIRECT_SUCCESS
        rows.append({"label": label, "prob": prob, "score": score, "ret": ret, "b": b, "g": score * (ret - b)})
    mean = sum(r["prob"] * r["g"] for r in rows)
    second = sum(r["prob"] * r["g"] ** 2 for r in rows)
    spread = math.sqrt(max(second - mean ** 2, 0.0))
    return p, v, rows, mean, second, spread


def retrieve_picture(phi=0.0, baseline="none"):
    phi = float(phi)
    p, v, rows, mean, second, spread = estimator_table(phi, baseline)
    gain = NET_RETRIEVE - DIRECT_SUCCESS  # 0.20
    utility = DIRECT_SUCCESS + gain * p
    gradient = gain * p * (1 - p)
    zs = np.linspace(-6, 6, 241)
    ps = 1 / (1 + np.exp(-zs))
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.plot(zs, DIRECT_SUCCESS + gain * ps, color=PALETTE["teal"])
    half = 1.6
    left.plot([phi - half, phi + half], [utility - gradient * half, utility + gradient * half], color=PALETTE["gold"],
              linewidth=2.2, linestyle="dashed")
    left.plot([phi], [utility], "o", color=PALETTE["terracotta"], markersize=9)
    if phi >= 2:
        label_point(left, phi, utility, f"J = {fmt(utility, 3)}\nslope {fmt(gradient, 4)}", color=PALETTE["terracotta"],
                    dx=-10, dy=-12, ha="right", va="top").set_bbox(BOX)
    else:
        label_point(left, phi, utility, f"J = {fmt(utility, 3)}\nslope {fmt(gradient, 4)}", color=PALETTE["terracotta"],
                    dx=10, dy=-12, ha="left", va="top").set_bbox(BOX)
    label_point(left, 5.8, DIRECT_SUCCESS, "always answer directly", color=PALETTE["grey"], dx=0, dy=-4, ha="right", va="top")
    label_point(left, 5.8, NET_RETRIEVE, "always retrieve", color=PALETTE["grey"], dx=0, dy=4, ha="right", va="bottom")
    left.set_xlim(-6, 6)
    left.set_ylim(DIRECT_SUCCESS - 0.05, 0.88)
    left.set_xlabel("Policy parameter phi")
    left.set_ylabel("Expected utility J (success minus cost)")
    left.set_title("Utility and its slope (dashed)", fontsize=11.5)
    gs = [r["g"] for r in rows]
    colors = [PALETTE["grey"], PALETTE["grey"], PALETTE["navy"], PALETTE["navy"]]
    xs = np.arange(4)
    right.bar(xs, gs, 0.6, color=colors, linewidth=0)
    right.axhline(mean, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.6)
    right.axhline(0, color=PALETTE["ink"], linewidth=0.8)
    # Fixed limits per phi across the three baselines, so bar heights stay comparable when the baseline control changes.
    all_g = [r["g"] for bl in BASELINES for r in estimator_table(phi, bl)[2]]
    all_mean = [estimator_table(phi, bl)[3] for bl in BASELINES]
    span = max(max(all_g), 0.1) - min(min(all_g), -0.1)
    low = min(min(all_g), 0, min(all_mean)) - 0.28 * span
    high = max(max(all_g), 0, max(all_mean)) + 0.32 * span
    for xi, g in zip(xs, gs):
        if g >= 0:
            right.text(xi, g + 0.02 * span, fmt(g, 3), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        else:
            right.text(xi, g - 0.02 * span, fmt(g, 3), ha="center", va="top", fontsize=10.5, color=PALETTE["ink"])
    right.set_xticks(xs, [f"{r['label']}\n{fmt(r['prob'], 3)}" for r in rows])
    right.set_ylim(low, high)
    right.set_xlim(-0.6, 3.6)
    right.set_xlabel("Sampled outcome and probability (dashed: mean)")
    right.set_ylabel("Update signal g = score x (G - b)")
    short = {"none": "No baseline", "expected": "Baseline b", "action": "Action baseline"}[baseline]
    right.set_title(f"{short}: mean {fmt(mean, 3)}, spread {fmt(spread, 3)}", fontsize=11.5)
    right.grid(axis="x", alpha=0)
    b_text = {"none": "0", "expected": fmt(v, 4), "action": "0.55 or 0.75"}[baseline]
    metrics = {
        "Retrieve probability p": fmt(p, 4),
        "Expected utility J": fmt(utility, 4),
        "True gradient dJ/dphi": fmt(gradient, 4),
        "Mean of the update signal": fmt(mean, 4),
        "Spread (standard deviation)": fmt(spread, 4),
        "Baseline value": b_text,
    }
    mean_terms = [f"{fmt(r['prob'], 4)} x {snum(r['g'], 4)}" for r in rows]
    second_terms = [f"{fmt(r['prob'], 4)} x {fmt(r['g'] ** 2, 4)}" for r in rows]
    if baseline == "none":
        verdict = (f"This is Equation (13.2) with T = 1 and no baseline: the mean equals the true gradient {fmt(gradient, 4)}, "
                   f"and the spread {fmt(spread, 4)} is the noise in each sampled update.")
    elif baseline == "expected":
        verdict = (f"The baseline b = {fmt(v, 4)} depends only on the context, so the mean is still the true gradient "
                   f"{fmt(gradient, 4)} and only the spread changes, from {fmt(estimator_table(phi, 'none')[5], 4)} to {fmt(spread, 4)}.")
    else:
        verdict = (f"This baseline uses the sampled action, so the expectation-zero argument no longer applies: the mean is "
                   f"{fmt(mean, 4)} instead of the true gradient {fmt(gradient, 4)}. Small spread is bought by losing the learning direction.")
    interpretation = (
        f"p = 1 / (1 + e^({fmt(-phi, 1)})) = {fmt(p, 4)}; true gradient = 0.20 x {fmt(p, 4)} x {fmt(1 - p, 4)} = {fmt(gradient, 4)}. "
        f"Mean of g = {join_sum(mean_terms)} = {fmt(mean, 4)}. "
        f"E[g^2] = {join_sum(second_terms)} = {fmt(second, 4)}, so spread = sqrt({fmt(second, 4)} - {fmt(mean ** 2, 4)}) = {fmt(spread, 4)}. {verdict}"
    )
    steps = [
        f"Retrieve probability p = sigma({fmt(phi, 1)}) = {fmt(p, 4)}.",
        f"Scores: retrieve 1 - p = {fmt(1 - p, 4)}, answer -p = {snum(-p, 4)}. Check: p x (1 - p) + (1 - p) x (-p) = 0.",
        f"Returns G: answer fails 0, answer wins 1, retrieve fails -0.05, retrieve wins 0.95.",
        f"Baseline b is {b_text}; update signal g = score x (G - b).",
        "g by outcome: " + ", ".join(f"{r['label'].replace(chr(10), ' ')} {snum(r['g'], 3)}" for r in rows) + ".",
        f"Mean = sum of probability x g = {fmt(mean, 4)}; true gradient {fmt(gradient, 4)}.",
        f"Spread = sqrt(E[g^2] - mean^2) = sqrt({fmt(second, 4)} - {fmt(mean ** 2, 4)}) = {fmt(spread, 4)}.",
    ]
    alt = (f"Left, expected utility against phi with a dashed tangent at phi {fmt(phi, 1)}, utility {fmt(utility, 3)}. "
           f"Right, four bars for the update signal of each sampled outcome with {BASELINES[baseline]}; "
           f"the dashed mean line is {fmt(mean, 3)} and the spread is {fmt(spread, 3)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: training on a verifier (laboratory function)

SCENARIOS = {
    "default": {
        "rewards": [1, 2], "success": [0.9, 0.2], "pots": [0, 0], "seeds": [3, 11], "lr": 0.08, "episodes": 120,
        "evals": 200, "names": ["action 0", "action 1"], "heading": "Default case",
    },
    "changed": {
        "rewards": [2, 1], "success": [0.9, 0.2], "pots": [0, 0], "seeds": [3, 11], "lr": 0.08, "episodes": 120,
        "evals": 200, "names": ["action 0", "action 1"], "heading": "Changed case",
    },
    "transfer": {
        "rewards": [0, 1], "success": [0, 1], "pots": [2, 0], "seeds": [7, 17], "lr": 0.1, "episodes": 100,
        "evals": 100, "names": ["action 0", "action 1"], "heading": "Transfer case",
    },
    "story": {
        "rewards": [0.63, 0.73, 0.95], "success": [0.55, 0.80, 0.0], "pots": [0, 0, 0], "seeds": [3, 11], "lr": 0.08,
        "episodes": 120, "evals": 200, "names": ["answer directly", "retrieve", "shortcut tool"],
        "heading": "Noisy verifier with a shortcut tool",
    },
}
LENGTHS = {"short": 10, "long": 400}


def lab_run(scenario, length):
    sc = SCENARIOS[scenario]
    episodes = sc["episodes"] if length == "case" else LENGTHS[length]
    data = {"rewards": sc["rewards"], "success_probabilities": sc["success"], "terminal_potentials": sc["pots"],
            "episodes": episodes, "seeds": sc["seeds"], "learning_rate": sc["lr"], "discount": 1,
            "evaluation_runs": sc["evals"]}
    return evaluate(data), episodes


def verifier_picture(scenario="default", length="case"):
    sc = SCENARIOS[scenario]
    out, episodes = lab_run(scenario, length)
    shaped = out["metrics"]["shaped_rewards"]
    runs = out["metrics"]["runs"]
    k = len(shaped)
    names = sc["names"]
    seeds = sc["seeds"]
    success = sc["success"]
    start_reward = sum(shaped) / k
    start_success = sum(success) / k
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    for curve, ls in zip(out["series"], ["solid", "dashed"]):
        left.plot(np.array(curve["x"]) + 1, curve["y"], color=PALETTE["navy"], linestyle=ls, linewidth=1.8)
    left.axhline(start_reward, color=PALETTE["grey"], linestyle="dotted", linewidth=1.4)
    left.set_xlim(1, episodes)
    low, high = min(shaped), max(shaped)
    spread = max(high - low, 0.1)
    left.set_ylim(low - 0.08 * spread, high + 0.4 * spread)
    label_point(left, episodes, start_reward, f"start {fmt(start_reward, 2)} (dotted)", color=PALETTE["grey"], dx=-4,
                dy=-6, ha="right", va="top").set_bbox(BOX)
    label_point(left, episodes, low - 0.04 * spread, f"solid: seed {seeds[0]}, dashed: seed {seeds[1]}",
                color=PALETTE["navy"], dx=-4, dy=0, ha="right", va="bottom")
    left.set_xlabel("Training episode")
    left.set_ylabel("Expected reward the learner trains on")
    left.set_title("What the learner is trained on", fontsize=11.5)
    values = [start_success] + [r["expected_external_success"] for r in runs]
    colors = [PALETTE["grey"], PALETTE["teal"], PALETTE["teal"]]
    marks = [None] + [r["independent_evaluation_rate"] for r in runs]
    for i, (val, c) in enumerate(zip(values, colors)):
        right.bar(i, val, 0.6, color=c, linewidth=0)
        right.text(i, max(val, marks[i] or 0.0) + 0.045, fmt(val, 3), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"],
                   zorder=5, bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.95})
    for i, r in enumerate(runs, start=1):
        right.plot([i], [r["independent_evaluation_rate"]], "D", color=PALETTE["gold"], markersize=8, zorder=6)
    best, worst = max(success), min(success)
    right.axhline(best, color=PALETTE["olive"], linestyle="dashed", linewidth=1.3)
    right.axhline(worst, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.3)
    label_point(right, 3.45, best, f"best action {fmt(best, 2)}", color=PALETTE["olive"], dx=0, dy=4, ha="right").set_bbox(BOX)
    label_point(right, 3.45, worst, f"worst action {fmt(worst, 2)}", color=PALETTE["terracotta"], dx=0, dy=4,
                ha="right").set_bbox(BOX)
    label_point(right, -0.45, 1.19, f"diamond: sampled evaluation, n = {sc['evals']}", color=PALETTE["gold"], dx=0, dy=0,
                ha="left", va="top")
    right.set_xticks(range(3), ["start", f"seed {seeds[0]}", f"seed {seeds[1]}"])
    right.set_xlim(-0.5, 3.5)
    right.set_ylim(0, 1.22)
    right.set_xlabel("Policy")
    right.set_ylabel("Expected true task success")
    right.set_title(f"What the task gets after {episodes} episodes", fontsize=11.5)
    right.grid(axis="x", alpha=0)
    ra, rb = runs
    metrics = {
        "Start: reward trained on": fmt(start_reward, 3),
        "Start: true success": fmt(start_success, 3),
        f"Seed {seeds[0]}: reward trained on": fmt(ra["expected_shaped_reward"], 3),
        f"Seed {seeds[0]}: true success": fmt(ra["expected_external_success"], 3),
        f"Seed {seeds[1]}: true success": fmt(rb["expected_external_success"], 3),
        f"Seed {seeds[0]}: sampled evaluation, n = {sc['evals']}": fmt(ra["independent_evaluation_rate"], 3),
    }
    opt = out["metrics"]["shaped_optimal_action"]
    task = out["metrics"]["task_optimal_action"]
    conflict = out["metrics"]["training_objective_conflicts_with_task"]
    metrics["Learner's best action"] = names[opt]
    metrics["Task's best action"] = names[task]
    if not out["metrics"]["policy_invariant_shaping_condition"]:
        metrics[f"Seed {seeds[0]}: unshaped verifier reward"] = fmt(ra["expected_training_reward"], 3)
    pol = [round(q, 4) for q in ra["policy"]]
    pol_text = ", ".join(f"{names[i]} {fmt(q, 4)}" for i, q in enumerate(pol))
    shaped_calc = join_sum([f"{fmt(q, 4)} x {snum(shaped[i])}" for i, q in enumerate(pol)])
    succ_calc = join_sum([f"{fmt(q, 4)} x {snum(success[i])}" for i, q in enumerate(pol)])
    reward_val = sum(q * shaped[i] for i, q in enumerate(pol))
    succ_val = sum(q * success[i] for i, q in enumerate(pol))
    share = "1/3" if k == 3 else fmt(1 / k, 3)  # 0.333 x 2.31 would print 0.769, not the 0.770 shown
    start_reward_calc = join_sum([f"{share} x {snum(shaped[i])}" for i in range(k)])
    start_succ_calc = join_sum([f"{share} x {snum(success[i])}" for i in range(k)])
    pa = ra["expected_external_success"]
    se = math.sqrt(pa * (1 - pa) / sc["evals"])
    if scenario == "default":
        verdict = ("The verifier pays most for the action with the lowest task success, so the learner moves toward it. "
                   "The reward curve climbs while the task result falls, and a plot of reward alone would call this progress.")
    elif scenario == "changed":
        verdict = ("Here the verifier and the task agree on the best action, so reward and task success rise together. "
                   "That agreement is a property of these constructed numbers, not something training can create.")
    elif scenario == "transfer":
        verdict = ("Action 0 has task success 0 but terminal potential 2, so its trained-on reward is 0 + 1 x 2 = 2 against 1 for "
                   "action 1. The unshaped verifier would still prefer action 1, yet the learner follows the shaped number and the task "
                   "result falls. A terminal bonus changed the objective.")
    else:
        verdict = ("The verifier scores are the chapter's expected scores: direct 0.55 x 0.9 + 0.45 x 0.3 = 0.63, retrieve "
                   "0.80 x 0.9 + 0.20 x 0.3 - 0.05 = 0.73, and the shortcut tool is accepted every time (0.95) with true success 0. "
                   "The learner is drawn to the shortcut, so measured reward rises while true success falls.")
    interpretation = (
        f"{sc['heading']}. Start: {start_reward_calc} = {fmt(start_reward, 3)} reward and {start_succ_calc} = {fmt(start_success, 3)} true success. "
        f"After {episodes} episodes seed {seeds[0]} has {pol_text}: reward = {shaped_calc} = {fmt(reward_val, 4)}; "
        f"true success = {succ_calc} = {fmt(succ_val, 4)}. "
        f"A sample of {sc['evals']} from exact {fmt(pa, 3)} has standard error sqrt({fmt(pa, 3)} x {fmt(1 - pa, 3)} / {sc['evals']}) = {fmt(se, 3)}, "
        f"so the sampled evaluation {fmt(ra['independent_evaluation_rate'], 3)} is a noisy view of the exact number. {verdict}"
    )
    steps = [
        f"Trained-on rewards (reward + gamma x terminal potential): " + ", ".join(
            f"{names[i]} {snum(sc['rewards'][i])} + 1 x {snum(sc['pots'][i])} = {snum(shaped[i])}" for i in range(k)) + ".",
        f"Start with equal odds; reward = {start_reward_calc} = {fmt(start_reward, 3)}, true success = {start_succ_calc} = {fmt(start_success, 3)}.",
        f"Each episode samples an action and raises its odds when its reward beats the policy's average reward.",
        f"After {episodes} episodes (seed {seeds[0]}): {pol_text}.",
        f"Reward trained on = {shaped_calc} = {fmt(reward_val, 4)}.",
        f"True success = {succ_calc} = {fmt(succ_val, 4)}.",
        f"The learner's best action is {names[opt]}; the task's best is {names[task]}"
        + (" (a conflict)." if conflict else " (no conflict)."),
    ]
    alt = (f"{sc['heading']}. Left, two training curves of the reward the learner trains on, rising from {fmt(start_reward, 2)}. "
           f"Right, true success bars: start {fmt(start_success, 3)}, seed {seeds[0]} {fmt(ra['expected_external_success'], 3)}, "
           f"seed {seeds[1]} {fmt(rb['expected_external_success'], 3)}, with sampled evaluation diamonds.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: shaping

def shaping_picture(evidence_potential=0.4, retrieve_end_potential=0.0, direct_end_potential=0.0):
    e = float(evidence_potential)
    tr = float(retrieve_end_potential)
    d = float(direct_end_potential)
    gamma = 1.0
    rewards = [-RETRIEVAL_COST, 1.0]
    pots = [0.0, e, tr]  # start, evidence state, terminal state of the retrieve route
    shaped = [rewards[t] + gamma * pots[t + 1] - pots[t] for t in range(2)]
    g0 = sum(rewards)
    g0_shaped = sum(shaped)
    g0_formula = g0 - pots[0] + gamma ** 2 * pots[2]
    direct_shaped = DIRECT_SUCCESS + gamma * d
    retrieve_shaped = NET_RETRIEVE + gamma ** 2 * tr
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    x = np.arange(2)
    w = 0.36
    left.bar(x - w / 2, rewards, w, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.1, label="original r_t")
    left.bar(x + w / 2, shaped, w, color=PALETTE["navy"], label="shaped r'_t")
    for xi, r, s in zip(x, rewards, shaped):
        left.text(xi - w / 2, max(r, 0) + 0.025, fmt(r, 2), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        left.text(xi + w / 2, max(s, 0) + 0.025, fmt(s, 2), ha="center", va="bottom", fontsize=10.5, color=PALETTE["navy"])
    left.set_xticks(x, ["t=0 retrieve", "t=1 release"])
    left.set_ylim(-0.12, 1.5)
    left.set_xlabel("Step on the retrieve route (release succeeds)")
    left.set_ylabel("Reward at step t")
    left.set_title(f"Evidence potential {fmt(e, 1)}: sum {fmt(g0_shaped, 2)}", fontsize=11.5)
    left.legend(loc="upper left", fontsize=10.5, frameon=True)
    left.grid(axis="x", alpha=0)
    routes = ["Answer directly", "Retrieve then answer"]
    originals = [DIRECT_SUCCESS, NET_RETRIEVE]
    shapeds = [direct_shaped, retrieve_shaped]
    xr = np.arange(2)
    right.bar(xr - w / 2, originals, w, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.1, label="original G_0")
    right.bar(xr + w / 2, shapeds, w, color=PALETTE["teal"], label="shaped G'_0")
    for xi, o, s in zip(xr, originals, shapeds):
        right.text(xi - w / 2, o + 0.02, fmt(o, 2), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        right.text(xi + w / 2, s + 0.02, fmt(s, 2), ha="center", va="bottom", fontsize=10.5, color=PALETTE["teal"])
    right.set_xticks(xr, routes)
    right.set_ylim(0, 1.5)
    right.set_xlabel("Route")
    right.set_ylabel("Expected return from the start state")
    right.set_title(f"End potentials: retrieve {fmt(tr, 1)}, direct {fmt(d, 1)}", fontsize=11.5)
    right.legend(loc="upper left", fontsize=10.5, frameon=True, ncol=2)
    right.grid(axis="x", alpha=0)
    if is_tie(direct_shaped, retrieve_shaped):
        ranking = "tie"
        verdict = (f"The shaped returns tie at {fmt(direct_shaped, 2)}. The original ranking (retrieve first) is lost, and "
                   "Equation (13.4) does not say which route the learner should prefer.")
    elif direct_shaped > retrieve_shaped:
        ranking = "Answer directly"
        verdict = (f"The direct route now ranks first, {fmt(direct_shaped, 2)} against {fmt(retrieve_shaped, 2)}. The end potential "
                   "belongs to one route only, so it is not a common offset. A bonus of 0.30 for avoiding retrieval gives the same "
                   "direct return, 0.55 + 0.30 = 0.85, and encodes a different trade-off rather than better evidence gathering.")
    else:
        ranking = "Retrieve then answer"
        if d == 0.0 and tr == 0.0:
            verdict = ("Retrieving ranks first. Both end potentials are 0, so the shaped returns equal the "
                       "original ones and nothing has changed.")
        elif tr > 0 and d == 0.0:
            verdict = ("Retrieving ranks first, now by a larger margin. The retrieve route's end potential adds to its return, "
                       "so the returns are no longer the true ones even though the ranking held.")
        elif math.isclose(d, tr, abs_tol=1e-9):
            verdict = (f"Retrieving still ranks first. Both routes carry the same end potential {fmt(tr, 1)}, a common offset, so the "
                       "ranking is unchanged by construction, but the returns are no longer the true ones.")
        else:
            verdict = (f"Retrieving still ranks first. The end potentials differ by {fmt(abs(d - tr), 1)}, which is less than the "
                       f"original gap {fmt(NET_RETRIEVE - DIRECT_SUCCESS, 2)}, so the ranking holds, but the returns are no longer the true ones.")
    metrics = {
        "Retrieve route G_0 (success case)": fmt(g0, 2),
        "Retrieve route G'_0 (success case)": fmt(g0_shaped, 2),
        "Direct route G'_0": fmt(direct_shaped, 2),
        "Retrieve route expected G'_0 (0.80 success)": fmt(retrieve_shaped, 2),
        "Ranked first after shaping": ranking,
    }
    interpretation = (
        f"r'_0 = {snum(rewards[0])} + 1 x {fmt(e, 1)} - 0 = {fmt(shaped[0], 2)}. "
        f"r'_1 = {fmt(rewards[1], 0)} + 1 x {fmt(tr, 1)} - {fmt(e, 1)} = {fmt(shaped[1], 2)}. "
        f"Their sum is {fmt(g0_shaped, 2)}, which equals G_0 - 0 + 1 x {fmt(tr, 1)} = {fmt(g0_formula, 2)} from Equation (13.4): "
        f"the {fmt(e, 1)} added at t=0 is taken back at t=1, and only the end potential survives. "
        f"Routes: direct = 0.55 + 1 x {fmt(d, 1)} = {fmt(direct_shaped, 2)}, "
        f"retrieve = 0.80 - 0.05 + 1 x {fmt(tr, 1)} = {fmt(retrieve_shaped, 2)}. {verdict}"
    )
    steps = [
        f"Potentials: start 0, evidence state {fmt(e, 1)}, retrieve-route end {fmt(tr, 1)}, direct-route end {fmt(d, 1)}.",
        f"r'_0 = r_0 + Pot(evidence) - Pot(start) = {snum(rewards[0])} + {fmt(e, 1)} - 0 = {fmt(shaped[0], 2)}.",
        f"r'_1 = r_1 + Pot(end) - Pot(evidence) = 1 + {fmt(tr, 1)} - {fmt(e, 1)} = {fmt(shaped[1], 2)}.",
        f"Sum G'_0 = {fmt(shaped[0], 2)} + {fmt(shaped[1], 2)} = {fmt(g0_shaped, 2)}; Equation (13.4) gives {fmt(g0, 2)} - 0 + {fmt(tr, 1)} = {fmt(g0_formula, 2)}.",
        f"Direct route: 0.55 + {fmt(d, 1)} = {fmt(direct_shaped, 2)}.",
        f"Retrieve route: 0.75 + {fmt(tr, 1)} = {fmt(retrieve_shaped, 2)}.",
        f"Ranked first: {ranking}.",
    ]
    alt = (f"Left, original and shaped rewards of the retrieve route with evidence potential {fmt(e, 1)}; the shaped sum is "
           f"{fmt(g0_shaped, 2)}. Right, original and shaped returns of the two routes: direct {fmt(direct_shaped, 2)}, "
           f"retrieve {fmt(retrieve_shaped, 2)}; ranked first: {ranking}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 13,
    "title": "Learning to Choose: Training an Agent from Trajectories",
    "subtitle": "Learning changes the chooser itself, and a reward that rises is not the same as a task that improves.",
    "summary": (
        "These four demonstrations follow the chapter's retrieve-or-answer agent. They show what a trajectory records and which "
        "tokens receive loss, how a policy-gradient update moves the chance of retrieving and what a baseline does to its noise, "
        "how a verifier that is wrong about success can steer training (the laboratory's default, changed and transfer cases and "
        "the chapter's shortcut story), and what reward shaping does and does not change. Every number is a constructed teaching value."
    ),
    "ask_skill": {
        "prompt": (
            "Run the learning probe on rewards 1 and 2 with external success 0.9 and 0.2, seeds 3 and 11, 120 episodes, learning "
            "rate 0.08 and 200 evaluation runs. Tell me which action the verifier prefers and which the task prefers, report the exact expected success and "
            "the separately sampled evaluation rate for each seed, and say whether training improved the task or only the signal."
        )
    },
    "demos": [
        {
            "id": "C13-D01",
            "title": "What one episode records: return-to-go and the action mask",
            "question": "What return is each step credited with, and which tokens of an episode receive training loss?",
            "equations": [EQ_TRAJECTORY, EQ_MASK],
            "symbols": (
                "tau is one whole episode: observations o, actions a and rewards r, ending at the terminal observation o_T. "
                "r_t is the reward at step t. G_t is the return-to-go: the discounted sum of rewards from step t to the end. "
                "gamma is the discount, a number from 0 to 1 that shrinks later rewards. T is the number of reward steps. "
                "The mask is a zero-or-one weight on each token's loss: the sampled retrieve action has log probability -0.4 and "
                "the observed tool reply text has log probability -1.2."
            ),
            "prediction": "In the exercise stream (rewards 1 then 2), what is G_0 when gamma is 0.5? Then switch the tool-text mask to 1 and watch the loss.",
            "prediction_options": ["1.5", "2.0", "2.5", "3.0"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "G_0 = 1 + 0.5 x 2 = 2.0, which is the chapter's Exercise 1. The first reward counts in full and the second is halved.",
                "incorrect": "The first reward counts in full and each later reward is multiplied by gamma for every step of delay, so G_0 = 1 + 0.5 x 2 = 2.0. Choose the exercise stream and gamma 0.5 to see it.",
            },
            "misconception": {
                "title": "A stable gradient means the right tokens are being trained",
                "text": (
                    "The chapter warns that if the tool-text mask becomes one, the implementation optimizes the probability of a response "
                    "the policy did not generate, and the gradient can look stable while training on the wrong distribution. Set the mask "
                    "to 1: the loss rises from 0.4 to 1.6."
                ),
            },
            "scope_note": {
                "text": (
                    "The masked-token check confirms one gradient computation. It does not show that a completed policy update "
                    "improved true success."
                ),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "Equation (13.1) lists what an episode contains and then defines G_t by adding the rewards from step t on, "
                "each multiplied by gamma raised to the number of steps since t. A late reward therefore counts less in an early "
                "step's return when gamma is below 1, and the last step's return is always just its own reward. Observations enter "
                "as context and carry mask 0, so only the policy's own sampled action gets loss: the chapter's loss is "
                "-[(1)(-0.4) + (0)(-1.2)] = 0.4."
            ),
            "application": (
                "When a training log reports one number per episode, ask which return it is, and when a loss is reported, ask which "
                "tokens it covers. A comparison needs the same definition on both sides."
            ),
            "assumptions": (
                "A short episode with fixed rewards and no randomness, and one gradient computation for the mask. Real trajectories "
                "include many tokens, and only the policy's own actions receive credit. The release task values are constructed for "
                "this reader; the log probabilities -0.4 and -1.2 are the chapter's."
            ),
            "check": "For rewards 1 then 2 with gamma = 0.9, what return is credited to the first action?",
            "answer": "G_0 = 1 + 0.9 x 2 = 2.8. The second step's return stays G_1 = 2.",
            "provenance": "Constructed example: the chapter's own exercise (rewards 1 and 2), the chapter's mask unit test (log probabilities -0.4 and -1.2) and a three-step release task with the book's retrieval cost 0.05, defined for this reader.",
            "source_section": "What one training episode contains",
            "source_anchor": "what-one-training-episode-contains",
            "controls": [
                {"key": "stream", "label": "Reward stream", "values": ["release", "exercise"], "default": "release",
                 "value_labels": ["Release task: -0.05, 0, 1", "Chapter exercise: 1, 2"]},
                {"key": "gamma", "label": "Discount gamma", "values": [1.0, 0.9, 0.5], "default": 1.0},
                {"key": "tool_mask", "label": "Mask on the observed tool text", "values": [0, 1], "default": 0,
                 "value_labels": ["Mask 0 (excluded from the loss)", "Mask 1 (counted by mistake)"]},
            ],
            "function": "return_picture",
        },
        {
            "id": "C13-D02",
            "title": "Retrieve or answer: the gradient of one choice and what a baseline changes",
            "question": "If a policy retrieves with probability p = sigma(phi), what is the expected learning signal, and what does a baseline do to its noise?",
            "equations": [EQ_GRADIENT, EQ_ZERO],
            "symbols": (
                "phi is the trainable policy parameter and p = sigma(phi) the probability of retrieving before answering. J is the "
                "expected utility: 0.55 for answering directly and 0.80 - 0.05 = 0.75 for retrieving first, mixed by p. sigma is the "
                "logistic function, sigma(z) = 1 / (1 + e^(-z)). In Equation (13.2), pi_phi(a_t | o_t) is the probability "
                "the policy gives action a_t after observation o_t, tau is an episode generated by following that policy, E is the "
                "average over such episodes, G_t is the return of the sampled action, and the log-probability term is its score: "
                "1 - p for retrieving and -p for answering. Here T = 1 and gamma^t = 1, because there is one decision. b is a baseline "
                "subtracted from G, and the update signal g is the score times (G - b)."
            ),
            "prediction": "At phi = 0, switch the baseline from none to the expected return b. What happens to the mean update signal and to its spread?",
            "prediction_options": [
                "The mean stays 0.05 and the spread shrinks",
                "The mean shrinks and the spread stays the same",
                "Both the mean and the spread shrink",
                "Nothing changes",
            ],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "The baseline depends only on the context, so the expected gradient stays 0.05. Only the variance changes, as Figure 13.2 says.",
                "incorrect": "A baseline that does not depend on the sampled action changes variance, not the expected gradient. Set phi to 0 and compare the baselines.",
            },
            "misconception": {
                "title": "A learned critic has found which earlier action caused the outcome",
                "text": (
                    "The chapter says an actor-critic pairs the policy with a learned value function that serves as the baseline, and that "
                    "it has not thereby identified which earlier action caused the outcome. The baseline only reduces noise."
                ),
            },
            "scope_note": {
                "text": (
                    "Equation (13.2) supplies a direction in expectation, not a guarantee that any single sampled update is beneficial. "
                    "The retrieve-or-answer numbers are stipulated for teaching."
                ),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "Expected utility is 0.55 plus 0.20 times p. Because p = sigma(phi) flattens near 0 and 1, the slope is 0.20 p (1 - p), "
                "largest at p = 0.5. Equation (13.2) says each sampled update is the score times the return; its average is that slope. "
                "Subtracting a baseline that depends only on the context leaves the average alone because the scores average to zero, "
                "but it shrinks the swings between samples. A baseline that uses the sampled action breaks that argument."
            ),
            "application": (
                "With a logistic parameterization, a policy that is already nearly sure of its choice receives almost no learning signal, "
                "even if the other choice is better. A training log should show action frequencies, not only an average reward."
            ),
            "assumptions": (
                "One decision with two actions, a fixed environment and exact expectations over the four outcomes. The expectation-zero "
                "argument requires the stated conditioning and action independence. The success values 0.55 and 0.80 and the cost 0.05 are "
                "the book's constructed numbers."
            ),
            "check": "With retrieve success 0.70 (cost still 0.05) and p = 0.5, what is the true gradient?",
            "answer": "Net value of retrieving = 0.70 - 0.05 = 0.65, gain = 0.65 - 0.55 = 0.10, so the slope is 0.10 x 0.5 x 0.5 = 0.025.",
            "provenance": "Constructed example: the chapter's retrieve-or-answer values 0.55, 0.80 and the cost 0.05; the baselines are defined for this reader from the chapter's Figure 13.2 discussion.",
            "source_section": "Retrieve or answer",
            "source_anchor": "retrieve-or-answer",
            "controls": [
                {"key": "phi", "label": "Policy parameter phi", "values": [-2, 0, 1, 3], "default": 0},
                {"key": "baseline", "label": "Baseline subtracted from the return", "values": ["none", "expected", "action"],
                 "default": "none",
                 "value_labels": ["None", "Expected return b (context only)", "Return of the sampled action (breaks the rule)"]},
            ],
            "function": "retrieve_picture",
        },
        {
            "id": "C13-D03",
            "title": "A verifier can teach the wrong success",
            "question": "If the verifier rewards the action that the task does not need, does more training help or hurt the task?",
            "equations": [EQ_GRADIENT],
            "symbols": (
                "The policy chooses among actions, each with a reward the learner trains on and a true-success probability (what the task "
                "needs). The default case has rewards 1 and 2 with success 0.9 and 0.2; the changed case swaps the rewards; the transfer case "
                "has rewards 0 and 1, success 0 and 1 and terminal potentials 2 and 0; the story case uses the chapter's expected verifier "
                "scores 0.63, 0.73 and 0.95 for answering directly, retrieving and a shortcut tool with true success 0.55, 0.80 and 0. "
                "Training makes a sampled update in the form of Equation (13.2), with a baseline equal to the policy's expected reward and "
                "softmax logits, so only the trained-on reward drives the change. In that equation pi_phi(a_t | o_t) is the policy's "
                "probability of action a_t, tau an episode, E an average over episodes, G_t the return, and gamma^t = 1 because there is "
                "one decision (T = 1). Two random seeds show the spread; the diamond is a separately sampled evaluation."
            ),
            "prediction": "In the default case (the verifier prefers action 1), will the longest training leave true success above or below the starting 0.55?",
            "prediction_options": ["Above 0.55", "Below 0.55", "Exactly 0.55"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Below. The update raises the action with the higher reward, which has task success 0.2, so true success falls while reward rises.",
                "incorrect": "The update raises the action with the higher reward, and that action has the lower task success, so true success ends below 0.55. Select the default case and step the training length to 400.",
            },
            "misconception": {
                "title": "A rising verifier score is a rising true-success curve",
                "text": (
                    "The chapter says a training curve measured by the verifier cannot be renamed a true-success curve. In the default "
                    "case the left curve climbs while the right bars fall."
                ),
            },
            "scope_note": {
                "text": (
                    "A policy update that raises measured reward while reward-model acceptance diverges from true success is not thereby "
                    "shown safe to ship. The noisy-verifier numbers are stipulated for teaching."
                ),
                "source_section": "What this does not settle",
            },
            "stepper": "length",
            "explanation": (
                "The update raises the probability of whichever action earns more reward than average. If that action has "
                "the lower success, the policy drifts toward failure while its reward curve rises. Swapping the two rewards "
                "makes the same update raise success. In the transfer case the terminal potential 2 lifts action 0's trained-on "
                "reward above action 1's, and in the story case the shortcut tool is accepted every time. The diamonds show a "
                "separately sampled evaluation: a single sampled rate is a noisy view of the exact number."
            ),
            "application": (
                "Before calling a rising reward curve an improvement, compute what the policy would score under a check that the reward "
                "model does not share, such as an outside audit of the outcome, and keep the evaluation sample separate from training."
            ),
            "assumptions": (
                "One-step choice, a fixed learning rate (0.08, or 0.1 in the transfer case), and two seeds. Rewards are fixed numbers, "
                "so the story case uses the chapter's expected scores rather than noisy draws. Real tasks have many steps. The seeds show "
                "that a run is a sample; they are not an estimate of how often it happens elsewhere."
            ),
            "check": "In the transfer case, if training ended at probability 0.90 for action 0, what is the true success?",
            "answer": "0.90 x 0 + 0.10 x 1 = 0.10, far below the start of 0.5 x 0 + 0.5 x 1 = 0.50, even though the trained-on reward is 0.90 x 2 + 0.10 x 1 = 1.90.",
            "provenance": "Constructed example: the laboratory's default, changed and transfer training cases, and the chapter's noisy-verifier numbers (0.9, 0.3, 0.55, 0.80, 0.05, shortcut 0.95) as fixed expected scores, run by the laboratory's training function.",
            "source_section": "A verifier can teach the wrong success",
            "source_anchor": "a-verifier-can-teach-the-wrong-success",
            "controls": [
                {"key": "scenario", "label": "Case", "values": ["default", "changed", "transfer", "story"], "default": "default",
                 "value_labels": ["Default: rewards 1, 2; success 0.9, 0.2", "Changed: rewards 2, 1",
                                  "Transfer: rewards 0, 1; potentials 2, 0; success 0, 1",
                                  "Chapter story: noisy verifier plus shortcut tool"]},
                {"key": "length", "label": "Training length", "values": ["short", "case", "long"], "default": "case",
                 "value_labels": ["10 episodes", "The case's own length (120; transfer 100)", "400 episodes"]},
            ],
            "function": "verifier_picture",
        },
        {
            "id": "C13-D04",
            "title": "Reward shaping: what cancels and what does not",
            "question": "Which parts of a shaped return survive the cancellation, and when can an end potential change which route ranks first?",
            "equations": [EQ_SHAPED, EQ_TELESCOPE],
            "symbols": (
                "r_t is the original reward and r'_t the shaped reward. Pot(x) is a potential assigned to state x: 0 at the start, "
                "a chosen value at the evidence state, and chosen end values on the retrieve route and on the direct route. "
                "gamma is 1 (no discount). G_0 and G'_0 are the original and shaped returns of the whole episode, and T the number of "
                "steps. Both routes start at x_0 with potential 0."
            ),
            "prediction": "Give the direct route's end the potential 0.3 (and the retrieve route's end 0). Which route ranks first?",
            "prediction_options": ["Retrieve then answer", "Answer directly", "They tie"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Direct = 0.55 + 0.3 = 0.85 against retrieve = 0.75. The end potential belongs to one route only, so it survives and flips the ranking.",
                "incorrect": "The direct route's end potential is added to its return and not cancelled: 0.55 + 0.3 = 0.85 against 0.75, so the direct route ranks first. Set the direct end to 0.3 and the retrieve end to 0.",
            },
            "misconception": {
                "title": "An extra reward discovers an efficient policy",
                "text": (
                    "The chapter says the additional score did not discover an efficient policy: it encoded a different trade-off, and the "
                    "numerical reward cannot be presented as proof that the policy learned better evidence gathering. A 0.30 bonus for "
                    "avoiding retrieval raises the direct route to 0.85 while its true completion stays 0.55."
                ),
            },
            "scope_note": {
                "text": (
                    "The derivation is a finite constructed one. A process scorer that emits arbitrary positive scores does not automatically take "
                    "the potential-difference form, and fitted scores need separate evidence about what they mean."
                ),
                "source_section": "This is a finite constructed derivation, not a blanket guarantee about learned reward models.",
            },
            "explanation": (
                "Each shaped reward adds the next state's potential and subtracts the current one, so a potential added when "
                "entering a state is subtracted when leaving it. Only the start and end potentials remain, as Equation (13.4) says. "
                "An end potential that only one route reaches does not cancel across routes, and can change the ranking."
            ),
            "application": (
                "If a team adds a bonus for visiting a useful intermediate state, check where the potential ends up. A bonus that "
                "vanishes at the end is bookkeeping; a bonus that remains at some end states is a new objective."
            ),
            "assumptions": (
                "No discount, a fixed starting state and exact expected returns. The potential is a function of state, as "
                "Equation (13.3) requires. The values 0.55, 0.80, 0.05 and 0.4 are the book's constructed numbers; the other "
                "potentials are defined for this reader."
            ),
            "check": "If the direct route's end state had potential 0.1 and the retrieve route's end 0, which route would rank first, and by how much?",
            "answer": "Direct = 0.55 + 0.1 = 0.65, retrieve = 0.80 - 0.05 = 0.75. Retrieving still ranks first, by 0.10.",
            "provenance": "Constructed example: the chapter's release construction (potential 0 at start and end, 0.4 after retrieval) with the book's 0.55, 0.80 and 0.05 and its 0.30 bonus; other potentials defined for this reader.",
            "source_section": "When the reward arrives in pieces",
            "source_anchor": "when-the-reward-arrives-in-pieces",
            "controls": [
                {"key": "evidence_potential", "label": "Potential of the evidence state", "values": [0.4, 1.0], "default": 0.4},
                {"key": "retrieve_end_potential", "label": "Potential at the end of the retrieve route", "values": [0.0, 0.2], "default": 0.0},
                {"key": "direct_end_potential", "label": "Potential at the end of the direct route", "values": [0.0, 0.2, 0.3], "default": 0.0},
            ],
            "function": "shaping_picture",
        },
    ],
}

"""Chapter 13 reader: Learning to Choose.

Four demonstrations built on Equations (13.1) to (13.4) and the chapter's
retrieve-or-answer construction. Demonstration 3 calls the laboratory's own
training function (math_ai_agents.chapters.ch13.evaluate), so the reader, the
notebook and the chapter skill agree. Every number is a constructed teaching
value; Demonstrations 2 and 4 use the book's own retrieve-or-answer numbers
(0.55, 0.80, 0.05, 0.4) and Demonstration 3 uses the laboratory's default case.
"""
import math

import numpy as np

from math_ai_agents.chapters.ch13 import evaluate
from readerkit import PALETTE, fmt, is_tie, label_point, new_figure, signed

EQ_TRAJECTORY = (
    r"\tau=(o_0,a_0,r_0,o_1,a_1,r_1,\ldots,o_T),"
    r"\qquad G_t=\sum_{k=t}^{T-1}\gamma^{k-t}r_k."
)
EQ_GRADIENT = (
    r"\nabla_\phi J(\phi)=\operatorname E_{\tau\sim\pi_\phi}\!\left["
    r"\sum_{t=0}^{T-1}\gamma^t\nabla_\phi\log \pi_\phi(a_t\mid o_t)\,G_t"
    r"\right]."
)
EQ_SHAPED = r"r'_t=r_t+\gamma\operatorname{Pot}(x_{t+1})-\operatorname{Pot}(x_t)."
EQ_TELESCOPE = r"G'_0=G_0-\operatorname{Pot}(x_0)+\gamma^T\operatorname{Pot}(x_T)."

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}

DIRECT_SUCCESS = 0.55    # book: direct answer, true-success probability
RETRIEVE_SUCCESS = 0.80  # book: retrieve then answer, true-success probability
RETRIEVAL_COST = 0.05    # book: retrieval cost on the same utility scale


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


# Demonstration 1

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


def return_picture(stream="release", gamma=1.0):
    gamma = float(gamma)
    label, rewards, ticks = STREAMS[stream]
    G = return_to_go(rewards, gamma)
    T = len(rewards)
    fig, ax = new_figure(height=4.2)
    x = np.arange(T)
    w = 0.36
    ax.bar(x - w / 2, rewards, w, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.1,
           label="reward r_t")
    ax.bar(x + w / 2, G, w, color=PALETTE["teal"], label="return-to-go G_t")
    top = max(max(G), max(rewards))
    for xi, r, g in zip(x, rewards, G):
        ax.text(xi - w / 2, max(r, 0) + 0.04 * top, fmt(r, 2), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        ax.text(xi + w / 2, max(g, 0) + 0.04 * top, fmt(g, 3), ha="center", va="bottom", fontsize=10.5, color=PALETTE["teal"])
    ax.set_xticks(x, ticks)
    ax.set_ylim(min(0, min(rewards)) - 0.05 * top, top * 1.5)
    ax.set_xlabel("Step in the episode")
    ax.set_ylabel("Reward or return-to-go (constructed units)")
    ax.set_title(f"{label.capitalize()}, discount gamma = {fmt(gamma, 1)}", fontsize=11.5)
    ax.legend(loc="upper left", fontsize=10.5, ncol=2, frameon=True)
    ax.grid(axis="x", alpha=0)
    metrics = {f"G_{t}": fmt(G[t], 3) for t in range(T)}
    metrics["Sum of rewards, no discount"] = fmt(sum(rewards), 3)
    metrics["Weight on the last reward in G_0"] = fmt(gamma ** (T - 1), 3)
    sums = ". ".join(written_return(rewards, gamma, t) for t in range(T))
    shrink = sum(rewards) - G[0]
    if gamma == 1.0:
        meaning = "With gamma = 1 nothing is discounted, so G_0 equals the plain sum of the rewards."
    else:
        meaning = (f"Discounting lowers G_0 by {fmt(shrink, 3)} compared with the plain sum {fmt(sum(rewards), 3)}, "
                   f"because the last reward is weighted by gamma^{T - 1} = {fmt(gamma ** (T - 1), 3)}.")
    interpretation = (f"{sums}. {meaning} G_t only adds rewards from step t onward, so each step's return ignores what came before it.")
    return fig, metrics, interpretation


# Demonstration 2

def retrieve_picture(phi=0.0, retrieve_success=RETRIEVE_SUCCESS):
    phi = float(phi)
    q = float(retrieve_success)
    net = q - RETRIEVAL_COST  # utility of retrieving: true success minus the retrieval cost
    gain = net - DIRECT_SUCCESS
    p = sigmoid(phi)
    utility = DIRECT_SUCCESS + gain * p
    gradient = gain * p * (1 - p)
    # Equation (13.2) for one step: the score of each action times its return, averaged over the two actions.
    identity = p * (1 - p) * net + (1 - p) * (-p) * DIRECT_SUCCESS
    zs = np.linspace(-6, 6, 241)
    ps = 1 / (1 + np.exp(-zs))
    fig, (left, right) = new_figure(ncols=2, height=4.2)
    left.plot(zs, DIRECT_SUCCESS + gain * ps, color=PALETTE["teal"])
    half = 1.6
    left.plot([phi - half, phi + half], [utility - gradient * half, utility + gradient * half], color=PALETTE["gold"],
              linewidth=2.2, linestyle="dashed")
    left.plot([phi], [utility], "o", color=PALETTE["terracotta"], markersize=9)
    label_point(left, phi, utility, f"utility {fmt(utility, 3)}", color=PALETTE["terracotta"], dx=10, dy=-12,
                ha="left", va="top").set_bbox(BOX)
    label_point(left, 5.8, DIRECT_SUCCESS, "always answer directly", color=PALETTE["grey"], dx=0, dy=-4, ha="right", va="top")
    label_point(left, 5.8, net, "always retrieve", color=PALETTE["grey"], dx=0, dy=4, ha="right", va="bottom")
    left.set_xlim(-6, 6)
    left.set_ylim(DIRECT_SUCCESS - 0.05, 0.88)
    left.set_xlabel("Policy parameter phi")
    left.set_ylabel("Expected utility J (success minus cost)")
    left.set_title("Utility and its slope (dashed)", fontsize=11.5)
    right.plot(zs, gain * ps * (1 - ps), color=PALETTE["navy"])
    right.plot([phi], [gradient], "o", color=PALETTE["terracotta"], markersize=9)
    if phi < 0:
        label_point(right, phi, gradient, f"slope {fmt(gradient, 4)}", color=PALETTE["terracotta"], dx=-10, dy=12,
                    ha="right").set_bbox(BOX)
    else:
        label_point(right, phi, gradient, f"slope\n{fmt(gradient, 4)}", color=PALETTE["terracotta"], dx=8, dy=8,
                    ha="left").set_bbox(BOX)
    right.set_xlim(-6, 6)
    right.set_ylim(0, 0.068)
    right.set_xlabel("Policy parameter phi")
    right.set_ylabel("Gradient of J with respect to phi")
    right.set_title("The gradient is biggest at p = 0.5", fontsize=11.5)
    metrics = {
        "Retrieve probability p": fmt(p, 4),
        "Expected utility J": fmt(utility, 4),
        "Gradient dJ/dphi": fmt(gradient, 4),
        "Gradient by Equation (13.2) sum": fmt(identity, 4),
    }
    interpretation = (
        f"p = 1 / (1 + e^({fmt(-phi, 1)})) = {fmt(p, 4)}. Retrieving is worth {fmt(q, 2)} - 0.05 = {fmt(net, 2)}, so J = 0.55 + {fmt(gain, 2)} x {fmt(p, 4)} = {fmt(utility, 4)}. "
        f"Gradient = {fmt(gain, 2)} x {fmt(p, 4)} x (1 - {fmt(p, 4)}) = {fmt(gradient, 4)}. "
        f"The same number comes from Equation (13.2) with one step: "
        f"{fmt(p, 4)} x {fmt(1 - p, 4)} x {fmt(net, 2)} - {fmt(1 - p, 4)} x {fmt(p, 4)} x 0.55 = {fmt(identity, 4)}. "
        "The slope shrinks toward zero at both ends because p(1 - p) does: a policy that is nearly sure gets almost no signal about the alternative."
    )
    return fig, metrics, interpretation


# Demonstration 3

REWARDS = {"misaligned": [1.0, 2.0], "aligned": [2.0, 1.0]}
SUCCESS = [0.9, 0.2]
LAB_BASE = {"success_probabilities": SUCCESS, "terminal_potentials": [0, 0], "seeds": [3, 11],
            "learning_rate": 0.08, "discount": 1, "evaluation_runs": 200}


def lab_run(ranking, episodes):
    data = dict(LAB_BASE, rewards=REWARDS[ranking], episodes=int(episodes))
    return evaluate(data)


def verifier_picture(ranking="misaligned", episodes=120):
    out = lab_run(ranking, episodes)
    rewards = REWARDS[ranking]
    runs = out["tables"]
    start_reward = 0.5 * rewards[0] + 0.5 * rewards[1]
    start_success = 0.5 * SUCCESS[0] + 0.5 * SUCCESS[1]
    fig, (left, right) = new_figure(ncols=2, height=4.2)
    styles = [("solid", "o"), ("dashed", "s")]
    for curve, (ls, mk), run in zip(out["series"], styles, runs):
        left.plot(np.array(curve["x"]) + 1, curve["y"], color=PALETTE["navy"], linestyle=ls, linewidth=1.8)
    left.axhline(start_reward, color=PALETTE["grey"], linestyle="dotted", linewidth=1.4)
    left.set_xlim(1, int(episodes))
    low, high = min(rewards), max(rewards)
    left.set_ylim(low - 0.08, high + 0.35)
    label_point(left, int(episodes), start_reward, f"start {fmt(start_reward, 2)} (dotted)", color=PALETTE["grey"], dx=-4,
                dy=-6, ha="right", va="top").set_bbox(BOX)
    label_point(left, int(episodes), low - 0.04, "solid: seed 3, dashed: seed 11", color=PALETTE["navy"], dx=-4, dy=0,
                ha="right", va="bottom")
    left.set_xlabel("Training episode")
    left.set_ylabel("Expected verifier reward")
    left.set_title("What the learner is trained on", fontsize=11.5)
    labels = ["start", "seed 3", "seed 11"]
    values = [start_success] + [r["expected_external_success"] for r in runs]
    colors = [PALETTE["grey"], PALETTE["teal"], PALETTE["teal"]]
    for i, (v, c) in enumerate(zip(values, colors)):
        right.bar(i, v, 0.6, color=c, linewidth=0)
        right.text(i, v + 0.025, fmt(v, 3), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"],
                   zorder=5, bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.95})
    right.axhline(SUCCESS[0], color=PALETTE["olive"], linestyle="dashed", linewidth=1.3)
    right.axhline(SUCCESS[1], color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.3)
    label_point(right, 3.45, SUCCESS[0], "best action 0.9", color=PALETTE["olive"], dx=0, dy=4, ha="right").set_bbox(BOX)
    label_point(right, 3.45, SUCCESS[1], "worst action 0.2", color=PALETTE["terracotta"], dx=0, dy=-4, ha="right", va="top").set_bbox(BOX)
    right.set_xticks(range(3), labels)
    right.set_xlim(-0.5, 3.5)
    right.set_ylim(0, 1.12)
    right.set_xlabel("Policy")
    right.set_ylabel("Expected true task success")
    right.set_title(f"What the task actually gets after {int(episodes)} episodes", fontsize=11.5)
    right.grid(axis="x", alpha=0)
    r3, r11 = runs
    p0 = round(r3["policy"][0], 4)
    p1 = round(1 - p0, 4)
    reward_calc = p0 * rewards[0] + p1 * rewards[1]
    success_calc = p0 * SUCCESS[0] + p1 * SUCCESS[1]
    metrics = {
        "Start: verifier reward": fmt(start_reward, 2),
        "Start: true success": fmt(start_success, 3),
        "Seed 3: verifier reward": fmt(r3["expected_training_reward"], 3),
        "Seed 3: true success": fmt(r3["expected_external_success"], 3),
        "Seed 11: true success": fmt(r11["expected_external_success"], 3),
        "Seed 3: separate evaluation, 200 runs": fmt(r3["independent_evaluation_rate"], 3),
    }
    if ranking == "misaligned":
        verdict = ("The verifier pays most for the action with the lowest task success, so the learner moves toward it. "
                   "The reward curve climbs while the task result falls, and a plot of reward alone would call this progress.")
    else:
        verdict = ("Here the verifier and the task agree on the best action, so reward and task success rise together. "
                   "That agreement is a property of these constructed numbers, not something training can create.")
    interpretation = (
        f"Start: 0.5 x {fmt(rewards[0], 0)} + 0.5 x {fmt(rewards[1], 0)} = {fmt(start_reward, 2)} reward and "
        f"0.5 x 0.9 + 0.5 x 0.2 = {fmt(start_success, 2)} true success. After {int(episodes)} episodes seed 3 picks action 0 with "
        f"probability {fmt(p0, 4)}: reward = {fmt(p0, 4)} x {fmt(rewards[0], 0)} + {fmt(p1, 4)} x {fmt(rewards[1], 0)} = {fmt(reward_calc, 4)}; "
        f"true success = {fmt(p0, 4)} x 0.9 + {fmt(p1, 4)} x 0.2 = {fmt(success_calc, 4)}. {verdict}"
    )
    return fig, metrics, interpretation


# Demonstration 4

DIRECT_RETURN = DIRECT_SUCCESS                      # direct answer, expected true completion
RETRIEVE_RETURN = RETRIEVE_SUCCESS - RETRIEVAL_COST  # 0.75, book value


def shaping_picture(evidence_potential=0.4, direct_end_potential=0.0):
    e = float(evidence_potential)
    d = float(direct_end_potential)
    gamma = 1.0
    rewards = [-RETRIEVAL_COST, 1.0]
    pots = [0.0, e, 0.0]  # start, evidence state, terminal
    shaped = [rewards[t] + gamma * pots[t + 1] - pots[t] for t in range(2)]
    g0 = sum(rewards)
    g0_shaped = sum(shaped)
    g0_formula = g0 - pots[0] + gamma ** 2 * pots[2]
    direct_shaped = DIRECT_RETURN - 0.0 + gamma * d
    retrieve_shaped = RETRIEVE_RETURN - 0.0 + gamma ** 2 * 0.0
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    x = np.arange(2)
    w = 0.36
    left.bar(x - w / 2, rewards, w, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.1, label="original r_t")
    left.bar(x + w / 2, shaped, w, color=PALETTE["navy"], label="shaped r'_t")
    for xi, r, s in zip(x, rewards, shaped):
        left.text(xi - w / 2, max(r, 0) + 0.025, fmt(r, 2), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        left.text(xi + w / 2, max(s, 0) + 0.025, fmt(s, 2), ha="center", va="bottom", fontsize=10.5, color=PALETTE["navy"])
    left.set_xticks(x, ["t=0 retrieve", "t=1 release"])
    left.set_ylim(-0.12, 1.45)
    left.set_xlabel("Step on the retrieve route (release succeeds)")
    left.set_ylabel("Reward at step t")
    left.set_title(f"Evidence state potential {fmt(e, 1)}: sum stays {fmt(g0_shaped, 2)}", fontsize=11.5)
    left.legend(loc="upper left", fontsize=10.5, frameon=True)
    left.grid(axis="x", alpha=0)
    routes = ["Answer directly", "Retrieve then answer"]
    originals = [DIRECT_RETURN, RETRIEVE_RETURN]
    shapeds = [direct_shaped, retrieve_shaped]
    xr = np.arange(2)
    right.bar(xr - w / 2, originals, w, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.1, label="original G_0")
    right.bar(xr + w / 2, shapeds, w, color=PALETTE["teal"], label="shaped G'_0")
    for xi, o, s in zip(xr, originals, shapeds):
        right.text(xi - w / 2, o + 0.02, fmt(o, 2), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        right.text(xi + w / 2, s + 0.02, fmt(s, 2), ha="center", va="bottom", fontsize=10.5, color=PALETTE["teal"])
    right.set_xticks(xr, routes)
    right.set_ylim(0, 1.3)
    right.set_xlabel("Route")
    right.set_ylabel("Expected return from the start state")
    right.set_title(f"Direct route end potential {fmt(d, 1)}", fontsize=11.5)
    right.legend(loc="upper left", fontsize=10.5, frameon=True, ncol=2)
    right.grid(axis="x", alpha=0)
    if is_tie(direct_shaped, retrieve_shaped):
        ranking = "tie"
        verdict = (f"The shaped returns tie at {fmt(direct_shaped, 2)}. The original ranking (retrieve first) is lost, and "
                   "Equation (13.4) does not say which route the learner should prefer.")
    elif direct_shaped > retrieve_shaped:
        ranking = "Answer directly"
        verdict = ("The direct route now ranks first. The end potential belongs to one route only, so it is not a common "
                   "offset and the ranking has changed.")
    else:
        ranking = "Retrieve then answer"
        if d == 0.0:
            verdict = ("Retrieving ranks first. The direct route's end potential is 0, so the shaped returns equal the "
                       "original ones and nothing has changed.")
        else:
            verdict = ("Retrieving still ranks first. A small end potential on one route can leave the ranking alone, but "
                       "the returns are no longer the true ones.")
    metrics = {
        "Retrieve route G_0 (success case)": fmt(g0, 2),
        "Retrieve route G'_0 (success case)": fmt(g0_shaped, 2),
        "Direct route G'_0": fmt(direct_shaped, 2),
        "Retrieve route G'_0": fmt(retrieve_shaped, 2),
        "Ranked first after shaping": ranking,
    }
    interpretation = (
        f"r'_0 = {snum(rewards[0])} + 1 x {fmt(e, 1)} - 0 = {fmt(shaped[0], 2)}. "
        f"r'_1 = {fmt(rewards[1], 0)} + 1 x 0 - {fmt(e, 1)} = {fmt(shaped[1], 2)}. "
        f"Their sum is {fmt(g0_shaped, 2)}, which equals G_0 - 0 + 1 x 0 = {fmt(g0_formula, 2)} from Equation (13.4): "
        f"the {fmt(e, 1)} added at t=0 is taken back at t=1. Routes: direct = 0.55 + 1 x {fmt(d, 1)} = {fmt(direct_shaped, 2)}, "
        f"retrieve = 0.80 - 0.05 + 0 = {fmt(retrieve_shaped, 2)}. {verdict}"
    )
    return fig, metrics, interpretation


CHAPTER = {
    "number": 13,
    "title": "Learning to Choose: Training an Agent from Trajectories",
    "subtitle": "Learning changes the chooser itself, and a reward that rises is not the same as a task that improves.",
    "summary": (
        "These four demonstrations follow the chapter's retrieve-or-answer agent. They show what a trajectory records, how "
        "a policy-gradient update moves the chance of retrieving, how a verifier that is wrong about success can steer "
        "training, and what reward shaping does and does not change. Every number is a constructed teaching value."
    ),
    "demos": [
        {
            "id": "C13-D01",
            "title": "What one episode records: return-to-go",
            "question": "How does the discount factor change the return that a step is credited with?",
            "equations": [EQ_TRAJECTORY],
            "symbols": (
                "tau is one whole episode: observations o, actions a and rewards r, ending at the terminal observation o_T. "
                "r_t is the reward at step t. G_t is the return-to-go: the discounted sum of rewards from step t to the end. "
                "gamma is the discount, a number from 0 to 1 that shrinks later rewards. T is the number of reward steps."
            ),
            "prediction": "In the exercise stream (rewards 1 then 2), what is G_0 when gamma is 0.5? Then check it against the picture.",
            "explanation": (
                "Equation (13.1) lists what an episode contains and then defines G_t by adding the rewards from step t on, "
                "each multiplied by gamma raised to the number of steps since t. A late reward therefore counts less in an early "
                "step's return when gamma is below 1, and the last step's return is always just its own reward."
            ),
            "application": (
                "When a training log reports one number per episode, ask which return it is. G_0 under different discounts, "
                "a plain sum of rewards and a later return G_t give different numbers for the same episode, so a comparison needs the same definition on both sides."
            ),
            "assumptions": (
                "A short episode with fixed rewards and no randomness. Real trajectories include observations that the policy did "
                "not choose, and only the policy's own actions receive credit; this picture shows rewards only. The release task "
                "values are constructed for this reader."
            ),
            "check": "For rewards 1 then 2 with gamma = 0.9, what return is credited to the first action?",
            "answer": "G_0 = 1 + 0.9 x 2 = 2.8. The second step's return stays G_1 = 2.",
            "provenance": "Constructed example: the chapter's own exercise (rewards 1 and 2) and a three-step release task with the book's retrieval cost 0.05, defined for this reader.",
            "source_section": "What one training episode contains",
            "source_anchor": "what-one-training-episode-contains",
            "controls": [
                {"key": "stream", "label": "Reward stream", "values": ["release", "exercise"], "default": "release",
                 "value_labels": ["Release task: -0.05, 0, 1", "Chapter exercise: 1, 2"]},
                {"key": "gamma", "label": "Discount gamma", "values": [1.0, 0.9, 0.5], "default": 1.0},
            ],
            "function": "return_picture",
        },
        {
            "id": "C13-D02",
            "title": "Retrieve or answer: the gradient of one choice",
            "question": "If a policy retrieves with probability p = sigma(phi), how steeply does expected utility change as phi moves?",
            "equations": [EQ_GRADIENT],
            "symbols": (
                "phi is the trainable policy parameter and p = sigma(phi) the probability of retrieving before answering. J is the "
                "expected utility: 0.55 for answering directly and the retrieve route's true success minus the retrieval cost 0.05 "
                "for retrieving first, mixed by p. sigma is the logistic function, sigma(z) = 1 / (1 + e^(-z)), which turns any phi into a "
                "probability. The gradient is the slope of J as phi changes. In Equation (13.2), pi_phi(a_t | o_t) is the probability "
                "the policy gives action a_t after observation o_t, tau is an episode generated by following that policy, E is the "
                "average over such episodes, G_t is the return of the sampled action, and the log-probability term is its score. "
                "Here T = 1 and gamma^t = 1, because there is one decision."
            ),
            "prediction": "At which phi is the slope largest, and what is the slope there when retrieving succeeds with probability 0.80 and costs 0.05?",
            "explanation": (
                "Expected utility is 0.55 plus the gain from retrieving times p; the gain is the retrieve route's success minus the cost 0.05, "
                "minus 0.55 (at the default 0.80 it is 0.75 - 0.55 = 0.20). Because p = sigma(phi) flattens near 0 and 1, "
                "the slope equals the gain times p(1 - p), which peaks at p = 0.5. Equation (13.2) gives the same number: it weights each "
                "action's score by its return and averages over the two actions."
            ),
            "application": (
                "With a logistic parameterization, a policy that is already nearly sure of its choice receives almost no learning signal, "
                "even if the other choice is better. A training log should show action frequencies, not only an average reward."
            ),
            "assumptions": (
                "One decision with two actions, a fixed environment and exact expectations. Equation (13.2) gives a direction in "
                "expectation; a single sampled update can point the wrong way. The success values 0.55 and 0.80 are the book's constructed "
                "numbers, and 0.70 is a value defined for this reader."
            ),
            "check": "With retrieve success 0.70 (cost still 0.05) and p = 0.5, what is the gradient?",
            "answer": "Net value of retrieving = 0.70 - 0.05 = 0.65, gain = 0.65 - 0.55 = 0.10, so the slope is 0.10 x 0.5 x 0.5 = 0.025.",
            "provenance": "Constructed example: the chapter's retrieve-or-answer values 0.55 and 0.80, with the cost 0.05 and one changed retrieve value (0.70) defined for this reader.",
            "source_section": "Retrieve or answer",
            "source_anchor": "retrieve-or-answer",
            "controls": [
                {"key": "phi", "label": "Policy parameter phi", "values": [-2, 0, 1, 3], "default": 0},
                {"key": "retrieve_success", "label": "True success when retrieving", "values": [0.8, 0.7], "default": 0.8},
            ],
            "function": "retrieve_picture",
        },
        {
            "id": "C13-D03",
            "title": "A verifier can teach the wrong success",
            "question": "If the verifier rewards the action that the task does not need, does more training help or hurt the task?",
            "equations": [EQ_GRADIENT],
            "symbols": (
                "The policy chooses between action 0 and action 1. Each action has a verifier reward (what training sees) and "
                "a true-success probability (what the task needs). Action 0 succeeds 90 percent of the time in this constructed case "
                "and action 1 succeeds 20 percent; these numbers and the rewards 1 and 2 come from the laboratory's default case, "
                "and are separate from the chapter's noisy-verifier example (accepts true answers with probability 0.9 and wrong "
                "answers with 0.3). Training makes a sampled update in the form of Equation (13.2), with a baseline equal to the "
                "policy's expected reward and softmax logits, using the verifier reward, so only reward drives the change. In that "
                "equation pi_phi(a_t | o_t) is the policy's probability of action a_t, tau an episode, E an average over episodes, "
                "G_t the return, and gamma^t = 1 because there is one decision (T = 1). Two random seeds, 3 and 11, show the spread."
            ),
            "prediction": "With rewards 1 and 2 (the verifier prefers action 1), will 400 episodes leave true success above or below the starting 0.55?",
            "explanation": (
                "The update raises the probability of whichever action earns more reward than average. If that action has "
                "the lower success, the policy drifts toward failure while its reward curve rises. Swapping the two rewards "
                "makes the same update raise success instead."
            ),
            "application": (
                "Before calling a rising reward curve an improvement, compute what the policy would score under a check that the reward "
                "model does not share, such as an outside audit of the outcome."
            ),
            "assumptions": (
                "One-step choice between two actions, a fixed learning rate of 0.08, and two seeds. Real verifiers are noisy rather "
                "than a fixed reward, and real tasks have many steps. The seeds show that this run is a sample; they are not an estimate of how "
                "often it happens elsewhere."
            ),
            "check": "With rewards 1 and 2, if training ended at probability 0.10 for action 0, what is the true success?",
            "answer": "0.10 x 0.9 + 0.90 x 0.2 = 0.09 + 0.18 = 0.27, well below the starting 0.55.",
            "provenance": "Constructed example: the laboratory's default training case (rewards 1 and 2, success 0.9 and 0.2, learning rate 0.08, seeds 3 and 11), with the training length varied.",
            "source_section": "A verifier can teach the wrong success",
            "source_anchor": "a-verifier-can-teach-the-wrong-success",
            "controls": [
                {"key": "ranking", "label": "Which action the verifier prefers", "values": ["misaligned", "aligned"],
                 "default": "misaligned",
                 "value_labels": ["Action 1, low success (rewards 1, 2)", "Action 0, high success (rewards 2, 1)"]},
                {"key": "episodes", "label": "Training episodes", "values": [10, 40, 120, 400], "default": 120},
            ],
            "function": "verifier_picture",
        },
        {
            "id": "C13-D04",
            "title": "Reward shaping: what cancels and what does not",
            "question": "Which parts of a shaped return survive the cancellation, and when can shaping change which route ranks first?",
            "equations": [EQ_SHAPED, EQ_TELESCOPE],
            "symbols": (
                "r_t is the original reward and r'_t the shaped reward. Pot(x) is a potential assigned to state x: here 0 at the "
                "start and at the end of the retrieve route, a chosen value at the evidence state, and a chosen end value on the direct route. "
                "gamma is 1 (no discount). G_0 and G'_0 are "
                "the original and shaped returns of the whole episode, and T the number of steps. Both routes start at x_0 "
                "with potential 0."
            ),
            "prediction": "Raise the evidence-state potential from 0.4 to 1.0. Does the sum of the shaped rewards change?",
            "explanation": (
                "Each shaped reward adds the next state's potential and subtracts the current one, so a potential added when "
                "entering a state is subtracted when leaving it. Only the start and end potentials remain, as Equation (13.4) says. "
                "A potential at an end state that only one route reaches does not cancel across routes, and can change the ranking."
            ),
            "application": (
                "If a team adds a bonus for visiting a useful intermediate state, check where the potential ends up. A bonus that "
                "vanishes at the end is bookkeeping; a bonus that remains at some end states is a new objective."
            ),
            "assumptions": (
                "No discount, a fixed starting state and exact expected returns. The potential is a function of state, as "
                "Equation (13.3) requires. A scorer that emits arbitrary positive scores does not take this form and gets no guarantee. "
                "The values 0.55, 0.80, 0.05 and 0.4 are the book's constructed numbers; the other potentials are defined for this reader."
            ),
            "check": "If the direct route's end state had potential 0.1, which route would rank first, and by how much?",
            "answer": "Direct = 0.55 + 0.1 = 0.65, retrieve = 0.80 - 0.05 = 0.75. Retrieving still ranks first, by 0.10.",
            "provenance": "Constructed example: the chapter's release construction (potential 0 at start and end, 0.4 after retrieval) with the book's 0.55, 0.80 and 0.05; other potentials defined for this reader.",
            "source_section": "When the reward arrives in pieces",
            "source_anchor": "when-the-reward-arrives-in-pieces",
            "controls": [
                {"key": "evidence_potential", "label": "Potential of the evidence state", "values": [0.4, 1.0], "default": 0.4},
                {"key": "direct_end_potential", "label": "Potential at the end of the direct route", "values": [0.0, 0.2, 0.5], "default": 0.0},
            ],
            "function": "shaping_picture",
        },
    ],
}

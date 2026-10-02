"""Chapter 18 reader: When an Action Has Coordinates.

Four demonstrations built on Equations (18.1) to (18.3). Demonstration 3 calls
the laboratory's own interface calculation
(math_ai_agents.chapters.ch18.evaluate) for the freshness probability, so the
reader, the notebook and the chapter skill agree. Demonstrations 1, 2 and 4
compute the chapter's small finite examples directly. Every number is a
constructed teaching value; the book's own values are named where they are used.
"""
import math

import numpy as np
from matplotlib.patches import Rectangle

from math_ai_agents.chapters.ch18 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure

EQ_TRANSITION = (
    r"P_{\mathrm{ui}}(x'\mid x,a)=\sum_{\tilde a\in\operatorname{Act}_{\mathrm{ui}}}"
    r"\operatorname{Exec}_{\mathrm{ui}}(\tilde a\mid x,a)P(x'\mid x,\tilde a)"
)
EQ_ROBUST = r"\mathcal A_{\mathrm{rob}}(\mathbf b)=\bigcap_{x:\,\mathbf b(x)>0}\mathcal A_{\mathrm{auth}}(x)"
EQ_FRESH = r"\operatorname{Fresh}(\Delta)=\exp(-\lambda_{\mathrm{ui}}\Delta)"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


# Demonstration 1: the interface in the transition law

def transition_picture(belief_layout1=0.8, permission_check="off"):
    b1 = float(belief_layout1)
    b2 = 1.0 - b1
    on = permission_check == "on"
    # Exec(realized operation | layout, saved click): deterministic in each layout (chapter, same section).
    exec_layout1 = {"v2": 1.0, "v3": 0.0, "denied": 0.0}
    exec_layout2 = {"v2": 0.0, "v3": 0.0 if on else 1.0, "denied": 1.0 if on else 0.0}
    # World law P(x' | x, realized operation): each operation leads to one next state.
    predicted = {k: b1 * exec_layout1[k] + b2 * exec_layout2[k] for k in exec_layout1}
    names = {"v2": "Release v2 (authorized)", "v3": "Release v3 (not authorized)", "denied": "Denied, no release"}
    colors = {"v2": PALETTE["teal"], "v3": PALETTE["terracotta"], "denied": PALETTE["navy"]}
    hatches = {"v2": "", "v3": "///", "denied": "\\\\\\"}
    fig, ax = new_figure(height=3.9)
    order = ["v2", "v3", "denied"]
    y = np.arange(3)[::-1]
    for yi, key in zip(y, order):
        ax.barh(yi, predicted[key], height=0.56, color=colors[key], hatch=hatches[key], edgecolor="white", linewidth=0)
        ax.text(predicted[key] + 0.02, yi, fmt(predicted[key], 2), va="center", fontsize=11, color=PALETTE["ink"])
    ax.set_yticks(y, [names[k] for k in order])
    ax.set_xlim(0, 1.18)
    ax.set_xlabel("Predicted probability of each outcome (constructed model)")
    ax.set_ylabel("What the saved click does")
    ax.grid(axis="y", alpha=0)
    ax.set_title(f"Belief {fmt(b1, 2)} / {fmt(b2, 2)} in the two layouts, permission check {'on' if on else 'off'}", fontsize=11.5)
    metrics = {
        "Release v2 (authorized completion)": fmt(predicted["v2"], 2),
        "Release v3 (prohibited release)": fmt(predicted["v3"], 2),
        "Denied, no release": fmt(predicted["denied"], 2),
        "Total": fmt(sum(predicted.values()), 2),
    }
    e2 = exec_layout2
    interpretation = (
        f"Layout 1 (v2 on top) has belief {fmt(b1, 2)}; layout 2 (rows swapped) has {fmt(b2, 2)}. "
        f"P(release v2) = {fmt(b1, 2)} x 1 + {fmt(b2, 2)} x 0 = {fmt(predicted['v2'], 2)}. "
        f"P(release v3) = {fmt(b1, 2)} x 0 + {fmt(b2, 2)} x {fmt(e2['v3'], 0)} = {fmt(predicted['v3'], 2)}. "
        f"P(denied) = {fmt(b1, 2)} x 0 + {fmt(b2, 2)} x {fmt(e2['denied'], 0)} = {fmt(predicted['denied'], 2)}. "
        f"The three add to {fmt(sum(predicted.values()), 2)}, as a normalized transition law must. "
        + ("The permission check turns the wrong-layout branch from a prohibited release into a denial; the "
           "controller's belief about the screen did not change, only the enforcement did."
           if on else
           "With no check, the wrong-layout branch becomes a prohibited release, with probability equal to the belief in that layout.")
    )
    return fig, metrics, interpretation


# Demonstration 2: support-wide authorization

COMMANDS = [
    ("Click the saved point", (True, False)),
    ("Request release of v2", (True, True)),
    ("Read metadata", (True, True)),
    ("Take a fresh screenshot", (True, True)),
    ("Abstain", (True, True)),
]


def robust_set_picture(belief_layout2=0.01):
    b2 = float(belief_layout2)
    b1 = 1.0 - b2
    beliefs = (b1, b2)
    counted = [b > 0 for b in beliefs]
    survives = [all(auth[i] for i in range(2) if counted[i]) for _, auth in COMMANDS]
    n_survive = sum(survives)
    fig, ax = new_figure(height=4.3)
    n = len(COMMANDS)
    for r, (name, auth) in enumerate(COMMANDS):
        for c in range(2):
            if not counted[c]:
                ax.add_patch(Rectangle((c, r), 1, 1, facecolor="#eef1f2", edgecolor="white", linewidth=2))
                ax.text(c + 0.5, r + 0.5, "not counted", ha="center", va="center", fontsize=10.5, color=PALETTE["grey"])
            elif auth[c]:
                ax.add_patch(Rectangle((c, r), 1, 1, facecolor="#cfe6e6", edgecolor="white", linewidth=2))
                ax.text(c + 0.5, r + 0.5, "authorized", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"])
            else:
                ax.add_patch(Rectangle((c, r), 1, 1, facecolor="#f0d6cf", edgecolor="white", linewidth=2, hatch="///"))
                ax.text(c + 0.5, r + 0.5, "not authorized", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"],
                        bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.9})
        ok = survives[r]
        ax.add_patch(Rectangle((2, r), 1, 1, facecolor="#cfe6e6" if ok else "#f0d6cf", edgecolor="white", linewidth=2,
                               hatch="" if ok else "///"))
        ax.text(2.5, r + 0.5, "survives" if ok else "removed", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"],
                bbox=None if ok else {"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.9})
    ax.set_xlim(0, 3)
    ax.set_ylim(n, 0)
    ax.set_xticks([0.5, 1.5, 2.5], [f"Layout 1\nbelief {fmt(b1, 2)}", f"Layout 2\nbelief {fmt(b2, 2)}", "Kept by the\nintersection"])
    ax.set_yticks(np.arange(n) + 0.5, [name for name, _ in COMMANDS])
    ax.set_xlabel("State considered possible, with its belief weight")
    ax.set_ylabel("Command")
    ax.grid(False)
    ax.tick_params(length=0)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    click_state = "survives" if survives[0] else "is removed"
    counted_names = [n_ for n_, flag in zip(("layout 1", "layout 2"), counted) if flag]
    removed = n - n_survive
    metrics = {
        "Belief in layout 1": fmt(b1, 2),
        "Belief in layout 2": fmt(b2, 2),
        "Layouts counted": " and ".join(counted_names),
        "Commands kept": f"{n_survive} of {n}",
        "Saved-point click": "kept" if survives[0] else "removed",
    }
    if all(counted):
        why = ("Both beliefs are above zero, so both layouts count, whatever their size. "
               "The click reaches an unapproved record in layout 2, so it is not authorized throughout the support.")
    elif counted[0]:
        why = ("Layout 2 has zero belief and is left out of the intersection, so only layout 1 constrains the set. "
               "That is safe only if the true layout really is layout 1.")
    else:
        why = ("Only layout 2 has positive belief, so the click, which reaches the unapproved record there, is not authorized. "
               "The other four commands stay authorized in layout 2.")
    interpretation = (
        f"Beliefs add to {fmt(b1, 2)} + {fmt(b2, 2)} = {fmt(b1 + b2, 2)}. {why} "
        f"Commands removed = {n} - {n_survive} = {removed}, so the saved-point click {click_state} and "
        f"{n_survive} of {n} commands remain. The request for v2 survives in either layout only because the service "
        "checks identity and approval at commit; belief alone never authorizes anything."
    )
    return fig, metrics, interpretation


# Demonstration 3: freshness

REFERENCE_INPUT = {
    "observation_age": 1, "max_age": 2, "observed_version": "layout-1", "current_version": "layout-2",
    "current_permission": True, "effect_confirmed": True, "coordinate_target": "delete",
    "semantic_target": "release", "wanted_target": "release",
}


def lab_freshness(rate, delay):
    """Fresh(delay) as computed by the laboratory's interface calculation."""
    data = dict(REFERENCE_INPUT, change_rate=float(rate), delays=[float(delay)])
    return evaluate(data)["metrics"]["freshness_by_delay"][0]["freshness_probability"]


def freshness_picture(rate=0.02, delay=30):
    rate, delay = float(rate), float(delay)
    fresh = lab_freshness(rate, delay)
    if not math.isclose(fresh, math.exp(-rate * delay), rel_tol=1e-12):
        raise AssertionError("laboratory freshness disagrees with exp(-rate x delay)")
    product = rate * delay
    stale = 1 - fresh
    half_life = math.log(2) / rate
    t = np.linspace(0, 82, 165)
    fig, ax = new_figure(height=4.2)
    ax.plot(t, np.exp(-rate * t), color=PALETTE["teal"], linewidth=2)
    marks = [5, 15, 30, 60]
    ax.plot(marks, [math.exp(-rate * m) for m in marks], "o", markerfacecolor="white", markeredgecolor=PALETTE["teal"], markersize=7)
    ax.plot([delay], [fresh], "o", color=PALETTE["terracotta"], markersize=10)
    ax.vlines(delay, 0, fresh, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.2)
    ax.hlines(fresh, 0, delay, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.2)
    label_point(ax, delay, fresh, f"Fresh = {fmt(fresh, 4)}", color=PALETTE["terracotta"], dx=10, dy=10, ha="left")
    ax.text(0.98, 0.95, f"Fresh = exp(-{fmt(rate, 2)} x delay)", transform=ax.transAxes, ha="right", va="top",
            fontsize=11, color=PALETTE["ink"])
    ax.set_xlim(0, 82)
    ax.set_ylim(0, 1.05)
    ax.set_xlabel("Delay between observing and acting (seconds)")
    ax.set_ylabel("Chance no invalidating change has occurred")
    ax.set_title(f"Constant-rate model, {fmt(rate, 2)} invalidating changes per second", fontsize=11.5)
    metrics = {
        "Rate": f"{fmt(rate, 2)} per second",
        "Delay": f"{fmt(delay, 0)} seconds",
        "Rate x delay": fmt(product, 2),
        "Chance still fresh": fmt(fresh, 4),
        "Chance of an invalidating change": fmt(stale, 4),
        "Delay at which freshness is one half": f"{fmt(half_life, 1)} seconds",
    }
    interpretation = (
        f"Rate x delay = {fmt(rate, 2)} x {fmt(delay, 0)} = {fmt(product, 2)}, a pure number with no unit left. "
        f"Fresh = exp(-{fmt(product, 2)}) = {fmt(fresh, 4)}, so the chance of at least one invalidating change is "
        f"1 - {fmt(fresh, 4)} = {fmt(stale, 4)}. Freshness reaches one half when rate x delay = ln 2 = 0.6931, "
        f"that is at 0.6931 / {fmt(rate, 2)} = {fmt(half_life, 1)} seconds. The hollow markers sit at delays of 5, 15, 30 and 60 seconds. "
        "The curve follows from the chosen change model; it says nothing about how often any real interface changes."
    )
    return fig, metrics, interpretation


# Demonstration 4: the price of another look

def another_look_picture(wrong_loss=40, wrong_chance=0.1):
    loss, p = float(wrong_loss), float(wrong_chance)
    cost = 2.0  # the chapter's cost of one more observation (units)
    now = p * loss
    gain = now - cost
    p_star = cost / loss
    if math.isclose(now, cost, abs_tol=1e-9):
        decision = "tie"
        verdict = ("The two options cost the same, so the comparison does not choose. Other considerations, such as a "
                   "deadline or the cost of a denial, have to break the tie.")
    elif gain > 0:
        decision = "Observe first"
        verdict = f"Observing first removes an expected loss of {fmt(now, 2)} for a cost of {fmt(cost, 1)}, so it pays."
    else:
        decision = "Click now"
        verdict = f"Clicking now risks an expected loss of only {fmt(now, 2)}, below the {fmt(cost, 1)} cost of looking, so another look does not pay."
    fig, (left, right) = new_figure(ncols=2, height=4.2)
    top = max(now, cost, 1.0) * 1.3
    left.bar([0], [now], width=0.55, color="white", edgecolor=PALETTE["terracotta"], hatch="///", linewidth=1.4)
    left.bar([1], [cost], width=0.55, color=PALETTE["teal"])
    left.text(0, now + top * 0.03, fmt(now, 2), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.text(1, cost + top * 0.03, fmt(cost, 2), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.set_xticks([0, 1], ["Click now", "Observe first"])
    left.set_xlim(-0.6, 1.6)
    left.set_ylim(0, top)
    left.set_xlabel("Option (hatched bar is expected loss)")
    left.set_ylabel("Expected cost (utility units)")
    left.set_title("Expected cost of each option", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    xmax = min(1.0, max(p, p_star) * 1.35 + 0.02)
    q = np.linspace(0, xmax, 101)
    right.plot(q, q * loss, color=PALETTE["terracotta"], linewidth=2)
    right.axhline(cost, color=PALETTE["teal"], linewidth=2)
    right.plot([p], [now], "o", color=PALETTE["terracotta"], markersize=9)
    right.plot([p_star], [cost], "s", color=PALETTE["ink"], markersize=7)
    label_point(right, xmax, cost, "cost of looking", color=PALETTE["teal"], dx=-4, dy=-6, ha="right", va="top")
    # name the rising line just above its right end, where the line lies below the text
    label_point(right, xmax, xmax * loss, "expected loss of clicking now", color=PALETTE["terracotta"], dx=-2, dy=5,
                ha="right", va="bottom")
    # the line is above the cost line to the right of break-even and below it to the left, so labels sit above-left or below-right
    if p_star >= 0.25 * xmax:
        side = {"dx": -6, "ha": "right", "dy": 8, "va": "bottom"}
    else:
        side = {"dx": 6, "ha": "left", "dy": -9, "va": "top"}
    if math.isclose(now, cost, abs_tol=1e-9):
        label_point(right, p, now, f"tie at {fmt(p, 2)}", color=PALETTE["ink"], **side).set_bbox(BOX)
    else:
        label_point(right, p_star, cost, f"break-even {fmt(p_star, 3)}", color=PALETTE["ink"], **side).set_bbox(BOX)
        top_r = max(xmax * loss, cost) * 1.22
        if now < 0.12 * top_r:
            # a point near the floor has no room below it: call it out from the clear area under the cost line
            right.annotate(f"chosen {fmt(p, 2)}", (p, now), xytext=(0.5 * xmax, 0.2 * top_r), textcoords="data",
                           ha="left", va="center", color=PALETTE["terracotta"], fontsize=10.5, bbox=BOX,
                           arrowprops={"arrowstyle": "->", "color": PALETTE["terracotta"], "linewidth": 1.2})
        else:
            label_point(right, p, now, f"chosen {fmt(p, 2)}", color=PALETTE["terracotta"], dx=8, dy=-10, va="top").set_bbox(BOX)
    right.set_xlim(0, xmax)
    right.set_ylim(0, max(xmax * loss, cost) * 1.22)
    right.set_xlabel("Chance the saved point is wrong")
    right.set_ylabel("Expected cost (utility units)")
    right.set_title(f"Wrong-target loss {fmt(loss, 0)}", fontsize=11.5)
    metrics = {
        "Expected loss of clicking now": fmt(now, 2),
        "Cost of one more look": fmt(cost, 2),
        "Net advantage of looking": fmt(gain, 2),
        "Break-even chance of a wrong target": fmt(p_star, 3),
        "Better option": decision,
    }
    interpretation = (
        f"Expected loss of clicking now = {fmt(p, 2)} x {fmt(loss, 0)} = {fmt(now, 2)}. Looking first costs {fmt(cost, 1)} "
        f"and removes that loss, so its net advantage is {fmt(now, 2)} - {fmt(cost, 1)} = {fmt(gain, 2)}. "
        f"Break-even chance = {fmt(cost, 1)} / {fmt(loss, 0)} = {fmt(p_star, 3)}. {verdict}"
    )
    return fig, metrics, interpretation


CHAPTER = {
    "number": 18,
    "title": "When an Action Has Coordinates",
    "subtitle": "A click names a position, not an object. What it does depends on the screen that is current when it arrives.",
    "summary": (
        "These four demonstrations follow the chapter's release console, where the rows can swap places after the controller "
        "has looked. They show how the interface enters the transition law, which commands survive when the screen is "
        "uncertain, how fast a screenshot goes stale, and when another look is worth its cost."
    ),
    "demos": [
        {
            "id": "C18-D01",
            "title": "One click, two layouts",
            "question": "If the controller is unsure which layout is current, what does its saved click do, and what does a permission check change?",
            "equations": [EQ_TRANSITION],
            "symbols": (
                "x is the current state (here, which layout is on screen), a is the proposed command (the saved click), and a-tilde "
                "is the operation the interface actually realizes: release v2, release v3 or a denial. Exec(a-tilde | x, a) is the "
                "chance the interface realizes a-tilde, and P(x' | x, a-tilde) is the world's law for the next state x'. "
                "Act with subscript ui is the set of operations the interface can realize, and Exec with subscript ui is the "
                "interface's own chance of realizing one. The belief is the controller's probability that layout 1 is current."
            ),
            "prediction": "With belief 0.6 in layout 1, what is the chance of a prohibited release with no permission check, and with one?",
            "explanation": (
                "In layout 1 the saved click realizes release v2 for certain; in layout 2 it realizes release v3 for certain, or a "
                "denial if the permission check is on. Equation (18.1) multiplies each realized operation by its world effect and "
                "adds, and the belief averages over the two layouts. Uncertainty sits in which layout is current, not in the click."
            ),
            "application": (
                "Before trusting a coordinate action, write down what it realizes under every layout you consider possible, "
                "and which of those realizations a current check would block."
            ),
            "assumptions": (
                "Two layouts, each with a deterministic realized operation that leads to one next state, and complete mediation when the check is on. "
                "The beliefs are probabilities in a constructed model, not measured accuracies of any visual model. If an "
                "unmediated route to the service exists, the check column does not apply."
            ),
            "check": "With belief 0.7 in layout 1, what is the chance of a prohibited release with no check, and with the check on?",
            "answer": "No check: 0.7 x 0 + 0.3 x 1 = 0.30. Check on: 0.7 x 0 + 0.3 x 0 = 0. Authorized completion stays 0.7 x 1 + 0.3 x 0 = 0.70 in both.",
            "provenance": "Constructed example: the chapter's two-layout console with its 0.8 and 0.2 beliefs; the 0.6 and 0.95 beliefs are defined for this reader.",
            "source_section": "The interface belongs in the transition law",
            "source_anchor": "the-interface-belongs-in-the-transition-law",
            "controls": [
                {"key": "belief_layout1", "label": "Belief that layout 1 (v2 on top) is current", "values": [0.6, 0.8, 0.95], "default": 0.8},
                {"key": "permission_check", "label": "Current permission check at the service", "values": ["off", "on"], "default": "off",
                 "value_labels": ["Off", "On"]},
            ],
            "function": "transition_picture",
        },
        {
            "id": "C18-D02",
            "title": "What survives when the screen is uncertain",
            "question": "Which commands stay authorized in every layout the controller still considers possible?",
            "equations": [EQ_ROBUST],
            "symbols": (
                "b(x) is the belief weight of state x, here layout 1 or layout 2. The set written A with subscript auth, at x, holds the "
                "commands whose protected effect is authorized in state x. The set written A with subscript rob, at b, is the "
                "intersection of those sets over every state with positive belief."
            ),
            "prediction": "Layout 2 has belief only 0.01. Does the saved-point click survive the intersection?",
            "explanation": (
                "A command is kept only if every state with positive weight authorizes it. Layout 2 does not authorize the saved-point "
                "click, so any positive weight on layout 2 removes it, while zero weight leaves layout 2 out of the intersection entirely. "
                "The weight itself never enters the result, only whether it is positive."
            ),
            "application": (
                "When a decision is removed by a state you think unlikely, the record shows which state removed it and which "
                "observation (a fresh screenshot, a metadata read) could narrow the support and restore it."
            ),
            "assumptions": (
                "The true layout must lie inside the counted support, and the authorization sets must be specified correctly; "
                "if either fails, the intersection guarantees nothing. The sets here are constructed, and the construction is "
                "conservative: it is not a substitute for the service's own current permission check."
            ),
            "check": "If layout 2 has belief 0.001, does the saved-point click survive? What if the belief is exactly 0?",
            "answer": "At 0.001 the weight is positive, so layout 2 counts and removes the click (4 of 5 commands remain). At 0 layout 2 is not counted, the click survives and 5 of 5 remain, but only if layout 1 is truly current.",
            "provenance": "Constructed example: the chapter's two-layout case, with authorization sets defined for this reader and belief weights chosen for illustration.",
            "source_section": "A belief over screens",
            "source_anchor": "a-belief-over-screens",
            "controls": [
                {"key": "belief_layout2", "label": "Belief that layout 2 (rows swapped) is current", "values": [0.0, 0.01, 0.5, 1.0], "default": 0.01},
            ],
            "function": "robust_set_picture",
        },
        {
            "id": "C18-D03",
            "title": "How fast a screenshot goes stale",
            "question": "If invalidating changes arrive at a steady rate, how likely is a saved coordinate to still be valid after a delay?",
            "equations": [EQ_FRESH],
            "symbols": (
                "Delta is the delay between observing and acting, in seconds. Lambda with subscript ui is the rate of invalidating "
                "interface changes, in changes per second. Their product is a pure number. Fresh(Delta) is the chance that no invalidating change "
                "occurred during the delay."
            ),
            "prediction": "At 0.02 changes per second, is the chance of still being fresh after 30 seconds above or below one half?",
            "explanation": (
                "If changes arrive at a constant rate, the chance of none in a delay falls as an exponential of rate times delay. "
                "Doubling the delay squares the freshness: at 0.02 per second, 15 seconds gives 0.7408 and 30 seconds gives 0.5488, "
                "which is 0.7408 squared. A higher rate steepens the fall in the same way."
            ),
            "application": (
                "Choose a maximum observation age by deciding what chance of an invalidating change you will accept, then "
                "refresh the observation or bind the command to a state version before that age is reached."
            ),
            "assumptions": (
                "Constant-rate, memoryless changes, and a clear definition of which changes invalidate the binding. Real interfaces "
                "can update periodically, in bursts, or in response to the agent's own actions, and a rate taken from quiet "
                "periods can mislead. The rates here are teaching inputs."
            ),
            "check": "At 0.05 invalidating changes per second and a 20 second delay, what is Fresh?",
            "answer": "Rate x delay = 0.05 x 20 = 1.0, so Fresh = exp(-1) = 0.3679. The chance of an invalidating change is 1 - 0.3679 = 0.6321.",
            "provenance": "Constructed example: the chapter's rate of 0.02 per second and delays of 5 and 30 seconds, computed with the laboratory's interface function; the 0.05 rate and the 60 second delay are defined for this reader.",
            "source_section": "How long a picture stays useful",
            "source_anchor": "how-long-a-picture-stays-useful",
            "controls": [
                {"key": "rate", "label": "Invalidating changes per second", "values": [0.02, 0.05], "default": 0.02},
                {"key": "delay", "label": "Delay before acting (seconds)", "values": [5, 15, 30, 60], "default": 30},
            ],
            "function": "freshness_picture",
        },
        {
            "id": "C18-D04",
            "title": "The price of another look",
            "question": "When does one more observation before the click earn its cost?",
            "equations": [EQ_TRANSITION],
            "symbols": (
                "The chance the saved point is wrong is the probability of the layout in which the click reaches the wrong "
                "record. The loss is what that outcome costs, in declared utility units. A second observation costs 2 units and "
                "is assumed to settle which layout is current. Equation (18.1) describes the possible outcomes of the click "
                "(its symbols are defined in Demonstration 1: a-tilde is a realized operation, Exec with subscript ui its chance, "
                "Act with subscript ui the set of realizable operations, x' the next state). This demonstration's own comparison "
                "is: expected loss of clicking now = chance x loss, and looking pays when chance x loss is more than 2."
            ),
            "prediction": "With a wrong-target loss of 3 (a denial) instead of 40, does the extra look still pay at a 0.1 chance of being wrong?",
            "explanation": (
                "Clicking now costs the chance of a wrong target times its loss. Looking first costs 2 and removes that loss. "
                "The look pays when chance x loss exceeds 2, which gives a break-even chance of 2 divided by the loss. "
                "Enforcement matters because it changes the loss, not the chance."
            ),
            "application": (
                "Do not buy information because uncertainty exists. Price the wrong-target branch under the interface you "
                "actually have, and look again only when that expected loss is larger than the cost of looking."
            ),
            "assumptions": (
                "The look is perfect, execution follows at once, and the loss lumps delay, retries and side effects into one number. "
                "A denied attempt can also use up a rate limit, lock an account or reveal information; if so the loss of 3 "
                "is too small. A deadline can raise the cost of looking."
            ),
            "check": "If one more look cost 3 units, the wrong-target loss were 40 and the chance of a wrong target 0.1, would looking first pay?",
            "answer": "Clicking now costs 0.1 x 40 = 4.0. Looking costs 3, so the net advantage is 4.0 - 3 = 1.0 and it pays. The break-even chance is 3 / 40 = 0.075, below 0.1.",
            "provenance": "Constructed example: the chapter's 0.1 chance of a wrong target, loss of 40 or 3 and observation cost of 2; the 0.05 and 0.2 chances are defined for this reader.",
            "source_section": "The price of another look",
            "source_anchor": "the-price-of-another-look",
            "controls": [
                {"key": "wrong_loss", "label": "Loss if the click reaches the wrong record", "values": [40, 3], "default": 40,
                 "value_labels": ["40: unguarded harmful release", "3: denied attempt (permission check)"]},
                {"key": "wrong_chance", "label": "Chance the saved point is wrong", "values": [0.05, 0.1, 0.2], "default": 0.1},
            ],
            "function": "another_look_picture",
        },
    ],
}

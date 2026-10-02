"""Chapter 8 reader: Acting in the Dark.

Four demonstrations built on Equations (8.1), (8.2) and (8.5). Demonstrations
1, 2 and 4 call the laboratory's own belief-and-information function
(math_ai_agents.chapters.ch08.evaluate), so the reader, the notebook and the
chapter skill agree. Demonstration 3 is the chapter's one-bit memory table,
computed directly. Every number is a constructed teaching value; the corridor
numbers for one and two moves, the runner posteriors 0.9709 and 0.7692 and the
verification-tool numbers are the book's own worked numbers.
"""
import math
from functools import lru_cache

import numpy as np

from math_ai_agents.chapters.ch08 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

# Equation (8.1), tag dropped, copied from the chapter.
EQ_UPDATE = (
    r"\mathbf{b}_{t+1}(x') \;=\;"
    "\n"
    r"\frac{\begin{gathered}"
    "\n"
    r"\operatorname{Obs}(o\mid x',a)\\"
    "\n"
    r"\cdot\sum_{x\in\mathcal{X}}P(x'\mid x,a)\,\mathbf{b}_t(x)"
    "\n"
    r"\end{gathered}}"
    "\n"
    r"{\begin{gathered}"
    "\n"
    r"\sum_{x''\in\mathcal{X}}\operatorname{Obs}(o\mid x'',a)\\"
    "\n"
    r"\cdot\sum_{x\in\mathcal{X}}P(x''\mid x,a)\,\mathbf{b}_t(x)"
    "\n"
    r"\end{gathered}}."
)
EQ_CORRIDOR = (
    r"T_E=\begin{pmatrix}"
    "\n"
    r"0.1&0.9&0&0\\"
    "\n"
    r"0.1&0&0.9&0\\"
    "\n"
    r"0&0.1&0&0.9\\"
    "\n"
    r"0&0&0.1&0.9"
    "\n"
    r"\end{pmatrix},\qquad"
    "\n"
    r"\operatorname{Obs}(\text{non-goal}\mid x')=(1,1,0,1)."
)
EQ_REWARD = r"\bar r(\mathbf{b},a)\;=\;\sum_{x\in\mathcal{X}}\mathbf{b}(x)\,r(x,a)."
EQ_VOI = (
    r"\begin{aligned}"
    "\n"
    r"\operatorname{VOI}(O)"
    "\n"
    r"&=\sum_{o}\Pr(o\mid\mathbf{b})\,"
    "\n"
    r"\max_{a\in\mathcal{A}}\bar r\big(\mathbf{b}'(\mathbf{b},o),a\big)\\"
    "\n"
    r"&\quad-\max_{a\in\mathcal{A}}\bar r(\mathbf{b},a)."
    "\n"
    r"\end{aligned}"
)

TOL = 1e-9
BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


# Demonstration 1: the corridor update, one step at a time

START = [1 / 3, 1 / 3, 0.0, 1 / 3]
NON_GOAL = 0
GOAL_SIGNAL = [[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 0.0]]  # columns: non-goal, goal


def east_matrix(slip):
    """Rows are current states, columns next states; EAST goes west with chance slip."""
    s = float(slip)
    return [[s, 1 - s, 0, 0], [s, 0, 1 - s, 0], [0, s, 0, 1 - s], [0, 0, s, 1 - s]]


def lab_corridor_step(belief, slip):
    """One EAST move and a non-goal report, computed by the laboratory's evaluate()."""
    out = evaluate({
        "belief": [float(x) for x in belief],
        "transition": east_matrix(slip),
        "observation": GOAL_SIGNAL,
        "observed": NON_GOAL,
        "action_rewards": [[0, 0, 0, 0]],
        "observation_cost": 0,
    })["metrics"]
    return out["predictive_belief"], out["posterior"], out["observed_probability"]


def corridor_sequence(moves, slip):
    beliefs, preds, kept = [list(START)], [], []
    for _ in range(moves):
        pred, post, mass = lab_corridor_step(beliefs[-1], slip)
        preds.append(pred)
        beliefs.append(post)
        kept.append(mass)
    return beliefs, preds, kept


def triple(values):
    return ", ".join(fmt(v, 3) for v in values)


def corridor_picture(moves=1, slip=0.1):
    moves = int(moves)
    beliefs, preds, kept = corridor_sequence(moves, slip)
    before, pred, after, mass = beliefs[-2], preds[-1], beliefs[-1], kept[-1]
    goal_pred = (1 - slip) * before[1] + slip * before[3]
    fig, axes = new_figure(ncols=3, height=4.1)
    panels = [
        (before, "Belief before the move", PALETTE["navy"], ""),
        (pred, "Predicted after EAST", PALETTE["grey"], "///"),
        (after, "After non-goal report", PALETTE["teal"], ""),
    ]
    x = np.arange(4)
    for ax, (values, title, color, hatch) in zip(axes, panels):
        ax.bar(x, values, color="white" if hatch else color, edgecolor=color, hatch=hatch, linewidth=1.4, width=0.62)
        for xi, v in zip(x, values):
            ax.annotate(fmt(v, 3), (xi, v), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                        fontsize=10.5, color=PALETTE["ink"])
        ax.set_xticks(x, ["1", "2", "3\ngoal", "4"])
        ax.set_ylim(0, 1.0)
        ax.set_xlabel("State, west to east")
        ax.set_ylabel("Probability")
        ax.set_title(title, fontsize=11.5)
        ax.grid(axis="x", alpha=0)
    metrics = {
        "Belief before the move": triple(before),
        "Predicted after EAST": triple(pred),
        "Belief after the report": triple(after),
        "Weight the report keeps": fmt(mass, 3),
        "West end after the report": fmt(after[0], 3),
    }
    interpretation = (
        f"Move {moves}, chance of sliding west {fmt(slip, 1)}. Predicted goal weight = {fmt(1 - slip, 3)} x {fmt(before[1], 3)}"
        f" + {fmt(slip, 3)} x {fmt(before[3], 3)} = {fmt(goal_pred, 3)}. A non-goal report rules out the goal, so it keeps"
        f" 1 - {fmt(goal_pred, 3)} = {fmt(mass, 3)} of the weight. West end after the report = {fmt(pred[0], 3)} / {fmt(mass, 3)}"
        f" = {fmt(after[0], 3)}; east end = {fmt(pred[3], 3)} / {fmt(mass, 3)} = {fmt(after[3], 3)}. The goal coordinate is exactly"
        f" 0 because the report excludes it. The west end is never exactly 0, because no report in this example rules it out."
    )
    return fig, metrics, interpretation


# Demonstration 2: the same report under different instrument models

THRESHOLD = 0.8


def lab_posterior_pass(prior, false_positive):
    """Probability the tests genuinely pass after a pass report, from the laboratory's evaluate()."""
    out = evaluate({
        "belief": [float(prior), 1 - float(prior)],
        "transition": [[1, 0], [0, 1]],
        "observation": [[1.0, 0.0], [float(false_positive), 1 - float(false_positive)]],
        "observed": 0,
        "action_rewards": [[0, 0]],
        "observation_cost": 0,
    })["metrics"]
    return out["posterior"][0]


def runner_picture(false_positive=0.03, prior=0.5):
    fp, prior = float(false_positive), float(prior)
    posterior = lab_posterior_pass(prior, fp)
    report_prob = prior + (1 - prior) * fp
    fps = np.linspace(0, 1, 101)
    curve = prior / (prior + (1 - prior) * fps)
    fig, ax = new_figure(height=4.2)
    ax.plot(fps, curve, color=PALETTE["teal"], linewidth=2)
    ax.axhline(THRESHOLD, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    ax.axhline(prior, color=PALETTE["gold"], linestyle="dotted", linewidth=1.6)
    ax.plot([fp], [posterior], "o", color=PALETTE["terracotta"], markersize=9)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.08)
    label_point(ax, 0.99, THRESHOLD, "release threshold 0.80", color=PALETTE["grey"], dx=0, dy=4, ha="right").set_bbox(BOX)
    label_point(ax, 0.99, prior, f"prior {fmt(prior, 2)}", color=PALETTE["gold"], dx=0, dy=-5, ha="right", va="top").set_bbox(BOX)
    side_right = fp < 0.55
    label_point(ax, fp, posterior, f"posterior {fmt(posterior, 4)}", color=PALETTE["terracotta"],
                dx=10 if side_right else -10, dy=-12 if posterior > prior + 0.12 else 14,
                ha="left" if side_right else "right", va="top" if posterior > prior + 0.12 else "bottom").set_bbox(BOX)
    ax.set_xlabel("False-positive probability: not passing, yet reports pass")
    ax.set_ylabel("Probability the tests pass, after a pass report")
    ax.set_title(f"Pass report, prior {fmt(prior, 2)}, false-positive {fmt(fp, 2)}", fontsize=11.5)
    if math.isclose(posterior, THRESHOLD, abs_tol=TOL):
        verdict = "exactly on the threshold, where releasing and declining have equal expected utility"
        decision = "tie at the threshold"
    elif posterior > THRESHOLD:
        verdict = "above the 0.80 threshold, so this one condition for release is met"
        decision = "above 0.80"
    else:
        verdict = "below the 0.80 threshold, so this one condition for release is not met"
        decision = "below 0.80"
    if math.isclose(fp, 1.0):
        extra = (" With false-positive probability 1, a pass report is equally likely from both states, so the report"
                 " carries no information and the posterior equals the prior.")
    else:
        extra = (" Holding the prior fixed, the only thing that changes across the false-positive settings is the assumed "
                 "instrument, never the report.")
    metrics = {
        "Chance of a pass report": fmt(report_prob, 4),
        "Posterior, tests pass": fmt(posterior, 4),
        "Compared with 0.80": decision,
        "Change from the prior": fmt(posterior - prior, 4),
    }
    interpretation = (
        f"Posterior = {fmt(prior, 2)} x 1 / ({fmt(prior, 2)} x 1 + {fmt(1 - prior, 2)} x {fmt(fp, 2)}) = "
        f"{fmt(prior, 2)} / {fmt(report_prob, 4)} = {fmt(posterior, 4)}, {verdict}.{extra}"
    )
    return fig, metrics, interpretation


# Demonstration 3: equal memory, different decision information

AUTHORIZED_GAIN = 4.0
FORMATTING_MEMORY_BELIEF = 0.5


def release_value(b, loss):
    """Equation (8.2) for the release action: belief-weighted reward (authorized +4, unauthorized loss)."""
    return AUTHORIZED_GAIN * b + loss * (1 - b)


def memory_picture(memory="authorization", loss=-12):
    loss = float(loss)
    b_grid = np.linspace(0, 1, 101)
    break_even = -loss / (AUTHORIZED_GAIN - loss)
    fig, ax = new_figure(height=4.3)
    ax.plot(b_grid, [release_value(b, loss) for b in b_grid], color=PALETTE["navy"], linewidth=2)
    ax.plot(b_grid, np.zeros_like(b_grid), color=PALETTE["terracotta"], linewidth=2)
    ax.axvline(break_even, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    ax.set_xlim(-0.02, 1.02)
    ax.set_ylim(min(loss, -4) - 2, 7)
    label_point(ax, 0.0, release_value(0.0, loss), "release", color=PALETTE["navy"], dx=8, dy=2, ha="left", va="bottom").set_bbox(BOX)
    label_point(ax, 1.0, 0.0, "hold", color=PALETTE["terracotta"], dx=-4, dy=-7, ha="right", va="top").set_bbox(BOX)
    left_of_line = break_even > 0.6
    label_point(ax, break_even, min(loss, -4) - 1.4, f"break-even {fmt(break_even, 2)}", color=PALETTE["grey"],
                dx=-5 if left_of_line else 5, dy=0, ha="right" if left_of_line else "left", va="bottom").set_bbox(BOX)
    if memory == "authorization":
        ax.plot([0.0, 1.0], [0.0, AUTHORIZED_GAIN], "s", color=PALETTE["teal"], markersize=9)
        label_point(ax, 1.0, AUTHORIZED_GAIN, "message yes: release, 4.0", color=PALETTE["teal"], dx=-6, dy=8, ha="right").set_bbox(BOX)
        label_point(ax, 0.0, 0.0, "message no: hold, 0.0", color=PALETTE["teal"], dx=8, dy=10, ha="left").set_bbox(BOX)
        mean_utility = (2 * AUTHORIZED_GAIN + 0 + 0) / 4
        posteriors = "1.00 after yes, 0.00 after no"
        unconstrained = "not needed (the belief is certain)"
        decision = "release on yes, hold on no"
        calc = (f"Message yes: belief 1.00, release = 1.00 x 4 + 0.00 x {signed(loss, 0)} = {fmt(release_value(1.0, loss), 1)}, "
                f"so release. Message no: belief 0.00, release = 0.00 x 4 + 1.00 x {signed(loss, 0)} = {fmt(release_value(0.0, loss), 1)}, "
                f"below hold at 0, so hold. Mean utility over the four histories = (4 + 4 + 0 + 0) / 4 = {fmt(mean_utility, 1)}.")
        meaning = " That equals the best the full history can do, because the discarded formatting bit never changes the decision."
    else:
        b = FORMATTING_MEMORY_BELIEF
        value = release_value(b, loss)
        ax.plot([b], [value], "o", color=PALETTE["teal"], markersize=9)
        ax.plot([b], [0.0], "s", color=PALETTE["teal"], markersize=9)
        label_point(ax, b, value, f"either letter: belief {fmt(b, 2)}", color=PALETTE["teal"], dx=10 if break_even < 0.5 else 8,
                    dy=10 if value <= 0.2 else -10, ha="left", va="bottom" if value <= 0.2 else "top").set_bbox(BOX)
        label_point(ax, b, 0.0, "actual choice: hold", color=PALETTE["teal"], dx=-8, dy=-12, ha="right", va="top").set_bbox(BOX)
        mean_utility = 0.0
        posteriors = "0.50 after either letter"
        unconstrained = fmt(value, 1)
        decision = "hold, because the authorization record is required"
        if math.isclose(value, 0.0, abs_tol=TOL):
            side = "The two actions tie at 0.0 on utility alone."
        elif value < 0:
            side = "Utility alone already favours hold."
        else:
            side = "Utility alone would favour release, but the required authorization is missing, so the rule forces hold."
        calc = (f"Either letter leaves belief {fmt(b, 2)}, so release = {fmt(b, 2)} x 4 + {fmt(1 - b, 2)} x {signed(loss, 0)} = "
                f"{fmt(value, 1)} against hold at 0. {side} Mean utility over the four histories = (0 + 0 + 0 + 0) / 4 = {fmt(mean_utility, 1)}.")
        meaning = " Same one bit of storage, but the retained bit carries no authorization information."
    ax.set_xlabel("Belief that the history is authorized")
    ax.set_ylabel("Expected reward of the action (utility points)")
    names = {"authorization": "keep authorization", "formatting": "keep formatting"}
    ax.set_title(f"One-bit memory: {names[memory]}; unauthorized release {fmt(loss, 0)}", fontsize=11.5)
    metrics = {
        "Belief after the message": posteriors,
        "Release value at that belief": unconstrained,
        "Action taken": decision,
        "Mean utility, four histories": fmt(mean_utility, 1),
    }
    return fig, metrics, calc + meaning


# Demonstration 4: when a look can change the decision

SUPPORT_REWARD = 10.0
UNSUPPORTED_LOSS = -40.0
PASS_IF_SUPPORTED = 0.9
FAIL_IF_UNSUPPORTED = 0.85
BAND_LOW = 0.4
BAND_HIGH = 34 / 35


@lru_cache(maxsize=None)
def lab_voi(p):
    """Gross value of one verification report, from the laboratory's evaluate() (zero cost)."""
    out = evaluate({
        "belief": [float(p), 1 - float(p)],
        "transition": [[1, 0], [0, 1]],
        "observation": [[PASS_IF_SUPPORTED, 1 - PASS_IF_SUPPORTED], [1 - FAIL_IF_UNSUPPORTED, FAIL_IF_UNSUPPORTED]],
        "observed": 0,
        "action_rewards": [[SUPPORT_REWARD, UNSUPPORTED_LOSS], [0, 0]],
        "observation_cost": 0,
    })["metrics"]
    value = out["gross_value_of_information"]
    return 0.0 if abs(value) < 1e-12 else value


def branch(p, supported_chance, unsupported_chance):
    """Best reward after one report, weighted by the report's probability (joint weights)."""
    release = SUPPORT_REWARD * supported_chance * p + UNSUPPORTED_LOSS * unsupported_chance * (1 - p)
    return release, max(release, 0.0)


def look_picture(prior=0.6, cost=0):
    p, cost = float(prior), float(cost)
    gross = lab_voi(round(p, 6))
    net = gross - cost
    now_release = SUPPORT_REWARD * p + UNSUPPORTED_LOSS * (1 - p)
    now = max(now_release, 0.0)
    pass_release, pass_best = branch(p, PASS_IF_SUPPORTED, 1 - FAIL_IF_UNSUPPORTED)
    fail_release, fail_best = branch(p, 1 - PASS_IF_SUPPORTED, FAIL_IF_UNSUPPORTED)
    if abs(gross - (pass_best + fail_best - now)) > 1e-9:
        raise AssertionError("hand calculation disagrees with the laboratory value of information")
    grid = np.linspace(0, 1, 201)
    curve = [lab_voi(round(float(g), 6)) for g in grid]
    fig, ax = new_figure(height=4.3)
    ax.axvspan(BAND_LOW, BAND_HIGH, facecolor="none", edgecolor=PALETTE["light"], hatch="//", linewidth=0)
    ax.plot(grid, curve, color=PALETTE["teal"], linewidth=2)
    if cost > 0:
        ax.axhline(cost, color=PALETTE["gold"], linestyle="dashed", linewidth=1.5)
        label_point(ax, 0.0, cost, f"cost of the look {fmt(cost, 1)}", color=PALETTE["gold"], dx=4, dy=4, ha="left").set_bbox(BOX)
    ax.plot([p], [gross], "o", color=PALETTE["terracotta"], markersize=9)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.3, 7.2)
    label_point(ax, 0.2, 0.0, "value 0 (flat, also above 34/35)", color=PALETTE["grey"], dx=0, dy=5, ha="center").set_bbox(BOX)
    label_point(ax, 0.69, 7.0, "band where a look can pay", color=PALETTE["grey"], dx=0, dy=0, ha="center", va="top")
    label_point(ax, 0.8, lab_voi(0.8), "peak 6.0", color=PALETTE["teal"], dx=6, dy=-2, ha="left", va="top").set_bbox(BOX)
    flip = p > 0.5
    label_point(ax, p, gross, f"prior {fmt(p, 2)}: {fmt(gross, 2)}", color=PALETTE["terracotta"],
                dx=-10 if flip else 10, dy=26 if gross < 0.8 else 6, ha="right" if flip else "left").set_bbox(BOX)
    ax.set_xlabel("Prior belief that the claim is supported")
    ax.set_ylabel("Value of one verification report (utility points)")
    ax.set_title(f"Verification tool; prior {fmt(p, 2)}; cost of looking {fmt(cost, 1)}", fontsize=11.5)

    if math.isclose(now_release, 0.0, abs_tol=TOL):
        now_text = f"release and decline tie at 0.0, so acting now is worth {fmt(now, 1)}"
    elif now_release > 0:
        now_text = f"release, worth {fmt(now, 1)}"
    else:
        now_text = f"decline, worth {fmt(now, 1)}"
    def pick(release):
        return "release" if release > TOL else "decline"
    if math.isclose(net, 0.0, abs_tol=TOL) and cost > 0:
        verdict = (f"The look breaks even: its value {fmt(gross, 2)} equals its cost {fmt(cost, 1)}, so Equation (8.5) leaves "
                   "looking and not looking tied and the person who owns the costs has to choose.")
        decision = "tie (break-even)"
    elif gross <= TOL:
        verdict = ("Both reports leave the same action best, so the look is worth exactly 0 however much it changes the belief."
                   + (" Paying anything for it loses." if cost > 0 else ""))
        decision = "do not look (value 0)" if cost > 0 else "no benefit (value 0)"
    elif net > 0:
        verdict = f"The look pays: {fmt(gross, 2)} - {fmt(cost, 1)} = {fmt(net, 2)} is above zero."
        decision = "look"
    else:
        verdict = f"The look is worth {fmt(gross, 2)}, less than its cost {fmt(cost, 1)}, so skip it."
        decision = "do not look"
    metrics = {
        "Best action without looking": (f"tie ({fmt(now, 1)})" if math.isclose(now_release, 0.0, abs_tol=TOL)
                                        else f"{pick(now_release)} ({fmt(now, 1)})"),
        "Value of looking (gross)": fmt(gross, 2),
        "Cost of looking": fmt(cost, 1),
        "Net value of looking": fmt(net, 2),
        "Decision": decision,
    }
    pass_chance = PASS_IF_SUPPORTED * p + (1 - FAIL_IF_UNSUPPORTED) * (1 - p)
    fail_chance = (1 - PASS_IF_SUPPORTED) * p + FAIL_IF_UNSUPPORTED * (1 - p)

    def per_report(best, chance):
        if best <= TOL or chance <= TOL:
            return ""
        return f" ({fmt(chance, 2)} x {fmt(best / chance, 2)}: the chance of the report times the expected reward after hearing it)"
    interpretation = (
        f"Acting now: 10 x {fmt(p, 2)} - 40 x {fmt(1 - p, 2)} = {fmt(now_release, 1)}, so {now_text}. "
        f"Each term below is weighted by the chance of the report, and 0.15 = 1 - 0.85 is the chance that an unsupported claim "
        f"still passes. After a pass (chance {fmt(pass_chance, 2)}): 0.90 x {fmt(p, 2)} x 10 - 0.15 x {fmt(1 - p, 2)} x 40 = "
        f"{fmt(PASS_IF_SUPPORTED * p * 10, 2)} - {fmt((1 - FAIL_IF_UNSUPPORTED) * (1 - p) * 40, 2)} = {fmt(pass_release, 2)}, "
        f"weighted best {pick(pass_release)} at {fmt(pass_best, 2)}{per_report(pass_best, pass_chance)}. "
        f"After a fail (chance {fmt(fail_chance, 2)}): 0.10 x {fmt(p, 2)} x 10 - 0.85 x {fmt(1 - p, 2)} x 40 = "
        f"{fmt((1 - PASS_IF_SUPPORTED) * p * 10, 2)} - {fmt(FAIL_IF_UNSUPPORTED * (1 - p) * 40, 2)} = {fmt(fail_release, 2)}, "
        f"weighted best {pick(fail_release)} at {fmt(fail_best, 2)}{per_report(fail_best, fail_chance)}. "
        f"Value of looking = {fmt(pass_best, 2)} + {fmt(fail_best, 2)} - {fmt(now, 1)} = {fmt(gross, 2)}. {verdict}"
    )
    return fig, metrics, interpretation


CHAPTER = {
    "number": 8,
    "title": "Acting in the Dark",
    "subtitle": "When one reading fits several situations, an agent keeps a belief over the possibilities and prices a look by the decisions it can change.",
    "summary": (
        "These four demonstrations follow the chapter from a robot in a corridor to an agent deciding whether to verify a claim. "
        "You will update a belief by hand-sized steps, see how the same report means different things under different instrument "
        "models, compare two equal-sized memories, and find the beliefs for which looking is worth anything."
    ),
    "demos": [
        {
            "id": "C08-D01",
            "title": "The corridor belief, step by step",
            "question": "After the robot moves east and hears that it is not at the goal, how does its belief over four places change?",
            "equations": [EQ_UPDATE, EQ_CORRIDOR],
            "symbols": (
                "b is the belief: one probability for each of four places in a corridor, numbered 1 to 4 from west to east, "
                "with place 3 the goal. An EAST move normally goes one place east, but with the chosen slip chance it goes one "
                "place west instead, and a move into a wall leaves the robot where it is. In Equation (8.1), a is the action taken "
                "(EAST), P(x' | x, a) is the chance that action a moves place x to place x', and Obs(o | x', a) is the chance of "
                "hearing report o in place x' after action a (here the report depends only on the place). x'' is a stand-in place "
                "used in the rescaling sum, and each sum runs over the four places. A non-goal report has chance 1 in places 1, 2 "
                "and 4 and chance 0 in place 3. The update has three stages: predict, weight by the report, rescale so the "
                "weights sum to 1."
            ),
            "prediction": "After the second move at slip chance 0.1 the west end holds 0.100. Will it still hold 0.100 after a third move?",
            "explanation": (
                "The prediction pushes each place's weight along the move, which is the inner sum of Equation (8.1). The "
                "report then multiplies each predicted weight by its likelihood, here 1 or 0, and the denominator rescales what "
                "is left. Because the report only removes the goal, the other places keep their relative sizes. The west end "
                "never reaches 0 because nothing the robot has heard rules it out. In the chapter's two worked moves at slip chance "
                "0.1 it holds at 0.100; that is true of those two moves only, and a third move lowers it, so it is not conserved."
            ),
            "application": (
                "Whenever a tool result leaves several explanations open, write down the possibilities, the chance the action "
                "moved each one, and the chance each would have produced the report. The three stages then give the new weights "
                "without rereading the whole history."
            ),
            "assumptions": (
                "The four-place corridor, the deterministic goal report and the move probabilities are stipulated. The chapter "
                "reports one and two moves at slip chance 0.1; the third move and the 0.3 slip are the same rule continued, "
                "not a result from the paper. The model is only as good as the move and report probabilities supplied to it; "
                "if the real corridor differs, the update is exact for the wrong world."
            ),
            "check": "Start from (1/3, 1/3, 0, 1/3) with slip chance 0.2. What is the west-end weight after the first non-goal report?",
            "answer": (
                "Predicted west end = 0.2 x (1/3) + 0.2 x (1/3) = 0.133. The goal is predicted to hold 0.8 x (1/3) + 0.2 x (1/3) = 1/3, "
                "so the report keeps 1 - 1/3 = 2/3. West end = 0.133 / 0.667 = 0.200."
            ),
            "provenance": (
                "Constructed example: the corridor of the chapter's worked update (the book's own values for one and two moves at "
                "slip chance 0.1), extended by one move and one alternative slip chance defined for this reader and computed with "
                "the laboratory's belief function."
            ),
            "source_section": "The update, worked",
            "source_anchor": "the-update-worked",
            "controls": [
                {"key": "moves", "label": "Number of EAST moves so far", "values": [1, 2, 3], "default": 1},
                {"key": "slip", "label": "Chance an EAST move goes west instead", "values": [0.1, 0.3], "default": 0.1},
            ],
            "function": "corridor_picture",
        },
        {
            "id": "C08-D02",
            "title": "The same report under different instruments",
            "question": "If a test runner says pass, how likely is it that the tests really pass, and what decides that?",
            "equations": [EQ_UPDATE],
            "symbols": (
                "The runner has two modeled states: the tests genuinely pass, or they do not (failed or never ran). The prior is "
                "the probability they pass before the report. A passing state always reports pass. The false-positive "
                "probability is the chance that a not-passing state also reports pass. Running the report does not change "
                "which state holds, so the predict stage leaves the belief as it is and only the weighting and rescaling remain. "
                "The dashed line at 0.80 is the release threshold used later in the chapter."
            ),
            "prediction": "Keep the prior at 0.50 and raise the false-positive probability from 0.03 to 0.30. Does the posterior cross 0.80, and in which direction?",
            "explanation": (
                "Equation (8.1) weights the passing state by 1 and the not-passing state by the false-positive probability, then "
                "rescales. A small false-positive probability makes a pass report strong evidence; a large one makes it weak; at 1 "
                "it is no evidence at all. The report is identical in every state of this demonstration. Holding the prior fixed, "
                "only the assumed instrument changes, and with it the conclusion."
            ),
            "application": (
                "Before trusting a pass, a green check or a found-nothing result, ask how often the bad state produces the same "
                "output. That one number, the false-positive probability, decides whether the report can carry a decision."
            ),
            "assumptions": (
                "Two states, a true-positive probability of 1, and the false-positive probabilities and priors shown, all "
                "stipulated for teaching and not measured from any runner. Correct arithmetic cannot repair a wrong likelihood. "
                "A single report is used; repeated reports would need a model of how they depend on each other."
            ),
            "check": "With prior 0.50 and true-positive probability 1, what false-positive probability puts the posterior exactly at 0.80?",
            "answer": "0.5 / (0.5 + 0.5 x f) = 0.8 gives 0.5 + 0.5 x f = 0.625, so f = 0.25. Below 0.25 the pass report clears 0.80; above it does not.",
            "provenance": (
                "Constructed example: the chapter's test-runner teaching assumptions (true-positive 1, false-positive 0.03 and 0.30, "
                "prior 0.5, giving 0.9709 and 0.7692), plus two more false-positive values and a second prior defined for this reader, "
                "computed with the laboratory's belief function."
            ),
            "source_section": "Where the observation kernel comes from",
            "source_anchor": "where-the-observation-kernel-comes-from",
            "controls": [
                {"key": "false_positive", "label": "False-positive probability", "values": [0.03, 0.1, 0.3, 1.0], "default": 0.03},
                {"key": "prior", "label": "Prior probability the tests pass", "values": [0.5, 0.2], "default": 0.5},
            ],
            "function": "runner_picture",
        },
        {
            "id": "C08-D03",
            "title": "Equal memory, different decisions",
            "question": "Two memories hold exactly one bit each. Why can one support the release decision and the other not?",
            "equations": [EQ_REWARD],
            "symbols": (
                "A history has two facts: whether release is authorized (yes or no) and an irrelevant formatting preference (A "
                "or B). The four histories are equally likely. b is the belief that the history is authorized. r(x, a) is the "
                "reward of action a in state x: releasing earns 4 when authorized and the chosen loss when not, and holding "
                "earns 0. The reward averaged under the belief is Equation (8.2). The break-even belief is where releasing and "
                "holding have the same average reward."
            ),
            "prediction": "Keep formatting instead of authorization. What is the belief after seeing letter A, and what is the mean utility of the controller?",
            "explanation": (
                "Keeping authorization gives belief 1 or 0, so the controller releases on yes and holds on no, for a mean of 2. "
                "Keeping the formatting letter splits each letter evenly between authorized and unauthorized histories, so the "
                "belief is 0.5 either way. Equation (8.2) at 0.5 is the average of the two rewards, and in this task release also "
                "requires authorization evidence, so the controller holds and earns 0."
            ),
            "application": (
                "When shrinking a summary or a memory, list the histories it merges and check whether the best allowed action "
                "agrees across each merged group. Equal size says nothing; what the retained bit distinguishes is what matters."
            ),
            "assumptions": (
                "A stipulated toy task: four equally likely histories, authorization fixed between observation and action, and "
                "release permitted only with an authoritative authorization record. If formatting decided a required output, or "
                "authorization could expire, the comparison would change. It shows decision sufficiency for one task, not that "
                "short summaries are better in general."
            ),
            "check": "If an unauthorized release cost 20 instead of 12, at what belief would releasing and holding have the same average reward?",
            "answer": "4 x b - 20 x (1 - b) = 0 gives 24 x b = 20, so b = 0.833. Above 0.833 releasing has the higher average reward.",
            "provenance": (
                "Constructed example: the chapter's four-history document-release table with the book's stipulated utilities "
                "(+4 authorized, -12 unauthorized, 0 for holding), plus two alternative losses defined for this reader."
            ),
            "source_section": "Where an agent's belief actually lives",
            "source_anchor": "where-an-agents-belief-actually-lives",
            "controls": [
                {"key": "memory", "label": "Which bit the memory keeps", "values": ["authorization", "formatting"], "default": "authorization",
                 "value_labels": ["Authorization", "Formatting letter"]},
                {"key": "loss", "label": "Utility of an unauthorized release", "values": [-12, -4, -1], "default": -12},
            ],
            "function": "memory_picture",
        },
        {
            "id": "C08-D04",
            "title": "A look pays only near the threshold",
            "question": "For which prior beliefs can a verification tool change the decision, and is the change worth its cost?",
            "equations": [EQ_VOI],
            "symbols": (
                "p is the prior belief that a claim is supported. Releasing a supported claim earns 10, an unsupported one loses "
                "40, and declining earns 0, so releasing is better when p is above 0.8. The tool reports pass on 90 percent of "
                "supported claims and fail on 85 percent of unsupported ones. The value of the look (VOI) is the average of the "
                "best reward after each report minus the best reward without looking. The dashed gold line is the price of the look."
            ),
            "prediction": "At prior 0.2 a pass would lift the belief to 0.60. Is the look worth anything, and what about at 0.99?",
            "explanation": (
                "After each report the controller picks its best action, and Equation (8.5) averages those best rewards by how "
                "likely each report is. If the same action is best after both reports, the average equals the best reward "
                "without looking and the value is exactly 0. Only priors where a report can push the belief across 0.8 give "
                "a positive value, and the peak sits at 0.8 where the two actions tie."
            ),
            "application": (
                "Before paying for a check, ask whether any answer it could give would change what you do. If not, its value "
                "is 0 however reassuring it sounds. If so, compare the value with the price of the check."
            ),
            "assumptions": (
                "One report, one decision afterward, a fixed price for looking, and the stipulated rewards and tool rates. The "
                "band from 0.4 to 34/35 describes beliefs, not how often cases land in it. Real tools can fail in ways the two "
                "rates do not describe, and checking takes time that a single price may not capture."
            ),
            "check": "With prior 0.5 and no cost, what is the value of the look?",
            "answer": (
                "After a pass: 0.9 x 0.5 x 10 - 0.15 x 0.5 x 40 = 4.5 - 3.0 = 1.5, so release. After a fail: 0.1 x 0.5 x 10 - 0.85 x 0.5 x 40 = "
                "0.5 - 17.0 = (-16.5), so decline at 0. Acting now: 10 x 0.5 - 40 x 0.5 = (-15), so decline at 0. Value = 1.5 + 0 - 0 = 1.5."
            ),
            "provenance": (
                "Constructed example: the chapter's verification-tool instance (rewards 10, -40 and 0; pass 0.90 and fail 0.85; "
                "value 3.0 at prior 0.6 and exactly 0 at 0.2 and 0.99), with two more priors and a price of 3.0 defined for this "
                "reader, computed with the laboratory's belief function."
            ),
            "source_section": "The condition that makes a look worthless",
            "source_anchor": "the-condition-that-makes-a-look-worthless",
            "controls": [
                {"key": "prior", "label": "Prior belief the claim is supported", "values": [0.2, 0.6, 0.8, 0.99], "default": 0.6},
                {"key": "cost", "label": "Price of the look", "values": [0, 3], "default": 0, "value_labels": ["Free", "3.0 utility points"]},
            ],
            "function": "look_picture",
        },
    ],
}

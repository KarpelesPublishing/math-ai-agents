"""Chapter 5 reader: What the Model Becomes Inside an Agent.

Four demonstrations built on the chapter's six-assembly experiment, the
composite transition law (Equation 5.2), the value of an observation
(Equation 5.4) and recurrence (Equation 5.5). Demonstrations 2 and 4 call the
laboratory's own computation (math_ai_agents.chapters.ch05.evaluate), so the
reader, the notebook and the chapter skill agree. Demonstrations 1 and 3
compute the chapter's closed forms directly. Every number is a constructed
teaching value; the defaults are the book's own worked numbers.
"""
import math
from functools import lru_cache

import numpy as np

from math_ai_agents.chapters.ch05 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

# The book's declared response laws (section "The fair experiment").
BOOK_REQUEST = 0.40      # probability that a blind context outputs `request`
BOOK_TOOL = 0.90         # probability that the tool reports the hidden bit correctly
MATCH, OPPOSITE, STOP = 0.85, 0.10, 0.05   # informed response law

EQ_INFORMED = r"0.90(0.85)+0.10(0.10)=0.775"
EQ_KERNEL = (
    r"\begin{aligned}"
    r"P_{\mathrm{env}}(x'\mid x,u)"
    r" &=\sum_{g,o}\operatorname{Grant}(g\mid x,u)\\"
    r" &\quad\cdot \operatorname{Env}(w',o\mid x,u,g)\\"
    r" &\quad\cdot \operatorname{Upd}(c',m',b'\mid x,u,g,w',o),\\[3pt]"
    r"P_\theta(x'\mid x)"
    r" &=\sum_u\pi_\theta(u\mid x)P_{\mathrm{env}}(x'\mid x,u)."
    r"\end{aligned}"
)
EQ_INFO = r"I(Y;O)=H(Y)-H(Y\mid O)"
EQ_PRODUCT = r"\Pr(x_{0:T})=\Pr(x_0)\prod_{t=0}^{T-1}P(x_{t+1}\mid x_t)"


def trim(x, digits=3):
    """Number text without trailing zeros (0.4 not 0.400), for written sums."""
    text = fmt(x, digits)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def informed_correct(accuracy):
    """Probability an informed answer is correct when the tool is right with probability `accuracy`."""
    return accuracy * MATCH + (1 - accuracy) * OPPOSITE


# Demonstration 1: the six assemblies

ROWS = [
    "1 Model only",
    "2 Memory, no reader",
    "3 Tool, no recurrence",
    "4 Recurrence, blind",
    "5 Connected, granted",
    "6 Connected, denied",
]


def assembly_scores(request, rejection):
    blind = (1 - request) / 2
    second_blind = blind + request * blind
    connected = blind + request * informed_correct(BOOK_TOOL)
    denied = blind if rejection == "stop" else second_blind
    return [blind, blind, blind, second_blind, connected, denied]


def six_assemblies_picture(request=0.4, rejection="stop"):
    request = float(request)
    scores = assembly_scores(request, rejection)
    blind = scores[0]
    informed = informed_correct(BOOK_TOOL)
    wrong = blind + request * (BOOK_TOOL * OPPOSITE + (1 - BOOK_TOOL) * MATCH)
    stopped = request * STOP
    fig, ax = new_figure(height=4.2)
    y = np.arange(6)[::-1]
    styles = [
        (PALETTE["light"], ""), (PALETTE["light"], "//"), (PALETTE["light"], "xx"),
        (PALETTE["gold"], ""), (PALETTE["teal"], ""), (PALETTE["terracotta"], "\\\\"),
    ]
    for yi, value, (color, hatch) in zip(y, scores, styles):
        ax.barh(yi, value, height=0.6, color=color, edgecolor=PALETTE["ink"], hatch=hatch, linewidth=0.9)
        ax.text(value + 0.012, yi, fmt(value, 3), va="center", fontsize=11, color=PALETTE["ink"])
    ax.axvline(blind, color=PALETTE["grey"], linestyle="dashed", linewidth=1.2)
    ax.set_yticks(y, ROWS)
    ax.set_xlim(0, 1.0)
    ax.set_xlabel("Probability the run ends with a correct answer")
    ax.set_ylabel("Assembly (frozen model in every row)")
    ax.grid(axis="y", alpha=0)
    policy = "stops with no answer" if rejection == "stop" else "makes a second blind call"
    ax.set_title(f"Blind call requests {fmt(request, 2)} of the time; denial {policy}", fontsize=11.5)
    metrics = {ROWS[i][2:]: fmt(scores[i], 3) for i in range(6)}
    metrics["Row 5 minus row 1"] = fmt(scores[4] - blind, 3)
    metrics["Row 5 wrong answer"] = fmt(wrong, 3)
    metrics["Row 5 stops with no answer"] = fmt(stopped, 3)
    if rejection == "stop":
        denial = (f"Row 6 stops at the rejection, so it scores the blind rate {fmt(blind, 3)}, exactly row 1. "
                  "The tool was never reached, so one revoked grant removes the whole gain.")
    else:
        denial = (f"With a second blind call after the rejection, row 6 scores {fmt(blind, 3)} + {fmt(request, 2)} x "
                  f"{fmt(blind, 3)} = {fmt(scores[5], 3)}, the same as row 4, because a denied tool adds no information.")
    interpretation = (
        f"A blind answer is correct with probability (1 - {fmt(request, 2)}) / 2 = {fmt(blind, 3)}, whatever the hidden bit is. "
        f"Row 4 = {fmt(blind, 3)} + {fmt(request, 2)} x {fmt(blind, 3)} = {fmt(scores[3], 3)}. "
        f"An informed answer is correct with probability 0.90 x 0.85 + 0.10 x 0.10 = {fmt(informed, 3)}, so row 5 = "
        f"{fmt(blind, 3)} + {fmt(request, 2)} x {fmt(informed, 3)} = {fmt(scores[4], 3)}. "
        f"Rows 2 and 3 hold real components that no later call reads, so they stay at {fmt(blind, 3)}. {denial} "
        f"Check: correct {fmt(scores[4], 3)} + wrong {fmt(wrong, 3)} + stopped {fmt(stopped, 3)} = "
        f"{fmt(scores[4] + wrong + stopped, 3)}."
    )
    return fig, metrics, interpretation


# Demonstration 2: the composite kernel (laboratory computation)

CHOOSER = [[0.8, 0.2], [0.3, 0.7]]
TOOLS = {
    "default": [[0.9, 0.1], [0.2, 0.8]],
    "changed": [[0.6, 0.4], [0.1, 0.9]],
}
TOOL_LABELS = {"default": "default tool", "changed": "changed tool"}
KERNEL_HORIZON = 30


@lru_cache(maxsize=None)
def lab_kernel(tool):
    """Composite kernel and state-0 occupancy from the laboratory's evaluate()."""
    out = evaluate({
        "step_success": 0.99, "steps": KERNEL_HORIZON, "conditional_success": [0.99] * KERNEL_HORIZON,
        "chooser": CHOOSER, "tool": TOOLS[tool], "initial": [1, 0],
    })
    occupancy = [s for s in out["series"] if s["label"] == "state zero occupancy"][0]["y"]
    return out["metrics"]["composite_kernel"], tuple(occupancy)


def composite_kernel_picture(tool="default", transitions=2):
    kernel, occupancy = lab_kernel(tool)
    other = "changed" if tool == "default" else "default"
    other_kernel, other_occupancy = lab_kernel(other)
    n = int(transitions)
    k00, k10 = kernel[0][0], kernel[1][0]
    long_run = k10 / (1 - k00 + k10)
    after = occupancy[n]
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    t = np.arange(KERNEL_HORIZON + 1)
    left.plot(t, other_occupancy, color=PALETTE["grey"], linestyle="dashed", linewidth=1.6)
    left.plot(t, occupancy, color=PALETTE["teal"], linewidth=2.2)
    left.plot([n], [after], "o", color=PALETTE["terracotta"], markersize=9)
    box = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
    label_point(left, 14, occupancy[14], f"{TOOL_LABELS[tool]} (chosen)", color=PALETTE["teal"], dx=0, dy=8 if occupancy[14] > other_occupancy[14] else -8,
                ha="center", va="bottom" if occupancy[14] > other_occupancy[14] else "top").set_bbox(box)
    label_point(left, 14, other_occupancy[14], TOOL_LABELS[other], color=PALETTE["grey"], dx=0, dy=-8 if occupancy[14] > other_occupancy[14] else 8,
                ha="center", va="top" if occupancy[14] > other_occupancy[14] else "bottom").set_bbox(box)
    left.set_xlim(-0.5, KERNEL_HORIZON + 1)
    left.set_ylim(0, 1.05)
    left.set_xlabel("Number of transitions")
    left.set_ylabel("Probability of being in state 0")
    left.set_title(f"Start in state 0; dot marks {n} transition" + ("" if n == 1 else "s"), fontsize=11.5)

    matrix = np.array(kernel)
    right.imshow(matrix, cmap="Blues", vmin=0, vmax=1.3, aspect="equal")
    for i in range(2):
        for j in range(2):
            right.text(j, i, fmt(matrix[i][j], 2), ha="center", va="center", fontsize=13,
                       color="white" if matrix[i][j] > 0.55 else PALETTE["ink"])
    right.set_xticks([0, 1], ["state 0", "state 1"])
    right.set_yticks([0, 1], ["state 0", "state 1"])
    right.set_xlabel("Next state j")
    right.set_ylabel("Current state i")
    right.set_title("Composite kernel K = chooser x tool", fontsize=11.5)
    right.grid(False)

    metrics = {
        "Composite row 0": f"[{fmt(kernel[0][0], 2)}, {fmt(kernel[0][1], 2)}]",
        "Composite row 1": f"[{fmt(kernel[1][0], 2)}, {fmt(kernel[1][1], 2)}]",
        f"State 0 after {n} transition" + ("" if n == 1 else "s"): fmt(after, 3),
        "Long-run state 0": fmt(long_run, 3),
        "Chooser rows": "unchanged: [0.80, 0.20] and [0.30, 0.70]",
    }
    t0, t1 = TOOLS[tool]
    row0 = (f"K(0,0) = 0.8 x {fmt(t0[0], 1)} + 0.2 x {fmt(t1[0], 1)} = {fmt(kernel[0][0], 2)} and "
            f"K(0,1) = 0.8 x {fmt(t0[1], 1)} + 0.2 x {fmt(t1[1], 1)} = {fmt(kernel[0][1], 2)}")
    row1 = f"K(1,0) = 0.3 x {fmt(t0[0], 1)} + 0.7 x {fmt(t1[0], 1)} = {fmt(kernel[1][0], 2)}"
    step1 = f"1 x {fmt(k00, 2)} + 0 x {fmt(k10, 2)} = {fmt(k00, 2)}"
    mu2 = k00 * k00 + (1 - k00) * k10
    step2 = f"{fmt(k00, 2)} x {fmt(k00, 2)} + {fmt(1 - k00, 2)} x {fmt(k10, 2)} = {fmt(mu2, 3)}"
    interpretation = (
        f"Each row of K mixes the tool's rows, weighted by the chooser's probabilities: {row0}; {row1}. "
        f"Starting in state 0, the chance of state 0 after one transition is {step1}, after two it is {step2}. "
        f"After {n} it is {fmt(after, 3)}, and it settles near {fmt(long_run, 3)}. "
        "Only the tool changed between the two curves; the chooser's probabilities are identical, yet the "
        "recurrent system the chooser lives in is different."
    )
    return fig, metrics, interpretation


# Demonstration 3: what an observation is worth

def entropy_bits(p):
    """Binary entropy in bits, with 0 log 0 taken as 0."""
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


def observation_picture(accuracy=0.9, reaches="stops"):
    a = float(accuracy)
    h_after = entropy_bits(a)
    info = 1 - h_after
    informed = informed_correct(a)
    blind = (1 - BOOK_REQUEST) / 2
    connected = reaches == "reaches"
    success = blind + BOOK_REQUEST * informed if connected else blind
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    grid = np.linspace(0.5, 1.0, 101)
    left.plot(grid, [1 - entropy_bits(x) for x in grid], color=PALETTE["navy"], linewidth=2)
    left.plot([a], [info], "o", color=PALETTE["terracotta"], markersize=9)
    box = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
    label_point(left, a, info, f"{fmt(info, 3)} bits", color=PALETTE["terracotta"], dx=-10 if a > 0.7 else 10,
                dy=8, ha="right" if a > 0.7 else "left", va="bottom")
    left.set_xlim(0.48, 1.02)
    left.set_ylim(-0.04, 1.12)
    left.set_xlabel("Chance the tool reports the hidden bit correctly")
    left.set_ylabel("Information about the bit (bits)")
    left.set_title("What the observation delivers", fontsize=11.5)

    right.bar([0, 1], [blind, success], width=0.55, color=[PALETTE["light"], PALETTE["teal"] if connected else PALETTE["gold"]],
              edgecolor=PALETTE["ink"], hatch=None)
    right.patches[1].set_hatch("" if connected else "//")
    for x, v in ((0, blind), (1, success)):
        right.text(x, v + 0.02, fmt(v, 3), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    right.set_xticks([0, 1], ["Model only", "Observation reaches\na later call" if connected else "Observation, then\nthe run stops"])
    right.set_xlim(-0.6, 1.6)
    right.set_ylim(0, 0.85)
    right.set_xlabel("Assembly")
    right.set_ylabel("Probability of a correct answer")
    right.set_title("What it changes in the outcome", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    metrics = {
        "Uncertainty after, H(Y | O)": f"{fmt(h_after, 3)} bits",
        "Information, I(Y;O)": f"{fmt(info, 3)} bits",
        "Success with this assembly": fmt(success, 3),
        "Success gain over model only": fmt(success - blind, 3),
    }
    if a >= 1 - 1e-12:
        entropy_sum = "H(Y | O) = 0 x 3.322 + 1 x 0 = 0.000 bits (the term 0 x log2 0 is taken as 0)"
    else:
        low, high = 1 - a, a
        entropy_sum = (f"H(Y | O) = {trim(low, 2)} x {fmt(-math.log2(low), 3)} + {trim(high, 2)} x {fmt(-math.log2(high), 3)}"
                       f" = {fmt(h_after, 3)} bits")
    info_line = f"{entropy_sum}, so I(Y;O) = 1 - {fmt(h_after, 3)} = {fmt(info, 3)} bits."
    if connected:
        decision = (f"The observation reaches a later call: informed answer correct = {trim(a, 2)} x 0.85 + {trim(1 - a, 2)} x 0.10 = "
                    f"{fmt(informed, 4)}, so success = {fmt(blind, 2)} + 0.40 x {fmt(informed, 4)} = {fmt(success, 3)}.")
        if a <= 0.5 + 1e-12:
            decision += (" The tool delivers 0 bits, yet success still rises. That rise comes from the declared informed "
                         "response law, which answers 95 percent of the time instead of 60 percent, not from information: "
                         "bits and score are different measures.")
    else:
        decision = (f"The run stops after the observation, so no choice consumes the bits: success = {fmt(blind, 2)} + 0.40 x 0 = "
                    f"{fmt(success, 2)}, the model-only rate. ")
        if info > 5e-4:
            decision += "The information is real and its decision value here is zero."
        else:
            decision += "The report carries no information, so its decision value is zero as well."
    interpretation = f"{info_line} {decision}"
    return fig, metrics, interpretation


# Demonstration 4: recurrence multiplies

STEPS = 100
HEADLINE = 40


@lru_cache(maxsize=None)
def lab_survival(q):
    """Probability that all i required steps succeed, i = 0..100, from the laboratory's evaluate()."""
    out = evaluate({
        "step_success": q, "steps": STEPS, "conditional_success": [q] * STEPS,
        "chooser": [[1, 0], [0, 1]], "tool": [[1, 0], [0, 1]], "initial": [1, 0],
    })
    curve = [s for s in out["series"] if s["label"] == "independent trajectory success"][0]["y"]
    if not math.isclose(out["metrics"]["chain_rule_all_success"], curve[-1], rel_tol=1e-9):
        raise AssertionError("laboratory chain rule disagrees with the independent curve")
    return tuple(curve)


def effective_step(p, handling):
    return p if handling == "none" else 1 - (1 - p) ** 2


def step_text(q):
    """A per-step probability for written arithmetic, with enough digits to tell it from 1."""
    return trim(q, 6 if q > 0.99995 else 4)


def horizon_text(q):
    half = math.log(0.5) / math.log(q)
    return f"{fmt(half, 0 if half >= 100 else 1)} steps"


def recurrence_picture(step_success=0.99, handling="none"):
    p = float(step_success)
    q = effective_step(p, handling)
    other_handling = "retry" if handling == "none" else "none"
    q_other = effective_step(p, other_handling)
    curve = lab_survival(q)
    other = lab_survival(q_other)
    names = {"none": "no retry", "retry": "one retry"}
    fig, ax = new_figure(height=4.3)
    x = np.arange(STEPS + 1)
    ax.plot(x, other, color=PALETTE["grey"], linestyle="dashed", linewidth=1.6)
    ax.plot(x, curve, color=PALETTE["teal"], linewidth=2.4)
    ax.plot([HEADLINE], [curve[HEADLINE]], "o", color=PALETTE["terracotta"], markersize=9)
    ax.axvline(HEADLINE, color=PALETTE["light"], linewidth=1.2, zorder=0)
    # Name each curve at its right-hand end, so no label sits on a line.
    for key in ("retry", "none"):
        yvals = curve if key == handling else other
        text = names[key] + (" (chosen)" if key == handling else "")
        label_point(ax, STEPS, yvals[STEPS], text, color=PALETTE["teal"] if key == handling else PALETTE["grey"],
                    dx=6, dy=0, ha="left", va="center")
    label_point(ax, HEADLINE, curve[HEADLINE], f"step 40: {fmt(curve[HEADLINE], 3)}", color=PALETTE["terracotta"],
                dx=8, dy=-8 if (curve[HEADLINE] > 0.9 and handling == "none") else 8, ha="left",
                va="top" if (curve[HEADLINE] > 0.9 and handling == "none") else "bottom")
    ax.set_xlim(0, 145)
    ax.set_xticks(range(0, STEPS + 1, 20))
    ax.set_ylim(-0.02, 1.12)
    ax.set_xlabel("Number of required steps")
    ax.set_ylabel("Probability every step so far succeeded")
    ax.set_title(f"Per-step success {fmt(p, 3)} before any retry", fontsize=11.5)
    metrics = {
        "Conditional success per step used": fmt(q, 6 if q > 0.99995 else 4),
        "After 10 steps": fmt(curve[10], 3),
        "After 40 steps": fmt(curve[40], 3),
        "After 100 steps": fmt(curve[100], 3),
        "Steps until success falls below 0.5": horizon_text(q) + (" (beyond the plotted 100)" if math.log(0.5) / math.log(q) > STEPS else ""),
    }
    shown40 = fmt(curve[40], 5 if curve[40] > 0.9995 else 3)
    factors = f"{step_text(q)} x {step_text(q)} x ... x {step_text(q)} (40 factors) = {shown40}"
    if handling == "retry":
        step_line = (f"With one independent retry, a step fails only if both tries fail: q = 1 - {trim(1 - p, 3)} x {trim(1 - p, 3)} = "
                     f"{trim(q, 6)}. ")
    else:
        step_line = f"Any failed step ends the task, so each step must succeed, q = {step_text(q)}. "
    interpretation = (
        f"{step_line}Equation (5.5) multiplies one-step probabilities along the run: two steps give {step_text(q)} x {step_text(q)} = "
        f"{trim(q * q, 6)}, and forty steps give {factors}. The success curve falls below one half after about "
        f"{horizon_text(q)}. This is the limit of this declared chain, not of agents in general."
    )
    return fig, metrics, interpretation


CHAPTER = {
    "number": 5,
    "title": "What the Model Becomes Inside an Agent",
    "subtitle": "Hold the model still, change what surrounds it, and the system's behavior changes. The chapter shows why with a small constructed experiment.",
    "summary": (
        "These four demonstrations follow the chapter's frozen-model experiment. First, six assemblies around one unchanged model "
        "give different success rates. Second, a fixed chooser and a changed tool produce different recurrent systems. Third, "
        "an observation is measured in bits and compared with what it changes. Fourth, a run's probability is a product, "
        "so small per-step failures compound."
    ),
    "demos": [
        {
            "id": "C05-D01",
            "title": "Six assemblies around one frozen model",
            "question": "If the model never changes, how can six assemblies of it succeed at different rates?",
            "equations": [EQ_INFORMED],
            "symbols": (
                "A blind call is a model call that has not seen the tool's result. Its request probability is the share of blind "
                "calls that output request instead of an answer; the rest is split equally between the two answers. The hidden bit "
                "Y is 0 or 1 with equal chance. The tool reports Y correctly with probability 0.90. In a context that contains the "
                "report, the model answers with the reported bit with probability 0.85, with the other bit with probability 0.10, "
                "and outputs request with probability 0.05. A success is a correct final answer."
            ),
            "prediction": "Leave the request probability at 0.40 and change denial to a second blind call. Which bar moves, and to what value?",
            "explanation": (
                "A blind answer is right about as often as it is wrong, whatever the hidden bit. Rows 2 and 3 add a memory and a tool, "
                "but no later call reads their output, so they cannot move the score. Row 4 adds a second blind call and row 5 adds an "
                "informed one, so both gain only through the requests they rescue. Row 6 is row 5 with one grant revoked."
            ),
            "application": (
                "When someone says an agent is better because it has memory or tools, ask which later decision reads their output. "
                "A component that sits on no path from the model's output to the outcome contributes exactly zero."
            ),
            "assumptions": (
                "Two model calls at most, a tool that is either granted or denied, and the response laws above, which hold in every "
                "row. The six bars are assembly comparisons, not a matched factorial design. The rejection rule matters: if denial "
                "sends the run to a second blind call, row 6 equals row 4, not row 1. Nothing here says deployed effect sizes look like these."
            ),
            "check": "If a blind call requested 0.60 of the time, what would the fully connected assembly (row 5) score?",
            "answer": "Blind rate = (1 - 0.60) / 2 = 0.20. Row 5 = 0.20 + 0.60 x 0.775 = 0.20 + 0.465 = 0.665.",
            "provenance": "Constructed example: the chapter's six-assembly experiment; the default 0.40 request probability gives the book's values 0.30, 0.42 and 0.61.",
            "source_section": "The fair experiment",
            "source_anchor": "the-fair-experiment",
            "controls": [
                {"key": "request", "label": "Share of blind calls that output request", "values": [0.2, 0.4, 0.6, 0.8], "default": 0.4},
                {"key": "rejection", "label": "What a denied request does", "values": ["stop", "blind"], "default": "stop",
                 "value_labels": ["Stops, no answer (the book's rule)", "Makes a second blind call"]},
            ],
            "function": "six_assemblies_picture",
        },
        {
            "id": "C05-D02",
            "title": "A fixed chooser, a different tool, a different system",
            "question": "If the chooser's probabilities never change, can changing only the tool change where the system spends its time?",
            "equations": [EQ_KERNEL],
            "symbols": (
                "A state is one of two constructed states, 0 and 1. The chooser row for state i gives the probability of each proposed "
                "action (the role of pi in the equation). The tool row for action a gives the probability of each next state (the role of "
                "P_env). Their composition K(i,j) is the chance of moving from state i to state j in one transition. The probability of "
                "state 0 after n transitions starts at 1 and is updated by K each step."
            ),
            "prediction": "Switch to the changed tool and keep two transitions. Does the chance of being in state 0 go up or down, and by about how much?",
            "explanation": (
                "Equation (5.2) averages the tool's next-state law over the chooser's proposals. With two states the sum is small enough "
                "to do by hand: each row of K is the chooser's weights times the tool's rows. Repeating that one-step kernel is recurrence, "
                "and it settles at a long-run share that depends on both factors."
            ),
            "application": (
                "When a model is blamed or credited for a change in behavior, ask which factor changed. Here the chooser rows are identical in "
                "both cases, so every difference in the curves is a consequence of the tool, not of the model."
            ),
            "assumptions": (
                "Two states, two proposals, no permission or budget coordinate, and a tool law that depends on the state only through the proposal. "
                "If the next state also depends on something the state leaves out, such as a memory version, the composite kernel is not a "
                "valid description and more transitions will not repair it."
            ),
            "check": "With the default tool, what is the chance of state 0 after two transitions when the system starts in state 0?",
            "answer": "K(0,0) = 0.76 and K(1,0) = 0.3 x 0.9 + 0.7 x 0.2 = 0.41. After two steps: 0.76 x 0.76 + 0.24 x 0.41 = 0.5776 + 0.0984 = 0.676.",
            "provenance": "Constructed example: the laboratory's default chooser and tool matrices; the first composite row [0.76, 0.24] is the one worked in the lab, computed with its composite-kernel function.",
            "source_section": "The law the model does not contain",
            "source_anchor": "the-law-the-model-does-not-contain",
            "controls": [
                {"key": "tool", "label": "Tool", "values": ["default", "changed"], "default": "default",
                 "value_labels": ["Default tool", "Changed tool"]},
                {"key": "transitions", "label": "Number of transitions", "values": [1, 2, 3, 30], "default": 2},
            ],
            "function": "composite_kernel_picture",
        },
        {
            "id": "C05-D03",
            "title": "What an observation is worth",
            "question": "How many bits does the tool's report deliver, and does delivering them change the outcome?",
            "equations": [EQ_INFO],
            "symbols": (
                "Y is the hidden bit and O the tool's report. H(Y) is the uncertainty about Y in bits, 1 bit when both values are equally "
                "likely. H(Y | O) is the uncertainty left after seeing O. I(Y;O) is their difference: the bits the report delivers. The "
                "accuracy is the chance the report equals Y. Success is the chance of a correct final answer."
            ),
            "prediction": "At accuracy 0.90, does the information change if the run stops right after the observation? Does the success rate change?",
            "explanation": (
                "With a report that is right with probability a, the posterior on the reported value is a, so H(Y | O) is the entropy of "
                "a and I = 1 - H(Y | O). That number depends only on the tool. Whether it matters for the task depends on a different "
                "question: does a later choice read it? The two panels separate those two questions."
            ),
            "application": (
                "For every piece of information a system collects, name the decision it changes. If no decision changes, the collection "
                "is decoration, however many bits it carries."
            ),
            "assumptions": (
                "One hidden bit with equal prior, a symmetric tool, and the informed response law held at the book's values for every "
                "accuracy. That includes 0.50, where the report carries no information but the declared law still responds to it, "
                "because the law is held fixed by construction. Mutual information is "
                "symmetric and not causal, and it measures uncertainty removed, not usefulness."
            ),
            "check": "A tool is right with probability 0.75. How many bits does it deliver, and what is H(Y | O)?",
            "answer": "H(Y | O) = 0.25 x 2.000 + 0.75 x 0.415 = 0.500 + 0.311 = 0.811 bits, so I = 1 - 0.811 = 0.189 bits.",
            "provenance": "Constructed example: the chapter's tool with accuracy 0.90 (about 0.531 bits) and the blind and informed response laws it declares; other accuracies are values defined for the reader.",
            "source_section": "What an observation is worth",
            "source_anchor": "what-an-observation-is-worth",
            "controls": [
                {"key": "accuracy", "label": "Chance the tool reports the bit correctly", "values": [0.5, 0.75, 0.9, 1.0], "default": 0.9},
                {"key": "reaches", "label": "Does the report reach a later model call?", "values": ["stops", "reaches"], "default": "stops",
                 "value_labels": ["No, the run stops (tool, no recurrence)", "Yes, it enters the next context (connected, granted)"]},
            ],
            "function": "observation_picture",
        },
        {
            "id": "C05-D04",
            "title": "Recurrence multiplies",
            "question": "If every step is very likely to succeed, how long a task can still survive?",
            "equations": [EQ_PRODUCT],
            "symbols": (
                "A run is a sequence of states x_0 to x_T. P(x_{t+1} | x_t) is the probability of one step. Here every required step "
                "succeeds with the same conditional probability q given that all earlier steps succeeded, and any unrepaired failure ends "
                "the task. With one retry per step, q is the chance that at least one of two independent tries succeeds. The horizontal "
                "axis counts required steps."
            ),
            "prediction": "At per-step success 0.95 with no retry, is the chance of finishing 40 steps closer to 0.9, 0.5 or 0.1?",
            "explanation": (
                "Equation (5.5) says a run's probability is a product of one-step probabilities. With a constant conditional success q, "
                "n steps give q multiplied by itself n times, which falls fast even when q is close to 1. A repair step raises q itself, "
                "which is why retries and verifiers are the main response to the exponent."
            ),
            "application": (
                "Before promising a long unattended task, ask what the per-step success is after the controller's own detection and "
                "recovery, not for the model's average accuracy on isolated questions."
            ),
            "assumptions": (
                "Constant conditional success and independent retries that use the same budget coordinate (each retry costs budget the "
                "chain here does not track). If failures share a cause, such as bad evidence, a retry fails for the same reason and q "
                "improves less than shown. Marginal step accuracies alone do not justify this product."
            ),
            "check": "With per-step success 0.90 and one retry per step, what is the chance of finishing 2 steps?",
            "answer": "q = 1 - 0.10 x 0.10 = 0.99. Two steps: 0.99 x 0.99 = 0.9801.",
            "provenance": "Constructed example: the chapter's compounding values (0.99 over 40 steps is 0.669, 0.95 is 0.129), computed with the laboratory's chain function; the retry rule is a construction defined for the reader.",
            "source_section": "Recurrence multiplies",
            "source_anchor": "recurrence-multiplies",
            "controls": [
                {"key": "step_success", "label": "Per-step success before any retry", "values": [0.9, 0.95, 0.99, 0.999], "default": 0.99},
                {"key": "handling", "label": "Failure handling", "values": ["none", "retry"], "default": "none",
                 "value_labels": ["Any failure ends the task", "One independent retry per step"]},
            ],
            "function": "recurrence_picture",
        },
    ],
}

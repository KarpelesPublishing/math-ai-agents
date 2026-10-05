"""Chapter 5 reader: What the Model Becomes Inside an Agent.

Four demonstrations built on the chapter's six-assembly experiment, the state
(Equation 5.1), the composite transition law (Equation 5.2), merging states
(Equation 5.3), the value of an observation (Equation 5.4) and recurrence
(Equation 5.5). Demonstrations 2 and 4 call the laboratory's own computation
(math_ai_agents.chapters.ch05.evaluate), including the notebook's transfer
case, so the reader, the notebook and the chapter skill agree. Demonstrations 1
and 3 compute the chapter's closed forms directly. Every number is a
constructed teaching value; the defaults are the book's own worked numbers.
"""
import math
from functools import lru_cache

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

from math_ai_agents.chapters.ch05 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure

# The book's declared response laws (section "The fair experiment").
BOOK_TOOL = 0.90         # probability that the tool reports the hidden bit correctly
MATCH, OPPOSITE, STOP = 0.85, 0.10, 0.05   # informed response law
BOOK_REQUEST = 0.40      # probability that a blind context outputs `request`

EQ_STATE = r"x_t=(c_t,m_t,w_t,b_t)"
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
EQ_ABSTRACT = (r"\sum_{y:\kappa(y)=\bar y}P(y\mid x_1,a)"
               r"="
               r"\sum_{y:\kappa(y)=\bar y}P(y\mid x_2,a)")
EQ_INFO = r"I(Y;O)=H(Y)-H(Y\mid O)"
EQ_PRODUCT = r"\Pr(x_{0:T})=\Pr(x_0)\prod_{t=0}^{T-1}P(x_{t+1}\mid x_t)"
EQ_HORIZON = r"n = \log 0.5 / \log p"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


def trim(x, digits=3):
    """Number text without trailing zeros (0.4 not 0.400), for written sums."""
    text = fmt(x, digits)
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text


def informed_correct(accuracy):
    """Probability an informed answer is correct when the tool is right with probability `accuracy`."""
    return accuracy * MATCH + (1 - accuracy) * OPPOSITE


# Demonstration 1: the six assemblies, decomposed, and the budget that pays for the second call

ROWS = [
    "1 Model only",
    "2 Memory, no reader",
    "3 Tool, no recurrence",
    "4 Recurrence, blind",
    "5 Connected, granted",
    "6 Connected, denied",
]
SEGMENTS = ["Correct on the first call", "Correct after the request", "Wrong answer", "Stopped with no answer"]
SEG_COLORS = [PALETTE["teal"], PALETTE["olive"], PALETTE["terracotta"], PALETTE["light"]]
SEG_HATCH = ["", "", "", "//"]


def assembly_parts(request, rejection, calls):
    """For each row: [correct first call, correct after the request, wrong, stopped]; the four parts sum to one."""
    blind = (1 - request) / 2
    stops = [blind, 0.0, blind, request]
    if calls == 1:
        # A request on the last call terminates without an answer: no row can use a second call.
        return [list(stops) for _ in range(6)]
    second_blind = [blind, request * blind, blind + request * blind, request * request]
    wrong_informed = BOOK_TOOL * OPPOSITE + (1 - BOOK_TOOL) * MATCH
    connected = [blind, request * informed_correct(BOOK_TOOL), blind + request * wrong_informed, request * STOP]
    denied = list(stops) if rejection == "stop" else list(second_blind)
    return [list(stops), list(stops), list(stops), second_blind, connected, denied]


def six_assemblies_picture(request=0.4, rejection="stop", calls=2):
    request, calls = float(request), int(calls)
    parts = assembly_parts(request, rejection, calls)
    scores = [p[0] + p[1] for p in parts]
    blind = scores[0]
    informed = informed_correct(BOOK_TOOL)
    wrong = parts[4][2]
    stopped = parts[4][3]
    fig, ax = new_figure(height=4.5)
    y = np.arange(6)[::-1]
    for yi, row in zip(y, parts):
        left = 0.0
        for k, value in enumerate(row):
            ax.barh(yi, value, left=left, height=0.62, color=SEG_COLORS[k], hatch=SEG_HATCH[k], edgecolor="white" if k < 3 else PALETTE["grey"],
                    linewidth=0.8)
            left += value
        ax.text(1.015, yi, fmt(row[0] + row[1], 3), va="center", ha="left", fontsize=11, color=PALETTE["ink"])
    ax.axvline(blind, color=PALETTE["ink"], linestyle="dashed", linewidth=1.2)
    ax.set_yticks(y, ROWS)
    ax.set_xlim(0, 1.13)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel("Probability of each outcome (the number at the end is the chance of a correct answer)")
    ax.set_ylabel("Assembly (frozen model in every row)")
    ax.grid(axis="y", alpha=0)
    policy = "stops with no answer" if rejection == "stop" else "makes a second blind call"
    if calls == 1:
        ax.set_title(f"One call allowed; blind call requests {fmt(request, 2)} of the time", fontsize=11.5)
    else:
        ax.set_title(f"Two calls; blind call requests {fmt(request, 2)}; denial {policy}", fontsize=11.5)
    fig.legend(handles=[Patch(facecolor=c, edgecolor=PALETTE["grey"] if i == 3 else "white", hatch=h, label=s)
                        for i, (c, h, s) in enumerate(zip(SEG_COLORS, SEG_HATCH, SEGMENTS))]
               + [Line2D([0], [0], color=PALETTE["ink"], linestyle="dashed", linewidth=1.2, label="Model-only rate (row 1)")],
               loc="outside lower center", ncol=3, fontsize=10.5, frameon=False)
    metrics = {ROWS[i][2:]: fmt(scores[i], 3) for i in range(6)}
    metrics["Row 5 minus row 1"] = fmt(scores[4] - blind, 3)
    metrics["Row 5 wrong answer"] = fmt(wrong, 3)
    metrics["Row 5 stops with no answer"] = fmt(stopped, 3)
    metrics["Calls allowed"] = str(calls)
    if calls == 1:
        denial = ("With one call allowed, a request on the last call ends the run with no answer, so there is no budget for a second call "
                  f"and every row scores the blind rate {fmt(blind, 3)}. The memory, the tool and the loop need budget to matter.")
    elif rejection == "stop":
        denial = (f"Row 6 stops at the rejection, so it scores the blind rate {fmt(blind, 3)}, exactly row 1. "
                  "The tool was never reached, so one revoked grant removes the whole gain.")
    else:
        denial = (f"With a second blind call after the rejection, row 6 scores {fmt(blind, 3)} + {fmt(request, 2)} x "
                  f"{fmt(blind, 3)} = {fmt(scores[5], 3)}, the same as row 4, because a denied tool adds no information.")
    if calls == 1:
        core = (f"A blind answer is correct with probability (1 - {fmt(request, 2)}) / 2 = {fmt(blind, 3)}, whatever the hidden bit is. "
                f"A request ends the run with probability {fmt(request, 2)}. ")
    else:
        core = (
            f"A blind answer is correct with probability (1 - {fmt(request, 2)}) / 2 = {fmt(blind, 3)}, whatever the hidden bit is. "
            f"Row 4 = {fmt(blind, 3)} + {fmt(request, 2)} x {fmt(blind, 3)} = {fmt(scores[3], 3)}. "
            f"An informed answer is correct with probability 0.90 x 0.85 + 0.10 x 0.10 = {fmt(informed, 3)}, so row 5 = "
            f"{fmt(blind, 3)} + {fmt(request, 2)} x {fmt(informed, 3)} = {fmt(scores[4], 3)}. "
            f"Rows 2 and 3 hold real components that no later call reads, so they stay at {fmt(blind, 3)}. ")
    interpretation = (
        f"{core}{denial} Check for row 5: correct {fmt(scores[4], 3)} + wrong {fmt(wrong, 3)} + stopped {fmt(stopped, 3)} = "
        f"{fmt(scores[4] + wrong + stopped, 3)}."
    )
    steps = [
        f"Blind call: answer 0 and answer 1 each have probability (1 - {fmt(request, 2)}) / 2 = {fmt(blind, 3)}; request has {fmt(request, 2)}.",
        f"Either answer is right half the time, so a blind answer is correct with probability {fmt(blind, 3)}.",
    ]
    if calls == 2:
        steps += [
            f"Row 4: the request starts a second blind call: {fmt(blind, 3)} + {fmt(request, 2)} x {fmt(blind, 3)} = {fmt(scores[3], 3)}.",
            f"Informed answer: 0.90 x 0.85 + 0.10 x 0.10 = {fmt(informed, 3)}; row 5 = {fmt(blind, 3)} + {fmt(request, 2)} x {fmt(informed, 3)} = {fmt(scores[4], 3)}.",
            f"Rows 1 to 3 cannot rescue a request, so each scores {fmt(blind, 3)}; row 6 is row 5 with the grant revoked.",
        ]
    else:
        steps += [
            "A request on the last call terminates without an answer, so a second call is not available in any row.",
            f"Every row therefore scores {fmt(blind, 3)}; the other {fmt(request, 2)} of runs stop with no answer.",
        ]
    alt = ("Six horizontal stacked bars, one per assembly, split into correct on the first call, correct after the request, wrong answer and "
           "stopped with no answer. " + ("With one call allowed all six bars are identical. " if calls == 1 else
           f"Rows 1 to 3 end at {fmt(blind, 3)} correct, row 4 at {fmt(scores[3], 3)}, row 5 at {fmt(scores[4], 3)} and row 6 at {fmt(scores[5], 3)}. ")
           + "A dashed line marks the model-only rate.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: the composite kernel (laboratory computation), including the notebook's transfer case

CHOOSER = {
    "default": [[0.8, 0.2], [0.3, 0.7]],
    "changed": [[0.8, 0.2], [0.3, 0.7]],
    "transfer": [[1.0, 0.0], [0.0, 1.0]],
}
TOOLS = {
    "default": [[0.9, 0.1], [0.2, 0.8]],
    "changed": [[0.6, 0.4], [0.1, 0.9]],
    "transfer": [[0.7, 0.3], [0.4, 0.6]],
}
INITIAL = {"default": [1, 0], "changed": [1, 0], "transfer": [0.5, 0.5]}
SYSTEM_LABELS = {"default": "default tool", "changed": "changed tool", "transfer": "transfer case"}
KERNEL_HORIZON = 30


@lru_cache(maxsize=None)
def lab_kernel(system):
    """Composite kernel and state-0 occupancy from the laboratory's evaluate()."""
    out = evaluate({
        "step_success": 0.99, "steps": KERNEL_HORIZON, "conditional_success": [0.99] * KERNEL_HORIZON,
        "chooser": CHOOSER[system], "tool": TOOLS[system], "initial": INITIAL[system],
    })
    occupancy = [s for s in out["series"] if s["label"] == "state zero occupancy"][0]["y"]
    return out["metrics"]["composite_kernel"], tuple(occupancy)


def composite_kernel_picture(system="default", transitions=2):
    kernel, occupancy = lab_kernel(system)
    n = int(transitions)
    k00, k10 = kernel[0][0], kernel[1][0]
    long_run = k10 / (1 - k00 + k10)
    after = occupancy[n]
    start0 = INITIAL[system][0]
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    t = np.arange(KERNEL_HORIZON + 1)
    order = [s for s in SYSTEM_LABELS if s != system] + [system]
    for other in order:
        _, occ = lab_kernel(other)
        if other == system:
            left.plot(t, occ, color=PALETTE["teal"], linewidth=2.4, zorder=3)
        else:
            left.plot(t, occ, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4, zorder=2)
    left.plot([n], [after], "o", color=PALETTE["terracotta"], markersize=9, zorder=5)
    # Name every curve at its right-hand end, nudged apart so the three names never meet.
    ends = {s: lab_kernel(s)[1][KERNEL_HORIZON] for s in SYSTEM_LABELS}
    names = sorted(ends, key=lambda s: ends[s])
    for rank, s in enumerate(names):
        label_point(left, KERNEL_HORIZON, ends[s], SYSTEM_LABELS[s] + (" (chosen)" if s == system else ""),
                    color=PALETTE["teal"] if s == system else PALETTE["grey"], dx=-4, dy=(-9 if rank < 2 else 9),
                    ha="right", va="top" if rank < 2 else "bottom").set_bbox(BOX)
    left.set_xlim(-0.5, KERNEL_HORIZON + 1)
    left.set_ylim(0, 1.05)
    left.set_xlabel("Number of transitions")
    left.set_ylabel("Probability of being in state 0")
    left.set_title(f"Start with {fmt(start0, 2)} in state 0; dot marks {n} transition" + ("" if n == 1 else "s"), fontsize=11.5)

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

    c = CHOOSER[system]
    t0, t1 = TOOLS[system]
    chooser_text = f"[{fmt(c[0][0], 2)}, {fmt(c[0][1], 2)}] and [{fmt(c[1][0], 2)}, {fmt(c[1][1], 2)}]"
    metrics = {
        "Composite row 0": f"[{fmt(kernel[0][0], 2)}, {fmt(kernel[0][1], 2)}]",
        "Composite row 1": f"[{fmt(kernel[1][0], 2)}, {fmt(kernel[1][1], 2)}]",
        f"State 0 after {n} transition" + ("" if n == 1 else "s"): fmt(after, 3),
        "Long-run state 0": fmt(long_run, 3),
        "Chooser rows": chooser_text + (" (unchanged)" if system != "transfer" else " (identity: the chooser keeps its state)"),
    }
    row0 = (f"K(0,0) = {fmt(c[0][0], 1)} x {fmt(t0[0], 1)} + {fmt(c[0][1], 1)} x {fmt(t1[0], 1)} = {fmt(kernel[0][0], 2)} and "
            f"K(0,1) = {fmt(c[0][0], 1)} x {fmt(t0[1], 1)} + {fmt(c[0][1], 1)} x {fmt(t1[1], 1)} = {fmt(kernel[0][1], 2)}")
    row1 = f"K(1,0) = {fmt(c[1][0], 1)} x {fmt(t0[0], 1)} + {fmt(c[1][1], 1)} x {fmt(t1[0], 1)} = {fmt(kernel[1][0], 2)}"
    if system == "transfer":
        step1 = f"{fmt(start0, 1)} x {fmt(k00, 2)} + {fmt(1 - start0, 1)} x {fmt(k10, 2)} = {fmt(occupancy[1], 3)}"
        mu1 = occupancy[1]
        step2 = f"{fmt(mu1, 3)} x {fmt(k00, 2)} + {fmt(1 - mu1, 3)} x {fmt(k10, 2)} = {fmt(occupancy[2], 3)}"
    else:
        step1 = f"1 x {fmt(k00, 2)} + 0 x {fmt(k10, 2)} = {fmt(k00, 2)}"
        mu2 = k00 * k00 + (1 - k00) * k10
        step2 = f"{fmt(k00, 2)} x {fmt(k00, 2)} + {fmt(1 - k00, 2)} x {fmt(k10, 2)} = {fmt(mu2, 3)}"
    if system == "transfer":
        closing = ("With the identity chooser the kernel equals the tool, so the system is the tool's own recurrence started half in each state.")
    else:
        closing = ("Only the tool differs between the default and changed systems; the chooser's probabilities are identical, yet the "
                   "recurrent system the chooser lives in is different.")
    interpretation = (
        f"Each row of K mixes the tool's rows, weighted by the chooser's probabilities: {row0}; {row1}. "
        f"Starting with probability {fmt(start0, 2)} in state 0, the chance of state 0 after one transition is {step1}, after two it is {step2}. "
        f"After {n} it is {fmt(after, 3)}, and it settles near {fmt(long_run, 3)}. {closing}"
    )
    steps = [
        f"Chooser row 0 = [{fmt(c[0][0], 2)}, {fmt(c[0][1], 2)}]; tool rows [{fmt(t0[0], 1)}, {fmt(t0[1], 1)}] and [{fmt(t1[0], 1)}, {fmt(t1[1], 1)}].",
        f"{row0}.",
        f"{row1}; the second entry of row 1 is 1 - {fmt(kernel[1][0], 2)} = {fmt(kernel[1][1], 2)}.",
        f"After one transition: {step1}.",
        f"After two transitions: {step2}.",
        f"After {n}: {fmt(after, 3)}; the long-run share is K(1,0) / (1 - K(0,0) + K(1,0)) = {fmt(long_run, 3)}.",
    ]
    alt = (f"Left: the chance of being in state 0 against the number of transitions for the default tool, the changed tool and the transfer case, "
           f"with the {SYSTEM_LABELS[system]} highlighted and its value {fmt(after, 3)} after {n} transition{'s' if n != 1 else ''} marked. "
           f"Right: the two by two composite kernel with rows {fmt(kernel[0][0], 2)}, {fmt(kernel[0][1], 2)} and {fmt(kernel[1][0], 2)}, {fmt(kernel[1][1], 2)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: what an observation is worth, and what a memory may drop

def entropy_bits(p):
    """Binary entropy in bits, with 0 log 0 taken as 0."""
    if p <= 0 or p >= 1:
        return 0.0
    return -p * math.log2(p) - (1 - p) * math.log2(1 - p)


PATH_NAMES = {
    "stops": "Report, then the run stops",
    "dropped": "Report dropped by memory",
    "reaches": "Report kept and read",
}


def observation_picture(accuracy=0.9, reaches="stops"):
    a = float(accuracy)
    h_after = entropy_bits(a)
    info = 1 - h_after
    informed = informed_correct(a)
    blind = (1 - BOOK_REQUEST) / 2
    second_blind = blind + BOOK_REQUEST * blind
    connected_success = blind + BOOK_REQUEST * informed
    outcomes = {"stops": blind, "dropped": second_blind, "reaches": connected_success}
    success = outcomes[reaches]
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    grid = np.linspace(0.5, 1.0, 101)
    left.plot(grid, [1 - entropy_bits(x) for x in grid], color=PALETTE["navy"], linewidth=2)
    left.plot([a], [info], "o", color=PALETTE["terracotta"], markersize=9)
    label_point(left, a, info, f"{fmt(info, 3)} bits", color=PALETTE["terracotta"], dx=-10 if a > 0.7 else 10,
                dy=8, ha="right" if a > 0.7 else "left", va="bottom")
    left.set_xlim(0.48, 1.02)
    left.set_ylim(-0.04, 1.12)
    left.set_xlabel("Chance the tool reports the hidden bit correctly")
    left.set_ylabel("Information about the bit (bits)")
    left.set_title("What the observation delivers", fontsize=11.5)

    names = ["Model only", PATH_NAMES["stops"], PATH_NAMES["dropped"], PATH_NAMES["reaches"]]
    values = [blind, blind, second_blind, connected_success]
    keys = [None, "stops", "dropped", "reaches"]
    y = np.arange(4)[::-1]
    for yi, v, key in zip(y, values, keys):
        chosen = key == reaches
        right.barh(yi, v, height=0.58, color=PALETTE["teal"] if chosen else PALETTE["light"], edgecolor=PALETTE["ink"] if chosen else PALETTE["grey"],
                   linewidth=1.4 if chosen else 0.8, hatch="//" if (key == "dropped") else "")
        right.text(v + 0.012, yi, fmt(v, 3), va="center", fontsize=11, color=PALETTE["ink"])
    right.axvline(blind, color=PALETTE["grey"], linestyle="dashed", linewidth=1.2)
    right.set_yticks(y, names)
    right.set_xlim(0, 0.8)
    right.set_xlabel("Probability of a correct answer")
    right.set_ylabel("What happens to the report")
    right.set_title("Same report, three outcomes (chosen in teal)", fontsize=11.5)
    right.grid(axis="y", alpha=0)

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
    if reaches == "reaches":
        decision = (f"The report is kept and enters a later call: informed answer correct = {trim(a, 2)} x 0.85 + {trim(1 - a, 2)} x 0.10 = "
                    f"{fmt(informed, 4)}, so success = {fmt(blind, 2)} + 0.40 x {fmt(informed, 4)} = {fmt(success, 3)}. Keeping the two "
                    "states 'report says 0' and 'report says 1' apart is what lets the model answer with the report.")
        if a <= 0.5 + 1e-12:
            decision += (" The tool delivers 0 bits, yet success still rises. That rise comes from the declared informed "
                         "response law, which answers 95 percent of the time instead of 60 percent, not from information: "
                         "bits and score are different measures.")
    elif reaches == "dropped":
        decision = (f"A memory that drops the report merges the states 'report says 0' and 'report says 1'. Equation (5.3) needs equal chances "
                    f"of entering each abstract class, but the chance of the class 'answer 0' would be {MATCH:.2f} from one state and {OPPOSITE:.2f} from the other "
                    f"if the two states were kept apart, so merging them is not exact. The second call is blind: success = {fmt(blind, 2)} + 0.40 x {fmt(blind, 2)} = {fmt(success, 3)}, "
                    f"the blind second call of row 4, whatever the accuracy {fmt(a, 2)} of the tool.")
    else:
        decision = (f"The run stops after the observation, so no choice consumes the bits: success = {fmt(blind, 2)} + 0.40 x 0 = "
                    f"{fmt(success, 2)}, the model-only rate. ")
        if info > 5e-4:
            decision += "The information is real and its decision value here is zero."
        else:
            decision += "The report carries no information, so its decision value is zero as well."
    interpretation = f"{info_line} {decision}"
    steps = [
        f"The tool reports the bit correctly with probability {trim(a, 2)}, so after a report the posterior on the reported value is {trim(a, 2)}.",
        f"{entropy_sum}.",
        f"I(Y;O) = H(Y) - H(Y | O) = 1 - {fmt(h_after, 3)} = {fmt(info, 3)} bits.",
    ]
    if reaches == "reaches":
        steps += [f"Informed answer correct = {trim(a, 2)} x 0.85 + {trim(1 - a, 2)} x 0.10 = {fmt(informed, 4)}.",
                  f"Success = {fmt(blind, 2)} + 0.40 x {fmt(informed, 4)} = {fmt(success, 3)}."]
    elif reaches == "dropped":
        steps += [f"The report is dropped, so the second call sees a blind context: it answers correctly with probability {fmt(blind, 2)}.",
                  f"Success = {fmt(blind, 2)} + 0.40 x {fmt(blind, 2)} = {fmt(success, 3)}."]
    else:
        steps += [f"The run stops, so no later call reads the report: success = {fmt(blind, 2)} + 0.40 x 0 = {fmt(success, 2)}."]
    alt = (f"Left: the information a report delivers against the tool's accuracy, with {fmt(info, 3)} bits marked at accuracy {fmt(a, 2)}. "
           f"Right: four horizontal bars of the chance of a correct answer: model only {fmt(blind, 3)}, report then stop {fmt(blind, 3)}, "
           f"report dropped by memory {fmt(second_blind, 3)} and report kept and read {fmt(connected_success, 3)}; the chosen bar is highlighted.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: recurrence multiplies, with a shared cause and the notebook's transfer case

STEPS = 100
HEADLINE = 40
TRANSFER_RATES = [0.9, 0.8, 0.7]
CASE_P = {"p95": 0.95, "p99": 0.99, "p999": 0.999}
CASE_NAMES = {"p95": "per-step 0.95", "p99": "per-step 0.99", "p999": "per-step 0.999", "transfer": "transfer: rates 0.9, 0.8, 0.7"}


@lru_cache(maxsize=None)
def lab_chain(q):
    """Independent trajectory success and shared-condition success for i = 0..100 steps, from the laboratory's evaluate()."""
    out = evaluate({
        "step_success": q, "steps": STEPS, "conditional_success": [q] * STEPS,
        "chooser": [[1, 0], [0, 1]], "tool": [[1, 0], [0, 1]], "initial": [1, 0],
    })
    independent = [s for s in out["series"] if s["label"] == "independent trajectory success"][0]["y"]
    shared = [s for s in out["series"] if s["label"] == "shared condition trajectory success"][0]["y"]
    if not math.isclose(out["metrics"]["chain_rule_all_success"], independent[-1], rel_tol=1e-9):
        raise AssertionError("laboratory chain rule disagrees with the independent curve")
    return tuple(independent), tuple(shared)


@lru_cache(maxsize=None)
def lab_transfer():
    """The notebook's transfer case: conditional rates 0.9, 0.8, 0.7 and step marginal 0.9, three steps."""
    out = evaluate({
        "step_success": 0.9, "steps": 3, "conditional_success": TRANSFER_RATES,
        "chooser": [[1, 0], [0, 1]], "tool": [[0.7, 0.3], [0.4, 0.6]], "initial": [0.5, 0.5],
    })
    return out["metrics"]["chain_rule_all_success"], out["metrics"]["independent_all_success"], out["metrics"]["shared_condition_all_success"]


def effective_step(p, handling):
    return 1 - (1 - p) ** 2 if handling == "retry" else p


def step_text(q):
    """A per-step probability for written arithmetic, with enough digits to tell it from 1."""
    return trim(q, 6 if q > 0.99995 else 4)


def horizon_text(q):
    half = math.log(0.5) / math.log(q)
    return f"{fmt(half, 0 if half >= 100 else 1)} steps"


LINESTYLE = {"none": "-", "retry": "-.", "shared": ":"}
HANDLING_NAMES = {"none": "independent steps", "retry": "one retry per step", "shared": "one shared cause"}


def recurrence_picture(case="p99", handling="none"):
    if case == "transfer":
        return transfer_picture(handling)
    p = CASE_P[case]
    q = effective_step(p, "retry" if handling == "retry" else "none")
    plain, shared = lab_chain(p)
    retry, _ = lab_chain(effective_step(p, "retry"))
    curves = {"none": plain, "retry": retry, "shared": shared}
    fig, ax = new_figure(height=4.3)
    x = np.arange(STEPS + 1)
    for key in ("none", "retry", "shared"):
        if key == handling:
            continue
        ax.plot(x, curves[key], color=PALETTE["grey"], linestyle=LINESTYLE[key], linewidth=1.8)
    ax.plot(x, curves[handling], color=PALETTE["teal"], linewidth=2.6, linestyle=LINESTYLE[handling])
    value = curves[handling][HEADLINE]
    ax.plot([HEADLINE], [value], "o", color=PALETTE["terracotta"], markersize=9)
    ax.axvline(HEADLINE, color=PALETTE["light"], linewidth=1.2, zorder=0)
    # A key to the right of the curves names each one (the curves end close together, so end labels would collide).
    handles = [Line2D([0], [0], color=PALETTE["teal"] if key == handling else PALETTE["grey"], linewidth=2.6 if key == handling else 1.8,
                      linestyle=LINESTYLE[key]) for key in ("none", "retry", "shared")]
    ax.legend(handles, [HANDLING_NAMES[k] + (" (chosen)" if k == handling else "") for k in ("none", "retry", "shared")],
              loc="center right", fontsize=10.5, frameon=False)
    # Below the curve only for independent steps: with a retry the independent curve lies just below, so the label goes above.
    below = value > 0.9 and handling == "none"
    label_point(ax, HEADLINE, value, f"step 40: {fmt(value, 3)}", color=PALETTE["terracotta"],
                dx=8, dy=-8 if below else 8, ha="left", va="top" if below else "bottom")
    ax.set_xlim(0, 215)
    ax.set_xticks(range(0, STEPS + 1, 20))
    ax.set_ylim(-0.02, 1.12)
    ax.set_xlabel("Number of required steps")
    ax.set_ylabel("Probability every step so far succeeded")
    ax.set_title(f"Per-step success {fmt(p, 3)} before any retry", fontsize=11.5)
    if handling == "shared":
        half_text = f"does not fall: stays at {fmt(p, 3)}"
    else:
        half_text = horizon_text(q) + (" (beyond the plotted 100)" if math.log(0.5) / math.log(q) > STEPS else "")
    metrics = {
        "Conditional success per step used": fmt(q, 6 if q > 0.99995 else 4) if handling != "shared" else f"{fmt(p, 3)} marginal",
        "After 10 steps": fmt(curves[handling][10], 3),
        "After 40 steps": fmt(value, 3),
        "After 100 steps": fmt(curves[handling][100], 3),
        "Steps until success falls below 0.5": half_text,
    }
    shown40 = fmt(value, 5 if value > 0.9995 else 3)
    factors = f"{step_text(q)} x {step_text(q)} x ... x {step_text(q)} (40 factors) = {shown40}"
    if handling == "shared":
        interpretation = (
            f"Suppose one shared condition, good with probability {fmt(p, 3)}, decides every step: if it is bad the first step fails, and if it is "
            f"good all steps succeed. Each step still succeeds with marginal probability {fmt(p, 3)}, but all-step success stays {fmt(p, 3)} at "
            f"10, 40 and 100 steps, while independent steps give {step_text(p)} x {step_text(p)} x ... x {step_text(p)} (40 factors) = {fmt(plain[HEADLINE], 3)} at 40 steps. The marginal rate alone does not "
            f"determine completion; Equation (5.5) needs the conditional step probabilities. This is a constructed joint law, not a claim about real agents."
        )
        step_lines = [
            f"One shared condition is good with probability {fmt(p, 3)}; every step succeeds exactly when it is good.",
            f"Each step then has marginal success {fmt(p, 3)}, the same as in the independent case.",
            f"All-step success is {fmt(p, 3)} at 10, 40 and 100 steps.",
            f"Independent steps at 40 steps: {step_text(p)} x ... x {step_text(p)} (40 factors) = {fmt(plain[HEADLINE], 3)}.",
        ]
    else:
        if handling == "retry":
            step_line = (f"With one independent retry, a step fails only if both tries fail: q = 1 - {trim(1 - p, 3)} x {trim(1 - p, 3)} = "
                         f"{trim(q, 6)}. ")
        else:
            step_line = f"Any failed step ends the task, so each step must succeed, q = {step_text(q)}. "
        interpretation = (
            f"{step_line}Equation (5.5) multiplies one-step probabilities along the run: two steps give {step_text(q)} x {step_text(q)} = "
            f"{trim(q * q, 6)}, and forty steps give {factors}. The success curve falls below one half after about "
            f"{horizon_text(q)}, which is n = log 0.5 / log {step_text(q)}. This is the limit of this declared chain, not of agents in general."
        )
        step_lines = [
            step_line.strip(),
            f"Two steps: {step_text(q)} x {step_text(q)} = {trim(q * q, 6)}.",
            f"Forty steps: {step_text(q)}^40 = {shown40}.",
            f"Half-success horizon: n = log 0.5 / log {step_text(q)} = {horizon_text(q)}.",
        ]
    alt = (f"Success probability against the number of required steps up to 100 for independent steps, one retry per step and one shared cause, "
           f"at per-step success {fmt(p, 3)}; the chosen curve is highlighted and its value {fmt(value, 3)} at 40 steps is marked.")
    return fig, metrics, interpretation, {"alt": alt, "steps": step_lines}


def transfer_picture(handling):
    chain, indep, shared_value = lab_transfer()
    rates = TRANSFER_RATES
    rr = [1 - (1 - c) ** 2 for c in rates]
    cum_none = np.concatenate([[1.0], np.cumprod(rates)])
    cum_retry = np.concatenate([[1.0], np.cumprod(rr)])
    cum_indep = np.array([0.9 ** i for i in range(4)])
    cum_shared = np.array([1.0, 0.9, 0.9, 0.9])
    chosen = {"none": cum_none, "retry": cum_retry, "shared": cum_shared}[handling]
    fig, ax = new_figure(height=4.3)
    x = np.arange(4)
    series = [
        ("three steps at 0.9 each, independent " + fmt(cum_indep[3], 3), cum_indep, PALETTE["grey"], (0, (5, 3)), "s", "retry_off"),
        ("shared cause " + fmt(cum_shared[3], 3), cum_shared, PALETTE["gold"], ":", "D", "shared"),
        ("chain rule " + fmt(cum_none[3], 3), cum_none, PALETTE["navy"], "-", "o", "none"),
        ("one retry per step " + fmt(cum_retry[3], 3), cum_retry, PALETTE["olive"], "-.", "^", "retry"),
    ]
    handles = []
    for name, ys, color, ls, marker, key in series:
        chosen_now = key == handling
        ax.plot(x, ys, color=PALETTE["teal"] if chosen_now else color, linestyle=ls, linewidth=2.8 if chosen_now else 1.6, marker=marker,
                markersize=8 if chosen_now else 6)
        handles.append(Line2D([0], [0], color=PALETTE["teal"] if chosen_now else color, linestyle=ls, marker=marker,
                              linewidth=2.8 if chosen_now else 1.6))
    ax.plot([3], [chosen[3]], "o", color=PALETTE["terracotta"], markersize=11, zorder=6)
    ax.legend(handles, [n + (" (chosen)" if k == handling else "") for n, _, _, _, _, k in series], loc="lower left", fontsize=10.5, frameon=False)
    ax.set_xlim(-0.1, 3.2)
    ax.set_xticks([0, 1, 2, 3])
    ax.set_ylim(0.3, 1.12)
    ax.set_xlabel("Number of required steps (transfer case, three steps)")
    ax.set_ylabel("Probability every step so far succeeded")
    ax.set_title("Conditional rates 0.9, 0.8, 0.7 (marginal 0.9)", fontsize=11.5)
    metrics = {
        "Chain rule with rates 0.9, 0.8, 0.7": fmt(chain, 3),
        "A different system: three independent steps each at 0.9": fmt(indep, 3),
        "Shared cause, marginal 0.9": fmt(shared_value, 3),
        "One retry per step on the rates": fmt(cum_retry[3], 4),
        "After 3 steps with this handling": fmt(chosen[3], 4 if handling == "retry" else 3),
    }
    base = ("Chain rule: 0.9 x 0.8 x 0.7 = " + fmt(chain, 3) + ". A different system, three independent steps that each succeed with probability 0.9, gives 0.9 x 0.9 x 0.9 = " + fmt(indep, 3) +
            ", and one shared cause with marginal 0.9 gives " + fmt(shared_value, 3) + ". The three answer different joint laws, so the marginal 0.9 does not fix the result. ")
    if handling == "retry":
        extra = ("With one independent retry on each step the conditional rates become 1 - 0.1 x 0.1 = 0.99, 1 - 0.2 x 0.2 = 0.96 and "
                 f"1 - 0.3 x 0.3 = 0.91, whose product is 0.99 x 0.96 x 0.91 = {fmt(cum_retry[3], 4)}.")
    elif handling == "shared":
        extra = "Under the shared cause a failure never recovers and a success never fails later, so completion stays at 0.9 whatever the length."
    else:
        extra = "These conditional rates are inputs: each is the chance of success given that every earlier step succeeded."
    interpretation = base + extra
    steps = [
        "Conditional rates: 0.9 for step 1, 0.8 for step 2 given step 1, 0.7 for step 3 given steps 1 and 2.",
        f"Chain rule: 0.9 x 0.8 x 0.7 = {fmt(chain, 3)}.",
        f"A different system, three independent steps each at 0.9: 0.9 x 0.9 x 0.9 = {fmt(indep, 3)}.",
        f"Shared cause with marginal 0.9: {fmt(shared_value, 3)}.",
        f"One retry per step: 0.99 x 0.96 x 0.91 = {fmt(cum_retry[3], 4)}.",
    ]
    alt = ("Cumulative success probability over three steps: the chain rule with rates 0.9, 0.8 and 0.7 ends at 0.504, a different system of three independent steps "
           "each at 0.9 ends at 0.729, a shared cause at 0.9, and one retry per step at about 0.865; the chosen handling is highlighted.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 5,
    "title": "What the Model Becomes Inside an Agent",
    "subtitle": "Hold the model still, change what surrounds it, and the system's behavior changes. The chapter shows why with a small constructed experiment.",
    "summary": (
        "These four demonstrations follow the chapter's frozen-model experiment. First, six assemblies around one unchanged model "
        "give different success rates, and the budget decides whether a second call exists. Second, a fixed chooser and a changed tool "
        "produce different recurrent systems, with the notebook's transfer case alongside. Third, an observation is measured in bits and "
        "compared with what it changes, and a memory that drops it fails the test for merging states. Fourth, a run's probability is a "
        "product, so small per-step failures compound and a shared cause breaks the product."
    ),
    "ask_skill": {
        "prompt": (
            "Help me write the state my agent carries between calls (context, memory, world, budget), name the decision that each piece of "
            "information I collect is supposed to change, and compute the probability that a required chain of n steps completes from "
            "the conditional success rates I have."
        ),
    },
    "demos": [
        {
            "id": "C05-D01",
            "title": "Six assemblies around one frozen model",
            "question": "If the model never changes, how can six assemblies of it succeed at different rates, and what does the budget have to do with it?",
            "equations": [EQ_INFORMED, EQ_STATE],
            "symbols": (
                "A blind call is a model call that has not seen the tool's result. Its request probability is the share of blind "
                "calls that output request instead of an answer; the rest is split equally between the two answers. The hidden bit "
                "Y is 0 or 1 with equal chance. The tool reports Y correctly with probability 0.90. In a context that contains the "
                "report, the model answers with the reported bit with probability 0.85, with the other bit with probability 0.10, "
                "and outputs request with probability 0.05. A success is a correct final answer. In the state x_t = (c_t, m_t, w_t, b_t), c is "
                "the context the model sees, m the retained memory, w the world and b the remaining budget; here b is the number of calls left."
            ),
            "prediction": "Leave the request probability at 0.40 and change denial to a second blind call. Which bar moves, and to what value?",
            "prediction_options": [
                "Row 6 rises from 0.300 to 0.420, the value of row 4",
                "Row 5 falls from 0.610 to 0.420",
                "No bar moves, because denial removes the tool either way",
            ],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "Row 6 becomes 0.30 + 0.40 x 0.30 = 0.42, the same as row 4: a denied tool adds no information, only a second blind try.",
                "incorrect": "Choose 'Makes a second blind call' with two calls allowed: only row 6 moves, from 0.300 to 0.420, because a second blind call rescues some requests but the denied tool adds no information.",
            },
            "explanation": (
                "A blind answer is right about as often as it is wrong, whatever the hidden bit. Rows 2 and 3 add a memory and a tool, "
                "but no later call reads their output, so they cannot move the score; the stacked bars show that no part of their runs is "
                "rescued after the request. Row 4 adds a second blind call and row 5 an informed one, so both gain only through the requests "
                "they rescue. Row 6 is row 5 with one grant revoked. Memory is what row 2 supplies, the world is what the tool reads in row 5, and the "
                "budget is what pays for row 4's second call: with one call allowed, every row falls to the blind rate."
            ),
            "application": (
                "When someone says an agent is better because it has memory or tools, ask which later decision reads their output. "
                "A component that sits on no path from the model's output to the outcome contributes exactly zero."
            ),
            "assumptions": (
                "At most two model calls, a tool that is either granted or denied, and the response laws above, which hold in every "
                "row. The six bars are assembly comparisons, not a matched factorial design: row 5 also adds recurrence, so the rows do not "
                "identify a memory and tool interaction. The rejection rule matters: if denial "
                "sends the run to a second blind call, row 6 equals row 4, not row 1. Nothing here says deployed effect sizes look like these. "
                "The one-call state is the chapter's own rule (a request on the last call terminates) applied to a smaller budget."
            ),
            "check": "If a blind call requested 0.60 of the time, what would the fully connected assembly (row 5) score?",
            "answer": "Blind rate = (1 - 0.60) / 2 = 0.20. Row 5 = 0.20 + 0.60 x 0.775 = 0.20 + 0.465 = 0.665.",
            "provenance": "Constructed example: the chapter's six-assembly experiment; the default 0.40 request probability gives the book's values 0.30, 0.42 and 0.61.",
            "source_section": "The fair experiment",
            "source_anchor": "the-fair-experiment",
            "misconception": {
                "title": "A component that is present must be contributing",
                "text": (
                    "Storage nobody reads adds nothing, a tool nobody calls adds nothing, and a tool whose result never reaches a decision adds "
                    "nothing. Rows 2 and 3 contain real, correctly built components that contribute exactly zero because they sit on no path from "
                    "the model's output to the outcome."
                ),
            },
            "scope_note": {
                "text": (
                    "The six assemblies are teaching numbers, illustrative rather than a measurement of any deployed system. The size of the jump "
                    "in row 5 is a modeling choice, made large because the argument is easier to see at full strength."
                ),
                "source_section": "Reading the table honestly",
            },
            "controls": [
                {"key": "request", "label": "Share of blind calls that output request", "values": [0.2, 0.4, 0.6], "default": 0.4},
                {"key": "rejection", "label": "What a denied request does", "values": ["stop", "blind"], "default": "stop",
                 "value_labels": ["Stops, no answer (the book's rule)", "Makes a second blind call"]},
                {"key": "calls", "label": "Calls allowed in a run", "values": [2, 1], "default": 2,
                 "value_labels": ["Two (the book's budget)", "One"]},
            ],
            "function": "six_assemblies_picture",
        },
        {
            "id": "C05-D02",
            "title": "A fixed chooser, a different tool, a different system",
            "question": "If the chooser's probabilities never change, can changing only the tool change where the system spends its time?",
            "equations": [EQ_KERNEL],
            "symbols": (
                "A state is one of two constructed states, 0 and 1, standing for coarsened values of the agent's full state. The chooser row for "
                "state i gives the probability of each proposed action (the role of pi in the equation). The tool row for action a gives the "
                "probability of each next state (the role of P_env). Their composition K(i,j) is the chance of moving from state i to state j in "
                "one transition. The probability of state 0 after n transitions starts at the chosen starting value and is updated by K each step. "
                "The transfer case has an identity chooser, so K equals the tool, and starts with probability one half in each state."
            ),
            "prediction": "Switch to the changed tool and keep two transitions. Does the chance of being in state 0 go up or down, and by about how much?",
            "prediction_options": [
                "Up, above 0.68",
                "Down, from about 0.68 to about 0.38",
                "Unchanged, because the chooser's rows are unchanged",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "The default tool gives 0.76 x 0.76 + 0.24 x 0.41 = 0.676 and the changed tool gives 0.50 x 0.50 + 0.50 x 0.25 = 0.375.",
                "incorrect": "Compare the default tool and the changed tool at two transitions: 0.676 against 0.375. The chooser's rows are the same, but the recurrent system is not, because K also contains the tool.",
            },
            "explanation": (
                "Equation (5.2) averages the tool's next-state law over the chooser's proposals. With two states the sum is small enough "
                "to do by hand: each row of K is the chooser's weights times the tool's rows. Repeating that one-step kernel is recurrence, "
                "and it settles at a long-run share that depends on both factors. The two states are a coarse version of x_t = (c_t, m_t, w_t, b_t) "
                "from Equation (5.1): the kernel is a law over those states, not over prompts."
            ),
            "application": (
                "When a model is blamed or credited for a change in behavior, ask which factor changed. Here the chooser rows are identical in "
                "the default and changed systems, so every difference in the curves is a consequence of the tool, not of the model."
            ),
            "assumptions": (
                "Two states, two proposals, no permission or budget coordinate, and a tool law that depends on the state only through the proposal. "
                "If the next state also depends on something the state leaves out, such as a memory version, the composite kernel is not a "
                "valid description and more transitions will not repair it."
            ),
            "check": "With the default tool, what is the chance of state 0 after two transitions when the system starts in state 0?",
            "answer": "K(0,0) = 0.76 and K(1,0) = 0.3 x 0.9 + 0.7 x 0.2 = 0.41. After two steps: 0.76 x 0.76 + 0.24 x 0.41 = 0.5776 + 0.0984 = 0.676.",
            "provenance": (
                "Constructed example: the laboratory's default chooser and tool matrices, the changed tool, and the notebook's transfer case "
                "(identity chooser, tool rows [0.7, 0.3] and [0.4, 0.6], start half in each state), computed with its composite-kernel function."
            ),
            "source_section": "The law the model does not contain",
            "source_anchor": "the-law-the-model-does-not-contain",
            "misconception": {
                "title": "Crediting the visible component",
                "text": (
                    "When an agent behaves differently, the most visible component need not be the cause. The frozen chooser's rows are identical in the "
                    "default and changed systems; everything that differs lies in the tool and in the recurrence it sits in."
                ),
            },
            "scope_note": {
                "text": (
                    "Equation (5.2) describes one factorization of one constructed agent; a different architecture factors differently."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "system", "label": "System", "values": ["default", "changed", "transfer"], "default": "default",
                 "value_labels": ["Default tool", "Changed tool", "Transfer case"]},
                {"key": "transitions", "label": "Number of transitions", "values": [1, 2, 3, 30], "default": 2},
            ],
            "function": "composite_kernel_picture",
        },
        {
            "id": "C05-D03",
            "title": "What an observation is worth, and what a memory may drop",
            "question": "How many bits does the tool's report deliver, does delivering them change the outcome, and what happens if the memory drops the report?",
            "equations": [EQ_INFO, EQ_ABSTRACT],
            "symbols": (
                "Y is the hidden bit and O the tool's report. H(Y) is the uncertainty about Y in bits, 1 bit when both values are equally "
                "likely. H(Y | O) is the uncertainty left after seeing O. I(Y;O) is their difference: the bits the report delivers. The "
                "accuracy is the chance the report equals Y. Success is the chance of a correct final answer. kappa merges detailed states into abstract "
                "classes; dropping the report merges the state 'report says 0' with the state 'report says 1'. Equation (5.3) asks each merged state to send "
                "equal probability into every abstract class, here the classes 'answer 0' and 'answer 1'."
            ),
            "prediction": "At accuracy 0.90, does the information change if the run stops right after the observation? Does the success rate change?",
            "prediction_options": [
                "The information stays 0.531 bits and success stays at the model-only 0.300",
                "The information stays 0.531 bits and success rises to 0.610",
                "The information falls to 0 bits and success stays at 0.300",
            ],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "The report still delivers 0.531 bits, but no later call reads it, so success stays at 0.30: the bits arrived where no decision uses them.",
                "incorrect": "Set the report to 'The run stops (tool, no recurrence)' at accuracy 0.90: the information is still 0.531 bits because it depends only on the tool, and success is still 0.300 because nothing reads the report.",
            },
            "explanation": (
                "With a report that is right with probability a, the posterior on the reported value is a, so H(Y | O) is the entropy of "
                "a and I = 1 - H(Y | O). That number depends only on the tool. Whether it matters for the task depends on a different "
                "question: does a later choice read it? A memory that keeps the report separates the two states and lets the model answer with it. A "
                "memory that drops it merges them, and Equation (5.3) fails because the next answer's chances differ between them, so the connected "
                "assembly degrades to the blind second call of row 4."
            ),
            "application": (
                "For every piece of information a system collects, name the decision it changes. If no decision changes, the collection "
                "is decoration, however many bits it carries. Before a summary replaces a record, check that the states it merges send the same "
                "probabilities into the same classes."
            ),
            "assumptions": (
                "One hidden bit with equal prior, a symmetric tool, and the informed response law held at the book's values for every "
                "accuracy. That includes 0.50, where the report carries no information but the declared law still responds to it, "
                "because the law is held fixed by construction. Mutual information is "
                "symmetric and not causal, and it measures uncertainty removed, not usefulness. Dropping the report entirely is the extreme case of a "
                "lossy memory; a partial summary would sit between the two connected rows."
            ),
            "check": "A tool is right with probability 0.75. How many bits does it deliver, and what is H(Y | O)?",
            "answer": "H(Y | O) = 0.25 x 2.000 + 0.75 x 0.415 = 0.500 + 0.311 = 0.811 bits, so I = 1 - 0.811 = 0.189 bits.",
            "provenance": "Constructed example: the chapter's tool with accuracy 0.90 (about 0.531 bits) and the blind and informed response laws it declares; other accuracies are values defined for the reader.",
            "source_section": "What an observation is worth",
            "source_anchor": "what-an-observation-is-worth",
            "misconception": {
                "title": "Counting bits as value",
                "text": (
                    "Mutual information measures reduction in uncertainty rather than usefulness: an observation can be highly informative about "
                    "something the agent has no way to act on, in which case its information value is real and its decision value is zero. It is also "
                    "symmetric and carries no direction, so it is not a causal statement."
                ),
            },
            "scope_note": {
                "text": "Mutual information measures uncertainty reduction, not causation and not usefulness.",
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "accuracy", "label": "Chance the tool reports the bit correctly", "values": [0.5, 0.75, 0.9, 1.0], "default": 0.9},
                {"key": "reaches", "label": "What happens to the report", "values": ["stops", "dropped", "reaches"], "default": "stops",
                 "value_labels": ["The run stops (tool, no recurrence)", "The memory drops it (second call is blind)",
                                  "It is kept and enters the next context (connected, granted)"]},
            ],
            "function": "observation_picture",
        },
        {
            "id": "C05-D04",
            "title": "Recurrence multiplies",
            "question": "If every step is very likely to succeed, how long a task can still survive, and what if the steps share a cause?",
            "equations": [EQ_PRODUCT, EQ_HORIZON],
            "symbols": (
                "A run is a sequence of states x_0 to x_T. P(x_{t+1} | x_t) is the probability of one step. Here every required step "
                "succeeds with the same conditional probability q given that all earlier steps succeeded, and any unrepaired failure ends "
                "the task. With one retry per step, q is the chance that at least one of two independent tries succeeds. With a shared cause, "
                "one condition that is good with the marginal probability decides every step together. The half-success horizon is the number of steps n "
                "at which q^n = 0.5, n = log 0.5 / log q. The transfer case lists a different conditional rate for each of three steps."
            ),
            "prediction": "At per-step success 0.95 with no retry, is the chance of finishing 40 steps closer to 0.9, 0.5 or 0.1?",
            "prediction_options": ["Closer to 0.9", "Closer to 0.5", "Closer to 0.1"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "0.95^40 = 0.129: forty required steps at 0.95 leave about one run in eight intact, and the half-success horizon is about 14 steps.",
                "incorrect": "Choose per-step 0.95 with independent steps: after 40 steps the chance is 0.129, closer to 0.1. The product falls fast even when each factor is near 1.",
            },
            "explanation": (
                "Equation (5.5) says a run's probability is a product of one-step probabilities. With a constant conditional success q, "
                "n steps give q multiplied by itself n times, which falls fast even when q is close to 1. A repair step raises q itself, "
                "which is why retries and verifiers are the main response to the exponent. A shared cause breaks the product altogether: the "
                "marginal rate per step is the same, but the steps are no longer independent, so completion depends on the joint law and not on p."
            ),
            "application": (
                "Before promising a long unattended task, ask what the per-step success is after the controller's own detection and "
                "recovery, not for the model's average accuracy on isolated questions."
            ),
            "assumptions": (
                "Constant conditional success and independent retries that use the same budget coordinate (each retry costs budget the "
                "chain here does not track). If failures share a cause, such as bad evidence, a retry fails for the same reason and q "
                "improves less than shown. The shared-cause line is one constructed joint law with the same marginals, not a model of any real agent. "
                "Marginal step accuracies alone do not justify this product."
            ),
            "check": "With per-step success 0.90 and one retry per step, what is the chance of finishing 2 steps?",
            "answer": "q = 1 - 0.10 x 0.10 = 0.99. Two steps: 0.99 x 0.99 = 0.9801.",
            "provenance": (
                "Constructed example: the chapter's compounding values (0.99 over 40 steps is 0.669, 0.95 is 0.129) and half-success horizons (about 14, 69 and 693 steps), "
                "computed with the laboratory's chain function; the retry rule is a construction defined for the reader, and the transfer case is the notebook's (rates 0.9, 0.8, 0.7)."
            ),
            "source_section": "Recurrence multiplies",
            "source_anchor": "recurrence-multiplies",
            "misconception": {
                "title": "Using average accuracy as the per-step rate",
                "text": (
                    "You cannot substitute the average accuracy of isolated model answers for the conditional per-step rate: marginal step accuracies alone "
                    "do not justify the product. Shared bad evidence can make failures cluster, and a verifier or recovery action changes which failures end the task."
                ),
            },
            "scope_note": {
                "text": "A task limit derived from this simple chain is a limit of that declared chain, not a universal ceiling on agents.",
                "source_section": "A failed step need not be a failed task",
            },
            "controls": [
                {"key": "case", "label": "Per-step success", "values": ["p95", "p99", "p999", "transfer"], "default": "p99",
                 "value_labels": ["0.95 per step", "0.99 per step", "0.999 per step", "Transfer: rates 0.9, 0.8, 0.7 over 3 steps"]},
                {"key": "handling", "label": "How steps relate", "values": ["none", "retry", "shared"], "default": "none",
                 "value_labels": ["Independent, no retry", "Independent, one retry per step", "One shared cause (same marginal)"]},
            ],
            "function": "recurrence_picture",
        },
    ],
}

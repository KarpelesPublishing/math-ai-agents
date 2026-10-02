"""Chapter 19 reader: When Another Mind Becomes Part of the World.

Four demonstrations built on Equations (19.1) to (19.4).

Demonstration 1 applies Equation (19.2) to the means the chapter prints for
five tasks (the laboratory's own cross-play function computes the loss, and
the module asserts that it agrees with the written formula). Demonstration 2
walks the chapter's three-action best-response cycle. Demonstration 3 uses
the chapter's smallest-map numbers to show how one fix moves three different
reported numbers in different directions. Demonstration 4 uses the
laboratory's constructed two-policy cross-play matrix, computed with the
laboratory's own function, to show how partner weights decide a ranking.
Every number is a teaching value: either printed in the chapter or declared
in the laboratory's inputs.
"""
import math

import numpy as np

from math_ai_agents.chapters.ch19 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

EQ_MATRIX = r"M_{st} \;=\; \mathrm{E}\Big[\,u\big(\pi_1^{(s)},\,\pi_2^{(t)}\big)\Big]."
EQ_JPC = r"\operatorname{JPC}(M) \;=\; \frac{\operatorname{diag}(M) - \operatorname{off}(M)}{\operatorname{diag}(M)}."
EQ_KERNEL = r"P\big(x' \mid x, a\big) \;\longrightarrow\; P\big(x' \mid x, a,\, \pi_{-i}\big)."
EQ_BR = r"\operatorname{BR}_i(\pi_{-i}) \;=\; \arg\max_{\pi_i}\; u_i\big(\pi_i, \pi_{-i}\big)."

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


# Demonstration 1: the instrument on the chapter's printed means

# task: (label, diagonal mean, off-diagonal mean, loss as printed in the chapter)
TASKS = {
    "small2": ("Laser Tag small2", 30.44, 20.03, 0.342),
    "small3": ("Laser Tag small3", 23.06, 9.06, 0.625),
    "small4": ("Laser Tag small4", 20.15, 5.71, 0.717),
    "gathering": ("Gathering", 147.34, 146.89, 0.003),
    "pathfinding": ("Pathfinding", 108.73, 106.32, 0.022),
}
SHORT = {"small2": "small2", "small3": "small3", "small4": "small4", "gathering": "gather", "pathfinding": "path"}
SCALE = 200.0  # the laboratory function takes probabilities, so the means are divided by this and the ratio is unchanged


def lab_loss(diag, off):
    """Equation (19.2) from the laboratory's cross-play function, using a matrix whose diagonal is diag and off-diagonal is off."""
    d, o = diag / SCALE, off / SCALE
    out = evaluate({"matrix": [[d, o], [o, d]], "partner_weights": [0.5, 0.5], "supervisor_weights": [0.5, 0.5]})
    return out["metrics"]["joint_policy_correlation_loss"]


def written_loss(diag, off):
    return (diag - off) / diag


def instrument_picture(task="small2"):
    name, diag, off, printed = TASKS[task]
    loss = lab_loss(diag, off)
    if not math.isclose(loss, written_loss(diag, off), abs_tol=1e-12):
        raise AssertionError("laboratory loss disagrees with Equation (19.2) written out")
    losses = {k: lab_loss(v[1], v[2]) for k, v in TASKS.items()}
    gap = diag - off

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    bars = left.bar([0, 1], [diag, off], width=0.55, color=[PALETTE["teal"], "#8fa3b8"], edgecolor=PALETTE["ink"], linewidth=1)
    bars[1].set_hatch("///")
    for x, v in ((0, diag), (1, off)):
        left.text(x, v + diag * 0.03, fmt(v, 2), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.set_xticks([0, 1], ["Diagonal\n(own training\npartner)", "Off-diagonal\n(a stranger)"])
    left.set_ylim(0, diag * 1.25)
    left.set_xlim(-0.6, 1.6)
    left.set_xlabel("Pairing in the matrix")
    left.set_ylabel("Mean return (units of the chapter's table)")
    left.set_title(name, fontsize=11.5)

    order = list(TASKS)
    xs = np.arange(len(order))
    heights = [losses[k] for k in order]
    colors = [PALETTE["teal"] if k == task else PALETTE["light"] for k in order]
    rb = right.bar(xs, heights, width=0.6, color=colors, edgecolor=PALETTE["ink"], linewidth=1)
    for bar, k in zip(rb, order):
        if k in ("gathering", "pathfinding"):
            bar.set_hatch("..")
    mismatch = abs(round(losses[task], 3) - printed) > 0.0005
    for x, k in zip(xs, order):
        if k == task and mismatch:
            right.text(x, losses[k] - 0.015, fmt(losses[k], 3), ha="center", va="top", fontsize=10.5, color="white", fontweight="bold")
        else:
            right.text(x, losses[k] + 0.012, fmt(losses[k], 3), ha="center", va="bottom", fontsize=10.5,
                       color=PALETTE["teal"] if k == task else PALETTE["ink"], fontweight="bold" if k == task else "normal")
    if mismatch:
        right.plot([order.index(task)], [printed], "D", color=PALETTE["terracotta"], markersize=8)
        label_point(right, order.index(task), printed, f"printed {fmt(printed, 3)}", color=PALETTE["terracotta"], dx=0, dy=14, ha="center").set_bbox(BOX)
    right.set_xticks(xs, [SHORT[k] for k in order])
    for tick, k in zip(right.get_xticklabels(), order):
        if k == task:
            tick.set_fontweight("bold")
            tick.set_color(PALETTE["teal"])
    right.set_ylim(0, 0.9)
    right.set_xlabel("Task (bold: chosen). gather = Gathering, path = Pathfinding:\ndotted bars, coordination not required, shown for comparison only")
    right.set_ylabel("Loss from Equation (19.2)")
    right.set_title("Loss for all five tasks", fontsize=11.5)

    if mismatch:
        verdict = (f"The chapter prints {fmt(printed, 3)} for this map, but its own printed means give {fmt(loss, 3)}. "
                   "This reader draws the recomputed value as the bar and marks the printed one with a diamond; the chapter flags the same difference in its text.")
        shown = f"{fmt(loss, 3)} (chapter prints {fmt(printed, 3)})"
    else:
        shown = fmt(loss, 3)
        if task in ("gathering", "pathfinding"):
            verdict = (f"The loss is only {fmt(loss, 3)}. The chapter reads this as a task where coordination is not required, "
                       "and says such a small gap does not prove the policies are independent.")
        else:
            verdict = (f"Strangers lose {fmt(100 * loss, 1)} percent of the diagonal mean on average. "
                       "That compares these pairings only; it is not a universal measure of cooperation.")
    metrics = {
        "Diagonal mean": fmt(diag, 2),
        "Off-diagonal mean": fmt(off, 2),
        "Loss from Equation (19.2)": shown,
    }
    interpretation = (f"Loss = ({fmt(diag, 2)} - {fmt(off, 2)}) / {fmt(diag, 2)} = {fmt(gap, 2)} / {fmt(diag, 2)} = {fmt(loss, 3)}. {verdict} "
                      "The diagonal says how the developed pairs do together; only the off-diagonal says what happens with a stranger.")
    return fig, metrics, interpretation


# Demonstration 2: a best-response cycle

ACTIONS = ["A", "B", "C"]
BEATS = {"A": "C", "B": "A", "C": "B"}  # key beats value; matches the chapter's preferences


def payoff(mine, theirs):
    """Payoff to the party choosing `mine` against `theirs` (plus one to the winner, minus one to the loser, zero for a tie)."""
    if mine == theirs:
        return 0
    return 1 if BEATS[mine] == theirs else -1


def best_response(theirs):
    scores = {a: payoff(a, theirs) for a in ACTIONS}
    best = max(scores.values())
    winners = [a for a in ACTIONS if scores[a] == best]
    if len(winners) != 1:
        raise AssertionError("best response is not unique")
    return winners[0]


def run_cycle(start, updates):
    """Party two starts at `start`. Party one updates first, then the parties alternate. Returns one record per update."""
    one, two = None, start
    rows = []
    for k in range(1, updates + 1):
        if k % 2 == 1:
            one = best_response(two)
            mover = "one"
        else:
            two = best_response(one)
            mover = "two"
        mover_payoff = payoff(one, two) if mover == "one" else payoff(two, one)
        rows.append({"k": k, "mover": mover, "one": one, "two": two, "payoff_one": payoff(one, two), "mover_payoff": mover_payoff})
    return rows


def cycle_picture(updates=6, start="A"):
    updates = int(updates)
    rows = run_cycle(start, updates)
    y = {a: i for i, a in enumerate(ACTIONS)}
    one_k = [r["k"] for r in rows if r["mover"] == "one"]
    one_a = [y[r["one"]] for r in rows if r["mover"] == "one"]
    two_k = [0] + [r["k"] for r in rows if r["mover"] == "two"]
    two_a = [y[start]] + [y[r["two"]] for r in rows if r["mover"] == "two"]
    payoffs = [r["payoff_one"] for r in rows]
    mean_one = sum(payoffs) / len(payoffs)
    back = next((r["k"] for r in rows if r["mover"] == "two" and r["two"] == start), None)

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.plot(two_k, two_a, "o", linestyle="dashed", color=PALETTE["navy"], markersize=8, linewidth=1.4)
    left.plot(one_k, one_a, "s", linestyle="dashed", color=PALETTE["terracotta"], markersize=8, linewidth=1.4, markerfacecolor="white", markeredgewidth=1.8)
    label_point(left, two_k[-1], two_a[-1], "party two", color=PALETTE["navy"], dx=0, dy=11, ha="right").set_bbox(BOX)
    label_point(left, one_k[-1], one_a[-1], "party one", color=PALETTE["terracotta"], dx=0, dy=-11, ha="right", va="top").set_bbox(BOX)
    if back is not None:
        left.axvline(back, color=PALETTE["grey"], linestyle=":", linewidth=1.4)
        label_point(left, back, 2.55, "party two back at start", color=PALETTE["grey"], dx=-4, dy=0, ha="right", va="top").set_bbox(BOX)
    left.set_yticks([0, 1, 2], ACTIONS)
    left.set_xticks(range(0, updates + 1, 2 if updates > 6 else 1))
    left.set_xlim(-0.5, updates + 0.5)
    left.set_ylim(-0.6, 2.6)
    left.set_xlabel("Update number (0 is the start)")
    left.set_ylabel("Option the party plays")
    left.set_title("Each party answers the other's last move", fontsize=11.5)

    xs = np.arange(1, updates + 1)
    colors = [PALETTE["teal"] if p > 0 else PALETTE["terracotta"] for p in payoffs]
    pb = right.bar(xs, payoffs, width=0.6, color=colors, edgecolor=PALETTE["ink"], linewidth=1)
    for bar, p in zip(pb, payoffs):
        if p < 0:
            bar.set_hatch("///")
    right.axhline(0, color=PALETTE["ink"], linewidth=1)
    right.set_xticks(xs, [f"{r['k']}\n{r['mover']}" for r in rows])
    right.set_ylim(-1.5, 1.5)
    right.set_xlabel("Update number, and which party moved")
    right.set_ylabel("Payoff to party one after the update")
    right.set_title("Every update helps its mover; nobody settles", fontsize=11.5)

    first_scores = ", ".join(signed(payoff(a, start), 0) for a in ACTIONS)
    first_option = rows[0]["one"]
    reply = rows[1]["two"]
    all_improve = all(r["mover_payoff"] == 1 for r in rows)
    sum_text = " + ".join(signed(p, 0) for p in payoffs)
    if back is not None:
        repeat = f"after {back} updates"
        tail = f" Party two is back at {start} after update {back}, so the cycle repeats."
    else:
        repeat = f"not yet in {updates} updates"
        tail = f" Party two has not yet returned to {start}; the cycle needs 6 updates to close."
    metrics = {
        "Updates shown": str(updates),
        "Party two back at its start": repeat,
        "Mover's payoff after its own update": "+1 every time" if all_improve else "not always +1",
        "Mean payoff to party one": fmt(mean_one, 2),
    }
    interpretation = (
        f"First update: with party two at {start}, party one's payoffs for A, B, C are {first_scores}, so Equation (19.4) picks "
        f"{rows[0]['one']}. Mean payoff to party one over the {updates} updates = ({sum_text}) / {updates} = {fmt(mean_one, 2)}. "
        f"Each mover gains 1 against the partner it faces, yet the partner then moves and the gain is gone: option {first_option} pays "
        f"{signed(payoff(first_option, start), 0)} against {start} but {signed(payoff(first_option, reply), 0)} against {reply}, the move party two "
        f"then makes (the dependence in Equation (19.3)). "
        f"A uniform mix of the three options pays (1 + 0 + (-1)) / 3 = 0.00 against any pure option.{tail}"
    )
    return fig, metrics, interpretation


# Demonstration 3: what a fix costs (chapter numbers, smallest map)

SMALL2 = {"independent": (30.44, 20.03), "population": (28.20, 26.63)}
TRACKED = {
    "diagonal": ("Diagonal mean", "Mean return against own training partner", True),
    "off": ("Off-diagonal mean", "Mean return against a stranger", True),
    "ratio": ("Loss from Equation (19.2)", "Loss from Equation (19.2)", False),
}


def tracked_value(which, diag, off):
    return {"diagonal": diag, "off": off, "ratio": (diag - off) / diag}[which]


def fix_cost_picture(tracked="diagonal"):
    label, ylabel, higher_is_better = TRACKED[tracked]
    d0, o0 = SMALL2["independent"]
    d1, o1 = SMALL2["population"]
    v0, v1 = tracked_value(tracked, d0, o0), tracked_value(tracked, d1, o1)
    change = v1 - v0
    better = change > 0 if higher_is_better else change < 0
    digits = 3 if tracked == "ratio" else 2

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    width = 0.36
    x = np.arange(2)
    lb1 = left.bar(x - width / 2, [d0, d1], width=width, color=PALETTE["teal"], edgecolor=PALETTE["ink"], linewidth=1)
    lb2 = left.bar(x + width / 2, [o0, o1], width=width, color="#8fa3b8", edgecolor=PALETTE["ink"], linewidth=1, hatch="///")
    for bars in (lb1, lb2):
        for bar in bars:
            left.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, fmt(bar.get_height(), 2), ha="center", va="bottom",
                      fontsize=10.5, color=PALETTE["ink"])
    left.set_xticks(x, ["Independent\nlearners", "Population\nmethod"])
    left.set_ylim(0, 42)
    left.set_xlabel("Training method (Laser Tag small2)")
    left.set_ylabel("Mean return")
    left.legend([lb1, lb2], ["solid: diagonal", "hatched: off-diagonal"], loc="upper center", ncol=2, fontsize=10.5, frameon=False,
                columnspacing=1.0, handlelength=1.2)
    left.set_title("The two means before and after", fontsize=11.5)

    rbars = right.bar([0, 1], [v0, v1], width=0.5, color=[PALETTE["light"], PALETTE["teal"] if better else PALETTE["terracotta"]],
                      edgecolor=PALETTE["ink"], linewidth=1)
    if not better:
        rbars[1].set_hatch("///")
    top = max(v0, v1)
    for xi, v in ((0, v0), (1, v1)):
        right.text(xi, v + top * 0.03, fmt(v, digits), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    right.set_xticks([0, 1], ["Independent\nlearners", "Population\nmethod"])
    right.set_ylim(0, top * 1.35)
    right.set_xlim(-0.6, 1.6)
    right.set_xlabel("Training method")
    right.set_ylabel(ylabel)
    reading = "improvement" if better else "regression"
    if tracked == "ratio":
        reading += " (lower is better)"
    right.set_title(f"Tracking this number shows an {reading}" if better else f"Tracking this number shows a {reading}", fontsize=11.5)

    printed_note = ""
    if tracked == "ratio":
        printed_note = (f" The chapter prints 5.5 percent; the printed means give {fmt(100 * v1, 2)} percent, so treat the last digit as reported, "
                        f"not recomputed. Likewise the chapter prints a reduction of 28.7 points, while the printed means give {fmt(100 * (v0 - v1), 1)}.")
        calc = (f"Loss before = ({fmt(d0, 2)} - {fmt(o0, 2)}) / {fmt(d0, 2)} = {fmt(v0, 3)}. Loss after = ({fmt(d1, 2)} - {fmt(o1, 2)}) / "
                f"{fmt(d1, 2)} = {fmt(d1 - o1, 2)} / {fmt(d1, 2)} = {fmt(v1, 3)}")
    else:
        a, b = (d0, d1) if tracked == "diagonal" else (o0, o1)
        calc = f"Change = {fmt(b, 2)} - {fmt(a, 2)} = {signed(b - a, 2)}"
    metrics = {
        "Number tracked": label,
        "Independent learners": fmt(v0, digits),
        "Population method": fmt(v1, digits),
        "Change": signed(change, digits).strip("()") if change >= 0 else fmt(change, digits),
        "Reads as": "improvement" if better else "regression",
    }
    interpretation = (
        f"{calc}. Judged by this number alone, the fix reads as {'an improvement' if better else 'a regression'}. "
        "The diagonal fell by 2.24 while the off-diagonal rose by 6.60, so the same intervention looks like a small regression "
        f"on the number most teams track and a large improvement on the number that describes a partner change.{printed_note}"
    )
    return fig, metrics, interpretation


# Demonstration 4: partner weights decide the ranking (laboratory matrix)

LAB_MATRIX = [[0.95, 0.2], [0.4, 0.9]]
LAB_SUPERVISOR = [0.9, 0.1]


def mixture_values(w0):
    out = evaluate({"matrix": LAB_MATRIX, "partner_weights": [w0, 1 - w0], "supervisor_weights": LAB_SUPERVISOR})
    return out["metrics"]


def partner_mix_picture(w0=0.5):
    w0 = float(w0)
    m = mixture_values(w0)
    v0, v1 = m["partner_mixture_values"]
    written0 = w0 * 0.95 + (1 - w0) * 0.2
    written1 = w0 * 0.4 + (1 - w0) * 0.9
    if not (math.isclose(v0, written0, abs_tol=1e-12) and math.isclose(v1, written1, abs_tol=1e-12)):
        raise AssertionError("laboratory values disagree with the written weighted sums")
    tie = math.isclose(v0, v1, abs_tol=1e-9)
    winner = "tie" if tie else ("Policy 0" if v0 > v1 else "Policy 1")
    jpc = m["joint_policy_correlation_loss"]
    diag_leader = "Policy 0" if LAB_MATRIX[0][0] > LAB_MATRIX[1][1] else "Policy 1"
    crossing = 0.7 / 1.25

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    grid = np.array(LAB_MATRIX)
    left.imshow(grid, cmap="Blues", vmin=0, vmax=1.25, aspect="auto")
    for i in range(2):
        for j in range(2):
            kind = "matched" if i == j else "stranger"
            left.text(j, i, f"{fmt(grid[i, j], 2)}\n{kind}", ha="center", va="center", fontsize=11.5,
                      color="white" if grid[i, j] > 0.6 else PALETTE["ink"])
            if i == j:
                left.add_patch(plt_rect(j, i))
    left.set_xticks([0, 1], ["0", "1"])
    left.set_yticks([0, 1], ["0", "1"])
    left.set_xlabel("Partner t (column)")
    left.set_ylabel("Policy s (row)")
    left.set_title("Matrix M: success probability", fontsize=11.5)
    left.grid(False)

    w = np.linspace(0, 1, 101)
    right.plot(w, w * 0.95 + (1 - w) * 0.2, color=PALETTE["navy"], linewidth=2)
    right.plot(w, w * 0.4 + (1 - w) * 0.9, color=PALETTE["terracotta"], linewidth=2, linestyle="dashed")
    right.axvline(crossing, color=PALETTE["grey"], linestyle=":", linewidth=1.4)
    right.axvline(w0, color=PALETTE["ink"], linewidth=1.2)
    label_point(right, w0, 1.03, "current p", color=PALETTE["ink"], dx=4 if w0 < 0.6 else -4, dy=0,
                ha="left" if w0 < 0.6 else "right", va="top").set_bbox(BOX)
    right.plot([w0], [v0], "o", color=PALETTE["navy"], markersize=9)
    right.plot([w0], [v1], "s", color=PALETTE["terracotta"], markersize=9, markerfacecolor="white", markeredgewidth=2)
    label_point(right, 0.3, 0.2 + 0.75 * 0.3, "policy 0", color=PALETTE["navy"], dx=6, dy=-8, ha="left", va="top").set_bbox(BOX)
    label_point(right, 0.0, 0.9, "policy 1", color=PALETTE["terracotta"], dx=6, dy=8, ha="left").set_bbox(BOX)
    label_point(right, crossing, 0.3, f"tie at {fmt(crossing, 2)}", color=PALETTE["grey"], dx=5, dy=0, ha="left", va="center").set_bbox(BOX)
    right.set_xlim(0, 1)
    right.set_ylim(0.15, 1.05)
    right.set_xlabel("Probability of meeting partner 0")
    right.set_ylabel("Success against the partner mix")
    right.set_title("Which policy ranks first depends on the mix", fontsize=11.5)

    if tie:
        verdict = (f"The two policies tie at {fmt(v0, 3)}. The ranking rule does not choose between them, and the diagonal alone "
                   f"would still name {diag_leader}.")
    elif winner == diag_leader:
        verdict = f"{winner} ranks first, which agrees with the diagonal here."
    else:
        verdict = f"{winner} ranks first, although the diagonal alone names {diag_leader}."
    metrics = {
        "Policy 0 against the mix": fmt(v0, 3),
        "Policy 1 against the mix": fmt(v1, 3),
        "Ranks first": winner,
        "Diagonal alone names": diag_leader,
        "Loss from Equation (19.2)": fmt(jpc, 3),
    }
    interpretation = (
        f"Policy 0 = {fmt(w0, 2)} x 0.95 + {fmt(1 - w0, 2)} x 0.2 = {fmt(v0, 3)}. Policy 1 = {fmt(w0, 2)} x 0.4 + {fmt(1 - w0, 2)} x 0.9 = "
        f"{fmt(v1, 3)}. {verdict} The loss is fixed by the matrix: (0.925 - 0.3) / 0.925 = {fmt(jpc, 3)}, whatever the mix. "
        f"The two policies tie where 0.2 + 0.75 x p = 0.9 - 0.5 x p, that is p = 0.7 / 1.25 = {fmt(crossing, 2)}."
    )
    return fig, metrics, interpretation


def plt_rect(j, i):
    from matplotlib.patches import Rectangle
    return Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=PALETTE["ink"], linewidth=3)


CHAPTER = {
    "number": 19,
    "title": "When Another Mind Becomes Part of the World",
    "subtitle": "A score earned beside one partner may not travel to another, so the partner belongs inside the measurement.",
    "summary": (
        "These four demonstrations follow the chapter's cross-play matrix. The first computes the loss statistic on the chapter's "
        "printed means. The second shows why simply optimizing against the current partner can go in circles. The third shows how one "
        "fix moves three reported numbers in different directions. The fourth shows how the partners you expect to meet decide which "
        "policy ranks first."
    ),
    "demos": [
        {
            "id": "C19-D01",
            "title": "Diagonal against off-diagonal",
            "question": "How much of a score is lost when a policy meets a partner from another training run instead of its own?",
            "equations": [EQ_MATRIX, EQ_JPC],
            "symbols": (
                "M_st is the mean return when the first party uses the policy from training run s and the second party uses the policy "
                "from run t. diag(M) is the average of the entries with s equal to t (matched partners). off(M) is the average of the "
                "entries with s different from t (strangers). JPC(M), the joint policy correlation loss, is their difference divided by diag(M), a proportional loss. E is the mean over many episodes, u is the "
                "joint return of the two parties (their returns added together), and pi_1^(s), pi_2^(t) are the policies the first and second party use. "
                "Returns here are in the units of the chapter's table."
            ),
            "prediction": "For the small4 map the diagonal mean is 20.15 and the off-diagonal mean is 5.71. Before selecting it, guess whether the loss is nearer 0.3 or 0.7.",
            "explanation": (
                "Equation (19.1) fills a table with one entry for every pairing of runs. Equation (19.2) averages the diagonal, averages "
                "the off-diagonal, subtracts, and divides by the diagonal average. A loss near zero means strangers score about what "
                "matched partners score; a loss near one means the score almost vanishes."
            ),
            "application": (
                "When two components of a system were developed together, evaluate them also against independently developed replacements, "
                "and report the diagonal, the off-diagonal and the loss, not only the diagonal."
            ),
            "assumptions": (
                "The statistic is meaningful only when the diagonal mean is positive, and it compares particular pairings under one "
                "procedure. It is not a universal measure of cooperation and does not show why a gap appears. A small loss does not show "
                "the policies are independent or interchangeable."
            ),
            "check": "A matrix has a diagonal mean of 10 and an off-diagonal mean of 8. What is the loss, and what changes if the diagonal mean is 0?",
            "answer": "(10 - 8) / 10 = 0.20. With a diagonal mean of 0 the denominator is 0, so the statistic is undefined and the chapter says to report the difference instead.",
            "provenance": (
                "Constructed example: the diagonal and off-diagonal means are the values the chapter prints for three Laser Tag maps and two "
                "control tasks, used here as a teaching example; the loss is computed with the laboratory's cross-play function."
            ),
            "source_section": "What the instrument found",
            "source_anchor": "what-the-instrument-found",
            "controls": [
                {"key": "task", "label": "Task", "values": ["small2", "small3", "small4", "gathering"], "default": "small2",
                 "value_labels": ["Laser Tag small2", "Laser Tag small3", "Laser Tag small4", "Gathering"]},
            ],
            "function": "instrument_picture",
        },
        {
            "id": "C19-D02",
            "title": "A best-response cycle",
            "question": "If each party always plays its best answer to the other's current move, does the sequence settle?",
            "equations": [EQ_KERNEL, EQ_BR],
            "symbols": (
                "BR_i(pi_-i) is the policy for party i that maximizes its payoff u_i when the other party's policy pi_-i is held fixed. "
                "P(x' | x, a, pi_-i) is the chance of next state x' given state x, action a and the other party's policy. Here each party "
                "picks one of three options A, B, C. A beats C, B beats A and C beats B; a win pays 1, a loss pays (-1) and a tie pays 0."
            ),
            "prediction": "Start party two at A and show 6 updates. Does the sequence stop at some pair of options, or return to where it began?",
            "explanation": (
                "Each update computes Equation (19.4) exactly against the option the other party is playing now. Because the other party then "
                "moves, the world the first party optimized against is gone, which is the added argument in Equation (19.3). In this "
                "game the sequence of options each party plays repeats every six updates."
            ),
            "application": (
                "When two adapting components keep re-tuning to each other, track a fixed set of evaluation partners rather than "
                "only the latest partner, because progress against the latest one can be undone by the next update."
            ),
            "assumptions": (
                "A constructed zero-sum game with one-step pure best responses, ties paying 0 (a choice made for this reader), and no noise. "
                "Some games converge under the same rule, and other update rules behave differently. The cycle shows that convergence is not guaranteed; it does not explain "
                "the transfer losses in Demonstration 1."
            ),
            "check": "If party two starts at B instead, which option does party one answer with first, and how many updates until party two is back at B?",
            "answer": "Party one's payoffs against B are A: (-1), B: 0, C: 1, so it plays C. Party two answers A, party one B, party two C, party one A, party two B, so party two is back at B after 6 updates.",
            "provenance": "Constructed example: the three-option game and the six-update trace described in the chapter's worked cycle, with ties defined by this reader.",
            "source_section": "A cycle, worked",
            "source_anchor": "a-cycle-worked",
            "controls": [
                {"key": "updates", "label": "Updates shown", "values": [2, 4, 6, 12], "default": 6},
                {"key": "start", "label": "Where party two starts", "values": ["A", "C"], "default": "A"},
            ],
            "function": "cycle_picture",
        },
        {
            "id": "C19-D03",
            "title": "What a fix costs",
            "question": "If a fix helps with strangers but slightly hurts with the training partner, which number tells you it worked?",
            "equations": [EQ_JPC],
            "symbols": (
                "diag(M) is the mean return against the policy's own training partner. off(M) is the mean return against a stranger. "
                "JPC(M), the joint policy correlation loss, is (diag(M) - off(M)) / diag(M), a proportional loss. Returns are joint returns (the two parties' returns added together). Independent learners are the baseline; the population "
                "method trains each policy against a mixture of other policies. Values are the chapter's printed means for the smallest map."
            ),
            "prediction": "Look at the diagonal mean first. Does the population method look better or worse than the baseline on it? Then check the off-diagonal mean.",
            "explanation": (
                "The population method lowered the diagonal from 30.44 to 28.20 and raised the off-diagonal from 20.03 to 26.63. "
                "The loss is driven by the gap between the two means, which shrank from 10.41 to 1.57, so it falls even though the diagonal fell. "
                "Which number a team watches decides whether the fix looks like progress."
            ),
            "application": (
                "When judging an intervention meant to improve transfer, print the diagonal, the off-diagonal and the loss together, so a "
                "success on partner change is not recorded as a regression."
            ),
            "assumptions": (
                "These are the chapter's printed means for one map and one method from one paper, not a general rate. Widening the "
                "partners a system trains against is something to test: it may move either mean in either direction in another setting."
            ),
            "check": "A fix lowers the diagonal from 20 to 19 and raises the off-diagonal from 10 to 15. What are the losses before and after?",
            "answer": "Before: (20 - 10) / 20 = 0.50. After: (19 - 15) / 19 = 0.21. The diagonal fell, but the loss more than halved.",
            "provenance": "Constructed example: the chapter's smallest-map means (30.44, 20.03, 28.20, 26.63) used as a teaching example.",
            "source_section": "Why training against a population helps",
            "source_anchor": "why-training-against-a-population-helps",
            "controls": [
                {"key": "tracked", "label": "Number you track", "values": ["diagonal", "off", "ratio"], "default": "diagonal",
                 "value_labels": ["Diagonal mean", "Off-diagonal mean", "Loss from Equation (19.2)"]},
            ],
            "function": "fix_cost_picture",
        },
        {
            "id": "C19-D04",
            "title": "Which partners will it meet?",
            "question": "If the diagonal favors one policy, can the partners you expect to meet make the other policy the better choice?",
            "equations": [EQ_MATRIX, EQ_JPC],
            "symbols": (
                "M_st is the success probability of policy s (row) against partner t (column). p is the probability that the policy will "
                "meet partner 0, and 1 minus p the probability of partner 1. A policy's value against the mix is its row averaged with these "
                "weights. JPC(M), the joint policy correlation loss, is the loss of Equation (19.2) for the whole matrix. In this demonstration u is a success indicator (1 for success, 0 otherwise), "
                "so each entry M_st = E[u] is a success probability."
            ),
            "prediction": "At p = 0.5 policy 0 has the better diagonal entry. Which policy has the better value against the mix?",
            "explanation": (
                "The matrix holds fixed numbers. The weights decide how much each column counts, so moving p changes which row averages higher "
                "while the matrix, and the loss computed from it, stay the same. The two rows tie at the single value of p where their "
                "lines cross."
            ),
            "application": (
                "Before choosing a component, write down the partner distribution you expect in use, and check whether the ranking "
                "survives plausible changes to it, instead of ranking by the diagonal."
            ),
            "assumptions": (
                "A constructed two-by-two matrix and a declared partner mix; the weighted average over partners is this laboratory's way of "
                "asking the deployment question, not a formula printed in the chapter. It assumes the matrix entries share one success definition, "
                "and that partners do not change how they behave once a policy is chosen."
            ),
            "check": "For the same matrix, which policy ranks first at p = 0.7, and what are the two values?",
            "answer": "Policy 0: 0.7 x 0.95 + 0.3 x 0.2 = 0.725. Policy 1: 0.7 x 0.4 + 0.3 x 0.9 = 0.55. Policy 0 ranks first, since 0.7 is above the crossing at 0.56.",
            "provenance": "Constructed example: the laboratory's two-policy cross-play matrix, computed with the laboratory's cross-play function.",
            "source_section": "Self-play is the diagonal",
            "source_anchor": "self-play-is-the-diagonal",
            "controls": [
                {"key": "w0", "label": "Probability of meeting partner 0", "values": [0.1, 0.5, 0.56, 0.9], "default": 0.5},
            ],
            "function": "partner_mix_picture",
        },
    ],
}

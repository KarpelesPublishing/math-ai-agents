"""Chapter 19 reader: When Another Mind Becomes Part of the World.

Four demonstrations built on Equations (19.1) to (19.4).

Demonstration 1 applies Equation (19.2) to the means the chapter prints for
its tasks (the laboratory's own cross-play function computes the loss, and the
module asserts that it agrees with the written formula). Its second view shows
what the chapter's population fix did, using only values the chapter prints or
that follow from printed values by subtraction. Demonstration 2 walks the
chapter's three-action best-response cycle and compares each local gain with
the average against a fixed evaluation set. Demonstration 3 is the chapter's
return on depth (Figure 19.3). Demonstration 4 uses the laboratory's two
constructed cross-play matrices (the default two-policy matrix and the transfer
three-policy matrix) with the default, changed and transfer partner mixtures,
computed with the laboratory's own function. Every number is a teaching value:
either printed in the chapter or declared in the laboratory's inputs.
"""
import math

import numpy as np

from math_ai_agents.chapters.ch19 import evaluate
from readerkit import PALETTE, argmax_set, fmt, label_point, new_figure, signed

EQ_MATRIX = r"M_{st} \;=\; \mathrm{E}\Big[\,u\big(\pi_1^{(s)},\,\pi_2^{(t)}\big)\Big]."
EQ_JPC = r"\operatorname{JPC}(M) \;=\; \frac{\operatorname{diag}(M) - \operatorname{off}(M)}{\operatorname{diag}(M)}."
EQ_KERNEL = r"P\big(x' \mid x, a\big) \;\longrightarrow\; P\big(x' \mid x, a,\, \pi_{-i}\big)."
EQ_BR = r"\operatorname{BR}_i(\pi_{-i}) \;=\; \arg\max_{\pi_i}\; u_i\big(\pi_i, \pi_{-i}\big)."

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
SCOPE_SECTION = "What this does not settle"


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

# What the population method did, in percentage points of loss, as the chapter prints them.
# base: independent learners; single: highest-level policy only; full: full mixed strategy.
# small3 base is the printed 0.625 (its printed means give 0.607). small4 full is not printed as a loss: the chapter
# prints the reduction 56.7 points, so the loss left is 71.7 - 56.7 = 15.0 points.
FIX = {
    "small2": {"base": 34.2, "single": 14.7, "full": 5.5, "red_single": 19.5, "red_full": 28.7, "full_derived": False},
    "small3": {"base": 62.5, "single": 27.0, "full": 8.2, "red_single": 36.5, "red_full": 54.3, "full_derived": False},
    "small4": {"base": 71.7, "single": 11.8, "full": 15.0, "red_single": 59.9, "red_full": 56.7, "full_derived": True},
}
SMALL2_MEANS = {"independent": (30.44, 20.03), "population": (28.20, 26.63)}


def lab_loss(diag, off):
    """Equation (19.2) from the laboratory's cross-play function, using a matrix whose diagonal is diag and off-diagonal is off."""
    d, o = diag / SCALE, off / SCALE
    out = evaluate({"matrix": [[d, o], [o, d]], "partner_weights": [0.5, 0.5], "supervisor_weights": [0.5, 0.5]})
    return out["metrics"]["joint_policy_correlation_loss"]


def written_loss(diag, off):
    return (diag - off) / diag


def five_task_bars(ax, task):
    losses = {k: lab_loss(v[1], v[2]) for k, v in TASKS.items()}
    order = list(TASKS)
    xs = np.arange(len(order))
    colors = [PALETTE["teal"] if k == task else PALETTE["light"] for k in order]
    rb = ax.bar(xs, [losses[k] for k in order], width=0.6, color=colors, edgecolor=PALETTE["ink"], linewidth=1)
    for bar, k in zip(rb, order):
        if k in ("gathering", "pathfinding"):
            bar.set_hatch("..")
    return losses, order, xs


def instrument_figure(task):
    name, diag, off, printed = TASKS[task]
    loss = lab_loss(diag, off)
    if not math.isclose(loss, written_loss(diag, off), abs_tol=1e-12):
        raise AssertionError("laboratory loss disagrees with Equation (19.2) written out")

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

    losses, order, xs = five_task_bars(right, task)
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
    return fig, loss, mismatch, printed


def fix_figure(task):
    """Second view: what the population method did on this map (or a message when the chapter reports no fix)."""
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    if task not in FIX:
        left.set_xlim(0, 1)
        left.set_ylim(0, 1)
        left.set_xticks([])
        left.set_yticks([])
        left.text(0.5, 0.5, "The chapter reports the fix\nonly on the three Laser Tag maps,\nnot on this task.", ha="center", va="center",
                  fontsize=11.5, color=PALETTE["ink"])
        left.set_xlabel("No fix reported for this task")
        left.set_ylabel("Nothing to compare")
        losses, order, xs = five_task_bars(right, task)
        for x, k in zip(xs, order):
            right.text(x, losses[k] + 0.012, fmt(losses[k], 3), ha="center", va="bottom", fontsize=10.5,
                       color=PALETTE["teal"] if k == task else PALETTE["ink"], fontweight="bold" if k == task else "normal")
        right.set_xticks(xs, [SHORT[k] for k in order])
        right.set_ylim(0, 0.9)
        right.set_xlabel("Task (bold: chosen), independent learners")
        right.set_ylabel("Loss from Equation (19.2)")
        right.set_title("Loss with no fix", fontsize=11.5)
        return fig

    f = FIX[task]
    names = ["Independent\nlearners", "Highest-level\nonly", "Full mixed\nstrategy"]
    vals = [f["base"], f["single"], f["full"]]
    lb = left.bar(range(3), vals, width=0.6, color=[PALETTE["light"], "#8fa3b8", PALETTE["teal"]], edgecolor=PALETTE["ink"], linewidth=1)
    lb[1].set_hatch("///")
    for x, v in enumerate(vals):
        left.text(x, v + 1.5, fmt(v, 1) + ("\n(derived)" if (x == 2 and f["full_derived"]) else ""), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.set_xticks(range(3), names)
    left.set_ylim(0, 85)
    left.set_xlabel(f"What is deployed ({TASKS[task][0]})")
    left.set_ylabel("Loss (percent of the diagonal mean)")
    left.set_title("Loss under each way of deploying", fontsize=11.5)

    if task == "small2":
        (d0, o0), (d1, o1) = SMALL2_MEANS["independent"], SMALL2_MEANS["population"]
        width = 0.36
        x = np.arange(2)
        rb1 = right.bar(x - width / 2, [d0, d1], width=width, color=PALETTE["teal"], edgecolor=PALETTE["ink"], linewidth=1)
        rb2 = right.bar(x + width / 2, [o0, o1], width=width, color="#8fa3b8", edgecolor=PALETTE["ink"], linewidth=1, hatch="///")
        for bars in (rb1, rb2):
            for bar in bars:
                right.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, fmt(bar.get_height(), 2), ha="center", va="bottom",
                           fontsize=10.5, color=PALETTE["ink"])
        right.set_xticks(x, ["Independent\nlearners", "Full mixed\nstrategy"])
        right.set_ylim(0, 42)
        right.legend([rb1, rb2], ["solid: diagonal", "hatched: off-diagonal"], loc="upper center", ncol=2, fontsize=10.5, frameon=False,
                     columnspacing=1.0, handlelength=1.2)
        right.set_xlabel("Training method (Laser Tag small2)")
        right.set_ylabel("Mean return")
        right.set_title("The diagonal fell, the off-diagonal rose", fontsize=11.5)
    else:
        reds = [f["red_single"], f["red_full"]]
        recomputed = [f["base"] - f["single"], f["base"] - f["full"]]
        rb = right.bar([0, 1], reds, width=0.55, color=["#8fa3b8", PALETTE["teal"]], edgecolor=PALETTE["ink"], linewidth=1)
        rb[0].set_hatch("///")
        for x, (p, r) in enumerate(zip(reds, recomputed)):
            right.text(x, p + 1.5, f"printed {fmt(p, 1)}", ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
            if abs(p - r) > 0.05:
                right.plot([x], [r], "D", color=PALETTE["terracotta"], markersize=8)
                label_point(right, x, r, f"recomputed {fmt(r, 1)}", color=PALETTE["terracotta"], dx=0, dy=-14, ha="center", va="top").set_bbox(BOX)
        right.set_xticks([0, 1], ["Highest-level\nonly", "Full mixed\nstrategy"])
        right.set_ylim(0, 75)
        right.set_xlabel("What is deployed")
        right.set_ylabel("Points removed from the loss")
        right.set_title("Reduction from the independent baseline", fontsize=11.5)
    return fig


def instrument_picture(task="small2", view="means"):
    name, diag, off, printed = TASKS[task]
    loss = lab_loss(diag, off)
    gap = diag - off
    if view == "means":
        fig, loss, mismatch, printed = instrument_figure(task)
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
        extra = ""
        if task == "small2":
            extra = (" Figure 19.1 shows the matrix is not symmetric: the entry for run four's first party with run one's second party is 27.3 and the reverse entry is 3.7, "
                     "so 27.3 / 3.7 = 7.4 (the matrix has more in it than one summary number).")
        metrics = {"Diagonal mean": fmt(diag, 2), "Off-diagonal mean": fmt(off, 2), "Loss from Equation (19.2)": shown}
        interpretation = (f"Loss = ({fmt(diag, 2)} - {fmt(off, 2)}) / {fmt(diag, 2)} = {fmt(gap, 2)} / {fmt(diag, 2)} = {fmt(loss, 3)}. {verdict} "
                          f"The diagonal says how the developed pairs do together; only the off-diagonal says what happens with a stranger.{extra}")
        steps = [f"Diagonal mean (own training partner) = {fmt(diag, 2)}.", f"Off-diagonal mean (a stranger) = {fmt(off, 2)}.",
                 f"Gap = {fmt(diag, 2)} - {fmt(off, 2)} = {fmt(gap, 2)}.", f"Loss = {fmt(gap, 2)} / {fmt(diag, 2)} = {fmt(loss, 3)}."]
        if mismatch:
            steps.append(f"The chapter prints {fmt(printed, 3)}; its own means give {fmt(loss, 3)}, and the chapter flags the difference.")
        if task in ("gathering", "pathfinding"):
            alt = f"Two bars, diagonal {fmt(diag, 2)} and off-diagonal {fmt(off, 2)}, almost equal, and a bar chart of the five losses with {name} nearly flat at {fmt(loss, 3)}."
        else:
            alt = f"Two bars, diagonal {fmt(diag, 2)} above off-diagonal {fmt(off, 2)}, and a bar chart of the five losses with {name} at {fmt(loss, 3)}."
        return fig, metrics, interpretation, {"alt": alt, "steps": steps}

    fig = fix_figure(task)
    if task not in FIX:
        metrics = {"Fix reported by the chapter": "none for this task", "Loss from Equation (19.2)": fmt(loss, 3)}
        interpretation = (f"Loss = ({fmt(diag, 2)} - {fmt(off, 2)}) / {fmt(diag, 2)} = {fmt(loss, 3)}. The chapter reports the population method only on the three Laser Tag maps, "
                          "so there is no before and after to compare for this task. The chapter reads the small loss as a task where coordination is not required; "
                          "it does not report a fix for this task.")
        steps = [f"Loss with independent learners = ({fmt(diag, 2)} - {fmt(off, 2)}) / {fmt(diag, 2)} = {fmt(loss, 3)}.",
                 "The chapter reports no population-method result for this task."]
        return fig, metrics, interpretation, {"alt": f"A message that the chapter reports no fix for {name}, and the five-task loss bars with {name} nearly flat.", "steps": steps}

    f = FIX[task]
    red_full_re = f["base"] - f["full"]
    red_single_re = f["base"] - f["single"]
    metrics = {
        "Loss, independent learners": f"{fmt(f['base'], 1)} percent",
        "Loss, highest-level policy only": f"{fmt(f['single'], 1)} percent",
        "Loss, full mixed strategy": f"{fmt(f['full'], 1)} percent" + (" (derived)" if f["full_derived"] else ""),
        "Points removed, full mixed strategy": fmt(f["red_full"], 1),
    }
    flags = []
    if abs(f["red_single"] - red_single_re) > 0.05:
        flags.append(f"The chapter prints {fmt(f['red_single'], 1)} for the highest-level-only reduction, but the displayed losses give "
                     f"{fmt(f['base'], 1)} - {fmt(f['single'], 1)} = {fmt(red_single_re, 1)}; the chapter flags this difference.")
    if f["full_derived"]:
        flags.append(f"The chapter prints the reduction 56.7 rather than the loss, so the loss left is {fmt(f['base'], 1)} - {fmt(f['red_full'], 1)} = {fmt(f['full'], 1)} points.")
    flag_text = (" " + " ".join(flags)) if flags else ""
    if task == "small2":
        d0, o0 = SMALL2_MEANS["independent"]
        d1, o1 = SMALL2_MEANS["population"]
        loss1 = written_loss(d1, o1)
        lead = (f"Full mixed strategy: ({fmt(d1, 2)} - {fmt(o1, 2)}) / {fmt(d1, 2)} = {fmt(loss1, 3)} (the chapter prints 5.5 percent). "
                f"The diagonal changed by {fmt(d1, 2)} - {fmt(d0, 2)} = {signed(d1 - d0, 2)} and the off-diagonal by {fmt(o1, 2)} - {fmt(o0, 2)} = {signed(o1 - o0, 2)}. "
                f"A report that tracks only the diagonal records the fix as a small regression, while the loss falls by {fmt(f['base'], 1)} - {fmt(f['full'], 1)} = {fmt(red_full_re, 1)} points "
                f"(highest-level only: {fmt(f['base'], 1)} - {fmt(f['single'], 1)} = {fmt(red_single_re, 1)}). ")
        steps = [f"Loss before = ({fmt(d0, 2)} - {fmt(o0, 2)}) / {fmt(d0, 2)} = {fmt(written_loss(d0, o0), 3)}.",
                 f"Loss after, full mixed strategy = ({fmt(d1, 2)} - {fmt(o1, 2)}) / {fmt(d1, 2)} = {fmt(loss1, 3)}.",
                 f"Diagonal change = {fmt(d1, 2)} - {fmt(d0, 2)} = {signed(d1 - d0, 2)}: a regression on the number most teams track.",
                 f"Off-diagonal change = {fmt(o1, 2)} - {fmt(o0, 2)} = {signed(o1 - o0, 2)}: an improvement on the partner-change number.",
                 f"Points removed = {fmt(f['base'], 1)} - {fmt(f['full'], 1)} = {fmt(red_full_re, 1)} (the chapter prints 28.7).",
                 f"Highest-level policy only leaves {fmt(f['single'], 1)} percent, a reduction of {fmt(f['base'], 1)} - {fmt(f['single'], 1)} = {fmt(red_single_re, 1)}."]
    else:
        lead = (f"Full mixed strategy: {fmt(f['base'], 1)} - {fmt(f['full'], 1)} = {fmt(red_full_re, 1)} points removed. "
                f"Highest-level policy only: {fmt(f['base'], 1)} - {fmt(f['single'], 1)} = {fmt(red_single_re, 1)} points removed. ")
        steps = [f"Loss with independent learners = {fmt(f['base'], 1)} percent.",
                 f"Full mixed strategy leaves {fmt(f['full'], 1)} percent: {fmt(f['base'], 1)} - {fmt(f['full'], 1)} = {fmt(red_full_re, 1)} points removed.",
                 f"Highest-level policy only leaves {fmt(f['single'], 1)} percent: {fmt(f['base'], 1)} - {fmt(f['single'], 1)} = {fmt(red_single_re, 1)} points removed."]
        if flags:
            steps.append(" ".join(flags))
    if f["single"] > f["full"]:
        tail = (f"Deploying only the highest-level policy leaves {fmt(f['single'], 1)} percent instead of {fmt(f['full'], 1)}: an agent that trains under the method "
                "and then deploys a single policy has discarded part of what it paid for.")
    else:
        tail = (f"Here the highest-level-only loss ({fmt(f['single'], 1)}) is below the {fmt(f['full'], 1)} implied by the printed 56.7-point reduction, although the chapter says the "
                "highest-level-only losses rise; the chapter does not reconcile these two printed figures, so treat them as reported, not recomputed.")
        steps.append("The printed highest-level-only loss is below the loss implied by the printed 56.7-point reduction; the chapter does not reconcile them.")
    interpretation = " ".join(part for part in (lead.strip(), flag_text.strip(), tail) if part)
    alt = (f"Bars of the loss on {TASKS[task][0]} for independent learners ({fmt(f['base'], 1)}), the highest-level policy only ({fmt(f['single'], 1)}) and the full mixed strategy ({fmt(f['full'], 1)}{', derived from the printed reduction 56.7' if f['full_derived'] else ''}), "
           + ("and the diagonal and off-diagonal means before and after." if task == "small2" else "and the points removed by each."))
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


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
            faced = two
            one = best_response(two)
            mover = "one"
            chosen = one
        else:
            faced = one
            two = best_response(one)
            mover = "two"
            chosen = two
        mover_payoff = payoff(chosen, faced)
        population = sum(payoff(chosen, a) for a in ACTIONS) / len(ACTIONS)
        rows.append({"k": k, "mover": mover, "one": one, "two": two, "faced": faced, "chosen": chosen,
                     "payoff_one": payoff(one, two), "mover_payoff": mover_payoff, "population": population})
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
    gains = [r["mover_payoff"] for r in rows]
    pb = right.bar(xs, gains, width=0.6, color=[PALETTE["teal"] if r["mover"] == "one" else PALETTE["navy"] for r in rows],
                   edgecolor=PALETTE["ink"], linewidth=1)
    right.plot(xs, [r["population"] for r in rows], "D", color=PALETTE["terracotta"], markersize=8, markerfacecolor="white", markeredgewidth=2, linestyle="none")
    right.axhline(0, color=PALETTE["ink"], linewidth=1)
    right.set_xticks(xs, [f"{r['k']}\n{r['mover']}" for r in rows])
    right.set_ylim(-0.6, 1.9)
    right.text(0.02, 0.97, "bars: gain against the option just faced\ndiamonds: average against A, B and C", transform=right.transAxes,
               ha="left", va="top", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
    right.set_xlabel("Update number, and which party moved")
    right.set_ylabel("Payoff to the mover")
    right.set_title("Each gain is local; against all options it is 0", fontsize=11.5)

    first_scores = ", ".join(signed(payoff(a, start), 0) for a in ACTIONS)
    first_option = rows[0]["one"]
    reply = rows[1]["two"] if updates >= 2 else None
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
        "Mover's average against A, B and C": "0.00 every time",
        "Mean payoff to party one": fmt(mean_one, 2),
    }
    interpretation = (
        f"First update: with party two at {start}, party one's payoffs for A, B, C are {first_scores}, so Equation (19.4) picks "
        f"{rows[0]['one']}. Mean payoff to party one over the {updates} updates = ({sum_text}) / {updates} = {fmt(mean_one, 2)}. "
        f"Each mover gains 1 against the partner it faces, yet the partner then moves and the gain is gone: option {first_option} pays "
        f"{signed(payoff(first_option, start), 0)} against {start} but {signed(payoff(first_option, reply), 0)} against {reply}, the move party two "
        f"then makes (the dependence in Equation (19.3)). "
        f"Against a fixed evaluation set that is a uniform mix of the three options, any option pays (1 + 0 + (-1)) / 3 = 0.00, so there is no progress there.{tail}"
    )
    steps = []
    shown_rows = rows if updates <= 6 else rows[:6]
    for r in shown_rows:
        mover = r["mover"]
        faced = r["faced"]
        scores = ", ".join(signed(payoff(a, faced), 0) for a in ACTIONS)
        other = "two" if mover == "one" else "one"
        steps.append(f"Update {r['k']}: party {other} plays {faced}. Payoffs of A, B, C to party {mover} are {scores}, so party {mover} plays {r['chosen']}.")
    if updates > 6:
        steps.append(f"Updates 7 to {updates} repeat updates 1 to {updates - 6}: the cycle has period 6.")
    alt = (f"Left, two stepped lines of the options each party plays over {updates} updates starting with party two at {start}"
           + (f"; party two returns to {start} after update {back}." if back is not None else "; party two has not yet returned to its start.")
           + " Right, bars of +1 for each mover's gain and diamonds at 0 for its average against all three options.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: the return on depth (Figure 19.3), Laser Tag small4

# Loss in percent: independent baseline, then levels 3, 5 and 10. Level 10 is derived from the printed reduction 56.7.
DEPTHS = {"base": ("Independent learners", 71.7), "l3": ("Level three", 24.6), "l5": ("Level five", 15.6), "l10": ("Level ten", 15.0)}
DEPTH_ORDER = ["base", "l3", "l5", "l10"]
PRINTED_L3_REDUCTION = 44.0


def depth_picture(depth="l3", view="loss"):
    base = DEPTHS["base"][1]
    losses = [DEPTHS[k][1] for k in DEPTH_ORDER]
    reductions = [base - v for v in losses]
    idx = DEPTH_ORDER.index(depth)
    name = DEPTHS[depth][0]
    short = ["baseline", "level 3", "level 5", "level 10"]
    gains = [None] + [reductions[i] - reductions[i - 1] for i in range(1, 4)]

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    colors = [PALETTE["teal"] if i == idx else PALETTE["light"] for i in range(4)]
    left.plot(range(4), losses, "-", color=PALETTE["grey"], linewidth=1.4, zorder=1)
    left.scatter(range(4), losses, s=[150 if i == idx else 70 for i in range(4)], c=colors, edgecolors=PALETTE["ink"], linewidths=1.2, zorder=3)
    for i, v in enumerate(losses):
        label_point(left, i, v, fmt(v, 1) + ("\n(derived)" if i == 3 else ""), color=PALETTE["teal"] if i == idx else PALETTE["ink"], dx=8, dy=8, ha="left")
    left.set_xticks(range(4), short)
    left.set_xlim(-0.4, 3.7)
    left.set_ylim(0, 85)
    left.set_xlabel("Depth of the method on Laser Tag small4")
    left.set_ylabel("Loss (percent of the diagonal mean)")
    left.set_title("Loss against depth (Figure 19.3)", fontsize=11.5)

    if view == "loss":
        rb = right.bar(range(4), losses, width=0.6, color=colors, edgecolor=PALETTE["ink"], linewidth=1)
        for i, v in enumerate(losses):
            right.text(i, v + 1.5, fmt(v, 1) + ("\n(derived)" if i == 3 else ""), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        right.set_ylim(0, 85)
        right.set_xlabel("Depth")
        right.set_ylabel("Loss (percent)")
        right.set_title("Loss left at the chosen depth", fontsize=11.5)
        right.set_xticks(range(4), short)
    elif view == "reduction":
        right.bar(range(4), reductions, width=0.6, color=colors, edgecolor=PALETTE["ink"], linewidth=1)
        for i, v in enumerate(reductions):
            right.text(i, v + 1.5, fmt(v, 1), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        right.plot([1], [PRINTED_L3_REDUCTION], "D", color=PALETTE["terracotta"], markersize=8)
        label_point(right, 1, PRINTED_L3_REDUCTION, "printed 44", color=PALETTE["terracotta"], dx=0, dy=-12, ha="center", va="top").set_bbox(BOX)
        right.set_ylim(0, 75)
        right.set_xlabel("Depth")
        right.set_ylabel("Points removed from the baseline loss")
        right.set_title("Reduction from the baseline", fontsize=11.5)
        right.set_xticks(range(4), short)
    else:
        right.bar(range(1, 4), gains[1:], width=0.6, color=colors[1:], edgecolor=PALETTE["ink"], linewidth=1)
        for i in range(1, 4):
            right.text(i, gains[i] + 1.2, fmt(gains[i], 1), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        right.set_xticks(range(1, 4), ["baseline to\nlevel 3", "level 3 to\nlevel 5", "level 5 to\nlevel 10"])
        right.set_xlim(0.4, 3.6)
        right.set_ylim(0, 58)
        right.set_xlabel("Step between tested depths")
        right.set_ylabel("Extra points removed by the step")
        right.set_title("Return on each step", fontsize=11.5)

    loss = DEPTHS[depth][1]
    derived = " (derived)" if depth == "l10" else ""
    metrics = {
        "Depth": name,
        "Loss": f"{fmt(loss, 1)} percent{derived}",
        "Points removed from the baseline": fmt(reductions[idx], 1) if idx else "0.0 (the starting point)",
        "Extra points from the last step": fmt(gains[idx], 1) if idx else "none (the starting point)",
    }
    if idx == 0:
        calc = f"Baseline loss = {fmt(base, 1)} percent, so the points removed so far = {fmt(base, 1)} - {fmt(base, 1)} = 0.0."
        steps = [f"Independent learners lose {fmt(base, 1)} percent of the diagonal mean on small4.",
                 f"Nothing is removed yet: {fmt(base, 1)} - {fmt(base, 1)} = 0.0 points.",
                 "Next, level three of the method (Figure 19.3)."]
    else:
        calc = (f"Points removed at {name.lower()} = {fmt(base, 1)} - {fmt(loss, 1)} = {fmt(reductions[idx], 1)}. "
                f"The step from the previous tested depth added {fmt(reductions[idx], 1)} - {fmt(reductions[idx - 1], 1)} = {fmt(gains[idx], 1)} points.")
        steps = [f"Baseline loss = {fmt(base, 1)} percent; {name.lower()} leaves {fmt(loss, 1)} percent{derived}.",
                 f"Points removed = {fmt(base, 1)} - {fmt(loss, 1)} = {fmt(reductions[idx], 1)}.",
                 f"Previous tested depth removed {fmt(reductions[idx - 1], 1)}, so this step added {fmt(reductions[idx], 1)} - {fmt(reductions[idx - 1], 1)} = {fmt(gains[idx], 1)}."]
    notes = []
    if depth == "l3":
        notes.append("The chapter prints 44 points for level three, but its displayed losses give 71.7 - 24.6 = 47.1; the chapter keeps the two figures separate and does not establish the cause.")
        steps.append("The chapter prints 44 for this reduction; the recomputed 47.1 stays separate.")
    if depth == "l10":
        notes.append("The chapter prints the level-ten reduction 56.7 rather than the loss, so the loss left is 71.7 - 56.7 = 15.0 points.")
    if depth == "l10":
        notes.append("Level ten removes only 0.6 points more than level five, the 'under one point' of the last doubling, and the chapter does not identify why the line flattens.")
    elif depth == "l5":
        notes.append("Level five already removes 56.1 of the 56.7 points that level ten removes.")
    interpretation = calc + " " + " ".join(notes) + " Compare the measured points before extrapolating: three tested depths do not establish a diminishing-return law."
    alt = (f"A line of loss at four depths of the method on small4, falling from {fmt(base, 1)} for independent learners to {fmt(losses[1], 1)}, {fmt(losses[2], 1)} and a derived {fmt(losses[3], 1)} (the printed reduction 56.7 subtracted from the baseline), "
           f"with {name.lower()} highlighted, and a bar chart of the {'loss' if view == 'loss' else ('reduction' if view == 'reduction' else 'return on each step')}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: partner mixtures decide the ranking (laboratory matrices)

MATRICES = {
    "two": [[0.95, 0.2], [0.4, 0.9]],
    "three": [[1.0, 0.0, 0.0], [0.6, 0.6, 0.6], [0.0, 0.0, 1.0]],
}
MIXES = {
    "two": {"target": [0.5, 0.5], "changed": [0.9, 0.1], "tie": [0.56, 0.44], "known": [1.0, 0.0]},
    "three": {"target": [0.2, 0.6, 0.2], "changed": [0.5, 0.0, 0.5], "tie": [0.6, 0.0, 0.4], "known": [1.0, 0.0, 0.0]},
}
MIX_NAMES = {"target": "the declared partner mix", "changed": "the changed (supervisor) mix", "tie": "a mix at the crossing",
             "known": "partner 0 only"}


def mixture_metrics(matrix, weights):
    out = evaluate({"matrix": matrix, "partner_weights": weights, "supervisor_weights": weights})
    return out["metrics"]


def partner_mix_picture(matrix="two", mix="target"):
    M = MATRICES[matrix]
    w = MIXES[matrix][mix]
    k = len(M)
    m = mixture_metrics(M, w)
    values = m["partner_mixture_values"]
    written = [sum(w[j] * M[i][j] for j in range(k)) for i in range(k)]
    if not all(math.isclose(a, b, abs_tol=1e-12) for a, b in zip(values, written)):
        raise AssertionError("laboratory values disagree with the written weighted sums")
    diag = [M[i][i] for i in range(k)]
    jpc = m["joint_policy_correlation_loss"]
    top = argmax_set({i: v for i, v in enumerate(values)}, 1e-9)
    diag_top = argmax_set({i: v for i, v in enumerate(diag)}, 1e-9)
    names = [f"Policy {i}" for i in range(k)]

    def join(ids):
        return " and ".join(names[i] for i in ids)

    winner = join(top) + (" tie" if len(top) > 1 else "")
    # largest asymmetry
    best = (0.0, None)
    for s in range(k):
        for t in range(s + 1, k):
            d = abs(M[s][t] - M[t][s])
            if d > best[0] + 1e-12:
                best = (d, (s, t))
    s, t = best[1]

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    grid = np.array(M)
    left.imshow(grid, cmap="Blues", vmin=0, vmax=1.35, aspect="auto")
    for i in range(k):
        for j in range(k):
            kind = "matched" if i == j else "stranger"
            left.text(j, i, f"{fmt(grid[i, j], 2)}\n{kind}", ha="center", va="center", fontsize=10.5 if k == 3 else 11.5,
                      color="white" if grid[i, j] > 0.6 else PALETTE["ink"])
            if i == j:
                left.add_patch(plt_rect(j, i))
    left.set_xticks(range(k), [f"{j}\nweight {fmt(w[j], 2)}" for j in range(k)])
    left.set_yticks(range(k), [str(i) for i in range(k)])
    left.set_xlabel("Partner t (column), with the chance of meeting it")
    left.set_ylabel("Policy s (row)")
    left.set_title("Matrix M: success probability", fontsize=11.5)
    left.grid(False)

    xs = np.arange(k)
    width = 0.36
    b1 = right.bar(xs - width / 2, diag, width=width, color="#8fa3b8", edgecolor=PALETTE["ink"], linewidth=1, hatch="///")
    b2 = right.bar(xs + width / 2, values, width=width, color=[PALETTE["teal"] if i in top else PALETTE["light"] for i in range(k)],
                   edgecolor=PALETTE["ink"], linewidth=1)
    for bars, digits in ((b1, 2), (b2, 3)):
        for bar in bars:
            right.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02, fmt(bar.get_height(), digits), ha="center", va="bottom",
                       fontsize=10.0, color=PALETTE["ink"])
    right.set_xticks(xs, [f"Policy {i}" for i in range(k)])
    right.set_ylim(0, 1.3)
    right.set_xlim(-0.6, k - 0.4)
    right.legend([b1, b2], ["hatched: matched partner", "solid: against the mix"], loc="upper center", ncol=2, fontsize=10.0, frameon=False,
                 columnspacing=0.8, handlelength=1.2)
    right.set_xlabel("Policy (teal: ranks first against the mix)")
    right.set_ylabel("Success probability")
    right.set_title("Diagonal against the partner mix", fontsize=11.5)

    if len(top) > 1:
        verdict = (f"{join(top)} tie at {fmt(values[top[0]], 3)}, so the ranking rule does not choose between them; the diagonal alone names {join(diag_top)}.")
    elif top == diag_top:
        verdict = f"{names[top[0]]} ranks first, which agrees with the diagonal here."
    else:
        verdict = f"{names[top[0]]} ranks first, although the diagonal alone names {join(diag_top)}."
    sums = []
    for i in range(k):
        terms = " + ".join(f"{fmt(w[j], 2)} x {fmt(M[i][j], 2)}" for j in range(k))
        sums.append(f"Policy {i} = {terms} = {fmt(values[i], 3)}")
    sym = (f"The matrix is not symmetric: cell ({s}, {t}) is {fmt(M[s][t], 2)} but cell ({t}, {s}) is {fmt(M[t][s], 2)}, "
           f"so a row and the matching column answer different questions.")
    if mix == "tie" and matrix == "two":
        cross = " The two policies tie where 0.2 + 0.75 x p = 0.9 - 0.5 x p, that is p = 0.7 / 1.25 = 0.56."
    elif mix == "tie":
        cross = " Policy 0 and the generalist (policy 1) both score 0.6 when the weight on partner 0 is 0.6: 0.6 x 1.00 + 0.4 x 0.00 = 0.60."
    else:
        cross = ""
    metrics = {f"Policy {i} against the mix": fmt(values[i], 3) for i in range(k)}
    metrics["Ranks first"] = winner
    metrics["Diagonal alone names"] = join(diag_top) + (" (tie)" if len(diag_top) > 1 else "")
    metrics["Loss from Equation (19.2)"] = fmt(jpc, 3)
    interpretation = ". ".join(sums) + f". {verdict} {sym} The loss is fixed by the matrix, whatever the mix: " \
        f"({fmt(sum(diag) / k, 3)} - {fmt((sum(map(sum, M)) - sum(diag)) / (k * (k - 1)), 3)}) / {fmt(sum(diag) / k, 3)} = {fmt(jpc, 3)}.{cross}"
    steps = [f"Weights on partners 0 to {k - 1} are {', '.join(fmt(x, 2) for x in w)} ({MIX_NAMES[mix]})."]
    steps += [sums[i] + "." for i in range(k)]
    steps.append(verdict)
    alt = (f"A {k} by {k} matrix of success probabilities with the diagonal outlined, and bars comparing each policy's matched-partner value with its value against the mix; "
           f"{join(top)} {'tie' if len(top) > 1 else 'ranks first'}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


def plt_rect(j, i):
    from matplotlib.patches import Rectangle
    return Rectangle((j - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=PALETTE["ink"], linewidth=3)


CHAPTER = {
    "number": 19,
    "title": "When Another Mind Becomes Part of the World",
    "subtitle": "A score earned beside one partner may not travel to another, so the partner belongs inside the measurement.",
    "summary": (
        "These four demonstrations follow the chapter's cross-play matrix. The first computes the loss statistic on the chapter's "
        "printed means and shows what its population fix did to three reported numbers. The second shows why simply optimizing against the current partner "
        "can go in circles. The third is the chapter's return on depth. The fourth shows how the partners you expect to meet decide which "
        "policy ranks first, on the laboratory's default, changed and transfer cases."
    ),
    "ask_skill": {"prompt": (
        "Here is my cross-play matrix and the partner mix I expect in deployment. Compute the diagonal mean, the off-diagonal mean and the loss, "
        "rank my policies against that mix, and tell me which cells I still need to measure before I trust the diagonal.")},
    "demos": [
        {
            "id": "C19-D01",
            "title": "Diagonal against off-diagonal",
            "question": "How much of a score is lost when a policy meets a partner from another training run instead of its own, and what did the fix change?",
            "equations": [EQ_MATRIX, EQ_JPC],
            "symbols": (
                "M_st is the mean return when the first party uses the policy from training run s and the second party uses the policy "
                "from run t. diag(M) is the average of the entries with s equal to t (matched partners). off(M) is the average of the "
                "entries with s different from t (strangers). JPC(M), the joint policy correlation loss, is their difference divided by diag(M), a proportional loss. E is the mean over many episodes, u is the "
                "joint return of the two parties (their returns added together), and pi_1^(s), pi_2^(t) are the policies the first and second party use. "
                "Returns here are in the units of the chapter's table. In the fix view, 'highest-level only' and 'full mixed strategy' are the two ways the chapter's population method can be deployed."
            ),
            "prediction": "For the small4 map the diagonal mean is 20.15 and the off-diagonal mean is 5.71. Before selecting it, guess whether the loss is nearer 0.3 or 0.7.",
            "prediction_options": ["Nearer 0.3", "Nearer 0.7"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "(20.15 - 5.71) / 20.15 = 14.44 / 20.15 = 0.717. Select Laser Tag small4 to see it.",
                "incorrect": "The gap is 20.15 - 5.71 = 14.44, and 14.44 / 20.15 = 0.717, nearer 0.7. Select Laser Tag small4 to see it.",
            },
            "misconception": {
                "title": "Reading the loss as a universal measure of cooperation",
                "text": ("The chapter says the denominator is meaningful only where the reference score supports the comparison, and the statistic is not a universal measure of cooperation. "
                         "A loss of 0.003 records a small difference between the evaluated means; it does not show the parties are interchangeable."),
            },
            "scope_note": {
                "text": ("The anchor is a single conference paper reporting its authors' own method on gridworld tasks, and its reductions are their measurements rather than a general rate. "
                         "The instrument requires multiple independent training runs, which many deployments cannot afford. In asymmetric games the effect varies across parties."),
                "source_section": SCOPE_SECTION,
            },
            "explanation": (
                "Equation (19.1) fills a table with one entry for every pairing of runs. Equation (19.2) averages the diagonal, averages "
                "the off-diagonal, subtracts, and divides by the diagonal average. A loss near zero means strangers score about what "
                "matched partners score; a loss near one means the score almost vanishes. The fix view shows the chapter's population method "
                "moving the loss and, on the smallest map, moving the two means in opposite directions."
            ),
            "application": (
                "When two components of a system were developed together, evaluate them also against independently developed replacements, "
                "and report the diagonal, the off-diagonal and the loss, not only the diagonal."
            ),
            "assumptions": (
                "The statistic is meaningful only when the diagonal mean is positive, and it compares particular pairings under one "
                "procedure. It is not a universal measure of cooperation and does not show why a gap appears. A small loss does not show "
                "the policies are independent or interchangeable. The fix view uses only losses the chapter prints, plus one subtraction for the small4 full-strategy loss."
            ),
            "check": "A matrix has a diagonal mean of 10 and an off-diagonal mean of 8. What is the loss, and what changes if the diagonal mean is 0?",
            "answer": "(10 - 8) / 10 = 0.20. With a diagonal mean of 0 the denominator is 0, so the statistic is undefined and the chapter says to report the difference instead.",
            "provenance": (
                "Values the chapter prints for three Laser Tag maps and two control tasks (the diagonal and off-diagonal means, and in the fix view its printed losses and reductions), "
                "plus recomputations marked as such, arranged here as a constructed teaching example; the loss is computed with the laboratory's cross-play function."
            ),
            "source_section": "What the instrument found",
            "source_anchor": "what-the-instrument-found",
            "controls": [
                {"key": "task", "label": "Task", "values": ["small2", "small3", "small4", "gathering"], "default": "small2",
                 "value_labels": ["Laser Tag small2", "Laser Tag small3", "Laser Tag small4", "Gathering"]},
                {"key": "view", "label": "View", "values": ["means", "fix"], "default": "means",
                 "value_labels": ["Means by pairing", "What the population fix did"]},
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
                "picks one of three options A, B, C. A beats C, B beats A and C beats B; a win pays 1, a loss pays (-1) and a tie pays 0. "
                "An update is one party switching to its best answer; the parties alternate, party one first."
            ),
            "prediction": "Start party two at A and show 6 updates. Does the sequence stop at some pair of options, or return to where it began?",
            "prediction_options": ["It stops at a pair of options", "It returns to where it began"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Party two is back at A after 6 updates, so the cycle repeats. Set Updates shown to 6 to see the dotted line.",
                "incorrect": "It does not stop: party two is back at A after 6 updates, so the cycle repeats. Set Updates shown to 6 to see the dotted line.",
            },
            "stepper": "updates",
            "misconception": {
                "title": "Every correct update must make progress",
                "text": ("Each of the six updates is an exact best response and improves its mover's payoff against the opponent it faces, yet the sequence goes nowhere. "
                         "The chapter's point is that each update can improve against the current opponent without producing progress against a fixed evaluation population."),
            },
            "scope_note": {
                "text": ("Best-response cycling is one distinct difficulty with adapting counterparties. The reported 34.2 percent transfer loss does not identify a cycle or prove that the training procedure has no single destination."),
                "source_section": "Best-response cycling is one distinct difficulty with adapting counterparties",
            },
            "explanation": (
                "Each update computes Equation (19.4) exactly against the option the other party is playing now. Because the other party then "
                "moves, the world the first party optimized against is gone, which is the added argument in Equation (19.3). In this "
                "game the sequence of options each party plays repeats every six updates. The diamonds show the same option scored against a fixed, uniform mix of the three "
                "options (equal weights): its average is 0, so the +1 gains never add up to progress against that set."
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
                {"key": "start", "label": "Where party two starts", "values": ["A", "B", "C"], "default": "A"},
            ],
            "function": "cycle_picture",
        },
        {
            "id": "C19-D03",
            "title": "Return on depth",
            "question": "How much of the available reduction in transfer loss does each added stretch of the fix buy?",
            "equations": [EQ_JPC],
            "symbols": (
                "JPC(M), the joint policy correlation loss, is (diag(M) - off(M)) / diag(M), a proportional loss, shown here in percent of the diagonal mean. diag(M) is the mean return against the policy's own training partner and off(M) the mean return against a stranger. "
                "The method trains in levels: level 0 plays uniformly at random and each higher level learns a policy that best responds to a mixture over the levels below. "
                "Depth is the number of levels. The values are for the largest map, Laser Tag small4."
            ),
            "prediction": "Level five removes 56.1 points of loss. Will level ten remove clearly more or almost the same?",
            "prediction_options": ["Clearly more", "Almost the same"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Level ten removes 56.7 points, only 0.6 more than level five. Choose Level ten and read the Extra points from the last step.",
                "incorrect": "Doubling the depth from level five to level ten does not double the gain: level five already removes 56.1 points and level ten removes 56.7, only 0.6 more. Choose Level ten and read the Extra points from the last step.",
            },
            "stepper": "depth",
            "misconception": {
                "title": "Treating the flattening as a law of diminishing returns",
                "text": ("Three tested depths show a small additional improvement from level five to level ten in this setting. The chapter says they do not identify the reason for that flattening, "
                         "establish a universal diminishing-return law, or show that remaining failures lie beyond the method's reach."),
            },
            "scope_note": {
                "text": ("The anchor is a single conference paper reporting its authors' own method on gridworld tasks, and its reductions are their measurements rather than a general rate."),
                "source_section": SCOPE_SECTION,
            },
            "explanation": (
                "Each point is the loss left after the method is trained to that depth, and each bar of the third view is the extra reduction bought by moving to the next tested depth. "
                "Most of the reduction arrives by level three and almost all by level five, so the last doubling of effort buys under one point. "
                "The chapter also shows where its own printed figures and recomputed differences disagree (44 against 47.1 at level three), and this view keeps them separate."
            ),
            "application": (
                "Before paying for more depth in a training procedure, measure the loss at two or three intermediate depths and compare the points each step buys with its cost."
            ),
            "assumptions": (
                "One method on one map from one paper. Level ten is the printed reduction 56.7 subtracted from the baseline. The flattening is observed at three tested depths, not explained, "
                "and it may not appear on other maps, with other methods, or for other counterparties."
            ),
            "check": "A different procedure loses 60 points at baseline, 25 at depth 4 and 20 at depth 8. How many extra points does the step from depth 4 to depth 8 buy?",
            "answer": "Points removed at depth 4: 60 - 25 = 35. At depth 8: 60 - 20 = 40. The step adds 40 - 35 = 5 points, much less than the first 35.",
            "provenance": "Constructed example: the chapter's printed small4 baseline and level three and five losses, and the printed level-ten reduction, used as a teaching example.",
            "source_section": "How much of the method is doing the work",
            "source_anchor": "how-much-of-the-method-is-doing-the-work",
            "controls": [
                {"key": "depth", "label": "Depth of the method", "values": ["base", "l3", "l5", "l10"], "default": "l3",
                 "value_labels": ["Independent learners (baseline)", "Level three", "Level five", "Level ten"]},
                {"key": "view", "label": "Right panel", "values": ["loss", "reduction", "step"], "default": "loss",
                 "value_labels": ["Loss left", "Points removed from the baseline", "Return on each step"]},
            ],
            "function": "depth_picture",
        },
        {
            "id": "C19-D04",
            "title": "Which partners will it meet?",
            "question": "If the diagonal favors one policy, can the partners you expect to meet make another policy the better choice?",
            "equations": [EQ_MATRIX, EQ_JPC],
            "symbols": (
                "M_st is the success probability of policy s (row) against partner t (column). The weight under each column is the probability that the policy "
                "meets that partner. A policy's value against the mix is its row averaged with these weights. JPC(M), the joint policy correlation loss, is the loss of Equation (19.2) for the whole matrix. In this demonstration u is a success indicator (1 for success, 0 otherwise), "
                "so each entry M_st = E[u] is a success probability. The changed (supervisor) mix is the distribution a supervisor routes to; the laboratory calls it the changed partner or supervisor distribution."
            ),
            "prediction": "With the two-policy matrix and equal weights, policy 0 has the better diagonal entry. Which policy has the better value against the mix?",
            "prediction_options": ["Policy 0", "Policy 1"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Policy 1 scores 0.5 x 0.4 + 0.5 x 0.9 = 0.65 against 0.575 for policy 0, despite the weaker diagonal. The default state shows it.",
                "incorrect": "The diagonal alone does not give the ranking: policy 0 scores 0.5 x 0.95 + 0.5 x 0.2 = 0.575 against the mix, while policy 1 scores 0.5 x 0.4 + 0.5 x 0.9 = 0.65, despite the weaker diagonal. The default state shows it.",
            },
            "misconception": {
                "title": "Assuming the matrix is symmetric",
                "text": ("Readers tend to assume a cross-play matrix is symmetric, and that assumption produces a wrong diagnosis. The cell for one role assignment and the cell for the opposite assignment "
                         "record different pairings, so read rows (a first-party policy across partners) and columns (a second-party policy across replacements) separately."),
            },
            "scope_note": {
                "text": ("A partner mixture is a declared deployment distribution. The chapter says the off-diagonal measures the tested replacements under the same evaluation conditions; it does not predict every future replacement, and Equation (19.2) cannot supply missing replacements."),
                "source_section": "Equation (19.2) summarizes the measured matrix; it cannot supply missing replacements",
            },
            "explanation": (
                "The matrix holds fixed numbers. The weights decide how much each column counts, so changing the mix changes which row averages higher "
                "while the matrix, and the loss computed from it, stay the same. In the three-policy matrix, one policy succeeds with probability 0.6 against every partner "
                "and two specialists succeed only against their own, so the mix decides whether specialization or breadth wins."
            ),
            "application": (
                "Before choosing a component, write down the partner distribution you expect in use, and check whether the ranking "
                "survives plausible changes to it, instead of ranking by the diagonal."
            ),
            "assumptions": (
                "Two constructed matrices and declared partner mixes; the weighted average over partners is this laboratory's way of "
                "asking the deployment question, not a formula printed in the chapter. It assumes the matrix entries share one success definition, "
                "and that partners do not change how they behave once a policy is chosen."
            ),
            "check": "For the two-policy matrix with weight 0.7 on partner 0, which policy ranks first, and what are the two values?",
            "answer": "Policy 0: 0.7 x 0.95 + 0.3 x 0.2 = 0.725. Policy 1: 0.7 x 0.4 + 0.3 x 0.9 = 0.55. Policy 0 ranks first, since 0.7 is above the crossing at 0.56.",
            "provenance": "Constructed example: the laboratory's default two-policy matrix with its default and changed partner weights, and its transfer three-policy matrix with the transfer weights, computed with the laboratory's cross-play function.",
            "source_section": "Self-play is the diagonal",
            "source_anchor": "self-play-is-the-diagonal",
            "controls": [
                {"key": "matrix", "label": "Matrix", "values": ["two", "three"], "default": "two",
                 "value_labels": ["Two policies (default case)", "Three policies (transfer case)"]},
                {"key": "mix", "label": "Partner mix", "values": ["target", "changed", "tie", "known"], "default": "target",
                 "value_labels": ["Declared mix", "Changed (supervisor) mix", "A mix where two policies tie", "Partner 0 only"]},
            ],
            "function": "partner_mix_picture",
        },
    ],
}

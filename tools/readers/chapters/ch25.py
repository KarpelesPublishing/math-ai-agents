"""Chapter 25 reader: Improving an Agent Without Trusting the Improvement.

Four demonstrations built on Equations (25.1) to (25.4).

Demonstration 1 follows one accepted version into a canary: a monitored
release whose rollback rule is declared before the first period, with the
model weights frozen throughout (Equation 25.1). Demonstration 2 calls the
laboratory's own development-guard gate (math_ai_agents.chapters.ch25.evaluate)
on the notebook's default, changed and transfer cases and shows the paired
guard cases behind the gain (Equation 25.2). Demonstration 3 evaluates the
chapter's constructed false-accept bound (Equation 25.3), compares it with one
exact tail and marks which guard decisions the accounting still covers once a
guard result has reached the designer. Demonstration 4 evaluates the
four-condition acceptance rule (Equation 25.4); the laboratory gate implements
only a simpler rule, so those numbers are computed directly. Every number is a
constructed teaching value; no result about a real agent is claimed.
"""
import math
from fractions import Fraction
from functools import lru_cache

import numpy as np
from matplotlib.patches import Rectangle

from math_ai_agents.chapters.ch25 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

# Equations are copied from the chapter, with only the tag removed.
EQ_FAMILY = r"\phi'\in\mathcal M(\phi_t,e_t), \qquad \theta_{t+1}=\theta_t."
EQ_SELECT = (
    r"\begin{aligned}"
    r"&\widehat\Delta_D(\phi_j)=\widehat V_D(\phi_j)-\widehat V_D(\phi_t), "
    r"\qquad \phi'=\arg\max_{\phi_j\in\Phi_t}\widehat\Delta_D(\phi_j),\\"
    r"&Z_i(\phi')\in[-1,1], \qquad \widehat\Delta_G(\phi')=\frac{1}{m}\sum_{i=1}^{m}Z_i(\phi')."
    r"\end{aligned}"
)
EQ_BOUND = (
    r"\Pr\!\left(\widehat\Delta_G(\phi')\geq 0.25\right) \leq "
    r"\exp\!\left(-\frac{200(0.25)^2}{2}\right) \approx 0.00193 "
    r"\quad\text{for every fixed }\phi'\text{ with }\Delta(\phi')\leq0, "
    r"\qquad 10(0.00193)\approx0.0193."
)
EQ_ACCEPT = (
    r"\operatorname{accept}(\phi')=1 \iff \begin{cases}"
    r"\widehat\Delta_G(\phi')\geq\tau,\\"
    r"\widehat C_G(\phi')\leq c-\varepsilon_{\mathrm{safe}},\\"
    r"\operatorname{Authorized}_{\mathcal G}(\phi')=1,\\"
    r"\operatorname{Rollback}(\phi',\phi_t)=1."
    r"\end{cases}"
)

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.92}
PINK = "#f1d9c9"
GREY = "#e6eaee"


def sig(x, digits=3):
    """Fixed-decimal text with the given number of significant digits (no exponent)."""
    x = float(x)
    if x == 0:
        return "0"
    places = max(0, digits - 1 - int(math.floor(math.log10(abs(x)))))
    return f"{x:.{places}f}"


def num_list(values, digits=2):
    return ", ".join(fmt(v, digits) for v in values)


# Demonstration 1: a canary with rollback rules fixed before it starts

PERIODS = 8
LIMIT_C = 1.00      # c, the current cost limit (constructed units)
MARGIN = 0.10       # epsilon_safe, the reserved margin
TRACES = {
    "steady": [0.80, 0.82, 0.81, 0.83, 0.82, 0.84, 0.83, 0.82],
    "creeping": [0.80, 0.83, 0.86, 0.89, 0.92, 0.95, 0.98, 1.01],
    "spike": [0.80, 0.81, 0.95, 0.82, 0.81, 0.80, 0.82, 0.81],
}
TRACE_NAMES = {
    "steady": "steady cost",
    "creeping": "cost creeping up",
    "spike": "one cost spike",
}


def first_over(costs, boundary):
    """First 1-based period whose cost is strictly above the boundary, or None."""
    for i, c in enumerate(costs):
        if c > boundary + 1e-12:
            return i + 1
    return None


def canary_picture(trace="creeping", rule="declared", fallback="restore"):
    costs = TRACES[trace]
    declared = LIMIT_C - MARGIN
    boundary = declared if rule == "declared" else LIMIT_C
    alert = first_over(costs, boundary)
    alert_declared = first_over(costs, declared)
    in_service = PERIODS if alert is None else alert
    after = PERIODS - in_service
    xs = list(range(1, PERIODS + 1))

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.plot(xs, costs, "-o", color=PALETTE["navy"], linewidth=2, markersize=6)
    left.axhline(boundary, color=PALETTE["ink"], linestyle="dashed", linewidth=1.5)
    if rule == "declared":
        blabel = f"boundary {fmt(boundary, 2)} (set first)"
    else:
        blabel = f"boundary {fmt(boundary, 2)} (set after looking)"
        left.axhline(declared, color=PALETTE["gold"], linestyle="dotted", linewidth=1.5)
        label_point(left, 1, declared, f"declared {fmt(declared, 2)}", color=PALETTE["gold"], dx=2, dy=-4,
                    ha="left", va="top").set_bbox(BOX)
    label_point(left, 0.65, boundary, blabel, color=PALETTE["ink"], dx=0, dy=4, ha="left", va="bottom").set_bbox(BOX)
    if alert is not None:
        left.plot([alert], [costs[alert - 1]], "X", color=PALETTE["terracotta"], markersize=13, zorder=6)
        label_point(left, alert, costs[alert - 1], f"alert, period {alert}", color=PALETTE["terracotta"],
                    dx=-10 if alert >= 7 else 0, dy=-14 if alert >= 7 else 12, ha="right" if alert >= 7 else "center",
                    va="top" if alert >= 7 else "bottom").set_bbox(BOX)
    else:
        left.text(0.97, 0.06, "no alert in 8 periods", transform=left.transAxes, ha="right", va="bottom",
                  fontsize=10.5, color=PALETTE["teal"], bbox=BOX)
    left.set_xlim(0.6, PERIODS + 0.4)
    left.set_ylim(0.70, 1.10)
    left.set_xticks(xs)
    left.set_xlabel("Canary period")
    left.set_ylabel("Cost per task (constructed units)")
    left.set_title("Monitored cost against the rollback boundary", fontsize=11.5)

    # Right panel: what runs in each period. Weights never change.
    fallback_word = "phi_t restored" if fallback == "restore" else "new tasks held"
    for x in xs:
        right.add_patch(Rectangle((x - 0.5, 1.15), 1, 0.7, facecolor=GREY, edgecolor=PALETTE["grey"], hatch="xxx", linewidth=0.8))
        served = x <= in_service
        if served:
            right.add_patch(Rectangle((x - 0.5, 0.15), 1, 0.7, facecolor=PALETTE["teal"], edgecolor="white", linewidth=0.8))
        elif fallback == "restore":
            right.add_patch(Rectangle((x - 0.5, 0.15), 1, 0.7, facecolor=PALETTE["navy"], edgecolor="white", linewidth=0.8))
        else:
            right.add_patch(Rectangle((x - 0.5, 0.15), 1, 0.7, facecolor="white", edgecolor=PALETTE["terracotta"], hatch="///", linewidth=1))
    right.text((PERIODS + 1) / 2, 1.5, "theta unchanged in every period", ha="center", va="center", fontsize=10.5,
               color=PALETTE["ink"], bbox=BOX)
    right.text((1 + in_service) / 2, 0.5, "phi' in service", ha="center", va="center", fontsize=10.5,
               color="white")
    if after:
        right.text((in_service + 1 + PERIODS) / 2, 0.5, fallback_word, ha="center", va="center", fontsize=10.5,
                   color="white" if fallback == "restore" else PALETTE["terracotta"],
                   bbox=None if fallback == "restore" else BOX)
    right.set_xlim(0.5, PERIODS + 0.5)
    right.set_ylim(0, 2.0)
    right.set_xticks(xs)
    right.set_yticks([0.5, 1.5], ["Procedure in service", "Model weights theta"])
    right.grid(alpha=0)
    right.set_xlabel("Canary period")
    right.set_ylabel("Part of the agent")
    right.set_title("What runs, period by period", fontsize=11.5)

    fall_text = ("restore the parent version phi_t" if fallback == "restore"
                 else "hold new tasks and hand the decision to the authority holder")
    metrics = {
        "Boundary used": f"{fmt(boundary, 2)} ({'declared before the canary' if rule == 'declared' else 'chosen after looking'})",
        "Alert under the declared 0.90": "none" if alert_declared is None else f"period {alert_declared}",
        "Alert under the boundary used": "none" if alert is None else f"period {alert}",
        "Periods under phi'": f"{in_service} of {PERIODS}",
        "Fallback after an alert": "restore phi_t" if fallback == "restore" else "hold new tasks, call authority holder",
        "Model parameters changed": "0 (theta stays frozen)",
    }
    cost_text = num_list(costs[:in_service] if alert else costs)
    if rule == "declared":
        head = f"Boundary = c - margin = {fmt(LIMIT_C, 2)} - {fmt(MARGIN, 2)} = {fmt(boundary, 2)}, fixed before period 1."
    else:
        head = (f"The declared boundary was c - margin = {fmt(LIMIT_C, 2)} - {fmt(MARGIN, 2)} = {fmt(declared, 2)}. Here the "
                f"boundary was instead set to c = {fmt(boundary, 2)} after the costs were seen.")
    if alert is None:
        body = (f" Costs run {cost_text}, and the highest, {fmt(max(costs), 2)}, is not above {fmt(boundary, 2)}, so no alert fires "
                f"and the canary ends at its maximum duration of {PERIODS} periods.")
        if rule != "declared" and alert_declared is not None:
            body += (f" The declared boundary {fmt(declared, 2)} would have fired in period {alert_declared} "
                     f"({fmt(costs[alert_declared - 1], 2)} > {fmt(declared, 2)}), so moving it hid the alert.")
        elif rule != "declared":
            body += " The costs never cross either boundary, so moving the boundary changes nothing for this trace."
        tail = " The weights theta did not change in any period."
    else:
        body = (f" Costs run {cost_text}; the first above {fmt(boundary, 2)} is period {alert} ({fmt(costs[alert - 1], 2)} > "
                f"{fmt(boundary, 2)}), so the alert fires there and the declared fallback, {fall_text}, applies"
                + (f" from period {alert + 1}." if after else ". No period remains after it."))
        if rule != "declared" and alert_declared is not None and alert_declared != alert:
            body += (f" Under the declared boundary {fmt(declared, 2)} the alert would have fired in period {alert_declared}, "
                     f"{alert - alert_declared} periods earlier.")
        tail = f" That is {in_service} of {PERIODS} periods under phi' and theta unchanged throughout."
    interpretation = head + body + tail

    steps = [
        (f"Boundary fixed before period 1: c - margin = {fmt(LIMIT_C, 2)} - {fmt(MARGIN, 2)} = {fmt(declared, 2)}."
         if rule == "declared" else
         f"Declared boundary {fmt(LIMIT_C, 2)} - {fmt(MARGIN, 2)} = {fmt(declared, 2)}; here it was moved to {fmt(boundary, 2)} after looking."),
        f"Observed cost per period: {num_list(costs)}.",
        (f"First period above {fmt(boundary, 2)}: period {alert} with cost {fmt(costs[alert - 1], 2)}." if alert
         else f"No period is above {fmt(boundary, 2)}; the highest cost is {fmt(max(costs), 2)}."),
        (f"The alert fires in period {alert}; the declared fallback is {fall_text}." if alert
         else f"No alert, so the canary ends at its maximum duration of {PERIODS} periods and the decision stays with the owner."),
        f"theta at step t + 1 equals theta at step t in every period, so rollback only changes the procedure version.",
    ]
    if alert:
        alt = (f"Cost per period against a dashed boundary at {fmt(boundary, 2)}; an alert marker sits at period {alert}. "
               f"Beside it, the procedure in service is phi prime for {in_service} periods and then "
               f"{'the restored parent version' if fallback == 'restore' else 'held new tasks'}; the weights row never changes.")
    else:
        alt = (f"Cost per period stays below the dashed boundary at {fmt(boundary, 2)} for all {PERIODS} periods, with no alert. "
               "Beside it, phi prime stays in service the whole time and the weights row never changes.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: development picks, the guard checks one frozen choice

SCENARIOS = {
    "default": {
        "baseline": [True, False, True, False],
        "threshold": 0.2,
        "candidates": {
            "flashy": {"development": [True, True, True, True], "guard": [True, False, True, False]},
            "steady": {"development": [True, True, True, False], "guard": [True, True, True, False]},
        },
    },
    "changed": {
        "baseline": [True, False, True, False],
        "threshold": 0.2,
        "candidates": {
            "flashy": {"development": [True, True, True, True], "guard": [True, True, True, False]},
            "steady": {"development": [True, True, True, False], "guard": [True, True, True, False]},
        },
    },
    "transfer": {
        "baseline": [False, True],
        "threshold": 0.1,
        "candidates": {
            "proposal": {"development": [True, True], "guard": [True, True]},
        },
    },
}


def lab_gate(case, picks, reused):
    sc = SCENARIOS[case]
    data = {
        "baseline_guard": sc["baseline"],
        "minimum_guard_gain": float(sc["threshold"]),
        "guard_reused": bool(reused),
        "candidates": [dict(name=n, **sc["candidates"][n]) for n in picks],
    }
    return evaluate(data)


def value_label_height(value, threshold):
    """Height and alignment for a bar label so the threshold line never crosses the text."""
    half = 0.04
    for y, va, lo, hi in ((value + 0.03, "bottom", value + 0.03, value + 0.03 + 2 * half),
                          (value / 2, "center", value / 2 - half, value / 2 + half)):
        if value >= 0.12 or va == "bottom":
            if not (lo - 0.015 <= threshold <= hi + 0.015):
                return y, va
    return threshold + 0.02, "bottom"


def gate_picture(case="default", guard="clean", chooser="development"):
    sc = SCENARIOS[case]
    names = list(sc["candidates"])
    threshold = sc["threshold"]
    baseline = sc["baseline"]
    m = len(baseline)
    dev_out = lab_gate(case, names, guard == "reused")
    dev_pick = dev_out["metrics"]["selected_candidate"]
    rates = {r["name"]: r["development_rate"] for r in dev_out["tables"]}
    gains = {n: lab_gate(case, [n], False)["metrics"]["selected_guard_gain"] for n in names}
    # A guard-based pick only differs from the development pick when the guard separates the candidates.
    best_guard = max(gains.values())
    if chooser == "guard" and gains[dev_pick] < best_guard - 1e-12:
        pick = next(n for n in names if gains[n] >= best_guard - 1e-12)
        shaped = True
    else:
        pick = dev_pick
        shaped = False
    reused = guard == "reused"
    out = lab_gate(case, [pick], reused or shaped)
    gain = out["metrics"]["selected_guard_gain"]
    accepted = bool(out["metrics"]["release_accepted"])
    pair = sc["candidates"][pick]["guard"]
    z = [int(c) - int(b) for c, b in zip(pair, baseline)]
    dev_cases = {n: len(sc["candidates"][n]["development"]) for n in names}
    dev_wins = {n: sum(sc["candidates"][n]["development"]) for n in names}

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    for i, n in enumerate(names):
        is_dev = n == dev_pick
        left.bar(i, rates[n], width=0.55, color=PALETTE["teal"] if is_dev else GREY,
                 edgecolor=PALETTE["teal"] if is_dev else PALETTE["grey"], hatch=None if is_dev else "///", linewidth=1.2)
        left.text(i, rates[n] + 0.03, fmt(rates[n], 2), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"], bbox=BOX)
    tick = []
    for n in names:
        if n == dev_pick:
            tick.append(f"{n}\n(development\nwinner)")
        elif shaped and n == pick:
            tick.append(f"{n}\n(guard's pick)")
        else:
            tick.append(f"{n}\n(not picked)")
    left.set_xticks(range(len(names)), tick)
    left.set_xlim(-0.6, len(names) - 0.4)
    left.set_ylim(0, 1.2)
    left.set_xlabel("Candidate procedure")
    left.set_ylabel("Development success rate")
    left.set_title("Step 1: development picks one", fontsize=11.5)

    rows = ["Parent", "Candidate", "Z = cand. - parent"]
    for j in range(m):
        cells = [(2, baseline[j], None), (1, pair[j], None)]
        for y, ok, _ in cells:
            right.add_patch(Rectangle((j, y), 1, 1, facecolor="#cfe5e3" if ok else "white", edgecolor=PALETTE["ink"],
                                      hatch=None if ok else "///", linewidth=1))
            right.text(j + 0.5, y + 0.5, "pass" if ok else "fail", ha="center", va="center", fontsize=10.5,
                       color=PALETTE["ink"], bbox=BOX)
        zc = PALETTE["teal"] if z[j] > 0 else (PALETTE["terracotta"] if z[j] < 0 else PALETTE["grey"])
        right.add_patch(Rectangle((j, 0), 1, 1, facecolor="white", edgecolor=PALETTE["ink"], linewidth=1))
        right.text(j + 0.5, 0.5, f"{z[j]:+d}" if z[j] else "0", ha="center", va="center", fontsize=12, color=zc, fontweight="bold")
    right.set_xlim(0, m)
    right.set_ylim(0, 3)
    right.set_xticks([j + 0.5 for j in range(m)], [str(j + 1) for j in range(m)])
    right.set_yticks([2.5, 1.5, 0.5], rows)
    right.grid(False)
    if reused:
        release = "rejected (guard reused)"
    elif shaped:
        release = "rejected (guard picked the winner)"
    elif accepted:
        release = "accepted by this gate"
    else:
        release = "rejected (gain below threshold)"
    right.set_xlabel(f"Guard case. Mean Z = {fmt(gain, 2)}; threshold {fmt(threshold, 2)}\nRelease: {release}")
    right.set_ylabel("Outcome on the guard case")
    sub = "\n(guard was reused)" if reused else ("\n(guard chose this pick)" if shaped else "")
    right.set_title(f"Step 2: guard cases for {pick}" + sub, fontsize=11.5)

    if reused:
        verdict = (f"The guard was reused, so release is rejected whatever the gain: once guard outcomes have shaped a "
                   f"decision, the guard is development evidence and no longer a test of {pick}.")
    elif shaped:
        verdict = (f"{pick} has the best guard gain, {fmt(gain, 2)}, but the guard chose it, so that number is the best of "
                   f"{len(names)} results and not an untouched test. Release is rejected; the development winner {dev_pick} "
                   f"has gain {fmt(gains[dev_pick], 2)}.")
    elif accepted:
        verdict = f"{fmt(gain, 2)} is at least {fmt(threshold, 2)}, so {pick} clears this finite gate."
    else:
        verdict = f"{fmt(gain, 2)} is below {fmt(threshold, 2)}, so {pick} fails this finite gate."
    if chooser == "guard" and not shaped and len(names) > 1:
        verdict += " The guard does not separate the candidates, so the development pick stands."
    if len(names) == 1:
        verdict += " There is one candidate, so there is nothing to choose between."
    dev_text = ", ".join(f"{n} {dev_wins[n]}/{dev_cases[n]} = {fmt(rates[n], 2)}" for n in names)
    sum_text = " + ".join(signed(d, 0) for d in z)
    interpretation = (
        f"Development rates: {dev_text}; the highest is {dev_pick}"
        + ("" if not shaped else f", but this state lets the guard choose, so {pick} is tested instead")
        + f". Its paired guard differences (candidate minus parent) are {sum_text}, so guard gain = ({sum_text}) / {m} = "
        f"{fmt(gain, 2)}. {verdict}"
    )
    steps = [
        f"Development rates: {dev_text}.",
        f"Development picks {dev_pick} and it is frozen." if not shaped else
        f"Development picks {dev_pick}, but here the guard's best score picks {pick} instead.",
        f"Paired guard differences Z (candidate minus parent), case by case: {sum_text}.",
        f"Guard gain = ({sum_text}) / {m} = {fmt(gain, 2)}.",
        f"Threshold {fmt(threshold, 2)} is fixed before guard access; {fmt(gain, 2)} is "
        f"{'at least' if gain >= threshold - 1e-12 else 'below'} it.",
        f"Guard status: {'reused' if reused else ('shaped the pick' if shaped else 'clean, used once')}. Release: {release}.",
    ]
    metrics = {
        "Development rates": ", ".join(f"{n} {fmt(rates[n], 2)}" for n in names),
        "Selected on development": dev_pick,
        "Candidate tested on the guard": pick,
        "Guard cases m": str(m),
        "Guard gain of the tested candidate": fmt(gain, 2),
        "Threshold": fmt(threshold, 2),
        "Guard status": "reused" if reused else ("shaped the pick" if shaped else "clean (used once)"),
        "Release decision": release,
    }
    alt = (f"Left, development success rates for {', '.join(names)} with {dev_pick} picked. Right, a grid of {m} paired guard "
           f"cases for {pick}: parent outcome, candidate outcome and their difference, averaging {fmt(gain, 2)} against a "
           f"threshold of {fmt(threshold, 2)}; release is {release}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: the false-accept bound and the cost of consulting a guard repeatedly

TAU = 0.25
SHOWN_AFTER = 2   # in the redesign states, guard result 2 reaches the designer, who revises candidate 3


def hoeffding(m, tau=TAU):
    return math.exp(-m * tau * tau / 2)


@lru_cache(maxsize=None)
def exact_tail(m, tau=TAU):
    """P(mean of m fair plus-or-minus 1 outcomes >= tau): one distribution with true uplift 0."""
    need = math.ceil(Fraction(m) * (1 + Fraction(str(tau))) / 2)  # least number of +1 outcomes
    total = sum(math.comb(m, k) for k in range(need, m + 1))
    return float(Fraction(total, 2 ** m))


def bound_picture(guard_cases=200, decisions=10, redesign="never"):
    m, q = int(guard_cases), int(decisions)
    covered = q if redesign == "never" else min(SHOWN_AFTER, q)
    fresh = q - covered
    single = hoeffding(m)
    union = covered * single
    exact = exact_tail(m)
    grid = np.arange(10, 401, 10)
    bound_curve = np.exp(-grid * TAU * TAU / 2)
    exact_curve = np.array([exact_tail(int(g)) for g in grid])

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.plot(grid, bound_curve, color=PALETTE["navy"], linewidth=2)
    left.plot(grid, exact_curve, color=PALETTE["teal"], linewidth=2, linestyle=(0, (5, 2)))
    left.axhline(1.0, color=PALETTE["grey"], linewidth=1.2, linestyle=":")
    left.plot([m], [single], "o", color=PALETTE["navy"], markersize=9)
    left.plot([m], [exact], "s", color=PALETTE["teal"], markersize=8)
    keys = []
    if covered > 1:
        left.plot(grid, covered * bound_curve, color=PALETTE["terracotta"], linewidth=2, linestyle="dashdot")
        left.plot([m], [union], "^", color=PALETTE["terracotta"], markersize=9)
        keys.append((f"dash-dot: {covered} covered decisions", PALETTE["terracotta"]))
    keys.append(("solid: bound, one decision", PALETTE["navy"]))
    keys.append(("dashed: exact tail, fair plus or minus 1", PALETTE["teal"]))
    for i, (text, color) in enumerate(keys):
        left.text(0.98, 0.97 - 0.075 * i, text, transform=left.transAxes, ha="right", va="top", fontsize=10.5, color=color)
    left.text(0.98, 0.97 - 0.075 * len(keys), "dotted line: probability 1", transform=left.transAxes, ha="right",
              va="top", fontsize=10.5, color=PALETTE["grey"])
    left.set_yscale("log")
    left.set_xlim(0, 405)
    left.set_ylim(1e-8, 1e3)
    left.set_xlabel("Number of guard cases m")
    left.set_ylabel("Chance a no-benefit candidate clears 0.25")
    left.set_title(f"Threshold 0.25; marked at m = {m}", fontsize=11.5)

    for j in range(1, q + 1):
        ok = j <= covered
        right.add_patch(Rectangle((j - 0.45, 0), 0.9, 1, facecolor="#cfe5e3" if ok else "white",
                                  edgecolor=PALETTE["teal"] if ok else PALETTE["terracotta"],
                                  hatch=None if ok else "///", linewidth=1.3))
        right.text(j, 0.5, str(j), ha="center", va="center", fontsize=11, color=PALETTE["ink"], bbox=BOX)
    right.text(0.55, 1.25, "fixed before guard access: bound applies" if fresh == 0 else "fixed first: bound applies",
               ha="left", va="center", fontsize=10.5, color=PALETTE["teal"])
    if fresh:
        right.text(q + 0.5, 1.85, "designed after a guard\nresult: new guard needed", ha="right", va="center",
                   fontsize=10.5, color=PALETTE["terracotta"])
    right.set_xlim(0.4, q + 0.6)
    right.set_ylim(-0.1, 2.3)
    right.set_xticks([])
    right.set_yticks([])
    right.grid(False)
    right.set_xlabel("Candidate decisions in the order they meet the guard")
    right.set_ylabel("One guard decision per box")
    right.set_title("Which decisions the accounting covers", fontsize=11.5)

    if union > 1:
        union_metric = f"{sig(union)} (above 1, says nothing)"
        union_note = (f" The total {sig(union)} over the {covered} covered decisions is above 1, so as a probability bound it "
                      f"says nothing at this size; more guard cases or fewer decisions are needed.")
    else:
        union_metric = sig(union)
        union_note = (f" Over the {covered} decision{'s' if covered != 1 else ''} fixed before any guard access the total is at most "
                      f"{covered} x {sig(single)} = {sig(union)}.")
    if fresh:
        redesign_note = (f" Here guard result {SHOWN_AFTER} was shown to the designer, who revised candidate {SHOWN_AFTER + 1}: "
                         f"{'decision ' + str(SHOWN_AFTER + 1) if fresh == 1 else 'decisions ' + str(SHOWN_AFTER + 1) + ' to ' + str(q)} "
                         f"({'not covered' if fresh == 1 else str(fresh) + ' of them, not covered'}): this state treats "
                         f"{'it' if fresh == 1 else 'them'} as redesigned after a guard result, a stipulation of the state, so the guard has become development evidence. The smaller total counts fewer decisions; "
                         "it is not a safer guard.")
    else:
        redesign_note = " Every decision was fixed before it met the guard, which is the condition the bound needs."
    metrics = {
        "Guard cases m": str(m),
        "Bound, one decision": sig(single),
        "Decisions fixed before guard access": f"{covered} of {q}",
        "Total bound over those decisions": union_metric,
        "Decisions needing a fresh guard": str(fresh),
        "Exact tail, fair plus or minus 1 case": sig(exact),
        "Bound divided by exact tail": fmt(single / exact, 1),
    }
    interpretation = (
        f"Exponent = m x tau^2 / 2 = {m} x {fmt(TAU * TAU, 4)} / 2 = {fmt(m * TAU * TAU / 2, 3)}, so the bound is "
        f"exp(-{fmt(m * TAU * TAU / 2, 3)}) = {sig(single)}.{union_note}{redesign_note} One concrete no-benefit guard (each paired "
        f"outcome plus 1 or minus 1 with equal chance) clears 0.25 with exact probability {sig(exact)}, below the bound, as it must be. "
        "Every number holds only if the candidate was fixed before guard access, outcomes lie in [-1, 1] and are independent."
    )
    steps = [
        f"Exponent = m x tau^2 / 2 = {m} x {fmt(TAU * TAU, 4)} / 2 = {fmt(m * TAU * TAU / 2, 3)}.",
        f"Bound for one fixed candidate: exp(-{fmt(m * TAU * TAU / 2, 3)}) = {sig(single)}.",
        f"Decisions fixed before any guard access: {covered} of {q}.",
        f"Total over those decisions: {covered} x {sig(single)} = {sig(union)}" + (" (above 1, says nothing)." if union > 1 else "."),
        (f"Decisions {SHOWN_AFTER + 1} to {q} followed a shown guard result, so they need a new frozen guard." if fresh
         else "No guard result reached a designer, so no decision needs a new guard."),
        f"Exact tail for one fair plus or minus 1 guard: {sig(exact)}, below the bound {sig(single)}.",
    ]
    alt = (f"Left, a log-scale plot of the bound and one exact tail against guard cases, marked at m = {m} with bound "
           f"{sig(single)}. Right, {q} boxes for guard decisions: the first {covered} are covered by the bound"
           + (f" and the remaining {fresh} need a fresh guard." if fresh else "."))
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: four conditions, all required

CONSTRAINT = 1.0   # c, the current cost limit (constructed units)
OTHER = {
    "all": dict(cost=0.80, authorized=1, rollback=1),
    "cost": dict(cost=0.95, authorized=1, rollback=1),
    "authority": dict(cost=0.80, authorized=0, rollback=1),
    "rollback": dict(cost=0.80, authorized=1, rollback=0),
}


def accept_picture(uplift=0.45, others="all"):
    uplift = float(uplift)
    cfg = OTHER[others]
    cost = cfg["cost"]
    limit = CONSTRAINT - MARGIN
    c1 = int(uplift >= TAU - 1e-12)
    c2 = int(cost <= limit + 1e-12)
    c3, c4 = cfg["authorized"], cfg["rollback"]
    accept = c1 * c2 * c3 * c4
    flags = [c1, c2, c3, c4, accept]

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    for x, v, ok in ((0, uplift, c1), (1, cost, c2)):
        left.bar(x, v, width=0.5, color=PALETTE["teal"] if ok else PINK,
                 edgecolor=PALETTE["teal"] if ok else PALETTE["terracotta"], hatch=None if ok else "///", linewidth=1.3)
        left.text(x, v + 0.03, fmt(v, 2), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"], bbox=BOX)
    left.plot([-0.4, 0.4], [TAU, TAU], color=PALETTE["ink"], linewidth=2, linestyle="dashed")
    left.plot([0.6, 1.4], [limit, limit], color=PALETTE["ink"], linewidth=2, linestyle="dashed")
    left.plot([0.6, 1.4], [CONSTRAINT, CONSTRAINT], color=PALETTE["grey"], linewidth=2, linestyle=":")
    left.set_xticks([0, 1], ["Guard uplift\n(dashed: needs\nat least 0.25)",
                            f"Guard cost\n(dashed: limit {fmt(limit, 2)};\ndotted: c = 1.00)"])
    left.set_xlim(-0.6, 1.6)
    left.set_ylim(0, 1.3)
    left.set_xlabel("Quantity measured on the guard")
    left.set_ylabel("Value (constructed units)")
    left.set_title("Measured against its requirement", fontsize=11.5)

    rows = ["1. uplift at least tau", "2. cost at most c - margin", "3. authorized in scope", "4. rollback path tested",
            "accept = 1 x 2 x 3 x 4"]
    ypos = np.arange(len(rows))[::-1]
    for y, ok, i in zip(ypos, flags, range(5)):
        last = i == 4
        word = ("ACCEPT" if ok else "REJECT") if last else ("pass" if ok else "FAIL")
        right.barh(y, 1, height=0.7, color=PALETTE["teal"] if ok else PINK,
                   edgecolor=PALETTE["teal"] if ok else PALETTE["terracotta"], hatch=None if ok else "///", linewidth=1.3)
        right.text(0.5, y, f"{word} ({ok})", ha="center", va="center", fontsize=11, color=PALETTE["ink"], bbox=BOX)
    right.set_yticks(ypos, rows)
    right.set_xticks([])
    right.set_xlim(0, 1)
    right.set_ylim(-0.6, 4.6)
    right.grid(alpha=0)
    right.axhline(0.5, color=PALETTE["ink"], linewidth=1)
    right.set_xlabel("Each condition is 1 (pass) or 0 (fail)")
    right.set_ylabel("Condition in Equation (25.4)")
    right.set_title("All four must pass", fontsize=11.5)

    def word(ok):
        return "pass" if ok else "fail"
    metrics = {
        "1. Uplift condition": f"{word(c1)} ({fmt(uplift, 2)} vs 0.25)",
        "2. Cost condition": f"{word(c2)} ({fmt(cost, 2)} vs {fmt(limit, 2)})",
        "3. Authorized in scope": word(c3),
        "4. Rollback path tested": word(c4),
        "Accept": "yes (1)" if accept else "no (0)",
    }
    reasons = []
    if not c1:
        reasons.append(f"uplift {fmt(uplift, 2)} is below 0.25")
    if not c2:
        reasons.append(f"cost {fmt(cost, 2)} is above {fmt(limit, 2)}" + (" although it is still under c = 1.00" if cost <= CONSTRAINT else ""))
    if not c3:
        reasons.append("the version is not authorized for this canary scope")
    if not c4:
        reasons.append("the return path to the parent version is untested")
    if accept:
        tail = ("All four conditions hold, so the version may enter the limited canary of Demonstration 1. Acceptance "
                "permits that monitored release; it does not show the change is safe at scale.")
    else:
        tail = "Rejected because " + "; ".join(reasons) + ". No strong condition can pay for a failed one."
        if not c3 and c1 and c2:
            tail += " Uplift and cost both pass here, and authority still blocks release."
    interpretation = (
        f"Limit = c - margin = {fmt(CONSTRAINT, 2)} - {fmt(MARGIN, 2)} = {fmt(limit, 2)}. Conditions: uplift {fmt(uplift, 2)} "
        f">= 0.25 gives {c1}; cost {fmt(cost, 2)} <= {fmt(limit, 2)} gives {c2}; authorized gives {c3}; rollback gives {c4}. "
        f"accept = {c1} x {c2} x {c3} x {c4} = {accept}. {tail}"
    )
    steps = [
        f"Cost limit with margin: c - margin = {fmt(CONSTRAINT, 2)} - {fmt(MARGIN, 2)} = {fmt(limit, 2)}.",
        f"Uplift: {fmt(uplift, 2)} is {'at least' if c1 else 'below'} tau = 0.25, so condition 1 = {c1}.",
        f"Cost: {fmt(cost, 2)} is {'at most' if c2 else 'above'} {fmt(limit, 2)}, so condition 2 = {c2}.",
        f"Authority for this scope = {c3}; tested rollback path = {c4}.",
        f"accept = {c1} x {c2} x {c3} x {c4} = {accept}; the conditions multiply, so one zero decides.",
    ]
    alt = (f"Left, bars for guard uplift {fmt(uplift, 2)} against a dashed line at 0.25 and guard cost {fmt(cost, 2)} against a "
           f"dashed limit at {fmt(limit, 2)}. Right, four pass or fail rows and an overall "
           f"{'ACCEPT' if accept else 'REJECT'} row.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 25,
    "title": "Improving an Agent Without Trusting the Improvement",
    "subtitle": "An agent can propose a useful change without supplying independent evidence that the change should be released.",
    "summary": (
        "These four demonstrations follow one proposed change to an agent's procedure: a canary with its rollback rule fixed "
        "first and the weights frozen throughout, why the development winner cannot certify itself, how much a frozen guard "
        "can tell you and how quickly repeated use erodes it, and why release needs four separate conditions. All values are "
        "constructed teaching examples, not measurements of any real system."
    ),
    "ask_skill": {
        "prompt": (
            "Here are the development success rates and the paired guard outcomes (candidate and parent, case by case) for "
            "my two candidate procedures, plus the guard threshold I fixed in advance and whether anyone has seen guard "
            "results before. Which candidate is frozen, what is its guard gain, is the guard still clean, and is release "
            "accepted by the gate? Then list what my canary record must name before it starts."
        ),
    },
    "demos": [
        {
            "id": "C25-D01",
            "title": "A canary is monitored evidence, and its rules come first",
            "question": "If an accepted version enters a limited release, when does it roll back, and what changes if the rule is chosen after the numbers are seen?",
            "equations": [EQ_FAMILY],
            "symbols": (
                "theta is the set of model parameters, frozen, so theta at step t + 1 equals theta at step t. phi_t is the parent "
                "version of the procedure: the prompt template, tool-routing rule, memory policy, verifier and retry cap assembled "
                "around the model. phi' is the accepted new version, so rollback restores a procedure version, not weights. "
                "The cost per period is a constructed resource measure. c is the cost limit (1.00) and the margin is 0.10, so "
                "the declared boundary is c minus the margin. An alert is the first period with cost strictly above the boundary."
            ),
            "prediction": "Take the creeping-cost trace under the rule declared first. In which period does the alert fire? Then switch to the rule chosen after looking.",
            "prediction_options": ["Period 3", "Period 5", "Period 8", "No alert"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Costs 0.80, 0.83, 0.86, 0.89 stay at or below 0.90 and 0.92 in period 5 is the first above it.",
                "incorrect": "The boundary is 1.00 - 0.10 = 0.90 and the first cost above it is 0.92 in period 5. Set the rule control to 'chosen after looking' to see it move to period 8.",
            },
            "explanation": (
                "A canary is a limited release to a declared population, action set, duration and resource budget. Its rollback "
                "trigger is set before it starts, here a cost boundary of c minus a margin, together with a named fallback. When "
                "the trigger fires the declared fallback applies and the weights were never involved, because Equation (25.1) holds "
                "theta fixed. If the boundary is moved after the costs are seen, the same trace can fire late or never."
            ),
            "application": (
                "Before a canary starts, write the monitoring cadence, population, metric, alert threshold, maximum duration, "
                "decision after an alert, and the fallback route. A canary is monitored evidence after acceptance, not a cheap "
                "second chance to pass the guard."
            ),
            "assumptions": (
                "One constructed cost metric, eight periods, one trigger type. The chapter also names a safety violation, a "
                "verifier failure, a decline in a monitored outcome and a missing authority condition as triggers; each needs its own "
                "pre-declared rule. A pre-declared boundary protects against moving the rule after the outcomes, but it does not by "
                "itself stop leakage through redesign, metric changes or holdout peeking, and a valid sequential procedure is a "
                "separate matter."
            ),
            "check": (
                "A canary declares its boundary as c - margin with c = 1.20 and margin 0.15. Costs by period are 1.00, 1.05, 1.08 "
                "and 1.12. In which period does the alert fire, and what happens if the boundary had been moved to c after looking?"
            ),
            "answer": (
                "The boundary is 1.20 - 0.15 = 1.05. A cost of 1.05 is not above 1.05, so the first cost above it is 1.08 in "
                "period 3. With the boundary moved to 1.20 none of the four costs is above it, so no alert fires."
            ),
            "provenance": "Constructed example: canary cost traces, an eight-period duration and a cost limit with margin defined for this reader around the chapter's rollback and monitoring rules.",
            "source_section": "Acceptance is a constrained release decision",
            "source_anchor": "acceptance-is-a-constrained-release-decision",
            "misconception": {
                "title": "Self-improvement means the model rewrites its weights",
                "text": (
                    "The chapter notes that the Reflexion paper calls its method verbal reinforcement learning but does not report a model "
                    "silently rewriting its weights after every failure. A reflection is text added to memory. The versioned object is "
                    "the procedure, so theta at step t + 1 equals theta at step t and rollback restores the parent procedure phi_t."
                ),
            },
            "scope_note": {
                "text": (
                    "Training-time model updates are a separate question. This chapter held theta fixed; changing it involves its own "
                    "training and evaluation controls, not covered here."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "trace", "label": "Cost trace during the canary", "values": ["steady", "creeping", "spike"], "default": "creeping",
                 "value_labels": ["Steady cost", "Cost creeping up", "One cost spike"]},
                {"key": "rule", "label": "When the boundary was set", "values": ["declared", "after"], "default": "declared",
                 "value_labels": ["Declared before the canary (0.90)", "Chosen after looking (1.00)"]},
                {"key": "fallback", "label": "Fallback named in advance", "values": ["restore", "hold"], "default": "restore",
                 "value_labels": ["Restore the parent version", "Hold new tasks, call the authority holder"]},
            ],
            "function": "canary_picture",
        },
        {
            "id": "C25-D02",
            "title": "Development chooses, the guard checks one frozen pick",
            "question": "Once development has picked a winner, what does a separate guard set decide, and what breaks if the guard picks or is reused?",
            "equations": [EQ_SELECT],
            "symbols": (
                "D is the development set and G the guard set. V-hat_D(phi) is a procedure's estimated success on D, and "
                "Delta-hat_D(phi_j) is candidate j's development uplift over the parent phi_t. The arg max picks the winner "
                "phi'. For guard case i, Z_i is the candidate's result minus the parent's, between -1 and 1 (here +1, 0 or -1), and "
                "Delta-hat_G is the average of Z_i over the m guard cases. The threshold is the smallest guard gain accepted. The "
                "candidates are named flashy and steady (and proposal in the transfer case); the names are labels only."
            ),
            "prediction": "In the laboratory's default case with a clean guard, threshold 0.20 and the development winner tested, which candidate is frozen and what happens?",
            "prediction_options": [
                "Flashy is frozen and fails the guard (gain 0.00)",
                "Flashy is frozen and passes the guard",
                "Steady is frozen and passes the guard (gain 0.25)",
            ],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "Flashy has the best development rate (4/4) but its guard outcomes equal the parent's, so every Z is 0 and the gain is 0.00.",
                "incorrect": "Development picks flashy (4/4 against 3/4), and its four guard cases match the parent, so every Z is 0 and the gain is 0.00, below 0.20. Steady's 0.25 does not count: choosing it after seeing the guard would put the guard inside selection.",
            },
            "explanation": (
                "Development picks the candidate with the best development score. Only that frozen candidate is then compared with the "
                "parent on guard cases, case by case, and the average of the differences Z is its guard gain. The other candidate may "
                "look better on the guard, but letting the guard choose would make the guard part of selection, so its best-of-several "
                "score stops being a test. If the guard was already reused, the gate rejects regardless of the gain."
            ),
            "application": (
                "Write down which candidate is frozen, and the threshold, before anyone opens guard outcomes. Report guard numbers for "
                "the frozen candidate only, and treat any guard that has informed a redesign as development data."
            ),
            "assumptions": (
                "Two or four paired cases with binary outcomes, as in the laboratory's teaching cases, so the gain can only be a "
                "multiple of 0.25 or 0.5 and the gate is a teaching device. A threshold is a rule, not a confidence statement. The "
                "reuse flag records what you declare, not the true history, and the threshold is only meaningful if fixed before guard "
                "access. A tie in guard gain leaves the development pick in place."
            ),
            "check": "A frozen candidate beats its parent on 2 of 8 guard cases, loses on 1 and ties on 5. Its threshold is 0.20. Does it pass a clean guard?",
            "answer": "Gain = (2 x 1 + 1 x (-1) + 5 x 0) / 8 = 1/8 = 0.125, which is below 0.20, so it does not pass.",
            "provenance": "Constructed example: the laboratory's default, changed and transfer teaching cases, computed with its own gate function.",
            "source_section": "Development can choose a candidate; it cannot certify one",
            "source_anchor": "development-can-choose-a-candidate-it-cannot-certify-one",
            "misconception": {
                "title": "The top of the development table certifies the winner",
                "text": (
                    "The chapter says the problem is selection, not bad faith: if several changes have no true benefit, random variation can "
                    "still place one at the top of the table. The winning development result records both the candidate and the selection "
                    "process that chose it, so it cannot also serve as untouched evidence for that candidate."
                ),
            },
            "scope_note": {
                "text": (
                    "The chapter does not promise a clean separation between procedure and environment. A new tool, memory store, "
                    "evaluator or task distribution can change the assembled system in ways that demand fresh evaluation."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "case", "label": "Teaching case", "values": ["default", "changed", "transfer"], "default": "default",
                 "value_labels": ["Default (winner matches the parent, threshold 0.20)", "Changed (winner repairs one case, threshold 0.20)",
                                  "Transfer (one proposal, 2 cases, threshold 0.10)"]},
                {"key": "guard", "label": "Guard history", "values": ["clean", "reused"], "default": "clean",
                 "value_labels": ["Clean (first use)", "Reused (outcomes shaped a decision)"]},
                {"key": "chooser", "label": "Who picks the candidate to test", "values": ["development", "guard"], "default": "development",
                 "value_labels": ["Development winner (the rule)", "Best guard score (breaks the rule)"]},
            ],
            "function": "gate_picture",
        },
        {
            "id": "C25-D03",
            "title": "How little a guard promises, and how it wears out",
            "question": "How likely is a candidate with no true benefit to clear a guard threshold, and which guard decisions does that number still cover after a guard result reaches the designer?",
            "equations": [EQ_BOUND],
            "symbols": (
                "m is the number of guard cases. Each paired difference Z_i lies between -1 and 1 and has true mean Delta, "
                "which is at most 0 for a candidate with no benefit. Delta-hat_G is the guard average. The threshold tau is 0.25, "
                "as in the chapter. exp(x) is e raised to the power x. The decision count q is how many separately fixed "
                "candidates use the guard, each added once. In the redesign states the second guard result is shown to the designer, "
                "who revises the third candidate."
            ),
            "prediction": "At 200 guard cases and 10 decisions the total is 0.0193. Switch to the state where guard result 2 reaches the designer. What happens to the total, and what happens to decisions 3 to 10?",
            "prediction_options": [
                "The total rises, because more decisions are added",
                "The total falls to 2 x 0.00193 but decisions 3 to 10 get no bound",
                "The total stays at 0.0193",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Only decisions 1 and 2 were fixed before guard access, so the total is 2 x 0.00193 = 0.00386, and the eight later decisions need a new frozen guard.",
                "incorrect": "Only decisions 1 and 2 still satisfy the fixed-before-guard condition, so the covered total is 2 x 0.00193 = 0.00386. That smaller number counts fewer decisions; decisions 3 to 10 have no bound until a new frozen guard exists.",
            },
            "explanation": (
                "The bound exp(-m x 0.25^2 / 2) shrinks quickly as guard cases are added. For several candidates, each fixed before it "
                "meets the guard, the chances add up, so ten decisions cost ten times the single bound. The exact tail for one concrete "
                "no-benefit guard lies below the bound, which is a worst-case guarantee, not a prediction. Once a guard result changes "
                "the next candidate, that candidate was not fixed before guard access and the adding-up no longer applies."
            ),
            "application": (
                "Set a guard query budget before use. Count how many candidates will be tested, size the guard so the total stays small, "
                "and retire the guard for release evidence once its results start steering redesign. Track who has seen which "
                "outcomes, not whether the bank file changed."
            ),
            "assumptions": (
                "The chapter's constructed conditions: every counted candidate is fixed before guard access, outcomes lie in [-1, 1], "
                "and outcomes are independent across cases. Shared tool state or a common evaluator can break independence. The exact "
                "tail uses one convenient distribution, plus or minus 1 with equal chance; it is not a real agent. The guard is evidence "
                "for one version, one task population and one evaluation protocol, and a shift in the task distribution changes what a "
                "clean result describes."
            ),
            "check": "With m = 300 guard cases and threshold 0.25, what is the bound for one decision?",
            "answer": "exp(-300 x 0.0625 / 2) = exp(-9.375) = 0.0000848, about 8.5 in 100,000.",
            "provenance": "Constructed example: the chapter's own 200-case, 0.25 threshold, ten-decision values and its three-query ledger, with other sizes and the redesign state defined for this reader.",
            "source_section": "A guard becomes development evidence when it is consulted repeatedly",
            "source_anchor": "a-guard-becomes-development-evidence-when-it-is-consulted-repeatedly",
            "misconception": {
                "title": "A frozen guard stays fresh while its file is unchanged",
                "text": (
                    "The chapter says the word frozen describes access, not a file format. A test bank on a server still becomes development "
                    "evidence if operators learn which changes passed it and redesign from that information."
                ),
            },
            "controls": [
                {"key": "guard_cases", "label": "Number of guard cases m", "values": [50, 200, 400], "default": 200},
                {"key": "decisions", "label": "Candidates tested on the guard", "values": [3, 10], "default": 10},
                {"key": "redesign", "label": "Did a guard result reach the designer?", "values": ["never", "after2"], "default": "never",
                 "value_labels": ["No, every candidate fixed first", "Yes: result 2 shown, candidate 3 revised"]},
            ],
            "function": "bound_picture",
        },
        {
            "id": "C25-D04",
            "title": "Acceptance needs four passes, not a high score",
            "question": "Can a large guard uplift make up for a cost that is over the limit, a missing permission or an untested rollback?",
            "equations": [EQ_ACCEPT],
            "symbols": (
                "phi' is the candidate version. Delta-hat_G is its guard uplift and tau the required uplift (0.25). C-hat_G is "
                "its guard cost estimate, c the current cost limit (1.00) and epsilon_safe the reserved margin (0.10). "
                "Authorized is 1 if the version is permitted in the proposed canary scope and 0 otherwise (a canary is a small monitored release). Rollback is 1 if "
                "a tested path back to the parent version exists and 0 otherwise."
            ),
            "prediction": "With uplift 0.45 and everything else passing, switch to cost 0.95. That is under the limit c = 1.00. Is the version accepted?",
            "prediction_options": ["Yes, 0.95 is under c = 1.00", "No, 0.95 is above c - margin = 0.90"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "The cost condition compares with c minus the margin, 1.00 - 0.10 = 0.90, and 0.95 is above it, so accept = 1 x 0 x 1 x 1 = 0.",
                "incorrect": "Cost is held to c minus the margin, 1.00 - 0.10 = 0.90, not to c. 0.95 is above 0.90, so the cost condition is 0 and accept = 1 x 0 x 1 x 1 = 0.",
            },
            "explanation": (
                "Equation (25.4) turns each condition into a pass or fail, then requires all four. Cost is held to c minus a "
                "margin, so a cost of 0.95 fails even though it is under c. The conditions multiply instead of adding, so a "
                "zero anywhere gives zero overall, however large the uplift. Authority and rollback are yes or no, not "
                "scores that can be traded against performance."
            ),
            "application": (
                "Write a release record with four lines: uplift against its threshold, cost against its limit minus margin, "
                "the named authority holder and scope, and the tested rollback route. Name the owner for each, for example the "
                "workflow owner for the guard result and the incident owner for rollback alerts. A missing line blocks release."
            ),
            "assumptions": (
                "Constructed values for one candidate, with uplift and cost already estimated on a clean guard (see "
                "Demonstration 3 for what that requires). The laboratory's gate in Demonstration 2 checks only the uplift "
                "threshold and the reuse flag, so cost, authority and rollback are computed directly here. A passing record "
                "permits a limited canary; it does not show that the change is safe at scale."
            ),
            "check": "A candidate has uplift 0.40, cost 0.92, authority granted and rollback tested, with c = 1.00 and margin 0.10. Is it accepted?",
            "answer": "The limit is 1.00 - 0.10 = 0.90 and 0.92 > 0.90, so the cost condition is 0 and accept = 1 x 0 x 1 x 1 = 0.",
            "provenance": "Constructed example: the chapter's threshold 0.25 with cost limit, margin and candidate values defined for this reader; the authority case follows the workbench's revised third candidate.",
            "source_section": "Acceptance is a constrained release decision",
            "source_anchor": "acceptance-is-a-constrained-release-decision",
            "misconception": {
                "title": "A high score can pay for a missing permission",
                "text": (
                    "The chapter says the four conditions are not four terms of a score to be traded against one another. A procedure that "
                    "improves a score but lacks permission to call a tool or lacks a recovery route is not accepted."
                ),
            },
            "scope_note": {
                "text": (
                    "An accepted procedure may later generate a new candidate. That does not convert the system into a source of "
                    "guaranteed recursive gains. A positive result for phi' does not prove that phi'' will improve, and it does not "
                    "license the system to expand its own change family or authority envelope."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "uplift", "label": "Guard uplift estimate", "values": [0.2, 0.25, 0.45], "default": 0.45},
                {"key": "others", "label": "Cost, authority and rollback", "values": ["all", "cost", "authority", "rollback"],
                 "default": "all",
                 "value_labels": ["All pass (cost 0.80)", "Cost 0.95, over the limit", "No authority for this scope", "Rollback untested"]},
            ],
            "function": "accept_picture",
        },
    ],
}

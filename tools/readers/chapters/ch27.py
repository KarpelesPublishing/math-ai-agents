"""Chapter 27 reader: The Mathematics of Delegation.

Four demonstrations built on Equations (27.1) to (27.4) and the chapter's M/M/1
mean time in system.

Demonstration 1 compares correctness (Equation 27.2) and then adds the deadline
with the workbench's timely-return problem. Demonstration 2 filters the four
routes of the pending transfer through the authorized set (Equation 27.1) before
choosing by value (Equation 27.3). Demonstration 3 calls the laboratory's own
review-queue function (math_ai_agents.chapters.ch27.evaluate) on the notebook's
default, changed and transfer cases and shows the route ledger it produces.
Demonstration 4 tests waiting against value of information and an authorized
fallback in every reachable deadline state (Equation 27.4). Every number is a
constructed teaching value; Demonstrations 2 to 4 reuse the numbers of the
book's pending transfer example and queue example.
"""
import math

import numpy as np
from matplotlib.patches import Rectangle

from math_ai_agents.chapters.ch27 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed, undefined

EQ_ROUTE = (
    r"\operatorname{route}^{\star}(x)="
    r"\begin{cases}"
    r"\operatorname{Del}(E,\Delta), & p_E(x)\geq \max_y p(y\mid x),\\"
    r"\arg\max_y p(y\mid x), & p_E(x)<\max_y p(y\mid x)."
    r"\end{cases}"
)
EQ_AUTH = (
    r"\mathcal A_{\mathrm{auth}}(x)"
    r"=\{a\in\mathcal A:\operatorname{Authorized}_{\mathcal G}(a,x)=1,"
    r"\;\operatorname{Pre}(a,x)=1\}."
)
EQ_CHOOSE = (
    r"\mathcal R_{\mathrm{auth}}(x)="
    r"\{(\mathrm{act},a),(\mathrm{delegate},d,\Delta),(\mathrm{wait},o,\Delta),(\mathrm{narrow},a'),(\mathrm{return})"
    r"\ \text{that are authorized at }x\},"
    r"\qquad"
    r"\operatorname{choose}^{\star}(x)\in"
    r"\arg\max_{\varrho\in\mathcal R_{\mathrm{auth}}(x)}V(\varrho,x)."
)
EQ_MM1 = r"1/(\mu-f\lambda)"
EQ_WAIT = (
    r"\operatorname{wait}^{\star}(o,\Delta,x)"
    r"\quad\text{only if}\quad"
    r"\operatorname{VOI}(o)>"
    r"\operatorname{DelayCost}(\Delta,x)"
    r"\quad\text{and}\quad"
    r"\operatorname{fallback}(\Delta,x_\Delta)\in\mathcal A_{\mathrm{auth}}(x_\Delta)"
    r"\ \text{for every reachable }x_\Delta."
)

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
PINK = "#f1d9c9"
GREEN = "#cfe5e3"


# Demonstration 1: route by comparing correctness (27.2), then add the deadline

UTIL_RIGHT, UTIL_WRONG, FEE, FALLBACK_UTIL = 10.0, -10.0, 1.0, 2.0   # the workbench's problem VI.3
CASES = {
    "chapter": {"model": 0.78, "expert": 0.95, "name": "chapter case: model 0.78, expert 0.95"},
    "general": {"model": 0.78, "expert": 0.60, "name": "chapter case: model 0.78, expert 0.60"},
    "bench": {"model": 0.80, "expert": 0.95, "name": "workbench case: act 0.80, expert 0.95"},
    "tie": {"model": 0.78, "expert": 0.78, "name": "tie: both 0.78"},
}
TIMELY = {1.0: "1.00", 0.6: "0.60", 5 / 7: "5/7"}


def t_text(t):
    """Probability as the hand calculation writes it: exact fractions for 5/7 and 2/7."""
    return {"1.00": "1.00", "0.60": "0.60", "5/7": "(5/7)"}[TIMELY[min(TIMELY, key=lambda v: abs(v - t))]]


def comp_text(t):
    c = 1 - t
    if abs(t - 5 / 7) < 1e-9:
        return "(2/7)"
    return fmt(c, 2)


def routing_picture(case="chapter", timely=1.0):
    cs = CASES[case]
    model, expert, t = cs["model"], cs["expert"], float(timely)
    delegate = expert >= model - 1e-12                       # Equation (27.2): defer when p_E(x) >= max_y p(y | x)
    tie = math.isclose(expert, model, abs_tol=1e-9)
    gap = expert - model
    act = model * UTIL_RIGHT + (1 - model) * UTIL_WRONG
    gross = expert * UTIL_RIGHT + (1 - expert) * UTIL_WRONG
    value_del = t * gross + (1 - t) * FALLBACK_UTIL - FEE
    if gross - FALLBACK_UTIL > 1e-12:
        t_star = (act - FEE) / (gross - FALLBACK_UTIL)
    else:
        t_star = None
    breaks = t_star is not None and t_star <= 1 + 1e-12
    value_route = "act" if act > value_del + 1e-9 else ("delegate" if value_del > act + 1e-9 else "tie")

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    y = [1, 0]
    values = [expert, model]
    win = [delegate, not delegate]
    for yi, v, w in zip(y, values, win):
        left.barh(yi, v, height=0.5, color=PALETTE["teal"] if w else "#8fa3b8", hatch="" if w else "///",
                  edgecolor="white" if w else PALETTE["grey"], linewidth=1)
        label_point(left, v, yi, fmt(v, 2), color=PALETTE["ink"], dx=-6, dy=0, ha="right", va="center").set_bbox(BOX)
    left.axvline(model, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    left.set_yticks(y, ["Expert E\ncorrect" + ("\n(27.2 picks)" if delegate else ""),
                        "Classifier's\nbest class" + ("\n(27.2 picks)" if not delegate else "")])
    left.set_xlim(0, 1.0)
    left.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    left.set_ylim(-0.6, 1.6)
    left.set_xlabel("Probability of a correct result")
    left.set_ylabel("Who answers")
    left.grid(axis="y", alpha=0)
    left.set_title("Equation (27.2): compare correctness", fontsize=11.5)

    for i, (v, col, hat) in enumerate(((act, PALETTE["navy"], ""), (value_del, PALETTE["teal"], "///"))):
        right.bar(i, v, color=col, hatch=hat, edgecolor="white", width=0.6)
        right.text(i, max(v, 0) + 0.2, fmt(v, 2), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    right.axhline(0, color=PALETTE["ink"], linewidth=1)
    right.set_xticks([0, 1], ["Act now", f"Delegate\n(on time {fmt(t, 2)})"])
    right.set_xlim(-0.6, 1.6)
    right.set_ylim(0, 10)
    right.set_xlabel("Route (fee 1, fallback worth 2)")
    right.set_ylabel("Net expected utility")
    right.set_title("Value with the deadline: " + {"act": "act wins", "delegate": "delegate wins", "tie": "tie"}[value_route], fontsize=11.5)

    eq_route = "Delegate to E" + (" (tie)" if tie else "") if delegate else "Predict the most probable class"
    star_text = (fmt(t_star, 3) if breaks else "none (delegation never matches acting)")
    metrics = {
        "Classifier best class probability": fmt(model, 2),
        "Expert correctness p_E": fmt(expert, 2),
        "Route by Equation (27.2), delay ignored": eq_route,
        "Value of acting now": fmt(act, 2),
        "Value of delegating": fmt(value_del, 2),
        "Route with the higher value": {"act": "act now", "delegate": "delegate", "tie": "tie"}[value_route],
        "Timely-return probability that ties them": star_text,
    }
    tt, cc = t_text(t), comp_text(t)
    calc_act = (f"Act = {fmt(model, 2)} x {fmt(UTIL_RIGHT, 0)} + {fmt(1 - model, 2)} x ({fmt(UTIL_WRONG, 0)}) = {fmt(act, 2)}.")
    calc_del = (f"Delegate = t x gross + (1 - t) x 2 - 1 = {tt} x {fmt(gross, 2)} + {cc} x 2 - 1 = {fmt(value_del, 2)}, where gross = "
                f"{fmt(expert, 2)} x {fmt(UTIL_RIGHT, 0)} + {fmt(1 - expert, 2)} x ({fmt(UTIL_WRONG, 0)}) = {fmt(gross, 2)}.")
    if tie:
        part = (f"Equation (27.2) sends a tie to the expert ({fmt(expert, 2)} >= {fmt(model, 2)}); any tie rule is a design choice.")
    elif delegate:
        part = (f"Equation (27.2): {fmt(expert, 2)} >= {fmt(model, 2)}, so it delegates (gap {fmt(expert, 2)} - {fmt(model, 2)} = {fmt(gap, 2)}).")
    else:
        part = (f"Equation (27.2): {fmt(expert, 2)} < {fmt(model, 2)}, so it keeps the prediction; confidence {fmt(model, 2)} alone is not a reason to delegate.")
    if value_route == "act" and delegate:
        flip = (f" With the deadline priced in, acting wins {fmt(act, 2)} against {fmt(value_del, 2)}: the expert's conditional accuracy "
                "alone cannot answer the question, because a correct answer that misses the deadline does not implement the same action.")
    elif value_route == "delegate" and not delegate:
        flip = " Delegation wins on value here even though Equation (27.2) would keep the prediction."
    elif value_route == "tie":
        flip = " The routes tie, so the timely-return probability sits exactly at the break-even."
    else:
        flip = f" The two readings agree: {'delegate' if value_route == 'delegate' else 'act'}."
    be = (f" Break-even: t = (act - 1) / (gross - 2) = ({fmt(act, 2)} - 1) / ({fmt(gross, 2)} - 2) = {fmt(t_star, 3)}." if breaks else
          (" Delegation's gross value does not exceed the fallback's 2, so no timely-return probability lets delegation match acting."
           if t_star is None else
           f" The break-even would be above 1 ({fmt(t_star, 3)}), so even guaranteed return does not let delegation match acting."))
    interpretation = f"{part} {calc_act} {calc_del}{flip}{be}"
    steps = [part, calc_act, f"Timely review gross = {fmt(expert, 2)} x {fmt(UTIL_RIGHT, 0)} + {fmt(1 - expert, 2)} x ({fmt(UTIL_WRONG, 0)}) = {fmt(gross, 2)}.",
             f"Delegate = {tt} x {fmt(gross, 2)} + {cc} x 2 - 1 = {fmt(value_del, 2)}; the fee is paid on both branches.",
             f"Higher value: {metrics['Route with the higher value']} ({fmt(act, 2)} against {fmt(value_del, 2)})."]
    alt = (f"Left, two bars: expert correctness {fmt(expert, 2)} and classifier best class {fmt(model, 2)}, with the route chosen by "
           f"Equation (27.2) marked. Right, net expected utility of acting now, {fmt(act, 2)}, against delegating with an on-time "
           f"probability of {fmt(t, 2)}, {fmt(value_del, 2)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: the authorized set (27.1), then the best route in it (27.3)

P_FRAUD = 0.10
RELEASE_NOW = 0.90 * 10 + P_FRAUD * (-100)                     # -1
TIMELY_GROSS = 0.90 * (0.98 * 10 + 0.02 * (-10)) + P_FRAUD * (0.94 * 0 + 0.06 * (-100))  # 8.04
HOLD_TIMEOUT = -4.0
REVIEW_FEE = 1.0
WAIT_NET = 0.50 * 9 + 0.50 * (-1) - 2                          # 2
ROUTE_KEYS = ["release", "review", "wait", "hold"]
ROUTE_LABELS = {
    "release": "Release now",
    "review": "Review;\nrelease on timeout",
    "wait": "Wait for confirmation;\nrelease on timeout",
    "hold": "Reversible hold and review;\nreturn on timeout",
}
# (Authorized, Pre) per route and status
STATUS_FLAGS = {
    "all": {},
    "holdno": {"hold": (0, 1)},
    "unavail": {"review": (1, 0), "hold": (1, 0)},
    "stopped": {"release": (0, 1)},
}
STATUS_TEXT = {
    "all": "All four routes authorized and the reviewer is available.",
    "holdno": "The hold is not authorized: Authorized = 0 for it.",
    "unavail": "The reviewer is unavailable: Pre = 0 for both routes that need a review.",
    "stopped": "An authorized stop was honored: Authorized = 0 for releasing now.",
}


STATUS_SHORT = {"all": "all routes authorized", "holdno": "hold not authorized", "unavail": "reviewer unavailable",
                "stopped": "authorized stop honored"}


def route_values(hold_cost):
    review = 0.35 * TIMELY_GROSS + 0.65 * RELEASE_NOW - REVIEW_FEE
    hold = 0.95 * TIMELY_GROSS + 0.05 * HOLD_TIMEOUT - float(hold_cost) - REVIEW_FEE
    return {"release": RELEASE_NOW, "review": review, "wait": WAIT_NET, "hold": hold}


def route_value_picture(hold_cost=2, status="all"):
    cost = float(hold_cost)
    vals = route_values(cost)
    flags = {k: STATUS_FLAGS[status].get(k, (1, 1)) for k in ROUTE_KEYS}
    inside = {k: bool(flags[k][0] and flags[k][1]) for k in ROUTE_KEYS}
    feasible = {k: v for k, v in vals.items() if inside[k]}
    best = max(feasible.values())
    winner = [k for k, v in feasible.items() if abs(v - best) < 1e-9]
    y = np.arange(len(ROUTE_KEYS))[::-1]
    fig, ax = new_figure(height=4.3)
    for yi, k in zip(y, ROUTE_KEYS):
        v = vals[k]
        a, p = flags[k]
        if not inside[k]:
            ax.barh(yi, v, height=0.56, color="white", edgecolor=PALETTE["terracotta"], hatch="xx", linewidth=1)
            ax.text(max(v, 0) + 0.15, yi, f"excluded: Authorized {a}, Pre {p}\n(would be {fmt(v, 3)})", va="center", fontsize=10.5,
                    color=PALETTE["terracotta"])
        else:
            ax.barh(yi, v, height=0.56, color=PALETTE["teal"] if k in winner else "#8fa3b8")
            ax.text(max(v, 0) + 0.15, yi, f"{fmt(v, 3)}" + ("  highest" if k in winner else "") + f"\nAuthorized {a}, Pre {p}", va="center",
                    fontsize=10.5, color=PALETTE["ink"])
    ax.axvline(0, color=PALETTE["ink"], linewidth=1)
    ax.set_yticks(y, [ROUTE_LABELS[k] for k in ROUTE_KEYS])
    ax.set_xlim(-2, 12.5)
    ax.set_xlabel("Net expected value (constructed utility units)")
    ax.set_ylabel("Route")
    ax.grid(axis="y", alpha=0)
    ax.set_title(f"Hold costs {fmt(cost, 0)}; {STATUS_SHORT[status]}", fontsize=11.5)

    hold_base = 0.95 * TIMELY_GROSS + 0.05 * HOLD_TIMEOUT - REVIEW_FEE
    break_even = hold_base - WAIT_NET
    names = {k: ROUTE_LABELS[k].replace("\n", " ") for k in ROUTE_KEYS}
    chosen = " and ".join(names[k] for k in winner)
    metrics = {names[k]: (fmt(vals[k], 3) if inside[k] else f"{fmt(vals[k], 3)} (excluded)") for k in ROUTE_KEYS}
    metrics["Routes in the authorized set"] = ", ".join(names[k].split(";")[0].lower() for k in ROUTE_KEYS if inside[k])
    metrics["Highest among the authorized routes"] = chosen
    metrics["Hold cost at which waiting (2) overtakes it"] = fmt(break_even, 3)
    calc = f"Hold = 0.95 x {fmt(TIMELY_GROSS, 2)} + 0.05 x ({fmt(HOLD_TIMEOUT, 0)}) - {fmt(cost, 0)} - 1 = {fmt(vals['hold'], 3)}."
    highest_overall = max(vals.values())
    excluded_top = [k for k in ROUTE_KEYS if not inside[k] and vals[k] >= highest_overall - 1e-9]
    if status == "all":
        if "hold" in winner:
            verdict = (f"The hold wins: {fmt(vals['hold'], 3)} is above waiting at {fmt(WAIT_NET, 0)}. Its value before its own cost is "
                       f"0.95 x {fmt(TIMELY_GROSS, 2)} + 0.05 x ({fmt(HOLD_TIMEOUT, 0)}) - 1 = {fmt(hold_base, 3)}, so its cost can rise to "
                       f"{fmt(hold_base, 3)} - {fmt(WAIT_NET, 0)} = {fmt(break_even, 3)} before waiting overtakes it.")
        else:
            verdict = (f"The hold's {fmt(vals['hold'], 3)} is now below waiting at {fmt(WAIT_NET, 0)}, because the cost {fmt(cost, 0)} "
                       f"is above the break-even {fmt(break_even, 3)}. Reversibility is not free.")
    else:
        top = (f" The excluded route would have had the highest value, {fmt(vals[excluded_top[0]], 3)}, and stays a recommendation, "
               "not an executable act." if excluded_top else "")
        verdict = (f"{STATUS_TEXT[status]} Equation (27.1) keeps only routes with Authorized = 1 and Pre = 1, so the set holds "
                   f"{metrics['Routes in the authorized set']}. Among them {chosen} has the highest value, {fmt(best, 3)}.{top}")
        if status == "stopped":
            verdict += (" A stop from an unverified source would be recorded but not executed, leaving release in the set: "
                        "correction has to reach the action interface to change what may run.")
    interpretation = (f"{calc} Timely review gross value = 0.90 x [0.98 x 10 + 0.02 x (-10)] + 0.10 x [0.94 x 0 + 0.06 x (-100)] "
                      f"= 8.64 + (-0.60) = {fmt(TIMELY_GROSS, 2)}. {verdict}")
    steps = [f"Timely review gross = 8.64 + (-0.60) = {fmt(TIMELY_GROSS, 2)}.",
             f"Net values: release {fmt(vals['release'], 3)}, review {fmt(vals['review'], 3)}, wait {fmt(vals['wait'], 3)}, hold {fmt(vals['hold'], 3)}.",
             f"Hold = 0.95 x {fmt(TIMELY_GROSS, 2)} + 0.05 x ({fmt(HOLD_TIMEOUT, 0)}) - {fmt(cost, 0)} - 1 = {fmt(vals['hold'], 3)}.",
             f"Status: {STATUS_TEXT[status]}",
             f"Authorized set: {metrics['Routes in the authorized set']}.",
             f"Highest value inside the set: {chosen} at {fmt(best, 3)}."]
    alt = (f"Horizontal bars for four routes with net values release {fmt(vals['release'], 2)}, review {fmt(vals['review'], 2)}, wait "
           f"{fmt(vals['wait'], 2)} and hold {fmt(vals['hold'], 2)}. Each carries its Authorized and Pre flags; "
           f"{'no route is excluded' if all(inside.values()) else 'excluded routes are hatched'}. The highest authorized route is {chosen.lower()}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: the review queue (M/M/1) and the route ledger

WINDOW_HOURS = 20 / 60
TASKS3 = [
    {"name": "routine", "agent_authorized": True, "risk": 0.02, "deadline": 2, "human_authorized": False, "review_received": False},
    {"name": "release", "agent_authorized": False, "risk": 0.05, "deadline": 2, "human_authorized": True, "review_received": True},
    {"name": "sensitive", "agent_authorized": False, "risk": 0.2, "deadline": 2, "human_authorized": True, "review_received": False},
]
TASK_APPROVAL = [{"name": "approval", "agent_authorized": False, "risk": 0.01, "deadline": 0.5, "human_authorized": True,
                  "review_received": True}]
QCASES = {
    "default": {"lam": 4.0, "mu": 3.0, "limit": 0.1, "tasks": TASKS3},
    "fast": {"lam": 4.0, "mu": 4.0, "limit": 0.1, "tasks": TASKS3},
    "transfer": {"lam": 1.0, "mu": 2.0, "limit": 0.05, "tasks": TASK_APPROVAL},
}


def queue_lab(case, fraction):
    c = QCASES[case]
    return evaluate({"arrival_rate": c["lam"], "service_rate": c["mu"], "delegation_fraction": float(fraction),
                     "agent_risk_limit": c["limit"], "tasks": c["tasks"]})


def queue_picture(case="default", delegation_fraction=0.5):
    c = QCASES[case]
    lam, mu, f = c["lam"], c["mu"], float(delegation_fraction)
    out = queue_lab(case, f)
    lab = out["metrics"]
    rows = out["tables"]
    load = lam * f
    stable = load < mu
    mean = lab["mean_review_sojourn"]
    if stable != lab["queue_stable"]:
        raise AssertionError("laboratory stability disagrees with f x lambda < mu")
    sat = min(1.0, mu / lam)
    ymax = 6 if case != "transfer" else 1.6
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    grid = np.linspace(0, min(sat, 1.0), 300)
    grid = grid[lam * grid < mu]
    left.plot(grid, 1.0 / (mu - lam * grid), color=PALETTE["navy"], linewidth=2)
    deadline = c["tasks"][1]["deadline"] if case != "transfer" else c["tasks"][0]["deadline"]
    left.axhline(deadline, color=PALETTE["terracotta"], linestyle="dotted", linewidth=1.6)
    label_point(left, 0.02, deadline, f"task deadline {fmt(deadline, 1)} h", color=PALETTE["terracotta"], dx=2, dy=4, ha="left", va="bottom").set_bbox(BOX)
    if case != "transfer":
        left.axhline(WINDOW_HOURS, color=PALETTE["gold"], linestyle="dotted", linewidth=1.6)
        label_point(left, 0.02, WINDOW_HOURS, "20-minute window", color=PALETTE["gold"], dx=2, dy=4, ha="left", va="bottom").set_bbox(BOX)
    left.axvspan(sat, 1.04, facecolor="white", edgecolor=PALETTE["terracotta"], hatch="///", alpha=0.9, linewidth=0)
    if sat < 1.0:
        left.axvline(sat, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.4)
        label_point(left, (sat + 1.04) / 2, ymax * 0.5, "no long-run\nmean exists", color=PALETTE["terracotta"], dx=0, dy=0,
                    ha="center", va="center").set_bbox(BOX)
    if stable:
        left.plot([f], [mean], "o", color=PALETTE["teal"], markersize=9)
        label_point(left, f, mean, f"{fmt(mean, 2)} h", color=PALETTE["teal"], dx=-8, dy=10, ha="right").set_bbox(BOX)
    else:
        left.plot([f], [0], "X", color=PALETTE["terracotta"], markersize=10, clip_on=False, zorder=6)
    left.set_xlim(0, 1.04)
    left.set_ylim(0, ymax)
    left.set_xlabel("Delegation fraction f")
    left.set_ylabel("Mean time in review (hours)")
    left.set_title(f"Arrivals {fmt(lam, 0)} per hour, reviewer finishes {fmt(mu, 0)} per hour", fontsize=11.5)

    cols = ["Needs\nreview", "Human\nauthority", "Packet\nreceived", "Mean in\ndeadline", "Released"]
    nrow = len(rows)
    for r, row in enumerate(rows):
        yy = nrow - 1 - r
        needs = row["delegation_required"]
        late = row["queue_mean_exceeds_deadline"]
        task = c["tasks"][r]
        cells = [("yes" if needs else "no", needs),
                 (("yes" if task["human_authorized"] else "no") if needs else "n/a", task["human_authorized"] if needs else None),
                 (("yes" if task["review_received"] else "no") if needs else "n/a", task["review_received"] if needs else None),
                 (("no" if late else "yes") if needs else "n/a", (not late) if needs else None),
                 ("yes" if row["released"] else "no", row["released"])]
        for x, (text, ok) in enumerate(cells):
            face = "white" if ok is None else (GREEN if ok else PINK)
            if x == 0:
                face = "#e6eaee"
            right.add_patch(Rectangle((x, yy), 1, 1, facecolor=face, edgecolor=PALETTE["ink"], linewidth=1,
                                      hatch="///" if (ok is False and x > 0) else None))
            right.text(x + 0.5, yy + 0.5, text, ha="center", va="center", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
    right.set_xlim(0, 5)
    right.set_ylim(0, nrow)
    right.set_xticks([x + 0.5 for x in range(5)], cols)
    right.set_yticks([nrow - 1 - r + 0.5 for r in range(nrow)], [row["task"] for row in rows])
    right.grid(False)
    right.set_xlabel("Release contract, checked column by column")
    right.set_ylabel("Task")
    right.set_title("Route ledger from the laboratory", fontsize=11.5)

    d_first = next((c["tasks"][r]["deadline"] for r, row in enumerate(rows) if row["delegation_required"]), None)
    tail = None
    if stable and d_first is not None:
        tail = 1 - math.exp(-(mu - load) * d_first)
    outcomes = []
    for row in rows:
        if not row["delegation_required"]:
            outcomes.append(f"{row['task']}: autonomous")
        elif row["released"]:
            outcomes.append(f"{row['task']}: released after review")
        else:
            why = []
            t = next(x for x in c["tasks"] if x["name"] == row["task"])
            if not t["human_authorized"]:
                why.append("no human authority")
            if not t["review_received"]:
                why.append("no review packet")
            if row["queue_mean_exceeds_deadline"]:
                why.append("queue mean beyond the deadline" if stable else "no stationary mean")
            outcomes.append(f"{row['task']}: blocked ({', '.join(why)})")
    metrics = {
        "Review arrivals f x lambda (per hour)": fmt(lab["effective_review_arrival_rate"], 2),
        "Reviewer capacity mu (per hour)": fmt(mu, 0),
        "Mean time in system": f"{fmt(mean, 2)} hours ({fmt(mean * 60, 0)} minutes)" if mean is not None
        else undefined("arrivals reach or exceed capacity"),
        "Tasks released": f"{lab['released_count']} of {len(rows)}",
        "Task outcomes": "; ".join(outcomes),
        "Chance the first delegated case meets its deadline": (fmt(tail, 3) if tail is not None else
                                                              ("not applicable" if d_first is None else undefined("no stationary mean"))),
    }
    if stable:
        within = "inside" if mean <= WINDOW_HOURS else "outside"
        qcalc = (f"Review arrivals = {fmt(f, 2)} x {fmt(lam, 0)} = {fmt(load, 2)} per hour, below {fmt(mu, 0)}. Mean time in system = "
                 f"1 / ({fmt(mu, 0)} - {fmt(load, 2)}) = 1 / {fmt(mu - load, 2)} = {fmt(mean, 2)} hours, which is {fmt(mean * 60, 0)} minutes"
                 + (f", {within} the 20-minute window" if case != "transfer" else "") + ". The reviewer's accuracy did not change; only the load did.")
        tcalc = (f" If the M/M/1 first-come-first-served assumption held exactly, a delegated case would meet a deadline of {fmt(d_first, 1)} "
                 f"hours with chance 1 - exp(-{fmt(mu - load, 2)} x {fmt(d_first, 1)}) = {fmt(tail, 3)}; a mean does not promise any single case meets its deadline."
                 if tail is not None else "")
    else:
        gap_text = "equals" if math.isclose(load, mu, abs_tol=1e-12) else "exceeds"
        qcalc = (f"Review arrivals = {fmt(f, 2)} x {fmt(lam, 0)} = {fmt(load, 2)} per hour, which {gap_text} the capacity {fmt(mu, 0)}. "
                 f"The formula would need 1 / ({fmt(mu, 0)} - {fmt(load, 2)}) = 1 / {signed(mu - load, 2)}, which is "
                 f"{'a division by zero' if math.isclose(load, mu, abs_tol=1e-12) else 'negative and meaningless as a time'}. "
                 "No stationary mean exists: the backlog grows without bound, so delegating this share is not a route the reviewer can serve.")
        tcalc = ""
    ledger = f" Ledger: {metrics['Task outcomes']}."
    interpretation = qcalc + tcalc + ledger
    steps = [f"Review arrivals = f x lambda = {fmt(f, 2)} x {fmt(lam, 0)} = {fmt(load, 2)} per hour; capacity mu = {fmt(mu, 0)}.",
             (f"Stable, since {fmt(load, 2)} < {fmt(mu, 0)}: mean = 1 / ({fmt(mu, 0)} - {fmt(load, 2)}) = {fmt(mean, 2)} hours." if stable
              else f"{fmt(load, 2)} is not below {fmt(mu, 0)}: no stationary mean, the backlog grows."),
             f"Tasks above the agent risk limit {fmt(c['limit'], 2)} or without agent authority need review: "
             + (", ".join(r["task"] for r in rows if r["delegation_required"]) or "none") + ".",
             "A delegated task is released only with human authority, a received review packet and a mean inside its deadline.",
             f"Result: {lab['released_count']} of {len(rows)} tasks released."]
    alt = (f"Left, mean time in the review queue against the delegation fraction, with the deadline lines and a marker at f = {fmt(f, 2)}"
           + (f" showing {fmt(mean, 2)} hours." if stable else "; the chosen share is past capacity, so no mean exists.")
           + f" Right, a ledger grid for {len(rows)} task{'s' if len(rows) > 1 else ''} with {lab['released_count']} released.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: wait only for a useful observation with an authorized fallback in every reachable state

GAIN_ON_ARRIVAL = 9.0
VALUE_NO_ARRIVAL = -1.0
DELAY_COST = 2.0
REACHABLE = ["Arrives\nin time", "Arrives\nlate", "Case\nchanges", "Source\nfails"]
BAD_INDEX = {"none": None, "late": 1, "changed": 2, "failed": 3}
BAD_NAME = {"late": "the observation arrives late", "changed": "the case changes", "failed": "the observation source fails"}


def wait_picture(arrival_probability=0.5, gap="none"):
    q = float(arrival_probability)
    bad = BAD_INDEX[gap]
    flags = [1, 1, 1, 1]
    if bad is not None:
        flags[bad] = 0
    ok = all(flags)
    gross = q * GAIN_ON_ARRIVAL + (1 - q) * VALUE_NO_ARRIVAL
    voi = gross - VALUE_NO_ARRIVAL            # gain over releasing now: q x (9 - (-1)) = 10 q
    informative = voi > DELAY_COST + 1e-9
    boundary = math.isclose(voi, DELAY_COST, abs_tol=1e-9)
    waits = informative and ok
    q_star = DELAY_COST / (GAIN_ON_ARRIVAL - VALUE_NO_ARRIVAL)
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    grid = np.linspace(0, 1, 101)
    left.plot(grid, grid * (GAIN_ON_ARRIVAL - VALUE_NO_ARRIVAL), color=PALETTE["navy"], linewidth=2)
    left.axhline(DELAY_COST, color=PALETTE["gold"], linestyle="dashed", linewidth=1.6)
    left.axvspan(q_star, 1.0, facecolor="#e8f1f1", edgecolor="#9fc3c5", hatch="..", linewidth=0)
    label_point(left, 1.0, DELAY_COST, "delay cost 2", color=PALETTE["gold"], dx=-4, dy=-5, ha="right", va="top").set_bbox(BOX)
    label_point(left, 0.3, 3.35, "VOI = 10 x q", color=PALETTE["navy"], dx=-6, dy=4, ha="right").set_bbox(BOX)
    color = PALETTE["teal"] if informative else PALETTE["terracotta"]
    left.plot([q], [voi], "o" if informative else "X", color=color, markersize=10)
    label_point(left, q, voi, "VOI above delay cost" if informative else "VOI not above delay cost", color=color,
                dx=8 if q < 0.6 else -8, dy=-16 if q < 0.55 else 12, ha="left" if q < 0.6 else "right",
                va="top" if q < 0.55 else "bottom").set_bbox(BOX)
    left.set_xlim(0, 1)
    left.set_ylim(0, 10.5)
    left.set_xlabel("Probability q that the confirmation arrives in time")
    left.set_ylabel("Value of information (utility units)")
    left.set_title("Condition 1: VOI above the delay cost", fontsize=11.5)

    for i, (name, flag) in enumerate(zip(REACHABLE, flags)):
        right.add_patch(Rectangle((i + 0.05, 0), 0.9, 1, facecolor=GREEN if flag else PINK,
                                  edgecolor=PALETTE["teal"] if flag else PALETTE["terracotta"], hatch=None if flag else "///", linewidth=1.3))
        right.text(i + 0.5, 0.5, "fallback\nauthorized" if flag else "NOT\nauthorized", ha="center", va="center", fontsize=10.5,
                   color=PALETTE["ink"], bbox=BOX)
    right.set_xlim(0, 4)
    right.set_ylim(0, 1)
    right.set_xticks([i + 0.5 for i in range(4)], REACHABLE)
    right.set_yticks([])
    right.grid(False)
    right.set_xlabel("State reachable by the deadline")
    right.set_ylabel("Fallback in that state")
    right.set_title("Condition 2: every reachable state", fontsize=11.5)

    if waits:
        decision = "Yes (waiting allowed)"
    elif not ok and informative:
        decision = "No (a reachable state has no authorized fallback)"
    elif not ok:
        decision = "No (VOI not above delay cost and a fallback is missing)"
    elif boundary:
        decision = "No (VOI equals delay cost)"
    else:
        decision = "No (VOI below delay cost)"
    metrics = {
        "Value of information (VOI)": fmt(voi, 2),
        "Delay cost": fmt(DELAY_COST, 2),
        "VOI minus delay cost": fmt(voi - DELAY_COST, 2),
        "Fallback authorized in every reachable state": "yes" if ok else f"no (fails when {BAD_NAME[gap]})",
        "Passes Equation (27.4)": decision,
        "Break-even arrival probability": fmt(q_star, 2),
    }
    calc = (f"VOI = {fmt(q, 1)} x 9 + {fmt(1 - q, 1)} x (-1) - (-1) = {fmt(voi, 2)}, and VOI - delay cost = {fmt(voi, 2)} - "
            f"{fmt(DELAY_COST, 0)} = {signed(voi - DELAY_COST, 2)}.")
    if waits:
        verdict = "Both conditions hold: the observation is worth more than the delay and a fallback is permitted in all four reachable states, so waiting passes."
    elif not ok:
        verdict = ("The condition on VOI " + ("holds" if informative else "fails") + f", but the fallback is not authorized when {BAD_NAME[gap]}. "
                   "Equation (27.4) needs authority to survive every reachable state: one gap and waiting could end with no permitted next action, "
                   "so it does not allow it.")
    elif boundary:
        verdict = ("VOI equals the delay cost exactly. Equation (27.4) uses a strict inequality, so this is a boundary case and waiting "
                   "is not allowed by the test; the break-even probability is 2 / 10 = 0.20.")
    else:
        verdict = "The expected information is worth less than the delay it costs, so the test does not allow waiting."
    interpretation = (f"{calc} {verdict} The equation is a necessary test (the word 'only if'): passing it does not prove waiting is "
                      "the best route, which Equation (27.3) still decides.")
    steps = [f"Gain from waiting over releasing now: VOI = {fmt(q, 1)} x 9 + {fmt(1 - q, 1)} x (-1) - (-1) = {fmt(voi, 2)}.",
             f"Condition 1: VOI {fmt(voi, 2)} against delay cost {fmt(DELAY_COST, 0)}, needing strictly more: {'holds' if informative else 'fails'}.",
             "Reachable states by the deadline: in time, late, the case changes, the source fails.",
             "Condition 2: the fallback must be authorized in every one: " + ("all four are." if ok else f"not when {BAD_NAME[gap]}."),
             f"Result: {decision}."]
    alt = (f"Left, a line of value of information against arrival probability with the delay cost at 2 and a marker at q = {fmt(q, 1)}. "
           f"Right, four boxes for the states reachable by the deadline, "
           + ("all marked fallback authorized." if ok else f"with one marked not authorized when {BAD_NAME[gap]}."))
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 27,
    "title": "The Mathematics of Delegation",
    "subtitle": "A handoff is an action with a destination, a deadline and a fallback, and it has to beat acting, waiting and narrowing on value.",
    "summary": (
        "These four demonstrations follow the chapter's pending transfer. A confident agent could send the money, but a "
        "named reviewer may know something it does not. Each demonstration changes one declared value and shows what moves "
        "the choice: who is more likely to be right and whether the answer arrives in time, which routes are authorized, how long "
        "a queue takes and who can be released through it, and whether waiting is worth its delay."
    ),
    "ask_skill": {
        "prompt": (
            "My review queue receives 4 tasks per hour and one reviewer finishes 3 per hour. I want to send half the tasks to "
            "review. For each task, here are its risk, deadline, whether the agent is authorized, whether a human holds authority "
            "and whether a review packet was received. Compute the mean time in review, say which tasks can be released under the "
            "contract, and tell me what to change if the delegation fraction rises to 0.9."
        ),
    },
    "demos": [
        {
            "id": "C27-D01",
            "title": "Defer by comparing correctness, then price the deadline",
            "question": "If the model is 0.78 sure, when should the case go to an expert instead, and does the expert's accuracy alone settle it once the answer has to arrive in time?",
            "equations": [EQ_ROUTE],
            "symbols": (
                "x is the case. The classifier's best class has probability max_y p(y | x) of being correct. p_E(x) is the "
                "probability that the designated expert E is correct on this case. Del(E, Delta) means delegate to E with maximum "
                "wait Delta. The arg max picks the most probable class. For the value comparison, a correct result is worth 10 and a "
                "wrong one -10, delegating costs a fee of 1 whether or not a reply arrives, and t is the probability the reply comes on "
                "time; a missed deadline triggers an authorized fallback worth 2. Probabilities are between 0 and 1."
            ),
            "prediction": "Pick the workbench case (acting is right 0.80, expert 0.95). With a guaranteed on-time return delegation wins 8 against 6. Now set the on-time probability to 0.60. Which route wins?",
            "prediction_options": ["Delegation still wins", "Acting wins", "They tie"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Delegation is worth 0.60 x 9 + 0.40 x 2 - 1 = 5.2, below acting at 6, even though the expert is still right 0.95 of the time.",
                "incorrect": "With on-time probability 0.60 delegation is worth 0.60 x 9 + 0.40 x 2 - 1 = 5.2, below acting at 6. The expert's 0.95 holds only when the reply arrives in time.",
            },
            "explanation": (
                "Equation (27.2) compares two chances of being correct and sends the case to whichever side is higher, with ties going "
                "to the expert. The model's confidence only matters as one of the two numbers. It also treats the delay as costless. Once the "
                "reply can miss its deadline, delegation's value mixes the timely branch and the fallback and pays the fee on both, so the "
                "expert's conditional accuracy cannot answer the question alone; the break-even on-time probability is where the two values meet."
            ),
            "application": (
                "A single confidence threshold such as 0.80, below which everything is sent to review, is justified only if the "
                "destination's correctness and timeliness are the same for all the cases it covers. Otherwise ask how likely the actual "
                "destination is to be right on this kind of case, how likely it is to answer in time, and compare with acting."
            ),
            "assumptions": (
                "Zero-one loss for Equation (27.2), one expert, and a known expert probability for this case type. The classifier's "
                "confidence is assumed calibrated. The utilities, fee and fallback value come from the workbench's constructed problem and "
                "are applied here to all four cases for comparison. The expert's accuracy is conditional on a timely reply and is not a "
                "permanent rating; if the probability is only a rough average, or the packet omits the evidence the expert needs, the "
                "comparison is no better than its inputs."
            ),
            "check": "A model is 0.97 sure and an expert is right with probability 0.95. Which route does Equation (27.2) choose, and by how much?",
            "answer": "0.95 < 0.97, so the route is the most probable class. The classifier leads by 0.97 - 0.95 = 0.02.",
            "provenance": "Constructed example: the chapter's two cases (model 0.78, expert 0.95 or 0.60) and the workbench's timely-return problem (acting 0.80, utilities 10 and -10, fee 1, fallback 2).",
            "source_section": "A value comparison, not a confidence threshold",
            "source_anchor": "a-value-comparison-not-a-confidence-threshold",
            "misconception": {
                "title": "Delegate whenever the model is uncertain",
                "text": (
                    "The chapter calls this an intuitive but mistaken rule. Uncertainty is only one side of a comparison: an uncertain model "
                    "may still be better than the available destination, and a confident model may be worse than a destination with decisive "
                    "side information."
                ),
            },
            "scope_note": {
                "text": (
                    "The chapter does not show how to estimate every action value, reviewer-error rate, queue delay, observation value, or "
                    "authority boundary in a live institution."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "case", "label": "Case", "values": ["chapter", "general", "bench", "tie"], "default": "chapter",
                 "value_labels": ["Chapter: model 0.78, expert 0.95", "Chapter: model 0.78, expert 0.60",
                                  "Workbench: act 0.80, expert 0.95", "Tie: model 0.78, expert 0.78"]},
                {"key": "timely", "label": "Probability the reply arrives on time (t)", "values": [1.0, 0.6, 5 / 7], "default": 1.0,
                 "value_labels": ["1.00 (guaranteed)", "0.60", "5/7 (break-even for the workbench case)"]},
            ],
            "function": "routing_picture",
        },
        {
            "id": "C27-D02",
            "title": "Four routes, but only the authorized ones can run",
            "question": "Which routes are in the authorized set, which of them has the highest net value, and what removes a route?",
            "equations": [EQ_AUTH, EQ_CHOOSE],
            "symbols": (
                "A route is one choice such as release now, review, wait or hold. The four rows are the chapter's act (release now), "
                "delegate (review), wait and narrow (the reversible hold); returning control is not given a value here. A_auth(x) is the "
                "set of actions in state x with Authorized = 1 (a declared grant covers them) and Pre = 1 (their state-specific "
                "preconditions hold, here a reviewer being available). R_auth(x) is the set of authorized routes, and V(route, x) is the "
                "route's net value in constructed utility units. Fraud has probability 0.10. A hold makes timely review likely (0.95) and costs "
                "the amount you choose; the timeout branch is worth -4. Review itself costs 1."
            ),
            "prediction": "The hold costs 2 by default and wins. Raise its cost to 5 with every route authorized. Which route has the highest value?",
            "prediction_options": ["The hold", "Waiting for confirmation", "Review with release on timeout", "Release now"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "At cost 5 the hold is worth 7.638 - 0.2 - 5 - 1 = 1.438, below waiting at 2, so waiting wins.",
                "incorrect": "At cost 5 the hold is worth 0.95 x 8.04 + 0.05 x (-4) - 5 - 1 = 1.438, below waiting at 2, so waiting has the highest value.",
            },
            "explanation": (
                "Equation (27.1) first filters the actions: a route is available only if it is authorized and its preconditions hold. "
                "Equation (27.3) then takes the highest-value route among those. Timely review has gross value 8.04, and the hold turns "
                "that into 0.95 x 8.04 + 0.05 x (-4) - 1 minus its own cost, so its value falls one point for each point of hold cost. An "
                "excluded route is not low-scoring, it is absent: if it would have won, it stays a recommendation."
            ),
            "application": (
                "Write the table for a consequential action: one row per route, each with its payoff, delay cost and fallback, and next to "
                "each row the grant that authorizes it and the precondition it needs. Then keep only the rows that are actually permitted. A "
                "delegation row also needs a named destination, a deadline and a fallback; without them it is not a route."
            ),
            "assumptions": (
                "Utilities, fraud probability, review error rates (detect fraud 0.94, wrongly reject 0.02) and response probabilities are the "
                "chapter's constructed values, and all four routes are costed on one scale. Real stakes may not fit one scale; a hard boundary "
                "may belong in the authorized set rather than in a cost. Changing any stated probability can change the winner. The reviewer "
                "accuracy here is held fixed, although in practice it can change with workload."
            ),
            "check": "If the hold cost 4 instead of 2, what is its net value and does it still beat waiting?",
            "answer": "0.95 x 8.04 + 0.05 x (-4) - 4 - 1 = 7.638 - 0.2 - 5 = 2.438, which is above waiting at 2, so it still wins narrowly.",
            "provenance": "Constructed example: the book's own route-value table for the pending transfer (values -1, 1.164, 2 and 4.438), with the hold cost and the authority status varied.",
            "source_section": "Queue economics: what timely review is worth",
            "source_anchor": "queue-economics-what-timely-review-is-worth",
            "misconception": {
                "title": "A high-scoring route can be executed",
                "text": (
                    "The chapter says a high-scoring action absent from the authorized set remains a recommendation, not an executable act, and "
                    "that the system can recommend an excluded action but cannot execute it merely because it ranked highly. Reversibility is not "
                    "free either: a hold has its own cost."
                ),
            },
            "scope_note": {
                "text": (
                    "The chapter does not make human review an oracle, nor does it rank every refusal above every act. Its bounded conclusion "
                    "is structural: delegation requires a named route and must compete with acting, waiting, narrowing and returning control."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "hold_cost", "label": "Cost of the reversible hold", "values": [2, 4, 5], "default": 2},
                {"key": "status", "label": "Authority and preconditions", "values": ["all", "holdno", "unavail", "stopped"], "default": "all",
                 "value_labels": ["All authorized, reviewer available", "Hold not authorized", "Reviewer unavailable", "Authorized stop honored (no release)"]},
            ],
            "function": "route_value_picture",
        },
        {
            "id": "C27-D03",
            "title": "Delegating more can make review slower than the deadline",
            "question": "How does sending a larger share of tasks to one reviewer change the mean time in review, and which tasks can then be released?",
            "equations": [EQ_MM1],
            "symbols": (
                "lambda is the arrival rate of tasks per hour. f is the delegation fraction, the share sent to review, so the reviewer "
                "sees f x lambda per hour. mu is the number of reviews the reviewer finishes per hour. The result is the mean hours a case "
                "spends waiting plus being reviewed. A stationary mean is that long-run average. In the ledger a task needs review when "
                "the agent is not authorized or its risk is above the agent's risk limit; it is released only with human authority, a received "
                "review packet and a mean time inside its deadline."
            ),
            "prediction": "With the default case (reviewer finishes 3 per hour), what happens to the mean time as the delegated share goes from 0.5 to 0.7? And at 0.9?",
            "prediction_options": [
                "1 hour, then 5 hours, then no stationary mean",
                "1 hour, then 1.4 hours, then 2 hours",
                "1 hour at every share below 1",
            ],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "1 / (3 - 2) = 1 hour, 1 / (3 - 2.8) = 5 hours, and at 0.9 the arrivals 3.6 exceed capacity 3, so no stationary mean exists.",
                "incorrect": "The time is 1 / (3 - f x 4): 1 hour at 0.5, 1 / 0.2 = 5 hours at 0.7, and at 0.9 the arrivals 3.6 exceed the capacity 3, so there is no stationary mean.",
            },
            "explanation": (
                "For one reviewer in the M/M/1 model, with random (Poisson) arrivals and exponentially distributed service times, the "
                "mean time in the system is 1/(mu - f x lambda) as long as the review arrivals stay below capacity. The time grows slowly at first and then steeply as the load approaches mu. "
                "At or beyond mu no stationary (long-run) mean exists and the backlog grows. The ledger shows what that does to the release "
                "contract: authority and a review packet are separate requirements from timing."
            ),
            "application": (
                "Before promising a review deadline, compare the planned review load with the reviewer's capacity. A rule such as "
                "delegate everything doubtful can overload the one route that was supposed to supply safety. Keep a route ledger per "
                "destination, with case type, deadline, packet completeness, response state and final action, so a failure can be placed: "
                "a bad recommendation, a wrong destination, a late answer or an unowned escalation."
            ),
            "assumptions": (
                "The M/M/1 model: one reviewer, independent random (Poisson) arrivals at a steady rate, exponentially distributed service "
                "times with a steady rate, and a long-run mean. Other service-time shapes give a different formula. Batching, priorities, "
                "correlated arrivals or a changing reviewer break the model. A mean does not promise that any single case meets its deadline, "
                "and the laboratory's deadline test is a planning diagnostic, not a probability. The faster reviewer is defined for this reader."
            ),
            "check": "With mu = 4 per hour and f = 0.75, what is the mean time in review in minutes?",
            "answer": "Review arrivals = 0.75 x 4 = 3 per hour. Mean = 1 / (4 - 3) = 1 hour, which is 60 minutes.",
            "provenance": "Constructed example: the notebook's default, changed and transfer cases and the chapter's queue example (4 tasks per hour, a reviewer finishing 3 per hour), computed with the laboratory's review-queue function, plus one faster reviewer defined for the reader.",
            "source_section": "Queue economics: what timely review is worth",
            "source_anchor": "queue-economics-what-timely-review-is-worth",
            "stepper": "delegation_fraction",
            "misconception": {
                "title": "A queue mean proves the deadline is met or missed",
                "text": (
                    "The chapter says a mean does not promise that any one case meets its deadline, and the notebook's output is a planning "
                    "diagnostic. Individual timing needs observed timestamps; the queue formula is a capacity-design check."
                ),
            },
            "controls": [
                {"key": "case", "label": "Case", "values": ["default", "fast", "transfer"], "default": "default",
                 "value_labels": ["Default: 4 per hour in, 3 per hour out, three tasks", "Faster reviewer: 4 per hour out, three tasks",
                                  "Transfer: 1 per hour in, 2 per hour out, one approval task"]},
                {"key": "delegation_fraction", "label": "Delegation fraction (f)", "values": [0.5, 0.7, 0.9, 1.0], "default": 0.5},
            ],
            "function": "queue_picture",
        },
        {
            "id": "C27-D04",
            "title": "Waiting needs an observation worth its delay and a fallback everywhere",
            "question": "When is it right to wait for a confirmation instead of acting now, and what if one state reachable by the deadline has no authorized fallback?",
            "equations": [EQ_WAIT],
            "symbols": (
                "VOI(o) is the value of the observation o: here the extra expected value of waiting for the signed confirmation "
                "compared with releasing now. DelayCost is what the wait costs (2 units). q is the probability that the confirmation "
                "arrives in time. The fallback is what the controller does at the deadline, and it must be an authorized action in every "
                "state reachable by then: the observation arrives in time, arrives late, the case changes, or the source fails."
            ),
            "prediction": "At q = 0.20, with a fallback authorized in every state, does the test allow waiting?",
            "prediction_options": ["Yes, VOI equals the delay cost", "No, the test needs VOI strictly above the delay cost", "Yes, 0.20 is above zero"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "VOI = 10 x 0.20 = 2, equal to the delay cost 2, and the inequality is strict, so waiting is not allowed.",
                "incorrect": "VOI = 0.20 x 9 + 0.80 x (-1) - (-1) = 2, which equals the delay cost 2. Equation (27.4) needs strictly more, so waiting fails at the boundary.",
            },
            "explanation": (
                "If the confirmation arrives, the transfer is handled correctly for a value of 9; if not, the fallback releases it at -1. "
                "So the gain over releasing now is 10 x q, a straight line. Equation (27.4) allows waiting only when that gain is strictly "
                "above the delay cost and the fallback is permitted in every reachable deadline state. One state without a permitted "
                "fallback is enough to fail the test, however valuable the observation."
            ),
            "application": (
                "When an agent says it will wait, ask four things: which fact would change the action, who supplies it, by when, and what "
                "happens if it never comes. If any answer is missing, there is no waiting action, only delay. If the observation source has "
                "become unavailable, move to the declared fallback instead of waiting under a plan that assumes its arrival."
            ),
            "assumptions": (
                "One observation and the chapter's constructed values (9, -1, delay cost 2). VOI is read here as the gain over releasing now, a "
                "simple special case of the Chapter 8 idea. The four reachable states are the ones the chapter lists; a real case can have more. "
                "Equation (27.4) is a necessary test: passing it does not make waiting the best route."
            ),
            "check": "If the delay cost rose to 3 and the confirmation still arrived with probability 0.5, does the test allow waiting (fallback authorized everywhere)?",
            "answer": "VOI = 0.5 x 9 + 0.5 x (-1) - (-1) = 5, and 5 > 3, so waiting passes. It would fail at or below q = 3 / 10 = 0.30, because equality fails the strict test.",
            "provenance": "Constructed example: the chapter's wait route (value 9 on arrival, -1 at the fallback, delay cost 2) with the arrival probability and the missing-fallback state varied.",
            "source_section": "Waiting is not hiding",
            "source_anchor": "waiting-is-not-hiding",
            "misconception": {
                "title": "Waiting is just not acting",
                "text": (
                    "The chapter says waiting with no identified observation, no deadline and no fallback is not an information action; it is "
                    "delay without a model. An agent that cannot say what missing fact would change the action, who supplies it, by when and what "
                    "happens otherwise has named uncertainty without resolving authority."
                ),
            },
            "scope_note": {
                "text": (
                    "The chapter does not prove that a learned rejector yields fair, lawful, safe, or corrigible deployment, and it does not "
                    "show how to estimate every observation value or authority boundary in a live institution."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "arrival_probability", "label": "Probability the confirmation arrives in time (q)", "values": [0.2, 0.5, 0.8], "default": 0.5},
                {"key": "gap", "label": "State with no authorized fallback", "values": ["none", "late", "changed", "failed"], "default": "none",
                 "value_labels": ["None: authorized in all four", "The observation arrives late", "The case changes", "The source fails"]},
            ],
            "function": "wait_picture",
        },
    ],
}

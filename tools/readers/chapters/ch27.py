"""Chapter 27 reader: The Mathematics of Delegation.

Four demonstrations built on Equations (27.2), (27.3), the chapter's M/M/1
mean time in system, and Equation (27.4). Demonstration 3 calls the
laboratory's own review-queue function (math_ai_agents.chapters.ch27.evaluate),
so the reader, the notebook and the chapter skill agree. Demonstrations 1, 2
and 4 compute the chapter's arithmetic directly. Every number is a constructed
teaching value; Demonstrations 2 to 4 reuse the numbers of the book's pending
transfer example and queue example.
"""
import math

import numpy as np

from math_ai_agents.chapters.ch27 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed, undefined

EQ_ROUTE = (
    r"\operatorname{route}^{\star}(x)="
    r"\begin{cases}"
    r"\operatorname{Del}(E,\Delta), & p_E(x)\geq \max_y p(y\mid x),\\"
    r"\arg\max_y p(y\mid x), & p_E(x)<\max_y p(y\mid x)."
    r"\end{cases}"
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


# Demonstration 1: route by comparing correctness (Equation 27.2)

def routing_picture(expert_correct=0.95, model_confidence=0.78):
    model, expert = float(model_confidence), float(expert_correct)
    delegate = expert >= model  # Equation (27.2): defer when p_E(x) >= max_y p(y | x)
    tie = math.isclose(expert, model, abs_tol=1e-9)
    gap = expert - model
    fig, ax = new_figure(height=3.8)
    names = ["Expert E correct" + ("\n(chosen route)" if delegate else ""),
             "Classifier's best class" + ("\n(chosen route)" if not delegate else ("\n(tied)" if tie else ""))]
    values = [expert, model]
    y = [1, 0]
    win = [delegate, not delegate]
    for yi, v, w in zip(y, values, win):
        ax.barh(yi, v, height=0.5, color=PALETTE["teal"] if w else "#8fa3b8",
                hatch="" if w else "///", edgecolor="white" if w else PALETTE["grey"], linewidth=1)
    ax.axvline(model, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    label_point(ax, model, 1.5, "dashed line: classifier's best class", color=PALETTE["grey"], dx=-5, dy=0, ha="right", va="center")
    for yi, v in zip(y, values):
        label_point(ax, v, yi, fmt(v, 2), color=PALETTE["ink"], dx=-6, dy=0, ha="right", va="center").set_bbox(BOX)
    ax.set_yticks(y, names)
    ax.set_xlim(0, 1.0)
    ax.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_ylim(-0.6, 1.6)
    ax.set_xlabel("Probability of a correct result (constructed values)")
    ax.set_ylabel("Who answers")
    ax.grid(axis="y", alpha=0)
    if tie:
        route = "Delegate to E (tie, so (27.2) defers)"
        verdict = (f"The two probabilities are equal at {fmt(model, 2)}. Equation (27.2) uses 'at least as large', so it "
                   "sends the case to the expert even though the classifier would do equally well. Any tie rule is a "
                   "design choice; the equation fixes this one.")
    elif delegate:
        route = "Delegate to E"
        verdict = (f"The expert is more likely to be correct than the classifier's best class, so Equation (27.2) delegates. "
                   f"The same classifier probability {fmt(model, 2)} would keep the prediction against an expert below {fmt(model, 2)} "
                   f"and delegates against an expert at or above it.")
    else:
        route = "Predict the most probable class"
        verdict = (f"The classifier's best class is more likely to be correct than the expert, so Equation (27.2) keeps "
                   f"the prediction. A confidence of {fmt(model, 2)} is not a reason to delegate by itself.")
    ax.set_title(f"Route: {route}", fontsize=11.5)
    metrics = {
        "Classifier best class probability": fmt(model, 2),
        "Expert correctness p_E": fmt(expert, 2),
        "Expert minus classifier": fmt(gap, 2),
        "Route chosen by Equation (27.2)": route,
    }
    cmp_sign = ">=" if delegate else "<"
    interpretation = (
        f"Compare p_E = {fmt(expert, 2)} with the best class probability {fmt(model, 2)}: gap = {fmt(expert, 2)} - "
        f"{fmt(model, 2)} = {signed(gap, 2)}, and {fmt(expert, 2)} {cmp_sign} {fmt(model, 2)}. {verdict} "
        "This is the book's zero-one special case: delay is treated as costless and the expert's probability is assumed known."
    )
    return fig, metrics, interpretation


# Demonstration 2: choose among authorized routes (Equation 27.3)

# The book's constructed decision model for the pending transfer. Fraud probability 0.10.
P_FRAUD = 0.10
RELEASE_NOW = 0.90 * 10 + P_FRAUD * (-100)                     # -1
TIMELY_GROSS = 0.90 * (0.98 * 10 + 0.02 * (-10)) + P_FRAUD * (0.94 * 0 + 0.06 * (-100))  # 8.04
HOLD_TIMEOUT = -4.0
REVIEW_FEE = 1.0
WAIT_NET = 0.50 * 9 + 0.50 * (-1) - 2                          # 2


def route_values(hold_cost):
    review = 0.35 * TIMELY_GROSS + 0.65 * RELEASE_NOW - REVIEW_FEE
    hold = 0.95 * TIMELY_GROSS + 0.05 * HOLD_TIMEOUT - float(hold_cost) - REVIEW_FEE
    return {"release": RELEASE_NOW, "review": review, "wait": WAIT_NET, "hold": hold}


def route_value_picture(hold_cost=2, hold_authorized="yes"):
    cost = float(hold_cost)
    authorized = hold_authorized == "yes"
    vals = route_values(cost)
    labels = {
        "release": "Release now",
        "review": "Review;\nrelease on timeout",
        "wait": "Wait for confirmation;\nrelease on timeout",
        "hold": "Reversible hold and review;\nreturn on timeout",
    }
    feasible = {k: v for k, v in vals.items() if k != "hold" or authorized}
    best = max(feasible.values())
    winner = [k for k, v in feasible.items() if abs(v - best) < 1e-9]
    keys = list(labels)
    y = np.arange(len(keys))[::-1]
    fig, ax = new_figure(height=4.2)
    for yi, k in zip(y, keys):
        v = vals[k]
        if k == "hold" and not authorized:
            ax.barh(yi, v, height=0.56, color="white", edgecolor=PALETTE["terracotta"], hatch="xx", linewidth=1)
            ax.text(max(v, 0) + 0.15, yi, f"excluded: not\nauthorized\n(would be {fmt(v, 3)})", va="center", fontsize=10.5, color=PALETTE["terracotta"])
        else:
            ax.barh(yi, v, height=0.56, color=PALETTE["teal"] if k in winner else "#8fa3b8")
            tag = "  highest" if k in winner else ""
            ax.text(max(v, 0) + 0.15, yi, fmt(v, 3) + tag, va="center", fontsize=11, color=PALETTE["ink"])
    ax.axvline(0, color=PALETTE["ink"], linewidth=1)
    ax.set_yticks(y, [labels[k] for k in keys])
    ax.set_xlim(-2, 9)
    ax.set_xlabel("Net expected value (constructed utility units)")
    ax.set_ylabel("Route")
    ax.grid(axis="y", alpha=0)
    ax.set_title(f"Hold costs {fmt(cost, 0)}; hold {'authorized' if authorized else 'not authorized'}", fontsize=11.5)
    hold_base = 0.95 * TIMELY_GROSS + 0.05 * HOLD_TIMEOUT - REVIEW_FEE  # 6.438 before the hold cost
    break_even = hold_base - WAIT_NET
    chosen = " and ".join(labels[k].replace("\n", " ") for k in winner)
    metrics = {labels[k].replace("\n", " "): (fmt(vals[k], 3) if (k != "hold" or authorized) else f"{fmt(vals[k], 3)} (excluded)")
               for k in keys}
    metrics["Highest of the four modeled routes"] = chosen
    metrics["Hold cost at which waiting (2) overtakes it"] = fmt(break_even, 3)
    calc = (f"Hold = 0.95 x {fmt(TIMELY_GROSS, 2)} + 0.05 x ({fmt(HOLD_TIMEOUT, 0)}) - {fmt(cost, 0)} - 1 = {fmt(vals['hold'], 3)}.")
    if not authorized:
        verdict = (f"The hold is outside the authorized set, so it cannot be chosen even though its value {fmt(vals['hold'], 3)} "
                   f"is {'higher' if vals['hold'] > best else 'lower'} than the best remaining route. Among the authorized routes, "
                   f"{chosen} has the highest value, {fmt(best, 3)}.")
    elif "hold" in winner:
        verdict = (f"The hold wins: {fmt(vals['hold'], 3)} is above waiting at {fmt(WAIT_NET, 0)}. Its value before its own cost is "
                   f"0.95 x {fmt(TIMELY_GROSS, 2)} + 0.05 x ({fmt(HOLD_TIMEOUT, 0)}) - 1 = {fmt(hold_base, 3)}, so its cost can rise to "
                   f"{fmt(hold_base, 3)} - {fmt(WAIT_NET, 0)} = {fmt(break_even, 3)} before waiting overtakes it.")
    else:
        verdict = (f"The hold's {fmt(vals['hold'], 3)} is now below waiting at {fmt(WAIT_NET, 0)}, because the cost {fmt(cost, 0)} "
                   f"is above the break-even {fmt(break_even, 3)}. Reversibility is not free.")
    interpretation = (f"{calc} Timely review gross value = 0.90 x [0.98 x 10 + 0.02 x (-10)] + 0.10 x [0.94 x 0 + 0.06 x (-100)] "
                      f"= 8.64 + (-0.60) = {fmt(TIMELY_GROSS, 2)}. {verdict}")
    return fig, metrics, interpretation


# Demonstration 3: the review queue (M/M/1 mean time in system)

ARRIVALS = 4.0   # tasks per hour (the book's constructed example)
WINDOW_HOURS = 20 / 60


def queue_lab(service, fraction):
    data = {
        "arrival_rate": ARRIVALS,
        "service_rate": float(service),
        "delegation_fraction": float(fraction),
        "agent_risk_limit": 0.1,
        "tasks": [{"name": "transfer", "agent_authorized": False, "risk": 0.2, "deadline": WINDOW_HOURS,
                   "human_authorized": True, "review_received": True}],
    }
    return evaluate(data)["metrics"]


def queue_picture(service_rate=3, delegation_fraction=0.5):
    mu, f = float(service_rate), float(delegation_fraction)
    lab = queue_lab(mu, f)
    load = ARRIVALS * f
    stable = load < mu
    mean = lab["mean_review_sojourn"]
    if stable != lab["queue_stable"]:
        raise AssertionError("laboratory stability disagrees with f x lambda < mu")
    sat = min(1.0, mu / ARRIVALS)
    fig, ax = new_figure(height=4.2)
    grid = np.linspace(0, sat, 400)[:-1] if sat <= 1 else np.linspace(0, 1, 400)
    grid = grid[ARRIVALS * grid < mu]
    ax.plot(grid, 1.0 / (mu - ARRIVALS * grid), color=PALETTE["navy"], linewidth=2)
    ax.axhline(WINDOW_HOURS, color=PALETTE["gold"], linestyle="dotted", linewidth=1.6)
    label_point(ax, 1.04, WINDOW_HOURS, "20-minute window", color=PALETTE["gold"], dx=-4, dy=4, ha="right", va="bottom").set_bbox(BOX)
    ax.axvspan(sat, 1.04, facecolor="white", edgecolor=PALETTE["terracotta"], hatch="///", alpha=0.9, linewidth=0)
    if sat < 1.0:
        ax.axvline(sat, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.4)
        label_point(ax, (sat + 1.04) / 2, 3.0, "no long-run\nmean exists\n(X: chosen f)", color=PALETTE["terracotta"], dx=0, dy=0, ha="center", va="center").set_bbox(BOX)
    else:
        label_point(ax, 1.0, 5.2, "f = 1 reaches\ncapacity" + ("\n(X: chosen f)" if not stable else ""), color=PALETTE["terracotta"], dx=-6, dy=0, ha="right", va="center").set_bbox(BOX)
    if stable:
        ax.plot([f], [mean], "o", color=PALETTE["teal"], markersize=9)
        label_point(ax, f, mean, f"{fmt(mean, 2)} h", color=PALETTE["teal"], dx=-8, dy=8, ha="right").set_bbox(BOX)
    else:
        ax.plot([f], [0], "X", color=PALETTE["terracotta"], markersize=10, clip_on=False, zorder=6)
    ax.set_xlim(0, 1.04)
    ax.set_ylim(0, 6)
    ax.set_xlabel("Delegation fraction f (share of tasks sent to review)")
    ax.set_ylabel("Mean time in review system (hours)")
    ax.set_title(f"Arrivals 4 per hour, reviewer finishes {fmt(mu, 0)} per hour", fontsize=11.5)
    metrics = {
        "Review arrivals f x lambda (per hour)": fmt(lab["effective_review_arrival_rate"], 2),
        "Reviewer capacity mu (per hour)": fmt(mu, 0),
        "Mean time in system": f"{fmt(mean, 2)} hours ({fmt(mean * 60, 0)} minutes)" if mean is not None
        else undefined("arrivals reach or exceed capacity"),
        "Mean within the 20-minute window": "not applicable" if mean is None else ("yes" if mean <= WINDOW_HOURS else "no"),
    }
    if stable:
        within = "inside" if mean <= WINDOW_HOURS else "outside"
        interpretation = (
            f"Review arrivals = {fmt(f, 2)} x 4 = {fmt(load, 2)} per hour, below {fmt(mu, 0)}. Mean time in system = "
            f"1 / ({fmt(mu, 0)} - {fmt(load, 2)}) = 1 / {fmt(mu - load, 2)} = {fmt(mean, 2)} hours, which is {fmt(mean * 60, 0)} minutes, "
            f"{within} the 20-minute window. The reviewer's accuracy did not change; only the load did. A mean does not promise "
            "that any single case meets its deadline."
        )
    else:
        gap_text = "equals" if math.isclose(load, mu, abs_tol=1e-12) else "exceeds"
        interpretation = (
            f"Review arrivals = {fmt(f, 2)} x 4 = {fmt(load, 2)} per hour, which {gap_text} the capacity {fmt(mu, 0)}. "
            f"The formula would need 1 / ({fmt(mu, 0)} - {fmt(load, 2)}) = 1 / {signed(mu - load, 2)}, which is "
            f"{'a division by zero' if math.isclose(load, mu, abs_tol=1e-12) else 'negative and meaningless as a time'}. "
            "No stationary (long-run) mean exists: the backlog grows without bound, so delegating this share is not a route the reviewer can serve."
        )
    return fig, metrics, interpretation


# Demonstration 4: wait only for a useful observation with an authorized fallback (Equation 27.4)

GAIN_ON_ARRIVAL = 9.0     # book: release the legitimate, stop the fraudulent, expected gross value 9
VALUE_NO_ARRIVAL = -1.0   # book: deadline fallback releases the transfer
DELAY_COST = 2.0          # book: declared cost of five minutes of waiting


def wait_picture(arrival_probability=0.5, fallback_authorized="yes"):
    q = float(arrival_probability)
    ok = fallback_authorized == "yes"
    gross = q * GAIN_ON_ARRIVAL + (1 - q) * VALUE_NO_ARRIVAL
    voi = gross - VALUE_NO_ARRIVAL            # gain over releasing now: q x (9 - (-1)) = 10 q
    net = gross - DELAY_COST
    informative = voi > DELAY_COST + 1e-9
    boundary = math.isclose(voi, DELAY_COST, abs_tol=1e-9)
    waits = informative and ok
    q_star = DELAY_COST / (GAIN_ON_ARRIVAL - VALUE_NO_ARRIVAL)
    fig, ax = new_figure(height=4.2)
    grid = np.linspace(0, 1, 101)
    ax.plot(grid, grid * (GAIN_ON_ARRIVAL - VALUE_NO_ARRIVAL), color=PALETTE["navy"], linewidth=2)
    ax.axhline(DELAY_COST, color=PALETTE["gold"], linestyle="dashed", linewidth=1.6)
    ax.axvspan(q_star, 1.0, facecolor="#e8f1f1", edgecolor="#9fc3c5", hatch="..", linewidth=0)
    label_point(ax, 1.0, DELAY_COST, "delay cost 2", color=PALETTE["gold"], dx=-4, dy=-5, ha="right", va="top").set_bbox(BOX)
    label_point(ax, 0.3, 3.0 + 0.35, "VOI = 10 x q", color=PALETTE["navy"], dx=-6, dy=4, ha="right").set_bbox(BOX)
    label_point(ax, 1.0, DELAY_COST, f"q above break-even {fmt(q_star, 2)}", color=PALETTE["teal"], dx=-4, dy=5, ha="right", va="bottom").set_bbox(BOX)
    color = PALETTE["teal"] if waits else PALETTE["terracotta"]
    ax.plot([q], [voi], "o" if waits else "X", color=color, markersize=10)
    verdict_short = "wait" if waits else "do not wait"
    label_point(ax, q, voi, f"{verdict_short}", color=color, dx=8 if q < 0.8 else -8, dy=-14 if q < 0.55 else 10,
                ha="left" if q < 0.8 else "right", va="top" if q < 0.55 else "bottom").set_bbox(BOX)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 10.5)
    ax.set_xlabel("Probability q that the signed confirmation arrives in time")
    ax.set_ylabel("Value of information (utility units)")
    ax.set_title(f"Confirmation arrives with probability {fmt(q, 1)}; fallback {'authorized' if ok else 'not authorized'}", fontsize=11.5)
    if waits:
        decision = "Yes (waiting allowed)"
    elif not ok:
        decision = "No (fallback not authorized)"
    elif boundary:
        decision = "No (VOI equals delay cost)"
    else:
        decision = "No (VOI below delay cost)"
    metrics = {
        "Value of information (VOI)": fmt(voi, 2),
        "Delay cost": fmt(DELAY_COST, 2),
        "VOI minus delay cost": fmt(voi - DELAY_COST, 2),
        "Fallback authorized at the deadline": "yes" if ok else "no",
        "Passes Equation (27.4)": decision,
        "Break-even arrival probability": fmt(q_star, 2),
    }
    calc = (f"VOI = {fmt(q, 1)} x 9 + {fmt(1 - q, 1)} x (-1) - (-1) = {fmt(voi, 2)}, and VOI - delay cost = {fmt(voi, 2)} - "
            f"{fmt(DELAY_COST, 0)} = {signed(voi - DELAY_COST, 2)}.")
    if waits:
        verdict = "Both conditions hold: the observation is worth more than the delay and the fallback is permitted, so waiting passes."
    elif not ok:
        verdict = ("The condition on VOI " + ("holds" if informative else "fails") + ", but the fallback is not authorized in the "
                   "deadline state. The inequality is not enough: waiting could end with no permitted next action, so Equation (27.4) "
                   "does not allow it.")
    elif boundary:
        verdict = ("VOI equals the delay cost exactly. Equation (27.4) uses a strict inequality, so this is a boundary case and waiting "
                   "is not allowed by the test; the break-even probability is 2 / 10 = 0.20.")
    else:
        verdict = "The expected information is worth less than the delay it costs, so the test does not allow waiting."
    interpretation = (f"{calc} {verdict} The equation is a necessary test (the word 'only if'): passing it does not prove waiting is "
                      "the best route, which Equation (27.3) still decides.")
    return fig, metrics, interpretation


CHAPTER = {
    "number": 27,
    "title": "The Mathematics of Delegation",
    "subtitle": "A handoff is an action with a destination, a deadline and a fallback, and it has to beat acting, waiting and narrowing on value.",
    "summary": (
        "These four demonstrations follow the chapter's pending transfer. A confident agent could send the money, but a "
        "named reviewer may know something it does not. Each demonstration changes one declared value and shows what moves "
        "the choice: who is more likely to be right, which routes are authorized, how long a queue takes, and whether "
        "waiting is worth its delay."
    ),
    "demos": [
        {
            "id": "C27-D01",
            "title": "Defer by comparing correctness, not by low confidence",
            "question": "If the model is 0.78 sure, when should the case go to an expert instead?",
            "equations": [EQ_ROUTE],
            "symbols": (
                "x is the case. The classifier's best class has probability max_y p(y | x) of being correct. p_E(x) is the "
                "probability that the designated expert E is correct on this case. Del(E, Delta) means delegate to E with maximum "
                "wait Delta. The arg max picks the most probable class. Probabilities are between 0 and 1."
            ),
            "prediction": "The model is 0.78 sure. With an expert who is right 0.60 of the time, then 0.95, does the route change? What happens at 0.78?",
            "explanation": (
                "Equation (27.2) compares two chances of being correct and sends the case to whichever side is higher, "
                "with ties going to the expert. The model's confidence only matters as one of the two numbers. The same "
                "confidence of 0.78 delegates to an expert at 0.95 and keeps the prediction against an expert at 0.60."
            ),
            "application": (
                "A single confidence threshold such as 0.80, below which everything is sent to review, is justified only if the "
                "destination's correctness is the same for all the cases it covers. Otherwise ask how likely the actual "
                "destination is to be right on this kind of case, and compare."
            ),
            "assumptions": (
                "Zero-one loss, one expert, and a known expert probability for this case type. The classifier's confidence is "
                "assumed calibrated, so it equals the true probability of being right. The delay Delta is not priced here, "
                "which is a design extension the chapter adds beyond the source result. If the expert probability is only a rough "
                "average, or the packet omits the evidence the expert needs, the comparison is no better than its inputs."
            ),
            "check": "A model is 0.97 sure and an expert is right with probability 0.95. Which route does Equation (27.2) choose, and by how much?",
            "answer": "0.95 < 0.97, so the route is the most probable class. The classifier leads by 0.97 - 0.95 = 0.02.",
            "provenance": "Constructed example: the chapter's two cases with model confidence 0.78 and expert correctness 0.95 or 0.60, plus values defined for the reader (0.97).",
            "source_section": "A value comparison, not a confidence threshold",
            "source_anchor": "a-value-comparison-not-a-confidence-threshold",
            "controls": [
                {"key": "expert_correct", "label": "Probability the expert is correct", "values": [0.6, 0.78, 0.95], "default": 0.95},
                {"key": "model_confidence", "label": "Classifier's best class probability", "values": [0.78, 0.97], "default": 0.78},
            ],
            "function": "routing_picture",
        },
        {
            "id": "C27-D02",
            "title": "Four routes for the pending transfer",
            "question": "Among the authorized routes, which has the highest net value, and what makes it lose?",
            "equations": [EQ_CHOOSE],
            "symbols": (
                "A route is one choice such as release now, review, wait or hold. The four rows are the chapter's act (release now), "
                "delegate (review), wait and narrow (the reversible hold); returning control is not given a value here. R_auth(x) is the set of routes authorized in the "
                "current state x, and V(route, x) is the route's declared net value in constructed utility units. Fraud has "
                "probability 0.10. A hold makes timely review likely (0.95) and costs the amount you choose; the timeout "
                "branch is worth -4. Review itself costs 1."
            ),
            "prediction": "The hold costs 2 by default. Raise its cost to 5. Does it still win? Then mark it not authorized at cost 2.",
            "explanation": (
                "Equation (27.3) takes the highest-value route, but only among routes that are authorized. Timely review has gross "
                "value 8.04. The hold turns that into 0.95 x 8.04 + 0.05 x (-4) - 1 minus its own cost, so its value falls one point "
                "for each point of hold cost. An excluded route is not low-scoring, it is absent."
            ),
            "application": (
                "Write the table for a consequential action: one row per route, each with its payoff, delay cost and fallback. "
                "Then ask which rows are actually permitted. A high-ranking row that is not permitted is a recommendation."
            ),
            "assumptions": (
                "Utilities, fraud probability, review error rates and response probabilities are the chapter's constructed values, "
                "and all four routes are costed on one scale. Real stakes may not fit one scale; a hard boundary may belong in the "
                "authorized set rather than in a cost. Changing any stated probability can change the winner."
            ),
            "check": "If the hold cost 4 instead of 2, what is its net value and does it still beat waiting?",
            "answer": "0.95 x 8.04 + 0.05 x (-4) - 4 - 1 = 7.638 - 0.2 - 5 = 2.438, which is above waiting at 2, so it still wins narrowly.",
            "provenance": "Constructed example: the book's own route-value table for the pending transfer (values -1, 1.164, 2 and 4.438), with the hold cost and its authorization varied.",
            "source_section": "Queue economics: what timely review is worth",
            "source_anchor": "queue-economics-what-timely-review-is-worth",
            "controls": [
                {"key": "hold_cost", "label": "Cost of the reversible hold", "values": [2, 4, 5], "default": 2},
                {"key": "hold_authorized", "label": "Is the hold authorized?", "values": ["yes", "no"], "default": "yes",
                 "value_labels": ["Yes, authorized", "No, not authorized"]},
            ],
            "function": "route_value_picture",
        },
        {
            "id": "C27-D03",
            "title": "Delegating more can make review slower than the deadline",
            "question": "How does sending a larger share of tasks to one reviewer change the mean time a case spends in review?",
            "equations": [EQ_MM1],
            "symbols": (
                "lambda is the arrival rate of tasks (4 per hour here). f is the delegation fraction, the share sent to review, so "
                "the reviewer sees f x lambda per hour. mu is the number of reviews the reviewer finishes per hour. The result "
                "is the mean hours a case spends waiting plus being reviewed. A stationary mean is that long-run average."
            ),
            "prediction": "With a reviewer finishing 3 per hour, what happens to the mean time as the delegated share goes from 0.5 to 0.7? And at 0.9?",
            "explanation": (
                "For one reviewer in the M/M/1 model, with random (Poisson) arrivals and exponentially distributed service times, the "
                "mean time in the system is 1/(mu - f x lambda) as long as the review arrivals stay below capacity. The time grows slowly at first and then steeply as the load approaches mu. "
                "At or beyond mu no stationary (long-run) mean exists and the backlog grows."
            ),
            "application": (
                "Before promising a review deadline, compare the planned review load with the reviewer's capacity. A rule such as "
                "delegate everything doubtful can overload the one route that was supposed to supply safety."
            ),
            "assumptions": (
                "The M/M/1 model: one reviewer, independent random (Poisson) arrivals at a steady rate, exponentially distributed service "
                "times with a steady rate, and a long-run mean. Other service-time shapes give a different formula. Batching, priorities, correlated arrivals or a changing reviewer break the model. A mean does not promise that any "
                "single case meets its deadline."
            ),
            "check": "With mu = 4 per hour and f = 0.75, what is the mean time in review in minutes?",
            "answer": "Review arrivals = 0.75 x 4 = 3 per hour. Mean = 1 / (4 - 3) = 1 hour, which is 60 minutes.",
            "provenance": "Constructed example: the chapter's queue example (4 tasks per hour, a reviewer finishing 3 per hour), computed with the laboratory's review-queue function, plus one faster reviewer defined for the reader.",
            "source_section": "Queue economics: what timely review is worth",
            "source_anchor": "queue-economics-what-timely-review-is-worth",
            "controls": [
                {"key": "service_rate", "label": "Reviews finished per hour (mu)", "values": [3, 4], "default": 3},
                {"key": "delegation_fraction", "label": "Delegation fraction (f)", "values": [0.5, 0.7, 0.9, 1.0], "default": 0.5},
            ],
            "function": "queue_picture",
        },
        {
            "id": "C27-D04",
            "title": "Waiting needs an observation worth its delay",
            "question": "When is it right to wait for a confirmation instead of acting now?",
            "equations": [EQ_WAIT],
            "symbols": (
                "VOI(o) is the value of the observation o: here the extra expected value of waiting for the signed confirmation "
                "compared with releasing now. DelayCost is what the wait costs (2 units). q is the probability that the confirmation "
                "arrives in time. The fallback is what the controller does if it does not, and it must be an authorized action."
            ),
            "prediction": "At q = 0.2, does the test allow waiting? What if the confirmation is far more likely but the fallback is not authorized?",
            "explanation": (
                "If the confirmation arrives, the transfer is handled correctly for a value of 9; if not, the fallback releases it at -1. "
                "So the gain over releasing now is 10 x q, a straight line. Equation (27.4) allows waiting only when that gain is strictly "
                "above the delay cost and the fallback is permitted."
            ),
            "application": (
                "When an agent says it will wait, ask four things: which fact would change the action, who supplies it, by when, and what "
                "happens if it never comes. If any answer is missing, there is no waiting action, only delay."
            ),
            "assumptions": (
                "One observation, one deadline state without the confirmation, and the chapter's constructed values (9, -1, delay cost 2). "
                "VOI is read here as the gain over releasing now, a simple special case of the Chapter 8 idea. Equation (27.4) is a "
                "necessary test: passing it does not make waiting the best route."
            ),
            "check": "If the delay cost rose to 3 and the confirmation still arrived with probability 0.5, does the test allow waiting (fallback authorized)?",
            "answer": "VOI = 0.5 x 9 + 0.5 x (-1) - (-1) = 5, and 5 > 3, so waiting passes. It would fail at or below q = 3 / 10 = 0.30, because equality fails the strict test.",
            "provenance": "Constructed example: the chapter's wait route (value 9 on arrival, -1 at the fallback, delay cost 2) with the arrival probability varied.",
            "source_section": "Waiting is not hiding",
            "source_anchor": "waiting-is-not-hiding",
            "controls": [
                {"key": "arrival_probability", "label": "Probability the confirmation arrives in time (q)", "values": [0.2, 0.3, 0.5, 0.8], "default": 0.5},
                {"key": "fallback_authorized", "label": "Is the fallback authorized?", "values": ["yes", "no"], "default": "yes",
                 "value_labels": ["Yes, authorized", "No, not authorized"]},
            ],
            "function": "wait_picture",
        },
    ],
}

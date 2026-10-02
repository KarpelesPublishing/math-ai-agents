"""Chapter 21 reader: Markets, Teams, and Institutions.

Four demonstrations on the chapter's Braess network (one unit of traffic by
default, two outer routes, a directed zero-latency middle link) and on
Equations (21.1) to (21.3). Demonstrations 1, 2 and 4 call the laboratory's
own congestion function (math_ai_agents.chapters.ch21.evaluate), so the
reader, the notebook and the chapter skill agree. Demonstration 3 adds the
chapter's marginal-cost charge (a charge on every congestible edge), which the
laboratory does not compute; it is derived directly and checked against the
laboratory's optimum. Every number is a constructed teaching value.

Network units used throughout: each congestible edge (S-U and L-T) has
latency equal to its flow, each fixed edge (U-T and S-L) has latency 1, and
the middle link U-L has latency 0 (plus an optional constant overhead in
Demonstration 2). Capacity and outer delay are both 1, as in the chapter.
"""
import math

import numpy as np
from matplotlib.patches import Patch

from math_ai_agents.chapters.ch21 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

EQ_TL = r"\operatorname{TL}(q) \;=\; \sum_{e\in\mathcal E} q_e\,\ell_e(q_e)"
EQ_BOUND = (r"\frac{\operatorname{TL}(q^{\mathrm{NE}})}{\operatorname{TL}(q^{\star})} \;\leq\; \frac{4}{3}"
            r"\qquad\text{when every }\ell_e(q_e)=a_e q_e+b_e\text{ with }a_e,b_e\geq0")
EQ_MC = (r"\ell^{\mathrm{mc}}_e(q_e) \;=\; \ell_e(q_e)+q_e\ell'_e(q_e),"
         r"\qquad \ell_e(q_e)=a_e q_e+b_e\;\Longrightarrow\;\ell^{\mathrm{mc}}_e(q_e)=2a_e q_e+b_e")
EQ_EXTRA = r"(1+\gamma_{\mathrm{cap}})r"
EQ_FACTOR = r"1/\gamma_{\mathrm{cap}}"

WHITE = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
TOL = 1e-9


def lab(demand, overhead=0.0, toll=0.0):
    """The laboratory's equilibrium and optimum for the chapter's network (capacity 1, outer delay 1)."""
    return evaluate({"demand": float(demand), "capacity": 1, "constant_time": 1,
                     "shortcut_overhead": float(overhead), "shortcut_toll": float(toll)})["metrics"]


def total_latency(x, z, overhead=0.0):
    """Equation (21.1) summed over the five edges: x on each outer route, z on the middle route."""
    v = x + z  # flow on each congestible edge
    return 2 * v * v + 2 * x * 1.0 + z * overhead


def exact(x, digits=3):
    """Show a calculation value without hiding digits: at least `digits` decimals, more when the exact value needs them (1.3125, 1.03125)."""
    text = f"{float(x):.6f}".rstrip("0")
    whole, _, frac = text.partition(".")
    return f"{whole}.{frac.ljust(digits, '0')}"


def route_flows(m):
    return {"S-U-T": float(m["equilibrium_outer_flow_each"]), "S-L-T": float(m["equilibrium_outer_flow_each"]),
            "S-U-L-T": float(m["equilibrium_shortcut_flow"])}


# Demonstration 1

def free_link_picture(demand=1):
    D = float(demand)
    m = lab(D)
    before = float(m["without_shortcut_total_time"])
    eq = float(m["equilibrium_social_time"])
    opt = float(m["optimal_social_time"])
    z = float(m["equilibrium_shortcut_flow"])
    x = float(m["equilibrium_outer_flow_each"])
    zo = float(m["optimal_shortcut_flow"])
    xo = (D - zo) / 2
    if abs(total_latency(x, z) - eq) > 1e-9 or abs(total_latency(xo, zo) - opt) > 1e-9:
        raise AssertionError("edge-by-edge total disagrees with the laboratory")
    rows = [("Before the\nlink", D / 2, 0.0), ("Link added,\nequilibrium", x, z), ("Social\noptimum", xo, zo)]

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    pos = np.arange(3)
    for i, (_, outer, mid) in enumerate(rows):
        left.bar(i, outer, width=0.6, color=PALETTE["navy"], edgecolor="white")
        left.bar(i, outer, bottom=outer, width=0.6, color="#9fb7c9", edgecolor=PALETTE["ink"], hatch="..", linewidth=0.6)
        if mid > 0:
            left.bar(i, mid, bottom=2 * outer, width=0.6, color="white", edgecolor=PALETTE["gold"], hatch="///", linewidth=1.2)
    handles = [Patch(facecolor=PALETTE["navy"], edgecolor="white", label="S-U-T"),
               Patch(facecolor="#9fb7c9", edgecolor=PALETTE["ink"], hatch="..", label="S-L-T"),
               Patch(facecolor="white", edgecolor=PALETTE["gold"], hatch="///", label="S-U-L-T (link)")]
    left.set_xticks(pos, [r[0] for r in rows])
    left.set_ylim(0, D * 1.75)
    left.legend(handles=handles, loc="upper left", fontsize=10.5, frameon=False, ncol=1)
    left.set_xlabel("Allocation")
    left.set_ylabel("Flow on each route (stacked, total = demand)")
    left.set_title("Who takes which route", fontsize=11.5)

    vals = [before, eq, opt]
    colors = [PALETTE["navy"], PALETTE["terracotta"], PALETTE["teal"]]
    hatches = ["", "xx", "//"]
    for i, (v, c, h) in enumerate(zip(vals, colors, hatches)):
        right.bar(i, v, width=0.6, color=c, hatch=h, edgecolor="white")
        right.text(i, v + max(vals) * 0.02, fmt(v, 3), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    right.set_xticks(pos, [r[0] for r in rows])
    right.set_ylim(0, max(vals) * 1.18)
    right.set_xlabel("Allocation")
    right.set_ylabel("Total latency TL (constructed units)")
    right.set_title("Equation (21.1) summed over the edges", fontsize=11.5)

    link_users = "none" if z <= TOL else ("all travellers" if abs(z - D) <= TOL else f"{fmt(z, 2)} of {fmt(D, 2)} units")
    ratio = eq / opt
    metrics = {
        "Total latency before the link": fmt(before, 3),
        "Total latency, link added (equilibrium)": fmt(eq, 3),
        "Total latency, social optimum": fmt(opt, 3),
        "Latency of each trip with the link": fmt(eq / D, 3),
        "Flow on the middle link": link_users,
        "Equilibrium over optimum": fmt(ratio, 3),
    }
    v = x + z
    edge_sum = (f"2 x {fmt(v, 2)} x {fmt(v, 2)} + 2 x {fmt(x, 2)} x 1.00 = {fmt(2 * v * v, 2)} + {fmt(2 * x, 2)} = {fmt(eq, 2)}")
    if abs(eq - before) <= TOL and z <= TOL:
        verdict = (f"The link is available but nobody uses it: the middle route costs 2 x {fmt(v, 2)} = {fmt(2 * v, 2)}, "
                   f"the same as an outer route ({fmt(v, 2)} + 1 = {fmt(v + 1, 2)}). Total latency is unchanged at {fmt(eq, 2)}, "
                   "so the link neither helps nor hurts at this demand.")
    elif eq > before + TOL:
        verdict = (f"Adding the link raised total latency from {fmt(before, 3)} to {fmt(eq, 3)}, a rise of {fmt(eq - before, 3)}, "
                   f"although no road got slower. The planner's best split ({fmt(opt, 3)}) is the old one and ignores the link.")
    else:
        verdict = (f"Here the link lowers total latency from {fmt(before, 3)} to {fmt(eq, 3)}, and the equilibrium already matches "
                   f"the optimum ({fmt(opt, 3)}). The paradox needs enough demand; it is not a property of every shortcut.")
    interpretation = (f"At equilibrium with the link, {link_users + ' take' if z > TOL else 'no one takes'} the middle link, so each congestible edge "
                      f"carries {fmt(v, 2)}. Summing flow x latency over the five edges (the middle link and its zero latency add nothing): "
                      f"{edge_sum}. Before the link the same demand split evenly: {fmt(D, 2)} x ({fmt(D, 2)} / 2 + 1) = {fmt(before, 3)}. {verdict}")
    return fig, metrics, interpretation


# Demonstration 2

GRID = np.round(np.arange(1, 51) * 0.05, 10)  # demands 0.05, 0.10, ..., 2.50


def bound_picture(overhead=0.0):
    o = float(overhead)
    ratios = np.array([float(lab(d, overhead=o)["price_of_anarchy"]) for d in GRID])
    top = float(ratios.max())
    flat = float(ratios.max() - ratios.min()) <= 1e-9
    k = int(np.argmax(ratios))
    peak_demand = float(GRID[k])
    mm = 1.0 - o  # demand at which the all-link equilibrium is just beaten by the no-link optimum

    fig, ax = new_figure(height=4.3)
    ax.axhspan(4 / 3, 1.5, facecolor="none", edgecolor=PALETTE["grey"], hatch="///", linewidth=0)
    ax.plot(GRID, ratios, color=PALETTE["teal"], linewidth=2)
    ax.axhline(4 / 3, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.6)
    label_point(ax, 0.05, 4 / 3, "bound 4/3 = 1.33", color=PALETTE["terracotta"], dx=2, dy=4, ha="left").set_bbox(WHITE)
    label_point(ax, 2.5, 1.46, "above 4/3: impossible when\nevery delay is linear", color=PALETTE["grey"], dx=-4, dy=0, ha="right", va="top").set_bbox(WHITE)
    if flat:
        label_point(ax, 1.25, top, "ratio is 1.00 at every demand", color=PALETTE["navy"], dx=0, dy=9, ha="center").set_bbox(WHITE)
    else:
        ax.plot([peak_demand], [top], "o", color=PALETTE["navy"], markersize=9)
        label_point(ax, peak_demand, top, f"peak {fmt(top, 2)} at demand {fmt(peak_demand, 2)}", color=PALETTE["navy"],
                    dx=10, dy=12, ha="left", va="bottom").set_bbox(WHITE)
    ax.set_xlim(0, 2.5)
    ax.set_ylim(0.95, 1.5)
    ax.set_xlabel("Demand (units of traffic from S to T)")
    ax.set_ylabel("Equilibrium total latency / optimal total latency")
    ax.set_title(f"Delay on the middle link: {fmt(o, 2)}", fontsize=11.5)

    if flat:
        peak_text = "every demand (flat)"
        calc = (f"With delay {fmt(o, 2)} on the link, a link trip costs 2v + {fmt(o, 2)} against v + 1 on an outer route, so nobody uses it (v is the flow on a congestible edge). "
                f"At demand 1 the equilibrium and the optimum coincide: 1 x (1 / 2 + 1) = 1.50 and 1.50 / 1.50 = 1.00")
        meaning = "The ratio never leaves 1.00: a link with a constant delay of 1, the delay of a fixed edge, changes nothing, so no gap opens."
        wc_eq = wc_opt = None
    else:
        peak_text = fmt(peak_demand, 2)
        eq_total = mm * (2 * mm + o)
        opt_total = mm * (mm / 2 + 1)
        if abs(peak_demand - mm) > 1e-9 or abs(top - eq_total / opt_total) > 1e-9:
            raise AssertionError("peak does not match the closed form")
        calc = (f"Peak at demand m = 1 - {fmt(o, 2)} = {fmt(mm, 2)}. Everyone on the link: each trip costs 2 x {fmt(mm, 2)} + {fmt(o, 2)} = "
                f"{fmt(2 * mm + o, 2)}, total {fmt(mm, 2)} x {fmt(2 * mm + o, 2)} = {exact(eq_total)}. Optimum, nobody on the link: each trip costs "
                f"{fmt(mm, 2)} / 2 + 1 = {exact(mm / 2 + 1)}, total {fmt(mm, 2)} x {exact(mm / 2 + 1)} = {exact(opt_total)}. "
                f"Ratio = {exact(eq_total)} / {exact(opt_total)} = {fmt(top, 3)}")
        if abs(top - 4 / 3) <= 1e-9:
            meaning = "This reaches 4/3 exactly: the bound is tight for the chapter's own network."
        else:
            meaning = f"This stays {fmt(4 / 3 - top, 3)} below 4/3: a slower link shrinks the damage, and the bound still holds."
    metrics = {
        "Largest ratio on the grid": fmt(top, 3),
        "Demand at the largest ratio": peak_text,
        "Bound from Equation (21.2)": fmt(4 / 3, 3),
        "Room below the bound": fmt(4 / 3 - top, 3),
    }
    interpretation = (f"{calc}. {meaning} The curve is computed on 50 demands from 0.05 to 2.50, and no point crosses 4/3. "
                      "The line is a ceiling for linear delays only; the chapter says the broader class has no finite ceiling.")
    return fig, metrics, interpretation


# Demonstration 3

RULES = {"none": "No charge", "marginal": "Marginal-cost charge", "toll": "Toll 0.5 on the link only"}


def mc_equilibrium(D):
    """Equilibrium flows when every congestible edge is charged 2 x flow (Equation 21.3 with a = 1, b = 0 or 1)."""
    z = min(D, max(0.0, 1.0 - D))
    return (D - z) / 2, z


def charged_picture(rule="none", demand=1):
    D = float(demand)
    if rule == "marginal":
        x, z = mc_equilibrium(D)
        lo = lab(D)
        if abs(z - float(lo["optimal_shortcut_flow"])) > 1e-9:
            raise AssertionError("marginal-cost equilibrium disagrees with the laboratory optimum")
    else:
        m = lab(D, toll=0.5 if rule == "toll" else 0.0)
        x, z = float(m["equilibrium_outer_flow_each"]), float(m["equilibrium_shortcut_flow"])
    v = x + z
    physical = 2 * v * v + 2 * x
    opt = float(lab(D)["optimal_social_time"])
    slope = 2.0 if rule == "marginal" else 1.0
    outer_cost = slope * v + 1.0
    middle_cost = 2 * slope * v + (0.5 if rule == "toll" else 0.0)
    costs = {"S-U-T": outer_cost, "S-L-T": outer_cost, "S-U-L-T": middle_cost}
    flows = {"S-U-T": x, "S-L-T": x, "S-U-L-T": z}
    used = [c for r, c in costs.items() if flows[r] > TOL]
    if max(used) - min(used) > 1e-9 or min(costs.values()) < min(used) - 1e-9:
        raise AssertionError("not an equilibrium")

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    q = np.linspace(0, 1.5, 61)
    left.plot(q, q, color=PALETTE["navy"], linewidth=2)
    left.plot(q, 2 * q, color=PALETTE["terracotta"], linewidth=2, linestyle="dashed", alpha=1.0 if rule == "marginal" else 0.35)
    left.plot(q, np.ones_like(q), color=PALETTE["grey"], linewidth=1.5, linestyle=":")
    label_point(left, 1.5, 1.5, "delay q", color=PALETTE["navy"], dx=-4, dy=6, ha="right").set_bbox(WHITE)
    label_point(left, 0.62, 1.24, "2q (with exported\ndelay added)" if rule == "marginal" else "2q (marginal-cost\ncharge only)",
                color=PALETTE["terracotta"] if rule == "marginal" else PALETTE["grey"], dx=-6, dy=2, ha="right").set_bbox(WHITE)
    label_point(left, 0.0, 1.0, "fixed edge: 1", color=PALETTE["grey"], dx=3, dy=4, ha="left").set_bbox(WHITE)
    left.plot([v], [v], "o", color=PALETTE["navy"], markersize=9)
    if rule == "marginal":
        left.plot([v], [2 * v], "s", color=PALETTE["terracotta"], markersize=9)
        left.plot([v, v], [v, 2 * v], color=PALETTE["gold"], linewidth=2.2)
        label_point(left, v, 1.5 * v, f"charge {fmt(v, 2)}", color=PALETTE["gold"], dx=6, dy=0, ha="left", va="center").set_bbox(WHITE)
    left.set_xlim(0, 1.5)
    left.set_ylim(0, 3.0)
    left.set_xlabel("Flow q on a congestible edge")
    left.set_ylabel("Delay or charged cost on that edge")
    left.set_title(f"Equation (21.3), a = 1 and b = 0; marker at flow {fmt(v, 2)}", fontsize=11.5)

    names = ["S-U-T", "S-L-T", "S-U-L-T"]
    hatch = {"S-U-T": "", "S-L-T": "..", "S-U-L-T": "///"}
    face = {"S-U-T": PALETTE["navy"], "S-L-T": "#9fb7c9", "S-U-L-T": "white"}
    edge = {"S-U-T": "white", "S-L-T": PALETTE["ink"], "S-U-L-T": PALETTE["gold"]}
    for i, n in enumerate(names):
        right.bar(i, flows[n], width=0.6, color=face[n], hatch=hatch[n], edgecolor=edge[n], linewidth=1.0)
        note = f"flow {fmt(flows[n], 2)}\ncost {fmt(costs[n], 2)}" if flows[n] > TOL else f"unused\ncost {fmt(costs[n], 2)}"
        right.text(i, flows[n] + D * 0.03, note, ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
    right.set_xticks(range(3), names)
    right.set_ylim(0, D * 1.6)
    right.set_xlabel("Route")
    right.set_ylabel("Flow on the route")
    right.set_title(f"Route costs the choosers see; physical total {fmt(physical, 3)}", fontsize=11.5)

    if rule == "marginal":
        step = (f"Corrected cost of an outer route = 2 x {fmt(v, 2)} + 1 = {fmt(outer_cost, 2)}; of the middle route = "
                f"2 x {fmt(v, 2)} + 2 x {fmt(v, 2)} = {fmt(middle_cost, 2)}")
    elif rule == "toll":
        step = (f"Outer route = {fmt(v, 2)} + 1 = {fmt(outer_cost, 2)}; middle route = {fmt(v, 2)} + {fmt(v, 2)} + 0.50 toll = {fmt(middle_cost, 2)}")
    else:
        step = f"Outer route = {fmt(v, 2)} + 1 = {fmt(outer_cost, 2)}; middle route = {fmt(v, 2)} + {fmt(v, 2)} = {fmt(middle_cost, 2)}"
    gap = physical - opt
    if abs(gap) <= TOL:
        after = f"Physical total latency {fmt(physical, 3)} equals the social optimum {fmt(opt, 3)}."
    else:
        after = f"Physical total latency {fmt(physical, 3)} is {fmt(gap, 3)} above the social optimum {fmt(opt, 3)}."
    if rule == "marginal":
        tail = ("The charge makes each chooser face the delay it adds for others, so the equilibrium lands on the optimum. "
                "Charge payments are transfers and are left out of physical latency.")
    elif rule == "toll":
        if abs(gap) <= TOL:
            tail = ("A toll on the link alone reaches the optimum here although it charges only one edge, "
                    "unlike the chapter's rule, which charges every congestible edge.")
        else:
            tail = ("A toll on the link alone does not reach the optimum here, and it charges only one edge, "
                    "unlike the chapter's rule, which charges every congestible edge.")
    else:
        tail = "Nothing prices the exported delay, so each trip takes the cheaper-looking route."
    metrics = {
        "Rule": RULES[rule],
        "Outer route cost seen": fmt(outer_cost, 2),
        "Middle route cost seen": fmt(middle_cost, 2),
        "Flow on the middle route": fmt(z, 2),
        "Physical total latency": fmt(physical, 3),
        "Social optimum": fmt(opt, 3),
    }
    interpretation = (f"At demand {fmt(D, 2)} the equilibrium puts {fmt(x, 2)} on each outer route and {fmt(z, 2)} on the middle, so each "
                      f"congestible edge carries {fmt(v, 2)}. {step}. Physical total = 2 x {fmt(v, 2)} x {fmt(v, 2)} + 2 x {fmt(x, 2)} x 1.00 = "
                      f"{fmt(physical, 3)}. {after} {tail}")
    return fig, metrics, interpretation


# Demonstration 4

def opt_cost_by_hand(d):
    """Optimal total latency at demand d, as a written sum, for the regimes this demonstration reaches (d >= 0.5)."""
    if d >= 1.0 - TOL:
        return d * (d / 2 + 1), f"{fmt(d, 3)} x ({fmt(d, 3)} / 2 + 1) = {fmt(d * (d / 2 + 1), 3)}"
    return 2 * d - 0.5, f"2 x {fmt(d, 3)} - 0.5 = {fmt(2 * d - 0.5, 3)}"


def capacity_picture(rate=1, extra=0.5):
    r, g = float(rate), float(extra)
    eq = float(lab(r)["equilibrium_social_time"])
    d = (1 + g) * r
    opt = float(lab(d)["optimal_social_time"])
    factor = 1 / g
    ratio = eq / opt
    hand_opt, hand_text = opt_cost_by_hand(d)
    if abs(hand_opt - opt) > 1e-9 or abs(2 * r * r - eq) > 1e-9:
        raise AssertionError("hand sums disagree with the laboratory")

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    dd = np.linspace(0.05, 2.5, 99)
    curve = np.array([float(lab(x)["optimal_social_time"]) for x in dd])
    left.plot(dd, curve, color=PALETTE["teal"], linewidth=2)
    left.axhline(eq, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.6)
    left.vlines(d, 0, opt, color=PALETTE["grey"], linestyle=":", linewidth=1.4)
    left.plot([d], [opt], "o", color=PALETTE["navy"], markersize=9)
    left.plot([r], [eq], "s", color=PALETTE["terracotta"], markersize=8)
    cx = 2.0
    label_point(left, cx, float(np.interp(cx, dd, curve)), "optimal cost curve", color=PALETTE["teal"], dx=-8, dy=8, ha="right").set_bbox(WHITE)
    left.text(0.03, 0.97, f"square: equilibrium at r = {fmt(r, 2)}, cost {fmt(eq, 3)}\ncircle: optimum at {fmt(d, 3)}, cost {fmt(opt, 3)}",
              transform=left.transAxes, ha="left", va="top", fontsize=10.5, color=PALETTE["ink"])
    left.set_xlim(0, 2.5)
    left.set_ylim(0, 7.2)
    left.set_xlabel("Traffic rate the optimal benchmark must carry")
    left.set_ylabel("Total latency")
    left.set_title("Equilibrium at r against optimum at (1 + extra) r", fontsize=11.5)

    gs = np.linspace(0.25, 1.0, 16)
    actual = np.array([float(lab(r)["equilibrium_social_time"]) / float(lab((1 + x) * r)["optimal_social_time"]) for x in gs])
    right.plot(gs, 1 / gs, color=PALETTE["terracotta"], linewidth=2)
    right.plot(gs, actual, color=PALETTE["navy"], linewidth=2, linestyle="dashed")
    right.plot([g], [factor], "s", color=PALETTE["terracotta"], markersize=9)
    right.plot([g], [ratio], "o", color=PALETTE["navy"], markersize=9)
    label_point(right, 0.25, 4.0, "guaranteed factor 1/extra", color=PALETTE["terracotta"], dx=24, dy=-6, ha="left", va="top").set_bbox(WHITE)
    label_point(right, 0.26, 1.35, "this network:\nequilibrium / optimum", color=PALETTE["navy"], dx=0, dy=0, ha="left", va="center")
    right.set_xlim(0.2, 1.05)
    right.set_ylim(0, 4.4)
    right.set_xlabel("Extra-traffic fraction (extra)")
    right.set_ylabel("Cost factor")
    right.set_title("Guarantee against this network", fontsize=11.5)

    metrics = {
        "Equilibrium cost at r": fmt(eq, 3),
        "Optimal cost at (1 + extra) r": fmt(opt, 3),
        "Equilibrium over optimum": fmt(ratio, 3),
        "Guaranteed factor 1/extra": fmt(factor, 2),
        "Within the guarantee": "yes" if eq <= factor * opt + 1e-9 else "no",
    }
    interpretation = (f"Equilibrium at r = {fmt(r, 2)}: 2 x {fmt(r, 2)} x {fmt(r, 2)} = {fmt(eq, 3)} (all traffic takes the link, each congestible "
                      f"edge carries {fmt(r, 2)}). The optimum must carry (1 + {fmt(g, 2)}) x {fmt(r, 2)} = {fmt(d, 3)}: {hand_text}. "
                      f"Ratio = {fmt(eq, 3)} / {fmt(opt, 3)} = {fmt(ratio, 3)}, against the guaranteed factor 1 / {fmt(g, 2)} = {fmt(factor, 2)}. "
                      "This network sits far under the guarantee, which is a worst case over all networks, not a forecast. "
                      "The benchmark is burdened with extra traffic, not given extra capacity.")
    return fig, metrics, interpretation


CHAPTER = {
    "number": 21,
    "title": "Markets, Teams, and Institutions",
    "subtitle": "Each participant can make a sensible local choice while the whole workflow gets slower; a rule decides whether local incentives add up to the task.",
    "summary": (
        "These four demonstrations use the chapter's five-edge traffic network: one unit of traffic from S to T, two routes that each mix a "
        "congestible edge with a fixed one, and a free directed link in the middle. They show what the free link does, how far the damage can go "
        "for linear delays, how a charge on exported delay repairs it, and what the capacity comparison does and does not promise."
    ),
    "demos": [
        {
            "id": "C21-D01",
            "title": "A free link: better, worse or unchanged",
            "question": "When a zero-latency link is added, does the stable pattern of choices get better or worse, and how does that depend on demand?",
            "equations": [EQ_TL],
            "symbols": (
                "S is the source, T the target, U the upper junction and L the lower junction. The three routes are S-U-T, S-L-T and S-U-L-T, which crosses the directed middle link from U to L. q is a flow (the amount of traffic) and q_e the traffic on edge e. The latency function l_e(q_e) is the delay a traveller meets on "
                "edge e. TL(q) is total latency: the sum over edges of traffic times delay. Here the two congestible edges (S-U and L-T) have "
                "delay equal to their flow, the two fixed edges (U-T and S-L) have delay 1, and the middle link has delay 0. Demand is the total "
                "traffic from S to T. The equilibrium is the pattern in which no traveller can lower their own delay by switching routes."
            ),
            "prediction": "At the chapter's demand of 1, will total latency with the link be higher, lower or the same as before? Then try demand 2.",
            "explanation": (
                "With the link, each traveller who enters at S-U and leaves by L-T meets only the two congestible edges, so the middle route is "
                "never worse than an outer route as long as demand is at most the chapter's 1. At demand 1 everyone takes it, each trip costs 1 + 1 = 2, and TL rises from 1.5 to 2, while the "
                "best split is still the old one. At low demand the link is a real gain, and at high demand it is unused because the outer routes "
                "have already become as slow as the middle."
            ),
            "application": (
                "Before adding a shared shortcut such as a common reviewer, a shared tool or a fast lane, ask what everyone will do once it exists, "
                "not whether one case could finish faster against yesterday's traffic."
            ),
            "assumptions": (
                "One unit-scale network with linear congestible edges, many small travellers who each pick the cheapest route, and a total-delay "
                "objective. It does not say that any real shortcut, tool or team behaves this way. When demand is large enough to make the "
                "outer routes slow, the paradox disappears."
            ),
            "check": "At demand 1.5, what does each trip cost with the link, and how does that compare with the cost of an outer route?",
            "answer": (
                "Equilibrium puts 0.5 on each outer route and 0.5 on the middle, so each congestible edge carries 1.0. An outer route costs "
                "1.0 + 1 = 2.0 and the middle costs 1.0 + 1.0 = 2.0, a tie. Total latency is 2 x 1.0 x 1.0 + 2 x 0.5 x 1 = 3.0, which is 2.0 per trip."
            ),
            "provenance": "Constructed example: the chapter's one-unit network with demand varied; equilibrium and optimum are computed with the laboratory's congestion function.",
            "source_section": "A free connection changes what best means",
            "source_anchor": "a-free-connection-changes-what-best-means",
            "controls": [
                {"key": "demand", "label": "Demand (units of traffic from S to T)", "values": [0.5, 1, 1.5, 2], "default": 1},
            ],
            "function": "free_link_picture",
        },
        {
            "id": "C21-D02",
            "title": "How bad can it get with linear delays",
            "question": "Across every demand, how large can the ratio of equilibrium delay to optimal delay be when every delay is linear?",
            "equations": [EQ_BOUND],
            "symbols": (
                "S is the source, T the target, U the upper junction and L the lower junction. The three routes are S-U-T, S-L-T and S-U-L-T, which crosses the directed middle link from U to L. TL(q) is total latency. q^NE is the equilibrium flow and q* the flow with the smallest total latency, so the ratio compares "
                "self-directed routing with the best feasible routing. Linear means each edge delay is a times its flow plus b, with a and b "
                "not negative. The control sets a constant delay on the middle link (the b of that edge); 0 is the chapter's free link."
            ),
            "prediction": "Make the link slower (delay 0.5). Does the highest ratio rise, fall or stay at 4/3?",
            "explanation": (
                "Each curve is the lab's equilibrium total divided by its optimal total at every demand. The ratio is 1 when the link is unused or "
                "already optimal. It peaks where demand is just large enough that the optimum shuts the link while the equilibrium still crowds "
                "onto it. With a free link the peak reaches 4/3 exactly, and no linear delay example can go higher."
            ),
            "application": (
                "When someone quotes a worst-case ratio for a queue or workflow, first check that its delays really are linear over the range "
                "of load the team will see. A ratio proved for one class of delay says nothing outside that class."
            ),
            "assumptions": (
                "The same one-unit network with the middle link given a constant delay. The bound applies because every delay stays linear. "
                "The chapter notes that if delays are only continuous and nondecreasing, the ratio can be unbounded; thresholds, retry storms "
                "and sudden queue growth may not have the linear form, in which case the 4/3 figure is not guaranteed."
            ),
            "check": "With a delay of 0.25 on the middle link, what is the highest ratio?",
            "answer": (
                "The peak is at demand m = 1 - 0.25 = 0.75. Equilibrium: 0.75 x (2 x 0.75 + 0.25) = 0.75 x 1.75 = 1.3125. Optimum: "
                "0.75 x (0.75 / 2 + 1) = 0.75 x 1.375 = 1.03125. The ratio is 1.3125 / 1.03125 = 1.273, below 4/3."
            ),
            "provenance": "Constructed example: the chapter's network with a middle-link delay defined for this reader; ratios are computed with the laboratory's congestion function.",
            "source_section": "What linear bound says, and what it does not",
            "source_anchor": "what-linear-bound-says-and-what-it-does-not",
            "controls": [
                {"key": "overhead", "label": "Constant delay on the middle link", "values": [0, 0.25, 0.5, 1], "default": 0,
                 "value_labels": ["0 (free link)", "0.25", "0.5", "1 (the same as a fixed edge)"]},
            ],
            "function": "bound_picture",
        },
        {
            "id": "C21-D03",
            "title": "Charging for the delay you export",
            "question": "If every congestible edge charges its own delay plus the delay the traveller adds for others, where does the equilibrium land?",
            "equations": [EQ_MC],
            "symbols": (
                "S is the source, T the target, U the upper junction and L the lower junction. The three routes are S-U-T, S-L-T and S-U-L-T, which crosses the directed middle link from U to L. l_e(q_e) is the delay on edge e at flow q_e. The marginal-cost latency adds q_e times the slope of l_e, which is the extra delay "
                "one more unit of flow imposes on those already there. For a delay a x q + b the charged cost is 2 x a x q + b: the congestion term "
                "doubles and the fixed term does not. Here a = 1 and b = 0 on a congestible edge, and a = 0 and b = 1 on a fixed edge."
            ),
            "prediction": "At demand 1 with the marginal-cost charge, how much traffic uses the middle link, and what is the physical total latency?",
            "explanation": (
                "Travellers still choose the cheapest route, but now by the charged cost. The charge turns the old comparison 1 + v against 2v "
                "into 2v + 1 against 4v, which moves traffic back toward the outer routes. The physical delay then equals the best possible total. "
                "The third rule, a toll only on the link, is the notebook's variant: a different rule, although at these two demands it gives "
                "the same flows and the same total as the marginal-cost charge."
            ),
            "application": (
                "In a shared workflow, the charge might be a rising budget for a busy shared tool, a queue-aware scheduler or a concurrency limit. "
                "The common property is that a local choice receives a signal about the shared resource it uses."
            ),
            "assumptions": (
                "Linear delays, a total-delay objective, and a charge that is paid but not counted as physical delay. A real signal can be late, "
                "noisy, gameable or attached to the wrong boundary, and the objective may omit fairness or safety. The chapter treats the "
                "construction as proof that one gap can be closed under stated conditions, not as a general policy answer."
            ),
            "check": "At demand 0.75 with the marginal-cost charge, what flow goes on the middle link?",
            "answer": (
                "Both route types are used, so their charged costs match: 2v + 1 = 4v gives v = 0.5. The middle flow is 1 - 0.75 = 0.25, "
                "each outer route carries 0.25, and the physical total is 2 x 0.5 x 0.5 + 2 x 0.25 = 1.0."
            ),
            "provenance": "Constructed example: the chapter's network and its marginal-cost charge; the no-charge and toll cases use the laboratory's congestion function, and the marginal-cost flows are derived here and checked against the laboratory's optimum.",
            "source_section": "Prices that make group target locally legible",
            "source_anchor": "prices-that-make-group-target-locally-legible",
            "controls": [
                {"key": "rule", "label": "Charging rule", "values": ["none", "marginal", "toll"], "default": "marginal",
                 "value_labels": ["No charge", "Marginal-cost charge", "Toll of 0.5 on the middle link only"]},
                {"key": "demand", "label": "Demand (units of traffic from S to T)", "values": [1, 0.75], "default": 1},
            ],
            "function": "charged_picture",
        },
        {
            "id": "C21-D04",
            "title": "Capacity is a comparison, not a cure",
            "question": "How does the cost of selfish routing at rate r compare with the best routing that must carry extra traffic?",
            "equations": [EQ_EXTRA, EQ_FACTOR],
            "symbols": (
                "r is the traffic rate and gamma_cap (written extra here) is a positive fraction. The first expression, (1 + gamma_cap) r, is the traffic the "
                "benchmark carries: an optimal flow that carries (1 + extra) times r. The second, 1 / gamma_cap, is the guaranteed factor. "
                "The theorem combines them: equilibrium cost at r is at most 1 / extra times the benchmark's cost at (1 + extra) r. The cost is total "
                "latency, as in Equation (21.1). Nobody adds a road: the network stays the same and only the benchmark's burden changes."
            ),
            "prediction": "With extra = 1 (the benchmark carries twice the traffic), is the equilibrium cost at r = 1 below or above the optimal cost at rate 2?",
            "explanation": (
                "Left panel: the optimal cost grows with the traffic it must carry, so asking the benchmark to carry more makes the comparison easier "
                "for the equilibrium. Right panel: the guaranteed factor 1 / extra falls from 4 to 1 as extra grows from 0.25 to 1, while this "
                "particular network stays near or under 1. The theorem is a worst-case promise and does not tell you which server to buy."
            ),
            "application": (
                "In a staffing meeting, separate delay caused by too little throughput from delay caused by a rule that steers work into one stage. "
                "More capacity can lower delay at a given flow, but it can also make a stage attractive to more work and shift the equilibrium again."
            ),
            "assumptions": (
                "The chapter's linear network and the two demands r = 0.5 and 1. The guarantee is a bound over all networks in its class, and "
                "this network does not come close to it, so the picture shows the comparison, not tightness. It says nothing about adding capacity "
                "to a real system, where demand responds."
            ),
            "check": "With r = 1 and extra = 0.5, what must the benchmark carry, and what is its cost?",
            "answer": (
                "It carries (1 + 0.5) x 1 = 1.5. At 1.5 the optimum uses only the outer routes, 0.75 each: 1.5 x (1.5 / 2 + 1) = 1.5 x 1.75 = 2.625. "
                "The equilibrium cost 2.0 is below it, and 1 / 0.5 = 2 times 2.625 is a much looser ceiling."
            ),
            "provenance": "Constructed example: the chapter's network at rates defined for this reader; all costs are computed with the laboratory's congestion function.",
            "source_section": "Capacity is a comparison, not a cure",
            "source_anchor": "capacity-is-a-comparison-not-a-cure",
            "controls": [
                {"key": "rate", "label": "Traffic rate r", "values": [0.5, 1], "default": 1},
                {"key": "extra", "label": "Extra-traffic fraction", "values": [0.25, 0.5, 1], "default": 0.5},
            ],
            "function": "capacity_picture",
        },
    ],
}

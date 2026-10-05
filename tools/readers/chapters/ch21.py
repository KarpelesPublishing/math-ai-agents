"""Chapter 21 reader: Markets, Teams, and Institutions.

Four demonstrations on the chapter's Braess network (one unit of traffic by
default, two outer routes, a directed zero-latency middle link) and on
Equations (21.1) to (21.3). Demonstrations 1, 2 and 4 call the laboratory's
own congestion function (math_ai_agents.chapters.ch21.evaluate), so the
reader, the notebook and the chapter skill agree. Demonstration 1 shows why the
stable pattern and the best pattern differ (route costs against the flow on the
middle link, and total latency against the same flow), with and without the
link. Demonstration 3 adds the chapter's marginal-cost charge (a charge on every
congestible edge), which the laboratory does not compute; it is derived directly
and checked against the laboratory's optimum, and it is set beside no charge and
tolls on the link alone (computed by the laboratory). Every number is a
constructed teaching value.

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


# Closed forms for the network (capacity 1, outer delay 1, link delay o); each is checked against the laboratory below.

def eq_link_flow(D, o=0.0):
    return min(D, max(0.0, 2 * (1.0 - o) - D))


def opt_link_flow(D, o=0.0):
    return min(D, max(0.0, (1.0 - o) - D))


def tl_at(D, z):
    """Total latency when z is on the middle link and (D - z) / 2 on each outer route (overhead 0)."""
    v = (D + z) / 2
    return 2 * v * v + (D - z)


# Demonstration 1

def free_link_picture(demand=1, network="link"):
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
    if abs(eq_link_flow(D) - z) > 1e-9 or abs(opt_link_flow(D) - zo) > 1e-9 or abs(tl_at(D, z) - eq) > 1e-9 or abs(tl_at(D, zo) - opt) > 1e-9:
        raise AssertionError("closed forms disagree with the laboratory")

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    if network == "link":
        zs = np.linspace(0, D, 101)
        c_out = (D + zs) / 2 + 1
        c_mid = D + zs
        (lo,) = left.plot(zs, c_out, color=PALETTE["navy"], linewidth=2)
        (lm,) = left.plot(zs, c_mid, color=PALETTE["terracotta"], linewidth=2, linestyle="dashed")
        left.axvline(z, color=PALETTE["grey"], linestyle=":", linewidth=1.5)
        left.plot([z], [(D + z) / 2 + 1], "o", color=PALETTE["navy"], markersize=8)
        left.plot([z], [D + z], "s", color=PALETTE["terracotta"], markersize=8, markerfacecolor="white", markeredgewidth=2)
        left.set_xlim(-0.03 * D, D * 1.03)
        left.set_ylim(0, max(c_out.max(), c_mid.max()) * 1.18)
        left.legend([lo, lm], ["outer route: v + 1", "middle route: 2 v"], loc="lower right", fontsize=10.5, frameon=False)
        label_point(left, z, left.get_ylim()[1], f"equilibrium z = {fmt(z, 2)}", color=PALETTE["grey"], dx=-4 if z > D / 2 else 4, dy=-4,
                    ha="right" if z > D / 2 else "left", va="top").set_bbox(WHITE)
        left.set_xlabel("Flow z on the middle route (v = (D + z) / 2 on each congestible edge)")
        left.set_ylabel("Route cost a traveller sees")
        left.set_title("Who gains by switching, at each z", fontsize=11.5)

        tl = np.array([tl_at(D, t) for t in zs])
        right.plot(zs, tl, color=PALETTE["teal"], linewidth=2)
        right.set_xlim(-0.03 * D, D * 1.03)
        right.set_ylim(tl.min() * 0.8, tl.max() * 1.18)
        same = abs(z - zo) <= TOL
        if same:
            right.plot([z], [eq], "o", color=PALETTE["teal"], markersize=10)
            label_point(right, z, eq, f"equilibrium = optimum, {fmt(eq, 3)}", color=PALETTE["teal"], dx=0, dy=-14,
                        ha="right" if z > D / 2 else "left", va="top").set_bbox(WHITE)
        else:
            right.plot([zo], [opt], "o", color=PALETTE["teal"], markersize=10)
            right.plot([z], [eq], "s", color=PALETTE["terracotta"], markersize=9)
            label_point(right, zo, opt, f"optimum {fmt(opt, 3)}", color=PALETTE["teal"], dx=6 if zo <= z else -6, dy=-12,
                        ha="left" if zo <= z else "right", va="top").set_bbox(WHITE)
            label_point(right, z, eq, f"equilibrium {fmt(eq, 3)}", color=PALETTE["terracotta"], dx=-6 if z >= zo else 6, dy=12,
                        ha="right" if z >= zo else "left", va="bottom").set_bbox(WHITE)
        right.set_xlabel("Flow z on the middle route")
        right.set_ylabel("Total latency TL (constructed units)")
        right.set_title("Equation (21.1) at each z", fontsize=11.5)
    else:
        qs = np.linspace(0, D, 101)
        (lu,) = left.plot(qs, 1 + qs, color=PALETTE["navy"], linewidth=2)
        (ll,) = left.plot(qs, 1 + D - qs, color=PALETTE["terracotta"], linewidth=2, linestyle="dashed")
        left.axvline(D / 2, color=PALETTE["grey"], linestyle=":", linewidth=1.5)
        left.plot([D / 2], [1 + D / 2], "o", color=PALETTE["navy"], markersize=8)
        left.set_xlim(-0.03 * D, D * 1.03)
        left.set_ylim(0, 1 + D + 0.4)
        left.legend([lu, ll], ["upper route: 1 + q", "lower route: 1 + D - q"], loc="lower center", fontsize=10.5, frameon=False)
        label_point(left, D / 2, left.get_ylim()[1], f"equal at q = {fmt(D / 2, 2)}", color=PALETTE["grey"], dx=4, dy=-4, ha="left", va="top").set_bbox(WHITE)
        left.set_xlabel("Flow q on the upper route (D - q on the lower)")
        left.set_ylabel("Route cost a traveller sees")
        left.set_title("Without the link: the routes must match", fontsize=11.5)

        tl = np.array([q * (1 + q) + (D - q) * (1 + D - q) for q in qs])
        if abs(tl.min() - before) > 1e-9:
            raise AssertionError("brute-force minimum disagrees with the closed form")
        right.plot(qs, tl, color=PALETTE["teal"], linewidth=2)
        right.plot([D / 2], [before], "o", color=PALETTE["teal"], markersize=10)
        right.set_xlim(-0.03 * D, D * 1.03)
        right.set_ylim(tl.min() * 0.8, tl.max() * 1.18)
        label_point(right, D / 2, before, f"equilibrium = optimum, {fmt(before, 3)}", color=PALETTE["teal"], dx=0, dy=-14, ha="center", va="top").set_bbox(WHITE)
        right.set_xlabel("Flow q on the upper route")
        right.set_ylabel("Total latency TL (constructed units)")
        right.set_title("Equation (21.1) at each q", fontsize=11.5)

    v = x + z
    link_users = "none" if z <= TOL else ("all travellers" if abs(z - D) <= TOL else f"{fmt(z, 2)} of {fmt(D, 2)} units")
    ratio = eq / opt
    if network == "nolink":
        metrics = {
            "Total latency, link removed (equilibrium)": fmt(before, 3),
            "Split on the upper route": f"{fmt(D / 2, 2)} of {fmt(D, 2)} units",
            "Latency of each trip": fmt(1 + D / 2, 3),
            "Total latency, social optimum": fmt(before, 3),
            "Equilibrium over optimum": fmt(1.0, 3),
        }
        interpretation = (f"Without the link the two routes cost 1 + q and 1 + {fmt(D, 2)} - q, equal only at q = {fmt(D, 2)} / 2 = {fmt(D / 2, 2)}, so each trip costs 1 + {fmt(D / 2, 2)} = {fmt(1 + D / 2, 3)}. "
                          f"Total latency = {fmt(D, 2)} x ({fmt(D, 2)} / 2 + 1) = {fmt(before, 3)}, and the same split minimizes it, so private choice and the planner agree (ratio 1.000). "
                          "Both routes are used because putting everything on one gives that route cost 1 + D against 1 for the unused one.")
        steps = [
            f"Without the link the routes cost 1 + q (upper) and 1 + {fmt(D, 2)} - q (lower).",
            f"Equal costs need q = {fmt(D, 2)} / 2 = {fmt(D / 2, 2)}.",
            f"Each trip then costs 1 + {fmt(D / 2, 2)} = {fmt(1 + D / 2, 3)}.",
            f"Total latency = {fmt(D, 2)} x ({fmt(D, 2)} / 2 + 1) = {fmt(before, 3)}.",
            "The same split minimizes total latency, so equilibrium over optimum = 1.000.",
        ]
        alt = (f"Left, two route-cost lines, upper rising and lower falling, crossing at q = {fmt(D / 2, 2)}. "
               f"Right, total latency against q with its minimum {fmt(before, 3)} at the same point.")
        return fig, metrics, interpretation, {"alt": alt, "steps": steps}

    metrics = {
        "Total latency before the link": fmt(before, 3),
        "Total latency, link added (equilibrium)": fmt(eq, 3),
        "Total latency, social optimum": fmt(opt, 3),
        "Latency of each trip with the link": fmt(eq / D, 3),
        "Flow on the middle link": link_users,
        "Equilibrium over optimum": fmt(ratio, 3),
    }
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
    switch = "so travellers switch to the link" if D / 2 + 1 > D + TOL else ("so there is a tie" if abs(D / 2 + 1 - D) <= TOL else "so nobody gains by switching")
    interpretation = (f"At z = 0 an outer route costs {fmt(D, 2)} / 2 + 1 = {fmt(D / 2 + 1, 2)} and the middle route costs {fmt(D, 2)} + 0 = {fmt(D, 2)}, {switch}. "
                      f"At equilibrium with the link, {link_users + ' take' if z > TOL else 'no one takes'} the middle link, so each congestible edge "
                      f"carries {fmt(v, 2)}. Summing flow x latency over the five edges (the middle link and its zero latency add nothing): "
                      f"{edge_sum}. Before the link the same demand split evenly: {fmt(D, 2)} x ({fmt(D, 2)} / 2 + 1) = {fmt(before, 3)}. {verdict}")
    steps = [
        f"Demand D = {fmt(D, 2)}. With z on the middle route, each congestible edge carries v = (D + z) / 2.",
        f"At z = 0: outer route {fmt(D, 2)} / 2 + 1 = {fmt(D / 2 + 1, 2)}; middle route {fmt(D, 2)} + 0 = {fmt(D, 2)}.",
        f"Equilibrium z = {fmt(z, 2)}, so v = ({fmt(D, 2)} + {fmt(z, 2)}) / 2 = {fmt(v, 2)}.",
        f"Seen costs at equilibrium: outer {fmt(v, 2)} + 1 = {fmt(v + 1, 2)}, middle 2 x {fmt(v, 2)} = {fmt(2 * v, 2)}.",
        f"Total latency at equilibrium = {edge_sum}.",
        f"Social optimum: z = {fmt(zo, 2)}, total latency {fmt(opt, 3)}.",
        f"Ratio = {fmt(eq, 3)} / {fmt(opt, 3)} = {fmt(ratio, 3)}.",
    ]
    alt = (f"Left, route costs against the flow z on the middle link: the outer route rises slowly and the middle route rises faster, with the equilibrium at z = {fmt(z, 2)}. "
           f"Right, total latency against z, with the optimum {fmt(opt, 3)} at z = {fmt(zo, 2)} and the equilibrium {fmt(eq, 3)} at z = {fmt(z, 2)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


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
    z_eq = np.array([float(lab(d, overhead=o)["equilibrium_shortcut_flow"]) for d in GRID])
    z_opt = np.array([float(lab(d, overhead=o)["optimal_shortcut_flow"]) for d in GRID])
    if (np.abs(z_eq - np.array([eq_link_flow(d, o) for d in GRID])).max() > 1e-9
            or np.abs(z_opt - np.array([opt_link_flow(d, o) for d in GRID])).max() > 1e-9):
        raise AssertionError("closed-form link flows disagree with the laboratory")

    fig, (left, ax2) = new_figure(ncols=2, height=4.3)
    ax = left
    ax.axhspan(4 / 3, 1.5, facecolor="none", edgecolor=PALETTE["grey"], hatch="///", linewidth=0)
    ax.plot(GRID, ratios, color=PALETTE["teal"], linewidth=2)
    ax.axhline(4 / 3, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.6)
    label_point(ax, 0.05, 4 / 3, "bound 4/3", color=PALETTE["terracotta"], dx=2, dy=-4, ha="left", va="top").set_bbox(WHITE)
    label_point(ax, 2.5, 1.48, "above 4/3:\nnot possible", color=PALETTE["grey"], dx=-4, dy=0, ha="right", va="top").set_bbox(WHITE)
    if flat:
        label_point(ax, 1.25, top, "ratio is 1.00 at every demand", color=PALETTE["navy"], dx=0, dy=9, ha="center").set_bbox(WHITE)
    else:
        ax.plot([peak_demand], [top], "o", color=PALETTE["navy"], markersize=9)
        label_point(ax, peak_demand, top, f"peak {fmt(top, 2)}\nat demand {fmt(peak_demand, 2)}", color=PALETTE["navy"],
                    dx=10, dy=-14, ha="left", va="top").set_bbox(WHITE)
    ax.set_xlim(0, 2.5)
    ax.set_ylim(0.95, 1.5)
    ax.set_xlabel("Demand (units of traffic from S to T)")
    ax.set_ylabel("Equilibrium total latency / optimal total latency")
    ax.set_title(f"Delay on the middle link: {fmt(o, 2)}", fontsize=11.5)

    (le,) = ax2.plot(GRID, z_eq, color=PALETTE["terracotta"], linewidth=2)
    (lo,) = ax2.plot(GRID, z_opt, color=PALETTE["navy"], linewidth=2, linestyle="dashed")
    ax2.fill_between(GRID, z_opt, z_eq, where=z_eq > z_opt + 1e-12, facecolor="none", edgecolor=PALETTE["gold"], hatch="///", linewidth=0)
    if not flat:
        ax2.axvline(mm, color=PALETTE["grey"], linestyle=":", linewidth=1.4)
    ax2.set_xlim(0, 2.5)
    ax2.set_ylim(-0.08, 1.15)
    ax2.legend([le, lo], ["equilibrium", "optimum"], loc="upper right", fontsize=10.5, frameon=False)
    ax2.set_xlabel("Demand (units of traffic from S to T)")
    ax2.set_ylabel("Flow on the middle link")
    ax2.set_title("Hatched: more link use than the optimum", fontsize=11.0)

    if flat:
        peak_text = "every demand (flat)"
        calc = (f"With delay {fmt(o, 2)} on the link, a link trip costs 2v + {fmt(o, 2)} against v + 1 on an outer route, so nobody uses it (v is the flow on a congestible edge). "
                f"At demand 1 the equilibrium and the optimum coincide: 1 x (1 / 2 + 1) = 1.50 and 1.50 / 1.50 = 1.00")
        meaning = "The ratio never leaves 1.00: a link with a constant delay of 1, the delay of a fixed edge, changes nothing, so no gap opens."
        steps = [
            f"A link trip costs 2v + {fmt(o, 2)} against v + 1 on an outer route, where v is the flow on a congestible edge.",
            f"At demand 1 with nobody on the link, v = 0.50, so a link trip would cost 2 x 0.50 + {fmt(o, 2)} = {fmt(1 + o, 2)} "
            f"against 0.50 + 1 = 1.50 on an outer route; 2v + {fmt(o, 2)} is never below v + 1.",
            "So the equilibrium puts no flow on the link at any demand, and neither does the optimum.",
            "At demand 1 both give 1 x (1 / 2 + 1) = 1.50, so the ratio is 1.50 / 1.50 = 1.00.",
        ]
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
        steps = [
            f"A link trip costs 2v + {fmt(o, 2)} against v + 1 on an outer route, where v is the flow on a congestible edge.",
            f"The ratio peaks where the optimum has just shut the link but the equilibrium still crowds onto it: m = 1 - {fmt(o, 2)} = {fmt(mm, 2)}.",
            f"Equilibrium total at m: {fmt(mm, 2)} x (2 x {fmt(mm, 2)} + {fmt(o, 2)}) = {exact(eq_total)}.",
            f"Optimal total at m: {fmt(mm, 2)} x ({fmt(mm, 2)} / 2 + 1) = {exact(opt_total)}.",
            f"Ratio = {exact(eq_total)} / {exact(opt_total)} = {fmt(top, 3)}.",
            f"Room below the bound = 4 / 3 - {fmt(top, 4)} = {fmt(4 / 3 - top, 3)} (the ratio carried to four decimals).",
        ]
    metrics = {
        "Largest ratio on the grid": fmt(top, 3),
        "Demand at the largest ratio": peak_text,
        "Bound from Equation (21.2)": fmt(4 / 3, 3),
        "Room below the bound": fmt(4 / 3 - top, 3),
    }
    interpretation = (f"{calc}. {meaning} The curve is computed on 50 demands from 0.05 to 2.50, and no point crosses 4/3. "
                      "The line is a ceiling for linear delays only; the chapter says the broader class has no finite ceiling.")
    alt = ((f"Left, the equilibrium to optimum ratio against demand, a flat line at 1.00 under a dashed 4/3 bound. " if flat else
            f"Left, the equilibrium to optimum ratio against demand, peaking at {fmt(top, 3)} at demand {fmt(peak_demand, 2)} under a dashed 4/3 bound. ")
           + "Right, the flow on the middle link at equilibrium and at the optimum against demand"
           + (", both zero." if flat else ", with a hatched gap where the equilibrium uses the link more than the optimum does."))
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3

RULES = {"none": "No charge", "marginal": "Marginal-cost charge", "toll": "Toll of 0.5 on the middle link only",
         "toll49": "Toll of 0.49 on the middle link only"}
TOLLS = {"toll": 0.5, "toll49": 0.49}


def mc_equilibrium(D):
    """Equilibrium flows when every congestible edge is charged 2 x flow (Equation 21.3 with a = 1, b = 0 or 1)."""
    z = min(D, max(0.0, 1.0 - D))
    return (D - z) / 2, z


def charged_picture(rule="marginal", demand=1):
    D = float(demand)
    tl = TOLLS.get(rule, 0.0)
    if rule == "marginal":
        x, z = mc_equilibrium(D)
        lo = lab(D)
        if abs(z - float(lo["optimal_shortcut_flow"])) > 1e-9:
            raise AssertionError("marginal-cost equilibrium disagrees with the laboratory optimum")
    else:
        m = lab(D, toll=tl)
        x, z = float(m["equilibrium_outer_flow_each"]), float(m["equilibrium_shortcut_flow"])
    v = x + z
    physical = 2 * v * v + 2 * x
    opt = float(lab(D)["optimal_social_time"])
    slope = 2.0 if rule == "marginal" else 1.0
    outer_cost = slope * v + 1.0
    middle_cost = 2 * slope * v + tl
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
    right.set_title(f"Route costs the choosers see; physical total {fmt(physical, 4)}", fontsize=11.0)

    if rule == "marginal":
        step = (f"Corrected cost of an outer route = 2 x {fmt(v, 2)} + 1 = {fmt(outer_cost, 2)}; of the middle route = "
                f"2 x {fmt(v, 2)} + 2 x {fmt(v, 2)} = {fmt(middle_cost, 2)}")
    elif rule in TOLLS:
        step = (f"Outer route = {fmt(v, 2)} + 1 = {fmt(outer_cost, 2)}; middle route = {fmt(v, 2)} + {fmt(v, 2)} + {fmt(tl, 2)} toll = {fmt(middle_cost, 2)}")
    else:
        step = f"Outer route = {fmt(v, 2)} + 1 = {fmt(outer_cost, 2)}; middle route = {fmt(v, 2)} + {fmt(v, 2)} = {fmt(middle_cost, 2)}"
    gap = physical - opt
    if abs(gap) <= TOL:
        after = f"Physical total latency {fmt(physical, 4)} equals the social optimum {fmt(opt, 4)}."
    else:
        after = f"Physical total latency {fmt(physical, 4)} is {fmt(gap, 4)} above the social optimum {fmt(opt, 4)}."
    if rule == "marginal":
        tail = ("The charge makes each chooser face the delay it adds for others, so the equilibrium lands on the optimum. "
                "Charge payments are transfers and are left out of physical latency.")
    elif rule in TOLLS:
        if abs(gap) <= TOL:
            tail = ("A toll on the link alone reaches the optimum here although it charges only one edge, "
                    "unlike the chapter's rule, which charges every congestible edge.")
        else:
            tail = ("A toll on the link alone does not reach the optimum here, and it charges only one edge, "
                    "unlike the chapter's rule, which charges every congestible edge. At demand 1 the smallest toll that empties the link is 0.5.")
    else:
        tail = "Nothing prices the exported delay, so each trip takes the cheaper-looking route."
    metrics = {
        "Rule": RULES[rule],
        "Outer route cost seen": fmt(outer_cost, 2),
        "Middle route cost seen": fmt(middle_cost, 2),
        "Flow on the middle route": fmt(z, 2),
        "Physical total latency": fmt(physical, 4),
        "Social optimum": fmt(opt, 4),
    }
    interpretation = (f"At demand {fmt(D, 2)} the equilibrium puts {fmt(x, 2)} on each outer route and {fmt(z, 2)} on the middle, so each "
                      f"congestible edge carries {fmt(v, 2)}. {step}. Physical total = 2 x {fmt(v, 2)} x {fmt(v, 2)} + 2 x {fmt(x, 2)} x 1.00 = "
                      f"{fmt(physical, 4)}. {after} {tail}")
    steps = [
        f"Rule: {RULES[rule].lower()}; demand D = {fmt(D, 2)}.",
        f"Travellers pick the cheapest seen route: {fmt(x, 2)} on each outer route and {fmt(z, 2)} on the middle.",
        f"Each congestible edge carries v = {fmt(x, 2)} + {fmt(z, 2)} = {fmt(v, 2)}.",
        step + ".",
        f"Physical total = 2 x {fmt(v, 2)} x {fmt(v, 2)} + 2 x {fmt(x, 2)} x 1.00 = {fmt(physical, 4)}.",
        f"Social optimum = {fmt(opt, 4)}; excess = {fmt(physical, 4)} - {fmt(opt, 4)} = {fmt(gap, 4)}.",
    ]
    alt = (f"Left, the delay line q with the doubled marginal-cost line and the fixed edge at 1, with a marker at flow {fmt(v, 2)}. "
           f"Right, flows on the three routes for '{RULES[rule].lower()}' at demand {fmt(D, 2)}: {fmt(x, 2)}, {fmt(x, 2)} and {fmt(z, 2)}, with the costs each chooser sees.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


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
    steps = [
        f"Equilibrium at r = {fmt(r, 2)}: everyone takes the link, so each congestible edge carries {fmt(r, 2)}.",
        f"Equilibrium cost = 2 x {fmt(r, 2)} x {fmt(r, 2)} = {fmt(eq, 3)}.",
        f"The benchmark must carry (1 + {fmt(g, 2)}) x {fmt(r, 2)} = {fmt(d, 3)}.",
        f"Its optimal cost: {hand_text}.",
        f"Ratio = {fmt(eq, 3)} / {fmt(opt, 3)} = {fmt(ratio, 3)}; guaranteed factor 1 / {fmt(g, 2)} = {fmt(factor, 2)}.",
    ]
    alt = (f"Left, the optimal cost curve against the traffic rate, with the equilibrium cost {fmt(eq, 3)} at r = {fmt(r, 2)} and the optimum {fmt(opt, 3)} at {fmt(d, 3)} marked. "
           f"Right, the guaranteed factor 1 over extra against this network's ratio {fmt(ratio, 3)}, well below it.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 21,
    "title": "Markets, Teams, and Institutions",
    "subtitle": "Each participant can make a sensible local choice while the whole workflow gets slower; a rule decides whether local incentives add up to the task.",
    "summary": (
        "These four demonstrations use the chapter's five-edge traffic network: one unit of traffic from S to T, two routes that each mix a "
        "congestible edge with a fixed one, and a free directed link in the middle. They show why the free link moves the stable pattern away from the best one, how far the damage can go "
        "for linear delays, how a charge on exported delay repairs it (and how a toll on the link alone differs), and what the capacity comparison does and does not promise."
    ),
    "ask_skill": {"prompt": (
        "Here are my routes, their delays and the demand. Find the equilibrium, the social optimum and the ratio, tell me whether the four-thirds "
        "bound applies to my delays, and test whether a charge on each congestible edge restores the optimum.")},
    "demos": [
        {
            "id": "C21-D01",
            "title": "A free link: better, worse or unchanged",
            "question": "When a zero-latency link is added, why does the stable pattern of choices differ from the best one, and how does that depend on demand?",
            "equations": [EQ_TL],
            "symbols": (
                "S is the source, T the target, U the upper junction and L the lower junction. The three routes are S-U-T, S-L-T and S-U-L-T, which crosses the directed middle link from U to L. q is a flow (the amount of traffic) and q_e the traffic on edge e. The latency function l_e(q_e) is the delay a traveller meets on "
                "edge e. TL(q) is total latency: the sum over edges of traffic times delay. Here the two congestible edges (S-U and L-T) have "
                "delay equal to their flow, the two fixed edges (U-T and S-L) have delay 1, and the middle link has delay 0. Demand D is the total "
                "traffic from S to T; z is the flow on the middle route, and v = (D + z) / 2 is then the flow on each congestible edge. The equilibrium is the pattern in which no traveller can lower their own delay by switching routes. "
                "Choosing 'link removed' deletes the middle link, so only the two outer routes remain."
            ),
            "prediction": "At the chapter's demand of 1, will total latency with the link be higher, lower or the same as before? Then try demand 2.",
            "prediction_options": ["Higher", "Lower", "The same"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "At demand 1 everyone takes the link, each trip costs 2, and total latency rises from 1.5 to 2. Select demand 1 with the link to see it.",
                "incorrect": "At demand 1 everyone takes the link, each trip costs 2, and total latency rises from 1.5 to 2 although no road got slower. Select demand 1 with the link to see it.",
            },
            "misconception": {
                "title": "More options must make everyone better off",
                "text": ("The chapter says this is no contradiction: each traveller correctly reads the available routes, and only the premise that more options must improve their collection fails. "
                         "The measurement that lies by omission records each traveller's best response, not whether those responses add up to the system's job."),
            },
            "scope_note": {
                "text": ("Braess's network does not prove that new tools, shared agents, markets, or centralized review make real teams worse. It gives a mechanism to test: changed options alter the equilibrium created by local rules."),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "The left panel prices each route at every possible flow z on the middle link: the middle route rises twice as fast as an outer route because it uses both congestible edges, "
                "so it stays cheaper than an outer route until z reaches 2 - D, and travellers keep switching until then. The right panel prices the whole system at the same z: total latency is smallest at z = 1 - D, "
                "or at zero when that is negative (for the demands from 0.5 to 2 offered here). The two panels have different minimisers, which is the gap between a stable private pattern and the best total. "
                "At demand 1 everyone takes the link, each trip costs 1 + 1 = 2, and TL rises from 1.5 to 2, while the best split is still the old one. At low demand the link is a real gain, and at high demand it is unused because the outer routes "
                "have already become as slow as the middle. Without the link the two panels agree on one split."
            ),
            "application": (
                "Before adding a shared shortcut such as a common reviewer, a shared tool or a fast lane, ask what everyone will do once it exists, "
                "not whether one case could finish faster against yesterday's traffic."
            ),
            "assumptions": (
                "One unit-scale network with linear congestible edges, many small travellers who each pick the cheapest route, and a total-delay "
                "objective. It does not say that any real shortcut, tool or team behaves this way. In this construction the paradox disappears once demand is large enough "
                "to make the outer routes as slow as the middle route (the two totals tie at demand 2); this is a result of the reader's computation, not a statement of the chapter."
            ),
            "check": "At demand 1.5, what does each trip cost with the link, and how does that compare with the cost of an outer route?",
            "answer": (
                "Equilibrium puts 0.5 on each outer route and 0.5 on the middle, so each congestible edge carries 1.0. An outer route costs "
                "1.0 + 1 = 2.0 and the middle costs 1.0 + 1.0 = 2.0, a tie. Total latency is 2 x 1.0 x 1.0 + 2 x 0.5 x 1 = 3.0, which is 2.0 per trip."
            ),
            "provenance": "Constructed example: the chapter's one-unit network with demand varied, with and without the link; equilibrium and optimum are computed with the laboratory's congestion function.",
            "source_section": "A free connection changes what best means",
            "source_anchor": "a-free-connection-changes-what-best-means",
            "controls": [
                {"key": "demand", "label": "Demand (units of traffic from S to T)", "values": [0.5, 1, 1.5, 2], "default": 1},
                {"key": "network", "label": "Network", "values": ["link", "nolink"], "default": "link",
                 "value_labels": ["With the free link", "Link removed"]},
            ],
            "function": "free_link_picture",
        },
        {
            "id": "C21-D02",
            "title": "How bad can it get with linear delays",
            "question": "Across every demand, how large can the ratio of equilibrium delay to optimal delay be when every delay is linear, and where does the gap come from?",
            "equations": [EQ_BOUND],
            "symbols": (
                "S is the source, T the target, U the upper junction and L the lower junction. The three routes are S-U-T, S-L-T and S-U-L-T, which crosses the directed middle link from U to L. TL(q) is total latency. q^NE is the equilibrium flow and q* the flow with the smallest total latency, so the ratio compares "
                "self-directed routing with the best feasible routing. Linear means each edge delay is a times its flow plus b, with a and b "
                "not negative. The control sets a constant delay on the middle link (the b of that edge); 0 is the chapter's free link. In the right panel, the flow on the middle link is shown for the equilibrium and for the optimum at each demand."
            ),
            "prediction": "Make the link slower (delay 0.5). Does the highest ratio rise, fall or stay at 4/3?",
            "prediction_options": ["Rise above 4/3", "Stay at 4/3", "Fall below 4/3"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "With delay 0.5 the peak is at demand 0.5: 0.5 x (2 x 0.5 + 0.5) / (0.5 x (0.5 / 2 + 1)) = 0.75 / 0.625 = 1.2, below 4/3. Select 0.5 to see it.",
                "incorrect": "With delay 0.5 the peak falls to 0.75 / 0.625 = 1.2, below 4/3, and it can never rise above 4/3 when every delay is linear. Select 0.5 to see it.",
            },
            "misconception": {
                "title": "Four thirds is a generic comfort number",
                "text": ("The chapter says treating four thirds as a generic comfort number would repeat the opening error, substituting a convenient measurement for the object being measured. "
                         "Under only continuous, nondecreasing latency functions the ratio can be unbounded, so the bound belongs to a declared model of delay, not to the word equilibrium."),
            },
            "scope_note": {
                "text": ("The linear four-thirds bound does not cover every queue or institution. Check the latency-function class before applying the ratio: a linear approximation over ordinary load does not establish a guarantee past that operating range."),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "Each point of the left curve is the lab's equilibrium total divided by its optimal total at one demand. The ratio is 1 when the link is unused or "
                "already optimal. The right panel shows why it rises: it peaks where demand is just large enough that the optimum shuts the link while the equilibrium still crowds "
                "onto it (the hatched gap). With a free link the peak reaches 4/3 exactly, and no linear delay example can go higher. "
                "The chapter's strings-and-springs image states the same bound as a distance: after severing, the weight hangs at least 1 / (4 / 3) = 0.75 of its original distance below the support."
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
            "provenance": "Constructed example: the chapter's network with a middle-link delay defined for this reader; ratios and flows are computed with the laboratory's congestion function.",
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
            "question": "If every congestible edge charges its own delay plus the delay the traveller adds for others, where does the equilibrium land, and how does a toll on the link alone compare?",
            "equations": [EQ_MC],
            "symbols": (
                "S is the source, T the target, U the upper junction and L the lower junction. The three routes are S-U-T, S-L-T and S-U-L-T, which crosses the directed middle link from U to L. l_e(q_e) is the delay on edge e at flow q_e. The marginal-cost latency adds q_e times the slope of l_e, which is the extra delay "
                "one more unit of flow imposes on those already there. For a delay a x q + b the charged cost is 2 x a x q + b: the congestion term "
                "doubles and the fixed term does not. Here a = 1 and b = 0 on a congestible edge, and a = 0 and b = 1 on a fixed edge. A toll on the link alone adds a fixed charge to the middle route only; it is a different rule from the marginal-cost charge."
            ),
            "prediction": "At demand 1 with the marginal-cost charge, how much traffic uses the middle link?",
            "prediction_options": ["All of it (1.00)", "Half of it (0.50)", "None (0.00)"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "Charged costs are 2v + 1 for an outer route and 4v for the middle; at v = 0.5 they tie at 2, so the flow stays on the outer routes, and the physical total is 1.5. Marginal-cost charge at demand 1 shows it.",
                "incorrect": "Charged costs are 2v + 1 for an outer route and 4v for the middle; at v = 0.5 they tie at 2, so no traffic uses the middle link and the physical total is 1.5. Marginal-cost charge at demand 1 shows it.",
            },
            "misconception": {
                "title": "Treating the toll on the link as the marginal-cost charge",
                "text": ("The notebook's toll of 0.5 on the shortcut alone is a different rule from the chapter's marginal-cost charge of 0.5 on each congestible edge (Equation (21.3)). "
                         "The chapter keeps the charge out of physical travel time: payments are transfers, and adding them to travel time would change the objective being minimized."),
            },
            "scope_note": {
                "text": ("Marginal-cost pricing does not decide fairness, authority, or legitimacy. Those require objectives and constraints stated outside the routing model."),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "Travellers still choose the cheapest route, but now by the charged cost. The charge turns the old comparison 1 + v against 2v "
                "into 2v + 1 against 4v, which moves traffic back toward the outer routes. The physical delay then equals the best possible total. "
                "A toll of 0.5 on the link alone is the notebook's variant: a different rule, although at the demands shown it gives "
                "the same flows and the same total as the marginal-cost charge. At demand 1 the smallest toll that empties the link is 0.5, and 0.49 leaves 0.02 of the traffic on it. "
                "At demand 0.5, the notebook's transfer case, the link is privately efficient, so the paradox depends on the demand regime."
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
            "provenance": "Constructed example: the chapter's network and its marginal-cost charge at the laboratory's default demand 1, a changed toll and the transfer demand 0.5; the no-charge and toll cases use the laboratory's congestion function, and the marginal-cost flows are derived here and checked against the laboratory's optimum.",
            "source_section": "Prices that make group target locally legible",
            "source_anchor": "prices-that-make-group-target-locally-legible",
            "controls": [
                {"key": "rule", "label": "Charging rule", "values": ["none", "marginal", "toll", "toll49"], "default": "marginal",
                 "value_labels": ["No charge", "Marginal-cost charge", "Toll of 0.5 on the middle link only", "Toll of 0.49 on the middle link only"]},
                {"key": "demand", "label": "Demand (units of traffic from S to T)", "values": [1, 0.75, 0.5], "default": 1},
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
            "prediction": "With extra = 1 (the benchmark carries twice the traffic) at r = 1, is the equilibrium cost below or above the optimal cost at rate 2?",
            "prediction_options": ["Below it", "Above it"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "Equilibrium at r = 1 costs 2 x 1 x 1 = 2, while the optimum at rate 2 costs 2 x (2 / 2 + 1) = 4. Select rate 1 and extra 1.",
                "incorrect": "Equilibrium at r = 1 costs 2 x 1 x 1 = 2, while the optimum at rate 2 costs 2 x (2 / 2 + 1) = 4, so it is below. Select rate 1 and extra 1.",
            },
            "misconception": {
                "title": "Reading 'twice the traffic' as doubled capacity",
                "text": ("The chapter says the phrase 'forced to carry twice the traffic' is the whole statement: it does not mean that capacity was doubled. "
                         "The network is unchanged and the comparison changes the amount of demand the optimal benchmark must serve."),
            },
            "scope_note": {
                "text": ("The bicriteria comparison says how much worse a self-directed allocation can be relative to a deliberately burdened benchmark. It does not identify which server to buy."),
                "source_section": "Capacity is a comparison, not a cure",
            },
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
                "The chapter's linear network and the rates r = 0.5, 0.75 and 1. The guarantee is a bound over all networks in its class, and "
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
                {"key": "rate", "label": "Traffic rate r", "values": [0.5, 0.75, 1], "default": 1},
                {"key": "extra", "label": "Extra-traffic fraction", "values": [0.25, 0.5, 1], "default": 0.5},
            ],
            "function": "capacity_picture",
        },
    ],
}

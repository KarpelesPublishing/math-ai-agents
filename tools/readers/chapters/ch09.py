"""Chapter 9 reader: Searching the Future.

Four demonstrations built on Equations (9.2) to (9.4). Demonstrations 2 and 3
check their own search arithmetic against the laboratory's A* function
(math_ai_agents.chapters.ch09.evaluate) on every state, so the reader, the
notebook and the chapter skill agree. Every number is a constructed teaching
value; Demonstrations 1 to 3 start from the chapter's own worked numbers and
Demonstration 4 from the chapter's 200 and 900 millisecond example.
"""
import heapq
import math

import numpy as np

from math_ai_agents.chapters.ch09 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

EQ_FHAT = r"\hat f(v) \;=\; \hat g(v) \;+\; \hat h(v)"
EQ_ADMISSIBLE = r"\hat h(v) \;\le\; h(v) \qquad \text{for every vertex } v"
EQ_CONSISTENT = r"h(u,v) \;+\; \hat h(v) \;\ge\; \hat h(u)"
EQ_CONSISTENT_EDGE = r"\hat h(u) \le \operatorname{cost}(u,v)+\hat h(v)"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


def num(x):
    """Whole numbers without decimals, others with one decimal."""
    x = float(x)
    return str(int(round(x))) if math.isclose(x, round(x), abs_tol=1e-9) else fmt(x, 1)


def names(items):
    return ", ".join(items)


# Demonstration 1: the recorded cost tightens (the chapter's four-vertex trace)

START_TO_A = 3
A_TO_C = 2


def recorded_cost_picture(ab_cost=3, direct_cost=7):
    ab_cost, direct_cost = float(ab_cost), float(direct_cost)
    g_a = float(START_TO_A)
    g_c = g_a + A_TO_C
    via_a = g_a + ab_cost
    lowered = via_a < direct_cost  # strict improvement, as in step 5 of the algorithm
    g_b_after = via_a if lowered else direct_cost

    fig, ax = new_figure(height=4.3)
    cats = ["A", "B", "C (new)"]
    x = np.arange(3)
    w = 0.36
    before = [g_a, direct_cost]
    ax.bar(x[:2] - w / 2, before, w, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.2,
           label="before A is expanded")
    after = [g_a, g_b_after, g_c]
    colors = [PALETTE["navy"], PALETTE["teal"] if lowered else PALETTE["navy"], PALETTE["navy"]]
    ax.bar(x + w / 2, after, w, color=colors, label="after A is expanded")
    for xi, v in zip(x[:2] - w / 2, before):
        ax.text(xi, v + 0.15, num(v), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
    kept = ", tie, kept" if math.isclose(via_a, direct_cost) else ", kept"
    tags = [num(g_a), (num(g_b_after) + (", lowered" if lowered else kept)), num(g_c)]
    for xi, v, tag in zip(x + w / 2, after, tags):
        ax.text(xi + 0.02, v + 0.15, tag, ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
    ax.set_xticks(x, cats)
    ax.set_xlim(-0.6, 2.7)
    ax.set_ylim(0, 11.5)
    ax.set_xlabel("Vertex")
    ax.set_ylabel("Recorded cost from the start (constructed units)")
    ax.set_title(f"s to A costs {num(START_TO_A)}, s to B costs {num(direct_cost)}\n"
                 f"A to C costs {num(A_TO_C)}, A to B costs {num(ab_cost)}", fontsize=11.5)
    ax.legend(loc="upper left", frameon=False, fontsize=10.5)
    ax.grid(axis="x", alpha=0)

    calc = (f"Expanding A (recorded cost {num(g_a)}) generates C at {num(g_a)} + {num(A_TO_C)} = {num(g_c)} and offers "
            f"B a route of {num(g_a)} + {num(ab_cost)} = {num(via_a)}. B's record was {num(direct_cost)}.")
    if lowered:
        verdict = (f" Since {num(via_a)} is strictly lower than {num(direct_cost)}, the record falls to {num(via_a)} and A becomes "
                   "B's parent. No estimate was involved: a cost recorded early was an upper bound, and a cheaper route tightened it.")
        change = f"lowered by {num(direct_cost - via_a)}"
    elif math.isclose(via_a, direct_cost):
        verdict = (f" The two routes tie at {num(via_a)}. The update rule needs a strictly lower cost, so the record and B's "
                   "parent do not change. Nothing was lost: both routes cost the same.")
        change = "no change (tie)"
    else:
        verdict = (f" The route through A is higher than the record, so {num(via_a)} is ignored and B keeps its record of "
                   f"{num(direct_cost)}.")
        change = "no change (route is dearer)"
    metrics = {
        "Recorded cost of A": num(g_a),
        "Recorded cost of C": num(g_c),
        "B before, after": f"{num(direct_cost)}, {num(g_b_after)}",
        "Route to B through A": num(via_a),
        "Record of B": change,
    }
    return fig, metrics, calc + verdict


# Demonstration 2: one overestimate hides the cheaper route (the chapter's two-route graph)

TWO_ROUTE_EDGES = {"s": [("a", 1.0), ("b", 1.0)], "a": [("goal_a", 9.0)], "b": [("goal_b", 24.0)]}
TWO_ROUTE_GOALS = ("goal_a", "goal_b")
TRUE_REMAINING = {"a": 9.0, "b": 24.0}
ROUTE_COSTS = {"goal_a": 10.0, "goal_b": 25.0}


def astar(edges, h, start, goals):
    """A* graph search with the chapter's queue rules: smallest f, then smaller g, then label; stale entries
    skipped; a vertex is requeued only on a strictly lower cost; the goal is tested on removal."""
    best = {start: 0.0}
    parent = {}
    queue = [(h[start], 0.0, start)]
    selected = []
    while queue:
        f, g, v = heapq.heappop(queue)
        if g != best[v]:
            continue
        selected.append(v)
        if v in goals:
            path = [v]
            while path[-1] != start:
                path.append(parent[path[-1]])
            return {"path": path[::-1], "cost": g, "selected": selected, "expanded": selected[:-1], "best": best}
        for w, c in edges.get(v, []):
            if g + c < best.get(w, math.inf):
                best[w] = g + c
                parent[w] = v
                heapq.heappush(queue, (g + c + h[w], g + c, w))
    raise ValueError("no goal is reachable")


def lab_two_route(h):
    """The laboratory's single-goal A*, with a zero-cost link from each goal to one shared terminal."""
    out = evaluate({
        "nodes": ["s", "a", "b", "goal_a", "goal_b", "done"], "start": "s", "goal": "done",
        "edges": [{"from": "s", "to": "a", "cost": 1}, {"from": "a", "to": "goal_a", "cost": 9},
                  {"from": "s", "to": "b", "cost": 1}, {"from": "b", "to": "goal_b", "cost": 24},
                  {"from": "goal_a", "to": "done", "cost": 0}, {"from": "goal_b", "to": "done", "cost": 0}],
        "heuristic": dict(h, done=0), "heuristic_cost": 0,
    })
    return out


def two_route_run(h_a, h_b):
    h = {"s": 0.0, "a": float(h_a), "b": float(h_b), "goal_a": 0.0, "goal_b": 0.0}
    mine = astar(TWO_ROUTE_EDGES, h, "s", TWO_ROUTE_GOALS)
    lab = lab_two_route(h)
    lab_order = [row["node"] for row in lab["tables"] if row["node"] != "done"]
    admissible = h["a"] <= TRUE_REMAINING["a"] and h["b"] <= TRUE_REMAINING["b"]
    if (lab["metrics"]["path_cost"] != mine["cost"] or lab_order != mine["selected"]
            or lab["metrics"]["admissible"] != admissible or lab["metrics"]["optimal_cost"] != 10.0):
        raise AssertionError("laboratory A* disagrees with the reader's search")
    return mine, admissible


def overestimate_picture(h_a=25, h_b=24):
    h_a, h_b = float(h_a), float(h_b)
    run, admissible = two_route_run(h_a, h_b)
    cost = run["cost"]
    score_a = 1 + h_a
    score_b = 1 + h_b
    unexpanded = [v for v in ("a", "b") if v not in run["expanded"]]

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    xs = np.linspace(0, 30, 61)
    left.axvspan(0, TRUE_REMAINING["a"], facecolor="white", edgecolor=PALETTE["grey"], hatch="///", alpha=0.6, linewidth=0)
    left.plot(xs, 1 + xs, color=PALETTE["navy"])
    left.axhline(25, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.5)
    left.axvline(TRUE_REMAINING["a"], color=PALETTE["grey"], linestyle="dotted", linewidth=1.4)
    left.plot([h_a], [score_a], "o", color=PALETTE["teal"], markersize=9)
    label_point(left, 9.4, 25, "goal_b scores 25", color=PALETTE["terracotta"], dx=4, dy=4, ha="left", va="bottom")
    label_point(left, TRUE_REMAINING["a"], 1.2, "true cost 9", color=PALETTE["ink"], dx=5, dy=0, ha="left", va="bottom")
    left.text(0.4, 31.2, "Eq. (9.3) holds", ha="left", va="top", fontsize=10.5, color=PALETTE["ink"])
    side_right = h_a > 15
    label_point(left, h_a, score_a, f"this state: {num(score_a)}", color=PALETTE["teal"], dx=-8 if side_right else 8,
                dy=10, ha="right" if side_right else "left", va="bottom").set_bbox(BOX)
    left.set_xlim(0, 30)
    left.set_ylim(0, 32)
    left.set_xlabel("Estimate at vertex a (cost units)")
    left.set_ylabel("Queue score of a: 1 + estimate")
    left.set_title(f"When is a expanded? Estimate at b is {num(h_b)}", fontsize=11.5)

    right.bar([0], [10], 0.6, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.2)
    right.bar([1], [cost], 0.6, color=PALETTE["teal"] if cost == 10 else PALETTE["terracotta"])
    right.text(0, 10.4, "10", ha="center", va="bottom", fontsize=10.5)
    right.text(1, cost + 0.4, num(cost), ha="center", va="bottom", fontsize=10.5)
    right.set_xticks([0, 1], ["Best route", "Route returned"])
    right.set_xlim(-0.6, 1.6)
    right.set_ylim(0, 30)
    right.set_xlabel("Route")
    right.set_ylabel("Total route cost (constructed units)")
    right.set_title(f"Expanded: {names(run['expanded'])}", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    if cost == 10:
        outcome = "optimal route (cost 10)"
    else:
        outcome = "suboptimal route (cost 25)"
    metrics = {
        "Score of a, score of b": f"{num(score_a)}, {num(score_b)}",
        "Equation (9.3) holds": "yes" if admissible else "no",
        "Vertices expanded": names(run["expanded"]),
        "Unexpanded": names(unexpanded) if unexpanded else "none",
        "Route returned": f"{outcome}",
    }
    calc = (f"Scores after s is expanded: a is 1 + {num(h_a)} = {num(score_a)} and b is 1 + {num(h_b)} = {num(score_b)}. "
            f"Reaching goal_b costs 1 + 24 = 25 and its estimate is 0, so goal_b would score 25 + 0 = 25.")
    if admissible:
        if cost == 10:
            verdict = (f" Both estimates are at or below the true remaining costs (9 and 24), so Equation (9.3) holds and the "
                       f"search returns the cost-10 route after expanding {names(run['expanded'])}. ")
        else:
            verdict = " Equation (9.3) holds, so this case should not occur."
        verdict += "Admissible estimates can save expansions (compare the zero estimate) but cannot lose the best route."
    elif cost == 10:
        verdict = (f" The estimate at a is above its true remaining cost of 9, so Equation (9.3) fails by {num(h_a - 9)}. "
                   f"Here the score {num(score_a)} still sits at or below 25, so a is expanded and the cost-10 route is found. "
                   "An overestimate does not always cost the answer; it removes the guarantee.")
    else:
        verdict = (f" The estimate at a is above its true remaining cost of 9, so Equation (9.3) fails by {num(h_a - 9)}. "
                   f"Its score {num(score_a)} exceeds 25, so goal_b is selected first and a stays on the queue: the search "
                   "returns cost 25 while a route of cost 10 waited unexpanded. That is 25 / 10 = 2.5 times the best cost.")
    return fig, metrics, calc + verdict


# Demonstration 3: a local consistency check (the chapter's fragment)

UPPER_COST, LOWER_COST, LOWER_ESTIMATE = 6, 3, 5


def lab_is_consistent(h_start, h_upper):
    """The laboratory's consistency flag on the fragment, with each branch closed off by a dear goal edge."""
    out = evaluate({
        "nodes": ["s", "upper", "lower", "goal"], "start": "s", "goal": "goal",
        "edges": [{"from": "s", "to": "upper", "cost": UPPER_COST}, {"from": "s", "to": "lower", "cost": LOWER_COST},
                  {"from": "upper", "to": "goal", "cost": 100}, {"from": "lower", "to": "goal", "cost": 100}],
        "heuristic": {"s": h_start, "upper": h_upper, "lower": LOWER_ESTIMATE, "goal": 0}, "heuristic_cost": 0,
    })
    return out["metrics"]["consistent"]


def consistency_picture(h_upper=1, h_start=8):
    h_upper, h_start = float(h_upper), float(h_start)
    drops = [h_start - h_upper, h_start - LOWER_ESTIMATE]
    costs = [float(UPPER_COST), float(LOWER_COST)]
    ok = [d <= c + 1e-12 for d, c in zip(drops, costs)]
    if lab_is_consistent(h_start, h_upper) != all(ok):
        raise AssertionError("laboratory consistency flag disagrees with the edge inequality")
    scores = [UPPER_COST + h_upper, LOWER_COST + LOWER_ESTIMATE]
    if math.isclose(scores[0], scores[1]):
        first = "tie on score; lower vertex first (smaller recorded cost)"
        first_short = "lower"
    elif scores[0] < scores[1]:
        first, first_short = "upper vertex", "upper"
    else:
        first, first_short = "lower vertex", "lower"
    below = scores[0 if first_short == "upper" else 1] < h_start - 1e-12

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    x = np.arange(2)
    w = 0.36
    left.bar(x - w / 2, drops, w, color=[PALETTE["terracotta"] if not o else "#8fa3b8" for o in ok], edgecolor=PALETTE["grey"],
             hatch="///", linewidth=1.0)
    left.bar(x + w / 2, costs, w, color=PALETTE["navy"])
    for xi, d, o in zip(x - w / 2, drops, ok):
        left.text(xi, d + 0.2, num(d) + ("" if o else " too big"), ha="center", va="bottom", fontsize=10.5)
    for xi, c in zip(x + w / 2, costs):
        left.text(xi, c + 0.2, num(c), ha="center", va="bottom", fontsize=10.5)
    left.set_xticks(x, ["upper edge", "lower edge"])
    left.set_xlim(-0.6, 1.6)
    left.set_ylim(0, 10.5)
    left.set_xlabel("Edge out of the start")
    left.set_ylabel("Cost units")
    left.set_title("Hatched: drop in estimate\nSolid: edge cost", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    first_idx = 0 if first_short == "upper" else 1
    right.bar(x, scores, 0.5, color=[PALETTE["teal"] if i == first_idx else "#8fa3b8" for i in range(2)], edgecolor=PALETTE["grey"])
    right.axhline(h_start, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.5)
    for xi, s in zip(x, scores):
        right.text(xi, s + 0.2, num(s), ha="center", va="bottom", fontsize=10.5)
    right.set_xticks(x, ["upper vertex", "lower vertex"])
    right.set_xlim(-0.6, 1.6)
    right.set_ylim(0, 13)
    right.set_xlabel("Vertex reached from the start")
    right.set_ylabel("Queue score: cost + estimate")
    right.set_title(f"Teal bar: selected first\nDashed line: start's estimate {num(h_start)}", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    calc = (f"Upper edge: {num(h_start)} <= {num(UPPER_COST)} + {num(h_upper)} = {num(UPPER_COST + h_upper)} is "
            f"{'true' if ok[0] else 'false'}, because the estimate drops by {num(h_start)} - {num(h_upper)} = {num(drops[0])} "
            f"across an edge costing {num(UPPER_COST)}. Lower edge: {num(h_start)} <= {num(LOWER_COST)} + {num(LOWER_ESTIMATE)} = "
            f"{num(LOWER_COST + LOWER_ESTIMATE)} is {'true' if ok[1] else 'false'}. ")
    if not ok[0]:
        verdict = (f"Equation (9.4) fails on the upper edge by {num(drops[0] - UPPER_COST)}. The upper vertex scores "
                   f"{num(UPPER_COST)} + {num(h_upper)} = {num(scores[0])} against {num(scores[1])}, so it is selected first, "
                   f"and its score is below the start's estimate of {num(h_start)} (the start's recorded cost is 0, so the two compare directly). That is the signature of an inconsistent "
                   "estimate. The fragment alone does not say whether the route is optimal or whether any vertex is reopened.")
    else:
        extra = (" The upper edge is exactly tight: the estimate drops by as much as the edge costs." if math.isclose(drops[0], UPPER_COST) else "")
        verdict = (f"The estimate never falls by more than an edge costs, so the fragment is consistent.{extra} Selected first: "
                   f"{first}, with scores {num(scores[0])} (upper) and {num(scores[1])} (lower).")
        if not below:
            verdict += f" No selected score is below the start's estimate of {num(h_start)}."
    metrics = {
        "Upper edge: drop, cost": f"{num(drops[0])}, {num(UPPER_COST)}",
        "Lower edge: drop, cost": f"{num(drops[1])}, {num(LOWER_COST)}",
        "Consistent on both edges": "yes" if all(ok) else "no (upper edge)",
        "Scores: upper, lower": f"{num(scores[0])}, {num(scores[1])}",
        "Selected first": first,
    }
    return fig, metrics, calc + verdict


# Demonstration 4: the estimate can cost more than the vertices it saves

EXPANSION_MS = 200.0


def lab_workflow_expansions(structural):
    """Laboratory A* on the chapter's research workflow (advancing actions only). Returns (selections, path cost)."""
    heuristic = {"s": 2, "found": 1, "fetched": 1, "goal": 0} if structural else {"s": 0, "found": 0, "fetched": 0, "goal": 0}
    out = evaluate({
        "nodes": ["s", "found", "fetched", "goal"], "start": "s", "goal": "goal",
        "edges": [{"from": "s", "to": "found", "cost": 1}, {"from": "found", "to": "fetched", "cost": 2},
                  {"from": "fetched", "to": "goal", "cost": 4}],
        "heuristic": heuristic, "heuristic_cost": 0,
    })
    return out["metrics"]["expansions"], out["metrics"]["path_cost"]


def spending_picture(saved=3, estimate_ms=900):
    saved, estimate_ms = float(saved), float(estimate_ms)
    gain = EXPANSION_MS * saved
    net = gain - estimate_ms
    break_even = estimate_ms / EXPANSION_MS
    fig, ax = new_figure(height=4.3)
    xs = np.linspace(0, 5, 51)
    ax.plot(xs, EXPANSION_MS * xs, color=PALETTE["teal"])
    ax.axhline(estimate_ms, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.6)
    ax.axvline(break_even, color=PALETTE["grey"], linestyle="dotted", linewidth=1.4)
    ax.plot([saved], [gain], "s", color=PALETTE["navy"], markersize=9, clip_on=False)
    ax.plot([saved, saved], [gain, estimate_ms], color=PALETTE["gold"], linewidth=2.2, linestyle="solid", clip_on=False)
    label_point(ax, 0.05, estimate_ms, f"estimate costs {num(estimate_ms)} ms", color=PALETTE["terracotta"], dx=0, dy=6, ha="left",
                va="bottom").set_bbox(BOX)
    label_point(ax, 1.0, EXPANSION_MS, "time saved", color=PALETTE["teal"], dx=-6, dy=8, ha="right", va="bottom")
    label_point(ax, break_even, 0, f"break-even {fmt(break_even, 2)}", color=PALETTE["ink"], dx=-5 if break_even > 3 else 5, dy=6,
                ha="right" if break_even > 3 else "left", va="bottom")
    ax.set_xlim(-0.15, 5)
    ax.set_ylim(-20, 1100)
    ax.set_xlabel("Expansions saved per vertex generated")
    ax.set_ylabel("Milliseconds per vertex")
    ax.set_title("Square: this state. Gold bar: saving minus cost", fontsize=11.5)

    if net > 1e-9:
        verdict = (f"The estimate pays for itself: it saves {num(net)} ms per vertex more than it costs, so fewer expansions "
                   "also means less total time here.")
    elif net < -1e-9:
        if saved > 0:
            verdict = (f"The estimate loses {num(-net)} ms per vertex. The search that expands the fewest vertices is the slowest to "
                       "finish, which is the chapter's warning about an estimate that costs more than the vertex it saves.")
        else:
            verdict = f"The estimate loses {num(-net)} ms per vertex."
    else:
        verdict = ("Saving and cost are exactly equal, so total time is the same with or without the estimate. Choose on other "
                   "grounds, such as whether the estimate keeps the best-route guarantee.")
    zero_note = ""
    if saved == 0:
        zero_note = (" With no expansions saved the estimate is pure overhead. That is the chapter's research workflow, where "
                     "the structural estimate and the zero estimate both select four vertices.")
    metrics = {
        "Time saved per vertex": f"{num(gain)} ms",
        "Estimate cost per vertex": f"{num(estimate_ms)} ms",
        "Net per vertex": f"{signed(net, 0)} ms" if net < 0 else f"{num(net)} ms",
        "Break-even expansions saved": fmt(break_even, 2),
    }
    interpretation = (f"Time saved = {num(saved)} x {num(EXPANSION_MS)} = {num(gain)} ms. Net = {num(gain)} - {num(estimate_ms)} = "
                      f"{signed(net, 0)} ms. Break-even = {num(estimate_ms)} / {num(EXPANSION_MS)} = {fmt(break_even, 2)} "
                      f"expansions saved per vertex. {verdict}{zero_note}")
    return fig, metrics, interpretation


CHAPTER = {
    "number": 9,
    "title": "Searching the Future",
    "subtitle": "A search needs a number for every branch it has not explored. What that number must satisfy, and what it costs to produce, decides what the search can promise.",
    "summary": (
        "These four demonstrations follow the chapter's A* search. First the recorded half of the score, then the "
        "condition that keeps the best route, then the condition that keeps the estimate consistent with itself, and "
        "finally the price of computing the estimate. Each one changes a declared value and shows which part of the "
        "result moves."
    ),
    "demos": [
        {
            "id": "C09-D01",
            "title": "The recorded cost is bookkeeping that tightens",
            "question": "When a cheaper route to an already-seen vertex turns up, what happens to its recorded cost, and where does the estimate come in?",
            "equations": [EQ_FHAT],
            "symbols": (
                "g-hat(v) is the cost of the cheapest path to vertex v that the search has found so far, and h-hat(v) is the "
                "estimate of the cost still to come. The queue sorts on f-hat(v), their sum. In this demonstration only the "
                "recorded half matters. s is the start; A, B and C are vertices; costs are in constructed units."
            ),
            "prediction": "Raise the cost of the edge from A to B from 3 to 4. Does the recorded cost of B still change?",
            "explanation": (
                "After A is expanded, the search offers B a route of 3 plus the A to B edge cost. If that is strictly lower than "
                "B's current record, the record drops. If it ties or is higher, nothing changes. Nobody supplied a judgment: the "
                "record only ever moves down toward the true cheapest cost, which is why the g-hat half of Equation (9.2) is "
                "bookkeeping and the h-hat half is the part that needs outside knowledge."
            ),
            "application": (
                "When an agent reaches the same state by two sequences of tool calls, keep one best cost for that state and "
                "update it only when a strictly cheaper sequence appears. The record is then a trustworthy upper bound."
            ),
            "assumptions": (
                "Edge costs are fixed, known and positive, and a repeated vertex is the same state however it was reached. "
                "That fails when the cost of a step depends on the history, for example a deadline or a tool whose price "
                "changes with use; then a state needs more than a vertex label."
            ),
            "check": "If the edge from A to B cost 2 and the direct edge from s to B cost 7, what would B's record become?",
            "answer": "3 + 2 = 5, which is strictly below 7, so the record falls to 5 and A becomes B's parent.",
            "provenance": "Constructed example: the chapter's four-vertex trace (edge costs 3, 7, 2 and 3, where 7 becomes 6), with the A to B cost and the direct cost varied.",
            "source_section": "The trace, worked",
            "source_anchor": "the-trace-worked",
            "controls": [
                {"key": "ab_cost", "label": "Cost of the edge from A to B", "values": [1, 3, 4, 5], "default": 3},
                {"key": "direct_cost", "label": "Cost of the direct edge from s to B", "values": [7, 5], "default": 7},
            ],
            "function": "recorded_cost_picture",
        },
        {
            "id": "C09-D02",
            "title": "One overestimate can hide the cheaper route",
            "question": "How far can the estimate at vertex a exceed its true remaining cost before the search returns the dearer route?",
            "equations": [EQ_ADMISSIBLE],
            "symbols": (
                "h(v) is the true cost of finishing from vertex v and h-hat(v) the estimate. The graph has two routes: s to a "
                "to goal_a costs 1 + 9 = 10, and s to b to goal_b costs 1 + 24 = 25. The true remaining cost is 9 at a and 24 at "
                "b. A queue score is cost so far plus estimate; the search removes the smallest score first."
            ),
            "prediction": "The true remaining cost at a is 9. Set the estimate at a to 20, which breaks Equation (9.3). Does the search return the cost-25 route?",
            "explanation": (
                "Vertex a is expanded only while its score 1 + h-hat(a) is at or below the score of goal_b, which is 25. An "
                "estimate at or below 9 keeps a well inside that limit. An estimate above 24 pushes a past it, goal_b is "
                "selected first, and the cheap route is never examined. Between 9 and 24 the condition is broken yet this graph "
                "still returns the best route, so the condition is a guarantee, not a symptom detector."
            ),
            "application": (
                "Before describing a search as optimal, ask whether any estimate in it can exceed the true remaining cost. "
                "One high estimate on the wrong branch is enough to lose the best route."
            ),
            "assumptions": (
                "The graph, its costs and the queue rules are fixed as stated in the chapter. This graph is one case: a "
                "broken Equation (9.3) can still return the best route, as the middle values show, and on other graphs the "
                "threshold would differ. Ties in score are broken by smaller cost so far, then by label."
            ),
            "check": "With the estimate at b equal to 24, what is the largest estimate at a that still lets the search expand a before selecting goal_b?",
            "answer": "The score of a is 1 + h-hat(a), and goal_b scores 25. At h-hat(a) = 24 the scores tie at 25 and a wins on smaller cost so far (1 against 25), so 24 still works. Any estimate above 24 loses the best route.",
            "provenance": "Constructed example: the chapter's two-route graph (costs 1, 9, 1, 24), with the estimates at a and b varied; each search is also run through the laboratory's A* function.",
            "source_section": "The condition that makes it correct",
            "source_anchor": "the-condition-that-makes-it-correct",
            "controls": [
                {"key": "h_a", "label": "Estimate at a (true remaining cost is 9)", "values": [0, 9, 20, 25], "default": 25},
                {"key": "h_b", "label": "Estimate at b (true remaining cost is 24)", "values": [0, 24], "default": 24},
            ],
            "function": "overestimate_picture",
        },
        {
            "id": "C09-D03",
            "title": "An estimate must not contradict itself",
            "question": "How far may the estimate fall across an edge before it breaks the consistency condition?",
            "equations": [EQ_CONSISTENT, EQ_CONSISTENT_EDGE],
            "symbols": (
                "u and v are neighbouring vertices joined by an edge. h-hat(u) and h-hat(v) are the estimates at each end, "
                "cost(u,v) is the edge cost, and h(u,v) is the true cheapest cost from u to v. In this fragment u is the start "
                "and each edge is the cheapest way across, so the two coincide. The drop is h-hat(u) minus h-hat(v)."
            ),
            "prediction": "Set the estimate at the upper vertex to 1. Which vertex is selected first, and is its score below the start's estimate of 8?",
            "explanation": (
                "Consistency says the estimate may not fall by more than the edge costs. Across the upper edge the start's "
                "estimate of 8 meets an edge cost of 6, so the upper vertex needs an estimate of at least 2. At 1 the "
                "estimate falls by 7 across a cost of 6, and the vertex's score of 7 dips below the start's own 8. The "
                "fragment shows that contradiction and nothing more."
            ),
            "application": (
                "When two estimates are produced separately for neighbouring states, compare their difference with the cost of "
                "the step between them. A difference larger than the step is a sign that the estimator disagrees with itself."
            ),
            "assumptions": (
                "Only the local fragment is drawn: no goal routes are shown, so it cannot tell you whether either estimate is "
                "admissible, which route is best, or whether a vertex will be reopened. A consistent estimate can still be "
                "wrong about the remaining cost; it only cannot be wrong in a self-contradicting way."
            ),
            "check": "If the start's estimate is 8 and the upper edge costs 4 instead of 6, what is the smallest estimate at the upper vertex that satisfies consistency?",
            "answer": "8 <= 4 + h-hat(upper) requires h-hat(upper) >= 8 - 4 = 4.",
            "provenance": "Constructed example: the chapter's consistency fragment (start estimate 8, edges costing 6 and 3, estimates 1 and 5), with the start's estimate and the upper estimate varied; the consistency flag is also checked with the laboratory's A* function.",
            "source_section": "The condition that makes it efficient",
            "source_anchor": "the-condition-that-makes-it-efficient",
            "controls": [
                {"key": "h_upper", "label": "Estimate at the upper vertex", "values": [1, 2, 3, 5], "default": 1},
                {"key": "h_start", "label": "Estimate at the start", "values": [8, 6], "default": 8},
            ],
            "function": "consistency_picture",
        },
        {
            "id": "C09-D04",
            "title": "When the estimate costs more than it saves",
            "question": "How many expansions must an estimate save per vertex before computing it saves any time?",
            "equations": [EQ_FHAT],
            "symbols": (
                "f-hat(v) = g-hat(v) + h-hat(v) must be computed for every vertex the search generates, and computing "
                "h-hat is not free. An expansion is one tool call and costs 200 milliseconds (ms). One estimate costs the chosen "
                "number of ms. Expansions saved is the number of tool calls the estimate spares for each vertex it scores."
            ),
            "prediction": "An estimate saves 3 expansions per vertex and costs 900 ms to compute. Does total time go down?",
            "explanation": (
                "The saving is 200 ms per expansion avoided. The estimate pays only when that saving exceeds what the estimate "
                "costs, so the break-even number of saved expansions is the estimate cost divided by 200. Below it, the search "
                "with the fewest expansions is the slower one."
            ),
            "application": (
                "Price the estimate in the same unit as the step it is meant to avoid. If scoring a candidate takes a model "
                "call, compare it with the tool call, and consider scoring candidates in batches or only when the choice is close."
            ),
            "assumptions": (
                "Constant costs per call, and a number of saved expansions that is assumed here, not measured. Queue work, "
                "storage and batching are left out. The 200 and 900 ms figures are the chapter's constructed example; 400 ms "
                "is a value chosen for this reader. Saving expansions can also matter for reasons other than time, such as the budget of tool calls."
            ),
            "check": "If one estimate costs 600 ms and an expansion costs 200 ms, how many expansions must it save per vertex to break even?",
            "answer": "600 / 200 = 3. At exactly 3 the time is equal; more than 3 saves time; fewer loses time.",
            "provenance": "Constructed example: the chapter's constructed agent latencies (a 200 ms tool call and a 900 ms estimate that saves three expansions), with the number of saved expansions and the estimate cost varied.",
            "source_section": "When the estimate costs more than the vertex",
            "source_anchor": "when-the-estimate-costs-more-than-the-vertex",
            "controls": [
                {"key": "saved", "label": "Expansions saved per vertex", "values": [0, 2, 3, 4], "default": 3},
                {"key": "estimate_ms", "label": "Cost of computing one estimate (ms)", "values": [400, 900], "default": 900},
            ],
            "function": "spending_picture",
        },
    ],
}

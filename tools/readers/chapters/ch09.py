"""Chapter 9 reader: Searching the Future.

Four demonstrations built on Equations (9.1) to (9.4). Every search is run with
the chapter's queue rules (smallest f-hat, then smaller g-hat, then label; stale
entries skipped; a vertex is requeued only on a strictly lower cost; a goal is
tested on removal) and is checked against the laboratory's A* function
(math_ai_agents.chapters.ch09.evaluate) on every state, so the reader, the
notebook and the chapter skill agree.

D01 a stepper through the chapter's own traces: the four-vertex bookkeeping
    graph (7 becomes 6), the two-route graph with the zero estimate, and the
    research workflow with the structural estimate.
D02 the admissibility condition and the exact f = g + h, on the chapter's
    two-route graph and the laboratory notebook's default, changed and transfer
    graphs.
D03 the local consistency fragment (9.4).
D04 what an estimate buys and what it costs: expansions with and without it
    (Theorem 2's subset relation) priced at 200 ms per expansion.
Every number is a constructed teaching value.
"""
import heapq
import math

import numpy as np
from matplotlib.ticker import MaxNLocator

from math_ai_agents.chapters.ch09 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

EQ_TRUE = r"f(v) \;=\; g(v) \;+\; h(v)"
EQ_FHAT = r"\hat f(v) \;=\; \hat g(v) \;+\; \hat h(v)"
EQ_ADMISSIBLE = r"\hat h(v) \;\le\; h(v) \qquad \text{for every vertex } v"
EQ_CONSISTENT = r"h(u,v) \;+\; \hat h(v) \;\ge\; \hat h(u)"
EQ_CONSISTENT_EDGE = r"\hat h(u) \le \operatorname{cost}(u,v)+\hat h(v)"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
EXPANSION_MS = 200.0


def num(x):
    """Whole numbers without decimals, others with one decimal."""
    x = float(x)
    return str(int(round(x))) if math.isclose(x, round(x), abs_tol=1e-9) else fmt(x, 1)


# The graphs

def e(a, b, c):
    return (a, b, float(c))


GRAPHS = {
    "fig91": {
        "nodes": ["s", "A", "B", "C"], "start": "s", "goals": ("B",),
        "edges": [e("s", "A", 3), e("s", "B", 7), e("A", "C", 2), e("A", "B", 3)],
        "h": {"s": 0, "A": 0, "B": 0, "C": 0},
    },
    "tworoute": {
        "nodes": ["s", "a", "b", "goal_a", "goal_b"], "start": "s", "goals": ("goal_a", "goal_b"),
        "edges": [e("s", "a", 1), e("a", "goal_a", 9), e("s", "b", 1), e("b", "goal_b", 24)],
        "h": {"s": 0, "a": 9, "b": 24, "goal_a": 0, "goal_b": 0},
    },
    "workflow": {
        "nodes": ["s", "found", "fetched", "goal"], "start": "s", "goals": ("goal",),
        "edges": [e("s", "found", 1), e("s", "s", 2), e("s", "s", 4),
                  e("found", "found", 1), e("found", "fetched", 2), e("found", "found", 4),
                  e("fetched", "fetched", 1), e("fetched", "fetched", 2), e("fetched", "goal", 4)],
        "h": {"s": 2, "found": 1, "fetched": 1, "goal": 0},
    },
    "notebook": {
        "nodes": ["S", "A", "B", "G"], "start": "S", "goals": ("G",),
        "edges": [e("S", "A", 1), e("A", "G", 4), e("S", "B", 2), e("B", "G", 1)],
        "h": {"S": 3, "A": 4, "B": 1, "G": 0},
    },
    "transfer": {
        "nodes": ["source", "middle", "target"], "start": "source", "goals": ("target",),
        "edges": [e("source", "middle", 2), e("middle", "target", 2), e("source", "target", 7)],
        "h": {"source": 0, "middle": 0, "target": 0},
    },
}


def adjacency(edges):
    out = {}
    for a, b, c in edges:
        out.setdefault(a, []).append((b, c))
    return out


def true_remaining(graph):
    """Exact cost to the nearest goal, by Dijkstra on reversed edges."""
    g = GRAPHS[graph]
    dist = {v: math.inf for v in g["nodes"]}
    heap = []
    for t in g["goals"]:
        dist[t] = 0.0
        heapq.heappush(heap, (0.0, t))
    rev = {}
    for a, b, c in g["edges"]:
        rev.setdefault(b, []).append((a, c))
    while heap:
        d, v = heapq.heappop(heap)
        if d > dist[v]:
            continue
        for u, c in rev.get(v, []):
            if d + c < dist[u]:
                dist[u] = d + c
                heapq.heappush(heap, (d + c, u))
    return dist


def true_g(graph):
    g = GRAPHS[graph]
    adj = adjacency(g["edges"])
    dist = {v: math.inf for v in g["nodes"]}
    dist[g["start"]] = 0.0
    heap = [(0.0, g["start"])]
    while heap:
        d, v = heapq.heappop(heap)
        if d > dist[v]:
            continue
        for w, c in adj.get(v, []):
            if d + c < dist[w]:
                dist[w] = d + c
                heapq.heappush(heap, (d + c, w))
    return dist


def astar(graph, h):
    """A* with the chapter's rules. Returns a log of every selection plus totals."""
    g = GRAPHS[graph]
    adj = adjacency(g["edges"])
    start, goals = g["start"], g["goals"]
    best = {start: 0.0}
    parent = {}
    queue = [(h[start], 0.0, start)]
    pushes = 0
    log, examined = [], 0
    while queue:
        f, gg, v = heapq.heappop(queue)
        if gg != best[v]:
            continue
        valid = sorted(x for x in queue if x[1] == best[x[2]])
        tie = bool(valid) and math.isclose(valid[0][0], f, abs_tol=1e-9)
        step = {"v": v, "g": gg, "f": f, "goal": v in goals, "updates": [], "rejected": [], "tie": tie}
        if v in goals:
            path = [v]
            while path[-1] != start:
                path.append(parent[path[-1]])
            step["path"] = path[::-1]
            step["frontier"] = []
            log.append(step)
            return {"log": log, "path": path[::-1], "cost": gg, "best": dict(best), "examined": examined,
                    "calls": 1 + pushes, "parent": dict(parent)}
        for w, c in adj.get(v, []):
            examined += 1
            if gg + c < best.get(w, math.inf):
                old = best.get(w)
                best[w] = gg + c
                parent[w] = v
                pushes += 1
                heapq.heappush(queue, (gg + c + h[w], gg + c, w))
                step["updates"].append((w, c, old, gg + c, h[w]))
            else:
                step["rejected"].append((w, c, gg + c, best.get(w)))
        step["frontier"] = sorted((x for x in queue if x[1] == best[x[2]]))
        step["best_after"] = dict(best)
        log.append(step)
    raise ValueError("no goal is reachable")


def expanded_of(run):
    return [s["v"] for s in run["log"] if not s["goal"]]


def lab_check(graph, h, run):
    """Compare the reader's search with the laboratory's A* (a shared terminal is added for several goals)."""
    g = GRAPHS[graph]
    nodes, edges, goal = list(g["nodes"]), [{"from": a, "to": b, "cost": c} for a, b, c in g["edges"]], g["goals"][0]
    heur = dict(h)
    if len(g["goals"]) > 1:
        nodes.append("done")
        goal = "done"
        for t in g["goals"]:
            edges.append({"from": t, "to": "done", "cost": 0})
        heur["done"] = 0
    out = evaluate({"nodes": nodes, "start": g["start"], "goal": goal, "edges": edges,
                    "heuristic": {k: float(v) for k, v in heur.items()}, "heuristic_cost": 0})
    m = out["metrics"]
    order = [row["node"] for row in out["tables"] if row["node"] != "done"]
    sel = [s["v"] for s in run["log"]]
    if m["path_cost"] != run["cost"] or order != sel:
        raise AssertionError(f"laboratory A* disagrees with the reader's search on {graph}")
    if m["heuristic_calls"] != run["calls"] + (1 if len(g["goals"]) > 1 else 0):
        raise AssertionError("laboratory heuristic call count disagrees with the reader's search")
    return m


def names(items):
    return ", ".join(items)


# Demonstration 1: stepping through the chapter's traces (Equation 9.2)

TRACES = {
    "fig91": ("Bookkeeping graph (Figure 9.1), goal B", "fig91"),
    "zero": ("Two-route graph, zero estimate", "tworoute"),
    "flow": ("Research workflow, structural estimate", "workflow"),
}
TRACE_H = {
    "fig91": None, "zero": {"s": 0, "a": 0, "b": 0, "goal_a": 0, "goal_b": 0}, "flow": None,
}


def trace_picture(trace="fig91", step=1):
    label, graph = TRACES[trace]
    step = int(step)
    h = dict(GRAPHS[graph]["h"]) if TRACE_H[trace] is None else dict(TRACE_H[trace])
    run = astar(graph, h)
    lab_check(graph, h, run)
    log = run["log"]
    cur = log[step - 1]
    nodes = GRAPHS[graph]["nodes"]
    # recorded costs after this step, and which vertices have been selected so far
    best_now = cur.get("best_after", run["best"]) if not cur["goal"] else run["best"]
    done = [s["v"] for s in log[:step]]
    expanded = [v for v in done if v not in GRAPHS[graph]["goals"] or v != cur["v"] or not cur["goal"]]
    expanded = [s["v"] for s in log[:step] if not s["goal"]]
    seen = [v for v in nodes if v in best_now]
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    x = np.arange(len(seen))
    for xi, v in zip(x, seen):
        gv, hv = best_now[v], h[v]
        edge = PALETTE["gold"] if v == cur["v"] else PALETTE["ink"]
        lw = 2.6 if v == cur["v"] else 0.8
        left.bar(xi, gv, 0.6, color=PALETTE["navy"], edgecolor=edge, linewidth=lw)
        if hv > 0:
            left.bar(xi, hv, 0.6, bottom=gv, color="white", edgecolor=PALETTE["teal"], hatch="///", linewidth=1.0)
        left.annotate(f"f {num(gv + hv)}", (xi, gv + hv), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom",
                      fontsize=10, color=PALETTE["ink"])
    for w, c, old, new, hw in cur["updates"]:
        if old is not None and w in seen:
            xi = seen.index(w)
            left.annotate(f"lowered from {num(old)}", (xi, new + hw), xytext=(0, 17), textcoords="offset points", ha="center",
                          va="bottom", fontsize=9.5, color=PALETTE["terracotta"])
    ymax = max(best_now[v] + h[v] for v in seen)
    left.set_ylim(0, ymax * 1.4 + 1)
    left.set_xlim(-0.6, max(len(seen), 3) - 0.4)
    left.set_xticks(x, [v + ("\nexpanded" if v in expanded else "") for v in seen])
    left.set_xlabel("Vertex generated so far")
    left.set_ylabel("Cost (seconds)" if graph == "workflow" else "Cost (constructed units)")
    left.yaxis.set_major_locator(MaxNLocator(integer=True))
    left.set_title(f"Step {step} of {len(log)}: select {cur['v']}", fontsize=11.5)
    left.text(0.02, 0.98, "navy: recorded cost\nhatched: estimate", transform=left.transAxes, ha="left", va="top", fontsize=10,
              color=PALETTE["ink"])
    left.grid(axis="x", alpha=0)
    fr = cur["frontier"]
    if fr:
        ys = np.arange(len(fr))[::-1]
        for y, (f, gg, v) in zip(ys, fr):
            right.barh(y, f, height=0.55, color=PALETTE["teal"] if y == ys[0] else PALETTE["light"], edgecolor=PALETTE["ink"], linewidth=0.8)
            right.text(f + 0.4, y, f"{v}: g {num(gg)}, f {num(f)}", va="center", fontsize=10, color=PALETTE["ink"])
        right.set_yticks(ys, [str(i + 1) for i in range(len(fr))][::-1][::-1])
        right.set_xlim(0, max(f for f, _, _ in fr) * 2.1 + 3)
        right.set_ylim(-0.6, len(fr) - 0.4)
    else:
        right.text(0.5, 0.5, "frontier empty:\nthe goal was selected, the search stops", transform=right.transAxes, ha="center", va="center",
                   fontsize=11, color=PALETTE["ink"])
        right.set_xlim(0, 1)
        right.set_ylim(0, 1)
        right.set_yticks([])
    right.set_xlabel("Queue score f (next entry on top)")
    right.set_ylabel("Queue position")
    right.set_title("Frontier after this step", fontsize=11.5)
    right.grid(axis="y", alpha=0)

    ex_count = sum(len(s["updates"]) + len(s["rejected"]) for s in log[:step])
    metrics = {
        "Selected": cur["v"] + (" (goal)" if cur["goal"] else ""),
        "Recorded cost g, score f": f"{num(cur['g'])}, {num(cur['f'])}",
        "Expanded so far": names(expanded) if expanded else "none",
        "Edges examined so far": str(ex_count),
        "Frontier, next first": ", ".join(f"{v} ({num(f)})" for f, _, v in fr) if fr else "empty",
    }
    pieces = [f"Select {cur['v']}: f = {num(cur['g'])} + {num(h[cur['v']])} = {num(cur['f'])}."]
    worked = [pieces[0]]
    if cur["goal"]:
        pieces.append(f"It is a goal and the goal test is on removal, so the search stops and returns the path {names(cur['path'])} "
                      f"with cost {num(cur['g'])}. No successors are generated.")
        worked.append(f"Goal test on removal passes: return {names(cur['path'])}, cost {num(cur['g'])}.")
    else:
        for w, c, old, new, hw in cur["updates"]:
            if old is None:
                t = f"{w} gets g = {num(cur['g'])} + {num(c)} = {num(new)} and f = {num(new)} + {num(hw)} = {num(new + hw)}."
            else:
                t = (f"{w} is offered {num(cur['g'])} + {num(c)} = {num(new)}, strictly below its record of {num(old)}, so the record falls "
                     f"from {num(old)} to {num(new)} and f = {num(new)} + {num(hw)} = {num(new + hw)}.")
            pieces.append(t)
            worked.append(t)
        rej = cur["rejected"]
        if rej:
            t = (f"{len(rej)} edge{'s' if len(rej) != 1 else ''} rejected for not beating the record: "
                 + "; ".join(f"{cur['v']} to {w} gives {num(c2)} against {num(b) if b is not None else 'none'}" for w, _, c2, b in rej)
                 + ".")
            pieces.append(t)
            worked.append(t)
        if not cur["updates"] and not rej:
            pieces.append("It has no outgoing edges.")
        worked.append("Frontier, next first: " + (", ".join(f"{v} {num(f)}" for f, _, v in fr) if fr else "empty") + ".")
        if cur["tie"]:
            pieces.append("The next entry ties on score, so the tie-break (smaller recorded cost, then label) decides.")
    interpretation = " ".join(pieces)
    worked = [w if len(w) <= 235 else w[:232] + "..." for w in worked][:8]
    alt = (f"Step {step} of {len(log)} of the {label.lower()}. Left: stacked bars of recorded cost and estimate for each generated vertex; "
           f"right: the queue after selecting {cur['v']}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 2: admissibility and the exact f = g + h (Equations 9.1 and 9.3)

CASES = {
    # key: (graph, vertex, levels, true remaining, rival route cost, label)
    "tworoute": ("tworoute", "a", [0, 9, 20, 25], 9.0, 25.0, "Chapter two-route graph"),
    "notebook": ("notebook", "B", [0, 1, 3, 10], 1.0, 5.0, "Notebook graph (default and changed)"),
    "transfer": ("transfer", "middle", [0, 2, 5, 9], 2.0, 7.0, "Notebook transfer graph"),
}
LEVEL_NAMES = ["zero", "exact", "over by a little", "over by a lot"]


def overestimate_picture(case="tworoute", level=0):
    graph, v, levels, true_h, rival, label = CASES[case]
    est = float(levels[int(level)])
    h = dict(GRAPHS[graph]["h"])
    h[v] = est
    run = astar(graph, h)
    lab = lab_check(graph, h, run)
    tg, th = true_g(graph), true_remaining(graph)
    nodes = GRAPHS[graph]["nodes"]
    gv = tg[v]
    cstar = tg[GRAPHS[graph]["start"]] + th[GRAPHS[graph]["start"]]
    exp = expanded_of(run)
    admissible = all(h[n] <= th[n] + 1e-9 for n in nodes)
    if lab["admissible"] != admissible:
        raise AssertionError("laboratory admissibility flag disagrees with Equation (9.3) by hand")
    score = gv + est
    best_cost = lab["optimal_cost"]
    returned = run["cost"]
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    xmax = float(max(levels)) + 3
    xs = np.linspace(0, xmax, 61)
    limit = rival - gv
    left.axvspan(0, limit, facecolor="white", edgecolor=PALETTE["grey"], hatch="///", alpha=0.6, linewidth=0)
    left.plot(xs, gv + xs, color=PALETTE["navy"])
    left.axhline(rival, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.5)
    left.axvline(true_h, color=PALETTE["grey"], linestyle="dotted", linewidth=1.4)
    left.plot([est], [score], "o", color=PALETTE["teal"], markersize=9, zorder=4)
    label_point(left, 0.2, rival, f"rival route scores {num(rival)}", color=PALETTE["terracotta"], dx=2, dy=4, ha="left", va="bottom").set_bbox(BOX)
    label_point(left, true_h, 0, f"true cost {num(true_h)}", color=PALETTE["ink"], dx=5, dy=4, ha="left", va="bottom").set_bbox(BOX)
    right_side = est > xmax * 0.5
    ytop = max(rival * 1.3 + 1, score * 1.2 + 1)
    low = score < 0.2 * ytop
    label_point(left, est, score, f"{v}: {num(score)}", color=PALETTE["teal"], dx=-8 if right_side else 8, dy=12 if low else -12,
                ha="right" if right_side else "left", va="bottom" if low else "top").set_bbox(BOX)
    left.set_xlim(0, xmax)
    left.set_ylim(0, max(rival * 1.3 + 1, score * 1.2 + 1))
    left.set_xlabel(f"Estimate at vertex {v} (cost units)")
    left.set_ylabel(f"Queue score of {v}: g + estimate")
    left.set_title(f"Hatched: {v} is expanded", fontsize=11.5)
    fs = [tg[n] + th[n] for n in nodes]
    x = np.arange(len(nodes))
    cols = [PALETTE["teal"] if math.isclose(f, cstar) else PALETTE["terracotta"] for f in fs]
    right.bar(x, fs, 0.6, color=cols, edgecolor=PALETTE["ink"], linewidth=0.8)
    right.axhline(cstar, color=PALETTE["ink"], linestyle="dashed", linewidth=1.2)
    for xi, f in zip(x, fs):
        right.annotate(num(f), (xi, f), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=10)
    right.set_xticks(x, [n.replace("_", "\n") for n in nodes], fontsize=10.5)
    right.set_ylim(0, max(fs) * 1.25 + 1)
    right.set_xlabel("Vertex (teal: on an optimal path)")
    right.set_ylabel("Exact f = g + h")
    right.set_title(f"Exact f; optimal cost C* = {num(cstar)}", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    unexpanded = [n for n in run["best"] if n not in exp and n not in run["path"]]
    on_opt = [n for n, f in zip(nodes, fs) if math.isclose(f, cstar)]
    metrics = {
        f"Score of {v}: g + estimate": num(score),
        "Equation (9.3) holds everywhere": "yes" if admissible else f"no (at {v})",
        "Vertices expanded": names(exp),
        "Generated but unexpanded": names(unexpanded) if unexpanded else "none",
        "Route returned": f"cost {num(returned)} ({'optimal' if math.isclose(returned, best_cost) else 'suboptimal'}, best is {num(best_cost)})",
    }
    calc = (f"Exact f: {names(f'{n} = {num(tg[n])} + {num(th[n])} = {num(tg[n] + th[n])}' for n in nodes)}. Vertices with f = C* = {num(cstar)} "
            f"(on an optimal path): {names(on_opt)}. Score of {v} = {num(gv)} + {num(est)} = {num(score)} against the rival route's {num(rival)}. ")
    if admissible:
        verdict = (f"The estimate at {v} is at or below its true remaining cost {num(true_h)}, so Equation (9.3) holds and the search returns "
                   f"cost {num(returned)}, the best. Admissible estimates can save expansions but cannot lose the best route.")
    elif math.isclose(returned, best_cost):
        verdict = (f"The estimate at {v} is {num(est - true_h)} above its true remaining cost {num(true_h)}, so Equation (9.3) fails. "
                   f"The score {num(score)} is still at or below {num(rival)}, so {v} is expanded and the best route is found. "
                   "An overestimate does not always cost the answer; it removes the guarantee.")
    else:
        verdict = (f"The estimate at {v} is {num(est - true_h)} above its true remaining cost {num(true_h)}, so Equation (9.3) fails. "
                   f"Its score {num(score)} exceeds {num(rival)}, so the rival goal is selected first and {v} stays on the queue: the search returns "
                   f"cost {num(returned)} while a route of cost {num(best_cost)} waited, {num(returned)} / {num(best_cost)} = {fmt(returned / best_cost, 2)} times the best.")
    interpretation = calc + verdict
    worked = [
        f"True remaining cost at {v} is h({v}) = {num(true_h)}; the estimate is {num(est)}.",
        f"Equation (9.3): {num(est)} <= {num(true_h)} is {'true' if est <= true_h + 1e-9 else 'false'}.",
        f"Score of {v} = {num(gv)} + {num(est)} = {num(score)}; the rival route scores {num(rival)}.",
        f"{v} is {'expanded' if v in exp else 'left on the queue'} (it is expanded only when its score is at most {num(rival)}).",
        f"Route returned costs {num(returned)}; the best costs {num(best_cost)}.",
        f"Exact f = g + h equals C* = {num(cstar)} on {names(on_opt)}.",
    ]
    alt = (f"Left: queue score of {v} against its estimate with the rival route's score as a dashed line and the expansion region hatched. "
           f"Right: exact f for each vertex, teal on an optimal path. With estimate {num(est)} the route returned costs {num(returned)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 3: a local consistency check (Equation 9.4)

UPPER_COST, LOWER_COST, LOWER_ESTIMATE = 6, 3, 5


def lab_is_consistent(h_start, h_upper):
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
        first, first_idx = "lower vertex (tie on score, smaller recorded cost)", 1
    elif scores[0] < scores[1]:
        first, first_idx = "upper vertex", 0
    else:
        first, first_idx = "lower vertex", 1
    below = scores[first_idx] < h_start - 1e-12

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    x = np.arange(2)
    w = 0.36
    left.bar(x - w / 2, drops, w, color=[PALETTE["terracotta"] if not o else "#8fa3b8" for o in ok], edgecolor=PALETTE["grey"],
             hatch="///", linewidth=1.0)
    left.bar(x + w / 2, costs, w, color=PALETTE["navy"])
    for xi, d, o in zip(x - w / 2, drops, ok):
        left.text(xi, max(d, 0) + 0.2, num(d) + ("" if o else " too big"), ha="center", va="bottom", fontsize=10.5)
    for xi, c in zip(x + w / 2, costs):
        left.text(xi, c + 0.2, num(c), ha="center", va="bottom", fontsize=10.5)
    left.set_xticks(x, ["upper edge", "lower edge"])
    left.set_xlim(-0.6, 1.6)
    left.set_ylim(0, 10.5)
    left.set_xlabel("Edge out of the start")
    left.set_ylabel("Cost units")
    left.set_title("Hatched: drop in estimate\nSolid: edge cost", fontsize=11.5)
    left.grid(axis="x", alpha=0)
    right.bar(x, scores, 0.5, color=[PALETTE["teal"] if i == first_idx else "#8fa3b8" for i in range(2)], edgecolor=PALETTE["grey"])
    right.axhline(h_start, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.5)
    for xi, s in zip(x, scores):
        right.text(xi, s + 0.2, num(s), ha="center", va="bottom", fontsize=10.5)
    right.set_xticks(x, ["upper vertex", "lower vertex"])
    right.set_xlim(-0.6, 1.6)
    right.set_ylim(0, 17)
    right.set_xlabel("Vertex reached from the start")
    right.set_ylabel("Queue score: cost + estimate")
    right.set_title(f"Teal bar: selected first\nDashed line: start's estimate {num(h_start)}", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    if drops[0] < 0:
        drop_phrase = f"rises by {num(h_upper)} - {num(h_start)} = {num(-drops[0])}"
        drop_step = f"the estimate goes from {num(h_start)} to {num(h_upper)}, a rise of {num(-drops[0])}"
    else:
        drop_phrase = f"drops by {num(h_start)} - {num(h_upper)} = {num(drops[0])}"
        drop_step = f"the estimate goes from {num(h_start)} to {num(h_upper)}, a drop of {num(drops[0])}"
    calc = (f"Upper edge: {num(h_start)} <= {num(UPPER_COST)} + {num(h_upper)} = {num(UPPER_COST + h_upper)} is "
            f"{'true' if ok[0] else 'false'}, because the estimate {drop_phrase} "
            f"across an edge costing {num(UPPER_COST)}. Lower edge: {num(h_start)} <= {num(LOWER_COST)} + {num(LOWER_ESTIMATE)} = "
            f"{num(LOWER_COST + LOWER_ESTIMATE)} is {'true' if ok[1] else 'false'}. ")
    if not ok[0]:
        verdict = (f"Equation (9.4) fails on the upper edge by {num(drops[0] - UPPER_COST)}. The upper vertex scores "
                   f"{num(UPPER_COST)} + {num(h_upper)} = {num(scores[0])} against {num(scores[1])}, so it is selected first, "
                   f"and its score is below the start's estimate of {num(h_start)}. That is the signature of an inconsistent "
                   "estimate. The fragment alone does not say whether the route is optimal or whether any vertex is reopened.")
    else:
        extra = ""
        if math.isclose(drops[0], UPPER_COST):
            extra = " The upper edge is exactly tight: the estimate drops by as much as the edge costs."
        elif drops[0] <= 1e-12:
            extra = " The estimate does not drop at all across the upper edge; consistency does not require progress."
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
    worked = [
        f"Upper edge: {drop_step}; the edge costs {num(UPPER_COST)}.",
        f"Equation (9.4) in edge form: {num(h_start)} <= {num(UPPER_COST)} + {num(h_upper)} = {num(UPPER_COST + h_upper)} is {'true' if ok[0] else 'false'}.",
        f"Lower edge: {num(h_start)} <= {num(LOWER_COST)} + {num(LOWER_ESTIMATE)} = {num(LOWER_COST + LOWER_ESTIMATE)} is {'true' if ok[1] else 'false'}.",
        f"Scores: upper {num(UPPER_COST)} + {num(h_upper)} = {num(scores[0])}, lower {num(LOWER_COST)} + {num(LOWER_ESTIMATE)} = {num(scores[1])}.",
        f"Selected first: {first}.",
    ]
    alt = (f"Left: for each edge out of the start, the drop in the estimate against the edge cost; the upper edge is "
           f"{'consistent' if ok[0] else 'inconsistent'}. Right: queue scores {num(scores[0])} and {num(scores[1])} against the start's estimate {num(h_start)}.")
    return fig, metrics, calc + verdict, {"alt": alt, "steps": worked}


# Demonstration 4: what an estimate buys and what it costs

SPEND = {
    # key: (graph, label of the informed estimate)
    "notebook": ("notebook", "notebook estimate (exact)"),
    "tworoute": ("tworoute", "exact estimate at a and b"),
    "workflow": ("workflow", "structural estimate"),
}


def zero_h(graph):
    return {n: 0 for n in GRAPHS[graph]["nodes"]}


def spending_picture(graph="notebook", price=0):
    graph, label = SPEND[graph]
    price = float(price)
    h_inf = dict(GRAPHS[graph]["h"])
    h_zero = zero_h(graph)
    inf, zero = astar(graph, h_inf), astar(graph, h_zero)
    lab_check(graph, h_inf, inf)
    lab_check(graph, h_zero, zero)
    ex_i, ex_z = expanded_of(inf), expanded_of(zero)
    if inf["cost"] != zero["cost"]:
        raise AssertionError("both admissible searches must return the same cost")
    subset = set(ex_i) <= set(ex_z)
    identical = set(ex_i) == set(ex_z)
    t_inf = EXPANSION_MS * len(ex_i) + price * inf["calls"]
    t_zero = EXPANSION_MS * len(ex_z)
    saved = len(ex_z) - len(ex_i)
    nodes = [n for n in GRAPHS[graph]["nodes"] if n in ex_z or n in ex_i]
    zero_tie = any(s["tie"] for s in zero["log"])
    inf_tie = any(s["tie"] for s in inf["log"])
    break_even = EXPANSION_MS * saved / inf["calls"]

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    ys = np.arange(len(nodes))[::-1]
    for y, n in zip(ys, nodes):
        for xi, ex in ((0, ex_i), (1, ex_z)):
            if n in ex:
                left.plot([xi], [y], "o", color=PALETTE["teal"] if xi == 0 else PALETTE["navy"], markersize=17, zorder=3)
                left.text(xi, y, str(ex.index(n) + 1), color="white", ha="center", va="center", fontsize=10.5, zorder=4)
            else:
                left.plot([xi], [y], "o", markerfacecolor="white", markeredgecolor=PALETTE["grey"], markersize=17, zorder=3)
                left.text(xi, y, "-", color=PALETTE["grey"], ha="center", va="center", fontsize=10.5, zorder=4)
    left.set_yticks(ys, nodes)
    left.set_xticks([0, 1], ["with the\nestimate", "zero\nestimate"])
    left.set_xlim(-0.6, 1.6)
    left.set_ylim(-0.7, len(nodes) - 0.3)
    left.set_xlabel("Search (number is the order expanded)")
    left.set_ylabel("Vertex")
    left.set_title(f"Expanded: {len(ex_i)} against {len(ex_z)}", fontsize=11.5)
    left.grid(alpha=0)
    xs = [0, 1]
    exp_time = [EXPANSION_MS * len(ex_i), t_zero]
    est_time = [price * inf["calls"], 0.0]
    right.bar(xs, exp_time, 0.55, color=[PALETTE["teal"], PALETTE["navy"]], edgecolor=PALETTE["ink"], linewidth=0.8)
    right.bar(xs, est_time, 0.55, bottom=exp_time, color="white", edgecolor=PALETTE["terracotta"], hatch="///", linewidth=1.0)
    for xi, a, b in zip(xs, exp_time, est_time):
        right.annotate(f"{num(a + b)} ms", (xi, a + b), xytext=(0, 3), textcoords="offset points", ha="center", va="bottom", fontsize=10.5)
    top = max(t_inf, t_zero)
    right.set_ylim(0, top * 1.25 + 50)
    right.set_xticks(xs, ["with the\nestimate", "zero\nestimate"])
    right.set_xlim(-0.6, 1.6)
    right.set_xlabel("Search (hatched: time spent computing estimates)")
    right.set_ylabel("Total time (ms)")
    right.set_title(f"Each estimate costs {num(price)} ms; each expansion {num(EXPANSION_MS)} ms", fontsize=11)
    right.grid(axis="x", alpha=0)

    if t_inf < t_zero - 1e-9:
        verdict = f"With the estimate the search is faster by {num(t_zero - t_inf)} ms."
        decision = "estimate pays"
    elif t_inf > t_zero + 1e-9 and saved > 0:
        verdict = (f"The estimate loses {num(t_inf - t_zero)} ms: the search that expands fewest vertices ({len(ex_i)}) is not the one that finishes "
                   f"soonest, which is the chapter's point that fewest expansions need not mean least total resources.")
        decision = "estimate loses"
    elif t_inf > t_zero + 1e-9:
        verdict = (f"The estimate loses {num(t_inf - t_zero)} ms: it saves no expansions, so its price is pure overhead "
                   f"(both searches expand {len(ex_i)} vertices).")
        decision = "estimate loses"
    else:
        verdict = "The two searches take the same time."
        decision = "equal"
    if identical:
        theorem = ("Both searches expand the identical set, which is the equality case of Theorem 2's corollary; the estimate saved no expansions, so "
                   "any price makes it pure overhead.")
    elif subset:
        theorem = (f"Every vertex expanded with the estimate is also expanded by the zero-estimate search ({names(ex_i)} inside {names(ex_z)}), "
                   "as Theorem 2's corollary says when the estimate is consistent and there are no ties.")
    else:
        theorem = "The expansion sets are not nested here."
    if zero_tie or inf_tie:
        theorem += (" A tie in score occurs in one of the runs, and Theorem 2 needs no ties, so the theorem does not apply to this "
                    "comparison as stated; the chapter's tie-break (smaller cost so far, then label) fixes the order.")
    metrics = {
        "Expansions, with and without": f"{len(ex_i)} and {len(ex_z)}",
        "Estimates computed": str(inf["calls"]),
        "Total time, with and without": f"{num(t_inf)} ms and {num(t_zero)} ms",
        "Break-even price per estimate": f"{num(break_even)} ms",
        "Verdict": decision,
    }
    interpretation = (
        f"Time with the estimate = {len(ex_i)} x {num(EXPANSION_MS)} + {inf['calls']} x {num(price)} = {num(t_inf)} ms; with the zero estimate "
        f"(free to compute) = {len(ex_z)} x {num(EXPANSION_MS)} = {num(t_zero)} ms. {verdict} Break-even price = {saved} x {num(EXPANSION_MS)} / "
        f"{inf['calls']} = {num(break_even)} ms per estimate. {theorem} Both return the same route cost, {num(inf['cost'])}."
    )
    worked = [
        f"Expansions: {len(ex_i)} with the {label} ({names(ex_i)}) and {len(ex_z)} with zero ({names(ex_z)}).",
        f"Estimates computed with the estimate: {inf['calls']} (one at the start, one each time a cheaper route is queued).",
        f"Time with the estimate = {len(ex_i)} x {num(EXPANSION_MS)} + {inf['calls']} x {num(price)} = {num(t_inf)} ms.",
        f"Time with zero = {len(ex_z)} x {num(EXPANSION_MS)} = {num(t_zero)} ms.",
        f"Expansions saved = {saved}; break-even price = {saved} x {num(EXPANSION_MS)} / {inf['calls']} = {num(break_even)} ms.",
        verdict,
    ]
    alt = (f"Left: a grid showing which vertices each search expands and in what order. Right: total time of the two searches; with the estimate "
           f"{num(t_inf)} ms against {num(t_zero)} ms for zero.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


CHAPTER = {
    "number": 9,
    "title": "Searching the Future",
    "subtitle": "A search needs a number for every branch it has not explored. What that number must satisfy, and what it costs to produce, decides what the search can promise.",
    "summary": (
        "These four demonstrations follow the chapter's A* search. First the chapter's own traces, one selection at a time. Then "
        "the condition that keeps the best route, tested on the chapter's graph and the notebook's graphs, then the condition that keeps "
        "the estimate consistent with itself, and finally what an estimate buys and what it costs. Each one changes a declared value "
        "and shows which part of the result moves."
    ),
    "ask_skill": {"prompt": (
        "On the graph S to A cost 1, A to G cost 4, S to B cost 2, B to G cost 1, with estimates S 3, A 4, B 10, G 0, run A*, "
        "audit whether the estimate is admissible and consistent, and tell me which path is returned and what the exact best cost is.")},
    "demos": [
        {
            "id": "C09-D01",
            "title": "Following the search one selection at a time",
            "question": "What does the search record, select and update at each step, and where does a recorded cost get corrected?",
            "equations": [EQ_FHAT],
            "symbols": (
                "g-hat(v) is the cost of the cheapest path to vertex v that the search has found so far (navy), h-hat(v) is the estimate of the "
                "cost still to come (hatched), and f-hat(v) their sum, the queue score. A selection removes the entry with the smallest score "
                "(ties: smaller g-hat, then label); an expansion generates its successors. A successor is updated only when an edge gives it a "
                "strictly lower cost. The three traces are the chapter's: four vertices with edge costs 3, 7, 2 and 3 (vertex B taken as the goal); "
                "the two-route graph with a zero estimate; and the research workflow with estimates 2, 1, 1, 0 (search 1 s, fetch 2 s, verify 4 s)."
            ),
            "prediction": "In the four-vertex trace, after A is expanded, does B's recorded cost stay at 7?",
            "prediction_options": ["Yes, 7 is the first cost found", "No, it falls to 6", "No, it rises to 8"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "A offers B the route 3 + 3 = 6, strictly below the record of 7, so B's record falls to 6 and no estimate was involved.",
                "incorrect": "Choose the bookkeeping graph and step to step 2: expanding A offers B the route 3 + 3 = 6, strictly below 7, so the record falls to 6.",
            },
            "explanation": (
                "Each step removes the cheapest queue entry and either stops at a goal or generates successors. The recorded cost only ever moves "
                "down toward the true cheapest cost, so that half of Equation (9.2) is bookkeeping; the estimate is the half that needs knowledge from "
                "outside. In the research workflow every action taken at the wrong stage is a self-loop with a higher cost for the same state, and the strict "
                "improvement rule discards it, so the frontier holds one useful state at a time."
            ),
            "application": (
                "When an agent reaches the same state by two sequences of tool calls, keep one best cost for that state and update it only when a "
                "strictly cheaper sequence appears. The record is then a trustworthy upper bound."
            ),
            "assumptions": (
                "Edge costs are fixed, known and positive, and a repeated vertex is the same state however it was reached. That fails when the cost "
                "of a step depends on the history, for example a deadline or a tool whose price changes with use. The bookkeeping graph names no goal in "
                "the chapter; B is taken as the goal here so that the trace ends."
            ),
            "check": "If the edge from A to B cost 2 and the direct edge from s to B cost 7, what would B's record become after A is expanded?",
            "answer": "3 + 2 = 5, which is strictly below 7, so the record falls to 5 and A becomes B's parent.",
            "provenance": "Constructed example: the chapter's four-vertex trace (edge costs 3, 7, 2 and 3, where 7 becomes 6), its two-route zero-estimate table and its research workflow (costs 1, 2, 4; estimates 2, 1, 1, 0), each checked against the laboratory's A* function.",
            "source_section": "The trace, worked",
            "source_anchor": "the-trace-worked",
            "misconception": {
                "title": "The recorded cost is a guess",
                "text": ("The chapter separates the two halves. The recorded cost is a record of work done: it can only be too high, and it falls when a cheaper "
                         "route turns up (7 becomes 6). The guess about what remains lives in the estimate."),
            },
            "scope_note": {
                "text": ("The worked guarantees here assume fixed, known positive edge costs. An agent can sometimes construct such a model, but uncertain "
                         "latency or history-dependent costs require additional modeling."),
                "source_section": "What this does not settle",
            },
            "stepper": "step",
            "controls": [
                {"key": "trace", "label": "Trace", "values": ["fig91", "zero", "flow"], "default": "fig91",
                 "value_labels": ["Four-vertex bookkeeping graph", "Two-route graph, zero estimate", "Research workflow, structural estimate"]},
                {"key": "step", "label": "Selection", "values": [1, 2, 3, 4], "default": 1,
                 "value_labels": ["1st", "2nd", "3rd", "4th"]},
            ],
            "function": "trace_picture",
        },
        {
            "id": "C09-D02",
            "title": "One overestimate can hide the cheaper route",
            "question": "How far can the estimate at one vertex exceed its true remaining cost before the search returns the dearer route, and which vertices does the exact f single out?",
            "equations": [EQ_TRUE, EQ_ADMISSIBLE],
            "symbols": (
                "g(v) is the cost of the best path from the start to v and h(v) the cost of the best path from v onward to a goal, so f(v) = g(v) + h(v) is the "
                "cost of the best route forced through v. h-hat(v) is the estimate. A queue score is cost so far plus estimate and the search removes the smallest first. "
                "The cases: the chapter's two-route graph (costs 1, 9, 1, 24; true remaining costs 9 at a and 24 at b), the notebook graph "
                "(S to A 1, A to G 4, S to B 2, B to G 1; true remaining cost 1 at B), and the notebook's transfer graph (2, 2 and a direct 7; true remaining cost 2 at the middle vertex). "
                "The estimate level is applied to the cheap route's first vertex."
            ),
            "prediction": "In the chapter's two-route graph the true remaining cost at a is 9. Set the estimate at a to its largest level, 25. Does the search return the cost-25 route?",
            "prediction_options": ["Yes, the cost-25 route", "No, the cost-10 route", "It returns nothing"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "The score of a is 1 + 25 = 26, above goal_b's 25, so goal_b is selected first and a stays on the queue: cost 25 against the best 10.",
                "incorrect": "Choose the two-route graph at the fourth level: a scores 1 + 25 = 26, goal_b scores 25 and is selected first, so the search returns cost 25.",
            },
            "explanation": (
                "A vertex is expanded only while its score is at or below the rival route's score. An estimate at or below the true remaining cost keeps it well inside "
                "that limit; one far above pushes it past, the rival goal is selected first and the cheap route is never examined. Between the two the condition is broken yet "
                "the best route can still come back, so the condition is a guarantee, not a symptom detector. The right panel shows Equation (9.1): f equals the optimal cost "
                "on every vertex of an optimal path and exceeds it everywhere else."
            ),
            "application": (
                "Before describing a search as optimal, ask whether any estimate in it can exceed the true remaining cost. One high estimate on the wrong branch is enough to lose "
                "the best route. The notebook's changed case and transfer case are the third and fourth levels of the notebook graph and the first level of the transfer graph."
            ),
            "assumptions": (
                "The graphs, costs and queue rules are fixed as stated. A broken Equation (9.3) can still return the best route, as the middle levels show, and on other graphs the "
                "threshold would differ. Ties in score are broken by smaller cost so far, then by label. Only one vertex's estimate is varied; the others keep the case's values."
            ),
            "check": "In the notebook graph the rival route through A reaches G at cost 5 and B has recorded cost 2. What is the largest estimate at B that still lets B be expanded before that goal is selected?",
            "answer": "B scores 2 + h-hat(B) and the goal scores 5, so h-hat(B) <= 3. At 3 the scores tie at 5 and B wins on smaller recorded cost (2 against 5). Above 3, the cost-5 route is returned although 3 was available.",
            "provenance": "Constructed example: the chapter's two-route graph (costs 1, 9, 1, 24), the laboratory notebook's default and changed graph (heuristic at B 1 and 10) and transfer graph (zero estimates), with other estimate levels defined for this reader; every search is also run through the laboratory's A* function.",
            "source_section": "The condition that makes it correct",
            "source_anchor": "the-condition-that-makes-it-correct",
            "misconception": {
                "title": "An overestimate always loses the best route",
                "text": ("The chapter says an overestimate need not cause a wrong answer on every graph; it removes the general guarantee. In the two-route graph an estimate "
                         "of 20 at a still returns the cost-10 route, and only 25 loses it."),
            },
            "scope_note": {
                "text": ("A learned predictor needs a certified uniform error bound over the relevant domain to justify claiming admissibility everywhere. "
                         "Subtracting the largest overshoot in a test set bounds those observed errors only; an unseen state can exceed it."),
                "source_section": "What the two conditions are really asking of a designer",
            },
            "controls": [
                {"key": "case", "label": "Graph", "values": ["tworoute", "notebook", "transfer"], "default": "tworoute",
                 "value_labels": ["Chapter two-route graph", "Notebook graph (default, changed)", "Notebook transfer graph"]},
                {"key": "level", "label": "Estimate at the cheap route's first vertex", "values": [0, 1, 2, 3], "default": 1,
                 "value_labels": ["Zero at this vertex", "Exact", "Over by a little", "Over by a lot"]},
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
                "and each edge is the cheapest way across, so the two coincide. The drop is h-hat(u) minus h-hat(v). The lower vertex's estimate is fixed at 5."
            ),
            "prediction": "Set the start's estimate to 8 and the estimate at the upper vertex to 1. Which vertex is selected first, and is its score below the start's estimate of 8?",
            "prediction_options": ["Lower vertex first, score 8", "Upper vertex first, score 7, below 8", "Upper vertex first, score 7, not below 8"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "The upper vertex scores 6 + 1 = 7 against 3 + 5 = 8, so it is selected first, and 7 is below the start's 8: the estimate fell by 7 across an edge costing 6.",
                "incorrect": "Set the start to 8 and the upper estimate to 1: the upper vertex scores 6 + 1 = 7, the lower 3 + 5 = 8, so the upper is first and its score is below 8.",
            },
            "explanation": (
                "Consistency says the estimate may not fall by more than the edge costs. Across the upper edge the start's estimate of 8 meets an edge cost of 6, so the upper vertex "
                "needs an estimate of at least 2. At 1 the estimate falls by 7 across a cost of 6, and the vertex's score of 7 dips below the start's own 8. The estimate may also stay "
                "unchanged across an edge: consistency limits the drop and does not require progress. The fragment shows the contradiction and nothing more."
            ),
            "application": (
                "When two estimates are produced separately for neighbouring states, compare their difference with the cost of the step between them. A difference larger than the step "
                "is a sign that the estimator disagrees with itself."
            ),
            "assumptions": (
                "Only the local fragment is drawn: no goal routes are shown, so it cannot tell you whether either estimate is admissible, which route is best, or whether a vertex will be "
                "reopened. A consistent estimate can still be wrong about the remaining cost; it only cannot be wrong in a self-contradicting way."
            ),
            "check": "If the start's estimate is 8 and the upper edge costs 4 instead of 6, what is the smallest estimate at the upper vertex that satisfies consistency?",
            "answer": "8 <= 4 + h-hat(upper) requires h-hat(upper) >= 8 - 4 = 4.",
            "provenance": "Constructed example: the chapter's consistency fragment (start estimate 8, edges costing 6 and 3, estimates 1 and 5), with the start's estimate and the upper estimate varied; the consistency flag is also checked with the laboratory's A* function.",
            "source_section": "The condition that makes it efficient",
            "source_anchor": "the-condition-that-makes-it-efficient",
            "misconception": {
                "title": "An inconsistent estimate means the route is wrong",
                "text": ("The chapter says the fragment shows a score decrease, not a suboptimal route or an actual reopening: selecting the first successor can still be "
                         "the right choice. Consistency prevents a kind of score reversal; it does not prove that an action advances the task."),
            },
            "scope_note": {
                "text": ("Without the onward paths to goals, it does not establish which route is optimal, whether the estimates are admissible, or whether any vertex will "
                         "need reopening."),
                "source_section": "The condition that makes it efficient",
            },
            "controls": [
                {"key": "h_upper", "label": "Estimate at the upper vertex", "values": [1, 2, 5, 8], "default": 1},
                {"key": "h_start", "label": "Estimate at the start", "values": [8, 7, 6], "default": 7},
            ],
            "function": "consistency_picture",
        },
        {
            "id": "C09-D04",
            "title": "What an estimate buys and what it costs",
            "question": "How many expansions does an estimate save compared with guessing zero, and does that pay once computing the estimate costs time?",
            "equations": [EQ_FHAT, EQ_CONSISTENT],
            "symbols": (
                "f-hat(v) = g-hat(v) + h-hat(v) must be computed for every vertex the search generates, and computing h-hat is not free. An expansion is one "
                "tool call and costs 200 milliseconds (ms); one estimate costs the chosen price. The zero estimate guesses 0 everywhere, costs nothing to compute and is "
                "admissible, so it turns A* into uniform-cost search. The informed estimate is the notebook's (3, 4, 1, 0), the two-route graph's exact values at a and b, or the "
                "research workflow's structural values (2, 1, 1, 0). Estimates computed is one at the start plus one each time a cheaper route to a vertex is queued."
            ),
            "prediction": "In the research workflow, how many expansions does the structural estimate save compared with the zero estimate?",
            "prediction_options": ["Three", "One", "None"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "Both searches select four vertices and expand three; duplicate merging has already removed the wasted alternatives, so the estimate saves nothing and any price is pure overhead.",
                "incorrect": "Choose the research workflow: both searches expand the same three vertices (s, found, fetched), so the structural estimate saves none.",
            },
            "explanation": (
                "Time is expansions times 200 ms plus estimates computed times the price. An admissible estimate always returns the same route cost as the zero estimate, and under Theorem 2's "
                "conditions it expands a subset of what the zero estimate expands; the saving is the difference. The estimate pays only while that saving, 200 ms per expansion avoided, exceeds "
                "what the estimates cost, so the search that expands the fewest vertices can be the slowest to finish."
            ),
            "application": (
                "Price the estimate in the same unit as the step it is meant to avoid. If scoring a candidate takes a model call, compare it with the tool call, and consider scoring candidates "
                "in batches or only when the choice is close."
            ),
            "assumptions": (
                "Constant costs per call, and expansion counts that come from these small graphs, not from measurement. Queue work, storage and batching are left out. The 200 ms figure and the "
                "900 ms estimate are the chapter's constructed example; 100 and 400 ms are values chosen for this reader. Theorem 2 compares algorithms with the same information, no ties and a "
                "consistent estimate."
            ),
            "check": "In the notebook graph the estimate saves one expansion and needs 4 estimates. What is the most one estimate may cost for the estimate to break even?",
            "answer": "1 x 200 / 4 = 50 ms per estimate. Above 50 ms the zero-estimate search is faster; below it the estimate pays.",
            "provenance": "Constructed example: the chapter's constructed agent latencies (a 200 ms tool call, a 900 ms estimate) applied to the notebook graph, the chapter's two-route graph and its research workflow, with expansions counted by the chapter's queue rules and checked against the laboratory's A* function.",
            "source_section": "When the estimate costs more than the vertex",
            "source_anchor": "when-the-estimate-costs-more-than-the-vertex",
            "misconception": {
                "title": "The search that expands the fewest vertices finishes soonest",
                "text": ("The chapter quotes the paper: the procedure that is optimal in minimum vertices expanded might not be optimal in minimum total resources expended, "
                         "because the estimate has to be computed whenever a vertex is generated."),
            },
            "scope_note": {
                "text": ("Theorem 2 holds only against algorithms with the same information, no ties, and a consistent estimate, which is a narrower class than the phrase optimal "
                         "search suggests."),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "graph", "label": "Graph and informed estimate", "values": ["notebook", "tworoute", "workflow"], "default": "notebook",
                 "value_labels": ["Notebook graph, exact estimate", "Two-route graph, exact estimate", "Research workflow, structural estimate"]},
                {"key": "price", "label": "Time to compute one estimate (ms)", "values": [0, 100, 400, 900], "default": 900},
            ],
            "function": "spending_picture",
        },
    ],
}

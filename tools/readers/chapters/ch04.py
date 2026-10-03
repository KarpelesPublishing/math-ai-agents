"""Chapter 4 reader: The Path from Prediction to Action.

Four demonstrations built on Equations (4.1) to (4.4) and the chapter's
constructed permission example. Demonstration 1 calls the laboratory's own
reachability function (math_ai_agents.chapters.ch04.evaluate) for the
document workflow and for the notebook's transfer workflow, so the reader, the
notebook and the chapter skill agree. Demonstrations 2 to 4 compute the
chapter's branching and chain-rule formulas directly. Every number is a
constructed teaching value; the book's own worked numbers are named where used.
"""
import math

import numpy as np
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyArrowPatch

from math_ai_agents.chapters.ch04 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure

EQ_REACH = r"\operatorname{Reach}_G(V_0)=\bigcup_{t\geq0}\operatorname{step}^{t}(V_0)."
EQ_ALLOWED = r"\operatorname{Allowed}_{\mathcal G}(v)=\mathcal{G}\bigl(\operatorname{Act}(v)\bigr)."
EQ_PERC = (r"\begin{gathered}\Pi_{G,v}(p)=\Pr_p\{|C_p(v)|=\infty\},\\"
           r"p_c(G,v)=\inf\{p:\Pi_{G,v}(p)>0\}.\end{gathered}")
EQ_THRESHOLD = r"p_c=\frac{1}{d}."
EQ_EXPECTED = r"(dp)^T"
EQ_EXISTS = r"1-[1-0.6(1-0.4^2)]^2=0.753984."
EQ_CHAIN = r"p = p_{\text{format}}\times p_{\text{parse}}\times p_{\text{grant}}\times p_{\text{tool}}."

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


def g(x):
    """Number for a written calculation: up to six significant digits, no trailing zeros."""
    text = f"{float(x):.6g}"
    return "0" if text == "-0" else text


def tiny(x, digits):
    """Probability text that never rounds a small positive value to zero: scientific notation below 0.001."""
    x = float(x)
    if 0 < abs(x) < 0.001:
        return f"{x:.3g}"
    return fmt(x, digits)


def near_one(x, miss, log10_x):
    """Text for a probability that may sit within rounding of 1 (written 1 - miss when miss is below 0.00001) or
    far below any decimal (written as a power of ten, because it is positive but underflows)."""
    if miss <= 0:
        return "1"
    if miss < 1e-5:
        return f"1 - {miss:.3g}"
    if log10_x < -100:
        exp10 = math.floor(log10_x)
        mantissa = float(f"{10 ** (log10_x - exp10):.2g}")
        if mantissa >= 10:
            mantissa, exp10 = 1.0, exp10 + 1
        return f"about {mantissa:g}e{exp10}"
    return tiny(x, 4)


def big(x):
    """Readable text for a count that may be very small or very large."""
    x = float(x)
    if x != 0 and (abs(x) < 0.001 or abs(x) >= 100000):
        return f"{x:.3g}"
    return fmt(x, 2 if abs(x) >= 10 else 3)


# Demonstration 1: reachability and the permission filter

DOC_NODES = ["draft", "review", "release", "archive"]
DOC_EDGES = [("draft", "review"), ("review", "release"), ("review", "draft"), ("draft", "archive")]
DOC_POSITIONS = {"draft": (0.0, 0.0), "review": (1.9, 0.85), "archive": (1.9, -0.85), "release": (3.8, 0.85)}
DOC_RADS = {("draft", "review"): 0.22, ("review", "draft"): 0.22, ("review", "release"): 0.0, ("draft", "archive"): 0.0}
# The notebook's transfer workflow: the first move is denied, the second is granted.
TRF_NODES = ["queued", "approved", "sent"]
TRF_EDGES = [("queued", "approved"), ("approved", "sent")]
TRF_POSITIONS = {"queued": (0.0, 0.0), "approved": (1.9, 0.0), "sent": (3.8, 0.0)}
TRF_RADS = {("queued", "approved"): 0.0, ("approved", "sent"): 0.0}

GRAPHS = {
    "document": {"nodes": DOC_NODES, "edges": DOC_EDGES, "positions": DOC_POSITIONS, "rads": DOC_RADS,
                 "start": "draft", "goal": "release", "name": "document workflow"},
    "transfer": {"nodes": TRF_NODES, "edges": TRF_EDGES, "positions": TRF_POSITIONS, "rads": TRF_RADS,
                 "start": "queued", "goal": "sent", "name": "transfer workflow"},
}
CASES = {
    "none": ("document", None),
    "review_release": ("document", ("review", "release")),
    "draft_review": ("document", ("draft", "review")),
    "transfer": ("transfer", ("queued", "approved")),
}
RADIUS = 0.42


def workflow(case):
    """The laboratory's input for one case: the chosen workflow with at most one move denied."""
    graph_key, gone = CASES[case]
    graph = GRAPHS[graph_key]
    return {
        "nodes": list(graph["nodes"]),
        "start": graph["start"],
        "goal": graph["goal"],
        "edges": [{"from": a, "to": b, "allowed": (a, b) != gone} for a, b in graph["edges"]],
    }


def layers_of(distances, nodes):
    """Group reached states by the fewest moves needed to reach them."""
    out = {}
    for node, k in distances.items():
        out.setdefault(k, []).append(node)
    return [sorted(out[k], key=nodes.index) for k in sorted(out)]


def draw_edge(ax, positions, a, b, allowed, rad):
    (xa, ya), (xb, yb) = positions[a], positions[b]
    length = math.hypot(xb - xa, yb - ya)
    ux, uy = (xb - xa) / length, (yb - ya) / length
    start = (xa + ux * (RADIUS + 0.04), ya + uy * (RADIUS + 0.04))
    end = (xb - ux * (RADIUS + 0.08), yb - uy * (RADIUS + 0.08))
    if allowed:
        ax.add_patch(FancyArrowPatch(
            start, end, arrowstyle="-|>", mutation_scale=17, linewidth=2.1, color=PALETTE["navy"],
            connectionstyle=f"arc3,rad={rad}", zorder=2,
        ))
        return
    # A denied move is drawn as a dashed line with a cross at its middle and a label beside it.
    ax.add_patch(FancyArrowPatch(
        start, end, arrowstyle="-", linewidth=2.1, color=PALETTE["terracotta"], linestyle=(0, (4, 3)),
        connectionstyle=f"arc3,rad={rad}", zorder=2,
    ))
    dx, dy = end[0] - start[0], end[1] - start[1]
    mx, my = (start[0] + end[0]) / 2 + 0.5 * rad * dy, (start[1] + end[1]) / 2 - 0.5 * rad * dx
    ax.plot([mx], [my], marker="X", markersize=12, markerfacecolor=PALETTE["terracotta"], markeredgecolor="white", zorder=4)
    if rad:
        nx, ny = rad * dy, -rad * dx  # the side the curve bulges toward
    else:
        nx, ny = -dy, dx
        if ny < 0:
            nx, ny = -nx, -ny
    norm = math.hypot(nx, ny)
    nx, ny = nx / norm, ny / norm
    ax.text(mx + 0.34 * nx, my + 0.34 * ny, "denied", color=PALETTE["terracotta"], fontsize=10.5, ha="center", va="center", zorder=4)


def permission_picture(denied="none"):
    graph_key, gone = CASES[denied]
    graph = GRAPHS[graph_key]
    nodes, edges, positions = graph["nodes"], graph["edges"], graph["positions"]
    out = evaluate(workflow(denied))
    distances = out["tables"]["authorized_distances"]
    path = out["metrics"]["authorized_path"]
    n_reached = out["metrics"]["authorized_count"]
    cumulative = out["series"][0]["y"]
    unfiltered = evaluate(workflow_all_granted(graph_key))["series"][0]["y"]

    fig, (picture, curve) = new_figure(ncols=2, height=4.2)
    picture.set_aspect("equal", adjustable="box")
    picture.set_xlim(-0.65, 4.3)
    picture.set_ylim(-1.85, 1.7)
    picture.axis("off")
    for a, b in edges:
        draw_edge(picture, positions, a, b, (a, b) != gone, graph["rads"][(a, b)])
    for node, (x, y) in positions.items():
        if node in distances:
            picture.add_patch(Circle((x, y), RADIUS, facecolor=PALETTE["teal"], edgecolor=PALETTE["ink"], linewidth=1.6, zorder=3))
            picture.text(x, y, f"{node}\nstep {distances[node]}", color="white", fontsize=10.5, ha="center", va="center", zorder=5, linespacing=1.15)
        else:
            picture.add_patch(Circle((x, y), RADIUS, facecolor="white", edgecolor=PALETTE["grey"], linewidth=1.6, linestyle="dashed",
                                     hatch="///", zorder=3))
            picture.text(x, y, f"{node}\nno path", color=PALETTE["ink"], fontsize=10.5, ha="center", va="center", zorder=5, linespacing=1.15,
                         bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "none", "alpha": 0.95})
    sx, sy = positions[graph["start"]]
    gx, gy = positions[graph["goal"]]
    picture.text(sx, sy + 0.6, "start", color=PALETTE["ink"], fontsize=10.5, ha="center", va="bottom")
    picture.text(gx, gy + 0.6, "goal", color=PALETTE["ink"], fontsize=10.5, ha="center", va="bottom")
    picture.text(1.8, -1.8, "solid arrow: permitted move; dashed line: denied move\nhatched circle: state not reached", color=PALETTE["ink"],
                 fontsize=10.5, ha="center", va="bottom", linespacing=1.3)
    title = "All moves granted" if gone is None else f"{gone[0].capitalize()} to {gone[1]} denied"
    picture.set_title(f"{graph['name'].capitalize()}: {title.lower()}" if graph_key == "transfer" else title, fontsize=11.5)

    x = np.arange(len(cumulative))
    curve.plot(x, unfiltered, color=PALETTE["grey"], linestyle=(0, (5, 3)), linewidth=2.2, marker="s", markersize=7)
    curve.plot(x, cumulative, color=PALETTE["teal"], marker="o", markersize=8)
    same = list(cumulative) == list(unfiltered)
    if same:
        label_point(curve, x[-1], unfiltered[-1], "all moves granted\n(same as these grants)", color=PALETTE["ink"], dx=-6, dy=-14, ha="right", va="top").set_bbox(BOX)
    else:
        label_point(curve, x[-1], unfiltered[-1], "all moves granted", color=PALETTE["grey"], dx=-6, dy=8, ha="right")
        label_point(curve, x[-1], cumulative[-1], "with these grants", color=PALETTE["teal"], dx=-6, dy=-10, ha="right", va="top").set_bbox(BOX)
    curve.set_xticks(x)
    curve.set_yticks(range(len(nodes) + 1))
    curve.set_xlim(-0.15, x[-1] + 0.15)
    curve.set_ylim(0, len(nodes) + 0.7)
    curve.set_xlabel("Step budget: most moves the controller may make")
    curve.set_ylabel("States it can reach")
    curve.set_title("Reach within a budget of k moves", fontsize=11.5)

    layers = layers_of(distances, nodes)
    sizes = [len(layer) for layer in layers]
    layer_lines = [
        (f"Step {k} holds {{{', '.join(layer)}}}." if k == 0 else f"Step {k} adds {{{', '.join(layer)}}}.") for k, layer in enumerate(layers)
    ]
    steps_text = "; ".join(
        (f"step {k} holds {{{', '.join(layer)}}}" if k == 0 else f"step {k} adds {{{', '.join(layer)}}}") for k, layer in enumerate(layers)
    )
    calc = (f"Reach = {' + '.join(str(s) for s in sizes)} = {n_reached} of {len(nodes)} states, "
            f"so states with no permitted path = {len(nodes)} - {n_reached} = {len(nodes) - n_reached}")
    if gone is None:
        filt = "Every grant is given, so Allowed(v) equals Act(v) at every state."
    else:
        a, b = gone
        acts = [y for x_, y in edges if x_ == a]
        kept = [y for y in acts if (a, y) != gone]
        keeps = f"keeps {{{', '.join(kept)}}}" if kept else "keeps no move"
        filt = (f"At {a}, Act({a}) = {{{', '.join(acts)}}}; the grant rule G {keeps}, "
                f"so the move {a} to {b} is deleted from the graph, not discouraged.")
    goal = graph["goal"]
    if path:
        goal_text = (f"{goal.capitalize()} is reached by {' to '.join(path)}, {len(path) - 1} moves, so a controller allowed fewer than "
                     f"{len(path) - 1} moves cannot reach it.")
    else:
        goal_text = (f"{goal.capitalize()} has no permitted path. With every grant given the path exists, so the missing piece is authority, "
                     "and no number of retries adds it.")
    cycle_text = ""
    if graph_key == "document" and "review" in distances and ("review", "draft") != gone:
        cycle_text = (" The permitted loop review to draft leads to a state already reached, so it adds no state and the search still ends.")
    budget_text = (f" Within 1 move the controller reaches {cumulative[1]} of {len(nodes)} states.") if len(cumulative) > 1 else ""
    interpretation = f"{steps_text}. {calc}.{budget_text} {filt} {goal_text}{cycle_text}"
    sinks = out["metrics"]["reachable_sinks"]
    metrics = {
        f"{goal.capitalize()} reachable with every grant": "yes" if out["metrics"]["raw_reachable"] else "no",
        f"{goal.capitalize()} reachable with these grants": "yes" if out["metrics"]["authorized_reachable"] else "no",
        "States reached": f"{n_reached} of {len(nodes)}",
        f"Shortest permitted path to {goal}": ", ".join(path) if path else "none",
        "Reached states with no way out": ", ".join(sorted(sinks, key=nodes.index)) if sinks else "none",
    }
    steps = layer_lines + [calc + ".", filt, goal_text]
    reached_names = ", ".join(sorted(distances, key=nodes.index))
    alt = (f"Left: the {graph['name']} with reached states filled and unreached states hatched; "
           f"{'no move is denied' if gone is None else 'the move ' + gone[0] + ' to ' + gone[1] + ' is crossed out'}. "
           f"Reached: {reached_names}. Right: the number of states reachable within each step budget, with and without the grants.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


def workflow_all_granted(graph_key):
    graph = GRAPHS[graph_key]
    return {
        "nodes": list(graph["nodes"]), "start": graph["start"], "goal": graph["goal"],
        "edges": [{"from": a, "to": b, "allowed": True} for a, b in graph["edges"]],
    }


# Demonstration 2: sampled finite trees against the infinite threshold

DEPTH = 4
# Four fixed draws (seeds chosen from 0 to 59 so that they differ): with edge probability p an edge is open when its
# uniform draw is below p, so the same draw is nested across the three probabilities.
SEEDS = {1: 8, 2: 6, 3: 3, 4: 15}
VERTICES = 2 ** (DEPTH + 1) - 1


def sample_tree(seed, p):
    """Open flags and reached flags for a binary tree of depth 4 (vertex 0 is the root, children of v are 2v+1 and 2v+2)."""
    draws = np.random.RandomState(seed).random_sample(VERTICES)
    open_edge = [False] + [bool(draws[v] < p) for v in range(1, VERTICES)]
    reached = [True] + [False] * (VERTICES - 1)
    for v in range(1, VERTICES):
        reached[v] = reached[(v - 1) // 2] and open_edge[v]
    return open_edge, reached


def reach_probability(p, depth):
    """Chance that some root-to-depth path of open edges exists in a binary tree: r_k = 1 - (1 - p r_(k-1))^2, r_0 = 1."""
    r = 1.0
    for _ in range(depth):
        r = 1 - (1 - p * r) ** 2
    return r


def survival(p, d):
    """Chance that the root's open cluster is infinite in the d-ary tree with edge probability p.

    Zero when d x p <= 1 (the chapter's threshold). Above it, one minus the smallest root of
    q = (1 - p + p q)^d, found by iterating the extinction recursion from q = 0.
    """
    if d * p <= 1 + 1e-12:
        return 0.0
    q = 0.0
    for _ in range(200000):
        nxt = (1 - p + p * q) ** d
        if abs(nxt - q) < 1e-15:
            q = nxt
            break
        q = nxt
    return 1.0 - q


def tree_xy():
    """Positions of the 31 vertices: leaves evenly spaced, each parent above the midpoint of its children."""
    xy = {}
    for i, v in enumerate(range(2 ** DEPTH - 1, VERTICES)):
        xy[v] = (float(i), -float(DEPTH))
    for v in range(2 ** DEPTH - 2, -1, -1):
        level = int(math.floor(math.log2(v + 1)))
        xy[v] = ((xy[2 * v + 1][0] + xy[2 * v + 2][0]) / 2, -float(level))
    return xy


def sample_picture(edge_probability=0.5, sample=1):
    p, sample = float(edge_probability), int(sample)
    seed = SEEDS[sample]
    open_edge, reached = sample_tree(seed, p)
    xy = tree_xy()
    leaves = range(2 ** DEPTH - 1, VERTICES)
    paths = sum(reached[v] for v in leaves)
    expected = (2 * p) ** DEPTH
    r = [reach_probability(p, k) for k in range(DEPTH + 1)]
    pi = survival(p, 2)
    committed = p ** DEPTH

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.axis("off")
    left.set_xlim(-0.8, 15.8)
    left.set_ylim(-DEPTH - 1.15, 0.6)
    for v in range(1, VERTICES):
        parent = (v - 1) // 2
        (x0, y0), (x1, y1) = xy[parent], xy[v]
        if open_edge[v]:
            left.plot([x0, x1], [y0, y1], color=PALETTE["teal"], linewidth=2.4 if reached[v] else 1.6, zorder=2,
                      alpha=1.0 if reached[v] else 0.55)
        else:
            left.plot([x0, x1], [y0, y1], color=PALETTE["light"], linewidth=1.2, linestyle=(0, (3, 3)), zorder=1)
    for v in range(VERTICES):
        x, y = xy[v]
        if reached[v]:
            left.plot([x], [y], "o", color=PALETTE["teal"], markersize=7.5, markeredgecolor=PALETTE["ink"], zorder=4)
        else:
            left.plot([x], [y], "o", color="white", markersize=6, markeredgecolor=PALETTE["grey"], zorder=3)
    for v in leaves:
        if reached[v]:
            left.plot([xy[v][0]], [xy[v][1]], "o", markersize=14, markerfacecolor="none", markeredgecolor=PALETTE["gold"],
                      markeredgewidth=2.2, zorder=5)
    left.text(7.5, 0.28, "root", ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
    left.text(7.5, -DEPTH - 0.55, "bottom row (depth 4)", ha="center", va="top", fontsize=10.5, color=PALETTE["ink"])
    left.text(7.5, -DEPTH - 1.1, "solid: open; faint: open but cut off; dashed: closed", ha="center", va="top", fontsize=10.5, color=PALETTE["grey"])
    plural = "path" if paths == 1 else "paths"
    left.set_title(f"p = {fmt(p, 2)}, draw {sample}: {paths} open {plural} to the bottom", fontsize=11.5)

    grid = np.linspace(0, 1, 201)
    right.plot(grid, [survival(float(v), 2) for v in grid], color=PALETTE["navy"], linewidth=2.2)
    right.plot(grid, [reach_probability(float(v), DEPTH) for v in grid], color=PALETTE["teal"], linewidth=2.2, linestyle=(0, (5, 2)))
    right.axvline(0.5, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    right.plot([p], [pi], "o", color=PALETTE["navy"], markersize=9, zorder=5)
    right.plot([p], [r[DEPTH]], "s", color=PALETTE["teal"], markersize=8, zorder=5)
    label_point(right, 0.74, survival(0.74, 2), "infinite tree", color=PALETTE["navy"], dx=8, dy=-10, ha="left", va="top")
    label_point(right, 0.62, reach_probability(0.62, DEPTH), "depth 4", color=PALETTE["teal"], dx=6, dy=-10, ha="left", va="top")
    label_point(right, 0.5, 1.0, "p_c = 1/2", color=PALETTE["ink"], dx=6, dy=-2, va="top").set_bbox(BOX)
    right.legend([Line2D([0], [0], color=PALETTE["navy"], linewidth=2.2, marker="o", markersize=7),
                  Line2D([0], [0], color=PALETTE["teal"], linewidth=2.2, linestyle=(0, (5, 2)), marker="s", markersize=7)],
                 ["infinite tree (circle)", "depth 4 (square)"], loc="center left", fontsize=10, frameon=False)
    right.set_xlim(0, 1)
    right.set_ylim(-0.03, 1.05)
    right.set_xlabel("Edge probability p")
    right.set_ylabel("Probability")
    right.set_title("Infinite survival is zero up to 1/2, then rises", fontsize=11.5)

    regime = "below" if p < 0.5 else ("at" if math.isclose(p, 0.5) else "above")
    metrics = {
        "Open paths to the bottom row in this draw": str(paths),
        "Expected open paths at depth 4, (dp)^4": fmt(expected, 3),
        "Chance a path to depth 4 exists": fmt(r[DEPTH], 3),
        "Chance one committed run finishes, p^4": fmt(committed, 4),
        "Chance the root's cluster is infinite": fmt(pi, 3),
        "Edge probability against 1/2": f"{regime} the threshold",
    }
    rec = "; ".join(
        f"r{k} = 1 - (1 - {g(p)} x {g(round(r[k - 1], 6))})^2 = {g(round(r[k], 6))}" for k in range(1, DEPTH + 1)
    )
    if p <= 0.5 + 1e-12:
        inf_text = f"The infinite tree has d x p = 2 x {g(p)} = {g(2 * p)}, not above 1, so its survival is 0 although this finite tree can still show a path."
    else:
        inf_text = (f"The infinite tree has d x p = 2 x {g(p)} = {g(2 * p)}, above 1, so its survival is positive ({fmt(pi, 3)}) but "
                    "not certain, and this finite draw can still show no path.")
    interpretation = (
        f"Expected open paths at depth 4 = (d x p)^4 = (2 x {g(p)})^4 = {fmt(expected, 3)}. The chance that at least one exists follows "
        f"r0 = 1 and r_k = 1 - (1 - p x r_(k-1))^2: {rec}. This draw shows {paths} {plural}; draws differ, so one drawing is not the regime. "
        f"The four drawings offered were chosen to differ, so how many of them show a path is not the chance r4 = {fmt(r[DEPTH], 3)}. {inf_text}"
    )
    steps = [
        f"Each open vertex has d = 2 possible children; an edge is open with p = {g(p)}.",
        f"Expected open vertices at depth 4 = (2 x {g(p)})^4 = {fmt(expected, 3)}.",
        f"Chance one branch gives a depth-k path: p x r_(k-1); two independent branches give r_k = 1 - (1 - p x r_(k-1))^2.",
        f"Starting at r0 = 1: r1 = {fmt(r[1], 3)}, r2 = {fmt(r[2], 3)}, r3 = {fmt(r[3], 3)}, r4 = {fmt(r[4], 3)}.",
        f"A committed run needs four particular edges open: p^4 = {g(p)}^4 = {fmt(committed, 4)}.",
        f"This draw shows {paths} open {plural} to the bottom row.",
        f"Infinite survival is {fmt(pi, 3)}: {'zero at or below 1/2' if p <= 0.5 + 1e-12 else 'positive above 1/2'}.",
    ]
    alt = (f"Left: a binary tree of depth 4 drawn with edge probability {fmt(p, 2)} (draw {sample}); {paths} {plural} of open edges "
           f"reach the bottom row. Right: two curves against edge probability, the infinite-tree survival that is zero up to one half "
           f"and the smooth chance of a depth-4 path, with this probability marked.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: possible, expected and completed are three numbers

def path_probability(p, d):
    """Chance an open path to depth two exists in a d-ary tree: the chapter's binary formula, generalized."""
    branch = p * (1 - (1 - p) ** d)
    return 1 - (1 - branch) ** d


def completion_picture(children=2, edge_probability=0.6):
    d, p = int(children), float(edge_probability)
    q = 1 - p
    inner = 1 - q ** d
    branch = p * inner
    exists = path_probability(p, d)
    committed = p * p
    expected = d * d * p * p
    grid = np.linspace(0, 1, 101)
    exists_curve = np.array([path_probability(float(v), d) for v in grid])

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.plot(grid, exists_curve, color=PALETTE["teal"])
    left.plot(grid, grid ** 2, color=PALETTE["navy"], linestyle=(0, (5, 2)))
    left.plot([p], [exists], "o", color=PALETTE["teal"], markersize=9, zorder=5)
    left.plot([p], [committed], "s", color=PALETTE["navy"], markersize=8, zorder=5)
    label_point(left, 0.5, path_probability(0.5, d), "a path exists", color=PALETTE["teal"], dx=-4, dy=8, ha="right").set_bbox(BOX)
    label_point(left, 0.62, 0.62 ** 2, "committed run", color=PALETTE["navy"], dx=8, dy=-6, ha="left", va="top").set_bbox(BOX)
    left.set_xlim(0, 1)
    left.set_ylim(0, 1.1)
    left.set_xlabel("Probability p that each edge is open")
    left.set_ylabel("Probability")
    left.set_title(f"Depth two, {d} children per vertex", fontsize=11.5)

    right.plot(grid, d * d * grid ** 2, color=PALETTE["gold"])
    right.axhline(1.0, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    right.plot([p], [expected], "D", color=PALETTE["gold"], markersize=8, zorder=5)
    label_point(right, p, expected, fmt(expected, 2), color=PALETTE["gold"], dx=-8, dy=8, ha="right").set_bbox(BOX)
    label_point(right, 0.02, 1.0, "1 descendant", color=PALETTE["grey"], dx=2, dy=6, ha="left").set_bbox(BOX)
    right.set_xlim(0, 1)
    right.set_ylim(0, d * d * 1.08)
    right.set_xlabel("Probability p that each edge is open")
    right.set_ylabel("Expected open depth-two descendants")
    right.set_title("An expected count, not a probability", fontsize=11.5)

    metrics = {
        "Expected open depth-two descendants (d^2 x p^2)": fmt(expected, 2),
        "A path to depth two exists": fmt(exists, 6),
        "Committed run finishes (p^2)": fmt(committed, 2),
        "Existence minus committed run": fmt(exists - committed, 6),
    }
    if (d, p) == (2, 0.6):
        note = " This is the chapter's constructed example."
    elif d == 2:
        note = f" Same reasoning as the chapter's binary example (two children), with p changed to {g(p)}."
    elif p == 0.6:
        note = " Same reasoning as the chapter's binary example, with the child count changed to 3."
    else:
        note = f" Same reasoning as the chapter's binary example, with the child count changed to {d} and p changed to {g(p)}."
    if expected < 1 and exists > 0:
        reading = (f"The expected count {fmt(expected, 2)} is below 1, yet a path exists with probability {fmt(exists, 6)}: "
                   "a small average does not rule out a path.")
    else:
        reading = (f"The expected count {fmt(expected, 2)} is a count, not a probability: it can exceed 1 while the chance of a path "
                   f"stays at {fmt(exists, 6)}.")
    interpretation = (
        f"Each root branch supplies a path with probability p x (1 - (1 - p)^{d}) = {g(p)} x (1 - {g(q)}^{d}) = {g(p)} x {g(inner)} = {g(branch)}. "
        f"The {d} branches are independent, so a path exists with probability 1 - (1 - {g(branch)})^{d} = 1 - {g((1 - branch) ** d)} = {g(exists)}. "
        f"A controller that commits to one branch per level succeeds with p^2 = {g(p)} x {g(p)} = {g(committed)}. "
        f"Expected open depth-two descendants = d^2 x p^2 = {d * d} x {g(committed)} = {g(expected)}. {reading}{note}"
    )
    steps = [
        f"A branch needs its first edge open ({g(p)}) and at least one of {d} lower edges open: 1 - {g(q)}^{d} = {g(inner)}.",
        f"One branch supplies a path with probability {g(p)} x {g(inner)} = {g(branch)}.",
        f"The {d} branches are independent: a path exists with probability 1 - (1 - {g(branch)})^{d} = {g(exists)}.",
        f"A committed run needs two particular edges open: {g(p)} x {g(p)} = {g(committed)}.",
        f"Expected open depth-two descendants = {d * d} x {g(committed)} = {g(expected)}.",
    ]
    alt = (f"Left: the chance that a path to depth two exists and the chance that a committed run finishes, both against edge probability, "
           f"with p = {g(p)} marked ({fmt(exists, 3)} and {fmt(committed, 2)}). Right: the expected number of open depth-two descendants "
           f"({fmt(expected, 2)} at this p) against edge probability, with a reference line at 1.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: the edge probability is a product of four rates, and what repeated failure shows

FORMAT, PARSE, TOOL = 0.95, 0.98, 0.80
CHILDREN = 2
STAGES = ["Format", "Parse", "Grant", "Tool"]
RUNS = np.logspace(0, 4, 400)   # a dense log grid so the curve is smooth and ends exactly at 10,000 runs


def chain_picture(grant=0.9, steps=3):
    grant, steps = float(grant), int(steps)
    rates = [FORMAT, PARSE, grant, TOOL]
    cumulative = np.cumprod(rates)
    p = float(cumulative[-1])
    mean = CHILDREN * p
    pc = 1.0 / CHILDREN
    chain = p ** steps
    count = mean ** steps
    book_mean = CHILDREN * FORMAT * PARSE * 0.9 * TOOL
    ratio = (0.9 / grant) ** steps if grant > 0 else None
    break_even = pc / (FORMAT * PARSE * TOOL)
    all_fail_10 = math.exp(10 * math.log1p(-chain))
    all_fail_10k = math.exp(10000 * math.log1p(-chain))
    miss_10 = -math.expm1(10 * math.log1p(-chain))      # 1 - all_fail, kept exact when it is tiny
    miss_10k = -math.expm1(10000 * math.log1p(-chain))
    t10 = near_one(all_fail_10, miss_10, 10 * math.log10(1 - chain))
    t10k = near_one(all_fail_10k, miss_10k, 10000 * math.log10(1 - chain))

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    y = np.arange(len(STAGES))[::-1]
    for yi, c, stage in zip(y, cumulative, STAGES):
        left.barh(yi, c, height=0.58, color=PALETTE["teal"], hatch="///" if stage == "Grant" else None,
                  edgecolor="white" if stage != "Grant" else PALETTE["ink"], linewidth=1.0)
        left.text(c + 0.02, yi, fmt(c, 3), va="center", fontsize=10.5, color=PALETTE["ink"])
    if grant == 0:
        # With a grant rate of 0 the hatched bar has no width; say so beside it.
        left.text(0.16, y[STAGES.index("Grant")], "grant rate 0:\nedge removed", va="center", fontsize=10.5, color=PALETTE["ink"],
                  linespacing=1.15, bbox=BOX)
    left.set_yticks(y, [f"{s} {fmt(r, 2)}" for s, r in zip(STAGES, rates)])
    left.set_xlim(0, 1.18)
    left.set_xlabel("Probability the call has passed this stage")
    left.set_ylabel("Stage and its rate")
    left.set_title("Stage by stage (hatched: grant)", fontsize=11.5)
    left.grid(axis="y", alpha=0)

    right.axhline(1.0, color=PALETTE["grey"], linestyle=(0, (5, 3)), linewidth=1.6)
    right.plot(RUNS, (1 - chain) ** RUNS, color=PALETTE["navy"], linewidth=2.2)
    right.plot([10, 10000], [all_fail_10, all_fail_10k], "o", color=PALETTE["terracotta"], markersize=8, zorder=5)
    right.set_xscale("log")
    right.set_xlim(0.8, 14000)
    right.set_ylim(-0.04, 1.12)
    label_point(right, 1, 1.0, "no path: every run fails", color=PALETTE["grey"], dx=4, dy=5, ha="left")
    if all_fail_10 > 0.5:
        label_point(right, 10, all_fail_10, f"10 runs:\n{t10}", color=PALETTE["terracotta"], dx=4, dy=-10, ha="left", va="top",
                    ).set_bbox(BOX)
    else:
        label_point(right, 10, all_fail_10, f"10 runs: {t10}", color=PALETTE["terracotta"], dx=8, dy=8, ha="left", va="bottom").set_bbox(BOX)
    if all_fail_10k > 0.5:
        label_point(right, 10000, all_fail_10k, f"10,000 runs:\n{t10k}", color=PALETTE["terracotta"], dx=-4, dy=-10, ha="right", va="top").set_bbox(BOX)
    elif all_fail_10k > 0.001:
        # Beside the marker, on the empty side of the falling curve, so the label never hides the curve's last stretch.
        label_point(right, 10000, all_fail_10k, f"10,000 runs:\n{t10k}", color=PALETTE["terracotta"], dx=-10, dy=0, ha="right", va="center").set_bbox(BOX)
    else:
        label_point(right, 10000, all_fail_10k, f"10,000 runs:\n{t10k}", color=PALETTE["terracotta"], dx=-6, dy=10, ha="right", va="bottom").set_bbox(BOX)
    right.set_xlabel("Number of runs, every one a failure (log scale)")
    right.set_ylabel("Chance all of them fail")
    right.set_title(f"One run = a chain of {steps} steps", fontsize=11.5)

    if mean > 1 + 1e-12:
        regime = "above the threshold"
    elif math.isclose(mean, 1.0, abs_tol=1e-12):
        regime = "exactly at the threshold"
    else:
        regime = "below the threshold"
    metrics = {
        "Edge success p": fmt(p, 5),
        "Open children per vertex (d x p, d = 2)": fmt(mean, 5),
        "Against the threshold 1/d = 0.5": regime,
        f"Expected open descendants at depth {steps} ((dp)^{steps})": big(count),
        f"One chain of {steps} steps (p^{steps})": tiny(chain, 5),
        "Chance 10 runs in a row all fail": t10,
        "Chance 10,000 runs in a row all fail": t10k,
        "Grant rate that gives d x p = 1": fmt(break_even, 4),
    }
    calc = f"p = 0.95 x 0.98 x {fmt(grant, 2)} x 0.80 = {fmt(p, 5)}, so d x p = 2 x {fmt(p, 5)} = {fmt(mean, 5)}"
    if grant == 0:
        body = (f"{calc}. A grant rate of 0 means the permission is absent, so the edge does not exist: p^{steps} = 0 and every run fails, "
                f"so 10 failures in a row have probability (1 - 0)^10 = 1 and so do 10,000. That is a structural failure, and retries cannot help.")
    else:
        side = {"above the threshold": "above 1, above the threshold in the binary-tree model",
                "below the threshold": "below 1, below the threshold in the binary-tree model",
                "exactly at the threshold": "exactly 1, at the threshold"}[regime]
        body = (f"{calc}, which is {side}. The expected open descendants at depth {steps} are {fmt(mean, 5)}^{steps} = {big(count)}, while one "
                f"chain of {steps} steps succeeds with probability p^{steps} = {fmt(p, 5)}^{steps} = {tiny(chain, 5)}. If each run is such a chain, "
                f"10 failures in a row have probability (1 - {tiny(chain, 5)})^10 = {t10} and 10,000 have {t10k}")
        if all_fail_10k > 0.5:
            body += ", close to the value 1 of a missing path: a log of failures cannot tell the two apart."
        else:
            body += ": here a long run of identical failures would be strong evidence against this model."
        if steps and grant != 0.9:
            ratio_text = f"{ratio / 1e6:.3f} million" if ratio >= 1e6 else big(ratio)
            body += (f" Against the book's grant rate of 0.90, the expected count at depth {steps} is smaller by "
                     f"(0.90 / {fmt(grant, 2)})^{steps} = {ratio_text}.")
    if steps == 20 and math.isclose(grant, 0.9):
        body += (f" The chapter rounds the mean to 1.34 and quotes about 348 at depth 20; the unrounded mean {fmt(mean, 5)} gives {big(count)}.")
    elif steps == 20 and math.isclose(grant, 0.4):
        body += (f" The chapter rounds the mean to 0.596 and quotes about 0.000032 at depth 20; the unrounded mean {fmt(mean, 5)} gives {big(count)}.")
    interpretation = (f"{body} The grant rate that puts d x p at exactly 1 is 0.5 / (0.95 x 0.98 x 0.80) = 0.5 / 0.7448 = "
                      f"{fmt(break_even, 4)}; a stricter review that lowers the grant rate below that value moves the model below the threshold.")
    steps_list = [
        f"Stage rates: format 0.95, parse 0.98, grant {fmt(grant, 2)}, tool 0.80, each given the earlier stages.",
        f"Edge success p = 0.95 x 0.98 x {fmt(grant, 2)} x 0.80 = {fmt(p, 5)}.",
        f"Open children per vertex d x p = 2 x {fmt(p, 5)} = {fmt(mean, 5)}, compared with 1.",
        f"Expected open descendants at depth {steps} = {fmt(mean, 5)}^{steps} = {big(count)}.",
        f"One chain of {steps} steps: p^{steps} = {tiny(chain, 5)}.",
        f"Ten failures in a row: (1 - {tiny(chain, 5)})^10 = {t10}; a missing path gives exactly 1.",
    ]
    alt = (f"Left: horizontal bars for the chance a call has passed the format, parse, grant and tool stages, ending at {fmt(p, 3)}. "
           f"Right: the chance that a growing number of runs all fail, from 1 to 10,000 runs, against a dashed line at 1 for a missing path; "
           f"for a chain of {steps} steps the values at 10 and 10,000 runs are {t10} and {t10k}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps_list}


CHAPTER = {
    "number": 4,
    "title": "The Path from Prediction to Action",
    "subtitle": "An agent can describe an action without having a route to perform it. Check the route before reading the success rate.",
    "summary": (
        "These four demonstrations follow the chapter's controller graph. The first shows how a permission deletes a move and everything "
        "beyond it, on the document workflow and on the notebook's transfer workflow. The next three separate numbers that are easy to confuse: "
        "what a finite drawing of a random tree can and cannot show about a threshold, whether a path exists, is expected or is completed in "
        "a small tree, and how a product of four rates makes a missing path look like a rare one."
    ),
    "ask_skill": {
        "prompt": (
            "A controller fails every time on one task. List its states and moves, mark which moves have a grant, find the shortest "
            "permitted path from the real start state, and say whether the failure looks structural (no allowed path) or probabilistic "
            "(a path exists but was not completed)."
        ),
    },
    "demos": [
        {
            "id": "C04-D01",
            "title": "A permission deletes a move, and the path with it",
            "question": "If one permission is removed, which states can the controller still reach, and does the goal survive?",
            "equations": [EQ_REACH, EQ_ALLOWED],
            "symbols": (
                "V_0 is the set of starting states (here one state). step^t(V_0) is the set of states reached after exactly t allowed "
                "moves, with step^0(V_0) = V_0, and Reach is the union over every t, so a state counts if at least one allowed path "
                "reaches it. Act(v) is the set of actions the model might emit at state v, G is the permission system, and Allowed(v) is "
                "what survives it. A step number below a state is the fewest moves needed to reach it. The step budget is the most moves the controller may make."
            ),
            "prediction": "Deny the move from review to release. Can the controller still reach release, and which states remain reachable?",
            "prediction_options": [
                "Yes: archive gives another route to release",
                "No: release is lost, but draft, review and archive are still reached",
                "No: only draft is still reached",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Release has no permitted path, and draft, review and archive remain: 1 + 2 = 3 of 4 states.",
                "incorrect": "Choose 'Review to release' in the selector: archive is a dead end, so release has no permitted path, and draft, review and archive remain (3 of 4 states).",
            },
            "explanation": (
                "Each state lists what the model might do next; the grant rule keeps a subset, and the kept moves are the only edges "
                "of the graph. The reachable set grows one move at a time from the start state, so a denied move removes the state behind "
                "it unless another permitted route leads there. The right panel counts how many states are reached within each step budget, "
                "so a controller allowed too few moves loses a state even when a path exists. The notebook's transfer workflow shows the "
                "sharpest case: the permitted move into sent cannot help, because the state it leaves is never reached."
            ),
            "application": (
                "When a task fails every time, list the states and moves, mark which moves the controller has a grant for, and search "
                "from the real start state before tuning prompts. A missing grant shows up in the list of states and moves; a prompt cannot add it."
            ),
            "assumptions": (
                "Grants are frozen at analysis time, each arrow stands for a mechanism that really exists, and states are coarse labels. "
                "Reachable does not mean likely, cheap or safe, and it does not show that an action happened. If a label hides a distinction the "
                "system depends on, such as which evidence a draft holds, the drawn path can be one the real controller does not have."
            ),
            "check": (
                "Suppose a new state, audit, can only be entered from release. With the move from review to release denied, is audit reachable, "
                "and how many states does the controller reach in all?"
            ),
            "answer": (
                "No. Audit sits behind release, and release has no permitted path, so audit is unreachable too. The reached states are draft, "
                "review and archive, so 1 + 2 = 3 of the 5 states."
            ),
            "provenance": (
                "Constructed example: the laboratory's four-state document workflow (draft, review, release, archive), whose denied review to "
                "release case is the notebook's changed case, and the notebook's transfer workflow (queued, approved, sent). Counts come from the "
                "laboratory's reachability function."
            ),
            "source_section": "Permission is a filter, not an opinion",
            "source_anchor": "permission-is-a-filter-not-an-opinion",
            "misconception": {
                "title": "A zero score means a weak model",
                "text": (
                    "A model that succeeds 2 percent of the time and a controller that cannot attempt the task both report as failing. The first is "
                    "a probability problem that more sampling or a stronger model may fix; the second is a reachability problem that nothing "
                    "of that kind touches. Check the graph before reading the score."
                ),
            },
            "scope_note": {
                "text": (
                    "A path existing means a path exists: it carries no claim that the path is likely, cheap, safe or correct. The graph is also a "
                    "chosen abstraction, so a label that hides a distinction the system depends on can draw a route the real system does not have."
                ),
                "source_section": "What the graph cannot say",
            },
            "controls": [
                {"key": "denied", "label": "Workflow and denied move", "values": ["none", "review_release", "draft_review", "transfer"],
                 "default": "none",
                 "value_labels": ["Document: every move granted", "Document: review to release denied", "Document: draft to review denied",
                                  "Transfer: queued to approved denied"]},
            ],
            "function": "permission_picture",
        },
        {
            "id": "C04-D02",
            "title": "A finite drawing is not the threshold",
            "question": "At edge probabilities below, at and above the threshold, what does one sampled tree show, and how does that differ from the infinite tree?",
            "equations": [EQ_PERC, EQ_THRESHOLD],
            "symbols": (
                "Each vertex of the binary tree has d = 2 possible children, and an edge to a child is open with probability p, independently. "
                "The root's open cluster is the set of vertices joined to the root by open edges; Pi(p) is the chance that this cluster is infinite and "
                "p_c = 1/d is the smallest p at which that chance is positive. The drawn tree has depth 4, so it has 16 vertices in its bottom row. "
                "r_k is the chance that some open path from the root reaches depth k. The expected number of open vertices at depth 4 is (dp)^4."
            ),
            "prediction": "At p = 0.30, below the threshold of 1/2, can a sampled depth-4 tree show an open path from the root to the bottom row?",
            "prediction_options": [
                "No: below the threshold nothing can reach the bottom",
                "Yes: a finite sample can show one, although the infinite tree dies out",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Draw 3 at p = 0.30 shows an open path. A finite tree can; only the infinite tree's survival is zero below 1/2.",
                "incorrect": "Set p to 0.30 and look at draw 3: it shows an open path to the bottom. The threshold concerns the infinite tree, not a finite drawing.",
            },
            "explanation": (
                "Each open vertex has d x p open children on average, so the expected count at depth T is (dp)^T, which is smooth in p. The chance "
                "that a depth-4 path exists is also smooth in p, built one level at a time. Only the infinite tree has a sharp change: its survival "
                "is zero up to p = 1/2 and positive above. The four draws use the same underlying random numbers at every p, so raising p only opens "
                "more edges, yet different draws disagree at the same p."
            ),
            "application": (
                "When someone shows one picture of a small random graph as evidence of a regime, ask for the probability law and the depth. A drawing "
                "can look connected below a threshold and broken above it; the threshold describes the law, not the drawing."
            ),
            "assumptions": (
                "A binary tree with independent open edges and a depth of 4. The four draws are fixed random draws, picked from seeds 0 to 59 so "
                "that they differ; they are not a measurement. The threshold 1/2 belongs to this graph shape, and real tool failures often share "
                "causes, which breaks independence."
            ),
            "check": "In a binary tree with p = 0.5, what is the expected number of open vertices at depth 4, and is the infinite tree's survival positive?",
            "answer": "(2 x 0.5)^4 = 1^4 = 1.000 open vertex on average, and survival is 0 because d x p = 1 is not above 1.",
            "provenance": (
                "Constructed example: the chapter's finite samples of an independent binary tree below, at and above the branching threshold "
                "(Figure 4.3), here with edge probabilities 0.3, 0.5 and 0.7 and four fixed draws defined for this reader."
            ),
            "source_section": "How many edges are enough",
            "source_anchor": "how-many-edges-are-enough",
            "misconception": {
                "title": "Reading one drawing as the regime",
                "text": (
                    "The number of displayed paths is random in every panel, and finite trees do not deterministically depict infinite-survival regimes. "
                    "A drawing below the threshold can show a path and a drawing above it can show none."
                ),
            },
            "scope_note": {
                "text": (
                    "The threshold 1/d belongs to a regular tree; other graph families have their own thresholds, and this value does not carry over. "
                    "The independence assumption is a simplification real systems violate."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "edge_probability", "label": "Edge probability p", "values": [0.3, 0.5, 0.7], "default": 0.5,
                 "value_labels": ["0.30 (below 1/2)", "0.50 (at 1/2)", "0.70 (above 1/2)"]},
                {"key": "sample", "label": "Random draw", "values": [1, 2, 3, 4], "default": 1},
            ],
            "function": "sample_picture",
        },
        {
            "id": "C04-D03",
            "title": "Possible, expected and completed are three numbers",
            "question": "In a small tree, how different are the chance that a path exists, the expected number of open descendants and the chance that a committed controller finishes?",
            "equations": [EQ_EXISTS, EQ_EXPECTED],
            "symbols": (
                "p is the chance that each edge is open, independently, and d is the number of children per vertex; the tree has depth two. "
                "A path exists when at least one chain of open edges runs from the root to depth two. A committed run picks one branch at "
                "each level before learning whether its edge is open and stops at the first closed edge. The expected count is a mean "
                "number of open depth-two descendants, not a probability. The tree has depth two, so (dp)^T with T = 2 is (dp)^2 = "
                "d^2 x p^2. The displayed existence equation is the chapter's instance (d = 2, p = 0.6); the general formula the "
                "demonstration computes is 1 - [1 - p(1 - (1 - p)^d)]^d."
            ),
            "prediction": "Set p to 0.4 with 2 children. Is the expected number of open depth-two descendants above or below 1, and is a path then impossible?",
            "prediction_options": [
                "Below 1 (0.64), yet a path exists with probability about 0.45",
                "Below 1, so a path is impossible",
                "Above 1, so a path is certain",
            ],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "4 x 0.4^2 = 0.64 is below 1, and a path still exists with probability 0.446464.",
                "incorrect": "Choose p = 0.4 with 2 children: the expected count is 0.64, below 1, but the chance of a path is 0.446464. An average does not rule a path out, and above 1 would not make it certain either.",
            },
            "explanation": (
                "A branch supplies a path when its first edge is open and at least one of its d children edges is open. The d branches are "
                "independent, so a path exists unless all of them fail. A committed run needs two particular edges open, which has "
                "probability p x p. The expected count multiplies the d x d possible depth-two vertices by p^2. The three quantities answer "
                "different questions."
            ),
            "application": (
                "When someone reports that a search or a tool graph has many possible paths, ask which number they mean: that a route exists, how "
                "many are open on average, or how often the actual controller completes one. Each needs different information."
            ),
            "assumptions": (
                "Independent open edges and depth two. An exhaustive search can realize the existence probability only if it can test every "
                "needed edge, revisit branching states and afford the budget; those are extra assumptions. The three-child case applies the chapter's reasoning "
                "to a new child count; it is not a number from the book."
            ),
            "check": "In the binary tree with p = 0.5, what is the committed-run probability, the expected number of open depth-two descendants, and the chance that a path exists?",
            "answer": (
                "Committed: 0.5^2 = 0.25. Expected count: 4 x 0.25 = 1.00. Existence: each branch gives 0.5 x (1 - 0.5^2) = 0.375, so "
                "1 - (1 - 0.375)^2 = 1 - 0.390625 = 0.609375."
            ),
            "provenance": (
                "Constructed example: the chapter's binary tree of depth two with p = 0.6 (expected count 1.44, existence 0.753984, committed run 0.36), "
                "with p and the child count varied by the same formulas."
            ),
            "source_section": "Reachability, expected descendants, and completion",
            "source_anchor": "reachability-expected-descendants-and-completion",
            "misconception": {
                "title": "Treating the expected count as a chance of finishing",
                "text": (
                    "The number of open descendants at depth T has expectation (dp)^T. That count is neither the probability that a path exists nor the "
                    "controller's completion probability, and it is not a grant of free exploration."
                ),
            },
            "scope_note": {
                "text": (
                    "A controller's completion probability depends on which branches it explores, what it observes and its budget; the existence "
                    "probability is realized only if the controller can test all necessary edges, revisit branching states and afford the search."
                ),
                "source_section": "Reachability, expected descendants, and completion",
            },
            "controls": [
                {"key": "children", "label": "Children per vertex d", "values": [2, 3], "default": 2},
                {"key": "edge_probability", "label": "Edge probability p", "values": [0.4, 0.6, 0.8], "default": 0.6},
            ],
            "function": "completion_picture",
        },
        {
            "id": "C04-D04",
            "title": "Four rates make one edge, and failure logs cannot tell rare from missing",
            "question": "How does tightening one stage, the grant, change the edge probability, the threshold test, the growth of descendants and what a long run of identical failures shows?",
            "equations": [EQ_CHAIN, EQ_THRESHOLD, EQ_EXPECTED],
            "symbols": (
                "p is the chance that one attempted call produces a usable next state. p_format is the chance the call is well formed, p_parse "
                "that the parser accepts it given that, p_grant that the permission system grants it given the earlier stages, and p_tool "
                "that the tool returns a usable response given all earlier stages. d x p compares p with the binary-tree threshold 1/d = 0.5. "
                "(dp)^T is the expected number of open descendants at depth T, while p^T is the chance that one chosen chain of T steps succeeds. "
                "A run here is one such chain; the right panel is the chance that n runs in a row all fail."
            ),
            "prediction": "The book lowers the grant rate from 0.90 to 0.40. By roughly what factor does the edge probability p fall, and does d x p stay above 1?",
            "prediction_options": [
                "p falls by about 2.25 times, and d x p falls below 1",
                "p falls by about 2.25 times, and d x p stays above 1",
                "p falls by about 5 times, and d x p falls below 1",
            ],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "p goes from 0.67032 to 0.29792, a factor of 0.90 / 0.40 = 2.25, and d x p goes from 1.34064 to 0.59584, below 1.",
                "incorrect": "Compare the grant rates 0.90 and 0.40 in the selector: p scales with the grant rate, 0.90 / 0.40 = 2.25, so p goes from 0.67032 to 0.29792 and d x p from 1.34064 to 0.59584, below 1.",
            },
            "explanation": (
                "Because each rate is conditional on the stages before it, the chain rule multiplies them without assuming independence. "
                "Lowering the grant rate scales p by the same factor, so p falls from 0.67032 to 0.29792 when the grant drops from 0.90 to 0.40, "
                "and d x p crosses from above 1 to below 1. A grant rate of 0 removes the edge outright. Over a chain of T steps the success "
                "probability p^T is tiny whenever p is modest, so many failures in a row look the same whether the chain is rare or absent."
            ),
            "application": (
                "Before a safety review tightens a grant, write the four rates and compute where d x p lands against the threshold. A change "
                "that looks like a modest percentage can move the model across 1/d, and repeating a chain of steps multiplies the loss. When the logs "
                "show only failures, inspect the grants and the transition rules: the pattern of failures alone cannot establish that no path exists."
            ),
            "assumptions": (
                "Constructed rates, an idealized binary tree with independent edges, and a controller that follows one chain. The product gives "
                "smooth finite-horizon sensitivity, not a discontinuity; the threshold concerns the infinite-depth model only. Real tools may share failure causes, "
                "and real graphs merge or loop. Treating each run as an independent chain with success p^T is a constructed simplification."
            ),
            "check": "With the grant rate at 0.60 and the other rates as shown, is d x p above or below 1?",
            "answer": "p = 0.95 x 0.98 x 0.60 x 0.80 = 0.44688 and d x p = 2 x 0.44688 = 0.89376, which is below 1. This matches 0.60 being under the break-even grant rate of 0.6713.",
            "provenance": (
                "Constructed example: the chapter's rates (0.95, 0.98, 0.80), its grant rates of 0.90 and 0.40 and its depth-twenty ratio (0.90 / 0.40)^20, "
                "about 11.057 million; the grant rates 0.70 and 0 and the chain lengths 3 and 10 are values defined for this reader."
            ),
            "source_section": "The permission graph, with numbers",
            "source_anchor": "the-permission-graph-with-numbers",
            "misconception": {
                "title": "Identical failures prove the edge is missing",
                "text": (
                    "Identical failures can reflect a poor policy, a rare event or a missing route, and a finite run of identical failures does not "
                    "establish that no path exists. Inspect the actual grants and transitions before concluding that a route is absent."
                ),
            },
            "scope_note": {
                "text": (
                    "The worked permission numbers are constructed, and their independence assumption is a simplification real systems violate. Products "
                    "of conditional success rates create strong finite-horizon sensitivity without a discontinuity or a universal threshold."
                ),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "grant", "label": "Grant rate p_grant", "values": [0.9, 0.7, 0.4, 0.0], "default": 0.9},
                {"key": "steps", "label": "Steps T in one chain", "values": [3, 10, 20], "default": 3},
            ],
            "function": "chain_picture",
        },
    ],
}

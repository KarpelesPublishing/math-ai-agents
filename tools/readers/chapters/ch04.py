"""Chapter 4 reader: The Path from Prediction to Action.

Four demonstrations built on Equations (4.1) to (4.4) and the chapter's
constructed permission example. Demonstration 1 calls the laboratory's own
reachability function (math_ai_agents.chapters.ch04.evaluate), so the reader,
the notebook and the chapter skill agree. Demonstrations 2 to 4 compute the
chapter's branching and chain-rule formulas directly. Every number is a
constructed teaching value; the book's own worked numbers are named where used.
"""
import math

import numpy as np
from matplotlib.patches import Circle, FancyArrowPatch

from math_ai_agents.chapters.ch04 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure

EQ_REACH = r"\operatorname{Reach}_G(V_0)=\bigcup_{t\geq0}\operatorname{step}^{t}(V_0)."
EQ_ALLOWED = r"\operatorname{Allowed}_{\mathcal G}(v)=\mathcal{G}\bigl(\operatorname{Act}(v)\bigr)."
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


def big(x):
    """Readable text for a count that may be very small or very large."""
    x = float(x)
    if x != 0 and (abs(x) < 0.001 or abs(x) >= 100000):
        return f"{x:.3g}"
    return fmt(x, 2 if abs(x) >= 10 else 3)


# Demonstration 1: reachability and the permission filter

NODES = ["draft", "review", "release", "archive"]
EDGES = [("draft", "review"), ("review", "release"), ("review", "draft"), ("draft", "archive")]
DENIALS = {
    "none": None,
    "review_release": ("review", "release"),
    "draft_review": ("draft", "review"),
    "draft_archive": ("draft", "archive"),
}
POSITIONS = {"draft": (0.0, 0.0), "review": (1.9, 0.85), "archive": (1.9, -0.85), "release": (3.8, 0.85)}
RADIUS = 0.42


def workflow(denied):
    """The laboratory's four-state document workflow, with at most one move denied."""
    gone = DENIALS[denied]
    return {
        "nodes": list(NODES),
        "start": "draft",
        "goal": "release",
        "edges": [{"from": a, "to": b, "allowed": (a, b) != gone} for a, b in EDGES],
    }


def layers_of(distances):
    """Group reached states by the fewest moves needed to reach them."""
    out = {}
    for node, k in distances.items():
        out.setdefault(k, []).append(node)
    return [sorted(out[k], key=NODES.index) for k in sorted(out)]


def draw_edge(ax, a, b, allowed, rad):
    (xa, ya), (xb, yb) = POSITIONS[a], POSITIONS[b]
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
    out = evaluate({**workflow(denied)})
    distances = out["tables"]["authorized_distances"]
    path = out["metrics"]["authorized_path"]
    n_reached = out["metrics"]["authorized_count"]
    cumulative = out["series"][0]["y"]
    unfiltered = evaluate(workflow("none"))["series"][0]["y"]
    gone = DENIALS[denied]

    fig, (graph, curve) = new_figure(ncols=2, height=4.2)
    graph.set_aspect("equal", adjustable="box")
    graph.set_xlim(-0.65, 4.3)
    graph.set_ylim(-1.85, 1.7)
    graph.axis("off")
    rads = {("draft", "review"): 0.22, ("review", "draft"): 0.22, ("review", "release"): 0.0, ("draft", "archive"): 0.0}
    for a, b in EDGES:
        draw_edge(graph, a, b, (a, b) != gone, rads[(a, b)])
    for node, (x, y) in POSITIONS.items():
        if node in distances:
            graph.add_patch(Circle((x, y), RADIUS, facecolor=PALETTE["teal"], edgecolor=PALETTE["ink"], linewidth=1.6, zorder=3))
            graph.text(x, y, f"{node}\nstep {distances[node]}", color="white", fontsize=10.5, ha="center", va="center", zorder=5, linespacing=1.15)
        else:
            graph.add_patch(Circle((x, y), RADIUS, facecolor="white", edgecolor=PALETTE["grey"], linewidth=1.6, linestyle="dashed",
                                   hatch="///", zorder=3))
            graph.text(x, y, f"{node}\nno path", color=PALETTE["ink"], fontsize=10.5, ha="center", va="center", zorder=5, linespacing=1.15,
                       bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "none", "alpha": 0.95})
    graph.text(0.0, 0.6, "start", color=PALETTE["ink"], fontsize=10.5, ha="center", va="bottom")
    graph.text(3.8, 1.35, "goal", color=PALETTE["ink"], fontsize=10.5, ha="center", va="bottom")
    graph.text(1.8, -1.8, "solid arrow: permitted move; dashed line: denied move\nhatched circle: state not reached", color=PALETTE["ink"],
               fontsize=10.5, ha="center", va="bottom", linespacing=1.3)
    title = "All moves granted" if gone is None else f"{gone[0].capitalize()} to {gone[1]} denied"
    graph.set_title(title, fontsize=11.5)

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
    curve.set_xlim(-0.15, x[-1] + 0.15)
    curve.set_ylim(0, 4.7)
    curve.set_xlabel("Step budget: most moves the controller may make")
    curve.set_ylabel("States it can reach")
    curve.set_title("Reach within a budget of k moves", fontsize=11.5)

    layers = layers_of(distances)
    sizes = [len(layer) for layer in layers]
    steps = "; ".join(
        (f"step {k} holds {{{', '.join(layer)}}}" if k == 0 else f"step {k} adds {{{', '.join(layer)}}}") for k, layer in enumerate(layers)
    )
    calc = f"Reach = {' + '.join(str(s) for s in sizes)} = {n_reached} of {len(NODES)} states"
    if gone is None:
        filt = "Every grant is given, so Allowed(v) equals Act(v) at every state."
    else:
        a, b = gone
        acts = [y for x_, y in EDGES if x_ == a]
        kept = [y for y in acts if (a, y) != gone]
        filt = (f"At {a}, Act({a}) = {{{', '.join(acts)}}}; the grant rule G keeps {{{', '.join(kept) if kept else 'nothing'}}}, "
                f"so the move {a} to {b} is deleted from the graph, not discouraged.")
    if path:
        goal_text = (f"Release is reached by {' to '.join(path)}, {len(path) - 1} moves, so a controller allowed fewer than "
                     f"{len(path) - 1} moves cannot reach it.")
    else:
        goal_text = ("Release has no permitted path. With every grant given the path exists, so the missing piece is authority, "
                     "and no number of retries adds it.")
    interpretation = f"{steps}. {calc}. {filt} {goal_text}"
    sinks = out["metrics"]["reachable_sinks"]
    metrics = {
        "Release reachable with every grant": "yes" if out["metrics"]["raw_reachable"] else "no",
        "Release reachable with these grants": "yes" if out["metrics"]["authorized_reachable"] else "no",
        "States reached": f"{n_reached} of {len(NODES)}",
        "Shortest permitted path to release": ", ".join(path) if path else "none",
        "Reached states with no way out": ", ".join(sorted(sinks, key=NODES.index)) if sinks else "none",
    }
    return fig, metrics, interpretation


# Demonstration 2: the branching threshold p_c = 1/d

DEPTHS = np.arange(0, 21)


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


def threshold_picture(children=2, edge_probability=0.67032):
    d, p = int(children), float(edge_probability)
    mean = d * p
    pc = 1.0 / d
    counts = mean ** DEPTHS
    surv = survival(p, d)
    grid = np.linspace(0, 1, 201)
    curve_y = np.array([survival(float(v), d) for v in grid])

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.plot(DEPTHS, counts, color=PALETTE["teal"], marker="o", markersize=4.5)
    left.axhline(1.0, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    left.set_yscale("log")
    left.set_ylim(1e-6, 1e7)
    left.set_xlim(0, 20.5)
    left.set_xticks([0, 5, 10, 15, 20])
    if math.isclose(mean, 1.0, abs_tol=1e-12):
        label_point(left, 20, 1.0, f"d x p = {g(mean)}: stays at 1", color=PALETTE["teal"], dx=-6, dy=8, ha="right").set_bbox(BOX)
    elif mean > 1:
        label_point(left, 10, counts[10], f"d x p = {g(mean)}", color=PALETTE["teal"], dx=-8, dy=12, ha="right", va="bottom").set_bbox(BOX)
        label_point(left, 0.3, 1.0, "1 descendant", color=PALETTE["grey"], dx=0, dy=-5, ha="left", va="top").set_bbox(BOX)
    else:
        (label_point(left, 8, counts[8], f"d x p = {g(mean)}", color=PALETTE["teal"], dx=12, dy=12, ha="left", va="bottom") if mean < 0.8 else
         label_point(left, 10, counts[10], f"d x p = {g(mean)}", color=PALETTE["teal"], dx=8, dy=-12, ha="left", va="top")).set_bbox(BOX)
        label_point(left, 0.3, 1.0, "1 descendant", color=PALETTE["grey"], dx=0, dy=6, ha="left").set_bbox(BOX)
    left.set_xlabel("Depth T (number of moves)")
    left.set_ylabel("Expected open descendants (log scale)")
    left.set_title("Expected descendants (dp)^T", fontsize=11.5)

    right.plot(grid, curve_y, color=PALETTE["navy"])
    right.axvline(pc, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    right.plot([p], [surv], "o", color=PALETTE["teal"], markersize=9, zorder=5)
    label_point(right, pc, 1.0, f"1/d = {fmt(pc, 2)}", color=PALETTE["ink"], dx=6, dy=-2, va="top").set_bbox(BOX)
    if surv < 0.1:
        label_point(right, p, surv, fmt(surv, 3), color=PALETTE["teal"], dx=8, dy=10, ha="left").set_bbox(BOX)
    else:
        label_point(right, p, surv, fmt(surv, 3), color=PALETTE["teal"], dx=10, dy=-12, ha="left", va="top").set_bbox(BOX)
    right.set_xlim(0, 1)
    right.set_ylim(-0.03, 1.05)
    right.set_xlabel("Edge probability p")
    right.set_ylabel("Chance the root's cluster is infinite")
    right.set_title(f"Survival with {d} children per vertex", fontsize=11.5)

    final = counts[-1]
    if math.isclose(mean, 1.0, abs_tol=1e-12):
        regime = "exactly at the threshold"
        verdict = (f"Exactly at the threshold: d x p = 1, so the expected count stays at 1 at every depth, yet the root's cluster "
                   "still dies out with probability 1. An expected count of 1 is not a survival probability.")
    elif mean < 1:
        regime = "below the threshold"
        verdict = (f"Below the threshold ({g(p)} < {g(pc)}): the root's cluster dies out with probability 1, and the expected count "
                   f"falls to about {big(final)} by depth 20. That does not make every finite target unreachable.")
    else:
        regime = "above the threshold"
        verdict = (f"Above the threshold ({g(p)} > {g(pc)}): survival has positive probability, here {fmt(surv, 3)}, which is not "
                   f"certainty. The expected count grows to about {big(final)} by depth 20.")
    metrics = {
        "Threshold p_c = 1/d": fmt(pc, 3),
        "Expected open children per vertex (d x p)": fmt(mean, 5),
        "Regime": regime,
        "Expected open descendants at depth 20": big(final),
        "Chance the root's cluster is infinite": fmt(surv, 3),
    }
    interpretation = (f"p_c = 1/d = 1/{d} = {fmt(pc, 3)}. Expected open children per open vertex = d x p = {d} x {g(p)} = {fmt(mean, 5)}, "
                      f"so the expected count at depth T is {fmt(mean, 5)}^T, which is {big(final)} at T = 20. {verdict}")
    if d == 2 and math.isclose(p, 0.67032):
        interpretation += (" The chapter rounds the mean to 1.34 and quotes about 348 at depth 20; the unrounded mean "
                           f"{fmt(mean, 5)} gives {big(final)}.")
    elif d == 2 and math.isclose(p, 0.29792):
        interpretation += (" The chapter rounds the mean to 0.596 and quotes about 0.000032 at depth 20; the unrounded mean "
                           f"{fmt(mean, 5)} gives {big(final)}.")
    return fig, metrics, interpretation


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
    return fig, metrics, interpretation


# Demonstration 4: the edge probability is a product of four rates

FORMAT, PARSE, TOOL = 0.95, 0.98, 0.80
CHILDREN = 2
STAGES = ["Format", "Parse", "Grant", "Tool"]


def chain_picture(grant=0.9, steps=3):
    grant, steps = float(grant), int(steps)
    rates = [FORMAT, PARSE, grant, TOOL]
    cumulative = np.cumprod(rates)
    p = float(cumulative[-1])
    mean = CHILDREN * p
    pc = 1.0 / CHILDREN
    chain = p ** steps
    break_even = pc / (FORMAT * PARSE * TOOL)

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

    t = np.arange(1, 13)
    right.plot(t, p ** t, color=PALETTE["navy"], marker="o", markersize=4.5)
    right.plot([steps], [chain], "o", color=PALETTE["terracotta"], markersize=10, zorder=5)
    label_point(right, steps, chain, tiny(chain, 4), color=PALETTE["terracotta"], dx=8, dy=10, ha="left").set_bbox(BOX)
    if grant == 0:
        right.text(6.5, 0.3, "grant rate 0: the edge does not exist,\nso every chain has probability 0", ha="center", va="center",
                   fontsize=10.5, color=PALETTE["ink"], linespacing=1.2, bbox=BOX)
    right.set_xlim(0.5, 12.5)
    right.set_ylim(-0.04, 1.08)
    right.set_xticks([1, 3, 5, 7, 9, 11])
    right.set_xlabel("Steps T in one chain")
    right.set_ylabel("Chance one chain succeeds (p^T)")
    right.set_title(f"A chain of {steps} steps", fontsize=11.5)

    if mean > pc * CHILDREN + 1e-12:
        regime = "above the threshold"
    elif math.isclose(mean, 1.0, abs_tol=1e-12):
        regime = "exactly at the threshold"
    else:
        regime = "below the threshold"
    metrics = {
        "Edge success p": fmt(p, 5),
        "Open children per vertex (d x p, d = 2)": fmt(mean, 5),
        "Against the threshold 1/d = 0.5": regime,
        f"One chain of {steps} steps (p^{steps})": tiny(chain, 5),
        "Grant rate that gives d x p = 1": fmt(break_even, 4),
    }
    calc = f"p = 0.95 x 0.98 x {fmt(grant, 2)} x 0.80 = {fmt(p, 5)}, so d x p = 2 x {fmt(p, 5)} = {fmt(mean, 5)}"
    if grant == 0:
        body = (f"{calc}. A grant rate of 0 means the permission is absent, so the edge does not exist: p^{steps} = 0 for every chain "
                "length and retries cannot help. That is a structural failure, not a probabilistic one.")
    else:
        side = {"above the threshold": f"above 1, above the threshold in the binary-tree model",
                "below the threshold": "below 1, below the threshold in the binary-tree model",
                "exactly at the threshold": "exactly 1, at the threshold"}[regime]
        body = (f"{calc}, which is {side}. One chain of {steps} steps succeeds with probability p^{steps} = {fmt(p, 5)}^{steps} = "
                f"{tiny(chain, 5)}.")
    interpretation = (f"{body} The grant rate that puts d x p at exactly 1 is 0.5 / (0.95 x 0.98 x 0.80) = 0.5 / 0.7448 = "
                      f"{fmt(break_even, 4)}; a stricter review that lowers the grant rate below that value moves the model below the threshold.")
    return fig, metrics, interpretation


CHAPTER = {
    "number": 4,
    "title": "The Path from Prediction to Action",
    "subtitle": "An agent can describe an action without having a route to perform it. Check the route before reading the success rate.",
    "summary": (
        "These four demonstrations follow the chapter's controller graph. The first shows how a permission deletes a move and everything "
        "beyond it. The next three separate three numbers that are easy to confuse: whether a route can survive, whether a path exists in a "
        "small tree, and how often a single attempt gets through a chain of stages."
    ),
    "demos": [
        {
            "id": "C04-D01",
            "title": "A permission deletes a move, and the path with it",
            "question": "If one permission is removed, which states can the controller still reach, and does the goal survive?",
            "equations": [EQ_REACH, EQ_ALLOWED],
            "symbols": (
                "V_0 is the set of starting states (here only draft). step^t(V_0) is the set of states reached after exactly t allowed "
                "moves, with step^0(V_0) = V_0, and Reach is the union over every t, so a state counts if at least one allowed path "
                "reaches it. Act(v) is the set of actions the model might emit at state v, G is the permission system, and Allowed(v) is "
                "what survives it. A step number below a state is the fewest moves needed to reach it. The step budget is the most moves the controller may make."
            ),
            "prediction": "Deny the move from review to release. Can the controller still reach release, and how many of the four states remain reachable?",
            "explanation": (
                "Each state lists what the model might do next; the grant rule keeps a subset, and the kept moves are the only edges "
                "of the graph. The reachable set grows one move at a time from the start state, so a denied move removes the state behind "
                "it unless another permitted route leads there. The right panel counts how many states are reached within each step budget."
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
                "Constructed example: the laboratory's four-state document workflow (draft, review, release, archive); the denied review to "
                "release case is the laboratory notebook's changed case. Counts come from the laboratory's reachability function."
            ),
            "source_section": "Permission is a filter, not an opinion",
            "source_anchor": "permission-is-a-filter-not-an-opinion",
            "controls": [
                {"key": "denied", "label": "Which move is denied", "values": ["none", "review_release", "draft_review", "draft_archive"],
                 "default": "none",
                 "value_labels": ["None: every move granted", "Review to release", "Draft to review", "Draft to archive"]},
            ],
            "function": "permission_picture",
        },
        {
            "id": "C04-D02",
            "title": "One threshold: when can a branching route survive?",
            "question": "How does the edge probability compare with the threshold, and what does that say about the expected number of open descendants?",
            "equations": [EQ_THRESHOLD, EQ_EXPECTED],
            "symbols": (
                "d is the number of children each vertex has and p is the chance that each edge to a child is open, independently. p_c is the "
                "critical probability, 1/d. d x p is the expected number of open children of an open vertex. If Z_T is the number of open "
                "descendants at depth T, then E[Z_T] = (dp)^T, the quantity in the second displayed expression. The right panel shows the chance that the cluster of open edges around the root never ends."
            ),
            "prediction": "With 2 children, set p to 0.5. Does the expected number of open descendants grow, shrink or stay flat, and does the root's cluster survive?",
            "explanation": (
                "Each open vertex has d possible children, each open with probability p, so it has d x p open children on average and the "
                "expected count is multiplied by d x p at every level. Above p_c = 1/d that factor exceeds 1 and survival has positive "
                "probability; at or below it the cluster dies out with probability 1. The survival curve is computed from the standard "
                "extinction recursion for this branching process."
            ),
            "application": (
                "When you must say whether a route can keep branching, compute d x p for the declared model and compare it with 1. "
                "If a design change moves p across 1/d, expect a qualitative change; if it moves p within one side, expect smaller changes."
            ),
            "assumptions": (
                "An infinite tree with the same number of children at every vertex and independent open edges. The threshold 1/d belongs "
                "to this graph shape and does not carry over to other graphs. The worked numbers are constructed, and real tool failures "
                "often share causes, which breaks independence."
            ),
            "check": "A tree has 4 children per vertex and each edge is open with probability 0.2. Is it above or below the threshold, and what is the expected count at depth 10?",
            "answer": "p_c = 1/4 = 0.25 and d x p = 4 x 0.2 = 0.8, so it is below the threshold. The expected count at depth 10 is 0.8^10 = 0.107.",
            "provenance": (
                "Constructed example: the edge probabilities 0.67032 and 0.29792 are the chapter's working and tightened-permission cases for "
                "two children per vertex; 0.5 and the three-child tree are values defined for this reader."
            ),
            "source_section": "How many edges are enough",
            "source_anchor": "how-many-edges-are-enough",
            "controls": [
                {"key": "children", "label": "Children per vertex d", "values": [2, 3], "default": 2},
                {"key": "edge_probability", "label": "Edge probability p", "values": [0.29792, 0.5, 0.67032], "default": 0.67032},
            ],
            "function": "threshold_picture",
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
            "controls": [
                {"key": "children", "label": "Children per vertex d", "values": [2, 3], "default": 2},
                {"key": "edge_probability", "label": "Edge probability p", "values": [0.4, 0.6, 0.8], "default": 0.6},
            ],
            "function": "completion_picture",
        },
        {
            "id": "C04-D04",
            "title": "The edge probability is a product of four rates",
            "question": "How does tightening one stage, the grant, change the edge probability, the threshold test and the success of a chain of steps?",
            "equations": [EQ_CHAIN, EQ_THRESHOLD],
            "symbols": (
                "p is the chance that one attempted call produces a usable next state. p_format is the chance the call is well formed, p_parse "
                "that the parser accepts it given that, p_grant that the permission system grants it given the earlier stages, and p_tool "
                "that the tool returns a usable response given all earlier stages. d x p compares p with the binary-tree threshold 1/d = 0.5. "
                "A chain of T steps succeeds with probability p^T."
            ),
            "prediction": "The book lowers the grant rate from 0.90 to 0.40. By roughly what factor does the edge probability p fall, and does d x p stay above 1?",
            "explanation": (
                "Because each rate is conditional on the stages before it, the chain rule multiplies them without assuming independence. "
                "Lowering the grant rate scales p by the same factor, so p falls from 0.67032 to 0.29792 when the grant drops from 0.90 to 0.40, "
                "and d x p crosses from above 1 to below 1. A grant rate of 0 removes the edge outright."
            ),
            "application": (
                "Before a safety review tightens a grant, write the four rates and compute where d x p lands against the threshold. A change "
                "that looks like a modest percentage can move the model across 1/d, and repeating a chain of steps multiplies the loss."
            ),
            "assumptions": (
                "Constructed rates, an idealized binary tree with independent edges, and a controller that follows one chain. The product gives "
                "smooth finite-horizon sensitivity, not a discontinuity; the threshold concerns the infinite-depth model only. Real tools may share failure causes, "
                "and real graphs merge or loop."
            ),
            "check": "With the grant rate at 0.60 and the other rates as shown, is d x p above or below 1?",
            "answer": "p = 0.95 x 0.98 x 0.60 x 0.80 = 0.44688 and d x p = 2 x 0.44688 = 0.89376, which is below 1. This matches 0.60 being under the break-even grant rate of 0.6713.",
            "provenance": (
                "Constructed example: the chapter's rates (0.95, 0.98, 0.80) and its grant rates of 0.90 and 0.40; the grant rates 0.70 and 0 "
                "and the chain lengths are values defined for this reader."
            ),
            "source_section": "The permission graph, with numbers",
            "source_anchor": "the-permission-graph-with-numbers",
            "controls": [
                {"key": "grant", "label": "Grant rate p_grant", "values": [0.9, 0.7, 0.4, 0.0], "default": 0.9},
                {"key": "steps", "label": "Steps T in one chain", "values": [3, 10], "default": 3},
            ],
            "function": "chain_picture",
        },
    ],
}

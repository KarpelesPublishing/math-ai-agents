"""Chapter 8 reader: Acting in the Dark.

Four demonstrations built on Equations (8.1) to (8.5). All call the laboratory's
own belief-and-information function (math_ai_agents.chapters.ch08.evaluate), so
the reader, the notebook and the chapter skill agree; each result is also checked
against a hand calculation.

D01 the belief update stepped through prior, prediction and correction, for the
    chapter's corridor (one and two moves) and the notebook default and
    transfer cases.
D02 the same report under different instruments (the chapter's runner, the
    notebook's informative and aliased sensors).
D03 a belief valued by its best plan: alpha vectors, the one-bit memories and
    the costly detour (8.2, 8.3, 8.4).
D04 the value of one report against belief and price (8.5): the chapter's
    verification tool and the notebook cases, with a break-even price.
Every number is a constructed teaching value.
"""
import math

import numpy as np

from math_ai_agents.chapters.ch08 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed, undefined

from readerkit import PALETTE, fmt, label_point, new_figure, signed

# Equation (8.1), tag dropped, copied from the chapter.
EQ_UPDATE = (
    r"\mathbf{b}_{t+1}(x') \;=\;"
    "\n"
    r"\frac{\begin{gathered}"
    "\n"
    r"\operatorname{Obs}(o\mid x',a)\\"
    "\n"
    r"\cdot\sum_{x\in\mathcal{X}}P(x'\mid x,a)\,\mathbf{b}_t(x)"
    "\n"
    r"\end{gathered}}"
    "\n"
    r"{\begin{gathered}"
    "\n"
    r"\sum_{x''\in\mathcal{X}}\operatorname{Obs}(o\mid x'',a)\\"
    "\n"
    r"\cdot\sum_{x\in\mathcal{X}}P(x''\mid x,a)\,\mathbf{b}_t(x)"
    "\n"
    r"\end{gathered}}."
)
EQ_CORRIDOR = (
    r"T_E=\begin{pmatrix}"
    "\n"
    r"0.1&0.9&0&0\\"
    "\n"
    r"0.1&0&0.9&0\\"
    "\n"
    r"0&0.1&0&0.9\\"
    "\n"
    r"0&0&0.1&0.9"
    "\n"
    r"\end{pmatrix},\qquad"
    "\n"
    r"\operatorname{Obs}(\text{non-goal}\mid x')=(1,1,0,1)."
)
EQ_REWARD = r"\bar r(\mathbf{b},a)\;=\;\sum_{x\in\mathcal{X}}\mathbf{b}(x)\,r(x,a)."
EQ_VOI = (
    r"\begin{aligned}"
    "\n"
    r"\operatorname{VOI}(O)"
    "\n"
    r"&=\sum_{o}\Pr(o\mid\mathbf{b})\,"
    "\n"
    r"\max_{a\in\mathcal{A}}\bar r\big(\mathbf{b}'(\mathbf{b},o),a\big)\\"
    "\n"
    r"&\quad-\max_{a\in\mathcal{A}}\bar r(\mathbf{b},a)."
    "\n"
    r"\end{aligned}"
)

EQ_BELIEF_VALUE = (
    r"\begin{aligned}"
    "\n"
    r"V(\mathbf{b})"
    "\n"
    r"&=\max_{a\in\mathcal{A}}\Big[\,\bar r(\mathbf{b},a)\\"
    "\n"
    r"&\quad+\gamma\sum_{o}\Pr(o\mid \mathbf{b},a)\,"
    "\n"
    r"V\big(\mathbf{b}'(\mathbf{b},a,o)\big)\Big]."
    "\n"
    r"\end{aligned}"
)
EQ_ALPHA = r"V_H(\mathbf b)=\max_{\alpha\in\Gamma_H}\alpha^\top\mathbf b."

TOL = 1e-9
BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
NOT_YET = "not computed yet"


def f3(x):
    return fmt(x, 3)


def join(values, digits=3):
    return ", ".join(fmt(v, digits) for v in values)


# Demonstration 1: the belief update, one stage at a time (Equation 8.1)

CORRIDOR_START = [1 / 3, 1 / 3, 0.0, 1 / 3]
CORRIDOR_SIGNAL = [[1.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 0.0]]  # columns: non-goal, goal


def east_matrix(slip):
    """Rows are current states, columns next states; EAST goes west with chance slip."""
    s = float(slip)
    return [[s, 1 - s, 0, 0], [s, 0, 1 - s, 0], [0, s, 0, 1 - s], [0, 0, s, 1 - s]]


def lab(data):
    return evaluate(data)["metrics"]


NOTEBOOK_DEFAULT = {
    "belief": [0.5, 0.5], "transition": [[1, 0], [0, 1]], "observation": [[0.9, 0.1], [0.1, 0.9]],
    "observed": 0, "action_rewards": [[10, -10], [-10, 10]], "observation_cost": 1,
}
NOTEBOOK_CHANGED = dict(NOTEBOOK_DEFAULT, observation=[[0.5, 0.5], [0.5, 0.5]])
NOTEBOOK_TRANSFER = {
    "belief": [0.8, 0.2], "transition": [[0.7, 0.3], [0.2, 0.8]], "observation": [[0.8, 0.2], [0.3, 0.7]],
    "observed": 1, "action_rewards": [[5, -4], [0, 2]], "observation_cost": 0.2,
}


def corridor_data(moves):
    belief = list(CORRIDOR_START)
    for _ in range(moves):
        data = {"belief": belief, "transition": east_matrix(0.1), "observation": CORRIDOR_SIGNAL, "observed": 0,
                "action_rewards": [[0, 0, 0, 0]], "observation_cost": 0}
        belief = lab(data)["posterior"]
        last = data
    return last


def corridor_before(moves):
    belief = list(CORRIDOR_START)
    for _ in range(moves - 1):
        belief = lab({"belief": belief, "transition": east_matrix(0.1), "observation": CORRIDOR_SIGNAL, "observed": 0,
                      "action_rewards": [[0, 0, 0, 0]], "observation_cost": 0})["posterior"]
    return belief


UPDATE_CASES = {
    "move1": {"title": "Corridor, first EAST move", "names": ["1", "2", "3\ngoal", "4"], "report": "non-goal report",
              "labels": ["place 1", "place 2", "place 3", "place 4"], "O": [1.0, 1.0, 0.0, 1.0]},
    "move2": {"title": "Corridor, second EAST move", "names": ["1", "2", "3\ngoal", "4"], "report": "non-goal report",
              "labels": ["place 1", "place 2", "place 3", "place 4"], "O": [1.0, 1.0, 0.0, 1.0]},
    "default": {"title": "Notebook default case", "names": ["state 1", "state 2"], "report": "observation 0",
                "labels": ["state 1", "state 2"], "O": [0.9, 0.1]},
    "transfer": {"title": "Notebook transfer case", "names": ["state 1", "state 2"], "report": "observation 1",
                 "labels": ["state 1", "state 2"], "O": [0.2, 0.7]},
}
STAGE_NAMES = ["Prior belief", "After prediction", "After the report"]


def update_data(case):
    if case == "move1":
        return corridor_data(1)
    if case == "move2":
        return corridor_data(2)
    return {"default": NOTEBOOK_DEFAULT, "transfer": NOTEBOOK_TRANSFER}[case]


def terms(weights, factors, digits=3):
    parts = [f"{fmt(w, digits)} x {fmt(f, digits)}" for w, f in zip(weights, factors) if abs(f) > 1e-12 and abs(w) > 1e-12]
    return " + ".join(parts) if parts else "0 x 0"


def update_picture(case="move1", stage=2):
    stage = int(stage)
    spec = UPDATE_CASES[case]
    data = update_data(case)
    out = lab(data)
    prior = list(data["belief"])
    if case == "move2":
        prior = corridor_before(2)
        data = dict(data, belief=prior)
        out = lab(data)
    pred, post, mass = out["predictive_belief"], out["posterior"], out["observed_probability"]
    P = data["transition"]
    k = len(prior)
    obs_col = [row[data["observed"]] for row in data["observation"]]
    # independent hand checks of the laboratory's numbers
    hand_pred = [sum(prior[i] * P[i][j] for i in range(k)) for j in range(k)]
    hand_mass = sum(hand_pred[j] * obs_col[j] for j in range(k))
    if not (all(math.isclose(a, b, abs_tol=1e-12) for a, b in zip(pred, hand_pred)) and math.isclose(mass, hand_mass, abs_tol=1e-12)
            and all(math.isclose(post[j], hand_pred[j] * obs_col[j] / hand_mass, abs_tol=1e-12) for j in range(k))):
        raise AssertionError("laboratory belief update disagrees with the hand calculation")
    series = [(prior, PALETTE["navy"], "", "before"), (pred, PALETTE["grey"], "///", "predicted"), (post, PALETTE["teal"], "", "after the report")]
    fig, ax = new_figure(height=4.2)
    x = np.arange(k)
    width = 0.26
    for s, (values, color, hatch, name) in enumerate(series):
        if s > stage:
            continue
        pos = x + (s - 1) * width
        ax.bar(pos, values, width, color="white" if hatch else color, edgecolor=color, hatch=hatch, linewidth=1.4)
        if s == stage:
            for xi, v in zip(pos, values):
                zero = abs(v) < 1e-12
                # a zero label starts at its own bar's left edge so it clears the neighbouring hatched bar
                ax.annotate(f3(v), (xi, v), xytext=(-6, 3) if zero else (0, 3), textcoords="offset points",
                            ha="left" if zero else "center", va="bottom", fontsize=10, color=PALETTE["ink"])
    ax.text(0.5, 0.985, "navy: before the move; hatched: predicted; teal: after the report", transform=ax.transAxes,
            ha="center", va="top", fontsize=10.5, color=PALETTE["ink"])
    ax.set_xticks(x, spec["names"])
    ax.set_ylim(0, 1.2)
    ax.set_xlim(-0.6, k - 0.4)
    ax.set_xlabel("State" + (", west to east" if k == 4 else ""))
    ax.set_ylabel("Probability")
    ax.set_title(f"{spec['title']}: step {stage + 1} of 3, {STAGE_NAMES[stage].lower()}", fontsize=11.5)
    ax.grid(axis="x", alpha=0)

    lab0, lab1 = spec["labels"][0], spec["labels"][1]
    metrics = {
        "Prior belief": join(prior),
        "Predicted belief": join(pred) if stage >= 1 else NOT_YET,
        "Belief after the report": join(post) if stage >= 2 else NOT_YET,
        "Weight the report keeps": f3(mass) if stage >= 2 else NOT_YET,
        f"First coordinate ({lab0}) after the report": f3(post[0]) if stage >= 2 else NOT_YET,
    }
    pc0 = terms(prior, [P[i][0] for i in range(k)])
    pc1 = terms(prior, [P[i][1] for i in range(k)])
    mass_terms = terms(pred, obs_col)
    if stage == 0:
        interpretation = (
            f"The belief before the move is ({join(prior)}). One coordinate per state; the check that it is a belief is {' + '.join(f3(v) for v in prior)} = {f3(sum(prior))}. The report will later "
            f"weight {lab0} by {f3(obs_col[0])} and {lab1} by {f3(obs_col[1])}, but it weights the predicted belief, not this prior. Nothing has "
            "been pushed through the action or weighted by the report yet; the next two steps do that."
        )
        worked = [
            f"The prior belief is ({join(prior)}), one probability per state.",
            f"Check that it is a belief: {' + '.join(f3(v) for v in prior)} = {f3(sum(prior))}.",
            f"The report will later weight {lab0} by {f3(obs_col[0])} and {lab1} by {f3(obs_col[1])}, applied to the predicted belief.",
            "Step 2 pushes this belief through the action (prediction, the inner sum of Equation (8.1)).",
            "Step 3 weights each predicted state by how well it explains the report, then rescales.",
        ]
        alt = f"Bars showing the prior belief over {k} states: {join(prior)}."
    elif stage == 1:
        interpretation = (
            f"Prediction pushes the prior through the action. {lab0.capitalize()}: {pc0} = {f3(pred[0])}. {lab1.capitalize()}: "
            f"{pc1} = {f3(pred[1])}. The predicted belief is ({join(pred)}). Prediction alone has not used the report."
            + (" Here the action is a pure stay, so the predicted belief equals the prior." if all(P[i][j] == (1 if i == j else 0) for i in range(k) for j in range(k))
               else " The predicted belief differs from the prior, so the prior must not be inserted directly into the weighting step.")
        )
        worked = [
            f"Prior belief ({join(prior)}); each row of the move table says where a state goes.",
            f"Predicted weight on {lab0} = {pc0} = {f3(pred[0])}.",
            f"Predicted weight on {lab1} = {pc1} = {f3(pred[1])}.",
            f"The predicted belief is ({join(pred)}); the report is not used yet.",
        ]
        alt = f"Bars of the prior belief and, beside them in hatching, the predicted belief ({join(pred)})."
    else:
        interpretation = (
            f"The {spec['report']} keeps weight {mass_terms} = {f3(mass)}. {lab0.capitalize()} after the report = "
            f"{f3(pred[0])} x {f3(obs_col[0])} / {f3(mass)} = {f3(post[0])}; {lab1} = {f3(pred[1])} x {f3(obs_col[1])} / {f3(mass)} = "
            f"{f3(post[1])}. The belief after the report is ({join(post)})."
            + (" A state the report rules out is exactly 0; a state it cannot rule out keeps weight, which is why the west end never reaches 0."
               if k == 4 else " The weights are rescaled so they sum to 1 again.")
        )
        worked = [
            f"Predicted belief ({join(pred)}); the report's likelihood in each state is ({join(obs_col)}).",
            f"Weight kept = {mass_terms} = {f3(mass)}.",
            f"{lab0.capitalize()} = {f3(pred[0])} x {f3(obs_col[0])} / {f3(mass)} = {f3(post[0])}.",
            f"{lab1.capitalize()} = {f3(pred[1])} x {f3(obs_col[1])} / {f3(mass)} = {f3(post[1])}.",
            f"The belief after the report is ({join(post)}).",
        ]
        alt = f"Bars of the prior, predicted and corrected beliefs over {k} states; the corrected belief is ({join(post)})."
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 2: the same report under different instruments (Equation 8.1)

KERNELS = {
    # key: (label, report chance in state A, report chance in state B, threshold, threshold text, state names)
    "run03": ("Runner, false-positive 0.03", 1.0, 0.03, 0.8, "the 0.80 release threshold"),
    "run30": ("Runner, false-positive 0.30", 1.0, 0.30, 0.8, "the 0.80 release threshold"),
    "sensor": ("Informative sensor (notebook default rows)", 0.9, 0.1, 0.5, "the 0.50 break-even belief of the notebook's rewards 10 and -10"),
    "aliased": ("Aliased sensor, identical rows (notebook changed case)", 0.5, 0.5, 0.5, "the 0.50 break-even belief of the notebook's rewards 10 and -10"),
}


def lab_posterior(prior, tp, fp):
    out = lab({"belief": [float(prior), 1 - float(prior)], "transition": [[1, 0], [0, 1]],
               "observation": [[tp, 1 - tp], [fp, 1 - fp]], "observed": 0, "action_rewards": [[0, 0]], "observation_cost": 0})
    return out["posterior"][0], out["observed_probability"]


def instrument_picture(kernel="run03", prior=0.5):
    label, tp, fp, thr, thr_text = KERNELS[kernel]
    prior = float(prior)
    post, report = lab_posterior(prior, tp, fp)
    hand = prior * tp / (prior * tp + (1 - prior) * fp)
    if not math.isclose(post, hand, abs_tol=1e-12):
        raise AssertionError("laboratory posterior disagrees with Bayes' rule by hand")
    runner = kernel.startswith("run")
    grid = np.linspace(0, 1, 101)
    curve = grid * tp / (grid * tp + (1 - grid) * fp)
    fig, ax = new_figure(height=4.2)
    ax.plot([0, 1], [0, 1], color=PALETTE["gold"], linestyle="dotted", linewidth=1.6)
    ax.plot(grid, curve, color=PALETTE["teal"], linewidth=2.2)
    ax.axhline(thr, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    ax.plot([prior], [post], "o", color=PALETTE["terracotta"], markersize=9, zorder=4)
    ax.plot([prior, prior], [prior, post], color=PALETTE["terracotta"], linewidth=1.2, zorder=3)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.2)
    label_point(ax, 1.0, thr, f"threshold {fmt(thr, 2)}", color=PALETTE["grey"], dx=0, dy=4, ha="right").set_bbox(BOX)
    label_point(ax, 0.97, 0.2, "dotted: no information,\nposterior = prior", color=PALETTE["gold"], dx=0, dy=0, ha="right", va="bottom").set_bbox(BOX)
    # the posterior is named in the clear lower-right corner (below the diagonal), so no label sits on a line
    label_point(ax, 0.97, 0.36, f"marker: posterior {fmt(post, 4)}", color=PALETTE["terracotta"], dx=0, dy=0, ha="right", va="bottom").set_bbox(BOX)
    ax.set_xlabel("Prior probability of the first state" + (" (tests pass)" if runner else ""))
    ax.set_ylabel("Probability after the report")
    ax.set_title(f"{label}; prior {fmt(prior, 2)}", fontsize=11)
    if math.isclose(post, thr, abs_tol=TOL):
        decision = "exactly on the threshold"
    elif post > thr:
        decision = "above the threshold"
    else:
        decision = "below the threshold"
    informative = not math.isclose(tp, fp, abs_tol=1e-12)
    if not informative:
        decision_metric = f"{decision} (unchanged: the report left the prior where it was)"
        extra = (" The report is equally likely from both states, so it carries no information: this is aliasing, and more readings of the same "
                 "kind would return the same ambiguity. The posterior equals the prior, so the decision is whatever the prior already implied.")
    else:
        decision_metric = decision
        extra = " Only the assumed instrument differs between the kernels; the report is the same."
    name_a = "tests pass" if runner else "state 1"
    name_b = "not passing" if runner else "state 2"
    wa, wb = prior * tp, (1 - prior) * fp
    metrics = {
        "Chance of this report": fmt(report, 4),
        "Posterior, first state": fmt(post, 4),
        "Compared with the threshold": decision_metric,
        "Change from the prior": fmt(post - prior, 4),
    }
    interpretation = (
        f"Posterior = {fmt(prior, 2)} x {fmt(tp, 2)} / ({fmt(prior, 2)} x {fmt(tp, 2)} + {fmt(1 - prior, 2)} x {fmt(fp, 2)}) = "
        f"{fmt(wa, 4)} / {fmt(report, 4)} = {fmt(post, 4)}, {decision} ({thr_text}).{extra}"
    )
    worked = [
        f"The report has chance {fmt(tp, 2)} in {name_a} and {fmt(fp, 2)} in {name_b}.",
        f"Weight of {name_a} = {fmt(prior, 2)} x {fmt(tp, 2)} = {fmt(wa, 4)}.",
        f"Weight of {name_b} = {fmt(1 - prior, 2)} x {fmt(fp, 2)} = {fmt(wb, 4)}.",
        f"Chance of the report = {fmt(wa, 4)} + {fmt(wb, 4)} = {fmt(report, 4)}.",
        f"Posterior = {fmt(wa, 4)} / {fmt(report, 4)} = {fmt(post, 4)}.",
        f"Compared with {thr_text}: {decision}.",
    ]
    alt = (f"Curve of the posterior against the prior for {label.lower()} with the no-information diagonal and a decision threshold of "
           f"{fmt(thr, 2)}. At prior {fmt(prior, 2)} the posterior is {fmt(post, 4)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 3: a belief is valued by its best plan (Equations 8.2, 8.3, 8.4)

SETTINGS = {
    # key: (title, xlabel, plans [(name, vector)], cases [(label, belief on first state)], first-state name)
    "alpha": ("Two contingent plans", "Belief on the first state",
              [("plan 1", (4.0, 1.0)), ("plan 2", (0.0, 3.0))],
              [("belief 0.25 (the chapter's)", 0.25), ("belief 0.50", 0.5), ("belief 0.75", 0.75)]),
    "auth": ("Memory keeps authorization", "Belief the history is authorized",
             [("release", (4.0, -12.0)), ("hold", (0.0, 0.0))],
             [("message yes", 1.0), ("message no", 0.0), ("no memory (baseline)", 0.5)]),
    "fmt": ("Memory keeps formatting", "Belief the history is authorized",
            [("release", (4.0, -12.0)), ("hold", (0.0, 0.0))],
            [("letter A", 0.5), ("letter B", 0.5), ("no memory (baseline)", 0.5)]),
    "detour": ("Costly detour", "Belief the committed route is right",
               [("commit now", (100.0, 0.0)), ("detour first", (97.0, 97.0))],
               [("belief 0.45", 0.45), ("belief 0.98", 0.98), ("belief 0.97", 0.97)]),
}


def lab_best(plans, b):
    out = lab({"belief": [b, 1 - b], "transition": [[1, 0], [0, 1]], "observation": [[0.5, 0.5], [0.5, 0.5]], "observed": 0,
               "action_rewards": [list(v) for _, v in plans], "observation_cost": 0})
    return out["act_now_value"]


def belief_picture(setting="alpha", case=0):
    title, xlabel, plans, cases = SETTINGS[setting]
    case_label, b = cases[int(case)]
    vals = [v[0] * b + v[1] * (1 - b) for _, v in plans]
    best = max(vals)
    if not math.isclose(lab_best(plans, b), best, abs_tol=1e-9):
        raise AssertionError("laboratory expected-reward maximum disagrees with the hand dot products")
    (n0, v0), (n1, v1) = plans
    cross = (v1[1] - v0[1]) / ((v0[0] - v0[1]) - (v1[0] - v1[1])) if ((v0[0] - v0[1]) - (v1[0] - v1[1])) else None
    tie = math.isclose(vals[0], vals[1], abs_tol=1e-9)
    chosen = "tie" if tie else (n0 if vals[0] > vals[1] else n1)
    grid = np.linspace(0, 1, 101)
    lines = [v[0] * grid + v[1] * (1 - grid) for _, v in plans]
    env = np.maximum(lines[0], lines[1])
    lo = min(0.0, min(min(l) for l in lines))
    hi = max(max(l) for l in lines)
    pad = (hi - lo) * 0.12
    fig, ax = new_figure(height=4.2)
    ax.fill_between(grid, lo - pad, env, color=PALETTE["light"], alpha=0.35)
    ax.plot(grid, lines[0], color=PALETTE["navy"], linewidth=2)
    ax.plot(grid, lines[1], color=PALETTE["terracotta"], linewidth=2)
    ax.plot(grid, env, color=PALETTE["ink"], linewidth=0.9, linestyle="dashed")
    ax.axvline(b, color=PALETTE["grey"], linestyle="dotted", linewidth=1.3)
    ax.plot([b], [best], "D", color=PALETTE["gold"], markersize=10, markeredgecolor=PALETTE["ink"], zorder=4, clip_on=False)
    ax.set_xlim(0, 1)
    ax.set_ylim(lo - pad, hi + pad * 1.6)
    label_point(ax, 0.0, lines[0][0], n0, color=PALETTE["navy"], dx=6, dy=6 if lines[0][0] >= lines[1][0] else -6,
                ha="left", va="bottom" if lines[0][0] >= lines[1][0] else "top").set_bbox(BOX)
    if setting == "detour":
        label_point(ax, 0.06, 97.0, n1, color=PALETTE["terracotta"], dx=0, dy=6, ha="left", va="bottom").set_bbox(BOX)
    else:
        label_point(ax, 1.0, lines[1][-1], n1, color=PALETTE["terracotta"], dx=-6, dy=6 if lines[1][-1] >= lines[0][-1] else -6,
                    ha="right", va="bottom" if lines[1][-1] >= lines[0][-1] else "top").set_bbox(BOX)
    left_side = b > 0.5
    # the value label sits in the clear band above every line, beside the belief's dotted marker
    label_point(ax, b, hi + pad * 1.55, f"value {fmt(best, 2)}", color=PALETTE["ink"], dx=-5 if left_side else 5, dy=0,
                ha="right" if left_side else "left", va="top").set_bbox(BOX)
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Expected reward of the plan")
    ax.set_title(f"{title}: {case_label}", fontsize=11.5)

    b2, c2 = fmt(b, 2), fmt(1 - b, 2)
    dots = [f"{n}: {fmt(v[0], 0)} x {b2} + {signed(v[1], 0)} x {c2} = {signed(val, 2)}" for (n, v), val in zip(plans, vals)]
    cross_text = f" The two plans cross at belief {fmt(cross, 3 if setting != 'detour' else 2)}." if cross is not None and 0 <= cross <= 1 else ""
    metrics = {
        f"Value of {n0}": signed(vals[0], 2),
        f"Value of {n1}": signed(vals[1], 2),
        "Belief value V(b) (the larger)": signed(best, 2),
        "Chosen": chosen,
        "Crossing belief": fmt(cross, 3) if cross is not None else undefined("the plans never cross"),
    }
    if setting == "alpha":
        tail = " The belief value is the highest line at the belief, as in Equation (8.4): a plan is a vector, the value its dot product with the belief."
    elif setting == "detour":
        tail = (" Looking is an action with a negative immediate reward. The chapter stipulates 97 for the detour; that equals 100 - 3 if routing "
                "then succeeds for certain. Here 97 stands in for the look-ahead term of Equation (8.3), and the belief update inside it is not computed.")
        if tie:
            tail += " At this belief commit and detour tie exactly, so Equation (8.3) has two maximizers."
        elif chosen == n1:
            tail += f" The detour wins by {fmt(best - vals[0], 0)}."
        else:
            tail += f" Committing wins by {fmt(best - vals[1], 0)}, so the recursion declines the look."
    else:
        if setting == "auth":
            if b >= 1.0 - 1e-12:
                tail = " Belief 1: release is allowed and best. Mean utility over the four histories with this memory = (4 + 4 + 0 + 0) / 4 = 2.0."
            elif b <= 1e-12:
                tail = " Belief 0: hold is best. Mean utility over the four histories with this memory = (4 + 4 + 0 + 0) / 4 = 2.0, the same as the full history."
            else:
                tail = " With no memory at all the belief stays at the prior 0.5, release is worth (-4), and the controller holds (mean utility 0.0)."
        elif int(case) == 2:
            tail = (" With no memory at all the belief stays at the prior 0.5 and the controller holds, for a mean utility of 0.0. This baseline is "
                    "not in the chapter.")
        else:
            tail = (" Letter A and letter B give the same belief and the same value, which is the point: the letter splits each history group evenly "
                    "between authorized and unauthorized, so the belief is 0.5. "
                    "Release also needs the authorization record, which this memory lacks, so the controller holds. Mean utility over the four "
                    "histories = (0 + 0 + 0 + 0) / 4 = 0.0.")
    if setting in ("auth", "fmt"):
        metrics["Mean utility over four histories: authorization memory against formatting memory"] = "2.0 against 0.0"
    interpretation = "Belief " + b2 + ". " + "; ".join(dots) + f". The larger is {signed(best, 2)}, so {('the plans tie' if tie else chosen + ' is chosen')}." + cross_text + tail
    worked = [f"Belief on the first state = {b2}, so the second state has {c2}."] + [d + "." for d in dots] + [
        f"The belief value is the larger: {signed(best, 2)} ({'tie' if tie else chosen})."]
    if cross is not None and 0 <= cross <= 1:
        worked.append(f"The lines cross at belief {fmt(cross, 3 if setting != 'detour' else 2)}.")
    alt = (f"Two straight lines of expected reward against belief for {title.lower()}, with the highest line shaded beneath. A diamond marks "
           f"belief {b2}, where the larger value is {signed(best, 2)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 4: when a look can change the decision (Equation 8.5)

TOOL = {
    "belief": [0.6, 0.4], "transition": [[1, 0], [0, 1]], "observation": [[0.9, 0.1], [0.15, 0.85]],
    "observed": 0, "action_rewards": [[10, -40], [0, 0]], "observation_cost": 0,
}
VOI_CASES = {
    # key: (label, data, case price, belief axis label, action names)
    "tool": ("Chapter verification tool, prior 0.6", TOOL, 1.0, "Belief the claim is supported", ["release", "decline"]),
    "default": ("Notebook default case", NOTEBOOK_DEFAULT, 1.0, "Belief in state 1 when the decision is made", ["act 1", "act 2"]),
    "changed": ("Notebook changed case (identical rows)", NOTEBOOK_CHANGED, 1.0, "Belief in state 1 when the decision is made", ["act 1", "act 2"]),
    "transfer": ("Notebook transfer case", NOTEBOOK_TRANSFER, 0.2, "Belief in state 1 when the decision is made", ["act 1", "act 2"]),
}
PRICE_MODES = ["free", "case", "even"]


def voi_curve_data(case):
    return dict(VOI_CASES[case][1], transition=[[1, 0], [0, 1]], observation_cost=0)


_curve_cache = {}


def voi_curve(case):
    if case not in _curve_cache:
        base = voi_curve_data(case)
        grid = np.linspace(0, 1, 2001)
        vals = []
        for g in grid:
            v = lab(dict(base, belief=[float(g), 1 - float(g)]))["gross_value_of_information"]
            vals.append(0.0 if abs(v) < 1e-12 else v)
        _curve_cache[case] = (grid, np.array(vals))
    return _curve_cache[case]


def gross_at(case, g):
    v = lab(dict(voi_curve_data(case), belief=[float(g), 1 - float(g)]))["gross_value_of_information"]
    return 0.0 if abs(v) < 1e-12 else v


def band_edges(case, grid, curve):
    """Beliefs where the value turns positive, refined from the scan by bisection."""
    idx = np.nonzero(curve > 1e-9)[0]
    i0, i1 = int(idx.min()), int(idx.max())
    lo = float(grid[i0])
    if i0 > 0:
        a, b = float(grid[i0 - 1]), lo
        for _ in range(50):
            m = (a + b) / 2
            a, b = (a, m) if gross_at(case, m) > 1e-9 else (m, b)
        lo = b
    hi = float(grid[i1])
    if i1 < len(grid) - 1:
        a, b = hi, float(grid[i1 + 1])
        for _ in range(50):
            m = (a + b) / 2
            a, b = (m, b) if gross_at(case, m) > 1e-9 else (a, m)
        hi = a
    return lo, hi


def weighted_best(pred, O, R):
    """Per report: weighted value of each action, and the best of them (joint weights, as in Equation (8.5))."""
    k, n_obs = len(pred), len(O[0])
    rows = []
    for o in range(n_obs):
        vals = [sum(pred[j] * O[j][o] * r[j] for j in range(k)) for r in R]
        rows.append((vals, max(vals)))
    return rows


def look_picture(case="tool", price="free"):
    label, data, case_price, xlabel, acts = VOI_CASES[case]
    out = lab(data)
    pred = out["predictive_belief"]
    b = pred[0]
    gross = out["gross_value_of_information"]
    gross = 0.0 if abs(gross) < 1e-12 else gross
    now = out["act_now_value"]
    O, R = data["observation"], data["action_rewards"]
    rows = weighted_best(pred, O, R)
    hand = sum(best for _, best in rows) - max(sum(pred[j] * r[j] for j in range(len(pred))) for r in R)
    if not math.isclose(hand, gross, abs_tol=1e-9):
        raise AssertionError("hand calculation disagrees with the laboratory value of information")
    cost = {"free": 0.0, "case": case_price, "even": gross}[price]
    net = gross - cost
    grid, curve = voi_curve(case)
    positive = grid[curve > 1e-9]
    band = band_edges(case, grid, curve) if len(positive) else None
    fig, ax = new_figure(height=4.3)
    if band:
        ax.axvspan(band[0], band[1], facecolor="none", edgecolor=PALETTE["light"], hatch="//", linewidth=0)
    ax.plot(grid, curve, color=PALETTE["teal"], linewidth=2)
    top = max(float(curve.max()), gross, cost) * 1.18 + 0.4
    if cost > 0:
        ax.axhline(cost, color=PALETTE["gold"], linestyle="dashed", linewidth=1.5)
        label_point(ax, 0.0, cost, f"price of the look {fmt(cost, 2)}", color=PALETTE["gold"], dx=4, dy=4, ha="left").set_bbox(BOX)
    ax.plot([b], [gross], "o", color=PALETTE["terracotta"], markersize=9, zorder=4)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(-0.05 * top, top)
    flip = b > 0.5
    slope = float(np.interp(min(b + 0.01, 1.0), grid, curve) - np.interp(max(b - 0.01, 0.0), grid, curve))
    if gross >= 0.15 * top:
        # above the curve, on the side away from its peak (to the right at the peak), so the label never sits on the line
        label_point(ax, b, gross, f"belief {fmt(b, 2)}: {fmt(gross, 2)}", color=PALETTE["terracotta"],
                    dx=-8 if slope > 1e-9 else 8, dy=8, ha="right" if slope > 1e-9 else "left", va="bottom").set_bbox(BOX)
    else:
        label_point(ax, b, gross, f"belief {fmt(b, 2)}: {fmt(gross, 2)}", color=PALETTE["terracotta"],
                    dx=-10 if flip else 10, dy=22 if gross < 0.15 * top else -12, ha="right" if flip else "left",
                    va="bottom" if gross < 0.15 * top else "top").set_bbox(BOX)
    if band:
        label_point(ax, (band[0] + band[1]) / 2, top, f"look can pay: {fmt(band[0], 3)} to {fmt(band[1], 3)}", color=PALETTE["grey"],
                    dx=0, dy=-4, ha="center", va="top")
    else:
        label_point(ax, 0.5, top, "flat at 0: no belief makes a look pay", color=PALETTE["grey"], dx=0, dy=-4, ha="center", va="top")
    ax.set_xlabel(xlabel)
    ax.set_ylabel("Gross value of one report (utility points)")
    price_name = {"free": "free", "case": f"price {fmt(case_price, 2)}", "even": f"break-even price {fmt(gross, 2)}"}[price]
    ax.set_title(f"{label}; look {price_name}", fontsize=11)

    acts_now = [sum(pred[j] * r[j] for j in range(len(pred))) for r in R]
    if math.isclose(net, 0.0, abs_tol=TOL) and cost > 0:
        decision = "tie (break-even)"
        verdict = (f"The look breaks even: its value {fmt(gross, 2)} equals its price {fmt(cost, 2)}, so Equation (8.5) leaves looking "
                   "and not looking tied and the person who owns the costs has to choose.")
    elif gross <= TOL:
        decision = "no benefit (value 0)" if cost == 0 else "do not look (value 0)"
        verdict = ("Both reports leave the same action best, so the look is worth exactly 0 however much it changes the belief."
                   + (" Paying anything for it loses." if cost > 0 else ""))
    elif net > 0:
        decision = "look"
        verdict = f"The look pays: {fmt(gross, 2)} - {fmt(cost, 2)} = {fmt(net, 2)} is above zero."
    else:
        decision = "do not look"
        verdict = f"The look is worth {fmt(gross, 2)}, less than its price {fmt(cost, 2)}, so skip it."
    now_best = int(np.argmax(acts_now))
    best_names = [acts[int(np.argmax(vals))] for vals, _ in rows]
    metrics = {
        "Best action without looking": f"{acts[now_best]} ({fmt(max(acts_now), 2)})",
        "Value of looking (gross)": fmt(gross, 2),
        "Price of looking": fmt(cost, 2),
        "Net value of looking": fmt(net, 2),
        "Decision": decision,
    }
    rep = " + ".join(fmt(best, 2) for _, best in rows)
    detail = "; ".join(
        f"report {o}: " + ", ".join(f"{acts[a]} {signed(v, 2)}" for a, v in enumerate(vals)) + f", best {acts[int(np.argmax(vals))]} {signed(best, 2)}"
        for o, (vals, best) in enumerate(rows))
    interpretation = (
        f"Belief at the decision ({join(pred, 2)}). Acting now: " + ", ".join(f"{acts[a]} {signed(v, 3)}" for a, v in enumerate(acts_now))
        + f", best {fmt(max(acts_now), 2)}. Each term after a report is weighted by the chance of the report: {detail}. "
        f"Value of looking = {rep} - {signed(max(acts_now), 2)} = {fmt(gross, 2)}. {verdict}"
        + (f" Against this case's reward and report rows, a look can have positive value only for beliefs between {fmt(band[0], 4)} and {fmt(band[1], 4)}."
           if band else " For this case no belief gives a look positive value.")
    )
    worked = [
        f"Belief when the decision is made: ({join(pred, 2)}).",
        "Acting now: " + ", ".join(f"{acts[a]} {signed(v, 3)}" for a, v in enumerate(acts_now)) + f"; best {fmt(max(acts_now), 2)}.",
    ] + [f"After report {o} (weighted by its chance): {', '.join(f'{acts[a]} {signed(v, 2)}' for a, v in enumerate(vals))}; best {signed(best, 2)}."
         for o, (vals, best) in enumerate(rows)] + [
        f"Value of looking = {rep} - {signed(max(acts_now), 2)} = {fmt(gross, 2)}.",
        f"Price {fmt(cost, 2)}: net = {fmt(gross, 2)} - {fmt(cost, 2)} = {fmt(net, 2)}.",
    ]
    alt = (f"Curve of the gross value of one report against belief for the {label.lower()}, with a hatched band where the value is positive "
           f"and a marker at belief {fmt(b, 2)} where it is {fmt(gross, 2)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


CHAPTER = {
    "number": 8,
    "title": "Acting in the Dark",
    "subtitle": "When one reading fits several situations, an agent keeps a belief over the possibilities and prices a look by the decisions it can change.",
    "summary": (
        "These four demonstrations follow the chapter from a robot in a corridor to an agent deciding whether to verify a claim. "
        "You will step a belief through prediction and correction, compare instruments including one that cannot discriminate, value a "
        "belief by its best plan, and find the beliefs for which looking is worth anything. The notebook's default, changed and "
        "transfer cases are selectable."
    ),
    "ask_skill": {"prompt": (
        "Take prior (0.5, 0.5), sensor rows (0.9, 0.1) and (0.1, 0.9), rewards (10, -10) and (-10, 10), and an observation cost of 1. "
        "Compute the posterior after observation 0, the gross and net value of information, and the cost at which looking breaks even.")},
    "demos": [
        {
            "id": "C08-D01",
            "title": "The belief update, one stage at a time",
            "question": "How does a belief change when an action is taken and a report arrives, and which part of the change is prediction and which is correction?",
            "equations": [EQ_UPDATE, EQ_CORRIDOR],
            "symbols": (
                "b is the belief: one probability per state. In the corridor there are four places numbered 1 to 4 from west to east, place 3 "
                "is the goal, and an EAST move goes east with chance 0.9 and west with chance 0.1 (a move into a wall leaves the robot in place). "
                "In Equation (8.1), a is the action, P(x' | x, a) the chance that action a moves state x to x', Obs(o | x', a) the chance of "
                "hearing report o in state x' (here the report depends only on the state), and x'' a stand-in state in the rescaling sum. "
                "The notebook cases use two states: the default keeps the state fixed and hears observation 0 from a sensor with rows "
                "(0.9, 0.1) and (0.1, 0.9); the transfer case moves the state with rows (0.7, 0.3) and (0.2, 0.8) and hears observation 1 from rows "
                "(0.8, 0.2) and (0.3, 0.7). The three steps are the prior, the prediction (inner sum) and the correction (weight by the report, rescale)."
            ),
            "prediction": "In the notebook transfer case the prior is (0.8, 0.2). After the prediction step, before the report is used, is the belief still (0.8, 0.2)?",
            "prediction_options": ["Yes, prediction leaves it unchanged", "No, it becomes (0.6, 0.4)", "No, it becomes (0.2, 0.8)"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Predicted first state = 0.8 x 0.7 + 0.2 x 0.2 = 0.60, so the belief is (0.6, 0.4). The report must be weighted against this predicted belief.",
                "incorrect": "Choose the notebook transfer case and step to the second stage: the first state gets 0.8 x 0.7 + 0.2 x 0.2 = 0.60, so the belief is (0.6, 0.4).",
            },
            "explanation": (
                "The prediction pushes each state's weight along the action, which is the inner sum of Equation (8.1). The report then multiplies "
                "each predicted weight by its likelihood and the denominator rescales what is left. When the action leaves the state fixed, prediction "
                "changes nothing and the prior is already the predicted belief. When it moves the state, the prior must not be inserted straight "
                "into the weighting step. The west end of the corridor never reaches 0 because nothing the robot has heard rules it out."
            ),
            "application": (
                "Whenever a tool result leaves several explanations open, write down the possibilities, the chance the action moved each one, "
                "and the chance each would have produced the report. The three steps then give the new weights without rereading the whole history."
            ),
            "assumptions": (
                "The corridor, its deterministic goal report and the move probabilities are the chapter's; the notebook cases are constructed. "
                "The model is only as good as the move and report probabilities supplied to it; if the real world differs, the update is exact for the wrong world."
            ),
            "check": "Start from (1/3, 1/3, 0, 1/3) with a move that goes west with chance 0.2 instead of 0.1. What is the west-end weight after the first non-goal report?",
            "answer": (
                "Predicted west end = 0.2 x (1/3) + 0.2 x (1/3) = 0.133. The goal is predicted to hold 0.8 x (1/3) + 0.2 x (1/3) = 1/3, "
                "so the report keeps 1 - 1/3 = 2/3. West end = 0.133 / 0.667 = 0.200."
            ),
            "provenance": (
                "Constructed example: the chapter's corridor update (the book's own values for one and two moves at slip chance 0.1) and the "
                "laboratory notebook's default and transfer cases, computed with the laboratory's belief function."
            ),
            "source_section": "The update, worked",
            "source_anchor": "the-update-worked",
            "misconception": {
                "title": "More moves drive the belief to the truth",
                "text": ("The chapter says a belief does not converge on the truth merely by running longer; it converges only as far as the evidence "
                         "distinguishes. In the corridor the west end falls to 0.100 and holds there across the paper's two moves, because no report rules it out."),
            },
            "scope_note": {
                "text": ("The belief formulation assumes the transition and observation kernels are known, and an agent operating on real tools has neither."),
                "source_section": "What this does not settle",
            },
            "stepper": "stage",
            "controls": [
                {"key": "case", "label": "Case", "values": ["move1", "move2", "default", "transfer"], "default": "move1",
                 "value_labels": ["Corridor, first move", "Corridor, second move", "Notebook default", "Notebook transfer"]},
                {"key": "stage", "label": "Step", "values": [0, 1, 2], "default": 2,
                 "value_labels": ["1. Prior belief", "2. Prediction", "3. Report and rescaling"]},
            ],
            "function": "update_picture",
        },
        {
            "id": "C08-D02",
            "title": "The same report under different instruments",
            "question": "If an instrument says pass, how far does the belief move, and what decides that: the report or the instrument model?",
            "equations": [EQ_UPDATE],
            "symbols": (
                "The runner has two modeled states: the tests genuinely pass, or they do not (failed or never ran). A passing state always reports pass; the "
                "false-positive probability is the chance that a not-passing state also reports pass. The sensor kernels have two states: the informative "
                "sensor reports observation 0 with chance 0.9 in the first state and 0.1 in the second; the aliased sensor has identical rows, so "
                "observation 0 has chance 0.5 in both. The prior is the probability of the first state before the report. The dotted diagonal is a report "
                "that carries no information (posterior equals prior). The dashed line is the belief at which the decision flips."
            ),
            "prediction": "Keep the prior at 0.50 and move from the runner with false-positive probability 0.03 to the one with 0.30. Does the posterior cross the 0.80 threshold, and in which direction?",
            "prediction_options": ["It rises further above 0.80", "It falls from above 0.80 to below it", "It stays above 0.80"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "0.5 / (0.5 + 0.5 x 0.03) = 0.9709 is above 0.80, and 0.5 / (0.5 + 0.5 x 0.30) = 0.7692 is below it.",
                "incorrect": "Compare the first two instruments at prior 0.50: 0.9709 for false-positive 0.03 and 0.7692 for 0.30, so the posterior falls below 0.80.",
            },
            "explanation": (
                "Equation (8.1) weights the first state by its report chance and the second by its own, then rescales. When the report chances differ a lot "
                "the posterior curve bows far from the diagonal; when they are equal it lies on the diagonal and the report carries nothing. Noise corrupts a "
                "reading that still discriminates; aliasing gives distinct states the same reading, and no operation on that reading recovers the difference. "
                "Holding the prior fixed, only the assumed instrument changes, and with it the conclusion."
            ),
            "application": (
                "Before trusting a pass, a green check or a found-nothing result, ask how often the bad state produces the same output. That one comparison "
                "decides whether the report can carry a decision."
            ),
            "assumptions": (
                "Two states, one report, and instrument probabilities that are teaching assumptions, not measurements of any runner or sensor. Correct "
                "arithmetic cannot repair a wrong likelihood. Repeated reports would need a model of how they depend on each other; rerunning the same "
                "broken or cached instrument does not automatically supply independent evidence."
            ),
            "check": "With prior 0.50 and a runner that always reports pass when the tests pass, what false-positive probability puts the posterior exactly at 0.80?",
            "answer": "0.5 / (0.5 + 0.5 x f) = 0.8 gives 0.5 + 0.5 x f = 0.625, so f = 0.25. Below 0.25 the pass report clears 0.80; above it does not.",
            "provenance": (
                "Constructed example: the chapter's test-runner teaching assumptions (true-positive 1, false-positive 0.03 and 0.30, prior 0.5, giving 0.9709 and "
                "0.7692) and the laboratory notebook's default and changed observation rows, with priors 0.2 and 0.8 defined for this reader."
            ),
            "source_section": "Where the observation kernel comes from",
            "source_anchor": "where-the-observation-kernel-comes-from",
            "misconception": {
                "title": "More readings fix any ambiguity",
                "text": ("The chapter separates noise from aliasing. More samples, better optics and longer integration attack noise and help. When two states "
                         "give the same reading, averaging more readings returns the same ambiguity with tighter error bars: the information was never in the observation."),
            },
            "scope_note": {
                "text": "A correct application of Bayes' rule cannot repair an incorrect likelihood supplied to it.",
                "source_section": "Where the observation kernel comes from",
            },
            "controls": [
                {"key": "kernel", "label": "Instrument", "values": ["run03", "run30", "sensor", "aliased"], "default": "run03",
                 "value_labels": ["Runner, false-positive 0.03", "Runner, false-positive 0.30", "Informative sensor (notebook default)",
                                  "Aliased sensor (notebook changed)"]},
                {"key": "prior", "label": "Prior probability of the first state", "values": [0.2, 0.5, 0.8], "default": 0.5},
            ],
            "function": "instrument_picture",
        },
        {
            "id": "C08-D03",
            "title": "A belief is valued by its best plan",
            "question": "If every plan is a straight line in the belief, what does the belief's value look like, and how can two equal memories give different values?",
            "equations": [EQ_REWARD, EQ_BELIEF_VALUE, EQ_ALPHA],
            "symbols": (
                "b is the belief, here the probability of the first state (the second has 1 - b). A plan has a reward in each state; its expected reward "
                "at the belief, Equation (8.2), is the weighted average, which is the dot product of the plan's vector alpha with b. V(b) is the best "
                "such value, the highest line, as in Equations (8.3) and (8.4). The settings are: the chapter's two plans alpha1 = (4, 1) and alpha2 = (0, 3); "
                "the one-bit memories of the document-release task (release earns 4 when authorized and -12 when not, holding earns 0); and the "
                "three-move detour (commit earns 100 with the chance that the committed route is right; the chapter stipulates 97 for the detour, which equals 100 - 3 if routing then succeeds for certain)."
            ),
            "prediction": "At belief 0.25 on the first state, which of the chapter's plans (4, 1) and (0, 3) has the larger expected reward?",
            "prediction_options": ["Plan 1, with 1.75", "Plan 2, with 2.25", "They tie"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Plan 1 is 4 x 0.25 + 1 x 0.75 = 1.75 and plan 2 is 0 x 0.25 + 3 x 0.75 = 2.25, so plan 2 is selected.",
                "incorrect": "Choose the two contingent plans at belief 0.25: plan 1 is 4 x 0.25 + 1 x 0.75 = 1.75, plan 2 is 0 x 0.25 + 3 x 0.75 = 2.25.",
            },
            "explanation": (
                "Equation (8.2) makes each plan's value linear in the belief, so each plan is a line and the value of the belief is the highest line, "
                "a piecewise linear convex curve. The two memories show why the belief matters more than storage size: keeping authorization gives a belief of "
                "1 or 0 and a mean utility of 2, while keeping the formatting letter leaves belief 0.5 and, because release also needs the authorization record, "
                "a mean utility of 0. A look is just another action with a negative immediate reward, so the detour is priced by the same maximum."
            ),
            "application": (
                "When shrinking a summary or a memory, list the histories it merges and check whether the best allowed action agrees across each merged group. "
                "Equal size says nothing; what the retained bit distinguishes is what matters."
            ),
            "assumptions": (
                "A stipulated toy task: four equally likely histories, authorization fixed between observation and action, and release permitted only with an "
                "authoritative authorization record. The detour value 97 is stipulated, not derived. This shows decision sufficiency for one task, not that "
                "short summaries are better in general, and the finite-horizon vector form does not make planning cheap."
            ),
            "check": "For plans (4, 1) and (0, 3), at what belief on the first state do they tie?",
            "answer": "4b + 1 x (1 - b) = 3 x (1 - b) gives 3b + 1 = 3 - 3b, so b = 1/3. Above 1/3 plan 1 is larger; below it plan 2 is.",
            "provenance": (
                "Constructed example: the chapter's alpha-vector pair, its four-history document-release table with the book's stipulated utilities "
                "(+4, -12 and 0) and its three-move detour (100, cost 3, value 97), with the break-even belief 0.97 derived from them; maxima checked with the "
                "laboratory's expected-reward function."
            ),
            "source_section": "Where an agent's belief actually lives",
            "source_anchor": "where-an-agents-belief-actually-lives",
            "misconception": {
                "title": "The agent is paid for believing",
                "text": ("The chapter notes the belief reward can seem strange, as if the agent were rewarded merely for believing it will be paid. "
                         "Equation (8.2) is an expected reward, not a payment for confidence; actual rewards depend on the realized state and chosen action."),
            },
            "scope_note": {
                "text": ("Equation (8.3) is a solution concept rather than an algorithm, and the space it ranges over cannot be enumerated."),
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "setting", "label": "Setting", "values": ["alpha", "auth", "fmt", "detour"], "default": "alpha",
                 "value_labels": ["Two contingent plans", "Memory keeps authorization", "Memory keeps formatting", "Costly detour"]},
                {"key": "case", "label": "Case within the setting (named in the figure)", "values": [0, 1, 2], "default": 1,
                 "value_labels": ["First case", "Second case", "Third case"]},
            ],
            "function": "belief_picture",
        },
        {
            "id": "C08-D04",
            "title": "A look pays only near the threshold",
            "question": "For which beliefs can a report change the decision, and is the change worth its price?",
            "equations": [EQ_VOI],
            "symbols": (
                "VOI(O) is the average of the best expected reward after each report minus the best expected reward without looking. Pr(o | b) is the chance of "
                "report o. In the chapter's verification tool, releasing a supported claim earns 10, an unsupported one loses 40, declining earns 0, the tool reports "
                "pass on 90 percent of supported claims and fail on 85 percent of unsupported ones, and releasing beats declining when the belief is above 0.8. The "
                "notebook cases use rewards (10, -10) and (-10, 10) for default and changed, and (5, -4) and (0, 2) for transfer. The curve shows the value against the "
                "belief at the moment of decision. The price is zero, the case's own price, or the break-even price equal to the value."
            ),
            "prediction": "In the notebook changed case the two observation rows are identical. Is one report worth anything?",
            "prediction_options": ["Yes, about 8", "No, exactly 0", "Yes, about 1"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Identical rows leave the belief at (0.5, 0.5) after any report, so the same action stays best and the value is exactly 0; at price 1 the net is (-1).",
                "incorrect": "Choose the notebook changed case: identical rows leave the belief unchanged, the best action never changes, and the value is exactly 0.",
            },
            "explanation": (
                "After each report the controller picks its best action, and Equation (8.5) averages those best rewards by how likely each report is. If the same action "
                "is best after every report, the average equals the best reward without looking and the value is exactly 0. Only beliefs where a report can push the "
                "decision across its threshold give a positive value, and the chapter's tool peaks at 0.8 where the two actions tie. Free information never hurts; priced "
                "information must clear its price."
            ),
            "application": (
                "Before paying for a check, ask whether any answer it could give would change what you do. If not, its value is 0 however reassuring it sounds. "
                "If so, compare the value with the price of the check."
            ),
            "assumptions": (
                "One report, one decision afterward, a fixed price for looking, and the stipulated rewards and rates. The band describes beliefs, not how often cases "
                "land in it. Real tools can fail in ways the rates do not describe, and checking takes time that a single price may not capture. The price 1.0 for the "
                "chapter's tool is defined for this reader."
            ),
            "check": "With the chapter's tool, prior 0.5 and no price, what is the value of the look?",
            "answer": (
                "After a pass: 0.9 x 0.5 x 10 - 0.15 x 0.5 x 40 = 4.5 - 3.0 = 1.5, so release. After a fail: 0.1 x 0.5 x 10 - 0.85 x 0.5 x 40 = "
                "0.5 - 17.0 = (-16.5), so decline at 0. Acting now: 10 x 0.5 - 40 x 0.5 = (-15), so decline at 0. Value = 1.5 + 0 - 0 = 1.5."
            ),
            "provenance": (
                "Constructed example: the chapter's verification-tool instance (rewards 10, -40 and 0; pass 0.90 and fail 0.85; value 3.0 at prior 0.6), and the laboratory "
                "notebook's default, changed and transfer cases, computed with the laboratory's belief function; the price 1.0 is defined for this reader."
            ),
            "source_section": "The condition that makes a look worthless",
            "source_anchor": "the-condition-that-makes-a-look-worthless",
            "misconception": {
                "title": "A sharper belief is worth its price",
                "text": ("The chapter says uncertainty reduction earns its cost only through the decisions it can improve. Information stops being a virtue and "
                         "becomes a line item: a look that never changes the action is worth exactly 0 however much it changes the belief."),
            },
            "scope_note": {
                "text": "The worked release numbers are constructed for teaching.",
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "case", "label": "Case", "values": ["tool", "default", "changed", "transfer"], "default": "tool",
                 "value_labels": ["Chapter verification tool, prior 0.6", "Notebook default", "Notebook changed (identical rows)", "Notebook transfer"]},
                {"key": "price", "label": "Price of the look", "values": ["free", "case", "even"], "default": "free",
                 "value_labels": ["Free", "The case's own price", "Break-even price"]},
            ],
            "function": "look_picture",
        },
    ],
}

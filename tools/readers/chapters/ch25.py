"""Chapter 25 reader: Improving an Agent Without Trusting the Improvement.

Four demonstrations built on Equations (25.1) to (25.4).

Demonstration 1 counts the candidate versions a bounded change family
contains (Equation 25.1). Demonstration 2 calls the laboratory's own
development-guard gate (math_ai_agents.chapters.ch25.evaluate) on the
book-sized teaching cases, so reader, notebook and chapter skill agree
(Equation 25.2). Demonstration 3 evaluates the chapter's constructed
false-accept bound (Equation 25.3) and compares it with one exact tail.
Demonstration 4 evaluates the four-condition acceptance rule (Equation
25.4); the laboratory gate implements only a simpler rule, so those
numbers are computed directly. Every number is a constructed teaching
value; no result about a real agent is claimed.
"""
import math
from fractions import Fraction
from functools import lru_cache

import numpy as np
from matplotlib.ticker import MaxNLocator

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


def sig(x, digits=3):
    """Fixed-decimal text with the given number of significant digits (no exponent)."""
    x = float(x)
    if x == 0:
        return "0"
    places = max(0, digits - 1 - int(math.floor(math.log10(abs(x)))))
    return f"{x:.{places}f}"


# Demonstration 1: the change family

PARTS = ["Prompt template", "Tool-routing rule", "Memory policy", "Verifier", "Retry cap"]


def family_sizes(parts, variants):
    """One edit at a time: parts x variants. Any combination: (variants + 1)^parts - 1."""
    return parts * variants, (variants + 1) ** parts - 1


def family_picture(parts=3, variants=2):
    parts, variants = int(parts), int(variants)
    one_edit, combos = family_sizes(parts, variants)
    fig, (left, right) = new_figure(ncols=2, height=4.3)

    rows = PARTS + ["Model weights theta"]
    ypos = np.arange(len(rows))[::-1]
    for i, (y, name) in enumerate(zip(ypos, rows)):
        if i < len(PARTS) and i < parts:
            left.barh(y, 1, height=0.7, color=PALETTE["teal"])
            text = "editable"
        elif i < len(PARTS):
            left.barh(y, 1, height=0.7, color="#e6eaee", edgecolor=PALETTE["grey"], hatch="///", linewidth=1)
            text = "outside the family"
        else:
            left.barh(y, 1, height=0.7, color="#e6eaee", edgecolor=PALETTE["ink"], hatch="xxx", linewidth=1.4)
            text = "frozen, never edited"
        on_dark = i < parts and i < len(PARTS)
        left.text(0.5, y, text, ha="center", va="center", fontsize=10.5, color="white" if on_dark else PALETTE["ink"],
                  bbox=None if on_dark else BOX)
    left.set_yticks(ypos, rows)
    left.set_xticks([])
    left.set_xlim(0, 1)
    left.set_ylim(-0.6, len(rows) - 0.4)
    left.grid(alpha=0)
    left.set_xlabel("Solid teal rows may be changed by the family;\nhatched rows may not")
    left.set_ylabel("Part of the agent")
    left.set_title("What a change may touch", fontsize=11.5)

    labels = ["One edit\nat a time", "Any combination\nof edits"]
    bars = right.bar([0, 1], [one_edit, combos], width=0.55, color=[PALETTE["teal"], "#f1d9c9"],
                     edgecolor=[PALETTE["teal"], PALETTE["terracotta"]], linewidth=1.2)
    bars[1].set_hatch("///")
    top = max(one_edit, combos)
    for x, v in ((0, one_edit), (1, combos)):
        right.text(x, v + top * 0.02, str(v), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    right.set_xticks([0, 1], labels)
    right.set_xlim(-0.6, 1.6)
    right.set_ylim(0, top * 1.15)
    right.yaxis.set_major_locator(MaxNLocator(integer=True))
    right.set_xlabel("How the change family is described")
    right.set_ylabel("Candidate versions to review")
    right.set_title("Size of the family", fontsize=11.5)

    metrics = {
        "Parts the family may edit": str(parts),
        "Alternative settings per part": str(variants),
        "Versions, one edit at a time": str(one_edit),
        "Versions, any combination of edits": str(combos),
        "Model parameters changed": "0 (theta stays frozen)",
    }
    plural = "" if parts == 1 else "s"
    if combos == one_edit:
        ratio_text = "the same number, because with one part there is nothing to combine"
        closing = ("A family you can list is a family you can version and review; with one part the two descriptions "
                   "coincide, so neither is harder to review than the other.")
    else:
        ratio_text = f"{fmt(combos / one_edit, 1)} times as many to describe and compare"
        closing = ("A family you can list is a family you can version and review; the second description grows "
                   "multiplicatively, which makes exhaustive human review impractical.")
    interpretation = (
        f"One edit at a time: {parts} part{plural} x {variants} alternatives = {one_edit} candidate versions. Allowing any "
        f"combination, each part is either left alone or set to one of {variants} alternatives, so the count is "
        f"({variants} + 1)^{parts} - 1 = {(variants + 1) ** parts} - 1 = {combos} versions, which is "
        f"{ratio_text}. In both cases theta at step t + 1 equals "
        f"theta at step t, so no model parameter is edited. {closing}"
    )
    return fig, metrics, interpretation


# Demonstration 2: development selects, the guard checks one frozen choice

BASELINE = [True, False, True, False]
CANDIDATES = {
    "default": {
        "flashy": {"development": [True, True, True, True], "guard": [True, False, True, False]},
        "steady": {"development": [True, True, True, False], "guard": [True, True, True, False]},
    },
    "changed": {
        "flashy": {"development": [True, True, True, True], "guard": [True, True, True, False]},
        "steady": {"development": [True, True, True, False], "guard": [True, True, True, False]},
    },
}


def lab_gate(case, threshold, reused):
    data = {
        "baseline_guard": BASELINE,
        "minimum_guard_gain": float(threshold),
        "guard_reused": bool(reused),
        "candidates": [dict(name=n, **v) for n, v in CANDIDATES[case].items()],
    }
    return evaluate(data)


def value_label_height(value, threshold):
    """Height and alignment for a bar's value label so the threshold line never crosses the text.

    A label spans about 0.06 of the axis height. Try above the bar, then the middle of the bar, then
    just above the threshold line.
    """
    half = 0.04
    for y, va, lo, hi in ((value + 0.03, "bottom", value + 0.03, value + 0.03 + 2 * half),
                          (value / 2, "center", value / 2 - half, value / 2 + half)):
        if value >= 0.12 or va == "bottom":
            if not (lo - 0.015 <= threshold <= hi + 0.015):
                return y, va
    return threshold + 0.02, "bottom"


def gate_picture(case="default", guard="clean", threshold=0.2):
    reused = guard == "reused"
    out = lab_gate(case, threshold, reused)
    rows = {r["name"]: r for r in out["tables"]}
    names = list(rows)
    chosen = out["metrics"]["selected_candidate"]
    accepted = bool(out["metrics"]["release_accepted"])
    gain = out["metrics"]["selected_guard_gain"]
    other = next(n for n in names if n != chosen)
    m = len(BASELINE)
    diffs = [int(g) - int(b) for g, b in zip(CANDIDATES[case][chosen]["guard"], BASELINE)]

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    for ax, key in ((left, "development_rate"), (right, "guard_gain")):
        for i, n in enumerate(names):
            picked = n == chosen
            ax.bar(i, rows[n][key], width=0.55, color=PALETTE["teal"] if picked else "#e6eaee",
                   edgecolor=PALETTE["teal"] if picked else PALETTE["grey"], hatch=None if picked else "///", linewidth=1.2)
            v = rows[n][key]
            if key == "guard_gain":
                ypos, va = value_label_height(v, float(threshold))
            else:
                ypos, va = v + 0.03, "bottom"
            ax.text(i, ypos, fmt(v, 2), ha="center", va=va, fontsize=11, color=PALETTE["ink"], bbox=BOX)
        ax.set_xticks(range(len(names)), [f"{n}\n(selected)" if n == chosen else f"{n}\n(not selected)" for n in names])
        ax.set_xlim(-0.6, len(names) - 0.4)
    left.set_ylim(0, 1.2)
    left.set_xlabel("Candidate procedure")
    left.set_ylabel("Development success rate")
    left.set_title("Step 1: development picks one", fontsize=11.5)

    right.axhline(float(threshold), color=PALETTE["ink"], linestyle="dashed", linewidth=1.4)
    right.set_ylim(-0.05, 0.5)
    right.set_xlabel("Candidate procedure")
    right.set_ylabel("Guard gain over the parent")
    right.set_title("Step 2: guard checks the frozen pick" + ("\n(guard was reused)" if reused else ""), fontsize=11.5)

    if reused:
        verdict = (f"The guard was reused, so release is rejected whatever the gain: once guard outcomes have shaped a "
                   f"decision, the guard is development evidence and no longer a test of {chosen}.")
        release = "rejected (guard reused)"
    elif accepted:
        verdict = f"{fmt(gain, 2)} is at least {fmt(threshold, 2)}, so {chosen} clears this finite gate."
        release = "accepted by this gate"
    else:
        verdict = f"{fmt(gain, 2)} is below {fmt(threshold, 2)}, so {chosen} fails this finite gate."
        release = "rejected (gain below threshold)"
    right.text(0.02, 0.98, f"dashed line: threshold {fmt(threshold, 2)}\nrelease: {release}", transform=right.transAxes,
               ha="left", va="top", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
    other_gain = rows[other]["guard_gain"]
    switch = (f" {other} has guard gain {fmt(other_gain, 2)}, but moving to it after reading guard outcomes would put the "
              "guard inside the selection, so the rule does not allow it.")
    dev_text = ", ".join(f"{n} {sum(CANDIDATES[case][n]['development'])}/{len(CANDIDATES[case][n]['development'])} = "
                         f"{fmt(rows[n]['development_rate'], 2)}" for n in names)
    sum_text = " + ".join(signed(d, 0) for d in diffs)
    metrics = {
        "Development rates": ", ".join(f"{n} {fmt(rows[n]['development_rate'], 2)}" for n in names),
        "Selected on development": chosen,
        "Guard gain of the selected": fmt(gain, 2),
        "Threshold": fmt(threshold, 2),
        "Guard status": "reused" if reused else "clean (used once)",
        "Release decision": release,
    }
    interpretation = (
        f"Development rates: {dev_text}; the highest is {chosen}, so it is frozen. Its paired guard differences "
        f"(candidate minus parent) are {sum_text}, so guard gain = ({sum_text}) / {m} = {fmt(gain, 2)}. {verdict}{switch}"
    )
    return fig, metrics, interpretation


# Demonstration 3: the false-accept bound and the cost of consulting a guard repeatedly

TAU = 0.25


def hoeffding(m, tau=TAU):
    return math.exp(-m * tau * tau / 2)


@lru_cache(maxsize=None)
def exact_tail(m, tau=TAU):
    """P(mean of m fair plus-or-minus 1 outcomes >= tau): one distribution with true uplift 0."""
    need = math.ceil(Fraction(m) * (1 + Fraction(str(tau))) / 2)  # least number of +1 outcomes
    total = sum(math.comb(m, k) for k in range(need, m + 1))
    return float(Fraction(total, 2 ** m))


def bound_picture(guard_cases=200, decisions=10):
    m, q = int(guard_cases), int(decisions)
    single = hoeffding(m)
    union = q * single
    exact = exact_tail(m)
    grid = np.arange(10, 401, 10)
    bound_curve = np.exp(-grid * TAU * TAU / 2)
    exact_curve = np.array([exact_tail(int(g)) for g in grid])

    fig, ax = new_figure(height=4.3)
    ax.plot(grid, bound_curve, color=PALETTE["navy"], linewidth=2)
    ax.plot(grid, exact_curve, color=PALETTE["teal"], linewidth=2, linestyle=(0, (5, 2)))
    ax.axhline(1.0, color=PALETTE["grey"], linewidth=1.2, linestyle=":")
    ax.plot([m], [single], "o", color=PALETTE["navy"], markersize=9)
    ax.plot([m], [exact], "s", color=PALETTE["teal"], markersize=8)
    keys = []
    if q > 1:
        ax.plot(grid, q * bound_curve, color=PALETTE["terracotta"], linewidth=2, linestyle="dashdot")
        ax.plot([m], [union], "^", color=PALETTE["terracotta"], markersize=9)
        keys.append((f"dash-dot: {q} decisions, {q} x bound", PALETTE["terracotta"]))
    keys.append(("solid: bound, one decision", PALETTE["navy"]))
    keys.append(("dashed: exact tail, fair plus or minus 1", PALETTE["teal"]))
    for i, (text, color) in enumerate(keys):
        ax.text(0.98, 0.97 - 0.07 * i, text, transform=ax.transAxes, ha="right", va="top", fontsize=10.5, color=color)
    ax.text(0.98, 0.69, "dotted line: probability 1", transform=ax.transAxes, ha="right", va="top", fontsize=10.5,
            color=PALETTE["grey"])
    ax.set_yscale("log")
    ax.set_xlim(0, 405)
    ax.set_ylim(1e-8, 1e3)
    ax.set_xlabel("Number of guard cases m")
    ax.set_ylabel("Chance a no-benefit candidate clears 0.25")
    ax.set_title(f"Threshold 0.25; marked at m = {m}", fontsize=11.5)

    if union > 1:
        union_metric = f"{sig(union)} (above 1, says nothing)"
        union_note = (f" The {q}-decision total {sig(union)} is above 1, so as a probability bound it says nothing at "
                      f"this size; more guard cases or fewer decisions are needed.")
    elif q > 1:
        union_metric = sig(union)
        union_note = (f" Over {q} decisions that each fix the candidate before guard access, the total is at most "
                      f"{q} x {sig(single)} = {sig(union)}.")
    else:
        union_metric = f"{sig(union)} (one decision)"
        union_note = f" With a single guard decision there is nothing to add up: 1 x {sig(single)} = {sig(single)}."
    metrics = {
        "Guard cases m": str(m),
        "Bound, one decision": sig(single),
        f"Bound, {q} decision{'' if q == 1 else 's'}": union_metric,
        "Exact tail, fair plus or minus 1 case": sig(exact),
        "Bound divided by exact tail": fmt(single / exact, 1),
    }
    interpretation = (
        f"Exponent = m x tau^2 / 2 = {m} x {fmt(TAU * TAU, 4)} / 2 = {fmt(m * TAU * TAU / 2, 3)}, so the bound is "
        f"exp(-{fmt(m * TAU * TAU / 2, 3)}) = {sig(single)}.{union_note} One concrete no-benefit guard (each paired outcome plus 1 or minus 1 with equal "
        f"chance) clears 0.25 with exact probability {sig(exact)}, below the bound, as it must be. Every number holds "
        "only if the candidate was fixed before guard access, outcomes lie in [-1, 1] and are independent."
    )
    return fig, metrics, interpretation


# Demonstration 4: four conditions, all required

CONSTRAINT = 1.0   # c, the current cost limit (constructed units)
MARGIN = 0.1       # epsilon_safe, the reserved margin
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
        left.bar(x, v, width=0.5, color=PALETTE["teal"] if ok else "#f1d9c9",
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
        right.barh(y, 1, height=0.7, color=PALETTE["teal"] if ok else "#f1d9c9",
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
        tail = "All four conditions hold, so the version may enter the limited canary."
    else:
        tail = "Rejected because " + "; ".join(reasons) + ". No strong condition can pay for a failed one."
    interpretation = (
        f"Limit = c - margin = {fmt(CONSTRAINT, 2)} - {fmt(MARGIN, 2)} = {fmt(limit, 2)}. Conditions: uplift {fmt(uplift, 2)} "
        f">= 0.25 gives {c1}; cost {fmt(cost, 2)} <= {fmt(limit, 2)} gives {c2}; authorized gives {c3}; rollback gives {c4}. "
        f"accept = {c1} x {c2} x {c3} x {c4} = {accept}. {tail}"
    )
    return fig, metrics, interpretation


CHAPTER = {
    "number": 25,
    "title": "Improving an Agent Without Trusting the Improvement",
    "subtitle": "An agent can propose a useful change without supplying independent evidence that the change should be released.",
    "summary": (
        "These four demonstrations follow one proposed change to an agent's procedure: what a bounded family of changes "
        "contains, why the development winner cannot certify itself, how much a frozen guard can tell you and how quickly "
        "repeated use erodes it, and why release needs four separate conditions. All values are constructed teaching "
        "examples, not measurements of any real system."
    ),
    "demos": [
        {
            "id": "C25-D01",
            "title": "What a change is allowed to touch",
            "question": "If the model weights stay frozen, how many candidate procedure versions must be described and reviewed?",
            "equations": [EQ_FAMILY],
            "symbols": (
                "theta is the set of model parameters, frozen here, so theta at step t + 1 equals theta at step t. phi_t is "
                "version t of the procedure: the prompt template, tool-routing rule, memory policy, verifier and retry cap "
                "assembled around the model. e_t is a recorded trial outcome. M is the change family, the set of procedure "
                "versions that e_t is allowed to propose. phi' is one proposed version."
            ),
            "prediction": "Go from 3 editable parts to 5 with 2 alternatives each. Which count grows faster, and by roughly how much?",
            "explanation": (
                "Equation (25.1) says the proposal comes from a named family built around the current version, and that the "
                "weights do not move. If the family allows one edit at a time, its size is the number of parts times the "
                "alternatives per part. If it allows any combination of edits, each part is either left alone or set to one "
                "alternative, which multiplies the options, so the count grows multiplicatively and exhaustive human review becomes impractical."
            ),
            "application": (
                "Before an improvement loop starts, write down the parts of the procedure it may edit and the alternatives for "
                "each. A family you can list can be versioned, compared with its parent and rolled back."
            ),
            "assumptions": (
                "A deliberately simple count: the five parts are five of the examples the chapter lists, alternatives are counted as distinct "
                "settings, and a version is just a choice of settings. A real family may have continuous settings or "
                "interactions that make the count larger, and the count says nothing about whether any version is good."
            ),
            "check": "A family may edit 4 parts of the procedure, each with 3 alternatives. How many versions with one edit at a time, and how many if any combination were allowed?",
            "answer": "One edit at a time: 4 x 3 = 12. Any combination: (3 + 1)^4 - 1 = 256 - 1 = 255.",
            "provenance": "Constructed example: five of the procedure parts the chapter lists, with counts defined for this reader.",
            "source_section": "The procedure is the mutable object",
            "source_anchor": "the-procedure-is-the-mutable-object",
            "controls": [
                {"key": "parts", "label": "Parts of the procedure the family may edit", "values": [1, 2, 3, 5], "default": 3},
                {"key": "variants", "label": "Alternative settings per part", "values": [2, 3], "default": 2},
            ],
            "function": "family_picture",
        },
        {
            "id": "C25-D02",
            "title": "Development chooses, the guard checks one frozen pick",
            "question": "Once development has picked a winner, what does a separate guard set decide, and what breaks if it is reused?",
            "equations": [EQ_SELECT],
            "symbols": (
                "D is the development set and G the guard set. V-hat_D(phi) is a procedure's estimated success on D, and "
                "Delta-hat_D(phi_j) is candidate j's development uplift over the parent phi_t. The arg max picks the winner "
                "phi'. For guard case i, Z_i is the candidate's result minus the parent's, between -1 and 1, and "
                "Delta-hat_G is the average of Z_i over the m guard cases. The threshold is the smallest guard gain accepted. Two candidate procedures are compared, named flashy and steady "
                "for this teaching case; the names are labels only."
            ),
            "prediction": "In the laboratory's default case with threshold 0.20, which candidate does development pick, and does it pass the guard?",
            "explanation": (
                "Development picks the candidate with the best development score, here by success rate. Only that frozen "
                "candidate is then compared with the parent on guard cases, and the average paired difference is its guard "
                "gain. The other candidate may look better on the guard, but choosing it after seeing the guard would make "
                "the guard part of selection. If the guard was already reused, the gate rejects regardless of the gain."
            ),
            "application": (
                "Write down which candidate is frozen, and the threshold, before anyone opens guard outcomes. Report guard "
                "numbers for the frozen candidate only, and treat any guard that has informed a redesign as development data."
            ),
            "assumptions": (
                "Four paired cases with binary outcomes, in the laboratory's teaching case. With four cases the gain can only "
                "be a multiple of 0.25, so a gate this small is a teaching device, and a threshold is a rule, not a confidence statement. The reuse flag records "
                "what you declare, not the true history, and the threshold is only meaningful if fixed before guard access."
            ),
            "check": "A frozen candidate beats its parent on 2 of 8 guard cases, loses on 1 and ties on 5. Its threshold is 0.20. Does it pass a clean guard?",
            "answer": "Gain = (2 x 1 + 1 x (-1) + 5 x 0) / 8 = 1/8 = 0.125, which is below 0.20, so it does not pass.",
            "provenance": "Constructed example: the laboratory's four-case development and guard teaching data, computed with its own gate function.",
            "source_section": "Development can choose a candidate; it cannot certify one",
            "source_anchor": "development-can-choose-a-candidate-it-cannot-certify-one",
            "controls": [
                {"key": "case", "label": "Guard outcomes for the frozen winner", "values": ["default", "changed"], "default": "default",
                 "value_labels": ["Laboratory default (winner matches the parent)", "Changed (winner repairs one case)"]},
                {"key": "guard", "label": "Guard history", "values": ["clean", "reused"], "default": "clean",
                 "value_labels": ["Clean (first use)", "Reused (outcomes shaped a decision)"]},
                {"key": "threshold", "label": "Smallest accepted guard gain", "values": [0.2, 0.3], "default": 0.2},
            ],
            "function": "gate_picture",
        },
        {
            "id": "C25-D03",
            "title": "How little a guard promises, and how it wears out",
            "question": "How likely is a candidate with no true benefit to clear a guard threshold, and what does repeated use do to that number?",
            "equations": [EQ_BOUND],
            "symbols": (
                "m is the number of guard cases. Each paired difference Z_i lies between -1 and 1 and has true mean Delta, "
                "which is at most 0 for a candidate with no benefit. Delta-hat_G is the guard average. The threshold tau is 0.25, "
                "as in the chapter. exp(x) is e raised to the power x. The decision count q is how many separately fixed "
                "candidates use the guard, each added once."
            ),
            "prediction": "At 200 guard cases the bound for one decision is 0.00193. Switch to ten decisions, then drop to 50 cases. What happens to the total?",
            "explanation": (
                "The bound exp(-m x 0.25^2 / 2) shrinks quickly as guard cases are added. For several candidates, each fixed "
                "before it meets the guard, the chances add up, so ten decisions cost ten times the single bound. The exact "
                "tail for one concrete no-benefit guard is also shown: it lies below the bound, which is a worst-case "
                "guarantee, not a prediction. At 50 cases ten decisions sum to more than 1, so the bound says nothing."
            ),
            "application": (
                "Set a guard query budget before use. Count how many candidates will be tested, size the guard so the total "
                "stays small, and retire the guard for release evidence once its results start steering redesign."
            ),
            "assumptions": (
                "The chapter's constructed conditions: every candidate is fixed before guard access, outcomes lie in [-1, 1], "
                "and outcomes are independent across cases. Shared tool state or a common evaluator can break independence. "
                "Once a guard result changes the next candidate, the adding-up no longer holds and a fresh guard is needed. "
                "The exact tail uses one convenient distribution, plus or minus 1 with equal chance; it is not a real agent."
            ),
            "check": "With m = 300 guard cases and threshold 0.25, what is the bound for one decision?",
            "answer": "exp(-300 x 0.0625 / 2) = exp(-9.375) = 0.0000848, about 8.5 in 100,000.",
            "provenance": "Constructed example: the chapter's own 200-case, 0.25 threshold, ten-decision values, with other sizes defined for this reader.",
            "source_section": "A guard becomes development evidence when it is consulted repeatedly",
            "source_anchor": "a-guard-becomes-development-evidence-when-it-is-consulted-repeatedly",
            "controls": [
                {"key": "guard_cases", "label": "Number of guard cases m", "values": [50, 100, 200, 400], "default": 200},
                {"key": "decisions", "label": "Candidates tested on the guard", "values": [1, 10], "default": 10},
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
            "explanation": (
                "Equation (25.4) turns each condition into a pass or fail, then requires all four. Cost is held to c minus a "
                "margin, so a cost of 0.95 fails even though it is under c. The conditions multiply instead of adding, so a "
                "zero anywhere gives zero overall, however large the uplift. Authority and rollback are yes or no, not "
                "scores that can be traded against performance."
            ),
            "application": (
                "Write a release record with four lines: uplift against its threshold, cost against its limit minus margin, "
                "the named authority holder and scope, and the tested rollback route. A missing line blocks release."
            ),
            "assumptions": (
                "Constructed values for one candidate, with uplift and cost already estimated on a clean guard (see "
                "Demonstration 3 for what that requires). The laboratory's gate in Demonstration 2 checks only the uplift "
                "threshold and the reuse flag, so cost, authority and rollback are computed directly here. A passing record "
                "permits a limited canary; it does not show that the change is safe at scale."
            ),
            "check": "A candidate has uplift 0.40, cost 0.92, authority granted and rollback tested, with c = 1.00 and margin 0.10. Is it accepted?",
            "answer": "The limit is 1.00 - 0.10 = 0.90 and 0.92 > 0.90, so the cost condition is 0 and accept = 1 x 0 x 1 x 1 = 0.",
            "provenance": "Constructed example: the chapter's threshold 0.25 with cost limit, margin and candidate values defined for this reader.",
            "source_section": "Acceptance is a constrained release decision",
            "source_anchor": "acceptance-is-a-constrained-release-decision",
            "controls": [
                {"key": "uplift", "label": "Guard uplift estimate", "values": [0.2, 0.45], "default": 0.45},
                {"key": "others", "label": "Cost, authority and rollback", "values": ["all", "cost", "authority", "rollback"],
                 "default": "all",
                 "value_labels": ["All pass (cost 0.80)", "Cost 0.95, over the limit", "No authority for this scope", "Rollback untested"]},
            ],
            "function": "accept_picture",
        },
    ],
}

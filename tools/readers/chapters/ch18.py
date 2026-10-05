"""Chapter 18 reader: When an Action Has Coordinates.

Four demonstrations built on Equations (18.1) to (18.3).

Demonstration 1 draws the release console's two layouts and compares the chapter's three interfaces (a
coordinate, a semantic control and a transactional request that carries the saved version); each
interface's issuance and target correctness come from the laboratory's own interface calculation
(math_ai_agents.chapters.ch18.evaluate). Demonstration 2 shows which commands survive across the layouts
still considered possible, and what a further observation does to that support. Demonstration 3 runs the
laboratory's default, changed and transfer cases (the three interfaces against age, version and
permission) beside the constant-rate freshness curve. Demonstration 4 prices another look, including the
chapter exercise with a look costing 1. Every number is a constructed teaching value.
"""
import math

import numpy as np
from matplotlib.patches import Rectangle

from math_ai_agents.chapters.ch18 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure

EQ_TRANSITION = (
    r"P_{\mathrm{ui}}(x'\mid x,a)=\sum_{\tilde a\in\operatorname{Act}_{\mathrm{ui}}}"
    r"\operatorname{Exec}_{\mathrm{ui}}(\tilde a\mid x,a)P(x'\mid x,\tilde a)"
)
EQ_ROBUST = r"\mathcal A_{\mathrm{rob}}(\mathbf b)=\bigcap_{x:\,\mathbf b(x)>0}\mathcal A_{\mathrm{auth}}(x)"
EQ_FRESH = r"\operatorname{Fresh}(\Delta)=\exp(-\lambda_{\mathrm{ui}}\Delta)"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


# Demonstration 1: the interface in the transition law

INTERFACES = {
    "coordinate": "Coordinate: click the saved point",
    "semantic": "Semantic: request the control bound to v2",
    "transactional": "Transactional: v2 with the saved screen version",
}
LAB_METHOD = {"coordinate": "coordinate", "semantic": "semantic", "transactional": "version-bound"}
LAYOUT_INPUTS = {
    # layout 1: the saved observation still matches the screen; layout 2: the rows have swapped and the version differs
    1: {"observation_age": 1, "max_age": 2, "observed_version": "layout-1", "current_version": "layout-1",
        "current_permission": True, "effect_confirmed": True, "coordinate_target": "v2", "semantic_target": "v2",
        "wanted_target": "v2"},
    2: {"observation_age": 1, "max_age": 2, "observed_version": "layout-1", "current_version": "layout-2",
        "current_permission": True, "effect_confirmed": True, "coordinate_target": "v3", "semantic_target": "v2",
        "wanted_target": "v2"},
}


def realized(interface, layout, check_on):
    """What the interface does in a layout: 'v2', 'v3' or 'denied'. Issuance and target come from the laboratory."""
    row = next(r for r in evaluate(LAYOUT_INPUTS[layout])["tables"] if r["method"] == LAB_METHOD[interface])
    if not row["issued"]:
        return "denied"  # the version-bound request is refused before any effect
    if row["correct_target"] and row["confirmed_completion"]:
        return "v2"
    return "denied" if check_on else "v3"


def draw_screens(ax, interface, check_on):
    ink = PALETTE["ink"]
    for lx, (upper, lower) in enumerate([("v2", "v3"), ("v3", "v2")]):
        x0 = lx * 1.25
        ax.add_patch(Rectangle((x0, 0), 1, 1, facecolor="#f4f6f6", edgecolor=ink, linewidth=1.2))
        rows = {}
        for ri, doc in enumerate((upper, lower)):
            y0 = 0.52 if ri == 0 else 0.06
            approved = doc == "v2"
            ax.add_patch(Rectangle((x0 + 0.05, y0), 0.9, 0.40, facecolor="#cfe6e6" if approved else "#f0d6cf",
                                   edgecolor="white", linewidth=1.5, hatch=None if approved else "///"))
            ax.text(x0 + 0.08, y0 + 0.2, f"{doc} approved" if approved else f"{doc} unapproved", va="center",
                    fontsize=10.5, color=ink, bbox=BOX)
            ax.add_patch(Rectangle((x0 + 0.76, y0 + 0.1), 0.16, 0.2, facecolor="white", edgecolor=ink, linewidth=1.0))
            rows[doc] = (x0 + 0.84, y0 + 0.2)
        upper_btn = (x0 + 0.84, 0.72)
        layout = lx + 1
        outcome = realized(interface, layout, check_on)
        if interface == "coordinate":
            target = upper_btn
        elif interface == "semantic":
            target = rows["v2"]
        else:
            target = rows["v2"] if outcome == "v2" else None
        if target is not None:
            ax.plot([target[0]], [target[1]], marker="*", markersize=15, color=PALETTE["gold"], markeredgecolor=ink, zorder=5)
        caption = {"v2": "reaches v2", "v3": "reaches v3",
                   "denied": "refused: version differs" if interface == "transactional" else "reaches v3: denied"}[outcome]
        ax.text(x0 + 0.5, -0.06, caption, ha="center", va="top", fontsize=10.5, color=ink)
    ax.set_xlim(-0.05, 2.3)
    ax.set_ylim(-0.3, 1.05)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("Left: layout 1 (observed). Right: layout 2 (rows swapped)")
    ax.set_ylabel("Screen (schematic, star = the command)")
    ax.grid(False)


def transition_picture(interface="coordinate", belief_layout1=0.8, permission_check="off"):
    b1 = float(belief_layout1)
    b2 = 1.0 - b1
    on = permission_check == "on"
    out1 = realized(interface, 1, on)
    out2 = realized(interface, 2, on)
    keys = ("v2", "v3", "denied")
    exec1 = {k: 1 if out1 == k else 0 for k in keys}
    exec2 = {k: 1 if out2 == k else 0 for k in keys}
    predicted = {k: b1 * exec1[k] + b2 * exec2[k] for k in keys}
    names = {"v2": "Release v2 (authorized)", "v3": "Release v3 (not authorized)", "denied": "Denied or refused, no release"}
    colors = {"v2": PALETTE["teal"], "v3": PALETTE["terracotta"], "denied": PALETTE["navy"]}
    hatches = {"v2": "", "v3": "///", "denied": "\\\\\\"}
    fig, (left, right) = new_figure(ncols=2, height=4.2)
    draw_screens(left, interface, on)
    left.set_title(f"Where the {interface} command lands", fontsize=11.5)
    y = np.arange(3)[::-1]
    for yi, key in zip(y, keys):
        right.barh(yi, predicted[key], height=0.56, color=colors[key], hatch=hatches[key], edgecolor="white", linewidth=0)
        right.text(predicted[key] + 0.02, yi, fmt(predicted[key], 2), va="center", fontsize=11, color=PALETTE["ink"])
    right.set_yticks(y, [names[k] for k in keys])
    right.set_xlim(0, 1.18)
    right.set_xlabel("Predicted probability (constructed model)")
    right.set_ylabel("What the command does")
    right.grid(axis="y", alpha=0)
    right.set_title(f"Belief {fmt(b1, 2)} / {fmt(b2, 2)}, permission check {'on' if on else 'off'}", fontsize=11.5)
    metrics = {
        "Release v2 (authorized completion)": fmt(predicted["v2"], 2),
        "Release v3 (prohibited release)": fmt(predicted["v3"], 2),
        "Denied or refused, no release": fmt(predicted["denied"], 2),
        "Total": fmt(sum(predicted.values()), 2),
    }
    who = {
        "coordinate": "The coordinate command takes its target from whatever occupies the saved point when it arrives",
        "semantic": ("The semantic request names the control bound to v2, so swapping the rows does not move its target "
                     "(here the identifier is taken to resolve correctly; a mislabeled control would break that)"),
        "transactional": ("The transactional request names v2 and the saved version and the service checks the version at commit, "
                          "so in layout 2 the saved screen version differs from the current one and it is refused rather than guessed"),
    }[interface]
    if out2 == "v3":
        tail = ("With no check, the wrong-layout branch becomes a prohibited release with probability equal to the belief in that layout. "
                "Later detection could identify it but cannot make the recipient unsee the document.")
    elif interface == "coordinate":
        tail = ("The permission check turns the wrong-layout branch from a prohibited release into a denial; the belief about the screen "
                "did not change, only the enforcement did, and the controller must inspect the denial and obtain a fresh layout before proposing v2.")
    elif interface == "semantic":
        tail = "Completion is 1.00 in both layouts, so the belief does not matter for this command: the target does not depend on the layout."
    else:
        tail = ("Safety here comes from the version check, not from locating the button better: the refusal costs the completion in "
                "layout 2, and the next proposal needs a current observation and still-current authority.")
    interpretation = (
        f"Layout 1 (v2 on top) has belief {fmt(b1, 2)}; layout 2 (rows swapped) has {fmt(b2, 2)}. {who}. "
        f"P(release v2) = {fmt(b1, 2)} x {exec1['v2']} + {fmt(b2, 2)} x {exec2['v2']} = {fmt(predicted['v2'], 2)}. "
        f"P(release v3) = {fmt(b1, 2)} x {exec1['v3']} + {fmt(b2, 2)} x {exec2['v3']} = {fmt(predicted['v3'], 2)}. "
        f"P(no release) = {fmt(b1, 2)} x {exec1['denied']} + {fmt(b2, 2)} x {exec2['denied']} = {fmt(predicted['denied'], 2)}. "
        f"The three add to {fmt(sum(predicted.values()), 2)}, as a normalized transition law must. {tail}"
    )
    steps = [
        f"Layout 1: the {interface} command realizes {'release v2' if out1 == 'v2' else out1}; layout 2: {'release v2' if out2 == 'v2' else ('release v3' if out2 == 'v3' else 'a denial or refusal')}.",
        f"P(release v2) = {fmt(b1, 2)} x {exec1['v2']} + {fmt(b2, 2)} x {exec2['v2']} = {fmt(predicted['v2'], 2)}.",
        f"P(release v3) = {fmt(b1, 2)} x {exec1['v3']} + {fmt(b2, 2)} x {exec2['v3']} = {fmt(predicted['v3'], 2)}.",
        f"P(no release) = {fmt(b1, 2)} x {exec1['denied']} + {fmt(b2, 2)} x {exec2['denied']} = {fmt(predicted['denied'], 2)}.",
        f"Check: {fmt(predicted['v2'], 2)} + {fmt(predicted['v3'], 2)} + {fmt(predicted['denied'], 2)} = {fmt(sum(predicted.values()), 2)}.",
    ]
    alt = (f"Left: two screens, layout 1 with v2 on top and layout 2 with the rows swapped, and a star where the {interface} command lands "
           f"in each. Right: predicted probabilities of releasing v2 ({fmt(predicted['v2'], 2)}), releasing v3 ({fmt(predicted['v3'], 2)}) "
           f"and no release ({fmt(predicted['denied'], 2)}).")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: support-wide authorization

COMMANDS = [
    ("Click the saved point", (True, False)),
    ("Request release of v2", (True, True)),
    ("Read metadata", (True, True)),
    ("Take a fresh screenshot", (True, True)),
    ("Abstain", (True, True)),
]
OBSERVATIONS = {
    "none": "No further observation",
    "layout1": "A perfect read shows layout 1",
    "layout2": "A perfect read shows layout 2",
}


def robust_set_picture(belief_layout2=0.01, observation="none"):
    prior2 = float(belief_layout2)
    if observation == "none":
        b2 = prior2
    elif observation == "layout1":
        b2 = 0.0
    else:
        b2 = 1.0
    b1 = 1.0 - b2
    beliefs = (b1, b2)
    counted = [b > 0 for b in beliefs]
    survives = [all(auth[i] for i in range(2) if counted[i]) for _, auth in COMMANDS]
    n_survive = sum(survives)
    fig, ax = new_figure(width=7.4, height=4.5)
    n = len(COMMANDS)
    for r, (name, auth) in enumerate(COMMANDS):
        for c in range(2):
            if not counted[c]:
                ax.add_patch(Rectangle((c, r), 1, 1, facecolor="#eef1f2", edgecolor="white", linewidth=2))
                ax.text(c + 0.5, r + 0.5, "not counted", ha="center", va="center", fontsize=10.5, color=PALETTE["grey"])
            elif auth[c]:
                ax.add_patch(Rectangle((c, r), 1, 1, facecolor="#cfe6e6", edgecolor="white", linewidth=2))
                ax.text(c + 0.5, r + 0.5, "authorized", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"])
            else:
                ax.add_patch(Rectangle((c, r), 1, 1, facecolor="#f0d6cf", edgecolor="white", linewidth=2, hatch="///"))
                ax.text(c + 0.5, r + 0.5, "not authorized", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"],
                        bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.9})
        ok = survives[r]
        ax.add_patch(Rectangle((2, r), 1, 1, facecolor="#cfe6e6" if ok else "#f0d6cf", edgecolor="white", linewidth=2,
                               hatch="" if ok else "///"))
        ax.text(2.5, r + 0.5, "survives" if ok else "removed", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"],
                bbox=None if ok else {"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.9})
        blockers = [f"layout {i + 1}" for i in range(2) if counted[i] and not auth[i]]
        ax.add_patch(Rectangle((3, r), 1, 1, facecolor="white", edgecolor="#e1e4e5", linewidth=1))
        ax.text(3.5, r + 0.5, ("removed by\n" + " and ".join(blockers)) if blockers else "nothing\nremoves it", ha="center",
                va="center", fontsize=10.5, color=PALETTE["ink"])
    ax.set_xlim(0, 4)
    ax.set_ylim(n, 0)
    ax.set_xticks([0.5, 1.5, 2.5, 3.5], [f"Layout 1\nbelief {fmt(b1, 2)}", f"Layout 2\nbelief {fmt(b2, 2)}", "Kept by the\nintersection", "Which state\nremoved it"])
    ax.set_yticks(np.arange(n) + 0.5, [name for name, _ in COMMANDS])
    ax.set_xlabel("State considered possible, with its belief weight")
    ax.set_ylabel("Command")
    ax.grid(False)
    ax.tick_params(length=0)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    click_state = "survives" if survives[0] else "is removed"
    counted_names = [n_ for n_, flag in zip(("layout 1", "layout 2"), counted) if flag]
    removed = n - n_survive
    metrics = {
        "Belief in layout 1": fmt(b1, 2),
        "Belief in layout 2": fmt(b2, 2),
        "Layouts counted": " and ".join(counted_names),
        "Commands kept": f"{n_survive} of {n}",
        "Saved-point click": "kept" if survives[0] else "removed",
    }
    if observation == "layout1":
        lead = ("A perfect fresh read shows layout 1, so the belief becomes 1 and 0 and layout 2 leaves the support. "
                + ("That restores the click, but only if the read was current and correct." if float(belief_layout2) > 0 else
                   "The click was never removed here, because layout 2 already had zero belief, so the read confirms the support "
                   "rather than restoring anything; it helps only if the read was current and correct."))
    elif observation == "layout2":
        lead = ("A perfect fresh read shows layout 2, so the belief becomes 0 and 1 and only layout 2 counts.")
    else:
        lead = ""
    if all(counted):
        why = ("Both beliefs are above zero, so both layouts count, whatever their size. "
               "The click reaches an unapproved record in layout 2, so it is not authorized throughout the support.")
    elif counted[0]:
        why = ("Layout 2 has zero belief and is left out of the intersection, so only layout 1 constrains the set. "
               "That is safe only if the true layout really is layout 1.")
    else:
        why = ("Only layout 2 has positive belief, so the click, which reaches the unapproved record there, is not authorized. "
               "The other four commands stay authorized in layout 2.")
    interpretation = (
        f"{lead} Beliefs add to {fmt(b1, 2)} + {fmt(b2, 2)} = {fmt(b1 + b2, 2)}. {why} "
        f"Commands removed = {n} - {n_survive} = {removed}, so the saved-point click {click_state} and "
        f"{n_survive} of {n} commands remain. The request for v2 survives in either layout only because the service "
        "checks identity and approval at commit; belief alone never authorizes anything."
    ).strip()
    steps = [
        f"Beliefs: layout 1 = {fmt(b1, 2)}, layout 2 = {fmt(b2, 2)}; they add to {fmt(b1 + b2, 2)}.",
        f"States with positive belief: {' and '.join(counted_names)}.",
        "Each command must be authorized in every counted layout; the saved-point click is not authorized in layout 2.",
        f"Commands removed = {n} - {n_survive} = {removed}; the saved-point click {click_state}.",
    ]
    alt = (f"A grid of five commands against layout 1, layout 2, the intersection and the state that removed each command. "
           f"{n_survive} of {n} commands survive; the saved-point click {click_state}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: age, version, permission and freshness

SCENARIOS = {
    # the notebook's default, changed (age 3 beyond the limit of 2) and transfer cases
    "default": {"observation_age": 1, "max_age": 2, "observed_version": "layout-1", "current_version": "layout-2",
                "current_permission": True, "effect_confirmed": True, "coordinate_target": "delete",
                "semantic_target": "release", "wanted_target": "release", "change_rate": 0.02},
    "changed": {"observation_age": 3, "max_age": 2, "observed_version": "layout-1", "current_version": "layout-2",
                "current_permission": True, "effect_confirmed": True, "coordinate_target": "delete",
                "semantic_target": "release", "wanted_target": "release", "change_rate": 0.02},
    "transfer": {"observation_age": 0, "max_age": 1, "observed_version": "page-C", "current_version": "page-C",
                 "current_permission": False, "effect_confirmed": False, "coordinate_target": "submit",
                 "semantic_target": "submit", "wanted_target": "submit", "change_rate": 0.05},
}
CHAPTER_DELAYS = [5, 10, 15, 30]
COLUMNS = ["Age ok", "Version", "Allowed", "Issued", "Target", "Done"]


def lab_run(scenario, delay):
    data = dict(SCENARIOS[scenario], delays=[float(delay)])
    return evaluate(data)


def freshness_picture(scenario="default", delay=30):
    delay = float(delay)
    case = SCENARIOS[scenario]
    out = lab_run(scenario, delay)
    rows = out["tables"]
    rate = case["change_rate"]
    fresh = out["metrics"]["freshness_by_delay"][0]["freshness_probability"]
    if not math.isclose(fresh, math.exp(-rate * delay), rel_tol=1e-12):
        raise AssertionError("laboratory freshness disagrees with exp(-rate x delay)")
    product = rate * delay
    stale = 1 - fresh
    half_life = math.log(2) / rate
    age, max_age = case["observation_age"], case["max_age"]
    fig, (left, right) = new_figure(ncols=2, height=4.4)
    # table of the three interfaces against the laboratory's predicates
    for r, row in enumerate(rows):
        values = [row["fresh"], None if row["method"] != "version-bound" else row["version_matches"], row["authorized"],
                  row["issued"], row["correct_target"], row["confirmed_completion"]]
        for c, v in enumerate(values):
            if v is None:
                left.add_patch(Rectangle((c, r), 1, 1, facecolor="#eef1f2", edgecolor="white", linewidth=2))
                left.text(c + 0.5, r + 0.5, "not\nchecked", ha="center", va="center", fontsize=10.5, color=PALETTE["grey"])
            elif v:
                left.add_patch(Rectangle((c, r), 1, 1, facecolor="#cfe6e6", edgecolor="white", linewidth=2))
                left.text(c + 0.5, r + 0.5, "yes", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"])
            else:
                left.add_patch(Rectangle((c, r), 1, 1, facecolor="#f0d6cf", edgecolor="white", linewidth=2, hatch="///"))
                left.text(c + 0.5, r + 0.5, "no", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"],
                          bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.9})
    left.set_xlim(0, len(COLUMNS))
    left.set_ylim(3, 0)
    left.set_xticks(np.arange(len(COLUMNS)) + 0.5, COLUMNS)
    reach = {"coordinate": case["coordinate_target"], "semantic": case["semantic_target"], "version-bound": case["semantic_target"]}
    left.set_yticks(np.arange(3) + 0.5, [f"{r['method'].capitalize()}\nreaches {reach[r['method']]}" for r in rows])
    left.set_xlabel("Done = issued, right target and effect confirmed")
    left.set_ylabel("Interface (wanted target: " + case["wanted_target"] + ")")
    left.grid(False)
    left.tick_params(length=0)
    for side in ("top", "right", "left", "bottom"):
        left.spines[side].set_visible(False)
    left.set_title(f"Age {age:g} s, limit {max_age:g} s; saved {case['observed_version']}, now {case['current_version']}", fontsize=11.5)

    t = np.linspace(0, 40, 161)
    right.plot(t, np.exp(-rate * t), color=PALETTE["teal"], linewidth=2)
    marks = CHAPTER_DELAYS
    right.plot(marks, [math.exp(-rate * m) for m in marks], "o", markerfacecolor="white", markeredgecolor=PALETTE["teal"], markersize=7)
    right.plot([delay], [fresh], "o", color=PALETTE["terracotta"], markersize=10)
    right.vlines(delay, 0, fresh, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.2)
    right.hlines(fresh, 0, delay, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.2)
    if delay > 20:
        label_point(right, delay, fresh, f"Fresh = {fmt(fresh, 4)}", color=PALETTE["terracotta"], dx=-10, dy=-10, ha="right", va="top").set_bbox(BOX)
    else:
        label_point(right, delay, fresh, f"Fresh = {fmt(fresh, 4)}", color=PALETTE["terracotta"], dx=10, dy=10, ha="left").set_bbox(BOX)
    right.set_xlim(0, 40)
    right.set_ylim(0, 1.05)
    right.set_xlabel("Delay between observing and acting (seconds)")
    right.set_ylabel("Chance no invalidating change has occurred")
    right.set_title(f"Fresh = exp(-{fmt(rate, 2)} x delay)", fontsize=11.5)

    metrics = {
        "Rate": f"{fmt(rate, 2)} per second",
        "Delay": f"{fmt(delay, 0)} seconds",
        "Rate x delay": fmt(product, 2),
        "Chance still fresh": fmt(fresh, 4),
        "Chance of an invalidating change": fmt(stale, 4),
        "Delay at which freshness is one half": f"{fmt(half_life, 1)} seconds",
        "Observation age against the limit": f"{age:g} s against {max_age:g} s: {'fresh' if age <= max_age else 'stale'}",
        "Interfaces that issue": ", ".join(r["method"] for r in rows if r["issued"]) or "none",
        "Confirmed completions": ", ".join(r["method"] for r in rows if r["confirmed_completion"]) or "none",
    }
    row_by = {r["method"]: r for r in rows}
    verdict = []
    if age > max_age:
        verdict.append(f"The age rule fails ({age:g} > {max_age:g}), so all three interfaces refuse to issue, including the semantic one: "
                       "this contract requires a renewed observation before acting.")
    elif not case["current_permission"]:
        verdict.append("The observation is fresh and the versions match, but current permission is false, so every interface refuses: "
                       "a stable interface cannot manufacture authority.")
    else:
        verdict.append(f"The age rule passes ({age:g} <= {max_age:g}) yet the saved {case['observed_version']} differs from the current "
                       f"{case['current_version']}, so only the version-bound request refuses. The coordinate request is issued and reaches "
                       f"{case['coordinate_target']}, not {case['wanted_target']}, so it does not complete; the semantic request reaches "
                       f"{case['semantic_target']} and completes.")
    interpretation = (
        f"Rate x delay = {fmt(rate, 2)} x {fmt(delay, 0)} = {fmt(product, 2)}, a pure number with no unit left. "
        f"Fresh = exp(-{fmt(product, 2)}) = {fmt(fresh, 4)}, so the chance of at least one invalidating change is "
        f"1 - {fmt(fresh, 4)} = {fmt(stale, 4)}. Freshness reaches one half at 0.6931 / {fmt(rate, 2)} = {fmt(half_life, 1)} seconds. "
        f"The table uses the case's observation age ({age:g} s) and the curve uses the delay you choose ({fmt(delay, 0)} s): they are separate inputs, "
        f"so changing the delay moves the curve and not the table. {' '.join(verdict)}"
    )
    steps = [
        f"Rate x delay = {fmt(rate, 2)} x {fmt(delay, 0)} = {fmt(product, 2)}.",
        f"Fresh = exp(-{fmt(product, 2)}) = {fmt(fresh, 4)}; an invalidating change has chance 1 - {fmt(fresh, 4)} = {fmt(stale, 4)}.",
        f"Age rule: observation age {age:g} s against a limit of {max_age:g} s is {'fresh' if age <= max_age else 'stale'}.",
        f"Version: saved {case['observed_version']}, current {case['current_version']}; only the version-bound request compares them.",
        f"Current permission is {'true' if case['current_permission'] else 'false'}; issued = fresh and allowed (and, for version-bound, same version).",
        f"Issued: {metrics['Interfaces that issue']}. Confirmed completion: {metrics['Confirmed completions']}.",
    ]
    alt = (f"Left: a table of coordinate, semantic and version-bound interfaces against fresh, version, allowed, issued, target and done; "
           f"interfaces that issue: {metrics['Interfaces that issue']}. Right: freshness falls from 1 to {fmt(fresh, 2)} at {fmt(delay, 0)} seconds "
           f"at {fmt(rate, 2)} changes per second; the table does not depend on the delay.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: the price of another look

def another_look_picture(wrong_loss=40, wrong_chance=0.1, look_cost=2):
    loss, p, cost = float(wrong_loss), float(wrong_chance), float(look_cost)
    now = p * loss
    gain = now - cost
    p_star = cost / loss
    if math.isclose(now, cost, abs_tol=1e-9):
        decision = "tie"
        verdict = ("The two options cost the same, so the comparison does not choose. Other considerations, such as a "
                   "deadline or the cost of a denial, have to break the tie.")
    elif gain > 0:
        decision = "Observe first"
        verdict = f"Observing first removes an expected loss of {fmt(now, 2)} for a cost of {fmt(cost, 1)}, so it pays."
    else:
        decision = "Click now"
        verdict = f"Clicking now risks an expected loss of only {fmt(now, 2)}, below the {fmt(cost, 1)} cost of looking, so another look does not pay."
    if p == 0:
        verdict += (" With the command bound to v2 and its version checked at commit, a layout change no longer alters the target, so "
                    "the look has no value for document identity; it may still answer another question, such as whether a blocking dialog "
                    "needs a different procedure.")
    fig, (left, right) = new_figure(ncols=2, height=4.2)
    top = max(now, cost, 1.0) * 1.3
    left.bar([0], [now], width=0.55, color="white", edgecolor=PALETTE["terracotta"], hatch="///", linewidth=1.4)
    left.bar([1], [cost], width=0.55, color=PALETTE["teal"])
    left.text(0, now + top * 0.03, fmt(now, 2), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.text(1, cost + top * 0.03, fmt(cost, 2), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.set_xticks([0, 1], ["Click now", "Observe first"])
    left.set_xlim(-0.6, 1.6)
    left.set_ylim(0, top)
    left.set_xlabel("Option (hatched bar is expected loss)")
    left.set_ylabel("Expected cost (utility units)")
    left.set_title("Expected cost of each option", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    xmax = min(1.0, max(p, p_star) * 1.35 + 0.02)
    q = np.linspace(0, xmax, 101)
    right.plot(q, q * loss, color=PALETTE["terracotta"], linewidth=2)
    right.axhline(cost, color=PALETTE["teal"], linewidth=2)
    right.plot([p], [now], "o", color=PALETTE["terracotta"], markersize=9)
    right.plot([p_star], [cost], "s", color=PALETTE["ink"], markersize=7)
    label_point(right, xmax, cost, "cost of looking", color=PALETTE["teal"], dx=-4, dy=-6, ha="right", va="top")
    label_point(right, xmax, xmax * loss, "expected loss of clicking now", color=PALETTE["terracotta"], dx=-2, dy=5,
                ha="right", va="bottom")
    top_cost = max(xmax * loss, cost) * 1.22
    if p_star >= 0.25 * xmax:
        side = {"dx": -6, "ha": "right", "dy": 8, "va": "bottom"}
    elif cost >= 0.12 * top_cost:
        side = {"dx": 6, "ha": "left", "dy": -9, "va": "top"}
    else:
        # a cheap look leaves no room under the cost line: put the label above it, clear of the steep loss line
        side = {"dx": 40, "ha": "left", "dy": 6, "va": "bottom"}
    if math.isclose(now, cost, abs_tol=1e-9):
        label_point(right, p, now, f"tie at {fmt(p, 2)}", color=PALETTE["ink"], **side).set_bbox(BOX)
    else:
        label_point(right, p_star, cost, f"break-even {fmt(p_star, 3)}", color=PALETTE["ink"], **side).set_bbox(BOX)
        top_r = max(xmax * loss, cost) * 1.22
        if now < 0.12 * top_r:
            right.annotate(f"chosen {fmt(p, 2)}", (p, now), xytext=(0.5 * xmax, 0.2 * top_r), textcoords="data",
                           ha="left", va="center", color=PALETTE["terracotta"], fontsize=10.5, bbox=BOX,
                           arrowprops={"arrowstyle": "->", "color": PALETTE["terracotta"], "linewidth": 1.2})
        else:
            label_point(right, p, now, f"chosen {fmt(p, 2)}", color=PALETTE["terracotta"], dx=8, dy=-10, va="top").set_bbox(BOX)
    right.set_xlim(0, xmax)
    right.set_ylim(0, max(xmax * loss, cost) * 1.22)
    right.set_xlabel("Chance the saved point is wrong")
    right.set_ylabel("Expected cost (utility units)")
    right.set_title(f"Wrong-target loss {fmt(loss, 0)}, a look costs {fmt(cost, 0)}", fontsize=11.5)
    metrics = {
        "Expected loss of clicking now": fmt(now, 2),
        "Cost of one more look": fmt(cost, 2),
        "Net advantage of looking": fmt(gain, 2),
        "Break-even chance of a wrong target": fmt(p_star, 3),
        "Better option": decision,
    }
    interpretation = (
        f"Expected loss of clicking now = {fmt(p, 2)} x {fmt(loss, 0)} = {fmt(now, 2)}. Looking first costs {fmt(cost, 1)} "
        f"and removes that loss, so its net advantage is {fmt(now, 2)} - {fmt(cost, 1)} = {fmt(gain, 2)}. "
        f"Break-even chance = {fmt(cost, 1)} / {fmt(loss, 0)} = {fmt(p_star, 3)}. {verdict}"
    )
    steps = [
        f"Expected loss of clicking now: {fmt(p, 2)} x {fmt(loss, 0)} = {fmt(now, 2)}.",
        f"A perfect look costs {fmt(cost, 1)} and removes that loss.",
        f"Net advantage of looking: {fmt(now, 2)} - {fmt(cost, 1)} = {fmt(gain, 2)}.",
        f"Break-even chance: {fmt(cost, 1)} / {fmt(loss, 0)} = {fmt(p_star, 3)}; the chosen chance is {fmt(p, 2)}.",
        f"Better option: {decision.lower()}.",
    ]
    alt = (f"Left: bars for the expected loss of clicking now ({fmt(now, 2)}) and the cost of looking ({fmt(cost, 2)}). Right: the expected "
           f"loss rising with the chance of a wrong target against the flat cost of looking, crossing at {fmt(p_star, 3)}; the chosen chance is {fmt(p, 2)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 18,
    "title": "When an Action Has Coordinates",
    "subtitle": "A click names a position, not an object. What it does depends on the screen that is current when it arrives.",
    "summary": (
        "These four demonstrations follow the chapter's release console, where the rows can swap places after the controller "
        "has looked. They show how the interface enters the transition law for a coordinate, a semantic and a transactional command, "
        "which commands survive when the screen is uncertain, how age, version and permission combine with a steady rate of change, "
        "and when another look is worth its cost."
    ),
    "ask_skill": {
        "prompt": (
            "Compare coordinate, semantic and version-bound action for an observation of age 3 against a freshness limit of 2, "
            "saved layout-1 against current layout-2, current permission true, effect confirmed, coordinate target delete, semantic "
            "target release and wanted target release, with a change rate of 0.02 per second and delays of 5, 15 and 30. For each "
            "interface say whether it is issued and whether authorized confirmed completion holds, and give the freshness "
            "probability at each delay."
        )
    },
    "demos": [
        {
            "id": "C18-D01",
            "title": "One command, two layouts, three interfaces",
            "question": "If the controller is unsure which layout is current, what does each kind of command do, and what does a permission check change?",
            "equations": [EQ_TRANSITION],
            "symbols": (
                "x is the current state (here, which layout is on screen), a is the proposed command, and a-tilde "
                "is the operation the interface actually realizes: release v2, release v3 or a denial. Exec(a-tilde | x, a) is the "
                "chance the interface realizes a-tilde, and P(x' | x, a-tilde) is the world's law for the next state x'. "
                "Act with subscript ui is the set of operations the interface can realize, and Exec with subscript ui is the "
                "interface's own chance of realizing one. The belief is the controller's probability that layout 1 is current. "
                "A coordinate command is a position; a semantic command names a control bound to v2; a transactional command names v2 "
                "and the saved screen version, which the service checks at commit."
            ),
            "prediction": "With belief 0.6 in layout 1, no permission check and the coordinate command, what is the chance of a prohibited release?",
            "prediction_options": ["0.60", "0.40", "0.00"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "P(release v3) = 0.6 x 0 + 0.4 x 1 = 0.40, which is the chapter's exercise 1. With the check on it falls to 0 while intended completion stays 0.60.",
                "incorrect": "The saved point reaches v3 in layout 2, which has belief 0.4: P(release v3) = 0.6 x 0 + 0.4 x 1 = 0.40. Choose the coordinate command, belief 0.6 and the check off to see it.",
            },
            "misconception": {
                "title": "A better visual model fixes the wrong target",
                "text": (
                    "The chapter notes that the improvement from a permission check comes from enforcement: the controller has not become "
                    "better at locating the button. A better visual model might reduce misreading, but it cannot establish that a previously "
                    "observed interface has remained unchanged. Turn the check on: the belief is the same, the prohibited release disappears."
                ),
            },
            "explanation": (
                "In layout 1 the saved click realizes release v2 for certain; in layout 2 the coordinate realizes release v3 for certain, or a "
                "denial if the permission check is on. Equation (18.1) multiplies each realized operation by its world effect and "
                "adds, and the belief averages over the two layouts. Uncertainty sits in which layout is current, not in the click. "
                "The semantic request is bound to the object, so the swap does not move it, and the transactional request adds the saved "
                "version, so a changed layout produces a refusal instead of an effect on a new record."
            ),
            "application": (
                "Before trusting a command, write down what it realizes under every layout you consider possible, "
                "and which of those realizations a current check would block. Compare interfaces with the task, the document, the authority "
                "and the deadline held fixed."
            ),
            "assumptions": (
                "Two layouts, each with a deterministic realized operation that leads to one next state, and complete mediation when the check is on. "
                "The beliefs are probabilities in a constructed model, not measured accuracies of any visual model. The semantic request is taken "
                "to resolve v2 correctly; a mislabeled or ambiguous control would break that, and a transactional request can fail because its "
                "precondition expired even when a person would accept the newer version. If an unmediated route to the service exists, the check "
                "does not apply."
            ),
            "check": "With belief 0.7 in layout 1, what is the chance of a prohibited release for the coordinate command with no check, and with the check on?",
            "answer": "No check: 0.7 x 0 + 0.3 x 1 = 0.30. Check on: 0.7 x 0 + 0.3 x 0 = 0. Authorized completion stays 0.7 x 1 + 0.3 x 0 = 0.70 in both.",
            "provenance": "Constructed example: the chapter's two-layout console with its 0.8 and 0.2 beliefs and chapter exercise 1's 0.6 and 0.4; the three interfaces are the chapter's, with issuance and target correctness computed by the laboratory's interface calculation.",
            "source_section": "The interface belongs in the transition law",
            "source_anchor": "the-interface-belongs-in-the-transition-law",
            "controls": [
                {"key": "interface", "label": "Kind of command", "values": list(INTERFACES), "default": "coordinate",
                 "value_labels": list(INTERFACES.values())},
                {"key": "belief_layout1", "label": "Belief that layout 1 (v2 on top) is current", "values": [0.6, 0.8], "default": 0.8},
                {"key": "permission_check", "label": "Current permission check at the service", "values": ["off", "on"], "default": "off",
                 "value_labels": ["Off", "On"]},
            ],
            "function": "transition_picture",
        },
        {
            "id": "C18-D02",
            "title": "What survives when the screen is uncertain",
            "question": "Which commands stay authorized in every layout the controller still considers possible, which state removes the rest, and which observation restores them?",
            "equations": [EQ_ROBUST],
            "symbols": (
                "b(x) is the belief weight of state x, here layout 1 or layout 2. The set written A with subscript auth, at x, holds the "
                "commands whose protected effect is authorized in state x. The set written A with subscript rob, at b, is the "
                "intersection of those sets over every state with positive belief. A perfect read is an observation that shows which layout "
                "is current."
            ),
            "prediction": "Layout 2 has belief only 0.01 and nothing further is observed. Does the saved-point click survive the intersection?",
            "prediction_options": ["Yes, 0.01 is negligible", "No, any positive weight removes it"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Any positive weight on layout 2 puts it in the support, and layout 2 does not authorize the click, so 5 - 4 = 1 command is removed. The size of the weight never enters.",
                "incorrect": "The intersection counts every state with positive belief, however small: layout 2 counts at 0.01, does not authorize the click, and removes it (4 of 5 remain). Choose belief 0.01 with no further observation.",
            },
            "misconception": {
                "title": "A likely target is authority for it",
                "text": (
                    "The chapter says a high-probability intended target is not current authority for a different target. At belief 0.99 in "
                    "layout 1 the click is probably right, yet the 0.01 on layout 2 removes it, because the intersection asks what is "
                    "authorized throughout the support, not what is most likely."
                ),
            },
            "explanation": (
                "A command is kept only if every state with positive weight authorizes it. Layout 2 does not authorize the saved-point "
                "click, so any positive weight on layout 2 removes it, while zero weight leaves layout 2 out of the intersection entirely. "
                "The weight itself never enters the result, only whether it is positive. The last column names the state that removed each "
                "command, and a perfect read narrows the support: seeing layout 1 restores the click, seeing layout 2 confirms its removal."
            ),
            "application": (
                "When a decision is removed by a state you think unlikely, the record shows which state removed it and which "
                "observation (a fresh screenshot, a metadata read) could narrow the support and restore it. Reading can often be "
                "permitted over a broader set of states than releasing, which is why it stays available."
            ),
            "assumptions": (
                "The true layout must lie inside the counted support, and the authorization sets must be specified correctly; "
                "if either fails, the intersection guarantees nothing. The sets here are constructed, and the construction is "
                "conservative: it is not a substitute for the service's own current permission check. A read only helps if it is current and correct."
            ),
            "check": "If layout 2 has belief 0.001 and nothing further is observed, does the saved-point click survive? What if the belief is exactly 0?",
            "answer": "At 0.001 the weight is positive, so layout 2 counts and removes the click (5 - 4 = 1 removed, 4 of 5 remain). At 0 layout 2 is not counted, the click survives and 5 of 5 remain, but only if layout 1 is truly current.",
            "provenance": "Constructed example: the chapter's two-layout case, with authorization sets defined for this reader and belief weights chosen for illustration.",
            "source_section": "A belief over screens",
            "source_anchor": "a-belief-over-screens",
            "controls": [
                {"key": "belief_layout2", "label": "Belief that layout 2 (rows swapped) is current", "values": [0.0, 0.01, 0.5, 1.0], "default": 0.01},
                {"key": "observation", "label": "Further observation", "values": list(OBSERVATIONS), "default": "none",
                 "value_labels": list(OBSERVATIONS.values())},
            ],
            "function": "robust_set_picture",
        },
        {
            "id": "C18-D03",
            "title": "How long a picture stays useful",
            "question": "Given its age, its saved version and the current permission, which interface may act, and how fast does a coordinate go stale if changes arrive at a steady rate?",
            "equations": [EQ_FRESH],
            "symbols": (
                "Delta is the delay between observing and acting, in seconds. Lambda with subscript ui is the rate of invalidating "
                "interface changes, in changes per second. Their product is a pure number. Fresh(Delta) is the chance that no invalidating change "
                "occurred during the delay. Separately, the age rule compares the observation's age with a limit; the version-bound interface also "
                "compares the saved version with the current one; every interface needs current permission."
            ),
            "prediction": "At 0.02 changes per second, is the chance of still being fresh after 30 seconds above or below one half?",
            "prediction_options": ["Above one half", "Below one half"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "Fresh = exp(-0.02 x 30) = exp(-0.60) = 0.5488, just above one half (the half point is 0.6931 / 0.02 = 34.7 seconds).",
                "incorrect": "Fresh = exp(-0.02 x 30) = exp(-0.60) = 0.5488, which is above one half: the half point is 0.6931 / 0.02 = 34.7 seconds. Choose the default case and a delay of 30 to see it.",
            },
            "misconception": {
                "title": "A freshly taken screenshot is current",
                "text": (
                    "The chapter notes that a fresh observation has latency: if observation, interpretation and execution take several "
                    "seconds, a controller can keep acquiring a new image and still act on an old state. Age by itself does not decide "
                    "validity; a state version, a lock, a commit precondition or a service action that checks the object may be needed."
                ),
            },
            "explanation": (
                "If changes arrive at a constant rate, the chance of none in a delay falls as an exponential of rate times delay. "
                "Doubling the delay squares the freshness: at 0.02 per second, 15 seconds gives 0.7408 and 30 seconds gives 0.5488, "
                "which is 0.7408 squared. The table shows what the age rule, the version and the permission do on top of that: in the "
                "default case the age is within its limit but the layout changed, so only the version-bound request refuses; in the "
                "changed case the age passes its limit and all three refuse; in the transfer case permission is false and every interface "
                "refuses although the observation is fresh and the versions match."
            ),
            "application": (
                "Choose a maximum observation age by deciding what chance of an invalidating change you will accept, then "
                "refresh the observation or bind the command to a state version before that age is reached, and check current "
                "permission at issuance, not from memory."
            ),
            "assumptions": (
                "The table and the curve are independent: the table uses the case's observation age, the curve uses the chosen delay. In the "
                "default and changed cases the coordinate target is called delete, the notebook's name for the wrong object (v3 in Demonstration 1). "
                "Constant-rate, memoryless changes, and a clear definition of which changes invalidate the binding. Real interfaces "
                "can update periodically, in bursts, or in response to the agent's own actions, and a rate taken from quiet "
                "periods can mislead. The rates and limits here are teaching inputs. Semantic resolution can itself be wrong, and a "
                "click receipt is not an effect receipt."
            ),
            "check": "At 0.05 invalidating changes per second and a 20 second delay, what is Fresh?",
            "answer": "Rate x delay = 0.05 x 20 = 1.0, so Fresh = exp(-1) = 0.3679. The chance of an invalidating change is 1 - 0.3679 = 0.6321.",
            "provenance": "Constructed example: the notebook's default case (age 1 against a limit of 2, layout-1 against layout-2, rate 0.02), changed case (age 3) and transfer case (permission false, rate 0.05), computed with the laboratory's interface function, and the chapter's delays of 5 and 30 seconds with chapter exercise 2's 15; the delay of 10 seconds is defined for this reader.",
            "source_section": "How long a picture stays useful",
            "source_anchor": "how-long-a-picture-stays-useful",
            "controls": [
                {"key": "scenario", "label": "Case", "values": list(SCENARIOS), "default": "default",
                 "value_labels": ["Default: age 1 of limit 2, layout changed", "Changed: age 3 beyond the limit of 2",
                                  "Transfer: fresh and matching, permission denied"]},
                {"key": "delay", "label": "Delay before acting (seconds)", "values": CHAPTER_DELAYS, "default": 30},
            ],
            "function": "freshness_picture",
        },
        {
            "id": "C18-D04",
            "title": "The price of another look",
            "question": "When does one more observation before the click earn its cost?",
            "equations": [EQ_TRANSITION],
            "symbols": (
                "The chance the saved point is wrong is the probability of the layout in which the click reaches the wrong "
                "record. The loss is what that outcome costs, in declared utility units. A second observation costs 1 or 2 units and "
                "is assumed to settle which layout is current. Equation (18.1) describes the possible outcomes of the click "
                "(its symbols are defined in Demonstration 1: a-tilde is a realized operation, Exec with subscript ui its chance, "
                "Act with subscript ui the set of realizable operations, x' the next state). This demonstration's own comparison "
                "is: expected loss of clicking now = chance x loss, and looking pays when chance x loss is more than its cost."
            ),
            "prediction": "With a wrong-target loss of 3 (a denial) instead of 40, a look costing 2 and a 0.1 chance of being wrong, does the extra look still pay?",
            "prediction_options": ["Yes, it still pays", "No, clicking now is cheaper"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Clicking now costs 0.1 x 3 = 0.3, below the 2 units a look costs, so the net advantage is 0.3 - 2 = -1.7: the permission check bounded the effect.",
                "incorrect": "Clicking now costs 0.1 x 3 = 0.3, well below the cost 2 of looking, so the look does not pay (net advantage 0.3 - 2 = -1.7). Choose loss 3, chance 0.1 and a look costing 2.",
            },
            "misconception": {
                "title": "Buy information whenever you are uncertain",
                "text": (
                    "The chapter says a controller should not buy information merely because uncertainty exists, but when the information "
                    "can change an authorized decision enough to justify its cost. With complete permission mediation a wrong click only "
                    "costs a denial, and the same perfect look no longer pays."
                ),
            },
            "scope_note": {
                "text": (
                    "Physical agents extend the problem further: contact, inertia, uncertain actuators and irreversible material effects "
                    "can require additional state and control models, and this chapter establishes no transfer guarantee from desktop "
                    "completion to robotics. For the release controller, the useful result is narrower: the model may choose the right "
                    "intention, and the interface must still connect that intention to the right object, current permission and confirmed consequence."
                ),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "Clicking now costs the chance of a wrong target times its loss. Looking first costs its price and removes that loss. "
                "The look pays when chance x loss exceeds the price, which gives a break-even chance of the price divided by the loss. "
                "Enforcement matters because it changes the loss, not the chance; binding the command to v2 with a version check removes the "
                "chance for document identity altogether, leaving the look nothing to buy on that question."
            ),
            "application": (
                "Do not buy information because uncertainty exists. Price the wrong-target branch under the interface you "
                "actually have, and look again only when that expected loss is larger than the cost of looking."
            ),
            "assumptions": (
                "The look is perfect, execution follows at once, and the loss lumps delay, retries and side effects into one number. "
                "A denied attempt can also use up a rate limit, lock an account or reveal information; if so the loss of 3 "
                "is too small. A deadline can raise the cost of looking. The number 2 is not a general price for visual safety."
            ),
            "check": "If one more look cost 3 units, the wrong-target loss were 40 and the chance of a wrong target 0.1, would looking first pay?",
            "answer": "Clicking now costs 0.1 x 40 = 4.0. Looking costs 3, so the net advantage is 4.0 - 3 = 1.0 and it pays. The break-even chance is 3 / 40 = 0.075, below 0.1.",
            "provenance": "Constructed example: the chapter's 0.1 chance of a wrong target, loss of 40 or 3 and observation cost of 2, chapter exercise 3's look costing 1 with a 0.2 chance, and the chapter's third interface with chance 0.",
            "source_section": "The price of another look",
            "source_anchor": "the-price-of-another-look",
            "controls": [
                {"key": "wrong_loss", "label": "Loss if the click reaches the wrong record", "values": [40, 3], "default": 40,
                 "value_labels": ["40: unguarded harmful release", "3: denied attempt (permission check)"]},
                {"key": "wrong_chance", "label": "Chance the saved point is wrong", "values": [0.0, 0.1, 0.2], "default": 0.1,
                 "value_labels": ["0: command bound to v2 with a version check", "0.1", "0.2"]},
                {"key": "look_cost", "label": "Cost of one more look", "values": [1, 2], "default": 2},
            ],
            "function": "another_look_picture",
        },
    ],
}

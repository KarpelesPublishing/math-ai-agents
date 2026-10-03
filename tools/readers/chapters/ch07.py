"""Chapter 7 reader: The Equation That Looks Ahead.

Four demonstrations built on Equations (7.1) to (7.5).
Demonstrations 2, 3 and 4 call the laboratory's own backward induction
(math_ai_agents.chapters.ch07.evaluate) for the values, so the reader, the
notebook and the chapter skill agree. Every number is a constructed teaching
value.

D01 discounting (7.1), 4 discount factors x 3 distances.
D02 the three-state controller computed backward, stepped one state at a time
    (7.2, 7.3), with the chapter's book values, its break-even cost and the
    workbench problem II.1 (and II.3) as selectable scenarios.
D03 remaining decisions and discount (7.4): the notebook default and changed
    cases (cash, prepare, release) and the transfer case (now, later, collect).
D04 the residual bound (7.5), stepped through a guess, the value of releasing
    at once, and the improved values (one pass of policy iteration).
"""
import math

import numpy as np

from math_ai_agents.chapters.ch07 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed, undefined

EQ_RETURN = r"\operatorname{Ret}_t=\sum_{k=0}^{\infty}\gamma^{k}r_{t+k}"
EQ_VALUE = r"V^{\pi}(x)=\operatorname{E}_{\pi}\!\left[\operatorname{Ret}_t \mid x_t=x\right]"
EQ_BELLMAN = (r"\begin{aligned}V^{\pi}(x)&=\sum_{a}\pi(a\mid x)\sum_{x'}P(x'\mid x,a)\\"
              r"&\quad\cdot\Bigl[r(x,a,x')+\gamma V^{\pi}(x')\Bigr].\end{aligned}")
EQ_OPTIMAL = r"V^{\star}(x)=\max_{a}\sum_{x'}P(x'\mid x,a)\Bigl[r(x,a,x')+\gamma V^{\star}(x')\Bigr]"
EQ_RESIDUAL = r"\|V-V^\star\|_\infty\leq \frac{\|TV-V\|_\infty}{1-\gamma}"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


def small(x):
    """Show a value with enough decimals that small numbers do not collapse to zero."""
    x = float(x)
    if abs(x) >= 1:
        return fmt(x, 1)
    if abs(x) >= 0.01:
        return fmt(x, 2)
    if abs(x) >= 0.0001:
        return fmt(x, 4)
    return f"less than 0.0001 (about {sci(x)})"


def sci(x):
    """Plain-text power of ten, for example 8.9 x 10^-14."""
    mant, exp = f"{float(x):.1e}".split("e")
    return f"{mant} x 10^{int(exp)}"


def tiny(x):
    """Short form for a figure legend."""
    return "under 0.0001" if abs(float(x)) < 0.0001 else small(x)


def nice(x):
    """One decimal, or two when the second decimal matters (65.25, not 65.2)."""
    x = float(x)
    text = f"{x:.2f}"
    if text.endswith("0"):
        text = text[:-1]
    if text.startswith("-") and float(text) == 0:
        text = text[1:]
    return text


def nsigned(x):
    text = nice(x)
    return f"({text})" if text.startswith("-") else text


# Demonstration 1: what a discount factor does to a delayed reward (Equation 7.1)

DISCOUNTS = [0.5, 0.9, 0.95, 0.99]


def discount_picture(gamma=0.9, steps=10):
    gamma, steps = float(gamma), int(steps)
    k = np.arange(0, 101)
    scale = 1.0 / (1.0 - gamma)
    worth = 100.0 * gamma ** steps
    at_scale = 100.0 * gamma ** scale
    eq = sci(worth) if abs(worth) < 0.0001 else small(worth)
    # the chapter states the rule of a third for 0.9, 0.95 and 0.99 only
    fig, ax = new_figure(height=4.2)
    for g in DISCOUNTS:
        if g != gamma:
            ax.plot(k, 100.0 * g ** k, color=PALETTE["light"], linewidth=1.4)
    ax.plot(k, 100.0 * gamma ** k, color=PALETTE["teal"], linewidth=2.4)
    ax.plot([scale], [at_scale], "D", color=PALETTE["navy"], markersize=13, zorder=3, clip_on=False)
    ax.plot([steps], [worth], "o", color=PALETTE["terracotta"], markersize=8, markeredgecolor="white",
            markeredgewidth=1.5, zorder=4, clip_on=False)
    ax.axvline(steps, color=PALETTE["terracotta"], linestyle="dotted", linewidth=1.3)
    ax.text(0.98, 0.95, f"circle: worth {tiny(worth)} at {steps} steps", transform=ax.transAxes, ha="right", va="top",
            fontsize=11, color=PALETTE["terracotta"], bbox=BOX, zorder=6)
    ax.text(0.98, 0.87, f"diamond: scale 1/(1 - gamma) = {fmt(scale, 0)} steps", transform=ax.transAxes, ha="right", va="top",
            fontsize=11, color=PALETTE["navy"], bbox=BOX, zorder=6)
    others = ", ".join(fmt(g, 2) for g in DISCOUNTS if g != gamma)
    ax.text(0.98, 0.79, f"teal: chosen gamma {fmt(gamma, 2)}\ngrey, steepest first: {others}",
            transform=ax.transAxes, ha="right", va="top", fontsize=11, color=PALETTE["teal"], bbox=BOX, zorder=6)
    ax.set_xlim(0, 102)
    ax.set_ylim(-6, 112)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel("Steps until the reward arrives")
    ax.set_ylabel("Worth now of a reward of 100")
    ax.set_title(f"Discount factor {fmt(gamma, 2)}; reward of 100 arriving {steps} steps away", fontsize=11.5)
    metrics = {
        "Worth now": small(worth),
        "Share of its value kept": f"{fmt(worth, 2)} out of 100" if worth >= 0.01 else f"{small(worth)} out of 100",
        "Planning scale 1/(1 - gamma)": f"{fmt(scale, 0)} steps",
        "Worth at that scale": fmt(at_scale, 1),
        "Return of 1 every step, forever": fmt(scale, 1),
    }
    interpretation = (
        f"Only the reward at step {steps} is counted here, so Equation (7.1) reduces to one term: "
        f"100 x {fmt(gamma, 2)}^{steps} = {eq}. The scale 1/(1 - {fmt(gamma, 2)}) = 1 / {fmt(1 - gamma, 2)} = "
        f"{fmt(scale, 1)} steps is where a reward has fallen to {'roughly a third' if gamma >= 0.8 else 'a quarter, not a third'}: 100 x {fmt(gamma, 2)}^{fmt(scale, 0)} = "
        f"{fmt(at_scale, 1)}"
        + ("" if gamma >= 0.8 else " (the rule of a third is only approximate for small gamma)")
        + f". A steady reward of 1 per step adds up to 1 / (1 - {fmt(gamma, 2)}) = {fmt(scale, 1)}. "
        "The curve never reaches zero, so a large enough delayed reward can still outweigh an immediate cost."
    )
    worked = [
        f"A reward R = 100 arrives k = {steps} steps from now, so only the k = {steps} term of Equation (7.1) is nonzero.",
        f"Worth now = R x gamma^k = 100 x {fmt(gamma, 2)}^{steps} = {eq}.",
        f"Planning scale = 1 / (1 - gamma) = 1 / {fmt(1 - gamma, 2)} = {fmt(scale, 1)} steps.",
        f"At that scale the reward is worth 100 x {fmt(gamma, 2)}^{fmt(scale, 0)} = {fmt(at_scale, 1)}" + (", about a third of 100." if gamma >= 0.8 else f", a quarter of 100: the rule of a third is only approximate for small gamma."),
        f"A steady reward of 1 per step is worth 1 / (1 - {fmt(gamma, 2)}) = {fmt(scale, 1)} in total.",
    ]
    alt = (f"Five decay curves of a reward of 100 against steps away. The curve for discount factor {fmt(gamma, 2)} is highlighted; "
           f"at {steps} steps it is worth {eq}, and a diamond marks the planning scale of {fmt(scale, 0)} steps.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstrations 2 and 4 share the book's controller. Expected rewards, as in the chapter.

def controller_states(verify_cost, verified_value, release_now):
    """Three-state controller in the laboratory's input format (expected rewards)."""
    return {
        "unverified": {"actions": [
            {"name": "release", "reward": float(release_now), "probabilities": [1.0], "next_states": ["done"]},
            {"name": "verify", "reward": -float(verify_cost), "probabilities": [1.0], "next_states": ["verified"]},
        ]},
        "verified": {"actions": [
            {"name": "release", "reward": float(verified_value), "probabilities": [1.0], "next_states": ["done"]},
        ]},
        "done": {"actions": [
            {"name": "stop", "reward": 0.0, "probabilities": [1.0], "next_states": ["done"]},
        ]},
    }


def lab_values(states, gamma, horizon=3, start="unverified"):
    out = evaluate({"horizon": horizon, "discount": gamma, "start": start, "states": states})
    m = out["metrics"]
    return m["values_by_remaining_steps"][horizon], m["policy_by_remaining_steps"][horizon - 1]


# Demonstration 2: three states, computed backward, one state at a time (Equations 7.2 and 7.3)

SCENARIOS = {
    # key: (release now, verified value, verification cost, discount, label)
    "book": (85.0, 97.0, 5.0, 1.0, "The chapter's controller"),
    "tie": (85.0, 97.0, 12.0, 1.0, "The chapter's controller at the break-even cost"),
    "wb1": (80.0, 95.0, 6.0, 0.9, "Workbench II.1 (discount 0.90)"),
    "wb3": (80.0, 95.0, 6.0, 0.75, "Workbench II.3 (discount 0.75)"),
}
STAGE_LABELS = ["Terminal state", "Verified state", "Start state"]


def backward_picture(scenario="book", stage=2):
    r_now, v_ver, c, g, name = SCENARIOS[scenario]
    stage = int(stage)
    states = controller_states(c, v_ver, r_now)
    values, _ = lab_values(states, g)
    v_verified = v_ver + g * 0.0                  # release, then the terminal value 0
    v_release = r_now + g * 0.0                   # policy: release at once
    v_verify = -c + g * v_verified                # policy: verify, then release
    if not (math.isclose(values["unverified"], max(v_release, v_verify), abs_tol=1e-9)
            and math.isclose(values["verified"], v_verified, abs_tol=1e-9)
            and math.isclose(values["done"], 0.0, abs_tol=1e-9)):
        raise AssertionError("laboratory backward induction disagrees with the hand values")
    tie = math.isclose(v_release, v_verify, abs_tol=1e-9)
    verify_wins = v_verify > v_release and not tie
    gain = v_verify - v_release
    break_even_cost = g * v_verified - v_release
    tie_discount = (c + r_now) / v_verified
    rows = [
        ("Terminal state", 0.0, 0.0, 0),
        ("Verified: release", v_verified, 0.0, 1),
        ("Start, policy: release at once", v_release, 0.0, 2),
        ("Start, policy: verify then release", -c, g * v_verified, 2),
    ]
    fig, ax = new_figure(height=4.0)
    ys = np.arange(len(rows))[::-1]
    for y, (label, immediate, cont, needed) in zip(ys, rows):
        if stage < needed:
            ax.text(2, y, "not computed yet", va="center", fontsize=10.5,
                    color=PALETTE["grey"], style="italic")
            continue
        ax.barh(y, immediate, left=0, height=0.52, color=PALETTE["navy"] if immediate >= 0 else PALETTE["terracotta"])
        start = immediate if immediate >= 0 else 0.0
        if cont:
            ax.barh(y, cont, left=start, height=0.52, color="white", edgecolor=PALETTE["teal"], hatch="///", linewidth=1.2)
        total = immediate + cont
        ax.plot([total], [y], "D", color=PALETTE["gold"], markersize=9, markeredgecolor=PALETTE["ink"])
        top = stage == 2 and label.startswith("Start") and (
            (label.endswith("then release") and (verify_wins or tie)) or (label.endswith("at once") and (not verify_wins or tie)))
        tag = (" (tied)" if tie else " (highest)") if top else ""
        ax.text(max(start + cont, total, 0) + 8, y, nice(total) + tag, va="center", fontsize=11, color=PALETTE["ink"])
    ax.text(0.98, 0.99, "solid: reward now\nhatched: discounted future\ndiamond: total value", transform=ax.transAxes,
            ha="right", va="top", fontsize=10.5, color=PALETTE["ink"])
    ax.set_ylim(-0.6, 4.5)
    ax.axvline(0, color=PALETTE["ink"], linewidth=1.0)
    ax.set_yticks(ys, [r[0] for r in rows])
    ax.set_xlim(-30, 175)
    ax.set_xlabel("Utility (constructed units)")
    ax.set_ylabel("State and policy")
    ax.set_title(f"Step {stage + 1} of 3: {STAGE_LABELS[stage].lower()}; verifying costs {fmt(c, 0)}", fontsize=11.5)
    ax.grid(axis="y", alpha=0)

    g2 = fmt(g, 2)
    if tie:
        chosen = "tie"
        verdict = (f"The two start values tie at {nice(v_release)}. Equation (7.3) prices each policy faithfully but "
                   "the comparison of Equation (7.4) cannot choose between them; a person or a stated tie-break must.")
    elif verify_wins:
        chosen = "verify"
        verdict = (f"Verify then release is worth {nice(gain)} more, so the controller verifies even though "
                   f"verifying scores {nsigned(-c)} on a one-step ledger against {nice(v_release)} for releasing.")
    else:
        chosen = "release"
        if g * v_verified - r_now < -1e-9:
            verdict = (f"Releasing at once is worth {nice(-gain)} more, so the controller releases. Even a free verification would lose "
                       f"at this discount, because {g2} x {nice(v_verified)} = {nice(g * v_verified)} is below the release value "
                       f"{nice(r_now)}: the discount, not the cost, does the damage.")
        else:
            verdict = (f"Releasing at once is worth {nice(-gain)} more, so the controller releases: "
                       "this verification costs more than the later support it buys.")
    if tie_discount > 1.0 + 1e-9:
        tie_text = f"{fmt(tie_discount, 3)} (above 1: release wins at every discount)"
    else:
        tie_text = fmt(tie_discount, 4)
    done = stage == 2
    metrics = {
        "Value of the terminal state": "0.0",
        "Value of the verified state": nice(v_verified) if stage >= 1 else "not computed yet",
        "Start value, release at once": nice(v_release) if done else "not computed yet",
        "Start value, verify then release": nice(v_verify) if done else "not computed yet",
        "Gain from verifying": nsigned(gain) if done else "not computed yet",
        "Chosen at the start": chosen if done else "not computed yet",
    }
    if stage == 0:
        interpretation = (
            f"Begin where nothing more can be collected. The stop action pays 0 and leads back to the terminal state, so its value is "
            f"0 + {g2} x 0 = 0.0. The release reward is paid on the transition into this state, so counting it again here would count it twice. "
            "No other value can be written until a successor value exists, which is why the order runs backward."
        )
        worked = [
            "The terminal state has one action, stop, with reward 0 and the terminal state as its successor.",
            f"Its value is 0 + {g2} x 0 = 0.0.",
            "The release payoff arrives on the transition into this state, so it is not counted a second time here.",
            "Step to the next state: the verified state needs only this number.",
        ]
        alt = "Bar chart with one row filled: the terminal state with value 0. The other three rows say they are not computed yet."
    elif stage == 1:
        interpretation = (
            f"The verified state has one action, release. Its value is the release payoff plus the discounted terminal value: "
            f"{nice(v_verified)} + {g2} x 0 = {nice(v_verified)}. This number is the continuation that verification will inherit. "
            "Nothing at the start state can be compared until this value exists."
        )
        worked = [
            f"The verified state has one action, release, paying {nice(v_verified)} on the way to the terminal state.",
            f"Value = {nice(v_verified)} + {g2} x 0 = {nice(v_verified)}.",
            "This value is what verification will carry back to the start state.",
            "Step to the start state to compare the two start policies.",
        ]
        alt = (f"Bar chart with two rows filled: the terminal state at 0 and the verified state at {nice(v_verified)}. "
               "The two start rows say they are not computed yet.")
    else:
        interpretation = (
            f"Release at once = {nice(v_release)} + {g2} x 0 = {nice(v_release)}. Verify then release = {nsigned(-c)} + "
            f"{g2} x {nice(v_verified)} = {nice(v_verify)}. Gain from verifying = {nice(v_verify)} - {nice(v_release)} = "
            f"{nsigned(gain)}. {verdict} The break-even cost is {g2} x {nice(v_verified)} - {nice(v_release)} = "
            f"{nice(break_even_cost)}{' (negative: no cost can rescue verification at this discount)' if break_even_cost < -1e-9 else ''}, and the break-even discount is ({fmt(c, 0)} + {fmt(r_now, 0)}) / {fmt(v_verified, 0)} = {tie_text}. "
            "The same start state has two values, one per policy; Equation (7.2) is always value under a policy."
        )
        worked = [
            f"Release at once: {nice(v_release)} + {g2} x 0 = {nice(v_release)}.",
            f"Verify then release: {nsigned(-c)} + {g2} x {nice(v_verified)} = {nice(v_verify)}.",
            f"Gain from verifying = {nice(v_verify)} - {nice(v_release)} = {nsigned(gain)}.",
            f"Equation (7.4) keeps the larger: {chosen}.",
            f"Break-even cost = {g2} x {nice(v_verified)} - {nice(v_release)} = {nice(break_even_cost)}.",
            f"Break-even discount = ({fmt(c, 0)} + {fmt(r_now, 0)}) / {fmt(v_verified, 0)} = {tie_text}.",
        ]
        alt = (f"Bar chart with four rows. The verified state is worth {nice(v_verified)}. The start state is worth "
               f"{nice(v_release)} under release at once and {nice(v_verify)} under verify then release; the controller chooses {chosen}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 3: the remaining horizon decides which action wins (Equation 7.4)

MODELS = {
    # key: (stop payoff, invest reward, later payoff, names, break-even, label)
    "prep": (2.0, -1.0, 6.0, ("cash", "prepare"), "draft", "Cash or prepare (notebook default and changed cases)"),
    "wait": (1.0, 0.0, 4.0, ("now", "later"), "wait", "Now or later (notebook transfer case)"),
}


def horizon_states_for(model):
    a, c, big, names, start, _ = MODELS[model]
    one = [1.0]
    imm, inv = names
    ready = "ready" if model == "prep" else "paid"
    end = "done" if model == "prep" else "end"
    collect = "release" if model == "prep" else "collect"
    return start, {
        start: {"actions": [
            {"name": imm, "reward": a, "probabilities": one, "next_states": [end]},
            {"name": inv, "reward": c, "probabilities": one, "next_states": [ready]},
        ]},
        ready: {"actions": [{"name": collect, "reward": big, "probabilities": one, "next_states": [end]}]},
        end: {"actions": [{"name": "stop", "reward": 0.0, "probabilities": one, "next_states": [end]}]},
    }


def q_values(model, h, gamma):
    """Action values at the start with h decisions left (the bracket of Equation 7.4, written out)."""
    a, c, big, _, _, _ = MODELS[model]
    later = big if h - 1 >= 1 else 0.0   # value of the ready state with h - 1 decisions left
    return {"imm": a + gamma * 0.0, "inv": c + gamma * later}


def horizon_picture(model="prep", horizon=2, discount=1.0):
    h, g = int(horizon), float(discount)
    a, c, big, names, start, label = MODELS[model]
    imm, inv = names
    _, states = horizon_states_for(model)
    q = q_values(model, h, g)
    best = max(q.values())
    tie = math.isclose(q["imm"], q["inv"], abs_tol=1e-9)
    chosen = "tie" if tie else (imm if q["imm"] > q["inv"] else inv)
    for n in (1, 2, 3):
        out = evaluate({"horizon": n, "discount": g, "start": start, "states": states})
        qn = q_values(model, n, g)
        if not math.isclose(out["metrics"]["start_value"], max(qn.values()), abs_tol=1e-9):
            raise AssertionError("laboratory backward induction disagrees with the hand values")
        lab_choice = out["metrics"]["policy_by_remaining_steps"][n - 1][start]
        if not math.isclose(qn["imm"], qn["inv"], abs_tol=1e-9) and lab_choice != (imm if qn["imm"] > qn["inv"] else inv):
            raise AssertionError("laboratory policy disagrees with the hand values")

    top = max(a, c + big) + 1.6
    bottom = min(a, c, 0.0) - 1.4
    fig, (left, right) = new_figure(ncols=2, height=4.2)
    hs = np.array([1, 2, 3])
    imm_line = np.array([q_values(model, n, g)["imm"] for n in hs])
    inv_line = np.array([q_values(model, n, g)["inv"] for n in hs])
    left.plot(hs, imm_line, "s-", color=PALETTE["terracotta"], markersize=7)
    left.plot(hs, inv_line, "o-", color=PALETTE["teal"], markersize=7)
    left.axvline(h, color=PALETTE["grey"], linestyle="dashed", linewidth=1.3)
    if inv_line[-1] > imm_line[-1] + 1e-9:
        label_point(left, 3, imm_line[-1], imm, color=PALETTE["terracotta"], dx=-6, dy=-10, ha="right", va="top").set_bbox(BOX)
        label_point(left, 3, inv_line[-1], inv, color=PALETTE["teal"], dx=-6, dy=8, ha="right").set_bbox(BOX)
    else:
        label_point(left, 3, imm_line[-1], imm, color=PALETTE["terracotta"], dx=-6, dy=8, ha="right").set_bbox(BOX)
        label_point(left, 3, inv_line[-1], inv, color=PALETTE["teal"], dx=-6, dy=-10, ha="right", va="top").set_bbox(BOX)
    label_point(left, h, top - 0.3, "selected", color=PALETTE["grey"], dx=5 if h < 3 else -5, dy=0,
                ha="left" if h < 3 else "right", va="top").set_bbox(BOX)
    left.set_xticks([1, 2, 3])
    left.set_xlim(0.7, 3.3)
    left.set_ylim(bottom, top)
    left.set_xlabel("Decisions remaining")
    left.set_ylabel("Action value at the start")
    left.set_title(f"Discount {fmt(g, 2)}: value of each action", fontsize=11.5)

    grid = np.linspace(0, 1, 101)
    imm_g = np.full_like(grid, a)
    inv_g = c + grid * (big if h >= 2 else 0.0)
    right.plot(grid, imm_g, color=PALETTE["terracotta"], linewidth=2)
    right.plot(grid, inv_g, color=PALETTE["teal"], linewidth=2)
    right.plot([g], [q["imm"]], "s", color=PALETTE["terracotta"], markersize=8)
    right.plot([g], [q["inv"]], "o", color=PALETTE["teal"], markersize=8)
    right.axvline(g, color=PALETTE["grey"], linestyle="dashed", linewidth=1.3)
    label_point(right, 0.0, a, imm, color=PALETTE["terracotta"], dx=4, dy=8, ha="left").set_bbox(BOX)
    be = (a - c) / big
    if h >= 2:
        label_point(right, 1.0, c + big, inv, color=PALETTE["teal"], dx=-6, dy=8, ha="right", va="bottom").set_bbox(BOX)
        right.plot([be], [a], "*", color=PALETTE["ink"], markersize=12)
        label_point(right, be, a, f"break-even {fmt(be, 2)}", color=PALETTE["ink"], dx=8, dy=-14, ha="left", va="top").set_bbox(BOX)
    else:
        label_point(right, 1.0, c, inv, color=PALETTE["teal"], dx=-6, dy=8, ha="right").set_bbox(BOX)
        right.text(0.5, (a + top) / 2 + 0.3, "no break-even: investing\npays nothing with one decision left",
                   color=PALETTE["ink"], ha="center", va="center", fontsize=10.5).set_bbox(BOX)
    right.set_xlim(0, 1.02)
    right.set_ylim(bottom, top)
    right.set_xlabel("Discount factor")
    right.set_ylabel("Action value at the start")
    right.set_title(f"With {h} decision{'s' if h > 1 else ''} left: value against discount", fontsize=11.5)

    breakeven = fmt(be, 2) if h >= 2 else undefined("investing has no payoff to discount")
    metrics = {
        "Value of the immediate action": fmt(q["imm"], 2),
        "Value of the investing action": signed(q["inv"], 2) if q["inv"] < 0 else fmt(q["inv"], 2),
        "Start value (the larger)": fmt(best, 2),
        "Chosen": chosen,
        "Break-even discount": breakeven,
    }
    ready_value = big if h >= 2 else 0.0
    g2 = fmt(g, 2)
    calc = (f"{imm.capitalize()} = {fmt(a, 0)} + {g2} x 0 = {fmt(q['imm'], 2)}. {inv.capitalize()} = {signed(c, 0)} + {g2} x "
            f"{fmt(ready_value, 0)} = {signed(q['inv'], 2)}, because the next state is worth {fmt(ready_value, 0)} with "
            f"{h - 1} decision{'s' if h - 1 != 1 else ''} left.")
    if tie:
        verdict = (f" The two actions tie exactly, so Equation (7.4) returns both as maximizers; the discount sits "
                   f"on the break-even value ({signed(c, 0)} + {fmt(big, 0)} x gamma = {fmt(a, 0)} gives gamma = {fmt(be, 2)}).")
    elif chosen == inv:
        verdict = f" {inv.capitalize()} wins by {fmt(q['inv'] - q['imm'], 2)}: the cost now is repaid by the payoff it enables."
    elif h < 2:
        verdict = (f" {imm.capitalize()} wins because one decision leaves no time to collect the later payoff; a controller that "
                   "ignores its deadline would invest and run out of steps. Stopping is the best action on the last call.")
    else:
        verdict = f" {imm.capitalize()} wins by {fmt(q['imm'] - q['inv'], 2)}: the discount shrinks the later payoff below the immediate one."
    extra = " A third decision adds nothing, because the terminal state pays zero." if h == 3 else ""
    interpretation = calc + verdict + extra
    worked = [
        f"With {h} decision{'s' if h > 1 else ''} left, the next state is worth {fmt(ready_value, 0)} "
        f"({'one more decision collects ' + fmt(big, 0) if h >= 2 else 'no decision is left to collect it'}).",
        f"Action value of {imm} = {fmt(a, 0)} + {g2} x 0 = {fmt(q['imm'], 2)}.",
        f"Action value of {inv} = {signed(c, 0)} + {g2} x {fmt(ready_value, 0)} = {signed(q['inv'], 2)}.",
        f"Equation (7.4) keeps the larger: start value = {fmt(best, 2)}, chosen: {chosen}.",
        (f"Break-even discount = ({fmt(a, 0)} - {signed(c, 0)}) / {fmt(big, 0)} = {fmt(be, 2)}." if h >= 2
         else "With one decision left, investing has no payoff to discount, so no break-even exists."),
    ]
    alt = (f"Two panels for the {imm} or {inv} model. Left: value of each action with 1, 2 and 3 decisions left at discount "
           f"{g2}. Right: value against discount factor with {h} decision{'s' if h > 1 else ''} left. The chosen action is {chosen}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": worked}


# Demonstration 4: a residual bounds the error of a candidate value function (Equation 7.5)

CAND_LABELS = ["Guess: all zeros", "Value of releasing at once", "After the improvement step"]
STATE_NAMES = {"unverified": "start", "verified": "verified", "done": "terminal"}
BOOK = (85.0, 97.0, 5.0)  # release now, verified release, verification cost: the chapter's controller


def lookahead(v, gamma):
    """T applied to V, computed by the laboratory: one backward step from terminal values V."""
    states = controller_states(BOOK[2], BOOK[1], BOOK[0])
    for s in states:
        states[s]["terminal"] = float(v[s])
    out = evaluate({"horizon": 1, "discount": gamma, "start": "unverified", "states": states})
    return out["metrics"]["values_by_remaining_steps"][1]


def residual_picture(discount=0.95, stage=0):
    g, stage = float(discount), int(stage)
    keys = ["unverified", "verified", "done"]
    seq = [{"unverified": 0.0, "verified": 0.0, "done": 0.0}]
    for _ in range(2):
        seq.append(lookahead(seq[-1], g))
    v = seq[stage]
    tv = lookahead(v, g)
    v_star, _ = lab_values(controller_states(BOOK[2], BOOK[1], BOOK[0]), g)
    if not all(math.isclose(seq[2][s], v_star[s], abs_tol=1e-9) for s in keys):
        raise AssertionError("two lookahead steps should reach the best values in this model")
    residual = max(abs(tv[s] - v[s]) for s in keys)
    error = max(abs(v[s] - v_star[s]) for s in keys)
    defined = 1.0 - g > 1e-12
    bound = residual / (1.0 - g) if defined else None
    if defined and error > bound + 1e-9:
        raise AssertionError("Equation (7.5) violated")

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    x = np.arange(len(keys))
    w = 0.26
    left.bar(x - w, [v[s] for s in keys], w, color=PALETTE["light"], edgecolor=PALETTE["ink"], hatch="..")
    left.bar(x, [tv[s] for s in keys], w, color=PALETTE["gold"], edgecolor=PALETTE["ink"], hatch="//")
    left.bar(x + w, [v_star[s] for s in keys], w, color=PALETTE["teal"], edgecolor=PALETTE["ink"])
    left.set_xticks(x, [STATE_NAMES[s] for s in keys])
    left.set_ylim(0, 128)
    left.set_xlim(-0.6, 2.6)
    left.set_xlabel("State")
    left.set_ylabel("Value")
    left.set_title(f"{CAND_LABELS[stage]}: V, its lookahead TV, and V*", fontsize=11)
    for xi, text, color in ((-w, "V", PALETTE["ink"]), (0, "TV", PALETTE["gold"]), (w, "V*", PALETTE["teal"])):
        label_point(left, 0 + xi, 106.0, text, color=color, dx=0, dy=0, ha="center", va="bottom")

    names = ["Actual error\nlargest gap, V to V*", "Residual\nlargest gap, TV to V", "Bound\nresidual / (1 - gamma)"]
    vals = [error, residual, bound]
    colors = [PALETTE["teal"], PALETTE["gold"], PALETTE["navy"]]
    hatches = ["", "//", "xx"]
    ypos = [2, 1, 0]
    for y, val, color, hatch in zip(ypos, vals, colors, hatches):
        if val is None:
            right.text(1.0, y, "undefined (1 - gamma = 0)", va="center", fontsize=11, color=PALETTE["ink"])
        else:
            right.barh(y, val, height=0.5, color=color, edgecolor=PALETTE["ink"], hatch=hatch)
            right.text(max(val, 0) * 1.25 + 0.4, y, fmt(val, 2 if val < 10 else 1), va="center", fontsize=11, color=PALETTE["ink"])
    right.set_xscale("symlog", linthresh=1)
    right.set_xlim(0, 100000)
    right.set_yticks(ypos, names)
    right.set_ylim(-0.6, 2.6)
    right.set_xlabel("Size in utility units (compressed scale)")
    right.set_ylabel("Quantity")
    right.set_title(f"Discount {fmt(g, 2)}: error never exceeds the bound" if defined
                    else f"Discount {fmt(g, 2)}: no bound exists", fontsize=11.5)
    right.grid(axis="y", alpha=0)

    g2 = fmt(g, 2)
    stay = -BOOK[2] + g * v["verified"]
    sums = (f"At the start, TV = max(85 + {g2} x {fmt(v['done'], 0)}, (-5) + {g2} x {fmt(v['verified'], 0)}) = "
            f"max(85.0, {signed(stay, 2)}) = {fmt(tv['unverified'], 2)}, against V = {fmt(v['unverified'], 2)}. "
            f"The verified state gives TV = 97 + {g2} x {fmt(v['done'], 0)} = {fmt(tv['verified'], 1)} against V = "
            f"{fmt(v['verified'], 0)}. The residual is the largest gap, {fmt(residual, 2)}.")
    if defined:
        if math.isclose(residual, 0.0, abs_tol=1e-9):
            tail = (f" Bound = {fmt(residual, 2)} / (1 - {g2}) = {fmt(residual, 2)} / {fmt(1 - g, 2)} = 0.00, so V is exactly "
                    "V*: the bound certifies a zero error without knowing V*.")
            if stage == 2 and math.isclose(seq[1]["unverified"], seq[2]["unverified"], abs_tol=1e-9):
                tail += (f" The improvement step changed nothing here: verifying scores {signed(stay, 2)} against 85.0, so "
                         "releasing at once was already the best policy.")
        else:
            tail = (f" Bound = {fmt(residual, 2)} / (1 - {g2}) = {fmt(residual, 2)} / {fmt(1 - g, 2)} = {fmt(bound, 1)}. "
                    f"The true error is {fmt(error, 2)}, which is inside the bound, though the bound can be loose"
                    + (f" (here {fmt(bound / error, 1)} times the error)" if error > 1e-9 else "") + ". "
                    "It bounds error for this declared model only.")
    else:
        tail = (" With a discount of 1 the divisor 1 - 1 = 0, so Equation (7.5) gives no bound and the bound is undefined. "
                f"The actual error here is {fmt(error, 2)}; this finite-horizon model (its terminal state loops with reward 0) "
                "still has exact values, but the residual cannot certify them.")
    metrics = {
        "Residual ||TV - V||": fmt(residual, 2),
        "Actual error ||V - V*||": fmt(error, 2),
        "Bound from Equation (7.5)": fmt(bound, 1) if defined else undefined("1 - gamma = 0, so Equation (7.5) gives no bound"),
        "Best start action under V*": "verify" if -BOOK[2] + g * v_star["verified"] > BOOK[0] + 1e-9
        else ("tie" if math.isclose(-BOOK[2] + g * v_star["verified"], BOOK[0], abs_tol=1e-9) else "release"),
    }
    worked = [
        f"Candidate V ({CAND_LABELS[stage].lower()}): start {fmt(v['unverified'], 2)}, verified {fmt(v['verified'], 1)}, terminal {fmt(v['done'], 1)}.",
        f"Lookahead at the start: max(85 + {g2} x {fmt(v['done'], 0)}, (-5) + {g2} x {fmt(v['verified'], 0)}) = {fmt(tv['unverified'], 2)}.",
        f"Lookahead at the verified state: 97 + {g2} x {fmt(v['done'], 0)} = {fmt(tv['verified'], 1)}.",
        f"Residual = largest gap between TV and V = {fmt(residual, 2)}.",
        (f"Bound = {fmt(residual, 2)} / (1 - {g2}) = {fmt(bound, 1)}." if defined
         else "Bound: 1 - gamma = 0, so Equation (7.5) gives no bound."),
        f"Actual error (needs V*) = {fmt(error, 2)}; it never exceeds the bound." if defined
        else f"Actual error (needs V*) = {fmt(error, 2)}, but the residual cannot certify it.",
    ]
    alt = (f"Left: grouped bars of the candidate V, its lookahead TV and V* for the start, verified and terminal states. "
           f"Right: bars for the actual error {fmt(error, 1)}, the residual {fmt(residual, 1)} and the bound "
           + (fmt(bound, 1) if defined else "(undefined)") + ".")
    return fig, metrics, f"Candidate: {CAND_LABELS[stage].lower()}. " + sums + tail, {"alt": alt, "steps": worked}


CHAPTER = {
    "number": 7,
    "title": "The Equation That Looks Ahead",
    "subtitle": "A choice made now must carry the value of what it makes possible later, and one recursion computes that value without anyone folding it in by hand.",
    "summary": (
        "These four demonstrations follow the chapter's document controller. It can release a report now or spend a step "
        "verifying first. Each demonstration changes one declared input (a discount, a cost, the time left, a candidate "
        "answer) and shows how the value of the future enters the present comparison. Two of them step through a "
        "calculation one state or one improvement at a time, and the chapter's workbench and transfer cases are selectable."
    ),
    "ask_skill": {"prompt": (
        "Using the draft, ready and done states (cash 2, prepare -1, release 6), compute the draft value at two decisions "
        "remaining by backward induction, then tell me at which discount factor cash and prepare tie.")},
    "demos": [
        {
            "id": "C07-D01",
            "title": "What a discount does to a distant reward",
            "question": "How much is a reward of 100 worth now if it arrives many steps from now, and what sets the planning scale?",
            "equations": [EQ_RETURN],
            "symbols": (
                "Ret_t is the return from time t: the sum of all future rewards, each multiplied by the discount factor gamma "
                "raised to how many steps away it is. r_(t+k) is the reward received k steps after t. gamma is a number between "
                "0 and 1 that the designer declares. Here a single reward of 100 arrives after the chosen number of steps, so "
                "only one term of the sum is nonzero."
            ),
            "prediction": "With gamma = 0.9, will a reward of 100 that is 50 steps away be worth more or less than 1 today?",
            "prediction_options": ["More than 1", "Less than 1, but still above 0", "Exactly 0"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "100 x 0.9^50 = 0.52: small, but every finite delay keeps a positive weight.",
                "incorrect": "Set gamma to 0.90 and steps to 50: the worth is 0.52, below 1 but above 0, because a finite delay never reaches zero.",
            },
            "explanation": (
                "Each step of delay multiplies the reward by gamma, so the worth falls geometrically without ever reaching zero. "
                "A steady reward of 1 per step adds up to 1/(1 - gamma), and that same number sets the scale on which delayed "
                "rewards fade to roughly a third. The factor is a declared valuation, not a measurement of how long a run lasts."
            ),
            "application": (
                "Before choosing a discount factor, compute what it does to the delayed benefit you care about. A factor that "
                "makes a useful verification or retrieval worth almost nothing will make the controller skip it."
            ),
            "assumptions": (
                "One delayed reward of fixed size, a constant discount factor, and rewards that arrive on a regular step count. "
                "The factors 0.9, 0.95 and 0.99 come from the chapter's text and 0.5 from its discussion of a short horizon. "
                "Reading gamma as a survival probability needs a separate assumption of independent continuation; time preference does not."
            ),
            "check": "With gamma = 0.95, about how many steps does it take for a reward to fall to roughly a third of its value, and what is a reward of 100 worth at 20 steps?",
            "answer": "The scale is 1 / (1 - 0.95) = 1 / 0.05 = 20 steps, and 100 x 0.95^20 = 35.8, roughly a third.",
            "provenance": "Constructed example: the chapter's discount arithmetic for a reward of 100 (factors 0.9, 0.95 and 0.99 at ten, fifty and a hundred steps), with gamma 0.5 from the chapter's horizon discussion.",
            "source_section": "What discounting does to a number",
            "source_anchor": "what-discounting-does-to-a-number",
            "misconception": {
                "title": "A discount factor is a cutoff",
                "text": ("The chapter says the discount factor sets an effective planning scale, not a finite horizon. Every finite delay keeps "
                         "a positive weight (100 x 0.9^50 = 0.52 is small but above zero), so a large enough delayed reward can still outweigh an immediate cost."),
            },
            "scope_note": {
                "text": "Discounting is a modeling choice rather than a fact, and a finite horizon is often a better choice than a discount.",
                "source_section": "What this does not settle",
            },
            "controls": [
                {"key": "gamma", "label": "Discount factor gamma", "values": [0.5, 0.9, 0.95, 0.99], "default": 0.9},
                {"key": "steps", "label": "Steps until the reward arrives", "values": [10, 50, 100], "default": 10},
            ],
            "function": "discount_picture",
        },
        {
            "id": "C07-D02",
            "title": "Three states, computed backward",
            "question": "Verifying costs something now. Can it still be the better first move, and at what cost does it stop being so?",
            "equations": [EQ_VALUE, EQ_BELLMAN],
            "symbols": (
                "V^pi(x) is the value of state x when the agent follows policy pi: the expected return from x onward. pi(a | x) is the "
                "chance the policy takes action a in x, P(x' | x, a) the chance of landing in state x', r(x, a, x') the reward on that "
                "move, and gamma the discount factor. The states are start, verified and terminal. Releasing pays its expected payoff "
                "(85 at the start and 97 once verified in the chapter's controller). Release now, verified release, verification cost and "
                "gamma are shown with each scenario."
            ),
            "prediction": "With the chapter's controller (verification costs 5), which start policy is worth more once you reach the start state?",
            "prediction_options": ["Release at once", "Verify, then release", "They tie"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Verify then release scores (-5) + 97 = 92, which beats 85 by 7.",
                "incorrect": "Choose the chapter's controller and step to the start state: verify then release scores (-5) + 97 = 92, above 85.",
            },
            "explanation": (
                "Start at the terminal state, whose remaining value is 0. The verified state has one action, so its value is its "
                "release payoff plus 0. At the start, releasing at once is worth its payoff plus 0, while verifying is worth minus its "
                "cost plus the discounted value of the verified state. The comparison that a one-step ledger misses sits in the second term. "
                "The same start state carries two values, one for each policy, which is what the superscript in Equation (7.2) records."
            ),
            "application": (
                "When a check, a retrieval or a clarifying question looks like pure cost, write the value of the state it leads "
                "to and compare. The break-even cost and the break-even discount tell you how expensive the check can be, and how "
                "heavily the future may be discounted, before skipping it is right."
            ),
            "assumptions": (
                "Three states, one verification opportunity, deterministic movement into the verified state, and expected payoffs "
                "standing in for the release gamble. Real verification can fail or be unavailable. Equation (7.3) only prices a "
                "policy it is handed; choosing the better one needs the extra comparison of Equation (7.4). The workbench scenarios "
                "put the release probabilities 0.80 and 0.95 on a payoff of 100."
            ),
            "check": "If a verified release were worth 90 (support probability 0.90), release at once were worth 85 and verifying cost 8, what would verifying be worth at the start with gamma = 1, and does the controller verify?",
            "answer": "Verifying is worth (-8) + 90 = 82 and releasing at once is worth 85, so the controller releases. The break-even cost is 90 - 85 = 5.",
            "provenance": "Constructed example: the book's three-state controller (release values 85 and 97, verification cost 5; the break-even cost 12 and the break-even discount 0.9278 are derived from it as 97 - 85 and 90/97, not stated in the chapter) and the original workbench problems II.1 and II.3 (80, 95, cost 6, discount 0.90 and 0.75), computed with the laboratory's backward induction.",
            "source_section": "Three states, computed backward",
            "source_anchor": "three-states-computed-backward",
            "misconception": {
                "title": "Judging verification by its own reward",
                "text": ("On a one-step ledger verification scores (-5) against 85 for releasing, so the controller never asks. The chapter's "
                         "point is that the verified state's value comes back through the successor term: (-5) + 97 = 92, a gain of 7."),
            },
            "scope_note": {
                "text": ("Backward induction requires a state space small enough to enumerate, which agent state spaces are not, and "
                         "Chapter 9 addresses that directly. The two-step example is constructed for teaching."),
                "source_section": "What this does not settle",
            },
            "stepper": "stage",
            "controls": [
                {"key": "scenario", "label": "Scenario", "values": ["book", "tie", "wb1", "wb3"], "default": "book",
                 "value_labels": ["Chapter controller: cost 5", "Chapter controller: break-even cost 12",
                                  "Workbench II.1: 80, 95, cost 6, discount 0.90", "Workbench II.3: discount 0.75"]},
                {"key": "stage", "label": "Backward step", "values": [0, 1, 2], "default": 0,
                 "value_labels": ["1. Terminal state", "2. Verified state", "3. Start state"]},
            ],
            "function": "backward_picture",
        },
        {
            "id": "C07-D03",
            "title": "How many decisions are left can change the answer",
            "question": "When does it pay to spend a step investing in a later payoff instead of taking a smaller payoff now?",
            "equations": [EQ_OPTIMAL],
            "symbols": (
                "V*(x) is the best achievable value from state x. For each action a, the bracket is the immediate reward r plus "
                "gamma times the value of the next state x', averaged over where the action leads with probability P(x' | x, a); "
                "that bracketed value of one action is its action value Q. The max keeps the largest. The start state offers a stopping "
                "action (cash 2, or now 1) or an investing action (prepare -1 then a release of 6, or later 0 then a collection of 4). "
                "The horizon is the number of decisions remaining."
            ),
            "prediction": "With gamma = 1 in the cash or prepare model, does preparing beat cash when two decisions remain? And when only one remains?",
            "prediction_options": ["Prepare with two left, cash with one left", "Cash with either", "Prepare with either"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "With two left, prepare is (-1) + 1 x 6 = 5 against cash 2. With one left, preparing is worth -1 because no decision remains to release.",
                "incorrect": "Choose the cash or prepare model at discount 1.00 and step the decisions remaining: two left gives prepare 5 against cash 2; one left gives prepare (-1) against 2.",
            },
            "explanation": (
                "With one decision left at the start, investing uses it and the next state has none left, so it is worth 0 and investing scores its cost. "
                "With two or more left the next state is worth its payoff, so investing scores its cost plus gamma times that payoff. Equation (7.4) "
                "compares that with the stopping action. A discount below one cuts the later payoff until stopping wins, and "
                "on the last call stopping is simply the best action: exploration has nothing left to improve."
            ),
            "application": (
                "A policy computed for three remaining steps can be wrong once steps have been spent (in the cash or prepare model at discount 1, "
                "preparing is right with two or three decisions left but wrong with one). Store the policy for "
                "each remaining horizon, and expect information-gathering moves to disappear near the end of a budget."
            ),
            "assumptions": (
                "A fully observed three-state model with certain transitions, rewards fixed in advance, and a stopping state that "
                "pays zero. The optimum holds inside this model only; an outage or a missing permission that the model omits "
                "can reverse the ranking. Ties are reported as ties."
            ),
            "check": "In the now or later model with two decisions left and gamma = 0.2, which action is worth more, and by how much?",
            "answer": "Later = 0 + 0.2 x 4 = 0.8 and now = 1 + 0.2 x 0 = 1.0, so now wins by 0.2. The break-even discount is (1 - 0) / 4 = 0.25.",
            "provenance": "Constructed example: the laboratory notebook's cash, prepare and release values (2, -1, 6) for the default and changed cases, and its transfer values (now 1, later 0, collect 4), computed with the laboratory's backward induction.",
            "source_section": "Horizons, and why agents have short ones",
            "source_anchor": "horizons-and-why-agents-have-short-ones",
            "misconception": {
                "title": "One policy for every remaining horizon",
                "text": ("The chapter says the same context with three calls left and with one call left are different states with different values. "
                         "At discount 1 preparing wins with two or three decisions left and loses with one, so a policy stored for three steps cannot be reused unchanged on the last call."),
            },
            "scope_note": {
                "text": ("The recursion assumes a Markov state. Direct model-based computation and state-indexed action selection add "
                         "requirements for a specified model and access to that state, respectively."),
                "source_section": "What this does not settle",
            },
            "stepper": "horizon",
            "controls": [
                {"key": "model", "label": "Model", "values": ["prep", "wait"], "default": "prep",
                 "value_labels": ["Cash or prepare (notebook default and changed)", "Now or later (notebook transfer)"]},
                {"key": "horizon", "label": "Decisions remaining", "values": [1, 2, 3], "default": 2},
                {"key": "discount", "label": "Discount factor gamma", "values": [1.0, 0.5], "default": 1.0},
            ],
            "function": "horizon_picture",
        },
        {
            "id": "C07-D04",
            "title": "A residual bounds the error of a value guess",
            "question": "If you only check how far a candidate value function is from its own one-step lookahead, what do you learn about its distance from the best values?",
            "equations": [EQ_RESIDUAL, EQ_OPTIMAL],
            "symbols": (
                "V is a candidate value for each state. T maps V to the one-step lookahead values, the right side of Equation (7.4). "
                "V* is the best achievable value. The double bars with a small infinity mean the largest absolute difference over "
                "the three states. ||TV - V|| is the residual, ||V - V*|| the actual error, and gamma the discount factor, which "
                "must be below 1 for the bound. The stages are the all-zeros guess, the value of releasing at once, and the values "
                "after one improvement step."
            ),
            "prediction": "At gamma = 0.99, will the bound from the all-zero guess be close to the actual error, or far above it?",
            "prediction_options": ["Close to the actual error", "Far above the actual error", "Below the actual error"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "The residual is 97 and 97 / (1 - 0.99) = 9700, a hundred times the true error of 97.",
                "incorrect": "Set gamma to 0.99 at the all-zeros stage: the bound is 97 / 0.01 = 9700 against a true error of 97. Dividing by 1 - gamma inflates it.",
            },
            "explanation": (
                "The residual measures the largest one-step inconsistency in the guess. Dividing by 1 - gamma, the contraction "
                "margin, turns that into a ceiling on the true error, so the ceiling grows as gamma approaches 1 and does not "
                "exist at 1. Stepping through the stages shows the residual shrink as the guess improves: releasing at once is the "
                "value of one policy, the improvement step picks the better start action, and a guess that already satisfies the "
                "recursion has residual 0 and so has error 0."
            ),
            "application": (
                "When values are learned or approximated, the residual can be computed without knowing V*. A small residual with a "
                "discount well below 1 is a certificate about the declared model, not about the world the model describes."
            ),
            "assumptions": (
                "A finite model with bounded rewards and 0 <= gamma < 1. The three-state controller here (verification cost 5, "
                "verified release 97, unverified release 85) is constructed, and a discount below 1 changes which start action "
                "is best compared with the chapter's undiscounted case. A small residual against a wrong model still guides a bad action."
            ),
            "check": "For the all-zeros guess at gamma = 0.9, the residual is 97. What does Equation (7.5) allow the error to be, at most?",
            "answer": "97 / (1 - 0.9) = 97 / 0.1 = 970. The true error is 97, well inside that ceiling.",
            "provenance": "Constructed example: the book's three-state controller values with discount factors defined for the reader; best values computed with the laboratory's backward induction and each lookahead step computed with the laboratory's one-step backward update.",
            "source_section": "Where the reward comes from",
            "source_anchor": "where-the-reward-comes-from",
            "misconception": {
                "title": "A small residual means a good action",
                "text": ("The chapter says model error is not solution error: a small residual against a wrong transition or reward law can still guide a bad action. "
                         "The bound certifies the values only for the declared model."),
            },
            "scope_note": {
                "text": "These results describe the supplied rewards, transitions, state, and discount convention. They cannot validate those inputs.",
                "source_section": "Summary",
            },
            "stepper": "stage",
            "controls": [
                {"key": "discount", "label": "Discount factor gamma", "values": [0.9, 0.95, 0.99, 1.0], "default": 0.95},
                {"key": "stage", "label": "Candidate value function", "values": [0, 1, 2], "default": 0,
                 "value_labels": ["1. All zeros", "2. Value of releasing at once", "3. After the improvement step"]},
            ],
            "function": "residual_picture",
        },
    ],
}

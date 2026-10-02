"""Chapter 7 reader: The Equation That Looks Ahead.

Four demonstrations built on Equations (7.1), (7.3), (7.4) and (7.5).
Demonstrations 2, 3 and 4 call the laboratory's own backward induction
(math_ai_agents.chapters.ch07.evaluate) for the optimal values, so the
reader, the notebook and the chapter skill agree. Every number is a
constructed teaching value. Demonstration 2 uses the book's three-state
controller (85, 97, cost 5); Demonstration 3 uses the notebook's cash, prepare
and release values (2, -1, 6).
"""
import math

import numpy as np

from math_ai_agents.chapters.ch07 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

EQ_RETURN = r"\operatorname{Ret}_t=\sum_{k=0}^{\infty}\gamma^{k}r_{t+k}"
EQ_BELLMAN = (r"\begin{aligned}V^{\pi}(x)&=\sum_{a}\pi(a\mid x)\sum_{x'}P(x'\mid x,a)\\"
              r"&\quad\cdot\Bigl[r(x,a,x')+\gamma V^{\pi}(x')\Bigr].\end{aligned}")
EQ_OPTIMAL = r"V^{\star}(x)=\max_{a}\sum_{x'}P(x'\mid x,a)\Bigl[r(x,a,x')+\gamma V^{\star}(x')\Bigr]"
EQ_RESIDUAL = r"\|V-V^\star\|_\infty\leq \frac{\|TV-V\|_\infty}{1-\gamma}"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
RELEASE_UNVERIFIED = 85.0  # book: support probability 0.85 on a release worth 100
VERIFY_COST_BOOK = 5.0


def small(x):
    """Show a value with enough decimals that small numbers do not collapse to zero."""
    x = float(x)
    if abs(x) >= 1:
        return fmt(x, 1)
    if abs(x) >= 0.01:
        return fmt(x, 2)
    return fmt(x, 4)


# Demonstration 1: what a discount factor does to a delayed reward

DISCOUNTS = [0.8, 0.9, 0.95, 0.99]


def discount_picture(gamma=0.9, steps=10):
    gamma, steps = float(gamma), int(steps)
    k = np.arange(0, 101)
    scale = 1.0 / (1.0 - gamma)
    worth = 100.0 * gamma ** steps
    at_scale = 100.0 * gamma ** scale
    fig, ax = new_figure(height=4.2)
    for g in DISCOUNTS:
        if g != gamma:
            ax.plot(k, 100.0 * g ** k, color=PALETTE["light"], linewidth=1.4)
    ax.plot(k, 100.0 * gamma ** k, color=PALETTE["teal"], linewidth=2.4)
    ax.plot([scale], [at_scale], "D", color=PALETTE["navy"], markersize=13, zorder=3, clip_on=False)
    ax.plot([steps], [worth], "o", color=PALETTE["terracotta"], markersize=8, markeredgecolor="white",
            markeredgewidth=1.5, zorder=4, clip_on=False)
    ax.axvline(steps, color=PALETTE["terracotta"], linestyle="dotted", linewidth=1.3)
    ax.text(0.98, 0.95, f"circle: worth {small(worth)} at {steps} steps", transform=ax.transAxes, ha="right", va="top",
            fontsize=11, color=PALETTE["terracotta"])
    ax.text(0.98, 0.87, f"diamond: scale 1/(1 - gamma) = {fmt(scale, 0)} steps", transform=ax.transAxes, ha="right", va="top",
            fontsize=11, color=PALETTE["navy"])
    others = ", ".join(fmt(g, 2) for g in DISCOUNTS if g != gamma)
    ax.text(0.98, 0.79, f"teal: chosen gamma {fmt(gamma, 2)}\ngrey, steepest first: {others}",
            transform=ax.transAxes, ha="right", va="top", fontsize=11, color=PALETTE["teal"])
    ax.set_xlim(0, 102)
    ax.set_ylim(-6, 112)
    ax.set_yticks([0, 20, 40, 60, 80, 100])
    ax.set_xlabel("Steps until the reward arrives")
    ax.set_ylabel("Worth now of a reward of 100")
    ax.set_title(f"Discount factor {fmt(gamma, 2)}; reward of 100 arriving {steps} steps away", fontsize=11.5)
    metrics = {
        "Worth now": small(worth),
        "Share of its value kept": f"{fmt(worth, 2)} out of 100" if worth >= 0.01 else f"{fmt(worth, 4)} out of 100",
        "Planning scale 1/(1 - gamma)": f"{fmt(scale, 0)} steps",
        "Worth at that scale": fmt(at_scale, 1),
        "Return of 1 every step, forever": fmt(scale, 1),
    }
    interpretation = (
        f"Only the reward at step {steps} is counted here, so Equation (7.1) reduces to one term: "
        f"100 x {fmt(gamma, 2)}^{steps} = {small(worth)}. The scale 1/(1 - {fmt(gamma, 2)}) = 1 / {fmt(1 - gamma, 2)} = "
        f"{fmt(scale, 1)} steps is where a reward has fallen to roughly a third: 100 x {fmt(gamma, 2)}^{fmt(scale, 0)} = "
        f"{fmt(at_scale, 1)}. A steady reward of 1 per step adds up to 1 / (1 - {fmt(gamma, 2)}) = {fmt(scale, 1)}. "
        "The curve never reaches zero, so a large enough delayed reward can still outweigh an immediate cost."
    )
    return fig, metrics, interpretation


# Demonstration 2: three states, computed backward

def controller_states(verify_cost, verified_support):
    """Book's three-state controller in the laboratory's input format (expected rewards, gamma = 1)."""
    release_verified = 100.0 * float(verified_support)
    return {
        "unverified": {"actions": [
            {"name": "release", "reward": RELEASE_UNVERIFIED, "probabilities": [1.0], "next_states": ["done"]},
            {"name": "verify", "reward": -float(verify_cost), "probabilities": [1.0], "next_states": ["verified"]},
        ]},
        "verified": {"actions": [
            {"name": "release", "reward": release_verified, "probabilities": [1.0], "next_states": ["done"]},
        ]},
        "done": {"actions": [
            {"name": "stop", "reward": 0.0, "probabilities": [1.0], "next_states": ["done"]},
        ]},
    }


def lab_values(states, gamma, horizon=3, start="unverified"):
    out = evaluate({"horizon": horizon, "discount": gamma, "start": start, "states": states})
    m = out["metrics"]
    return m["values_by_remaining_steps"][horizon], m["policy_by_remaining_steps"][horizon - 1]


def backward_picture(verify_cost=5, verified_support=0.97):
    c, q = float(verify_cost), float(verified_support)
    states = controller_states(c, q)
    values, policy = lab_values(states, 1.0)
    v_verified = 100.0 * q + 0.0            # value of the verified state: release, then terminal value 0
    v_release = RELEASE_UNVERIFIED + 0.0    # policy: release at once
    v_verify = -c + v_verified              # policy: verify, then release
    if not (math.isclose(values["unverified"], max(v_release, v_verify), abs_tol=1e-9)
            and math.isclose(values["verified"], v_verified, abs_tol=1e-9)):
        raise AssertionError("laboratory backward induction disagrees with the hand values")
    tie = math.isclose(v_release, v_verify, abs_tol=1e-9)
    verify_wins = v_verify > v_release and not tie
    rows = [
        ("Terminal state", 0.0, 0.0, "value 0.0"),
        ("Verified: release", v_verified, 0.0, f"value {fmt(v_verified, 1)}"),
        ("Start, policy: release at once", v_release, 0.0, f"value {fmt(v_release, 1)}"),
        ("Start, policy: verify then release", -c, v_verified, f"value {fmt(v_verify, 1)}"),
    ]
    fig, ax = new_figure(height=4.0)
    ys = np.arange(len(rows))[::-1]
    for y, (name, immediate, cont, text) in zip(ys, rows):
        ax.barh(y, immediate, left=0, height=0.52, color=PALETTE["navy"] if immediate >= 0 else PALETTE["terracotta"])
        start = immediate if immediate >= 0 else 0.0
        if cont:
            ax.barh(y, cont, left=start, height=0.52, color="white", edgecolor=PALETTE["teal"], hatch="///", linewidth=1.2)
        total = immediate + cont
        ax.plot([total], [y], "D", color=PALETTE["gold"], markersize=9, markeredgecolor=PALETTE["ink"])
        top = name.startswith("Start") and ((name.endswith("then release") and (verify_wins or tie))
                                            or (name.endswith("at once") and (not verify_wins or tie)))
        tag = (" (tied)" if tie else " (highest)") if top else ""
        ax.text(max(start + cont, total, 0) + 8, y, text.replace("value ", "") + tag, va="center", fontsize=11, color=PALETTE["ink"])
    ax.text(0.98, 0.97, "solid: reward now\nhatched: value of what follows\ndiamond: total value", transform=ax.transAxes,
            ha="right", va="top", fontsize=10.5, color=PALETTE["ink"])
    ax.axvline(0, color=PALETTE["ink"], linewidth=1.0)
    ax.set_yticks(ys, [r[0] for r in rows])
    ax.set_xlim(-30, 160)
    ax.set_xlabel("Utility (constructed units)")
    ax.set_ylabel("State and policy")
    ax.set_title(f"Verifying costs {fmt(c, 0)}; a verified release is worth {fmt(v_verified, 0)}", fontsize=11.5)
    ax.grid(axis="y", alpha=0)
    if tie:
        verdict = (f"The two start values tie at {fmt(v_release, 1)}. Equation (7.3) prices each policy faithfully but "
                   "the comparison of Equation (7.4) cannot choose between them; a person or a stated tie-break must.")
        chosen = "tie"
    elif verify_wins:
        verdict = (f"Verify then release is worth {fmt(v_verify - v_release, 1)} more, so the controller verifies even though "
                   f"verifying scores {signed(-c, 1)} on a one-step ledger against {fmt(v_release, 1)} for releasing.")
        chosen = "verify"
    else:
        verdict = (f"Releasing at once is worth {fmt(v_release - v_verify, 1)} more, so the controller releases: "
                   "this verification costs more than the support it buys.")
        chosen = "release"
    metrics = {
        "Value of the verified state": fmt(v_verified, 1),
        "Start value, release at once": fmt(v_release, 1),
        "Start value, verify then release": fmt(v_verify, 1),
        "Gain from verifying": signed(v_verify - v_release, 1),
        "Chosen at the start": chosen,
    }
    interpretation = (
        f"Working backward: terminal 0, then verified = {fmt(100 * q, 1)} + 0 = {fmt(v_verified, 1)}. At the start, release = "
        f"{fmt(v_release, 1)} + 0 = {fmt(v_release, 1)} and verify = {signed(-c, 1)} + {fmt(v_verified, 1)} = {fmt(v_verify, 1)}. "
        f"Gain from verifying = {fmt(v_verify, 1)} - {fmt(v_release, 1)} = {signed(v_verify - v_release, 1)}. {verdict} "
        f"The break-even verification cost is {fmt(v_verified, 1)} - {fmt(v_release, 1)} = {fmt(v_verified - v_release, 1)}."
    )
    return fig, metrics, interpretation


# Demonstration 3: the remaining horizon decides which action wins

def horizon_states(gamma):
    """The laboratory notebook's draft, ready and done states."""
    one = [1.0]
    return {
        "draft": {"actions": [
            {"name": "cash", "reward": 2.0, "probabilities": one, "next_states": ["done"]},
            {"name": "prepare", "reward": -1.0, "probabilities": one, "next_states": ["ready"]},
        ]},
        "ready": {"actions": [{"name": "release", "reward": 6.0, "probabilities": one, "next_states": ["done"]}]},
        "done": {"actions": [{"name": "stop", "reward": 0.0, "probabilities": one, "next_states": ["done"]}]},
    }


def q_values(h, gamma):
    """Action values for the start state with h decisions left (Equation 7.4, written out)."""
    v_ready_after = 6.0 if h - 1 >= 1 else 0.0  # value of ready with h - 1 decisions left
    return {"cash": 2.0 + gamma * 0.0, "prepare": -1.0 + gamma * v_ready_after}


def horizon_picture(horizon=2, discount=1.0):
    h, g = int(horizon), float(discount)
    states = horizon_states(g)
    lab_start = {}
    for n in (1, 2, 3):
        out = evaluate({"horizon": n, "discount": g, "start": "draft", "states": states})
        lab_start[n] = (out["metrics"]["start_value"], out["metrics"]["policy_by_remaining_steps"][n - 1]["draft"])
    q = q_values(h, g)
    best = max(q.values())
    tie = math.isclose(q["cash"], q["prepare"], abs_tol=1e-9)
    chosen = "tie" if tie else max(q, key=q.get)
    for n in (1, 2, 3):
        qn = q_values(n, g)
        if not math.isclose(lab_start[n][0], max(qn.values()), abs_tol=1e-9):
            raise AssertionError("laboratory backward induction disagrees with the hand values")
        if not math.isclose(qn["cash"], qn["prepare"], abs_tol=1e-9) and lab_start[n][1] != max(qn, key=qn.get):
            raise AssertionError("laboratory policy disagrees with the hand values")

    fig, (left, right) = new_figure(ncols=2, height=4.2)
    hs = np.array([1, 2, 3])
    cash_line = np.array([q_values(n, g)["cash"] for n in hs])
    prep_line = np.array([q_values(n, g)["prepare"] for n in hs])
    left.plot(hs, cash_line, "s-", color=PALETTE["terracotta"], markersize=7)
    left.plot(hs, prep_line, "o-", color=PALETTE["teal"], markersize=7)
    left.axvline(h, color=PALETTE["grey"], linestyle="dashed", linewidth=1.3)
    if prep_line[-1] > cash_line[-1] + 1e-9:  # cash is the lower line: label it below, prepare above
        label_point(left, 3, cash_line[-1], "cash", color=PALETTE["terracotta"], dx=-6, dy=-10, ha="right", va="top").set_bbox(BOX)
        label_point(left, 3, prep_line[-1], "prepare", color=PALETTE["teal"], dx=-6, dy=8, ha="right").set_bbox(BOX)
    else:  # prepare is the lower (or equal) line: cash above, prepare below
        label_point(left, 3, cash_line[-1], "cash", color=PALETTE["terracotta"], dx=-6, dy=8, ha="right").set_bbox(BOX)
        label_point(left, 3, prep_line[-1], "prepare", color=PALETTE["teal"], dx=-6, dy=-10, ha="right", va="top").set_bbox(BOX)
    label_point(left, h, 7.0, "selected", color=PALETTE["grey"], dx=5 if h < 3 else -5, dy=0,
                ha="left" if h < 3 else "right", va="top").set_bbox(BOX)
    left.set_xticks([1, 2, 3])
    left.set_xlim(0.7, 3.3)
    left.set_ylim(-2, 7.4)
    left.set_xlabel("Decisions remaining")
    left.set_ylabel("Action value at the start")
    left.set_title(f"Discount {fmt(g, 2)}: value of each action", fontsize=11.5)

    grid = np.linspace(0, 1, 101)
    cash_g = np.full_like(grid, 2.0)
    prep_g = -1.0 + grid * (6.0 if h >= 2 else 0.0)
    right.plot(grid, cash_g, color=PALETTE["terracotta"], linewidth=2)
    right.plot(grid, prep_g, color=PALETTE["teal"], linewidth=2)
    right.plot([g], [q["cash"]], "s", color=PALETTE["terracotta"], markersize=8)
    right.plot([g], [q["prepare"]], "o", color=PALETTE["teal"], markersize=8)
    right.axvline(g, ymax=1.0 if h >= 2 else 0.5, color=PALETTE["grey"], linestyle="dashed", linewidth=1.3)
    label_point(right, 0.0, 2.0, "cash", color=PALETTE["terracotta"], dx=4, dy=8, ha="left").set_bbox(BOX)
    if h >= 2:
        label_point(right, 1.0, 5.0, "prepare", color=PALETTE["teal"], dx=-6, dy=0, ha="right", va="center").set_bbox(BOX)
        right.plot([0.5], [2.0], "*", color=PALETTE["ink"], markersize=12)
        label_point(right, 0.5, 2.0, "break-even 0.50", color=PALETTE["ink"], dx=8, dy=-14, ha="left", va="top").set_bbox(BOX)
    else:
        label_point(right, 1.0, -1.0, "prepare", color=PALETTE["teal"], dx=-6, dy=8, ha="right").set_bbox(BOX)
        label_point(right, 0.5, 5.2, "no break-even: preparing\npays nothing with one decision left",
                    color=PALETTE["ink"], dx=0, dy=0, ha="center", va="center").set_bbox(BOX)
    right.set_xlim(0, 1.02)
    right.set_ylim(-2, 7.4)
    right.set_xlabel("Discount factor")
    right.set_ylabel("Action value at the start")
    right.set_title(f"With {h} decision{'s' if h > 1 else ''} left: value against discount", fontsize=11.5)

    breakeven = "0.50" if h >= 2 else "undefined (preparing has no payoff to discount)"
    metrics = {
        "Value of cash": fmt(q["cash"], 2),
        "Value of prepare": signed(q["prepare"], 2),
        "Start value (the larger)": fmt(best, 2),
        "Chosen": chosen,
        "Break-even discount": breakeven,
    }
    ready_value = 6.0 if h >= 2 else 0.0
    calc = (f"Cash = 2 + {fmt(g, 2)} x 0 = {fmt(q['cash'], 2)}. Prepare = (-1) + {fmt(g, 2)} x {fmt(ready_value, 0)} = "
            f"{signed(q['prepare'], 2)}, because the ready state is worth {fmt(ready_value, 0)} with {h - 1} decision"
            f"{'s' if h - 1 != 1 else ''} left.")
    if tie:
        verdict = (" The two actions tie exactly, so Equation (7.4) returns both as maximizers and the discount sits "
                   "on the break-even value (-1 + 6 x gamma = 2 gives gamma = 0.5).")
    elif chosen == "prepare":
        verdict = f" Prepare wins by {fmt(q['prepare'] - q['cash'], 2)}: the cost now is repaid by the release it enables."
    else:
        if h < 2:
            verdict = (" Cash wins because one decision leaves no time to collect the release; a controller that ignores "
                       "its deadline would prepare and run out of steps.")
        else:
            verdict = f" Cash wins by {fmt(q['cash'] - q['prepare'], 2)}: the discount shrinks the later release below the immediate payoff."
    interpretation = calc + verdict + " A third decision adds nothing, because the terminal state pays zero."
    return fig, metrics, interpretation


# Demonstration 4: a residual bounds the error of a candidate value function

CANDIDATES = {
    "zeros": ("All zeros", {"unverified": 0.0, "verified": 0.0, "done": 0.0}),
    "one_step": ("Best immediate reward", {"unverified": 85.0, "verified": 97.0, "done": 0.0}),
}
STATE_NAMES = {"unverified": "start", "verified": "verified", "done": "terminal"}


def bellman_image(v, gamma):
    """T applied to a candidate V for the book's controller (cost 5, verified support 0.97)."""
    return {
        "unverified": max(RELEASE_UNVERIFIED + gamma * v["done"], -VERIFY_COST_BOOK + gamma * v["verified"]),
        "verified": 97.0 + gamma * v["done"],
        "done": 0.0 + gamma * v["done"],
    }


def residual_picture(discount=0.95, candidate="zeros"):
    g = float(discount)
    label, v = CANDIDATES[candidate]
    v_star, _ = lab_values(controller_states(VERIFY_COST_BOOK, 0.97), g)
    tv = bellman_image(v, g)
    keys = ["unverified", "verified", "done"]
    residual = max(abs(tv[s] - v[s]) for s in keys)
    error = max(abs(v[s] - v_star[s]) for s in keys)
    defined = 1.0 - g > 1e-12
    bound = residual / (1.0 - g) if defined else None
    if defined and error > bound + 1e-9:
        raise AssertionError("Equation (7.5) violated")

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    x = np.arange(len(keys))
    w = 0.26
    left.bar(x - w, [v[s] for s in keys], w, color=PALETTE["light"], edgecolor=PALETTE["ink"], hatch="..", label="V")
    left.bar(x, [tv[s] for s in keys], w, color=PALETTE["gold"], edgecolor=PALETTE["ink"], hatch="//")
    left.bar(x + w, [v_star[s] for s in keys], w, color=PALETTE["teal"], edgecolor=PALETTE["ink"])
    left.set_xticks(x, [STATE_NAMES[s] for s in keys])
    left.set_ylim(0, 128)
    left.set_xlim(-0.6, 2.6)
    left.set_xlabel("State")
    left.set_ylabel("Value")
    left.set_title("Candidate V, its one-step lookahead TV, and V*", fontsize=11.5)
    for xi, text, color in ((-w, "V", PALETTE["ink"]), (0, "TV", PALETTE["gold"]), (w, "V*", PALETTE["teal"])):
        label_point(left, 0 + xi, 106.0, text, color=color, dx=0, dy=0, ha="center", va="bottom")
    left.set_xlim(-0.6, 2.6)

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
            right.text(max(val, 0) * 1.25 + 0.4, y, fmt(val, 1), va="center", fontsize=11, color=PALETTE["ink"])
    right.set_xscale("symlog", linthresh=1)
    right.set_xlim(0, 400000)
    right.set_yticks(ypos, names)
    right.set_ylim(-0.6, 2.6)
    right.set_xlabel("Size in utility units (compressed scale)")
    right.set_ylabel("Quantity")
    right.set_title(f"Discount {fmt(g, 2)}: error never exceeds the bound" if defined
                    else f"Discount {fmt(g, 2)}: no bound exists", fontsize=11.5)
    right.grid(axis="y", alpha=0)

    stay = -VERIFY_COST_BOOK + g * v["verified"]
    sums = (f"At the start, TV = max(85 + {fmt(g, 2)} x {fmt(v['done'], 0)}, (-5) + {fmt(g, 2)} x {fmt(v['verified'], 0)}) = "
            f"max(85.0, {signed(stay, 2)}) = {fmt(tv['unverified'], 2)}, against V = {fmt(v['unverified'], 0)}. "
            f"The verified state gives TV = 97 + {fmt(g, 2)} x {fmt(v['done'], 0)} = {fmt(tv['verified'], 1)} against V = "
            f"{fmt(v['verified'], 0)}. The residual is the largest gap, {fmt(residual, 2)}.")
    if defined:
        if math.isclose(residual, 0.0, abs_tol=1e-9):
            tail = (f" Bound = {fmt(residual, 2)} / (1 - {fmt(g, 2)}) = {fmt(residual, 2)} / {fmt(1 - g, 2)} = 0.00, so V is exactly "
                    "V*: the bound certifies a zero error. Note that at this discount verifying no longer wins (it scores "
                    f"{fmt(stay, 2)} against 85.0).")
        else:
            tail = (f" Bound = {fmt(residual, 2)} / (1 - {fmt(g, 2)}) = {fmt(residual, 2)} / {fmt(1 - g, 2)} = {fmt(bound, 1)}. "
                    f"The true error is {fmt(error, 2)}, which is inside the bound, though the bound can be loose"
                    + (f" (here {fmt(bound / error, 1)} times the error)" if error > 1e-9 else "") + ". "
                    "It bounds error for this declared model only.")
    else:
        tail = (" With a discount of 1 the divisor 1 - 1 = 0, so Equation (7.5) gives no bound and the bound is undefined. "
                f"The actual error here is {fmt(error, 2)}; this finite-horizon model (its terminal state loops with reward 0) still has exact values, but the residual cannot certify them.")
    metrics = {
        "Residual ||TV - V||": fmt(residual, 2),
        "Actual error ||V - V*||": fmt(error, 2),
        "Bound from Equation (7.5)": fmt(bound, 1) if defined else undefined_text(),
        "Best start action under V*": "verify" if -VERIFY_COST_BOOK + g * v_star["verified"] > RELEASE_UNVERIFIED + 1e-9
        else ("tie" if math.isclose(-VERIFY_COST_BOOK + g * v_star["verified"], RELEASE_UNVERIFIED, abs_tol=1e-9) else "release"),
    }
    return fig, metrics, f"Candidate: {label.lower()}. " + sums + tail


def undefined_text():
    from readerkit import undefined
    return undefined("1 - gamma = 0, so Equation (7.5) gives no bound")


CHAPTER = {
    "number": 7,
    "title": "The Equation That Looks Ahead",
    "subtitle": "A choice made now must carry the value of what it makes possible later, and one recursion computes that value without anyone folding it in by hand.",
    "summary": (
        "These four demonstrations follow the chapter's document controller. It can release a report now or spend a step "
        "verifying first. Each demonstration changes one declared input (a discount, a cost, the time left, a candidate "
        "answer) and shows how the value of the future enters the present comparison."
    ),
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
                "The factors 0.8 to 0.99 are values chosen for the reader. Reading gamma as a survival probability needs a separate "
                "assumption of independent continuation; time preference does not."
            ),
            "check": "With gamma = 0.95, about how many steps does it take for a reward to fall to roughly a third of its value, and what is a reward of 100 worth at 20 steps?",
            "answer": "The scale is 1 / (1 - 0.95) = 1 / 0.05 = 20 steps, and 100 x 0.95^20 = 35.8, roughly a third.",
            "provenance": "Constructed example: the chapter's discount arithmetic for a reward of 100, with factors 0.9, 0.95 and 0.99 from the text and 0.8 added for the reader.",
            "source_section": "What discounting does to a number",
            "source_anchor": "what-discounting-does-to-a-number",
            "controls": [
                {"key": "gamma", "label": "Discount factor gamma", "values": [0.8, 0.9, 0.95, 0.99], "default": 0.9},
                {"key": "steps", "label": "Steps until the reward arrives", "values": [10, 50], "default": 10},
            ],
            "function": "discount_picture",
        },
        {
            "id": "C07-D02",
            "title": "Three states, computed backward",
            "question": "Verifying costs something now. Can it still be the better first move, and at what cost does it stop being so?",
            "equations": [EQ_BELLMAN],
            "symbols": (
                "V^pi(x) is the value of state x when the agent follows policy pi. pi(a | x) is the chance the policy takes action a "
                "in x, P(x' | x, a) the chance of landing in state x', r(x, a, x') the reward on that move, and gamma the discount "
                "factor, here set to 1, which a finite horizon permits. The states are start, verified and terminal. Releasing pays the "
                "expected payoff of the release (85 at the start, 100 times the chosen support probability once verified)."
            ),
            "prediction": "With verification costing 12 and a verified release worth 97, how do the two start policies compare: is either one worth more?",
            "explanation": (
                "Start at the terminal state, whose remaining value is 0. The verified state has one action, so its value is its "
                "release payoff plus 0. At the start, releasing at once is worth 85 plus 0, while verifying is worth minus its "
                "cost plus the verified state's value. The comparison that a one-step ledger misses sits in the second term."
            ),
            "application": (
                "When a check, a retrieval or a clarifying question looks like pure cost, write the value of the state it leads "
                "to and compare. The break-even cost, the verified value minus the immediate release value, tells you how expensive "
                "the check can be before skipping it is right."
            ),
            "assumptions": (
                "Three states, one verification opportunity, deterministic movement into the verified state, and expected payoffs "
                "standing in for the release gamble. Real verification can fail or be unavailable. Equation (7.3) only prices a "
                "policy it is handed; choosing the better one needs the extra comparison of Equation (7.4)."
            ),
            "check": "If a verified release were worth 90 (support probability 0.90) and verifying cost 8, what would verifying be worth at the start, and does the controller verify?",
            "answer": "Verifying is worth (-8) + 90 = 82, releasing at once is worth 85, so the controller releases. The break-even cost is 90 - 85 = 5.",
            "provenance": "Constructed example: the book's three-state controller (release values 85 and 97, verification cost 5), with other costs and a 0.90 support probability defined for the reader and computed with the laboratory's backward induction.",
            "source_section": "Three states, computed backward",
            "source_anchor": "three-states-computed-backward",
            "controls": [
                {"key": "verify_cost", "label": "Cost of verifying", "values": [5, 12, 20], "default": 5},
                {"key": "verified_support", "label": "Support probability after verifying", "values": [0.97, 0.9], "default": 0.97},
            ],
            "function": "backward_picture",
        },
        {
            "id": "C07-D03",
            "title": "How many decisions are left can change the answer",
            "question": "When does it pay to spend a step preparing instead of taking a smaller payoff now?",
            "equations": [EQ_OPTIMAL],
            "symbols": (
                "V*(x) is the best achievable value from state x. For each action a, the bracket is the immediate reward r plus "
                "gamma times the value of the next state x', averaged over where the action leads with probability P(x' | x, a). "
                "The max keeps the largest. Here the start state offers cash (reward 2, then finish) or prepare (reward -1, "
                "then a ready state whose release pays 6). The horizon is the number of decisions remaining."
            ),
            "prediction": "With gamma = 1, does preparing beat cash when two decisions remain? And when only one remains?",
            "explanation": (
                "With one decision left at the start, preparing uses it and the ready state has none left, so it is worth 0 and preparing scores -1. "
                "With two or more left the ready state is worth 6, so preparing scores -1 plus gamma times 6. Equation (7.4) "
                "compares that with cash, which scores 2. A discount below one cuts the later release until cash wins."
            ),
            "application": (
                "A policy computed for three remaining steps can be wrong once steps have been spent (in this model at discount 1, "
                "preparing is right with two or three decisions left but wrong with one). Store the policy for "
                "each remaining horizon, and expect information-gathering moves to disappear near the end of a budget."
            ),
            "assumptions": (
                "A fully observed three-state model with certain transitions, rewards fixed in advance, and a stopping state that "
                "pays zero. The optimum holds inside this model only; an outage or a missing permission that the model omits "
                "can reverse the ranking. Ties are reported as ties."
            ),
            "check": "With two decisions left and gamma = 0.4, which action is worth more, and by how much?",
            "answer": "Prepare = (-1) + 0.4 x 6 = 1.4 and cash = 2 + 0.4 x 0 = 2.0, so cash wins by 0.6. The break-even gamma is 0.5.",
            "provenance": "Constructed example: the laboratory notebook's cash, prepare and release values (2, -1, 6) computed with the laboratory's backward induction; the discount values are defined for the reader.",
            "source_section": "Horizons, and why agents have short ones",
            "source_anchor": "horizons-and-why-agents-have-short-ones",
            "controls": [
                {"key": "horizon", "label": "Decisions remaining", "values": [1, 2], "default": 2},
                {"key": "discount", "label": "Discount factor gamma", "values": [1.0, 0.75, 0.5, 0.25], "default": 1.0},
            ],
            "function": "horizon_picture",
        },
        {
            "id": "C07-D04",
            "title": "A residual bounds the error of a value guess",
            "question": "If you only check how far a candidate value function is from its own one-step lookahead, what do you learn about its distance from the best values?",
            "equations": [EQ_RESIDUAL],
            "symbols": (
                "V is a candidate value for each state. T maps V to the one-step lookahead values, the right side of Equation (7.4). "
                "V* is the best achievable value. The double bars with a small infinity mean the largest absolute difference over "
                "the three states. ||TV - V|| is the residual, ||V - V*|| the actual error, and gamma the discount factor, which "
                "must be below 1 for the bound."
            ),
            "prediction": "At gamma = 0.99, will the bound from an all-zero guess be close to the actual error, or far above it?",
            "explanation": (
                "The residual measures the largest one-step inconsistency in the guess. Dividing by 1 - gamma, the contraction "
                "margin, turns that into a ceiling on the true error, so the ceiling grows as gamma approaches 1 and does not "
                "exist at 1. A guess that already satisfies the recursion has residual 0 and so has error 0."
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
            "provenance": "Constructed example: the book's three-state controller values with discount factors defined for the reader; best values computed with the laboratory's backward induction.",
            "source_section": "Where the reward comes from",
            "source_anchor": "where-the-reward-comes-from",
            "controls": [
                {"key": "discount", "label": "Discount factor gamma", "values": [0.9, 0.95, 0.99, 1.0], "default": 0.95},
                {"key": "candidate", "label": "Candidate value function", "values": ["zeros", "one_step"], "default": "zeros",
                 "value_labels": ["All zeros", "Best immediate reward in each state"]},
            ],
            "function": "residual_picture",
        },
    ],
}

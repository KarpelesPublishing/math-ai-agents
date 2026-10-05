"""Chapter 14 reader: Building a World Inside.

Four demonstrations built on Equations (14.1) to (14.4).

D01  The chapter's temperature table (Figure 14.1): the score inside the learned
     model against the score in the actual environment, and what judging by
     only one column picks. The scores are the chapter's reported numbers.
D02  Equations (14.1) and (14.2) on the laboratory's own transition-model
     function (math_ai_agents.chapters.ch14.evaluate): the default, changed
     (horizon 20), transfer (identical kernels) and chapter-illustration cases,
     with the actual finite value error drawn under both valid bounds.
D03  Equation (14.3) and Figure 14.3: twelve constructed options, a gap, and an
     optimizer that climbs to the one place the model is generous.
D04  Equation (14.4): the certified horizon, including the Figure 14.2 gaps and
     the chapter's priced twenty-step plan.

Every example other than the reported table is a constructed teaching value.
"""
from fractions import Fraction
import math

import numpy as np

from math_ai_agents.chapters.ch14 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

# Equations copied from the chapter with the tag dropped.
EQ_EPS = r"\epsilon \;=\; \max_{x,a}\; \tfrac{1}{2}\sum_{x'}\big|\hat P(x'\mid x,a) - P(x'\mid x,a)\big|."
EQ_BOUND = r"\big|\hat V^{\pi}(x) - V^{\pi}(x)\big| \;\le\; \frac{\gamma\,\epsilon\,R}{(1-\gamma)^2}."
EQ_GAP = r"\Delta(x) \;=\; \max_{a}Q^{\pi}(x,a) \;-\; \max_{a \neq a^{*}}Q^{\pi}(x,a)."
EQ_HSTAR = (r"H^{*} \;=\; \max\Big\{ H \in \mathbb{Z}_{>0} \;:\; H \leq H_{\max},\;"
            r"R\,\epsilon\,H(H-1) \;<\; \Delta \Big\}.")

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
# A lighter halo for labels that sit beside curves, so the curve they name stays visible through it.
BOX_SOFT = {"boxstyle": "round,pad=0.08", "fc": "white", "ec": "none", "alpha": 0.45}

# The laboratory's default pair of kernels (data/examples and the workbook default case): two states, one fixed policy.
TRUE_KERNEL = [[0.9, 0.1], [0.2, 0.8]]


def lab_run(shift0, shift1, rewards=(0.0, 1.0), discount=0.9, horizon=1):
    """The laboratory's evaluate() on the default true kernel and a model kernel that moves
    shift0 of probability in state 1's row and shift1 in state 2's row."""
    model = [[0.9 - shift0, 0.1 + shift0], [0.2 + shift1, 0.8 - shift1]]
    return evaluate({"true_transition": TRUE_KERNEL, "model_transition": model, "rewards": list(rewards),
                     "discount": discount, "horizon": horizon})


# Demonstration 1: the reported temperature table

TABLE = [(0.10, 2086, 193), (0.50, 2060, 196), (1.00, 1145, 868), (1.15, 918, 1092), (1.30, 732, 753)]
RANDOM_POLICY = 210
LEADERBOARD = 820
RANDOM_SPREAD = 108
SPREADS = {0.10: ((2086, 140), (193, 58)), 1.15: ((918, 546), (1092, 556))}  # (dream, real), reported only for these rows


def dream_real_picture(temperature=0.10, judge="dream"):
    t = float(temperature)
    rows = {r[0]: r for r in TABLE}
    _, dream, real = rows[t]
    temps = [r[0] for r in TABLE]
    dreams = [r[1] for r in TABLE]
    reals = [r[2] for r in TABLE]
    col = dreams if judge == "dream" else reals
    win_i = int(np.argmax(col))
    win_t, win_dream, win_real = TABLE[win_i]
    fig, (left, right) = new_figure(ncols=2, height=4.4)
    xs = np.arange(len(TABLE))
    for ax, vals, color, name in ((left, dreams, PALETTE["teal"], "dream"), (right, reals, PALETTE["navy"], "real")):
        bars = ax.bar(xs, vals, 0.62, color=color, linewidth=0)
        for i, (tt, v) in enumerate(zip(temps, vals)):
            if tt == t:
                bars[i].set_edgecolor(PALETTE["ink"])
                bars[i].set_linewidth(2.6)
            top = v
            if tt in SPREADS:
                spread = SPREADS[tt][0 if name == "dream" else 1][1]
                ax.errorbar([i], [v], yerr=[spread], color=PALETTE["ink"], capsize=4, linewidth=1.3, zorder=5)
                top = v + spread
            ax.text(i, top + 40, str(v), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"],
                    bbox={"boxstyle": "round,pad=0.12", "fc": "white", "ec": "none", "alpha": 0.9}, zorder=6)
        ax.set_xticks(xs, [f"{tt:.2f}" for tt in temps])
        ax.set_ylim(0, 2750)
        ax.set_xlim(-0.6, len(TABLE) - 0.4)
        ax.set_xlabel("Sampling temperature of the imagined world")
        ax.grid(axis="x", alpha=0)
    left.set_ylabel("Score (reported)")
    right.set_ylabel("Score (reported)")
    left.set_title("Score inside the learned model", fontsize=11.5)
    right.set_title("Score in the actual environment", fontsize=11.5)
    right.axhspan(RANDOM_POLICY - RANDOM_SPREAD, RANDOM_POLICY + RANDOM_SPREAD, color=PALETTE["light"], alpha=0.45, linewidth=0, zorder=0)
    right.axhline(RANDOM_POLICY, color=PALETTE["grey"], linestyle="dashed", linewidth=1.6, label=f"random policy {RANDOM_POLICY} (band: its spread)")
    right.axhline(LEADERBOARD, color=PALETTE["olive"], linestyle="dotted", linewidth=2, label=f"best leaderboard entry {LEADERBOARD}")
    right.legend(loc="upper left", fontsize=10.5, frameon=True)
    judged = left if judge == "dream" else right
    judged_vals = dreams if judge == "dream" else reals
    judged.plot([win_i], [(judged_vals[win_i] + SPREADS[TABLE[win_i][0]][0 if judge == "dream" else 1][1] + 330) if (TABLE[win_i][0] in SPREADS) else judged_vals[win_i] + 260], marker="v", color=PALETTE["gold"],
                markersize=11, linestyle="none", zorder=7)
    metrics = {
        "Temperature": f"{t:.2f}",
        "Score inside the model": str(dream),
        "Score in the actual environment": str(real),
        "Model minus actual": str(dream - real),
        "Actual minus random policy (210)": str(real - RANDOM_POLICY),
        f"Picked by the {judge} column": f"{win_t:.2f}",
        "Picked: score in the actual environment": str(win_real),
        "Picked: actual minus random policy (210)": str(win_real - RANDOM_POLICY),
    }
    if t in SPREADS:
        (dv, ds), (rv, rs) = SPREADS[t]
        metrics["Reported spreads (model, actual)"] = f"{dv} +/- {ds}, {rv} +/- {rs}"
    if judge == "dream":
        verdict = (f"Judged only by the model column, the winner is T = {win_t:.2f} with {win_dream}. In the actual environment it "
                   f"scores {win_real}, and {win_real} - {RANDOM_POLICY} = {win_real - RANDOM_POLICY} puts it below the random policy: "
                   "ranked first and confidently wrong.")
    else:
        verdict = (f"Judged by the actual column, the winner is T = {win_t:.2f} with {win_real}, which is {win_real} - {LEADERBOARD} = "
                   f"{win_real - LEADERBOARD} above the best leaderboard entry. Only the second column can reveal this. The reported spread "
                   f"of {win_real} is +/- {SPREADS[win_t][1][1]}, larger than {win_real - LEADERBOARD}, so the reported range reaches the leaderboard entry and these numbers alone do not settle the ranking.")
    extra = ""
    if t == 0.10:
        extra = (" The chapter reports the authors' account of this row: at the lowest temperature the monsters fail to shoot at all "
                 "(mode collapse), so a policy learned in that imagined world scores near-perfectly and then fails in the actual one. "
                 "The reported spread 193 +/- 58 overlaps the random policy's 210 +/- 108.")
    elif t == 1.30:
        extra = " One notch above the best setting the actual score falls to 753, which the chapter reports as a less risky strategy with lower return variance."
    elif t == 1.15:
        extra = " This is the setting with the best reported actual score, 1092, although its model score is lower than at 0.10."
    interpretation = (
        f"At T = {t:.2f}: model {dream} - actual {real} = {dream - real}. Actual against the random policy: {real} - {RANDOM_POLICY} = {real - RANDOM_POLICY}. "
        f"Worst to best setting in the actual column: 1092 - 193 = 899 points. {verdict}{extra}"
    )
    steps = [
        f"Read the chosen row: model {dream}, actual {real}.",
        f"Model minus actual: {dream} - {real} = {dream - real}.",
        f"Actual minus the random policy's {RANDOM_POLICY}: {real} - {RANDOM_POLICY} = {real - RANDOM_POLICY}.",
        f"Rank the five settings by the {judge} column alone: the largest is {col[win_i]} at T = {win_t:.2f}.",
        f"That pick's actual score is {win_real}: {win_real} - {RANDOM_POLICY} = {win_real - RANDOM_POLICY} against the random policy.",
        "Spreads were reported only for 0.10 and 1.15; the table does not give the transition error of Equation (14.1).",
    ]
    alt = (f"Two bar charts of five sampling temperatures. Left, model scores from 2086 down to 732. Right, actual scores from 193 up to 1092 "
           f"with the random policy at 210 and the best leaderboard entry at 820. Judged by the {judge} column the pick is temperature "
           f"{win_t:.2f}; the highlighted row is {t:.2f}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: Equations (14.1) and (14.2), bound against actual error (laboratory function)

GAMMA_GRID = np.linspace(0.5, 0.995, 120)
CASES = {
    "default": {"shift": 0.02, "rewards": (0.0, 1.0), "horizon": 5, "identical": False,
                "heading": "Default case"},
    "changed": {"shift": 0.02, "rewards": (0.0, 1.0), "horizon": 20, "identical": False,
                "heading": "Changed case (horizon 20)"},
    "transfer": {"shift": 0.0, "rewards": (1.0, 2.0), "horizon": 4, "identical": True,
                 "heading": "Transfer case (identical kernels)"},
    "percent": {"shift": 0.01, "rewards": (0.0, 1.0), "horizon": 20, "identical": False,
                "heading": "Chapter illustration (error 0.01)"},
}


def case_run(case, discount):
    c = CASES[case]
    if c["identical"]:
        ident = [[1, 0], [0, 1]]
        return evaluate({"true_transition": ident, "model_transition": ident, "rewards": list(c["rewards"]),
                         "discount": discount, "horizon": c["horizon"]})
    return lab_run(c["shift"], c["shift"], rewards=c["rewards"], discount=discount, horizon=c["horizon"])


def two_reward_check(case, discount):
    """Hand check of the actual error after two rewards: V_2(x) = r(x) + gamma x sum P(x'|x) r(x')."""
    c = CASES[case]
    if c["identical"]:
        P = Q = [[1.0, 0.0], [0.0, 1.0]]
    else:
        s = c["shift"]
        P = TRUE_KERNEL
        Q = [[0.9 - s, 0.1 + s], [0.2 + s, 0.8 - s]]
    r = c["rewards"]
    out = []
    for i in range(2):
        v = r[i] + discount * (P[i][0] * r[0] + P[i][1] * r[1])
        w = r[i] + discount * (Q[i][0] * r[0] + Q[i][1] * r[1])
        vc = f"{fmt(r[i], 2)} + {fmt(discount, 2)} x ({fmt(P[i][0], 2)} x {fmt(r[0], 2)} + {fmt(P[i][1], 2)} x {fmt(r[1], 2)})"
        wc = f"{fmt(r[i], 2)} + {fmt(discount, 2)} x ({fmt(Q[i][0], 2)} x {fmt(r[0], 2)} + {fmt(Q[i][1], 2)} x {fmt(r[1], 2)})"
        out.append((v, w, abs(v - w), vc, wc))
    worst = max(range(2), key=lambda i: out[i][2])
    return worst + 1, out[worst]


def bound_picture(case="default", discount=0.9):
    c = CASES[case]
    gamma = float(discount)
    out = case_run(case, gamma)
    m = out["metrics"]
    eps = m["uniform_tv_error"]
    R = max(c["rewards"])
    H = c["horizon"]
    errors = out["series"][0]["y"]
    finite = out["series"][1]["y"]
    discounted = m["discounted_infinite_bound"]
    hs = np.arange(1, H + 1)
    exact_disc = gamma * eps * R / (1 - gamma) ** 2
    if not math.isclose(discounted, exact_disc, rel_tol=1e-9, abs_tol=1e-12):
        raise AssertionError("laboratory bound disagrees with Equation (14.2)")
    fig, (left, right) = new_figure(ncols=2, height=4.4)
    positive = eps > 0
    if positive:
        mask = hs >= 2  # at H = 1 both the error and the bound are exactly 0, which a log axis cannot show
        left.plot(hs[mask], np.array(finite)[mask], "s-", color=PALETTE["terracotta"], linewidth=1.8, markersize=5)
        left.plot(hs[mask], np.array(errors)[mask], "o-", color=PALETTE["teal"], linewidth=1.8, markersize=5)
        left.axhline(discounted, color=PALETTE["gold"], linestyle="dashed", linewidth=2)
        left.set_yscale("log")
        low = min(np.array(errors)[mask].min(), np.array(finite)[mask].min()) / 2.2
        high = max(discounted, finite[-1]) * 3.2
        left.set_ylim(low, high)
        left.set_xlim(1.5, H + 0.5)
        label_point(left, 1.6, discounted, f"discounted bound {fmt(discounted, 2)}", color=PALETTE["gold"], dx=0, dy=5,
                    ha="left", va="bottom").set_bbox({**BOX_SOFT, "alpha": 1.0})
        label_point(left, H, finite[-1], f"finite bound {fmt(finite[-1], 2)}", color=PALETTE["terracotta"], dx=-6, dy=9,
                    ha="right", va="bottom").set_bbox({**BOX_SOFT, "alpha": 1.0})
        label_point(left, H, errors[-1], f"actual {fmt(errors[-1], 3)}", color=PALETTE["teal"], dx=-6, dy=-10,
                    ha="right", va="top").set_bbox({**BOX_SOFT, "alpha": 1.0})
        left.set_ylabel("Value error in reward units (log scale)")
    else:
        left.plot(hs, errors, "o-", color=PALETTE["teal"], linewidth=1.8, markersize=5)
        left.plot(hs, finite, "s--", color=PALETTE["terracotta"], linewidth=1.5, markersize=5)
        left.set_ylim(-0.05, 1.0)
        left.set_xlim(0.5, H + 0.5)
        label_point(left, H, 0.0, "actual error and both bounds are 0", color=PALETTE["ink"], dx=0, dy=12, ha="right",
                    va="bottom").set_bbox({**BOX_SOFT, "alpha": 1.0})
        left.set_ylabel("Value error in reward units")
    left.set_xticks((hs[1:] if positive else hs) if H <= 5 else [2, 5, 10, 15, 20])
    left.set_xlabel("Reward horizon H")
    left.set_title(f"{c['heading']}: epsilon {fmt(eps, 2)}", fontsize=11.5)
    # Right panel: the compounding factor across discounts.
    scale = R / (1 - gamma)
    value_scale = R / (1 - GAMMA_GRID)
    right.plot(GAMMA_GRID, value_scale, color=PALETTE["grey"], linestyle="dashed", linewidth=1.8)
    right.axvline(gamma, color=PALETTE["light"], linewidth=1.2)
    right.plot([gamma], [scale], "s", color=PALETTE["grey"], markersize=8)
    right.set_yscale("log")
    right.set_xlim(0.47, 1.0)
    right.set_ylim(0.01, 5000)
    label_point(right, 0.52, value_scale[2], "largest possible value R/(1-gamma)", color=PALETTE["grey"], dx=0, dy=7,
                ha="left").set_bbox({**BOX_SOFT, "alpha": 1.0})
    if positive:
        curve = GAMMA_GRID * eps * R / (1 - GAMMA_GRID) ** 2
        right.plot(GAMMA_GRID, curve, color=PALETTE["terracotta"], linewidth=2.2)
        right.plot([gamma], [discounted], "o", color=PALETTE["terracotta"], markersize=9)
        label_point(right, 0.52, curve[2], "value-error bound", color=PALETTE["terracotta"], dx=0, dy=8,
                    ha="left").set_bbox({**BOX_SOFT, "alpha": 1.0})
    else:
        label_point(right, 0.52, 0.03, "bound is 0 for every gamma\n(epsilon = 0; no curve on a log axis)",
                    color=PALETTE["terracotta"], dx=0, dy=0, ha="left", va="bottom").set_bbox({**BOX_SOFT, "alpha": 1.0})
    right.set_xlabel("Discount factor gamma")
    right.set_ylabel("Reward units, log scale")
    right.set_title(f"gamma = {fmt(gamma, 2)}: bound {fmt(discounted, 2)}, value scale {fmt(scale, 1)}", fontsize=11.5)
    actual = m["max_finite_value_error"]
    fin = m["finite_horizon_bound"]
    tight = min(fin, discounted)
    which = "finite" if fin <= discounted else "discounted"
    if abs(fin - discounted) < 1e-12:
        which = "finite and discounted (equal)"
    metrics = {
        "Epsilon (Equation 14.1)": fmt(eps, 3),
        f"Actual error after H = {H}": fmt(actual, 4),
        f"Finite bound at H = {H}": fmt(fin, 3),
        "Discounted bound (Equation 14.2)": fmt(discounted, 3),
        "Tightest valid bound": fmt(tight, 3),
        "Largest possible value R/(1-gamma)": fmt(scale, 1),
    }
    s = c["shift"]
    row_calc = (f"1/2 x (|{fmt(0.9 - s, 2)} - 0.90| + |{fmt(0.1 + s, 2)} - 0.10|) = 1/2 x ({fmt(s, 2)} + {fmt(s, 2)}) = {fmt(eps, 2)}"
                if not c["identical"] else "1/2 x (|1.00 - 1.00| + |0.00 - 0.00|) = 0.00")
    state_no, (v2, w2, d2, vc2, wc2) = two_reward_check(case, gamma)
    if positive:
        ratio_text = (f"Each bound holds under its own assumptions; here the actual error {fmt(actual, 4)} is below both, "
                      f"{fmt(100 * actual / tight, 0)} percent of the smaller one ({which} bound {fmt(tight, 3)}).")
    else:
        ratio_text = ("With identical kernels every error and both bounds are exactly 0, a check that the recurrences and the matrix alignment are right. "
                      "The laboratory notes that a reward model that also differs would need an additional term.")
    interpretation = (
        f"Epsilon = {row_calc}. Finite bound = {fmt(R, 0)} x {fmt(eps, 2)} x {H} x {H - 1} / 2 = {fmt(fin, 3)}. "
        f"Discounted bound = {fmt(gamma, 2)} x {fmt(eps, 2)} x {fmt(R, 0)} / (1 - {fmt(gamma, 2)})^2 = {fmt(discounted, 3)}. "
        f"Check by hand after two rewards (state {state_no}): true {vc2} = {fmt(v2, 3)}; model {wc2} = {fmt(w2, 3)}; "
        f"|{fmt(v2, 3)} - {fmt(w2, 3)}| = {fmt(d2, 3)}. The two recurrences give {fmt(actual, 4)} after {H}"
        + (" (the left plot starts at H = 2 because H = 1 has error 0 and is not drawn)" if positive else "") + f". {ratio_text}"
    )
    steps = [
        f"Row error by Equation (14.1): {row_calc}.",
        f"Epsilon is the largest row error: {fmt(eps, 2)}. Rewards are shared; R = {fmt(R, 0)}.",
        f"Finite bound after H = {H}: R x eps x H(H-1)/2 = {fmt(R, 0)} x {fmt(eps, 2)} x {H} x {H - 1} / 2 = {fmt(fin, 3)}.",
        f"Discounted bound by Equation (14.2): gamma x eps x R / (1-gamma)^2 = {fmt(discounted, 3)}.",
        f"Each bound holds under its own assumptions; the smaller of the two numbers is {fmt(tight, 3)}.",
        f"Two rewards by hand (state {state_no}): V = {vc2} = {fmt(v2, 3)}, model {wc2} = {fmt(w2, 3)}, difference {fmt(d2, 3)}.",
        f"Actual error after {H} rewards, from the two recurrences: {fmt(actual, 4)}.",
    ]
    alt = (f"{c['heading']}. Left, on a log axis, the actual value error and the finite bound against the horizon up to {H}, with the "
           f"discounted bound {fmt(discounted, 2)} as a dashed line. Right, the bound and the largest possible value against the discount factor, "
           f"marked at gamma {fmt(gamma, 2)}." if positive else
           f"{c['heading']}. Left, the actual error and both bounds are zero at every horizon up to {H}. Right, the largest possible value against "
           f"the discount factor, marked at gamma {fmt(gamma, 2)}; the bound is zero.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: Equation (14.3) and Figure 14.3, twelve options

TRUE12 = [0.20, 0.30, 0.40, 0.50, 0.60, 0.90, 0.55, 0.45, 0.35, 0.25, 0.15, 0.10]  # constructed; best tool 6, runner-up tool 5
BEST_I, RUNNER_I, LAST_I = 5, 4, 11
PATTERNS = {
    "shared": "the same offset on every tool",
    "favorable": "one favorable error on tool 12 only",
    "adversarial": "best marked down, runner-up marked up",
}


def landscape_picture(pattern="shared", error=0.05):
    e = float(error)
    true = np.array(TRUE12)
    model = true.copy()
    if pattern == "shared":
        model = true + e
    elif pattern == "favorable":
        model[LAST_I] += e
    else:
        model[BEST_I] -= e
        model[RUNNER_I] += e
    err = model - true
    gap = float(true[BEST_I] - true[RUNNER_I])
    max_err = float(np.abs(err).max())
    mean_err = float(np.abs(err).mean())
    top = float(model.max())
    picks = [i for i in range(12) if math.isclose(model[i], top, abs_tol=1e-9)]
    certified = Fraction(str(e)) * 2 < Fraction(str(round(gap, 12)))
    fig, (left, right) = new_figure(ncols=2, height=4.4)
    xs = np.arange(1, 13)
    left.plot(xs, true, "o-", color=PALETTE["navy"], linewidth=1.8, markersize=6)
    left.plot(xs, model, "D--", color=PALETTE["terracotta"], linewidth=1.4, markersize=5, markerfacecolor="white")
    for i in picks:
        left.plot([xs[i]], [model[i]], "*", color=PALETTE["gold"], markersize=17, zorder=6)
        left.plot([xs[i], xs[i]], [true[i], model[i]], color=PALETTE["ink"], linewidth=1, linestyle=":")
    if len(picks) == 1:
        i = picks[0]
        word = f"picks tool {i + 1}: model {fmt(model[i], 2)}, true {fmt(true[i], 2)}"
    else:
        word = "tie: tools " + " and ".join(str(i + 1) for i in picks)
    top_y = max(1.2, top + 0.5)
    label_point(left, 0.7, top_y, "solid navy: true value, dashed hollow: model", color=PALETTE["ink"], dx=0, dy=-4, ha="left", va="top")
    label_point(left, 0.7, top_y, f"star: optimizer {word}", color=PALETTE["gold"], dx=0, dy=-20, ha="left", va="top")
    left.set_xlim(0.5, 12.5)
    left.set_ylim(0, top_y)
    left.set_xticks(xs)
    left.set_xlabel("Option (tool), constructed")
    left.set_ylabel("Action value Q")
    left.set_title(f"True gap {fmt(gap, 2)}; error {fmt(e, 2)}", fontsize=11.5)
    right.bar(xs, err, 0.62, color=PALETTE["terracotta"], linewidth=0)
    right.axhline(max_err, color=PALETTE["ink"], linewidth=1.6)
    right.axhline(mean_err, color=PALETTE["grey"], linewidth=1.6, linestyle="dashed")
    right.axhline(0, color=PALETTE["ink"], linewidth=0.8)
    rtop = max(e, 0.1) * 1.55
    right.set_ylim(-1.15 * max(e, 0.1), rtop)  # same limits for every pattern at one error size; room for the adversarial -e bar
    right.set_xlim(0.5, 12.5)
    right.set_xticks(xs)
    if math.isclose(max_err, mean_err, abs_tol=1e-12):
        label_point(right, 12.4, max_err, f"largest = average = {fmt(max_err, 3)}", color=PALETTE["ink"], dx=0, dy=5, ha="right",
                    va="bottom").set_bbox(BOX)
    else:
        label_point(right, 12.4, max_err, f"largest error {fmt(max_err, 3)}", color=PALETTE["ink"], dx=0, dy=5, ha="right",
                    va="bottom").set_bbox(BOX)
        label_point(right, 12.4, mean_err, f"average {fmt(mean_err, 3)}", color=PALETTE["grey"], dx=0, dy=4, ha="right",
                    va="bottom").set_bbox(BOX)
    right.set_xlabel("Option (tool), constructed")
    right.set_ylabel("Model value minus true value")
    right.set_title("Where the model is wrong", fontsize=11.5)
    pick_text = ("tools " + " and ".join(str(i + 1) for i in picks) + " (tie)") if len(picks) > 1 else f"tool {picks[0] + 1}"
    model_pick = fmt(model[picks[0]], 2)
    true_pick = " or ".join(fmt(true[i], 2) for i in picks)
    metrics = {
        "True gap (Equation 14.3)": fmt(gap, 2),
        "Largest error": fmt(max_err, 3),
        "Average error over 12 tools": fmt(mean_err, 3),
        "Twice the largest error": fmt(2 * max_err, 2),
        "Guarantee 2 x error < gap holds": "yes" if certified else "no",
        "Model's pick": pick_text,
        "Model's value of the pick": model_pick,
        "True value of the pick": true_pick,
    }
    top_true = float(true[BEST_I])
    bias = float(model[picks[0]] - true[picks[0]])
    if len(picks) > 1:
        verdict = ("The model scores tools 5 and 6 equally at 0.75: its own gap is 0, a tie, and 2 x error equals the true gap exactly, "
                   "so the strict test 2 x error < gap fails at equality and the ranking is not preserved.")
    elif picks[0] == BEST_I:
        if certified:
            verdict = (f"The model still picks tool 6, and the guarantee holds: 2 x {fmt(e, 2)} = {fmt(2 * e, 2)} is below the gap {fmt(gap, 2)}.")
        elif pattern == "shared":
            verdict = ("The model still picks tool 6. A shared offset moves every value together, so no ordering changes, however large the offset "
                       "and even though the guarantee is not met.")
        else:
            verdict = (f"The model still picks tool 6, but the guarantee is not met: 2 x {fmt(e, 2)} = {fmt(2 * e, 2)} is not below the gap {fmt(gap, 2)}. "
                       "The test is sufficient, not necessary, so a failed test leaves the ranking undecided rather than wrong.")
    else:
        tail = ("The model was accurate on eleven tools and the search found the twelfth." if pattern == "favorable" else
                "The model is exact on ten tools and wrong on the two the decision turns on; the search climbs to the favorable error at tool 5.")
        verdict = (f"The optimizer now picks tool {picks[0] + 1}, where the model says {model_pick} and the truth is {true_pick}: the score "
                   f"inside the model overstates the real one by {fmt(bias, 2)}. {tail}")
    interpretation = (
        f"Gap = 0.90 - 0.60 = {fmt(gap, 2)}. Twice the largest error = 2 x {fmt(e, 2)} = {fmt(2 * e, 2)}. "
        f"Error pattern: {PATTERNS[pattern]}. Average error = {fmt(float(np.abs(err).sum()), 2)} / 12 = {fmt(mean_err, 3)}, largest error {fmt(max_err, 2)}. "
        f"Model values: tool 5 {fmt(model[RUNNER_I], 2)}, tool 6 {fmt(model[BEST_I], 2)}, tool 12 {fmt(model[LAST_I], 2)}. {verdict}"
    )
    steps = [
        "True values: tool 6 is best at 0.90, tool 5 is next at 0.60, tool 12 is lowest at 0.10.",
        f"Gap by Equation (14.3): 0.90 - 0.60 = {fmt(gap, 2)}.",
        f"Error pattern: {PATTERNS[pattern]}, size {fmt(e, 2)}.",
        f"Model values: tool 5 {fmt(model[RUNNER_I], 2)}, tool 6 {fmt(model[BEST_I], 2)}, tool 12 {fmt(model[LAST_I], 2)}.",
        f"Largest error {fmt(max_err, 2)}; average error {fmt(float(np.abs(err).sum()), 2)} / 12 = {fmt(mean_err, 3)}.",
        f"Guarantee test: 2 x {fmt(e, 2)} = {fmt(2 * e, 2)} against the gap {fmt(gap, 2)}: {'holds' if certified else 'not met'}.",
        f"The optimizer takes the highest model value: {pick_text}, true value {true_pick}.",
    ]
    alt = (f"Left, true values of twelve tools as a navy line with a peak at tool 6 and model values as hollow diamonds; a star marks the "
           f"optimizer's pick, {pick_text}. Right, the error of each tool; largest error {fmt(max_err, 2)}, average {fmt(mean_err, 3)}. "
           f"Pattern: {PATTERNS[pattern]}, size {fmt(e, 2)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: Equation (14.4), the certified horizon

H_MAX = 9  # declared planning cap for this reader


def lhs(reward, eps, h):
    """R x eps x H x (H - 1), exactly."""
    return Fraction(str(reward)) * Fraction(str(eps)) * h * (h - 1)


def certified_horizon(reward, eps, gap, h_max=H_MAX):
    best = None
    for h in range(1, h_max + 1):
        if lhs(reward, eps, h) < Fraction(str(gap)):
            best = h
    return best


SCENARIOS = {
    "r1": (1.0, 0.5),    # R = 1 with the action gap 0.5 of Figure 14.2
    "r1small": (1.0, 0.2),  # R = 1 with the action gap 0.2 of Figure 14.2
    "r10": (10.0, 2.0),  # the chapter's priced twenty-step plan: R = 10, gap about 2
}


def horizon_picture(scenario="r1", error=0.02):
    reward, gap = SCENARIOS[scenario]
    eps = float(error)
    h_star = certified_horizon(reward, eps, gap)
    # The laboratory's finite-horizon bound R x eps x H(H-1)/2, doubled, is the left side of Equation (14.4).
    series = lab_run(eps, eps, rewards=(0.0, reward), discount=0.9, horizon=H_MAX)["series"][1]["y"]
    hs = np.arange(1, H_MAX + 1)
    values = np.array([2 * b for b in series])
    exact = np.array([float(lhs(reward, eps, int(h))) for h in hs])
    if not np.allclose(values, exact, rtol=1e-9, atol=1e-12):
        raise AssertionError("laboratory bound disagrees with R x eps x H(H-1)")
    passed = np.array([lhs(reward, eps, int(h)) < Fraction(str(gap)) for h in hs])
    fig, ax = new_figure(height=4.3)
    first_fail_value = float(lhs(reward, eps, h_star + 1)) if h_star < H_MAX else 0.0
    top = max(3.2 * gap, 1.5 * first_fail_value)  # the first failing horizon is always drawn
    ax.axhline(gap, color=PALETTE["gold"], linewidth=2)
    shown = exact <= 0.70 * top  # keep markers clear of the top edge and the note
    ax.plot(hs[passed & shown], exact[passed & shown], "o", color=PALETTE["teal"], markersize=9)
    ax.plot(hs[~passed & shown], exact[~passed & shown], "X", color=PALETTE["terracotta"], markersize=9)
    ax.plot(hs[shown], exact[shown], color=PALETTE["light"], linewidth=1.2, zorder=0)
    if h_star < H_MAX:
        ax.vlines(h_star + 0.5, 0, 0.70 * top, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    label_point(ax, 0.6, gap, f"action gap {fmt(gap, 1)}", color=PALETTE["gold"], dx=0, dy=6, ha="left").set_bbox(BOX)
    hidden = [int(h) for h in hs[~shown]]
    note = "circle: certified; cross: not certified"
    if h_star < H_MAX:
        note += "\ndashed line: after the last certified horizon"
    if hidden:
        span = f"H = {hidden[0]}" if len(hidden) == 1 else f"H = {hidden[0]} to {hidden[-1]}"
        note += f"\nnot drawn, above the plot: {span}"
    label_point(ax, 0.6, 0.99 * top, note, color=PALETTE["ink"], dx=0, dy=0, ha="left", va="top")
    label_point(ax, h_star, exact[h_star - 1], f"H* = {h_star}", color=PALETTE["teal"], dx=0, dy=-12, ha="center", va="top").set_bbox(BOX)
    ax.set_xlim(0.5, H_MAX + 0.5)
    ax.set_ylim(0, top)
    ax.set_xticks(hs)
    ax.set_xlabel(f"Horizon H, in rewards (planning cap {H_MAX})")
    ax.set_ylabel("R x epsilon x H(H-1), twice the error bound")
    ax.set_title(f"R = {fmt(reward, 0)}, epsilon = {fmt(eps, 2)}, gap = {fmt(gap, 1)}", fontsize=11.5)
    at_star = lhs(reward, eps, h_star)
    twenty = lhs(reward, eps, 20)
    calc = (f"At H = {h_star}: {fmt(reward, 0)} x {fmt(eps, 2)} x {h_star} x {h_star - 1} = {fmt(float(at_star), 2)}, below the gap {fmt(gap, 1)}.")
    if h_star < H_MAX:
        nxt = lhs(reward, eps, h_star + 1)
        equal = nxt == Fraction(str(gap))
        calc += (f" At H = {h_star + 1}: {fmt(reward, 0)} x {fmt(eps, 2)} x {h_star + 1} x {h_star} = {fmt(float(nxt), 2)}, ")
        calc += ("equal to the gap, and the test is strict, so it fails by equality." if equal else f"not below the gap {fmt(gap, 1)}.")
        tail = (f" The certificate covers {h_star} rewards. Its failure at {h_star + 1} is inconclusive: it does not "
                "show that the ranking reverses, only that this guarantee stops.")
        first_fail = str(h_star + 1)
    else:
        tail = f" No horizon up to the declared cap of {H_MAX} fails, so the cap, not the certificate, ends the search."
        first_fail = "none up to the cap"
    plan = (f" A twenty-step plan committed in advance would need {fmt(reward, 0)} x {fmt(eps, 2)} x 20 x 19 = {fmt(float(twenty), 1)} to be "
            f"below the gap {fmt(gap, 1)}, which it is not: plan {h_star}, look, and replan.")
    metrics = {
        "Certified horizon H*": str(h_star),
        "First horizon that fails": first_fail,
        f"R x epsilon x H(H-1) at H* = {h_star}": fmt(float(at_star), 2),
        "Action gap": fmt(gap, 1),
        "Same quantity at a twenty-step plan": fmt(float(twenty), 1),
    }
    steps = [
        f"Inputs: R = {fmt(reward, 0)}, epsilon = {fmt(eps, 2)}, action gap = {fmt(gap, 1)}, planning cap {H_MAX}.",
        f"Test each H: R x epsilon x H(H-1) must be strictly below {fmt(gap, 1)}.",
        f"Largest H that passes: H* = {h_star}, because {fmt(reward, 0)} x {fmt(eps, 2)} x {h_star} x {h_star - 1} = {fmt(float(at_star), 2)}.",
        ("First failure at H = " + first_fail + ": " + f"{fmt(reward, 0)} x {fmt(eps, 2)} x {h_star + 1} x {h_star} = {fmt(float(lhs(reward, eps, h_star + 1)), 2)}.")
        if h_star < H_MAX else f"No failure up to the cap {H_MAX}.",
        f"Twenty steps: {fmt(reward, 0)} x {fmt(eps, 2)} x 20 x 19 = {fmt(float(twenty), 1)}, far above the gap.",
    ]
    if not hidden:
        drawn = f"Points for horizons 1 to {H_MAX} of R x epsilon x H(H-1)"
    else:
        last = hidden[0] - 1
        gone = f"horizon {hidden[0]} lies" if len(hidden) == 1 else f"horizons {hidden[0]} to {hidden[-1]} lie"
        drawn = (f"Points for horizons 1 to {last} of R x epsilon x H(H-1) "
                 f"({gone} above the plotted range and {'is' if len(hidden) == 1 else 'are'} not drawn)")
    alt = (f"{drawn} against a horizontal action-gap line at {fmt(gap, 1)}; "
           f"circles below the line are certified, crosses on or above it are not. The certified horizon is {h_star}.")
    return fig, metrics, calc + tail + plan, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 14,
    "title": "Building a World Inside",
    "subtitle": "An agent that plans inside a learned model scores well only as far as the model's error stays smaller than what the decision can tolerate.",
    "summary": (
        "These four demonstrations follow the chapter. First the reported temperature table, where the score inside a learned model "
        "and the score in the actual environment come apart. Then the finite certificate for a learned transition model: one number "
        "for how wrong the model is and how that error compounds against the actual error, why an optimizer finds the one place a model "
        "is generous and the action gap decides whether a ranking survives, and the number of imagined steps those pieces certify. "
        "Apart from the reported table, all worlds, errors and gaps are constructed teaching values."
    ),
    "ask_skill": {
        "prompt": (
            "Take two states with true rows (0.9, 0.1) and (0.2, 0.8) and model rows (0.88, 0.12) and (0.22, 0.78), rewards 0 and 1, "
            "discount 0.9 and horizon 20. Report the uniform error, the actual finite value error, the finite bound and the "
            "discounted bound, say which bound is tighter, and explain why neither is a certificate for an action ranking."
        )
    },
    "demos": [
        {
            "id": "C14-D01",
            "evidence_kind": "source-reported game scores with a constructed judging comparison",
            "title": "The score inside the model against the score in the world",
            "question": "If you pick the setting that scores best inside the learned model, how does it do in the actual environment?",
            "equations": [EQ_EPS],
            "symbols": (
                "Temperature is the sampling parameter of the imagined world: low values make it cleaner and more predictable, high values "
                "harder. The model score is the controller's score when evaluated in its own learned environment, and the actual score is its "
                "score in the real game. The random policy and the best leaderboard entry are the chapter's reference scores. The table "
                "does not report the transition error epsilon of Equation (14.1), which is the maximum over states and actions of half the "
                "summed difference between the model's and the true next-state probabilities."
            ),
            "prediction": "Rank the five settings by the model column alone. Which wins, and how does it score in the actual environment against the random policy's 210?",
            "prediction_options": [
                "T = 0.10 wins and scores below the random policy in the actual environment",
                "T = 0.10 wins and beats the best leaderboard entry in the actual environment",
                "T = 1.15 wins and scores 1092 in the actual environment",
            ],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "At T = 0.10 the model reports 2086 and the actual score is 193, which is 17 below the random policy's 210.",
                "incorrect": "The model column is largest at T = 0.10 (2086), and that setting scores only 193 in the actual environment, below the random policy's 210. Pick the model column in the judge control.",
            },
            "misconception": {
                "title": "A higher score inside the model means a better agent",
                "text": (
                    "The chapter notes that an evaluation run only in the dream would have reported 2086 at the low setting, ranked it first, "
                    "and been confidently wrong. Many agent evaluations have one column."
                ),
            },
            "scope_note": {
                "text": (
                    "The anchor is a preprint reporting on its authors' own systems in one game, and the temperature that worked there is "
                    "not a value to copy."
                ),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "The table has two columns because the researchers had two environments. Over the first four rows the columns run in opposite "
                "directions, so the setting that flatters the model most is the least useful in the world. Judging by the model column alone "
                "cannot show this; only the second column can. The scores do not supply the transition error epsilon or any action gap, so "
                "they do not give a certified horizon."
            ),
            "application": (
                "When a system proposes an action, predicts its outcome and scores itself on the prediction, it is reading the left column. "
                "Hold out some real outcomes and keep the second column, however small, and compare the two."
            ),
            "assumptions": (
                "The scores are the chapter's reported numbers for one game setup and one training and evaluation procedure, each with "
                "its own variability (spreads were reported for 0.10 and 1.15 here). They show that the two evaluations can come apart, "
                "not a general temperature rule and not a measure of epsilon."
            ),
            "check": "At T = 1.30, what is the model score minus the actual score, and which column is higher?",
            "answer": "732 - 753 = -21, so the actual score is higher by 21. The columns can also run the other way.",
            "provenance": "Constructed example (reported values in a constructed comparison): the scores are copied from the chapter's temperature table (reported by the cited paper for one game setup); the judging rule and the comparison are defined for this reader.",
            "source_section": "The knob the authors added, and what it bought",
            "source_anchor": "the-knob-the-authors-added-and-what-it-bought",
            "controls": [
                {"key": "temperature", "label": "Setting to inspect (temperature)", "values": [0.10, 1.00, 1.15, 1.30], "default": 0.10,
                 "value_labels": ["0.10", "1.00", "1.15", "1.30"]},
                {"key": "judge", "label": "Pick the winner by", "values": ["dream", "real"], "default": "dream",
                 "value_labels": ["The score inside the model", "The score in the actual environment"]},
            ],
            "function": "dream_real_picture",
        },
        {
            "id": "C14-D02",
            "title": "One step of error, compounded, against the actual error",
            "question": "How large can the value error become when a small one-step error compounds, and how large is it in a constructed model?",
            "equations": [EQ_EPS, EQ_BOUND],
            "symbols": (
                "P(x' | x, a) is the true probability of moving to state x' from state x after action a; the hat marks the model's estimate. "
                "Epsilon is the largest row error, half the summed absolute difference. V(x) is the true value of state x under a fixed behaviour "
                "and V-hat(x) the value the model computes, gamma the discount factor and R the largest immediate reward. The actual error is the "
                "largest gap between the two value recurrences after H rewards, and the finite bound R x epsilon x H(H-1)/2 is the chapter's "
                "finite-horizon envelope. The value scale R/(1-gamma) is the most any run could collect."
            ),
            "prediction": "In the default case (error 0.02, R = 1) raise gamma to 0.99. About how large is the discounted bound?",
            "prediction_options": ["About 2", "About 20", "About 200"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "0.99 x 0.02 x 1 / (1 - 0.99)^2 = 0.0198 / 0.0001 = 198, about 200, against a largest possible value of 100.",
                "incorrect": "The denominator (1 - 0.99)^2 is 0.0001, so 0.99 x 0.02 / 0.0001 = 198, about 200. Select gamma 0.99 in the default case.",
            },
            "misconception": {
                "title": "Reading the bound as the error the model actually makes",
                "text": (
                    "The chapter says the bound is worst case and often loose, and that a model with a large error may perform far better than "
                    "it permits. At horizon 20 the finite bound is 3.8 while the actual error stays small."
                ),
            },
            "scope_note": {
                "text": (
                    "The bound in Equation (14.2) is worst case and often loose, and a model with a large error may perform far better than "
                    "it permits."
                ),
                "source_section": "What this does not settle",
            },
            "stepper": "discount",
            "explanation": (
                "The bound multiplies gamma, epsilon and R, then divides by (1 - gamma) squared: one factor of 1/(1-gamma) counts the steps that "
                "matter and the second counts that a mistake at each step displaces everything after it. The finite bound grows with H(H-1) "
                "instead. Each bound holds under its own assumptions, and the actual error from the two recurrences stays under "
                "both. Raising gamma shrinks nothing in the finite bound but inflates the discounted one."
            ),
            "application": (
                "Before trusting a long imagined rollout, divide the bound by the largest possible value. If the share is near or above 1, "
                "the guarantee has nothing to say. If the model cannot be improved, consult the world more often."
            ),
            "assumptions": (
                "The bound needs a fixed behaviour, the same expected immediate reward in model and world, rewards in [0, R], and error at most "
                "epsilon for every state and action that behaviour reaches. The kernels are the laboratory's constructed two-state defaults, so "
                "the actual error is that of one small model, not a general rate. A single number can also hide where the model is bad."
            ),
            "check": "With gamma = 0.8, epsilon = 0.05 and R = 1, what is the discounted bound, and what is the largest possible value?",
            "answer": "Bound = 0.8 x 0.05 / (1 - 0.8)^2 = 0.04 / 0.04 = 1.0. The largest possible value is 1 / 0.2 = 5, so the bound is a fifth of the range.",
            "provenance": "Constructed example: the laboratory's default, changed and transfer cases (kernels (0.90, 0.10), (0.20, 0.80) and model rows shifted by 0.02, horizons 5 and 20, identical kernels with rewards 1 and 2) and the chapter's 0.01 illustration, all computed with the laboratory's transition-model function.",
            "source_section": "What one step of error becomes",
            "source_anchor": "what-one-step-of-error-becomes",
            "controls": [
                {"key": "case", "label": "Case", "values": ["default", "changed", "transfer", "percent"], "default": "default",
                 "value_labels": ["Default: error 0.02, horizon 5", "Changed: horizon 20", "Transfer: identical kernels, rewards 1, 2, horizon 4",
                                  "Chapter illustration: error 0.01, horizon 20"]},
                {"key": "discount", "label": "Discount factor gamma", "values": [0.5, 0.9, 0.99], "default": 0.9},
            ],
            "function": "bound_picture",
        },
        {
            "id": "C14-D03",
            "title": "The optimizer finds where the model is generous, and the gap decides",
            "question": "A model can be wrong about every action value and still choose correctly, or be right about eleven tools and choose the twelfth. What decides which?",
            "equations": [EQ_GAP],
            "symbols": (
                "Q(x, a) is the true value of taking action a at state x and then following the fixed behaviour; here the twelve options are tools "
                "with constructed values. Delta is the gap between the best action's value and the runner-up's (a* is a best action; if several "
                "actions tie for the maximum, the gap is defined as zero). The model's value of each action is off by the chosen error, and the "
                "chapter's ranking guarantee is that the model keeps the true ranking whenever twice that error is smaller than the gap: 2 delta < Delta. "
                "The largest error is the maximum over options, the average is the mean."
            ),
            "prediction": "Use the adversarial pattern with error 0.15, where twice the error equals the gap 0.30. What does the model do with tools 5 and 6?",
            "prediction_options": [
                "It still picks tool 6",
                "It scores tools 5 and 6 equally, a tie",
                "It picks tool 5",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Tool 6 falls to 0.90 - 0.15 = 0.75 and tool 5 rises to 0.60 + 0.15 = 0.75: an exact tie, so the strict test 2 x error < gap cannot certify the ranking.",
                "incorrect": "Marking the best down and the runner-up up by 0.15 gives 0.75 for both, an exact tie. Set the adversarial pattern and the error 0.15.",
            },
            "misconception": {
                "title": "Judging a planning model by its average accuracy",
                "text": (
                    "The chapter says the useful question is never how accurate the model is, but whether its error is small relative to the gaps in "
                    "the decision it serves, and that the diagnostic is whether errors are correlated across the options it ranks, not the average."
                ),
            },
            "scope_note": {
                "text": (
                    "This schematic explains the selection mechanism rather than supplying a measured error landscape."
                ),
                "source_section": "This schematic explains the selection mechanism rather than supplying a measured error landscape.",
            },
            "explanation": (
                "A shared offset moves every value together, so the ordering is untouched however large the offset is. One favorable error on a "
                "tool that is truly poor changes the choice only if it lifts that tool above the best, but when it does, the average error is "
                "tiny (the error divided by twelve) while the largest is the whole error: this is why Equation (14.1) is a maximum and not an "
                "average. An adversarial error marks the best down and the runner-up up, so the two meet when twice the error equals the gap."
            ),
            "application": (
                "Judge a planning model against the decision it serves, not against a single accuracy figure. Ask how large the gap is "
                "between the best option and the next one, compare twice the value error to it in the same units, and check whether the "
                "errors are concentrated on options the optimizer will rank."
            ),
            "assumptions": (
                "Twelve options with constructed values, a uniform bound on the action-value error, and three hand-made error patterns. The "
                "chapter adds that this bound is an extra assumption: Equation (14.2) bounds state values and does not supply it. The test "
                "2 x error < gap is sufficient, not necessary, so a failed test leaves the ranking undecided rather than wrong."
            ),
            "check": "True values 0.90 and 0.60, adversarial error 0.12. Which action does the model pick, and does the guarantee hold?",
            "answer": "Model values: 0.90 - 0.12 = 0.78 and 0.60 + 0.12 = 0.72, so the model still picks tool 6. Twice the error is 0.24, below the gap 0.30, so the guarantee holds.",
            "provenance": "Constructed example: twelve option values defined for this reader (best 0.90, runner-up 0.60), with error patterns that illustrate the chapter's ranking argument and its eleven-right, one-wrong tool example.",
            "source_section": "The number that actually matters",
            "source_anchor": "the-number-that-actually-matters",
            "controls": [
                {"key": "pattern", "label": "Error pattern", "values": ["shared", "favorable", "adversarial"], "default": "shared",
                 "value_labels": ["Shared offset on every tool", "One favorable error on tool 12 only", "Adversarial: best down, runner-up up"]},
                {"key": "error", "label": "Size of the error", "values": [0.05, 0.15, 0.3, 0.9], "default": 0.05},
            ],
            "function": "landscape_picture",
        },
        {
            "id": "C14-D04",
            "title": "How many imagined steps are certified",
            "question": "Given the model error, the reward range and the action gap, how many steps ahead can the certificate vouch for?",
            "equations": [EQ_HSTAR],
            "symbols": (
                "H is the number of rewards the agent plans over, H-max the declared planning cap (9 here), and H-star the largest H that passes. "
                "R is the largest immediate reward, epsilon the uniform one-step error from Equation (14.1), and Delta the lower bound on the action "
                "gap from Equation (14.3). The left side R x epsilon x H(H-1) is twice the finite-horizon action-value error bound R x epsilon x H(H-1)/2."
            ),
            "prediction": "With R = 10 and a gap of 2, cut the error by 8 times, from 0.08 to 0.01. Does the certified horizon grow by 8 times, or by far less?",
            "prediction_options": ["It grows from 2 to 4", "It grows from 2 to 16", "It stays at 2"],
            "prediction_answer": 0,
            "prediction_feedback": {
                "correct": "At 0.08, 10 x 0.08 x 2 x 1 = 1.6 passes and H = 3 gives 4.8; at 0.01, H = 4 gives 10 x 0.01 x 12 = 1.2 and H = 5 fails by equality at 2.0.",
                "incorrect": "H(H-1) grows like H squared, so the horizon scales roughly with the square root of gap over R x epsilon: 0.08 certifies 2 rewards and 0.01 certifies 4. Choose scenario R = 10 and step the error down.",
            },
            "misconception": {
                "title": "A failed certificate proves the ranking reverses",
                "text": (
                    "The chapter says the certificate's failure at six is inconclusive, not evidence that the model must make a wrong decision "
                    "there. It only says this sufficient guarantee stops."
                ),
            },
            "scope_note": {
                "text": (
                    "The horizon arithmetic is constructed for teaching. How to bound what a system could achieve given a model, rather than "
                    "what it does achieve, waits for Chapters 24 and 26."
                ),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "Twice the error bound grows with H times H-1, so each extra step costs more than the last. The certificate keeps the largest H "
                "for which that quantity is still strictly below the gap. Because H(H-1) grows like H squared, the horizon scales roughly with "
                "the square root of gap over R x epsilon: for long horizons, cutting the error by 8 times raises it by about 2.8 times, not 8. "
                "A twenty-step plan committed in advance fails the test by a wide margin, which is why the countermeasure is to plan a few steps, look, and replan."
            ),
            "application": (
                "Use the certified horizon to set how many steps an agent commits to before it observes the world again. Plan that many, "
                "execute a few, look, and replan, rather than emitting a long plan against an error nobody measured."
            ),
            "assumptions": (
                "A finite covered domain, equal expected immediate rewards in model and world, the same initial state and fixed behaviour, "
                "uniform error epsilon, zero terminal continuation and a declared gap. The R = 10 case uses the chapter's priced plan, where "
                "a logged prediction miss rate is declared a conservative proxy for epsilon, which is not the same thing. A failed test is "
                "inconclusive, not proof of a wrong decision, and the inputs are usually not measured."
            ),
            "check": "With R = 1, epsilon = 0.04 and a gap of 0.5, what is the certified horizon?",
            "answer": "R x epsilon x H(H-1) = 0.04 x H(H-1). At H = 4 it is 0.04 x 12 = 0.48, below 0.5. At H = 5 it is 0.04 x 20 = 0.80, which is not. H-star = 4.",
            "provenance": "Constructed example: the chapter's Figure 14.2 gaps (R = 1, epsilon 0.02, gaps 0.2 and 0.5) and its priced twenty-step plan (R = 10, gap 2, epsilon 0.08 and 0.01); the other error values are defined for this reader, and each curve is checked against the laboratory's finite-horizon bound.",
            "source_section": "How many steps a model is good for",
            "source_anchor": "how-many-steps-a-model-is-good-for",
            "controls": [
                {"key": "scenario", "label": "Reward range and action gap", "values": ["r1", "r1small", "r10"], "default": "r1",
                 "value_labels": ["R = 1, gap 0.5 (Figure 14.2)", "R = 1, gap 0.2 (Figure 14.2)", "R = 10, gap 2 (priced plan)"]},
                {"key": "error", "label": "One-step error epsilon", "values": [0.01, 0.02, 0.04, 0.08], "default": 0.02},
            ],
            "function": "horizon_picture",
        },
    ],
}

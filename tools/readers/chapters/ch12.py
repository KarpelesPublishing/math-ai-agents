"""Chapter 12 reader: Credit for Consequences.

Four demonstrations built on Equations (12.1) to (12.4).

Scenarios (all constructed teaching values):
  D01 one pass, two or three update rules, repeated pass by pass on four
      runs: the book's four-action trajectory, and the laboratory's default
      (draft, review, done), changed (truncated, terminal = false) and transfer
      (a, b, c, d) cases; every value comes from the laboratory's own
      trajectory-credit function (math_ai_agents.chapters.ch12.evaluate);
  D02 the book's eight-episode construction (batch form, checked against the
      closed form);
  D03 Equation (12.4)'s weights for the book's eight-transition case, beside the
      random-walk experiment of Figure 12.2 (100 constructed training sets of
      10 seeded walks, scored against the exactly known values 1/6 to 5/6);
  D04 the book's first-search TD error (-0.02, estimates 0.20 and 0.50 or 0.10)
      and its finish-or-inspect example whose learned continuation value
      switches the chosen action (0.6 against 0.4, then 0.8).
"""
import math
from functools import lru_cache

import numpy as np

from math_ai_agents.chapters.ch12 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

EQ_OUTCOME = r"\hat V_{t+1}(x_t) = \hat V_t(x_t) + \alpha\big[\operatorname{Ret}_t - \hat V_t(x_t)\big]."
EQ_DELTA = r"\delta_t = r_t + \gamma\,\hat V_t(x_{t+1}) - \hat V_t(x_t)."
EQ_TD = r"\hat V_{t+1}(x_t) = \hat V_t(x_t) + \alpha\,\delta_t."
EQ_LAMBDA = (
    r"\operatorname{Ret}^{\lambda}_t = (1-\lambda)\sum_{k=1}^{N-t-1}\lambda^{\,k-1}"
    r"\Big[\textstyle\sum_{j=0}^{k-1}\gamma^{\,j} r_{t+j} + \gamma^{\,k}\hat V_t(x_{t+k})\Big] "
    r"+ \lambda^{N-t-1}\operatorname{Ret}_t."
)

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
SCOPE = "What this does not settle"


def num(x, digits=4):
    """A number without trailing zeros for written sums (0.505, 0.5, 1)."""
    text = f"{float(x):.{digits}f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def sn(x):
    """Written number, negatives in parentheses."""
    t = num(x)
    return f"({t})" if t.startswith("-") else t


# Demonstration 1: four runs, pass by pass

CASES = {
    "book": {
        "name": "four-action run", "states": ["state 1", "state 2", "state 3", "state 4", "end"], "rewards": [0, 0, 0, 1],
        "discount": 1, "alpha": 0.1, "lam": 0, "terminal": True,
        "values": {"state 1": 0.5, "state 2": 0.5, "state 3": 0.5, "state 4": 0.5, "end": 0.0},
    },
    "default": {
        "name": "draft, review, done run", "states": ["draft", "review", "done"], "rewards": [0, 1],
        "discount": 1, "alpha": 0.5, "lam": 0.8, "terminal": True,
        "values": {"draft": 0, "review": 0, "done": 0},
    },
    "changed": {
        "name": "truncated draft, review, done run", "states": ["draft", "review", "done"], "rewards": [0, 1],
        "discount": 1, "alpha": 0.5, "lam": 0.8, "terminal": False,
        "values": {"draft": 0, "review": 0, "done": 2},
    },
    "transfer": {
        "name": "a, b, c, d run", "states": ["a", "b", "c", "d"], "rewards": [1, 0, 2],
        "discount": 0.9, "alpha": 0.2, "lam": 0, "terminal": True,
        "values": {"a": 0, "b": 1, "c": 0, "d": 0},
    },
}
EST_KEYS = {"outcome": "monte_carlo_values", "onestep": "td_zero_values", "trace": "td_lambda_values"}


def lab_pass(spec, estimator, values):
    out = evaluate({
        "states": spec["states"], "rewards": spec["rewards"], "discount": spec["discount"],
        "learning_rate": spec["alpha"], "lambda": spec["lam"], "terminal": spec["terminal"], "values": values,
    })
    return dict(out["metrics"][EST_KEYS[estimator]]), list(out["metrics"]["returns"]), list(out["series"][1]["y"])


def passes(case, n):
    """Values of each estimator after 1..n passes (each estimator iterates its own values)."""
    spec = CASES[case]
    estimators = ["outcome", "onestep"] + (["trace"] if spec["lam"] > 0 else [])
    vals = {e: dict(spec["values"]) for e in estimators}
    history = []
    for _ in range(n):
        before = {e: dict(v) for e, v in vals.items()}
        for e in estimators:
            vals[e], returns, _ = lab_pass(spec, e, vals[e])
        history.append((before, {e: dict(v) for e, v in vals.items()}))
    return estimators, history


def hand_lines(spec, before):
    """Written arithmetic of one pass for each rule, rebuilt without the laboratory (and checked against it)."""
    states, rewards, g, alpha, lam = spec["states"], spec["rewards"], spec["discount"], spec["alpha"], spec["lam"]
    n = len(rewards)
    boot = 0.0 if spec["terminal"] else spec["values"][states[-1]]
    returns = [0.0] * n
    ret = boot
    for t in range(n - 1, -1, -1):
        ret = rewards[t] + g * ret
        returns[t] = ret
    lines = {"outcome": [], "onestep": [], "trace": []}
    new = {"outcome": {}, "onestep": {}, "trace": {}}
    mc = dict(before["outcome"])
    for t in range(n):
        s = states[t]
        old = mc[s]
        mc[s] = old + alpha * (returns[t] - old)
        lines["outcome"].append(f"{s}: return {num(returns[t])}, {num(old)} + {num(alpha)} x ({num(returns[t])} - {num(old)}) = {num(mc[s])}")
    new["outcome"] = mc
    td = dict(before["onestep"])
    for t in range(n):
        s, nx = states[t], states[t + 1]
        nxt = 0.0 if spec["terminal"] and t == n - 1 else td[nx]
        delta = rewards[t] + g * nxt - td[s]
        old = td[s]
        td[s] = old + alpha * delta
        lines["onestep"].append(
            f"{s}: delta = {num(rewards[t])} + {num(g)} x {num(nxt)} - {num(old)} = {num(delta)}, so {num(old)} + {num(alpha)} x {sn(delta)} = {num(td[s])}")
    new["onestep"] = td
    if "trace" in before:
        tr = dict(before["trace"])
        elig = {k: 0.0 for k in tr}
        for t in range(n):
            s, nx = states[t], states[t + 1]
            nxt = 0.0 if spec["terminal"] and t == n - 1 else tr[nx]
            vs = tr[s]
            err = rewards[t] + g * nxt - vs
            elig[s] += 1
            moves = []
            for k in sorted(tr, key=lambda s: states.index(s) if s in states else len(states)):  # run order; the lab dict order follows set() hashing
                if elig[k]:
                    old = tr[k]
                    tr[k] = old + alpha * err * elig[k]
                    moves.append(f"{k} {num(old)} + {num(alpha)} x {sn(err)} x {num(elig[k])} = {num(tr[k])}")
                    elig[k] *= g * lam
            lines["trace"].append(f"step {t + 1}: error = {num(rewards[t])} + {num(g)} x {num(nxt)} - {num(vs)} = {num(err)}; " + "; ".join(moves))
        new["trace"] = tr
    return lines, new


def est_text(x, start, strip=True):
    """Three decimals, or four when a real move would otherwise print as no move (0.5005 shown as 0.500)."""
    x, start = float(x), float(start)
    if abs(x - start) > 1e-12 and round(x, 3) == round(start, 3):
        return f"{x:.4f}"
    return num(x, 3) if strip else fmt(x, 3)


def trajectory_picture(case="book", passes_done=1):
    spec = CASES[case]
    n_pass = int(passes_done)
    estimators, history = passes(case, n_pass)
    before, after = history[-1]
    lines, mine = hand_lines(spec, before)
    for e in estimators:  # the hand arithmetic must agree with the laboratory
        for s in spec["states"][:-1]:
            if not math.isclose(mine[e][s], after[e][s], abs_tol=1e-9):
                raise AssertionError(f"hand arithmetic disagrees with the laboratory: {case} {e} {s}")
    shown = spec["states"][:-1]
    labels = {"outcome": "outcome rule", "onestep": "one-step rule", "trace": f"trace rule (lambda {num(spec['lam'])})"}
    colors = {"outcome": PALETTE["navy"], "onestep": PALETTE["teal"], "trace": PALETTE["gold"]}
    hatches = {"outcome": "///", "onestep": "", "trace": ".."}
    k = len(estimators)
    width = 0.8 / k
    x = np.arange(len(shown))
    fig, ax = new_figure(height=4.4)
    changes = []
    for j, e in enumerate(estimators):
        offs = x + (j - (k - 1) / 2) * width
        ch = [after[e][s] - spec["values"][s] for s in shown]
        changes += ch
        ax.bar(offs, ch, width=width * 0.92, color="white" if e == "outcome" else colors[e], edgecolor=colors[e],
               hatch=hatches[e], linewidth=1.3)
        for xo, c, s in zip(offs, ch, shown):
            va = "bottom" if c >= 0 else "top"
            ax.annotate(est_text(after[e][s], spec['values'][s], strip=False), (xo, c), xytext=(0, 3 if c >= 0 else -3), textcoords="offset points", ha="center",
                        va=va, fontsize=10, color=colors[e])
    ax.axhline(0, color=PALETTE["ink"], linewidth=1)
    lo, hi = min(changes + [0]), max(changes + [0])
    span = max(hi - lo, 0.05)
    ax.set_ylim(lo - 0.25 * span if lo < 0 else -0.05 * span, hi + 0.35 * span)
    ax.set_xticks(x, [f"{s}\nstart {num(spec['values'][s])}" for s in shown])
    ax.set_xlim(-0.6, len(shown) - 0.4)
    ax.set_xlabel("State on the run (labels show the new estimate)")
    ax.set_ylabel("Change in the estimate since the start\n(bar labels give the new estimate)")
    ax.grid(axis="x", alpha=0)
    for e in estimators:
        ax.bar([20], [0], color="white" if e == "outcome" else colors[e], edgecolor=colors[e], hatch=hatches[e], label=labels[e])
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=k, frameon=False, fontsize=10)
    ax.set_title(f"The {spec['name']}, after {n_pass} {'pass' if n_pass == 1 else 'passes'}, step size {num(spec['alpha'])}", fontsize=11.5)

    def moved(e):
        return sum(1 for s in shown if abs(after[e][s] - spec["values"][s]) > 1e-12)
    metrics = {f"{labels[e].capitalize()}, states in order": ", ".join(est_text(after[e][s], spec["values"][s], strip=False) for s in shown) for e in estimators}
    metrics["States moved (outcome / one-step)"] = f"{moved('outcome')} / {moved('onestep')}"
    first_moved = [s for s in shown if abs(after["onestep"][s] - before["onestep"][s]) > 1e-12]
    td_lines = "; ".join(lines["onestep"])
    verdict = (f"After this pass the outcome rule has moved {moved('outcome')} of {len(shown)} estimates and the one-step rule {moved('onestep')}. "
               + ("The one-step rule has not yet moved any estimate. " if not moved("onestep") else "")
               + "Neither movement says which action deserved the result: each is a repair of a prediction of future return.")
    extra = ""
    if not spec["terminal"]:
        extra = (" The run is truncated, not terminated: the last state keeps its supplied estimate " + num(spec["values"][spec["states"][-1]])
                 + " as the continuation, so treating it as terminal (continuation 0) would erase that estimate.")
    if spec["lam"] == 0 and case == "transfer":
        extra += " With lambda = 0 the trace rule is the one-step rule."
    if case == "book" and n_pass > 1:
        extra += (" The raised estimate of state 4 reaches state 3 on the second pass, state 2 on the third and state 1 on the fourth: the one-step "
                  "rule moves terminal information back one state per pass.")
    interpretation = (
        f"Pass {n_pass} of the {spec['name']}. Outcome rule: {lines['outcome'][0]}. One-step rule: {td_lines}. {verdict}{extra}"
    )
    n_out = len(lines["outcome"]) if ("trace" not in estimators and len(lines["outcome"]) + len(lines["onestep"]) <= 8) else 3
    steps = [f"Outcome rule, {ln}." for ln in lines["outcome"][:n_out]]
    steps += [f"One-step rule, {ln}." for ln in lines["onestep"]][: max(0, 8 - len(steps) - (len(lines["trace"]) if "trace" in estimators else 0))]
    if "trace" in estimators:
        steps += [f"Trace rule, {ln}." for ln in lines["trace"]]
    steps = [s if len(s) <= 238 else s[:235] + "..." for s in steps][:8]
    alt = (f"Grouped bars for each state of the {spec['name']} after {n_pass} {'pass' if n_pass == 1 else 'passes'}: the change in the estimate under the "
           f"{' and '.join(labels[e] for e in estimators)}. The outcome rule moved {moved('outcome')} of {len(shown)} states and the one-step rule {moved('onestep')}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: the eight episodes

def batch_values(ones_in_b_only, a_final):
    """Batch form of both rules on the eight episodes; returns (A, B) for each rule.

    Episode 1: A then B, no reward, then B ends with reward a_final. Seven more
    episodes start in B and end at once with rewards: ones_in_b_only ones, then zeros.
    """
    b_rewards = [float(a_final)] + [1.0] * ones_in_b_only + [0.0] * (7 - ones_in_b_only)
    # Outcome rule: each state moves toward the mean of the returns that followed it.
    out_b = sum(b_rewards) / 8
    out_a = float(a_final)
    # One-step rule: repeated batch presentation of every transition, small step size.
    va = vb = 0.5
    step = 0.05
    for _ in range(6000):
        da = vb - va                            # the one A to B transition: reward 0
        db = sum(r - vb for r in b_rewards) / 8  # B's eight transitions into the end (value 0)
        va, vb = va + step * da, vb + step * db
    return (out_a, out_b), (va, vb)


def eight_episodes_picture(ones_in_b_only=6, a_final=0):
    k, a = int(ones_in_b_only), int(a_final)
    (out_a, out_b), (td_a, td_b) = batch_values(k, a)
    b_true = (k + a) / 8
    if not (math.isclose(td_b, b_true, abs_tol=1e-6) and math.isclose(td_a, b_true, abs_tol=1e-6)
            and math.isclose(out_b, b_true, abs_tol=1e-12)):
        raise AssertionError("batch result disagrees with the closed form")
    td_a, td_b = b_true, b_true  # exact limits (the iteration above confirms them)
    gap = abs(td_a - out_a)
    fig, ax = new_figure(height=4.2)
    x = np.array([0, 1])
    ax.bar(x - 0.2, [out_a, out_b], width=0.38, color="white", edgecolor=PALETTE["navy"], hatch="///", linewidth=1.3)
    ax.bar(x + 0.2, [td_a, td_b], width=0.38, color=PALETTE["teal"])
    for xi, o, t in zip(x, [out_a, out_b], [td_a, td_b]):
        ax.text(xi - 0.2, o + 0.02, fmt(o, 3), ha="center", va="bottom", fontsize=10.5, color=PALETTE["navy"])
        ax.text(xi + 0.2, t + 0.02, fmt(t, 3), ha="center", va="bottom", fontsize=10.5, color=PALETTE["teal"])
    ax.set_xticks(x, ["Value of A (seen once)", "Value of B (seen 8 times)"])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, 1.25)
    ax.text(-0.55, 1.2, "hatched = outcome rule; solid = one-step rule", ha="left", va="top", fontsize=10.5, color=PALETTE["ink"]).set_bbox(BOX)
    ax.set_xlabel("State")
    ax.set_ylabel("Value each rule settles on")
    ax.set_title(f"Seven B-only episodes with {k} paying 1; the A episode ends with {a}", fontsize=11.5)
    metrics = {
        "Value of B (both rules)": fmt(b_true, 3),
        "Value of A, outcome rule": fmt(out_a, 3),
        "Value of A, one-step rule": fmt(td_a, 3),
        "Disagreement about A": fmt(gap, 3),
    }
    if gap < 1e-12:
        verdict = "The one episode that passed through A happened to end at B's average, so the two rules agree about A."
    else:
        verdict = (f"The outcome rule fits the single A episode exactly (error 0) but is {fmt(gap, 3)} away from B's value; "
                   "the one-step rule gives A the value of its successor B, using the seven episodes that never contained A.")
    interpretation = (
        f"B's returns are {k} + {a} ones in 8 visits, so B = ({k} + {a}) / 8 = {fmt(b_true, 3)} under either rule. "
        f"The outcome rule gives A the one return it saw: {a}. The one-step rule gives A = 0 + B = {fmt(td_a, 3)}. "
        f"Disagreement about A = |{fmt(td_a, 3)} - {fmt(out_a, 3)}| = {fmt(gap, 3)}. {verdict}"
    )
    steps = [
        f"B is visited 8 times; its returns hold {k} + {a} ones, so B = ({k} + {a}) / 8 = {fmt(b_true, 3)}.",
        f"A is visited once and the return that followed was {a}, so the outcome rule sets A = {a}.",
        f"Every A transition goes to B with reward 0, so the one-step rule sets A = 0 + B = {fmt(td_a, 3)}.",
        f"Disagreement = |{fmt(td_a, 3)} - {fmt(out_a, 3)}| = {fmt(gap, 3)}.",
    ]
    alt = (f"Two groups of bars. For state A, seen once, the outcome rule gives {fmt(out_a, 2)} and the one-step rule {fmt(td_a, 2)}. "
           f"For state B, seen eight times, both rules give {fmt(b_true, 2)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: the lambda dial and the random-walk experiment

def lambda_weights(lam, remaining):
    """Equation (12.4) weights: (1 - lam) lam^(k-1) for k = 1..n-1, then lam^(n-1) on the full return."""
    n = int(remaining)
    w = [(1 - lam) * lam ** (k - 1) for k in range(1, n)]
    w.append(lam ** (n - 1))
    return w


LAMBDAS = [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]
TRUE_VALUES = np.arange(1, 6) / 6  # right-terminal probabilities of B..F
ALPHAS = [round(0.05 * i, 2) for i in range(0, 13)]
N_SETS, N_WALKS, RW_SEED = 100, 10, 0


def random_walk(rng):
    """One walk on the chain A..G from D: interior state numbers 1..5 (B..F) and the outcome 0 or 1."""
    s, seq = 3, []
    while True:
        seq.append(s)
        s += 1 if rng.random() < 0.5 else -1
        if s == 0:
            return seq, 0.0
        if s == 6:
            return seq, 1.0


def normal_equations(train, lam):
    """Offline linear system of the lambda rule: the batch limit solves A w = b over the states that were visited."""
    A = np.zeros((5, 5))
    b = np.zeros(5)
    for seq, z in train:
        e = np.zeros(5)
        m = len(seq)
        for t, s in enumerate(seq):
            e = lam * e
            e[s - 1] += 1
            A[:, s - 1] += e
            if t < m - 1:
                A[:, seq[t + 1] - 1] -= e
            else:
                b += e * z
    return A, b


def repeated_weights(train, lam):
    A, b = normal_equations(train, lam)
    visited = sorted({s - 1 for seq, _ in train for s in seq})
    w = np.full(5, 0.5)  # a state that no walk visited keeps its starting value
    w[visited] = np.linalg.solve(A[np.ix_(visited, visited)], b[visited])
    return w


def single_presentation_weights(train, lam, alpha):
    w = np.full(5, 0.5)
    for seq, z in train:
        e = np.zeros(5)
        dw = np.zeros(5)
        m = len(seq)
        for t, s in enumerate(seq):
            e = lam * e
            e[s - 1] += 1
            nxt = w[seq[t + 1] - 1] if t < m - 1 else z
            dw += (nxt - w[s - 1]) * e
        w = w + alpha * dw
    return w


def rms(w):
    return float(np.sqrt(np.mean((w - TRUE_VALUES) ** 2)))


def training_error(train, w):
    return float(np.sqrt(np.mean([(w[s - 1] - z) ** 2 for seq, z in train for s in seq])))


@lru_cache(maxsize=1)
def random_walk_results():
    rng = np.random.default_rng(RW_SEED)
    sets = [[random_walk(rng) for _ in range(N_WALKS)] for _ in range(N_SETS)]
    out = {"repeated": {}, "once": {}}
    for lam in LAMBDAS:
        ws = [repeated_weights(tr, lam) for tr in sets]
        errs = [rms(w) for w in ws]
        out["repeated"][lam] = {
            "error": float(np.mean(errs)), "se": float(np.std(errs) / math.sqrt(N_SETS)),
            "train": float(np.mean([training_error(tr, w) for tr, w in zip(sets, ws)])),
        }
        best = None
        for alpha in ALPHAS:
            errs = [rms(single_presentation_weights(tr, lam, alpha)) for tr in sets]
            m = float(np.mean(errs))
            if best is None or m < best[0] - 1e-15:
                best = (m, alpha, float(np.std(errs) / math.sqrt(N_SETS)))
        out["once"][lam] = {"error": best[0], "alpha": best[1], "se": best[2]}
    return out


def lambda_picture(lam=0.9, protocol="repeated"):
    lam = float(lam)
    n = 8
    w = lambda_weights(lam, n)
    total = sum(w)
    fig, (left, right) = new_figure(ncols=2, height=4.4)
    ks = np.arange(1, n + 1)
    left.bar(ks[:-1], w[:-1], width=0.62, color=PALETTE["teal"])
    left.bar([n], [w[-1]], width=0.62, color="white", edgecolor=PALETTE["terracotta"], hatch="///", linewidth=1.3)
    for k, v in zip(ks, w):
        if v >= 0.0005 or k == n:  # the full-return bar is always labelled, even when its weight is tiny or zero
            text = "0" if v == 0 else ("<0.001" if v < 0.0005 else fmt(v, 3))
            left.text(k, v + 0.015, text, ha="center", va="bottom", fontsize=10,
                      color=PALETTE["terracotta"] if k == n else PALETTE["teal"])
    left.set_xticks(ks, [str(k) if k < n else f"{k}\nfull" for k in ks])
    left.set_xlim(0.4, n + 0.6)
    left.set_ylim(0, 1.12)
    left.set_xlabel("Target k (k-step lookahead; last bar: complete return)")
    left.set_ylabel("Weight in the lambda target")
    left.set_title(f"Weights, lambda = {fmt(lam, 1)}, {n} transitions left", fontsize=11.5)

    res = random_walk_results()[protocol]
    errs = [res[l]["error"] for l in LAMBDAS]
    right.plot(LAMBDAS, errs, color=PALETTE["teal"], marker="o", linewidth=1.8, label="error against the true values")
    if protocol == "repeated":
        right.plot(LAMBDAS, [res[l]["train"] for l in LAMBDAS], color=PALETTE["navy"], marker="s", linestyle="dashed", linewidth=1.6,
                   label="error on the training sample")
    sel = res[lam]
    right.plot([lam], [sel["error"]], "o", color=PALETTE["terracotta"], markersize=11, markerfacecolor="none", markeredgewidth=2)
    label_point(right, lam, sel["error"], f"{fmt(sel['error'], 3)}", color=PALETTE["terracotta"], dx=0, dy=10 if protocol == "once" else -16,
                ha="center", va="bottom" if protocol == "once" else "top").set_bbox(BOX)
    right.set_xlim(-0.06, 1.06)
    right.set_ylim(0, 0.5)
    right.set_xlabel("Lambda (0: one-step rule, 1: outcome rule)")
    right.set_ylabel("Root mean squared error")
    right.set_title("Random walk: 100 seeded training sets" if protocol == "repeated" else "Random walk: each set presented once", fontsize=11.5)
    right.legend(loc="upper center", bbox_to_anchor=(0.5, -0.2), ncol=1, frameon=False, fontsize=10)

    terminal = w[-1]
    e0, e1 = res[0.0], res[1.0]
    metrics = {
        "Weight on the one-step target": fmt(w[0], 4),
        "Weight on the full return": fmt(terminal, 4),
        "Weight on the other lookahead targets": fmt(total - terminal - w[0], 4),
        "Weights add to": fmt(total, 4),
        "Random-walk error at this lambda": fmt(sel["error"], 3),
        "Random-walk error at lambda 0 and 1": f"{fmt(e0['error'], 3)} and {fmt(e1['error'], 3)}",
    }
    if protocol == "repeated":
        metrics["Training-sample error at lambda 0 and 1"] = f"{fmt(e0['train'], 3)} and {fmt(e1['train'], 3)}"
    else:
        metrics["Best step size at this lambda"] = fmt(sel["alpha"], 2)
    if lam == 0:
        note = "At lambda = 0 all weight sits on the one-step target, which is the target inside Equation (12.2)."
    elif lam == 1:
        note = "At lambda = 1 all weight sits on the complete return, which is the target in Equation (12.1)."
    else:
        note = "Raising lambda moves weight from the short targets toward the complete return, but the weights always add to one."
    if protocol == "repeated":
        sim = (f" In the constructed random walk, each of 100 seeded sets of 10 walks was presented repeatedly until the weights stopped changing. "
               f"The error against the true values k/6 is {fmt(e0['error'], 3)} at lambda 0 and {fmt(e1['error'], 3)} at lambda 1 (standard error about "
               f"{fmt(e1['se'], 3)}), while the error on the training sample runs the other way, {fmt(e0['train'], 3)} to {fmt(e1['train'], 3)}: "
               "the outcome rule fits the sample best and the truth worst.")
    else:
        bestl = min(LAMBDAS, key=lambda l: res[l]["error"])
        sim = (f" In the constructed random walk each training set was presented once, with the best step size chosen at each lambda. "
               f"The lowest error in this run is at lambda {fmt(bestl, 1)} ({fmt(res[bestl]['error'], 3)}), not at lambda 0 ({fmt(e0['error'], 3)}), "
               f"and the outcome rule is last ({fmt(e1['error'], 3)}); differences among the small lambda values are within about one standard error, "
               f"{fmt(res[bestl]['se'], 3)}.")
    calc_first = f"First weight = 1 - {fmt(lam, 1)} = {fmt(w[0], 4)}. Full-return weight = {fmt(lam, 1)}^{n - 1} = {fmt(terminal, 4)}. "
    interpretation = (
        f"{calc_first}Check: lookahead weights add to 1 - {fmt(lam, 1)}^{n - 1} = {fmt(1 - terminal, 4)}, and {fmt(1 - terminal, 4)} + "
        f"{fmt(terminal, 4)} = {fmt(total, 4)}. {note}{sim}"
    )
    steps = [
        f"First weight = 1 - lambda = 1 - {fmt(lam, 1)} = {fmt(w[0], 4)}.",
        f"Weight of the k-step target = (1 - lambda) x lambda^(k-1), for k = 1 to {n - 1}.",
        f"Full-return weight = lambda^{n - 1} = {fmt(lam, 1)}^{n - 1} = {fmt(terminal, 4)}.",
        f"Lookahead weights add to 1 - {fmt(terminal, 4)} = {fmt(1 - terminal, 4)}.",
        f"Total = {fmt(1 - terminal, 4)} + {fmt(terminal, 4)} = {fmt(total, 4)}.",
    ]
    alt = (f"Left: eight bars of weight for the k-step targets at lambda {fmt(lam, 1)}; the first is {fmt(w[0], 3)} and the last, the full return, is {fmt(terminal, 3)}. "
           f"Right: root mean squared error of the random-walk predictions at seven lambda values, from {fmt(e0['error'], 3)} at lambda 0 to {fmt(e1['error'], 3)} at lambda 1; "
           f"the selected lambda is circled at {fmt(sel['error'], 3)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: an error that is not blame, and a value that changes the action

REWARD = -0.02  # the book's cost of the first, unhelpful search
PRIOR = 0.2
FINISH = 0.6
INSPECT_COST = -0.1
Y_START = 0.5


def lab_one_step(states, rewards, values, alpha, terminal):
    out = evaluate({
        "states": states, "rewards": rewards, "discount": 1, "learning_rate": alpha,
        "lambda": 0, "terminal": terminal, "values": values,
    })
    return out["metrics"]["td_zero_values"], out["series"][1]["y"]


def td_error_picture(successor=0.5, alpha=0.8):
    successor, alpha = float(successor), float(alpha)
    _, deltas = lab_one_step(["before", "after"], [REWARD], {"before": PRIOR, "after": successor}, 0.5, False)
    delta = deltas[0]
    if not math.isclose(delta, REWARD + successor - PRIOR, abs_tol=1e-12):
        raise AssertionError("laboratory TD error disagrees with Equation (12.2)")
    vals, _ = lab_one_step(["y", "end"], [1], {"y": Y_START, "end": 0}, alpha, True)
    y_new = vals["y"]
    if not math.isclose(y_new, Y_START + alpha * (1 + 0 - Y_START), abs_tol=1e-12):
        raise AssertionError("laboratory update disagrees with Equation (12.3)")
    inspect_before = INSPECT_COST + Y_START
    inspect_after = INSPECT_COST + y_new
    chosen_before = "inspect" if inspect_before > FINISH + 1e-12 else "finish"
    if abs(inspect_after - FINISH) < 1e-9:
        chosen_after = "tie"
    else:
        chosen_after = "inspect" if inspect_after > FINISH else "finish"

    fig, (left, right) = new_figure(ncols=2, height=4.4)
    parts = [REWARD, successor, -PRIOR, delta]
    names = ["reward r", "successor\nestimate", "minus own\nestimate", "error delta"]
    colors = [PALETTE["gold"], PALETTE["navy"], PALETTE["grey"], PALETTE["terracotta"]]
    for i, (v, c) in enumerate(zip(parts, colors)):
        left.bar(i, v, width=0.6, color=c if i < 3 else "white", edgecolor=c, hatch=None if i < 3 else "///", linewidth=1.3)
        left.annotate(fmt(v, 2), (i, v), xytext=(0, 4 if v >= 0 else -4), textcoords="offset points", ha="center",
                      va="bottom" if v >= 0 else "top", fontsize=10.5, color=PALETTE["ink"])
    left.axhline(0, color=PALETTE["ink"], linewidth=1)
    left.set_xticks(range(4), names)
    left.set_ylim(-0.5, 1.0)
    left.set_xlim(-0.6, 3.6)
    left.set_xlabel("Terms of Equation (12.2), then their sum")
    left.set_ylabel("Size of term (constructed units)")
    left.set_title(f"Search: estimate {fmt(PRIOR, 2)} before, {fmt(successor, 2)} after", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    bars = [("finish", FINISH, PALETTE["terracotta"], ""), ("inspect,\nbefore training", inspect_before, PALETTE["navy"], "///"),
            ("inspect,\nafter training", inspect_after, PALETTE["teal"], "")]
    for i, (name, v, c, h) in enumerate(bars):
        right.bar(i, v, width=0.6, color="white" if h else c, edgecolor=c, hatch=h, linewidth=1.3)
        right.annotate(fmt(v, 2), (i, v), xytext=(0, 4), textcoords="offset points", ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
    right.set_xticks(range(3), [b[0] for b in bars])
    right.set_ylim(0, 1.15)
    right.set_xlim(-0.6, 2.6)
    right.set_xlabel(f"Option at state x (continuation estimate {fmt(Y_START, 2)}, then {fmt(y_new, 2)})")
    right.set_ylabel("Value of the option (constructed units)")
    right.set_title(f"Lookahead, step size {fmt(alpha, 1)}", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    sign = "zero" if abs(delta) < 1e-12 else ("positive" if delta > 0 else "negative")
    break_even = PRIOR - REWARD
    metrics = {
        "TD error delta": fmt(delta, 2),
        "Sign": sign,
        "Successor estimate that gives zero": fmt(break_even, 2),
        "Continuation estimate after training": fmt(y_new, 3),
        "Inspect after training": fmt(inspect_after, 3),
        "Action chosen after training": chosen_after,
    }
    if abs(delta) < 1e-12:
        verdict = "The error is exactly zero: the reward and the new estimate together match the old estimate, so nothing is repaired."
    elif delta > 0:
        verdict = (("The book's first search was unhelpful" if math.isclose(successor, 0.5) else
                    "Like the book's first search, this one was unhelpful") + f" and cost {fmt(-REWARD, 2)}, yet the error is positive, because the estimate after it "
                   f"is higher than the estimate before it by more than that cost, so the forecast for the earlier state is raised.")
    elif successor < PRIOR:
        verdict = (f"The error is negative. The estimate fell from {fmt(PRIOR, 2)} to {fmt(successor, 2)} after the search, and the cost of "
                   f"{fmt(-REWARD, 2)} adds to that, so the earlier state's forecast is lowered. This is a repair of a prediction, not a verdict on the search.")
    else:
        verdict = (f"The error is negative. The estimate rose from {fmt(PRIOR, 2)} to {fmt(successor, 2)} after the search, by less than the cost of "
                   f"{fmt(-REWARD, 2)}, so the earlier state's forecast is lowered. This is a repair of a prediction, not a verdict on the search.")
    if chosen_after == "tie":
        lookahead = (f"Lookahead: inspect scores {fmt(INSPECT_COST, 1)} + {fmt(y_new, 3)} = {fmt(inspect_after, 3)}, exactly finish's {fmt(FINISH, 1)}, "
                     "so the comparison ties and the updated estimate does not yet choose.")
    elif chosen_after == "inspect":
        lookahead = (f"Lookahead: inspect now scores {sn(INSPECT_COST)} + {fmt(y_new, 3)} = {fmt(inspect_after, 3)}, above finish's {fmt(FINISH, 1)}, "
                     "so the chosen action switches to inspect.")
    else:
        lookahead = (f"Lookahead: inspect scores {sn(INSPECT_COST)} + {fmt(y_new, 3)} = {fmt(inspect_after, 3)}, still below finish's {fmt(FINISH, 1)}, "
                     "so the controller still finishes.")
    interpretation = (
        f"delta = {signed(REWARD, 2)} + {fmt(successor, 2)} - {fmt(PRIOR, 2)} = {fmt(delta, 2)}. The error is zero at a successor "
        f"estimate of {fmt(PRIOR, 2)} - {signed(REWARD, 2)} = {fmt(break_even, 2)}; above that it is positive, below it negative. {verdict} "
        f"Training on a run that reaches y and pays 1: delta = 1 + 0 - {fmt(Y_START, 1)} = {fmt(1 - Y_START, 1)}, so the continuation estimate becomes "
        f"{fmt(Y_START, 1)} + {fmt(alpha, 1)} x {fmt(1 - Y_START, 1)} = {fmt(y_new, 3)}. {lookahead} "
        "Before training, inspect scored -0.1 + 0.5 = 0.4 against 0.6, so the controller finished; this update repairs predictions only and does not say which action caused any outcome."
    )
    steps = [
        f"Search error: delta = {signed(REWARD, 2)} + {fmt(successor, 2)} - {fmt(PRIOR, 2)} = {fmt(delta, 2)} ({sign}).",
        f"Zero error at a successor estimate of {fmt(PRIOR, 2)} + {fmt(-REWARD, 2)} = {fmt(break_even, 2)}.",
        f"Before training: inspect = {sn(INSPECT_COST)} + {fmt(Y_START, 1)} = {fmt(inspect_before, 1)} against finish {fmt(FINISH, 1)}, so finish.",
        f"Training run reaches y and pays 1: delta = 1 + 0 - {fmt(Y_START, 1)} = {fmt(1 - Y_START, 1)}.",
        f"Update: {fmt(Y_START, 1)} + {fmt(alpha, 1)} x {fmt(1 - Y_START, 1)} = {fmt(y_new, 3)}.",
        f"After training: inspect = {sn(INSPECT_COST)} + {fmt(y_new, 3)} = {fmt(inspect_after, 3)} against finish {fmt(FINISH, 1)}: {chosen_after}.",
    ]
    alt = (f"Left: four bars for the first search, reward {fmt(REWARD, 2)}, successor estimate {fmt(successor, 2)}, minus own estimate {fmt(-PRIOR, 2)}, "
           f"and the error {fmt(delta, 2)}. Right: three bars, finish {fmt(FINISH, 1)}, inspect before training {fmt(inspect_before, 1)} and inspect after training "
           f"{fmt(inspect_after, 2)}; the action chosen after training is {chosen_after}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 12,
    "title": "Credit for Consequences",
    "subtitle": "Predictions of future return can be repaired from the final outcome or from the next prediction. Neither repair says which action caused the outcome.",
    "summary": (
        "These four demonstrations follow the chapter's progression: update rules pass by pass on four runs, the "
        "eight-episode construction on which they disagree, the dial that blends them beside the random-walk experiment, and a "
        "tool-call example where the sign of the error depends on predictions rather than on blame, and a learned value can change the next action."
    ),
    "ask_skill": {
        "prompt": (
            "Use my own trajectory: states plan, search, answer, rewards 0 then 1, discount 1, learning rate 0.4, lambda 0.5, terminal "
            "true, all values 0. Show the return targets and the outcome, one-step and trace updates, and then repeat it with terminal false and a final value of 1."
        )
    },
    "demos": [
        {
            "id": "C12-D01",
            "title": "One run, three update rules, pass by pass",
            "question": "When a run pays only at its last step, which state estimates move, and how far does the news travel on each pass under each rule?",
            "equations": [EQ_OUTCOME, EQ_DELTA, EQ_TD],
            "symbols": (
                "V-hat is the current estimate of a state's future return. Ret is the return that actually followed the state. alpha is the step size, "
                "the fraction of the gap that is kept. r is the immediate reward, gamma is the discount factor (1 except in the a, b, c, d run, where it is 0.9), "
                "x_t is the state visited at step t, and delta is the one-step error: the reward plus the next state's estimate minus the state's "
                "own estimate. The end of a terminated run has value 0; a truncated run keeps a supplied estimate. The trace rule uses lambda to carry later "
                "errors back to earlier states. A pass is one sequential run through the same trajectory."
            ),
            "prediction": "In the four-action run (step size 0.1, estimates 0.5, final reward 1), after the first pass, how many of the four estimates have moved under the outcome rule, and how many under the one-step rule?",
            "prediction_options": [
                "Only state 4 under both rules.",
                "All four under the outcome rule, only state 4 under the one-step rule.",
                "Only state 4 under the outcome rule, all four under the one-step rule.",
                "All four under both rules.",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "The outcome rule moves every state to 0.5 + 0.1 x (1 - 0.5) = 0.55; the one-step errors for states 1 to 3 are 0 + 0.5 - 0.5 = 0, and only state 4 moves, 1 + 0 - 0.5 = 0.5.",
                "incorrect": "Choose the four-action run at pass 1: the outcome rule moves every state to 0.5 + 0.1 x (1 - 0.5) = 0.55, while the one-step errors for states 1 to 3 are 0 + 0.5 - 0.5 = 0, so only state 4 moves.",
            },
            "stepper": "passes_done",
            "explanation": (
                "The outcome rule waits for the end and then moves every visited estimate toward the return that followed it. "
                "The one-step rule uses the reward plus the next estimate as its target. With every estimate at 0.5 and zero reward before the last step, "
                "the first three errors are exactly zero, so only the last state moves on the first pass; on later passes the raised estimate reaches "
                "one state further back each time. The trace rule sits between the two. In the truncated run the final estimate is supplied, so it anchors the targets "
                "instead of the terminal value 0."
            ),
            "application": (
                "When a long run ends in success or failure, an update that touches every visited state is a statement about "
                "the returns that followed those states under the policy that was run. It is not an itemised receipt for "
                "each action, and the one-step rule's zero errors do not say the early steps were unimportant."
            ),
            "assumptions": (
                "States visited once each in a fixed order, one sequential pass repeated on the same trajectory, and values and step sizes declared "
                "for each run (the notebook's draft, review, done run, its truncated variant and its a, b, c, d run, and the book's four-action run). "
                "Different starting estimates, discounts or replay orders change which states move. Repeating one trajectory is a teaching device, not a training set."
            ),
            "check": "In the draft, review, done run (step size 0.5, lambda 0.8, terminal) after one pass, what does the outcome rule give draft, and what does the one-step rule give draft?",
            "answer": "The return from draft is 0 + 1 = 1, so the outcome rule gives 0 + 0.5 x (1 - 0) = 0.5. The one-step error at draft is 0 + 0 - 0 = 0 (review is still 0 when draft is updated), so draft stays at 0.",
            "provenance": "Constructed example: the book's four-action trajectory (estimates 0.5, step size 0.1, final reward 1) and the laboratory's default, changed and transfer cases (draft, review, done; truncated; a, b, c, d), computed with the laboratory's trajectory-credit function and repeated pass by pass.",
            "source_section": "The two rules on one trajectory",
            "source_anchor": "the-two-rules-on-one-trajectory",
            "misconception": {
                "title": "Equal updates mean equal credit",
                "text": ("The chapter says the four identical updates of the outcome rule are predictions of subsequent return, not allocations of causal responsibility, "
                         "and that the first three TD errors vanish by arithmetic without certifying that those transitions were unimportant."),
            },
            "scope_note": {
                "text": ("The convergence result is for the linear one-step rule with linearly independent state representations under repeated "
                         "presentation, and arbitrary language-model agent representations and training procedures need not satisfy those conditions."),
                "source_section": SCOPE,
            },
            "controls": [
                {"key": "case", "label": "Run", "values": ["book", "default", "changed", "transfer"], "default": "book",
                 "value_labels": ["Book: four actions, final reward 1", "Notebook default: draft, review, done", "Notebook changed: the run is truncated",
                                  "Notebook transfer: a, b, c, d"]},
                {"key": "passes_done", "label": "Passes through the run", "values": [1, 2, 3], "default": 1},
            ],
            "function": "trajectory_picture",
        },
        {
            "id": "C12-D02",
            "title": "Eight episodes, two answers about state A",
            "question": "Why do the two rules agree about state B but disagree about state A, which was seen only once?",
            "equations": [EQ_OUTCOME, EQ_DELTA, EQ_TD],
            "symbols": (
                "A and B are the two states. Each episode ends with a reward when it reaches the end. The outcome rule sets a "
                "state to the average return that followed its visits. The one-step rule sets a state to the reward plus the "
                "estimate of the state that followed it. No discounting (gamma is 1). x_t is the state at step t and V-hat its "
                "estimate. Values are what each rule settles on when it is run "
                "in batch form, repeatedly over the same eight episodes with a small step size."
            ),
            "prediction": "With six of the seven B-only episodes paying 1 and the A episode ending at 0, what does each rule say A is worth?",
            "prediction_options": [
                "Outcome rule 0.75, one-step rule 0.",
                "Both rules say 0.75.",
                "Both rules say 0.",
                "Outcome rule 0, one-step rule 0.75.",
            ],
            "prediction_answer": 3,
            "prediction_feedback": {
                "correct": "B = (6 + 0) / 8 = 0.75. The outcome rule copies A's one return, 0; the one-step rule gives A = 0 + B = 0.75.",
                "incorrect": "Use six ones and an A episode ending at 0: B = (6 + 0) / 8 = 0.75, the outcome rule gives A the one return it saw (0), and the one-step rule gives A = 0 + B = 0.75.",
            },
            "explanation": (
                "B is visited eight times, so both rules average its eight returns. A is visited once, followed by B with no "
                "reward. The outcome rule copies that single return. The one-step rule says A is worth whatever B is worth, "
                "and so it borrows the evidence from the seven episodes that never contained A."
            ),
            "application": (
                "When a state is rare but its successor is common, ask whether the stated process really sends the rare state "
                "to that successor. If so, the successor-based answer pools more evidence; if not, it imports a mistake."
            ),
            "assumptions": (
                "The process is stipulated: A always goes to B with no reward, and B pays at random. Eight observations do not "
                "prove that. The one-step answer is better only if that process is real and the successor's value is "
                "reliable. The outcome rule is not wrong about the data; it fits them exactly."
            ),
            "check": "Suppose three of the seven B-only episodes pay 1 and the A episode ends at 0. What is B, and how far is the outcome rule's value for A from the one-step rule's?",
            "answer": "B = (3 + 0) / 8 = 0.375. The outcome rule gives A = 0, the one-step rule gives A = 0.375, so they differ by 0.375.",
            "provenance": "Constructed example: the book's eight-episode construction (six ones among the seven B-only episodes, the A episode ending at 0), with those counts varied.",
            "source_section": "Eight episodes, two answers",
            "source_anchor": "eight-episodes-two-answers",
            "misconception": {
                "title": "The rule that fits the data perfectly is the right one",
                "text": ("The chapter says the outcome rule is not wrong about the data: it fits the single A episode with zero error, which is exactly what its guarantee promises. "
                         "The guarantee names a criterion, fit to a sample, and what anybody wanted is accuracy on cases not yet seen."),
            },
            "controls": [
                {"key": "ones_in_b_only", "label": "B-only episodes that pay 1 (out of 7)", "values": [3, 6, 7], "default": 6},
                {"key": "a_final", "label": "Reward at the end of the one A episode", "values": [0, 1], "default": 0},
            ],
            "function": "eight_episodes_picture",
        },
        {
            "id": "C12-D03",
            "title": "One dial between the two rules",
            "question": "How does the blending parameter lambda divide weight between short lookahead targets and the complete return, and what does it do to prediction on a random walk?",
            "equations": [EQ_LAMBDA],
            "symbols": (
                "lambda is the blending parameter between 0 and 1. A k-step target adds the next k rewards to the estimate k "
                "steps ahead. N is the number of transitions in the whole episode and t the current step, so n = N - t "
                "is the number of transitions left (8 here, as in Figure 12.4); j counts the rewards inside a target, and gamma is the discount "
                "factor (the weights do not depend on it). With n transitions left, the first n - 1 targets get weight (1 - lambda) x lambda^(k-1) and "
                "the complete return gets the remaining weight, lambda^(n-1). The weights always add to 1. It is not the "
                "step size and not the discount factor. In the right panel, the true value of each interior state B to F of the seven-state random walk "
                "is k/6 for k = 1 to 5, and the error is the root mean square miss over those five states."
            ),
            "prediction": "With 8 transitions remaining and lambda = 0.9, does the complete return or the one-step target get more weight?",
            "prediction_options": [
                "The one-step target, which always gets the most weight.",
                "They get equal weight.",
                "The complete return, 0.9^7 = 0.478, against 0.1 for the one-step target.",
            ],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "The complete return gets 0.9^7 = 0.4783 and the one-step target gets 1 - 0.9 = 0.1, as in Figure 12.4.",
                "incorrect": "Set lambda to 0.9: the one-step target gets 1 - 0.9 = 0.1, while the complete return gets the remaining weight 0.9^7 = 0.4783, as in Figure 12.4.",
            },
            "explanation": (
                "Each extra step of lookahead is weighted lambda times the one before it, so small lambda piles weight on the "
                "one-step target and large lambda spreads it out. Whatever weight the lookahead targets leave over goes to the "
                "complete return, so the two opening rules are the two ends of the dial. The right panel scores the dial on the chapter's random walk. When each training set is "
                "presented repeatedly, the outcome rule (lambda 1) has the lowest error on the training sample and the highest error against the truth. "
                "Presented once, the best lambda is small but is not clearly the one-step end, and the chapter attributes that to the one-step rule being slow at propagating information back."
            ),
            "application": (
                "When a method is described as temporal-difference (TD) learning with a lambda setting, read it as a choice of target mixture: how much to "
                "trust the agent's own estimates relative to what actually happened. For a fixed policy and a prediction target, it "
                "changes the estimator, not the objective."
            ),
            "assumptions": (
                "The weights are for a single episode that terminates after n transitions, with terminal value zero. The right panel is a constructed experiment: "
                "100 training sets of 10 walks drawn with a fixed seed, a table of five values, and, for the single presentation, a step size chosen from a grid at each lambda. "
                "It reproduces the shape of the chapter's experiment, not Sutton's published numbers, and it does not say which lambda is best for any other problem."
            ),
            "check": "With 8 transitions remaining and lambda = 0.3, what weight does the first target get, and what does the complete return get?",
            "answer": "First target: 1 - 0.3 = 0.7. Complete return: 0.3^7 = 0.0002187, which the figure labels as less than 0.001. The weights still add to 1.",
            "provenance": "Constructed example: the weights of Equation (12.4) for the book's eight-transition case (Figure 12.4) and the chapter's random-walk chain (Figure 12.2), with seeded walks and lambda values defined for this reader.",
            "source_section": "The family between the two rules",
            "source_anchor": "the-family-between-the-two-rules",
            "misconception": {
                "title": "Lambda is the discount factor or the learning rate",
                "text": ("The chapter says lambda is a statement about the estimator, how much the agent trusts its own estimates relative to what happened, while the discount factor "
                         "is a statement about the objective. It is also not the step size, which controls how far each update moves, and not exploration."),
            },
            "scope_note": {
                "text": ("The random walk is five numbers; the results are a demonstration rather than a general performance claim."),
                "source_section": SCOPE,
            },
            "controls": [
                {"key": "lam", "label": "Blending parameter lambda", "values": [0, 0.3, 0.9, 1], "default": 0.9},
                {"key": "protocol", "label": "How each training set is presented", "values": ["repeated", "once"], "default": "repeated",
                 "value_labels": ["Repeatedly, until the weights stop changing", "Once, with the best step size"]},
            ],
            "function": "lambda_picture",
        },
        {
            "id": "C12-D04",
            "title": "A positive error for a useless search, and a value that switches the action",
            "question": "Can the one-step error be positive after a search that cost something and returned nothing useful, and when does an updated value change the next action?",
            "equations": [EQ_DELTA, EQ_TD],
            "symbols": (
                "r is the reward for the call, here a cost of 0.02 (reward -0.02). The discount factor gamma is 1. The prior estimate is the "
                "agent's forecast of future return before the search (0.20); the successor estimate is its forecast after the "
                "search. delta is the reward plus the successor estimate minus the prior estimate; it is the temporal-difference (TD) error. "
                "Right panel: at state x, finish ends with reward 0.6, and inspect costs 0.1 and reaches state y, where a fixed continuation policy takes the final action. "
                "The estimate of y starts at 0.5 and is trained with step size alpha on a run that reaches y and pays 1."
            ),
            "prediction": "With the prior estimate at 0.20, which successor estimates give a positive error: 0.10, 0.50 or 0.80?",
            "prediction_options": [
                "All three, because the cost is only 0.02.",
                "0.50 and 0.80: any successor above 0.22.",
                "Only 0.80.",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "delta = -0.02 + successor - 0.20: 0.10 gives -0.12, 0.50 gives 0.28 and 0.80 gives 0.58. The error is positive above 0.22.",
                "incorrect": "Use delta = -0.02 + successor - 0.20: successor 0.10 gives -0.12, 0.50 gives 0.28 and 0.80 gives 0.58, so only the two higher successors give a positive error.",
            },
            "explanation": (
                "The error compares the old forecast with the observed reward plus the new forecast. A cost of 0.02 makes the "
                "reward slightly negative, but the sign is set by the two estimates. The right panel adds the bridge to action: training moves the continuation estimate of y "
                "from 0.5 toward 1, so inspect rises from 0.4 to -0.1 plus the new estimate, and it overtakes finish (0.6) once that estimate passes 0.7, which with these numbers "
                "needs a step size above 0.4. The update needed visits to y; a controller that always finishes never reaches y."
            ),
            "application": (
                "When reading a log of TD errors from an agent, do not treat a positive error as praise for the call just made, "
                "or a negative one as blame. Credit for a particular call needs a comparison with what would have happened "
                "without it, which these updates do not provide."
            ),
            "assumptions": (
                "One transition with the reward and estimates set by hand, as in the chapter's example, and a model at x that is known while the continuation value is learned. "
                "Estimates here are declared numbers, not fitted values; one reward of 1 may overstate the continuation policy's mean, so the switch is an improvement in the "
                "estimated comparison, and its real return still needs evaluation."
            ),
            "check": "At step size 0.5, what is the estimate of y after training, and which action does the controller now choose?",
            "answer": "delta = 1 + 0 - 0.5 = 0.5, so the estimate becomes 0.5 + 0.5 x 0.5 = 0.75. Inspect scores -0.1 + 0.75 = 0.65, above finish's 0.6, so the controller now inspects.",
            "provenance": "Constructed example: the book's first search (reward -0.02, estimates 0.20 before and 0.50 or 0.10 after) and its finish-or-inspect example (finish 0.6, inspect cost 0.1, estimate 0.5, step size 0.8); other successor estimates and step sizes are defined for this reader; both updates are checked against the laboratory's trajectory-credit function.",
            "source_section": "When a learned value changes the next action",
            "source_anchor": "when-a-learned-value-changes-the-next-action",
            "misconception": {
                "title": "A positive error praises the call that was just made",
                "text": ("The chapter says the TD error is not a verdict on the call: with a reward of -0.02, a prior estimate of 0.20 and a successor estimate of 0.50 the error is 0.28, "
                         "positive despite the search's cost and lack of useful results, and an optimistic estimate can fall after a useful action."),
            },
            "scope_note": {
                "text": ("Chapter 14 takes up what happens when the dynamics are learned explicitly rather than implied."),
                "source_section": SCOPE,
            },
            "controls": [
                {"key": "successor", "label": "Estimate after the search", "values": [0.1, 0.5, 0.8], "default": 0.5},
                {"key": "alpha", "label": "Step size for training the estimate of y", "values": [0.3, 0.4, 0.5, 0.8], "default": 0.8},
            ],
            "function": "td_error_picture",
        },
    ],
}

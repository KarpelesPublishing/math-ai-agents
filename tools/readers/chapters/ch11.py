"""Chapter 11 reader: The Mathematics of Curiosity.

Four demonstrations built on Equations (11.1) to (11.4).

Scenarios (all constructed teaching values):
  D01 regret of three allocation rules, each drawn from one seeded run of the
      laboratory's own bandit function (math_ai_agents.chapters.ch11.evaluate):
      the chapter's tools A 0.78 and B 0.90, and the notebook's default (0.4,
      0.7), changed (swapped means) and transfer (three arms) worlds, plus the
      closed-form lines of the two rules that do not work;
  D02 the chapter's ten-pull table (pulls 4 and 5), the trapped controller of
      Figure 11.1 at task twenty (A 18 pulls with 14 successes, B 2 pulls with
      none) and the original workbench problem III.1 (80 and 20 pulls);
  D03 information gain against decision value for a claim check;
  D04 the book's worked price of one observation (7/3).
"""
import math
from functools import lru_cache

import numpy as np

from math_ai_agents.chapters.ch11 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

EQ_REGRET = r"\operatorname{Reg}(T)=T\mu^{\star}-\operatorname{E}\!\left[\sum_{t=0}^{T-1}\mu_{a_t}\right]"
EQ_UCB = r"a_t=\arg\max_{a\in\mathcal{A}}\left(\hat\mu_a+c\sqrt{\frac{\ln t}{N_t(a)}}\right)"
EQ_GAIN = r"\operatorname{Gain}(O)=I(Y;O)=H(Y)-H(Y\mid O)"
EQ_VOI = r"\operatorname{VOI}(O)=\operatorname{E}_{O}\!\left[\max_{a}\operatorname{EU}(a\mid O)\right]-\max_{a}\operatorname{EU}(a)"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
SCOPE = "What this does not settle"


def big(x, digits=1):
    """Number with thousands separators and fixed decimals, ASCII only (1,200.0)."""
    return f"{float(x):,.{digits}f}"


def count_text(x):
    """Integer with thousands separators, ASCII only."""
    return f"{int(round(x)):,}"


# Demonstration 1: regret of three allocation rules in four worlds

WORLDS = {
    "book": {"means": [0.78, 0.90], "seed": 11, "rounds": 1000, "cost": 0.0},
    "default": {"means": [0.4, 0.7], "seed": 7, "rounds": 120, "cost": 0.05},
    "swapped": {"means": [0.7, 0.4], "seed": 7, "rounds": 120, "cost": 0.05},
    "three": {"means": [0.2, 0.5, 0.8], "seed": 19, "rounds": 90, "cost": 0.1},
}
RULES = [("greedy", "Always the\ncurrent best"), ("ucb", "Optimistic\n(UCB)"), ("thompson", "Posterior\nsampling")]
RULE_NAMES = {"greedy": "always the current best", "ucb": "optimistic rule", "thompson": "posterior sampling"}
ARM_COLORS = [PALETTE["navy"], PALETTE["gold"], PALETTE["teal"]]


@lru_cache(maxsize=None)
def lab_run(world, scale):
    spec = WORLDS[world]
    rounds = spec["rounds"] * (10 if scale == "ten" else 1)
    out = evaluate({"means": spec["means"], "rounds": rounds, "seed": spec["seed"], "pull_cost": spec["cost"]})
    curves = {s["label"].split()[0]: tuple(s["y"]) for s in out["series"]}
    return rounds, out["metrics"]["policies"], curves


POOL_SEEDS = 200


@lru_cache(maxsize=None)
def pooled(world, scale):
    """Regret of each rule over seeds 0..POOL_SEEDS-1 of the laboratory bandit, plus how often the always-the-current-best
    rule ends above half of the stuck line (the best arm was locked out early)."""
    spec = WORLDS[world]
    means = spec["means"]
    rounds = spec["rounds"] * (10 if scale == "ten" else 1)
    best = max(means)
    half_stuck = 0.5 * (best - sorted(means)[-2]) * rounds
    totals = {k: 0.0 for k, _ in RULES}
    locked = 0
    for seed in range(POOL_SEEDS):
        out = evaluate({"means": means, "rounds": rounds, "seed": seed, "pull_cost": spec["cost"]})["metrics"]["policies"]
        for k, _ in RULES:
            totals[k] += out[k]["cumulative_pseudo_regret"]
        if out["greedy"]["cumulative_pseudo_regret"] > half_stuck:
            locked += 1
    return {k: v / POOL_SEEDS for k, v in totals.items()}, locked


def regret_picture(world="book", scale="own"):
    spec = WORLDS[world]
    means = spec["means"]
    arms = "ABC"[:len(means)]
    best = max(means)
    gaps = [best - m for m in means]
    rounds, policies, curves = lab_run(world, scale)
    ordered = sorted(means)
    runner_up = ordered[-2]
    gap_ru = best - runner_up
    stuck = gap_ru * rounds
    rotate = rounds * (best - sum(means) / len(means))
    t = np.arange(1, rounds + 1)
    keep = np.unique(np.append(np.arange(0, rounds, max(1, rounds // 150)), rounds - 1))

    fig, (left, right) = new_figure(ncols=2, height=4.8)
    left.plot(t, gap_ru * t, color=PALETTE["terracotta"], linewidth=2, linestyle="dashed", label="stuck on the runner-up arm (gap x tasks)")
    left.plot(t, rotate / rounds * t, color=PALETTE["grey"], linewidth=2, linestyle="dotted", label="rotate evenly")
    styles = {"greedy": (PALETTE["navy"], "solid"), "ucb": (PALETTE["teal"], "solid"), "thompson": (PALETTE["gold"], "dashdot")}
    for key, name in RULES:
        y = np.array(curves[key])
        left.plot(t[keep], y[keep], color=styles[key][0], linestyle=styles[key][1], linewidth=1.8,
                  label=f"{RULE_NAMES[key]}, one seeded run")
    top = max(stuck, rotate, max(max(c) for c in curves.values()))
    left.set_xlim(0, rounds * 1.03)
    left.set_ylim(-0.04 * top, top * 1.08)
    left.set_yticks([v for v in left.get_yticks() if v >= 0])
    left.set_ylim(-0.04 * top, top * 1.08)
    left.set_xlabel("Task number")
    left.set_ylabel("Accumulated regret (successes forgone)")
    left.set_title(f"Regret over {count_text(rounds)} tasks", fontsize=11.5)
    left.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=1, frameon=False, fontsize=10)

    for r, (key, name) in enumerate(RULES):
        counts = policies[key]["counts"]
        y = len(RULES) - 1 - r
        start = 0
        for a, n in enumerate(counts):
            right.barh(y, n, left=start, height=0.6, color=ARM_COLORS[a])
            if n >= 0.07 * rounds:
                right.text(start + n / 2, y, str(n), ha="center", va="center", fontsize=10.5, color="white")
            start += n
    right.set_yticks(range(len(RULES) - 1, -1, -1), [n for _, n in RULES])
    right.set_xlim(0, rounds)
    right.set_xlabel("Pulls of each arm (tasks)")
    right.set_ylabel("Rule")
    right.grid(axis="y", alpha=0)
    for a in range(len(means)):
        right.bar([rounds * 5], [0], color=ARM_COLORS[a], label=f"arm {arms[a]} (success {fmt(means[a], 2)})")
    right.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=1, frameon=False, fontsize=10)
    right.set_title("Where the pulls went", fontsize=11.5)

    regrets = {}
    terms = {}
    for key, _ in RULES:
        counts = policies[key]["counts"]
        regrets[key] = sum(g * n for g, n in zip(gaps, counts))
        if not math.isclose(regrets[key], policies[key]["cumulative_pseudo_regret"], abs_tol=1e-6):
            raise AssertionError("regret differs from the sum of gap x pulls")
        terms[key] = " + ".join(f"{fmt(g, 2)} x {n}" for g, n in zip(gaps, counts) if g > 1e-12)
    p_unlucky = (1 - best) ** 2
    pool_mean, pool_locked = pooled(world, scale)
    pool_text = (f"Over seeds 0 to {POOL_SEEDS - 1} of the same laboratory function, the mean regret is "
                 f"{fmt(pool_mean['greedy'], 2)} for always the current best, {fmt(pool_mean['ucb'], 2)} for the optimistic rule and "
                 f"{fmt(pool_mean['thompson'], 2)} for posterior sampling, and always the current best ends above half of the stuck line in "
                 f"{pool_locked} of {POOL_SEEDS} seeds (the best arm was locked out early), so one seeded run is a thin guide to this rule.")
    metrics = {
        "Stuck on the runner-up arm": fmt(stuck, 2),
        "Rotate evenly": fmt(rotate, 2),
        "Always the current best (this run)": fmt(regrets["greedy"], 2),
        "Optimistic rule (this run)": fmt(regrets["ucb"], 2),
        "Posterior sampling (this run)": fmt(regrets["thompson"], 2),
        f"Always the current best, seeds above half the stuck line (of {POOL_SEEDS})": str(pool_locked),
        f"Mean regret over {POOL_SEEDS} seeds, always the current best": fmt(pool_mean["greedy"], 2),
        f"Mean regret over {POOL_SEEDS} seeds, optimistic rule": fmt(pool_mean["ucb"], 2),
        f"Mean regret over {POOL_SEEDS} seeds, posterior sampling": fmt(pool_mean["thompson"], 2),
        "Chance the chapter's controller draws two failures in a row from the best arm": fmt(p_unlucky, 2),
        "Success rate a stuck agent would report": fmt(runner_up, 2),
        "Best success rate available": fmt(best, 2),
    }
    n_arms = len(means)
    avg = sum(means) / n_arms
    calc_runs = "; ".join(f"{RULE_NAMES[k]}: {terms[k]} = {fmt(regrets[k], 2)}" for k, _ in RULES)
    greedy_other = sum(n for a, n in enumerate(policies["greedy"]["counts"]) if gaps[a] > 1e-12)
    if regrets["greedy"] < regrets["ucb"]:
        luck = (f" In this one seeded run the always-the-current-best rule pulled the arms that are not best only {greedy_other} times, "
                "so it beat the optimistic rule. That is the luck of one seed, not a ranking: the danger the chapter names is "
                "that an unlucky first pull can lock the best arm out for good, and the stuck line prices that case.")
    else:
        luck = (" In this one seeded run the always-the-current-best rule did worse than the optimistic rule; "
                "a single seed is not a performance estimate either way.")
    cost_text = ""
    if spec["cost"]:
        cost_text = (f" A common cost of {fmt(spec['cost'], 2)} per pull lowers every rule's net reward by {fmt(spec['cost'], 2)} x "
                     f"{count_text(rounds)} = {fmt(spec['cost'] * rounds, 2)} and leaves these regrets unchanged.")
    interpretation = (
        f"Regret of a run is the sum of gap x pulls: {calc_runs}. "
        f"Stuck on the runner-up arm for {count_text(rounds)} tasks: {fmt(gap_ru, 2)} x {count_text(rounds)} = {fmt(stuck, 2)}. "
        f"Rotating evenly: {count_text(rounds)} x ({fmt(best, 2)} - {fmt(avg, 2)}) = {fmt(rotate, 2)}. "
        f"The best arm's first two pulls both fail with chance (1 - {fmt(best, 2)}) x (1 - {fmt(best, 2)}) = {fmt(p_unlucky, 2)}. "
        f"A stuck agent would report a success rate of {fmt(runner_up, 2)} and look stable, while {fmt(best, 2)} was available.{luck} {pool_text}{cost_text}"
    )
    steps = [
        "Gaps: best mean minus each arm's mean, " + ", ".join(f"arm {arms[a]} {fmt(gaps[a], 2)}" for a in range(n_arms)) + ".",
        "Pulls of each arm in this run: " + "; ".join(f"{RULE_NAMES[k]} {', '.join(str(n) for n in policies[k]['counts'])}" for k, _ in RULES) + ".",
        f"Regret = sum of gap x pulls. {RULE_NAMES['ucb'].capitalize()}: {terms['ucb']} = {fmt(regrets['ucb'], 2)}.",
        f"Posterior sampling: {terms['thompson']} = {fmt(regrets['thompson'], 2)}.",
        f"Stuck line: {fmt(gap_ru, 2)} x {count_text(rounds)} = {fmt(stuck, 2)}.",
        f"The chapter's controller drew two failures in a row from the best arm: {fmt(1 - best, 2)} x {fmt(1 - best, 2)} = {fmt(p_unlucky, 2)}.",
        f"Over seeds 0 to {POOL_SEEDS - 1}, mean regret: current best {fmt(pool_mean['greedy'], 2)}, optimistic {fmt(pool_mean['ucb'], 2)}, "
        f"posterior {fmt(pool_mean['thompson'], 2)}; current best ends above half the stuck line in {pool_locked} of {POOL_SEEDS} seeds.",
    ]
    alt = (f"Left: accumulated regret over {count_text(rounds)} tasks for five lines: a dashed straight line for being stuck on the runner-up arm "
           f"ending at {fmt(stuck, 1)}, a dotted line for rotating evenly ending at {fmt(rotate, 1)}, and one seeded run each of always the current best "
           f"({fmt(regrets['greedy'], 1)}), the optimistic rule ({fmt(regrets['ucb'], 1)}) and posterior sampling ({fmt(regrets['thompson'], 1)}). "
           "Right: stacked bars of how many pulls each rule gave each arm.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: optimism, the ten pulls, the trapped controller and the workbench problem

def reward(arm, pulls_so_far):
    """Deterministic teaching rewards: A returns 1, 0, 1, 0, ...; B returns 0, 1, 0, 1, ..."""
    return (1 - pulls_so_far % 2) if arm == 0 else (pulls_so_far % 2)


def trace(c, last_pull):
    """Replay the chapter's deterministic trace with confidence coefficient c up to pull number last_pull.

    Returns the record of the decision made at pull number last_pull.
    """
    counts = [0, 0]
    sums = [0.0, 0.0]
    record = None
    for pull in range(1, last_pull + 1):
        t = pull - 1  # completed pulls
        means = [sums[a] / counts[a] if counts[a] else None for a in (0, 1)]
        if 0 in counts:
            bonuses = [None, None]
            indices = [None, None]
            selected = counts.index(0)
        else:
            bonuses = [c * math.sqrt(math.log(t) / counts[a]) for a in (0, 1)]
            indices = [means[a] + bonuses[a] for a in (0, 1)]
            selected = 0 if indices[0] >= indices[1] - 1e-9 else 1  # exact ties go to A (alphabetical)
        r = reward(selected, counts[selected])
        record = {"pull": pull, "t": t, "counts": tuple(counts), "means": means, "bonuses": bonuses,
                  "indices": indices, "selected": selected, "reward": r}
        counts[selected] += 1
        sums[selected] += r
    return record


# (completed pulls t, counts, empirical means) for the two situations that are not the table
STATIC = {
    "trap": (20, (18, 2), (14 / 18, 0.0)),
    "bench": (100, (80, 20), (0.70, 0.60)),
}


def record_for(situation, c):
    if situation in ("p4", "p5"):
        rec = trace(c, int(situation[1]))
        rec["title"] = f"Pull {rec['pull']}, {rec['t']} pulls completed, c = {fmt(c, 3)}"
        rec["noun"] = "tool"
        return rec
    t, counts, means = STATIC[situation]
    bonuses = [c * math.sqrt(math.log(t) / counts[a]) for a in (0, 1)]
    indices = [means[a] + bonuses[a] for a in (0, 1)]
    selected = 0 if indices[0] >= indices[1] - 1e-9 else 1
    title = (f"Trapped controller after {t} tasks, c = {fmt(c, 3)}" if situation == "trap"
             else f"Workbench problem, {t} pulls completed, c = {fmt(c, 3)}")
    return {"pull": None, "t": t, "counts": counts, "means": list(means), "bonuses": bonuses, "indices": indices,
            "selected": selected, "reward": None, "title": title, "noun": "tool" if situation == "trap" else "action"}


def ucb_picture(situation="p4", c=math.sqrt(2)):
    c = float(c)
    rec = record_for(situation, c)
    noun = rec["noun"]
    names = ["A", "B"]
    fig, ax = new_figure(height=4.3)
    top = max(rec["indices"])
    for a in (0, 1):
        color = PALETTE["navy"] if a == 0 else PALETTE["olive"]
        ax.bar(a, rec["means"][a], width=0.55, color=color)
        ax.bar(a, rec["bonuses"][a], bottom=rec["means"][a], width=0.55, color="white", edgecolor=color, hatch="///", linewidth=1.4)
        chosen = " (selected)" if a == rec["selected"] else ""
        ax.text(a, rec["indices"][a] + 0.05, f"index {fmt(rec['indices'][a], 3)}{chosen}", ha="center", va="bottom",
                fontsize=11, color=PALETTE["ink"], bbox=BOX)
        if rec["means"][a] > 0.15:
            ax.text(a, rec["means"][a] / 2, f"mean\n{fmt(rec['means'][a], 3)}", ha="center", va="center", fontsize=11, color="white")
        else:  # a mean too small to hold a label inside its bar is still printed, at the baseline
            ax.text(a, 0.02, f"mean {fmt(rec['means'][a], 3)}", ha="center", va="bottom", fontsize=10.5,
                    color=PALETTE["ink"], bbox=BOX)
        bonus_y = rec["means"][a] + rec["bonuses"][a] / 2
        ax.text(a, bonus_y, f"bonus\n{fmt(rec['bonuses'][a], 3)}", ha="center", va="center", fontsize=11,
                color=PALETTE["ink"], bbox=BOX)
    cap = noun.capitalize()
    ax.set_xticks([0, 1], [f"{cap} {n}: {rec['counts'][i]} {'pull' if rec['counts'][i] == 1 else 'pulls'}" for i, n in enumerate(names)])
    ax.set_xlim(-0.6, 1.6)
    ax.set_ylim(0, top + 0.45)
    ax.set_xlabel(f"{'Retrieval tool' if noun == 'tool' else 'Action'} and how often it has been pulled")
    ax.set_ylabel("Index = mean + bonus (hatched part)")
    ax.grid(axis="x", alpha=0)
    ax.set_title(rec["title"], fontsize=11.5)

    chosen_name = names[rec["selected"]]
    mean_choice = 0 if rec["means"][0] >= rec["means"][1] else 1
    metrics = {
        "Counts A, B": f"{rec['counts'][0]}, {rec['counts'][1]}",
        "Index A": fmt(rec["indices"][0], 3),
        "Index B": fmt(rec["indices"][1], 3),
        "Selected": chosen_name,
        "Selected by mean alone": names[mean_choice],
    }
    if rec["reward"] is not None:
        metrics["Reward seen after the pull"] = str(rec["reward"])
    lnt = math.log(rec["t"])
    sums = []
    step_lines = [f"Completed pulls t = {rec['t']}, so ln t = ln {rec['t']} = {fmt(lnt, 3)}."]
    for a in (0, 1):
        s = (f"{names[a]}: bonus = {fmt(c, 3)} x sqrt({fmt(lnt, 3)} / {rec['counts'][a]}) = {fmt(rec['bonuses'][a], 3)}, "
             f"index = {fmt(rec['means'][a], 3)} + {fmt(rec['bonuses'][a], 3)} = {fmt(rec['indices'][a], 3)}")
        sums.append(s)
        step_lines.append(s + ".")
    other = 1 - rec["selected"]
    gap = rec["indices"][rec["selected"]] - rec["indices"][other]
    if abs(gap) < 1e-9:
        verdict = f"The indices tie exactly, so the rule's alphabetical tie-break selects {chosen_name}."
    else:
        verdict = (f"{cap} {chosen_name} has the larger index by {fmt(gap, 3)}, so Equation (11.2) selects it.")
        if rec["reward"] is not None:
            verdict += f" Its pull number {rec['pull']} then returns {rec['reward']}."
    if mean_choice == rec["selected"]:
        mean_note = f"Ranking by mean alone would also select {chosen_name}, so here the bonus does not change the call."
    else:
        mean_note = (f"Ranking by mean alone would select {names[mean_choice]} ({fmt(rec['means'][mean_choice], 3)} against "
                     f"{fmt(rec['means'][1 - mean_choice], 3)}); the bonus is what lets {chosen_name} in.")
    step_lines.append(f"{verdict} {mean_note}")
    extra = ""
    if situation == "trap":
        extra = (" This is the controller of Figure 11.1: tool B has two pulls and a record of 0.000, and a rule that only ranks means "
                 "would never call it again.")
    interpretation = (f"With {rec['t']} completed pulls, ln {rec['t']} = {fmt(lnt, 3)}. " + ". ".join(sums) + f". {verdict} {mean_note}{extra} "
                      f"{'An' if noun[0] in 'aeiou' else 'A'} {noun} with few pulls keeps a large bonus even when its mean is low.")
    alts = {
        "p4": "the ten-pull table at pull 4", "p5": "the ten-pull table at pull 5",
        "trap": "the trapped controller after 20 tasks", "bench": "the workbench problem with 80 and 20 pulls",
    }
    alt = (f"Two stacked bars for {alts[situation]}: mean (solid) plus bonus (hatched) for A and B. Indices {fmt(rec['indices'][0], 3)} for A "
           f"and {fmt(rec['indices'][1], 3)} for B; {chosen_name} is selected.")
    return fig, metrics, interpretation, {"alt": alt, "steps": step_lines}


# Demonstration 3: information gain is not decision value

SUPPORTED_VALUE = 100.0   # release utility when every claim is supported (unsupported release is worth 0)
EVIDENCE_VALUE = 92.0     # request evidence: 0.97 x 100 - 5, the book's score


def entropy(p):
    """Binary entropy in bits; 0 at the ends."""
    if p <= 0 or p >= 1:
        return 0.0
    return -(p * math.log2(p) + (1 - p) * math.log2(1 - p))


def check_outcomes(prior, accuracy):
    """Symmetric check of a claim: joint probabilities and release scores for each possible report."""
    rows = []
    for report in ("supported", "unsupported"):
        if report == "supported":
            p_report = prior * accuracy + (1 - prior) * (1 - accuracy)
            joint_supported = prior * accuracy
        else:
            p_report = prior * (1 - accuracy) + (1 - prior) * accuracy
            joint_supported = prior * (1 - accuracy)
        posterior = joint_supported / p_report
        rows.append({"report": report, "p": p_report, "joint": joint_supported, "posterior": posterior,
                     "release": SUPPORTED_VALUE * posterior})
    return rows


def gain_value_picture(accuracy=0.85, prior=0.85):
    rows = check_outcomes(prior, accuracy)
    h_before = entropy(prior)
    h_after = sum(r["p"] * entropy(r["posterior"]) for r in rows)
    gain = h_before - h_after
    best_now = max(SUPPORTED_VALUE * prior, EVIDENCE_VALUE)
    best_after = sum(max(SUPPORTED_VALUE * r["joint"], EVIDENCE_VALUE * r["p"]) for r in rows)
    voi = best_after - best_now
    changes = any((r["release"] > EVIDENCE_VALUE) != (SUPPORTED_VALUE * prior > EVIDENCE_VALUE) for r in rows)

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.bar([0, 1], [h_before, h_after], width=0.55, color=[PALETTE["grey"], PALETTE["teal"]])
    left.bar([1], [gain], bottom=[h_after], width=0.55, color="white", edgecolor=PALETTE["teal"], hatch="///", linewidth=1.4)
    left.text(0, h_before + 0.02, f"{fmt(h_before, 3)}", ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.text(1, h_before + 0.02, f"{fmt(h_after, 3)}\ngain {fmt(gain, 3)}", ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.set_xticks([0, 1], ["Before the check", "After the check"])
    left.set_xlim(-0.6, 1.6)
    left.set_ylim(0, 1.3)
    left.set_xlabel("Uncertainty about the claim (hatched part is removed)")
    left.set_ylabel("Entropy in bits")
    left.set_title("Uncertainty resolved", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    xs = [0, 1]
    colors = [PALETTE["teal"] if r["release"] > EVIDENCE_VALUE else PALETTE["navy"] for r in rows]
    right.bar(xs, [r["release"] for r in rows], width=0.55, color="white", edgecolor=colors, hatch="..", linewidth=1.4)
    right.axhline(EVIDENCE_VALUE, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.8)
    right.axhline(SUPPORTED_VALUE * prior, color=PALETTE["grey"], linestyle="dotted", linewidth=1.4)
    for x, r in zip(xs, rows):
        verdict = "release" if r["release"] > EVIDENCE_VALUE else "request evidence"
        right.text(x, 14, f"{fmt(r['release'], 1)}\n{verdict}", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
    no_check_above = SUPPORTED_VALUE * prior > EVIDENCE_VALUE
    label_point(right, 1.4, EVIDENCE_VALUE, "evidence 92.0", color=PALETTE["terracotta"], dx=0, dy=-4 if no_check_above else 4, ha="left",
                va="top" if no_check_above else "bottom")
    label_point(right, 1.4, SUPPORTED_VALUE * prior, f"no check {fmt(SUPPORTED_VALUE * prior, 1)}", color=PALETTE["grey"], dx=0,
                dy=4 if no_check_above else -4, ha="left", va="bottom" if no_check_above else "top")
    right.set_xticks(xs, ["Check says\nsupported", "Check says\nunsupported"])
    right.set_xlim(-0.6, 2.55)
    right.set_ylim(0, 110)
    right.set_xlabel("What the check reports (bar is the release score)")
    right.set_ylabel("Expected utility of releasing")
    right.set_title("Does the best action change?", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    metrics = {
        "Uncertainty before, H(Y)": f"{fmt(h_before, 3)} bits",
        "Uncertainty after, H(Y | O)": f"{fmt(h_after, 3)} bits",
        "Information gain I(Y; O)": f"{fmt(gain, 3)} bits",
        "Decision value VOI": fmt(voi, 2),
        "Best action changes": "yes" if changes else "no",
    }
    parts = []
    for r in rows:
        parts.append(f"{r['report']} report (chance {fmt(r['p'], 4)}, posterior release score {fmt(r['release'], 2)}): "
                     f"weighted by that chance, max(100 x {fmt(r['joint'], 4)}, 92 x {fmt(r['p'], 4)}) = "
                     f"max({fmt(SUPPORTED_VALUE * r['joint'], 2)}, {fmt(EVIDENCE_VALUE * r['p'], 2)}) = "
                     f"{fmt(max(SUPPORTED_VALUE * r['joint'], EVIDENCE_VALUE * r['p']), 2)}")
    if changes:
        meaning = "The report moves the best action in at least one case, so the check is worth something before its cost."
    else:
        meaning = ("Both reports leave the same action on top, so the decision value is exactly zero even though the check "
                   f"removed {fmt(gain, 3)} bits of uncertainty. Information gain and decision value are different quantities.")
    interpretation = (
        f"Best action without the check = max(100 x {fmt(prior, 2)}, 92) = max({fmt(SUPPORTED_VALUE * prior, 2)}, 92.00) = {fmt(best_now, 2)}. "
        + "; ".join(parts) + f". VOI = {fmt(best_after, 2)} - {fmt(best_now, 2)} = {fmt(voi, 2)}. " + meaning
    )
    sup, uns = rows
    steps = [
        f"Before the check: H(Y) = {fmt(h_before, 3)} bits; best action now = max({fmt(SUPPORTED_VALUE * prior, 2)}, 92) = {fmt(best_now, 2)}.",
        f"Report supported (chance {fmt(sup['p'], 4)}): posterior {fmt(sup['posterior'], 4)}, release scores {fmt(sup['release'], 2)} against 92.",
        f"Report unsupported (chance {fmt(uns['p'], 4)}): posterior {fmt(uns['posterior'], 4)}, release scores {fmt(uns['release'], 2)} against 92.",
        f"After the check: H(Y | O) = {fmt(h_after, 3)} bits, so the gain is {fmt(h_before, 3)} - {fmt(h_after, 3)} = {fmt(gain, 3)} bits.",
        f"Value: {fmt(best_after, 2)} - {fmt(best_now, 2)} = {fmt(voi, 2)}.",
    ]
    alt = (f"Left: entropy falls from {fmt(h_before, 2)} bits before the check to {fmt(h_after, 2)} bits after it. Right: two bars give the release score "
           f"after each report, {fmt(sup['release'], 1)} after supported and {fmt(uns['release'], 1)} after unsupported, against a dashed line at 92 for requesting evidence. "
           + ("The best action changes." if changes else "The best action does not change."))
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: a worked price for one observation (the book's classifier)

P_FLAG = 1 / 3
RELEASE_FLAG = 75.0
RELEASE_CLEAR = 90.0
SEVEN_THIRDS = 7 / 3


def cost_text(call_cost):
    if abs(call_cost - SEVEN_THIRDS) < 1e-9:
        return "7/3"
    return fmt(call_cost, 1)


def classifier_picture(shift=10, call_cost=0):
    shift = float(shift)
    call_cost = float(call_cost)
    release_flag = RELEASE_FLAG + shift
    release_clear = RELEASE_CLEAR + shift
    release_before = P_FLAG * release_flag + (1 - P_FLAG) * release_clear
    best_before = max(release_before, EVIDENCE_VALUE)
    best_flag = max(release_flag, EVIDENCE_VALUE)
    best_clear = max(release_clear, EVIDENCE_VALUE)
    best_after = P_FLAG * best_flag + (1 - P_FLAG) * best_clear
    voi = best_after - best_before
    net = voi - call_cost

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    groups = [("after flag\n(prob 1/3)", release_flag), ("after clear\n(prob 2/3)", release_clear), ("before\nobserving", release_before)]
    width = 0.36
    for i, (name, rel) in enumerate(groups):
        win_release = rel > EVIDENCE_VALUE
        left.bar(i - width / 2, rel, width=width, color=PALETTE["navy"] if win_release else "white", edgecolor=PALETTE["navy"], linewidth=1.4, hatch="" if win_release else "//")
        left.bar(i + width / 2, EVIDENCE_VALUE, width=width, color=PALETTE["teal"] if not win_release else "white", edgecolor=PALETTE["teal"], linewidth=1.4, hatch="" if not win_release else "..")
        left.text(i - width / 2, rel + 0.8, fmt(rel, 1), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        left.text(i + width / 2, EVIDENCE_VALUE + 0.8, "92.0", ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        left.text(i, 14, "release\nwins" if win_release else "evidence\nwins", ha="center", va="center", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
    left.set_xticks(range(3), [g[0] for g in groups])
    left.set_ylim(0, 118)
    left.set_xlim(-0.6, 2.6)
    left.set_xlabel("When the choice is made (left bar release, right bar evidence)")
    left.set_ylabel("Expected utility")
    left.set_title("Best action under each result", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    bars = [("Gross value", voi, PALETTE["teal"], ""), ("Net of call cost", net, PALETTE["gold"], "///")]
    for i, (name, value, color, hatch) in enumerate(bars):
        right.bar(i, value, width=0.55, color="white", edgecolor=color, hatch=hatch, linewidth=1.6)
        right.text(i, value + (0.12 if value >= 0 else -0.12), fmt(value, 3), ha="center", va="bottom" if value >= 0 else "top", fontsize=11, color=PALETTE["ink"])
    right.axhline(0, color=PALETTE["ink"], linewidth=1)
    right.set_xticks([0, 1], [b[0] for b in bars])
    right.set_xlim(-0.6, 1.6)
    right.set_ylim(-2.9, 3.0)
    right.set_xlabel(f"Call cost charged: {cost_text(call_cost)}" + (" (about 2.333)" if cost_text(call_cost) == "7/3" else ""))
    right.set_ylabel("Value of the observation (utility points)")
    right.set_title("What the call is worth", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    if abs(net) < 1e-9 and call_cost > 0:
        verdict = "Net value is exactly zero, so buying the call and skipping it tie; Equation (11.4) alone does not choose."
        buy = "tie"
    elif net > 0:
        verdict = "Net value is positive, so the call is worth buying for this one decision."
        buy = "yes"
    elif voi < 1e-9:
        verdict = "Gross value is zero: the same action wins after either result, so no price makes the call worth buying."
        buy = "no"
    else:
        verdict = "The call costs more than it can return for this decision, so it is not worth buying."
        buy = "no"
    metrics = {
        "Release now, no observation": fmt(release_before, 3),
        "Best action without the call": fmt(best_before, 3),
        "Best expected utility with the call": fmt(best_after, 3),
        "Gross value": fmt(voi, 3),
        "Net value": fmt(net, 3),
        "Worth buying": buy,
    }
    interpretation = (
        f"Release scores {fmt(release_flag, 0)} after flag and {fmt(release_clear, 0)} after clear, so before observing it scores "
        f"1/3 x {fmt(release_flag, 0)} + 2/3 x {fmt(release_clear, 0)} = {fmt(release_before, 3)} against 92 for requesting evidence. "
        f"With the call the best choices are {fmt(best_flag, 0)} after flag and {fmt(best_clear, 0)} after clear, so "
        f"1/3 x {fmt(best_flag, 0)} + 2/3 x {fmt(best_clear, 0)} = {fmt(best_after, 3)}. Gross value = {fmt(best_after, 3)} - {fmt(best_before, 3)} "
        f"= {fmt(voi, 3)}; net value = {fmt(voi, 3)} - {cost_text(call_cost)} = {fmt(net, 3)}. {verdict} "
        "The classifier itself never changed between states; only the decision it feeds did."
    )
    steps = [
        f"Release scores {fmt(release_flag, 0)} after flag and {fmt(release_clear, 0)} after clear; requesting evidence scores 92 either way.",
        f"Without the call: 1/3 x {fmt(release_flag, 0)} + 2/3 x {fmt(release_clear, 0)} = {fmt(release_before, 3)}, best = {fmt(best_before, 3)}.",
        f"With the call: 1/3 x {fmt(best_flag, 0)} + 2/3 x {fmt(best_clear, 0)} = {fmt(best_after, 3)}.",
        f"Gross value = {fmt(best_after, 3)} - {fmt(best_before, 3)} = {fmt(voi, 3)}.",
        f"Net value = {fmt(voi, 3)} - {cost_text(call_cost)} = {fmt(net, 3)}.",
    ]
    alt = (f"Left: for each of three moments (after flag, after clear, before observing) a release bar and an evidence bar of 92. "
           f"Right: bars for gross value {fmt(voi, 2)} and net value {fmt(net, 2)} at call cost {cost_text(call_cost)}. Worth buying: {buy}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 11,
    "title": "The Mathematics of Curiosity",
    "subtitle": "Choosing a tool decides which evidence you get about it. Curiosity becomes a costed allocation rule, and information is worth only what it can change.",
    "summary": (
        "These four demonstrations follow the chapter's document controller and its two retrieval tools. First the cost of "
        "never looking again is measured as regret for three rules in four worlds, then an optimistic rule is traced pull by pull, "
        "then information gain is separated from decision value, and finally one observation is priced."
    ),
    "ask_skill": {
        "prompt": (
            "Use my own two tools with success probabilities 0.5 and 0.65, 200 rounds, seed 3 and a pull cost of 0.02. "
            "Compare the pseudo-regret of the greedy, upper-confidence and Thompson policies, and check that each equals the gap "
            "times that policy's pulls of the worse tool."
        )
    },
    "demos": [
        {
            "id": "C11-D01",
            "title": "Regret: what never looking again costs",
            "question": "How fast does the shortfall against an all-knowing agent grow under the rules that always exploit, always rotate, explore with optimism or sample from a belief?",
            "equations": [EQ_REGRET],
            "symbols": (
                "T is the number of tasks. mu-star is the success probability of the best arm (tool). mu of a_t is the success probability "
                "of the arm chosen at task t, and E is the average over luck. Regret is the total successes forgone compared with "
                "always using the best arm; for a run it equals the sum, over arms, of the gap to the best mean times the pulls of that arm. "
                "Worlds: the book's tools (A 0.78, B 0.90, 1,000 tasks), the notebook's default (0.4 and 0.7, 120 tasks), its swapped case "
                "(0.7 and 0.4) and its three-arm case (0.2, 0.5 and 0.8, 90 tasks). Each curve is one seeded run."
            ),
            "prediction": "In the book's world, go from the run of 1,000 tasks to the ten-times-longer run of 10,000. By what factor does the regret of being stuck on the worse tool grow, and does the optimistic rule's seeded regret grow by more or less?",
            "prediction_options": [
                "Both grow ten times.",
                "Stuck regret grows ten times; the optimistic run grows by more than ten times.",
                "Stuck regret grows ten times; the optimistic run grows by less than ten times.",
            ],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "Stuck regret is 0.12 x 1,000 = 120 and 0.12 x 10,000 = 1,200, ten times. The optimistic run goes from 29.64 to 105.24, about 3.6 times.",
                "incorrect": "Choose the ten-times-longer run in the book's world: stuck regret goes from 0.12 x 1,000 = 120 to 0.12 x 10,000 = 1,200 (ten times), while the optimistic run goes from 29.64 to 105.24, about 3.6 times.",
            },
            "explanation": (
                "Taking the worse arm every time forgoes the gap on every task, so regret is the gap times T, a straight line; rotating evenly "
                "forgoes the average gap, a straight line half as steep for two arms. The optimistic rule and posterior sampling keep trying "
                "a thin-record arm only while it is still uncertain, so their regret flattens relative to the lines. The right panel shows "
                "why: regret is the sum of gap x pulls, so it is made only of pulls of arms that are not best. A seeded run is not an average: always "
                "taking the current best can look best when its first pulls happen to find the best arm."
            ),
            "application": (
                "When a team reports a success rate for a deployed agent, ask how much of its action set it has sampled recently. "
                "Regret itself needs the true means, which a deployed agent does not have, so this is the question that can be asked. "
                "An agent that took one action thousands of times and the alternatives twice may have stopped measuring."
            ),
            "assumptions": (
                "Independent fixed success probabilities and one seeded run per rule, so each curve is one draw of luck: it is not a policy "
                "performance estimate and not the expectation in Equation (11.1). Regret here is pseudo-regret, computed from the known means, "
                "which a deployed agent does not have. The stuck and rotate lines are closed forms. Real tools change over time, which this model does not cover."
            ),
            "check": "If tool A succeeds 0.78 and tool B 0.90, how much regret does an agent that rotates evenly build up over 500 tasks?",
            "answer": "Half the tasks go to A and cost 0.12 each: 250 x 0.12 = 30. Equivalently 500 x 0.90 - (250 x 0.78 + 250 x 0.90) = 450 - 420 = 30.",
            "provenance": "Constructed example: the book's invented success rates 0.78 and 0.90 and its 1,000-task comparison, and the notebook's default, swapped and three-arm worlds; every curve is one seeded run computed with the laboratory's bandit function.",
            "source_section": "What is actually being lost",
            "source_anchor": "what-is-actually-being-lost",
            "misconception": {
                "title": "A stable, respectable success rate means nothing better was available",
                "text": ("The chapter says under-exploration is invisible in an evaluation: a trapped controller reports 78 percent, its logs show consistent "
                         "behavior, and an evaluation reports what a system did, not what a differently behaving version would have done. The metric "
                         "'success rate a stuck agent would report' sits beside 'best success rate available' for that reason."),
            },
            "scope_note": {
                "text": ("The setting assumes actions do not change the world and payoffs are drawn independently, and neither holds for a deployed agent."),
                "source_section": SCOPE,
            },
            "controls": [
                {"key": "world", "label": "World", "values": ["book", "default", "swapped", "three"], "default": "book",
                 "value_labels": ["Book tools: A 0.78, B 0.90", "Notebook default: 0.4 and 0.7", "Notebook changed: 0.7 and 0.4",
                                  "Notebook transfer: 0.2, 0.5 and 0.8"]},
                {"key": "scale", "label": "Length of the run", "values": ["own", "ten"], "default": "own",
                 "value_labels": ["The world's own run (book 1,000; notebook 120; three-arm 90 tasks)", "Ten times longer"]},
            ],
            "function": "regret_picture",
        },
        {
            "id": "C11-D02",
            "title": "Optimism: why a thin record gets another call",
            "question": "Why does a tool with a poor record and few pulls get called again, and what changes that?",
            "equations": [EQ_UCB],
            "symbols": (
                "t is the number of completed pulls. N_t(a) is how many of those pulls went to tool a. mu-hat of a is tool a's average reward so far. "
                "c is the confidence coefficient; the book uses the square root of two, about 1.414, for rewards between 0 and 1. ln is the natural logarithm. "
                "The index is the mean plus the bonus c x sqrt(ln t / N_t(a)), and the tool with the larger index is called. Situations: pull 4 or "
                "pull 5 of the chapter's ten-pull table; the trapped controller after 20 tasks (A has 18 pulls and 14 successes, B has 2 pulls and none); "
                "the workbench problem (A has 80 pulls and mean 0.70, B has 20 pulls and mean 0.60)."
            ),
            "prediction": "Pick pull 5 of the table with c = 1.414 (square root of 2). Tool B has a mean of 0.000 and tool A has 0.667. Does the rule call A or B?",
            "prediction_options": ["Tool A, because its mean is higher.", "Tool B, because its bonus is larger than the gap in means."],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "B's index is 0.000 + 1.665 = 1.665 and A's is 0.667 + 0.961 = 1.628, so B is called although its mean is lower.",
                "incorrect": "Pick pull 5 with c = 1.414: B's bonus is 1.414 x sqrt(1.386 / 1) = 1.665, so its index 1.665 beats A's 0.667 + 0.961 = 1.628 and B is called.",
            },
            "explanation": (
                "The bonus grows slowly with the clock and shrinks as a tool is pulled, so a tool that is left alone gains bonus until it wins "
                "a call. In the trapped controller, B's two pulls give it a bonus of 1.731 against A's 0.577, enough to overturn a mean gap of 0.778. "
                "A smaller c shrinks every bonus: at c = 0.5 the same controller keeps calling A. If B then succeeds its estimate rises, and if it fails "
                "its count rises and its bonus shrinks; either way it is being updated again."
            ),
            "application": (
                "When a controller must choose among components with thin records, an index of this shape gives a written reason for each "
                "call, which can be audited, instead of a vague claim that the system is curious."
            ),
            "assumptions": (
                "The table's rewards are the book's invented alternating sequence (A returns 1, 0, 1, 0, and so on; B returns 0, 1, 0, 1), not a "
                "test of the stochastic guarantee. Each tool is pulled once first, ties go to A, and the bonus uses unrounded values. Changing c "
                "changes the rule; the book's guarantee is stated for c equal to the square root of two with rewards in [0, 1]. The trapped controller and the "
                "workbench problem are single decisions given counts and means, not runs."
            ),
            "check": "At pull 5 of the table the counts are 3 and 1 after 4 completed pulls. With c = 1.414, what is B's bonus?",
            "answer": "ln 4 = 1.386, so the bonus is 1.414 x sqrt(1.386 / 1) = 1.414 x 1.177 = 1.665 (rounded).",
            "provenance": "Constructed example: the chapter's ten-pull table with c equal to the square root of two (invented teaching rewards), the chapter's trapped controller (18 pulls with 14 successes, 2 pulls with none) and the original workbench problem III.1 (80 and 20 pulls); the values of c other than the square root of two are defined for this reader.",
            "source_section": "A proved rule and ten constructed pulls",
            "source_anchor": "a-proved-rule-and-ten-constructed-pulls",
            "misconception": {
                "title": "A low estimate is a reason never to look again",
                "text": ("The chapter's trapped controller drew two failures from a nine-in-ten process, and its rule contained no reason to look again: once a tool's "
                         "estimate falls low enough to stop being selected, nothing will update it. The failure is in the loop from estimates to choices to data, "
                         "not in the arithmetic of the estimate."),
            },
            "scope_note": {
                "text": ("Equation (11.2) requires a constant whose right value depends on the payoff scale."),
                "source_section": SCOPE,
            },
            "controls": [
                {"key": "situation", "label": "Situation", "values": ["p4", "p5", "trap", "bench"], "default": "p4",
                 "value_labels": ["Ten-pull table, pull 4", "Ten-pull table, pull 5", "Trapped controller after 20 tasks",
                                  "Workbench: 80 and 20 pulls"]},
                {"key": "c", "label": "Confidence coefficient c", "values": [math.sqrt(2), 1.0, 0.5], "default": math.sqrt(2),
                 "value_labels": ["square root of 2 (about 1.414)", "1", "0.5"]},
            ],
            "function": "ucb_picture",
        },
        {
            "id": "C11-D03",
            "title": "Information gain is not decision value",
            "question": "Can a check remove uncertainty about a claim and still be worth exactly nothing?",
            "equations": [EQ_GAIN, EQ_VOI],
            "symbols": (
                "Y is the proposition the decision turns on: every claim in the draft is supported. O is the report of a check. H is entropy in bits, "
                "a measure of uncertainty (1 bit for a fair coin, 0 when certain). I(Y; O) is the uncertainty about Y that O removes. VOI is the "
                "decision value: the average best expected utility with the report, minus the best without it. Releasing scores 100 if supported and 0 if not; "
                "requesting evidence scores 92."
            ),
            "prediction": "With prior 0.85 and a check that is right 0.60 of the time, does the check remove uncertainty, and does it change what the agent does?",
            "prediction_options": [
                "It removes uncertainty and changes the action.",
                "It removes uncertainty but does not change the action.",
                "It removes no uncertainty.",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "The gain is positive, but a supported report moves the release score only to 100 x 0.8947 = 89.5, still below 92, so the same action wins and VOI is 0.",
                "incorrect": "Set accuracy 0.60 and prior 0.85: the gain is positive (the reports correlate with the claim), but neither report lifts the release score above 92, so the action never changes and VOI is 0.",
            },
            "explanation": (
                "Entropy falls whenever the report is correlated with the claim, so the gain is positive. The value in Equation (11.4) is positive only if some report "
                "pushes the release score across the fixed value 92 of the alternative. When the reports leave the release score on the same side of 92 as the no-check score, "
                "the same action wins either way and VOI is zero, as at accuracy 0.60 with prior 0.85. Where that line falls depends on the prior: "
                "accuracy 0.70 is enough at prior 0.85 but not at prior 0.97, and at prior 0.50 even a strong check is needed to lift the score above 92."
            ),
            "application": (
                "Before paying for a check, write down which action follows each possible report. If it is the same action every time, the check is "
                "decoration, however interesting its output."
            ),
            "assumptions": (
                "A symmetric check (equally accurate on supported and unsupported claims), a single decision between releasing and requesting evidence, and a "
                "belief that the stated prior and accuracy are correct. Accuracy and prior here are constructed; a real check may be biased in one direction, which this "
                "model does not cover."
            ),
            "check": "With prior 0.85 and a check that is right 0.70 of the time, a report of unsupported leaves the release score at 70.8. Does that report change the action?",
            "answer": "P(supported and report unsupported) = 0.85 x 0.30 = 0.255 and P(report unsupported) = 0.36, so the release score is 100 x 0.255 / 0.36 = 70.8. That is below 92, which is also the action chosen before the check, so this report changes nothing; only the supported report (score 92.97) does.",
            "provenance": "Constructed example: the book's release score 85 and evidence score 92 (Table 6.1 values); the checks, their accuracies and the priors are defined for this reader.",
            "source_section": "Uncertainty is not the same as value",
            "source_anchor": "uncertainty-is-not-the-same-as-value",
            "misconception": {
                "title": "Resolving uncertainty is the goal",
                "text": ("The chapter says a rule that seeks uncertainty as such will happily spend a budget resolving the number of words in a passage, which is uncertain, "
                         "cheaply resolved and irrelevant. What the agent wants is uncertainty reduction about the quantity the decision turns on, and information has "
                         "value only when it could change what the agent does."),
            },
            "scope_note": {
                "text": ("Equation (11.4) prices a single observation against a fixed decision, not a sequence of them. All numbers in the opening construction are invented for teaching."),
                "source_section": SCOPE,
            },
            "controls": [
                {"key": "accuracy", "label": "How often the check is right", "values": [0.6, 0.7, 0.85, 0.95], "default": 0.85},
                {"key": "prior", "label": "Prior chance the claims are supported", "values": [0.5, 0.85, 0.97], "default": 0.85},
            ],
            "function": "gain_value_picture",
        },
        {
            "id": "C11-D04",
            "title": "A worked price for one observation",
            "question": "How much is one call to a classifier worth, and how can the same classifier be worth zero in one decision and something in another?",
            "equations": [EQ_VOI],
            "symbols": (
                "A classifier reports flag with probability one third and clear with probability two thirds. Releasing scores 75 after flag and 90 after clear, plus the shift "
                "you choose; requesting evidence scores 92 either way. VOI is the average best score with the report minus the best score without it. The call cost "
                "is subtracted to give the net value. The book's price is 7/3, about 2.333."
            ),
            "prediction": "Add 10 to the release scores. Does the classifier become worth buying at a call cost of 2?",
            "prediction_options": [
                "No: gross value is 2.0, so the net value is 0.",
                "Yes: gross value is 7/3 = 2.333, above 2, so the net value is 0.333.",
                "No: the classifier is worth exactly zero.",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "With 10 added, flag leaves release at 85 (evidence wins, 92) and clear gives 100: 1/3 x 92 + 2/3 x 100 = 97.333 against 95 before, so gross 7/3 and net 7/3 - 2 = 0.333.",
                "incorrect": "Set the shift to 10 and the cost to 2: with the call the best scores are 92 after flag and 100 after clear, 1/3 x 92 + 2/3 x 100 = 97.333, against 95 without it, so gross value is 7/3 = 2.333 and net 0.333.",
            },
            "explanation": (
                "With no shift, evidence wins under both reports and the value is exactly zero. A shift of 10 pushes the release score above 92 after clear but not after flag, "
                "so the best action now depends on the report. From a shift of 10 on, releasing already beats requesting evidence before observing (95 at shift 10), so the call can only "
                "rescue the flag branch. At a shift of 15 that branch still scores 90 against 92, so the call adds only 1/3 x (92 - 90) = 0.667. "
                "At a call cost of exactly 7/3 the shift-10 call ties with skipping it."
            ),
            "application": (
                "Price a verification step against the specific decision it feeds. The same step, with the same accuracy and cost, can be a bargain for one decision and "
                "worthless for another. Before spending any budget, also check whether the system already holds the answer in a log it failed to structure: free "
                "information should always be used."
            ),
            "assumptions": (
                "One decision, one observation, a coherent probability model, and a gross value that ignores any later decisions the observation could also inform. "
                "The conditional release scores are the book's constructed values; a real classifier's scores would have to be estimated, and a wrong estimate can flip the verdict."
            ),
            "check": "With a shift of 5, what is the gross value, and is the call worth buying at cost 2?",
            "answer": "Release scores 80 after flag and 95 after clear, and 90 before. With the call: 1/3 x 92 + 2/3 x 95 = 94.0, so gross value = 94 - 92 = 2.0. Net = 2 - 2 = 0, a tie.",
            "provenance": "Constructed example: the book's worked classifier (flag one third, release scores 75 and 90, evidence 92, shift 10 giving 7/3); the other shifts and costs are defined for this reader.",
            "source_section": "A worked price for one observation",
            "source_anchor": "a-worked-price-for-one-observation",
            "misconception": {
                "title": "A call that returns interesting material was worth making",
                "text": ("The chapter says an agent that runs a call whose result cannot change its action is not being thorough: it is failing to distinguish what the call "
                         "would tell it from what it would do differently. The call has a real cost, a real information gain and zero value."),
            },
            "scope_note": {
                "text": ("Equation (11.4) prices a single observation against a fixed decision, not a sequence of them."),
                "source_section": SCOPE,
            },
            "controls": [
                {"key": "shift", "label": "Added to both release scores", "values": [0, 5, 10, 15], "default": 10},
                {"key": "call_cost", "label": "Cost of the call", "values": [0, 2, 7 / 3], "default": 0,
                 "value_labels": ["0", "2", "7/3 (about 2.333)"]},
            ],
            "function": "classifier_picture",
        },
    ],
}

"""Chapter 10 reader: Plans Within Plans.

Four demonstrations built on Equations (10.1) to (10.3). Demonstrations 2 and
4 call the laboratory's own option-duration function
(math_ai_agents.chapters.ch10.evaluate), so the reader, the notebook and the
chapter skill agree.

Scenarios (all constructed teaching values):
  D01 the three parts of an option, with a start rule, an early stop and a
      blocked start (an option that cannot start earns nothing);
  D02 the chapter's worked numbers (rewards 2 and 3, continuation 10, discount
      0.9, value 12.8 against 13.7, also the in-chapter exercise) and the
      workbook transfer case (rewards 0 and 4, continuation 8, discount 0.5);
  D03 the chapter's release workflow (6 minutes, 16 credits), with the audit
      length, the schedule and a stale completion (source v17 then v18);
  D04 the laboratory's review-release default (6.038), the interruption cases
      (-1.9 after 2 steps) and the workbook transfer case (inspect worth 4, a
      disabled option worth 0).
"""
import math

import numpy as np

from math_ai_agents.chapters.ch10 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, signed

EQ_OPTION = r"o=(\mathcal{I}_o,\pi_o,\beta_o)"
EQ_VALUE = (r"Q^{\mu}(x,o)=\operatorname E_\mu\!\left[\sum_{k=0}^{\tau-1}\gamma^k r_{t+k}"
            r"+\gamma^\tau V^\mu(x_{t+\tau})\;\middle|\;x_t=x,o_t=o\right]")
EQ_TOTALS = (r"T_{\mathrm{release}}=\max\{2+3+1,\;4\}=6\text{ minutes},"
             r"\qquad C_{\mathrm{tools}}=4+7+2+3=16\text{ credits}")

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}


def plain(x, digits=4):
    """A number without trailing zeros, for written sums (0.9, 0.81, 0.729)."""
    text = f"{float(x):.{digits}f}".rstrip("0").rstrip(".")
    return "0" if text in ("", "-0") else text


def discounted_sum_text(rewards, gamma, continuation=None, duration=None):
    """Written sum: 1 x r0 + g x r1 + ... [+ g^d x continuation]."""
    parts = [f"{plain(gamma ** t)} x {signed(r, 0)}" for t, r in enumerate(rewards)]
    if continuation is not None:
        parts.append(f"{plain(gamma ** duration)} x {signed(continuation, 0)}")
    return " + ".join(parts)


def plural(n, word="step"):
    return f"{n} {word}" if n == 1 else f"{n} {word}s"


# Demonstration 1: the three parts of an option

RECORDS = list(range(1, 9))  # start states: records still to check
EXAMPLE_START = 6
FAR_START = 8


def option_duration(x, stop_at):
    """Steps from start state x when each step checks one record.

    The option stops when no record is left, or earlier when a missing approval
    is met with stop_at records left (stop_at = 0 means no early stop). The
    stop is tested after each step, so a start state at or below stop_at runs
    to the end.
    """
    return x - stop_at if 0 < stop_at < x else x


def steps_run(x, stop_at, min_records):
    """Steps actually executed: zero when the start rule blocks the start."""
    return option_duration(x, stop_at) if x >= min_records else 0


def parts_picture(min_records=1, stop_at=0):
    allowed = [x for x in RECORDS if x >= min_records]
    fig, ax = new_figure(height=4.7)
    for x in RECORDS:
        tau = option_duration(x, stop_at)
        if x >= min_records:
            for s in range(1, tau + 1):
                ax.barh(x, 0.92, left=s - 1 + 0.04, height=0.72, color=PALETTE["teal"])
            for s in range(tau + 1, x + 1):
                ax.barh(x, 0.92, left=s - 1 + 0.04, height=0.72, color="white", edgecolor=PALETTE["terracotta"],
                        hatch="///", linewidth=0.9)
            note = f"{tau}" if tau == x else f"{tau}, stops early"
            ax.text(x + 0.25, x, note, ha="left", va="center", fontsize=10.5, color=PALETTE["ink"])
        else:
            for s in range(1, tau + 1):
                ax.barh(x, 0.92, left=s - 1 + 0.04, height=0.72, color="white", edgecolor=PALETTE["grey"],
                        hatch="..", linewidth=0.9)
            ax.text(x + 0.25, x, "0, blocked", ha="left", va="center", fontsize=10.5, color=PALETTE["grey"])
    ax.set_yticks(RECORDS)
    ax.set_xticks(range(0, 9))
    ax.set_xlim(0, 11.2)
    ax.set_ylim(0.4, 8.6)
    ax.set_xlabel("Primitive steps taken (one record checked per step)")
    ax.set_ylabel("Start state x: records left")
    ax.grid(axis="y", alpha=0)
    stop_text = "stops only when no record is left" if stop_at == 0 else f"also stops when {stop_at} records remain"
    ax.set_title(f"Start needs x of at least {min_records}; the option {stop_text}", fontsize=11.5)
    ax.bar([20], [0], color=PALETTE["teal"], label="step the option takes")
    ax.bar([20], [0], color="white", edgecolor=PALETTE["terracotta"], hatch="///", label="step not taken (stopped early)")
    ax.bar([20], [0], color="white", edgecolor=PALETTE["grey"], hatch="..", label="start blocked by the start rule")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.17), ncol=1, frameon=False, fontsize=10.5)

    durations = [steps_run(x, stop_at, min_records) for x in RECORDS]
    longest = max(durations)
    d6 = steps_run(EXAMPLE_START, stop_at, min_records)
    d8 = steps_run(FAR_START, stop_at, min_records)
    metrics = {
        "Initiation set": f"x = {allowed[0]} to {allowed[-1]}",
        "Start states allowed": f"{len(allowed)} of {len(RECORDS)}",
        f"Steps run from x = {EXAMPLE_START}": plural(d6),
        f"Steps run from x = {FAR_START}": plural(d8),
        "Longest run from an allowed start": plural(longest),
    }
    if EXAMPLE_START >= min_records:
        t6 = option_duration(EXAMPLE_START, stop_at)
        if stop_at and stop_at < EXAMPLE_START:
            calc6 = (f"From x = {EXAMPLE_START} with a stop when {stop_at} remain, the option checks "
                     f"{EXAMPLE_START} - {stop_at} = {t6} records, so it runs {plural(t6)}.")
        else:
            calc6 = f"From x = {EXAMPLE_START} it checks one record per step, so it runs {EXAMPLE_START} x 1 = {t6} steps."
    else:
        calc6 = (f"From x = {EXAMPLE_START} the start rule x of at least {min_records} fails ({EXAMPLE_START} is below "
                 f"{min_records}), so the option cannot start: it runs 0 steps.")
    t8 = option_duration(FAR_START, stop_at)
    if stop_at:
        calc8 = f"From x = {FAR_START} it runs {FAR_START} - {stop_at} = {t8} steps."
    else:
        calc8 = f"From x = {FAR_START} it runs {FAR_START} x 1 = {t8} steps."
    if min_records > 1:
        gate = (f"The start rule keeps the states {allowed[0]} to {allowed[-1]} and blocks {min_records - 1} of the 8 "
                "states; at a blocked state the controller may not select the option, so it earns nothing there.")
    else:
        gate = "The start rule x of at least 1 allows every state shown."
    if stop_at:
        stop = (f"A start state with {stop_at} or fewer records left never meets the missing approval after a step, "
                f"so it runs to the end: from x = {stop_at} the duration is {option_duration(stop_at, stop_at)}.")
    else:
        stop = "Without an early stop, the duration always equals the number of records."
    interpretation = f"{calc6} {calc8} {gate} {stop} The termination rule, not only the start state, fixes the duration."
    steps = [
        f"Initiation set: states x of at least {min_records}, so x = {allowed[0]} to {allowed[-1]}.",
        "Inner policy: check one record per primitive step.",
        (f"Termination: stop when {stop_at} records remain, else when none remain." if stop_at
         else "Termination: stop only when no record is left."),
        calc6,
        calc8,
    ]
    alt = (f"Eight rows, one per start state from 1 to 8 records left. Allowed rows show one filled cell per step taken; "
           f"the longest run from an allowed start is {plural(longest)}. "
           + (f"{min_records - 1} rows are blocked by the start rule and show dotted cells with 0 steps. " if min_records > 1 else "")
           + (f"Hatched cells mark the {stop_at} steps that the early stop removes from each longer row." if stop_at else
              "No early stop, so every allowed row runs one step per record."))
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 2: value when duration varies

CASES = {
    "chapter": {"rewards": [2.0, 3.0], "continuation": 10.0, "name": "Chapter example"},
    "transfer": {"rewards": [0.0, 4.0], "continuation": 8.0, "name": "Workbook transfer"},
}


def lab_option_value(case, duration, gamma):
    """Equation (10.2) for a completed option, computed by the laboratory's evaluate()."""
    spec = CASES[case]
    rewards = spec["rewards"] + [0.0] * (duration - len(spec["rewards"]))
    out = evaluate({
        "discount": float(gamma), "deadline": 10,
        "options": [{"name": "check", "initiation": True, "rewards": rewards, "terminated": True,
                     "continuation_value": spec["continuation"]}],
    })
    row = out["tables"][0]
    return rewards, row["value"], row["continuation_discount"]


def duration_picture(case="chapter", duration=2, gamma=0.9):
    spec = CASES[case]
    cont_v = spec["continuation"]
    rewards, value, cont_discount = lab_option_value(case, duration, gamma)
    inside = sum(gamma ** t * r for t, r in enumerate(rewards))
    continuation = value - inside
    one_step_cont = gamma * cont_v
    one_step_value = inside + one_step_cont
    overstatement = one_step_value - value
    if not math.isclose(overstatement, cont_v * (gamma - gamma ** duration), abs_tol=1e-9):
        raise AssertionError("overstatement disagrees with V x (gamma - gamma^tau)")

    fig, (left, right) = new_figure(ncols=2, height=4.0)
    rows = [
        ("Rewards inside", 0.0, inside, PALETTE["navy"], None),
        ("Continuation,\ngamma^tau", inside, continuation, PALETTE["teal"], None),
        ("Value by (10.2)", 0.0, value, PALETTE["teal"], None),
        ("Continuation,\ngamma^1", inside, one_step_cont, "white", "///"),
        ("One-step value", 0.0, one_step_value, "white", "///"),
    ]
    top = max(value, one_step_value)
    for i, (label, start, width, color, hatch) in enumerate(rows):
        y = len(rows) - 1 - i
        edge = PALETTE["terracotta"] if hatch else color
        left.barh(y, width, left=start, height=0.58, color=color, edgecolor=edge, hatch=hatch, linewidth=1.2)
        left.text(start + width + 0.25, y, fmt(width, 3), ha="left", va="center", fontsize=10.5, color=PALETTE["ink"])
    left.set_yticks(range(len(rows) - 1, -1, -1), [r[0] for r in rows])
    left.set_xlim(0, top * 1.25 + 1)
    left.set_xlabel("Value (constructed units)")
    left.set_ylabel("Part of the calculation")
    left.grid(axis="y", alpha=0)
    left.set_title(f"{plural(duration)}, discount {fmt(gamma, 1)}", fontsize=11.5)

    ts = np.arange(0, 5)
    weights = gamma ** ts
    colors = [PALETTE["light"]] * 5
    right.bar(ts, weights, width=0.6, color=colors, edgecolor=PALETTE["grey"], linewidth=0.8)
    right.bar([duration], [gamma ** duration], width=0.6, color=PALETTE["teal"])
    right.bar([1], [gamma], width=0.6, color="white", edgecolor=PALETTE["terracotta"], hatch="///", linewidth=1.3)
    if duration == 1:
        pass
    for t, w in zip(ts, weights):
        right.text(t, w + 0.03, (fmt(w, 3) if abs(round(w, 3) - w) < 1e-12 else fmt(w, 4)), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
    right.set_ylim(0, 1.3)
    right.set_xticks(ts)
    right.set_xlabel("Primitive steps elapsed t (teal: where the option ends; hatched: one-step shortcut)")
    right.set_ylabel("Discount weight gamma^t")
    right.set_title("The exponent counts steps", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    metrics = {
        "Rewards inside the option": fmt(inside, 3),
        f"Continuation discounted by gamma^{duration}": fmt(continuation, 3),
        "Value by Equation (10.2)": fmt(value, 3),
        "Value if discounted as one step": fmt(one_step_value, 3),
        "Overstatement": fmt(overstatement, 3),
    }
    written = discounted_sum_text(rewards, gamma, cont_v, duration)
    later = duration - 2
    steps_note = "" if duration == 2 else (
        f" The steps after the second pay 0, so the continuation is pushed {plural(later)} later.")
    v_text = f"{plain(cont_v)}"
    interpretation = (
        f"Value = {written} = {fmt(value, 3)}. Treating the option as one step instead gives "
        f"{fmt(inside, 3)} + {plain(gamma)} x {v_text} = {fmt(one_step_value, 3)}, which is {fmt(overstatement, 3)} too high."
        f"{steps_note} The exponent counts the steps the option really used, so a longer option has its continuation "
        "worth less. Ignoring duration makes delay look too cheap."
    )
    if case == "transfer" and duration == 2 and abs(gamma - 0.5) < 1e-12:
        interpretation += (f" The continuation contributes {plain(gamma ** 2)} x {v_text} = {fmt(continuation, 3)}, "
                           f"not {plain(gamma)} x {v_text} = {fmt(one_step_cont, 3)}, because the option took two steps.")
    inside_terms = " + ".join(f"{plain(gamma ** t)} x {signed(r, 0)}" for t, r in enumerate(rewards))
    steps = [
        f"Rewards inside: {inside_terms} = {fmt(inside, 3)}.",
        f"The option lasts {plural(duration)}, so the continuation is discounted by gamma^{duration} = {plain(gamma ** duration)}.",
        f"Continuation: {plain(gamma ** duration)} x {v_text} = {fmt(continuation, 3)}.",
        f"Value = {fmt(inside, 3)} + {fmt(continuation, 3)} = {fmt(value, 3)}.",
        f"One-step shortcut: {fmt(inside, 3)} + {plain(gamma)} x {v_text} = {fmt(one_step_value, 3)}.",
        f"Overstatement = {fmt(one_step_value, 3)} - {fmt(value, 3)} = {fmt(overstatement, 3)}.",
    ]
    alt = (f"Left: five bars. Rewards inside the option {fmt(inside, 2)}, continuation {fmt(continuation, 2)}, value {fmt(value, 2)}, "
           f"and hatched bars for the one-step shortcut, continuation {fmt(one_step_cont, 2)} and value {fmt(one_step_value, 2)}. "
           f"Right: discount weights for steps 0 to 4, with the weight at step {duration} marked as where the option ends.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: two totals, and a stale completion

ACTIVITIES = [("Draft", 2, 4), ("Verify", 3, 7), ("Publish", 1, 2)]  # name, minutes, credits
AUDIT_CREDITS = 3
REVALIDATE = ("Revalidate", 3, 7)  # stipulated: repeats Verify against the current version


def chain_items(source):
    items = [ACTIVITIES[0], ACTIVITIES[1]]
    if source == "changed":
        items.append(REVALIDATE)
    items.append(ACTIVITIES[2])
    return items


def schedule(audit_minutes, mode, source="same"):
    """Start and end minute of every activity, and the release time."""
    chain, t = {}, 0
    for name, minutes, _ in chain_items(source):
        chain[name] = (t, t + minutes)
        t += minutes
    audit_start = 0 if mode == "parallel" else t
    chain["Audit"] = (audit_start, audit_start + audit_minutes)
    release = max(end for _, end in chain.values())
    return chain, release


def totals_picture(audit_minutes=4, mode="parallel", source="same"):
    items = chain_items(source)
    chain, release = schedule(audit_minutes, mode, source)
    credits = {name: c for name, _, c in items}
    credits["Audit"] = AUDIT_CREDITS
    total_credits = sum(credits.values())
    chain_minutes = sum(m for _, m, _ in items)
    chain_names = [n for n, _, _ in items]
    if mode == "parallel":
        chain_critical = chain_minutes >= audit_minutes
        audit_critical = audit_minutes >= chain_minutes
    else:
        chain_critical = audit_critical = True
    critical = {n: chain_critical for n in chain_names}
    critical["Audit"] = audit_critical
    names = chain_names + ["Audit"]
    stale = source == "changed"
    fig, ax = new_figure(height=4.3)
    for i, name in enumerate(names):
        start, end = chain[name]
        hot = critical[name]
        on_navy = name == "Audit"
        if name == "Verify" and stale:
            fill = PALETTE["gold"]
        elif name == "Revalidate":
            fill = PALETTE["olive"]
        elif on_navy:
            fill = PALETTE["navy"]
        else:
            fill = PALETTE["teal"]
        ax.barh(i, end - start, left=start, height=0.58, color=fill,
                edgecolor=("white" if fill != PALETTE["teal"] else PALETTE["ink"]) if hot else "none",
                hatch="///" if hot else None, linewidth=1.2)
        if hot and fill != PALETTE["teal"]:
            ax.barh(i, end - start, left=start, height=0.58, fill=False, edgecolor=PALETTE["ink"], linewidth=2.0)
        if name == "Verify" and stale:
            ax.text((start + end) / 2, i, "v17", ha="center", va="center", fontsize=11, color="white",
                    bbox={"boxstyle": "round,pad=0.15", "fc": PALETTE["gold"], "ec": "none"})
        if name == "Revalidate":
            ax.text((start + end) / 2, i, "v18", ha="center", va="center", fontsize=11, color="white",
                    bbox={"boxstyle": "round,pad=0.15", "fc": PALETTE["olive"], "ec": "none"})
    ax.set_yticks(range(len(names)), [f"{n} ({credits[n]} credits)" for n in names])
    ax.set_ylim(len(names) - 0.3, -1.0)
    ax.axvline(release, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.6)
    right_side = release > 8
    label_point(ax, release, -0.62, f"release done at minute {release}", color=PALETTE["terracotta"],
                dx=-5 if right_side else 5, dy=0, ha="right" if right_side else "left", va="center").set_bbox(BOX)
    ax.set_xlim(0, 19)
    ax.set_xlabel("Minutes from the start")
    ax.set_ylabel("Activity (tool credits)")
    ax.grid(axis="y", alpha=0)
    label = "Audit in parallel" if mode == "parallel" else "Audit after Publish"
    second = ("hatched bars lie on the longest chain" if not stale else
              "source changed to v18: the v17 check is stale, so Revalidate is added;\nhatched bars lie on the longest chain")
    ax.set_title(f"Release at minute {release} ({total_credits} credits)\n{label}, audit {audit_minutes} min\n{second}", fontsize=10.5)
    if mode == "parallel":
        if chain_critical and audit_critical:
            which = f"{', '.join(chain_names)} and Audit (tie)"
        elif chain_critical:
            which = ", ".join(chain_names)
        else:
            which = "Audit"
    else:
        which = "all, in sequence"
    chain_label = "Chain " + ", ".join(chain_names)
    metrics = {
        "Release time": f"{release} minutes",
        "Total tool cost": f"{total_credits} credits",
        "Longest chain": which,
        chain_label: f"{chain_minutes} minutes",
    }
    chain_sum = " + ".join(str(m) for _, m, _ in items)
    cost_sum = " + ".join(str(c) for c in credits.values())
    if mode == "parallel":
        calc = f"Time T = max{{{chain_sum}, {audit_minutes}}} = max{{{chain_minutes}, {audit_minutes}}} = {release} minutes."
        if chain_critical and audit_critical:
            tie = (f" The two chains tie at {chain_minutes} minutes, so both are on the longest chain: shortening one of them alone "
                   "would not make the release earlier.")
        elif chain_critical:
            tie = f" The audit has {chain_minutes - audit_minutes} {'minute' if chain_minutes - audit_minutes == 1 else 'minutes'} of slack, so speeding it up would not release earlier."
        else:
            tie = (f" Now the audit is the longest chain, so the release waits {audit_minutes - chain_minutes} {'minute' if audit_minutes - chain_minutes == 1 else 'minutes'} "
                   "for it after Publish is finished.")
    else:
        calc = f"Time T = {chain_sum} + {audit_minutes} = {release} minutes, because nothing runs side by side."
        tie = " Running the audit in parallel would have cut the delay without changing the credits."
    stale_text = ""
    if stale:
        stale_text = (" The completion of Verify says something about v17, not v18, so Publish may not use it. Revalidating against "
                      "the current version is added to the required chain (taken here to cost what Verify costs, 3 minutes and 7 credits), "
                      "so the chain and the cost both grow.")
    interpretation = (f"{calc} Cost C = {cost_sum} = {total_credits} credits in every schedule, because every required "
                      f"activity is paid for.{tie}{stale_text}")
    steps = [
        f"Chain minutes: {chain_sum} = {chain_minutes}.",
        f"Audit minutes: {audit_minutes}, starting {'at minute 0' if mode == 'parallel' else 'after Publish'}.",
        (f"Time T = max{{{chain_minutes}, {audit_minutes}}} = {release} minutes." if mode == "parallel"
         else f"Time T = {chain_minutes} + {audit_minutes} = {release} minutes."),
        f"Cost C = {cost_sum} = {total_credits} credits.",
    ]
    if stale:
        steps.insert(1, "Source moved from v17 to v18, so the v17 verification cannot release Publish: add Revalidate (3 min, 7 credits).")
    alt = (f"A bar chart of minutes for {', '.join(names)}. "
           f"The release line is at minute {release} and the total cost is {total_credits} credits. "
           + ("The Verify bar is marked v17 and a Revalidate bar marked v18 follows it. " if stale else "")
           + ("The audit bar starts at minute 0." if mode == "parallel" else "The audit bar starts after Publish ends."))
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: interruption, completion and a disabled option

REVIEW = {"name": "review-release", "rewards": [-1.0, -1.0, 8.0], "continuation": 2.0}
ARCHIVE = {"name": "archive", "rewards": [1.0], "continuation": 0.0}
INSPECT = {"name": "inspect", "rewards": [0.0, 4.0], "continuation": 8.0, "initiation": True}
DISABLED = {"name": "disabled", "rewards": [9.0], "continuation": 0.0, "initiation": False}


def case_inputs(case, gamma):
    """The laboratory input for one case of Demonstration 4 and its two option specs."""
    if case == "transfer":
        specs = (INSPECT, DISABLED)
        data = {"discount": float(gamma), "deadline": 2, "start_time": 0}
    else:
        specs = (dict(REVIEW, initiation=True), dict(ARCHIVE, initiation=True))
        data = {"discount": float(gamma), "deadline": 5}
        if case == "two":
            data["interrupt_after"] = 2
        elif case == "one":
            data["interrupt_after"] = 1
    data["options"] = [
        {"name": o["name"], "initiation": o["initiation"], "rewards": o["rewards"], "terminated": True,
         "continuation_value": o["continuation"]}
        for o in specs
    ]
    return data, specs


CASE_TITLES = {"none": "no interruption", "two": "interrupted after 2 steps", "one": "interrupted after 1 step",
               "transfer": "workbench case: a disabled option beside inspect"}


def interruption_picture(case="none", gamma=0.9):
    data, specs = case_inputs(case, gamma)
    out = evaluate(data)
    rows = {r["name"]: r for r in out["tables"]}
    best = out["metrics"]["best_executed_value"]
    first, second = specs
    r1, r2 = rows[first["name"]], rows[second["name"]]
    fig, ax = new_figure(height=4.3)
    ticks = []
    lows, highs = [0.0], [0.0]
    for x, spec in zip((0.0, 1.9), specs):
        row = rows[spec["name"]]
        cont = row["continuation_discount"] * spec["continuation"] if row["complete"] else 0.0
        inside = row["value"] - cont
        if not row["initiated"]:
            on_offer = spec["rewards"][0]
            ax.bar(x, on_offer, width=0.5, color="white", edgecolor=PALETTE["grey"], hatch="..", linewidth=1.3, linestyle="dashed")
            label_point(ax, x + 0.27, on_offer / 2, f"reward on offer\n{fmt(on_offer, 0)}, never earned", color=PALETTE["grey"],
                        dx=4, dy=0, ha="left", va="center", size=10.5).set_bbox(BOX)
            highs.append(on_offer)
        else:
            ax.bar(x, inside, width=0.5, color=PALETTE["navy"])
            lows.append(min(inside, 0.0))
            highs.append(max(inside, 0.0))
            if row["complete"] and cont != 0:
                ax.bar(x, cont, bottom=inside, width=0.5, color="white", edgecolor=PALETTE["teal"], hatch="///", linewidth=1.4)
                label_point(ax, x - 0.27, inside + cont / 2, f"continuation\n+{fmt(cont, 3)}", dx=-4, dy=0, ha="right",
                            va="center", size=10.5, color=PALETTE["teal"]).set_bbox(BOX)
                highs.append(inside + cont)
        ax.plot([x - 0.25, x + 0.25], [row["value"]] * 2, color=PALETTE["ink"], linewidth=2.2)
        tag = ", chosen" if spec["name"] == best else ""
        label_point(ax, x + 0.25, row["value"], f"value {fmt(row['value'], 3)}{tag}", dx=6, dy=0, ha="left", va="center",
                    size=11).set_bbox(BOX)
        if not row["initiated"]:
            status = "not initiated"
        else:
            status = "completed" if row["complete"] else "not completed"
        ticks.append(f"{spec['name']}\n{row['executed']} of {row['duration']} {'step' if row['duration'] == 1 else 'steps'}, {status}")
    ax.axhline(0, color=PALETTE["grey"], linewidth=1)
    ax.set_xticks([0.0, 1.9], ticks)
    ax.set_xlim(-1.45, 3.7)
    lo, hi = min(lows), max(highs)
    pad = 0.18 * (hi - lo)
    ax.set_ylim(lo - 0.08 * (hi - lo) - 0.6, hi + pad + 0.6)
    ax.set_xlabel("Option, steps that ran, and whether it reached its end")
    ax.set_ylabel("Discounted value (constructed units)")
    ax.grid(axis="x", alpha=0)
    ax.bar([5], [0], color=PALETTE["navy"], label="rewards in the steps that ran")
    ax.bar([5], [0], color="white", edgecolor=PALETTE["teal"], hatch="///", label="continuation, only after completion (stipulated)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.30), ncol=1, frameon=False, fontsize=10.5)
    ax.set_title(f"Discount {fmt(gamma, 1)}; {CASE_TITLES[case]}", fontsize=11.5)

    metrics = {
        f"{first['name']} value": fmt(r1["value"], 3),
        f"{second['name']} value": fmt(r2["value"], 3),
        f"{first['name']} completed": "yes" if r1["complete"] else "no",
        "Higher executed value": best,
    }
    k = r1["executed"]
    if case == "transfer":
        written = discounted_sum_text(first["rewards"], gamma, first["continuation"], 2)
        note = (f"The option ran both steps, so its continuation 8 is discounted by {plain(gamma)} x {plain(gamma)} = "
                f"{plain(gamma ** 2)}, which gives {plain(gamma ** 2)} x 8 = {fmt(gamma ** 2 * 8, 3)} (discounting by one step would "
                f"give {plain(gamma)} x 8 = {fmt(gamma * 8, 3)}). The disabled option fails its start rule, so it runs 0 of 1 "
                "steps and is worth 0 although a reward of 9 is on offer.")
        outcome = f"Inspect is higher, {fmt(r1['value'], 3)} against 0.000 for disabled."
        written_value = f"Inspect = {written} = {fmt(r1['value'], 3)}."
        archive_note = ""
    else:
        if r1["complete"]:
            written = discounted_sum_text(REVIEW["rewards"], gamma, REVIEW["continuation"], 3)
            note = ("The option reached its end, so the continuation value 2 is added after discounting by "
                    f"{plain(gamma)} x {plain(gamma)} x {plain(gamma)} = {plain(gamma ** 3)}.")
        else:
            written = discounted_sum_text(REVIEW["rewards"][:k], gamma)
            note = (f"The option stopped after {k} of 3 steps. The 8 that the third step would pay is never earned and no "
                    "continuation is added here (the reached state is valued at 0 by stipulation).")
        if best == "archive":
            outcome = f"Archive is higher, {fmt(r2['value'], 3)} against {fmt(r1['value'], 3)}."
        else:
            outcome = f"Review-release is higher, {fmt(r1['value'], 3)} against {fmt(r2['value'], 3)} for archive."
        if case == "none" and abs(gamma - 0.5) < 1e-12:
            outcome += " Here the full option is completed yet loses, because heavy discounting shrinks its late reward."
        archive_note = ""
        if case != "none":
            archive_note = (f" Archive needs one step, so an interruption after {plural(k)} does not touch it.")
        written_value = f"Review-release = {written} = {fmt(r1['value'], 3)}."
    interpretation = f"{written_value} {note if case != 'transfer' else note} {outcome}{archive_note}"
    if case == "transfer":
        steps = [
            f"Inspect: rewards 0 then 4, so the inside value is 1 x 0 + {plain(gamma)} x 4 = {fmt(gamma * 4, 3)}.",
            f"It ran 2 of 2 steps and ended, so continuation = {plain(gamma ** 2)} x 8 = {fmt(gamma ** 2 * 8, 3)}.",
            f"Inspect = {fmt(gamma * 4, 3)} + {fmt(gamma ** 2 * 8, 3)} = {fmt(r1['value'], 3)}.",
            "Disabled: the start rule fails, so it runs 0 steps and earns 0.",
            outcome,
        ]
        alt = (f"Two bars. Inspect has an inside reward of {fmt(gamma * 4, 2)} plus a hatched continuation of "
               f"{fmt(gamma ** 2 * 8, 2)}, total {fmt(r1['value'], 2)}. Disabled is an empty dashed bar for a reward of 9 that is never earned, total 0.")
    else:
        if r1["complete"]:
            inside_v = sum(gamma ** t * r for t, r in enumerate(REVIEW["rewards"]))
            steps = [
                f"Inside rewards: {discounted_sum_text(REVIEW['rewards'], gamma)} = {fmt(inside_v, 3)}.",
                f"Continuation: {plain(gamma ** 3)} x 2 = {fmt(gamma ** 3 * 2, 3)}.",
                f"Review-release = {fmt(inside_v, 3)} + {fmt(gamma ** 3 * 2, 3)} = {fmt(r1['value'], 3)}.",
                f"Archive = 1 x 1 = 1.000.",
                outcome,
            ]
            alt = (f"Two bars. Review-release has inside rewards {fmt(inside_v, 2)} plus a hatched continuation {fmt(gamma ** 3 * 2, 2)}, "
                   f"total {fmt(r1['value'], 2)}. Archive is a single bar of 1.")
        else:
            steps = [
                f"Only the first {plural(k)} ran: {discounted_sum_text(REVIEW['rewards'][:k], gamma)} = {fmt(r1['value'], 3)}.",
                "The third step's reward of 8 is never earned and no continuation is added (stipulated).",
                f"Review-release = {fmt(r1['value'], 3)}; archive = 1 x 1 = 1.000.",
                outcome,
            ]
            alt = (f"Two bars. Review-release, stopped after {plural(k)}, has value {fmt(r1['value'], 2)} with no continuation. "
                   "Archive is a single bar of 1.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


SCOPE_DOES_NOT_SETTLE = "What this does not settle"

CHAPTER = {
    "number": 10,
    "title": "Plans Within Plans",
    "subtitle": "A skill that lasts several steps needs a start rule, an inner policy and a stopping rule, and its value must count how long it really ran.",
    "summary": (
        "These four demonstrations follow the chapter's document-release workflow. First the three parts of an option, "
        "then how its value changes with duration, then how time and cost add up differently (and what a stale completion adds), "
        "and last what an interruption does to completion. Every number is a constructed teaching value."
    ),
    "ask_skill": {
        "prompt": (
            "Using my own option, rewards 2, 0 and 5, continuation value 6, discount 0.9 and a deadline of 4 steps, "
            "compute its executed steps, whether it completed, and its value. Then interrupt it after 2 steps and show "
            "which terms disappear, and compare it with a one-step option that pays 1."
        )
    },
    "demos": [
        {
            "id": "C10-D01",
            "title": "An option has three parts",
            "question": "Where may an option start, how long does it run once it has started, and what does a blocked start earn?",
            "equations": [EQ_OPTION],
            "symbols": (
                "o is the option. ℐ (script I) is its initiation set: the states where it may start. The policy π (pi) says which primitive "
                "action to take at each step while it runs; here it checks one record per step. β (beta) is the termination "
                "rule that says when control returns. The state x is the number of records still to check; the duration "
                "is counted in primitive steps. In written sums, x between numbers means multiply."
            ),
            "prediction": "Require at least 4 records and add an early stop when 2 records remain. How long does the option run from x = 6, and can it start from x = 3?",
            "prediction_options": [
                "It runs 6 steps from x = 6, and it cannot start from x = 3.",
                "It runs 2 steps from x = 6, and it cannot start from x = 3.",
                "It runs 4 steps from x = 6, and it cannot start from x = 3.",
                "It runs 4 steps from x = 6, and it can start from x = 3.",
            ],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "From x = 6 the option checks 6 - 2 = 4 records. Row x = 3 is below the start rule, so it is blocked.",
                "incorrect": "Set the start rule to 4 and the early stop to 2 records remaining: from x = 6 the option checks 6 - 2 = 4 records, and row x = 3 is blocked because 3 is below 4.",
            },
            "explanation": (
                "Equation (10.1) lists three separate things. The start rule only decides which rows are blocked. The inner "
                "policy fixes what each step does. The stopping rule decides where each run ends and how many steps it never takes. "
                "Changing the stopping rule changes durations without changing where the option may start, and the reverse."
            ),
            "application": (
                "Before calling a workflow a reusable skill, write down all three: where it may begin, what it does at "
                "each step, and what event hands control back. A workflow with a name but no stated stopping rule has "
                "not yet been defined as an option."
            ),
            "assumptions": (
                "A row of 8 start states, one record checked per step, and a missing approval that is "
                "met at a fixed number of records remaining. A start state at or below the stop level runs to the end, so "
                "durations need not rise steadily with x. Real options act on richer state, and their stopping may "
                "depend on what they see. The start rules and stop levels here are declared examples, not rules from the chapter."
            ),
            "check": "With no early stop and a start rule of at least 4, how many start states are allowed, and how long does the option run from x = 8?",
            "answer": "The allowed states are 4, 5, 6, 7 and 8, so 8 - 4 + 1 = 5 states. From x = 8 it checks one record per step, so it runs 8 x 1 = 8 steps.",
            "provenance": "Constructed example: a record-checking option defined for this reader to illustrate the three parts in Equation (10.1).",
            "source_section": "A skill is not a label",
            "source_anchor": "a-skill-is-not-a-label",
            "misconception": {
                "title": "A named workflow is already an option",
                "text": ("The chapter says \"Retrieve, then decide\" is not an option merely because it has a name in an interface. One must state where it may "
                         "begin, what primitive choices it makes in response to state, and what event returns control. Change the start rule or the stop here and "
                         "watch the rows: each of the three parts changes a different thing."),
            },
            "controls": [
                {"key": "min_records", "label": "Start rule: at least this many records left", "values": [1, 4, 7], "default": 1},
                {"key": "stop_at", "label": "Early stop on a missing approval", "values": [0, 2, 4], "default": 0,
                 "value_labels": ["No early stop", "Stop when 2 records remain", "Stop when 4 records remain"]},
            ],
            "function": "parts_picture",
        },
        {
            "id": "C10-D02",
            "title": "Discount by the steps the option really took",
            "question": "How much does the value rise when the continuation after an option is discounted as if it took one step?",
            "equations": [EQ_VALUE],
            "symbols": (
                "Q(x, o) is the value of starting option o in state x under the parent policy μ (mu). τ (tau) is the number of "
                "primitive steps the option lasts. r is the reward earned at a step inside the option, γ (gamma) the discount "
                "per primitive step, and V is the value of the state where the option ends. In the chapter example the rewards are 2 then 3, "
                "and V is 10; in the workbook transfer case they are 0 then 4, and V is 8. Rewards and the end state are deterministic here, "
                "so the expectation is a single value. In written sums, x between numbers means multiply."
            ),
            "prediction": "With discount 0.9 and a duration of 2, the chapter says 12.8 against 13.7. Make the option last 4 steps. Does the overstatement of the one-step shortcut grow or shrink?",
            "prediction_options": [
                "It stays at 0.9, because the shortcut ignores duration.",
                "It grows, from 0.9 to 2.439.",
                "It shrinks, because later rewards count for less.",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "The overstatement is 10 x (0.9 - 0.9^4) = 10 x (0.9 - 0.6561) = 2.439, up from 10 x (0.9 - 0.81) = 0.9.",
                "incorrect": "Set the duration to 4 with the chapter example and discount 0.9: the overstatement is 10 x (0.9 - 0.9^4) = 2.439, up from 0.9 at duration 2.",
            },
            "stepper": "duration",
            "explanation": (
                "Equation (10.2) discounts each inner reward by how many steps passed and then discounts the value that "
                "remains by the whole duration. The shortcut discounts it by a single step. The longer the option runs, "
                "the more the shortcut overstates the continuation. With these inputs the overstatement is V x (gamma - "
                "gamma^tau): a smaller gamma gives a larger gap at durations 2 to 4, and the gap grows with duration for "
                "either discount. The right panel shows why: the weight at the step where the option ends falls with every extra step."
            ),
            "application": (
                "When comparing a one-step action with a multi-step skill, put both on the same clock. A skill that "
                "takes five steps to return should not get the continuation value of one that returns immediately."
            ),
            "assumptions": (
                "The duration is known and the option always reaches its end. Rewards are paid at primitive steps and "
                "the first is undiscounted. The discount is per step, not per minute: wall-clock time needs its own "
                "model. Steps after the second pay 0 here, a constructed choice to make the duration vary."
            ),
            "check": "With discount 0.9, rewards 2 and 3, and continuation 10, what is the value if the option takes 3 steps and the third step pays 0?",
            "answer": "2 + 0.9 x 3 + 0.81 x 0 + 0.729 x 10 = 2 + 2.7 + 0 + 7.29 = 11.99.",
            "provenance": "Constructed example: the chapter's worked numbers (rewards 2 and 3, continuation 10, discount 0.9, also its Exercise 1) and the workbook transfer case (rewards 0 and 4, continuation 8, discount 0.5), with the duration and discount varied, computed with the laboratory's option function.",
            "source_section": "Value when duration varies",
            "source_anchor": "value-when-duration-varies",
            "misconception": {
                "title": "Discount the continuation as if the option took one step",
                "text": ("The chapter calls that calculation inconsistent: keeping both inner rewards but discounting the continuation by one step "
                         "returns 13.7 instead of 12.8, and it makes delay look too cheap. The exponent must be the number of primitive steps the "
                         "option really used, and the clock must be named: wall-clock time would need its own model."),
            },
            "scope_note": {
                "text": ("Equation (10.2)'s value presumes the option's initiation, policy, and termination are already correctly declared, not "
                         "discovered by the option itself. The numbers are stipulated for teaching, not measured from a deployed system."),
                "source_section": SCOPE_DOES_NOT_SETTLE,
            },
            "controls": [
                {"key": "case", "label": "Case", "values": ["chapter", "transfer"], "default": "chapter",
                 "value_labels": ["Chapter example: rewards 2 and 3, value 10", "Workbook transfer: rewards 0 and 4, value 8"]},
                {"key": "duration", "label": "Duration of the option (primitive steps)", "values": [2, 3, 4], "default": 2},
                {"key": "gamma", "label": "Discount per primitive step", "values": [0.5, 0.9], "default": 0.9},
            ],
            "function": "duration_picture",
        },
        {
            "id": "C10-D03",
            "title": "Release time is not release cost",
            "question": "If one activity runs beside the others, how can the release be early while the cost stays the same, and what does a stale verification add?",
            "equations": [EQ_TOTALS],
            "symbols": (
                "T is the time until release, in minutes, and C the total tool cost, in credits. Draft (2 minutes, 4 "
                "credits), Verify (3, 7) and Publish (1, 2) must run one after another. Audit (4 minutes by default, 3 "
                "credits) is independent. Release needs both Publish and Audit. The longest chain of required "
                "activities sets T; every required activity adds to C. If the source changes from v17 to v18 while Verify runs, "
                "Verify's completion is about v17, so a Revalidate activity against v18 is added; its 3 minutes and 7 credits "
                "are a value set for this reader (it repeats Verify)."
            ),
            "prediction": "Make the audit take 8 minutes, in parallel, with the source unchanged. Which chain sets the release time, and does the cost change?",
            "prediction_options": [
                "Draft, Verify, Publish still set 6 minutes, and the cost stays 16 credits.",
                "The audit sets 8 minutes, and the cost rises to 19 credits.",
                "The audit sets 8 minutes, and the cost stays 16 credits.",
            ],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "T = max{2 + 3 + 1, 8} = max{6, 8} = 8 minutes, so the audit is the longest chain. The cost is still 4 + 7 + 2 + 3 = 16 credits.",
                "incorrect": "Set the audit to 8 minutes in parallel with an unchanged source: T = max{6, 8} = 8 minutes, so the audit is the longest chain, and the cost stays 4 + 7 + 2 + 3 = 16 credits.",
            },
            "explanation": (
                "Time follows the longest dependency chain: a maximum. Cost follows everything that must be paid for: "
                "a sum. The two totals therefore respond to different things. Shortening an activity off the longest "
                "chain buys no time, and running activities in parallel saves time without saving a single credit. A stale "
                "completion adds required work to the chain, so it raises both totals."
            ),
            "application": (
                "When a controller says a workflow is cheap or fast, ask which total is meant. A plan can be fast by "
                "running work side by side; running it in sequence is slower but, in this example, costs the same."
            ),
            "assumptions": (
                "Fixed durations and costs with no waiting for tools, no failures and no shared resource between the "
                "parallel activities. The sequential schedule and the revalidation (3 minutes, 7 credits) are variations added here, not in the "
                "chapter. The chapter's own case is a 4 minute audit in parallel with an unchanged source. Real durations vary and credits may depend on the order of work."
            ),
            "check": "In the parallel schedule with an unchanged source, how long must the audit take before it, rather than the chain Draft, Verify, Publish, sets the release time?",
            "answer": "The chain takes 2 + 3 + 1 = 6 minutes, so the audit must take more than 6 minutes. At exactly 6 the two chains tie. The cost stays 4 + 7 + 2 + 3 = 16 credits.",
            "provenance": "Constructed example: the chapter's release workflow (Equation 10.3, 6 minutes and 16 credits) with the audit length and the schedule varied; the stale completion follows the chapter's v17 and v18 account, and its revalidation cost is defined for this reader.",
            "source_section": "A release workflow has two totals",
            "source_anchor": "a-release-workflow-has-two-totals",
            "misconception": {
                "title": "One step count, or one total, for the whole workflow",
                "text": ("The chapter warns that agent systems often report a single step count although four different counts are mixed: token emissions, "
                         "tool invocations, test runs and delegated tasks, and none determines another. Here two clocks already differ: minutes follow a maximum "
                         "and credits follow a sum. A controller must state which resource its value measures before it combines them."),
            },
            "scope_note": {
                "text": ("Shared-state conflicts between options are named, not solved: a lock, snapshot, or retry rule is a separate "
                         "transition-law decision this chapter does not make."),
                "source_section": SCOPE_DOES_NOT_SETTLE,
            },
            "controls": [
                {"key": "audit_minutes", "label": "Audit duration (minutes)", "values": [4, 6, 8], "default": 4},
                {"key": "mode", "label": "Audit schedule", "values": ["parallel", "after"], "default": "parallel",
                 "value_labels": ["In parallel from minute 0", "After Publish"]},
                {"key": "source", "label": "Source during Verify", "values": ["same", "changed"], "default": "same",
                 "value_labels": ["Unchanged", "Changes from v17 to v18"]},
            ],
            "function": "totals_picture",
        },
        {
            "id": "C10-D04",
            "title": "An interrupted option is scored here without continuation",
            "question": "If an option is stopped early, how much of its value survives, can the preferred option change, and what does an option that cannot start earn?",
            "equations": [EQ_VALUE, EQ_OPTION],
            "symbols": (
                "review-release is a three-step option with rewards -1, -1 and 8 and a continuation value of 2. archive "
                "is a one-step option that pays 1. In the workbook case, inspect has rewards 0 and 4 and a continuation value of 8, and disabled "
                "is a one-step option that would pay 9 but whose start rule fails. γ (gamma) is the discount per primitive step. The deadline is 5 steps "
                "(2 in the workbook case) and does not bind. An interruption stops every option after the chosen number of steps. The "
                "laboratory's rule, used in this demonstration, gives an option that did not reach its end no "
                "continuation, which is the same as setting the value of the state it reached to 0."
            ),
            "prediction": "At discount 0.9, interrupt review-release after 2 steps. What is its value, and which option is now higher?",
            "prediction_options": [
                "Review-release is still worth 6.038, so it stays higher.",
                "Review-release is worth -1.0, so archive (1) is higher.",
                "Review-release is worth 0.9, so it ties with archive.",
                "Review-release is worth -1.9, so archive (1) is higher.",
            ],
            "prediction_answer": 3,
            "prediction_feedback": {
                "correct": "Only two rewards are earned: 1 x (-1) + 0.9 x (-1) = -1.9, with no continuation, so archive (1) is higher.",
                "incorrect": "Choose 'interrupted after 2 steps' at discount 0.9: only two rewards are earned, 1 x (-1) + 0.9 x (-1) = -1.9, with no continuation, so archive (1) is higher.",
            },
            "explanation": (
                "Equation (10.2) adds γ^τ V for the state where the option ends. In this demonstration the "
                "laboratory stipulates V = 0 for an interrupted option, so only the rewards of the steps that ran are "
                "counted; Equation (10.2) itself would add γ^τ V at the state actually reached, which is "
                "not computed here. The interruption does not change the payoff of releasing; it removes access to the "
                "later reward. An option whose start rule fails (the disabled option) is the extreme case: it runs no steps at all."
            ),
            "application": (
                "A parent controller should treat an interrupted skill as a different outcome from a finished one and "
                "plan from the state it actually reached, with a stated cancellation or recovery step."
            ),
            "assumptions": (
                "Rewards, durations and the interruption point are given, not random. The chapter warns that an "
                "interruption can leave effects behind (spend, writes) and that cancellation needs an acknowledgement. "
                "This calculation shows only the value of the executed steps (the reached state is valued at 0 by stipulation) "
                "and says nothing about how to clean up."
            ),
            "check": "At discount 0.9, what is the value of review-release if it is stopped after 1 step?",
            "answer": "Only the first reward is earned and nothing is discounted yet: 1 x (-1) = -1. This demonstration adds no continuation, so archive (1) is higher.",
            "provenance": "Constructed example: the laboratory's review-release and archive options, using the laboratory's example values (6.038 complete, -1.9 interrupted after 2 steps, at discount 0.9), a second discount, and the workbook transfer case (inspect worth 4 at discount 0.5, a disabled option worth 0), computed with the laboratory's option function.",
            "source_section": "Interruption changes what completion means",
            "source_anchor": "interruption-changes-what-completion-means",
            "misconception": {
                "title": "A timeout or a cancel request means the option stopped",
                "text": ("The chapter says timeout alone neither acknowledges cancellation nor fences off outstanding effects, and that \"cancel requested\" is not proof of "
                         "non-application. Without an acknowledgement the parent loses the right to assume the option ended; the stopped option here is only "
                         "scored as stopped because the interruption point is given."),
            },
            "scope_note": {
                "text": ("This chapter does not prove that a compact completion interface loses no distinction a later decision needs; that check "
                         "belongs to the interface designer, not to the option contract itself."),
                "source_section": SCOPE_DOES_NOT_SETTLE,
            },
            "controls": [
                {"key": "case", "label": "Case", "values": ["none", "two", "one", "transfer"], "default": "none",
                 "value_labels": ["No interruption", "Interrupted after 2 steps", "Interrupted after 1 step",
                                  "Workbook case: inspect and a disabled option"]},
                {"key": "gamma", "label": "Discount per primitive step", "values": [0.9, 0.5], "default": 0.9},
            ],
            "function": "interruption_picture",
        },
    ],
}

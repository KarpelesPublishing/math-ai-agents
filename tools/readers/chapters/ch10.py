"""Chapter 10 reader: Plans Within Plans.

Four demonstrations built on Equations (10.1) to (10.3). Demonstrations 2 and
4 call the laboratory's own option-duration function
(math_ai_agents.chapters.ch10.evaluate), so the reader, the notebook and the
chapter skill agree. Demonstration 2 uses the chapter's worked numbers
(rewards 2 and 3, continuation 10, discount 0.9, value 12.8 against 13.7);
Demonstration 3 uses the chapter's release workflow (6 minutes, 16 credits);
Demonstration 4 uses the laboratory's review-release example (6.038 and the
interrupted -1.9). Every number is a constructed teaching value.
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


# Demonstration 1: the three parts of an option

RECORDS = list(range(1, 9))  # start states: records still to check
EXAMPLE_START = 6


def option_duration(x, stop_at):
    """Steps from start state x when each step checks one record.

    The option stops when no record is left, or earlier when a missing approval
    is met with stop_at records left (stop_at = 0 means no early stop). The
    stop is tested after each step, so a start state at or below stop_at runs
    to the end.
    """
    return x - stop_at if 0 < stop_at < x else x


def parts_picture(min_records=1, stop_at=0):
    allowed = [x for x in RECORDS if x >= min_records]
    taus = [option_duration(x, stop_at) for x in RECORDS]
    fig, ax = new_figure(height=4.0)
    for x, tau in zip(RECORDS, taus):
        if x in allowed:
            ax.bar(x, tau, width=0.62, color=PALETTE["teal"])
        else:
            ax.bar(x, tau, width=0.62, color="white", edgecolor=PALETTE["grey"], hatch="///", linewidth=1.2)
        ax.text(x, tau + 0.25, str(tau), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    ax.text(0.5, 9.6, "solid bar: start allowed (state is in I)\nhatched bar: start not allowed", ha="left", va="top",
            fontsize=10.5, color=PALETTE["ink"])
    ax.set_xticks(RECORDS)
    ax.set_xlim(0.4, 8.6)
    ax.set_ylim(0, 10)
    ax.set_xlabel("State x: records still to check when the option starts")
    ax.set_ylabel("Duration (primitive steps)")
    stop_text = "stops only when no record is left" if stop_at == 0 else f"also stops when {stop_at} records remain"
    ax.set_title(f"Start needs x of at least {min_records}; the option {stop_text}", fontsize=11.5)
    ax.grid(axis="x", alpha=0)
    longest = max(option_duration(x, stop_at) for x in allowed)
    in_set = f"x = {allowed[0]} to {allowed[-1]}"
    metrics = {
        "Initiation set": in_set,
        "Start states allowed": f"{len(allowed)} of {len(RECORDS)}",
        f"Duration from x = {EXAMPLE_START}": f"{option_duration(EXAMPLE_START, stop_at)} steps",
        "Longest duration from an allowed start": f"{longest} steps",
    }
    tau6 = option_duration(EXAMPLE_START, stop_at)
    if stop_at and stop_at < EXAMPLE_START:
        calc = (f"Starting with {EXAMPLE_START} records left and stopping when {stop_at} remain, the option checks "
                f"{EXAMPLE_START} - {stop_at} = {tau6} records, so its duration is {tau6} steps.")
    else:
        calc = (f"Starting with {EXAMPLE_START} records left and checking one per step, the option runs "
                f"{EXAMPLE_START} x 1 = {tau6} steps.")
    if min_records > 1:
        gate = (f"The start rule x of at least {min_records} keeps the states {allowed[0]} to {allowed[-1]} and blocks "
                f"{min_records - 1} of the 8 states, so the controller may not select this option there.")
    else:
        gate = "The start rule x of at least 1 allows every state shown."
    if stop_at:
        stop = (f"A start state with {stop_at} or fewer records left never meets the missing approval after a step, "
                f"so it runs to the end: from x = {stop_at} the duration is {option_duration(stop_at, stop_at)}.")
    else:
        stop = "Without an early stop, the duration always equals the number of records."
    interpretation = f"{calc} {gate} {stop} The termination rule, not only the start state, fixes the duration."
    return fig, metrics, interpretation


# Demonstration 2: value when duration varies

BOOK_REWARDS = [2.0, 3.0]
CONTINUATION = 10.0


def lab_option_value(duration, gamma):
    """Equation (10.2) for a completed option, computed by the laboratory's evaluate()."""
    rewards = BOOK_REWARDS + [0.0] * (duration - len(BOOK_REWARDS))
    out = evaluate({
        "discount": float(gamma), "deadline": 10,
        "options": [{"name": "check", "initiation": True, "rewards": rewards, "terminated": True,
                     "continuation_value": CONTINUATION}],
    })
    row = out["tables"][0]
    return rewards, row["value"], row["continuation_discount"]


def duration_picture(duration=2, gamma=0.9):
    rewards, value, cont_discount = lab_option_value(duration, gamma)
    inside = sum(gamma ** t * r for t, r in enumerate(rewards))
    continuation = value - inside
    one_step_cont = gamma * CONTINUATION
    one_step_value = inside + one_step_cont
    overstatement = one_step_value - value
    fig, ax = new_figure(height=3.9)
    rows = [
        ("Rewards inside the option", 0.0, inside, PALETTE["navy"], None),
        ("Continuation, gamma^tau", inside, continuation, PALETTE["teal"], None),
        ("Value by Equation (10.2)", 0.0, value, PALETTE["teal"], None),
        ("Continuation, gamma^1", inside, one_step_cont, "white", "///"),
        ("Value, one-step error", 0.0, one_step_value, "white", "///"),
    ]
    top = max(value, one_step_value)
    for i, (label, left, width, color, hatch) in enumerate(rows):
        y = len(rows) - 1 - i
        edge = PALETTE["terracotta"] if hatch else color
        ax.barh(y, width, left=left, height=0.58, color=color, edgecolor=edge, hatch=hatch, linewidth=1.2)
        shown = width if left == 0.0 else width
        ax.text(left + width + 0.25, y, fmt(shown, 3), ha="left", va="center", fontsize=11, color=PALETTE["ink"])
    ax.set_yticks(range(len(rows) - 1, -1, -1), [r[0] for r in rows])
    ax.set_xlim(0, top * 1.22 + 1)
    ax.set_xlabel("Value (constructed units)")
    ax.set_ylabel("Part of the calculation")
    ax.grid(axis="y", alpha=0)
    ax.set_title(f"Option lasting {duration} steps, discount {fmt(gamma, 1)}; hatched rows treat it as one step", fontsize=11.5)
    metrics = {
        "Rewards inside the option": fmt(inside, 3),
        f"Continuation discounted by gamma^{duration}": fmt(continuation, 3),
        "Value by Equation (10.2)": fmt(value, 3),
        "Value if discounted as one step": fmt(one_step_value, 3),
        "Overstatement": fmt(overstatement, 3),
    }
    written = discounted_sum_text(rewards, gamma, CONTINUATION, duration)
    later = duration - 2
    steps_note = "" if duration == 2 else (
        f" The steps after the second pay 0, so the continuation is pushed {later} {'step' if later == 1 else 'steps'} later.")
    interpretation = (
        f"Value = {written} = {fmt(value, 3)}. Treating the option as one step instead gives "
        f"{fmt(inside, 3)} + {plain(gamma)} x 10 = {fmt(one_step_value, 3)}, which is {fmt(overstatement, 3)} too high."
        f"{steps_note} The exponent counts the steps the option really used, so a longer option has its continuation "
        "worth less. Ignoring duration makes delay look too cheap."
    )
    return fig, metrics, interpretation


# Demonstration 3: two totals

ACTIVITIES = [("Draft", 2, 4), ("Verify", 3, 7), ("Publish", 1, 2)]  # name, minutes, credits
AUDIT_CREDITS = 3


def schedule(audit_minutes, mode):
    """Start and end minute of every activity, and the release time."""
    chain, t = {}, 0
    for name, minutes, _ in ACTIVITIES:
        chain[name] = (t, t + minutes)
        t += minutes
    audit_start = 0 if mode == "parallel" else t
    chain["Audit"] = (audit_start, audit_start + audit_minutes)
    release = max(end for _, end in chain.values())
    return chain, release


def totals_picture(audit_minutes=4, mode="parallel"):
    chain, release = schedule(audit_minutes, mode)
    credits = {name: c for name, _, c in ACTIVITIES}
    credits["Audit"] = AUDIT_CREDITS
    total_credits = sum(credits.values())
    chain_minutes = sum(m for _, m, _ in ACTIVITIES)
    if mode == "parallel":
        chain_critical = chain_minutes >= audit_minutes
        audit_critical = audit_minutes >= chain_minutes
    else:
        chain_critical = audit_critical = True
    critical = {"Draft": chain_critical, "Verify": chain_critical, "Publish": chain_critical, "Audit": audit_critical}
    fig, ax = new_figure(height=4.1)
    names = ["Draft", "Verify", "Publish", "Audit"]
    for i, name in enumerate(names):
        start, end = chain[name]
        hot = critical[name]
        on_navy = name == "Audit"
        ax.barh(i, end - start, left=start, height=0.58, color=PALETTE["navy"] if on_navy else PALETTE["teal"],
                edgecolor=("white" if on_navy else PALETTE["ink"]) if hot else "none",
                hatch="///" if hot else None, linewidth=1.2)
        if hot and on_navy:
            # light hatch on the dark fill, plus a dark outline so the bar edge stays crisp
            ax.barh(i, end - start, left=start, height=0.58, fill=False, edgecolor=PALETTE["ink"], linewidth=2.0)
    ax.set_yticks(range(4), [f"{n} ({credits[n]} credits)" for n in names])
    ax.set_ylim(3.7, -1.0)
    ax.axvline(release, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.6)
    right_side = release > 8
    label_point(ax, release, -0.62, f"release done at minute {release}", color=PALETTE["terracotta"],
                dx=-5 if right_side else 5, dy=0, ha="right" if right_side else "left", va="center").set_bbox(BOX)
    ax.set_xlim(0, 16)
    ax.set_xlabel("Minutes from the start")
    ax.set_ylabel("Activity (tool credits)")
    ax.grid(axis="y", alpha=0)
    label = "Audit in parallel" if mode == "parallel" else "Audit after Publish"
    ax.set_title(f"{label}, audit takes {audit_minutes} min: {release} min, {total_credits} credits\nhatched bars lie on the longest chain",
                 fontsize=11.5)
    if mode == "parallel":
        if chain_critical and audit_critical:
            which = "Draft, Verify, Publish and Audit (tie)"
        elif chain_critical:
            which = "Draft, Verify, Publish"
        else:
            which = "Audit"
    else:
        which = "all four, in sequence"
    metrics = {
        "Release time": f"{release} minutes",
        "Total tool cost": f"{total_credits} credits",
        "Longest chain": which,
        "Chain Draft, Verify, Publish": f"{chain_minutes} minutes",
    }
    if mode == "parallel":
        calc = f"Time T = max{{2 + 3 + 1, {audit_minutes}}} = max{{{chain_minutes}, {audit_minutes}}} = {release} minutes."
        if chain_critical and audit_critical:
            tie = (" The two chains tie at 6 minutes, so both are on the longest chain: shortening one of them alone "
                   "would not make the release earlier.")
        elif chain_critical:
            tie = f" The audit has {chain_minutes - audit_minutes} minutes of slack, so speeding it up would not release earlier."
        else:
            tie = (f" Now the audit is the longest chain, so the release waits {audit_minutes - chain_minutes} minutes "
                   "for it after Publish is finished.")
    else:
        calc = f"Time T = 2 + 3 + 1 + {audit_minutes} = {release} minutes, because nothing runs side by side."
        tie = " Running the audit in parallel would have cut the delay without changing the credits."
    interpretation = (f"{calc} Cost C = 4 + 7 + 2 + 3 = {total_credits} credits in every schedule, because every required "
                      f"activity is paid for.{tie}")
    return fig, metrics, interpretation


# Demonstration 4: interruption and completion

REVIEW = {"name": "review-release", "rewards": [-1.0, -1.0, 8.0], "continuation": 2.0}
ARCHIVE = {"name": "archive", "rewards": [1.0], "continuation": 0.0}


def interruption_picture(steps_allowed=3, gamma=0.9):
    options = [
        {"name": o["name"], "initiation": True, "rewards": o["rewards"], "terminated": True,
         "continuation_value": o["continuation"]}
        for o in (REVIEW, ARCHIVE)
    ]
    data = {"discount": float(gamma), "deadline": 5, "options": options}
    if steps_allowed < 3:
        data["interrupt_after"] = int(steps_allowed)
    out = evaluate(data)
    rows = {r["name"]: r for r in out["tables"]}
    best = out["metrics"]["best_executed_value"]
    fig, ax = new_figure(height=4.2)
    ticks = []
    for x, spec in zip((0.0, 1.3), (REVIEW, ARCHIVE)):
        row = rows[spec["name"]]
        cont = row["continuation_discount"] * spec["continuation"] if row["complete"] else 0.0
        inside = row["value"] - cont
        ax.bar(x, inside, width=0.5, color=PALETTE["navy"])
        if row["complete"] and cont != 0:
            ax.bar(x, cont, bottom=inside, width=0.5, color="white", edgecolor=PALETTE["teal"], hatch="///", linewidth=1.4)
        if row["complete"] and cont != 0:
            label_point(ax, x - 0.27, inside + cont / 2, f"continuation\n+{fmt(cont, 3)}", dx=-4, dy=0, ha="right",
                        va="center", size=10.5, color=PALETTE["teal"]).set_bbox(BOX)
        ax.plot([x - 0.25, x + 0.25], [row["value"]] * 2, color=PALETTE["ink"], linewidth=2.2)
        tag = ", chosen" if spec["name"] == best else ""
        label_point(ax, x + 0.25, row["value"], f"value {fmt(row['value'], 3)}{tag}", dx=6, dy=0, ha="left", va="center",
                    size=11).set_bbox(BOX)
        status = "completed" if row["complete"] else "not completed"
        unit = "step" if row["duration"] == 1 else "steps"
        ticks.append(f"{spec['name']}\n{row['executed']} of {row['duration']} {unit}, {status}")
    ax.axhline(0, color=PALETTE["grey"], linewidth=1)
    ax.set_xticks([0.0, 1.3], ticks)
    ax.set_xlim(-0.95, 2.7)
    # a tighter vertical range at the heavy discount, where every value is small
    ax.set_ylim(*((-4, 8) if gamma >= 0.9 else (-2.5, 3)))
    ax.set_xlabel("Option, steps that ran, and whether it reached its end")
    ax.set_ylabel("Discounted value (constructed units)")
    ax.grid(axis="x", alpha=0)
    ax.bar([5], [0], color=PALETTE["navy"], label="rewards in the steps that ran")
    ax.bar([5], [0], color="white", edgecolor=PALETTE["teal"], hatch="///", label="continuation, only after completion (stipulated)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.30), ncol=1, frameon=False, fontsize=10.5)
    if steps_allowed == 3:
        stop_text = "no interruption"
    else:
        stop_text = f"interrupted after {steps_allowed} {'step' if steps_allowed == 1 else 'steps'}"
    ax.set_title(f"Discount {fmt(gamma, 1)}; {stop_text}", fontsize=11.5)
    rr, ar = rows["review-release"], rows["archive"]
    metrics = {
        "review-release value": fmt(rr["value"], 3),
        "archive value": fmt(ar["value"], 3),
        "review-release completed": "yes" if rr["complete"] else "no",
        "Higher executed value": best,
    }
    k = rr["executed"]
    if rr["complete"]:
        written = discounted_sum_text(REVIEW["rewards"], gamma, REVIEW["continuation"], 3)
        note = ("The option reached its end, so the continuation value 2 is added after discounting by "
                f"{plain(gamma)} x {plain(gamma)} x {plain(gamma)} = {plain(gamma ** 3)}.")
    else:
        written = discounted_sum_text(REVIEW["rewards"][:k], gamma)
        note = (f"The option stopped after {k} of 3 steps. The 8 that the third step would pay is never earned and no "
                "continuation is added here (the reached state is valued at 0 by stipulation).")
    if best == "archive":
        outcome = (f"Archive is higher, {fmt(ar['value'], 3)} against {fmt(rr['value'], 3)}.")
    else:
        outcome = (f"Review-release is higher, {fmt(rr['value'], 3)} against {fmt(ar['value'], 3)} for archive.")
    if steps_allowed == 3 and gamma == 0.5:
        outcome += " Here the full option is completed yet loses, because heavy discounting shrinks its late reward."
    archive_note = ""
    if steps_allowed < 3:
        archive_note = (f" Archive needs one step, so an interruption after {steps_allowed} "
                        f"{'step' if steps_allowed == 1 else 'steps'} does not touch it.")
    interpretation = f"Review-release = {written} = {fmt(rr['value'], 3)}. {note} {outcome}{archive_note}"
    return fig, metrics, interpretation


CHAPTER = {
    "number": 10,
    "title": "Plans Within Plans",
    "subtitle": "A skill that lasts several steps needs a start rule, an inner policy and a stopping rule, and its value must count how long it really ran.",
    "summary": (
        "These four demonstrations follow the chapter's document-release workflow. First the three parts of an option, "
        "then how its value changes with duration, then how time and cost add up differently, and last what an "
        "interruption does to completion. Every number is a constructed teaching value."
    ),
    "demos": [
        {
            "id": "C10-D01",
            "title": "An option has three parts",
            "question": "Where may an option start, and how long does it run once it has started?",
            "equations": [EQ_OPTION],
            "symbols": (
                "o is the option. \u2110 (script I) is its initiation set: the states where it may start. The policy \u03c0 (pi) says which primitive "
                "action to take at each step while it runs; here it checks one record per step. \u03b2 (beta) is the termination "
                "rule that says when control returns. The state x is the number of records still to check; the duration "
                "is counted in primitive steps. In written sums, x between numbers means multiply."
            ),
            "prediction": "Require at least 4 records and add an early stop when 2 records remain. How long does the option run from x = 6, and can it start from x = 3?",
            "explanation": (
                "Equation (10.1) lists three separate things. The start rule only decides which bars are solid. The inner "
                "policy fixes what each step does. The stopping rule decides where each bar ends. Changing the stopping "
                "rule changes durations without changing where the option may start, and the reverse."
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
                "depend on what they see. The start rule here is a declared example, not a rule from the chapter."
            ),
            "check": "With no early stop and a start rule of at least 4, how many start states are allowed, and how long does the option run from x = 8?",
            "answer": "The allowed states are 4, 5, 6, 7 and 8, so 8 - 4 + 1 = 5 states. From x = 8 it checks one record per step, so it runs 8 x 1 = 8 steps.",
            "provenance": "Constructed example: a record-checking option defined for this reader to illustrate the three parts in Equation (10.1).",
            "source_section": "A skill is not a label",
            "source_anchor": "a-skill-is-not-a-label",
            "controls": [
                {"key": "min_records", "label": "Start rule: at least this many records left", "values": [1, 4], "default": 1},
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
                "Q(x, o) is the value of starting option o in state x under the parent policy \u03bc (mu). \u03c4 (tau) is the number of "
                "primitive steps the option lasts. r is the reward earned at a step inside the option, \u03b3 (gamma) the discount "
                "per primitive step, and V is the value of the state where the option ends. Here the rewards are 2 then 3, "
                "and V is 10. Rewards and the end state are deterministic here, so the expectation is a single value. "
                "In written sums, x between numbers means multiply."
            ),
            "prediction": "With discount 0.9 and a duration of 2, the chapter says 12.8 against 13.7. Make the option last 4 steps. Does the overstatement of the one-step shortcut grow or shrink?",
            "explanation": (
                "Equation (10.2) discounts each inner reward by how many steps passed and then discounts the value that "
                "remains by the whole duration. The shortcut discounts it by a single step. The longer the option runs, "
                "the more the shortcut overstates the continuation. With these inputs the overstatement is 10 x (gamma - "
                "gamma^tau): a smaller gamma gives a larger gap at durations 2 to 4, and the gap grows with duration for "
                "either discount. The reader shows durations 2 to 4 only."
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
            "provenance": "Constructed example: the chapter's worked numbers (rewards 2 and 3, continuation 10, discount 0.9) with the duration and discount varied, computed with the laboratory's option function.",
            "source_section": "Value when duration varies",
            "source_anchor": "value-when-duration-varies",
            "controls": [
                {"key": "duration", "label": "Duration of the option (primitive steps)", "values": [2, 3, 4], "default": 2},
                {"key": "gamma", "label": "Discount per primitive step", "values": [0.5, 0.9], "default": 0.9},
            ],
            "function": "duration_picture",
        },
        {
            "id": "C10-D03",
            "title": "Release time is not release cost",
            "question": "If one activity runs beside the others, how can the release be early while the cost stays the same?",
            "equations": [EQ_TOTALS],
            "symbols": (
                "T is the time until release, in minutes, and C the total tool cost, in credits. Draft (2 minutes, 4 "
                "credits), Verify (3, 7) and Publish (1, 2) must run one after another. Audit (4 minutes by default, 3 "
                "credits) is independent. Release needs both Publish and Audit. The longest chain of required "
                "activities sets T; every required activity adds to C."
            ),
            "prediction": "Make the audit take 8 minutes. Which chain sets the release time, and does the cost change?",
            "explanation": (
                "Time follows the longest dependency chain: a maximum. Cost follows everything that must be paid for: "
                "a sum. The two totals therefore respond to different things. Shortening an activity off the longest "
                "chain buys no time, and running activities in parallel saves time without saving a single credit."
            ),
            "application": (
                "When a controller says a workflow is cheap or fast, ask which total is meant. A plan can be fast by "
                "running work side by side; running it in sequence is slower but, in this example, costs the same."
            ),
            "assumptions": (
                "Fixed durations and costs with no waiting for tools, no failures and no shared resource between the "
                "parallel activities. The sequential schedule is a variation added here, not in the chapter. The "
                "chapter's own case is a 4 minute audit in parallel. Real durations vary and credits may depend on the order of work."
            ),
            "check": "In the parallel schedule, how long must the audit take before it, rather than the chain Draft, Verify, Publish, sets the release time?",
            "answer": "The chain takes 2 + 3 + 1 = 6 minutes, so the audit must take more than 6 minutes. At exactly 6 the two chains tie. The cost stays 4 + 7 + 2 + 3 = 16 credits.",
            "provenance": "Constructed example: the chapter's release workflow (Equation 10.3, 6 minutes and 16 credits) with the audit length and the schedule varied.",
            "source_section": "A release workflow has two totals",
            "source_anchor": "a-release-workflow-has-two-totals",
            "controls": [
                {"key": "audit_minutes", "label": "Audit duration (minutes)", "values": [2, 4, 6, 8], "default": 4},
                {"key": "mode", "label": "Audit schedule", "values": ["parallel", "after"], "default": "parallel",
                 "value_labels": ["In parallel from minute 0", "After Publish"]},
            ],
            "function": "totals_picture",
        },
        {
            "id": "C10-D04",
            "title": "An interrupted option is scored here without continuation",
            "question": "If an option is stopped early, how much of its value survives, and can the preferred option change?",
            "equations": [EQ_VALUE],
            "symbols": (
                "review-release is a three-step option with rewards -1, -1 and 8 and a continuation value of 2. archive "
                "is a one-step option that pays 1. \u03b3 (gamma) is the discount per primitive step. The deadline is 5 steps and "
                "does not bind here. An interruption stops every option after the chosen number of steps. The "
                "laboratory's rule, used in this demonstration, gives an option that did not reach its end no "
                "continuation, which is the same as setting the value of the state it reached to 0."
            ),
            "prediction": "At discount 0.9, interrupt review-release after 2 steps. What is its value, and which option is now higher?",
            "explanation": (
                "Equation (10.2) adds \u03b3^\u03c4 V for the state where the option ends. In this demonstration the "
                "laboratory stipulates V = 0 for an interrupted option, so only the rewards of the steps that ran are "
                "counted; Equation (10.2) itself would add \u03b3^\u03c4 V at the state actually reached, which is "
                "not computed here. The interruption does not change the payoff of releasing; it removes access to the "
                "later reward."
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
            "provenance": "Constructed example: the laboratory's review-release and archive options, using the laboratory's example values (6.038 complete, -1.9 interrupted after 2 steps, at discount 0.9) and a second discount, computed with the laboratory's option function.",
            "source_section": "Interruption changes what completion means",
            "source_anchor": "interruption-changes-what-completion-means",
            "controls": [
                {"key": "steps_allowed", "label": "Steps allowed before the interruption", "values": [3, 2, 1], "default": 3,
                 "value_labels": ["3 (no interruption)", "2 steps", "1 step"]},
                {"key": "gamma", "label": "Discount per primitive step", "values": [0.9, 0.5], "default": 0.9},
            ],
            "function": "interruption_picture",
        },
    ],
}

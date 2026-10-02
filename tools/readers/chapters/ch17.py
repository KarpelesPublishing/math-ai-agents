"""Chapter 17 reader: State and Consequence.

Four demonstrations built on Equations (17.1) to (17.4). Demonstration 1 counts
effects with the laboratory's own effect ledger
(math_ai_agents.chapters.ch17.evaluate) and Demonstration 3 takes its expected
duplicate harm from the same function, so the reader, the notebook and the
chapter skill agree. Demonstrations 2 and 4 are direct closed forms. Every
number is a constructed teaching value.
"""
import math

import numpy as np

from math_ai_agents.chapters.ch17 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure

EQ_IDEMPOTENT = (
    r"\operatorname{eff}_{I}\!\big(\operatorname{eff}(T,\operatorname{eff}(T,x))\big) \;=\; "
    r"\operatorname{eff}_{I}\!\big(\operatorname{eff}(T,x)\big) \qquad\text{for every reachable } x ."
)
EQ_BELIEF = (
    r"\mathbf{b}'(\text{applied}) \;=\; \frac{\operatorname{Obs}(\varnothing \mid \text{applied})\;\Pr(\text{applied})}"
    r"{\begin{gathered}\operatorname{Obs}(\varnothing \mid \text{applied})\,\Pr(\text{applied}) \\"
    r"{}+\; \operatorname{Obs}(\varnothing \mid \text{not applied})\,\Pr(\text{not applied})\end{gathered}}."
)
EQ_RETRY = (
    r"\operatorname{EU}(\text{retry}) - \operatorname{EU}(\text{decline}) \;=\; (1-\beta)\,c_{\text{miss}} \;-\; \beta\,c_{\text{dup}} ."
)
EQ_REPEAT_SET = (
    r"\operatorname{Rep}(x) \;=\; \Big\{\, T \;:\; \operatorname{Ready}(T,x)\;\land\;\big[\text{(17.1) holds for this request}"
    r"\;\lor\;\operatorname{Absent}(T,x)\;\lor\;\operatorname{Restored}(T,x)\big] \,\Big\}."
)

START = 100.0   # constructed starting value of the record
STEP = 50.0     # constructed amount a charge adds, or the target of a set (150)
TARGET = 150.0


# Demonstration 1

OPERATIONS = {
    "put": "Set the record to 150 (PUT-like)",
    "delete": "Delete the record (DELETE-like)",
    "charge": "Add a charge of 50, no key",
    "charge_key": "Add a charge of 50, key stored",
}


def lab_effects(n_requests, idempotent):
    """Number of durable effects after n identical requests, from the laboratory's effect ledger."""
    events = [
        {"kind": "request", "key": "op-1", "payload": "charge-50", "effect": True, "ack": i == n_requests - 1}
        for i in range(n_requests)
    ]
    out = evaluate({
        "idempotent": idempotent, "events": events, "verify_cost": 1, "retry_cost": 0.2,
        "effect_probability": 0.5, "duplicate_cost": 1,
    })
    return int(out["metrics"]["effects"])


def record_after(operation, k):
    """Intended coordinate (the record's value, 0 when absent) after k identical requests."""
    if k == 0:
        return START
    if operation == "put":
        return TARGET
    if operation == "delete":
        return 0.0
    if operation == "charge":
        return START + STEP * lab_effects(k, False)
    return START + STEP * lab_effects(k, True)


def repeat_picture(operation="put", requests=2):
    n = int(requests)
    values = [record_after(operation, k) for k in range(n + 1)]
    holds = all(math.isclose(values[k], values[1]) for k in range(2, n + 1))
    fig, (left, right) = new_figure(ncols=2, height=4.3)
    ks = np.arange(n + 1)
    for k in ks:
        if k == 0:
            color, hatch = "#8fa3b8", None
        elif k == 1 or math.isclose(values[k], values[1]):
            color, hatch = PALETTE["teal"], None
        else:
            color, hatch = PALETTE["terracotta"], "///"
        left.bar(k, values[k], color=color, hatch=hatch, edgecolor="white" if hatch is None else PALETTE["ink"], width=0.62)
        text = "absent" if (operation == "delete" and k > 0) else fmt(values[k], 0)
        left.text(k, values[k] + 6, text, ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    left.set_xticks(ks, ["start"] + [f"after {k}" for k in range(1, n + 1)])
    left.set_ylim(0, 290)
    left.set_xlabel("Identical requests sent")
    left.set_ylabel("Record value (0 means absent)")
    left.set_title("Intended effect (the part Equation 17.1 compares)", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    right.bar(ks[1:], ks[1:], color=PALETTE["navy"], width=0.62)
    for k in ks[1:]:
        right.text(k, k + 0.12, str(int(k)), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    right.set_xticks(ks[1:], [f"after {k}" for k in range(1, n + 1)])
    right.set_ylim(0, 3.8)
    right.set_yticks([0, 1, 2, 3])
    right.set_xlabel("Identical requests sent")
    right.set_ylabel("Log lines kept by the service")
    right.set_title("Outside the intended effect", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    label_after = f"{n} requests"
    if operation == "put":
        calc = (f"Every request sets the record to 150, so the record after {n} requests minus the record after one is "
                f"{fmt(values[n], 0)} - {fmt(values[1], 0)} = {fmt(values[n] - values[1], 0)}.")
        responses = "same answer each time"
    elif operation == "delete":
        calc = (f"The record is gone after the first request and stays gone: after {n} requests minus after one is "
                f"{fmt(values[n], 0)} - {fmt(values[1], 0)} = {fmt(values[n] - values[1], 0)}.")
        responses = "first: deleted; repeats: not found"
    elif operation == "charge":
        calc = (f"Each request adds a charge, so after one the record is {fmt(START, 0)} + 1 x {fmt(STEP, 0)} = {fmt(values[1], 0)} "
                f"and after {n} it is {fmt(START, 0)} + {n} x {fmt(STEP, 0)} = {fmt(values[n], 0)}, a difference of "
                f"{fmt(values[n], 0)} - {fmt(values[1], 0)} = {fmt(values[n] - values[1], 0)}.")
        responses = "each request reports a charge"
    else:
        calc = (f"The stored key makes the service count the charge once, so after {n} requests the record is "
                f"{fmt(START, 0)} + 1 x {fmt(STEP, 0)} = {fmt(values[n], 0)}, and {fmt(values[n], 0)} - {fmt(values[1], 0)} = "
                f"{fmt(values[n] - values[1], 0)} against the state after one request.")
        responses = "repeats return the saved result"
    if holds:
        verdict = (f"Equation (17.1) holds here: one request and {label_after} leave the same intended effect. "
                   f"The service still wrote {n} log lines, which sit outside the intended-effect coordinate.")
    else:
        verdict = (f"Equation (17.1) fails here: {label_after} leave the record at {fmt(values[n], 0)}, not {fmt(values[1], 0)}, "
                   "so a retry after a lost reply is not safe on this evidence alone.")
    metrics = {
        "Record after one request": "absent" if operation == "delete" else fmt(values[1], 0),
        f"Record after {n} requests": "absent" if operation == "delete" else fmt(values[n], 0),
        "Equation (17.1)": "holds" if holds else "fails",
        "Log lines written": str(n),
        "Replies": responses,
    }
    interpretation = f"{calc} {verdict} A reply can differ without breaking the equation, because the equation compares effects, not replies."
    return fig, metrics, interpretation


# Demonstration 2

SILENCE_IF_NOT_APPLIED = 0.5  # constructed likelihood of silence when the request did not apply


def posterior(prior, silence_if_applied, silence_if_not=SILENCE_IF_NOT_APPLIED):
    """Equation (17.2). Returns None when silence has probability zero in both worlds."""
    num = silence_if_applied * prior
    den = num + silence_if_not * (1 - prior)
    return None if den == 0 else num / den


def belief_picture(prior=0.5, silence_if_applied=0.5):
    prior = float(prior)
    la = float(silence_if_applied)
    ln = SILENCE_IF_NOT_APPLIED
    post = posterior(prior, la, ln)
    grid = np.linspace(0, 1, 201)
    curve = np.array([posterior(p, la, ln) for p in grid])
    fig, ax = new_figure(height=4.3)
    ax.plot([0, 1], [0, 1], linestyle=":", color=PALETTE["grey"], linewidth=1.4)
    ax.plot(grid, curve, color=PALETTE["teal"], linewidth=2.2)
    ax.plot([prior, prior], [prior, post], color=PALETTE["gold"], linewidth=2.0, linestyle="dashed")
    ax.plot([prior], [prior], "s", color=PALETTE["navy"], markersize=8)
    ax.plot([prior], [post], "o", color=PALETTE["terracotta"], markersize=9)
    box = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
    equal = math.isclose(post, prior, abs_tol=1e-12)
    label_point(ax, 0.02, 1.1, "dotted line: silence changes nothing", color=PALETTE["grey"], dx=0, dy=0, va="top")
    label_point(ax, 0.98, 0.04, "solid line: belief after silence", color=PALETTE["teal"], dx=0, dy=0, ha="right", va="bottom")
    on_left = prior < 0.5
    if prior > 0.9:
        # the before and after markers nearly coincide at the right edge: name both in one callout placed in the empty
        # part of the plot, with an arrow to the markers
        spot = (0.5, 0.3) if post >= prior else (0.18, 0.78)
        text = (f"before = after = {fmt(prior, 3)}" if equal else f"before {fmt(prior, 3)}\nafter {fmt(post, 3)}\n"
                f"(a move of {fmt(abs(post - prior), 3)})")
        ax.annotate(text, (prior, (prior + post) / 2), xytext=spot, textcoords="data", ha="center", va="center",
                    color=PALETTE["ink"], fontsize=10.5, bbox=box,
                    arrowprops={"arrowstyle": "->", "color": PALETTE["ink"], "linewidth": 1.2})
    elif equal:
        label_point(ax, prior, post, f"before = after = {fmt(prior, 3)}", color=PALETTE["ink"],
                    dx=10 if on_left else -10, dy=-14, ha="left" if on_left else "right", va="top").set_bbox(box)
    else:
        label_point(ax, prior, post, f"after {fmt(post, 3)}", color=PALETTE["terracotta"],
                    dx=10 if on_left else -10, dy=10 if post > prior else -12, ha="left" if on_left else "right",
                    va="bottom" if post > prior else "top").set_bbox(box)
        label_point(ax, prior, prior, f"before {fmt(prior, 3)}", color=PALETTE["navy"],
                    dx=10 if on_left else -10, dy=-12 if post > prior else 10, ha="left" if on_left else "right",
                    va="top" if post > prior else "bottom").set_bbox(box)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.12)
    ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    ax.set_xlabel("Belief that the effect landed, before the silence")
    ax.set_ylabel("Belief after the silence")
    ax.set_title(f"Silence likelihood: {fmt(la, 1)} if applied, {fmt(ln, 1)} if not", fontsize=11.5)
    numerator = la * prior
    denominator = numerator + ln * (1 - prior)
    if equal:
        verdict = ("The two likelihoods are equal, so they cancel and the belief stays at its prior. Silence here is "
                   "an uninformative observation, which the chapter uses as its honest baseline.")
    elif post > prior:
        verdict = ("Silence is more likely when the effect landed than when it did not, so the belief rises. "
                   "The belief moved because of the assumed likelihoods, not because silence is bad news by itself.")
    else:
        verdict = ("Silence is less likely when the effect landed than when it did not, so the belief falls. "
                   "A lost reply made the effect look less likely, which only holds under these assumed likelihoods.")
    metrics = {
        "Belief before (prior)": fmt(prior, 3),
        "Silence if applied": fmt(la, 2),
        "Silence if not applied": fmt(ln, 2),
        "Belief after silence": fmt(post, 3),
        "Change": fmt(post - prior, 3),
    }
    interpretation = (
        f"Belief after = ({fmt(la, 1)} x {fmt(prior, 2)}) / ({fmt(la, 1)} x {fmt(prior, 2)} + {fmt(ln, 1)} x {fmt(1 - prior, 2)}) "
        f"= {fmt(numerator, 3)} / {fmt(denominator, 3)} = {fmt(post, 3)}. {verdict}"
    )
    return fig, metrics, interpretation


# Demonstration 3

C_MISS = 10.0  # constructed cost of the action never happening


def lab_duplicate_term(beta, c_dup):
    """Expected duplicate harm beta x c_dup, from the laboratory's retry pricing with no request cost."""
    out = evaluate({
        "idempotent": False,
        "events": [{"kind": "request", "key": "op-1", "payload": "charge-50", "effect": True, "ack": False}],
        "verify_cost": 1, "retry_cost": 0, "effect_probability": float(beta), "duplicate_cost": float(c_dup),
    })
    return float(out["metrics"]["retry_expected_cost"])


def retry_picture(c_dup=10, belief=0.5):
    c_dup, beta = float(c_dup), float(belief)
    dup_term = lab_duplicate_term(beta, c_dup)
    miss_term = (1 - beta) * C_MISS
    diff = miss_term - dup_term
    threshold = C_MISS / (C_MISS + c_dup)
    grid = np.linspace(0, 1, 101)
    line = (1 - grid) * C_MISS - grid * c_dup
    fig, ax = new_figure(height=4.3)
    ax.axhline(0, color=PALETTE["ink"], linewidth=1.0)
    ax.plot(grid, line, color=PALETTE["teal"], linewidth=2.2)
    ax.axvline(threshold, color=PALETTE["grey"], linestyle="dashed", linewidth=1.4)
    tie = math.isclose(diff, 0.0, abs_tol=1e-9)
    ax.plot([beta], [diff], "o", color=PALETTE["terracotta"], markersize=9, zorder=5)
    low = min(-c_dup, 0) * 1.12 - 1
    ax.set_xlim(0, 1.0)
    ax.set_ylim(low, C_MISS * 1.25)
    box = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}
    right_side = beta > 0.5
    # the line falls from the upper left, so for a negative difference the label goes below the point, clear of the line
    below = diff < -1e-9
    label_point(ax, beta, diff, f"{fmt(diff, 1)}", color=PALETTE["terracotta"], dx=-9 if right_side else 9,
                dy=-12 if below else 9, ha="right" if right_side else "left", va="top" if below else "bottom").set_bbox(box)
    if threshold >= 0.999:
        label_point(ax, 1.0, 0, "threshold = 1.00 (tie at belief 1)", color=PALETTE["ink"], dx=-4, dy=-6,
                    ha="right", va="top").set_bbox(box)
        label_point(ax, 0.02, C_MISS * 1.2, "retry is better at every belief below 1", color=PALETTE["teal"], dx=0, dy=0, va="top")
    else:
        near_left = threshold < 0.3
        label_point(ax, threshold, C_MISS * 1.2, f"threshold {fmt(threshold, 2)}", color=PALETTE["ink"],
                    dx=6 if near_left else -6, dy=0, ha="left" if near_left else "right", va="top")
        # the vertical axis is EU(retry) minus EU(decline): above zero retry is better, below zero decline is better
        label_point(ax, 0.02, 0.0, "retry better", color=PALETTE["teal"], dx=0, dy=6, va="bottom") if threshold > 0.3 else None
        label_point(ax, 0.98, 0.0, "decline better", color=PALETTE["terracotta"], dx=0, dy=-6, ha="right", va="top")
    ax.set_xlabel("Belief that the effect already landed")
    ax.set_ylabel("EU(retry) minus EU(decline)")
    ax.set_title(f"Missing the action costs {fmt(C_MISS, 0)}; a duplicate costs {fmt(c_dup, 0)}", fontsize=11.5)
    if tie:
        verdict = (f"The difference is exactly zero: retry and decline tie, and Equation (17.3) does not choose. "
                   f"The belief {fmt(beta, 2)} sits exactly on the threshold {fmt(threshold, 2)}.")
        chosen = "tie"
    elif diff > 0:
        verdict = f"Retry wins: the belief {fmt(beta, 2)} is below the threshold {fmt(threshold, 2)}."
        chosen = "retry"
    else:
        verdict = f"Decline wins: the belief {fmt(beta, 2)} is above the threshold {fmt(threshold, 2)}."
        chosen = "decline"
    metrics = {
        "Chance the action is still needed": fmt(1 - beta, 2),
        "Cost of missing, weighted": fmt(miss_term, 2),
        "Cost of a duplicate, weighted": fmt(dup_term, 2),
        "EU(retry) minus EU(decline)": fmt(diff, 2),
        "Retry threshold": fmt(threshold, 2),
        "Better action": chosen,
    }
    interpretation = (
        f"Difference = (1 - {fmt(beta, 2)}) x {fmt(C_MISS, 0)} - {fmt(beta, 2)} x {fmt(c_dup, 0)} = {fmt(miss_term, 2)} - "
        f"{fmt(dup_term, 2)} = {fmt(diff, 2)}. Threshold = {fmt(C_MISS, 0)} / ({fmt(C_MISS, 0)} + {fmt(c_dup, 0)}) = "
        f"{fmt(threshold, 2)}. {verdict} The threshold depends only on the two costs, not on the belief; the belief only decides which side of it the state falls."
    )
    return fig, metrics, interpretation


# Demonstration 4

EVIDENCE = ["none", "idempotent", "absent", "restored"]


def repeat_set_picture(evidence="none", ready="yes"):
    r = 1 if ready == "yes" else 0
    routes = [int(evidence == "idempotent"), int(evidence == "absent"), int(evidence == "restored")]
    held = sum(routes)
    member = r * held > 0
    rows = [
        ("Ready: authority and preconditions", r),
        ("Route 1: idempotent request (17.1)", routes[0]),
        ("Route 2: Absent (proven never applied)", routes[1]),
        ("Route 3: Restored (verified recovery)", routes[2]),
        ("At least one route holds", int(held > 0)),
        ("Eligible: in Rep(x)", int(member)),
    ]
    fig, ax = new_figure(height=4.3)
    n = len(rows)
    ypos = np.arange(n)[::-1]
    for y, (name, value) in zip(ypos, rows):
        final = name.startswith("Eligible")
        ax.barh(y, 1, color="white", edgecolor=PALETTE["grey"], height=0.62, linewidth=1.2)
        if value:
            ax.barh(y, 1, color=PALETTE["teal"], height=0.62, edgecolor=PALETTE["ink"] if final else PALETTE["teal"],
                    linewidth=2.0 if final else 1.0)
            ax.text(0.5, y, "true", ha="center", va="center", fontsize=11, color="white", fontweight="bold")
        else:
            ax.barh(y, 1, color="white", height=0.62, edgecolor=PALETTE["terracotta"], hatch="///", linewidth=1.2)
            ax.text(0.5, y, "false", ha="center", va="center", fontsize=11, color=PALETTE["ink"], fontweight="bold",
                    bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.95})
    ax.set_yticks(ypos, [name for name, _ in rows])
    ax.set_xlim(0, 1)
    ax.set_xticks([])
    ax.set_xlabel("Filled bar: the condition holds. Hatched bar: it does not.")
    ax.set_ylabel("Condition in Equation (17.4)")
    ax.grid(alpha=0)
    if evidence == "none":
        title = "No evidence yet"
    else:
        title = {"idempotent": "Idempotent semantics apply", "absent": "Proof of terminal non-application",
                 "restored": "Verified restoration"}[evidence]
    ax.set_title(f"{title}; ready = {ready}", fontsize=11.5)
    if member:
        verdict = "The request is in Rep(x): a repeat attempt is eligible, though eligible does not mean free or required."
        status = "in Rep(x)"
    elif not r and held:
        verdict = ("A route holds but the request is not Ready, so it is outside Rep(x). Evidence of safety cannot "
                   "replace current authority and preconditions.")
        status = "not in Rep(x)"
    elif not r:
        verdict = ("Nothing holds: no authority check and no route. The request is outside Rep(x), and the next step "
                   "may be an observation, a recovery, a deliberate risk decision or a person.")
        status = "not in Rep(x)"
    else:
        verdict = ("Ready holds but no evidence supports a route, so the request is outside Rep(x). If the operation is "
                   "uncertain and not idempotent, it may need observation, recovery, a deliberate risk decision or a person "
                   "before another attempt.")
        status = "not in Rep(x)"
    metrics = {
        "Ready": "true" if r else "false",
        "Routes that hold": f"{held} of 3",
        "Membership": status,
    }
    interpretation = (
        f"Routes held = {routes[0]} + {routes[1]} + {routes[2]} = {held}. Ready x routes held = {r} x {held} = {r * held}, "
        f"and any positive result is membership. {verdict}"
    )
    return fig, metrics, interpretation


CHAPTER = {
    "number": 17,
    "title": "State and Consequence",
    "subtitle": "A lost reply does not say whether the effect happened. Four ideas turn that silence into a decision.",
    "summary": (
        "These four demonstrations follow the chapter's agent that sent a request and lost the reply. The first compares "
        "repeating a request with sending it once. The second turns silence into a belief. The third prices a retry "
        "against a duplicate. The fourth shows which evidence makes a repeat attempt eligible."
    ),
    "demos": [
        {
            "id": "C17-D01",
            "title": "Send it twice: what is different afterward?",
            "question": "For which kinds of request does a repeat leave the intended effect unchanged?",
            "equations": [EQ_IDEMPOTENT],
            "symbols": (
                "T is the tool, x the state of the world, eff(T, x) the state after the tool runs, and eff with subscript I "
                "keeps only the coordinates the request asked about (here the record's value). The equation says running T twice gives "
                "the same intended coordinates as running it once. Log lines are outside that projection."
            ),
            "prediction": "Pick the charge with no key and 3 requests. Will the record end at 150, 200 or 250?",
            "explanation": (
                "Setting a value and deleting a record land in the same place however often they repeat, so the equation "
                "holds. A charge adds again each time, so it fails. A stored key lets the service count the charge once, "
                "which restores the equation for that request. The service may still keep a log line per request."
            ),
            "application": (
                "Ask of every tool: if this is called twice with identical arguments, what is different afterward? "
                "Write the answer on the tool definition, because the agent cannot infer it from a name."
            ),
            "assumptions": (
                "One tool at one state, with one record and constructed values (start 100, target 150, charge 50). The "
                "equation says nothing about sequences of tools, and a key only helps if the service really deduplicates "
                "under its contract: a lost key or a reused key can break it. The service is also constructed to log every "
                "request and to reply as shown."
            ),
            "check": "A charge of 50 with a stored key is sent 4 times from a record of 100. Where does the record end?",
            "answer": "The key makes the service count it once: 100 + 1 x 50 = 150. Without the key it would be 100 + 4 x 50 = 300.",
            "provenance": "Constructed example: values defined for this reader; effects are counted with the laboratory's effect ledger.",
            "source_section": "The classification the specification actually uses",
            "source_anchor": "the-classification-the-specification-actually-uses",
            "controls": [
                {"key": "operation", "label": "Kind of request", "values": list(OPERATIONS), "default": "put",
                 "value_labels": list(OPERATIONS.values())},
                {"key": "requests", "label": "Identical requests sent", "values": [2, 3], "default": 2},
            ],
            "function": "repeat_picture",
        },
        {
            "id": "C17-D02",
            "title": "Silence as evidence",
            "question": "After no reply, how likely is it that the effect already landed?",
            "equations": [EQ_BELIEF],
            "symbols": (
                "Pr(applied) is the belief that the effect landed, before the silence is taken into account. Obs(silence | "
                "applied) is the probability of getting no reply when it did land, and Obs(silence | not applied) the "
                "probability of no reply when it did not. b'(applied) is the belief after the silence. In the equation the empty-set symbol stands for silence, the empty "
                "response."
            ),
            "prediction": "If silence is exactly as likely in both worlds, does the belief of 0.5 move? Then set the chance of silence if the effect landed to 0.9, against a fixed 0.5 if it did not. Does the belief rise or fall?",
            "explanation": (
                "Bayes' rule weighs how likely silence is in each world by how likely each world was. If the likelihoods are "
                "equal they cancel and nothing changes. If silence is more likely when the effect landed, the belief rises; "
                "if less likely, it falls. The likelihoods are the whole story."
            ),
            "application": (
                "Do not turn a timeout into a probability by instinct. Ask what the service does when the request lands "
                "and what it does when it does not, because those two likelihoods set the belief."
            ),
            "assumptions": (
                "Two worlds only (applied, not applied) and constructed likelihoods, with silence 0.5 likely if the request "
                "did not apply. A real transport symptom rarely supplies either likelihood, and an agent that writes its "
                "own status report is feeding its own belief. If silence is impossible in both worlds the formula is "
                "undefined, because the observation could not have happened."
            ),
            "check": "Prior belief 0.2, silence 0.9 likely if applied and 0.5 likely if not. What is the belief after silence?",
            "answer": "(0.9 x 0.2) / (0.9 x 0.2 + 0.5 x 0.8) = 0.18 / 0.58 = 0.310, up from 0.2.",
            "provenance": "Constructed example: priors and likelihoods defined for this reader; the chapter's own baseline is the equal-likelihood case.",
            "source_section": "Stage two: how likely is it that the effect landed",
            "source_anchor": "stage-two-how-likely-is-it-that-the-effect-landed",
            "controls": [
                {"key": "prior", "label": "Belief before silence", "values": [0.5, 0.99], "default": 0.5},
                {"key": "silence_if_applied", "label": "Chance of silence if the effect landed", "values": [0.1, 0.5, 0.9], "default": 0.5},
            ],
            "function": "belief_picture",
        },
        {
            "id": "C17-D03",
            "title": "Retry or decline: pricing a duplicate",
            "question": "At what belief does sending the request again stop being worth it?",
            "equations": [EQ_RETRY],
            "symbols": (
                "Beta, the Greek letter in the equation, is the belief that the effect already landed. The cost written c with "
                "subscript miss is the cost of the action never happening (10 here) and c with subscript dup is the cost of "
                "applying it twice. EU(retry) minus EU(decline) is how much better a "
                "retry is than leaving things alone, in the same cost units."
            ),
            "prediction": "With a duplicate cost of 10 and a belief of 0.5, which wins? Predict before changing the control.",
            "explanation": (
                "A retry is right with chance 1 minus the belief, saving the missing cost, and wrong with the belief's own "
                "chance, adding the duplicate cost. The difference crosses zero at a belief equal to the missing cost divided "
                "by the missing cost plus the duplicate cost, a threshold that depends only on the two costs. A free duplicate pushes it to 1; a costly one pulls it toward 0."
            ),
            "application": (
                "Write down both costs before the connection drops. A team that has not priced a duplicate has still made "
                "the decision, by leaving it to whatever default the retry library has."
            ),
            "assumptions": (
                "The chapter's teaching construction: a retry certainly applies the effect, the original attempt can no "
                "longer apply, there are no other request costs, and the costs and beliefs are constructed. A request fee, "
                "an expired authority or a changed resource version would change the comparison."
            ),
            "check": "With a missing cost of 10 and a duplicate cost of 30, what is the retry threshold, and does a belief of 0.3 retry?",
            "answer": "10 / (10 + 30) = 0.25. A belief of 0.3 is above it, so decline: 0.7 x 10 - 0.3 x 30 = 7 - 9 = -2.",
            "provenance": "Constructed example: costs defined for this reader; the duplicate term comes from the laboratory's retry pricing.",
            "source_section": "Stage three: the retry decision, priced",
            "source_anchor": "stage-three-the-retry-decision-priced",
            "controls": [
                {"key": "c_dup", "label": "Cost of a duplicate effect", "values": [0, 10, 90], "default": 10,
                 "value_labels": ["0 (idempotent)", "10 (balanced)", "90 (very costly)"]},
                {"key": "belief", "label": "Belief the effect already landed", "values": [0.5, 0.99], "default": 0.5},
            ],
            "function": "retry_picture",
        },
        {
            "id": "C17-D04",
            "title": "Which repeats are eligible",
            "question": "What evidence has to be in hand before another attempt is eligible?",
            "equations": [EQ_REPEAT_SET],
            "symbols": (
                "Rep(x) is the set of tools T whose repeat attempt is eligible at state x. Ready(T, x) means authority, "
                "preconditions and retry limits hold now. Absent(T, x) means authoritative proof the original never applied "
                "and cannot apply later. Restored(T, x) means recovery succeeded and was verified."
            ),
            "prediction": "With no evidence, is a Ready request in Rep(x)? Then pick Proof of non-application and set Ready to no.",
            "explanation": (
                "Equation (17.4) is a logical gate: the request must be Ready and at least one route must hold, either "
                "idempotent semantics, proof of terminal non-application, or verified restoration. Ready alone is not "
                "enough, and a route alone is not enough."
            ),
            "application": (
                "Before a retry leaves, run the gate. If it fails, the next step may be a read, a recovery, a deliberate risk decision or a person. "
                "Do not treat a posterior near zero as proof of absence: it is a risk estimate."
            ),
            "assumptions": (
                "The set is the chapter's conservative construction, not a rule from the HTTP standard, and one evidence "
                "route is shown at a time. If a read shows the request applied and complete, nothing here is repeated "
                "and the request is closed. Having an undo tool does not count as Restored until recovery is verified. "
                "Evidence goes stale: authority can expire and a version check can become out of date."
            ),
            "check": "A read proves a non-idempotent charge was applied and complete. Is the charge in Rep(x)?",
            "answer": (
                "No. Applied is not Absent, the charge is not idempotent and nothing was restored, so 0 + 0 + 0 = 0 routes "
                "hold. The request is already done, so stop."
            ),
            "provenance": "Constructed example: the evidence cases are defined for this reader from the chapter's own routes.",
            "source_section": "Stage four: memory, undo, and the set they produce",
            "source_anchor": "stage-four-memory-undo-and-the-set-they-produce",
            "controls": [
                {"key": "evidence", "label": "Evidence in hand", "values": EVIDENCE, "default": "none",
                 "value_labels": ["No evidence", "Idempotent semantics apply", "Proof of non-application", "Verified restoration"]},
                {"key": "ready", "label": "Ready (authority and preconditions hold)", "values": ["yes", "no"], "default": "yes"},
            ],
            "function": "repeat_set_picture",
        },
    ],
}

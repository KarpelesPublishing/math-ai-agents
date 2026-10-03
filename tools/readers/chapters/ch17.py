"""Chapter 17 reader: State and Consequence.

Four demonstrations built on Equations (17.1) to (17.4).

Demonstration 1 counts effects with the laboratory's own effect ledger
(math_ai_agents.chapters.ch17.evaluate), covering the notebook's default trace (no key),
its changed trace (key stored), and the chapter's safe, idempotent and neither classes.
Demonstration 2 chains Equation (17.2) into Equation (17.3) and the value of a read
(workbench problems IV.1 and IV.3); its duplicate term comes from the laboratory's retry pricing.
Demonstration 3 walks the recovery sequence behind Restored in Equation (17.4), and uses the
laboratory's ledger for the notebook's transfer trace (a lost reply followed by a read).
Demonstration 4 evaluates Equation (17.4) on the chapter's six-step plan.
Every number is a constructed teaching value.
"""
import math

import numpy as np
from matplotlib.patches import Rectangle

from math_ai_agents.chapters.ch17 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure, undefined

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

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.9}

START = 100.0   # constructed starting value of the record
STEP = 50.0     # constructed amount a charge adds, or the target of a set (150)
TARGET = 150.0


# Demonstration 1

OPERATIONS = {
    "read": "Read the record (safe, GET-like)",
    "put": "Set the record to 150 (idempotent, PUT-like)",
    "delete": "Delete the record (idempotent, DELETE-like)",
    "charge": "Add a charge of 50, no key (neither, POST-like)",
    "charge_key": "Add a charge of 50, key stored by the service",
    "charge_lost_key": "Add a charge of 50, key lost or past its retention window",
}

CLASSES = {
    "read": ("safe (so also idempotent)", "allowed: the intended effect is unchanged, subject to current authority and the service contract"),
    "put": ("idempotent", "allowed: the intended effect is unchanged, subject to current authority and the service contract"),
    "delete": ("idempotent", "allowed: the intended effect is unchanged, subject to current authority and the service contract"),
    "charge": ("neither safe nor idempotent", "not on this evidence alone: needs known idempotent semantics or proof the first was never applied"),
    "charge_key": ("idempotent by the key's contract, not by the method", "allowed only while the key's contract covers this request"),
    "charge_lost_key": ("key not recognized, so it behaves as neither", "not on this evidence alone"),
}


def lab_effects(n_requests, idempotent, same_key=True, effect=True):
    """Number of durable effects after n identical requests, from the laboratory's effect ledger."""
    events = [
        {"kind": "request", "key": "op-1" if same_key else f"op-1-{i}", "payload": "charge-50", "effect": effect,
         "ack": bool(effect) and i == n_requests - 1}
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
    if operation == "read":
        return START + STEP * lab_effects(k, True, effect=False)
    if operation == "put":
        return TARGET
    if operation == "delete":
        return 0.0
    if operation == "charge":
        return START + STEP * lab_effects(k, False)
    if operation == "charge_key":
        return START + STEP * lab_effects(k, True)
    return START + STEP * lab_effects(k, True, same_key=False)


REQUESTS = 3  # identical requests sent in every state of Demonstration 1

KINDS = {
    "read": "Read the record (safe, GET-like)",
    "put": "Set the record to 150 (idempotent, PUT-like)",
    "delete": "Delete the record (idempotent, DELETE-like)",
    "charge": "Add a charge of 50 (POST-like)",
}
KEYS = {
    "none": "No key",
    "stored": "Key stored by the service",
    "lost": "Key lost or past its retention window",
}


def repeat_picture(kind="put", key="none"):
    n = REQUESTS
    operation = kind if kind != "charge" else {"none": "charge", "stored": "charge_key", "lost": "charge_lost_key"}[key]
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
    if operation == "read":
        calc = (f"A read requests no change, so the record after {n} requests minus the record after one is "
                f"{fmt(values[n], 0)} - {fmt(values[1], 0)} = {fmt(values[n] - values[1], 0)}. A method that requests no change "
                "requests the same no change twice, so every safe method is also idempotent.")
        responses = "the same record each time"
    elif operation == "put":
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
    elif operation == "charge_key":
        calc = (f"The stored key makes the service count the charge once, so after {n} requests the record is "
                f"{fmt(START, 0)} + 1 x {fmt(STEP, 0)} = {fmt(values[n], 0)}, and {fmt(values[n], 0)} - {fmt(values[1], 0)} = "
                f"{fmt(values[n] - values[1], 0)} against the state after one request.")
        responses = "repeats return the saved result"
    else:
        calc = (f"The repeat carries a key the service no longer recognizes, so it is applied as a new charge: after one request "
                f"the record is {fmt(START, 0)} + 1 x {fmt(STEP, 0)} = {fmt(values[1], 0)} and after {n} it is "
                f"{fmt(START, 0)} + {n} x {fmt(STEP, 0)} = {fmt(values[n], 0)}, a difference of "
                f"{fmt(values[n], 0)} - {fmt(values[1], 0)} = {fmt(values[n] - values[1], 0)}.")
        responses = "each request reports a charge"
    if holds:
        verdict = (f"Equation (17.1) holds here: one request and {label_after} leave the same intended effect. "
                   f"The service still wrote {n} log lines, which sit outside the intended-effect coordinate.")
    else:
        verdict = (f"Equation (17.1) fails here: {label_after} leave the record at {fmt(values[n], 0)}, not {fmt(values[1], 0)}, "
                   "so a retry after a lost reply is not safe on this evidence alone.")
    klass, retry = CLASSES[operation]
    metrics = {
        "Class (Figure 17.2)": klass,
        "Record after one request": "absent" if operation == "delete" else fmt(values[1], 0),
        f"Record after {n} requests": "absent" if operation == "delete" else fmt(values[n], 0),
        "Equation (17.1)": "holds" if holds else "fails",
        "Log lines written": str(n),
        "Replies": responses,
        "Automatic retry after a lost reply": retry,
    }
    interpretation = f"{calc} {verdict} A reply can differ without breaking the equation, because the equation compares effects, not replies."
    alt = (f"Left: bars for the record value at the start and after each of {n} identical requests, ending at "
           f"{'absent' if operation == 'delete' else fmt(values[n], 0)}; the bars are flagged when they differ from the state after one request. "
           f"Right: the service's log lines, one per request, {n} in all.")
    return fig, metrics, interpretation, alt


# Demonstration 2: from silence to a decision

SILENCE_IF_NOT_APPLIED = 0.5  # constructed likelihood of silence when the request did not apply
C_MISS = 10.0                 # constructed cost of the action never happening
READ_COST = 1.0               # workbench IV.3: a perfect read costs 1 utility unit


def posterior(prior, silence_if_applied, silence_if_not=SILENCE_IF_NOT_APPLIED):
    """Equation (17.2). Returns None when silence has probability zero in both worlds."""
    num = silence_if_applied * prior
    den = num + silence_if_not * (1 - prior)
    return None if den == 0 else num / den


def lab_duplicate_term(beta, c_dup):
    """Expected duplicate harm beta x c_dup, from the laboratory's retry pricing with no request cost."""
    out = evaluate({
        "idempotent": False,
        "events": [{"kind": "request", "key": "op-1", "payload": "charge-50", "effect": True, "ack": False}],
        "verify_cost": 1, "retry_cost": 0, "effect_probability": float(beta), "duplicate_cost": float(c_dup),
    })
    return float(out["metrics"]["retry_expected_cost"])


def decision_picture(prior=0.3, silence_if_applied=0.5, c_dup=40):
    prior, la, c_dup = float(prior), float(silence_if_applied), float(c_dup)
    ln = SILENCE_IF_NOT_APPLIED
    w_applied = la * prior
    w_not = ln * (1 - prior)
    beta = posterior(prior, la, ln)
    retry_cost = lab_duplicate_term(beta, c_dup)
    decline_cost = (1 - beta) * C_MISS
    diff = decline_cost - retry_cost  # EU(retry) - EU(decline), Equation (17.3)
    threshold = C_MISS / (C_MISS + c_dup)
    best_blind = min(retry_cost, decline_cost)
    costs = {"Retry": retry_cost, "Decline": decline_cost, "Read first": READ_COST}
    lowest = min(costs.values())
    cheapest = [k for k, v in costs.items() if abs(v - lowest) < 1e-9]
    gross = best_blind  # a perfect read leaves no expected duplicate or omission loss
    net = gross - READ_COST

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    xs = np.array([0.0, 1.0])
    left.bar(xs - 0.19, [prior, beta], width=0.36, color=PALETTE["terracotta"], edgecolor=PALETTE["ink"], linewidth=0.8)
    left.bar(xs + 0.19, [1 - prior, 1 - beta], width=0.36, color=PALETTE["navy"], edgecolor=PALETTE["ink"], linewidth=0.8)
    for x, a, b in zip(xs, [prior, beta], [1 - prior, 1 - beta]):
        left.text(x - 0.19, a + 0.02, fmt(a, 3), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
        left.text(x + 0.19, b + 0.02, fmt(b, 3), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"])
    left.set_xticks(xs, ["Before the silence", "After the silence"])
    left.set_xlim(-0.6, 1.6)
    left.set_ylim(0, 1.2)
    left.set_xlabel("Belief state (terracotta: effect landed, navy: it did not)")
    left.set_ylabel("Belief")
    left.set_title(f"Silence: {fmt(la, 1)} likely if applied, {fmt(ln, 1)} if not", fontsize=11.5)
    left.grid(axis="x", alpha=0)

    labels = list(costs)
    vals = [costs[k] for k in labels]
    for i, (name, v) in enumerate(zip(labels, vals)):
        win = abs(v - lowest) < 1e-9
        right.bar(i, v, width=0.55, color=PALETTE["teal"] if win else "#8fa3b8", edgecolor=PALETTE["ink"], linewidth=1.4 if win else 0.8)
        right.text(i, v + max(vals) * 0.03 + 0.15, fmt(v, 2) + ("\nlowest" if win else ""), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"])
    for i, v in enumerate(vals):
        if abs(v - lowest) < 1e-9:
            right.plot([i], [v], marker="v", color=PALETTE["teal"], markeredgecolor=PALETTE["ink"], markersize=11, zorder=6)
    right.set_xticks(range(3), labels)
    right.set_ylim(0, max(vals) * 1.3 + 1.6)
    right.set_xlabel("Action (teal bar or teal marker: lowest expected cost)")
    right.set_ylabel("Expected cost (utility units)")
    right.set_title(f"Belief {fmt(beta, 2)}, threshold {fmt(threshold, 2)}; duplicate costs {fmt(c_dup, 0)}", fontsize=11.5)
    right.grid(axis="x", alpha=0)

    if math.isclose(la, ln):
        belief_note = ("The two likelihoods are equal, so they cancel and the belief stays at its prior: silence is an uninformative "
                       "observation, the chapter's honest baseline.")
    elif beta > prior:
        belief_note = ("Silence is more likely when the effect landed, so the belief rises; that comes from the assumed "
                       "likelihoods, not from silence being bad news by itself.")
    else:
        belief_note = ("Silence is less likely when the effect landed, so the belief falls, under these assumed likelihoods only.")
    if len(cheapest) == 1:
        best_text = {"Retry": "retrying", "Decline": "declining", "Read first": "reading first"}[cheapest[0]]
        decision = (f"The lowest expected cost is {fmt(lowest, 2)}, from {best_text}.")
    else:
        decision = f"{' and '.join(cheapest)} tie at {fmt(lowest, 2)}, so the comparison does not choose."
    # the displayed two-decimal costs can differ by 0.01 from their displayed difference
    shown_diff = round(round(decline_cost, 2) - round(retry_cost, 2), 2)
    rounding_note = "" if math.isclose(shown_diff, round(diff, 2), abs_tol=1e-9) else "(computed from the unrounded belief) "
    interpretation = (
        f"Belief after = ({fmt(la, 1)} x {fmt(prior, 2)}) / ({fmt(la, 1)} x {fmt(prior, 2)} + {fmt(ln, 1)} x {fmt(1 - prior, 2)}) = "
        f"{fmt(w_applied, 3)} / {fmt(w_applied + w_not, 3)} = {fmt(beta, 3)}. {belief_note} "
        f"Retrying costs {fmt(beta, 4)} x {fmt(c_dup, 0)} = {fmt(retry_cost, 2)} and declining costs (1 - {fmt(beta, 4)}) x {fmt(C_MISS, 0)} = "
        f"{fmt(decline_cost, 2)}, so Equation (17.3) gives {fmt(decline_cost, 2)} - {fmt(retry_cost, 2)} = {fmt(diff, 2)} "
        f"{rounding_note}(threshold {fmt(C_MISS, 0)} / ({fmt(C_MISS, 0)} + {fmt(c_dup, 0)}) = {fmt(threshold, 2)}). A perfect read costs {fmt(READ_COST, 0)}: "
        f"its gross value is the best cost without it, {fmt(gross, 2)}, and its net value is {fmt(gross, 2)} - {fmt(READ_COST, 0)} = "
        f"{fmt(net, 2)}. {decision}"
    )
    if c_dup == 0:
        interpretation += (" With no duplicate cost, retrying is as good as acting with the information, so the read is worth nothing "
                           "to this decision: idempotent semantics and observation substitute for each other here.")
    steps = [
        f"Weight if the effect landed: {fmt(la, 1)} x {fmt(prior, 2)} = {fmt(w_applied, 3)}.",
        f"Weight if it did not: {fmt(ln, 1)} x {fmt(1 - prior, 2)} = {fmt(w_not, 3)}.",
        f"Belief after silence (beta): {fmt(w_applied, 3)} / ({fmt(w_applied, 3)} + {fmt(w_not, 3)}) = {fmt(beta, 3)}.",
        f"Retry: beta x c_dup = {fmt(beta, 4)} x {fmt(c_dup, 0)} = {fmt(retry_cost, 2)}.",
        f"Decline: (1 - beta) x c_miss = {fmt(1 - beta, 4)} x {fmt(C_MISS, 0)} = {fmt(decline_cost, 2)}.",
        f"Equation (17.3): {fmt(decline_cost, 2)} - {fmt(retry_cost, 2)} = {fmt(diff, 2)}{' (computed from the unrounded belief)' if rounding_note else ''}; threshold {fmt(threshold, 2)}.",
        f"Perfect read: gross value {fmt(gross, 2)}, net {fmt(gross, 2)} - {fmt(READ_COST, 0)} = {fmt(net, 2)}.",
    ]
    metrics = {
        "Belief before silence (prior)": fmt(prior, 3),
        "Belief after silence (beta)": fmt(beta, 3),
        "Expected cost of retrying": fmt(retry_cost, 2),
        "Expected cost of declining": fmt(decline_cost, 2),
        "Cost of reading first": fmt(READ_COST, 2),
        "EU(retry) minus EU(decline)": fmt(diff, 2),
        "Retry threshold": fmt(threshold, 2),
        "Lowest expected cost": " and ".join(cheapest),
        "Gross value of a perfect read": fmt(gross, 2),
        "Net value of the read": fmt(net, 2),
    }
    alt = (f"Left: belief that the effect landed before silence, {fmt(prior, 3)}, and after, {fmt(beta, 3)}, as paired bars with the "
           f"complementary belief. Right: expected cost of retrying {fmt(retry_cost, 2)}, declining {fmt(decline_cost, 2)} and "
           f"reading first {fmt(READ_COST, 2)}; the lowest is {' and '.join(cheapest)}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: recovery before a repeat

COORDS = [
    "Money returned to the customer",
    "Confirmation email retracted",
    "Downstream webhook retracted",
    "Partner ledger entry removed",
]
OUTCOMES = {
    "works": "The undo works and is verified",
    "unavailable": "No undo can run (absent or expired)",
    "partial": "Partial: the refund returns the money, the rest stays",
    "lost": "The undo call is itself lost (no verifying read yet)",
}
STAGES = {1: "1. Observe: read what happened", 2: "2. Run the undo", 3: "3. Verify, then check preconditions"}
STATUS_STYLE = {
    "place": ("Consequence still in place", "#f0d6cf", "///"),
    "applied": ("Undo applied, not yet verified", "#f3e3b8", ""),
    "verified": ("Verified restored", "#cfe6e6", ""),
    "unknown": ("Not verified: the undo reply was lost", "#e6e9ea", ""),
}


def lab_transfer_ledger():
    """The notebook's transfer trace: one request takes effect without an acknowledgement, then a read observes it."""
    out = evaluate({
        "idempotent": False,
        "events": [
            {"kind": "request", "key": "send-2", "payload": "packet-B", "effect": True, "ack": False},
            {"kind": "verify", "observed_effect": True},
        ],
        "verify_cost": 0.5, "retry_cost": 0.1, "effect_probability": 0.6, "duplicate_cost": 4,
    })
    m = out["metrics"]
    return int(m["effects"]), bool(m["confirmed"]), m["preferred_next_step"]


def coordinate_status(stage, outcome):
    """Status of the four coordinates at a stage for an undo outcome (constructed from the chapter's examples)."""
    if stage == 1:
        return ["place"] * 4
    if stage == 2:
        return {"works": ["applied"] * 4, "unavailable": ["place"] * 4,
                "partial": ["applied", "place", "place", "place"], "lost": ["unknown"] * 4}[outcome]
    return {"works": ["verified"] * 4, "unavailable": ["place"] * 4,
            "partial": ["verified", "place", "place", "place"], "lost": ["unknown"] * 4}[outcome]


def recovery_picture(stage=1, outcome="works"):
    stage = int(stage)
    status = coordinate_status(stage, outcome)
    verified = [1 if (stage == 3 and s == "verified") else 0 for s in status]
    count = sum(verified)
    restored = stage == 3 and count == 4
    effects, confirmed, preferred = lab_transfer_ledger()
    fig, ax = new_figure(height=4.4)
    n = len(COORDS)
    for r, (name, st) in enumerate(zip(COORDS, status)):
        text, color, hatch = STATUS_STYLE[st]
        ax.add_patch(Rectangle(
            (0, r), 1, 1, facecolor=color, edgecolor="white", linewidth=2, hatch=hatch or None))
        ax.text(0.5, r + 0.5, text, ha="center", va="center", fontsize=10.5, color=PALETTE["ink"],
                bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.9} if hatch else None)
    ok = restored
    ax.add_patch(Rectangle(
        (0, n), 1, 1, facecolor="#cfe6e6" if ok else "#f0d6cf", edgecolor=PALETTE["ink"], linewidth=2,
        hatch=None if ok else "///"))
    ax.text(0.5, n + 0.5, f"Restored(T, x) = {'true' if ok else 'false'} ({count} of 4 verified)", ha="center", va="center",
            fontsize=10.5, color=PALETTE["ink"], fontweight="bold",
            bbox=None if ok else {"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.95})
    ax.set_xlim(0, 1)
    ax.set_ylim(n + 1, 0)
    ax.set_xticks([])
    ax.set_yticks(np.arange(n + 1) + 0.5, COORDS + ["Restored in Equation (17.4)"])
    ax.set_xlabel("Status at this stage of the recovery sequence")
    ax.set_ylabel("Consequence of the original charge")
    ax.grid(False)
    ax.tick_params(length=0)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    short = {"works": "undo works", "unavailable": "no undo can run", "partial": "partial undo", "lost": "undo call lost"}[outcome]
    ax.set_title(f"Stage {stage} of 3 (scenario: {short})", fontsize=11.5)

    parts = " + ".join(str(v) for v in verified)
    if stage == 1:
        nxt = "Do not send another charge: the read shows it landed. Any repeat needs a recovery that is run and verified."
        story = (f"A read of the ledger finds {effects} charge entry and confirms it, so the original request is applied and "
                 "complete; none of its consequences is undone yet.")
    elif stage == 2:
        story = {
            "works": "The undo ran and reports success on every consequence, but a report is not verification.",
            "unavailable": "No undo can run: either none exists or its window has closed, and the chapter notes the absence is usually discovered at the moment it matters.",
            "partial": "The refund ran and returns the money; it does not retract the email, the webhook or the partner's ledger entry.",
            "lost": "The undo is another call and its reply was lost, so whether it applied is unknown; the retry question recurs one level down.",
        }[outcome]
        nxt = "Verify the result of the undo before treating anything as restored."
    else:
        story = {
            "works": "Verification finds every consequence restored.",
            "unavailable": "Verification finds every consequence still in place, because no undo could run.",
            "partial": "Verification finds the money restored and the other three consequences still in place.",
            "lost": "No verifying read has been made after the lost undo reply, so nothing is verified and no consequence counts as restored. A read of each consequence would resolve it into one of the other outcomes.",
        }[outcome]
        nxt = ("A fresh charge is eligible only if Ready also holds: this stage includes the check of authority and preconditions."
               if restored else
               "Not restored, so Equation (17.4) gives no route 3. Escalate, decide a risk, or give the undo its own retry and escalation limits.")
    interpretation = (
        f"Verified restored = {parts} = {count} of 4, and Restored needs 4 of 4, so Restored(T, x) is {'true' if ok else 'false'}. "
        f"{story} {nxt}"
    )
    steps = {
        1: ["The original request landed but its reply was lost.",
            f"A read of the ledger shows {effects} charge entry and confirms it: applied and complete.",
            f"Coordinates verified restored: {parts} = {count} of 4.",
            "Do not repeat the charge; start recovery only if the charge is not wanted."],
        2: ["Run the undo (a second transaction, not the absence of the charge).",
            f"Result: {short}.",
            f"Coordinates verified restored so far: {parts} = {count} of 4, because nothing is verified yet.",
            "Verify before treating anything as restored."],
        3: [("No verifying read has been made after the lost undo reply; a read of each consequence would settle it, then check authority and preconditions."
             if outcome == "lost" else "Verify each consequence by a read, then check authority and preconditions."),
            f"Result: {short}.",
            f"Verified restored: {parts} = {count} of 4.",
            f"Restored(T, x) needs 4 of 4: it is {'true' if ok else 'false'}."],
    }[stage]
    metrics = {
        "Stage": STAGES[stage],
        "Undo outcome": short,
        "Charge entries on the ledger (at the stage 1 read)": str(effects),
        "Coordinates verified restored": f"{count} of 4",
        "Restored(T, x)": "true" if ok else "false",
        "Route 3 of Equation (17.4)": "holds (if Ready holds)" if ok else "does not hold",
    }
    alt = (f"Four rows for the consequences of the charge, each colored by status at stage {stage} ({short}), and a bottom row "
           f"stating that Restored is {'true' if ok else 'false'} with {count} of 4 verified.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: the six-step plan

PLAN = {
    "merge": ("Step 3: write the merged record", True,
              "Writing a specified merged record can be idempotent with respect to that content, if identifiers are stable and the write carries a version condition."),
    "delete": ("Step 4: delete the older record", True,
               "Deleting a specific older record can be idempotent with respect to its absence, but repeating a delete and undoing it are different questions: the older contents are gone unless they were retained."),
    "notify": ("Step 5: notify the customer", False,
               "A second notification may send a second email, so the request has no idempotent semantics for its intended effect."),
    "audit": ("Step 6: log the change to the audit system", False,
              "An audit append may create a second entry; an interface could deduplicate one logical event, but this one does not say so."),
}
EVIDENCE = {
    "none": "No extra evidence",
    "absent": "A read proves terminal non-application (Absent)",
    "expired": "Authority has expired (not Ready)",
}


SHORT_EVIDENCE = {"none": "no extra evidence", "absent": "non-application proven", "expired": "authority expired"}


def plan_picture(step="merge", evidence="none"):
    title, idem, why = PLAN[step]
    ready = int(evidence != "expired")
    routes = [int(idem), int(evidence == "absent"), 0]
    held = sum(routes)
    member = ready * held > 0
    rows = [
        ("Ready: authority and preconditions", ready),
        ("Route 1: idempotent for this request (17.1)", routes[0]),
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
    ax.set_title(f"{title}; {SHORT_EVIDENCE[evidence]}", fontsize=11.5)
    if member:
        verdict = "The request is in Rep(x): a repeat is eligible, though eligible does not mean free, harmless or required."
    elif not ready and held:
        verdict = ("A route holds but the request is not Ready, so it is outside Rep(x). Evidence about the effect cannot "
                   "replace current authority and preconditions.")
    elif not ready:
        verdict = ("Nothing holds: authority has expired and no route supports a repeat. The next step is a read, a renewed "
                   "authorization, a deliberate risk decision or a person.")
    else:
        verdict = ("Ready holds but no route does, so the request is outside Rep(x): this step needs a read that proves terminal "
                   "non-application, a key the service honors, or a verified recovery before another attempt.")
    interpretation = (
        f"{why} Routes held = {routes[0]} + {routes[1]} + {routes[2]} = {held}. Ready x routes held = {ready} x {held} = {ready * held}, "
        f"and any positive result is membership. {verdict}"
    )
    steps = [
        f"{title}: idempotent for this request? {'yes' if idem else 'no'}, so route 1 is {routes[0]}.",
        f"Evidence: {EVIDENCE[evidence].lower()}; route 2 (Absent) is {routes[1]}, route 3 (Restored) is {routes[2]}.",
        f"Routes held = {routes[0]} + {routes[1]} + {routes[2]} = {held}.",
        f"Ready = {ready}; Ready x routes held = {ready} x {held} = {ready * held}.",
        f"{'In' if member else 'Not in'} Rep(x).",
    ]
    metrics = {
        "Step": title,
        "Ready": "true" if ready else "false",
        "Routes that hold": f"{held} of 3",
        "Membership": "in Rep(x)" if member else "not in Rep(x)",
    }
    alt = (f"Six condition bars for {title.lower()}: Ready is {'true' if ready else 'false'}, routes held {held} of 3, and the request "
           f"is {'in' if member else 'not in'} the repeat set.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 17,
    "title": "State and Consequence",
    "subtitle": "A lost reply does not say whether the effect happened. Four ideas turn that silence into a decision.",
    "summary": (
        "These four demonstrations follow the chapter's agent that sent a request and lost the reply. The first compares "
        "repeating a request with sending it once, across the chapter's safe, idempotent and neither classes and a key that is lost. "
        "The second turns silence into a belief and prices a retry, a decline and a perfect read. The third follows the recovery "
        "sequence and the four ways an undo fails. The fourth runs the repeat set over the chapter's six-step plan."
    ),
    "ask_skill": {
        "prompt": (
            "Replay a trace in which a request with key send-2 and payload packet-B takes effect without an acknowledgement and is "
            "then verified, with verification cost 0.5, retry cost 0.1, effect probability 0.6 and duplicate cost 4. Report the "
            "effect count, whether confirmation holds, and the blind-retry cost against the verification cost, and say which next "
            "step each unresolved state would justify."
        )
    },
    "demos": [
        {
            "id": "C17-D01",
            "title": "Send it twice: what is different afterward?",
            "question": "For which kinds of request does a repeat leave the intended effect unchanged, and what happens when a key is lost?",
            "equations": [EQ_IDEMPOTENT],
            "symbols": (
                "T is the tool, x the state of the world, eff(T, x) the state after the tool runs, and eff with subscript I "
                "keeps only the coordinates the request asked about (here the record's value). The equation says running T twice gives "
                "the same intended coordinates as running it once. Log lines are outside that projection. A safe request is read-only "
                "by its defined semantics; a key is a token the service uses to recognize a repeated request."
            ),
            "prediction": "Pick the charge with no key. After three identical requests, will the record end at 150, 200 or 250?",
            "prediction_options": ["150", "200", "250"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "Each request adds a charge: 100 + 3 x 50 = 250. The equation fails, which is why a retry after a lost reply is not safe on this evidence alone.",
                "incorrect": "With no key every request is applied: 100 + 3 x 50 = 250. Choose the charge with no key to see the bars.",
            },
            "misconception": {
                "title": "Idempotent means the reply is the same",
                "text": (
                    "The chapter says Equation (17.1) is about effects and not responses: a second DELETE can return a different status "
                    "code and still leave the same intended absence. Choose Delete: the replies differ, and the equation still holds."
                ),
            },
            "scope_note": {
                "text": (
                    "RFC 9110 governs HTTP semantics and is not a specification for agent tools; every transfer in this chapter is an "
                    "argument by analogy that the chapter states rather than assumes. Equation (17.1) covers one tool at one state and "
                    "not sequences. The retry costs and the belief numbers are constructed for teaching. Chapter 22 takes up what a "
                    "safety constraint on a measured cost can and cannot guarantee, including why it says little about state the cost "
                    "does not register."
                ),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "A read requests no change, and setting a value or deleting a record land in the same place however often they repeat, so the "
                "equation holds for all three. A charge adds again each time, so it fails. A stored key lets the service count the "
                "charge once, which restores the equation for that request, but only while the service still recognizes the key: a lost "
                "key or one past its retention window lets the repeat be applied again. The service may keep a log line per request."
            ),
            "application": (
                "Ask of every tool: if this is called twice with identical arguments, what is different afterward? "
                "Write the answer on the tool definition, because the agent cannot infer it from a name."
            ),
            "assumptions": (
                "One tool at one state, with one record and constructed values (start 100, target 150, charge 50). The "
                "equation says nothing about sequences of tools, and a key only helps if the service really deduplicates "
                "under its contract: it must say what the key identifies, whether the arguments must match, who owns it and how long "
                "it is kept. Deduplication is not queryability. The service is also constructed to log every request and to reply as shown."
            ),
            "check": "A charge of 50 with a stored key is sent 4 times from a record of 100. Where does the record end?",
            "answer": "The key makes the service count it once: 100 + 1 x 50 = 150. Without the key it would be 100 + 4 x 50 = 300, and with the key lost the same 300.",
            "provenance": "Constructed example: values defined for this reader; effects are counted with the laboratory's effect ledger, whose default trace sends two identical requests with no key and whose changed trace stores the key.",
            "source_section": "The classification the specification actually uses",
            "source_anchor": "the-classification-the-specification-actually-uses",
            "controls": [
                {"key": "kind", "label": "Kind of request (three identical requests are sent)", "values": list(KINDS), "default": "put",
                 "value_labels": list(KINDS.values())},
                {"key": "key", "label": "Key for the charge (no effect on the other kinds)", "values": list(KEYS), "default": "none",
                 "value_labels": list(KEYS.values())},
            ],
            "function": "repeat_picture",
        },
        {
            "id": "C17-D02",
            "title": "From silence to a decision: retry, decline or read",
            "question": "After no reply, how likely is it that the effect landed, and what does that belief make of a retry, a decline and a perfect read?",
            "equations": [EQ_BELIEF, EQ_RETRY],
            "symbols": (
                "Pr(applied) is the belief that the effect landed, before the silence is taken into account. Obs(silence | "
                "applied) is the probability of getting no reply when it did land, and Obs(silence | not applied) the "
                "probability of no reply when it did not (0.5 here). b'(applied) is the belief after the silence, written beta in the "
                "second equation. In the first equation the empty-set symbol stands for silence, the empty response. The cost written c "
                "with subscript miss is the cost of the action never happening (10) and c with subscript dup the cost of applying it "
                "twice. EU(retry) minus EU(decline) is how much better a retry is than leaving things alone. A perfect read reveals "
                "whether the effect landed, costs 1, creates no effect and finishes while the authorization is valid; after it the "
                "agent retries only if the effect is absent."
            ),
            "prediction": "With belief 0.30, a duplicate cost of 40 and a missing cost of 10, which action has the lowest expected cost when a perfect read costs 1?",
            "prediction_options": ["Retry", "Decline", "Read first"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "Retry costs 0.30 x 40 = 12, decline costs 0.70 x 10 = 7, and a read costs 1: its gross value is 7 and its net value 7 - 1 = 6 (workbench IV.3). The default state shows it.",
                "incorrect": "Reading first costs 1, against 12 for a retry and 7 for a decline, so it has the lowest expected cost; its net value is 7 - 1 = 6. The default state (belief 0.30, duplicate cost 40) shows it.",
            },
            "misconception": {
                "title": "A 99 percent success rate means the effect landed",
                "text": (
                    "The chapter warns that a 99 percent success rate among requests that reach a server does not by itself supply either "
                    "likelihood of silence. Choose the prior 0.99 with equal silence likelihoods: the belief stays at 0.99, and it moves "
                    "only when the two likelihoods differ, which the rate does not say."
                ),
            },
            "explanation": (
                "Bayes' rule weighs how likely silence is in each world by how likely each world was. If the likelihoods are equal they "
                "cancel and nothing changes; if silence is more likely when the effect landed, the belief rises. Equation (17.3) then "
                "prices a retry against a decline: a retry is right with chance 1 minus the belief and wrong with the belief's own chance, "
                "and the difference crosses zero at the missing cost divided by the missing cost plus the duplicate cost. A read that "
                "settles which world holds removes both losses, so it pays when the best action without it is dearer than the read. When "
                "a duplicate costs nothing, retrying is already as good as acting with the information and the read is worth nothing."
            ),
            "application": (
                "Do not turn a timeout into a probability by instinct, and do not leave the duplicate cost unpriced: a team that has "
                "never written it down has still decided, by leaving the choice to the retry library's default. Ask what the service "
                "does when the request lands and what it does when it does not, and what a status read would cost."
            ),
            "assumptions": (
                "Two worlds only (applied, not applied), constructed likelihoods with silence 0.5 likely if the request did not apply, and "
                "the chapter's teaching construction: authorized attempts, preconditions hold, a retry certainly applies the effect, no "
                "other request costs, and the original attempt can no longer apply. The read is perfect and costs 1, as in workbench IV.3. "
                "A real transport symptom rarely supplies either likelihood, and an agent that writes its own status report is feeding its "
                "own belief. A request fee, expired authority or changed version would change the comparison. The laboratory's own retry price adds the request cost to belief times duplicate cost and compares that with a verification cost; this demonstration sets the request cost to 0 and follows Equation (17.3), so the notebook default (belief 0.8, retry cost 0.2, duplicate cost 10) is a different frame from the states shown."
            ),
            "check": "Prior belief 0.2 with silence 0.9 likely if applied and 0.5 if not, a missing cost of 10 and a duplicate cost of 10. What is the belief after silence, and does a retry beat a decline?",
            "answer": "Belief = (0.9 x 0.2) / (0.9 x 0.2 + 0.5 x 0.8) = 0.18 / 0.58 = 0.310. Retry costs 0.310 x 10 = 3.10 and decline costs 0.690 x 10 = 6.90, so retry wins; the threshold is 10 / (10 + 10) = 0.50.",
            "provenance": "Constructed example: the chapter's equal-likelihood baseline and its 0.99 prior; workbench problems IV.1 (belief 0.30, duplicate cost 40, missing cost 10) and IV.3 (a perfect read for 1, and the repeatable interface with duplicate cost 0); the other likelihoods and the duplicate cost 10 are defined for this reader. The duplicate term comes from the laboratory's retry pricing.",
            "source_section": "Stage three: the retry decision, priced",
            "source_anchor": "stage-three-the-retry-decision-priced",
            "controls": [
                {"key": "prior", "label": "Belief before silence", "values": [0.3, 0.99], "default": 0.3},
                {"key": "silence_if_applied", "label": "Chance of silence if the effect landed", "values": [0.5, 0.9], "default": 0.5},
                {"key": "c_dup", "label": "Cost of a duplicate effect", "values": [0, 10, 40], "default": 40,
                 "value_labels": ["0 (idempotent interface)", "10 (balanced)", "40 (workbench IV.1)"]},
            ],
            "function": "decision_picture",
        },
        {
            "id": "C17-D03",
            "title": "Recovery before a repeat: how an undo can fail",
            "question": "When does a recovery tool count as Restored, and how can it fail to?",
            "equations": [EQ_REPEAT_SET],
            "symbols": (
                "Restored(T, x) is one of the three routes inside the braces of the equation: recovery has already succeeded and verified "
                "restoration of every relevant precondition and consequence required for another attempt. Here the relevant consequences "
                "are the four in the figure, taken from the chapter's refund example. The stages follow the chapter: observe what "
                "happened, perform an authorized repair, then verify and check the fresh attempt's preconditions."
            ),
            "prediction": "Choose the partial undo and move to stage 3. Is Restored true once the money is back?",
            "prediction_options": ["Yes: the main consequence is undone", "No: only 1 of 4 consequences is verified restored", "It cannot be decided"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Verified restored = 1 + 0 + 0 + 0 = 1 of 4, and Restored needs every relevant consequence: the refund does not retract the email, the webhook or the partner's ledger entry.",
                "incorrect": "Restored needs every relevant consequence verified, and here 1 + 0 + 0 + 0 = 1 of 4: the refund returns the money but does not retract the email, the webhook or the partner's ledger entry. Choose the partial undo and stage 3.",
            },
            "stepper": "stage",
            "misconception": {
                "title": "An undo tool restores the earlier state",
                "text": (
                    "The chapter says an undo is not a mathematical inverse: a refund is not the absence of a charge but a second transaction "
                    "that leaves two ledger entries, takes days and can itself fail. Merely having an undo tool does not establish "
                    "Restored, which denotes completed, verified recovery."
                ),
            },
            "explanation": (
                "Restored is a conclusion about a finished sequence, not about a tool. Reading the ledger shows what happened; the undo "
                "is another call with its own ways to fail: it may be absent or expired, so it cannot run; it may be partial, restoring "
                "some consequences and not others; or it may itself be lost, which repeats the retry question one level down. Only the "
                "last stage, verification of every relevant consequence, can make Restored true, and the repeat is then eligible only if "
                "Ready also holds."
            ),
            "application": (
                "Treat membership by the recovery route as a claim that needs evidence, like the observation route. Give the recovery "
                "path its own retry and escalation limits, so that an agent cannot spend its whole budget trying to clean up."
            ),
            "assumptions": (
                "The four consequences and their statuses are constructed from the chapter's refund example; a real recovery has its own "
                "list. Absent and expired are shown together because both mean no undo can run; the chapter distinguishes them (none "
                "exists, or its window closed). Verification is taken to be a reliable read; in the lost-undo outcome no verifying read has been made yet, so nothing counts as verified, and once the read is made that outcome becomes one of the other three. Outstanding attempts must also be resolved "
                "or fenced against delayed effects, which this figure does not draw."
            ),
            "check": "A refund returns the money and retracts the email, but the downstream webhook and the partner's ledger entry stay. How many of the four consequences are verified restored, and is Restored true?",
            "answer": "1 + 1 + 0 + 0 = 2 of 4, and Restored needs 4 of 4, so it is false.",
            "provenance": "Constructed example: the chapter's refund, confirmation email, downstream webhook and partner ledger entry, and its four ways an undo fails; the notebook's transfer trace (a request with a lost reply, then a read) supplies the ledger entry in stage 1 through the laboratory's effect ledger.",
            "source_section": "The four ways an undo fails",
            "source_anchor": "the-four-ways-an-undo-fails",
            "controls": [
                {"key": "stage", "label": "Stage of the recovery sequence", "values": [1, 2, 3], "default": 1,
                 "value_labels": list(STAGES.values())},
                {"key": "outcome", "label": "How the undo goes", "values": list(OUTCOMES), "default": "works",
                 "value_labels": list(OUTCOMES.values())},
            ],
            "function": "recovery_picture",
        },
        {
            "id": "C17-D04",
            "title": "Which repeats are eligible: the six-step plan",
            "question": "For each step of the duplicate-record plan, does a lost reply leave a repeat eligible?",
            "equations": [EQ_REPEAT_SET],
            "symbols": (
                "Rep(x) is the set of tools T whose repeat attempt is eligible at state x. Ready(T, x) means authority, "
                "preconditions and retry limits hold now. Absent(T, x) means authoritative proof the original never applied "
                "and cannot apply later. Restored(T, x) means recovery succeeded and was verified; none has run here. The plan is the "
                "chapter's: search, read both, write a merged record, delete the older one, notify the customer, log to an audit system."
            ),
            "prediction": "With authority current and no extra evidence, is a repeat of the customer notification (step 5) eligible?",
            "prediction_options": ["Yes, it is eligible", "No, it is not eligible"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "A second notification may send a second email, so no idempotent route holds, and nothing else is in hand: 0 + 0 + 0 = 0 routes, Ready x 0 = 0.",
                "incorrect": "Not eligible: a second notification may send a second email, so route 1 is false, and with no proof of non-application 0 + 0 + 0 = 0 routes hold. Choose step 5 with no extra evidence.",
            },
            "misconception": {
                "title": "Idempotent steps make an idempotent plan",
                "text": (
                    "The chapter says a sequence of idempotent operations is not idempotent in general, because reapplying a sequence "
                    "from the middle can interleave with what the first pass already did, and that there is no general rule that sorting "
                    "operations by membership in Rep(x) produces a valid plan. Equation (17.1) is about one tool at one state."
                ),
            },
            "explanation": (
                "Equation (17.4) is a logical gate: the request must be Ready and at least one route must hold, either idempotent "
                "semantics for this request, proof of terminal non-application, or verified restoration. Steps 3 and 4 have plausible "
                "idempotent semantics, so they pass when authority is current; steps 5 and 6 do not, so they need a read that proves the "
                "original never applied. An expired authority removes every step whatever the evidence."
            ),
            "application": (
                "Before a retry leaves, run the gate on that request, not on the plan. If it fails, the next step may be a read, a "
                "recovery, a deliberate risk decision or a person. A posterior near zero is a risk estimate, not proof of absence."
            ),
            "assumptions": (
                "The set is the chapter's conservative construction, not a rule from the HTTP standard. Steps 3 and 4 are idempotent only "
                "with stable identifiers and appropriate concurrency conditions; a record version may change between reading and writing. "
                "Steps 1 and 2 (search and read) have read-only semantics and are left out. If a read shows a request applied and "
                "complete, nothing here is repeated. Evidence goes stale: authority can expire and a version check can become out of date."
            ),
            "check": "A read proves a non-idempotent charge was applied and complete. Is the charge in Rep(x)?",
            "answer": (
                "No. Applied is not Absent, the charge is not idempotent and nothing was restored, so 0 + 0 + 0 = 0 routes "
                "hold. The request is already done, so stop."
            ),
            "provenance": "Constructed example: the chapter's six-step plan and its classification of each step; the evidence cases are defined for this reader from the chapter's own routes.",
            "source_section": "A trajectory, classified",
            "source_anchor": "a-trajectory-classified",
            "controls": [
                {"key": "step", "label": "Step whose reply was lost", "values": list(PLAN), "default": "merge",
                 "value_labels": [v[0] for v in PLAN.values()]},
                {"key": "evidence", "label": "Evidence in hand", "values": list(EVIDENCE), "default": "none",
                 "value_labels": list(EVIDENCE.values())},
            ],
            "function": "plan_picture",
        },
    ],
}

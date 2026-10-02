"""Chapter 23 reader: When the Environment Gives Instructions.

Four demonstrations built on Equations (23.1) to (23.4). Demonstration 1
checks every state against the laboratory's own security monitor
(math_ai_agents.chapters.ch23.evaluate), and Demonstration 3 checks its
version cases against the same monitor, so the reader, the notebook and the
chapter skill agree. The laboratory monitor has no recipient field, so the
recipient and document matches in Demonstration 3 are worked directly from
Equation (23.3). Every number is a constructed teaching value; the
capability set and the approved triple are the chapter's own release trace.
"""
import math

from matplotlib.patches import Rectangle

from math_ai_agents.chapters.ch23 import evaluate
from readerkit import PALETTE, argmax_set, fmt, label_point, new_figure

EQ_CONTAIN = r"\mathcal C_{\mathrm{child}}\subseteq\mathcal C_{\mathrm{parent}}"
EQ_MONITOR = r"M_{t+1}=\operatorname{Mon}(M_t,e_t)"
EQ_PUBLISH = r"\operatorname{Publish}(\delta,v,r,M_t)=1 \iff (\delta,v,r)\in\operatorname{Approved}(M_t)"
EQ_RISK = r"\operatorname{Risk}(\mathcal F)=\max_{f\in\mathcal F}\Pr[\text{violation}\mid f]"

BOX = {"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.92}


# Demonstration 1: capability containment (Equation 23.1)

EFFECTS = ["read_source", "draft_summary", "release", "send_data"]
PARENT = ["read_source", "draft_summary", "release"]  # the chapter's trace: send_data was never granted
CHILD_SETS = {
    "inherits": ["read_source", "draft_summary", "release"],
    "narrowed": ["read_source", "draft_summary"],
}


def lab_admits(child, action):
    """The laboratory monitor's capability check for one proposed action by a user-authorized path."""
    out = evaluate({
        "capabilities": list(child),
        "current_version": "v1",
        "events": [{"kind": "action", "action": action, "authority_source": "user", "version": "v1", "executed": False}],
    })
    return out["tables"][0]["monitor_allowed"]


def containment_picture(proposed="send_data", child="inherits"):
    child_set = CHILD_SETS[child]
    inside = proposed in child_set
    if lab_admits(child_set, proposed) != inside:
        raise AssertionError("laboratory monitor disagrees with set membership")
    shared = sum(1 for e in child_set if e in PARENT)
    outside = len(child_set) - shared
    fig, ax = new_figure(height=4.2)
    columns = {"Parent set": (0.0, PARENT), "Child set": (1.15, child_set)}
    for title, (x0, held) in columns.items():
        for row, effect in enumerate(EFFECTS):
            y = len(EFFECTS) - 1 - row
            has = effect in held
            ax.add_patch(Rectangle((x0, y - 0.38), 1.0, 0.76, facecolor="#cfe3e4" if has else "white",
                                   edgecolor=PALETTE["teal"] if has else PALETTE["grey"], linewidth=1.3,
                                   hatch=None if has else "///"))
            ax.text(x0 + 0.5, y, "held" if has else "not held", ha="center", va="center", fontsize=11,
                    color=PALETTE["ink"], bbox=None if has else BOX)
    row_of = {e: len(EFFECTS) - 1 - i for i, e in enumerate(EFFECTS)}
    y = row_of[proposed]
    ax.add_patch(Rectangle((-0.05, y - 0.46), 2.25, 0.92, facecolor="none", edgecolor=PALETTE["gold"], linewidth=2.2))
    verdict = "capability present" if inside else "capability absent: denied"
    ax.text(2.32, y, verdict, ha="left", va="center", fontsize=11, color=PALETTE["teal"] if inside else PALETTE["terracotta"],
            wrap=False)
    ax.set_xlim(-0.1, 3.9)
    ax.set_ylim(-0.6, len(EFFECTS) - 0.4)
    ax.set_yticks([row_of[e] for e in EFFECTS], EFFECTS)
    ax.set_xticks([0.5, 1.65], ["Parent set", "Child set"])
    ax.set_xlabel("Who holds each effect (gold box: the proposed effect)")
    ax.set_ylabel("Effect")
    ax.grid(alpha=0)
    ax.set_title(f"Child proposes {proposed}", fontsize=11.5)
    metrics = {
        "Child contained in parent (Equation 23.1)": "yes" if outside == 0 else "no",
        "Child holds the proposed effect": "yes" if inside else "no",
        "Capability check (Allowed)": "passes" if inside else "fails",
        "Still needed after a pass": "Equation (23.3) lookup" if (inside and proposed == "release") else ("none for this effect" if inside else "nothing can follow"),
    }
    if not inside and proposed in PARENT:
        reason = (f"{proposed} is not in the child set. Anything the child delegates to can hold at most a subset of the child "
                  f"set, so none of them can get {proposed} back, although the parent still holds it. The capability check "
                  "fails before any approval is consulted.")
    elif not inside:
        reason = (f"{proposed} is not in the child set, and the parent does not hold it either. Delegation only narrows a set, "
                  "so no descendant can hold it. The capability check fails before any approval is consulted.")
    elif proposed == "release":
        reason = ("Holding release only lets the request reach the lookup of Equation (23.3); it does not authorize "
                  "any particular release.")
    else:
        reason = f"{proposed} is held, so the capability check passes. It is a read or draft effect, not an external one."
    interpretation = (
        f"The child holds {len(child_set)} effects and {shared} of them are also held by the parent, so effects outside "
        f"the parent = {len(child_set)} - {shared} = {outside}. A count of 0 means the inclusion of Equation (23.1) holds. "
        f"{reason} Parent: read_source, draft_summary, release (the chapter's trace); send_data was never granted."
    )
    return fig, metrics, interpretation


# Demonstration 2: a monitor's memory (Equation 23.2)

SCENARIOS = {
    "approved": {"label": "Approval event, then quiet", "events": ["e0: approval\nevent observed", "e1: nothing\nobserved"],
                 "steps": [1, 0]},
    "claim": {"label": "Page claims approval", "events": ["e0: page says 'approved'\n(text, not an event)", "e1: nothing\nobserved"],
              "steps": [0, 0]},
    "revoked": {"label": "Approval, then user revokes", "events": ["e0: approval\nevent observed", "e1: user revokes\nthe request"],
                "steps": [1, -1]},
    "replaced": {"label": "Approval, then source replaced", "events": ["e0: approval\nevent observed", "e1: source replaced\nby version 5"],
                 "steps": [1, -1]},
}
CHECKS = {"entry": 1, "recheck": 2}  # index of the record the decision reads: M_1 (planning) or M_2 (just before effect)


def monitor_picture(scenario="revoked", check="entry"):
    spec = SCENARIOS[scenario]
    d0, d1 = spec["steps"]
    levels = [0, d0, d0 + d1]
    decided_at = CHECKS[check]
    usable_then = levels[decided_at]
    usable_now = levels[2]
    allowed = usable_then > 0
    correct = usable_now > 0
    fig, ax = new_figure(height=4.3)
    ax.plot([0, 1, 2], levels, "-", color=PALETTE["navy"], linewidth=2)
    ax.plot([0, 1, 2], levels, "o", color=PALETTE["navy"], markersize=8)
    ax.plot([decided_at], [usable_then], "o", markerfacecolor="none", markeredgecolor=PALETTE["gold"], markeredgewidth=2.6, markersize=20)
    decides = "this check decides:\nrelease allowed" if allowed else "this check decides:\nrelease denied"
    # The line only continues to the right of M1, so at M1 the label goes above the marker; at M2 the line ends, so it goes right.
    if decided_at == 1:
        label_point(ax, decided_at, usable_then, decides, color=PALETTE["gold"], dx=0, dy=18, ha="center", va="bottom").set_bbox(BOX)
    else:
        label_point(ax, decided_at, usable_then, decides, color=PALETTE["gold"], dx=16, dy=0, va="center").set_bbox(BOX)
    for i, text in enumerate(spec["events"]):
        label_point(ax, i + 0.5, 1.8, text, color=PALETTE["ink"], dx=0, dy=0, ha="center", va="center")
    ax.set_xlim(-0.2, 2.9)
    ax.set_ylim(-0.4, 2.15)
    ax.set_xticks([0, 1, 2], ["M0\nstart", "M1\nplanning check", "M2\njust before effect"])
    ax.set_yticks([0, 1], ["none", "one"])
    ax.set_xlabel("Monitor record over time (events arrive between records)")
    ax.set_ylabel("Usable approvals on file")
    mode = "Checked at planning only" if check == "entry" else "Checked again just before the effect"
    ax.set_title(f"{spec['label']}: {mode}", fontsize=11.5)
    decision = "release allowed" if allowed else "release denied"
    truth = "release allowed" if correct else "release denied"
    agree = "agrees" if allowed == correct else "WRONG: acts on old authorization"
    outcome = "it agrees" if allowed == correct else "this check is WRONG: it acts on old authorization"
    metrics = {
        "Usable approvals at M1": str(levels[1]),
        "Usable approvals at M2": str(levels[2]),
        "Decision of this check": decision,
        "Decision against the current record M2": truth,
        "This check": agree,
    }
    notes = {
        "approved": "The approval stays valid, so both ways of checking give the same answer.",
        "claim": "Mon has no argument for prose, so M never moved and nothing was ever approved.",
        "revoked": "The revocation event removed the approval after planning.",
        "replaced": "The approval was for version 4, which no longer matches the current document, so it covers nothing.",
    }
    def term(x):
        return f"+ {x}" if x >= 0 else f"- {abs(x)}"
    interpretation = (
        f"Usable approvals at M2 = 0 {term(d0)} {term(d1)} = {levels[2]}. The planning check read M1, which held {levels[1]}; "
        f"the final check reads M2, which holds {levels[2]}. {notes[scenario]} This check says {decision}; the current record "
        f"says {truth}, so {outcome}. Only observed events move the record under Equation (23.2)."
    )
    return fig, metrics, interpretation


# Demonstration 3: the release predicate (Equation 23.3)

APPROVED = ("Q3-report", "4", "external-board")
VARIANTS = {
    "none": (None, ("Q3-report", "4", "external-board")),
    "document": (0, ("Q2-report", "4", "external-board")),
    "version": (1, ("Q3-report", "5", "external-board")),
    "recipient": (2, ("Q3-report", "4", "all subscribers")),
}
FIELDS = ["document identity", "version", "recipient"]


def lab_version_check(proposed_version):
    """Laboratory monitor: a review bound to version 4 and a publish of the proposed version."""
    out = evaluate({
        "capabilities": ["release", "publish"],
        "current_version": f"v{proposed_version}",
        "events": [
            {"kind": "review", "valid": True, "version": "v4"},
            {"kind": "action", "action": "publish", "authority_source": "user", "version": f"v{proposed_version}", "executed": False},
        ],
    })
    return out["tables"][1]["monitor_allowed"]


def release_picture(changed="version", source="event"):
    index, proposed = VARIANTS[changed]
    on_file = source == "event"
    matches = [a == b for a, b in zip(APPROVED, proposed)]
    n_match = sum(matches)
    hit = on_file and all(matches)
    publish = 1 if hit else 0
    if on_file and changed in ("none", "version"):
        if lab_version_check(proposed[1]) != hit:
            raise AssertionError("laboratory monitor disagrees with the version match")
    fig, ax = new_figure(height=4.2)
    rows = [("Approved(M_t)", 2), ("Proposed release", 1),
            ("Field match" if on_file else "Match if it\nhad been recorded", 0)]
    for label, y in rows:
        ax.text(-0.08, y, label, ha="right", va="center", fontsize=11, color=PALETTE["ink"])
    for col in range(3):
        x0 = col * 1.0
        if on_file:
            ax.add_patch(Rectangle((x0 + 0.03, 1.62), 0.94, 0.76, facecolor="#e8eef3", edgecolor=PALETTE["navy"], linewidth=1.2))
            ax.text(x0 + 0.5, 2, APPROVED[col], ha="center", va="center", fontsize=10.5, color=PALETTE["ink"])
        ax.add_patch(Rectangle((x0 + 0.03, 0.62), 0.94, 0.76, facecolor="white", edgecolor=PALETTE["ink"], linewidth=1.2))
        ax.text(x0 + 0.5, 1, proposed[col], ha="center", va="center", fontsize=10.5, color=PALETTE["ink"])
        ok = matches[col]
        ax.add_patch(Rectangle((x0 + 0.03, -0.38), 0.94, 0.76, facecolor="#cfe3e4" if ok else "white",
                               edgecolor=PALETTE["teal"] if ok else PALETTE["terracotta"], linewidth=1.4, hatch=None if ok else "///"))
        word = ("matches" if ok else "differs") if on_file else ("would match" if ok else "would differ")
        ax.text(x0 + 0.5, 0, word, ha="center", va="center", fontsize=11, color=PALETTE["ink"],
                bbox=None if ok else BOX)
    if not on_file:
        ax.add_patch(Rectangle((0.03, 1.62), 2.94, 0.76, facecolor="white", edgecolor=PALETTE["terracotta"], linewidth=1.4, hatch="///"))
        ax.text(1.5, 2, "empty: the approval was only a sentence", ha="center", va="center", fontsize=11, color=PALETTE["ink"], bbox=BOX)
    ax.set_xlim(-1.35, 3.05)
    ax.set_ylim(-0.6, 2.6)
    ax.set_xticks([0.5, 1.5, 2.5], ["document identity", "version", "recipient"])
    ax.set_yticks([])
    ax.set_xlabel("Field of the triple (delta, v, r)")
    ax.set_ylabel("Record and proposal")
    ax.grid(alpha=0)
    ax.set_title(f"Publish = {publish}", fontsize=14, color=PALETTE["teal"] if publish else PALETTE["terracotta"])
    failed = [FIELDS[i] for i, ok in enumerate(matches) if not ok]
    metrics = {
        "Approval came from": "an observed event" if on_file else "a sentence in the source",
        "Fields matching": f"{n_match} of 3" + ("" if on_file else " (only if it had been recorded)"),
        "Triple is in Approved(M_t)": "yes" if hit else "no",
        "Publish (Equation 23.3)": str(publish),
        "What failed": ("nothing" if hit else (" and ".join(failed) if failed and on_file else ("no approval was ever recorded" if not on_file and not failed else "no approval recorded, and " + " and ".join(failed)))),
    }
    on_file_flag = 1 if on_file else 0
    all_flag = 1 if all(matches) else 0
    if not on_file:
        cause = ("The sentence adds nothing to Approved(M_t) because it never became an approval event; in this scenario no real "
                 "approval is on file, so even an exact match finds nothing to match against." if all(matches) else
                 "The record is empty because the sentence never became an approval event, and the proposal differs as well.")
    elif hit:
        cause = "All three fields equal the recorded triple, so the lookup succeeds."
    else:
        cause = f"The {' and '.join(failed)} differs, and no partial match counts, so the lookup fails."
    interpretation = (
        f"{'Fields matching' if on_file else 'Fields that would match if the triple had been recorded'}: {int(matches[0])} + {int(matches[1])} + {int(matches[2])} = {n_match} of 3. "
        f"Publish = {all_flag} x {on_file_flag} = {publish}, where the first number says all three fields match and the "
        f"second says the approved triple is on file from an observed event. {cause}"
    )
    return fig, metrics, interpretation


# Demonstration 4: risk over a declared family (Equation 23.4)

BASE_ATTACKS = [("Instruction\ninjection", 0.05), ("Source\npoisoning", 0.10), ("Confused-deputy\ndelegation", None)]
RETRY = ("Retry that\nskips the check", 0.45)


def risk_picture(deputy=0.30, family="three"):
    attacks = [(n, deputy if p is None else p) for n, p in BASE_ATTACKS]
    declared = family == "four"
    if declared:
        attacks.append(RETRY)
    flat = [(n.replace("\n", " "), p) for n, p in attacks]
    scores = dict(flat)
    risk = max(scores.values())
    setters = argmax_set(scores)
    mean = sum(scores.values()) / len(scores)
    fig, ax = new_figure(height=4.3)
    for i, (name, p) in enumerate(attacks):
        is_max = abs(p - risk) <= 1e-9
        ax.bar(i, p, width=0.62, color=PALETTE["terracotta"] if is_max else "#8fa3b8", edgecolor=PALETTE["ink"], linewidth=1.1,
               hatch="///" if is_max else None)
        ax.text(i, p + 0.015, fmt(p, 2), ha="center", va="bottom", fontsize=11, color=PALETTE["ink"], zorder=5, bbox=BOX)
    ax.set_xticks(range(len(attacks)), [n for n, _ in attacks])
    ax.axhline(risk, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.4)
    ax.axhline(mean, color=PALETTE["grey"], linestyle="dotted", linewidth=1.4)
    xr = 3.9
    label_point(ax, xr, risk, f"Risk {fmt(risk, 2)}", color=PALETTE["terracotta"], dx=0, dy=3, va="bottom").set_bbox(BOX)
    label_point(ax, xr, mean, f"mean {fmt(mean, 3)}", color=PALETTE["grey"], dx=0, dy=-3, va="top").set_bbox(BOX)
    if not declared:
        # Put the note at the first height that clears both reference lines (about 0.11 each).
        note_y = next(y for y in (0.17, 0.30, 0.45, 0.58) if abs(y - risk) > 0.11 and abs(y - mean) > 0.11)
        ax.text(3, note_y, "retry path\nnot declared:\nnot covered", ha="center", va="center", fontsize=10.5, color=PALETTE["grey"], bbox=BOX, zorder=5)
    ax.set_xlim(-0.6, 5.0)
    ax.set_ylim(0, 0.75)
    ax.set_xlabel("Attack in the declared family")
    ax.set_ylabel("Chance of an unauthorized effect")
    ax.set_title(f"Confused-deputy chance {fmt(deputy, 2)}; family of {len(attacks)} attacks", fontsize=11.5)
    who = " and ".join(setters)
    metrics = {
        "Risk of the declared family": fmt(risk, 2),
        "Set by": who + (" (tie)" if len(setters) > 1 else ""),
        "Mean, for contrast only": fmt(mean, 3),
        "Attacks declared": str(len(attacks)),
    }
    values = ", ".join(fmt(p, 2) for _, p in attacks)
    total = " + ".join(fmt(p, 2) for _, p in attacks)
    if len(setters) > 1:
        verdict = f"{who} tie for the maximum, so the value is the same whichever of them you look at."
    else:
        verdict = f"{who} alone sets the value; the safer members do not dilute it."
    if declared:
        scope = "The retry path is now a declared member, so the value covers it."
    else:
        scope = ("A retry path that skips the check is not in this family, so the value says nothing about it; "
                 "declaring it can only keep Risk the same or raise it.")
    interpretation = (
        f"Risk = max({values}) = {fmt(risk, 2)}. Mean for contrast = ({total}) / {len(attacks)} = {fmt(mean, 3)}. "
        f"{verdict} {scope}"
    )
    return fig, metrics, interpretation


CHAPTER = {
    "number": 23,
    "title": "When the Environment Gives Instructions: The Mathematics of Agent Security",
    "subtitle": "Untrusted text may inform a proposal, but only an observed, authorized, exactly matching event may approve an effect.",
    "summary": (
        "These four demonstrations follow the chapter's malicious-source trace. A genuine quarterly report carries one "
        "hostile sentence. You will see why a delegated child cannot gain a capability, why a sentence cannot update the "
        "monitor, why a release must match document, version and recipient, and why risk is the worst case of a declared family."
    ),
    "demos": [
        {
            "id": "C23-D01",
            "title": "A child can never hold more than its parent",
            "question": "If an injected sentence asks a delegated step to send the customer database, can any depth of delegation make that possible?",
            "equations": [EQ_CONTAIN],
            "symbols": (
                "C_parent is the set of effects the parent process may perform; C_child is the set available to anything it "
                "delegates to. The sign between them (a rounded U on its side with a bar under it) means "
                "'is contained in': every effect in the child set is also in the parent set. Effects here are read_source, "
                "draft_summary, release and send_data."
            ),
            "prediction": "The child inherits the whole parent set and the injected text asks it to use send_data. Does the capability check pass? Now narrow the child set and propose release. What changes?",
            "explanation": (
                "Equation (23.1) says delegation can narrow a capability set but never widen it. The parent in the book's trace "
                "holds read, draft and release, and send_data was never granted by any ancestor. So a proposal to send data "
                "fails the capability check whatever the text of the source says, while reading and drafting stay available."
            ),
            "application": (
                "When you give a sub-task to a tool-using helper, list the effects it needs and hand over only those. "
                "A compromised helper then cannot reach an effect that nobody above it ever held."
            ),
            "assumptions": (
                "The capability sets are the chapter's constructed trace, not a real deployment. The inclusion holds only if "
                "every delegation really passes through the check (complete mediation). It says nothing about which effects "
                "a parent should hold, and holding release does not authorize any specific release."
            ),
            "check": "A parent holds only read_source and draft_summary. A delegated child proposes release. Is the child allowed to hold release, and why?",
            "answer": "No. The child set must lie inside the parent set of 2 effects, and release is not one of them, so the child cannot hold it however many levels of delegation are added.",
            "provenance": "Constructed example: the capability sets are the chapter's malicious-source trace; the check is computed with the laboratory's own security monitor.",
            "source_section": "Data may inform; control may direct",
            "source_anchor": "data-may-inform-control-may-direct",
            "controls": [
                {"key": "proposed", "label": "Effect the child proposes", "values": EFFECTS, "default": "send_data"},
                {"key": "child", "label": "Child capability set", "values": ["inherits", "narrowed"], "default": "inherits",
                 "value_labels": ["Inherits all three parent effects", "Narrowed to read and draft"]},
            ],
            "function": "containment_picture",
        },
        {
            "id": "C23-D02",
            "title": "The monitor moves only on observed events",
            "question": "If authorization is checked once when the plan is made, what goes wrong when the world changes before the effect?",
            "equations": [EQ_MONITOR],
            "symbols": (
                "M_t is the monitor's record at time t: the capabilities, approvals and revocations in force. e_t is one observed "
                "event, such as a granted approval, a user revocation or a source replaced by a new version. Mon is the update rule "
                "that turns M_t and e_t into M_(t+1). The vertical axis counts approvals on file that still cover the current document."
            ),
            "prediction": "Choose 'Approval, then user revokes' with the check at planning only. Is the release allowed? Switch to checking again just before the effect.",
            "explanation": (
                "Under Equation (23.2) the record changes only when an event is observed, and a sentence describing an event "
                "is not an event. A check at planning reads an early record, so a revocation or a new version that arrives later "
                "is invisible to it. Checking again just before the effect reads the record as it stands then."
            ),
            "application": (
                "Re-check authority at three moments: when an action is proposed, when any material parameter changes, and "
                "immediately before the effect. Log the order, because a later acknowledgement does not show that an earlier check saw current state."
            ),
            "assumptions": (
                "Two time steps and one approval, constructed for teaching. The monitor must receive events through a channel "
                "the attacker cannot write to; if the attacker controls the permission service, the record itself cannot be trusted. "
                "The final check is taken to be the last step before the effect: no event is assumed to arrive between it and the effect."
            ),
            "check": "An approval event arrives at t = 0 and the user revokes at t = 1. How many usable approvals are on file at the end, and which check would have been wrong?",
            "answer": "Usable approvals = 0 + 1 - 1 = 0. A check made only at planning (after the approval, before the revocation) would have seen 1 and been wrong.",
            "provenance": "Constructed example: the four event sequences are defined for the reader from the chapter's discussion of revocation, replacement and unobserved claims.",
            "source_section": "A monitor's memory only advances from observed events",
            "source_anchor": "a-monitors-memory-only-advances-from-observed-events",
            "controls": [
                {"key": "scenario", "label": "What happens around the approval", "values": ["approved", "claim", "revoked", "replaced"],
                 "default": "revoked", "value_labels": [s["label"] for s in SCENARIOS.values()]},
                {"key": "check", "label": "When authority is checked", "values": ["entry", "recheck"], "default": "entry",
                 "value_labels": ["At planning only", "Again just before the effect"]},
            ],
            "function": "monitor_picture",
        },
        {
            "id": "C23-D03",
            "title": "Release needs the exact triple",
            "question": "The injected sentence says to publish. If exactly one of document, version or recipient differs from the approved triple, does the lookup still pass?",
            "equations": [EQ_PUBLISH],
            "symbols": (
                "delta is a document's identity, v its version and r the recipient. Approved(M_t) is the set of (delta, v, r) "
                "triples the monitor's record currently authorizes. Publish equals 1 only when the proposed triple is in that set, "
                "and 0 otherwise. The book's approved triple is (Q3-report, 4, external-board)."
            ),
            "prediction": "Change only the version from 4 to 5 with an approval from an observed event. What does Publish return, and which field is blamed? Then switch the approval source to a sentence in the document with nothing else changed.",
            "explanation": (
                "Equation (23.3) is a lookup, not a similarity score. One wrong field means the triple is not in the set, "
                "so the answer is 0, and a stale approval for version 4 cannot cover version 5. An approval that exists only as "
                "a sentence in the source never became an event, so it adds nothing to the set; with no real approval on file, even a perfect match is refused."
            ),
            "application": (
                "Bind an approval to every field that defines the effect (what, which revision, to whom) and record it only from an "
                "authenticated approval event. Re-approve after any revision instead of trusting that the new text looks the same."
            ),
            "assumptions": (
                "One approved triple, constructed from the book's trace. The laboratory notebook checks version and capability but has "
                "no recipient field, so the document and recipient matches are worked here from Equation (23.3) alone. A passing lookup "
                "also assumes every route to release passes through it and that the predicate is specified correctly."
            ),
            "check": "Approved(M_t) holds (Q3-report, 4, external-board). The document is revised to version 6 with no new approval event and a release to external-board is proposed. What is Publish, and which field fails?",
            "answer": "Publish = 0. Document and recipient match but the version differs (4 against 6), so the triple is not in the set. Fields matching: 1 + 0 + 1 = 2 of 3.",
            "provenance": "Constructed example: the approved triple and the three attempted releases are the chapter's own release trace; the Q2-report case is defined for the reader.",
            "source_section": "Publish needs identity, version, recipient, and current approval",
            "source_anchor": "publish-needs-identity-version-recipient-and-current-approval",
            "controls": [
                {"key": "changed", "label": "Field changed in the proposal", "values": ["none", "document", "version", "recipient"],
                 "default": "version", "value_labels": ["Nothing changed", "Different document", "Newer version (5)", "Different recipient"]},
                {"key": "source", "label": "Where the approval came from", "values": ["event", "sentence"], "default": "event",
                 "value_labels": ["An observed approval event", "A sentence in the source document"]},
            ],
            "function": "release_picture",
        },
        {
            "id": "C23-D04",
            "title": "Risk is the worst member, not the average",
            "question": "If nine attacks are blocked and one is not, what single exposure number does a declared family report?",
            "equations": [EQ_RISK],
            "symbols": (
                "F is one declared, finite family of attacks under a fixed threat model. For an attack f in F, Pr[violation | f] "
                "is the chance that f produces an unauthorized effect against the stated enforcement. Risk(F) is the largest of those "
                "chances. The chances in the figure are values defined for the reader, not measurements."
            ),
            "prediction": "Raise the confused-deputy chance from 0.30 to 0.60 with three declared attacks. How do Risk and the mean each change? Then declare the retry path at 0.30.",
            "explanation": (
                "Equation (23.4) takes a maximum over the family, so one dangerous member sets the value no matter how many "
                "safe ones surround it. An average would let the safe attacks hide the dangerous one. The value is also only about the "
                "attacks that were declared: a path that was never named is outside the guarantee."
            ),
            "application": (
                "When reporting security, name the attack family first and report the worst member for each enforcement mechanism. "
                "Add any unmediated route you discover to the family instead of leaving it out of the number, and close the route: adding it to the family only measures it."
            ),
            "assumptions": (
                "A threat-model measure, not an empirical security rate and not a proof. It presumes complete mediation and a "
                "correctly specified predicate. The chances here are constructed; an attack outside the family, or a monitor with "
                "a specification gap, is not covered by the value."
            ),
            "check": "A declared family has violation chances 0.20, 0.35, 0.05 and 0.35. What is Risk, and what is the mean?",
            "answer": "Risk = max(0.20, 0.35, 0.05, 0.35) = 0.35, set by the two members tied at 0.35. The mean = (0.20 + 0.35 + 0.05 + 0.35) / 4 = 0.2375, which is not the reported value.",
            "provenance": "Constructed example: the three attack names are the chapter's declared family and the retry path is its unmediated-call example; every chance is defined for the reader.",
            "source_section": "A security case needs a declared adversary",
            "source_anchor": "a-security-case-needs-a-declared-adversary",
            "controls": [
                {"key": "deputy", "label": "Chance for the confused-deputy attack", "values": [0.02, 0.1, 0.3, 0.6], "default": 0.3},
                {"key": "family", "label": "Declared family", "values": ["three", "four"], "default": "three",
                 "value_labels": ["Three attacks", "Three plus the retry path (0.45)"]},
            ],
            "function": "risk_picture",
        },
    ],
}

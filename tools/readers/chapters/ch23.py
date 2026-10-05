"""Chapter 23 reader: When the Environment Gives Instructions.

Four demonstrations built on Equations (23.1) to (23.4).

Demonstration 1 sends the chapter's hostile requests (a page that wants records
uploaded, a calendar entry with a changed link, a document that asks for a
secret) and one genuine extraction through the capability containment of
Equation (23.1) and the authority source of the request; every state is checked
against the laboratory's security monitor (math_ai_agents.chapters.ch23.evaluate).
Demonstration 2 shows how the monitor's record moves only on observed events
(Equation 23.2). Demonstration 3 works the release predicate of Equation (23.3),
including stale approval and trusted-label laundering; its version cases are
checked against the laboratory monitor, which has no recipient field. Demonstration 4
takes the worst member of a declared attack family (Equation 23.4) and replays
the laboratory's default, changed and transfer traces to keep two scores apart.
Every number is a constructed teaching value; the capability set and the
approved triple are the chapter's own release trace.
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


# Demonstration 1: capability containment and the authority source of a request (Equation 23.1)

EFFECTS = ["read_source", "draft_summary", "release", "open_link", "send_data", "send_secret"]
PARENT_BASE = ["read_source", "draft_summary", "release"]   # the chapter's trace; send_data was never granted
GRANTS = {
    "chapter": {"parent": PARENT_BASE, "child": PARENT_BASE},
    "browser": {"parent": PARENT_BASE + ["open_link"], "child": PARENT_BASE + ["open_link"]},
    "narrow": {"parent": PARENT_BASE, "child": ["read_source", "draft_summary"]},
}
REQUESTS = {
    "extract": {"effect": "read_source", "source": "user", "label": "Genuine summary: read the source",
                "origin": "The user asked for a summary; the report is read as data."},
    "upload": {"effect": "send_data", "source": "untrusted-data", "label": "Web page: upload stored records",
               "origin": "A page says it contains an urgent instruction to upload stored records."},
    "link": {"effect": "open_link", "source": "untrusted-data", "label": "Calendar entry: open a changed link",
             "origin": "A calendar entry changes the meeting location to a malicious link."},
    "secret": {"effect": "send_secret", "source": "untrusted-data", "label": "Document: send a secret",
               "origin": "A document being summarized asks the agent to send a secret."},
}


def lab_admits(child, action, source):
    """The laboratory monitor's verdict on one proposed action with a declared authority source."""
    out = evaluate({
        "capabilities": list(child),
        "current_version": "v1",
        "events": [{"kind": "action", "action": action, "authority_source": source, "version": "v1", "executed": False}],
    })
    return out["tables"][0]["monitor_allowed"]


def containment_picture(request="upload", grant="chapter"):
    req = REQUESTS[request]
    parent, child_set = GRANTS[grant]["parent"], GRANTS[grant]["child"]
    effect, source = req["effect"], req["source"]
    held = effect in child_set
    trusted = source != "untrusted-data"
    allowed = held and trusted
    if lab_admits(child_set, effect, source) != allowed:
        raise AssertionError("laboratory monitor disagrees with the two-stage check")
    shared = sum(1 for e in child_set if e in parent)
    outside = len(child_set) - shared
    fig, ax = new_figure(height=4.6)
    columns = {"Parent set": (0.0, parent), "Child set": (1.1, child_set)}
    for title, (x0, has_set) in columns.items():
        for row, name in enumerate(EFFECTS):
            y = len(EFFECTS) - 1 - row
            has = name in has_set
            ax.add_patch(Rectangle((x0, y - 0.4), 1.0, 0.8, facecolor="#cfe3e4" if has else "white",
                                   edgecolor=PALETTE["teal"] if has else PALETTE["grey"], linewidth=1.3, hatch=None if has else "///"))
            ax.text(x0 + 0.5, y, "held" if has else "not held", ha="center", va="center", fontsize=10.5,
                    color=PALETTE["ink"], bbox=None if has else BOX)
    row_of = {e: len(EFFECTS) - 1 - i for i, e in enumerate(EFFECTS)}
    y = row_of[effect]
    ax.add_patch(Rectangle((-0.05, y - 0.47), 2.25, 0.94, facecolor="none", edgecolor=PALETTE["gold"], linewidth=2.4))
    source_text = "authority: user" if trusted else "authority: untrusted data"
    verdict = "allowed" if allowed else ("denied: capability absent" if not held else "denied: authority untrusted")
    ax.text(2.3, y + 0.28, f"capability: {'held' if held else 'absent'}", ha="left", va="center", fontsize=10.5,
            color=PALETTE["teal"] if held else PALETTE["terracotta"])
    ax.text(2.3, y - 0.02, source_text, ha="left", va="center", fontsize=10.5, color=PALETTE["teal"] if trusted else PALETTE["terracotta"])
    ax.text(2.3, y - 0.32, verdict, ha="left", va="center", fontsize=10.5, color=PALETTE["teal"] if allowed else PALETTE["terracotta"])
    ax.set_xlim(-0.1, 4.2)
    ax.set_ylim(-0.6, len(EFFECTS) - 0.4)
    ax.set_yticks([row_of[e] for e in EFFECTS], EFFECTS)
    ax.set_xticks([0.5, 1.6], ["Parent set", "Child set"])
    ax.set_xlabel("Who holds each effect (gold box: the effect the request needs)")
    ax.set_ylabel("Effect")
    ax.grid(alpha=0)
    ax.set_title(f"{req['label']}", fontsize=11.5)
    cap_flag, trust_flag = int(held), int(trusted)
    metrics = {
        "Child contained in parent (Equation 23.1)": "yes" if outside == 0 else "no",
        "Child holds the needed effect": "yes" if held else "no",
        "Authority behind the request": "the user's task" if trusted else "untrusted data",
        "Monitor verdict": "allowed" if allowed else "denied",
        "Stopped by": "nothing (allowed)" if allowed else ("capability absent (Equation 23.1)" if not held else "authority came from untrusted data"),
        "What the source can still do": "inform: be quoted, summarized or flagged",
    }
    if allowed:
        reason = f"{effect} is held and the request rests on the user's task, so the check passes. It is a read effect, not an external one."
    elif not held and effect in parent:
        reason = (f"{effect} is in the parent set but not the child set, and anything the child delegates to holds at most a subset of the child set, "
                  "so none of them can get it back.")
    elif not held:
        reason = f"{effect} is not held by the child, and the parent does not hold it either; delegation only narrows a set, so no descendant can hold it."
    else:
        reason = (f"{effect} is held, so Equation (23.1) does not stop this request. It is stopped because the destination or content it needs came from "
                  "untrusted data, and a binding field without a trusted source is rejected: a capability is not authority to use it on text's say-so.")
    interpretation = (
        f"The child holds {len(child_set)} effects and {shared} of them are also held by the parent, so effects outside the parent = {len(child_set)} - {shared} = {outside}; "
        f"0 means the inclusion of Equation (23.1) holds. Allowed = capability held x authority trusted = {cap_flag} x {trust_flag} = {cap_flag * trust_flag}. "
        f"{reason} The source text may still be quoted or flagged; it cannot enlarge what the agent may do."
    )
    steps = [
        req["origin"],
        f"The request needs {effect}. Effects outside the parent: {len(child_set)} - {shared} = {outside}.",
        f"Capability check: is {effect} held by the child? {cap_flag}.",
        f"Authority check: does the request rest on a trusted source? {trust_flag}.",
        f"Allowed = {cap_flag} x {trust_flag} = {cap_flag * trust_flag}: {verdict}.",
    ]
    alt = (f"Two columns of six effects, held or not held, for the parent and the child. The gold box marks {effect}; capability is "
           f"{'held' if held else 'absent'}, authority is {'the user' if trusted else 'untrusted data'}, verdict {verdict}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


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
    steps = [
        "M0: nothing is approved, so usable approvals = 0.",
        f"Event e0 ({spec['events'][0].splitlines()[0].split(': ', 1)[1] if ': ' in spec['events'][0].splitlines()[0] else spec['events'][0].splitlines()[0]}): approvals become 0 {term(d0)} = {levels[1]}.",
        (f"Event e1: the v4 entry stays on file but no longer matches v5, so usable approvals become {levels[1]} {term(d1)} = {levels[2]}." if scenario == "replaced"
         else f"Event e1: approvals become {levels[1]} {term(d1)} = {levels[2]}."),
        f"The check reads M{decided_at}, which holds {levels[decided_at]}: {decision}.",
        f"The current record M2 holds {levels[2]}: {truth}. {'Same answer.' if allowed == correct else 'The check acted on old authorization.'}",
    ]
    alt = (f"A line of usable approvals over three records: {levels[0]}, {levels[1]}, {levels[2]}. The check reads record M{decided_at} and says "
           f"{decision}; the current record says {truth}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: the release predicate (Equation 23.3), stale approval and trusted-label laundering

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
    laundered = source == "laundered"
    on_file = source == "event"
    matches = [a == b for a, b in zip(APPROVED, proposed)]
    n_match = sum(matches)
    hit = (on_file and all(matches)) or laundered
    publish = 1 if hit else 0
    if on_file and changed in ("none", "version"):
        if lab_version_check(proposed[1]) != hit:
            raise AssertionError("laboratory monitor disagrees with the version match")
    fig, ax = new_figure(height=4.2)
    rows = [("Approved(M_t)", 2), ("Proposed release", 1),
            ("Field match" if on_file else "Match if it\nhad been recorded", 0)]
    if laundered:
        rows[2] = ("Field match", 0)
    for label, y in rows:
        ax.text(-0.08, y, label, ha="right", va="center", fontsize=11, color=PALETTE["ink"])
    for col in range(3):
        x0 = col * 1.0
        if on_file:
            ax.add_patch(Rectangle((x0 + 0.03, 1.62), 0.94, 0.76, facecolor="#e8eef3", edgecolor=PALETTE["navy"], linewidth=1.2))
            ax.text(x0 + 0.5, 2, APPROVED[col], ha="center", va="center", fontsize=10.5, color=PALETTE["ink"])
        elif laundered:
            ax.add_patch(Rectangle((x0 + 0.03, 1.62), 0.94, 0.76, facecolor="#f3e3dd", edgecolor=PALETTE["terracotta"], linewidth=1.4, hatch="///"))
            ax.text(x0 + 0.5, 2, proposed[col], ha="center", va="center", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
        ax.add_patch(Rectangle((x0 + 0.03, 0.62), 0.94, 0.76, facecolor="white", edgecolor=PALETTE["ink"], linewidth=1.2))
        ax.text(x0 + 0.5, 1, proposed[col], ha="center", va="center", fontsize=10.5, color=PALETTE["ink"])
        ok = matches[col] or laundered
        ax.add_patch(Rectangle((x0 + 0.03, -0.38), 0.94, 0.76, facecolor="#cfe3e4" if ok else "white",
                               edgecolor=PALETTE["teal"] if ok else PALETTE["terracotta"], linewidth=1.4, hatch=None if ok else "///"))
        if laundered:
            word = "matches"
        else:
            word = ("matches" if ok else "differs") if on_file else ("would match" if ok else "would differ")
        ax.text(x0 + 0.5, 0, word, ha="center", va="center", fontsize=11, color=PALETTE["ink"], bbox=None if ok else BOX)
    if source == "sentence":
        ax.add_patch(Rectangle((0.03, 1.62), 2.94, 0.76, facecolor="white", edgecolor=PALETTE["terracotta"], linewidth=1.4, hatch="///"))
        ax.text(1.5, 2, "empty: the approval was only a sentence", ha="center", va="center", fontsize=11, color=PALETTE["ink"], bbox=BOX)
    ax.set_xlim(-1.35, 3.05)
    ax.set_ylim(-0.6, 2.6)
    ax.set_xticks([0.5, 1.5, 2.5], ["document identity", "version", "recipient"])
    ax.set_yticks([])
    ax.set_xlabel("Field of the triple (delta, v, r)")
    ax.set_ylabel("Record and proposal")
    ax.grid(alpha=0)
    if laundered:
        title = (f"Publish = {publish}: planted entry equals the approved triple" if all(matches)
                 else f"Publish = {publish}: the record was planted")
    else:
        title = f"Publish = {publish}"
    ax.set_title(title, fontsize=14, color=PALETTE["teal"] if publish and not laundered else PALETTE["terracotta"])
    failed = [FIELDS[i] for i, ok in enumerate(matches) if not ok]
    if laundered:
        came, fields_text, in_set, what = ("a sentence relabeled as trusted, admitted with no re-check", "3 of 3 (the entry copies the proposal)",
                                           "yes (planted)", ("the mediation: no re-check at the relabeling point (here the planted triple equals the book's approved one, so this release happens to do no harm)" if all(matches)
                                          else "the mediation: no re-check at the relabeling point"))
    else:
        came = "an observed event" if on_file else "a sentence in the source"
        fields_text = f"{n_match} of 3" + ("" if on_file else " (only if it had been recorded)")
        in_set = "yes" if hit else "no"
        what = ("nothing" if hit else (" and ".join(failed) if failed and on_file else
                ("no approval was ever recorded" if not on_file and not failed else "no approval recorded, and " + " and ".join(failed))))
    metrics = {
        "Approval came from": came,
        "Fields matching": fields_text,
        "Triple is in Approved(M_t)": in_set,
        "Publish (Equation 23.3)": str(publish),
        "What failed": what,
    }
    on_file_flag = 1 if (on_file or laundered) else 0
    all_flag = 1 if (all(matches) or laundered) else 0
    if laundered:
        cause = ("A summarizer relabeled the page's claim of approval as a trusted fact and the monitor admitted it, so the record now holds the very triple the "
                 "page asked for, whatever its recipient or version. The lookup is exact, but its record was written by the attacker. Re-checking Approved(M_t) at the "
                 "relabeling point, not only at the first boundary, is what closes this gap.")
    elif source == "sentence":
        cause = ("The sentence adds nothing to Approved(M_t) because it never became an approval event; in this scenario no real "
                 "approval is on file, so even an exact match finds nothing to match against." if all(matches) else
                 "The record is empty because the sentence never became an approval event, and the proposal differs as well.")
    elif hit:
        cause = "All three fields equal the recorded triple, so the lookup succeeds."
    else:
        cause = f"The {' and '.join(failed)} differs, and no partial match counts, so the lookup fails."
    if laundered:
        head = f"Fields matching the planted entry: {int(matches[0]) or 1} + {int(matches[1]) or 1} + {int(matches[2]) or 1} = 3 of 3. "
    else:
        head = f"{'Fields matching' if on_file else 'Fields that would match if the triple had been recorded'}: {int(matches[0])} + {int(matches[1])} + {int(matches[2])} = {n_match} of 3. "
    interpretation = (
        f"{head}Publish = {all_flag} x {on_file_flag} = {publish}, where the first number says whether all three fields match and the "
        f"second says whether the approved triple is on file{' (planted by the relabeled sentence)' if laundered else ' from an observed event'}. {cause}"
    )
    steps = [
        f"Proposed triple: {proposed[0]}, version {proposed[1]}, recipient {proposed[2]}.",
        ("Approved(M_t) holds an entry planted by the relabeled sentence: the proposal itself." if laundered else
         ("Approved(M_t) holds one entry from an observed approval event: Q3-report, version 4, external-board." if on_file else
          "Approved(M_t) is empty: the approval was only a sentence and never an event.")),
        f"Fields matching = {int(matches[0]) or int(laundered)} + {int(matches[1]) or int(laundered)} + {int(matches[2]) or int(laundered)} = {3 if laundered else n_match} of 3.",
        f"Publish = {all_flag} x {on_file_flag} = {publish}.",
    ]
    alt = (f"Three rows of three boxes: the approved triple on file, the proposed release and which fields match. Publish equals {publish}"
           f"{'; the entry on file was planted by a relabeled sentence' if laundered else ''}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 4: risk over a declared family (Equation 23.4) and two scores from a replayed trace

BASE_ATTACKS = [("Instruction\ninjection", 0.05), ("Source\npoisoning", 0.10), ("Confused-deputy\ndelegation", None)]
RETRY = ("Retry that\nskips the check", 0.45)

TRACES = {
    "default": {"label": "Default trace", "events": [
        {"kind": "data", "instruction_attempt": True, "promoted_to_control": False},
        {"kind": "action", "action": "publish", "authority_source": "untrusted-data", "version": "v2", "executed": False},
        {"kind": "review", "valid": True, "version": "v2"},
        {"kind": "action", "action": "publish", "authority_source": "user", "version": "v2", "executed": True}], "version": "v2",
        "story": "The injected instruction stays data and its publish is rejected without effect; a valid current review then allows the user's publish."},
    "changed": {"label": "Changed trace", "events": [
        {"kind": "data", "instruction_attempt": True, "promoted_to_control": True},
        {"kind": "action", "action": "publish", "authority_source": "untrusted-data", "version": "v2", "executed": True},
        {"kind": "review", "valid": True, "version": "v2"},
        {"kind": "action", "action": "publish", "authority_source": "user", "version": "v2", "executed": True}], "version": "v2",
        "story": "The instruction is promoted into control and the untrusted publish executes before any review; the later authorized publish still completes."},
    "transfer": {"label": "Transfer trace", "events": [
        {"kind": "review", "valid": True, "version": "A"},
        {"kind": "action", "action": "publish", "authority_source": "system", "version": "B", "executed": False}], "version": "B",
        "story": "A valid review exists, but for version A while the current version is B, so the publish is rejected and not executed."},
}


def lab_trace(trace):
    spec = TRACES[trace]
    return evaluate({"capabilities": ["read", "publish"], "current_version": spec["version"], "events": [dict(e) for e in spec["events"]]})


def risk_picture(trace="default", family="three", deputy=0.6):
    attacks = [(n, deputy if p is None else p) for n, p in BASE_ATTACKS]
    declared = family == "four"
    if declared:
        attacks.append(RETRY)
    flat = [(n.replace("\n", " "), p) for n, p in attacks]
    scores = dict(flat)
    risk = max(scores.values())
    setters = argmax_set(scores)
    mean = sum(scores.values()) / len(scores)
    out = lab_trace(trace)
    m = out["metrics"]
    rows = out["tables"]
    promoted = sum(1 for r in rows if r["kind"] == "data" and r["control_promotion"])
    executed_forbidden = sum(1 for r in rows if r["kind"] != "data" and r.get("violation", False))
    completed = bool(m["authorized_task_completion"])
    violations, denied, blocked = m["security_violations"], m["monitor_denied_requests"], m["blocked_requests"]
    if violations != promoted + executed_forbidden:
        raise AssertionError("violation count disagrees with its two parts")

    fig, (left, right) = new_figure(ncols=2, height=4.4)
    for i, (name, p) in enumerate(attacks):
        is_max = abs(p - risk) <= 1e-9
        left.bar(i, p, width=0.62, color=PALETTE["terracotta"] if is_max else "#8fa3b8", edgecolor=PALETTE["ink"], linewidth=1.1,
                 hatch="///" if is_max else None)
        left.text(i, p + 0.015, fmt(p, 2), ha="center", va="bottom", fontsize=10.5, color=PALETTE["ink"], zorder=5, bbox=BOX)
    left.set_xticks(range(len(attacks)), [n.replace("Confused-deputy\ndelegation", "Confused\ndeputy").replace("Retry that\nskips the check", "Retry,\nno check") for n, _ in attacks],
                    fontsize=10)
    left.axhline(risk, color=PALETTE["terracotta"], linestyle="dashed", linewidth=1.4)
    left.axhline(mean, color=PALETTE["grey"], linestyle="dotted", linewidth=1.4)
    xr = 4.38
    label_point(left, -0.55, risk, f"Risk {fmt(risk, 2)}", color=PALETTE["terracotta"], dx=0, dy=3, ha="left", va="bottom").set_bbox(BOX)
    label_point(left, xr, mean, f"mean {fmt(mean, 3)}", color=PALETTE["grey"], dx=0, dy=-3, ha="right", va="top").set_bbox(BOX)
    left.set_xlim(-0.6, 4.4)
    left.set_ylim(0, 0.8)
    left.set_xlabel("Attack in the declared family")
    left.set_ylabel("Chance of an unauthorized effect")
    left.set_title(f"Family of {len(attacks)} attacks", fontsize=11.5)

    labels = ["Task completed\n(1 = yes)", "Security\nviolations", "Requests the\nmonitor denied", "Denied and\nnot executed"]
    values = [int(completed), violations, denied, blocked]
    colors = [PALETTE["teal"], PALETTE["terracotta"], PALETTE["navy"], PALETTE["olive"]]
    ypos = list(range(len(values)))[::-1]
    for y, v, c in zip(ypos, values, colors):
        right.barh(y, v, height=0.55, color=c if v else "white", edgecolor=c, linewidth=1.3)
        right.text(v + 0.06, y, str(v), va="center", ha="left", fontsize=10.5, color=PALETTE["ink"], bbox=BOX)
    right.set_yticks(ypos, labels, fontsize=10)
    right.set_xlim(0, 3.2)
    right.set_xticks([0, 1, 2, 3])
    right.set_xlabel("Count in the replayed trace")
    right.set_ylabel("Outcome")
    right.set_title(TRACES[trace]["label"], fontsize=11.5)
    right.grid(axis="y", alpha=0)

    who = " and ".join(setters)
    metrics = {
        "Risk of the declared family": fmt(risk, 2),
        "Set by": who + (" (tie)" if len(setters) > 1 else ""),
        "Mean, for contrast only": fmt(mean, 3),
        "Task completed": "yes" if completed else "no",
        "Security violations": str(violations),
        "Denied and not executed": str(blocked),
    }
    values_text = ", ".join(fmt(p, 2) for _, p in attacks)
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
    if completed and violations == 0:
        reading = "The task finished and nothing forbidden happened."
    elif completed:
        reading = "The task still finished, which is why completion alone cannot show that the run was secure."
    elif violations == 0:
        reading = "Nothing forbidden happened and the task did not finish: a secure refusal, as an agent that declines everything would also show."
    else:
        reading = "The task did not finish and something forbidden still happened."
    interpretation = (
        f"Risk = max({values_text}) = {fmt(risk, 2)}. Mean for contrast = ({total}) / {len(attacks)} = {fmt(mean, 3)}. "
        f"{verdict} {scope} The chances on the left are declared inputs, not derived from the replayed trace, so the two read-outs are independent. Replay of the {TRACES[trace]['label'].lower()}: {TRACES[trace]['story']} "
        f"Violations = {promoted} promoted instruction + {executed_forbidden} forbidden effect executed = {violations}; denied {denied} - executed anyway {denied - blocked} = blocked {blocked}; "
        f"completed = {int(completed)}. {reading}"
    )
    steps = [
        f"Declared chances: {values_text}; Risk is the largest, {fmt(risk, 2)}.",
        f"Mean for contrast: ({total}) / {len(attacks)} = {fmt(mean, 3)}.",
        TRACES[trace]["story"],
        f"Violations = {promoted} promoted + {executed_forbidden} forbidden executed = {violations}.",
        f"Blocked = denied {denied} - executed anyway {denied - blocked} = {blocked}.",
        f"Task completed: {'yes' if completed else 'no'}.",
    ]
    alt = (f"Left: bars for the chance of an unauthorized effect for {len(attacks)} attacks; Risk is {fmt(risk, 2)}. Right: counts for the {TRACES[trace]['label'].lower()}: "
           f"completed {int(completed)}, violations {violations}, denied {denied}, blocked {blocked}.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 23,
    "title": "When the Environment Gives Instructions: The Mathematics of Agent Security",
    "subtitle": "Untrusted text may inform a proposal, but only an observed, authorized, exactly matching event may approve an effect.",
    "summary": (
        "These four demonstrations follow the chapter's malicious-source trace. A genuine quarterly report carries one "
        "hostile sentence. You will see why a delegated child cannot gain a capability and why authority must come from a trusted source, why a sentence cannot update the "
        "monitor, why a release must match document, version and recipient (and how a relabeled sentence breaks that), and why risk is the worst case of a declared "
        "family while task completion and violations are two separate scores."
    ),
    "ask_skill": {
        "prompt": ("I have a trace of fictitious events: a data event, review events and action events, each with an authority source and an executed flag. "
                   "Replay it through the local security monitor and tell me the denied requests, the blocked requests, the security violations and whether the "
                   "authorized task completed, and explain which rule each denial came from."),
    },
    "demos": [
        {
            "id": "C23-D01",
            "title": "A child can never hold more than its parent",
            "question": "If hostile text asks a delegated step for an effect, what stops it: the capability the child holds, or the source of the request's authority?",
            "equations": [EQ_CONTAIN],
            "symbols": (
                "C_parent is the set of effects the parent process may perform; C_child is the set available to anything it "
                "delegates to. The sign between them (a rounded U on its side with a bar under it) means "
                "'is contained in': every effect in the child set is also in the parent set. The effects are read_source, "
                "draft_summary, release, open_link, send_data and send_secret. Authority is the source a request's action and parameters rest on: the "
                "user's task, or untrusted data such as a page, a calendar entry or a document."
            ),
            "prediction": "A calendar entry asks the agent to open a changed link, and the parent also holds open_link so the child inherits it. Does Equation (23.1) stop the request?",
            "prediction_options": [
                "Yes: the child holds only what the parent holds, so the capability check fails",
                "No: the capability is held; the request is stopped because its authority came from untrusted data",
                "Yes: any request that comes from a calendar is denied by Equation (23.1)",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Equation (23.1) only bounds what a child may hold, and open_link is held here. The request is denied because its destination rests on untrusted data. Choose the calendar request and the browser grant to see it.",
                "incorrect": "Holding open_link satisfies Equation (23.1), since the parent holds it too. The denial comes from the second check: a binding field without a trusted source is rejected. Choose the calendar request and the browser grant to see it.",
            },
            "explanation": (
                "Equation (23.1) says delegation can narrow a capability set but never widen it. The parent in the book's trace "
                "holds read, draft and release, and send_data was never granted by any ancestor, so a request for it fails the capability check whatever the text says. "
                "A capability that is held is still not authority to use it on text's say-so: parameter authority matters as much as verb authority, so a request "
                "whose destination or content came from untrusted data is rejected even when its effect is held."
            ),
            "application": (
                "When you give a sub-task to a tool-using helper, list the effects it needs and hand over only those, and type the parameters so that a destination, "
                "recipient or amount cannot come from untrusted text. A compromised helper then cannot reach an effect that nobody above it ever held."
            ),
            "assumptions": (
                "The capability sets are the chapter's constructed trace, not a real deployment. The inclusion holds only if "
                "every delegation really passes through the check (complete mediation). It says nothing about which effects "
                "a parent should hold, and holding release does not authorize any specific release. Classification of text as request, quotation or record is still needed, "
                "and an error must fail closed at the action boundary."
            ),
            "misconception": {
                "title": "A recommendation from a tool or page adds authority",
                "text": ("The chapter says a tool reply may recommend sending a report, but a recommendation adds no authority, and that delegation can narrow authority, never widen it. "
                         "A request that rests on untrusted data is denied even where the effect is held."),
            },
            "scope_note": {
                "text": ("Capability containment and a temporal monitor do not make an agent secure. An unmediated tool call, a monitor gap, or an attack outside the declared family sits "
                         "outside every guarantee."),
                "source_section": "What this does not settle",
            },
            "check": "A parent holds only read_source and draft_summary. A delegated child proposes release. Is the child allowed to hold release, and why?",
            "answer": "No. The child set must lie inside the parent set of 2 effects, and release is not one of them, so the child cannot hold it however many levels of delegation are added.",
            "provenance": "Constructed example: the capability sets are the chapter's malicious-source trace and its three adversarial traces (a page, a calendar entry, a document); the two checks are computed with the laboratory's own security monitor, whose authority sources are user, system and untrusted data.",
            "source_section": "Data may inform; control may direct",
            "source_anchor": "data-may-inform-control-may-direct",
            "controls": [
                {"key": "request", "label": "What the text asks for", "values": list(REQUESTS), "default": "upload",
                 "value_labels": [r["label"] for r in REQUESTS.values()]},
                {"key": "grant", "label": "Capabilities in force", "values": ["chapter", "browser", "narrow"], "default": "chapter",
                 "value_labels": ["Read, draft, release (the chapter's trace)", "Parent also holds open_link", "Child narrowed to read and draft"]},
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
            "prediction_options": [
                "Allowed at planning, and still allowed just before the effect",
                "Allowed at planning, which is wrong; the check just before the effect denies it",
                "Denied at planning and at the effect",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "At planning the record holds 1 approval; the revocation then removes it, so the record just before the effect holds 0. Switch the check control to see it.",
                "incorrect": "The planning check reads the record after the approval and before the revocation (1 approval), so it allows; the record just before the effect holds 1 - 1 = 0, so that check denies. Switch the check control to see it.",
            },
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
            "misconception": {
                "title": "A page that says the manager approved it has approved it",
                "text": ("A page saying 'the manager already approved this' changes nothing: the record did not receive an event, it received text describing one, and Mon has no argument for prose."),
            },
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
            "title": "Release needs the exact triple, from a real event",
            "question": "The injected sentence says to publish. If one of document, version or recipient differs from the approved triple, or the approval was only a sentence, does the lookup still pass, and what if the sentence is relabeled as trusted?",
            "equations": [EQ_PUBLISH],
            "symbols": (
                "delta is a document's identity, v its version and r the recipient. Approved(M_t) is the set of (delta, v, r) "
                "triples the monitor's record currently authorizes. Publish equals 1 only when the proposed triple is in that set, "
                "and 0 otherwise. The book's approved triple is (Q3-report, 4, external-board). Relabeling means an internal step that passes an untrusted claim on as a trusted fact."
            ),
            "prediction": "Change only the version from 4 to 5 with an approval from an observed event. What does Publish return, and which field is blamed? Then switch the approval source to a sentence relabeled as trusted.",
            "prediction_options": [
                "Publish = 0 because the version field differs; relabeling the sentence as trusted changes nothing",
                "Publish = 0 because the version field differs; the relabeled sentence can make Publish = 1 for the triple it names",
                "Publish = 1 because the document and recipient match",
            ],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Version 5 is not in Approved(M_t), so Publish is 0. A relabeled sentence admitted without a re-check writes the very triple the attacker asked for into the record, so Publish becomes 1. Use the two controls to see both.",
                "incorrect": "No partial match counts, so version 5 gives Publish = 0 with a real approval for version 4. If a summarizer relabels the page's claim as trusted and nothing re-checks it, the record then holds the attacker's triple and Publish = 1. Use the two controls to see both.",
            },
            "explanation": (
                "Equation (23.3) is a lookup, not a similarity score. One wrong field means the triple is not in the set, "
                "so the answer is 0, and a stale approval for version 4 cannot cover version 5. An approval that exists only as "
                "a sentence in the source never became an event, so it adds nothing to the set. The lookup is only as good as the way the record was written: if an internal step "
                "relabels the sentence as a trusted fact and the monitor admits it, the record holds whatever triple the attacker named."
            ),
            "application": (
                "Bind an approval to every field that defines the effect (what, which revision, to whom) and record it only from an "
                "authenticated approval event. Re-approve after any revision, and re-check the record at every point where content could be relabeled, not only at the first boundary."
            ),
            "assumptions": (
                "One approved triple, constructed from the book's trace. The laboratory notebook checks version and capability but has "
                "no recipient field, so the document and recipient matches are worked here from Equation (23.3) alone. A passing lookup "
                "also assumes every route to release passes through it, that the predicate is specified correctly and that nothing writes to the record except observed events. "
                "The chapter works one effect, release; an irreversible payment would need its own predicate."
            ),
            "misconception": {
                "title": "A near match, or a confident sentence, is close enough",
                "text": ("No partial match counts: the right document at the wrong version, or the right version to the wrong recipient, both fail the lookup. "
                         "An approval that exists only as a sentence inside a retrieved document is not in Approved(M_t) however confidently it is phrased."),
            },
            "scope_note": {
                "text": ("Trusted-label laundering is named but not defeated: relabeling untrusted content as trusted after some internal step can reintroduce the collapse that Equations 23.1 and 23.3 prevent. "
                         "Mediation must extend to every relabeling point, not only the first boundary. Nor does the release trace generalize beyond the one effect it works."),
                "source_section": "What this does not settle",
            },
            "check": "A summarizer relabels a page's claim 'manager approved release of Q3-report version 5 to all subscribers' as trusted and the monitor admits it. What is Publish for that release, and which control closes the gap?",
            "answer": "Publish = 1. The record now holds the triple the sentence named, so the lookup succeeds although no approval event occurred. Re-checking Approved(M_t) at the relabeling point, so that only an observed approval event can add an entry, closes it.",
            "provenance": "Constructed example: the approved triple and the attempted releases are the chapter's own release trace and its stale-approval and laundering exercises; the Q2-report case is defined for the reader.",
            "source_section": "Publish needs identity, version, recipient, and current approval",
            "source_anchor": "publish-needs-identity-version-recipient-and-current-approval",
            "controls": [
                {"key": "changed", "label": "Field changed in the proposal", "values": ["none", "document", "version", "recipient"],
                 "default": "version", "value_labels": ["Nothing changed", "Different document", "Newer version (5)", "Different recipient"]},
                {"key": "source", "label": "Where the approval came from", "values": ["event", "sentence", "laundered"], "default": "event",
                 "value_labels": ["An observed approval event", "A sentence in the source document",
                                  "A sentence relabeled trusted, admitted with no re-check"]},
            ],
            "function": "release_picture",
        },
        {
            "id": "C23-D04",
            "title": "Risk is the worst member; two scores are not one",
            "question": "If nine attacks are blocked and one is not, what single exposure number does a declared family report, and why must task completion and security violations be reported separately?",
            "equations": [EQ_RISK],
            "symbols": (
                "F is one declared, finite family of attacks under a fixed threat model. For an attack f in F, Pr[violation | f] "
                "is the chance that f produces an unauthorized effect against the stated enforcement. Risk(F) is the largest of those "
                "chances. The chances in the left figure are values defined for the reader, not measurements. The right figure replays the laboratory's fictitious traces: "
                "a task is completed when an authorized publish executes, a violation is a promoted instruction or an executed forbidden effect, and a request is blocked when "
                "the monitor denied it and it did not execute."
            ),
            "prediction": "Declare the retry path (0.45) while the confused-deputy chance is 0.1. Which attack sets Risk?",
            "prediction_options": ["Instruction injection (0.05)", "The retry path that skips the check (0.45)", "The confused-deputy delegation (0.10)"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Risk is the maximum, and 0.45 is larger than 0.05, 0.10 and 0.10. Set the family to four attacks and the confused-deputy chance to 0.1 to see it.",
                "incorrect": "Equation (23.4) takes the largest chance in the family, and the retry path at 0.45 exceeds 0.05, 0.10 and 0.10. Set the family to four attacks and the confused-deputy chance to 0.1 to see it.",
            },
            "explanation": (
                "Equation (23.4) takes a maximum over the family, so one dangerous member sets the value no matter how many "
                "safe ones surround it. An average would let the safe attacks hide the dangerous one. The value is also only about the "
                "attacks that were declared: a path that was never named is outside the guarantee. The right panel keeps two outcomes apart: a run can complete and still "
                "contain violations, and a secure refusal can finish nothing."
            ),
            "application": (
                "When reporting security, name the attack family first and report the worst member for each enforcement mechanism, then report utility and attack success as two numbers. "
                "Add any unmediated route you discover to the family instead of leaving it out of the number, and close the route: adding it to the family only measures it."
            ),
            "assumptions": (
                "A threat-model measure, not an empirical security rate and not a proof. It presumes complete mediation and a "
                "correctly specified predicate. The chances here are constructed; an attack outside the family, or a monitor with "
                "a specification gap, is not covered by the value. The traces are the laboratory's fictitious events; checking a trace does not enforce a real tool boundary."
            ),
            "misconception": {
                "title": "One score, completion or attack success, is enough",
                "text": ("The chapter says utility under attack and attack success must be reported separately: an agent that refuses everything can lower attack success while destroying utility, "
                         "and an agent that finishes the task while leaking data keeps utility while failing security."),
            },
            "scope_note": {
                "text": ("Risk of the declared family is bounded only over that family, under complete mediation, with the allowed and publish predicates correctly specified; "
                         "an unmediated tool call, a monitor gap, or an attack outside the family sits outside every guarantee."),
                "source_section": "What this does not settle",
            },
            "check": "A declared family has violation chances 0.20, 0.35, 0.05 and 0.35. What is Risk, and what is the mean? And in the changed trace, how many violations are there and why?",
            "answer": ("Risk = max(0.20, 0.35, 0.05, 0.35) = 0.35, set by the two members tied at 0.35. The mean = (0.20 + 0.35 + 0.05 + 0.35) / 4 = 0.2375, which is not the reported value. "
                       "In the changed trace violations = 1 promoted instruction + 1 forbidden publish executed = 2, even though the later authorized publish completes the task."),
            "provenance": "Constructed example: the three attack names are the chapter's declared family and the retry path is its unmediated-call example; every chance is defined for the reader. The three traces are the laboratory's default, changed and transfer cases, replayed with the laboratory's own monitor.",
            "source_section": "A security case needs a declared adversary",
            "source_anchor": "a-security-case-needs-a-declared-adversary",
            "controls": [
                {"key": "trace", "label": "Trace replayed on the right", "values": ["default", "changed", "transfer"], "default": "default",
                 "value_labels": ["Default: injection kept as data", "Changed: injection promoted and executed", "Transfer: stale review of A, current B"]},
                {"key": "family", "label": "Declared family", "values": ["three", "four"], "default": "three",
                 "value_labels": ["Three attacks", "Three plus the retry path (0.45)"]},
                {"key": "deputy", "label": "Chance for the confused-deputy attack", "values": [0.1, 0.6], "default": 0.6},
            ],
            "function": "risk_picture",
        },
    ],
}

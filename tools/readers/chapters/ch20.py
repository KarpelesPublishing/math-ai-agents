"""Chapter 20 reader: Messages, Beliefs, and Consensus.

Four demonstrations built on Equations (20.1) and (20.2) and the chapter's
last-message argument. Demonstrations 1 to 3 use one small model of a chain of
messages in which every message is sent only after the previous one arrives;
who knows what is computed by listing the runs and the runs each party cannot
tell apart. Demonstration 4 calls the laboratory's own bounded-message
computation (math_ai_agents.chapters.ch20.evaluate), so the reader, the
notebook and the chapter skill agree. Every number is a constructed teaching
value.
"""
import math

import numpy as np
from matplotlib.patches import FancyBboxPatch, Rectangle

from math_ai_agents.chapters.ch20 import evaluate
from readerkit import PALETTE, fmt, label_point, new_figure

EQ_MK = (r"\operatorname{MK}_{\mathcal P}^{n+1}(F) = \bigwedge_{i \in \mathcal P} \operatorname{Know}_i\!\left("
         r"\operatorname{MK}_{\mathcal P}^{n}(F)\right), \qquad \operatorname{MK}_{\mathcal P}^{1}(F) = "
         r"\bigwedge_{i \in \mathcal P} \operatorname{Know}_i(F).")
EQ_CK = (r"\operatorname{CK}_{\mathcal P}(F) \quad\Longleftrightarrow\quad \bigwedge_{n=1}^{\infty} "
         r"\operatorname{MK}_{\mathcal P}^{n}(F).")
EQ_KNOW = r"\operatorname{Know}_i(F)"

INK = PALETTE["ink"]
TEAL = PALETTE["teal"]
GOLD = PALETTE["gold"]
NAVY = PALETTE["navy"]
TERRA = PALETTE["terracotta"]
OLIVE = PALETTE["olive"]
GREY = PALETTE["grey"]
LIGHT = PALETTE["light"]


# The chain model shared by Demonstrations 1 to 3

class Chain:
    """Runs of a chain of at most N messages between A and B.

    Message j goes from A to B when j is odd and from B to A when j is even.
    Message 1 is always sent; message j is sent only after message j-1 was
    delivered. Run k is the run in which exactly messages 1..k are delivered
    (k = 0..N). A party's view is the set of messages it sent and received; two
    runs look the same to a party when its views match.
    """

    def __init__(self, planned):
        self.n = int(planned)
        self.runs = list(range(self.n + 1))
        self.classes = {"A": [], "B": []}
        self.class_of = {"A": {}, "B": {}}
        for party in ("A", "B"):
            seen = {}
            for k in self.runs:
                seen.setdefault(self.view(party, k), []).append(k)
            for members in seen.values():
                self.classes[party].append(members)
                for k in members:
                    self.class_of[party][k] = members

    def view(self, party, k):
        mine_odd = party == "A"
        sent = tuple(j for j in range(1, min(k + 1, self.n) + 1) if (j % 2 == 1) == mine_odd)
        got = tuple(j for j in range(1, k + 1) if (j % 2 == 1) != mine_odd)
        return sent, got

    def know(self, party, truth):
        """Truth vector of Know_party(statement), given the statement's truth vector over runs."""
        return [all(truth[w] for w in self.class_of[party][k]) for k in self.runs]

    def levels(self, fact, top):
        """[F, MK^1(F), ..., MK^top(F)] as truth vectors, by Equation (20.1)."""
        out = [list(fact)]
        for _ in range(top):
            a, b = self.know("A", out[-1]), self.know("B", out[-1])
            out.append([x and y for x, y in zip(a, b)])
        return out

    def reachable(self, start):
        """Runs linked to `start` by a chain of 'some party cannot tell these apart' steps."""
        seen, todo = {start}, [start]
        while todo:
            k = todo.pop()
            for party in ("A", "B"):
                for w in self.class_of[party][k]:
                    if w not in seen:
                        seen.add(w)
                        todo.append(w)
        return sorted(seen)


def first_message_delivered(chain):
    """F = 'message 1 was delivered'."""
    return [k >= 1 for k in chain.runs]


def draw_cell(ax, x, y, holds, yes="yes", no="no", width=0.84, height=0.7):
    """A solid teal cell with the word yes, or a hatched white cell with the word no."""
    rect = Rectangle((x - width / 2, y - height / 2), width, height,
                     facecolor=TEAL if holds else "white", edgecolor=TEAL if holds else GREY,
                     hatch=None if holds else "///", linewidth=1.2)
    ax.add_patch(rect)
    ax.text(x, y, yes if holds else no, ha="center", va="center", fontsize=11.5,
            color="white" if holds else INK, fontweight="bold" if holds else "normal",
            bbox=None if holds else {"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.95})


def actual_note(ax, x, y, text, hi):
    ha = "left" if x <= 0.5 else ("right" if x >= hi - 0.5 else "center")
    ax.text(x, y, text, ha=ha, va="center", fontsize=10.5, color=INK,
            bbox={"boxstyle": "round,pad=0.2", "fc": "white", "ec": "none", "alpha": 0.95})


def sender_of(j):
    return "A" if j % 2 == 1 else "B"


def trim(x):
    s = f"{x:.6f}".rstrip("0").rstrip(".")
    return s or "0"


# Demonstration 1: runs that look the same, and the mutual-knowledge ladder

def ladder_picture(delivered=2, planned=4):
    k, planned = int(delivered), int(planned)
    chain = Chain(planned)
    levels = chain.levels(first_message_delivered(chain), 5)
    # Level 0 stands for F itself. Highest level n >= 1 that holds, or 0 if none.
    highest = 0
    for n in range(1, 6):
        if levels[n][k]:
            highest = n
        else:
            break
    last_sender = sender_of(k)
    last_class = chain.class_of[last_sender][k]

    fig, (left, right) = new_figure(ncols=2, height=4.4)
    rows = {"A": 2.0, "B": 0.0}
    for party, y in rows.items():
        for members in chain.classes[party]:
            lo, hi = min(members), max(members)
            actual = k in members
            box = FancyBboxPatch((lo - 0.32, y - 0.27), hi - lo + 0.64, 0.54,
                                 boxstyle="round,pad=0,rounding_size=0.16",
                                 facecolor=("#d6e9ea" if party == "A" else "#f1e4cc"),
                                 edgecolor=INK if actual else GREY, linewidth=2.6 if actual else 1.2,
                                 hatch=None if party == "A" else "//")
            left.add_patch(box)
    left.axvline(k, color=GREY, linestyle="dashed", linewidth=1.2, zorder=0)
    left.plot(chain.runs, [1.0] * len(chain.runs), "o", color="white", markeredgecolor=INK, markersize=9, zorder=3)
    left.plot([k], [1.0], "*", color=INK, markersize=17, zorder=4)
    actual_note(left, k, 3.0, f"actual run: {k} delivered", planned)
    left.set_xlim(-0.6, planned + 0.6)
    left.set_ylim(-0.6, 3.35)
    left.set_xticks(chain.runs)
    left.set_yticks([0.0, 1.0, 2.0], ["B", "runs", "A"])
    left.set_xlabel("Run: how many messages were delivered")
    left.set_ylabel("Runs one party cannot tell apart")
    left.set_title("Runs inside one box look the same to that party", fontsize=11.5)
    left.grid(alpha=0)

    right.set_xlim(0.4, 5.6)
    right.set_ylim(-0.6, 2.6)
    for n in range(1, 6):
        draw_cell(right, n, 2.0, chain.know("A", levels[n - 1])[k])
        draw_cell(right, n, 1.0, chain.know("B", levels[n - 1])[k])
        draw_cell(right, n, 0.0, levels[n][k], yes="holds", no="fails")
    right.set_xticks(range(1, 6))
    right.set_yticks([0.0, 1.0, 2.0], ["level n", "B knows\nlevel n-1", "A knows\nlevel n-1"])
    right.set_xlabel("Level n of mutual knowledge of F (level 0 is F itself)")
    right.set_ylabel("Who knows the previous level")
    right.set_title("Level n holds only if both know level n-1", fontsize=11.5)
    right.grid(alpha=0)

    blocker = [p for p in ("A", "B") if not chain.know(p, levels[highest])[k]]
    blocker_text = " and ".join(blocker) if blocker else "nobody"
    know_a = chain.know("A", levels[0])[k]
    metrics = {
        "Messages delivered": f"{k} of {planned} planned",
        "B knows F (Know_B)": "yes" if chain.know("B", levels[0])[k] else "no",
        "A knows F (Know_A)": "yes" if know_a else "no",
        "Highest level that holds": str(highest) if highest else "none (A does not know F)",
        f"Level {highest + 1} is blocked by": blocker_text,
    }
    classes_text = f"runs {' and '.join(str(r) for r in last_class)}" if len(last_class) > 1 else f"run {k}"
    interpretation = (
        f"F is 'message 1 was delivered'. Highest level that holds = {k} - 1 = {k - 1}. "
        f"{'Level 1 needs A to know F, and A has no message back.' if highest == 0 else f'Level {highest} holds because both parties know level {highest - 1}.'} "
        f"Level {highest + 1} fails because {blocker_text} does not know level {highest}: {blocker_text} sent "
        f"the newest delivered message (number {k}) and cannot tell {classes_text} apart, and in the other run the level does not hold. "
        f"Each further delivered message moves the highest level up by exactly 1."
    )
    return fig, metrics, interpretation


# Demonstration 2: the three-message rule and the last message

ROUND_MESSAGES = 3


def rule_runs(a_needs, b_needs):
    """Decisions of the threshold rule in runs 0..3 (A receives even-numbered messages, B odd-numbered)."""
    out = []
    for k in range(ROUND_MESSAGES + 1):
        recv_a, recv_b = k // 2, (k + 1) // 2
        out.append({"run": k, "recv_a": recv_a, "recv_b": recv_b,
                    "a": recv_a >= a_needs, "b": recv_b >= b_needs})
    return out


def rule_picture(a_needs=1, b_needs=2):
    a_needs, b_needs = int(a_needs), int(b_needs)
    runs = rule_runs(a_needs, b_needs)
    unsafe = [r["run"] for r in runs if r["a"] != r["b"]]
    a_runs = [r["run"] for r in runs if r["a"]]
    b_runs = [r["run"] for r in runs if r["b"]]
    full_attack = runs[-1]["a"] and runs[-1]["b"]

    fig, ax = new_figure(height=4.2)
    ys = {"A": 2.0, "B": 1.0, "joint": 0.0}
    for r in runs:
        draw_cell(ax, r["run"], ys["A"], r["a"], yes="attacks", no="holds", width=0.88)
        draw_cell(ax, r["run"], ys["B"], r["b"], yes="attacks", no="holds", width=0.88)
        bad = r["a"] != r["b"]
        both = r["a"] and r["b"]
        ax.add_patch(Rectangle((r["run"] - 0.44, -0.35), 0.88, 0.7, facecolor="#f3d9d1" if bad else "white",
                               edgecolor=TERRA if bad else GREY, hatch="xx" if bad else None, linewidth=1.2))
        label = "UNSAFE" if bad else ("both" if both else "neither")
        ax.text(r["run"], 0.0, label, ha="center", va="center", fontsize=10.5, color=INK, fontweight="bold" if bad else "normal",
                bbox={"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.95} if bad else None)
    chain = Chain(ROUND_MESSAGES)
    for party, y in (("A", 2.0), ("B", 1.0)):
        for members in chain.classes[party]:
            if len(members) > 1:
                lo, hi = min(members), max(members)
                ax.add_patch(Rectangle((lo - 0.47, y - 0.47), 0.94 + (hi - lo), 0.94, fill=False, edgecolor=INK,
                                       linestyle="dashed", linewidth=1.6))
    ax.set_xlim(-0.6, 3.6)
    ax.set_ylim(-0.7, 2.75)
    ax.set_xticks(range(ROUND_MESSAGES + 1))
    ax.set_yticks([0.0, 1.0, 2.0], ["outcome", "B", "A"])
    ax.set_xlabel("Run: how many of the three messages were delivered")
    ax.set_ylabel("Decision at dawn")
    ax.set_title(f"A needs {a_needs} received, B needs {b_needs}\nDashed box: runs that division cannot tell apart", fontsize=11.0)
    ax.grid(alpha=0)

    metrics = {
        "A attacks in runs": ", ".join(map(str, a_runs)) if a_runs else "none",
        "B attacks in runs": ", ".join(map(str, b_runs)) if b_runs else "none",
        "Unsafe runs (exactly one attacks)": ", ".join(map(str, unsafe)) if unsafe else "none",
        "Safe in every run": "yes" if not unsafe else "no",
        "Both attack when all 3 arrive": "yes" if full_attack else "no",
    }
    if unsafe:
        u = runs[unsafe[0]]
        who = "A attacks and B holds" if u["a"] else "B attacks and A holds"
        calc = (f"Run {u['run']}: A has received {u['run']} / 2 = {u['run'] / 2:.1f}, rounded down to {u['recv_a']} message(s), needs {a_needs}. "
                f"B has received ({u['run']} + 1) / 2 = {(u['run'] + 1) / 2:.1f}, rounded down to {u['recv_b']}, needs {b_needs}. "
                f"So {who}: the rule is unsafe.")
        if full_attack:
            tail = " The rule does make both attack when all three arrive, but the unsafe run shows a lost message breaks it."
            if (a_needs, b_needs) == (1, 2):
                tail += " This is the chapter's three-message table."
        else:
            tail = " The theorem says some run must go wrong for any rule that ever attacks."
    else:
        calc = (f"A needs {a_needs}, but at most 3 / 2 = 1.5, so 1 whole message, can reach A. "
                f"B needs {b_needs}, but at most (3 + 1) / 2 = 2 can reach B. Nobody attacks in any run.")
        tail = (" This rule is safe only because it never attacks, which is the chapter's corollary: the safe protocol is inaction.")
    interpretation = (calc + tail + " A's decision is the same in runs that look the same to A, and B's likewise, "
                      "so a rule cannot make the last message decisive without making one lost message harmful.")
    return fig, metrics, interpretation


# Demonstration 3: common knowledge, messages against a public clock

FACTS = {
    "message": "message 1 was delivered",
    "clock": "dawn is the attack time on a public clock",
}
CK_LEVELS = 6


def common_knowledge_picture(planned=3, fact="message"):
    planned = int(planned)
    chain = Chain(planned)
    k = planned
    truth = first_message_delivered(chain) if fact == "message" else [True] * len(chain.runs)
    levels = chain.levels(truth, CK_LEVELS)
    holds = [levels[n][k] for n in range(1, CK_LEVELS + 1)]
    reach = chain.reachable(k)
    ck = all(truth[w] for w in reach)
    # In a model with W runs, level W already equals common knowledge (the reachable set is within W - 1 steps).
    deep = chain.levels(truth, len(chain.runs))[len(chain.runs)][k]
    if deep != ck:
        raise AssertionError("reachability and deep mutual knowledge disagree")
    highest = 0
    for n in range(1, CK_LEVELS + 1):
        if holds[n - 1]:
            highest = n
        else:
            break

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    for j in chain.runs:
        draw_cell(left, j, 1.0, truth[j], yes="F", no="not F", width=0.7, height=0.62)
    for party, style in (("A", "solid"), ("B", "dashed")):
        for members in chain.classes[party]:
            for lo, hi in zip(members, members[1:]):
                left.plot([lo + 0.12, lo + 0.12, hi - 0.12, hi - 0.12], [0.69, 0.4, 0.4, 0.69], color=INK, linestyle=style, linewidth=2.2)
                left.text((lo + hi) / 2, 0.16, party, ha="center", va="center", fontsize=11.0, color=INK, fontweight="bold")
    left.plot([k], [1.62], "*", color=INK, markersize=16)
    actual_note(left, k, 1.95, f"actual run: all {planned} delivered", planned + 0.0)
    left.set_xlim(-0.6, planned + 0.6)
    left.set_ylim(-0.1, 2.25)
    left.set_xticks(chain.runs)
    left.set_yticks([])
    left.set_xlabel("Run: how many messages were delivered")
    left.set_ylabel("Fact F, and links between runs")
    left.set_title(f"F: {FACTS[fact]}\nLink letter: the division that cannot tell the two runs apart", fontsize=10.5)
    left.grid(alpha=0)

    right.set_xlim(0.4, CK_LEVELS + 2.0)
    right.set_ylim(-0.1, 1.3)
    for n in range(1, CK_LEVELS + 1):
        draw_cell(right, n, 0.6, holds[n - 1], yes="yes", no="no", width=0.78, height=0.9)
    draw_cell(right, CK_LEVELS + 1.5, 0.6, ck, yes="yes", no="no", width=0.9, height=0.9)
    right.set_xticks(list(range(1, CK_LEVELS + 1)) + [CK_LEVELS + 1.5], [str(n) for n in range(1, CK_LEVELS + 1)] + ["CK"])
    right.set_yticks([])
    right.set_xlabel("Level n of mutual knowledge, then common knowledge (CK)")
    right.set_ylabel("Holds in the actual run?")
    right.set_title("Common knowledge needs every level", fontsize=11.5)
    right.grid(alpha=0)

    if fact == "message":
        highest_text = f"{highest} (level {highest + 1} fails)"
        calc = (f"Highest level that holds = {planned} - 1 = {planned - 1}. From run {planned} the links lead through "
                f"{planned} - 0 = {planned} steps down to run 0, where message 1 was not delivered, so F is false in a run "
                f"reachable from the actual one.")
        tail = (" Equation (20.2) needs F at every level, so common knowledge fails. A longer chain only pushes the highest level up, "
                "and the same walk back to run 0 is always there. Messages added no common knowledge that run 0 did not already have.")
    else:
        highest_text = f"all {CK_LEVELS} checked hold"
        calc = (f"Runs reachable from run {planned}: {planned} + 1 = {planned + 1} (every run), and F is true in all {planned + 1}. "
                f"So levels 1 to {CK_LEVELS} hold and so does every higher level.")
        tail = (" Equation (20.2) is satisfied from the start. The clock is public, so no message was needed and no lost message can "
                "remove it. The delivery chain is just as blind as before, but F does not depend on it.")
    metrics = {
        "Highest level that holds": highest_text,
        "Runs reachable from the actual run": f"{len(reach)} of {len(chain.runs)}",
        "Common knowledge of F (Equation 20.2)": "holds" if ck else "fails",
        "F true in every reachable run": "yes" if ck else "no",
    }
    return fig, metrics, calc + tail


# Demonstration 4: probability of agreement against knowledge of agreement

def lab_numbers(rounds, drop):
    out = evaluate({"rounds": int(rounds), "drop_probability": float(drop)})
    return out["metrics"]


def agreement_picture(rounds=2, drop=0.3):
    rounds, drop = int(rounds), float(drop)
    m = lab_numbers(rounds, drop)
    by_round = [lab_numbers(r, drop) for r in range(1, rounds + 1)]
    agree = [row["agreement_probability"] for row in by_round]
    bob_knows = [row["bob_knows_ack_receipt_probability"] for row in by_round]
    alone = m["bob_commits_without_alice_probability"]

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    items = [
        ("Both commit or\nneither does", m["agreement_probability"], TEAL, None),
        ("Alice knows the\nrequest arrived", m["alice_knows_delivery_probability"], NAVY, ".."),
        ("Bob knows his reply\narrived", m["bob_knows_ack_receipt_probability"], OLIVE, "\\\\"),
        ("Bob commits,\nAlice does not", alone, TERRA, "xx"),
    ]
    ypos = np.arange(len(items))[::-1]
    for y, (name, value, color, hatch) in zip(ypos, items):
        left.barh(y, value, height=0.58, color=color if hatch is None else "white", edgecolor=color, hatch=hatch, linewidth=1.4)
        left.text(value + 0.02, y, fmt(value, 3), va="center", ha="left", fontsize=11, color=INK)
    left.set_yticks(ypos, [i[0] for i in items])
    left.set_xlim(0, 1.2)
    left.set_xticks([0, 0.25, 0.5, 0.75, 1.0])
    left.set_xlabel("Probability")
    left.set_ylabel("Event")
    left.set_title(f"{rounds} rounds, each message dropped with probability {fmt(drop, 1)}", fontsize=11.0)
    left.grid(axis="y", alpha=0)

    xs = list(range(1, rounds + 1))
    right.plot(xs, agree, "-o", color=TEAL, markersize=8)
    right.plot(xs, bob_knows, "--s", color=OLIVE, markersize=8, markerfacecolor="white", markeredgewidth=2)
    right.set_xlim(0.5, rounds + 0.5)
    right.set_ylim(-0.1, 1.15)
    right.set_xticks(xs)
    right.set_xlabel("Rounds of request and reply allowed")
    right.set_ylabel("Probability")
    right.set_title("Agreement and Bob's knowledge by number of rounds", fontsize=11.0)
    if drop == 0:
        label_point(right, 1, 1.0, "agreement: 1.000 in every round", color=TEAL, dx=0, dy=10, ha="left", va="bottom")
        label_point(right, rounds, 1.0, "Bob knows his reply arrived: 1.000", color=OLIVE, dx=0, dy=-12, ha="right", va="top")
    else:
        for x, y in zip(xs, agree):
            label_point(right, x, y, fmt(y, 3), color=TEAL, dx=0, dy=9, ha="center", va="bottom")
        label_point(right, 1, agree[0], "agreement", color=TEAL, dx=0, dy=22, ha="left", va="bottom")
        label_point(right, rounds, bob_knows[-1], "Bob knows his reply arrived", color=OLIVE, dx=0, dy=8, ha="right", va="bottom")

    miss = 1 - (1 - drop) ** 2
    possible = f"{m['possible_worlds']} of {m['enumerated_worlds']}"
    metrics = {
        "Agreement probability": fmt(m["agreement_probability"], 4),
        "Alice knows the request arrived": fmt(m["alice_knows_delivery_probability"], 4),
        "Bob knows his reply arrived": fmt(m["bob_knows_ack_receipt_probability"], 4),
        "Bob commits without Alice": fmt(alone, 4),
        "Delivery bit patterns allowed": possible,
    }
    calc = (f"A round in which the reply does not get back to Alice = 1 - (1 - {trim(drop)}) x (1 - {trim(drop)}) = {trim(miss)}. "
            f"Bob commits alone = {trim(miss)}^{rounds} - {trim(drop)}^{rounds} = {trim(miss ** rounds)} - {trim(drop ** rounds)} = {trim(alone)}, "
            f"so agreement = 1 - {trim(alone)} = {trim(m['agreement_probability'])}.")
    if drop == 0:
        tail = (" With a drop probability of 0 the model allows only one delivery pattern, so Bob 'knows' his reply arrived "
                "because losing it was ruled out by assumption, not because he received anything.")
    else:
        tail = (" Bob's chance of knowing his reply arrived stays 0: a lost reply looks the same to him as a delivered one. "
                "An agreement probability, high or not, is a statement about outcomes, not about what each party knows at every level, so it is not common knowledge in the sense of Equation (20.2).")
    return fig, metrics, calc + tail


CHAPTER = {
    "number": 20,
    "title": "Messages, Beliefs, and Consensus",
    "subtitle": "Sending, receiving, acknowledging and committing are different events, and an unreliable final message cannot make them one.",
    "summary": (
        "These four demonstrations follow the chapter's two divisions that can win only by attacking together and can talk only by a "
        "messenger who may be lost. They show who knows what after each message, why a rule built on the last message fails, why no "
        "number of messages gives common knowledge, and why a high chance of agreement is not knowledge of agreement."
    ),
    "demos": [
        {
            "id": "C20-D01",
            "title": "One more message, one more level",
            "question": "After a few messages have been delivered, how many levels of mutual knowledge exist, and who blocks the next one?",
            "equations": [EQ_MK],
            "symbols": (
                "P = {A, B} is the set of the two parties. F is the fact 'message 1, from A to B, was delivered'. Know_i(F) means party i knows F. MK^1(F) means both A and B know F; "
                "MK^(n+1)(F) means each party knows MK^n(F). A run is labelled by k, the number of messages delivered in order: A sends the "
                "odd-numbered messages, B the even-numbered ones, and each is sent only after the one before it arrived. A party's view is the "
                "messages it sent and received. A party knows a fact only if the fact is true in every run that looks the same to it."
            ),
            "prediction": "Set 3 messages delivered out of 4 planned. Which is the highest level of mutual knowledge of F, and who cannot reach the next one?",
            "explanation": (
                "The last sender of a delivered message cannot see that it arrived, so its view is the same in the run where it arrived and the one "
                "where it was lost. Equation (20.1) needs both parties to know the previous level, so the newest message's sender is always the one "
                "who fails. Each further delivered message passes the block to the other party and raises the highest level by exactly one."
            ),
            "application": (
                "When a log shows request, reply and confirmation, write down who saw each message. The deepest level of mutual knowledge the "
                "exchange supports is one less than the number of messages delivered, and the next level depends on a message nobody can confirm."
            ),
            "assumptions": (
                "One chain of messages in which each is sent only after the previous one arrived, and a message lost is not signalled to its sender. "
                "Other message patterns, a shared clock or a signal on loss would change which runs look the same. The level count depends on the "
                "choice of F; a fact both parties already knew would start higher."
            ),
            "check": "If 4 messages are delivered out of 5 planned, what is the highest level of mutual knowledge of F?",
            "answer": "Highest level = 4 - 1 = 3. Level 4 fails because B sent message 4 and cannot tell run 3 from run 4, so B does not know level 3 (level 3 holds in runs 4 and 5 but not in run 3). A does know level 3, because level 3 holds in both runs 4 and 5, the two runs A cannot separate.",
            "provenance": "Constructed example: a chain of messages defined for this reader to follow the chapter's two-division story, with who-knows-what computed from the runs.",
            "source_section": "Stage three: finite depth has a boundary",
            "source_anchor": "stage-three-finite-depth-has-a-boundary",
            "controls": [
                {"key": "delivered", "label": "Messages delivered", "values": [1, 2, 3, 4], "default": 2},
                {"key": "planned", "label": "Messages the protocol plans to send", "values": [4, 5], "default": 4},
            ],
            "function": "ladder_picture",
        },
        {
            "id": "C20-D02",
            "title": "A rule that trusts the last message",
            "question": "Can a rule that tells each division to attack after receiving enough messages be safe and ever attack?",
            "equations": [EQ_KNOW],
            "symbols": (
                "Know_i(F) means division i knows F, where F is any statement about which messages arrived; i knows F when F is true in every run that "
                "looks the same to i, so a decision rule for i can use only i's own sent and received messages. Three messages are "
                "sent in order: a proposal from A, an acknowledgement from B, a confirmation from A. A receives only the even-numbered message "
                "(the acknowledgement) and B the odd-numbered ones (the proposal and the confirmation), so after k messages have been delivered A has "
                "received k / 2 and B has received (k + 1) / 2, each rounded down to a whole message. A attacks once it has received at least its "
                "needed number of messages, B likewise. Safety means that in every run either both attack or neither does."
            ),
            "prediction": "Keep A needing 1 and B needing 2 (the chapter's rule). Which single run makes exactly one division attack?",
            "explanation": (
                "A rule can be written as a pair of thresholds on received messages. For every pair that ever makes a division attack, some run has "
                "one attacking and one holding, because the party that sent the final message cannot tell the last run from the one before it. "
                "With each division needing at least one received message (the chapter's no-message nonattack base), the only pair that is safe is the one that never attacks."
            ),
            "application": (
                "Test a handoff specification by asking what happens if the last message is lost. If the outcome changes for one party only, "
                "the specification has hidden a final delivery that nobody can observe."
            ),
            "assumptions": (
                "A threshold rule over three messages that are sent in sequence and can each be lost. A rule that uses a public clock or a shared "
                "record is outside this model. A rule that accepts some chance of mismatch makes a different promise from the one tested here."
            ),
            "check": "If A needed 1 and B needed 1, in which run does only B attack?",
            "answer": "In run 1 only the proposal arrived: B has received (1 + 1) / 2 = 1, enough, and A has received 1 / 2 = 0.5, rounded down to 0. So B attacks alone.",
            "provenance": "Constructed example: the chapter's three-message table (acknowledgement then confirmation), with the needed numbers of received messages varied.",
            "source_section": "Stage four: why last message cannot save attack",
            "source_anchor": "stage-four-why-last-message-cannot-save-attack",
            "controls": [
                {"key": "a_needs", "label": "Messages A needs to have received", "values": [1, 2], "default": 1},
                {"key": "b_needs", "label": "Messages B needs to have received", "values": [1, 2, 3], "default": 2},
            ],
            "function": "rule_picture",
        },
        {
            "id": "C20-D03",
            "title": "Messages against a public clock",
            "question": "Does any number of delivered messages make a fact common knowledge, and what does a public clock do differently?",
            "equations": [EQ_CK],
            "symbols": (
                "P = {A, B} is the set of the two parties. CK(F) is common knowledge of F: every level MK^n(F) holds, for n = 1, 2, 3 and so on without end. A run is the number of messages "
                "delivered. Two runs are linked when one division cannot tell them apart; a solid link is a link for A, a dashed link one for B. "
                "A fact is common knowledge in the actual run exactly when it is true in every run reachable by links."
            ),
            "prediction": "With 4 messages planned and every one delivered, is message 1 common knowledge? Then switch the fact to the public clock.",
            "explanation": (
                "From the run where everything arrived, follow links: each one steps back by a single message, and the chain ends at the run with "
                "no message delivered, where message 1 was not. So the fact fails at some level however many messages are planned. A fact that is true in "
                "every run, like a public clock both can read, holds at every level with no message at all."
            ),
            "application": (
                "Before counting acknowledgements, list the facts every participant can observe and knows the others observe: a deadline on a "
                "shared clock, a record all can read. Those can anchor a joint action; a private reply chain cannot."
            ),
            "assumptions": (
                "The same message chain as Demonstration 1, with loss that the sender cannot observe. If a loss produced a signal visible to both "
                "parties, the links would break and the conclusion would not hold. A public clock still needs a shared reading of time and a "
                "rule tying time to action."
            ),
            "check": "With 5 messages planned and all delivered, which is the highest level of mutual knowledge of message 1, and how many link steps lead back to the silent run?",
            "answer": "Highest level = 5 - 1 = 4. The walk back crosses 5 - 0 = 5 links to run 0, where message 1 was not delivered, so common knowledge fails.",
            "provenance": "Constructed example: the Demonstration 1 chain of messages, with a second fact (a public clock) defined for this reader to contrast with it.",
            "source_section": "Stage five: common knowledge is not a long finite list",
            "source_anchor": "stage-five-common-knowledge-is-not-a-long-finite-list",
            "controls": [
                {"key": "planned", "label": "Messages planned, all delivered", "values": [2, 3, 4, 5], "default": 3},
                {"key": "fact", "label": "Fact being tested", "values": ["message", "clock"], "default": "message",
                 "value_labels": ["Message 1 was delivered", "Dawn on a public clock"]},
            ],
            "function": "common_knowledge_picture",
        },
        {
            "id": "C20-D04",
            "title": "High chance of agreement, no knowledge of it",
            "question": "If parties usually end up committing together, do they know that they will?",
            "equations": [EQ_CK],
            "symbols": (
                "P = {Alice, Bob} is the set of the two parties. Each round, Alice sends a request and Bob, if it arrives, sends a reply; each message is dropped independently with probability d. "
                "Alice commits if she sees a reply; Bob commits if he sees a request. Agreement means both or neither commit. 'Alice knows' means "
                "that in every possible message pattern that looks the same to her, the request arrived. The same test is used for Bob and his reply. "
                "R is the number of rounds."
            ),
            "prediction": "At a drop probability of 0.5, does a second round raise agreement above the one-round value of 0.75? And does Bob's chance of knowing his reply arrived change with the number of rounds?",
            "explanation": (
                "Bob commits alone when some request arrives but no reply gets back: probability [1 - (1 - d)^2]^R - d^R. For a small drop "
                "probability more rounds shrink it. For a large one the first term decays slowly and agreement can dip before it recovers (at d = 0.5 "
                "it goes 0.75, 0.6875, 0.703). Bob's view never shows whether his reply arrived, so the worlds he cannot tell apart always include "
                "a lost reply, and his knowledge stays at 0 unless losses are declared impossible."
            ),
            "application": (
                "A report that two components usually agree is not a guarantee that either can act on the agreement. Ask what each party can "
                "observe, and whether the gap between agreeing and knowing it matters for the action."
            ),
            "assumptions": (
                "A fixed number of rounds with synchronized ticks, independent drops, and Alice and Bob each acting on one local trigger. Real "
                "systems can crash or reorder messages. At drop probability 0 the model rules out loss by assumption; that is a statement about the "
                "model, not evidence that a channel cannot fail. This does not prove the theorem; it shows the two quantities differ."
            ),
            "check": "With a drop probability of 0.2 and 2 rounds, what is the chance that Bob commits and Alice does not?",
            "answer": "A round in which the reply does not get back to Alice has probability 1 - 0.8 x 0.8 = 0.36. So Bob commits alone with probability 0.36^2 - 0.2^2 = 0.1296 - 0.04 = 0.0896, and agreement is 0.9104.",
            "provenance": "Constructed example: the laboratory's bounded request-and-reply model with the notebook's default (2 rounds, 0.3) and transfer (3 rounds, 0.5) cases, computed with the laboratory's own function.",
            "source_section": "Stage eight: consensus begins with a shared event model",
            "source_anchor": "stage-eight-consensus-begins-with-a-shared-event-model",
            "controls": [
                {"key": "rounds", "label": "Rounds of request and reply", "values": [2, 3], "default": 2},
                {"key": "drop", "label": "Probability that a message is dropped", "values": [0, 0.3, 0.5], "default": 0.3},
            ],
            "function": "agreement_picture",
        },
    ],
}

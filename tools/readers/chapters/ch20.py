"""Chapter 20 reader: Messages, Beliefs, and Consensus.

Four demonstrations built on Equations (20.1) and (20.2) and the chapter's
last-message argument. Demonstrations 1 to 3 use one small model of a chain of
messages in which every message is sent only after the previous one arrives;
who knows what is computed by listing the runs and the runs each party cannot
tell apart. Demonstration 1 climbs the mutual-knowledge ladder and ends at
common knowledge (message against public clock), Demonstration 2 removes the
last delivered message one run at a time, Demonstration 3 compares two private
decisions with an escrow state that has a deadline (Figure 20.4), and
Demonstration 4 calls the laboratory's own bounded-message computation
(math_ai_agents.chapters.ch20.evaluate), so the reader, the notebook and the
chapter skill agree. Every number is a constructed teaching value.
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


# Demonstration 1: runs that look the same, the mutual-knowledge ladder, and common knowledge

PLANNED = 4
FACTS = {
    "message": "message 1 was delivered",
    "clock": "dawn is the attack time on a public clock",
}
LEVELS = 5
WHITE_BOX = {"boxstyle": "round,pad=0.15", "fc": "white", "ec": "none", "alpha": 0.95}


def fact_truth(chain, fact):
    return first_message_delivered(chain) if fact == "message" else [True] * len(chain.runs)


def ladder_picture(delivered=2, fact="message"):
    k = int(delivered)
    chain = Chain(PLANNED)
    truth = fact_truth(chain, fact)
    levels = chain.levels(truth, LEVELS)
    highest = 0
    for n in range(1, LEVELS + 1):
        if levels[n][k]:
            highest = n
        else:
            break
    all_hold = highest == LEVELS
    reach = chain.reachable(k)
    ck = all(truth[w] for w in reach)
    deep = chain.levels(truth, len(chain.runs))[len(chain.runs)][k]
    if deep != ck:
        raise AssertionError("reachability and deep mutual knowledge disagree")
    if fact == "message" and highest != k - 1:
        raise AssertionError("highest level is not delivered minus one")
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
    for j in chain.runs:
        draw_cell(left, j, 1.0, truth[j], yes="F", no="not F", width=0.62, height=0.44)
    actual_note(left, k, 3.0, f"actual run: {k} delivered", PLANNED)
    left.set_xlim(-0.6, PLANNED + 0.6)
    left.set_ylim(-0.6, 3.35)
    left.set_xticks(chain.runs)
    left.set_yticks([0.0, 1.0, 2.0], ["B", "F in run", "A"])
    left.set_xlabel("Run: how many messages were delivered")
    left.set_ylabel("Runs one party cannot tell apart")
    left.set_title("Runs inside one box look the same to that party", fontsize=11.0)
    left.grid(alpha=0)
    left.axvline(k, color=GREY, linestyle="dashed", linewidth=1.2, zorder=0)

    right.set_xlim(0.4, LEVELS + 2.3)
    right.set_ylim(-0.6, 2.6)
    for n in range(1, LEVELS + 1):
        draw_cell(right, n, 2.0, chain.know("A", levels[n - 1])[k])
        draw_cell(right, n, 1.0, chain.know("B", levels[n - 1])[k])
        draw_cell(right, n, 0.0, levels[n][k], yes="holds", no="fails")
    right.axvline(LEVELS + 0.75, color=GREY, linestyle=":", linewidth=1.4)
    draw_cell(right, LEVELS + 1.6, 0.0, ck, yes="holds", no="fails", width=0.96)
    right.text(LEVELS + 1.6, 1.5, "all levels\ntogether", ha="center", va="center", fontsize=10.5, color=INK)
    right.set_xticks(list(range(1, LEVELS + 1)) + [LEVELS + 1.6], [str(n) for n in range(1, LEVELS + 1)] + ["CK"])
    right.set_yticks([0.0, 1.0, 2.0], ["level n", "B knows\nlevel n-1", "A knows\nlevel n-1"])
    right.set_xlabel("Level n of mutual knowledge of F, then common knowledge (CK)")
    right.set_ylabel("Who knows the previous level")
    right.set_title("Level n holds only if both know level n-1", fontsize=11.0)
    right.grid(alpha=0)

    know_a = chain.know("A", levels[0])[k]
    know_b = chain.know("B", levels[0])[k]
    if fact == "message":
        blocker = [p for p in ("A", "B") if not chain.know(p, levels[highest])[k]]
        blocker_text = " and ".join(blocker) if blocker else "nobody"
        highest_text = str(highest) if highest else "none (A does not know F)"
        classes_text = f"runs {' and '.join(str(r) for r in last_class)}" if len(last_class) > 1 else f"run {k}"
        calc = (f"F is 'message 1 was delivered'. Highest level that holds = {k} - 1 = {k - 1}. "
                f"{'Level 1 needs A to know F, and A has no message back.' if highest == 0 else f'Level {highest} holds because both parties know level {highest - 1}.'} "
                f"Level {highest + 1} fails because {blocker_text} does not know level {highest}: {blocker_text} sent "
                f"the newest delivered message (number {k}) and cannot tell {classes_text} apart, and in the other run the level does not hold. "
                f"The links between runs lead from run {k} down to run 0 in {k} - 0 = {k} steps, and F is false in run 0, "
                "so Equation (20.2) fails: every delivered message pushes the highest level up by one and the walk back to run 0 is always there.")
        steps = [
            f"Run {k}: {k} of {PLANNED} messages delivered; A sends the odd-numbered messages, B the even-numbered ones.",
            f"The newest delivered message is number {k}, sent by {last_sender}, who cannot tell {classes_text} apart.",
            f"Highest level of mutual knowledge of F that holds = {k} - 1 = {k - 1}.",
            f"Level {highest + 1} fails because {blocker_text} does not know level {highest}.",
            f"Walking back through runs a party cannot tell apart takes {k} - 0 = {k} steps and ends in run 0, where F is false.",
            "So F is not common knowledge (Equation 20.2) however many messages arrive.",
        ]
        metrics = {
            "Messages delivered": f"{k} of {PLANNED} planned",
            "B knows F (Know_B)": "yes" if know_b else "no",
            "A knows F (Know_A)": "yes" if know_a else "no",
            "Highest level that holds": highest_text,
            "Next level blocked by": blocker_text,
            "Runs reachable from the actual run": f"{len(reach)} of {len(chain.runs)}",
            "Common knowledge of F (Equation 20.2)": "holds" if ck else "fails",
        }
        alt = (f"Left, runs 0 to {PLANNED} with F true from run 1; boxes show the runs each party cannot tell apart, with run {k} marked. "
               f"Right, levels 1 to {LEVELS}: levels up to {highest} hold and the next fails, and common knowledge fails.")
    else:
        calc = (f"F is 'dawn is the attack time on a public clock', true in every run. Runs reachable from run {k}: {PLANNED} + 1 = {PLANNED + 1} (every run), "
                f"and F is true in all {PLANNED + 1}. So levels 1 to {LEVELS} hold and so does every higher level. "
                "Equation (20.2) is satisfied from the start: the clock is public, so no message was needed and no lost message can remove it. "
                f"The {k} delivered messages change which runs look alike, not whether F holds.")
        steps = [
            f"Run {k}: {k} of {PLANNED} messages delivered, as before.",
            "F is true in every run, because the clock is visible to both divisions whatever the messages do.",
            f"So every party knows F, and knows level 1, and so on: levels 1 to {LEVELS} all hold.",
            f"Runs reachable by links from run {k}: {PLANNED} + 1 = {PLANNED + 1}, and F is true in all of them.",
            "So F is common knowledge (Equation 20.2) before any message is needed.",
        ]
        metrics = {
            "Messages delivered": f"{k} of {PLANNED} planned",
            "B knows F (Know_B)": "yes" if know_b else "no",
            "A knows F (Know_A)": "yes" if know_a else "no",
            "Highest level that holds": f"all {LEVELS} checked hold",
            "Next level blocked by": "nobody (no level fails)",
            "Runs reachable from the actual run": f"{len(reach)} of {len(chain.runs)}",
            "Common knowledge of F (Equation 20.2)": "holds" if ck else "fails",
        }
        alt = (f"Left, runs 0 to {PLANNED} with F true in every run; boxes show the runs each party cannot tell apart, with run {k} marked. "
               f"Right, levels 1 to {LEVELS} all hold and common knowledge holds.")
    return fig, metrics, calc, {"alt": alt, "steps": steps}


# Demonstration 2: the three-message rule and the last-message reduction

ROUND_MESSAGES = 3


def rule_runs(a_needs, b_needs):
    """Decisions of the threshold rule in runs 0..3 (A receives even-numbered messages, B odd-numbered)."""
    out = []
    for k in range(ROUND_MESSAGES + 1):
        recv_a, recv_b = k // 2, (k + 1) // 2
        out.append({"run": k, "recv_a": recv_a, "recv_b": recv_b,
                    "a": recv_a >= a_needs, "b": recv_b >= b_needs})
    return out


def outcome_word(r):
    if r["a"] and r["b"]:
        return "both attack"
    if not r["a"] and not r["b"]:
        return "neither"
    return "A only" if r["a"] else "B only"


def rule_picture(a_needs=1, b_needs=2):
    a_needs, b_needs = int(a_needs), int(b_needs)
    runs = rule_runs(a_needs, b_needs)
    unsafe = [r["run"] for r in runs if r["a"] != r["b"]]
    a_runs = [r["run"] for r in runs if r["a"]]
    b_runs = [r["run"] for r in runs if r["b"]]
    full_attack = runs[-1]["a"] and runs[-1]["b"]

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    ys = {"A": 2.0, "B": 1.0, "joint": 0.0}
    for r in runs:
        draw_cell(left, r["run"], ys["A"], r["a"], yes="attacks", no="holds", width=0.88)
        draw_cell(left, r["run"], ys["B"], r["b"], yes="attacks", no="holds", width=0.88)
        bad = r["a"] != r["b"]
        left.add_patch(Rectangle((r["run"] - 0.44, -0.35), 0.88, 0.7, facecolor="#f3d9d1" if bad else "white",
                                 edgecolor=TERRA if bad else GREY, hatch="xx" if bad else None, linewidth=1.2))
        label = "UNSAFE" if bad else ("both" if r["a"] and r["b"] else "neither")
        left.text(r["run"], 0.0, label, ha="center", va="center", fontsize=10.5, color=INK, fontweight="bold" if bad else "normal",
                  bbox=WHITE_BOX if bad else None)
    chain = Chain(ROUND_MESSAGES)
    for party, y in (("A", 2.0), ("B", 1.0)):
        for members in chain.classes[party]:
            if len(members) > 1:
                lo, hi = min(members), max(members)
                left.add_patch(Rectangle((lo - 0.47, y - 0.47), 0.94 + (hi - lo), 0.94, fill=False, edgecolor=INK,
                                         linestyle="dashed", linewidth=1.6))
    left.set_xlim(-0.6, 3.6)
    left.set_ylim(-0.7, 2.75)
    left.set_xticks(range(ROUND_MESSAGES + 1))
    left.set_yticks([0.0, 1.0, 2.0], ["outcome", "B", "A"])
    left.set_xlabel("Run: how many of the three messages were delivered")
    left.set_ylabel("Decision at dawn")
    left.set_title(f"A needs {a_needs} received, B needs {b_needs}\nDashed box: runs that division cannot tell apart", fontsize=10.5)
    left.grid(alpha=0)

    # right panel: remove the last delivered message, one run at a time (run 3, 2, 1, 0)
    blind = {3: "A", 2: "B", 1: "A"}  # the sender of message j cannot tell run j from run j - 1
    order = [3, 2, 1, 0]
    for pos, run in enumerate(order):
        r = runs[run]
        word = outcome_word(r)
        bad = r["a"] != r["b"]
        both = r["a"] and r["b"]
        face = TEAL if both else ("#f3d9d1" if bad else "white")
        edge = TEAL if both else (TERRA if bad else GREY)
        right.add_patch(Rectangle((pos - 0.41, 0.45), 0.82, 1.1, facecolor=face, edgecolor=edge, linewidth=1.4,
                                  hatch="xx" if bad else (None if both else "///")))
        right.text(pos, 1.25, f"run {run}", ha="center", va="center", fontsize=10.5, color="white" if both else INK, fontweight="bold",
                   bbox=None if both else WHITE_BOX)
        right.text(pos, 0.78, word, ha="center", va="center", fontsize=10.0, color="white" if both else INK,
                   bbox=None if both else WHITE_BOX)
    for pos, run in enumerate(order[:-1]):
        right.annotate("", xy=(pos + 0.57, 1.0), xytext=(pos + 0.43, 1.0), arrowprops={"arrowstyle": "->", "color": INK, "linewidth": 1.4})
        right.text(pos + 0.5, 1.82, f"{blind[run]} cannot\ntell", ha="center", va="center", fontsize=10.0, color=INK)
    right.text(3.0, 0.1, "no-message base:\nnobody attacks", ha="center", va="center", fontsize=10.0, color=INK)
    right.set_xlim(-0.6, 3.6)
    right.set_ylim(-0.2, 2.25)
    right.set_xticks([])
    right.set_yticks([])
    right.set_xlabel("Remove the last delivered message, one run at a time")
    right.set_ylabel("Same view, same decision")
    right.set_title("The reduction from run 3 down to run 0", fontsize=11.0)
    right.grid(alpha=0)

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
        tail = " This rule is safe only because it never attacks, which is the chapter's corollary: the safe protocol is inaction."
    interpretation = (calc + tail + " A's decision is the same in runs that look the same to A, and B's likewise, "
                      "so a rule cannot make the last message decisive without making one lost message harmful.")
    r3 = runs[3]
    steps = [
        f"Rule: A attacks after receiving at least {a_needs} message(s), B after at least {b_needs}.",
        f"Run 3 (all delivered): A has received 3 / 2 = 1.5, rounded down to {r3['recv_a']}; B has received (3 + 1) / 2 = 2.",
        f"Run 3 outcome: {outcome_word(r3)}.",
        f"Remove message 3 (sent by A): A's view is unchanged, so A decides the same in run 2 ({'attacks' if runs[2]['a'] else 'holds'}).",
        f"Remove message 2 (sent by B): B's view is unchanged, so B decides the same in run 1 ({'attacks' if runs[1]['b'] else 'holds'}).",
        f"Remove message 1 (sent by A): A's view is unchanged, so A decides the same in run 0 ({'attacks' if runs[0]['a'] else 'holds'}).",
        "Run 0 is the no-message base, where nobody attacks.",
        (f"Unsafe run{'s' if len(unsafe) > 1 else ''}: {', '.join(map(str, unsafe))}." if unsafe else "No run has exactly one division attacking, because nobody ever attacks."),
    ]
    alt = ("Left, a grid of attack or hold decisions for A and B in runs 0 to 3 with the runs each cannot tell apart boxed, and an outcome row marking unsafe runs. "
           "Right, the four runs from 3 down to 0 joined by arrows labelled with the party that cannot tell neighbouring runs apart, coloured by outcome.")
    return fig, metrics, interpretation, {"alt": alt, "steps": steps}


# Demonstration 3: private decisions against escrow with a deadline (Figure 20.4)

POLICIES = {
    "private": "Two private decisions",
    "escrow_seen": "Escrow, condition visible",
    "escrow_unseen": "Escrow, condition not visible",
}
OWNER_TEXT = {"A": "A keeps it", "B": "B holds it", "nobody": "nobody holds it"}


def token_outcome(policy, k):
    """(owner at dawn, A releases, B takes) for the policy in the run where k of the 3 messages were delivered."""
    if policy == "private":
        a_releases = k // 2 >= 1
        b_takes = (k + 1) // 2 >= 2
        if a_releases and b_takes:
            return "B", True, True
        if a_releases and not b_takes:
            return "nobody", True, False
        if b_takes and not a_releases:
            return "nobody", False, True
        return "A", False, False
    return ("B" if policy == "escrow_seen" else "A"), None, None


def escrow_picture(delivered=2, policy="private"):
    k = int(delivered)
    owner, a_rel, b_take = token_outcome(policy, k)
    outcomes = [token_outcome(policy, r)[0] for r in range(ROUND_MESSAGES + 1)]
    safe_runs = [r for r in range(ROUND_MESSAGES + 1) if outcomes[r] != "nobody"]
    unsafe_count = ROUND_MESSAGES + 1 - len(safe_runs)

    fig, (left, right) = new_figure(ncols=2, height=4.3)
    left.plot([0, ROUND_MESSAGES + 0.4], [1.0, 1.0], color=GREY, linewidth=1.2)
    left.plot([0, ROUND_MESSAGES + 0.4], [0.0, 0.0], color=GREY, linewidth=1.2)
    for j in range(1, ROUND_MESSAGES + 1):
        sender_a = j % 2 == 1
        y0, y1 = (1.0, 0.0) if sender_a else (0.0, 1.0)
        x0, x1 = j - 1 + 0.1, j - 0.1
        if j <= k:
            left.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops={"arrowstyle": "->", "color": TEAL, "linewidth": 2.2})
            left.text(x0 + 0.3 * (x1 - x0), y0 + 0.3 * (y1 - y0), str(j), ha="center", va="center", fontsize=11.5, color=TEAL, fontweight="bold", bbox=WHITE_BOX)
        elif j == k + 1:
            left.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops={"arrowstyle": "->", "color": TERRA, "linewidth": 1.8, "linestyle": "dashed"})
            left.text(x0 + 0.3 * (x1 - x0), y0 + 0.3 * (y1 - y0), str(j), ha="center", va="center", fontsize=11.5, color=TERRA, fontweight="bold", bbox=WHITE_BOX)
            left.text(x0 + 0.7 * (x1 - x0), y0 + 0.7 * (y1 - y0), "lost", ha="center", va="center", fontsize=10.5, color=TERRA, bbox=WHITE_BOX)
    left.set_xlim(-0.3, ROUND_MESSAGES + 0.5)
    left.set_ylim(-0.7, 1.7)
    left.set_xticks([])
    left.set_yticks([0.0, 1.0], ["B", "A"])
    left.set_xlabel("Messages: 1 proposal, 2 acknowledgement,\n3 confirmation (solid arrow: delivered)")
    left.set_ylabel("Division")
    left.set_title("What each division saw", fontsize=11.0)
    left.grid(alpha=0)

    if policy == "private":
        row_labels = ["A releases", "B takes", "token at dawn"]
    else:
        row_labels = ["authority", "messages seen", "token at dawn"]
    for r in range(ROUND_MESSAGES + 1):
        o, ar, bt = token_outcome(policy, r)
        if policy == "private":
            draw_cell(right, r, 2.0, ar, yes="releases", no="keeps", width=0.9)
            draw_cell(right, r, 1.0, bt, yes="takes", no="waits", width=0.9)
        else:
            draw_cell(right, r, 2.0, policy == "escrow_seen", yes="to B", no="to A", width=0.9)
            right.add_patch(Rectangle((r - 0.45, 0.65), 0.9, 0.7, facecolor="#e6ebec", edgecolor=GREY, linewidth=1.2))
            right.text(r, 1.0, f"{r} of 3", ha="center", va="center", fontsize=10.5, color=INK)
        bad = o == "nobody"
        right.add_patch(Rectangle((r - 0.45, -0.35), 0.9, 0.7, facecolor="#f3d9d1" if bad else "white", edgecolor=TERRA if bad else GREY,
                                  hatch="xx" if bad else None, linewidth=1.2))
        right.text(r, 0.0, {"A": "A", "B": "B", "nobody": "nobody"}[o], ha="center", va="center", fontsize=10.5, color=INK,
                   fontweight="bold" if bad else "normal", bbox=WHITE_BOX if bad else None)
    right.add_patch(Rectangle((k - 0.5, -0.45), 1.0, 2.9, fill=False, edgecolor=INK, linewidth=2.4))
    right.set_xlim(-0.6, ROUND_MESSAGES + 0.6)
    right.set_ylim(-0.7, 2.75)
    right.set_xticks(range(ROUND_MESSAGES + 1))
    right.set_yticks([0.0, 1.0, 2.0], row_labels[::-1])
    right.set_xlabel("Run: how many messages were delivered (boxed: this run)")
    right.set_ylabel("Decision or owner")
    right.set_title(POLICIES[policy], fontsize=11.0)
    right.grid(alpha=0)

    metrics = {
        "Policy": POLICIES[policy],
        "Messages delivered": f"{k} of 3",
        "Token at dawn": OWNER_TEXT[owner],
        "Exactly one owner in this run": "no" if owner == "nobody" else "yes",
        "Runs with exactly one owner": f"{len(safe_runs)} of {ROUND_MESSAGES + 1}",
    }
    if policy == "private":
        ra, rb = k // 2, (k + 1) // 2
        calc = (f"A has received {k} / 2 = {k / 2:.1f}, rounded down to {ra} message(s), and releases the token when it has received 1. "
                f"B has received ({k} + 1) / 2 = {(k + 1) / 2:.1f}, rounded down to {rb}, and takes it when it has received 2. "
                f"So the token ends with {'nobody (A released it and B did not take it)' if owner == 'nobody' else owner}. "
                f"Runs with exactly one owner = {ROUND_MESSAGES + 1} - {unsafe_count} = {len(safe_runs)}.")
        tail = (" Each division acts on its own private view, so run 2 is lost: A cannot tell run 2 from run 3, which is the same last-message problem as Demonstration 2.")
        steps = [
            "A releases the token once it has received B's acknowledgement; B takes it once it has received the confirmation.",
            f"A has received {k} / 2 = {k / 2:.1f}, rounded down to {ra}, so A {'releases' if a_rel else 'keeps'} the token.",
            f"B has received ({k} + 1) / 2 = {(k + 1) / 2:.1f}, rounded down to {rb}, so B {'takes' if b_take else 'waits'}.",
            f"Token at dawn: {OWNER_TEXT[owner]}.",
            f"Runs with exactly one owner = {ROUND_MESSAGES + 1} - {unsafe_count} = {len(safe_runs)} of {ROUND_MESSAGES + 1}.",
        ]
    else:
        seen = policy == "escrow_seen"
        calc = (f"Messages seen by the parties: {k} of 3, and this changes nothing: the authority applies one rule at the deadline. "
                f"The named condition is {'visible, so it releases the token to B' if seen else 'not visible, so it returns the token to A'}. "
                f"Runs with exactly one owner = {ROUND_MESSAGES + 1} - {unsafe_count} = {len(safe_runs)}.")
        tail = (" The token has one owner whatever the private messages did, which is the safety the two private decisions lacked. "
                + ("A transfer happens only because the public condition was visible." if seen else
                   "The price is that no transfer happens: the guarantee of joint action is replaced by a safe fallback."))
        steps = [
            "A places the token in escrow with a deadline; the authority, not A or B, moves it.",
            f"At the deadline the named condition is {'visible' if seen else 'not visible'}.",
            f"So the authority {'releases the token to B' if seen else 'returns the token to A'}.",
            f"The {k} of 3 delivered messages do not enter the rule, so the owner is the same in every run.",
            f"Runs with exactly one owner = {ROUND_MESSAGES + 1} - {unsafe_count} = {len(safe_runs)} of {ROUND_MESSAGES + 1}.",
        ]
    alt = (f"Left, a lane picture of the three messages with {k} delivered and the next one lost. Right, for the policy '{POLICIES[policy]}', "
           f"decisions and the token owner in each of four runs; the token ends with {OWNER_TEXT[owner]} in the boxed run.")
    return fig, metrics, calc + tail, {"alt": alt, "steps": steps}


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
    left.set_title(f"{rounds} round{'' if rounds == 1 else 's'}, each message dropped with probability {fmt(drop, 1)}", fontsize=11.0)
    left.grid(axis="y", alpha=0)

    xs = list(range(1, rounds + 1))
    (la,) = right.plot(xs, agree, "-o", color=TEAL, markersize=8)
    (lb,) = right.plot(xs, bob_knows, "--s", color=OLIVE, markersize=8, markerfacecolor="white", markeredgewidth=2)
    right.set_xlim(0.5, rounds + 0.5)
    right.set_ylim(-0.1, 1.2)
    right.set_xticks(xs)
    right.set_xlabel("Rounds of request and reply allowed")
    right.set_ylabel("Probability")
    right.set_title("Agreement and Bob's knowledge by round", fontsize=11.0)
    for x, y in zip(xs, agree):
        label_point(right, x, y, fmt(y, 3), color=TEAL, dx=0, dy=9, ha="center", va="bottom")
    for x, y in zip(xs, bob_knows):
        label_point(right, x, y, fmt(y, 3), color=OLIVE, dx=0, dy=-9 if drop == 0 else 9, ha="center", va="top" if drop == 0 else "bottom")
    right.legend([la, lb], ["agreement", "Bob knows his reply arrived"], loc="center", fontsize=10.0, frameon=False)

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
    steps = [
        f"Drop probability d = {trim(drop)}; a round has a request and a reply, each dropped independently.",
        f"A round fails to bring a reply back = 1 - (1 - {trim(drop)}) x (1 - {trim(drop)}) = {trim(miss)}.",
        f"Bob commits alone when every round fails but at least one request arrives: {trim(miss)}^{rounds} - {trim(drop)}^{rounds} = {trim(alone)}.",
        f"Agreement = 1 - {trim(alone)} = {trim(m['agreement_probability'])}.",
        f"Bob knows his reply arrived: {fmt(m['bob_knows_ack_receipt_probability'], 4)}, because "
        + ("losses were ruled out by assumption." if drop == 0 else "a lost reply looks the same to him as a delivered one."),
    ]
    alt = (f"Left, horizontal bars of four probabilities for {rounds} rounds at drop probability {fmt(drop, 1)}: agreement {fmt(m['agreement_probability'], 3)}, "
           f"Alice knows {fmt(m['alice_knows_delivery_probability'], 3)}, Bob knows {fmt(m['bob_knows_ack_receipt_probability'], 3)}, Bob commits alone {fmt(alone, 3)}. "
           "Right, agreement and Bob's knowledge against the number of rounds.")
    return fig, metrics, calc + tail, {"alt": alt, "steps": steps}


CHAPTER = {
    "number": 20,
    "title": "Messages, Beliefs, and Consensus",
    "subtitle": "Sending, receiving, acknowledging and committing are different events, and an unreliable final message cannot make them one.",
    "summary": (
        "These four demonstrations follow the chapter's two divisions that can win only by attacking together and can talk only by a "
        "messenger who may be lost. They show who knows what after each message and why no number of messages gives common knowledge, "
        "why a rule built on the last message fails, how an escrow state with a deadline stays safe when private messages do not, "
        "and why a high chance of agreement is not knowledge of agreement."
    ),
    "ask_skill": {"prompt": (
        "Take my handoff protocol, list the messages and what each party can observe after each one, and tell me which runs a party cannot "
        "tell apart. Then compute the agreement probability for my number of rounds and drop probability, and say what extra receipt "
        "or deadline rule the action I care about would need.")},
    "demos": [
        {
            "id": "C20-D01",
            "title": "One more message, one more level",
            "question": "After a few messages have been delivered, how many levels of mutual knowledge exist, who blocks the next one, and what makes a fact common knowledge?",
            "equations": [EQ_MK, EQ_CK],
            "symbols": (
                "P = {A, B} is the set of the two parties. F is a fact: either 'message 1, from A to B, was delivered' or 'dawn is the attack time on a public clock'. Know_i(F) means party i knows F. MK^1(F) means both A and B know F; "
                "MK^(n+1)(F) means each party knows MK^n(F). CK(F) is common knowledge of F: every level MK^n(F) holds. A run is labelled by k, the number of messages delivered in order (4 are planned): A sends the "
                "odd-numbered messages, B the even-numbered ones, and each is sent only after the one before it arrived. A party's view is the "
                "messages it sent and received. A party knows a fact only if the fact is true in every run that looks the same to it. A fact is common knowledge in the actual run exactly when it is true in every run reachable by links between runs a party cannot tell apart."
            ),
            "prediction": "Set 3 messages delivered, with the fact 'message 1 was delivered'. Which is the highest level of mutual knowledge, and who cannot reach the next one?",
            "prediction_options": ["Level 1, blocked by A", "Level 2, blocked by A", "Level 2, blocked by B", "Level 3, blocked by B"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "Highest level = 3 - 1 = 2. A sent message 3 and cannot tell run 2 from run 3, so A does not know level 2 and level 3 fails.",
                "incorrect": "Highest level = 3 - 1 = 2, and message 3 was sent by A, who cannot tell run 2 from run 3, so A blocks level 3. Set Messages delivered to 3 to see it.",
            },
            "stepper": "delivered",
            "misconception": {
                "title": "Enough acknowledgements make it common knowledge",
                "text": ("The chapter calls this an appealing but incorrect move: choosing a large enough number of acknowledgements and treating the remaining uncertainty as irrelevant by definition. "
                         "There is a strict gap between every finite depth and common knowledge."),
            },
            "scope_note": {
                "text": ("Finite unreliable messages can deepen awareness without common knowledge, so they cannot guarantee coordinated attack. "
                         "The chapter's point is narrower than a ban on messages: a private acknowledgement chain is not a guaranteed shared trigger for an irreversible simultaneous act."),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "The last sender of a delivered message cannot see that it arrived, so its view is the same in the run where it arrived and the one "
                "where it was lost. Equation (20.1) needs both parties to know the previous level, so the newest message's sender is always the one "
                "who fails. Each further delivered message passes the block to the other party and raises the highest level by exactly one, but the walk back through runs a party cannot "
                "tell apart always reaches the silent run, so Equation (20.2) never holds. A fact that is true in every run, like a public clock both can read, holds at every level with no message at all."
            ),
            "application": (
                "When a log shows request, reply and confirmation, write down who saw each message. The deepest level of mutual knowledge the "
                "exchange supports, for the fact that message 1 was delivered in a chain where each message is sent only after the previous one arrived, is one less than the number of messages delivered, and the next level depends on a message nobody can confirm. "
                "Before counting acknowledgements, list the facts every participant can observe and knows the others observe."
            ),
            "assumptions": (
                "One chain of messages in which each is sent only after the previous one arrived, and a message lost is not signalled to its sender. "
                "Other message patterns, a shared clock, or a signal when a message is lost would change which runs look the same. The level count depends on the "
                "choice of F; a fact both parties already knew would start higher. A public clock still needs a shared reading of time and a rule tying time to action."
            ),
            "check": "If 4 messages are delivered out of 4 planned, what is the highest level of mutual knowledge of message 1, and how many link steps lead back to the silent run?",
            "answer": "Highest level = 4 - 1 = 3. Level 4 fails because B sent message 4 and cannot tell run 3 from run 4. The walk back crosses 4 - 0 = 4 links to run 0, where message 1 was not delivered, so common knowledge fails.",
            "provenance": "Constructed example: a chain of messages defined for this reader to follow the chapter's two-division story, with who-knows-what computed from the runs and a public clock defined as a contrasting fact.",
            "source_section": "Stage three: finite depth has a boundary",
            "source_anchor": "stage-three-finite-depth-has-a-boundary",
            "controls": [
                {"key": "delivered", "label": "Messages delivered (4 planned)", "values": [1, 2, 3, 4], "default": 2},
                {"key": "fact", "label": "Fact being tested", "values": ["message", "clock"], "default": "message",
                 "value_labels": ["Message 1 was delivered", "Dawn on a public clock"]},
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
            "prediction_options": ["Run 1", "Run 2", "Run 3"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "In run 2 A has received 1 message and attacks, while B has received (2 + 1) / 2 = 1.5, rounded down to 1, and holds. Dashed boxes show A cannot tell run 2 from run 3.",
                "incorrect": "Run 2 is the unsafe run: A has received 1 message and attacks, while B has received 1 and needs 2. In run 3 both attack, and A cannot tell run 2 from run 3.",
            },
            "misconception": {
                "title": "One more confirmation fixes it",
                "text": ("The chapter's answer to requiring B to acknowledge once more is that it moves the vulnerable boundary back to A. "
                         "Every delivered message looks like extra protection and often is for a local decision, but a final delivery does not have a final acknowledgement within a finite exchange."),
            },
            "scope_note": {
                "text": ("The test is not a substitute for a full protocol proof; it locates a hidden assumption instead. Randomized rules cannot restore an absolute all-runs guarantee, "
                         "and a public commitment already authorizing both attacks lies outside this result."),
                "source_section": "The test is not a substitute for a full protocol proof",
            },
            "explanation": (
                "A rule can be written as a pair of thresholds on received messages. For every pair that ever makes a division attack, some run has "
                "one attacking and one holding, because the party that sent the final message cannot tell the last run from the one before it. "
                "The right panel replays the chapter's reduction: remove the last delivered message, the sender's view is unchanged so its decision is unchanged, "
                "and repeating this reaches the no-message run where nobody attacks. With each division needing at least one received message (the chapter's no-message nonattack base), the only pair that is safe is the one that never attacks."
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
            "title": "Escrow with a deadline",
            "question": "If two private decisions can strand a token, what does an escrow state with a deadline guarantee, and what does it give up?",
            "equations": [EQ_KNOW],
            "symbols": (
                "Know_i(F) means division i knows F. Three messages are sent in order (proposal, acknowledgement, confirmation) and a run is the number k that were delivered. "
                "Two private decisions: A releases the token once it has received the acknowledgement, B takes it once it has received the confirmation. Escrow with a deadline: A places the token in escrow, "
                "and at the deadline a shared authority releases it to B if a named condition is visible and returns it to A if not. 'Exactly one owner' means the token is with A, with B or in escrow, never held by nobody."
            ),
            "prediction": "With two private decisions, in which run is the token held by nobody?",
            "prediction_options": ["Run 0", "Run 1", "Run 2", "Run 3"],
            "prediction_answer": 2,
            "prediction_feedback": {
                "correct": "In run 2 A has received 1 message and releases the token, while B has received 1 and needs 2, so nobody holds it. Select 2 messages delivered.",
                "incorrect": "Run 2 strands the token: A has received 1 message and releases it, while B has received 1 and needs 2. Select 2 messages delivered to see it.",
            },
            "misconception": {
                "title": "A timeout proves what happened remotely",
                "text": ("The chapter says timeouts do not reveal what happened remotely: they end local waiting under a shared policy. "
                         "Their value is a predictable, safe response to uncertainty, so the escrow rule here never uses a guess about which messages arrived."),
            },
            "scope_note": {
                "text": ("The result does not rank protocols, set retry counts, or require a public ledger. Engineering chooses deadlines, recovery paths, and delivery assumptions."),
                "source_section": "What this does not settle",
            },
            "explanation": (
                "With two private decisions, each division acts on its own view, so the run where A has released but B has not taken leaves the token stranded: the last-message problem again. "
                "With escrow, the irreversible step moves to a shared authority that applies one rule at a deadline, so the owner is the same in every run and the private messages no longer decide it. "
                "What changes is the guarantee: the escrow always has an owner, but a transfer happens only when the public condition is visible."
            ),
            "application": (
                "For a handoff that moves an external effect, put the irreversible act behind one authority with a deadline and a named condition, and state the fallback, instead of making two private acknowledgements trigger it."
            ),
            "assumptions": (
                "A constructed token and three messages in sequence. The authority is reliable, its rule and deadline are known to both parties, and the named condition is a declared input, not a message. "
                "Real systems must also say who observes the condition, how clock skew is handled and what happens if the authority is unreachable."
            ),
            "check": "With two private decisions and 3 messages delivered, who holds the token, and how many of the four runs end with exactly one owner?",
            "answer": "A has received 3 / 2 = 1.5, rounded down to 1, and releases; B has received (3 + 1) / 2 = 2 and takes it. B holds it. Only run 2 strands the token, so 4 - 1 = 3 of 4 runs end with exactly one owner.",
            "provenance": "Constructed example: the chapter's two-agent resource transfer with an escrow state and deadline (Figure 20.4), with the three-message rule of Demonstration 2 used for the private decisions.",
            "source_section": "Stage seven: building agent protocols that fail safely",
            "source_anchor": "stage-seven-building-agent-protocols-that-fail-safely",
            "controls": [
                {"key": "delivered", "label": "Messages delivered (of 3)", "values": [0, 1, 2, 3], "default": 2},
                {"key": "policy", "label": "Policy", "values": ["private", "escrow_seen", "escrow_unseen"], "default": "private",
                 "value_labels": ["Two private decisions", "Escrow, condition visible", "Escrow, condition not visible"]},
            ],
            "function": "escrow_picture",
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
            "prediction": "At a drop probability of 0.5, does a second round raise agreement above the one-round value of 0.75?",
            "prediction_options": ["Higher than 0.75", "Lower than 0.75", "Exactly 0.75"],
            "prediction_answer": 1,
            "prediction_feedback": {
                "correct": "With R = 2, Bob commits alone with probability 0.75^2 - 0.5^2 = 0.3125, so agreement is 0.6875, below 0.75. Select 2 rounds at 0.5.",
                "incorrect": "With R = 2, Bob commits alone with probability 0.75^2 - 0.5^2 = 0.3125, so agreement is 0.6875, below 0.75. Select 2 rounds at 0.5.",
            },
            "misconception": {
                "title": "A high agreement probability is knowledge of agreement",
                "text": ("The chapter's companion notebook shows that probability of agreement and knowledge of agreement are different quantities. "
                         "Great depth can make an accident very unlikely under a probabilistic model, but it cannot satisfy the logical demand that neither division attacks unless the other will."),
            },
            "scope_note": {
                "text": ("The bounded model adds probabilities to a finite exchange. It shows that the two quantities differ, and it does not prove the theorem."),
                "source_section": "it does not prove the theorem",
            },
            "explanation": (
                "Bob commits alone when some request arrives but no reply gets back: probability [1 - (1 - d)^2]^R - d^R. For a small drop "
                "probability more rounds shrink it. For a large one the first term decays slowly and agreement can dip before it recovers (at d = 0.5 "
                "it goes 0.75, 0.6875, 0.703, 0.746). Bob's view never shows whether his reply arrived, so the worlds he cannot tell apart always include "
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
            "provenance": "Constructed example: the laboratory's bounded request-and-reply model with the notebook's default (2 rounds, 0.3), changed (2 rounds, 0) and transfer (3 rounds, 0.5) cases, computed with the laboratory's own function.",
            "source_section": "Stage eight: consensus begins with a shared event model",
            "source_anchor": "stage-eight-consensus-begins-with-a-shared-event-model",
            "controls": [
                {"key": "rounds", "label": "Rounds of request and reply", "values": [1, 2, 3, 4], "default": 2},
                {"key": "drop", "label": "Probability that a message is dropped", "values": [0, 0.3, 0.5], "default": 0.3},
            ],
            "function": "agreement_picture",
        },
    ],
}

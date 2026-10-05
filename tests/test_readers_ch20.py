"""Chapter 20 laboratory reader: independent hand checks of a freshly built page.

Every expected number is recomputed here from the chapter's own arithmetic
(the knowledge ladder of a message chain, the three-message rule, the walk
back to the silent run, the bounded-message probabilities), not read back from
the module that produced the page. The reader is built into a temporary
directory, so the test needs no committed output.
"""
from __future__ import annotations

import html
import json
import math
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
PYTHON = LAB / ".venv" / "bin" / "python"


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


@unittest.skipUnless(PYTHON.is_file(), "laboratory .venv absent")
class Chapter20ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([str(PYTHON), str(WRAPPER), "--chapters", "20", "--out", cls.tmp.name],
                             capture_output=True, text=True, timeout=900)
        assert run.returncode == 0, run.stdout + run.stderr
        cls.reader = next(Path(cls.tmp.name).glob("20-*/reader.html"))
        cls.page = cls.reader.read_text(encoding="utf-8")
        match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', cls.page, re.S)
        cls.data = json.loads(match.group(1))
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def section_text(self, demo_id):
        """Visible static text of one demonstration (question, explanation, symbols, check and answer)."""
        match = re.search(rf'<section class="demo" id="{demo_id}".*?</section>', self.page, re.S)
        self.assertIsNotNone(match, demo_id)
        return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", match.group(0))).split())

    RAW = {
        "C20-D01": [[1, 2, 3, 4], ["message", "clock"]],
        "C20-D02": [[1, 2], [1, 2, 3]],
        "C20-D03": [[0, 1, 2, 3], ["private", "escrow_seen", "escrow_unseen"]],
        "C20-D04": [[1, 2, 3, 4], [0, 0.3, 0.5]],
    }

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [self.RAW[demo_id][n][i] for n, i in enumerate(idx)]
            yield values, state, dict(state["metrics"])

    def test_structure_and_budget(self):
        self.assertEqual(list(self.demos), ["C20-D01", "C20-D02", "C20-D03", "C20-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 6, 12, 12])
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    @staticmethod
    def chain_levels(planned, delivered, fact):
        """Independent possible-worlds check of the knowledge ladder; returns (holds[n], A knows level n-1, B knows level n-1) for n = 1..5."""
        runs = range(planned + 1)

        def view(party, k):
            mine_odd = party == "A"
            sent = tuple(j for j in range(1, min(k + 1, planned) + 1) if (j % 2 == 1) == mine_odd)
            got = tuple(j for j in range(1, k + 1) if (j % 2 == 1) != mine_odd)
            return sent, got

        def knows(party, truth, k):
            return all(truth[w] for w in runs if view(party, w) == view(party, k))

        level = [k >= 1 for k in runs] if fact == "message" else [True for _ in runs]
        out = []
        for n in range(1, 6):
            a = [knows("A", level, k) for k in runs]
            b = [knows("B", level, k) for k in runs]
            both = [x and y for x, y in zip(a, b)]
            out.append((both[delivered], a[delivered], b[delivered]))
            level = both
        return out

    @staticmethod
    def walk_length(planned, start):
        """Links between runs a party cannot tell apart, from `start` to run 0 (breadth first), written independently."""
        def view(party, k):
            mine_odd = party == "A"
            sent = tuple(j for j in range(1, min(k + 1, planned) + 1) if (j % 2 == 1) == mine_odd)
            got = tuple(j for j in range(1, k + 1) if (j % 2 == 1) != mine_odd)
            return sent, got
        dist, todo = {start: 0}, [start]
        while todo:
            k = todo.pop(0)
            for w in range(planned + 1):
                if w not in dist and any(view(p, w) == view(p, k) for p in "AB"):
                    dist[w] = dist[k] + 1
                    todo.append(w)
        return dist[0], len(dist)

    def test_d01_level_is_delivered_minus_one_and_the_blocker_is_the_last_sender(self):
        for (k, fact), state, m in self.states("C20-D01"):
            rows = self.chain_levels(4, k, fact)
            highest = 0
            for holds, _, _ in rows:
                if holds:
                    highest += 1
                else:
                    break
            if fact == "message":
                self.assertEqual(highest, k - 1)
                self.assertEqual(m["Highest level that holds"], str(highest) if highest else "none (A does not know F)")
                self.assertEqual(m["B knows F (Know_B)"], "yes")
                self.assertEqual(m["A knows F (Know_A)"], "yes" if k >= 2 else "no")
                sender = "A" if k % 2 == 1 else "B"  # the sender of message k cannot see it arrive
                self.assertEqual(m["Next level blocked by"], sender)
                nxt = rows[highest]  # row for level highest + 1: who knows level `highest`
                self.assertEqual([not nxt[1], not nxt[2]], [sender == "A", sender == "B"])
                steps_len, reachable = self.walk_length(4, k)
                self.assertEqual(steps_len, k)
                self.assertEqual(m["Common knowledge of F (Equation 20.2)"], "fails")
                self.assertEqual(m["Runs reachable from the actual run"], f"{reachable} of 5")
                self.assertIn(f"= {k} - 1 = {k - 1}", state["interpretation"])
                self.assertIn(f"{k} - 0 = {k}", state["interpretation"])
                self.assertIn(f"Highest level of mutual knowledge of F that holds = {k} - 1 = {k - 1}.", state["steps"])
            else:
                self.assertEqual(highest, 5)
                self.assertEqual(m["Highest level that holds"], "all 5 checked hold")
                self.assertEqual(m["Common knowledge of F (Equation 20.2)"], "holds")
                self.assertEqual(m["Runs reachable from the actual run"], "5 of 5")
                self.assertIn("4 + 1 = 5", state["interpretation"])

    def test_d01_check_answer_blames_b_for_four_of_four(self):
        rows = self.chain_levels(4, 4, "message")
        self.assertEqual([n + 1 for n, (h, _, _) in enumerate(rows) if h], [1, 2, 3])
        _, a_knows_3, b_knows_3 = rows[3]  # row for n = 4 asks who knows level 3
        self.assertTrue(a_knows_3)
        self.assertFalse(b_knows_3)
        text = self.section_text("C20-D01")
        self.assertIn("Level 4 fails because B sent message 4 and cannot tell run 3 from run 4", text)

    def test_d01_prediction_answer_matches_run_three(self):
        rows = self.chain_levels(4, 3, "message")
        self.assertEqual([h for h, _, _ in rows][:3], [True, True, False])  # highest level 2
        self.assertFalse(rows[2][1])  # A does not know level 2
        self.assertTrue(rows[2][2])   # B does
        self.assertIn("Level 2, blocked by A", self.section_text("C20-D01"))

    def test_d02_threshold_rule_by_hand(self):
        for (a, b), state, m in self.states("C20-D02"):
            a, b = int(a), int(b)
            a_runs = [k for k in range(4) if k // 2 >= a]          # A receives messages 2 only
            b_runs = [k for k in range(4) if (k + 1) // 2 >= b]    # B receives messages 1 and 3
            unsafe = [k for k in range(4) if (k in a_runs) != (k in b_runs)]
            show = lambda xs: ", ".join(map(str, xs)) if xs else "none"
            self.assertEqual(m["A attacks in runs"], show(a_runs))
            self.assertEqual(m["B attacks in runs"], show(b_runs))
            self.assertEqual(m["Unsafe runs (exactly one attacks)"], show(unsafe))
            self.assertEqual(m["Safe in every run"], "yes" if not unsafe else "no")
            # Theorem: a rule that ever attacks is unsafe somewhere; only inaction is safe.
            if a_runs or b_runs:
                self.assertTrue(unsafe, (a, b))
            else:
                self.assertEqual(unsafe, [])
        chapter_rule = dict((tuple(v), s) for v, s, _ in self.states("C20-D02"))[(1, 2)]
        cm = dict(chapter_rule["metrics"])  # the chapter's table: only run 2 splits, run 3 has both attack
        self.assertEqual(cm["Unsafe runs (exactly one attacks)"], "2")
        self.assertEqual(cm["Both attack when all 3 arrive"], "yes")
        inaction = dict(next(s for v, s, _ in self.states("C20-D02") if v == [2, 3])["metrics"])
        self.assertEqual(inaction["Safe in every run"], "yes")
        self.assertEqual(inaction["A attacks in runs"], "none")

    def test_d02_reduction_steps_follow_the_induction(self):
        # Removing message j leaves its sender's view unchanged: message 3 is A's, 2 is B's, 1 is A's.
        for (a, b), state, m in self.states("C20-D02"):
            steps = state["steps"]
            self.assertEqual(len(steps), 8)
            self.assertIn("Remove message 3 (sent by A): A's view is unchanged", steps[3])
            self.assertIn("Remove message 2 (sent by B): B's view is unchanged", steps[4])
            self.assertIn("Remove message 1 (sent by A): A's view is unchanged", steps[5])
            a_run2 = 2 // 2 >= a
            self.assertTrue(steps[3].endswith(f"({'attacks' if a_run2 else 'holds'})."), (a, b, steps[3]))
            b_run1 = (1 + 1) // 2 >= b
            self.assertTrue(steps[4].endswith(f"({'attacks' if b_run1 else 'holds'})."), (a, b, steps[4]))
            a_run0 = 0 // 2 >= a
            self.assertTrue(steps[5].endswith(f"({'attacks' if a_run0 else 'holds'})."), (a, b, steps[5]))

    def test_d02_scope_of_the_only_safe_pair_and_the_chapter_table_clause(self):
        self.assertIn("at least one received message", self.section_text("C20-D02"))
        for (a, b), state, _ in self.states("C20-D02"):
            tail_has_table = "chapter's three-message table" in state["interpretation"]
            self.assertEqual(tail_has_table, (a, b) == (1, 2), (a, b))
        one_one = next(s for (a, b), s, _ in self.states("C20-D02") if (a, b) == (1, 1))
        self.assertIn("Run 1:", one_one["interpretation"])  # B attacks on the proposal alone, unlike the chapter's table row
        self.assertIn("B attacks and A holds", one_one["interpretation"])

    def test_d02_symbols_define_the_floor_counts_and_f(self):
        text = self.section_text("C20-D02")
        self.assertIn("A receives only the even-numbered message", text)
        self.assertIn("(k + 1) / 2", text)
        self.assertIn("F is any statement about which messages arrived", text)
        for demo_id in ("C20-D01", "C20-D04"):
            self.assertIn("is the set of the two parties", self.section_text(demo_id), demo_id)

    def test_d02_figure_boxes_cover_every_indistinguishable_pair(self):
        # A cannot tell run 0 from run 1 (sent message 1, received nothing), nor 2 from 3; B cannot tell 1 from 2.
        def view_a(k):
            return (1,), tuple(j for j in range(1, k + 1) if j % 2 == 0)
        self.assertEqual(view_a(0), view_a(1))
        self.assertEqual(view_a(2), view_a(3))
        self.assertNotEqual(view_a(1), view_a(2))

    def test_d03_token_outcomes_by_hand(self):
        owner_text = {"A": "A keeps it", "B": "B holds it", "nobody": "nobody holds it"}
        for (k, policy), state, m in self.states("C20-D03"):
            if policy == "private":
                a_releases, b_takes = k // 2 >= 1, (k + 1) // 2 >= 2
                owner = "B" if (a_releases and b_takes) else ("nobody" if a_releases != b_takes else "A")
                safe = sum(1 for r in range(4) if not ((r // 2 >= 1) != ((r + 1) // 2 >= 2)))
                self.assertEqual(safe, 3)
                self.assertIn(f"Runs with exactly one owner = 4 - {4 - safe} = {safe}.", state["interpretation"])
                self.assertIn(f"A has received {k} / 2 = {k / 2:.1f}, rounded down to {k // 2}", state["interpretation"])
                self.assertIn(f"B has received ({k} + 1) / 2 = {(k + 1) / 2:.1f}, rounded down to {(k + 1) // 2}", state["interpretation"])
            else:
                owner = "B" if policy == "escrow_seen" else "A"
                safe = 4
                self.assertIn("Runs with exactly one owner = 4 - 0 = 4.", state["interpretation"])
            self.assertEqual(m["Token at dawn"], owner_text[owner])
            self.assertEqual(m["Exactly one owner in this run"], "no" if owner == "nobody" else "yes")
            self.assertEqual(m["Runs with exactly one owner"], f"{safe} of 4")
        # The only stranded run under two private decisions is run 2, the unsafe run of the three-message table.
        stranded = [k for (k, p), s, m in self.states("C20-D03") if p == "private" and m["Exactly one owner in this run"] == "no"]
        self.assertEqual(stranded, [2])

    def test_d03_escrow_owner_ignores_the_messages(self):
        owners = {}
        for (k, policy), state, m in self.states("C20-D03"):
            owners.setdefault(policy, set()).add(m["Token at dawn"])
        self.assertEqual(owners["escrow_seen"], {"B holds it"})
        self.assertEqual(owners["escrow_unseen"], {"A keeps it"})
        self.assertEqual(len(owners["private"]), 3)

    def test_d04_bounded_message_probabilities(self):
        for (rounds, drop), state, m in self.states("C20-D04"):
            r, d = int(rounds), float(drop)
            miss = 1 - (1 - d) ** 2
            alone = miss ** r - d ** r
            alice = 1 - miss ** r  # Alice knows delivery exactly when she saw a reply
            self.assertEqual(m["Bob commits without Alice"], f"{alone:.4f}")
            self.assertEqual(m["Agreement probability"], f"{1 - alone:.4f}")
            self.assertEqual(m["Alice knows the request arrived"], f"{alice:.4f}")
            self.assertEqual(m["Bob knows his reply arrived"], "1.0000" if d == 0 else "0.0000")
            self.assertEqual(m["Delivery bit patterns allowed"], f"{1 if d == 0 else 4 ** r} of {4 ** r}")
        by = {tuple(v): dict(s["metrics"]) for v, s, _ in self.states("C20-D04")}
        self.assertEqual(by[(2, 0.3)]["Bob commits without Alice"], "0.1701")      # notebook default
        self.assertEqual(by[(2, 0)]["Agreement probability"], "1.0000")            # changed case: no drops
        self.assertEqual(by[(3, 0.5)]["Bob commits without Alice"], "0.2969")      # notebook transfer case
        self.assertEqual(by[(3, 0.5)]["Agreement probability"], "0.7031")
        # Agreement is not monotone in rounds at drop 0.5: 0.75, 0.6875, 0.703, 0.746.
        self.assertEqual([by[(r, 0.5)]["Agreement probability"] for r in (1, 2, 3, 4)], ["0.7500", "0.6875", "0.7031", "0.7461"])

    def test_d04_wording_fixes(self):
        for (rounds, drop), state, m in self.states("C20-D04"):
            text = state["interpretation"]
            self.assertIn("A round in which the reply does not get back to Alice = 1 - ", text)
            if drop > 0:
                self.assertIn("An agreement probability, high or not,", text)
        state = next(s for (r, d), s, _ in self.states("C20-D04") if (r, d) == (2, 0.3))
        self.assertIn("the reply does not get back to Alice = 1 - (1 - 0.3) x (1 - 0.3) = 0.51", state["interpretation"])
        self.assertIn("Delivery bit patterns allowed", dict(state["metrics"]))

    def test_optional_features_are_present(self):
        self.assertIn("Ask the chapter skill", self.page)
        for demo_id in self.demos:
            text = self.section_text(demo_id)
            self.assertIn("Common wrong turn", text, demo_id)
            self.assertIn("What this does not settle", text, demo_id)
            self.assertIn("Your prediction", text, demo_id)
            for _, state, _ in self.states(demo_id):
                self.assertTrue(2 <= len(state["steps"]) <= 8)

    def test_scope_notes_quote_the_chapter(self):
        chapter = (LAB.parent / "Manuscript/part-v/20-messages-beliefs-and-consensus.md").read_text(encoding="utf-8")
        flat = " ".join(chapter.split())
        for phrase in ("Finite unreliable messages can deepen awareness without common knowledge, so they cannot guarantee coordinated attack.",
                       "a private acknowledgement chain is not a guaranteed shared trigger for an irreversible simultaneous act",
                       "The test is not a substitute for a full protocol proof; it locates a hidden assumption instead.",
                       "The result does not rank protocols, set retry counts, or require a public ledger.",
                       "Engineering chooses deadlines, recovery paths, and delivery assumptions.",
                       "it does not prove the theorem"):
            self.assertIn(phrase, flat)

    def test_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 20)
        norm = lambda t: re.sub(r"[\s{}]", "", re.sub(r"\\[,;:!]|\\q?quad", "", re.sub(r"\\tag\{[^}]*\}", "", t))).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        allowed.add(norm(r"\operatorname{Know}_i(F)"))
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertGreaterEqual(len(alts), 1)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_text_rules(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "--", "\u2212"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_every_state_renders_and_check_is_clean(self):
        run = subprocess.run([str(PYTHON), str(WRAPPER), "--chapters", "20", "--check"], capture_output=True, text=True, timeout=900)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=180)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (38, 4, 8))
        self.assertEqual(report["ask_skill"], 1)


    def test_patch2_scope_of_k_minus_one_and_duplicate_phrase(self):
        text = self.section_text("C20-D01")
        self.assertIn("for the fact that message 1 was delivered in a chain where each message is sent only after the previous one arrived", text)
        self.assertIn("a shared clock, or a signal when a message is lost would change", text)
        self.assertNotIn("a shared clock used as a signal on loss", text)


if __name__ == "__main__":
    unittest.main()

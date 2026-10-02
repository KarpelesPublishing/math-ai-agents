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

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)]
            yield values, state, dict(state["metrics"])

    def test_structure_and_budget(self):
        self.assertEqual(list(self.demos), ["C20-D01", "C20-D02", "C20-D03", "C20-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 6, 8, 6])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_level_is_delivered_minus_one(self):
        for (k, planned), state, m in self.states("C20-D01"):
            k = int(k)
            highest = k - 1
            self.assertEqual(m["Highest level that holds"], str(highest) if highest else "none (A does not know F)")
            self.assertEqual(m["B knows F (Know_B)"], "yes")  # message 1 arrived in every selectable run
            self.assertEqual(m["A knows F (Know_A)"], "yes" if k >= 2 else "no")
            sender = "A" if k % 2 == 1 else "B"  # the sender of message k cannot see it arrive
            self.assertEqual(m[f"Level {highest + 1} is blocked by"], sender)
            self.assertIn(f"= {k} - 1 = {highest}", state["interpretation"])

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

    def test_d03_walk_back_and_public_clock(self):
        for (n, fact), state, m in self.states("C20-D03"):
            n = int(n)
            if fact == "Message 1 was delivered":
                self.assertEqual(m["Highest level that holds"], f"{n - 1} (level {n} fails)")
                self.assertEqual(m["Common knowledge of F (Equation 20.2)"], "fails")
                self.assertEqual(m["F true in every reachable run"], "no")
                self.assertIn(f"= {n} - 1 = {n - 1}", state["interpretation"])
                self.assertIn(f"{n} - 0 = {n}", state["interpretation"])
            else:
                self.assertEqual(m["Common knowledge of F (Equation 20.2)"], "holds")
                self.assertEqual(m["Highest level that holds"], "all 6 checked hold")
                self.assertIn(f"{n} + 1 = {n + 1}", state["interpretation"])
            self.assertEqual(m["Runs reachable from the actual run"], f"{n + 1} of {n + 1}")

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
        self.assertEqual(by[(3, 0.5)]["Bob commits without Alice"], "0.2969")      # notebook transfer case
        self.assertEqual(by[(3, 0.5)]["Agreement probability"], "0.7031")
        # Agreement is not monotone in rounds at drop 0.5: one round 0.75, two rounds 0.6875.
        one_round = 1 - ((1 - 0.25) - 0.5)
        self.assertAlmostEqual(one_round, 0.75)
        self.assertLess(float(by[(2, 0.5)]["Agreement probability"]), one_round)

    @staticmethod
    def chain_blockers(delivered, planned):
        """Independent possible-worlds check: who fails to know the next level of mutual knowledge of F = 'message 1 delivered'."""
        runs = range(planned + 1)

        def view(party, k):
            mine_odd = party == "A"
            sent = tuple(j for j in range(1, min(k + 1, planned) + 1) if (j % 2 == 1) == mine_odd)
            got = tuple(j for j in range(1, k + 1) if (j % 2 == 1) != mine_odd)
            return sent, got

        def knows(party, truth, k):
            return all(truth[w] for w in runs if view(party, w) == view(party, k))

        level = [k >= 1 for k in runs]  # F
        out = []
        for n in range(1, 6):
            both = [knows("A", level, k) and knows("B", level, k) for k in runs]
            out.append((n, both[delivered], knows("A", level, delivered), knows("B", level, delivered)))
            level = both
        return out

    def test_d01_check_answer_blames_b_not_a_for_four_of_five(self):
        # g7-09: with 4 delivered of 5 planned, level 4 is blocked by B alone; A still knows level 3.
        rows = self.chain_blockers(4, 5)
        holds = {n: h for n, h, _, _ in rows}
        self.assertEqual([n for n in range(1, 6) if holds[n]], [1, 2, 3])
        _, _, a_knows_3, b_knows_3 = rows[3]  # row for n = 4 asks who knows level 3
        self.assertTrue(a_knows_3)
        self.assertFalse(b_knows_3)
        text = self.section_text("C20-D01")
        self.assertIn("Level 4 fails because B sent message 4 and cannot tell run 3 from run 4, so B does not know level 3", text)
        self.assertNotIn("Level 4 fails because A sent the fifth message", text)
        state = next(s for (k, n), s, _ in self.states("C20-D01") if (k, n) == (4, 5))
        self.assertEqual(dict(state["metrics"])["Level 4 is blocked by"], "B")

    def test_d01_control_label_does_not_promise_a_loss(self):
        self.assertNotIn("before a loss", self.section_text("C20-D01"))
        self.assertIn("Messages delivered", [c["label"] for c in self.demos["C20-D01"]["controls"]])

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
        for demo_id in ("C20-D01", "C20-D03", "C20-D04"):
            self.assertIn("is the set of the two parties", self.section_text(demo_id), demo_id)

    def test_d02_figure_boxes_cover_every_indistinguishable_pair(self):
        # A cannot tell run 0 from run 1 (sent message 1, received nothing), nor 2 from 3; B cannot tell 1 from 2.
        def view_a(k):
            return (1,), tuple(j for j in range(1, k + 1) if j % 2 == 0)
        self.assertEqual(view_a(0), view_a(1))
        self.assertEqual(view_a(2), view_a(3))
        self.assertNotEqual(view_a(1), view_a(2))

    def test_d03_message_fact_claims_only_no_common_knowledge_gain(self):
        for (n, fact), state, _ in self.states("C20-D03"):
            if fact == "Message 1 was delivered":
                self.assertIn("Messages added no common knowledge that run 0 did not already have.", state["interpretation"])
                self.assertNotIn("Messages added nothing that run 0", state["interpretation"])

    def test_d04_wording_fixes(self):
        for (rounds, drop), state, m in self.states("C20-D04"):
            text = state["interpretation"]
            self.assertNotIn("A round without a delivered request and reply", text)
            self.assertIn("A round in which the reply does not get back to Alice = 1 - ", text)
            if drop > 0:
                self.assertIn("An agreement probability, high or not,", text)
                self.assertNotIn("A high agreement probability", text)
        # The quantity is 1 - (1 - d)^2 = 0.51 at d = 0.3, while neither message arriving has probability 0.09.
        self.assertAlmostEqual(1 - 0.7 * 0.7, 0.51)
        self.assertAlmostEqual(0.3 * 0.3, 0.09)
        state = next(s for (r, d), s, _ in self.states("C20-D04") if (r, d) == (2, 0.3))
        self.assertIn("the reply does not get back to Alice = 1 - (1 - 0.3) x (1 - 0.3) = 0.51", state["interpretation"])
        # 16 and 64 are delivery bit patterns; the distinct histories are 3^R (9 and 27).
        self.assertEqual((3 ** 2, 3 ** 3), (9, 27))
        self.assertIn("Delivery bit patterns allowed", dict(state["metrics"]))
        self.assertNotIn("Possible message patterns", dict(state["metrics"]))

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
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (28, 4, 8))


if __name__ == "__main__":
    unittest.main()

"""Chapter 19 laboratory reader: independent hand checks of the built page.

Expected numbers are recomputed here from the chapter's printed means, from
the chapter's three-option cycle, and from weighted sums of the laboratory's
two-by-two matrix, not read back from the module that produced the page. The
reader is built into a temporary directory, so the committed readers folder
is never touched.
"""
from __future__ import annotations

import html
import importlib.util
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
MODULE = LAB / "tools" / "readers" / "chapters" / "ch19.py"
SLUG = "19-cross-play-transfer"


def builder_python():
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers.builder_python()


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


class Chapter19ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.python = builder_python()
        if cls.python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([cls.python, str(WRAPPER), "--chapters", "19", "--out", cls.tmp.name], capture_output=True,
                             text=True, timeout=600)
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls.tmp.name) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    # Raw control values, written here from the design (the page shows labels for text controls).
    RAW = {
        "C19-D01": [["small2", "small3", "small4", "gathering"]],
        "C19-D02": [[2, 4, 6, 12], ["A", "C"]],
        "C19-D03": [["diagonal", "off", "ratio"]],
        "C19-D04": [[0.1, 0.5, 0.56, 0.9]],
    }

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [self.RAW[demo_id][n][i] for n, i in enumerate(idx)], state

    def section_text(self, demo_id):
        """Visible static text of one demonstration (question, explanation, symbols and so on)."""
        match = re.search(rf'<section class="demo" id="{demo_id}".*?</section>', self.page, re.S)
        self.assertIsNotNone(match, demo_id)
        return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", match.group(0))).split())

    @staticmethod
    def m(state):
        return dict(state["metrics"])

    # structure and budgets

    def test_four_demonstrations_all_combinations_render(self):
        self.assertEqual(list(self.demos), ["C19-D01", "C19-D02", "C19-D03", "C19-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [4, 8, 3, 4])
        for d in self.data["demos"]:
            self.assertLessEqual(len(d["states"]), 8)
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    # D1: Equation (19.2) on the chapter's printed means

    def test_d01_losses_by_hand(self):
        means = {"small2": (30.44, 20.03), "small3": (23.06, 9.06), "small4": (20.15, 5.71), "gathering": (147.34, 146.89)}
        expected = {"small2": "0.342", "small3": "0.607", "small4": "0.717", "gathering": "0.003"}
        for (task,), state in self.states("C19-D01"):
            diag, off = means[task]
            loss = (diag - off) / diag
            m = self.m(state)
            self.assertEqual(m["Diagonal mean"], f"{diag:.2f}")
            self.assertEqual(m["Off-diagonal mean"], f"{off:.2f}")
            shown = m["Loss from Equation (19.2)"]
            self.assertTrue(shown.startswith(f"{loss:.3f}"), (task, shown))
            self.assertTrue(shown.startswith(expected[task]))
            self.assertIn(f"({diag:.2f} - {off:.2f}) / {diag:.2f}", state["interpretation"])

    def test_d01_small3_printed_value_is_flagged_not_hidden(self):
        # The chapter prints 0.625 for small3 but its printed means give 14 / 23.06 = 0.607.
        self.assertAlmostEqual(14.0 / 23.06, 0.607, places=3)
        small3 = next(s for (t,), s in self.states("C19-D01") if t == "small3")
        self.assertEqual(self.m(small3)["Loss from Equation (19.2)"], "0.607 (chapter prints 0.625)")
        self.assertIn("0.625", small3["interpretation"])
        for task, state in (("small2", None), ("small4", None), ("gathering", None)):
            s = next(s for (t,), s in self.states("C19-D01") if t == task)
            self.assertNotIn("chapter prints", self.m(s)["Loss from Equation (19.2)"])

    def test_d01_control_task_loss_is_small(self):
        gathering = next(s for (t,), s in self.states("C19-D01") if t == "gathering")
        self.assertLess(float(self.m(gathering)["Loss from Equation (19.2)"]), 0.01)
        self.assertIn("does not prove", gathering["interpretation"])

    # D2: the chapter's three-option cycle

    @staticmethod
    def reference_cycle(start, updates):
        # The chapter: party one prefers B against A, C against B, A against C; party two "the same way one step around".
        answer = {"A": "B", "B": "C", "C": "A"}
        beats = {("B", "A"), ("C", "B"), ("A", "C")}

        def pay(mine, theirs):
            return 0 if mine == theirs else (1 if (mine, theirs) in beats else -1)

        one, two = None, start
        trace, p1 = [], []
        for k in range(1, updates + 1):
            if k % 2:
                one = answer[two]
            else:
                two = answer[one]
            trace.append((k, one, two))
            p1.append(pay(one, two))
        return trace, p1

    def test_d02_chapter_trace_closes_after_six_updates(self):
        trace, p1 = self.reference_cycle("A", 6)
        # Chapter: party one B, party two C, party one A, party two B, party one C, party two A.
        self.assertEqual([t[1] if i % 2 == 0 else t[2] for i, t in enumerate(trace)], ["B", "C", "A", "B", "C", "A"])
        self.assertEqual(trace[-1][2], "A")
        self.assertEqual(sum(p1), 0)

    def test_d02_metrics_every_state(self):
        for (updates, start), state in self.states("C19-D02"):
            updates = int(updates)
            trace, p1 = self.reference_cycle(start, updates)
            back = next((k for k, one, two in trace if k % 2 == 0 and two == start), None)
            m = self.m(state)
            self.assertEqual(m["Updates shown"], str(updates))
            self.assertEqual(m["Mean payoff to party one"], f"{sum(p1) / updates:.2f}")
            self.assertEqual(m["Mover's payoff after its own update"], "+1 every time")
            if updates >= 6:
                self.assertEqual(back, 6)
                self.assertEqual(m["Party two back at its start"], "after 6 updates")
            else:
                self.assertIsNone(back)
                self.assertTrue(m["Party two back at its start"].startswith("not yet"))
            # first update answers the start option
            first = trace[0][1]
            self.assertIn(f"so Equation (19.4) picks {first}", state["interpretation"])

    def test_d02_mover_always_gains_one(self):
        # Each update is an exact best response: the mover's payoff is +1 against the option it faces.
        for start in "ABC":
            trace, _ = self.reference_cycle(start, 12)
            beats = {("B", "A"), ("C", "B"), ("A", "C")}
            for k, one, two in trace:
                mine, theirs = (one, two) if k % 2 else (two, one)
                self.assertIn((mine, theirs), beats)

    def test_d02_dependence_sentence_names_the_option_actually_played(self):
        # Regression for the reviewer's g7-01: the old text hard-coded option B (pays 1 against A, (-1) against C),
        # which is false when party two starts at C and party one plays A.
        beats = {("B", "A"), ("C", "B"), ("A", "C")}

        def pay(mine, theirs):
            return 0 if mine == theirs else (1 if (mine, theirs) in beats else -1)

        show = lambda v: "1" if v == 1 else ("0" if v == 0 else "(-1)")
        for (updates, start), state in self.states("C19-D02"):
            trace, _ = self.reference_cycle(start, int(updates))
            option, reply = trace[0][1], trace[1][2]
            expected = f"option {option} pays {show(pay(option, start))} against {start} but {show(pay(option, reply))} against {reply}"
            self.assertIn(expected, state["interpretation"], (updates, start))
            self.assertNotIn("the same option pays", state["interpretation"])
            if start == "C":
                self.assertEqual((option, reply), ("A", "B"))
                self.assertIn("option A pays 1 against C but (-1) against B", state["interpretation"])
                self.assertNotIn("pays 1 against A and (-1) against C", state["interpretation"])
            else:
                self.assertIn("option B pays 1 against A but (-1) against C", state["interpretation"])

    def test_d02_static_text_does_not_misstate_the_option_order(self):
        # g7-02: the options played in the default state are B, C, A, B, C, A, not A, B, C, A, B, C.
        self.assertNotIn("A, B, C, A, B, C", self.section_text("C19-D02"))
        self.assertIn("repeats every six updates", self.section_text("C19-D02"))

    def test_d01_does_not_claim_the_chapter_draws_a_diamond(self):
        small3 = next(s for (t,), s in self.states("C19-D01") if t == "small3")
        self.assertNotIn("as the chapter does", small3["interpretation"])
        self.assertIn("the chapter flags the same difference in its text", small3["interpretation"])

    def test_symbols_expand_jpc_and_define_u(self):
        for demo_id in ("C19-D01", "C19-D03", "C19-D04"):
            self.assertIn("joint policy correlation", self.section_text(demo_id), demo_id)
        self.assertIn("joint return", self.section_text("C19-D01"))
        self.assertIn("success indicator", self.section_text("C19-D04"))

    # D3: what a fix costs

    def test_d03_three_numbers_move_in_different_directions(self):
        before, after = (30.44, 20.03), (28.20, 26.63)
        loss0, loss1 = (before[0] - before[1]) / before[0], (after[0] - after[1]) / after[0]
        self.assertAlmostEqual(loss0, 0.342, places=3)
        self.assertAlmostEqual(loss1, 1.57 / 28.20, places=12)
        expected = {
            "Diagonal mean": (f"{before[0]:.2f}", f"{after[0]:.2f}", f"{after[0] - before[0]:.2f}", "regression"),
            "Off-diagonal mean": (f"{before[1]:.2f}", f"{after[1]:.2f}", f"{after[1] - before[1]:.2f}", "improvement"),
            "Loss from Equation (19.2)": (f"{loss0:.3f}", f"{loss1:.3f}", f"{loss1 - loss0:.3f}", "improvement"),
        }
        seen = set()
        for _, state in self.states("C19-D03"):
            m = self.m(state)
            b, a, change, verdict = expected[m["Number tracked"]]
            self.assertEqual((m["Independent learners"], m["Population method"], m["Change"], m["Reads as"]), (b, a, change, verdict))
            seen.add(m["Number tracked"])
        self.assertEqual(seen, set(expected))
        self.assertEqual(f"{after[0] - before[0]:.2f}", "-2.24")
        self.assertEqual(f"{after[1] - before[1]:.2f}", "6.60")

    def test_d03_ratio_state_flags_printed_5_5(self):
        ratio = next(s for (k,), s in self.states("C19-D03") if k == "ratio")
        self.assertIn("5.5 percent", ratio["interpretation"])
        self.assertIn("5.57 percent", ratio["interpretation"])

    def test_d03_loss_is_attributed_to_the_gap_and_the_28_7_point_difference_is_flagged(self):
        # g7-04: the loss falls because the gap collapses (10.41 to 1.57), not because of the division by the diagonal.
        self.assertAlmostEqual(30.44 - 20.03, 10.41)
        self.assertAlmostEqual(28.20 - 26.63, 1.57)
        # Dividing by the smaller diagonal alone would push the ratio up: 1.57 / 30.44 < 1.57 / 28.20.
        self.assertLess(1.57 / 30.44, 1.57 / 28.20)
        for _, state in self.states("C19-D03"):
            self.assertIn("driven by the gap", self.section_text("C19-D03"))
        explanation = self.section_text("C19-D03")
        self.assertIn("from 10.41 to 1.57", explanation)
        self.assertNotIn("Because Equation (19.2) divides the gap by the diagonal", explanation)
        # g7-05: chapter prints 34.2 - 5.5 = 28.7 points; the printed means give 28.6.
        ratio = next(s for (k,), s in self.states("C19-D03") if k == "ratio")
        self.assertEqual(f"{100 * ((30.44 - 20.03) / 30.44 - 1.57 / 28.20):.1f}", "28.6")
        self.assertIn("reduction of 28.7 points, while the printed means give 28.6", ratio["interpretation"])

    # D4: partner mix with the laboratory's matrix

    def test_d04_weighted_values_by_hand(self):
        for (w,), state in self.states("C19-D04"):
            v0 = w * 0.95 + (1 - w) * 0.2
            v1 = w * 0.4 + (1 - w) * 0.9
            m = self.m(state)
            self.assertEqual(m["Policy 0 against the mix"], f"{v0:.3f}")
            self.assertEqual(m["Policy 1 against the mix"], f"{v1:.3f}")
            expected = "tie" if abs(v0 - v1) < 1e-9 else ("Policy 0" if v0 > v1 else "Policy 1")
            self.assertEqual(m["Ranks first"], expected, w)
            self.assertEqual(m["Diagonal alone names"], "Policy 0")  # 0.95 against 0.90
            self.assertEqual(m["Loss from Equation (19.2)"], f"{(0.925 - 0.3) / 0.925:.3f}")

    def test_d04_the_tie_and_the_chapter_cases(self):
        by_w = {w: s for (w,), s in self.states("C19-D04")}
        self.assertAlmostEqual(0.7 / 1.25, 0.56)
        self.assertEqual(self.m(by_w[0.56])["Ranks first"], "tie")
        self.assertIn("tie at 0.620", by_w[0.56]["interpretation"].replace("The two policies tie at 0.620", "tie at 0.620"))
        # Laboratory worked values: equal weights give 0.575 and 0.65, weights 0.9 and 0.1 give 0.875 and 0.45.
        m5, m9 = self.m(by_w[0.5]), self.m(by_w[0.9])
        self.assertEqual((m5["Policy 0 against the mix"], m5["Policy 1 against the mix"], m5["Ranks first"]), ("0.575", "0.650", "Policy 1"))
        self.assertEqual((m9["Policy 0 against the mix"], m9["Policy 1 against the mix"], m9["Ranks first"]), ("0.875", "0.450", "Policy 0"))
        self.assertEqual(self.m(by_w[0.1])["Ranks first"], "Policy 1")

    def test_laboratory_function_agrees_with_the_chapter_formula(self):
        sys.path.insert(0, str(LAB / "src"))
        try:
            from math_ai_agents.chapters.ch19 import evaluate
        finally:
            sys.path.pop(0)
        out = evaluate({"matrix": [[0.95, 0.2], [0.4, 0.9]], "partner_weights": [0.5, 0.5], "supervisor_weights": [0.9, 0.1]})
        self.assertAlmostEqual(out["metrics"]["joint_policy_correlation_loss"], (0.925 - 0.3) / 0.925)
        one = evaluate({"matrix": [[0.9]], "partner_weights": [1.0], "supervisor_weights": [1.0]})
        self.assertIsNone(one["metrics"]["joint_policy_correlation_loss"])  # one policy: no off-diagonal, statistic undefined

    # equations, text rules, links, harness

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 19)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")

        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'alt="Equation: ([^"]+)"', self.page)
        self.assertEqual(len(alts), 7)  # D1: two, D2: two, D3: one, D4: two
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter", "scipy"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))
        source = MODULE.read_text(encoding="utf-8")
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, source)

    def test_links_and_accessibility(self):
        for href in ("../../notebooks/19-cross-play-transfer.ipynb", "../../skills/maa-19-cross-play-transfer/SKILL.md"):
            self.assertIn(f'href="{href}"', self.page)
            self.assertTrue((LAB / href.replace("../../", "")).exists(), href)
        self.assertIn('<a class="skip" href="#main">', self.page)
        self.assertEqual(self.page.count('aria-live="polite"'), 4)

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"]), (19, 4))


if __name__ == "__main__":
    unittest.main()

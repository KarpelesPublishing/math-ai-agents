"""Chapter 15 laboratory reader: independent hand checks of a freshly built page.

Every expected number is recomputed here from the chapter's arithmetic
(8 - 2 = 6, the 2 epsilon regret bound, the Exercise 1 value 4.8), not read
back from the module that produced the page. The page is built into a
temporary directory; the standard library reads it.
"""
from __future__ import annotations

import html
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from math_ai_agents.chapters.ch15 import evaluate

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"


def builder_python():
    for cand in (LAB / ".venv" / "bin" / "python",):
        if cand.is_file():
            return str(cand)
    return None


def payload(text):
    return json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))


def num(text):
    return float(text)


@unittest.skipIf(builder_python() is None, "laboratory .venv absent")
class Chapter15ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([builder_python(), str(WRAPPER), "--chapters", "15", "--out", cls.tmp.name],
                             capture_output=True, text=True, timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        assert run.returncode == 0, run.stdout + run.stderr
        cls.reader = Path(cls.tmp.name) / "15-memory-budget" / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [c["values"][i] for c, i in zip(demo["controls"], idx)]
            values = [float(v) if re.fullmatch(r"-?\d+(\.\d+)?", str(v)) else v for v in values]
            yield values, dict(state["metrics"]), state["interpretation"]

    def test_four_demos_and_budgets(self):
        self.assertEqual(list(self.demos), ["C15-D01", "C15-D02", "C15-D03", "C15-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 8, 6, 8])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_budgeted_retrieval_by_enumeration(self):
        records = [("rev", 2, 8), ("sum", 2, 3), ("app", 2, 0), ("note", 2, 0)]
        for (lam, budget), m, text in self.states("C15-D01"):
            best, sets = None, []
            for k in range(5):
                for sub in itertools.combinations(records, k):
                    if sum(r[1] for r in sub) > budget:
                        continue
                    tot = sum(r[2] - lam * r[1] for r in sub)
                    if best is None or tot > best + 1e-9:
                        best, sets = tot, [sub]
                    elif abs(tot - best) <= 1e-9:
                        sets.append(sub)
            self.assertEqual(m["Total net value"], f"{best:.1f}", (lam, budget))
            self.assertEqual(m["Best sets"], str(len(sets)), (lam, budget))
            self.assertEqual("(tie)" in m["Chosen by Equation (15.1)"], len(sets) > 1)
        by = {tuple(v): (m, t) for v, m, t in self.states("C15-D01")}
        m, t = by[(1.0, 2.0)]  # the book's case: room for 2 tokens, lambda 1
        self.assertEqual((m["Chosen by Equation (15.1)"], m["Total net value"]), ("Current revocation", "6.0"))
        self.assertIn("8 - 1 x 2 = 6.0", t)
        self.assertIn("0 - 1 x 2 = -2.0", t)
        m, _ = by[(1.0, 4.0)]
        self.assertEqual(m["Total net value"], "7.0")  # 6 + 1, both fit
        m, _ = by[(4.0, 2.0)]  # revocation net 8 - 8 = 0: tie with keeping nothing
        self.assertEqual(m["Best sets"], "2")
        self.assertIn("tie", m["Chosen by Equation (15.1)"])
        m, _ = by[(1.5, 4.0)]  # summary net 3 - 3 = 0: tie
        self.assertEqual((m["Best sets"], m["Total net value"]), ("2", "5.0"))
        m, _ = by[(1.5, 2.0)]  # summary net 0 but no room beside the revocation: no tie
        self.assertEqual(m["Best sets"], "1")

    def test_laboratory_agrees_with_book_example(self):
        out = evaluate({"budget": 2, "now": 10, "current_version": "v2", "records": [
            {"id": "rev", "tokens": 2, "decision_value": 6, "timestamp": 9, "ttl": 3, "authority": True, "version": "v2"},
            {"id": "old", "tokens": 2, "decision_value": 100, "timestamp": 9, "ttl": 3, "authority": True, "version": "v1"}],
            "original_action_values": [1, 0], "compressed_action_values": [1, 0]})
        self.assertEqual(out["metrics"]["retrieved_ids"], ["rev"])
        self.assertEqual(out["metrics"]["excluded_ids"], ["old"])

    def test_d02_regret_bound(self):
        for (eps, kind), m, text in self.states("C15-D02"):
            self.assertEqual(m["Limit 2\u03b5"], f"{2 * eps:.1f}")
            if kind.startswith("Scores"):
                s = [10 - eps, 6 + eps, 3]
                full = [10, 6, 3]
                top = max(s)
                picks = [i for i in range(3) if abs(s[i] - top) < 1e-9]
                regrets = [10 - full[i] for i in picks]
                self.assertEqual(m["Bound applies"], "yes")
                self.assertEqual(m["Largest error of the summary"], f"{eps:.1f}")
                if len(picks) > 1:
                    self.assertEqual(m["Regret of that action"], f"0.0 or {max(regrets):.1f}")
                    self.assertIn("(tie)", m["Summary follows"])
                else:
                    self.assertEqual(m["Regret of that action"], f"{regrets[0]:.1f}")
                self.assertLessEqual(max(regrets), 2 * eps + 1e-9)
            else:
                self.assertEqual(m["Bound applies"], "no")
                self.assertEqual(m["Regret of that action"], "56.0")  # 6 - (-50)
                self.assertEqual(m["Largest error of the summary"], "60.0")  # 10 - (-50)
                self.assertIn("no 2 epsilon claim applies", text)
        by = {tuple(v): (m, t) for v, m, t in self.states("C15-D02")}
        m, t = by[(2.0, "Scores off by epsilon, same actions")]  # exact tie at 8 = 8; the bound is reached (4 = 4)
        self.assertIn("(tie)", m["Summary follows"])
        self.assertIn("10 - 6 = 4.0", t)
        m, t = by[(3.0, "Scores off by epsilon, same actions")]
        self.assertEqual((m["Summary follows"], m["Regret of that action"], m["Limit 2\u03b5"]), ("Ask owner", "4.0", "6.0"))

    def test_d02_dropped_state_names_the_real_mechanism(self):
        # Reviewer finding g5-15: the figure lists the same three actions, with release scored -50 against 10.
        for (eps, kind), m, text in self.states("C15-D02"):
            if not kind.startswith("Dropped"):
                continue
            self.assertNotIn("The action sets differ", text)
            self.assertNotIn("whatever epsilon is", text)
            self.assertIn("this reader draws that as a value of -50", text)
            self.assertIn("an error of 10 - (-50) = 60, far above epsilon = " + f"{eps:g}", text)
            self.assertIn("The two versions disagree about which actions are permitted, so no 2 epsilon claim applies", text)
            self.assertIn("Changing epsilon moves only the limit bar here", text)  # g5-20
            self.assertEqual((m["Largest error of the summary"], m["Regret of that action"]), ("60.0", "56.0"))
        # The error 60 is the same in all four dropped states, so epsilon only moves the limit bar.
        dropped = [(m["Largest error of the summary"], m["Regret of that action"]) for v, m, _ in self.states("C15-D02")
                   if v[1].startswith("Dropped")]
        self.assertEqual(set(dropped), {("60.0", "56.0")})

    def test_d02_static_text_is_exact_about_ties_and_the_claim(self):
        page = html.unescape(self.page)
        # g5-16: at a gap of exactly 2 epsilon the rival ties, so the wording is "at most".
        self.assertNotIn("overtake only when the gap is under 2 epsilon", page)
        self.assertIn("match or overtake only when the gap is at most 2 epsilon", page)
        by = {tuple(v): (m, t) for v, m, t in self.states("C15-D02")}
        m, _ = by[(2.0, "Scores off by epsilon, same actions")]
        self.assertIn("(tie)", m["Summary follows"])  # gap 10 - 6 = 4 = 2 x 2
        # g5-15: the explanation no longer says the figure's actions differ.
        self.assertIn("the full history no longer permits release (drawn here as a value of -50)", page)
        # g5-17: the symbols say what the 2 epsilon limit bounds.
        self.assertIn("this regret is at most 2 epsilon when the conditions below hold", page)

    def test_d03_and_d04_state_their_modelling_conditions(self):
        page = html.unescape(self.page)
        # g5-18
        self.assertIn("The note is taken to be newer than the old approval; this ordering is defined for this reader", page)
        # g5-19: p = 0 is a feature of this model, not a general fact.
        self.assertNotIn("and can never pay for itself", page)
        self.assertIn("in this model, where a record is worth 8 only while it is current", page)
        for _, _, text in self.states("C15-D04"):
            self.assertIn("In this model a record is worth 8 only while it is current", text)
            self.assertNotIn("A deleted, expired or superseded record has p = 0", text)

    def test_d03_policies(self):
        for (rs, auth), m, text in self.states("C15-D03"):
            reach = auth == "Yes"
            sims = {"Old approval": 0.98, "Irrelevant note": 0.80}
            if reach:
                sims["Current revocation"] = rs
            top = max(sims, key=sims.get)
            expected_sim = {"Old approval": "Unauthorized release", "Current revocation": "Release blocked (correct)",
                            "Irrelevant note": "Irrelevant recollection"}[top]
            self.assertEqual(m["Similarity only"], f"{top}: {expected_sim}")
            self.assertTrue(m["Recency only"].startswith("Current revocation" if reach else "Irrelevant note"))
            if reach:
                self.assertEqual(m["Decision aware"], "Current revocation: Release blocked (correct)")
                self.assertIn("8 - 1 x 2 = 6.0", text)
            else:
                self.assertEqual(m["Decision aware"], "Abstain (correct)")
                self.assertNotIn("8 - 1 x 2", text)
        by = {tuple(v): m for v, m, _ in self.states("C15-D03")}
        self.assertTrue(by[(0.99, "Yes")]["Similarity only"].startswith("Current revocation"))
        self.assertTrue(by[(0.9, "Yes")]["Similarity only"].startswith("Old approval"))

    def test_d04_exercise_one(self):
        for (p, lam), m, text in self.states("C15-D04"):
            ev, net = 8 * p, 8 * p - lam
            self.assertEqual(m["Expected value"], f"{ev:.2f}")
            self.assertEqual(m["Net value"], f"{net:.2f}")
            self.assertEqual(m["Break-even p"], f"{lam / 8:.3f}")
            want = "tie" if abs(net) < 1e-9 else ("Retrieve" if net > 0 else "Leave out")
            self.assertEqual(m["Decision"], want)
        by = {tuple(v): (m, t) for v, m, t in self.states("C15-D04")}
        m, t = by[(0.6, 1.0)]
        self.assertEqual((m["Expected value"], m["Net value"]), ("4.80", "3.80"))  # the book's 4.8 and 3.8
        self.assertIn("0.60 x 8 + 0.40 x 0 = 4.80", t)
        self.assertEqual(by[(0.5, 4.0)][0]["Decision"], "tie")   # 4 - 4 = 0
        self.assertEqual(by[(0.25, 4.0)][0]["Net value"], "-2.00")

    def test_equations_are_chapter_text(self):
        source = (LAB.parent / "Manuscript" / "part-iv" / "15-what-an-agent-should-remember.md").read_text(encoding="utf-8")
        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t)
        flat = norm(source)
        found = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(found), 2)  # Equation (15.1) in Demonstrations 1 and 3
        for inline in (r"2\varepsilon", r"0.6\times8+0.4\times0=4.8"):
            self.assertIn(inline, flat)
            self.assertIn(inline, norm(self.page.replace('&#92;', chr(92))) + norm(html.unescape(self.page)))
        for tex in found:
            self.assertIn(norm(html.unescape(tex)).rstrip("."), flat)

    def test_text_rules_and_links(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for d in self.data["demos"]:
            for s in d["states"].values():
                text += " " + s["interpretation"] + " " + " ".join(" ".join(p) for p in s["metrics"])
        for bad in ("\u2014", "\u2013", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))
        self.assertIn('href="../../notebooks/15-memory-budget.ipynb"', self.page)

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual(report["states_checked"], 30)
        self.assertEqual(report["resets_checked"], 4)


if __name__ == "__main__":
    unittest.main()

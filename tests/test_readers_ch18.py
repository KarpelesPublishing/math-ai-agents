"""Chapter 18 laboratory reader: independent hand checks of a fresh build.

Every expected number is recomputed here from the chapter's own arithmetic
(two-layout beliefs, the intersection rule, exp(-rate x delay), and the
price of another look), not read back from the module that produced the page.
The reader is built into a temporary directory.
"""
from __future__ import annotations

import html
import importlib.util
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


def _builder_python():
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers.builder_python()


def payload(text):
    return json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))


def as_number(text):
    text = text.split(":")[0]  # labels such as "40: unguarded harmful release"
    try:
        return float(text)
    except ValueError:
        return text


@unittest.skipIf(_builder_python() is None, "no interpreter with numpy, matplotlib and jinja2")
class Chapter18ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([_builder_python(), str(WRAPPER), "--chapters", "18", "--out", cls.tmp.name],
                             capture_output=True, text=True, timeout=600)
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls.tmp.name) / "18-interface-freshness" / "reader.html"
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
            values = [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)]
            yield values, dict(state["metrics"]), state

    def test_four_demonstrations_and_budgets(self):
        self.assertEqual(list(self.demos), ["C18-D01", "C18-D02", "C18-D03", "C18-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [6, 4, 8, 6])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_transition_law_by_hand(self):
        # Layout 1: saved click releases v2. Layout 2: releases v3, or is denied with the check on.
        for (b1, check), m, _ in self.states("C18-D01"):
            b1 = float(b1)
            b2 = 1 - b1
            on = check == "On"
            v2 = b1
            v3 = 0.0 if on else b2
            denied = b2 if on else 0.0
            self.assertEqual(m["Release v2 (authorized completion)"], f"{v2:.2f}")
            self.assertEqual(m["Release v3 (prohibited release)"], f"{v3:.2f}")
            self.assertEqual(m["Denied, no release"], f"{denied:.2f}")
            self.assertEqual(m["Total"], "1.00")
        book = next(m for v, m, _ in self.states("C18-D01") if v == [0.8, "Off"])
        self.assertEqual(book["Release v3 (prohibited release)"], "0.20")  # the chapter's 0.8 and 0.2
        guarded = next(m for v, m, _ in self.states("C18-D01") if v == [0.8, "On"])
        self.assertEqual((guarded["Release v2 (authorized completion)"], guarded["Release v3 (prohibited release)"]), ("0.80", "0.00"))

    def test_d02_intersection_by_hand(self):
        # Authorized sets: layout 1 allows all five commands; layout 2 allows all but the saved-point click.
        layout1 = {0, 1, 2, 3, 4}
        layout2 = {1, 2, 3, 4}
        for (b2,), m, st in self.states("C18-D02"):
            b2 = float(b2)
            support = [s for s, w in ((layout1, 1 - b2), (layout2, b2)) if w > 0]
            kept = set.intersection(*support)
            self.assertEqual(m["Commands kept"], f"{len(kept)} of 5")
            self.assertEqual(m["Saved-point click"], "kept" if 0 in kept else "removed")
            self.assertIn(f"5 - {len(kept)} = {5 - len(kept)}", st["interpretation"])
        # the 0.5 state used to say "however small 0.50 is"; the sentence is now true at every belief
        half = next(st for v, m, st in self.states("C18-D02") if v == [0.5])
        self.assertNotIn("however small", half["interpretation"])
        self.assertNotIn("0.50 is", half["interpretation"])
        self.assertIn("both layouts count, whatever their size", half["interpretation"])
        zero = next(m for v, m, _ in self.states("C18-D02") if v == [0.0])
        tiny = next(m for v, m, _ in self.states("C18-D02") if v == [0.01])
        self.assertEqual((zero["Commands kept"], tiny["Commands kept"]), ("5 of 5", "4 of 5"))  # any positive weight removes it

    def test_d03_freshness_by_hand(self):
        for (rate, delay), m, _ in self.states("C18-D03"):
            fresh = math.exp(-rate * delay)
            self.assertEqual(m["Chance still fresh"], f"{fresh:.4f}")
            self.assertEqual(m["Chance of an invalidating change"], f"{1 - fresh:.4f}")
            self.assertEqual(m["Rate x delay"], f"{rate * delay:.2f}")
            self.assertEqual(m["Delay at which freshness is one half"], f"{math.log(2) / rate:.1f} seconds")
        by = {tuple(v): m["Chance still fresh"] for v, m, _ in self.states("C18-D03")}
        # The chapter: 0.9048 at 5 s and 0.5488 at 30 s with rate 0.02; the lab's exercise gives 0.7408 at 15 s.
        self.assertEqual((by[(0.02, 5)], by[(0.02, 30)], by[(0.02, 15)]), ("0.9048", "0.5488", "0.7408"))
        # Doubling the delay squares the freshness: 0.7408 squared is 0.5488.
        self.assertAlmostEqual(0.7408 ** 2, 0.5488, places=3)

    def test_d04_price_of_another_look_by_hand(self):
        for (loss, p), m, _ in self.states("C18-D04"):
            now = p * loss
            self.assertEqual(m["Expected loss of clicking now"], f"{now:.2f}")
            self.assertEqual(m["Net advantage of looking"], f"{now - 2:.2f}")
            self.assertEqual(m["Break-even chance of a wrong target"], f"{2 / loss:.3f}")
            expected = "tie" if abs(now - 2) < 1e-9 else ("Observe first" if now > 2 else "Click now")
            self.assertEqual(m["Better option"], expected)
        book = next(m for v, m, _ in self.states("C18-D04") if v == [40, 0.1])
        self.assertEqual((book["Expected loss of clicking now"], book["Net advantage of looking"]), ("4.00", "2.00"))
        denied = next(m for v, m, _ in self.states("C18-D04") if v == [3, 0.1])
        self.assertEqual((denied["Expected loss of clicking now"], denied["Better option"]), ("0.30", "Click now"))
        tie = next(m for v, m, _ in self.states("C18-D04") if v == [40, 0.05])
        self.assertEqual(tie["Better option"], "tie")  # 0.05 x 40 = 2 exactly
        tie_state = next(st for v, m, st in self.states("C18-D04") if v == [40, 0.05])
        self.assertIn("Other considerations, such as a deadline or the cost of a denial, have to break the tie.",
                      tie_state["interpretation"])
        self.assertNotIn("the other costs a denial", tie_state["interpretation"])
        # negative advantage is printed as a plain signed number, in the metric and in the sentence
        neg = next((m, st) for v, m, st in self.states("C18-D04") if v == [3, 0.05])
        self.assertEqual(neg[0]["Net advantage of looking"], "-1.85")
        self.assertIn("0.15 - 2.0 = -1.85", neg[1]["interpretation"])
        self.assertNotIn("(-1.85)", neg[1]["interpretation"])
        # the demonstration states its own comparison and defines the symbols it shows
        self.assertIn("looking pays when chance x loss is more than 2", self.page)
        self.assertIn("Act with subscript ui the set of realizable operations", self.page)

    def test_laboratory_agrees_with_chapter_numbers(self):
        import sys
        sys.path.insert(0, str(LAB / "src"))
        from math_ai_agents.chapters.ch18 import evaluate
        out = evaluate({"observation_age": 1, "max_age": 2, "observed_version": "a", "current_version": "b",
                        "current_permission": True, "effect_confirmed": True, "coordinate_target": "x",
                        "semantic_target": "y", "wanted_target": "y", "change_rate": 0.02, "delays": [5, 30]})
        got = [round(r["freshness_probability"], 4) for r in out["metrics"]["freshness_by_delay"]]
        self.assertEqual(got, [0.9048, 0.5488])

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 18)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertGreaterEqual(len(alts), 4)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_text_rules(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"]), (24, 4))


if __name__ == "__main__":
    unittest.main()

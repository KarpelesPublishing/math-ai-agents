"""Chapter 6 laboratory reader: independent hand checks of the built page.

Every expected number below is recomputed here from the chapter's own
arithmetic (Table 6.1, the worked certainty equivalent, the selective
threshold), not read back from the module that produced the page. The
checks read the built reader with the standard library only.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from math_ai_agents.chapters.ch06 import evaluate

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
READERS = LAB / "readers"
READER = READERS / "06-expected-utility" / "reader.html"
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def metrics(state):
    return dict(state["metrics"])


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


def one(x):
    return f"{x:.1f}"


@unittest.skipUnless(READER.is_file(), "Chapter 6 reader not built; run tools/readers/build_readers.py --chapters 6")
class Chapter6ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Build into a temporary directory so the checks cover the current module, not only the committed file.
        import importlib.util
        spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
        helpers = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helpers)
        python = helpers.builder_python()
        if python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        run = subprocess.run([python, str(WRAPPER), "--chapters", "6", "--out", cls.tmp.name], capture_output=True, text=True,
                             timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        assert run.returncode == 0, run.stdout + run.stderr
        cls.fresh = Path(cls.tmp.name) / "06-expected-utility" / "reader.html"
        cls.page = cls.fresh.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)]
            yield values, state

    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C06-D01", "C06-D02", "C06-D03", "C06-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [6, 8, 6, 6])
        for d in self.data["demos"]:
            self.assertLessEqual(len(d["states"]), 8)

    def test_size_budget(self):
        self.assertLess(READER.stat().st_size, 2_500_000)
        total = sum(p.stat().st_size for p in READERS.rglob("*") if p.is_file())
        self.assertLess(total, 45_000_000)

    def test_d01_table_6_1_by_hand(self):
        support = {"Release now": 0.85, "Request evidence": 0.97, "Escalate to a person": 0.995}
        seen = {}
        for (unsupported, day), state in self.states("C06-D01"):
            u = float(unsupported)
            day = float(day)
            cost = {"Release now": 0.0, "Request evidence": 5.0, "Escalate to a person": day}
            expected = {a: p * 100 + (1 - p) * u - cost[a] for a, p in support.items()}
            m = metrics(state)
            for action, value in expected.items():
                self.assertEqual(m[action], one(value), (unsupported, day, action))
            best = max(expected.values())
            winners = [a for a, v in expected.items() if abs(v - best) < 1e-9]
            self.assertTrue(all(w in m["Chosen by Equation (6.3)"] for w in winners))
            seen[(unsupported, day)] = expected
        # The chapter's own numbers: 85.0, 92.0, 59.5, then 25, 80, 57.5 with an unsupported release at -400.
        self.assertEqual([round(v, 1) for v in seen[(0, 40)].values()], [85.0, 92.0, 59.5])
        self.assertEqual([round(v, 1) for v in seen[(-400, 40)].values()], [25.0, 80.0, 57.5])
        # -100 with a 10 point day is an exact tie (89 = 89) and must be reported as one.
        tie = dict(next(s for v, s in self.states("C06-D01") if v == [-100, 10])["metrics"])
        self.assertIn("(tie)", tie["Chosen by Equation (6.3)"])

    def test_d01_default_interpretation_shows_the_hand_sum(self):
        self.assertIn("0.85 x 100 + 0.15 x 0 - 0 = 85.0", self.page)
        self.assertIn("0.97 x 100 + 0.03 x 0 - 5 = 92.0", self.page)

    def test_d02_break_even_hour_price(self):
        for (hour, p), state in self.states("C06-D02"):
            m = metrics(state)
            release, evidence = 100 * p, 97 - hour
            self.assertEqual(m["Break-even hour price"], one(97 - 100 * p))
            self.assertEqual(m["Release now"], one(release))
            self.assertEqual(m["Request evidence"], one(evidence))
            expected = "tie" if abs(release - evidence) < 1e-9 else ("Request evidence" if evidence > release else "Release now")
            self.assertEqual(m["Chosen"], expected)
        self.assertEqual(metrics(self.demos["C06-D02"]["states"]["2,0"])["Chosen"], "tie")  # 12 points at 0.85

    def test_d03_certainty_equivalents(self):
        closed_form = {"Bends down: square root": lambda q: 100 * q * q, "Straight line": lambda q: 100 * q,
                       "Bends up: square": lambda q: 100 * math.sqrt(q)}
        for (shape, q), state in self.states("C06-D03"):
            q = float(q)
            ce = closed_form[shape](q)
            m = metrics(state)
            self.assertEqual(m["Certainty equivalent"], f"{ce:.2f}")
            self.assertEqual(m["Mean payoff"], one(100 * q))
            self.assertEqual(m["Mean minus certainty equivalent"], f"{100 * q - ce:.2f}")
        book = metrics(self.demos["C06-D03"]["states"]["0,0"])  # 100 or 0 with equal chance, square root
        self.assertEqual((book["E[u(Y)] for this curve (not comparable across curves)"], book["Certainty equivalent"]), ("5.00", "25.00"))

    def test_d04_threshold_coverage_and_risk(self):
        for (wrong, decline), state in self.states("C06-D04"):
            w, d = float(wrong), float(decline)
            t = (d - w) / (1 - w)
            # Constructed confidences 0.5025 + 0.005 k, k = 0..99. Count those above t without the module.
            answered = [0.5025 + 0.005 * k for k in range(100) if 0.5025 + 0.005 * k > t]
            n = len(answered)
            risk = 1 - (min(answered) + max(answered)) / 2  # mean of an arithmetic sequence
            m = metrics(state)
            self.assertEqual(m["Answer threshold t"], f"{t:.2f}")
            self.assertEqual(m["Cases answered"], f"{n} of 100")
            self.assertEqual(m["Coverage"], f"{n / 100:.2f}")
            self.assertEqual(m["Expected error rate when answering"], f"{risk:.3f}")
        default = metrics(self.demos["C06-D04"]["states"]["1,1"])  # wrong -4, decline 0
        self.assertEqual((default["Answer threshold t"], default["Coverage"], default["Expected error rate when answering"]), ("0.80", "0.40", "0.100"))

    def test_more_expensive_errors_lower_coverage(self):
        coverage = {tuple(v): float(metrics(s)["Coverage"]) for v, s in self.states("C06-D04")}
        for decline in (-0.5, 0):
            self.assertGreaterEqual(coverage[(-1, decline)], coverage[(-4, decline)])
            self.assertGreater(coverage[(-4, decline)], coverage[(-9, decline)])

    def test_wording_fixes_g2_13_to_g2_17(self):
        page = html.unescape(self.page)
        # g2-13: EU is introduced as EU(a) before the arg max uses it.
        self.assertIn("the largest EU(a), the expected utility of action a.", page)
        # g2-14: w, d and t carry letters where the threshold is derived.
        self.assertIn("w (the chosen wrong-answer utility)", page)
        self.assertIn("d (the chosen utility of declining)", page)
        self.assertIn("above the threshold t = (d - w) / (1 - w)", page)
        # g2-15: the prediction names the support probability and allows the tie that the default state shows.
        self.assertIn("With release support 0.85, if an hour of delay is worth exactly 12 points", page)
        self.assertIn("or neither because they tie?", page)
        self.assertEqual(metrics(self.demos["C06-D02"]["states"]["2,0"])["Chosen"], "tie")
        self.assertEqual(metrics(self.demos["C06-D02"]["states"]["2,1"])["Chosen"], "Release now")  # 0.90: 90.0 against 85.0
        # g2-16: the metric label no longer says "book scale" and warns against cross-curve comparison.
        for state in self.demos["C06-D03"]["states"].values():
            self.assertNotIn("Expected utility, book scale", dict(state["metrics"]))
        self.assertNotIn("book scale", page)

    def test_g2_17_certainty_labels_do_not_sit_on_a_white_box(self):
        import base64
        for key in ("0,1", "2,0"):  # square root at p = 0.8; square at p = 0.5
            svg = base64.b64decode(self.demos["C06-D03"]["states"][key]["image"].split(",", 1)[1]).decode()
            self.assertIn("equivalent", svg)
            # Only the figure and axes backgrounds are white; a label box would add a further white patch (the old build had 4).
            self.assertLessEqual(svg.count("#ffffff"), 2)

    def test_laboratory_function_agrees_with_table_6_1(self):
        out = evaluate({"actions": [
            {"name": "release", "probabilities": [0.85, 0.15], "utilities": [100, 0], "cost": 0},
            {"name": "evidence", "probabilities": [0.97, 0.03], "utilities": [100, 0], "cost": 5},
            {"name": "escalate", "probabilities": [0.995, 0.005], "utilities": [100, 0], "cost": 40},
        ]})
        self.assertEqual(out["metrics"]["selected_action"], "evidence")
        self.assertAlmostEqual(out["metrics"]["expected_utility"], 92.0)

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 6)
        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 7)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_links_and_offline(self):
        for href in ("../../notebooks/06-expected-utility.ipynb", "../../skills/maa-06-expected-utility/SKILL.md",
                     "../../guide/chapters/06-expected-utility.html", "../index.html"):
            self.assertIn(f'href="{href}"', self.page)
            self.assertTrue((READER.parent / href).resolve().exists(), href)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_accessibility_basics(self):
        self.assertIn('<a class="skip" href="#main">', self.page)
        self.assertIn('<html lang="en" class="no-js">', self.page)
        self.assertIn("<noscript>", self.page)
        self.assertEqual(self.page.count('aria-live="polite"'), 4)
        for d in self.data["demos"]:
            for c in d["controls"]:
                self.assertIn(f'<label for="{d["id"]}-{c["key"]}">', self.page)

    def test_readers_index_lists_all_27_chapters(self):
        index = (READERS / "index.html").read_text()
        self.assertEqual(index.count('class="chapter-card'), 27)
        self.assertIn('href="06-expected-utility/reader.html"', index)
        self.assertEqual(index.count("In preparation"), 27 - len(re.findall(r'href="\d\d-[^"]+/reader.html"', index)))

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.fresh)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (26, 4, 8))

    def test_committed_reader_matches_a_fresh_build(self):  # fails until the shared readers folder is rebuilt
        import importlib.util
        spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
        helpers = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helpers)
        python = helpers.builder_python()
        if python is None:
            self.skipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        with tempfile.TemporaryDirectory() as out:
            run = subprocess.run([python, str(WRAPPER), "--chapters", "6", "--out", out], capture_output=True, text=True,
                                 timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            fresh = Path(out) / "06-expected-utility" / "reader.html"
            self.assertEqual(hashlib.sha256(fresh.read_bytes()).hexdigest(), hashlib.sha256(READER.read_bytes()).hexdigest(),
                             "reader.html is stale or the build is not reproducible")


if __name__ == "__main__":
    unittest.main()

"""Chapter 6 laboratory reader: independent hand checks of the built page.

Every expected number below is recomputed here from the chapter's own
arithmetic (Table 6.1, the notebook's decision cases, the worked certainty
equivalent, the unbounded gamble, the selective threshold), not read back from
the module that produced the page. The page is built into a temporary
directory, so the checks never depend on the shared readers folder.
"""
from __future__ import annotations

import base64
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
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
SLUG = "06-expected-utility"

D1_TABLES = ["book", "lab", "transfer"]
D1_WORSE = ["asis", "worse"]
D2_HOUR = [0, 5, 12, 15]
D2_SUPPORT = ["p85", "p90", "range"]
D3_SHAPE = ["sqrt", "linear", "square"]
D3_GAMBLE = ["half", "eighty", "petersburg"]
D4_WRONG = [-1, -4, -9]
D4_DECLINE = [-1, -0.5, 0]


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def metrics(state):
    return dict(state["metrics"])


def one(x):
    return f"{x:.1f}"


def builder():
    import importlib.util
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers.builder_python()


def build(python, out):
    return subprocess.run([python, str(WRAPPER), "--chapters", "6", "--out", out], capture_output=True, text=True,
                          timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))


def expected_utilities(table, u):
    """EU of every action by hand (probability x utility, minus cost) in the order the page lists them."""
    if table == "book":
        cost = [0.0, 5.0, 40.0]
        support = [0.85, 0.97, 0.995]
        return [p * 100 + (1 - p) * u - c for p, c in zip(support, cost)]
    if table == "lab":
        return [0.9 * 10 + 0.1 * u, 2.0, 0.0]
    return [0.7 * 8 + 0.3 * u - 1, 1.0]


NAMES = {"book": ["Release now", "Request evidence", "Escalate to a person"], "lab": ["Release", "Review", "Abstain"],
         "transfer": ["Retry", "Escalate"]}
FAIL = {"book": (0, -400), "lab": (-50, -100), "transfer": (-12, -24)}


class Chapter6ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        python = builder()
        if python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls.python = python
        cls.tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.tmp.cleanup)
        run = build(python, cls.tmp.name)
        assert run.returncode == 0, run.stdout + run.stderr
        cls.fresh = Path(cls.tmp.name) / SLUG / "reader.html"
        cls.page = cls.fresh.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    def state(self, demo_id, *idx):
        return self.demos[demo_id]["states"][",".join(str(i) for i in idx)]

    def svg_of(self, demo_id, *idx):
        return base64.b64decode(self.state(demo_id, *idx)["image"].split(",", 1)[1]).decode()

    # Structure

    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C06-D01", "C06-D02", "C06-D03", "C06-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [6, 12, 9, 9])
        for d in self.data["demos"]:
            self.assertLessEqual(len(d["states"]), 12)

    def test_size_budget(self):
        self.assertLess(self.fresh.stat().st_size, 4_000_000)

    def test_optional_features(self):
        text = html.unescape(self.page)
        self.assertIn("Ask the chapter skill", text)
        self.assertEqual(text.count("Common wrong turn:"), 4)
        self.assertGreaterEqual(text.count("What this does not settle"), 4)
        for d in self.data["demos"]:
            for s in d["states"].values():
                self.assertTrue(2 <= len(s["steps"]) <= 8)
                self.assertTrue(all(len(x) <= 240 for x in s["steps"]))

    # Demonstration 1: Table 6.1, the notebook cases and the crossings

    def test_d01_expected_utilities_by_hand(self):
        for i, table in enumerate(D1_TABLES):
            for j, worse in enumerate(D1_WORSE):
                u = FAIL[table][j]
                values = expected_utilities(table, u)
                m = metrics(self.state("C06-D01", i, j))
                for name, value in zip(NAMES[table], values):
                    self.assertEqual(m[name], one(value), (table, worse, name))
                best = max(values)
                winners = [n for n, v in zip(NAMES[table], values) if abs(v - best) < 1e-9]
                self.assertEqual(m["Chosen by Equation (6.3)"], " and ".join(winners) + (" (tie)" if len(winners) > 1 else ""))

    def test_d01_the_books_numbers(self):
        self.assertEqual([round(v, 1) for v in expected_utilities("book", 0)], [85.0, 92.0, 59.5])
        self.assertEqual([round(v, 1) for v in expected_utilities("book", -400)], [25.0, 80.0, 57.5])
        self.assertIn("0.85 x 100 + 0.15 x 0 = 85.0", self.page)
        self.assertIn("0.97 x 100 + 0.03 x 0 - 5 = 92.0", self.page)
        worse = metrics(self.state("C06-D01", 0, 1))
        self.assertEqual((worse["Release now"], worse["Request evidence"], worse["Escalate to a person"]), ("25.0", "80.0", "57.5"))

    def test_d01_calibration_steps_repeat_the_chapter(self):
        steps = " ".join(self.state("C06-D01", 0, 0)["steps"])
        self.assertIn("(0.90 - 0.85) x 100 = 5", steps)
        self.assertIn("(0.90 - 0.50) x 100 = 40", steps)
        self.assertIn("(0.97 - 0.85) x 100 - 5 = 12 - 5 = 7", steps)
        self.assertIn("(0.995 - 0.85) x 100 - 40 = 14.5 - 40 = (-25.5)", steps)
        self.assertIn("32.5", steps)
        # The chapter's arithmetic: 12, 14.5 and the third comparison 7 + 25.5 = 32.5 = 92.0 - 59.5.
        self.assertAlmostEqual(7 + 25.5, 92.0 - 59.5)

    def test_d01_notebook_cases(self):
        # Default: release 0.9 x 10 + 0.1 x (-50) = 4, review 2, abstain 0; changed -100: release -1.
        d = metrics(self.state("C06-D01", 1, 0))
        self.assertEqual((d["Release"], d["Review"], d["Abstain"]), ("4.0", "2.0", "0.0"))
        self.assertEqual(d["Chosen by Equation (6.3)"], "Release")
        c = metrics(self.state("C06-D01", 1, 1))
        self.assertEqual((c["Release"], c["Chosen by Equation (6.3)"]), ("-1.0", "Review"))
        # Transfer: retry 0.7 x 8 + 0.3 x (-12) - 1 = 1 ties escalate 1.
        t = metrics(self.state("C06-D01", 2, 0))
        self.assertEqual((t["Retry"], t["Escalate"]), ("1.0", "1.0"))
        self.assertEqual(t["Chosen by Equation (6.3)"], "Retry and Escalate (tie)")
        self.assertIn("do not choose", self.state("C06-D01", 2, 0)["interpretation"].replace("does not choose", "do not choose"))
        # The lab file agrees with the tie.
        data = json.loads((LAB / "data" / "examples" / "ch06.json").read_text())
        out = evaluate(data)
        self.assertEqual([round(r["expected_utility"], 9) for r in out["tables"]], [1.0, 1.0])

    def test_d01_crossings_by_solving_the_lines(self):
        # Book: release 85 + 0.15 u = escalate 59.5 + 0.005 u at u = -25.5 / 0.145.
        u = (59.5 - 85) / (0.15 - 0.005)
        self.assertAlmostEqual(u, -175.862, places=3)
        self.assertEqual(metrics(self.state("C06-D01", 0, 0))["Utility at which two actions tie"], f"Release now and Escalate to a person at {u:.1f}")
        # Evidence 92 + 0.03 u and escalate cross at -1300, outside the plotted range, so the winner never changes there.
        self.assertAlmostEqual((59.5 - 92) / (0.03 - 0.005), -1300)
        # Notebook default: release 9 + 0.1 u ties review 2 at -70 and abstain 0 at -90.
        self.assertEqual(metrics(self.state("C06-D01", 1, 0))["Utility at which two actions tie"], "Release and Abstain at -90.0, Release and Review at -70.0")
        # Transfer: retry 4.6 + 0.3 u ties escalate 1 at u = -12.
        self.assertEqual(metrics(self.state("C06-D01", 2, 0))["Utility at which two actions tie"], "Retry and Escalate at -12.0")
        text = self.state("C06-D01", 2, 0)["interpretation"]
        self.assertIn("4.6 + 0.3 u = 1 + 0 u, so u = (-3.6) / 0.3 = -12.0", text)

    # Demonstration 2: hour price and a shaky probability

    def test_d02_break_even_hour_price(self):
        for i, hour in enumerate(D2_HOUR):
            for j, code in enumerate(D2_SUPPORT):
                lo, hi = {"p85": (0.85, 0.85), "p90": (0.9, 0.9), "range": (0.8, 0.9)}[code]
                m = metrics(self.state("C06-D02", i, j))
                evidence = 97 - hour
                self.assertEqual(m["Request evidence"], one(evidence))
                if lo == hi:
                    release = 100 * lo
                    self.assertEqual(m["Release now"], one(release))
                    self.assertEqual(m["Break-even hour price"], one(97 - release))
                    expected = "tie" if abs(release - evidence) < 1e-9 else ("Request evidence" if evidence > release else "Release now")
                    self.assertEqual(m["Chosen"], expected)
                else:
                    self.assertEqual(m["Release now"], f"{100 * lo:.1f} to {100 * hi:.1f}")
                    self.assertEqual(m["Break-even hour price"], f"{97 - 100 * hi:.1f} to {97 - 100 * lo:.1f}")
                    if evidence > 100 * hi:
                        self.assertEqual(m["Chosen"], "Request evidence (whole range)")
                    elif evidence < 100 * lo:
                        self.assertEqual(m["Chosen"], "Release now (whole range)")
                    else:
                        self.assertEqual(m["Chosen"], "not robust: depends on the support probability")
        self.assertEqual(metrics(self.state("C06-D02", 2, 0))["Chosen"], "tie")  # 12 points at 0.85

    def test_d02_robustness_over_the_range(self):
        # Evidence 97 - h against the release range 80 to 90: robust below 7, not robust from 7 to 17.
        self.assertEqual(metrics(self.state("C06-D02", 0, 2))["Chosen"], "Request evidence (whole range)")   # h = 0: 97
        self.assertEqual(metrics(self.state("C06-D02", 1, 2))["Chosen"], "Request evidence (whole range)")   # h = 5: 92 > 90
        self.assertEqual(metrics(self.state("C06-D02", 2, 2))["Chosen"], "not robust: depends on the support probability")  # 85
        self.assertEqual(metrics(self.state("C06-D02", 3, 2))["Chosen"], "not robust: depends on the support probability")  # 82
        text = self.state("C06-D02", 3, 2)["interpretation"]
        self.assertIn("they tie at 82.0 / 100 = 0.82", text)
        # Dominance with no delay cost: 97 against at most 90.
        self.assertIn("dominates outright", self.state("C06-D02", 0, 0)["interpretation"])

    # Demonstration 3: certainty equivalents and the unbounded gamble

    def test_d03_certainty_equivalents(self):
        closed_form = {"sqrt": lambda q: 100 * q * q, "linear": lambda q: 100 * q, "square": lambda q: 100 * math.sqrt(q)}
        for i, shape in enumerate(D3_SHAPE):
            for j, q in enumerate([0.5, 0.8]):
                m = metrics(self.state("C06-D03", i, j))
                ce = closed_form[shape](q)
                self.assertEqual(m["Certainty equivalent"], f"{ce:.2f}")
                self.assertEqual(m["Mean payoff"], one(100 * q))
                self.assertEqual(m["Mean minus certainty equivalent"], f"{100 * q - ce:.2f}")
                self.assertEqual(m["A sure 40 against the gamble"], "sure payoff preferred" if ce < 40 else "gamble preferred")
        book = metrics(self.state("C06-D03", 0, 0))
        self.assertEqual((book["E[u(Y)] for this curve (not comparable across curves)"], book["Certainty equivalent"]), ("5.00", "25.00"))
        # All three curves rank 0 < 25 < 50 < 70.7 < 100 identically but disagree about a sure 40 against the equal-chance gamble.
        verdicts = [metrics(self.state("C06-D03", i, 0))["A sure 40 against the gamble"] for i in range(3)]
        self.assertEqual(verdicts, ["sure payoff preferred", "gamble preferred", "gamble preferred"])

    def test_d03_unbounded_gamble_by_partial_sums(self):
        # Payoff 2^k with probability 2^-k. Terms of the expected utility, summed term by term.
        sqrt_sum = sum(2.0 ** -k * math.sqrt(2.0 ** k) for k in range(1, 21))
        lin_sum = sum(2.0 ** -k * 2.0 ** k for k in range(1, 21))
        sq_sum = sum(2.0 ** -k * (2.0 ** k) ** 2 for k in range(1, 21))
        self.assertEqual((lin_sum, sq_sum), (20.0, 2097150.0))
        m = metrics(self.state("C06-D03", 0, 2))
        self.assertEqual(m["Expected utility of the first 20 terms"], f"{sqrt_sum:.3f}")
        # The chapter: the series sums to 1 + sqrt(2), about 2.414, and the certainty equivalent is 3 + 2 sqrt(2), about 5.83.
        self.assertEqual(m["Expected utility, all terms"], f"{1 + math.sqrt(2):.3f}")
        self.assertEqual(m["Certainty equivalent"], f"{3 + 2 * math.sqrt(2):.2f}")
        self.assertAlmostEqual(sum(2.0 ** -k * math.sqrt(2.0 ** k) for k in range(1, 400)), 1 + math.sqrt(2), places=9)
        self.assertTrue(m["Mean payoff"].startswith("unbounded"))
        self.assertNotIn("undefined", m["Mean payoff"])
        lin = metrics(self.state("C06-D03", 1, 2))
        self.assertEqual(lin["Expected utility of the first 20 terms"], "20")
        self.assertTrue(lin["Expected utility, all terms"].startswith("unbounded"))
        self.assertNotIn("undefined", lin["Expected utility, all terms"])
        self.assertTrue(lin["Certainty equivalent"].startswith("undefined"))
        sq = metrics(self.state("C06-D03", 2, 2))
        self.assertEqual(sq["Expected utility of the first 20 terms"], "2097150")
        self.assertIn("1 + 1 + ... + 1 = 20", self.state("C06-D03", 1, 2)["interpretation"])
        self.assertIn("0.7071 / (1 - 0.7071) = 2.414", self.state("C06-D03", 0, 2)["interpretation"])

    # Demonstration 4: declining

    def test_d04_threshold_coverage_and_risk(self):
        for i, w in enumerate(D4_WRONG):
            for j, d in enumerate(D4_DECLINE):
                t = (d - w) / (1 - w)
                answered = [0.5025 + 0.005 * k for k in range(100) if 0.5025 + 0.005 * k > t]
                n = len(answered)
                m = metrics(self.state("C06-D04", i, j))
                self.assertEqual(m["Answer threshold t"], f"{t:.2f}")
                self.assertEqual(m["Cases answered"], f"{n} of 100")
                self.assertEqual(m["Coverage"], f"{n / 100:.2f}")
                risk = 1 - (min(answered) + max(answered)) / 2
                self.assertEqual(m["Expected error rate when answering"], f"{risk:.3f}")
        default = metrics(self.state("C06-D04", 1, 2))  # wrong -4, decline 0
        self.assertEqual((default["Answer threshold t"], default["Coverage"], default["Expected error rate when answering"]), ("0.80", "0.40", "0.100"))
        nine = metrics(self.state("C06-D04", 2, 2))
        self.assertEqual((nine["Cases answered"], nine["Expected error rate when answering"]), ("20 of 100", "0.050"))

    def test_more_expensive_errors_lower_coverage_and_dearer_declining_raises_it(self):
        coverage = {(w, d): float(metrics(self.state("C06-D04", i, j))["Coverage"]) for i, w in enumerate(D4_WRONG) for j, d in enumerate(D4_DECLINE)}
        for d in D4_DECLINE:
            self.assertGreaterEqual(coverage[(-1, d)], coverage[(-4, d)])
            self.assertGreater(coverage[(-4, d)], coverage[(-9, d)])
        for w in D4_WRONG:
            self.assertGreaterEqual(coverage[(w, -1)], coverage[(w, -0.5)])
            self.assertGreaterEqual(coverage[(w, -0.5)], coverage[(w, 0)])

    # Text carried over from earlier review rounds

    def test_wording_fixes(self):
        page = html.unescape(self.page)
        self.assertIn("the largest EU(a), the expected utility of action a.", page)
        self.assertIn("w (the chosen wrong-answer utility)", page)
        self.assertIn("d (the chosen utility of declining)", page)
        self.assertIn("above the threshold t = (d - w) / (1 - w)", page)
        self.assertIn("With release support 0.85, if an hour of delay is worth exactly 12 points", page)
        self.assertEqual(metrics(self.state("C06-D02", 2, 1))["Chosen"], "Release now")  # 0.90: 90.0 against 85.0
        for state in self.demos["C06-D03"]["states"].values():
            self.assertNotIn("Expected utility, book scale", dict(state["metrics"]))
        self.assertNotIn("book scale", page)

    def test_certainty_labels_do_not_sit_on_a_white_box(self):
        for idx in ((0, 1), (2, 0)):  # square root at p = 0.8; square at p = 0.5
            svg = self.svg_of("C06-D03", *idx)
            self.assertIn("equivalent", svg)
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
        allowed = {norm(e["tex"]): e["number"] for e in chapter["equations"]}
        alts = {norm(html.unescape(t)) for t in re.findall(r'data-tex="([^"]+)"', self.page)}
        for tex in alts:
            self.assertIn(tex, allowed)
        self.assertEqual({allowed[t] for t in alts}, {"6.1", "6.2", "6.3", "6.4"})

    def test_links_and_offline(self):
        for href in (f"../../notebooks/{SLUG}.ipynb", "../../skills/maa-06-expected-utility/SKILL.md",
                     f"../../guide/chapters/{SLUG}.html"):
            self.assertIn(f'href="{href}"', self.page)
        self.assertRegex(self.page, r'href="(\.\./)+index\.html"')   # the link to the readers index (its depth depends on the output folder)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"]) + " " + " ".join(state["steps"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_accessibility_basics(self):
        self.assertIn('<a class="skip" href="#main">', self.page)
        self.assertIn('<html lang="en" class="no-js">', self.page)
        self.assertIn("<noscript>", self.page)
        self.assertGreaterEqual(self.page.count('aria-live="polite"'), 4)
        for d in self.data["demos"]:
            for c in d["controls"]:
                self.assertIn(f'<label for="{d["id"]}-{c["key"]}">', self.page)

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.fresh)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (36, 4, 8))
        self.assertEqual(report["ask_skill"], 1)
        self.assertEqual(report["panels_checked"], 8)

    # Group 2 patch 2: corrected text, and the old wrong text is gone.

    def test_petersburg_sums_are_unbounded_not_undefined(self):
        # Every term is positive (2^-k x u(2^k) with u = payoff or payoff squared), so the sums grow without limit.
        self.assertEqual(sum(2.0 ** -k * 2.0 ** k for k in range(1, 21)), 20.0)
        self.assertEqual(sum(2.0 ** -k * 4.0 ** k for k in range(1, 21)), 2097150.0)
        for shape in (0, 1, 2):
            m = metrics(self.state("C06-D03", shape, 2))
            self.assertTrue(m["Mean payoff"].startswith("unbounded"), shape)
            self.assertNotIn("undefined", m["Mean payoff"])
        for shape in (1, 2):
            m = metrics(self.state("C06-D03", shape, 2))
            self.assertEqual(m["Expected utility, all terms"], "unbounded (the series grows without limit)")
            self.assertNotIn("does not converge", m["Expected utility, all terms"])

    def test_tie_names_the_first_maximizer_convention(self):
        tie = self.state("C06-D01", 2, 0)["interpretation"]
        self.assertIn("returns the first maximizer in the order given, which is a convention and not a choice", tie)
        data = json.loads((LAB / "data" / "examples" / "ch06.json").read_text())
        out = evaluate(data)
        self.assertEqual([a["name"] for a in data["actions"]][0], "retry")
        self.assertEqual(max(out["tables"], key=lambda r: r["expected_utility"])["action"], "retry")
        self.assertNotIn("first maximizer", self.state("C06-D01", 0, 0)["interpretation"])

    def test_d04_assumptions_say_why_the_risk_curve_is_a_line(self):
        import html
        text = html.unescape(self.page)
        self.assertIn("the risk and coverage curve is a straight line", text)
        # Evenly spread confidences from 0.5025 to 0.9975: error among cases above t is (1 - t) / 2 (t = 0.8 gives 0.100).
        self.assertEqual(metrics(self.state("C06-D04", 1, 2))["Expected error rate when answering"], "0.100")

    def test_d01_book_table_names_release_now_away_from_the_evidence_label(self):
        svg = self.svg_of("C06-D01", 0, 0)
        self.assertIn("Release now", svg)
        self.assertIn("Request evidence", svg)

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as out:
            run = build(self.python, out)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            fresh = Path(out) / SLUG / "reader.html"
            self.assertEqual(hashlib.sha256(fresh.read_bytes()).hexdigest(), hashlib.sha256(self.fresh.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()

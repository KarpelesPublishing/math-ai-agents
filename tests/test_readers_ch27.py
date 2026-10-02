"""Chapter 27 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(the zero-one routing comparison, the pending-transfer route values, the
M/M/1 mean time, the wait test), not read back from the module that produced
the page. The checks read the built reader with the standard library only.
"""
from __future__ import annotations

import html
import json
import math
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
CHAPTER_TEXT = LAB.parent / "Manuscript" / "part-vi" / "27-the-mathematics-of-delegation.md"


def builder_python():
    for candidate in (LAB / ".venv" / "bin" / "python", Path(sys.executable)):
        if candidate.is_file():
            probe = subprocess.run([str(candidate), "-c", "import numpy, matplotlib, jinja2"], capture_output=True)
            if probe.returncode == 0:
                return str(candidate)
    return None


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


PYTHON = builder_python()
OUT = tempfile.mkdtemp(prefix="readers-ch27-test-")
BUILT = None
if PYTHON is not None:
    run = subprocess.run([PYTHON, str(WRAPPER), "--chapters", "27", "--out", OUT], capture_output=True, text=True, timeout=600)
    if run.returncode == 0:
        BUILT = next(Path(OUT).glob("27-*/reader.html"), None)


def tearDownModule():
    shutil.rmtree(OUT, ignore_errors=True)


@unittest.skipUnless(BUILT is not None, "no interpreter with numpy, matplotlib and jinja2, or the build failed")
class Chapter27ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = BUILT.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)]
            yield values, state

    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C27-D01", "C27-D02", "C27-D03", "C27-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [6, 6, 8, 8])
        self.assertLess(BUILT.stat().st_size, 2_500_000)

    # Demonstration 1: Equation (27.2), defer when p_E >= max_y p(y | x)
    def test_d01_route_by_comparison(self):
        seen = {}
        for (expert, model), state in self.states("C27-D01"):
            m = dict(state["metrics"])
            defers = expert >= model - 1e-12
            route = m["Route chosen by Equation (27.2)"]
            self.assertEqual(route.startswith("Delegate"), defers, (expert, model))
            self.assertEqual(m["Expert minus classifier"], f"{expert - model:.2f}")
            seen[(expert, model)] = route
        # The chapter's two cases at confidence 0.78: expert 0.95 delegates, expert 0.60 does not.
        self.assertTrue(seen[(0.95, 0.78)].startswith("Delegate"))
        self.assertFalse(seen[(0.6, 0.78)].startswith("Delegate"))
        # Boundary: equality defers (the "at least as large" side) and is called a tie.
        self.assertIn("tie", seen[(0.78, 0.78)])
        # The same expert at 0.95 loses to a 0.97 classifier.
        self.assertFalse(seen[(0.95, 0.97)].startswith("Delegate"))

    # Demonstration 2: the book's route-value table and Equation (27.3)
    def test_d02_route_values_against_the_books_table(self):
        gross = 0.90 * (0.98 * 10 + 0.02 * (-10)) + 0.10 * (0.94 * 0 + 0.06 * (-100))
        self.assertAlmostEqual(gross, 8.04)
        for (cost, authorized), state in self.states("C27-D02"):
            m = dict(state["metrics"])
            release = 0.90 * 10 + 0.10 * (-100)
            review = 0.35 * gross + 0.65 * release - 1
            wait = 0.5 * 9 + 0.5 * (-1) - 2
            hold = 0.95 * gross + 0.05 * (-4) - cost - 1
            self.assertEqual(m["Release now"], f"{release:.3f}")
            self.assertEqual(m["Review; release on timeout"], f"{review:.3f}")
            self.assertEqual(m["Wait for confirmation; release on timeout"], f"{wait:.3f}")
            hold_shown = m["Reversible hold and review; return on timeout"]
            allowed = {"Release now": release, "Review; release on timeout": review, "Wait for confirmation; release on timeout": wait}
            if authorized == "Yes, authorized":
                self.assertEqual(hold_shown, f"{hold:.3f}")
                allowed["Reversible hold and review; return on timeout"] = hold
            else:
                self.assertEqual(hold_shown, f"{hold:.3f} (excluded)")
            best = max(allowed, key=allowed.get)
            self.assertEqual(m["Highest of the four modeled routes"], best)
            # Break-even hold cost: 0.95 x 8.04 + 0.05 x (-4) - 1 - 2 = 4.438
            self.assertEqual(m["Hold cost at which waiting (2) overtakes it"], f"{0.95 * 8.04 - 0.2 - 1 - 2:.3f}")
        book = dict(next(s for v, s in self.states("C27-D02") if v == [2, "Yes, authorized"])["metrics"])
        self.assertEqual((book["Release now"], book["Review; release on timeout"], book["Wait for confirmation; release on timeout"],
                          book["Reversible hold and review; return on timeout"]), ("-1.000", "1.164", "2.000", "4.438"))
        # At hold cost 5 the hold falls below waiting; unauthorized, the hold cannot win even at cost 2.
        self.assertEqual(dict(next(s for v, s in self.states("C27-D02") if v == [5, "Yes, authorized"])["metrics"])["Highest of the four modeled routes"],
                         "Wait for confirmation; release on timeout")
        self.assertEqual(dict(next(s for v, s in self.states("C27-D02") if v == [2, "No, not authorized"])["metrics"])["Highest of the four modeled routes"],
                         "Wait for confirmation; release on timeout")

    # Demonstration 3: mean time in system 1 / (mu - f lambda)
    def test_d03_mm1_mean_time(self):
        lam = 4.0
        for (mu, f), state in self.states("C27-D03"):
            m = dict(state["metrics"])
            load = f * lam
            self.assertEqual(m["Review arrivals f x lambda (per hour)"], f"{load:.2f}")
            shown = m["Mean time in system"]
            if load < mu:
                mean = 1 / (mu - load)
                self.assertEqual(shown, f"{mean:.2f} hours ({mean * 60:.0f} minutes)")
                self.assertEqual(m["Mean within the 20-minute window"], "yes" if mean <= 20 / 60 else "no")
            else:
                self.assertTrue(shown.startswith("undefined"), (mu, f))
                self.assertEqual(m["Mean within the 20-minute window"], "not applicable")
        pick = lambda mu, f: dict(next(s for v, s in self.states("C27-D03") if v == [mu, f])["metrics"])["Mean time in system"]
        # The chapter's numbers at 3 reviews per hour: 1 hour at f = 0.5, 5 hours at f = 0.7, undefined at 0.9.
        self.assertTrue(pick(3, 0.5).startswith("1.00 hours (60 minutes)"))
        self.assertTrue(pick(3, 0.7).startswith("5.00 hours (300 minutes)"))
        self.assertTrue(pick(3, 0.9).startswith("undefined"))
        # Singular case: f x lambda = mu exactly is a division by zero and is called one.
        self.assertTrue(pick(4, 1.0).startswith("undefined"))
        self.assertIn("division by zero", next(s for v, s in self.states("C27-D03") if v == [4, 1.0])["interpretation"])

    # Demonstration 4: Equation (27.4), VOI > delay cost and an authorized fallback
    def test_d04_wait_test(self):
        for (q, fallback), state in self.states("C27-D04"):
            m = dict(state["metrics"])
            voi = q * 9 + (1 - q) * (-1) - (-1)
            self.assertAlmostEqual(voi, 10 * q)
            self.assertEqual(m["Value of information (VOI)"], f"{voi:.2f}")
            self.assertEqual(m["VOI minus delay cost"], f"{voi - 2:.2f}")
            ok = fallback == "Yes, authorized"
            waits = voi > 2 + 1e-9 and ok
            self.assertEqual(m["Passes Equation (27.4)"].startswith("Yes"), waits, (q, fallback))
            self.assertEqual(m["Break-even arrival probability"], "0.20")
        decision = lambda q, fb: dict(next(s for v, s in self.states("C27-D04") if v == [q, fb])["metrics"])["Passes Equation (27.4)"]
        # Boundary: q = 0.2 makes VOI exactly equal the delay cost, and the strict inequality fails.
        self.assertIn("equals", decision(0.2, "Yes, authorized"))
        self.assertEqual(decision(0.5, "Yes, authorized"), "Yes (waiting allowed)")
        self.assertIn("fallback not authorized", decision(0.8, "No, not authorized"))
        # The book's wait route: 0.50 x 9 + 0.50 x (-1) - 2 = 2 equals the net value shown by VOI 5 minus delay 2 plus release (-1).
        self.assertEqual(0.50 * 9 + 0.50 * (-1) - 2, 5 - 2 + (-1))

    # Regression tests for the reviewed fixes
    def test_d03_names_the_m_m_1_model(self):
        self.assertIn("M/M/1", self.page)
        self.assertIn("exponentially distributed service times", self.page)
        self.assertNotIn("random service times with a steady rate", self.page)
        self.assertNotIn("For one reviewer with random arrivals and service times", self.page)
        # The counterexample the review used: deterministic service at mu = 3 with 2 arrivals per hour is 2/3 hour, not 1.
        rho, mu = 2 / 3, 3
        self.assertAlmostEqual(1 / mu + rho / (2 * mu * (1 - rho)), 2 / 3)
        self.assertAlmostEqual(1 / (mu - 2), 1.0)

    def test_d04_check_answer_boundary_is_strict(self):
        # At q = 0.30 and delay cost 3, VOI equals the delay cost, which fails the strict test.
        voi = 0.3 * 9 + 0.7 * (-1) + 1
        self.assertAlmostEqual(voi, 3.0)
        answer = self.page
        self.assertIn("at or below q = 3 / 10 = 0.30", answer)
        self.assertNotIn("It would fail only below q = 3 / 10", answer)
        # The demonstration itself treats VOI equal to the delay cost as failing (q = 0.2, delay 2).
        eq = dict(next(s for v, s in self.states("C27-D04") if v == [0.2, "Yes, authorized"])["metrics"])
        self.assertEqual(eq["Passes Equation (27.4)"], "No (VOI equals delay cost)")

    def test_d02_shows_where_the_break_even_comes_from(self):
        state = next(s for v, s in self.states("C27-D02") if v == [2, "Yes, authorized"])
        self.assertIn("0.95 x 8.04 + 0.05 x (-4) - 1 = 6.438", state["interpretation"])
        self.assertIn("6.438 - 2 = 4.438", state["interpretation"])
        metrics = dict(state["metrics"])
        self.assertNotIn("Chosen by Equation (27.3)", metrics)
        self.assertNotIn("Break-even hold cost", metrics)
        self.assertIn("returning control is not given a value", self.page)

    def test_d01_d03_d04_wording(self):
        self.assertNotIn("never low in absolute terms", self.page)
        self.assertNotIn("Do not set a single confidence threshold", self.page)
        self.assertIn("justified only if the destination's correctness is the same", html.unescape(self.page))
        self.assertIn("assumed calibrated", self.page)
        self.assertNotIn("licensed", self.page)
        self.assertNotIn("Decision under Equation (27.4)", self.page)
        unstable = next(s for v, s in self.states("C27-D03") if v == [3, 0.9])
        self.assertNotIn("No stationary mean exists", unstable["interpretation"])
        self.assertIn("long-run", unstable["interpretation"])

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 27)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\(quad|qquad)", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".,;")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        allowed |= {norm(m) for m in re.findall(r"`([^`]+)`", CHAPTER_TEXT.read_text(encoding="utf-8"))}
        alts = re.findall(r'alt="Equation: ([^"]+)"', self.page)
        self.assertEqual(len(alts), 3)  # (27.2), (27.3), (27.4) are pre-rendered; the inline M/M/1 formula is typeset as TeX
        self.assertIn(r"1/(\mu-f\lambda)", html.unescape(self.page))
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "--", "\u2212"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_all_control_combinations_render(self):
        for d in self.data["demos"]:
            expected = 1
            for c in d["controls"]:
                expected *= len(c["values"])
            self.assertEqual(len(d["states"]), expected, d["id"])
            for state in d["states"].values():
                self.assertTrue(state["image"].startswith("data:image/svg+xml"))
                self.assertTrue(state["interpretation"])

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(BUILT)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (28, 4, 8))


if __name__ == "__main__":
    unittest.main()

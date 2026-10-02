"""Chapter 24 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(the two-bank example, the onset definition, the union-bound margin, the
two-task repeated-run construction), not read back from the module that
produced the page. The reader is built into a private temporary directory, so
the tests do not depend on, or change, the committed readers folder.
"""
from __future__ import annotations

import html
import importlib.util
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
SLUG = "24-matched-capability"


def builder_python():
    import importlib.util
    import sys
    if all(importlib.util.find_spec(m) for m in ("numpy", "matplotlib", "jinja2")):
        return sys.executable
    candidate = LAB / ".venv" / "bin" / "python"
    if candidate.exists():
        probe = subprocess.run([str(candidate), "-c", "import numpy, matplotlib, jinja2"], capture_output=True)
        if probe.returncode == 0:
            return str(candidate)
    return None


def authored_demos(number):
    """The authored CHAPTER dictionary of the module under test, keyed by demonstration id (for wording checks)."""
    import sys
    for p in (str(LAB / "tools" / "readers" / "engine"), str(LAB / "src")):
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location(f"reader_ch{number}_wording", LAB / "tools" / "readers" / "chapters" / f"ch{number}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {d["id"]: d for d in mod.CHAPTER["demos"]}


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


@unittest.skipIf(builder_python() is None, "no interpreter with numpy, matplotlib and jinja2")
class Chapter24ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="reader-ch24-")
        run = subprocess.run([builder_python(), str(WRAPPER), "--chapters", "24", "--out", cls.tmp], capture_output=True,
                             text=True, timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls.tmp) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    CONTROL_VALUES = {  # the values each control takes, in the order the page lists them (written here by hand)
        "C24-D01": [[100, 400, 1600], [0.73, 0.78]],
        "C24-D02": [[0.3, 0.5, 0.6, 0.7], ["all", "odd"]],
        "C24-D03": [[100, 400, 1600], [2, 4]],
        "C24-D04": [["0.50", "0.35", "0.20", "0.10"], [2, 3]],
    }

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [vals[i] for vals, i in zip(self.CONTROL_VALUES[demo_id], idx)], state

    def test_four_demonstrations_all_combinations_render(self):
        self.assertEqual(list(self.demos), ["C24-D01", "C24-D02", "C24-D03", "C24-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [6, 8, 6, 8])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    # Demonstration 1: two independent banks

    def test_d01_book_example_and_every_state(self):
        for (n, q), state in self.states("C24-D01"):
            n = int(n)
            passes_b, passes_m = round(0.8 * n), round(q * n)
            pb, pm = passes_b / n, passes_m / n
            se = math.sqrt(pb * (1 - pb) / n + pm * (1 - pm) / n)
            diff = pb - pm
            lo, hi = diff - 1.96 * se, diff + 1.96 * se
            m = dict(state["metrics"])
            self.assertEqual(m["Gap (Equation 24.2)"], f"{diff:.3f}")
            self.assertEqual(m["Standard error of the gap"], f"{se:.5f}")
            self.assertEqual(m["95% interval"], f"[{lo:.5f}, {hi:.5f}]")
            self.assertEqual(m["Interval and zero"], "excludes zero" if lo > 0 else "includes zero")
        # The chapter's own numbers: 0.07, 0.029879, [0.01144, 0.12856] at 400 tasks.
        book = dict(next(s for v, s in self.states("C24-D01") if v == [400, 0.73])["metrics"])
        self.assertEqual(book["Standard error of the gap"], "0.02988")
        self.assertEqual(book["95% interval"], "[0.01144, 0.12856]")
        thin = dict(next(s for v, s in self.states("C24-D01") if v == [100, 0.73])["metrics"])
        self.assertEqual(thin["Interval and zero"], "includes zero")

    def test_d01_standard_error_halves_when_tasks_quadruple(self):
        se = {n: float(dict(s["metrics"])["Standard error of the gap"]) for (n, q), s in self.states("C24-D01") if q == 0.73}
        self.assertAlmostEqual(se[100] / se[400], 2.0, delta=0.01)
        self.assertAlmostEqual(se[400] / se[1600], 2.0, delta=0.01)

    # Demonstration 2: onset

    def test_d02_onset_by_hand(self):
        g = [0.04, 0.09, 0.17, 0.30, 0.46, 0.58, 0.66, 0.71]
        expected = {  # (threshold, tested) -> onset by reading the list
            (0.3, "all"): 4, (0.3, "odd"): 5, (0.5, "all"): 6, (0.5, "odd"): 7,
            (0.6, "all"): 7, (0.6, "odd"): 7, (0.7, "all"): 8, (0.7, "odd"): None,
        }
        for (zeta, tested), state in self.states("C24-D02"):
            members = range(1, 9) if tested == "all" else (1, 3, 5, 7)
            reached = [m for m in members if g[m - 1] >= zeta - 1e-12]
            onset = reached[0] if reached else None
            self.assertEqual(onset, expected[(zeta, tested)])
            m = dict(state["metrics"])
            if onset is None:
                self.assertTrue(m["Onset"].startswith("undefined"), m["Onset"])
                self.assertEqual(m["Highest tested score"], "0.66")
            else:
                self.assertEqual(m["Onset"], f"m = {onset}")
        # A score exactly at the threshold counts (0.30 at member 4 reaches 0.30).
        self.assertEqual(dict(next(s for v, s in self.states("C24-D02") if v == [0.3, "all"])["metrics"])["Onset"], "m = 4")

    def test_d02_sparser_testing_never_moves_onset_earlier(self):
        onset = {tuple(v): dict(s["metrics"])["Onset"] for v, s in self.states("C24-D02")}
        for zeta in (0.3, 0.5, 0.6, 0.7):
            dense, sparse = onset[(zeta, "all")], onset[(zeta, "odd")]
            if sparse.startswith("m = "):
                self.assertGreaterEqual(int(sparse[4:]), int(dense[4:]))

    def test_d01_wording_does_not_overstate(self):
        # Findings g8-30 and g8-31: no "precise", "unreadable" or "usually"; the chapter's own wording is used.
        demo = authored_demos(24)["C24-D01"]
        self.assertNotIn("precise", demo["explanation"])
        self.assertNotIn("unreadable", demo["explanation"])
        self.assertIn("excludes zero at 400 tasks and includes zero at 100", demo["explanation"])
        for v, state in self.states("C24-D01"):
            self.assertNotIn("usually", state["interpretation"])
        book = next(s for v, s in self.states("C24-D01") if v == [400, 0.73])
        self.assertIn("The interval excludes zero under this sampling model.", book["interpretation"])
        # The recomputed intervals behind the new sentence: 400 tasks excludes zero, 100 tasks includes it.
        for n, excludes in ((400, True), (100, False)):
            se = math.sqrt(0.8 * 0.2 / n + 0.73 * 0.27 / n)
            self.assertEqual(0.07 - 1.96 * se > 0, excludes)
        # Finding g8-32: the symbols line maps U-hat, V_bench, V_match and theta to p1, p2.
        self.assertIn("V_bench and V_match", demo["symbols"])
        self.assertIn("theta is the fixed model", demo["symbols"])

    def test_d02_verdict_follows_the_plotted_state(self):
        # Findings g8-27 and g8-28: the onset moves only in some states, and the text says which.
        by = {tuple(v): s["interpretation"] for v, s in self.states("C24-D02")}
        for text in by.values():
            self.assertNotIn("rose by a small amount", text)
            self.assertNotIn("moves with it", text)
        self.assertIn("leaves the onset at m = 7, the same as with all eight members", by[(0.6, "odd")])
        self.assertNotIn("moves the onset", by[(0.6, "odd")])
        self.assertIn("moves the onset from m = 6 (all eight tested) to m = 7", by[(0.5, "odd")])
        self.assertIn("moves the onset from m = 4 (all eight tested) to m = 5", by[(0.3, "odd")])
        self.assertIn("can move this onset", by[(0.5, "all")])
        self.assertIn("can move it further", authored_demos(24)["C24-D02"]["explanation"])

    def test_d02_negative_difference_has_no_stray_parentheses(self):
        # Finding g8-29: 0.66 - 0.70 = -0.04, printed plainly.
        _, state = next(s for s in self.states("C24-D02") if s[0] == [0.7, "odd"])
        self.assertIn("0.66 - 0.70 = -0.04 is below zero", state["interpretation"])
        self.assertNotIn("(-0.04)", state["interpretation"])

    # Demonstration 3: simultaneous lower frontier

    def test_d03_union_bound_margin_and_frontier(self):
        rates = [0.60, 0.68, 0.72, 0.74]
        names = ["Direct prompt", "Retrieval", "Retrieval and tools", "Tools and selector"]
        for (n, k), state in self.states("C24-D03"):
            n, k = int(n), int(k)
            t = math.sqrt(math.log(k / 0.05) / (2 * n))
            single = math.sqrt(math.log(1 / 0.05) / (2 * n))
            best = max(range(k), key=lambda i: rates[i])
            m = dict(state["metrics"])
            self.assertEqual(m["Configurations tested"], str(k))
            self.assertEqual(m["Simultaneous margin t"], f"{t:.3f}")
            self.assertEqual(m["Margin if one configuration were tested alone"], f"{single:.3f}")
            self.assertEqual(m["Frontier value (LCF)"], f"{rates[best] - t:.3f}")
            self.assertEqual(m["Configuration that sets it"], names[best])
            self.assertGreater(t, single)
        # Hoeffding check: at the margin the tail bound k times exp(-2 n t^2) equals the allowed 0.05.
        t = math.sqrt(math.log(4 / 0.05) / (2 * 400))
        self.assertAlmostEqual(4 * math.exp(-2 * 400 * t * t), 0.05, places=12)
        # Check-question answer printed in the page: 1600 tasks, four configurations, estimate 0.74.
        self.assertAlmostEqual(0.74 - math.sqrt(math.log(80) / 3200), 0.703, places=3)

    def test_d03_untested_configurations_stay_out_of_the_frontier(self):
        two = dict(next(s for v, s in self.states("C24-D03") if v == [400, 2])["metrics"])
        four = dict(next(s for v, s in self.states("C24-D03") if v == [400, 4])["metrics"])
        self.assertEqual(two["Configuration that sets it"], "Retrieval")
        self.assertEqual(four["Configuration that sets it"], "Tools and selector")
        interpretation = next(s for v, s in self.states("C24-D03") if v == [400, 2])["interpretation"]
        self.assertIn("were never run", interpretation)

    # Demonstration 4: same average, different reliability

    def test_d04_two_task_construction(self):
        pairs = {"0.50": (0.5, 0.5), "0.35": (0.35, 0.65), "0.20": (0.2, 0.8), "0.10": (0.1, 0.9)}
        for (spread, k), state in self.states("C24-D04"):
            k = int(k)
            a, b = pairs[spread]
            m = dict(state["metrics"])
            self.assertEqual(m["Mean single-run success"], "0.50")
            self.assertEqual(m["All runs, average of tasks"], f"{(a ** k + b ** k) / 2:.3f}")
            self.assertEqual(m["All runs, mean-rate formula"], f"{0.5 ** k:.3f}")
            self.assertEqual(m["At least one, average of tasks"], f"{((1 - (1 - a) ** k) + (1 - (1 - b) ** k)) / 2:.3f}")
            self.assertEqual(m["At least one, mean-rate formula"], f"{1 - 0.5 ** k:.3f}")
        # The chapter's numbers: 0.34 against 0.25, and 0.66 against 0.75.
        book = dict(next(s for v, s in self.states("C24-D04") if v == ["0.20", 2])["metrics"])
        self.assertEqual((book["All runs, average of tasks"], book["All runs, mean-rate formula"]), ("0.340", "0.250"))
        self.assertEqual((book["At least one, average of tasks"], book["At least one, mean-rate formula"]), ("0.660", "0.750"))

    def test_d04_identical_tasks_make_the_formulas_agree(self):
        for k in (2, 3):
            state = next(s for v, s in self.states("C24-D04") if v == ["0.50", k])
            m = dict(state["metrics"])
            self.assertEqual(m["All runs, average of tasks"], m["All runs, mean-rate formula"])
            self.assertEqual(m["At least one, average of tasks"], m["At least one, mean-rate formula"])
            self.assertIn("no spread", state["interpretation"])

    def test_d04_task_spread_pushes_the_two_numbers_in_opposite_directions(self):
        for v, s in self.states("C24-D04"):
            if v[0] == "0.50":
                continue
            m = dict(s["metrics"])
            self.assertGreater(float(m["All runs, average of tasks"]), float(m["All runs, mean-rate formula"]))
            self.assertLess(float(m["At least one, average of tasks"]), float(m["At least one, mean-rate formula"]))

    def test_d03_dependence_wording_and_symbols(self):
        demo = authored_demos(24)["C24-D03"]
        # Finding g8-34: no unsupported general claim about dependence.
        self.assertNotIn("the margin is too small.", demo["assumptions"])
        self.assertIn("independence-based margin is no longer justified", demo["assumptions"])
        # Finding g8-33: V, S_xi and the instantiation of Lower^sim are named.
        self.assertIn("S_xi is the set of components enabled in configuration xi", demo["symbols"])
        self.assertIn("instantiated here as the observed rate minus the margin t", demo["symbols"])

    def test_d04_verdict_uses_the_run_count_and_equal_gaps_print_equally(self):
        # Finding g8-26: with three runs the mean-rate formula is a cube, not a square.
        for spread in ("0.35", "0.20", "0.10"):
            text = next(s for v, s in self.states("C24-D04") if v == [spread, 3])["interpretation"]
            self.assertIn("Raising the mean rate to the power 3 misses by", text)
            self.assertNotIn("Squaring", text)
            text2 = next(s for v, s in self.states("C24-D04") if v == [spread, 2])["interpretation"]
            self.assertIn("Squaring the mean rate misses by", text2)
        # Finding g8-37: at 0.35 and 0.65 with two runs both gaps are exactly 0.0225, so both print 0.023.
        text = next(s for v, s in self.states("C24-D04") if v == ["0.35", 2])["interpretation"]
        self.assertIn("misses by 0.023 for all-runs success", text)
        self.assertIn("misses by 0.023 for at-least-one success", text)
        self.assertNotIn("0.022", text)

    # Page level checks

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 24)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".,;")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 3)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)
        manuscript = (LAB.parent / "Manuscript" / "part-vi" / "24-how-much-capability-have-we-extracted.md").read_text()
        for tex in (r"1-(1-.9)^3=.999", r".9^3=.729"):
            self.assertIn(f"`{tex}`", manuscript)
            self.assertIn(html.escape(tex, quote=False), self.page)

    def test_headings_exist_in_the_canonical_chapter(self):
        manuscript = (LAB.parent / "Manuscript" / "part-vi" / "24-how-much-capability-have-we-extracted.md").read_text()
        headings = set(re.findall(r"^#{1,3} (.+)$", manuscript, re.M))
        text = html.unescape(self.page)
        cited = re.findall(r'Chapter 24 source: section "([^"]+)"', text)
        self.assertEqual(len(cited), 4)
        for heading in cited:
            self.assertIn(heading, headings)

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (28, 4, 8))


if __name__ == "__main__":
    unittest.main()

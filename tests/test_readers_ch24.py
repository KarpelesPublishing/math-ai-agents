"""Chapter 24 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(the two-bank counts 320 and 292 of 400, the laboratory's paired records, the
no-overlap transfer records, the aged-benchmark mixture, the onset of a gradual
curve, the union-bound margin and the two-task and recorded-bank reliability
constructions), not read back from the
module that produced the page. The reader is built fresh into a
temporary directory, so nothing under readers/ is touched.
"""
from __future__ import annotations

import html
import importlib.util
import json
import itertools
import math
import os
from fractions import Fraction
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from math_ai_agents.chapters.ch24 import evaluate

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
SLUG = "24-matched-capability"


def _builder_python():
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers.builder_python()


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


def f1(x):
    return f"{x:.1f}"


class Chapter24ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        python = _builder_python()
        if python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls._tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([python, str(WRAPPER), "--chapters", "24", "--out", cls._tmp.name], capture_output=True, text=True,
                             timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls._tmp.name) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def grid(self, demo_id):
        """Every state keyed by the tuple of raw control values (the page shows labels; the module holds the raw values)."""
        demo = self.demos[demo_id]
        raw = authored_demos(24)[demo_id]["controls"]
        out = {}
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = tuple(c["values"][i] for c, i in zip(raw, idx))
            out[values] = (dict(state["metrics"]), state["interpretation"], state)
        return out

    def test_patch2_d04_recorded_bank_is_attributed_to_the_workbench(self):
        # g8-13, g8-14
        demo = authored_demos(24)["C24-D04"]
        self.assertIn("Mathematical Workbench E.5", demo["provenance"])
        self.assertNotIn("the chapter's recorded bank", demo["provenance"])
        self.assertIn("subset size for the recorded bank", demo["controls"][1]["label"])

    def test_four_demonstrations_all_states_render(self):
        self.assertEqual(list(self.demos), ["C24-D01", "C24-D02", "C24-D03", "C24-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 9, 8])
        for demo in self.data["demos"]:
            combos = math.prod(len(c["values"]) for c in demo["controls"])
            self.assertEqual(len(demo["states"]), combos)
            for state in demo["states"].values():
                self.assertTrue(state["image"].startswith("data:image/svg+xml"))
                self.assertTrue(state["interpretation"])
                self.assertTrue(state["alt"])
                self.assertGreaterEqual(len(state["steps"]), 2)

    def test_size_budget(self):
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    # Demonstration 1: observations, denominators and estimands

    @staticmethod
    def wilson(s, n, z=1.959963984540054):
        p = s / n
        q = 1 + z * z / n
        c = (p + z * z / (2 * n)) / q
        h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / q
        return max(0, c - h), min(1, c + h)

    def test_d01_two_bank_case_by_hand(self):
        g = self.grid("C24-D01")
        m, text, _ = g[("book", "scores")]
        self.assertEqual((m["Benchmark score"], m["Matched score"]), ("0.80", "0.73"))   # 320 / 400 and 292 / 400
        self.assertIn("(1 / 400) x 320 = 0.80", text)
        self.assertEqual(m["Half-width, benchmark"], f"{1.96 * math.sqrt(0.8 * 0.2 / 400):.4f}")
        m, text, _ = g[("book", "gap")]
        self.assertEqual(m["Gap (Equation 24.2)"], "0.070")
        for n in (100, 400, 1600):
            se = math.sqrt(0.8 * 0.2 / n + 0.73 * 0.27 / n)
            self.assertEqual(m[f"Standard error at {n} tasks"], f"{se:.5f}")
        self.assertEqual(m["95% interval at 400 tasks"], "[0.01144, 0.12856]")          # the chapter's interval
        self.assertEqual(m["Interval excludes zero at 100, 400, 1600"], "no, yes, yes")
        self.assertAlmostEqual(math.sqrt(0.8 * 0.2 / 400 + 0.73 * 0.27 / 400), 0.029879, places=6)
        self.assertAlmostEqual(math.sqrt(0.8 * 0.2 / 1600 + 0.73 * 0.27 / 1600) * 2, math.sqrt(0.8 * 0.2 / 400 + 0.73 * 0.27 / 400), places=9)
        # Independent banks have no task cells to re-weight.
        self.assertTrue(g[("book", "weights")][0]["Task-weighted score"].startswith("undefined"))

    def test_d01_lab_records_by_hand(self):
        g = self.grid("C24-D01")
        base = [True, False, True, False]    # runs 0 to 3
        new = [True, True, True, False]
        m, text, _ = g[("lab", "scores")]
        self.assertEqual((m["Base score (all runs)"], m["New score (all runs)"]), ("0.50", "0.75"))
        lo, hi = self.wilson(2, 4)
        self.assertEqual(m["Base 95% Wilson interval"], f"[{lo:.3f}, {hi:.3f}]")
        lo, hi = self.wilson(3, 4)
        self.assertEqual(m["New 95% Wilson interval"], f"[{lo:.3f}, {hi:.3f}]")
        self.assertEqual(m["Exposed rate, base and new"], "0.00 of 2 and 0.50 of 2")   # hard runs only: runs 1 and 3
        m, text, _ = g[("lab", "gap")]
        diffs = [int(n) - int(b) for b, n in zip(base, new)]
        mean = sum(diffs) / 4
        se = math.sqrt(sum((d - mean) ** 2 for d in diffs) / 3 / 4)
        self.assertEqual(m["Paired differences"], "0, 1, 0, 0")
        self.assertEqual((m["Matched difference"], m["Standard error (independent pairs)"]), (f"{mean:.2f}", f"{se:.2f}"))
        self.assertIn("(0 + 1 + 0 + 0) / 4 = 0.25", text)
        m, text, _ = g[("lab", "weights")]
        def mix(rates, w_easy):
            return w_easy * rates["easy"] + (1 - w_easy) * rates["hard"]
        rb, rn = {"easy": 1.0, "hard": 0.0}, {"easy": 1.0, "hard": 0.5}
        self.assertEqual(m["Base and new, equal weights"], f"{mix(rb, .5):.2f} and {mix(rn, .5):.2f}")
        self.assertEqual(m["Base and new, hard-heavy"], f"{mix(rb, .1):.2f} and {mix(rn, .1):.2f}")   # 0.10 and 0.55
        self.assertEqual(m["Records changed"], "none")
        self.assertIn("0.1 x 1 + 0.9 x 0.5 = 0.55", text)

    def test_d01_transfer_records_are_unavailable_not_zero(self):
        g = self.grid("C24-D01")
        m, text, _ = g[("transfer", "scores")]
        self.assertEqual((m["Old score"], m["Proposal score"]), ("1.00 (1 of 1)", "0.00 (0 of 1)"))
        lo, hi = self.wilson(1, 1)
        self.assertEqual(m["Old Wilson interval"], f"[{lo:.3f}, {hi:.3f}]")
        m, text, _ = g[("transfer", "gap")]
        self.assertEqual(m["Matched pairs"], "0")
        self.assertTrue(m["Matched difference"].startswith("undefined"))
        self.assertTrue(m["Standard error"].startswith("undefined"))
        self.assertIn("0 + 0 = 0", text)
        m, text, _ = g[("transfer", "weights")]
        self.assertEqual((m["Cells needed"], m["Cells observed"]), ("4 (2 procedures x 2 tasks)", "2"))
        self.assertTrue(m["Mixture score, old"].startswith("undefined"))
        self.assertTrue(m["Mixture score, proposal"].startswith("undefined"))
        self.assertIn("1 + 1 = 2 of 4", text)

    def test_d01_aged_benchmark_mixture(self):
        g = self.grid("C24-D01")
        m, text, _ = g[("aged", "scores")]
        self.assertEqual(m["Aggregate success"], "0.52")                  # 0.2 x 1 + 0.8 x 0.4
        self.assertIn("0.2 x 1 + 0.8 x 0.4 = 0.52", text)
        m, text, _ = g[("aged", "gap")]
        self.assertEqual((m["Difference"], m["Difference in points"]), ("0.12", "12"))
        self.assertIn("0.2 x (1 - 0.4) = 0.12", text)
        self.assertIn("not a measured contamination effect", text)
        m, text, _ = g[("aged", "weights")]
        self.assertEqual((m["Aggregate at 0% exposed"], m["Aggregate at 20% exposed"], m["Aggregate at 50% exposed"]), ("0.40", "0.52", "0.70"))
        self.assertIn("0.4 + 0.6 x 0.5 = 0.70", text)

    def test_d01_lab_function_agrees_with_the_cases(self):
        out = evaluate({"baseline": "base", "candidate": "new", "records": [
            {"procedure": "base", "task": t, "run": r, "success": s, "cost": 1, "exposed": t == "hard"} for t, r, s in
            (("easy", "0", True), ("hard", "1", False), ("easy", "2", True), ("hard", "3", False))] + [
            {"procedure": "new", "task": t, "run": r, "success": s, "cost": 2, "exposed": t == "hard"} for t, r, s in
            (("easy", "0", True), ("hard", "1", True), ("easy", "2", True), ("hard", "3", False))],
            "task_weights": {"easy": 0.1, "hard": 0.9}})
        self.assertEqual(out["metrics"]["matched_difference"], 0.25)
        self.assertAlmostEqual(out["metrics"]["task_mixture_rates"]["new"], 0.55)

    # Demonstration 2: onset

    def test_d02_onset_by_hand(self):
        scores = [0.04, 0.09, 0.17, 0.30, 0.46, 0.58, 0.66, 0.71]
        sets = {"all": range(1, 9), "odd": (1, 3, 5, 7), "even": (2, 4, 6, 8)}
        for (zeta, tested), (m, text, _) in self.grid("C24-D02").items():
            reached = [k for k in sets[tested] if round(scores[k - 1] * 100) >= round(zeta * 100)]
            if reached:
                self.assertEqual(m["Onset"], f"m = {reached[0]}")
            else:
                self.assertTrue(m["Onset"].startswith("undefined"))
            self.assertEqual(m["Highest tested score"], f"{max(scores[k - 1] for k in sets[tested]):.2f}")
            full = next((k for k in range(1, 9) if round(scores[k - 1] * 100) >= round(zeta * 100)), None)
            self.assertEqual(m["Onset with all eight tested"], f"m = {full}" if full else "undefined")
            if tested != "all" and reached and full and reached[0] > full:
                self.assertIn(f"moves the onset from m = {full} (all eight tested) to m = {reached[0]}", text)
            if tested != "all" and not reached and full:
                self.assertIn("untested, not never", text)
        by = {k: v[0] for k, v in self.grid("C24-D02").items()}
        self.assertEqual(by[(0.6, "all")]["Onset"], "m = 7")                           # check question
        self.assertEqual(by[(0.6, "even")]["Onset"], "m = 8")
        self.assertTrue(by[(0.7, "odd")]["Onset"].startswith("undefined"))             # prediction
        self.assertEqual(by[(0.7, "all")]["Onset"], "m = 8")
        for zeta in (0.3, 0.5, 0.6, 0.7):                                              # sparser testing never moves onset earlier
            full = by[(zeta, "all")]["Onset"]
            for t in ("odd", "even"):
                o = by[(zeta, t)]["Onset"]
                if not o.startswith("undefined"):
                    self.assertGreaterEqual(int(o.split("= ")[1]), int(full.split("= ")[1]))

    # Demonstration 3: union-bound frontier

    def test_d03_union_bound_margin_and_frontier_by_hand(self):
        rates = [("Direct prompt", 0.60), ("Retrieval", 0.68), ("Retrieval and tools", 0.72), ("Tools and selector", 0.74)]
        for (n, k), (m, text, _) in self.grid("C24-D03").items():
            t = math.sqrt(math.log(k / 0.05) / (2 * n))
            chosen = rates[:k]
            lcf = max(r for _, r in chosen) - t
            self.assertEqual(m["Simultaneous margin t"], f"{t:.3f}")
            self.assertEqual(m["Margin if one configuration were tested alone"], f"{math.sqrt(math.log(1 / 0.05) / (2 * n)):.3f}")
            self.assertEqual(m["Frontier value (LCF)"], f"{lcf:.3f}")
            self.assertEqual(m["Configuration that sets it"], max(chosen, key=lambda c: c[1])[0])
            # Hoeffding check: the tail bound summed over k configurations equals the allowed 0.05.
            self.assertAlmostEqual(k * math.exp(-2 * n * t * t), 0.05, places=9)
            if k < 4:
                self.assertIn("never run", text)
        by = {k: v[0] for k, v in self.grid("C24-D03").items()}
        self.assertEqual(by[(1600, 4)]["Frontier value (LCF)"], "0.703")                # check question
        self.assertLess(float(by[(400, 2)]["Simultaneous margin t"]), float(by[(400, 4)]["Simultaneous margin t"]))   # prediction
        self.assertLess(float(by[(400, 3)]["Simultaneous margin t"]), float(by[(400, 4)]["Simultaneous margin t"]))

    # Demonstration 4: reliability

    @staticmethod
    def f3(x):
        from decimal import ROUND_HALF_UP, Decimal
        return str(Decimal(repr(round(x, 10))).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP))

    def test_d04_two_task_and_recorded_bank_by_hand(self):
        pairs = {"0.50": (0.5, 0.5), "0.20": (0.2, 0.8), "0.10": (0.1, 0.9)}
        for (bank, k), (m, text, _) in self.grid("C24-D04").items():
            if bank == "recorded":
                runs = [True, True, True, False]
                subsets = list(itertools.combinations(runs, k))
                all_frac = sum(all(s) for s in subsets) / len(subsets)
                any_frac = sum(any(s) for s in subsets) / len(subsets)
                p = sum(runs) / len(runs)
                self.assertEqual(m["All runs, subset fraction"], self.f3(all_frac))
                self.assertEqual(m["At least one, subset fraction"], self.f3(any_frac))
                self.assertEqual(m["All runs, plug-in formula"], self.f3(p ** k))
                self.assertEqual(m["At least one, plug-in formula"], self.f3(1 - (1 - p) ** k))
            else:
                lo, hi = pairs[bank]
                mean = (lo + hi) / 2
                self.assertEqual(m["Mean single-run success"], f"{mean:.2f}")
                self.assertEqual(m["All runs, average of tasks"], self.f3((lo ** k + hi ** k) / 2))
                self.assertEqual(m["All runs, mean-rate formula"], self.f3(mean ** k))
                self.assertEqual(m["At least one, average of tasks"], self.f3(((1 - (1 - lo) ** k) + (1 - (1 - hi) ** k)) / 2))
                self.assertEqual(m["At least one, mean-rate formula"], self.f3(1 - (1 - mean) ** k))

    def test_d04_chapter_numbers(self):
        by = {k: v for k, v in self.grid("C24-D04").items()}
        m = by[("0.20", 2)][0]   # the chapter: 0.04 and 0.64 average to 0.34, squaring the mean gives 0.25; 0.36 and 0.96 give 0.66, coverage of the mean 0.75
        self.assertEqual((m["All runs, average of tasks"], m["All runs, mean-rate formula"]), ("0.340", "0.250"))
        self.assertEqual((m["At least one, average of tasks"], m["At least one, mean-rate formula"]), ("0.660", "0.750"))
        m = by[("0.10", 3)][0]   # check question: (0.001 + 0.729) / 2 = 0.365 against 0.125
        self.assertEqual((m["All runs, average of tasks"], m["All runs, mean-rate formula"]), ("0.365", "0.125"))
        m = by[("recorded", 2)][0]   # C(3,2) / C(4,2) = 3 / 6 and all six two-run subsets contain a success
        self.assertEqual((m["All runs, subset fraction"], m["At least one, subset fraction"]), ("0.500", "1.000"))
        self.assertIn("C(3,2) / C(4,2) = 3 / 6 = 0.500", by[("recorded", 2)][1])
        # Identical tasks make the formulas agree.
        m = by[("0.50", 2)][0]
        self.assertEqual(m["All runs, average of tasks"], m["All runs, mean-rate formula"])
        self.assertIn("no spread between tasks", by[("0.50", 2)][1])
        # The workbench E.5 numbers: mean 0.5, consistency 0.34, coverage 0.66, squared mean 0.25, coverage of the mean 0.75.
        self.assertAlmostEqual((0.04 + 0.64) / 2, 0.34)
        self.assertAlmostEqual((0.36 + 0.96) / 2, 0.66)

    # Optional fields

    def test_optional_fields_are_present_and_sourced(self):
        authored = authored_demos(24)
        text = (LAB.parent / "Manuscript" / "part-vi" / "24-how-much-capability-have-we-extracted.md").read_text(encoding="utf-8")
        self.assertIn("## What this does not settle", text)
        for demo_id, demo in authored.items():
            self.assertEqual(demo["scope_note"]["source_section"], "What this does not settle")
            self.assertIn("misconception", demo)
            self.assertEqual(len(demo["prediction_options"]), 3)
        self.assertIn("Ask the chapter skill", self.page)
        self.assertEqual(self.page.count("Common wrong turn"), 4)

    # Page-level checks

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 24)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".,;")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        shown = {norm(html.unescape(t)) for t in alts}
        self.assertEqual(len(alts), 4)  # 24.1 and 24.2, 24.3, 24.4 (the inline pair is typeset from the chapter's own text)
        for tex in shown:
            self.assertIn(tex, allowed)
        self.assertEqual(len(shown), 4)  # all four display equations are covered, including (24.1)
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
        self.assertIn("What this does not settle", headings)

    def test_links_and_offline(self):
        config = json.loads((LAB / "tools" / "readers" / "reader.config.json").read_text(encoding="utf-8"))
        index_href = config["links"]["index"]["href"]  # read from the configuration, which another owner may change
        for href in (f"../../notebooks/{SLUG}.ipynb", "../../skills/maa-24-matched-capability/SKILL.md", index_href):
            self.assertIn(f'href="{href}"', self.page)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for demo in self.data["demos"]:
            for state in demo["states"].values():
                text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"]) + " " + " ".join(state["steps"]) + " " + state["alt"]
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
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (41, 4, 8))
        self.assertEqual((report["ask_skill"], report["predictions_checked"], report["panels_checked"]), (1, 12, 8))


if __name__ == "__main__":
    unittest.main()

"""Chapter 26 reader: independent hand checks.

Expected numbers are recomputed here from the chapter's own arithmetic (the
ten-candidate subset example, the three-task bank, the reported percentages,
and the three constructed saturation points), not read from the module.
"""
from __future__ import annotations

import html
import importlib.util
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"


def builder_python():
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers.builder_python()


def payload(text):
    return json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


class Chapter26ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.python = builder_python()
        if cls.python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2")
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([cls.python, str(WRAPPER), "--chapters", "26", "--out", cls.tmp.name],
                             capture_output=True, text=True, timeout=600)
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.path = next(Path(cls.tmp.name).glob("26-*/reader.html"))
        cls.page = cls.path.read_text(encoding="utf-8")
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
            yield values, state

    def test_four_demos_and_every_state_rendered(self):
        self.assertEqual(list(self.demos), ["C26-D01", "C26-D02", "C26-D03", "C26-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 6, 8, 6])
        self.assertLess(self.path.stat().st_size, 2_500_000)

    def test_d01_finite_pool_coverage(self):
        for (c, k), state in self.states("C26-D01"):
            c, k = int(c), int(k)
            n = 10
            # Hypergeometric: probability that no passing program is among k chosen.
            none = math.prod((n - c - i) / (n - i) for i in range(k))
            m = dict(state["metrics"])
            self.assertEqual(m["Finite-pool coverage"], f"{1 - none:.4f}")
            self.assertEqual(m["Independent-draw formula"], f"{1 - (1 - c / n) ** k:.4f}")
            self.assertEqual(m["No-signal selector success"], f"{c / n:.2f}")
            self.assertEqual(m["Subsets with no pass"], str(round(none * math.comb(n, k))))
        book = dict(next(s for v, s in self.states("C26-D01") if v == [2, 3])["metrics"])
        self.assertEqual((book["Subsets in total"], book["Subsets with no pass"]), ("120", "56"))
        self.assertEqual(book["Finite-pool coverage"], "0.5333")
        self.assertEqual(book["Independent-draw formula"], "0.4880")
        self.assertEqual(book["Coverage not collected by that selector"], "0.3333")
        self.assertIn("1 - C(8,3) / C(10,3) = 1 - 56 / 120 = 0.5333", self.page)

    def test_d01_subset_table_matches_the_chapter(self):
        # 56 / 56 / 8 subsets with zero, one, two passes; 64 covered; uniform selector 24 of 120.
        n, c, k = 10, 2, 3
        rows = [math.comb(c, j) * math.comb(n - c, k - j) for j in range(3)]
        self.assertEqual(rows, [56, 56, 8])
        self.assertEqual(sum(rows[1:]), 64)
        self.assertAlmostEqual((rows[1] * 1 / 3 + rows[2] * 2 / 3) / 120, 0.2)

    def test_d02_ceiling_by_hand(self):
        weights = [0.2, 0.3, 0.5]
        bank = [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
        for (m, selector), state in self.states("C26-D02"):
            m = int(m)
            rows = bank[:m]
            cov = sum(w for t, w in enumerate(weights) if any(r[t] for r in rows))
            if selector.startswith("Always"):
                sel = sum(w for t, w in enumerate(weights) if rows[0][t])
            else:
                sel = cov  # an oracle takes a passing candidate whenever one exists
            mt = dict(state["metrics"])
            self.assertEqual(mt["Oracle coverage Cov"], f"{cov:.2f}")
            self.assertEqual(mt["Actual selection Sel"], f"{sel:.2f}")
            self.assertEqual(mt["Cov minus Sel"], f"{cov - sel:.2f}")
            self.assertLessEqual(sel, cov + 1e-12)
        # The no-passing-candidate reminder appears only when a task is uncovered (bank of 1 or 2).
        for (m_, selector), state in self.states("C26-D02"):
            has_note = "adds nothing to Cov" in state["interpretation"]
            self.assertEqual(has_note, int(m_) < 3, (m_, selector))
        by_key = {k: dict(s["metrics"]) for k, s in self.demos["C26-D02"]["states"].items()}
        # Notebook default: oracle 1, first-candidate selection 0.2.
        self.assertEqual((by_key["2,0"]["Oracle coverage Cov"], by_key["2,0"]["Actual selection Sel"]), ("1.00", "0.20"))
        # One-candidate bank: ceiling is only task 1 (weight 0.2), no selector passes it.
        self.assertEqual(by_key["0,1"]["Oracle coverage Cov"], "0.20")

    def test_d03_gap_and_hypothetical_share(self):
        base = {"Single sample (37.7, one draw, shown for scale)": 37.7, "Mean log-probability (44.5)": 44.5}
        for (start, share), state in self.states("C26-D03"):
            b, share = base[start], float(share)
            gap = 77.5 - b
            after = b + share * gap
            m = dict(state["metrics"])
            self.assertEqual(m["Gap Cov minus Sel (points)"], f"{gap:.1f}")
            digits = 1 if all(abs(x * 10 - round(x * 10)) < 1e-9 for x in (after, 77.5 - after)) else 2
            self.assertEqual(m["New selected success"], f"{after:.{digits}f}")
            self.assertEqual(m["Gap that remains"], f"{77.5 - after:.{digits}f}")
            # The written subtraction on the page must be true for the digits it shows.
            shown_after = float(m["New selected success"])
            shown_left = float(m["Gap that remains"])
            self.assertAlmostEqual(77.5 - shown_after, shown_left, places=6)
            self.assertIn(f"77.5 - {m['New selected success']} = {m['Gap that remains']} points", state["interpretation"])
            self.assertGreaterEqual(gap, 0)
        mid = dict(next(s for v, s in self.states("C26-D03") if v == ["Mean log-probability (44.5)", 0.5])["metrics"])
        self.assertEqual((mid["Gap Cov minus Sel (points)"], mid["New selected success"], mid["Gap that remains"]), ("33.0", "61.0", "16.5"))
        # Regression: the 0.25 share from 44.5 is 52.75 and 24.75, not the rounded 52.8 and a false 24.8.
        quarter = next(s for v, s in self.states("C26-D03") if v == ["Mean log-probability (44.5)", 0.25])
        self.assertIn("44.5 + 0.25 x 33.0 = 52.75, leaving 77.5 - 52.75 = 24.75 points", quarter["interpretation"])
        self.assertNotIn("52.8", quarter["interpretation"])
        self.assertNotIn("24.8", quarter["interpretation"])
        self.assertEqual(dict(quarter["metrics"])["New selected success"], "52.75")
        # The single-sample start is not a matched-bank gap and says so; the key explains both outlines.
        single = next(s for v, s in self.states("C26-D03") if v[0].startswith("Single") and v[1] == 0.5)
        self.assertIn("shown for scale", single["interpretation"])
        self.assertNotIn("as Equation (26.3) says", single["interpretation"])
        self.assertIn("as Equation (26.3) says", quarter["interpretation"])
        full = dict(next(s for v, s in self.states("C26-D03") if v == ["Mean log-probability (44.5)", 1.0])["metrics"])
        self.assertEqual(full["Gap that remains"], "0.0")

    def test_d04_exact_fits_and_limits(self):
        pts = [(10, 0.40), (25, 0.55), (50, 0.63)]

        def solve(curve_basis, lo, hi):
            # Find the shape number by bisection on the ratio of successive differences, independent of the module.
            target = (0.55 - 0.40) / (0.63 - 0.55)
            f = lambda p: (curve_basis(10, p) - curve_basis(25, p)) / (curve_basis(25, p) - curve_basis(50, p)) - target
            for _ in range(300):
                mid = (lo + hi) / 2
                lo, hi = (lo, mid) if f(lo) * f(mid) <= 0 else (mid, hi)
            p = (lo + hi) / 2
            b = 0.15 / (curve_basis(10, p) - curve_basis(25, p))
            a = 0.63 + b * curve_basis(50, p)
            return p, b, a

        exp = solve(lambda k, p: math.exp(-k / p), 1, 400)
        hyp = solve(lambda k, p: 1 / (k + p), 0.01, 200)
        pw = solve(lambda k, p: k ** -p, 0.01, 3)
        # The chapter's stated values.
        self.assertAlmostEqual(exp[0], 16.7, delta=0.05)
        self.assertAlmostEqual(hyp[0], 8.8, delta=0.05)
        self.assertAlmostEqual(pw[0], 0.43, delta=0.005)
        self.assertEqual([round(x[2], 2) for x in (exp, hyp, pw)], [0.65, 0.74, 0.86])
        # Hyperbolic closed form: h = 150 / 17 and A = 0.63 + B / (50 + h) with B = 0.15 / (1/(10+h) - 1/(25+h)).
        self.assertAlmostEqual(hyp[0], 150 / 17, places=6)
        # Every fit passes through all three points.
        for (p, b, a), basis in ((exp, lambda k, p: math.exp(-k / p)), (hyp, lambda k, p: 1 / (k + p)), (pw, lambda k, p: k ** -p)):
            for k, c in pts:
                self.assertAlmostEqual(a - b * basis(k, p), c, places=9)
        shown = {"Exponential approach": exp, "Hyperbolic approach": hyp, "Power-law approach": pw}
        for (family, horizon), state in self.states("C26-D04"):
            p, b, a = shown[family]
            m = dict(state["metrics"])
            self.assertEqual(m["Projected limit A"], f"{a:.3f}")
            self.assertEqual(m["Limits of all three families"], "0.65 / 0.74 / 0.86")
            self.assertEqual(m["Spread of the limits (points)"], f"{100 * (pw[2] - exp[2]):.0f}")
            basis = {"Exponential approach": lambda k: math.exp(-k / p), "Hyperbolic approach": lambda k: 1 / (k + p),
                     "Power-law approach": lambda k: k ** -p}[family]
            self.assertEqual(m[f"Curve at k = {int(horizon)}"], f"{a - b * basis(horizon):.3f}")

    def test_wording_fixes(self):
        self.assertIn("pass@k (coverage at k)", self.page)
        self.assertIn("per-task pass counts", self.page)
        self.assertIn("Euler", self.page)
        self.assertIn("all fitted", self.page)

    def test_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 26)
        text = (LAB.parent / "Manuscript" / "part-vi" / "26-how-much-more-could-the-system-become.md").read_text()

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".,;")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        inline = {norm(x) for x in re.findall(r"`([^`]+)`", text)}
        alts = [norm(html.unescape(a)) for a in re.findall(r'data-tex="([^"]+)"', self.page)]
        self.assertEqual(len(alts), 3)  # 26.1 to 26.3 as pre-rendered images; the curve formulas are inline TeX
        for a in alts:
            self.assertTrue(a in allowed or a in inline, a)
        flat = norm(html.unescape(self.page))
        for tex in (r"A - B e^{-k/\tau}", r"A - B/(k+h)", r"A - B k^{-a}"):
            self.assertIn(norm(tex), inline)
            self.assertIn(norm(tex), flat)

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
        run = subprocess.run(["node", str(HARNESS), str(self.path)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertGreaterEqual(report["states_checked"], 28)
        self.assertEqual(report["labelled_controls"], 8)


if __name__ == "__main__":
    unittest.main()

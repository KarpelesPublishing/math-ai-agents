"""Chapter 26 reader: independent hand checks.

Expected numbers are recomputed here from the chapter's own arithmetic (the
ten-candidate subset example, the three-task bank, the reported percentages,
and the three constructed saturation points), not read from the module.
"""
from __future__ import annotations

import html
import itertools
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
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 12, 6])
        self.assertLess(self.path.stat().st_size, 4_000_000)
        for text in ("Ask the chapter skill", "Common wrong turn", "What this does not settle", "Your prediction", "Worked steps"):
            self.assertIn(text, self.page)
        self.assertIn("Step 2 of 4", self.page)  # D01 stepper on the subset size
        for demo in self.data["demos"]:
            for state in demo["states"].values():
                self.assertGreaterEqual(len(state["steps"]), 2)

    def test_d01_finite_pool_coverage(self):
        pools = {"Chapter's worked pool (one task, 2 passing)": [2], "Low temperature (passes 8, 8, 0, 0)": [8, 8, 0, 0],
                 "High temperature (passes 3, 3, 2, 2)": [3, 3, 2, 2]}
        n = 10
        for (name, k), state in self.states("C26-D01"):
            k = int(k)
            counts = pools[name]
            cov = plug = sel = 0.0
            for c in counts:
                # enumerate every size-k subset of ten programs, the first c of which pass
                subsets = list(itertools.combinations(range(n), k))
                hit = sum(1 for sub in subsets if any(i < c for i in sub))
                cov += hit / len(subsets)
                plug += 1 - (1 - c / n) ** k
                sel += c / n
            t = len(counts)
            m = dict(state["metrics"])
            self.assertEqual(m[f"Exact coverage at k = {k}"], f"{cov / t:.4f}")
            self.assertEqual(m["Independent-draw formula"], f"{plug / t:.4f}")
            self.assertEqual(m["No-signal selector success"], f"{sel / t:.3f}")
            self.assertEqual(m["Tasks in the bank"], str(t))
            self.assertGreaterEqual(cov / t + 1e-12, plug / t)
            if k == 1:
                self.assertEqual(f"{cov / t:.4f}", f"{plug / t:.4f}")
        book = dict(next(s for v, s in self.states("C26-D01") if v[0].startswith("Chapter") and v[1] == 3)["metrics"])
        self.assertEqual(book["Exact coverage at k = 3"], "0.5333")
        self.assertEqual(book["Independent-draw formula"], "0.4880")
        self.assertEqual(book["Coverage not collected by that selector"], "0.3333")
        interp = next(s for v, s in self.states("C26-D01") if v[0].startswith("Chapter") and v[1] == 3)["interpretation"]
        self.assertIn("1 - C(8,3) / C(10,3) = 1 - 56 / 120 = 0.5333", interp)

    def test_d01_temperature_crossing_and_table(self):
        # k = 1: the concentrated bank leads; k = 5: the dispersed bank leads (the chapter's temperature direction)
        by = {}
        for (name, k), state in self.states("C26-D01"):
            by[(name.split()[0], int(k))] = float(dict(state["metrics"])[f"Exact coverage at k = {int(k)}"])
        self.assertGreater(by[("Low", 1)], by[("High", 1)])
        self.assertGreater(by[("High", 5)], by[("Low", 5)])
        # the chapter's table: 56 / 56 / 8 subsets with zero, one, two passes; 64 covered; uniform selector 24 of 120
        rows = [math.comb(2, j) * math.comb(8, 3 - j) for j in range(3)]
        self.assertEqual(rows, [56, 56, 8])
        self.assertEqual(sum(rows[1:]), 64)
        self.assertAlmostEqual((rows[1] / 3 + 2 * rows[2] / 3) / 120, 0.2)
        steps = next(s for v, s in self.states("C26-D01") if v[0].startswith("Chapter") and v[1] == 3)["steps"]
        self.assertTrue(any("0 passes: 56, 1 pass: 56, 2 passes: 8" in x for x in steps))

    def test_d02_ladder_by_hand_and_lab_cases(self):
        nb = lambda n: json.loads((LAB / "data" / "examples" / f"ch{n}.json").read_text())
        transfer = nb(26)
        self.assertEqual(transfer["selected_candidates"], [1, 1])
        self.assertEqual(transfer["deployment_allowed"], [True, False])
        banks = {"Three specialists (notebook default)": ([[1, 0, 0], [0, 1, 0], [0, 0, 1]], [0.2, 0.3, 0.5], [0, 0, 0], [0, 1, 2], [1, 1, 0]),
                 "First two specialists only": ([[1, 0, 0], [0, 1, 0]], [0.2, 0.3, 0.5], [0, 0, 0], [0, 1, 0], [1, 1, 0]),
                 "Two candidates, two tasks (notebook transfer)": ([[1, 1], [1, 0]], [0.5, 0.5], [1, 1], [0, 0], [1, 0])}
        for (bank, selector, deploy), state in self.states("C26-D02"):
            mat, w, dflt, orc, denied = banks[bank]
            chosen = dflt if selector.startswith("The notebook") else orc
            allowed = [1] * len(w) if deploy.startswith("Every") else denied
            cov = sum(w[t] for t in range(len(w)) if any(r[t] for r in mat))
            sel = sum(w[t] for t in range(len(w)) if mat[chosen[t]][t])
            dep = sum(w[t] for t in range(len(w)) if mat[chosen[t]][t] and allowed[t])
            m = dict(state["metrics"])
            self.assertEqual(m["Oracle coverage Cov"], f"{cov:.2f}")
            self.assertEqual(m["Actual selection Sel"], f"{sel:.2f}")
            self.assertEqual(m["Deployed success"], f"{dep:.2f}")
            self.assertEqual(m["Lost to selection (Cov minus Sel)"], f"{cov - sel:.2f}")
            self.assertEqual(m["Lost to deployment (Sel minus deployed)"], f"{sel - dep:.2f}")
            self.assertLessEqual(dep, sel + 1e-12)
            self.assertLessEqual(sel, cov + 1e-12)
            self.assertEqual("adds nothing to Cov" in state["interpretation"], any(not any(r[t] for r in mat) for t in range(len(w))))
        by_key = {k: dict(s["metrics"]) for k, s in self.demos["C26-D02"]["states"].items()}
        g = lambda key: tuple(by_key[key][x] for x in ("Oracle coverage Cov", "Actual selection Sel", "Deployed success"))
        self.assertEqual(g("0,0,0"), ("1.00", "0.20", "0.20"))      # notebook default
        self.assertEqual(g("0,1,1"), ("1.00", "1.00", "0.50"))      # notebook changed
        self.assertEqual(g("2,0,1"), ("1.00", "0.50", "0.50"))      # notebook transfer
        self.assertEqual(g("1,1,0"), ("0.50", "0.50", "0.50"))      # task 3 absent, nothing to select
        self.assertIn("task 3 absent from bank", by_key["1,0,0"]["Where each task stands"])
        self.assertEqual(by_key["1,0,0"]["Coverage as candidates are added"], "0.20 / 0.50")

    def test_d03_gap_and_hypothetical_share(self):
        pts = {"Codex-S, mean log-probability (44.5 of 77.5)": (44.5, 77.5, 1),
               "Codex-12B, one sample against pass@100 (28.81, 72.31)": (28.81, 72.31, 2),
               "Constructed: selector near the ceiling": (78.0, 80.0, 1),
               "Constructed: low ceiling": (15.0, 20.0, 1)}
        for (name, share), state in self.states("C26-D03"):
            sel, cov, d = pts[name]
            share = float(share)
            gap = cov - sel
            after = sel + share * gap
            m = dict(state["metrics"])
            self.assertEqual(m["Gap Cov minus Sel (points)"], f"{gap:.{d}f}")
            self.assertEqual(m["New selected success"], f"{after:.{d}f}")
            self.assertEqual(m["Gap that remains"], f"{cov - after:.{d}f}")
            self.assertAlmostEqual(cov - float(m["New selected success"]), float(m["Gap that remains"]), places=6)
            self.assertIn(f"{cov:.{d}f} - {m['New selected success']} = {m['Gap that remains']} points", state["interpretation"])
            self.assertGreaterEqual(gap, 0)
        mid = dict(next(s for v, s in self.states("C26-D03") if v[0].startswith("Codex-S") and v[1] == 0.5)["metrics"])
        self.assertEqual((mid["Gap Cov minus Sel (points)"], mid["New selected success"], mid["Gap that remains"]), ("33.0", "61.0", "16.5"))
        interp = next(s for v, s in self.states("C26-D03") if v[0].startswith("Codex-S") and v[1] == 0.5)["interpretation"]
        self.assertIn("44.5 - 37.7 = 6.8", interp)       # gain over a single sample, as the chapter reports
        self.assertIn("44.5 + 0.50 x 33.0 = 61.0", interp)
        c12 = next(s for v, s in self.states("C26-D03") if v[0].startswith("Codex-12B") and v[1] == 0)["interpretation"]
        self.assertIn("72.31 / 28.81 = 2.51", c12)        # the chapter's "about two and a half times"
        self.assertAlmostEqual(72.31 / 28.81, 2.51, places=2)
        full = dict(next(s for v, s in self.states("C26-D03") if v[0].startswith("Codex-S") and v[1] == 1.0)["metrics"])
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
        sel50 = {"0.60 (selector near the ceiling)": 0.60, "0.30 (selector far below it)": 0.30}
        for (family, selector), state in self.states("C26-D04"):
            p, b, a = shown[family]
            m = dict(state["metrics"])
            self.assertEqual(m["Projected limit A"], f"{a:.3f}")
            self.assertEqual(m["Limits of all three families"], "0.65 / 0.74 / 0.86")
            self.assertEqual(m["Spread of the limits (points)"], f"{100 * (pw[2] - exp[2]):.0f}")
            basis = {"Exponential approach": lambda k: math.exp(-k / p), "Hyperbolic approach": lambda k: 1 / (k + p),
                     "Power-law approach": lambda k: k ** -p}[family]
            at100 = a - b * basis(100)
            self.assertEqual(m["Curve at k = 100"], f"{at100:.3f}")
            self.assertEqual(m["Room from a larger bank (50 to 100)"], f"{at100 - 0.63:.3f}")
            self.assertEqual(m["Room below the ceiling at k = 50"], f"{0.63 - sel50[selector]:.3f}")
        # the larger room depends on the family when the selector is near the ceiling
        near = {}
        for (family, selector), state in self.states("C26-D04"):
            if selector.startswith("0.60"):
                m = dict(state["metrics"])
                near[family] = float(m["Room from a larger bank (50 to 100)"]) > float(m["Room below the ceiling at k = 50"])
        self.assertEqual(near, {"Exponential approach": False, "Hyperbolic approach": True, "Power-law approach": True})

    def test_c26_d04_verdict_matches_family_comparison(self):
        far_old = "under this family the selector has the larger room, and a different family could reverse that"
        for (family, selector), state in self.states("C26-D04"):
            text = state["interpretation"]
            self.assertNotIn(far_old, text)
            self.assertNotIn("a different family could reverse that", text)
            if selector.startswith("0.30"):
                self.assertIn("all three families agree that the selector has the larger room", text)
            else:
                self.assertIn("the families disagree at this selector value: a larger bank has the larger room under the hyperbolic and power-law curves, "
                              "the selector under the exponential curve", text)

    def test_minor_wording_patch2(self):
        equal_seen = 0
        for state in self.demos["C26-D01"]["states"].values():
            m = dict(state["metrics"])
            text = state["interpretation"]
            if m.get("Exact coverage at k = 1") is None and "Independent-draw formula" in m and len(m) > 4:
                pass
            exact = [v for key, v in m.items() if key.startswith("Exact coverage") or key.startswith("Mean coverage")]
            plug = m.get("Independent-draw formula")
            if exact and plug is not None and exact[0] == plug and "which differs from the exact mean" in text:
                self.fail("claims a difference that prints equal: " + text)
            if "matches the exact mean to four decimals" in text:
                equal_seen += 1
                self.assertEqual(exact[0], plug)
        self.assertGreater(equal_seen, 0)
        codex12 = [s["interpretation"] for s in self.demos["C26-D03"]["states"].values() if "two and a half times" in s["interpretation"]]
        self.assertTrue(codex12)
        for text in codex12:
            self.assertNotIn("as Equation (26.3) says", text)

    def test_wording_fixes(self):
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
        self.assertEqual(report["states_checked"], 42)


if __name__ == "__main__":
    unittest.main()

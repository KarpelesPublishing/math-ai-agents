"""Chapter 16 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(Equations 16.1 to 16.5, the sixty-unit construction, the three constructed
procedures), not read back from the module that produced the page. The test
builds the reader into a private temporary directory, so it never touches the
committed readers folder.
"""
from __future__ import annotations

import hashlib
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
SLUG = "16-sample-allocation"


def _builder_python():
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers.builder_python()


PYTHON = _builder_python()
_CACHE = {}


def build(tag):
    out = tempfile.mkdtemp(prefix=f"readers-ch16-{tag}-")
    run = subprocess.run([PYTHON, str(WRAPPER), "--chapters", "16", "--out", out], capture_output=True, text=True,
                         timeout=900, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    if run.returncode != 0:
        raise RuntimeError(run.stdout + run.stderr)
    return Path(out)


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


def cov(p, k):
    return 1 - (1 - p) ** k


@unittest.skipIf(PYTHON is None, "no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
class Chapter16ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.out = build("a")
        cls.reader = cls.out / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.out, ignore_errors=True)

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)]
            yield values, dict(state["metrics"]), state

    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C16-D01", "C16-D02", "C16-D03", "C16-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 8, 8, 6])

    def test_size_budget(self):
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_coverage_blind_selection_and_marginal_gain(self):
        for (p, k), m, state in self.states("C16-D01"):
            k = int(k)
            c = 1 - (1 - p) ** k
            gain = p * (1 - p) ** k
            self.assertEqual(m["Coverage Cov(k)"], f"{c:.4f}")
            self.assertEqual(m["Blind selection Sel(k)"], f"{p:.2f}")
            self.assertEqual(m["Gap a selector could close"], f"{c - p:.4f}")
            shown = m[f"Gain from sample {k + 1}"]
            self.assertEqual(shown, f"{gain:.4f}" if gain >= 1e-4 else f"{gain:.1e}")
            # Equation (16.4) against the difference of two coverages, computed independently
            self.assertAlmostEqual(gain, (1 - (1 - p) ** (k + 1)) - c, places=12)
            self.assertIn(f"Cov({k}) = 1 - (1 - {p:.2f})^{k}", state["interpretation"])
        # the chapter's own numbers: 0.89 and 0.99 at p = 0.2; 0.40 and 0.99 at p = 0.05
        book = {(0.2, 10): "0.8926", (0.2, 20): "0.9885", (0.05, 10): "0.4013", (0.05, 100): "0.9941"}
        for (p, k), m, _ in self.states("C16-D01"):
            if (p, int(k)) in book:
                self.assertEqual(m["Coverage Cov(k)"], book[(p, int(k))])
        self.assertAlmostEqual(0.3 * 0.7 ** 4, 0.07203)  # the chapter's "fifth sample buys 0.07" at p = 0.3

    def test_d02_selector_by_hand_and_dependence_boundary(self):
        p = 0.4
        for (q, kind), m, state in self.states("C16-D02"):
            shared = "shared" in str(kind).lower()
            covered = p if shared else cov(p, 5)
            # under one shared failure a bank with a correct sample holds only correct samples, so the
            # selector's conditional success is 1 whatever its setting: selected = coverage = p
            selected = covered if shared else covered * q
            self.assertEqual(m["Coverage at k = 5"], f"{covered:.4f}", (q, kind))
            self.assertEqual(m["Selected success at k = 5"], f"{selected:.4f}", (q, kind))
            self.assertEqual(m["Selected minus blind"], f"{selected - p:.4f}", (q, kind))
        # notebook case: 0.4 coverage base, 5 samples, selector 0.9: 0.92224 and 0.830016
        independent_09 = next(m for v, m, _ in self.states("C16-D02") if v[0] == 0.9 and "ndependent" in str(v[1]))
        self.assertEqual((independent_09["Coverage at k = 5"], independent_09["Selected success at k = 5"]), ("0.9222", "0.8300"))
        self.assertAlmostEqual(1 - 0.6 ** 5, 0.92224)
        self.assertAlmostEqual(0.92224 * 0.9, 0.830016)
        # shared failure: the selector setting is irrelevant, delivery equals blind selection exactly
        for (q, kind), m, st in self.states("C16-D02"):
            if "hared" in str(kind):
                self.assertEqual(m["Selected success at k = 5"], "0.4000")
                self.assertEqual(m["Selected minus blind"], "0.0000")
                text = st["interpretation"]
                self.assertIn("0.40 x 1 + (1 - 0.40) x 0 = 0.4000", text)
                self.assertIn("is not used", text)
                self.assertIn("exactly as good as five", text)
                # regression: the old, inconsistent claims are gone
                self.assertNotIn("can only lose", text)
                self.assertNotIn("at least as good as five", text)
                self.assertNotIn(f"0.40 x {q:.2f} + (1 - 0.40) x 0", text)
                for old in ("0.2000", "0.3000", "0.3600"):
                    if q < 0.9:
                        self.assertNotEqual(m["Selected success at k = 5"], old)
        # the independent states credit both factors, not the selector alone
        for (q, kind), m, st in self.states("C16-D02"):
            if "ndependent" in str(kind):
                self.assertNotIn("The selector, not the sampling, opened the gap", st["interpretation"])
        beat = next(s for v, m, s in self.states("C16-D02") if v[0] == 0.9 and "ndependent" in str(v[1]))
        self.assertIn("The gap needs both: samples to put a correct answer in the bank, and a selector to find it.",
                      beat["interpretation"])
        # a perfect selector under shared failure ties blind selection exactly (the merged-label case)
        tie = next(m for v, m, _ in self.states("C16-D02") if v[0] == 1.0 and "hared" in str(v[1]))
        self.assertEqual(tie["Selected minus blind"], "0.0000")
        # a half-reliable selector with two samples falls below blind selection: 0.64 x 0.5 = 0.32
        low = next(s for v, m, s in self.states("C16-D02") if v[0] == 0.5 and "ndependent" in str(v[1]))
        self.assertIn("0.64 x 0.50 = 0.32", low["interpretation"])
        self.assertAlmostEqual(cov(0.4, 2) * 0.5, 0.32)

    def test_d02_reader_passes_the_selector_setting_to_the_lab_unchanged(self):
        # The laboratory function now handles the shared failure itself, so the reader no longer
        # substitutes a perfect selector for that state.
        source = (LAB / "tools" / "readers" / "chapters" / "ch16.py").read_text(encoding="utf-8")
        self.assertNotIn("1.0 if shared", source)
        self.assertIn('"selector_accuracy": float(selector)', source)

    def test_d03_sixty_unit_allocations(self):
        cases = {"Book values: 0.73 and 0.785": (0.73, 0.785), "Strong: 0.95 for both": (0.95, 0.95),
                 "Weak: 0.50 for both": (0.5, 0.5), "Worse than random: 0.15 for both": (0.15, 0.15)}
        for (case, long_p), m, state in self.states("C16-D03"):
            pi3, pi4 = cases[case]
            expected = [long_p, 0.2, (1 - 0.8 ** 48) * pi3, (1 - (1 - long_p) ** 12) * pi4]
            self.assertEqual([m["All on length"], m["All on volume"], m["Volume + selector"], m["Length + selector"]],
                             [f"{v:.3f}" for v in expected], (case, long_p))
            best = max(expected)
            winners = [n for n, v in zip(("All on length", "All on volume", "Volume + selector", "Length + selector"), expected)
                       if abs(v - best) < 1e-9]
            self.assertEqual(m["Best allocation"], " and ".join(winners))
        # the book's own figures: 0.35, 0.20, about 0.73 and about 0.78; coverage 0.99998 and 0.994
        book = next(m for v, m, _ in self.states("C16-D03") if v == ["Book values: 0.73 and 0.785", 0.35])
        self.assertEqual((book["All on length"], book["All on volume"], book["Volume + selector"], book["Length + selector"]),
                         ("0.350", "0.200", "0.730", "0.781"))
        self.assertEqual(round((1 - 0.65 ** 12) * 0.785, 2), 0.78)  # the book says roughly 0.78
        self.assertAlmostEqual(1 - 0.8 ** 48, 0.99998, places=5)
        self.assertAlmostEqual(1 - 0.65 ** 12, 0.994, places=3)
        # budget arithmetic of the four allocations: 15 x 4, 60 x 1, 48 + 12, 12 x 4 + 3
        self.assertEqual((15 * 4, 60 * 1, 48 * 1 + 48 * 0.25, 12 * 4 + 12 * 0.25), (60, 60, 60, 51))
        # a selector worse than random loses to its blind counterpart
        worse = next(m for v, m, _ in self.states("C16-D03") if v == ["Worse than random: 0.15 for both", 0.35])
        self.assertEqual(worse["Best allocation"], "All on length")
        # both selector allocations fall below their blind counterparts (0.150 < 0.200, 0.149 < 0.350)
        for long_p in (0.35, 0.25):
            st = next(s for v, m, s in self.states("C16-D03") if v == ["Worse than random: 0.15 for both", long_p])
            self.assertIn("Both selector allocations fall below their blind counterparts", st["interpretation"])
            self.assertNotIn("At least one", st["interpretation"])
        # the unequal spend is stated: allocation 4 uses 51 of the 60 units and leaves 9
        for _, _, st in self.states("C16-D03"):
            self.assertIn("12 x 4 + 12 x 0.25 = 51 units and leaves 9 unspent", st["interpretation"])

    def test_d04_cost_per_success_and_feasibility(self):
        procs = {"A": (1.0, 0.60, 1.0), "B": (1.5, 0.80, 2.0), "C": (2.0, 0.85, 5.0)}
        for (deadline, need), m, state in self.states("C16-D04"):
            feasible = [n for n, (c, r, t) in procs.items() if r >= need and t <= deadline]
            per_success = {n: (100 * c) / (100 * r) for n, (c, r, t) in procs.items()}
            for n in procs:
                self.assertEqual(m[f"Cost per success {n}"], f"{per_success[n]:.2f}")
            self.assertEqual(m["Feasible procedures"], ", ".join(feasible) if feasible else "none")
            if feasible:
                cheapest = min(feasible, key=lambda n: per_success[n])
                loss = {n: c + (1 - r) * 20 for n, (c, r, t) in procs.items()}
                self.assertEqual(m["Cheapest per success among feasible"], cheapest)
                self.assertEqual(m["Lowest cost plus failure loss (20 per failure)"], min(feasible, key=lambda n: loss[n]))
            else:
                self.assertTrue(m["Cheapest per success among feasible"].startswith("undefined"))
        # the chapter's numbers: 1.6667, 1.875, 2.3529; 5.5 and 5 with a loss of 20 per failure
        self.assertAlmostEqual(100 / 60, 1.6667, places=4)
        self.assertAlmostEqual(150 / 80, 1.875)
        self.assertAlmostEqual(200 / 85, 2.3529, places=4)
        self.assertAlmostEqual(1.5 + 0.2 * 20, 5.5)
        self.assertAlmostEqual(2 + 0.15 * 20, 5.0)
        # 3 seconds and 0.75: only B. 3 seconds and 0.82: nobody. 10 seconds and 0.82: only C.
        by = {tuple(v): m for v, m, _ in self.states("C16-D04")}
        self.assertEqual(by[(3, 0.75)]["Feasible procedures"], "B")
        self.assertEqual(by[(3, 0.82)]["Feasible procedures"], "none")
        self.assertEqual(by[(10, 0.82)]["Feasible procedures"], "C")
        self.assertEqual(by[(10, 0.5)]["Cheapest per success among feasible"], "A")
        self.assertEqual(by[(10, 0.75)]["Lowest cost plus failure loss (20 per failure)"], "C")
        self.assertEqual(by[(3, 0.75)]["Cheapest per success among feasible"], "B")
        # the unconditional comparison: A is lowest of the three whatever the constraints
        for m in by.values():
            self.assertEqual(m["Cheapest per success overall"], "A")
        self.assertIn("lowest of the three cost-per-success values", self.page)
        self.assertNotIn("Is it the cheapest per success?", self.page)

    def test_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 16)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".,;")

        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        shown = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertGreaterEqual(len(shown), 8)
        for tex in shown:
            self.assertIn(norm(html.unescape(tex)), allowed)
        # g6-10: the alt text names the equation by number instead of being raw TeX alone
        alts = re.findall(r'<p class="equation"><img [^>]*alt="([^"]+)"', self.page)
        self.assertEqual(len(alts), len(shown))
        numbers = {e["number"] for e in chapter["equations"]}
        for alt in alts:
            match = re.match(r"Equation \((16\.\d)\), written in LaTeX: ", html.unescape(alt))
            self.assertIsNotNone(match, alt)
            self.assertIn(match.group(1), numbers)
        # g6-17: equation images are sized by width and may shrink to the column
        self.assertNotIn("max-width:none", self.page)
        self.assertIn(".equation img{display:block;max-width:100%;height:auto", self.page)

    def test_links_and_offline(self):
        for href in ("../../notebooks/16-sample-allocation.ipynb", "../../skills/maa-16-sample-allocation/SKILL.md"):
            self.assertIn(f'href="{href}"', self.page)
            self.assertTrue((self.reader.parent / href).resolve().exists() or
                            (LAB / href.replace("../../", "")).exists(), href)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

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
        self.assertNotRegex(text, r"\b(nan|inf)\b")

    def test_accessibility_basics(self):
        self.assertIn('<a class="skip" href="#main">', self.page)
        self.assertIn("<noscript>", self.page)
        self.assertEqual(self.page.count('aria-live="polite"'), 4)
        for d in self.data["demos"]:
            for c in d["controls"]:
                self.assertIn(f'<label for="{d["id"]}-{c["key"]}">', self.page)

    def test_every_control_combination_renders_with_labelled_axes(self):
        script = (
            "import importlib.util, itertools, sys\n"
            f"sys.path[:0] = [{str(LAB / 'tools' / 'readers' / 'engine')!r}, {str(LAB / 'src')!r}]\n"
            "import matplotlib; matplotlib.use('Agg')\n"
            "import matplotlib.pyplot as plt\n"
            f"spec = importlib.util.spec_from_file_location('ch16m', {str(LAB / 'tools' / 'readers' / 'chapters' / 'ch16.py')!r})\n"
            "m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\n"
            "n = 0\n"
            "for demo in m.CHAPTER['demos']:\n"
            "    f = getattr(m, demo['function'])\n"
            "    for combo in itertools.product(*[c['values'] for c in demo['controls']]):\n"
            "        fig, metrics, text = f(**{c['key']: v for c, v in zip(demo['controls'], combo)})\n"
            "        assert metrics and text\n"
            "        for ax in fig.axes:\n"
            "            assert ax.get_xlabel() and ax.get_ylabel(), (demo['id'], combo)\n"
            "        plt.close(fig); n += 1\n"
            "print(n)\n"
        )
        run = subprocess.run([PYTHON, "-c", script], capture_output=True, text=True, timeout=300)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.strip(), str(8 + 8 + 8 + 6))

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=180)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (30, 4, 8))

    def test_build_is_reproducible(self):
        other = build("b")
        try:
            fresh = other / SLUG / "reader.html"
            self.assertEqual(hashlib.sha256(fresh.read_bytes()).hexdigest(), hashlib.sha256(self.reader.read_bytes()).hexdigest())
        finally:
            shutil.rmtree(other, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

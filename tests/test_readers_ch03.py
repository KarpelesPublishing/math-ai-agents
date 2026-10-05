"""Chapter 3 laboratory reader: independent hand checks of the built page.

Every expected number below is recomputed here with separate arithmetic (exact
fractions, a closed-form two-parameter solve, closed-form least squares), not
read back from the module that produced the page. The tests build Chapter 3
into a private temporary folder, so they never touch the committed readers.
"""
from __future__ import annotations

import html
import importlib.util
import json
import math
import os
from fractions import Fraction
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


def _builder_python():
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


def norm(text):
    text = re.sub(r"\\tag\{[^}]*\}", "", text)
    text = re.sub(r"\\(?:,|;|:|!|quad|qquad)", "", text)
    return re.sub(r"[\s{}]", "", text)


class Chapter3ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        python = _builder_python()
        if python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([python, str(WRAPPER), "--chapters", "3", "--out", cls.tmp.name], capture_output=True, text=True,
                             timeout=900, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = next(Path(cls.tmp.name).glob("03-*/reader.html"))
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def states(self, demo_id):
        """Yield (control indices, metrics, interpretation)."""
        for key, state in self.demos[demo_id]["states"].items():
            yield tuple(int(i) for i in key.split(",")), dict(state["metrics"]), state["interpretation"]

    def text(self, demo_id, key):
        return self.demos[demo_id]["states"][key]["interpretation"]

    # structure

    def test_four_demonstrations_all_combinations_render(self):
        self.assertEqual(list(self.demos), ["C03-D01", "C03-D02", "C03-D03", "C03-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 8, 12])
        for demo in self.data["demos"]:
            expected = 1
            for control in demo["controls"]:
                expected *= len(control["values"])
            self.assertEqual(len(demo["states"]), expected)
            for state in demo["states"].values():
                self.assertGreaterEqual(len(state["steps"]), 2)
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 3)
        text = (LAB.parent / chapter["source_path"]).read_text(encoding="utf-8")
        self.assertNotIn("Manuscript/chapters/", chapter["source_path"])
        # Read the equation strings from the page itself (alt text or TeX source), not from the module.
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 3)  # (3.1), (3.3) and (3.2) are pre-rendered; the slope line is typeset from its TeX
        body = norm(text)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)).rstrip(".,;"), body, tex)
        slope = "[(1-2)(0.10-0.20)+(3-2)(0.29-0.20)]/2=0.095"
        self.assertIn(slope, html.unescape(self.page))
        self.assertIn(norm(slope), body)

    def test_source_sections_exist_in_the_canonical_chapter(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 3)
        text = (LAB.parent / chapter["source_path"]).read_text(encoding="utf-8")
        headings = {m.group(2).strip() for m in re.finditer(r"^(#{1,3})\s+(.*)$", text, re.M)}
        for name in ("The forecast model", "A constructed forecast example", "Smooth ability, abrupt score", "The eight-step protocol"):
            self.assertIn(name, headings)

    # Demonstration 1: Equation (3.1)

    @staticmethod
    def solve_a_c(us, ys):
        """Closed-form least squares for y = a u + c (two unknowns, normal equations)."""
        n = len(us)
        su, sy = sum(us), sum(ys)
        suu = sum(u * u for u in us)
        suy = sum(u * y for u, y in zip(us, ys))
        a = (n * suy - su * sy) / (n * suu - su * su)
        return a, (sy - a * su) / n

    def independent_forecast(self, decades, runs):
        pattern = {"exact": [0, 0, 0, 0, 0], "wiggle": [0.04, -0.04, -0.04, 0.04, 0.04], "silent": [0, 0, 0, 0.10, 0.10]}[runs]
        xs = [-decades - 2 + 0.5 * i for i in range(5)]
        ys = [1.5 * 10 ** (-0.15 * x) + 1.0 + p for x, p in zip(xs, pattern)]
        best = None
        for k in range(10, 1001):
            b = -k / 1000
            us = [10 ** (b * x) for x in xs]
            a, c = self.solve_a_c(us, ys)
            sse = sum((a * u + c - y) ** 2 for u, y in zip(us, ys))
            if best is None or sse < best[0] - 1e-15:
                best = (sse, b, a, c)
        _, b, a, c = best
        return b, a, c, a + c

    def test_d01_forecast_and_residual(self):
        runs_of = ["exact", "wiggle", "silent"]
        residuals = {}
        for (di, ri), m, interp in self.states("C03-D01"):
            decades, runs = di + 1, runs_of[ri]
            b, a, c, forecast = self.independent_forecast(decades, runs)
            self.assertEqual(m["Observed later (constructed true value)"], "2.500")
            self.assertAlmostEqual(float(m["Forecast at the held-out run"]), forecast, delta=0.0011)
            self.assertAlmostEqual(float(m["Residual, observed minus forecast"]), 2.5 - forecast, delta=0.0011)
            self.assertEqual(m["Fitted a, b, c"].split(", ")[1], f"{b:.3f}")
            residuals[(decades, runs)] = float(m["Residual, observed minus forecast"])
            if runs != "exact":
                self.assertIn(f"a = {a:.3f} and c = {c:.3f} against the true 1.5 and 1.0", interp)
        for d in (1, 2, 3, 4):
            self.assertEqual(residuals[(d, "exact")], 0.0)
        for runs in ("wiggle", "silent"):
            sizes = [abs(residuals[(d, runs)]) for d in (1, 2, 3, 4)]
            self.assertEqual(sizes, sorted(sizes))
        self.assertGreater(abs(residuals[(4, "wiggle")]), 2 * abs(residuals[(1, "wiggle")]))
        self.assertIn("trained differently and nobody recorded the difference", self.text("C03-D01", "1,2"))
        self.assertIn("1.500 + 1.000 = 2.500", self.text("C03-D01", "2,0"))
        self.assertEqual(self.demos["C03-D01"]["predict"]["answer"], 0)

    def test_d01_mechanism_sentence_matches_the_displayed_numbers(self):
        errors, misses = [], []
        for d in (1, 2, 3, 4):
            b, a, c, forecast = self.independent_forecast(d, "wiggle")
            errors.append(abs(b - (-0.15)))
            misses.append(abs(2.5 - forecast))
        self.assertEqual(errors, sorted(errors, reverse=True))
        self.assertEqual(misses, sorted(misses))
        self.assertNotIn("multiplied across", self.page)
        self.assertIn("Across the four distances the miss grows for this wiggle pattern", self.text("C03-D01", "0,1"))

    def test_d04_symbols_define_psi_and_the_plotted_score(self):
        text = html.unescape(self.page)
        self.assertIn("f_psi in Equation (3.2), where psi stands for the line's fitted intercept and slope", text)
        self.assertIn("the plotted score stands in for the quantity Gamma_m", text)

    # Demonstration 2: the chapter's constructed forecast, the commitment boundary and what a rewrite does

    def test_d02_interval_by_exact_fractions(self):
        xs = [Fraction(1), Fraction(2), Fraction(3)]
        ys = [Fraction("0.10"), Fraction("0.21"), Fraction("0.29")]
        xbar, ybar = sum(xs) / 3, sum(ys) / 3
        slope = sum((x - xbar) * (y - ybar) for x, y in zip(xs, ys)) / sum((x - xbar) ** 2 for x in xs)
        intercept = ybar - slope * xbar
        forecast = intercept + slope * 4
        self.assertEqual((xbar, ybar, slope, intercept, forecast), (2, Fraction("0.20"), Fraction("0.095"), Fraction("0.01"), Fraction("0.39")))
        weights = [Fraction(1, 3) + (4 - xbar) * (x - xbar) / sum((v - xbar) ** 2 for v in xs) for x in xs]
        self.assertEqual(weights, [Fraction(-2, 3), Fraction(1, 3), Fraction(4, 3)])
        observed_values = ["0.30", "0.36", "0.43", "0.50"]
        d = Fraction("0.02")
        half = sum(abs(w) for w in weights) * d + d
        low, high = forecast - half, forecast + half
        for (oi, ci), m, interp in self.states("C03-D02"):
            obs = Fraction(observed_values[oi])
            self.assertEqual(m["Registered interval"], f"{float(low):.6f} to {float(high):.6f}")
            self.assertEqual(m["Registered point forecast at x = 4"], "0.39")
            self.assertEqual(m["Residual against the registered forecast"], f"{float(obs - forecast):.2f}".replace("-0.00", "0.00"))
            self.assertEqual(m["Inside the registered interval"], "yes" if low <= obs <= high else "no")
            # Refit through all four points by exact fractions.
            pts = [(Fraction(1), ys[0]), (Fraction(2), ys[1]), (Fraction(3), ys[2]), (Fraction(4), obs)]
            xb, yb = Fraction(5, 2), sum(p[1] for p in pts) / 4
            s4 = sum((x - xb) * (y - yb) for x, y in pts) / sum((x - xb) ** 2 for x, _ in pts)
            fit4 = yb + s4 * (4 - xb)
            if ci == 1:
                self.assertEqual(m["Refit forecast after the result"], f"{float(fit4):.3f}")
                self.assertEqual(m["Residual against the refit"], f"{float(obs - fit4):.3f}")
                self.assertLess(abs(obs - fit4), abs(obs - forecast))  # the refit always looks better
            if ci == 2:
                pad = abs(obs - forecast)
                self.assertEqual(m["Interval written after the result"], f"{float(forecast - pad):.2f} to {float(forecast + pad):.2f}")
                self.assertEqual(m["Contains the observed value"], "yes, by construction")
        book = dict(self.demos["C03-D02"]["states"]["2,0"]["metrics"])
        self.assertEqual(book["Registered interval"], "0.323333 to 0.456667")
        self.assertEqual((book["Residual against the registered forecast"], book["Inside the registered interval"]), ("0.04", "yes"))
        outcomes = [dict(self.demos["C03-D02"]["states"][f"{i},0"]["metrics"])["Inside the registered interval"] for i in range(4)]
        self.assertEqual(outcomes, ["no", "yes", "yes", "no"])
        self.assertIn("0.2575 + 1.5 x 0.107 = 0.418", self.text("C03-D02", "2,1"))
        self.assertEqual(self.demos["C03-D02"]["predict"]["answer"], 0)

    def test_d02_check_question_answer(self):
        high = 0.39 + (7 / 3 + 1) * 0.02  # 0.456667
        self.assertAlmostEqual(high, 0.456667, places=6)
        self.assertGreater(0.46, high)
        self.assertEqual(round(0.46 - 0.39, 2), 0.07)

    # Demonstration 3: Equation (3.3)

    def test_d03_first_pass_and_one_step_changes(self):
        def q_of(profile, m):
            if profile == "latent":
                return Fraction(5, 100) + Fraction(3, 100) * (m - 1)
            if profile == "jump":
                return Fraction(1, 10) + Fraction(1, 10) * (m - 1)
            if profile == "onset":
                return 1 / (1 + math.exp(-2.5 * (m - 5)))
            return Fraction(2, 10)
        names = ["latent", "jump", "onset", "none"]
        for (pi, ti), m, interp in self.states("C03-D03"):
            profile, tau = names[pi], [0.5, 0.8][ti]
            qs = [q_of(profile, k) for k in range(1, 10)]
            # Equation (3.3): pass when q is at least tau (exact comparison; a tie passes).
            verdicts = [1 if q >= Fraction(str(tau)) else 0 for q in qs]
            first = next((k for k, v in zip(range(1, 10), verdicts) if v), None)
            self.assertEqual(m["First member that passes"], "none in this range" if first is None else f"m = {first}")
            self.assertEqual(m["Largest one-step change in q"], f"{max(abs(float(b) - float(a)) for a, b in zip(qs, qs[1:])):.3f}")
            self.assertEqual(m["Largest one-step change in the verdict"], str(max(abs(b - a) for a, b in zip(verdicts, verdicts[1:]))))
        # Tie at the threshold: q(5) = 0.5 exactly and the member passes.
        jump = next((m, i) for v, m, i in self.states("C03-D03") if v == (1, 0))
        self.assertEqual(jump[0]["First member that passes"], "m = 5")
        self.assertIn("0.1 + 0.1 x 4 = 0.50 >= 0.50", jump[1])
        self.assertIn("reaches the threshold exactly", jump[1])
        onset = next(m for v, m, _ in self.states("C03-D03") if v == (2, 0))
        self.assertEqual(onset["First member that passes"], "m = 5")
        # The sharp rise: q changes by 1/(1+e^2.5) to 1/2 between members 4 and 5.
        self.assertEqual(onset["Largest one-step change in q"], f"{0.5 - 1 / (1 + math.exp(2.5)):.3f}")

    def test_d03_flat_cases_say_never(self):
        for (pi, ti), m, interp in self.states("C03-D03"):
            if pi in (0, 3):
                self.assertEqual(m["First member that passes"], "none in this range")
                self.assertIn("verdict is 0 at every member", interp)
        latent = next(i for v, _, i in self.states("C03-D03") if v == (0, 0))
        self.assertIn("0.05 + 0.03 x 8 = 0.29", latent)  # 0.05 + 0.24

    def test_d03_check_question_answer(self):
        q = lambda m: Fraction(1, 10) + Fraction(1, 10) * (m - 1)
        self.assertEqual([m for m in range(1, 10) if q(m) >= Fraction("0.65")][0], 7)
        self.assertEqual((q(7), q(6)), (Fraction(7, 10), Fraction(6, 10)))

    # Demonstration 4: Equation (3.2) with the laboratory's frozen forecast

    @staticmethod
    def fit(family, xs, ys):
        z = [math.log(x) for x in xs] if family == "log" else list(xs)
        zbar, ybar = sum(z) / len(z), sum(ys) / len(ys)
        slope = sum((a - zbar) * (b - ybar) for a, b in zip(z, ys)) / sum((a - zbar) ** 2 for a in z)
        return slope, ybar - slope * zbar

    def test_d04_frozen_forecast_by_closed_form(self):
        data = [([1, 2, 3], [0.2, 0.3, 0.4], [4, 5], [[0.5, 0.6], [0.8, 0.95], [0.45, 0.48]]),
                ([1, 2, 4], [0.0, 0.69314718056, 1.38629436112], [8, 16],
                 [[2.07944154168, 2.77258872224], [2.5, 3.5], [1.8, 2.0]])]
        families = ["linear", "log"]
        rmse = {}
        for (di, fi, oi), m, interp in self.states("C03-D04"):
            dev_x, dev_y, test_x, outs = data[di]
            family, test_y = families[fi], outs[oi]
            slope, intercept = self.fit(family, dev_x, dev_y)
            f = (lambda v: math.log(v)) if family == "log" else (lambda v: v)
            forecast = [intercept + slope * f(x) for x in test_x]
            residuals = [o - p for o, p in zip(test_y, forecast)]
            value = math.sqrt(sum(r * r for r in residuals) / 2)
            rmse[(di, family, oi)] = value
            t0, t1 = test_x
            self.assertEqual(m[f"Frozen forecast at {t0} and {t1}"], f"{forecast[0]:.3f}, {forecast[1]:.3f}")
            self.assertEqual(m["Residuals, observed minus forecast"], f"{residuals[0]:.3f}, {residuals[1]:.3f}".replace("-0.000", "0.000"))
            self.assertEqual(m["Test RMSE"], f"{value:.3f}")
            self.assertEqual(m["Fitted slope and intercept"], f"{slope:.4f}, {intercept:.4f}".replace("-0.0000", "0.0000"))
        for di in (0, 1):
            for oi in (0, 1, 2):
                for family, other in (("linear", "log"), ("log", "linear")):
                    key = f"{di},{families.index(family)},{oi}"
                    state = dict(self.demos["C03-D04"]["states"][key]["metrics"])
                    best = family if rmse[(di, family, oi)] <= rmse[(di, other, oi)] + 1e-9 else other
                    self.assertEqual(state["Family that fits best after the fact"], best, key)
        slopes = {m["Fitted slope and intercept"] for v, m, _ in self.states("C03-D04") if v[0] == 0 and v[1] == 0}
        self.assertEqual(slopes, {"0.1000, 0.1000"})
        changed = dict(self.demos["C03-D04"]["states"]["0,0,1"]["metrics"])
        self.assertEqual(changed["Residuals, observed minus forecast"], "0.300, 0.350")
        self.assertEqual(changed["Mean residual (bias)"], "0.325")
        # Transfer: log family on log-shaped data reproduces the laboratory's example, 2.0794 and 2.7726, with RMSE 0.
        exact = dict(self.demos["C03-D04"]["states"]["1,1,0"]["metrics"])
        self.assertEqual(exact["Frozen forecast at 8 and 16"], "2.079, 2.773")
        self.assertEqual(exact["Test RMSE"], "0.000")
        self.assertEqual(exact["Fitted slope and intercept"], "1.0000, 0.0000")
        self.assertEqual(self.demos["C03-D04"]["predict"]["answer"], 0)

    def test_d04_retrospective_choice_is_named(self):
        lost = self.text("C03-D04", "0,0,2")
        self.assertIn("log family would have fitted better", lost)
        self.assertIn("retrospective fit", lost)

    def test_d04_check_question_answer(self):
        slope, intercept = self.fit("log", [1, 2, 3], [0.2, 0.3, 0.4])
        self.assertEqual((f"{slope:.4f}", f"{intercept:.4f}"), ("0.1780", "0.1937"))
        self.assertEqual(f"{intercept + slope * math.log(4):.3f}", "0.440")

    def test_patch2_wording_fixes(self):
        # g1-15: default is the wiggle case, so distance matters on first view.
        runs = next(c for c in self.demos["C03-D01"]["controls"] if c["key"] == "runs")
        self.assertEqual(runs["default"], 1)
        self.assertIn("(the default)", self.page)
        # g1-16: transfer calculation prints observed values to four decimals and parenthesises the negative intercept.
        text = self.text("C03-D04", "1,0,0")
        self.assertNotIn("+ -", text)
        self.assertIn("(-0.3466)", text)
        self.assertIn("Residual at 8 = 2.0794 - 3.218 = -1.139", text)
        self.assertIn("at 16 = 2.7726 - 6.783 = -4.010", text)
        self.assertEqual((round(2.0794 - 3.218, 3), round(2.7726 - 6.783, 3)), (-1.139, -4.010))
        # g1-18: scope note on D04 taken from the chapter's 'What this does not settle'.
        self.assertIn("The worked forecast numbers are constructed.", self.page)

    def test_optional_panels_present(self):
        self.assertIn("Ask the chapter skill", self.page)
        self.assertIn("maa-03-prospective-forecast", self.page)
        self.assertGreaterEqual(self.page.count("Chapter 3 source:"), 3)
        self.assertGreaterEqual(self.page.count("Common wrong turn"), 4)

    # text rules and page checks

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for demo in self.data["demos"]:
            for state in demo["states"].values():
                text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter", "scipy"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_every_state_has_a_hand_calculation(self):
        pattern = re.compile(r"\(?-?\d+(?:\.\d+)?\)?\s*(?:[x*/+]|\s-\s)\s*\(?-?\d+(?:\.\d+)?\)?[^=]{0,160}=\s*\(?-?\d")
        for demo in self.data["demos"]:
            for key, state in demo["states"].items():
                self.assertRegex(state["interpretation"], pattern, (demo["id"], key))

    def test_links_and_offline(self):
        for href in ("../../notebooks/03-prospective-forecast.ipynb", "../../skills/maa-03-prospective-forecast/SKILL.md", "../index.html"):
            self.assertIn(f'href="{href}"', self.page)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=180)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["labelled_controls"]), (12 + 12 + 8 + 12, 9))


if __name__ == "__main__":
    unittest.main()

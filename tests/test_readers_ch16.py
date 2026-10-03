"""Chapter 16 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(Equations 16.1 to 16.5, the sixty-unit construction, the three constructed
procedures, the notebook's default, changed and transfer cases and workbench
problem E.4), not read back from the module that produced the page. The test
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
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 8, 12])

    def test_size_budget(self):
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_optional_fields_present(self):
        self.assertIn("Ask the chapter skill", self.page)
        for d in self.data["demos"]:
            self.assertIn("predict", d)
            self.assertIn(d["predict"]["answer"], range(4))  # the answer is an option index; both feedback strings are present
            self.assertTrue(d["predict"]["correct"] and d["predict"]["incorrect"])
            for state in d["states"].values():
                self.assertTrue(2 <= len(state["steps"]) <= 8)
        self.assertEqual(self.page.count("Common wrong turn:"), 4)
        self.assertGreaterEqual(self.page.count("What this does not settle"), 1)
        self.assertIn('Chapter 16 source: "What this does not settle".', html.unescape(self.page))

    def test_d01_coverage_thin_bank_and_marginal_gain(self):
        for (spread, p, k), m, state in self.states("C16-D01"):
            k = int(k)
            thin = spread.startswith("Overconfident")
            # chance per sample on each half of the problems when the bank is thin: 2p and 0 (average p)
            self.assertAlmostEqual(0.5 * (2 * p) + 0.5 * 0, p)
            c = 0.5 * (1 - (1 - 2 * p) ** k) if thin else 1 - (1 - p) ** k
            gain = p * (1 - 2 * p) ** k if thin else p * (1 - p) ** k
            c_next = 0.5 * (1 - (1 - 2 * p) ** (k + 1)) if thin else 1 - (1 - p) ** (k + 1)
            self.assertEqual(m["Coverage Cov(k)"], f"{c:.4f}")
            self.assertEqual(m["Blind selection Sel(k)"], f"{p:.2f}")
            self.assertEqual(m["Gap a selector could close"], f"{c - p:.4f}")
            shown = m[f"Gain from sample {k + 1}"]
            self.assertEqual(shown, f"{gain:.4f}" if gain >= 1e-4 else f"{gain:.1e}")
            # Equation (16.4) against the difference of two coverages, computed independently
            self.assertAlmostEqual(gain, c_next - c, places=12)
            self.assertIn(f"Cov({k}) = ", state["interpretation"])
            if thin:
                self.assertLess(c, 1 - (1 - p) ** k)  # same average p, thinner bank
        # the chapter's own numbers (shared setting): 0.89 and 0.99 at p = 0.2; 0.40 and 0.99 at p = 0.05
        book = {(0.2, 10): "0.8926", (0.05, 10): "0.4013", (0.05, 100): "0.9941"}
        for (spread, p, k), m, _ in self.states("C16-D01"):
            if spread.startswith("Every") and (p, int(k)) in book:
                self.assertEqual(m["Coverage Cov(k)"], book[(p, int(k))])
            if spread.startswith("Every") and p == 0.2:
                self.assertEqual(m["Coverage at 20 samples"], "0.9885")
            if spread.startswith("Every") and p == 0.3:
                # the chapter: the first sample buys 0.30, the fifth 0.07, the twentieth under 0.001
                self.assertEqual(m["Gain from sample 5"], f"{0.3 * 0.7 ** 4:.4f}")
                self.assertEqual(m["Gain from sample 5"], "0.0720")
                self.assertLess(0.3 * 0.7 ** 19, 0.001)
                self.assertEqual(m["Gain from sample 20"], "0.0003")
        self.assertAlmostEqual(0.3 * 0.7 ** 0, 0.3)
        # one worked state in the text: p = 0.2 thin, k = 10: 0.5 x (1 - 0.6^10) = 0.4970 against 0.8926
        thin_state = next(s for v, m, s in self.states("C16-D01") if v[0].startswith("Overconfident") and v[1] == 0.2 and v[2] == 10)
        self.assertIn("0.5 x 0.993953 = 0.4970, against 0.8926", thin_state["interpretation"])
        self.assertAlmostEqual(0.5 * (1 - 0.6 ** 10), 0.4969765, places=6)

    def test_d02_cases_by_hand(self):
        cases = {
            "Notebook default": dict(p=0.4, c=1, l=1, sc=1, sl=1, deadline=6, budget=6, shared=False, counts=[1, 2, 3, 5]),
            "Changed": dict(p=0.4, c=1, l=1, sc=1, sl=1, deadline=6, budget=6, shared=True, counts=[1, 2, 3, 5]),
            "Transfer": dict(p=0.7, c=2, l=1, sc=3, sl=2, deadline=3, budget=6, shared=False, counts=[1, 2, 4]),
            "No allocation": dict(p=0.4, c=1, l=1, sc=1, sl=1, deadline=6, budget=0.5, shared=False, counts=[1, 2, 3, 5]),
        }
        seen = 0
        for (label, q), m, state in self.states("C16-D02"):
            case = next(v for key, v in cases.items() if label.startswith(key))
            p, shared = case["p"], case["shared"]
            rows = []
            for n in case["counts"]:
                coverage = p if shared else 1 - (1 - p) ** n
                selected = p if n == 1 else (coverage if shared else coverage * q)
                cost = n * case["c"] + (case["sc"] if n > 1 else 0)
                time = n * case["l"] + (case["sl"] if n > 1 else 0)
                rows.append((n, coverage, selected, cost, time, cost <= case["budget"] and time <= case["deadline"]))
            feasible = [r for r in rows if r[5]]
            self.assertEqual(m["Feasible allocations"], ", ".join(f"n = {r[0]}" for r in feasible) if feasible else "none")
            if feasible:
                best = max(feasible, key=lambda r: (round(r[2], 12), -r[3]))
                self.assertEqual(m["Chosen allocation"], f"n = {best[0]}")
                self.assertEqual(m["Coverage of the chosen allocation"], f"{best[1]:.4f}")
                self.assertEqual(m["Selected success of the chosen allocation"], f"{best[2]:.4f}")
            else:
                self.assertTrue(m["Chosen allocation"].startswith("undefined"))
            self.assertEqual(m["Blind selection"], f"{p:.2f}")
            big = rows[-1]
            label = f"Coverage minus delivery at n = {big[0]}" + ("" if big[5] else " (over a limit)")
            self.assertEqual(m[label], f"{big[1] - big[2]:.4f}")
            for r in rows:
                if r[0] > 1:
                    self.assertIn(f"n = {r[0]}: cost {r[0]} x {case['c']:g} + {case['sc']:g} = {r[3]:g}", state["interpretation"] + " ".join(state["steps"]))
            seen += 1
        self.assertEqual(seen, 12)
        # notebook default with selector 0.9: 0.92224 and 0.830016, cost and time both 6
        by = {(v[0][:8], v[1]): (m, s) for v, m, s in self.states("C16-D02")}
        default = by[("Notebook", 0.9)][0]
        self.assertEqual((default["Chosen allocation"], default["Selected success of the chosen allocation"]), ("n = 5", "0.8300"))
        self.assertAlmostEqual(1 - 0.6 ** 5, 0.92224)
        self.assertAlmostEqual(0.92224 * 0.9, 0.830016)
        # changed case: every row ties at 0.4, so the cheaper single sample wins (workbook question 2)
        changed = by[("Changed:", 0.9)][0]
        self.assertEqual((changed["Chosen allocation"], changed["Selected success of the chosen allocation"]), ("n = 1", "0.4000"))
        self.assertIn("ties go to the lower cost", by[("Changed:", 0.9)][1]["interpretation"])
        # transfer case with its notebook selector 0.5: only one candidate is feasible; two samples deliver 0.91 x 0.5 = 0.455
        transfer = by[("Transfer", 0.5)]
        self.assertEqual(transfer[0]["Chosen allocation"], "n = 1")
        self.assertIn("n = 2: cost 2 x 2 + 3 = 7, time 2 x 1 + 2 = 4", transfer[1]["interpretation"])
        self.assertIn("n = 4: cost 4 x 2 + 3 = 11, time 4 x 1 + 2 = 6", transfer[1]["interpretation"])
        self.assertAlmostEqual(0.91 * 0.5, 0.455)
        # g6-01: n = 2 and n = 4 cannot run, so the limits (not the selector) are the constraint
        self.assertIn("the deadline or budget is the constraint", transfer[1]["interpretation"])
        self.assertNotIn("the selector is the constraint", transfer[1]["interpretation"])
        # no feasible row: workbook question 3
        none = by[("No alloc", 0.9)]
        self.assertEqual(none[0]["Feasible allocations"], "none")
        self.assertIn("revise the limits or abstain", " ".join(none[1]["steps"]))
        # a half-reliable selector with two samples falls below blind selection: 0.64 x 0.5 = 0.32
        self.assertAlmostEqual(cov(0.4, 2) * 0.5, 0.32)

    def test_g6_01_diagnosis_uses_the_chosen_row_not_an_infeasible_bank(self):
        for (label, q), m, state in self.states("C16-D02"):
            text = state["interpretation"]
            if label.startswith("Transfer"):
                self.assertIn("the deadline or budget is the constraint", text, q)
                self.assertNotIn("the selector is the constraint", text, q)
                self.assertNotIn("0.992", text)  # coverage of the infeasible n = 4 bank is no longer diagnosed
            if label.startswith("No allocation"):
                self.assertIn("the budget and the deadline are the constraint", text, q)
                self.assertNotIn("largest bank", text, q)
                self.assertNotIn("the generator is the constraint", text, q)
            if label.startswith("Notebook") and q == 1.0:
                # coverage 0.922 equals delivery: nothing left for a selector, but coverage is not low
                self.assertNotIn("the generator is the constraint", text)
                self.assertIn("neither the selector nor the generator", text)
            if label.startswith("Changed"):
                self.assertIn("the generator is the constraint", text, q)  # coverage 0.4 equals delivery 0.4
            self.assertNotIn("At the largest bank", text)

    def test_g6_05_prediction_feedback_matches_the_state_numbers(self):
        fb = self.demos["C16-D03"]["predict"]
        for key in ("correct", "incorrect"):
            self.assertIn("0.9943", fb[key])
            self.assertIn("0.781", fb[key])
            self.assertNotIn("0.9942", fb[key])
            self.assertNotIn("0.780", fb[key])
        self.assertEqual(f"{1 - 0.65 ** 12:.4f}", "0.9943")
        self.assertEqual(f"{(1 - 0.65 ** 12) * 0.785:.3f}", "0.781")

    def test_g6_06_misconception_names_the_declared_ratio(self):
        text = html.unescape(self.page)
        self.assertIn("the lowest ratio is always A, even when A is not feasible", text)
        self.assertNotIn("The lowest ratio is A in every state here", text)

    def test_g6_09_thirteenth_sample_sentence_is_not_a_blanket_claim(self):
        for (case, long_p), m, state in self.states("C16-D03"):
            self.assertNotIn("the unspent units do not belong to more samples", state["interpretation"])
            self.assertIn("to coverage (Equation 16.4)", state["interpretation"])

    def test_d02_reader_passes_the_selector_setting_to_the_lab_unchanged(self):
        source = (LAB / "tools" / "readers" / "chapters" / "ch16.py").read_text(encoding="utf-8")
        self.assertNotIn("1.0 if shared", source)
        self.assertIn('selector_accuracy=float(selector)', source)

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
            # Equation (16.4): the thirteenth long sample adds p x (1 - p)^12
            self.assertIn(f"{long_p:.2f} x {1 - long_p:.2f}^12 = {long_p * (1 - long_p) ** 12:.4f}", state["interpretation"])
        # the book's own figures: 0.35, 0.20, about 0.73 and about 0.78; coverage 0.99998 and 0.994
        book = next(m for v, m, _ in self.states("C16-D03") if v == ["Book values: 0.73 and 0.785", 0.35])
        self.assertEqual((book["All on length"], book["All on volume"], book["Volume + selector"], book["Length + selector"]),
                         ("0.350", "0.200", "0.730", "0.781"))
        self.assertEqual(round((1 - 0.65 ** 12) * 0.785, 2), 0.78)  # the book says roughly 0.78
        self.assertAlmostEqual(1 - 0.8 ** 48, 0.99998, places=5)
        self.assertAlmostEqual(1 - 0.65 ** 12, 0.994, places=3)
        self.assertLess(0.35 * 0.65 ** 12, 0.002)  # the chapter: the thirteenth long sample buys under 0.002
        # budget arithmetic of the four allocations: 15 x 4, 60 x 1, 48 + 12, 12 x 4 + 3
        self.assertEqual((15 * 4, 60 * 1, 48 * 1 + 48 * 0.25, 12 * 4 + 12 * 0.25), (60, 60, 60, 51))
        # a selector worse than random loses to its blind counterpart
        worse = next(m for v, m, _ in self.states("C16-D03") if v == ["Worse than random: 0.15 for both", 0.35])
        self.assertEqual(worse["Best allocation"], "All on length")
        for long_p in (0.35, 0.25):
            st = next(s for v, m, s in self.states("C16-D03") if v == ["Worse than random: 0.15 for both", long_p])
            self.assertIn("Both selector allocations fall below their blind counterparts", st["interpretation"])
        for _, _, st in self.states("C16-D03"):
            self.assertIn("12 x 4 + 12 x 0.25 = 51 units and leaves 9 unspent", st["interpretation"])

    def test_d04_cost_per_success_feasibility_and_missing_denominator(self):
        procs = {"A": (1.0, 0.60, 1.0), "B": (1.5, 0.80, 2.0), "C": (2.0, 0.85, 5.0)}
        observed = 0
        for (deadline, need, evidence), m, state in self.states("C16-D04"):
            if evidence.startswith("Two observed"):
                observed += 1
                # workbench E.4 step 4: costs 2 and 3, no success: 5 / 0 is undefined
                self.assertEqual(m["Total cost"], f"{2 + 3:.1f}")
                self.assertEqual(m["Authorized confirmed completions"], "0")
                self.assertTrue(m["Cost per success"].startswith("undefined"))
                self.assertIn("2 + 3 = 5", state["interpretation"])
                self.assertIn("5 / 0 has no value", " ".join(state["steps"]))
                continue
            feasible = [n for n, (c, r, t) in procs.items() if r >= need and t <= deadline]
            per_success = {n: (100 * c) / (100 * r) for n, (c, r, t) in procs.items()}
            for n in procs:
                self.assertEqual(m[f"Cost per success {n}"], f"{per_success[n]:.2f}")
            self.assertEqual(m["Feasible procedures"], ", ".join(feasible) if feasible else "none")
            self.assertEqual(m["Procedures on the Pareto frontier"], "A, B, C")
            if feasible:
                cheapest = min(feasible, key=lambda n: per_success[n])
                loss = {n: c + (1 - r) * 20 for n, (c, r, t) in procs.items()}
                self.assertEqual(m["Cheapest per success among feasible"], cheapest)
                self.assertEqual(m["Lowest cost plus failure loss (20 per failure)"], min(feasible, key=lambda n: loss[n]))
            else:
                self.assertTrue(m["Cheapest per success among feasible"].startswith("undefined"))
        self.assertEqual(observed, 6)
        # no procedure beats another on completion (up), cost (down) and time (down): all three are nondominated
        for a, (ca, ra, ta) in procs.items():
            for b, (cb, rb, tb) in procs.items():
                if a != b:
                    self.assertFalse(rb >= ra and cb <= ca and tb <= ta and (rb, cb, tb) != (ra, ca, ta), (a, b))
        # the chapter's numbers: 1.6667, 1.875, 2.3529; 5.5 and 5 with a loss of 20 per failure
        self.assertAlmostEqual(100 / 60, 1.6667, places=4)
        self.assertAlmostEqual(150 / 80, 1.875)
        self.assertAlmostEqual(200 / 85, 2.3529, places=4)
        self.assertAlmostEqual(1.5 + 0.2 * 20, 5.5)
        self.assertAlmostEqual(2 + 0.15 * 20, 5.0)
        # 3 seconds and 0.75: only B. 3 seconds and 0.82: nobody. 10 seconds and 0.82: only C.
        by = {tuple(v): m for v, m, _ in self.states("C16-D04") if not str(v[2]).startswith("Two")}
        decl = "The three procedures' declared rates"
        self.assertEqual(by[(3, 0.75, decl)]["Feasible procedures"], "B")
        self.assertEqual(by[(3, 0.82, decl)]["Feasible procedures"], "none")
        self.assertEqual(by[(10, 0.82, decl)]["Feasible procedures"], "C")
        self.assertEqual(by[(10, 0.5, decl)]["Cheapest per success among feasible"], "A")
        self.assertEqual(by[(10, 0.75, decl)]["Lowest cost plus failure loss (20 per failure)"], "C")
        self.assertEqual(by[(3, 0.75, decl)]["Cheapest per success among feasible"], "B")
        for m in by.values():
            self.assertEqual(m["Cheapest per success overall"], "A")  # the unconditional comparison

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
        self.assertEqual(self.page.count('aria-live="polite"'), 8)  # per demo: the state region and the prediction feedback
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
            "        out = f(**{c['key']: v for c, v in zip(demo['controls'], combo)})\n"
            "        fig, metrics, text = out[0], out[1], out[2]\n"
            "        assert metrics and text\n"
            "        for ax in fig.axes:\n"
            "            assert ax.get_xlabel() and ax.get_ylabel(), (demo['id'], combo)\n"
            "        plt.close(fig); n += 1\n"
            "print(n)\n"
        )
        run = subprocess.run([PYTHON, "-c", script], capture_output=True, text=True, timeout=300)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.strip(), str(12 + 12 + 8 + 12))

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=180)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (44, 4, 10))
        self.assertEqual((report["ask_skill"], report["predictions_checked"] > 0, report["steps_checked"] > 0, report["panels_checked"] > 0), (1, True, True, True))

    def test_build_is_reproducible(self):
        other = build("b")
        try:
            fresh = other / SLUG / "reader.html"
            self.assertEqual(hashlib.sha256(fresh.read_bytes()).hexdigest(), hashlib.sha256(self.reader.read_bytes()).hexdigest())
        finally:
            shutil.rmtree(other, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()

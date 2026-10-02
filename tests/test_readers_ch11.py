"""Chapter 11 laboratory reader: independent hand checks of the built page.

The reader is built into a private temporary directory (never into the shared
readers folder). Every expected number is recomputed here from the chapter's
own arithmetic (regret as gap times tasks, the ten-pull table, the entropy of a
check, the worked classifier), not read back from the module that made the page.
"""
from __future__ import annotations

import html
import json
import math
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
PYTHON = LAB / ".venv" / "bin" / "python"


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def one(x, d=1):
    return f"{x:.{d}f}"


@unittest.skipUnless(PYTHON.is_file(), "laboratory .venv absent; cannot build the reader")
class Chapter11ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="reader-ch11-test-")
        run = subprocess.run([str(PYTHON), str(WRAPPER), "--chapters", "11", "--out", cls.tmp], capture_output=True, text=True, timeout=900)
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls.tmp) / "11-bounded-exploration" / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [math.sqrt(2) if str(c["values"][i]).startswith("square root of 2") else float(c["values"][i])
                      for c, i in zip(demo["controls"], idx)]
            yield values, dict(state["metrics"]), state

    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C11-D01", "C11-D02", "C11-D03", "C11-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 8, 8, 8])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_regret_is_gap_times_tasks(self):
        for (horizon, mean_b), m, state in self.states("C11-D01"):
            gap = mean_b - 0.78
            self.assertEqual(m["Always the current best"], one(horizon * mean_b - horizon * 0.78))
            # Rotating evenly: half the tasks on each tool.
            rotating = horizon * mean_b - (horizon / 2 * 0.78 + horizon / 2 * mean_b)
            self.assertEqual(m["Rotate evenly"], one(rotating))
            self.assertAlmostEqual(rotating, gap * horizon / 2)
            # The seeded run is far below both straight lines and below the always-best line by a wide margin.
            ucb = float(m["One seeded run of the optimistic rule"])
            self.assertLess(ucb, rotating)
            self.assertGreaterEqual(ucb, 0)
        # The book's own numbers: about 120 and 60 after 1,000 tasks, about 1,200 and 600 after 10,000.
        by_state = {tuple(v): m for v, m, _ in self.states("C11-D01")}
        self.assertEqual(by_state[(1000, 0.9)]["Always the current best"], "120.0")
        self.assertEqual(by_state[(1000, 0.9)]["Rotate evenly"], "60.0")
        self.assertEqual(by_state[(10000, 0.9)]["Always the current best"], "1200.0")
        self.assertEqual(by_state[(10000, 0.9)]["Rotate evenly"], "600.0")

    def test_d01_seeded_run_matches_an_independent_replay(self):
        """Replay the optimistic rule with its own random stream (Bernoulli draws from one seeded generator)."""
        import random
        means = [0.78, 0.90]
        rng = random.Random(11)
        counts, wins, regret, curve = [0, 0], [0, 0], 0.0, []
        for t in range(1000):
            if 0 in counts:
                a = counts.index(0)
            else:
                a = max(range(2), key=lambda i: wins[i] / counts[i] + math.sqrt(2 * math.log(t) / counts[i]))
            r = int(rng.random() < means[a])
            counts[a] += 1
            wins[a] += r
            regret += max(means) - means[a]
            curve.append(regret)
        state = {tuple(v): m for v, m, _ in self.states("C11-D01")}[(1000, 0.9)]
        self.assertEqual(state["One seeded run of the optimistic rule"], one(curve[-1]))

    def test_d02_ten_pull_table(self):
        """Rows of the chapter's table: (pull, counts, means, bonuses, selected, reward)."""
        table = {
            3: ((1, 1), (1.000, 0.000), (1.177, 1.177), "A"),
            4: ((2, 1), (0.500, 0.000), (1.048, 1.482), "A"),
            5: ((3, 1), (2 / 3, 0.000), (0.961, 1.665), "B"),
            10: ((6, 3), (0.500, 1 / 3), (0.856, 1.210), "B"),
        }
        c = math.sqrt(2)
        for (pull, cc), m, state in self.states("C11-D02"):
            if abs(cc - c) > 1e-9:
                continue
            counts, means, bonuses, selected = table[int(pull)]
            t = int(pull) - 1
            self.assertEqual(m["Counts A, B"], f"{counts[0]}, {counts[1]}")
            for i, name in enumerate("AB"):
                bonus = c * math.sqrt(math.log(t) / counts[i])
                self.assertAlmostEqual(bonus, bonuses[i], places=3)
                self.assertEqual(m[f"Index {name}"], one(means[i] + bonus, 3))
            self.assertEqual(m["Selected"], selected)
        # The chapter's key claim: A's index is 1.548 against B's 1.482 at pull 4, and B overtakes at pull 5.
        by_state = {(int(v[0]), round(v[1], 3)): m for v, m, _ in self.states("C11-D02")}
        self.assertEqual((by_state[(4, 1.414)]["Index A"], by_state[(4, 1.414)]["Index B"]), ("1.548", "1.482"))
        self.assertEqual((by_state[(5, 1.414)]["Index A"], by_state[(5, 1.414)]["Index B"]), ("1.628", "1.665"))

    def test_d02_smaller_coefficient_changes_the_path(self):
        """With c = 0.5, replay the alternating rewards by hand to pull 10 and compare the counts."""
        c = 0.5
        counts, sums = [0, 0], [0, 0]
        for pull in range(1, 10):  # decisions before pull 10
            t = pull - 1
            if 0 in counts:
                a = counts.index(0)
            else:
                idx = [sums[i] / counts[i] + c * math.sqrt(math.log(t) / counts[i]) for i in (0, 1)]
                a = 0 if idx[0] >= idx[1] else 1
            r = (1 if counts[a] % 2 == 0 else 0) if a == 0 else (counts[a] % 2)
            counts[a] += 1
            sums[a] += r
        by_state = {(int(v[0]), round(v[1], 3)): m for v, m, _ in self.states("C11-D02")}
        self.assertEqual(by_state[(10, 0.5)]["Counts A, B"], f"{counts[0]}, {counts[1]}")
        self.assertNotEqual(by_state[(10, 0.5)]["Counts A, B"], by_state[(10, 1.414)]["Counts A, B"])

    def test_d03_gain_and_value_of_a_check(self):
        def h(p):
            return 0.0 if p in (0, 1) else -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
        for (acc, prior), m, state in self.states("C11-D03"):
            p_s = prior * acc + (1 - prior) * (1 - acc)
            p_u = 1 - p_s
            post_s = prior * acc / p_s
            post_u = prior * (1 - acc) / p_u
            after = p_s * h(post_s) + p_u * h(post_u)
            self.assertEqual(m["Uncertainty before, H(Y)"], f"{h(prior):.3f} bits")
            self.assertEqual(m["Information gain I(Y; O)"], f"{h(prior) - after:.3f} bits")
            # Decision value from posteriors: best of release (100 x posterior) and evidence (92), weighted by report probability.
            best_after = p_s * max(100 * post_s, 92) + p_u * max(100 * post_u, 92)
            voi = best_after - max(100 * prior, 92)
            self.assertEqual(m["Decision value VOI"], f"{voi:.2f}")
            self.assertGreaterEqual(voi, -1e-12)
        by_state = {tuple(v): m for v, m, _ in self.states("C11-D03")}
        # Information gain without decision value: a weak check removes uncertainty but cannot change the action.
        weak = by_state[(0.6, 0.85)]
        self.assertGreater(float(weak["Information gain I(Y; O)"].split()[0]), 0)
        self.assertEqual((weak["Decision value VOI"], weak["Best action changes"]), ("0.00", "no"))
        weak_high_prior = by_state[(0.6, 0.97)]
        self.assertEqual((weak_high_prior["Decision value VOI"], weak_high_prior["Best action changes"]), ("0.00", "no"))
        # Chapter 11 check question: accuracy 0.70, prior 0.85, an unsupported report scores 70.8 and the supported report 92.97.
        self.assertAlmostEqual(100 * 0.85 * 0.3 / 0.36, 70.83, places=2)
        self.assertAlmostEqual(100 * 0.85 * 0.7 / 0.64, 92.97, places=2)
        self.assertEqual(by_state[(0.7, 0.85)]["Best action changes"], "yes")

    def test_d04_worked_classifier_by_hand(self):
        by_state = {tuple(v): m for v, m, _ in self.states("C11-D04")}
        # The book's worked price: no shift gives zero, a shift of 10 gives 7/3.
        self.assertEqual(by_state[(0, 0)]["Gross value"], "0.000")
        self.assertEqual(by_state[(10, 0)]["Gross value"], f"{7 / 3:.3f}")
        self.assertEqual(by_state[(10, 0)]["Best expected utility with the call"], f"{92 / 3 + 2 * 100 / 3:.3f}")
        self.assertEqual(by_state[(10, 0)]["Release now, no observation"], "95.000")
        self.assertEqual(by_state[(0, 0)]["Release now, no observation"], "85.000")
        for (shift, cost), m, state in self.states("C11-D04"):
            flag, clear = 75 + shift, 90 + shift
            before = max(flag / 3 + 2 * clear / 3, 92)
            after = max(flag, 92) / 3 + 2 * max(clear, 92) / 3
            voi = after - before
            self.assertEqual(m["Gross value"], f"{voi:.3f}")
            self.assertEqual(m["Net value"], f"{voi - cost:.3f}")
            self.assertGreaterEqual(voi, -1e-12)
        # Boundary cases the module claims to handle: an exact tie, a gross zero, a clear purchase, and a loss.
        self.assertEqual(by_state[(5, 2)]["Worth buying"], "tie")       # 94 - 92 = 2, net 0
        self.assertEqual(by_state[(0, 2)]["Worth buying"], "no")        # gross zero
        self.assertEqual(by_state[(10, 2)]["Worth buying"], "yes")      # 7/3 - 2 > 0
        self.assertEqual(by_state[(15, 2)]["Worth buying"], "no")       # 2/3 - 2 < 0
        # The value is not monotone in the shift: it rises to a peak and then falls.
        gross = [float(by_state[(s, 0)]["Gross value"]) for s in (0, 5, 10, 15)]
        self.assertEqual(gross.index(max(gross)), 2)
        self.assertGreater(gross[2], gross[3])

    def prose(self):
        """Visible page text with whitespace collapsed (prompts, explanations, answers)."""
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", text)))

    def test_patch_g4_ch11_wording(self):
        prose = self.prose()
        # g4-15: releasing already wins before observing at shift 10; shift 15 adds only the flag branch.
        self.assertNotIn("A shift of 15 makes releasing the best choice even before observing", prose)
        self.assertIn("From a shift of 10 on, releasing already beats requesting evidence before observing", prose)
        self.assertIn("1/3 x (92 - 90) = 0.667", prose)
        self.assertAlmostEqual((92 - 90) / 3, 0.667, places=3)
        self.assertGreater((75 + 10) / 3 + 2 * (90 + 10) / 3, 92)   # 95.0 at shift 10
        self.assertLess((75 + 5) / 3 + 2 * (90 + 5) / 3, 92)        # 90.0 at shift 5
        by_state = {tuple(v): m for v, m, _ in self.states("C11-D04")}
        self.assertEqual(by_state[(15, 0)]["Gross value"], "0.667")
        # g4-24: a negative net value is printed plainly, as in the metrics panel.
        for (shift, cost), m, state in self.states("C11-D04"):
            if cost == 2 and shift in (0, 15):
                self.assertNotIn("(-", state["interpretation"].split("net value =")[1].split(".")[0] + ".")
                self.assertIn(f"= {m['Net value']}.", state["interpretation"])
        # g4-16 / g4-23: state-aware wording and consistent thousands separators in D01.
        d1 = {tuple(v): (m, st) for v, m, st in self.states("C11-D01")}
        for key, (m, st) in d1.items():
            self.assertNotIn("far below both lines", st["interpretation"])
            self.assertNotIn("rising more slowly", st["interpretation"])
            ratio = float(m["One seeded run of the optimistic rule"]) / float(m["Rotate evenly"])
            self.assertIn(f"about {100 * ratio:.0f} percent of the rotate-evenly total", st["interpretation"])
        self.assertIn("= 1,200.0.", d1[(10000, 0.9)][1]["interpretation"])
        self.assertIn("= 600.0.", d1[(10000, 0.9)][1]["interpretation"])
        self.assertNotIn(" 1200.0", d1[(10000, 0.9)][1]["interpretation"])
        # g4-17: the dotted growth factor is qualitative in the prompt and bounded in the explanation.
        self.assertNotIn("by what factor does the dotted curve grow", prose.lower())
        for mb, low in ((0.9, 3.5), (0.84, 6.5)):
            factor = float(d1[(10000, mb)][0]["One seeded run of the optimistic rule"]) / float(
                d1[(1000, mb)][0]["One seeded run of the optimistic rule"])
            self.assertTrue(low <= factor < low + 0.1, (mb, factor))
            self.assertLess(factor, 10)
        self.assertIn("about 3.6", prose)
        self.assertIn("about 6.5", prose)
        # g4-18: the application states the chapter's instrument, not an unobservable best score.
        self.assertNotIn("what the best available action would have scored", prose)
        self.assertIn("sampled recently", prose)
        # g4-19 / g4-20: the prediction names c and the pull number; the check shows the exact product.
        self.assertIn("pull number to 5 with c = 1.414", prose)
        self.assertIn("1.414 x 0.8326 = 1.177", prose)
        self.assertNotIn("0.833 = 1.177", prose)
        self.assertAlmostEqual(1.414 * 0.8326, 1.177, places=3)
        # g4-22: the zero-VOI rule is tied to the release score staying on one side of 92, with prior-dependence stated.
        self.assertNotIn("A weak check moves beliefs a little", prose)
        self.assertIn("same side of 92", prose)
        self.assertIn("depends on the prior", prose)
        by3 = {tuple(v): m for v, m, _ in self.states("C11-D03")}
        self.assertEqual(by3[(0.7, 0.85)]["Best action changes"], "yes")
        self.assertEqual(by3[(0.7, 0.97)]["Best action changes"], "no")

    def test_d02_zero_mean_is_labelled_in_the_figure(self):
        """g4-21: whenever tool B has mean 0.000, the figure prints that mean (the SVG text is not base64 hidden)."""
        import base64
        seen = 0
        for key, state in self.demos["C11-D02"]["states"].items():
            svg = base64.b64decode(state["image"].split(",", 1)[1]).decode("utf-8")
            if "index = 0.000 +" in state["interpretation"]:
                seen += 1
                self.assertIn("mean 0.000", svg, key)
        self.assertGreaterEqual(seen, 6)

    def test_every_state_has_a_hand_calculation(self):
        pattern = re.compile(r"[-\d.()/]+ [x/+-] [-\d.()/a-z]+.* = [-\d.()]+")
        for demo in self.data["demos"]:
            for state in demo["states"].values():
                self.assertRegex(state["interpretation"], pattern)

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 11)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 5)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

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
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=300)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (32, 4, 8))


if __name__ == "__main__":
    unittest.main()

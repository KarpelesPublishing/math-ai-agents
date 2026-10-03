"""Chapter 11 reader tests: independent hand checks.

Every expected number is recomputed here from the chapter's own arithmetic
(regret as the sum of gap x pulls, the ten-pull table, the trapped controller,
the workbench indices, the entropy of a check, the worked classifier), and the
seeded runs are replayed with a separate implementation of the three rules.
The reader is built into a private temporary directory, never the shared
readers folder.
"""
from __future__ import annotations

import html
import importlib.util
import itertools
import json
import math
import os
import random
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
ENGINE = LAB / "tools" / "readers" / "engine"
CHAPTERS = LAB / "tools" / "readers" / "chapters"
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = ENGINE / "dom_harness.js"
PYTHON = LAB / ".venv" / "bin" / "python"
for p in (str(LAB / "src"), str(ENGINE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

spec = importlib.util.spec_from_file_location("reader_ch11", CHAPTERS / "ch11.py")
ch11 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ch11)

SQ2 = math.sqrt(2)


def run(i, **controls):
    d = ch11.CHAPTER["demos"][i]
    fig, metrics, text, extra = getattr(ch11, d["function"])(**controls)
    plt.close(fig)
    return metrics, text, extra


def states(i):
    d = ch11.CHAPTER["demos"][i]
    for combo in itertools.product(*[c["values"] for c in d["controls"]]):
        yield {c["key"]: v for c, v in zip(d["controls"], combo)}


def replay(means, rounds, seed, policy):
    """Independent replay of one seeded policy; returns (counts, pseudo-regret)."""
    rng = random.Random(seed)
    counts = [0] * len(means)
    wins = [0] * len(means)
    regret = 0.0
    best = max(means)
    for t in range(rounds):
        if 0 in counts:
            a = counts.index(0)
        elif policy == "greedy":
            a = max(range(len(means)), key=lambda i: wins[i] / counts[i])
        elif policy == "ucb":
            a = max(range(len(means)), key=lambda i: wins[i] / counts[i] + math.sqrt(2 * math.log(t) / counts[i]))
        else:
            a = max(range(len(means)), key=lambda i: rng.betavariate(wins[i] + 1, counts[i] - wins[i] + 1))
        r = int(rng.random() < means[a])
        counts[a] += 1
        wins[a] += r
        regret += best - means[a]
    return counts, regret


class Chapter11ReaderTests(unittest.TestCase):
    def test_structure(self):
        demos = ch11.CHAPTER["demos"]
        self.assertEqual([d["id"] for d in demos], ["C11-D01", "C11-D02", "C11-D03", "C11-D04"])
        sizes = []
        for d in demos:
            n = 1
            for c in d["controls"]:
                n *= len(c["values"])
            sizes.append(n)
        self.assertEqual(sizes, [8, 12, 12, 12])
        self.assertIn("prompt", ch11.CHAPTER["ask_skill"])
        for d in demos:
            self.assertIn("misconception", d)
            self.assertIn("scope_note", d)
            self.assertIn("prediction_options", d)

    def test_every_state_renders_with_steps_and_alt(self):
        for i in range(4):
            for kw in states(i):
                m, text, extra = run(i, **kw)
                self.assertTrue(m and text and extra["alt"] and 2 <= len(extra["steps"]) <= 8, (i, kw))
                for s in extra["steps"]:
                    self.assertLessEqual(len(s), 240, s)
                for bad in ("\u2014", "\u2013", "--"):
                    self.assertNotIn(bad, text + " ".join(extra["steps"]))

    def test_d01_regret_is_sum_of_gap_times_pulls_and_matches_replay(self):
        worlds = {"book": ([0.78, 0.90], 11, 1000), "default": ([0.4, 0.7], 7, 120),
                  "swapped": ([0.7, 0.4], 7, 120), "three": ([0.2, 0.5, 0.8], 19, 90)}
        keys = {"greedy": "Always the current best (this run)", "ucb": "Optimistic rule (this run)",
                "thompson": "Posterior sampling (this run)"}
        for world, scale in itertools.product(worlds, ["own", "ten"]):
            means, seed, base = worlds[world]
            rounds = base * (10 if scale == "ten" else 1)
            m, text, _ = run(0, world=world, scale=scale)
            best = max(means)
            for policy, key in keys.items():
                counts, regret = replay(means, rounds, seed, policy)
                self.assertEqual(sum(counts), rounds)
                by_gap = sum((best - mu) * n for mu, n in zip(means, counts))
                self.assertAlmostEqual(by_gap, regret, places=6)
                self.assertEqual(m[key], f"{regret:.2f}")
            ordered = sorted(means)
            gap = best - ordered[-2]
            self.assertEqual(m["Stuck on the runner-up arm"], f"{gap * rounds:.2f}")
            self.assertEqual(m["Rotate evenly"], f"{rounds * (best - sum(means) / len(means)):.2f}")
            self.assertEqual(m["Chance the chapter's controller draws two failures in a row from the best arm"], f"{(1 - best) ** 2:.2f}")
            self.assertEqual(m["Best success rate available"], f"{best:.2f}")
        # the book's numbers: 0.12 x 1,000 = 120 and 0.12 x 500 = 60 (rotating)
        b = run(0, world="book", scale="own")[0]
        self.assertEqual((b["Stuck on the runner-up arm"], b["Rotate evenly"]), ("120.00", "60.00"))
        t = run(0, world="book", scale="ten")[0]
        self.assertEqual((t["Stuck on the runner-up arm"], t["Rotate evenly"]), ("1200.00", "600.00"))
        self.assertEqual(b["Chance the chapter's controller draws two failures in a row from the best arm"], "0.01")
        # workbook: default regret through counts, 0.3 x worse-arm pulls
        counts, regret = replay([0.4, 0.7], 120, 7, "ucb")
        self.assertIn(f"0.30 x {counts[0]} = {0.3 * counts[0]:.2f}", run(0, world="default", scale="own")[1])
        # workbook transfer: 0.6 n0 + 0.3 n1
        c3, r3 = replay([0.2, 0.5, 0.8], 90, 19, "ucb")
        self.assertIn(f"0.60 x {c3[0]} + 0.30 x {c3[1]} = {0.6 * c3[0] + 0.3 * c3[1]:.2f}",
                      run(0, world="three", scale="own")[1])
        # a common pull cost lowers net reward and leaves pseudo-regret alone
        self.assertIn("0.05 x 120 = 6.00", run(0, world="default", scale="own")[1])

    def test_d01_prediction_factor(self):
        own = run(0, world="book", scale="own")[0]
        ten = run(0, world="book", scale="ten")[0]
        self.assertEqual((own["Optimistic rule (this run)"], ten["Optimistic rule (this run)"]), ("29.64", "105.24"))
        self.assertLess(105.24 / 29.64, 10)

    def test_d02_table_trap_and_workbench(self):
        def idx(mean, n, t, c):
            return mean + c * math.sqrt(math.log(t) / n)
        # table (chapter): pull 4 counts 2,1 (A 1.548, B 1.482 -> A); pull 5 counts 3,1 (1.628, 1.665 -> B)
        m4 = run(1, situation="p4", c=SQ2)[0]
        self.assertEqual((m4["Index A"], m4["Index B"], m4["Selected"]), ("1.548", "1.482", "A"))
        m5 = run(1, situation="p5", c=SQ2)[0]
        self.assertEqual((m5["Index A"], m5["Index B"], m5["Selected"]), ("1.628", "1.665", "B"))
        self.assertEqual(m5["Counts A, B"], "3, 1")
        # trapped controller after 20 tasks: A 18 pulls, 14 wins; B 2 pulls, 0 wins
        for c in (SQ2, 1.0, 0.5):
            m = run(1, situation="trap", c=c)[0]
            ia, ib = idx(14 / 18, 18, 20, c), idx(0.0, 2, 20, c)
            self.assertEqual((m["Index A"], m["Index B"]), (f"{ia:.3f}", f"{ib:.3f}"))
            self.assertEqual(m["Selected"], "B" if ib > ia else "A")
            self.assertEqual(m["Selected by mean alone"], "A")
        self.assertEqual(run(1, situation="trap", c=SQ2)[0]["Selected"], "B")
        self.assertEqual(run(1, situation="trap", c=0.5)[0]["Selected"], "A")
        # workbench III.1: t = 100, bonuses 0.3393 and 0.6786, indices 1.0393 and 1.2786, B selected
        mb = run(1, situation="bench", c=SQ2)[0]
        self.assertEqual((mb["Index A"], mb["Index B"], mb["Selected"]), ("1.039", "1.279", "B"))
        self.assertAlmostEqual(math.sqrt(2 * math.log(100) / 80), 0.3393, places=4)
        self.assertAlmostEqual(math.sqrt(2 * math.log(100) / 20), 0.6786, places=4)
        self.assertEqual(mb["Selected by mean alone"], "A")
        self.assertIn("ln 20 = 2.996", run(1, situation="trap", c=SQ2)[1])

    def test_d03_gain_and_value_of_a_check(self):
        def h(p):
            return 0.0 if p in (0, 1) else -(p * math.log2(p) + (1 - p) * math.log2(1 - p))
        out = {}
        for kw in states(2):
            acc, prior = kw["accuracy"], kw["prior"]
            m = run(2, **kw)[0]
            p_s = prior * acc + (1 - prior) * (1 - acc)
            p_u = 1 - p_s
            post_s, post_u = prior * acc / p_s, prior * (1 - acc) / p_u
            after = p_s * h(post_s) + p_u * h(post_u)
            self.assertEqual(m["Uncertainty before, H(Y)"], f"{h(prior):.3f} bits")
            self.assertEqual(m["Information gain I(Y; O)"], f"{h(prior) - after:.3f} bits")
            best_after = p_s * max(100 * post_s, 92) + p_u * max(100 * post_u, 92)
            voi = best_after - max(100 * prior, 92)
            self.assertEqual(m["Decision value VOI"], f"{voi:.2f}")
            self.assertGreaterEqual(voi, -1e-12)
            out[(acc, prior)] = m
        weak = out[(0.6, 0.85)]
        self.assertGreater(float(weak["Information gain I(Y; O)"].split()[0]), 0)
        self.assertEqual((weak["Decision value VOI"], weak["Best action changes"]), ("0.00", "no"))
        self.assertEqual(out[(0.7, 0.85)]["Best action changes"], "yes")
        self.assertEqual(out[(0.7, 0.97)]["Best action changes"], "no")
        self.assertAlmostEqual(100 * 0.85 * 0.3 / 0.36, 70.83, places=2)
        self.assertAlmostEqual(100 * 0.85 * 0.7 / 0.64, 92.97, places=2)
        # prior 0.5: no check scores max(50, 92) = 92; accuracy 0.95 lifts the supported report to 95
        self.assertEqual(out[(0.95, 0.5)]["Best action changes"], "yes")
        self.assertEqual(out[(0.6, 0.5)]["Decision value VOI"], "0.00")

    def test_d04_worked_classifier_by_hand(self):
        by = {}
        for kw in states(3):
            shift, cost = kw["shift"], kw["call_cost"]
            m = run(3, **kw)[0]
            flag, clear = 75 + shift, 90 + shift
            before = max(flag / 3 + 2 * clear / 3, 92)
            after = max(flag, 92) / 3 + 2 * max(clear, 92) / 3
            voi = after - before
            self.assertEqual(m["Gross value"], f"{voi:.3f}")
            self.assertEqual(m["Net value"], f"{voi - cost:.3f}")
            by[(shift, round(cost, 3))] = m
        self.assertEqual(by[(0, 0)]["Gross value"], "0.000")
        self.assertEqual(by[(10, 0)]["Gross value"], f"{7 / 3:.3f}")
        self.assertEqual(by[(10, 0)]["Release now, no observation"], "95.000")
        self.assertEqual(by[(0, 0)]["Release now, no observation"], "85.000")
        self.assertEqual(by[(5, 2)]["Worth buying"], "tie")
        self.assertEqual(by[(0, 2)]["Worth buying"], "no")
        self.assertEqual(by[(10, 2)]["Worth buying"], "yes")
        self.assertEqual(by[(15, 2)]["Worth buying"], "no")
        # the book's price 7/3: a call costing exactly 7/3 ties at shift 10; above it is not worth buying
        self.assertEqual(by[(10, 2.333)]["Worth buying"], "tie")
        self.assertEqual(by[(10, 2.333)]["Net value"], "0.000")
        self.assertEqual(by[(5, 2.333)]["Worth buying"], "no")
        gross = [float(by[(s, 0)]["Gross value"]) for s in (0, 5, 10, 15)]
        self.assertEqual(gross.index(max(gross)), 2)

    def test_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 11)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        for d in ch11.CHAPTER["demos"]:
            for tex in d["equations"]:
                self.assertIn(norm(html.unescape(tex)), allowed, d["id"])

    def test_text_rules(self):
        blob = json.dumps(ch11.CHAPTER, ensure_ascii=False)
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, blob)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, blob.lower())
        for d in ch11.CHAPTER["demos"]:
            self.assertIn("constructed", d["provenance"].lower())
            self.assertTrue(d["check"].endswith("?"))
            self.assertEqual(d["scope_note"]["source_section"], "What this does not settle")


@unittest.skipUnless(PYTHON.is_file(), "laboratory .venv absent; cannot build the reader")
class Chapter11BuiltPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="reader-ch11-test-")
        r = subprocess.run([str(PYTHON), str(WRAPPER), "--chapters", "11", "--out", cls.tmp], capture_output=True, text=True,
                           timeout=900, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        assert r.returncode == 0, r.stdout + r.stderr
        cls.reader = Path(cls.tmp) / "11-bounded-exploration" / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', cls.page, re.S).group(1))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_size_states_and_panels(self):
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 12, 12, 12])
        self.assertLess(self.reader.stat().st_size, 4_000_000)
        for text in ("Ask the chapter skill", "What this does not settle", "Common wrong turn", "Your prediction", "Worked steps"):
            self.assertIn(text, self.page)
        self.assertEqual(len(re.findall(r'data-tex="', self.page)), 5)

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed")
        r = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        report = json.loads(r.stdout)["reports"][0]
        self.assertEqual(report["states_checked"], 44)


class Chapter11Patch2Tests(unittest.TestCase):
    def test_pooled_greedy_lockout_matches_independent_replay(self):
        worlds = {"book": ([0.78, 0.90], 1000), "default": ([0.4, 0.7], 120), "swapped": ([0.7, 0.4], 120), "three": ([0.2, 0.5, 0.8], 90)}
        for world, (means, rounds) in worlds.items():
            m, text, extra = run(0, world=world, scale="own")
            best = max(means)
            half = 0.5 * (best - sorted(means)[-2]) * rounds
            locked = 0
            mean = {"greedy": 0.0, "ucb": 0.0, "thompson": 0.0}
            for seed in range(200):
                for pol in mean:
                    mean[pol] += replay(means, rounds, seed, pol)[1] / 200
                if replay(means, rounds, seed, "greedy")[1] > half:
                    locked += 1
            self.assertEqual(m["Always the current best, seeds above half the stuck line (of 200)"], str(locked))
            self.assertEqual(m["Mean regret over 200 seeds, always the current best"], f"{mean['greedy']:.2f}")
            self.assertEqual(m["Mean regret over 200 seeds, optimistic rule"], f"{mean['ucb']:.2f}")
            self.assertEqual(m["Mean regret over 200 seeds, posterior sampling"], f"{mean['thompson']:.2f}")
            self.assertIn(f"in {locked} of 200 seeds", text)
            self.assertIn(f"{locked} of 200 seeds", " ".join(extra["steps"]))
            self.assertNotIn("Chance the best arm fails its first two pulls", m)
        book = run(0, world="book", scale="own")[0]
        self.assertGreater(int(book["Always the current best, seeds above half the stuck line (of 200)"]), 20)

    def test_d03_figure_scores_appear_in_the_arithmetic(self):
        m, text, _ = run(2, accuracy=0.7, prior=0.85)
        self.assertIn("posterior release score 92.97", text)
        self.assertIn("posterior release score 70.83", text)
        self.assertIn("weighted by that chance, max(100 x 0.5950", text)

    def test_article_agrees_with_noun(self):
        for situation in ("p4", "p5", "trap", "bench"):
            text = run(1, situation=situation)[1]
            self.assertNotIn("A action", text)
        self.assertIn("An action with few pulls", run(1, situation="bench")[1])
        self.assertIn("A tool with few pulls", run(1, situation="trap")[1])

    def test_correct_prediction_is_not_always_first(self):
        answers = [d["prediction_answer"] for d in ch11.CHAPTER["demos"]]
        self.assertNotEqual(set(answers), {0})
        self.assertEqual(ch11.CHAPTER["demos"][0]["prediction_options"][ch11.CHAPTER["demos"][0]["prediction_answer"]],
                         "Stuck regret grows ten times; the optimistic run grows by less than ten times.")


if __name__ == "__main__":
    unittest.main()

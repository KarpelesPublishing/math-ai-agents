"""Chapter 13 laboratory reader: independent hand checks of the built page.

Every expected number below is recomputed here by a different method from the
one in the chapter module (backward recursion for return-to-go, a finite
difference for the gradient, a direct simulation of the one-step training rule,
telescoping sums for shaping), not read back from the module that produced the
page. The checks read the built reader with the standard library only.
"""
from __future__ import annotations

import html
import json
import math
import random
import re
import shutil
import subprocess
import tempfile
import unittest
import importlib.util
import os
from pathlib import Path

from math_ai_agents.chapters.ch13 import evaluate

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
READER = LAB / "readers" / "13-finite-policy-learning" / "reader.html"
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
MODULE = LAB / "tools" / "readers" / "chapters" / "ch13.py"


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


def build_into(out):
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    python = helpers.builder_python()
    if python is None:
        return None
    run = subprocess.run([python, str(WRAPPER), "--chapters", "13", "--out", out], capture_output=True, text=True,
                         timeout=900, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    assert run.returncode == 0, run.stdout + run.stderr
    return Path(out) / "13-finite-policy-learning" / "reader.html"


class Chapter13Base(unittest.TestCase):
    """Builds the chapter into a private temporary directory, so no shared output is touched."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls._tmp.cleanup)
        cls.reader = build_into(cls._tmp.name)
        if cls.reader is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    def states(self, demo_id, axes):
        """Yield (control values, metrics dict, state); values come from the hand-written axes, indexed by the state key."""
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [axis[i] for axis, i in zip(axes, idx)]
            yield values, dict(state["metrics"]), state



STREAMS = [[-0.05, 0.0, 1.0], [1.0, 2.0]]
GAMMAS = [1.0, 0.9, 0.5]
MASKS = [0, 1]
PHIS = [-2, 0, 1, 3]
BASELINES = ["none", "expected", "action"]
CASES = [
    {"rewards": [1, 2], "success": [0.9, 0.2], "pots": [0, 0], "seeds": [3, 11], "lr": 0.08, "episodes": 120, "n": 200},
    {"rewards": [2, 1], "success": [0.9, 0.2], "pots": [0, 0], "seeds": [3, 11], "lr": 0.08, "episodes": 120, "n": 200},
    {"rewards": [0, 1], "success": [0, 1], "pots": [2, 0], "seeds": [7, 17], "lr": 0.1, "episodes": 100, "n": 100},
    {"rewards": [0.63, 0.73, 0.95], "success": [0.55, 0.8, 0.0], "pots": [0, 0, 0], "seeds": [3, 11], "lr": 0.08,
     "episodes": 120, "n": 200},
]
LENGTHS = [10, None, 400]  # None: the case's own length
EVIDENCE = [0.4, 1.0]
RETRIEVE_END = [0.0, 0.2]
DIRECT_END = [0.0, 0.2, 0.3]


def reinforce_final(shaped, seed, lr, episodes, *, trace=False):
    """One-step softmax REINFORCE with the policy's expected reward as baseline, written from the update rule."""
    rng = random.Random(seed)
    k = len(shaped)
    logits = [0.0] * k
    history = []
    for _ in range(episodes):
        m = max(logits)
        w = [math.exp(v - m) for v in logits]
        z = sum(w)
        p = [v / z for v in w]
        u, cum, chosen = rng.random(), 0.0, k - 1
        for i, pi in enumerate(p):
            cum += pi
            if u < cum:
                chosen = i
                break
        base = sum(pi * r for pi, r in zip(p, shaped))
        for i in range(k):
            logits[i] += lr * (shaped[chosen] - base) * ((i == chosen) - p[i])
        m = max(logits)
        weights = [math.exp(v - m) for v in logits]
        denominator = sum(weights)
        history.append(sum(w * r for w, r in zip(weights, shaped)) / denominator)
    m = max(logits)
    w = [math.exp(v - m) for v in logits]
    z = sum(w)
    final = [v / z for v in w]
    return (final, history) if trace else final


def estimator(phi, baseline):
    """Exact mean and spread of g = score x (G - b) over the four outcomes, by explicit enumeration."""
    p = 1 / (1 + math.exp(-phi))
    v = p * 0.75 + (1 - p) * 0.55
    cases = [  # (probability, score, return, action baseline)
        ((1 - p) * 0.45, -p, 0.0, 0.55), ((1 - p) * 0.55, -p, 1.0, 0.55),
        (p * 0.20, 1 - p, -0.05, 0.75), (p * 0.80, 1 - p, 0.95, 0.75),
    ]
    gs = []
    for prob, score, ret, qa in cases:
        b = {"none": 0.0, "expected": v, "action": qa}[baseline]
        gs.append((prob, score * (ret - b)))
    mean = sum(q * g for q, g in gs)
    var = sum(q * (g - mean) ** 2 for q, g in gs)
    return mean, math.sqrt(var)


@unittest.skipUnless(MODULE.is_file(), "Chapter 13 module missing")
class Chapter13ReaderTests(Chapter13Base):
    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C13-D01", "C13-D02", "C13-D03", "C13-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 12, 12])
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_d01_return_to_go_by_backward_recursion_and_mask_loss(self):
        seen = {}
        for (rewards, gamma, mask), m, _ in self.states("C13-D01", [STREAMS, GAMMAS, MASKS]):
            G, ahead = [0.0] * len(rewards), 0.0
            for t in reversed(range(len(rewards))):  # G_t = r_t + gamma G_{t+1}
                ahead = rewards[t] + gamma * ahead
                G[t] = ahead
            for t, g in enumerate(G):
                self.assertEqual(m[f"G_{t}"], f"{g:.3f}", (rewards, gamma, t))
            self.assertEqual(m["Sum of rewards, no discount"], f"{sum(rewards):.3f}")
            self.assertEqual(m["Weight on the last reward in G_0"], f"{gamma ** (len(rewards) - 1):.3f}")
            # The chapter's unit test: -[(1)(-0.4) + (mask)(-1.2)] is 0.4 with mask 0 and 1.6 with mask 1.
            self.assertEqual(m["Selected-token loss"], f"{-(1 * -0.4 + mask * -1.2):.1f}")
            seen[(tuple(rewards), gamma)] = G
        self.assertAlmostEqual(seen[((1.0, 2.0), 0.5)][0], 2.0)  # Exercise 1: 1 + 0.5 x 2
        self.assertAlmostEqual(seen[((1.0, 2.0), 0.9)][0], 2.8)
        self.assertAlmostEqual(seen[((-0.05, 0.0, 1.0), 0.5)][0], -0.05 + 0.25)
        self.assertIn("G_0 = 1.0 + 0.5 x 2.0 = 2.000", self.page)
        self.assertIn("-[(1)(-0.4)+(0)(-1.2)] = 0.4", self.page)
        self.assertIn("-[(1)(-0.4)+(1)(-1.2)] = 1.6", self.page)

    def test_d02_estimator_mean_and_spread_by_enumeration(self):
        for (phi, baseline), m, _ in self.states("C13-D02", [PHIS, BASELINES]):
            p = 1 / (1 + math.exp(-phi))
            h = 1e-6
            J = lambda f: (lambda q: q * 0.75 + (1 - q) * 0.55)(1 / (1 + math.exp(-f)))
            numeric = (J(phi + h) - J(phi - h)) / (2 * h)
            mean, spread = estimator(phi, baseline)
            self.assertEqual(m["Retrieve probability p"], f"{p:.4f}")
            self.assertEqual(m["Expected utility J"], f"{J(phi):.4f}")
            self.assertEqual(m["True gradient dJ/dphi"], f"{numeric:.4f}", (phi, baseline))
            self.assertEqual(m["Mean of the update signal"], f"{mean + 0.0:.4f}".replace("-0.0000", "0.0000"), (phi, baseline))
            self.assertEqual(m["Spread (standard deviation)"], f"{spread:.4f}", (phi, baseline))
            if baseline in ("none", "expected"):
                self.assertAlmostEqual(mean, numeric, places=6)  # a context-only baseline leaves the mean alone
            else:
                self.assertAlmostEqual(mean, 0.0, places=9)      # an action-dependent baseline removes the signal
        book = dict(self.demos["C13-D02"]["states"]["1,0"]["metrics"])  # phi = 0, no baseline
        self.assertEqual((book["Retrieve probability p"], book["Expected utility J"], book["True gradient dJ/dphi"]),
                         ("0.5000", "0.6500", "0.0500"))  # the chapter: utility 0.65, gradient 0.05
        for phi in PHIS:  # the baseline lowers the spread at every phi
            self.assertLess(estimator(phi, "expected")[1], estimator(phi, "none")[1])

    def test_d03_matches_independent_reinforce_runs_for_every_case(self):
        for (case, length), m, _ in self.states("C13-D03", [CASES, LENGTHS]):
            episodes = case["episodes"] if length is None else length
            shaped = [r + 1 * v for r, v in zip(case["rewards"], case["pots"])]
            k = len(shaped)
            start_r = sum(shaped) / k
            start_s = sum(case["success"]) / k
            self.assertEqual(m["Start: reward trained on"], f"{start_r:.3f}")
            self.assertEqual(m["Start: true success"], f"{start_s:.3f}")
            for seed in case["seeds"]:
                p = reinforce_final(shaped, seed, case["lr"], episodes)
                self.assertEqual(m[f"Seed {seed}: true success"], f"{sum(a * b for a, b in zip(p, case['success'])):.3f}",
                                 (case["rewards"], seed, episodes))
            p0 = reinforce_final(shaped, case["seeds"][0], case["lr"], episodes)
            self.assertEqual(m[f"Seed {case['seeds'][0]}: reward trained on"], f"{sum(a * b for a, b in zip(p0, shaped)):.3f}")
            self.assertIn(f"Seed {case['seeds'][0]}: sampled evaluation, n = {case['n']}", m)

    def test_d03_direction_of_the_mismatch(self):
        end = {}
        for (case, length), m, _ in self.states("C13-D03", [CASES, LENGTHS]):
            end[(tuple(case["rewards"]), length)] = (float(m[f"Seed {case['seeds'][0]}: true success"]),
                                                      float(m["Start: true success"]))
        for rewards in ((1, 2), (0, 1), (0.63, 0.73, 0.95)):  # the learner is drawn away from the task
            for length in (10, None, 400):
                self.assertLess(end[(rewards, length)][0], end[(rewards, length)][1], (rewards, length))
        for length in (10, None, 400):                          # aligned rewards help the task
            self.assertGreater(end[((2, 1), length)][0], end[((2, 1), length)][1])
        for rewards in ((1, 2), (0, 1), (0.63, 0.73, 0.95)):    # longer training moves further the same way
            self.assertTrue(end[(rewards, 10)][0] > end[(rewards, None)][0] > end[(rewards, 400)][0], rewards)

    def test_d03_lab_function_agrees_and_flags_the_conflict(self):
        out = evaluate({"rewards": [0, 1], "success_probabilities": [0, 1], "terminal_potentials": [2, 0], "episodes": 100,
                        "seeds": [7, 17], "learning_rate": 0.1, "discount": 1, "evaluation_runs": 100})
        self.assertEqual(out["metrics"]["shaped_rewards"], [2.0, 1.0])
        self.assertEqual(out["metrics"]["verifier_optimal_action"], 1)
        self.assertEqual(out["metrics"]["shaped_optimal_action"], 0)
        self.assertTrue(out["metrics"]["training_objective_conflicts_with_task"])
        self.assertFalse(out["metrics"]["policy_invariant_shaping_condition"])
        state = next(m for (c, length), m, _ in self.states("C13-D03", [CASES, LENGTHS])
                     if c["rewards"] == [0, 1] and length is None)
        self.assertEqual(state["Seed 7: true success"], f"{out['metrics']['runs'][0]['expected_external_success']:.3f}")
        self.assertEqual(state["Seed 7: unshaped verifier reward"], f"{out['metrics']['runs'][0]['expected_training_reward']:.3f}")
        # The chapter's verifier arithmetic for the story case: 0.63, 0.78 - 0.05 = 0.73.
        self.assertAlmostEqual(0.55 * 0.9 + 0.45 * 0.3, 0.63)
        self.assertAlmostEqual(0.80 * 0.9 + 0.20 * 0.3 - 0.05, 0.73)
        self.assertIn("0.55 x 0.9 + 0.45 x 0.3 = 0.63", self.page)

    def test_d04_shaping_telescopes_and_ranking(self):
        ranks = {}
        for (e, tr, d), m, _ in self.states("C13-D04", [EVIDENCE, RETRIEVE_END, DIRECT_END]):
            rewards = [-0.05, 1.0]
            pots = [0.0, e, tr]
            shaped = [rewards[t] + pots[t + 1] - pots[t] for t in range(2)]
            self.assertAlmostEqual(sum(shaped), sum(rewards) - pots[0] + pots[2])  # Equation (13.4)
            self.assertEqual(m["Retrieve route G_0 (success case)"], f"{sum(rewards):.2f}")
            self.assertEqual(m["Retrieve route G'_0 (success case)"], f"{sum(shaped):.2f}")
            # Expected shaped return over success (0.80) and failure (0.20) of the release step.
            retrieve = 0.8 * (-0.05 + 1.0 + tr) + 0.2 * (-0.05 + 0.0 + tr)
            direct = 0.55 + d
            self.assertEqual(m["Direct route G'_0"], f"{direct:.2f}")
            self.assertEqual(m["Retrieve route expected G'_0 (0.80 success)"], f"{retrieve:.2f}")
            expected = "tie" if abs(direct - retrieve) < 1e-9 else ("Answer directly" if direct > retrieve else "Retrieve then answer")
            self.assertEqual(m["Ranked first after shaping"], expected, (e, tr, d))
            ranks[(e, tr, d)] = expected
        self.assertEqual(ranks[(0.4, 0.0, 0.0)], "Retrieve then answer")  # the book's potential: ranking preserved
        self.assertEqual(ranks[(0.4, 0.0, 0.2)], "tie")
        self.assertEqual(ranks[(1.0, 0.0, 0.3)], "Answer directly")       # the chapter's 0.30 bonus: 0.85 against 0.75
        self.assertEqual(ranks[(0.4, 0.2, 0.3)], "Retrieve then answer")

    def test_d04_closing_sentence_matches_the_state(self):
        by = {tuple(v): s["interpretation"] for v, _, s in self.states("C13-D04", [EVIDENCE, RETRIEVE_END, DIRECT_END])}
        for key in ((0.4, 0.0, 0.0), (1.0, 0.0, 0.0)):
            self.assertIn("Both end potentials are 0, so the shaped returns equal the original ones", by[key])
        for key in ((0.4, 0.0, 0.2), (1.0, 0.0, 0.2)):
            self.assertIn("tie", by[key])
        for key in ((0.4, 0.0, 0.3), (1.0, 0.0, 0.3)):
            self.assertIn("0.55 + 0.30 = 0.85", by[key])
        for key in ((0.4, 0.2, 0.0), (1.0, 0.2, 0.0)):
            self.assertIn("by a larger margin", by[key])

    def test_d04_shared_and_unequal_end_potentials_are_worded_apart(self):
        by = {tuple(v): s["interpretation"] for v, _, s in self.states("C13-D04", [EVIDENCE, RETRIEVE_END, DIRECT_END])}
        self.assertIn("same end potential 0.2, a common offset", by[(0.4, 0.2, 0.2)])
        self.assertIn("differ by 0.1, which is less than the original gap 0.20", by[(0.4, 0.2, 0.3)])
        for text in by.values():
            self.assertNotIn("A modest end potential on one route", text)

    def test_wording_fixes_from_review(self):
        page = self.page
        self.assertIn("does not automatically take", page)
        self.assertNotIn("without any error message", page)
        self.assertIn("1/3 x 0.63 + 1/3 x 0.73 + 1/3 x 0.95 = 0.770", page)
        self.assertNotIn("0.333 x 0.63", page)
        self.assertIn("200 evaluation runs", page)

    def test_optional_fields_are_present_and_consistent(self):
        page = html.unescape(self.page)
        self.assertIn("Ask the chapter skill", page)
        for demo in self.data["demos"]:
            self.assertTrue(demo["predict"]["correct"] and demo["predict"]["incorrect"])
            for state in demo["states"].values():
                self.assertGreaterEqual(len(state["steps"]), 2)
                self.assertLessEqual(len(state["steps"]), 8)
                self.assertTrue(state["alt"])
        self.assertEqual(self.demos["C13-D03"]["stepper"], "length")
        self.assertEqual(page.count("Common wrong turn"), 4)
        self.assertGreaterEqual(page.count("What this does not settle"), 4)
        # Misconceptions rest on sentences the chapter itself states.
        text = (LAB.parent / "Manuscript" / "part-iii" / "13-learning-to-choose.md").read_text()
        flat = re.sub(r"\s+", " ", text).lower()
        for phrase in ("the gradient can look stable while training on the wrong distribution",
                       "it has not thereby identified",
                       "A training curve measured by the verifier cannot be renamed a true-success curve",
                       "The additional score did not discover an efficient policy"):
            self.assertIn(phrase.lower(), flat)

    def test_static_text_defines_symbols_once(self):
        page = html.unescape(self.page)
        self.assertEqual(page.count("sigma is the logistic function, sigma(z) = 1 / (1 + e^(-z))"), 1)
        self.assertEqual(page.count("pi_phi(a_t | o_t) is the probability"), 1)
        self.assertEqual(page.count("pi_phi(a_t | o_t) is the policy's probability of action a_t"), 1)
        self.assertIn("sampled update in the form of Equation (13.2), with a baseline equal to the policy's expected reward and softmax logits", page)
        self.assertIn("a single sampled rate is a noisy view of the exact number", page)

    def test_displayed_equations_are_chapter_equations(self):
        import sys
        for path in (str(LAB / "src"), str(LAB / "tools" / "readers" / "engine")):
            if path not in sys.path:
                sys.path.insert(0, path)
        spec = importlib.util.spec_from_file_location("ch13_reader_module", MODULE)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        text = (LAB.parent / "Manuscript" / "part-iii" / "13-learning-to-choose.md").read_text()

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\(?:[,;:!]|quad|qquad)", "", t)
            return re.sub(r"[\s{}]", "", t)

        chapter = norm(text)
        for demo in module.CHAPTER["demos"]:
            for tex in demo["equations"]:
                self.assertIn(norm(tex).rstrip(".,;"), chapter, tex)
            self.assertEqual(demo["source_anchor"], re.sub(r"[^a-z0-9]+", "-", demo["source_section"].lower()).strip("-"))
            self.assertRegex(text, rf"(?m)^#{{1,3}} {re.escape(demo['source_section'])}$")

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"]) + " " + " ".join(state["steps"]) + " " + state["alt"]
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_every_control_combination_renders_with_a_hand_calculation(self):
        for demo in self.data["demos"]:
            self.assertEqual(len(demo["states"]), math.prod(len(c["values"]) for c in demo["controls"]))
            for state in demo["states"].values():
                self.assertTrue(state["image"].startswith("data:image/svg+xml"))
                self.assertRegex(state["interpretation"], r"[\d.)]+ [x/+-] .*= [\d(.-]")

    def test_links_and_offline(self):
        for href in ("../../notebooks/13-finite-policy-learning.ipynb", "../../skills/maa-13-finite-policy-learning/SKILL.md"):
            self.assertIn(f'href="{href}"', self.page)
        # The index link target is set by the shared configuration (it was changed to ../../index.html during this work).
        self.assertRegex(self.page, r'href="(\.\./)+index\.html"')
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual(report["states_checked"], 48)
        self.assertEqual(report["resets_checked"], 4)
        self.assertGreaterEqual(report["predictions_checked"], 4)
        self.assertGreater(report["stepper_moves"], 0)


@unittest.skipUnless(MODULE.is_file(), "Chapter 13 module missing")
class Chapter13FreshBuildTests(unittest.TestCase):
    def test_fresh_build_succeeds_and_is_reproducible(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            first = build_into(a)
            if first is None:
                self.skipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
            second = build_into(b)
            self.assertEqual(first.read_bytes(), second.read_bytes(), "the build is not reproducible")


if __name__ == "__main__":
    unittest.main()

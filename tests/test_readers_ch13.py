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

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)]
            yield values, dict(state["metrics"]), state


def stream_values():
    return {"Release task: -0.05, 0, 1": [-0.05, 0.0, 1.0], "Chapter exercise: 1, 2": [1.0, 2.0]}


@unittest.skipUnless(MODULE.is_file(), "Chapter 13 module missing")
class Chapter13ReaderTests(Chapter13Base):
    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C13-D01", "C13-D02", "C13-D03", "C13-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [6, 8, 8, 6])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_return_to_go_by_backward_recursion(self):
        seen = {}
        for (stream, gamma), m, _ in self.states("C13-D01"):
            rewards = stream_values()[stream]
            G, ahead = [0.0] * len(rewards), 0.0
            for t in reversed(range(len(rewards))):  # G_t = r_t + gamma G_{t+1}
                ahead = rewards[t] + gamma * ahead
                G[t] = ahead
            for t, g in enumerate(G):
                self.assertEqual(m[f"G_{t}"], f"{g:.3f}", (stream, gamma, t))
            self.assertEqual(m["Sum of rewards, no discount"], f"{sum(rewards):.3f}")
            self.assertEqual(m["Weight on the last reward in G_0"], f"{gamma ** (len(rewards) - 1):.3f}")
            seen[(stream, gamma)] = G
        # The chapter's Exercise 1: rewards 1, 2 with gamma 0.5 give a first return of 1 + 0.5 x 2 = 2.
        self.assertAlmostEqual(seen[("Chapter exercise: 1, 2", 0.5)][0], 2.0)
        self.assertAlmostEqual(seen[("Chapter exercise: 1, 2", 0.9)][0], 2.8)
        self.assertAlmostEqual(seen[("Release task: -0.05, 0, 1", 0.5)][0], -0.05 + 0.25)
        self.assertIn("G_0 = 1.0 + 0.5 x 2.0 = 2.000", self.page)

    def test_d02_gradient_by_finite_difference_and_book_values(self):
        def J(phi, net):
            p = 1 / (1 + math.exp(-phi))
            return p * net + (1 - p) * 0.55

        for (phi, q), m, _ in self.states("C13-D02"):
            net = q - 0.05
            h = 1e-6
            numeric = (J(phi + h, net) - J(phi - h, net)) / (2 * h)
            p = 1 / (1 + math.exp(-phi))
            self.assertEqual(m["Retrieve probability p"], f"{p:.4f}")
            self.assertEqual(m["Expected utility J"], f"{J(phi, net):.4f}")
            self.assertEqual(m["Gradient dJ/dphi"], f"{numeric:.4f}", (phi, q))
            self.assertEqual(m["Gradient by Equation (13.2) sum"], f"{numeric:.4f}", (phi, q))
        book = dict(self.demos["C13-D02"]["states"]["1,0"]["metrics"])  # phi = 0, retrieve success 0.80
        self.assertEqual((book["Retrieve probability p"], book["Expected utility J"], book["Gradient dJ/dphi"]),
                         ("0.5000", "0.6500", "0.0500"))  # the chapter: utility 0.65, gradient 0.05

    def test_d03_matches_an_independent_one_step_reinforce_run(self):
        success = [0.9, 0.2]
        for (ranking, episodes), m, _ in self.states("C13-D03"):
            rewards = [1.0, 2.0] if ranking.startswith("Action 1") else [2.0, 1.0]
            finals = {}
            for seed in (3, 11):
                rng = random.Random(seed)
                logits = [0.0, 0.0]
                for _ in range(int(episodes)):
                    mx = max(logits)
                    w = [math.exp(v - mx) for v in logits]
                    p = [v / sum(w) for v in w]
                    u, cum, chosen = rng.random(), 0.0, 1
                    for i, pi in enumerate(p):
                        cum += pi
                        if u < cum:
                            chosen = i
                            break
                    base = sum(pi * r for pi, r in zip(p, rewards))
                    for i in range(2):
                        logits[i] += 0.08 * (rewards[chosen] - base) * ((i == chosen) - p[i])
                mx = max(logits)
                w = [math.exp(v - mx) for v in logits]
                finals[seed] = [v / sum(w) for v in w]
            p3 = finals[3]
            self.assertEqual(m["Start: verifier reward"], f"{(rewards[0] + rewards[1]) / 2:.2f}")
            self.assertEqual(m["Start: true success"], "0.550")
            self.assertEqual(m["Seed 3: true success"], f"{p3[0] * 0.9 + p3[1] * 0.2:.3f}", (ranking, episodes))
            self.assertEqual(m["Seed 11: true success"], f"{finals[11][0] * 0.9 + finals[11][1] * 0.2:.3f}", (ranking, episodes))
            self.assertEqual(m["Seed 3: verifier reward"], f"{p3[0] * rewards[0] + p3[1] * rewards[1]:.3f}")

    def test_d03_direction_of_the_mismatch(self):
        end = {tuple(v): float(m["Seed 3: true success"]) for v, m, _ in self.states("C13-D03")}
        misaligned = [k for k in end if k[0].startswith("Action 1")]
        aligned = [k for k in end if k[0].startswith("Action 0")]
        for k in misaligned:
            self.assertLess(end[k], 0.55)
        for k in aligned:
            self.assertGreater(end[k], 0.55)
        # Longer training moves the result further in the same direction.
        ordered = sorted(misaligned, key=lambda k: k[1])
        self.assertTrue(all(end[a] > end[b] for a, b in zip(ordered, ordered[1:])))

    def test_d03_lab_function_agrees_on_the_default_case(self):
        out = evaluate({"rewards": [1, 2], "success_probabilities": [0.9, 0.2], "terminal_potentials": [0, 0], "episodes": 120,
                        "seeds": [3, 11], "learning_rate": 0.08, "discount": 1, "evaluation_runs": 200})
        self.assertEqual(out["metrics"]["verifier_optimal_action"], 1)
        self.assertEqual(out["metrics"]["task_optimal_action"], 0)
        state = next(m for v, m, _ in self.states("C13-D03") if v[1] == 120 and v[0].startswith("Action 1"))
        self.assertEqual(state["Seed 3: true success"], f"{out['metrics']['runs'][0]['expected_external_success']:.3f}")

    def test_d04_shaping_telescopes_and_ranking(self):
        for (evidence, d), m, _ in self.states("C13-D04"):
            rewards = [-0.05, 1.0]
            pots = [0.0, evidence, 0.0]
            shaped = [rewards[t] + pots[t + 1] - pots[t] for t in range(2)]
            self.assertAlmostEqual(sum(shaped), sum(rewards))  # interior potential cancels
            self.assertEqual(m["Retrieve route G_0 (success case)"], f"{sum(rewards):.2f}")
            self.assertEqual(m["Retrieve route G'_0 (success case)"], f"{sum(shaped):.2f}")
            direct, retrieve = 0.55 + d, 0.80 - 0.05
            self.assertEqual(m["Direct route G'_0"], f"{direct:.2f}")
            self.assertEqual(m["Retrieve route G'_0"], f"{retrieve:.2f}")
            expected = "tie" if abs(direct - retrieve) < 1e-9 else ("Answer directly" if direct > retrieve else "Retrieve then answer")
            self.assertEqual(m["Ranked first after shaping"], expected, (evidence, d))
        # A zero end potential preserves the ranking, 0.2 is an exact tie, 0.5 reverses it.
        ranks = {tuple(v): m["Ranked first after shaping"] for v, m, _ in self.states("C13-D04")}
        self.assertEqual(ranks[(0.4, 0.0)], "Retrieve then answer")
        self.assertEqual(ranks[(0.4, 0.2)], "tie")
        self.assertEqual(ranks[(1.0, 0.5)], "Answer directly")

    def test_d04_closing_sentence_matches_the_state(self):
        # Reviewer finding g5-01: with direct end potential 0 the shaped returns equal the originals.
        by = {tuple(v): s["interpretation"] for v, _, s in self.states("C13-D04")}
        for key in ((0.4, 0.0), (1.0, 0.0)):
            text = by[key]
            self.assertIn("The direct route's end potential is 0, so the shaped returns equal the original ones", text)
            self.assertIn("direct = 0.55 + 1 x 0.0 = 0.55", text)
            self.assertNotIn("A small end potential", text)
            self.assertNotIn("no longer the true ones", text)
        for key in ((0.4, 0.2), (1.0, 0.2)):
            self.assertIn("tie", by[key])
            self.assertNotIn("A small end potential", by[key])
        for key in ((0.4, 0.5), (1.0, 0.5)):
            self.assertIn("The direct route now ranks first", by[key])

    def test_static_text_matches_every_state_and_defines_symbols(self):
        page = html.unescape(self.page)
        # g5-02: the gain is state dependent, so the explanation names the default.
        self.assertNotIn("(0.75 - 0.55 = 0.20) times p", page)
        self.assertIn("at the default 0.80 it is 0.75 - 0.55 = 0.20", page)
        self.assertAlmostEqual(0.70 - 0.05 - 0.55, 0.10)  # the 0.70 state has gain 0.10, so a fixed 0.20 would be wrong there
        # g5-03: sigma and the policy symbols are defined where Equation (13.2) is shown.
        self.assertEqual(page.count("sigma is the logistic function, sigma(z) = 1 / (1 + e^(-z))"), 1)
        self.assertEqual(page.count("pi_phi(a_t | o_t) is the probability"), 1)
        self.assertEqual(page.count("pi_phi(a_t | o_t) is the policy's probability of action a_t"), 1)
        # g5-04 and g5-08: the training rule and the source of the numbers are stated.
        self.assertNotIn("Training updates the policy by Equation (13.2)", page)
        self.assertIn("sampled update in the form of Equation (13.2), with a baseline equal to the policy's expected reward and softmax logits", page)
        self.assertIn("separate from the chapter's noisy-verifier example", page)
        # g5-05: the direct route's end potential is named in the symbols.
        self.assertNotIn("here 0 at the start and at the end, and a chosen value", page)
        self.assertIn("a chosen end value on the direct route", page)
        # g5-06 and g5-07
        self.assertNotIn("would be much better", page)
        self.assertIn("With a logistic parameterization", page)
        self.assertNotIn("G_0, a discounted sum and a plain sum", page)

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
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
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
        for href in ("../../notebooks/13-finite-policy-learning.ipynb", "../../skills/maa-13-finite-policy-learning/SKILL.md",
                     "../index.html"):
            self.assertIn(f'href="{href}"', self.page)
            self.assertTrue((LAB / "readers" / "13-finite-policy-learning" / href).resolve().exists(), href)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual(report["states_checked"], 28 + 0)
        self.assertEqual(report["resets_checked"], 4)


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

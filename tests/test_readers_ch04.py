"""Chapter 4 laboratory reader: independent hand checks of the built page.

The reader is built into a temporary directory, then every displayed number is
recomputed here from the chapter's own arithmetic (the two workflows, the
branching threshold, sampled depth-4 trees, the depth-two tree, the chain rule
and repeated failure), by independent methods, not read back from the module
that produced the page.
"""
from __future__ import annotations

import hashlib
import html
import json
import math
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

import numpy as np

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
SLUG = "04-permission-reachability"

D1_CASES = ["none", "review_release", "draft_review", "transfer"]
D2_P = [0.3, 0.5, 0.7]
D2_SAMPLE = [1, 2, 3, 4]
D3_D = [2, 3]
D3_P = [0.4, 0.6, 0.8]
D4_GRANT = [0.9, 0.7, 0.4, 0.0]
D4_STEPS = [3, 10, 20]


def builder_python():
    import importlib.util
    import sys
    if all(importlib.util.find_spec(m) for m in ("numpy", "matplotlib", "jinja2")):
        return sys.executable
    for candidate in (LAB / ".venv/bin/python", LAB / ".venv/Scripts/python.exe"):
        if candidate.exists():
            probe = subprocess.run([str(candidate), "-c", "import numpy, matplotlib, jinja2"], capture_output=True)
            if probe.returncode == 0:
                return str(candidate)
    return None


def build(python, out):
    return subprocess.run([python, str(WRAPPER), "--chapters", "4", "--out", out], capture_output=True, text=True,
                          timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))


def payload(text):
    return json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))


def reachable(edges, denied, start):
    """Breadth-first layers by hand: states reached after exactly t moves, first time seen."""
    seen = {start: 0}
    frontier = [start]
    t = 0
    while frontier:
        t += 1
        nxt = []
        for a, b in edges:
            if a in frontier and (a, b) != denied and b not in seen:
                seen[b] = t
                nxt.append(b)
        frontier = nxt
    return seen


DOC_EDGES = [("draft", "review"), ("review", "release"), ("review", "draft"), ("draft", "archive")]
TRF_EDGES = [("queued", "approved"), ("approved", "sent")]
CASE_SPEC = {
    "none": (DOC_EDGES, None, "draft", 4),
    "review_release": (DOC_EDGES, ("review", "release"), "draft", 4),
    "draft_review": (DOC_EDGES, ("draft", "review"), "draft", 4),
    "transfer": (TRF_EDGES, ("queued", "approved"), "queued", 3),
}


def survival_by_bisection(p, d):
    """Smallest root q of q = (1 - p + p q)^d in [0, 1) by bisection on the lower root; survival is 1 - q."""
    f = lambda q: (1 - p + p * q) ** d - q
    lo, hi = 0.0, 1.0 - 1e-9
    if f(hi) >= 0:
        return 0.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 1.0 - (lo + hi) / 2


def binom_pmf(n, k, p):
    return math.comb(n, k) * p ** k * (1 - p) ** (n - k)


def branching_levels(p, depth):
    """Distribution of the number of open vertices at each level of a binary tree, by convolution (independent of the module)."""
    dist = {1: 1.0}
    out = [dict(dist)]
    for _ in range(depth):
        nxt = {}
        for z, w in dist.items():
            for k in range(2 * z + 1):
                nxt[k] = nxt.get(k, 0.0) + w * binom_pmf(2 * z, k, p)
        dist = nxt
        out.append(dict(dist))
    return out


def sample_paths(seed, p):
    """Open root-to-bottom paths of a depth-4 tree drawn with one uniform per non-root vertex, by explicit path walking."""
    u = np.random.RandomState(seed).random_sample(31)
    count = 0
    for leaf in range(15, 31):
        v, ok = leaf, True
        while v > 0:
            if not u[v] < p:
                ok = False
                break
            v = (v - 1) // 2
        count += ok
    return count


class Chapter4ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.python = builder_python()
        if cls.python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls.tmp = tempfile.TemporaryDirectory()
        run = build(cls.python, cls.tmp.name)
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls.tmp.name) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def state(self, demo_id, *idx):
        return self.demos[demo_id]["states"][",".join(str(i) for i in idx)]

    def metrics(self, demo_id, *idx):
        return dict(self.state(demo_id, *idx)["metrics"])

    # Structure

    def test_four_demonstrations_and_budgets(self):
        self.assertEqual(list(self.demos), ["C04-D01", "C04-D02", "C04-D03", "C04-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [4, 12, 6, 12])
        for d in self.data["demos"]:
            self.assertLessEqual(len(d["states"]), 12)
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_optional_features_are_present(self):
        text = html.unescape(self.page)
        self.assertEqual(self.data["demos"][0]["id"], "C04-D01")
        self.assertIn("Ask the chapter skill", text)
        self.assertEqual(text.count("Common wrong turn:"), 4)
        self.assertGreaterEqual(text.count("What this does not settle"), 4)  # one panel per demonstration
        for d in self.data["demos"]:
            for state in d["states"].values():
                self.assertGreaterEqual(len(state["steps"]), 2)
                self.assertLessEqual(len(state["steps"]), 8)
                for step in state["steps"]:
                    self.assertLessEqual(len(step), 240)
        self.assertIn("Your prediction", text)

    # Demonstration 1: permission filter, document workflow and the notebook's transfer workflow

    def test_d01_reachability_by_hand(self):
        for i, case in enumerate(D1_CASES):
            edges, denial, start, n_nodes = CASE_SPEC[case]
            seen = reachable(edges, denial, start)
            m = self.metrics("C04-D01", i)
            goal = "release" if case != "transfer" else "sent"
            Goal = goal.capitalize()
            self.assertEqual(m["States reached"], f"{len(seen)} of {n_nodes}", case)
            self.assertEqual(m[f"{Goal} reachable with these grants"], "yes" if goal in seen else "no")
            self.assertEqual(m[f"{Goal} reachable with every grant"], "yes")
            interpretation = self.state("C04-D01", i)["interpretation"]
            self.assertIn(f"states with no permitted path = {n_nodes} - {len(seen)} = {n_nodes - len(seen)}", interpretation)
        default = self.metrics("C04-D01", 0)
        self.assertEqual(default["Shortest permitted path to release"], "draft, review, release")
        self.assertEqual(default["Reached states with no way out"], "release, archive")
        self.assertIn("Reach = 1 + 2 + 1 = 4 of 4 states", self.state("C04-D01", 0)["interpretation"])
        # The loop review to draft is permitted but adds no new state.
        self.assertIn("permitted loop review to draft leads to a state already reached", self.state("C04-D01", 0)["interpretation"])
        # Denying review to release leaves a raw path but no permitted one, and the sum drops to 1 + 2 = 3.
        denied = self.state("C04-D01", 1)
        self.assertIn("Reach = 1 + 2 = 3 of 4 states", denied["interpretation"])
        self.assertEqual(dict(denied["metrics"])["Shortest permitted path to release"], "none")
        # Denying draft to review makes review and release both unreachable: only draft and archive.
        self.assertIn("Reach = 1 + 1 = 2 of 4 states", self.state("C04-D01", 2)["interpretation"])
        self.assertNotIn("permitted loop", self.state("C04-D01", 2)["interpretation"])

    def test_d01_transfer_case_matches_the_notebook(self):
        # Notebook transfer: queued, approved, sent; queued to approved denied, approved to sent allowed.
        data = json.loads((LAB / "data" / "examples" / "ch04.json").read_text())
        self.assertEqual(data["nodes"], ["queued", "approved", "sent"])
        denied = [(e["from"], e["to"]) for e in data["edges"] if not e["allowed"]]
        self.assertEqual(denied, [("queued", "approved")])
        state = self.state("C04-D01", 3)
        m = dict(state["metrics"])
        self.assertEqual(m["States reached"], "1 of 3")
        self.assertEqual(m["Shortest permitted path to sent"], "none")
        self.assertEqual(m["Reached states with no way out"], "queued")
        self.assertIn("Act(queued) = {approved}; the grant rule G keeps no move", state["interpretation"])
        self.assertNotIn("keeps {nothing}", state["interpretation"])
        # With every grant the path exists (the unfiltered curve reaches all three states within two moves).
        self.assertEqual(reachable(TRF_EDGES, None, "queued"), {"queued": 0, "approved": 1, "sent": 2})
        self.assertIn("Within 1 move the controller reaches 1 of 3 states", state["interpretation"])
        self.assertIn("no number of retries adds it", state["interpretation"])

    def test_d01_budget_sentence_matches_layers(self):
        # Within one move the default workflow reaches draft, review and archive: 3 states.
        self.assertIn("Within 1 move the controller reaches 3 of 4 states", self.state("C04-D01", 0)["interpretation"])
        self.assertIn("Within 1 move the controller reaches 3 of 4 states", self.state("C04-D01", 1)["interpretation"])
        self.assertIn("Within 1 move the controller reaches 2 of 4 states", self.state("C04-D01", 2)["interpretation"])

    # Demonstration 2: sampled depth-4 trees against the infinite threshold

    def test_d02_expected_counts_and_path_chances_by_convolution(self):
        for pi, p in enumerate(D2_P):
            levels = branching_levels(p, 4)
            expected = sum(z * w for z, w in levels[4].items())
            self.assertAlmostEqual(expected, (2 * p) ** 4, places=9)
            exists = 1 - levels[4][0]
            survival = 0.0 if 2 * p <= 1 + 1e-12 else survival_by_bisection(p, 2)
            for si in range(4):
                m = self.metrics("C04-D02", pi, si)
                self.assertEqual(m["Expected open paths at depth 4, (dp)^4"], f"{expected:.3f}")
                self.assertEqual(m["Chance a path to depth 4 exists"], f"{exists:.3f}")
                self.assertEqual(m["Chance one committed run finishes, p^4"], f"{p ** 4:.4f}")
                self.assertEqual(m["Chance the root's cluster is infinite"], f"{survival:.3f}")
                regime = "below" if p < 0.5 else ("at" if p == 0.5 else "above")
                self.assertEqual(m["Edge probability against 1/2"], f"{regime} the threshold")
        # d = 2 closed form for survival above one half: 1 - ((1 - p) / p)^2.
        s = float(self.metrics("C04-D02", 2, 0)["Chance the root's cluster is infinite"])
        self.assertAlmostEqual(s, 1 - (0.3 / 0.7) ** 2, places=3)

    def test_d02_depth_two_matches_the_chapter(self):
        # The recursion at depth 2 equals the chapter's depth-two formula 1 - [1 - p(1 - (1 - p)^2)]^2 and its 0.753984 at p = 0.6.
        r2 = 1 - (1 - 0.6 * (1 - (1 - 0.6) ** 2)) ** 2
        self.assertAlmostEqual(r2, 0.753984, places=6)
        # Full enumeration of the six edges of the depth-two tree at p = 0.6 agrees.
        total = 0.0
        for mask in range(2 ** 6):
            e = [(mask >> i) & 1 for i in range(6)]
            prob = math.prod(0.6 if x else 0.4 for x in e)
            if (e[0] and (e[2] or e[3])) or (e[1] and (e[4] or e[5])):
                total += prob
        self.assertAlmostEqual(total, 0.753984, places=6)

    def test_d02_samples_by_explicit_path_walking(self):
        seeds = {1: 8, 2: 6, 3: 3, 4: 15}
        expected = {1: [0, 0, 0], 2: [0, 1, 2], 3: [1, 2, 2], 4: [1, 5, 7]}
        for si, sample in enumerate(D2_SAMPLE):
            counts = [sample_paths(seeds[sample], p) for p in D2_P]
            self.assertEqual(counts, expected[sample], sample)
            self.assertEqual(counts, sorted(counts))  # the same draw opens more edges as p grows
            for pi in range(3):
                m = self.metrics("C04-D02", pi, si)
                self.assertEqual(m["Open paths to the bottom row in this draw"], str(counts[pi]))
                self.assertIn(f"This draw shows {counts[pi]} {'path' if counts[pi] == 1 else 'paths'}", self.state("C04-D02", pi, si)["interpretation"])
        # The prediction: below the threshold a finite sample can still show a path (draw 3 at p = 0.3).
        self.assertEqual(self.metrics("C04-D02", 0, 2)["Open paths to the bottom row in this draw"], "1")
        # Above the threshold a draw can show none (draw 1 at p = 0.7), and the module says so.
        self.assertIn("can still show no path", self.state("C04-D02", 2, 0)["interpretation"])

    def test_d02_recursion_is_written_with_the_state_numbers(self):
        text = self.state("C04-D02", 1, 0)["interpretation"]  # p = 0.5
        # The chain prints each r_k unrounded (to six figures) so the next line can be redone from the printed value.
        self.assertIn("r1 = 1 - (1 - 0.5 x 1)^2 = 0.75;", text)
        self.assertIn("r2 = 1 - (1 - 0.5 x 0.75)^2 = 0.609375;", text)
        self.assertIn("r3 = 1 - (1 - 0.5 x 0.609375)^2 = 0.516541;", text)
        self.assertIn("(2 x 0.5)^4 = 1.000", text)
        self.assertIn("d x p = 2 x 0.5 = 1, not above 1, so its survival is 0", text)

    # Demonstration 3: possible, expected and completed

    def test_d03_depth_two_tree(self):
        for di, d in enumerate(D3_D):
            for pi, p in enumerate(D3_P):
                m = self.metrics("C04-D03", di, pi)
                branch = p * (1 - (1 - p) ** d)
                exists = 1 - (1 - branch) ** d
                self.assertEqual(m["A path to depth two exists"], f"{exists:.6f}", (d, p))
                self.assertEqual(m["Committed run finishes (p^2)"], f"{p * p:.2f}")
                self.assertEqual(m["Expected open depth-two descendants (d^2 x p^2)"], f"{d * d * p * p:.2f}")
                self.assertEqual(m["Existence minus committed run"], f"{exists - p * p:.6f}")
        # Independent check by exhaustive enumeration of every edge state for the binary tree at p = 0.4.
        p, edges = 0.4, 6
        total = 0.0
        for mask in range(2 ** edges):
            e = [(mask >> i) & 1 for i in range(edges)]  # e[0], e[1] root edges; e[2:4] under child 0; e[4:6] under child 1
            prob = math.prod(p if x else 1 - p for x in e)
            ok = (e[0] and (e[2] or e[3])) or (e[1] and (e[4] or e[5]))
            total += prob if ok else 0.0
        self.assertEqual(self.metrics("C04-D03", 0, 0)["A path to depth two exists"], f"{total:.6f}")
        # The chapter's numbers: 1.44, 0.753984 and 0.36 at p = 0.6 with two children.
        book = self.metrics("C04-D03", 0, 1)
        self.assertEqual(book["Expected open depth-two descendants (d^2 x p^2)"], "1.44")
        self.assertEqual(book["A path to depth two exists"], "0.753984")
        self.assertEqual(book["Committed run finishes (p^2)"], "0.36")
        self.assertIn("below 1, yet a path exists", self.state("C04-D03", 0, 0)["interpretation"])
        # The worked steps repeat the chapter's 0.504 per branch.
        self.assertIn("0.6 x 0.84 = 0.504", " ".join(self.state("C04-D03", 0, 1)["steps"]))

    # Demonstration 4: chain rule, growth of descendants and repeated failure

    def test_d04_chain_rule_and_counts(self):
        for gi, grant in enumerate(D4_GRANT):
            for ti, steps in enumerate(D4_STEPS):
                m = self.metrics("C04-D04", gi, ti)
                p = 0.95 * 0.98 * grant * 0.80
                self.assertEqual(m["Edge success p"], f"{p:.5f}")
                self.assertEqual(m["Open children per vertex (d x p, d = 2)"], f"{2 * p:.5f}")
                self.assertEqual(m["Against the threshold 1/d = 0.5"], "above the threshold" if 2 * p > 1 else "below the threshold")
                count_key = f"Expected open descendants at depth {steps} ((dp)^{steps})"
                count = math.exp(steps * math.log(2 * p)) if p else 0.0
                shown = m[count_key]
                if 0 < count < 0.001 or count >= 100000:
                    self.assertAlmostEqual(float(shown) / count, 1.0, delta=0.006)
                else:
                    self.assertAlmostEqual(float(shown), count, delta=0.0051 if count < 10 else 0.0051)
                chain_key = f"One chain of {steps} steps (p^{steps})"
                chain = math.exp(steps * math.log(p)) if p else 0.0
                if 0 < chain < 0.001:
                    self.assertAlmostEqual(float(m[chain_key]) / chain, 1.0, delta=0.006)
                else:
                    self.assertEqual(m[chain_key], f"{chain:.5f}")
                self.assertEqual(m["Grant rate that gives d x p = 1"], f"{0.5 / (0.95 * 0.98 * 0.80):.4f}")
        book = self.state("C04-D04", 0, 0)
        self.assertEqual(dict(book["metrics"])["Edge success p"], "0.67032")  # the chapter's working case
        tight = self.metrics("C04-D04", 2, 0)
        self.assertEqual(tight["Edge success p"], "0.29792")  # the chapter's tightened case
        self.assertEqual(tight["Open children per vertex (d x p, d = 2)"], "0.59584")
        self.assertGreater(0.70, 0.5 / 0.7448)   # grant 0.70 sits above the break-even 0.6713
        self.assertLess(0.40, 0.5 / 0.7448)

    def test_d04_repeated_failure_by_independent_arithmetic(self):
        # Chance that n runs in a row all fail, one run being a chain of T steps with success p^T.
        for gi, grant in enumerate(D4_GRANT):
            for ti, steps in enumerate(D4_STEPS):
                m = self.metrics("C04-D04", gi, ti)
                p = 0.95 * 0.98 * grant * 0.80
                s = p ** steps
                for n, key in ((10, "Chance 10 runs in a row all fail"), (10000, "Chance 10,000 runs in a row all fail")):
                    fail = (1 - s) ** n
                    miss = 1 - fail
                    shown = m[key]
                    if shown == "1":
                        self.assertEqual(s, 0.0)
                    elif shown.startswith("1 - "):
                        self.assertAlmostEqual(float(shown[4:]) / (n * s), 1.0, delta=0.01)
                        self.assertLess(miss, 1e-5)
                    elif shown.startswith("about "):
                        # Underflows a decimal: compare mantissa and exponent, from n x log10(1 - s), by logarithms.
                        log10 = n * math.log10(1 - s)
                        mantissa, exponent = shown[6:].split("e")
                        self.assertEqual(int(exponent), math.floor(log10))
                        self.assertAlmostEqual(float(mantissa), 10 ** (log10 - math.floor(log10)), delta=0.06 * float(mantissa))
                        self.assertLess(log10, -100)
                    else:
                        self.assertEqual(shown, f"{fail:.4f}" if fail >= 0.001 else f"{fail:.3g}", (grant, steps, n))
        # Chapter: one in a million per run, 10,000 failures in a row has probability about 0.99005.
        self.assertAlmostEqual((1 - 1e-6) ** 10000, 0.99005, places=5)
        # A grant of 0 removes the edge: every run fails, probability exactly 1, and the module says structural failure.
        zero = self.state("C04-D04", 3, 0)
        self.assertEqual(dict(zero["metrics"])["Chance 10 runs in a row all fail"], "1")
        self.assertIn("structural failure", zero["interpretation"])
        self.assertEqual(dict(zero["metrics"])["Edge success p"], "0.00000")

    def test_d04_depth_twenty_ratio_and_rounding_notes(self):
        # The chapter quotes (0.90 / 0.40)^20, about 11.057 million, for the exact products.
        self.assertAlmostEqual((0.90 / 0.40) ** 20 / 1e6, 11.057, places=2)
        ratio = (0.95 * 0.98 * 0.9 * 0.8 * 2) ** 20 / (0.95 * 0.98 * 0.4 * 0.8 * 2) ** 20
        self.assertAlmostEqual(ratio / 1e6, 11.057, places=2)
        tight = self.state("C04-D04", 2, 2)["interpretation"]  # grant 0.40, T = 20
        self.assertIn("(0.90 / 0.40)^20 = 11.057 million", tight)
        self.assertIn("rounds the mean to 0.596 and quotes about 0.000032 at depth 20; the unrounded mean 0.59584 gives 3.18e-05", tight)
        working = self.state("C04-D04", 0, 2)["interpretation"]  # grant 0.90, T = 20
        self.assertIn("rounds the mean to 1.34 and quotes about 348 at depth 20; the unrounded mean 1.34064 gives 351.76", working)
        self.assertAlmostEqual(1.34 ** 20, 348, delta=2)
        self.assertAlmostEqual(0.596 ** 20, 3.2e-5, delta=3e-6)

    def test_d04_small_probabilities_are_not_rounded_to_zero(self):
        state = self.state("C04-D04", 2, 1)  # grant 0.40, T = 10
        chain = (0.95 * 0.98 * 0.4 * 0.8) ** 10
        self.assertAlmostEqual(chain, 5.51e-06, delta=1e-8)
        self.assertEqual(dict(state["metrics"])["One chain of 10 steps (p^10)"], "5.51e-06")
        self.assertIn("0.29792^10 = 5.51e-06", state["interpretation"])
        self.assertNotIn("0.00001", state["interpretation"])
        svg = self.svg_of("C04-D04", "2,1")
        self.assertNotIn(">0.0000<", svg)
        # Grant 0.70, T = 10 is 0.00148, above the notation cutoff.
        self.assertEqual(dict(self.state("C04-D04", 1, 1)["metrics"])["One chain of 10 steps (p^10)"], "0.00148")
        # 10,000 runs at this chain success: (1 - 5.51e-06)^10000 = 0.946.
        self.assertEqual(dict(state["metrics"])["Chance 10,000 runs in a row all fail"], "0.9464")

    def test_d04_grant_zero_is_annotated(self):
        for key in ("3,0", "3,1", "3,2"):
            self.assertIn("edge removed", self.svg_of("C04-D04", key))
        self.assertNotIn("edge removed", self.svg_of("C04-D04", "0,0"))

    # Text carried over from the earlier review round

    def test_application_does_not_generalize_the_hour(self):
        self.assertNotIn("found in an hour", self.page)
        self.assertIn("A missing grant shows up in the list of states and moves; a prompt cannot add it.", self.page)

    def test_note_names_what_changed(self):
        notes = {}
        for di, d in enumerate(D3_D):
            for pi, p in enumerate(D3_P):
                notes[(d, p)] = self.state("C04-D03", di, pi)["interpretation"]
        self.assertIn("This is the chapter's constructed example.", notes[(2, 0.6)])
        for p in (0.4, 0.8):
            self.assertIn(f"(two children), with p changed to {p}.", notes[(2, p)])
            self.assertNotIn("child count changed", notes[(2, p)])
        self.assertIn("with the child count changed to 3.", notes[(3, 0.6)])
        self.assertIn("child count changed to 3 and p changed to 0.4.", notes[(3, 0.4)])

    def test_equation_blocks_are_explained(self):
        page = html.unescape(self.page)
        self.assertIn("chapter's instance (d = 2, p = 0.6)", page)
        self.assertIn("1 - [1 - p(1 - (1 - p)^d)]^d", page)
        self.assertIn("(dp)^T with T = 2 is (dp)^2", page)
        branch = 0.4 * (1 - 0.6 ** 3)
        self.assertEqual(self.metrics("C04-D03", 1, 0)["A path to depth two exists"], f"{1 - (1 - branch) ** 3:.6f}")

    def svg_of(self, demo_id, key):
        import base64
        return base64.b64decode(self.demos[demo_id]["states"][key]["image"].split(",", 1)[1]).decode()

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 4)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".,;")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        text = (LAB.parent / chapter["source_path"]).read_text(encoding="utf-8")
        inline = {norm(m) for m in re.findall(r"\$([^$\n]+)\$", text)}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertGreaterEqual(len(alts), 5)
        shown = {norm(html.unescape(t)) for t in alts}
        for tex in shown:
            self.assertTrue(tex in allowed or tex in inline, tex)
        # Equation (4.3), the percolation definition, is now displayed.
        eq43 = next(norm(e["tex"]) for e in chapter["equations"] if e["number"] == "4.3")
        self.assertIn(eq43, shown)

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"]) + " " + " ".join(state["steps"])
        for bad in ("\u2014", "\u2013", "--", "\u2212"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_accessibility_and_offline(self):
        self.assertIn('<a class="skip" href="#main">', self.page)
        self.assertIn("<noscript>", self.page)
        self.assertGreaterEqual(self.page.count('aria-live="polite"'), 4)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))
        for d in self.data["demos"]:
            for c in d["controls"]:
                self.assertIn(f'<label for="{d["id"]}-{c["key"]}">', self.page)

    def test_alt_text_describes_each_state(self):
        for d in self.data["demos"]:
            for key, state in d["states"].items():
                self.assertTrue(state["image"].startswith("data:image/svg+xml;base64,"))
                self.assertTrue(state["interpretation"])
        self.assertIn("a binary tree of depth 4 drawn with edge probability 0.30", html.unescape(self.page))

    def test_every_control_combination_renders(self):
        for demo in self.data["demos"]:
            n = 1
            for c in demo["controls"]:
                n *= len(c["values"])
            self.assertEqual(len(demo["states"]), n, demo["id"])

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["labelled_controls"]), (34, 7))
        self.assertEqual(report["ask_skill"], 1)
        self.assertGreaterEqual(report["predictions_checked"], 11)
        self.assertEqual(report["panels_checked"], 8)

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as out:
            run = build(self.python, out)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            fresh = Path(out) / SLUG / "reader.html"
            self.assertEqual(hashlib.sha256(fresh.read_bytes()).hexdigest(), hashlib.sha256(self.reader.read_bytes()).hexdigest())

    # Group 2 patch 2: corrected text and numbers, and the old wrong text is gone.

    def test_d02_right_panel_title_does_not_say_the_survival_jumps(self):
        # Infinite-tree survival for d = 2 is (2p - 1) / p^2 above 1/2: continuous at p_c (0.0769 at 0.51, 0.816 at 0.70).
        self.assertAlmostEqual((2 * 0.51 - 1) / 0.51 ** 2, 0.0769, places=4)
        self.assertAlmostEqual((2 * 0.5001 - 1) / 0.5001 ** 2, 0.0, places=2)
        self.assertAlmostEqual((2 * 0.70 - 1) / 0.70 ** 2, 0.816, places=3)
        for key in ("0,0", "1,0", "2,3"):
            svg = self.svg_of("C04-D02", key)
            self.assertIn("Infinite survival is zero up to 1/2, then rises", svg)
            self.assertNotIn("survival jumps", svg)

    def test_d04_small_values_keep_their_mantissa(self):
        # (1 - 0.29792^3)^10000 = 4.1e-117 (log10 = -116.38), not 1e-116.
        self.assertEqual(dict(self.state("C04-D04", 2, 0)["metrics"])["Chance 10,000 runs in a row all fail"], "about 4.1e-117")
        self.assertNotIn("about 1e-116", json.dumps(self.state("C04-D04", 2, 0)))
        # (1 - 0.52136^3)^10000 = 2.09e-664 at grant 0.70, T = 3.
        self.assertEqual(dict(self.state("C04-D04", 1, 0)["metrics"])["Chance 10,000 runs in a row all fail"], "about 2.1e-664")
        self.assertNotIn("about 1e-664", json.dumps(self.state("C04-D04", 1, 0)))

    def test_d04_curve_reaches_ten_thousand_runs(self):
        # The plotted grid is dense and ends at exactly 10,000 runs (it used to be integer-rounded).
        import sys
        sys.path[:0] = [str(LAB / "src"), str(LAB / "tools" / "readers" / "engine"), str(LAB / "tools" / "readers" / "chapters")]
        import ch04
        self.assertEqual(float(ch04.RUNS[0]), 1.0)
        self.assertAlmostEqual(float(ch04.RUNS[-1]), 10000.0, places=6)
        self.assertGreaterEqual(len(ch04.RUNS), 300)

    def test_d02_draws_are_said_to_be_chosen_to_differ(self):
        text = self.state("C04-D02", 0, 2)["interpretation"]   # p = 0.30, draw 3
        self.assertIn("chosen to differ", text)
        self.assertIn("not the chance r4 = 0.095", text)
        self.assertEqual(self.metrics("C04-D02", 0, 2)["Chance a path to depth 4 exists"], "0.095")

    def test_d01_state_count_axis_has_integer_ticks(self):
        svg = self.svg_of("C04-D01", "3")
        for bad in (">0.5<", ">1.5<", ">3.5<"):
            self.assertNotIn(bad, svg)


if __name__ == "__main__":
    unittest.main()

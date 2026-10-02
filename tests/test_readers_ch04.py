"""Chapter 4 laboratory reader: independent hand checks of the built page.

The reader is built into a temporary directory, then every displayed number is
recomputed here from the chapter's own arithmetic (the four-state workflow, the
branching threshold, the depth-two tree, the chain rule), by independent
methods, not read back from the module that produced the page.
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

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
SLUG = "04-permission-reachability"


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


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


def reachable(edges, denied, start="draft"):
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


def survival_by_bisection(p, d):
    """Smallest root q of q = (1 - p + p q)^d in [0, 1) by bisection on the lower root; survival is 1 - q."""
    f = lambda q: (1 - p + p * q) ** d - q
    # f(0) > 0 and f(q) < 0 just below the largest root below 1; search for a sign change on [0, 1 - eps].
    lo, hi = 0.0, 1.0 - 1e-9
    if f(hi) >= 0:
        return 0.0
    for _ in range(200):
        mid = (lo + hi) / 2
        # the smallest root is where f first crosses from positive to non-positive
        if f(mid) > 0:
            lo = mid
        else:
            hi = mid
    return 1.0 - (lo + hi) / 2


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

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)]
            yield values, dict(state["metrics"]), state

    def test_four_demonstrations_and_budgets(self):
        self.assertEqual(list(self.demos), ["C04-D01", "C04-D02", "C04-D03", "C04-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [4, 6, 6, 8])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    def test_d01_reachability_by_hand(self):
        edges = [("draft", "review"), ("review", "release"), ("review", "draft"), ("draft", "archive")]
        denial = {"None: every move granted": None, "Review to release": ("review", "release"),
                  "Draft to review": ("draft", "review"), "Draft to archive": ("draft", "archive")}
        expected_counts = {"None: every move granted": 4, "Review to release": 3, "Draft to review": 2, "Draft to archive": 3}
        for (label,), m, state in self.states("C04-D01"):
            seen = reachable(edges, denial[label])
            self.assertEqual(m["States reached"], f"{len(seen)} of 4", label)
            self.assertEqual(len(seen), expected_counts[label])
            self.assertEqual(m["Release reachable with these grants"], "yes" if "release" in seen else "no")
            self.assertEqual(m["Release reachable with every grant"], "yes")
        default = dict(self.demos["C04-D01"]["states"]["0"]["metrics"])
        self.assertEqual(default["Shortest permitted path to release"], "draft, review, release")
        self.assertEqual(default["Reached states with no way out"], "release, archive")
        self.assertIn("Reach = 1 + 2 + 1 = 4 of 4 states", self.demos["C04-D01"]["states"]["0"]["interpretation"])
        # Denying review to release leaves a raw path but no permitted one, and the sum drops to 1 + 2 = 3.
        denied = self.demos["C04-D01"]["states"]["1"]
        self.assertIn("Reach = 1 + 2 = 3 of 4 states", denied["interpretation"])
        self.assertEqual(dict(denied["metrics"])["Shortest permitted path to release"], "none")
        # Denying draft to review makes review and release both unreachable: only draft and archive.
        self.assertIn("Reach = 1 + 1 = 2 of 4 states", self.demos["C04-D01"]["states"]["2"]["interpretation"])

    def test_d02_threshold_and_expected_counts(self):
        for (d, p), m, state in self.states("C04-D02"):
            d = int(d)
            mean = d * p
            self.assertEqual(m["Threshold p_c = 1/d"], f"{1 / d:.3f}")
            self.assertEqual(m["Expected open children per vertex (d x p)"], f"{mean:.5f}")
            regime = ("exactly at the threshold" if math.isclose(mean, 1.0) else
                      "below the threshold" if mean < 1 else "above the threshold")
            self.assertEqual(m["Regime"], regime)
            expected_survival = 0.0 if mean <= 1 else survival_by_bisection(p, d)
            self.assertEqual(m["Chance the root's cluster is infinite"], f"{expected_survival:.3f}", (d, p))
            # Counts at depth 20 recomputed with logarithms rather than a power.
            depth20 = math.exp(20 * math.log(mean))
            shown = float(m["Expected open descendants at depth 20"].replace(",", ""))
            self.assertAlmostEqual(shown / depth20, 1.0, delta=0.006)
        # d = 2 closed form for survival: 1 - ((1 - p) / p)^2 above one half.
        s = float(dict(self.demos["C04-D02"]["states"]["0,2"]["metrics"])["Chance the root's cluster is infinite"])
        self.assertAlmostEqual(s, 1 - ((1 - 0.67032) / 0.67032) ** 2, places=3)
        # The chapter's rounded depth-twenty counts: about 348 for 1.34 and 0.000032 for 0.596.
        self.assertAlmostEqual(1.34 ** 20, 348, delta=2)
        self.assertAlmostEqual(0.596 ** 20, 3.2e-5, delta=3e-6)
        # The exact threshold case is reported as such, with survival zero.
        tie = self.demos["C04-D02"]["states"]["0,1"]
        self.assertEqual(dict(tie["metrics"])["Regime"], "exactly at the threshold")
        self.assertIn("2 x 0.5 = 1.00000", tie["interpretation"])

    def test_d03_depth_two_tree(self):
        for (d, p), m, state in self.states("C04-D03"):
            d = int(d)
            # Enumerate the tree: a root edge and a leaf edge must both be open; branches are independent.
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
        state = dict(self.demos["C04-D03"]["states"]["0,0"]["metrics"])
        self.assertEqual(state["A path to depth two exists"], f"{total:.6f}")
        # The chapter's numbers: 1.44, 0.753984 and 0.36 at p = 0.6 with two children.
        book = dict(self.demos["C04-D03"]["states"]["0,1"]["metrics"])
        self.assertEqual(book["Expected open depth-two descendants (d^2 x p^2)"], "1.44")
        self.assertEqual(book["A path to depth two exists"], "0.753984")
        self.assertEqual(book["Committed run finishes (p^2)"], "0.36")
        # Expected count below one while a path still exists (p = 0.4, d = 2).
        self.assertLess(0.4 * 0.4 * 4, 1)
        self.assertIn("below 1, yet a path exists", self.demos["C04-D03"]["states"]["0,0"]["interpretation"])

    def test_d04_chain_rule(self):
        for (grant, steps), m, state in self.states("C04-D04"):
            p = 0.95 * 0.98 * grant * 0.80
            self.assertEqual(m["Edge success p"], f"{p:.5f}")
            self.assertEqual(m["Open children per vertex (d x p, d = 2)"], f"{2 * p:.5f}")
            self.assertEqual(m["Against the threshold 1/d = 0.5"], "above the threshold" if 2 * p > 1 else "below the threshold")
            key = [k for k in m if k.startswith("One chain of")][0]
            chain = math.exp(int(steps) * math.log(p)) if p else 0.0
            # Values below 0.001 are shown in scientific notation so they never round to zero.
            self.assertEqual(m[key], f"{chain:.3g}" if 0 < chain < 0.001 else f"{chain:.5f}")
            self.assertEqual(m["Grant rate that gives d x p = 1"], f"{0.5 / (0.95 * 0.98 * 0.80):.4f}")
        book = self.demos["C04-D04"]["states"]
        self.assertEqual(dict(book["0,0"]["metrics"])["Edge success p"], "0.67032")  # the chapter's working case
        self.assertEqual(dict(book["2,0"]["metrics"])["Edge success p"], "0.29792")  # the chapter's tightened case
        self.assertEqual(dict(book["2,0"]["metrics"])["Open children per vertex (d x p, d = 2)"], "0.59584")
        # Grant 0.70 sits above the break-even 0.6713 and grant 0.40 below it.
        self.assertGreater(0.70, 0.5 / 0.7448)
        self.assertLess(0.40, 0.5 / 0.7448)
        # A grant of zero removes the edge: undefined powers are shown as zero probability with the reason in words.
        zero = book["3,0"]
        self.assertIn("structural failure", zero["interpretation"])
        self.assertEqual(dict(zero["metrics"])["Edge success p"], "0.00000")

    def test_g2_01_application_does_not_generalize_the_hour(self):
        # The only "hour" in the chapter is the constructed ticketing case; the workflow demo has no time quantity.
        text = self.page
        self.assertNotIn("found in an hour", text)
        self.assertIn("A missing grant shows up in the list of states and moves; a prompt cannot add it.", text)

    def test_g2_02_note_names_what_changed(self):
        notes = {}
        for (d, p), m, state in self.states("C04-D03"):
            notes[(int(d), p)] = state["interpretation"]
        self.assertIn("This is the chapter's constructed example.", notes[(2, 0.6)])
        for p in (0.4, 0.8):
            self.assertIn(f"(two children), with p changed to {p}.", notes[(2, p)])
            self.assertNotIn("child count changed", notes[(2, p)])
        self.assertIn("with the child count changed to 3.", notes[(3, 0.6)])
        self.assertIn("child count changed to 3 and p changed to 0.4.", notes[(3, 0.4)])

    def test_g2_03_04_equation_blocks_are_explained(self):
        page = html.unescape(self.page)
        self.assertIn("chapter's instance (d = 2, p = 0.6)", page)
        self.assertIn("1 - [1 - p(1 - (1 - p)^d)]^d", page)
        self.assertIn("(dp)^T with T = 2 is (dp)^2", page)
        self.assertIn("E[Z_T] = (dp)^T", page)
        # The d = 3, p = 0.4 state computes the general formula that the static block does not show.
        branch = 0.4 * (1 - 0.6 ** 3)
        self.assertEqual(dict(self.demos["C04-D03"]["states"]["1,0"]["metrics"])["A path to depth two exists"],
                         f"{1 - (1 - branch) ** 3:.6f}")

    def svg_of(self, demo_id, key):
        import base64
        return base64.b64decode(self.demos[demo_id]["states"][key]["image"].split(",", 1)[1]).decode()

    def test_g2_05_small_probabilities_are_not_rounded_to_zero(self):
        state = self.demos["C04-D04"]["states"]["2,1"]  # grant 0.40, T = 10
        chain = (0.95 * 0.98 * 0.4 * 0.8) ** 10
        self.assertAlmostEqual(chain, 5.51e-06, delta=1e-8)
        self.assertEqual(dict(state["metrics"])["One chain of 10 steps (p^10)"], "5.51e-06")
        self.assertIn("0.29792^10 = 5.51e-06", state["interpretation"])
        self.assertNotIn("0.00001", state["interpretation"])
        # The figure marker label agrees with the text instead of reading 0.0000.
        svg = self.svg_of("C04-D04", "2,1")
        self.assertIn("5.51e-06", svg)
        self.assertNotIn(">0.0000<", svg)
        # Grant 0.70, T = 10 is 0.00148, above the notation cutoff.
        self.assertEqual(dict(self.demos["C04-D04"]["states"]["1,1"]["metrics"])["One chain of 10 steps (p^10)"], "0.00148")

    def test_g2_06_grant_zero_is_annotated(self):
        for key in ("3,0", "3,1"):
            self.assertIn("edge removed", self.svg_of("C04-D04", key))
        self.assertNotIn("edge removed", self.svg_of("C04-D04", "0,0"))

    def test_g2_07_depth_twenty_counts_are_reconciled_with_the_chapter(self):
        text = self.demos["C04-D02"]["states"]["0,2"]["interpretation"]  # d = 2, p = 0.67032
        self.assertIn("The chapter rounds the mean to 1.34 and quotes about 348 at depth 20; the unrounded mean 1.34064 gives 351.76.", text)
        tight = self.demos["C04-D02"]["states"]["0,0"]["interpretation"]  # d = 2, p = 0.29792
        self.assertIn("rounds the mean to 0.596 and quotes about 0.000032", tight)
        self.assertIn("3.18e-05", tight)

    def test_chapter_ratio_of_depth_twenty_counts(self):
        # The chapter quotes (0.90 / 0.40)^20, about 11.057 million, for the exact products.
        self.assertAlmostEqual((0.90 / 0.40) ** 20 / 1e6, 11.057, places=2)
        ratio = (0.95 * 0.98 * 0.9 * 0.8 * 2) ** 20 / (0.95 * 0.98 * 0.4 * 0.8 * 2) ** 20
        self.assertAlmostEqual(ratio / 1e6, 11.057, places=2)

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
        self.assertGreaterEqual(len(alts), 4)
        for tex in alts:
            self.assertTrue(norm(html.unescape(tex)) in allowed or norm(html.unescape(tex)) in inline, tex)

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "--", "\u2212"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_accessibility_and_offline(self):
        self.assertIn('<a class="skip" href="#main">', self.page)
        self.assertIn("<noscript>", self.page)
        self.assertEqual(self.page.count('aria-live="polite"'), 4)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))
        for d in self.data["demos"]:
            for c in d["controls"]:
                self.assertIn(f'<label for="{d["id"]}-{c["key"]}">', self.page)

    def test_every_control_combination_renders(self):
        for demo in self.data["demos"]:
            n = 1
            for c in demo["controls"]:
                n *= len(c["values"])
            self.assertEqual(len(demo["states"]), n, demo["id"])
            for state in demo["states"].values():
                self.assertTrue(state["image"].startswith("data:image/svg+xml;base64,"))
                self.assertTrue(state["interpretation"])

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["labelled_controls"]), (24, 7))

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as out:
            run = build(self.python, out)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            fresh = Path(out) / SLUG / "reader.html"
            self.assertEqual(hashlib.sha256(fresh.read_bytes()).hexdigest(), hashlib.sha256(self.reader.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()

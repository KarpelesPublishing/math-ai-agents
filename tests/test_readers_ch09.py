"""Chapter 9 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(the four-vertex trace, the two-route graph, the consistency fragment and the
200 and 900 millisecond example), not read back from the module that produced
the page. The test builds the reader into a private temporary directory, so it
never touches the committed readers folder.
"""
from __future__ import annotations

import heapq
import importlib.util
import json
import math
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from math_ai_agents.chapters.ch09 import evaluate

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
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


def n(x):
    """Whole numbers without decimals, others with one decimal (the reader's display rule)."""
    return str(int(round(x))) if math.isclose(x, round(x), abs_tol=1e-9) else f"{x:.1f}"


def reference_astar(edges, h, start, goals):
    """A second, independent A* (plain dictionaries and a heap) returning (cost, selected order)."""
    best, queue, selected = {start: 0}, [(h[start], 0, start)], []
    while queue:
        f, g, v = heapq.heappop(queue)
        if g > best[v]:
            continue
        selected.append(v)
        if v in goals:
            return g, selected
        for w, c in edges.get(v, []):
            if g + c < best.get(w, math.inf):
                best[w] = g + c
                heapq.heappush(queue, (g + c + h[w], g + c, w))
    raise AssertionError("no goal")


@unittest.skipIf(_builder_python() is None, "no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
class Chapter9ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="reader-ch09-")
        run = subprocess.run([_builder_python(), str(WRAPPER), "--chapters", "9", "--out", cls.tmp],
                             capture_output=True, text=True, timeout=600)
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls.tmp) / "09-astar-audit" / "reader.html"
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
            values = [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)]
            yield values, state, dict(state["metrics"])

    def state(self, demo_id, values):
        for vals, state, m in self.states(demo_id):
            if vals == values:
                return state, m
        self.fail(f"no state {values} in {demo_id}")

    # structure

    def test_four_demonstrations_all_states_render(self):
        self.assertEqual(list(self.demos), ["C09-D01", "C09-D02", "C09-D03", "C09-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 8, 8, 8])
        for d in self.data["demos"]:
            for state in d["states"].values():
                self.assertTrue(state["image"].startswith("data:image/svg+xml"))
                self.assertTrue(state["interpretation"])
                self.assertTrue(state["metrics"])

    def test_size_budget(self):
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    # Demonstration 1: recorded cost, the chapter's trace (7 becomes 6)

    def test_d01_recorded_cost_update(self):
        for (ab, direct), state, m in self.states("C09-D01"):
            via = 3 + ab
            after = via if via < direct else direct  # strict improvement only
            self.assertEqual(m["B before, after"], f"{n(direct)}, {n(after)}")
            self.assertEqual(m["Route to B through A"], n(via))
            self.assertEqual(m["Recorded cost of A"], "3")
            self.assertEqual(m["Recorded cost of C"], "5")
            self.assertIn(f"3 + {n(ab)} = {n(via)}", state["interpretation"])
        _, book = self.state("C09-D01", [3, 7])
        self.assertEqual(book["B before, after"], "7, 6")  # the chapter: 7 falls to 6
        self.assertEqual(book["Record of B"], "lowered by 1")

    def test_d01_tie_and_dearer_routes_do_not_update(self):
        state, m = self.state("C09-D01", [4, 7])  # 3 + 4 = 7 ties the record
        self.assertEqual(m["B before, after"], "7, 7")
        self.assertEqual(m["Record of B"], "no change (tie)")
        self.assertIn("strictly lower", state["interpretation"])
        _, m = self.state("C09-D01", [3, 5])  # 3 + 3 = 6 is dearer than 5
        self.assertEqual(m["B before, after"], "5, 5")
        self.assertTrue(m["Record of B"].startswith("no change"))

    # Demonstration 2: the two-route graph

    def test_d02_two_route_graph_by_hand(self):
        edges = {"s": [("a", 1), ("b", 1)], "a": [("goal_a", 9)], "b": [("goal_b", 24)]}
        for (h_a, h_b), state, m in self.states("C09-D02"):
            h = {"s": 0, "a": h_a, "b": h_b, "goal_a": 0, "goal_b": 0}
            cost, selected = reference_astar(edges, h, "s", {"goal_a", "goal_b"})
            # Independent closed form: a is reached before goal_b is selected iff 1 + h(a) <= 25.
            self.assertEqual(cost, 25 if 1 + h_a > 25 else 10, (h_a, h_b))
            self.assertEqual(m["Vertices expanded"], ", ".join(selected[:-1]), (h_a, h_b))
            self.assertEqual(m["Score of a, score of b"], f"{n(1 + h_a)}, {n(1 + h_b)}")
            self.assertEqual(m["Equation (9.3) holds"], "yes" if (h_a <= 9 and h_b <= 24) else "no")
            self.assertIn("(cost 10)" if cost == 10 else "(cost 25)", m["Route returned"])
            self.assertEqual(m["Unexpanded"], "none" if {"a", "b"} <= set(selected) else ", ".join(v for v in ("a", "b") if v not in selected))

    def test_d02_chapter_numbers(self):
        # Zero estimate: three non-goal vertices expanded, cost 10.
        _, zero = self.state("C09-D02", [0, 0])
        self.assertEqual(zero["Vertices expanded"], "s, a, b")
        self.assertIn("(cost 10)", zero["Route returned"])
        # One overestimate (a high by 16 over its true 9): two vertices expanded, cost 25, 2.5 times the best.
        state, over = self.state("C09-D02", [25, 24])
        self.assertEqual(over["Vertices expanded"], "s, b")
        self.assertEqual(over["Unexpanded"], "a")
        self.assertIn("(cost 25)", over["Route returned"])
        self.assertIn("fails by 16", state["interpretation"])
        self.assertIn("25 / 10 = 2.5", state["interpretation"])
        self.assertEqual(25 / 10, 2.5)
        self.assertEqual(25 - 9, 16)

    def test_d02_boundary_estimates(self):
        # Exactly at the limit 1 + 24 = 25 the scores tie and a wins on smaller cost so far.
        edges = {"s": [("a", 1), ("b", 1)], "a": [("goal_a", 9)], "b": [("goal_b", 24)]}
        h = {"s": 0, "a": 24, "b": 24, "goal_a": 0, "goal_b": 0}
        cost, selected = reference_astar(edges, h, "s", {"goal_a", "goal_b"})
        self.assertEqual((cost, selected), (10, ["s", "a", "goal_a"]))
        # An overestimate that stays under the limit (20 against a true 9) still finds cost 10.
        _, m = self.state("C09-D02", [20, 24])
        self.assertIn("(cost 10)", m["Route returned"])
        self.assertEqual(m["Equation (9.3) holds"], "no")

    def test_d02_laboratory_function_agrees(self):
        out = evaluate({
            "nodes": ["s", "a", "b", "goal_a", "goal_b", "done"], "start": "s", "goal": "done",
            "edges": [{"from": "s", "to": "a", "cost": 1}, {"from": "a", "to": "goal_a", "cost": 9},
                      {"from": "s", "to": "b", "cost": 1}, {"from": "b", "to": "goal_b", "cost": 24},
                      {"from": "goal_a", "to": "done", "cost": 0}, {"from": "goal_b", "to": "done", "cost": 0}],
            "heuristic": {"s": 0, "a": 25, "b": 24, "goal_a": 0, "goal_b": 0, "done": 0}, "heuristic_cost": 0,
        })
        self.assertEqual(out["metrics"]["path_cost"], 25)
        self.assertEqual(out["metrics"]["optimal_cost"], 10)
        self.assertFalse(out["metrics"]["admissible"])

    # Demonstration 3: the consistency fragment

    def test_d03_consistency_by_hand(self):
        for (h_up, h_start), state, m in self.states("C09-D03"):
            drop_up, drop_low = h_start - h_up, h_start - 5
            ok_up, ok_low = h_start <= 6 + h_up, h_start <= 3 + 5
            self.assertEqual(m["Upper edge: drop, cost"], f"{n(drop_up)}, 6")
            self.assertEqual(m["Lower edge: drop, cost"], f"{n(drop_low)}, 3")
            self.assertEqual(m["Consistent on both edges"], "yes" if (ok_up and ok_low) else "no (upper edge)")
            self.assertEqual(m["Scores: upper, lower"], f"{n(6 + h_up)}, 8")
            self.assertIn(f"{n(h_start)} <= 6 + {n(h_up)} = {n(6 + h_up)} is {'true' if ok_up else 'false'}", state["interpretation"])

    def test_d03_chapter_fragment(self):
        # The chapter: start estimate 8, edges 6 and 3, estimates 1 and 5: scores 7 and 8, and 8 > 6 + 1.
        state, m = self.state("C09-D03", [1, 8])
        self.assertEqual(m["Scores: upper, lower"], "7, 8")
        self.assertEqual(m["Selected first"], "upper vertex")
        self.assertEqual(m["Consistent on both edges"], "no (upper edge)")
        self.assertGreater(8, 6 + 1)
        self.assertIn("fails on the upper edge by 1", state["interpretation"])
        self.assertIn("below the start's estimate of 8", state["interpretation"])

    def test_d03_tight_and_tied_boundary(self):
        # With estimate 2 the upper edge is exactly tight (8 = 6 + 2) and both scores are 8: a tie.
        state, m = self.state("C09-D03", [2, 8])
        self.assertEqual(m["Consistent on both edges"], "yes")
        self.assertIn("tie", m["Selected first"])
        self.assertIn("exactly tight", state["interpretation"])

    def test_d03_laboratory_flag_agrees(self):
        def flag(h_start, h_up):
            return evaluate({
                "nodes": ["s", "u", "l", "g"], "start": "s", "goal": "g",
                "edges": [{"from": "s", "to": "u", "cost": 6}, {"from": "s", "to": "l", "cost": 3},
                          {"from": "u", "to": "g", "cost": 100}, {"from": "l", "to": "g", "cost": 100}],
                "heuristic": {"s": h_start, "u": h_up, "l": 5, "g": 0}, "heuristic_cost": 0,
            })["metrics"]["consistent"]
        self.assertFalse(flag(8, 1))
        self.assertTrue(flag(8, 2))
        self.assertTrue(flag(6, 1))

    # Demonstration 4: the estimate that costs more than it saves

    def test_d04_time_arithmetic(self):
        for (saved, cost), state, m in self.states("C09-D04"):
            gain = 200 * saved
            net = gain - cost
            self.assertEqual(m["Time saved per vertex"], f"{n(gain)} ms")
            self.assertEqual(m["Estimate cost per vertex"], f"{n(cost)} ms")
            self.assertEqual(m["Net per vertex"], f"({n(net)}) ms" if net < 0 else f"{n(net)} ms")
            self.assertEqual(m["Break-even expansions saved"], f"{cost / 200:.2f}")
            self.assertIn(f"{n(saved)} x 200 = {n(gain)}", state["interpretation"])

    def test_d04_chapter_example_and_boundaries(self):
        # The chapter: 3 expansions saved is 600 ms, the estimate costs 900 ms.
        state, m = self.state("C09-D04", [3, 900])
        self.assertEqual((m["Time saved per vertex"], m["Net per vertex"]), ("600 ms", "(-300) ms"))
        self.assertIn("slowest to finish", state["interpretation"])
        # Exact tie: 2 x 200 = 400 = 400.
        state, m = self.state("C09-D04", [2, 400])
        self.assertEqual(m["Net per vertex"], "0 ms")
        self.assertIn("exactly equal", state["interpretation"])
        # Nothing saved: pure overhead.
        state, m = self.state("C09-D04", [0, 900])
        self.assertEqual(m["Time saved per vertex"], "0 ms")
        self.assertIn("pure overhead", state["interpretation"])
        # g3-19: with nothing saved there is no "search that expands the fewest"; g3-20: no undefined "paper"
        for est in (400, 900):
            state, m = self.state("C09-D04", [0, est])
            self.assertNotIn("expands the fewest", state["interpretation"])
            self.assertNotIn("slowest to finish", state["interpretation"])
            self.assertIn(f"The estimate loses {est} ms per vertex.", state["interpretation"])
        for vals, state, m in self.states("C09-D04"):
            self.assertNotIn("the paper", state["interpretation"])
        state, _ = self.state("C09-D04", [2, 900])
        self.assertIn("the chapter's warning about an estimate that costs more than the vertex it saves", state["interpretation"])
        self.assertIn("slowest to finish", state["interpretation"])
        # g3-23: the inconsistency signature holds because the start's recorded cost is 0
        state, _ = self.state("C09-D03", [1, 8])
        self.assertIn("the start's recorded cost is 0", state["interpretation"])
        # Above break-even the estimate pays.
        _, m = self.state("C09-D04", [4, 400])
        self.assertEqual(m["Net per vertex"], "400 ms")

    def test_d04_workflow_saves_no_expansions(self):
        # The chapter's research workflow: stage costs 1, 2, 4; true remaining 7, 6, 4, 0.
        remaining = {"goal": 0}
        remaining["fetched"] = 4 + remaining["goal"]
        remaining["found"] = 2 + remaining["fetched"]
        remaining["s"] = 1 + remaining["found"]
        self.assertEqual([remaining[k] for k in ("s", "found", "fetched", "goal")], [7, 6, 4, 0])
        structural = {"s": 2, "found": 1, "fetched": 1, "goal": 0}
        self.assertTrue(all(structural[k] <= remaining[k] for k in remaining))
        for heuristic in (structural, dict.fromkeys(structural, 0)):
            out = evaluate({
                "nodes": ["s", "found", "fetched", "goal"], "start": "s", "goal": "goal",
                "edges": [{"from": "s", "to": "found", "cost": 1}, {"from": "found", "to": "fetched", "cost": 2},
                          {"from": "fetched", "to": "goal", "cost": 4}],
                "heuristic": heuristic, "heuristic_cost": 0,
            })
            self.assertEqual(out["metrics"]["expansions"], 4)  # four selections, three of them expansions
            self.assertEqual(out["metrics"]["path_cost"], 7)

    # equations, text and page

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 9)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\(?:[,;:!]|quad|qquad)", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        import html
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 4)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)
        # The one inline equation (the edge form) is in the chapter text.
        text = (LAB.parent / "Manuscript" / "part-iii" / "09-searching-the-future.md").read_text()
        self.assertIn(r"\hat h(u) \le \operatorname{cost}(u,v)+\hat h(v)", text)

    def test_page_text_has_no_dashes_or_dependency_names(self):
        import html
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter", "scipy"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_links_and_offline(self):
        for href in ("../../notebooks/09-astar-audit.ipynb", "../../skills/maa-09-astar-audit/SKILL.md", "../index.html"):
            self.assertIn(f'href="{href}"', self.page)
        for target in ("notebooks/09-astar-audit.ipynb", "skills/maa-09-astar-audit/SKILL.md"):
            self.assertTrue((LAB / target).exists(), target)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (32, 4, 8))


if __name__ == "__main__":
    unittest.main()

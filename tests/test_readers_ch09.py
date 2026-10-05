"""Chapter 9 laboratory reader: independent hand checks of the built page.

Expected numbers are recomputed here by an independent list-based A* and by the chapter's own tables,
not read back from the module.
"""
from __future__ import annotations

from fractions import Fraction as F
import base64
import html
import json
import math
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
SLUG = "09-astar-audit"


def build_python():
    venv = LAB / ".venv" / "bin" / "python"
    return str(venv) if venv.exists() else sys.executable


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


class Chapter9ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([build_python(), str(WRAPPER), "--chapters", "9", "--out", cls.tmp.name],
                             capture_output=True, text=True, timeout=600)
        if run.returncode != 0:
            raise unittest.SkipTest("cannot build: " + run.stdout + run.stderr)
        cls.reader = Path(cls.tmp.name) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        m = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', cls.page, re.S)
        cls.data = json.loads(m.group(1))
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)], dict(state["metrics"]), state

    def by_index(self, demo_id):
        out = {}
        for key, st in self.demos[demo_id]["states"].items():
            out[tuple(int(i) for i in key.split(","))] = (dict(st["metrics"]), st)
        return out

    @staticmethod
    def search(edges, h, start, goals):
        """Independent A*: plain list scan for the minimum (f, g, label); returns (selected order, cost)."""
        best = {start: 0}
        queue = [(h[start], 0, start)]
        selected = []
        while queue:
            queue.sort()
            f, g, v = queue.pop(0)
            if g != best[v]:
                continue
            selected.append(v)
            if v in goals:
                return selected, g
            for a, b, c in edges:
                if a == v and g + c < best.get(b, 10 ** 9):
                    best[b] = g + c
                    queue.append((g + c + h[b], g + c, b))
        raise ValueError

    def test_structure_and_optional_fields(self):
        self.assertEqual(list(self.demos), ["C09-D01", "C09-D02", "C09-D03", "C09-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 12, 12])
        self.assertLess(self.reader.stat().st_size, 4_000_000)
        text = html.unescape(self.page)
        self.assertIn("Ask the chapter skill", text)
        self.assertEqual(text.count("Common wrong turn"), 4)
        self.assertGreaterEqual(text.count("What this does not settle"), 4)
        self.assertEqual(len(re.findall(r'type="radio"', text)), 12)
        for d in self.data["demos"]:
            for s in d["states"].values():
                self.assertTrue(s.get("steps"))

    def test_d01_traces(self):
        got = self.by_index("C09-D01")
        # four-vertex trace (B is the goal): select s, A, C, B; B's record falls from 7 to 6
        edges = [("s", "A", 3), ("s", "B", 7), ("A", "C", 2), ("A", "B", 3)]
        order, cost = self.search(edges, {"s": 0, "A": 0, "B": 0, "C": 0}, "s", {"B"})
        self.assertEqual(order, ["s", "A", "C", "B"])
        self.assertEqual(cost, 6)
        for k, v in enumerate(order):
            self.assertTrue(got[(0, k)][0]["Selected"].startswith(v))
        self.assertIn("falls from 7 to 6", got[(0, 1)][1]["interpretation"])
        self.assertEqual(got[(0, 1)][0]["Frontier, next first"], "C (5), B (6)")
        self.assertEqual(got[(0, 0)][0]["Frontier, next first"], "A (3), B (7)")
        self.assertEqual(got[(0, 3)][0]["Recorded cost g, score f"], "6, 6")
        # two-route graph, zero estimate: expand s, a, b, then select goal_a at cost 10 (the chapter's table)
        er = [("s", "a", 1), ("a", "goal_a", 9), ("s", "b", 1), ("b", "goal_b", 24)]
        zero = {n: 0 for n in ("s", "a", "b", "goal_a", "goal_b")}
        order, cost = self.search(er, zero, "s", {"goal_a", "goal_b"})
        self.assertEqual((order, cost), (["s", "a", "b", "goal_a"], 10))
        for k, v in enumerate(order):
            self.assertTrue(got[(1, k)][0]["Selected"].startswith(v))
        self.assertEqual(got[(1, 3)][0]["Selected"], "goal_a (goal)")
        self.assertEqual(got[(1, 1)][0]["Frontier, next first"], "b (1), goal_a (10)")
        self.assertEqual(got[(1, 2)][0]["Frontier, next first"], "goal_a (10), goal_b (25)")
        # research workflow with the structural estimate: frontier (1,2), (3,4), (7,7); nine edges examined, six rejected self-loops
        wf = [("s", "found", 1), ("s", "s", 2), ("s", "s", 4), ("found", "found", 1), ("found", "fetched", 2), ("found", "found", 4),
              ("fetched", "fetched", 1), ("fetched", "fetched", 2), ("fetched", "goal", 4)]
        order, cost = self.search(wf, {"s": 2, "found": 1, "fetched": 1, "goal": 0}, "s", {"goal"})
        self.assertEqual((order, cost), (["s", "found", "fetched", "goal"], 7))
        self.assertEqual(got[(2, 0)][0]["Frontier, next first"], "found (2)")
        self.assertEqual(got[(2, 1)][0]["Frontier, next first"], "fetched (4)")
        self.assertEqual(got[(2, 2)][0]["Frontier, next first"], "goal (7)")
        self.assertEqual(got[(2, 3)][0]["Frontier, next first"], "empty")
        self.assertEqual(got[(2, 2)][0]["Edges examined so far"], "9")
        self.assertIn("rejected for not beating the record", got[(2, 1)][1]["interpretation"])

    def test_d02_admissibility_cases(self):
        cases = [
            ("two", [("s", "a", 1), ("a", "goal_a", 9), ("s", "b", 1), ("b", "goal_b", 24)],
             {"s": 0, "a": 0, "b": 24, "goal_a": 0, "goal_b": 0}, "a", [0, 9, 20, 25], {"goal_a", "goal_b"}, 9),
            ("note", [("S", "A", 1), ("A", "G", 4), ("S", "B", 2), ("B", "G", 1)],
             {"S": 3, "A": 4, "B": 0, "G": 0}, "B", [0, 1, 3, 10], {"G"}, 1),
            ("trans", [("source", "middle", 2), ("middle", "target", 2), ("source", "target", 7)],
             {"source": 0, "middle": 0, "target": 0}, "middle", [0, 2, 5, 9], {"target"}, 2),
        ]
        got = self.by_index("C09-D02")
        for ci, (name, edges, h, v, levels, goals, true_h) in enumerate(cases):
            for li, est in enumerate(levels):
                hh = dict(h)
                hh[v] = est
                start = edges[0][0]
                order, cost = self.search(edges, hh, start, goals)
                met, st = got[(ci, li)]
                self.assertEqual(met["Route returned"].split(" ")[1], f"{cost}")
                self.assertEqual(met["Vertices expanded"], ", ".join(order[:-1]))
                self.assertEqual(met["Equation (9.3) holds everywhere"].startswith("yes"), est <= true_h)
        # chapter: zero estimate returns 10 after three expansions; the overestimate at a returns 25 after two
        self.assertEqual(got[(0, 0)][0]["Vertices expanded"], "s, a")   # b is exact (score 25), so only a is expanded
        self.assertEqual(got[(0, 3)][0]["Vertices expanded"], "s, b")
        self.assertIn("cost 25 (suboptimal, best is 10)", got[(0, 3)][0]["Route returned"])
        self.assertIn("cost 10 (optimal, best is 10)", got[(0, 2)][0]["Route returned"])   # 20 breaks (9.3) but the best route still returns
        self.assertEqual(got[(0, 3)][0]["Equation (9.3) holds everywhere"], "no (at a)")
        # notebook default (exact) returns 3, changed (B = 10) returns 5; transfer with zero returns 4 not 7
        self.assertIn("cost 3 (optimal", got[(1, 1)][0]["Route returned"])
        self.assertIn("cost 5 (suboptimal, best is 3)", got[(1, 3)][0]["Route returned"])
        self.assertIn("cost 4 (optimal, best is 4)", got[(2, 0)][0]["Route returned"])
        self.assertIn("cost 7 (suboptimal, best is 4)", got[(2, 3)][0]["Route returned"])
        # exact f marks the optimal path: S, B, G have f = 3 and A has f = 1 + 4 = 5
        self.assertIn("A = 1 + 4 = 5", got[(1, 0)][1]["interpretation"])
        self.assertIn("B = 2 + 1 = 3", got[(1, 0)][1]["interpretation"])
        # score of B at estimate 3 ties the rival at 5: A goes first (smaller cost), then B beats the queued goal on smaller cost, so cost 3 is found
        self.assertEqual(got[(1, 2)][0]["Vertices expanded"], "S, A, B")
        self.assertIn("cost 3 (optimal", got[(1, 2)][0]["Route returned"])

    def test_d03_consistency(self):
        hu, hs = [1, 2, 5, 8], [8, 7, 6]
        got = self.by_index("C09-D03")
        for (ui, si), (met, st) in got.items():
            u, s = hu[ui], hs[si]
            ok_up = s - u <= 6
            ok_low = s - 5 <= 3
            self.assertEqual(met["Consistent on both edges"], "yes" if (ok_up and ok_low) else "no (upper edge)")
            self.assertEqual(met["Scores: upper, lower"], f"{6 + u}, 8")
            self.assertEqual(met["Upper edge: drop, cost"], f"{s - u}, 6")
        m = got[(0, 0)][0]
        self.assertEqual(m["Consistent on both edges"], "no (upper edge)")   # the chapter's 8 > 6 + 1
        self.assertEqual(m["Selected first"], "upper vertex")
        self.assertEqual(m["Scores: upper, lower"], "7, 8")
        self.assertEqual(got[(0, 1)][0]["Consistent on both edges"], "yes")   # 7 <= 6 + 1, exactly tight
        self.assertIn("exactly tight", got[(0, 1)][1]["interpretation"])
        self.assertIn("does not drop at all", got[(3, 2)][1]["interpretation"])

    def test_d04_spending(self):
        graphs = [
            ("note", [("S", "A", 1), ("A", "G", 4), ("S", "B", 2), ("B", "G", 1)], {"S": 3, "A": 4, "B": 1, "G": 0}, {"G"}),
            ("two", [("s", "a", 1), ("a", "goal_a", 9), ("s", "b", 1), ("b", "goal_b", 24)],
             {"s": 0, "a": 9, "b": 24, "goal_a": 0, "goal_b": 0}, {"goal_a", "goal_b"}),
            ("wf", [("s", "found", 1), ("s", "s", 2), ("s", "s", 4), ("found", "found", 1), ("found", "fetched", 2), ("found", "found", 4),
                    ("fetched", "fetched", 1), ("fetched", "fetched", 2), ("fetched", "goal", 4)],
             {"s": 2, "found": 1, "fetched": 1, "goal": 0}, {"goal"}),
        ]
        prices = [0, 100, 400, 900]
        got = self.by_index("C09-D04")
        expect = {0: (2, 3, 4), 1: (2, 3, 4), 2: (3, 3, 4)}   # expansions with, without; estimates computed
        for (gi, pi), (met, st) in got.items():
            name, edges, h, goals = graphs[gi]
            zero = {k: 0 for k in h}
            o_i, c_i = self.search(edges, h, edges[0][0], goals)
            o_z, c_z = self.search(edges, zero, edges[0][0], goals)
            ei, ez = len(o_i) - 1, len(o_z) - 1
            self.assertEqual((ei, ez, ei, ), (expect[gi][0], expect[gi][1], expect[gi][0]))
            self.assertEqual(c_i, c_z)
            calls = expect[gi][2]
            self.assertEqual(met["Expansions, with and without"], f"{ei} and {ez}")
            self.assertEqual(met["Estimates computed"], str(calls))
            t_i, t_z = 200 * ei + prices[pi] * calls, 200 * ez
            self.assertEqual(met["Total time, with and without"], f"{t_i} ms and {t_z} ms")
            self.assertEqual(met["Break-even price per estimate"], f"{200 * (ez - ei) / calls:g} ms".replace("e+", "e"))
            self.assertEqual(met["Verdict"], "estimate pays" if t_i < t_z else ("estimate loses" if t_i > t_z else "equal"))
        # chapter: the workflow estimate saves nothing; the two-route zero search expands three vertices
        self.assertEqual(got[(2, 0)][0]["Verdict"], "equal")
        self.assertIn("identical set", got[(2, 3)][1]["interpretation"])
        self.assertEqual(got[(0, 3)][0]["Break-even price per estimate"], "50 ms")
        self.assertEqual(got[(1, 3)][0]["Verdict"], "estimate loses")
        self.assertIn("tie in score", got[(1, 0)][1]["interpretation"])

    def test_equations_come_from_chapter(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 9)
        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        # The edge form of Equation (9.4) is quoted from the chapter's text (inline code, line 281 of the
        # source) and has no chapter asset; newer engines show it as raw TeX, older ones omitted it.
        edge = norm(r"\hat h(u) \le \operatorname{cost}(u,v)+\hat h(v)")
        self.assertIn(len(alts), (6, 7))
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed | {edge})

    def test_patch2_no_false_fewest_expansions_claim(self):
        # g3-01: the workflow expands the same 3 vertices with and without the estimate, so the
        # "fewest vertices is not fastest" sentence must not appear there; it still holds on the notebook graph.
        got = self.by_index("C09-D04")
        for price in (1, 2, 3):
            m, st = got[(2, price)]
            self.assertEqual(m["Expansions, with and without"], "3 and 3")
            text = st["interpretation"] + " " + " ".join(st["steps"])
            self.assertNotIn("expands fewest vertices", text)
            self.assertNotIn("fewest expansions need not mean", text)
            self.assertIn("saves no expansions", text)
            self.assertIn("pure overhead", text)
        m, st = got[(2, 3)]
        self.assertIn("The estimate loses 3600 ms", st["interpretation"])
        m, st = got[(0, 3)]
        self.assertEqual(m["Expansions, with and without"], "2 and 3")
        self.assertIn("expands fewest vertices (2)", st["interpretation"])

    def test_patch2_rise_not_negative_drop(self):
        # g3-31: a start estimate of 6 against an upper estimate of 8 is a rise of 2, not a drop of -2
        demo = self.demos["C09-D03"]
        key = "3,2"
        st = demo["states"][key]
        self.assertIn("rises by 8 - 6 = 2", st["interpretation"])
        self.assertNotIn("drops by 6 - 8", st["interpretation"])
        self.assertNotIn("= -2", st["interpretation"] + " ".join(st["steps"]))
        self.assertIn("a rise of 2", " ".join(st["steps"]))
        self.assertIn("The lower vertex's estimate is fixed at 5", html.unescape(self.page))

    def test_patch2_labels_and_defaults(self):
        # g3-27 level 'Zero' only zeroes the chosen vertex; g3-26 and g3-25 defaults are one control from the answer
        d2 = self.demos["C09-D02"]
        self.assertEqual(d2["controls"][1]["values"][0], "Zero at this vertex")
        self.assertEqual(d2["controls"][1]["default"], 1)
        self.assertEqual(self.demos["C09-D01"]["controls"][1]["default"], 0)
        self.assertEqual(self.demos["C09-D03"]["controls"][1]["default"], 1)
        self.assertEqual(self.demos["C09-D04"]["controls"][0]["default"], 0)
        # g3-29 scope note names the admissibility limit, not latency figures
        text = html.unescape(self.page)
        self.assertIn("certified uniform error bound", text)

    def test_text_rules(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for d in self.data["demos"]:
            for s in d["states"].values():
                text += " " + s["interpretation"] + " " + " ".join(" ".join(p) for p in s["metrics"])
        for bad in ("\u2014", "\u2013", "--", "\u2212"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_dom_harness(self):
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        if run.returncode != 0 and "not found" in run.stderr:
            self.skipTest("node missing")
        self.assertEqual(run.returncode, 0, run.stderr + run.stdout)


if __name__ == "__main__":
    unittest.main()

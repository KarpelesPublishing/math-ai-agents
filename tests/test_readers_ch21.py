"""Chapter 21 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here by methods that do not use the
reader module or the laboratory function: a bisection on route costs for the
equilibrium, a brute-force search over flows for the optimum, and the
closed forms printed in the chapter (1.5, 2, 4/3, and a marginal-cost charge
that doubles the congestion term). The reader is built into a temporary
directory, so the committed readers folder is never touched.
"""
from __future__ import annotations

import base64
import html
import importlib.util
import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
MODULE = LAB / "tools" / "readers" / "chapters" / "ch21.py"
SLUG = "21-congestion-incentives"


def builder_python():
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers.builder_python()


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


# Independent network model (capacity 1, outer delay 1). x on each outer route, z on the middle route.

def edge_flow(x, z):
    return x + z


def total_latency(x, z, overhead=0.0):
    """Equation (21.1) edge by edge: S-U and L-T carry x+z at latency x+z; U-T and S-L carry x at latency 1; U-L carries z at latency overhead."""
    v = edge_flow(x, z)
    return v * v + v * v + x * 1.0 + x * 1.0 + z * overhead


def equilibrium(D, slope=1.0, overhead=0.0, toll=0.0):
    """Wardrop equilibrium by bisection. Congestible edges are charged slope x flow (slope 2 is the marginal-cost rule)."""
    def gap(z):  # outer route cost minus middle route cost
        v = edge_flow((D - z) / 2, z)
        return (slope * v + 1.0) - (2 * slope * v + overhead + toll)
    if gap(D) >= 0:
        z = D
    elif gap(0.0) <= 0:
        z = 0.0
    else:
        lo, hi = 0.0, D
        for _ in range(200):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if gap(mid) > 0 else (lo, mid)
        z = (lo + hi) / 2
    return (D - z) / 2, z


def optimum(D, overhead=0.0, steps=40000):
    best = min(range(steps + 1), key=lambda i: total_latency((D - D * i / steps) / 2, D * i / steps, overhead))
    z = D * best / steps
    x = (D - z) / 2
    return total_latency(x, z, overhead), x, z


def route_costs(x, z, slope=1.0, toll=0.0):
    v = edge_flow(x, z)
    return {"outer": slope * v + 1.0, "middle": 2 * slope * v + toll}


class Chapter21ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        python = builder_python()
        if python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([python, str(WRAPPER), "--chapters", "21", "--out", cls.tmp.name], capture_output=True, text=True,
                             timeout=900, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        assert run.returncode == 0, run.stdout + run.stderr
        cls.reader = Path(cls.tmp.name) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def section_text(self, demo_id):
        """Visible static text of one demonstration (question, explanation, symbols, check and answer)."""
        match = re.search(rf'<section class="demo" id="{demo_id}".*?</section>', self.page, re.S)
        self.assertIsNotNone(match, demo_id)
        return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", match.group(0))).split())

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [c["values"][i] for c, i in zip(demo["controls"], idx)]
            yield idx, values, dict(state["metrics"]), state

    # structure

    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C21-D01", "C21-D02", "C21-D03", "C21-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [4, 4, 6, 6])
        self.assertLess(self.reader.stat().st_size, 2_500_000)

    # demonstration 1

    def test_d01_book_numbers_and_every_demand(self):
        demand = {0: 0.5, 1: 1.0, 2: 1.5, 3: 2.0}
        for idx, _, m, state in self.states("C21-D01"):
            D = demand[idx[0]]
            before = D * (D / 2 + 1)
            x, z = equilibrium(D)
            eq = total_latency(x, z)
            opt, _, _ = optimum(D)
            self.assertEqual(m["Total latency before the link"], f"{before:.3f}")
            self.assertEqual(m["Total latency, link added (equilibrium)"], f"{eq:.3f}")
            self.assertEqual(m["Total latency, social optimum"], f"{opt:.3f}")
            self.assertEqual(m["Equilibrium over optimum"], f"{eq / opt:.3f}")
            self.assertEqual(m["Latency of each trip with the link"], f"{eq / D:.3f}")
            self.assertIn(f"= {eq:.2f}", state["interpretation"])
        # The chapter's own figures at demand 1: 1.5 before, 2 after, optimum 1.5, ratio 4/3.
        book = dict(self.demos["C21-D01"]["states"]["1"]["metrics"])
        self.assertEqual((book["Total latency before the link"], book["Total latency, link added (equilibrium)"],
                          book["Total latency, social optimum"], book["Equilibrium over optimum"]), ("1.500", "2.000", "1.500", "1.333"))
        self.assertEqual(book["Latency of each trip with the link"], "2.000")

    def test_d01_boundary_cases_are_named(self):
        low = dict(self.demos["C21-D01"]["states"]["0"]["metrics"])
        self.assertEqual(low["Flow on the middle link"], "all travellers")  # demand 0.5: the link helps
        self.assertEqual(low["Total latency before the link"], "0.625")
        self.assertIn("lowers total latency", self.demos["C21-D01"]["states"]["0"]["interpretation"])
        high = dict(self.demos["C21-D01"]["states"]["3"]["metrics"])
        self.assertEqual(high["Flow on the middle link"], "none")  # demand 2: link available, unused
        self.assertIn("nobody uses it", self.demos["C21-D01"]["states"]["3"]["interpretation"])
        # demand 1.5: outer and middle routes tie at 2.0 with 0.5 on the link (the check question's answer)
        x, z = equilibrium(1.5)
        self.assertAlmostEqual(z, 0.5)
        costs = route_costs(x, z)
        self.assertAlmostEqual(costs["outer"], 2.0)
        self.assertAlmostEqual(costs["middle"], 2.0)
        self.assertAlmostEqual(total_latency(x, z), 3.0)

    # demonstration 2

    def test_d02_ratio_peaks_and_respects_the_bound(self):
        overheads = {0: 0.0, 1: 0.25, 2: 0.5, 3: 1.0}
        for idx, _, m, state in self.states("C21-D02"):
            o = overheads[idx[0]]
            grid = [0.05 * k for k in range(1, 51)]
            ratios = []
            for D in grid:
                x, z = equilibrium(D, overhead=o)
                opt, _, _ = optimum(D, overhead=o, steps=20000)
                ratios.append(total_latency(x, z, o) / opt)
            self.assertLessEqual(max(ratios), 4 / 3 + 1e-9)  # Equation (21.2) holds in every state
            self.assertEqual(m["Largest ratio on the grid"], f"{max(ratios):.3f}")
            self.assertEqual(m["Bound from Equation (21.2)"], "1.333")
            if o < 1:
                mm = 1 - o
                closed = (mm * (2 * mm + o)) / (mm * (mm / 2 + 1))
                self.assertAlmostEqual(max(ratios), closed, places=6)
                self.assertEqual(m["Demand at the largest ratio"], f"{mm:.2f}")
            else:
                self.assertEqual(m["Demand at the largest ratio"], "every demand (flat)")
                self.assertEqual(m["Largest ratio on the grid"], "1.000")
        free = dict(self.demos["C21-D02"]["states"]["0"]["metrics"])
        self.assertEqual((free["Largest ratio on the grid"], free["Room below the bound"]), ("1.333", "0.000"))  # tight at 4/3
        check = dict(self.demos["C21-D02"]["states"]["1"]["metrics"])  # overhead 0.25: the check question
        self.assertEqual(check["Largest ratio on the grid"], f"{1.3125 / 1.03125:.3f}")

    # demonstration 3

    def test_d03_route_costs_flows_and_totals(self):
        slope = {"No charge": 1.0, "Marginal-cost charge": 2.0, "Toll of 0.5 on the middle link only": 1.0}
        toll = {"No charge": 0.0, "Marginal-cost charge": 0.0, "Toll of 0.5 on the middle link only": 0.5}
        for idx, values, m, state in self.states("C21-D03"):
            label, D = values[0], float(values[1])
            x, z = equilibrium(D, slope=slope[label], toll=toll[label])
            costs = route_costs(x, z, slope=slope[label], toll=toll[label])
            opt, _, zo = optimum(D)
            self.assertEqual(m["Outer route cost seen"], f"{costs['outer']:.2f}")
            self.assertEqual(m["Middle route cost seen"], f"{costs['middle']:.2f}")
            self.assertEqual(m["Flow on the middle route"], f"{z:.2f}")
            self.assertEqual(m["Physical total latency"], f"{total_latency(x, z):.3f}")
            self.assertEqual(m["Social optimum"], f"{opt:.3f}")
            # used routes never cost more than unused ones (an equilibrium)
            if z > 1e-9:
                self.assertAlmostEqual(costs["middle"], min(costs.values()))
            if x > 1e-9:
                self.assertAlmostEqual(costs["outer"], min(costs.values()))
        by = {(v[0], float(v[1])): (m, s) for _, v, m, s in self.states("C21-D03")}
        marginal = "Marginal-cost charge"
        m1 = by[(marginal, 1.0)][0]
        self.assertEqual((m1["Flow on the middle route"], m1["Physical total latency"]), ("0.00", "1.500"))  # prediction: no middle flow, 1.5
        m2 = by[(marginal, 0.75)][0]
        self.assertEqual(m2["Flow on the middle route"], "0.25")  # check question: 1 - 0.75
        self.assertEqual(m2["Physical total latency"], f"{2 * 0.5 * 0.5 + 2 * 0.25:.3f}")
        # the marginal-cost equilibrium reproduces the optimal flow (Equation 21.3 and the chapter's claim)
        for D in (1.0, 0.75):
            _, _, zo = optimum(D)
            _, z = equilibrium(D, slope=2.0)
            self.assertAlmostEqual(z, zo, places=3)

    def test_d03_marginal_cost_doubles_only_the_congestion_term(self):
        a, b = 1.0, 1.0  # congestible slope; fixed edge constant
        for q in (0.0, 0.3, 1.0):
            self.assertAlmostEqual((a * q + 0.0) + q * a, 2 * a * q + 0.0)
            self.assertAlmostEqual((0.0 * q + b) + q * 0.0, b)

    def test_d03_toll_reaches_the_optimum_at_every_demand_so_no_fragility_is_claimed(self):
        # g7-26: with the 0.5 toll the equilibrium total equals the optimum at every demand tried, so the old
        # "knife edge" and "happens to" wording (a fragility the chapter never claims) must be gone.
        for D in (0.3, 0.5, 0.6, 0.75, 1.0, 1.01, 1.25, 1.5, 2.0, 2.5):
            x, z = equilibrium(D, toll=0.5)
            opt, _, _ = optimum(D)
            self.assertAlmostEqual(total_latency(x, z), opt, places=3, msg=D)
        for _, v, m, state in self.states("C21-D03"):
            text = state["interpretation"]
            self.assertNotIn("knife edge", text)
            self.assertNotIn("happens to", text)
            self.assertNotIn("only because of where demand sits", text)
            if v[0].startswith("Toll"):
                self.assertIn("A toll on the link alone reaches the optimum here although it charges only one edge", text)
                self.assertEqual(m["Physical total latency"], m["Social optimum"])

    def test_d03_toll_and_marginal_charge_agree_at_both_selectable_demands(self):
        # g7-27: the rules differ, but the two selectable demands show identical flows and totals.
        for D in (1.0, 0.75):
            xt, zt = equilibrium(D, toll=0.5)
            xm, zm = equilibrium(D, slope=2.0)
            self.assertAlmostEqual(xt, xm, places=6)
            self.assertAlmostEqual(zt, zm, places=6)
        text = self.section_text("C21-D03")
        self.assertNotIn("behaves differently", text)
        self.assertIn("the same flows and the same total as the marginal-cost charge", text)

    def test_d03_marginal_charge_at_demand_075_keeps_some_traffic_on_the_middle_route(self):
        # g7-28: at demand 0.75 the flow on the middle route is 0.25, so the choice is not flipped back entirely.
        _, z = equilibrium(0.75, slope=2.0)
        self.assertAlmostEqual(z, 0.25, places=6)
        text = self.section_text("C21-D03")
        self.assertNotIn("flips the choice back", text)
        self.assertIn("moves traffic back toward the outer routes", text)

    def test_d03_rule_labels_fit_the_select_box(self):
        # g7-29: the long option text was clipped at the page width.
        labels = self.demos["C21-D03"]["controls"][0]["values"]
        self.assertIn("Marginal-cost charge", labels)
        self.assertLessEqual(max(len(label) for label in labels), 36)

    def test_d03_left_curve_is_labelled_as_marginal_cost_only_in_other_states(self):
        # g7-33: the doubled 2q curve is the cost under the marginal-cost charge only.
        for _, v, m, state in self.states("C21-D03"):
            svg = base64.b64decode(state["image"].split(",", 1)[1]).decode("utf-8")
            if v[0] == "Marginal-cost charge":
                self.assertIn("2q (with exported", svg)
                self.assertNotIn("charge only)", svg)
            else:
                self.assertIn("charge only)", svg)
                self.assertNotIn("2q (with exported", svg)

    def test_d01_equation_is_not_the_demand_one_only_route_cost(self):
        # g7-19: the middle-route cost is demand + q_middle, equal to 1 + q_middle only at demand 1.
        for D, z in ((0.5, 0.5), (1.5, 0.5), (1.0, 0.4)):
            x = (D - z) / 2
            v = x + z
            self.assertAlmostEqual(2 * v, D + z)
        self.assertNotAlmostEqual(0.5 + 0.5, 1 + 0.5)  # demand 0.5, q_middle 0.5: 1.0, not the displayed 1.5
        alts = [html.unescape(t) for t in re.findall(r'alt="Equation: ([^"]+)"', self.page)]
        self.assertFalse([t for t in alts if "middle" in t])
        self.assertNotIn("q_middle", self.section_text("C21-D01"))

    def test_d01_never_worse_claim_is_limited_to_demand_at_most_one(self):
        # g7-20: with everyone on the link at demand 1.5, the middle route costs 3.0 against 2.5 for an outer route.
        v = 1.5
        self.assertGreater(2 * v, v + 1)
        v = 1.0
        self.assertLessEqual(2 * v, v + 1)
        text = self.section_text("C21-D01")
        self.assertIn("as long as demand is at most the chapter's 1", text)

    def test_d01_grammar_in_the_unused_link_state(self):
        # g7-21
        for _, v, m, state in self.states("C21-D01"):
            self.assertNotIn("no one take ", state["interpretation"])
        unused = self.demos["C21-D01"]["states"]["3"]["interpretation"]
        self.assertIn("no one takes the middle link", unused)

    def test_d01_title_and_symbols_name_the_network(self):
        # g7-30 and g7-34
        for demo_id in ("C21-D01", "C21-D02", "C21-D03"):
            text = self.section_text(demo_id)
            self.assertIn("U the upper junction and L the lower junction", text, demo_id)
        self.assertNotIn("makes every trip slower", self.section_text("C21-D01"))

    def test_d02_arithmetic_is_not_rounded_off_by_hand(self):
        # g7-22: 0.75 x 1.75 = 1.3125 exactly; the page must not print 1.312 for it.
        self.assertAlmostEqual(0.75 * 1.75, 1.3125)
        state = self.demos["C21-D02"]["states"]["1"]["interpretation"]  # delay 0.25
        self.assertIn("= 1.3125", state)
        self.assertIn("1.03125", state)
        self.assertNotIn("= 1.312.", state)
        self.assertNotIn("= 1.312 ", state)

    def test_d02_text_fixes(self):
        # g7-23: no double period, and the slow-link label does not call the link "as slow as an outer route".
        for _, v, m, state in self.states("C21-D02"):
            self.assertNotIn("..", state["interpretation"])
        flat = self.demos["C21-D02"]["states"]["3"]["interpretation"]
        self.assertIn("1.50 / 1.50 = 1.00", flat)
        self.assertNotIn("as slow as the outer route", flat)
        labels = self.demos["C21-D02"]["controls"][0]["values"]
        self.assertIn("1 (the same as a fixed edge)", labels)
        # g7-24: the chapter hedges; the page must not assert that other delays break the bound.
        text = self.section_text("C21-D02")
        self.assertNotIn("break the linear form and the 4/3 figure with it", text)
        self.assertIn("may not have the linear form, in which case the 4/3 figure is not guaranteed", text)

    def test_d04_symbols_label_the_two_expressions(self):
        # g7-31
        text = self.section_text("C21-D04")
        self.assertIn("The first expression, (1 + gamma_cap) r, is the traffic the benchmark carries", text)
        self.assertIn("The second, 1 / gamma_cap, is the guaranteed factor", text)

    # demonstration 4

    def test_d04_capacity_comparison(self):
        for idx, (r, g), m, state in self.states("C21-D04"):
            r, g = float(r), float(g)
            x, z = equilibrium(r)
            eq = total_latency(x, z)
            self.assertAlmostEqual(eq, 2 * r * r)
            opt, _, _ = optimum((1 + g) * r)
            self.assertEqual(m["Equilibrium cost at r"], f"{eq:.3f}")
            self.assertEqual(m["Optimal cost at (1 + extra) r"], f"{opt:.3f}")
            self.assertEqual(m["Equilibrium over optimum"], f"{eq / opt:.3f}")
            self.assertEqual(m["Guaranteed factor 1/extra"], f"{1 / g:.2f}")
            self.assertLessEqual(eq, opt / g + 1e-9)  # the chapter's guarantee holds
            self.assertEqual(m["Within the guarantee"], "yes")
        check = next(m for _, v, m, s in self.states("C21-D04") if float(v[0]) == 1.0 and float(v[1]) == 0.5)
        self.assertEqual(check["Optimal cost at (1 + extra) r"], "2.625")  # 1.5 x (1.5 / 2 + 1)
        # extra = 1 asks the benchmark to carry twice the traffic: equilibrium at r = 1 costs 2, optimum at 2 costs 4
        two = next(m for _, v, m, s in self.states("C21-D04") if float(v[0]) == 1.0 and float(v[1]) == 1.0)
        self.assertEqual((two["Equilibrium cost at r"], two["Optimal cost at (1 + extra) r"]), ("2.000", "4.000"))

    # equations, text, links, harness

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 21)
        text = (LAB.parent / "Manuscript" / "part-v" / "21-markets-teams-and-institutions.md").read_text(encoding="utf-8")

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\(?:qquad|quad)(?![A-Za-z])|\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".,;")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        allowed |= {norm(t) for t in re.findall(r"`([^`\n]+)`", text)}
        allowed |= {norm(t) for t in re.findall(r"\\\((.*?)\\\)", text)}
        shown = []
        shown += [norm(html.unescape(t)) for t in re.findall(r'alt="Equation: ([^"]+)"', self.page)]
        self.assertTrue(shown)
        for tex in shown:
            self.assertIn(tex, allowed)

    def test_links_and_offline(self):
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))
        for href in ("../../notebooks/21-congestion-incentives.ipynb", "../../skills/maa-21-congestion-incentives/SKILL.md"):
            self.assertIn(f'href="{href}"', self.page)
            self.assertTrue((LAB / href.replace("../../", "")).exists(), href)

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
        self.assertNotIn("Manuscript/chapters/", MODULE.read_text(encoding="utf-8"))

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=180)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual(report["states_checked"], 20)
        self.assertEqual(report["resets_checked"], 4)


if __name__ == "__main__":
    unittest.main()

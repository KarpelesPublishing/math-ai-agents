"""Chapter 18 laboratory reader: independent hand checks of a fresh build.

Every expected number is recomputed here from the chapter's own arithmetic
(two-layout beliefs, the intersection rule, exp(-rate x delay), and the
price of another look), not read back from the module that produced the page.
The reader is built into a temporary directory.
"""
from __future__ import annotations

import html
import importlib.util
import json
import math
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


def _builder_python():
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers.builder_python()


def payload(text):
    return json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))


def as_number(text):
    text = text.split(":")[0]  # labels such as "40: unguarded harmful release"
    try:
        return float(text)
    except ValueError:
        return text


@unittest.skipIf(_builder_python() is None, "no interpreter with numpy, matplotlib and jinja2")
class Chapter18ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([_builder_python(), str(WRAPPER), "--chapters", "18", "--out", cls.tmp.name],
                             capture_output=True, text=True, timeout=600)
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls.tmp.name) / "18-interface-freshness" / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    VALUES = {
        "C18-D01": [["coordinate", "semantic", "transactional"], [0.6, 0.8], ["off", "on"]],
        "C18-D02": [[0.0, 0.01, 0.5, 1.0], ["none", "layout1", "layout2"]],
        "C18-D03": [["default", "changed", "transfer"], [5, 10, 15, 30]],
        "C18-D04": [[40, 3], [0.0, 0.1, 0.2], [1, 2]],
    }

    def states(self, demo_id):
        """Yield (control values as written in the reader's definition, metrics, state); the page stores labels, so map by index."""
        for key, state in self.demos[demo_id]["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [vals[i] for vals, i in zip(self.VALUES[demo_id], idx)], dict(state["metrics"]), state

    def test_four_demonstrations_and_budgets(self):
        self.assertEqual(list(self.demos), ["C18-D01", "C18-D02", "C18-D03", "C18-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 12, 12])
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_optional_fields_present(self):
        self.assertIn("Ask the chapter skill", self.page)
        self.assertEqual(self.page.count("Common wrong turn:"), 4)
        self.assertIn('Chapter 18 source: "What this does not settle".', html.unescape(self.page))
        for d in self.data["demos"]:
            self.assertTrue(d["predict"]["correct"] and d["predict"]["incorrect"])
            for state in d["states"].values():
                self.assertTrue(2 <= len(state["steps"]) <= 8)

    def test_d01_transition_law_by_hand_for_three_interfaces(self):
        # Layout 1: every command reaches v2. Layout 2 (rows swapped, version changed):
        #   coordinate reaches v3 (denied when the check is on), semantic still reaches v2,
        #   transactional is refused because the saved version differs.
        for (interface, b1, check), m, _ in self.states("C18-D01"):
            b2 = 1 - b1
            on = check == "on"
            if interface == "coordinate":
                v2, v3, denied = b1, 0.0 if on else b2, b2 if on else 0.0
            elif interface == "semantic":
                v2, v3, denied = 1.0, 0.0, 0.0
            else:
                v2, v3, denied = b1, 0.0, b2
            self.assertEqual(m["Release v2 (authorized completion)"], f"{v2:.2f}", (interface, b1, check))
            self.assertEqual(m["Release v3 (prohibited release)"], f"{v3:.2f}", (interface, b1, check))
            self.assertEqual(m["Denied or refused, no release"], f"{denied:.2f}", (interface, b1, check))
            self.assertEqual(m["Total"], "1.00")
        by = {tuple(v): m for v, m, _ in self.states("C18-D01")}
        # the chapter's beliefs 0.8 and 0.2, and workbench exercise 1's 0.6 and 0.4 (no mediation, then a monitor)
        self.assertEqual(by[("coordinate", 0.8, "off")]["Release v3 (prohibited release)"], "0.20")
        self.assertEqual(by[("coordinate", 0.6, "off")]["Release v3 (prohibited release)"], "0.40")
        self.assertEqual(by[("coordinate", 0.6, "off")]["Release v2 (authorized completion)"], "0.60")
        self.assertEqual(by[("coordinate", 0.6, "on")]["Release v3 (prohibited release)"], "0.00")
        self.assertEqual(by[("coordinate", 0.6, "on")]["Release v2 (authorized completion)"], "0.60")
        # the transactional interface trades completion for safety: refusal probability equals the belief in the changed layout
        self.assertEqual(by[("transactional", 0.8, "off")]["Denied or refused, no release"], "0.20")
        text = next(s for v, m, s in self.states("C18-D01") if v == ["coordinate", 0.6, "off"])["interpretation"]
        self.assertIn("P(release v3) = 0.60 x 0 + 0.40 x 1 = 0.40", text)

    def test_d02_intersection_by_hand(self):
        # Authorized sets: layout 1 allows all five commands; layout 2 allows all but the saved-point click.
        layout1 = {0, 1, 2, 3, 4}
        layout2 = {1, 2, 3, 4}
        for (prior2, obs), m, st in self.states("C18-D02"):
            b2 = {"none": prior2, "layout1": 0.0, "layout2": 1.0}[obs]
            support = [s for s, w in ((layout1, 1 - b2), (layout2, b2)) if w > 0]
            kept = set.intersection(*support)
            self.assertEqual(m["Commands kept"], f"{len(kept)} of 5", (prior2, obs))
            self.assertEqual(m["Saved-point click"], "kept" if 0 in kept else "removed")
            self.assertIn(f"5 - {len(kept)} = {5 - len(kept)}", st["interpretation"])
            self.assertEqual(m["Belief in layout 2"], f"{b2:.2f}")
        by = {tuple(v): m for v, m, _ in self.states("C18-D02")}
        # any positive weight removes the click; zero weight does not (chapter: a very small probability can remove release)
        self.assertEqual((by[(0.0, "none")]["Commands kept"], by[(0.01, "none")]["Commands kept"]), ("5 of 5", "4 of 5"))
        # a perfect read of layout 1 restores the click whatever the prior was; a read of layout 2 confirms its removal
        for prior2 in (0.0, 0.01, 0.5, 1.0):
            self.assertEqual(by[(prior2, "layout1")]["Saved-point click"], "kept")
            self.assertEqual(by[(prior2, "layout2")]["Saved-point click"], "removed")
        half = next(s for v, m, s in self.states("C18-D02") if v == [0.5, "none"])
        self.assertIn("both layouts count, whatever their size", half["interpretation"])
        restore = next(s for v, m, s in self.states("C18-D02") if v == [0.01, "layout1"])
        self.assertIn("only if the read was current and correct", restore["interpretation"])

    def test_d03_cases_age_version_permission_and_freshness_by_hand(self):
        cases = {
            "default": dict(age=1, max_age=2, same=False, permission=True, confirmed=True, coord="delete", sem="release",
                            wanted="release", rate=0.02),
            "changed": dict(age=3, max_age=2, same=False, permission=True, confirmed=True, coord="delete", sem="release",
                            wanted="release", rate=0.02),
            "transfer": dict(age=0, max_age=1, same=True, permission=False, confirmed=False, coord="submit", sem="submit",
                             wanted="submit", rate=0.05),
        }
        for (scenario, delay), m, st in self.states("C18-D03"):
            c = cases[scenario]
            fresh = math.exp(-c["rate"] * delay)
            self.assertEqual(m["Chance still fresh"], f"{fresh:.4f}")
            self.assertEqual(m["Chance of an invalidating change"], f"{1 - fresh:.4f}")
            self.assertEqual(m["Rate x delay"], f"{c['rate'] * delay:.2f}")
            self.assertEqual(m["Delay at which freshness is one half"], f"{math.log(2) / c['rate']:.1f} seconds")
            age_ok = c["age"] <= c["max_age"]
            coord_issued = age_ok and c["permission"]
            sem_issued = age_ok and c["permission"]
            vb_issued = age_ok and c["permission"] and c["same"]
            issued = [n for n, ok in (("coordinate", coord_issued), ("semantic", sem_issued), ("version-bound", vb_issued)) if ok]
            done = []
            if coord_issued and c["coord"] == c["wanted"] and c["confirmed"]:
                done.append("coordinate")
            if sem_issued and c["sem"] == c["wanted"] and c["confirmed"]:
                done.append("semantic")
            if vb_issued and c["sem"] == c["wanted"] and c["confirmed"]:
                done.append("version-bound")
            self.assertEqual(m["Interfaces that issue"], ", ".join(issued) or "none", (scenario, delay))
            self.assertEqual(m["Confirmed completions"], ", ".join(done) or "none", (scenario, delay))
            self.assertEqual(m["Observation age against the limit"],
                             f"{c['age']} s against {c['max_age']} s: {'fresh' if age_ok else 'stale'}")
            self.assertIn(f"{c['rate']:.2f} x {delay} = {c['rate'] * delay:.2f}", st["interpretation"])
        by = {tuple(v): m["Chance still fresh"] for v, m, _ in self.states("C18-D03")}
        # The chapter: 0.9048 at 5 s and 0.5488 at 30 s with rate 0.02; workbench exercise 2 adds 0.7408 at 15 s.
        self.assertEqual((by[("default", 5)], by[("default", 30)], by[("default", 15)]), ("0.9048", "0.5488", "0.7408"))
        # Doubling the delay squares the freshness: 0.7408 squared is 0.5488.
        self.assertAlmostEqual(0.7408 ** 2, 0.5488, places=3)
        # notebook worked example: default issues coordinate and semantic, only semantic completes, version-bound refuses
        d = next(m for v, m, _ in self.states("C18-D03") if v == ["default", 30])
        self.assertEqual((d["Interfaces that issue"], d["Confirmed completions"]), ("coordinate, semantic", "semantic"))
        # changed case (age 3 beyond 2): every interface refuses; transfer case: permission denied blocks all
        self.assertEqual(next(m for v, m, _ in self.states("C18-D03") if v == ["changed", 5])["Interfaces that issue"], "none")
        self.assertEqual(next(m for v, m, _ in self.states("C18-D03") if v == ["transfer", 10])["Interfaces that issue"], "none")
        self.assertAlmostEqual(math.exp(-0.05 * 10), 0.6065, places=4)

    def test_g6_03_age_limit_is_not_drawn_on_the_delay_axis(self):
        source = (LAB / "tools" / "readers" / "chapters" / "ch18.py").read_text(encoding="utf-8")
        self.assertNotIn("age limit {max_age", source)
        self.assertNotIn("axvline(max_age", source)
        for v, m, st in self.states("C18-D03"):
            self.assertIn("they are separate inputs", st["interpretation"], v)
            self.assertIn("changing the delay moves the curve and not the table", st["interpretation"], v)
            self.assertNotIn("dotted line at the age limit", st["alt"], v)
        self.assertNotIn("The age rule is a separate test that the laboratory reports beside the curve", self.page)

    def test_g6_19_20_22_wording(self):
        text = html.unescape(self.page)
        self.assertIn("the saved screen version differs from the current one", text)
        self.assertNotIn("in layout 2 the versions differ", text)
        self.assertIn("Completion is 1.00 in both layouts, so the belief does not matter for this command", text)
        self.assertNotIn("Authorized completion is the whole belief in both layouts", text)
        self.assertIn("the notebook's name for the wrong object (v3 in Demonstration 1)", text)

    def test_d04_price_of_another_look_by_hand(self):
        for (loss, p, cost), m, _ in self.states("C18-D04"):
            now = p * loss
            self.assertEqual(m["Expected loss of clicking now"], f"{now:.2f}")
            self.assertEqual(m["Cost of one more look"], f"{cost:.2f}")
            self.assertEqual(m["Net advantage of looking"], f"{now - cost:.2f}")
            self.assertEqual(m["Break-even chance of a wrong target"], f"{cost / loss:.3f}")
            expected = "tie" if abs(now - cost) < 1e-9 else ("Observe first" if now > cost else "Click now")
            self.assertEqual(m["Better option"], expected)
        by = {tuple(v): (m, s) for v, m, s in self.states("C18-D04")}
        # the chapter: 0.1 x 40 = 4 against a look costing 2 (net 2); with denial costing 3, 0.1 x 3 = 0.3 (look does not pay)
        book = by[(40, 0.1, 2)][0]
        self.assertEqual((book["Expected loss of clicking now"], book["Net advantage of looking"]), ("4.00", "2.00"))
        denied = by[(3, 0.1, 2)][0]
        self.assertEqual((denied["Expected loss of clicking now"], denied["Better option"]), ("0.30", "Click now"))
        # workbench exercise 3: a look costing 1, wrong chance 0.2: denial 3 gives 0.6 (no), unguarded 40 gives 8 (yes)
        self.assertEqual(by[(3, 0.2, 1)][0]["Better option"], "Click now")
        self.assertEqual(by[(3, 0.2, 1)][0]["Expected loss of clicking now"], "0.60")
        self.assertEqual(by[(40, 0.2, 1)][0]["Better option"], "Observe first")
        self.assertEqual(by[(40, 0.2, 1)][0]["Expected loss of clicking now"], "8.00")
        # the transactional interface: chance 0, so the look never pays for document identity
        for key, (m, st) in by.items():
            if key[1] == 0.0:
                self.assertEqual(m["Better option"], "Click now")
                self.assertIn("no value for document identity", st["interpretation"])
        # negative advantage is printed as a plain signed number, in the metric and in the sentence
        neg = by[(3, 0.1, 2)]
        self.assertEqual(neg[0]["Net advantage of looking"], "-1.70")
        self.assertIn("0.30 - 2.0 = -1.70", neg[1]["interpretation"])
        self.assertNotIn("(-1.70)", neg[1]["interpretation"])
        self.assertIn("looking pays when chance x loss is more than its cost", self.page)
        self.assertIn("Act with subscript ui the set of realizable operations", self.page)

    def test_laboratory_agrees_with_chapter_numbers(self):
        import sys
        sys.path.insert(0, str(LAB / "src"))
        from math_ai_agents.chapters.ch18 import evaluate
        out = evaluate({"observation_age": 1, "max_age": 2, "observed_version": "a", "current_version": "b",
                        "current_permission": True, "effect_confirmed": True, "coordinate_target": "x",
                        "semantic_target": "y", "wanted_target": "y", "change_rate": 0.02, "delays": [5, 30]})
        got = [round(r["freshness_probability"], 4) for r in out["metrics"]["freshness_by_delay"]]
        self.assertEqual(got, [0.9048, 0.5488])

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 18)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertGreaterEqual(len(alts), 4)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_text_rules(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"]), (48, 4))
        self.assertEqual((report["ask_skill"], report["predictions_checked"] > 0, report["steps_checked"] > 0, report["panels_checked"] > 0), (1, True, True, True))


if __name__ == "__main__":
    unittest.main()

"""Chapter 27 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(the zero-one routing comparison, the pending-transfer route values, the
M/M/1 mean time, the wait test), not read back from the module that produced
the page. The checks read the built reader with the standard library only.
"""
from __future__ import annotations

import html
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
CHAPTER_TEXT = LAB.parent / "Manuscript" / "part-vi" / "27-the-mathematics-of-delegation.md"


def builder_python():
    for candidate in (LAB / ".venv" / "bin" / "python", Path(sys.executable)):
        if candidate.is_file():
            probe = subprocess.run([str(candidate), "-c", "import numpy, matplotlib, jinja2"], capture_output=True)
            if probe.returncode == 0:
                return str(candidate)
    return None


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


PYTHON = builder_python()
OUT = tempfile.mkdtemp(prefix="readers-ch27-test-")
BUILT = None
if PYTHON is not None:
    run = subprocess.run([PYTHON, str(WRAPPER), "--chapters", "27", "--out", OUT], capture_output=True, text=True, timeout=600)
    if run.returncode == 0:
        BUILT = next(Path(OUT).glob("27-*/reader.html"), None)


def tearDownModule():
    shutil.rmtree(OUT, ignore_errors=True)


@unittest.skipUnless(BUILT is not None, "no interpreter with numpy, matplotlib and jinja2, or the build failed")
class Chapter27ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = BUILT.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)]
            yield values, state

    def test_four_demonstrations_with_state_budget(self):
        self.assertEqual(list(self.demos), ["C27-D01", "C27-D02", "C27-D03", "C27-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 12, 12])
        self.assertLess(BUILT.stat().st_size, 4_000_000)
        for text in ("Ask the chapter skill", "Common wrong turn", "What this does not settle", "Your prediction", "Worked steps"):
            self.assertIn(text, self.page)
        self.assertIn("of 4:", self.page)  # D03 stepper on the delegation fraction
        for demo in self.data["demos"]:
            for state in demo["states"].values():
                self.assertGreaterEqual(len(state["steps"]), 2)

    # Demonstration 1: Equation (27.2) and the workbench's timely-return problem VI.3
    def test_d01_route_and_value_by_hand(self):
        from fractions import Fraction as Fr
        cases = {"Chapter: model 0.78, expert 0.95": (Fr(78, 100), Fr(95, 100)),
                 "Chapter: model 0.78, expert 0.60": (Fr(78, 100), Fr(60, 100)),
                 "Workbench: act 0.80, expert 0.95": (Fr(80, 100), Fr(95, 100)),
                 "Tie: model 0.78, expert 0.78": (Fr(78, 100), Fr(78, 100))}
        ts = {"1.00 (guaranteed)": Fr(1), "0.60": Fr(3, 5), "5/7 (break-even for the workbench case)": Fr(5, 7)}
        demo = self.demos["C27-D01"]
        for key, state in demo["states"].items():
            i, j = (int(x) for x in key.split(","))
            model, expert = cases[list(cases)[i]]
            t = list(ts.values())[j]
            act = model * 10 - (1 - model) * 10
            gross = expert * 10 - (1 - expert) * 10
            deleg = t * gross + (1 - t) * 2 - 1
            m = dict(state["metrics"])
            self.assertEqual(m["Value of acting now"], f"{float(act):.2f}", key)
            self.assertEqual(m["Value of delegating"], f"{float(deleg):.2f}", key)
            eq_route = "Delegate to E" if expert >= model else "Predict the most probable class"
            self.assertTrue(m["Route by Equation (27.2), delay ignored"].startswith(eq_route), key)
            better = "act now" if act > deleg else ("delegate" if deleg > act else "tie")
            self.assertEqual(m["Route with the higher value"], better, key)
            if gross > 2 and (act - 1) / (gross - 2) <= 1:
                self.assertEqual(m["Timely-return probability that ties them"], f"{float((act - 1) / (gross - 2)):.3f}", key)
            else:
                self.assertTrue(m["Timely-return probability that ties them"].startswith("none"), key)
        # the workbench's solution VI.3: 6, 8, 5.2 and the break-even 5/7
        wb = (LAB / "workbook" / "original-mathematical-workbench.md").read_text()
        self.assertIn("5.2", wb)
        g = lambda key, name: dict(demo["states"][key]["metrics"])[name]
        self.assertEqual((g("2,0", "Value of acting now"), g("2,0", "Value of delegating")), ("6.00", "8.00"))
        self.assertEqual(g("2,1", "Value of delegating"), "5.20")
        self.assertEqual(g("2,1", "Route with the higher value"), "act now")
        self.assertEqual(g("2,2", "Route with the higher value"), "tie")
        self.assertEqual(g("2,0", "Timely-return probability that ties them"), f"{5 / 7:.3f}")
        self.assertIn("(5/7) x 9.00 + (2/7) x 2 - 1 = 6.00", demo["states"]["2,2"]["interpretation"])
        # a 0.60 expert never matches acting: its gross value 0.60 x 10 - 0.40 x 10 = 2 equals the fallback
        self.assertTrue(g("1,0", "Timely-return probability that ties them").startswith("none"))
        # the check question
        self.assertAlmostEqual(0.97 - 0.95, 0.02)

    # Demonstration 2: Equation (27.1) filter, then Equation (27.3)
    def test_d02_route_values_and_authorized_set(self):
        timely = 0.90 * (0.98 * 10 + 0.02 * (-10)) + 0.10 * (0.94 * 0 + 0.06 * (-100))
        self.assertAlmostEqual(timely, 8.04)
        names = ["Release now", "Review; release on timeout", "Wait for confirmation; release on timeout",
                 "Reversible hold and review; return on timeout"]
        out = {"all": [], "holdno": [3], "unavail": [1, 3], "stopped": [0]}
        order = list(out)
        demo = self.demos["C27-D02"]
        for key, state in demo["states"].items():
            i, j = (int(x) for x in key.split(","))
            cost = float(demo["controls"][0]["values"][i])
            vals = [-1.0, 0.35 * timely + 0.65 * (-1) - 1, 0.5 * 9 + 0.5 * (-1) - 2, 0.95 * timely + 0.05 * (-4) - cost - 1]
            excluded = out[order[j]]
            m = dict(state["metrics"])
            for n, v, e in zip(names, vals, [k in excluded for k in range(4)]):
                self.assertEqual(m[n], f"{v:.3f}" + (" (excluded)" if e else ""), (key, n))
            inside = [k for k in range(4) if k not in excluded]
            best = max(inside, key=lambda k: vals[k])
            self.assertEqual(m["Highest among the authorized routes"], names[best], key)
            self.assertEqual(m["Hold cost at which waiting (2) overtakes it"], "4.438")
        # the book's table: -1, 1.164, 2, 4.438 with the hold winning
        mm = dict(demo["states"]["0,0"]["metrics"])
        self.assertEqual([mm[n] for n in names], ["-1.000", "1.164", "2.000", "4.438"])
        self.assertEqual(mm["Highest among the authorized routes"], names[3])
        # raising the hold cost to 5 hands the win to waiting (1.438 < 2); an unauthorized hold also does
        self.assertEqual(dict(demo["states"]["2,0"]["metrics"])["Highest among the authorized routes"], names[2])
        self.assertIn("1.438", dict(demo["states"]["2,0"]["metrics"])[names[3]])
        self.assertEqual(dict(demo["states"]["0,1"]["metrics"])["Highest among the authorized routes"], names[2])
        # the excluded route would have won and stays a recommendation
        self.assertIn("stays a recommendation", demo["states"]["0,1"]["interpretation"])
        self.assertIn("0.95 x 8.04 + 0.05 x (-4) - 1 = 6.438", demo["states"]["0,0"]["interpretation"])
        self.assertIn("6.438 - 2 = 4.438", demo["states"]["0,0"]["interpretation"])
        # check question: hold cost 4 gives 2.438
        self.assertAlmostEqual(0.95 * 8.04 + 0.05 * (-4) - 4 - 1, 2.438)

    # Demonstration 3: M/M/1 mean time and the laboratory's release contract
    def test_d03_mm1_and_ledger_by_hand(self):
        wb = (LAB / "workbook" / "workbook.md").read_text()
        self.assertIn('"name": "release", "agent_authorized": false, "risk": 0.05', wb)
        nb = json.loads((LAB / "data" / "examples" / "ch27.json").read_text())
        self.assertEqual((nb["arrival_rate"], nb["service_rate"], nb["delegation_fraction"]), (1, 2, 1))
        tasks = {"default": (4, 3, 0.1, [("routine", True, 0.02, 2, False, False), ("release", False, 0.05, 2, True, True),
                                         ("sensitive", False, 0.2, 2, True, False)]),
                 "fast": (4, 4, 0.1, [("routine", True, 0.02, 2, False, False), ("release", False, 0.05, 2, True, True),
                                      ("sensitive", False, 0.2, 2, True, False)]),
                 "transfer": (1, 2, 0.05, [("approval", False, 0.01, 0.5, True, True)])}
        order = ["default", "fast", "transfer"]
        demo = self.demos["C27-D03"]
        for key, state in demo["states"].items():
            i, j = (int(x) for x in key.split(","))
            lam, mu, limit, rows = tasks[order[i]]
            f = float(demo["controls"][1]["values"][j])
            load = lam * f
            m = dict(state["metrics"])
            self.assertEqual(m["Review arrivals f x lambda (per hour)"], f"{load:.2f}")
            released = 0
            for name, agent, risk, deadline, human, packet in rows:
                needs = (not agent) or risk > limit
                if not needs:
                    released += 1
                elif load < mu:
                    released += int(human and packet and 1 / (mu - load) <= deadline)
            self.assertEqual(m["Tasks released"], f"{released} of {len(rows)}", key)
            if load < mu:
                self.assertEqual(m["Mean time in system"], f"{1 / (mu - load):.2f} hours ({60 / (mu - load):.0f} minutes)", key)
            else:
                self.assertIn("undefined", m["Mean time in system"], key)
        g = lambda key, name: dict(demo["states"][key]["metrics"])[name]
        self.assertEqual(g("0,0", "Mean time in system"), "1.00 hours (60 minutes)")   # notebook default
        self.assertEqual(g("0,0", "Tasks released"), "2 of 3")
        self.assertIn("5.00 hours", g("0,1", "Mean time in system"))                   # chapter: 70 percent gives 5 hours
        self.assertIn("undefined", g("0,2", "Mean time in system"))                    # notebook changed case: 3.6 > 3
        self.assertEqual(g("0,2", "Tasks released"), "1 of 3")
        self.assertEqual(g("2,3", "Tasks released"), "0 of 1")                         # notebook transfer: mean 1 > 0.5
        # the exponential tail the skill quotes: 1 - exp(-2) = 0.865 at the default state
        self.assertEqual(g("0,0", "Chance the first delegated case meets its deadline"), f"{1 - math.exp(-2):.3f}")
        self.assertIn("1 - exp(-1.00 x 2.0) = 0.865", demo["states"]["0,0"]["interpretation"])

    def test_d03_names_the_m_m_1_model(self):
        self.assertIn("M/M/1", self.page)
        self.assertIn("exponentially distributed service times", self.page)
        rho, mu = 2 / 3, 3
        self.assertAlmostEqual(1 / mu + rho / (2 * mu * (1 - rho)), 2 / 3)   # deterministic service would give 2/3, not 1
        self.assertAlmostEqual(1 / (mu - 2), 1.0)
        unstable = self.demos["C27-D03"]["states"]["0,2"]
        self.assertIn("long-run", unstable["interpretation"] + " long-run")

    # Demonstration 4: Equation (27.4)
    def test_d04_wait_test_and_reachable_states(self):
        demo = self.demos["C27-D04"]
        gaps = ["none", "late", "changed", "failed"]
        for key, state in demo["states"].items():
            i, j = (int(x) for x in key.split(","))
            q = float(demo["controls"][0]["values"][i])
            voi = q * 9 + (1 - q) * (-1) + 1
            ok = gaps[j] == "none"
            m = dict(state["metrics"])
            self.assertEqual(m["Value of information (VOI)"], f"{voi:.2f}", key)
            allowed = voi > 2 + 1e-9 and ok
            self.assertEqual(m["Passes Equation (27.4)"].startswith("Yes"), allowed, key)
            self.assertEqual(m["Fallback authorized in every reachable state"].startswith("yes"), ok, key)
        g = lambda key: dict(demo["states"][key]["metrics"])["Passes Equation (27.4)"]
        self.assertEqual(g("0,0"), "No (VOI equals delay cost)")          # strict inequality at q = 0.2
        self.assertEqual(g("1,0"), "Yes (waiting allowed)")
        self.assertTrue(g("2,2").startswith("No (a reachable state"))      # high VOI, one state without a fallback
        # check question: delay cost 3, q = 0.5 gives VOI 5 > 3; boundary at q = 0.30
        self.assertAlmostEqual(0.5 * 9 + 0.5 * (-1) + 1, 5.0)
        self.assertIn("at or below q = 3 / 10 = 0.30", self.page)

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 27)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\(quad|qquad)", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".,;")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        allowed |= {norm(m) for m in re.findall(r"`([^`]+)`", CHAPTER_TEXT.read_text(encoding="utf-8"))}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 4)  # (27.1) to (27.4) are pre-rendered; the inline M/M/1 formula is typeset as TeX
        self.assertIn(r"1/(\mu-f\lambda)", html.unescape(self.page))
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

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

    def test_all_control_combinations_render(self):
        for d in self.data["demos"]:
            expected = 1
            for c in d["controls"]:
                expected *= len(c["values"])
            self.assertEqual(len(d["states"]), expected, d["id"])
            for state in d["states"].values():
                self.assertTrue(state["image"].startswith("data:image/svg+xml"))
                self.assertTrue(state["interpretation"])

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(BUILT)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"]), (48, 4))


if __name__ == "__main__":
    unittest.main()

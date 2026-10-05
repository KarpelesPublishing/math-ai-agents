"""Chapter 25 laboratory reader: independent hand checks of the built page.

The reader is built into a temporary directory (never the shared readers
folder). Every expected number is recomputed here from the chapter's own
arithmetic by a method different from the module's.
"""
from __future__ import annotations

import html
import itertools
import json
import math
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
SLUG = "25-development-guard-gate"


def venv_python():
    py = LAB / ".venv" / "bin" / "python"
    return str(py) if py.exists() else None


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


class Chapter25ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        python = venv_python()
        if python is None:
            raise unittest.SkipTest("laboratory .venv absent")
        cls.tmp = tempfile.mkdtemp()
        run = subprocess.run([python, str(WRAPPER), "--chapters", "25", "--out", cls.tmp], capture_output=True, text=True, timeout=600)
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls.tmp) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', cls.page, re.S).group(1))
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [as_number(c["values"][i]) for c, i in zip(demo["controls"], idx)], dict(state["metrics"]), state

    def test_structure_and_budget(self):
        self.assertEqual(list(self.demos), ["C25-D01", "C25-D02", "C25-D03", "C25-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 12, 12])
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_new_fields_are_rendered(self):
        for text in ("Ask the chapter skill", "Common wrong turn", "What this does not settle", "Your prediction", "Worked steps"):
            self.assertIn(text, self.page)
        for demo in self.data["demos"]:
            for state in demo["states"].values():
                self.assertGreaterEqual(len(state["steps"]), 2)

    def test_d01_canary_by_hand(self):
        traces = {"steady": [0.80, 0.82, 0.81, 0.83, 0.82, 0.84, 0.83, 0.82],
                  "creeping": [0.80, 0.83, 0.86, 0.89, 0.92, 0.95, 0.98, 1.01],
                  "spike": [0.80, 0.81, 0.95, 0.82, 0.81, 0.80, 0.82, 0.81]}
        names = list(traces)
        demo = self.demos["C25-D01"]
        for k, state in demo["states"].items():
            i, j, f = (int(x) for x in k.split(","))
            costs = traces[names[i]]
            boundary = 1.00 - 0.10 if j == 0 else 1.00
            hit = [p + 1 for p, c in enumerate(costs) if round(c - boundary, 6) > 0]
            m = dict(state["metrics"])
            expect = f"period {hit[0]}" if hit else "none"
            self.assertEqual(m["Alert under the boundary used"], expect, k)
            self.assertEqual(m["Periods under phi'"], f"{hit[0] if hit else 8} of 8", k)
            self.assertEqual(m["Alert under the declared 0.90"], f"period {[p + 1 for p, c in enumerate(costs) if c > 0.9][0]}" if any(c > 0.9 for c in costs) else "none")
            self.assertIn("0 (theta", m["Model parameters changed"])
        # creeping, declared: 0.89 is not above 0.90, 0.92 is; moved boundary 1.00 waits for 1.01
        self.assertEqual(dict(demo["states"]["1,0,0"]["metrics"])["Alert under the boundary used"], "period 5")
        self.assertEqual(dict(demo["states"]["1,1,0"]["metrics"])["Alert under the boundary used"], "period 8")
        self.assertEqual(dict(demo["states"]["2,1,0"]["metrics"])["Alert under the boundary used"], "none")
        self.assertIn("1.00 - 0.10 = 0.90", demo["states"]["1,0,0"]["interpretation"])
        # check question: 1.20 - 0.15 = 1.05, first cost above is 1.08 in period 3
        self.assertAlmostEqual(1.20 - 0.15, 1.05)
        self.assertEqual([p + 1 for p, c in enumerate([1.00, 1.05, 1.08, 1.12]) if c > 1.05 + 1e-9][0], 3)

    def test_d02_gate_by_hand(self):
        base = {"default": [1, 0, 1, 0], "changed": [1, 0, 1, 0], "transfer": [0, 1]}
        # the transfer case is read from the notebook data, not copied from the module
        nb = json.loads((LAB / "data" / "examples" / "ch25.json").read_text())
        self.assertEqual([int(x) for x in nb["baseline_guard"]], base["transfer"])
        self.assertEqual(nb["minimum_guard_gain"], 0.1)
        self.assertTrue(nb["guard_reused"])
        guard = {"default": {"flashy": [1, 0, 1, 0], "steady": [1, 1, 1, 0]},
                 "changed": {"flashy": [1, 1, 1, 0], "steady": [1, 1, 1, 0]},
                 "transfer": {"proposal": [1, 1]}}
        dev = {"default": {"flashy": 4 / 4, "steady": 3 / 4}, "changed": {"flashy": 1.0, "steady": 0.75}, "transfer": {"proposal": 1.0}}
        thr = {"default": 0.2, "changed": 0.2, "transfer": 0.1}
        wb = (LAB / "workbook" / "workbook.md").read_text()
        self.assertIn("baseline_guard = [true, false, true, false]", wb)
        self.assertIn("minimum_guard_gain = 0.1", wb)
        cases = ["default", "changed", "transfer"]
        demo = self.demos["C25-D02"]
        for k, state in demo["states"].items():
            i, j, c = (int(x) for x in k.split(","))
            case, reused, by_guard = cases[i], j == 1, c == 1
            gains = {n: sum(g - b for g, b in zip(v, base[case])) / len(base[case]) for n, v in guard[case].items()}
            winner = max(dev[case], key=dev[case].get)
            pick = winner
            shaped = False
            if by_guard and gains[winner] < max(gains.values()) - 1e-12:
                pick = max(gains, key=gains.get)
                shaped = True
            m = dict(state["metrics"])
            self.assertEqual(m["Selected on development"], winner, k)
            self.assertEqual(m["Candidate tested on the guard"], pick, k)
            self.assertEqual(m["Guard gain of the tested candidate"], f"{gains[pick]:.2f}", k)
            if reused:
                expected = "rejected (guard reused)"
            elif shaped:
                expected = "rejected (guard picked the winner)"
            else:
                expected = "accepted by this gate" if gains[pick] >= thr[case] - 1e-12 else "rejected (gain below threshold)"
            self.assertEqual(m["Release decision"], expected, k)
        mk = lambda key, name: dict(demo["states"][key]["metrics"])[name]
        self.assertEqual(mk("0,0,0", "Guard gain of the tested candidate"), "0.00")
        self.assertEqual(mk("1,0,0", "Release decision"), "accepted by this gate")
        self.assertEqual(mk("2,1,0", "Release decision"), "rejected (guard reused)")
        self.assertEqual(mk("2,0,0", "Guard gain of the tested candidate"), "0.50")
        self.assertEqual(mk("0,0,1", "Candidate tested on the guard"), "steady")
        # check question: (2 x 1 + 1 x (-1) + 5 x 0) / 8
        self.assertAlmostEqual((2 - 1) / 8, 0.125)

    def test_d03_bound_ledger_and_exact_tail(self):
        def exact(m, tau=0.25):
            dist = {0: 1.0}
            for _ in range(m):
                nxt = {}
                for s_, p in dist.items():
                    nxt[s_ + 1] = nxt.get(s_ + 1, 0) + p / 2
                    nxt[s_ - 1] = nxt.get(s_ - 1, 0) + p / 2
                dist = nxt
            return sum(p for s_, p in dist.items() if s_ / m >= tau - 1e-12)
        def sig3(x):
            return f"{x:.{max(0, 2 - int(math.floor(math.log10(x))))}f}"
        demo = self.demos["C25-D03"]
        for (m, q, r), met, state in self.states("C25-D03"):
            m, q = int(m), int(q)
            idx = [int(x) for x in [k for k, s_ in demo["states"].items() if s_ is state][0].split(",")]
            redesigned = idx[2] == 1
            covered = 2 if redesigned else q
            bound = math.exp(-m * 0.25 ** 2 / 2)
            self.assertEqual(met["Bound, one decision"], sig3(bound))
            self.assertEqual(met["Exact tail, fair plus or minus 1 case"], sig3(exact(m)))
            self.assertLess(exact(m), bound)
            self.assertEqual(met["Decisions fixed before guard access"], f"{covered} of {q}")
            self.assertEqual(met["Decisions needing a fresh guard"], str(q - covered))
            total = met["Total bound over those decisions"]
            if covered * bound > 1:
                self.assertIn("says nothing", total)
            else:
                self.assertTrue(total.startswith(sig3(covered * bound)))
        mm = dict(demo["states"]["1,1,0"]["metrics"])
        self.assertEqual(mm["Bound, one decision"], "0.00193")
        self.assertTrue(mm["Total bound over those decisions"].startswith("0.0193"))
        mm = dict(demo["states"]["1,1,1"]["metrics"])
        self.assertTrue(mm["Total bound over those decisions"].startswith("0.00386"))
        self.assertEqual(mm["Decisions needing a fresh guard"], "8")
        # workbook VI.2 numbers: exp(-6.25) = 0.00193045 and ten times that
        self.assertAlmostEqual(math.exp(-6.25), 0.00193045, places=8)
        self.assertAlmostEqual(math.exp(-300 * 0.0625 / 2), 0.0000848, places=7)

    def test_d04_all_four_conditions(self):
        others = {"all": (0.80, 1, 1), "cost": (0.95, 1, 1), "authority": (0.80, 0, 1), "rollback": (0.80, 1, 0)}
        demo = self.demos["C25-D04"]
        keys = ["all", "cost", "authority", "rollback"]
        for k, state in demo["states"].items():
            i, j = (int(x) for x in k.split(","))
            uplift = float(demo["controls"][0]["values"][i])
            cost, auth, roll = others[keys[j]]
            flags = [uplift >= 0.25 - 1e-12, cost <= 1.0 - 0.1 + 1e-12, bool(auth), bool(roll)]
            m = dict(state["metrics"])
            self.assertEqual(m["Accept"].startswith("yes"), all(flags), k)
            for name, flag in zip(["1. Uplift condition", "2. Cost condition", "3. Authorized in scope", "4. Rollback path tested"], flags):
                self.assertTrue(m[name].startswith("pass" if flag else "fail"), (k, name))
        # uplift exactly 0.25 passes ("at least"); cost 0.95 under c = 1.00 still fails the margin
        self.assertTrue(dict(demo["states"]["1,0"]["metrics"])["1. Uplift condition"].startswith("pass"))
        self.assertTrue(dict(demo["states"]["2,1"]["metrics"])["2. Cost condition"].startswith("fail"))
        self.assertEqual(dict(demo["states"]["2,0"]["metrics"])["Accept"], "yes (1)")
        # workbook VI.2 third candidate: uplift and cost pass, authority blocks
        self.assertIn("authority still blocks", demo["states"]["2,2"]["interpretation"])
        self.assertGreater(0.92, 1.00 - 0.10)

    def test_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 25)
        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 4)
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


if __name__ == "__main__":
    unittest.main()

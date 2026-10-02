"""Chapter 10 reader tests: independent recomputation of every headline number.

Expected values are derived here from the chapter's own arithmetic, not read
back from the module. The module is built in memory, so no committed page is
needed.
"""
from __future__ import annotations

import html
import importlib.util
import itertools
import json
import re
import sys
import unittest
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
ENGINE = LAB / "tools" / "readers" / "engine"
CHAPTERS = LAB / "tools" / "readers" / "chapters"
for p in (str(LAB / "src"), str(ENGINE)):
    if p not in sys.path:
        sys.path.insert(0, p)

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

spec = importlib.util.spec_from_file_location("reader_ch10", CHAPTERS / "ch10.py")
ch10 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ch10)


def run(demo_index, **controls):
    demo = ch10.CHAPTER["demos"][demo_index]
    fig, metrics, text = getattr(ch10, demo["function"])(**controls)
    plt.close(fig)
    return metrics, text


class Chapter10ReaderTests(unittest.TestCase):
    def test_structure_and_state_budget(self):
        demos = ch10.CHAPTER["demos"]
        self.assertEqual([d["id"] for d in demos], ["C10-D01", "C10-D02", "C10-D03", "C10-D04"])
        counts = []
        for d in demos:
            n = 1
            for c in d["controls"]:
                n *= len(c["values"])
            counts.append(n)
        self.assertEqual(counts, [6, 6, 8, 6])

    def test_every_control_combination_renders(self):
        for d in ch10.CHAPTER["demos"]:
            for combo in itertools.product(*[c["values"] for c in d["controls"]]):
                kwargs = {c["key"]: v for c, v in zip(d["controls"], combo)}
                metrics, text = run(ch10.CHAPTER["demos"].index(d), **kwargs)
                self.assertTrue(metrics and text, (d["id"], kwargs))
                for bad in ("\u2014", "\u2013", "--"):
                    self.assertNotIn(bad, text)

    def test_d01_durations_and_initiation_set(self):
        for n, m in itertools.product([1, 4], [0, 2, 4]):
            metrics, text = run(0, min_records=n, stop_at=m)
            allowed = [x for x in range(1, 9) if x >= n]
            tau = lambda x: x - m if (m and x > m) else x
            self.assertEqual(metrics["Start states allowed"], f"{len(allowed)} of 8")
            self.assertEqual(metrics["Duration from x = 6"], f"{tau(6)} steps")
            self.assertEqual(metrics["Longest duration from an allowed start"], f"{max(tau(x) for x in allowed)} steps")
        # Chapter-style hand check: 6 records, stop at 2 remaining: 6 - 2 = 4.
        self.assertIn("6 - 2 = 4", run(0, min_records=1, stop_at=2)[1])
        # Boundary: a start at or below the stop level runs to the end (x = 2 with stop 2 lasts 2).
        self.assertIn("from x = 2 the duration is 2", run(0, min_records=1, stop_at=2)[1])
        self.assertEqual(run(0, min_records=4, stop_at=0)[0]["Initiation set"], "x = 4 to 8")

    def test_d02_book_numbers_and_all_states(self):
        # Chapter: 2 + 0.9(3) + 0.9^2(10) = 12.8; one-step continuation gives 13.7.
        metrics, text = run(1, duration=2, gamma=0.9)
        self.assertEqual(metrics["Value by Equation (10.2)"], "12.800")
        self.assertEqual(metrics["Value if discounted as one step"], "13.700")
        self.assertEqual(metrics["Overstatement"], "0.900")
        for tau, g in itertools.product([2, 3, 4], [0.5, 0.9]):
            rewards = [2, 3] + [0] * (tau - 2)
            value = sum(g ** k * r for k, r in enumerate(rewards)) + g ** tau * 10
            wrong = sum(g ** k * r for k, r in enumerate(rewards)) + g * 10
            m, _ = run(1, duration=tau, gamma=g)
            self.assertEqual(m["Value by Equation (10.2)"], f"{value:.3f}")
            self.assertEqual(m["Value if discounted as one step"], f"{wrong:.3f}")
            self.assertGreaterEqual(wrong, value - 1e-12)
        self.assertEqual(run(1, duration=3, gamma=0.9)[0]["Value by Equation (10.2)"], "11.990")

    def test_d03_time_is_a_maximum_and_cost_is_a_sum(self):
        for a, mode in itertools.product([2, 4, 6, 8], ["parallel", "after"]):
            m, text = run(2, audit_minutes=a, mode=mode)
            t = max(6, a) if mode == "parallel" else 6 + a
            self.assertEqual(m["Release time"], f"{t} minutes")
            self.assertEqual(m["Total tool cost"], "16 credits")
        self.assertEqual(run(2, audit_minutes=4, mode="parallel")[0]["Release time"], "6 minutes")
        tie = run(2, audit_minutes=6, mode="parallel")
        self.assertIn("tie", tie[0]["Longest chain"])
        self.assertIn("tie at 6 minutes", tie[1])
        self.assertEqual(run(2, audit_minutes=8, mode="parallel")[0]["Longest chain"], "Audit")
        self.assertEqual(run(2, audit_minutes=2, mode="parallel")[0]["Longest chain"], "Draft, Verify, Publish")

    def test_d04_interruption(self):
        expected = {}
        for k, g in itertools.product([3, 2, 1], [0.9, 0.5]):
            rewards = [-1, -1, 8][:k]
            v = sum(g ** t * r for t, r in enumerate(rewards))
            if k == 3:
                v += g ** 3 * 2
            expected[(k, g)] = v
            m, _ = run(3, steps_allowed=k, gamma=g)
            self.assertEqual(m["review-release value"], f"{v:.3f}")
            self.assertEqual(m["archive value"], "1.000")
            self.assertEqual(m["review-release completed"], "yes" if k == 3 else "no")
            self.assertEqual(m["Higher executed value"], "review-release" if v > 1 else "archive")
        self.assertAlmostEqual(expected[(3, 0.9)], 6.038)
        self.assertAlmostEqual(expected[(2, 0.9)], -1.9)
        self.assertEqual(run(3, steps_allowed=3, gamma=0.5)[0]["review-release value"], "0.750")
        self.assertEqual(run(3, steps_allowed=3, gamma=0.5)[0]["Higher executed value"], "archive")

    def test_patch_g4_ch10_wording(self):
        demos = ch10.CHAPTER["demos"]
        # g4-01: the smaller gamma is not claimed to grow the gap faster.
        d2 = demos[1]
        self.assertNotIn("grow faster", d2["explanation"])
        self.assertNotIn("stronger discount", d2["explanation"])
        self.assertIn("larger gap at durations 2 to 4", d2["explanation"])
        over = {}
        for tau, g in itertools.product([2, 3, 4], [0.5, 0.9]):
            over[(tau, g)] = run(1, duration=tau, gamma=g)[0]["Overstatement"]
            self.assertEqual(over[(tau, g)], f"{10 * (g - g ** tau):.3f}")
        for tau in (2, 3, 4):
            self.assertGreater(float(over[(tau, 0.5)]), float(over[(tau, 0.9)]))
        # g4-05: question direction matches the metric.
        self.assertIn("How much does the value rise", d2["question"])
        self.assertNotIn("lost", d2["question"])
        # g4-06: no literal placeholder, correct plural.
        self.assertIn("pushed 1 step later", run(1, duration=3, gamma=0.9)[1])
        self.assertIn("pushed 2 steps later", run(1, duration=4, gamma=0.9)[1])
        for tau, g in itertools.product([2, 3, 4], [0.5, 0.9]):
            self.assertNotIn("step(s)", run(1, duration=tau, gamma=g)[1])
        # g4-02: the zero continuation is stated as a stipulation, not as Equation (10.2).
        d4 = demos[3]
        self.assertNotIn("has no continuation", d4["title"])
        self.assertIn("without continuation", d4["title"])
        self.assertNotIn("adds the continuation only when the option ends", d4["explanation"])
        self.assertIn("stipulates V = 0", d4["explanation"])
        self.assertIn("stipulation", d4["assumptions"])
        for k in (2, 1):
            self.assertIn("by stipulation", run(3, steps_allowed=k, gamma=0.9)[1])
            self.assertNotIn("unfinished work does not inherit", run(3, steps_allowed=k, gamma=0.9)[1])
        # g4-03: provenance names the laboratory values, not "the chapter's discount".
        self.assertNotIn("chapter's discount 0.9", d4["provenance"])
        self.assertIn("laboratory's example values", d4["provenance"])
        # g4-04: sequence is not claimed to be cheaper.
        self.assertNotIn("cheap but slow", demos[2]["application"])
        self.assertIn("costs the same", demos[2]["application"])
        # g4-07: no interruption in the default state, no stray archive sentence, no placeholder.
        for g in (0.9, 0.5):
            default = run(3, steps_allowed=3, gamma=g)[1]
            self.assertNotIn("Archive needs one step", default)
            self.assertNotIn("step(s)", default)
        fig_title = None
        for k, expected in ((3, "no interruption"), (2, "interrupted after 2 steps"), (1, "interrupted after 1 step")):
            fig, _, text = getattr(ch10, "interruption_picture")(steps_allowed=k, gamma=0.9)
            fig_title = fig.axes[0].get_title()
            plt.close(fig)
            self.assertIn(expected, fig_title)
            self.assertNotIn("step(s)", fig_title)
            if k < 3:
                self.assertIn(f"interruption after {k} ", text)
        # g4-11 / g4-12: undefined jargon removed, termination sentence corrected.
        self.assertNotIn("reward-free corridor", demos[0]["assumptions"])
        self.assertIn("at or below the stop level runs to the end", demos[0]["assumptions"])
        self.assertNotIn("Duration depends on where the option starts", run(0, min_records=1, stop_at=0)[1])
        # g4-14 note: the deadline is said not to bind.
        self.assertIn("does not bind", d4["symbols"])

    def test_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 10)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\(?:quad|qquad)|\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".,;")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        for d in ch10.CHAPTER["demos"]:
            for tex in d["equations"]:
                self.assertIn(norm(html.unescape(tex)), allowed, d["id"])

    def test_text_rules(self):
        blob = json.dumps(ch10.CHAPTER, ensure_ascii=False)
        for bad in ("\u2014", "\u2013", "--"):
            self.assertNotIn(bad, blob)
        for d in ch10.CHAPTER["demos"]:
            self.assertIn("constructed", d["provenance"].lower())
            self.assertTrue(d["check"].endswith("?"))


if __name__ == "__main__":
    unittest.main()

"""Chapter 10 reader tests: independent recomputation of every headline number.

Expected values are derived here from the chapter's own arithmetic, not read
back from the module. The module is imported for state-by-state checks, and
the reader is built into a temporary directory (never the shared readers
folder) for the page, equation and DOM-harness checks.
"""
from __future__ import annotations

import html
import importlib.util
import itertools
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

LAB = Path(__file__).resolve().parent.parent
ENGINE = LAB / "tools" / "readers" / "engine"
CHAPTERS = LAB / "tools" / "readers" / "chapters"
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = ENGINE / "dom_harness.js"
PYTHON = LAB / ".venv" / "bin" / "python"
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
    fig, metrics, text, extra = getattr(ch10, demo["function"])(**controls)
    plt.close(fig)
    return metrics, text, extra


def f3(x):
    return f"{x:.3f}"


def states(index):
    d = ch10.CHAPTER["demos"][index]
    for combo in itertools.product(*[c["values"] for c in d["controls"]]):
        yield {c["key"]: v for c, v in zip(d["controls"], combo)}


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
        self.assertEqual(counts, [9, 12, 12, 8])
        self.assertIn("prompt", ch10.CHAPTER["ask_skill"])

    def test_every_state_renders_with_steps_and_alt(self):
        for i in range(4):
            for kwargs in states(i):
                metrics, text, extra = run(i, **kwargs)
                self.assertTrue(metrics and text and extra["alt"] and 2 <= len(extra["steps"]) <= 8, (i, kwargs))
                for s in extra["steps"]:
                    self.assertLessEqual(len(s), 240)
                for bad in ("\u2014", "\u2013", "--"):
                    self.assertNotIn(bad, text + " ".join(extra["steps"]))

    def test_d01_durations_blocked_starts_and_initiation_set(self):
        for n, m in itertools.product([1, 4, 7], [0, 2, 4]):
            metrics, text, _ = run(0, min_records=n, stop_at=m)
            allowed = [x for x in range(1, 9) if x >= n]
            tau = lambda x: x - m if (m and x > m) else x
            run_steps = lambda x: tau(x) if x >= n else 0
            plural = lambda k: "1 step" if k == 1 else f"{k} steps"
            self.assertEqual(metrics["Start states allowed"], f"{len(allowed)} of 8")
            self.assertEqual(metrics["Steps run from x = 6"], plural(run_steps(6)))
            self.assertEqual(metrics["Steps run from x = 8"], plural(run_steps(8)))
            self.assertEqual(metrics["Longest run from an allowed start"], plural(max(run_steps(x) for x in range(1, 9))))
        self.assertIn("6 - 2 = 4", run(0, min_records=1, stop_at=2)[1])
        self.assertIn("from x = 2 the duration is 2", run(0, min_records=1, stop_at=2)[1])
        self.assertEqual(run(0, min_records=4, stop_at=0)[0]["Initiation set"], "x = 4 to 8")
        # a blocked start earns nothing: x = 6 with a start rule of at least 7
        blocked = run(0, min_records=7, stop_at=0)
        self.assertEqual(blocked[0]["Steps run from x = 6"], "0 steps")
        self.assertIn("cannot start", blocked[1])
        # the prediction state: at least 4, stop at 2 remaining: x = 6 runs 4 steps, x = 3 is blocked
        self.assertEqual(run(0, min_records=4, stop_at=2)[0]["Steps run from x = 6"], "4 steps")

    def test_d02_book_numbers_exercise_and_transfer(self):
        # Chapter: 2 + 0.9(3) + 0.9^2(10) = 12.8; one-step continuation gives 13.7.
        metrics, text, _ = run(1, case="chapter", duration=2, gamma=0.9)
        self.assertEqual(metrics["Value by Equation (10.2)"], "12.800")
        self.assertEqual(metrics["Value if discounted as one step"], "13.700")
        self.assertEqual(metrics["Overstatement"], "0.900")
        for case, rewards, v in (("chapter", [2, 3], 10), ("transfer", [0, 4], 8)):
            for tau, g in itertools.product([2, 3, 4], [0.5, 0.9]):
                r = rewards + [0] * (tau - 2)
                inside = sum(g ** k * x for k, x in enumerate(r))
                value = inside + g ** tau * v
                wrong = inside + g * v
                m, _, _ = run(1, case=case, duration=tau, gamma=g)
                self.assertEqual(m["Value by Equation (10.2)"], f3(value))
                self.assertEqual(m["Value if discounted as one step"], f3(wrong))
                self.assertEqual(m["Overstatement"], f3(v * (g - g ** tau)))
        self.assertEqual(run(1, case="chapter", duration=3, gamma=0.9)[0]["Value by Equation (10.2)"], "11.990")
        # workbook transfer: continuation contributes 0.25 x 8 = 2, not 0.5 x 8 = 4; total 4
        m, t, _ = run(1, case="transfer", duration=2, gamma=0.5)
        self.assertEqual(m["Value by Equation (10.2)"], "4.000")
        self.assertIn("0.25 x 8 = 2.000", t)
        self.assertIn("0.5 x 8 = 4.000", t)
        self.assertIn("pushed 1 step later", run(1, duration=3, gamma=0.9, case="chapter")[1])
        self.assertIn("pushed 2 steps later", run(1, duration=4, gamma=0.9, case="chapter")[1])
        # prediction text: 10 x (0.9 - 0.9^4) = 2.439
        self.assertEqual(run(1, case="chapter", duration=4, gamma=0.9)[0]["Overstatement"], "2.439")

    def test_d03_time_is_a_maximum_and_cost_is_a_sum(self):
        for a, mode, src in itertools.product([4, 6, 8], ["parallel", "after"], ["same", "changed"]):
            m, text, _ = run(2, audit_minutes=a, mode=mode, source=src)
            chain = 6 + (3 if src == "changed" else 0)
            t = max(chain, a) if mode == "parallel" else chain + a
            cost = 16 + (7 if src == "changed" else 0)
            self.assertEqual(m["Release time"], f"{t} minutes")
            self.assertEqual(m["Total tool cost"], f"{cost} credits")
        self.assertEqual(run(2, audit_minutes=4, mode="parallel", source="same")[0]["Release time"], "6 minutes")
        tie = run(2, audit_minutes=6, mode="parallel", source="same")
        self.assertIn("tie", tie[0]["Longest chain"])
        self.assertIn("tie at 6 minutes", tie[1])
        self.assertEqual(run(2, audit_minutes=8, mode="parallel", source="same")[0]["Longest chain"], "Audit")
        self.assertEqual(run(2, audit_minutes=4, mode="parallel", source="same")[0]["Longest chain"], "Draft, Verify, Publish")
        stale = run(2, audit_minutes=4, mode="parallel", source="changed")
        self.assertEqual(stale[0]["Release time"], "9 minutes")
        self.assertEqual(stale[0]["Total tool cost"], "23 credits")
        self.assertIn("v17", stale[1])
        self.assertIn("max{2 + 3 + 3 + 1, 4} = max{9, 4} = 9", stale[1])
        self.assertIn("4 + 7 + 7 + 2 + 3 = 23", stale[1])

    def test_d04_interruption_and_transfer(self):
        for (case, k), g in itertools.product([("none", 3), ("two", 2), ("one", 1)], [0.9, 0.5]):
            rewards = [-1, -1, 8][:k]
            v = sum(g ** t * r for t, r in enumerate(rewards))
            if k == 3:
                v += g ** 3 * 2
            m, _, _ = run(3, case=case, gamma=g)
            self.assertEqual(m["review-release value"], f3(v))
            self.assertEqual(m["archive value"], "1.000")
            self.assertEqual(m["review-release completed"], "yes" if k == 3 else "no")
            self.assertEqual(m["Higher executed value"], "review-release" if v > 1 else "archive")
        self.assertEqual(run(3, case="none", gamma=0.9)[0]["review-release value"], "6.038")
        self.assertEqual(run(3, case="two", gamma=0.9)[0]["review-release value"], "-1.900")
        self.assertEqual(run(3, case="none", gamma=0.5)[0]["review-release value"], "0.750")
        self.assertEqual(run(3, case="none", gamma=0.5)[0]["Higher executed value"], "archive")
        # workbook transfer: inspect = 0 + 0.5 x 4 + 0.25 x 8 = 4; disabled runs 0 steps and earns 0
        m, t, _ = run(3, case="transfer", gamma=0.5)
        self.assertEqual(m["inspect value"], "4.000")
        self.assertEqual(m["disabled value"], "0.000")
        self.assertEqual(m["Higher executed value"], "inspect")
        self.assertIn("0.25 x 8 = 2.000", t)
        self.assertIn("0 of 1 steps", t)
        m9, _, _ = run(3, case="transfer", gamma=0.9)
        self.assertEqual(m9["inspect value"], f3(0.9 * 4 + 0.81 * 8))

    def test_wording_guards(self):
        demos = ch10.CHAPTER["demos"]
        self.assertIn("without continuation", demos[3]["title"])
        self.assertIn("stipulates V = 0", demos[3]["explanation"])
        self.assertIn("does not bind", demos[3]["symbols"])
        self.assertIn("costs the same", demos[2]["application"])
        self.assertIn("larger gap at durations 2 to 4", demos[1]["explanation"])
        for i in (1, 2, 3):
            self.assertIn("scope_note", demos[i])
            self.assertEqual(demos[i]["scope_note"]["source_section"], "What this does not settle")
        for d in demos[:2] + demos[2:3] + demos[3:]:
            self.assertIn("misconception", d)

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


@unittest.skipUnless(PYTHON.is_file(), "laboratory .venv absent")
class Chapter10BuiltPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp(prefix="reader-ch10-test-")
        r = subprocess.run([str(PYTHON), str(WRAPPER), "--chapters", "10", "--out", cls.tmp], capture_output=True,
                           text=True, timeout=900, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        assert r.returncode == 0, r.stdout + r.stderr
        cls.reader = Path(cls.tmp) / "10-option-duration" / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', cls.page, re.S).group(1))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def test_size_and_state_counts(self):
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [9, 12, 12, 8])
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_optional_panels_present(self):
        self.assertIn("Ask the chapter skill", self.page)
        self.assertIn("What this does not settle", self.page)
        self.assertIn("Common wrong turn", self.page)
        self.assertIn("Your prediction", self.page)
        self.assertIn("Worked steps", self.page)

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed")
        r = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=300)
        self.assertEqual(r.returncode, 0, r.stderr + r.stdout)
        report = json.loads(r.stdout)["reports"][0]
        self.assertEqual(report["states_checked"], 41)


class Chapter10Patch2Tests(unittest.TestCase):
    def test_d02_figure_labels_match_metrics(self):
        fig, metrics, text, _ = ch10.duration_picture(case="chapter", duration=4, gamma=0.5)
        labels = [t.get_text() for ax in fig.axes for t in ax.texts]
        plt.close(fig)
        self.assertEqual(metrics["Continuation discounted by gamma^4"], "0.625")
        self.assertIn("0.625", labels)
        self.assertIn("0.0625", labels)
        self.assertNotIn("0.62", labels)
        self.assertNotIn("0.062", labels)

    def test_d03_pluralisation_and_titles(self):
        for audit in (4, 6, 8):
            for mode in ("parallel", "after"):
                for source in ("same", "changed"):
                    text = run(2, audit_minutes=audit, mode=mode, source=source)[1]
                    self.assertNotIn("1 minutes", text)
        self.assertIn("1 minute of slack", run(2, audit_minutes=8, mode="parallel", source="changed")[1])
        fig, *_ = ch10.totals_picture(audit_minutes=6, mode="parallel", source="same")
        title = fig.axes[0].get_title()
        plt.close(fig)
        self.assertTrue(title.startswith("Release at minute 6 (16 credits)"))
        self.assertNotIn("min: 6 min", title)

    def test_correct_prediction_is_not_always_first(self):
        self.assertNotEqual({d["prediction_answer"] for d in ch10.CHAPTER["demos"]}, {0})


if __name__ == "__main__":
    unittest.main()

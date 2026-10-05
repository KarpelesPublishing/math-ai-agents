"""Chapter 19 laboratory reader: independent hand checks of the built page.

Expected numbers are recomputed here from the chapter's printed means, from
the chapter's three-option cycle, and from weighted sums of the laboratory's
two-by-two matrix, not read back from the module that produced the page. The
reader is built into a temporary directory, so the committed readers folder
is never touched.
"""
from __future__ import annotations

import html
import importlib.util
import json
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
MODULE = LAB / "tools" / "readers" / "chapters" / "ch19.py"
SLUG = "19-cross-play-transfer"


def builder_python():
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


class Chapter19ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.python = builder_python()
        if cls.python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([cls.python, str(WRAPPER), "--chapters", "19", "--out", cls.tmp.name], capture_output=True,
                             text=True, timeout=600)
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls.tmp.name) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    # Raw control values, written here from the design (the page shows labels for text controls).
    RAW = {
        "C19-D01": [["small2", "small3", "small4", "gathering"], ["means", "fix"]],
        "C19-D02": [[2, 4, 6, 12], ["A", "B", "C"]],
        "C19-D03": [["base", "l3", "l5", "l10"], ["loss", "reduction", "step"]],
        "C19-D04": [["two", "three"], ["target", "changed", "tie", "known"]],
    }

    def states(self, demo_id):
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [self.RAW[demo_id][n][i] for n, i in enumerate(idx)], state

    def section_text(self, demo_id):
        """Visible static text of one demonstration (question, explanation, symbols and so on)."""
        match = re.search(rf'<section class="demo" id="{demo_id}".*?</section>', self.page, re.S)
        self.assertIsNotNone(match, demo_id)
        return " ".join(html.unescape(re.sub(r"<[^>]+>", " ", match.group(0))).split())

    @staticmethod
    def m(state):
        return dict(state["metrics"])

    # structure and budgets

    def test_four_demonstrations_all_combinations_render(self):
        self.assertEqual(list(self.demos), ["C19-D01", "C19-D02", "C19-D03", "C19-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 12, 12, 8])
        for d in self.data["demos"]:
            self.assertLessEqual(len(d["states"]), 12)
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    # D1: Equation (19.2) on the chapter's printed means

    def test_d01_losses_by_hand(self):
        means = {"small2": (30.44, 20.03), "small3": (23.06, 9.06), "small4": (20.15, 5.71), "gathering": (147.34, 146.89)}
        expected = {"small2": "0.342", "small3": "0.607", "small4": "0.717", "gathering": "0.003"}
        for (task, view), state in self.states("C19-D01"):
            if view != "means":
                continue
            diag, off = means[task]
            loss = (diag - off) / diag
            m = self.m(state)
            self.assertEqual(m["Diagonal mean"], f"{diag:.2f}")
            self.assertEqual(m["Off-diagonal mean"], f"{off:.2f}")
            shown = m["Loss from Equation (19.2)"]
            self.assertTrue(shown.startswith(f"{loss:.3f}"), (task, shown))
            self.assertTrue(shown.startswith(expected[task]))
            self.assertIn(f"({diag:.2f} - {off:.2f}) / {diag:.2f}", state["interpretation"])
            self.assertIn(f"Gap = {diag:.2f} - {off:.2f} = {diag - off:.2f}.", " ".join(state["steps"]))

    def test_d01_small3_printed_value_is_flagged_not_hidden(self):
        # The chapter prints 0.625 for small3 but its printed means give 14 / 23.06 = 0.607.
        self.assertAlmostEqual(14.0 / 23.06, 0.607, places=3)
        small3 = next(s for (t, v), s in self.states("C19-D01") if t == "small3" and v == "means")
        self.assertEqual(self.m(small3)["Loss from Equation (19.2)"], "0.607 (chapter prints 0.625)")
        self.assertIn("0.625", small3["interpretation"])
        for task in ("small2", "small4", "gathering"):
            s = next(s for (t, v), s in self.states("C19-D01") if t == task and v == "means")
            self.assertNotIn("chapter prints", self.m(s)["Loss from Equation (19.2)"])

    def test_d01_control_task_loss_is_small(self):
        gathering = next(s for (t, v), s in self.states("C19-D01") if t == "gathering" and v == "means")
        self.assertLess(float(self.m(gathering)["Loss from Equation (19.2)"]), 0.01)
        self.assertIn("does not prove", gathering["interpretation"])

    def test_d01_figure_19_1_asymmetry_is_the_printed_pair(self):
        # Chapter: the entry for run four's first party with run one's second party is 27.3, the reverse is 3.7.
        self.assertEqual(f"{27.3 / 3.7:.1f}", "7.4")
        small2 = next(s for (t, v), s in self.states("C19-D01") if t == "small2" and v == "means")
        self.assertIn("27.3 / 3.7 = 7.4", small2["interpretation"])

    def test_d01_fix_view_numbers_by_hand(self):
        # Chapter: losses in percent. small2 34.2 -> 5.5 (full) and 14.7 (highest only); small3 62.5 -> 8.2 and 27.0;
        # small4 71.7 -> highest only 11.8; full is the printed reduction 56.7 subtracted from 71.7 = 15.0.
        want = {"small2": (34.2, 14.7, 5.5), "small3": (62.5, 27.0, 8.2), "small4": (71.7, 11.8, 71.7 - 56.7)}
        for (task, view), state in self.states("C19-D01"):
            if view != "fix" or task == "gathering":
                continue
            base, single, full = want[task]
            m = self.m(state)
            self.assertEqual(m["Loss, independent learners"], f"{base:.1f} percent")
            self.assertEqual(m["Loss, highest-level policy only"], f"{single:.1f} percent")
            self.assertTrue(m["Loss, full mixed strategy"].startswith(f"{full:.1f} percent"))
            self.assertIn(f"{base:.1f} - {full:.1f} = {base - full:.1f}", state["interpretation"])
            self.assertIn(f"{base:.1f} - {single:.1f} = {base - single:.1f}", state["interpretation"])
        # reductions the chapter prints: 28.7, 54.3, 56.7 (full) and 19.5, 36.5, 59.9 (highest only)
        self.assertAlmostEqual(34.2 - 5.5, 28.7)
        self.assertAlmostEqual(62.5 - 8.2, 54.3)
        self.assertAlmostEqual(71.7 - 15.0, 56.7)
        self.assertAlmostEqual(34.2 - 14.7, 19.5)
        self.assertAlmostEqual(71.7 - 11.8, 59.9)
        self.assertAlmostEqual(62.5 - 27.0, 35.5)  # the chapter prints 36.5 and flags the difference
        small3 = next(s for (t, v), s in self.states("C19-D01") if t == "small3" and v == "fix")
        self.assertIn("prints 36.5", small3["interpretation"])
        self.assertIn("35.5", small3["interpretation"])

    def test_d01_fix_small2_tracks_three_numbers_in_different_directions(self):
        small2 = next(s for (t, v), s in self.states("C19-D01") if t == "small2" and v == "fix")
        self.assertAlmostEqual(28.20 - 30.44, -2.24)
        self.assertAlmostEqual(26.63 - 20.03, 6.60)
        self.assertAlmostEqual((28.20 - 26.63) / 28.20, 0.0557, places=4)
        text = small2["interpretation"]
        self.assertIn("28.20 - 30.44 = (-2.24)", text)
        self.assertIn("26.63 - 20.03 = 6.60", text)
        self.assertIn("(28.20 - 26.63) / 28.20 = 0.056", text)
        self.assertIn("5.5 percent", text)

    def test_d01_small4_fix_flags_the_unreconciled_figures(self):
        small4 = next(s for (t, v), s in self.states("C19-D01") if t == "small4" and v == "fix")
        self.assertIn("does not reconcile", small4["interpretation"])
        self.assertTrue(self.m(small4)["Loss, full mixed strategy"].endswith("(derived)"))

    def test_d01_gathering_fix_state_says_there_is_no_fix(self):
        g = next(s for (t, v), s in self.states("C19-D01") if t == "gathering" and v == "fix")
        self.assertEqual(self.m(g)["Fix reported by the chapter"], "none for this task")
        self.assertIn("(147.34 - 146.89) / 147.34 = 0.003", g["interpretation"])

    # D2: the chapter's three-option cycle

    @staticmethod
    def reference_cycle(start, updates):
        # The chapter: party one prefers B against A, C against B, A against C; party two "the same way one step around".
        answer = {"A": "B", "B": "C", "C": "A"}
        beats = {("B", "A"), ("C", "B"), ("A", "C")}

        def pay(mine, theirs):
            return 0 if mine == theirs else (1 if (mine, theirs) in beats else -1)

        one, two = None, start
        trace, p1 = [], []
        for k in range(1, updates + 1):
            if k % 2:
                one = answer[two]
            else:
                two = answer[one]
            trace.append((k, one, two))
            p1.append(pay(one, two))
        return trace, p1

    def test_d02_chapter_trace_closes_after_six_updates(self):
        trace, p1 = self.reference_cycle("A", 6)
        # Chapter: party one B, party two C, party one A, party two B, party one C, party two A.
        self.assertEqual([t[1] if i % 2 == 0 else t[2] for i, t in enumerate(trace)], ["B", "C", "A", "B", "C", "A"])
        self.assertEqual(trace[-1][2], "A")
        self.assertEqual(sum(p1), 0)

    def test_d02_metrics_every_state(self):
        for (updates, start), state in self.states("C19-D02"):
            updates = int(updates)
            trace, p1 = self.reference_cycle(start, updates)
            back = next((k for k, one, two in trace if k % 2 == 0 and two == start), None)
            m = self.m(state)
            self.assertEqual(m["Updates shown"], str(updates))
            self.assertEqual(m["Mean payoff to party one"], f"{sum(p1) / updates:.2f}")
            self.assertEqual(m["Mover's payoff after its own update"], "+1 every time")
            self.assertEqual(m["Mover's average against A, B and C"], "0.00 every time")
            if updates >= 6:
                self.assertEqual(back, 6)
                self.assertEqual(m["Party two back at its start"], "after 6 updates")
            else:
                self.assertIsNone(back)
                self.assertTrue(m["Party two back at its start"].startswith("not yet"))
            first = trace[0][1]
            self.assertIn(f"so Equation (19.4) picks {first}", state["interpretation"])
            self.assertIn("(1 + 0 + (-1)) / 3 = 0.00", state["interpretation"])

    def test_d02_steps_follow_the_trace(self):
        for (updates, start), state in self.states("C19-D02"):
            updates = int(updates)
            trace, _ = self.reference_cycle(start, updates)
            steps = state["steps"]
            shown = min(updates, 6)
            self.assertEqual(len(steps), shown + (1 if updates > 6 else 0))
            for k, one, two in trace[:shown]:
                mover_choice = one if k % 2 else two
                self.assertTrue(steps[k - 1].startswith(f"Update {k}: "), steps[k - 1])
                self.assertTrue(steps[k - 1].endswith(f"plays {mover_choice}."), (steps[k - 1], mover_choice))
            if updates > 6:
                self.assertIn("period 6", steps[-1])

    def test_d02_mover_always_gains_one_and_averages_zero(self):
        beats = {("B", "A"), ("C", "B"), ("A", "C")}

        def pay(mine, theirs):
            return 0 if mine == theirs else (1 if (mine, theirs) in beats else -1)

        for start in "ABC":
            trace, _ = self.reference_cycle(start, 12)
            for k, one, two in trace:
                mine, theirs = (one, two) if k % 2 else (two, one)
                self.assertIn((mine, theirs), beats)
                self.assertEqual(sum(pay(mine, o) for o in "ABC"), 0)

    def test_d02_dependence_sentence_names_the_option_actually_played(self):
        beats = {("B", "A"), ("C", "B"), ("A", "C")}

        def pay(mine, theirs):
            return 0 if mine == theirs else (1 if (mine, theirs) in beats else -1)

        show = lambda v: "1" if v == 1 else ("0" if v == 0 else "(-1)")
        for (updates, start), state in self.states("C19-D02"):
            trace, _ = self.reference_cycle(start, int(updates))
            option, reply = trace[0][1], trace[1][2]
            expected = f"option {option} pays {show(pay(option, start))} against {start} but {show(pay(option, reply))} against {reply}"
            self.assertIn(expected, state["interpretation"], (updates, start))
        by = {(u, s): st for (u, s), st in self.states("C19-D02")}
        self.assertIn("option A pays 1 against C but (-1) against B", by[(6, "C")]["interpretation"])
        self.assertIn("option C pays 1 against B but (-1) against A", by[(6, "B")]["interpretation"])

    def test_d02_static_text_does_not_misstate_the_option_order(self):
        self.assertNotIn("A, B, C, A, B, C", self.section_text("C19-D02"))
        self.assertIn("repeats every six updates", self.section_text("C19-D02"))

    def test_d01_does_not_claim_the_chapter_draws_a_diamond(self):
        small3 = next(s for (t, v), s in self.states("C19-D01") if t == "small3" and v == "means")
        self.assertNotIn("as the chapter does", small3["interpretation"])
        self.assertIn("the chapter flags the same difference in its text", small3["interpretation"])

    def test_symbols_expand_jpc_and_define_u(self):
        for demo_id in ("C19-D01", "C19-D03", "C19-D04"):
            self.assertIn("joint policy correlation", self.section_text(demo_id), demo_id)
        self.assertIn("joint return", self.section_text("C19-D01"))
        self.assertIn("success indicator", self.section_text("C19-D04"))

    # D3: return on depth

    def test_d03_depth_numbers_by_hand(self):
        loss = {"base": 71.7, "l3": 24.6, "l5": 15.6, "l10": 71.7 - 56.7}
        order = ["base", "l3", "l5", "l10"]
        # Chapter: reductions 47.1 (level three, printed 44) and 56.1 (level five), 56.7 (level ten); last doubling buys under one point.
        self.assertAlmostEqual(71.7 - 24.6, 47.1)
        self.assertAlmostEqual(71.7 - 15.6, 56.1)
        self.assertLess(56.7 - 56.1, 1.0)
        for (depth, view), state in self.states("C19-D03"):
            i = order.index(depth)
            red = 71.7 - loss[depth]
            m = self.m(state)
            self.assertTrue(m["Loss"].startswith(f"{loss[depth]:.1f} percent"))
            if i == 0:
                self.assertTrue(m["Points removed from the baseline"].startswith("0.0"))
                self.assertTrue(m["Extra points from the last step"].startswith("none"))
            else:
                prev = 71.7 - loss[order[i - 1]]
                self.assertEqual(m["Points removed from the baseline"], f"{red:.1f}")
                self.assertEqual(m["Extra points from the last step"], f"{red - prev:.1f}")
                self.assertIn(f"71.7 - {loss[depth]:.1f} = {red:.1f}", state["interpretation"])
                self.assertIn(f"{red:.1f} - {prev:.1f} = {red - prev:.1f}", state["interpretation"])
            self.assertEqual(m["Loss"].endswith("(derived)"), depth == "l10")

    def test_d03_level_three_flags_printed_44(self):
        for (depth, view), state in self.states("C19-D03"):
            if depth == "l3":
                self.assertIn("prints 44 points", state["interpretation"])
                self.assertIn("71.7 - 24.6 = 47.1", state["interpretation"])
            else:
                self.assertNotIn("prints 44 points", state["interpretation"])

    def test_d03_last_doubling_buys_under_one_point(self):
        l10 = next(s for (d, v), s in self.states("C19-D03") if d == "l10")
        self.assertEqual(self.m(l10)["Extra points from the last step"], "0.6")
        self.assertIn("under one point", l10["interpretation"])

    # D4: partner mixtures with the laboratory's matrices

    MATRIX = {"two": [[0.95, 0.2], [0.4, 0.9]], "three": [[1, 0, 0], [0.6, 0.6, 0.6], [0, 0, 1]]}
    MIX = {
        "two": {"target": [0.5, 0.5], "changed": [0.9, 0.1], "tie": [0.56, 0.44], "known": [1, 0]},
        "three": {"target": [0.2, 0.6, 0.2], "changed": [0.5, 0, 0.5], "tie": [0.6, 0, 0.4], "known": [1, 0, 0]},
    }

    def test_d04_weighted_values_by_hand(self):
        for (matrix, mix), state in self.states("C19-D04"):
            M, w = self.MATRIX[matrix], self.MIX[matrix][mix]
            k = len(M)
            values = [sum(w[j] * M[i][j] for j in range(k)) for i in range(k)]
            m = self.m(state)
            for i in range(k):
                self.assertEqual(m[f"Policy {i} against the mix"], f"{values[i]:.3f}", (matrix, mix, i))
            best = max(values)
            winners = [i for i in range(k) if abs(values[i] - best) < 1e-9]
            expected = " and ".join(f"Policy {i}" for i in winners) + (" tie" if len(winners) > 1 else "")
            self.assertEqual(m["Ranks first"], expected, (matrix, mix))
            diag = [M[i][i] for i in range(k)]
            dbest = max(diag)
            dwin = [i for i in range(k) if abs(diag[i] - dbest) < 1e-9]
            self.assertEqual(m["Diagonal alone names"], " and ".join(f"Policy {i}" for i in dwin) + (" (tie)" if len(dwin) > 1 else ""))
            dmean = sum(diag) / k
            off = (sum(map(sum, M)) - sum(diag)) / (k * (k - 1))
            self.assertEqual(m["Loss from Equation (19.2)"], f"{(dmean - off) / dmean:.3f}")

    def test_d04_the_chapter_laboratory_cases(self):
        by = {(a, b): s for (a, b), s in self.states("C19-D04")}
        # default: equal weights 0.575 and 0.65, policy 1 wins; changed: 0.875 and 0.45, policy 0 wins
        d, c = self.m(by[("two", "target")]), self.m(by[("two", "changed")])
        self.assertEqual((d["Policy 0 against the mix"], d["Policy 1 against the mix"], d["Ranks first"]), ("0.575", "0.650", "Policy 1"))
        self.assertEqual((c["Policy 0 against the mix"], c["Policy 1 against the mix"], c["Ranks first"]), ("0.875", "0.450", "Policy 0"))
        # tie at p = 0.7 / 1.25 = 0.56
        self.assertAlmostEqual(0.7 / 1.25, 0.56)
        self.assertEqual(self.m(by[("two", "tie")])["Ranks first"], "Policy 0 and Policy 1 tie")
        self.assertIn("p = 0.7 / 1.25 = 0.56", by[("two", "tie")]["interpretation"])
        # transfer: generalist 0.6 against specialists 0.2 and 0.2; supervisor mix 0.5 each, still below 0.6
        t, s = self.m(by[("three", "target")]), self.m(by[("three", "changed")])
        self.assertEqual((t["Policy 0 against the mix"], t["Policy 1 against the mix"], t["Policy 2 against the mix"], t["Ranks first"]),
                         ("0.200", "0.600", "0.200", "Policy 1"))
        self.assertEqual((s["Policy 0 against the mix"], s["Policy 1 against the mix"], s["Policy 2 against the mix"], s["Ranks first"]),
                         ("0.500", "0.600", "0.500", "Policy 1"))
        self.assertEqual(self.m(by[("three", "tie")])["Ranks first"], "Policy 0 and Policy 1 tie")
        self.assertEqual(self.m(by[("three", "known")])["Ranks first"], "Policy 0")

    def test_d04_asymmetry_is_named_from_the_matrix(self):
        by = {(a, b): s for (a, b), s in self.states("C19-D04")}
        self.assertIn("cell (0, 1) is 0.20 but cell (1, 0) is 0.40", by[("two", "target")]["interpretation"])
        self.assertIn("cell (0, 1) is 0.00 but cell (1, 0) is 0.60", by[("three", "target")]["interpretation"])

    def test_d04_steps_list_one_weighted_sum_per_policy(self):
        for (matrix, mix), state in self.states("C19-D04"):
            k = len(self.MATRIX[matrix])
            self.assertEqual(len(state["steps"]), k + 2)

    def test_laboratory_function_agrees_with_the_chapter_formula(self):
        sys.path.insert(0, str(LAB / "src"))
        try:
            from math_ai_agents.chapters.ch19 import evaluate
        finally:
            sys.path.pop(0)
        out = evaluate({"matrix": [[0.95, 0.2], [0.4, 0.9]], "partner_weights": [0.5, 0.5], "supervisor_weights": [0.9, 0.1]})
        self.assertAlmostEqual(out["metrics"]["joint_policy_correlation_loss"], (0.925 - 0.3) / 0.925)
        one = evaluate({"matrix": [[0.9]], "partner_weights": [1.0], "supervisor_weights": [1.0]})
        self.assertIsNone(one["metrics"]["joint_policy_correlation_loss"])  # one policy: no off-diagonal, statistic undefined
        transfer = evaluate({"matrix": [[1, 0, 0], [0.6, 0.6, 0.6], [0, 0, 1]], "partner_weights": [0.2, 0.6, 0.2], "supervisor_weights": [0.5, 0, 0.5]})
        self.assertEqual(transfer["metrics"]["selected_policy"], 1)

    # optional reader features

    def test_optional_features_are_present(self):
        self.assertIn("Ask the chapter skill", self.page)
        for demo_id in self.demos:
            text = self.section_text(demo_id)
            self.assertIn("Common wrong turn", text, demo_id)
            self.assertIn("What this does not settle", text, demo_id)
            self.assertIn("Your prediction", text, demo_id)
        for demo_id in self.demos:
            for _, state in self.states(demo_id):
                self.assertTrue(2 <= len(state["steps"]) <= 8)

    def test_scope_notes_quote_the_chapter(self):
        chapter = (LAB.parent / "Manuscript/part-v/19-when-another-mind-becomes-part-of-the-world.md").read_text(encoding="utf-8")
        flat = " ".join(chapter.split())
        for phrase in ("single conference paper reporting its authors' own method on gridworld tasks",
                       "instrument requires multiple independent training runs, which many deployments cannot afford",
                       "Best-response cycling is one distinct difficulty with adapting counterparties"):
            self.assertIn(phrase, flat)

    # equations, text rules, links, harness

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 19)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")

        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 7)  # D1: two, D2: two, D3: one, D4: two
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter", "scipy"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))
        source = MODULE.read_text(encoding="utf-8")
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, source)

    def test_links_and_accessibility(self):
        for href in ("../../notebooks/19-cross-play-transfer.ipynb", "../../skills/maa-19-cross-play-transfer/SKILL.md"):
            self.assertIn(f'href="{href}"', self.page)
            self.assertTrue((LAB / href.replace("../../", "")).exists(), href)
        self.assertIn('<a class="skip" href="#main">', self.page)
        self.assertGreaterEqual(self.page.count('aria-live="polite"'), 4)

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"]), (40, 4))
        self.assertEqual(report["ask_skill"], 1)


    def test_patch2_wording_fixes(self):
        gath = " ".join(self.demos["C19-D01"]["states"][k]["interpretation"] for k in self.demos["C19-D01"]["states"] if "fix" in k or True)
        self.assertNotIn("so a fix has little to repair", gath)
        self.assertIn("does not report a fix for this task", gath)
        text = self.section_text("C19-D02") + " " + " ".join(s["interpretation"] for s in self.demos["C19-D02"]["states"].values())
        self.assertIn("uniform mix of the three options", text)
        self.assertNotIn("fixed evaluation set of all three options", text)
        self.assertIn("Values the chapter prints", self.section_text("C19-D01"))
        self.assertNotIn("Constructed example: the diagonal and off-diagonal means", self.section_text("C19-D01"))
        for d in ("C19-D03",):
            alts = " ".join(s.get("alt", "") for s in self.demos[d]["states"].values())
            self.assertIn("a derived 15.0", alts)
        fb = self.demos["C19-D04"]["prediction"]["feedback"] if "feedback" in self.demos["C19-D04"].get("prediction", {}) else None
        page = self.page
        self.assertIn("The diagonal alone does not give the ranking", html.unescape(page))
        self.assertIn("Doubling the depth from level five to level ten", html.unescape(page))


if __name__ == "__main__":
    unittest.main()

"""Chapter 17 laboratory reader: independent hand checks of the built page.

The reader is built into a private temporary directory (never into readers/),
then every headline number is recomputed here from the chapter's own
arithmetic with exact fractions, not read back from the module that made it.
"""
from __future__ import annotations

import hashlib
import html
import importlib.util
import json
import os
from fractions import Fraction as F
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
SLUG = "17-effect-and-retry"


def builder_python():
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers.builder_python()


def build(out):
    python = builder_python()
    if python is None:
        return None
    run = subprocess.run([python, str(WRAPPER), "--chapters", "17", "--out", out], capture_output=True, text=True,
                         timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    assert run.returncode == 0, run.stdout + run.stderr
    return Path(out) / SLUG / "reader.html"


def payload(text):
    return json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))


def num(text):
    try:
        return float(text)
    except ValueError:
        return text


class Chapter17ReaderTests(unittest.TestCase):
    def test_d01_authored_steps_compute_each_operation(self):
        import importlib.util
        import sys
        import matplotlib
        matplotlib.use("Agg")
        sys.path.insert(0, str(LAB / "tools/readers/engine"))
        spec = importlib.util.spec_from_file_location("ch17_authored_steps", LAB / "tools/readers/chapters/ch17.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        import matplotlib.pyplot as plt
        for kind in ("read", "put", "delete", "charge"):
            for key in ("none", "stored", "lost"):
                figure, metrics, _, presentation = module.repeat_picture(kind, key)
                try:
                    self.assertIsInstance(presentation, dict)
                    self.assertEqual(len(presentation["steps"]), 6)
                    final = 100 if kind == "read" else 150 if kind == "put" or kind == "charge" and key == "stored" else 0 if kind == "delete" else 250
                    single = 100 if kind == "read" else 0 if kind == "delete" else 150
                    self.assertIn(f"{final} - {single} = {final-single}", presentation["steps"][3])
                    self.assertEqual(metrics["Equation (17.1)"], "holds" if final == single else "fails")
                finally:
                    plt.close(figure)

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.reader = build(cls._tmp.name)
        if cls.reader is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    VALUES = {
        "C17-D01": [["read", "put", "delete", "charge"], ["none", "stored", "lost"]],
        "C17-D02": [[0.3, 0.99], [0.5, 0.9], [0, 10, 40]],
        "C17-D03": [[1, 2, 3], ["works", "unavailable", "partial", "lost"]],
        "C17-D04": [["merge", "delete", "notify", "audit"], ["none", "absent", "expired"]],
    }

    def states(self, demo_id):
        """Yield (control values as written in the reader's definition, state); the page stores labels, so map by index."""
        for key, state in self.demos[demo_id]["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [vals[i] for vals, i in zip(self.VALUES[demo_id], idx)], state

    def test_structure_and_budgets(self):
        self.assertEqual(list(self.demos), ["C17-D01", "C17-D02", "C17-D03", "C17-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 12, 12])
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_optional_fields_present(self):
        self.assertIn("Ask the chapter skill", self.page)
        self.assertEqual(self.page.count("Common wrong turn:"), 4)
        self.assertIn('Chapter 17 source: "What this does not settle".', html.unescape(self.page))
        for d in self.data["demos"]:
            self.assertTrue(d["predict"]["correct"] and d["predict"]["incorrect"])
        for demo_id in ("C17-D02", "C17-D03", "C17-D04"):
            for state in self.demos[demo_id]["states"].values():
                self.assertTrue(2 <= len(state["steps"]) <= 8)
        # the stepper is the stage control of Demonstration 3
        self.assertIn("Step", self.page)

    def test_d01_repeat_by_hand(self):
        seen = 0
        for (kind, key), state in self.states("C17-D01"):
            n = 3
            m = dict(state["metrics"])
            if kind == "read":
                one, many = 100, 100
            elif kind == "put":
                one, many = 150, 150
            elif kind == "delete":
                one = many = None
            else:
                one = 150
                many = {"none": 100 + 50 * n, "stored": 100 + 50, "lost": 100 + 50 * n}[key]
            if kind == "delete":
                self.assertEqual(m["Record after one request"], "absent")
                self.assertEqual(m["Equation (17.1)"], "holds")
            else:
                self.assertEqual(m["Record after one request"], f"{one}")
                self.assertEqual(m[f"Record after {n} requests"], f"{many}")
                self.assertEqual(m["Equation (17.1)"], "holds" if one == many else "fails")
            self.assertEqual(m["Log lines written"], str(n))
            retry = m["Automatic retry after a lost reply"]
            self.assertEqual(retry.startswith("allowed"), m["Equation (17.1)"] == "holds")
            seen += 1
        self.assertEqual(seen, 12)
        # classes of Figure 17.2: safe methods are idempotent too; a charge is neither unless a key covers it
        cls = {tuple(v): dict(s["metrics"])["Class (Figure 17.2)"] for v, s in self.states("C17-D01")}
        self.assertEqual(cls[("read", "none")], "safe (so also idempotent)")
        self.assertEqual(cls[("charge", "none")], "neither safe nor idempotent")
        self.assertTrue(cls[("charge", "stored")].startswith("idempotent by the key"))
        self.assertTrue(cls[("charge", "lost")].startswith("key not recognized"))
        # the book's point: a charge with no key repeated 3 times ends at 250; the notebook's changed trace (key stored) ends at 150
        charge3 = next(s for v, s in self.states("C17-D01") if v == ["charge", "none"])
        self.assertEqual(dict(charge3["metrics"])["Record after 3 requests"], "250")
        self.assertIn("100 + 3 x 50 = 250", charge3["interpretation"])
        keyed = next(s for v, s in self.states("C17-D01") if v == ["charge", "stored"])
        self.assertIn("100 + 1 x 50 = 150", keyed["interpretation"])
        lost = next(s for v, s in self.states("C17-D01") if v == ["charge", "lost"])
        self.assertIn("100 + 3 x 50 = 250", lost["interpretation"])
        self.assertIn("The service is also constructed to log every request and to reply as shown.", self.page)

    def test_d02_chain_from_silence_to_decision_by_hand(self):
        cmiss, read = F(10), F(1)
        for (prior, la, cdup), state in self.states("C17-D02"):
            p, a, b, c = F(str(prior)), F(str(la)), F(1, 2), F(cdup)
            beta = a * p / (a * p + b * (1 - p))
            retry = beta * c
            decline = (1 - beta) * cmiss
            diff = decline - retry
            thr = cmiss / (cmiss + c)
            best_blind = min(retry, decline)
            m = dict(state["metrics"])
            self.assertEqual(m["Belief before silence (prior)"], f"{float(p):.3f}")
            self.assertEqual(m["Belief after silence (beta)"], f"{float(beta):.3f}")
            self.assertEqual(m["Expected cost of retrying"], f"{float(retry):.2f}")
            self.assertEqual(m["Expected cost of declining"], f"{float(decline):.2f}")
            self.assertEqual(m["Cost of reading first"], "1.00")
            self.assertEqual(m["EU(retry) minus EU(decline)"], f"{float(diff):.2f}")
            self.assertEqual(m["Retry threshold"], f"{float(thr):.2f}")
            self.assertEqual(m["Gross value of a perfect read"], f"{float(best_blind):.2f}")
            self.assertEqual(m["Net value of the read"], f"{float(best_blind - read):.2f}")
            lowest = min(retry, decline, read)
            names = [n for n, v in (("Retry", retry), ("Decline", decline), ("Read first", read)) if v == lowest]
            self.assertEqual(m["Lowest expected cost"], " and ".join(names))
            # the sign of the difference agrees with comparing beta to the threshold
            self.assertEqual(diff > 0, beta < thr)
        by = {tuple(v): dict(s["metrics"]) for v, s in self.states("C17-D02")}
        # workbench IV.1 and IV.3: belief 0.30 (equal likelihoods), duplicate 40: retry 12, decline 7, difference -5, threshold 0.20,
        # a perfect read costing 1 has gross value 7 and net value 6
        iv = by[(0.3, 0.5, 40)]
        self.assertEqual((iv["Expected cost of retrying"], iv["Expected cost of declining"], iv["EU(retry) minus EU(decline)"],
                          iv["Retry threshold"], iv["Gross value of a perfect read"], iv["Net value of the read"],
                          iv["Lowest expected cost"]), ("12.00", "7.00", "-5.00", "0.20", "7.00", "6.00", "Read first"))
        self.assertAlmostEqual(0.30 * 40, 12)
        self.assertAlmostEqual(0.70 * 10, 7)
        # the repeatable interface (duplicate cost 0): retry is free, the read is worth nothing, buying it loses 1
        free = by[(0.3, 0.5, 0)]
        self.assertEqual((free["Expected cost of retrying"], free["Gross value of a perfect read"], free["Net value of the read"],
                          free["Retry threshold"], free["Lowest expected cost"]), ("0.00", "0.00", "-1.00", "1.00", "Retry"))
        # the chapter's 0.99 baseline: equal likelihoods leave the belief at 0.99
        base = next(s for v, s in self.states("C17-D02") if v == [0.99, 0.5, 40])
        self.assertEqual(dict(base["metrics"])["Belief after silence (beta)"], "0.990")
        self.assertIn("cancel", base["interpretation"])
        # a balanced duplicate cost puts the threshold at one half; a belief 0.435 is below it, so retry beats decline
        bal = next(s for v, s in self.states("C17-D02") if v == [0.3, 0.9, 10])
        self.assertEqual(dict(bal["metrics"])["Retry threshold"], "0.50")
        self.assertEqual(dict(bal["metrics"])["Belief after silence (beta)"], "0.435")
        # the check question: prior 0.2, silence 0.9 and 0.5: belief 0.310; retry 3.10 against decline 6.90
        self.assertAlmostEqual(float(F(9, 10) * F(1, 5) / (F(9, 10) * F(1, 5) + F(1, 2) * F(4, 5))), 0.310, places=3)
        self.assertIn("the empty-set symbol stands for silence", self.page)

    def test_d03_recovery_sequence_by_hand(self):
        for (stage, outcome), state in self.states("C17-D03"):
            m = dict(state["metrics"])
            # coordinates verified restored: only at stage 3, and only those a verified undo covers
            verified = 0
            if stage == 3:
                verified = {"works": 4, "unavailable": 0, "partial": 1, "lost": 0}[outcome]
            self.assertEqual(m["Coordinates verified restored"], f"{verified} of 4", (stage, outcome))
            restored = stage == 3 and verified == 4
            self.assertEqual(m["Restored(T, x)"], "true" if restored else "false")
            self.assertEqual(m["Route 3 of Equation (17.4)"].startswith("holds"), restored)
            # the lab ledger of the notebook's transfer trace: one effect, confirmed
            self.assertEqual(m["Charge entries on the ledger (at the stage 1 read)"], "1")
            parts = " + ".join(["1" if (stage == 3 and ((outcome == "works") or (outcome == "partial" and i == 0))) else "0" for i in range(4)])
            self.assertIn(f"Verified restored = {parts} = {verified} of 4", state["interpretation"])
        # only the verified, complete undo restores; partial restores 1 of 4 (the money), lost and unavailable restore none
        ok = [v for v, s in self.states("C17-D03") if dict(s["metrics"])["Restored(T, x)"] == "true"]
        self.assertEqual(ok, [[3, "works"]])
        # the chapter's own examples: a refund returns the money and does not retract the email, webhook or partner entry
        for phrase in ("refund, confirmation email, downstream webhook and partner ledger entry",):
            self.assertIn(phrase, self.page)
        partial = next(s for v, s in self.states("C17-D03") if v == [3, "partial"])
        self.assertIn("1 + 0 + 0 + 0 = 1 of 4", partial["interpretation"])
        # a lab-computed read shows the charge landed and was confirmed: stop repeating
        stage1 = next(s for v, s in self.states("C17-D03") if v[0] == 1)
        self.assertIn("applied and complete", stage1["interpretation"])
        self.assertIn("Do not send another charge", stage1["interpretation"])

    def test_g6_02_lost_undo_does_not_contradict_the_reliable_read(self):
        text = html.unescape(self.page)
        self.assertNotIn("Verification cannot tell whether the undo applied", text)
        self.assertNotIn("Unknown: the undo call was lost", text)
        lost3 = next(s for v, s in self.states("C17-D03") if v == [3, "lost"])
        self.assertIn("No verifying read has been made", lost3["interpretation"])
        self.assertIn("no verifying read yet", text)
        self.assertTrue(any("No verifying read has been made" in step for step in lost3["steps"]))
        self.assertIn("Verification is taken to be a reliable read; in the lost-undo outcome no verifying read has been made", text)
        self.assertEqual(dict(lost3["metrics"])["Restored(T, x)"], "false")

    def test_g6_12_idempotent_retry_metric_names_authority_and_contract(self):
        for v, s in self.states("C17-D01"):
            retry = dict(s["metrics"])["Automatic retry after a lost reply"]
            if retry.startswith("allowed: the intended effect"):
                self.assertIn("subject to current authority and the service contract", retry)

    def test_g6_13_hand_steps_use_four_decimal_belief(self):
        s = next(s for v, s in self.states("C17-D02") if v == [0.3, 0.9, 40])
        beta = 0.27 / 0.62
        self.assertIn(f"{beta:.4f} x 40 = {beta * 40:.2f}", " ".join(s["steps"]))
        self.assertIn(f"0.4355 x 40 = 17.42", " ".join(s["steps"]))
        for v, st in self.states("C17-D02"):
            self.assertNotIn("0.994 x 40", " ".join(st["steps"]))

    def test_g6_14_lowest_option_has_a_marker_and_caption(self):
        source = (LAB / "tools" / "readers" / "chapters" / "ch17.py").read_text(encoding="utf-8")
        self.assertIn("teal bar or teal marker: lowest expected cost", source)
        self.assertNotIn('"Action (teal: lowest expected cost)"', source)
        self.assertIn('marker="v"', source)

    def test_g6_15_title_and_ledger_label(self):
        d = self.demos["C17-D03"]
        self.assertEqual(d["title"], "Recovery before a repeat: how an undo can fail")
        self.assertNotIn("the four ways an undo fails", d["title"])

    def test_g6_17_assumptions_name_the_laboratory_frame(self):
        self.assertIn("this demonstration sets the request cost to 0", html.unescape(self.page))

    def test_d03_lab_ledger_for_transfer_trace(self):
        import sys
        sys.path.insert(0, str(LAB / "src"))
        from math_ai_agents.chapters.ch17 import evaluate
        out = evaluate({"idempotent": False, "events": [
            {"kind": "request", "key": "send-2", "payload": "packet-B", "effect": True, "ack": False},
            {"kind": "verify", "observed_effect": True}], "verify_cost": 0.5, "retry_cost": 0.1,
            "effect_probability": 0.6, "duplicate_cost": 4})["metrics"]
        self.assertEqual((out["effects"], out["confirmed"], out["preferred_next_step"]), (1, True, "stop"))
        # blind retry at the unresolved point costs 0.1 + 0.6 x 4 = 2.5, against 0.5 to verify (use-cases.md)
        self.assertAlmostEqual(0.1 + 0.6 * 4, 2.5)

    def test_d04_gate_truth_table_on_the_plan(self):
        idem = {"merge": True, "delete": True, "notify": False, "audit": False}
        for (step, evidence), state in self.states("C17-D04"):
            routes = [idem[step], evidence == "absent", False]
            ready = evidence != "expired"
            member = ready and any(routes)
            m = dict(state["metrics"])
            self.assertEqual(m["Membership"], "in Rep(x)" if member else "not in Rep(x)", (step, evidence))
            self.assertEqual(m["Routes that hold"], f"{sum(routes)} of 3")
            self.assertEqual(m["Ready"], "true" if ready else "false")
            held = sum(routes)
            self.assertIn(f"Routes held = {int(routes[0])} + {int(routes[1])} + 0 = {held}", state["interpretation"])
            self.assertIn(f"Ready x routes held = {int(ready)} x {held} = {int(ready) * held}", state["interpretation"])
        by = {tuple(v): dict(s["metrics"])["Membership"] for v, s in self.states("C17-D04")}
        # with no extra evidence the chapter's idempotent steps pass and the notification and audit append do not
        self.assertEqual([by[(s, "none")] for s in ("merge", "delete", "notify", "audit")],
                         ["in Rep(x)", "in Rep(x)", "not in Rep(x)", "not in Rep(x)"])
        # proof of terminal non-application makes every step eligible; expired authority removes every step
        self.assertTrue(all(by[(s, "absent")] == "in Rep(x)" for s in ("merge", "delete", "notify", "audit")))
        self.assertTrue(all(by[(s, "expired")] == "not in Rep(x)" for s in ("merge", "delete", "notify", "audit")))
        notify = next(s for v, s in self.states("C17-D04") if v == ["notify", "none"])
        self.assertIn("A second notification may send a second email", notify["interpretation"])

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 17)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\(?:[,;:!]|quad|qquad)", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".,;")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 5)
        for tex in alts:
            self.assertIn(norm(html.unescape(tex)), allowed)

    def test_links_and_offline(self):
        self.assertIn('href="../../notebooks/17-effect-and-retry.ipynb"', self.page)
        self.assertIn('href="../../skills/maa-17-effect-and-retry/SKILL.md"', self.page)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_page_text_rules(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for state in (s for d in self.data["demos"] for s in d["states"].values()):
            text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"])
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed; the DOM harness needs it")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (48, 4, 9))
        self.assertEqual((report["ask_skill"], report["predictions_checked"] > 0, report["steps_checked"] > 0, report["panels_checked"] > 0), (1, True, True, True))
        self.assertGreater(report["stepper_moves"], 0)

    def test_build_is_reproducible(self):
        with tempfile.TemporaryDirectory() as out:
            again = build(out)
            self.assertEqual(hashlib.sha256(again.read_bytes()).hexdigest(), hashlib.sha256(self.reader.read_bytes()).hexdigest())


if __name__ == "__main__":
    unittest.main()

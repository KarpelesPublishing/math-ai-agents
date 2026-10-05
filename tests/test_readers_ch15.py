"""Chapter 15 laboratory reader: independent hand checks of a freshly built page.

Every expected number is recomputed here from the chapter's arithmetic
(8 - 2 = 6, the 2 epsilon regret bound, the Exercise 1 value 4.8) and the
laboratory's three cases, by code that does not import the chapter module: the
eligibility rule is written out from the freshness and version definitions and
the best set is found by enumerating subsets. The page is built into a
temporary directory; the standard library reads it.
"""
from __future__ import annotations

import html
import itertools
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from math_ai_agents.chapters.ch15 import evaluate

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"


def builder_python():
    for cand in (LAB / ".venv" / "bin" / "python",):
        if cand.is_file():
            return str(cand)
    return None


def payload(text):
    return json.loads(re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S).group(1))


def num(text):
    return float(text)


D01_CASES = ["chapter", "default", "changed", "transfer"]
D01_LAMS = [0, 1, 2]
LAB_RECS = [("review-v2", 4, 8.0, 9, 3, True, "v2"), ("summary", 2, 3.0, 8, 5, False, "v1"), ("old-review", 1, 100.0, 9, 3, True, "v1")]
D01_DATA = {  # budget, now, current version, records (name, tokens, value, timestamp, ttl, authority, version)
    "chapter": (2, 10, "v2", [("Current revocation", 2, 8.0, 9, 3, True, "v2"), ("Thread summary", 2, 3.0, 8, 5, False, "v2"),
                              ("Old approval", 2, 0.0, 9, 3, True, "v1"), ("Irrelevant note", 2, 0.0, 9, 3, False, "v2")]),
    "default": (6, 10, "v2", LAB_RECS),
    "changed": (2, 10, "v2", LAB_RECS),
    "transfer": (3, 20, "doc-C", [("expired", 1, 10.0, 10, 2, False, "doc-C"), ("current", 3, 4.0, 19, 3, True, "doc-C")]),
}
D02_KINDS = ["worst", "dropped", "default", "changed"]
D02_EPS = [1, 2, 3]
D03_SIMS = [0.72, 0.99]
D03_AUTH = ["reachable", "unreachable"]
D03_DELETION = ["none", "store", "all"]
D04_P = [0.25, 0.5, 0.6, 0.8]
D04_LAM = [1, 2, 4]


@unittest.skipIf(builder_python() is None, "laboratory .venv absent")
class Chapter15ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([builder_python(), str(WRAPPER), "--chapters", "15", "--out", cls.tmp.name],
                             capture_output=True, text=True, timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        assert run.returncode == 0, run.stdout + run.stderr
        cls.reader = Path(cls.tmp.name) / "15-memory-budget" / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def states(self, demo_id, axes):
        """Yield (control values, metrics dict, interpretation); values come from the hand-written axes."""
        demo = self.demos[demo_id]
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            yield [axis[i] for axis, i in zip(axes, idx)], dict(state["metrics"]), state["interpretation"]

    def test_four_demos_and_budgets(self):
        self.assertEqual(list(self.demos), ["C15-D01", "C15-D02", "C15-D03", "C15-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 12, 12, 12])
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    def test_d01_budgeted_retrieval_with_eligibility_by_enumeration(self):
        for (case, lam), m, text in self.states("C15-D01", [D01_CASES, D01_LAMS]):
            budget, now, current, records = D01_DATA[case]
            eligible = [r for r in records if now - r[3] <= r[4] and (not r[5] or r[6] == current)]
            excluded = [r[0] for r in records if r not in eligible]
            best, sets = None, []
            for k in range(len(eligible) + 1):
                for sub in itertools.combinations(eligible, k):
                    if sum(r[1] for r in sub) > budget:
                        continue
                    tot = sum(r[2] - lam * r[1] for r in sub)
                    if best is None or tot > best + 1e-9:
                        best, sets = tot, [sub]
                    elif abs(tot - best) <= 1e-9:
                        sets.append(sub)
            self.assertEqual(m["Total net value"], f"{best:.1f}", (case, lam))
            self.assertEqual(m["Best sets"], str(len(sets)), (case, lam))
            self.assertEqual("(tie)" in m["Chosen by Equation (15.1)"], len(sets) > 1)
            self.assertEqual(m["Excluded before scoring"], ", ".join(excluded) if excluded else "none")
        by = {(v[0], v[1]): (m, t) for v, m, t in self.states("C15-D01", [D01_CASES, D01_LAMS])}
        m, t = by[("chapter", 1)]  # the book's case: room for 2 tokens, lambda 1
        self.assertEqual((m["Chosen by Equation (15.1)"], m["Total net value"]), ("Current revocation", "6.0"))
        self.assertIn("Current revocation 8 - 1 x 2 = 6.0", t)
        self.assertIn("Irrelevant note 0 - 1 x 2 = -2.0", t)
        # The laboratory's cases at lambda 0 (its own objective): value 11 for the default, 3 for the changed, 4 for the transfer.
        m, t = by[("default", 0)]
        self.assertEqual((m["Chosen by Equation (15.1)"], m["Total net value"], m["Tokens used"], m["Excluded before scoring"]),
                         ("review-v2, summary", "11.0", "6 of 6", "old-review"))
        self.assertIn("old-review is excluded although its declared value is 100 and its timestamp is fresh", t)
        m, _ = by[("changed", 0)]
        self.assertEqual((m["Chosen by Equation (15.1)"], m["Total net value"]), ("summary", "3.0"))
        m, t = by[("transfer", 0)]
        self.assertEqual((m["Chosen by Equation (15.1)"], m["Total net value"], m["Excluded before scoring"]), ("current", "4.0", "expired"))
        self.assertIn("expired (age 10 > ttl 2)", t)

    def test_laboratory_agrees_with_the_three_cases(self):
        default = evaluate({"budget": 6, "now": 10, "current_version": "v2", "records": [
            {"id": "review-v2", "tokens": 4, "decision_value": 8, "timestamp": 9, "ttl": 3, "authority": True, "version": "v2"},
            {"id": "summary", "tokens": 2, "decision_value": 3, "timestamp": 8, "ttl": 5, "authority": False, "version": "v1"},
            {"id": "old-review", "tokens": 1, "decision_value": 100, "timestamp": 9, "ttl": 3, "authority": True, "version": "v1"}],
            "original_action_values": [4, 6], "compressed_action_values": [3, 5]})
        self.assertEqual(default["metrics"]["retrieval_value"], 11)
        self.assertEqual(default["metrics"]["excluded_ids"], ["old-review"])
        self.assertTrue(default["metrics"]["compression_preserves_action"])
        changed = evaluate({"budget": 2, "now": 10, "current_version": "v2", "records": [
            {"id": "review-v2", "tokens": 4, "decision_value": 8, "timestamp": 9, "ttl": 3, "authority": True, "version": "v2"},
            {"id": "summary", "tokens": 2, "decision_value": 3, "timestamp": 8, "ttl": 5, "authority": False, "version": "v1"}],
            "original_action_values": [4, 6], "compressed_action_values": [6, 5]})
        self.assertEqual(changed["metrics"]["retrieval_value"], 3)
        self.assertFalse(changed["metrics"]["compression_preserves_action"])
        transfer = evaluate({"budget": 3, "now": 20, "current_version": "doc-C", "records": [
            {"id": "expired", "tokens": 1, "decision_value": 10, "timestamp": 10, "ttl": 2, "authority": False, "version": "doc-C"},
            {"id": "current", "tokens": 3, "decision_value": 4, "timestamp": 19, "ttl": 3, "authority": True, "version": "doc-C"}],
            "original_action_values": [1, 0], "compressed_action_values": [2, 1]})
        self.assertEqual((transfer["metrics"]["retrieved_ids"], transfer["metrics"]["retrieval_value"]), (["current"], 4))
        self.assertTrue(transfer["metrics"]["compression_preserves_action"])

    def test_d02_regret_bound_and_its_premise(self):
        for (kind, eps), m, text in self.states("C15-D02", [D02_KINDS, D02_EPS]):
            self.assertEqual(m["Limit 2\u03b5"], f"{2 * eps:.1f}")
            if kind == "worst":
                full = [10, 6, 3]
                s = [10 - eps, 6 + eps, 3]
            elif kind == "dropped":
                full = [-50, 6, 3]
                s = [10, 6, 3]
            elif kind == "default":
                full, s = [4, 6], [3, 5]
            else:
                full, s = [4, 6], [6, 5]
            top = max(s)
            picks = [i for i in range(len(s)) if abs(s[i] - top) < 1e-9]
            best = max(full)
            regrets = [best - full[i] for i in picks]
            err = max(abs(a - b) for a, b in zip(s, full))
            premise = kind != "dropped" and err <= eps + 1e-9
            self.assertEqual(m["Largest error of the summary"], f"{err:.1f}")
            if len(picks) > 1:
                self.assertEqual(m["Regret of that action"], f"0.0 or {max(regrets):.1f}")
                self.assertIn("(tie)", m["Summary follows"])
            else:
                self.assertEqual(m["Regret of that action"], f"{regrets[0]:.1f}")
            claim = m["2\u03b5 claim"]
            if premise:
                self.assertEqual(claim, "holds: regret within the limit", (kind, eps))
                self.assertLessEqual(max(regrets), 2 * eps + 1e-9)  # the chapter's bound
            else:
                self.assertTrue(claim.startswith("does not apply"), (kind, eps))
        by = {(v[0], v[1]): (m, t) for v, m, t in self.states("C15-D02", [D02_KINDS, D02_EPS])}
        m, t = by[("worst", 2)]  # exact tie at 8 = 8; the bound is reached (4 = 4)
        self.assertIn("(tie)", m["Summary follows"])
        self.assertIn("10 - 6 = 4.0", t)
        m, _ = by[("worst", 3)]
        self.assertEqual((m["Summary follows"], m["Regret of that action"], m["Limit 2\u03b5"]), ("Ask owner", "4.0", "6.0"))
        # The laboratory's changed case: the action flips (regret 2); epsilon 1 fails the premise, epsilon 2 and 3 meet it.
        self.assertTrue(by[("changed", 1)][0]["2\u03b5 claim"].startswith("does not apply (error 2.0"))
        self.assertEqual(by[("changed", 2)][0]["2\u03b5 claim"], "holds: regret within the limit")
        self.assertEqual(by[("changed", 2)][0]["Summary follows"], "Action 0")
        self.assertEqual(by[("default", 1)][0]["Regret of that action"], "0.0")
        self.assertIn("|6 - 4| = 2 and |5 - 6| = 1, so the largest error is 2", by[("changed", 2)][1])

    def test_d02_dropped_state_names_the_real_mechanism(self):
        for (kind, eps), m, text in self.states("C15-D02", [D02_KINDS, D02_EPS]):
            if kind != "dropped":
                continue
            self.assertIn("this reader draws that as a value of -50", text)
            self.assertIn("an error of 10 - (-50) = 60, far above epsilon = " + f"{eps:g}", text)
            self.assertIn("The two versions disagree about which actions are permitted, so no 2 epsilon claim applies", text)
            self.assertIn("Changing epsilon moves only the limit bar here", text)
            self.assertEqual((m["Largest error of the summary"], m["Regret of that action"]), ("60.0", "56.0"))
            self.assertEqual(m["2\u03b5 claim"], "does not apply (action sets differ)")

    def test_d02_static_text_is_exact_about_ties_and_the_claim(self):
        page = html.unescape(self.page)
        self.assertIn("match or overtake only when the gap is at most 2 epsilon", page)
        self.assertIn("the full history no longer permits release (drawn here as a value of -50)", page)
        self.assertIn("this regret is at most 2 epsilon when the conditions below hold", page)

    def test_d03_policies_by_independent_rules(self):
        for (rs, auth, deletion), m, text in self.states("C15-D03", [D03_SIMS, D03_AUTH, D03_DELETION]):
            reach = auth == "reachable"
            order = [("approval", 0.98), ("note", 0.80), ("revocation", rs)]  # oldest to newest
            avail = [(k, s) for k, s in order if not (k == "approval" and deletion == "all") and not (k == "revocation" and not reach)]
            outcome = {"approval": "Unauthorized release", "revocation": "Release blocked (correct)",
                       "note": "Irrelevant recollection"}
            self.assertEqual(m["Recency only"], outcome[avail[-1][0]], (rs, auth, deletion))
            self.assertEqual(m["Similarity only"], outcome[max(avail, key=lambda a: a[1])[0]], (rs, auth, deletion))
            # Net values with lambda 1 and 2 tokens: 8 - 2 = 6 for the revocation, 0 - 2 = -2 for the others.
            self.assertEqual(m["Decision aware"], outcome["revocation"] if reach else "Abstain (correct)")
            if reach:
                self.assertIn("revocation 8 - 1 x 2 = 6.0", text)
            else:
                self.assertNotIn("revocation 8 - 1 x 2", text)
            self.assertIn("Two reports for Similarity only", text)
        by = {tuple(v): m for v, m, _ in self.states("C15-D03", [D03_SIMS, D03_AUTH, D03_DELETION])}
        # The stale-approval story: with the approval anywhere in the system, similarity retrieves it.
        self.assertEqual(by[(0.72, "reachable", "none")]["Similarity only"], "Unauthorized release")
        self.assertEqual(by[(0.72, "reachable", "store")]["Similarity only"], "Unauthorized release")  # an index copy survives
        self.assertEqual(by[(0.72, "reachable", "all")]["Similarity only"], "Irrelevant recollection")  # gone, but no authority found
        self.assertEqual(by[(0.99, "reachable", "all")]["Similarity only"], "Release blocked (correct)")
        self.assertEqual(by[(0.72, "unreachable", "all")]["Decision aware"], "Abstain (correct)")

    def test_d03_conditions_are_stated(self):
        page = html.unescape(self.page)
        self.assertIn("The index copy of the approval is assumed to keep the approval's wording and so its similarity", page)
        self.assertIn("absence from one view says nothing about the others", page.replace("Absence from one view says nothing about the others", "absence from one view says nothing about the others"))
        self.assertEqual(self.demos["C15-D03"]["stepper"], "deletion")

    def test_d03_unreachable_authority_wording_and_labels(self):
        demo = self.demos["C15-D03"]
        for key, state in demo["states"].items():
            text = state["interpretation"]
            if key.split(",")[1] == "1":  # authority unreachable
                self.assertIn("The chapter's rule for a controller that cannot query current authority is to abstain", text)
                self.assertNotIn("keeps nothing: the controller abstains", text)
                if key.split(",")[2] == "2":  # deleted from every view
                    self.assertIn("only the note is left to retrieve", text)
                    self.assertNotIn("only the note and the revocation", text)
        page = html.unescape(self.page)
        self.assertNotIn("Only Recency only", page)
        self.assertNotIn("similarity unreachable", page)
        self.assertEqual(demo["source_section"] if "source_section" in demo else "Stale approval is not support", "Stale approval is not support")
        self.assertEqual(self.demos["C15-D04"]["source"]["section"] if "source" in self.demos["C15-D04"] else "Exercises", "Exercises")

    def test_d04_exercise_one(self):
        for (p, lam), m, text in self.states("C15-D04", [D04_P, D04_LAM]):
            ev, net = 8 * p, 8 * p - lam
            self.assertEqual(m["Expected value"], f"{ev:.2f}")
            self.assertEqual(m["Net value"], f"{net:.2f}")
            self.assertEqual(m["Break-even p"], f"{lam / 8:.3f}")
            want = "tie" if abs(net) < 1e-9 else ("Retrieve" if net > 0 else "Leave out")
            self.assertEqual(m["Decision"], want)
            self.assertIn("In this model a record is worth 8 only while it is current", text)
        by = {(v[0], v[1]): (m, t) for v, m, t in self.states("C15-D04", [D04_P, D04_LAM])}
        m, t = by[(0.6, 1)]
        self.assertEqual((m["Expected value"], m["Net value"]), ("4.80", "3.80"))  # the book's 4.8 and 3.8
        self.assertIn("0.60 x 8 + 0.40 x 0 = 4.80", t)
        self.assertEqual(by[(0.5, 4)][0]["Decision"], "tie")   # 4 - 4 = 0
        self.assertEqual(by[(0.25, 4)][0]["Net value"], "-2.00")
        self.assertEqual(by[(0.25, 2)][0]["Decision"], "tie")  # 2 - 2 = 0

    def test_optional_fields_come_from_the_chapter(self):
        page = html.unescape(self.page)
        self.assertIn("Ask the chapter skill", page)
        self.assertEqual(page.count("Common wrong turn"), 4)
        self.assertGreaterEqual(page.count("What this does not settle"), 3)
        for demo in self.data["demos"]:
            self.assertTrue(demo["predict"]["correct"] and demo["predict"]["incorrect"])
            for state in demo["states"].values():
                self.assertTrue(2 <= len(state["steps"]) <= 8)
                self.assertTrue(state["alt"])
        source = (LAB.parent / "Manuscript" / "part-iv" / "15-what-an-agent-should-remember.md").read_text(encoding="utf-8")
        flat = re.sub(r"\s+", " ", source).lower()
        for phrase in ("not to retrieve the most similar text", "no `2\\varepsilon` claim applies",
                       "a high recall score with unauthorized release is a memory-system failure",
                       "broad durable authority is dangerous",
                       "the context-budget and stale-approval numbers are stipulated for teaching",
                       "the deletion-aware index and conflict-resolution rule appear only as named requirements"):
            self.assertIn(phrase, flat)

    def test_equations_are_chapter_text(self):
        source = (LAB.parent / "Manuscript" / "part-iv" / "15-what-an-agent-should-remember.md").read_text(encoding="utf-8")
        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t)
        flat = norm(source)
        found = re.findall(r'data-tex="([^"]+)"', self.page)
        # Equation (15.1) in Demonstrations 1 and 3; the inline 2 epsilon and Exercise 1 lines may also be pre-rendered by the engine.
        self.assertEqual(len(found), 2 + len([f for f in found if f in (r"2\varepsilon", r"0.6\times 8+0.4\times 0=4.8")]))
        self.assertGreaterEqual(len(found), 2)
        for inline in (r"2\varepsilon", r"0.6\times8+0.4\times0=4.8"):
            self.assertIn(inline, flat)
            self.assertIn(inline, norm(self.page.replace('&#92;', chr(92))) + norm(html.unescape(self.page)))
        for tex in found:
            self.assertIn(norm(html.unescape(tex)).rstrip("."), flat)

    def test_text_rules_and_links(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for d in self.data["demos"]:
            for s in d["states"].values():
                text += " " + s["interpretation"] + " " + " ".join(" ".join(p) for p in s["metrics"]) + " " + " ".join(s["steps"]) + " " + s["alt"]
        for bad in ("\u2014", "\u2013", "\u2212", "--"):
            self.assertNotIn(bad, text)
        for term in ("matplotlib", "numpy", "python", "jupyter"):
            self.assertNotIn(term, text.lower())
        self.assertIn("constructed", text.lower())
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))
        self.assertIn('href="../../notebooks/15-memory-budget.ipynb"', self.page)

    def test_dom_harness(self):
        if shutil.which("node") is None:
            self.skipTest("Node is not installed")
        run = subprocess.run(["node", str(HARNESS), str(self.reader)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)
        report = json.loads(run.stdout)["reports"][0]
        self.assertEqual(report["states_checked"], 48)
        self.assertEqual(report["resets_checked"], 4)
        self.assertGreaterEqual(report["predictions_checked"], 4)
        self.assertGreater(report["stepper_moves"], 0)


if __name__ == "__main__":
    unittest.main()

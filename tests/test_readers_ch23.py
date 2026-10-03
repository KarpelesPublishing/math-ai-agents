"""Chapter 23 laboratory reader: independent hand checks of the built page.

Every expected number is recomputed here from the chapter's own arithmetic
(the capability sets of the malicious-source trace, the monitor record over
two events, the approved release triple, the declared attack family and the
laboratory's default, changed and transfer traces), not read back from the
module that produced the page. The reader is built fresh into a
temporary directory, so nothing under readers/ is touched.
"""
from __future__ import annotations

import html
import importlib.util
import json
import math
import os
from fractions import Fraction
from pathlib import Path
import re
import shutil
import subprocess
import tempfile
import unittest

from math_ai_agents.chapters.ch23 import evaluate

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
WRAPPER = LAB / "tools" / "readers" / "build_readers.py"
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
SLUG = "23-local-security-monitor"


def _builder_python():
    spec = importlib.util.spec_from_file_location("reader_engine_tests", HERE / "test_readers_engine.py")
    helpers = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(helpers)
    return helpers.builder_python()


def authored_demos(number):
    """The authored CHAPTER dictionary of the module under test, keyed by demonstration id (for wording checks)."""
    import sys
    for p in (str(LAB / "tools" / "readers" / "engine"), str(LAB / "src")):
        if p not in sys.path:
            sys.path.insert(0, p)
    spec = importlib.util.spec_from_file_location(f"reader_ch{number}_wording", LAB / "tools" / "readers" / "chapters" / f"ch{number}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return {d["id"]: d for d in mod.CHAPTER["demos"]}


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def as_number(text):
    try:
        return float(text)
    except ValueError:
        return text


def f1(x):
    return f"{x:.1f}"


class Chapter23ReaderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        python = _builder_python()
        if python is None:
            raise unittest.SkipTest("no interpreter with numpy, matplotlib and jinja2 (laboratory .venv absent)")
        cls._tmp = tempfile.TemporaryDirectory()
        run = subprocess.run([python, str(WRAPPER), "--chapters", "23", "--out", cls._tmp.name], capture_output=True, text=True,
                             timeout=600, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
        if run.returncode != 0:
            raise AssertionError(run.stdout + run.stderr)
        cls.reader = Path(cls._tmp.name) / SLUG / "reader.html"
        cls.page = cls.reader.read_text(encoding="utf-8")
        cls.data = payload(cls.page)
        cls.demos = {d["id"]: d for d in cls.data["demos"]}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def grid(self, demo_id):
        """Every state keyed by the tuple of raw control values (the page shows labels; the module holds the raw values)."""
        demo = self.demos[demo_id]
        raw = authored_demos(23)[demo_id]["controls"]
        out = {}
        for key, state in demo["states"].items():
            idx = [int(i) for i in key.split(",")]
            values = tuple(c["values"][i] for c, i in zip(raw, idx))
            out[values] = (dict(state["metrics"]), state["interpretation"], state)
        return out

    def test_four_demonstrations_all_states_render(self):
        self.assertEqual(list(self.demos), ["C23-D01", "C23-D02", "C23-D03", "C23-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [12, 8, 12, 12])
        for demo in self.data["demos"]:
            combos = math.prod(len(c["values"]) for c in demo["controls"])
            self.assertEqual(len(demo["states"]), combos)
            for state in demo["states"].values():
                self.assertTrue(state["image"].startswith("data:image/svg+xml"))
                self.assertTrue(state["interpretation"])
                self.assertTrue(state["alt"])
                self.assertGreaterEqual(len(state["steps"]), 2)

    def test_size_budget(self):
        self.assertLess(self.reader.stat().st_size, 4_000_000)

    # Demonstration 1: capability containment and authority

    EFFECT_OF = {"extract": ("read_source", "user"), "upload": ("send_data", "untrusted-data"),
                 "link": ("open_link", "untrusted-data"), "secret": ("send_secret", "untrusted-data")}
    CHILD_OF = {"chapter": ({"read_source", "draft_summary", "release"}, {"read_source", "draft_summary", "release"}),
                "browser": ({"read_source", "draft_summary", "release", "open_link"}, {"read_source", "draft_summary", "release", "open_link"}),
                "narrow": ({"read_source", "draft_summary", "release"}, {"read_source", "draft_summary"})}

    def test_d01_every_state_by_hand_and_against_the_laboratory_monitor(self):
        for (request, grant), (m, text, _) in self.grid("C23-D01").items():
            effect, source = self.EFFECT_OF[request]
            parent, child = self.CHILD_OF[grant]
            held = effect in child
            trusted = source != "untrusted-data"
            allowed = held and trusted
            out = evaluate({"capabilities": sorted(child), "current_version": "v1", "events": [
                {"kind": "action", "action": effect, "authority_source": source, "version": "v1", "executed": False}]})
            self.assertEqual(out["tables"][0]["monitor_allowed"], allowed)
            self.assertEqual(m["Monitor verdict"], "allowed" if allowed else "denied")
            self.assertEqual(m["Child holds the needed effect"], "yes" if held else "no")
            self.assertEqual(m["Child contained in parent (Equation 23.1)"], "yes" if child <= parent else "no")
            self.assertIn(f"{len(child)} - {len(child & parent)} = {len(child - parent)}", text)
            self.assertIn(f"{int(held)} x {int(trusted)} = {int(allowed)}", text)
            if allowed:
                self.assertEqual(m["Stopped by"], "nothing (allowed)")
            elif not held:
                self.assertIn("capability absent", m["Stopped by"])
            else:
                self.assertIn("untrusted data", m["Stopped by"])

    def test_d01_chapter_traces(self):
        by = self.grid("C23-D01")
        # Exfiltration: send_data was never granted by any ancestor.
        self.assertEqual(by[("upload", "chapter")][0]["Monitor verdict"], "denied")
        self.assertIn("capability absent", by[("upload", "chapter")][0]["Stopped by"])
        # A calendar link with the browser capability held: Equation 23.1 passes, authority fails.
        m, text, _ = by[("link", "browser")]
        self.assertEqual((m["Child holds the needed effect"], m["Monitor verdict"]), ("yes", "denied"))
        self.assertIn("authority came from untrusted data", m["Stopped by"])
        self.assertIn("1 x 0 = 0", text)
        # Extraction is allowed in all three grants.
        for grant in ("chapter", "browser", "narrow"):
            self.assertEqual(by[("extract", grant)][0]["Monitor verdict"], "allowed")
        # The narrowed child cannot get release back, but release is not one of the requests; the check question is covered below.
        parent_two = {"read_source", "draft_summary"}
        self.assertNotIn("release", parent_two)

    # Demonstration 2: monitor memory

    def test_d02_monitor_memory_by_hand(self):
        expected = {"approved": (1, 1), "claim": (0, 0), "revoked": (1, 0), "replaced": (1, 0)}
        for (scenario, check), (m, text, _) in self.grid("C23-D02").items():
            m1, m2 = expected[scenario]
            self.assertEqual((m["Usable approvals at M1"], m["Usable approvals at M2"]), (str(m1), str(m2)))
            read = m1 if check == "entry" else m2
            self.assertEqual(m["Decision of this check"], "release allowed" if read else "release denied")
            self.assertEqual(m["Decision against the current record M2"], "release allowed" if m2 else "release denied")
            self.assertEqual(m["This check"].startswith("WRONG"), (read > 0) != (m2 > 0))
        by = self.grid("C23-D02")
        self.assertTrue(by[("revoked", "entry")][0]["This check"].startswith("WRONG"))
        self.assertEqual(by[("revoked", "recheck")][0]["This check"], "agrees")
        self.assertIn("0 + 1 - 1 = 0", by[("revoked", "entry")][1])
        self.assertIn("so this check is WRONG: it acts on old authorization.", by[("replaced", "entry")][1])
        self.assertIn("so it agrees.", by[("revoked", "recheck")][1])
        self.assertIn("Mon has no argument for prose", by[("claim", "entry")][1])

    # Demonstration 3: the release predicate

    APPROVED = ("Q3-report", "4", "external-board")
    PROPOSALS = {"none": ("Q3-report", "4", "external-board"), "document": ("Q2-report", "4", "external-board"),
                 "version": ("Q3-report", "5", "external-board"), "recipient": ("Q3-report", "4", "all subscribers")}

    def test_d03_publish_lookup_by_hand(self):
        for (changed, source), (m, text, _) in self.grid("C23-D03").items():
            triple = self.PROPOSALS[changed]
            n = sum(a == b for a, b in zip(self.APPROVED, triple))
            if source == "event":
                publish = 1 if triple == self.APPROVED else 0
                self.assertEqual(m["Fields matching"], f"{n} of 3")
            elif source == "sentence":
                publish = 0
                self.assertEqual(m["Fields matching"], f"{n} of 3 (only if it had been recorded)")
            else:
                publish = 1  # the planted entry is the proposal itself
                self.assertEqual(m["Fields matching"], "3 of 3 (the entry copies the proposal)")
            self.assertEqual(m["Publish (Equation 23.3)"], str(publish))
            self.assertEqual(m["Triple is in Approved(M_t)"], ("yes (planted)" if source == "laundered" else ("yes" if publish else "no")))
            self.assertIn(f"Publish = ", text)

    def test_d03_chapter_cases(self):
        by = self.grid("C23-D03")
        self.assertEqual(by[("version", "event")][0]["What failed"], "version")      # exercise 4: version 5 against version 4
        self.assertEqual(by[("recipient", "event")][0]["What failed"], "recipient")  # the near match to all subscribers
        self.assertEqual(by[("none", "event")][0]["Publish (Equation 23.3)"], "1")   # exercise 7: authorized versioned release
        self.assertEqual(by[("none", "sentence")][0]["What failed"], "no approval was ever recorded")
        self.assertEqual(by[("recipient", "laundered")][0]["Publish (Equation 23.3)"], "1")  # exercise 5: the collapse
        self.assertIn("Re-checking Approved(M_t) at the relabeling point", by[("recipient", "laundered")][1])
        self.assertTrue(by[("version", "event")][1].startswith("Fields matching: 1 + 0 + 1 = 2 of 3."))
        # The laboratory monitor agrees on the version cases with an event approval.
        for version, expected in (("4", True), ("5", False)):
            out = evaluate({"capabilities": ["release", "publish"], "current_version": f"v{version}", "events": [
                {"kind": "review", "valid": True, "version": "v4"},
                {"kind": "action", "action": "publish", "authority_source": "user", "version": f"v{version}", "executed": False}]})
            self.assertEqual(out["tables"][1]["monitor_allowed"], expected)

    # Demonstration 4: risk over a family, and two scores from a replayed trace

    @staticmethod
    def replay_by_hand(events, current):
        """The chapter's monitor rules applied event by event, independently of the laboratory function."""
        capabilities = {"read", "publish"}
        review = False
        denied = blocked = violations = 0
        completed = False
        for e in events:
            if e["kind"] == "review":
                review = e["valid"] and e["version"] == current
            elif e["kind"] == "data":
                violations += int(e["instruction_attempt"] and e["promoted_to_control"])
            else:
                permitted = (e["action"] in capabilities and e["authority_source"] != "untrusted-data"
                             and (e["action"] != "publish" or (review and e["version"] == current)))
                denied += int(not permitted)
                blocked += int((not permitted) and not e["executed"])
                violations += int(e["executed"] and not permitted)
                completed = completed or (e["action"] == "publish" and e["executed"] and permitted)
        return denied, blocked, violations, completed

    TRACE_EVENTS = {
        "default": ([{"kind": "data", "instruction_attempt": True, "promoted_to_control": False},
                     {"kind": "action", "action": "publish", "authority_source": "untrusted-data", "version": "v2", "executed": False},
                     {"kind": "review", "valid": True, "version": "v2"},
                     {"kind": "action", "action": "publish", "authority_source": "user", "version": "v2", "executed": True}], "v2"),
        "changed": ([{"kind": "data", "instruction_attempt": True, "promoted_to_control": True},
                     {"kind": "action", "action": "publish", "authority_source": "untrusted-data", "version": "v2", "executed": True},
                     {"kind": "review", "valid": True, "version": "v2"},
                     {"kind": "action", "action": "publish", "authority_source": "user", "version": "v2", "executed": True}], "v2"),
        "transfer": ([{"kind": "review", "valid": True, "version": "A"},
                      {"kind": "action", "action": "publish", "authority_source": "system", "version": "B", "executed": False}], "B"),
    }

    def test_patch2_d03_correct_option_does_not_claim_any_proposal(self):
        # g8-01 (major): relabeling plants only the triple the sentence names, not "any proposal".
        demo = authored_demos(23)["C23-D03"]
        options = demo["prediction_options"]
        correct = options[demo["prediction_answer"]]
        self.assertIn("for the triple it names", correct)
        self.assertNotIn("any proposal", " ".join(options))
        self.assertNotIn("any proposal", self.page)
        self.assertIn("for the triple it names", self.page)

    def test_patch2_d03_unchanged_laundered_state_is_not_called_a_failure(self):
        # g8-02: with nothing changed the planted entry equals the approved triple.
        m, _, _ = self.grid("C23-D03")[("none", "laundered")]
        self.assertIn("gap is not exercised", m["What failed"])
        m2, _, _ = self.grid("C23-D03")[("version", "laundered")]
        self.assertEqual(m2["What failed"], "the mediation: no re-check at the relabeling point")

    def test_patch2_d02_replaced_step_says_entry_no_longer_matches(self):
        # g8-10
        found = [st for key, st in self.demos["C23-D02"]["states"].items() if "no longer matches v5" in " ".join(st.get("steps", []))]
        self.assertEqual(len(found), 2)

    def test_patch2_d04_states_panels_are_independent(self):
        # g8-08
        for _, text, _ in self.grid("C23-D04").values():
            self.assertIn("declared inputs, not derived from the replayed trace", text)

    def test_d04_every_state_by_hand(self):
        for (trace, family, deputy), (m, text, _) in self.grid("C23-D04").items():
            chances = [0.05, 0.10, deputy] + ([0.45] if family == "four" else [])
            self.assertEqual(m["Risk of the declared family"], f"{max(chances):.2f}")
            self.assertEqual(m["Mean, for contrast only"], f"{sum(chances) / len(chances):.3f}")
            ties = sum(abs(c - max(chances)) < 1e-9 for c in chances)
            self.assertEqual("(tie)" in m["Set by"], ties > 1)
            events, current = self.TRACE_EVENTS[trace]
            denied, blocked, violations, completed = self.replay_by_hand(events, current)
            self.assertEqual(m["Security violations"], str(violations))
            self.assertEqual(m["Denied and not executed"], str(blocked))
            self.assertEqual(m["Task completed"], "yes" if completed else "no")
            self.assertIn(f"= {violations}", text)

    def test_d04_chapter_values_and_the_two_scores(self):
        by = self.grid("C23-D04")
        # Violations: the changed trace has two (promotion and forbidden execution); the plot-style count would be one.
        self.assertEqual(by[("changed", "three", 0.6)][0]["Security violations"], "2")
        self.assertEqual(by[("changed", "three", 0.6)][0]["Task completed"], "yes")
        self.assertIn("1 promoted instruction + 1 forbidden effect executed = 2", by[("changed", "three", 0.6)][1])
        self.assertEqual((by[("default", "three", 0.6)][0]["Security violations"], by[("default", "three", 0.6)][0]["Task completed"]), ("0", "yes"))
        self.assertEqual((by[("transfer", "three", 0.6)][0]["Security violations"], by[("transfer", "three", 0.6)][0]["Task completed"]), ("0", "no"))
        self.assertIn("secure refusal", by[("transfer", "three", 0.6)][1])
        # Family maximum: a tie at 0.1, and the retry path setting Risk once declared.
        self.assertEqual(by[("default", "three", 0.1)][0]["Set by"], "Source poisoning and Confused-deputy delegation (tie)")
        self.assertEqual(by[("default", "four", 0.1)][0]["Set by"], "Retry that skips the check")
        self.assertEqual(by[("default", "four", 0.6)][0]["Set by"], "Confused-deputy delegation")
        # Check question: 0.20, 0.35, 0.05, 0.35 gives 0.35 and 0.2375.
        chances = [0.20, 0.35, 0.05, 0.35]
        self.assertEqual(max(chances), 0.35)
        self.assertAlmostEqual(sum(chances) / 4, 0.2375)
        # Laboratory counters agree with the hand replay.
        for trace, (events, current) in self.TRACE_EVENTS.items():
            out = evaluate({"capabilities": ["read", "publish"], "current_version": current, "events": events})
            denied, blocked, violations, completed = self.replay_by_hand(events, current)
            m = out["metrics"]
            self.assertEqual((m["monitor_denied_requests"], m["blocked_requests"], m["security_violations"], m["authorized_task_completion"]),
                             (denied, blocked, violations, completed))

    def test_d04_mean_label_has_three_decimals(self):
        import sys
        for p in (str(LAB / "tools" / "readers" / "engine"), str(LAB / "src")):
            if p not in sys.path:
                sys.path.insert(0, p)
        spec = importlib.util.spec_from_file_location("reader_ch23_labels", LAB / "tools" / "readers" / "chapters" / "ch23.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        for deputy, family, expected in ((0.1, "four", "mean 0.175"), (0.6, "three", "mean 0.250")):
            fig, metrics, *_ = mod.risk_picture(trace="default", family=family, deputy=deputy)
            labels = [t.get_text() for t in fig.axes[0].texts]
            plt.close(fig)
            self.assertIn(expected, labels)
            self.assertEqual(metrics["Mean, for contrast only"], expected.split()[1])

    def test_d01_check_question_by_hand(self):
        # A parent holds only read_source and draft_summary; a child proposing release is not contained.
        parent, child = {"read_source", "draft_summary"}, {"read_source", "draft_summary", "release"}
        self.assertFalse(child <= parent)
        authored = authored_demos(23)
        self.assertIn("release", authored["C23-D01"]["check"])
        self.assertIn("close the route", authored["C23-D04"]["application"])

    # Optional fields

    def test_optional_fields_are_present_and_sourced(self):
        authored = authored_demos(23)
        text = (LAB.parent / "Manuscript" / "part-vi" / "23-when-the-environment-gives-instructions.md").read_text(encoding="utf-8")
        self.assertIn("## What this does not settle", text)
        for demo_id in ("C23-D01", "C23-D03", "C23-D04"):
            self.assertEqual(authored[demo_id]["scope_note"]["source_section"], "What this does not settle")
        for demo_id, demo in authored.items():
            self.assertIn("misconception", demo)
            self.assertEqual(len(demo["prediction_options"]), 3)
        self.assertIn("Ask the chapter skill", self.page)
        self.assertEqual(self.page.count("Common wrong turn"), 4)

    # Page-level checks

    def test_displayed_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 23)

        def norm(t):
            t = re.sub(r"\\tag\{[^}]*\}", "", t)
            t = re.sub(r"\\[,;:!]", "", t)
            return re.sub(r"[\s{}]", "", t).rstrip(".")
        allowed = {norm(e["tex"]) for e in chapter["equations"]}
        alts = re.findall(r'data-tex="([^"]+)"', self.page)
        self.assertEqual(len(alts), 4)
        shown = {norm(html.unescape(t)) for t in alts}
        for tex in shown:
            self.assertIn(tex, allowed)
        self.assertEqual(len(shown), 4)

    def test_source_sections_exist_in_the_canonical_chapter(self):
        text = (LAB.parent / "Manuscript" / "part-vi" / "23-when-the-environment-gives-instructions.md").read_text(encoding="utf-8")
        headings = {line.lstrip("#").strip() for line in text.splitlines() if line.startswith("#")}
        expected = ["Data may inform; control may direct", "A monitor's memory only advances from observed events",
                    "Publish needs identity, version, recipient, and current approval", "A security case needs a declared adversary",
                    "What this does not settle"]
        for title in expected:
            self.assertIn(title, headings)
            self.assertIn(title, html.unescape(self.page))

    def test_links_and_offline(self):
        config = json.loads((LAB / "tools" / "readers" / "reader.config.json").read_text(encoding="utf-8"))
        index_href = config["links"]["index"]["href"]  # read from the configuration, which another owner may change
        for href in (f"../../notebooks/{SLUG}.ipynb", "../../skills/maa-23-local-security-monitor/SKILL.md", index_href):
            self.assertIn(f'href="{href}"', self.page)
        self.assertIsNone(re.search(r'(src|href)="(https?:)?//', self.page))

    def test_page_text_has_no_dashes_or_dependency_names(self):
        text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", self.page, flags=re.S)
        text = html.unescape(re.sub(r"<[^>]+>", " ", text))
        for demo in self.data["demos"]:
            for state in demo["states"].values():
                text += " " + state["interpretation"] + " " + " ".join(" ".join(p) for p in state["metrics"]) + " " + " ".join(state["steps"]) + " " + state["alt"]
        for bad in ("\u2014", "\u2013", "--"):
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
        self.assertEqual((report["states_checked"], report["resets_checked"], report["labelled_controls"]), (44, 4, 9))
        self.assertEqual((report["ask_skill"], report["predictions_checked"], report["panels_checked"]), (1, 12, 7))


if __name__ == "__main__":
    unittest.main()

"""Chapter 23 laboratory reader: independent hand checks of the built page.

Expected values are recomputed here from the chapter's own trace (capability
sets, the approved triple, the declared attack family), not read back from the
module that produced the page.
"""
from __future__ import annotations

import html
import itertools
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest

HERE = Path(__file__).resolve().parent
LAB = HERE.parent
import os
READER = Path(os.environ.get("READER23", LAB / "readers" / "23-local-security-monitor" / "reader.html"))
HARNESS = LAB / "tools" / "readers" / "engine" / "dom_harness.js"
ENGINE = LAB / "tools" / "readers"


def payload(text):
    match = re.search(r'<script id="reader-data" type="application/json">(.*?)</script>', text, re.S)
    return json.loads(match.group(1))


def number(text):
    try:
        return float(text)
    except ValueError:
        return text


class Chapter23ModuleTests(unittest.TestCase):
    """Run the figure functions directly: every control combination renders and numbers match the chapter."""

    @classmethod
    def setUpClass(cls):
        import sys
        try:
            import matplotlib
            import numpy  # noqa: F401
            import jinja2  # noqa: F401
        except ImportError:
            raise unittest.SkipTest("needs the laboratory .venv (numpy, matplotlib)")
        matplotlib.use("Agg")
        for p in (str(ENGINE / "engine"), str(LAB / "src")):
            if p not in sys.path:
                sys.path.insert(0, p)
        import importlib.util
        spec = importlib.util.spec_from_file_location("reader_ch23_under_test", ENGINE / "chapters" / "ch23.py")
        cls.mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.mod)

    def run_fn(self, name, **kw):
        import matplotlib.pyplot as plt
        fig, metrics, text = getattr(self.mod, name)(**kw)
        plt.close(fig)
        return metrics, text

    def test_all_combinations_render(self):
        import matplotlib.pyplot as plt
        for demo in self.mod.CHAPTER["demos"]:
            keys = [c["key"] for c in demo["controls"]]
            for combo in itertools.product(*[c["values"] for c in demo["controls"]]):
                fig, metrics, text = getattr(self.mod, demo["function"])(**dict(zip(keys, combo)))
                plt.close(fig)
                self.assertTrue(metrics and text)

    def test_d01_containment(self):
        parent = {"read_source", "draft_summary", "release"}
        children = {"inherits": parent, "narrowed": {"read_source", "draft_summary"}}
        for child, held in children.items():
            for effect in ("read_source", "draft_summary", "release", "send_data"):
                m, text = self.run_fn("containment_picture", proposed=effect, child=child)
                self.assertEqual(m["Child holds the proposed effect"], "yes" if effect in held else "no")
                self.assertEqual(m["Capability check (Allowed)"], "passes" if effect in held else "fails")
                self.assertEqual(m["Child contained in parent (Equation 23.1)"], "yes" if held <= parent else "no")
                self.assertIn(f"{len(held)} - {len(held)} = 0", text)
        # send_data is never in any child of this parent
        self.assertEqual(self.run_fn("containment_picture", proposed="send_data", child="inherits")[0]["Capability check (Allowed)"], "fails")

    def test_d02_monitor_memory(self):
        # usable approvals at M1 and M2 from the event sequence, by hand
        expected = {"approved": (1, 1), "claim": (0, 0), "revoked": (1, 0), "replaced": (1, 0)}
        for scenario, (m1, m2) in expected.items():
            for check in ("entry", "recheck"):
                m, text = self.run_fn("monitor_picture", scenario=scenario, check=check)
                self.assertEqual((m["Usable approvals at M1"], m["Usable approvals at M2"]), (str(m1), str(m2)))
                read = m1 if check == "entry" else m2
                self.assertEqual(m["Decision of this check"], "release allowed" if read else "release denied")
                self.assertEqual(m["Decision against the current record M2"], "release allowed" if m2 else "release denied")
                wrong = (read > 0) != (m2 > 0)
                self.assertEqual(m["This check"].startswith("WRONG"), wrong)
        # entry-only is wrong exactly in the revoked and replaced cases
        self.assertTrue(self.run_fn("monitor_picture", scenario="revoked", check="entry")[0]["This check"].startswith("WRONG"))
        self.assertEqual(self.run_fn("monitor_picture", scenario="revoked", check="recheck")[0]["This check"], "agrees")
        self.assertIn("0 + 1 - 1 = 0", self.run_fn("monitor_picture", scenario="revoked", check="entry")[1])

    def test_d03_publish_lookup(self):
        approved = ("Q3-report", "4", "external-board")
        proposals = {"none": approved, "document": ("Q2-report", "4", "external-board"),
                     "version": ("Q3-report", "5", "external-board"), "recipient": ("Q3-report", "4", "all subscribers")}
        for changed, triple in proposals.items():
            for source in ("event", "sentence"):
                m, text = self.run_fn("release_picture", changed=changed, source=source)
                n = sum(a == b for a, b in zip(approved, triple))
                publish = 1 if (source == "event" and triple == approved) else 0
                self.assertEqual(m["Fields matching"], f"{n} of 3" + ("" if source == "event" else " (only if it had been recorded)"))
                self.assertEqual(m["Publish (Equation 23.3)"], str(publish))
                self.assertEqual(m["Triple is in Approved(M_t)"], "yes" if publish else "no")
        self.assertEqual(self.run_fn("release_picture", changed="version", source="event")[0]["What failed"], "version")
        # exact match from a sentence is still refused: the empty record is the boundary case
        m, _ = self.run_fn("release_picture", changed="none", source="sentence")
        self.assertEqual(m["Publish (Equation 23.3)"], "0")
        self.assertEqual(m["What failed"], "no approval was ever recorded")

    def test_d01_reason_for_a_missing_effect_is_state_aware(self):
        # Finding g8-16: the parent holds release, so containment in the parent is not why the child cannot get it back.
        _, text = self.run_fn("containment_picture", proposed="release", child="narrowed")
        self.assertIn("Anything the child delegates to can hold at most a subset of the child set", text)
        self.assertIn("although the parent still holds it", text)
        self.assertNotIn("because the child set sits inside the parent set", text)
        # send_data is outside the parent as well, so the parent-side reason applies.
        for child in ("inherits", "narrowed"):
            _, text = self.run_fn("containment_picture", proposed="send_data", child=child)
            self.assertIn("the parent does not hold it either", text)
            self.assertNotIn("because the child set sits inside the parent set", text)
            self.assertNotIn("although the parent still holds it", text)

    def test_d02_verdict_sentence_is_grammatical(self):
        # Finding g8-18: the old text read "so it WRONG: acts on old authorization".
        for scenario in ("revoked", "replaced"):
            _, text = self.run_fn("monitor_picture", scenario=scenario, check="entry")
            self.assertIn("so this check is WRONG: it acts on old authorization.", text)
            self.assertNotIn("so it WRONG", text)
        _, text = self.run_fn("monitor_picture", scenario="revoked", check="recheck")
        self.assertIn("so it agrees.", text)
        self.assertNotIn("WRONG", text)

    def test_d03_sentence_scenario_does_not_claim_a_matching_record(self):
        # Finding g8-20: no record is on file, so the field row is conditional and the set is not called empty.
        for changed in ("none", "document", "version", "recipient"):
            m, text = self.run_fn("release_picture", changed=changed, source="sentence")
            self.assertIn("only if it had been recorded", m["Fields matching"])
            self.assertIn("would match if the triple had been recorded", text)
            self.assertNotIn("the set is empty", text)
        m, text = self.run_fn("release_picture", changed="none", source="sentence")
        self.assertIn("adds nothing to Approved(M_t)", text)
        self.assertEqual(m["Fields matching"], "3 of 3 (only if it had been recorded)")
        # With an event on file the plain wording stays.
        m, text = self.run_fn("release_picture", changed="version", source="event")
        self.assertEqual(m["Fields matching"], "2 of 3")
        self.assertTrue(text.startswith("Fields matching: 1 + 0 + 1 = 2 of 3."))
        demo = next(d for d in self.mod.CHAPTER["demos"] if d["id"] == "C23-D03")
        self.assertIn("adds nothing to the set", demo["explanation"])
        self.assertNotIn("so the set is empty", demo["explanation"])
        self.assertIn("does the lookup still pass", demo["question"])
        self.assertNotIn("Which single change", demo["question"])

    def test_d04_figure_prints_the_mean_with_three_decimals(self):
        # Finding g8-21: the figure label must agree with the metric (0.175 and 0.225, not 0.17 and 0.23).
        import matplotlib.pyplot as plt
        for deputy, family, expected in ((0.1, "four", "mean 0.175"), (0.3, "four", "mean 0.225"), (0.02, "three", "mean 0.057")):
            fig, metrics, _ = self.mod.risk_picture(deputy=deputy, family=family)
            labels = [t.get_text() for t in fig.axes[0].texts]
            plt.close(fig)
            self.assertIn(expected, labels)
            self.assertEqual(metrics["Mean, for contrast only"], expected.split()[1])

    def test_d04_application_says_to_close_the_route(self):
        demo = next(d for d in self.mod.CHAPTER["demos"] if d["id"] == "C23-D04")
        self.assertIn("close the route", demo["application"])

    def test_d04_risk_is_a_maximum(self):
        for deputy in (0.02, 0.1, 0.3, 0.6):
            for family in ("three", "four"):
                chances = [0.05, 0.10, deputy] + ([0.45] if family == "four" else [])
                m, text = self.run_fn("risk_picture", deputy=deputy, family=family)
                self.assertEqual(m["Risk of the declared family"], f"{max(chances):.2f}")
                self.assertEqual(m["Mean, for contrast only"], f"{sum(chances) / len(chances):.3f}")
                self.assertEqual(m["Attacks declared"], str(len(chances)))
                ties = sum(abs(c - max(chances)) < 1e-9 for c in chances)
                self.assertEqual("(tie)" in m["Set by"], ties > 1)
        self.assertEqual(self.run_fn("risk_picture", deputy=0.1, family="three")[0]["Set by"], "Source poisoning and Confused-deputy delegation (tie)")
        # the worst member of the four-attack family beats the confused-deputy value at 0.30
        self.assertEqual(self.run_fn("risk_picture", deputy=0.3, family="four")[0]["Set by"], "Retry that skips the check")
        # declaring one more attack can only keep Risk or raise it
        for deputy in (0.02, 0.1, 0.3, 0.6):
            three = float(self.run_fn("risk_picture", deputy=deputy, family="three")[0]["Risk of the declared family"])
            four = float(self.run_fn("risk_picture", deputy=deputy, family="four")[0]["Risk of the declared family"])
            self.assertGreaterEqual(four, three)


@unittest.skipUnless(READER.is_file(), "Chapter 23 reader not built; run tools/readers/build_readers.py --chapters 23")
class Chapter23BuiltPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = READER.read_text(encoding="utf-8")
        cls.data = payload(cls.page)

    def test_four_demonstrations_within_budget(self):
        self.assertEqual([d["id"] for d in self.data["demos"]], ["C23-D01", "C23-D02", "C23-D03", "C23-D04"])
        self.assertEqual([len(d["states"]) for d in self.data["demos"]], [8, 8, 8, 8])
        self.assertLess(READER.stat().st_size, 2_500_000)

    def test_equations_are_chapter_equations(self):
        chapter = next(c for c in json.loads((LAB / "chapter-map.json").read_text()) if c["chapter"] == 23)

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
        run = subprocess.run(["node", str(HARNESS), str(READER)], capture_output=True, text=True, timeout=120)
        self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == "__main__":
    unittest.main()

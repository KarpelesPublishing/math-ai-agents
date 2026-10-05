"""Operational checks independent of the chapter implementations."""
from __future__ import annotations
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from math_ai_agents.core import analyze, available_chapters, chapter_content, bundle_root
from math_ai_agents.routing import suggest, workflow, ALIASES
from math_ai_agents.capstone import simulate, DEFAULTS


class RuntimeTests(unittest.TestCase):
    def test_full_collection_is_available(self):
        self.assertEqual(available_chapters(), list(range(1, 28)))

    def test_all_three_cases_execute_without_mutating_inputs(self):
        for n in available_chapters():
            with self.subTest(chapter=n):
                content = chapter_content(n)
                for field in ("defaults", "changed", "transfer"):
                    data = copy.deepcopy(content[field]); before = copy.deepcopy(data)
                    report = analyze(n, data)
                    self.assertEqual(data, before)
                    self.assertTrue(report["receipt"]["executed"])
                    self.assertEqual(report["mode"], "analyze")
                    self.assertIn("provenance not independently verified", report["evidence_kind"])
                    json.dumps(report, allow_nan=False)
                    self.assertTrue(report["result"]["series"])
                original = analyze(n)["result"]
                changed = analyze(n, case="changed")["result"]
                self.assertNotEqual(original, changed, "Changed assumption must change some calculated conclusion or diagnostic.")

    def test_example_provenance_is_explicit(self):
        self.assertEqual(analyze(6)["evidence_kind"], "constructed teaching example")

    def test_non_object_and_nonfinite_inputs_stop(self):
        with self.assertRaises(ValueError): analyze(6, [])
        with self.assertRaises(ValueError): analyze(6, {"invalid": float("nan")})
        with self.assertRaises(ValueError): analyze(True)

    def test_54_natural_phrase_routes(self):
        for n, phrases in ALIASES.items():
            for phrase in phrases[:2]:
                with self.subTest(chapter=n, phrase=phrase):
                    result = suggest("Please analyze the " + phrase + " in my agent workflow.")
                    self.assertIn(n, result["chapters"])
                    self.assertEqual(result["chapters"][0], n)

    def test_ambiguous_and_unknown_requests_do_not_auto_execute(self):
        self.assertEqual(suggest("Can I trust this memory?")["status"], "ambiguous")
        self.assertEqual(suggest("Schedule my dentist appointment")["status"], "needs-context")
        self.assertEqual(suggest("Teach chapter 99")["status"], "unsupported")
        with self.assertRaises(ValueError): suggest("")

    def test_named_workflows_run_and_require_all_supplied_inputs(self):
        for name in ("reliability", "compute-budget", "memory-improvement", "safe-release"):
            result = workflow(name)
            self.assertGreater(len(result["reports"]), 1)
            self.assertIn("not interchangeable", result["composition_boundary"])
            with self.assertRaises(ValueError): workflow(name, {})

    def test_every_packaged_chapter_helper_operates_outside_bundle(self):
        root = bundle_root()
        for entry in json.loads((root / "chapter-map.json").read_text()):
            script = root / "skills" / entry["skill"] / "scripts/run.py"
            with tempfile.TemporaryDirectory() as d:
                run = subprocess.run([sys.executable, str(script), "--case", "transfer"], cwd=d, capture_output=True, text=True, timeout=30)
                self.assertEqual(run.returncode, 0, run.stderr)
                report = json.loads(run.stdout)
                self.assertEqual(report["chapter"], entry["chapter"])
                self.assertEqual(report["mode"], "transfer")


class CapstoneTests(unittest.TestCase):
    def test_guarded_permission_and_exactly_once_completion(self):
        d = dict(DEFAULTS, runs=40, step_success=1.0, shared_failure=0.0,
                 stale_layout_probability=1.0, injection_probability=0.0,
                 dropped_ack_probability=1.0, approved_probability=1.0)
        result = simulate(d)
        self.assertEqual(result["metrics"]["guarded"]["authorized_confirmed_completions"], 40)
        self.assertEqual(result["metrics"]["guarded"]["unauthorized_effects"], 0)
        self.assertEqual(result["metrics"]["baseline"]["duplicate_effects"], 40)
        self.assertEqual(result["metrics"]["baseline"]["unauthorized_effects"], 40)

    def test_zero_budget_prevents_effects(self):
        result = simulate(dict(DEFAULTS, runs=10, budget=0))
        self.assertTrue(all(r["effects"] == 0 for r in result["records"]))

    def test_unavailable_reviewer_never_creates_approval(self):
        d = dict(DEFAULTS, runs=10, step_success=1, shared_failure=0,
                 injection_probability=0, approved_probability=0, review_available_probability=0)
        result = simulate(d)
        self.assertEqual(result["metrics"]["guarded"]["outcomes"], {"review_unavailable": 10})
        self.assertEqual(result["metrics"]["guarded"]["unauthorized_effects"], 0)

    def test_incomplete_and_invalid_capstone_inputs_stop(self):
        with self.assertRaises(ValueError): simulate({"runs": 10})
        with self.assertRaises(ValueError): simulate(dict(DEFAULTS, runs=True))
        with self.assertRaises(ValueError): simulate(dict(DEFAULTS, step_success=float("nan")))

    def test_route_helper_does_not_suggest_from_one_generic_word(self):
        self.assertEqual(suggest("weather forecast for Paris")["status"], "weak-match")
        self.assertEqual(suggest("Compare the tool retry with verification")["chapters"][0], 17)

    def test_display_rounding_hides_float_noise_but_not_stored_precision(self):
        from math_ai_agents.core import report_text
        report = {"chapter": 0, "method": "m", "question": "q", "evidence_kind": "e",
                  "result": {"metrics": {"a": 0.7600000000000001, "b": -1.1102230246251565e-16}}}
        text = report_text(report)
        self.assertIn('"a": 0.76', text); self.assertNotIn("0.7600000000000001", text); self.assertIn('"b": 0.0', text)
        self.assertEqual(report["result"]["metrics"]["a"], 0.7600000000000001)

    def test_capstone_contract_stage_is_tagged_with_the_approval_chapter(self):
        out = simulate(DEFAULTS)
        stages = [t for run in out.get("sample_traces", []) for t in (run if isinstance(run, list) else run.get("trace", []))]
        contract = [t for t in stages if isinstance(t, dict) and t.get("stage") == "contract"]
        self.assertTrue(contract)
        self.assertTrue(all(t["chapter"] == 22 for t in contract))

    def test_legacy_probes_match_expected_outputs_and_no_root_duplicates(self):
        root = Path(__file__).resolve().parents[1]
        for stray in ("expected", "fixtures", "release-console.html"):
            self.assertFalse((root / stray).exists(), stray + " duplicates Companion/" + stray)
        for script, fixture in [("document_release_simulator", "release-probe"), ("computer_use_probe", "computer-use"),
                                ("agent_learning_probe", "learning"), ("orchestration_probe", "orchestration"),
                                ("resource_allocation_probe", "resources"), ("evaluation_probe", "evaluation")]:
            run = subprocess.run([sys.executable, f"scripts/{script}.py", "--manifest", f"Companion/fixtures/{fixture}.json"],
                                 cwd=root, capture_output=True, text=True, timeout=60)
            self.assertEqual(run.returncode, 0, run.stderr)
            self.assertEqual(json.loads(run.stdout), json.loads((root / f"Companion/expected/{fixture}.json").read_text()), script)


TOOLS = Path(__file__).resolve().parents[1] / "tools"


def _load_tool(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location("maa_tool_" + name, TOOLS / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class NotebookContentTests(unittest.TestCase):
    def test_formula_callouts_survive_wrapped_blockquotes(self):
        build = _load_tool("build_materials")
        single = "\n> **What it does.** One line.\n\n> **Reading the formula.** Another line.\n"
        wrapped = ("\n> **What it does.** Names a proposed procedure version while keeping the\n"
                   "> underlying model parameters frozen.\n>\n"
                   "> **Reading the formula.** `e_t` can lead to a change in `\\phi`; it does\n"
                   "> not make a claim about a new value of `\\theta`.\n\nProse after.\n")
        self.assertEqual(build.formula_callouts(single), ["One line.", "Another line."])
        self.assertEqual(build.formula_callouts(wrapped), [
            "Names a proposed procedure version while keeping the underlying model parameters frozen.",
            "`e_t` can lead to a change in `\\phi`; it does not make a claim about a new value of `\\theta`."])

    def test_reading_export_shows_stream_and_result_outputs(self):
        try:
            import markdown  # noqa: F401
        except ImportError:
            self.skipTest("Markdown package not installed")
        export = _load_tool("export_reading")
        nb = {"cells": [{"cell_type": "code", "source": "print('alpha')\n1+1", "outputs": [
            {"output_type": "stream", "name": "stdout", "text": ["alpha\n"]},
            {"output_type": "execute_result", "execution_count": 1, "metadata": {}, "data": {"text/plain": "2"}}]}]}
        body = "".join(export.notebook_sections(nb))
        self.assertIn("alpha", body)
        self.assertIn('<div class="output"><pre>2</pre></div>', body)

    def test_saved_notebooks_keep_printed_output(self):
        """Every code cell that prints must have saved stream output (regression for lost stdout)."""
        import os, re
        folder = Path(os.environ.get("MAA_NOTEBOOK_DIR", Path(__file__).resolve().parents[1] / "notebooks"))
        missing = []
        for path in sorted(folder.glob("*.ipynb")):
            nb = json.loads(path.read_text(encoding="utf-8"))
            for index, cell in enumerate(nb["cells"]):
                if cell["cell_type"] != "code":
                    continue
                source = "".join(cell["source"]) if isinstance(cell["source"], list) else cell["source"]
                if re.search(r"^\s*print\(", source, flags=re.M) and not any(o["output_type"] == "stream" for o in cell.get("outputs", [])):
                    missing.append(f"{path.name} cell {index}")
        self.assertEqual(missing, [], "Re-run tools/execute_notebooks.py: printed output was not saved.")


if __name__ == "__main__": unittest.main()

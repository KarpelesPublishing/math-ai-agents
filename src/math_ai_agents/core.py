"""Chapter discovery and explicit, inspectable local computations."""
from __future__ import annotations

import hashlib
import importlib
import json
import math
from pathlib import Path
import sys
import time

VERSION = "1.0.0"


def bundle_root() -> Path:
    root = Path(__file__).resolve().parents[2]
    if not (root / "content").is_dir():
        raise RuntimeError("The chapter content directory is missing. Restore the complete laboratory bundle.")
    return root


def chapter_content(chapter: int) -> dict:
    if type(chapter) is not int or not 1 <= chapter <= 27:
        raise ValueError("Choose an integer chapter from 1 through 27.")
    path = bundle_root() / "content" / f"ch{chapter:02d}.json"
    if not path.is_file():
        raise ValueError(f"Chapter {chapter} has not been installed in this bundle.")
    return json.loads(path.read_text(encoding="utf-8"))


def available_chapters() -> list[int]:
    return sorted(int(p.stem[2:]) for p in (bundle_root() / "content").glob("ch??.json"))


def _finite_tree(value):
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("The calculation produced a nonfinite number; inspect its domain and assumptions.")
    if isinstance(value, dict):
        for item in value.values():
            _finite_tree(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _finite_tree(item)


def analyze(chapter: int, data: dict | None = None, case: str = "example") -> dict:
    content = chapter_content(chapter)
    fields = {"example": "defaults", "changed": "changed", "transfer": "transfer"}
    if case not in fields:
        raise ValueError("Case must be example, changed or transfer.")
    supplied = data is not None
    if not supplied:
        data = content[fields[case]]
    if not isinstance(data, dict):
        raise ValueError("Chapter input must be a JSON object. Use the chapter's documented schema.")
    # Copy so a caller can reuse a manifest without a method mutating it.
    encoded = json.dumps(data, sort_keys=True, allow_nan=False)
    clean = json.loads(encoded)
    module = importlib.import_module(f"math_ai_agents.chapters.ch{chapter:02d}")
    started = time.perf_counter()
    result = module.evaluate(clean)
    _finite_tree(result)
    json.dumps(result, allow_nan=False)
    module_path = Path(module.__file__)
    return {
        "lab_version": VERSION,
        "chapter": chapter,
        "method": content["slug"],
        "question": content["question"],
        "evidence_kind": "supplied local inputs; provenance not independently verified" if supplied else "constructed teaching example",
        "mode": "analyze" if supplied else case,
        "inputs": clean,
        "result": result,
        "receipt": {
            "executed": True,
            "python": sys.version.split()[0],
            "input_sha256": hashlib.sha256(encoded.encode()).hexdigest(),
            "method_sha256": hashlib.sha256(module_path.read_bytes()).hexdigest(),
            "shared_validation_sha256": hashlib.sha256((module_path.parent / "_shared.py").read_bytes()).hexdigest(),
            "runtime_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "content_sha256": hashlib.sha256((bundle_root() / "content" / f"ch{chapter:02d}.json").read_bytes()).hexdigest(),
            "elapsed_seconds": time.perf_counter() - started,
        },
    }


def _display_numbers(value):
    """Round floats for reading (10 significant digits; float noise near zero shown as 0)."""
    if isinstance(value, float):
        return 0.0 if abs(value) < 1e-12 else float(f"{value:.10g}")
    if isinstance(value, dict):
        return {k: _display_numbers(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_display_numbers(v) for v in value]
    return value


def report_text(report: dict) -> str:
    result = report["result"]
    parts = [f"Chapter {report['chapter']}: {report['method']}", report["question"],
             f"Evidence: {report['evidence_kind']}", "\nCalculated quantities:",
             json.dumps(_display_numbers(result.get("metrics", result)), indent=2, ensure_ascii=False, allow_nan=False)]
    if result.get("interpretation"):
        parts += ["\nInterpretation:", str(result["interpretation"])]
    for key in ("assumptions", "limitations"):
        values = result.get(key, [])
        if values:
            parts += [f"\n{key.capitalize()}:"] + [f"- {v}" for v in values]
    parts += ["\nExecution: completed locally; constructed inputs are not deployment measurements."]
    return "\n".join(parts)

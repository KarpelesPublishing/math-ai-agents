#!/usr/bin/env python3
"""Install the lab skills into an explicit host discovery directory."""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def skill_sources(root):
    """Select canonical skills from the registry, excluding URL compatibility aliases."""
    entries = json.loads((root / "chapter-map.json").read_text(encoding="utf-8"))
    return sorted([root / "skills/math-ai-agents/SKILL.md",
                   *(root / entry["skill_path"] for entry in entries)])


def install(root: Path, target: Path) -> dict:
    root, target = root.resolve(), target.expanduser().resolve()
    manifest = json.loads((root / "lab-manifest.json").read_text(encoding="utf-8"))
    sources = skill_sources(root)
    if len(sources) != 28:
        raise ValueError("Expected all 28 skills. Use the complete laboratory bundle.")
    target.mkdir(parents=True, exist_ok=True)
    installed, preserved = [], []
    for entry in sources:
        source, destination = entry.parent, target / entry.parent.name
        if destination.exists():
            preserved.append(destination.name)
            continue
        shutil.copytree(source, destination)
        pointer = {"bundle_root": str(root), "lab_version": manifest["lab_version"],
                   "python": str(root / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python"))}
        (destination / "references" / "runtime-location.json").write_text(json.dumps(pointer, indent=2) + "\n", encoding="utf-8")
        files = {str(p.relative_to(destination)): file_hash(p) for p in destination.rglob("*") if p.is_file()}
        (destination / "references" / "installation-record.json").write_text(json.dumps({"files": files}, indent=2) + "\n", encoding="utf-8")
        installed.append(destination.name)
    return {"installed": installed, "preserved_existing": preserved, "skill_directory": str(target),
            "runtime_directory": str(root), "next_step": "Keep the laboratory folder at this location. Restart the assistant to refresh skill discovery. Actual discovery depends on the host."}


def uninstall(root: Path, target: Path) -> dict:
    removed, preserved = [], []
    for source in skill_sources(root):
        destination = target / source.parent.name
        record = destination / "references" / "installation-record.json"
        if not record.exists():
            if destination.exists(): preserved.append(destination.name)
            continue
        saved = json.loads(record.read_text(encoding="utf-8"))["files"]
        current = {str(p.relative_to(destination)): file_hash(p) for p in destination.rglob("*")
                   if p.is_file() and p != record}
        if current != saved:
            preserved.append(destination.name)
            continue
        shutil.rmtree(destination)
        removed.append(destination.name)
    return {"removed": removed, "preserved_modified_or_unmanaged": preserved,
            "note": "Notebooks, user inputs and the laboratory runtime are retained."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--target", type=Path, default=Path.home() / ".codex" / "skills")
    parser.add_argument("--uninstall", action="store_true")
    args = parser.parse_args()
    result = uninstall(args.root.resolve(), args.target.expanduser().resolve()) if args.uninstall else install(args.root, args.target)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

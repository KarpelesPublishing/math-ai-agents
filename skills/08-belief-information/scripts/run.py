#!/usr/bin/env python3
"""Find the version-matched lab for a direct-bundle or installed skill."""
from __future__ import annotations
import json
from pathlib import Path
import sys


def resolve(skill: Path) -> Path:
    pointer = skill / "references" / "runtime-location.json"
    if pointer.exists():
        info = json.loads(pointer.read_text(encoding="utf-8"))
        root = Path(info["bundle_root"])
        expected = info["lab_version"]
    else:
        root = next((p for p in skill.parents if (p / "lab-manifest.json").exists()), None)
        expected = "1.0.0"
    if root is None or not (root / "lab-manifest.json").is_file():
        raise ValueError("Laboratory runtime missing. Restore the complete extracted bundle or rerun its skill installer.")
    manifest = json.loads((root / "lab-manifest.json").read_text(encoding="utf-8"))
    if manifest["lab_version"] != expected:
        raise ValueError("Skill and runtime versions differ. Reinstall skills from this bundle.")
    return root


def main():
    skill = Path(__file__).resolve().parents[1]
    try:
        root = resolve(skill)
        sys.path.insert(0, str(root / "src"))
        from math_ai_agents.__main__ import main as lab_main
        args = sys.argv[1:]
        chapter_file = skill / "references" / "chapter.json"
        if chapter_file.exists():
            chapter = json.loads(chapter_file.read_text(encoding="utf-8"))["chapter"]
            if args and args[0] in ('demo', 'demo-list'):
                args = [args[0], '--chapter', str(chapter)] + args[1:]
            else:
                args = ["run", "--chapter", str(chapter)] + args
        return lab_main(args)
    except (ValueError, OSError, KeyError) as error:
        print(str(error), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

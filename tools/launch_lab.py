#!/usr/bin/env python3
"""A small reader launcher for guides, computations, notebooks and skills."""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import webbrowser


def main():
    # Windows consoles often default to a legacy code page; never fail on a printable report.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError):
            pass
    root = Path(__file__).resolve().parents[1]
    if sys.version_info < (3, 10):
        print("Python 3.10 or later is required to run calculations. Opening the reading guide, which needs no Python.")
        webbrowser.open((root / "guide" / "index.html").as_uri())
        return
    sys.path.insert(0, str(root / "src"))
    from math_ai_agents.core import analyze, report_text, available_chapters, chapter_content
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=int)
    parser.add_argument("--case", choices=["example", "changed", "transfer"], default="example")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--guide", action="store_true")
    args = parser.parse_args()
    if args.run is not None:
        try:
            print(report_text(analyze(args.run, case=args.case)))
        except (ValueError, KeyError) as error:
            print("Cannot complete that action:", error, file=sys.stderr)
            raise SystemExit(2)
        return
    if args.list:
        for n in available_chapters(): print(f"{n:02d}: {chapter_content(n)['question']}")
        return
    if args.guide:
        webbrowser.open((root / "guide" / "index.html").as_uri())
        return
    while True:
        print("\nThe Mathematics of Artificial Intelligence Agents Laboratory\n"
              "1  Read the illustrated guide (no installation)\n"
              "2  Run a chapter example\n"
              "3  Install notebook tools\n"
              "4  Open Jupyter notebooks\n"
              "5  Install the 28 skills for Codex\n"
              "6  Remove unmodified installed skills\n"
              "0  Close\n")
        try:
            choice = input("Choose a number: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return
        try:
            if choice == "0": return
            if choice == "1": webbrowser.open((root / "guide" / "index.html").as_uri())
            elif choice == "2":
                chapter = int(input("Chapter number (1-27): "))
                print(report_text(analyze(chapter)))
            elif choice == "3":
                from setup_lab import prepare
                prepare(root)
            elif choice == "4":
                python = root / ".venv" / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
                if not python.exists():
                    print("Choose 3 first to prepare notebook tools."); continue
                env = dict(os.environ)
                env["JUPYTER_PATH"] = str(root / ".venv" / "share" / "jupyter")
                env["IPYTHONDIR"] = str(root / ".local-state" / "ipython")
                env["JUPYTER_RUNTIME_DIR"] = str(root / ".local-state" / "jupyter")
                subprocess.run([str(python), "-m", "jupyterlab", "--notebook-dir", str(root)], cwd=root, env=env)
            elif choice in ("5", "6"):
                from install_skills import install, uninstall
                target = Path.home() / ".codex" / "skills"
                print("Skill directory:", target)
                print("Existing skills and reader modifications are preserved.")
                if input("Proceed? Type yes: ").strip().lower() == "yes":
                    print(json.dumps(install(root, target) if choice == "5" else uninstall(root, target), indent=2))
            else:
                print("Choose one of the displayed numbers.")
        except (ValueError, OSError, KeyError) as error:
            print("Cannot complete that action:", error)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Prepare a dedicated notebook environment without changing system Python."""
from __future__ import annotations
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import venv


def prepare(root: Path, install_dependencies=True):
    if sys.version_info < (3, 10):
        raise ValueError("Python 3.10 or later is required. Install a supported Python, then reopen the launcher.")
    if install_dependencies and sys.version_info < (3, 11):
        raise ValueError("The tested notebook stack needs Python 3.11 or later. Python 3.10 can still run the standard-library chapter examples.")
    root = root.resolve()
    environment = root / ".venv"
    interpreter = environment / ("Scripts/python.exe" if sys.platform == "win32" else "bin/python")
    if not interpreter.exists():
        venv.EnvBuilder(with_pip=True).create(environment)
    if install_dependencies:
        dependencies = root / "requirements-notebooks.txt"
        command = [str(interpreter), "-m", "pip", "install", "--disable-pip-version-check", "-r", str(dependencies)]
        print("Installing notebook dependencies into", environment, flush=True)
        run = subprocess.run(command, cwd=root)
        if run.returncode:
            raise ValueError("Notebook setup did not finish. Check your connection and rerun setup. The reading guide and standard-library chapter commands remain available.")
        run = subprocess.run([str(interpreter), "-m", "ipykernel", "install", "--prefix", str(environment), "--name", "maa-lab", "--display-name", "Mathematics of AI Agents"], cwd=root)
        if run.returncode:
            raise ValueError("Dependencies installed, but kernel registration failed. Rerun setup before opening Jupyter.")
    record = {"environment": str(environment), "python": str(interpreter),
              "dependencies_requested": install_dependencies, "system_python_modified": False}
    (root / "setup-receipt.json").write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    return record


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--headless", action="store_true", help="Create only the dedicated Python environment; skip notebook dependencies.")
    args = parser.parse_args()
    try:
        print(json.dumps(prepare(args.root, not args.headless), indent=2))
    except (ValueError, OSError) as error:
        print(error, file=sys.stderr)
        raise SystemExit(2)


if __name__ == "__main__":
    main()

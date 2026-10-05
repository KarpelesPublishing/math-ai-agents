#!/usr/bin/env python3
"""Build the laboratory readers for this book.

Thin wrapper around the project-independent engine in engine/build_readers.py.
It supplies this book's configuration (reader.config.json beside this file)
unless --config is given. All other options pass through unchanged:

  .venv/bin/python tools/readers/build_readers.py --chapters 6 --check
  .venv/bin/python tools/readers/build_readers.py --chapters all
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE / "engine"))
sys.dont_write_bytecode = True

from build_readers import main  # noqa: E402  (the engine module of the same name)

if __name__ == "__main__":
    args = sys.argv[1:]
    if "--config" not in args:
        args = ["--config", str(HERE / "reader.config.json"), *args]
    sys.exit(main(args))

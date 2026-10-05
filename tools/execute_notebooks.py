#!/usr/bin/env python3
"""Execute notebooks in fresh processes and genuine IPython kernels.

The in-process Jupyter kernel avoids listening sockets. Each notebook gets a
new operating-system process and a new kernel, with an empty namespace. This
is distinct from testing the normal browser/server transport.
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import time


def execute_one(source: Path, target: Path):
    import nbformat
    from ipykernel.inprocess.manager import InProcessKernelManager

    nb = nbformat.read(source, as_version=4)
    nbformat.validate(nb)
    for cell in nb.cells:
        if cell.cell_type == "code":
            cell.outputs = []
            cell.execution_count = None
    os.chdir(source.parent)
    manager = InProcessKernelManager()
    manager.start_kernel()
    client = manager.client()
    client.start_channels()
    started = time.perf_counter()
    count = 0
    try:
        for cell in nb.cells:
            if cell.cell_type != "code" or not cell.source.strip():
                continue
            count += 1
            msg_id = client.execute(cell.source, allow_stdin=False, stop_on_error=True)
            reply = client.get_shell_msg(timeout=120)
            while True:
                message = client.get_iopub_msg(timeout=120)
                # The in-process kernel emits stream (print) messages with an empty
                # parent header, so only reject messages that name another request.
                # Cells run one at a time, so an unparented message belongs to this cell.
                parent_id = (message.get("parent_header") or {}).get("msg_id")
                if parent_id is not None and parent_id != msg_id:
                    continue
                kind = message["msg_type"]
                if kind == "execute_input":
                    cell.execution_count = message["content"]["execution_count"]
                elif kind in ("stream", "display_data", "execute_result", "error"):
                    cell.outputs.append(nbformat.v4.output_from_msg(message))
                elif kind == "clear_output":
                    cell.outputs = []
                elif kind == "status" and message["content"]["execution_state"] == "idle":
                    break
            if reply["content"]["status"] != "ok":
                raise RuntimeError(f"Cell {count} failed: {reply['content'].get('ename')}: {reply['content'].get('evalue')}")
            if re.search(r"^\s*print\(", cell.source, flags=re.M) and not any(o.output_type == "stream" for o in cell.outputs):
                raise RuntimeError(f"Cell {count} prints but no stream output was captured.")
        nb.metadata["lab_execution"] = {
            "method": "fresh process; new ipykernel InProcessKernelManager; cells submitted as Jupyter execute requests",
            "python": sys.version.split()[0], "code_cells": count,
            "elapsed_seconds": time.perf_counter() - started,
            "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
            "created_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "network_transport_tested": False,
        }
        nbformat.validate(nb)
        target.parent.mkdir(parents=True, exist_ok=True)
        nbformat.write(nb, target)
    finally:
        client.stop_channels()
        manager.shutdown_kernel()
    return nb.metadata["lab_execution"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--receipt", type=Path)
    parser.add_argument("--one", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--chapters", help="Comma-separated notebook prefixes, such as 06,17,24.")
    args = parser.parse_args()
    if args.one:
        execute_one(args.one.resolve(), args.target.resolve() if args.target else args.one.resolve())
        return
    root = args.root.resolve()
    selected = set(args.chapters.split(",")) if args.chapters else None
    notebooks = [p for p in sorted((root / "notebooks").glob("*.ipynb")) if selected is None or p.name[:2] in selected]
    if not notebooks:
        raise SystemExit("No notebooks matched.")
    records = []
    for source in notebooks:
        with tempfile.TemporaryDirectory(prefix="maa-execution-") as sandbox:
            target = Path(sandbox) / source.name
            env = dict(os.environ)
            env.update({"IPYTHONDIR": str(Path(sandbox) / "ipython"), "MPLCONFIGDIR": str(Path(sandbox) / "matplotlib"), "PYTHONHASHSEED": "0"})
            run = subprocess.run([sys.executable, str(Path(__file__).resolve()), "--one", str(source), "--target", str(target)],
                                 capture_output=True, text=True, timeout=180, env=env)
            record = {"notebook": str(source.relative_to(root)), "exit_code": run.returncode,
                      "stderr": run.stderr, "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest()}
            if run.returncode == 0:
                import nbformat
                executed = nbformat.read(target, as_version=4)
                record["execution"] = dict(executed.metadata["lab_execution"])
                source.write_bytes(target.read_bytes())
                record["executed_sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
            records.append(record)
            print(source.name, "PASS" if run.returncode == 0 else "FAIL", flush=True)
            if run.returncode:
                print(run.stderr, file=sys.stderr)
                break
    receipt = args.receipt or root / "reader-output" / "execution-receipt.json"  # reader-output is never packaged
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps({"method": "fresh subprocess and fresh in-process Jupyter kernel per notebook",
                                  "interpreter": sys.executable, "records": records,
                                  "status": "PASS" if len(records) == len(notebooks) and all(r["exit_code"] == 0 for r in records) else "FAIL"}, indent=2) + "\n")
    if len(records) != len(notebooks) or any(r["exit_code"] for r in records):
        raise SystemExit(1)


if __name__ == "__main__":
    main()

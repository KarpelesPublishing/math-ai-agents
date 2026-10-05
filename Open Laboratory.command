#!/bin/zsh
set -eu
LAB_ROOT="${0:A:h}"
cd "$LAB_ROOT"
if [[ -x "$LAB_ROOT/.venv/bin/python" ]]; then
    "$LAB_ROOT/.venv/bin/python" "$LAB_ROOT/tools/launch_lab.py"
elif command -v python3 >/dev/null 2>&1; then
    python3 "$LAB_ROOT/tools/launch_lab.py"
else
    open "$LAB_ROOT/guide/index.html"
    print "Reading guide opened. Running calculations needs Python 3.10 or later."
    read -r "reply?Press Return to close."
fi

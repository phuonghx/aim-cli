#!/bin/bash
# Prefer python3: modern macOS and Debian/Ubuntu do not ship a bare `python`.
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python"
fi
"$PYTHON_CMD" "$(dirname "$0")/aim/aim_cli.py" "$@"

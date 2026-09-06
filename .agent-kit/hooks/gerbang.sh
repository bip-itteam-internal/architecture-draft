#!/usr/bin/env bash
# gerbang.sh — cermin gerbang.ps1 untuk mac/linux; logikanya di gerbang-lib.py (satu tempat).
# pakai: gerbang.sh <path> [--base origin/main] [--kit <kit>] [--tanpa-build] [--tanpa-test] [--keluaran <file>]
command -v python3 >/dev/null 2>&1 || { echo "butuh python3" >&2; exit 2; }
exec python3 "$(dirname "${BASH_SOURCE[0]}")/gerbang-lib.py" gerbang "$@"

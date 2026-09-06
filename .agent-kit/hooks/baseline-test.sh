#!/usr/bin/env bash
# baseline-test.sh — cermin baseline-test.ps1 untuk mac/linux; logikanya di gerbang-lib.py (satu tempat).
# pakai: baseline-test.sh <path checkout origin/main bersih> [--kit <kit>] [--services a,b]
command -v python3 >/dev/null 2>&1 || { echo "butuh python3" >&2; exit 2; }
exec python3 "$(dirname "${BASH_SOURCE[0]}")/gerbang-lib.py" baseline "$@"

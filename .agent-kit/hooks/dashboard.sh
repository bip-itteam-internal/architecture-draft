#!/usr/bin/env bash
# dashboard.sh — cermin dashboard.ps1 untuk mac/linux; logikanya di dashboard.py, UI di dashboard.template.html.
# pakai: dashboard.sh [--workspace WS] [--hari 30] [--repos a,b] [--tanpa-gh] [--loop DETIK] [--keluaran F]
command -v python3 >/dev/null 2>&1 || { echo "butuh python3" >&2; exit 2; }
exec python3 "$(dirname "${BASH_SOURCE[0]}")/dashboard.py" "$@"

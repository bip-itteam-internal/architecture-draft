#!/usr/bin/env bash
# antre.sh - cermin antre.ps1 untuk mac/linux: NO-OP TERCATAT (kit 1.30.0). Perintahnya langsung
# dijalankan tanpa mengantre; antrean hanya diimplementasikan untuk Windows (lihat antre-lib.ps1).
# pakai: antre.sh -- <perintah> [argumen...]
[ "${1:-}" = "--" ] && shift
[ "$#" -eq 0 ] && { echo "pakai: antre.sh -- <perintah> [argumen...]" >&2; exit 2; }
echo "[antre] mac/linux: antrean tidak diimplementasikan, langsung jalan" >&2
exec "$@"

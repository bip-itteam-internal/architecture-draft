#!/usr/bin/env bash
# sesi-selesai.sh — SessionEnd: tandai sesi selesai. Selalu exit 0.
. "$(dirname "${BASH_SOURCE[0]}")/sesi-lib.sh"
raw="$(hook_input)"
sid="$(hook_field "$raw" session_id)"; [ -n "$sid" ] || exit 0
ws="$(hook_field "$raw" cwd)"; [ -n "$ws" ] || ws="$PWD"
f="$(sesi_path "$ws" "$sid")"; [ -f "$f" ] || exit 0
now="$(now_utc)"
sesi_write "$ws" "$sid" "$(file_field "$f" mulai)" "$now" "$now" "selesai" "$ws" "$(file_field "$f" tahap)" "$(file_field "$f" task)" "$(file_field "$f" worktree)" "$(file_field "$f" branch)"
exit 0

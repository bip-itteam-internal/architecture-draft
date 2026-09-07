#!/usr/bin/env bash
# sesi-sentuh.sh — UserPromptSubmit: perbarui terakhir/tahap/task. Selalu exit 0.
. "$(dirname "${BASH_SOURCE[0]}")/sesi-lib.sh"
raw="$(hook_input)"
sid="$(hook_field "$raw" session_id)"; [ -n "$sid" ] || exit 0
ws="$(hook_field "$raw" cwd)"; [ -n "$ws" ] || ws="$PWD"
prompt="$(hook_field "$raw" prompt)"
f="$(sesi_path "$ws" "$sid")"; now="$(now_utc)"
if [ -f "$f" ]; then
  mulai="$(file_field "$f" mulai)"; tahap="$(file_field "$f" tahap)"; task="$(file_field "$f" task)"
  wt="$(file_field "$f" worktree)"; br="$(file_field "$f" branch)"
else
  mulai="$now"; tahap="mulai"; task=""; wt=""; br=""
fi
dikenal='start-task|plan|implement|review|sync-docs|wrap|analisa-kebutuhan|brief|kerjakan|judge|supervise|ekstrak-skill|papan-sesi'
if printf '%s' "$prompt" | grep -Eq "^[[:space:]]*/($dikenal)([[:space:]]|$)"; then
  tahap="$(printf '%s' "$prompt" | sed -E "s#^[[:space:]]*/($dikenal).*#\1#")"
  arg="$(printf '%s' "$prompt" | sed -E "s#^[[:space:]]*/($dikenal)[[:space:]]*##" | tr -s '[:space:]' ' ' | cut -c1-80)"
  case "$tahap" in start-task|kerjakan|brief|analisa-kebutuhan) [ -n "$arg" ] && task="$arg";; esac
fi
sesi_write "$ws" "$sid" "$mulai" "$now" "" "aktif" "$ws" "$tahap" "$task" "$wt" "$br"
exit 0

#!/usr/bin/env bash
# session-start.sh — info flow + cek versi kit + cek staleness vault + daftarkan sesi ke papan
. "$(dirname "${BASH_SOURCE[0]}")/sesi-lib.sh"
raw="$(hook_input)"
ws="$(hook_field "$raw" cwd)"; [ -n "$ws" ] || ws="$PWD"
sid="$(hook_field "$raw" session_id)"
vault="$ws/architecture-draft"
kit_ver_file="$vault/.agent-kit/VERSION"
inst_file="$ws/.claude/.kit-version"

ctx="Flow wajib: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap"
ctx="$ctx | Opsional sebelum flow: /analisa-kebutuhan <kebutuhan manajemen> (mentah -> ADR + dok + daftar task)"
ctx="$ctx | Loop otonom: /brief <masalah> -> /kerjakan <brief> (judge otomatis, berhenti di PR). Sesi lain: /papan-sesi. Skill: /ekstrak-skill, /supervise"

if [ -f "$kit_ver_file" ]; then
  kit_ver="$(tr -d '[:space:]' < "$kit_ver_file")"
  inst_ver="unknown"; [ -f "$inst_file" ] && inst_ver="$(tr -d '[:space:]' < "$inst_file")"
  if [ "$kit_ver" != "$inst_ver" ]; then
    ctx="$ctx | Update agent-kit tersedia (terpasang: $inst_ver, terbaru: $kit_ver). Jalankan ulang .agent-kit/init.sh lalu restart sesi."
  else
    ctx="$ctx | Agent-kit v$inst_ver (terkini)."
  fi
fi

git -C "$vault" fetch --quiet >/dev/null 2>&1 || true
local_rev="$(git -C "$vault" rev-parse @ 2>/dev/null || true)"
remote_rev="$(git -C "$vault" rev-parse '@{u}' 2>/dev/null || true)"
base_rev="$(git -C "$vault" merge-base @ '@{u}' 2>/dev/null || true)"
# "ketinggalan" hanya bila local = merge-base & beda dari remote (remote di depan)
if [ -n "$local_rev" ] && [ -n "$remote_rev" ] && [ -n "$base_rev" ] && [ "$local_rev" != "$remote_rev" ] && [ "$local_rev" = "$base_rev" ]; then
  ctx="$ctx | architecture-draft ketinggalan dari remote. Jalankan: git -C architecture-draft pull"
fi

# daftarkan sesi; sesi yang di-resume mempertahankan `mulai`
if [ -n "$sid" ]; then
  f="$(sesi_path "$ws" "$sid")"; now="$(now_utc)"
  if [ -f "$f" ]; then
    sesi_write "$ws" "$sid" "$(file_field "$f" mulai)" "$now" "" "aktif" "$ws" "$(file_field "$f" tahap)" "$(file_field "$f" task)" "$(file_field "$f" worktree)" "$(file_field "$f" branch)"
  else
    sesi_write "$ws" "$sid" "$now" "$now" "" "aktif" "$ws" "mulai" "" "" ""
  fi
  ctx="$ctx | Sesi ini: $sid (papan: .task-plans/sesi/$sid.json)"
fi

# ctx tidak mengandung tanda kutip ganda -> aman ditempel ke JSON string
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$ctx"
exit 0

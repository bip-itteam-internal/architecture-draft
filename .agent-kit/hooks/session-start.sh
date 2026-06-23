#!/usr/bin/env bash
# session-start.sh — info flow + cek versi kit + cek staleness vault
vault="$PWD/architecture-draft"
kit_ver_file="$vault/.agent-kit/VERSION"
inst_file="$PWD/.claude/.kit-version"

ctx="Flow wajib: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap"

if [ -f "$kit_ver_file" ]; then
  kit_ver="$(tr -d '[:space:]' < "$kit_ver_file")"
  inst_ver="unknown"; [ -f "$inst_file" ] && inst_ver="$(tr -d '[:space:]' < "$inst_file")"
  if [ "$kit_ver" != "$inst_ver" ]; then
    ctx="$ctx | Update agent-kit tersedia (terpasang: $inst_ver, terbaru: $kit_ver). Jalankan ulang .agent-kit/init.sh."
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

# ctx tidak mengandung tanda kutip ganda -> aman ditempel ke JSON string
printf '{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"%s"}}\n' "$ctx"
exit 0

#!/usr/bin/env bash
set -euo pipefail

ws="$PWD"; active=""; no_precommit=0
while [ $# -gt 0 ]; do
  case "$1" in
    --workspace) ws="$2"; shift 2;;
    --active-project) active="$2"; shift 2;;
    --no-precommit-hook) no_precommit=1; shift;;
    *) echo "arg tak dikenal: $1"; exit 1;;
  esac
done

kit_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"   # .agent-kit
vault="$ws/architecture-draft"
[ -d "$vault" ] || { echo "architecture-draft tidak ada sebagai sibling di '$ws'. Clone dulu."; exit 1; }

git -C "$vault" fetch --quiet >/dev/null 2>&1 || true

# deteksi project sibling ber-.git
mapfile -t projects < <(for d in "$ws"/*/; do
  name="$(basename "$d")"
  [ "$name" = "architecture-draft" ] && continue
  [ -d "$d/.git" ] && echo "$name"
done)

if [ -z "$active" ]; then
  [ "${#projects[@]}" -gt 0 ] || { echo "Tidak ada project sibling ber-.git."; exit 1; }
  echo "Project terdeteksi:"; i=0
  for p in "${projects[@]}"; do echo "  [$i] $p"; i=$((i+1)); done
  read -r -p "Pilih nomor/nama project aktif: " sel
  if [[ "$sel" =~ ^[0-9]+$ ]]; then active="${projects[$sel]}"; else active="$sel"; fi
fi

claude="$ws/.claude"; mkdir -p "$claude"
for d in commands hooks skills rules; do
  rm -rf "$claude/$d"   # prune file lama yg dihapus di kit baru
  [ -d "$kit_root/$d" ] && { mkdir -p "$claude/$d"; cp -R "$kit_root/$d/." "$claude/$d/"; }
done

ss_cmd="bash \\\"$claude/hooks/session-start.sh\\\""
pc_cmd="bash \\\"$claude/hooks/pre-commit-reminder.sh\\\""
if [ "$no_precommit" -eq 1 ]; then
  cat > "$claude/settings.json" <<JSON
{ "hooks": { "SessionStart": [ { "hooks": [ { "type": "command", "command": "$ss_cmd" } ] } ] } }
JSON
else
  cat > "$claude/settings.json" <<JSON
{ "hooks": {
  "SessionStart": [ { "hooks": [ { "type": "command", "command": "$ss_cmd" } ] } ],
  "PreToolUse": [ { "matcher": "Bash", "hooks": [ { "type": "command", "command": "$pc_cmd" } ] } ]
} }
JSON
fi

kit_ver="$(tr -d '[:space:]' < "$kit_root/VERSION")"
sed -e "s/__KIT_VERSION__/$kit_ver/g" -e "s/__ACTIVE_PROJECT__/$active/g" \
  "$kit_root/templates/workspace-CLAUDE.md" > "$claude/CLAUDE.md"
printf '%s' "$kit_ver" > "$claude/.kit-version"

echo ""
echo "OK. Agent-kit v$kit_ver terpasang ke $claude"
echo "Project aktif: $active"
echo "Flow: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap"
[ "$no_precommit" -eq 1 ] && echo "(pre-commit reminder: NONAKTIF)" || echo "(pre-commit reminder: aktif)"

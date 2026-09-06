#!/usr/bin/env bash
set -euo pipefail

ws="$PWD"; active=""; no_precommit=0; no_githooks=0
while [ $# -gt 0 ]; do
  case "$1" in
    --workspace) ws="$2"; shift 2;;
    --active-project) active="$2"; shift 2;;
    --no-precommit-hook) no_precommit=1; shift;;
    --no-githooks) no_githooks=1; shift;;
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
# team-memory TIDAK disalin: di-import langsung dari vault oleh CLAUDE.md (lihat template)
# hooks/githooks ikut tersalin sebagai subfolder hooks; dipakai lewat core.hooksPath di bawah
for d in commands hooks skills agents; do
  rm -rf "$claude/$d"   # prune file lama yg dihapus di kit baru
  [ -d "$kit_root/$d" ] && { mkdir -p "$claude/$d"; cp -R "$kit_root/$d/." "$claude/$d/"; }
done
chmod +x "$claude"/hooks/*.sh "$claude"/hooks/githooks/* 2>/dev/null || true

ss_cmd="bash \\\"$claude/hooks/session-start.sh\\\""
pc_cmd="bash \\\"$claude/hooks/pre-commit-gate.sh\\\""
up_cmd="bash \\\"$claude/hooks/sesi-sentuh.sh\\\""
se_cmd="bash \\\"$claude/hooks/sesi-selesai.sh\\\""

# Plugin WAJIB tim, di-enable lewat settings SCOPE PROJECT supaya berlaku bagi siapa pun
# yang clone + trust workspace ini — tak perlu tiap orang ingat menyalakannya.
# Sengaja hanya yang WAJIB; rekomendasi lain tetap opsional lewat /skills.
plugins_json='"superpowers@claude-plugins-official": true'

# Matcher mencakup PowerShell juga: satu kit untuk Windows dan mac/linux (ADR 0077).
if [ "$no_precommit" -eq 1 ]; then
  cat > "$claude/settings.json" <<JSON
{
  "enabledPlugins": { $plugins_json },
  "hooks": {
    "SessionStart":     [ { "hooks": [ { "type": "command", "command": "$ss_cmd" } ] } ],
    "UserPromptSubmit": [ { "hooks": [ { "type": "command", "command": "$up_cmd" } ] } ],
    "SessionEnd":       [ { "hooks": [ { "type": "command", "command": "$se_cmd" } ] } ]
  }
}
JSON
else
  cat > "$claude/settings.json" <<JSON
{
  "enabledPlugins": { $plugins_json },
  "hooks": {
    "SessionStart":     [ { "hooks": [ { "type": "command", "command": "$ss_cmd" } ] } ],
    "UserPromptSubmit": [ { "hooks": [ { "type": "command", "command": "$up_cmd" } ] } ],
    "SessionEnd":       [ { "hooks": [ { "type": "command", "command": "$se_cmd" } ] } ],
    "PreToolUse": [ { "matcher": "Bash|PowerShell", "hooks": [ { "type": "command", "command": "$pc_cmd" } ] } ]
  }
}
JSON
fi

kit_ver="$(tr -d '[:space:]' < "$kit_root/VERSION")"
sed -e "s/__KIT_VERSION__/$kit_ver/g" -e "s/__ACTIVE_PROJECT__/$active/g" \
  "$kit_root/templates/workspace-CLAUDE.md" > "$claude/CLAUDE.md"

# git hooks lokal (pre-push) lewat core.hooksPath ABSOLUT per repo kode; yang sudah punya
# hooksPath lain (mis. husky) dilewati, bukan ditimpa.
githooks="$claude/hooks/githooks"
dipasang=""; dilewati=""
if [ "$no_githooks" -eq 0 ]; then
  for p in "${projects[@]}"; do
    dir="$ws/$p"
    existing="$(git -C "$dir" config --get core.hooksPath 2>/dev/null || true)"
    if [ -n "$existing" ] && [ "$existing" != "$githooks" ]; then dilewati="$dilewati $p(sudah:$existing)"; continue; fi
    if git -C "$dir" config core.hooksPath "$githooks" 2>/dev/null; then dipasang="$dipasang $p"; else dilewati="$dilewati $p(gagal)"; fi
  done
fi

mkdir -p "$ws/.task-plans/sesi" "$ws/.task-plans/briefs" "$ws/.task-plans/judge"
printf '%s' "$kit_ver" > "$claude/.kit-version"

echo ""
echo "OK. Agent-kit v$kit_ver terpasang ke $claude"
echo "Project aktif: $active"
echo "Flow: /start-task -> /plan -> /implement -> /review -> /sync-docs -> /wrap"
echo "Loop: /brief -> /kerjakan (judge otomatis) -> PR | /papan-sesi | /supervise | /ekstrak-skill"
[ "$no_precommit" -eq 1 ] && echo "(gerbang pre-commit: NONAKTIF)" || echo "(gerbang pre-commit: aktif, matcher Bash|PowerShell)"
[ -n "$dipasang" ] && echo "(pre-push terpasang:$dipasang)"
[ -n "$dilewati" ] && echo "(pre-push DILEWATI:$dilewati)"
echo "Restart sesi Claude Code supaya hook baru terbaca."

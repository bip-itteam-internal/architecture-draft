#!/usr/bin/env bash
# pre-commit-gate.sh — cermin pre-commit-gate.ps1 (alasan desain ada di sana).
# MENOLAK `git commit` di branch default repo KODE lewat exit 2; vault dikecualikan.
#
# CATATAN (brief pre-commit-gate-overhead, 2026-09-12): init.sh memasang skrip ini di
# belakang filter "if" (pola *commit*) sehingga proses ini TIDAK di-spawn sama sekali kalau
# isi command tak cocok. Menambah bentuk commit baru yang dikenali DI SINI wajib diikuti
# memperluas pola "if" di init.ps1 DAN init.sh -- lihat komentar di init.ps1 untuk detail dan
# hasil verifikasi.
raw="$( [ -t 0 ] && printf '' || cat )"
[ -n "$raw" ] || exit 0
if command -v python3 >/dev/null 2>&1; then
  cmd="$(printf '%s' "$raw" | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command",""))
except Exception: print("")' 2>/dev/null)"
  cwd="$(printf '%s' "$raw" | python3 -c 'import json,sys
try: print(json.load(sys.stdin).get("cwd",""))
except Exception: print("")' 2>/dev/null)"
else
  cmd="$(printf '%s' "$raw" | sed -n 's/.*"command":[[:space:]]*"\(\([^"\\]\|\\.\)*\)".*/\1/p' | head -n1)"
  cwd="$(printf '%s' "$raw" | sed -n 's/.*"cwd":[[:space:]]*"\([^"]*\)".*/\1/p' | head -n1)"
fi
[ -n "$cmd" ] || exit 0

# tiap segmen (; && || baris baru): cari `git [-C dir] [-c k=v]... commit`
sq="'"
seg_re="(^|[[:space:]/\\\\])git(\\.exe)?([[:space:]]+(-C[[:space:]]+(\"[^\"]*\"|$sq[^$sq]*$sq|[^[:space:]]+)|-c[[:space:]]+[^[:space:]]+|--?[^[:space:]]+))*[[:space:]]+commit([[:space:]]|$)"
hit=""; dir=""
while IFS= read -r seg; do
  if printf '%s' "$seg" | grep -Eq "$seg_re"; then
    hit=1
    dir="$(printf '%s' "$seg" | sed -nE "s/.*[[:space:]]-C[[:space:]]+(\"([^\"]*)\"|$sq([^$sq]*)$sq|([^[:space:]]+)).*/\2\3\4/p")"
    break
  fi
done <<EOF
$(printf '%s\n' "$cmd" | sed 's/&&/\n/g; s/||/\n/g; s/;/\n/g')
EOF
[ -n "$hit" ] || exit 0

# `$v="..."; git -C $v commit`
case "$dir" in \$*) n="${dir#\$}"; n="${n#\{}"; n="${n%\}}"
  v="$(printf '%s\n' "$cmd" | sed -nE "s/.*\\\$$n[[:space:]]*=[[:space:]]*(\"([^\"]*)\"|$sq([^$sq]*)$sq).*/\2\3/p" | head -n1)"; [ -n "$v" ] && dir="$v";; esac
# GAGAL-TERTUTUP: -C ada tetapi path-nya tidak bisa ditentukan (ekspresi/variabel) -> tolak.
# Versi gagal-terbuka pernah meloloskan commit di main lewat `-C $t` (2026-09-06).
if [ -n "$dir" ] && [ ! -d "$dir" ]; then
  echo "DITOLAK gerbang agent-kit: ada 'git commit' tetapi repo-nya tidak bisa ditentukan dari perintah (path '$dir' dari ekspresi/variabel). Tulis path LITERAL di -C. Gerbang ini sengaja gagal-tertutup." >&2
  exit 2
fi
[ -n "$dir" ] || dir="$cwd"
[ -n "$dir" ] && [ -d "$dir" ] || exit 0

common="$(git -C "$dir" rev-parse --path-format=absolute --git-common-dir 2>/dev/null)" || exit 0
[ -n "$common" ] || exit 0
case "$common" in *architecture-draft*)
  printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Vault: stage per-nama berkas (jangan git add -A), wikilink 0 broken, regenerasi VAULT-INDEX bila dok berubah, tanpa trailer Co-Authored-By."}}\n'
  exit 0;; esac

branch="$(git -C "$dir" symbolic-ref --short HEAD 2>/dev/null)" || exit 0
[ -n "$branch" ] || exit 0
defaults="main master"
oh="$(git -C "$dir" symbolic-ref --short refs/remotes/origin/HEAD 2>/dev/null || true)"
[ -n "$oh" ] && defaults="$defaults ${oh#origin/}"
for d in $defaults; do
  if [ "$d" = "$branch" ]; then
    echo "DITOLAK gerbang agent-kit: 'git commit' di branch '$branch' repo kode '$dir'. Semua repo kode wajib lewat PR (team-memory, ADR 0077). Buat branch dulu: git -C \"$dir\" checkout -b feat/<nama> lalu commit di sana." >&2
    exit 2
  fi
done
printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Reminder sebelum commit: sudah /sync-docs? wikilink resolve (0 broken)? test hijau? Tanpa trailer Co-Authored-By."}}\n'
exit 0

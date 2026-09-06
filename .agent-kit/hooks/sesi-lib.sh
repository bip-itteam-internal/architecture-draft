#!/usr/bin/env bash
# sesi-lib.sh — cermin sesi-lib.ps1: SATU tempat bentuk berkas sesi untuk hook mac/linux.
# Bentuk dan artinya lihat sesi-lib.ps1. python3 dipakai bila ada (parsing JSON yang benar);
# tanpa python3 jatuh ke sed yang cukup untuk field string sederhana.

sesi_dir()  { printf '%s/.task-plans/sesi' "$1"; }
sesi_path() { printf '%s/.task-plans/sesi/%s.json' "$1" "$2"; }
now_utc()   { date -u +%Y-%m-%dT%H:%M:%SZ; }

# stdin JSON dari Claude Code; bila dijalankan manusia tanpa stdin jangan memblokir
hook_input() { if [ -t 0 ]; then printf ''; else cat; fi; }

# hook_field <json> <key>  -> nilai string ("" bila tak ada / null)
hook_field() {
  if command -v python3 >/dev/null 2>&1; then
    printf '%s' "$1" | python3 -c 'import json,sys
try:
    d=json.load(sys.stdin); v=d.get(sys.argv[1],"")
    print("" if v is None else v)
except Exception: print("")' "$2" 2>/dev/null
  else
    printf '%s' "$1" | sed -n "s/.*\"$2\":[[:space:]]*\"\([^\"]*\)\".*/\1/p" | head -n1
  fi
}
# file_field <file> <key>
file_field() { [ -f "$1" ] || { printf ''; return; }; hook_field "$(cat "$1")" "$2"; }

json_esc() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g' | tr -d '\n\r'; }

# sesi_write ws id mulai terakhir selesai status cwd tahap task worktree branch
sesi_write() {
  mkdir -p "$(sesi_dir "$1")"
  if [ -z "$5" ]; then selj=null; else selj="\"$(json_esc "$5")\""; fi
  printf '{\n  "session_id": "%s",\n  "mulai": "%s",\n  "terakhir": "%s",\n  "selesai": %s,\n  "status": "%s",\n  "cwd": "%s",\n  "tahap": "%s",\n  "task": "%s",\n  "worktree": "%s",\n  "branch": "%s"\n}\n' \
    "$(json_esc "$2")" "$(json_esc "$3")" "$(json_esc "$4")" "$selj" "$(json_esc "$6")" "$(json_esc "$7")" \
    "$(json_esc "$8")" "$(json_esc "$9")" "$(json_esc "${10}")" "$(json_esc "${11}")" > "$(sesi_path "$1" "$2")"
}

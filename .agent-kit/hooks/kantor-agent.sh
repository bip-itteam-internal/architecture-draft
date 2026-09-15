#!/usr/bin/env bash
# kantor-agent.sh — cermin kantor-agent.ps1 untuk mac/linux. Alasan desain ada di kantor-agent.ps1;
# logika data di kantor-agent.py, UI di kantor-agent.template.html.
# pakai: kantor-agent.sh [--workspace WS] [--proyek-dir DIR] [--sekali] [--interval 2] [--sepi-menit 60] [--tanpa-buka] [--berhenti]
set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WS="$(pwd)"; PROYEK="$HOME/.claude/projects"; SEKALI=0; INTERVAL=2; SEPI=60; BUKA=1; BERHENTI=0
while [ $# -gt 0 ]; do
  case "$1" in
    --workspace) WS="$2"; shift 2 ;;
    --proyek-dir) PROYEK="$2"; shift 2 ;;
    --sekali) SEKALI=1; shift ;;
    --interval) INTERVAL="$2"; shift 2 ;;
    --sepi-menit) SEPI="$2"; shift 2 ;;
    --tanpa-buka) BUKA=0; shift ;;
    --berhenti) BERHENTI=1; shift ;;
    *) echo "kantor-agent: argumen tak dikenal: $1" >&2; exit 2 ;;
  esac
done
KELUAR="$WS/.task-plans"; PIDF="$KELUAR/kantor-agent.pid"; HTML="$KELUAR/kantor-agent.html"; LOG="$KELUAR/kantor-agent.log"
hidup() { [ -f "$PIDF" ] && P="$(cat "$PIDF")" && ps -p "$P" -o command= 2>/dev/null | grep -q kantor-agent.py; }
if [ "$BERHENTI" = 1 ]; then
  if hidup; then kill "$P" && echo "Penulis Kantor Agent (pid $P) dihentikan."; else echo "Tidak ada penulis Kantor Agent yang hidup."; fi
  rm -f "$PIDF"; exit 0
fi
command -v python3 >/dev/null 2>&1 || { echo "kantor-agent: butuh python3 (3.8+)" >&2; exit 2; }
mkdir -p "$KELUAR" && cp "$DIR/kantor-agent.template.html" "$HTML" || exit 2
buka() {
  [ "$BUKA" = 1 ] || return 0
  if command -v open >/dev/null 2>&1; then open "$HTML"; elif command -v xdg-open >/dev/null 2>&1; then xdg-open "$HTML" >/dev/null 2>&1; fi
}
if [ "$SEKALI" = 1 ]; then
  python3 "$DIR/kantor-agent.py" --workspace "$WS" --proyek-dir "$PROYEK" --sekali || exit $?
  echo "Kantor Agent: $HTML"; buka; exit 0
fi
if hidup; then
  echo "Penulis Kantor Agent sudah jalan (pid $P); tidak menyalakan yang kedua."
else
  nohup python3 "$DIR/kantor-agent.py" --workspace "$WS" --proyek-dir "$PROYEK" --loop "$INTERVAL" --sepi-menit "$SEPI" --log "$LOG" >/dev/null 2>&1 &
  echo "Penulis Kantor Agent menyala (pid $!)."
fi
echo "Kantor Agent: $HTML  (hentikan: kantor-agent.sh --berhenti)"
buka

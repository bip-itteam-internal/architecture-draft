#!/usr/bin/env bash
# papan-sesi.sh — cermin papan-sesi.ps1 untuk mac/linux: TABEL saja (tanpa HTML). Butuh python3.
# pakai: papan-sesi.sh [workspace=.] [jam_basi=24] [--bersihkan]
command -v python3 >/dev/null 2>&1 || { echo "butuh python3" >&2; exit 2; }
ws="${1:-$PWD}"; jam="${2:-24}"; bersih=0; for a in "$@"; do [ "$a" = "--bersihkan" ] && bersih=1; done
python3 - "$ws" "$jam" "$bersih" <<'PY'
import json, os, sys, glob, datetime
ws, jam, bersih = sys.argv[1], float(sys.argv[2]), sys.argv[3] == "1"
d = os.path.join(ws, ".task-plans", "sesi"); now = datetime.datetime.now(datetime.timezone.utc)
def p(s):
    try: return datetime.datetime.fromisoformat(s.replace("Z", "+00:00"))
    except Exception: return None
rows = []
for f in sorted(glob.glob(os.path.join(d, "*.json"))):
    try: s = json.load(open(f, encoding="utf-8"))
    except Exception: continue
    t = p(s.get("terakhir") or "")
    if bersih and s.get("status") == "selesai" and t and (now - t).days > 7:
        os.remove(f); continue
    basi = s.get("status") == "aktif" and t and (now - t).total_seconds() > jam * 3600
    keadaan = "BASI" if basi else ("AKTIF" if s.get("status") == "aktif" else "selesai")
    senyap = "" if not t else ("%dm" % ((now - t).seconds // 60) if (now - t).total_seconds() < 3600 else "%dj" % ((now - t).total_seconds() // 3600) if (now - t).total_seconds() < 172800 else "%dh" % (now - t).days)
    rows.append((0 if keadaan == "AKTIF" else 1 if keadaan == "BASI" else 2, s.get("terakhir", ""), keadaan, (s.get("session_id") or "")[:8], s.get("tahap", ""), (s.get("task") or "")[:40], s.get("branch", ""), s.get("worktree", ""), senyap))
rows.sort(key=lambda r: (r[0], r[1]), reverse=False)
n_aktif = sum(1 for r in rows if r[2] == "AKTIF"); n_basi = sum(1 for r in rows if r[2] == "BASI")
print("PAPAN SESI  aktif %d · basi(>%gj) %d · total %d" % (n_aktif, jam, n_basi, len(rows)))
if not rows: print("Belum ada sesi terdaftar. Hook SessionStart menulisnya; pastikan kit >= 1.15.0 sudah di-init dan sesi di-restart."); sys.exit(0)
print("%-8s %-9s %-14s %-40s %-32s %-40s %s" % ("KEADAAN", "SESI", "TAHAP", "TASK", "BRANCH", "WORKTREE", "SENYAP"))
for r in rows: print("%-8s %-9s %-14s %-40s %-32s %-40s %s" % r[2:])
PY

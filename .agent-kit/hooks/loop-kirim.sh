#!/usr/bin/env bash
# loop-kirim.sh — cermin loop-kirim.ps1 (alasan desain di sana). BEST-EFFORT, selalu exit 0.
# pakai: loop-kirim.sh <jenis> '<json bagian>' [konfig=~/.agent-kit/loop-ingest.json]
# Butuh: curl, openssl; python3 untuk JSON (tanpa python3: no-op).
jenis="${1:-}"; data="${2:-{}}"; konfig="${3:-$HOME/.agent-kit/loop-ingest.json}"
[ -n "$jenis" ] && [ -f "$konfig" ] || exit 0
command -v python3 >/dev/null 2>&1 && command -v curl >/dev/null 2>&1 && command -v openssl >/dev/null 2>&1 || exit 0
dir="$(dirname "$konfig")"; gagal="$dir/loop-ingest.gagal"; loginf="$dir/gh-login.txt"
# jeda 10 menit setelah 3 kegagalan beruntun
if [ -f "$gagal" ]; then
  if python3 - "$gagal" <<'PY' ; then exit 0; fi
import json,sys,datetime
try:
    g=json.load(open(sys.argv[1])); n=int(g.get("beruntun",0)); t=g.get("terakhir","")
    d=datetime.datetime.fromisoformat(t.replace("Z","+00:00"))
    sys.exit(0 if n>=3 and (datetime.datetime.now(datetime.timezone.utc)-d).total_seconds()<600 else 1)
except Exception: sys.exit(1)
PY
fi
login=""; [ -f "$loginf" ] && login="$(tr -d '[:space:]' < "$loginf")"
if [ -z "$login" ] && command -v gh >/dev/null 2>&1; then login="$(gh api user --jq .login 2>/dev/null)"; [ -n "$login" ] && printf '%s' "$login" > "$loginf"; fi
email="$(git config --global user.email 2>/dev/null)"; nama="$(git config --global user.name 2>/dev/null)"
badan="$(python3 - "$konfig" "$jenis" "$data" "$login" "$email" "$nama" <<'PY'
import json,sys,datetime,socket
k=json.load(open(sys.argv[1])); jenis=sys.argv[2]
try: bagian=json.loads(sys.argv[3])
except Exception: sys.exit(1)
kunci={"sesi":"sesi","brief":"brief","judge":"judge","loop":"pr"}.get(jenis.split(".")[0])
if not kunci: sys.exit(1)
m={"versi":1,"jenis":jenis,"waktu":datetime.datetime.now(datetime.timezone.utc).isoformat().replace("+00:00","Z"),
   "mesin":k.get("mesin") or socket.gethostname(),
   "orang":{"login":sys.argv[4] or None,"email":sys.argv[5] or None,"name":sys.argv[6] or None},kunci:bagian}
print(json.dumps(m,ensure_ascii=False,separators=(",",":")))
PY
)" || exit 0
url="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("url",""))' "$konfig")"
secret="$(python3 -c 'import json,sys;print(json.load(open(sys.argv[1])).get("secret","").strip())' "$konfig")"
[ -n "$url" ] && [ -n "$secret" ] || exit 0
hex="$(printf '%s' "$badan" | openssl dgst -sha256 -hmac "$secret" | sed 's/^.* //')"
kode="$(curl -s -o /dev/null -w '%{http_code}' --max-time 3 -X POST -H 'Content-Type: application/json; charset=utf-8' -H "X-Loop-Signature-256: sha256=$hex" --data-binary "$badan" "$url" 2>/dev/null || echo "000")"
case "$kode" in 2*) rm -f "$gagal";; *)
  n=1; [ -f "$gagal" ] && n=$(( $(python3 -c 'import json,sys;print(int(json.load(open(sys.argv[1])).get("beruntun",0)))' "$gagal" 2>/dev/null || echo 0) + 1 ))
  printf '{"beruntun":%d,"terakhir":"%s","kode":"%s"}' "$n" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" "$kode" > "$gagal";; esac
exit 0

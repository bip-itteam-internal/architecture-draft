#!/usr/bin/env bash
# cek-lock-receipt.sh - padanan cek-lock-receipt.ps1 (lihat berkas itu untuk alasan dan format).
# Konfig opt-in per mesin: ~/.agent-kit/prod-ssh.json  { "host": "<user>@<alamat>", "key": "<path kunci>" }
# Satu baris ke stdout; exit selalu 0; tanpa konfig/ssh/python hasilnya "tidak bisa dicek", bukan "aman".
dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
konfig="${1:-$HOME/.agent-kit/prod-ssh.json}"
gagal() { echo "Receipt lock tidak bisa dicek ($1), jangan diasumsikan aman"; exit 0; }

py=""
for c in python3 python; do command -v "$c" >/dev/null 2>&1 && { py="$c"; break; }; done
[ -n "$py" ] || gagal "python tidak ditemukan"
[ -f "$konfig" ] || gagal "belum ada $konfig"
host="$("$py" -c 'import json,sys;print(json.load(open(sys.argv[1])).get("host",""))' "$konfig" 2>/dev/null)"
key="$("$py" -c 'import json,sys;print(json.load(open(sys.argv[1])).get("key",""))' "$konfig" 2>/dev/null)"
[ -n "$host" ] && [ -n "$key" ] || gagal "prod-ssh.json tanpa host/key"

fakta="$(ssh -o BatchMode=yes -o ConnectTimeout=15 -i "$key" "$host" 'bash -s' < "$dir/cek-lock-receipt.remote.sh" 2>/dev/null)" || gagal "ssh ke server prod gagal"
[ -n "$fakta" ] || gagal "ssh ke server prod gagal"
hasil="$(printf '%s\n' "$fakta" | "$py" "$dir/cek-lock-receipt.py" 2>/dev/null | tail -1)"
[ -n "$hasil" ] || gagal "keputusan gagal dihitung"
echo "$hasil"
exit 0

#!/bin/bash
# Dijalankan DI SERVER prod lewat `ssh ... bash -s` (stdin) oleh cek-lock-receipt.ps1/.sh.
# BACA-SAJA: hanya find/findOne. Mencetak SATU baris JSON fakta; keputusan aman/tidak ada di
# cek-lock-receipt.py (satu tempat). Tak menulis berkas apa pun di server.
CID=$(docker ps --filter name=Integration-Service --format '{{.ID}}' | head -1)
U=$(docker exec Integration-MongoDB printenv MONGO_INITDB_ROOT_USERNAME 2>/dev/null)
P=$(docker exec Integration-MongoDB printenv MONGO_INITDB_ROOT_PASSWORD 2>/dev/null)
JS=$(cat <<'EOF'
const num = (v) => (v && v.low !== undefined) ? (v.low >>> 0) + v.high * 4294967296 : Number(v || 0);
const ms = (d) => d ? d.getTime() : null;
const W = db.getSiblingDB('workers'), D = db.getSiblingDB('integration_db');
const lk = W.worker_locks.findOne({_id: 'lock:receipt-sync'});
const cfg = W.worker_configs.findOne({_id: 'receipt-sync'});
const runs = D.receipt_sync_runs.find({}, {started_at: 1, finished_at: 1}).sort({started_at: -1}).limit(5).toArray();
print(JSON.stringify({
  sekarang_ms: Date.now(),
  container_id: CID,
  lock: lk ? {owner: lk.owner, kedaluwarsa_ms: ms(lk.expires_at)} : null,
  konfig: cfg ? {jadwal: cfg.schedule, timeout_ms: Math.round(num(cfg.timeout) / 1e6), aktif: cfg.enabled !== false} : null,
  putaran: runs.map(r => ({mulai_ms: ms(r.started_at), selesai_ms: ms(r.finished_at)}))
}));
EOF
)
docker exec Integration-MongoDB mongosh -u "$U" -p "$P" --authenticationDatabase admin --quiet --eval "const CID='${CID}'; ${JS}" 2>/dev/null | grep '^{' | tail -1

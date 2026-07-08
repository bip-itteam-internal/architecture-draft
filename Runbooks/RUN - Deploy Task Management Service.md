> **Status:** ⚠️ Implemented (prosedur diturunkan & terverifikasi dari deploy **dev** 2026-07-08 dengan migrasi data nyata; nilai host/creds prod diisi saat eksekusi. Belum dijalankan di prod.)

## Tujuan

Men-deploy service **task-management** bip-erp ke lingkungan baru (khususnya **produksi**) tanpa mengulang jebakan config yang ditemui saat deploy dev. Grounded ke [[Microservices - Task Management Service]].

## Kapan dipakai

- Cut-over produksi dari BE standalone lama (`bharata-task-manager-be`) ke service bip-erp.
- Setup task-management di environment bip-erp baru.

## Prasyarat

- Stack bip-erp jalan (gateway, employee-service, file-service, notification-service, MinIO). Lihat [[CORE - API Master Gateway]].
- Akses `.env` VM prod + izin `docker compose`.
- (Bila migrasi data) akses ke mongo/MinIO task-manager lama.

---

## 1. Env `.env` di VM prod (paling sering jadi masalah)

Var per-service (`FILE_MODULE_URL`, `NOTIFICATION_MODULE_URL`, `MONGO_URI`, dst.) sudah tertulis di `docker-compose.yml`; yang **wajib kamu isi di `.env`**:

| Var | Catatan |
|---|---|
| **`MONGO_TASK_MANAGEMENT_DB=task_management_db`** | 🔴 KRITIS. Tanpa ini `MONGO_DB` kosong → `client.Database("")` → **semua read gagal "find failed"** (ping tetap sukses, service hidup tapi rusak senyap). Guard `main.go` kini menolak start bila kosong. |
| **`MONGO_URI_ERP`** + **`DB_NAME_ERP=employee_db`** | Baca `employee_db` (nama assignee, validasi divisi, cari supervisor/admin). Pakai replica-set **internal** employee-mongo, mis. `mongodb://$MONGO_ROOT_USER:$MONGO_ROOT_PASSWORD@employee-mongo-primary:27017,employee-mongo-secondary:27017/?replicaSet=rs-employee&authSource=admin`. JANGAN IP eksternal. Lihat [[Microservices - Employee Service]]. |
| **`TASK_MANAGEMENT_MODULE_URL`** (env **gateway**) | 🔴 Bila tak ada, **gateway PANIC** (`ValidateInternalURL`) → **SELURUH ERP down**. Wajib ada sebelum deploy. |
| **`NOTIFICATION_SERVICE_KEY`** | Harus **identik** dengan yang dipakai notification-service (di dev pernah placeholder → FCM/inbox 401). Beda = push gagal (best-effort, tak nge-block). Lihat [[Microservices - Notification Service]]. |
| `MINIO_TASK_KEY`, `MINIO_TASK_READ_KEY` | Attachment via file-service (prefix `task/`). Lihat [[Microservices - File Service]]. |
| `INTERNAL_GATEWAY_KEY`, `JWT_SECRET`, `MONGO_ROOT_USER/PASSWORD`, `MINIO_*` | Standar; konsisten se-stack. |

## 2. Deploy service

```bash
docker compose up -d --force-recreate task-management-service
```
`--force-recreate` **wajib**: perubahan env/compose (termasuk publish port) tak terbaca hot-reload. Cek log:
```bash
docker logs Task-Management-Service --tail 40 | grep -iE "Connected to MongoDB|\[ERP\]"
```
Harus: `Connected to MongoDB: task_management_db` (ADA namanya) + `[ERP] connected to employee_db (read-only)`.

## 3. Database (task_management_db)

Container dedicated `task-management-mongo-db` (pola database-per-service). **Bila prod punya data task-manager lama**, migrasi:

```bash
# (di host yg menjangkau mongo lama) dump — pakai --user agar izin volume host tak menolak
mkdir -p /tmp/tm-dump
docker run --rm --network host --user "$(id -u):$(id -g)" -v /tmp/tm-dump:/dump mongo:latest \
  mongodump --uri="mongodb://<user>:<pass>@<mongo-lama>:27017/<db-lama>?authSource=admin" --out=/dump
# restore ke container prod, rename db → task_management_db
docker cp /tmp/tm-dump Task-Management-MongoDB:/tmp/tm-dump
docker exec Task-Management-MongoDB mongorestore -u <MONGO_ROOT_USER> -p <MONGO_ROOT_PASSWORD> \
  --authenticationDatabase admin --nsFrom="<db-lama>.*" --nsTo="task_management_db.*" /tmp/tm-dump
```

**Normalisasi audit lama (WAJIB bila migrasi):** BE lama simpan `detail` sebagai **objek** + field `createdAt` (camelCase); skema baru `Detail string` + `created_at`. Tanpa normalisasi, `/tasks/:id/history` & `/audits` bisa **500 "cursor error"**.
```bash
docker exec Task-Management-MongoDB mongosh -u <U> -p <P> --authenticationDatabase admin --quiet --eval '
const c = db.getSiblingDB("task_management_db").audits;
c.find({}).forEach(a => { const s={},u={};
  if (a.createdAt!==undefined && a.created_at===undefined){s.created_at=a.createdAt;u.createdAt="";}
  if (a.detail!==null && typeof a.detail==="object" && !(a.detail instanceof Date)){s.detail=JSON.stringify(a.detail);}
  const up={}; if(Object.keys(s).length)up.$set=s; if(Object.keys(u).length)up.$unset=u;
  if(Object.keys(up).length)c.updateOne({_id:a._id},up);
});'
```

## 4. WebSocket ingress (untuk realtime FE)

Port service dipublish (sudah di compose). Tambah **rute reverse-proxy** yang mem-front domain gateway (prosedur & contoh nginx lengkap: `services/task-management/WEBSOCKET.md`):
```nginx
location /ws/task-management {
    proxy_pass         http://<task-management-service-host>:6977/ws;   # map ke /ws
    proxy_http_version 1.1;
    proxy_set_header   Upgrade    $http_upgrade;
    proxy_set_header   Connection "upgrade";
    proxy_read_timeout 3600s;
}
```
Tanpa rute ini app tetap jalan (FE polling) tapi tak ada live push. Verifikasi: handshake token valid → `101 Open`; tanpa token → ditolak.

## 5. Attachment / MinIO

- Bucket prod `app-bucket`, key `MINIO_TASK_KEY`/`READ_KEY`, prefix `task/`. Batas **4 MB/file** (file-service; FE sudah selaras).
- **Bila mau preview file lampiran LAMA jalan**, mirror objek dari MinIO lama → prod (path di DB sudah `task/<space>/<task>/<att>-<file>`, cocok tanpa ubah data):
  ```bash
  docker run --rm --network host \
    -e MC_HOST_src="http://<KEY>:<SECRET>@<minio-lama>:9000" \
    -e MC_HOST_dst="http://<KEY>:<SECRET>@<minio-prod>:9000" \
    minio/mc mirror --overwrite src/<bucket>/task/ dst/app-bucket/task/
  ```

## 6. Role / RBAC di ERP prod

3-role (admin > supervisor > staff) diturunkan dari **nilai** `system_authentication.system_roles` **per-divisi**:
- **supervisor** = `<divisi>: "supervisor"` (mengelola divisinya).
- **admin (sekretaris)** = `<divisi>: "admin"` (lintas SEMUA divisi).
- selain itu **staff**.

Pastikan role di ERP prod diisi sesuai ini, jika tidak semua orang jadi staff.

## 7. Frontend prod (`bharata-task-manager-fe`, branch `feature/gateway-cutover`)

- `NEXT_PUBLIC_ERP_GATEWAY_URL` → gateway prod
- `NEXT_PUBLIC_WS_URL` → `wss://<gateway-prod>/ws/task-management`
- `NEXT_PUBLIC_ERP_LOGIN_URL` → login ERP prod
- Gateway CORS: allow origin FE prod (`task.bharatainternasional.com`).
- Detail sisi FE: [[APP - Dynamic Task Tracker]].

## 8. Urutan cut-over aman

1. Set `.env` prod (§1) → deploy service (§2) → verifikasi (§9).
2. Migrasi data (§3) + attachment (§5) bila perlu.
3. Rute ingress WS (§4).
4. **Bekukan tulis BE lama**, arahkan FE prod ke gateway.
5. Verifikasi prod stabil beberapa hari → baru **decommission** BE/mongo/MinIO lama (arsipkan branch lama jadi tag dulu).

## 9. Verifikasi (E2E, via gateway)

Login → cek: `/spaces` & `/tasks/filter` (ada data, bukan 500), `/me` (role benar), `/tasks/:id/history`, `/users` & `/departments` (terisi), upload attachment (>4MB → **413**), WS handshake (token→`101`, tanpa token→ditolak). **Uji akun ber-role admin** (lintas-divisi) + **supervisor** (divisinya) + **staff**.

## Troubleshooting (gejala → akar → fix)

| Gejala | Akar | Fix |
|---|---|---|
| `/spaces`,`/tasks/filter` **500 "find failed"** | `MONGO_TASK_MANAGEMENT_DB` kosong → db name `""` | Set var, `--force-recreate`. Log `Connected to MongoDB:` (kosong) = tanda ini |
| Seluruh ERP down pasca-deploy | `TASK_MANAGEMENT_MODULE_URL` tak ada di gateway → panic `ValidateInternalURL` | Isi var, restart gateway |
| Nama assignee = ID, `/users`,`/departments` kosong | `MONGO_URI_ERP`/`DB_NAME_ERP` tak diset → `[ERP] ... degraded` | Isi var (replica-set internal), recreate |
| `/tasks/:id/history` / `/audits` **500 "cursor error"** | Audit lama `detail` objek / `createdAt` camelCase | Normalisasi audit (§3) |
| FCM/inbox tak sampai | `NOTIFICATION_SERVICE_KEY` beda dgn notification-service | Samakan key; best-effort (tak nge-block) |
| WS tak connect dari FE | Rute ingress `/ws/task-management` belum ada | Tambah rute nginx (§4) |
| Port 6977 tak reachable | Deploy tak recreate container | `docker compose up -d --force-recreate` |

## Dokumen Terkait

- [[Microservices - Task Management Service]] — implementasi BE (endpoint, RBAC, SLA)
- [[APP - Dynamic Task Tracker]] — sisi FE
- [[CORE - API Master Gateway]] · [[Microservices - Employee Service]] · [[Microservices - File Service]] · [[Microservices - Notification Service]]

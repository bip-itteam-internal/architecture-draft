## Deskripsi

*Kumpulan **runbook** operasional bip-erp — langkah konkret untuk tugas berulang. Runbook "tambah service baru" **grounded** dari [[HOMEPAGE]] + pola kode; sisanya menunjuk ke dok yang ada, detail langkah (TBD) bila belum terdokumentasi penuh.*

- **Status**: ⚠️ Sebagian — runbook service-baru lengkap; restore/rotasi/incident = pointer + TBD

## Runbook 1 — Tambah microservice baru (grounded)

Pola dari [[HOMEPAGE]] + [[ADR - 0002 Database-per-Service]]:
1. `bip-erp/services/<svc>/` → `go mod init '<svc>'`.
2. Link shared-library: `go mod edit -replace github.com/bharata/shared-library=../../shared-library` → `go get github.com/bharata/shared-library@v0.0.0`.
3. Salin `services/.template` (atau service mirip) → `main.go` + `Dockerfile`; daftarkan rute via `RegisterRoutes(app)`; akses Mongo via `mongodb.GetCollection(...)`.
4. Tambah service + Mongo container + volume di `docker-compose.yml` (replikasi blok service yang ada).
5. Tambah `<SVC>_MODULE_URL` ke `api-gateway/main.go` hashmap `InternalURL` + env gateway di compose.
6. Tambah variabel ke `.env` / `.env.example` (`<SVC>_SERVICE_PORT`, `MONGO_<SVC>_DB`).
7. Identitas user dibaca dari header `BIP-*` di belakang [[CORE - API Master Gateway]]; RBAC via `system_roles`.

> Contoh penerapan lengkap (path eksak): rencana [[ERPGo - Form Builder]] §Rencana Implementasi.

## Runbook 2 — Deploy / rilis

- Push ke `main` → **deploy otomatis** (GitHub Actions self-hosted runner; Codemagic untuk mobile). Alur branch: feature → `dev` (test) → `main` (prod). Detail: [[IT - CI-CD]] · [[SCRUM SPECS]].
- (Langkah rollback manual = TBD)

## Runbook 3 — Backup & restore DB

- Backup tersimpan di `mongo-backup` / `minio-backup`. Prosedur restore detail: [[IT - Backup & DR]] (langkah step-by-step = TBD bila belum ada).

## Runbook 4 — Rotasi secret / incident response

- (TBD) Rotasi `INTERNAL_GATEWAY_KEY` / `JWT_SECRET` / kredensial Mongo — koordinasi dengan [[IT - Security]].
- (TBD) Incident response + jalur eskalasi → [[IT - Monitoring System]], [[REF - Ownership & RACI]].

## Dokumen Terkait

- [[HOMEPAGE]] · [[IT - CI-CD]] · [[IT - Backup & DR]] · [[IT - Security]] · [[IT - Monitoring System]]
- [[ADR - 0002 Database-per-Service]] · [[CORE - API Master Gateway]] · [[IT - Environment Inventory]]

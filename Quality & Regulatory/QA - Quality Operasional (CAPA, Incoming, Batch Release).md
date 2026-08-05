## Deskripsi

*Workspace ERP operasional untuk divisi **Quality** (branch `feature/workspace-position`). Tiga register inti P1: **Register CAPA & Temuan Audit** (temuan internal/BPOM + tindakan korektif, dipakai bersama R&D), **Incoming Inspection** (pemeriksaan bahan/kemasan datang, lulus/tolak + tenggat retur), dan **Antrean Release Batch** (batch menunggu keputusan release/hold). Memberi jejak kerja mutu di ERP sehingga "berapa penjualan tertahan & kerugian dicegah" terlihat. Dashboard Mutu, IPC/Pre-Check/CPPB (form batch-record), checklist GMP/kalibrasi/storage, dan Komplain (dari reviews) belum termasuk.*

- **Stack**: Go (Fiber, di-host di employee-service) + MongoDB (`quality_capa`, `quality_incoming`, `quality_batch_release`) + JWT/`system_roles`; frontend Next.js (App Router, TanStack Query).
- **Path di repo**:
  - Backend: `bip-erp/services/employee/{quality_capa.go,quality_incoming.go,quality_batch.go}` (`RegisterQualityRoutes`) · model `QualityCAPA`/`QualityIncoming`/`QualityBatchRelease` di `.../models/employee/models.go` · collection senama · RBAC `RequireQualityStaff`/`RequireQualitySupervisor` di `.../common/roles.go`. Department `quality` **sudah ada** di seed.
  - Frontend: `erp-frontend/src/app/(main)/quality/{capa,incoming,batch-release}/page.tsx` · `src/features/quality/{capa,incoming,batch,shared}/*` · menu di `sidebar.tsx` (blok `quality`) · gating di `proxy.ts`.
- **Status**: ⚠️ Implemented (ada catatan). Tiga register + unggah PDF **live di kode** (Go build + FE typecheck/eslint lolos), **belum diverifikasi runtime**. Sisanya (Dashboard, IPC/CPPB/Pre-Check, checklist, Komplain) belum.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Staf Quality (QA/QC) | department `quality` | `quality:staff` — kelola CAPA/inspeksi/batch | Web ERP |
| Supervisor Quality | department `quality` | `quality:supervisor` — termasuk hapus; menu KPI | Web ERP |

- **Tujuan**: satu tempat mencatat temuan & tindak lanjut, memutuskan lulus/tolak bahan, dan me-release/hold batch — dengan alert keterlambatan.

## Fitur (Sudah Diimplementasikan)

Dipanggil FE lewat `/api/employee/quality/*`. Semua GET/POST/PUT gate `RequireQualityStaff`, DELETE gate `RequireQualitySupervisor`.

**Register CAPA & Temuan Audit** (`quality_capa.go`, collection `quality_capa`):
- `GET/POST /quality/capa`, `GET/PUT/DELETE /quality/capa/:id`. Filter `?source=`&`?severity=`&`?status=`.
- Model `QualityCAPA`: `title`, `source` (Internal/BPOM/Audit Eksternal/HACCP/GMP), `severity` (Major/Minor/Observasi), `status` (Terbuka/Proses/Selesai), `pic`, `due_date`, `corrective_action`, `notes`, `file_object`+`file_name` (bukti penutupan). **Alert tenggat H-7/Telat** di UI. **Dipakai bersama R&D** (temuan audit eksternal) — lihat [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]].

**Incoming Inspection Bahan Kemas** (`quality_incoming.go`, collection `quality_incoming`):
- `GET/POST /quality/incoming`, `GET/PUT/DELETE /quality/incoming/:id`. Filter `?supplier=`&`?status=`.
- Model `QualityIncoming`: `material`, `supplier`, `status` (Menunggu/Lulus/Tolak), `reason`, `pic`, `received_date`, `return_deadline`, `notes`, file. **Alert "Telat" bila status Menunggu > 3 hari** sejak `received_date`.

**Antrean Release Batch** (`quality_batch.go`, collection `quality_batch_release`):
- `GET/POST /quality/batch-releases`, `GET/PUT/DELETE /quality/batch-releases/:id`. Filter `?product=`&`?status=`.
- Model `QualityBatchRelease`: `batch_number`, `product`, `status` (Menunggu/Release/Hold), `doc_status` (Lengkap/Belum Lengkap), `pic`, `produced_date`, `notes`, file. **Umur antrean (jam) + badge bila Menunggu > 24 jam** dari `produced_date`.

**Unggah PDF** — reuse `POST /api/employee/upload` (`minio.UploadSingleHandler`); FE `features/quality/shared/upload.ts`.

**RBAC & sidebar**: role key `quality` (`quality:staff|supervisor`) — department `quality` sudah di-seed sebelumnya. Menu blok `quality` kini berisi 3 register + KPI (KPI tetap supervisor-only). Lihat [[CORE - RBAC dan Permission Set]].

## Belum Diimplementasikan / Catatan

- **Dashboard Mutu** (P1, `/quality/dashboard`) — agregasi QA release time, defect rate, komplain, temuan terbuka; **belum**.
- **IPC, Pre-Check Batch Record, Dokumen CPPB** (form terkait Dokumen Produksi Batch/L. Hasil Produksi) — **belum**; perlu integrasi ke modul Manufacture.
- **Checklist GMP / Kalibrasi / Kontrol Ruang Penyimpanan** (P2/P3) — **belum**.
- **Komplain & Rating Produk** (P1, `Ada sebagian`) — sumbernya `/integration/reviews`; belum difilter-mutu di modul Quality.
- **Hosting di employee-service** (TBD) — sama seperti Legal/R&D; ekstrak ke service `quality` bila beban tumbuh.
- **Verifikasi runtime**: build/typecheck lolos; smoke-test E2E belum — perlu redeploy `docker-compose.dev.yml`.

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — host endpoint `/quality/*`, Mongo.
- [[CORE - API Master Gateway]] — meneruskan `/api/employee/quality/*` + header `BIP-*`.
- [[CORE - RBAC dan Permission Set]] — role key `quality`.
- [[APP - Web ERP]] — modul frontend `quality` (3 register + KPI).
- [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]] — berbagi Register CAPA.

## Dokumen Terkait

- [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]]
- [[QA - Register Perizinan & Sertifikasi]]
- [[Microservices - Employee Service]]

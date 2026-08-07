## Deskripsi

*Workspace ERP operasional untuk divisi **Quality** (branch `feature/workspace-position`). Tiga register inti P1: **Register CAPA & Temuan Audit** (temuan internal/BPOM + tindakan korektif, dipakai bersama R&D), **Incoming Inspection** (pemeriksaan bahan/kemasan datang, lulus/tolak + tenggat retur), dan **Antrean Release Batch** (batch menunggu keputusan release/hold). Memberi jejak kerja mutu di ERP sehingga "berapa penjualan tertahan & kerugian dicegah" terlihat. Dashboard Mutu, IPC/Pre-Check/CPPB (form batch-record), checklist GMP/kalibrasi/storage, dan Komplain (dari reviews) belum termasuk.*

- **Stack**: Go (Fiber, di-host di employee-service) + MongoDB (`quality_capa`, `quality_incoming`, `quality_batch_release`, `quality_complaint`, `quality_rm_check`) + JWT/`system_roles`; frontend Next.js (App Router, TanStack Query).
- **Path di repo**:
  - Backend: `bip-erp/services/employee/{quality_capa.go,quality_capa_approval.go,quality_incoming.go,quality_batch.go,quality_complaint.go,quality_rm_check.go}` (`RegisterQualityRoutes`) · model `QualityCAPA`/`QualityIncoming`/`QualityBatchRelease`/`QualityComplaint`/`QualityRMCheck` (+ `CAPAApproval`) di `.../models/employee/models.go` · collection senama · RBAC `RequireQualityStaff`/`RequireQualitySupervisor` (+ `RequireCAPAApprover`, `RequireMarketingStaff`, `RequireQualityOrMarketing`, `HasQualityRole`) di `.../common/roles.go`. Department `quality` **sudah ada** di seed.
  - Frontend: `erp-frontend/src/app/(main)/quality/{capa,incoming,batch-release,komplain,pengecekan-rm}/page.tsx` · input marketing `src/app/(main)/icc/komplain-qc/page.tsx` · `src/features/quality/{capa,incoming,batch,complaint,rm-check,shared}/*` · menu di `sidebar-menus.tsx` (blok `quality` & `icc`) · gating di `proxy.ts`.
- **Status**: ⚠️ Implemented (ada catatan). Lima register + unggah PDF + alur approval CAPA + komplain QC marketing + pengecekan RM **live di kode** (Go build + FE typecheck/eslint/test lolos), **belum diverifikasi runtime**. Sisanya (Dashboard, IPC/CPPB/Pre-Check, checklist) belum.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Staf Quality (QA/QC) | department `quality` | `quality:staff` — kelola CAPA/inspeksi/batch; validasi komplain; cek RM; finalisasi QA CAPA | Web ERP |
| Supervisor Quality | department `quality` | `quality:supervisor` — termasuk hapus; menu KPI | Web ERP |
| Staf Marketing | department Kyura/Beauty Hacks (role `kyura`/`beauty_hacks`) / adv `insentive` | `RequireMarketingStaff` — input komplain ke QC (`/icc/komplain-qc`) | Web ERP |
| Admin Produksi / Admin Warehouse | modul `manufacture`/`warehouse` | approver alur CAPA (`RequireCAPAApprover`) | Web ERP |

- **Tujuan**: satu tempat mencatat temuan & tindak lanjut, memutuskan lulus/tolak bahan, dan me-release/hold batch — dengan alert keterlambatan.

## Fitur (Sudah Diimplementasikan)

Dipanggil FE lewat `/api/employee/quality/*`. Semua GET/POST/PUT gate `RequireQualityStaff`, DELETE gate `RequireQualitySupervisor`.

**Register CAPA & Temuan Audit** (`quality_capa.go`, collection `quality_capa`):
- `GET/POST /quality/capa`, `GET/PUT/DELETE /quality/capa/:id`. Filter `?source=`&`?severity=`&`?status=`.
- Model `QualityCAPA`: `title`, `source` (Internal/BPOM/Audit Eksternal/HACCP/GMP), `severity` (Major/Minor/Observasi), `status` (Terbuka/Proses/Selesai), `pic`, `due_date`, `corrective_action`, `notes`, `file_object`+`file_name` (bukti **penutupan**), `evidence_object`+`evidence_name` (bukti **temuan**, diunggah QA saat input). **Alert tenggat H-7/Telat** di UI. **Dipakai bersama R&D** (temuan audit eksternal) — lihat [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]].
- **Alur persetujuan CAPA** (`quality_capa_approval.go`): dimensi `approval_status` terpisah dari `status` — Draft → Diajukan → Menunggu Persetujuan QA → Disetujui; "Revisi" bila dikembalikan. Aksi: `PUT /quality/capa/:id/submit` (QA), `PUT .../approve` (Admin Produksi & Admin Warehouse, **dua-duanya** wajib Approve; slot diverifikasi per peran), `PUT .../finalize` (QA setujui/kembalikan). Approver gate `RequireCAPAApprover` (`IsCAPAProduksiApprover`/`IsCAPAWarehouseApprover`); tiga slot `CAPAApproval` (`approval_produksi`/`approval_warehouse`/`approval_qa`). FE gating cermin di `features/quality/capa/lib/capa-approval.ts`.

**Incoming Inspection Bahan Kemas** (`quality_incoming.go`, collection `quality_incoming`):
- `GET/POST /quality/incoming`, `GET/PUT/DELETE /quality/incoming/:id`. Filter `?supplier=`&`?status=`.
- Model `QualityIncoming`: `material`, `supplier`, `status` (Menunggu/Lulus/Tolak), `reason`, `pic`, `received_date`, `return_deadline`, `notes`, file. **Alert "Telat" bila status Menunggu > 3 hari** sejak `received_date`.

**Antrean Release Batch** (`quality_batch.go`, collection `quality_batch_release`):
- `GET/POST /quality/batch-releases`, `GET/PUT/DELETE /quality/batch-releases/:id`. Filter `?product=`&`?status=`.
- Model `QualityBatchRelease`: `batch_number`, `product`, `status` (Menunggu/Release/Hold), `doc_status` (Lengkap/Belum Lengkap), `pic`, `produced_date`, `notes`, file. **Umur antrean (jam) + badge bila Menunggu > 24 jam** dari `produced_date`.

**Komplain QC dari Marketing** (`quality_complaint.go`, collection `quality_complaint`):
- `GET /quality/complaints` (gate `RequireQualityOrMarketing`, filter `?status=`), `POST /quality/complaints` & `PUT /quality/complaints/:id` (gate `RequireMarketingStaff`; edit hanya selagi "Menunggu Validasi"), `PUT /quality/complaints/:id/validate` (gate `RequireQualityStaff`), `DELETE` (supervisor).
- Alur: **Marketing menginput** komplain yang menuding kesalahan QC (status "Menunggu Validasi") → **QC memvalidasi** verdict **Valid** (memang kesalahan QC) / **Ditolak** (bukan; alasan wajib). Model `QualityComplaint`: `title`, `description`, `product`, `sku`, `order_ref`, `severity`, `status`, `verdict`, `reason`, `validated_by`, `validated_at`, file.
- FE: input di workspace **ICC** (`/icc/komplain-qc`, marketing brand Kyura/Beauty Hacks), validasi di workspace **Quality** (`/quality/komplain`). `features/quality/complaint/*`.

**Pengecekan Raw Material** (`quality_rm_check.go`, collection `quality_rm_check`):
- `GET /quality/rm-checks`, `PUT /quality/rm-checks/:ref` (upsert status cek by `penerimaan_ref`) — gate `RequireQualityStaff`.
- Daftar **penerimaan barang procurement** ditarik FE (read-only) dari `GET /api/procurement/penerimaan-erp` — rute itu kini dibuka untuk QC via gate `aksesRM` (izin baca procurement **atau** `common.HasQualityRole`) di `services/procurement/main.go`. FE join penerimaan × status cek by id. Model `QualityRMCheck`: `penerimaan_ref`, `penerimaan_number`, `check_status` (Belum/OK/Bermasalah), `reason`, `pic`, `notes`, file. FE `/quality/pengecekan-rm`, `features/quality/rm-check/*`.

**Formula (lintas-modul, FE)** — menu Quality "Data Produksi WMS → **Formula**" membuka Gudang RM Manufacture dalam mode `?form=formula` (hanya tab Formula/BOM). Lihat [[Manufacture - Stock & Material Management]] / akses lintas-modul `TAB_WMS_QUALITY`.

**Unggah PDF** — reuse `POST /api/employee/upload` (`minio.UploadSingleHandler`); FE `features/quality/shared/upload.ts`.

**RBAC & sidebar**: role key `quality` (`quality:staff|supervisor`) — department `quality` sudah di-seed sebelumnya. Menu blok `quality` kini berisi 3 register + KPI (KPI tetap supervisor-only). Lihat [[CORE - RBAC dan Permission Set]].

## Belum Diimplementasikan / Catatan

- **Dashboard Mutu** (P1, `/quality/dashboard`) — agregasi QA release time, defect rate, komplain, temuan terbuka; **belum**.
- **IPC, Pre-Check Batch Record, Dokumen CPPB** (form terkait Dokumen Produksi Batch/L. Hasil Produksi) — **belum**; perlu integrasi ke modul Manufacture.
- **Checklist GMP / Kalibrasi / Kontrol Ruang Penyimpanan** (P2/P3) — **belum**.
- **Komplain QC dari Marketing** — ✅ live (lihat register di atas). **Komplain & Rating Produk dari review marketplace** (sumber `/integration/reviews`) tetap **belum** difilter-mutu di modul Quality (register `quality_complaint` khusus komplain internal marketing→QC, bukan review pembeli).
- **Hosting di employee-service** (TBD) — sama seperti Legal/R&D; ekstrak ke service `quality` bila beban tumbuh.
- **Verifikasi runtime**: build/typecheck lolos; smoke-test E2E belum — perlu redeploy `docker-compose.dev.yml`.

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — host endpoint `/quality/*`, Mongo.
- [[CORE - API Master Gateway]] — meneruskan `/api/employee/quality/*` + `/api/procurement/penerimaan-erp` + header `BIP-*`.
- [[CORE - RBAC dan Permission Set]] — role key `quality` + gate marketing/approver CAPA.
- [[APP - Web ERP]] — modul frontend `quality` (5 register + KPI) + input komplain di `icc`.
- [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]] — berbagi Register CAPA.
- [[Manufacture - Stock & Material Management]] — sumber penerimaan RM (procurement) & Formula/BOM Gudang RM.

## Dokumen Terkait

- [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]]
- [[QA - Register Perizinan & Sertifikasi]]
- [[Microservices - Employee Service]]

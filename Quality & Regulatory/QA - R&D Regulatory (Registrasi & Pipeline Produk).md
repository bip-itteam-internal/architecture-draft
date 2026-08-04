## Deskripsi

*Workspace ERP untuk posisi **R&D Regulatory** (branch `feature/workspace-position`). Dua register: **Register NIE / BPOM / Halal** (memantau proses registrasi izin edar produk baru sampai terbit, dengan alert bila lewat target) dan **Papan Pengembangan Produk Baru** (pipeline tahap ide → formulasi → trial → registrasi → siap launching). Memberi jejak kerja di ERP bagi divisi yang selama ini bekerja lewat spreadsheet. Simulasi HPP produk baru (ke Cost Control) dan Register CAPA audit eksternal (bersama Quality) belum termasuk.*

- **Stack**: Go (Fiber, di-host di employee-service) + MongoDB (`rnd_registration`, `rnd_product`) + JWT/`system_roles`; frontend Next.js (App Router, TanStack Query).
- **Path di repo**:
  - Backend: `bip-erp/services/employee/{rnd_regulatory.go,rnd_product.go}` (`RegisterRnDRoutes`) · model `RnDRegistration`/`RnDProduct` di `.../models/employee/models.go` · collection `rnd_registration`/`rnd_product` · RBAC `RequireRnDStaff`/`RequireRnDSupervisor` di `.../common/roles.go` · seed department `rnd` di `.../master_data.go`.
  - Frontend: `erp-frontend/src/app/(main)/rnd/{regulatory,product-development}/page.tsx` · `src/features/rnd/{regulatory,product,shared}/*` · menu `rnd` di `sidebar.tsx` · gating di `proxy.ts`.
- **Status**: ⚠️ Implemented (ada catatan). Kedua register + unggah PDF **live di kode** (Go build + FE typecheck/eslint lolos), **belum diverifikasi runtime**. Simulasi HPP & CAPA belum; Papan Pengembangan berupa **tabel bertahap** (belum kanban drag-drop).

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| R&D Regulatory | department `rnd` | `rnd:staff` — kelola registrasi & pipeline | Web ERP |
| R&D Regulatory Supervisor | department `rnd` | `rnd:supervisor` — termasuk hapus | Web ERP |

- **Tujuan**: satu layar untuk "izin apa yang sedang diproses & apakah lewat target", dan "produk apa di pipeline & tahap mana".
- **Pain point**: status registrasi & progres formulasi terpencar; keterlambatan target 14 hari kerja tak terlihat sampai ditanya.

## Fitur (Sudah Diimplementasikan)

**Register NIE / BPOM / Halal** (`rnd_regulatory.go`, collection `rnd_registration`), dipanggil FE lewat `/api/employee/rnd/*`:
- `GET/POST /rnd/registrations`, `GET/PUT /rnd/registrations/:id` (gate `RequireRnDStaff`), `DELETE` (gate `RequireRnDSupervisor`). Filter `?registration_type=`&`?status=`.
- Model `RnDRegistration`: `product`, `registration_type` (NIE/BPOM · Halal · SNI · Lainnya), `status` (Persiapan → Terdaftar → Review BPOM → Terbit/Ditolak), `number` (nomor NIE), `issuer`, `pic`, `register_date`, `target_date`, `expires_at` (ISO string), `notes`, `file_object`+`file_name`.
- **Alert target di UI**: badge `Telat {n}h`/`H-{n}` dari `target_date` selama status belum Terbit/Ditolak.

**Papan Pengembangan Produk Baru** (`rnd_product.go`, collection `rnd_product`):
- `GET/POST /rnd/products`, `GET/PUT /rnd/products/:id` (gate `RequireRnDStaff`), `DELETE` (gate `RequireRnDSupervisor`). Filter `?stage=`&`?status=`.
- Model `RnDProduct`: `product`, `stage` (Ide/Formulasi/Trial/Registrasi/Siap Launching), `status` (On Track/Telat/Selesai), `pic`, `start_date`, `target_date`, `notes`, `file_object`+`file_name` (hasil uji).

**Unggah PDF** — reuse endpoint generik `POST /api/employee/upload` (`minio.UploadSingleHandler`); FE `features/rnd/shared/upload.ts`. Pola identik dengan Legal — lihat [[QA - Register Perizinan & Sertifikasi]].

**RBAC & seed**: role key `rnd` pada tier `system_roles` (`rnd:staff|supervisor`), department `rnd` (nama `R&D Regulatory`) di-seed di `DefaultDepartments`. Lihat [[CORE - RBAC dan Permission Set]].

## Belum Diimplementasikan / Catatan

- **Simulasi HPP Produk Baru** (P1, route `/finance/cost-control/hpp?mode=simulasi`) — butuh data BOM/harga dari Cost Control/Manufacture; **belum**.
- **Register CAPA Audit Eksternal** (P2) — kini **sudah tersedia** lewat modul Quality (`/quality/capa`, sumber `Audit Eksternal/BPOM/HACCP`); R&D memakai register yang sama. Lihat [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]].
- **Papan Pengembangan** masih **tabel** dengan kolom tahap + badge, bukan **kanban drag-drop**; lead time vs target 14 hari kerja belum dihitung otomatis (baru badge target_date manual).
- **Hosting di employee-service** (TBD) — sama seperti Legal; ekstrak ke service `rnd` bila beban tumbuh. Lihat [[CORE - API Master Gateway]].
- **Verifikasi runtime**: build/typecheck lolos; smoke-test E2E (akun `rnd`, CRUD ke employee-service) belum — perlu redeploy `docker-compose.dev.yml`.
- **Overlap dengan Legal**: registrasi BPOM/Halal produk (R&D) vs izin perusahaan (Legal) beririsan; dijaga terpisah — R&D memantau proses per-produk sampai terbit, Legal memantau izin aktif perusahaan.

## Dependensi & Integrasi

- [[Microservices - Employee Service]] — host endpoint `/rnd/*`, Mongo, seed department.
- [[CORE - API Master Gateway]] — meneruskan `/api/employee/rnd/*` + header `BIP-*`.
- [[CORE - RBAC dan Permission Set]] — role key `rnd` pada tier `system_roles`.
- [[APP - Web ERP]] — modul frontend `rnd`.

## Dokumen Terkait

- [[QA - Register Perizinan & Sertifikasi]]
- [[Microservices - Employee Service]]
- [[CORE - RBAC dan Permission Set]]

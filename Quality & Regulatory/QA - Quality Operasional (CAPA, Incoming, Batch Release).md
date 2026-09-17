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
| Staf Marketing | department Kyura/Beauty Hacks (role `kyura`/`beauty_hacks`) / adv `insentive` | `RequireMarketingStaff` — input komplain ke QC (`/icc/komplain-qc`); mengubah hanya komplain **miliknya** selagi menunggu validasi (🟡 belum merge, lihat register Komplain QC) | Web ERP |
| Admin Produksi / Admin Warehouse | modul `manufacture`/`warehouse` | approver alur CAPA (`RequireCAPAApprover`) | Web ERP |

- **Tujuan**: satu tempat mencatat temuan & tindak lanjut, memutuskan lulus/tolak bahan, dan me-release/hold batch — dengan alert keterlambatan.

## Fitur (Sudah Diimplementasikan)

Dipanggil FE lewat `/api/employee/quality/*`. Semua GET/POST/PUT gate `RequireQualityStaff`, DELETE gate `RequireQualitySupervisor`, kecuali register Komplain QC yang gerbangnya dirinci di bagiannya.

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
- **Hanya pengaju yang boleh mengubah** (🟡 bip-erp branch `fix/komplain-qc-cek-pemilik` + erp-frontend branch `fix/komplain-qc-edit-pemilik`, **belum merge** per 2026-09-15). `PUT /quality/complaints/:id` diterima hanya dari **pengaju** (`metadata.created_by`, diisi sekali saat `POST` dan tak ditimpa saat diubah) atau **SPV/admin IT** (`common.IsITSupervisor`), lewat fungsi murni `bolehUbahKomplain`. Urutannya: tanpa `BIP-Employee-ID` dibalas **403** sebelum membaca Mongo; bukan pengaju **403** berkalimat, diperiksa **sebelum** status; komplain yang sudah divalidasi tetap **409**. Sebelumnya gerbangnya `RequireMarketingStaff` saja, sehingga staf marketing mana pun bisa menulis ulang komplain orang lain sementara komplain itu tetap tercatat, dan hasil validasinya tetap dikirim, atas nama pengaju asli.
  - Layar ICC **mencerminkan** aturan itu di `features/quality/complaint/lib/boleh-ubah.ts`: tombol Ubah hanya untuk yang berhak, komplain orang lain yang masih menunggu berbunyi "diajukan orang lain", dan tombol ikon Ubah kini berlabel. Cerminnya memakai `isSupervisorOrAdmin` (`it` supervisor **atau** admin, setara backend), bukan `isItSupervisor` yang hanya mengenal supervisor. Dua salinan aturan ini **disengaja**: layar hanya menyembunyikan tombol yang pasti ditolak, penolakan tetap di backend, dan keduanya diuji matriks kasus yang sama. Ubah keduanya bersama.
- Alur: **Marketing menginput** komplain yang menuding kesalahan QC (status "Menunggu Validasi") → **QC memvalidasi** verdict **Valid** (memang kesalahan QC) / **Ditolak** (bukan; alasan wajib). Model `QualityComplaint`: `title`, `description`, `product`, `sku`, `order_ref`, `severity`, `status`, `verdict`, `reason`, `validated_by`, `validated_at`, file.
- FE: input di workspace **ICC** (`/icc/komplain-qc`, marketing brand Kyura/Beauty Hacks), validasi di workspace **Quality** (`/quality/komplain`). `features/quality/complaint/*`.
- **Notifikasi menutup loop** (2026-09-15, `quality_complaint_notify.go`): saat Marketing menginput → inbox **`komplain-qc-diajukan`** ke **seluruh staf QC** perusahaan pengaju (ketuk ke `/quality/komplain`, memuat severity/produk untuk triase); saat QC memvalidasi → inbox **`komplain-qc-divalidasi`** ke **pengaju** (verdict + alasan, ketuk ke `/icc/komplain-qc`). Best-effort sesudah simpan. Sebelumnya alur **bisu** di kedua arah sehingga komplain menganggur (0 tersimpan di prod). Kategori & jebakan deploy di [[Microservices - Notification Service]] (employee-service + notification-service **naik bersama**); pemetaan [[APP - MyBharata]] menyusul (interim tampil "Sistem").
- 🟡 **Rencana satu pintu** ([[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]], diusulkan 2026-09-17, **belum ada kodenya**). Yang akan berubah pada register ini:
  - **Kategori tertutup** yang diterbitkan lewat endpoint baca, isinya ditetapkan tim QC (usulan: `dugaan_tidak_asli`, `segel_terbuka`, `isi_tidak_sesuai`, `kedaluwarsa`). Pengaju memilih kategori, bukan unit; unit tujuan diturunkan dari register pemilik kategori.
  - **`product` dan `sku` diisi server** dari item pesanan di integration-service berdasarkan nomor pesanan dan identitas item, bukan diketik. Pesanan tak ditemukan ditolak. Hari ini ketiganya (`product`, `sku`, `order_ref`) teks bebas tanpa validasi apa pun; satu-satunya yang diperiksa `title` (`quality_complaint.go:73-75`).
  - **`severity` pindah ke QC** saat validasi, tidak lagi dipilih pengaju.
  - Gerbang tulis mengikuti register gudang (pemegang toko atas tokonya, atau staf marketing), `company_id` ditambahkan, dan race `ReplaceOne` ditutup.
  - Formulir `/icc/komplain-qc` diganti formulir satu pintu; `/quality/komplain` tetap.
  - **Ganti kategori**: komplain yang ternyata milik gudang dialihkan lewat rute internal berkunci layanan, idempoten atas id komplain asal, dan komplain asal berstatus akhir "dialihkan".
  - **Tidak** disambungkan ke CAPA.

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
- **Komplain QC dari Marketing** — ✅ live (lihat register di atas). **Komplain & Rating Produk dari review marketplace** (sumber `/integration/reviews`) tetap **belum** difilter-mutu di modul Quality (register `quality_complaint` khusus komplain internal marketing→QC, bukan review pembeli). 🟡 **Arahnya sudah diputuskan 2026-09-16** di [[ADR - 0099 Komplain dari Ulasan Marketplace Dirutekan per Departemen lewat Register Komplain yang Ada]]: komplain dari ulasan dirutekan ke register yang SUDAH ADA di tiap tujuan, yaitu register ini untuk keluhan mutu, dan `warehouse_komplain_gudang` (warehouse-service) untuk keluhan pekerjaan gudang packing. ⛔ Register ini **TIDAK** diberi field tujuan departemen dan **TIDAK** memakai master kategori baru; keduanya sempat diputuskan lalu dibatalkan hari itu juga setelah register gudang ditemukan sudah lengkap berikut daftar kategori tertutupnya sendiri. Yang ditambahkan ke sini hanya salinan isi ulasan berikut penanda sumber, dan itu pun hanya bila jalur QC memang disentuh. Hanya Shopee: TikTok tak menyediakan teks ulasan per pembeli. Dua butir di bawah (race `ReplaceOne` dan `company_id` yang belum ada) ditutup bila jalur ini disentuh, bukan diwariskan diam-diam. ⚠️ **Revisi 2026-09-17**: [[ADR - 0103 Satu Pintu Komplain Produk, Unit Tujuan Diturunkan dari Kategori]] menggantikan "pengaju memilih tujuan dulu" dan menambahkan lebih dari salinan ulasan ke register ini: kategori tertutup miliknya sendiri (bukan master pusat, jadi tidak bertentangan dengan pembatalan di atas), produk dan SKU yang diisi server, dan status akhir "dialihkan". Rinciannya di register Komplain QC di atas.
- **Race simpan komplain vs validasi QC** (sudah ada sebelum aturan pemilik; follow-up) — `PUT /quality/complaints/:id` menimpa lewat `ReplaceOne` berfilter `_id` saja. Validasi QC yang mendarat di antara baca dan simpan tertimpa kembali menjadi "Menunggu Validasi" **tanpa pesan**, padahal notifikasi `komplain-qc-divalidasi` sudah terkirim ke pengaju. Perbaikannya: status "Menunggu Validasi" masuk filter dan balasan 409 bila `MatchedCount` 0. **Belum**.
- **Daftar komplain terbuka lintas brand dan lintas perusahaan** — `GET /quality/complaints` hanya menyaring `?status=`, dan `QualityComplaint` tak menyimpan `company_id` (notifikasi memakai perusahaan pemanggil). Menutupnya butuh migrasi data dan keputusan visibilitas; **belum diputuskan**.
- **`POST` tanpa identitas menyimpan `created_by` kosong** — hanya bisa terjadi lewat token layanan, karena gateway selalu mengisi `BIP-Employee-ID` dari JWT. Komplain seperti itu hanya bisa diubah SPV/admin IT, dan hasil validasinya tak diberitahukan ke siapa pun (dicatat di log `quality_complaint_notify.go`).
- **Tabel `/icc/komplain-qc` tak menampilkan pengaju** (data hanya membawa `employee_id`), jadi komplain milik orang lain tak menyebut siapa yang bisa dimintai koreksi. Titik putus yang diterima sadar saat aturan pemilik dibuat.
- ⚠️ **Seluruh register Quality belum pernah terisi di produksi.** Diukur PROD 2026-09-17: `employee_db` tidak punya satu pun koleksi berawalan `quality_` (kontrol positif: 30 koleksi lain terbaca), jadi CAPA, incoming, batch release, komplain, dan pengecekan RM semuanya nol dokumen. Jangan membangun otomatisasi di atas register ini (misalnya sambungan komplain ke CAPA) sebelum ada pemakaian nyata; ukur ulang sebelum dipakai memutuskan.
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

## Deskripsi

*Digitalisasi **batch release dossier** produksi (form manual 7 lembar "Ceklis Kelengkapan Dokumen Produksi" PT. Bharata) menjadi menu WMS: admin produksi mengisi form terstruktur, QC/RnD memeriksa & memberi paraf, lalu keputusan rilis (LULUS / Release for Sale). Menu baru yang **terisolasi** — tidak mengubah menu "Laporan Produksi" yang sudah ada, dan (sesuai desain) **tidak menyentuh stok/Accurate**.*

- **Stack**: Go/Fiber + MongoDB (backend), Next.js/React + TypeScript + Tailwind (frontend)
- **Path (backend)**: `bip-erp/services/manufacture/batch_record.go`, `batch_record_logic.go`; model di `shared-library/models/manufacture/models.go` (`BatchRecord`)
- **Path (frontend)**: `erp-frontend/src/features/manufacture/` → `components/BatchRecordView.tsx` · `BatchRecordForm.tsx` · `BatchRecordPrint.tsx`, `hooks/useBatchRecords.ts`, `lib/batch-record-calc.ts`, `types/batch-record.ts`, `akses.ts`
- **Menu**: Manufacture (WMS) → grup **Order & Dokumen** → **Dokumen Produksi Batch** (`/manufacture/dokumen-produksi-batch`)
- **Status**: ✅ Implemented

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC (`system_roles`) | Device |
|---|---|---|---|
| Admin RM (Restu) | Manufaktur — gudang RM | `manufacture = admin_gudang_rm` — buat/isi kolom **Ditimbang** (pra-produksi) + No.Batch bahan | Desktop web |
| Admin Produksi (Mame) | Manufaktur — produksi | `manufacture = admin_produksi` — isi **Sisa + Hasil PCS** + data proses; edit (DRAFT/DITOLAK), ajukan | Desktop web |
| QC / RnD (PJ Teknis) | Manufaktur — QC/RnD | `manufacture = qc`/`rnd` — periksa, isi field mutu, setujui (LULUS)/tolak; **tidak** bisa melihat DRAFT | Desktop web |
| PPIC / SPV | Manufaktur | super-akses (lihat semua tab WMS) | Desktop web |

- **Tujuan**: memindahkan dokumen batch manual (tulisan tangan) ke sistem, dengan pemisahan tanggung jawab pengisian: admin produksi mengisi data proses; QC mengisi data uji + memberi paraf saat rilis.
- **Pain point (sistem lama/manual)**: dokumen kertas, tanpa softfile, tanpa jejak persetujuan, rentan hilang; approval "tiba-tiba" tanpa proses cek.
- **Aksi utama**: buat dossier → isi 7 lembar → ajukan → QC periksa & centang & paraf → LULUS/DITOLAK → cetak PDF 7 lembar.

## Fitur (Sudah Diimplementasikan)

### 7 lembar (satu dossier = satu no. batch)
Mengikuti urutan & format dokumen manual:
1. **Ceklis Kelengkapan Dokumen Produksi** (cover) — daftar dokumen ADA/TIDAK + catatan; ttd Yang Mengajukan & Penanggung Jawab Teknis.
2. **Daftar Kesiapan Ruang Pengolahan** (No.Doc PR/04/PD/011/03) — tahapan · persyaratan · hasil · paraf Pelaksana/Pemeriksa.
3. **Catatan Pengolahan Batch** — penimbangan **multi-peran** (kolom **Teoritis · MO · Ditimbang · Sisa · Pemakaian · Rekon %**), rekonsiliasi, fase proses (A/B/AB/C/ABC/FILLING) + Hasil QC, ttd Ka.Bag Produksi & Ka.Bag Pengawasan Mutu.
4. **Daftar Kesiapan Ruang Pengemasan** (No.Doc PR/04/PD/011/04).
5. **Catatan Pengemasan Batch** (No.Dok PR/SOP/007/01/F/01) — komposisi kemasan (botol/label/hologram), prosedur pengemasan sekunder, **foto kemasan**, rekonsiliasi produk jadi.
6. **Catatan Pengujian** — pengujian produksi per fase, keseragaman bobot/volume (S1/S2/S3), pengujian pengemasan (Jelas/Rapih), pelaksana.
7. **Lembar Keputusan** — Daftar Checklist QA + stempel **RELEASE FOR SALE / LULUS**.

### Workflow & approval
- Status: **DRAFT → DIAJUKAN → LULUS / DITOLAK** (transisi terjaga di server, anti-race via guarded update; audit trail via `writeAudit`).
- **Pemisahan peran**: admin produksi membuat & mengajukan; **QC/RnD** memeriksa & menyetujui/menolak. Identitas & waktu pengaju/penyetuju **distempel dari header JWT** (nama lengkap karyawan), bukan dari body → tanda tangan digital.
- **Mode Pengecekan QC** (bukan approve buta): tombol **Periksa & Setujui** membuka **preview dokumen interaktif**. QC mengisi field yang jadi tanggung jawabnya — Catatan Pengujian (**Hasil** uji, keseragaman, Jelas/Rapih, pelaksana), **Hasil & Paraf Pemeriksa** di Kesiapan Ruang, **Hasil QC per fase** di Catatan Pengolahan, **Hasil QC & Paraf Pemeriksa** di Prosedur Pengemasan, serta men-**centang Ada + Catatan** pada **Ceklis Kelengkapan** & **Daftar Checklist QA** — lalu **Setujui (LULUS)** (tombol di bagian bawah dokumen) atau **Tolak** + alasan. Field isian bertanda latar kuning; menekan **Tab** pada field kosong mengisi otomatis teks contohnya.
- **Field milik QC dikunci di form admin**: seluruh field di atas **read-only** di form Dokumen Produksi Batch (admin produksi/RM) dan **hanya** bisa diisi di layar review — cerminan tulisan tangan QC pada dokumen asli. Saat approve, `ceklis`, `prosedur_kemas`, `fase`, `uji_produksi`, `kesiapan_olah/kemas`, `checklist_qa`, dll. di-`$set` dari body review (kolom admin—deskripsi/jam/hasil/pelaksana—dipertahankan dari record yang di-load, QC hanya menambah kolomnya).
- **Pengecualian**: **Nama Bahan** per fase pada Catatan Pengujian = data proses/formula → tetap diisi **admin produksi** di form (QC hanya mengisi kolom **Hasil**). Kolom **MO** = auto dari Material Order (lihat bawah), **bukan** input manual.

### Penimbangan multi-peran & rekonsiliasi MO (support ticket 2026-07)
- Tabel penimbangan diisi **dua peran** pada satu dossier: **admin RM (Restu)** mengisi **Ditimbang** (jumlah ditimbang pra-produksi) + No.Batch bahan; **admin produksi (Mame)** mengisi **Sisa** (sisa timbangan pasca-produksi) + **Hasil PCS**. Kolom dikunci per peran (RM tak bisa ubah Sisa, dan sebaliknya); PPIC/SPV boleh semua.
- **Pemakaian = Ditimbang − Sisa** (auto). **Rekonsiliasi = Pemakaian/Teoritis × 100** (batas <2%). Kolom **MO** auto dari [[Manufacture - Order Production Workflow (Flow Source)|Material Order]] (`qty_needed_total`, ditaut by `no_batch`); ditandai **kuning** bila **Pemakaian > MO** → "jumlah MO sesuai pemakaian" terpantau.
- **BPOM** tetap dokumen fisik (di luar sistem); versi **Perusahaan** = softfile ini. Jadi tidak ada dua varian ekspor — cukup satu output.
- Gate: `admin_gudang_rm` masuk `bolehBuatBatchRecord` + middleware `requireBatchCreate` (rbac.go).

### Rekonsiliasi (warning-only)
- Penimbangan bahan: `R = nyata/teoritis × 100%`, batas keberterimaan penyimpangan **< 2%**.
- Mixing / Filling / Produk Jadi: batas **98–102%**.
- Di luar batas → ditandai (merah) + flag `di_luar_batas`, **tetap boleh disimpan/diajukan** (dicatat di Penyimpangan). Dihitung ulang di server saat simpan; ditampilkan live saat mengetik.
- **BOM/teoritis** auto dari [[Microservices - Manufacture Service]] `Formula` (`/api/manufacture/formula`) × ukuran batch; pemilih formula ber-search (dark-mode aware).

### Cetak
- Tampilan cetak **7 halaman A4** (`@page A4`, tiap lembar `break-before-page`), berkop **logo PT Bharata**, tabel/garis meniru kertas asli, stempel LULUS bila disetujui. Dirender via React **portal ke `<body>`** + `@media print` (menyembunyikan chrome aplikasi) → Ctrl-P/Save-as-PDF. Belum ada generate PDF server-side.

### Daftar & filter
- Filter status berbentuk **tab** (Semua/Draft/Diajukan/Lulus/Ditolak + hitungan) + **filter bulan-tahun** (default bulan berjalan) + pencarian. Kolom: No. Dossier · Produk · No. Batch · Tgl · **Mengajukan** · **Menyetujui** · Status. Untuk akun QC-only: default tab **Diajukan** & baris DRAFT disembunyikan.

### Tautan silang ke Laporan Produksi
- Dicocokkan berdasarkan **`no_batch`** yang sama: dari dossier, **No. Batch** menjadi link ke [[Manufacture - Order Production Workflow (Flow Source)|Laporan Produksi]] (`/manufacture/production?batch=<no_batch>`), dan sebaliknya baris Laporan Produksi menampilkan link **"Dokumen Batch"**. Menu tujuan otomatis ter-prefilter. (Klien mem-fetch set `no_batch` menu lawan; link muncul hanya bila ada padanan. Link ke Laporan Produksi disembunyikan untuk QC-only yang tak punya akses menu itu.)

## Model Data & Endpoint

- **Collection**: `manufacture_batch_record` (struct `BatchRecord`). Field kunci: `nomor_dossier` (auto `BR/<tahun>/<urut>`), `status`, header produk, `dibuat_oleh_*`, `diajukan_oleh_*`, `disetujui_oleh_*`, sub-struct 7 lembar (`ceklis`, `kesiapan_olah/kemas`, `penimbangan` [+`qty_mo`, `nyata`=ditimbang, `sisa`, `pemakaian`], `fase`, `rekon_*`, `komposisi_kemasan`, `prosedur_kemas`, `foto_kemasan` [MinIO key], `uji_produksi`, `keseragaman`, `checklist_qa`, dll).
- **Endpoint** (via gateway → manufacture service, lihat [[API - Manufacture Service]]):
  - `GET /api/manufacture/batch-record` (list; filter status/produk) · `GET .../:id`
  - `POST .../batch-record` (buat draft; auto nomor + seed ceklis/kesiapan/uji) · `PUT .../:id` (edit saat DRAFT/DITOLAK)
  - `POST .../:id/ajukan` · `POST .../:id/approve` (body opsional `reviewed:true` + field isian QC) · `POST .../:id/tolak` (wajib `reason`)
- **Enforcement peran di backend** (bukan hanya sembunyi menu): `bolehBuatBatchRecord` / `bolehApproveBatchRecord` di `batch_record_logic.go`.

## Belum Diimplementasikan / Catatan

- **Berdiri sendiri terhadap stok** (by design): tidak mengonsumsi bahan / menciptakan stok FG / push Accurate — itu ranah [[Manufacture - Stock & Material Management|Laporan Produksi & stok]]. Dossier ini murni dokumentasi mutu + keputusan rilis.
- **Tanggal Pengujian** (lembar 6) sementara memakai `tgl_selesai_olah` sebagai proxy (belum ada field tanggal uji tersendiri).
- **Label role QC** — kode menerima `manufacture = qc` / `rnd`; konfirmasi istilah persis di Master Data tim manufacture sebelum go-live.
- **Cetak** = print-to-PDF browser; **generate PDF server-side** = (TBD).
- Foto kemasan: dikompres di browser (`utils/compress-image.ts`: maks 1600px, JPEG q0.7) lalu diunggah presigned ke MinIO lewat [[Microservices - File Service]] (`service=manufacture`, `document=batch-record`).

## Dependensi & Integrasi

- [[Microservices - Manufacture Service]] — host endpoint `batch-record` + sumber `Formula`.
- [[Microservices - File Service]] — presigned upload/preview foto kemasan (MinIO).
- [[Microservices - Employee Service]] — sumber nama lengkap karyawan (pengaju/penyetuju) via JWT.
- [[CORE - API Master Gateway]] — proxy generik `/api/manufacture/*` + injeksi header `BIP-System-Roles`, `BIP-Fullname`.
- [[APP - Web ERP]] — shell frontend (modul manufacture, `akses.ts` matriks tab).

## Dokumen Terkait

- [[QA - Batch Record & Traceability]] — konsep QA/RA batch record & ketertelusuran (dokumen ini adalah implementasi digitalnya).
- [[QA - CPOB (GMP)]] — konteks kepatuhan CPOB (form kesiapan ruang, rekonsiliasi, release for sale).
- [[Manufacture - Order Production Workflow (Flow Source)]] — alur produksi & Laporan Produksi (tertaut via `no_batch`).
- [[Manufacture - Stock & Material Management]] — pencatatan stok bahan & produk jadi (di luar lingkup dossier ini).

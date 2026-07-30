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
| Admin RM (Restu) | Manufaktur — gudang RM | `manufacture = admin_gudang_rm` — buat/isi kolom **Ditimbang** (pra-produksi) | Desktop web |
| Admin Produksi (Mame) | Manufaktur — produksi | `manufacture = admin_produksi` — isi **Hasil PCS** + data proses; edit (DRAFT/DITOLAK), ajukan; isi **Sisa timbangan** di menu **Rekonsiliasi MO** | Desktop web |
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
3. **Catatan Pengolahan Batch** — penimbangan bahan (kolom **Nama Bahan · No. Batch · Teoritis · Ditimbang · Rekon %**, persis kertas), rekonsiliasi (Ditimbang/Teoritis, <2%), fase proses (A/B/AB/C/ABC/FILLING) + Hasil QC, ttd Ka.Bag Produksi & Ka.Bag Pengawasan Mutu.
4. **Daftar Kesiapan Ruang Pengemasan** (No.Doc PR/04/PD/011/04).
5. **Catatan Pengemasan Batch** (No.Dok PR/SOP/007/01/F/01) — komposisi kemasan (botol/label/hologram), prosedur pengemasan sekunder, **foto kemasan**, rekonsiliasi produk jadi.
6. **Catatan Pengujian** — pengujian produksi per fase, keseragaman bobot/volume (S1/S2/S3), pengujian pengemasan (Jelas/Rapih), pelaksana.
7. **Lembar Keputusan** — Daftar Checklist QA + stempel **RELEASE FOR SALE / LULUS**.

### Workflow & approval
- Status: **DRAFT → DIAJUKAN → LULUS / DITOLAK** (transisi terjaga di server, anti-race via guarded update; audit trail via `writeAudit`).
- **Pemisahan peran**: admin produksi membuat & mengajukan; **QC/RnD** memeriksa & menyetujui/menolak. Identitas & waktu pengaju/penyetuju **distempel dari header JWT** (nama lengkap karyawan), bukan dari body → tanda tangan digital.
- **Mode Pengecekan QC** (bukan approve buta): tombol **Periksa & Setujui** membuka **preview dokumen interaktif**. QC mengisi field yang jadi tanggung jawabnya — Catatan Pengujian (**Hasil** uji, keseragaman, Jelas/Rapih), **Hasil** di Kesiapan Ruang, **Hasil QC per fase** di Catatan Pengolahan, **Hasil QC** di Prosedur Pengemasan, serta men-**centang Ada + Catatan** pada **Ceklis Kelengkapan** & **Daftar Checklist QA** — lalu **Setujui (LULUS)** (tombol di bagian bawah dokumen) atau **Tolak** + alasan. Field isian bertanda latar kuning; menekan **Tab** pada field kosong mengisi otomatis teks contohnya. (Kolom **paraf** = jabatan, lihat bawah — bukan diisi QC.)
- **Field milik QC dikunci di form admin**: seluruh field di atas **read-only** di form Dokumen Produksi Batch (admin produksi/RM) dan **hanya** bisa diisi di layar review — cerminan tulisan tangan QC pada dokumen asli. Saat approve, `ceklis`, `prosedur_kemas`, `fase`, `uji_produksi`, `kesiapan_olah/kemas`, `checklist_qa`, dll. di-`$set` dari body review (kolom admin—deskripsi/jam/hasil/pelaksana—dipertahankan dari record yang di-load, QC hanya menambah kolomnya).
- **Pengecualian (field bersumber → ditaut, bukan ketik bebas)**: **Nama Bahan** per fase pada Catatan Pengujian dipilih **admin produksi** lewat picker dari **tabel penimbangan** dossier (sumber = formula; disimpan string `"a, b, c"`) — QC hanya mengisi kolom **Hasil**. Header **Nama Produk/Kode Produk** + seluruh baris **penimbangan** auto ter-isi saat pilih **Formula**.
- **Paraf by jabatan (bukan ketik nama)**: panel **"Tim Batch — Jabatan Paraf"** di form — pilih **jabatan** sekali per peran (picker dari Master Karyawan HRIS, `GET /api/employee/list?type=employee` → `position`) lalu **tersebar otomatis** ke semua kolom paraf 7 lembar: `kesiapan_olah/kemas` (pelaksana/pemeriksa), `prosedur_kemas` (pelaksana/pemeriksa), `olah/kemas_ka_bag_produksi/mutu`, `pelaksana_uji`. Kolom paraf jadi **read-only** (sumber = `ParafRoster`). **Yang Mengajukan** & **Penanggung Jawab Teknis** distempel **nama + jabatan** (`diajukan/disetujui_oleh_jabatan` dari `BIP-Position`) saat Ajukan/Approve — orangnya bisa berganti, jabatan yang dipatok. Alasan: paraf harus tanpa ketik manual & tak selalu orang yang sama.

### Penimbangan = persis dokumen asli
- Tabel penimbangan dossier **mengikuti kertas** (Catatan Pengolahan Batch hal. 4): **No. Batch** + **Ditimbang** diisi **admin RM (Restu)** saat penimbangan; **Rekonsiliasi = Ditimbang / Teoritis × 100%** (batas <2%). **Tidak ada** kolom MO / Sisa / Pemakaian di dossier — itu bukan bagian dokumen asli.
- Backend `recalcBatchRecord` menghitung rekon atas **Nyata (Ditimbang)**, bukan Pemakaian.

### Rekonsiliasi Pemakaian vs MO (support ticket 2026-07) — ✅ menu terpisah "Rekonsiliasi MO"
- Kebutuhan tiket ("agar **jumlah MO sesuai pemakaian**") **bukan** bagian dokumen batch asli & Laporan Produksi tak menampung data per-bahan → dibuat **menu tersendiri** `RekonMoView` (`/manufacture/rekonsiliasi-mo`, tab `rekon_mo`), **memakai koleksi `manufacture_batch_record` yang sama** (Ditimbang tetap satu sumber — tak diduplikasi), **tidak** ikut cetak 7-lembar dossier.
- Per bahan menampilkan **MO** (dari [[Manufacture - Order Production Workflow (Flow Source)|Material Order]] `qty_needed_total`, by `no_batch`) · **Ditimbang** (dari dossier, Restu) · **Sisa** (diisi **Mame**) · **Pemakaian** (= Ditimbang − Sisa) · **Selisih vs MO** (kuning bila ≠). Plus **Hasil PCS** (`rekon_produk_jadi`).
- **SPV QC** memeriksa: ceklis "Kelengkapan hasil produksi" + "Hasil timbangan dari produksi" + catatan → tandai **DICEK**. Output **Perusahaan** = cetak softfile ("Laporan Catatan Pengolahan dan Pengemasan Batch"); **BPOM** tetap fisik/di luar sistem.
- Endpoint: `PUT .../batch-record/:id/rekon-mo` (isi Sisa+qty_mo; `requireBatchCreate` = admin produksi/RM) · `POST .../batch-record/:id/rekon-mo/approve` (`requireBatchApprove` = QC/RnD). Field: `rekon_mo_status` ("" | "DICEK"), `rekon_mo_ceklis`, `rekon_mo_catatan`, `rekon_mo_diperiksa_oleh_*`, `rekon_mo_diperiksa_at`. `qty_mo`/`sisa`/`pemakaian` di `penimbangan` (sebelumnya dormant) kini dipakai di sini.
- Gate: `admin_gudang_rm` masuk `bolehBuatBatchRecord` + `requireBatchCreate`; matriks tab `rekon_mo` = {admin_produksi, admin_gudang_rm, qc, rnd} (FE `akses.ts` + BE `rbac.go`).

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

- **Collection**: `manufacture_batch_record` (struct `BatchRecord`). Field kunci: `nomor_dossier` (auto `BR/<tahun>/<urut>`), `status`, header produk, `dibuat_oleh_*`, `diajukan_oleh_*`, `disetujui_oleh_*`, sub-struct 7 lembar (`ceklis`, `kesiapan_olah/kemas`, `penimbangan` [`no_batch_bahan`, `teoritis`, `nyata`=ditimbang, `rekonsiliasi`; + `qty_mo`/`sisa`/`pemakaian` **dormant** utk fitur rekonsiliasi MO], `fase`, `rekon_*`, `komposisi_kemasan`, `prosedur_kemas`, `foto_kemasan` [MinIO key], `uji_produksi`, `keseragaman`, `checklist_qa`, `paraf_roster` [jabatan tiap peran paraf] + `diajukan/disetujui_oleh_jabatan`, `rekon_mo_*` [status/ceklis/catatan/diperiksa — fitur Rekonsiliasi MO], dll).
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

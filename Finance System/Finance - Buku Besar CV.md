# Finance - Buku Besar CV

## Deskripsi

*Konsep modul buku besar dan konsolidasi 40 CV grup di dalam ERP: satu identitas CV, bagan akun, jurnal, laporan keuangan per CV, kertas kerja konsolidasi, tutup buku, dan jurnal otomatis dari pembayaran, kas kecil, payroll, marketplace, serta mutasi bank. Keputusan dan alasannya di [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]]; spesifikasi awalnya [[APP - Buku Besar Konsolidasi CV FINCON]].*

- **Status**: 🟡 **Konsep** untuk bagan akun, jurnal, laporan, konsolidasi, dan tutup buku (dirancang 2026-09-15); pembukuan 40 CV hari ini masih berjalan di FINCON, di luar ERP. ⚠️ **Master entitas CV, penugasan pemegang, dan cakupan tulis (T1) dikodekan** di branch `feat/finance-entitas-cv` bip-erp dan erp-frontend 2026-09-15, **belum merge**, lihat §Master entitas CV dan §Belum Diimplementasikan / Catatan.
- **Implementasi**: modul finance-service ([[Finance - Rancangan Finance Service]]); rute T1 di [[API - Finance Service]] §Buku Besar CV, layar `/finance/entitas-cv` dan `/finance/entitas-cv/saya` di [[APP - Web ERP]]. Sisanya TBD.

## Latar Belakang

- **Buku CV di luar pagar.** FINCON membukukan 40 CV sejak 2026-08-05 dari repo pribadi dan database Supabase, dengan otorisasi hanya di peramban ([[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]]).
- **Satu pembayaran dicatat berkali-kali.** Survei alur kerja Finance (2026-09-14) memperlihatkan pembayaran CV dicatat di voucher BKK FINCON, AppSheet, Kopra, jurnal, dan arsip kertas, oleh Junior Accountant yang masing-masing memegang sekelompok CV.
- **ERP punya potongan-potongannya tanpa buku untuk dituju.** Pengajuan Barang, alokasi kas kecil per CV, payroll per badan usaha, dan data marketplace per toko sudah ada, tetapi seluruh jurnalnya menuju Accurate PT; tak ada buku per CV di ERP.
- **Identitas CV terpecah** di payroll, rekening Accurate, FINCON, dan katalog procurement, tanpa kunci bersama ([[REF - Kepemilikan Data]] §Duplikasi).

## Ruang Lingkup / Cakupan (business view)

### Master entitas CV

- Satu daftar 40 CV berkode `CV01` sampai `CV40` (kode FINCON), dengan nama resmi, rujukan badan usaha payroll, rekening Accurate 1299xx, dan toko marketplace yang dimilikinya.
- PT hanya dirujuk sebagai lawan transaksi; pembukuannya tetap di Accurate.
- Penugasan pemegang CV per karyawan. FINCON hari ini membagi CV ke enam akun bersama (7, 7, 7, 7, 6, dan 6 CV); pembagian itu titik awal, bukan ketentuan.

**Yang dikodekan T1** (branch `feat/finance-entitas-cv`, belum merge; `bip-erp/services/finance/akuntansi_cv_*.go`):

- **Semai**: 40 CV bawaan dari FINCON `src/utils/accounting.js` `DEFAULT_COMPANIES` (kode, singkatan tiga huruf, nama) di-upsert `$setOnInsert` per perusahaan, jadi mengulang semai tak menimpa nama yang sudah dikoreksi. Rujukan diisi otomatis hanya bila masih kosong, hanya untuk CV aktif, dan hanya untuk cocok tunggal sesudah normalisasi format nama ([[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] §2 amandemen); ambigu dan tak cocok dibiarkan kosong lalu dilaporkan. Tombol Semai tampil selama `GET /akuntansi-cv/entitas/bawaan` menyebut ada kode bawaan yang belum disemai; jumlah CV bawaan hanya hidup di daftar bawaan backend.
- **Rujukan**: `payroll_company_id` (badan usaha payroll, dibaca lewat rute internal payroll berkunci layanan) dan `akun_accurate_no` (anak COA 1299, bukan induknya, `common.AdalahRekeningCV`, dibaca dari bagan akun Accurate lewat integration). Satu rujukan hanya boleh dipakai satu CV (index unik parsial dan 409). Mengubah rujukan diperiksa ke sumbernya: sumber tak terbaca 503, rujukan tak ada 422. Bagan akun dibaca integration dari cache, jadi rekening yang baru dibuat di Accurate bisa belum terlihat beberapa saat.
- **Laporan kecocokan**, dihitung saat dibuka (pola laporan kesehatan toko ICC): `BELUM_DIPETAKAN_PAYROLL`, `BELUM_DIPETAKAN_REKENING`, `PAYROLL_TIDAK_ADA`, `REKENING_TIDAK_ADA`, `NAMA_PAYROLL_BEDA`, `NAMA_REKENING_BEDA`, `BADAN_USAHA_TANPA_ENTITAS` (badan usaha PT dikecualikan), `REKENING_TANPA_ENTITAS`, `PEMEGANG_TANPA_IZIN`, `CV_TANPA_PEMEGANG`. Status per sumber (payroll, integration, employee): sumber yang gagal dibaca **tidak** melahirkan temuan, dan layar menampilkan "Belum pasti", bukan "Cocok". Nama payroll dibetulkan HR di Pengaturan Gaji, nama rekening di Accurate; laporan hanya melaporkan.
- **Penugasan**: satu dokumen per CV (`akuntansi_cv_penugasan`: `kode_cv`, `pemegang[]`, `versi`), diganti atomik dengan prasyarat versi; versi basi dijawab 409 dan layar memuat ulang datanya. Calon pemegang hanya pemegang izin `akuntansicv.cv.tulis`, dibaca dari `GET /internal/permission-holders` employee-service dan gagal-tertutup 503; yang tak berizin ditolak 422 dengan menyebut orangnya; pengelola tak boleh menugaskan dirinya sendiri (403).
- **Cakupan tulis**: `CakupanTulisCV` = izin `cv.tulis` DAN penugasan DAN CV aktif; entitas nonaktif atau yang tak ada di master tertutup. CV tanpa pemegang tertutup untuk tulis, tetap terbaca pembaca semua CV. Layar CV Saya memakai fungsi yang sama, dan gerbang tulis T2/T3 wajib memanggilnya juga.
- **Jejak**: koleksi sendiri `akuntansi_cv_jejak` untuk semai, ubah entitas, dan atur pemegang (sebelum/sesudah hanya field yang berubah). Jejak ditulis sesudah perubahan; kegagalannya menggagalkan respons dengan pesan "sudah tersimpan" dan dicatat keras ke log beserta isinya, perubahannya tidak dibatalkan. Semai yang berhenti di tengah sesudah menulis tetap meninggalkan jejak berisi yang sudah ditulis beserta galatnya.

### Bagan akun

- Satu COA bersama untuk 40 CV, seperti FINCON: kode, nama, tipe (Asset, Liability, Equity, Revenue, Expense), dan saldo normal. COA bawaan FINCON (sekitar 66 akun berkode 3 digit, `accounting.js` `DEFAULT_COA`) jadi titik awal.
- Akun yang muncul di alur survei sudah ada di COA itu, antara lain Utang Iklan Advertiser (213), Utang BPJS-TK (215), Utang Pajak PP 55 (227), Beban Iklan Ads (611), dan beban kas kecil per brand (618, 620, 621).
- Akun kontra bersaldo normal kebalikan kelompoknya: Akumulasi Penyusutan (161) kredit, Prive (314) debit.
- Mengubah COA tidak menghapus lalu mengisi ulang seluruh akun, cara yang dipakai FINCON hari ini.

### Jurnal

- Jenis: kas, piutang, utang, umum, penyesuaian; ditambah saldo awal, penyusutan, dan eliminasi.
- Aturan penyimpanan, validasi, penomoran, koreksi, kunci periode, dan pemeriksa ada di [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] §4.
- Format nomor voucher dari FINCON (`CashJournalForm.jsx`): `BKK/NNN/MM/YY/BANK` untuk kas keluar, `BKM/NNN/MM/YY/BANK` untuk kas masuk, `SA/MM/YY/BANK` untuk saldo awal bulanan. `BANK` diturunkan dari nama akun kas: BMRI, BCA, BNI, BRI, selain itu KAS.

### Sumber jurnal otomatis (bertahap)

| Sumber | Dokumen asal yang sudah ada | Jurnal yang dibentuk di buku CV | Prasyarat yang belum ada |
|---|---|---|---|
| Pengajuan uang (IKLAN, DANA, KONSUMSI) bersumber dana rekening CV | Pengajuan Barang, pembayaran, bukti transfer ([[Microservices - Procurement Service]]) | Kas keluar bernomor BKK | CV tujuan eksplisit, cakupan per CV |
| Kas kecil | Transaksi kas kecil dan alokasi per CV ([[Finance - Kas Kecil dan Pengajuan Budget]]) | Beban per CV | Master entitas |
| Gaji dan BPJS TK | Payroll run per badan usaha ([[Microservices - Payroll Service]]) | Beban gaji, utang BPJS, pembayaran | Daftar bayar dan rekap iuran per badan usaha |
| Penjualan marketplace | Faktur, penerimaan, dan retur per toko ([[Microservices - Integration Service]]) | Penjualan, potongan platform, ongkir, HPP, kas toko | Pemetaan toko ke CV, gerbang kolom di bawah |
| Penarikan saldo toko | Mutasi wallet Shopee, penarikan TikTok, transaksi akun Lazada | Kas toko ke rekening CV | Pemetaan toko ke CV |
| Mutasi rekening | Belum ada | Pencocokan, beban adm dan bunga bank | Format berkas mutasi (TBD) |
| Hutang CV ke PT | TBD | TBD | Makna hutang supplier CV (TBD) |

### Laporan

- Buku besar per akun, neraca saldo, laba rugi bertingkat, neraca kumulatif, arus kas metode langsung, perubahan ekuitas, laporan bulanan 12 kolom, rasio, dan register aset tetap.
- Saldo tiap akun mengikuti saldo normalnya.
- Laba rugi bertingkat (laba kotor, EBITDA, EBIT, laba bersih) ditambahkan di FINCON `origin/main` 2026-09-08; rumus persisnya diambil dari kode itu saat task laporan direncanakan.
- Penyusutan garis lurus bulanan sejak bulan perolehan, dibulatkan dua desimal, dengan enam kelompok umur: 4, 8, 16, dan 20 tahun, bangunan permanen 20 tahun, bangunan semi permanen 10 tahun (FINCON `FixedAssetsView.jsx`).

### Konsolidasi

- Kertas kerja 40 kolom: saldo tiap CV dijumlah, lalu jurnal eliminasi diterapkan mengikuti saldo normal (debit menambah akun bersaldo normal debit, kredit menambah akun bersaldo normal kredit), seperti FINCON `accounting.js` `calculateConsolidatedData`.
- Berbeda dari FINCON: jurnal eliminasi menyimpan pasangan entitasnya; neraca konsolidasi kumulatif; eliminasi akun laba rugi ikut mengalir ke Laba Tahun Berjalan; baris eliminasi ke akun di luar COA ditolak, bukan diabaikan.
- PT belum ikut digabung (TBD).

### Tutup buku dan rekonsiliasi

- Kunci periode per CV dan daftar periksa tutup buku.
- Rekonsiliasi kas buku CV terhadap mutasi rekening yang diimpor. Kartu selisih rekening koran di dashboard posisi Accounting CV dan Senior Accountant hari ini menandai modul itu belum ada ([[Finance - Dashboard per Posisi (FAT)]]).
- Rekonsiliasi bulanan kas buku CV terhadap rekening CV 1299xx di Accurate PT (makna rekening itu TBD).

### Gerbang kolom

Jurnal penjualan otomatis hanya dibentuk dari komponen **sejajar** identitas income. Kolom di bawah bukan komponen sejajar, jadi tidak boleh dijumlahkan sebagai baris jurnal tersendiri. Diperiksa ke `bip-erp/services/integration/internal/domain/entity/` `origin/main` 2026-09-15.

| Kolom | Relasi | Berkas |
|---|---|---|
| `TotalShippingRebate` | Bagian dari `TotalOtherIncome` | `transaction.go` |
| `TotalOrderAdjustment` | Sudah terkandung di `TotalSettlementAmount`; menambahkannya ke beban menghitung dua kali | `transaction.go` |
| `TotalInsuranceFee` | Bukan komponen identitas income; wadah reklas dari adjustment | `transaction.go` |
| `TotalAdjustment` | Residual identitas, penyeimbang jurnal | `transaction.go` |
| `FeeCommDynamic`, `FeeCommService` | Pecahan `FeeCommission` | `settlement.go` |
| `FeeProcCashback`, `FeeProcInfra`, `FeeProcMall` | Pecahan `FeeProcess` | `settlement.go` |
| `Retur` | Kolom informasi; nilainya sudah tercermin di `Other` dan `NetSettlement` | `settlement.go` |
| `PerubahanSaldo` | Sudah memuat `UangMasuk` dan `Penarikan`; `SaldoTersedia` snapshot, bukan jumlah periode | `wallet.go` |
| `FeeMarketplace` | Total seluruh potongan breakdown | `profit.go` |
| `BundleProfit` | Tumpang tindih dengan alokasi ke produk komponen | `profit.go` |
| `PayoutAmount` | Relasi dengan kolom settlement tidak dinyatakan di kode; verifikasi dulu sebelum dipakai | `transaction.go` |

Klasifikasi fee Lazada ke akun Accurate mengikuti [[ADR - 0078 Klasifikasi Fee Lazada Mengikuti Pemetaan COA Finance]]; pemetaannya ke COA CV TBD.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Junior Accountant pemegang CV | Junior Accountant, FAT | **DUA paket**: "Buku Besar CV: Pemegang" (`akuntansicv.cv.tulis`, merge 2026-09-16) yang membuka layar **CV Saya**, plus "Budget: Transfer Kas CV" (`budget.cv.transfer`, T2 branch) yang membuka tahap transfer. Antrean transfernya tinggal di CV Saya, bukan `/finance/ap` yang digerbang `finance.ap.view`. Belum dipasang di prod; per 2026-09-12 lima dari tujuh belum punya paket izin apa pun ([[Finance - FAT Persona]]) | Web ERP |
| Senior Accountant | Senior Accountant, FAT | Baca semua CV lewat paket "Buku Besar CV: Pembaca" (`akuntansicv.view`, rencana pemasangan T1); pemeriksa jurnal manual; review bukti transfer | Web ERP |
| SPV FAT | Finance Supervisor | Paket "Buku Besar CV: Pengelola" (`akuntansicv.view` + `akuntansicv.kelola`, sengaja tanpa `cv.tulis`, rencana pemasangan T1): semai, rujukan, penugasan; `budget.approve.finance`, `budget.approve.pembayaran`; kunci periode (TBD) | Web ERP |
| Tax Officer | Tax Staff | Baca semua CV untuk omzet dan pajak CV lewat paket "Buku Besar CV: Pembaca" (rencana pemasangan T1) | Web ERP |
| Account Payable | Account Payable | Transfer pengajuan bersumber dana rekening PT, `budget.ap.bayar`. Dokumen ber-kode CV **tidak** masuk antreannya (T2, branch) | Web ERP |
| Pemohon | Karyawan Marketing, HR, GA | `budget_pemohon_*` | Web ERP |
| Direktur | Direksi | Baca master entitas dan penugasan lewat paket "Buku Besar CV: Pembaca" (rencana pemasangan T1); izin laporan dan konsolidasi TBD | Web ERP |

- **Tujuan**: tiap transaksi CV dicatat sekali di tempat asalnya, dan laporan per CV serta konsolidasi siap sesudah tutup buku.
- **Pain point**: voucher, AppSheet, internet banking, dan jurnal diketik terpisah; menunggu data penarikan marketplace dan persetujuan; buku CV di aplikasi luar tanpa kendali akses di server.
- **Aksi utama**: menindak antrean pembayaran CV dan mengunggah bukti; memeriksa dan memposting jurnal; mengunci periode; membaca laporan per CV dan konsolidasi.

## Konsumen Data

- [[HRIS - Matriks KPI per Departemen]]: baris KPI Accounting CV berbobot 0,30 (laporan keuangan akurat maksimal tanggal 4 bulan berikutnya), hari ini belum dipetakan.
- [[Finance - Dashboard per Posisi (FAT)]]: kartu posisi Accounting CV dan Senior Accountant yang menunggu data per entitas.
- Tax Officer: omzet per CV untuk PPh final PP 55.

## Kendala

- MongoDB prod standalone: satu jurnal satu dokumen, penomoran lewat penghitung atomik.
- Accurate satu database dengan jatah laju 6 permintaan per detik yang dibagi seluruh service ([[External - Accurate]]), relevan untuk rekonsiliasi terhadap rekening 1299xx.
- Isi dan volume data FINCON di Supabase belum diketahui; migrasi bergantung pada ekspor oleh pemiliknya.
- Nama CV sudah menyimpang antar sumber (dua beda singkatan, satu berkarakter tak terlihat). Pencocokan otomatis hanya aman untuk selisih format dengan cocok tunggal; singkatan yang berbeda tetap ditetapkan manusia.
- Angka waktu kerja dari survei belum dikonfirmasi wawancara.

## Belum Diimplementasikan / Catatan

Keputusan user 2026-09-15 (`/review` T1) yang diterima tanpa kode:

- **Pemegang yang kehilangan izin tampil sebagai `employee_id`**, bukan nama: nama hanya datang dari daftar pemegang izin. employee-service belum punya endpoint internal nama per daftar id, dan `/internal/aggregate/employee/:id` memuat data pribadi yang tak layak dibaca demi nama.
- **Jejak semai satu baris** (`kunci: "*"`) berisi cacah dan kode yang dipasangkan, tanpa id rujukan, dan tidak muncul di riwayat per CV. Rujukan yang sengaja dilepas lewat Ubah bisa dipasang ulang otomatis oleh semai berikutnya; tombol Semai hanya tampil selama ada CV bawaan yang belum disemai.
- **`GET /akuntansi-cv/jejak` dipotong 200 baris terbaru tanpa penanda**; panel riwayat jejak di layar belum ada.
- **Master per `company_id` pemanggil, sumbernya lintas perusahaan**: badan usaha payroll dan bagan akun Accurate tidak disaring perusahaan. Paketnya hanya dipasang IT, jadi pengelola dari perusahaan lain tidak diharapkan.
- **Ubah entitas tanpa prasyarat versi**: hanya field yang berubah yang dikirim, jadi dua pengelola yang mengubah field berbeda tak saling menimpa; untuk field yang sama, yang terakhir menang.
- **Belum ada notifikasi penugasan** (belum ada aksi yang menunggu pemegang di T1) dan belum ada penjadwal laporan kecocokan.
- **Pemetaan toko ke CV** pindah ke T8.

## Belum Diputuskan (TBD)

1. Makna rekening CV 1299xx di buku PT, dan buku mana yang jadi dasar laporan pajak CV.
2. Apakah hutang supplier CV adalah hutang ke PT atas barang yang dijual, dan bentuk dokumennya.
3. Format dan frekuensi impor mutasi rekening.
4. ✅ **Terjawab 2026-09-15 (T1)**: modul izin `akuntansicv` (tiga izin, tiga paket, tanpa fallback tier) plus penugasan terpisah per CV di finance-service; lihat §Master entitas CV.
5. Siapa yang boleh mengunci dan membuka periode.
6. Kapan PT ikut konsolidasi.
7. Penomoran COA CV tetap 3 digit FINCON atau diselaraskan dengan akun Accurate, dan pemetaan fee marketplace ke COA CV.
8. ✅ **Terjawab sebagian 2026-09-15**: pemegang ditetapkan per karyawan oleh pengelola di layar Entitas CV, dan satu CV boleh lebih dari satu pemegang; enam kelompok FINCON bukan ketentuan. Siapa memegang CV mana tetap keputusan operasional SPV FAT.

## Dokumen Terkait

- [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] · [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] · [[ADR - 0001 Akuntansi via Accurate]]
- [[APP - Buku Besar Konsolidasi CV FINCON]] · [[Finance - FAT Persona]] · [[Finance - Big Pictures]]
- [[Microservices - Procurement Service]] · [[Microservices - Payroll Service]] · [[Microservices - Integration Service]] · [[External - Accurate]]
- [[REF - Kepemilikan Data]] · [[CORE - RBAC dan Permission Set]] · [[API - Finance Service]] · [[API - Payroll Service]] · [[APP - Web ERP]]

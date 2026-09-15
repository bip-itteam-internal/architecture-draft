# Finance - Buku Besar CV

## Deskripsi

*Konsep modul buku besar dan konsolidasi 40 CV grup di dalam ERP: satu identitas CV, bagan akun, jurnal, laporan keuangan per CV, kertas kerja konsolidasi, tutup buku, dan jurnal otomatis dari pembayaran, kas kecil, payroll, marketplace, serta mutasi bank. Keputusan dan alasannya di [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]]; spesifikasi awalnya [[APP - Buku Besar Konsolidasi CV FINCON]].*

- **Status**: 🟡 **Konsep**, belum ada di kode (dirancang 2026-09-15). Pembukuan 40 CV hari ini masih berjalan di FINCON, di luar ERP.
- **Implementasi**: TBD, direncanakan sebagai modul finance-service ([[Finance - Rancangan Finance Service]] · [[API - Finance Service]]).

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
| Junior Accountant pemegang CV | Junior Accountant, FAT | Izin buku besar CV dan penugasan CV (baru, TBD); per 2026-09-12 lima dari tujuh belum punya paket izin ([[Finance - FAT Persona]]) | Web ERP |
| Senior Accountant | Senior Accountant, FAT | Baca semua CV; pemeriksa jurnal manual; review bukti transfer | Web ERP |
| SPV FAT | Finance Supervisor | Baca semua CV; `budget.approve.finance`, `budget.approve.pembayaran`; kunci periode (TBD) | Web ERP |
| Tax Officer | Tax Staff | Baca semua CV untuk omzet dan pajak CV (izin TBD) | Web ERP |
| Account Payable | Account Payable | Transfer pengajuan bersumber dana rekening PT, `budget.ap.bayar` | Web ERP |
| Pemohon | Karyawan Marketing, HR, GA | `budget_pemohon_*` | Web ERP |
| Direktur | Direksi | Baca laporan dan konsolidasi (izin TBD) | Web ERP |

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
- Nama CV sudah menyimpang antar sumber (dua beda singkatan, satu berkarakter tak terlihat); pencocokan otomatis tanpa penetapan manusia tidak aman.
- Angka waktu kerja dari survei belum dikonfirmasi wawancara.

## Belum Diputuskan (TBD)

1. Makna rekening CV 1299xx di buku PT, dan buku mana yang jadi dasar laporan pajak CV.
2. Apakah hutang supplier CV adalah hutang ke PT atas barang yang dijual, dan bentuk dokumennya.
3. Format dan frekuensi impor mutasi rekening.
4. Nama izin dan bentuk penyimpanan penugasan CV (paket izin atau penugasan terpisah).
5. Siapa yang boleh mengunci dan membuka periode.
6. Kapan PT ikut konsolidasi.
7. Penomoran COA CV tetap 3 digit FINCON atau diselaraskan dengan akun Accurate, dan pemetaan fee marketplace ke COA CV.
8. Pembagian pemegang CV: mengikuti enam kelompok FINCON atau ditetapkan ulang.

## Dokumen Terkait

- [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] · [[ADR - 0068 Buku Besar Konsolidasi 40 CV di Luar Accurate]] · [[ADR - 0001 Akuntansi via Accurate]]
- [[APP - Buku Besar Konsolidasi CV FINCON]] · [[Finance - FAT Persona]] · [[Finance - Big Pictures]]
- [[Microservices - Procurement Service]] · [[Microservices - Payroll Service]] · [[Microservices - Integration Service]] · [[External - Accurate]]
- [[REF - Kepemilikan Data]] · [[CORE - RBAC dan Permission Set]]

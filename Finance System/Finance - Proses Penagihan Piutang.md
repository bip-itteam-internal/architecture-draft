# Finance - Proses Penagihan Piutang

## Deskripsi

*Proses P14, penagihan piutang, dari [[Finance - Proses Bisnis dan Kebutuhan Sistem]]. Dok ini memuat tujuan, cara dikerjakan hari ini, yang sudah ada di ERP, alur target di sistem, celah yang harus ditutup, kontrol yang wajib dijaga, dan ukuran untuk membuktikan efisiensinya. Pencocokan retur dan piutang terbuka ada di [[Finance - Proses Retur dan Piutang Marketplace]]; dok ini tentang mengejar uang yang tertahan.*

- **Status**: ⚠️ **Implemented (ada catatan)**. Umur piutang marketplace dan B2B sudah terbaca di ERP dan dinilai KPI otomatis; pencatatan tindak lanjut penagihan (kontak, janji bayar) belum ada.
- **Sumber**: [[Finance - FAT Persona]] (peran AR Leader dan AR Staff), survei alur kerja Finance 14 sampai 16 September 2026, dan kode `bip-erp` dan `erp-frontend` di `origin/main` 2026-09-17.
- **Kelompok celah**: **A** sudah ada, tinggal dipakai · **B** sudah ada, perlu diperbaiki · **C** belum ada, perlu dibangun (definisi di dok induk).

## Tujuan

Uang yang tertahan di pelanggan tertagih, umur piutang terkendali, dan setiap tindak lanjut penagihan tercatat sehingga bisa diteruskan siapa pun.

## Hari ini

- Menurut rancangan peran di [[Finance - FAT Persona]]: porsi piutang di atas 60 dan 90 hari serta uang tertagih per minggu dipantau, tetapi janji bayar, janji yang lewat, dan hasil per cara hubung dicatat di luar sistem karena belum ada log kontak; status "sudah dihubungi" juga belum tercatat.
- *Survei 2026-09*: piutang dicek harian lewat basis data kerja dengan memperbarui tanggal penerimaan dan retur; piutang minus ditelusuri karena ada penerimaan yang berubah jadi retur; piutang terbuka direkonsiliasi dengan retur.
- Posisi AR Leader, pemilik penagihan menurut rancangan peran, per 2026-09-17 belum punya pemegang aktif.

## Sudah ada di ERP

- Umur piutang marketplace: `GET /transactions/orders/piutang/summary`, tren posisi per akhir bulan `GET /transactions/orders/piutang/tren`, dan ekspor `GET /transactions/orders/piutang/export` di integration-service (`bip-erp/services/integration/main.go:1339-1341`); layar piutang per marketplace dan uang gantung di `erp-frontend/src/app/(main)/finance/piutang/` (all, shopee, tiktok, lazada, uang-gantung).
- Piutang B2B dan kategori pelanggan: `GET /accounting/receivables` dan `GET /accounting/customer-categories` (`bip-erp/services/integration/main.go:1514-1515`), dipakai dashboard posisi AR Leader (`erp-frontend/src/features/finance/posisi/data/ar-leader.ts`).
- KPI AR otomatis dari tren piutang per akhir bulan, sebagai metrik tim dan bukan per orang (`bip-erp/services/employee/kpi_sumber_ar.go:13-28`).

## Aturan kolom

Porsi piutang lewat 14 hari memuat yang lewat 60 hari, dan yang lewat 60 hari memuat yang lewat 90 hari. Ketiganya himpunan bersarang, bukan kelompok yang saling lepas: menjumlahkannya menghitung uang yang sama berkali-kali (`bip-erp/services/employee/kpi_sumber_ar.go:48-51`).

## Alur target

Daftar piutang jatuh umur per pelanggan atau toko → ditugaskan ke penagih → kontak, janji bayar, dan hasilnya dicatat di ERP → pengingat saat janji bayar lewat → pelunasan tercocokkan otomatis lewat penerimaan dan retur ([[Finance - Proses Penjualan Marketplace dan Uang Masuk]], [[Finance - Proses Retur dan Piutang Marketplace]]) → laporan umur piutang dan uang tertagih untuk Supervisor FAT.

## Celah

- **A** Tetapkan pemilik proses penagihan, karena posisi AR Leader belum punya pemegang aktif.
- **B** Piutang minus dan pengecualian retur ditandai sistem, bukan ditelusuri di basis data kerja (sama dengan daftar pengecualian di P4).
- **C** Log kontak, janji bayar, dan pengingat janji yang lewat.
- **TBD** Pembagian penagihan antara piutang marketplace (uang tertahan di platform) dan piutang pelanggan B2B, dan cara menagih masing-masing.
- **TBD** Aturan penghapusan atau koreksi piutang dan siapa yang menyetujuinya; belum ditemukan di kode.

## Kontrol wajib

Penagih tidak menghapus atau mengoreksi piutang sendiri tanpa persetujuan peran lain; pelunasan dicatat dari penerimaan uang, bukan dari laporan penagih.

## Ukuran efisiensi

Porsi piutang lewat 60 dan 90 hari per akhir bulan; uang tertagih per minggu; jumlah janji bayar yang lewat tanpa tindak lanjut.

Sumber data baseline: tren piutang per akhir bulan (`/transactions/orders/piutang/tren`, sudah dipakai KPI AR); catatan penagihan (belum ada di sistem).

## Proses terkait

- P3: [[Finance - Proses Penjualan Marketplace dan Uang Masuk]]
- P4: [[Finance - Proses Retur dan Piutang Marketplace]]
- P5: [[Finance - Proses Rekonsiliasi Kas Toko dan Bank]]

## Dokumen Terkait

- [[Finance - Proses Bisnis dan Kebutuhan Sistem]] · [[Finance - Kalender dan Rantai Tenggat]] · [[Finance - Sambungan dan Permintaan Data Lintas Departemen]] · [[Finance - FAT Persona]]
- [[Microservices - Integration Service]] · [[Finance - Dashboard per Posisi (FAT)]]

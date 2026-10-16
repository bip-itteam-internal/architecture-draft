# ANALISA - Cashflow Tujuh Komponen Uang Keluar

Papan kerja untuk [[ADR - 0184 Forecast Kas Mingguan Mencakup Tujuh Komponen Uang Keluar, Dibagi Empat Minggu, Realisasi Bertahap]] (🟢 Diterima 2026-10-16, Azzerith). Dok domain: [[Finance - Serapan Anggaran dan Cost Control]], bagian *Cashflow Tujuh Komponen*.

## Kebutuhan sebenarnya

Cost Control merencanakan dan memantau **seluruh uang keluar bulanan**. Forecast yang ada sekarang hanya mengukur 6 akun beban, sehingga KPI #4 tidak mengukur pekerjaan cashflow yang sebenarnya dilakukan Finance sejak Juli 2026.

## Task

Setiap task satu repo dan satu PR. Urutannya: BE dulu, lalu FE. Issue induk dibuat di bip-erp.

| # | Repo | Task | Bergantung | Catatan |
|---|---|---|---|---|
| C0 | (manual) | Verifikasi bagan akun Accurate prod: isi 5201, 5102, 53xx, 61xx, 62xx, 73xx; daftar akun penyusutan; akun persediaan/pembelian material. Baca saja | — | Fixture test memakai 5201 = "Beban Admin E-Commerce". Pemetaan **tidak boleh** dibangun sebelum C0 |
| C1 | bip-erp (integration) | Pemetaan akun → 7 komponen berbasis nomor/awalan di satu tempat, dengan penyusutan dikecualikan. Pembagian 4 minggu (minggu 4 = tanggal 22–akhir) di `minggu_periode.go`. Laporan mingguan per komponen; jumlah sebulan = Σ proyeksi komponen. Penyegar realisasi diperluas ke akun komponen. Respons membawa `komponen` dan `sifat_realisasi` per baris | C0 | Kontrak laporan mingguan berubah, jadi deploy BE sebelum FE. Atur proyeksi (ADR 0161) tetap jalan untuk 4 minggu |
| C2 | bip-erp (integration) | Isian proyeksi per komponen per bulan (Material, BOP, Pajak, Aset) dan anggaran aset tahunan: entitas, CRUD bergerbang `finance.anggaran.kelola`, sisa anggaran aset tahun berjalan | C1 | Pola isian sama dengan pagu gabungan. BOP = isian + RAPB 5xxx bila ada, dikunci supaya tidak dihitung ganda |
| C3 | bip-erp (integration + finance + employee) | Realisasi tahap 1 per komponen: Pajak dari `pajak_setoran_accurate`, Aset dari salinan aset tetap, Material dari akun hasil C0. Total uang keluar riil dari salinan ADR 0163 ditampilkan berdampingan. KPI #4: employee tidak lagi menyalin angka "6 akun"; penyebut cakupan dibaca dari respons | C1, C2 | Bisa jadi 2 PR (integration + employee). employee-service ikut deploy |
| C4 | erp-frontend | Tab Forecast Mingguan per komponen: ringkasan 4 minggu, rincian per komponen (lalu per akun), penanda akrual/kas, total uang keluar riil sebagai pembanding, seksi isian proyeksi komponen + anggaran aset (sisa tahun berjalan), Atur proyeksi untuk 4 minggu | C1–C3 | Deploy sesudah BE |
| C5 | (Finance/HRD) | Konfirmasi asumsi A1–A7 ADR 0184; HRD memutuskan apakah skor Juli–September dihitung ulang | — | Jawaban A1 membuka tahap 2 |
| C6 | bip-erp | Tahap 2: sumber realisasi per komponen diganti ke basis kas sesuai jawaban A1 | C5 | Kontrak layar dan KPI tidak berubah |

## Pertanyaan terbuka untuk Finance (A1–A7 di ADR)

1. Saat menyusun realisasi cashflow secara manual, angka uang keluar per komponen diambil dari laporan atau menu Accurate apa?
2. Siapa yang mengisi proyeksi Material, BOP, Pajak, dan Aset, dan dari sumber apa?
3. Aset: apakah anggaran tahunan ikut total bulanan, atau cukup ditampilkan sebagai info sisa?
4. Bulan berisi 5 minggu: minggu ke-5 digabung ke minggu 4? (Asumsi sementara: ya.)
5. Beban gaji: dari RAPB 6100/6200, atau dari payroll?
6. Apa isi akun 7300?
7. Perlengkapan produksi: dari catatan biaya perlengkapan yang sudah ada, atau dari akun tertentu?

## Verifikasi per tahap

- **C1:** laporan September 2026, yang menurut Finance sudah lengkap, menampilkan tujuh komponen dalam 4 minggu, dan Σ proyeksi = total yang ditampilkan.
- **C3:** skor KPI #4 periode berjalan berubah sesuai definisi baru, dan skor yang sudah beku tetap.
- **Semua:** Cost Control membandingkan layar dengan Excel cashflow mereka untuk September.

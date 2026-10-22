# ANALISA - Cashflow Tujuh Komponen Uang Keluar

Papan kerja untuk [[ADR - 0184 Forecast Kas Mingguan Mencakup Tujuh Komponen Uang Keluar, Dibagi Empat Minggu, Realisasi Bertahap]] (🟢 Diterima 2026-10-16, Azzerith). Dok domain: [[Finance - Serapan Anggaran dan Cost Control]], bagian *Cashflow Tujuh Komponen*.

## Kebutuhan sebenarnya

Cost Control merencanakan dan memantau **seluruh uang keluar bulanan**. Forecast yang ada sekarang hanya mengukur 6 akun beban, sehingga KPI #4 tidak mengukur pekerjaan cashflow yang sebenarnya dilakukan Finance sejak Juli 2026.

## Task

Setiap task satu repo dan satu PR. Urutannya: BE dulu, lalu FE. Issue induk dibuat di bip-erp.

| # | Repo | Task | Bergantung | Catatan |
|---|---|---|---|---|
| C0 | (manual) | Verifikasi bagan akun Accurate prod: isi 5201, 5102, 53xx, 61xx, 62xx, 73xx; daftar akun penyusutan; akun persediaan/pembelian material. Baca saja | — | Fixture test memakai 5201 = "Beban Admin E-Commerce". Atas arahan Azzerith 2026-10-16, C1 dibangun lebih dulu memakai nomor akun dari Finance. C0 menjadi **verifikasi sesudah deploy** (cocokkan laporan September 2026 dengan Excel Finance) |
| C1 ✅ PR bip-erp#3233 | bip-erp (integration) | Pemetaan akun → 7 komponen berbasis nomor/awalan di satu tempat, dengan penyusutan dikecualikan. Pembagian 4 minggu (minggu 4 = tanggal 22–akhir) di `minggu_periode.go`. Laporan mingguan per komponen; jumlah sebulan = Σ proyeksi komponen. Penyegar realisasi diperluas ke akun komponen. Respons membawa `komponen` dan `sifat_realisasi` per baris | C0 | Kontrak laporan mingguan berubah, jadi deploy BE sebelum FE. Atur proyeksi (ADR 0161) tetap jalan untuk 4 minggu |
| C2 | bip-erp (integration) | Isian proyeksi per komponen per bulan (Material, BOP, Pajak, Aset) dan anggaran aset tahunan: entitas, CRUD bergerbang `finance.anggaran.kelola`, sisa anggaran aset tahun berjalan | C1 | Pola isian sama dengan pagu gabungan. BOP = isian + RAPB 5xxx bila ada, dikunci supaya tidak dihitung ganda |
| C3a 🟡 PR bip-erp#3258 (issue #3256) | bip-erp (integration) | Realisasi Aset dari `accurate_fixed_assets`, sisa anggaran aset tahun berjalan, akun beban pajak dikeluarkan dari semua komponen (PKB tetap ops adum), isian masuk basis akurasi per komponen (BOP, Aset), kunci minggu isian | C2 | Bertumpuk di atas #3236 |
| C3b 🟡 PR bip-erp#3260 (issue #3259) | bip-erp (finance + integration + compose) | Realisasi Pajak dari setoran lewat rute mesin `/internal/forecast-kas/pajak`, uang keluar riil lewat `/internal/forecast-kas/arus-keluar`, Pajak masuk basis bila terukur. Hanya entitas PT Bharata (asumsi, tanya Finance) | C3a | Env baru `FINANCE_MODULE_URL`/`FINANCE_SERVICE_KEY` di integration (amandemen ADR 0184, 2026-10-18). Deploy finance dulu |
| C3c 🟡 PR bip-erp#3262 (issue #3261) | bip-erp (integration) | Realisasi Material = Σ jenis pembelian ("Penerimaan Barang", "Faktur Pembelian"; "Retur Pembelian" mengurangi) di 1601/1602/1603, bukan mutasi bersih. Disimpan penyegar harian 03:50; masuk basis bila ketiga akun terukur | C3b, C0 | Akun dan jenis diukur dari Accurate prod 2026-10-18 (izin Azzerith). September 2026 = Rp385.370.294 |
| C3 (rencana awal) | bip-erp (integration + finance + employee) | Realisasi tahap 1 per komponen: Pajak dari `pajak_setoran_accurate`, Aset dari salinan aset tetap, Material dari akun hasil C0. Total uang keluar riil dari salinan ADR 0163 ditampilkan berdampingan. Keluarkan akun beban pajak dari `ops_adum` (lihat Catatan dari C1). Penyebut KPI sudah dibaca dari `jumlah_akun` sejak C1 | C1, C2 | Bisa jadi 2 PR (integration + employee). employee-service ikut deploy |
| C4a 🟡 PR erp-frontend#2570 (issue #2568) | erp-frontend | Tampilan: tujuh komponen (buka ke akun), badge Akrual/Kas, sebab belum terukur (bukan Rp 0), kartu pembanding uang keluar riil, anggaran aset + sisa. Fallback backend lama | C1–C3c | Deploy sesudah BE |
| C4b 🟡 PR erp-frontend#2572 (issue #2571) | erp-frontend | Isian proyeksi komponen (Material/BOP/Pajak/Aset) + anggaran aset tahunan (form, gerbang `finance.anggaran.kelola`, pesan 422 kunci minggu); Sheet Atur proyeksi memakai `proyeksi_rencana`/`total_anggaran_bulan` | C4a | Dialog (bukan Sheet). Daftar komponen penerima isian disalin di FE karena laporan belum membawa penanda; usulan BE: field `dapat_diisi` di `komponen[]` |
| C4 (rencana awal) | erp-frontend | Tab Forecast Mingguan per komponen: ringkasan 4 minggu, rincian per komponen (lalu per akun), penanda akrual/kas, total uang keluar riil sebagai pembanding, seksi isian proyeksi komponen + anggaran aset (sisa tahun berjalan), Atur proyeksi untuk 4 minggu | C1–C3 | Deploy sesudah BE |
| C3d 🟡 PR bip-erp#3325 (issue #3321) | bip-erp (integration) | Realisasi Aset dari buku besar (1801–1806 + Aset dlm Penyelesaian), netto per transaksi, penyegar 04:30, bukan dari register | C3a | Amandemen ADR 0184 Decision 5 (2026-10-20) |
| C7a 🟡 PR bip-erp#3362 (issue #3357) | bip-erp (integration) | CapEx di luar cashflow: Aset keluar dari `komponen[]`, total, akurasi, dan KPI. Anggaran CapEx per **periode** (rute `capex-periode` menggantikan `aset-tahunan`). Ditambah `laporan.capex` berisi proyeksi/bulan, realisasi bulan dan kumulatif, serta sisa | C3d | Amandemen ADR 0184 Decision 3, 2026-10-21. Deploy BE dulu |
| C7b 🟡 PR erp-frontend#2674 (issue #2656) | erp-frontend | Bagian "Belanja Modal (CapEx)" di bawah forecast, dialog anggaran periode (pemilih bulan lokal), bersihkan kartu/dialog aset tahunan | C7a (kontrak sama, dikerjakan paralel) | Deploy sesudah C7a |
| C6a ✅ merged PR bip-erp#3386 (issue #3376) | bip-erp (integration) | Penyegar arus kas keluar per akun lawan per minggu, meniru Arus Kas (Langsung): populasi kas = semua CASH_BANK daun dari bagan, pengecualian jenis Penerimaan Penjualan, rute GET /accounting/anggaran/arus-kas | ADR 0184 tahap 2 (2026-10-21) | Uji kelayakan prod September cocok untuk 7 akun; Utang Usaha selisih Rp 2.500 |
| C6b ✅ merged PR bip-erp#3394 (issue #3393) | bip-erp (integration) | Pemetaan akun lawan → komponen (tabel ADR tahap 2), realisasi semua komponen dari C6a, minus per akun per minggu, sifat kas; bulan belum tersinkron tetap tahap 1 | C6a | Pertanyaan Finance: 5201, 72xx tanpa PPh/PPN, 6101 |
| C6c ✅ merged + deploy prod 2026-10-21, PR erp-frontend#2697 (issue #2691) | erp-frontend | Layar Forecast Mingguan: rincian per akun Arus Kas, sel `diganti_kas` "Dipantau di Serapan", kontrol tak terpetakan/dikecualikan | C6b | Belum dilihat di browser |
| C6d 🟡 PR bip-erp#3442 (issue #3440) | bip-erp (integration) | Kunci transaksi `transId` menggantikan jenis+nomor. Jurnal penutupan bulan bernomor sama ("September 2026") tidak lagi terlebur. Fungsi `KunciTransaksi` dipakai juga untuk netting aset | C6a | Ditemukan dari laporan Arus Kas September cetak ulang 22 Okt (62 akun cocok; 5104/penyusutan/6222 menyimpang). Gerbang pasca-deploy: 62 akun tetap cocok |
| C6e 🟡 PR bip-erp#3433 (issue #3430) | bip-erp (assistant) | Copilot `anggaran_mingguan` mengenali bulan berbasis kas | C6b | Deploy assistant-service |
| C5 | (Finance/HRD) | Konfirmasi asumsi A1–A7 ADR 0184; HRD memutuskan apakah skor Juli–September dihitung ulang | — | Jawaban A1 membuka tahap 2 |
| C6 | bip-erp | Tahap 2: sumber realisasi per komponen diganti ke basis kas sesuai jawaban A1 | C5 | Kontrak layar dan KPI tidak berubah |

## Catatan dari C1 (bip-erp#3233, judge 2026-10-16)

- ⛔ **Jangan jumlahkan akun beban pajak ke komponen pajak.**
  - Akun Beban PPh 21, PPh Final UMKM, PPh Badan 31E, PPh 23, PPN KMS Gedung, Denda Pajak, dan Pajak KOL ada di `DaftarKomponenOpex`. Bila nomornya 62xx/73xx, C1 memasukkannya ke `ops_adum`.
  - Saat C3 mengisi komponen `pajak` dari setoran nyata, akun-akun itu **wajib dikeluarkan** dari `ops_adum`. Kalau tidak, rupiah yang sama terhitung dua kali dan Σ komponen menggelembung tanpa ada galat.
- **Realisasi tanggal 29–31 untuk bulan Agustus 2026 ke belakang hilang tanpa tanda.**
  - Baris lama `minggu=5` diabaikan.
  - Baris lama minggu 4 hanya mencakup tanggal 22–28, dan penyegar hanya menarik ulang bulan berjalan dan bulan lalu.
  - Pilihannya: gabungkan baris minggu 5 lama saat dibaca bila stempelnya lebih tua dari deploy, atau tandai minggu 4 periode itu sebagai belum tersinkron.
- **Timeout penyegar 20 menit masih berupa perkiraan.** Setelah run pertama di prod, baca `panggilan_accurate` dan durasinya di log.

## Catatan dari C0 (bagan akun Accurate prod, diukur 2026-10-18, baca saja)

- **Cocok dengan Finance:**
  - 5201 = Biaya Tenaga Kerja Tidak Langsung.
  - 5102 = Biaya Angkut Pembelian.
  - 53xx = BOP Variabel (5301–5314).
  - Fixture test lama yang menyebut 5201 "Beban Admin E-Commerce" hanyalah data test.
- **Beban pajak ada di 72xx** (7201–7212), bukan 62xx/73xx. Dengan predikat C1, akun-akun ini memang tidak pernah masuk ops adum. Kekhawatiran hitung ganda di "Catatan dari C1" ternyata tidak terjadi di prod, tetapi pengecualian C3a tetap dipertahankan sebagai penjaga.
- **Bukan uang keluar, tetapi ikut komponen.** Perlu ditanyakan ke Finance:
  - 7303 "Laba/Rugi Penjualan, Pembelian, & Revaluasi Aset" dan 7304 "Laba/Rugi Disposisi Aset Tetap" masuk ops adum (asumsi A6).
  - 5313 "Laba/Rugi Selisih Persediaan" masuk BOP.
- **Material.** Persediaan 1601/1602/1603 didebit oleh jenis "Penerimaan Barang". Jenis "Pengambilan Bahan Baku" dan "Penyesuaian Persediaan" adalah pemakaian/koreksi, sehingga mutasi bersih tidak bisa dipakai sebagai realisasi. Contoh 1601 September: mutasi bersih −65,6 jt, sedangkan pembelian 82,9 jt.

## Catatan dari Arus Kas (Langsung) Accurate (A1, 2026-10-20)

Finance menjawab A1: sumber cashflow manual mereka adalah **laporan arus kas**. Yang cocok adalah **Laporan → Keuangan → Arus Kas (Langsung)**. Export September 2026 PT Bharata sudah dibaca. Laporan itu menyusun uang keluar per **akun lawan** transaksi kas/bank.

- **Cocok persis dengan buku besar prod.**
  - Utang Gaji 2202, jenis "Pembayaran", berjumlah Rp 587.564.829.
  - Aset dlm Penyelesaian Gudang Baru 1728 berjumlah Rp 461.213.877, terdiri dari Jurnal Umum Rp 345,2 jt dan Pembayaran Rp 116,0 jt.
- **Perkiraan per komponen, September:**

  | Komponen | Baris laporan | Nilai |
  |---|---|---|
  | Material | Kas untuk Pembelian | Rp 832 jt (akrual kita Rp 385 jt) |
  | BOP | — | Rp 8 jt |
  | Marketing | termasuk iklan Rp 2.294 jt | Rp 2.279 jt |
  | Gaji | Utang Gaji + asuransi | ~Rp 644 jt |
  | Ops adum | Adum + Utang Beban + bank | ~Rp 321 jt |
  | Pajak | Utang PPN/PPh, PPh 25 dibayar di muka | ~Rp 240 jt; akunnya sama dengan daftar setoran finance, jadi C3b di jalur yang benar |
  | Aset | Aset dlm Penyelesaian | ~Rp 461 jt |

- **Akibatnya:**
  - Sumber realisasi Aset diganti ke buku besar (bip-erp#3321, amandemen ADR 0184 Decision 5).
  - Gaji akrual jauh di bawah kas, karena gaji dibayar lewat Utang Gaji.
  - Ada uang keluar yang belum masuk komponen mana pun: Anggaran FO/Kegiatan, Prepaid, piutang karyawan, investasi, dan cicilan kreditur.
  - Laporan itu juga memuat baris yang bukan kas (Akumulasi Penyusutan −1,9 jt, 7303 −0,3 jt), jadi jangan dipakai mentah sebagai acuan.
- **Untuk tahap 2 (C6):** "uang keluar" **tidak** bisa dikenali dari jenis transaksi saja. Utang Beban 2205 punya Pembayaran Rp 55,6 jt, ditambah sebagian Jurnal Umum yang menyentuh bank. Penandanya adalah transaksi yang menyentuh akun kas/bank, jadi perlu menggabungkan riwayat akun lawan dengan riwayat kas/bank per nomor transaksi.
- **Pertanyaan yang tersisa untuk Finance:** dari "Kas untuk Pembelian" Rp 832 jt, bagian mana yang mereka hitung sebagai Material, dan sisanya masuk komponen apa?

## Catatan dari prod sesudah deploy C3d (2026-10-21, baca saja)

- **Penyegar Aset (04:30) sukses pada run pertama**, 21 Okt, untuk Januari–September 2026. Durasinya 7,6 detik. Lognya mencatat `dinetralkan=0` di semua bulan, dengan `dilepas` antara 1 dan 13.
- **`dilepas` di April (13) adalah kredit asli, bukan reklasifikasi:**
  - 12 baris *Disposisi Aset Tetap* (penjualan laptop bekas ke Flash Computer, 28 April, Rp 91,4 jt);
  - satu Jurnal Umum penyusutan ATB yang dikreditkan **langsung** ke 1806 Aset Tetap Lainnya, bukan ke akun akumulasi.
- **Pola reklasifikasi Aset dlm Penyelesaian ke aset tetap terbukti satu dokumen.** Dokumen berjenis "Aset Tetap" mengkredit akun ADP dan mendebit 1802 dengan nomor yang sama. Sudah terjadi tiga kali:

  | Dokumen | Dari | Nilai |
  |---|---|---|
  | AB-003, 01/04/2025 | 1701 Gerbang Utama | Rp 367,4 jt |
  | AB-005, 01/07/2025 | 1702 Office Lt 3 | Rp 2.293,3 jt |
  | AB-006, 24/08/2025 | 1703 Gedung 3 Lt | Rp 3.531,1 jt |

  Netting jenis + nomor di C3d menangkap pola ini. Saat Gudang Baru (1728, saldo Rp 2,68 M, progres 95% per September) direklasifikasi, angkanya tidak akan dihitung dua kali, **asalkan** Finance memakai dokumen "Aset Tetap" yang sama. Sesudah reklasifikasi itu, cek log: `dinetralkan` harus ≥ 1.
- **Akrual dan kas berbeda untuk mesin.** Pembelian mesin April (AMP-015/016, Rp 178,3 jt) tercatat sebagai dokumen "Aset Tetap" di 1803. Di Arus Kas (Langsung), uangnya kemungkinan muncul di "Kas untuk Pembelian" saat faktur dibayar. Ini perlu diperhatikan saat pemetaan C6: jangan sampai terhitung di Aset dan Material sekaligus.

## Catatan dari jawaban Finance 2026-10-20 (WA Tika)

Cara Finance menyusun realisasi:
1. Buka Arus Kas (Langsung), periode bulan berjalan, semua cabang.
2. Ambil **angka minus saja**. Uang masuk (penjualan, pendapatan non-operasional) tidak dihitung.
3. Klasifikasikan per anggaran:
   - akun yang berkaitan dengan pajak masuk realisasi Pajak;
   - piutang selain pajak masuk Ops Umum;
   - **tidak semua beban marketing** dihitung: beban yang memotong uang masuk di toko marketplace (mis. admin toko) bukan uang yang kita keluarkan;
   - aset lancar: Anggaran FO masuk ops Marketing, Anggaran Kegiatan masuk ops Adum, PPN Masukan masuk Pajak, Aset dlm Penyelesaian masuk Aset/capex;
   - utang dipilah per baris, rinciannya belum disebut.
4. Masalah yang Finance sendiri sebutkan: laporan ini tidak bisa ditarik per minggu, jadi mereka memakai total sebulan. **C6 menjawab ini**, karena baris yang sama dibangun ulang dari buku besar per transaksi yang bertanggal.

Pemetaan per baris yang masih menunggu koreksi Finance (WA 2026-10-21):
- beban marketing mana yang tidak dihitung;
- apakah seluruh "Kas untuk Pembelian" masuk Material;
- klasifikasi tiap utang;
- Investasi Elite SK, Prepaid Desty, Utang kepada Kreditur, dan Akumulasi Penyusutan.

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

# ADR - 0184 Forecast Kas Mingguan Mencakup Tujuh Komponen Uang Keluar, Dibagi Empat Minggu, Realisasi Bertahap

> **Status**: 🟢 Diterima, 2026-10-16, oleh Azzerith (Opsi 3 beserta asumsinya disetujui di sesi `/analisa-kebutuhan`). **Tahap 1 merged ke `main` 2026-10-19, deploy prod TBD.** BE: bip-erp #3234, #3275 (pemulihan C2–C3c), #3276. FE: erp-frontend #2570, #2583, #2584. Rincian perilaku dan aturan membaca angka ada di [[Finance - Serapan Anggaran dan Cost Control]] §Cashflow Tujuh Komponen. Tahap 2 (A1) menunggu rekap laporan arus kas dari Finance. Asumsi A1–A7 di §Context menunggu konfirmasi Finance/HRD; jawabannya bisa mengubah sumber realisasi (tahap 2) tanpa mengubah keputusan lain. Mengamandemen [[ADR - 0161 Proyeksi Forecast Kas Mingguan Diatur Porsinya per Minggu oleh Cost Control, Jumlah Sebulan Tetap RAPB]] K1, K3, dan K5.

## Untuk Manajemen

**Apa yang berubah di layar.** Tab Forecast Mingguan di menu Anggaran & Cost Control tidak lagi hanya memuat 6 pos beban. Isinya kini **tujuh komponen uang keluar**:
- Pembelian material produksi
- BOP produksi
- Beban marketing
- Beban gaji
- Beban ops adum
- Pengeluaran pajak
- Pembelian aset

Untuk tiap komponen ditampilkan proyeksi dan realisasinya per minggu.

- **Proyeksi.** Operasional (marketing, gaji, adum) diambil dari RAPB tanpa penyusutan. Material, BOP, pajak, dan aset diisi sendiri oleh Cost Control. Pembelian aset juga menampilkan sisa anggaran tahunan yang masih berjalan.
- **Pembagian minggu.** Sebulan dibagi **4 minggu**. Minggu ke-4 menampung sisa hari di akhir bulan.
- **Total uang keluar riil.** Total uang yang benar-benar keluar dari rekening bank tampil berdampingan dengan total realisasi, supaya selisihnya terlihat.

**Siapa yang terdampak.** Cost Control (mengisi proyeksi komponen), pemegang KPI Cost Control #4 dan SPV Finance F4 (skor akurasi forecast), dan HRD (penilaian KPI).

**Apa yang TIDAK dijanjikan.**
- **Realisasi tahap pertama belum murni "uang yang benar-benar keluar".** Realisasi per komponen sementara diambil dari mutasi akun beban (akrual), dan layar menandainya begitu. Realisasi berbasis kas per komponen menyusul (tahap 2), setelah Finance menjelaskan sumber yang mereka pakai secara manual.
- **Skor KPI yang sudah beku (Juli–September) tidak dihitung ulang**, kecuali HRD memutuskannya. Laporan bulan-bulan itu tetap bisa dilihat dengan definisi baru.
- Pembagian minggu **bukan per kalender Senin–Minggu**.

**Perkiraan besaran kerja.** Tahap 1 sekitar 4 PR, backend lebih dulu. Tahap 2 sekitar 1–2 PR setelah sumber kas diputuskan.

## Deskripsi

*Forecast kas mingguan mengukur seluruh uang keluar bulanan dalam tujuh komponen: material, BOP, marketing, gaji, ops adum, pajak, dan aset. Cakupannya tidak lagi enam akun yang direproduksi dari berkas cashflow Juli. Jumlah sebulan = Σ proyeksi komponen, tidak lagi = RAPB. Sebulan dibagi empat minggu. Sumber realisasi per komponen diisolasi supaya bisa diganti dari akrual ke kas tanpa mengubah layar maupun KPI. KPI Cost Control #4 ikut definisi baru.*

- **Status**: 🟢 Diterima 2026-10-16 (Azzerith). Kode tahap 1 merged ke `main` 2026-10-19, deploy prod TBD
- **Path di repo** (rencana):
  - `bip-erp/services/integration/internal/usecase/kas_keluar_daftar.go` (diganti oleh pemetaan komponen)
  - `bip-erp/services/integration/internal/usecase/komponen_kas.go` (baru)
  - `bip-erp/services/integration/internal/usecase/minggu_periode.go`
  - `bip-erp/services/integration/internal/usecase/proyeksi_mingguan.go`
  - `bip-erp/services/integration/internal/usecase/laporan_mingguan.go`
  - `bip-erp/services/integration/internal/interface/http/anggaran_mingguan_handler.go`
  - `bip-erp/services/integration/internal/interface/http/anggaran_proyeksi_handler.go`
  - `bip-erp/services/integration/internal/worker/tasks/realisasi_mingguan_refresh.go`
  - `bip-erp/services/integration/internal/domain/entity/proyeksi_komponen.go` (baru)
  - `bip-erp/services/employee/kpi_sumber_forecast_kas.go`
  - `erp-frontend/src/features/finance/anggaran/components/tab-forecast-mingguan.tsx`
  - `erp-frontend/src/features/finance/anggaran/components/tabel-forecast-kas.tsx`
  - `erp-frontend/src/features/finance/anggaran/components/tabel-rincian-forecast.tsx`
  - `erp-frontend/src/features/finance/anggaran/components/sheet-atur-proyeksi.tsx`
  - `erp-frontend/src/features/finance/anggaran/components/seksi-proyeksi-komponen.tsx` (baru)
  - `erp-frontend/src/features/finance/anggaran/lib/rincian-forecast.ts`
- **Tanggal**: 2026-10-16

## Context

**Permintaan Finance 2026-10-16 (WA, diteruskan user).** Mulai Juli 2026, cashflow dihitung dari total uang yang benar-benar harus keluar dalam sebulan. Komponennya:
1. Pembelian (material produksi)
2. BOP Produksi
3. Beban Marketing (packing, iklan, ops)
4. Beban Gaji
5. Beban ops adum
6. Pengeluaran Pajak
7. Pengeluaran pembelian aset. Anggarannya tahunan, sehingga yang ditampilkan adalah sisa anggaran berjalan.

**Jawaban Finance atas pertanyaan susulan:**
- Proyeksi Operasional Marketing dan Operasional Umum diambil dari RAPB, **kecuali beban penyusutan**. Material, BOP, Pajak, dan Aset punya angka proyeksi sendiri.
- Realisasi = **uang yang benar-benar keluar**.
- Akun Operasional:
  - **6100** (Marketing), **6200** (Adum), **7300**;
  - pembayaran hutang beban ikut dihitung sebagai operasional, karena pencatatannya perpetual.
- BOP: **5201** (tenaga kerja tidak langsung), **5102** (biaya angkut pembelian), seluruh **5300**, dan perlengkapan produksi.
- Pembagian per minggu: **total sebulan dibagi 4**.
- Berlaku **mulai Juli 2026**.
- **KPI akurasi ≥ 95% ikut perhitungan baru.**

**Keadaan kode** (`bip-erp` origin/main 407e56df1, `erp-frontend` origin/main fc8e798e8; diverifikasi):
- **Cakupan.** Forecast saat ini hanya mencakup 6 akun, `DaftarAkunKasKeluar` (`services/integration/internal/usecase/kas_keluar_daftar.go:29-36`): Iklan, Pelatihan Karyawan, Program Careness, Registrasi/Administrasi/Perizinan, Uji Lab, Software.
  - Keenam akun itu direproduksi dari `Juli_Cashflow.pdf` (`:5-18`).
  - Daftar ini sengaja berupa subset supaya tidak mengukur hal yang sama dengan metrik #1 varians OPEX (`:20-24`).
  - Akun dicocokkan berdasarkan **nama**, bukan nomor.
- **Proyeksi** = RAPB (`anggaran_opex`) yang disaring ke 6 akun. Jumlah sebulan selalu = RAPB (`usecase/proyeksi_mingguan.go:79-123`, ADR 0161 K3).
- **Realisasi** = mutasi saldo akun **beban**, ditarik per akun per minggu lewat Accurate `glaccount/get-balance.do` (`worker/tasks/realisasi_mingguan_refresh.go:132-138`). Ini **akrual**, bukan kas.
- **Minggu** = potongan 7 hari dari tanggal 1, sehingga sebulan berisi 4–5 minggu. Pro-rata dihitung menurut jumlah hari (`usecase/minggu_periode.go:41-148`).
- **KPI #4** (`services/employee/kpi_sumber_forecast_kas.go`):
  - membaca `/accounting/anggaran/mingguan/kpi`;
  - rumus `akurasi = max(0, 100 − |100 − realisasi/proyeksi×100|)` dihitung dari total minggu selesai (`integration/internal/domain/entity/anggaran_mingguan.go:104-159`);
  - menyalin angka "6 akun" ke penyebut cakupan (`kpi_sumber_forecast_kas.go:201`).
- **Uang keluar riil yang sudah ada:**
  - total keluar per rekening per bulan, `kas_bank_arus_salinan.rekening[].keluar_sen` di finance-service ([[ADR - 0163 Salinan Saldo dan Arus Kas-Bank per Rekening Dimiliki Finance Service, Ditarik lewat Integration Service]]), tanpa pecahan komponen atau minggu;
  - setoran pajak per transaksi, `pajak_setoran_accurate` (`services/finance/pajak_setoran.go:41-67`).
  - Baris riwayat transaksi bank Accurate **tidak membawa akun lawan** (`integration/.../accurate_client_riwayat_akun.go:55-66`), sehingga uang keluar bank tidak bisa dipilah ke komponen tanpa menarik detail jurnal tiap transaksi.
- **Proyeksi non-RAPB yang sudah ada:**
  - kewajiban pajak per masa dengan `nilai` (`services/finance/pajak_kewajiban.go:40-86`), master-nya kosong di prod per dok Proses Pajak;
  - biaya perlengkapan produksi diisi manual per periode (`services/finance/biaya_variabel.go:33-53`);
  - utang faktur pembelian beserta jatuh temponya (`services/procurement/faktur.go:85-140`).
  - **Anggaran aset tahunan tidak ada di mana pun**: `git grep` atas capex, anggaran aset, dan pembelian aset hasilnya kosong.
- **Nomor akun.** Konstanta akun 5201, 5102, 5300, 6100, 6200, dan 7300 tidak ada di kode non-test. Di fixture test, 5201 dipakai sebagai "Beban Admin E-Commerce" (`anggaran_akun_seluruh_perusahaan_test.go:153`), bertentangan dengan arti 5201 versi Finance. **Pemetaan nomor harus diverifikasi ke bagan akun Accurate prod sebelum dipakai.**
- **Data prod belum diukur** di analisa ini: isi bagan akun 5xxx dan 7300, serta volume transaksi bank per bulan. Ini risiko, lihat Consequences.
- **Aturan bisnis.** `BUSINESS_LOGIC_IMPLEMENTATION.md` (Peraturan Perusahaan) tidak mengatur cashflow maupun anggaran.

**Asumsi** (belum dijawab Finance/HRD; dicatat supaya pekerjaan tidak tertahan):
- **A1.** Sumber realisasi kas per komponen: **TBD**. Tahap 1 memakai mutasi akun (akrual) dan menandainya di layar.
- **A2.** Proyeksi Material, BOP, Pajak, dan Aset diisi manual oleh Cost Control per komponen per bulan.
- **A3.** Anggaran aset diisi sekali per tahun dan ditampilkan sebagai sisa berjalan. Aset ikut total bulanan hanya bila proyeksi bulan itu diisi.
- **A4.** "Dibagi 4": sebulan selalu 4 minggu. Minggu 1–3 masing-masing 7 hari dari tanggal 1, minggu 4 berisi tanggal 22 sampai akhir bulan. Pembagian bawaan rata ¼, dan Atur proyeksi tetap tersedia.
- **A5.** Beban Gaji ikut RAPB lewat akun gaji di 6100/6200.
- **A6.** Akun 7300 ikut Operasional Adum.
- **A7.** Perlengkapan produksi untuk BOP diambil dari catatan biaya variabel produksi yang sudah ada.

## Decision

1. **Cakupan = tujuh komponen.**
   - Pemetaan akun ke komponen berbasis **nomor akun dan awalan** (5201, 5102, 53xx, 61xx, 62xx, 73xx), menggantikan pencocokan nama 6 akun.
   - Pemetaan ditulis di **satu** tempat di integration-service dan dikirim ke layar lewat respons. FE tidak menyalinnya.
   - **Akun penyusutan dikecualikan** secara eksplisit.
   - Material, Pajak, dan Aset adalah komponen yang angkanya berasal dari isian dan sumbernya sendiri, bukan dari RAPB.
2. **Jumlah sebulan = Σ proyeksi komponen.** Amandemen ADR 0161 K3.
   - Operasional (marketing, gaji, adum) diambil dari RAPB tanpa penyusutan.
   - Material, BOP, Pajak, dan Aset diambil dari **isian proyeksi per komponen per bulan** oleh Cost Control. Gerbang izinnya `finance.anggaran.kelola`, dengan pola isian yang sama dengan anggaran gabungan.
   - BOP = isian proyeksi ditambah bagian RAPB bila akun 5xxx dianggarkan. Aturannya dikunci di task BE supaya tidak terhitung ganda.
3. **Aset tahunan.** Anggaran aset diisi per tahun, dan layar menampilkan "sisa anggaran tahun berjalan" = anggaran tahun − realisasi aset sejak Januari. Aset ikut total bulanan hanya lewat proyeksi bulan itu.
4. **Empat minggu.** Amandemen ADR 0161 K5.
   - Minggu 1–3 masing-masing 7 hari dari tanggal 1; minggu 4 berisi tanggal 22 sampai akhir bulan.
   - Porsi bawaan rata ¼.
   - Atur proyeksi (K2, K4, K6–K13) tetap berlaku untuk empat minggu itu.
   - Aturan minggu tetap ditulis di satu fungsi (`minggu_periode.go`).
5. **Realisasi bertahap, sumbernya diisolasi.**
   - Realisasi per komponen dihitung oleh satu antarmuka sumber per komponen.
   - **Tahap 1:**
     - Operasional dan BOP memakai mutasi akun (akrual, penyegar yang sudah ada diperluas ke akun komponen);
     - Pajak memakai setoran nyata (`pajak_setoran_accurate`);
     - Aset memakai salinan aset tetap (tanggal perolehan × biaya). **Diamandemen 2026-10-20 (Azzerith):** sumbernya diganti ke **buku besar** akun aset tetap 1801–1806 ditambah akun *Aset dlm Penyelesaian* (1701, 1702, 1703, 1726, 1727, 1728, 1730, 1737). Netto dihitung per transaksi, jadi reklasifikasi tidak terhitung dua kali dan pelepasan tidak dihitung (bip-erp#3321, PR #3325). Alasannya, uang keluar aset terbesar September 2026 (Gudang Baru Rp 461,2 jt) tercatat di Aset dlm Penyelesaian, yang tidak ada di register aset tetap;
     - Material memakai mutasi akun persediaan atau pembelian (diputuskan di task BE dari bagan akun prod).
   - Respons menandai sifat realisasi tiap komponen (`akrual` atau `kas`).
   - **Tahap 2** mengganti sumber per komponen ke basis kas setelah A1 terjawab, tanpa mengubah kontrak layar maupun KPI.
6. **Total uang keluar riil berdampingan.** Laporan bulanan menampilkan Σ uang keluar seluruh rekening bank dari salinan ADR 0163, di samping total realisasi komponen, sebagai kontrol. Angka ini **tidak** dipakai KPI.
7. **KPI #4 ikut definisi baru.**
   - Rumus akurasi tidak berubah; yang berubah populasi dan proyeksinya.
   - employee-service tidak lagi menyalin angka "6 akun". Penyebut cakupan dibaca dari respons.
   - Berlaku untuk periode yang belum beku. Skor Juli–September yang sudah beku tidak dihitung ulang tanpa keputusan HRD.
   - *Urutan penerapan (diputuskan Azzerith 2026-10-16, setelah judge C2):*
     - Sampai realisasi komponen isian (Material, Pajak, Aset, bagian isian BOP) tersedia di C3, **akurasi forecast dan KPI tetap dihitung dari bagian RAPB saja**.
     - Proyeksi yang memuat isian dikirim di field terpisah dengan nama yang tidak mungkin tertukar. Satu objek ringkasan minggu tidak boleh memuat proyeksi dan akurasi dari populasi yang berbeda.
     - Isian masuk basis akurasi bersamaan dengan realisasinya di C3. Sejak saat itu, isian bulan berjalan wajib tunduk pada kunci minggu dan batas ubah yang sama (ADR 0161).
     - *Penerapan C3 (2026-10-18):*
       - C3 dipecah menjadi tiga bagian:
         - **C3a** (bip-erp#3256): Aset, sisa anggaran aset, dan pengeluaran beban pajak dari ops adum;
         - **C3b** (bip-erp#3259): Pajak dan total uang keluar riil;
         - **C3c**: Material, menunggu bagan akun prod.
       - Isian masuk basis **per komponen**, hanya bila sumber realisasi komponen itu terukur. Contohnya salinan aset sudah disinkron, atau setoran pajak terbaca dari finance.
       - Isian Material tetap di luar basis sampai C3c.
8. **Pemisahan dari metrik #1 dilepas secara sadar.** Varians OPEX (metrik #1) dan forecast (#4) kini sama-sama memuat OPEX. Ini permintaan Finance, dan alasan subset di `kas_keluar_daftar.go:20-24` tidak berlaku lagi.

## Consequences

- **ADR 0161 diamandemen** di K1 (cakupan), K3 (jumlah sebulan), dan K5 (pembagian minggu). Bagian lain ADR 0161 tetap berlaku: penguncian minggu, batas dua kali ubah, riwayat, dan bulan mendatang.
- **KPI #4 bergeser.** Total proyeksi bulanan naik dari Rp ~5 M (6 akun Juli) ke seluruh kas keluar, sehingga akurasinya bisa berubah tajam. HRD dan Finance perlu diberi tahu sebelum deploy, termasuk SPV Finance F4 yang memakai sumber yang sama.
- **Selama tahap 1, realisasi bersifat akrual.** Akurasi KPI bisa berbeda dari angka Excel Finance yang berbasis kas. Layar menandainya, dan total uang keluar riil ditampilkan sebagai pembanding.
- **Risiko data:**
  - nomor akun 5201, 5102, 53xx, dan 7300 belum diverifikasi ke bagan akun Accurate prod (fixture test memakai 5201 untuk arti lain);
  - jumlah akun komponen menambah panggilan `get-balance.do` per minggu, dan beban ke Accurate belum diukur.
- **Deploy:**
  - integration-service dan **employee-service** naik bersama, karena salinan angka 6 dihapus;
  - finance-service hanya ikut bila task membaca pajak atau perlengkapan lewat rute baru;
  - BE sebelum FE, karena kontrak laporan mingguan berubah;
  - ~~tidak ada env baru.~~ **Diamandemen 2026-10-18 (Azzerith):**
    - Realisasi Pajak (`pajak_setoran_accurate`) dan uang keluar riil (`kas_bank_arus_salinan`) dimiliki finance-service. integration-service membacanya lewat rute mesin baru `GET /internal/forecast-kas/{pajak,arus-keluar}` di finance, dengan gerbang `FINANCE_SERVICE_KEY`.
    - Akibatnya blok compose integration-service mendapat env baru `FINANCE_MODULE_URL` dan `FINANCE_SERVICE_KEY`. Tidak ada variabel `.env` baru, karena kuncinya sudah dipakai procurement dan payroll.
    - finance-service di-deploy lebih dulu, lalu integration-service dengan `--force-recreate`.
    - Integration tidak menarik buku besar pajak dari Accurate sendiri, karena itu akan menjadi salinan kedua `akunPajakSetoran`.
    - Populasi forecast: entitas PT Bharata saja. Ini asumsi yang menunggu konfirmasi Finance.
- **REF - Kepemilikan Data** perlu baris baru: proyeksi komponen dan anggaran aset (integration), serta salinan arus kas-bank (finance). Baris salinan arus kas-bank sudah dijanjikan ADR 0163 tetapi belum ditambahkan.

## Dokumen Terkait

- [[ADR - 0161 Proyeksi Forecast Kas Mingguan Diatur Porsinya per Minggu oleh Cost Control, Jumlah Sebulan Tetap RAPB]]
- [[ADR - 0163 Salinan Saldo dan Arus Kas-Bank per Rekening Dimiliki Finance Service, Ditarik lewat Integration Service]]
- [[ADR - 0178 Serapan Anggaran per Departemen Jurnal, Seluruh Perusahaan Dihapus, Pagu Gabungan per Departemen]]
- [[ADR - 0180 Akun Anggaran Seluruh Perusahaan Diatur Finance, Non Ops Dua Akun dengan Baseline Isian]]
- [[Finance - Serapan Anggaran dan Cost Control]]
- [[Finance - Rancangan Finance Service]]
- [[HRIS - Matriks KPI per Departemen]]
- [[REF - Kepemilikan Data]]

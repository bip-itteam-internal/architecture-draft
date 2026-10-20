# ADR - 0191 KPI Penurunan Biaya Cost Control Mencakup OPEX dan Non Ops, Baseline Accurate Tahun Lalu

> **Status**: 🟢 Diterima, 2026-10-20, oleh Azzerith. Bentuknya dipilih lewat pilihan ganda di sesi `/analisa-kebutuhan` atas permintaan pemilik KPI Cost Control (2026-10-20). Kode belum ada; issue bip-erp#3336 (integration) lalu #3337 (employee). Mengamandemen [[ADR - 0180 Akun Anggaran Seluruh Perusahaan Diatur Finance, Non Ops Dua Akun dengan Baseline Isian]] butir 5 dan 6, **hanya** untuk KPI Cost Control #2.

## Untuk Manajemen

**Apa yang berubah di layar.**
- KPI Cost Control baris 2 tidak lagi mengukur dua akun Non Ops saja. Baris ini kini mengukur **seluruh biaya operasional (OPEX) ditambah biaya non-operasional**. Kumpulan akunnya sama persis dengan sheet Finance "Realisasi Opex & Non Ops".
- Pembandingnya adalah **realisasi bulan yang sama tahun lalu**, dibaca otomatis dari Accurate. Finance tidak perlu mengisi baseline apa pun untuk KPI ini.
- Angkanya: (biaya bulan ini − biaya bulan yang sama tahun lalu) ÷ biaya tahun lalu. **Minus berarti turun.** Target "≤ −2%".
- Label baris 2 diganti menjadi "Penurunan biaya operasional & non-operasional minimal 2% YoY". Cacah rekomendasi efisiensi tetap metrik tersendiri, bila HRD ingin memasangnya.

**Siapa yang terdampak.** Pemegang KPI Cost Control (skor baris 2) dan HRD (mengganti sumber baris 2 di template).
- Laporan Non Ops dan baseline isiannya tetap ada untuk Finance.
- KPI Finance Supervisor F3 (rasio beban non-ops) tidak berubah.

**Apa yang TIDAK dijanjikan.**
- Skor bulan yang sudah dibekukan tidak dihitung ulang.
- Skor baru berlaku setelah HRD mengganti sumber baris 2 di template.
- Angkanya ikut memuat **penyusutan dan beban pajak**, karena keduanya termasuk daftar OPEX Finance. Jadi tidak semuanya berada dalam kendali Cost Control.
- Kalau Accurate belum punya data bulan yang sama tahun lalu, skor bulan itu berbunyi "data tahun lalu belum ada", bukan 0%.
- Tidak ada angka "×1,25" di KPI ini.

**Perkiraan besaran kerja.** Dua PR, backend lebih dulu:
1. Cuplikan biaya bulanan dan endpoint KPI di integration-service.
2. Sumber KPI baru di employee-service.

Tidak ada layar baru. HRD cukup memilih sumber baru lewat Kelola template.

## Deskripsi

*KPI Cost Control #2 mengukur perubahan YoY total biaya OPEX + Non Ops: populasi yang sudah ditanam di kode (`DaftarKomponenOpex` ∪ `DaftarAkunAdminNonOps`), dengan bulan yang sama tahun lalu sebagai pembanding. Kedua sisi dibaca dari Accurate lewat satu mekanisme yang sama, lalu disimpan sebagai cuplikan bulanan di integration-service. Sumber `admin_non_ops` tidak disentuh.*

- **Status**: 🟢 Diterima 2026-10-20 (Azzerith), kode belum ada
- **Path di repo** (rencana):
  - `bip-erp/services/integration/internal/usecase/biaya_yoy.go` (baru): populasi, ringkasan, rumus
  - `bip-erp/services/integration/internal/domain/entity/biaya_yoy.go` (baru)
  - `bip-erp/services/integration/internal/worker/tasks/biaya_yoy_refresh.go` (baru)
  - `bip-erp/services/integration/internal/interface/http/biaya_yoy_handler.go` (baru)
  - `bip-erp/services/integration/internal/infrastructure/repository/` (repo cuplikan, baru)
  - `bip-erp/services/integration/main.go` (rute)
  - `bip-erp/services/employee/kpi_sumber_biaya_yoy.go` (baru)
- **Tanggal**: 2026-10-20

## Context

**Permintaan pemilik KPI Cost Control (2026-10-20, diteruskan user):** baris 2 "Analisis biaya berulang dan rekomendasi perbaikan" harus mengukur penurunan biaya operasional **dan** non-operasional secara keseluruhan, minimal 2% YoY, bukan hanya biaya admin/non-ops. Ini muncul saat menyelidiki kenapa KPI Cost Control Oktober 2026 tidak terhitung. Baris 2 gagal dengan galat "baseline belum diisi Finance untuk 2 akun".

**Keadaan template prod** (`GET /kpi/templates`, 89 template, diukur 2026-10-20, baca saja):

| Template | Baris | Sumber/metrik | Target | Arah |
|---|---|---|---|---|
| Cost Control (`6a0d3a3aaf417b963150bde7`) | #1 | `forecast_kas/akurasi_forecast_kas` | 5 | naik |
| Cost Control | #2 | `admin_non_ops/penurunan_yoy_persen` | 2 | naik |
| Cost Control | #3 | `varians_anggaran/varians_absolut_persen` | 95 | turun |
| Finance Supervisor (`6a0d32a0af417b963150bde3`) | #2 | `varians_anggaran/varians_absolut_persen` | 5 | turun |
| Finance Supervisor | #3 | `admin_non_ops/rasio_beban_non_ops_persen` | 2 | turun |
| Finance Supervisor | #4 | `forecast_kas/akurasi_forecast_kas` | 95 | naik |

- `penurunan_yoy_persen` **hanya** dipakai Cost Control #2.
- Sumber baris #1 dan #3 Cost Control tertukar. Target dan arahnya cocok dengan baris tetangganya. Ini dibetulkan HR lewat UI dan bukan bagian ADR ini.

**Keadaan kode** (`bip-erp` origin/main 2026-10-20, diverifikasi):
- **Populasi OPEX** = `DaftarKomponenOpex` (`services/integration/internal/usecase/opex_daftar.go`), berisi 58 akun ditambah `DaftarBebanPajak`.
  - Sumbernya sheet Finance `1 & 2 Realisasi Opex & Non Ops`, dan totalnya terverifikasi sama dengan TOTAL OPEX sheet itu.
  - Penjualan, HPP, dan blok e-commerce sengaja dikeluarkan.
  - `SaringKatalogOpex` meresolusi nama ke kode akun dan melaporkan `TakAda` dan `Ambigu`, tidak dibuang diam-diam.
- **Populasi Non Ops** = `DaftarAkunAdminNonOps` (`usecase/admin_nonops_daftar.go:37-40`): Beban Iuran & Sumbangan dan Beban Entertainment Adum.
  - Test `TestAkunAdminNonOpsTidakAdaDiDaftarOpex` menjaga agar kedua daftar tidak beririsan. Gabungan keduanya karena itu tidak menghitung satu akun dua kali.
- **Pola YoY Non Ops yang sudah ada:**
  - `PeriodeBaseline` = bulan yang sama tahun lalu (`admin_nonops_daftar.go:70-72`);
  - worker `accurate-realisasi-nonops-refresh` menarik bulan berjalan, bulan lalu, dan baseline keduanya (`worker/tasks/realisasi_nonops_refresh.go:96-108`);
  - ringkasan yang tak terdefinisi bila satu sisi kurang (`entity/admin_nonops.go:128-157`);
  - sumber KPI yang menggalatkan, bukan menolkan, keadaan tak terdefinisi (`services/employee/kpi_sumber_admin_nonops.go:97-116`).
- **`realisasi_opex` tidak bisa dipakai untuk sisi tahun lalu.** Worker-nya hanya menarik bulan berjalan dan bulan lalu, tanpa backfill (`worker/tasks/realisasi_opex_refresh.go:127-132`). Populasinya juga lebih luas dari OPEX, karena memuat akun beranggaran, akun Seluruh perusahaan, dan anggota pagu (`:252-300`).
- **Accurate bisa dibaca untuk periode mana pun:**
  - `GetProfitLossAccounts` (`infrastructure/clients/accurate_client_report.go:145`, `glaccount/get-pl-account-amount.do`) memberi saldo seluruh akun laba-rugi dalam satu panggilan per periode;
  - `KatalogAkunBeban` (`usecase/anggaran_katalog.go:14-35`) menyaring akun beban non-induk.
- **YoY atas OPEX belum ada di mana pun.** Satu-satunya YoY lain adalah biaya variabel produksi (isian manual, `services/finance/biaya_variabel.go:192`).
- **`kinerja_cost_control/rekomendasi_efisiensi`** hanya menghitung cacah dokumen rekomendasi (`services/employee/kpi_sumber_cost_control.go:26,49`; `services/finance/rekomendasi.go:211`), bukan besaran biaya.
- **Aturan bisnis.** Peraturan Perusahaan (`BUSINESS_LOGIC_IMPLEMENTATION.md`) tidak mengatur anggaran maupun KPI biaya (sama dengan ADR 0184).

**Pilihan bentuk (Azzerith, 2026-10-20):**
- cakupan OPEX 58 + Non Ops 2;
- baseline otomatis dari Accurate, bulan yang sama tahun lalu;
- basis bulanan;
- label diganti, dan yang diukur hanya penurunan.

**Asumsi dan risiko yang belum diukur:**
- **R1. Terjawab 2026-10-20: data Accurate 2025 ada.** Diukur lewat `GET /accounting/account-balance` prod (baca saja, rinciannya di bip-erp#3336):
  - total populasi Sep 2025 Rp 3.831,8 jt (46 akun bersaldo), Okt 2025 Rp 4.413,0 jt (47 akun), Sep 2026 Rp 3.184,1 jt (51 akun). YoY September 2026 = −16,9%;
  - 59 dari 60 nama ketemu di katalog. `Beban PPN KMS Gedung` tak ketemu, dan tidak ada nama yang ambigu;
  - kode akun 2025 sama dengan kode 2026 untuk semua akun yang ketemu;
  - Non Ops: Entertainment Adum = 6226, Iuran & Sumbangan = 6225.
- **R2.** Akun yang ada di 2025 tetapi tidak ada lagi di katalog sekarang (ditutup atau diganti kode) tidak tercakup di sisi tahun lalu. Akibatnya baseline mengecil tanpa tanda, kecuali dilaporkan.
- **R3.** Mesin skor diasumsikan menerima target negatif dengan arah turun, sebagaimana sudah diputuskan ADR 0180 butir 6. Belum diverifikasi di `kpi_reduksi`.
- **R4.** Entitas: populasi Accurate PT Bharata saja (database Accurate yang sama dengan `realisasi_opex`).

## Decision

1. **Populasi = `DaftarKomponenOpex` ∪ `DaftarAkunAdminNonOps`.**
   - Dirakit dari kedua daftar yang sudah ada, bukan daftar ketiga. Akibatnya, mengubah daftar OPEX atau Non Ops otomatis mengubah populasi KPI ini.
   - Nama diresolusi ke **kode akun** lewat katalog akun beban saat ini, dengan normalisasi yang sama dengan `SaringKatalogOpex`.
   - `TakAda` dan `Ambigu` dilaporkan di respons, bukan dibuang.
2. **Kedua sisi dibaca lewat satu mekanisme, dicocokkan per kode akun.**
   - Realisasi bulan penilaian dan realisasi bulan yang sama tahun lalu (`PeriodeBaseline`) dibaca dengan panggilan Accurate yang **sama**, yaitu saldo akun laba-rugi per periode. Pilihan antara `get-pl-account-amount.do` dan `get-balance.do` per akun diputuskan di task BE, setelah angka September 2026 dicocokkan ke `realisasi_opex`.
   - Pencocokan memakai kode, bukan nama. Akibatnya, akun yang namanya berubah antartahun tetap terpasangkan.
   - Akun bersaldo di satu sisi saja tetap dihitung apa adanya, lalu dicacah dan dilaporkan (`akun_satu_sisi`).
3. **Cuplikan bulanan di integration-service** (koleksi baru, satu dokumen per tahun × bulan, berisi total dan rincian per akun).
   - Penyegar harian menarik empat periode: bulan berjalan, bulan lalu, dan pembanding tahun lalu keduanya. Polanya sama dengan `realisasi_nonops_refresh`.
   - Bila penarikan gagal, angka lama tidak ditimpa, dan keadaan "belum ditarik" dibedakan dari nol.
   - Penyegaran manual untuk periode tertentu boleh ada, supaya bulan lampau bisa diisi tanpa menunggu.
4. **Rumus bertanda = (Realisasi − Baseline) ÷ Baseline × 100.** Negatif berarti turun, konvensi yang sama dengan ADR 0180 butir 6.
   - Bila salah satu total belum tersedia, atau baseline = 0, hasilnya **tak terdefinisi**. Sumber KPI menggalatkannya dengan sebab yang dibedakan; hasilnya bukan 0.
   - Tidak ada pengali ×1,25.
5. **Endpoint** `GET /accounting/biaya-yoy/kpi?tahun=&bulan=&key=` (nama final di task BE) membalas:
   - total realisasi, total baseline, persen bertanda, dan penanda terdefinisi;
   - cacah akun populasi, `tak_ada`, `ambigu`, dan `akun_satu_sisi`.
   - Gerbangnya kunci layanan integration, sama dengan `admin-nonops/kpi`. Rute baca untuk layar **tidak** dibuat (`Copilot: tidak, karena tidak ada layar`).
6. **Sumber KPI baru `biaya_yoy`** di employee-service.
   - Metriknya `perubahan_yoy_persen`, arah turun, target bawaan −2, cakupan perusahaan.
   - `Rincian` memuat baris total realisasi dan total baseline sebagai komponen, satu baris hasil berawalan `= `, dan baris `(tak ikut dihitung)` untuk `tak_ada` dan `ambigu`.
   - Penyebut cakupan dibaca dari respons, tidak disalin sebagai konstanta.
7. **`admin_non_ops` tidak diubah.**
   - Laporan Non Ops, baseline isian, `rasio_beban_non_ops_persen` (Finance Supervisor F3), dan `penurunan_yoy_persen` tetap seperti ADR 0180.
   - Setelah HRD mengganti Cost Control #2, `penurunan_yoy_persen` tidak lagi dipakai template mana pun. Metrik itu dibiarkan supaya skor beku tetap terbaca.
   - Metrik bertanda `perubahan_yoy_persen` milik `admin_non_ops` yang direncanakan ADR 0180 butir 6 **tidak lagi dibutuhkan untuk Cost Control #2**.
8. **Label template** baris 2 diganti HRD menjadi "Penurunan biaya operasional & non-operasional minimal 2% YoY". Penggantian dilakukan lewat layar Kelola template, tanpa kode.

## Consequences

- **ADR 0180 diamandemen untuk Cost Control #2 saja.**
  - Butir 5: baseline isian tidak lagi menjadi dasar KPI baris 2.
  - Butir 6: KPI-nya pindah ke sumber `biaya_yoy`.
  - Butir lain, serta laporan Non Ops, tetap berlaku.
- ⚠️ **Beban Iklan (6107) sekitar 67% dari total populasi** (Rp 2.539,9 jt dari 3.831,8 jt pada Sep 2025; Rp 2.133,7 jt dari 3.184,1 jt pada Sep 2026). Skor baris ini praktis digerakkan oleh belanja iklan, dan −16,9% September 2026 sebagian besar berasal dari iklan yang turun. Ini konsekuensi pilihan cakupan. Mengecualikan iklan butuh keputusan baru; prasedennya `varians_absolut_persen_tanpa_iklan` di sumber varians.
- **Angka KPI berubah skala.** Basisnya naik dari dua akun (puluhan juta) ke seluruh OPEX (miliaran per bulan). Satu beban besar yang musiman, misalnya bonus atau penyusutan aset baru, bisa membalik skor bulan itu. Pemilik KPI dan HRD perlu tahu ini sebelum template diganti.
- **Metrik #3 (varians OPEX ≤ ±5%) dan #2 kini memuat populasi OPEX yang sama.** Ini disengaja, karena pertanyaannya berbeda: #3 membandingkan dengan anggaran, #2 membandingkan dengan tahun lalu. Kedua skor jangan dibaca sebagai bukti independen.
- **Penyusutan dan beban pajak ikut**, mengikuti daftar OPEX. Jika kelak Finance memutuskan mengecualikannya, yang diubah adalah populasi KPI ini (dengan ADR baru), bukan `DaftarKomponenOpex`, karena daftar itu juga dipakai varians.
- **Beban ke Accurate** bertambah empat panggilan per hari bila memakai `get-pl-account-amount.do`, atau sekitar 4 × 60 bila memakai `get-balance.do` per akun. Ini ikut menentukan pilihan di butir 2.
- **Deploy:**
  - integration-service naik lebih dulu (koleksi baru, worker, rute), lalu employee-service (sumber baru);
  - tidak ada env baru, karena `INTEGRATION_MODULE_URL` dan `INTEGRATION_SERVICE_KEY` sudah terpasang di employee-service;
  - setelah itu HRD mengganti sumber dan label baris 2, dengan target −2 arah turun.
- **REF - Kepemilikan Data** mendapat baris cuplikan biaya YoY: salinan turunan Accurate, satu arah.
- **Dok yang usang dan ikut dibetulkan:**
  - [[HRIS - Matriks KPI per Departemen]] baris Cost Control #2, yang masih menulis "Accurate live proxy";
  - [[Finance - Serapan Anggaran dan Cost Control]].

## Dokumen Terkait

- [[ADR - 0180 Akun Anggaran Seluruh Perusahaan Diatur Finance, Non Ops Dua Akun dengan Baseline Isian]]
- [[ADR - 0184 Forecast Kas Mingguan Mencakup Tujuh Komponen Uang Keluar, Dibagi Empat Minggu, Realisasi Bertahap]]
- [[ADR - 0178 Serapan Anggaran per Departemen Jurnal, Seluruh Perusahaan Dihapus, Pagu Gabungan per Departemen]]
- [[Finance - Serapan Anggaran dan Cost Control]]
- [[HRIS - Matriks KPI per Departemen]]
- [[HRIS - Otomasi Skor KPI]]
- [[REF - Kepemilikan Data]]

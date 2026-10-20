# ANALISA - KPI Penurunan Biaya OPEX dan Non Ops YoY

> **Status**: [[ADR - 0191 KPI Penurunan Biaya Cost Control Mencakup OPEX dan Non Ops, Baseline Accurate Tahun Lalu]] 🟢 Diterima 2026-10-20 (Azzerith). Issue dibuat di Backlog Project #15; belum `Siap Agent` karena data prod issue 1 belum ditempel.

Blueprint ini hasil `/analisa-kebutuhan` 2026-10-20, atas permintaan pemilik KPI Cost Control: *"baris 2 harus mengukur penurunan biaya operasional dan non-operasional secara keseluruhan minimal 2% YoY, bukan hanya biaya admin/non-ops"*. Berkas ini papan kerja dan berubah setiap issue selesai. Keputusannya ada di ADR.

- **Keputusan**: [[ADR - 0191 KPI Penurunan Biaya Cost Control Mencakup OPEX dan Non Ops, Baseline Accurate Tahun Lalu]], yang mengamandemen [[ADR - 0180 Akun Anggaran Seluruh Perusahaan Diatur Finance, Non Ops Dua Akun dengan Baseline Isian]] butir 5–6 untuk Cost Control #2.
- **Dok domain**: [[Finance - Serapan Anggaran dan Cost Control]] §KPI Penurunan Biaya OPEX + Non Ops YoY · [[HRIS - Matriks KPI per Departemen]] §Cost Control · [[REF - Kepemilikan Data]]
- **Pemutus**: `Azzerith` (pilihan bentuk 2026-10-20)
- **Ukuran**: **Sedang**. Satu repo (`bip-erp`), dua PR berurutan.
  - integration-service: belum ada YoY atas OPEX, dan `realisasi_opex` tidak menyimpan bulan tahun lalu (`worker/tasks/realisasi_opex_refresh.go:127-132`).
  - employee-service: perlu sumber KPI baru.
  - `erp-frontend` **tidak** berubah: HRD memilih sumber lewat Kelola template, dan dropdown sumber dibaca dari katalog.
  - `my-bharata` tidak berubah.
- **Urutan**: issue 1 lalu issue 2. Deploy integration sebelum employee. Tidak ada env baru.

## Kebutuhan dan temuan

- **Kebutuhan sebenarnya**: skor baris 2 harus menjawab apakah total biaya yang dipantau Cost Control turun ≥ 2% dibanding bulan yang sama tahun lalu. Sumber saat ini (`admin_non_ops`) hanya memuat 2 akun dengan baseline isian. Isian Oktober 2026 kosong, sehingga skornya tidak terhitung.
- **Yang sudah ada**:
  - `DaftarKomponenOpex` dan `DaftarAkunAdminNonOps`, dijaga tidak beririsan;
  - `SaringKatalogOpex` (resolusi nama ke kode, dengan `TakAda` dan `Ambigu`);
  - `PeriodeBaseline`;
  - pola worker `realisasi_nonops_refresh`, yang sudah menarik baseline tahun lalu;
  - `GetProfitLossAccounts` (periode bebas);
  - pola sumber KPI yang menggalatkan keadaan tak terdefinisi.
- **Pemakai di prod (diukur 2026-10-20)**:
  - `admin_non_ops/penurunan_yoy_persen` hanya dipakai Cost Control #2;
  - `rasio_beban_non_ops_persen` dipakai Finance Supervisor #3, dan tidak disentuh.
- **Keputusan user 2026-10-20**: cakupan OPEX 58 + Non Ops 2; baseline Accurate bulan yang sama tahun lalu tanpa isian; basis bulanan; label diganti dan yang diukur hanya penurunan.
- **Asumsi eksplisit**: R1–R4 di ADR. Yang paling menentukan adalah R1, data Accurate 2025 lengkap, dan ini belum diukur.

## Langkah manusia

1. Setujui ADR 0191 (`🟢 Diterima, <tanggal>, oleh <login>`), lalu hapus baris "Menunggu ADR … Diterima" di atas.
2. Jalankan pengukuran **Perlu ukur prod** di issue 1 (baca saja) dan tempel hasilnya.
3. Buat kedua issue di `bip-erp` dari draf di bawah, lalu masukkan ke Project #15 dengan Status Backlog.
4. Pasang label `Siap Agent` pada issue yang lolos Definition of Ready.
5. Sesudah issue 2 ter-deploy, HRD mengganti template Cost Control baris 2:
   - sumber `biaya_yoy`, metrik `perubahan_yoy_persen`, target −2, arah turun;
   - label "Penurunan biaya operasional & non-operasional minimal 2% YoY".

   (Baris #1 dan #3 yang tertukar dibetulkan terpisah.)

## Issue 1: `bip-erp`: Cuplikan biaya OPEX + Non Ops YoY dan endpoint KPI di integration-service

- **Urutan**: bagian 1/2 · **Issue**: [bip-erp#3336](https://github.com/bip-itteam-internal/bip-erp/issues/3336)

**Pemutus:** @Azzerith
**PIC:** @

### Masalah

KPI Cost Control #2 harus mengukur perubahan YoY total biaya OPEX + Non Ops. Integration-service belum punya angka ini. `realisasi_opex` hanya menyimpan bulan berjalan dan bulan lalu, tanpa backfill (`services/integration/internal/worker/tasks/realisasi_opex_refresh.go:127-132`). Jalur Non Ops (`realisasi_admin_nonops`) hanya memuat dua akun.

### Keputusan

ADR "ADR - 0191 KPI Penurunan Biaya Cost Control Mencakup OPEX dan Non Ops, Baseline Accurate Tahun Lalu" (vault `architecture-draft/Decisions/`), butir 1–5. Issue ini layak `Siap Agent` sesudah ADR berstatus Diterima. Statusnya sekarang 🟡 Diusulkan.

Bentuknya:
- populasi `DaftarKomponenOpex` ∪ `DaftarAkunAdminNonOps`, diresolusi ke kode akun;
- kedua periode dibaca lewat satu mekanisme Accurate dan dicocokkan per kode;
- cuplikan bulanan disegarkan harian untuk 4 periode;
- endpoint KPI berkunci layanan;
- rumus bertanda (R − B) ÷ B × 100, tak terdefinisi bila salah satu sisi kurang atau B = 0.

### Yang harus benar

- [ ] Populasi dirakit dari kedua daftar yang ada, bukan daftar baru. Test membuktikan bahwa menambah nama ke `DaftarKomponenOpex` ikut menambah populasi.
- [ ] Pencocokan antartahun memakai kode akun. Test: akun yang sama dengan nama berbeda di dua periode tetap terpasangkan.
- [ ] `tak_ada`, `ambigu`, dan `akun_satu_sisi` ada di respons, dan tidak dibuang diam-diam.
- [ ] Total September 2026 untuk akun OPEX cocok dengan Σ `realisasi_opex` departemen `""` untuk akun yang sama. Bila berbeda, selisih dan sebabnya ditulis di PR. Langkah ini menentukan pilihan `get-pl-account-amount.do` atau `get-balance.do` (ADR butir 2).
- [ ] Persen tak terdefinisi dibedakan menurut sebab (belum ditarik, data tahun lalu kosong, baseline 0), dan tidak pernah dikirim sebagai 0.
- [ ] Gagal tarik tidak menimpa cuplikan lama. "Belum ditarik" dibedakan dari total 0.
- [ ] Tersedia penyegaran manual per periode, untuk mengisi bulan lampau.
- [ ] Test kontrak mengurai rekaman respons Accurate sungguhan (`get-pl-account-amount.do` atau `get-balance.do`), bukan struct tiruan.

### Di luar cakupan

- Sumber KPI di employee-service (issue 2).
- Perubahan `admin_non_ops`, laporan Non Ops, atau `realisasi_opex`.
- Layar apa pun (`Copilot: tidak, karena tidak ada layar`).
- Mengecualikan penyusutan dan pajak (butuh ADR baru).

### Data / bukti pendukung

- Template prod 2026-10-20: Cost Control #2 = `admin_non_ops/penurunan_yoy_persen`, target 2, arah naik (lihat Context ADR 0191).
- **Perlu ukur prod (baca saja, belum dijalankan):**
  - total Σ akun populasi untuk Oktober 2025 dan September 2025 lewat `GET /accounting/akun-saldo` atau laporan laba-rugi Accurate, untuk membuktikan data 2025 ada (R1);
  - jumlah akun populasi yang ter-resolve di katalog Accurate prod saat ini (`TakAda`/`Ambigu` dari `/accounting/anggaran/opex` atau sejenisnya).

### Prasyarat

- ADR 0191 Diterima.

## Issue 2: `bip-erp`: Sumber KPI `biaya_yoy` di employee-service

- **Urutan**: bagian 2/2, sesudah issue 1 merged · **Issue**: [bip-erp#3337](https://github.com/bip-itteam-internal/bip-erp/issues/3337)

**Pemutus:** @Azzerith
**PIC:** @

### Masalah

Template Cost Control #2 perlu sumber KPI yang membaca perubahan YoY biaya OPEX + Non Ops dari integration-service (issue 1). Sumber `admin_non_ops` sengaja tidak diubah (ADR 0191 butir 7).

### Keputusan

ADR "ADR - 0191 KPI Penurunan Biaya Cost Control Mencakup OPEX dan Non Ops, Baseline Accurate Tahun Lalu", butir 6–7. Bentuknya:
- sumber `biaya_yoy` di grup finance;
- metrik `perubahan_yoy_persen`, arah turun, target bawaan −2, cakupan perusahaan;
- `Rincian` tiga jenis: baris komponen, baris hasil `= `, dan baris `(tak ikut dihitung)`;
- penyebut cakupan dibaca dari respons.

### Yang harus benar

- [ ] Sumber terdaftar lewat `DaftarkanSumberBermetrik` dan muncul di katalog `GET /kpi/sumber-katalog` grup finance.
- [ ] Keadaan tak terdefinisi dari integration menjadi galat bersebab, bukan skor 0. Pola ini sama dengan `kpi_sumber_admin_nonops.go:97-116`.
- [ ] Skor dengan target −2 dan arah turun dihitung benar oleh mesin reduksi (R3 di ADR). Diuji untuk tiga keadaan: −3% (tercapai), −1% (belum), +2% (naik).
- [ ] Tidak ada konstanta jumlah akun di employee-service. Cakupan dibaca dari respons.
- [ ] `admin_non_ops` tidak berubah. Test-nya tetap hijau tanpa disunting.
- [ ] Satu test `app.Test` atau sejenisnya melewati jalur HTTP ke integration tiruan yang membalas bentuk respons sungguhan dari issue 1.

### Di luar cakupan

- Mengganti template prod (dilakukan HRD lewat UI).
- Menghitung ulang skor yang sudah dibekukan.

### Prasyarat

- Issue 1 merged.
- Urutan deploy: integration-service naik lebih dulu, lalu employee-service. Tidak ada env baru, karena `INTEGRATION_MODULE_URL` dan `INTEGRATION_SERVICE_KEY` sudah ada.

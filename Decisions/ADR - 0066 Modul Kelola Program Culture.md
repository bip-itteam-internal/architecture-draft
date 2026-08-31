## Deskripsi

*Mengganti pendekatan "form realisasi diisi officer" ([[ADR - 0065 Template Form Generik untuk Realisasi Program (Culture)]]) dengan **modul Kelola Program Culture** khusus di [[Microservices - Form Builder Service]]. KPI jabatan **Culture & Industrial** kini dihitung dari **skor komposit** tiap program (blueprint 30/30/40) yang komponennya berasal dari **penilaian PESERTA**, bukan self-report officer. Empat keputusan dicatat: (1) modul sendiri (`culture_programs` + `culture_feedback`) alih-alih form-builder; (2) implementasi/efektivitas **dihitung otomatis**, tak diisi manual; (3) `jenis` program me-resolve **target diundang otomatis** dari daftar karyawan aktif; (4) distribusi pilar dipecah ke **Core Value atomik**.*

- **Status**: ⚠️ **Diterima** oleh pemilik produk 2026-08-31 (menggantikan [[ADR - 0065 Template Form Generik untuk Realisasi Program (Culture)]]). Kode di branch **`feature/workspace-position`** (bip-erp + erp-frontend), **terverifikasi lokal/DEV lewat gateway, belum merge ke `main`, belum di prod**. Bukan status "live".
- **Path di repo**: `bip-erp/services/form-builder/models_culture.go` · `culture_programs.go` · `culture_feedback.go` · `culture_metrics.go` · `bip-erp/services/employee/kpi_sumber_culture.go` · `erp-frontend/src/app/(main)/hris/program-culture/*` · `src/features/form-builder/{types,hooks}/*culture*`
- **Tanggal**: 2026-08-31

## Context

ADR 0065 menurunkan metrik `culture` dari **satu form-builder** yang diisi officer Culture & Industrial sendiri tiap bulan (template `program-culture-rencana-realisasi`, field penggerak radio `terlaksana_sesuai_jadwal`). Saat dibangun, muncul pertanyaan pemilik produk yang berulang: *"apa yang sebenarnya diukur, kalau isian formnya teks semua dan officer menilai dirinya sendiri?"*

Dua cacat mendasar tersingkap:

1. **Self-report.** Officer mengisi sendiri apakah programnya "terlaksana sesuai jadwal". KPI yang dinilai dari laporan diri orang yang dinilai tak mengukur dampak apa pun.
2. **Beban pengisi.** Form panjang berisi teks (rancangan, before/after, root-cause/CAPA) berat diisi dan tak menghasilkan angka yang bisa dipercaya.

Yang seharusnya diukur: apakah program culture **benar-benar menjangkau dan memuaskan** orang yang ditujunya. Data itu ada di **peserta**, bukan di officer.

## Decision

### 1. Modul Kelola Program Culture, bukan form-builder

Dua koleksi baru di form-builder, bukan menumpang `Form`/`form_responses`:

- **`culture_programs`** — officer mencatat program: `nama`, `pilar`, `jenis`, `target`, `tanggal`, `jam_mulai`/`jam_selesai`. `created_by` = officer pemilik (kunci atribusi KPI).
- **`culture_feedback`** — PESERTA menilai: `rating` 1–5 + `masukan` opsional. Diakses lewat **link per-program** (`?program=<id>`) — peserta tak memilih program, tak login form panjang, tak mengetik selain masukan opsional. Index unik `(program_id, respondent_id)`: satu penilaian per peserta.

Rute `/culture/*` digerbang `requireEmployee` (officer & peserta sama-sama karyawan biasa). Tiga sumber angka dipisah menurut **siapa yang tahu**: target dari officer, partisipasi & antusiasme dari peserta, implementasi dari sistem.

### 2. Skor komposit 30/30/40 — implementasi DIHITUNG, bukan diisi

`hitungSkorProgram` (SATU tempat, `culture_metrics.go`) per program:

- **Partisipasi (30%)** = responden ÷ target × 100.
- **Antusiasme (30%)** = rata-rata rating ÷ 5 × 100.
- **Implementasi (40%)** = **Partisipasi × Antusiasme ÷ 100** — efektivitas = jangkauan × kualitas.

Implementasi semula dirancang diisi atasan; pemilik produk menegaskan **"itu otomatis perhitungan sistem"**. Menghitungnya menghapus satu langkah manual yang bisa lupa dan satu lagi jalan self-grade. KPI officer = **rata-rata** skor seluruh programnya pada periode. Bobot hidup HANYA di backend (satu fakta satu tempat) — tak disalin ke FE maupun sumber KPI.

### 3. `jenis` program → target diundang OTOMATIS

Target (penyebut partisipasi) tak diketik; di-resolve dari `jenis` saat simpan (di-snapshot supaya tak bergeser), memakai daftar karyawan aktif dari [[Microservices - Employee Service]] (`GET /list?type=employee` via `EMPLOYEE_MODULE_URL`):

- `internal` — seluruh karyawan aktif.
- `department` — jumlah staf `target_departemen`.
- `employees` — jumlah `target_karyawan` (dedup).

`EMPLOYEE_MODULE_URL` dibaca `os.Getenv` langsung, DI LUAR map `InternalURL` (pola file-service: `ValidateInternalURL` panic pada entri kosong). Jenis **`club`** (butuh modul Kelola Club) dan **`public`** (survei tanpa login, field nama+asal) **ditunda ke fase berikut**; publik direncanakan dengan **proteksi token per-program**.

### 4. Distribusi pilar dipecah ke Core Value atomik

`pecahPilar` memecah pilar campur: program "Happiness & Grow" dihitung Happiness +1 DAN Grow +1. Distribusi per pilar hanya mengenal **Happiness, Kaizen, Grow** (urut tetap) — officer tetap boleh memilih pilar campur, tapi grafik tak pernah menampilkan kategori campur.

## Consequences

**Yang membaik.** KPI culture kini mengukur **dampak ke peserta** (jangkauan × kepuasan), bukan laporan diri officer. Pengisian peserta ringan (rating + masukan opsional lewat link). Target tak bisa dikarang — di-resolve dari data karyawan nyata. Verifikasi end-to-end di DEV: `internal`→185, `department` (Beauty Hacks)→47, `employees` [dedup]→3; feedback 2 peserta → `hadir:2`; rantai skor → `auto_score` di employee-service.

**Yang memburuk / diterima sadar.**
- **Ketergantungan employee-service** untuk resolve target: bila `EMPLOYEE_MODULE_URL` kosong, pembuatan program gagal dengan pesan jelas (bukan diam-diam). Dependensi opsional sengaja di luar map `InternalURL`.
- **`club`/`public` belum ada** — hanya tiga jenis fase 1. Publik menunggu keputusan proteksi token.
- **Peserta menilai lewat link tak terautentikasi-ke-program** (masih `requireEmployee`): satu peserta satu program ditegakkan index unik, tapi identitas peserta = `respondent_id` dari header, bukan bukti kehadiran fisik. Diterima: KPI mengukur kepuasan yang **melapor**, bukan absensi.

**Yang tetap.** Batas [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] tak berubah: yang **menulis** `kpi_score` tetap employee-service; form-builder **melapor** lewat `GET /internal/culture/metrics` (`{data{<emp>:{komposit[],jumlah}}}`), menggerbang dirinya sendiri ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Wiring sumber + target oleh HR lewat "Atur Target" ([[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]]): formula `rata_rata`, target 100, arah naik pada template aktif `HR Organizational Development`. Koleksi generik `form_templates` dari ADR 0065 tetap ada sebagai kapabilitas tanpa konsumen.

## Dokumen Terkait

- [[Microservices - Form Builder Service]] — rumah kode modul culture + endpoint metrik
- [[API - Form Builder Service]] — kontrak rute `/culture/*` dan `/internal/culture/metrics`
- [[HRIS - Otomasi Skor KPI]] — kerangka otomasi tempat sumber `program_culture` terdaftar
- [[HRIS - Matriks KPI per Departemen]] — metrik `Culture 2`
- [[REF - Penamaan Metrik & Sumber KPI]] — penamaan sumber `program_culture` + key label FE
- [[Microservices - Employee Service]] — pemilik katalog sumber KPI (`kpi_sumber_culture.go`)
- [[ADR - 0065 Template Form Generik untuk Realisasi Program (Culture)]] — keputusan yang digantikan ADR ini
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]

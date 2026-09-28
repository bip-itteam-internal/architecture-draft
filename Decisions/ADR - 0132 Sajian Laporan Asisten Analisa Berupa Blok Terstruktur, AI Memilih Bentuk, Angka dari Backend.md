---
tags: [adr, marketing-analytics, ai, frontend]
status: Accepted
tanggal: 2026-09-28
---

# ADR - 0132 Sajian Laporan Asisten Analisa Berupa Blok Terstruktur, AI Memilih Bentuk, Angka dari Backend

> Status: **Accepted** (2026-09-28, keputusan pemilik produk). Melengkapi [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]] §5 dan [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]] §4; tidak menggantikan keduanya.

## Context

Laporan Asisten Analisa hari ini menyajikan keputusan AI sebagai kalimat, sementara angka dan diagram di tab Hasil analisa disusun tetap oleh FE. Pemilik produk meminta laporan yang **memutuskan bentuk penyajian yang paling cocok**: angka tunggal cukup teks, daftar atau perbandingan jadi tabel, tren atau perbandingan antar kategori jadi chart (bar/line), dengan output berupa **data terstruktur** yang FE render sesuai jenisnya, dan chart WAJIB memakai komponen yang sudah ada di erp-frontend (ChartContainer + Recharts beserta aturan bakunya), bukan sistem chart baru.

Tiga bagian contoh tampilan yang disetujui pemilik produk belum bisa ditampilkan karena datanya tidak dikirim backend: tindak lanjut kiriman sebelumnya per tim (hanya ada di pesan bayangan), revenue dan belanja iklan per toko (hasil_analisa hanya menyimpan total), dan pembanding periode sebelumnya.

Batas yang tetap berlaku: model **tidak menerima dan tidak menulis angka mentah** (ADR 0120 §4, ADR 0127 §5), rules menentukan kelayakan (ADR 0127 §4), dan angka yang dibekukan saat kiriman tidak berubah arti belakangan.

## Decision

### §1 Satu kiriman membawa `sajian`: daftar blok + katalog dataset

Tiap dokumen `keputusan_kiriman` membawa `sajian`, dibekukan saat kiriman dibuat (angka tidak dihitung ulang saat dibaca):

- **`dataset`**: peta `id → dataset` yang **dihitung backend**. Tiap dataset memuat judul (bahasa bisnis), satuan (`rupiah` | `rasio` | `persen` | `jumlah` | `skor`), `bentuk_diizinkan` (subset `angka` | `tabel` | `bar` | `line`), definisi kolom/seri berlabel, baris data, dan ambang bila ada (mis. target ROAS dari `mart_ambang`).
- **`blok`**: daftar berurutan `{jenis, judul, kalimat?, dataset_id?}` dengan `jenis` ∈ `teks` | `angka` | `tabel` | `bar` | `line`. Blok `teks` hanya membawa kalimat; blok lain WAJIB merujuk `dataset_id` yang ada dan `jenis`-nya harus termasuk `bentuk_diizinkan` dataset itu.
- **`sumber_susunan`**: `aturan` | `model`.

Katalog awal: angka utama laporan, laba harian, ROAS per pekan dengan garis target, revenue dan belanja iklan per toko, pembanding periode sebelumnya, keputusan per jenis tindakan, status keputusan, tindak lanjut kiriman sebelumnya per tim. Katalog boleh tumbuh: satu dataset = satu penghitung backend + uji.

### §2 AI memilih bentuk dan urutan; tidak pernah menulis angka

Model menerima **daftar dataset beserta metadatanya** (id, judul, satuan, bentuk_diizinkan, ringkasan hasil hitung yang sudah boleh ia terima menurut ADR 0127 §5), lalu mengembalikan urutan blok, jenis tiap blok, dan kalimat penjelas. Model **tidak** mengembalikan angka, baris, atau seri. Validator menolak blok yang merujuk dataset tak dikenal, jenis di luar `bentuk_diizinkan`, atau kalimat yang memuat angka yang tidak ada di ringkasan hasil hitung. Model gagal, habis waktu, atau seluruh bloknya ditolak → **susunan bawaan dari aturan** (`sumber_susunan: aturan`) yang selalu tersedia, sehingga laporan tidak pernah kosong.

Aturan pemilihan bentuk yang dipakai susunan bawaan dan dijadikan instruksi model: satu nilai → `angka`; daftar atau perbandingan beberapa atribut → `tabel`; tren waktu → `line`; perbandingan antar kategori → `bar`.

### §3 FE hanya perender, memakai komponen yang sudah ada

- `teks`/`angka`: komponen teks dan kartu angka yang ada; `tabel`: tabel yang ada; `bar`/`line`: `ChartContainer` (`components/ui/chart.tsx`) + Recharts dengan aturan baku tim (team-memory § Bagan/chart): warna `theme:{light,dark}` dari `--fb-seri-*`/`WARNA_BAGAN` (bukan `--chart-1..5`, bukan hex), `domain={[0,100]}` untuk satuan `skor`, `connectNulls={false}`, `type="monotone"`, deret kosong disembunyikan diganti satu kalimat, legend berlabel, garis ambang hanya bila dataset membawa ambang.
- Format angka di render dengan `intlLocale(lang)` sesuai `satuan`; label dari backend apa adanya.
- Dokumen PDF A4 memakai perender blok yang sama.
- Blok yang tak dapat dirender (jenis/dataset tak dikenal oleh FE lama) dilewati diam dan dicatat, bukan menjatuhkan halaman.

### §4 Satu fakta satu tempat

Rumus tiap dataset hidup di backend; FE tidak menghitung ulang total, rasio, atau status. Status keputusan tetap `statusKeputusanTerakhir` (TOLAK MENANG), label tindakan tetap `labelTindakan`.

## Consequences

- Kontrak `GET /keputusan-kiriman` bertambah field `sajian` (aditif). **BE sebelum FE**; FE tanpa `sajian` jatuh ke tampilan yang ada hari ini.
- Dokumen `keputusan_kiriman` membesar (dataset beku). Dataset dibatasi jumlah baris (mis. per toko teratas N) dan dicatat di dok service.
- Kiriman yang dibuat sebelum ADR ini tidak punya `sajian`; layar menampilkan tampilan lama untuknya.
- Pemanggilan model per kiriman tetap satu (ADR 0127 §5): pemilihan blok digabung ke panggilan keputusan yang sama, bukan panggilan kedua.

## Terkait

- [[ADR - 0127 Laporan Asisten Analisa Membawa Keputusan AI, Orang Menjalankan atau Menolak]]
- [[ADR - 0120 Asisten Analisa Marketing Jadi Menu ERP, Template dan Jadwal Lebih Dulu Tanpa AI]]
- [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
- [[Microservices - Marketing Analytics Service]]

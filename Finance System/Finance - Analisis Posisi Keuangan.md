**Status**: 🟢 **Implementasi (FE)** — menu `/finance/analisis-posisi` di `erp-frontend`; dashboard Neraca komparatif dari data Accurate nyata. Rasio ditunda (butuh pemetaan pos).

## Deskripsi

Dashboard "Analisis Posisi Keuangan" — meniru pola *Financial Position Analysis*: stat total, tabel **Neraca komparatif antar‑periode + panah tren**, dan **komposisi per‑sisi** (Aset vs Pendanaan). Tujuannya: baca posisi keuangan sekilas.

Kode: `erp-frontend/src/features/finance/analisis-posisi/`, rute `app/(main)/finance/analisis-posisi/page.tsx`. Guard reuse izin `finance.accounting.view` (tanpa RBAC baru); entri menu di `components/layout/sidebar-menus.tsx`.

## Sumber data (grounded)

- Hook `useFetchNeraca(asOfDate)` → `GET /api/integration/accounting/balance-sheet` — **Neraca Accurate apa adanya** (`BarisLaporan[]`: `HEADER`/`TOTAL`/`LIST`, `level`, `seq`, `is_top_total`, `balance`). Dipanggil **dua kali**: per tanggal pilihan (default akhir bulan lalu) & tanggal sama **−1 tahun**.
- bip-erp & FE **pass‑through Accurate** — lihat [[Finance - Big Pictures]] & [[External - Accurate]]. **Tidak ada master/enum klasifikasi** Aset Lancar/Tidak Lancar, Liabilitas Lancar, atau Persediaan di kode mana pun.

## Prinsip yang dijaga

- **Angka selalu nyata.** `balance`/data `null` → "—"/keadaan kosong, bukan 0.
- **Tanpa klasifikasi tebakan.** Komposisi memakai **struktur & label asli Accurate** (subtotal `level 2` per sisi; pisah sisi di `is_top_total` pertama — asumsi "Aset lebih dulu"). Bila struktur tak terbaca → `terbaca:false`, komposisi kosong jujur (angka tak pernah tampil dengan pengelompokan salah).
- **Panah tren netral** (↑/↓/→ warna muted) — "naik" pada neraca tak selalu berarti baik (mis. liabilitas naik), jadi warna tak menghakimi.
- Donut pakai **Recharts** (konvensi chart finance non‑FAT), warna token tema.

## Ditunda (jujur di UI)

- **Rasio Lancar/Cepat/Kas + radar** dan **donut Lancar‑vs‑Tidak‑Lancar sebagai rasio** — panel "menunggu pemetaan pos". Perlu master/pemetaan pos (aset lancar, liabilitas lancar, persediaan) yang belum ada; menghitungnya sekarang = menebak = dilarang.

## Fase berikutnya

Pemetaan pos neraca (pilih dari baris Accurate asli) → aktifkan rasio dari angka nyata. Catatan verifikasi: proporsi komposisi sebaiknya dicek sekali terhadap payload Neraca Accurate nyata (struktur `level`/`is_top_total` per COA perusahaan).

## Dokumen Terkait

- [[Finance - Big Pictures]] — peta domain Finance System
- [[Finance - Dashboard per Posisi (FAT)]] — dashboard per posisi (kartu + grafik)
- [[External - Accurate]] — sumber angka neraca (pass‑through)

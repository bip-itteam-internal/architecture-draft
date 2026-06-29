---
publish: false
---

# Meeting Arahan Platform & Infra

- **Tanggal**: 2026-06-29
- **Jenis**: Meeting internal — arahan manajemen ke tim IT
- **Peserta**: Pak Widi (stakeholder), Tim IT

---

## Keputusan & Arahan

### 1. Data Platform — Semua Matriks Harus Tampil

Semua sumber data platform harus terintegrasi dan ditampilkan dalam satu dashboard:

- **Ads data** — data iklan (marketplace ads, social ads)
- **Transaction data** — data transaksi penjualan semua channel
- **Video content data** — data performa konten video (TikTok, dll)

> **Requirement**: ketiga matriks ini **harus muncul semua** dalam satu view. Tidak boleh ada yang hilang atau tidak tersinkron.

**Status**: 🟡 Direncanakan — belum diimplementasikan

---

### 2. Data Profit — Detail Per Dimensi

Laporan profit harus breakdown sampai level detail:

- **Per produk (SKU)** — profit tiap SKU
- **Per piece** — profit per satuan unit
- **Per toko** — profit per toko/channel
- **Detail lainnya** — dimensi tambahan sesuai kebutuhan bisnis (TBD bersama finance/bisnis)

**Status**: 🟡 Direncanakan — belum diimplementasikan

---

### 3. Infra — Backup Internet Khusus Server

- Server wajib punya **koneksi internet backup** (failover) — tidak boleh bergantung satu ISP/jalur saja
- Jika koneksi utama down, server otomatis switch ke jalur backup
- Motivasi: webhook Shopee & TikTok butuh koneksi selalu-on untuk jaga success rate >90%

**Status**: 🟡 Direncanakan — belum diimplementasikan

---

### 4. Infra — Data Utama Server Backup ke Lokal

- Data utama di server (production) harus di-backup secara berkala ke storage lokal (on-premise)
- Tujuan: resiliensi bila server cloud down atau data corruption

**Status**: 🟡 Direncanakan — belum ada mekanisme backup lokal terdokumentasi

---

### 5. Progress Update Harian ke Pak Widi

- Tim IT wajib kirim **laporan progres harian** ke Pak Widi
- Format dan channel update: TBD (konfirmasi ke Pak Widi)

---

### 6. Server Uptime — Zero Downtime Wajib

- **Server tidak boleh down** dalam kondisi apapun
- **Deployment pun tidak boleh menyebabkan downtime** — wajib rolling deploy / blue-green / zero-downtime strategy
- Ini berlaku untuk semua service production

**Status**: ⚠️ Perlu diverifikasi — strategy zero-downtime deployment belum terdokumentasi eksplisit

---

### 7. Migrasi Data Marketplace — URGENT

- Migrasi data MP (marketplace) ditandai **URGENT** oleh manajemen
- Harus diprioritaskan di atas pekerjaan lain yang tidak blocking

**Status**: 🟡 In-progress — lihat [[Integration Cloud Migration]]

---

## Tindak Lanjut

- [ ] Desain & implementasi dashboard data platform (ads + transaction + video content terintegrasi)
- [ ] Desain laporan profit multi-dimensi (per SKU, per piece, per toko)
- [ ] Riset & setup backup internet untuk server (failover ISP / bonding)
- [ ] Setup mekanisme backup data server ke lokal (cron/script + storage)
- [ ] Tentukan format & channel daily progress report ke Pak Widi
- [ ] Audit & dokumentasi strategy zero-downtime deployment semua service
- [ ] **[URGENT]** Eksekusi migrasi data marketplace — lihat [[Integration Cloud Migration]]

---

## Dokumen Terkait

- [[Integration Cloud Migration]]
- [[IT - Background Jobs & Schedulers]]
- [[Microservices - Integration Service]]

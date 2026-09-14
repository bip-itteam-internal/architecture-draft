## Deskripsi

*Pengajuan Pembelian tipe **KONSUMSI** mengikuti ambang persetujuan Direktur yang berbagi dengan tipe lain (nominal ≥ ambang → Direktur disisipkan), persis seperti DANA. Ini **membalik** keputusan bisnis 2026-09-09 yang membuat KONSUMSI kebal Direktur dan berhenti di SPV Finance berapa pun nominalnya. KONSUMSI tetap tipe terpisah untuk pelaporan, bukan cabang jenjang.*

- **Status**: ✅ **Implemented** — kode di `main` bip-erp (`services/procurement/pengajuan_barang_jenjang.go`, `tipeKebalDirektur`) dan cermin `erp-frontend` (`TIPE_KEBAL_DIREKTUR`). Ambang berbagi `ambangDirekturBawaan` = Rp 5.000.000 tidak diubah.
- **Path di repo**: `bip-erp/services/procurement/pengajuan_barang_jenjang.go` · `erp-frontend/src/features/pengajuan-barang/types/pengajuan-barang.ts`
- **Tanggal**: 2026-09-14

## Context

Modul Pengajuan Pembelian ([[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]], modul aktif kini `pengajuan_barang`) menyisipkan tahap Direktur pada rantai persetujuan bila nominal mencapai ambang. Ambang itu satu nilai **berbagi** untuk semua tipe (`ambangDirekturBawaan` = Rp 5 juta); ADR-0055 sadar tidak membedakannya per tipe.

Tipe **KONSUMSI** (permintaan uang untuk jamuan, pantry, konsumsi rapat/acara) mengalir lewat cabang uang seperti DANA — tak menyentuh gudang, tak lewat Procurement, nominalnya diketik pengaju. Pada 2026-09-09 diputuskan KONSUMSI **kebal Direktur**: berhenti di SPV Finance berapa pun nominalnya, dengan alasan "belanja konsumsi diputus di tingkat Finance". Keputusan itu hidup **hanya sebagai komentar kode** di `tipeKebalDirektur` — tidak pernah naik ke vault.

Pemilik proses (2026-09-14) meminta KONSUMSI bernilai besar tetap disetujui Direktur: belanja konsumsi ≥ Rp 5 juta cukup material untuk menuntut persetujuan setingkat Direktur, sama seperti penggantian dana (DANA). Aturan yang diminta:

- `mengajukan → SPV departemen pengaju → SPV Finance → finance`
- bila nominal ≥ Rp 5 juta: `mengajukan → SPV departemen pengaju → SPV Finance → Direktur → finance`

Ambang Rp 5 juta yang diminta sudah sama persis dengan ambang berbagi yang berlaku, sehingga tidak diperlukan ambang khusus per tipe.

## Decision

### 1. KONSUMSI dikeluarkan dari daftar kebal Direktur

`tipeKebalDirektur` kini hanya memuat `IKLAN`. Dengan itu KONSUMSI melewati cabang Direktur yang sama seperti DANA: `ambangDirektur > 0 && nominal >= ambangDirektur` menyisipkan `pb_direktur`. Jenjang KONSUMSI menjadi **identik DANA**:

```
< ambang:  pb_spv_divisi → pb_spv_finance → pb_finance_setujui_bayar → pb_ap_transfer
≥ ambang:  pb_spv_divisi → pb_spv_finance → pb_direktur → pb_finance_setujui_bayar → pb_ap_transfer
```

(Pembuka `pb_spv_divisi` dilewati bila pengajunya SPV, sama seperti tipe uang lain.)

### 2. Ambang tetap berbagi, tidak dibuat per tipe

KONSUMSI memakai `ambangDirekturBawaan` yang sama (Rp 5 juta). Tidak dibuat ambang khusus KONSUMSI: itu akan menyimpang lebih jauh dari ADR-0055 §7 (menolak parameter per-tipe) tanpa kebutuhan nyata, dan angka yang diminta memang sudah sama dengan ambang berbagi. Bila kelak ambang berbagi diubah, KONSUMSI ikut — itu perilaku yang diinginkan.

### 3. Tidak ada tahap, izin, atau kategori inbox baru

`pb_direktur` sudah dipakai DANA/UMUM/RAWMATERIAL: mesin tahap berbasis posisi (`TahapBerikutnyaBarang`), gerbang per-tahap, resolver penyetuju ([[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]]), dan notifikasi tahap Direktur seluruhnya sudah ada dan teruji. KONSUMSI memakainya ulang apa adanya. Perubahan perilaku murni di pembangun jenjang.

### 4. KONSUMSI tetap tipe terpisah

Peleburan KONSUMSI ke DANA ditolak: KONSUMSI tetap dipilih pengaju dan dilaporkan sebagai kategori tersendiri. Yang identik kini rantai persetujuannya, bukan identitasnya.

## Consequences

### Yang membaik

- Belanja konsumsi bernilai besar tidak lagi lolos dari mata Direktur; gerbang uang KONSUMSI setara DANA.
- Aturan kebal Direktur kini punya **satu** anggota beralasan jelas (IKLAN), bukan dua yang salah satunya menyimpang dari cabang uang lainnya.
- Keputusan yang tadinya hidup hanya sebagai komentar kode kini tercatat di vault.

### Yang memburuk atau tetap terbuka

- Dokumen KONSUMSI ≥ ambang yang **sudah** diajukan sebelum deploy tetap memakai `jenjang_wajib` beku lamanya (tanpa Direktur) — jenjang dibekukan saat submit. Hanya pengajuan baru terdampak. Diterima sadar.
- Beban persetujuan Direktur bertambah untuk konsumsi besar; itu justru maksud keputusan ini.

### Yang sengaja tidak dilakukan

- Tidak membuat ambang per-tipe (§2).
- Tidak melebur KONSUMSI ke DANA (§4).

## Dokumen Terkait

- [[ADR - 0055 Pengajuan Pembelian Empat Tipe Menggantikan Pengajuan Budget]] — modul dan mesin jenjang yang keputusan ini sentuh
- [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]] — penyetuju tahap Direktur yang dipakai ulang
- [[REF - Alur Persetujuan]] — siapa yang berwenang memutuskan
- [[Microservices - Procurement Service]]

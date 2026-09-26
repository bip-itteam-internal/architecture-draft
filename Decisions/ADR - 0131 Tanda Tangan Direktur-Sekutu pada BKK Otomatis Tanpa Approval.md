# ADR - 0131 Tanda Tangan Direktur/Sekutu pada BKK Otomatis Tanpa Approval

## Untuk Manajemen

- **Yang berubah di layar**: BKK (Bukti Kas Keluar) dan form request yang dibayar atas
  nama CV/PT tertentu kini menampilkan kop dan gambar tanda tangan direktur/sekutu badan
  usaha itu secara otomatis, begitu AP menyelesaikan pengisian BKK — tanpa direktur/
  sekutu itu login atau menekan apa pun di sistem ini.
- **Siapa terdampak**: AP (melihat kop/ttd berubah sesuai CV/PT dokumen), Accounting
  (menerima dokumen yang sama), direktur/sekutu 40 CV dan PT non-Bharata (namanya
  tercetak, tanpa aksi dari mereka).
- **Tidak dijanjikan**: bukti bahwa direktur/sekutu itu benar-benar menyetujui transaksi
  spesifik sebelum dokumennya tercetak — ini konsekuensi yang diterima sadar, bukan
  kelalaian.
- **Besaran kerja**: kecil-sedang setelah master data (ADR 0096 amandemen) berdiri.

## Deskripsi

*BKK dan form request untuk pengajuan yang dibayar atas nama CV/PT tertentu mencetak
gambar tanda tangan direktur/sekutu badan usaha itu secara OTOMATIS begitu kode badan
usaha dokumen final, TANPA tahap approval baru. Ini SECARA SADAR menyimpang dari
[[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]],
yang melarang gambar tanda tangan/stempel tercetak sebelum approval sungguhan terjadi.*

- **Status**: 🟡 Diusulkan, disetujui user 2026-09-26 lewat brainstorming.
- **Path di repo**: `bip-erp/services/finance/akuntansi_cv_signatory*.go` (baru),
  `bip-erp/services/finance/akuntansi_cv_entitas.go` (rujukan `KodeSignatory`),
  `erp-frontend/src/features/manufacture/components/KopSurat.tsx` (prop `signatory`),
  `erp-frontend/src/features/pengajuan-barang/components/tab-bkk-pengajuan.tsx`
- **Tanggal**: 2026-09-26

## Context

ADR 0089 §3 (Decision) dan `contract_pkwt_pdf.go:23-24` menetapkan: dokumen PDF buatan
sistem tidak boleh mencetak gambar tanda tangan/stempel sebelum orangnya benar-benar
menyetujui — supaya dokumen tidak *tampak* sudah disetujui sebelum aksi approval
sungguhan terjadi. Alasan itu berlaku untuk PKWT (kontrak kerja yang mengikat karyawan
secara hukum).

BKK dan form request adalah domain berbeda: dokumen kas keluar **internal**, bukan
kontrak yang mengikat pihak eksternal. Kop dan nama direktur/sekutu yang tercetak di
BKK berfungsi sebagai **identifikasi badan usaha pembayar** (mana CV/PT yang uangnya
keluar), bukan sebagai persetujuan direktur atas transaksi itu — persetujuan
sesungguhnya sudah terjadi lebih dulu di jenjang Cost Control/SPV Finance/Direktur
sebelum tahap AP (lihat [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]]
§Jalur A, dan jenjang pengajuan yang sudah berjalan).

Menambahkan tahap approval direktur/sekutu CV untuk SETIAP BKK akan menghambat alur
transfer AP yang sudah dirancang cepat (Cost Control sudah di awal jenjang), dan
direktur/sekutu 40 CV + PT non-Bharata bukan pengguna sistem ERP ini sehari-hari —
memaksa mereka login untuk tiap BKK tidak proporsional dengan risikonya (dokumen kas
internal, bukan kontrak eksternal).

## Decision

### 1. Gambar tanda tangan, bukan stempel teks

Berbeda dari pola `ParafStempel` (nama·posisi·timestamp, dipakai Batch Record) — user
eksplisit meminta gambar tanda tangan asli yang diunggah, disimpan di
`EntitasSignatory.TtdURL`.

### 2. Otomatis, tanpa tahap approval baru

Tanda tangan tercetak begitu `KodeCV`/kode badan usaha dokumen final diketahui (saat AP
mengisi BKK, tahap `pb_ap_transfer`). Tidak ada endpoint/tahap baru di mana direktur/
sekutu login atau mengklik setuju.

### 3. Risiko diterima sadar

Dokumen BKK bisa menampilkan gambar tanda tangan direktur/sekutu yang tidak pernah
membuka atau melihat transaksi spesifik itu di ERP ini. Ini berbeda dari kekhawatiran
ADR 0089 (kontrak yang mengikat hukum pihak eksternal) — BKK adalah dokumen internal,
dan otorisasi pengeluaran uang yang sesungguhnya sudah terjadi di jenjang persetujuan
sebelum tahap AP.

## Consequences

- ➕ AP dan Accounting mendapat dokumen yang konsisten (kop+ttd sesuai badan usaha) tanpa
  menambah langkah approval yang memperlambat alur.
- ➖ Tidak ada bukti sistem bahwa direktur/sekutu spesifik menyetujui transaksi spesifik
  itu — bila kelak dibutuhkan (mis. sengketa), ERP ini tidak menyediakannya.
- ⚠️ Bila kelak persyaratan hukum/audit berubah menuntut approval eksplisit direktur/
  sekutu per BKK, ADR ini perlu direvisi bersama alur jenjangnya.

## Dokumen Terkait

- [[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]] (domain berbeda, dibandingkan bukan digantikan)
- [[ADR - 0096 Buku Besar 40 CV Dibangun di ERP dengan FINCON sebagai Spesifikasi]] (amandemen berdampingan)

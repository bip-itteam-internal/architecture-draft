## Deskripsi

*Menetapkan bagaimana koreksi faktur yang finance nyatakan lewat file Excel "Rekap Lengkap" diterjemahkan oleh sistem: setiap sel yang berubah dipetakan ke **tuas yang sudah ada** (keluarkan order, pindah hari, vonis fake order, Mapping SKU, riwayat Harga Jual), dan **tidak** ada penyimpanan koreksi per baris faktur. Keputusan ini lahir karena baris faktur auto-sync dihitung ulang dari order + master setiap kirim ulang, sehingga koreksi yang tak dituangkan ke master-data atau flag order pasti tertimpa sweep berikutnya.*

- **Status**: 🟡 **Diputuskan 2026-09-04, implementasi menunggu merge** — bip-erp PR [#1712](https://github.com/bip-itteam-internal/bip-erp/pull/1712) (endpoint + mesin) dan erp-frontend PR [#1453](https://github.com/bip-itteam-internal/erp-frontend/pull/1453) (modal). Uji prod pasca-deploy (file tanpa diedit ⇒ 0 koreksi) belum dijalankan.
- **Path di repo**: `bip-erp/services/integration/internal/usecase/accurate_koreksi_import*.go`, `accurate_prefix_rekap.go` · `erp-frontend/src/features/integration/accurate/auto-sync/components/koreksi-import-modal.tsx`
- **Tanggal**: 2026-09-04

## Context

Finance merekonsiliasi faktur Accurate lewat file **Download Rekap Lengkap** (satu baris per item order, enam kolom prefix Accurate: Accurate Number · Code · Name · Unit Price · Quantity (Daily Sales) · Amount). Temuan lalu diperbaiki satu per satu lewat dialog koreksi per order, halaman Mapping SKU, atau Harga Jual. Permintaannya: perbaiki langsung di Excel, unggah kembali, sistem yang membetulkan Accurate.

Tiga fakta kode yang mengikat rancangannya:

1. **Baris faktur tidak dipersist.** `buildDetailItemsFromOrders` merakit ulang baris dari order + `product_sku_mappings` + resolver harga (riwayat efektif → `items.base_price` → harga order) setiap kali faktur dikirim ulang, dan `accurate_daily_invoice.go` mencatat eksplisit *"untuk FAKTUR belum ada tuas koreksi resmi per-baris"* (rem `ADOPTED_MANUAL` hanya pengakuan, bukan dokumen koreksi). Koreksi yang disimpan di tempat lain akan kalah saat sweep malam atau Retry.
2. **Kolom prefix Rekap Lengkap bukan baris faktur.** Sampai PR #1712, `Unit Price` dibaca dari `items.base_price` **hari ini** lewat join `accurate_products`, tanpa riwayat harga per hari kirim dan tanpa ekspansi mapping SKU — angka yang tak pernah dibukukan faktur mana pun. Laporan yang finance pakai untuk rekonsiliasi bisa menyembunyikan selisih, dan diff "file vs faktur" akan menampilkan baris yang tidak diedit sebagai koreksi.
3. **Aturan bisnis harga**: [[Finance - Incentive]] menyebut harga jual hanya diubah Marketing SPV dengan persetujuan Direktur; Upload Massal Harga Jual sudah bergerbang `IsProfitEditor`. Sementara Mapping SKU sudah punya preseden ditulis dari layar auto-sync ("Petakan produk" di tab Order FO).

Dua alternatif yang ditolak: **override per baris faktur** (koleksi baru yang dibaca `buildDetailItemsFromOrders`) — menciptakan invariant baru yang tak punya kasus nyata di riwayat prod (semua koreksi harga/kode sejak Juli ternyata salah master atau salah mapping); dan **tolak semua koreksi yang menyentuh master, arahkan ke halaman master** — mengembalikan finance ke alur satu-per-satu yang ingin dihilangkan.

## Decision

### 1. File Excel adalah cara menyatakan koreksi, bukan tempat koreksi disimpan

Tiap sel prefix yang berbeda dari **baris faktur sebenarnya** (`KoreksiBaseline`: order + faktur hari efektif + `PrefixFakturPerOrder`) diterjemahkan ke satu tuas:

| Sel berubah | Jenis | Tuas | Menyentuh master |
|---|---|---|---|
| Accurate Number kosong (seluruh baris order) | `KELUARKAN` | invoice-exclusion | tidak |
| Accurate Number = `FO` | `FAKE_ORDER` | fake-order override + kaskade (uang dulu) | tidak |
| Accurate Number = nomor faktur lain, toko + channel sama | `PINDAH_HARI` | invoice-date-override | tidak |
| Code berubah | `MAPPING_SKU` | `product_sku_mappings` (listing → master, qty_per_unit = qty faktur / qty order) | **ya** |
| Unit Price berubah | `HARGA` | riwayat harga efektif sejak hari faktur terawal + `ApplyPriceToInvoices` faktur di file | **ya** |
| Quantity berubah pada SKU ber-mapping | `QTY_PER_UNIT` | `qty_per_unit` mapping | **ya** |
| Name / Amount berubah | — | diabaikan (Accurate membaca kode; Amount turunan) | tidak |

Yang **ditolak** dengan alasan terang: paket multi-komponen (ubah lewat Mapping SKU), faktur `ADOPTED_MANUAL` / `EXTERNAL_EDIT` / `IMPORTED` / `VOIDED`, pengecilan nilai faktur `INVOICE_PAID`, order pra-cutover, kode yang tak ada di master, qty bukan kelipatan qty order, qty SKU master langsung (qty faktur = qty order — tak ada tuas), dan dua nilai berbeda untuk SKU yang sama dalam satu file.

### 2. Kelas master-data butuh persetujuan eksplisit, harga bergerbang role

Koreksi `MAPPING_SKU`/`QTY_PER_UNIT` dan `HARGA` berstatus **PERLU_PERSETUJUAN** di preview dan hanya dijalankan bila kelasnya dicentang saat commit (`apply_mapping`, `apply_price`). Kelas harga ditolak di klasifikasi bila aktor bukan profit editor (gerbang yang sama dengan Upload Massal Harga Jual). Harga untuk **kode baru** (Code + Unit Price berubah bersamaan) bergantung pada mappingnya: bila mapping tidak diterapkan, harganya dilewati — faktur tak memuat kode itu dan kirim ulang paksa hanya membuang kuota.

### 3. Baris yang hilang dari file tidak berarti apa-apa

Finance boleh mengunggah sebagian baris. Mengeluarkan order harus **eksplisit** (mengosongkan Accurate Number). Preview memperingatkan bila ≥ 20 order akan dikeluarkan, karena kolom kosong massal biasanya berasal dari unduhan yang lookup fakturnya gagal senyap, bukan niat finance.

### 4. Prefix Rekap Lengkap = baris faktur

`PrefixFakturPerOrder` mengisi enam kolom prefix dengan resolver yang sama dengan jalur kirim (kode master hasil mapping, harga riwayat efektif hari-faktur, qty terekspansi; paket multi-komponen digulung ke SKU listing), dan kolom Accurate Number mengikuti hari faktur **efektif** (`invoice_date_override` menang atas `shipped_at`). Ini prasyarat: tanpa itu "file tidak diedit" tidak menghasilkan "0 koreksi".

### 5. Satu kirim ulang per faktur, uang dulu

Commit menulis semua flag & master lebih dulu (mapping → riwayat harga → flag keluarkan / pindah hari / FO dengan tunda-rebuild), menjalankan kaskade FO sekali per dokumen (penerimaan → faktur → retur), lalu mengirim ulang tiap faktur tersentuh **sekali** (sadar harga untuk kelas harga, biasa untuk sisanya). Faktur hanya dianggap sudah dikirim ulang bila `RESENT`. Pagar: 60.000 baris dan 150 faktur per batch.

## Consequences

- **Positif**: koreksi tahan sweep (tersimpan sebagai master/flag yang dibaca jalur kirim), beraudit (tuas existing menulis jejaknya sendiri + jejak `KOREKSI_IMPORT` per order + arsip batch `invoice_correction_import_batches`), dan Rekap Lengkap menjadi cermin faktur yang jujur.
- **Semantik laporan berubah**: Amount di Rekap Lengkap untuk SKU ber-mapping/ber-riwayat harga kini = yang dibukukan; finance perlu diberi tahu sebelum deploy.
- **Harga jual bisa ditulis dari layar finance** — menyimpang dari [[Finance - Incentive]] (Marketing SPV + Direktur); mitigasinya gerbang profit editor, centang eksplisit, alasan batch wajib. Bila tim menganggap ini terlalu longgar, kelas harga bisa dinonaktifkan tanpa menyentuh kelas lain.
- **Tidak ada tuas per baris**: qty SKU master langsung dan hari tanpa faktur tetap lewat dialog koreksi per order; perbaikan `accurate_products.product_code` (Config Accurate) dan koreksi Penerimaan lewat file di luar cakupan.
- Harga hanya dikirim ulang ke faktur **di dalam file** — faktur lain yang memuat SKU sama tidak disentuh otomatis (sama dengan tuas Harga Jual → Dampak Harga); ini disengaja agar satu unggahan tidak memicu kirim ulang massal, tetapi berarti finance harus mengunggah rentang yang lengkap.
- Commit per koreksi tanpa transaksi (pola import FO): kegagalan di tengah tidak membatalkan yang sudah benar; nasib tiap baris/dokumen diarsipkan.

## Dokumen Terkait

- [[Microservices - Integration Service]] · [[API - Integration Service]] · [[APP - Web ERP]] · [[DB - Data Dictionary]]
- [[RUN - Import Koreksi Faktur dari Rekap Lengkap]] — prosedur langkah-per-langkah untuk finance.
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]] — faktur tak pernah dihapus; koreksi isi lewat edit-by-id.
- [[ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift]] — "cermin untuk melihat, Accurate untuk memutuskan".
- [[External - Accurate]] — batas edit faktur (terkunci retur, terbayar).
- [[Finance - Incentive]] — aturan perubahan harga jual.

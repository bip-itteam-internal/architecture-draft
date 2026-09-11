## Deskripsi

*Menetapkan bagaimana koreksi faktur yang finance nyatakan lewat file Excel "Rekap Lengkap" diterjemahkan oleh sistem: setiap sel yang berubah dipetakan ke **tuas yang sudah ada** (keluarkan order, pindah hari, vonis fake order, Mapping SKU, riwayat Harga Jual), dan **tidak** ada penyimpanan koreksi per baris faktur. Keputusan ini lahir karena baris faktur auto-sync dihitung ulang dari order + master setiap kirim ulang, sehingga koreksi yang tak dituangkan ke master-data atau flag order pasti tertimpa sweep berikutnya.*

- **Status**: ✅ **Implemented & terverifikasi di produksi** — bip-erp [#1712](https://github.com/bip-itteam-internal/bip-erp/pull/1712) + erp-frontend [#1453](https://github.com/bip-itteam-internal/erp-frontend/pull/1453) merged 2026-09-04, lingkup dipangkas lewat bip-erp [#1717](https://github.com/bip-itteam-internal/bip-erp/pull/1717) + erp-frontend [#1455](https://github.com/bip-itteam-internal/erp-frontend/pull/1455) (merged 2026-09-04 09:23 UTC), **deployed 2026-09-05**. Uji prod hari itu: Rekap Lengkap satu toko TikTok satu hari diunduh lalu diunggah balik **tanpa disunting** ⇒ 35 baris dibaca, **35 tidak berubah, 0 koreksi, 0 ditolak** — membuktikan prefix export = baris faktur. Jalur commit belum pernah dijalankan di prod. 🟡 **Amandemen §1c koreksi GUDANG**: branch `feat/koreksi-gudang-import` bip-erp + erp-frontend (2026-09-11), **belum merged/deployed**.
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
| Accurate Number = nomor faktur lain, toko + channel sama | `PINDAH_HARI` | invoice-date-override | tidak |
| Code berubah | `MAPPING_SKU` | `product_sku_mappings` (listing → master, qty_per_unit = qty faktur / qty order) | **ya** |
| Unit Price berubah | `HARGA` | riwayat harga efektif sejak hari faktur terawal + `ApplyPriceToInvoices` faktur di file | **ya** |
| Quantity berubah pada SKU ber-mapping | `QTY_PER_UNIT` | `qty_per_unit` mapping | **ya** |
| Gudang Accurate berubah (kolom paling kanan) — 🟡 §1c | `GUDANG` | `transaction_orders.warehouse_override` per pesanan + dokumen retur pesanan dipindah | **stok** |
| Name / Amount berubah | — | diabaikan (Accurate membaca kode; Amount turunan) | tidak |

Yang **ditolak** dengan alasan terang: paket multi-komponen (ubah lewat Mapping SKU), faktur `ADOPTED_MANUAL` / `EXTERNAL_EDIT` / `IMPORTED` / `VOIDED`, pengecilan nilai faktur `INVOICE_PAID`, order pra-cutover, kode yang tak ada di master, qty bukan kelipatan qty order, qty SKU master langsung (qty faktur = qty order — tak ada tuas), dan dua nilai berbeda untuk SKU yang sama dalam satu file.

### 1b. Mengeluarkan order & vonis fake order SENGAJA tidak lewat berkas ini (amandemen 2026-09-04)

Versi pertama memetakan **Accurate Number kosong** → keluarkan order dan **`FO`** → vonis fake order. Keduanya dicabut sebelum fitur dipakai finance, dengan dua alasan:

1. **Duplikat.** `POST /accurate/orders/fake-order-override/bulk` sudah ada sejak 2026-08-22 dan menerima export rekap mentah apa adanya — cukup unggah daftar nomor pesanan, tanpa mengetik apa pun ke sel. Mengeluarkan order punya tuas satuan di dialog koreksi per order.
2. **Sel kosong adalah keadaan paling mudah terjadi tanpa disengaja.** Kolom Accurate Number bisa kosong **sejak diunduh** bila lookup faktur harian gagal senyap di export (`transaction_export_multiple.go`, `invLookupOK`). Membacanya sebagai perintah membuat satu unduhan cacat sanggup mengeluarkan banyak penjualan sekaligus. Pagar berupa peringatan pada ≥20 order hanya menambal gejalanya, dan pagar itu ikut dibuang.

Sel kosong dan `FO` kini **DITOLAK sambil menunjuk tuas yang benar**, bukan diabaikan diam-diam. Tersisa tiga jenis koreksi: `PINDAH_HARI`, `MAPPING_SKU` (+`QTY_PER_UNIT`), `HARGA`.

### 1c. Koreksi GUDANG per pesanan (amandemen 2026-09-11, 🟡 belum merged)

Pemilik fitur: satu toko **bisa mengirim dari dua gudang dalam satu hari**, dan tak ada data marketplace yang menunjukkan gudang pengirim (probe prod 2026-09-05, lihat Consequences). Keputusannya:

1. **Penanda per pesanan, bukan override baris.** Kolom `Gudang Accurate` (ujung keempat format Rekap Lengkap; sengaja bukan `Warehouse Name` milik TikTok/Lazada) diterjemahkan ke `transaction_orders.warehouse_override`. Selaras dengan §1: file hanya menyatakan, penanda di order yang disimpan, dan perakit faktur & retur membacanya (`GudangEfektif`) sehingga kirim ulang tak mengembalikan gudang.
2. **Baris faktur dipecah per gudang.** Faktur harian menggabung semua pesanan toko-hari per (kode, harga) dan satu baris Accurate = satu gudang, jadi memindah satu pesanan = memecah baris. Pola `cmd/gudangfix` (ganti gudang seluruh baris) tak cukup untuk koreksi per pesanan.
3. **Sidik faktur hanya berubah untuk baris ber-penanda** (`GudangKoreksi`): gudang baris biasa tetap di luar `hashInvoiceLines`/`hashInvoiceQty` supaya ribuan faktur lama tak dikirim ulang. Baris pesanan yang **dikembalikan** ke gudang toko tetap bertanda (penanda ditulis eksplisit), kalau tidak pecahan lamanya di faktur terkunci tak pernah digabung balik.
4. **Faktur terkunci retur ikut** — prod 2026-09-11: 654 dari 1.410 faktur sejak 1 Agu (46%) terkunci. Faktur terkunci menolak hapus baris, jadi pemecahan = UPDATE qty baris lama (≥ qty yang sudah diretur) + SISIP baris gudang tujuan, lalu baca-ulang. Yang mentok dilaporkan, tidak didiamkan.
5. **Retur mengikuti faktur** (barang keluar & masuk di gudang yang sama). Dokumen retur yang sudah terbit dipindah dengan pola `cmd/gudangfix` (seluruh baris induk verbatim, verifikasi identik). Satu dokumen retur hanya satu gudang: kelompok pesanan yang berbagi retur harus berakhir di gudang yang sama, diproses **semua-atau-tidak**; memecah baris retur belum pernah diuji di Accurate dan karena itu ditolak.
6. **Kelas `Pindah gudang` wajib dicentang** (`apply_gudang`, vonis `PERLU_PERSETUJUAN`): Rekap Lengkap mengisi kolom gudang di SEMUA baris, sehingga file unduhan lama bisa diam-diam mengembalikan gudang yang sudah dikoreksi — dan koreksi ini memindah stok.
7. **Faktur Juli ditolak** di kode, dengan pilihan per unggahan *Koreksi gudang mulai tanggal* (`gudang_mulai`, bawaan & paling awal 2026-08-01, `usecase.GudangMulaiTerawal`). Faktur Juli sengaja dibiarkan di gudang lama (keputusan user 2026-09-02); mengirim ulang satu faktur Juli memindah seluruh barisnya.

### 2. Kelas master-data butuh persetujuan eksplisit, harga bergerbang role

Koreksi `MAPPING_SKU`/`QTY_PER_UNIT` dan `HARGA` berstatus **PERLU_PERSETUJUAN** di preview dan hanya dijalankan bila kelasnya dicentang saat commit (`apply_mapping`, `apply_price`). Kelas harga ditolak di klasifikasi bila aktor bukan profit editor (gerbang yang sama dengan Upload Massal Harga Jual). Harga untuk **kode baru** (Code + Unit Price berubah bersamaan) bergantung pada mappingnya: bila mapping tidak diterapkan, harganya dilewati — faktur tak memuat kode itu dan kirim ulang paksa hanya membuang kuota.

### 3. Baris yang hilang dari file tidak berarti apa-apa

Finance boleh mengunggah sebagian baris. (Versi pertama mengeluarkan order lewat Accurate Number kosong dengan peringatan ≥ 20 order; keduanya dicabut, lihat §1b.)

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
- **Koreksi GUDANG — dijawab §1c (🟡 belum merged).** Konteks awalnya (dinyatakan pemilik fitur 2026-09-04): Terukur di kode: gudang selalu dari `accurate_shops.warehouse_name` sehingga satu faktur hanya bisa punya satu gudang, padahal satu toko nyatanya memakai gudang berbeda; tak ada `warehouse_override` di mana pun; dan `hashInvoiceLines` (itemNo|unitPrice|qty) **tidak memuat gudang**, sehingga membetulkan config toko tak pernah memicu perbaikan faktur lama — sweep dan Retry sama-sama menyimpulkan "isi tak berubah". Akibatnya hari ini tak ada satu pun jalan di ERP untuk membetulkan gudang faktur yang sudah terbit.

  **Probe prod 2026-09-05 (read-only) menutup pertanyaan "dari mana sistem tahu gudang yang benar": TIDAK ADA SUMBER OTOMATIS.**
  - `accurate_shops`: **53 toko, hanya 2 gudang** — *Gudang Sadewa* (23 toko) dan *Gudang Sidareja* (30 toko).
  - TikTok `warehouse_id` **ADA dan terisi** di `tt_shop_order_details` (415.746 dok, 42 nilai unik), tapi pada 3.000 order terkirim terbaru lintas **33 toko**, **nol toko** memakai lebih dari satu `warehouse_id`. Artinya itu gudang **terdaftar di TikTok per toko**, bukan gudang fisik yang benar-benar mengirim.
  - `transaction_orders` **tidak punya field gudang sama pun** (nol field cocok `ware|gudang|scan|fulfil`).
  - Lazada punya `warehouse_code` di cache native; **Shopee tak punya sama sekali**.

  Konsekuensinya untuk rancangan: pemetaan "id gudang marketplace → nama gudang Accurate" **tidak berguna**, karena marketplace tak tahu gudang mana yang mengirim. Kebenarannya hanya dipegang manusia atau WMS, sehingga koreksi gudang harus berupa **penanda manual per pesanan** — dan karena gudangnya cuma dua, validasinya cukup terhadap `distinct(accurate_shops.warehouse_name)`. Dirancang di §1c.
- **Kolom Gudang Accurate = gudang menurut ERP**, bukan dibaca dari Accurate (satu panggilan per faktur akan menembus batas gateway 30 detik saat ekspor). Dokumen yang gudangnya diubah di luar ERP (faktur Juli) tampil berbeda dari Accurate.
- **Belum terbukti di prod** (§1c): gudang komponen ketika baris induk paket **disisipkan** ke gudang koreksi; dan penyapu malam belum memegang kunci faktur di cabang faktur terkunci (celah lama jalur append, kini juga jalur pindah gudang).
- **Tampilan belum ikut**: detail/ekspor faktur Auto-Sync belum menampilkan gudang per baris (baris pecahan tampil kembar kode+harga) dan Lacak Order belum menampilkan gudang koreksi — task lanjutan.

## Dokumen Terkait

- [[Microservices - Integration Service]] · [[API - Integration Service]] · [[APP - Web ERP]] · [[DB - Data Dictionary]]
- [[RUN - Import Koreksi Faktur dari Rekap Lengkap]] — prosedur langkah-per-langkah untuk finance.
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]] — faktur tak pernah dihapus; koreksi isi lewat edit-by-id.
- [[ADR - 0066 Salinan Dokumen Retur Accurate + Pemindai Drift]] — "cermin untuk melihat, Accurate untuk memutuskan".
- [[External - Accurate]] — batas edit faktur (terkunci retur, terbayar).
- [[Finance - Incentive]] — aturan perubahan harga jual.

**Status**: ✅ **Implemented & Deployed** — PR #1451 merged & live 26 Agustus 2026 (deploy 20:36 WIB). Diverifikasi ke dokumen Accurate nyata pada dua penerimaan yang finance laporkan selisih.

# ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order

Menentukan **bagaimana** `tt_statement_adjustments` dibukukan ke Accurate — koleksi yang sudah lama ditarik & disimpan tapi tak pernah dipakai satu pun jalur pembukuan.

## Deskripsi

*Penyesuaian statement TikTok (mayoritas: ganti rugi paket hilang) dibukukan dengan **menambah payout pesanan yang disebutnya**, lalu mesin receipt yang ada mengurus sisanya — bukan sebagai baris pendapatan lain-lain tersendiri.*

- **Status**: ✅ **Implemented & Deployed** (26 Agustus 2026)
- **Path di repo**: `bip-erp/services/integration/internal/infrastructure/repository/tiktok_statement_adjustment_repo.go` · `.../transaction_repo.go` (`ListOrdersByTiktokStatement`) · `internal/usecase/accurate_receipt_usecase.go` (`orderBatalDilewati`) · `internal/usecase/accurate_rts_usecase.go` (`diserapPenyesuaianStatement`) · `internal/domain/entity/transaction.go` (`PenyesuaianStatement`)
- **Tanggal**: 2026-08-26

## Context

### Uangnya nyata, tapi nol yang dibukukan

`tt_statement_adjustments` diisi rapi oleh jalur fetch statement, tapi interface repositorinya **hanya punya `Upsert`** — tak ada satu pun method baca. Akibatnya tak ada jalur pembukuan yang bisa memakainya sekalipun ingin. Pola "dibangun lalu tak dinyalakan", sekelas KPI Finance.

Terukur prod 26 Agustus 2026: **274 baris, Rp26.538.490**, seluruhnya POSITIF (uang masuk).

Gejalanya konsisten dan bisa dicocokkan satu-satu: pada **setiap** receipt yang statement-nya punya penyesuaian, `chequeAmount` lebih kecil dari `payable_amount` TikTok **persis sebesar** penyesuaiannya; receipt tanpa penyesuaian selisihnya nol.

| Receipt | cheque − payable | Σ penyesuaian |
|---|---|---|
| `INC/2026/08/17/015-BH` | −284.199 | 284.199 |
| `INC/2026/08/20/018-BH` | −99.000 | 99.000 |
| `INC/2026/08/18/015-BH` | −14.500 | 14.500 |

Selama ini selisih itu dikira "wajar karena order pra-cutover".

### `LOGISTICS_REIMBURSEMENT` bukan penggantian ongkir

97% penyesuaian bertipe `LOGISTICS_REIMBURSEMENT`, dan **namanya menyesatkan**. Diukur atas 263 baris, bukan diterjemahkan dari labelnya:

| Nilai penyesuaian sama dengan… | cocok |
|---|---|
| `total_refund` pesanan | **244** |
| `total_shipping_cost` pesanan | **0** |
| `subtotal_after_seller_discount` | 0 |

Status pesanan penerima: **CANCELLED 254**, RETURNED 2, tak ada di ERP 7. Dan **244 dari 263 tak punya `warehouse_items`** — barangnya tak pernah kembali ke gudang.

Artinya: **paket hilang di logistik TikTok** → pembeli di-refund penuh → TikTok mengganti **seluruh nilai pesanan** kepada kita. Bukan mengganti ongkir. Sisanya `PLATFORM_REIMBURSEMENT` (Rp785.922, belum diperiksa isinya).

Secara ekonomi barang keluar (stok berkurang — benar, barangnya memang hilang) dan uangnya tetap diterima penuh; yang berubah cuma **siapa yang membayar**: TikTok, bukan pembeli.

### Halangan struktural

Dua hal membuat penyesuaian tak bisa sekadar "dijumlahkan":

1. **Pesanannya sering tak ada di statement itu.** Kompensasi datang di statement yang lebih baru daripada penjualannya — 43 dari 274 begitu, ditambah 17 pesanan yang tak punya baris transaksi sama sekali.
2. **`allocateInvoices` membuang semua order CANCELLED** dengan alasan "payout order batal pasti 0". Asumsi itu batal begitu ada kompensasi — dan justru 254 dari 263 penerima kompensasi berstatus CANCELLED.

## Decision

### 1. Penyesuaian melipat ke payout pesanan, bukan jadi baris pendapatan tersendiri

`ListOrdersByTiktokStatement` menambahkan penyesuaian ke `income.TotalSettlementAmount`. Karena `payoutOf` membaca field itu, **seluruh rantai receipt ikut benar tanpa satu pun cabang baru di usecase**: cheque, alokasi ke faktur, dan penyerapan ke potongan penjualan.

Hasilnya mengikuti model Sistem B yang sudah berlaku: `paymentAmount` = base price faktur, `DetailDiscount` menyerap selisih (**boleh NEGATIF** bila kompensasi > harga faktur), net kas = payout.

Alternatif yang ditolak: membukukannya sebagai **Pendapatan Lain-lain** terpisah. Ditolak karena finance menghitungnya sebagai bagian dari pelunasan faktur — terbukti cocok pada `INV/2026/07/22/020-BH`: base 191.000 · potongan **−4.200** · settlement 195.200, tiga sel persis sama dengan hitungan manual finance.

### 2. Pesanan yang tak ada di statement ditarik terpisah, dengan income HANYA-penyesuaian

Untuk 60 kasus di atas, pesanannya diambil dari `transaction_orders` lalu diberi income yang isinya **hanya** penyesuaian — seluruh angka lain nol. Memakai income tersimpan (agregat seluruh statement) berarti membukukan ulang penjualan yang sudah dibukukan di statement lain: kekeliruan yang sama persis dengan bug porsi lintas-statement (PR #1439).

### 3. Gerbang order CANCELLED membaca PENANDA, bukan menebak dari angka

Ada penanda eksplisit `TransactionIncome.PenyesuaianStatement` (**tak dipersist**, `bson:"-"` — penyesuaian melekat pada satu statement, sedangkan income tersimpan adalah agregat seluruh statement).

Gerbangnya `o.Status == CANCELLED && !o.Income.AdaPenyesuaian()`.

Alternatif yang ditolak: `payoutOf(o.Income) != 0`. Ditolak karena akan ikut meloloskan **setiap** order batal ber-refund bukan-nol — ribuan order di luar lingkup perubahan ini, masing-masing dengan payment negatif ke faktur yang tak pernah dimaksudkan menerimanya.

### 4. Jenis penyesuaian TIDAK di-whitelist

Semua yang TikTok bayar ikut dibukukan, apa pun `type`-nya. Daftar-putih jenis adalah pola yang **sudah tiga kali membuang uang diam-diam** di layanan ini — terakhir pada penyesuaian dompet Shopee, di mana 7 dari 10 jenis tak dikenal switch-nya dan hilang tanpa jejak.

### 5. Penyesuaian pesanan pra-cutover DILEWATI

Tidak ada cabang baru untuk ini: order batal yang lolos gerbang §3 tetap menghadapi penjaga `shipped_at` / batas toko / cutover di bawahnya, persis seperti order lain. Era sebelum `autoSyncCutoverDateWIB` (`20260710`) memang ranah pembukuan manual finance ([[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] memakai prinsip yang sama untuk retur).

Konsekuensinya diterima: receipt-nya tetap kurang dari `payable_amount`, dan **itu selisih yang SAH**.

### 6. Yang tak bisa dibukukan wajib berjejak

Tiga kelas dicatat WARN beserta nilainya, tidak dibuang diam-diam: nominal tak terbaca, penyesuaian tanpa pesanan terkait, dan pesanan yang tak ada di ERP.

## Consequences

### Sebaran 274 penyesuaian setelah perubahan

| Baris | Nilai | Keadaan |
|---|---|---|
| **232** | **Rp22.881.051** | DIBUKUKAN |
| 32 | Rp2.759.939 | pra-cutover — ranah manual finance (§5) |
| 7 | Rp609.500 | pesanan tak ada di ERP (ber-jejak WARN) |
| 2 | Rp189.000 | faktur hari-kirim tak ada |
| 1 | Rp99.000 | faktur berstatus VOIDED |

Tiga baris terakhir (Rp288.000) belum punya pemilik proses — perlu diperiksa terpisah.

### Verifikasi sebelum deploy (nol tulis)

Binary di-cross-compile, di-scp ke VM, dijalankan read-only, lalu dihapus.

- Uji integrasi ke data prod: 64 statement berpenyesuaian masing-masing membawa totalnya utuh, **nol order ganda**; statement tanpa penyesuaian tak tersentuh.
- Dry-run `cmd/receipttest` atas **seluruh 64 receipt terdampak**, lama vs baru: **64 balance sebelum, 64 balance sesudah, nol gagal**; **25 statement kontrol** payload **byte-identik**.

### Verifikasi sesudah deploy (dokumen Accurate dibaca ulang)

Dua penerimaan yang finance laporkan selisih di-retry per-dokumen, lalu isinya dibaca ulang dari Accurate — bukan dipercaya dari status kirim:

| Receipt | cheque | Baris yang dibuktikan |
|---|---|---|
| `INC/2026/08/10/018-BH` | 13.646.903 → **13.731.402** | `INV/2026/07/28/023-BH` bayar 292.500 net **191.536** |
| `INC/2026/08/17/015-BH` | 6.919.303 → **7.114.503** | `INV/2026/07/22/020-BH` bayar 191.000 net **195.200** |

Keduanya sama persis dengan hitungan manual finance. Sisa selisih `015-BH` −88.999 adalah penyesuaian pra-cutover (§5) — bersih, tak ada sisa lain.

### Gerbang retur ikut berubah

Membayar fakturnya **membuka** lubang dobel yang sebelumnya tertutup hanya karena uangnya tak pernah dibukukan: begitu kompensasi masuk receipt, faktur pesanan itu lunas, dan Retur Penjualan di atasnya = pembalikan dobel. Perubahan gerbangnya ada di amandemen [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] 2026-08-26.

### Keterbatasan yang disadari

**19 dari 263 pesanan berkompensasi ternyata barangnya TETAP kembali ke gudang** (Rp1.983.747; 17 di antaranya menumpuk pada satu faktur `INV/2026/07/27/013-BH`). Untuk mereka, men-skip retur berarti stok tak bertambah padahal barangnya nyata ada. Gerbang tak bisa tahu — scan gudang terjadi jauh setelah keputusannya diambil. Karena itu keputusannya meninggalkan baris `SKIPPED` yang **terlihat** di UI retur, bukan diam.

**4 dokumen retur sudah SENT**, 2 di antaranya tanpa `warehouse_items` → stok Accurate bertambah untuk barang yang tak pernah kembali. Salah stok nyata, kecil, belum dikoreksi.

**208 dokumen retur menggantung `PENDING`** menunggu scan gudang atas barang yang takkan pernah datang — bagian dari temuan "retur tertahan gerbang gudang". Gerbang baru berlaku **maju**; baris yang sudah terlanjur ada tidak tersentuh.

### 🔑 Jebakan alat

`DryRunTiktok` / `cmd/receipttest` **tidak menerapkan** `applySampleShipping` maupun `mergeManualAdjustments`, sehingga cheque-nya bisa meleset dari jalur nyata (terukur Rp30.980 pada `015-BH`). **Jangan pakai angka dry-run sebagai ramalan cheque final** — ia hanya sah untuk membanding komposisi baris lama vs baru.

## Dokumen Terkait

- [[Microservices - Integration Service]] — Auto Sync Income (receipt) & Auto-Sync Retur
- [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] — gerbang retur yang ikut berubah karenanya
- [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] — prinsip cutover yang §5 ikuti
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]] — sisi faktur dari pembukuan yang sama
- [[ADR - 0001 Akuntansi via Accurate]] — alasan pembukuan tak dilakukan sendiri
- [[APP - Web ERP]] — halaman Auto Sync Income & Auto-Sync Retur tempat hasilnya terlihat

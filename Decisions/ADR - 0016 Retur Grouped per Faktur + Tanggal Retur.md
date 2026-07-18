✅ **Implemented** (kode + deploy 2026-07-17)

# ADR - 0016 Retur: Grouped per (Faktur Sumber + Tanggal Retur)

Satu dokumen **Retur Penjualan** merekap semua retur yang berbagi faktur sumber & tanggal retur. Melengkapi [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] & [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]].

## Context

- Implementasi awal ([[ADR - 0012 Retur Refund-only Push-all]]): **1 dokumen Retur Penjualan per `return_sn`**. Akibatnya beberapa retur yang jatuh di hari sama & membalik faktur yang sama jadi beberapa dokumen terpisah — finance merekapnya manual.
- Permintaan bisnis: retur dengan **tanggal & toko yang sama direkap jadi satu** dokumen retur.
- **Kendala Accurate (menentukan)**: `sales-return/save.do` punya **satu** field `invoiceNumber` di **header**, dan `detailItem` **tak punya rujukan faktur per baris**. Artinya **satu Retur Penjualan = satu faktur** — merekap retur lintas-faktur **mustahil**, bukan soal implementasi.
- Faktur auto-sync dikunci **1:1** per `(shop_id, channel, hari-kirim)` (`accurate_daily_invoices`; terverifikasi prod: 0 duplikat, dan tanggal di nomor faktur == `date_wib` pada 500/500 sampel). Maka **"faktur yang sama" ≡ "toko + tanggal-faktur yang sama"** — dua kalimat untuk hal identik.
- **Sistem lama finance sampai ke kunci yang sama** (bukti prod: `RTR/26/07/14/014-BH`, Qty 3 — tiga order dengan **tanggal order berbeda** (4 & 5 Jul) tapi **satu faktur** `INV/2026/07/06/015-BH`). Dua sistem yang dibangun terpisah bertemu di kunci yang sama karena kendala Accurate-nya sama.

## Decision

**1. Group key = `<invoice_number>|<YYYYMMDD tanggal-retur>`** (`returnGroupKey`), unik per `(shop_id, channel)` lewat index `uniq_shop_channel_dedupe`. Faktur **WAJIB** bagian kunci — konsekuensi langsung kendala Accurate di atas. **Tanggal order TIDAK berperan** (sistem lama pun begitu).

**2. Entity grup**: `Members []ReturnGroupMember{OrderID, ReturnSN}` = sumber kebenaran anggota (`order_id`/`return_sn` top-level hanya penanda member pertama utk tampilan). `LinesHash` = sidik jari line-set terakhir yang dibukukan.

**3. Rebuild = HAPUS dok lama + book fresh** (bukan edit in-place — menghindari risiko protokol edit pada baris bundle). Hanya dijalankan bila `lines_hash` berubah (idempoten). Gagal hapus → **batalkan book** (cegah dua dokumen). Setelah hapus sukses → `accurate_return_id` **langsung di-clear**; tanpa itu, book yang gagal meninggalkan id dok terhapus → retry mencoba menghapusnya lagi → grup **macet permanen**.

**4. Mode header campuran** (barang-balik + refund-only dalam satu grup) → `PARTIALLY_RETURNED` (`aggregateGroupHeaderMode`); baris tetap per-mode (`deriveReturnMode` dihitung ulang tiap rebuild dari `solution`+`partial`).

**5. Sanity over-retur per GRUP** (`groupWouldOverReturn`): total qty grup vs qty terjual di faktur. `srcInv.ReturnQuantity` **hanya** dihitung saat first-book — pada rebuild, dok lama grup sendiri masih terhitung di sana → self-count → false-fire.

**6. Guard anti-dobel by-MEMBER** (`GetByMember`, index `shop_channel_member_returnsn`) — **tidak** bergantung `dedupe_key`. Kunci memuat tanggal, jadi **begitu tanggal retur bergeser, kunci ikut bergeser** → lookup by-key meleset → grup baru → retur yang sama dibukukan **dua kali** di Accurate. Terbukti lewat tes: tanpa guard ini, pergeseran tanggal menghasilkan dokumen ganda.

## Consequences

- **Manfaat praktis kecil, dan itu wajar**: hanya **2 peleburan dari 74** dokumen (prod 2026-07-17). Sebab: faktur dibuat per **hari-kirim**, sedangkan retur di hari sama umumnya berasal dari order yang dikirim di hari **berbeda** → faktur berbeda → tak bisa digabung. Grouping dibatasi **cara faktur dipecah**, bukan kode. Memperbanyaknya = mengubah granularitas faktur (mis. per minggu) → keputusan finance, bukan teknis.
- **Nomor RTR** dibentuk dari **tanggal retur** (`util.WIBDayStart(transDateAt)`), bukan hari-kirim — lihat [[ADR - 0017 Tanggal Retur TikTok via order_update_date]].
- **Migrasi**: `cmd/returnconsolidate` (DRY-RUN default) menggabungkan dokumen lama; **wajib `RTS_RETURN_ENABLED=true`** + verifikasi hasil (lihat Consequences [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]]).
- **FE**: `auto-sync-return` menampilkan badge "N pesanan" + daftar order member; `GetDailyReturnDetail` mengembalikan baris **gabungan** semua member + `orders[]`.
- Baris lama pra-grup (ber-`dedupe_key` = `return_sn`) tetap aman: `GetByMember` juga mencocokkan penanda representatif → tak dibukukan ulang.

## Dokumen Terkait
- [[Microservices - Integration Service]] — Auto-Sync Retur (model grup)
- [[ADR - 0017 Tanggal Retur TikTok via order_update_date]]
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]]
- [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]]
- [[APP - Web ERP]] — halaman Auto-Sync Retur

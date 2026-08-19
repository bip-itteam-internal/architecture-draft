**Status**: ✅ **Implemented** (kode + deploy 2026-07-17). **Amandemen 2026-08-20 (✅ deployed, PR #1299):** kunci grup ditambah segmen **JENIS** → `<faktur>|<YYYYMMDD>|<JENIS>` — satu dokumen = satu jenis retur (Decision #1 diperluas; Decision #4 mode-campuran **tak lagi terjadi** untuk dokumen baru). Lihat amandemen di bawah.

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

### Kunci grup punya TIGA cara jadi basi — semuanya berujung dokumen ganda

Kunci `<faktur>|<tanggal>` menggabungkan dua nilai yang **bisa bergerak setelah baris dibuat**. Begitu salah satunya bergeser, lookup by-key meleset, rebuild tak menemukan dokumen lama untuk dihapus, dan lahirlah **dua Retur Penjualan untuk satu retur**. Ketiganya terpisah ditemukan, satu pola:

1. **Tanggal bergeser** (didokumentasikan sejak awal, Decision #6) → ditutup guard anti-dobel **by-MEMBER** yang tak bergantung kunci.
2. **`trans_date` tak diwarisi saat re-book** → ditutup PR #1000 `34ee2cd1` (2026-08-06): `SyncOrderReturn` mewarisi `trans_date`/`date_source` baris existing sebelum membentuk kunci. Lihat [[Microservices - Integration Service]].
3. **Nomor faktur basi di dalam kunci** (ditemukan 2026-08-06 saat remediasi paket). Faktur yang dibuat ulang di Accurate berganti id/nomor, tapi `dedupe_key` baris retur masih menyimpan nomor lama → re-book membentuk kunci baru. Terjadi nyata: `RTR/2026/07/10/102` melahirkan `103` (Accurate id 113437) sementara 102 tetap hidup. **Terdeteksi dari cacah faktur 10 → 11**, bukan dari error apa pun — mekanisme ini **gagal senyap**. Sensus: **29 dari 1.652** baris SENT masih memikul nomor faktur basi. Belum ada guard; yang menahan kerusakan cuma guard by-member (#1), dan itu hanya menolong bila membernya benar-benar beririsan.

⚠️ **Jebakan saat membetulkan data: re-book bisa MENGHIDUPKAN baris `SKIPPED`.** Membukukan ulang satu baris "penyintas" dari sepasang dokumen kembar akan ikut menarik member yang baris pasangannya sengaja `SKIPPED` — bila member pasangan itu **bukan himpunan bagian** dari member penyintas, hasilnya dokumen Accurate baru untuk retur yang sengaja tak dibukukan. Terjadi pada `RTR/2026/07/22/003` & `RTR/2026/07/23/055-BH`; ketahuan karena cacah SENT jadi 1.294, bukan 1.292 — **selalu cacah ulang sesudah remediasi, jangan percaya laporan alatnya saja.**

- **Pembersihan dokumen kembar ✅ SELESAI 2026-08-06**: Agustus **8 pasang** (−Rp1.500.000); Juli **9 pasang** se-bulan + **4 pasang** lintas-bulan (−Rp1.033.500). Dihapus lewat `cmd/returndescope --return` (memakai `sales-return/delete.do`).

### Amandemen 2026-08-20 — segmen JENIS di kunci grup: satu dokumen = satu jenis (✅ deployed, PR #1299)

**Permintaan finance**: keterangan dokumen tak boleh "campur" — pengelompokan juga per **jenis retur**. Kunci grup menjadi `<faktur>|<YYYYMMDD>|<JENIS>` dengan JENIS = segmen stabil dari `classifyReturnKind` (`RETUR_REFUND` barang+dana / `REFUND_DANA` dana-saja / `RETUR_COD` batal tanpa dana; `returnKindKeySegment` — segmen ≠ label tampilan, karena label RETUR COD bisa "RETUR <metode gabungan>" yang berubah ikut komposisi). Konsekuensi: retur beda jenis pada faktur+tanggal sama → **dokumen terpisah & homogen** → keterangan (`returnDescriptionLabel` agregat) otomatis bersih, mode header tegas (`RETURNED`/`NOT_RETURNED`; `PARTIALLY_RETURNED` kini **murni dari retur parsial**, bukan campuran mode lintas member — Decision #4 tak lagi terjadi utk dokumen baru). Satu faktur+tanggal kini bisa 2–3 dokumen RTR.

**Kompat-mundur TANPA migrasi** (pola pelajaran §"tiga cara kunci jadi basi"): `return_kind` **dipersist** di baris saat dibuat (seperti `trans_date`); `pindahKeGrupGudang` memakai jenis tersimpan → baris LAMA tanpa jenis tetap berformat lama & gabung-gudang tak lintas format/jenis. Reuse `trans_date` (butir #2) **diperluas ke KUNCI PENUH**: member yang sudah punya baris memakai `dedupe_key` tersimpan, dengan dua pengecualian — baris jejak `SKIPPED` (kunci per-`return_sn`; mengadopsinya = menghidupkan keputusan yang sengaja dilewati, lubang amandemen ADR-0024 2026-08-05) dan baris ber-faktur beda/kosong (penanda gagal-fetch `RecordReturnFetchFailure`). Cabang "kunci bergeser" pada guard SENT yang mati oleh reuse dihapus. **Dokumen lama campur (~84, Jul–Ags) SENGAJA dibiarkan** (keputusan user; pecah-ulang = hapus+book-ulang → sentuh stok + nomor RTR); label agregatnya tetap benar & kolom laporan per-order (PR #1260) menampilkan jenis per baris. Grounded: `returnGroupKey`/`returnKindKeySegment`/`SyncOrderReturn`/`pindahKeGrupGudang` (`accurate_rts_usecase.go`), `entity.AccurateDailyReturn.ReturnKind`, tes `accurate_return_groupkey_test.go` + `accurate_return_group_gudang_test.go`.

## Dokumen Terkait
- [[Microservices - Integration Service]] — Auto-Sync Retur (model grup)
- [[ADR - 0017 Tanggal Retur TikTok via order_update_date]]
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]]
- [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]]
- [[APP - Web ERP]] — halaman Auto-Sync Retur

**Status**: ✅ **Implemented & Deployed** (2026-08-06, PR #1017 commit `35b1860d`; koreksi data existing Juli+Agustus **SELESAI** hari yang sama lewat **dua gelombang** — 245 + 109 dokumen, sisa temuan **0**, nomor RTR utuh; gelombang 1 sempat bocor 109 dokumen karena detektornya bergantung fetch Accurate yang gagal senyap, lihat Consequences). Menyempurnakan pembentukan baris Retur Penjualan untuk SKU **paket/bundle** — uang mengikuti harga paket di faktur, stok tetap mengikuti pecahan komponen.

# ADR - 0040 Retur Paket Utuh: Bukukan BARIS INDUK Faktur, Bukan Komponen

Keputusan dari investigasi anomali "Ter-book Rp0" (2026-08-04/06) pada [[Microservices - Integration Service]] Auto-Sync Retur. Melengkapi [[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]] (bentuk dokumen) dan tidak mengubah gerbang di [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] / [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]].

## Context

Accurate mencatat bundle sebagai **baris INDUK berharga** (`itemType GROUP`) diikuti **sub-baris komponen ber-`unitPrice` 0** yang mengikutinya sampai baris berharga berikutnya. Sub-baris komponen itulah yang memikul `returnQuantity` dan menggerakkan stok. Struktur ini terverifikasi pada **8 bundle / 3 faktur** prod (2026-08-05); harga induk **berbeda per faktur** (mis. `PJG-002 + PJG-004` @98.000 di satu faktur, @93.000 di faktur lain) sehingga **wajib dibaca per-faktur**, bukan dari master.

Pembentuk baris retur memecah paket jadi komponen lalu mencari harga tiap komponen. Dua aturan bertabrakan pada satu paket:

1. komponen yang **kebetulan punya baris jual satuan** di faktur hari yang sama → dihargai **harga satuan**;
2. komponen lain → **dialokasikan** dari harga induk.

Akibatnya satu paket dihargai dua aturan sekaligus dan totalnya **melebihi harga paketnya**. Terukur prod 2026-08-06:

| Dokumen | Paket yang diretur | Harga faktur | Dibukukan | Kelebihan |
|---|---|---|---|---|
| `RTR/2026/08/04/018-KY+GB` | `PJG-002 + PJG-003 + PJG-004` | 146.000 | 59.000+59.000+48.667 = **166.667** | +20.667 |
| `RTR/2026/08/04/067-KY+GB` | `PJG-003 + PJG-006` | 93.000 | 59.000+48.667 = **107.667** | +14.667 |
| `RTR/2026/08/05/047-KY+GB` | `PJG-001 isi 3` | 146.000 | 3 × 59.000 = **177.000** | +31.000 |

Akar teknisnya di `buildWarehouseDetailItems`: tiap barang hasil scan gudang dibungkus jadi **order sintetis satu baris** (`OrderID: "warehouse-confirm"`) sebelum harga dihitung → **konteks paket hilang**, jadi resolver tak pernah tahu komponen itu bagian dari paket mana.

**Harga pecahan (48.666,67) hanya GEJALA**, bukan penyakitnya — mayoritas kasus meleset dalam rupiah bulat sehingga tak terlihat. Dari 1.589 retur SENT sejak 10 Juli, **707 (44%) melibatkan SKU paket** = populasi berisiko, tapi hanya 2 yang punya penanda kasatmata.

**Jalan buntu yang sempat ditempuh**: membobot alokasi dengan refund per item dari marketplace **TIDAK BISA** — `return.items[].sku` terukur **45 dari 45 = SKU listing**, tak pernah komponen. Untuk paket, marketplace hanya punya SATU baris retur menutupi seluruh paket.

## Decision

**Retur paket UTUH membukukan BARIS INDUK paket @harga faktur, bukan komponennya.** Accurate otomatis menurunkan sub-baris komponen @Rp0 yang menggerakkan stok — satu tindakan memenuhi dua kebutuhan sekaligus:

- **UANG** mengikuti harga paket di faktur (tak mungkin melebihi yang dicatat penjualan);
- **STOK** tetap mengikuti pecahan komponen (Accurate yang menurunkannya).

Tak perlu dua mekanisme, tak ada rupiah pecahan. `buildWarehouseDetailItems` kini menerima **daftar order anggota + faktur sumber**, mencocokkan hasil scan **per pesanan** dengan komposisi paket yang pesanan itu beli, lalu mengirim SKU induknya bila lengkap. `buildReturnDetailItems` berhenti memecah paket yang punya baris induk berharga.

**Retur SEBAGIAN** (paket isi 3, balik 1 botol) tetap **alokasi proporsional** dari nilai induk, dibulatkan ke rupiah penuh (*largest remainder*) — bukan harga satuan komponen.

**Bobot alokasi = harga satuan `all-or-nothing`**: dipakai hanya bila **SEMUA** komponen punya baris jual satuan di faktur itu; selain itu **RATA**. Bobot campur ditolak karena menekan sistematis komponen yang tak punya baris satuan (terukur: PJG-003 dapat 42.632 vs rata 48.667 padahal sekelas).

## Consequences

- **Over-reversal kelas ini tertutup by-design**: nilai retur paket ≤ harga paket di faktur, karena angkanya **disalin** dari baris faktur, bukan dihitung ulang.
- **Bentuk dokumen berubah**: retur paket kini **1 baris induk + n sub-baris komponen @Rp0** (cermin persis baris fakturnya), dulu n baris komponen berharga. Stok **tidak berubah** — jumlah unit komponen sama.
- **Koreksi data existing SELESAI 2026-08-06** (`cmd/returnfix --returns <nomor> --apply`, nomor RTR dipertahankan): 3 dokumen Agustus (−Rp66.334) + 3 dokumen Juli (−Rp123.000). Audit `--category zero` & `--category nilai` **0 temuan** dari 1.644 retur SENT sejak 1 Juli.
- **Sapuan data lama — DUA GELOMBANG, ✅ tuntas 2026-08-06.** Semula direncanakan "tak ada sweep otomatis, tunggu grup tersentuh sendiri", tapi pemilik meminta seluruh data Juli–Agustus dibetulkan sekaligus.
  - **Gelombang 1 — 245 dari 246 dokumen** (Σ kelebihan Rp8.840.000 → Rp96.000). Sisa 1 (`RTR/2026/07/30/094-KY+GB`) tertahan **guard anti-dobel**, bukan gerbang income — pesan `returnfix` menyebut "gerbang income" dan itu **menyesatkan**.
  - **⚠️ Gelombang 1 TERNYATA TIDAK LENGKAP** — pemilik menemukan sendiri satu dokumen yang masih salah (`RTR/2026/08/05/077-KY+GB`). Sebabnya di butir detektor di bawah. Sensus ulang menemukan **109 dokumen** lagi.
  - **Gelombang 2 — 109 dokumen** (105 berharga-komponen + 4 diperiksa terpisah): Σ Rp14.750.000 → Rp12.700.000 dan Rp610.000 → Rp659.000. Dikerjakan bertahap 5 → 73 → 27 (dengan snapshot pengaman di antaranya) karena **27 di antaranya berisiko**: membernya punya baris `SKIPPED` yang bisa hidup lagi saat re-book. Semua gelombang mempertahankan **nomor RTR**.
  - **Sesudahnya: sisa temuan 0**, dokumen berbaris-induk **362**, `accurate_return_id` kembar **0**.
- **⚠️ Detektor berbasis FETCH FAKTUR gagal SENYAP — jangan dipakai lagi.** Versi yang menurunkan komposisi bundle dari dokumen faktur di Accurate butuh satu panggilan API per dokumen; panggilan yang kena **429 hilang tanpa error**, sehingga angka "246 dokumen" adalah *yang berhasil dibaca*, bukan *yang ada* — itulah sebab gelombang 1 bocor 109 dokumen. **Detektor yang benar tidak memanggil Accurate sama sekali**: komposisi paket dibaca dari string SKU pesanan (`transaction_orders.items[].sku` menyimpan literal `"PJG-002 + PJG-004"` / `"PJG-001 isi 2"`), scan dari `warehouse_items` per `order_id`. Pembeda pasti: **baris induk mustahil ada sebelum deploy 2026-08-06 08:44 WIB**, jadi dokumen paket-utuh ber-`updated_at` lebih tua pasti masih berbaris komponen — tak perlu menebak harga.
  > **Aturan umum**: audit yang bergantung fetch pihak ketiga WAJIB melaporkan jumlah fetch **gagal**, dan hasilnya diperlakukan sebagai **batas bawah**. Kalau ada sinyal DB-only yang setara, pakai itu.
- **Versi pertama detektor juga salah, dengan penanda yang khas**: 415 temuan Σ **−Rp11.739.000** — retur bundle **sebagian** ikut tertuduh, dan kelebihan satu bundle diadu dengan **total dokumen**. Penandanya Σ **negatif** padahal tiap baris contoh positif; jumlah bertanda campur pada besaran yang mestinya searah = **rumusnya** yang salah, bukan datanya.
- **Pengaman paling tajam untuk re-book massal: cacah `accurate_return_id > 0` TOTAL.** Rebuild = hapus + buat, jadi angkanya harus **TETAP**; baris `SKIPPED` yang hidup akan menaikkannya. Terbukti pada seluruh gelombang 2 (2679 sebelum dan sesudah, kembar 0). ⚠️ **Jangan** memakai "SKIPPED ber-`accurate_return_id` > 0" sebagai uji kebangkitan — ada **1.016** baris seperti itu dan semuanya warisan descope 19 Juli yang id-nya menunjuk dokumen terhapus.
- **Harga paket terverifikasi dari faktur** (dasar audit berikutnya): `PJG-002 + PJG-004` = **98.000** (sebagian faktur 93.000) · `PJG-002 + PJG-003 + PJG-004` = 146.000 · `PJG-001 isi 2` = 93.000 · `PJK-010 isi 2` = 196.000 · `PJK-009 + PJK-010` = 174.000 — dibanding harga komponen 59.000/botol.
- **Koreksi bisa berjalan DUA ARAH.** Tiga dari empat dokumen yang dipisahkan karena nilainya bukan kelipatan harga komponen ternyata **sudah benar** dan tak bergerak saat dibangun ulang (rebuild bersifat idempoten — itu sekaligus cara membuktikannya). Yang keempat justru **naik** Rp223.000 → Rp272.000: dokumen itu **kurang** membalik. Jadi kelas bug ini tak selalu over-reversal.
- **"Aman ke depan" belum teruji di jalur otomatis.** Dari **98 dokumen retur yang lahir setelah deploy**, **0** memuat paket kembali utuh (mayoritas masih menunggu scan gudang) — jadi jalur gudang→baris-induk **belum pernah dijalani sekali pun di prod**. Yang terbukti: kodenya ter-deploy + 362 dokumen benar hasil koreksi memakai sumber yang sama. **Spot-check retur paket pertama yang discan** setelah ini.
- **Gerbang gudang baru hidup 22 Juli** ([[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]) — retur yang lebih tua **tak pernah** melewatinya. Karena itu `--skip-warehouse-gate` **tak boleh dipukul-rata** ke seluruh 246 dokumen saat remediasi: pada dokumen pasca-22-Juli, melewati gerbang berarti membukukan barang yang belum discan siapa pun.
- **Membetulkan retur TIDAK menuntut koreksi tandingan di income** — pertanyaan yang wajar muncul saat nilai retur berubah. Dibuktikan ke dokumen terposting `INC/2026/07/14/015-KY+GB`: `buildReceiptPayload` hanya membukukan **akun beban** (6112/6113/6114) dan **tak pernah membaca** nilai Retur Penjualan. Retur mengkredit piutang, receipt membayarnya, keduanya dihitung independen. Sebelum koreksi, retur mengkredit Rp118.000 atas baris faktur Rp98.000 → fakturnya **kelebihan dilunasi Rp20.000**; koreksi ini **menghapus kelebihan itu**, bukan menciptakan kekurangan baru. Detail sensus di [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]].
- ⚠️ **Konsekuensi yang WAJIB disampaikan ke finance**: karena pembalikannya berkurang, **pendapatan Juli–Agustus NAIK ±Rp10,7 juta** (gelombang 1 Rp8,74 jt + gelombang 2 Rp2,00 jt bersih). Itu memang isi koreksinya, tapi kalau Juli sudah ditutup/dilaporkan, angkanya bergerak. **Belum diverifikasi**: saldo piutang aktual per faktur di Accurate — penalaran memperkirakan bergerak dari minus menuju nol, tapi belum dicek dokumen per dokumen.
- **Jangan jalankan audit & `--apply` berbarengan.** Accurate membatasi **8 request/detik per token** dan keduanya berbagi token yang sama → 429, dan satu retur sempat jadi `FAILED` palsu karenanya.
- **Kopling ke kebijakan kondisi barang**: baris induk **tak bisa** menyatakan kondisi per komponen (Reuse/Rework/Reject). Aman selama ketiganya dibukukan `RETURNED` (keputusan 2026-07-21, [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]). Bila kebijakan itu dibalik (Reject → `NOT_RETURNED`), model paket-utuh **harus pecah lagi** ke komponen.
- **Belum terverifikasi**: apakah Accurate menerima baris induk `GROUP` ber-`NOT_RETURNED` (refund-only). Yang terbukti hanya mode `RETURNED`. Paparan kecil; gagal → `FAILED` (terlihat).
- **Guard NILAI over-retur ADA tapi TIDAK disambungkan** (`accurate_return_value_guard.go`, audit-only). Alasannya diukur: faktur kita **harian agregat**, sementara model kepemilikan first-wins mengandaikan faktur per pesanan → guard meleset **dua arah** (salah-tuduh 6 dari 9 temuan Juli; sekaligus **melewatkan** kasus yang melahirkannya karena plafonnya nilai SEHARI). Uji yang sahih = SKU paket yang **dibeli pesanan** vs baris faktur, bukan agregat harian.

## Dokumen Terkait
- [[Microservices - Integration Service]] — Auto-Sync Retur (pembentukan baris & harga)
- [[ADR - 0016 Retur Grouped per Faktur + Tanggal Retur]] — bentuk dokumen grup
- [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]] — gerbang payout (tak diubah ADR ini)
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] — gerbang gudang & kebijakan kondisi barang
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]] — semua pembalikan lewat retur

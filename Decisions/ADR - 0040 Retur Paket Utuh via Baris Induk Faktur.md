**Status**: ✅ **Implemented & Deployed** (2026-08-06, PR #1017 commit `35b1860d`; koreksi data existing Juli+Agustus **SELESAI** hari yang sama — **245 dari 246 dokumen** disapu, Σ kelebihan Rp8.840.000 → Rp96.000, nomor RTR utuh). Menyempurnakan pembentukan baris Retur Penjualan untuk SKU **paket/bundle** — uang mengikuti harga paket di faktur, stok tetap mengikuti pecahan komponen.

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
- **Sapuan data lama ✅ SELESAI 2026-08-06** — semula direncanakan "tak ada sweep otomatis, tunggu grup tersentuh sendiri", tapi user meminta seluruh data Juli–Agustus dibetulkan sekaligus. **245 dari 246 dokumen** berhasil dikoreksi lewat `cmd/returnfix --apply`: Σ kelebihan **Rp8.840.000 → Rp96.000**, dokumen berbaris-induk **338 → 600**, **nomor RTR dipertahankan**, jumlah baris SENT tak bergeser (1.653), dan **nol** `accurate_return_id` kembar. Sisa **1 dokumen** (`RTR/2026/07/30/094-KY+GB`, Rp96.000) tertahan **guard anti-dobel**, bukan gerbang income — pesan `returnfix` menyebut "gerbang income" dan itu **menyesatkan**.
- **Audit paket wajib membandingkan per-BUNDLE, bukan per-dokumen.** Versi pertama detektornya melaporkan 415 temuan Σ **−Rp11.739.000** — dua cacat: retur bundle **sebagian** ikut tertuduh, dan kelebihan satu bundle diadu dengan **total dokumen**. Penandanya: Σ **negatif** padahal tiap baris contoh positif — jumlah bertanda campur pada besaran yang mestinya searah = ukurannya salah, bukan datanya. Versi benar menurunkan komposisi bundle **dari fakturnya** lalu menghitung kelebihan hanya atas baris komponen bundle itu.
- **Gerbang gudang baru hidup 22 Juli** ([[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]) — retur yang lebih tua **tak pernah** melewatinya. Karena itu `--skip-warehouse-gate` **tak boleh dipukul-rata** ke seluruh 246 dokumen saat remediasi: pada dokumen pasca-22-Juli, melewati gerbang berarti membukukan barang yang belum discan siapa pun.
- **Membetulkan retur TIDAK menuntut koreksi tandingan di income** — pertanyaan yang wajar muncul saat nilai retur berubah. Dibuktikan ke dokumen terposting `INC/2026/07/14/015-KY+GB`: `buildReceiptPayload` hanya membukukan **akun beban** (6112/6113/6114) dan **tak pernah membaca** nilai Retur Penjualan. Retur mengkredit piutang, receipt membayarnya, keduanya dihitung independen. Sebelum koreksi, retur mengkredit Rp118.000 atas baris faktur Rp98.000 → fakturnya **kelebihan dilunasi Rp20.000**; koreksi ini **menghapus kelebihan itu**, bukan menciptakan kekurangan baru. Detail sensus di [[ADR - 0024 Retur Gerbang Payout + Tanggal per-Solution]].
- ⚠️ **Konsekuensi yang WAJIB disampaikan ke finance**: karena pembalikannya berkurang, **pendapatan Juli–Agustus NAIK ±Rp8,74 juta**. Itu memang isi koreksinya, tapi kalau Juli sudah ditutup/dilaporkan, angkanya bergerak. **Belum diverifikasi**: saldo piutang aktual per faktur di Accurate — penalaran memperkirakan bergerak dari minus menuju nol, tapi belum dicek dokumen per dokumen.
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

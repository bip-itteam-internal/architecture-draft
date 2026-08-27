**Status**: ⚠️ **Implemented & Deployed; perbaikan cacat MENUNGGU DEPLOY** (cacat 2026-08-07: cabang bukti-mutasi-dompet men-skip kasus yang justru TIDAK dobel, paparan 1 order — **fix di PR #1085, belum deploy**; lihat amandemen 2026-08-07 & 2026-08-08). Riwayat: (2026-07-18/19: gerbang payout + tanggal per-solution + pemicu settlement + **cutover retur ikut faktur/hari-kirim** + gate cutover-fix; deploy 2026-07-19; cleanup data existing **SELESAI** — descope 1565 retur < 1 Jul, void 1 dobel). **Amandemen 2026-08-05 (✅ DEPLOYED 2026-08-05, commit `779b0a06`; verifikasi prod: 38 baris jejak tersemai, dari 1):** janji "SKIP → baris `SKIPPED`" di Decision #1 akhirnya benar-benar dipenuhi — sebelumnya baris hanya ditandai bila kebetulan sudah ada, sehingga mayoritas retur payout>0 **tak berjejak sama sekali** di UI; sekaligus menutup lubang dobel-booking lewat konfirmasi gudang yang baru terlihat setelah baris jejak itu ada. **Amandemen 2026-08-06 (✅ DEPLOYED, PR #1038):** cabang Shopee berhenti menebak dari kanal dan **menuntut bukti** mutasi penyerap; backfill + sensus penutup SELESAI hari yang sama (129 dari 131 retur ACCEPTED sudah berbaris; 2 sisanya DEFER benar). Lihat Consequences. **Amandemen 2026-08-12 (kode, belum deploy):** fallback tanggal **hari-kirim DIBUANG**, ganti ke `order.returned_at` lalu tanggal deteksi (PR bip-erp#1161 + erp-frontend#977). **Amandemen 2026-08-26 (✅ DEPLOYED, PR #1451):** kompensasi paket hilang ([[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]]) kini ikut menyerap — jalur cancel tak lagi membukukan retur untuk pesanan batal yang fakturnya sudah dilunasi kompensasi.

# ADR - 0024 Retur: Gerbang Payout≈0 (Income vs Retur) + Tanggal per-Solution

Dua keputusan dari satu investigasi (2026-07-18, "Opsi B") yang membenahi **Retur Penjualan** auto-sync ke Accurate. Menggantikan sebagian [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] (keputusan tanggal) & premis refund-only-as-retur di [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] / [[ADR - 0012 Retur Refund-only Push-all]].

## Context

Investigasi berangkat dari keluhan: tanggal & jumlah retur di ERP ≠ Shopee (contoh `260622R69SUCKP`). Dua temuan grounded:

**1. Refund Shopee = penyesuaian INCOME (escrow), bukan dokumen retur.** `get_escrow_detail`: `order_income.escrow_amount` **sudah net-of-refund** (rumus resmi memuat `+seller_return_refund`; kurir-salah → `seller_lost_compensation` menutup, seller tak rugi). ERP punya **dua sisi** di Accurate: Faktur+Retur (revenue) & **Auto Sync Income / Bukti Terima Kas** (kas). `buildReceiptPayload` (`accurate_receipt_usecase.go`) **sudah** menyerap refund untuk order **payout>0** (baris Potongan Penjualan `discount = basePorsi − payment − feeLain`, `payment`=payout net-of-refund; akun discount 4003) & **melunasi piutang penuh**; order **payout≈0** (refund penuh) **di-skip receipt** (Accurate tolak baris 0-payment) → kode itu sendiri mengarahkan koreksi **lewat retur**. Tapi pipeline retur membukukan **SEMUA** retur tanpa melihat payout → untuk order payout>0 terjadi **DOBEL** (revenue balik dua kali + piutang ter-kredit minus). Terukur prod: **7 RTR SENT dobel**, 92 baris FAILED payout>0 = ranjau (jadi dobel bila di-retry).

**2. Tanggal `accepted` Shopee TIDAK bersih.** [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] memakai `accepted` (`update_time`) seragam dengan premis "Shopee tak kena settle-drift". **Terbantah 2026-07-18**: `updated_at` Shopee **melar mundur** saat settle refund — median **3 hari**, 46 dari 49 lebih lambat dari kedatangan fisik (penyakit sama `update_time` TikTok). `return_tracking` (reverse-tracking RECEIVED / `last_event_at`) menyediakan tanggal **fisik** barang-sampai untuk 49 retur barang-balik Shopee — lebih benar.

**3. Shopee tak punya push retur.** `push_config_on_list` resmi (13 tipe: order-status, tracking-no, dst.) **tak memuat return/refund** → retur tak real-time; koreksi harus lewat **field anti-drift + polling**, bukan webhook. (Push order-status hanya bantu deteksi **cancel**.)

## Decision

**1. Retur Penjualan ⟺ order `payout ≈ 0`.** `returnPayoutGate(order)` (`accurate_rts_usecase.go`, reuse `payoutOf()` **identik** dgn receipt):
- order **CANCELLED** → **book** langsung (tak punya escrow, tak menunggu).
- income belum settle (`Income.PaidAt == nil`) → **DEFER** (payout belum diketahui).
- settled & **payout > 0 & ship ≥ 10 Jul** (post-cutover faktur) → **SKIP** (baris `SKIPPED`; Auto Sync Income/receipt menyerap refund). ⚠️ **Syarat cutover WAJIB**: receipt sendiri skip ship < 10 Jul → untuk pra-cutover retur TETAP book (kalau di-skip, pembalikan HILANG — tak ada yang menangani).
- settled & **payout ≈ 0** → **book**.

Dipasang di `SyncOrderReturn` (auto) & `RetryDailyReturn` (manual tolak payout>0/belum-settle). **Pemicu**: retur DEFER di-book saat escrow cair — `triggerReturnAfterSettlement` di `syncEscrowReleaseWindow` (refetch branch, `shopee_new_usecase.go`) memanggil `SyncOrderReturn` bila payout≈0; urutan sebaliknya (settle dulu, retur menyusul) ditangani ingestion `SyncReturns` yang gate-nya melihat income settled. Idempoten (guard by-member) & fire-and-forget.

**2. Tanggal retur per-solution (Shopee).** `resolveReturnTransDate`: CANCELLED→`cancelled_at`; **TikTok**→`order_update_date` (tetap, [[ADR - 0017 Tanggal Retur TikTok via order_update_date]]); **Shopee refund-only** (`solution=1`)→`requested_at` (`create_time`, anti-drift); **Shopee barang-balik** (`solution=0`) + `return_tracking.status==RECEIVED` + `last_event_at`→**arrival**; fallback `updated_at`→`requested_at`→`order_returned` lalu `detected` (jaring terakhir bila tak ada timestamp marketplace; `shipped` DIBUANG, lihat amandemen 2026-08-12). Memakai sub-doc `return_tracking` yang **sudah** diisi cron reverse-tracking — **bukan** menghidupkan `arrivalResolver` lama yang dicabut ADR-0023.

**3. Cutover retur = HARI KIRIM (ikut faktur), bukan tanggal-retur** (2026-07-19). Gate cutover di `SyncOrderReturn`/`RetryDailyReturn`/`RecordReturnFetchFailure` menilai `dateWIB` (hari-kirim = tanggal faktur sumber) ≥ `autoSyncReturnCutoverDateWIB` "20260701" — BUKAN tanggal retur. Alasan: retur harus mengikuti era faktur & income sumbernya. Order kirim < 1 Jul = era **manual finance** (faktur IMPORTED/tak-ada, income di-skip receipt) → returnya JUGA manual, tak auto. Basis tanggal-retur lama menarik retur order-lama (kirim Mei/Juni, faktur manual) ke auto → retur auto membalik pembukuan manual (tak konsisten + dobel). Menggantikan basis retur di [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] #2 (struktur split 2-konstanta tetap; basis retur berubah).

## Consequences

- **Dobel mustahil by-design**: payout>0 & payout≈0 saling eksklusif — Receipt ATAU Retur, tak pernah keduanya.
- **Income/Auto Sync Income sync TIDAK diubah** — ia sudah benar (menyerap refund payout>0, defer payout≈0 ke retur). Perbaikan 100% di sisi retur.
- **Tanggal benar go-forward**: refund-only pakai tanggal ajukan (stabil), barang-balik pakai tanggal fisik sampai gudang.
- **Menggantikan**: ADR-0023 **keputusan #1** (accepted-seragam) — premisnya salah; ADR-0023 **keputusan #2** — struktur split tetap, **basis cutover retur diubah** (tanggal-retur → hari-kirim, lihat Decision #3). Juga menutup premis "refund-only selalu jadi retur" di [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] / [[ADR - 0012 Retur Refund-only Push-all]].
- **Cleanup data existing (✅ SELESAI 2026-07-19)**: `cmd/returndescope` mengeluarkan **1565 retur hari-kirim < 1 Jul** dari auto (**1007 dok Retur Penjualan dihapus dari Accurate** via `delete.do`, semua ditandai `SKIPPED`); **1 dobel post-cutover** `RTR/2026/07/16/006-BH` (payout>0 + receipt) di-void. Era kept ≥ 1 Jul: 615 SENT sah + 8 FAILED (SKU era-baru, ditunda).
- **Edge butuh finance**: barang-balik `solution=0` **payout>0** (~48, ~1–2 SENT) — receipt urus revenue, tapi **stok tak balik** (Accurate under-stock). Konservatif (stok-opname backstop), idealnya retur-stok-saja — **ditahan untuk finance**.

### Amandemen 2026-08-05 — keputusan SKIP wajib berjejak (✅ deployed 2026-08-05, commit `779b0a06`)

**Masalah**: Decision #1 menuliskan "SKIP (baris `SKIPPED`)", tapi implementasinya hanya menandai baris yang **kebetulan sudah ada**; bila belum ada, keputusan itu cuma masuk log. Akibatnya retur payout>0 **lenyap total** dari halaman Auto-Sync Retur dan finance tak punya cara tahu pembalikannya ada di dokumen lain. Terukur prod 2026-08-04 pada order Shopee `2607180VU58AJP`: refund pasca-cair **Rp198.930** nyata terbukukan di receipt `INC/2026/07/28/014-BH` (diverifikasi ke Accurate: Bayar faktur −184.000, akun 6112 −32.070, akun 6114 +47.000 = net −198.930), tapi nol jejak di UI retur.

**Keputusan**: `SyncOrderReturn` cabang skip kini **membuat** baris jejak (`seedSkippedReturnRow`) bila belum ada. Baris ini **bukan antrean kerja** — tak ada dokumen Accurate yang lahir darinya — sehingga: dedupe **per-retur (`return_sn`)**, bukan group-key `<faktur>|<tanggal>`; `attempts` tetap 0; `trans_date` **wajib** diisi (filter tanggal FE menyaring lewat field itu — jejak yang tak bisa ditemukan sama saja dengan tak ada). Baris SENT tak pernah diturunkan. **DEFER tetap tanpa baris**: payout belum diketahui, keputusannya belum final, mencatatnya hanya menghasilkan baris yang berubah-ubah sendiri.

**Lubang yang ikut ditutup — dobel-booking lewat scan gudang.** Justru keberadaan baris jejak membukanya: kunci yang dipegang gudang (`return_sn`) seformat `dedupe_key` baris non-grup, sehingga **cadangan pencarian by-key** di `ConfirmReturnFromWarehouse` memungutnya, lalu `rebuildAndSendGroup` — yang **tak punya gerbang payout sendiri** — mengirim Retur Penjualan ke Accurate. Terbukti lewat tes regresi: 1 dokumen terbukukan sebelum diperbaiki, tepat pembalikan dobel yang ADR ini ada untuk mencegah. Lookup utama (`GetByMemberOrderIDAny`) sudah mengabaikan `SKIPPED`; cadangannya yang melewatkan — kini disamakan. Efek sampingnya menutup lubang yang **sudah ada sebelumnya**: baris `SKIPPED` **pra-cutover** pun tadinya bisa dibukukan lewat scan gudang, melanggar cutover Decision #3.

**Konsekuensi**: baris "DILEWATI" kelas ini kini muncul di UI untuk SEMUA channel, termasuk edge `solution=0` payout>0 di atas — justru bagus, finance akhirnya melihatnya. Baris tetap **inert** bagi seluruh proses terjadwal (sweep rekonsiliasi, laporan summary, anomaly check, unmapped-SKU semuanya memfilter SENT/FAILED/PENDING). **Batas yang disadari**: bila payout suatu order suatu saat berbalik ke ≈0 setelah jejaknya dibuat, jalur booking memakai group-key sehingga lahir baris kedua dan jejak lama tertinggal dengan keterangan basi — sangat jarang (penyesuaian wallet tak mengubah `total_settlement_amount`) dan tak menimbulkan kesalahan angka, jadi tak dibuatkan mesin khusus.

### Amandemen 2026-08-05 — gerbang menuntut BUKTI penyerapan (✅ deployed, PR #995 `4bb89eb2`)

Decision #1 memakai `payout > 0` sebagai proksi "receipt sudah menyerap refund". Proksi itu **tak berlaku untuk TikTok**: penyerap yang dimaksud (`ADJUSTMENT_FOR_RR_AFTER_ESCROW_VERIFIED` di `accurate_receipt_wallet_adjustment.go`) **Shopee-only**, dan `tt_shop_transaction_by_orders` menyimpan **1 dokumen per order** (upsert by `order_id`) sehingga clawback pasca-settle tak bisa hidup berdampingan dengan record aslinya. Terukur prod 2026-08-05 pada 38 baris jejak: ke-11 order TikTok yang kena gate masih bersettlement **positif**, nol clawback terlihat; sisi Shopee pun tipis (`shopee_wallet_transactions` tipe RR cuma **35 dokumen total**, dan dari 27 baris gate hanya **2** yang punya).

**Keputusan**: `returnPayoutGate` kini SKIP hanya bila ada bukti penyerapan — kanal **Shopee** (penyerap wallet-adjustment memang ada) **ATAU** `income.TotalRefund != 0` (refund sudah ternetto di settlement). Dipakai `!= 0` karena **tandanya berbeda antar kanal**: TikTok positif (negasi `refund_subtotal`), Shopee negatif (`seller_return_refund + drc_adjustable_refund`). Diuji terhadap 11 order TikTok: 6 flip→book, 2 tetap skip (refund memang ternetto), 3 sudah book sendiri — payout jadi **negatif** setelah TikTok meng-upsert record settlement order yang sama, jadi TikTok **bisa** claw back lewat penimpaan dokumen, bukan dokumen baru.

**Konsekuensi**: 5 dari 6 yang flip bersolution 0 → tertahan **PENDING** gerbang gudang, bukan langsung terbukukan. Ini benar per [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]].

### Amandemen 2026-08-06 — cabang Shopee menuntut BUKTI, bukan kanal (✅ deployed 2026-08-06, PR #1038)

Amandemen di atas masih memakai **kanal** sebagai proksi: "Shopee → pasti ada penyerap". Proksi itu **terlalu lebar**. Penyerapnya satu hal yang sangat spesifik — mutasi dompet `ADJUSTMENT_FOR_RR_AFTER_ESCROW_VERIFIED` — dan mayoritas order Shopee ber-`payout>0` **tidak punya**. Sensus prod 2026-08-06 atas **23 order Shopee** yang gerbang ini skip: hanya **1** punya mutasi RR (`2607180VU58AJP`, −198.930, terverifikasi ke `INC/2026/07/28/014-BH`); **22 sisanya nol penyerap** dan `total_refund` 0 — penjualannya tak pernah terbalik dokumen apa pun, dan **stok barang-baliknya juga tak pernah bertambah** karena receipt tak menggerakkan stok. Menebak dari kanal = menghilangkan 22 pembalikan sah demi melindungi 1.

**Keputusan**: cabang Shopee kini **bertanya** — `HasShopeeRefundAdjustment(orderSN)` pada `shopee_wallet_transactions` (tipe RR, status `COMPLETED`). Hanya tipe RR; `LOST_PARCEL_SELLER_ADD` & `AFFILIATE_SAMPLE_SHIPPING_FEE_DEDUCT` bukan pembalikan penjualan sehingga tak boleh membatalkan retur.

Rinciannya:
- **Lookup MALAS** — dipanggil hanya saat Shopee + settled + `payout>0` + post-cutover + `TotalRefund == 0`. `SyncOrderReturn` jalur panas; menanyakannya di luar kondisi itu = query DB sia-sia. Dua kasus tes mengunci bahwa jalur lain tak menyentuhnya sama sekali.
- **Gagal baca / repo nil → BOOK**, bukan skip. Salah-book masih bisa dihapus (`sales-return/delete.do`); salah-skip menghilangkan pembalikan tanpa jejak. Arah kesalahan yang bisa diperbaiki dipilih sadar.
- **Interface lokal `ReturnAbsorberRepo`** (1 method) + `NewReturnAbsorberRepo()` — interface Go struktural, jadi `repository.WalletRepository` dan seluruh fake-nya tak ikut berubah. Disuntik pasca-konstruksi (`SetWalletAbsorberRepo`) mengikuti pola `SetReturnBooker`.
- **Pra-saring** di `triggerReturnAfterSettlement` & diagnostik `accurate_why` memakai `nil` (keduanya tanpa ctx/repo). Aman: gerbang yang mengikat tetap yang di `SyncOrderReturn`, jadi pra-saring longgar hanya menghasilkan satu panggilan yang berujung skip — bukan dobel. Diagnostik `accurate_why` jadi **meremehkan** penyerapan; itu arah yang benar untuk alat diagnosa.

**Backfill ✅ SELESAI 2026-08-06** (pasca-deploy): baris SKIPPED yang aman dipicu ulang; **47 order backlog cancel** masuk antrean **PENDING** gerbang gudang, bukan langsung terbukukan — benar per [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]. **39 keterangan `last_error` basi** (masih berbunyi *"ditangani Auto Sync Income"*, premis yang gerbang baru ini cabut) ditulis ulang agar menyebut PR #1038 + apakah pembukuan aktualnya ada di baris lain. **7 baris tetap dikarantina** karena refund SEBAGIAN — baru boleh dibukukan setelah keputusan 🟡 di bawah diimplementasi.

**Sensus penutup 2026-08-06 — "apakah ada refund yang terlanjur kehitung ke income?"** Kekhawatiran wajar: jejak SKIP baru tersemai 5 Agustus, jadi keputusan gerbang sebelum itu tak berbekas. Diukur langsung, bukan disimpulkan: dari **131 order** ber-`return.status = ACCEPTED` dan pernah dikirim ≥ 1 Juli, **129 sudah punya baris pembukuan** (`order_id` atau `members.order_id`). **2 sisanya nol baris** (`585194325258241785`, `585173767020054038`, ±Rp260.000, dua-duanya TikTok `solution=0`) dan keduanya **DEFER benar** — escrow belum cair. **Tak ada refund yang nyangkut jadi pendapatan.**

Pengecekan ulang sore harinya menutup keraguan yang sempat muncul. Sempat disimpulkan bahwa TikTok **tak punya** pemicu retur pasca-settle sehingga order DEFER-nya akan hilang — dasarnya benar (`triggerReturnAfterSettlement` memang hanya ada di `shopee_new_usecase.go`), tapi **kesimpulannya salah**: `585194325258241785` yang escrow-nya cair 6 Agustus **kini punya baris** dan berstatus PENDING menunggu scan gudang, yang memang benar untuk `solution=0`. Jalur susulannya adalah **ingestion `SyncReturns`** yang gate-nya menilai income settled (Decision #1, urutan terbalik) — bukan pemicu escrow. Sensus akhir: TikTok ber-retur ACCEPTED tanpa baris tinggal **1**, dan escrow-nya memang belum cair. ⚠️ Pemicu persisnya belum dipastikan (bisa juga efek restart container); uji sekali lagi pada order TikTok DEFER berikutnya.

**Lima order `RETURNED` ber-faktur SENT tanpa pembalikan — ✅ TERJAWAB, bukan lubang.** Sempat dicurigai sebagai penjualan yang tak pernah terbalik. Diukur: kelimanya (`260713J5X2GM5Q`, `2607217RQW2HPB`, `260715QC755Y4M`, `26073018U2FJBX`, `260714KY4EA1CF`, semua Shopee) punya `return.status = CANCELLED`, **refund Rp0**, settlement **positif** (dibayar penuh), dan **nol scan gudang**. Artinya permintaan returnya dibatalkan, barang tetap di pembeli, uang tetap di kita — **tak ada yang perlu dibalik, pembukuannya sudah benar**. Yang salah hanya **label `order.status`** yang tertulis `RETURNED`; itu mengganggu laporan yang menyaring per status, bukan angka. Barisnya semua `SKIPPED`/acc 0 — konsisten.

### ⚠️ Amandemen 2026-08-07 — DUA mekanisme penyerapan, efek akuntansi BERBEDA (gerbang men-skip kasus yang SALAH)

Seluruh ADR ini berdiri di atas satu premis: "kalau receipt sudah menyerap refund, retur akan jadi pembalikan **dobel**". Premis itu **hanya benar untuk satu dari dua** mekanisme penyerapan, dan keduanya selama ini disamakan.

| Mekanisme | Akun yang dipakai | Efek ke **pendapatan** | Retur akan dobel? |
|---|---|---|---|
| **Potongan Penjualan** (refund SEBAGIAN, `buildReceiptPayload`) | **4003** — kontra-pendapatan | **BERKURANG** | **YA** → gerbang BENAR |
| **Mutasi dompet RR pasca-cair** (`accurate_receipt_wallet_adjustment.go` §2 *Refund pasca-cair*) | 6112/6114 — akun **beban**, plus mengurangi `PaymentAmount` | **TIDAK BERUBAH** | **TIDAK** → gerbang SALAH |

Grounded ke kode: cabang refund pasca-cair menghitung `dana := -r.Tx.Amount + feeBack - shipping`, lalu `di.PaymentAmount -= dana` dan menambahkan diskon hanya ke `acc.Admin` (−feeBack) & `acc.Shipping` (+shipping). **Nol akun kontra-pendapatan.** Mengurangi `PaymentAmount` mencatat **UANG** — piutang fakturnya justru tetap terbuka — bukan membalik **PENDAPATAN**.

Terverifikasi aritmetik pada `2607180VU58AJP`: `198.930 + 32.070 − 47.000 = ` **184.000**, tepat nilai barang di faktur (PJB-003 ×2 @92.000), dan cocok dengan dokumen terposting `INC/2026/07/28/014-BH` (Bayar faktur −184.000 · 6112 −32.070 · 6114 +47.000).

**Konsekuensinya tajam**: amandemen 2026-08-06 membuat gerbang **menuntut bukti mutasi dompet lalu men-SKIP saat bukti itu ada** — yaitu persis kasus di mana skip **tidak** melindungi apa pun. Yang tertinggal: pendapatan tetap diakui dan piutangnya menggantung tanpa ada dokumen yang menutupnya.

**Paparan kecil** (itu yang menyelamatkan): dari 23 order Shopee yang gerbang ini skip, hanya **1** punya mutasi RR. Sensus `shopee_wallet_transactions` tipe RR di seluruh DB juga hanya puluhan dokumen.

**Obat untuk `2607180VU58AJP`** — pendapatan lebih catat Rp184.000, piutang menggantung Rp184.000, sedangkan **stok & kas sudah benar**: satu **Retur Penjualan Rp184.000 mode `NOT_RETURNED`** (refund-only; `return_solution=1`, barang tidak dikirim balik — mode `RETURNED` akan menambah stok 2 unit untuk barang yang tak pernah datang). Berdiri sendiri: **tidak menunggu** keputusan 🟡 di bawah, karena sisi receipt-nya memang tak menyentuh pendapatan. Yang menunggu 🟡 hanya 7 baris karantina kelas Potongan-Penjualan.

⚠️ **Revisi untuk rencana 🟡 di bawah**: butir *"baris wallet-adjustment Shopee berhenti mengurangi bayar-faktur untuk porsi nilai barang"* **jangan diterapkan apa adanya**. Untuk jalur ini justru keliru — kas yang benar-benar keluar tak punya tempat mendarat sehingga receipt tak seimbang. Butir itu ditulis dengan asumsi receipt menyerap **pendapatan**; benar untuk jalur 4003, salah untuk jalur dompet. Yang mengurangi bayar-faktur mencatat **uang**, yang mengurangi pendapatan adalah **retur** — keduanya memang perlu ada berdampingan.

> **Pelajaran umum**: "sudah diserap di tempat lain" bukan satu pernyataan, melainkan pertanyaan **akun mana**. Sebelum memakai keberadaan suatu dokumen sebagai alasan tidak membukukan dokumen lain, telusuri **akun** yang tersentuh — bukan sekadar ada/tidaknya penyerap.

### Amandemen 2026-08-08 — gerbang bertanya ANGKA, bukan ada/tidak (✅ kode, PR #1085 — belum deploy)

Menutup cacat di atas. `returnPayoutGate` tak lagi menerima `func() bool` ("ada penyerap?") melainkan **`func() float64`** — Σ mutasi `ADJUSTMENT_FOR_RR_AFTER_ESCROW_VERIFIED` order itu. Aturannya jadi pertanyaan yang sebenarnya: **setelah ditarik, uangnya masih di kita atau tidak.** `payoutOf(income) + Σpenyesuaian ≤ 0.5` → penjualan memang batal → **BOOK**.

- **Filter gerbang sengaja SEMPIT** (hanya tipe RR), berbeda dari filter TAMPILAN yang memungut ketiga tipe: `LOST_PARCEL_SELLER_ADD` & `AFFILIATE_SAMPLE_SHIPPING_FEE_DEDUCT` memindahkan uang tapi **tidak membatalkan penjualan**, jadi keberadaannya tak boleh ikut menentukan perlu-tidaknya retur. Dua pertanyaan berbeda → dua filter berbeda, dikunci tes.
- **Cabang "penarikan ADA tapi kas akhir masih positif" DIPERTAHANKAN apa adanya** (tetap SKIP seperti PR #1038). Kelas itu **nol kejadian** di prod — 13 dari 13 order ber-mutasi RR kas akhirnya ≤ 0 — jadi mengubahnya berarti menebak tanpa data.
- **Jejak SKIP tak lagi disemai untuk retur yang belum/tak disetujui.** Gerbang ACCEPTED (`resolveReturnMode`) berada **setelah** gerbang payout, sehingga permintaan yang dibatalkan ikut dapat baris — melahirkan "retur hantu". Terlihat pada `2607180VU58AJP`: retur `2607240H2Y0WVEK` berstatus CANCELLED tetap berbaris, berdampingan dengan yang ACCEPTED.

**Paparan terukur sebelum menulis kode** — 0 order punya refund-SEBAGIAN **dan** mutasi dompet sekaligus (jadi nol risiko pembalikan dobel); 36 order ber-mutasi RR; 13 akan mulai terbukukan; **12 tertahan benar oleh cutover hari-kirim** (2 kirim Juni, 10 tanpa `shipped_at` sehingga tak pernah masuk faktur) → **dampak nyata 1 order**.

⚠️ **Residu dua-basis — ✅ DITUTUP PR #1098 (belum deploy).** Nilai retur memakai **harga faktur** (`2607180VU58AJP` = 2 × 99.000 = Rp198.000), sedangkan `dana` di wallet-adjustment memakai **angka dompet** (Rp184.000). Dua langkah pada faktur yang sama dengan dua basis berbeda → faktur dilunasi lebih besar daripada yang dibatalkan, dan piutang serta pendapatan berakhir **−Rp14.000** (Σ populasi 15 order = −Rp9.000).

> **Yang membuatnya layak diperbaiki bukan nominalnya, melainkan identitas `faktur = income + retur`.** Identitas itu alat ukur yang dipakai memeriksa kebenaran pembukuan; kalau ia sendiri boleh meleset, setiap selisih di kemudian hari tak bisa lagi dibedakan antara error sungguhan dan residu yang "memang biasa". Nominal kecil bukan alasan membiarkan invariant bocor.

Pembatalan kini memakai `basePorsi` (harga faktur) dan selisih basis pulang lewat akun **potongan penjualan 4003** — cermin potongan yang receipt PEMBAYARAN bukukan, sehingga net kedua receipt nol. **Kas tak berubah sepeser pun** (tetap −Rp198.930); yang berubah hanya pemecahannya. Basis diambil dari `lookupSentShopeeInvoice` (yang sudah dipakai jalur kompensasi, mengembalikan `priceMap` ber-cache) — lookup lama hanya memberi nomor faktur sehingga basisnya tak pernah bisa diketahui. Basis tak ter-resolve → mundur ke perilaku lama. ⚠️ **Berlaku go-forward**: receipt yang sudah terposting tak berubah sendiri.

⚠️ **Perbaikan ini sempat INERT — diblokir bug hulu (ditemukan saat verifikasi deploy, ditutup PR #1096).** Gerbang barunya memang memutuskan BOOK untuk `2607180VU58AJP` (kas akhir −49.042), tapi `resolveReturnMode` sesudahnya menolak karena sub-dokumen `order.return` ternyata memuat record yang **CANCELLED**: satu order punya beberapa record retur sementara sub-dokumennya cuma satu slot, dan `SetOrderReturn` menulis tanpa syarat sehingga yang disinkron terakhir menang (ACCEPTED 06:00:08 → CANCELLED 06:00:09). **Pelajaran**: memperbaiki gerbang tak ada gunanya bila data yang dibacanya salah orang — verifikasi pasca-deploy harus menelusuri sampai hasil akhirnya, bukan berhenti di "kode sudah benar". Detail di [[Microservices - Integration Service]].

📌 **Belum dikerjakan**: menyembunyikan baris jejak `SKIPPED` saat ordernya sudah punya baris hidup. Menyaring setelah paginasi merusak ukuran halaman; menandai baris saat booking adalah perubahan tulis tersendiri. Sesudah PR ini `2607180VU58AJP` tampil **2 baris** (1 jejak + 1 retur nyata), bukan 3.

### 🟡 Keputusan bisnis 2026-08-05 — nilai barang SELALU via retur (BELUM diimplementasi)

**Status: 🟡 Diputuskan, belum ada di kode.** Gerbang payout masih aktif di produksi per 2026-08-06.

Pemilik memutuskan menghapus asimetri kanal: **nilai barang selalu dibalik Retur Penjualan untuk SEMUA kanal**, sedangkan **komisi/fee/ongkir/kompensasi tetap di jalur income**. Dua peristiwa diperlakukan **independen**: (1) penjualan batal → retur membalik nilai faktur + stok, tak peduli siapa menanggung; (2) pergerakan uang → jalur income/kas. Konsekuensi praktis: kasus "marketplace TIDAK memotong refund dari kita" jadi **decidable** — retur tetap dibukukan, dan uang yang kita pegang muncul sebagai pendapatan lain-lain/kompensasi. Akun other-income **sudah ada & dipakai** (`resolvedCompFallback`), jadi tak ada akun baru yang perlu diputuskan finance.

Alasan: aturan lama (Shopee→receipt, TikTok→retur) bukan prinsip akuntansi melainkan kebetulan teknis (ada/tidaknya penyerap), dan efeknya nyata — laporan retur **understate** Shopee, dan **stok Shopee barang-balik tak pernah bertambah** karena receipt tak menggerakkan stok.

**Dua tempat WAJIB berubah bersamaan** (kalau tidak → dobel seketika): (a) baris wallet-adjustment Shopee berhenti mengurangi bayar-faktur untuk porsi **nilai barang**; (b) `buildReceiptPayload` — refund tak lagi jatuh ke akun discount (`loadReceiptAccounts`: *"Refund tidak punya akun sendiri — digabung ke discount"*), melainkan mengurangi `basePorsi` order, sehingga piutang sisa dilunasi retur.

**Paparan terukur 2026-08-06** (dasar prioritas). Angka pertama yang dipakai — *1.274 dari 1.645 retur SENT (77%) punya ≥1 order ber-`TotalRefund` ≠ 0, ±Rp197 jt* — **DICABUT: kriterianya salah.** `TotalRefund ≠ 0` memungut **seluruh** order ber-refund, padahal refund **penuh** terbukti tidak pernah dobel (lihat paragraf berikut). Kondisi dobel yang sebenarnya = refund **SEBAGIAN**: `TotalRefund ≠ 0` **DAN** `total_settlement_amount > 0`, yaitu order yang receipt-nya tetap terbit sambil membawa baris potongan. Disensus ulang dengan kriteria itu: **1 order**, bukan 1.274 dokumen. Sisi sebaliknya jauh lebih besar dan arahnya **berlawanan** — **38 baris SKIPPED** yang nilai barangnya **tak pernah** dibalik sama sekali. Jadi paparan nyata gerbang ini adalah **KURANG catat**, bukan dobel.

✅ **Batas pengetahuan itu kini tertutup.** Refund **penuh** terbukti tidak dobel — `buildReceiptPayload` men-**skip** faktur ber-payment 0 (`accurate_receipt_usecase.go` ~488: *"koreksi pendapatan order refund lewat retur faktur"*), diverifikasi ke dokumen terposting `INC/2026/07/14/015-KY+GB`: potongannya murni akun beban 6112/6113/6114, faktur order refund penuh **tak ada** di receipt. Refund **sebagian** — yang dulu ditulis "belum diverifikasi" — sudah disensus di atas: **1 order**. Yang ikut terbukti dari dokumen terposting yang sama: **receipt tak pernah membaca nilai Retur Penjualan**; potongannya lahir dari akun beban, bukan dari dokumen retur. Konsekuensinya penting untuk pekerjaan koreksi data — **membetulkan nilai retur TIDAK menuntut koreksi tandingan di sisi income**; lihat [[ADR - 0040 Retur Paket Utuh via Baris Induk Faktur]] §Consequences.

### Amandemen 2026-08-12 — fallback tanggal: hari-kirim DIBUANG → `returned_at` lalu tanggal deteksi (✅ kode, PR bip-erp#1161 + erp-frontend#977 — belum deploy)

Jaring TERAKHIR `resolveReturnTransDate` dulu **hari-kirim** (`shipped`, `date_wib`) — itu tanggal kirim **KE PEMBELI**, bukan tanggal retur. Di UI ia tampil identik dengan kolom "Hari kirim" (menyesatkan), dan badge "cek tanggal" menyala untuknya.

**Keputusan**: buang `shipped` dari prioritas. Urutan baru: `cancelled_at` → TikTok `order_update_date` → Shopee per-solution (refund `requested_at` / arrival) → `accepted` → `requested` → **`order_returned`** (`order.returned_at` — timestamp ORDER saat jadi RETURNED; tetap ada walau sub-dokumen retur tak ter-ingest) → **`detected`**. Jaring terakhir: resolver mentah balik `(zero, "detected")`, lalu `resolveReturnTransDateOrNow(order, dateWIB, now)` mengisinya dengan **waktu deteksi** (`now`) supaya `trans_date` tetap terisi (filter Tanggal Retur FE menyaring lewat field itu — amandemen 2026-08-05); di-persist sekali → stabil (rebuild memakai nilai tersimpan). Untuk barang-balik, `detected` **sementara** — ditimpa tanggal scan gudang (`warehouse`) saat dikonfirmasi ([[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]]).

**Penanda perkiraan** (Keterangan Accurate + badge amber "cek tanggal", `hasApproxDate`) kini menyala untuk `date_source = detected` (dulu `shipped`); `shipped` masih ada di baris LAMA sehingga tetap ditandai. Sumber sah lain (`accepted`/`requested`/`arrival`/`cancelled`/`order_updated`/`order_returned`/`warehouse`) tak ditandai.

**FE** (erp-frontend#977): asal tanggal kini **DITAMPILKAN** sebagai keterangan ringkas di tabel & modal (mis. "tgl retur disetujui", "tgl barang discan gudang", "perkiraan (tgl dicatat)") — sebelumnya hanya tooltip; tipe `date_source` dilengkapi semua nilai backend.

**Ops tools** (`returnfix`/`returnrebuild`/`returnredate`) aman — sudah ber-guard `IsZero()`: order tanpa timestamp apa pun kini balik ZERO → di-skip konservatif (tak lagi ter-redate/rebuild ke hari-kirim).

Grounded: `resolveReturnTransDate`/`resolveReturnTransDateOrNow` (`accurate_rts_usecase.go`), tes `accurate_return_date_test.go` (`TestResolveReturnTransDate_ReturnedAtLaluDetected`).

### Amandemen 2026-08-26 — kompensasi paket hilang juga penyerap (✅ deployed, PR #1451)

Sejak [[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]], **penyesuaian statement TikTok** (97% ganti rugi PAKET HILANG) dibukukan sebagai penambah payout pesanan → receipt melunasi fakturnya. Begitu itu terjadi, membukukan Retur Penjualan di atasnya = **pembalikan dobel**: pendapatan terbalik dua kali, piutang ter-kredit minus.

Jalur cancel gerbang ini justru yang paling terpapar: ia mengembalikan `book` **tanpa bertanya apa pun**, sementara **254 dari 263** pesanan penerima kompensasi berstatus `CANCELLED` (terukur prod 2026-08-26). Artinya membayar fakturnya *membuka* lubang dobel yang sebelumnya tertutup hanya karena uangnya tak pernah dibukukan.

**Keputusan**: `diserapPenyesuaianStatement` diperiksa **paling dulu**, sebelum cabang cancel. Prinsipnya sama dengan cabang Shopee di amandemen 2026-08-08 — pertanyaannya bukan *"ada penyerap?"* melainkan **ANGKA**: `payoutOf(income) + Σpenyesuaian > 0.5` berarti uangnya masih di kita, jadi penjualannya **TIDAK batal** → `SKIP` (baris `SKIPPED`, Auto Sync Income yang urus).

Batasnya sengaja sempit, dan tiga-tiganya mengikat:
- hanya kanal **TikTok** (penyesuaian statement tak ada di kanal lain);
- hanya **hari-kirim ≥ `autoSyncCutoverDateWIB`** — receipt tak membukukan order pra-cutover, jadi di sana **tak ada** yang menyerap dan retur TETAP harus dibukukan (syarat yang sama sudah berlaku untuk cabang payout>0);
- **lookup MALAS** — `SumByOrder` hanya dipanggil setelah dua syarat di atas terpenuhi, karena ia query DB per-order di jalur terpanas.

Repo belum tersuntik (`cmd` one-off, tes lama) → dianggap tak ada kompensasi → **BOOK**, arah yang sama dengan `shopeeRefundAdjustment`: salah-book terlihat sebagai dokumen yang bisa dihapus, salah-skip hilang tanpa jejak.

⚠️ **Keterbatasan yang disadari**: **19 dari 263** pesanan berkompensasi ternyata barangnya TETAP kembali ke gudang. Untuk mereka skip berarti stok tak bertambah padahal barangnya nyata ada. Gerbang tak bisa tahu — scan gudang terjadi jauh setelah keputusan ini diambil, jadi hasilnya sengaja berupa baris `SKIPPED` yang **terlihat** di UI (bukan diam) supaya kelas 7% itu dapat mata finance. Berlaku **maju**; 208 baris `PENDING` yang sudah terlanjur ada tidak tersentuh.

Grounded: `returnPayoutGate`/`diserapPenyesuaianStatement`/`tiktokStatementAdjustment` (`accurate_rts_usecase.go`), `tiktokStatementAdjustmentRepo.SumByOrder` (`tiktok_statement_adjustment_repo.go`), tes `accurate_receipt_penyesuaian_test.go` (`TestGerbangRetur*`).

## Dokumen Terkait
- [[Microservices - Integration Service]] — Auto-Sync Retur (gerbang payout, tanggal per-solution) & Auto Sync Income (receipt)
- [[ADR - 0056 Penyesuaian Statement TikTok Menambah Payout Order]] — kompensasi paket hilang yang kini ikut menyerap (amandemen 2026-08-26)
- [[ADR - 0040 Retur Paket Utuh via Baris Induk Faktur]] — pembentukan baris & harga retur paket (tak mengubah gerbang ini)
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] — gerbang gudang; jalur konfirmasinya sempat bisa menghidupkan baris `SKIPPED` jadi pembukuan dobel (amandemen 2026-08-05)
- [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] — keputusan #1 digantikan; #2 tetap
- [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]]
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]]
- [[ADR - 0017 Tanggal Retur TikTok via order_update_date]]

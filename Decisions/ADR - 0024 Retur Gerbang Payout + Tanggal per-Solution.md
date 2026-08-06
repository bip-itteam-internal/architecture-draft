✅ **Implemented & Deployed** (2026-07-18/19: gerbang payout + tanggal per-solution + pemicu settlement + **cutover retur ikut faktur/hari-kirim** + gate cutover-fix; deploy 2026-07-19; cleanup data existing **SELESAI** — descope 1565 retur < 1 Jul, void 1 dobel). **Amandemen 2026-08-05 (✅ DEPLOYED 2026-08-05, commit `779b0a06`; verifikasi prod: 38 baris jejak tersemai, dari 1):** janji "SKIP → baris `SKIPPED`" di Decision #1 akhirnya benar-benar dipenuhi — sebelumnya baris hanya ditandai bila kebetulan sudah ada, sehingga mayoritas retur payout>0 **tak berjejak sama sekali** di UI; sekaligus menutup lubang dobel-booking lewat konfirmasi gudang yang baru terlihat setelah baris jejak itu ada. Lihat Consequences.

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

**2. Tanggal retur per-solution (Shopee).** `resolveReturnTransDate`: CANCELLED→`cancelled_at`; **TikTok**→`order_update_date` (tetap, [[ADR - 0017 Tanggal Retur TikTok via order_update_date]]); **Shopee refund-only** (`solution=1`)→`requested_at` (`create_time`, anti-drift); **Shopee barang-balik** (`solution=0`) + `return_tracking.status==RECEIVED` + `last_event_at`→**arrival**; fallback `updated_at`→`requested_at`→`shipped`. Memakai sub-doc `return_tracking` yang **sudah** diisi cron reverse-tracking — **bukan** menghidupkan `arrivalResolver` lama yang dicabut ADR-0023.

**3. Cutover retur = HARI KIRIM (ikut faktur), bukan tanggal-retur** (2026-07-19). Gate cutover di `SyncOrderReturn`/`RetryDailyReturn`/`RecordReturnFetchFailure` menilai `dateWIB` (hari-kirim = tanggal faktur sumber) ≥ `autoSyncReturnCutoverDateWIB` "20260701" — BUKAN tanggal retur. Alasan: retur harus mengikuti era faktur & income sumbernya. Order kirim < 1 Jul = era **manual finance** (faktur IMPORTED/tak-ada, income di-skip receipt) → returnya JUGA manual, tak auto. Basis tanggal-retur lama menarik retur order-lama (kirim Mei/Juni, faktur manual) ke auto → retur auto membalik pembukuan manual (tak konsisten + dobel). Menggantikan basis retur di [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] #2 (struktur split 2-konstanta tetap; basis retur berubah).

## Consequences

- **Dobel mustahil by-design**: payout>0 & payout≈0 saling eksklusif — Receipt ATAU Retur, tak pernah keduanya.
- **Income/Auto Sync Income sync TIDAK diubah** — ia sudah benar (menyerap refund payout>0, defer payout≈0 ke retur). Perbaikan 100% di sisi retur.
- **Tanggal benar go-forward**: refund-only pakai tanggal ajukan (stabil), barang-balik pakai tanggal fisik sampai gudang.
- **Menggantikan**: ADR-0023 **keputusan #1** (accepted-seragam) — premisnya salah; ADR-0023 **keputusan #2** — struktur split tetap, **basis cutover retur diubah** (tanggal-retur → hari-kirim, lihat Decision #3). Juga menutup premis "refund-only selalu jadi retur" di [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]] / [[ADR - 0012 Retur Refund-only Push-all]].
- **Cleanup data existing (✅ SELESAI 2026-07-19)**: `cmd/returndescope` mengeluarkan **1565 retur hari-kirim < 1 Jul** dari auto (**1007 dok Retur Penjualan dihapus dari Accurate** via `delete.do`, semua ditandai `SKIPPED`); **1 dobel post-cutover** `RTR/2026/07/16/006-BH` (payout>0 + receipt) di-void. Era kept ≥ 1 Jul: 615 SENT sah + 8 FAILED (SKU era-baru, ditunda).
- **Edge butuh finance**: barang-balik `solution=0` **payout>0** (~48, ~1–2 SENT) — receipt urus revenue, tapi **stok tak balik** (Accurate under-stock). Konservatif (stok-opname backstop), idealnya retur-stok-saja — **ditahan untuk finance**.

### Amandemen 2026-08-05 — keputusan SKIP wajib berjejak (un-deployed)

**Masalah**: Decision #1 menuliskan "SKIP (baris `SKIPPED`)", tapi implementasinya hanya menandai baris yang **kebetulan sudah ada**; bila belum ada, keputusan itu cuma masuk log. Akibatnya retur payout>0 **lenyap total** dari halaman Auto-Sync Retur dan finance tak punya cara tahu pembalikannya ada di dokumen lain. Terukur prod 2026-08-04 pada order Shopee `2607180VU58AJP`: refund pasca-cair **Rp198.930** nyata terbukukan di receipt `INC/2026/07/28/014-BH` (diverifikasi ke Accurate: Bayar faktur −184.000, akun 6112 −32.070, akun 6114 +47.000 = net −198.930), tapi nol jejak di UI retur.

**Keputusan**: `SyncOrderReturn` cabang skip kini **membuat** baris jejak (`seedSkippedReturnRow`) bila belum ada. Baris ini **bukan antrean kerja** — tak ada dokumen Accurate yang lahir darinya — sehingga: dedupe **per-retur (`return_sn`)**, bukan group-key `<faktur>|<tanggal>`; `attempts` tetap 0; `trans_date` **wajib** diisi (filter tanggal FE menyaring lewat field itu — jejak yang tak bisa ditemukan sama saja dengan tak ada). Baris SENT tak pernah diturunkan. **DEFER tetap tanpa baris**: payout belum diketahui, keputusannya belum final, mencatatnya hanya menghasilkan baris yang berubah-ubah sendiri.

**Lubang yang ikut ditutup — dobel-booking lewat scan gudang.** Justru keberadaan baris jejak membukanya: kunci yang dipegang gudang (`return_sn`) seformat `dedupe_key` baris non-grup, sehingga **cadangan pencarian by-key** di `ConfirmReturnFromWarehouse` memungutnya, lalu `rebuildAndSendGroup` — yang **tak punya gerbang payout sendiri** — mengirim Retur Penjualan ke Accurate. Terbukti lewat tes regresi: 1 dokumen terbukukan sebelum diperbaiki, tepat pembalikan dobel yang ADR ini ada untuk mencegah. Lookup utama (`GetByMemberOrderIDAny`) sudah mengabaikan `SKIPPED`; cadangannya yang melewatkan — kini disamakan. Efek sampingnya menutup lubang yang **sudah ada sebelumnya**: baris `SKIPPED` **pra-cutover** pun tadinya bisa dibukukan lewat scan gudang, melanggar cutover Decision #3.

**Konsekuensi**: baris "DILEWATI" kelas ini kini muncul di UI untuk SEMUA channel, termasuk edge `solution=0` payout>0 di atas — justru bagus, finance akhirnya melihatnya. Baris tetap **inert** bagi seluruh proses terjadwal (sweep rekonsiliasi, laporan summary, anomaly check, unmapped-SKU semuanya memfilter SENT/FAILED/PENDING). **Batas yang disadari**: bila payout suatu order suatu saat berbalik ke ≈0 setelah jejaknya dibuat, jalur booking memakai group-key sehingga lahir baris kedua dan jejak lama tertinggal dengan keterangan basi — sangat jarang (penyesuaian wallet tak mengubah `total_settlement_amount`) dan tak menimbulkan kesalahan angka, jadi tak dibuatkan mesin khusus.

### Amandemen 2026-08-05 — gerbang menuntut BUKTI penyerapan (✅ deployed, PR #995 `4bb89eb2`)

Decision #1 memakai `payout > 0` sebagai proksi "receipt sudah menyerap refund". Proksi itu **tak berlaku untuk TikTok**: penyerap yang dimaksud (`ADJUSTMENT_FOR_RR_AFTER_ESCROW_VERIFIED` di `accurate_receipt_wallet_adjustment.go`) **Shopee-only**, dan `tt_shop_transaction_by_orders` menyimpan **1 dokumen per order** (upsert by `order_id`) sehingga clawback pasca-settle tak bisa hidup berdampingan dengan record aslinya. Terukur prod 2026-08-05 pada 38 baris jejak: ke-11 order TikTok yang kena gate masih bersettlement **positif**, nol clawback terlihat; sisi Shopee pun tipis (`shopee_wallet_transactions` tipe RR cuma **35 dokumen total**, dan dari 27 baris gate hanya **2** yang punya).

**Keputusan**: `returnPayoutGate` kini SKIP hanya bila ada bukti penyerapan — kanal **Shopee** (penyerap wallet-adjustment memang ada) **ATAU** `income.TotalRefund != 0` (refund sudah ternetto di settlement). Dipakai `!= 0` karena **tandanya berbeda antar kanal**: TikTok positif (negasi `refund_subtotal`), Shopee negatif (`seller_return_refund + drc_adjustable_refund`). Diuji terhadap 11 order TikTok: 6 flip→book, 2 tetap skip (refund memang ternetto), 3 sudah book sendiri — payout jadi **negatif** setelah TikTok meng-upsert record settlement order yang sama, jadi TikTok **bisa** claw back lewat penimpaan dokumen, bukan dokumen baru.

**Konsekuensi**: 5 dari 6 yang flip bersolution 0 → tertahan **PENDING** gerbang gudang, bukan langsung terbukukan. Ini benar per [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]].

### Amandemen 2026-08-06 — cabang Shopee menuntut BUKTI, bukan kanal (✅ commit `03739530`, belum deploy)

Amandemen di atas masih memakai **kanal** sebagai proksi: "Shopee → pasti ada penyerap". Proksi itu **terlalu lebar**. Penyerapnya satu hal yang sangat spesifik — mutasi dompet `ADJUSTMENT_FOR_RR_AFTER_ESCROW_VERIFIED` — dan mayoritas order Shopee ber-`payout>0` **tidak punya**. Sensus prod 2026-08-06 atas **23 order Shopee** yang gerbang ini skip: hanya **1** punya mutasi RR (`2607180VU58AJP`, −198.930, terverifikasi ke `INC/2026/07/28/014-BH`); **22 sisanya nol penyerap** dan `total_refund` 0 — penjualannya tak pernah terbalik dokumen apa pun, dan **stok barang-baliknya juga tak pernah bertambah** karena receipt tak menggerakkan stok. Menebak dari kanal = menghilangkan 22 pembalikan sah demi melindungi 1.

**Keputusan**: cabang Shopee kini **bertanya** — `HasShopeeRefundAdjustment(orderSN)` pada `shopee_wallet_transactions` (tipe RR, status `COMPLETED`). Hanya tipe RR; `LOST_PARCEL_SELLER_ADD` & `AFFILIATE_SAMPLE_SHIPPING_FEE_DEDUCT` bukan pembalikan penjualan sehingga tak boleh membatalkan retur.

Rinciannya:
- **Lookup MALAS** — dipanggil hanya saat Shopee + settled + `payout>0` + post-cutover + `TotalRefund == 0`. `SyncOrderReturn` jalur panas; menanyakannya di luar kondisi itu = query DB sia-sia. Dua kasus tes mengunci bahwa jalur lain tak menyentuhnya sama sekali.
- **Gagal baca / repo nil → BOOK**, bukan skip. Salah-book masih bisa dihapus (`sales-return/delete.do`); salah-skip menghilangkan pembalikan tanpa jejak. Arah kesalahan yang bisa diperbaiki dipilih sadar.
- **Interface lokal `ReturnAbsorberRepo`** (1 method) + `NewReturnAbsorberRepo()` — interface Go struktural, jadi `repository.WalletRepository` dan seluruh fake-nya tak ikut berubah. Disuntik pasca-konstruksi (`SetWalletAbsorberRepo`) mengikuti pola `SetReturnBooker`.
- **Pra-saring** di `triggerReturnAfterSettlement` & diagnostik `accurate_why` memakai `nil` (keduanya tanpa ctx/repo). Aman: gerbang yang mengikat tetap yang di `SyncOrderReturn`, jadi pra-saring longgar hanya menghasilkan satu panggilan yang berujung skip — bukan dobel. Diagnostik `accurate_why` jadi **meremehkan** penyerapan; itu arah yang benar untuk alat diagnosa.

**Menunggu**: backfill **31 baris SKIPPED yang aman** (refund penuh / tanpa refund, Σ nilai barang ±Rp4.054.500 — TikTok 9, Shopee 22; 14 bersolution 0 akan tertahan gerbang gudang, 17 langsung terbukukan). **7 baris dikarantina** karena refund SEBAGIAN (receipt sudah menyerap lewat potongan penjualan) — baru boleh dibukukan setelah keputusan 🟡 di bawah diimplementasi.

### 🟡 Keputusan bisnis 2026-08-05 — nilai barang SELALU via retur (BELUM diimplementasi)

**Status: 🟡 Diputuskan, belum ada di kode.** Gerbang payout masih aktif di produksi per 2026-08-06.

Pemilik memutuskan menghapus asimetri kanal: **nilai barang selalu dibalik Retur Penjualan untuk SEMUA kanal**, sedangkan **komisi/fee/ongkir/kompensasi tetap di jalur income**. Dua peristiwa diperlakukan **independen**: (1) penjualan batal → retur membalik nilai faktur + stok, tak peduli siapa menanggung; (2) pergerakan uang → jalur income/kas. Konsekuensi praktis: kasus "marketplace TIDAK memotong refund dari kita" jadi **decidable** — retur tetap dibukukan, dan uang yang kita pegang muncul sebagai pendapatan lain-lain/kompensasi. Akun other-income **sudah ada & dipakai** (`resolvedCompFallback`), jadi tak ada akun baru yang perlu diputuskan finance.

Alasan: aturan lama (Shopee→receipt, TikTok→retur) bukan prinsip akuntansi melainkan kebetulan teknis (ada/tidaknya penyerap), dan efeknya nyata — laporan retur **understate** Shopee, dan **stok Shopee barang-balik tak pernah bertambah** karena receipt tak menggerakkan stok.

**Dua tempat WAJIB berubah bersamaan** (kalau tidak → dobel seketika): (a) baris wallet-adjustment Shopee berhenti mengurangi bayar-faktur untuk porsi **nilai barang**; (b) `buildReceiptPayload` — refund tak lagi jatuh ke akun discount (`loadReceiptAccounts`: *"Refund tidak punya akun sendiri — digabung ke discount"*), melainkan mengurangi `basePorsi` order, sehingga piutang sisa dilunasi retur.

**Paparan terukur 2026-08-06** (dasar prioritas): dari **1.645** retur SENT sejak 1 Juli, **1.274 (77%)** punya ≥1 order ber-`TotalRefund` ≠ 0. Sisi sebaliknya: **38 baris SKIPPED** = nilai barang **tak pernah** dibalik sama sekali. ⚠️ Nilai Rp197 jt pada 1.274 dokumen itu **total nilai dokumennya, BUKAN jumlah yang dobel** — satu dokumen grup memuat banyak order.

⚠️ **Batas pengetahuan**: refund **penuh** terbukti **tidak** dobel — `buildReceiptPayload` men-**skip** faktur ber-payment 0 (`accurate_receipt_usecase.go` ~488: *"koreksi pendapatan order refund lewat retur faktur"*), diverifikasi ke dokumen terposting `INC/2026/07/14/015-KY+GB`: potongannya murni akun beban 6112/6113/6114, faktur order refund penuh **tak ada** di receipt. Yang **belum** diverifikasi = refund **sebagian** (payout > 0), yaitu justru kasus yang gerbang ini jaga.

## Dokumen Terkait
- [[Microservices - Integration Service]] — Auto-Sync Retur (gerbang payout, tanggal per-solution) & Auto Sync Income (receipt)
- [[ADR - 0040 Retur Paket Utuh via Baris Induk Faktur]] — pembentukan baris & harga retur paket (tak mengubah gerbang ini)
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] — gerbang gudang; jalur konfirmasinya sempat bisa menghidupkan baris `SKIPPED` jadi pembukuan dobel (amandemen 2026-08-05)
- [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] — keputusan #1 digantikan; #2 tetap
- [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]]
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]]
- [[ADR - 0017 Tanggal Retur TikTok via order_update_date]]

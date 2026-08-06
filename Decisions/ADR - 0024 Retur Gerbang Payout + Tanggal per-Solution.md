✅ **Implemented & Deployed** (2026-07-18/19: gerbang payout + tanggal per-solution + pemicu settlement + **cutover retur ikut faktur/hari-kirim** + gate cutover-fix; deploy 2026-07-19; cleanup data existing **SELESAI** — descope 1565 retur < 1 Jul, void 1 dobel). **Amandemen 2026-08-05 (belum deploy):** janji "SKIP → baris `SKIPPED`" di Decision #1 akhirnya benar-benar dipenuhi — sebelumnya baris hanya ditandai bila kebetulan sudah ada, sehingga mayoritas retur payout>0 **tak berjejak sama sekali** di UI; sekaligus menutup lubang dobel-booking lewat konfirmasi gudang yang baru terlihat setelah baris jejak itu ada. Lihat Consequences.

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

## Dokumen Terkait
- [[Microservices - Integration Service]] — Auto-Sync Retur (gerbang payout, tanggal per-solution) & Auto Sync Income (receipt)
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] — gerbang gudang; jalur konfirmasinya sempat bisa menghidupkan baris `SKIPPED` jadi pembukuan dobel (amandemen 2026-08-05)
- [[ADR - 0023 Retur Tanggal Accepted-Seragam + Cutover Terpisah]] — keputusan #1 digantikan; #2 tetap
- [[ADR - 0022 Retur via Sales Return per Mode + Keep Invoice Line]]
- [[ADR - 0018 Faktur Permanen - Semua Pembalikan via Retur]]
- [[ADR - 0017 Tanggal Retur TikTok via order_update_date]]

# Sales to System — Sampel, Summary Otomatis, Export Multiple

Tanggal: 2026-07-13 · Status: disetujui user · Sumber: dokumen finance "Sales to System.docx" (+7 screenshot)

Konteks: fitur auto-sync faktur Accurate sudah live (trigger SHIPPED, 1 faktur/toko/hari WIB,
non-pajak, Departemen/Proyek per brand, keterangan "Dikirim <tanggal>"). Dokumen finance
meminta 3 hal lanjutan. Requirement pajak/keterangan/dept-proyek SUDAH terpenuhi (PR #361,
#371, #372/#373) — di luar spec ini.

## Scope 1 — Order sampel dikecualikan dari faktur, masuk Penyesuaian Persediaan

**Deteksi (diverifikasi ke data & API):**
- TikTok: field resmi `is_sample_order` di order detail API — sudah tersimpan di
  `tt_shop_order_details` (390 order historis). Ini SATU-SATUNYA sumber deteksi; tidak pakai
  heuristik harga-0.
- Shopee: tidak punya program sampel (0 order berpola sampel dalam 30 hari) — di luar scope.

**Perubahan data:**
- Field baru `transaction_orders.is_sample` (bool, bson omitempty). Rantai LENGKAP tiga titik
  (pelajaran PR #372/#373 — field di entity saja = data terbuang): DTO client TikTok →
  entity raw `tt_shop_order_details` (sudah ada `is_sample_order`) → mapping transform →
  `transaction_orders.is_sample`. Berlaku di jalur cron sync DAN webhook direct.
- Backfill 390 order lama via script join `tt_shop_order_details._id = order_id` (manual, sekali).

**Keluar dari faktur:**
- Filter level query: field baru `TransactionOrderFilter.ExcludeSample` — dipasang di SEMUA
  call site snapshot faktur (OnOrderToShip, RetryDailyInvoice, SweepDailyInvoice/
  snapshotUnchanged, GetDailyInvoiceDetail, jalur correction). Satu titik terlewat = hash
  sender vs sweep berbeda → edit ulang tiap malam. Baris sampel (harga 0) hilang dari faktur;
  total faktur tak berubah.

**Masuk Penyesuaian Persediaan (diverifikasi live ke API Accurate):**
- 1 dokumen per (toko, hari kirim WIB) via `item-adjustment/save.do`; baris per item:
  `{itemNo (via resolver accurate_products), quantity, itemAdjustmentType: ADJUSTMENT_OUT,
  warehouseName (dari config toko)}`. Keterangan: `Sample Tiktok <nama toko>` + transDate =
  hari kirim — meniru persis dokumen manual finance (mis. IA.26.07.00008).
- `adjustmentAccountNo` TIDAK dikirim → Accurate memakai default preferensi (perilaku yang
  sama dengan input manual finance). Tidak ada config akun baru di ERP.
- `unitCost` wajib di schema tapi berdeskripsi "hanya untuk penambahan"; untuk ADJUSTMENT_OUT
  kirim 0 — verifikasi saat implement, fallback omit.
- Ketahanan meniru faktur: koleksi `accurate_daily_adjustments` (nomor stabil per toko-hari,
  `accurate_id`, last_status SENT/FAILED/PENDING, lines_hash, lock, attempts), edit protokol
  resmi (header `id` + baris lama `_status:"delete"` + snapshot baru), retry 3×, notif
  Telegram, skip-unchanged (hash lokal). Model dokumen = SNAPSHOT (semua order sampel
  shipped toko-hari itu, dibangun ulang tiap sync — sampel yang batal otomatis keluar),
  bukan append. Trigger: hook SHIPPED/COMPLETED existing — order `is_sample` memicu sync
  adjustment; sync faktur tetap jalan (no-op karena sampel tak pernah masuk snapshot faktur).
- Monitoring: seksi terpisah "Penyesuaian Sampel" di tab Auto Sync FE (tabel sendiri di bawah
  tabel faktur: tanggal, toko, nomor IA, status, lines, error, tombol Retry) — endpoint
  list/retry paralel dgn daily-invoices (`/accurate/daily-adjustments`).

**Backfill era fitur:** setelah deploy, faktur 10 Jul–sekarang di-retry (baris sampel keluar)
dan dokumen penyesuaian dibuat untuk hari-hari tsb. Hari sebelum 10 Jul tidak disentuh
(era manual — finance sudah input, mis. IA.26.07.00004–00011).

## Scope 2 — Summary otomatis harian (raw file)

- Worker harian 22:30 WIB (setelah sweep faktur 22:00): buat `transaction_summary_reports`
  per (toko, hari) dari order auto-sync hari itu, `report_type: SALES_INVOICE`, status baru
  `AUTO`.
- Status `AUTO`: TIDAK pernah dikirim ke Accurate — endpoint `send/:service` menolak,
  tombol send disembunyikan di FE. 409-guard manual-send tidak berubah (tetap membandingkan
  ke `accurate_daily_invoices`, bukan summary).
- KRITIS anti-bentrok: summary AUTO **tidak menstempel** order (`BatchUpdateReportID`
  TIDAK dipanggil) — stempel `sales_invoice_report_id` tetap milik alur manual. Raw export
  untuk report AUTO mengambil order via query (shop_id, channel, hari-kirim WIB), bukan via
  stempel. Idempoten: unique index parsial (shop_id, channel, date, status AUTO) — worker
  rerun tidak menggandakan.
- Halaman Summary existing menampilkannya → download Raw File existing
  (`GET /summary/reports/:id/orders/export`) langsung jalan (bercabang by status AUTO).
  Kolom "Accurate Number" diisi `accurate_daily_invoices.invoice_number` via join
  (shop_id, channel, hari-kirim WIB).
- Order sampel TETAP tampil di raw file (finance perlu lihat), kolom Accurate Number kosong
  (tidak pernah difakturkan); kolom nomor penyesuaian menyusul bila diminta — YAGNI.

## Scope 3 — Export multiple (sheet per toko)

- Endpoint baru `GET /transactions/summary/reports/orders/export-multiple`
  (param `date_from`, `date_to`, `shop_ids` csv, `channel`) → satu file Excel:
  1 sheet per toko (nama sheet = nama toko, format kolom raw existing per channel),
  baris sort tanggal. Reuse generator raw existing (refactor jadi fungsi per-sheet).
- FE (repo erp-frontend): tombol "Export Multiple" + multi-select toko + date-range di
  halaman Summary Shopee & TikTok.

## Urutan & batasan

- 3 PR backend berurutan (scope 1 → 2 → 3) + 1–2 PR FE (monitoring adjustment; tombol export).
- Tidak menyentuh: alur summary manual/income/retur, 409-guard, stok lokal, sweep faktur.
- Test: unit per guard/transform/generator; verifikasi live pola sama seperti fitur faktur
  (bandingkan dokumen adjustment auto vs manual finance via detail.do).

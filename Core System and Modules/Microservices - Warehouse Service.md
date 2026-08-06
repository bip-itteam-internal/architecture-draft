## Deskripsi

*Microservice **warehouse-service** — WMS Tinggarjaya fulfillment MVP: event ingestion, state machine fulfillment, reconciler periodik, dan operasi gudang approve/pick/pack/RTS/label/dashboard. Implementasi nyata dari konsep [[WH - Fulfillment Flow & WMS Tinggarjaya]].*

- **Stack**: Go + Fiber v2 + MongoDB (driver resmi) + Redis (via redsync distributed lock) + shared-library; di belakang [[CORE - API Master Gateway]] (`/api/warehouse/*`), route internal dilindungi `BIP-Gateway-ID`.
- **Path di repo**: `bip-erp/services/warehouse/` · flat package `main` · `models.go` (state machine) · `fulfillment_event.go` (event ingestion) · `reconciler.go` (sync 60s) · `fulfillment_ops.go` (operasi WMS + role guard).
- **Port**: `6980` (default). **Database**: `warehouse_db` (MongoDB per-service). **Env kunci**: `MONGO_URI`, `MONGO_DB`, `REDIS_URL`, `INTERNAL_GATEWAY_KEY`, `INTEGRATION_MODULE_URL`.
- **Status**: ⚠️ Implemented (ada catatan) — event ingestion + reconciler ✅; operasi WMS lengkap (approve/pick/pack/rts/labels/handover/dashboard/export rekon) ✅; jalur cepat APPROVED→RTS + gerbang rekon `exported_at` ✅; master produk CRUD ✅; frontend warehouse lengkap ✅ (queue+filter+unduh, picking, packing, RTS, label, handover). ✅ **Deadlock cursor reconciler diperbaiki & deploy 2026-07-24** (PR #638, commit `14b9795c`) — lihat *Event Ingestion & Reconciler*.
- **API**: [[API - Warehouse Service]].

## Endpoint / Fitur (Sudah Diimplementasikan)

Daftar rute lengkap di [[API - Warehouse Service]]. Ringkas:

### Event Ingestion & Reconciler

- **`POST /fulfillment/events`** — terima event order dari integration service. Idempoten upsert by `order_id + channel`; abaikan bila `update_time` lebih lama (watermark). Buat order baru `StatusWMS: NEW` bila `status_mp = TO_SHIP`. Propagasi CANCELLED ke order WMS yang belum final. Dilindungi gateway key middleware.
- **Reconciler 60s** — goroutine poll integration `GET /transactions/orders/list` setiap 60 detik, Redis lock (`lock:warehouse-reconciler`, TTL 50s). Menarik **4 stream status**: `TO_SHIP` (antrian kerja) + `SHIPPED`/`COMPLETED`/`RETURNED` (untuk auto-close order yang diproses di luar WMS). **Cursor TERPISAH per status** di `sync_cursors` (`warehouse-reconciler`, `-shipped`, `-completed`, `-returned`) — satu cursor bersama akan terseret stream TO_SHIP yang cepat habis dan melewatkan backlog. Query pakai `sort_by=order_update_date&sort_order=asc` (watermark ASC) supaya catch-up batch-demi-batch tidak melompat. Batch 500/stream, **di-paginasi** (`page`→`$skip`) sampai halaman parsial supaya jendela yang lebih besar dari satu batch terkuras habis dalam satu tick — lihat catatan deadlock (diperbaiki 2026-07-24). Dibatasi 20 halaman/tick (10.000 order/stream); bila batas tersentuh tanpa kemajuan, cursor didorong maju +1 detik. Cursor baru mulai dari 1 Juli 2026. Overlap 5 menit.
- **Open-order sweep 5m** (`open_order_sweep.go`) — jaring pengaman **self-healing** untuk celah reconciler berbasis-cursor. Goroutine tiap 5 menit, Redis lock (`lock:warehouse-open-sweep`, TTL 4m). Berbeda dari reconciler yang menarik order **by-watermark** (`order_update_date`, bisa melewatkan update yang datang telat → order nyangkut permanen), sweep digerakkan oleh **kondisi WMS**: kumpulkan `order_id` semua order **terbuka** (`status_wms NOT IN [HANDED_OVER, CANCELLED]`, tertua-dulu via `updated_at` asc), **batch 100** (bukan 500 max endpoint — `order_ids` dikirim sebagai query string; 500 id ~10KB melebihi buffer header Fiber → HTTP 431), tanya status terkini ke `GET /transactions/orders/list?order_ids=…`, lalu panggil `doUpsert` (auto-close/cancel/update). **Tanpa cursor** → tidak ada order yang bisa terlewat. Dibatasi 5000/tick (sisanya tick berikutnya; progres terjamin karena order tertutup keluar dari himpunan). Idempoten. Run pertama sekaligus membersihkan backlog order nyangkut. Lihat [[ADR - 0027 Status Sinkron Resi Terpisah dari Update_Time Marketplace]] & [[External - Desty]] (konteks migrasi lepas-Desty).
- **`GET /health`** — health check.

### Operasi WMS (Task 7 — `fulfillment_ops.go`)

Role guard via `system_roles["warehouse"]` (header `BIP-System-Roles` dari gateway): `admin_gudang`, `leader`, `spv` (operasional penuh); `admin_qc` (read-only: queue + dashboard).

⚠️ **`admin_gudang_sadewa` (mitra gudang Sadewa) tidak mewarisi izin siapa pun** — pewarisannya ke `admin_gudang` **sudah dicabut** (commit `435bb8ab`). Ia dipegang orang di luar perusahaan, jadi harus disebut **eksplisit** per-rute; hari ini hanya di 8 rute: `queue`, `dashboard`, `labels/history`, `labels/history/export`, `sadewa-shops` (baca) dan `rts`, `labels`, `labels/merged` (tulis). Ketiga rute tulis itu masih dilapisi `gerbangPesananSadewa` (`sadewa_scope.go`) yang — khusus saat aktornya Sadewa — menolak order di luar toko Sadewa. Jalur "akses penuh pengawas WMS" (PPIC & supervisor manufaktur) sengaja **tidak** berlaku baginya. Menambah rute baru tak otomatis membukanya; harus ditulis di daftar `warehouseGuard` rute itu. Detail & alasan pencabutan: [[WH - Warehouse Sadewa]].

> Baris **`Role:`** pada tiap endpoint di bawah **tidak** mencantumkan `admin_gudang_sadewa`. Daftar 8 rute di atas yang jadi acuan untuk role itu; jangan simpulkan "tak boleh" dari baris per-endpoint.

- **`GET /fulfillment/queue`** — antrian order; filter `status` (multi `A,B,C`), `q` (regex order_id/**awb**/SKU/**nama produk**), `shop_ids`, `couriers` (`shipping_provider` $in), `mp_status`/`mp_status_ne` (pisah tab Dikirim/Selesai), `date_from`/`date_to` (WIB, dukung jam `T15:04`), `sort` (created/updated/**qty_desc/qty_asc** via aggregation `total_qty`), pagination. Role: admin_gudang, leader, spv, admin_qc.
- **`GET /fulfillment/queue/counts`** — jumlah per `status_wms` + `ALL`; plus **`DIKIRIM`** (HANDED_OVER & `order_status_mp` ≠ COMPLETED) dan **`SELESAI`** (HANDED_OVER & COMPLETED) untuk tab FE. Role: admin_gudang, leader, spv, admin_qc.
- **`GET /fulfillment/queue/shops`** — daftar distinct toko (`shop_id`, `shop_name`, `channel`), sort `shop_name ASC`. Filter per toko FE. Role: admin_gudang, leader, spv, admin_qc.
- **`GET /fulfillment/queue/couriers`** — daftar distinct kurir (`shipping_provider`) non-kosong, sort ASC. Dropdown filter kurir FE. Role: admin_gudang, leader, spv, admin_qc.
- **`GET /fulfillment/queue/export`** — unduh xlsx rekon (filter sama dengan queue termasuk multi-status koma, tanpa pagination; 1 baris per item; max 20.000 order). `only_new=true` = hanya order belum ditarik. `packer_code=T1` = tim dipilih saat unduh — terisi di kolom xlsx + dicap ke order baru ditarik (tidak menimpa). Efek samping: cap `exported_at`/`exported_by` sekali pada order yang ikut ter-export — gerbang wajib sebelum RTS. Role: admin_gudang, leader, spv, admin_qc.
- **`POST /fulfillment/approve`** — batch approve `order_ids[]`; NEW/HELD → APPROVED. Catat `approved_by/at`. Non-all-or-nothing: kembalikan `{transitioned, skipped, failed}`.
- **`POST /fulfillment/hold`** — batch hold `order_ids[]`; NEW/APPROVED → HELD. Opsional `note` di history.
- **`POST /fulfillment/pick`** — batch konfirmasi picking `order_ids[]`; APPROVED → PICKING. Catat `picked_by/at`.
- **`POST /fulfillment/pack`** — verifikasi scan barcode `scanned_items[]` vs `order.Items` (SKU+qty harus cocok persis); PICKING → PACKED. Catat `packed_by/at` + `packer_code` opsional (kode tim harian T1/T2). Mismatch → HTTP 422 + detail.
- **Menu "Perlu Diproses" (tahap di DEPAN antrian) — `GET /fulfillment/pending-arrange` + `POST /fulfillment/arrange`.** Menggantikan pekerjaan yang selama ini dilakukan admin di aplikasi Desty: melihat order yang **belum punya resi** lalu menerbitkannya. **Keputusan arsitektur inti: order "perlu diproses" TIDAK dibuat sebagai record WMS** — hanya ditampilkan (proxy dari integration). Record `fulfillment_orders` tetap lahir hanya saat order jadi `TO_SHIP` lewat jalur ingest existing, sehingga aturan *"order di WMS pasti sudah punya resi"* utuh dan `fulfillment_event.go` + state machine **tidak diubah**. Aksi proses memakai ulang `ship-batch` (timeout 5 menit untuk batch ≤100). **TikTok didukung (sejak 2026-07-23, commit `779467f1`)** — root cause lama (`Upsert` di `transaction_repo.go` tidak memuat `package_id` ke `setFields`, sehingga nilai hasil `TransformFromTiktok` selalu dibuang saat persist) sudah diperbaiki; backlog lama dilunasi via `cmd/pkgidbackfill` (dry-run default, join `tt_shop_order_details` → `transaction_orders`, tanpa panggilan API TikTok). Guard yang tersisa **hanya** menyaring order TikTok yang `package_id`-nya **masih kosong** (belum sempat tersinkron/backfill) — dikembalikan sebagai hasil gagal, pesan: *"package_id belum tersedia — tunggu sinkronisasi berikutnya atau jalankan backfill"*. Order TikTok ber-`package_id` diproses normal lewat `callShipBatchWithTimeout`, sama seperti channel lain. **Shopee tetap tidak butuh `package_id`** (tanpa guard ini). FE (`PendingArrangeView.tsx`) menonaktifkan baris & menampilkan badge "Menunggu sinkronisasi" hanya untuk baris yang kena guard ini — bukan lagi seluruh TikTok. Alur gudang setelahnya tak berubah: resi terbit → order muncul di "Pesanan Baru" → cetak → kemas → serah kurir. Lihat [[API - Warehouse Service]] & [[External - Desty]].
- **`POST /fulfillment/rts`** — batch RTS; proxy ke integration `POST /fulfillment/ship-batch`. **Gerbang rekon**: order dengan `exported_at` kosong ditolak (422 + `not_exported[]` bila semua tertolak). Transisi dari APPROVED (jalur cepat) atau PACKED (jalur scan). Partial result per order: sukses → RTS_OK + AWB; gagal → RTS_FAILED + `rts_error`. Role: admin_gudang, leader, spv.
- **`POST /fulfillment/labels`** — proxy ke integration `POST /fulfillment/labels`; jika integration 200 OK, update order yang bisa → LABEL_PRINTED + `label_printed_at` + cap `packer_code` batch (tidak menimpa kode dari scan packing). Order yang sudah LABEL_PRINTED dicatat history `"cetak ulang resi"`. Shopee async (PROCESSING → FE auto-retry).
- **`POST /fulfillment/labels/merged`** — cetak batch besar jadi SATU PDF gabungan (proxy integration `/fulfillment/labels/merged`, pdfcpu). Max 100 order/batch (`labelsMergedMaxBatch`), timeout 5 menit (`labelsMergedTimeout`). Hanya order di `included` (labelnya READY & masuk PDF) yang → LABEL_PRINTED. Response `{pdf: base64, included, data}`. Role: admin_gudang, leader, spv.
- **`GET /fulfillment/labels/history`** — riwayat resi tercetak (audit keterlambatan): `printed_by`/`reprint_count` diturunkan dari `history[]`, plus `handed_over_at` untuk deteksi "dicetak tapi belum diserahkan kurir", `package_id` untuk Cetak Ulang TikTok dari FE. Filter `q` (order_id/awb), `date_from`/`date_to` WIB, `actor_role` (→ `printed_by_role`, memisahkan riwayat per gudang; dipakai menu Riwayat Cetak Resi Sadewa, lihat [[WH - Warehouse Sadewa]]), pagination. Role: admin_gudang, leader, spv, admin_qc, **admin_gudang_sadewa** (disebut eksplisit di guard `labels/history` & `labels/history/export`). `printed_by_role` distempel saat `markLabelPrinted` dari role warehouse aktor (`admin_gudang` vs `admin_gudang_sadewa`); resi pra-perubahan tak ber-tag → tak lolos filter.
- **`GET /fulfillment/labels/history/export`** — unduh riwayat sebagai xlsx (filter sama, tanpa pagination, max 20.000): kode packer & dicetak-oleh terisi otomatis — bahan evaluasi salah kirim per tim. Tanpa efek samping. Role: admin_gudang, leader, spv, admin_qc.
- **`POST /fulfillment/handover`** — konfirmasi serah-terima ke kurir; LABEL_PRINTED → HANDED_OVER. Catat `handed_over_at`. Pola sama dengan approve/pick (batch, non-all-or-nothing, `{transitioned, skipped, failed}`). Role: admin_gudang, leader, spv.
- **`GET /fulfillment/dashboard`** — MongoDB `$group by status_wms + $sum 1`; kembalikan `{data:[{status,count}], counts:{STATUS:N}}`. Role: admin_gudang, leader, spv, admin_qc.

## Model Data (`warehouse_db`)

3 collection, grounded ke `models.go`:

- `fulfillment_orders` — state machine per order marketplace. Field: `order_id`, `channel`, `shop_id`, `shop_name`, `order_status_mp`, `status_wms`, `items[]{sku, barcode, nama, qty, rak}`, `update_time` (watermark), `recipient_name`, `recipient_address`, `shipping_provider` (kurir/**Expedisi**; backfill-if-empty menembus watermark — lihat `awb`), `package_id` (TikTok: diambil dari PackageID line-item pertama saat event/reconciler; boleh kosong untuk Shopee atau order TikTok lama), `approved_by/at`, `picked_by/at`, `packed_by/at`, `packer_code` (kode tim packer harian T1/T2 — dari batch labels atau scan pack), `exported_at`/`exported_by` (cap tarikan data rekon — gerbang RTS), `awb` (no resi; TikTok tidak dikembalikan saat RTS → diisi dari `tracking_number` marketplace via event/reconciler, backfill-if-empty, menembus watermark karena resi terbit tanpa menaikkan `update_time`; pola yang sama kini dipakai `shipping_provider`/`package_id`/`recipient` lewat helper bersama `backfillEmptyFields` — lihat fix-log P6 2026-07-27), `rts_at`, `rts_error`, `label_printed_at`, `handed_over_at`, `history[]{actor, at, from, to, note}`, `created_at`, `updated_at`. **Index**: `{order_id, channel}` unique compound, `{status_wms}`, `{update_time}`.
- `warehouse_products` — master SKU + lokasi rak. Field: `sku`, `barcode`, `nama`, `lokasi_rak`. CRUD manual (Task 5–9).
- `sync_cursors` — watermark reconciler (koleksi bersama dengan pola integration service).

## State Machine `status_wms`

```
Jalur cepat (utama):  NEW → APPROVED → RTS_OK → LABEL_PRINTED → HANDED_OVER
Jalur scan (opsional): NEW → APPROVED → PICKING → PACKED → RTS_OK → ...
                       (PICKING juga boleh langsung → RTS_OK — order lama di
                        tahap scan tidak terdampar saat UI scan dihilangkan)
                                    APPROVED/PICKING/PACKED ↘ RTS_FAILED → RTS_OK (retry)
NEW / APPROVED → HELD → APPROVED / CANCELLED
semua status pra-HANDED_OVER → CANCELLED
```

Implementasi: `CanTransition(to string) bool` di `models.go` — dipanggil setiap transisi status.

**Gerbang rekon**: RTS menolak (422) order yang `exported_at`-nya kosong — data
pesanan wajib diunduh via `GET /fulfillment/queue/export` dulu (rekap rekon gudang
diambil per batch sebelum cetak resi). Detail alur: [[WH - Fulfillment Flow & WMS Tinggarjaya]].

**Auto-close order eksternal**: bila event/reconciler membawa status marketplace
SHIPPED/COMPLETED/RETURNED sementara `status_wms` masih pra-RTS
(NEW/APPROVED/PICKING/PACKED/RTS_FAILED/HELD) → order ditutup otomatis ke
HANDED_OVER (action `closed_external`, history "diproses via Seller Center").
Order yang RTS-nya lewat WMS (RTS_OK/LABEL_PRINTED) tidak disentuh — webhook
SHIPPED hasil RTS sendiri hanya memperbarui `order_status_mp`. Reconciler kini
menarik 4 status (TO_SHIP + SHIPPED/COMPLETED/RETURNED) sebagai fallback webhook;
integration `shouldNotifyWarehouse` ikut meneruskan status tersebut.

## Keputusan Teknis (grounded)

- **Flat package `main`**: semua file di `services/warehouse/` root, tidak ada sub-package. Konsisten dengan pola service lain di bip-erp.
- **`doUpsert` shared function**: logika upsert MongoDB (cek watermark, insert baru, cancel propagation, update status_mp) diekstrak ke `doUpsert(ctx, payload, actor)` — dipanggil handler HTTP dan reconciler tanpa network hop ke diri sendiri.
- **Redis guard graceful**: `startReconciler()` log warning dan return (tanpa crash) bila `REDIS_URL` kosong — memudahkan run dev lokal tanpa Redis.
- **`InternalURL` diisi saat init**: `map[string]string{common.Env.IntegrationModuleURL: os.Getenv(...)}` — `validation.ValidateInternalURL` panic bila kosong (proteksi boot-time).

## Belum Diimplementasikan / Catatan (TBD)

- Label Shopee bersifat async 3-langkah (create → poll → download) — FE harus retry order yang masih PROCESSING.
- ⚠️ Penandaan LABEL_PRINTED (dan log reprint) bersifat per-batch integration 200 OK, bukan per hasil order — order Shopee yang masih PROCESSING ikut tertandai printed. Mitigasi: tombol **Cetak Ulang** di FE Riwayat Cetak Resi (order tetap bisa di-retry walau sudah keluar dari layar Pengemasan). Perbaikan ideal: parse hasil per order sebelum menandai.
- Cetak ulang setelah HANDED_OVER tidak dicatat di history (hanya saat masih LABEL_PRINTED).
- Order APPROVED yang sudah ada sebelum deploy gerbang rekon belum punya `exported_at` — perlu sekali "Unduh Semua" agar tertandai dan bisa diproses RTS.
- Deploy backend + frontend harus serentak: gate 422 dan `packer_code` saling bergantung antara service dan UI.
- `POST /fulfillment/labels` menggunakan POST (bukan GET) karena TikTok memerlukan `package_id` per order yang tidak bisa di-derive dari `order_id` saja.
- ✅ **Root cause `package_id` kosong sudah diperbaiki (2026-07-23, commit `779467f1`)**: `Upsert` (`transaction_repo.go`) sebelumnya tidak memuat `package_id` ke `setFields`, sehingga nilai hasil `TransformFromTiktok` selalu terbuang saat persist — order baru/ter-sync ulang sejak fix ini otomatis punya `package_id`. Backlog order TikTok lama dilunasi via `cmd/pkgidbackfill` (baru; join lokal `tt_shop_order_details → transaction_orders`, dry-run default, **tanpa** panggilan API TikTok — beda dari `cmd/ttorderbackfill` yang re-sync penuh lewat API). UI RTS/Perlu Diproses tetap menampilkan peringatan untuk sisa order yang `package_id`-nya belum sempat terisi (sinkron berikutnya atau backfill manual).
- Container `Warehouse-MongoDB` + gateway route `/api/warehouse/*` + docker-compose entry — sudah dikonfigurasi di VM dev; verifikasi production.
- ✅ **Reconciler cursor deadlock — batch saturation (ditemukan & DIPERBAIKI 2026-07-24, PR #638 / commit `14b9795c`).** **Gejala (sebelum fix):** `runReconciler` hanya memanggil `writeCursor` bila ada order dengan `order_update_date` **melampaui** cursor. Query menarik `updated_since = cursor - 300` (overlap 5 mnt) diurutkan ASC dengan `limit=500`. Bila **≥500 order** punya `order_update_date` di dalam jendela `[cursor-300s, cursor]`, seluruh jatah batch habis oleh order yang timestamp-nya **≤ cursor** → cursor tak pernah ditulis → **jendela yang sama ditarik ulang tiap 60 detik selamanya**. Terjadi nyata 24 Juli 2026 09:17 WIB: 514 order `TO_SHIP` mendarat dalam satu jendela, cursor `warehouse-reconciler` beku di `1784859445` selama ≥1 jam 44 menit (log mengulang `TO_SHIP processed 500 orders` tiap menit; 82 order menumpuk di atas cursor). Dampak nyata nihil saat itu (order tertahan sudah masuk WMS lewat webhook), tapi **jaring pengaman reconciler sedang mati**. Kelas bug identik dengan yang dicatat di `resi_wms_safety_net_task.go:42-47`, bentuknya beda: penyebabnya **saturasi batch**, bukan `update_time` yang tak naik. **Perbaikan:** logika inti dipisah ke `reconcileStream(ctx, url, status, cursor, upsert)` yang **mem-paginasi** (`pullOrders` menerima `page`; endpoint list sudah mendukung `page`→`$skip`) sampai halaman parsial, dibatasi `reconcilerMaxPages = 20` (10.000 order/stream/tick). Bila seluruh batas halaman terkuras TANPA satu pun watermark melampaui cursor (deadlock pada skala 10.000), cursor didorong maju `+1` detik — overlap 5 menit tetap menjamin tak ada order terlewat. **Terverifikasi live pasca-deploy:** log berubah dari selalu `500` menjadi `processed 595 orders` lalu `cursor → 1784860814` (bergerak), dan cursor menyusul penuh ke titik terkini. Regresi dijaga `reconciler_test.go` (`TestReconcileStreamDeadlock`, `TestReconcileStreamDorongMajuSaatSeluruhKurasanBuntu`). Catatan: **open-order sweep TIDAK menutup celah ini** — sweep hanya menyegarkan order yang **sudah ada** di WMS (`open_order_sweep.go:124`), tidak bisa menarik masuk order yang belum pernah terdaftar.
- ✅ **`shipping_provider` (Expedisi) kini di-backfill menembus watermark (DIPERBAIKI 2026-07-27, PR #710).** **Gejala (sebelum fix):** blok watermark-skip `doUpsert` (`update_time ≤ existing`) hanya mengisi `awb`, mengabaikan `shipping_provider`/`package_id`/`recipient` — Shopee sering menerbitkan kurir tanpa menaikkan `update_time` order, jadi kolom **Expedisi** (di antrian & riwayat cetak resi) kosong permanen. Terukur 27 Jul 2026: **1.897** `fulfillment_orders` ber-`shipping_provider` kosong (98% terminal SHIPPED/COMPLETED). **Perbaikan:** ekstrak helper murni `backfillEmptyFields(existing, payload)` (fill-only, tak menimpa) yang dipakai **dua jalur** — update normal DAN watermark-skip — sehingga semua field pengiriman kosong (`awb`/`shipping_provider`/`package_id`/`recipient_name`/`recipient_address`) terisi saat re-check; watermark-skip kini `return "backfilled"` (dulu `"awb_backfilled"`, tanpa konsumen lain). Regresi dijaga `fulfillment_backfill_test.go` (`TestBackfillEmptyFields`). **Backlog historis:** sweep hanya menyentuh order **terbuka** → 1.858 order terminal TIDAK auto-heal; dilunasi via **backfill one-off** (salin `shipping_provider` dari `transaction_orders` integration by `order_id`, fill-only + pre-image rollback) — **1.718 terisi (91%)**, sisa 175 tanpa sumber di integration (163 terminal + 12 TO_SHIP terbuka yang akan terisi sendiri). Guard integration terkait: [[Microservices - Integration Service]] (*Guard urutan webhook Shopee `UpdateIfNewer`*). Grounded: `fulfillment_event.go` (`backfillEmptyFields`, `doUpsert`).

## Dependensi & Integrasi

- [[CORE - API Master Gateway]] (routing + gateway key middleware)
- [[Microservices - Integration Service]] — sumber order TO_SHIP (pull via reconciler + push via hook); endpoint internal ship-batch + labels (dibangun Task 5+)
- [[External - Accurate]] — hilir settlement (tidak langsung dari warehouse)
- [[WH - Fulfillment Flow & WMS Tinggarjaya]] — arsitektur lengkap + gap analysis
- [[DB - Overview and Notes]] · [[APP - Web ERP]] (frontend modul warehouse — TBD)

## Dokumen Terkait

- [[WH - Fulfillment Flow & WMS Tinggarjaya]] · [[API - Warehouse Service]]
- [[Microservices - Integration Service]] · [[IT - Background Jobs & Schedulers]]
- [[RUN - Deploy Microservices bip-erp]] — deploy per-service aman (`--no-deps`)

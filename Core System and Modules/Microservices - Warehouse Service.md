## Deskripsi

*Microservice **warehouse-service** — WMS Tinggarjaya fulfillment MVP: event ingestion, state machine fulfillment, reconciler periodik, dan operasi gudang approve/pick/pack/RTS/label/dashboard. Implementasi nyata dari konsep [[WH - Fulfillment Flow & WMS Tinggarjaya]].*

- **Stack**: Go + Fiber v2 + MongoDB (driver resmi) + Redis (via redsync distributed lock) + shared-library; di belakang [[CORE - API Master Gateway]] (`/api/warehouse/*`), route internal dilindungi `BIP-Gateway-ID`.
- **Path di repo**: `bip-erp/services/warehouse/` · flat package `main` · `models.go` (state machine) · `fulfillment_event.go` (event ingestion) · `reconciler.go` (sync 60s) · `fulfillment_ops.go` (operasi WMS + role guard).
- **Port**: `6980` (default). **Database**: `warehouse_db` (MongoDB per-service). **Env kunci**: `MONGO_URI`, `MONGO_DB`, `REDIS_URL`, `INTERNAL_GATEWAY_KEY`, `INTEGRATION_MODULE_URL`.
- **Status**: ⚠️ Implemented (ada catatan) — event ingestion + reconciler ✅; operasi WMS lengkap (approve/pick/pack/rts/labels/handover/dashboard/export rekon) ✅; jalur cepat APPROVED→RTS + gerbang rekon `exported_at` ✅; master produk CRUD ✅; frontend warehouse lengkap ✅ (queue+filter+unduh, picking, packing, RTS, label, handover).
- **API**: [[API - Warehouse Service]].

## Endpoint / Fitur (Sudah Diimplementasikan)

Daftar rute lengkap di [[API - Warehouse Service]]. Ringkas:

### Event Ingestion & Reconciler

- **`POST /fulfillment/events`** — terima event order dari integration service. Idempoten upsert by `order_id + channel`; abaikan bila `update_time` lebih lama (watermark). Buat order baru `StatusWMS: NEW` bila `status_mp = TO_SHIP`. Propagasi CANCELLED ke order WMS yang belum final. Dilindungi gateway key middleware.
- **Reconciler 60s** — goroutine poll `GET {INTEGRATION_MODULE_URL}/transactions/orders/list?status=TO_SHIP` setiap 60 detik. Redis distributed lock (`lock:warehouse-reconciler`, TTL 50s) cegah concurrent run antar-pod. Cursor watermark tersimpan di `sync_cursors` (ID: `warehouse-reconciler`), overlap 5 menit untuk catch-up event yang hilang.
- **`GET /health`** — health check.

### Operasi WMS (Task 7 — `fulfillment_ops.go`)

Role guard via `system_roles["warehouse"]` (header `BIP-System-Roles` dari gateway): `admin_gudang`, `leader`, `spv` (operasional penuh); `admin_qc` (read-only: queue + dashboard).

- **`GET /fulfillment/queue`** — antrian order; filter `status`, `q` (regex order_id/SKU), `shop_ids`, `date_from`/`date_to` (WIB, dukung jam `T15:04`), `sort`, pagination `page`/`limit`. Role: admin_gudang, leader, spv, admin_qc.
- **`GET /fulfillment/queue/counts`** — jumlah order per `status_wms` + kunci `ALL` (total). MongoDB `$group by status_wms + $sum 1`. Role: admin_gudang, leader, spv, admin_qc.
- **`GET /fulfillment/queue/shops`** — daftar distinct toko (`shop_id`, `shop_name`, `channel`) yang ada di `fulfillment_orders`, sort `shop_name ASC`. Digunakan FE untuk filter per toko. Role: admin_gudang, leader, spv, admin_qc.
- **`GET /fulfillment/queue/export`** — unduh xlsx rekon (filter sama dengan queue, tanpa pagination; 1 baris per item; max 20.000 order). `only_new=true` = hanya order belum ditarik. Efek samping: cap `exported_at`/`exported_by` sekali pada order yang ikut ter-export — gerbang wajib sebelum RTS. Role: admin_gudang, leader, spv, admin_qc.
- **`POST /fulfillment/approve`** — batch approve `order_ids[]`; NEW/HELD → APPROVED. Catat `approved_by/at`. Non-all-or-nothing: kembalikan `{transitioned, skipped, failed}`.
- **`POST /fulfillment/hold`** — batch hold `order_ids[]`; NEW/APPROVED → HELD. Opsional `note` di history.
- **`POST /fulfillment/pick`** — batch konfirmasi picking `order_ids[]`; APPROVED → PICKING. Catat `picked_by/at`.
- **`POST /fulfillment/pack`** — verifikasi scan barcode `scanned_items[]` vs `order.Items` (SKU+qty harus cocok persis); PICKING → PACKED. Catat `packed_by/at` + `packer_code` opsional (kode tim harian T1/T2). Mismatch → HTTP 422 + detail.
- **`POST /fulfillment/rts`** — batch RTS; proxy ke integration `POST /fulfillment/ship-batch`. **Gerbang rekon**: order dengan `exported_at` kosong ditolak (422 + `not_exported[]` bila semua tertolak). Transisi dari APPROVED (jalur cepat) atau PACKED (jalur scan). Partial result per order: sukses → RTS_OK + AWB; gagal → RTS_FAILED + `rts_error`. Role: admin_gudang, leader, spv.
- **`POST /fulfillment/labels`** — proxy ke integration `POST /fulfillment/labels`; jika integration 200 OK, update order yang bisa → LABEL_PRINTED + `label_printed_at` + cap `packer_code` batch (tidak menimpa kode dari scan packing). Order yang sudah LABEL_PRINTED dicatat history `"cetak ulang resi"`. Shopee bersifat async (PROCESSING → FE retry).
- **`GET /fulfillment/labels/history`** — riwayat resi tercetak (audit keterlambatan): `printed_by`/`reprint_count` diturunkan dari `history[]`, plus `handed_over_at` untuk deteksi "dicetak tapi belum diserahkan kurir". Filter `q` (order_id/awb), `date_from`/`date_to` WIB, pagination. Role: admin_gudang, leader, spv, admin_qc.
- **`POST /fulfillment/handover`** — konfirmasi serah-terima ke kurir; LABEL_PRINTED → HANDED_OVER. Catat `handed_over_at`. Pola sama dengan approve/pick (batch, non-all-or-nothing, `{transitioned, skipped, failed}`). Role: admin_gudang, leader, spv.
- **`GET /fulfillment/dashboard`** — MongoDB `$group by status_wms + $sum 1`; kembalikan `{data:[{status,count}], counts:{STATUS:N}}`. Role: admin_gudang, leader, spv, admin_qc.

## Model Data (`warehouse_db`)

3 collection, grounded ke `models.go`:

- `fulfillment_orders` — state machine per order marketplace. Field: `order_id`, `channel`, `shop_id`, `shop_name`, `order_status_mp`, `status_wms`, `items[]{sku, barcode, nama, qty, rak}`, `update_time` (watermark), `recipient_name`, `recipient_address`, `shipping_provider`, `package_id` (TikTok: diambil dari PackageID line-item pertama saat event/reconciler; boleh kosong untuk Shopee atau order TikTok lama), `approved_by/at`, `picked_by/at`, `packed_by/at`, `packer_code` (kode tim packer harian T1/T2 — dari batch labels atau scan pack), `exported_at`/`exported_by` (cap tarikan data rekon — gerbang RTS), `awb`, `rts_at`, `rts_error`, `label_printed_at`, `handed_over_at`, `history[]{actor, at, from, to, note}`, `created_at`, `updated_at`. **Index**: `{order_id, channel}` unique compound, `{status_wms}`, `{update_time}`.
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

## Keputusan Teknis (grounded)

- **Flat package `main`**: semua file di `services/warehouse/` root, tidak ada sub-package. Konsisten dengan pola service lain di bip-erp.
- **`doUpsert` shared function**: logika upsert MongoDB (cek watermark, insert baru, cancel propagation, update status_mp) diekstrak ke `doUpsert(ctx, payload, actor)` — dipanggil handler HTTP dan reconciler tanpa network hop ke diri sendiri.
- **Redis guard graceful**: `startReconciler()` log warning dan return (tanpa crash) bila `REDIS_URL` kosong — memudahkan run dev lokal tanpa Redis.
- **`InternalURL` diisi saat init**: `map[string]string{common.Env.IntegrationModuleURL: os.Getenv(...)}` — `validation.ValidateInternalURL` panic bila kosong (proteksi boot-time).

## Belum Diimplementasikan / Catatan (TBD)

- Label Shopee bersifat async 3-langkah (create → poll → download) — FE harus retry order yang masih PROCESSING.
- ⚠️ Penandaan LABEL_PRINTED (dan log reprint) bersifat per-batch integration 200 OK, bukan per hasil order — order Shopee yang masih PROCESSING ikut tertandai printed. Perbaikan: parse hasil per order sebelum menandai.
- Cetak ulang setelah HANDED_OVER tidak dicatat di history (hanya saat masih LABEL_PRINTED).
- Order APPROVED yang sudah ada sebelum deploy gerbang rekon belum punya `exported_at` — perlu sekali "Unduh Semua" agar tertandai dan bisa diproses RTS.
- Deploy backend + frontend harus serentak: gate 422 dan `packer_code` saling bergantung antara service dan UI.
- `POST /fulfillment/labels` menggunakan POST (bukan GET) karena TikTok memerlukan `package_id` per order yang tidak bisa di-derive dari `order_id` saja.
- Order TikTok lama (sebelum deploy yang menyimpan `package_id`) memiliki `package_id` kosong — UI RTS menampilkan peringatan ⚠️; backfill via `cmd/ttorderbackfill` di VM setelah deploy.
- Container `Warehouse-MongoDB` + gateway route `/api/warehouse/*` + docker-compose entry — sudah dikonfigurasi di VM dev; verifikasi production.

## Dependensi & Integrasi

- [[CORE - API Master Gateway]] (routing + gateway key middleware)
- [[Microservices - Integration Service]] — sumber order TO_SHIP (pull via reconciler + push via hook); endpoint internal ship-batch + labels (dibangun Task 5+)
- [[External - Accurate]] — hilir settlement (tidak langsung dari warehouse)
- [[WH - Fulfillment Flow & WMS Tinggarjaya]] — arsitektur lengkap + gap analysis
- [[DB - Overview and Notes]] · [[APP - Web ERP]] (frontend modul warehouse — TBD)

## Dokumen Terkait

- [[WH - Fulfillment Flow & WMS Tinggarjaya]] · [[API - Warehouse Service]]
- [[Microservices - Integration Service]] · [[IT - Background Jobs & Schedulers]]

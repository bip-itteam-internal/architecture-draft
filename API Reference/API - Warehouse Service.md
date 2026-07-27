## Deskripsi

*Endpoint **warehouse-service** (WMS Tinggarjaya fulfillment MVP: event ingestion, state machine, reconciler, operasi gudang). Gateway: `/api/warehouse/*`. Grounded ke `services/warehouse/`.*

- **Implementasi**: [[Microservices - Warehouse Service]] · **Status**: ⚠️ Implemented (ada catatan) — event ingestion ✅; operasi WMS lengkap termasuk handover ✅; master produk CRUD ✅; frontend sebagian ✅
- **Indeks**: [[API - Index]] · Auth: gateway key `BIP-Gateway-ID` untuk semua route. Operasional WMS tambahan: role guard via `BIP-System-Roles` header (`system_roles["warehouse"]`).

## Fulfillment — Event Ingestion (✅ Diimplementasikan)

| Method | Path | Fungsi |
|---|---|---|
| POST | `/fulfillment/events` | Terima event order dari integration service. Idempoten upsert by `order_id + channel`; abaikan bila `update_time` ≤ existing. Buat `status_wms: NEW` untuk order TO_SHIP baru. Propagasi CANCELLED ke order WMS yang belum final (HANDED_OVER/CANCELLED). |
| GET | `/health` | Health check |

**Request body** `POST /fulfillment/events`:
```json
{
  "order_id":         "string (wajib)",
  "channel":          "string (wajib) — tiktok / shopee",
  "shop_id":          "string",
  "shop_name":        "string",
  "status":           "string — TO_SHIP / CANCELLED / dll",
  "update_time":      "int64 (unix timestamp)",
  "recipient_name":   "string — nama penerima",
  "recipient_address":"string — alamat lengkap penerima",
  "shipping_provider":"string — nama kurir (JNE, SiCepat, dll)",
  "package_id":       "string — TikTok saja; diambil dari PackageID line-item pertama; boleh kosong untuk Shopee",
  "items": [{ "sku": "string", "qty": "int" }]
}
```

**Response**:
- `201 Created` + `{"action": "created"}` — order baru berhasil dibuat
- `200 OK` + `{"action": "updated"}` — status_mp diperbarui
- `200 OK` + `{"action": "cancelled"}` — cancel propagasi berhasil
- `200 OK` + `{"action": "closed_external"}` — order diproses di luar WMS (marketplace SHIPPED/COMPLETED/RETURNED saat status_wms masih pra-RTS) → auto-close ke HANDED_OVER + history "diproses via Seller Center"
- `200 OK` + `{"action": "skipped", "reason": "stale_event"}` — update_time lebih lama
- `200 OK` + `{"action": "skipped", "reason": "already_final"}` — cancel tapi sudah HANDED_OVER/CANCELLED
- `200 OK` + `{"action": "ignored", "reason": "not_to_ship"}` — order baru tapi bukan TO_SHIP
- `400 Bad Request` — body tidak valid atau `order_id`/`channel` kosong
- `401 Unauthorized` — gateway key tidak cocok

## Fulfillment — Operasi WMS (✅ Diimplementasikan — Task 7)

Auth tambahan: `BIP-System-Roles` header (JSON map), key `"warehouse"`, value = role string.

| Method | Path | Role yang Diizinkan | Fungsi |
|---|---|---|---|
| GET | `/fulfillment/queue` | admin_gudang, leader, spv, admin_qc | Antrian order: filter status/q/shop_ids/couriers/tanggal+jam/status_mp, sort, pagination |
| GET | `/fulfillment/queue/counts` | admin_gudang, leader, spv, admin_qc | Jumlah order per status_wms + `ALL`; plus `DIKIRIM`/`SELESAI` (pecahan HANDED_OVER) |
| GET | `/fulfillment/queue/shops` | admin_gudang, leader, spv, admin_qc | Daftar distinct toko yang ada di antrian, sort nama ASC |
| GET | `/fulfillment/queue/couriers` | admin_gudang, leader, spv, admin_qc | Daftar distinct kurir (`shipping_provider`) non-kosong, sort ASC — dropdown filter kurir |
| GET | `/fulfillment/queue/export` | admin_gudang, leader, spv, admin_qc | Unduh xlsx rekon (filter sama dengan queue); `only_new`/`packer_code`; tandai `exported_at` |
| GET | `/fulfillment/pending-arrange` | admin_gudang, leader, spv, admin_qc | **Menu "Perlu Diproses"** — daftar order yang **belum punya resi** (`raw_status ∈ {AWAITING_SHIPMENT, READY_TO_SHIP, RETRY_SHIP}`, termasuk COD; `UNPAID`/`ON_HOLD` dikecualikan) dan belum `arrange_status=arranged`. **Order ini BUKAN record WMS** — proxy ke integration `GET /fulfillment/pending-arrange`. Param: `shop_ids`, `date_from`/`date_to` (`YYYY-MM-DD[THH:mm]` WIB, `date_to` inklusif; format lain → 400), `q` (no pesanan/SKU/nama produk), `page`, `limit` (default 50, maks 200). Urut `order_date` ASC |
| POST | `/fulfillment/arrange` | admin_gudang, leader, spv | **Proses Pengiriman** — terbitkan resi untuk batch order pilihan admin. Body `{orders:[{order_id, channel, shop_id, package_id}]}`, **maks 100**; 0 order → 422. Memakai ulang integration `POST /fulfillment/ship-batch` (timeout **5 menit** — batch 100 diproses sekuensial di sisi marketplace). **TikTok didukung** (sejak 2026-07-23, commit `779467f1`). Sebelumnya sempat diblokir total karena `package_id` selalu kosong; akar masalahnya ternyata **bug persist**: `setFields` di `Upsert` (`transaction_repo.go`) tak memuat `package_id`, sehingga nilai hasil `TransformFromTiktok` (dari `line_items[].package_id`) selalu dibuang — 0 dari 313.503 order TikTok punya `package_id`. TikTok **sudah** menyediakan package sejak `AWAITING_SHIPMENT` (terverifikasi: 10.304/10.304 order mentah punya `line_items[].package_id`), jadi **tidak** perlu TikTok Create Package API. Backlog lama dilunasi lewat `cmd/pkgidbackfill` (lokal, tanpa panggilan API). Guard tersisa: order TikTok yang `package_id`-nya **masih** kosong ditolak dengan pesan *"package_id belum tersedia — tunggu sinkronisasi berikutnya atau jalankan backfill"*. **Shopee tak butuh `package_id`** (`ShipOrder(orderSN)`). Respons `{data:[{order_id, channel, success, awb, error}]}` per order. **Tidak** menyentuh `fulfillment_orders` maupun state machine |
| POST | `/fulfillment/approve` | admin_gudang, leader, spv | Batch approve → APPROVED |
| POST | `/fulfillment/hold` | admin_gudang, leader, spv | Batch hold → HELD |
| POST | `/fulfillment/pick` | admin_gudang, leader, spv | Batch konfirmasi picking → PICKING |
| POST | `/fulfillment/pack` | admin_gudang, leader, spv | Verifikasi scan SKU+qty per order → PACKED (+ `packer_code` opsional) |
| POST | `/fulfillment/rts` | admin_gudang, leader, spv | Batch RTS → proxy integration ship-batch; gate `exported_at` (422 `not_exported`) |
| POST | `/fulfillment/labels` | admin_gudang, leader, spv | Cetak resi per order (URL/PDF) → LABEL_PRINTED; reprint dicatat di history |
| POST | `/fulfillment/labels/merged` | admin_gudang, leader, spv | Cetak batch besar → **SATU PDF gabungan** (max 100/batch, timeout 5 mnt); hanya `included` → LABEL_PRINTED |
| GET | `/fulfillment/labels/history` | admin_gudang, leader, spv, admin_qc | Riwayat resi tercetak — audit keterlambatan (dicetak siapa/kapan, cetak ulang, serah kurir); filter opsional `actor_role` (per gudang) |
| GET | `/fulfillment/labels/history/export` | admin_gudang, leader, spv, admin_qc | Unduh riwayat xlsx (filter jam WIB + `actor_role`); kolom: Waktu Cetak, No Resi, Expedisi, Nama Toko, Nama Produk, Qty |
| POST | `/fulfillment/handover` | admin_gudang, leader, spv | Konfirmasi serah-terima kurir → HANDED_OVER |
| GET | `/fulfillment/dashboard` | admin_gudang, leader, spv, admin_qc | Aggregate count per status_wms |

### Request / Response

**`GET /fulfillment/queue`**
- Query (semua opsional):
  - `status=NEW` — dicocokkan ke `status_wms`; dukung multi-status `status=A,B,C` (`$in`)
  - `q=` — regex case-insensitive ke `order_id` / **`awb` (no resi)** / `items.sku` / **`items.nama` (nama produk)**
  - `shop_ids=id1,id2` — filter multi-toko
  - `couriers=J&T Express,SPX` — filter multi-kurir (`shipping_provider` `$in`)
  - `mp_status=COMPLETED` / `mp_status_ne=COMPLETED` — filter `order_status_mp` (exact / not-equal); memecah HANDED_OVER jadi tab Dikirim (`mp_status_ne=COMPLETED`) vs Selesai (`mp_status=COMPLETED`)
  - `date_from=` / `date_to=` — filter `created_at`, timezone WIB. Dua format: `2006-01-02T15:04` (dengan jam; `date_to` inklusif sampai akhir menit) atau `2006-01-02` (tanpa jam; `date_to` sampai 23:59:59.999). Format tidak valid diabaikan (graceful skip)
  - `sort=` — `created_desc` / `updated_desc` / `qty_desc` / `qty_asc`; default created_at ASC. Qty-sort: total qty produk per order (aggregation `total_qty`), tanggal terlama sebagai kunci kedua
  - `page=` (default 1), `limit=` (default 50, max 200)
- Response `200`: `{"data": [FulfillmentOrder...], "total": n, "page": n, "limit": n}`

**`POST /fulfillment/labels/merged`** — cetak batch besar jadi satu PDF:
```json
// Request (max 100 order/batch)
{ "orders": [{"order_id": "...", "package_id": "..."}], "packer_code": "T1" }
// Response 200
{ "pdf": "<base64 PDF gabungan>", "included": ["ORDER_A", ...], "data": [LabelResult...] }
```
- Proxy ke integration `POST /fulfillment/labels/merged` (pdfcpu MergeRaw). Hanya order yang labelnya READY masuk PDF (`included`); yang gagal/PROCESSING dilaporkan di `data` tapi tidak ditandai LABEL_PRINTED
- Hanya order di `included` yang transisi ke LABEL_PRINTED + cap `packer_code`
- `400` bila > 100 order/batch; timeout 5 menit (batch Shopee polling lambat)
- FE: tombol "Buka PDF Gabungan (N resi)" — satu tab, satu perintah print (tanpa 100 tab terpisah)

**`GET /fulfillment/queue/export`** — unduh xlsx untuk rekap/rekon gudang:
- Query: filter sama dengan `/queue` (status — termasuk multi-status koma, q, shop_ids, date_from/to, sort — tanpa pagination), plus:
  - `only_new=true` = hanya order yang `exported_at`-nya belum ada (rekon per batch — unduhan siang tidak membawa data pagi)
  - `packer_code=T1` = kode tim packer batch ini — satu batch unduhan dikerjakan satu tim, jadi tim dipilih saat unduh; kode terisi di kolom xlsx **dan dicap ke order yang baru ditarik** (tidak menimpa kode yang sudah ada)
- Satu baris per item produk. Kolom: No, Nomor Pesanan, Tanggal Pesanan Masuk (WIB), No Resi (awb), SKU, Nama Barang, Qty Pesanan, Nama Toko, Expedisi, Kode Packer (urutan: `packer_code` order → param `packer_code` → `packed_by`), Keterangan (kosong, diisi manual)
- Efek samping: order yang ikut ter-export dicap `exported_at` + `exported_by` (sekali; unduhan ulang tidak menimpa) — **gerbang wajib sebelum RTS**
- FE Pengambilan Barang memakai `status=APPROVED,PICKING,PACKED,RTS_FAILED` agar order legacy tahap scan ikut bisa ditarik
- Response `200`: file xlsx (`Content-Disposition: attachment`); `400` bila hasil filter > 20.000 order

**`POST /fulfillment/approve` / `/hold` / `/pick`** (pola sama):
```json
// Request
{ "order_ids": ["ORDER_A", "ORDER_B"], "note": "opsional" }
// Response 200
{ "transitioned": ["ORDER_A"], "skipped": ["ORDER_B"], "failed": [] }
```
- `skipped`: order yang tidak bisa transisi per state machine (`CanTransition` false)
- `failed`: order tidak ditemukan di DB atau error update

**`POST /fulfillment/pack`**:
```json
// Request — packer_code opsional (kode tim harian/freelance T1/T2)
{
  "order_id": "ORDER_A",
  "scanned_items": [{"sku": "SKU-001", "qty": 2}, {"sku": "SKU-002", "qty": 1}],
  "packer_code": "T1"
}
// Response 200
{ "action": "packed", "order_id": "ORDER_A" }
// Response 422 (SKU/qty mismatch)
{ "error": "verifikasi SKU/qty gagal", "mismatches": [{"sku": "SKU-001", "expected": 2, "got": 1}] }
```
- `409`: order tidak bisa transisi ke PACKED (status saat ini bukan PICKING)

**`POST /fulfillment/rts`**:
```json
// Request — package_id diperlukan untuk TikTok; Shopee boleh kosong
{ "orders": [{"order_id": "ORDER_A", "package_id": "PKG_123"}] }
// Response 200 — partial result per order; not_exported = order yang ditolak gerbang rekon
{ "data": [{"order_id": "ORDER_A", "channel": "tiktok", "success": true, "awb": "JNE123"}], "not_exported": [] }
// Response 422 — SEMUA order yang diminta belum ditarik datanya (gerbang rekon)
{ "error": "data pesanan belum ditarik — unduh data pesanan masuk dulu sebelum RTS/cetak resi", "not_exported": ["ORDER_A"] }
```
- **Gerbang rekon**: order dengan `exported_at` kosong ditolak — wajib unduh via `/queue/export` dulu
- Transisi valid: APPROVED/PICKING → RTS_OK (jalur cepat tanpa scan; PICKING ikut agar order lama di tahap scan tidak terdampar) atau PACKED → RTS_OK (jalur scan); RTS_FAILED → RTS_OK (retry)
- `502`: integration service tidak bisa dihubungi

**`POST /fulfillment/labels`**:
```json
// Request — packer_code (T1/T2) dicap ke semua order batch yang transisi ke LABEL_PRINTED
{ "orders": [{"order_id": "ORDER_A", "package_id": "PKG_123"}], "packer_code": "T1" }
// Response — proxy langsung dari integration
{ "status": "success", "data": [{"order_id": "ORDER_A", "channel": "tiktok", "status": "READY", "url": "https://..."}] }
```
- Label status: `READY` | `PROCESSING` (Shopee async, FE harus retry) | `FAILED`
- Jika response integration 200 OK → order yang bisa transisi diupdate ke `LABEL_PRINTED`
- `packer_code` tidak menimpa kode yang sudah ada dari scan packing
- Order yang sudah `LABEL_PRINTED` → dicatat entry history `note: "cetak ulang resi"` (untuk kolom Cetak Ulang di riwayat)
- ⚠️ Penandaan LABEL_PRINTED bersifat per-batch (integration 200 OK), bukan per hasil order — order Shopee yang masih `PROCESSING` ikut tertandai

**`GET /fulfillment/labels/history`** — riwayat resi tercetak untuk audit keterlambatan:
- Query: `q=` (regex order_id/awb), `date_from=`/`date_to=` (WIB `2006-01-02`, pada `label_printed_at`), `actor_role=` (dinormalisasi → `printed_by_role`; mis. `admin_gudang_sadewa` untuk menu Riwayat Cetak Resi Warehouse Sadewa), `page`/`limit` (default 50, max 1000)
- Sort `label_printed_at DESC`. Hanya order yang `label_printed_at`-nya terisi.
```json
// Response 200
{
  "data": [{
    "order_id": "...", "channel": "tiktok", "shop_name": "...",
    "package_id": "PKG_123", "awb": "JNE123", "packer_code": "T1",
    "status_wms": "LABEL_PRINTED",
    "label_printed_at": "...", "printed_by": "EMP-001",
    "printed_by_role": "admin_gudang_sadewa",
    "reprint_count": 1, "last_reprint_at": "...",
    "handed_over_at": null
  }],
  "total": 120, "page": 1, "limit": 50
}
```
- `printed_by` diambil dari history entry pertama dengan `to: LABEL_PRINTED` tanpa note; `reprint_count` dari entry `note: "cetak ulang resi"`
- `printed_by_role` = role warehouse aktor pencetak awal (`admin_gudang` / `admin_gudang_sadewa`), distempel saat `markLabelPrinted`; dipakai `actor_role` untuk memisahkan riwayat per gudang. Resi tercetak **sebelum** field ini ada tak punya `printed_by_role` → tak lolos filter `actor_role`
- `package_id` disertakan untuk tombol Cetak Ulang FE (TikTok butuh package_id saat re-request label; Shopee cukup `order_sn` + `shop_id`)
- Interpretasi audit: `handed_over_at` kosong = resi dicetak tapi paket belum diserahkan ke kurir
- FE Riwayat menyediakan tombol **Cetak Ulang** per baris — sekaligus jalur retry order Shopee `PROCESSING` yang sudah telanjur tercap LABEL_PRINTED (penandaan per-batch) dan tidak muncul lagi di layar Pengemasan

**`GET /fulfillment/labels/history/export`** — unduh riwayat sebagai xlsx:
- Query: `q` + `date_from`/`date_to` (WIB, dukung jam `2006-01-02T15:04` atau tanggal saja, batas menit inklusif) + `actor_role` — sama dengan `/labels/history`; tanpa pagination; max 20.000 baris
- Kolom (kebutuhan rekap tim, 2026-07-20; **Expedisi** ditambah 2026-07-24 untuk surat jalan): **No, Waktu Cetak (WIB), No Resi, Expedisi, Nama Toko, Nama Produk, Qty** — satu baris per produk. `Expedisi` = `shipping_provider` (kosong bila belum terisi event/reconciler), ejaan konsisten dengan export rekon antrian.
- Basis filter = `label_printed_at` (waktu cetak resi). Tanpa efek samping (tidak ada penandaan apa pun)

**`GET /fulfillment/queue/counts`**:
```json
// Response 200 — map status_wms → jumlah order; "ALL" = total semua status.
// DIKIRIM/SELESAI = pecahan HANDED_OVER (belum COMPLETED vs COMPLETED).
{"NEW": 5, "APPROVED": 3, "RTS_OK": 2, "HANDED_OVER": 40, "DIKIRIM": 18, "SELESAI": 22, "ALL": 50}
```

**`GET /fulfillment/queue/shops`**:
```json
// Response 200 — array distinct toko, sorted shop_name ASC
[{"shop_id": "123", "shop_name": "BH Official", "channel": "tiktok"}]
```

**`GET /fulfillment/queue/couriers`**:
```json
// Response 200 — array distinct kurir (shipping_provider) non-kosong, sort ASC
["ID Express", "J&T Express", "JNE Reguler", "SPX Standard"]
```

**`POST /fulfillment/handover`** (pola sama dengan approve/hold/pick):
```json
// Request
{ "order_ids": ["ORDER_A", "ORDER_B"], "note": "opsional" }
// Response 200
{ "transitioned": ["ORDER_A"], "skipped": ["ORDER_B"], "failed": [] }
```
- Transisi yang diizinkan: LABEL_PRINTED → HANDED_OVER.
- Catat `handed_over_at` timestamp pada order yang berhasil transisi.

**`GET /fulfillment/dashboard`**:
```json
// Response 200
{
  "data": [{"status": "APPROVED", "count": 5}, {"status": "NEW", "count": 12}],
  "counts": {"APPROVED": 5, "NEW": 12, "PACKED": 3}
}
```

### Error Umum (semua endpoint operasional)

| Code | Keterangan |
|---|---|
| 400 | Body tidak valid atau `order_ids`/`orders` kosong |
| 401 | `BIP-Employee-ID` header kosong |
| 403 | `system_roles["warehouse"]` tidak ada dalam daftar role yang diizinkan |
| 404 | Order tidak ditemukan (pack only) |
| 409 | Transisi tidak valid per state machine (pack only) |
| 422 | SKU/qty mismatch (pack) · semua order belum ditarik datanya (rts) |
| 502 | Integration service tidak bisa dihubungi (rts, labels) |

## Master Produk (✅ Diimplementasikan)

Auth: gateway key + role guard `system_roles["warehouse"]`. Path group `/wms/`.

| Method | Path | Role yang Diizinkan | Fungsi |
|---|---|---|---|
| GET | `/wms/products` | admin_gudang, leader, spv, admin_qc | List master SKU, filter `?q=` |
| POST | `/wms/products` | admin_gudang, leader, spv | Buat SKU baru |
| PUT | `/wms/products/:sku` | admin_gudang, leader, spv | Update data SKU |
| DELETE | `/wms/products/:sku` | admin_gudang, leader, spv | Hapus SKU |
| POST | `/wms/products/import` | admin_gudang, leader, spv | Import xlsx master produk |

## Dokumen Terkait

- [[Microservices - Warehouse Service]] · [[WH - Fulfillment Flow & WMS Tinggarjaya]] · [[API - Integration Service]] · [[API - Index]]

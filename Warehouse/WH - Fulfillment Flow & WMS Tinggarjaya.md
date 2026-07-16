# WH - Fulfillment Flow & WMS Tinggarjaya

## Deskripsi

*Dokumen ini merangkum alur fulfillment end-to-end gudang Tinggarjaya — dari order masuk
via webhook marketplace hingga serah kurir dan settlement di Accurate. Mencakup arsitektur
`services/warehouse` (MVP), state machine, event architecture, dan gap analysis terhadap
sistem yang sudah berjalan.*

- **Status**: ⚠️ Implemented (ada catatan) — Fase 1 ✅ existing; Fase 2 event+reconciler ✅ Task 4; Fase 3 operasi WMS ⚠️ partial (approve/pick/pack/rts/labels/dashboard ✅ Task 7; produk CRUD 🟡); Fase 4 settlement ✅ existing
- **Referensi**: Blueprint WMS Tinggarjaya (Juli 2026) · Design doc `2026-07-12-wms-tinggarjaya-fulfillment-design.md`
- **Implementasi**: [[Microservices - Warehouse Service]] · **API**: [[API - Warehouse Service]]
- **Dependensi utama**: [[Microservices - Integration Service]], [[External - Accurate]]

---

## Alur Fulfillment Lengkap

### Fase 1 — Order Masuk (✅ Sudah Berjalan)

```
TikTok Shop                    Shopee
      │                           │
      ▼                           ▼
Webhook langsung dari marketplace (direct integration)
      │                           │
      └──────────┬────────────────┘
                 │
                 ▼
Queue (Redis) → webhook_consumer_task (polling 5 detik)
        │
        ├─ TikTok → TiktokDirectProcessor
        │           (selalu tarik detail order dari API TikTok)
        │
        └─ Shopee → ShopeePushProcessor
                    (create-on-missing: order baru = tarik dari Shopee,
                     order lama = update status saja)
        │
        ▼
transaction_orders (unified model)
Status: TO_PROCESS → auto-evaluated → TO_SHIP / PENDING
        │
        ▼ hook baru OnOrderUpsert (dibangun di MVP)
        │
        ▼
POST warehouse /fulfillment/events  (async + retry via webhook_tasks)
```

> **Auto-approve berjadwal untuk WMS tidak dibangun.** Approve order di WMS dilakukan
> manual (batch) oleh Admin Gudang / Leader / SPV. Auto-ship existing (00:01–14:59 WIB)
> tetap berjalan di integration service — ini berbeda dari approve WMS.

### Fase 2 — Event & Reconciler (✅ Diimplementasikan — Task 4)

```
Integration service
        │
        ├─ OnOrderUpsert hook → POST warehouse /fulfillment/events   [🟡 hook belum ada]
        │  payload: order_id, channel, shop_id, status, items[{sku, qty}]
        │  • Idempoten (upsert by order_id + channel; bandingkan update_time)   ✅
        │  • Retry via webhook_tasks existing (event gagal tidak hilang)
        │  • Cancel webhook (type 11) → order CANCELLED realtime               ✅
        │
        └─ Reconciler sweep (tiap 60 detik, goroutine warehouse)               ✅
           • Cursor watermark di sync_cursors + overlap 5 menit                ✅
           • Redis lock lock:warehouse-reconciler TTL 50s (cegah concurrent)   ✅
           • Pull GET /transactions/orders/list?status=TO_SHIP&updated_since=  ✅
           • Tangkap event yang hilang saat restart / network drop              ✅
           • Worst-case keterlambatan: ±1 menit
```

> **Catatan**: Hook `OnOrderUpsert` di integration service belum diimplementasikan. Saat ini hanya reconciler 60s yang aktif (worst-case lag ±1 mnt). Hook push realtime menjadi bagian Task integration berikutnya.

### Fase 3 — Operasi Gudang / WMS (⚠️ Partial — approve/pick/pack/rts/labels/dashboard ✅ Task 7)

#### State Machine `fulfillment_orders`

```
NEW → APPROVED → PICKING → PACKED → RTS_OK → LABEL_PRINTED → HANDED_OVER
                                  ↘ RTS_FAILED (retryable → RTS_OK)

NEW / APPROVED → HELD (tahan manual, mencurigakan)
semua status pra-RTS → CANCELLED (dari webhook cancel marketplace)
```

#### Alur Operasional

```
[1. APPROVE — batch]
Admin Gudang / Leader / SPV centang N order NEW
POST /fulfillment/approve → status: APPROVED
Order mencurigakan → HELD
        │
        ▼
[2. PICKING]
Picklist agregat per batch (group by SKU → lokasi rak)
Satu putaran ambil banyak order sekaligus
Scan barcode rak → konfirmasi ambil → PICKING selesai per order
        │
        ▼
[3. PACKING]
Scan resi / pilih order → tampil item wajib
Scan barcode SKU per item
Qty & SKU harus cocok persis (mismatch = tolak, indikator merah)
Status → PACKED
        │
        ▼
[4. RTS BATCH]
Order PACKED → POST integration /fulfillment/ship-batch
  ├─ TikTok: ShipPackage (POST /fulfillment/202309/packages/{id}/ship)
  │          → sudah ada di kode (tiktok_client.go:542)
  └─ Shopee: ship_order (POST /api/v2/logistics/ship_order)
             → sudah ada di kode
Per order: RTS_OK + AWB, atau RTS_FAILED + alasan (retryable)
Batch tidak all-or-nothing — partial result per order
        │
        ▼
[5. CETAK RESI]
GET integration /fulfillment/labels?order_ids=
  ├─ TikTok (sync):
  │   GET /fulfillment/202309/packages/{id}/shipping_documents
  │   → respons doc_url (PDF) ← ENDPOINT BARU di integration
  │
  └─ Shopee (async, 3 langkah):
      create_shipping_document (task per order)
         ↓
      poll get_shipping_document_result (PROCESSING → READY / FAILED)
         ↓
      download_shipping_document (binary PDF, hanya saat READY)
      → FE cetak order yang READY duluan; poll ulang yang masih PROCESSING
      ← ENDPOINT BARU di integration

Merge batch → 1 PDF → print → LABEL_PRINTED

⚠️ PRASYARAT: label hanya tersedia SETELAH RTS. Urutan ini final.
⚠️ RISIKO: scope/permission app untuk shipping document belum terverifikasi.
   Langkah pertama implementasi = test harness cmd/labeltest dengan order
   real ter-RTS. Build label feature hanya jika 200 OK.
        │
        ▼
[6. SERAH KURIR]
Webhook IN_TRANSIT dari platform (existing) → event → HANDED_OVER
Lifecycle selanjutnya dipantau transaction_orders (integration)
```

### Fase 4 — Settlement & Akuntansi (✅ Sudah Berjalan)

```
Kurir pickup → status pengiriman diupdate platform
        │
        ▼
Order status = COMPLETED
        │
        ├─ Income reconciler TikTok  (tiap jam :30)
        │  Batch 600 order/run, circuit breaker
        │
        └─ Shopee escrow reconciler  (tiap jam :00)
        │
        ▼
Settlement breakdown per-SKU tersimpan
        │
        ▼
Summary report harian
POST /summary/reports/:id/send/ACCURATE
        │
        ▼
Accurate Online (Sales Invoice / Sales Return)
```

### Fase 5 — Return (⚠️ Sebagian Berjalan — WMS fase berikut)

```
Buyer ajukan retur di platform
        │
        ▼
Status → RETURNED (entity TransactionReturn sudah ada ✅)
        │
        ▼
[WMS: Modul Return] ← 🟡 fase berikut, bukan MVP
        │
        ├─ Reuse   — barang masih layak jual, masuk stok kembali
        ├─ Rework  — perlu perbaikan/re-packing sebelum dijual lagi
        └─ Reject  — barang rusak, tidak bisa dijual
```

---

## Arsitektur WMS — Keputusan

### Keputusan: Service baru `services/warehouse` ✅

WMS Tinggarjaya dibangun sebagai **service terpisah** — bukan di integration, bukan di manufacture.

> *"lumayan complex, service terpisah, jangan di integration"* — keputusan user 2026-07-12

| Komponen | Tanggung jawab |
|---|---|
| **`services/warehouse` (BARU)** | Otak WMS: Go + Fiber + MongoDB `warehouse_db`. State machine fulfillment, endpoint approve/pick/pack/rts/labels, penerima event, dashboard |
| `services/integration` | **Proxy tipis API marketplace** — pemilik OAuth credentials. Endpoint internal: `ship-batch` (bungkus ShipPackage/ShipOrder existing) + `labels` (client baru TikTok + Shopee shipping document) |
| `services/manufacture` | **Tidak tersentuh.** `manufacture_resi` existing tetap untuk fungsi lamanya (scan form Return & Keluar FG). Warehouse **tidak** bergantung ke manufacture — AWB didapat dari respons RTS + webhook |
| `erp-frontend` | Modul baru `warehouse` di `(main)`, akses via `system_roles["warehouse"]` |

**Infra baru yang perlu dibuat:**
- Container `Warehouse-MongoDB` (`warehouse_db`)
- Gateway route `/api/warehouse/*`
- Entri docker-compose + deploy config bip-vps
- Port baru untuk warehouse service

### Struktur `warehouse_db`

```
warehouse_db (MongoDB, pola standar bip-erp)
├── fulfillment_orders    — state machine per order
│   fields: order_id, channel, shop_id, shop_name, order_status_mp,
│           status_wms, items[{sku, barcode, nama, qty, rak}],
│           approved_by/at, picked_by/at, packed_by/at,
│           awb, rts_at, rts_error, label_printed_at, handed_over_at,
│           history[] (audit tiap transisi: siapa, kapan, dari→ke)
│
└── warehouse_products    — master SKU + lokasi rak
    fields: sku, barcode, nama, lokasi_rak
    CRUD manual di FE + import xlsx (MVP)
    Sumber jangka panjang: master product manufacture — kini dari data HPP
    (POST /master-product/sync-hpp), BUKAN lagi Google Sheet
    (jangan jadi dependency MVP)
```

### Endpoint baru

**`services/warehouse`** (via gateway `/api/warehouse/*`, role-guarded):

| Method | Path | Fungsi |
|---|---|---|
| POST | `/fulfillment/events` | Terima event order dari integration (internal, idempoten) |
| GET | `/fulfillment/queue` | Antrian order per status WMS |
| POST | `/fulfillment/approve` | Approve batch order NEW → APPROVED |
| POST | `/fulfillment/hold` | Tahan order → HELD |
| POST | `/fulfillment/pick` | Konfirmasi picking per order |
| POST | `/fulfillment/pack` | Verifikasi scan barcode SKU + qty → PACKED |
| POST | `/fulfillment/rts` | RTS batch → proxy ke integration ship-batch |
| GET | `/fulfillment/labels` | Cetak label → proxy ke integration labels |
| GET | `/fulfillment/dashboard` | Kartu antrian, resi keluar, cancel, RTS gagal |
| CRUD | `/products` + `/products/import` | Master SKU + lokasi rak + import xlsx |

**`services/integration`** (internal, gateway-key) — endpoint baru:

| Method | Path | Fungsi |
|---|---|---|
| POST | `/fulfillment/ship-batch` | Batch ShipPackage (TikTok) + ship_order (Shopee); hasil per-order |
| GET | `/fulfillment/labels` | Ambil shipping document PDF per platform, merge batch |

---

## Gap Analysis: Blueprint WMS vs Sistem yang Ada

| Modul Blueprint | Status | Keterangan |
|---|---|---|
| Order Marketplace | ✅ Sudah ada | Integration sync TikTok + Shopee, event ke warehouse (dibangun MVP) |
| Approve + Picking + Packing | ❌ Belum ada | Core WMS MVP |
| RTS batch | ⚠️ Sebagian | `ShipPackage`/`ShipOrder` ada, endpoint batch belum |
| Cetak Resi (label) | ❌ Belum ada | Client baru di integration; Shopee async 3-langkah |
| Return Reuse/Rework/Reject | ❌ Belum ada | Fase berikut (bukan MVP) |
| Dashboard gudang | ❌ Belum ada | Bagian dari `services/warehouse` MVP |
| Master SKU + lokasi rak | ❌ Belum ada | `warehouse_products` di warehouse_db |
| Report internal gudang | ❌ Belum ada | Fase berikut |

---

## Peran KiriminAja

KiriminAja **tidak diperlukan** untuk fulfillment order TikTok Shop dan Shopee.

| Channel Order | Logistik | Butuh KiriminAja? |
|---|---|---|
| TikTok Shop | Platform assign kurir + resi | ❌ Tidak |
| Shopee | Platform assign kurir + resi | ❌ Tidak |
| Order Online / Reseller / Non-marketplace | Tidak ada platform yang urus | ✅ Ya |

KiriminAja baru dibutuhkan jika ada channel penjualan di luar marketplace — channel ini
belum ada entity-nya di `bip-erp` (TBD).

---

## Hak Akses (`system_roles["warehouse"]`)

| Role | Akses MVP |
|---|---|
| Admin Gudang | Approve, picking, packing, RTS, cetak label; full antrian |
| Leader / SPV | Semua di atas + monitoring penuh |
| Admin QC | Lihat pesanan masuk/keluar/pending/cancel (read-only MVP) |
| Admin RETUR | Belum aktif — modul retur = fase berikut |

Pola mapping role meniru modul manufacture existing (role dari header `system_roles`,
bukan body request).

---

## Keputusan Tercatat

| Keputusan | Status | Keterangan |
|---|---|---|
| Service baru `services/warehouse` | ✅ Diputuskan | Bukan di integration, bukan di manufacture |
| Auto-approve berjadwal | ❌ Tidak dibangun | Approve tetap manual (batch) oleh Admin Gudang |
| Event push realtime | ✅ Diputuskan | Hook `OnOrderUpsert` → POST warehouse; reconciler 60 detik sebagai fallback |
| Cetak resi dari sistem | ✅ Masuk MVP | Bukan dari Seller Center |
| Watermark "terima kasih / unboxing" | 🟡 Fase berikut | Kemungkinan langgar ToS MP; cetakan terpisah, bukan di label resmi |
| Lazada | 🟡 Fase berikut | Tidak ada Lazada client di integration saat ini |
| KiriminAja | 🟡 TBD | Dibutuhkan hanya untuk channel non-marketplace |
| `cmd/labeltest` sebelum build label | ✅ Wajib | Permission app Shopee/TikTok untuk shipping document belum terverifikasi |

---

## Dependensi & Integrasi

- [[Microservices - Integration Service]] — webhook marketplace, sumber order TO_SHIP, endpoint internal ship-batch + labels
- [[External - Accurate]] — bridging akuntansi hilir (settlement → Accurate, tidak berubah)
- [[Microservices - Manufacture Service]] — **tidak tersentuh** oleh WMS; `manufacture_resi` tetap untuk fungsi inbound return-nya sendiri
- [[WH - Management System]] — dok konsep warehouse sebelumnya
- [[WH - Outbound (Sending)]] — logging outbound
- [[WH - Inbound (Receiving)]] — logging inbound / retur

## Dokumen Terkait

- [[Sales - Marketplace Integration]] — konsep bisnis integrasi marketplace
- [[Microservices - Integration Service]] — implementasi backend + proxy API marketplace
- [[DB - Overview and Notes]] — MongoDB & Redis

# WH - Fulfillment Flow & WMS Tinggarjaya

## Deskripsi

*Dokumen ini merangkum alur fulfillment end-to-end gudang Tinggarjaya — dari order masuk
via webhook marketplace hingga serah kurir dan settlement di Accurate. Mencakup arsitektur
`services/warehouse` (MVP), state machine, event architecture, dan gap analysis terhadap
sistem yang sudah berjalan.*

- **Status**: ⚠️ Implemented (ada catatan) — Fase 1 ✅ existing; Fase 2 event+reconciler ✅ Task 4; Fase 3 operasi WMS ✅ (approve/pick/pack/rts/labels/handover/dashboard/produk CRUD/export rekon + jalur cepat APPROVED→RTS); Fase 4 settlement ✅ existing
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

### Fase 3 — Operasi Gudang / WMS (✅ — jalur cepat + gerbang rekon + jalur scan opsional)

#### State Machine `fulfillment_orders`

```
Jalur cepat (utama — alur real gudang, 100+ resi/hari):
NEW → APPROVED → RTS_OK → LABEL_PRINTED → HANDED_OVER
              ↘ RTS_FAILED (retryable → RTS_OK)

Jalur scan (opsional — endpoint pick/pack tetap ada, UI scan sudah dihilangkan):
NEW → APPROVED → PICKING → PACKED → RTS_OK → LABEL_PRINTED → HANDED_OVER
                        ↘ (PICKING boleh langsung → RTS_OK — order lama di
                           tahap scan tidak terdampar)
                                  ↘ RTS_FAILED (retryable → RTS_OK)

NEW / APPROVED → HELD (tahan manual, mencurigakan)
semua status pra-RTS → CANCELLED (dari webhook cancel marketplace)
```

**Gerbang rekon (wajib, kedua jalur)**: order hanya bisa RTS bila datanya
sudah ditarik (`exported_at` terisi via `GET /fulfillment/queue/export`).
Alasan bisnis: rekap rekon diambil dari file unduhan **sebelum** cetak resi —
per batch, sehingga unduhan siang tidak membawa order batch pagi
(`only_new=true` hanya mengambil order yang belum pernah ditarik). RTS order
yang belum ditarik → 422 + daftar `not_exported`.

**Kode packer (`packer_code`, T1/T2)**: tim packer harian/freelance tidak
terdaftar di database employee → dicatat sebagai kode tim, dipilih admin saat
batch cetak label (`POST /fulfillment/labels`), dicap ke semua order batch
yang transisi LABEL_PRINTED. Jalur scan juga bisa mengisinya saat pack
(opsional); label tidak menimpa kode yang sudah ada. Muncul di kolom
"Kode Packer" file export — untuk evaluasi salah kirim/qty kurang per tim.

**Riwayat cetak resi**: menu "Riwayat Cetak Resi" (`GET /fulfillment/labels/history`)
merekam per order: waktu cetak, siapa yang cetak, tim packer, cetak ulang
(history note `"cetak ulang resi"`), serah kurir, dan selisih cetak→serah.
Untuk diagnosis pesanan terlambat: belum dicetak = bottleneck gudang; dicetak
tapi `handed_over_at` kosong = paket tidak ikut pickup kurir.
Tambahan: tombol **Unduh** (xlsx riwayat — kode packer terisi otomatis, bahan
evaluasi per tim; beda dari file rekon yang packer-nya diisi manual) dan tombol
**Cetak Ulang** per baris (juga jalur retry Shopee PROCESSING yang sudah keluar
dari layar Pengemasan).

**Dua file, dua tujuan**: file rekon (`/queue/export`, dibuat sebelum pengemasan,
kolom Kode Packer diisi manual saat bagi tugas) vs file riwayat
(`/labels/history/export`, dibuat setelah cetak, kode packer otomatis).
Unduh rekon dipusatkan di menu **Pengambilan Barang** saja — punya efek samping
gerbang rekon, sehingga dihapus dari Antrian Pesanan agar tidak terpicu dari tab NEW.

#### Alur Operasional (jalur cepat — utama)

Menu FE (bahasa baku): Antrian Pesanan · Pengambilan Barang · Pengemasan ·
Atur Pengiriman · Cetak Resi · Riwayat Cetak Resi · Serah Terima Kurir ·
Master Produk. UI scan barcode dihilangkan (terlalu lambat untuk 100+
resi/hari — keputusan tim gudang); endpoint pick/pack tetap ada.

```
[1. APPROVE — batch]  (menu Antrian Pesanan)
Admin Gudang / Leader / SPV centang N order NEW
POST /fulfillment/approve → status: APPROVED
Order mencurigakan → HELD
        │
        ▼
[2. UNDUH DATA PESANAN — gerbang rekon]  (menu Pengambilan Barang — satu pintu)
GET /fulfillment/queue/export?status=APPROVED&only_new=true
→ xlsx rekap (1 baris per item: nomor pesanan, tanggal, SKU, nama barang,
  qty, toko, expedisi, kode packer, keterangan)
→ order yang ikut terunduh dicap exported_at + exported_by (sekali)
Badge FE tab Disetujui: "Sudah Ditarik" / "Belum Ditarik"
        │
        ▼
[3. PENGEMASAN — CETAK RESI satu klik]  (menu Pengemasan)
Ceklis pesanan (pilih semua) + pilih Tim Packer (T1/T2) → klik "Cetak Resi"
FE otomatis dua langkah:
  POST /fulfillment/rts (untuk yang belum RTS; hanya order exported) → RTS_OK + AWB
  POST /fulfillment/labels {packer_code} → LABEL_PRINTED + resi terbuka
Panel "Hasil Proses Terakhir" bertahan setelah refetch (Buka Resi / Coba Lagi)
Packer tempel resi ke paket sesuai rekap
        │
        ▼
[4. SERAH KURIR]  (menu Serah Terima Kurir) → HANDED_OVER
Audit: menu Riwayat Cetak Resi
```

#### Alur Operasional (jalur scan — opsional)

```
[1. APPROVE — batch] → sama seperti di atas
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
| GET | `/fulfillment/queue` | Antrian order: status, search, toko, tanggal+jam, sort, pagination |
| GET | `/fulfillment/queue/export` | Unduh xlsx rekon; `only_new=true` per batch; cap `exported_at` (gerbang RTS) |
| POST | `/fulfillment/approve` | Approve batch order NEW → APPROVED |
| POST | `/fulfillment/hold` | Tahan order → HELD |
| POST | `/fulfillment/pick` | Konfirmasi picking per order |
| POST | `/fulfillment/pack` | Verifikasi scan barcode SKU + qty → PACKED (+ `packer_code` opsional) |
| POST | `/fulfillment/rts` | RTS batch (gerbang: hanya order ter-export) → proxy integration ship-batch |
| POST | `/fulfillment/labels` | Cetak label + cap `packer_code` batch → proxy integration labels; reprint tercatat |
| GET | `/fulfillment/labels/history` | Riwayat resi tercetak — audit keterlambatan per order |
| GET | `/fulfillment/labels/history/export` | Unduh riwayat xlsx — kode packer otomatis (evaluasi per tim) |
| POST | `/fulfillment/handover` | Konfirmasi serah kurir → HANDED_OVER |
| GET | `/fulfillment/dashboard` | Kartu antrian, resi keluar, cancel, RTS gagal |
| CRUD | `/wms/products` + `/wms/products/import` | Master SKU + lokasi rak + import xlsx |

> Detail request/response lengkap: [[API - Warehouse Service]].

**`services/integration`** (internal, gateway-key) — endpoint baru:

| Method | Path | Fungsi |
|---|---|---|
| POST | `/fulfillment/ship-batch` | Batch ShipPackage (TikTok) + ship_order (Shopee); hasil per-order |
| POST | `/fulfillment/labels` | Ambil shipping document per platform (TikTok sync URL; Shopee async PDF) — deviation dari brief GET: POST agar body array |

---

## Gap Analysis: Blueprint WMS vs Sistem yang Ada

| Modul Blueprint | Status | Keterangan |
|---|---|---|
| Order Marketplace | ✅ Sudah ada | Integration sync TikTok + Shopee, event ke warehouse |
| Approve + Picking + Packing | ✅ Sudah ada | Approve batch; picking/packing = jalur scan opsional (jalur cepat melewatinya) |
| Unduh data rekon (export xlsx) | ✅ Sudah ada | `/queue/export` + gerbang `exported_at` sebelum RTS; `only_new` per batch |
| RTS batch | ✅ Sudah ada | `/fulfillment/rts` → integration ship-batch; dari APPROVED (cepat) atau PACKED (scan) |
| Cetak Resi (label) | ✅ Sudah ada | `/fulfillment/labels` + cap kode packer T1/T2; Shopee async retry |
| Return Reuse/Rework/Reject | ❌ Belum ada | Fase berikut (bukan MVP) |
| Dashboard gudang | ✅ Sudah ada | `/fulfillment/dashboard` |
| Master SKU + lokasi rak | ✅ Sudah ada | `warehouse_products` + import xlsx; ⚠️ barcode/nama sebagian SKU masih kosong |
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

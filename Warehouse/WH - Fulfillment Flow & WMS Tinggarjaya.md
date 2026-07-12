# WH - Fulfillment Flow & WMS Tinggarjaya

## Deskripsi

*Dokumen ini merangkum alur fulfillment end-to-end dari sistem ERP Bharata — mulai dari order
masuk via webhook marketplace hingga barang dikirim dan settlement tercatat di Accurate. Mencakup
analisis gap antara sistem yang sudah berjalan ([[Microservices - Integration Service]]) dengan
blueprint WMS Tinggarjaya yang akan dibangun.*

- **Status**: 🟡 Konsep / Draft — sistem WMS belum diimplementasikan
- **Referensi blueprint**: Blueprint WMS Tinggarjaya (dokumen PDF, Juli 2026)
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
Status: TO_PROCESS
```

### Fase 2 — Auto-Approve / Auto-Ship (✅ Sudah Berjalan)

```
Order status = TO_PROCESS
        │
        ▼
Evaluasi waktu & hari libur (integration service)
        │
        ├─ 00:01–14:59 WIB + bukan hari libur
        │       │
        │       ▼
        │  ShipOrder → API TikTok / Shopee (langsung)
        │  Status → TO_SHIP
        │
        └─ ≥15:00 WIB ATAU hari libur
            (Shopee: juga bila besok libur)
                │
                ▼
           Status = PENDING
           (diproses keesokan harinya)
```

### Fase 3 — Operasi Gudang / WMS (❌ Belum Dibangun)

```
Order status = TO_SHIP
        │
        ▼
[WMS: Modul Order Marketplace]
Daftar order siap proses ditampilkan ke Admin Gudang
(baca dari integration service, filter status TO_SHIP)
        │
        ▼
[WMS: Picking]
Admin Gudang scan lokasi rak → ambil barang
        │
        ▼
[WMS: Packing]
Scan barcode SKU → verifikasi produk & qty
        │
        ▼
[WMS: Shipping — Cetak Resi]
Ambil label dari API marketplace:
  - Shopee  : GET /api/v2/logistics/get_shipping_document
  - TikTok  : GET /fulfillment/packages/{id}/shipping_document
Print label (dengan watermark ucapan terima kasih +
keterangan wajib video unboxing)
        │
        ▼
Trigger ShipOrder → Integration Service
(konfirmasi ke platform bahwa barang siap pickup)
        │
        ▼
Kurir pickup dari gudang
(dijadwalkan dan dikelola oleh platform marketplace)
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

### Fase 5 — Return (⚠️ Sebagian Berjalan)

```
Buyer ajukan retur di platform
        │
        ▼
Status → RETURNED (entity TransactionReturn sudah ada ✅)
        │
        ▼
[WMS: Modul Return] ← ❌ belum dibangun
        │
        ├─ Reuse   — barang masih layak jual, masuk stok kembali
        ├─ Rework  — perlu perbaikan/re-packing sebelum dijual lagi
        └─ Reject  — barang rusak, tidak bisa dijual
```

---

## Gap Analysis: Blueprint WMS vs Sistem yang Ada

| Modul Blueprint | Status | Keterangan |
|---|---|---|
| Order Marketplace | ✅ Sudah ada | Integration service sync TikTok + Shopee otomatis |
| Cetak Resi | ⚠️ Sebagian | `ShipOrder` ada, endpoint ambil *label dokumen* belum |
| Return (data) | ⚠️ Sebagian | Entity + status RETURNED ada, alur Reuse/Rework/Reject belum |
| Report | ⚠️ Sebagian | Summary report ke Accurate ada, laporan internal gudang belum |
| Dashboard gudang | ⚠️ Sebagian | Dashboard order ada di integration, dashboard *gudang* belum |
| Inventory stok produk | ❌ Belum ada | Service `inventory` yang ada adalah untuk **aset IT**, bukan stok produk |
| Master Produk (SKU + lokasi rak) | ❌ Sebagian | SKU/items ada di integration, **lokasi rak** tidak ada |
| Picking | ❌ Belum ada | |
| Packing (scan barcode) | ❌ Belum ada | |
| Shipping (ambil label + pickup) | ❌ Belum lengkap | Perlu tambah endpoint label ke integration service |

---

## Tentang Cetak Resi

Label pengiriman (resi) **di-generate oleh marketplace**, bukan oleh sistem WMS atau
KiriminAja. Contoh: J&T Express pada order Shopee = kurir yang di-assign Shopee.

```
WMS Packing selesai
        │
        ▼
GET /api/v2/logistics/get_shipping_document  (Shopee)
GET /fulfillment/packages/{id}/shipping_document  (TikTok)
        │
        ▼
PDF/PNG label → print ke printer gudang
```

Watermark custom ("TERIMA KASIH / VIDEO UNBOXING WAJIB") diisi sebagai
**catatan pengiriman** di setting toko platform saat ShipOrder dipanggil —
bukan modifikasi label secara langsung.

---

## Peran KiriminAja

KiriminAja **tidak diperlukan** untuk fulfillment order TikTok Shop dan Shopee.

| Channel Order | Logistik | Butuh KiriminAja? |
|---|---|---|
| TikTok Shop | Platform assign kurir + resi | ❌ Tidak |
| Shopee | Platform assign kurir + resi | ❌ Tidak |
| Order Online / Reseller / Non-marketplace | Tidak ada platform yang urus | ✅ Ya |

KiriminAja baru dibutuhkan jika ada channel penjualan di luar marketplace
(Order Online, reseller, WhatsApp order) — channel ini belum ada entity-nya
di `bip-erp` sama sekali (TBD).

---

## Arsitektur WMS — Keputusan Arsitektur

### Konteks yang sudah ada

`services/manufacture` sudah ada sebagai WMS manufaktur dengan kondisi:
- **Gudang Tinggar** (Tinggarjaya) sudah dipetakan di manufacture service — spreadsheet "GUDANG TINGGAR JAYA" → stok barang jadi di `manufacture_db`
- `manufacture_resi` sudah berisi resi TikTok/Shopee via resi-bridge (`sync-tiktok`, `sync-shopee`) — dipakai untuk scan form **Return & Keluar FG** (inbound return dari kurir)
- Stok produk jadi (FG) di Gudang Tinggar sudah dicatat di manufacture

### Keputusan: Extend `services/manufacture` ✅

**Bukan** service baru. Tambahkan modul fulfillment ke manufacture service yang sudah ada.

**Alasan:**

| Faktor | Extend Manufacture | Service Baru |
|---|---|---|
| Stok FG Tinggar | ✅ sudah ada, langsung pakai | ❌ harus sync/duplikasi |
| Resi inbound | ✅ `manufacture_resi` sudah terisi otomatis | ❌ baca dari manufacture via API |
| Kompleksitas infra | ✅ 1 service, 1 DB, 1 deploy | ❌ +1 service, +1 DB, +1 port, +auth |
| Maintenance | ✅ tim yang sama jaga 1 codebase | ⚠️ dua tim harus koordinasi saat ada perubahan domain |
| Cross-service join | ✅ tidak ada — semua data lokal | ❌ fulfillment butuh stok dari manufacture, resi dari manufacture |

**Batas domain tetap dijaga** — modul fulfillment dipisah secara kode (file/handler terpisah), bukan digabung ke handler yang ada:

```
bip-erp/services/manufacture/
├── internal/handler/
│   ├── master_handler.go         ← existing
│   ├── stok_handler.go           ← existing
│   ├── produksi_handler.go       ← existing
│   ├── resi_handler.go           ← existing (resi inbound)
│   │
│   ├── fulfillment_order_handler.go    ← NEW — antrian order TO_SHIP
│   ├── fulfillment_picking_handler.go  ← NEW — picking per lokasi rak
│   ├── fulfillment_packing_handler.go  ← NEW — scan barcode, verifikasi qty
│   ├── fulfillment_shipping_handler.go ← NEW — cetak label, trigger ShipOrder
│   └── fulfillment_return_handler.go   ← NEW — Reuse/Rework/Reject
│
└── internal/models/ (baru di manufacture_db)
    ├── manufacture_rak            ← lokasi rak (gudang Tinggar)
    ├── manufacture_fulfillment_order  ← order antrian picking (snapshot dari integration)
    └── manufacture_return_disposition ← keputusan Reuse/Rework/Reject
```

### Pemisahan tanggung jawab resi

| Data | Service | Keterangan |
|---|---|---|
| `manufacture_resi` | manufacture | Resi **inbound** (return dari kurir → scan form Return & Keluar FG) — sudah jalan |
| Label cetak outbound | integration service | GET `/tiktok/shop/orders/resi-feed` atau Shopee shipping document — ditarik **saat cetak**, tidak disimpan terpisah |

### Route baru di manufacture (prefix `/api/manufacture/fulfillment/*`)

```
GET  /fulfillment/orders          ← order TO_SHIP siap diproses
GET  /fulfillment/orders/:id/picking  ← detail picking (SKU + lokasi rak)
POST /fulfillment/orders/:id/packed   ← konfirmasi packing selesai
POST /fulfillment/orders/:id/ship     ← trigger ShipOrder ke integration
GET  /fulfillment/returns         ← daftar return masuk
POST /fulfillment/returns/:id/disposition  ← Reuse/Rework/Reject
```

### Frontend

Modul fulfillment ditambahkan ke `erp-frontend/src/features/manufacture/` sebagai sub-fitur baru.
Sidebar: tambah item di menu `manufacture` yang sudah ada (bukan module baru).

```
manufacture: [
  { title: "WMS",           url: "/manufacture" },         ← existing
  { title: "Fulfillment",   url: "/manufacture/fulfillment" }, ← NEW
  { title: "KPI",           url: "/manufacture/kpi" },
]
```

---

## Hak Akses (dari Blueprint)

| Role | Akses |
|---|---|
| Admin Gudang | Full |
| Admin QC | Pesanan masuk, keluar, pending, cancel |
| Admin RETUR | Retur masuk, keluar, pending; Reuse/Rework/Reject |
| Leader | Full & Monitoring |
| SPV | Full & Monitoring |

---

## Keputusan Terbuka (TBD)

1. **WMS Tinggarjaya → extend `services/manufacture`** ✅ DIPUTUSKAN
   Modul fulfillment ditambahkan ke manufacture service. Stok FG dan resi inbound sudah ada di sana. Detail arsitektur di bagian "Keputusan Arsitektur" di atas.

2. **Inventory stok produk — siapa sumber kebenaran?**
   → WMS kelola stok sendiri, atau sinkronisasi ke sistem lain?

3. **Lazada** — blueprint menyebut Lazada tapi tidak ada client Lazada di
   integration service. Apakah masuk scope WMS fase ini?

4. **Watermark label cetak** — apakah API marketplace mengizinkan custom note
   saat ShipOrder? Perlu verifikasi per platform.

5. **KiriminAja** — masuk scope setelah WMS stabil, atau paralel?

---

## Dependensi & Integrasi

- [[Microservices - Integration Service]] — webhook langsung marketplace, sumber order (TO_SHIP), endpoint ShipOrder
- [[Microservices - Manufacture Service]] — service tempat modul fulfillment dibangun; stok FG Gudang Tinggar + resi inbound sudah ada di sana
- [[External - Accurate]] — bridging akuntansi hilir
- [[WH - Management System]] — dok konsep warehouse sebelumnya
- [[WH - Outbound (Sending)]] — logging outbound
- [[WH - Inbound (Receiving)]] — logging inbound / retur

## Dokumen Terkait

- [[Sales - Marketplace Integration]] — konsep bisnis integrasi marketplace
- [[Microservices - Integration Service]] — implementasi backend
- [[Microservices - Manufacture Service]] — service host modul fulfillment
- [[DB - Overview and Notes]] — MongoDB & Redis

## Deskripsi

*Rancangan mapping antara **karyawan ICC (Internal Content Creator)** dengan akun TikTok yang mereka kelola: TikTok Shop (toko) dan TikTok Ads (advertiser). Dokumen ini adalah **rancangan implementasi masa depan** — posisi karyawan saat ini tetap ICC; perubahan jabatan ke Account Manager (AM) akan dilakukan terpisah di kemudian hari.*

- **Stack:** Go + Fiber v2 + MongoDB (backend) · Next.js (frontend)
- **Path target:** `bip-erp/services/integration/` (koleksi & endpoint baru)
- **Status:** ⚠️ Implemented (ada catatan) — Phase 1–2 selesai; ada bug akses staff ICC ke endpoint; Phase 3–4 belum
- **Dokumen terkait:** [[Sales - ICC Affiliate Mapping]] · [[Microservices - Integration Service]] · [[Microservices - Insentive Service]]

---

## Latar Belakang

Program ICC saat ini berfokus pada peran kreator/affiliate: karyawan membuat konten TikTok dan mempromosikan produk toko Bharata, lalu mendapat komisi.

Rencana ke depan: setiap karyawan ICC akan menjadi **Account Manager (AM)** yang bertanggung jawab penuh atas:
1. **TikTok Shop account** — mengelola toko (produk, order, ulasan)
2. **TikTok Ads account** — mengelola kampanye iklan (GMV Max, budget, ROAS)

Saat ini ada **16 akun TikTok Shop** yang aktif. Mapping ICC ↔ shop+ads perlu dibuat lebih dahulu agar sistem ERP bisa mengaitkan data performa per-toko/per-iklan ke karyawan yang bertanggung jawab.

### Kondisi Saat Ini

```
ICC Employee → [creator_username]   (affiliate/kreator, sudah ada)
ICC Employee → ?                    (shop + ads account, belum ada)
```

### Target Kondisi (setelah implementasi dokumen ini)

```
ICC Employee → {
  tiktok_creator_usernames[],    ← sudah ada (Sales - ICC Affiliate Mapping)
  tiktok_shop_ids[],             ← BARU: 1 atau lebih toko yang dikelola
  tiktok_advertiser_ids[],       ← BARU: 1 atau lebih akun ads yang dikelola
}
```

> Kardinalitas: **1 karyawan → N toko, N akun ads**. Setiap toko dan setiap advertiser tetap hanya dimiliki satu karyawan aktif (many-to-one dari sisi toko/advertiser).

---

## Entitas yang Terlibat

### Sudah Ada di Sistem

| Entitas | Collection | Service | Keterangan |
|---|---|---|---|
| TikTok Shop | `tt_shop_authorized_shops` | Integration | 16 toko aktif, berisi `id`, `name`, `cipher` |
| TikTok Ads Advertiser | `tt_business_advertisers` | Integration | Akun iklan per-toko, berisi `advertiser_id`, `advertiser_name` |
| ICC Affiliate Username | Konstanta FE | Frontend | Lihat [[Sales - ICC Affiliate Mapping]] |
| Employee Mapping (ADV) | `employee_performance_mappings` | Insentive | Mapping karyawan ADV Leader → advertiser_id + store_id |
| ICC Account Mapping | `icc_account_mappings` | Integration | ✅ Phase 1: Mapping ICC employee → shop_id + advertiser_id |

---

## Model Data: `icc_account_mappings`

```json
{
  "_id": "ObjectID",
  "employee_id":      "BIP-0123",
  "employee_name":    "Aan Budiyanto",
  "tiktok_shop_id":   "7123456789012345678",
  "tiktok_shop_name": "YouGlow.id",
  "tiktok_advertiser_id":   "7234567890123456",
  "tiktok_advertiser_name": "YouGlow Ads",
  "is_active":  true,
  "notes":      "Mulai handle per 2026-08-01",
  "created_by": "ADMIN_001",
  "updated_by": "ADMIN_001",
  "created_at": "2026-07-04T00:00:00Z",
  "updated_at": "2026-07-04T00:00:00Z"
}
```

**Constraints:**
- `tiktok_shop_id` harus ada di `tt_shop_authorized_shops`
- `tiktok_advertiser_id` harus ada di `tt_business_advertisers`
- **1 karyawan boleh handle >1 toko dan >1 ads** — tidak ada unique index pada `employee_id`
- Satu shop hanya boleh di-assign ke satu karyawan aktif — unique index `(tiktok_shop_id, is_active=true)`
- Satu advertiser hanya boleh di-assign ke satu karyawan aktif — unique index `(tiktok_advertiser_id, is_active=true)`

---

## Flow Lengkap

### Flow 1: Admin Membuat Mapping

```
Admin ERP
  → POST /icc/mappings
    body: { employee_id, tiktok_shop_id, tiktok_advertiser_id }
      → Validasi: shop_id ada di tt_shop_authorized_shops?
      → Validasi: advertiser_id ada di tt_business_advertisers?
      → Validasi: shop belum di-assign ke karyawan lain (is_active=true)?
      → Validasi: advertiser belum di-assign ke karyawan lain?
      → Enrich: ambil shop_name dari tt_shop_authorized_shops
      → Enrich: ambil advertiser_name dari tt_business_advertisers
      → Insert: icc_account_mappings
      → Response: 201 Created + data mapping
```

### Flow 2: ICC Dashboard — Staff ICC Lihat Performa Sendiri (⚠️ Ada bug akses, lihat §Catatan Bug)

```
Staff ICC login (position=icc)
  → Halaman /icc/my-accounts (sidebar: "ICC Dashboard")
  → GET /icc/mappings?employee_id=BIP-0123   ← ⚠️ saat ini 403 karena RequireMarketingLeader
    → Returns: { tiktok_shop_id, tiktok_advertiser_id, tiktok_shop_name, ... }

  Tab "Performa Toko":
  → GET /integration/transactions/orders/summary?shop_id=...&time_from=...&time_to=...
  → GET /integration/transactions/orders/dashboard/summary?shop_id=...
    → Returns: total pesanan, revenue, cancel, return + status real-time

  Tab "Performa Iklan":
  → GET /integration/tiktok/business/report/gmv_max/performance/summary
      ?advertiser_id=...&store_id=...&start_date=...&end_date=...
    → Returns: cost, gross_revenue, ROI, orders, CTR, CVR, CPA
```

### Flow 3: Laporan Akuntabilitas AM

```
Insentive Service (cron harian)
  → GET /icc/mappings?is_active=true     (endpoint baru)
  → Untuk setiap mapping:
      → Fetch GMV Ads dari Integration Service (advertiser_id)
      → Fetch GMV Order dari Integration Service (store_id)
      → Hitung KPI AM
  → Upsert incentive_results (DRAFT)
```

### Flow 4: Rotasi/Pergantian AM

```
Admin ERP
  → PATCH /icc/mappings/:id { is_active: false, notes: "Rotasi per 2026-09-01" }
    → Deaktivasi mapping lama
  → POST /icc/mappings { employee_id: BIP-XXXX, tiktok_shop_id: ..., ... }
    → Buat mapping baru untuk karyawan pengganti
```

---

## Otorisasi (RBAC)

Fitur ini khusus untuk tim marketing. Middleware baru `RequireMarketingLeader` perlu dibuat di `shared-library/common/roles.go`:

```go
// RequireMarketingLeader grants access to marketing SPV (Kyura/BeautyHacks) and ADV Leader.
// Used for /icc/mappings endpoints.
var RequireMarketingLeader = validateRole(
    checkRole("kyura",        RoleSupervisor, RoleAdmin),
    checkRole("beauty_hacks", RoleSupervisor, RoleAdmin),
    checkRole("insentive",    RoleInsentiveAdvLeader), // "adv_leader"
    checkRole("integration",  RoleSupervisor, RoleAdmin), // IT admin retain access
)
```

| Role | System Key | Value | Akses |
|---|---|---|---|
| SPV Marketing Kyura | `kyura` | `supervisor` | Lihat semua + assign |
| SPV Marketing BeautyHacks | `beauty_hacks` | `supervisor` | Lihat semua + assign |
| ADV Leader | `insentive` | `adv_leader` | Lihat semua + assign |
| IT Admin (fallback) | `integration` | `supervisor` / `admin` | Lihat semua + assign |

> Catatan: SPV dapat melihat **semua** akun shop dan ads beserta pemegang aktifnya (tidak difilter per departemen).

---

## Endpoint (✅ Phase 1 Diimplementasikan)

Semua endpoint berada di **Integration Service** (`bip-erp/services/integration`), prefix `/icc`.
Semua endpoint dilindungi middleware `RequireMarketingLeader` (lihat §Otorisasi di atas).

### `GET /icc/mappings`

Daftar mapping ICC aktif.

**Query params:**
| Param | Type | Keterangan |
|---|---|---|
| `employee_id` | string | Filter per karyawan |
| `tiktok_shop_id` | string | Filter per toko |
| `tiktok_advertiser_id` | string | Filter per akun ads |
| `is_active` | bool | Default `true` |

**Response 200:**
```json
{
  "data": [
    {
      "id": "...",
      "employee_id":            "BIP-0114",
      "employee_name":          "Aan Budiyanto",
      "tiktok_shop_id":         "7123456789012345678",
      "tiktok_shop_name":       "YouGlow.id",
      "tiktok_advertiser_id":   "7234567890123456",
      "tiktok_advertiser_name": "YouGlow Ads",
      "is_active":   true,
      "notes":       "",
      "created_at":  "2026-07-04T00:00:00Z",
      "updated_at":  "2026-07-04T00:00:00Z"
    }
  ]
}
```

---

### `POST /icc/mappings`

Buat mapping baru.

**Request body:**
```json
{
  "employee_id":          "BIP-0114",
  "employee_name":        "Aan Budiyanto",
  "tiktok_shop_id":       "7123456789012345678",
  "tiktok_advertiser_id": "7234567890123456",
  "notes":                "Mulai handle per 2026-08-01"
}
```

**Response 201:** data mapping yang dibuat.

**Error 409:** jika shop atau advertiser sudah di-assign ke karyawan lain yang aktif.

---

### `PATCH /icc/mappings/:id`

Update mapping (deaktivasi atau ganti catatan).

**Request body (semua opsional):**
```json
{
  "is_active": false,
  "notes": "Rotasi per 2026-09-01"
}
```

**Response 200:** data mapping yang diupdate.

---

### `DELETE /icc/mappings/:id`

Hapus mapping (hanya jika `is_active=false`). Jika masih aktif → 409.

---

### `GET /icc/mappings/available-shops`

Daftar TikTok Shop yang **belum di-assign** ke karyawan manapun (untuk dropdown form assign).

**Response 200:**
```json
{
  "data": [
    { "shop_id": "...", "shop_name": "...", "region": "ID" }
  ]
}
```

---

### `GET /icc/mappings/available-advertisers`

Daftar TikTok Ads advertiser yang belum di-assign.

**Response 200:**
```json
{
  "data": [
    { "advertiser_id": "...", "advertiser_name": "..." }
  ]
}
```

---

## Catatan Bug & Gap (Phase 2)

### Bug: Staff ICC tidak bisa akses endpoint `/icc/mappings`

Semua route `/icc/mappings` dilindungi `RequireMarketingLeader`. Staff ICC (position=icc) **bukan** marketing leader, sehingga request dari halaman ICC Dashboard akan mendapat **403 Forbidden**.

Solusi yang dibutuhkan di Phase 3:
- Tambah route terpisah `GET /icc/mappings/me` dengan middleware yang mengizinkan staff ICC (cek `BIP-Position: icc` atau `system_roles.insentive: icc`)
- Atau: buat middleware `RequireIccAccess` yang menerima marketing leader ATAU icc staff, dengan filter otomatis `employee_id` untuk staff (tidak bisa lihat data orang lain)

### Gap: Isolasi data antar tim (Kyura vs BeautyHacks)

Saat ini mapping tidak menyimpan informasi tim/departemen. SPV Kyura dan SPV BeautyHacks sama-sama bisa melihat **semua** mapping dari kedua tim. Idealnya:
- Tambah field `team` (`"kyura"` | `"beautyhacks"`) di `icc_account_mappings` — diisi otomatis dari `BIP-Department` header si creator
- Endpoint List filter by `team` berdasarkan department si pemanggil

### Perubahan teknis (sudah diimplementasikan)

| Item | Perubahan |
|---|---|
| `ListAllAdvertisers()` | Ditambah `$group` by `advertiser_id` untuk deduplikasi — advertiser yang muncul di beberapa dokumen `tt_business_advertisers` (linked ke beberapa core user) sebelumnya menyebabkan duplicate key error di dropdown |
| Employee lookup di form Assign | Beralih dari `role_system=insentive&role_value=icc` ke `position=icc` (filter berdasarkan jabatan di WorkData); endpoint `/api/employee/list?type=employee` ditambah dukungan param `position` |
| Response format handler | Dihapus wrapping `fiber.Map{"data": ...}` yang menyebabkan `data.data` berupa object bukan array di frontend |

---

## Dependensi & Risiko

| Item | Detail |
|---|---|
| **Data shop** | `tt_shop_authorized_shops` harus sudah terisi lengkap (16 toko) |
| **Data advertiser** | `tt_business_advertisers` harus sudah terisi (sync dari TikTok BC). Dokumen disimpan sebagai nested array `{core_user_id, advertisers: [{advertiser_id, advertiser_name, ...}]}` — endpoint `available-advertisers` menggunakan aggregate+unwind (`$unwind $advertisers` → `$replaceRoot`). ✅ Method `ListAllAdvertisers()` sudah ditambahkan ke `TiktokBusinessRepository`. |
| **Employee data** | `employee_id` dan `employee_name` diisi manual sementara; idealnya dari Employee Service |
| **Kardinalitas shop** | 1 AM dapat handle **lebih dari 1 toko dan lebih dari 1 akun ads** (dikonfirmasi). Unique index hanya pada `(tiktok_shop_id, is_active=true)` dan `(tiktok_advertiser_id, is_active=true)` — tiap toko/advertiser hanya punya 1 pemegang aktif, tapi 1 karyawan bisa punya banyak mapping |
| **Risiko: rotasi** | Jika mapping sering berubah, laporan historis perlu snapshot (siapa handle toko X di bulan Y) — perlu `effective_from`/`effective_to` di fase berikutnya |
| **Belum terintegrasi insentif** | Insentive Service belum konsumsi endpoint ini; integrasi dilakukan saat jabatan ICC → AM resmi berubah |

---

## Fase Implementasi

| Fase | Scope | Status |
|---|---|---|
| **0** | Dok ini — rancangan + endpoint spec | ✅ Selesai |
| **1** | Backend: koleksi + endpoint CRUD `/icc/mappings` + middleware `RequireMarketingLeader` | ✅ Selesai (2026-07-08) |
| **2** | Frontend: sidebar "MARKETING ICC", halaman ICC Management (CRUD assign), ICC Dashboard (performa toko + iklan per staff) | ✅ Selesai (2026-07-09) |
| **3** | Dashboard tim: SPV/Leader lihat performa seluruh staff ICC tim (per departemen Kyura/BeautyHacks); isolasi data antar tim; route `/icc/mappings/me` untuk staff ICC | 🟡 Belum — lihat §Catatan Bug di bawah |
| **4** | Integrasi Insentive Service: hitung KPI AM dari mapping ini | 🟡 Belum |

---

## Hubungan dengan Dokumen Lain

```
Sales - ICC Affiliate Mapping     ← mapping kreator username (affiliate)
Sales - ICC Account Manager Mapping  ← dokumen ini: mapping shop + ads (AM)
    ↕
Microservices - Integration Service  ← sumber data shop & advertiser
    ↕
Microservices - Insentive Service    ← konsumen mapping (fase 4)
    ↕
Sales - Incentive                    ← aturan insentif AM (TBD)
```

## Dokumen Terkait

- [[Sales - ICC Affiliate Mapping]] — mapping kreator username TikTok per anggota ICC
- [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]] — sumber data affiliate
- [[Microservices - Integration Service]] — service target implementasi endpoint baru
- [[Microservices - Insentive Service]] — konsumen data mapping (fase 4, saat jabatan berubah)
- [[Sales - Incentive]] — aturan insentif role ICC & (rencana) AM

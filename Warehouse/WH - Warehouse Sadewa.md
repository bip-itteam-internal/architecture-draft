# WH - Warehouse Sadewa

## Deskripsi

*Gudang **Sadewa** (barang titipan) sebagai warehouse kedua di modul fulfillment, terpisah
dari [[WH - Fulfillment Flow & WMS Tinggarjaya|Tinggar]] tapi **berbagi antrian fulfillment
dan komponen `PackingBoard` yang sama**. Pembeda utamanya: aksi gudang Sadewa yang sensitif
(cetak resi) melewati **lapisan persetujuan Sadewa→Tinggar**, sedangkan operator Tinggar
mengerjakannya langsung. Data aksi disimpan service **manufacture** (collection
`manufacture_sadewa_action`), bukan di service warehouse.*

- **Status**: ⚠️ Implemented (ada catatan) — backend aksi Sadewa (CRUD + approval + audit + index) ✅ penuh; FE cetak-resi mode approval + halaman Persetujuan + retur ✅ terhubung; **catatan**: tab "Retur log" kemungkinan selalu kosong (FE tak pernah menulis `SadewaAction{type:RETUR}` — lihat §Catatan), dan sejumlah komentar kode masih menyebut "scaffold/stub FE-first" yang sudah **stale**.
- **Path repo**: FE `erp-frontend/src/app/(main)/warehouse/sadewa/*` + `src/features/warehouse-sadewa/*`; BE `bip-erp/services/manufacture/sadewa.go`
- **Keputusan user 2026-07-27**: role `admin_gudang_sadewa` = role modul **warehouse**; PPIC & SPV boleh akses penuh menu Warehouse
- **Implementasi service**: [[Microservices - Manufacture Service]] (aksi Sadewa) · [[Microservices - Warehouse Service]] (antrian fulfillment bersama) · **FE**: [[APP - Web ERP]]

---

## Menu & Struktur FE

Modul `warehouse` di sidebar dipecah dua grup lewat field `group` (`erp-frontend/src/components/layout/sidebar-menus.tsx`):

| Grup | Item | Route |
|---|---|---|
| **Warehouse Sadewa** | **Pengemasan** (dulu "Cetak Resi", di-rename agar selaras Pengemasan Tinggar — berbagi `PackingBoard`) | `/warehouse/sadewa/labels` |
| **Warehouse Sadewa** | **Riwayat Cetak Resi** (reuse `LabelHistoryView`, disaring ke aktor `admin_gudang_sadewa`) | `/warehouse/sadewa/label-history` |
| **Warehouse Sadewa** | **Retur** | `/warehouse/sadewa/return` |
| **Warehouse Tinggar** | **Persetujuan** (sengaja di grup Tinggar — approver = otoritas Tinggar) | `/warehouse/sadewa/approvals` |
| **Warehouse Tinggar** | **Toko Gudang Sadewa** (assign toko → Sadewa; grup Tinggar karena pengelola = otoritas Tinggar) | `/warehouse/sadewa-shops` |

> **Catatan rename (sesi 2026-07-27)**: menu Sadewa **"Cetak Resi" → "Pengemasan"**, ikon `Printer` → `Package`, plus judul halaman `PackingBoard` (`title="Pengemasan — Warehouse Sadewa"`) dan pesan `SadewaAccessGuard`. Action type backend `CETAK_RESI` **tidak** diganti (enum, bukan label UI).

**Push modul & filter item** — `src/components/layout/sidebar.tsx`: modul `warehouse` di-push bila `bolehAksesSadewa(...)` true, sehingga admin Sadewa & otoritas Tinggar melihat modul meski tak memegang system role `warehouse` "asli". Filter: grup "Warehouse Sadewa" → `bolehAksesSadewa`; "Persetujuan" → `bolehApproveReturSadewa`; item Tinggar → pemegang role warehouse Tinggar (admin Sadewa **dikecualikan**) atau IT-spv atau pengawas WMS (PPIC/SPV).

---

## Hak Akses (`features/manufacture/akses.ts`)

| Fungsi | Boleh | Dipakai untuk |
|---|---|---|
| `bolehAksesSadewa(systemRoles, itSupervisor)` | IT-spv **atau** `warehouse:admin_gudang_sadewa` **atau** `manufacture:{admin_gudang_fg, ppic, supervisor}` | Buka menu Pengemasan & Retur Sadewa |
| `punyaRoleAdminGudangSadewa(systemRoles.warehouse)` | role `admin_gudang_sadewa` di modul **warehouse** | Bedakan aktor Sadewa (mode approval) vs otoritas Tinggar (cetak langsung) |
| `bolehApproveReturSadewa(manufacture, itSupervisor)` | IT-spv **atau** `manufacture:{ppic, supervisor, admin_gudang_fg}` | Gate menu Persetujuan |
| `punyaRolePengawasWms(manufacture)` | `ppic` / `supervisor` | Akses penuh menu Warehouse (push modul + filter) |

Pencocokan role dinormalisasi (huruf kecil, non-alfanumerik → underscore). Enforcement approver **juga nyata di backend** (`sadewaBolehApprove`, `sadewa.go`) — bukan hanya FE. ⚠️ Komentar `akses.ts` yang menyebut approver "stub FE-first, enforcement menyusul" sudah **stale**.

Untuk matriks akses WMS Tinggar/manufacture lengkap lihat [[Microservices - Manufacture Service]] (bagian "Akses modul WMS").

---

## Alur Cetak Resi Sadewa (approval Sadewa→Tinggar)

```
[Admin Gudang Sadewa]  /warehouse/sadewa/labels  (SadewaApprovalBoard, mode approval)
   ceklis order dari antrian fulfillment bersama (GET /api/warehouse/fulfillment/queue)
   → "Ajukan Cetak Resi"
   → POST /api/manufacture/sadewa/actions {type:CETAK_RESI, source:SADEWA, payload:{orders[]}}
   → backend set status PENDING
        │
        ▼
[Otoritas Tinggar: admin gudang FG / PPIC / SPV]  /warehouse/sadewa/approvals  (tab "Cetak Resi")
   Setujui → POST /sadewa/actions/:id/approve → status APPLIED
   Tolak (wajib alasan) → POST /sadewa/actions/:id/reject {reason} → status REJECTED
        │
        ▼
[Admin Gudang Sadewa]  order jadi state APPROVED ("siap cetak") → cetak resi sendiri via PackingBoard
```

- **Aturan status kunci** (`sadewa.go`): default aksi = `APPLIED`; **hanya** `type==CETAK_RESI && source==SADEWA` yang lahir `PENDING`. Artinya cetak resi oleh **otoritas Tinggar** langsung `APPLIED` (tanpa approval), dan **retur** apa pun langsung `APPLIED`.
- **Source ditentukan server dari JWT** (`sadewaActorContext`): role warehouse `admin_gudang_sadewa` → `SADEWA` (label "Admin Gudang Sadewa"); selain itu → `TINGGAR`. Aktor & label distempel server (anti-palsu).
- **Mode di `PackingBoard`**: aktor Sadewa dapat `gating.mode="approval"` (tombol "Ajukan Cetak Resi" / badge status pengajuan; order PENDING tak bisa dipilih ulang), otoritas Tinggar dapat `gating.mode="direct"` (langsung "Cetak Resi"). `indexCetakResiByOrder` memetakan aksi→state per order (APPROVED > PENDING > REJECTED > NONE).

**Antrian bersama**: halaman Sadewa memakai endpoint fulfillment **warehouse** yang identik dengan Tinggar (`/api/warehouse/fulfillment/{queue,rts,labels,labels/merged}`) — tidak ada antrian khusus Sadewa. Yang membedakan hanya lapisan `sadewa/actions`. Di service warehouse, `admin_gudang_sadewa` **mewarisi izin `admin_gudang`** di `warehouseGuard` (`services/warehouse/fulfillment_ops.go`) agar lolos ke endpoint antrian.

---

## Riwayat Cetak Resi Sadewa (atribusi per gudang)

*Karena antrian & riwayat cetak resi **dikongsi** Tinggar+Sadewa dan history hanya menyimpan `actor` (employee ID, tanpa role/gudang), atribusi per gudang direkam saat cetak lalu dipakai memfilter menu riwayat Sadewa.*

- **Rekam saat cetak** (`markLabelPrinted`, `services/warehouse/fulfillment_ops.go`): pada cetak awal, field top-level `printed_by_role` di dokumen `FulfillmentOrder` di-stempel dari `normRoleWms(id.SystemRoles["warehouse"])` aktor (mis. `admin_gudang` vs `admin_gudang_sadewa`); tiap entry `history` (cetak awal & cetak ulang) juga membawa `actor_role`. Diskriminatornya = **role aktor yang mencetak**, bukan asal order.
- **Filter riwayat** (`fulfillment_label_history.go`): `buildLabelHistoryFilter` menerima query `actor_role` → `filter["printed_by_role"]` (dinormalisasi). Dipakai `GetLabelHistory` **dan** `ExportLabelHistory` (endpoint & guard tetap; `admin_gudang_sadewa` sudah lolos `warehouseGuard`). `labelHistoryRow` menambah `printed_by_role`.
- **FE**: `LabelHistoryView` menerima prop opsional `actorRole`/`title`/`subtitle` (default = perilaku Tinggar tanpa filter). Halaman `/warehouse/sadewa/label-history` (dibungkus `SadewaAccessGuard`) memanggilnya dengan `actorRole="admin_gudang_sadewa"`; `useLabelHistory` meneruskan `actor_role`.
- ⚠️ **Backfill**: resi yang tercetak **sebelum** perubahan ini belum ber-tag `printed_by_role` → tidak muncul di menu Sadewa (riwayat mulai terisi sejak deploy). Dampak minimal karena gudang Sadewa baru. Perlu **REBUILD+redeploy [[Microservices - Warehouse Service|warehouse service]]** agar tag & filter aktif.

---

## Alur Retur Sadewa (langsung, tanpa approval)

- Halaman `/warehouse/sadewa/return` **me-reuse** `GudangBarangJadiView` mode `returOnly` — sumber data & alur **sama persis** dengan retur Tinggar (tab "Return Dari Ekspedisi" Gudang FG).
- Menulis lewat **pipeline transaksi manufacture** (`POST /api/manufacture/transaksi`), **bukan** ke collection `sadewa_action`. Server menstempel `detail.sumberGudang = SADEWA` & `created_by_name` dari JWT (anti-palsu).
- Alasan retur: Rework (Isi berkurang / Segel terbuka) & Reject (Pecah / Tidak sesuai).

---

## Menu Toko Gudang Sadewa (assignment toko → Sadewa)

*Menentukan **toko marketplace mana** yang ditangani Warehouse Sadewa. Assignment ini men-**scope** antrian Pengemasan & feed Retur menu Sadewa agar hanya menampilkan pesanan dari toko-toko tersebut. Sumber daftar toko = Shop Mapping (Config Accurate / `accurate_shops`); di warehouse service hanya disimpan yang di-assign.*

- **Route/FE**: `/warehouse/sadewa-shops` (`app/(main)/warehouse/sadewa-shops/page.tsx`), grup sidebar **Warehouse Tinggar**, gate `bolehKelolaTokoSadewa` (`SadewaAccessGuard`).
- **Pengelola = otoritas Tinggar saja**: staff warehouse Tinggar (`admin_gudang`/`leader`/`spv`) atau pengawas WMS (PPIC/SPV) atau IT-spv. **`admin_gudang_sadewa` DIKECUALIKAN** (penerima, bukan pengelola) — ditegakkan FE (`bolehKelolaTokoSadewa`) **dan** BE (`sadewaShopWriteGuard`, yang sengaja **tidak** mewariskan `admin_gudang_sadewa→admin_gudang`).
- **UX (sejak 2026-07-27)**: tabel menampilkan **hanya toko yang sudah di-assign** (`useSadewaShops`), tiap baris punya tombol **Lepas** (unassign). Menambah lewat tombol **Tambahkan Toko** → popover berisi search + daftar **semua toko** (`useFetchShops`, Config Accurate) yang **belum** di-assign; klik toko → assign. (Sebelumnya: tabel menampilkan **semua** toko dengan toggle "Tandai"/"Ditandai".)
- **BE** (`services/warehouse/sadewa_shops.go`, collection `SadewaShops`): `GET /wms/sadewa-shops` (list, sort `shop_name`), `POST /wms/sadewa-shops` (upsert by `shop_id`+`channel`), `DELETE /wms/sadewa-shops/:shopId?channel=` (unassign). Field `SadewaShop`: `shop_id`, `channel`, `shop_name`, `assigned_by`, `assigned_at`.

---

## Backend & Data

**Route** (`services/manufacture/main.go`, semua di belakang gateway-key):

| Method | Path | Handler |
|---|---|---|
| GET | `/sadewa/actions?type=&status=&source=` | `ListSadewaActions` (sort terbaru, limit 500) |
| POST | `/sadewa/actions` | `CreateSadewaAction` (set PENDING hanya utk CETAK_RESI+SADEWA) |
| POST | `/sadewa/actions/:id/approve` | `ApproveSadewaAction` → APPLIED |
| POST | `/sadewa/actions/:id/reject` | `RejectSadewaAction` → REJECTED + reason |

- **Collection**: `manufacture_sadewa_action` (service manufacture). Index `type + status + metadata.created_at desc` (`ensureSadewaIndexes`, dipanggil saat boot).
- **Enum** (`shared-library/models/manufacture/models.go`): `SadewaActionType {CETAK_RESI, RETUR}` · `SadewaActionStatus {PENDING, APPLIED, REJECTED}` · `SadewaSource {TINGGAR, SADEWA}`.
- **Guard approver** `sadewaBolehApprove`: `manufacture ∈ {admin_gudang_fg, ppic, supervisor}` atau `it ∈ {supervisor, admin}`. Decide hanya untuk CETAK_RESI berstatus PENDING (403 bila bukan otoritas, 409 bila status/type salah). Audit: `CREATE_SADEWA_<type>`, `APPROVE_SADEWA_CETAK_RESI`, `REJECT_SADEWA_CETAK_RESI`.
- Service **warehouse** tidak punya handler/collection Sadewa tersendiri — hanya mengenali role Sadewa untuk otorisasi antrian fulfillment bersama.

---

## Belum Diimplementasikan / Catatan

- ⚠️ **Tab "Retur log" di Persetujuan kemungkinan selalu kosong**: tab itu me-list `SadewaAction{type:RETUR}` dari `manufacture_sadewa_action`, tetapi FE retur (`/sadewa/return`) menulis ke **transaksi manufacture**, bukan ke `/sadewa/actions`. Tidak ada kode FE yang mem-`POST` `type:RETUR` ke `/sadewa/actions`. Backend mendukung tipe RETUR, tapi FE saat ini tak mengisinya — dua jalur data retur yang berbeda. (Fakta dari kode, bukan asumsi.)
- ⚠️ **Komentar stale di kode**: `sidebar-menus.tsx` masih menyebut Sadewa "scaffold; UI & data menyusul" / "belum terintegrasi dengan Tinggar", dan `akses.ts` menyebut approver "stub FE-first" — keduanya tertinggal dari fase awal; kode aktual sudah berbagi `PackingBoard`/antrian dan menegakkan role di backend.
- 🟡 Referensi spec `docs/superpowers/specs/2026-07-27-cetak-resi-sadewa-*` disebut di `PackingBoard.tsx` (tidak diverifikasi di dok ini).

---

## Dependensi & Integrasi

- [[WH - Fulfillment Flow & WMS Tinggarjaya]] — antrian fulfillment, `PackingBoard`, state machine, dan endpoint `/api/warehouse/fulfillment/*` yang dipakai bersama
- [[Microservices - Manufacture Service]] — pemilik collection `manufacture_sadewa_action`, handler & guard aksi Sadewa, matriks akses WMS
- [[Microservices - Warehouse Service]] — antrian/queue, RTS, labels; `warehouseGuard` yang mewariskan izin `admin_gudang` ke `admin_gudang_sadewa`
- [[APP - Web ERP]] — modul FE `warehouse` (halaman `sadewa/*`, fitur `warehouse-sadewa/*`)

## Dokumen Terkait

- [[RUN - Panduan WMS Fulfillment Gudang Tinggarjaya]] — panduan operasional fulfillment (Tinggar; alur pengemasan/cetak resi sejenis)
- [[WH - Management System]] — konsep warehouse

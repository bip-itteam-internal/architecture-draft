## Deskripsi

*Pengelolaan daftar akun TikTok affiliate milik **ICC (Internal Content Creator)** — karyawan internal Bharata yang menjalankan akun affiliate TikTok sebagai bagian dari program insentif perusahaan — dan integrasi data tersebut dengan sistem kepegawaian (Employee Service).*

- **Stack:** Next.js (frontend) · Go + Fiber v2 + MongoDB (backend)
- **Path frontend:** `frontend/src/features/marketing-insight/affiliate/`
- **Path backend (target):** `bip-erp/services/integration/` · `bip-erp/services/employee/` (TBD)
- **Status:** ⚠️ Implemented parsial — mapping berjalan tapi hardcoded di frontend; integrasi Employee Service belum ada

---

## Latar Belakang

Program ICC (Internal Content Creator) adalah insentif bagi karyawan Bharata yang membuat dan mengelola akun TikTok affiliate untuk mempromosikan produk toko. Setiap anggota ICC bisa memiliki 1–2 akun TikTok affiliate.

Data performa affiliate (GMV, komisi, order) sudah ter-capture otomatis dari TikTok API via `affiliate_orders` collection di Integration Service (lihat [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]]). Namun sistem belum bisa membedakan mana order dari kreator **internal (ICC)** vs kreator **eksternal (publik)** — keduanya muncul hanya sebagai `creator_username`.

---

## Implementasi Saat Ini (Hardcoded — ⚠️)

### Lokasi

`frontend/src/features/marketing-insight/affiliate/constants/internal-creators.ts`

### Mekanisme

Daftar username TikTok setiap anggota ICC di-hardcode sebagai konstanta TypeScript:

```ts
export const ICC_MEMBER_ACCOUNTS: Record<string, string[]> = {
  JULIAN:   ["i_skin"],
  FAJAR:    ["akubeauty.id", "akubeautyid"],
  // ... 33 anggota, 41 username total
};

export const INTERNAL_CREATOR_USERNAMES: Set<string> = new Set(
  Object.values(ICC_MEMBER_ACCOUNTS).flat().map(u => u.toLowerCase()),
);

export function isInternalCreator(username: string): boolean {
  return INTERNAL_CREATOR_USERNAMES.has(username.toLowerCase());
}
```

### Penggunaan

Tab **ICC** di halaman Affiliate Performance (`/marketing-insight/affiliate`) memfilter data `SummaryByCreator` menggunakan `isInternalCreator()`:

```
creatorsQuery (API: GET /affiliate/summary/creators)
  → creators[]
    → filter isInternalCreator(username)   ← dari konstanta hardcoded
      → iccCreators[]                      → render tabel tab ICC
```

Kolom tambahan **Nama ICC** menampilkan nama karyawan via `getIccMemberName(username)`.

### Masalah Pendekatan Ini

| Masalah | Dampak |
|---|---|
| Tambah/keluar anggota ICC → harus edit kode + deploy ulang | Effort dev untuk perubahan non-teknis |
| Nama karyawan hardcoded (bukan dari DB karyawan) | Rentan tidak sinkron jika ada perubahan nama/jabatan |
| Tidak ada validasi apakah username masih aktif | Username bisa berubah tanpa sistem mengetahui |
| Tidak bisa dikelola oleh HR/ADV Leader tanpa akses kode | Ketergantungan ke developer |
| Tidak ada audit trail perubahan daftar | Tidak bisa tahu siapa/kapan username ditambah/dihapus |

---

## Rancangan Integrasi dengan Employee Service

### Tujuan

Menggantikan konstanta hardcoded dengan data yang bersumber dari **Employee Service** (HRIS), sehingga daftar ICC dan username TikTok-nya dikelola oleh HR/ADV Leader via ERP, tanpa perlu intervensi developer.

### Pilihan Arsitektur

#### Opsi A — Field `tiktok_usernames` di Employee Service (Direkomendasikan)

Tambahkan field profil sosial media ke data karyawan di Employee Service. Integration Service mengambil daftar ICC via API Employee Service saat query.

```
Employee Service (HRIS)
  └── employee_profiles collection
        └── tiktok_usernames: string[]   ← field baru
        └── is_icc: bool                 ← flag ICC aktif

Integration Service
  └── GET /affiliate/summary/creators?icc_only=true
        └── query Employee Service untuk daftar username ICC
        └── filter creator rows by username match
```

**Kelebihan:** Single source of truth di HRIS; HR bisa kelola langsung via ERP.
**Kekurangan:** Integration Service harus HTTP call ke Employee Service per request (bisa di-cache).

---

#### Opsi B — Koleksi `icc_creators` di Integration Service

Integration Service punya koleksi sendiri yang di-sync dari Employee Service secara periodik.

```
Employee Service  →  (sync cron / webhook)  →  icc_creators (MongoDB, Integration Service)
                                                   └── employee_id: string
                                                   └── employee_name: string
                                                   └── tiktok_usernames: string[]
                                                   └── active: bool
                                                   └── updated_at: time
```

**Kelebihan:** Tidak ada runtime dependency ke Employee Service; query tetap cepat.
**Kekurangan:** Data bisa stale (lag antara perubahan di HRIS dan sync); lebih kompleks.

---

#### Opsi C — Frontend fetch dari API (tanpa backend baru)

Integration Service expose endpoint baru yang membaca mapping dari Employee Service atau config DB, Frontend memanggil endpoint ini menggantikan konstanta.

```
GET /affiliate/icc-creators
  → [{employee_name, tiktok_usernames[]}]
```

**Kelebihan:** Perubahan paling minimal di backend.
**Kekurangan:** Endpoint baru di Integration Service tetap perlu dibuat; Employee Service tetap harus punya data username.

---

### Rekomendasi

**Opsi A** dengan caching di Integration Service:

1. **Employee Service** — tambah field `tiktok_usernames []string` dan `is_icc bool` ke entitas employee. HR/ADV Leader update via form di ERP.
2. **Integration Service** — cache daftar ICC username (TTL 1 jam) dari Employee Service. Gunakan cache untuk filter `SummaryByCreator` dan `ListOrders`.
3. **Frontend** — hapus `internal-creators.ts` setelah backend siap. API sudah return `is_internal: bool` per row.

Alasan memilih Opsi A: konsisten dengan pola yang sudah ada di [[Microservices - Insentive Service]] dimana mapping employee → performance juga bersumber dari Employee Service.

---

## Rencana Implementasi (Bertahap)

### Fase 1 — Employee Service: Tambah Data TikTok ICC (Backend)

**File:** `bip-erp/services/employee/` (path eksak TBD — perlu cek struktur repo)

- Tambah field `tiktok_usernames []string` dan `is_icc bool` ke entitas karyawan
- Tambah endpoint `GET /employees/icc-creators` yang mengembalikan `[{employee_id, name, tiktok_usernames}]` (hanya karyawan `is_icc=true`)
- Tambah validasi: username TikTok harus lowercase, tanpa `@`, unik per sistem
- Seed data awal dari daftar ICC yang ada (33 anggota, 41 username)
- **Test:** unit test entitas + integration test endpoint

### Fase 2 — Integration Service: Cache & Filter ICC (Backend)

**File:** `bip-erp/services/integration/internal/`

- Tambah `icc_cache.go` — in-memory cache daftar ICC username dengan TTL 1 jam, refresh dari Employee Service via HTTP
- Update `affiliate_repo.go` — `SummaryByCreator` dan `ListOrders` terima filter `ICCOnly bool`; join dengan cache username
- Update `affiliate_handler.go` — expose `?icc_only=true` query param
- Update entity `AffiliateCreatorSummary` — tambah field `IsInternal bool` dan `EmployeeName string`
- **Test:** unit test cache TTL + mock Employee Service response

### Fase 3 — Frontend: Konsumsi Data dari API (Frontend)

**File:** `frontend/src/features/marketing-insight/affiliate/`

- Update `use-fetch-affiliate.ts` — tambah fetch `GET /affiliate/icc-creators` untuk tab ICC
- Update `page.tsx` — tab ICC menggunakan data dari API (bukan filter klien)
- Hapus `constants/internal-creators.ts` setelah Fase 2 live
- **Test:** pastikan tab ICC masih render benar setelah konstanta dihapus

### Fase 4 — UI Manajemen ICC di ERP (Frontend + Backend) — TBD

- Form di halaman HR/Employee untuk ADV Leader mengelola `tiktok_usernames` per karyawan
- Audit log perubahan username
- Validasi duplikasi username antar karyawan

---

## Dependensi & Risiko

| Item | Detail |
|---|---|
| **Prereq** | [[Microservices - Employee Service]] harus sudah bisa menerima field `tiktok_usernames` |
| **Risiko: username berubah** | Kreator bisa ganti username TikTok kapan saja; tidak ada notifikasi otomatis dari API TikTok |
| **Akun bersama (by design)** | Satu username bisa dimiliki >1 karyawan ICC (mis. `auraliaa__`, `efcare`, `gumince`); model data harus many-to-many (username → [employee_id]) — bukan unique constraint per username |
| **Risiko: akun tidak aktif** | Kreator yang resign tidak otomatis off dari daftar ICC |
| **Dependency runtime** | Fase 2 menambah HTTP call ke Employee Service; pastikan timeout + fallback (jika Employee Service down, fallback ke cache lama) |

### Catatan Data Saat Ini

Dari daftar ICC 2026-07-04 (33 anggota):
- **41 username** aktif (beberapa anggota punya 2 akun)
- **SATRIO** — username TikTok belum diketahui (TBD)
- **HANIF** — username diverifikasi `zestique_beauty` (bukan `zestique beauty`)
- **BELIA & FADLY** — berbagi akun `auraliaa__` (dikelola bersama — by design)
- **FIRA & IPUL** — berbagi akun `efcare` (dikelola bersama — by design)
- **GUMILANG & FUAD** — berbagi akun `gumince` (dikelola bersama — by design)

---

## Dokumen Terkait

- [[ADR - 0009 Affiliate via Search Seller Affiliate Orders API]] — sumber data affiliate TikTok
- [[Microservices - Insentive Service]] — engine insentif ICC (pay-per-video, scoring)
- [[Sales - Incentive]] — kriteria & aturan insentif ICC
- [[Microservices - Integration Service]] — service yang menyimpan `affiliate_orders`
- [[Microservices - Employee Service]] — target integrasi data karyawan
- [[APP - Web ERP]] — frontend ERP (tab ICC di Affiliate Performance)

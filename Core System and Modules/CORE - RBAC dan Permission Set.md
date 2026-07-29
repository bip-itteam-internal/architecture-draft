## Deskripsi

*Mekanisme hak akses bersama seluruh bip-erp: tiga sumbu (modul, tingkat aksi, cakupan data), paket hak bernama yang menempel pada posisi/jabatan, dan penegakannya di gateway, service, serta frontend. Dokumen ini adalah katalog acuan; keputusan arsitekturnya di [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].*

- **Stack**: Go (fiber middleware) + MongoDB (`master_permission_set`, `master_department`, `system_authentication`) + JWT HS256 sebagai pembawa izin efektif; frontend Next.js membaca klaim yang sama.
- **Path di repo**: `bip-erp/shared-library/common/{permissions.go,catalog_ticket.go,roles.go,position.go}` · `bip-erp/shared-library/models/employee/permission_set.go` · `bip-erp/services/employee/permission_resolve.go` · `bip-erp/services/task-management/{rbac.go,routes.go}` · `erp-frontend/src/utils/access.ts` · `erp-frontend/src/features/hris/master-data/*`
- **Status**: ⚠️ Implemented (ada catatan). Mesin permission-set sudah jalan penuh untuk modul **ticket**; 14 modul lain masih bertumpu pada `system_roles` tier, dan lapisan posisi-memegang-hak belum ada.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| HR / atasan pemberi hak | HRD, supervisor departemen | memilih **paket** per modul untuk sebuah posisi (`admin.assignment.manage`) | Web ERP |
| IT (perancang hak) | Tech Development | menyusun isi paket dari permission granular (`admin.permissionset.manage`) | Web ERP |
| Karyawan | semua divisi | self-service tanpa permission (slip gaji, KPI, insentif, inbox miliknya sendiri) | Web ERP, MyBharata |

- **Tujuan**: HR bisa menjawab "posisi ini boleh apa" tanpa membaca kode; IT bisa mengubah rincian tanpa mengubah kode; karyawan tak pernah kehilangan akses ke datanya sendiri.
- **Pain point**: hari ini jawaban "posisi ini boleh apa" hanya ada di kepala developer, tersebar di `system_roles`, empat pengecualian posisi hardcoded, dan matriks menu di frontend.
- **Aksi utama**: pasang paket ke posisi · baca tabel "Siapa Boleh Apa" · sunting isi paket (IT).

## Fitur (Sudah Diimplementasikan)

**Mesin permission-set (dipakai modul ticket):**
- **Katalog per modul** — `common.RegisterCatalog(module, permissions)` dipanggil saat service start; permission wajib terdaftar sebelum boleh dirakit ke set (mencegah permission yatim). Katalog ticket berisi 15 permission.
- **Set sebagai bundel** — `MasterPermissionSet{key,name,module,permissions[],reach}`, divalidasi `ValidatePermissionSet` (permission harus sepadan modulnya dan terdaftar di katalog).
- **Cakupan (reach)** — `own` / `division` / `all`, dibandingkan dengan `common.HigherReach`.
- **Resolusi saat login** — `resolveEffectivePermissions` menggabungkan permission semua set yang di-assign + satu penanda reach per modul, hasilnya masuk klaim JWT `permissions`. Akun tanpa set menghasilkan klaim kosong sehingga konsumen jatuh ke tier lama.
- **Transport anti-palsu** — gateway membuang seluruh namespace `BIP-*` kiriman klien lalu mengisinya ulang dari klaim JWT (`routes.Reroute`), termasuk `BIP-Permissions` dan `BIP-Position`.
- **Penegakan** — `common.RequirePermission(perm)` (deny-by-default) dan `gate(perm, tierFallback...)` di task-management; kill-switch env `TICKET_PERMISSION_ENFORCEMENT=off`.
- **API katalog untuk frontend** — `GET /api/employee/master/permission-catalog/:module` menyajikan katalog dari Go, dipakai modal permission-set di Master Data.
- **UI kelola set & assign per akun** — `erp-frontend/src/features/hris/master-data/components/{permission-set-form-modal,permission-set-assign}.tsx`.

**Pencocokan posisi (hasil pembenahan 2026-07-29):** `common.KanonPosisi` + `common.PosisiCocok` (`shared-library/common/position.go`) menyatukan aturan pencocokan nama posisi (huruf kecil, non-alfanumerik jadi underscore, exact match atas bentuk kanonik), dipakai `checkPosition` dan `isCostControl`.

## Katalog acuan

**Tangga tingkat**, sama di semua modul. Tingkat tidak otomatis bertingkat; paket yang menggabungkan.

| Kode | Label UI | Artinya |
|---|---|---|
| `view` | Lihat | membuka dan membaca |
| `work` | Kerjakan | membuat dan mengubah |
| `approve` | Setujui | keputusan final (approve/reject/publish) |
| `manage` | Kelola | mengubah aturan, master, dan konfigurasi |

**Modul dan tingkat yang berlaku** (52 permission + 15 ticket = 67):

| Modul | view | work | approve | manage | Pengecualian | Reach |
|---|---|---|---|---|---|---|
| `hris` | ✅ | ✅ | ✅ | ✅ | | own/div/all |
| `payroll` | ✅ | ✅ | ✅ | ✅ | | all |
| `recruitment` | ✅ | ✅ | ✅ | ✅ | | div/all |
| `kpi` | ✅ | ✅ | | ✅ | | own/div/all |
| `training` | ✅ | ✅ | | ✅ | | all |
| `hrdoc` | ✅ | ✅ | | ✅ | | own/div/all |
| `wms` | ✅ | ✅ | ✅ | ✅ | `wms.selisih.create` | all |
| `warehouse` | ✅ | ✅ | ✅ | ✅ | | all |
| `procurement` | ✅ | ✅ | ✅ | ✅ | | all |
| `integration` | ✅ | ✅ | | ✅ | `integration.export` | all |
| `insentive` | ✅ | ✅ | ✅ | ✅ | | own/div/all |
| `ga` | ✅ | ✅ | | ✅ | | all |
| `notification` | ✅ | | | ✅ | `notification.broadcast.send` | all |
| `admin` | ✅ | | | ✅ | `admin.permissionset.manage`, `admin.assignment.manage` | all |
| `ticket` | 15 permission granular (sudah live, tidak diubah) | | | | | own/div/all |

**Self-service tanpa permission**: slip gaji, KPI, insentif, tugas onboarding, dan inbox **milik sendiri** adalah hak bawaan tiap karyawan, ditegakkan BE lewat `employee_id` dari token.

**Contoh paket bawaan** (yang dipilih HR; isi hanya bisa diubah IT):

| Modul | Paket |
|---|---|
| hris | Lihat Tim (view, division) · Penyetuju Pengajuan (view+approve, division) · Pelaksana HR (view+work, all) · Admin HR (semua, all) · Pemantau Pengajuan (view, all) |
| payroll | Lihat · Pelaksana (view+work) · Penyetuju (view+approve) · Admin (semua) |
| wms | Admin Gudang RM · Admin Gudang FG · Admin Produksi · PPIC/Pengawas · Pencatat Selisih (`wms.selisih.create` saja) · Pemantau |

Paket WMS adalah terjemahan langsung matriks tab yang sudah berjalan di `erp-frontend/src/features/manufacture/akses.ts`.

## Belum Diimplementasikan / Catatan

**Status penegakan per service** (scan 950 rute, 2026-07-29). "Telanjang" = rute user-facing tanpa middleware apa pun; rute sistem (`/internal`, `/public`, `/health`, `/webhook`) tidak dihitung.

| Service | Rute | Ber-middleware | Telanjang | Tulis telanjang |
|---|---|---|---|---|
| integration | 318 | 43 RBAC (+29 cache) | 241 | 74 |
| employee | 132 | 35 | 84 | 38 |
| manufacture | 96 | 0 | 95 | 60 |
| recruitment | 92 | 86 | 3 | 1 |
| attendance | 65 | 19 | 45 | 19 |
| task-management | 57 | 54 | 2 | 0 |
| insentive | 33 | 0 | 32 | 16 |
| payroll | 30 | 26 | 3 | 0 |
| warehouse | 29 | 26 | 2 | 1 |
| procurement | 25 | 24 | 1 | 0 |
| inventory | 24 | 3 | 20 | 4 |
| notification | 19 | 0 | 18 | 13 |
| hrd-document | 14 | 13 | 1 | 0 |
| file | 11 | 0 | 10 | 4 |
| tiktok-shop | 4 | 0 | 2 | 0 |

Total **557 rute user-facing tanpa gerbang, 230 di antaranya tulis**.

**Yang belum ada:**
- **Posisi belum jadi entitas ber-identitas.** `master_department.positions` masih `[]string` dan `work_data.position` teks bebas, jadi rename posisi memutus akses tanpa jejak. Prasyarat semua lapisan di atasnya.
- **Posisi belum bisa memegang paket.** `permission_sets` baru ada di `system_authentication` (per akun), belum di posisi; `resolveEffectivePermissions` baru menerima set akun.
- **Frontend belum menyaring dari permission.** `can()` dan `reachFor()` ada di `erp-frontend/src/utils/access.ts` dan klaim `permissions` sudah dibaca `use-auth.ts`, tapi **belum dipanggil di satu tempat pun**; menu masih disaring `system_roles` plus empat pengecualian posisi hardcoded (Cost Control, Security, Personalia, ICC).
- **Katalog 14 modul lain belum ditulis**, jadi belum ada yang bisa di-assign selain ticket.
- **`master_permission_set` dan `system_authentication.permission_sets` belum terdaftar** di [[DB - Data Dictionary]].
- **Layar yang belum ada**: "Hak per Posisi" (HR memilih paket) dan "Siapa Boleh Apa" (tabel baca posisi kali modul).
- **TBD**: pemisahan per area gudang (RM vs FG) sebagai cakupan alih-alih permission; perilaku seragam saat pemakai membuka URL tanpa hak (403 informatif vs pengalihan).

**Aturan kerja**: satu PR sama dengan satu modul, memuat katalog + paket bawaan, gerbang BE + kill-switch env, dan penyaringan FE sekaligus. Urutan: payroll, recruitment, hris, wms, integration (integration terakhir karena terbesar dan paling banyak celah).

## Dependensi & Integrasi

- [[CORE - API Master Gateway]] — menerbitkan JWT dan menstempel `BIP-Permissions`/`BIP-Position`/`BIP-System-Roles` ke setiap request internal; tanpa ini semua sumbu bisa dipalsukan klien.
- [[CORE - SSO Flow]] — konsumen SSO ikut membawa klaim yang sama.
- [[Microservices - Employee Service]] — pemilik master posisi, departemen, permission-set, dan resolusi izin saat login.
- [[Microservices - Task Management Service]] — satu-satunya modul yang sudah menegakkan permission-set (acuan bentuk).
- [[Microservices - Payroll Service]] · [[Microservices - Recruitment Service]] · [[Microservices - Manufacture Service]] · [[Microservices - Warehouse Service]] · [[Microservices - Procurement Service]] · [[Microservices - Integration Service]] · [[Microservices - Insentive Service]] · [[Microservices - Notification Service]] · [[Microservices - Inventory Service]] · [[Microservices - HRD Document Service]] — konsumen katalog per modul.
- [[APP - Web ERP]] — penyaringan menu dan tombol dari klaim `permissions`.
- [[HRIS - Organization Structure]] — posisi dan departemen sebagai master data, termasuk relasi supervisi yang menentukan makna `reach: division`.
- [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] — `company_id` adalah batas data yang **terpisah** dari RBAC; keduanya berlaku bersamaan.

## Dokumen Terkait

- [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] (keputusan & konsekuensi)
- [[ADR - 0003 SSO-only Gateway]] · [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]
- [[DB - Data Dictionary]] · [[DB - Overview and Notes]]
- [[APP - Web ERP]] · [[HRIS - Organization Structure]]

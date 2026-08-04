## Deskripsi

*Mekanisme hak akses bersama seluruh bip-erp: tiga sumbu (modul, tingkat aksi, cakupan data), paket hak bernama yang menempel pada posisi/jabatan, dan penegakannya di gateway, service, serta frontend. Dokumen ini adalah katalog acuan; keputusan arsitekturnya di [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].*

- **Stack**: Go (fiber middleware) + MongoDB (`master_permission_set`, `master_department`, `system_authentication`) + JWT HS256 sebagai pembawa izin efektif; frontend Next.js membaca klaim yang sama.
- **Path di repo**: `bip-erp/shared-library/common/{permissions.go,catalog_ticket.go,roles.go,position.go}` · `bip-erp/shared-library/models/employee/permission_set.go` · `bip-erp/services/employee/permission_resolve.go` · `bip-erp/services/task-management/{rbac.go,routes.go}` · `erp-frontend/src/utils/access.ts` · `erp-frontend/src/features/hris/master-data/*`
- **Status**: ⚠️ Implemented (ada catatan). Lapisan **posisi-memegang-hak sudah live** (migrasi + resolver + layar Hak per Posisi & Siapa Boleh Apa), dan penegakan per-aksi jalan di **ticket**, **payroll**, **procurement**, serta **monitoring**. **finance** baru punya katalog + paket, **belum ada endpoint yang memeriksanya**. Modul lain masih bertumpu pada `system_roles` tier.

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
- **API daftar modul** — `GET /api/employee/master/permission-modules` (dari `common.CatalogModules()`, urut abjad) mengisi pemilih modul di modal. Sengaja dari katalog, bukan konstanta di FE: modul tanpa katalog selalu ditolak `ValidatePermissionSet`, jadi menawarkannya hanya memancing pemakai menyusun paket yang pasti gagal disimpan. Efeknya terbukti saat katalog `finance` mendarat: modulnya langsung muncul di dropdown tanpa satu baris perubahan FE.
- **API pengecualian per-akun** — `GET /api/employee/master/permission-set-exceptions` mengembalikan akun ber-`permission_sets` beserta jabatannya plus `dari_posisi` (paket yang sudah diberikan posisinya). Field terakhir dipakai layar Siapa Boleh Apa menandai pengecualian yang **redundan**, yaitu yang aman dikosongkan tanpa mengubah akses.
- **Pemasangan hak ke posisi** — `PUT /api/employee/master/departments/:key/positions/:positionKey/permission-sets` (gate interim `RequireITSupervisor`). Menyentuh satu posisi saja, tak lewat `ReplaceOne` seluruh dokumen departemen.
- **Backfill paket per-akun DICABUT** (`migratePermissionSetAssignment`, dicabut 2026-07-30). Syaratnya "akun punya role ticket & `permission_sets` kosong", dan "kosong" tak bisa dibedakan dari "sengaja dikosongkan" — akibatnya setiap restart service mengembalikan paket per-akun yang baru dirapikan ke posisi. Paket yang sudah ada tidak dihapus; yang berubah, pengosongan kini bertahan dan karyawan baru mendapat hak dari posisi.
- **UI kelola set & assign per akun** — `erp-frontend/src/features/hris/master-data/components/{permission-set-form-modal,permission-set-assign}.tsx`.

**Tampilan menu per posisi — BUKAN bagian dari RBAC (2026-07-31, branch `feat/menu-per-posisi` + `feat/pengaturan-menu-posisi`, belum merge):**

`master_department.position_items[].menu_hidden` menyimpan url menu yang **disembunyikan** dari sidebar bagi pemegang sebuah jabatan, disetel di **HRIS → Personalia → Pengaturan → Tampilan Menu**. Ditaruh di dokumen ini karena menempel pada objek yang sama dengan `permission_sets` dan gampang tertukar dengannya. **Keduanya berbeda jenis dan jangan disatukan:**

| | `permission_sets` | `menu_hidden` |
|---|---|---|
| Jenis | hak akses | tampilan |
| Arah | memberi | **hanya mengurangi** |
| Ditegakkan | gerbang backend | tidak ditegakkan sama sekali |
| Gerbang tulis | `RequireITSupervisor` | `RequireHRISOrITSupervisor` |
| Berlaku | setelah login ulang | setelah muat ulang halaman |

Aturan yang mengikat: `tampil = (boleh menurut role/izin) DAN (tidak ada di menu_hidden)`. Karena itu ia dijalankan **setelah** seluruh penyaringan izin dan tak pernah bisa memperluas akses; salah setel paling buruk menyembunyikan menu. Rutenya tetap terbuka lewat URL — menyembunyikan menu **bukan keamanan**, konsisten dengan [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]. Gerbang tulisnya sengaja lebih longgar daripada pemasangan paket justru karena ia tak bisa menaikkan hak siapa pun.

Disimpan sebagai daftar yang **disembunyikan**, bukan yang ditampilkan, supaya menu baru otomatis muncul untuk semua posisi alih-alih hilang diam-diam sampai ada yang mendaftarkannya ke 79 jabatan.

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
| `finance` | (live, TIDAK memakai tangga — lihat catatan di bawah) | | | | | all |

> **Penyimpangan rencana vs implementasi (per 2026-07-30).** Katalog `finance` yang sudah live memakai izin **per-objek**, bukan tangga tingkat: `finance.ar.view`, `finance.ar.export`, `finance.ap.view`, `finance.profit.view`, `finance.payout.view`, `finance.kastoko.view`. Bentuk itu masuk akal untuk finance karena tiap objek (piutang, utang, laba, pencairan, kas toko) memang ditinjau orang berbeda, tapi ia belum diselaraskan dengan ADR 0030 yang menetapkan tangga `view/work/approve/manage` plus pengecualian terbatas. **Perlu diputuskan:** perlebar ADR untuk mengizinkan pola per-objek pada modul multi-objek, atau selaraskan finance ke tangga. Selama belum diputuskan, dua pola hidup berbarengan dan itu akan membingungkan modul berikutnya.

**Self-service tanpa permission**: slip gaji, KPI, insentif, tugas onboarding, dan inbox **milik sendiri** adalah hak bawaan tiap karyawan, ditegakkan BE lewat `employee_id` dari token.

**Contoh paket bawaan** (yang dipilih HR; isi hanya bisa diubah IT):

| Modul | Paket |
|---|---|
| hris | Lihat Tim (view, division) · Penyetuju Pengajuan (view+approve, division) · Pelaksana HR (view+work, all) · Admin HR (semua, all) · Pemantau Pengajuan (view, all) |
| payroll | Lihat · Pelaksana (view+work) · Penyetuju (view+approve) · Admin (semua) |
| wms | Admin Gudang RM · Admin Gudang FG · Admin Produksi · PPIC/Pengawas · Pencatat Selisih (`wms.selisih.create` saja) · Pemantau |

Paket WMS adalah terjemahan langsung matriks tab yang sudah berjalan di `erp-frontend/src/features/manufacture/akses.ts`.

> **Modul tier lama (`system_roles`).** Modul di luar tabel katalog di atas masih memakai peran `staff`/`supervisor` langsung dari `system_roles`, digating via `common.Require<Modul>Staff/Supervisor` (`roles.go`). Termasuk **`legal`** — role key baru (Agustus 2026) dengan `RequireLegalStaff`/`RequireLegalSupervisor` + department `legal` di-seed di `DefaultDepartments`, dipakai Register Perizinan & Sertifikasi (lihat [[QA - Register Perizinan & Sertifikasi]]). Modul begini belum punya katalog permission-set, jadi belum bisa dirakit jadi paket per posisi.

## Belum Diimplementasikan / Catatan

**Status penegakan per service** (scan 950 rute, 2026-07-29). "Telanjang" = rute user-facing tanpa middleware apa pun; rute sistem (`/internal`, `/public`, `/health`, `/webhook`) tidak dihitung.

> ⚠️ **Angka di bawah UNDER-COUNT.** Pengecualian `/internal` pada scan itu keliru: prefix tersebut **bukan** batas keamanan. Gateway meneruskan seluruh sub-path `/api/<module>/*` apa adanya dan `Reroute` mengisi sendiri `BIP-Gateway-ID`, jadi rute `/internal/...` bisa dipanggil dari internet oleh siapa pun yang punya token login. Audit 2026-07-30 di employee-service menemukan 3 rute tulis `/internal/auth/*` tanpa gerbang (satu di antaranya menulis `system_roles` apa pun, termasuk `group=admin`) plus 6 rute yang membocorkan peran dan dokumen pribadi. Semuanya ditambal dan ter-deploy hari itu, dan employee-service kini dijaga uji `internal_routes_guard_test.go`. **Scan ulang service lain harus memasukkan `/internal`.** Lihat [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] dan [[LOG - 2026-07-30 Audit Otorisasi Employee Service]].

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

**Sudah selesai sejak dok ini pertama ditulis** (semua terverifikasi live di dev): posisi ber-`key` stabil + `work_data.position_key` + migrasi; posisi bisa memegang paket dan ikut resolusi login (union dengan paket akun, reach tertinggi); layar **Hak per Posisi** & **Siapa Boleh Apa** termasuk daftar pengecualian per-akun; penyaringan menu FE dari klaim `permissions`; katalog **payroll** (5 izin, ditegakkan), **procurement** (7 izin, ditegakkan), **monitoring** (2 izin, ditegakkan), dan **finance** (6 izin, belum ditegakkan).

⚠️ **Pola izin nyata menyimpang dari tangga, dan tangga kini justru minoritas.** Dari lima katalog yang hidup, **hanya `payroll`** yang mengikuti `view/work/approve/manage`. `finance` memakai per-objek baca, `procurement` memakai satu `view` luas plus tulis yang dipecah per objek (`tagihan.save`, `bayar.save`, `po.save`, `master.save`), `ticket` memakai 15 izin granular, `monitoring` cuma `view`+`export`. Yang konvergen di lapangan adalah **satu `view` luas, lalu izin tulis dipecah menurut RISIKO**; `catalog_procurement.go` menuliskan alasannya sendiri — `bayar.save` dipisah dari `tagihan.save` karena "membuat tagihan hanya mengakui utang, membayar memindahkan uang", dan pembayaran tak bisa dibatalkan dari ERP. Keputusan yang tertunda di §TBD bukan lagi "selaraskan finance ke tangga", melainkan **apakah tangga masih layak jadi acuan**.

**Yang belum ada:**
- **Rute `/internal` service lain belum disapu.** employee-service sudah bereskan + dijaga uji, tapi integration, manufacture, attendance, dan insentive belum diperiksa dengan asumsi yang benar (bahwa `/internal` terbuka ke internet). Pertahanan di tepi (gateway menolak `/internal/` dari luar) menutup kelas ini sekaligus, tapi menunggu `erp-frontend` memindahkan `/api/attendance/internal/fingerprint/*` keluar namespace tersebut. Rinciannya di [[ADR - 0031 Prefix internal Bukan Batas Keamanan]].
- **finance belum punya gerbang.** Katalog + 3 paket sudah live dan bisa dipasang ke posisi, tapi **tak satu pun endpoint memeriksanya** — jadi paketnya masih dekoratif. Tak ada `RegisterCatalog(ModuleFinance, ...)` di service pemilik data finance (hanya di employee-service untuk validasi), dan tak ada pemakaian `PermFinance*` di `services/`.
- **Katalog 12 modul lain belum ditulis** (hris, recruitment, kpi, training, hrdoc, wms, warehouse, integration, insentive, ga, notification, admin). `procurement` dan `monitoring` **sudah** — dikoreksi 2026-07-31 setelah ditemukan masih tercatat belum ditulis di sini padahal keduanya hidup di kode.
- **`master_permission_set` dan `system_authentication.permission_sets` belum terdaftar** di [[DB - Data Dictionary]].
- **Empat gate posisi hardcoded belum dicabut** (Cost Control, Security, Personalia, ICC) — menunggu katalog modul yang bersangkutan.
- **Gate `admin.assignment.manage` belum ada**, jadi pemasangan hak ke posisi masih dikunci interim ke `RequireITSupervisor`, bukan ke HR.
- **TBD**: pemisahan per area gudang (RM vs FG) sebagai cakupan alih-alih permission; perilaku seragam saat pemakai membuka URL tanpa hak (403 informatif vs pengalihan); penyelarasan pola izin finance (per-objek) dengan tangga ADR 0030.

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

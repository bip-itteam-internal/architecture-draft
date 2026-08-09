## Deskripsi

*Mekanisme hak akses bersama seluruh bip-erp: tiga sumbu (modul, tingkat aksi, cakupan data), paket hak bernama yang menempel pada posisi/jabatan, dan penegakannya di gateway, service, serta frontend. Dokumen ini adalah katalog acuan; keputusan arsitekturnya di [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].*

- **Stack**: Go (fiber middleware) + MongoDB (`master_permission_set`, `master_department`, `system_authentication`) + JWT HS256 sebagai pembawa izin efektif; frontend Next.js membaca klaim yang sama.
- **Path di repo**: `bip-erp/shared-library/common/{permissions.go,catalog_ticket.go,catalog_menu.go,catalog_hris.go,roles.go,position.go}` · `bip-erp/shared-library/models/employee/permission_set.go` · `bip-erp/services/employee/{permission_resolve.go,menu_terbatas.go,hris_gate.go}` · `bip-erp/services/attendance/hris_gate.go` · `bip-erp/services/task-management/{rbac.go,routes.go}` · `erp-frontend/src/utils/{access.ts,menu-terbatas.ts,posisi.ts}` · `erp-frontend/src/features/hris/master-data/*`
- **Status**: ⚠️ Implemented (ada catatan). Lapisan **posisi-memegang-hak sudah live** (migrasi + resolver + layar Hak per Posisi & Siapa Boleh Apa), dan penegakan per-aksi jalan di **ticket**, **payroll**, **procurement**, **monitoring**, **hris**, **recruitment**, **training**, serta **kpi**. **finance** baru punya katalog + paket, **belum ada endpoint yang memeriksanya**. Modul **`menu`** (menu terbatas) sudah berkatalog + bergerbang tapi **belum merge dan belum berfungsi penuh** (celah akun-tanpa-paket, lihat §Belum Diimplementasikan). Modul lain masih bertumpu pada `system_roles` tier.

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

`master_department.position_items[].menu_hidden` menyimpan url menu yang **disembunyikan** dari sidebar bagi pemegang sebuah jabatan, disetel di dua layar: **HRGA → Pengaturan → Organisasi & Jabatan → Tampilan Menu** (lingkup HRGA) dan **IT → Konfigurasi Sistem → Pengaturan** (seluruh departemen). Ditaruh di dokumen ini karena menempel pada objek yang sama dengan `permission_sets` dan gampang tertukar dengannya. **Keduanya berbeda jenis dan jangan disatukan:**

| | `permission_sets` | `menu_hidden` |
|---|---|---|
| Jenis | hak akses | tampilan |
| Arah | memberi | **hanya mengurangi** |
| Ditegakkan | gerbang backend | tidak ditegakkan sama sekali |
| Gerbang tulis | `RequireITSupervisor` | `RequireHRISOrITSupervisor` |
| Berlaku | setelah login ulang | setelah muat ulang halaman |

Aturan yang mengikat: `tampil = (boleh menurut role/izin) DAN (tidak ada di menu_hidden)`. Karena itu ia dijalankan **setelah** seluruh penyaringan izin dan tak pernah bisa memperluas akses; salah setel paling buruk menyembunyikan menu. Rutenya tetap terbuka lewat URL — menyembunyikan menu **bukan keamanan**, konsisten dengan [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]. Gerbang tulisnya sengaja lebih longgar daripada pemasangan paket justru karena ia tak bisa menaikkan hak siapa pun.

⚠️ **Karena yang disimpan url, memindahkan sebuah menu ke rute baru membatalkan setelannya secara SENYAP** — pencocokannya persis, jadi entri lama jadi basi dan menunya muncul kembali tanpa satu pun galat. Penawarnya `terjemahkanTersembunyi` (`components/layout/sidebar-menu-shape.ts`), yang **mengganti** url lama dengan penerusnya saat dibaca dan **wajib dipakai di kedua sisi**: sidebar yang membaca setelan dan layar Tampilan Menu yang menyuntingnya. Dipakai di satu sisi saja menghasilkan kegagalan yang lebih halus daripada bug aslinya — kedua layar tak sepakat, dan mencentang menu agar tampil tak mengubah apa pun karena penyimpanannya juga mencocokkan url persis sehingga url lamanya tetap tinggal. Detail pemetaan & alasan menu yang pecah tidak dipetakan penuh: [[APP - Web ERP]].

Disimpan sebagai daftar yang **disembunyikan**, bukan yang ditampilkan, supaya menu baru otomatis muncul untuk semua posisi alih-alih hilang diam-diam sampai ada yang mendaftarkannya ke 79 jabatan.

**Menu terbatas — modul `menu` (2026-08-06, branch `feat/oneForAll`, belum merge):**

Whitelist **per akun** untuk satu menu, dipakai pertama kali oleh halaman Laporan Keuangan (`/finance/accounting`) yang memuat posisi keuangan seluruh perusahaan. Keputusan & konsekuensinya di [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]]; yang perlu diketahui di sini adalah **bentuknya berbeda dari izin modul biasa**, dan ia menu-ketiga yang menyentuh sidebar sehingga mudah tertukar dengan dua saudaranya:

| | `permission_sets` | `menu_hidden` | modul `menu` (menu terbatas) |
|---|---|---|---|
| Jenis | hak akses | tampilan | hak akses |
| Menempel pada | posisi (+akun) | posisi | **akun** (+posisi) |
| Arah | memberi | hanya mengurangi | memberi ke yang ditunjuk, **menutup yang lain** |
| Bawaan | deny-by-default | tampil | **terbuka sampai ada yang di-assign** |
| Ditegakkan | gerbang backend | tidak sama sekali | gerbang backend (parsial, lihat ADR) |

Yang membedakannya dari izin modul biasa: **default terbuka**. Selama paketnya belum dipasang ke siapa pun, menu berperilaku persis seperti sebelum fitur ada; begitu ada ≥1 assignment, hanya pemegang paket yang boleh. Fakta "sudah ada yang di-assign" bersifat global, jadi employee-service menghitungnya saat token terbit lalu menempelkan penanda `$menulock.<kunci>` ke klaim **setiap orang** — tanpa penanda itu konsumen tak bisa membedakan "belum aktif" dari "aktif tapi saya tak di-assign". Penandanya sengaja **di luar namespace `menu.`** agar tak terhitung sebagai izin modul, sama alasannya dengan penanda reach.

Batas pemakaian: satu izin + satu paket per menu. Kalau dipakai berlebihan, katalog `menu` akan tumbuh jadi daftar halaman — persis yang ditolak ADR 0030 lewat "satu permission per keputusan akses, bukan per endpoint". Kunci yang ada baru `menu.finance.laporan`.

**Pencocokan posisi (hasil pembenahan 2026-07-29):** `common.KanonPosisi` + `common.PosisiCocok` (`shared-library/common/position.go`) menyatukan aturan pencocokan nama posisi (huruf kecil, non-alfanumerik jadi underscore, exact match atas bentuk kanonik), dipakai `checkPosition` dan `isCostControl`.

**Frontend menyusul (2026-08-09):** pembenahan di atas hanya menyentuh backend; sidebar masih memakai tiga gaya berbeda, dan menu **Payroll** membandingkan string MENTAH (`position !== "Personalia"`) sehingga "personalia" atau "Personalia " melenyapkan menu itu bagi staf Personalia yang sah — tanpa error, tanpa penjelasan. `erp-frontend/src/utils/posisi.ts` (`kanonPosisi`/`posisiCocok`) kini jadi cerminan `KanonPosisi`/`PosisiCocok`, dipakai gerbang Payroll (`sidebar.tsx`), Cost Control (`portal-menu.ts`), dan ICC (`sidebar.tsx`). **Satu pengecualian yang disengaja:** `isSecurityPosition` (`services/manufacture/rbac.go`) dan padanannya di sidebar tetap memakai **substring** `"security"` — menyempitkannya ke exact akan mencabut akses "Security Officer" dkk. yang hari ini memilikinya, jadi itu keputusan bisnis, bukan pembersihan kode. Ditandai di kedua sisi supaya tak "diseragamkan" tanpa keputusan.

**Resolusi paket posisi tak lagi gagal karena ejaan departemen (2026-08-09).** `positionSetKeys` (`services/employee/permission_resolve.go`) mencari dokumen departemen lewat query Mongo yang sama persis huruf demi huruf, sedangkan `/me/menu-hidden` mencocokkannya dengan `EqualFold`. Untuk pasangan (departemen, posisi) yang SAMA, keduanya bisa berbeda pendapat: menu tersembunyi sesuai setelan, tapi paket hak dari jabatan **diam-diam tak terbentuk** sehingga izinnya hilang dan pemakai jatuh ke tier lama tanpa satu pesan pun. Karena `work_data.department` datang dari dropdown, impor lama, dan input manual, beda kapitalisasi/spasi memang terjadi. Keduanya kini memakai satu helper `indeksDepartemen` (`position_assign.go`, saudara `indeksItemPosisi`), dijaga `TestIndeksDepartemenCocokTanpaPeduliHurufDanSpasi`. Ini menyentuh **fondasi** ADR 0030 (hak menempel di posisi), jadi dampaknya bukan kosmetik.

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
| `menu` | (di luar tangga sepenuhnya: satu izin per MENU, bukan per aksi — `menu.finance.laporan`) | | | | | all |

> **Penyimpangan rencana vs implementasi (per 2026-07-30).** Katalog `finance` yang sudah live memakai izin **per-objek**, bukan tangga tingkat: `finance.ar.view`, `finance.ar.export`, `finance.ap.view`, `finance.profit.view`, `finance.payout.view`, `finance.kastoko.view`. Bentuk itu masuk akal untuk finance karena tiap objek (piutang, utang, laba, pencairan, kas toko) memang ditinjau orang berbeda, tapi ia belum diselaraskan dengan ADR 0030 yang menetapkan tangga `view/work/approve/manage` plus pengecualian terbatas. **Perlu diputuskan:** perlebar ADR untuk mengizinkan pola per-objek pada modul multi-objek, atau selaraskan finance ke tangga. Selama belum diputuskan, dua pola hidup berbarengan dan itu akan membingungkan modul berikutnya.

**Self-service tanpa permission**: slip gaji, KPI, insentif, tugas onboarding, dan inbox **milik sendiri** adalah hak bawaan tiap karyawan, ditegakkan BE lewat `employee_id` dari token.

**Contoh paket bawaan** (yang dipilih HR; isi hanya bisa diubah IT):

| Modul | Paket |
|---|---|
| hris | Lihat Tim (view, division) · Penyetuju Pengajuan (view+approve, division) · Pelaksana HR (view+work, all) · Admin HR (semua, all) · Pemantau Pengajuan (view, all) |
| payroll | Lihat · Pelaksana (view+work) · Penyetuju (view+approve) · Admin (semua) |
| wms | Admin Gudang RM · Admin Gudang FG · Admin Produksi · PPIC/Pengawas · Pencatat Selisih (`wms.selisih.create` saja) · Pemantau |

Paket WMS adalah terjemahan langsung matriks tab yang sudah berjalan di `erp-frontend/src/features/manufacture/akses.ts`.

> **Modul tier lama (`system_roles`).** Modul di luar tabel katalog di atas masih memakai peran `staff`/`supervisor` langsung dari `system_roles`, digating via `common.Require<Modul>Staff/Supervisor` (`roles.go`). Termasuk **`legal`** — role key baru (Agustus 2026) dengan `RequireLegalStaff`/`RequireLegalSupervisor` + department `legal` di-seed di `DefaultDepartments`, dipakai Register Perizinan & Sertifikasi (lihat [[QA - Register Perizinan & Sertifikasi]]) — dan **`rnd`** (`RequireRnDStaff`/`RequireRnDSupervisor` + department `rnd` = `R&D Regulatory`), dipakai Register NIE/BPOM/Halal & Papan Pengembangan Produk (lihat [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]]). **`quality`** kini juga menegakkan endpoint (`RequireQualityStaff`/`RequireQualitySupervisor`) untuk register CAPA/Incoming/Batch Release — sebelumnya hanya dipakai gating menu KPI (lihat [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]]). **`procurement`** menegakkan `RequireProcurementStaff`/`RequireProcurementSupervisor` untuk register Kontrak Vendor & Penghematan (di employee-service, di luar service Accurate; lihat [[Microservices - Procurement Service]]). Modul begini belum punya katalog permission-set, jadi belum bisa dirakit jadi paket per posisi. **Supervisor IT** punya super-akses ke keempat register ini di KEDUA lapisan — `Require{Legal,RnD,Quality,Procurement}*` meloloskan `checkRole("it", supervisor/admin)`, dan `erp-frontend/src/proxy.ts` mengecualikan `itSupervisor` dari gerbang `/legal /rnd /quality /procurement` — konsisten dengan sidebar (`itSupervisor ? Object.keys(menus)`). Tanpa keduanya, menu tampil tapi klik memantul ke `/dashboard` dan datanya 403.

## Belum Diimplementasikan / Catatan

**Status penegakan per service** (scan 950 rute, 2026-07-29). "Telanjang" = rute user-facing tanpa middleware apa pun; rute sistem (`/internal`, `/public`, `/health`, `/webhook`) tidak dihitung.

> ⚠️ **Angka di bawah UNDER-COUNT.** Pengecualian `/internal` pada scan itu keliru: prefix tersebut **bukan** batas keamanan. Gateway meneruskan seluruh sub-path `/api/<module>/*` apa adanya dan `Reroute` mengisi sendiri `BIP-Gateway-ID`, jadi rute `/internal/...` bisa dipanggil dari internet oleh siapa pun yang punya token login. Audit 2026-07-30 di employee-service menemukan 3 rute tulis `/internal/auth/*` tanpa gerbang (satu di antaranya menulis `system_roles` apa pun, termasuk `group=admin`) plus 6 rute yang membocorkan peran dan dokumen pribadi. Semuanya ditambal dan ter-deploy hari itu, dan employee-service kini dijaga uji `internal_routes_guard_test.go`. **Scan ulang service lain harus memasukkan `/internal`.**
>
> ⚠️ **Sapuan itu sendiri punya titik buta, dan satu rute lolos (ditemukan & ditambal 2026-08-09).** `internal_routes_guard_test.go` hanya menelusuri prefix `/internal/`, sehingga rute sensitif di AKAR tak pernah diperiksa. `GET /system` (employee-service) terdaftar **tanpa gerbang sama sekali** dan mengembalikan dokumen `system_authentication` apa adanya — termasuk **hash password**, karena field `Password` ber-tag `json:"password"` (bukan `json:"-"` seperti `PIN`), sementara komentar di sebelahnya keliru menyatakan keduanya "skipped on JSON". Siapa pun bertoken login sah bisa menarik hash + `system_roles` karyawan mana pun lewat gateway, lalu menebaknya offline tanpa meninggalkan jejak login. Saudaranya `GET /get/:employee_id/system-auth` sudah bergerbang + meredaksi sejak lama, jadi ini murni rute yang terlewat. Kini bergerbang `RequireHRISOrITStaff` + diredaksi lewat helper `tanpaKredensial` (dipakai kedua rute), dijaga uji `system_auth_response_test.go` — pengujiannya memeriksa daftar tetap dua rute (`/system` dan `/get/:employee_id/system-auth`) dengan memindai `main.go` saja, bukan pemindaian otomatis atas seluruh rute penyaji `system_authentication`, jadi rute baru yang menyajikan koleksi ini tak otomatis tertangkap sampai ditambahkan ke daftar itu. **Pelajaran: penjaga berbasis prefix hanya menjaga prefix itu** — kelas rute sensitif perlu penjaganya sendiri. Lihat [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] dan [[LOG - 2026-07-30 Audit Otorisasi Employee Service]].

| Service | Rute | Ber-middleware | Telanjang | Tulis telanjang |
|---|---|---|---|---|
| integration | 318 | 43 RBAC (+29 cache) | 241 | 74 |
| employee | 132 | 35 | 84 | 38 |
| manufacture | 96 | **seluruhnya (sejak 2026-07-29)** | 0 | 0 |
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

Total **557 rute user-facing tanpa gerbang, 230 di antaranya tulis** (angka scan 2026-07-29; baris `manufacture` sudah dikoreksi di atas, jadi total nyatanya kini **±462 / ±170**).

> **Baris `manufacture` dikoreksi 2026-08-09.** Scan aslinya dijalankan pada hari yang sama dengan mendaratnya `services/manufacture/rbac.go`, sehingga mencatat service itu 0 ber-middleware. Sejak commit tersebut **seluruh** rute WMS bergerbang (`requireTabRead`/`requireTabWrite`/`requireWmsSupervisor`/`requireBatch*`/gerbang Sadewa) — terverifikasi ulang dengan membaca `services/manufacture/main.go`. Baris service lain **belum** diverifikasi ulang dan masih memakai angka scan lama.

**Sudah selesai sejak dok ini pertama ditulis** (semua terverifikasi live di dev): posisi ber-`key` stabil + `work_data.position_key` + migrasi; posisi bisa memegang paket dan ikut resolusi login (union dengan paket akun, reach tertinggi); layar **Hak per Posisi** & **Siapa Boleh Apa** termasuk daftar pengecualian per-akun; penyaringan menu FE dari klaim `permissions`; katalog **payroll** (5 izin, ditegakkan), **procurement** (7 izin, ditegakkan), **monitoring** (2 izin, ditegakkan), dan **finance** (6 izin, belum ditegakkan).

⚠️ **Pola izin nyata menyimpang dari tangga, dan tangga kini justru minoritas.** Dari lima katalog yang hidup, **hanya `payroll`** yang mengikuti `view/work/approve/manage`. `finance` memakai per-objek baca, `procurement` memakai satu `view` luas plus tulis yang dipecah per objek (`tagihan.save`, `bayar.save`, `po.save`, `master.save`), `ticket` memakai 15 izin granular, `monitoring` cuma `view`+`export`. Yang konvergen di lapangan adalah **satu `view` luas, lalu izin tulis dipecah menurut RISIKO**; `catalog_procurement.go` menuliskan alasannya sendiri — `bayar.save` dipisah dari `tagihan.save` karena "membuat tagihan hanya mengakui utang, membayar memindahkan uang", dan pembayaran tak bisa dibatalkan dari ERP. Keputusan yang tertunda di §TBD bukan lagi "selaraskan finance ke tangga", melainkan **apakah tangga masih layak jadi acuan**.

🟡 **Sumbu keempat muncul di `ticket`: hak yang menempel pada OBJEK.** Sebuah space bisa menunjuk `admins`-nya sendiri, dan orang itu boleh menriase, menugaskan, melihat laporan, serta mengubah pengaturan **space tersebut** walau tier-nya `staff` dan walau ia dari departemen lain. Hak ini tak lewat katalog dan tak terlihat di layar **Siapa Boleh Apa**, yang membaca posisi dan paket; satu-satunya jejaknya ada di halaman space dan di audit trail. Alasannya, batasnya, dan hal-hal yang belum diputuskan ada di [[ADR - 0038 Hak Per-Objek Admin Space Task Management]]. **MERGED ke `main` 2026-08-06** (bip-erp PR #1027 + erp-frontend PR #818); belum diuji lewat gateway dan prod belum di-deploy.

**Yang belum ada:**
- **Rute `/internal` service lain belum disapu.** employee-service sudah bereskan + dijaga uji, tapi integration, manufacture, attendance, dan insentive belum diperiksa dengan asumsi yang benar (bahwa `/internal` terbuka ke internet). Pertahanan di tepi (gateway menolak `/internal/` dari luar) menutup kelas ini sekaligus, tapi menunggu `erp-frontend` memindahkan `/api/attendance/internal/fingerprint/*` keluar namespace tersebut. Rinciannya di [[ADR - 0031 Prefix internal Bukan Batas Keamanan]].
- **finance belum punya gerbang.** Katalog + 3 paket sudah live dan bisa dipasang ke posisi, tapi **tak satu pun endpoint memeriksanya** — jadi paketnya masih dekoratif. Tak ada `RegisterCatalog(ModuleFinance, ...)` di service pemilik data finance (hanya di employee-service untuk validasi), dan tak ada pemakaian `PermFinance*` di `services/`. Gerbang pertama yang mendarat di endpoint akuntansi justru milik modul **`menu`**, bukan `finance` — dan hanya pada `/accounting/balance-sheet`; lihat butir berikutnya.
- ⚠️ **Menu terbatas BELUM berfungsi sebagaimana dimaksud — jangan dinyalakan dulu.** Penanda kunci hanya menumpang pada klaim yang sudah tak kosong, sehingga akun tanpa permission-set tak pernah menerimanya dan tetap lolos lewat fallback lama. Celah itu semula diduga kosong; **2026-08-06 terbukti tidak** — token yang terbit hari itu untuk akun `finance: supervisor` + `it: supervisor` + `group: admin` sama sekali tak membawa klaim `permissions`. Akibatnya memasang paket membuka halaman bagi yang ditunjuk tetapi **tidak menutupnya** bagi yang lain. Prasyarat perbaikannya ada di [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]]: **langkah pertama sudah dikerjakan 2026-08-09** (fallback task-management kini per-modul, penutupan akun luar jadi cabang eksplisit, predikatnya dipusatkan di `common.KlaimMemuatIzinModul`), tetapi **langkah kedua belum** — penjaga `gabungPenandaMenu` masih terpasang, jadi celah akun-tanpa-paket tetap terbuka dan fitur ini tetap jangan dinyalakan.
- **Gerbang backend menu terbatas juga sengaja parsial.** Hanya `/accounting/balance-sheet` yang digerbang (satu-satunya endpoint eksklusif halaman itu); `/profit-loss` & `/account-balance` dibiarkan terbuka karena halaman posisi SPV, Tax, dan Cost Control ikut memakainya. Jadi ini kontrol **menu**, bukan segel data.
- **Katalog 8 modul lain belum ditulis** (hrdoc, wms, warehouse, integration, insentive, ga, notification, admin). `procurement` dan `monitoring` **sudah** — dikoreksi 2026-07-31 setelah ditemukan masih tercatat belum ditulis di sini padahal keduanya hidup di kode.

	**`training` sudah, sejak 2026-08-09** — modul KEDUA yang dipecah keluar dari kategori sidebar `hris`, dan batasnya paling jelas dari semuanya karena ia sudah punya service sendiri (`learning`). 21 rute digerbang: 6 master (jenis pelatihan & pelatih), 7 operasional, 8 baca. Tier default memberi ketiga tier SELURUH izin — bukan kelalaian, melainkan cermin kenyataan bahwa semua rute tulis (termasuk master) digerbang `RequireHRISStaff` yang meloloskan staff; pembedaan yang berguna karena itu ada di PAKET (“Pelatihan: Pelaksana” tanpa master), bukan di tier. Sakelar: `TRAINING_PERMISSION_ENFORCEMENT` + `TRAINING_TIER_FALLBACK`.

	⚠️ **Delapan rute baca learning-service sebelumnya TIDAK bergerbang sama sekali** — termasuk `GET /training/history/:employeeId`, yang berarti siapa pun bertoken sah bisa menarik riwayat pelatihan karyawan mana pun. Memetakannya ke `training.view` MENYEMPITKAN akses; diverifikasi aman karena seluruh pemanggilnya di FE ada di layar HR (`features/hris/training/*`), sedangkan self-service karyawan memakai grup `/me` yang terpisah. Untuk rute-rute ini `fallback` kill-switch-nya `nil`, jadi mematikan enforcement mengembalikannya terbuka persis seperti sebelum fitur ada.

	✅ **`kpi` sudah, sejak 2026-08-09 — sekaligus menegakkan `reach: division` untuk pertama kalinya di luar task-management.** Ini menutup prasyarat yang sebelumnya membuat modul ini ditunda. Bentuk katalognya SENGAJA berbeda: seluruh 13 titik pemeriksaan KPI memanggil SATU fungsi (`RequireKPIDepartmentRBAC`), dan yang diputuskan di sana bukan tingkat aksi melainkan **departemen mana yang boleh dilihat**. Karena itu katalognya hanya memuat `kpi.view`, dan pembedaan antar-orang dilakukan lewat REACH — dua paket bawaan (`KPI: Divisi Sendiri` / `KPI: Semua Divisi`) memuat izin yang sama dan hanya berbeda reach. Menambah `kpi.work`/`kpi.manage` sekarang akan melahirkan izin yang tak satu pun titik kode memeriksanya.

	Penegakannya disisipkan di titik cekik itu sehingga **nol call site berubah**, dan akun tanpa paket `kpi` jatuh ke tier lama apa adanya. Cakupan kini dibaca dari **struktur organisasi** (`BIP-Supervised-Departments`) alih-alih peta `deptKeyToNames` yang di-hardcode. Keputusan itu diambil setelah **pengukuran ke data dev**: dari 20 pemegang akses KPI, 18 lolos lewat cabang `hris` staff/supervisor yang berlaku lintas-departemen (dipetakan ke `ReachAll`, tak berubah sedikit pun), dan hanya **2** lolos semata lewat peta modul tanpa ditandai supervisor di `work_data` — ditangani sebagai perbaikan data, bukan dengan melonggarkan aturan.

	⚠️ Kehalusan yang dikunci uji: **`hris: admin` TIDAK disebut cabang pertama** gerbang lama (`checkRole` hanya menyebut staff & supervisor), jadi reach-nya `division`, bukan `all`. Menaikkannya akan MELEBARKAN hak — arah yang lebih berbahaya daripada penyempitan karena tak bergejala.


	✅ Yang tetap dikerjakan untuk KPI: **`GET /kpi/dashboard` ditutup** (2026-08-09). Rute itu tak punya cek akses sama sekali padahal menyajikan agregat SELURUH karyawan aktif — nama, foto, departemen, jabatan, dan skor KPI. Nol pemanggil di frontend, jadi menggerbangnya (`RequireHRISStaff`) tak memutus siapa pun; rute yang terlewat, bukan yang dipakai — pola sama dengan `GET /system`.

	**`recruitment` sudah, sejak 2026-08-09** — modul PERTAMA yang dipecah keluar dari kategori sidebar `hris`, sesuai §Decision yang menetapkan batas modul mengikuti service/domain dan bukan sidebar. Pendorongnya keluhan nyata: staf Personalia ikut melihat seluruh menu Rekrutmen karena keduanya digerbang satu key role `system_roles.hris` yang sama. Katalognya memakai tangga penuh (`view`/`work`/`approve`/`manage`) yang mencerminkan PERSIS gerbang hari ini — `isHR` → view+work, `isHRSupervisor` → approve, `isHRAdmin` → manage — sehingga 77 rute digerbang tanpa mengubah hak siapa pun. Dua rute sengaja TIDAK dipetakan karena lintas-modul: `POST /requisitions` (pengajunya atasan di luar HR) dan persetujuan final hire (meloloskan Secretary yang tak punya tier `hris`).

	⚠️ **Pemecahan katalog saja BELUM mengubah perilaku.** Selama fallback tier hidup, pemegang `hris` tier apa pun tetap melihat menu Rekrutmen walau posisinya tak dipasangi paket — itulah yang membuat penyalaan aman, dan sekaligus alasan staf Personalia MASIH melihatnya. Penghentiannya adalah **fase kedua** yang baru boleh dijalankan setelah paket dipasang ke posisi berhak: env `RECRUITMENT_TIER_FALLBACK=off` di recruitment-service, plus menghapus baris fallback `recruitment.view` di `erp-frontend/src/utils/menu-permission.ts`. Dibuat env supaya peralihan fase tak menuntut deploy kode dan bisa dikembalikan seketika bila ada posisi yang terlewat.

`hris` sudah berkatalog (`hris.view` saja) DAN sejak 2026-08-09 ditegakkan pada 12 rute BACA di employee-service (10) dan attendance-service (2), dengan kill-switch `HRIS_PERMISSION_ENFORCEMENT` dan saringan FE (`perm: "hris.view"` pada enam menu). Aturan keputusan izinnya (klaim vs fallback tier) tinggal SATU kali di `common.IzinHrisEfektif` karena hris adalah modul pertama yang ditegakkan di dua service — menyalinnya akan mengulang kelas bug yang dicatat [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]]. Irisan TULIS sengaja belum digarap; alasan lengkapnya di `shared-library/common/catalog_hris.go`: sebagian gerbang tulis menyimpang dari tangga, dan memetakannya sekarang akan mencabut hak staf HR tanpa satu pun galat.

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
- [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]] (modul `menu`, penanda kunci, batas penegakannya)
- [[ADR - 0003 SSO-only Gateway]] · [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]
- [[DB - Data Dictionary]] · [[DB - Overview and Notes]]
- [[APP - Web ERP]] · [[HRIS - Organization Structure]]

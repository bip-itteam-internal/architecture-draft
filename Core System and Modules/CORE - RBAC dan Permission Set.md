## Deskripsi

*Mekanisme hak akses bersama seluruh bip-erp: tiga sumbu (modul, tingkat aksi, cakupan data), paket hak bernama yang menempel pada posisi/jabatan, dan penegakannya di gateway, service, serta frontend. Dokumen ini adalah katalog acuan; keputusan arsitekturnya di [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]].*

- **Stack**: Go (fiber middleware) + MongoDB (`master_permission_set`, `master_department`, `system_authentication`) + JWT HS256 sebagai pembawa izin efektif; frontend Next.js membaca klaim yang sama.
- **Path di repo**: `bip-erp/shared-library/common/{permissions.go,catalog_ticket.go,catalog_menu.go,catalog_hris.go,catalog_payroll.go,catalog_legal.go,roles.go,position.go,tier_fallback.go}` · `bip-erp/services/employee/{legal_gate.go,hris_gate.go,peran_dari_jabatan.go}` · `bip-erp/shared-library/models/employee/permission_set.go` · `bip-erp/services/employee/{permission_resolve.go,menu_terbatas.go,hris_gate.go}` · `bip-erp/services/attendance/{hris_gate.go,payroll_gate.go}` · `bip-erp/services/payroll/rbac.go` · `bip-erp/services/task-management/{rbac.go,routes.go}` · `erp-frontend/src/utils/{access.ts,menu-permission.ts,menu-terbatas.ts,posisi.ts}` · `erp-frontend/src/components/layout/{sidebar-menus.tsx,portal-menu.ts,modul-aktif.ts}` · `erp-frontend/src/features/hris/master-data/*`
- **Status**: ⚠️ Implemented (ada catatan). Lapisan **posisi-memegang-hak sudah live** (migrasi + resolver + layar Hak per Posisi & Siapa Boleh Apa), dan penegakan per-aksi jalan di **ticket**, **payroll**, **procurement**, **monitoring**, **hris**, **recruitment**, **training**, **kpi**, **kaskecil**, serta **legal** (yang terakhir ⚠️ belum merge). **finance** punya katalog + 5 paket dan menunya sudah bertanda izin, tetapi **belum ada endpoint yang memeriksanya**. Modul **`menu`** (menu terbatas) **sudah merge** namun **belum berfungsi penuh** (celah akun-tanpa-paket, lihat §Belum Diimplementasikan). Modul lain masih bertumpu pada `system_roles` tier.
- **FASE DUA dimulai 2026-08-09 di dev**: `recruitment` dan `kpi` tak lagi menolong akun tanpa paket (`RECRUITMENT_TIER_FALLBACK=off`, `KPI_TIER_FALLBACK=off`), setelah 17 jabatan dipasangi paket padanannya. `hris` sengaja tetap di fase satu. Lihat §Fase dua.
- **Katalog yang benar-benar terdaftar per 2026-08-09 ada 11**, terverifikasi dari `origin/main` (berkas `shared-library/common/catalog_*.go` + titik `common.RegisterCatalog`): `finance`, `hris`, `kaskecil`, `kpi`, `menu`, `monitoring`, `payroll`, `procurement`, `recruitment`, `ticket`, `training`. `legal` belum ada di `main`. Daftar ini yang mengisi `GET /api/employee/master/permission-modules`, jadi ia juga yang menentukan modul mana yang bisa dipilih HR saat menyusun paket.

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

**Menu terbatas — modul `menu` (2026-08-06, ✅ MERGED ke `main`; ⚠️ tetap jangan dinyalakan, lihat §Belum Diimplementasikan):**

> Terverifikasi di `origin/main` 2026-08-09: `shared-library/common/catalog_menu.go` ada, didaftarkan di `services/employee/main.go:128`, dan gerbangnya hidup di `services/integration/main.go:1169` (`accountingRoute.Get("/balance-sheet", httpDelivery.RequireMenuLaporanKeuangan(), …)`) beserta `menu_gate_test.go`. Dok ini sempat menyebutnya "belum merge"; yang masih benar adalah **belum berfungsi penuh**, dan itu dua hal berbeda. Sudah-merge justru menaikkan taruhannya: kodenya kini hidup di produksi, jadi yang menahan fitur ini tinggal keputusan untuk tidak memasang paketnya ke siapa pun.

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

**Paket hak kini ikut menentukan KATEGORI sidebar, bukan cuma isinya (2026-08-09).** Sebelum ini kategori lahir semata dari `system_roles`, sehingga paket yang menempel di posisi hanya bisa **menyempitkan** di dalam modul yang sudah dibuka role — tak pernah **membuka** modul. Itu memotong premis ADR 0030 separuh jalan, dan Finance memperlihatkannya paling telanjang: **16 dari 18 akun Finance tak punya satu pun `system_role`**, jadi memasang paket "Finance: Lihat" ke jabatan AR Staff tak akan mengubah apa pun karena kategori FINANCE-nya sendiri tak pernah muncul. Aturannya kini di `erp-frontend/src/components/layout/modul-aktif.ts` (`kunciModulAktif`), diuji tanpa merender sidebar. Cakupannya sempit dengan sendirinya — hanya modul yang punya katalog **dan** punya kategori sidebar yang bisa terpengaruh, hari ini `finance` dan `procurement`; `kpi`, `recruitment`, `training`, dan `payroll` menumpang di kategori lain sehingga tak memunculkan apa pun (dikunci uji). Dua penanda sengaja tak dihitung sebagai izin modul: penanda reach dan penanda menu terkunci — yang terakhir menumpang di klaim SEMUA orang, jadi menghitungnya akan memberi kategori kepada tiap pemakai.

**Peran sistem diturunkan dari jabatan untuk modul yang belum berkatalog (2026-08-09).** Mekanisme terpisah, sengaja: `manufacture` dan `insentive` sudah punya pembedaan per pekerjaan yang halus dan sudah ditegakkan (matriks WMS + cerminnya di `rbac.go`; nilai `insentive` yang sudah berbentuk pekerjaan), sehingga yang rusak bukan aturannya melainkan **datanya**. Tabel `services/employee/peran_dari_jabatan.go` mengisi `system_roles` yang KOSONG dari (departemen, jabatan) saat token terbit, tak pernah menimpa, dinilai per modul. Keputusan, batas, dan daftar jabatan yang sengaja tak dipetakan: [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]. **Ini jembatan** — dicabut begitu kedua modul berkatalog.

## Fase dua

Tiap modul berkatalog melewati dua fase. **Fase satu** memasang gerbang tanpa mencabut apa pun: akun yang belum punya paket jatuh ke tier `system_roles`-nya. **Fase dua** mematikan fallback itu, dan sejak saat itu hanya pemegang paket yang boleh — inilah yang membuat "posisi X boleh menu Y" benar-benar berlaku.

Sakelar per modul, semuanya env sehingga peralihan fase tak menuntut deploy dan bisa dikembalikan seketika:

| Modul | Sakelar | Status dev |
|---|---|---|
| `recruitment` | `RECRUITMENT_TIER_FALLBACK` | **off** sejak 2026-08-09 |
| `kpi` | `KPI_TIER_FALLBACK` | **off** sejak 2026-08-09 |
| `training` | `TRAINING_TIER_FALLBACK` | masih fase satu (service `learning` belum terpasang di dev) |
| `hris` | `HRIS_TIER_FALLBACK` | sengaja fase satu — modul dasar seluruh tim HR |

Dua sakelar terakhir menuntut penegaknya tinggal di shared-library (dipakai employee & attendance untuk `hris`), jadi keduanya dipusatkan di `shared-library/common/tier_fallback.go`: dibaca sekali per proses, bawaannya menyala, dan **hanya nilai `off` yang mematikan** sehingga salah ketik menyisakan akses alih-alih mencabutnya. Keputusannya dipisah jadi bentuk murni ber-parameter (`izinHrisEfektifDenganFallback`, `kpiRBACDenganFallback`) supaya kedua fase bisa diuji tanpa menyentuh env proses yang global.

**Prasyarat yang dipenuhi lebih dulu:** 17 jabatan yang hari ini lolos gerbang lama dipasangi paket padanannya di `master_department.position_items`, diturunkan dari pengukuran ke data dev — bukan dari tebakan. Lima jabatan HR dipasangi versi **sempit** sesuai tugasnya (Personalia hanya `hris_pelaksana`; Recruitment & Onboarding `recruitment_pelaksana` + `hris_lihat`; Training Officer `training_admin` + `kpi_semua` + `hris_lihat`; Culture & Industrial `training_pelaksana` + `hris_lihat`; HRD Supervisor tetap penuh), sisanya **setara** sehingga nol perubahan.

> ⚠️ **PENGUKURAN ULANG 2026-08-09 malam: pemasangan paket itu TIDAK ADA di data dev, dan sakelarnya jadi ranjau.** Query langsung ke `employee_db` (`master_department.position_items[].permission_sets` + `system_authentication.permission_sets`) menemukan **hanya 6 posisi dan 1 akun** yang berpaket, dan **tak satu pun memuat `hris_*`, `recruitment_*`, `kpi_*`, maupun `training_*`** — isinya semata `ticket_*`, `payroll_*`, `finance_*`. Yang terpasang: HRD Supervisor & Personalia (payroll+ticket), Tech Development Supervisor, Direktur, Finance Supervisor, Manufacturing Supervisor. Katalognya sendiri sehat: ke-36 paket ter-seed di `master_permission_set`, termasuk dua paket pengajuan yang baru.
>
> Yang membuatnya berbahaya bukan doknya melainkan **keadaan setengah jalan**: `docker-compose.dev.yml` SUDAH menyetel `KPI_TIER_FALLBACK: "off"` (baris 115) dan `RECRUITMENT_TIER_FALLBACK: "off"` (baris 396), tetapi container yang BERJALAN belum membawa env itu (`printenv` di recruitment-service, employee-service, dan attendance-service: kosong). Env dibaca saat container DIBUAT, jadi selama tak ada yang me-recreate, fase dua belum benar-benar menyala dan tak ada yang rusak. **Begitu container berikutnya dibuat — deploy rutin sekalipun — Rekrutmen dan KPI akan menolak SEMUA ORANG di dev**, sebab sakelarnya menyala sementara tak seorang pun memegang paketnya.
>
> Dua hal yang harus dipilih sebelum recreate berikutnya: pasang paketnya lebih dulu, atau cabut kedua baris env itu. Perlu diperiksa juga apakah pemasangan 17 jabatan itu pernah dijalankan lalu hilang (mis. tertimpa seed atau migrasi), karena kalau ya, memasang ulang saja tak cukup.
>
> **Konsekuensi untuk `hris`, dan ini yang menyangkut halaman Pengajuan**: karena nol posisi memegang paket `hris_*`, `HRIS_TIER_FALLBACK=off` hari ini akan mencabut SELURUH akses hris untuk semua orang, bukan cuma pengajuan — kontrak, resign, cuti, laporan kehadiran, semuanya. Union gerbang pengajuan sengaja diikat ke sakelar yang sama, jadi fase dua pengajuan **tak bisa dinyalakan sendirian** tanpa memecah sakelarnya. Itu keputusan yang tertunda, bukan yang sudah diambil.

⚠️ **Memasang paket "setara" saja melestarikan masalah yang memicu pekerjaan ini.** Personalia, Recruitment & Onboarding, Training Officer, dan Culture & Industrial semuanya ber-`hris:staff`, jadi paket setaranya identik — dan staf Personalia tetap melihat menu Rekrutmen. Nilai fase dua ada di penyempitannya, bukan di pemasangannya.

⚠️ **Dua jabatan sengaja DITUNDA** karena pemegangnya memegang hak jauh di atas jabatannya: `Finance/Junior Accountant` (1 dari 8 pemegang ber-`hris:admin`+`finance:admin`) dan `Kesekretariatan/Personal Assistant` (`group:admin` + `it:supervisor`). Memasang paket lebih dulu hanya mengabadikan anomali itu jadi aturan.

⚠️ **Pencabutan fallback di FE ditulis sebagai nilai `tolak`, BUKAN dengan menghapus barisnya.** `bolehMenu` memperlakukan izin tanpa entri sebagai "modulnya belum berkatalog" dan **meloloskannya**, jadi menghapus baris fallback justru membuka menu untuk semua orang — kebalikan dari yang dimaksud. Jebakan itu dikunci uji di `menu-permission.test.ts`.

**Biaya transisinya nyata:** paket menempel di token, jadi selama satu siklus token (72 jam) siapa pun yang belum login ulang kehilangan sementara menu modul yang fase duanya menyala.

## Katalog acuan

**Tangga tingkat**, sama di semua modul. Tingkat tidak otomatis bertingkat; paket yang menggabungkan.

| Kode | Label UI | Artinya |
|---|---|---|
| `view` | Lihat | membuka dan membaca |
| `work` | Kerjakan | membuat dan mengubah |
| `approve` | Setujui | keputusan final (approve/reject/publish) |
| `manage` | Kelola | mengubah aturan, master, dan konfigurasi |

**Modul dan tingkat yang berlaku** (52 permission + 15 ticket = 67; `legal` menambah 3 di luar hitungan awal ADR 0030 karena modulnya sendiri belum ada saat ADR ditulis, dan `hris` menambah 2 izin berlingkup pengajuan pada 2026-08-09):

| Modul | view | work | approve | manage | Pengecualian | Reach |
|---|---|---|---|---|---|---|
| `hris` | ✅ | ✅ | | ✅ | `hris.pengajuan.view`, `hris.pengajuan.approve` | own/div/all |
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
| `legal` | ✅ | ✅ | | ✅ | | all |
| `ticket` | 15 permission granular (sudah live, tidak diubah) | | | | | own/div/all |
| `finance` | (live, TIDAK memakai tangga — lihat catatan di bawah) | | | | | all |
| `kaskecil` | (live & ditegakkan; 8 izin, `approve` DIPECAH EMPAT — lihat catatan di bawah) | | | | | own/div/all |
| `menu` | (di luar tangga sepenuhnya: satu izin per MENU, bukan per aksi — `menu.finance.laporan`) | | | | | all |

> **Modul `kaskecil` — satu-satunya yang TANPA fallback tier, dan itu disengaja** (`shared-library/common/catalog_kaskecil.go`, ditegakkan `services/procurement/main.go` + `kas_gate_test.go`). Delapan izin: `view`, `transaksi.save`, `pengajuan.save`, empat izin persetujuan terpisah (`approve.atasan`/`approve.aset`/`approve.finance`/`approve.direksi`), dan `master.save`. Dua hal yang membedakannya dari seluruh modul lain di tabel ini, keduanya layak dibaca sebelum menggarap modul berikutnya:
>
> - **`KasKecilTierDefault` SELALU mengembalikan kosong.** ADR 0030 menetapkan "fallback tier wajib", tapi kewajiban itu lahir untuk melindungi akses yang **sudah dipakai orang**. Kas kecil belum punya satu pun pemakai lama, jadi tak ada yang perlu dilindungi dan yang tersisa hanya risikonya: memberi hak membelanjakan uang karena seseorang kebetulan supervisor di modul lain adalah cara termudah melahirkan pengeluaran yang tak seorang pun merasa memberikannya. Seluruh aksesnya **wajib ditugaskan eksplisit** lewat permission-set. Ini bukan pelanggaran ADR melainkan pembacaan yang benar atas alasannya, dan preseden untuk setiap modul baru yang lahir setelah permission-set ada.
> - **`approve` dipecah empat, bukan disatukan.** Blueprint menaruh empat pihak pada tingkat nominal berbeda; menyatukannya berarti siapa pun yang boleh menyetujui belanja kecil otomatis boleh menyetujui yang bernilai puluhan juta. Contoh konkret kenapa tangga empat-kata-kerja tak selalu cukup.
>
> Izin memposting jurnal **sengaja belum ada**: arah jurnal masih menunggu keputusan Finance (ERP berhenti di pencatatan, atau menulis ke Accurate), dan menyediakan izinnya sekarang berarti menjanjikan kemampuan yang belum diputuskan bentuknya. Konsep bisnisnya di [[Finance - Kas Kecil dan Pengajuan Budget]].

> **Penyimpangan rencana vs implementasi (per 2026-07-30).** Katalog `finance` yang sudah live memakai izin **per-objek**, bukan tangga tingkat: `finance.ar.view`, `finance.ar.export`, `finance.ap.view`, `finance.profit.view`, `finance.payout.view`, `finance.kastoko.view`. Bentuk itu masuk akal untuk finance karena tiap objek (piutang, utang, laba, pencairan, kas toko) memang ditinjau orang berbeda, tapi ia belum diselaraskan dengan ADR 0030 yang menetapkan tangga `view/work/approve/manage` plus pengecualian terbatas. **Perlu diputuskan:** perlebar ADR untuk mengizinkan pola per-objek pada modul multi-objek, atau selaraskan finance ke tangga. Selama belum diputuskan, dua pola hidup berbarengan dan itu akan membingungkan modul berikutnya.

**Self-service tanpa permission**: slip gaji, KPI, insentif, tugas onboarding, dan inbox **milik sendiri** adalah hak bawaan tiap karyawan, ditegakkan BE lewat `employee_id` dari token.

**Contoh paket bawaan** (yang dipilih HR; isi hanya bisa diubah IT):

| Modul | Paket |
|---|---|
| hris | **Yang benar-benar di-seed** (`DefaultHrisSets`, lima): HRIS: Lihat (view) · HRIS: Pelaksana (view+work) · HRIS: Admin (view+work+manage) · HRIS: Pemantau Pengajuan (`pengajuan.view`) · HRIS: Penyetuju Pengajuan (`pengajuan.view`+`approve`). Semuanya reach `all` |
| payroll | Lihat · Pelaksana (view+work) · Penyetuju (view+approve) · Admin (semua) |
| wms | Admin Gudang RM · Admin Gudang FG · Admin Produksi · PPIC/Pengawas · Pencatat Selisih (`wms.selisih.create` saja) · Pemantau |

Paket WMS adalah terjemahan langsung matriks tab yang sudah berjalan di `erp-frontend/src/features/manufacture/akses.ts`.

**Modul `legal` — berkatalog penuh sejak 2026-08-09** (branch `feat/legal-permission-set`, ⚠️ **belum merge**). Tiga izin (`legal.view` 6 rute GET, `legal.work` 6 rute POST/PUT, `legal.manage` 3 rute DELETE) + tiga paket (Lihat · Pelaksana · Admin, reach `all`), digerbang `gateLegal` di employee-service dengan fallback tier di tiap rute dan kill-switch `LEGAL_PERMISSION_ENFORCEMENT=off`. Empat hal yang membedakannya dari modul sebelumnya, dan layak dibaca sebelum menggarap modul berikutnya:

- **Digerbang PENUH sejak PR pertama**, bukan dicicil seperti `hris`. Bukan keberanian melainkan ukuran: 15 rute CRUD dengan hanya dua tingkat gerbang lama bisa dibuktikan setara satu per satu, sementara `hris` punya 79 gerbang di tiga service dan sebagian menyimpang dari tangga.
- **Tanpa `approve`, dan itu keputusan.** Tak ada satu pun rute yang menyetujui apa pun; `review_status` kontrak dan `status` dispute adalah field biasa yang ikut di `PUT` yang sama dengan nama dan tanggal. Memberi `approve` arti berarti memecah `PUT` dan mencabut sesuatu yang hari ini boleh dilakukan staf. Ditahan uji supaya tak ditambahkan tanpa keputusan.
- **Super-akses supervisor IT ditambahkan sebagai UNION, bukan cabang `else`.** Fallback tier hanya membaca `system_roles["legal"]`, sedangkan kedua gerbang lama meloloskan `it` supervisor/admin tanpa memeriksa peran legal sama sekali. Tanpa cabang ini mereka justru kehilangan akses tepat saat gerbang menyala — dan lihat sensus di bawah untuk kenapa itu berarti seluruh modul padam, bukan sebagian.
- ⚠️ **Pelajaran uji yang mahal**: tabel kesetaraan gerbang lama vs izin baru sempat **tidak** menangkap satu pelebaran akses, karena tiruan gerbang lama di dalam uji ikut memangkas spasi persis seperti kode yang diujinya. `checkRole` membandingkan nilai header **apa adanya**, jadi `"  staff  "` hari ini ditolak. **Acuan yang meniru kesalahan yang diujinya tidak membuktikan apa pun** — tulis acuannya dari sumber aslinya, jangan dari kode yang sedang ditulis.

> **Modul tier lama (`system_roles`).** Modul di luar tabel katalog di atas masih memakai peran `staff`/`supervisor` langsung dari `system_roles`, digating via `common.Require<Modul>Staff/Supervisor` (`roles.go`). Termasuk **`rnd`** (`RequireRnDStaff`/`RequireRnDSupervisor` + department `rnd` = `R&D Regulatory`), dipakai Register NIE/BPOM/Halal & Papan Pengembangan Produk (lihat [[QA - R&D Regulatory (Registrasi & Pipeline Produk)]]). **`quality`** kini juga menegakkan endpoint (`RequireQualityStaff`/`RequireQualitySupervisor`) untuk register CAPA/Incoming/Batch Release — sebelumnya hanya dipakai gating menu KPI (lihat [[QA - Quality Operasional (CAPA, Incoming, Batch Release)]]). **`procurement`** menegakkan `RequireProcurementStaff`/`RequireProcurementSupervisor` untuk register Kontrak Vendor & Penghematan (di employee-service, di luar service Accurate; lihat [[Microservices - Procurement Service]]). Modul begini belum punya katalog permission-set, jadi belum bisa dirakit jadi paket per posisi. **Supervisor IT** punya super-akses ke register-register ini di KEDUA lapisan — `Require{Legal,RnD,Quality,Procurement}*` meloloskan `checkRole("it", supervisor/admin)`, dan `erp-frontend/src/proxy.ts` mengecualikan `itSupervisor` dari gerbang `/legal /rnd /quality /procurement` — konsisten dengan sidebar (`itSupervisor ? Object.keys(menus)`). Tanpa keduanya, menu tampil tapi klik memantul ke `/dashboard` dan datanya 403. `legal` **sudah keluar dari daftar ini** (lihat blok di atas), tapi gerbang lamanya tetap hidup sebagai fallback dan super-akses ITnya dipertahankan di lapisan izin.

> ⚠️ **Katalog tak membuka menunya sendiri, dan ini sistemik.** Sidebar memilih grup menu dari `Object.keys(systemRoles)` dan `proxy.ts` menggerbang rute dari `roles.<modul>`. Artinya memberi seseorang **paket** sebuah modul TANPA `system_roles.<modul>` tetap tak membuka menunya — berlaku sama untuk `hris`, `procurement`, dan kini `legal`. Sumbu "modul mana yang ada untuk saya" masih `system_roles`; permission-set baru mengatur "boleh apa di dalamnya". Menyatukan keduanya adalah keputusan arsitektur tersendiri, bukan pekerjaan migrasi satu modul.

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

⚠️ **Pola izin nyata menyimpang dari tangga, dan tangga kini justru minoritas.** Dari **11 katalog** yang hidup di `main` (angka ini dulu tertulis "lima" dan sudah tertinggal), **hanya `payroll` dan `recruitment`** yang mengikuti `view/work/approve/manage` penuh. `finance` memakai per-objek baca, `procurement` memakai satu `view` luas plus tulis yang dipecah per objek (`tagihan.save`, `bayar.save`, `po.save`, `master.save`), `ticket` memakai 15 izin granular, `monitoring` cuma `view`+`export`, `kpi` cuma `kpi.view` yang dibedakan lewat **reach**, `hris` mulai dari `view` saja lalu menyusul `work`+`manage` tanpa `approve`, `kaskecil` memecah `approve` jadi empat, dan `menu` di luar tangga sepenuhnya. Yang konvergen di lapangan adalah **satu `view` luas, lalu izin tulis dipecah menurut RISIKO**; `catalog_procurement.go` menuliskan alasannya sendiri — `bayar.save` dipisah dari `tagihan.save` karena "membuat tagihan hanya mengakui utang, membayar memindahkan uang", dan pembayaran tak bisa dibatalkan dari ERP. Keputusan yang tertunda di §TBD bukan lagi "selaraskan finance ke tangga", melainkan **apakah tangga masih layak jadi acuan**.

🟡 **Sumbu keempat muncul di `ticket`: hak yang menempel pada OBJEK.** Sebuah space bisa menunjuk `admins`-nya sendiri, dan orang itu boleh menriase, menugaskan, melihat laporan, serta mengubah pengaturan **space tersebut** walau tier-nya `staff` dan walau ia dari departemen lain. Hak ini tak lewat katalog dan tak terlihat di layar **Siapa Boleh Apa**, yang membaca posisi dan paket; satu-satunya jejaknya ada di halaman space dan di audit trail. Alasannya, batasnya, dan hal-hal yang belum diputuskan ada di [[ADR - 0038 Hak Per-Objek Admin Space Task Management]]. **MERGED ke `main` 2026-08-06** (bip-erp PR #1027 + erp-frontend PR #818); belum diuji lewat gateway dan prod belum di-deploy.

**Yang belum ada:**
- **Rute `/internal` service lain belum disapu.** employee-service sudah bereskan + dijaga uji, tapi integration, manufacture, attendance, dan insentive belum diperiksa dengan asumsi yang benar (bahwa `/internal` terbuka ke internet). Pertahanan di tepi (gateway menolak `/internal/` dari luar) menutup kelas ini sekaligus, tapi menunggu `erp-frontend` memindahkan `/api/attendance/internal/fingerprint/*` keluar namespace tersebut. Rinciannya di [[ADR - 0031 Prefix internal Bukan Batas Keamanan]].
- **finance belum punya gerbang.** Katalog + paket sudah live dan bisa dipasang ke posisi, tapi **tak satu pun endpoint memeriksanya** — jadi penegakannya berhenti di frontend. Tak ada `RegisterCatalog(ModuleFinance, ...)` di service pemilik data finance (hanya di employee-service untuk validasi), dan tak ada pemakaian `PermFinance*` di `services/`. Gerbang pertama yang mendarat di endpoint akuntansi justru milik modul **`menu`**, bukan `finance` — dan hanya pada `/accounting/balance-sheet`; lihat butir berikutnya. Data finance dilayani **integration-service**, yang justru service dengan rute telanjang terbanyak, jadi menutupnya bersinggungan dengan pekerjaan itu.

	**Paketnya tak lagi dekoratif di sisi menu (2026-08-09).** Ketujuh halaman finance sudah menegakkan izin katalognya lewat `FinanceModuleGuard` sejak katalognya dibuat, tapi **menunya tak pernah ditandai** — sehingga menu tampil untuk orang yang halamannya menolak, kegagalan yang baru terlihat setelah diklik. Kini tiap menu memakai izin yang halamannya sudah pakai (`/finance` & `/finance/gl` & `/finance/anggaran` → `accounting.view`, `/finance/ar` → `ar.view`, `/finance/ap` → `ap.view`, `/integration/payouts` → `payout.view`, `/integration-accurate/kas-toko` → `kastoko.view`). Nilai fallback-nya menyalin `useFinanceFallback` apa adanya, **termasuk dua pintu tambahan yang mudah terlewat**: Accounts Payable juga milik `procurement`, Kas Toko juga milik `integration_accurate` lewat `accurateBridgingMenus`. Tanpa keduanya penandaan ini akan mencabut menu dari tim yang halamannya tetap membuka untuk mereka.

	**Dua paket per AREA ditambahkan (2026-08-09): `finance_ar` & `finance_ap`.** Tangga lihat/pelaksana/admin hanya menyatakan SEBERAPA DALAM, bukan BAGIAN MANA — dan AR Staff serta Account Payable adalah dua jabatan berbeda dengan kedalaman yang sama, sehingga paket tersempit yang tersedia (`finance_view`) sudah memuat piutang, utang, dan dashboard divisi sekaligus. Keduanya sengaja tanpa `accounting.view`: izin itu membuka Jurnal & Buku Besar, Anggaran OPEX, dan Ringkasan Divisi. Ini contoh konkret bahwa **tangga saja tak cukup menjawab "menu sesuai jabatan"** — bahan untuk TBD "apakah tangga masih layak jadi acuan".

	Kedelapan jabatan Finance kini dipasangi paket; anomali `finance:admin` pada seorang Junior Accountant tertutup dengan sendirinya karena paket mengalahkan tier.
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

**`payroll` kini ditegakkan di DUA service juga** (2026-08-09, [#1126](https://github.com/bip-itteam-internal/bip-erp/pull/1126) + erp-frontend [#922](https://github.com/bip-itteam-internal/erp-frontend/pull/922), merged). Master **Perlakuan Kehadiran** (`GET`/`PUT /payroll-status-treatment`) datanya tinggal di attendance-service karena bersanding dengan status kehadiran, tapi yang diputuskan di sana adalah keputusan penggajian. Sebelumnya ia digerbang `isHRDept`, **satu-satunya gerbang departemen yang tersisa di seluruh permukaan payroll**, dan ganjil di dua arah sekaligus: staf payroll yang sah tertolak karena departemennya Finance, sementara siapa pun di HR bisa mengubah aturan penggajian tanpa peran payroll apa pun. Kini `payroll.view` untuk baca dan `payroll.manage` untuk tulis.

Tiga hal yang membedakannya dari irisan-irisan sebelumnya, dan ketiganya jadi preseden:

- **Gerbang lama TIDAK diunionkan.** Beda dari izin pengajuan yang mempertahankan gerbang lamanya sebagai union, di sini keputusannya memang berhenti menilai dari departemen; mempertahankannya akan membatalkan maksudnya. `isHRDept` tinggal sebagai perilaku kill-switch (`PAYROLL_PERMISSION_ENFORCEMENT=off`).
- **Karena itu perpindahannya BUKAN nol-perubahan, dan dampaknya diukur lebih dulu ke data dev** sesuai patokan ADR 0030: **13 orang mendapat akses baca** (9 Tech Development, 3 Kesekretariatan, 1 Finance) dan **1 orang kehilangan** (staf dept HR yang akunnya tak punya `system_roles.hris` sama sekali). Pelebarannya konsisten dengan yang sudah mereka pegang: ketiga belasnya sudah punya `payroll.view` lewat tier untuk rute payroll-service, artinya sudah bisa melihat run dan gaji karyawan yang jauh lebih sensitif daripada master ini. Kedua arah dikunci uji supaya tak ada yang "merapikannya" tanpa mengulang pengukurannya.
- **Tulis dipisah dari baca, dan pemisahannya nyata.** `payroll.manage` hanya dimiliki tier admin sementara `payroll.view` dimiliki staff ke atas, jadi dari 13 orang itu hanya satu yang bisa mengubah, dan ia memang sudah bisa mengubah konfigurasi BPJS dan pajak hari ini. Di FE, tab-nya terbuka bagi pemegang `payroll.view` tapi sakelar dan tombol Simpan digerbang `bolehUbahPayroll` — menutup catatan "belum selesai" yang sudah lama ditulis di `bolehPayroll`.

Konsekuensi pemeliharaannya: `izinPayrollEfektif` NAIK ke `common.IzinPayrollEfektifDari`, dan payroll-service mendelegasikan ke sana alih-alih menyimpan salinan kedua. Syaratnya sama persis dengan hris di bawah, dan sejak sekarang **berlaku sebagai aturan**: begitu sebuah modul ditegakkan di service kedua, aturan keputusan izinnya pindah ke `common` pada PR yang sama.

`hris` sudah berkatalog (`hris.view` saja) DAN sejak 2026-08-09 ditegakkan pada 12 rute BACA di employee-service (10) dan attendance-service (2), dengan kill-switch `HRIS_PERMISSION_ENFORCEMENT` dan saringan FE (`perm: "hris.view"` pada enam menu). Aturan keputusan izinnya (klaim vs fallback tier) tinggal SATU kali di `common.IzinHrisEfektif` karena hris adalah modul pertama yang ditegakkan di dua service — menyalinnya akan mengulang kelas bug yang dicatat [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]]. **Irisan TULIS menyusul 2026-08-09** — `hris.work` + `hris.manage`, 11 rute (9 work: kontrak 3, resign 4, kuota cuti 1, koreksi presensi 1; 2 manage: master hari libur).

Peringatan yang ditinggalkan penulis irisan pertama kini dikunci uji. `POST /holiday` adalah master data yang secara tangga masuk `manage`, TAPI hari ini digerbang `RequireHRISStaff` yang meloloskan staff — memetakannya ke `manage` sambil membiarkan tier staff tanpa `manage` akan mencabut hak staf HR tanpa satu pun galat. Jalan keluarnya bukan menahan `manage`, melainkan menaruh pembedaannya di tempat yang benar: **tier memberi ketiganya** (cermin gerbang hari ini, jadi nol perubahan akses) dan **paket yang membedakan** — "HRIS: Pelaksana" sengaja tanpa `manage`. Pola sama dipakai `training`, yang gerbang tulisnya juga seragam di `RequireHRISStaff`. Uji penjaganya: `TestHrisTierDefaultMemberiManageKeStaffDemiHoliday`.

`hris.approve` POLOS tetap TIDAK ada di katalog, tapi alasannya berubah bentuk sejak irisan ketiga di bawah: dulu karena tak satu pun rute hris digerbang persetujuan terpisah, kini karena persetujuan yang ADA berlingkup pengajuan, bukan hris secara umum. Izin polos akan menjanjikan kewenangan atas persetujuan hris apa pun yang lahir kelak tanpa satu pun titik kode memeriksanya. Dikecualikan dan disengaja: dua rute `/internal/transaction/*` (dipanggil HRIS orchestrator) dan seluruh gerbang `RequireHRISOrIT*` yang lintas-modul — memetakannya ke `hris.*` akan memutus staf IT yang sah memakainya.

**Irisan KETIGA — halaman Pengajuan, 2026-08-09** (bip-erp [#1123](https://github.com/bip-itteam-internal/bip-erp/pull/1123) + erp-frontend [#920](https://github.com/bip-itteam-internal/erp-frontend/pull/920), keduanya **merged**). Dua izin, `hris.pengajuan.view` (mode admin `GET /hr/requests` + `/hr/requests/detail`) dan `hris.pengajuan.approve` (cabang tahap HRD di 4 rute review: `/request/review`, `/business-trip/review`, `/correction/:id/review`, `/schedule-exchange/review`), plus dua paket. Ini **pencabutan pertama** dari empat gate posisi hardcoded yang dijanjikan ADR 0030. Lima hal yang membedakannya dari dua irisan sebelumnya, dan layak dibaca sebelum menggarap gate posisi berikutnya:

- **Izin berlingkup objek, BUKAN memakai ulang `hris.view`.** Himpunan pemakainya memang berbeda: `hris.view` dipegang setiap tier hris lewat `HrisTierDefault`, sedangkan halaman ini hanya terbuka bagi dept `Human Resource` dan posisi `Cost Control`. Memakai ulang `hris.view` akan membukanya bagi pemegang role hris di departemen lain — pelebaran yang tak bergejala.
- **Tier SENGAJA tak menyintesis keduanya.** `HrisTierDefault` memetakan `system_roles["hris"]`, sedangkan gerbang yang digantikan berbasis DEPARTEMEN dan POSISI, dua sumbu yang tak terlihat dari sana. Fallback-nya karena itu tinggal di attendance-service (`gerbangLamaBacaPengajuan`), tempat header departemen memang terbaca, dan diikat ke `HRIS_TIER_FALLBACK` yang sudah ada supaya fase dua tetap satu sakelar. Dikunci `TestHrisTierDefaultTidakMemberiIzinPengajuan`.
- **Paket "HRIS: Admin" TIDAK ikut tumbuh**, karena itu `HrisPermissionCatalog()` tak lagi dipakai apa adanya sebagai isinya (kini `hrisIzinAdministrasi()`). Paket yang mungkin sudah terpasang ke posisi tak boleh berubah artinya diam-diam; kewenangan baru diberikan lewat paket baru supaya pemasangannya terlihat di layar Hak per Posisi.
- **Gerbangnya PREDIKAT (`izinPengajuan`), bukan middleware `gateHris`.** Rute yang sama melayani dua pemakai: `/hr/requests` melayani admin HR sekaligus antrean peninjau lewat `?as`, dan `/request/review` melayani tahap SPV sekaligus tahap HRD. Middleware menilai sebelum handler tahu mode mana yang dipakai, jadi memasangnya di situ memutus supervisor yang menyetujui bawahannya sendiri.
- ⚠️ **Antrean ikut digerbang, bukan hanya tombolnya.** Keempat handler review menyaring lewat `build*ReviewFilter` SEBELUM `switch`, jadi menggerbang cabangnya saja menahan pemegang paket di `FindOne`, sementara membiarkan filternya membuat fase dua menampilkan pengajuan yang menolak saat ditekan (pesannya pun menyesatkan: "already being reviewed or you are not a reviewer"). Ketiga filter karena itu menerima `bolehTahapHR` dari predikat yang sama. Tukar Jadwal perlu pengenal slot tambahan (`slotHRLevelDepartemen`): slot HR di sana cocok karena KEBETULAN bertuliskan "Human Resource" yang sama dengan departemen pemanggil, jadi tanpa itu paketnya hanya berfungsi untuk tiga dari empat jenis pengajuan.

- ⚠️ **Tahap HRD tak selalu duduk di `hr_status`, dan irisan pertama melewatkannya** (ditemukan saat review, ditutup [#1127](https://github.com/bip-itteam-internal/bip-erp/pull/1127)). Dua jenis pengajuan memakai alur SATU tahap dan menaruh peninjau HR di slot `spv_status`: **Koreksi milik staf HR** (`correction.go` Case 3, di situ HR adalah penyetuju FINAL) dan **Tukar milik atasan** departemen mana pun atau orang HR (`determineScheduleExchangeReviewers`). Akibatnya fase dua semula hanya mengunci tiga dari empat jalur, dan yang bocor justru pengajuan milik orang HR sendiri. Penjaganya berbentuk **"bukan slot HR ATAU boleh"** dan mengenali slot dari DATANYA, sehingga cabang atasan biasa tak tersentuh secara konstruksi: slot SPV karyawan reguler selalu orang spesifik, dan slot tingkat departemen milik departemen lain tak pernah bernama "Human Resource". Menggerbang seluruh cabang SPV akan mencabut antrean setiap atasan di setiap departemen, kegagalan yang jauh lebih besar daripada lubang yang ditutup. **Pelajaran yang bisa dibawa ke modul lain: "tahap" adalah makna, bukan nama field** — cari slot yang BERPERAN sebagai tahap itu, jangan percaya penamaannya. Sisa yang sengaja dibiarkan: klausa daftar pengajuan **dibatalkan** di `buildCorrectionReviewFilter` punya pencocokan spv tingkat departemen sendiri di luar `deptOrPositionMatch`, jadi tak ikut tergerbang; isinya riwayat yang tak bisa ditindak, jadi dampaknya keterlihatan saja.

⚠️ **Sisi tajam saat memasang paket, dan ia berlaku untuk SEMUA modul, bukan cuma ini.** Paket pengajuan tetap bermodul `hris`, jadi memasangnya membuat klaim memuat izin hris dan fallback tier PADAM untuk seluruh modul itu. Memasang "HRIS: Penyetuju Pengajuan" SENDIRIAN ke posisi HR karena itu mencabut `hris.view` yang tadinya datang dari tier: menu Kontrak, Resign, Laporan, dan Cuti ikut hilang. Ini kontrak modul yang sudah berlaku sejak irisan pertama (paket menggantikan tier, bukan menambahinya), yang berubah hanya peluang ketemunya karena kini ada paket yang isinya sengaja sempit. **Cara pasang yang benar**: posisi HR diberi paket administrasi (Lihat/Pelaksana/Admin) BERSAMA paket pengajuan, sebab resolusi login menggabungkan keduanya; posisi non-HR seperti Cost Control cukup paket pengajuan. Dipatok `TestPaketPengajuanMematikanFallbackTierSepertiPaketHrisLain`.

Sisi FE: menu **HRIS > Personalia > Pengajuan** kini ber-`perm: "hris.pengajuan.view"` (sebelumnya tanpa `perm` sama sekali, jadi tampil untuk setiap pemegang kategori `hris` walau endpoint-nya membalas 403), dan tabel `FALLBACK` di `menu-permission.ts` menerima konteks identitas (departemen + jabatan) karena gerbang backend izin ini memang bukan role. Pintasan Portal Saya memakai `can()` langsung, bukan `bolehMenu()`, supaya orang HR tak melihat pintasan kedua ke halaman yang sudah ada di menu HRIS-nya. Menu **Tim Terlambat** sengaja TIDAK ikut pindah meski dulu menumpang `case` yang sama: halamannya buku tamu, digerbang `RequireGuestbookRBAC`, modul lain.

⚠️ Catatan sisi FE yang mudah terlewat: `bolehMenu` mengembalikan `true` untuk izin yang tak punya entri `FALLBACK`, mengikuti aturan "modul belum berkatalog, jangan sembunyikan apa pun". Begitu sebuah modul BERKATALOG, aturan itu tak lagi berlaku untuknya — entri fallback wajib ada bahkan untuk izin yang belum dipakai menu mana pun, kalau tidak tombol yang kelak ditandai `hris.manage` akan tampil bagi orang non-HR.

- **`master_permission_set` dan `system_authentication.permission_sets` belum terdaftar** di [[DB - Data Dictionary]].
- **Tiga dari empat gate posisi hardcoded belum dicabut** (Security, Personalia, ICC) — menunggu katalog modul yang bersangkutan. **Cost Control sudah dicabut SEBAGIAN** (2026-08-09): untuk halaman Pengajuan ia kini paket "HRIS: Pemantau Pengajuan", tapi `checkPosition(PosisiCostControl)` di `RequireGuestbookRBAC` masih hidup karena modulnya lain (buku tamu). Konstanta `common.PosisiCostControl` karena itu belum boleh dihapus.
- **Gate `admin.assignment.manage` belum ada**, jadi pemasangan hak ke posisi masih dikunci interim ke `RequireITSupervisor`, bukan ke HR.
- **TBD**: pemisahan per area gudang (RM vs FG) sebagai cakupan alih-alih permission; perilaku seragam saat pemakai membuka URL tanpa hak (403 informatif vs pengalihan); penyelarasan pola izin finance (per-objek) dengan tangga ADR 0030.

⚠️ **Penemuan yang membatalkan asumsi seluruh dok ini untuk lingkungan dev (2026-08-09): permission-set TAK PERNAH aktif di dev sampai hari itu.** Image `api-gateway` yang berjalan dibangun **12 Juli**, sedangkan klaim `permissions` baru masuk `common.PayloadJWT` **25 Juli**. Gateway lama mem-parse balasan employee-service ke struct versi lama, **membuang** `permissions` dan `supervised_departments`, lalu menandatangani token tanpa keduanya. Jadi seluruh paket — payroll, finance, procurement, monitoring, hris, dan seterusnya — tak pernah sampai ke token siapa pun di dev, dan `reach: division` tak pernah punya cakupan untuk dinilai.

Gejalanya menyesatkan: menu tetap hilang meski paket sudah dipasang dan sudah login ulang berkali-kali, sehingga tuduhan pertama jatuh ke logika RBAC-nya.

Sebabnya gateway **tak bisa dibangun ulang**: ia memanggil `ValidateInternalURL` untuk SELURUH isi `InternalURL` saat start, dan tujuh modul yang belum dijalankan di dev tak punya entri `*_MODULE_URL`, sehingga tiap percobaan build berakhir restart-loop. Port ketujuhnya ada di `.env.example` tapi tak pernah tersalin ke `.env` lokal. Keduanya sudah ditambal; verifikasinya lewat gateway sungguhan — token tanpa klaim `permissions` → 403 di `/api/recruitment/candidates` dan `/api/employee/kpi`, dengan klaim → 200.

> **Pelajaran yang berlaku lebih luas dari RBAC:** membaca kode di repo tidak cukup untuk menyimpulkan perilaku lingkungan. Tujuh service lain masih memakai image 12 Juli, dan pola yang sama sudah menggigit dua kali dalam satu hari (gateway, lalu IT-Orchestrator — lihat [[CORE - IT Orchestrator]]). Lihat [[RUN - Deploy Microservices bip-erp]].

**Aturan kerja**: satu PR sama dengan satu modul, memuat katalog + paket bawaan, gerbang BE + kill-switch env, dan penyaringan FE sekaligus. Urutan: payroll, recruitment, hris, wms, integration (integration terakhir karena terbesar dan paling banyak celah).

**Yang berubah dari urutan itu (2026-08-09):** `wms` **tidak** dikatalogkan. Pengukuran ke data menunjukkan masalah nyatanya bukan ketiadaan aturan melainkan ketiadaan data peran, dan matriks WMS yang sudah ada terlalu mahal untuk disalin ke bentuk kedua — lihat [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]. Urutan sisanya juga diturunkan dari data, bukan dari ukuran service: **56 dari 63 jabatan** berbagi tanda tangan `system_roles` yang identik dengan jabatan lain di departemennya, artinya RBAC hari ini tak bisa membedakan mereka sama sekali. Terparah Finance (8 jabatan → 3 pola) dan Beauty Hacks (10 → 11 pola tapi lima jabatan menyatu jadi satu).

Akar teknisnya satu angka: **18 dari 156 menu** yang punya penanda izin, dan 16 di antaranya HRIS. Menu tanpa penanda selalu tampil, tak peduli paketnya — jadi memasang paket ke jabatan di modul yang menunya belum ditandai tidak mengubah apa pun di layar.

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
- [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] (jembatan untuk `manufacture` & `insentive` yang belum berkatalog)
- [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]] (modul `menu`, penanda kunci, batas penegakannya)
- [[ADR - 0003 SSO-only Gateway]] · [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]
- [[DB - Data Dictionary]] · [[DB - Overview and Notes]]
- [[APP - Web ERP]] · [[HRIS - Organization Structure]]

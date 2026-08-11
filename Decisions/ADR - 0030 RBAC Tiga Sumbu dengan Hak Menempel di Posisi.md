**Status**: ⚠️ Implemented (ada catatan). Keputusan ini **sudah dijalankan dan terverifikasi live di dev DAN produksi** (2026-07-30): posisi memegang paket hak, izin efektif digabung dari posisi + akun dengan reach tertinggi, layar Hak per Posisi & Siapa Boleh Apa jalan, dan penegakan per-aksi aktif di `ticket` serta `payroll`. Paket per-akun sudah dirapikan (dev 5 jadi 1, prod 4 jadi 0, sehingga hampir semua hak kini berasal dari jabatan). Catatan per 2026-08-11: **14 modul sudah berkatalog** (`ga` menyusul lewat [#1163](https://github.com/bip-itteam-internal/bip-erp/pull/1163)) dan penegakannya jalan di semuanya kecuali `finance`, yang berkatalog tanpa satu pun gerbang endpoint; **7 modul dari daftar asli belum berkatalog** (`hrdoc`, `wms`, `warehouse`, `integration`, `insentive`, `notification`, `admin`); dan pola izin antar-modul belum seragam (lihat Consequences). Yang menahan dampaknya bukan katalog melainkan dua hal lain: fase dua belum menyala di modul mana pun, dan baru 29 dari 171 entri menu yang ditandai izin — rinciannya di [[CORE - RBAC dan Permission Set]].

## Context

Hari ini ada **tiga mekanisme akses yang hidup berdampingan** di bip-erp, tanpa satu pun dokumen yang menyatukannya:

1. **`system_roles`** (map modul ke satu nilai role: `staff`/`supervisor`/`admin` plus nilai granular seperti `admin_gudang_rm`, `ppic`, `icc`). Ditegakkan `common.Require*` / `checkRole` (`shared-library/common/roles.go`). Ini yang dipakai hampir semua service.
2. **Permission-set** (bundel permission granular + `reach`), pilot di modul **ticket**: katalog `shared-library/common/catalog_ticket.go` (15 permission), validasi set `shared-library/models/employee/permission_set.go`, resolusi izin efektif saat login `services/employee/permission_resolve.go`, penegakan `common.RequirePermission` + `gate()` di `services/task-management/routes.go`.
3. **Posisi** (`work_data.position`) sebagai pengecualian lintas-modul di **empat titik**: Cost Control (BE `checkPosition` + `isCostControl`), Security, Personalia, dan ICC (ketiganya **hanya di FE**). Sejak 2026-07-30 bertambah **titik kelima**, lihat §Consequences. *(Cost Control sudah dicabut sebagian pada 2026-08-09; `isCostControl` kini hanya fallback union, bukan gerbang utama.)*

Empat fakta hasil audit 2026-07-29 yang membentuk keputusan ini:

- **Posisi bukan entitas.** Ia hanya elemen `[]string` di dalam `master_department.positions` (`shared-library/models/employee/master_data.go:29`), dan `work_data.position` menyimpan namanya sebagai teks. Tanpa ID atau key stabil, rename posisi memutus akses tanpa jejak.
- **Penegakan sangat tidak rata.** Dari 950 rute di 16 service, **557 rute user-facing tanpa middleware apa pun, 230 di antaranya operasi tulis**. Terparah: integration (241 telanjang), manufacture (95, seluruh WMS), employee (84), attendance (45), insentive (32). Sebaliknya recruitment, payroll, procurement, warehouse, hrd-document, dan task-management sudah tergerbang rapi.
- **FE punya pipa tapi belum tersambung.** `can()` dan `reachFor()` ada di `erp-frontend/src/utils/access.ts` dan klaim `permissions` sudah dibaca `use-auth.ts`, tapi **nol pemakai**: penyaringan menu masih memakai `system_roles` plus pengecualian posisi hardcoded.
- **Katalog per-endpoint terlalu rinci untuk dipakai.** Draft awal menghasilkan 150 permission; layar assign dengan 20 checkbox per modul tidak akan dipakai HR.

## Decision

**RBAC tiga sumbu, dengan hak default menempel pada POSISI.**

**Sumbu 1, modul**: batas mengikuti service/domain, **bukan** modul sidebar (sidebar mencampur domain; `hris` memuat 36 menu yang sebenarnya empat domain). 15 modul: `hris`, `payroll`, `recruitment`, `kpi`, `training`, `hrdoc`, `wms`, `warehouse`, `procurement`, `integration`, `insentive`, `ga`, `notification`, `admin`, `ticket`.

> **Daftar ini bertambah, dan memang boleh bertambah** (2026-08-09): **`legal`** menjadi modul ke-16 saat register Perizinan/Kontrak/Dispute dikatalogkan. Ia tak ada di daftar asli karena modulnya sendiri belum lahir saat ADR ini ditulis, bukan karena sengaja dikecualikan. Yang mengikat bukan panjang daftarnya melainkan **aturan pembentuknya**: satu modul = satu batas service/domain, dan satu permission per keputusan akses. Modul baru yang memenuhi keduanya masuk tanpa mengubah keputusan ini; yang tidak, perlu ADR sendiri. `menu`, `finance`, `kaskecil`, dan `monitoring` juga sudah menyusul dengan alasan berbeda-beda yang dicatat di [[CORE - RBAC dan Permission Set]].
>
> **`formbuilder` menyusul 2026-08-10** ([#1138](https://github.com/bip-itteam-internal/bip-erp/pull/1138)) dan ia contoh terbersih bahwa aturan pembentuk itu yang bekerja, bukan daftarnya: Form Builder punya service sendiri sehingga lolos syarat "satu modul = satu batas service", padahal menunya muncul di DUA kategori sidebar (`it` dan `ga`) sekaligus. Kepemilikan formnya ditentukan `owner_department`, bukan key modul — persis alasan sumbu modul dipisah dari sumbu organisasi di ADR ini. Yang TIDAK ikut pindah ke sumbu izin adalah cakupan departemennya; lihat [[Microservices - Form Builder Service]].

**Sumbu 2, tingkat**: tangga empat kata kerja yang sama di semua modul, `view` (Lihat) / `work` (Kerjakan) / `approve` (Setujui) / `manage` (Kelola). Modul hanya memakai tingkat yang relevan. Tingkat tidak otomatis bertingkat; paket yang menggabungkan.

**Sumbu 3, cakupan**: `reach` = `own` / `division` / `all`, hanya di modul yang datanya milik orang atau divisi (`hris`, `kpi`, `ticket`, `insentive`, `recruitment`). Modul operasional selalu `all`.

Keputusan turunan:

- **Total 67 permission** (52 baru + 15 ticket), bukan 150. Aturannya: satu permission per **keputusan akses yang berbeda**, bukan per endpoint.
- **Lima pengecualian granular** yang dibenarkan kasus nyata: `wms.selisih.create` (posisi Security mencatat bukti selisih RM tanpa hak WMS lain), `integration.export` (data keluar sistem), `notification.broadcast.send` (tak bisa ditarik), `admin.permissionset.manage` dan `admin.assignment.manage` (bisa menaikkan hak sendiri).
- **Self-service tanpa permission**: slip gaji sendiri, KPI sendiri, insentif sendiri, tugas onboarding sendiri, inbox sendiri adalah hak bawaan tiap karyawan, ditegakkan BE lewat `employee_id` dari token.
- **Posisi memegang paket, akun jadi pengecualian.** Posisi diberi `key` slug stabil, `master_department.positions` naik dari `[]string` jadi objek ber-`key`/`name`/`permission_sets`, dan `work_data` dapat `position_key` (nama tetap disimpan agar konsumen lama tak pecah). Resolusi login menggabungkan (union) set dari akun dan set dari posisi, dengan `reach` tertinggi per modul.
- **Paket bernama** (`MasterPermissionSet`) adalah yang dipilih HR, bukan permission. Nama pakai bahasa manusia ("Payroll: Pelaksana", "WMS: Admin Gudang RM"). Isi paket hanya bisa diubah IT (`admin.permissionset.manage`).
- **FE menyaring dari permission**, bukan dari role: tiap item menu mendeklarasikan `perm`, sidebar memakai `can(permissions, perm, fallbackTier)`, tombol aksi memakai `can()` yang sama. Penyembunyian di FE adalah kenyamanan, bukan keamanan.
- **Fallback tier wajib** selama migrasi: akun tanpa permission-set jatuh ke tier `system_roles` lama, di BE maupun FE, supaya tak ada yang kehilangan akses saat penyalaan.
- **Satu PR sama dengan satu modul**, dan setiap PR wajib memuat tiga hal sekaligus: katalog + paket bawaan, gerbang BE (`RequirePermission`) + kill-switch env, dan penyaringan FE. Urutan: payroll, recruitment, hris, wms, integration.

## Consequences

**Konsekuensi yang diterima:**

- **Hak ikut token, berlaku 72 jam** (`shared-library/auth/jwt.go`). Mengubah posisi atau isi paket baru terasa setelah pemakai login ulang. Ini pertukaran yang sama dengan `supervised_departments` dan sudah jadi gotcha yang dikenal (SPV HRGA wajib login ulang).
- **Empat gate posisi hardcoded akan dicabut** dan diganti paket: Cost Control jadi "Kepegawaian: Pemantau Pengajuan", Personalia jadi "Payroll: Pelaksana", Security jadi "WMS: Pencatat Selisih", ICC jadi "Insentive: Lihat Sendiri".

	✅ **Yang pertama sudah dijalankan 2026-08-09** (bip-erp [#1123](https://github.com/bip-itteam-internal/bip-erp/pull/1123) + erp-frontend [#920](https://github.com/bip-itteam-internal/erp-frontend/pull/920), merged): paketnya bernama **"HRIS: Pemantau Pengajuan"**, bukan "Kepegawaian: …", mengikuti awalan yang sudah dipakai seluruh paket modul ini. Pencabutannya **sebagian**: hanya untuk halaman Pengajuan; `checkPosition(PosisiCostControl)` di `RequireGuestbookRBAC` masih hidup karena buku tamu modul lain.

	Dua hal yang ditemukan saat menjalankannya, dan keduanya berlaku untuk tiga gate sisanya. **Pertama, izinnya tak bisa memakai ulang izin modulnya** (`hris.view`): gate posisi ada justru karena himpunan pemakainya berbeda dari tier, jadi memakai ulang berarti memberi hak itu ke seluruh pemegang tier. Yang lahir sepasang izin berlingkup objek, `hris.pengajuan.view` dan `hris.pengajuan.approve`. **Kedua, fallback tier tak sanggup mencerminkan gate posisi**, sebab `*TierDefault` hanya membaca `system_roles` sementara gate-nya berbasis departemen dan jabatan. Fallback-nya karena itu tinggal di service, di tempat headernya terbaca, dan diikat ke sakelar `<MODUL>_TIER_FALLBACK` yang sudah ada supaya fase dua tetap satu langkah. Rinciannya di [[CORE - RBAC dan Permission Set]] §irisan ketiga.
- **`admin.permissionset.manage` dan `admin.assignment.manage` adalah hak yang bisa menaikkan hak sendiri**, jadi wajib menempel di satu posisi saja dan setiap perubahannya diaudit. Tanpa itu, seluruh pondasi ini bisa dilewati dari dalam.
- **Katalog tanpa gerbang BE adalah dekorasi.** Modul dengan rute telanjang (WMS, integration, insentive, notification, sebagian employee dan attendance) tidak boleh dinyalakan penyaringan FE-nya sebelum endpoint-nya digerbang, karena hasilnya persis masalah WMS sekarang: menu rapi, endpoint tetap bisa dipanggil langsung.

**Konsekuensi yang muncul saat dijalankan (2026-07-30):**

- **Backfill paket per-akun dicabut.** `migratePermissionSetAssignment` memberi paket ke akun yang punya role ticket eksplisit dan `permission_sets` kosong. Karena "kosong" tak bisa dibedakan dari "sengaja dikosongkan", setiap restart service mengembalikan paket per-akun yang baru dirapikan ke posisi (terbukti di dev: 2 akun kembali dalam satu deploy). Backfill dicabut; paket yang sudah ada tidak dihapus.
- **Jalur per-akun TETAP dipertahankan, dan itu keputusan berdasar data.** Sempat diusulkan mencabutnya agar sumber hak tunggal, tapi di dev ada akun berposisi **ICC yang dipegang 40 orang** yang diberi hak supervisi tiket. Memindahkannya ke posisi berarti menaikkan hak 39 orang lain; mengarang posisi khusus satu orang mengotori struktur organisasi yang dibaca fitur lain (supervisi, KPI, requisition). Jadi: posisi untuk hak yang mengikuti jabatan, akun untuk pengecualian individu. Yang wajib diperbaiki keterlihatannya, dan itu sudah dikerjakan lewat daftar pengecualian di layar Siapa Boleh Apa.
- **Patokan sebelum memindahkan hak akun ke posisi**: hitung dulu jumlah pemegang posisi itu. Tanpa langkah ini, pembersihan yang tampak rapi bisa berubah jadi kenaikan hak massal.
- **"Fallback tier wajib" butuh BUKTI, dan buktinya gampang palsu** (ditemukan saat mengkatalogkan `legal`, 2026-08-09). Cara membuktikannya adalah tabel yang menjalankan tiap kombinasi peran terhadap tiap izin lalu membandingkannya dengan gerbang lama. Yang menentukan: **tiruan gerbang lama di dalam uji harus ditulis dari sumber aslinya, bukan dari kode yang sedang ditulis.** Sekali ia menyalin asumsi implementasinya (di sini: memangkas spasi, padahal `checkRole` membandingkan nilai header apa adanya), kedua sisi sepakat pada jawaban yang sama-sama salah dan tabelnya berhenti membuktikan apa pun. Pelebaran akses yang lolos lewat celah ini tak punya gejala sama sekali — tak ada yang mengeluh saat mendapat hak yang bukan haknya.
- **Pola izin belum seragam.** Katalog `payroll` mengikuti tangga tingkat (dengan satu pengecualian `payroll.salary.write`), sementara `finance` yang menyusul memakai izin **per-objek** (`finance.ar.view`, `finance.kastoko.view`, dst). Belum diputuskan mana yang jadi acuan; lihat catatan penyimpangan di [[CORE - RBAC dan Permission Set]].
- **"Rute telanjang" ternyata lebih terbuka dari yang dicatat ADR ini.** Audit lanjutan menemukan prefix `/internal/` **bukan** batas keamanan (gateway meneruskan seluruh sub-path dan mengisi sendiri gateway key), sehingga sebagian rute tanpa middleware bisa dipanggil dari internet oleh siapa pun yang bisa login, termasuk satu rute yang menulis `system_roles` apa pun. Dua lubang ditambal dan ter-deploy hari yang sama. Ini menguatkan poin "katalog tanpa gerbang BE adalah dekorasi" di atas: urutan yang benar adalah gerbangi endpoint dulu, baru nyalakan penyaringan FE. Detail keputusan di [[ADR - 0031 Prefix internal Bukan Batas Keamanan]], bukti dan forensiknya di [[LOG - 2026-07-30 Audit Otorisasi Employee Service]].

**KPI cakupan tim — gerbang RELASI, bukan izin (2026-07-31, branch `feat/atasan-langsung-kpi-leader`, belum merge):**

`GET /kpi?scope=team` menggerbang aksesnya dari **keberadaan bawahan langsung** (`work_data.supervisor_id`), bukan dari izin `kpi.view.team` sebagaimana dikehendaki ADR ini. Sebabnya modul `kpi` termasuk 15 modul di §Decision tapi **belum punya katalog izin**, dan membuat katalognya berarti menyeret pekerjaan itu ke dalam task yang seharusnya kecil.

Perlu dicatat bahwa ini **bukan** pengecualian berbasis nama posisi seperti empat titik sebelumnya. Justru sebaliknya: pendekatan berbasis nama jabatan sengaja **ditolak** karena pola `Supervisor|^Leader$` tak cocok untuk "Leader Production", "AR Leader", maupun "QA Leader" yang benar-benar ada di data. Gerbang berbasis relasi lebih dekat ke semangat ADR ini ketimbang cocok-cocokan nama, dan otomatis benar saat jabatan di-rename.

Penekan kerugiannya: pemeriksaannya satu fungsi terpusat (`bawahanAktif`), jadi saat katalog `kpi` dibuat nanti cukup fungsi itu yang diganti pemanggilnya.

**Titik pengecualian posisi KELIMA — Dashboard HRIS per posisi (2026-07-30, branch `feat/dashboard-hris-per-posisi`, belum merge):**

Berlawanan arah dengan ADR ini, dan disepakati sadar oleh pemilik keputusan setelah keterbatasannya disampaikan. Isi `/hris/dashboard` dipilih dari **nama posisi**, bukan `position_key` maupun paket izin, karena dua prasyarat belum ada: `position_key` belum diteruskan ke frontend (yang sampai ke sana hanya cookie `position` berisi nama tampilan), dan modul `hris`/`recruitment`/`kpi` belum punya katalog izin sehingga `bolehMenu` sengaja mengembalikan `true`.

Yang membedakannya dari empat titik sebelumnya, dan yang membuatnya bisa dibongkar nanti tanpa perburuan:

- **Terpusat** di `features/hris/dashboard/lib/position-view.ts`, bukan `if` telanjang tersebar seperti `sidebar.tsx` (yang mencocokkan `icc`, `security`, `cost control` di tiga tempat berbeda).
- **Bagian terpenting tidak bergantung nama**: status supervisor diambil dari `system_roles.hris`, jadi rename posisi tak mencabut tampilan lengkap SPV. Nama posisi hanya membedakan sesama staf, di mana `system_roles` memang tak punya informasi.
- **Fallback aman**: nama tak dikenal jatuh ke preset `default` yang tetap berguna, bukan layar kosong.
- **Daftar nama posisi dikunci test**, sehingga perubahan master data bikin CI merah lebih dulu daripada pemakai menemukan dashboardnya berganti diam-diam.

✅ **SEBAGIAN DICABUT 2026-08-11** (branch `feat/hris-izin-divisi` + `feat/hris-izin-divisi-fe`, **belum merge**). Yang dicabut adalah sumbu "siapa melihat SELURUH tab", yang ternyata bukan gate berbasis nama posisi sama sekali melainkan `isAnySupervisor(systemRoles) || isItMember(systemRoles)` — kewenangan yang bukan fakta bisa-ditugaskan melainkan **efek samping** memegang role supervisor di modul tak berhubungan, sehingga supervisor Warehouse/Quality/Procurement ikut melihat meja kerja Personalia. Kini izin `hris.divisi.view` lewat paket **"HRIS: Pemantau Divisi"**. Dua prasyarat yang disebut di atas memang sudah gugur: klaim `permissions` dibaca `use-auth.ts`, dan `hris` berkatalog.

Yang BELUM dicabut: pemilihan **tab milik siapa** masih dari nama posisi (`PETA_POSISI` di `lib/tab-untuk-posisi.ts`), sebab `position_key` masih belum mengalir ke frontend.

⚠️ **Jalan keluar yang dijanjikan paragraf ini sudah TIDAK ADA.** `presetUntuk` dicabut di erp-frontend [#951](https://github.com/bip-itteam-internal/erp-frontend/pull/951) sebagai kode mati — enam preset di baliknya tak pernah terjangkau sejak tab-tab bermigrasi ke kosakata kartu. Titik masuk sebenarnya kini `saringTab` (siapa lihat semua) dan `slugTabSaya` (tab milik siapa), keduanya di `lib/tab-untuk-posisi.ts`. Pelajarannya: **rencana pencabutan yang menyebut nama fungsi ikut membusuk bersama fungsinya**, dan tak ada yang memberi tahu.

Tiga hal yang ditemukan saat menjalankannya, dan ketiganya berlaku untuk pencabutan berikutnya:

1. **`can(perms, izin, fallback)` MENGABAIKAN argumen fallback-nya** begitu token memuat izin modul yang sama (`utils/access.ts`: `modulPunyaIzin(...) ? false : fallback`). Aturan itu benar untuk izin atas DATA, tapi mematikan fase satu di sini: setiap supervisor HR sudah memegang `hris.view/work/manage` dari `HrisTierDefault`, jadi klaim modul `hris` SELALU ada dan fallback tak pernah terbaca. Bentuk yang aman: izin diperiksa KETAT (`can(..., false)`) lalu aturan lama di-**OR** terpisah. Sama bentuknya dengan pelajaran Cost Control di §Consequences — fallback tinggal di tempat informasinya terbaca, sebab `system_roles` lintas modul tak terlihat oleh `HrisTierDefault` maupun `can()`.
2. **Izin yang tak punya entri `FALLBACK` DILOLOSKAN `bolehMenu`.** Menambah izin ke katalog tanpa menambah barisnya berarti siapa pun yang tokennya tak memuat izin modul itu lolos begitu ada yang menandai sebuah menu dengannya — kebalikan dari maksud izin yang justru dibuat untuk menyempitkan. Untuk izin yang gerbangnya BUKAN `bolehMenu`, entrinya diisi `tolak`: dua resolver untuk satu izin pasti menyimpang, dan arah gagal yang benar untuk jalur tak terpakai adalah menutup.
3. **Izin TAMPILAN tak punya gerbang BE, dan itu bukan pelanggaran "katalog tanpa gerbang BE adalah dekorasi".** Yang digerbang komposisi TAB, bukan data; endpoint di balik tiap tab sudah digerbang per modul. Aturan itu ditulis untuk izin atas data. Penyimpangan ini disengaja dan ditulis di kodenya.

**Batas nyata yang ditemukan saat verifikasi dev 2026-07-30**: preset `ga`, `security`, dan `office-boy` **tidak akan pernah tampil**, karena menu HRIS menuntut `system_roles.hris` sedangkan posisi itu tak punya (`GA Staff` 2 orang `ga:staff`, `Security` 7 orang `ga:security`, `Office Boy` 4 orang `system_roles` **kosong**). Praktisnya **13 dari 17 orang HRGA belum terlayani**. Presetnya sengaja dipertahankan agar siap pakai, tapi jangan dibaca sebagai "GA sudah dapat dashboard".

Catatan penting: penyaringan ini **kenyamanan tampilan, bukan kontrol akses**. `/hris/dashboard` tak dijaga middleware, penjaga sebenarnya tetap 403 backend.

**Field kedua yang menempel di posisi tapi BUKAN hak — jenjang jabatan (2026-08-03, live di produksi):**

`position_items[]` kini punya `level_key` di samping `permission_sets` dan `menu_hidden`. Ketiganya menempel pada jabatan, tapi hanya yang pertama menentukan akses.

Ini titik yang mudah longgar. Begitu sebuah struktur jadi tempat menggantung banyak hal, godaan menjadikan salah satunya gerbang akses tumbuh sendiri: satu baris `if RankOf(...) >= ...` di resolver terasa praktis dan tak akan membuat satu pun test fungsional gagal. Akibatnya baru terasa berbulan-bulan kemudian, saat seseorang naik jenjang lalu diam-diam mendapat wewenang yang tak pernah diputuskan siapa pun, dan ada dua sumber hak yang bisa menyimpang.

Karena itu larangannya **ditulis sebagai test yang membaca sumber**: `TestJenjangBukanSumbuHakAkses` menolak kemunculan `LevelKey`/`level_key`/`RankOf`/`JobLevel` di `permission_resolve.go` dan `permission_exceptions.go`. Pola sama dengan [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] yang dijaga `internal_routes_guard_test.go`. Kalau suatu saat gerbang berbasis jenjang memang dibutuhkan, itu keputusan arsitektur baru yang mengubah ADR ini, bukan penambahan satu `if`.

Catatan gerbang: `PUT .../positions/:positionKey/level` memakai `RequireHRISOrITSupervisor`, sama dengan `menu-hidden` dan lebih longgar dari `permission-sets` yang dikunci IT. Konsisten dengan prinsip di atas — yang tak bisa menaikkan hak tak perlu dikunci seketat yang bisa. Sama seperti dua saudaranya, gerbang itu **berbasis peran, bukan cakupan departemen**: supervisor HRIS mana pun bisa menyetel jabatan departemen mana pun. Untuk jenjang dan menu dampak terburuknya label atau tampilan yang salah, tapi ini pola yang perlu diingat saat menambah setelan per-posisi berikutnya.

Detail desainnya (rank renggang, pemisahan nama dari urutan) di [[HRIS - Organization Structure]].

**Premisnya sempat tak lengkap, dan itu baru ketahuan saat dipakai sungguhan (2026-08-09).** Keputusan ini menyatakan hak menempel di posisi lewat paket, tapi paket hanya bisa **menyempitkan** di dalam modul yang sudah dibuka `system_roles` — kategori sidebar lahir semata dari sana, sehingga paket tak pernah bisa **membuka** modul. Finance memperlihatkannya paling telanjang: 16 dari 18 akunnya tak punya satu pun `system_role`, jadi memasang paket ke jabatan AR Staff tak mengubah apa pun. Sejak `kunciModulAktif` (`erp-frontend/src/components/layout/modul-aktif.ts`), paket ikut menentukan kategori. Cakupannya sempit dengan sendirinya — hanya modul yang punya katalog **dan** kategori sidebar; hari ini `finance` dan `procurement`.

**Dua modul justru tak akan dikatalogkan, dan itu keputusan terpisah.** `manufacture` dan `insentive` sudah punya pembedaan per pekerjaan yang halus dan sudah ditegakkan; yang rusak di sana datanya, bukan aturannya. Menyalin matriks WMS 400 baris ke bentuk katalog akan melipatgandakan permukaan yang bisa menyimpang. Jembatannya di [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]] — yang eksplisit menyatakan dirinya sementara dan dicabut begitu kedua modul berkatalog.

**Yang belum diputuskan (TBD):**

- **Pemisahan per area gudang** (Admin Gudang RM vs FG) bukan soal permission melainkan cakupan area. Menempelkannya ke permission akan melahirkan `wms.rm.*` dan `wms.fg.*` dan membengkakkan katalog. Tahap pertama menyamakan dengan matriks FE yang berlaku; kemungkinan arah: cakupan mirip `reach`, bukan permission baru.

	TBD ini kini **menghalangi hal yang konkret**: jabatan `Admin Warehouse` dan `Warehouse Leader` tak bisa dipetakan ke peran WMS mana pun karena gudangnya RM atau FG tak bisa disimpulkan dari namanya, sehingga keduanya tertinggal tanpa akses di [[ADR - 0043 Peran Sistem Diturunkan dari Jabatan]]. Menunggu jawaban pengelola.
- **Perilaku saat pemakai membuka URL tanpa hak**: halaman 403 yang menyebut permission yang dibutuhkan, atau pengalihan ke dashboard (perilaku WMS sekarang). Perlu satu perilaku seragam.
- **Peran "admin pusat"** masih dipetakan interim ke `system_roles.group = admin` (lihat [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]); hubungannya dengan modul `admin` di katalog ini perlu dirapikan.
- **Cara posisi GA (GA Staff, Security, Office Boy) mendapat dashboardnya**: diberi `system_roles.hris`, atau dibuatkan dashboard sendiri di bawah `/ga/`. Pilihan pertama membuka seluruh menu HRIS untuk mereka, jadi kemungkinan besar bukan yang diinginkan.

## Terkait

- [[CORE - RBAC dan Permission Set]] (katalog lengkap, paket, dan status penegakan per service)
- [[Microservices - Employee Service]] (master posisi, permission-set, resolusi izin saat login) · [[Microservices - Task Management Service]] (pilot yang sudah jalan)
- [[Microservices - Payroll Service]] · [[Microservices - Manufacture Service]] · [[Microservices - Recruitment Service]]
- [[CORE - API Master Gateway]] (stempel header identitas dari klaim JWT) · [[CORE - SSO Flow]]
- [[APP - Web ERP]] (penyaringan menu & tombol) · [[HRIS - Organization Structure]] (posisi & departemen sebagai master)
- [[DB - Data Dictionary]] (`master_permission_set` dan `permission_sets` belum terdaftar di sana)
- [[ADR - 0003 SSO-only Gateway]] · [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]

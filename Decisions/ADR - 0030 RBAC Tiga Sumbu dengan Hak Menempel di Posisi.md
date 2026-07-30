**Status**: ⚠️ Implemented (ada catatan). Keputusan ini **sudah dijalankan dan terverifikasi live di dev** (2026-07-30): posisi memegang paket hak, izin efektif digabung dari posisi + akun dengan reach tertinggi, layar Hak per Posisi & Siapa Boleh Apa jalan, dan penegakan per-aksi aktif di `ticket` serta `payroll`. **Belum di produksi.** Catatan: `finance` baru berkatalog tanpa gerbang, 11 modul lain belum berkatalog, dan pola izin antar-modul belum seragam (lihat Consequences).

## Context

Hari ini ada **tiga mekanisme akses yang hidup berdampingan** di bip-erp, tanpa satu pun dokumen yang menyatukannya:

1. **`system_roles`** (map modul ke satu nilai role: `staff`/`supervisor`/`admin` plus nilai granular seperti `admin_gudang_rm`, `ppic`, `icc`). Ditegakkan `common.Require*` / `checkRole` (`shared-library/common/roles.go`). Ini yang dipakai hampir semua service.
2. **Permission-set** (bundel permission granular + `reach`), pilot di modul **ticket**: katalog `shared-library/common/catalog_ticket.go` (15 permission), validasi set `shared-library/models/employee/permission_set.go`, resolusi izin efektif saat login `services/employee/permission_resolve.go`, penegakan `common.RequirePermission` + `gate()` di `services/task-management/routes.go`.
3. **Posisi** (`work_data.position`) sebagai pengecualian lintas-modul di **empat titik**: Cost Control (BE `checkPosition` + `isCostControl`), Security, Personalia, dan ICC (ketiganya **hanya di FE**).

Empat fakta hasil audit 2026-07-29 yang membentuk keputusan ini:

- **Posisi bukan entitas.** Ia hanya elemen `[]string` di dalam `master_department.positions` (`shared-library/models/employee/master_data.go:29`), dan `work_data.position` menyimpan namanya sebagai teks. Tanpa ID atau key stabil, rename posisi memutus akses tanpa jejak.
- **Penegakan sangat tidak rata.** Dari 950 rute di 16 service, **557 rute user-facing tanpa middleware apa pun, 230 di antaranya operasi tulis**. Terparah: integration (241 telanjang), manufacture (95, seluruh WMS), employee (84), attendance (45), insentive (32). Sebaliknya recruitment, payroll, procurement, warehouse, hrd-document, dan task-management sudah tergerbang rapi.
- **FE punya pipa tapi belum tersambung.** `can()` dan `reachFor()` ada di `erp-frontend/src/utils/access.ts` dan klaim `permissions` sudah dibaca `use-auth.ts`, tapi **nol pemakai**: penyaringan menu masih memakai `system_roles` plus pengecualian posisi hardcoded.
- **Katalog per-endpoint terlalu rinci untuk dipakai.** Draft awal menghasilkan 150 permission; layar assign dengan 20 checkbox per modul tidak akan dipakai HR.

## Decision

**RBAC tiga sumbu, dengan hak default menempel pada POSISI.**

**Sumbu 1, modul**: batas mengikuti service/domain, **bukan** modul sidebar (sidebar mencampur domain; `hris` memuat 36 menu yang sebenarnya empat domain). 15 modul: `hris`, `payroll`, `recruitment`, `kpi`, `training`, `hrdoc`, `wms`, `warehouse`, `procurement`, `integration`, `insentive`, `ga`, `notification`, `admin`, `ticket`.

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
- **`admin.permissionset.manage` dan `admin.assignment.manage` adalah hak yang bisa menaikkan hak sendiri**, jadi wajib menempel di satu posisi saja dan setiap perubahannya diaudit. Tanpa itu, seluruh pondasi ini bisa dilewati dari dalam.
- **Katalog tanpa gerbang BE adalah dekorasi.** Modul dengan rute telanjang (WMS, integration, insentive, notification, sebagian employee dan attendance) tidak boleh dinyalakan penyaringan FE-nya sebelum endpoint-nya digerbang, karena hasilnya persis masalah WMS sekarang: menu rapi, endpoint tetap bisa dipanggil langsung.

**Konsekuensi yang muncul saat dijalankan (2026-07-30):**

- **Backfill paket per-akun dicabut.** `migratePermissionSetAssignment` memberi paket ke akun yang punya role ticket eksplisit dan `permission_sets` kosong. Karena "kosong" tak bisa dibedakan dari "sengaja dikosongkan", setiap restart service mengembalikan paket per-akun yang baru dirapikan ke posisi (terbukti di dev: 2 akun kembali dalam satu deploy). Backfill dicabut; paket yang sudah ada tidak dihapus.
- **Jalur per-akun TETAP dipertahankan, dan itu keputusan berdasar data.** Sempat diusulkan mencabutnya agar sumber hak tunggal, tapi di dev ada akun berposisi **ICC yang dipegang 40 orang** yang diberi hak supervisi tiket. Memindahkannya ke posisi berarti menaikkan hak 39 orang lain; mengarang posisi khusus satu orang mengotori struktur organisasi yang dibaca fitur lain (supervisi, KPI, requisition). Jadi: posisi untuk hak yang mengikuti jabatan, akun untuk pengecualian individu. Yang wajib diperbaiki keterlihatannya, dan itu sudah dikerjakan lewat daftar pengecualian di layar Siapa Boleh Apa.
- **Patokan sebelum memindahkan hak akun ke posisi**: hitung dulu jumlah pemegang posisi itu. Tanpa langkah ini, pembersihan yang tampak rapi bisa berubah jadi kenaikan hak massal.
- **Pola izin belum seragam.** Katalog `payroll` mengikuti tangga tingkat (dengan satu pengecualian `payroll.salary.write`), sementara `finance` yang menyusul memakai izin **per-objek** (`finance.ar.view`, `finance.kastoko.view`, dst). Belum diputuskan mana yang jadi acuan; lihat catatan penyimpangan di [[CORE - RBAC dan Permission Set]].

**Yang belum diputuskan (TBD):**

- **Pemisahan per area gudang** (Admin Gudang RM vs FG) bukan soal permission melainkan cakupan area. Menempelkannya ke permission akan melahirkan `wms.rm.*` dan `wms.fg.*` dan membengkakkan katalog. Tahap pertama menyamakan dengan matriks FE yang berlaku; kemungkinan arah: cakupan mirip `reach`, bukan permission baru.
- **Perilaku saat pemakai membuka URL tanpa hak**: halaman 403 yang menyebut permission yang dibutuhkan, atau pengalihan ke dashboard (perilaku WMS sekarang). Perlu satu perilaku seragam.
- **Peran "admin pusat"** masih dipetakan interim ke `system_roles.group = admin` (lihat [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]); hubungannya dengan modul `admin` di katalog ini perlu dirapikan.

## Terkait

- [[CORE - RBAC dan Permission Set]] (katalog lengkap, paket, dan status penegakan per service)
- [[Microservices - Employee Service]] (master posisi, permission-set, resolusi izin saat login) · [[Microservices - Task Management Service]] (pilot yang sudah jalan)
- [[Microservices - Payroll Service]] · [[Microservices - Manufacture Service]] · [[Microservices - Recruitment Service]]
- [[CORE - API Master Gateway]] (stempel header identitas dari klaim JWT) · [[CORE - SSO Flow]]
- [[APP - Web ERP]] (penyaringan menu & tombol) · [[HRIS - Organization Structure]] (posisi & departemen sebagai master)
- [[DB - Data Dictionary]] (`master_permission_set` dan `permission_sets` belum terdaftar di sana)
- [[ADR - 0003 SSO-only Gateway]] · [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]

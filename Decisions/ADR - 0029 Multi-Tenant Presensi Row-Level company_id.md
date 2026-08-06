**Status**: ⚠️ Implemented (ada catatan). Fase 1 (Presensi) + Fase 2 parsial sudah di `main`; perusahaan kedua (ELT) sudah terdaftar & terpakai di dev; payroll, recruitment, HRD-document, dan task-management BELUM ter-scope.

## Context

Bharata Group ingin sistem **presensi** bip-erp dipakai perusahaan lain di bawah grup (multi-tenant), bukan hanya PT Bharata Internasional (BIP). Kondisi awal (grounded): presensi implisit **single-tenant** — tak ada penanda perusahaan di model karyawan/presensi; JWT & header `BIP-*` tanpa company; mesin fingerprint, koordinat GPS, dan WiFi hardcoded satu kantor. Pemisahan yang ada hanya per-departemen. Entitas "Company" sebelumnya cuma di payroll (kop slip gaji), bukan batas data.

## Decision

Multi-tenant **satu database** dengan penanda **`company_id` row-level** (BUKAN instance/DB terpisah), disaring di lapisan bersama.

- `company_id` = key perusahaan (mis. `"BIP"`, `"PGL"`); default `common.DefaultCompanyID = "BIP"`. Disimpan di `work_data`, klaim JWT, dan header `BIP-Company-ID`.
- **Gateway** meng-inject `BIP-Company-ID` + `BIP-System-Roles` dari klaim JWT ke **semua** request internal (`routes.Reroute`); service-to-service diteruskan via `InternalRequest`.
- `common.CompanyID(c)` = perusahaan **penulis** (dipakai di create/stamp); `common.EffectiveCompanyID(c)` = perusahaan **pembaca**, menghormati override `?company=` **hanya** untuk central admin. `IsCentralAdmin` = **`system_roles.group = admin`** (`common.SystemRoleGroup`, `shared-library/common/company_scope.go:27`). Pemetaan interim ke `system_roles.it` supervisor/admin **sudah DICABUT** supaya "admin IT" dan "admin grup" terpisah; regresinya dikunci `shared-library/common/company_scope_test.go`.
- **BIP = perusahaan default**; data lama di-backfill `company_id=BIP`; fallback di mana-mana → perilaku BIP tak berubah (gerbang regresi wajib).
- Master perusahaan: collection `master_company` (`key`/`name`/`code`) + CRUD `/master/companies` (gate IT supervisor). `code` = prefix `employee_id` per perusahaan (wajib & unik).
- Capture presensi via **MyBharata mobile** — ter-scope otomatis via JWT (interceptor kirim Bearer; endpoint tak kirim identitas perusahaan). **Admin pusat** = peran `system_roles.group = admin` (`common.IsCentralAdmin`, `shared-library/common/company_scope.go:27`; gerbang rute `common.RequireCentralAdmin`, `roles.go:94`), **bukan lagi** IT supervisor/admin. Pemberiannya dijaga `preserveCentralAdminRole` (`services/employee/central_admin.go:21`): `PATCH /account/roles` digerbang `RequireITStaff`, jadi tanpa penjagaan itu staf IT bisa mengangkat dirinya sendiri jadi admin grup. Frontend masih memakai patokan interim lama, lihat §Masih terbuka.

## Scope Fase 1 (di `main`)

Paket **presensi penuh**: absen, jadwal, izin/cuti/sakit + approval, laporan HR. Plus:
- Fondasi: `company_id` di `work_data`/JWT/header, `master_company`, migrasi backfill BIP.
- Attendance: `company_id` di 10 struct koleksi + stempel saat create + saring jalur utama (`/entries`, `/today` team, `/mood`, `/report`, HR admin, review koreksi/dinas, cron entry, wifi/fingerprint WFO, notification FCM).
- Web (erp-frontend): halaman **Kelola Perusahaan** `/hris/companies`, **pemilih perusahaan admin pusat** di header (kirim `?company` ke presensi), **Buat Karyawan** pilih-perusahaan-dulu + prefix ikut perusahaan.
- Mobile (my-bharata): identitas perusahaan di **Profil Perusahaan** (dari `/me`) + **onboarding** (dari respons login), gate profil lengkap ke BIP.

## Consequences / Known Limitations (audit 2026-07-24, disegarkan 2026-07-28)

**Attendance (in-scope) — hardening:**
- **Batch A (PR #653):** hari libur (`resolveEmployeeSchedule` + `/holiday` GET/DELETE), filter reviewer leave & tukar jadwal (`/request/view`,`/review`, `/schedule-exchange/*`, `/hr/requests/detail`), `/guestbook` GET, `/request/security-lookup`+`verify`, `PATCH /:id/update`, review koreksi, komentar telat guestbook → **ter-scope `company_id`**. (Libur kini per-perusahaan: perusahaan baru mengelola daftar liburnya sendiri, termasuk nasional.)
- **A5 supervisor-lookup (PR #655):** employee `/list?type=supervisor` + attendance `getSupervisorData` (8 call-site + cron) ter-scope `company_id` via query param (sebab `InternalRequest(nil)` tak forward header). **Masih terbuka:** cron satu sweep global.
- **Batch B (PR #656):** `company_work_schedule` + `company_group_rotation` ber-`company_id` (kepemilikan; lookup resolusi jadwal tetap by `schedule_id`/`group_id` yang **unik global** — sengaja, agar hot-path resolusi inti tak diubah) + seed BIP aman restart (`DeleteMany` BIP, bukan `Drop`) + CRUD `/company-work-schedule` (list/create/delete, **ENFORCE `schedule_id` unik global** = jaminan isolasi). FE Kelola Shift = erp-frontend #501.
- **Fingerprint per-perusahaan (PR #657):** koleksi `company_fingerprint` (serial→tenant+lokasi, serial unik global) menggantikan allowlist + koordinat hardcoded; `/tap` fingerprint scope entry ke perusahaan pemilik mesin. **Temuan:** GPS mobile TAK dipakai untuk radius (jadwal WFA hanya butuh lokasi ADA), jadi hardcode GPS bukan blocker pilot mobile; hanya website `/tap` (501) yang masih pakai koordinat tetap.
- **CRUD rotasi shift (PR #658):** `/company-group-rotation` (list/create/delete, `group_id` unik global) untuk perusahaan shift bergilir.
- **FE kelola fingerprint + FE kelola rotasi sudah ADA** (lihat §Fase 2), jadi tak lagi jadi item terbuka.

**Di LUAR fase 1 (belum ter-scope, per desain, fase lanjut):**
- **Payroll** — `company_id` = badan usaha penggaji (kop slip), **BUKAN tenant** (`services/payroll/models_employee_salary.go:31`); `listEmployeeSalaries`/run/THR campur semua perusahaan.
- **Recruitment** — tanpa field company; portal karir publik (`/public/postings`, `/apply`) bersama semua tenant.
- **HRD-document** — distribusi global (`my/documents` + `target:all` sampai ke semua tenant).
- **Task-management (Helpdesk IT)** — tanpa field company; tiket bercampur lintas perusahaan.
- **Departemen per-perusahaan** — ✅ **live di main via PR #652**: `master_department.company_id` + scope `/data-type/department`,`/position`,`/master/departments` (`EffectiveCompanyID`) + migrasi backfill BIP. (Catatan proses: PR #649 sempat **ter-orphan** ke branch stacked yang sudah mati, lalu dipulihkan via #652.)
- **Employee directory** — ✅ **sudah ter-scope** sejak F2-A (PR #659), lihat §Fase 2. Sisa: pengelompokan KPI (`kpi_group`) + supervisor-lookup masih berbasis nama departemen, jadi dua perusahaan dengan nama departemen sama bisa ter-merge.

**Sudah aman:** gateway (header ke semua service), notification FCM (personal/dept/broadcast ter-scope + `/list?type=fcm-token` filter company), core employee create + `/me` + respons login onboarding.

## Fase 2 (lanjutan, sudah di `main` 2026-07-24 sampai 2026-07-25)

- **F2-A direktori & agregat karyawan (PR #659)** — helper `companyEmployeeIDs(c)` (`services/employee/company.go:19`) membatasi jalur yang berangkat dari `personal_data`/`system_authentication` (dua koleksi itu tak punya `company_id`) ke himpunan karyawan perusahaan pembaca. Ter-scope: `/v2/internal/aggregate/employees`, `/summary`, `/it`, `/list?type=employee`, `/internal/export/all`, `handleEmployeeView`, plus sub-list sensitif headcount, KPI, `kpi/dashboard`, contract, BPJS, analysis, birthdays, vacation. Index `{company_id, employee_id}` dipasang saat seed (covered query).
- **Orchestrator meneruskan `?company` (PR #660)** — `orchestrator/hris` (`/employees/v2/multi/summary`, `/employees/export`) sempat membuang query string sehingga override admin pusat hilang (direktori benar, summary tetap angka BIP). Kini diteruskan.
- **Katalog jadwal data-driven (PR #661)** — `GetScheduleType` yang hardcoded menolak `schedule_id` milik perusahaan lain (mis. `ELT-REGULAR`), jadi onboarding jadwal perusahaan baru butuh ubah kode shared-library. Kini resolusi tipe jadwal dibaca dari `company_work_schedule` (static) / `company_group_rotation` (pattern) dengan fallback katalog lama; endpoint `/sync/company-group-rotations` menyusul. Hot-path presensi (cron & clock-in) sengaja tak disentuh.
- **Artikel Informasi ter-tenant + broadcast grup (PR #662)** — `GET /article` sebelumnya global sehingga karyawan ELT melihat pengumuman BIP (ketahuan saat uji mobile). Kini `Article` punya `company_id` + `group_wide`; baca = perusahaan pembaca ATAU `group_wide`, tulis distempel `CompanyID(c)`, dan `group_wide` hanya boleh diset admin pusat. Ada migrasi backfill artikel lama ke BIP.
- **Admin pusat kelola WiFi perusahaan lain (PR #663)** — `getCompanyNetworks`/`add`/`delete` naik ke `EffectiveCompanyID` supaya WiFi kantor perusahaan pilot (yang tak punya user IT sendiri) bisa didaftarkan admin pusat. Verifikasi clock-in WFO tetap memakai `CompanyID` (karyawan absen di WiFi perusahaannya sendiri).
- **Web (erp-frontend, semua di `main`)** — `CompanySwitcher` dipindah ke footer sidebar, Kelola Rotasi + Mesin Fingerprint per perusahaan di `/hris/schedule`, Kelola Network ikut switcher, toggle "Bharata Group" di form artikel, dan direktori/agregat karyawan ikut perusahaan terpilih (F2-A FE).
- **Mobile (my-bharata, PR #89/#90/#91 merged ke `dev`, versionCode 120, belum naik ke `main`)** — identitas perusahaan dari `/me` + onboarding, konten beranda dinamis per tenant (blok "Tentang Perusahaan" & "Bharata Community" khusus BIP), nama perusahaan di kartu cuaca & QR lanyard, dan menu **Pengajuan disembunyikan untuk non-BIP** selama pilot. Konsekuensi: tenant baru praktis dapat absen + jadwal saja di mobile, bukan paket presensi penuh seperti tertulis di §Scope Fase 1.

## Perbaikan jalur edit karyawan (2026-07-30, branch — belum merge)

Audit yang berangkat dari keluhan nyata (form **Edit Data Pekerjaan** karyawan ELT menampilkan departemen/jabatan BIP) menemukan **dua** cacat berbeda pada jalur yang sama. Keduanya diperbaiki di branch `fix/employee-partial-update` (bip-erp) + `fix/edit-workdata-company-scope` (erp-frontend); **belum merge, belum deploy**.

**1. Dropdown master data tak ter-scope (FE).** `edit-workdata.tsx` memanggil `/data-type/department` dan `/position` **tanpa** parameter `company`, sehingga `EffectiveCompanyID` jatuh ke perusahaan pemakai yang login. BE sudah benar sejak PR #652; yang tertinggal jalur edit. Form **Buat Karyawan** (`create-employee/step1.tsx`) sudah mengirimnya sejak awal. Perbaikan: `work_data.company_id` dialirkan dari `work.tsx` ke modal. Menyusul dari itu, karena perusahaan pilot bisa belum punya `master_department` sama sekali, nilai tersimpan karyawan disisipkan sebagai opsi (`lib/select-options.ts`) agar tak lenyap dari pilihan lalu terhapus saat disimpan.

**2. Orchestrator menimpa field yang tak dikirim FE (BE).** `UpdateWorkData`/`UpdatePersonalData` (`orchestrator/hris/employee_route.go`) mem-parse body parsial ke **struct penuh** lalu me-`json.Marshal` ulang. Karena `company_id` dan `photo` tak ber-`omitempty`, dan `omitempty` **tidak berlaku untuk struct** di `encoding/json` (sehingga `vacation` ikut terpancar), setiap simpan form menulis: `work_data.company_id = ""`, `work_data.vacation` ter-nol-kan (kuota cuti hilang), dan `personal_data.photo` dikosongkan. Ditambah `UpsertMetadata` pada payload tanpa metadata selalu masuk cabang `created_*`, sehingga jejak pembuatan tertimpa waktu edit dan `updated_*` tak pernah tercatat.

Perbaikan: orchestrator meneruskan body sebagai **map** (`orchestrator/hris/partial_update.go`), dan employee-service menstempel audit lewat **dot-notation** `metadata.updated_at`/`updated_by` (`services/employee/partial_update.go`) supaya `created_*` tak tersentuh.

**Status kerusakan di dev (verifikasi 2026-07-30):** belum terjadi. **Nol** dokumen ber-`company_id` kosong, dan tak ada `vacation` yang ter-nol-kan jalur ini. Sebabnya 31 dokumen yang membawa jejak jalur edit itu terakhir disentuh sekitar **25 Mei 2026**, yaitu **sebelum** `company_id` (24 Juli 2026) dan `Vacation` masuk struct `WorkData` — dibuktikan 14 di antaranya bahkan tak punya field `vacation` sama sekali. **Produksi belum diperiksa.** Yang sudah terlanjur rusak justru tipe BSON-nya (lihat §Masih terbuka).

## Status pilot (verifikasi live dev 2026-07-28)

Lewat gateway dev `10.10.10.121:6969` (read-only, akun admin pusat):

- `master_company` = **2 tenant**: `BIP` (PT Bharata Internasional, prefix `BIP-`) dan `ELT` (CV Elit, prefix `ELT-`, dibuat 2026-07-24 oleh `BIP-0221-10-25`).
- Isolasi terbukti di `/v2/internal/aggregate/employees/summary`: `?company=BIP` → 169 karyawan, `?company=ELT` → 1 karyawan (departemen "Operasional").
- ELT sudah punya jadwal `ELT-REGULAR` (Senin sampai Jumat 08:00-17:00, Sabtu 08:00-13:00, `remote:false`).
- **Belum lengkap untuk go-live pilot**: `master_department` ELT masih **0** (dropdown departemen ELT kosong walau karyawannya sudah berdepartemen), `company_group_rotation` ELT 0, dan **WiFi kantor ELT masih kosong** padahal jadwalnya WFO. PR #663 dibuat justru agar admin pusat bisa mendaftarkan WiFi itu, tapi datanya belum diisi.

## Akun tanpa `work_data` (pihak luar) — ditutup 2026-08-04, PR [#956](https://github.com/bip-itteam-internal/bip-erp/pull/956)

Seluruh ADR ini bertumpu pada satu asumsi diam-diam: **setiap pemegang akun punya `work_data`**. Akun pihak luar (vendor/mitra) mematahkannya, dan akibatnya `resolveCompanyID` jatuh ke `DefaultCompanyID` sehingga tiap vendor **diam-diam tercatat sebagai tenant BIP** — fail-open, tanpa satu pun galat.

- Perbaikannya: koleksi `external_account` menyimpan `company_id` sendiri, dan `companyIDAkun` (`services/employee/external_account.go`) memilih sumbernya berdasarkan `system_authentication.account_type` — `work_data` untuk karyawan, `external_account` untuk pihak luar. Karyawan tetap memakai jalur lama apa adanya (dikunci uji).
- **Konsekuensi untuk ADR ini**: `external_account` adalah koleksi employee **kedua** (selain `work_data`) yang memegang `company_id` kanonis. Jalur mana pun yang menurunkan tenant dari `work_data` wajib menyadari akun tanpa `work_data`, bukan menganggap ketiadaannya sebagai "data lama BIP".
- Akun luar **tak masuk** himpunan `companyEmployeeIDs` (yang berangkat dari `work_data`), jadi otomatis terkecualikan dari direktori & agregat karyawan — diperiksa, bukan diasumsikan.
- Masih terbuka di sisi ini: `permission_sets` untuk akun luar belum dipasang, sehingga akun vendor bisa login tapi belum berhak atas modul apa pun. Detail: [[Microservices - Employee Service]] §Akun pihak luar.

## Masih terbuka

- **Cron presensi satu sweep global** — `cronScheduleCheck` membaca seluruh `work_schedule` tanpa filter perusahaan (`services/attendance/cron.go:62`). Entri hasilnya tetap ber-`company_id` (diturunkan dari `work_schedule`), jadi bukan kebocoran data, tapi belum ada pemisahan per tenant (mis. zona waktu / jadwal cron sendiri).
- **Definisi admin pusat BEDA antara FE dan BE** — peran resmi di BE kini `system_roles.group = admin` (lihat §Decision), tapi FE masih memakai patokan interim lama `isSupervisorOrAdmin(systemRoles?.it)` untuk memutuskan siapa yang melihat `CompanySwitcher` (`erp-frontend/src/components/layout/sidebar.tsx:89`, dipasang di footer sidebar baris 630). Akibatnya FE bisa menampilkan pemilih perusahaan dan mengirim `?company=` untuk user yang override-nya justru diabaikan BE. Titiknya kini **tinggal satu**: `/hris/schedule` tak lagi memilih perusahaan di level halaman (hanya `isItMember` untuk menampilkan tab fingerprint), sebab perusahaan terpilih mengalir lewat cookie `selected_company` yang ditempelkan interceptor axios ke semua GET ber-scope perusahaan (`erp-frontend/src/lib/axios.ts:120-128`).
- **`executeEmployeeUpdateTransaction` bisa mengosongkan tenant** — `$set: update.WorkData` tanpa `defaultWorkCompany` (`services/employee/func.go:205`), dan `WorkData.CompanyID` ber-tag `bson:"company_id"` **tanpa** `omitempty`, jadi payload yang tak menyertakan `company_id` menimpanya jadi `""`. Jalur create sudah aman (`func.go:58` + `func.go:114`). **Masih terbuka**; jalur ini BUKAN yang dipakai form Web ERP (lihat butir berikut).
- **Korupsi tipe BSON di jalur update parsial** — `PUT /update/:employee_id/work` dan `/personal` (`services/employee/main.go`) mem-parse body ke `map[string]interface{}` lalu men-`$set` apa adanya, sehingga tanggal tersimpan sebagai **string** dan angka sebagai **double**, padahal model mendeklarasikan `time.Time` dan `int`. Terverifikasi di DB dev 2026-07-30: **31 dari 179** `work_data` punya `join_date`/`contract_ending` string, `fingerprint_id` double, dan `metadata.created_at` string; **6** `personal_data` punya `date_of_birth` string. Dokumen itu gagal didekode ke struct. Belum diperbaiki dan belum ada migrasi.

## Terkait

- [[Microservices - Attendance Service]] · [[Microservices - Employee Service]] · [[Microservices - Notification Service]] · [[Microservices - Payroll Service]] · [[Microservices - Recruitment Service]] · [[Microservices - HRD Document Service]]
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] · [[DB - Overview and Notes]]
- [[APP - MyBharata]] · [[APP - Web ERP]]
- [[ADR - 0002 Database-per-Service]] (multi-tenant di sini = row-level dalam DB per-service, bukan DB per-tenant)

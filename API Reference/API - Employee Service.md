## Deskripsi

*Endpoint **employee-service** (HRIS inti: data karyawan, auth, KPI, jadwal, dokumen). Gateway: `/api/employee/*`. Grounded ke `services/employee/main.go`.*

- **Implementasi**: [[Microservices - Employee Service]] · **Status**: ✅
- **Indeks**: [[API - Index]] · **RBAC**: `RequireHRISStaff` (HR), `RequireITStaff` (IT), `RequireKPIDepartmentRBAC`, header-based (`/me`), sisanya internal/open.

## Auth & Onboarding
| Method | Path | Fungsi |
|---|---|---|
| POST | `/auth/login` · `/auth/login-pin` · `/auth/login-biometrics` | Login (dipakai gateway) |
| GET | `/auth/refresh` · POST `/auth/verify-pin` | Refresh / verifikasi PIN |
| POST | `/onboarding/register` | Aktivasi akun karyawan baru (handoff) |
| GET | `/qr/:employee_id` · `/data-type/:dt` · `/check-unique/:field/:value` | QR profil, enum, cek unik. `/data-type/department?grouped=true` menggabungkan departemen satu tim jadi **satu opsi** berlabel kelompok (mis. `HRGA`) yang bisa dikirim balik apa adanya sebagai filter; **opt-in** karena sebagian halaman justru perlu departemen satuan |

## Personal & Work Data
| Method | Path | Fungsi |
|---|---|---|
| POST/GET/PUT/DELETE | `/create|get|update|delete/:employee_id/personal` | CRUD personal_data |
| POST/GET/PUT/DELETE | `/create|get|update|delete/:employee_id/work` (+ `/get/list/work`) | CRUD work_data |
| GET | `/birthdays` `?month=1-12` | Karyawan **aktif** (`is_active`) yang ulang tahun per bulan (default bulan berjalan): nama/posisi/dept/foto/umur, urut per tanggal; field aman (tanpa NIK/KK/alamat). `date_of_birth` di-handle string/Date + konversi WIB |
| POST/GET/GET/PUT/DELETE | `/.../:employee_id/personal-documents` (by `:doc_type`) | Dokumen pribadi |
| POST/GET/GET/PUT/DELETE | `/.../:employee_id/work-documents` (by `:doc_type`) | Dokumen kerja |
| POST/GET/PUT/DELETE | `/.../:employee_id/schedule` · GET `/sync/work-schedules` | Jadwal kerja |

## System Auth & Account
| Method | Path | Fungsi |
|---|---|---|
| POST/GET/PUT/DELETE | `/.../system-auth` | Kredensial/role akun |
| PUT/GET | `/internal/auth/change-password/:username` · `/roles/:username` · `/disable/:employee_id` · `/user/:username` · `/employee/:employee_id` | Internal auth mgmt |
| PATCH/GET | `/account/active-status` · `/forget-device` · `/reset` · `/roles` | Kelola akun (RequireITStaff) |
| GET/POST/DELETE | `/device` · `/web-browser` | Perangkat & sesi browser |

## Master Data (departemen & system role)
| Method | Path | Fungsi | RBAC |
|---|---|---|---|
| GET | `/master/departments[/:key]` · `/master/system-roles` | List/detail master | open (di belakang gateway) |
| POST/PUT/DELETE | `/master/departments[/:key]` | CRUD departemen (key, name, positions, roles, **supervised_by**, **supervision_label**). ⚠️ `PUT` memakai `ReplaceOne`; dua field terakhir **dipertahankan** bila tak disebut di body, supaya pemanggil yang hanya mengirim sebagian field tak memutus relasi supervisi. Kirim eksplisit (boleh string kosong) untuk melepasnya — itu yang dilakukan form `/hris/master-data` | `RequireHRISOrITSupervisor` (supervisor/admin HRIS **atau** IT) |
| POST/PUT/DELETE | `/master/system-roles[/:key]` | CRUD definisi system role | `RequireITSupervisor` (supervisor/admin IT) |
| PUT | `/master/departments/:key/positions/:positionKey/menu-hidden` | Url menu yang **disembunyikan** dari sidebar bagi pemegang jabatan itu. **Setelan tampilan, BUKAN hak akses**: hanya mengurangi yang sudah boleh dilihat, tak pernah menambah, dan rutenya tetap terbuka lewat URL. Menyentuh satu posisi saja. Daftar kosong = tak menyembunyikan apa pun (aksi sah). Entri tanpa `/` di awal dibuang karena tak akan pernah cocok dengan menu mana pun | `RequireHRISOrITSupervisor` — sengaja lebih longgar daripada `permission-sets` karena tak bisa menaikkan hak siapa pun |
| GET | `/master/job-levels` | Tangga jenjang jabatan (`key`, `name`, `rank`), urut rank menaik. Lima baris berisi nama tingkat, tak memuat data siapa pun | open (di belakang gateway) |
| PUT | `/master/departments/:key/positions/:positionKey/level` | Jenjang jabatan sebuah posisi (`{"level_key":"supervisor"}`). **Penanda organisasi, BUKAN hak akses.** String kosong = melepas jenjang (aksi sah). Key tak dikenal **ditolak 400** beserta daftar key yang sah — jenjang hantu tak akan pernah tampil dan pemasangnya menyangka sudah tersimpan. Menyentuh satu field pada satu posisi; `permission_sets` & `menu_hidden` tak tersentuh. Berlaku **seketika** (tak ikut token, beda dari `permission-sets`) | `RequireHRISOrITSupervisor` — sama dengan `menu-hidden`, karena tak menaikkan hak siapa pun |

> Konsumen FE: halaman `/hris/master-data` (di-link dari **menu IT**) & System Setup Personalia; tombol kelola disembunyikan bila role tak berhak.

## Akun pihak luar (vendor/mitra) — ⚠️ merged, tanpa role & tanpa UI
> Fondasi data untuk orang di luar perusahaan yang butuh akun, tanpa dijadikan record karyawan. Seluruh grup digerbang `RequireITSupervisor` — sengaja **lebih ketat** dari master data lain, karena ini menerbitkan kredensial, bukan mengelola data HR. Detail & alasannya: [[Microservices - Employee Service]].

| Method | Path | Fungsi | RBAC |
|---|---|---|---|
| GET | `/master/external-accounts` | Daftar akun luar milik perusahaan pembaca (`EffectiveCompanyID`) | `RequireITSupervisor` |
| POST | `/master/external-accounts` | Terbitkan akun luar + baris kredensial di `system_authentication` (`account_type=external`). ID di-generate server berprefiks **`EXT-`**; `company_id` diisi dari perusahaan pembuat bila kosong. **Ditolak 400** bila `valid_until` sudah lewat (akun terbit dalam keadaan mati) atau `sponsor_employee_id` tak ada di `work_data` (penanggung jawab karangan = akun tanpa pemilik). Bila insert kredensial gagal, data pendamping di-rollback supaya tak tertinggal akun setengah jadi | `RequireITSupervisor` |
| PUT | `/master/external-accounts/:employeeID` | Perbarui data pendamping; **perpanjangan `valid_until`** adalah alasan utamanya ada. `employee_id` & `company_id` **tak bisa diubah** (kunci identitas & batas tenant). Field kosong diabaikan, bukan dikosongkan | `RequireITSupervisor` |
| DELETE | `/master/external-accounts/:employeeID` | **Menonaktifkan** (`is_active=false`), bukan menghapus — jejak siapa pernah punya akses tetap ada. ⚠️ Token yang sudah beredar **tidak ikut mati** (JWT TTL 72 jam, revoke masih placeholder); respons menyebutkannya eksplisit | `RequireITSupervisor` |

> 🔴 **Belum ada konsumen FE.** Pembuatan vendor sementara hanya lewat API. `permission_sets` untuk akun luar juga belum dipasang, jadi akun terbit bisa login tapi belum berhak atas modul apa pun.
> ⚠️ Itu baru benar **setelah** penambalan `izinAkun`: sebelumnya akun vendor tanpa paket diam-diam dapat 6 izin modul `ticket` lewat fallback tier. Lihat [[Microservices - Employee Service]] §Akun pihak luar.

## Training Program (HRIS) — ✅ merged (deploy dev pending)
> BE+FE **merged ke main** (`services/employee/training.go`; UI `/hris/training`); **deploy dev pending**. **Department opsional** (peran penyelenggara — TIDAK membatasi peserta; peserta lintas dept di-assign HRD), tanpa Branch. RBAC tulis = `RequireHRISStaff`; GET open (di belakang gateway). Detail konsep: [[HRIS - Training Program]].

| Method | Path | Fungsi |
|---|---|---|
| GET · POST | `/training/types` · `/training/trainers` | List / buat master jenis pelatihan & trainer (internal/eksternal) |
| GET · PUT · DELETE | `/training/types/:id` · `/training/trainers/:id` | Detail/ubah/hapus master (by ObjectID) |
| GET · POST | `/training` (`?department_key=&status=`) | List / buat event pelatihan (cek FK type/trainer; department **opsional**) |
| GET · PUT · DELETE | `/training/:id` | Detail / ubah (guard transisi status) / hapus (cascade peserta) |
| GET · POST | `/training/:id/participants` | List / enroll peserta (unique index anti-duplikat, **tanpa cap keras** — kapasitas = jumlah peserta; FE assign multi-select lintas dept) |
| PATCH · DELETE | `/training/:id/participants/:employeeId` | Tandai kehadiran (boolean) / batalkan peserta |
| GET | `/training/history/:employeeId` | Riwayat pelatihan per karyawan |

## KPI · Vacation · Reports (HRIS)
| Method | Path | Fungsi | RBAC |
|---|---|---|---|
| GET/POST | `/kpi` · `/kpi/dashboard` · `/kpi/templates` | KPI score + template. `GET /kpi` filter `?department=` (boleh **beberapa dipisah koma** → semua harus berhak), `?period=YYYY-MM`, `?status=`. Departemen yang satu tim otomatis digabung dari master data; `?merge=` + `?merge_label=` untuk penggabungan ad-hoc (detail: [[HRIS - Key Performance Index]]) | KPIDepartmentRBAC / HRIS |
| GET | `/kpi?scope=team` | KPI **bawahan langsung** pemanggil (Leader). Gerbangnya **keberadaan bawahan aktif**, bukan role — Leader ber-role `staff` selalu ditolak KPIDepartmentRBAC. Filter `?department=` diabaikan: cakupannya orang. Tanpa bawahan aktif → 403 | Punya bawahan |
| GET | `/kpi/auto-values` | ⚠️ **belum merge** (branch `feat/kpi-auto-value`). Pratinjau nilai otomatis metrik KPI, **read-only**. Query wajib `employee_id`·`period=YYYY-MM`·`template_id`. Balasan per metrik: `key`·`label`·`source` (`otomatis`/`semi`/`manual`)·`auto_value`·`auto_basis`·`auto_cakupan`. Metrik tanpa konfigurasi `auto` selalu `manual`; hitungan gagal juga jatuh ke `manual` dengan alasannya di `auto_basis`, tidak diisi angka. Detail: [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] | KPIDepartmentRBAC |
| GET/PUT | `/supervisor-assignment` | Baca & tetapkan **atasan langsung** per departemen. GET `?department=` menerima **nama departemen ATAU label grup** (`HRGA`) dan memekarkannya ke satu tim penuh lewat `ResolveDepartmentFilter`+`ExpandToDepartmentGroup` — sama seperti `/kpi`, jadi meminta satu anggota mengembalikan seluruh grupnya. Nama tak dikenal master dipakai apa adanya, bukan dijawab kosong. Balasan: `employee_id`·`full_name`·`position`·`supervisor_id`·`is_supervisor`·**`is_active`**. PUT semua-atau-tidak: satu baris tak sah membatalkan seluruh permintaan + daftar masalahnya; `supervisor_id` kosong = melepas atasan | HRIS/IT staff |
| GET | `/org-chart` | **Bagan organisasi**: seluruh karyawan **aktif** satu perusahaan + daftar departemennya, satu panggilan. Mengirim daftar **DATAR** (`employee_id`·`full_name`·`position`·`department`·`supervisor_id`·`is_supervisor`), bukan pohon jadi — penyusunan pohon **beserta penjaga siklusnya** dikerjakan FE supaya bisa diuji tanpa render. Departemen ikut dikirim karena dipakai FE sebagai kerangka. Ikut dikirim `groups` (label kelompok supervisi → daftar nama departemen anggotanya, **induk lebih dulu**; dari `DepartmentGroups`, sumber yang sama dengan `/kpi` dan `/supervisor-assignment`), dipakai FE untuk melebur departemen se-kelompok jadi SATU simpul (mis. `HRGA`). Sengaja dihitung di BE supaya aturan `supervised_by` tidak disalin ke TypeScript; kosong `{}` bila tak ada relasi supervisi, dan FE jatuh ke gambar per departemen | `RequireHRISOrITSupervisor` — menampilkan seluruh nama & garis pelaporan satu perusahaan sekaligus |
| GET/POST | `/vacation` · `/vacation/quota` · `/vacation/decrement` | Kuota & pemakaian cuti | HRIS (decrement: open) |
| GET/PATCH | `/contract` · `/bpjs` · `/analysis` | Kontrak (filter `department`/`employment_type`/`status`/`ending_month`=`YYYY-MM` berdasar `contract_ending`), BPJS, analisis | HRIS |
| GET | `/internal/aggregate/employee/:id` · `/v2/internal/aggregate/employees[/summary|/it]` · `/internal/export/all` | Aggregate & export | HRIS / IT |
| POST/PUT | `/internal/transaction/create-employee` · `/update-employee/:id` | Bulk create/update employee | HRIS |

## Listing · View · Me
| Method | Path | Fungsi |
|---|---|---|
| GET | `/list` · `/view` · `/personal` · `/work` · `/schedule` · `/system` | Daftar & view tab |
| GET/POST | `/me/` · `/me/kpi-score` · `/me/vacation` · `/me/payroll-approx` · `/me/photo` | Profil sendiri (header) |
| GET | `/me/subordinates` | Bawahan **langsung** yang akunnya aktif. Dipakai FE untuk menentukan menu KPI di Portal Saya tampil, dan mengisi halamannya |
| GET | `/me/menu-hidden` | Url menu yang disembunyikan bagi posisi pemanggil. Departemen & posisi **diselesaikan di server** dari `work_data`, bukan diterima sebagai query: FE hanya menyimpan NAMA posisi di cookie, dan nama jabatan tidak unik lintas departemen ("GA Staff" dipakai dua peran). Pencocokan departemen **case-insensitive**, sama seperti kode pemetaan departemen lain. Kegagalan membalas daftar kosong (200), bukan error: sidebar yang gagal memuat setelan harus menampilkan menu apa adanya |
| POST | `/upload` · `/upload/multiple` | Upload file |

> ~90 endpoint. Daftar lengkap path per `:doc_type`/method ada di `services/employee/main.go`.

## Dokumen Terkait
- [[Microservices - Employee Service]] · [[HRIS - Payroll]] · [[HRIS - Key Performance Index]] · [[API - Index]]

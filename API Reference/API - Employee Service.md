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

> Konsumen FE: halaman `/hris/master-data` (di-link dari **menu IT**) & System Setup Personalia; tombol kelola disembunyikan bila role tak berhak.

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
| GET/PUT | `/supervisor-assignment` | Baca & tetapkan **atasan langsung** per departemen (alat isi-massal). PUT semua-atau-tidak: satu baris tak sah membatalkan seluruh permintaan + daftar masalahnya | HRIS/IT staff |
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

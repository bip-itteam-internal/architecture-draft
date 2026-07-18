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
| GET | `/qr/:employee_id` · `/data-type/:dt` · `/check-unique/:field/:value` | QR profil, enum, cek unik |

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
| POST/PUT/DELETE | `/master/departments[/:key]` | CRUD departemen (key, name, positions, roles) | `RequireHRISOrITSupervisor` (supervisor/admin HRIS **atau** IT) |
| POST/PUT/DELETE | `/master/system-roles[/:key]` | CRUD definisi system role | `RequireITSupervisor` (supervisor/admin IT) |

> Konsumen FE: halaman `/hris/master-data` (di-link dari **menu IT**) & System Setup Personalia; tombol kelola disembunyikan bila role tak berhak.

## Training Program (HRIS) — ⚠️ branch `feat/employee-training`
> BE MVP diimplementasi (`services/employee/training.go`), **belum merge ke main / belum deploy**. Org unit = **Department** (`master_department.key`), tanpa Branch. RBAC tulis = `RequireHRISStaff`; GET open (di belakang gateway). Detail konsep: [[HRIS - Training Program]].

| Method | Path | Fungsi |
|---|---|---|
| GET · POST | `/training/types` · `/training/trainers` | List / buat master jenis pelatihan & trainer (internal/eksternal) |
| GET · PUT · DELETE | `/training/types/:id` · `/training/trainers/:id` | Detail/ubah/hapus master (by ObjectID) |
| GET · POST | `/training` (`?department_key=&status=`) | List / buat event pelatihan (cek FK type/trainer/department) |
| GET · PUT · DELETE | `/training/:id` | Detail / ubah (guard transisi status) / hapus (cascade peserta) |
| GET · POST | `/training/:id/participants` | List / enroll peserta (**cap keras** + unique index anti-duplikat) |
| PATCH · DELETE | `/training/:id/participants/:employeeId` | Tandai kehadiran (boolean) / batalkan peserta |
| GET | `/training/history/:employeeId` | Riwayat pelatihan per karyawan |

## KPI · Vacation · Reports (HRIS)
| Method | Path | Fungsi | RBAC |
|---|---|---|---|
| GET/POST | `/kpi` · `/kpi/dashboard` · `/kpi/templates` | KPI score + template | KPIDepartmentRBAC / HRIS |
| GET/POST | `/vacation` · `/vacation/quota` · `/vacation/decrement` | Kuota & pemakaian cuti | HRIS (decrement: open) |
| GET/PATCH | `/contract` · `/bpjs` · `/analysis` | Kontrak, BPJS, analisis | HRIS |
| GET | `/internal/aggregate/employee/:id` · `/v2/internal/aggregate/employees[/summary|/it]` · `/internal/export/all` | Aggregate & export | HRIS / IT |
| POST/PUT | `/internal/transaction/create-employee` · `/update-employee/:id` | Bulk create/update employee | HRIS |

## Listing · View · Me
| Method | Path | Fungsi |
|---|---|---|
| GET | `/list` · `/view` · `/personal` · `/work` · `/schedule` · `/system` | Daftar & view tab |
| GET/POST | `/me/` · `/me/kpi-score` · `/me/vacation` · `/me/payroll-approx` · `/me/photo` | Profil sendiri (header) |
| POST | `/upload` · `/upload/multiple` | Upload file |

> ~90 endpoint. Daftar lengkap path per `:doc_type`/method ada di `services/employee/main.go`.

## Dokumen Terkait
- [[Microservices - Employee Service]] · [[HRIS - Payroll]] · [[HRIS - Key Performance Index]] · [[API - Index]]

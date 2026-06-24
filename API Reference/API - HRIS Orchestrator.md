## Deskripsi

*Endpoint **HRIS Orchestrator** (aksi lintas-service HR: buat employee + dokumen + notif sekaligus). Gateway: `/api/hris/*`. Grounded ke `orchestrator/hris`. RBAC `RequireHRISStaff`.*

- **Implementasi**: [[CORE - HRIS Orchestrator]] · **Status**: ✅
- **Indeks**: [[API - Index]]

## Employees
| Method | Path | Fungsi |
|---|---|---|
| PATCH | `/employees/personal-data` · `/work-data` · `/personal-documents` · `/work-documents` · `/work-schedule` | Update data/dokumen/jadwal (HRIS) |
| GET | `/employees/it` · `/employees/export` | Karyawan IT / export Excel |
| GET | `/employees/v2/multi[/summary]` · `/employees/:employee_id/multi` | Aggregate semua / per-karyawan |
| POST/PUT | `/employees/multi` · `/employees/multi/:employee_id` | Buat/update employee (multipart + dokumen) |
| GET | `/employees/:employee_id/documents/*` | Stream dokumen dari MinIO |
| PUT/POST | `/employees/:employee_id/bank/detail` · `/bank/details` · `/bank/set-active` | Rekening bank |

## Attendances
| Method | Path | Fungsi |
|---|---|---|
| GET | `/attendances/summary` | Ringkasan kehadiran |
| PATCH | `/attendances/:id/update` | Update entri (JSON/multipart + dokumen) |
| GET/POST/DELETE | `/attendances/holiday` · `/holiday/:id` · `/holiday/delete/all` | Hari libur |

## Dokumen Terkait
- [[CORE - HRIS Orchestrator]] · [[Microservices - Employee Service]] · [[Microservices - Attendance Service]] · [[API - Index]]

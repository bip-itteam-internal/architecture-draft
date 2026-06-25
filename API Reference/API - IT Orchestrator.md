## Deskripsi

*Endpoint **IT Orchestrator** (manajemen akun/role/jaringan oleh IT). Gateway: `/api/it/*`. Grounded ke `orchestrator/it`. RBAC `RequireITStaff` (sebagian rute admin-internal).*

- **Implementasi**: [[CORE - IT Orchestrator]] · **Status**: ✅
- **Indeks**: [[API - Index]]

## Akun & Role
| Method | Path | Fungsi |
|---|---|---|
| GET | `/v2/multi` | List semua karyawan IT (aggregate internal) · ITStaff |
| POST | `/roles/get` · `/roles/set` | Ambil / set semua role karyawan |
| POST | `/reset-password` | Reset password karyawan |
| POST | `/account/activate` · `/deactivate` · `/status` · `/toggle` | Aktivasi/nonaktif/status akun |

## Jaringan
| Method | Path | Fungsi |
|---|---|---|
| GET/POST/DELETE | `/network` | List/tambah/hapus jaringan |
| GET | `/health` | Health check |

## Dokumen Terkait
- [[CORE - IT Orchestrator]] · [[IT - Network Management]] · [[Microservices - Employee Service]] · [[API - Index]]

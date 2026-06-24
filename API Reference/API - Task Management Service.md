## Deskripsi

*Endpoint **task-management-service** (task & space ala Kanban; kini diposisikan ticketing/helpdesk). Gateway: `/api/task-management/*`. RBAC `staff`/`supervisor` dari `system_roles["task-management"]`. Grounded ke `services/task-management/routes.go` (branch `main`).*

- **Implementasi**: [[Microservices - Task Management Service]] · **Status**: ✅
- **Indeks**: [[API - Index]]
- > Catatan: branch `feat/sso-task-management` menambah attachment/comment-file/WS/users — di `main` belum (lihat dok implementasi).

## Sistem
| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` · `/me` | Health / identitas user |

## Spaces
| Method | Path | Fungsi |
|---|---|---|
| POST/GET | `/spaces` · `/spaces/:id` | Buat/list/detail space (`?division=`) |
| PUT/DELETE | `/spaces/:id` | Update/hapus space |

## Tasks
| Method | Path | Fungsi |
|---|---|---|
| POST | `/tasks` | Buat task |
| GET | `/tasks/filter` · `/tasks/:id` | Filter/detail task |
| PUT | `/tasks/:id/status` · `/archive` · `/unarchive` · `/due-date` · `/priority` · `/space` | Ubah status/arsip/jadwal/prioritas/pindah |
| PUT/POST | `/tasks/:id/assign` · `/approve` · `/reject` | Assign/approve/reject (supervisor) |
| DELETE | `/tasks/:id` | Hapus task (supervisor) |

## Comments · Checklist · Notifications
| Method | Path | Fungsi |
|---|---|---|
| POST/PUT/DELETE | `/tasks/:id/comments` · `/tasks/:taskId/comments/:commentId` | Komentar |
| POST/PUT/DELETE | `/tasks/:id/checklist` · `/tasks/:taskId/checklist/:itemId[/toggle]` | Checklist |
| GET/PUT/DELETE | `/notifications` · `/notifications/unread-count` · `/read-all` · `/:id/read` · `/:id` | Notifikasi |

## Dokumen Terkait
- [[Microservices - Task Management Service]] · [[APP - Dynamic Task Tracker]] · [[API - Index]]

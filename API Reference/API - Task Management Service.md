## Deskripsi

*Endpoint **task-management-service** (task & space ala Kanban; kini diposisikan ticketing/helpdesk). Gateway: `/api/task-management/*` (WebSocket via ingress langsung ke service). RBAC `staff`/`supervisor` di-derive dari map `system_roles`. Grounded ke `services/task-management/routes.go` + `main.go` (branch `feat/task-management-parity`).*

- **Implementasi**: [[Microservices - Task Management Service]] · **Status**: ⚠️ (branch belum merge; WS butuh rute ingress)
- **Indeks**: [[API - Index]]
- > Catatan: branch `feat/task-management-parity` menambah attachment (via file-service), reports/stats, history/audit, users/departments, WebSocket, dan SLA — melengkapi paritas dengan FE gateway-cutover.

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
| POST | `/tasks` | Buat task (set `response_due_at`+24h, notif supervisor) |
| GET | `/tasks/filter` · `/tasks/:id` | Filter (flag `assigned_to_me`/`created_by_me`/`pending_my_approval`/`filter_by_admin_division`) / detail (populated + `sla`) |
| GET | `/tasks/stats` · `/tasks/admin-stats` | Statistik status FLAT (rentang tanggal) |
| PUT | `/tasks/:id` | Edit generik (partial) |
| PUT | `/tasks/:id/status` · `/archive` · `/unarchive` · `/due-date` · `/priority` · `/space` | Ubah status/arsip/jadwal/prioritas/pindah |
| PUT/POST | `/tasks/:id/assign` · `/approve` · `/reject` | Assign/approve (body `start_date/due_date/priority_id/assign_to`)/reject (supervisor) |
| GET | `/tasks/:id/history` | Riwayat perubahan (array) |
| DELETE | `/tasks/:id` | Hapus task (supervisor) |

## Attachments (via file-service)
| Method | Path | Fungsi |
|---|---|---|
| POST | `/tasks/:id/attachments` · `/tasks/:id/links` | Upload file (field `file`, resp `{attachment}`) / tambah link (resp `{link}`) |
| GET | `/tasks/:id/attachments/:fileId/preview` | Presigned URL preview (`{url}`) |
| DELETE | `/tasks/:id/attachments/:attachmentId` | Hapus lampiran |

## Reports & Users
| Method | Path | Fungsi |
|---|---|---|
| GET | `/report/summary-by-department` · `/report/timeline` · `/report/manpower-performance` · `/report/sla` | Laporan (scope supervisor→divisi, staff→sendiri) |
| GET | `/users` · `/users/byDivision` · `/departments` | Dropdown assignee & divisi (dari ERP) |
| GET | `/audits` | Audit trail lintas-task (`{items,total}`, scope divisi supervisor) |

## WebSocket
| Path | Fungsi |
|---|---|
| `GET /ws?token=<JWT>` | Realtime (bypass gateway, via ingress). Event: `notification`/`task_update`/`space_update` |

## Comments · Checklist · Notifications
| Method | Path | Fungsi |
|---|---|---|
| POST/PUT/DELETE | `/tasks/:id/comments` · `/tasks/:taskId/comments/:commentId` | Komentar |
| POST/PUT/DELETE | `/tasks/:id/checklist` · `/tasks/:taskId/checklist/:itemId[/toggle]` | Checklist |
| GET/PUT/DELETE | `/notifications` · `/notifications/unread-count` · `/read-all` · `/:id/read` · `/:id` | Notifikasi |

## Dokumen Terkait
- [[Microservices - Task Management Service]] · [[APP - Dynamic Task Tracker]] · [[API - Index]]

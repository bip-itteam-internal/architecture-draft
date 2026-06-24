## Deskripsi

*Endpoint **file-service** (proxy MinIO: upload/download/preview/delete + presigned URL). Gateway: `/api/file/*`. Tiap operasi terima service key `?key=` ATAU JWT. Grounded ke `services/file/main.go`.*

- **Implementasi**: [[Microservices - File Service]] · **Status**: ⚠️ (RBAC per-role pada akses file masih TBD — `services/file/main.go:124-137`)
- **Indeks**: [[API - Index]]

## Operasi file
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/preview` | Preview file (`?minio_object=`) | `?key=` atau JWT |
| GET | `/download` | Download file (attachment) | `?key=` atau JWT |
| GET | `/exist` | Cek file ada (bool) | `?key=` atau JWT |
| POST | `/upload` | Upload file (multipart: file, minio_object; max 4MB) | `?key=` atau JWT |
| POST | `/copy` · `/move` | Copy/move object (JSON: source, destination) | `?key=` atau JWT |
| DELETE | `/delete` | Hapus object (`?minio_object=`) | `?key=` atau JWT |

## Presigned URL (internal)
| Method | Path | Fungsi | Auth |
|---|---|---|---|
| GET | `/minio/presigned` | Presigned PUT URL (`?service=inventory&document=purchase|arrived`) | gateway key |
| GET | `/minio/preview` | Presigned GET URL (`?minio_object=`) | gateway key |
| GET | `/health` | Health check | gateway key |

> **Akses key**: write-key per direktori (`employee/`, `attendance/`, `task/`, `notification/`) vs read-only key. RBAC berbasis role pada file masih **TBD** (lihat [[Microservices - File Service]]).

## Dokumen Terkait
- [[Microservices - File Service]] · [[DB - Overview and Notes]] · [[API - Index]]

## Deskripsi

*Storage gateway terpusat yang berjalan di atas **MinIO** sebagai object store; menjadi file server utama untuk seluruh aplikasi. Konsep "folder" diwujudkan sebagai prefix pada nama object, dengan otorisasi per-service melalui access-key. Service ini sengaja dibangun ramping namun fungsional penuh dalam satu file.*

- **Stack:** Go + Fiber v2 + MinIO (tanpa MongoDB)
- **Path:** `services/file` (satu `main.go` ~496 baris, fungsional penuh — bukan placeholder)
- **Status:** ✅ Implemented (1 file by design)

## Endpoint / Fitur (Sudah Diimplementasikan)

- **Health:** `GET /health`
- **Baca (read):**
	- `GET /preview` — stream object dengan content-type sesuai
	- `GET /download` — kirim object sebagai attachment
	- `GET /exist` — cek keberadaan object
- **Tulis (write):**
	- `POST /upload` — multipart, cap 4 MB, mengembalikan metadata `MinIOFile`
	- `POST /copy` — salin object
	- `POST /move` — pindah object
	- `DELETE /delete` — hapus object
- **Presigned URL:**
	- `GET /minio/presigned` — presigned PUT
	- `GET /minio/preview` — presigned GET
- **Otorisasi:** `validateDirectoryAccess` memeriksa access-key (`?key=`) terhadap map write/read per prefix (`employee/`, `attendance/`, `task/`, `notification/`), meng-enforce prefix scoping serta pemisahan read-only vs read-write.

## Belum Diimplementasikan / Catatan

- **Akses via JWT/RBAC tanpa access-key = `501 NotImplemented`** ("native JWT validation with RBAC not supported yet"). Praktis hanya caller ber-access-key yang dapat berjalan.
- Presigned PUT hanya tersedia untuk `service=inventory` (`document=purchase|arrived`).
- `POST /upload` menimpa object yang sudah ada secara diam-diam (silent overwrite), tanpa proteksi atau versioning.

## Dependencies & Integrasi

- **MinIO** — satu-satunya backing store (object store; tanpa database tambahan).
- **Access-key** untuk prefix `employee/`, `attendance/`, `task/`, `notification/` dikonfigurasi via environment variable (pasangan read-write & read-only per prefix).
- Caller yang berintegrasi:
	- [[CORE - API Master Gateway]]
	- [[Microservices - Employee Service]]
	- [[Microservices - Attendance Service]]
	- [[Microservices - Task Management Service]]
	- [[Microservices - Inventory Service]]
- Lihat juga [[DB - Overview and Notes]].

## Dokumen Terkait

- [[CORE - API Master Gateway]]
- [[Microservices - Employee Service]]
- [[Microservices - Attendance Service]]
- [[Microservices - Task Management Service]]
- [[Microservices - Inventory Service]]
- [[Microservices - Notification Service]]
- [[DB - Overview and Notes]]
- [[APP - Mobile Application]]

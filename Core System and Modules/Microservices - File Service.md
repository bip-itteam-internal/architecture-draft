## Deskripsi

*Storage gateway terpusat yang berjalan di atas **MinIO** sebagai object store; menjadi file server utama untuk seluruh aplikasi. Konsep "folder" diwujudkan sebagai prefix pada nama object, dengan otorisasi per-service melalui access-key. Service ini sengaja dibangun ramping namun fungsional penuh dalam satu file.*

- **Stack:** Go + Fiber v2 + MinIO (tanpa MongoDB)
- **Path:** `services/file` (satu `main.go` ~496 baris, fungsional penuh — bukan placeholder)
- **Status**: ✅ Implemented (1 file by design)

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
- **Otorisasi:** `validateDirectoryAccess` memeriksa access-key (`?key=`) terhadap map write/read per prefix (`employee/`, `attendance/`, `task/`, `notification/`, **`form/`**), meng-enforce prefix scoping serta pemisahan read-only vs read-write.

### Prefix `form/` dan perakitan peta akses

> Ditambahkan PR [#1057](https://github.com/bip-itteam-internal/bip-erp/pull/1057), ✅ **live dev + prod 2026-08-06**. Dipakai lampiran [[Microservices - Form Builder Service]] (semua tipe form, termasuk program Kaizen).

"Access key" di sini **bukan kredensial MinIO IAM**, melainkan string rahasia yang dipetakan service ini ke satu prefix direktori. Menambah prefix baru berarti dua sisi: pengirim mengirimkannya sebagai `?key=`, dan service ini yang tahu kunci itu berarti prefix apa. Kalau hanya sisi pengirim yang ditambah, unggahannya dibalas `invalid access key` betapa pun benar nilai env-nya.

**Peta dirakit `bangunAccessMap`, yang MELEWATI env kosong** dan mencatat namanya di log saat boot. Sebelumnya peta dirakit langsung dari `os.Getenv` lalu diperiksa fungsi yang **panic** bila ada kunci kosong, dan itu punya dua akibat buruk:

1. Satu env yang belum diisi **mematikan seluruh file-service** — foto karyawan, bukti presensi, lampiran tiket, semuanya — padahal yang belum siap cuma satu modul. Kelas kegagalan yang sama sudah dua kali menggigit lewat `ValidateInternalURL`.
2. Menambah prefix baru jadi **ranjau deploy**: entri baru wajib sudah ada di `.env` tiap lingkungan sebelum service di-rebuild.

Perubahan itu sekaligus menutup lubang yang tak kentara: env kosong dulu memasukkan kunci `""` ke peta, sehingga permintaan **tanpa** `?key=` cocok dengan prefix itu dan mendapat akses. Panic membuatnya tak terjangkau — tapi hanya selama panic-nya masih ada.

**Panic dipertahankan untuk satu kasus**: dua modul memakai nilai kunci yang sama, yang berarti keduanya bisa saling membaca dan menimpa berkas.

> ⚠️ **`MINIO_PROCUREMENT_KEY` ada di `.env.example` dan dikirim ke procurement-service, tapi TIDAK terdaftar di peta service ini.** Polanya persis sama dengan `form/` sebelum #1057, jadi unggahan bukti kas kecil kemungkinan dibalas `invalid access key`. Belum diverifikasi apakah modul itu sudah dipakai.

## Belum Diimplementasikan / Catatan

- **Akses via JWT/RBAC tanpa access-key = `501 NotImplemented`** ("native JWT validation with RBAC not supported yet"). Praktis hanya caller ber-access-key yang dapat berjalan.
- Presigned PUT hanya tersedia untuk `service=inventory` (`document=purchase|arrived`).
- `POST /upload` menimpa object yang sudah ada secara diam-diam (silent overwrite), tanpa proteksi atau versioning.

## Dependencies & Integrasi

- **MinIO** — satu-satunya backing store (object store; tanpa database tambahan).
- **Access-key** untuk prefix `employee/`, `attendance/`, `task/`, `notification/`, `form/` dikonfigurasi via environment variable (pasangan read-write & read-only per prefix). Konvensi nilainya di prod: 24 karakter heks untuk kunci tulis, dan kunci baca = **12 karakter pertama** kunci tulis.
- Caller yang berintegrasi:
	- [[CORE - API Master Gateway]]
	- [[Microservices - Employee Service]]
	- [[Microservices - Attendance Service]]
	- [[Microservices - Task Management Service]]
	- [[Microservices - Inventory Service]]
	- [[Microservices - Form Builder Service]] — lampiran jawaban, prefix `form/`
- Lihat juga [[DB - Overview and Notes]].

## Dokumen Terkait

- [[CORE - API Master Gateway]]
- [[Microservices - Employee Service]]
- [[Microservices - Attendance Service]]
- [[Microservices - Task Management Service]]
- [[Microservices - Inventory Service]]
- [[Microservices - Notification Service]]
- [[DB - Overview and Notes]]
- [[APP - MyBharata]]

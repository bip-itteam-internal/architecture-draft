## Deskripsi

*Storage gateway terpusat yang berjalan di atas **MinIO** sebagai object store; menjadi file server utama untuk seluruh aplikasi. Konsep "folder" diwujudkan sebagai prefix pada nama object, dengan otorisasi per-service melalui access-key. Service ini sengaja dibangun ramping namun fungsional penuh dalam satu file.*

- **Stack:** Go + Fiber v2 + MinIO (tanpa MongoDB)
- **Path:** `services/file` (satu `main.go` ~609 baris, fungsional penuh — bukan placeholder)
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
- **Otorisasi:** `validateDirectoryAccess` memeriksa access-key (`?key=`) terhadap map write/read per prefix, meng-enforce prefix scoping serta pemisahan read-only vs read-write.

### Sepuluh prefix tulis, lima kunci baca

Diverifikasi ke `services/file/main.go` 2026-09-03.

| Prefix | Env kunci tulis | Punya kunci baca? | Dipakai |
|---|---|---|---|
| `employee/` | `MINIO_EMPLOYEE_KEY` | ✅ `MINIO_EMPLOYEE_READ_KEY` | employee-service |
| `attendance/` | `MINIO_ATTENDANCE_KEY` | ✅ | attendance-service |
| `task/` | `MINIO_TASK_KEY` | ✅ | task-management |
| `notification/` | `MINIO_NOTIFICATION_KEY` | ✅ | notification-service |
| `form/` | `MINIO_FORM_KEY` | ✅ `MINIO_FORM_READ_KEY` | [[Microservices - Form Builder Service]] |
| `kas-kecil/` | `MINIO_PROCUREMENT_KEY` | ❌ | procurement-service |
| `pengajuan-barang/` | `MINIO_PENGAJUAN_KEY` | ❌ | procurement-service |
| `pembayaran/` | `MINIO_PEMBAYARAN_KEY` | ❌ | bukti transfer AP |
| `pajak/` | `MINIO_PAJAK_KEY` | ❌ | arsip pajak finance-service |
| `audit/` | `MINIO_AUDIT_KEY` | ❌ **disengaja** | [[Finance - Audit Internal]], bukti sisi lawan |

⛔ **Prefix `audit/` sengaja TIDAK punya kunci baca**, dan itu keputusan keamanan, bukan kelalaian. Kunci baca hari ini sampai ke **browser**: erp-frontend membacanya dari `NEXT_PUBLIC_MINIO_*_READ_KEY` (`src/hooks/use-document.ts`), yang ditanam ke bundel klien saat build. Satu kunci baca memberi akses ke **seluruh prefix**, jadi kunci baca `audit/` berarti tiap rekening koran terbaca siapa pun yang punya bundelnya — bertentangan dengan inti [[ADR - 0074 Audit Internal Dipisah jadi Service dan Aplikasi Sendiri]]. Dikunci test `TestPrefixAuditTakPunyaKunciBaca`. Lihat [[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]].

⚠️ **Empat prefix lain juga tak punya kunci baca**, dan itu belum pernah diputuskan — cuma belum dibuat. Bedanya dengan `audit/`: yang terakhir menolaknya secara sadar dan mengunci penolakannya.

### Membaca berkas berizin: PROXY di sisi server, bukan kunci di peramban

Pola yang dipakai **lima kali** di employee-service — `contract_file.go:159`, `kpi_evidence.go:562`, `mutasi_file.go:132`, `resign_file.go:182`, `warning_file.go:139` — dan kini juga di finance-service untuk bukti audit:

```
InternalURL["file"] + "/preview?minio=" + objek + "&key=" + kunci
```

Alasannya tertulis di `kpi_evidence.go`: *"Sengaja proxy, bukan menerbitkan presigned URL: URL sementara tetap bisa diteruskan ke orang lain selama masa berlakunya, sedangkan proxy memeriksa hak akses SETIAP KALI file diminta."*

⚠️ **Tiga jebakan yang sudah tertulis di kelima pemakainya:**

1. Rutenya `/preview`, parameternya **`minio`** — bukan `minio_object`, yang hanya dipakai `/upload`.
2. `routes.InternalRequest` **membuang header respons upstream**, termasuk `Content-Type` yang dihitung file-service dari isi objek. Tanpa dibangun ulang dari ekstensi, fasthttp memakai `text/plain` dan peramban menampilkan PDF sebagai sampah karakter.
3. Nama berkas yang datang dari pengguna wajib disaring sebelum masuk `Content-Disposition` — CR/LF di sana memungkinkan header splitting.

### Perakitan peta akses

> Ditambahkan PR [#1057](https://github.com/bip-itteam-internal/bip-erp/pull/1057), ✅ **live dev + prod 2026-08-06**. Dipakai lampiran [[Microservices - Form Builder Service]] (semua tipe form, termasuk program Kaizen).

"Access key" di sini **bukan kredensial MinIO IAM**, melainkan string rahasia yang dipetakan service ini ke satu prefix direktori. Menambah prefix baru berarti dua sisi: pengirim mengirimkannya sebagai `?key=`, dan service ini yang tahu kunci itu berarti prefix apa. Kalau hanya sisi pengirim yang ditambah, unggahannya dibalas `invalid access key` betapa pun benar nilai env-nya.

**Peta dirakit `bangunAccessMap`, yang MELEWATI env kosong** dan mencatat namanya di log saat boot. Sebelumnya peta dirakit langsung dari `os.Getenv` lalu diperiksa fungsi yang **panic** bila ada kunci kosong, dan itu punya dua akibat buruk:

1. Satu env yang belum diisi **mematikan seluruh file-service** — foto karyawan, bukti presensi, lampiran tiket, semuanya — padahal yang belum siap cuma satu modul. Kelas kegagalan yang sama sudah dua kali menggigit lewat `ValidateInternalURL`.
2. Menambah prefix baru jadi **ranjau deploy**: entri baru wajib sudah ada di `.env` tiap lingkungan sebelum service di-rebuild.

Perubahan itu sekaligus menutup lubang yang tak kentara: env kosong dulu memasukkan kunci `""` ke peta, sehingga permintaan **tanpa** `?key=` cocok dengan prefix itu dan mendapat akses. Panic membuatnya tak terjangkau — tapi hanya selama panic-nya masih ada.

⛔ **Kunci yang BERTABRAKAN juga tidak lagi memanic.** Dua modul memakai nilai kunci yang sama memang kesalahan konfigurasi serius — keduanya bisa saling membaca dan menimpa berkas — tetapi obatnya bukan panic. Peta dirakit saat inisialisasi variabel paket, jadi panic terjadi **sebelum `main()`**: tak satu pun baris log menjelaskan sebabnya, dan yang terlihat cuma container restart-loop.

Yang berlaku sekarang (`main.go:162-174`): **kedua prefix yang bertabrakan dibuang**, dicatat keras di log, dan prefix lain tetap hidup. Keduanya dibuang, bukan salah satu dipilih — memilih berarti menebak, dan tebakan yang salah memberi satu modul akses **tulis** ke ruang modul lain. Dikunci `TestKunciBertabrakanTidakMematikanPrefixLain` dan `TestKunciBentrokTigaEntriTetapDitolak` (urutan iterasi map Go acak, jadi tabrakan harus ditolak apa pun urutannya).

⚠️ **Konsekuensi operasional**: nilai tiap kunci di `.env` wajib **berbeda satu sama lain**. Menyalin nilai `MINIO_PAJAK_KEY` ke `MINIO_AUDIT_KEY` tidak membuat keduanya jalan — ia mematikan **keduanya**.

### Penjaga irisan prefix

`TestTakAdaPrefixYangBeririsan` memeriksa **seluruh pasangan** di `writeAccessEnv`: tak satu pun prefix boleh berada di dalam prefix lain, dan tak satu pun boleh kosong (prefix kosong memberi akses tulis ke seluruh bucket). Sebelumnya pemeriksaan itu hanya berjalan untuk `pengajuan-barang/`; digeneralisasi PR [#1699](https://github.com/bip-itteam-internal/bip-erp/pull/1699) karena menyalinnya tiap ada prefix baru berarti satu aturan hidup di banyak tempat.

⚠️ Nested **object path** tidak terpengaruh: lampiran pengajuan budget disimpan di `kas-kecil/pengajuan-budget/…`, tapi itu letak objek di bawah satu prefix, bukan entri prefix kedua.

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

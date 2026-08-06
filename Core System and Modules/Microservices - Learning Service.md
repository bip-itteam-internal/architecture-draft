## Deskripsi

*Rumah modul **pelatihan karyawan**, sekaligus fondasi **LMS People Development** yang akan dibangun di atasnya. Service ini lahir dari **LMS Fase 0**: memindahkan modul Training dari [[Microservices - Employee Service]] apa adanya, tanpa perubahan yang terlihat pengguna. Fitur LMS-nya sendiri (materi, kuis, skoring, kurikulum jabatan) **belum ada** — lihat Belum Diimplementasikan.*

- **Stack:** Go + Fiber v2 + MongoDB (`learning_db`), discaffold dari `services/.template`
- **Path:** `services/learning`
- **Port internal:** 6987 · **Modul gateway:** `learning` (`/api/learning/*`)
- **Status**: ✅ **Implemented & live di dev + produksi 2026-08-06** (bip-erp PR [#1020](https://github.com/bip-itteam-internal/bip-erp/pull/1020), frontend [erp-frontend#814](https://github.com/bip-itteam-internal/erp-frontend/pull/814)). Data 4 koleksi sudah dipindah di kedua lingkungan, jumlah terverifikasi cocok. Konsep & rencana lanjutan: [[HRIS - Training Program]]

## Kenapa service sendiri

Modul Training dulu menumpang Employee Service. Dipindah karena LMS menuntut **kelas tatap muka dan belajar mandiri berbagi satu angka progres**; bila keduanya tinggal di service berbeda, tiap perhitungan progres jadi panggilan lintas-service. Sesuai [[ADR - 0002 Database-per-Service]], modul baru = service + database sendiri.

Service ini **tidak menyimpan** master karyawan, jabatan, maupun departemen. Semuanya tetap milik [[Microservices - Employee Service]] dan dibaca lewat panggilan internal.

## Endpoint / Fitur (Sudah Diimplementasikan)

Daftar lengkap: [[API - Learning Service]]. Ringkasnya empat kelompok, semuanya pindahan utuh dari Employee Service:

- **Master jenis pelatihan** — CRUD `/training/types`
- **Master trainer** — CRUD `/training/trainers`, internal (tautan `employee_id`) atau eksternal
- **Event pelatihan** — CRUD `/training` dengan filter `?department_key=&status=`, guard transisi status (Scheduled → Ongoing → Completed, atau → Cancelled), hapus cascade ke peserta
- **Peserta & kehadiran** — `/training/:id/participants` (unique index `{training_id, employee_id}` anti-duplikat, tanpa cap kapasitas), kehadiran boolean, `/training/history/:employeeId`

RBAC tulis = `RequireHRISStaff`; GET terbuka di belakang gateway. Fungsi validasi murni (`ValidateTraining`, `CanEnroll`, `IsValidStatusTransition`, `validateTrainer`) beserta ujinya ada di `services/learning/models_training.go` dan `models_training_test.go`.

### Verifikasi departemen lewat panggilan internal

Satu-satunya perilaku yang **berubah** saat pemindahan. Sebelumnya `verifyTrainingRefs` mengueri koleksi `master_department` langsung dengan `mongodb.FindOne`. Koleksi itu milik Employee Service, jadi setelah pindah kueri tersebut mengarah ke `learning_db` dan **selalu gagal** — setiap pelatihan yang mengisi departemen akan ditolak "department not found".

Diganti panggilan `GET {EMPLOYEE_MODULE_URL}/master/departments/{key}` lewat `routes.InternalRequest`. Tiga hal yang menyertainya:

- ⚠️ **`EMPLOYEE_MODULE_URL` dibaca langsung `os.Getenv`, TIDAK masuk map `InternalURL`.** `validation.ValidateInternalURL` panic pada entri kosong, sehingga menaruhnya di sana berarti seluruh service mati saat env belum terisi. Pola dan alasannya sama dengan [[Microservices - Form Builder Service]].
- Kunci departemen di-escape dengan `url.PathEscape`. Tanpa itu `department_key = "IT?bogus=1"` lolos verifikasi karena `?bogus=1` terlepas jadi query, dan nilai palsu itu tersimpan sebagai departemen yang tak pernah ada.
- Pemetaan hasil dipisah tegas dan diuji sebagai fungsi murni: 2xx lolos, **404 → 400** (departemen memang tidak ada), **status lain / galat transport / env kosong → 502**. Menyebut departemen tidak ada padahal service-nya tak terjangkau akan menyesatkan pembacanya, dan mencatat gangguan server sebagai kesalahan klien membuat pemantauan 5xx tak menyala.

## Belum Diimplementasikan / Catatan

- **Seluruh fitur LMS belum ada.** Course, materi PDF & video, bank soal, pre/post test, skoring otomatis, kurikulum per jabatan, tenggat, Talent Pool, penilaian trainer — semuanya Fase 1 ke atas. Desainnya sudah lengkap, lihat [[HRIS - Training Program]].
- ⚠️ **Koleksi `training` belum punya `company_id`**, dan `GET /training` tidak menyaring perusahaan, sehingga semua tenant melihat semua pelatihan. Sementara itu verifikasi departemen **tersaring perusahaan** (endpoint employee-service memfilter `company_id`), padahal kueri lama tidak. Hari ini dampaknya nol karena seluruh data Training milik `BIP`, tapi begitu `ELT` memakai modul ini, pengguna BIP akan melihat pelatihan ELT di daftar lalu gagal mengeditnya dengan pesan 400 yang menyesatkan. **Fase 1 wajib memasang `company_id` + backfill + saring daftar per perusahaan** ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]).
- **Belum ada uji level handler** (`app.Test`), hanya fungsi murni. Bukan regresi, kode lama pun tidak punya, tapi kelas cacat glue handler tak tertangkap uji fungsi murni.
- Bawaan dari kode lama, belum diperbaiki: `PUT` bersifat full-replace sehingga frontend wajib mengirim objek lengkap, pendaftaran peserta belum memeriksa karyawan benar-benar ada di `work_data`, dan daftar belum berpaginasi.
- **Rute lama `/api/employee/training/*` masih hidup di produksi.** `employee-service` sengaja tidak di-rebuild saat cut-over agar tidak ikut mendorong perubahan orang lain ke produksi. Tidak ada pemanggil yang tersisa. Koleksi Training lama juga masih ada di `employee_db` sebagai jalan pulang.

## Dependensi & Integrasi

- **MongoDB `learning_db`** — koleksi `training_type`, `trainer`, `training`, `training_participant`. Lihat [[DB - Overview and Notes]].
- [[Microservices - Employee Service]] — sumber master departemen (verifikasi `department_key`) dan master karyawan untuk pemilih peserta serta trainer internal.
- [[CORE - API Master Gateway]] — modul `learning`, env `LEARNING_MODULE_URL`.
- [[APP - Web ERP]] — layar `/hris/training` dan `/hris/training/masters` di grup menu People Development.

## Dokumen Terkait

- [[HRIS - Training Program]] — konsep, desain LMS lengkap, dan rencana bertahap
- [[API - Learning Service]] · [[API - Index]]
- [[Microservices - Employee Service]] — rumah lama modul ini
- [[ADR - 0002 Database-per-Service]] · [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]

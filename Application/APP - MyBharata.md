## Deskripsi

*Aplikasi mobile **MyBharata** (`my_bharata`) adalah aplikasi HRIS resmi PT Bharata Internasional — satu codebase Flutter untuk Android & iOS yang menjadi portal karyawan untuk seluruh siklus HR: attendance → cuti/izin → lembur → payroll → evaluasi. Aplikasi menegakkan aturan "Peraturan Perusahaan 2026–2028" secara otomatis dan mencegah kecurangan absensi melalui biometric + geofencing + validasi QR.*

- **Status**: ✅ Implemented — aplikasi HRIS mobile produksi (Flutter, Android/iOS); rilis dev 1.10.2+104.

- Pengguna: karyawan, supervisor, HRD, IT admin, dan tamu eksternal (guest book)
- Versi build saat ini: **1.10.2+104** (dev; `pubspec.yaml`) — PR Support Ticket (#83) menaikkan ke **1.10.3+105**
- Target platform: Android (minSdk 23 / Android 6.0+), iOS 13+
- Survei perangkat mobile karyawan [terdaftar di sini](https://docs.google.com/spreadsheets/d/1w2blhMgFx1BI9zu6ni5gmQJab_NfMhdocm0cj5pyO_s/edit?usp=sharing)

## Tech Stack

- **Framework**: Flutter (Dart SDK `^3.8.1`)
- **State management**: `flutter_bloc` / `bloc` (pola event `Verb+Object`, state Initial/Loading/Loaded/Error/Empty)
- **Dependency Injection**: `get_it` (registrasi berlapis: core → services → datasources → repositories → usecases → blocs)
- **Networking**: `dio` melalui `ApiInterface`; response dibungkus `BaseResponse`; error dipetakan ke `Failure` (functional error handling pakai `fpdart` → `Either<Failure, T>`). **Timeout wajib** di `buildApiBaseOptions` (connect 15s / receive 30s / send 60s) agar request tak menggantung tanpa batas saat jaringan tak stabil — mencegah spinner "muter terus" padahal data sudah tersimpan (yang memicu retry & data ganda); timeout dipetakan ke `NetworkFailure` sehingga UI selalu resolve
- **Routing**: `go_router` dengan redirect terpusat (intro → login → PIN → auth)
- **Lokalisasi**: `flutter_localizations` + `intl`; **Bahasa Indonesia (default)** & **English** via file ARB, diakses lewat `context.l10n.<key>`
- **Firebase**: Core, Analytics, Crashlytics, Messaging (FCM), Performance — dengan dua flavor `dev`/`prod` (project `hris-bharata-dev` & `hris-bharata-prod`)
- **Library penting lain**: `mobile_scanner` + `pretty_qr_code` (QR), `geolocator`/`geocoding` (geofencing), `local_auth` (biometric), `pinput` (PIN), `flutter_secure_storage` + `jwt_decoder` (auth), `syncfusion_flutter_pdfviewer` (payslip), `fl_chart` (grafik KPI), `table_calendar`, `flutter_local_notifications`
- **CI/CD**: Codemagic

## Arsitektur

- **Pola**: Clean Architecture + **Feature-First** — setiap fitur di `lib/src/features/<feature>/`, dengan kode bersama di `lib/src/core/`
- **Layer per fitur**: `domain/` (entity, kontrak repository, usecase — pure Dart) → `data/` (model, datasource, implementasi repository + pembungkusan error) → `presentation/` (bloc, pages, widgets)
- **Aliran data** searah: UI → BLoC → Usecase → Repository (abstract) → RepositoryImpl → Datasource, dan mengembalikan `Either<Failure, Entity>` ke atas
- **Aturan**: domain bebas dependency framework; presentation hanya bicara ke BLoC; model data wajib `extend` entity domain

## Autentikasi

- Login **email/password** menerbitkan **JWT** dengan silent refresh; token disimpan di `flutter_secure_storage`
- **Biometric** (Face ID / fingerprint, via `local_auth`) untuk re-login cepat dan akses sensitif
- **PIN** sebagai metode re-login alternatif
- Kebijakan **1 akun = 1 device** (validasi pakai `device_info_plus`)
- Onboarding: karyawan baru login pertama kali dengan Employee ID + password sementara dari HRD, lalu diarahkan untuk mengatur kredensial baru

> [!note] Catatan integrasi backend
> Pada implementasi saat ini, MyBharata terhubung **langsung ke HRIS backend** (`https://admin.hris-bharata.com`, UAT `https://admin-dev.hris-bharata.com`) menggunakan JWT — **bukan** melalui [[CORE - API Master Gateway]] dan **bukan** SSO. Ini adalah selisih antara rencana arsitektur (portal terpusat di belakang API Master Gateway) dengan kondisi aplikasi yang sudah dibangun. Lihat bagian *Dependencies & Integrasi*.

## Fitur Utama (Live)

### Navigasi & Beranda
- **Bottom navigation 5 tab**: Home, History (riwayat kehadiran), Scan/QR (Wi-Fi verification), Information (berita/artikel), Profile
- **Home dashboard**: ringkasan kehadiran hari ini, pengumuman/berita perusahaan, carousel cuaca, dan grid menu cepat
- **Notification center**: daftar + detail notifikasi (push via FCM), badge jumlah belum dibaca

### Attendance (Kehadiran)
- Clock-in / clock-out tervalidasi **QR Code + geofencing + biometric**, disertai capture **mood** karyawan
- Lihat **jadwal kerja** (shift) dan **riwayat kehadiran** (kalender + statistik)
- **My Team**: supervisor melihat kehadiran tim
- **Employee Mood List**: pemantauan mood check-in karyawan
- **Tukar Shift (Tukar Jadwal Kerja)** ⚠️ *(branch `feature/schedule-exchange`, PR #78 → `dev`, belum rilis)* — pemohon ajukan tukar slot shift dengan rekan se-departemen/se-site, lalu **consent rekan** → review atasan/HRD; fitur `features/schedule_exchange` memanggil `/schedule-exchange/*` langsung. Detail: [[HRIS - Tukar Jadwal Kerja]]

### Submission — Izin & Cuti
- Pengajuan **cuti tahunan, sakit, dispensasi, dinas luar kota**, dan **cuti melahirkan** (maternity, approval 3 tingkat: supervisor langsung → HR → Direksi) beserta riwayatnya
- **Vacation Quota**: lihat sisa kuota cuti
- **Check Permission / Verify Leaves**: verifikasi/approval pengajuan (untuk HR/atasan)
- **Review Submission** (peninjau): inbox **lintas jenis** (Izin/Cuti/Sakit/Dinas/Koreksi/Tukar) dalam satu daftar via `/hr/requests` (`?as=reviewer` antrian / `reviewed` sudah); detail fetch-on-tap via `/hr/requests/detail`. "Aktivitas Saya" & kartu beranda "menunggu persetujuan" juga pakai endpoint terpadu (`/requests/mine`, `/hr/requests`). Kontrak: [[API - Attendance Service]]

### Lembur (Overtime)
- Pengajuan lembur (form tanggal, alasan, upload file) dengan alur **approval SPKL** oleh supervisor

### Payroll
- Lihat **payslip** bulanan (PDF terenkripsi, **dilindungi PIN**, ditampilkan in-app) dan riwayat payslip tahunan

### KPI & Support Ticket
- **KPI**: laporan performa kuartalan (read-only di mobile) dengan grafik
- **Support Ticket** *(sebelumnya "Helpdesk IT")* — buat tiket ke **Space per divisi** (lintas divisi) lewat form "Buat Tiket": pilih Space, Judul, Deskripsi, **lampiran opsional** (**create-then-upload** per-file ke `/tasks/:id/attachments`, batas **4 MB/file** selaras file-service). Daftar tiket punya **3 tab scope** — *Tiket Saya* / *Ditugaskan ke Saya* / *Tiket Tim* (supervisor) — dengan **badge jumlah aktif** (`/tasks/counts`), pencarian, filter (status/prioritas/periode), urut terbaru; warna status kartu/header ikut `status_color` per-space. **Detail** dibagi section **Checklist** (hanya **centang**; item dibuat lewat web) & **Komentar** (terbaru dulu); **ubah status** (maju-saja) & **komentar** lewat **bottom action bar**. Gate izin: hanya **assignee/supervisor** yang boleh ubah status & checklist; **pemohon read-only** (hanya komentar). **Approve/Reject permintaan hanya di web** — mobile belum punya alur approval, sehingga notif "Permintaan baru" mengarahkan buka website ERP. URL di deskripsi jadi tautan klik; input teks auto-kapital huruf pertama (sentence-case). Fitur `features/task`. Backend: [[Microservices - Task Management Service]] · web: [[APP - Web ERP]] · tracker: [[APP - Dynamic Task Tracker]]

### Fitur pendukung lain
- **QR Code**: tampilkan QR pribadi + akses scanner inventory
- **Guest Book**: tamu eksternal mengisi buku tamu (scan QR, input manual, kategori)
- **Information**: feed berita/artikel internal
- **Company Info**: detail perusahaan, handbook, kebijakan, struktur organisasi, kontak darurat
- **Help Center**: FAQ (pencarian + kontak)
- **IT Support**: daftar kontak IT (termasuk WhatsApp)
- **Weather**: widget cuaca lokal untuk karyawan lapangan
- **Settings**: bahasa (ID/EN), tema (terang/gelap), toggle biometric, pengaturan notifikasi

## Fitur Developer / Admin

> Catatan: belum ada **role-based gating** di routing layer — fitur ini hanya "tersembunyi" (tidak muncul di menu UI normal) dan diasumsikan di-enforce oleh backend.

- **Developer Menu** (`/developer`) — hub navigasi untuk menguji seluruh route + demo halaman attendance
- **Components Test** (`/component`) — sandbox komponen UI
- **IT Admin — Account Reset** (`/it/account-reset`) — reset password akun karyawan

## Fitur "Coming Soon" (Belum Tersedia)

Tercantum di menu tetapi masih placeholder (route `/coming-soon` atau stub):
- Digital ID, My Documents, Policy/Handbook, Insurance, Loan, Meeting Room, Vehicle, Learning Center, Inbox, Chat HRD

## Roadmap (Belum Diimplementasikan)

- **Offline-Mode Attendance** — rekam absensi offline (GPS terenkripsi lokal), auto-sync saat online *(prioritas: High)*
- Naikkan test coverage 55% → 70% (fokus `attendance`, `payroll`)
- Migrasi widget `payroll` lama ke dark theme
- Penyatuan penanganan timezone (server UTC, format lokal di presentation)

## Known Issues

1. **Selisih waktu attendance lintas timezone** — perjalanan dinas lintas zona (mis. WIB → WITA) menampilkan jam clock-in yang salah; sebagian presentation pakai `DateTime.now()` lokal alih-alih konversi dari UTC server
2. **Download payslip gagal di sebagian Android 13+** — permission storage lama ditolak Android 13 (API 33); workaround: lihat payslip via viewer in-app
3. **JWT expiry setelah lama di background** — setelah >2 jam, app bisa freeze/terlempar ke Login akibat tabrakan refresh token pada request paralel

## Dependencies & Integrasi

- **HRIS backend** (`admin.hris-bharata.com`) — sumber data utama; integrasi langsung via REST + JWT
- **Firebase** — Analytics, Crashlytics, FCM (push notification), Performance
- [ ] [[CORE - API Master Gateway]] — *rencana awal:* portal terpusat di belakang gateway. *Kondisi saat ini:* belum dipakai oleh MyBharata (lihat catatan integrasi backend di atas)

## Dokumen Terkait

- [[HRIS - Attendance System]]
- [[HRIS - Payroll]]
- [[Microservices - Attendance Service]]
- [[Microservices - Employee Service]]
- [[Microservices - Notification Service]]
- [[Microservices - Task Management Service]]
- [[APP - Dynamic Task Tracker]]

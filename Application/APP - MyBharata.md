## Deskripsi

*Aplikasi mobile **MyBharata** (`my_bharata`) adalah aplikasi HRIS resmi PT Bharata Internasional — satu codebase Flutter untuk Android & iOS yang menjadi portal karyawan untuk seluruh siklus HR: attendance → cuti/izin → lembur → payroll → evaluasi. Aplikasi menegakkan aturan "Peraturan Perusahaan 2026–2028" secara otomatis dan mencegah kecurangan absensi melalui biometric + geofencing + validasi QR.*

- **Status**: ✅ Implemented — aplikasi HRIS mobile produksi (Flutter, Android/iOS); rilis dev 1.10.2+104.
- **Multi-perusahaan** ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]): presensi (absen/jadwal/izin) ter-scope **otomatis via JWT** (tak ada perubahan). **Profil Perusahaan** dari `/me` (BIP profil penuh; perusahaan lain nama saja) & **onboarding** (welcome + setup-selesai) dari respons login `new_user`, membuang hardcode "PT Bharata". **Konten dinamis per tenant (F2-C, PR #90)**: helper `CompanyScope` / `companyScopeOf(context)` dari `UserProfileBloc` (key kosong = BIP demi kompatibilitas token lama); blok "Tentang Perusahaan" (Visi/Misi/Company Info/SOP) & "Bharata Community" hanya untuk BIP, sedangkan kartu cuaca kantor dan nama pada strap QR lanyard kini ikut nama perusahaan user. **Menu Pengajuan disembunyikan untuk non-BIP (PR #91)** selama pilot, di dua entry point (`home_menu_grid` + `more_menu`), karena perusahaan lain fokus presensi dulu. **Status rilis**: PR #89/#90/#91 sudah **merged ke `dev`** (versionCode 120), belum naik ke `main`. **Masih TBD (butuh data per-perusahaan di BE):** kontak HR, nama gedung + guestbook, handbook/SOP PDF. Kontak IT sengaja tetap pusat (helpdesk grup, dipakai juga pra-login sebelum perusahaan diketahui).

- Pengguna: karyawan, supervisor, HRD, IT admin, dan tamu eksternal (guest book)
- Versi build saat ini: **1.11.0+122** (`origin/dev`; `pubspec.yaml`) — PR penyelarasan kontrak `owner_department` ([#94](https://github.com/bip-itteam-internal/my-bharata/pull/94), open) menaikkan ke **1.11.1+123**
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
> **Dikoreksi 2026-08-01 (grounded ke kode):** MyBharata **memang lewat** [[CORE - API Master Gateway]]. `lib/src/core/api/url.dart` menetapkan base URL `https://api.bharatainternasional.com/` (prod) dan `http://10.10.10.121:6969/` (dev) — keduanya alamat gateway — dan **seluruh** konstanta endpoint berprefix `api/<module>/...` (mis. `api/attendance/tap`, `api/notification/inbox`, `api/file/preview`), yaitu pola routing `/api/:module/*` milik gateway.
>
> Catatan lama di tempat ini menyatakan aplikasi terhubung langsung ke `admin.hris-bharata.com` dan **bukan** melalui gateway. Itu **tidak sesuai kode** dan sudah dicabut. Yang masih benar: MyBharata memakai **JWT Bearer**, bukan alur SSO ticket ([[CORE - SSO Flow]]) yang dipakai FE Task Manager.
>
> Konsekuensi praktisnya: service baru yang terdaftar di map `InternalURL` gateway **otomatis terjangkau** MyBharata tanpa infrastruktur tambahan — dasar yang dipakai [[Microservices - Form Builder Service]] untuk menargetkan pengisian form lewat mobile.

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

### KPI & Task Management
- **KPI**: laporan performa kuartalan (read-only di mobile) dengan grafik
- **Task Management** *(sebelumnya "Support Ticket", sebelumnya lagi "Helpdesk IT"; label diselaraskan dengan web pada 2026-07-28 — istilah user-facing kini **Tugas**/**Task**, key l10n `menuTaskManagement`/`task*` tidak berubah)* — buat tugas ke **Space per divisi** (lintas divisi) lewat form "Buat Tugas": pilih Space, Judul, Deskripsi, **lampiran opsional** (**create-then-upload** per-file ke `/tasks/:id/attachments`, batas **4 MB/file** selaras file-service). Daftar tugas punya **3 tab scope** — *Tugas Saya* / *Ditugaskan ke Saya* / *Tugas Tim* (supervisor) — dengan **badge jumlah aktif** (`/tasks/counts`), pencarian, filter (status/prioritas/periode), urut terbaru; warna status kartu/header ikut `status_color` per-space. **Detail** dibagi section **Checklist** (hanya **centang**; item dibuat lewat web) & **Komentar** (terbaru dulu); **ubah status** (maju-saja) & **komentar** lewat **bottom action bar**. Gate izin: hanya **assignee/supervisor** yang boleh ubah status & checklist; **pemohon read-only** (hanya komentar). **Approve/Reject permintaan hanya di web** — mobile belum punya alur approval, sehingga notif "Permintaan baru" mengarahkan buka website ERP. URL di deskripsi jadi tautan klik; input teks auto-kapital huruf pertama (sentence-case). Fitur `features/task`. Backend: [[Microservices - Task Management Service]] · web: [[APP - Web ERP]] · tracker: [[APP - Dynamic Task Tracker]]

### Survei / Form Builder
- **Section "Survei" di beranda**, tepat di bawah quick menu, berisi form terbit yang ditujukan ke karyawan itu dan **belum** ia isi. Tiap kartu menampilkan jumlah pertanyaan, tenggat gerbang, dan penanda merah **"Wajib sebelum absen"** bila form-nya menahan clock-in.
- **Halaman pengisian `/survey/:id`** merender **9 tipe pertanyaan** (`short_text`, `long_text`, `number`, `date`, `time`, `dropdown`, `radio`, `checkbox`, `scale`), memvalidasi cermin aturan backend sebelum kirim, lalu menyegarkan section supaya form yang baru diisi langsung lenyap.
- Sumber data `GET /api/form-builder/me/forms` + `POST /api/form-builder/me/forms/:id/responses`. Backend: [[Microservices - Form Builder Service]] · kontrak: [[API - Form Builder Service]]
- Fitur `features/form`. my-bharata PR [#93](https://github.com/bip-itteam-internal/my-bharata/pull/93) (merged, `dev`).

> [!important] Section ini menghilang sepenuhnya saat gagal memuat, bukan hanya saat kosong
> `form-builder-service` **belum jalan di prod**, jadi di produksi endpointnya membalas `404`. Datasource menerjemahkan `404` jadi daftar kosong, dan section memperlakukan keadaan gagal **sama dengan kosong**: tak ada judul menggantung, tak ada kerangka, tak ada pesan galat. Memunculkan kegagalan di layar utama untuk fitur yang belum dirilis di lingkungan itu lebih buruk daripada diam. Halaman pengisian tetap menampilkan pesan errornya sendiri.

> [!warning] Tiga aturan kontrak yang mudah dilanggar diam-diam
> **`number` dan `scale` wajib dikirim sebagai angka JSON.** Backend memakai pembanding tipe yang menolak string, sedangkan input teks di layar selalu menghasilkan string. Konversinya dipusatkan di `answer_encoder.dart`.
>
> **Koma diterima sebagai pemisah desimal** ("36,5") lalu dinormalkan ke titik. Papan ketik angka menyediakan komanya dan orang Indonesia menulis begitu; menolaknya berarti menjebak pemakai.
>
> **`scale_min` bertag `omitempty` di backend**, jadi skala `0..N` datang **tanpa** field itu. Nilai bawaannya harus 0, bukan 1 — menebak 1 membuat pilihan terendah tak pernah bisa disentuh.

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

- [[CORE - API Master Gateway]] — **pintu masuk seluruh request** (`api.bharatainternasional.com`, dev `10.10.10.121:6969`), dipanggil dengan pola `api/<module>/...` + JWT Bearer. Lihat koreksi di catatan integrasi backend di atas.
- **Firebase** — Analytics, Crashlytics, FCM (push notification), Performance

## Dokumen Terkait

- [[HRIS - Attendance System]]
- [[HRIS - Payroll]]
- [[Microservices - Attendance Service]]
- [[Microservices - Employee Service]]
- [[Microservices - Notification Service]]
- [[Microservices - Task Management Service]]
- [[APP - Dynamic Task Tracker]]

## Deskripsi

*Aplikasi mobile **MyBharata** (`my_bharata`) adalah aplikasi HRIS resmi PT Bharata Internasional — satu codebase Flutter untuk Android & iOS yang menjadi portal karyawan untuk seluruh siklus HR: attendance → cuti/izin → lembur → payroll → evaluasi. Aplikasi menegakkan aturan "Peraturan Perusahaan 2026–2028" secara otomatis dan mencegah kecurangan absensi melalui biometric + geofencing + validasi QR.*

- **Status**: ✅ Implemented — aplikasi HRIS mobile produksi (Flutter, Android/iOS). **Rilis di HP pemakai: `1.14.5+135`** (`origin/main`, GitHub Release 2026-08-03); `origin/dev` sudah di **`1.14.9+143`** dan belum ditarik ke `main`, jadi delapan PR terakhir termasuk **Pelatihan Saya** (#112) belum sampai ke siapa pun. Angka lama "rilis dev 1.10.2+104" di baris ini sudah tidak berlaku (diverifikasi ke `pubspec.yaml` kedua branch 2026-08-19).
- **Multi-perusahaan** ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]): presensi (absen/jadwal/izin) ter-scope **otomatis via JWT** (tak ada perubahan). **Profil Perusahaan** dari `/me` (BIP profil penuh; perusahaan lain nama saja) & **onboarding** (welcome + setup-selesai) dari respons login `new_user`, membuang hardcode "PT Bharata". **Konten dinamis per tenant (F2-C, PR #90)**: helper `CompanyScope` / `companyScopeOf(context)` dari `UserProfileBloc` (key kosong = BIP demi kompatibilitas token lama); blok "Tentang Perusahaan" (Visi/Misi/Company Info/SOP) & "Bharata Community" hanya untuk BIP, sedangkan kartu cuaca kantor dan nama pada strap QR lanyard kini ikut nama perusahaan user. **Menu Pengajuan disembunyikan untuk non-BIP (PR #91)** selama pilot, di dua entry point (`home_menu_grid` + `more_menu`), karena perusahaan lain fokus presensi dulu. ✅ **Gerbang itu DIBUKA di PR [#113](https://github.com/bip-itteam-internal/my-bharata/pull/113)** (**merged ke `dev`**; `companyScopeOf(context).isBip` dicabut di kedua entry point): `attendance-service` kini menyaring per `company_id` di seluruh jalurnya, jadi menahannya lebih lama berarti seluruh karyawan CV Elit dan Sadewa tak bisa mengajukan cuti lewat aplikasi sama sekali padahal servernya sudah siap. ⚠️ Dua gerbang KONTEN (visi-misi + Bharata Community di beranda, profil perusahaan lengkap) **sengaja TIDAK ikut dibuka**: di baliknya `CompanyInfoModel.dummy()` dan `ClubEntity.sample()`, yaitu data BIP yang dipaku di kode. Mencabut kondisinya tidak membuka akses, melainkan menampilkan visi-misi dan alamat PT Bharata Internasional kepada karyawan CV Elit seolah itu perusahaannya sendiri. Yang dibutuhkan di sana konten per-tenant, bukan penghapusan `if`. **Status rilis**: PR #89/#90/#91 sudah **merged ke `dev`** (versionCode 120), belum naik ke `main`. **Masih TBD (butuh data per-perusahaan di BE):** kontak HR, nama gedung + guestbook, handbook/SOP PDF. Kontak IT sengaja tetap pusat (helpdesk grup, dipakai juga pra-login sebelum perusahaan diketahui).

- Pengguna: karyawan, supervisor, HRD, IT admin, dan tamu eksternal (guest book)
- Versi build saat ini: **1.14.9+143** (`origin/dev`; `pubspec.yaml`) — naik dari 135 lewat PR #107 (slip gaji terbit + unduh PDF), #108 (menu Kaizen), #109 (progres KPI bulan berjalan), #110 (kategori notifikasi `employee-moved`), #111 (section Survei ke puncak beranda), #112 (menu Pelatihan), #113 (membuka Pengajuan untuk non-BIP), dan [#114](https://github.com/bip-itteam-internal/my-bharata/pull/114) (memunculkan menu Kaizen & Pelatihan yang ternyata tak pernah terjangkau — lihat [[#Struktur menu beranda]]).
- Versi rilis: **1.14.5+135** (`origin/main`, tag `v1.14.5+135`, GitHub Release 2026-08-03) — itulah yang terpasang di HP pemakai. Seluruh PR di atas **belum ikut rilis**; catatan lama di sini menyebut rilis terakhir masih `1.14.2+132` dan `main` belum pernah ditarik dari `dev`, dua-duanya sudah tidak berlaku.
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
- **Library penting lain**: `mobile_scanner` + `pretty_qr_code` (QR), `geolocator`/`geocoding` (geofencing), `local_auth` (biometric), `pinput` (PIN), `flutter_secure_storage` + `jwt_decoder` (auth), `syncfusion_flutter_pdfviewer` (**PDF kebijakan perusahaan dari asset**, bukan payslip — dikoreksi 2026-08-05), `fl_chart` (grafik KPI), `table_calendar`, `flutter_local_notifications`
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
> **Dikoreksi 2026-08-05 (grounded ke kode).** Catatan lama di sini menyebut "payslip bulanan PDF terenkripsi, dilindungi PIN, ditampilkan in-app" beserta riwayat tahunan. **Tak satu pun ada di kode `my-bharata`** — tidak ada enkripsi, tidak ada PIN, dan sampai hari ini aplikasi belum pernah memanggil endpoint slip terbit. Deskripsi itu kemungkinan terbawa dari aplikasi lama `hris_bharata`. Jangan dijadikan rujukan.

- **Perkiraan gaji bulan berjalan** (`api/employee/me/payroll-approx`) — yang selama ini tampil di halaman "Slip Gaji". Endpoint itu **proxy ke [[Microservices - Attendance Service]] `/payroll-supplement`**, yaitu data turunan presensi (`payout_pct`, jam kerja, lembur) yang jadi **bahan masukan** perhitungan gaji, **bukan slip**.
- **Slip gaji terbit + unduh PDF** (branch `feat/payroll-slip-pdf`, **belum merge**): `GET /payroll-runs/my` menampilkan slip dari run **published** saja, tiap kartu punya tombol unduh yang mengambil `…/pdf` (lihat [[Microservices - Payroll Service]]). Keduanya **hidup berdampingan** dengan kartu perkiraan: perkiraan tetap berguna sebelum gajian, dan menggantinya akan membuat halaman kosong sampai run pertama diterbitkan.
	- Bytes diambil lewat `ApiInterface.getBytes` yang baru (`BaseResponse` mengasumsikan JSON), disimpan ke **direktori aplikasi** lalu dibuka lewat lembar berbagi (`ShareUtil.shareBytes`). **Sengaja bukan folder Unduhan bersama** — itu menuntut izin storage, dan justru itulah sumber Known Issue unduh Android 13+ pada aplikasi lama.
	- BLoC terpisah dari `PayrollBloc` karena sumber & daur hidupnya beda: mengganti bulan tak boleh ikut memuat ulang daftar slip.

### KPI & Task Management
- **KPI**: laporan performa kuartalan (read-only di mobile) dengan grafik
- **Task Management** *(sebelumnya "Support Ticket", sebelumnya lagi "Helpdesk IT"; label diselaraskan dengan web pada 2026-07-28 — istilah user-facing kini **Tugas**/**Task**, key l10n `menuTaskManagement`/`task*` tidak berubah)* — buat tugas ke **Space per divisi** (lintas divisi) lewat form "Buat Tugas": pilih Space, Judul, Deskripsi, **lampiran opsional** (**create-then-upload** per-file ke `/tasks/:id/attachments`, batas **4 MB/file** selaras file-service). Daftar tugas punya **3 tab scope** — *Tugas Saya* / *Ditugaskan ke Saya* / *Tugas Tim* (supervisor) — dengan **badge jumlah aktif** (`/tasks/counts`), pencarian, filter (status/prioritas/periode), urut terbaru; warna status kartu/header ikut `status_color` per-space. **Detail** dibagi section **Checklist** (hanya **centang**; item dibuat lewat web) & **Komentar** (terbaru dulu); **ubah status** (maju-saja) & **komentar** lewat **bottom action bar**. Gate izin: hanya **assignee/supervisor** yang boleh ubah status & checklist; **pemohon read-only** (hanya komentar). **Approve/Reject permintaan hanya di web** — mobile belum punya alur approval, sehingga notif "Permintaan baru" mengarahkan buka website ERP. URL di deskripsi jadi tautan klik; input teks auto-kapital huruf pertama (sentence-case). Fitur `features/task`. Backend: [[Microservices - Task Management Service]] · web: [[APP - Web ERP]] · tracker: [[APP - Dynamic Task Tracker]]

- **Tipe permintaan ✅** (PR [#105](https://github.com/bip-itteam-internal/my-bharata/pull/105)) — form Buat Tugas punya field **Tipe Permintaan** memakai `CustomSelectBottomSheet` yang sudah ada (radio list, bukan grid kartu seperti pemilih Space; keterangan tiap tipe tampil **di dalam** daftar). Muncul **hanya** bila Space tujuan punya daftar tipe, dan pilihannya **dibuang saat Space berganti** karena tipe milik satu space tertentu. `type_id` **dihilangkan dari body** saat kosong, bukan dikirim string kosong (BE menolaknya sebagai id tak sah).
	- ⚠️ Field `types` datang dalam **tiga bentuk** yang semuanya berarti kosong: absen, `null` (Go memancarkan slice nil sebagai null), dan bukan-list. Parsing di `TaskSpaceOptionModel` menangani ketiganya; entri tanpa `id` dibuang karena tak bisa dikirim balik.
- **Pengingat penilaian tiket (CSAT)** — banner di beranda saat ada tiket **selesai yang belum dinilai**; menekannya membuka halaman Task Management. Sumber datanya `GET /tasks/pending-csat` yang dibuat khusus untuk ini (PR bip-erp [#872](https://github.com/bip-itteam-internal/bip-erp/pull/872)); sebelumnya tak ada cara menanyakan hal itu ke server, karena `/tasks/counts` justru **mengecualikan** tiket selesai.

> [!note] Kenapa banner menetap, bukan SnackBar
> SnackBar sungguhan menghilang sendiri setelah beberapa detik, jadi pengingat akan terlewat oleh orang yang sedang menggulir atau baru membuka aplikasi — padahal justru itu yang mau diingatkan. Bentuk dan warnanya tetap meniru snackbar (`inverseSurface`), tapi ia tinggal di halaman sampai tiketnya dinilai.
>
> Menuju **daftar** tiket, bukan langsung ke satu tiket: saat ada beberapa yang menunggu, memilihkan salah satunya berarti menebak. Hilang sepenuhnya saat tak ada yang menunggu maupun saat gagal memuat (termasuk `404` dari server yang belum memuat rute ini) — pengingat bukan sesuatu yang diminta pemakai, jadi kegagalannya tak layak memakan layar utama.

### Survei / Form Builder
- **Section "Survei" di beranda**, berisi form terbit yang ditujukan ke karyawan itu dan **belum** ia isi. Tiap kartu menampilkan jumlah pertanyaan, tenggat gerbang, dan penanda merah **"Wajib sebelum absen"** bila form-nya menahan clock-in.
- **Posisinya paling atas** di daftar beranda — anak pertama `SliverList`, **di atas** kartu "menunggu persetujuan" (PR [#111](https://github.com/bip-itteam-internal/my-bharata/pull/111), **merged ke `dev` 2026-08-11**, versionCode **140**). Sebelumnya berada di bawah section "Akses Cepat". Tak ada `SizedBox` pemisah yang dipasang di puncak daftar: section membawa jaraknya sendiri di dua sisi (atas 16 dari `padding` bawaan `SectionHeader`, bawah 16 dari `SizedBox` terakhir di `Column`-nya), sehingga saat ia menyembunyikan diri — yang terjadi pada mayoritas pemakai, lihat catatan di bawah — puncak beranda tak meninggalkan celah menggantung.
- **Halaman pengisian `/survey/:id`** merender **9 tipe pertanyaan** (`short_text`, `long_text`, `number`, `date`, `time`, `dropdown`, `radio`, `checkbox`, `scale`), memvalidasi cermin aturan backend sebelum kirim, lalu menyegarkan section supaya form yang baru diisi langsung lenyap.
- **Dropdown, tanggal, dan jam memakai satu jalur yang sama** (PR [#95](https://github.com/bip-itteam-internal/my-bharata/pull/95)): mode nilai `CustomFormField` + pemilih milik aplikasi. Dropdown memakai **`CustomSelectBottomSheet`**, bukan `DropdownButtonFormField` bawaan Material — repo sudah punya komponennya, dan menu melayang di layar sempit sering terpotong sedangkan lembar bawah memang dirancang untuk jempol. Ketiganya kini punya tombol **"Kosongkan"** saat pertanyaannya opsional; sebelumnya tanggal dan jam terkunci begitu tersentuh karena pemilih tak punya cara bawaan membatalkan pilihan.
- **Keterangan ujung skala** digambar di bawah deretan angka bila dikirim backend; satu ujung saja tetap digambar.
- **Pengisian per bagian** (PR [#95](https://github.com/bip-itteam-internal/my-bharata/pull/95)): form berbagian dipecah jadi satu halaman per bagian lewat `splitSurveyPages()` — fungsi murni, teruji tanpa merender. Form **tanpa** bagian tetap satu halaman tanpa navigasi, jadi perilaku lamanya tak berubah. Pemeriksaan jawaban berjalan **per halaman** saat menekan Berikutnya; menundanya sampai tombol kirim berarti pengisi baru menemukan kesalahan bagian pertama setelah menyelesaikan bagian terakhir. Saat mengirim, kesalahan pertama membawa layar **lompat ke halamannya**, karena pesan untuk pertanyaan yang tak terlihat membuat pengisi menebak-nebak.
- **Penilaian karyawan lain, berurutan** (PR [#104](https://github.com/bip-itteam-internal/my-bharata/pull/104), **merged ke `dev` 2026-08-02**): form penilaian dibuka **sekali**, lalu pengisi maju dari orang ke orang tanpa kembali ke daftar. Tanpa ini, menilai empat office boy berarti membuka form empat kali dan mengisi ulang seluruh halamannya. Tombolnya **"Simpan & Lanjut"**, berganti **"Simpan & Selesai"** pada orang terakhir.
	- Header "sedang menilai" (nama, jabatan, nomor keberapa dari berapa, garis kemajuan) diulang di **setiap** halaman bagian, bukan cuma di awal: pertanyaannya sama persis untuk empat orang, dan itu yang paling mudah terlupakan begitu pengisi menggulir.
	- **Orang berikutnya dicari dari yang BELUM selesai**, bukan indeks berikutnya, sehingga pengisi yang menutup aplikasi di tengah jalan kembali ke tempatnya berhenti.
	- **Pengalihan ke alur ini dikerjakan di `SurveyFillPage`, bukan di kartu beranda**: notifikasi "form terbit" dari backend memakai rute `/form/<id>` yang sama untuk kedua jenis form, jadi kalau ditaruh di kartu, penerima tautan notifikasi mendarat di halaman pengisian biasa yang pasti ditolak backend karena tak menyebut siapa yang dinilai.
	- `SurveyFillView` **dilepas dari `SurveyBloc`** dan menerima callback `onSubmit`; tampilan yang sama dipakai dua alur berbeda blocnya. Kunci widget diganti per orang (`ValueKey(employeeId)`) supaya State isian lama dibuang — tanpa itu jawaban orang sebelumnya terbawa dan terkirim tanpa disadari.
	- Daftar sasaran yang **kosong atau sudah selesai** tak dibiarkan masuk ke layar pengisian, dan **kegagalan mengambilnya tidak** diperlakukan sebagai daftar kosong (berbeda dari daftar form di beranda yang memang sengaja diam saat gagal). Keduanya akan mengatakan "sudah selesai semua" kepada orang yang belum menilai siapa pun.
- Sumber data `GET /api/form-builder/me/forms` + `GET .../me/forms/:id/subjects` + `POST .../me/forms/:id/responses` (+`subject_employee_id`). Backend: [[Microservices - Form Builder Service]] · kontrak: [[API - Form Builder Service]]
- Fitur `features/form`. my-bharata PR [#93](https://github.com/bip-itteam-internal/my-bharata/pull/93) (merged, `dev`) · [#104](https://github.com/bip-itteam-internal/my-bharata/pull/104) (open, versionCode **134**).

> [!important] Section ini menghilang sepenuhnya saat gagal memuat, bukan hanya saat kosong
> `form-builder-service` **belum jalan di prod**, jadi di produksi endpointnya membalas `404`. Datasource menerjemahkan `404` jadi daftar kosong, dan section memperlakukan keadaan gagal **sama dengan kosong**: tak ada judul menggantung, tak ada kerangka, tak ada pesan galat. Memunculkan kegagalan di layar utama untuk fitur yang belum dirilis di lingkungan itu lebih buruk daripada diam. Halaman pengisian tetap menampilkan pesan errornya sendiri.

> [!warning] Tiga aturan kontrak yang mudah dilanggar diam-diam
> **`number` dan `scale` wajib dikirim sebagai angka JSON.** Backend memakai pembanding tipe yang menolak string, sedangkan input teks di layar selalu menghasilkan string. Konversinya dipusatkan di `answer_encoder.dart`.
>
> **Koma diterima sebagai pemisah desimal** ("36,5") lalu dinormalkan ke titik. Papan ketik angka menyediakan komanya dan orang Indonesia menulis begitu; menolaknya berarti menjebak pemakai.
>
> **`scale_min` bertag `omitempty` di backend**, jadi skala `0..N` datang **tanpa** field itu. Nilai bawaannya harus 0, bukan 1 — menebak 1 membuat pilihan terendah tak pernah bisa disentuh.

### Struktur menu beranda

> Status: ✅ Implemented — diperbaiki di PR [#114](https://github.com/bip-itteam-internal/my-bharata/pull/114), **merged ke `dev`** 2026-08-11 (versionCode **143**). ⚠️ Belum diverifikasi di aplikasi berjalan; lihat catatan di akhir bagian ini.

**Hanya ada SATU daftar menu yang benar-benar dirender: `home_quick_access.dart`.** Grid beranda menampilkan favorit tersimpan pemakai, dan tombol **"Semua Menu"** membuka `showQuickAccessMoreBottomSheet` yang merender daftar yang sama tanpa penyaring. Menu baru **wajib** masuk ke situ.

Grid hijau di atasnya (`home_menu_grid.dart`) bukan daftar menu umum: isinya empat pintasan tetap (Jadwal, Pengajuan, Slip Gaji, QR Code).

> [!warning] Sheet "Lainnya" mati diam-diam selama hampir enam bulan
> `more_menu_page.dart` (`MoreMenuBottomSheet`) berisi 19 menu dan **tak pernah bisa dibuka sejak commit `e125b6e0`, 2026-02-21**. Pemanggilnya digerbang item ber-route `RouteNames.moreMenu`, dan item itu hilang saat UI beranda dirombak, sementara cabang `if`-nya tertinggal. Berkasnya jadi terlihat persis seperti tempat yang benar untuk menambah menu, lalu memakan **dua fitur berturut-turut**: Kaizen (PR #108, 2026-08-06) dan Pelatihan (PR #112, 2026-08-11). Keduanya merged, ter-build, dan mustahil dibuka pemakai.
>
> Tak satu pun test merah, karena **tak ada test yang pernah menanyakan apakah sebuah menu bisa dicapai**. Penjaganya kini `quick_access_items_test.dart`: menu ada di daftar yang benar, **dan** tiap rute menu benar-benar terdaftar di router.
>
> Berkasnya dihapus di PR #114 setelah diaudit: dari 19 item, 7 placeholder `comingSoon`, 8 sudah punya pintu lain, 1 (`inbox`) rutenya memang tak pernah terdaftar, 1 (`overtime`) rutenya sah tapi tanpa pintu lain. Tak ada menu berfungsi yang hilang.

**Cacat sejenis yang belum ditutup** (dicatat, belum dikerjakan):

- **Lembur** (`RouteNames.overtime`) punya `GoRoute` dan halaman sah, tapi **nol pintu masuk** untuk pemakai biasa sejak Februari 2026. Hanya ada di menu developer.
- **`/inbox`** dideklarasikan di `names.dart` **tanpa `GoRoute` maupun halaman**. Halaman notifikasi yang asli adalah `/notifications`.

⚠️ **PR #114 merged tapi BELUM pernah dijalankan di aplikasi.** Bukti yang ada baru 727 test hijau plus `dart analyze` bersih, dan justru bug inilah yang membuktikan keduanya bukan bukti fitur terjangkau. Yang masih harus dilakukan sekali: buka flavor dev → **Semua Menu** → pastikan Kaizen dan Learning terlihat → tekan keduanya sampai halamannya benar-benar terbuka. **Halaman Pelatihan yang tampil kosong adalah pertanyaan, bukan kabar baik** — `learning-service` di dev harus sudah naik, dan `/me/trainings` tercatat belum pernah dipanggil siapa pun.

### Kaizen (menu tersendiri)

> Status: **merged ke `dev`** lewat PR my-bharata [#108](https://github.com/bip-itteam-internal/my-bharata/pull/108) (versionCode **137**). ⚠️ **Menunya tak pernah benar-benar bisa dibuka** sampai PR [#114](https://github.com/bip-itteam-internal/my-bharata/pull/114) — lihat [[#Struktur menu beranda]]. Konsep: [[HRIS - Kaizen (Ide Perbaikan)]].

Menu **Kaizen** di **Quick Access** (`home_quick_access.dart`), sebelah KPI. **Bukan** kartu di section Survei, dan form Kaizen justru **dikeluarkan** dari section itu.

> Catatan koreksi: PR #108 menaruhnya di "Lainnya → Pengembangan Diri", dan catatan lama di dok ini menyebut lokasi itu. Sheet "Lainnya" ternyata sudah mati sejak Februari 2026, jadi selama dua bulan Kaizen hanya terjangkau lewat deep link notifikasi. Dipindahkan ke Quick Access di PR #114.

Sebabnya program Kaizen bukan "satu form lagi" bagi pengisinya: berulang tiap periode, berkuota, punya riwayat keputusan komite. Satu kartu survei tak bisa menjelaskan semuanya sekaligus, dan menampilkannya di dua tempat membuat karyawan mengira ada dua hal berbeda yang harus dikerjakan.

- **Beranda menu** — kartu progres kuota ("1 dari 2 ide, sisa 9 hari") + tombol kirim ide. Tombolnya **tidak dimatikan** saat kuota terpenuhi: kuota adalah lantai, bukan langit-langit.
- **Riwayat** — ide sendiri lintas periode, terbaru dulu, berhalaman. **Detail ide tak memanggil apa pun** karena jawaban sudah ikut di daftar, jadi terbuka seketika dan tetap terbaca tanpa jaringan.
- **Menu selalu tampil**, tidak disembunyikan berdasarkan sasaran program. Sasaran ditentukan HR dan berubah tiap periode; menu yang muncul-hilang mengikutinya terbaca sebagai fitur rusak. Halamannya sendiri yang menjelaskan saat tak ada program.
- **Riwayat yang gagal dimuat dibedakan dari riwayat kosong**, dan kegagalannya tak menjatuhkan kartu progres. "Belum ada ide" kepada orang yang sudah mengirim sepuluh membuatnya mengira datanya hilang.
- Sumber data `GET /api/form-builder/me/kaizen` + `.../me/kaizen/ideas`; pengiriman idenya memakai `POST .../me/forms/:id/responses` **yang sama** dengan survei. `SurveyFillView` dan `SurveyBloc` dipakai ulang apa adanya, bukan ditiru.
- Fitur `features/kaizen`.

**Penyaringan Kaizen dari section Survei dikerjakan di `surveySectionOf`, bukan di dalam bloc.** Halaman pengisian form mencari formnya lewat `pendingOf`, dan menyaring di sana akan mematikan tautan lama dari notifikasi yang terlanjur terkirim. Form tanpa `form_type` (dokumen sebelum tipe form ada) **tetap tampil**: menjatuhkannya akan membuat form lenyap dari layar karyawan tanpa satu pun galat.

> [!warning] Navigasi notifikasi digerakkan KATEGORI, bukan field `route` dari backend
> `NotificationRouteMapper` memetakan kategori ke rute internal, dan field `route` yang dikirim backend (`/form/<id>`) **tak dibaca sama sekali** — rute itu bahkan tak ada di `RouteNames`. Kategori yang tak dikenal jatuh ke kotak masuk, jadi kategori baru **wajib** didaftarkan di mapper itu atau notifikasinya mendarat di tempat yang salah tanpa galat.
>
> PR #108 mendaftarkan `kaizen-reminder` dan `kaizen-decided` → menu Kaizen, dan menambahkan empat kategori form-builder ke `NotificationType` (`form-published` dan `form-submitted` sudah lama live tapi tak pernah dikenali, jadi tampil dengan ikon server).
>
> Terpisah dari itu: kategori Kaizen juga belum terdaftar di **`shared-library` sisi backend**, sehingga notifikasinya ditolak `400` dan tak pernah terkirim sejak awal. Dua lapis berbeda, keduanya harus dibereskan.

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

Semula tercantum di menu tetapi masih placeholder (route `/coming-soon` atau stub):
- Digital ID, My Documents, Policy/Handbook, Insurance, Loan, Meeting Room, Vehicle, Inbox, Chat HRD

⚠️ **Tujuh di antaranya (Digital ID sampai Vehicle) sudah tak tercantum di menu mana pun** sejak `more_menu_page.dart` dihapus di PR #114 — dan sebenarnya sudah tak terjangkau sejak Februari 2026, lihat [[#Struktur menu beranda]]. Key l10n-nya sengaja **dibiarkan** di kedua berkas ARB sebagai satu-satunya catatan tersisa bahwa menu ini pernah direncanakan. Menghidupkannya kembali berarti menambahkannya ke `home_quick_access.dart`.

✅ **Learning** tak lagi placeholder sejak PR [#112](https://github.com/bip-itteam-internal/my-bharata/pull/112) **merged ke `dev`** — lihat di bawah.

## Pelatihan Saya — ✅ PR [#112](https://github.com/bip-itteam-internal/my-bharata/pull/112) merged ke `dev`

Mengisi menu **Learning** yang selama ini `ComingSoon`. Daftar pelatihan yang diikuti (berjalan / riwayat), **tandai hadir mandiri**, dan **penilaian trainer** empat aspek.

Ini menutup lubang lama: `/me/trainings` di [[Microservices - Learning Service]] **tak pernah dipanggil siapa pun** — tidak oleh web, tidak oleh aplikasi. `can_attend` bahkan dirancang khusus untuk aplikasi ini sejak awal, lengkap dengan alasan tertulis kenapa server yang menghitungnya, tapi tak pernah ada tombolnya.

- **Seluruh keputusan dari server**: `can_attend` + `attend_block_reason`, `boleh_menilai` + `sudah_dinilai`. Tak satu pun dihitung ulang di Dart.
- **Field yang absen gagal-TERTUTUP**: server versi lama tak mengirim penanda penilaian; absen diperlakukan "tidak boleh" supaya tak ada tombol yang pasti dibalas 409.
- **Pesan galat server diteruskan apa adanya** — sebagian penolakan memberi tahu, bukan sekadar gagal.
- ✅ ~~Pengajuan pelatihan TIDAK termasuk~~ — prasyaratnya (bip-erp PR [#1153](https://github.com/bip-itteam-internal/bip-erp/pull/1153), `department_key` jadi opsional) **merged 2026-08-11**, dan layarnya menyusul di PR [#115](https://github.com/bip-itteam-internal/my-bharata/pull/115). Lihat bagian tersendiri di bawah.
- ⚠️ **Publish sebelum `learning-service` di dev naik = menu terlihat tapi kosong**, dan tombol Nilai Trainer tak pernah muncul (gagal-tertutup di atas).
- ⚠️ **Rute `/pelatihan-saya` tak pernah didaftarkan di PR #112.** Halamannya ada di `misc_pages.dart`, `GoRoute`-nya tidak, jadi menekan menunya akan mendarat di layar galat go_router, bukan di halamannya. **Halaman terdaftar di `AppPages.getPage` bukan berarti rutenya ada** — keduanya berkas terpisah dan tak ada yang memaksa keduanya sinkron. Diperbaiki di PR #114 beserta test regresinya.

## Pengajuan Pelatihan & Tugas Onboarding — 🔜 PR [#115](https://github.com/bip-itteam-internal/my-bharata/pull/115) (belum merge)

> ⛔ **Masih OPEN per 2026-08-19, enam hari sesudah menunya dicabut di web.** Diverifikasi: commit-nya tak ada di `origin/dev` maupun `origin/main`. Selama PR ini menggantung, **karyawan biasa tak punya satu pun jalan bermenu** untuk mengajukan pelatihan — web sudah mencabut menunya 2026-08-13, aplikasinya belum punya layarnya. Terlihat di data produksi: `training_request` **0 dokumen** walau endpointnya live sejak 2026-08-11. Ini bukan sekadar fitur tertunda melainkan **alur yang terputus di tengah**, dan yang menutupnya cuma merge + rilis PR ini. Lihat [[Microservices - Learning Service]] dan [[HRIS - Training Program]].

Dua layar **self-service yang PINDAH dari web**: menunya dicabut dari Portal Saya > Manajemen HR di erp-frontend [#1022](https://github.com/bip-itteam-internal/erp-frontend/pull/1022). Keduanya urusan karyawan atas pekerjaannya sendiri, dan sebagian besar karyawan tak duduk di depan komputer. Detail sisi web di [[APP - Web ERP]].

- **`/pengajuan-pelatihan`** menumpang `features/training/` yang sudah ada: daftar pengajuan sendiri (`as=self`) berikut kedua tahap peninjauan dan catatan penolakannya, formulir topik/alasan/perkiraan biaya, dan pembatalan untuk yang masih menunggu keputusan.
- **`/tugas-onboarding`** jadi modul baru `features/onboarding_tasks/`. ⚠️ Namanya sengaja **BUKAN** `onboarding`: berkas itu sudah dipakai onboarding APLIKASI (registrasi, PIN, biometrik) dan tak berhubungan sama sekali dengan checklist karyawan baru.
- ⚠️ **Formulir memakai TOPIK BEBAS, tanpa katalog jenis pelatihan.** Bukan penyederhanaan sementara: `GET /training/types` digerbang `PermTrainingView`, yaitu izin **mengelola** pelatihan, sehingga karyawan biasa dibalas 403. Server memang menerima katalog **atau** topik bebas.
- ⚠️ **Body pengajuan tak mengirim `department_key` maupun `employee_id`.** Keduanya kosong berarti "departemen saya" dan "untuk saya sendiri", diselesaikan server dari header identitas. Mengirim key dari aplikasi menuntutnya menyalin pemetaan nama↔key departemen, dan salinan itu persis yang melahirkan bug 409 di 6 dari 10 departemen. Dikunci test regresi.
- ⚠️ **Catatan tugas onboarding SELALU ikut dikirim**, walau tak diubah: server menyetel `tasks.$.note` apa adanya, jadi menyimpan status tanpa menyertakan catatan yang sedang tampil akan menghapusnya tanpa satu pun pesan. Dikunci test regresi.
- **Antrean peninjau TIDAK ikut pindah.** Aplikasi hanya memakai `as=self`; menyetujui dan menolak tetap di web, sebab penyetujunya bekerja dari sana dan penolakan di tahap mana pun bersifat final.
- ⚠️ **Menunya sudah dicabut di web SEBELUM rilis ini naik ke store.** Sampai build-nya sampai ke orang, kedua layar itu hanya terjangkau lewat tautan langsung ke rute web yang dibiarkan dormant. Tugas onboarding yang paling terasa: modulnya tak mengirim notifikasi apa pun, sehingga PIC tak punya pemberitahuan lain.
- ⚠️ **Deep link notifikasinya belum benar-benar hidup.** `rutePengajuanUntukMobile` di learning-service kini berisi rute aplikasi (bip-erp [#1198](https://github.com/bip-itteam-internal/bip-erp/pull/1198)) dan nilainya dikunci test di kedua repo, TAPI `/inbox/send` hanya menyimpan dokumen inbox tanpa push FCM, dan daftar notifikasi di aplikasi belum menavigasi ke mana pun. Membuat inbox bisa diketuk berarti fitur baru untuk SELURUH kategori notifikasi (10 titik pengirim, sebagian masih mengisi `app_route` dengan rute web) — keputusan produk tersendiri.

## Roadmap (Belum Diimplementasikan)

- **Offline-Mode Attendance** — rekam absensi offline (GPS terenkripsi lokal), auto-sync saat online *(prioritas: High)*
- Naikkan test coverage 55% → 70% (fokus `attendance`, `payroll`)
- Migrasi widget `payroll` lama ke dark theme
- Penyatuan penanganan timezone (server UTC, format lokal di presentation)

## Known Issues

1. **Selisih waktu attendance lintas timezone** — perjalanan dinas lintas zona (mis. WIB → WITA) menampilkan jam clock-in yang salah; sebagian presentation pakai `DateTime.now()` lokal alih-alih konversi dari UTC server
2. ⛔ **(Tidak berlaku) Download payslip gagal di sebagian Android 13+** — dicabut 2026-08-05: **tidak ada kode unduh payslip** di `my-bharata` yang bisa gagal; ini terbawa dari aplikasi lama. Unduhan PDF yang baru menulis ke direktori aplikasi sendiri sehingga tak menyentuh izin storage yang jadi sebab masalah itu.
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
- [[Microservices - Form Builder Service]] · [[API - Form Builder Service]]
- [[HRIS - Kaizen (Ide Perbaikan)]] — konsep program ide bulanan di balik menu Kaizen
- [[APP - Dynamic Task Tracker]]

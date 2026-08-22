## Deskripsi

*Hub notifikasi multi-channel untuk seluruh ekosistem: in-app inbox, FCM push, WhatsApp, splash promotion, dan article. Menyatukan berbagai channel pihak ketiga dalam satu service sehingga tiap service lain tidak perlu melakukan setup sendiri-sendiri.*

- **Stack:** Go + Fiber v2 + MongoDB
- **Path:** `services/notification`
- **Status**: ✅ Implemented penuh · multi-perusahaan: pengiriman FCM (personal/departemen/broadcast) **ter-scope `company_id`** (`common.CompanyID(c)` → `/list?type=fcm-token&company_id=`) dan **feed Article ter-scope** (PR #662). `InboxMessage` belum punya `company_id` (baca per-`employee_id` = aman; flag bila ada fitur agregat inbox). Lihat [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].

## Endpoint / Fitur (Sudah Diimplementasikan)

- **Health & util:**
	- `GET /health`
	- `GET /data-type/:dt`
	- `GET /debug/fcm` (khusus dev)
- **Inbox (in-app):**
	- `GET /inbox` — list, dukung `?count=unread|read|all`, serta `?id=` untuk mark-read
	- `GET /inbox?page=N` — **paginasi OPT-IN** (`?limit=` bawaan 15 batas 100, `?status=unread|read`). Balasannya `{data, pagination}` dengan enam kunci yang sama persis dengan `GET /warnings` di [[Microservices - Employee Service]].
		- ⛔ **Tanpa `?page` bentuknya WAJIB tetap array telanjang.** MyBharata membaca badan respons mentah lalu menguji `data is List`; begitu balasan bawaannya dibungkus jadi objek, uji itu gagal dan cabang `else`-nya mengembalikan **list kosong, bukan galat** — inbox jadi kosong tanpa satu pun pesan. Dan karena APK yang sudah terpasang tak bisa dipaksa update, memperbaiki mobile lalu rilis ke store tidak menyelamatkan versi yang beredar. Karena itu paginasinya opt-in, bukan penggantian. Dikunci dua test berikut kontrol negatifnya (`services/notification/inbox_test.go`), termasuk penjagaan bahwa inbox kosong tetap `[]` dan bukan `null` — `json.Marshal` atas nil-slice menghasilkan `null`, dan `null is List` juga false.
	- `POST /inbox/read-all` — tandai seluruh notifikasi pemanggil yang belum dibaca. Balasannya `{"modified": n}`, **bukan 200 kosong**: tanpa angka itu frontend menampilkan "berhasil" untuk operasi yang tak mengubah apa pun.
	- `DELETE /inbox`
	- **Mark-read menyaring pemilik.** Sebelum 2026-08-20 `?id=` memakai `UpdateByID` **tanpa** filter `employee_id`, jadi siapa pun yang punya sesi bisa menandai notifikasi orang lain terbaca — ia tak bisa membacanya, tapi notifikasi yang dibaca tanpa pernah dilihat adalah notifikasi yang hilang bagi yang berhak. Kini `UpdateOne` berfilter pemilik dan membalas **404**.
	- **Indeks** `{employee_id, metadata.created_at}` dan `{employee_id, is_read}` dibuat saat startup (`ensureInboxIndexes`, pola yang sama dengan employee/learning/warehouse). Sebelumnya koleksi ini **tanpa indeks apa pun**, jadi tiap pembacaan adalah scan penuh — tertahankan selama pemakainya cuma mobile, tidak lagi setelah web menyalakan pencacah berkala untuk semua karyawan.
- **Splash promotion:**
	- `GET /splash` — yang aktif, atau `?show_all`
	- `POST /splash` — multipart image (di-upload via file-service/MinIO)
	- `DELETE /splash` — sekaligus menghapus object di MinIO
- **Article:**
	- `GET /article` — `?id`, `?recent`, atau seluruhnya; **ter-scope tenant**: hanya artikel `company_id` = perusahaan pembaca (`EffectiveCompanyID`) ATAU yang ber-`group_wide` (broadcast Bharata Group). Berlaku di ketiga cabang (all / recent / by-id).
	- `POST /article` — multipart; distempel `company_id` = perusahaan pembuat (`CompanyID(c)`, default BIP). Flag `group_wide` **hanya boleh diset admin pusat** (`IsCentralAdmin`) supaya perusahaan biasa tak bisa broadcast lintas-tenant.
	- `DELETE /article`
- **Route pengiriman (ber-service-key, `?key=` cocok `NotificationServiceKey`):**
	- `POST /inbox/send`
	- `POST /wa/send-personal`
	- `POST /wa/send-group`
	- `POST /fcm/send-personal`
	- `POST /fcm/send-department`
	- `POST /fcm/send-broadcast` (batch 500 token)
	- `POST /email/send` — Email via **Resend** (`resend-go/v3`); body `html`/`text`, attachment (base64 `content` atau `path` URL, mis. offer letter PDF), dan `idempotency_key` opsional untuk retry-safe. Field **`from` opsional**: bila kosong dipakai `RESEND_FROM_EMAIL`; **tidak divalidasi** handler (hanya `to`/`subject`/body/attachment yang dicek) → diteruskan apa adanya ke Resend, sehingga format RFC `Nama <email>` didukung — ini dasar **identitas pengirim per-service** (lihat catatan di bawah).
- **Push DUA KANAL — fan-out dari `/inbox/send`, bukan dari tiap pengirim** (browser sejak 2026-08-20, ponsel menyusul 2026-08-22):
	- Semua service pengirim sudah memanggil `/inbox/send`, jadi kipasnya dipusatkan di situ. **Nol service pengirim yang perlu disentuh**, sekarang maupun saat pengirim baru lahir — sekaligus menutup kelas bug "pengirim yang lupa" yang sudah dua kali menggigit lewat kategori inbox.
	- Dipicu **setelah insert berhasil dan di goroutine**. Keduanya perlu: pengiriman di sisi pemanggil best-effort dan hanya nge-log, jadi bila FCM yang lambat sampai menggagalkan permintaan, yang hilang bukan push-nya melainkan **notifikasinya sendiri**.
	- ⛔ **`PushWebCategories` DICABUT 2026-08-22** ([[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]]). Setiap dokumen inbox kini mendorong push ke browser **dan** ponsel tanpa penyaringan kategori. Daftar-izin lama beralasan bahwa desktop berisik membuat orang memblokir izin permanen; kekhawatiran itu tak pernah diukur, dan saat diukur ke prod puncaknya **7,4 notifikasi/hari** untuk orang tersibuk se-perusahaan. Harganya dibayar di tempat lain: Surat Peringatan tak pernah membuat ponsel berdering, sementara notifikasi task management berdering di ponsel tapi diam di desktop. **Jangan menghidupkannya kembali tanpa membaca ADR-nya**; bila kebisingan jadi masalah, bentuk yang benar adalah peredaman lonjakan, bukan penyaringan per kategori.
	- **`InboxCategories` kini satu-satunya daftar-izin kategori yang tersisa.** Ia menjaga hal berbeda: kategori salah-ketik tetap ditolak 400.
	- **Fan-out ponsel juga dipusatkan.** Panggilan `/fcm/send-*` langsung dicabut dari tiap pengirim yang sudah menulis inbox ([[Microservices - Attendance Service]], [[Microservices - Task Management Service]], `cronReminderKPI` di [[Microservices - Employee Service]]). ⚠️ **Urutan deploy jadi mengikat**: ketiga service itu wajib naik **sebelum** notification-service, kalau tidak seluruh penerima mendapat notifikasi ponsel dua kali.
	- **Payload ponsel sengaja dibiarkan seperti sebelumnya** (title + body, `data` kosong, priority normal) supaya [[APP - MyBharata]] tak perlu ikut diuji. Dikunci test.
	- **`ExtraResource.WebRoute`** diturunkan dari `AppRoute` di satu tempat (`services/notification/webpush.go`), dipakai bersama oleh tautan klik push **dan** tombol tujuan di dialog inbox web. Diisi saat tulis **dan** saat baca, supaya notifikasi yang tersimpan sebelum field ini ada tak kehilangan tujuannya. `AppRoute` adalah rute MOBILE dan hanya sebagian punya padanan web (`/form/<id>` tak punya sama sekali; `/task-management/tasks/<id>` harus ditulis ulang jadi `/task-management/<id>`), jadi bentuknya daftar-izin: yang tak terdaftar **tidak menampilkan tombol apa pun**.
	- Pencarian token **personal sengaja tanpa `company_id`**. `/inbox/send` dipanggil pakai service key tanpa identitas karyawan, jadi `common.CompanyID(c)` jatuh ke BIP dan karyawan perusahaan lain tak akan pernah ditemukan tokennya — push hilang tanpa satu pun galat. `employee_id` sudah menunjuk satu orang. Penyaringan perusahaan tetap berlaku untuk pencarian **per-departemen**, dan di sana ia dikerjakan di sisi pemanggil.
	- `fcm.SendWebToToken` adalah fungsi **baru** di shared-library, bukan perubahan signature `SendToToken`, supaya `attendance-service` tak ikut terseret rebuild. Ia membawa `WebpushConfig.FCMOptions.Link` (tanpa itu notifikasinya muncul tapi kliknya tak mengantar ke mana pun; FCM menolak link relatif, jadi butuh env **`WEB_APP_URL`** — env baru, menuntut `--force-recreate`).
	- ⚠️ **`POST /inbox/send` membalas 503 bila database belum terhubung.** Sebelum 2026-08-22 `mongodb.GetCollection` memanik di jalur ini, dan panik itu tak terlihat sebagai panik dari luar: fasthttp memutus koneksi, gateway membalas **502 tanpa petunjuk**. Ditemukan oleh test handler lewat Fiber, bukan oleh pembacaan kode.
- **Cron:** harian pukul 03:00 WIB menghapus inbox berumur > 2 bulan.
- **Kategori inbox = daftar-izin** di `notification.InboxCategories` (`shared-library`). Kategori di luar daftar ditolak **400**, dan pengiriman di service pengirim best-effort (gagal cuma nge-log) — jadi kategori tak terdaftar menghasilkan fitur yang tampak jalan penuh sementara notifikasinya tak pernah tiba. Sudah menggigit dua kali (`form-published`, `kaizen-*`), jadi penjaganya kini test di tiap service pengirim.
	- Ditambahkan 2026-08-10: **`employee-moved`** dari [[Microservices - Employee Service]], dikirim saat perpindahan jabatan (promosi/mutasi) benar-benar diterapkan. Untuk perpindahan antar-perusahaan ia bukan sekadar kabar melainkan **penambal**: modul itu sengaja belum punya approval, jadi inilah satu-satunya pemberitahuan yang diterima perusahaan tujuan ([[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]).
	- Ditambahkan 2026-08-22: **`request-replacement`** dari [[Microservices - Attendance Service]], dikirim ke orang yang ditunjuk menggantikan pekerjaan pemohon cuti atau perjalanan dinas — **setelah HRD menyetujui**, bukan saat penunjukan. Sengaja kategori sendiri, bukan menumpang `request-approved`: penerimanya tidak mengajukan apa pun, jadi label "Permohonan Disetujui" akan salah bagi orang yang justru baru diberi pekerjaan tambahan. Sudah dipetakan di MyBharata (`notification_type.dart`, label "Menggantikan Rekan") berikut test kategorinya di sisi pengirim. Lihat [[HRIS - Employee Request & Approval]].
	- ⚠️ **Kategori yang SALAH lebih sering daripada yang absen, dan sama senyapnya.** MyBharata memilih label, warna, dan ikon dari kategori (`notification_type.dart`), jadi kategori yang tak dipetakan di sana jatuh ke `system` dan tampil berlabel "Sistem" berikon server. `employee-moved` sudah dipetakan (my-bharata [#110](https://github.com/bip-itteam-internal/my-bharata/pull/110), merged ke `dev` 2026-08-10) berikut **test pemetaan yang sebelumnya belum ada sama sekali** — yang dijaganya bukan kategori yang hilang melainkan yang terpetakan keliru, sebab yang keliru tampil dengan label dan ikon yang percaya diri tapi salah.

## Belum Diimplementasikan / Catatan

- **Channel Email (Resend)** — ✅ sudah di kode (`POST /email/send`, lihat di atas) memakai SDK resmi `resend-go/v3`; ditujukan untuk notifikasi **kandidat recruitment** ([[Microservices - Recruitment Service]]). **✅ Terverifikasi jalan live di dev (2026-07-16)** — email "Lamaran Anda Telah Kami Terima" sampai ke inbox kandidat, jadi `RESEND_API_KEY` & `RESEND_FROM_EMAIL` sudah terpasang di deploy. Catatan operasional: `from` wajib memakai domain terverifikasi di Resend (`bharatainternasional.com` — SPF/DKIM/DMARC) atau Resend menolak (HTTP 422); bila env kosong, `email.Init()` warn-and-skip sehingga service tetap berjalan.
- **Identitas pengirim per-service (pola wajib)** — `RESEND_FROM_EMAIL` adalah **default untuk SEMUA service**, jadi **jangan** diisi nama satu domain-bisnis (mis. "Recruitment"): email service lain (mis. payroll/slip gaji) yang tidak mengisi `from` akan ikut tampil dengan nama itu. Pola: `RESEND_FROM_EMAIL` = default **generik** (mis. `Bharata Internasional <noreply@…>`); **tiap service mengisi `from` sendiri** lewat env-nya — recruitment: `RECRUITMENT_EMAIL_FROM` (mis. `Bharata Recruitment <noreply@…>`, lihat [[Microservices - Recruitment Service]]); payroll dst. mengikuti pola sama **tanpa** mengubah shared-library. Cukup menambah display name di depan alamat yang sudah terverifikasi. Saat ini **recruitment adalah satu-satunya pemanggil `/email/send`**.
- Semua channel (inbox/FCM/WhatsApp/email/splash/article) sudah fungsional di kode — tidak ada stub berarti.
- **Isolasi tenant feed Article (PR #662)**: `GET /article` dulu global (`bson.M{}`) sehingga karyawan perusahaan lain melihat pengumuman BIP; ketahuan saat uji mobile akun ELT. Model `Article` kini punya `company_id` + `group_wide`, plus migrasi backfill idempoten artikel lama ke BIP (guard `$exists:false`). Backward-compat: FE lama tetap jalan karena `group_wide` default `false`. Toggle "Bharata Group" di web sudah ada ([[APP - Web ERP]]).
- Group `/debug/fcm` ditandai dapat dihapus saat production.

## Dependencies & Integrasi

- **MongoDB** — penyimpanan inbox, splash, dan article.
- **FCM** — push notification (via shared-library).
- **WhatsApp** — pesan personal/grup (via shared-library).
- **Resend** — provider email transactional (via `resend-go/v3` di shared-library `notification/email`); butuh env `RESEND_API_KEY` & `RESEND_FROM_EMAIL` (sender pada domain terverifikasi). Alasan memakai layanan pihak ketiga alih-alih mail server sendiri: [[ADR - 0026 Email Transaksional via Resend (bukan Mail Server Sendiri)]].
- Service lain:
	- [[Microservices - Employee Service]] — sumber nomor telepon & FCM token (by id/nama/department/platform).
	- [[Microservices - File Service]] — upload/hapus object di MinIO untuk image splash & article.
- Diakses melalui [[CORE - API Master Gateway]].
- Lihat juga [[DB - Overview and Notes]].

## Dokumen Terkait

- [[CORE - API Master Gateway]]
- [[Microservices - Employee Service]]
- [[Microservices - File Service]]
- [[DB - Overview and Notes]]
- [[APP - MyBharata]]
- [[ADR - 0026 Email Transaksional via Resend (bukan Mail Server Sendiri)]] — kenapa Resend, bukan mail server self-hosted
- [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]] — kenapa daftar-izin push dicabut, dan kenapa jangan dihidupkan kembali
- [[IT - Background Jobs & Schedulers]] — cron service ini (cleanup inbox >2 bulan, harian 03:00)

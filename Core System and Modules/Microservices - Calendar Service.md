## Deskripsi

*Kalender terpusat lintas modul. Service ini menarik agenda dari service lain lewat satu kontrak feed yang seragam, menormalkannya jadi satu bentuk, lalu menyajikannya sebagai satu daftar; sejak 2026-08-06 ia juga **memiliki satu jenis agenda sendiri** (`event`), yaitu agenda yang dibuat karyawan langsung dari kalender. Tujuannya agar karyawan punya satu tempat untuk semua yang menyangkut dirinya, dan agar setiap modul baru yang punya tanggal cukup **mendaftarkan feed**, bukan membangun kalender sendiri-sendiri.*

> **Prinsip tiga lapis** (keputusan pemilik produk, 2026-08-06): kalender memuat **data diri sendiri**, **pekerjaan sendiri**, dan **agenda perusahaan**. Data pribadi orang lain **tidak boleh** masuk, sekalipun pemanggilnya seorang supervisor. Prinsip ini yang menutup insiden privasi di bawah, dan ia mengikat semua feed baru.

- **Status**: ⚠️ Implemented (ada catatan) — agregasi + agenda mandiri **live di DEV** dan terverifikasi lewat gateway. Terakhir: PATCH sebagian ([#1067](https://github.com/bip-itteam-internal/bip-erp/pull/1067), 2026-08-07). **PROD tertinggal**: baru sampai irisan 1. Irisan 3 (sesi wajib) belum ada kode.
- **Stack**: Go + Fiber + MongoDB (`calendar_db`, koleksi `calendar_events`). Env `MONGO_CALENDAR_DB` **wajib**; tanpa itu service tetap hidup tapi seluruh agenda mandiri membalas 500.
- **Path di repo**: `bip-erp/services/calendar/` · FE: `erp-frontend/src/features/calendar/` + `src/app/(main)/calendar/`
- **Rute gateway**: `/api/calendar/*` (entri `"calendar"` di map `InternalURL` [[CORE - API Master Gateway]]; masuk `noCacheRoutes`).

## Aturan Integrasi (WAJIB dibaca sebelum menambah fitur bertanggal)

> **Aturan pokok**: fitur apa pun yang punya **tanggal, jadwal, atau tenggat** yang perlu dilihat orang **WAJIB mendaftarkan feed** ke service ini, dan **DILARANG** membangun halaman kalender sendiri.

Alasannya bukan kerapian: tiap kalender tambahan membawa salinan aturan visibilitasnya sendiri, dan salinan itu yang menyimpang diam-diam sampai ada yang melihat agenda yang seharusnya tidak boleh dilihatnya.

### Cara mendaftarkan feed

1. **Kalau service Anda belum punya feed**: tambah `GET /internal/calendar-feed?from=<RFC3339>&to=<RFC3339>` yang membalas `{"items": [...]}`.
2. **Kalau sudah punya**: cukup tambah `kind` baru di endpoint feed yang sudah ada. Tidak ada perubahan di frontend.
3. Tambah satu baris di `providerRegistry` (`services/calendar/providers.go`) bila service Anda belum terdaftar, plus env `<SERVICE>_MODULE_URL` di blok `calendar-service` pada `docker-compose.yml`.

### Bentuk item (wajib diikuti)

| Field | Aturan |
|---|---|
| `id` | Berprefiks sumber: `<source>:<kind>:<id-asli>`. ObjectId antar-service bisa bertabrakan dan React butuh key yang benar-benar unik |
| `kind` | Slug jenis agenda. Jenis yang belum dikenal FE tetap tampil dengan gaya netral, jadi aman menambah duluan |
| `start_at` / `end_at` | RFC3339 |
| `all_day` | Dipisah dari waktu. Cuti, libur, dan ulang tahun berlangsung seharian; interview dan rapat berjam. Tanpa penanda ini tampilan bulanan salah merender keduanya |
| `scope` | `personal` \| `department` \| `company` |
| `deep_link` | **Wajib**. Kalender adalah **pintu, bukan tujuan**: mengkliknya berarti lompat ke halaman modul asalnya. Karena itu feed tak perlu menyalin detail agenda |
| `status` | `confirmed` \| `tentative` \| `cancelled` |

### Aturan yang tidak boleh dilanggar

- **Penyaringan hak akses dikerjakan DI SERVICE SUMBER**, bukan di kalender. Kalender sengaja tidak punya aturan visibilitas sendiri untuk item yang ditariknya. (Pengecualian: agenda mandiri milik service ini punya aturannya sendiri di `event_visibility.go`, karena datanya memang miliknya.)
- **Feed HANYA memancarkan data pemanggil sendiri.** Batasnya bukan "yang boleh dilihat menurut RBAC", melainkan "milik pemanggil". Supervisor punya halaman modul untuk melihat anak buahnya; kalender bukan tempatnya. Pelanggaran aturan ini pernah terjadi dan tidak terdeteksi test mana pun (lihat insiden privasi di bawah).
- **Prefix `/internal/` TIDAK membuat rute privat.** Gateway tetap meneruskan permintaan dari internet, jadi tiap endpoint feed wajib memeriksa identitas pemanggil sendiri. Lihat [[Microservices - Employee Service]] yang sudah mencatat pola ini di rute `/internal/check`.
- **Jangan masukkan URL provider ke map yang divalidasi `ValidateInternalURL`.** Penjaga itu memanggil panic untuk URL kosong, dan di sini URL kosong adalah keadaan sah: service sumber yang belum ter-deploy cukup dilewati. Melanggar ini memadamkan seluruh kalender hanya karena satu service belum di-deploy.
- **Jangan menulis ulang resolusi milik modul lain.** Feed shift memanggil resolver jadwal yang sama dengan halaman Jadwal, karena urutan menangnya berlapis (roster menimpa jadwal dasar, lalu Tukar Shift menimpa keduanya). Menyalin urutan itu melahirkan sumber kebenaran kedua yang pasti menyimpang.
- **Jangan menambah endpoint kalender sendiri.** Rencana `GET /bookings/calendar` di [[GA - Asset Loan & Room Booking]] harus menjadi `/internal/calendar-feed` di [[Microservices - Inventory Service]] saat dikerjakan, bukan kalender kedua.
- **Feed yang gagal tidak boleh menjatuhkan kalender.** Kegagalan apa pun (termasuk 404 karena endpoint belum ada) turun kelas jadi penanda `degraded`, dan frontend memberi tahu pengguna. Kalender bolong tanpa pemberitahuan lebih berbahaya daripada kalender yang mengaku sedang pincang.

### Checklist untuk AI agent

Saat merencanakan fitur yang menyentuh tanggal, jawab dulu:

1. Apakah fitur ini menghasilkan sesuatu yang orang perlu lihat di kalender? Kalau ya, feed-nya masuk lingkup pekerjaan, bukan follow-up.
2. Siapa yang boleh melihat item ini, dan apakah penyaringnya sudah ada di service sumber?
3. Apakah item ini seharian atau berjam?
4. `deep_link`-nya ke halaman mana?
5. Apakah jenis ini bertabrakan dengan feed yang sudah ada (mis. hari libur yang sudah dipancarkan attendance)?

## Endpoint / Fitur (Sudah Diimplementasikan)

**Publik (lewat gateway):**
- `GET /api/calendar?from&to&scope&kinds` → `{ items[], degraded[] }`. `from`/`to` wajib RFC3339, `to >= from`, rentang maksimal 400 hari. `scope` opsional (`personal`/`department`/`company`), `kinds` opsional (dipisah koma).
- `POST /api/calendar/events` → agenda mandiri baru. `company_id`, `created_by`, dan `cancelled_at` **diturunkan dari identitas pemanggil**, bukan dari badan permintaan.
- `GET /api/calendar/events/:id` → detail. Membalas **404, bukan 403**, saat pemanggil tak berhak: membedakan keduanya memberi tahu penanya bahwa agenda itu ada, dan keberadaannya sendiri sudah informasi.
- `PATCH /api/calendar/events/:id` → perubahan **sebagian**; field yang tidak disebut dipertahankan. Hanya pembuat.
- `POST /api/calendar/events/:id/cancel` → pembatalan **lunak**. Agenda yang batal tetap terlihat sampai waktunya lewat, karena agenda yang lenyap tanpa jejak membuat peserta mengira mereka salah ingat.

**Feed yang sudah terdaftar:**

| Service | `kind` | Catatan |
|---|---|---|
| [[Microservices - Attendance Service]] | `holiday` | Hari libur perusahaan, seharian, lingkup `company` |
| [[Microservices - Attendance Service]] | `leave` | Cuti/izin/sakit **milik pemanggil sendiri saja**, berstatus disetujui. Izin berjam tidak dijadikan seharian |
| [[Microservices - Employee Service]] | `contract_end` | Kontrak pemanggil sendiri berakhir. PKWTT dibuang karena `end_date`-nya kosong |
| [[Microservices - Task Management Service]] | `task_due` | Tenggat tugas pemanggil. Penyaring "belum selesai" memakai `completed_at`/`is_archived` **plus** status `Ditolak` secara eksplisit, karena penolakan tidak menstempel `completed_at` dan kosakata statusnya tidak konsisten (Done/Selesai/Dikerjakan/Progress/Ongoing/Todo/Request) |
| [[Microservices - Form Builder Service]] | `form_period` | **Kaizen saja.** Hanya kaizen yang menyimpan snapshot peserta, jadi hanya di sana bisa dipastikan periode itu memang kewajiban pemanggil. Item ditaruh di `closes_at`, dan yang sudah memenuhi kuota dilewati lewat `countMyKaizenIdeas` yang sudah ada |
| **calendar (sendiri)** | `event` | Agenda mandiri. Satu-satunya jenis yang menampilkan orang lain, dan itu sah karena pesertanya dilibatkan dengan sengaja oleh pembuatnya |

### Aturan visibilitas agenda mandiri

Ditegakkan `canViewEvent` di `event_visibility.go`, urutannya penting:

1. **Beda `company_id` selalu ditolak**, diperiksa paling awal. Tenant mendahului segalanya.
2. Pembuat dan peserta selalu boleh.
3. Selebihnya bergantung `scope`: `company` boleh siapa saja setenant, `department` hanya yang departemennya sama, `personal` tidak ada tambahan.

Perbandingan tak peka huruf besar-kecil, dan **string kosong tidak pernah dianggap sama dengan string kosong** — kalau tidak, karyawan tanpa departemen akan saling melihat agenda departemen masing-masing.

Query Mongo menyempitkan seadanya, lalu **tiap dokumen tetap dilewatkan `canViewEvent`**. Query adalah pengecil beban, bukan gerbang: menaruh aturan visibilitas di dua tempat berarti keduanya bisa menyimpang diam-diam.

## Belum Diimplementasikan / Catatan

### Insiden privasi 2026-08-06 (baca sebelum menambah feed)

Feed `leave` dan `contract_end` semula menyaring pakai aturan RBAC modul asalnya, sehingga **`hris:supervisor` dan `admin` melihat cuti serta akhir kontrak seluruh karyawan** di kalendernya. Secara RBAC itu sah; sebagai kalender itu salah, dan pemilik produk menemukannya dari layar, bukan dari test. Keduanya kini **milik-sendiri saja** ([#1047](https://github.com/bip-itteam-internal/bip-erp/pull/1047)), dikunci test dua arah.

Pelajarannya: **"boleh diakses" bukan "layak muncul di kalender"**. Kalender adalah ruang pribadi seseorang, dan menaruh data orang lain di sana mengubah artinya tanpa satu pun pesan. Tiap feed baru wajib menjawab pertanyaan ini secara eksplisit, dan jawabannya harus dikunci test.

### Keputusan lingkup

- **Ulang tahun karyawan sengaja TIDAK masuk** (2026-08-06). Endpointnya ada dan murah, tapi itu bukan alasan memasukkannya. Ia tetap tampil di widget Agenda Mendatang pada dashboard HRIS.
- **Jadwal kerja / shift DIHAPUS dari kalender** (2026-08-06), padahal feed-nya sudah jadi dan sudah terverifikasi 79 dari 79 cocok dengan halaman Jadwal. Alasannya lingkup, bukan mutu: shift adalah keadaan sehari-hari, bukan agenda, dan memenuhi kalender dengannya menenggelamkan hal-hal yang benar-benar perlu diingat. Kodenya dihapus, bukan dimatikan lewat flag; [[Microservices - Attendance Service]] tetap menyediakan resolvernya untuk halaman Jadwal.
- **Tukar Shift** ikut hilang dengan sendirinya karena hasilnya dulu tercermin di feed `shift`.

### Belum ada

- **Jadwal club/komunitas — TERBLOKIR.** Datanya masih konstanta di frontend ([[Microservices - Employee Service]] tidak menyimpannya), jadi belum ada yang bisa dijadikan feed. Butuh keputusan pemilik data lebih dulu: HR mengelolanya lewat UI (perlu master data + halaman pengelolaan baru) atau IT yang menanamnya (read-only, di-seed).
- **Irisan 3, sesi wajib (belum ada kode)**: mesin kewajiban berulang (one-on-one bulanan, pelatihan wajib) beserta papan kepatuhan. Polanya menyalin `FormPeriod` di [[Microservices - Form Builder Service]] yang sudah terbukti di produksi. Yang wajib memilih sendiri lawan sesinya dari kandidat yang lolos aturan `counterpart` per-template, aturan itu ditegakkan **di server** bukan sekadar dipakai menyaring dropdown. Menjadwalkan **tidak** langsung memenuhi kewajiban; pertemuannya tetap harus ditandai selesai, supaya angka kepatuhan mengukur kenyataan, bukan niat.
- **TIDAK ADA persetujuan lawan** (keputusan pemilik produk 2026-08-07, membatalkan rancangan sebelumnya). Sesi wajib dihitung sebagai KPI, jadi agenda yang menunggu tombol setuju berarti **kepatuhan seseorang ditentukan oleh kecepatan orang lain merespons**: yang sudah menjadwalkan tepat waktu bisa tercatat lalai hanya karena lawannya tak membuka aplikasi. Lawan **diberi tahu, bukan dimintai izin**. Konsekuensi yang diterima: kalender tak tahu apakah lawan bisa hadir, bentroknya baru ketahuan saat harinya tiba, dan diselesaikan lewat percakapan biasa. Akibatnya `POST /events/:id/respond` **tidak dibuat**, status `proposed` dihapus dari `obligation_fulfillments`, dan `EventParticipant.Status` tetap `pending` untuk semua peserta tanpa ada yang membacanya (field-nya dipertahankan hanya karena dokumen lama memuatnya).
- **Belum ada**: booking ruang meeting, pengingat lewat [[Microservices - Notification Service]], kalender di [[APP - MyBharata]], seret untuk menggeser agenda.

### Catatan teknis dan gotcha

- **GOTCHA yang menggigit saat rilis**: gateway MEMBUANG prefix `/api/<module>` (`routes.Reroute` memanggil `strings.TrimPrefix`), jadi `/api/calendar` tiba di service sebagai `/`. Rute agregat sempat didaftarkan di `/calendar` sehingga seluruh permintaan lewat jalur normal membalas 404 `Cannot GET /`, padahal 33 test hijau karena semuanya memanggil path lokal langsung ke Fiber. Diperbaiki di [#1041](https://github.com/bip-itteam-internal/bip-erp/pull/1041) beserta test yang mereproduksi pemotongan prefix itu. **Berlaku untuk service mana pun**: rute akar modul didaftarkan di `/`, bukan `/<module>`.
- **GOTCHA `MONGO_CALENDAR_DB`**: env-nya sempat tidak ada di dev, dan akibatnya bukan kegagalan yang berisik. `mongodb.GetCollection` **memanik** saat DB nil, dan panik di sini tak terlihat sebagai panik: fasthttp memutus koneksi per-permintaan, gateway membalas 502, dan tak ada satu pun petunjuk di respons. Sekarang diturunkan jadi galat biasa lewat penjaga `mongodb.DB == nil`, sehingga kegagalannya muncul sebagai penanda `degraded` yang bisa dibaca orang. Env di container dibaca **saat container dibuat**, jadi menambah env menuntut `--force-recreate`, bukan `restart`.
- **GOTCHA PATCH menimpa penuh** ([#1067](https://github.com/bip-itteam-internal/bip-erp/pull/1067), 2026-08-07): `PATCH /events/:id` semula memakai bentuk yang sama dengan pembuatan, sehingga permintaan tanpa `participants` **menghapus seluruh daftar tamu tanpa satu pun pesan**. Ditemukan lewat kecelakaan pengujian, bukan test yang dirancang, karena seluruh test lama mengirim payload lengkap persis seperti formulir frontend. Sekarang `EventPatch` seluruhnya pointer (nil = jangan sentuh) dan validasinya dijalankan atas **hasil gabungan**, sehingga mengubah hanya `end_at` tetap ditolak bila mendahului `start_at` lama. Pointer dipakai justru agar nilai kosong bisa dibedakan dari tak-disebut.
- **Batas rentang WIB melebar satu hari penuh**, sehingga `to=2026-09-30T23:59:59Z` ikut memunculkan item 1 Oktober. Tidak berbahaya untuk frontend (grid-nya memang mencakup hari luapan), tapi secara kontrak memasukkan item di luar rentang yang diminta. Belum dirapikan.
- **Widget Agenda Mendatang** di dashboard HRIS masih menggabungkan hari libur dan ulang tahun sendiri. Setelah `/api/calendar` hidup, widget itu sebaiknya diarahkan ke sana supaya normalisasinya satu, bukan dua.

### Hasil verifikasi di DEV

- **2026-08-06**, lewat gateway dengan akun nyata: hari libur muncul dengan `all_day` dan lingkup `company`; cuti muncul lengkap dengan subtipe dan membedakan izin berjam dari seharian; `degraded` selalu kosong. Kebenaran tanggal ditriangulasi memakai hari libur yang menyebut tanggalnya sendiri di deskripsi ("diganti di tanggal 16 Februari" → tersimpan `2026-02-15T17:00:00Z` → keluar sebagai `2026-02-16T00:00:00+07:00`).
- **Agenda mandiri**, tiga akun: pembuat 200, peserta 200, orang luar 404. Pembatalan lunak terbukti menyisakan agendanya.
- **PATCH sebagian, 2026-08-07**: PATCH hanya `title` mempertahankan 2 peserta beserta lokasi, catatan, dan waktu; `participants: []` tetap bisa mengosongkan dengan sengaja; `end_at` mundur ditolak 400. Data uji dihapus setelahnya.

## Dependensi & Integrasi

- [[CORE - API Master Gateway]] — rute `/api/calendar/*`, identitas pemanggil, dan `noCacheRoutes`.
- [[Microservices - Attendance Service]] · [[Microservices - Employee Service]] · [[Microservices - Task Management Service]] · [[Microservices - Form Builder Service]] — penyedia feed. **Semuanya opsional**: URL kosong berarti feed-nya dilewati, dan itulah sebabnya URL provider tidak boleh masuk map yang divalidasi `ValidateInternalURL`.
- [[CORE - RBAC dan Permission Set]] — penyaringan item tarikan tetap milik service sumber; kalender tidak menambah lapis izin sendiri, kecuali untuk agenda mandiri yang memang datanya.

## Dokumen Terkait

- [[APP - Web ERP]] — halaman `/calendar`: tampilan **bulan**, **minggu berkolom jam**, dan **daftar agenda**; saringan per jenis yang diingat `localStorage`; formulir buat/sunting agenda; `deep_link` `/calendar?event=<id>` membuka agenda tertentu.
- [[GA - Asset Loan & Room Booking]] — rencana booking ruang yang harus masuk sebagai feed, bukan kalender kedua.
- [[Microservices - Form Builder Service]] — asal pola periode dan papan kepatuhan untuk irisan 3.

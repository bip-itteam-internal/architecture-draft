## Deskripsi

*Kalender terpusat lintas modul. Service ini menarik agenda dari service lain lewat satu kontrak feed yang seragam, menormalkannya jadi satu bentuk, lalu menyajikannya sebagai satu daftar; sejak 2026-08-06 ia juga **memiliki satu jenis agenda sendiri** (`event`), yaitu agenda yang dibuat karyawan langsung dari kalender. Tujuannya agar karyawan punya satu tempat untuk semua yang menyangkut dirinya, dan agar setiap modul baru yang punya tanggal cukup **mendaftarkan feed**, bukan membangun kalender sendiri-sendiri.*

> **Prinsip tiga lapis** (keputusan pemilik produk, 2026-08-06): kalender memuat **data diri sendiri**, **pekerjaan sendiri**, dan **agenda perusahaan**. Data pribadi orang lain **tidak boleh** masuk, sekalipun pemanggilnya seorang supervisor. Prinsip ini yang menutup insiden privasi di bawah, dan ia mengikat semua feed baru.

- **Status**: ⚠️ Implemented (ada catatan) — agregasi + agenda mandiri **live di DEV** dan terverifikasi lewat gateway. **Mesin kewajiban (irisan 3) SUDAH ada di `main`** sejak PR [#1074](https://github.com/bip-itteam-internal/bip-erp/pull/1074) (2026-08-07), tetapi baru separuh: template, periode, dan tagihan berjalan sendiri, sementara **jalur pemakainya belum ada sama sekali** (§ Mesin kewajiban). **PROD tertinggal**: baru sampai irisan 1.
- **Stack**: Go + Fiber + MongoDB (`calendar_db`; koleksi `calendar_events`, `obligation_templates`, `obligation_periods`, `obligation_fulfillments`). Env `MONGO_CALENDAR_DB` **wajib**; tanpa itu service tetap hidup tapi seluruh agenda mandiri membalas 500. `EMPLOYEE_MODULE_URL` dipakai potret peserta kewajiban dan sengaja opsional (kosong = potret tertunda, bukan service mati).
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

**Template kewajiban** (`/api/calendar/obligations/templates`, seluruhnya digerbang `common.RequireHRISSupervisor`):
- `GET /` (opsional `?active=true|false`) · `POST /` · `GET /:id` · `PUT /:id` · `DELETE /:id`.
- Gerbangnya **lebih sempit** daripada gerbang pengelola di [[Microservices - Form Builder Service]], dan itu disengaja: satu template melahirkan kewajiban ber-KPI bagi orang di seluruh perusahaan, jadi membiarkan tiap pengelola departemen membuatnya berarti membiarkan IT menagihi Finance.
- **PUT, bukan PATCH**, dan nama rutenya dibuat jujur sejak awal supaya tak mengulang bug `PATCH /events/:id` yang diam-diam menimpa penuh. Di sini menimpa penuh memang benar: bentuknya dikelola satu formulir yang selalu mengirim seluruh field.
- `DELETE` menghapus **lunak** (`deleted_at` + `active:false`). Laporan kepatuhan bulan lampau menyebut nama templatenya; yang dihapus hilang dari daftar, bukan dari sejarah.
- `company_id` dan `created_by` **diturunkan dari identitas pemanggil**, dan penyaring `company_id` ada di dalam query, bukan diperiksa sesudah dokumennya terbaca.

**Feed yang sudah terdaftar:**

| Service | `kind` | Catatan |
|---|---|---|
| [[Microservices - Attendance Service]] | `holiday` | Hari libur perusahaan, seharian, lingkup `company` |
| [[Microservices - Attendance Service]] | `leave` | Cuti/izin/sakit **milik pemanggil sendiri saja**, berstatus disetujui. Izin berjam tidak dijadikan seharian |
| [[Microservices - Employee Service]] | `contract_end` | Kontrak pemanggil sendiri berakhir. PKWTT dibuang karena `end_date`-nya kosong |
| [[Microservices - Employee Service]] | `movement` | ⚠️ **merged ke `main` 2026-08-10** (PR [#1142](https://github.com/bip-itteam-internal/bip-erp/pull/1142)), belum diverifikasi lewat gateway. Promosi/mutasi pemanggil sendiri, seharian. Catatan `cancelled` tak pernah muncul (orang akan bersiap untuk kepindahan yang batal), `applied` tetap muncul sebab itu peristiwa yang benar-benar terjadi. `company_id` item diambil dari perusahaan **pembaca**, bukan dari dokumen: pemiliknya ada di tenant asal sebelum tanggal efektif dan di tenant tujuan sesudahnya, jadi item yang distempel salah satu sisi tersaring hilang persis di sisi tempat ia berdiri ([[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]) |
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

## Mesin kewajiban (irisan 3) — mesinnya jalan, jalur pemakainya belum

> ⚠️ **Dokumen ini sempat menyatakan "irisan 3 belum ada kode" selama tiga minggu sesudah kodenya merged** (PR [#1074](https://github.com/bip-itteam-internal/bip-erp/pull/1074), 7 Agustus 2026). Klaim itu salah, dan salahnya mahal: ia mengundang orang berikutnya membangun ulang template kewajiban yang sudah berjalan. Yang benar adalah **pondasinya ada, jalur pemakainya belum**, dan dua bagian itu harus dibaca terpisah.

### Yang sudah berjalan

| Bagian | Berkas | Isi |
|---|---|---|
| Template kewajiban | `models_obligation.go` · `obligation_handlers.go` | Pengulangan `monthly`/`weekly`, `quota`, `grace_days`, `active`, hapus lunak |
| Aturan sasaran (`audience`) | `obligation_audience.go` | `all` · `department` · `position` · `employment_type` · `manual` |
| Aturan lawan sesi (`counterpart`) | `models_obligation.go` | `supervisor` · `department` · `position` · `any`, atau `required:false` untuk kewajiban mandiri |
| Penanggalan periode | `obligation_window.go` | `2026-08` bulanan, `2026-W32` mingguan (ISO), plus `missedAt` |
| Cron tiap jam (Asia/Jakarta) | `obligation_cron.go` | Buka periode → potret peserta → terbitkan tagihan → tutup periode → tandai `missed` |
| Simpan periode & tagihan | `obligation_period_store.go` · `db.go` | Idempoten lewat **index unik**, bukan lewat pemeriksaan "sudah ada?" |

Status tagihan: `pending` → `scheduled` → `fulfilled`, atau `missed`. Status `proposed` dari rancangan awal **dihapus** bersama alur terima/tolak.

### Keputusan yang sudah terkunci di kode

Baca ini sebelum menambah apa pun; sebagian besar tak akan tertebak dari bentuk datanya.

- **`audience` adalah ATURAN, bukan daftar orang**, dan dievaluasi ulang tiap periode dibuka. Daftar id membusuk: ia menagih orang yang sudah resign selamanya sekaligus tak pernah menagih karyawan baru.
- **`quota`, `template_name`, dan `grace_days` DIBEKUKAN per periode**, `quota` bahkan per orang. HR boleh mengganti nama kewajiban atau memperpanjang toleransi kapan saja, dan tanpa pembekuan ini perubahan hari ini diam-diam mengubah arti laporan bulan lalu.
- **`missed` DITULIS cron, bukan dihitung saat dibaca.** "Belum" dan "telat" dua hal berbeda, dan yang kedua tak boleh bisa berubah lagi hanya karena laporannya dibuka di hari yang berbeda.
- **Penutupan periode dan penandaan `missed` sengaja dipisah.** Periode tutup di ujung bulan; tagihannya baru terlewat sesudah masa tenggang, yang dihitung dari `closes_at` **bukan** dari tanggal agendanya. Yang ditoleransi adalah keterlambatan mencatat, bukan keterlambatan bertemu.
- **Potret peserta yang gagal tidak menutup periode**, hanya menandai `participants_partial`. Orang tetap bisa menjadwalkan; yang ditahan cuma angka persentase, karena persentase dari penyebut yang salah lebih menyesatkan daripada tak ada angka sama sekali.
- ⛔ **Sasaran `department` mencocokkan `work_data.department` apa adanya** (`cocokSalahSatu`, tak peka huruf besar-kecil, spasi pinggir diabaikan). **Label grup supervisi seperti `HRGA` tak akan cocok dengan siapa pun**, dan hasilnya periode berisi nol peserta tanpa satu pun galat — kelas kegagalan yang sudah menggigit berulang kali di tempat lain. Untuk grup, sebut kedua nama departemen aslinya atau pakai mode `position`. Awas pula spasi di ujung nama posisi yang memang tersimpan begitu di produksi.
- **Nilai kosong tidak pernah cocok dengan kosong.** Karyawan yang departemennya belum diisi tak boleh diam-diam masuk sasaran "departemen tertentu"; karyawan tanpa `employee_id` dibuang karena tak bisa dihitung kepatuhannya maupun dikirimi pengingat.
- **Mode `audience` yang tak dikenal mengembalikan false, bukan true.** Sasaran yang tak terbaca berarti tak ada yang ditagih, jauh lebih baik daripada menagih seluruh perusahaan karena satu salah ketik.
- **Kuota nol ditolak di muka** (minimal 1, maksimal 31): kewajiban yang tak pernah bisa dipenuhi maupun dilanggar membuat papan kepatuhan menampilkan orang yang selamanya hijau tanpa melakukan apa pun. Peserta di atas 1000 juga ditolak, **tidak dipotong diam-diam**.
- **`open_day` bulanan dibatasi 1..28** karena Februari, dan jendelanya **selalu** berakhir di ujung bulan atau minggu. Durasi bebas bisa melewati batas bulan sehingga dua periode hidup bersamaan, dan begitu itu terjadi "periode mana yang aktif" tak punya jawaban yang benar.
- **Cron dinyalakan SESUDAH kunci internal siap** (`main.go`), karena potret pesertanya memanggil employee-service dengan kunci itu. Perusahaan dikirim eksplisit lewat header: `InternalRequest` tanpa `Ctx` membuat employee-service jatuh ke `DefaultCompanyID` dan mengembalikan daftar tenant yang **salah**, yang artinya menagih orang dari tenant lain.
- **`cron.Recover` bukan kehati-hatian berlebihan.** Panik di handler HTTP cuma memutus satu koneksi karena fasthttp menangkapnya, tapi panik di goroutine cron menjatuhkan **seluruh proses**: agregasi kalender ikut mati hanya karena satu template bermasalah.
- **`obligation_window.go` menyalin `services/form-builder/period.go` dengan sengaja.** Keduanya `package main` di service berbeda sehingga tak bisa saling impor; tempat yang benar untuk menyatukannya kelak adalah `shared-library`.

### Yang BELUM ada, dan inilah yang membuat modul ini belum bisa dipakai siapa pun

1. ⛔ **Tak ada satu pun rute untuk karyawan yang wajib.** Rute yang terdaftar di `routes.go` hanya CRUD template. Tak ada "kewajiban saya", tak ada cara menautkan agenda ke tagihan, tak ada cara menandai sesi selesai. `event_ids`, `counterpart_id`, `completed_count`, `completed_at`, dan `completed_by` ada di model tapi **tak pernah ditulis dari mana pun**. Akibatnya konkret: **bila HR membuat template hari ini, cron menerbitkan tagihan lalu menandai SEMUA orang `missed`** begitu masa tenggangnya habis, karena tak ada jalan untuk memenuhinya. Ini bukan fitur yang kurang, ini modul yang akan menghukum semua orang bila dinyalakan apa adanya.
2. **Papan kepatuhan belum ada.** Index-nya sudah disiapkan (`db.go`, "Papan kepatuhan per periode" dan "Kewajiban saya, diurutkan menurut tenggat"), handler-nya belum ditulis.
3. **Tagihan tak muncul di kalender.** `GET /` hanya menggabungkan provider luar; belum ada `kind: obligation` untuk data milik service ini sendiri. Satu-satunya jejak `obligation` di [[APP - Web ERP]] adalah test gaya untuk `kind` tak dikenal, bukan fitur.
4. **Belum ada rute internal ber-kunci-layanan untuk KPI** (§ berikutnya).
5. **Belum ada frontend sama sekali** — tak ada halaman kelola template untuk HR maupun kartu kewajiban untuk karyawan.

**Uji yang sudah ada**: `obligation_template_test.go`, `obligation_audience_test.go`, `obligation_window_test.go`, `obligation_cron_test.go`. Seluruhnya menguji fungsi murni dan validasi. **Belum ada satu pun test yang melewati Fiber** untuk rute template, jadi kelas cacat glue handler yang sudah menggigit service lain belum tergerbang di sini.

### Jalan menuju metrik KPI "Monitoring Kegiatan Sinkronisasi/Review"

Modul ini adalah rumah yang sudah ditetapkan untuk metrik Fullstack `Implementasi` (bobot 0,2, deskripsi "Monitoring Implementasi Sinkronisasi/Review dengan Requester") di [[HRIS - Matriks KPI per Departemen]], dan untuk 9 metrik log 1-on-1 di [[HRIS - Otomasi Skor KPI]] butir 12 yang sejalan dengan [[HRIS - Work Review]]. Yang masih memisahkan keduanya, berurut:

1. **Rute pemakai di service ini** (celah 1 di atas), termasuk penegakan aturan `counterpart` **di server**, bukan sekadar menyaring dropdown.
2. **Rute internal di sini yang menggerbangi dirinya dengan kunci layanan SENDIRI**, bukan bersandar `INTERNAL_GATEWAY_KEY`: gateway memasang header itu untuk setiap permintaan yang lolos JWT, sehingga rute yang bersandar padanya terbuka bagi seluruh karyawan yang sudah login ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Kunci yang belum dikonfigurasi harus **menutup** rute, bukan membukanya.
3. **Sumber KPI baru di [[Microservices - Employee Service]]**. Per 2026-08-31, tak satu pun dari 56 berkas `kpi_sumber_*.go` membaca kewajiban kalender, dan `CALENDAR_MODULE_URL` hanya dipakai gateway. URL-nya **dibaca langsung dari env**, jangan dimasukkan ke map yang divalidasi `ValidateInternalURL` — penjaga itu memanggil panic saat kosong, sehingga satu env yang belum dipasang mematikan seluruh employee-service demi satu metrik KPI. Prosedurnya di [[RUN - Menambah Metrik KPI Otomatis]].

⚠️ **Dua hal yang harus diputuskan orang, bukan kode:**

- **Siapa yang menandai sesi selesai.** Bila yang dinilai menandai sendiri, sebagian kemudi KPI berada di tangan yang dinilai. Tapi meminta konfirmasi lawan bertabrakan langsung dengan keputusan 7 Agustus 2026 bahwa undangan **memberi tahu, bukan meminta izin** — keputusan yang justru dibuat supaya kepatuhan seseorang tidak ditentukan kecepatan orang lain merespons.
- **Mode `counterpart` untuk metrik itu.** "Requester" adalah pemohon tiket yang bisa berada di departemen mana pun, jadi yang muat hanya `any`. Tetapi `any` membuat kepatuhan mudah dikadali, karena orang tinggal memilih rekan yang pasti bersedia.

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
- **Irisan 3, sesi wajib — SEBAGIAN sudah ada, rinciannya di § Mesin kewajiban.** Template, periode, potret peserta, dan penerbitan tagihan berjalan sejak PR [#1074](https://github.com/bip-itteam-internal/bip-erp/pull/1074) (2026-08-07); polanya menyalin `FormPeriod` di [[Microservices - Form Builder Service]] yang sudah terbukti di produksi. Yang **belum** ada: rute pemakai, papan kepatuhan, feed `obligation`, rute internal KPI, dan frontend. Yang tetap berlaku sebagai rancangan: yang wajib memilih sendiri lawan sesinya dari kandidat yang lolos aturan `counterpart` per-template, ditegakkan **di server** bukan sekadar dipakai menyaring dropdown; dan menjadwalkan **tidak** langsung memenuhi kewajiban, pertemuannya tetap harus ditandai selesai supaya angka kepatuhan mengukur kenyataan, bukan niat.
- **Belum diverifikasi: apakah biner kewajiban sudah naik ke DEV maupun PROD.** Kodenya ada di `main`, tetapi kehadirannya di container yang berjalan belum diukur — TBD. Sensus produksi 2026-08-28 mencatat **0 template, 0 periode, 0 pemenuhan**, dan angka nol itu belum dapat dibedakan antara "belum ada yang membuat template" dan "binernya memang belum di sana".
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

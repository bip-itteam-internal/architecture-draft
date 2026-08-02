## Deskripsi

*Form Builder Service adalah pembuat form dinamis tanpa coding: sebuah departemen menyusun form sendiri (9 tipe pertanyaan), menerbitkannya ke sasaran tertentu, membaca rekap jawabannya, dan mengekspornya ke CSV — tanpa rilis kode untuk tiap form baru. Sejak PR #907 form juga bisa **menilai karyawan lain**: satu form dipakai berulang untuk banyak orang tanpa pengisinya mengulang dari awal. Service ini juga menyediakan satu endpoint kepatuhan yang dipakai [[Microservices - Attendance Service]] untuk menahan clock-in mobile bila ada form wajib yang belum diisi.*

- **Stack:** Go + Fiber v2 + MongoDB (database sendiri `form_builder_db`)
- **Path:** `services/form-builder`
- **Port:** 6986 (internal, `expose`; tidak dipublish ke host)
- **Status**: ⚠️ **Implemented & LIVE di dev DAN prod** (PR [#849](https://github.com/bip-itteam-internal/bip-erp/pull/849) + perbaikan [#855](https://github.com/bip-itteam-internal/bip-erp/pull/855)); prod naik 2026-08-01 dengan kepemilikan per departemen, bagian, dan keterangan ujung skala (PR [#869](https://github.com/bip-itteam-internal/bip-erp/pull/869), [#870](https://github.com/bip-itteam-internal/bip-erp/pull/870), [#871](https://github.com/bip-itteam-internal/bip-erp/pull/871)). FE web di [[APP - Web ERP]] sudah lengkap (kelola, builder, **analisa jawaban**) dan ikut ter-deploy; pengisian di [[APP - MyBharata]] sudah ada (section Survei di beranda + halaman isi berbagian). **Yang diverifikasi saat deploy hanya health `200` lewat gateway + backfill data lama**; alur buat→terbit→isi→analisa **belum diuji ulang** pada versi baru ini, baik di dev maupun prod.
- **Penilaian karyawan lain + tipe form**: PR [#907](https://github.com/bip-itteam-internal/bip-erp/pull/907) **merged & LIVE di dev 2026-08-02** (log boot mencatat `8 form lama ditandai form_type="survey"`, handler jadi 31). Rekap per orang & tingkat penyelesaian: PR [#908](https://github.com/bip-itteam-internal/bip-erp/pull/908) **merged 2026-08-02**. ✅ **PROD naik 2026-08-02** (log boot: `2 form lama ditandai form_type="survey"`, handler 31, health lewat gateway `200`). ⚠️ Alur penilaian **belum diuji end-to-end** di lingkungan mana pun — yang terverifikasi baru boot service dan backfill.

> [!warning] `notification-service` WAJIB ikut di-deploy, bukan hanya form-builder
> Kategori inbox `form-published` dan `form-submitted` lahir di `shared-library`, dan notification-service **memvalidasi kategori terhadap daftar itu** (`IsInboxCategoryValid` → `400` bila di luar daftar). Selama containernya masih memakai kode lama, seluruh notifikasi Form Builder **ditolak dan hilang tanpa jejak** sementara form-builder tampak berjalan normal — kegagalannya best-effort dan hanya muncul di log. Keduanya di-rebuild bersama saat deploy prod 2026-08-02.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Staf/SPV IT | Tech Development | Peran staff/supervisor/admin + departemen `Tech Development` aktif | Web |
| Staf/SPV HRGA | Human Resource · General Affair | Idem; SPV HRGA membawahi keduanya lewat `supervised_by` | Web |
| Karyawan | Semua divisi | Terautentikasi (tanpa syarat peran) | Mobile (MyBharata), Web |

- **Tujuan** — pemilik form: membuat form ad-hoc (survei, deklarasi, pendataan) tanpa menunggu rilis kode, lalu membaca hasilnya. Karyawan: mengisi form yang ditujukan kepadanya.
- **Pain point** — sebelum ini setiap form baru berarti satu siklus development; permintaan pendataan mendadak tak terlayani.
- **Aksi utama** — pemilik form: susun pertanyaan → tentukan sasaran → terbitkan → baca analisa/export. Karyawan: buka daftar form → isi → kirim.

> Peran `security` milik GA (satpam) **sengaja dikecualikan** dari pengelola form: tingkat perannya bukan staff/supervisor/admin, jadi tak pernah lolos gerbang.

## Endpoint / Fitur (Sudah Diimplementasikan)

Prefix gateway `/api/form-builder/*`. Kontrak lengkap: [[API - Form Builder Service]].

**Kelola form** (gerbang `requireFormManager`: tingkat peran pengelola + departemen aktif)
- `POST /forms` · `GET /forms` — buat & daftar form. Daftar **hanya menampilkan form milik departemen dalam cakupan pemanggil**, jadi tim GA tak melihat form IT.
- `GET /forms/:id` · `PATCH /forms/:id` · `DELETE /forms/:id` — detail, sunting, hapus lunak (`deleted_at`).
- `PATCH /forms/:id/status` — `draft` → `published` → `closed`. Form terbit **tidak bisa mundur** ke draft.
- `owner_department` tak bisa dipindah setelah dibuat (memindahkannya akan membuat form lenyap dari daftar pemiliknya sendiri).
- `GET /me/capability` — `{can_manage, departments[]}` untuk klien, supaya daftar departemen aktif tak perlu disalin ke FE.
- **Susunan pertanyaan terkunci begitu ada jawaban masuk** (balas `409`). Menyunting field setelah orang menjawab membuat jawaban lama menunjuk pertanyaan yang sudah berubah arti, dan analisanya diam-diam jadi salah.

**Tipe pertanyaan (9)** — `short_text`, `long_text`, `number`, `date`, `time`, `dropdown`, `radio`, `checkbox`, `scale`. Validasi struktur (key unik, options wajib untuk tipe pilihan, rentang scale maksimal 10 langkah, `min ≤ max`) dan validasi jawaban (tipe cocok, nilai ∈ options, batas angka & panjang teks, format `YYYY-MM-DD` dan `HH:MM`) keduanya **fungsi murni** — teruji tanpa Mongo.

**Tipe form (4)** — `survey`, `evaluation`, `request`, `checklist`. Bukan sekadar label: tanpanya daftar form berisi survei, pengajuan, checklist, dan penilaian yang tampak serupa padahal cara mengisinya berbeda jauh. `GET /forms?form_type=` menyaringnya; nilai `survey` sengaja ikut menjaring dokumen yang field-nya belum ada, karena backfill baru mengisinya saat boot. Kiriman tanpa `form_type` diberi default `survey` (klien lama belum mengirimnya), tapi nilai **tak dikenal diteruskan apa adanya** supaya validasi menolaknya dengan pesan jelas alih-alih diam-diam berubah jadi survei.

**Bagian (`section`)** — penanda pemisah halaman, bukan pertanyaan. Lihat bagian tersendiri di bawah.

**Hitungan jawaban di daftar form** — tiap item membawa `response_count` (jumlah jawaban) dan `respondent_count` (jumlah ORANG). Dibedakan karena pada form penilaian keduanya berbeda jauh: 185 karyawan menilai 4 office boy menghasilkan 740 jawaban, dan menjawab "sudah berapa yang mengisi" dengan 740 terbaca seolah empat kali lipat karyawan perusahaan sudah mengisi. Keduanya **diturunkan** saat menyusun daftar (`bson:"-"`), tak pernah disimpan, lewat **satu agregasi** untuk seluruh halaman.

**Keterangan ujung skala** (`scale_min_label`/`scale_max_label`, maks 40 karakter, opsional) — tanpa itu pengisi harus menebak apakah angka terkecil berarti terbaik atau terburuk, dan tebakan yang salah membuat **seluruh jawaban skala terbalik artinya sementara analisanya tetap tampak masuk akal**. Hanya berlaku untuk tipe `scale`; menempel di tipe lain ditolak karena pasti sisa perpindahan tipe.

**Sasaran form (audience)** — `all`, `departments`, atau `employees`. Diresolusi dari **header identitas yang sudah dibawa gateway** (`BIP-Employee-ID`, `BIP-Department`), sehingga jalur pengisian **tak memanggil satu service pun**. Tipe sasaran yang tak dikenal **gagal-tertutup** (tidak cocok), supaya salah ketik tak pernah menahan presensi sekantor.

**Sasaran penilaian (subject)** — siapa yang DINILAI, sumbu terpisah dari `audience`. Lihat bagian tersendiri di bawah.

**Pengisian** (cukup karyawan terautentikasi)
- `GET /me/forms` — form terbit yang ditujukan ke pemanggil, lengkap dengan penanda `submitted` dan `blocks_attendance`. Untuk form penilaian ikut membawa `subject_enabled`, `subject_total`, `subject_done`, `subject_anonymous`; `submitted` baru bernilai `true` setelah **seluruh** sasaran dinilai, bukan setelah orang pertama.
- `GET /me/forms/:id/subjects` — daftar orang yang harus dinilai pemanggil, beserta mana yang sudah selesai. Dibaca dari potret di dokumen form, jadi jalur ini **tak menyentuh employee-service sama sekali**.
- `POST /me/forms/:id/responses` — kirim jawaban. Form non-`published` ditolak, dan bukan-sasaran ditolak `403`.
- `GET /me/responses` — riwayat jawaban sendiri.
- **Idempoten**: pengiriman identik dalam 2 menit dianggap retry dan dibalas sukses tanpa insert baru. Sidiknya di-hash dari jawaban yang **kuncinya diurutkan lebih dulu**, jadi klien yang menyusun ulang payload saat retry tetap terdeteksi. Pola sejenis dipakai leave request di [[Microservices - Attendance Service]].
- `settings.single_response` membatasi satu jawaban per karyawan (balas `409`).

**Analisa & export**
- `GET /forms/:id/analytics` — hitungan per opsi (**termasuk opsi ber-nol, urut sesuai definisi form** supaya grafik tak berganti susunan tiap data bertambah), rata-rata/min/maks untuk `number` & `scale`, cuplikan 5 jawaban teks terbaru, `answered`/`skipped` per pertanyaan, tren harian, dan tingkat pengisian.
- `GET /forms/:id/responses` — daftar jawaban berhalaman.
- `GET /forms/:id/export` — CSV; satu pertanyaan = satu kolom secara konsisten, checkbox digabung `"; "` dalam satu sel, angka tanpa nol berlebih.

**Kepatuhan presensi**
- `GET /internal/compliance` — dipakai attendance-service saat clock-in. Membalas `blocking` (mode `block`) dan `warning` (mode `warn`).

## Kepemilikan form: departemen, bukan modul

Sampai PR #869, pemilik form adalah key `system_roles` (`it`/`ga`). Itu **salah sumbu**: `system_roles` adalah hak akses modul/menu, bukan hierarki organisasi (lihat [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]). Akibatnya orang yang kebetulan punya peran di dua modul melihat form dua tim sekaligus — SPV HRD sempat melihat form IT di daftarnya.

Sekarang:

- **Pemilik** = `owner_department`, nilai `master_department` (mis. `"General Affair"`).
- **Cakupan** = `common.SupervisedDepartments` (departemen sendiri + yang dibawahi lewat `master_department.supervised_by`) **diiris** daftar departemen aktif. Pola yang sama sudah dipakai `services/recruitment/rbac.go`.
- **Departemen aktif** = env `FORM_BUILDER_DEPARTMENTS` (dipisah koma). Bila kosong dipakai bawaan `Human Resource, General Affair, Tech Development`. Defaultnya sengaja ada: daftar kosong berarti tak seorang pun bisa membuka Form Builder, jadi env yang lupa diisi akan mematikan fitur tanpa pesan galat yang menjelaskan sebabnya.
- **Tingkat peran** tetap `staff`/`supervisor`/`admin` di modul mana pun. Key `group` **dikecualikan** — itu penanda jangkauan lintas-perusahaan (`common.IsCentralAdmin`), bukan modul; tanpa pengecualian ini setiap admin grup jadi pengelola Form Builder.

Hasilnya "HRGA" tak pernah jadi nilai tersimpan di mana pun: ia gabungan dua departemen yang muncul sendiri dari master data, persis seperti di [[HRIS - Organization Structure]].

> [!warning] Dua jebakan yang sudah ditutup, keduanya diam-diam
> **Kanonikalisasi ejaan.** Penyaringan daftar memakai `$in` Mongo yang PEKA HURUF. Kiriman `"tech development"` lolos pemeriksaan akses (yang tak sensitif huruf) lalu tersimpan apa adanya — formnya berhasil dibuat dan **langsung lenyap dari daftar pembuatnya sendiri**. Karena itu `owner_department` dikanonikkan ke ejaan daftar aktif saat menulis.
>
> **Backfill saat boot, bukan skrip manual.** Begitu versi ini naik, form yang masih menyimpan `owner_module` tak cocok filter mana pun: hilang dari daftar dan menolak dibuka dengan `403`. Dev deploy-nya otomatis dari `main`, jadi jedanya tak bisa dijadwalkan. Pemindahan dijalankan idempoten saat boot (`it`→`Tech Development`, `ga`→`General Affair`), bersama pembuatan index.

**Siapa yang berubah aksesnya**: staf HR (`hris:staff`) yang dulu terkunci kini bisa membangun form; pemegang peran `it`/`ga` yang departemennya di luar daftar aktif kehilangan akses; karyawan tanpa `department` di `work_data` kini tertutup (fail-closed, disengaja untuk perubahan kontrol akses). Token berlaku 72 jam, jadi SPV HRGA yang belum login ulang sementara hanya melihat departemennya sendiri — fallback `SupervisedDepartments` menanganinya tanpa error.

## Penilaian karyawan lain: sumbu `subject`, terpisah dari `audience`

Kasus nyata yang jadi acuan: **seluruh karyawan menilai tiap Office Boy, satu per satu**. Di produksi itu 185 karyawan × 4 Office Boy = **740 penilaian**, dan tiap orang mengisi 4 kali dalam satu duduk.

Dua sumbu yang berbeda dan sengaja tidak digabung:

| Sumbu | Menjawab | Nilai |
|---|---|---|
| `audience` (lama) | siapa yang **MENGISI** | `all` · `departments` · `employees` |
| `subject` (baru) | siapa yang **DINILAI** | aturan `departments` · `positions` · `employees` |

Skenario OB jadi `audience: all` + `subject.rules: [positions]` dengan `positions: ["Office Boy"]`. Aturan digabung sebagai **OR** — "semua OB ditambah seluruh tim Security" permintaan wajar, sedangkan "OB yang sekaligus Security" tak pernah ada.

**Form tanpa `subject` berperilaku persis seperti sebelumnya**, jadi tak satu pun form lama perlu dimigrasi.

**Tipe `evaluation` terikat DUA ARAH dengan `subject`**: tipe penilaian wajib punya sasaran, dan yang punya sasaran wajib bertipe penilaian. Tanpa ikatan itu keduanya jadi dua saklar terpisah yang bisa bertentangan, dan hasilnya form yang tampak benar di editor tapi berperilaku lain di tangan pengisi — form "Penilaian Karyawan" yang dibuka lalu tak menemukan seorang pun untuk dinilai.

### Potret sasaran diambil sekali saat terbit

`subject.resolved` membekukan daftar orang **tepat saat form diterbitkan**, dan itu bukan cache demi kecepatan semata. Orang pindah jabatan dan karyawan baru masuk kapan saja; daftar yang bergeser di tengah periode membuat sebagian penilai mendapat orang yang tak pernah dilihat penilai lain, lalu angkanya dibandingkan seolah setara.

Efek sampingnya seluruh jalur pengisian **tak menyentuh employee-service sama sekali** — service itu hanya dipanggil pada saat menerbitkan.

Gagal memotret **menggagalkan penerbitan** (`422`), berbeda dari notifikasi yang cuma di-log: form berpenilaian tanpa daftar sasaran tampak normal bagi pengelolanya sementara tak seorang pun pengisi melihat siapa yang harus dinilai. Batasnya **300 orang**, ditolak di muka dan tidak dipotong diam-diam.

### Aturan relasional sengaja belum ada

Atasan langsung, bawahan, dan sejawat satu atasan **tidak ditawarkan**. Penentunya `supervisor_id` di `work_data`, yang lapangan menunjukkan baru terisi pada segelintir karyawan (lihat [[HRIS - Organization Structure]]). Aturan yang diam-diam menghasilkan daftar kosong lebih buruk daripada aturan yang belum ada.

### Kunci keunikan bergeser

Dari (form, pengisi) jadi **(form, pengisi, yang dinilai)**. Tanpa itu `single_response` menghentikan pengisi tepat setelah sasaran pertama dan sisa daftarnya mustahil diselesaikan. Guard idempotensi ikut memakai `subject_employee_id`: dua penilaian berturut-turut atas orang **berbeda** bisa punya jawaban yang persis sama (lima bintang untuk semuanya), dan tanpa pembeda itu yang kedua dibuang sebagai retry.

`subject_employee_id` dari klien **tidak dipercaya** dan dicocokkan ulang ke potret; tanpa itu siapa pun bisa mengirim penilaian atas orang yang tak pernah ada di daftarnya.

> [!warning] Jebakan yang ikut ditutup: field yang hilang ≠ string kosong
> Jawaban yang tersimpan **sebelum** fitur ini tak punya `subject_employee_id` sama sekali (`omitempty`), dan di Mongo `{field: ""}` **tidak cocok** dengan dokumen yang field-nya hilang. Tanpa `subjectQuery` (yang memakai `$in: ["", null]`), `single_response` dan guard idempotensi diam-diam berhenti bekerja pada **seluruh form lama**: form sekali-isi bisa diisi ulang, dan retry jaringan mulai melahirkan jawaban ganda.

### Gerbang presensi DILARANG pada form penilaian

Keputusan sadar. Gerbang menahan orang masuk kerja; form penilaian menuntut **seluruh** sasaran dinilai lebih dulu. Pada kasus OB itu berarti menahan 185 orang di depan pintu sampai masing-masing menyelesaikan 4 penilaian. Larangan ini sekaligus menjaga jalur clock-in tetap murah: tanpanya tiap clock-in harus menghitung kelengkapan penilaian per orang.

### Kerahasiaan penilai: saklar per form

`subject.anonymous`, default mati. Identitas penilai **tetap tersimpan** supaya satu orang tak bisa menilai dua kali dan jejaknya tetap bisa diaudit, tapi dikosongkan di export CSV dan daftar jawaban. Yang **dinilai** tetap utuh, karena itulah gunanya laporan ini dibaca. Kolomnya dikosongkan, bukan dihapus, supaya bentuk file CSV tak berubah dan template lama tak patah.

Disetel per form karena bobotnya beda jauh: survei fasilitas kantor tak butuh kerahasiaan, penilaian sejawat oleh 184 orang justru tak ada artinya tanpa itu.

### Rekap per orang & tingkat penyelesaian (PR #908)

`GET /forms/:id/analytics` bertambah `evaluation`, `subjects`, dan `subjects_truncated` — semuanya absen pada form biasa.

**Tingkat penyelesaian memakai penyebut yang berbeda.** Angka bawaan menghitung siapa saja yang mengirim minimal satu penilaian, jadi pada sasaran 4 orang seseorang yang baru menilai satu sudah terhitung penuh dan angkanya menyentuh 100% jauh sebelum pekerjaannya selesai. Yang dilaporkan sekarang adalah penilai yang menyelesaikan **seluruh** daftarnya, diperiksa **per penilai terhadap daftar miliknya sendiri** — jumlah sasaran tiap orang bisa berbeda satu, karena yang namanya ikut di daftar tidak menilai dirinya sendiri kecuali `allow_self` menyala.

**Rekap per orang bertumpu pada potret, bukan pada jawaban yang masuk.** Orang yang belum dinilai siapa pun tetap muncul dengan angka nol; kalau disusun dari jawaban saja, orang yang paling terlewat justru lenyap dari laporan padahal dialah yang paling perlu ditindaklanjuti. Rata-rata hanya untuk pertanyaan `number` dan `scale` — merata-ratakan pilihan atau teks tak punya arti, dan mencampur skala 1..5 dengan 1..10 justru menyesatkan. Rata-rata memakai pointer, bukan 0: "belum ada yang menilai" dan "dinilai nol" berjauhan artinya.

## Notifikasi inbox

Saat form **terbit**, seluruh sasaran diberi tahu lewat [[Microservices - Notification Service]] (`POST /inbox/send`), dan jumlah orang yang menunggu dinilai disebut di muka supaya penerima bisa memilih waktu yang cukup. Daftar penerima disusun **sinkron** (butuh header perusahaan dari Ctx hidup), pengirimannya **asinkron**: 185 kiriman inbox berurutan tak boleh menyandera tombol terbit.

Saat pengisian **selesai**, konfirmasi dikirim **sekali** ketika seluruh sasaran rampung, bukan tiap satu orang dinilai. Empat notifikasi berturut-turut hanya melatih orang mengabaikan inbox-nya.

Kategori `form-published` dan `form-submitted` didaftarkan di `shared-library/models/notification`; notification-service menolak `400` kategori di luar daftar itu, jadi tanpa entri itu notifnya hilang tanpa jejak.

## Bagian (section): penanda di daftar datar, bukan struktur bersarang

Form panjang bisa dipecah jadi beberapa halaman saat diisi. Bagian disimpan sebagai **item bertipe `section` di dalam `fields` yang tetap datar** — `label` jadi judulnya, `description` jadi keterangannya, jadi tak ada penambahan skema.

Tiga bentuk dipertimbangkan; yang dipilih paling murah justru karena bentuk datanya tak berubah:

| Bentuk | Konsekuensi |
|---|---|
| `Form.Sections[]` bersarang berisi `fields[]` | Paling rapi secara konsep, tapi SEMUA pengulang `form.Fields` ikut berubah: validasi, analitik, export, renderer web, renderer mobile. Plus migrasi seluruh form lama |
| `section_index` di tiap field + daftar judul terpisah | Dua sumber kebenaran yang bisa tak sinkron; menggeser urutan jadi rawan |
| **Penanda di daftar datar** ✅ | Reorder, validasi, analitik, dan export cukup MELEWATI penanda. **Tak ada migrasi** |

Penjagaan yang dipasang:

- **Bagian tak bisa diwajibkan.** Kontradiksi: tak ada yang bisa diisi di sana, jadi form-nya jadi mustahil dikirim.
- **Bagian menolak `options`, rentang scale, batas panjang, dan batas angka.** Atribut yang menempel padanya pasti sisa perpindahan tipe, dan membiarkannya lolos berarti menyimpan aturan yang tak pernah dijalankan siapa pun.
- **Jawaban yang menunjuk key bagian ditolak** (`400`). Nilainya tak akan pernah muncul di analisa maupun export, jadi diam-diam hilang.
- **Analisa dan export memakai `questionFields()`**, supaya bagian tak jadi kolom CSV yang selalu kosong maupun kartu analisa hampa.

Bagian tetap wajib punya key unik dan judul, mengikuti aturan field lain. Form yang sudah punya jawaban tetap terkunci (`409`), jadi bagian tak bisa ditambahkan ke form berjalan.

**Pemecahan halamannya terjadi di klien**, bukan di bentuk datanya: [[APP - MyBharata]] memakai `splitSurveyPages()` untuk memecah daftar datar jadi halaman. Form tanpa bagian menghasilkan tepat satu halaman, sehingga perilaku lamanya tak berubah.

## Keputusan yang menjaga presensi tetap hidup

Fitur ini menyentuh jalur clock-in, jadi beberapa keputusan sengaja konservatif:

- **Gerbang gagal-tertutup pada data cacat.** Gerbang tanpa jendela tanggal lengkap dianggap **tidak aktif** (gerbang tanpa tanggal berakhir berarti presensi tertahan selamanya bila form-nya dilupakan). Mode enum yang tak dikenal **turun kelas jadi peringatan**, bukan penahan.
- **`mode` default `warn`** saat form dibuat. Menahan presensi harus jadi pilihan yang ditulis eksplisit.
- **Jendela tanggal wajib** saat gerbang menyala.
- **Identitas `/internal/compliance` terkunci ke header.** Query param hanya dihormati bila **tak ada** identitas header sama sekali (ciri panggilan service-to-service). Tanpa aturan ini, karyawan mana pun bisa mengirim `?employee_id=<orang-lain>&company_id=<perusahaan-lain>` dan mengintip form tertunda milik orang lain menembus batas tenant — persis kelas bug di [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]. Header aman dijadikan sandaran karena gateway membuang seluruh namespace `BIP-*` kiriman klien lalu mengisinya dari klaim JWT.

## Multi-perusahaan (tenant)

Ter-scope `company_id` **sejak awal**, bukan ditambal belakangan: stempel `common.CompanyID` saat menulis, `common.EffectiveCompanyID` saat membaca (override `?company=` hanya untuk admin pusat). Lihat [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]].

## Belum Diimplementasikan / Catatan

- ✅ **LIVE di dev sejak 2026-08-01.** `form-builder-service` + `form-builder-mongo-db` dijalankan dan `api-gateway` dibangun ulang; `GET /health?check=form-builder` balas `200`. Terverifikasi end-to-end lewat gateway: buat → terbit → isi → analisa → export → hapus.
- ✅ **PROD JALAN sejak 2026-08-01**: `form-builder-service` + `form-builder-mongo-db` sehat, `GET /health?check=form-builder` lewat gateway balas `200`. Di-deploy manual (`docker compose build form-builder-service task-management-service` lalu `up -d --no-deps`); prod **tidak** auto-deploy.
- ⚠️ **`FORM_BUILDER_DEPARTMENTS` belum diisi di `.env` prod**, jadi compose memunculkan peringatan "variable is not set" dan service memakai daftar bawaannya. Itu perilaku yang dirancang dan nilainya benar; mengisi env hanya menghilangkan peringatannya.

> [!warning] Backfill menyelamatkan data yang dokumen ini sempat bilang tak ada
> Catatan sebelumnya menyatakan prod belum punya data Form Builder. **Itu keliru**: container sudah dinaikkan lebih dulu dan sudah ada 1 form di sana. Log boot saat deploy mencatat:
>
> `[Form-Builder] 1 form dipindah dari owner_module="it" ke owner_department="Tech Development"`
>
> Kalau pemindahan dijalankan sebagai skrip manual seperti rencana awal, form itu akan lenyap dari daftar pemiliknya dan menolak dibuka dengan `403` sampai ada yang menyadarinya. Pelajarannya: **migrasi yang menempel di boot service lebih aman daripada yang menempel di ingatan orang**, terutama saat catatan tentang isi database bisa saja sudah basi.
- ⚠️ **attendance-service masih pra-merge di dev dan prod**, jadi gerbang presensi belum aktif di mana pun. Itu aman selama belum ada form ber-mode `block`.
- ✅ **`.env` dev dan prod SUDAH diisi (2026-08-01)**: `FORM_BUILDER_SERVICE_PORT=6986` + `MONGO_FORM_BUILDER_DB=form_builder_db`. Diverifikasi lewat `docker compose config` di kedua server — `FORM_BUILDER_MODULE_URL` merender `http://form-builder-service:6986` di blok gateway maupun attendance. Backup disimpan (`~/apps/bip-erp/.env.bak-*`). Port 6986 bebas di keduanya.
- ⚠️ **Kenapa dua variabel itu wajib ada SEBELUM gateway di-redeploy.** Berbeda dari attendance (yang sengaja menaruh URL form-builder DI LUAR map tervalidasi), gateway memasukkan `form-builder` ke `InternalURL` dan menjalankan `validation.ValidateInternalURL` — nilai kosong berarti **gateway panic saat boot dan SELURUH ERP ikut mati**. `docker-compose.yml` meredam ini karena nilainya dirakit dari string literal (`http://form-builder-service:${...}`) sehingga tak pernah benar-benar kosong, tapi variabel port yang hilang tetap menghasilkan URL rusak dan semua `/api/form-builder/*` gagal. Deploy gateway HARUS memakai compose yang ikut ter-merge, bukan env lama.
- **Konsumen**: [[APP - Web ERP]] memakai seluruh rute `/forms*` **termasuk** `analytics`, `responses`, dan `export` (halaman analisa, erp-frontend PR #683).
- ✅ **Pengisian (`/me/*`) sudah punya konsumen**: [[APP - MyBharata]] (my-bharata PR #93, merged) — section Survei di beranda + halaman isi 9 tipe. Web sengaja tetap tak menyediakan halaman isi form.
- ⚠️ **Gerbang mode `block` tetap belum boleh dinyalakan di produksi.** Alasannya kini tinggal satu: **attendance-service masih pra-merge**, jadi ia belum memanggil `/internal/compliance` sama sekali. Menyalakan `block` hanya akan memasang penanda yang tak ditegakkan siapa pun — dan begitu attendance naik, ia langsung menahan clock-in tanpa masa transisi. Lihat [[IT - Form Builder]].
- ⚠️ **`FORM_BUILDER_DEPARTMENTS` belum diisi di `.env` mana pun** — tak masalah, bawaannya sudah benar. Isi hanya bila daftarnya mau berbeda.

> [!warning] Gotcha yang sudah menggigit: BSON tak sama dengan JSON
> **PR #855, ditemukan di dev 2026-08-01.** Pertanyaan checkbox melaporkan SEMUA opsi bernilai nol dan kolom CSV-nya keluar sebagai `[Tidak ada]` lengkap dengan kurung siku, padahal datanya tersimpan benar di Mongo.
>
> Sebabnya driver Mongo men-decode array BSON menjadi **`primitive.A`**, yaitu tipe **BERNAMA** (`type A []interface{}`). Type switch `case []interface{}:` **tidak cocok dengan tipe bernama**, jadi setiap nilai yang dibaca **kembali** dari database gagal dikenali sebagai daftar lalu jatuh ke `fmt.Sprintf("%v")`. Jalur TULIS aman karena nilainya masih dari JSON — itulah kenapa validasi saat submit tak pernah menolak apa pun dan bug ini lolos sampai dev.
>
> Perbaikannya memakai **reflection** (`reflect.Kind() == Slice`), bukan mendaftar tipe satu per satu, supaya bentuk lain ikut tertangani.
>
> **Pelajaran yang berlaku untuk service mana pun di repo ini:** 122 unit test service ini semuanya hijau saat bug ini hidup, karena setiap fixture dirakit tangan sebagai `[]interface{}` dan tak satu pun melewati BSON. Uji dengan data buatan sendiri **tidak** menguji lapisan decode database. Regresinya dikunci di `bson_values_test.go` memakai `primitive.A` asli.
- **Upload file** belum didukung (menyusul via [[Microservices - File Service]], cap 4 MB).
- **Logika percabangan** (lompat seksi berdasarkan jawaban) belum ada.
- **Jumlah PENGISI tidak dihitung otomatis.** Untuk `audience` bertipe `all`/`departments`, penyebut tingkat pengisian tetap memakai `audience.estimated_size` yang diisi manual pembuat form. Bila kosong, tingkat pengisian **tidak dilaporkan** (menampilkan 0% lebih menyesatkan daripada tak menampilkan apa pun). Berbeda dari `subject`, yang JUSTRU di-resolve otomatis dari employee-service saat terbit — sumbu yang dinilai butuh nama dan jabatan, sedangkan sumbu pengisi cukup dicocokkan dari header.
- **Agregasi dibatasi 20.000 jawaban.** Bila terlampaui, total sebenarnya tetap dilaporkan dan hasil ditandai `truncated` + `sample_size`, sedangkan tingkat pengisian disembunyikan. Export menandai lewat header `X-Export-Truncated`.
- **`attendance_gate.start_date`/`end_date` hanya menerima RFC3339** (mis. `2026-08-01T00:00:00Z`); kiriman `"2026-08-01"` akan ditolak dengan pesan parse JSON yang tidak informatif. Perlu dibereskan saat FE dibangun.
- **RBAC belum berkatalog permission-set** per [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]. Pindah ke sumbu departemen **mendekatkan** ke ADR itu (hak menempel pada tempat orang bekerja, bukan pada key modul) tapi belum memenuhinya: tingkat perannya masih tier lama `staff`/`supervisor`/`admin`, bukan permission-set granular.
- ✅ **Section/multi-halaman sudah ada** (PR [#870](https://github.com/bip-itteam-internal/bip-erp/pull/870)).
- ✅ **Keterangan ujung skala sudah ada** (PR [#871](https://github.com/bip-itteam-internal/bip-erp/pull/871)).
- **Upload file, percabangan, grid, dan opsi "Lainnya" belum ada** — jarak yang tersisa terhadap Google Forms. Urutan yang disarankan: opsi "Lainnya" (murah) → upload file → percabangan. Percabangan menuju bagian, jadi kini sudah punya landasannya.
- **Analisa belum mengelompokkan hasil per bagian.** Yang dijamin sekarang hanya bagian tak muncul sebagai kartu kosong; pengelompokan visualnya polesan yang belum dikerjakan.
- **Form approval yang sudah matang JANGAN dimigrasikan ke sini** (leave/overtime/koreksi presensi) — semuanya punya workflow & rantai approval sendiri. Form Builder untuk kasus baru/ad-hoc.

## Dependensi & Integrasi

- **MongoDB** `form_builder_db` — koleksi `forms`, `form_responses`. Index dibuat idempoten saat boot. Lihat [[DB - Overview and Notes]].
- [[CORE - API Master Gateway]] — satu-satunya pintu masuk; modul `form-builder` di map `InternalURL`.
- [[Microservices - Attendance Service]] — **konsumen** `GET /internal/compliance` pada jalur clock-in mobile.
- Auth mengikuti [[CORE - SSO Flow]]; identitas datang sebagai header `BIP-*`.
- [[Microservices - Employee Service]] — **dependensi OPSIONAL**, dipanggil HANYA saat menerbitkan form penilaian (`GET /list?type=employee`) untuk memotret sasaran dan menyusun penerima notifikasi. Daftar diambil **sekali** untuk keduanya.
- [[Microservices - Notification Service]] — **dependensi OPSIONAL**, `POST /inbox/send` saat form terbit dan saat pengisian selesai. Best-effort: gagal hanya di-log.

> [!warning] Kedua dependensi itu SENGAJA di luar map `InternalURL`
> `validation.ValidateInternalURL` **panic** pada entri kosong, jadi menaruh `EMPLOYEE_MODULE_URL` / `NOTIFICATION_MODULE_URL` di map itu berarti **seluruh service mati** — termasuk gerbang presensi dan pengisian form biasa — hanya karena env satu fitur belum diisi saat deploy. Keduanya dibaca `os.Getenv` langsung dengan penjaga nil. Pola yang sama dipakai task-management untuk notification-service, dan pernah menggigit sebelumnya (lihat catatan `ValidateInternalURL` di dok ini).
>
> Konsekuensinya: **jalur pengisian form (`/me/*`) tetap tak memanggil service mana pun.** Yang berubah cuma jalur menerbitkan.

## Dokumen Terkait

- [[IT - Form Builder]] — konsep & latar belakang
- [[API - Form Builder Service]] — daftar endpoint
- [[Microservices - Attendance Service]] · [[CORE - API Master Gateway]] · [[DB - Overview and Notes]]
- [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
- [[APP - Web ERP]] · [[APP - MyBharata]] — klien yang belum dibangun

## Deskripsi

*Form Builder Service adalah pembuat form dinamis tanpa coding: sebuah departemen menyusun form sendiri (9 tipe pertanyaan), menerbitkannya ke sasaran tertentu, membaca rekap jawabannya, dan mengekspornya ke CSV — tanpa rilis kode untuk tiap form baru. Sejak PR #907 form juga bisa **menilai karyawan lain**: satu form dipakai berulang untuk banyak orang tanpa pengisinya mengulang dari awal. Service ini juga menyediakan satu endpoint kepatuhan yang dipakai [[Microservices - Attendance Service]] untuk menahan clock-in mobile bila ada form wajib yang belum diisi.*

- **Stack:** Go + Fiber v2 + MongoDB (database sendiri `form_builder_db`)
- **Path:** `services/form-builder`
- **Port:** 6986 (internal, `expose`; tidak dipublish ke host)
- **Status**: ⚠️ **Implemented & LIVE di dev DAN prod** (PR [#849](https://github.com/bip-itteam-internal/bip-erp/pull/849) + perbaikan [#855](https://github.com/bip-itteam-internal/bip-erp/pull/855)); prod naik 2026-08-01 dengan kepemilikan per departemen, bagian, dan keterangan ujung skala (PR [#869](https://github.com/bip-itteam-internal/bip-erp/pull/869), [#870](https://github.com/bip-itteam-internal/bip-erp/pull/870), [#871](https://github.com/bip-itteam-internal/bip-erp/pull/871)). FE web di [[APP - Web ERP]] sudah lengkap (kelola, builder, **analisa jawaban**) dan ikut ter-deploy; pengisian di [[APP - MyBharata]] sudah ada (section Survei di beranda + halaman isi berbagian). **Yang diverifikasi saat deploy hanya health `200` lewat gateway + backfill data lama**; alur buat→terbit→isi→analisa **belum diuji ulang** pada versi baru ini, baik di dev maupun prod.
- **Form berulang (periode bulanan & mingguan)**: PR [#938](https://github.com/bip-itteam-internal/bip-erp/pull/938) (fondasi periode), [#940](https://github.com/bip-itteam-internal/bip-erp/pull/940) (gerbang presensi memakai jendela periode), [#942](https://github.com/bip-itteam-internal/bip-erp/pull/942) (analisa & export per periode) — ketiganya **merged ke `main` 2026-08-03**. ⚠️ **Itu SETELAH deploy prod 2026-08-01 dan 2026-08-02** yang disebut di dua butir di atas, jadi fitur ini **tidak ikut** pada rilis tersebut. Dev naik otomatis dari `main` lewat Harness; **status prod belum diverifikasi** dan tidak boleh diasumsikan dari tanggal deploy sebelumnya. **Tak pernah tercatat di dokumen ini maupun [[API - Form Builder Service]]** sampai 2026-08-06, dan **belum ada catatan uji end-to-end** untuk alur berulang di lingkungan mana pun. Lihat bagian tersendiri di bawah.
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

**Tipe pertanyaan (10)** — `short_text`, `long_text`, `number`, `date`, `time`, `dropdown`, `radio`, `checkbox`, `scale`, **`file`**. Validasi struktur (key unik, options wajib untuk tipe pilihan, rentang scale maksimal 10 langkah, `min ≤ max`) dan validasi jawaban (tipe cocok, nilai ∈ options, batas angka & panjang teks, format `YYYY-MM-DD` dan `HH:MM`) keduanya **fungsi murni** — teruji tanpa Mongo.

**Tipe form (4)** — `survey`, `evaluation`, `checklist`, `kaizen`. Bukan sekadar label: tanpanya daftar form berisi survei, checklist, dan penilaian yang tampak serupa padahal cara mengisinya berbeda jauh. `GET /forms?form_type=` menyaringnya; nilai `survey` sengaja ikut menjaring dokumen yang field-nya belum ada, karena backfill baru mengisinya saat boot. Kiriman tanpa `form_type` diberi default `survey` (klien lama belum mengirimnya), tapi nilai **tak dikenal diteruskan apa adanya** supaya validasi menolaknya dengan pesan jelas alih-alih diam-diam berubah jadi survei.

> [!success] Tipe `request` ("Pengajuan") DIHAPUS — ✅ live di dev DAN prod
> **Merged ke `main` 2026-08-08**: FE [erp-frontend#864](https://github.com/bip-itteam-internal/erp-frontend/pull/864) pukul 13:43 UTC lebih dulu, lalu BE [#1097](https://github.com/bip-itteam-internal/bip-erp/pull/1097) 13:44 UTC — urutan itu disengaja, lihat di bawah. **Live di dev** dan terverifikasi lewat gateway 2026-08-09: `GET /form-type-rules` membalas `form_types` berisi **empat** nilai, tanpa `request`. **Prod ikut naik 2026-08-09** lewat deploy manual yang sama; prod tetap 0 dokumen `request` (`evaluation` 2, `survey` 2, `checklist` 1) sehingga backfill senyap — dan senyap di sini adalah keadaan yang BENAR, bukan tanda backfill gagal jalan.
>
> **Merge tidak langsung berarti deploy, dan jedanya tak bisa ditebak.** Diperiksa 20 menit setelah merge, container `Form-Builder-Service` di dev masih `Up 39 hours` — belum tersentuh. Diperiksa lagi keesokan harinya, perubahan itu sudah mendarat. Jadi dev memang naik sendiri, tapi **tidak seketika**, dan menyimpulkan "sudah ter-deploy" dari waktu merge sama salahnya dengan menyimpulkan "tidak akan ter-deploy" dari satu kali pemeriksaan. Yang benar: **periksa uptime containernya**, jangan diasumsikan dari kedua arah.
>
> Dari lima tipe, hanya `evaluation` (terikat `subject`), `kaizen` (terikat `settings.kaizen`), dan `survey` (default `normalizeFormType`, sasaran backfill, punya cabang filternya sendiri) yang benar-benar mengubah perilaku. `request` dan `checklist` sama-sama label murni, jadi yang membedakan nasib keduanya **keputusan produk, bukan keterikatan di kode**; menghapus `request` tak menyentuh satu pun jalur pengisian, analisa, atau gerbang presensi.
>
> Yang berisiko datanya, bukan perilakunya. Begitu entri hilang dari `knownFormTypes`, `validateFormType` menolaknya, sehingga form yang tertinggal bertipe itu **gagal disunting dengan `400` tanpa jalan keluar** — `FormType` hanya bisa diubah selagi status `draft` (lihat `updateFormHandler`), jadi form `published`/`closed` yang tertinggal terkunci selamanya. Karena itu pemindahan `request` → `survey` dijalankan **saat boot** lewat `retiredFormTypes`/`backfillRetiredFormType` di `migrate.go`, meniru `backfillOwnerDepartment`.

**Kedua lingkungan ternyata sudah bersih**: dev dan prod sama-sama **0 dokumen** bertipe `request` (dihitung langsung ke `Form-Builder-MongoDB` masing-masing, 2026-08-08 — prod: `evaluation` 2, `survey` 2, `checklist` 1; dev: `survey` 11, `kaizen` 2). Jadi backfill takkan memindahkan apa pun, dan barisnya akan **senyap** di log boot. Ia tetap ada sebagai jaring pengaman, karena angka nol hari ini tak menjamin nol di lingkungan yang belum pernah dilihat.
>
> **Urutan deploy TERBALIK dari kebiasaan "BE dulu, FE menyusul".** Aturan itu untuk penambahan field, di mana FE lama aman karena fallback. Untuk **penghapusan nilai enum** kebalikannya: BE dulu berarti FE lama masih menawarkan "Pengajuan" dan siapa pun yang memilihnya kena `400`, sedangkan FE dulu menghilangkan pilihannya sementara BE masih menerima — tak ada jendela galat sama sekali.

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

## Izin tipe form per departemen

> Status: ✅ **LIVE dan teruji end-to-end di dev DAN prod.** Merged 2026-08-08: BE [#1099](https://github.com/bip-itteam-internal/bip-erp/pull/1099) 17:23 UTC lebih dulu, FE [erp-frontend#866](https://github.com/bip-itteam-internal/erp-frontend/pull/866) 17:24 UTC. Prod di-deploy manual 2026-08-09. Keputusan dan alasannya: [[ADR - 0041 Izin Tipe Form Menempel di Departemen]].
>
> Yang dibuktikan di dev, bukan sekadar boot `200`: akun ber-`it:staff` ditolak `403` sementara `it:supervisor` lolos (jadi gerbangnya membedakan **tingkat**, bukan sekadar keberadaan kunci modul) · melarang sebuah tipe langsung terbaca di `GET /me/capability` milik **pemakai lain** · nilai tipe tak dikenal ditolak `400` · membuat form bertipe terlarang ditolak `403` sementara tipe yang sama **berhasil** dibuat saat aturannya dilonggarkan — kontrol negatif **dan** positif, karena `403` juga muncul bila gerbangnya salah pasang. Pesan penolakannya sampai utuh lewat gateway: `departemen Tech Development tidak diizinkan membuat form bertipe evaluation. Hubungi tim IT bila ini keliru`.
>
> **Di prod diuji ulang penuh 2026-08-09** dengan cara yang **tidak membuat satu dokumen pun**, memanfaatkan urutan validasi `createForm`: `validateRecurrence` berjalan SESUDAH gerbang tipe. Payload sah bermuatan `open_day: 99` karena itu dibalas `400 open_day untuk bulanan harus 1..28` saat tipenya diizinkan (**bukti gerbangnya dilewati**) dan `403` saat tipenya dilarang (**bukti gerbangnya menahan**) — kontrol positif dan negatif dari satu payload, tanpa residu. Diperiksa sesudahnya: prod tetap 5 form dengan distribusi tak bergeser. `/me/capability` ikut berubah bolak-balik mengikuti aturannya.
>
> Dua percobaan membuktikan rute lewat probe **tanpa token** sebelumnya gagal memberi informasi, dan keduanya ketahuan justru karena disertai kontrol negatif: lewat gateway, rute karangan pun dibalas `401`; langsung ke service, sama saja, karena penjaga kunci-gateway dipasang **global** sebelum routing. Kalau kontrol negatifnya dilewatkan, `401` pada rute baru akan terbaca sebagai "rute terdaftar" padahal tak membuktikan apa-apa. Yang akhirnya membuktikan adalah panggilan **berautentikasi**.
>
> ⚠️ **Peran akun bisa BERBEDA antara dev dan prod.** `panpan` ber-`it:staff` di dev (karena itu dipakai sebagai kontrol negatif di sana) tetapi lolos `can_manage_type_rules` di prod. Jangan menyalin asumsi peran antar-lingkungan; baca `/me/capability` di lingkungan yang sedang diuji.

Tiap departemen bisa dibatasi tipe form apa yang boleh **dibuatnya**. Ditetapkan tim IT lewat layar tersendiri, bukan konfigurasi env.

**Yang disimpan adalah tipe yang DILARANG** (koleksi `form_type_rules`, index unik `(company_id, department)`), bawaannya semua boleh. Tak ada dokumen untuk sebuah departemen berarti tak ada larangan, jadi tak satu pun form lama perlu dimigrasi dan departemen yang baru ditambahkan ke `FORM_BUILDER_DEPARTMENTS` langsung bekerja tanpa menunggu siapa pun mengatur barisnya.

Arah bawaan itu dipilih karena **kegagalannya berbalik arah**: dengan daftar-izin, tipe form yang ditambahkan nanti tak terlihat oleh satu pun departemen sampai tiap baris disunting — merge, deploy, lalu diam, persis pola `recurrence` dan kategori inbox Kaizen. Dengan daftar-larangan, yang terjadi cuma sebuah departemen mendapat tipe yang tak diniatkan IT: terlihat, tak merusak data, diperbaiki dalam semenit. **Ini tidak membatalkan pilihan daftar-izin di papan ide Kaizen** — di sana yang dijaga kebocoran ke layar sekantor, di sini tak ada yang bocor.

> [!warning] Aturan berlaku saat tipe DITETAPKAN, bukan saat form disunting
> Hanya dua titik: `createForm` (setelah `owner_department` dikanonikkan — mencarinya dengan ejaan kiriman akan meleset lalu meloloskan tipe yang sengaja ditutup) dan `updateForm` **bila tipenya benar-benar berganti pada form draft**.
>
> Mencabut sebuah tipe **tidak menyentuh** form yang sudah terlanjur bertipe itu. Ini syarat kebenaran, bukan kelonggaran: `FormType` cuma bisa diubah selagi draft dan form terbit tak bisa mundur ke draft, jadi memeriksa aturan pada tiap penyuntingan akan **mengunci form itu selamanya** — pemiliknya bahkan tak bisa mengganti judul. Pelajaran yang dibayar hari yang sama saat tipe `request` dihapus. Penempatannya dijadikan predikat murni `typeCheckNeeded` supaya bisa diuji, bukan cuma diyakini; **jangan pindahkan ke `validateFormDefinition`** meski di sana terlihat lebih rapi.

**Nilai tak dikenal ditolak saat MENULIS, diabaikan saat MEMBACA.** Asimetri disengaja: saat menulis orangnya ada di depan layar dan bisa diberi tahu mana yang salah; saat membaca, satu nilai basi (mis. `request` yang sudah dihapus) tak boleh berubah jadi pemadaman Form Builder yang sebabnya tak terbaca dari pesan galat mana pun.

**Gerbangnya kunci MODUL `system_roles["it"]`**, tingkat `supervisor` atau `admin` — bukan nama departemen `"Tech Development"`. Keduanya sumbu berbeda dan sudah pernah tertukar di service ini (PR #869). `staff` dikecualikan karena aturan ini membatasi departemen lain; `admin`-saja ditolak karena bila tak seorang pun memegang `it:admin`, layarnya tak bisa dibuka siapa pun dan gejalanya senyap.

Rute `/form-type-rules/*` hidup **di luar grup `/forms`**, meniru pemisahan rute komite Kaizen: grup itu menuntut keanggotaan departemen aktif, sedangkan yang menetapkan aturan justru IT untuk departemen yang **bukan** miliknya.

**`GET /me/capability` menjawab daftar POSITIF per departemen** (`form_types_by_department`), sehingga frontend tak memegang satu baris pun logika aturan. Per departemen, bukan datar: SPV HRGA membawahi dua sekaligus, dan meratakannya salah ke dua arah — irisan menyembunyikan tipe yang sebenarnya boleh, gabungan menawarkan tipe yang pasti ditolak. `can_manage_type_rules` dihitung **terpisah** dari `can_manage`, karena admin IT belum tentu mengelola satu departemen pun dan kalau haknya ikut mati ia tak pernah melihat pintu masuk layarnya.

> [!note] "Jangan diratakan" berlaku untuk PEMBUATAN, bukan untuk penyaringan daftar
> Peringatan di atas menjawab dropdown tipe di editor, tempat setiap pilihan berakhir jadi permintaan tulis yang bisa ditolak `403`. Sejak 2026-08-10 frontend juga memakai jawaban ini untuk **tab penyaring di daftar form**, dan di sana yang benar justru **gabungan** seluruh departemen dalam cakupan: daftarnya memuat form kedua departemen, jadi mengiris akan menyembunyikan tab untuk form yang benar-benar ada, sementara "menawarkan tipe yang pasti ditolak" tak berlaku karena menyaring bukan menulis. Dua sumbu berbeda dari satu jawaban yang sama; detail di [[APP - Web ERP]].

Yang **tidak** diselesaikan: `audience` dan `subject` masih hanya diperiksa bentuknya, bukan jangkauannya. Departemen yang dibatasi tipenya tetap bisa menyasar karyawan departemen lain memakai tipe yang masih boleh dibuatnya.

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

⚠️ **Gerbang ini lebih lebar daripada yang dibaca sepintas.** `managedDepartments` memakai `common.SupervisedDepartments` yang **selalu menyertakan departemen sendiri**, bukan versi `Strict`. Jadi yang lolos bukan "atasan di departemen aktif", melainkan **siapa pun yang bekerja di sana dan punya peran apa pun di modul apa pun** — staf dengan `ticket:staff` sekalipun. Shared-library menandai perbedaan itu sendiri: docstring `SupervisedDepartmentsStrict` menyebut versi non-strict "membuat SETIAP karyawan tampak sebagai supervisor departemennya sendiri" dan mensyaratkan jalur tulis memakai yang strict. Apakah itu memang dikehendaki **belum pernah diputuskan tertulis**; komentar gerbangnya berbunyi "berada di departemen yang diaktifkan", yang mengesankan disengaja.

## Kepemilikan bersama: `owner_departments` jamak

> **Status**: 🔜 **Branch `feat/formbuilder-owner-jamak`, terverifikasi LOKAL** (BE `go build`/`vet`/`test` hijau; FE `pnpm tsc`/`eslint`/`vitest` hijau), **BELUM merge, BELUM deploy.** Alur end-to-end lewat gateway (buat form dua-owner → pembaca departemen lain melihatnya) **belum diuji** — itu gerbang yang tersisa sebelum bisa diklaim jalan. Jangan baca status ini sebagai "live".

Sebuah form kini bisa dimiliki BEBERAPA departemen supervisi sekaligus, bukan cuma satu. Pemicunya nyata: di prod, dua form General Affair yang sedang `published` hanya bisa dikelola satu orang (SPV HRD, satu-satunya `is_supervisor` Human Resource yang cakupannya mencakup General Affair), karena kepemilikan tunggal `owner_department` menautkan form ke satu departemen saja.

- **`Form.OwnerDepartments []string`** — field BARU, bukan mengganti tipe `OwnerDepartment`. `OwnerDepartment` tetap = owner PRIMER (elemen pertama), sehingga seluruh pembaca lama (analisa, tampilan, kaizen) tak tersentuh. Dokumen lama tanpa field ini diperlakukan `[OwnerDepartment]` lewat `effectiveOwners`; backfill saat boot mengisinya (`owner_departments = [owner_department]`, update-pipeline), tapi gerbang dan filter sudah benar sebelum backfill jalan.
- **Lihat** = cakupan pembaca mengandung SALAH SATU owner. `GET /forms` menyaring `owner_departments $in cakupan` dengan cabang `$or` fallback ke `owner_department` untuk dokumen belum ter-backfill — tanpa cabang itu form owner tunggal lama lenyap dari daftar pemiliknya, senyap. Pola sama dengan `periodQuery`/`subjectQuery`.
- **Tulis** (sunting, terbit, hapus) = pembaca mengelola SALAH SATU owner (`canManageAnyDepartment`, gerbang tunggal `loadManagedForm` + dua rute Kaizen). Keputusan sadar **"kelola salah satu, bukan semua"**: menyebar beban supaya form GA tak bergantung satu orang. Risiko yang diterima: staf salah satu departemen bisa menghapus form bersama — tapi HANYA form yang sengaja dibagikan, karena membuat form bersama menuntut pembuatnya mengelola SEMUA owner (`canonicalDepartments` menolak seluruhnya bila satu owner di luar cakupan; `403`).
- **Tipe form diperiksa PER owner**: form HR+GA hanya sah bertipe yang boleh dibuat KEDUANYA (irisan aturan [[ADR - 0041 Izin Tipe Form Menempel di Departemen]]). FE menawarkan irisan (`allowedFormTypesForAll`); BE menolak di owner pertama yang melarang.
- **Owner terkunci saat pembuatan**, sama seperti `owner_department` tunggal: `updateForm` tak memindahnya (`updated := *form` mempertahankan `OwnerDepartments`).

**Konsekuensi privasi, diterima sadar.** Analisa menampilkan nama, departemen, jabatan, dan seluruh jawaban tiap pengisi. Untuk form yang dibagikan HR+GA, staf HR kini bisa membaca jawaban form GA. Ini **MELEBARKAN kembali** penyempitan yang sengaja dibangun PR #869 (yang mempersempit lingkaran pembaca analisa ke departemen pemilik). Berlaku HANYA untuk form yang eksplisit dibagikan, dan disepakati sadar bersama pemilik keputusan.

**Perbaikan alur ikut** (di [[APP - Web ERP]]): menu Form Builder ditambahkan ke kategori sidebar `ga`. Staf GA yang cuma pegang role `ga` (tanpa `hris`) sebelumnya **lolos** `requireFormManager` (General Affair ada di daftar aktif) tapi tak pernah melihat menunya — sidebar menampilkan menu per key `system_roles`, dan menu GA tinggal di kategori `hris`. Sensus prod 2026-08-20: 1 orang (GA Staff) persis di keadaan ini. Duplikat bagi pemegang HRGA (punya kategori `hris` DAN `ga`) dibuang di `gabungBlokHrga`.

> [!warning] Penyimpangan sadar dari ADR 0030 & ADR 0041
> [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] (baris 26) menyatakan yang TIDAK ikut pindah ke sumbu izin adalah cakupan departemen Form Builder. Perubahan ini **tidak** memindahnya ke `reach` (env `FORM_BUILDER_DEPARTMENTS` + `managedDepartments` tetap), melainkan menambah **kejamakan** pada owner — sumbu yang belum dijelaskan ADR 0041. Keduanya perlu ditinjau bersamaan saat sumbu izin `reach` untuk Form Builder kelak dibangun. Sumbu izin `formbuilder` (fase satu, di bawah) tak berubah.

## Izin: katalog `formbuilder` (fase satu)

> **Status**: ⚠️ **Merged & LIVE di dev DAN prod, 2026-08-10** (PR [#1138](https://github.com/bip-itteam-internal/bip-erp/pull/1138), merge commit `0c5d5231`).
>
> **Dev** terverifikasi lewat gateway: `formbuilder` muncul di `GET /master/permission-modules`, ketiga paket ter-seed dengan izin dan reach yang benar, dan `/me/capability` membawa `can_write`. Akun uji `it:staff` mendapat `can_manage:true`, `can_write:true`, `can_manage_type_rules:false` — identik dengan sebelum perubahan, jadi fase satu terbukti tak mengubah akses.
>
> **Prod** naik manual hari itu juga dengan **dua container** (`employee-service` + `form-builder-service`, `--no-deps`). Bukti bukan sekadar container hidup: log boot menulis `[Migrate] 3 paket permission default disisipkan`, dan sensus langsung ke `employee_db` prod mencatat ketiga paket ada (total paket 36 → **39**).
>
> ⚠️ **Belum ada satu jabatan pun yang dipasangi paketnya, di dev maupun prod.** Selama itu, seluruh akses masih ditentukan tier lama lewat fallback — persis yang dimaksud fase satu, dan sekaligus alasan kenapa [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] belum terpenuhi untuk modul ini.

Sampai PR itu masuk, Form Builder adalah **satu-satunya modul ber-UI yang aksesnya tak bisa diatur dari layar Hak per Posisi**: gerbangnya tier lama, dan daftar departemennya env yang menuntut `--force-recreate`.

Tiga izin, masing-masing cermin gerbang yang berlaku hari ini:

| Izin | Menggerbang | Cermin gerbang lama |
|---|---|---|
| `formbuilder.view` | rute baca di `/forms/*` | `requireFormManager` |
| `formbuilder.work` | buat, ubah, terbitkan atau tutup, hapus | idem — grup lama tak memisahkan baca dari tulis |
| `formbuilder.rules.manage` | `/form-type-rules/*` | `requireTypeRulesAdmin` (`it` supervisor/admin; `staff` dikecualikan) |

Tiga paket: `formbuilder_lihat`, `formbuilder_pengelola`, dan `formbuilder_penata_aturan`.

**Dua sumbu, dan hanya satu yang pindah.** Gerbang lama menggabungkan tingkat peran DAN keanggotaan departemen aktif. Izin menggantikan syarat **pertama saja**; cakupan departemen tetap dikerjakan `managedDepartments` + `canManageDepartment`, tidak dipindah ke `reach`.

Itu keputusan sadar. Penyaringan `reach: division` belum ditegakkan di mana pun selain [[Microservices - Task Management Service]], jadi memindahkannya sekarang berarti menukar penjaga yang bekerja dengan penanda yang tak dibaca siapa pun. Seluruh paket karena itu ber-reach `all`, dan itu menyatakan apa adanya alih-alih menjanjikan pembatasan tanpa penegak. Akibat yang harus diterima: **pembatasan per-departemen lewat paket belum mungkin** — paket ber-reach `division` akan tersimpan rapi lalu berperilaku persis `all`.

**Fase satu tidak mengubah akses siapa pun.** Sakelarnya `FORMBUILDER_PERMISSION_ENFORCEMENT` dan `FORMBUILDER_TIER_FALLBACK`, keduanya default menyala, mengikuti pola [[Microservices - Recruitment Service]] dan [[Microservices - Learning Service]]. Yang baru hanya dua kemampuan yang sebelumnya mustahil: memberi akses **baca jawaban tanpa hak menghapus form**, dan memberi hak **menata aturan tipe tanpa hak mengelola form**.

⚠️ **`capabilityHandler` ikut berubah** dan mendapat field `can_write`. Membiarkannya menilai sendiri lewat `hasManagerRole` akan membuat layar dan server berbeda pendapat begitu paket pertama dipasang: tombol muncul lalu setiap aksinya ditolak `403`. **Frontend nol perubahan** — Form Builder tak pernah menyalin aturan aksesnya ke FE, dan justru itu yang membuatnya lolos dari divergensi yang sedang terjadi di `recruitment`/`training`, di mana tabel `FALLBACK` frontend sudah fase dua sementara backend masih fase satu ([[CORE - RBAC dan Permission Set]]).

**Celah yang ikut tertutup di PR yang sama**: `recruitment` dan `training` tak pernah didaftarkan `RegisterCatalog` di employee-service sejak katalognya dibuat, sehingga paket keduanya tak muncul di `GET /master/permission-modules` dan setiap upaya mengubahnya ditolak "permission tak terdaftar di katalog" — padahal paketnya tetap bisa dipasang ke posisi, jadi gejalanya senyap. Registrasinya kini fungsi bernama dengan penjaga yang menilai dari sisi **seed**, bukan daftar modul yang diketik ulang.

## Skor gabungan: satu angka per orang yang dinilai

> **Status**: ✅ **Merged & live di dev 2026-08-10** (BE [#1141](https://github.com/bip-itteam-internal/bip-erp/pull/1141), FE [erp-frontend #954](https://github.com/bip-itteam-internal/erp-frontend/pull/954)). Terverifikasi lewat gateway dev dengan form penilaian sungguhan. **PROD belum.**

Rekap per pertanyaan menjawab "aspek mana yang lemah"; `Overall` menjawab "siapa yang perlu ditindaklanjuti" tanpa membandingkan delapan kolom sekaligus.

**Dua lapis rata-rata, perlakuannya sengaja berbeda.** Di dalam satu penilai **berbobot**, sebab bobot menyatakan pertanyaan mana yang lebih penting. Antar penilai **polos**, sebab tak ada penilai yang lebih penting dari penilai lain. Menjadikan lapis kedua berbobot berarti diam-diam memutuskan suara sebagian orang lebih berat.

⚠️ **Penyebut bobot dihitung dari pertanyaan yang DIJAWAB penilai itu**, bukan dari seluruh bobot form. Memakai total form sama saja menghitung pertanyaan kosong sebagai nol, sehingga penilai yang melewati satu pertanyaan berbobot besar terlihat memberi nilai rendah di situ padahal ia cuma tak menilainya.

**Bobot (`FormField.Weight`) bernilai RELATIF, bukan persentase wajib-100.** Bobot 3 berarti tiga kali lebih berat dari 1. Dipilih relatif supaya menghapus satu pertanyaan tak memaksa menyetel ulang seluruh bobot lain; angka persen tetap bisa diisi apa adanya karena jumlahnya memang 100. Pointer, sebab **0 adalah bobot yang sah** (pertanyaan pelengkap yang sengaja tak ikut) dan harus bisa dibedakan dari tak-diisi. Kosong berarti 1, jadi **form lama tak menuntut migrasi** — dikunci uji tersendiri.

**Hanya tipe `scale` yang ikut**, sengaja lebih sempit dari `numericFields` yang memasok kolom per-pertanyaan. `number` tak punya batas atas: nilai 90 pada "berapa kali terlambat" akan menenggelamkan skala 1..5 di sebelahnya. `numericFields` **tidak disentuh**, dan ada uji yang menjaga agar keduanya tak pernah disatukan "supaya rapi".

**Cakupan dilaporkan, tidak disembunyikan.** `OverallFields`/`TotalQuestions` membuat layar berbunyi "Skor dihitung dari 5 dari 12 pertanyaan". Tanpa itu, form yang dibangun memakai `radio` menghasilkan skor dari sebagian kecil pertanyaan dan tak ada apa pun yang memberitahu pembacanya. Pola yang sama dipakai `Populasi` di mesin KPI ([[HRIS - Otomasi Skor KPI]]).

**Kosong bukan nol.** `Overall` dihilangkan dari muatan JSON saat belum ada yang menilai — nol berarti "sudah dinilai dan hasilnya buruk", tuduhan yang tak dibuat siapa pun. Dikunci uji kontrak JSON.

Nilai di luar rentang **diklem**: validasi menolaknya saat menulis, tapi dokumen lama bisa menyimpannya dan satu jawaban 7 pada skala 1..5 tak boleh keluar sebagai 150.

> **Belum masuk KPI, dan itu disengaja.** Angkanya berhenti di layar analisa. Menyambungkannya ke `kpi_score` menuntut definisi yang stabil selamanya, sebab angka periode lalu harus tetap berarti saat rumusnya berubah. Melihatnya dulu di analisa memberi kesempatan mengoreksi rumus tanpa merusak riwayat siapa pun. Bila kelak dilanjutkan, polanya sudah ada di `kpi_sumber_kaizen.go`, dan [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] menetapkan employee-service tetap pemilik tunggal `kpi_score`.

## Indeks layanan departemen: `metric_key` + `GET /me/service-index`

> **Status**: ⚠️ **Merged ke `main` 2026-08-25** (PR [#1417](https://github.com/bip-itteam-internal/bip-erp/pull/1417) + [#1418](https://github.com/bip-itteam-internal/bip-erp/pull/1418)). **Belum di-deploy, belum diuji lewat gateway.** Konsep produknya di [[IT - Form Builder]].

Skor gabungan di atas menjawab "siapa yang perlu ditindaklanjuti". Bagian ini menjawab pertanyaan yang berbeda: **bagaimana orang di luar sebuah departemen menilai layanannya**, sebagai satu angka per bulan yang dibaca di halaman ringkasan divisi.

**Perhitungannya memanggil `overallOf` apa adanya, bukan rumus baru.** Keduanya meringkas jawaban berskala berbobot jadi satu angka, dan dua definisi yang sama-sama masuk akal akan menyimpang begitu salah satunya disentuh — tanpa satu pun layar yang menunjukkan bahwa angka di ringkasan dan angka di halaman analisa sudah berbeda artinya. Ada uji yang membandingkan keduanya langsung untuk masukan yang sama.

**`metric_key` menandai form, bukan id yang ditanam di frontend.** Id Mongo di klien tak bisa diaudit, tak ikut berpindah saat form dibuat ulang, dan tak punya tempat yang menjelaskan kenapa angkanya berasal dari form itu. Validasinya menutup tiga kegagalan senyap sekaligus: nilai tak dikenal, tipe selain `survey`, dan form yang tidak berulang bulanan — yang terakhir paling berbahaya karena jawabannya tersimpan tanpa `period_key` sehingga kartunya kosong selamanya sementara jawaban terus berdatangan.

**Keunikan ditegakkan indeks unik PARSIAL**, bukan sekadar pemeriksaan hitungan saat terbit. Dua permintaan bersamaan sama-sama melihat hitungan nol dan keduanya lolos; yang kalah kini ditolak Mongo dan diterjemahkan jadi `409` yang sama. ⚠️ Filternya wajib parsial: `metric_key` bertanda `omitempty`, jadi indeks unik biasa akan memperlakukan seluruh form tanpa penanda sebagai satu nilai null yang sama dan dua form biasa di satu departemen akan saling menolak. Pembuatan indeksnya **tidak fatal** bila gagal, sebab service yang menolak boot demi satu indeks memadamkan seluruh Form Builder.

**Rutenya di grup `/me`, bukan `/forms`.** Alasannya sama persis dengan rute komite Kaizen: yang membacanya staf divisi di ringkasannya sendiri, yang belum tentu mengelola form apa pun. Gerbangnya pindah ke dalam handler dan bersumbu departemen (`common.SupervisedDepartments`, yang selalu memuat departemen pemanggil sendiri). Rute BACA, jadi terkunci `EffectiveCompanyID` — memakai `CompanyID` membuat admin pusat melihat angka perusahaannya sendiri di bawah label perusahaan yang sedang dibuka.

**Kerahasiaan meluas ke form tanpa sasaran.** `settings.anonymous` melengkapi `subject.anonymous` yang lebih dulu ada, dan keduanya sengaja **tidak** dijumlahkan sebagai OR — form bersasaran hanya membaca miliknya sendiri. Penentu tunggalnya `anonimAktif` di `anonim.go`, menggantikan syarat yang sebelumnya ditulis ulang di daftar jawaban dan export. Mencabutnya setelah ada jawaban dibalas `409`, dan pada `PATCH` field yang absen berarti jangan diubah.

**Pertanyaan berbobot nol dikembalikan terpisah** sebagai `unweighted`, bukan disembunyikan: ia jadi pembanding di luar indeks, sehingga indeks yang naik sementara pertanyaan keseluruhan turun menunjukkan bobot antar aspeknya yang salah, bukan layanannya yang membaik.

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

## Form berulang: periode bulanan dan mingguan

Sebuah form bisa terbit ulang dengan sendirinya tiap bulan atau tiap minggu, tanpa pemiliknya membuat form baru. Kasus nyata yang jadi acuan: survei pelayanan Office Boy dan Office Girl yang dibuka tiap tanggal 26 sampai akhir bulan.

`Form.Recurrence` (`{enabled, unit, open_day}`) nil berarti form sekali jalan, dan perilakunya **persis** seperti sebelum fitur ini ada. Pointer, bukan nilai, supaya dokumen lama tidak terbaca sebagai "berulang dengan aturan kosong".

**Satuannya sengaja hanya dua**, `monthly` dan `weekly`. Kuartalan dan tahunan belum punya kasus nyata, dan menambahkannya sekarang berarti menebak.

- Bulanan: `open_day` 1..28. Dibatasi 28 karena Februari, dan karena "tanggal 31" pada bulan 30 hari tak punya arti yang jelas.
- Mingguan: `open_day` 1..7 mengikuti hari ISO (Senin sampai Minggu).

**Jendelanya SELALU berakhir di ujung bulan atau minggu**, bukan "sekian hari setelah buka". Durasi bebas bisa melewati batas bulan sehingga dua periode hidup bersamaan, dan begitu itu terjadi tak ada jawaban yang benar untuk pertanyaan "periode mana yang aktif sekarang".

Penanda periode: `2026-08` untuk bulanan, `2026-W32` untuk mingguan. Penomoran minggu memakai **ISO** supaya minggu yang melintasi pergantian tahun tak melahirkan dua penanda berbeda untuk minggu yang sama.

Seluruh aturan penanggalan di `period.go` adalah **fungsi murni**: `now` selalu diberikan pemanggil, jadi teruji tanpa menunggu tanggal tertentu tiba. Zona waktunya mengikuti `now`, bukan dipaksa UTC, karena memaksa UTC menggeser "tanggal 26" sehari bagi pemakai WIB dan pergeseran macam itu baru ketahuan saat periode terbuka di hari yang salah.

> [!warning] Fitur ini SEMPAT ter-merge, ter-deploy, dan tetap mustahil dipakai
> Dari PR #938 (2026-08-03) sampai PR [#1019](https://github.com/bip-itteam-internal/bip-erp/pull/1019) (2026-08-06), **`recurrence` tidak pernah bisa diset lewat API**. `formRequest` — satu-satunya badan request untuk create dan update form — tak punya fieldnya, dan `git log -S "req.Recurrence"` menunjukkan tak pernah punya sepanjang sejarah repo.
>
> Seluruh lapisan domainnya lengkap dan teruji: aturan penanggalan, snapshot, cron, gerbang presensi berjendela periode, analisa per periode. Yang hilang cuma satu baris pengikatan, dan tanpa itu **tak seorang pun bisa membuat form berulang**. Bukti diamnya: prod punya **0 form berulang dan 0 dokumen periode** setelah tiga hari fiturnya "live".
>
> Efek ikutannya, `form_type: "kaizen"` yang mewajibkan pengulangan bulanan jadi **mustahil dibuat sama sekali**, sehingga tahap 1 sampai 3 Kaizen praktis tak bisa disentuh siapa pun meski sudah merge dan deploy.
>
> Penjaga "pengulangan tak boleh dinyalakan pada form yang sudah punya jawaban" juga **kode mati** selama itu: `sudahBerulang` dan `akanBerulang` selalu bernilai sama karena `updated` cuma salinan dokumen tersimpan. Baru hidup setelah #1019.
>
> Ketahuan hanya lewat uji end-to-end. 185 unit test hijau, termasuk yang menguji aturan periode sampai kasus tahun kabisat, tapi tak satu pun memeriksa apakah field itu bisa SAMPAI ke sana dari JSON. Dikunci sekarang oleh `form_request_test.go`.
>
> Setelah #1019, `recurrence` pada `PATCH` mengikuti kaidah **absen berarti jangan diubah** (seperti blok kaizen), supaya satu kiriman parsial tak diam-diam mengubah survei bulanan jadi form sekali jalan.

### Cron pembuka periode

`cronManager()` jalan **tiap jam** dengan zona `Asia/Jakarta`, bukan sekali di tengah malam: periode yang terlewat karena service mati saat pergantian hari akan terbuka pada jam berikutnya, bukan tertunda sehari penuh.

Hanya form `published` yang dibukakan periode. Form `closed` yang tetap melahirkan periode baru tiap bulan hanya menumpuk putaran yang tak seorang pun mengisinya. Kegagalan satu form **tidak menghentikan** sisanya, karena satu aturan pengulangan yang rusak tidak boleh membekukan seluruh form berulang lainnya.

> [!warning] Pemanggilan `cronManager()` di `main.go` tidak boleh hilang
> Kegagalannya senyap total: build tetap hijau, seluruh test tetap lulus, dan tak satu pun periode pernah terbuka. `CronManager` milik integration-service jadi dead code justru karena langkah ini pernah terlewat. Lihat [[IT - Background Jobs & Schedulers]].

Pembuatan periode **idempoten lewat index unik** `(form_id, period_key)`, bukan lewat pemeriksaan "sudah ada?" di baris sebelumnya. Dua instance cron yang berjalan bersamaan bisa sama-sama lolos pemeriksaan itu lalu sama-sama menyisip; yang kalah ditolak Mongo dengan galat duplicate-key dan diperlakukan sebagai "sudah dibuat orang lain". Tanpa penanganan itu cron mencatat galat tiap jam untuk keadaan yang sebenarnya benar.

### Apa yang berubah pada jalur pengisian

- `FormResponse.PeriodKey` menandai putaran mana sebuah jawaban milik. **Kosong untuk form biasa DAN untuk seluruh jawaban yang tersimpan sebelum fitur ini**, dan keduanya sah.
- Kunci keunikan bergeser sekali lagi, kini ditambah periode: dari (form, pengisi, yang dinilai) jadi (form, pengisi, yang dinilai, periode). Tanpa itu form bulanan hanya bisa diisi **sekali seumur hidup**, karena jawaban Agustus akan menghentikan pengisi di bulan September.
- Penanda `submitted` di `GET /me/forms` dihitung terhadap **periode berjalan**. Tanpa pembeda ini form bulanan yang sudah diisi Agustus tetap tersembunyi dari daftar di September, dan pengisi tak pernah tahu ada putaran baru.
- Penanda periode **diturunkan dari `windowFor` dan waktu sekarang**, bukan dibaca dari koleksi periode. Jalur ini berjalan pada setiap pengiriman, jadi query tambahan di sana dihindari.

> [!warning] `period_key` kosong tidak sama dengan field yang hilang
> Jawaban yang tersimpan sebelum fitur ini tak punya `period_key` sama sekali (`omitempty`), dan di Mongo `{period_key: ""}` **tidak cocok** dengan dokumen yang field-nya hilang. Setiap pencocokan wajib lewat `periodQuery` (yang memakai `$in: ["", null]`), bukan perbandingan langsung. Tanpa itu penjaga duplikat dan `single_response` diam-diam berhenti bekerja pada **seluruh form lama**. Ini pola yang sama persis dengan `subjectQuery`, dan alasannya sama.

### Gerbang presensi memakai jendela periode

Form berulang memakai jendela **periode berjalan**, bukan `start_date`/`end_date` statis. Tanggal statis hanya masuk akal untuk form sekali jalan: pada survei bulanan ia akan lewat setelah bulan pertama dan gerbangnya tak pernah menyala lagi, padahal formnya justru terbit ulang tiap bulan. Form biasa jatuh ke perilaku lama persis.

### Menyalakan pengulangan setelah ada jawaban DILARANG

`PATCH /forms/:id` menolak `409` bila pengulangan dinyalakan pada form yang sudah punya jawaban. Sebabnya data campur: sebagian jawaban punya asal-usul periode, sebagian tidak, dan mengarang periode untuk data lama justru memalsukan kapan jawaban itu sebenarnya diberikan. **Mematikan** pengulangan tetap boleh; yang dilarang hanya menyalakannya.

### Analisa per periode

`GET /forms/:id/analytics`, `/responses`, dan `/export` menerima `?period=`.

> [!warning] Periode kosong artinya KEBALIKAN di dua tempat
> Di `analyticsFilter`, periode kosong berarti **seluruh periode**: pemilik form yang membuka halaman analisa tanpa memilih periode mengharapkan rekap penuh. Di `responseGuardFilter`, periode kosong berarti **hanya jawaban yang memang tak punya periode**, karena pertanyaannya "apakah orang ini sudah mengisi putaran ini". Menyamakan keduanya akan membuat salah satunya salah diam-diam.

## Tipe `kaizen`: program pengumpulan ide bulanan

> Status: ✅ **Seluruh backend LIVE di dev DAN prod** sejak 2026-08-06, teruji end-to-end di dev. PR [#1016](https://github.com/bip-itteam-internal/bip-erp/pull/1016) (tahap 1-3), [#1028](https://github.com/bip-itteam-internal/bip-erp/pull/1028) (papan ide + pengingat), [#1029](https://github.com/bip-itteam-internal/bip-erp/pull/1029) (setoran KPI), [#1034](https://github.com/bip-itteam-internal/bip-erp/pull/1034) (permukaan karyawan), [#1039](https://github.com/bip-itteam-internal/bip-erp/pull/1039) (gerbang presensi di `/me/kaizen`), [#1044](https://github.com/bip-itteam-internal/bip-erp/pull/1044) (kategori inbox), [#1046](https://github.com/bip-itteam-internal/bip-erp/pull/1046) (penemuan komite). Prod di-deploy manual bersama notification-service dan diverifikasi dengan kontrol positif+negatif. Lampiran berkas ikut menyusul lewat [#1023](https://github.com/bip-itteam-internal/bip-erp/pull/1023) + [#1057](https://github.com/bip-itteam-internal/bip-erp/pull/1057), **live dan teruji end-to-end**. Konsep dan keputusan bisnisnya di [[HRIS - Kaizen (Ide Perbaikan)]].
>
> **Fitur masih inert di prod**: belum ada satu pun form kaizen dibuat, jadi cron pengingat tak punya apa pun untuk dikirim.

Tipe form yang **ditambahkan terakhir** (kelima saat itu, sebelum `request` dihapus), dan seperti `evaluation` ia bukan sekadar label: seluruh perilaku barunya digerbang tipe ini, sehingga tipe-tipe lama tak berubah sedikit pun dan tak ada satu pun form lama yang perlu dimigrasi.

**Ikatan dua arah** dengan blok `settings.kaizen`, meniru pola `evaluation` ↔ `subject`. Tipe `kaizen` wajib punya blok itu, dan blok itu hanya sah pada tipe `kaizen`. Selain itu tipe ini **wajib berulang bulanan** (kuota bulanan tanpa periode tak punya arti), serta **menolak** `single_response` (yang akan menghentikan pengaju tepat setelah ide pertama sehingga kuota lebih dari satu mustahil dipenuhi) dan menolak sasaran penilaian.

**Kuota adalah lantai, bukan langit-langit.** Ide melebihi kuota tetap diterima; program yang tujuannya mengumpulkan ide tapi menolak ide keempat karena kuotanya tiga jelas keliru. Angka bawaan boleh ditimpa per departemen, dan entri berkuota `0` berarti departemen itu dikecualikan dari kewajiban tapi tetap boleh mengirim. Bentuknya daftar entri eksplisit, bukan map, supaya nol tak pernah rancu dengan "belum diatur".

**Satu program aktif per `company_id`**, ditegakkan di jalur tulis saat menerbitkan (`409`). Menyaring daftar saja tak cukup karena gateway meneruskan permintaan apa adanya, dan aturan ini pula yang membuat "berapa kuota saya bulan ini" selalu punya jawaban tunggal.

### Potret peserta: penyebut papan kepatuhan

`FormPeriod` bertambah `participants`, `participants_at`, dan `participants_partial`. Isinya potret orang yang wajib mengisi pada periode itu, lengkap dengan nama, departemen, jabatan, dan **kuota yang dibekukan per orang**.

Ini menggantikan `audience.estimated_size` yang diisi manual pembuat form. Angka yang diisi tangan tak bisa dipakai menyatakan seseorang menunggak.

Diambil **tiap periode**, bukan sekali saat form terbit, dan itu sengaja **berbeda dari `subject.resolved`**: di sana yang dijaga keadilan pembanding penilaian sehingga daftarnya harus beku sepanjang umur form, di sini yang dijaga kejujuran laporan tiap bulan. Karyawan masuk dan keluar tiap bulan; potret sekali-seumur-form akan menagih orang yang sudah resign selamanya sekaligus tak pernah menagih karyawan baru. Kuota dibekukan per orang dengan alasan serupa: kalau dihitung ulang saat laporan dibaca, mengubah kuota di bulan Oktober akan mengubah status kepatuhan orang untuk bulan Agustus.

> [!warning] Potret dijalankan dari cron, yang TIDAK punya `fiber.Ctx`
> `fetchActiveEmployees` menuntut Ctx hidup karena header perusahaan diteruskan dari situ. Mengirim Ctx nil saja tidak cukup: `routes.InternalRequest` memang menjaga `c != nil` dan tak akan panic, tapi employee-service lalu jatuh ke `common.DefaultCompanyID` dan mengembalikan daftar **tenant yang salah**. Karena itu dipakai `InternalRequestCustomHeader` dengan `BIP-Company-ID` dipasang eksplisit dari `company_id` milik form. **Jalur ini belum pernah dijalankan sungguhan.**

**Gagal memotret tidak menggagalkan periode.** Bila employee-service sedang mati, periode tetap dibuka sehingga orang tetap bisa mengirim ide, `participants_partial` ditandai, dan cron jam berikutnya mencoba lagi. Sengaja berbeda dari penerbitan form penilaian yang gagal-keras: di sana pengisi tak punya siapa pun untuk dinilai, di sini yang rusak cuma laporan. Batas potret 1000 orang, ditolak di muka dan tidak dipotong diam-diam.

### Keputusan komite

`FormResponse` bertambah `decision` (pointer, `omitempty`). Nil berarti **belum ditinjau**, dan itu pula keadaan seluruh jawaban form non-kaizen. Konsekuensinya pencocokan "belum ditinjau" wajib memakai `$exists: false` atau `$in: [null]`, bukan perbandingan dengan dokumen kosong — jebakan yang sama sudah menggigit `period_key` dan `subject_employee_id` di service ini.

Keputusan disimpan **terpisah dari `answers`** dan tak pernah menyentuhnya, jadi analisa, daftar jawaban, dan export lama tetap jalan tanpa perubahan bentuk.

Transisi yang sah: belum ditinjau → `accepted` atau `rejected`; `accepted` → `implemented` atau `rejected`. `rejected` dan `implemented` **terminal**. Membuka kembali ide yang sudah diputuskan akan mengubah angka KPI periode yang laporannya mungkin sudah dibaca dan ditandatangani orang.

- **Menolak wajib beralasan** (`400` bila kosong). Penolakan tanpa alasan hanya mengajari orang berhenti mengirim ide. Aturan yang sama dipakai CSAT di [[Microservices - Task Management Service]].
- **`implemented_at` wajib diisi**, tidak diisi otomatis dengan waktu sekarang: skor KPI menghitung ide yang diterapkan per periode, jadi komite yang menandai terlambat akan menyetorkan angka ke bulan yang salah.

> [!warning] Penjaga balapan ada di FILTER TULIS, bukan cuma di validator
> Validator bekerja atas keadaan yang dibaca beberapa saat sebelumnya. Komite di sini terpusat, jadi beberapa orang memang membuka antrean yang sama, dan satu orang yang menekan tombol dua kali cepat pun cukup. Tanpa prasyarat di filter tulis, yang menang adalah yang menulis terakhir — **termasuk menimpa status terminal**, sehingga ide yang sudah ditandai diterapkan bisa berubah jadi sekadar "diterima". Filter tulisnya membawa `{"decision": {"$in": [null]}}` atau `{"decision.status": <status saat dibaca>}`, dan `MatchedCount == 0` dibalas `409`. Bentuknya menyalin cara `ensurePeriod` bersandar pada index unik alih-alih pemeriksaan "sudah ada?".

Aksi massal dibatasi **200 per kiriman** dan melapor **per id**: menggagalkan seluruh kiriman karena satu ide yang keburu diputuskan orang lain membuat komite mengulang pekerjaan yang sudah hampir selesai.

### Papan kepatuhan

Disusun dari potret peserta sebagai penyebut dan hitungan ide sebagai pembilang, lewat satu agregasi.

- Orang yang **belum mengirim apa pun tetap muncul** dengan angka nol. Papan yang disusun dari jawaban yang masuk saja justru menghilangkan orang yang paling perlu ditindaklanjuti — pelajaran yang sudah dibayar sekali di rekap per orang form penilaian.
- Kuota nol selalu terhitung terpenuhi.
- **Persentase disembunyikan** bila potretnya parsial atau pesertanya kosong. Angka dari penyebut yang salah lebih menyesatkan daripada tidak ada angka. Periode yang dokumennya belum ada sama sekali diperlakukan **parsial**, bukan "nol peserta", karena nol peserta terbaca seolah tak seorang pun diwajibkan.
- Export CSV menandai potret parsial lewat **header** `X-Kaizen-Participants-Partial`, bukan baris catatan di dalam berkas yang akan terbaca sebagai data oleh spreadsheet.

### Rute komite hidup di luar grup `/forms`

Prefix `/kaizen/*`, digerbang `requireEmployee` lalu diperiksa per-form oleh `loadCommitteeForm`. Grup `/forms` digerbang `requireFormManager` yang menuntut tingkat peran pengelola **dan** departemen aktif, sedangkan anggota komite ditunjuk HR dan bisa saja staf biasa dari departemen mana pun — menaruh rute ini di sana membuat komite tak pernah bisa membuka antreannya sendiri.

Komite = anggota yang terdaftar di `settings.kaizen.committee_employee_ids` **atau** siapa pun yang boleh mengelola departemen pemilik form. Butir kedua pengaman, bukan kelonggaran: tanpa itu salah isi daftar komite membuat program jadi yatim dan tak seorang pun bisa memperbaikinya.

**Seluruh permukaan komite dikunci `common.CompanyID`, bukan `EffectiveCompanyID`.** Override `?company=` milik admin pusat adalah lingkup baca, dan memutuskan nasib ide adalah menulis. Antrean dan papan ikut dikunci supaya yang dilihat dan yang bisa ditindak selalu sama; kalau berbeda, komite membaca daftar yang tombolnya justru menolak bekerja.

### `settings.kaizen` yang absen berarti "jangan diubah"

`PATCH /forms/:id` berperilaku ganti-seluruhnya. Untuk `title` itu wajar, untuk blok ini tidak: kehilangannya tak sekadar mengosongkan field melainkan **mengubah jenis form**. Satu kiriman tanpa `form_type` dan tanpa `settings.kaizen` akan mengubah program Kaizen yang masih draft jadi survei biasa, membuang kuota per departemen berikut seluruh daftar komite, tanpa satu pun galat.

Aturannya menyalin `SpaceType.Fields` di [[Microservices - Task Management Service]] yang juga membedakan "tidak dikirim" dari "dikosongkan". **Konsekuensi yang disengaja: tipe kaizen tak bisa diubah ke tipe lain lewat `PATCH`.** Itu bukan alur kerja nyata — satu perusahaan hanya punya satu program aktif, dan menghentikannya dilakukan dengan menutup form.

> [!warning] Cacat 502 yang ditemukan saat verifikasi, sudah diperbaiki di dev DAN prod
> **Setiap jalur galat rute kelola form memanik**, dan cacatnya sudah hidup jauh sebelum Kaizen ada. `GET /forms/<id-ngawur>`, `GET /forms/<id-yang-tak-ada>`, beserta `analytics`, `responses`, dan `export` semuanya membalas **502**.
>
> Sebabnya `loadManagedForm` mengembalikan `c.Status(...).JSON(...)` sebagai nilai galat. `c.JSON()` mengembalikan `nil` saat penulisan berhasil, jadi baris itu sebenarnya `return nil, nil`; penjaga `if errResp != nil` tak pernah menyala, eksekusi lanjut dengan form nil, lalu dereferensi pointer nil. Service tidak mati, koneksinya yang diputus, dan di belakang gateway itu terbaca 502.
>
> Diperbaiki PR [#1018](https://github.com/bip-itteam-internal/bip-erp/pull/1018) dengan mengganti tanda tangan jadi `(*Form, bool)`. **Terverifikasi di dev dan prod 2026-08-06**: id ngawur `400`, id sah tapi tak ada `404`, rute tak dikenal tetap `404`, jalur normal tetap `200`.
>
> **183 unit test tetap hijau selama cacat ini hidup**, karena semuanya fungsi murni dan tak satu pun melewati Fiber. Regresinya kini dikunci `handler_guard_test.go` memakai `app.Test`, tanpa database sama sekali. Pelajaran lintas-service ini dicatat di ingatan tim.

### Belum diverifikasi dan cacat yang diketahui

Tiga jalur yang tak bisa dijamin unit test dan baru terbukti setelah dijalankan: agregasi hitungan ide per orang, potret peserta yang memanggil employee-service dari cron, dan penjaga balapan yang bersandar pada `MatchedCount` dari driver Mongo.

Dua cacat yang sudah diketahui tapi sengaja belum diperbaiki:

- Menandai ide "diterapkan" padahal belum pernah diterima dibalas `400`, seharusnya `409`. Tak ada data yang rusak.
- `blocks_attendance` di `GET /me/forms` memakai `gateActiveAt` (tanggal statis), sedangkan gerbang sesungguhnya di `/internal/compliance` memakai `gateActiveForForm` (jendela periode). Pada form berulang ber-gerbang, aplikasi akan memberi tahu "kamu tidak ditahan" sementara attendance-service menahan clock-in. Laten selama belum ada form ber-mode `block` dan attendance-service masih pra-merge, tapi akan menggigit tepat pada hari service itu naik.

### Papan ide publik

> Merged ke `main` 2026-08-06 lewat PR [#1028](https://github.com/bip-itteam-internal/bip-erp/pull/1028). Rute `GET /me/kaizen/board`, cukup karyawan terautentikasi.

Yang menjaga isinya **bukan gerbang peran melainkan saringan status**: hanya ide `accepted` dan `implemented` yang tampil. Saringannya `$in` atas dua status itu, bukan "bukan pending", supaya ide yang **ditolak** juga tak pernah muncul. Ide yang masih ditinjau tak pernah tampil — menampilkannya berarti mempermalukan ide setengah matang di depan sekantor, dan itu cara tercepat membuat orang berhenti mengirim.

Jawaban yang boleh tampil ditentukan **daftar izin tipe field**, bukan daftar larangan. Papan dibaca seluruh karyawan, jadi tipe pertanyaan yang ditambahkan nanti (lampiran berkas, yang nilainya cuma id unggahan) **tersembunyi secara bawaan** sampai seseorang sengaja mengizinkannya. Daftar larangan bekerja sebaliknya: tipe baru bocor lebih dulu, dan ketahuannya setelah tampil di depan sekantor. Di atasnya masih ada `board_hidden_fields` per form untuk menyembunyikan key tertentu (perkiraan biaya, misalnya).

Dibatasi **100 kartu** terbaru. Papan berisi ribuan kartu tak dibaca siapa pun.

### Pengingat kuota berjenjang

Dikirim **H-7 dan H-2** sebelum periode ditutup, hanya kepada peserta yang jumlah idenya masih di bawah kuota. Isinya menyebut **angka** ("kurang 1 lagi dari 2") dan sisa hari: orang yang tak tahu kurang berapa akan menunda karena mengira pekerjaannya besar, dan dua pesan identik seminggu berturut-turut hanya melatih orang mengabaikannya.

**Penjaga kirim-ganda STRUKTURAL**, bukan pemeriksaan. Koleksi `ReminderLog` punya index unik `(form_id, period_key, employee_id, tag)`. Cron pembuka periode jalan **tiap jam**, dan pemeriksaan "sudah dikirim?" sebelum mengirim bisa kalah balapan — hasilnya orang yang sama dikirimi 24 kali sehari. Pola yang sama dipakai `ensurePeriod`. Penanda tahapnya (`h7`, `h2`) **tersimpan**, jadi mengubah ejaannya akan mengirim ulang seluruh pengingat periode berjalan.

Perbandingan jatuh temponya memakai **hari**, bukan detik, karena cron jalan tiap jam.

> [!success] Pengingat sempat TIDAK PERNAH SAMPAI — sudah diperbaiki dan dibuktikan
> Kategori inbox `kaizen-reminder` dan `kaizen-decided` sempat **tidak terdaftar** di `InboxCategories` (`shared-library/models/notification/models.go`). Notification-service memvalidasi kategori terhadap daftar itu dan membalas **`400`** untuk yang di luar daftar, sementara pengiriman di form-builder bersifat best-effort — kegagalannya hanya muncul di log. Jadi seluruh pengingat kuota dan pemberitahuan keputusan **hilang tanpa jejak**, sedangkan cron, papan kepatuhan, dan keputusan komite tampak bekerja normal.
>
> Ini **persis kegagalan yang sudah diperingatkan** di rencana tahap 5 [[HRIS - Kaizen (Ide Perbaikan)]], dan sudah pernah terjadi saat kategori `form-published` lahir. Terulang karena PR [#1028](https://github.com/bip-itteam-internal/bip-erp/pull/1028) menambah kategori di form-builder tanpa mendaftarkannya di shared-library.
>
> **Diperbaiki PR [#1044](https://github.com/bip-itteam-internal/bip-erp/pull/1044)** (2026-08-06). Penjaganya dipindah dari komentar ke **test**: `notify_category_test.go` menegaskan tiap konstanta kategori di `notify.go` lolos `IsInboxCategoryValid`, plus test kedua yang menjaga agar validatornya sendiri tak berubah jadi meloloskan apa pun. Penjaga itu **dibuktikan menyala**, bukan sekadar hijau — dengan kedua kategori dihapus sementara dari daftar, test gagal dan menyebut persis kategori yang bermasalah.
>
> ✅ **Terbukti sampai di dev 2026-08-06**: kotak masuk bertambah 71 → 72 dengan judul "Ide Kaizen Anda sudah diterapkan". Percobaan pertama, 4 menit setelah merge, **gagal total** — deploy dev belum mendarat. Itu sekaligus bukti bahwa **notification-service wajib ikut naik**: daftarnya ikut terkompilasi ke dalam biner, jadi container lama tetap menolak. Prosedurnya kini di [[RUN - Deploy Microservices bip-erp]] §3a.

### Setoran metrik ke KPI

> Merged ke `main` 2026-08-06 lewat PR [#1029](https://github.com/bip-itteam-internal/bip-erp/pull/1029).

`GET /internal/kaizen/metrics?period=YYYY-MM` membalas hitungan per orang: `submitted`, `accepted`, `implemented`. **Tiga angka, bukan satu**, karena matriks KPI memakai dua redaksi berbeda — sebagian menghitung ide yang diajukan, sebagian yang benar-benar diterapkan. Menggabungkannya berarti salah satu departemen dinilai dengan angka yang bukan miliknya.

Rutenya **menggerbang dirinya sendiri** ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]): identitas terkunci ke header, dan `?company=` hanya dihormati bila permintaan tak membawa identitas header sama sekali — ciri panggilan service-to-service. Tanpa aturan itu karyawan mana pun bisa mengintip hitungan perusahaan lain, persis kelas bug yang sudah ditutup di `/internal/compliance`.

Yang **menulis** `kpi_score` tetap [[Microservices - Employee Service]], sesuai [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]. Service ini hanya melaporkan angkanya. Di sisi employee-service ada dua sumber terdaftar, `kaizen_ide_diajukan` dan `kaizen_ide_diterapkan`, yang menarik lewat `FORM_BUILDER_MODULE_URL` (sudah ada di `docker-compose.yml`). `has_program:false` membedakan "perusahaan ini belum menjalankan programnya" dari "gagal mengambil data"; hanya yang kedua dilaporkan sebagai metrik gagal hitung.

### Permukaan karyawan: `/me/kaizen*`

> Merged ke `main` 2026-08-06 lewat PR [#1034](https://github.com/bip-itteam-internal/bip-erp/pull/1034).

`GET /me/kaizen` (program berjalan + progres kuota) dan `GET /me/kaizen/ideas` (riwayat ide sendiri lintas periode, berhalaman, membawa keputusannya).

**Terpisah dari `/me/forms` dengan sengaja.** Program Kaizen bukan "satu form lagi" bagi pengisinya: berulang tiap periode, berkuota, punya riwayat keputusan, dan idenya dibaca orang lain di papan. Menumpangkan semua itu ke daftar survei berarti satu kartu yang harus menjelaskan lima hal sekaligus. [[APP - MyBharata]] menampilkannya di **menu tersendiri**.

`/me/forms` ikut mengirim **`form_type`** supaya klien bisa mengecualikan program Kaizen dari daftar survei. Dokumen lama tak punya field itu dan dijawab `survey`: klien tak boleh bergantung pada urutan deploy, karena di jeda sebelum backfill jalan, klien yang menyaring berdasarkan tipe akan menjatuhkan form lama dari **semua** daftar dan formnya lenyap tanpa satu pun galat. Nilai **asing diteruskan apa adanya**, bukan disamarkan jadi `survey` — validator sudah menolaknya di jalur tulis, dan menyamarkan data yang tak dikenal membuat penyebabnya mustahil ditelusuri.

Bukan sasaran program dibalas `has_program:false`, **bukan `404`**: menu Kaizen tetap bisa dibuka dan menjelaskan keadaannya alih-alih menampilkan layar galat untuk keadaan yang sebenarnya normal.

✅ **Gerbang presensi ikut di `/me/kaizen`** (`blocks_attendance`, `gate_end_date`) sejak PR [#1039](https://github.com/bip-itteam-internal/bip-erp/pull/1039). Perlu karena form Kaizen dikeluarkan dari daftar survei di mobile: tanpa field ini, karyawan yang tertahan clock-in tak punya satu pun petunjuk di layar — kartunya tak ada lagi di beranda, dan menu Kaizen tak tahu ada gerbang yang menyala. Perhitungannya sama persis dengan `/me/forms`, termasuk `gateActiveAt`.

### Penemuan program untuk komite

> Merged ke `main` 2026-08-06 lewat PR [#1046](https://github.com/bip-itteam-internal/bip-erp/pull/1046), live dev + prod.

`GET /me/kaizen/committee` menjawab pertanyaan yang sebelumnya **tak punya jawaban sama sekali**: "program Kaizen mana yang boleh saya tinjau?"

Seluruh rute komite menuntut id form, dan satu-satunya cara menemukannya adalah `GET /forms` — yang digerbang `requireFormManager`, menuntut peran pengelola DAN departemen aktif. Anggota komite ditunjuk HR dan bisa saja staf biasa dari departemen mana pun, jadi **persis orang yang butuh justru dibalas `403`**. Sebelum endpoint ini, komite hanya bisa membuka antreannya bila ada yang mengirimkan URL-nya secara manual, dan layar komite di [[APP - Web ERP]] praktis tak terjangkau.

Ada di grup `/me` (cukup karyawan terautentikasi), BUKAN `/kaizen` maupun `/forms`: rute ini justru harus bisa dipanggil orang yang haknya **belum diketahui** — itu memang pertanyaannya.

Bukan komite dibalas `is_committee:false`, **bukan `403`**, supaya menunya menjelaskan keadaannya sendiri. "Tak ada program" dan "bukan tugas saya" sengaja tak dibedakan, sama seperti `has_program`: bagi pemakai ujungnya sama, dan membedakannya membocorkan keberadaan program ke orang di luar komite. Gerbangnya memakai predikat `isKaizenCommittee` yang sama persis dengan `loadCommitteeForm`, supaya menu tak pernah muncul untuk orang yang tombolnya justru menolak bekerja.

## Lampiran berkas (tipe field `file`)

> PR [#1023](https://github.com/bip-itteam-internal/bip-erp/pull/1023) + [#1057](https://github.com/bip-itteam-internal/bip-erp/pull/1057), ✅ **live dev + prod 2026-08-06 dan TERUJI end-to-end di dev**. Berlaku **semua tipe form**, bukan cuma Kaizen.

**Unggah dulu, kirim jawaban kemudian.** Satu jawaban dikirim sebagai satu JSON, jadi berkas tak bisa ikut di dalamnya. `POST /me/forms/:id/uploads` (multipart) membalas `upload_id`, dan id itulah yang jadi **nilai jawaban** untuk field bertipe `file`.

Berkasnya sendiri tinggal di [[Microservices - File Service]] dengan prefix **`form/`**; service ini hanya menyimpan penunjuknya di koleksi `form_uploads`.

**Berkas yatim dibersihkan cron harian 03:00** — unggahan yang pengisiannya tak pernah diselesaikan. Harian, bukan tiap jam: batas umurnya 24 jam, jadi memeriksanya lebih sering hanya membaca koleksi yang sama tanpa temuan. Jam 3 pagi karena penghapusan objek memanggil file-service satu per satu.

**`FILE_MODULE_URL` dan `MINIO_FORM_KEY` dibaca `os.Getenv` langsung, di luar map `InternalURL`.** `ValidateInternalURL` panic pada entri kosong, jadi menaruhnya di sana berarti seluruh service mati — termasuk gerbang presensi dan pengisian form biasa — hanya karena env satu fitur belum diisi. Selama env belum ada, unggahan gagal dengan pesan "file-service belum dikonfigurasi" sementara sisa service tetap jalan.

**Export CSV menulis path preview, bukan presigned URL**: presigned URL kedaluwarsa dalam hitungan menit sementara berkas export dibaca berhari-hari kemudian.

### Hasil uji end-to-end di dev (2026-08-06)

| Langkah | Hasil |
|---|---|
| `POST /me/forms/:id/uploads` | `201`, membalas `{file_name, size, upload_id}` |
| Kirim jawaban memakai `upload_id` | OK |
| `GET /me/uploads/:id/preview` | `200`, presigned URL ke `app-bucket/`**`form/`**`<id>.txt` |
| `upload_id` karangan (kontrol negatif) | `404` |

Objeknya benar-benar mendarat di prefix `form/` — bagian yang paling mungkin diam-diam salah. Data ujinya dihapus dan diverifikasi bersih.

> Percobaan pertama dibalas `403`, dan itu **benar**: skrip ujinya salah membaca `employee_id` (respons `/api/employee/me` datar, bukan bersarang di `data`), sehingga formnya menyasar daftar kosong dan pemanggil memang bukan sasarannya sendiri.

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

> [!warning] `FormPeriod.Fields` ditulis tapi TIDAK PERNAH dibaca
> Snapshot pertanyaan per periode dibuat `ensurePeriod` dan didokumentasikan di kodenya sebagai penjaga keabsahan pembanding antar-bulan, dengan janji "pemilik form boleh menyunting pertanyaan kapan saja, dan perubahannya berlaku mulai periode BERIKUTNYA".
>
> **Janji itu tidak ditepati siapa pun.** Jalur pengisian menyajikan dan memvalidasi dari `form.Fields`, bukan dari snapshot; pencarian `Collections.Periods` menunjukkan koleksi itu hanya ditulis (`period_store.go`, `cron.go`) dan tak pernah dibaca oleh handler mana pun. Snapshotnya menganggur.
>
> Yang benar-benar menjaga konsistensi adalah kunci `409` di `updateForm`, dan kunci itu **tidak memedulikan apakah form berulang**: begitu ada satu jawaban masuk, susunan pertanyaan terkunci selamanya. Untuk survei bulanan yang hidup bertahun-tahun, artinya pemiliknya tak akan pernah bisa memperbaiki satu pun pertanyaan.
>
> Perbaikannya punya urutan yang **tidak boleh dibalik**: jadikan snapshot penopang beban lebih dulu, baru longgarkan kuncinya. Dijadwalkan sebagai tahap 1 pekerjaan [[HRIS - Kaizen (Ide Perbaikan)]].
>
> **"Penopang beban" mencakup TIGA jalur, bukan dua.** Selain menyajikan (`GET /me/forms`) dan memvalidasi (`POST /me/forms/:id/responses`), **analisa dan export juga wajib memakai snapshot periode yang diminta**. Tanpa yang ketiga, melonggarkan kunci hanya memindahkan kerusakan dari jalur tulis ke jalur baca: begitu pertanyaan disunting untuk bulan depan, rekap bulan LAMPAU dihitung terhadap daftar pertanyaan yang tak pernah dilihat pengisinya, jawaban yang key-nya sudah hilang lenyap dari rekap, dan pertanyaan baru muncul sebagai "tidak dijawab" oleh semua orang. Tak ada galat, hanya angka salah yang tetap tampak masuk akal. Versi pertama catatan ini menyebut dua jalur saja, dan kekurangan itu sempat lolos sampai review.
>
> Batas yang tersisa: `?period=` kosong berarti rekap **seluruh** periode, dan di sana memang tak ada satu susunan pertanyaan yang benar karena jawabannya bisa berasal dari beberapa susunan berbeda. Yang dipakai adalah susunan terbaru milik form.

- **Kuartalan dan tahunan belum ada** pada form berulang, sengaja: belum ada kasus nyatanya, dan menambahkannya sekarang berarti menebak bentuk yang benar.
- **Kiriman sebelum `open_day` tetap diterima.** `windowFor` mengembalikan `active=false` sebelum hari buka, tapi `submitResponse` **membuang** nilai itu dan hanya memakai penandanya, sehingga jawaban yang masuk lebih awal tetap tersimpan atas periode berjalan. Gerbang presensi justru menghormati `active` lewat `gateActiveForForm`. Jadi pada rentang itu form belum menahan siapa pun tapi sudah bisa diisi. Belum tentu salah (survei yang dibuka lebih awal tidak merugikan), tapi ketidaksamaan kedua jalur ini **belum pernah diputuskan**, cuma terjadi.
- **Jumlah PENGISI tidak dihitung otomatis.** Untuk `audience` bertipe `all`/`departments`, penyebut tingkat pengisian tetap memakai `audience.estimated_size` yang diisi manual pembuat form. Bila kosong, tingkat pengisian **tidak dilaporkan** (menampilkan 0% lebih menyesatkan daripada tak menampilkan apa pun). Berbeda dari `subject`, yang JUSTRU di-resolve otomatis dari employee-service saat terbit — sumbu yang dinilai butuh nama dan jabatan, sedangkan sumbu pengisi cukup dicocokkan dari header.
- **Agregasi dibatasi 20.000 jawaban.** Bila terlampaui, total sebenarnya tetap dilaporkan dan hasil ditandai `truncated` + `sample_size`, sedangkan tingkat pengisian disembunyikan. Export menandai lewat header `X-Export-Truncated`.
- **`attendance_gate.start_date`/`end_date` hanya menerima RFC3339** (mis. `2026-08-01T00:00:00Z`); kiriman `"2026-08-01"` akan ditolak dengan pesan parse JSON yang tidak informatif. Perlu dibereskan saat FE dibangun.
- ⚠️ **RBAC berkatalog permission-set: fase satu live di dev DAN prod, tapi belum satu jabatan pun dipasangi paket.** Modul `formbuilder` beserta tiga izin dan tiga paket merged & di-deploy 2026-08-10 (PR [#1138](https://github.com/bip-itteam-internal/bip-erp/pull/1138)). Sampai paket benar-benar dipasang lewat layar Hak per Posisi, seluruh akses masih ditentukan tier lama lewat fallback, jadi [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] **belum** terpenuhi untuk modul ini. Memasang paketnya adalah keputusan HR, bukan langkah rilis. Rancangan + alasan cakupan departemen tak ikut pindah ke `reach`: §Izin: katalog `formbuilder` di atas.
- **Fase dua belum dinyalakan.** `FORMBUILDER_TIER_FALLBACK` tak diset di lingkungan mana pun, jadi bawaannya menyala. Mematikannya sebelum paket terpasang akan mencabut akses SELURUH pengelola form sekaligus. Prasyaratnya sama untuk semua modul berkatalog dan dilacak di [[CORE - RBAC dan Permission Set]].
- **Cakupan departemen belum bisa dibatasi lewat paket.** Konsekuensi langsung dari keputusan di atas: `reach: division` tak punya penegak di modul ini, jadi paket yang disetel "divisi sendiri" akan berperilaku persis "semua departemen". Bila pembatasan itu memang dibutuhkan, yang harus dibangun adalah penegaknya, bukan nilai di layar.
- ✅ **Section/multi-halaman sudah ada** (PR [#870](https://github.com/bip-itteam-internal/bip-erp/pull/870)).
- ✅ **Keterangan ujung skala sudah ada** (PR [#871](https://github.com/bip-itteam-internal/bip-erp/pull/871)).
- ✅ **Upload file SUDAH ada** — tipe `file` terdaftar di `knownFieldTypes`, dengan `POST /me/forms/:id/uploads` dan dua rute pratinjau. Butir ini sempat berbunyi "belum ada" jauh setelah fiturnya mendarat; diperbaiki 2026-08-10.
- **Percabangan, grid, dan opsi "Lainnya" belum ada** — jarak yang tersisa terhadap Google Forms. Urutan yang disarankan: opsi "Lainnya" (murah) → percabangan. Percabangan menuju bagian, jadi kini sudah punya landasannya.
- **Nilai per opsi pada `radio`/`dropdown` belum ada**, dan itulah yang menahan keduanya keluar dari skor gabungan. `Options` masih `[]string` polos. Menurunkan nilai dari URUTAN opsi sudah ditolak eksplisit: skornya terbalik total begitu ada pembuat form yang menuliskan "Sangat Baik" lebih dulu, tanpa satu pun tanda di layar.
- **Analisa belum mengelompokkan hasil per bagian.** Yang dijamin sekarang hanya bagian tak muncul sebagai kartu kosong; pengelompokan visualnya polesan yang belum dikerjakan.
- **Form approval yang sudah matang JANGAN dimigrasikan ke sini** (leave/overtime/koreksi presensi) — semuanya punya workflow & rantai approval sendiri. Form Builder untuk kasus baru/ad-hoc.

## Dependensi & Integrasi

- **MongoDB** `form_builder_db` — koleksi `forms`, `form_responses`, `form_periods`, `kaizen_reminder_logs`. Index dibuat idempoten saat boot; `(form_id, period_key)` di `form_periods` **unik**, dan keunikan itulah yang membuat pembuatan periode oleh cron aman tanpa lock. Index unik `(form_id, period_key, employee_id, tag)` pada catatan pengingat memainkan peran yang sama untuk pengingat kuota. Lihat [[DB - Overview and Notes]].
- [[IT - Background Jobs & Schedulers]] — cron pembuka periode form berulang, tiap jam, zona `Asia/Jakarta`; cron yang sama memotret peserta Kaizen dan mengirim pengingat kuota H-7/H-2.
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
- [[HRIS - Kaizen (Ide Perbaikan)]] — ⚠️ konsep & keputusan bisnis; menumpang service ini sebagai `form_type` tersendiri
- [[IT - Background Jobs & Schedulers]] — cron pembuka periode
- [[Microservices - Attendance Service]] · [[CORE - API Master Gateway]] · [[DB - Overview and Notes]]
- [[Microservices - Employee Service]] — penarik metrik Kaizen ke `kpi_score`
- [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]
- [[APP - Web ERP]] · [[APP - MyBharata]] — klien

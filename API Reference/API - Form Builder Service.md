## Deskripsi

*Endpoint **form-builder-service** (form dinamis + analisa jawaban + kepatuhan presensi). Gateway: `/api/form-builder/*`. Kelola form butuh **tingkat peran** `staff`/`supervisor`/`admin` di modul mana pun DAN departemen pemanggil ada di daftar departemen aktif; mengisi cukup terautentikasi. Grounded ke `services/form-builder/routes.go` + handler terkait (`main`, PR #849; kepemilikan per departemen PR #869).*

- **Status**: ⚠️ Implemented (live di dev **dan prod** sejak 2026-08-01; **penilaian karyawan, tipe form, dan rekap per orang dinilai** merged 2026-08-02 lewat PR #907 + #908 — **live di dev DAN prod** sejak 2026-08-02). **Form berulang** (`recurrence`, `period_key`, `?period=`) merged ke `main` 2026-08-03 lewat PR #938, #940, #942 — **setelah** deploy prod 08-01/08-02, jadi **status prod belum diverifikasi**. Baru didokumentasikan 2026-08-06 dan belum punya catatan uji end-to-end.
- **Indeks layanan departemen** (`metric_key`, `settings.anonymous`, rute `/me/service-index`) ⚠️ **merged ke `main` 2026-08-25** lewat PR [#1417](https://github.com/bip-itteam-internal/bip-erp/pull/1417); perbaikan hasil review menyusul di PR [#1418](https://github.com/bip-itteam-internal/bip-erp/pull/1418) (lingkup baca `EffectiveCompanyID`, indeks unik parsial, `settings.anonymous` jadi pointer). **Belum di-deploy dan belum diuji lewat gateway** — jalur sukses endpoint dan bentuk `has_form:false` menyentuh Mongo sehingga test-nya melewatkan diri tanpa database. Konsumennya kartu Indeks Layanan IT di [[APP - Web ERP]] (erp-frontend [#1205](https://github.com/bip-itteam-internal/erp-frontend/pull/1205), [#1206](https://github.com/bip-itteam-internal/erp-frontend/pull/1206)).
- **Kaizen** (`form_type: "kaizen"`, rute `/kaizen/*`, `/me/kaizen*`, `/internal/kaizen/metrics`) ✅ **live dev + prod** sejak 2026-08-06 lewat PR #1016, #1028, #1029, #1034, #1039, #1044, #1046 — seluruhnya teruji end-to-end di dev. Belum ada satu pun form kaizen di prod, jadi masih inert.
- **Inspeksi Satgas 5R & K3** (`metric_key: inspeksi_satgas`, gerbang izin `kepatuhan.satgas.input` di jalur isi, `metric_key` di `/me/forms`, rute `/me/satgas`) ⚠️ **merged 2026-09-11** lewat PR [#1849](https://github.com/bip-itteam-internal/bip-erp/pull/1849); biner form-builder dev memuatnya (diukur 2026-09-11), **gerbang Satgas belum diuji lewat gateway**. `file_fields` pada respons analytics merged 2026-09-11 lewat bip-erp PR [#1852](https://github.com/bip-itteam-internal/bip-erp/pull/1852) dan ✅ **terverifikasi lewat gateway dev** hari yang sama; prod belum. Keputusan: [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]].
- **Nilai Satgas per orang dan cek ulang lintas bulan** (T3 ADR 0090: `GET /internal/satgas/metrics`, `period_key` opsional pada kirim jawaban dan unggah, kartu cek ulang di `/me/satgas`, `subject_rule` di analytics) ⚠️ **selesai di branch 2026-09-12, belum PR, belum merge, belum deploy**: bip-erp `feat/satgas-nilai-kpi`, lalu `feat/satgas-cek-ulang` yang bertumpu padanya. Butir bertanda *(T3, branch)* di dok ini belum ada di `main`.
- **Implementasi**: [[Microservices - Form Builder Service]]
- **Indeks**: [[API - Index]]
- **Konsumen**: seluruh rute `/forms*` — termasuk `analytics`, `responses`, `export` — dipakai [[APP - Web ERP]]. Rute **`/me/*`** dipakai [[APP - MyBharata]] (section Survei di beranda + halaman pengisian), dan **`/me/kaizen*`** dipakai menu Kaizen tersendiri di aplikasi itu.

## Sistem
| Method | Path | Fungsi |
|---|---|---|
| GET | `/health` | Health check (di belakang gateway key) |

## Kelola Form (RBAC per departemen)
| Method | Path | Fungsi |
|---|---|---|
| POST | `/forms` | Buat form (lahir `draft`; owner wajib dalam cakupan pemanggil, ejaannya **dikanonikkan** ke daftar departemen aktif). `owner_departments[]` opsional untuk kepemilikan bersama (lihat catatan 🔜 di bawah) |
| GET | `/forms` | Daftar form yang **salah satu owner-nya** dalam cakupan pemanggil (`?status=`, `?form_type=`, `?search=`, `?page=`, `?limit=` maks 100). Tiap item membawa `form_type`, `response_count` (jumlah jawaban) dan `respondent_count` (jumlah ORANG) |
| GET | `/forms/:id` | Detail + `response_count` |
| PATCH | `/forms/:id` | Sunting. `409` bila susunan field diubah padahal sudah ada jawaban (**berlaku juga untuk form berulang**, lihat catatan di bawah). `409` juga bila `recurrence` **dinyalakan** pada form yang sudah punya jawaban; mematikannya tetap boleh. `owner_department` tak bisa dipindah |
| PATCH | `/forms/:id/status` | `draft`→`published`→`closed`. `409` bila mencoba mundur dari `published` ke `draft`. Saat terbit: **memotret sasaran penilaian** (`422` bila gagal, kosong, atau >300 orang) lalu mengirim notifikasi inbox ke seluruh sasaran |
| DELETE | `/forms/:id` | Hapus lunak (`deleted_at` + status `closed`) |

> **Cakupannya departemen, bukan modul.** Diambil dari `common.SupervisedDepartments` (departemen sendiri + yang dibawahi lewat `master_department.supervised_by`) lalu diiris daftar departemen aktif. SPV HRGA karena itu melihat form Human Resource **dan** General Affair, tapi tidak Tech Development. Daftar aktifnya konfigurasi `FORM_BUILDER_DEPARTMENTS`; bila kosong dipakai bawaan `Human Resource, General Affair, Tech Development`.

> [!note] 🔜 Kepemilikan bersama (`owner_departments[]`) — branch `feat/formbuilder-owner-jamak`, terverifikasi lokal, **belum merge/deploy**
> Sebuah form bisa dimiliki beberapa departemen supervisi sekaligus. `POST /forms` menerima `owner_departments[]` (SEMUA wajib dalam cakupan pembuat; satu yang bukan → `403`). `owner_department` = elemen pertama, dikirim juga untuk klien lama. **Lihat** = cakupan pembaca mengandung salah satu owner; **tulis** (sunting/hapus/terbit) = pembaca mengelola salah satu owner. `GET /forms` menyaring `owner_departments $in cakupan` dengan fallback `$or` ke `owner_department` untuk dokumen lama. Tipe form harus boleh dibuat **SEMUA** owner (irisan, [[ADR - 0041 Izin Tipe Form Menempel di Departemen]]). Konsekuensi sadar: analisa form yang dibagikan terbaca staf tiap departemen pemilik. Detail: [[Microservices - Form Builder Service]].

## Aturan Tipe Form per Departemen (khusus IT)

> ✅ **LIVE dan teruji end-to-end lewat gateway di dev DAN prod** (prod deploy manual + uji 2026-08-09). Merged 2026-08-08 (BE [#1099](https://github.com/bip-itteam-internal/bip-erp/pull/1099), FE [erp-frontend#866](https://github.com/bip-itteam-internal/erp-frontend/pull/866)). Keputusan: [[ADR - 0041 Izin Tipe Form Menempel di Departemen]].

Digerbang `system_roles["it"]` tingkat `supervisor`/`admin` — **kunci MODUL, bukan nama departemen** `"Tech Development"`. `staff` ditolak. Grupnya sengaja di luar `/forms` karena yang menetapkan aturan adalah IT untuk departemen yang bukan miliknya.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/form-type-rules` | Aturan **seluruh** departemen aktif, termasuk yang belum diatur (`blocked_types: []`). Membawa juga `form_types` (daftar tipe master) supaya klien tak pernah menyalinnya |
| PUT | `/form-type-rules/:department` | Tetapkan `{blocked_types[]}`. **PUT, menimpa penuh** — layarnya memang mengirim seluruh keadaan centang. `400` bila ada nilai di luar tipe dikenal (pesannya menyebut nilainya) atau departemen di luar daftar aktif |

Membuat form atau mengganti tipenya pada form `draft` dibalas **`403`** bila tipe itu dilarang untuk departemen pemiliknya; pesannya menyebut departemen, tipe, dan arahan menghubungi IT. Menyunting form yang **sudah** bertipe terlarang tetap boleh — lihat [[Microservices - Form Builder Service]] untuk alasannya.

Jalur tulis dikunci `common.CompanyID`, bukan `EffectiveCompanyID`: `?company=` milik admin pusat adalah lingkup baca.

## Kelola Template Form (cetakan reusable)

> ⚠️ **Branch `feature/workspace-position`**, terverifikasi lokal/DEV, **belum merge ke `main`, belum di prod.** Keputusan: [[ADR - 0065 Template Form Generik untuk Realisasi Program (Culture)]].

Template = **cetakan** form yang bisa dipakai berulang; ia **TIDAK menerima jawaban**. Koleksi Mongo baru `form_templates` (`Collections.Templates`). Grup digerbang `requireFormManager`; jalur tulis juga `requireFormWriter`.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/form-templates` | Daftar template (`?status=active\|archived`, `?form_type=`, `?search=`) |
| GET | `/form-templates/:id` | Detail satu template |
| POST | `/form-templates` | Buat template |
| PUT | `/form-templates/:id` | Sunting template |
| DELETE | `/form-templates/:id` | **Hard delete** — form yang sudah di-instantiate dari template ini **tetap ada** |
| POST | `/form-templates/:id/instantiate` | Buat `Form` **draft** dari template (salin `fields` + `form_type` + `default_recurrence`, set `template_id`), balas form. Form lahir `draft` lalu diterbitkan lewat jalur `PATCH /forms/:id/status` biasa — **tak melewati gerbang penerbitan tersendiri** |

**Struct `FormTemplate`** (`models_template.go`): `name`, `description`, `form_type`, `fields[]`, `default_recurrence`, `default_audience`, `target_department`, `target_position`, `slug`, `status` (`active`/`archived`), `created_by`, timestamps. **Field disalin (bukan dirujuk)** ke `Form` saat instantiate, jadi menyunting template tak mengubah arti jawaban form yang sudah terbit.

> Template ini semula dibangun untuk realisasi program Culture, di-seed saat boot. **Seed itu (`seed_culture.go`) sudah dihapus**: Culture kini punya modul sendiri (bawah). Kapabilitas template tetap ada, tanpa konsumen aktif.

## Kelola Program Culture (jabatan Culture & Industrial)

> ⚠️ **Branch `feature/workspace-position`**, terverifikasi lokal/DEV, **belum merge ke `main`, belum di prod.** Menggantikan pendekatan seed-form. Keputusan: [[ADR - 0066 Modul Kelola Program Culture]]. Konteks: [[Microservices - Form Builder Service]].

Grup `/culture/*` digerbang **`requireEmployee`** (cukup karyawan terautentikasi): officer mengelola programnya sendiri, peserta menilai lewat **link per-program**. Koleksi `culture_programs` + `culture_feedback`.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/culture/employees` | Daftar karyawan aktif untuk pemilih target (ditarik dari employee-service via `EMPLOYEE_MODULE_URL`) |
| GET | `/culture/programs` | Daftar program milik pemanggil; pengelola form boleh `?scope=all` (seluruh perusahaan). `?period=YYYY-MM`. Tiap baris membawa `hadir` (responden) |
| POST | `/culture/programs` | Buat program (`nama`, `pilar`, `jenis`, `target_departemen`/`target_karyawan` sesuai jenis, `tanggal`, `jam_mulai`/`jam_selesai`). `target` **di-resolve otomatis** dari jenis, bukan diketik. `tipe` **disalin dari master**, bukan dari klien |
| PUT | `/culture/programs/:id` | Sunting program milik sendiri |
| DELETE | `/culture/programs/:id` | Hapus program milik sendiri (feedback yatim ikut dibuang) |
| GET | `/culture/feedback/programs` | Program aktif untuk dinilai (`?period=`) |
| GET | `/culture/feedback/program/:id` | Info satu program untuk halaman penilaian (dibuka lewat link `?program=<id>`) |
| POST | `/culture/feedback` | Kirim penilaian peserta (`program_id`, `rating` 1–5, `masukan?`). Satu per `(program, responden)` — upsert |
| GET | `/culture/summary` | Ringkasan dashboard (`?period=`, `?scope=all`): rata-rata partisipasi/antusiasme/komposit, distribusi per pilar **atomik** (`pecahPilar`), daftar program terhitung |

**`jenis` → `target` (penyebut partisipasi), di-snapshot saat simpan**: `internal` = seluruh karyawan aktif · `department` = jumlah staf `target_departemen` · `employees` = jumlah `target_karyawan` (dedup). Jenis `club`/`public` menyusul (TBD).

**`tipe` (`event` | `non_event`)** — [[ADR - 0093 Tipe Program Culture Non-Event Dinilai Terlaksana dengan Approval SPV HR, plus Jadwal di Master]]. Sumbu **berbeda** dari `jenis` (resolve target) dan `pelaksanaan` (frekuensi), **disalin master→program** (klien tak dipercaya); dokumen lama tanpa `tipe` dibaca `event` (tanpa migrasi). Status: T1 (field) **merged ke `main`** (PR #1861); **T2–T5** ⚠️ branch `feat/culture-tipe`, belum merge/prod.
- **Event**: seperti di atas — target di-resolve, kehadiran scan, rating → komposit 30/30/40.
- **Non-event** (mis. Kamis Batik): tanpa undangan/kehadiran/rating. `POST /culture/programs` **melewati** resolusi target & `scan_token`, `tanggal` **opsional**. Officer menandai pelaksanaan lewat `/culture/programs/:id/terlaksana` (bawah); skornya **100 bila ada tanda `approved` pada periode, selain itu 0** (`skorNonEvent`, satu tempat). **Tak tampil di alur rating peserta** (`/culture/feedback/*` menyaring `tipe != non_event`).

**Master menyimpan jadwal berulang acuan** (⚠️ branch, T2): `jadwal_hari` (0–6, konvensi getDay) untuk `pelaksanaan=mingguan`, `jadwal_tanggal` (1–31) untuk `bulanan`. Opsional; hanya **pra-isi tanggal** saat membuat program (dihitung FE), TIDAK membangkitkan sesi.

### Terlaksana non-event & approval (⚠️ branch `feat/culture-tipe`, ADR 0093)

Koleksi `culture_terlaksana`: tanda pelaksanaan program **non-event** yang menunggu keputusan SPV HR. Hanya tanda `approved` yang membuat program terhitung 100 pada periodenya.

| Method | Path | Gerbang | Fungsi |
|---|---|---|---|
| POST | `/culture/programs/:id/terlaksana` | pemilik program | Officer menandai program non-event terlaksana (`tanggal?`, `catatan?`) → status `pending`. Ditolak `400` bila program `event` |
| GET | `/culture/programs/:id/terlaksana` | pemilik program | Riwayat tanda satu program |
| GET | `/culture/terlaksana/pending` | `requireCultureManager` | Antrean approval SPV HR: seluruh tanda `pending`, diperkaya nama+pilar program |
| PUT | `/culture/terlaksana/:id` | `requireCultureManager` | Keputusan SPV HR (`status`: `approved`\|`rejected`). Transisi **atomik** (filter `status=pending`); yang sudah diputus balas `409` |

⚠️ **Loop approval belum bernotifikasi** (SPV HR tak dikabari saat pending, officer tak dikabari saat diputus) — follow-up terpisah, belum dikerjakan.

**Skor komposit blueprint 30/30/40, otomatis** (`hitungSkorProgram`, satu tempat): Partisipasi 30% + Antusiasme 30% + Implementasi 40%, dengan **Implementasi = Partisipasi × Antusiasme ÷ 100** (dihitung, bukan diisi). KPI officer = rata-rata skor programnya. Detail konsep: [[Microservices - Form Builder Service]].

## Analisa & Export (RBAC per departemen)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/forms/:id/analytics` | Rekap per pertanyaan + tren harian + tingkat pengisian (lihat bentuk respons di bawah). `?period=` menyaring satu putaran form berulang |
| GET | `/forms/:id/responses` | Daftar jawaban berhalaman (`?page=`, `?limit=` maks 200), terbaru dulu. `?period=` |
| GET | `/forms/:id/export` | CSV (`text/csv`). Header `X-Export-Truncated` muncul bila menyentuh batas 20.000 baris. `?period=` |

> **`?period=` kosong berarti SELURUH periode di sini**, dan itu KEBALIKAN dari arti periode kosong pada penjaga duplikat saat mengisi (di sana kosong berarti "hanya jawaban yang memang tak punya periode"). Pemilik form yang membuka halaman analisa tanpa memilih periode mengharapkan rekap penuh, bukan rekap yang diam-diam menyusut.

> **Kolom dan kartu analisa mengikuti pertanyaan PERIODE yang diminta**, bukan susunan terbaru milik form. Keduanya bisa berbeda karena pertanyaan form berulang boleh disunting untuk periode berikutnya. Tanpa `?period=`, yang dipakai adalah susunan terbaru — pada rentang banyak periode memang tak ada satu susunan yang benar.

## Pengisian (karyawan terautentikasi)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/me/capability` | `{can_manage, can_write, can_manage_type_rules, departments[], form_types_by_department{}}` — apa yang boleh dilakukan pemanggil di Form Builder. `can_write` lahir bersama katalog izin (PR [#1138](https://github.com/bip-itteam-internal/bip-erp/pull/1138), merged & live di dev **dan prod** 2026-08-10): pemegang paket "Lihat" membuka layarnya (`can_manage`) tapi tak boleh membuat atau menyunting form (`can_write`). Selama fase satu nilainya selalu sama dengan `can_manage` |
| GET | `/me/forms` | Form terbit yang ditujukan ke pemanggil (+`owner_department`, `form_type`, `submitted`, `blocks_attendance`, `gate_end_date`). Form penilaian ikut membawa `subject_enabled`, `subject_total`, `subject_done`, `subject_anonymous`. Pada form berulang, `submitted` dihitung terhadap **periode berjalan**, dan form yang putarannya **belum buka tidak muncul sama sekali**. ⚠️ *(Satgas, merged #1849, deploy belum diukur)* Tiap entri membawa **`metric_key`** (kosong = form biasa; `inspeksi_satgas` = form Satgas yang dikeluarkan klien dari daftar survei), dan form Satgas **tak muncul** bagi yang tak memegang `kepatuhan.satgas.input` |
| GET | `/me/forms/:id/subjects` | Daftar orang yang harus DINILAI pemanggil + `progress{done,total,anonymous}`. `409` bila form tak menilai siapa pun. ⚠️ *(Satgas, merged #1849)* `403` berpesan pada form Satgas bila tak memegang izin |
| POST | `/me/forms/:id/responses` | Kirim jawaban (+`subject_employee_id` untuk form penilaian). `403` bila bukan sasaran atau menilai orang di luar daftar, `409` bila form tak `published`, orang itu sudah dinilai, **atau putaran form berulang belum dibuka**. Balas `subject_done`, `subject_total`, `all_completed`. ⚠️ *(Satgas, merged #1849)* `403` berpesan pada form Satgas bila tak memegang izin; kiriman form Satgas tak memicu notifikasi "selesai". ⚠️ *(T3, branch)* Menerima **`period_key`** opsional (kosong = periode berjalan, perilaku lama); bulan lalu pada form Satgas = cek ulang. `period_key` yang tak diterima dibalas `400` atau `409` berpesan, dan balasan `201` ikut membawa `period_key` tempat kiriman dicatat. Aturannya di bagian Inspeksi Satgas di bawah |
| GET | `/me/satgas` | ⚠️ *(Satgas, merged #1849, deploy belum diukur)* Menu Satgas 5R & K3 untuk MyBharata. Tanpa izin `200 {allowed:false, forms:[]}`; dengan izin `200 {allowed:true, forms:[...]}` berisi ringkasan per PIC. Rincian di bagian di bawah |
| GET | `/me/responses` | Riwayat jawaban sendiri |
| GET | `/me/service-index` | **Indeks layanan sebuah departemen** pada satu bulan. `?department=` dan `?period=YYYY-MM` **keduanya wajib**. Balas `{has_form, form_id, title, department, period_key, index, scored_questions, respondents, audience_size, coverage_pct, aspects[], unweighted[]}` |
| POST | `/me/forms/:id/uploads` | Unggah satu lampiran (**multipart**, field **`file`**; `field_key` tak dibaca, dan berkas baru dicocokkan ke pertanyaannya saat jawaban dikirim; diperiksa ke `uploads.go` 2026-09-12. Di `main` hanya field itu yang dibaca. ⚠️ *(T3, branch)* Field **`period_key`** opsional ikut dibaca dengan aturan yang sama dengan kirim jawaban, dan wajib sama dengan `period_key` jawabannya: lampiran periode lain ditolak `400` saat jawaban dikirim). `201` membalas `{"data": {upload_id, file_name, size}}`. `400` bila field `file` tak ada. Cap 4 MB milik file-service; `413 {"error": "Ukuran berkas melebihi batas 4 MB"}` bila lewat. `409` juga bila form tak `published`. **`409` bila putaran form berulang belum dibuka** (di branch T3: seluruh tolakan `period_key`, `400` maupun `409`), diperiksa SEBELUM berkasnya naik supaya tak meninggalkan objek yatim. ⚠️ *(Satgas, merged #1849)* `403` berpesan pada form Satgas bila tak memegang izin, juga diperiksa sebelum berkas naik |
| GET | `/me/uploads/:uploadId/preview` | Presigned URL lampiran sendiri. `404` untuk id yang bukan miliknya |
| GET | `/forms/:id/uploads/:uploadId/preview` | Idem untuk **pengelola form** (grup `/forms`, digerbang `requireFormManager`) |

> **Unggah dulu, kirim jawaban kemudian.** Satu jawaban dikirim sebagai satu JSON, jadi berkas tak bisa ikut di dalamnya. Nilai jawaban untuk field bertipe `file` adalah **`upload_id`**, bukan isi berkasnya. Unggahan yang jawabannya tak pernah dikirim dibersihkan cron harian 03:00.

> **Idempoten**: pengiriman identik dalam 2 menit dibalas `200 {"duplicate": true}` tanpa insert baru (sidik jawaban di-hash setelah kunci diurutkan, jadi payload yang disusun ulang saat retry tetap terdeteksi).

> **Kenapa `/me/service-index` ada di grup pengisian, bukan di balik `requireFormManager`.** Yang membacanya adalah staf divisi di halaman ringkasannya sendiri, dan ia belum tentu mengelola form apa pun — makin tidak setelah paket izin dipasang ke jabatan. Pemisahan dan alasan yang sama persis dipakai `/me/kaizen/committee`. Gerbangnya tetap ada, hanya bersumbu **departemen** dan dikerjakan di dalam handler: departemen yang diminta wajib ada di `common.SupervisedDepartments` pemanggil (yang selalu memuat departemennya sendiri), selain itu `403`.
>
> **Periode WAJIB dan tak punya nilai bawaan** (`400` bila kosong atau bukan `YYYY-MM`). Ini KEBALIKAN dari `?period=` pada `/forms/:id/analytics`, tempat kosong berarti seluruh periode. Memakai arti itu di sini akan membuat kartu bulanan menampilkan akumulasi seumur form sambil menuliskan nama satu bulan di bawahnya; bawaan "bulan berjalan" sama buruknya karena angkanya naik-turun sepanjang bulan. Penanda mingguan (`2026-W32`) ditolak, sebab `metric_key` hanya sah pada form berulang bulanan.
>
> **Departemen tanpa form bertanda dibalas `200 {"has_form": false}`, BUKAN `404`** — meniru `has_program:false` milik Kaizen: keadaan itu normal, dan `404` memaksa kartunya menampilkan layar galat untuk sesuatu yang bukan galat. `index` **absen** (bukan `0`) bila belum ada jawaban berskala; nol berarti sudah dinilai dan hasilnya nol. Rute BACA, jadi terkunci `EffectiveCompanyID`.

> **Kenapa `/me/capability` ada di grup pengisian, bukan di balik `requireFormManager`.** Daftar departemen aktif tinggal di konfigurasi server; tanpa endpoint ini setiap klien harus menyalinnya dan pasti melenceng saat daftarnya berubah. Ditaruh di `/me` supaya yang tak berhak menerima `can_manage:false` yang bisa dibaca klien, bukan `403` yang harus ditebak artinya. `departments` sengaja dikosongkan bila `can_manage:false`.
>
> **`form_types_by_department` adalah daftar POSITIF per departemen** (tipe yang boleh dibuat, sudah dihitung server), supaya klien tak memegang satu baris pun logika aturan. Per departemen, bukan datar: SPV HRGA membawahi dua sekaligus, dan meratakannya salah ke dua arah — irisan menyembunyikan tipe yang sebenarnya boleh, gabungan menawarkan tipe yang pasti ditolak `403`. Field ini **absen pada versi lama**; klien wajib menganggap absen = semua tipe boleh, karena BE dan FE tak naik bersamaan. **`can_manage_type_rules` dihitung TERPISAH dari `can_manage`** — admin IT belum tentu mengelola satu departemen pun.

## Inspeksi Satgas 5R & K3 (`/me/satgas` dan gerbang izin)

> ⚠️ **Merged 2026-09-11** lewat bip-erp PR [#1849](https://github.com/bip-itteam-internal/bip-erp/pull/1849), **deploy belum diukur, belum diuji lewat gateway**. Konsumen MyBharata (menu Satgas, halaman isi, unggah foto) ada di PR draft my-bharata [#144](https://github.com/bip-itteam-internal/my-bharata/pull/144) (2026-09-12). Keputusan: [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]].
>
> ⚠️ **T3 (nilai per orang, `GET /internal/satgas/metrics`, cek ulang lintas bulan) selesai di branch 2026-09-12, belum PR, belum merge, belum deploy, belum diuji lewat gateway.** bip-erp `feat/satgas-nilai-kpi` memuat aturan nilai, tab analitik, endpoint internal, dan sumber KPI `nilai_inspeksi_satgas` di employee-service; `feat/satgas-cek-ulang` bertumpu padanya dan menambah cek ulang lintas bulan. Nomor PR belum ada. Butir bertanda *(T3, branch)* di bawah belum ada di `main`; cara kerja dan alasannya di [[Microservices - Form Builder Service]].

**Gerbang.** Form ber-`metric_key: inspeksi_satgas` hanya bisa diisi pemegang izin `kepatuhan.satgas.input`, diperiksa di `POST /me/forms/:id/responses`, `POST /me/forms/:id/uploads`, `GET /me/forms/:id/subjects`, dan penyaring `GET /me/forms`. Tolakannya **`403 {"error": "..."}`** dengan pesan yang menyebut paket "Kepatuhan: Petugas Satgas 5R & K3" dan perlunya login ulang, diperiksa **sesudah** audience, jadi bukan-sasaran tetap mendapat `403` yang lama. Form tanpa penanda tak tersentuh. Kill-switch `KEPATUHAN_PERMISSION_ENFORCEMENT=off` mengembalikan form Satgas ke aturan audience saja.

**`GET /me/satgas`** meniru `/me/kaizen`: yang tak berhak menerima `200 {allowed:false, forms:[]}`, bukan `403`, dan izinnya dinilai **sebelum** database disentuh. Pemegang izin menerima:

```json
{
  "allowed": true,
  "forms": [{
    "form_id": "...", "title": "...", "description": "...",
    "period_key": "2026-09", "opens_at": "...", "closes_at": "...",
    "people": [{
      "employee_id": "...", "full_name": "...", "department": "...", "position": "...",
      "status": "open_finding", "submission_count": 2, "last_submitted_at": "..."
    }],
    "counts": {"not_rated": 0, "open_finding": 1, "resolved": 10}
  }]
}
```

- Hanya form Satgas **terbit** yang pemanggilnya masuk audience. Kartu putaran berjalan hanya dikirim bila putarannya **buka**; di `main` form di luar jendela periode tidak dikirim sama sekali. ⚠️ *(T3, branch)* Sampai batas cek ulang, form yang sama bisa membawa kartu kedua untuk **bulan lalu** (di bawah), diletakkan sebelum kartu putaran berjalannya dan tetap dikirim di rentang mati awal bulan.
- ⚠️ *(T3, branch)* Kartu putaran berjalan ikut membawa `fields` (susunan pertanyaan periode itu) dan `owner_department`, supaya halaman isi tak bergantung pada `/me/forms` yang menyembunyikan form di rentang mati.
- `people` = roster sasaran yang dibekukan saat terbit. Kiriman atas orang di luar roster diabaikan.
- `status` diturunkan dari **kiriman terakhir** atas orang itu pada periode berjalan, dari petugas **siapa pun**: tanpa kiriman `not_rated`; "Ada temuan?" = ya `open_finding`; = tidak `resolved`. Jawaban yang tak terbaca dibaca `open_finding`. Seri waktu dipecah lewat ObjectID.
- `last_submitted_at` absen bila `not_rated`. `forms` selalu array (`[]`, bukan `null`).
- Ringkasan ini **status**, bukan skor, dan sikapnya konservatif (`statusDariKiriman`). Di `main` skor dan KPI dari cek ulang terakhir belum ada. ⚠️ *(T3, branch)* Nilai per orang dilaporkan `GET /internal/satgas/metrics` (bagian Internal) dan tab analitik membawa `subject_rule` (bagian Bentuk data). Kiriman terakhirnya dipilih fungsi yang sama dengan ringkasan ini (`terakhirPerSasaran`), jadi menu dan KPI tak mungkin memilih kiriman berbeda.

**Kartu cek ulang bulan lalu** ⚠️ *(T3, branch)*. Sampai batas cek ulang, tiap form Satgas bulanan bisa membawa entri kedua untuk bulan temuan:

```json
{
  "form_id": "...", "title": "...", "description": "...", "owner_department": "...",
  "period_key": "2026-08", "cek_ulang": true, "batas_cek_ulang": "2026-09-05T23:59:59+07:00",
  "fields": ["..."],
  "people": [{"employee_id": "...", "full_name": "...", "status": "open_finding", "submission_count": 1, "last_submitted_at": "..."}],
  "counts": {"not_rated": 0, "open_finding": 1, "resolved": 0}
}
```

- Tanpa `opens_at`/`closes_at`.
- `fields` = susunan pertanyaan **bulan temuan** (snapshot periodenya; yang tak ada atau tak terbaca jatuh ke susunan terbaru milik form). Kiriman cek ulang divalidasi terhadap susunan itu, jadi klien merender `fields` ini dan mengirim `period_key` ini.
- `people` dan `counts` hanya memuat orang yang cek ulangnya **sah** menurut predikat yang sama dengan gerbang kiriman (`cekUlangBerlaku`, di bawah). Tanpa orang yang sah, entrinya tak dikirim.

**Cek ulang lintas bulan** ⚠️ *(T3, branch)*. `POST /me/forms/:id/responses` (field JSON `period_key`) dan `POST /me/forms/:id/uploads` (field multipart `period_key`) memakai satu keputusan, `periodeKiriman`. Batas cek ulang temuan bulan M = tanggal **5 bulan M+1 pukul 23:59:59** (zona waktu service; compose memasang `TZ: Asia/Jakarta`).

| `period_key` | Hasil |
|---|---|
| kosong | periode berjalan (perilaku lama); `409` bila putarannya belum buka |
| periode berjalan | diterima bila putarannya buka, `409` bila belum |
| bulan lalu, form Satgas, batas belum lewat | diterima sebagai **cek ulang** dan dicatat ke bulan itu, termasuk di rentang mati awal bulan |
| bulan lampau, form Satgas, batas sudah lewat | `409` `Cek ulang temuan <bulan> sudah ditutup <tanggal>. Nilai bulan itu memakai kiriman terakhirnya.` |
| selain itu | `400` `period_key "<nilai>" tidak sah untuk form ini` |

Pada kiriman cek ulang:

- Snapshot pertanyaan bulan temuan dibaca, **tidak dibuat**. Yang tak ada membuat validasi jatuh ke `fields` form. Yang **gagal dibaca** dibalas `500`: kunci "Ada temuan?" yang memutuskan boleh tidaknya cek ulang dibaca dari susunan bulan itu, jadi menebaknya dari susunan terbaru bisa membuka bulan lalu bagi orang yang temuannya sudah selesai. Kartu di `/me/satgas` tetap jatuh ke susunan terbaru pada keadaan itu, karena ia hanya menawarkan.
- Hanya orang yang jawaban "Ada temuan?" pada kiriman **terakhir** atas dirinya di bulan temuan (dari petugas siapa pun) bernilai `true` eksplisit yang boleh dicek ulang. Selain itu `409` berpesan, salah satu dari: temuan sudah dinyatakan selesai (dengan arahan memuat ulang menu Satgas), orang itu tak punya temuan terbuka pada bulan itu, jawaban terakhirnya tak terbaca, atau susunan pertanyaan bulan itu tak punya tepat satu pertanyaan "Ada temuan?".
- Penjaga itu diperiksa **sesudah** penjaga idempotensi: kiriman ulang identik dari petugas yang sama dalam 2 menit tetap dibalas `200 {"duplicate": true}`.
- Unggahan tak membawa orang yang dinilai, jadi syarat "masih bertemuan" baru diperiksa saat jawaban dikirim.
- Tampilan menu tetap konservatif (`statusDariKiriman`), gerbang tulis ketat (`cekUlangBerlaku`); keduanya membaca jawaban lewat satu fungsi, `jawabanTemuan`.

## Kaizen untuk karyawan (`/me/kaizen*`)

> Merged ke `main` 2026-08-06: papan ide lewat PR [#1028](https://github.com/bip-itteam-internal/bip-erp/pull/1028), permukaan karyawan lewat PR [#1034](https://github.com/bip-itteam-internal/bip-erp/pull/1034). **Belum diverifikasi lewat gateway hidup.**

**Terpisah dari `/me/forms` dengan sengaja.** Program Kaizen bukan "satu form lagi" bagi pengisinya: ia berulang tiap periode, berkuota, punya riwayat keputusan, dan idenya dibaca orang lain. [[APP - MyBharata]] menampilkannya di **menu tersendiri**, bukan bercampur di daftar survei.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/me/kaizen` | Program berjalan untuk pemanggil: `{has_program, form_id, title, description, fields, progress, board_visible}`. `progress` = `{quota, submitted, fulfilled, period_key, opens_at, closes_at}`. Membalas `has_program: false` bila **putarannya belum buka**, sama seperti keadaan "belum ada program": kuota tak boleh mulai menagih sebelum putarannya dibuka |
| GET | `/me/kaizen/ideas` | Riwayat ide sendiri **lintas periode**, terbaru dulu. `?period=`, `?page=`, `?limit=` maks **50**. Balas `{data[{id,period_key,submitted_at,answers,decision}], total, page, limit, fields}` |
| GET | `/me/kaizen/board` | Papan ide publik: `{data[{id,employee_name,department,status,submitted_at,answers}], period_key}`. `?period=` (default periode berjalan), maks **100** kartu |
| GET | `/me/kaizen/committee` | Program mana yang boleh ditinjau pemanggil: `{is_committee, form_id, title, period_key, can_manage_form}`. Bukan komite dibalas `{is_committee:false}`, **bukan `403`** |

> **Kenapa penemuan komite ada di `/me/*`, bukan `/kaizen/*`.** Seluruh rute komite menuntut id form, dan satu-satunya cara lain menemukannya adalah `GET /forms` — yang digerbang peran pengelola DAN departemen aktif, sedangkan komite ditunjuk HR dan bisa saja staf biasa dari departemen mana pun. Rute ini justru harus bisa dipanggil orang yang haknya **belum diketahui**, karena itu memang pertanyaannya. Dipakai menu **Komite Kaizen** di [[APP - Web ERP]]. `can_manage_form` membedakan anggota terdaftar dari pengelola departemen pemilik: keduanya boleh meninjau, hanya yang kedua boleh menyunting programnya.

> **Bukan sasaran program dibalas `has_program:false`, BUKAN `404`.** Menu Kaizen tetap bisa dibuka dan menjelaskan keadaannya, alih-alih menampilkan layar galat untuk keadaan yang sebenarnya normal. `has_program:false` juga menjawab "perusahaan ini belum punya program" — backend tak membedakan keduanya karena bagi pemakai keduanya memang sama.

> **Definisi pertanyaan dikirim SEKALI di tingkat atas** pada `/me/kaizen/ideas`, tidak diulang tiap ide. Riwayat 50 ide yang masing-masing membawa salinan definisi form akan berlipat ukurannya tanpa menambah satu pun informasi.

> **Papan menyaring dengan DAFTAR IZIN tipe field**, bukan daftar larangan. Papan dibaca seluruh karyawan, jadi tipe pertanyaan yang ditambahkan nanti (lampiran berkas, yang nilainya cuma id unggahan) tersembunyi secara bawaan sampai seseorang sengaja mengizinkannya. Daftar larangan bekerja sebaliknya: tipe baru bocor lebih dulu, ketahuan setelah tampil di depan sekantor. Ide yang masih ditinjau maupun yang ditolak **tak pernah** muncul; papan juga kosong bila `board_visible:false`.

> ✅ **`/me/kaizen` ikut membawa `blocks_attendance` dan `gate_end_date`** sejak PR [#1039](https://github.com/bip-itteam-internal/bip-erp/pull/1039), memakai perhitungan yang sama persis dengan `/me/forms`. Perlu karena form Kaizen dikeluarkan dari daftar survei di mobile: tanpanya, karyawan yang tertahan saat clock-in tak punya satu pun petunjuk di layar.
>
> ⚠️ **"Sama persis" itu sempat tidak benar.** Kedua permukaan memang memakai ekspresi yang sama, tapi ekspresi itu **salah untuk form berulang**: ia membaca `start_date`/`end_date` statis lewat `gateActiveAt`, sedangkan gerbang yang benar-benar menahan clock-in memakai jendela periode lewat `gateActiveForForm`. Untuk form berulang tanggal statisnya kedaluwarsa setelah putaran pertama, jadi keduanya melaporkan `false` selamanya sementara gerbangnya terus menyala tiap putaran. Diperbaiki di branch `feat/form-builder-periode-terbuka` 2026-09-01 (BELUM merge, BELUM deploy): keduanya kini lewat satu fungsi `menahanPresensi`. Latar lengkap di [[Microservices - Form Builder Service]] §Gerbang presensi memakai jendela periode.

## Kaizen (komite program ide bulanan)

> Merged ke `main` 2026-08-06 lewat PR #1016. Dev naik otomatis lewat Harness, **belum diverifikasi**; prod tidak auto-deploy. Konsepnya di [[HRIS - Kaizen (Ide Perbaikan)]].

**Prefix `/kaizen/*`, SENGAJA di luar grup `/forms`.** Grup itu digerbang `requireFormManager` (tingkat peran pengelola + departemen aktif), sedangkan anggota komite ditunjuk HR dan bisa saja staf biasa dari departemen mana pun. Gerbangnya per-form: terdaftar di `settings.kaizen.committee_employee_ids` **atau** boleh mengelola departemen pemilik form.

| Method | Path | Fungsi |
|---|---|---|
| GET | `/kaizen/forms/:id/responses` | Antrean komite. `?period=` (default periode berjalan), `?status=pending\|accepted\|rejected\|implemented`, `?department=`, `?page=`, `?limit=` maks 200. Membawa `fields` periode itu supaya label jawaban benar |
| PATCH | `/kaizen/forms/:id/responses/:responseId/decision` | Keputusan atas satu ide |
| POST | `/kaizen/forms/:id/responses/decisions` | Keputusan massal, maks **200** id sekali kirim. Membalas `{decided[], failed[{id,error}]}` — satu ide yang keburu diputuskan orang lain gagal sendirian, sisanya tetap tersimpan |
| GET | `/kaizen/forms/:id/compliance` | Papan kepatuhan periode itu: `{period_key, summary, data[]}` |
| GET | `/kaizen/forms/:id/compliance/export` | CSV kepatuhan. Header `X-Kaizen-Participants-Partial` muncul bila potret pesertanya belum lengkap |

> **Seluruh permukaan ini terkunci ke perusahaan pemanggil** (`common.CompanyID`), termasuk jalur bacanya. Override `?company=` milik admin pusat TIDAK berlaku di sini: memutuskan nasib ide adalah menulis, dan antrean sengaja ikut dikunci supaya yang dilihat selalu sama dengan yang bisa ditindak.

**Keputusan** (`decision` pada FormResponse): `{status, note, reviewed_by, reviewed_by_name, reviewed_at, implemented_at, pic_employee_id, pic_name, implementation_note}`. Absen = **belum ditinjau**; tak ada nilai `pending` yang tersimpan, jadi saringannya memakai `?status=pending` yang di server diterjemahkan jadi `$in: [null]`.

Transisi sah: belum ditinjau → `accepted`/`rejected`; `accepted` → `implemented`/`rejected`. `rejected` dan `implemented` **terminal** (`409`). Menolak **wajib** `note` (`400`), menandai diterapkan **wajib** `implemented_at` (`400`, sengaja tidak diisi otomatis karena skor KPI menghitung per periode).

⚠️ Menandai "diterapkan" pada ide yang belum pernah diterima saat ini dibalas `400`; seharusnya `409`. Diketahui, belum diperbaiki.

## Internal (dipanggil service lain)
| Method | Path | Fungsi |
|---|---|---|
| GET | `/internal/compliance` | Form wajib yang belum diisi: `{blocking:[{id,title}], warning:[...]}`. Dipakai [[Microservices - Attendance Service]] saat clock-in |
| GET | `/internal/kaizen/metrics` | Hitungan ide per orang pada satu periode: `{data{<employee_id>:{submitted,accepted,implemented}}, period_key, has_program}`. `?period=YYYY-MM` (default periode berjalan). Ditarik [[Microservices - Employee Service]] untuk skor KPI |
| GET | `/internal/culture/metrics` | Skor komposit program culture per officer pada satu periode: `{data{<employee_id>:{komposit[],jumlah}}, period_key, has_program}`. `?period=YYYY-MM`. Ditarik [[Microservices - Employee Service]] untuk sumber KPI `program_culture` (reduksi `rata_rata`). Program **event** disaring `period_key`; program **non-event** (⚠️ branch, ADR 0093) ongoing → menyumbang **100/0** (ada tanda `approved` pada periode) ke array `komposit` **yang sama** — bentuk payload TETAP ([[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]) |
| GET | `/internal/satgas/metrics` | ⚠️ *(T3, branch)* Nilai inspeksi Satgas per orang pada satu periode: `{has_form, period_key, orang[{employee_id, nilai, forms_dinilai, forms_total, ada_kiriman, menunggu_cek_ulang, batas_cek_ulang, form_tanpa_skala}]}`. `?period=YYYY-MM` **wajib**, tanpa nilai bawaan. Digerbang **kunci layanan** `?key=`, bukan header gateway (catatan di bawah). Ditarik [[Microservices - Employee Service]] untuk sumber KPI `nilai_inspeksi_satgas` |

> **Tiga angka, bukan satu.** Kepatuhan dihitung dari ide yang **diajukan** (karyawan memegang kendali penuh atas kepatuhannya sendiri), skor KPI dari ide yang **diterapkan** — begitulah redaksi metriknya di [[HRIS - Matriks KPI per Departemen]]. `has_program:false` membedakan "perusahaan ini belum menjalankan programnya" dari "gagal mengambil data"; hanya yang kedua layak dilaporkan sebagai metrik gagal hitung.

> **`/internal/culture/metrics` mengagregasi `culture_programs` + `culture_feedback` per periode**, bukan jawaban form. Per program: skor komposit `hitungSkorProgram` (Partisipasi 30% + Antusiasme 30% + Implementasi 40%, implementasi = part×ant÷100). `komposit[]` = daftar skor tiap program officer, `jumlah` = banyaknya program; employee-service me-`rata_rata`-kannya jadi KPI. `has_program:false` bila belum ada program aktif. Sama seperti Kaizen, rute ini **menggerbang dirinya sendiri** ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]) dan hanya **melapor** — yang menulis `kpi_score` tetap employee-service ([[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]).

> **Identitas terkunci ke header.** Query `?employee_id=&department=&company_id=` HANYA dihormati bila request tak membawa `BIP-Employee-ID` sama sekali (ciri panggilan service-to-service). Request pemakai lewat gateway selalu terkunci ke dirinya sendiri — tanpa aturan ini rute ini jadi jalan mengintip form tertunda orang lain lintas perusahaan. Lihat [[ADR - 0031 Prefix internal Bukan Batas Keamanan]].

> ⚠️ *(T3, branch)* **`/internal/satgas/metrics` digerbang kunci layanan, bukan header gateway.** Gateway memasang `BIP-Gateway-ID` pada setiap permintaan yang lolos JWT ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]), sedangkan muatan ini nilai per orang. `?key=` wajib sama dengan env `FORM_BUILDER_SERVICE_KEY`: header gateway saja, kunci salah, maupun kunci gateway yang dipakai sebagai `key` dibalas `401`, dan env yang kosong **menutup** rute bagi semua pemanggil. Header gateway tetap dituntut seperti rute lain. Sesudah gerbang: `period` kosong atau bukan `YYYY-MM` dibalas `400`, database belum terhubung `500`. Rute ini tidak memakai aturan penguncian identitas di atas: `company_id` dibaca dari header, bila kosong dari query `company_id`.
>
> Yang dibaca: form Satgas `published` **dan** `closed` yang tak terhapus, supaya nilai bulan saat form masih berjalan tak hilang ketika form ditutup. Form tanpa snapshot periode dan tanpa kiriman pada periode itu dilewati; bila tak tersisa satu pun, `has_form:false`. Susunan pertanyaan diambil dari snapshot periode yang diminta, dan gagal membacanya `500`. Kiriman satu form yang mencapai batas baca 20.000 juga `500`, dengan pesan yang menyebut judul formnya.
>
> **Muatannya sengaja sempit**: tanpa nama, departemen, jabatan, daftar form, atau rincian per form. `nilai` (0..100) **absen**, bukan `0`, bila belum ada form yang bernilai atas orang itu; `batas_cek_ulang` hanya ada bila `menunggu_cek_ulang`; `form_tanpa_skala` berisi judul form yang menilai orang itu tapi tak punya pertanyaan skala. `orang` absen bila kosong, termasuk saat `has_form:false`. Aturan nilainya (kiriman terakhir, rumus skala, batas cek ulang, gabungan antar form) di [[Microservices - Form Builder Service]].

## Bentuk data penting

**Tipe field** (`fields[].type`): `short_text` · `long_text` · `number` · `date` (`YYYY-MM-DD`) · `time` (`HH:MM`) · `dropdown` · `radio` · `checkbox` (jawaban berupa array) · `scale` (rentang maks 10 langkah) · **`file`** (nilai jawaban = `upload_id`) · **`section`**.

**`section` bukan pertanyaan** melainkan penanda awal bagian, hidup di dalam `fields` yang tetap datar. `label` jadi judul bagian, `description` jadi keterangannya. Aturannya: tak boleh `required`, tak boleh membawa `options`/`min`/`max`/`max_length`/`scale_*`, dan **jawaban yang menunjuk key bagian ditolak** (`400`). Bagian tak muncul di `analytics.fields` maupun kolom CSV.

**Keterangan ujung skala** (`scale_min_label`, `scale_max_label`) — mis. `"Sangat tidak puas"` .. `"Sangat puas"`. Keduanya opsional dan satu ujung saja pun sah; maksimal **40 karakter**; hanya berlaku untuk tipe `scale` (menempel di tipe lain ditolak `400`). Murni keterangan tampilan: nilai jawaban tetap angka, dan mengirim teks labelnya sebagai jawaban tetap ditolak.

**Bobot** (`weight`) — angka **relatif**, bukan persentase yang wajib berjumlah 100: bobot 3 berarti tiga kali lebih berat dari 1. Hanya berarti pada tipe `scale`. Dipakai dua jalur: `overall` di analisa form penilaian, dan **indeks layanan departemen** lewat `GET /me/service-index` (lihat di bawah). Keduanya memanggil `overallOf` yang sama; tak ada rumus kedua. Kosong berarti **1**, sehingga form lama tak berubah artinya. Nol **sah** (pertanyaan pelengkap yang tak ikut menghitung); negatif ditolak `400`, sebab akan membalik arah penilaian tanpa satu pun tanda di layar. Angka persen tetap bisa diisi apa adanya (40/20/10/30) karena jumlahnya memang 100.

**Pemilik** (`owner_department`, dan `owner_departments[]` 🔜 branch, belum deploy): nama departemen `master_department` (mis. `"General Affair"`), BUKAN key `system_roles`. Form lama yang masih menyimpan `owner_module` dipindah otomatis saat service boot (`it`→`Tech Development`, `ga`→`General Affair`). `owner_departments[]` memuat SELURUH departemen pemilik saat form dibagikan, dengan `owner_department` sebagai elemen pertama; dokumen lama tanpa `owner_departments` diperlakukan sebagai `[owner_department]` (backfill saat boot).

**Sasaran** (`audience.type`): `all` · `departments` (+`departments[]`) · `employees` (+`employee_ids[]`). `estimated_size` diisi manual sebagai penyebut tingkat pengisian; bila 0, `response_rate` tidak dikirim. Perhatikan `audience.departments` menjawab **siapa yang mengisi**, sedangkan `owner_department` menjawab **siapa yang memiliki** — keduanya tak harus sama.

**Asal template** (`template_id`) — ⚠️ branch `feature/workspace-position`. Menjejak `Form` yang dibuat lewat `POST /form-templates/:id/instantiate` ke template asalnya. Kosong pada form yang dibuat langsung tanpa template. (Dulu dipakai `/internal/culture/metrics` menandai form culture; sejak Culture punya modul sendiri, penanda itu tak lagi dipakai — lihat [[ADR - 0066 Modul Kelola Program Culture]].)

**Penanda metrik** (`metric_key`) — menandai sebuah form sebagai SUMBER angka ringkasan yang dibaca di luar layar analisa. Satu nilai dikenal: `service_index` (indeks layanan departemen, tampil di ringkasan divisi pemiliknya). Kosong = form biasa, dan itulah keadaan seluruh form lama. Tiga syarat, ketiganya menutup kegagalan **senyap**: nilai wajib dikenal (penanda salah tulis tak akan pernah ditemukan pembacanya), wajib `form_type: survey`, dan wajib `recurrence` ber-`unit: monthly` — jawaban form tak berulang tersimpan tanpa `period_key` sehingga permintaan indeks untuk bulan mana pun tak mencocokkan apa pun dan kartunya kosong selamanya padahal jawaban terus masuk. Pada `PATCH`, **absen berarti jangan diubah**; kirim `""` eksplisit untuk mencabut.

> **Satu form terbit per (perusahaan, departemen, penanda).** Ditegakkan **indeks unik parsial** atas dokumen `status: "published"`, bukan hanya pemeriksaan hitungan saat terbit — dua permintaan bersamaan sama-sama melihat hitungan nol dan keduanya lolos, lalu indeksnya berpindah mengikuti dokumen mana yang kebetulan ditemukan lebih dulu. Penerbitan kedua dibalas `409`, baik lewat pemeriksaan maupun lewat duplicate-key. Filternya **parsial** karena `metric_key` bertanda `omitempty`: indeks unik biasa akan memperlakukan seluruh form tanpa penanda sebagai satu nilai null yang sama sehingga dua form biasa di departemen yang sama saling menolak.

**Tipe form** (`form_type`): `survey` · `evaluation` · `checklist` · `kaizen`. Kiriman kosong jadi `survey`; nilai tak dikenal ditolak `400` (bukan diam-diam diubah). **Terikat dua arah dengan `subject`**: `evaluation` wajib punya sasaran, dan yang punya sasaran wajib `evaluation`. ✅ `request` ("Pengajuan") **dihapus** dan kini masuk kelompok "tak dikenal" — merged 2026-08-08 (BE [#1097](https://github.com/bip-itteam-internal/bip-erp/pull/1097), FE [erp-frontend#864](https://github.com/bip-itteam-internal/erp-frontend/pull/864)), **live di dev** dan terverifikasi lewat gateway 2026-08-09 (`form_types` membalas empat nilai); prod belum. Alasan, backfill dokumen lama, dan urutan deploy: [[Microservices - Form Builder Service]].

**Pengaturan Kaizen** (`settings.kaizen`): `{quota_default, quota_by_department[{department,quota}], committee_employee_ids[], board_visible, board_hidden_fields[]}`. **Terikat dua arah dengan `form_type: "kaizen"`**: tipe itu wajib punya blok ini, dan blok ini hanya sah di tipe itu. Tipe `kaizen` juga wajib `recurrence.unit: "monthly"`, serta menolak `single_response: true` dan menolak `subject`.

`quota_default` dan tiap `quota` antara 0 dan 31; departemen ganda ditolak `400`; `board_hidden_fields` wajib menunjuk key yang benar-benar ada. Kuota adalah **lantai**, bukan langit-langit: ide melebihi kuota tetap diterima, dan entri berkuota `0` berarti dikecualikan tapi tetap boleh mengirim. Menerbitkan form kaizen kedua saat masih ada yang `published` di perusahaan yang sama ditolak `409`.

> ⚠️ **`settings.kaizen` yang ABSEN pada `PATCH` berarti "jangan diubah"**, bukan "hapus". Tanpa aturan ini satu kiriman tanpa blok itu akan mengubah program Kaizen yang masih draft jadi survei biasa dan membuang kuota berikut daftar komite, tanpa galat. Konsekuensinya **tipe kaizen tidak bisa diubah ke tipe lain lewat `PATCH`** — hentikan programnya dengan menutup form.

**Potret peserta** (`participants`, `participants_at`, `participants_partial` pada dokumen periode): daftar orang yang wajib mengisi periode itu berikut kuota masing-masing, diambil cron **tiap periode**. Dipakai sebagai penyebut papan kepatuhan, menggantikan `audience.estimated_size` yang diisi manual. Gagal memotret tidak menggagalkan periode; yang ditahan hanya persentase di papan.

**Sasaran PENILAIAN** (`subject`): `{rules[], departments[], positions[], employee_ids[], allow_self, anonymous, resolved[]}`. `rules` digabung **OR**, isinya `departments`/`positions`/`employees`, dan tiap aturan wajib membawa daftarnya sendiri. `resolved` adalah **potret** yang diisi backend saat terbit — kiriman klien diabaikan. `anonymous` mengosongkan identitas penilai di export dan daftar jawaban, tapi TIDAK di database.

> **Form TANPA sasaran memakai `settings.anonymous`, bukan `subject.anonymous`.** Keduanya sengaja TIDAK dijumlahkan sebagai OR: form bersasaran hanya membaca `subject.anonymous`, dan form biasa hanya membaca `settings.anonymous`. Validasi menolak `settings.anonymous` pada form bersasaran (`400`), supaya dua saklar bermakna sama tak pernah bisa saling bertentangan pada satu dokumen sementara cuma satu yang dibaca. Penentu tunggalnya `anonimAktif` di `anonim.go`, dipakai daftar jawaban maupun export.
>
> **Mematikan anonim pada form yang sudah punya jawaban dibalas `409`** — kerahasiaan sudah dijanjikan kepada orang yang terlanjur mengisi, dan mencabutnya membuka identitas mereka surut. Pada `PATCH`, `settings.anonymous` yang **absen berarti jangan diubah** (pointer di sisi request), sebab tanpa itu klien lama yang menyunting judul akan mematikan kerahasiaan form yang masih kosong tanpa satu pun pesan.

> **`subject` menjawab siapa yang DINILAI**, `audience` menjawab siapa yang MENGISI. Skenario "semua karyawan menilai tiap Office Boy" = `audience.type: all` + `subject.rules: ["positions"]`, `positions: ["Office Boy"]`. **Gerbang presensi ditolak `400`** pada form bersasaran penilaian.

**Form berulang** (`recurrence`): `{enabled, unit: "monthly"|"weekly", open_day}`. ⚠️ **Baru benar-benar bisa dikirim sejak PR #1019 (2026-08-06)**; sebelum itu `formRequest` tak punya fieldnya sehingga form berulang mustahil dibuat lewat API. Pada `PATCH`, **absen berarti jangan diubah** — kirim `{"enabled": false, ...}` eksplisit untuk mematikannya. Nil atau `enabled:false` berarti form sekali jalan, dan perilakunya persis seperti sebelum fitur ini ada. `open_day` 1..28 untuk bulanan (dibatasi 28 karena Februari), 1..7 untuk mingguan mengikuti hari ISO Senin sampai Minggu. Nilai di luar rentang atau `unit` tak dikenal ditolak `400`.

Jendela periode **selalu berakhir di ujung bulan atau minggu**, bukan sekian hari setelah buka, supaya dua periode tak pernah hidup bersamaan. Penandanya (`period_key`) `2026-08` untuk bulanan dan `2026-W32` untuk mingguan (penomoran **ISO**, supaya minggu yang melintasi pergantian tahun tak melahirkan dua penanda). Periode dibuka otomatis oleh cron **tiap jam** (`Asia/Jakarta`), hanya untuk form `published`.

**`period_key` pada jawaban** (`FormResponse.period_key`): kosong untuk form biasa **dan** untuk seluruh jawaban yang tersimpan sebelum fitur ini. Di `main` klien tidak mengirimnya; backend menurunkannya dari aturan pengulangan dan waktu kirim. ⚠️ *(T3, branch)* Klien **boleh** mengirim `period_key` pada kirim jawaban dan unggah; kosong tetap diturunkan backend, dan satu-satunya nilai selain periode berjalan yang diterima adalah bulan lalu pada form Satgas sampai batas cek ulang (bagian Inspeksi Satgas). Kunci keunikan pengisian ikut bergeser jadi (form, pengisi, yang dinilai, periode), sehingga form bulanan bisa diisi ulang tiap putaran.

**Gerbang presensi** (`attendance_gate`): `{enabled, mode: "warn"|"block", start_date, end_date}`. Tanggal wajib **RFC3339** (`2026-08-01T00:00:00Z`); `"2026-08-01"` akan ditolak. **Pada form berulang, `start_date`/`end_date` diabaikan** dan yang dipakai adalah jendela periode berjalan: tanggal statis akan lewat setelah bulan pertama dan gerbangnya tak pernah menyala lagi, padahal formnya terbit ulang tiap bulan.

**Respons analytics**: `total_responses`, `unique_respondents`, `audience_size`, `sample_size`, `truncated`, `response_rate` (opsional), `daily[{date,count}]`, `fields[{key,label,type,answered,skipped,options[{option,count}],average,min,max,sample_text[]}]`. Saat `truncated=true`, `response_rate` sengaja tidak dikirim karena tak bisa dihitung jujur dari sebagian data. **`file_fields[{key,label}]`** (merged lewat bip-erp [#1852](https://github.com/bip-itteam-internal/bip-erp/pull/1852); ✅ terverifikasi gateway dev 2026-09-11, ⚠️ prod belum): pertanyaan bertipe `file`, urut sesuai form dan mengikuti `?period=` seperti `fields`; **absen** pada form tanpa berkas. Terpisah dari `fields` karena berkas tak diringkas (`fields` memang tak pernah memuatnya); klien memakainya untuk tahu jawaban mana yang dibuka lewat `GET /forms/:id/uploads/:uploadId/preview`.

**Blok `index` pada respons analytics** (opsional) — ringkasan satu angka atas seluruh pertanyaan berskala: `{index, scored_questions, respondents, aspects[], unweighted[]}`, dengan tiap aspek membawa `{key, label, answered, skipped, average, scale_min, scale_max, weight}`. Bentuknya **sama persis** dengan balasan `/me/service-index`, sebab keduanya memanggil perhitungan yang sama; angka di ringkasan divisi dan di halaman analisa karena itu tak bisa berbeda.

> ⚠️ **Inilah satu-satunya tempat `weight` sampai ke klien.** `fields[]` tidak membawanya sama sekali, jadi tanpa blok ini mustahil menampilkan pertanyaan mana yang menggerakkan angkanya.
>
> **Absen pada dua keadaan, dan keputusan kapan absen itu yang penting** — angka yang muncul di tempat salah tak pernah terlihat salah, sebab bentuknya selalu wajar. Pertama, form **bersasaran penilaian**: merata-ratakan seluruh penilai lintas orang yang dinilai melebur nilai dua orang berbeda jadi satu, dan `subjects[]` sudah menjawabnya per orang. Kedua, form **tanpa pertanyaan berskala**: tak ada yang bisa diringkas. Belum adanya JAWABAN bukan salah satunya — aspeknya tetap dilaporkan supaya pembaca tahu apa yang akan diukur, dan yang absen cukup `index` sendiri.
>
> Susunan pertanyaan yang dipakai mengikuti `?period=` yang diminta, sama dengan `fields[]`.

**Respons analytics form penilaian** (absen pada form biasa): `evaluation{subject_count, evaluators_started, evaluators_completed, pairs_done}`, `subjects[{employee_id,name,department,position,responses,scores[{key,label,answered,average}],overall,overall_fields,total_questions}]`, `subjects_truncated`, ⚠️ *(T3, branch)* `subject_rule`. `scores` hanya untuk pertanyaan `number`/`scale`, dan `average` **absen** (bukan 0) bila belum ada yang menilai. `response_rate` di sini = `evaluators_completed / audience_size` — yang dihitung penilai yang menyelesaikan SELURUH daftarnya, bukan yang sekadar mengirim satu penilaian.

> ⚠️ *(T3, branch)* **Form Satgas membawa `subject_rule: "last_per_period"`**, absen pada form lain. Aturannya dipilih dari penanda form di satu tempat (`rekapSasaran`), tak diwariskan diam-diam. `subjects[].scores` dan `overall` dihitung dari kiriman **terakhir** per orang per periode: dengan `?period=` itulah nilai kiriman terakhir bulan itu, tanpa `?period=` rata-rata nilai akhir tiap bulan. `subjects[].responses` dan `evaluation` tetap menghitung **seluruh** kiriman, karena temuan dan cek ulang sama-sama terjadi. Di `main` tab ini masih merata-ratakan seluruh jawaban form Satgas.

## Dokumen Terkait

- [[Microservices - Form Builder Service]] · [[IT - Form Builder]]
- [[API - Index]] · [[API - Attendance Service]] · [[CORE - API Master Gateway]]

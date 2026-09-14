> **Status**: ⚠️ **Diterima, sebagian terimplementasi.** T1+T2 **merged** 2026-09-11 (bip-erp PR [#1849](https://github.com/bip-itteam-internal/bip-erp/pull/1849)); biner form-builder dev memuatnya (diukur 2026-09-11), employee-service dev dan gerbang Satgas belum diuji lewat gateway. T4 **merged** 2026-09-11 (bip-erp [#1852](https://github.com/bip-itteam-internal/bip-erp/pull/1852) + erp-frontend [#1542](https://github.com/bip-itteam-internal/erp-frontend/pull/1542)) dan **live di dev**: `file_fields` terverifikasi lewat gateway dev, bundel frontend dev memuat editor baru. Layar belum dicoba sebagai orang, prod belum. T6 **selesai di branch** 2026-09-12 (my-bharata `feat/satgas-inspeksi`, `1.18.0+162`, PR draft [my-bharata#144](https://github.com/bip-itteam-internal/my-bharata/pull/144), belum dicoba di perangkat), bersama PR erp-frontend [#1550](https://github.com/bip-itteam-internal/erp-frontend/pull/1550) yang mencabut larangan berkas wajib (draft, merge ditahan sampai adopsi terukur). **T3 selesai di branch** 2026-09-12: bip-erp `feat/satgas-nilai-kpi` (nilai, endpoint internal, sumber KPI) dan `feat/satgas-cek-ulang` (cek ulang lintas bulan, bertumpu pada branch pertama), erp-frontend `feat/kpi-sumber-satgas`, dan commit tambahan di PR draft my-bharata #144. Belum PR, belum deploy, dan jalur cek ulang lintas bulan baru bisa dibuktikan 1-5 Oktober 2026. T5 dan T7 belum dikerjakan. Rincian di `## Deskripsi`.

## Untuk Manajemen

Dokumentasi inspeksi Satgas 5R & K3 pindah dari Google Form dan WhatsApp ke aplikasi. Petugas OD & Industrial Relation memotret temuan (atau memilih foto dari galeri) lewat menu khusus di MyBharata, lalu menilai ulang beberapa hari kemudian. Nilai hasil cek ulang itulah yang menjadi nilai KPI Office Boy dan Security bulan itu, dihitung sistem, bukan diketik ulang.

**Yang berubah di layar:**

- **MyBharata**: menu baru "Satgas 5R & K3" yang hanya muncul untuk jabatan petugas yang ditunjuk. Isinya daftar Office Boy dan Security yang dinilai, tempat memotret temuan dan perbaikan, serta siapa yang belum dicek ulang bulan ini. Form Satgas tidak lagi tercampur di daftar survei beranda. Petugas juga mendapat kartu di beranda yang menyebut berapa orang belum dinilai dan masih ada temuan. Temuan akhir bulan tetap bisa dicek ulang sampai tanggal 5 bulan berikutnya, dan hasilnya dihitung ke bulan temuannya.
- **Web ERP**: halaman rekap Satgas untuk OD & IR/HR (nilai per orang per bulan beserta fotonya), dan Form Builder kini bisa membuat pertanyaan berisi foto.
- **KPI** Office Boy (5R area tanggung jawab) dan Security (kebersihan pos jaga) terisi otomatis sebagai draf, tetap diverifikasi atasan. Temuan yang masih boleh dicek ulang belum dihitung sampai tanggal 5 bulan berikutnya, supaya nilai yang tersimpan tidak mendahului cek ulangnya.

**Siapa yang terdampak:** petugas OD & IR (mengisi), Office Boy dan Security yang dinilai (per Agustus 2026: 7 Security, 4 Office Boy), atasan mereka (memverifikasi KPI), dan tim IT (memasang hak akses ke jabatan petugas).

**Apa yang TIDAK dijanjikan:**

- Tidak ada penilaian otomatis oleh AI. Yang menilai tetap petugas Satgas.
- Tidak ada peringkat antar departemen.
- Office Boy dan Security belum diberi tahu lewat aplikasi, dan belum bisa melihat foto temuan atas dirinya. Pemberitahuan temuan tetap lewat WhatsApp pada tahap ini.
- Temuan K3 hanya tercatat, belum punya alur tindak lanjut ke GA.
- Tidak menyentuh sanksi, Surat Peringatan, maupun gaji secara langsung.

**Perkiraan besaran kerja:** sedang, di tiga permukaan (backend, web, MyBharata). Sebagian besar bahan sudah ada: form penilaian per orang, penyimpanan foto di server, dan jalur ke KPI. Yang baru: hak akses khusus petugas, penanda form Satgas, aturan nilai dari cek ulang, halaman rekap, dan dukungan foto di aplikasi. Rumus konversi skor 1-5 ke nilai 0-100 sudah diputuskan (skor 3 menjadi 50). Bagian backend pertama (hak akses, penanda, gerbang, dan data untuk menu) sudah masuk kode utama. Editor web (pertanyaan foto dan sakelar penanda) sudah masuk kode utama dan berjalan di server uji, belum di produksi. Aplikasi MyBharata versi baru (foto, menu Satgas, cek ulang) sudah selesai dikerjakan dan menunggu rilis. Perhitungan nilai KPI dari cek ulang, termasuk cek ulang yang jatuh ke bulan berikutnya, sudah selesai dikerjakan dan menunggu pemeriksaan serta rilis. Pertanyaan foto baru boleh dibuat wajib sesudah sebagian besar petugas memasang versi itu.

## Deskripsi

*Inspeksi Satgas 5R & K3 memakai Form Builder (tipe `evaluation`, yang dinilai Office Boy dan Security) dengan satu penanda form yang dibaca tiga pihak: MyBharata (menu khusus, bukan daftar survei), gerbang pengisian di server, dan satu sumber KPI per orang yang memakai **jawaban terakhir dalam periode**, bukan rata-rata. Menu dan pengisian digerbang modul izin baru yang tertutup sejak awal. Menyimpang dari jalur KPI form yang sudah ada (`service_team_index` ke `nilai_layanan_pribadi`), karena jalur itu melebur seluruh form bertanda di satu departemen dan merata-ratakan jawaban.*

- **Status**: ⚠️ **Diterima, sebagian terimplementasi.** T1+T2 merged 2026-09-11 (PR [#1849](https://github.com/bip-itteam-internal/bip-erp/pull/1849)), biner form-builder dev memuatnya, employee-service dev belum diukur. T4 merged 2026-09-11 (bip-erp [#1852](https://github.com/bip-itteam-internal/bip-erp/pull/1852) + erp-frontend [#1542](https://github.com/bip-itteam-internal/erp-frontend/pull/1542)), live dev, prod belum. T6 selesai 2026-09-12, PR draft [my-bharata#144](https://github.com/bip-itteam-internal/my-bharata/pull/144); larangan berkas wajib dicabut di PR erp-frontend terpisah [#1550](https://github.com/bip-itteam-internal/erp-frontend/pull/1550) yang merge-nya ditahan. T3 selesai di branch 2026-09-12, belum PR, belum deploy. Daftar task: `Workspace/ANALISA - Inspeksi Satgas 5R dan K3.md`
- **Path di repo**:
  - bip-erp, **T1+T2 (merged #1849)**: `shared-library/common/catalog_kepatuhan.go` · `shared-library/models/employee/permission_set.go` · `services/employee/permission_catalogs.go` · `services/form-builder/models_form.go` · `services/form-builder/validate.go` · `services/form-builder/satgas_gate.go` · `services/form-builder/satgas_me.go` · `services/form-builder/permission_gate.go` · `services/form-builder/response_handlers.go` · `services/form-builder/uploads.go` · `services/form-builder/form_handlers.go` · `services/form-builder/routes.go`
  - bip-erp, **T3 (branch `feat/satgas-nilai-kpi`, belum PR)**: `services/form-builder/{satgas_nilai,satgas_metrics,analytics,routes,satgas_me}.go` · `services/employee/{kpi_sumber_inspeksi_satgas,kpi_galat_sumber,kpi_auto}.go` · `shared-library/common/env.go` · `docker-compose.yml` · `docker-compose.dev.yml` · `.env.example`
  - bip-erp, **T3 cek ulang lintas bulan (branch `feat/satgas-cek-ulang`, bertumpu branch di atas, belum PR)**: `services/form-builder/{satgas_cek_ulang,response_handlers,uploads,satgas_me,periode_terbuka}.go`
  - bip-erp, **T4 (merged [#1852](https://github.com/bip-itteam-internal/bip-erp/pull/1852))**: `services/form-builder/analytics.go` (`file_fields`)
  - erp-frontend, **T3 (branch `feat/kpi-sumber-satgas`, belum PR)**: `src/features/hris/kpi/lib/label-otomatis.ts` · `src/features/hris/kpi/components/auto-overview-view.tsx` · `src/features/form-builder/types/form.ts` · `src/features/form-builder/components/analytics/subject-tab.tsx` · `src/i18n/locales/{id,en}.ts`
  - erp-frontend, **T4 (merged [#1542](https://github.com/bip-itteam-internal/erp-frontend/pull/1542))**: `src/features/form-builder/types/form.ts` · `src/features/form-builder/lib/{schema,field-types,field-type-icons,tabs,pivot}.ts` · `src/features/form-builder/components/{satgas-settings-fields,question-row,form-editor}.tsx` · `src/features/form-builder/components/kaizen/queue-view.tsx` · `src/features/form-builder/hooks/use-analytics.ts` · `src/features/form-builder/components/analytics/{lampiran-jawaban,question-tab,individual-tab,analytics-view}.tsx` · `src/features/hris/master-data/lib/label-modul.ts`
  - erp-frontend, **T5 (baru, belum ada)**: `src/features/hris/satgas/*` · `src/app/(main)/hris/satgas/page.tsx` · `src/components/layout/sidebar-menus.tsx`
  - mybharata-app, **T6 (PR draft [#144](https://github.com/bip-itteam-internal/my-bharata/pull/144), branch `feat/satgas-inspeksi`)**: `lib/src/features/form/domain/entities/{survey,survey_field}.dart` · `lib/src/features/form/domain/validators/answer_encoder.dart` · `lib/src/features/form/data/datasources/survey_remote_datasource.dart` · `lib/src/features/form/presentation/bloc/{survey_bloc,survey_upload_cubit}.dart` · `lib/src/features/form/presentation/widgets/{survey_field_input,survey_fill_view,survey_boolean_input,survey_file_input}.dart` · `lib/src/core/utils/photo_compressor.dart` · `lib/src/features/satgas/*` · `lib/src/features/home/presentation/widgets/home_page/{home_quick_access,quick_access_more_bottom_sheet}.dart` · `lib/src/features/home/presentation/pages/home_page.dart` · `lib/app_root.dart`
  - mybharata-app, **T3 (commit tambahan di PR draft #144)**: `lib/src/features/satgas/{data/models/satgas_overview_model,domain/entities/satgas_form}.dart` · `lib/src/features/satgas/presentation/bloc/{satgas_fill_args,satgas_fill_cubit}.dart` · `lib/src/features/satgas/presentation/pages/{satgas_page,satgas_fill_page}.dart` · `lib/src/features/satgas/presentation/widgets/{satgas_view,satgas_person_header}.dart` · `lib/src/features/form/data/{datasources/survey_remote_datasource,repositories/survey_repository_impl}.dart` · `lib/src/features/form/domain/{repositories/survey_repository,usecases/submit_survey,usecases/upload_survey_file}.dart` · `lib/src/features/form/presentation/{bloc/survey_upload_cubit,widgets/survey_fill_view}.dart` · `lib/src/core/config/di/bloc_injection.dart` · `lib/l10n/app_{id,en}.arb`
  - erp-frontend, **pencabutan larangan berkas wajib (PR draft [#1550](https://github.com/bip-itteam-internal/erp-frontend/pull/1550), merge ditahan)**: `src/features/form-builder/lib/{schema,field-types}.ts` · `src/features/form-builder/components/question-row.tsx` · `src/i18n/locales/{id,en}.ts`
- **Tanggal**: 2026-09-11

## Context

Kebutuhan datang dari manajemen sebagai tiga gagasan sekaligus: posisi Culture sebagai "intel perusahaan", catatan pelanggaran atribut (sepatu, lanyard), dan Satgas 5R & K3. Catatan atribut sudah diputuskan di [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] dan tidak diubah di sini. Keputusan ini hanya tentang Satgas.

Pemakainya (OD & Industrial Relation Officer) menyatakan masalahnya sendiri: mengunggah dokumentasi inspeksi masih lewat Google Form, dan temuan disebar manual lewat WhatsApp ke tiap PIC. Siklusnya: temuan difoto, PIC memperbaiki, beberapa hari kemudian dicek ulang, dan **nilai KPI bulan itu diambil dari hasil cek ulang**. Tanpa temuan, nilainya penuh.

Lembar "KPI DEPARTEMEN HRGA" milik HRD (dibaca 2026-09-11, hanya baris yang memuat SATGAS/5R/K3/Culture) memperlihatkan masalah yang tidak dikeluhkan tetapi lebih mahal. Skor Satgas sudah dipakai sebagai KPI perorangan Office Boy (`Kebersihan 3`, bobot 0,15) dan Security (`Kerapihan dan kebersihan Pos`, bobot 0,2), diketik tangan dengan skala yang berganti tiap bulan. Pada Maret 2026 skor "4" (skala 1-5) tercatat sebagai 60 poin di metrik berbobot 15, dan **total KPI Office Girl bulan itu 131 dari 100 lolos berstatus disetujui**. April memakai konversi yang berbeda (3 menjadi 9,0, yaitu 60%). Kolom "SISTEM ERP" di lembar itu sudah meminta "penambahan fitur temuan Satgas di OD, form report Satgas di MyBharata".

Grounding ke kode (bip-erp dan erp-frontend `origin/main`, mybharata-app `origin/dev`, 2026-09-11):

1. **Field `file` baru ada di backend.** Satu field berisi satu `upload_id` (`services/form-builder/validate.go:590-601`), batas 4 MB berlaku untuk seluruh file-service (`services/file/main.go:337`), dan jenis berkas tidak diperiksa. Editor web tak bisa membuat field ini (`erp-frontend/src/features/form-builder/types/form.ts:17-37` tak memuat `file`), dan MyBharata tak bisa mengisinya (`lib/src/features/form/domain/entities/survey_field.dart:8-21`).
2. **Jalur KPI per orang dari form sudah ada, tetapi melebur.** Form `evaluation` ber-`metric_key: service_team_index` mengalir ke `nilai_layanan_pribadi` (per orang, dipakai metrik Security "Rating Pelayanan dan Keamanan") dan `indeks_layanan_tim` (KPI atasan HRGA), keduanya dari angka yang sama (`services/employee/kpi_sumber_indeks_layanan_tim.go:31-44`). Nilai seseorang adalah rata-rata dari **semua** form bertanda tempat ia dinilai (`services/form-builder/service_team_index.go:148-156`). Per 2026-08 tim General Service sudah dinilai lewat dua form, Security 7 orang dengan 1.149 jawaban dan Office Boy 4 orang dengan 581 jawaban (`:28-30`). Menandai form Satgas dengan penanda yang sama akan mencampur skor 5R dengan rating pelayanan di KPI anggota **dan** atasannya, tanpa satu pun galat.
3. **Beberapa jawaban dalam satu periode dirata-rata.** `overallOf` merata-ratakan antar jawaban (`services/form-builder/skor_gabungan.go:119-142`) dan dipakai juga oleh tab analitik per orang (`analytics_subject.go:94`). Cek ulang yang dikirim sebagai jawaban baru akan tercampur dengan temuannya.
4. **Konversi skala sistem adalah `(v-min)/(max-min)×100`** (`skor_gabungan.go:61`), sehingga skala 1-5 menjadi 1=0, 3=50, 5=100. Lembar HRD memakai `v/5` (3 menjadi 60).
5. **Gerbang pengisian hanya `audience`.** `submitResponse` memeriksa status terbit dan `audienceMatches` saja (`response_handlers.go:364-369`), dan `audience` hanya mengenal `all`/`departments`/`employees`. Menyembunyikan menu di aplikasi tidak menahan apa pun.
6. **MyBharata tak pernah menerima izin.** Body login dari gateway hanya membawa `system_roles`, `department`, dan `position` (`api-gateway/main.go:316-325`). Gerbang menu di aplikasi hanya `SystemRoles` dari cache lokal, dan rantai menu beranda meloloskan semua bila peran belum termuat (`home_quick_access.dart:215`).
7. **Prefiks izin menentukan fallback.** Satu klaim izin berprefiks sebuah modul mematikan fallback tier modul itu (`services/form-builder/permission_gate.go:89-92`), kelas insiden yang sama dengan modul `engagement` ([[CORE - RBAC dan Permission Set]]). Pola [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]] juga tak cocok, karena menunya terbuka untuk semua sampai ada penugasan pertama.
8. **Tipe `report` tidak cocok.** Ia melarang `subject` (`validate.go:390-391`), dan yang memutus adalah penyetuju departemen pengirim, bukan petugas inspeksi.
9. **`settings` form dikirim utuh ke klien** (`response_handlers.go:216`), sedangkan `metric_key` tidak. Kaizen disaring dari daftar survei di sisi klien (`survey_bloc.dart:74-75`).
10. **Peraturan Perusahaan tidak memuat pasal 5R, K3, atau atribut kerja** (`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`; `git grep` kosong, dengan kontrol positif kata "mangkir"). Nilai ini karena itu murni KPI, bukan sanksi. Lihat [[HRIS - Kepatuhan Peraturan Perusahaan]].

Yang dibuang dari usulan awal: penilaian foto oleh AI, peringkat antar departemen, dan master area. Tak satu pun diminta pemakainya, dan penilaian tetap dilakukan Satgas sendiri, sehingga syarat ketiga [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] (ada keputusan yang berubah karena hasilnya) tidak terpenuhi. Modul K3 manufaktur juga tidak dipakai: areanya ditulis mati `{Produksi, Gudang}` dan terikat penyebut KPI SPV Manufaktur (`shared-library/models/manufacture/k3_gmp.go:40-49`).

⚠️ Dua dok yang disinggung keputusan ini berstatus 🟡, yaitu [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] dan [[GA - Checklist Management]]. Keduanya rencana, bukan kenyataan.

## Decision

### 1. Form Builder, bukan modul baru

Satgas memakai form `evaluation` yang sudah ada: petugas mengisi, Office Boy dan Security menjadi `subject` (aturan `positions`), dan formnya berulang bulanan. Modul inspeksi tersendiri ditolak karena mengulang penyimpanan foto, potret sasaran, dan jalur KPI yang sudah ada, sekaligus membiarkan utang field `file` di klien tetap tak terbayar. Ini bukan tipe form baru, jadi aturan tipe [[ADR - 0041 Izin Tipe Form Menempel di Departemen]] tidak berubah.

### 2. Satu penanda `inspeksi_satgas` di form, dibaca tiga pihak

Form Satgas diberi penanda **`metric_key: inspeksi_satgas`** (`MetricSatgasInspeksi`), dinyalakan pengelola lewat sakelar "Inspeksi Satgas 5R & K3" di tab Pengaturan form Penilaian (T4, merged erp-frontend #1542, live dev 2026-09-11). Sakelar itu terkunci selama syaratnya belum terpenuhi dan selama form sudah bertanda lain (mis. `service_team_index`), supaya penanda layanan tak tertimpa diam-diam. Menyalakannya mematikan `single_response`, dan mengganti tipe form melepas penanda yang tak sah untuk tipe barunya. Satu fakta itu dibaca MyBharata (menu Satgas, dikeluarkan dari daftar survei), gerbang server (§4), dan sumber KPI (§8).

Syaratnya ditegakkan saat form dibuat (`validateMetricKey` + `validateSatgas`): tipe `evaluation`, berulang bulanan, sasaran aktif, **tepat satu** pertanyaan `boolean` ("Ada temuan?"), dan **tanpa** `settings.single_response`. Tepat satu, karena pertanyaan itulah satu-satunya pembeda jawaban temuan dari cek ulang, dan memilih yang pertama dari beberapa akan membuat artinya bergantung urutan pertanyaan. Tanpa `single_response`, karena cek ulang adalah kiriman kedua atas orang yang sama pada periode yang sama dan `single_response` menolaknya `409`. Penandanya masuk `metrikJamak`, jadi Security dan Office Boy boleh punya form Satgas terpisah di departemen yang sama.

Penandanya **bukan** `service_team_index`. Memakai penanda itu mencampur skor 5R dengan rating pelayanan di KPI anggota dan atasannya (§Context 2).

### 3. Nilai = jawaban TERAKHIR per orang per periode, dihitung di SATU fungsi

Untuk form bertanda Satgas, nilai seseorang dalam satu periode adalah jawaban terakhirnya, bukan rata-rata. Temuan pertama (skor rendah + foto temuan) tergantikan oleh cek ulang (skor final + foto perbaikan). PIC tanpa temuan cukup satu jawaban dengan skor penuh.

Fungsinya satu, dan dipakai endpoint KPI, halaman rekap web, serta tab analitik "Yang Dinilai" untuk form bertanda. Analitik **tidak boleh** menampilkan rata-rata untuk form Satgas: temuan skor 2 lalu cek ulang skor 5 akan tampil 62,5 di analitik dan 100 di KPI, dua angka untuk satu orang di satu bulan tanpa petunjuk mana yang benar. Aturan rata-rata untuk form layanan tidak berubah. Kedua aturan dipilih eksplisit dari penandanya, tidak diwariskan diam-diam. Sejak T1+T2 (merged) aturan ini dipakai STATUS ringkasan menu (§5). **Sejak T3 (branch, belum deploy)** pemilih yang sama (`terakhirPerSasaran`) juga dipakai nilai, endpoint KPI, dan tab analitik: pada satu periode skornya kiriman terakhir, tanpa pilihan periode skornya rata-rata nilai akhir tiap bulan, kolom jumlah tetap menghitung seluruh kiriman, dan respons analitik membawa `subject_rule: "last_per_period"` supaya layarnya menyebut aturan itu.

Tanpa jawaban dalam periode berarti "belum dinilai": metrik itu jatuh ke penilaian manual, bukan 0 dan bukan 100. **Penyimpangan T3 (keputusan user 2026-09-12):** sumbernya tidak mengembalikan galat biasa, melainkan galat bertipe "belum dapat dihitung". Galat biasa diberi prefiks gagal sumber yang menyembunyikan SELURUH skor otomatis orang itu, padahal yang terjadi hanya satu metrik belum punya angka. "Belum dapat dihitung" juga dipakai untuk temuan yang masih menunggu cek ulang, kiriman terakhir tanpa skor, dan periode tanpa form Satgas berjalan. Galat biasa tersisa untuk yang harus dibetulkan orang atau sistem: orang bukan sasaran form Satgas mana pun, form tanpa pertanyaan skala (pesan menyebut judulnya), form-builder tak terjangkau, dan kunci layanan salah.

### 4. Gerbang: modul izin `kepatuhan`, tertutup sejak awal, ditegakkan server

Izin Satgas berdiri di modul izin sendiri, **`kepatuhan`**, dengan satu izin **`kepatuhan.satgas.input`** dan satu paket bawaan **`kepatuhan_petugas_satgas`** ("Kepatuhan: Petugas Satgas 5R & K3"). Bukan `hris` dan bukan `formbuilder`, supaya memasangnya tidak mencabut akses HRIS atau Form Builder milik petugas (§Context 7). Tanpa fallback tier: tak seorang pun memegangnya sampai IT memasang paket ke jabatan petugas OD & IR lewat [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]. Polanya meniru [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]], bukan [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]].

Form-builder menolak kirim jawaban, unggah foto (sebelum berkas naik ke file-service), dan pembacaan daftar sasaran pada form bertanda Satgas bila pengirimnya tak memegang izin itu, dengan `403` berpesan yang menyebut paketnya dan perlunya login ulang. Form Satgas juga tak muncul di `/me/forms` bagi mereka. Semua jalur memakai satu predikat, jadi tak ada yang bisa menyimpang sendiri. Ini gerbang pengisian berbasis izin yang pertama di Form Builder; semua preseden yang ada (`requireCultureManager`, peninjau Kaizen, `requireFormManager`) menggerbang kelola atau tinjau, bukan pengisian.

Kill-switch **`KEPATUHAN_PERMISSION_ENFORCEMENT`**: hanya `off` yang mematikannya, dan saat itu form Satgas kembali ke perilaku form lain (cukup audience). Jalan mundur darurat, bukan mode operasi; sengaja tak ditulis di compose.

### 5. Menu MyBharata bertanya ke server lewat `GET /me/satgas`, bukan ke `system_roles`

Endpoint **`GET /me/satgas`**, meniru pola `/me/kaizen`, menilai izin **sebelum** database disentuh: yang tak berhak dijawab `200 {allowed:false}`. Pemegang izin menerima form Satgas terbit yang putarannya buka dan ia masuk audience-nya, beserta ringkasan per PIC dari kiriman petugas **siapa pun** pada periode berjalan, berstatus `not_rated`, `open_finding`, atau `resolved`, diturunkan dari jawaban terakhir (§3). Jawaban "Ada temuan?" yang tak terbaca dibaca `open_finding`, supaya temuan yang tak pernah dicek tak tertutup sendiri. Menu tampil hanya bila server menjawab boleh. Cache `system_roles` tidak dipakai, karena tak memuat izin dan meloloskan semua saat belum termuat (§Context 6).

`metric_key` kini ikut dikirim di `/me/forms`, sehingga beranda menyaring form Satgas dengan pola `isKaizen` (`surveySectionOf`), sementara `pendingOf` sengaja tidak disaring agar halaman isi `/survey/:id` tetap menemukan formnya.

**Penyimpangan di T6 (keputusan user 2026-09-12, PR draft my-bharata [#144](https://github.com/bip-itteam-internal/my-bharata/pull/144)).** Halaman isinya **`SatgasFillPage`** tersendiri, bukan `EvaluationFillPage`: halaman itu menutup diri begitu semua orang pernah dinilai, sedangkan cek ulang menilai orang yang sudah pernah dinilai. Halaman Satgas menampilkan status tiap orang dari `/me/satgas` (yang masih bertemuan di atas), dan orang berstatus Selesai tetap bisa dibuka. Definisi pertanyaannya diambil dari `/me/forms` daftar PENUH, karena form tetap dikirim walau semua sasaran sudah dinilai, dan kirimannya membawa `subject_employee_id`. Baris menu dievaluasi **sebelum** jalan pintas `roles == null` di `home_quick_access.dart`, favorit Satgas tak dipangkas editor Atur Menu selama izin belum dijawab server, dan jawaban izin dikosongkan saat logout (jawaban yang tiba sesudahnya dibuang). Karena menu baru tak masuk grid favorit yang sudah tersimpan, petugas mendapat **kartu beranda** yang hanya tampil bila ada orang belum dinilai atau masih bertemuan. Kegagalan muat pertama menyembunyikan menu dan kartu, diterima sadar; kegagalan sesudah sukses mempertahankan jawaban terakhir.

**Penyimpangan di T3 (keputusan user 2026-09-12, branch bip-erp `feat/satgas-cek-ulang` + commit tambahan my-bharata #144).** `GET /me/satgas` kini membawa `fields` (susunan pertanyaan periode kartu) dan `owner_department` di setiap entri, sehingga halaman isi merakit formnya dari kartu dan tak lagi bergantung pada `/me/forms`, yang tetap jadi cadangan bila `fields` absen. Alasannya: `/me/forms` menyembunyikan form selama putaran berjalan belum buka, tepat saat cek ulang bulan lalu masih boleh dikirim. Sampai batas cek ulang, tiap form juga bisa membawa **kartu cek ulang bulan lalu** (`cek_ulang: true`, `period_key` bulan temuan, `batas_cek_ulang`), didahulukan dan tampil juga di rentang mati awal bulan, berisi hanya orang yang cek ulangnya sah (§Diputuskan sesudah ADR ditulis). Kiriman dan unggahan dari kartu membawa `period_key`-nya. Kepala halaman isi kartu cek ulang menyebut bulan tujuan dan batasnya, karena orang yang sama bisa tampil di kartu cek ulang dan kartu putaran berjalan yang judulnya sama. Halaman Satgas memuat ulang daftar setiap kali halaman isi ditutup, bukan hanya sesudah tersimpan: tolakan `409` cek ulang justru paling sering berarti daftarnya basi. Ringkasan status menu tetap konservatif, sementara kartu cek ulang dan gerbang kiriman memakai predikat ketat.

### 6. Halaman rekap Satgas di web

Menu web di kategori HRIS, digerbang izin modul yang sama, membaca endpoint rekap yang sama dengan §5: nilai per orang per bulan dari fungsi §3, foto temuan dan perbaikan, dan orang yang belum dicek ulang (T5, belum dikerjakan).

**Diubah di T3 (branch, belum deploy).** Semula tertulis "analitik generik Form Builder bukan tempat membaca nilai Satgas". Tab "Yang Dinilai" di analitik Form Builder kini membaca nilai Satgas dengan aturan §3 yang sama, supaya pengelola form tak melihat dua angka untuk satu orang di satu bulan, dan menyebut aturannya dalam satu kalimat. Tab itu tetap bukan halaman rekap: tak menampilkan batas cek ulang maupun siapa yang belum dicek ulang, dan hanya terbuka bagi pengelola form.

### 7. Field foto di klien Form Builder

Editor web bisa membuat field `file`, dan analitik menampilkan fotonya lewat rute pratinjau pengelola yang sudah ada (T4: bip-erp #1852 + erp-frontend #1542 merged dan live dev 2026-09-11; `file_fields` terverifikasi lewat gateway dev). Rute pratinjau saja ternyata **tidak cukup**: backend mengeluarkan field berkas dari `fields` analitik (`analyzableFields`), padahal tab Individu dan Pertanyaan mengulang daftar itu. Karena itu respons analitik kini membawa daftar terpisah **`file_fields`** `[{key,label}]` (absen pada form tanpa berkas), dan tombol "Lihat berkas" mengambil presigned URL saat diklik. MyBharata (T6, branch) mengambil foto dari kamera **atau galeri** (keputusan user 2026-09-12), memperkecil sisi terpanjang ke 1920 px dan menyimpan ulang sebagai JPEG di isolate sampai di bawah 3,8 MB, lalu mengunggahnya lebih dulu (`POST /me/forms/:id/uploads`, field `file`; sejak T3 juga `period_key` kartu bila ada) dan menjawab pertanyaan dengan `upload_id`. Tombol Kembali, Lanjut, dan Kirim terkunci selama unggahan berjalan. Batas 4 MB file-service tidak dinaikkan. Kompresi di web tidak dibangun, karena erp-frontend tak punya jalur pengisian form.

**Editor web masih menolak pertanyaan berkas yang wajib.** Pertanyaan berkas wajib membuat pengisi beraplikasi lama ditolak server, dan pada form bergerbang presensi mode tahan ikut menahan clock-in. T6 membuat MyBharata bisa mengunggah, tetapi larangannya **tidak** dicabut bersamaan rilis: pencabutannya PR erp-frontend terpisah ([#1550](https://github.com/bip-itteam-internal/erp-frontend/pull/1550), draft) yang baru di-merge sesudah adopsi versi T6 di kalangan petugas terukur lewat `app_version` karyawan (keputusan user 2026-09-12). Backend sendiri tak pernah melarangnya; tipe `report` justru mewajibkan minimal satu pertanyaan berkas yang wajib (`validate.go`). Antrean komite Kaizen menampilkan penanda "Ada lampiran" alih-alih id unggahan; komite belum bisa membuka lampirannya karena pratinjau khusus pengelola form.

Banyak foto per orang berarti beberapa field `file` terpisah, karena satu field satu berkas dan unggahan sekali pakai per orang yang dinilai. `max_files` ditunda sampai ada pemakai kedua. Kemampuan ini sekaligus membuka tipe `report`, yang mewajibkan field berkas tetapi hari ini tak bisa diisi klien mana pun. MyBharata kini mengenal tipe `boolean` untuk "Ada temuan?" (T6, branch), dikirim sebagai bool JSON: teks `"false"` akan terbaca masih bertemuan tanpa satu pun galat.

### 8. Sumber KPI per orang

Form-builder melapor lewat endpoint internal yang menggerbang dirinya sendiri ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Employee-service tetap satu-satunya penulis `kpi_score` ([[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]) lewat sumber per orang yang baru, dipasang HR pada metrik Office Boy `Kebersihan 3` dan Security `Kerapihan dan kebersihan Pos` lewat "Atur Target" ([[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]]).

Konversi skala 1-5 ke 0-100 hanya satu rumus, di backend: `(v-1)/4`, diputuskan 2026-09-12. Nilainya berstatus draf yang diverifikasi atasan. Template Office Boy dan Security tidak seluruhnya otomatis, jadi pembekuan otomatis [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] tidak berlaku.

**Wujud T3 (branch `feat/satgas-nilai-kpi`, belum deploy).** Endpoint **`GET /internal/satgas/metrics?period=YYYY-MM`** digerbang **kunci layanan `FORM_BUILDER_SERVICE_KEY`** lewat query `key`, bukan kunci gateway: gateway memasang header gateway untuk setiap permintaan ber-JWT, jadi rute yang bersandar padanya terbuka bagi karyawan mana pun yang login, sementara muatannya nilai per orang. Kunci yang belum dikonfigurasi menutup rute. Ini menyimpang dari rute internal form-builder yang lebih dulu ada (`service-team-index`, `kpi-checklist/metrics`) dan mengikuti [[RUN - Menambah Metrik KPI Otomatis]]; rute lama itu task keamanan tersendiri. Muatannya **sempit**, hanya yang dibaca sumber KPI: `employee_id`, nilai, jumlah form yang menilai dan yang sudah bernilai, penanda ada kiriman, penanda menunggu cek ulang beserta batasnya, dan judul form tanpa pertanyaan skala. Tanpa nama, departemen, jabatan, atau rincian per form. Form `published` dan `closed` dibaca; form tanpa snapshot periode dan tanpa kiriman pada periode itu dilewati.

Sumber employee-service **`nilai_inspeksi_satgas`** (grup SDM, cakupan individu) memetakan muatan itu. Orang yang dinilai lewat lebih dari satu form mendapat rata-rata nilai akhir tiap form, dihitung di form-builder supaya rekap T5 memakai angka yang sama, dan cakupannya tercatat. **Temuan yang masih boleh dicek ulang belum final** sampai tanggal 5 bulan berikutnya pukul 23.59.59 WIB, kecuali formnya sudah ditutup: `POST /kpi` menyalin nilai otomatis saat penilai menyimpan, jadi angka temuan yang telanjur tersimpan tak ikut berubah saat cek ulang masuk. Sampai batas itu metriknya "belum dapat dihitung" dengan tanggal batas di pesannya (§3).

### 9. Hubungan dengan catatan kepatuhan (ADR 0085)

Petugasnya sama. Modul izin `kepatuhan` diusulkan menjadi gerbang tunggal petugas lapangan OD & IR untuk kedua fitur (satu modul, dua izin), menjawab TBD "petugas ditunjuk" di [[HRIS - Industrial Relation]], supaya siapa petugasnya tercatat di satu tempat. Datanya tetap terpisah: catatan atribut bukan KPI, inspeksi Satgas adalah KPI.

### 10. Form Satgas tak memicu notifikasi inbox form-builder

Tidak saat terbit, dan tidak saat pengisian "selesai". Petugas bekerja dari menu Satgas yang sudah menampilkan siapa yang masih bertemuan. Notifikasi terbit akan membuat seluruh audience menerima kabar inspeksi; notifikasi selesai dikirim `notifySubmitted` pada SETIAP kiriman begitu seluruh sasaran pernah dinilai, sehingga tiap cek ulang akan melahirkan "sudah lengkap" yang sama lagi. Keduanya satu keputusan, jadi satu predikat (`kirimNotifForm`) untuk kedua titik. Bagian "selesai" diputuskan saat review T1+T2 (2026-09-11), sesudah perilaku berulangnya ditemukan di kode.

## Consequences

### Yang membaik

- Nilai KPI 5R dihitung dari satu rumus di sistem, sehingga kelas kesalahan "skala campur, total 131" tertutup.
- Dokumentasi, nilai, dan KPI berada di satu tempat. Foto tak lagi tercecer di Drive yang tak terhubung ke angkanya.
- Field foto Form Builder berguna untuk form lain, termasuk tipe `report`.

### Yang memburuk atau tetap terbuka

- ⚠️ Form-builder kini punya dua aturan agregasi per orang: rata-rata untuk layanan, terakhir-menang untuk Satgas. Wajib dipilih eksplisit dari penanda, dengan uji yang membuktikan keduanya tidak tertukar.
- ⚠️ Nilai bergantung pada disiplin cek ulang. Temuan yang tak dicek ulang sampai batasnya tetap bernilai temuan. Ringkasan di menu §5 menampilkan siapa yang masih bertemuan justru untuk menahan ini.
- ⚠️ Sampai T3 di-deploy, tab analitik "Yang Dinilai" di dev dan prod masih merata-ratakan jawaban form Satgas.
- ⚠️ Nilai KPI Satgas bulan M baru final sesudah tanggal 5 bulan M+1. Penilai yang membuka scorecard lebih awal melihat "belum dapat dihitung" untuk orang yang temuannya belum dicek ulang, tanpa pemberitahuan saat nilainya final (diterima; tanggal batas disebut di pesan).
- Satu jawaban "Ada temuan?" dibaca dengan dua sikap: tampilan menu konservatif (tak terbaca dianggap masih bertemuan), gerbang tulis cek ulang ketat (hanya `true` eksplisit membuka bulan lalu). Pembaca jawabannya satu fungsi, sikapnya sengaja berbeda.
- Jalur handler kiriman cek ulang lintas bulan tak punya test tanpa database. Sebagian perilakunya (kirim ulang identik, orang yang sudah selesai, foto berperiode bulan temuan) baru bisa dibuktikan lewat gateway pada 1-5 Oktober 2026.
- Temuan dan cek ulang tidak saling tertaut di data. Yang menyatukannya hanya urutan waktu per orang per periode.
- Daftar Office Boy dan Security yang dinilai dibekukan saat form terbit, jadi karyawan baru butuh form diterbitkan ulang.
- PIC tidak diberi tahu lewat aplikasi dan tak bisa melihat temuan atas dirinya. WhatsApp tetap dipakai.
- MyBharata versi lama menampilkan pertanyaan foto dan Ya/Tidak sebagai tipe yang belum didukung, melewatinya saat memeriksa isian, lalu ditolak backend bila pertanyaannya wajib. Karena itu larangan berkas wajib di editor web baru dicabut sesudah adopsi versi T6 terukur, bukan saat rilis. Angka versi minimum aplikasi di gateway ditulis mati dan hanya ajakan (`api-gateway/main.go:701`), jadi adopsi tak bisa dipaksa dari server.
- Petugas beraplikasi lama yang mengisi form Satgas dari daftar survei (versi lama belum menyaringnya) mengirim tanpa jawaban "Ada temuan?" bila pertanyaan itu opsional, dan kirimannya terbaca `open_finding`. Penahannya proses, bukan kode: paket izin dipasang sesudah petugas memperbarui aplikasi, dan "Ada temuan?" dibuat wajib.
- ⚠️ Objek di file-service tersimpan `application/octet-stream`, jadi PDF mungkin terunduh alih-alih tampil di pratinjau. Belum diuji dengan berkas sungguhan.
- Pengelola departemen pemilik form membaca seluruh jawaban dan foto lewat analitik Form Builder. Form Satgas karena itu sebaiknya dimiliki Human Resource saja; bila General Affair ikut jadi pemilik, pengelola dari departemen PIC membaca inspeksi atas timnya sendiri.

### Konsekuensi deploy

- employee-service dan form-builder naik **bersama**: katalog izin diresolusi di yang satu dan ditegakkan di yang lain, dan sumber KPI baru (T3) memanggil endpoint internal baru. Sesudahnya erp-frontend, lalu PR cek ulang lintas bulan (`feat/satgas-cek-ulang`), lalu MyBharata dengan version name dan versionCode dinaikkan. Backend cek ulang dengan aplikasi lama membuat cek ulang tetap masuk bulan berjalan seperti hari ini, tidak lebih buruk.
- Sesudah deploy, IT memasang paket izin ke jabatan petugas, lalu petugas login ulang (token berlaku 72 jam). Paketnya disisipkan otomatis saat employee-service boot.
- Katalog izin baru wajib terdaftar di seluruh tempat registrasinya. Yang terlewat gagal senyap, tetapi kini tertangkap tiga uji penjaga employee-service ([[CORE - RBAC dan Permission Set]]).
- **Env wajib baru `FORM_BUILDER_SERVICE_KEY`** (T3), bernilai sama di blok employee-service dan form-builder-service. Env dibaca saat container dibuat, jadi keduanya `--force-recreate`. Kosong di form-builder menutup rute internal; kosong di employee-service membuat metrik Satgas gagal sumber dengan pesan yang menyebut env-nya ([[RUN - Deploy Microservices bip-erp]]). Tanpa kategori inbox baru. Env unggah form-builder (`FILE_MODULE_URL`, `MINIO_FORM_KEY`) tercatat live sejak 2026-08-06, tetapi belum diukur ulang di prod.

### Yang sengaja tidak dilakukan

- Penilaian foto oleh AI, peringkat antar departemen, dan master area.
- Tipe form baru atau mesin status yang menautkan temuan ke cek ulang, beserta notifikasi ke PIC. Ditinjau ulang setelah satu atau dua bulan pemakaian bila penyebaran lewat WhatsApp tetap menjadi keluhan utama. Saat itu, kategori inbox baru menuntut form-builder dan notification-service naik bersama.
- Menaikkan batas 4 MB file-service.
- Batas cek ulang yang bisa diatur per form, dan aturan wajib pertanyaan skala saat form dibuat.

### Diputuskan sesudah ADR ditulis (dijawab 2026-09-12)

- **Rumus konversi `(v-1)/4`**, rumus sistem yang sudah ada (skor 3 menjadi 50), bukan `v/5` praktik lembar HRD.
- **Cek ulang yang jatuh ke bulan berikutnya dihitung ke periode bulan temuan.** Terwujud di T3 (branch `feat/satgas-cek-ulang`, belum deploy): kirim jawaban dan unggah foto menerima `period_key`; bulan lalu diterima sebagai cek ulang hanya pada form Satgas bulanan sampai batasnya, termasuk di rentang mati awal bulan; sesudah batas `409` yang menyebut tanggalnya; penanda lain `400`. Periode yang tersimpan adalah bulan temuan, jadi KPI, analitik, dan rekap cukup membaca `period_key` apa adanya.
- **Batas cek ulang: tanggal 5 bulan berikutnya pukul 23.59.59 WIB**, sejajar tenggat ceklis KPI dan pembekuan Finance. Bulan lalu dihitung dari tanggal 1, bukan dengan menggeser tanggal sebulan, supaya tanggal 31 tak terbaca sebagai bulan cek ulang.
- **Temuan belum final sebelum batas** (§8), kecuali formnya sudah ditutup.
- **Cek ulang ke bulan lalu hanya sah bila jawaban "Ada temuan?" terakhir orang itu di bulan temuan secara eksplisit `true`** (tindak lanjut review T3). Kunci pertanyaan yang tak terbaca, jawaban yang hilang, atau jawaban bukan bool ditolak `409` berpesan; snapshot bulan temuan yang gagal dibaca ditolak `500`. Tanpa predikat ketat ini, form penilaian bulanan yang baru diberi penanda Satgas akan membuka seluruh sasaran bulan lalu untuk ditulis ulang. Penjaga ini berjalan sesudah penjaga idempotensi, supaya kirim ulang karena jaringan dibalas duplikat, bukan `409`.
- **Orang di lebih dari satu form Satgas**: rata-rata nilai akhir tiap form. **Form tanpa pertanyaan skala**: sumber menolak dengan pesan yang menyebut judul form, tanpa aturan baru saat form dibuat.
- **Kunci layanan tersendiri dan muatan internal sempit** (§8), dan **"belum dapat dihitung" untuk data yang memang belum ada** (§3).

### Belum Diputuskan (TBD, wajib dijawab HR sebelum go-live)

- Jumlah field foto per orang, dan apakah foto wajib.
- Siapa selain petugas yang boleh membuka rekap web (usul: atasan Office Boy dan Security).
- Pemeriksaan jenis berkas di server. Hari ini hanya klien yang membatasi ke gambar.

## Dokumen Terkait

- [[Microservices - Form Builder Service]] (cara kerja, termasuk bagian Inspeksi Satgas 5R & K3) · [[API - Form Builder Service]]
- [[Microservices - Employee Service]] (sumber KPI, katalog izin) · [[Microservices - File Service]]
- [[CORE - RBAC dan Permission Set]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]] · [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]]
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] · [[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]]
- [[ADR - 0041 Izin Tipe Form Menempel di Departemen]] · [[REF - Penamaan Metrik & Sumber KPI]] · [[RUN - Menambah Metrik KPI Otomatis]] · [[RUN - Deploy Microservices bip-erp]]
- [[HRIS - Matriks KPI per Departemen]] (metrik Office Boy dan Security) · [[GA - Checklist Management]]
- [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] · [[HRIS - Industrial Relation]]
- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] · [[HRIS - Kepatuhan Peraturan Perusahaan]]
- [[APP - MyBharata]] · [[APP - Web ERP]]

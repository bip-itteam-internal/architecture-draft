> **Status**: 🟡 **Diusulkan**, disetujui 2026-09-11, kode belum ada. Rincian di `## Deskripsi`.

## Untuk Manajemen

Dokumentasi inspeksi Satgas 5R & K3 pindah dari Google Form dan WhatsApp ke aplikasi. Petugas OD & Industrial Relation memotret temuan lewat menu khusus di MyBharata, lalu menilai ulang beberapa hari kemudian. Nilai hasil cek ulang itulah yang menjadi nilai KPI Office Boy dan Security bulan itu, dihitung sistem, bukan diketik ulang.

**Yang berubah di layar:**

- **MyBharata**: menu baru "Satgas 5R & K3" yang hanya muncul untuk jabatan petugas yang ditunjuk. Isinya daftar Office Boy dan Security yang dinilai, tempat memotret temuan dan perbaikan, serta siapa yang belum dicek ulang bulan ini. Form Satgas tidak lagi tercampur di daftar survei beranda.
- **Web ERP**: halaman rekap Satgas untuk OD & IR/HR (nilai per orang per bulan beserta fotonya), dan Form Builder kini bisa membuat pertanyaan berisi foto.
- **KPI** Office Boy (5R area tanggung jawab) dan Security (kebersihan pos jaga) terisi otomatis sebagai draf, tetap diverifikasi atasan.

**Siapa yang terdampak:** petugas OD & IR (mengisi), Office Boy dan Security yang dinilai (per Agustus 2026: 7 Security, 4 Office Boy), atasan mereka (memverifikasi KPI), dan tim IT (memasang hak akses ke jabatan petugas).

**Apa yang TIDAK dijanjikan:**

- Tidak ada penilaian otomatis oleh AI. Yang menilai tetap petugas Satgas.
- Tidak ada peringkat antar departemen.
- Office Boy dan Security belum diberi tahu lewat aplikasi, dan belum bisa melihat foto temuan atas dirinya. Pemberitahuan temuan tetap lewat WhatsApp pada tahap ini.
- Temuan K3 hanya tercatat, belum punya alur tindak lanjut ke GA.
- Tidak menyentuh sanksi, Surat Peringatan, maupun gaji secara langsung.

**Perkiraan besaran kerja:** sedang, di tiga permukaan (backend, web, MyBharata). Sebagian besar bahan sudah ada: form penilaian per orang, penyimpanan foto di server, dan jalur ke KPI. Yang baru: hak akses khusus petugas, penanda form Satgas, aturan nilai dari cek ulang, halaman rekap, dan dukungan foto di aplikasi. Sebelum aktif, HR perlu memutuskan rumus konversi skor 1-5 ke nilai 0-100.

## Deskripsi

*Inspeksi Satgas 5R & K3 memakai Form Builder (tipe `evaluation`, yang dinilai Office Boy dan Security) dengan satu penanda form yang dibaca tiga pihak: MyBharata (menu khusus, bukan daftar survei), gerbang pengisian di server, dan satu sumber KPI per orang yang memakai **jawaban terakhir dalam periode**, bukan rata-rata. Menu dan pengisian digerbang modul izin baru yang tertutup sejak awal. Menyimpang dari jalur KPI form yang sudah ada (`service_team_index` ke `nilai_layanan_pribadi`), karena jalur itu melebur seluruh form bertanda di satu departemen dan merata-ratakan jawaban.*

- **Status**: 🟡 **Diusulkan**, disetujui 2026-09-11, kode belum ada. Daftar task: `Workspace/ANALISA - Inspeksi Satgas 5R dan K3.md`
- **Path di repo** (nama final ditentukan `/plan`):
  - bip-erp: `shared-library/common/catalog_<modul>.go` (baru) · `services/employee/permission_catalogs.go` · `services/employee/permission_set.go` · `services/form-builder/models_form.go` · `services/form-builder/validate.go` · `services/form-builder/response_handlers.go` · `services/form-builder/uploads.go` · `services/form-builder/<satgas>_me.go` (baru) · `services/form-builder/<satgas>_nilai.go` (baru) · `services/employee/kpi_sumber_<satgas>.go` (baru)
  - erp-frontend: `src/features/form-builder/types/form.ts` · `src/features/form-builder/lib/schema.ts` · `src/features/form-builder/lib/field-types.ts` · `src/features/form-builder/components/question-row.tsx` · `src/features/form-builder/lib/format-answer.ts` · `src/features/hris/satgas/*` (baru) · `src/app/(main)/hris/satgas/page.tsx` (baru) · `src/components/layout/sidebar-menus.tsx`
  - mybharata-app: `lib/src/features/form/domain/entities/survey_field.dart` · `lib/src/features/form/presentation/widgets/survey_field_input.dart` · `lib/src/features/form/data/datasources/survey_remote_datasource.dart` · `lib/src/features/form/presentation/bloc/survey_bloc.dart` · `lib/src/features/satgas/*` (baru) · `lib/src/features/home/presentation/widgets/home_page/home_quick_access.dart`
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

### 2. Satu penanda "inspeksi Satgas" di form, dibaca tiga pihak

Form Satgas diberi penanda tersendiri (nama final di `/plan`, mengikuti [[REF - Penamaan Metrik & Sumber KPI]]), dinyalakan pengelola di editor web, dan sah hanya pada tipe `evaluation` yang berulang bulanan. Satu fakta itu dibaca MyBharata (menu Satgas, dikeluarkan dari daftar survei), gerbang server (§4), dan sumber KPI (§8).

Penandanya **bukan** `service_team_index`. Memakai penanda itu mencampur skor 5R dengan rating pelayanan di KPI anggota dan atasannya (§Context 2).

### 3. Nilai = jawaban TERAKHIR per orang per periode, dihitung di SATU fungsi

Untuk form bertanda Satgas, nilai seseorang dalam satu periode adalah jawaban terakhirnya, bukan rata-rata. Temuan pertama (skor rendah + foto temuan) tergantikan oleh cek ulang (skor final + foto perbaikan). PIC tanpa temuan cukup satu jawaban dengan skor penuh.

Fungsinya satu, dan dipakai endpoint KPI, halaman rekap web, serta tab analitik "Yang Dinilai" untuk form bertanda. Analitik **tidak boleh** menampilkan rata-rata untuk form Satgas: temuan skor 2 lalu cek ulang skor 5 akan tampil 62,5 di analitik dan 100 di KPI, dua angka untuk satu orang di satu bulan tanpa petunjuk mana yang benar. Aturan rata-rata untuk form layanan tidak berubah. Kedua aturan dipilih eksplisit dari penandanya, tidak diwariskan diam-diam.

Tanpa jawaban dalam periode berarti "belum dinilai": sumber mengembalikan galat dan metrik jatuh ke penilaian manual, bukan 0 dan bukan 100.

### 4. Gerbang: modul izin baru, tertutup sejak awal, ditegakkan server

Izin Satgas berdiri di modul izin sendiri, bukan `hris` dan bukan `formbuilder`, supaya memasangnya tidak mencabut akses HRIS atau Form Builder milik petugas (§Context 7). Tanpa fallback tier: tak seorang pun memegangnya sampai IT memasang paket ke jabatan petugas OD & IR lewat [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]. Polanya meniru [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]], bukan [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]].

Form-builder menolak kirim jawaban **dan** unggah foto pada form bertanda Satgas bila pengirimnya tak memegang izin itu. Ini akan menjadi gerbang pengisian berbasis izin yang pertama di Form Builder; semua preseden yang ada (`requireCultureManager`, peninjau Kaizen, `requireFormManager`) menggerbang kelola atau tinjau, bukan pengisian.

### 5. Menu MyBharata bertanya ke server, bukan ke `system_roles`

Endpoint khusus di grup `/me`, meniru pola `/me/kaizen`, mengembalikan form Satgas milik pemanggil yang berizin beserta ringkasan kiriman periode ini per orang yang dinilai: siapa sudah bernilai final, siapa masih bertemuan. Menu tampil hanya bila server menjawab boleh. Cache `system_roles` tidak dipakai, karena tak memuat izin dan meloloskan semua saat belum termuat (§Context 6).

Beranda menyaring form bertanda Satgas dengan pola `isKaizen`, sementara `pendingOf` sengaja tidak disaring supaya tautan notifikasi tetap jalan. Halaman isinya memakai `EvaluationFillPage` apa adanya.

### 6. Halaman rekap Satgas di web

Menu web di kategori HRIS, digerbang izin modul yang sama, membaca endpoint rekap yang sama dengan §5. Isinya: nilai per orang per bulan dari fungsi §3, foto temuan dan perbaikan, dan orang yang belum dicek ulang. Analitik generik Form Builder bukan tempat membaca nilai Satgas.

### 7. Field foto di klien Form Builder

Editor web bisa membuat field `file`, dan analitik menampilkan fotonya lewat rute pratinjau pengelola yang sudah ada. MyBharata memotret lalu mengompres sebelum unggah: resolusi dibatasi, ukuran diperiksa di bawah 4 MB, dan tombol kirim terkunci selama unggahan berjalan. Batas 4 MB file-service tidak dinaikkan.

Banyak foto per orang berarti beberapa field `file` terpisah, karena satu field satu berkas dan unggahan sekali pakai per orang yang dinilai. `max_files` ditunda sampai ada pemakai kedua. Kemampuan ini sekaligus membuka tipe `report`, yang mewajibkan field berkas tetapi hari ini tak bisa diisi klien mana pun.

### 8. Sumber KPI per orang

Form-builder melapor lewat endpoint internal yang menggerbang dirinya sendiri ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Employee-service tetap satu-satunya penulis `kpi_score` ([[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]) lewat sumber per orang yang baru, dipasang HR pada metrik Office Boy `Kebersihan 3` dan Security `Kerapihan dan kebersihan Pos` lewat "Atur Target" ([[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]]).

Konversi skala 1-5 ke 0-100 hanya satu rumus, di backend. Nilainya berstatus draf yang diverifikasi atasan. Template Office Boy dan Security tidak seluruhnya otomatis, jadi pembekuan otomatis [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] tidak berlaku.

### 9. Hubungan dengan catatan kepatuhan (ADR 0085)

Petugasnya sama. Modul izin §4 diusulkan menjadi gerbang tunggal petugas lapangan OD & IR untuk kedua fitur (satu modul, dua izin), menjawab TBD "petugas ditunjuk" di [[HRIS - Industrial Relation]], supaya siapa petugasnya tercatat di satu tempat. Datanya tetap terpisah: catatan atribut bukan KPI, inspeksi Satgas adalah KPI.

## Consequences

### Yang membaik

- Nilai KPI 5R dihitung dari satu rumus di sistem, sehingga kelas kesalahan "skala campur, total 131" tertutup.
- Dokumentasi, nilai, dan KPI berada di satu tempat. Foto tak lagi tercecer di Drive yang tak terhubung ke angkanya.
- Field foto Form Builder berguna untuk form lain, termasuk tipe `report`.

### Yang memburuk atau tetap terbuka

- ⚠️ Form-builder kini punya dua aturan agregasi per orang: rata-rata untuk layanan, terakhir-menang untuk Satgas. Wajib dipilih eksplisit dari penanda, dengan uji yang membuktikan keduanya tidak tertukar.
- ⚠️ Nilai bergantung pada disiplin cek ulang. Temuan yang tak dicek ulang dalam periode tetap bernilai temuan. Ringkasan di menu §5 menampilkan siapa yang masih bertemuan justru untuk menahan ini.
- Temuan dan cek ulang tidak saling tertaut di data. Yang menyatukannya hanya urutan waktu per orang per periode.
- Daftar Office Boy dan Security yang dinilai dibekukan saat form terbit, jadi karyawan baru butuh form diterbitkan ulang.
- PIC tidak diberi tahu lewat aplikasi dan tak bisa melihat temuan atas dirinya. WhatsApp tetap dipakai.
- MyBharata versi lama melewati field foto lalu ditolak backend dengan pesan yang menyebut key field. Field foto jangan dibuat wajib sebelum petugas memperbarui aplikasinya.

### Konsekuensi deploy

- employee-service dan form-builder naik **bersama**: katalog izin diresolusi di yang satu dan ditegakkan di yang lain, dan sumber KPI baru memanggil endpoint internal baru. Sesudahnya erp-frontend, lalu MyBharata dengan version name dan versionCode dinaikkan.
- Sesudah deploy, IT memasang paket izin ke jabatan petugas, lalu petugas login ulang (token berlaku 72 jam).
- Katalog izin baru wajib terdaftar di seluruh tempat registrasinya. Yang terlewat gagal senyap ([[CORE - RBAC dan Permission Set]]).
- Tanpa env baru dan tanpa kategori inbox baru. Env unggah form-builder (`FILE_MODULE_URL`, `MINIO_FORM_KEY`) tercatat live sejak 2026-08-06, tetapi belum diukur ulang di prod.

### Yang sengaja tidak dilakukan

- Penilaian foto oleh AI, peringkat antar departemen, dan master area.
- Tipe form baru atau mesin status yang menautkan temuan ke cek ulang, beserta notifikasi ke PIC. Ditinjau ulang setelah satu atau dua bulan pemakaian bila penyebaran lewat WhatsApp tetap menjadi keluhan utama. Saat itu, kategori inbox baru menuntut form-builder dan notification-service naik bersama.
- Menaikkan batas 4 MB file-service.

### Belum Diputuskan (TBD, wajib dijawab HR sebelum go-live)

- Rumus konversi: `(v-1)/4` (rumus sistem, 3 = 50) atau `v/5` (praktik lembar HRD, 3 = 60).
- Cek ulang yang jatuh ke bulan berikutnya masuk periode mana.
- Jumlah field foto per orang, dan apakah foto wajib.
- Siapa selain petugas yang boleh membuka rekap web (usul: atasan Office Boy dan Security).
- Pemeriksaan jenis berkas di server. Hari ini hanya klien yang membatasi ke gambar.

## Dokumen Terkait

- [[Microservices - Form Builder Service]] (cara kerja, termasuk bagian Inspeksi Satgas 5R & K3) · [[API - Form Builder Service]]
- [[Microservices - Employee Service]] (sumber KPI, katalog izin) · [[Microservices - File Service]]
- [[CORE - RBAC dan Permission Set]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0039 Menu Terbatas Default Terbuka sampai Di-assign]] · [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]]
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] · [[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]]
- [[ADR - 0041 Izin Tipe Form Menempel di Departemen]] · [[REF - Penamaan Metrik & Sumber KPI]]
- [[HRIS - Matriks KPI per Departemen]] (metrik Office Boy dan Security) · [[GA - Checklist Management]]
- [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] · [[HRIS - Industrial Relation]]
- [[ADR - 0058 Kapabilitas AI Digerbang Kelayakan Data, Bukan Kelayakan Teknologi]] · [[HRIS - Kepatuhan Peraturan Perusahaan]]
- [[APP - MyBharata]] · [[APP - Web ERP]]

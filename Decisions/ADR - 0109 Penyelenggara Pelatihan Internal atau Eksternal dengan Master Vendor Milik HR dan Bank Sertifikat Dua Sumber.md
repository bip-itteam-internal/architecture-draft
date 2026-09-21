## Untuk Manajemen

- **Yang berubah di layar**: saat membuat butir rencana pelatihan dan saat membuat kelas, HR memilih penyelenggaranya **Internal** (departemen mana) atau **Eksternal** (vendor mana, dari daftar vendor pelatihan yang HR kelola sendiri di Pengaturan Pelatihan). Trainer eksternal bisa ditandai berasal dari vendor mana. Tiap kelas punya pilihan **memberi e-sertifikat atau tidak**, sehingga kelas yang memang tidak bersertifikat berhenti menerbitkan sertifikat. Tab Sertifikasi Pelatihan berubah menjadi **bank data**: sertifikat internal yang terbit sendiri, ditambah sertifikat dari pihak luar yang diunggah HR beserta nomor, tanggal, dan masa berlakunya. Sertifikat internal ikut memuat gambar tanda tangan, stempel, dan logo yang diunggah sekali. Di data karyawan muncul tab **Riwayat Pelatihan**: pelatihan apa saja yang pernah diikuti orang itu beserta sertifikatnya.
- **Siapa terdampak**: Training & Performance Officer dan HR (isian baru dan satu tempat mengunggah), karyawan (melihat sertifikatnya sendiri, termasuk yang dari pihak luar), dan atasan yang memakai riwayat pelatihan saat menimbang promosi atau penempatan.
- **Tidak dijanjikan**: **upload materi PPT tidak termasuk di keputusan ini** dan diputuskan terpisah, karena berkas presentasi umumnya melampaui batas ukuran unggah yang berlaku di seluruh sistem hari ini. Sistem **tidak** menghitung ikatan dinas 3 bulan maupun ganti rugi 50% biaya pelatihan; datanya tersedia, hitungannya tetap manual HR. Masa berlaku sertifikat **dicatat tanpa pengingat otomatis**. Evaluasi vendor tidak menghasilkan skor vendor; yang tersedia adalah rekap dan penilaian peserta per kelas. Dan satu hal yang menentukan semuanya: seluruh layar ini hanya sebaik data pesertanya. Per 17 September 2026, dari 13 kelas yang tercatat hanya 4 baris peserta yang pernah diinput, sehingga riwayat dan bank sertifikat akan tampak kosong sampai peserta kelas lama dimasukkan.
- **Besaran kerja**: sedang. Satu service backend, satu layar web bertambah beberapa isian dan dua tab baru, satu perubahan infrastruktur penyimpanan berkas, dan satu rilis aplikasi MyBharata untuk sertifikat pihak luar.

## Deskripsi

*Penyelenggara pelatihan dicatat eksplisit sebagai Internal (departemen) atau Eksternal (vendor), dengan **master vendor pelatihan milik HR di learning-service** alih-alih memakai master Pemasok Procurement yang terikat Accurate. Tiap kelas mendapat saklar e-sertifikat yang disimpan **terbalik** supaya form lama tidak mematikannya diam-diam. Tab Sertifikasi Pelatihan menjadi bank data dua sumber: sertifikat internal yang terbit otomatis dan sertifikat pihak luar yang diunggah HR, keduanya tampil per kelas maupun per karyawan. Spesimen tanda tangan, stempel, dan logo dihidupkan, membalik keputusan "teks saja" 2026-09-15. Materi PPT dipisah jadi keputusan sendiri karena batas unggah 4 MB.*

- **Status**: 🟡 **Diusulkan** 2026-09-18, disetujui pemilik proses (Opsi B: catatan dan bukti dulu, berkas besar menyusul). ✅ **Keputusan 1 (data peserta lebih dulu) sudah LIVE di PROD** (diukur 2026-09-21): bip-erp PR [#1969](https://github.com/bip-itteam-internal/bip-erp/pull/1969) dan erp-frontend PR [#1647](https://github.com/bip-itteam-internal/erp-frontend/pull/1647) merged 2026-09-18, DEV terverifikasi lewat gateway, PROD lolos gerbang biner dan bundel. Keputusan 2 sampai 11 **belum ada kodenya sama sekali**. Rencana T1: `.task-plans/2026-09-18-peserta-massal-pelatihan.md`.
- **Path di repo**: `bip-erp/services/learning/models_training.go` · `models_rencana.go` · `models_sertifikat.go` · `training.go` · `rencana.go` · `sertifikat.go` · `sertifikat_pdf.go` · `models_vendor.go` (baru) · `vendor.go` (baru) · `sertifikat_eksternal.go` (baru) · `bip-erp/services/file/main.go` (prefix `learning/`) · `erp-frontend/src/features/hris/training/list/components/training-form-modal.tsx` · `plan/components/plan-item-form-modal.tsx` · `masters/components/trainer-form-modal.tsx` · `certificate/components/certificate-settings-section.tsx` · `src/app/(main)/hris/employee/[id]/page.tsx` · `my-bharata/lib/src/features/training/*` (rilis berikutnya)
- **Tanggal**: 2026-09-18
- **Terkait**: [[HRIS - Training Program]] · [[Microservices - Learning Service]] · [[API - Learning Service]] · [[Microservices - File Service]] · [[REF - Kepemilikan Data]] · [[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]] · [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]] · [[HRIS - Kepatuhan Peraturan Perusahaan]]

## Context

Permintaan datang sebagai enam solusi dari pemilik proses (2026-09-17): penyelenggara Internal/Eksternal di butir rencana dan di kelas, vendor pada trainer eksternal, saklar e-sertifikat per kelas, bank data sertifikat dengan unggahan untuk yang eksternal, upload PPT materi, dan cara melihat riwayat pelatihan seseorang. Wawancara memisahkan empat kebutuhan di bawahnya: menjawab "siapa sudah dilatih apa, oleh siapa, dengan bukti apa" untuk audit, promosi, dan rekap; identitas penyelenggara yang konsisten supaya rekap internal versus eksternal dan evaluasi vendor bisa dihitung; materi tersimpan di satu tempat; dan sertifikat internal yang terlihat resmi. Keempatnya dipakai untuk keputusan nyata (audit, pemilihan vendor, rekap manajemen, promosi), jadi ini bukan laporan hiasan.

**Keadaan yang diukur, bukan diasumsikan.**

- Prod `learning_db` 2026-09-17 malam: `training` **13** (11 di antaranya dibuat hari itu, jadi HR sedang memasukkan kelas yang sudah berlangsung), `training_participant` **4** (12 kelas nol peserta), `training_certificate` **0**, `training_plan_item` **0**, `trainer` 7 (5 internal, 2 eksternal), `course` 1, `quiz` 1 (hanya `post`), `training_certificate_setting` 1 dengan hanya nama dan jabatan penanda tangan. Tiga kelas punya `cost` terisi, tertinggi Rp25 juta.
- Salah satu trainer eksternal prod mengisi `qualification = "Vendor"`. Tidak ada tempat untuk asal vendor, jadi orang menaruhnya di kolom terdekat. Ini bukti kebutuhan (2), diukur bukan ditebak.
- **Trainer** punya `is_internal` dan `employee_id`, tanpa satu pun field vendor (`services/learning/models_training.go:76-90`).
- **Kelas** sudah punya `department_key` yang artinya departemen **penyelenggara**, bukan sasaran (`services/learning/models_rencana.go:78-79`), dan di web isian itu memang sudah berlabel "Penyelenggara" (`erp-frontend/src/features/hris/training/list/components/training-form-modal.tsx:207-213`). Yang belum ada hanya pembedaan Internal/Eksternal dan vendornya.
- **Butir rencana** punya `department_keys` sebagai departemen **sasaran**, informasional, boleh lebih dari satu (`models_rencana.go:80-83`). Sasaran dan penyelenggara dua hal berbeda, jadi penyelenggara tetap belum ada.
- **Sertifikat** terbit otomatis untuk setiap kelas `Completed` yang syaratnya terpenuhi, tanpa saklar per kelas (`models_sertifikat.go:135-157`), dipicu peristiwa tanpa cron (`sertifikat.go:370-378`).
- **Spesimen tidak ada, dan itu disengaja**: PDF dibuat tanpa gambar tanda tangan, stempel, maupun logo (`services/learning/sertifikat_pdf.go:15-17`, `:142`), dan testnya menolak PDF yang memuat `/Subtype /Image` (`sertifikat_pdf_test.go:86-87`). Keputusan lingkupnya tertulis di `.task-plans/2026-09-15-rencana-sertifikat-pelatihan.md:622` sebagai "teks saja". Jadi anggapan dalam permintaan bahwa "spesimennya sudah ada" **tidak benar**; pemilik proses mengonfirmasi 2026-09-18 bahwa yang dimaksud gambar tanda tangan **beserta stempel dan logo**.
- **Unggahan berkas**: file-service dan pola kliennya sudah teruji di enam modul, tetapi `handleUpload` dibatasi **4 MB** (`services/file/main.go:337-338`) dan tidak memvalidasi MIME sama sekali, sehingga daftar-izin dipasang di pemanggil (pola [[ADR - 0075 Bukti Sisi Lawan Dilampirkan dan Angkanya Dicatat, Pembacaan Otomatis Menyusul]]). Learning-service **belum pernah** memakainya: `InternalURL` kosong (`services/learning/main.go:20-23`) dan compose learning tak punya `FILE_MODULE_URL`. Prefix `learning/` belum ada di daftar sepuluh prefix. Menaikkan batas 4 MB sengaja tidak dilakukan dua kali sebelumnya (ADR 0075, [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]]).
- **Master Pemasok** ada di procurement (`services/procurement/models.go:105-169`), 139 dokumen prod, tetapi kategorinya terikat **nama kategori di Accurate** (`models.go:12-18`: Pemasok Bahan Baku, Pemasok Bahan Kemas, Umum), tanpa kategori jasa pelatihan, **tanpa `company_id`**, dan tulisnya digerbang izin procurement yang tidak dipegang HR. Pemilik proses memilih 2026-09-18: master vendor pelatihan dikelola HR sendiri.
- **Riwayat per karyawan**: `GET /training/history/:employeeId` ada dan mengembalikan **baris pendaftaran mentah** `{data: []TrainingParticipant, count}` tanpa judul, tanggal, trainer, maupun sertifikat (`services/learning/training.go:673-680`). Konsumennya **nol**: di erp-frontend satu-satunya pemanggil `/history` adalah jalur `me` (`src/features/hris/training/evaluation/hooks/use-evaluation.ts:52`), dan di MyBharata hanya `/me/trainings/history`. Jadi bentuknya boleh diubah.
- **Aturan perusahaan yang belum pernah masuk sistem**: `mybharata-app/docs/policy/leave_terms.md:84-86` menetapkan pelatihan eksternal bersertifikat mewajibkan bekerja minimal **3 bulan** pasca-pelatihan, dan resign sebelum itu dikenakan ganti rugi **50% dari total biaya pelatihan**. Tidak ada di vault (pola `ikatan dinas` nol hit di folder HRIS, Decisions, Reference) dan tidak ada di kode bip-erp. `BUSINESS_LOGIC_IMPLEMENTATION.md` sendiri tidak memuat pasal pelatihan sama sekali, jadi peta kepatuhan [[HRIS - Kepatuhan Peraturan Perusahaan]] juga belum menyebutnya.

⚠️ **Landasan dok yang belum sepenuhnya kokoh**: [[HRIS - Training Program]] berstatus ⚠️ MVP Implemented, [[API - File Service]] ⚠️ (RBAC per peran masih TBD), dan [[HRIS - Dashboard per Posisi]] memuat baris Training & Performance Officer yang sudah basi. Keputusan di bawah berdiri di atas **kode `origin/main` yang dibaca langsung**, bukan di atas dok itu.

Yang ditolak saat analisa:

- **Memakai master Pemasok Procurement sebagai master vendor pelatihan**: kategori terikat Accurate, tanpa `company_id`, dan HR tak punya izin menulisnya. Konsultan perorangan yang tak pernah ditagih lewat pembelian juga tak akan ada di sana.
- **Menurunkan penyelenggara kelas dari trainer**: seorang trainer eksternal bisa berpindah vendor, dan kelas yang diselenggarakan vendor bisa dibawakan trainer yang identitas vendornya berbeda. Menurunkannya berarti rekap vendor berubah arti saat master trainer disunting.
- **Menyimpan saklar sertifikat sebagai `beri_sertifikat` (positif)**: `PUT /training/:id` memakai `ReplaceOne` (`services/learning/training.go:422`), jadi form lama yang tidak mengirim field membuat bool jatuh ke `false` dan **mematikan sertifikat seluruh kelas tanpa satu pun galat**.
- **Menggabungkan sertifikat eksternal ke koleksi `training_certificate`**: yang internal adalah snapshot bernomor yang sengaja tak bisa disunting dan punya alur pencabutan; menyatukannya membuat sertifikat resmi bisa diketik tangan.
- **Upload PPT lewat jalur 4 MB yang ada**: berkas presentasi pelatihan umumnya lebih besar, dan menaikkan batas global sudah dua kali ditolak ADR lain. Karena itu materi dipisah, bukan dipaksa masuk.
- **Memasang masa berlaku sertifikat ke kalender sekarang**: pemilik proses memilih "cukup dicatat". Bila kelak perlu diingatkan, jalurnya feed `calendar-service`, bukan halaman kalender sendiri.

## Decision

### 1. Data peserta lebih dulu, dan itu bagian dari keputusan ini

Sebelum layar apa pun di bawah dibangun, HR mengisi peserta kelas yang sudah berlangsung, dan sistem dibuat memudahkannya: **tambah peserta beberapa orang sekaligus** untuk satu kelas, plus peringatan di layar saat kelas yang ditambahi sudah `Completed`. Menambah peserta ke kelas Completed **tetap diizinkan** (hari ini pun tidak ada penjaga status, hanya duplikat dan kuota lewat `CanEnroll`, `models_training.go:202-216`), karena pengisian data lama justru butuh itu. Yang ditambahkan hanya peringatan, bukan penjaga.

Alasannya bukan kerapian: riwayat per karyawan, bank sertifikat, rekap internal versus eksternal, dan evaluasi vendor semuanya berhitung dari `training_participant`, dan hari ini isinya 4 baris untuk 13 kelas. Membangun layarnya lebih dulu menghasilkan lima layar benar yang semuanya kosong, dan kekosongan itu akan terbaca sebagai fiturnya tidak jalan.

⚠️ Konsekuensi yang diterima sadar: peserta yang ditambahkan ke kelas bermateri **sesudah** kelas Completed tidak bisa lagi mengerjakan pre-test, sehingga post-testnya tertutup permanen (`pre_test_terlewat`, aturannya di [[HRIS - Training Program]] Alur Ujian E-Learning). Untuk kelas lama yang memang tanpa materi, ini tidak berlaku.

⚠️ **Koreksi premis, 2026-09-18** (ditulis sesudah kodenya dikerjakan): yang satu-per-permintaan itu **endpoint backend**, sementara **layarnya sudah lama** menugaskan banyak orang sekaligus lewat multi-select. Jadi ini bukan fitur baru melainkan tiga cacat pada yang sudah ada, dan ketiganya senyap: cacahan yang gagal dihitung lalu tak pernah ditampilkan (sepuluh penolakan tetap tampil sebagai kabar sukses "0 peserta ditambahkan"); kuota bisa **dilampaui** karena N permintaan paralel masing-masing memeriksanya atas bacaan daftar pesertanya sendiri, dan unique index hanya menjaga duplikat; dan tak ada peringatan sama sekali untuk kelas yang sudah selesai. Isi keputusan ini tidak berubah, hanya sebabnya. Rujukan `CanEnroll` yang semula ada di butir ini juga sudah tidak berlaku: fungsi itu dihapus karena nol pemanggil produksi, dan aturan duplikat serta kuota kini tinggal di `services/learning/models_participant.go` (`PilihYangBolehMasuk`).

⚠️ **Temuan sampingan yang ikut diperbaiki di task yang sama**: kuota `max_participants` ditegakkan server sebagai cap keras sejak 2026-08-11, tetapi **tak punya isian di layar mana pun**, sementara keterangan di bawah form Buat Pelatihan justru menyatakan kapasitas mengikuti jumlah yang ditugaskan. Lebih jauh, karena `PUT /training/:id` mengganti seluruh dokumen sementara form tak membawa field itu, **menyunting judul atau lokasi kelas diam-diam mengosongkan kuotanya**. Isian Kapasitas Peserta karena itu masuk ke form pada task ini, bukan ditunda.

**Status kode T1** (diukur ulang 2026-09-21): rute massal, laporan per orang, peringatan kelas selesai, dan isian kuota **merged dan LIVE di PROD**. bip-erp PR [#1969](https://github.com/bip-itteam-internal/bip-erp/pull/1969), erp-frontend PR [#1647](https://github.com/bip-itteam-internal/erp-frontend/pull/1647), keduanya merged 2026-09-18.

- **DEV terverifikasi lewat gateway** 2026-09-21 dengan kelas uji yang dibuat lalu dihapus: rute lama tetap 201 dan duplikatnya 409 berkalimat lama; batch 3 id yang satu sudah terdaftar membalas `diterima 2` beserta satu penolakan `sudah_terdaftar`; kelas berkuota 1 menolak dua kandidat sekaligus dengan `kuota_penuh` dan pesertanya TETAP 1, yang membuktikan kuota benar-benar ditegakkan; daftar kosong dan 251 id sama-sama 400, yang kedua menyebut batas 250.
- **PROD** lolos gerbang biner (rute batch dan `PilihYangBolehMasuk` ada di biner yang berjalan, `CanEnroll` 0, kontrol negatif 0) dan gerbang bundel frontend (kunci baru ada, kunci lama `capacityHint` 0). Perilakunya TIDAK diuji di prod karena menulis ke prod dilarang.
- ⚠️ **Yang masih belum**: satu perjalanan layar utuh sebagai orang. Dan yang menentukan nilai seluruhnya, data prod 2026-09-21 masih **4 baris peserta** untuk 13 kelas (11 kelas nol, 0 sertifikat, pendaftaran terbaru 2026-09-17): alat pengisiannya sudah live, tetapi belum dipakai. Selama itu belum terjadi, bank sertifikat dan riwayat per karyawan akan tetap tampak kosong, dan itu keadaan data, bukan kerusakan.

### 2. Penyelenggara dicatat eksplisit, dan rencana versus realisasi adalah dua fakta

- **Kelas** mendapat `penyelenggara_jenis ∈ {internal, eksternal}`. Bila `internal`, penyelenggaranya `department_key` **yang sudah ada** dan artinya tidak berubah; tidak ada field departemen baru. Bila `eksternal`, `vendor_id` wajib merujuk master vendor (keputusan 3), dan `department_key` tetap boleh diisi sebagai departemen pendamping di dalam.
- **Butir rencana** mendapat pasangan field yang sama, artinya **rencana**: pelatihan ini direncanakan diselenggarakan internal oleh departemen X atau eksternal lewat vendor Y. Ini bukan duplikasi dari kelas: butir rencana menyimpan niat, kelas menyimpan pelaksanaannya, dan selisih keduanya justru informasi yang berguna. `department_keys` di butir rencana tetap berarti **sasaran** dan tidak boleh dibaca sebagai penyelenggara.
- **Kelas dan butir yang sudah ada** tidak dimigrasi. `penyelenggara_jenis` yang absen dibaca **internal**, karena itulah arti `department_key` yang sudah terisi di 13 kelas prod. Yang absen tidak boleh dibaca "belum diisi" lalu memaksa HR menyunting ulang.

### 3. Master vendor pelatihan milik learning-service, dikelola HR

Koleksi baru `training_vendor` di `learning_db`: `{ company_id, nama, jenis ∈ {vendor, konsultan, lembaga}, kontak?, email?, alamat?, catatan?, pemasok_vendor_no?, is_active }`, nama unik per perusahaan tanpa beda kapitalisasi, dikelola di **Pengaturan > Pengaturan Pelatihan** sebagai tab baru, digerbang izin yang sama dengan master trainer (`PermTrainingManage` + `RequireHRISStaff`).

- Sesuai aturan 3 di [[REF - Kepemilikan Data]]: fakta baru di domain yang sudah ada menjadi **koleksi baru di service pemilik domain**, bukan service baru dan bukan field tempelan di koleksi milik procurement.
- `pemasok_vendor_no` **opsional dan hanya rujukan**, bukan salinan: nama dan data pemasok tetap milik procurement dan tidak pernah disalin ke `training_vendor`. Kalau kelak pembayaran vendor pelatihan perlu disambungkan ke pembelian, rujukan itu jalannya. Tidak ada penulis kedua, jadi tidak ada drift yang perlu dijaga pemindai.
- Vendor **tidak pernah dihapus keras** bila sudah dirujuk kelas atau butir rencana; hanya dinonaktifkan. Master trainer hari ini boleh dihapus walau masih dipakai kelas (`training.go:292`), dan itu pola yang sengaja tidak diulang.

### 4. Vendor pada trainer adalah AFILIASI, bukan penentu penyelenggara

`trainer` mendapat `vendor_id` opsional, hanya bermakna bila `is_internal = false`. Ia menjawab "trainer ini orang dari mana", dan berguna saat memilih trainer.

⛔ **Penyelenggara kelas TIDAK diturunkan dari trainer, dan rekap vendor TIDAK dihitung dari `trainer.vendor_id`.** Yang dihitung selalu `vendor_id` yang tersimpan di kelas. Layar boleh **menyarankan** vendor trainer saat HR memilih trainer eksternal, tetapi yang tersimpan adalah pilihan di kelas. Dua field ini terlihat seperti satu fakta dan bukan: trainer bisa berpindah vendor, dan kelas yang sudah lewat tidak boleh berubah penyelenggaranya karena master trainer disunting.

### 5. Saklar e-sertifikat per kelas, disimpan TERBALIK

Kelas mendapat `tanpa_sertifikat bool` (bukan `beri_sertifikat`). Artinya:

- Field **absen atau `false` berarti menerbitkan sertifikat**, yaitu perilaku hari ini, sehingga 13 kelas prod dan form versi lama tidak berubah arti.
- `true` berarti kelas ini tidak menerbitkan e-sertifikat internal. `syaratSertifikat` mengembalikan tidak berhak dengan alasan baru `kelas_tanpa_sertifikat`, dan status per peserta menampilkannya sebagai keterangan, bukan sebagai kegagalan.
- **Menyalakan `tanpa_sertifikat` pada kelas yang masih punya sertifikat aktif ditolak 409**, sejalan dengan `DELETE /training/:id` yang sudah menolak kelas bersertifikat aktif (`sertifikat.go:359-368`). HR mencabut dulu bila memang salah terbit. Mematikannya diam-diam sambil membiarkan sertifikat yang sudah beredar akan membuat dua pernyataan yang bertentangan hidup bersamaan.
- Mematikan saklar (kembali ke menerbitkan) memicu sinkron seperti peristiwa lain lewat `picuSinkronSertifikat`.

Pilihan ini yang menyambung ke permintaan "biar nyambung dengan e-sertifikat otomatis": kelas eksternal yang sertifikatnya datang dari vendor ditandai `tanpa_sertifikat`, lalu buktinya masuk lewat keputusan 6.

### 6. Bank sertifikat = satu layar, dua koleksi

Koleksi baru `training_certificate_external`: `{ company_id, employee_id, judul, penerbit_vendor_id? , penerbit_nama, nomor?, tanggal_terbit, berlaku_sampai?, training_id?, berkas { object, nama, ukuran, tipe }, catatan?, metadata }`.

- **HR yang mengunggah** (keputusan pemilik proses 2026-09-18), digerbang `PermTrainingWork` + `RequireHRISStaff`; **karyawan melihat dan mengunduh miliknya sendiri**, `employee_id` selalu dari header identitas gateway, tidak pernah dari path atau query, sama dengan sertifikat internal (`sertifikat.go:602-624`).
- Berkas `.pdf`, `.jpg`, `.jpeg`, `.png`, maksimal 4 MB, daftar-izin ditegakkan **di learning-service** karena file-service tidak memvalidasi tipe (pola ADR 0075). Sertifikat selembar muat di 4 MB, jadi batas itu tidak menghalangi apa pun di sini.
- **Tidak bernomor sistem**: nomornya milik penerbit dan diketik apa adanya, boleh kosong. Penomoran `NNN/SERT/...` tetap khusus sertifikat internal dan tetap tak pernah dipakai ulang.
- **Masa berlaku dicatat, tanpa pengingat**: `berlaku_sampai` opsional, statusnya (berlaku, kedaluwarsa, tanpa masa berlaku) **dihitung saat dibaca**, tidak disimpan, supaya tidak ada dua sumber yang bisa berselisih. Tidak ada cron, tidak ada notifikasi inbox, dan **tidak** didaftarkan ke feed kalender pada keputusan ini.
- Layar "Sertifikasi Pelatihan" menampilkan **gabungan dua sumber** dengan penanda asal (Internal terbit sistem / Eksternal diunggah), bisa disaring per karyawan dan per kelas. Yang digabung hanya **tampilannya**; koleksinya tetap dua, dan sertifikat internal tetap tak bisa disunting tangan.
- Rute baru `GET /training/certificates/by-employee/:employeeId` melayani kedua sumber untuk satu orang, digerbang `PermTrainingView` + `RequireHRISStaff` (gerbang KHUSUS, bukan fallback `nil`, alasannya sama dengan rute sertifikat yang sudah ada). Didaftarkan **sebelum** `/training/certificates/:certId/pdf` supaya tidak tertelan rute ber-parameter.

### 7. Spesimen tanda tangan, stempel, dan logo dihidupkan

`training_certificate_setting` bertambah `spesimen_ttd { object, nama }`, `stempel { object, nama }`, dan `logo { object, nama }`, ketiganya opsional, gambar `.png` atau `.jpg` maksimal 2 MB, diunggah di tab Pengaturan Pelatihan yang sama dengan nama dan jabatan penanda tangan.

- **Ini membalik keputusan 2026-09-15** ("teks saja", `.task-plans/2026-09-15-rencana-sertifikat-pelatihan.md:622`; `sertifikat_pdf.go:15-17`). Pembalikan dicatat di sini supaya tidak terbaca sebagai kelalaian, dan test yang menolak `/Subtype /Image` (`sertifikat_pdf_test.go:86-87`) **diubah sadar**: yang dikunci berubah menjadi "gambar muncul hanya bila pengaturannya punya berkasnya", bukan "tidak ada gambar".
- **PDF tetap deterministik** (katalog terurut, tanggal dari `terbit_at`): berkas yang sama menghasilkan bytes yang sama. Gambar dibaca dari object yang sama selama pengaturannya tidak diganti.
- **Isi sertifikat yang sudah terbit tetap dibekukan.** Sertifikat lama tidak mendadak bergambar; pengaturan gambar berlaku untuk PDF yang dibangkitkan sesudahnya, sama seperti nama penanda tangan hari ini yang tidak mengubah snapshot. ⚠️ Ini berarti dua sertifikat dari kelas yang sama bisa tampil berbeda bila spesimen diganti di antaranya, dan itu diterima sadar karena alternatifnya menyimpan gambar ke dalam setiap snapshot.
- Ketiga gambar disimpan di file-service, **bukan base64 di Mongo**: dokumen pengaturan dibaca di setiap pembangkitan PDF, dan menanam gambar di dalamnya membuat setiap pembacaan menyeret ratusan KB.

### 8. Prefix `learning/` di file-service, dengan akses baca lewat proxy

Prefix tulis kesebelas `learning/` ditambahkan beserta env kunci aksesnya di file-service **dan** `FILE_MODULE_URL` di learning-service. Object key: `learning/certificate-external/<employee_id>/<hex><ext>` dan `learning/certificate-setting/<company_id>/<jenis>-<hex><ext>`, hex acak supaya unggahan tidak saling menimpa (`POST /upload` menimpa object lama tanpa peringatan).

Sertifikat orang lain dan spesimen tanda tangan **tidak boleh** dijangkau lewat kunci baca yang tertanam di bundel browser, jadi prefix ini dibuat **tanpa kunci baca** dan dibaca lewat proxy di learning-service yang menilai identitas pemanggil, pola yang sama dengan arsip kontrak ([[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]] §9).

### 9. Riwayat pelatihan per karyawan memperluas endpoint yang sudah ada

`GET /training/history/:employeeId` berhenti mengembalikan baris pendaftaran mentah dan mengembalikan baris kaya: judul kelas, jenis, tanggal, trainer, penyelenggara (internal dengan departemennya atau eksternal dengan vendornya), kehadiran, status post-test, dan sertifikat yang dimiliki dari kelas itu. Bentuknya mengikuti `MeTraining` yang sudah ada (`services/learning/me.go:16-97`) supaya tidak lahir dua bentuk untuk satu hal.

Mengubah bentuknya **aman dan diverifikasi**: nol konsumen di erp-frontend dan MyBharata. Layarnya tab baru **Riwayat Pelatihan** di data karyawan, di samping tab Dokumen, hanya untuk pemegang `training.view`. Karyawan tetap melihat miliknya sendiri lewat jalur `me`; ini bukan data pribadi orang lain yang dipindah ke layar umum, melainkan riwayat pekerjaan yang dibaca HR.

### 10. Materi pelatihan (PPT) dipisah jadi keputusan sendiri

Upload materi **tidak** diputuskan di sini. Yang membuatnya beda dari lima keputusan di atas: berkas presentasi umumnya melampaui 4 MB, sehingga ia menuntut keputusan tersendiri soal jalur unggah (presigned PUT langsung ke MinIO, yang hari ini hanya disediakan untuk inventory dan manufacture), batas ukuran, cara menampilkan di web, dan cara membukanya di MyBharata yang jalur unduhnya terkunci ke PDF. Menyeretnya ke sini akan menahan bagian yang sudah jelas.

### 11. Ikatan dinas tidak dihitung sistem

`leave_terms.md:84-86` (pelatihan eksternal bersertifikat mengikat 3 bulan, ganti rugi 50% biaya bila resign lebih awal) **tidak diotomatiskan** oleh keputusan ini, dan tidak ada penjaga yang menahan resign. Yang dilakukan keputusan ini hanya membuat datanya ada dan bisa ditelusuri: penyelenggara eksternal per kelas, biaya kelas (`cost`, tetap informasional, [[ADR - 0001 Akuntansi via Accurate]]), sertifikat yang diperoleh, dan tanggalnya.

⚠️ Yang menghalangi otomatisasi bukan kodenya: "total biaya pelatihan" per orang belum terdefinisi ( `cost` adalah biaya kelas, bukan per peserta), dan aturan itu belum pernah masuk peta kepatuhan. Bila kelak diotomatiskan, ia menyentuh uang dan karena itu wajib ADR sendiri beserta pembacaan Peraturan Perusahaan, sesuai [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]].

## Consequences

**Yang menjadi mungkin**

- Rekap "berapa pelatihan internal versus eksternal, dari vendor mana" dan riwayat pelatihan per orang beserta buktinya, keduanya dari data yang sama tanpa spreadsheet.
- Kelas yang memang tidak bersertifikat berhenti menerbitkan sertifikat, dan sertifikat dari pihak luar punya tempat resmi yang bisa dicari saat audit.
- Sertifikat internal bisa dipakai sebagai dokumen yang layak diedarkan, karena bertanda tangan, berstempel, dan berlogo.

**Urutan dan ongkos deploy**

- **Dua container harus naik bersama** untuk prefix `learning/`: file-service (yang mengenali prefix dan kunci aksesnya) dan learning-service (yang memegang `FILE_MODULE_URL` dan kuncinya). Env baru berarti container **dibuat ulang** (`--force-recreate`), bukan di-restart, karena env dibaca saat container dibuat. Kunci yang kosong gagal **senyap** sebagai `invalid access key`, dan dua prefix yang kuncinya bernilai sama membuat keduanya dibuang.
- **Backend sebelum frontend** untuk setiap perubahan kontrak di atas.
- **`ReplaceOne` adalah jebakan nyata di tiga tempat**: PUT trainer (`training.go:280`), PUT kelas (`:422`), PUT course (`course.go:110`). Setiap field baru wajib ikut dipertahankan seperti `plan_item_id` dan `course_id` sekarang (`rencana_tautan.go:24-36`), atau dikirim lengkap oleh form. Untuk butir rencana sebaliknya: PUT memakai `$set` eksplisit dan input di-whitelist (`rencana.go:31-52`, `:233-245`), jadi field baru yang lupa didaftarkan akan **diabaikan diam-diam** tanpa galat.
- **Pembaca yang tidak terganggu**: feed kalender learning membaca judul, tanggal, jam, status, dan lokasi; sumber KPI `pelatihan` membaca status, tanggal, peserta, ujian, dan penilaian; sumber `rencana_pelatihan` membaca tahun, bulan, judul, status, dan tautan kelas. Tidak satu pun menyentuh field baru, jadi KPI dan kalender tidak berubah arti. ⛔ Konsekuensinya juga harus dinyatakan: **`penyelenggara_jenis` dan `vendor_id` tidak menjadi metrik KPI apa pun** pada keputusan ini.

**MyBharata**

- Aplikasi yang beredar **tidak patah**: modelnya hanya membaca kunci yang disebut eksplisit dan memperlakukan yang absen sebagai `false`, dan `sertifikat_tersedia` dihitung server (`my_bharata/lib/src/features/training/data/models/my_training_model.dart:51,69-73`).
- Dua hal **menunggu rilis store**, jadi janji "karyawan melihat sertifikatnya" baru tiba di rilis berikutnya: (a) sertifikat eksternal tidak boleh disajikan lewat `GET /me/trainings/:id/certificate`, karena unduhan aplikasi mengunci `Accept: application/pdf` dan menamai berkasnya `.pdf` tanpa memeriksa content-type, sehingga sertifikat berupa JPG akan tersimpan sebagai PDF rusak; ia butuh rute dan layar baru. (b) kalimat sesudah post-test lulus yang menjanjikan "sertifikat terbit sendiri" menjadi keliru untuk kelas ber-`tanpa_sertifikat` (`lib/l10n/app_id.arb:57`).
- Sampai rilis itu, bank sertifikat dipakai HR dan karyawan melihat sertifikat internalnya seperti sekarang.

**Risiko dan yang diterima sadar**

- **Layar kosong bila peserta tidak diisi.** Ini risiko terbesar dan satu-satunya yang tidak bisa diselesaikan kode. Keputusan 1 menaruhnya di depan justru karena itu.
- **Vendor ganda berpotensi muncul** bila HR mengetik vendor yang sama dengan ejaan berbeda. Yang menahannya hanya nama unik per perusahaan tanpa beda kapitalisasi; kemiripan ("PT Sinergi" versus "Sinergi Training") tidak dideteksi.
- **Rujukan `pemasok_vendor_no` bisa menunjuk pemasok yang dihapus atau diganti**, karena procurement tidak punya endpoint hapus hari ini dan tidak ada pemberitahuan perubahan. Rujukan itu keterangan, bukan kunci hitungan, jadi kerusakannya terbatas pada tautan yang tak menemukan apa-apa.
- **Sertifikat eksternal adalah klaim yang diunggah HR**, bukan yang diverifikasi ke penerbit. Bila dipakai sebagai bukti audit, keasliannya tetap tanggung jawab manusia.
- **Spesimen tanda tangan adalah gambar yang bisa disalahgunakan.** Karena itu prefixnya tanpa kunci baca dan aksesnya lewat proxy (keputusan 8). Menyimpannya di prefix berkunci baca akan membuat gambar tanda tangan direktur dapat diambil siapa pun yang membuka bundel browser.

**Dokumentasi**

- Aturan pemakaian yang wajib hidup di dok, bukan hanya komentar Go: penyelenggara kelas tidak diturunkan dari trainer (keputusan 4), `department_keys` butir rencana adalah sasaran dan bukan penyelenggara (keputusan 2), dan saklar sertifikat bermakna terbalik (keputusan 5). Ketiganya sudah dicatat di [[HRIS - Training Program]] dan [[Microservices - Learning Service]] saat kodenya masuk.
- [[REF - Kepemilikan Data]] bertambah dua baris (vendor pelatihan, sertifikat eksternal) dan kelak baris materi bila keputusan 10 diambil.

**Daftar task**: `Workspace/ANALISA - Penyelenggara dan Bank Sertifikat Pelatihan`.

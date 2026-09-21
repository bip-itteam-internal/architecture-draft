## Untuk Manajemen

- **Yang berubah di layar**: tidak ada, dan itu disengaja. Keputusan ini justru menahan pembangunan empat modul baru (program perbaikan kinerja, talent mapping 9-box beserta talent pool, analisis kebutuhan pelatihan, dan program pengembangan) sampai ada keputusan nyata yang menunggunya.
- **Siapa terdampak**: HR People & Development, yang untuk sementara tetap memakai spreadsheet seperti sekarang. Satu hal yang berubah untuk mereka: penilaian KPI bulanan harus berhenti dikerjakan di dua tempat.
- **Tidak dijanjikan**: tidak ada modul baru yang dibangun dari keputusan ini. Jalur "KPI rendah lalu surat peringatan" **tidak** diotomatiskan, karena Peraturan Perusahaan yang berlaku sama sekali tidak menyebut KPI sebagai pemicu surat peringatan. Penyatuan KPI juga belum memutuskan sisi mana yang menang; yang diputuskan baru bahwa satu sumber itu wajib.
- **Besaran kerja**: kecil. Membandingkan dua sumber KPI untuk periode yang sama, lalu satu keputusan pemilik proses. Tidak ada service baru, tidak ada layar baru.

## Deskripsi

*Permintaan memindahkan 25 sheet Dashboard People & Development ke ERP ditunda, karena pengukuran menemukan tidak ada keputusan yang menunggu pemindahan itu, sementara menemukan masalah lain yang tidak ditanyakan dan lebih mahal: KPI bulanan sudah hidup di DUA tempat sekaligus, dan seluruh angka turunan di spreadsheet bergantung padanya. Modul Training yang dibangun lengkap tahun ini juga terbukti hampir kosong, jadi menambah empat modul lagi kemungkinan besar mengulang pola yang sama.*

- **Status**: 🟡 **Diusulkan** 2026-09-21, disetujui pemilik proses hari yang sama (opsi A dari tiga opsi yang disajikan). Tidak ada kode yang dibangun dari keputusan ini; yang dihasilkan adalah penundaan bersyarat beserta satu pekerjaan data.
- **Path di repo**: tidak ada berkas kode yang disentuh. Yang dirujuk dan **tidak** diubah: `bip-erp/services/employee` (`kpi_score`, `kpi_template`, `kpi_template_assignment`), `bip-erp/services/learning` (modul Training), `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` (aturan surat peringatan).
- **Tanggal**: 2026-09-21
- **Terkait**: [[REF - Peta Spreadsheet People and Development ke ERP]] · [[HRIS - Work Review]] · [[HRIS - Career & Promotion]] · [[HRIS - Training Program]] · [[HRIS - Kepatuhan Peraturan Perusahaan]] · [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]] · [[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]] · [[ADR - 0109 Penyelenggara Pelatihan Internal atau Eksternal dengan Master Vendor Milik HR dan Bank Sertifikat Dua Sumber]]

## Context

Permintaannya datang sebagai analisis mandiri atas spreadsheet Dashboard People & Development 2026 (25 sheet, ±170 karyawan) yang mengusulkan meringkasnya jadi 6 modul dan ±18 tabel di sistem. Usulan itu rapi dan analisis kualitas datanya benar. Yang belum dilakukan adalah memeriksa apakah ERP sudah memiliki sebagiannya, dan apakah ada keputusan yang benar-benar menunggu.

**Keadaan yang diukur, bukan diasumsikan** (`origin/main` dan prod, 2026-09-21).

- **Sudah ada di ERP dan dipakai**: KPI bulanan per karyawan. `kpi_score` prod berisi **679 skor**, dengan **108 sampai 165 karyawan per bulan** untuk April sampai Agustus 2026, ditopang **119** `kpi_template` dan **207** `kpi_template_assignment`. Ini bukan modul kosong; ini dipakai menilai orang setiap bulan.
- **Sudah ada di ERP tetapi hampir kosong**: seluruh domain Training pelaksanaan (`training`, `training_participant`, `training_type`, `trainer`, `course`, `quiz`, `quiz_attempt`, `trainer_evaluation`, `training_certificate`, `training_plan_item`, `training_request`). Prod 2026-09-21: **13 kelas, 4 baris peserta, 0 sertifikat, 0 butir rencana, 1 evaluasi trainer**.
- **Sudah lebih maju daripada spreadsheet**: sheet REPORT PERFORMANCE TRAINING VS KPI tidak perlu dibangun, karena dampak pelatihan ke KPI sudah menjadi metrik KPI otomatis `kenaikan_kpi_peserta_persen` ([[ADR - 0102 Kesesuaian Materi Dinilai Peserta dan Dampak Pelatihan dari Kenaikan Skor KPI]]).
- **Belum ada sama sekali** (`git grep` ke `origin/main`, nol berkas untuk masing-masing): `improvement_plan` (KPK), `talent_assessment` dan `nine_box` (9-box), `talent_pool`, TNA sebagai kata, `training_vendor`, `development_program`, `kompetensi` dan `competency`, `silabus`. Kata `bootcamp` dan `magang` memang muncul, tetapi keduanya soal pengecualian KPI dan jenis kontrak PKWT, bukan modul program.

⛔ **Temuan yang tidak ditanyakan dan menentukan keputusan ini: KPI bulanan hidup di DUA tempat.** ERP menilai 108 sampai 165 orang per bulan; spreadsheet memegang fakta yang sama untuk ±170 orang Januari sampai Desember. Cakupannya pun berbeda, karena ERP tidak punya skor Januari dan Februari dan hanya 1 orang di Maret. Ini kelas kerusakan yang paling sering menggigit di repo ini, yaitu satu fakta di dua tempat yang menyimpang diam-diam tanpa satu pun galat. Yang membuatnya lebih berat di sini: **hampir seluruh sheet lain adalah turunan KPI** (KPK, 9-box, talent pool, training versus KPI), jadi selama ada dua sumber KPI, setiap angka turunannya tidak punya jawaban tunggal.

⛔ **Gerbang aturan bisnis dijalankan, dan hasilnya mengejutkan.** Karena KPK bermuara ke surat peringatan, `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` dibuka lebih dulu sesuai [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]]. Dokumen yang menang itu memicu SP 1 dari **kehadiran** (terlambat 3x sebulan), dan menyebut kata "KPI" **nol kali**. Jadi jalur "KPI rendah lalu KPK lalu SP 1" yang dipakai spreadsheet tidak punya dasar di aturan yang tertulis.

⚠️ **Status dokumen yang menopang**: [[HRIS - Work Review]] berstatus 🟡 Konsep untuk siklus review, dan [[HRIS - Career & Promotion]] menyatakan kaderisasi **baru desain**. Jadi bila empat modul itu dibangun sekarang, ia berdiri di atas rencana, bukan kenyataan.

**Pemilik proses ditanya dua hal yang tidak bisa dijawab indeks maupun kode**, dan jawabannya mengubah arah: (1) tidak ada keputusan yang mendesak berubah, spreadsheet masih jadi tempat memutuskan, jadi yang diminta memindahkan penyimpanan; (2) hasil talent mapping hanya boleh dilihat HR.

## Decision

1. **Empat modul baru TIDAK dibangun sekarang**: program perbaikan kinerja (KPK), talent assessment 9-box beserta talent pool, analisis kebutuhan pelatihan (TNA), dan program pengembangan beserta bootcamp dan magang. Alasannya bukan ongkos melainkan ketiadaan keputusan yang menunggu, ditambah preseden terukur bahwa modul Training dibangun lengkap lalu hampir tidak diisi.
2. **KPI bulanan wajib punya SATU sumber.** Yang diputuskan di sini baru kewajibannya, bukan sisi mana yang menang. Langkah pertama membandingkan nilai kedua sumber untuk periode yang sama (April sampai Agustus 2026, yang dimiliki keduanya), karena hari ini belum ada yang tahu apakah keduanya cocok. Arah penyatuan diputuskan pemilik proses sesudah selisihnya terlihat.
3. ⛔ **Jalur KPK menuju surat peringatan TIDAK diotomatiskan** sampai dasarnya tertulis. Peraturan Perusahaan yang berlaku memicu SP dari kehadiran, bukan dari KPI. Bila kelak diotomatiskan, ia wajib ADR sendiri dan wajib membuka `BUSINESS_LOGIC_IMPLEMENTATION.md` lebih dulu, karena ia menyentuh sanksi dan gaji.
4. **Modul Training yang sudah ada diisi lebih dulu** sebelum modul People & Development mana pun ditambahkan. Kelas, peserta, kehadiran, dan evaluasi yang hari ini hampir nol adalah bahan yang dibutuhkan talent pool dan TNA; membangun keduanya di atas data kosong menghasilkan layar yang berwibawa dan tidak menjawab apa pun.
5. **Bila talent mapping kelak dibangun, kategorinya hanya terlihat HR** (keputusan pemilik proses 2026-09-21). Atasan boleh mengisi penilaian tanpa melihat kategori akhirnya.
6. **Syarat tinjau ulang**, supaya penundaan ini tidak jadi penolakan permanen dan tidak perlu dianalisis ulang dari nol. Keputusan ini dibuka kembali begitu **salah satu** terpenuhi: (a) ada keputusan nyata yang tertunda karena datanya cuma ada di spreadsheet; (b) KPI sudah satu sumber dan modul Training sudah benar-benar terisi; atau (c) muncul kewajiban audit atau kepatuhan yang menuntut jejak talent mapping di sistem.

## Consequences

- **Spreadsheet tetap dipakai**, dan itu diterima sadar. Masalah kualitas data yang dicatat analisisnya (nama tidak seragam, departemen tidak baku, rumus rusak, sheet yang menyalin sheet lain) tetap ada sampai pemindahan benar-benar dikerjakan.
- **Satu pekerjaan nyata lahir dari keputusan ini**, yaitu menghentikan KPI ganda. Itu satu-satunya hal yang memburuk bila didiamkan, karena selisih antara dua sumber tumbuh tiap bulan dan tidak ada yang berbunyi.
- **Empat modul yang ditunda tetap terdokumentasi** lengkap dengan apa yang sudah ada dan apa yang belum, di [[REF - Peta Spreadsheet People and Development ke ERP]]. Jadi bila kelak dibangun, analisisnya tidak diulang dari nol.
- ⚠️ **Risiko yang diterima**: bila pemilik proses ternyata membutuhkan salah satu modul lebih cepat daripada yang dinyatakan hari ini, penundaan ini menambah satu putaran keputusan. Biayanya dianggap lebih kecil daripada membangun empat modul yang tidak ada yang menunggunya.
- ⚠️ **Yang belum terbukti dan jangan diklaim**: apakah nilai KPI di spreadsheet dan di ERP benar-benar berbeda. Yang terbukti hanya bahwa keduanya terisi. Perbandingannya adalah task pertama, bukan kesimpulan yang sudah dipegang.

## Deskripsi

*Dashboard ini menampilkan seluruh attrition dari departemen internal yang mencakup karyawan yang masuk dan yang keluar*

- **Status**: ⚠️ Sebagian diimplementasikan — **catatan terminasi sudah live di produksi** (koleksi `employee_resign`, sejak 2026-08-05), dan **kartu turnover bulan berjalan ✅ live** di halaman Resign serta di Dashboard HRGA (verifikasi produksi 2026-08-10). Dashboard penuh (ikhtisar, detail per departemen, demografi) masih 🟡 konsep; contohnya masih spreadsheet.

[Contoh dari sistem ini](https://docs.google.com/spreadsheets/d/113QO_RgfYz7f6NTyfFWxZjN5YQp1GxyJ/edit?gid=340825885#gid=340825885)

## Fitur

- Dashboard
	- Ikhtisar segala hal yang sangat baik untuk pelaporan kepada stakeholder
- Detail
	- Tampilan attrition secara detail yang dilihat per departemen
- Demografi
	- Informasi detail mengenai gender, tipe, dan alasan terminasi (lookup tambahan yang mudah untuk kepergian per departemen)

## Kebutuhan

- [x] Master data karyawan (referensi lookup)
- [x] **Catatan terminasi (pembuatan dan terhubung ke data karyawan)** — koleksi `employee_resign` di [[Microservices - Employee Service]]: kategori, tanggal efektif, **alasan**, dan dokumen pendukung per karyawan. ✅ **live di produksi 2026-08-05** (PR bip-erp [#1009](https://github.com/bip-itteam-internal/bip-erp/pull/1009), erp-frontend [#803](https://github.com/bip-itteam-internal/erp-frontend/pull/803)). Lihat [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]].

Yang berubah dengan adanya catatan resign adalah **prasyarat datanya terpenuhi**: lima kategori terminasi dan alasan bebas per karyawan kini tersimpan, sehingga bagian Demografi ("gender, tipe, dan alasan terminasi") punya sumber. Sebelumnya `system_authentication.is_active` cuma boolean tanpa konteks, jadi pertanyaan "berapa yang keluar karena PHK bulan ini" tak bisa dijawab dari data mana pun.

⚠️ **Datanya masih kosong.** Verifikasi produksi 2026-08-06: `employee_resign` **0 dokumen**, akun aktif **183**. Angka apa pun yang dihitung darinya akan nol sampai HR benar-benar memakai menunya.

⚠️ **Dipakai sebagian, dan itu bentuk kekosongan yang lebih menipu.** Diukur ulang PROD 2026-09-21: `employee_resign` **12 dokumen**, akun aktif **182**, akun non-aktif **35** — tetapi hanya **11** dari yang non-aktif itu punya catatan, jadi **24 kepergian tak punya tanggal sama sekali**. Angka turnover karena itu bukan nol melainkan **terlalu kecil**, dan tampak wajar. Menambal 24 itu akan mengubah turnover bulan-bulan lampau dari 11 menjadi 35 orang keluar. Penjaganya: panel "akun nonaktif tanpa catatan keluar" di halaman Resign (🔜 belum merge; [[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]]), dan sejak itu hidup tiap penonaktifan meninggalkan jejak bertanggal sehingga kekurangan ini tak bisa tumbuh diam-diam lagi.

### Kartu turnover bulan berjalan — ✅ live di produksi

Cicilan pertama Dashboard: empat kartu di halaman Resign ([[APP - Web ERP]]) yang disuplai `GET /resign/summary`, kini juga tampil sebagai `KartuAmbang` di tab **Ringkasan** dan **HRD Supervisor** Dashboard HRGA.

⚠️ **Turnover 0% tampil HIJAU "aman"** karena `statusAmbang` menilai `0 <= target` sebagai memenuhi. Selama `employee_resign` masih kosong itu mengabarkan retensi sempurna yang sebenarnya berarti "belum ada yang dicatat".

✅ **Sudah ditangani di dashboard** (erp-frontend [#951](https://github.com/bip-itteam-internal/erp-frontend/pull/951)): `KartuAmbang` mendapat prop `keterangan` yang dirender **permanen**, dan kartu turnover di tab Ringkasan maupun HRD Supervisor memakainya. Aturannya **dipinjam** dari halaman Resign yang sudah memutuskannya lebih dulu untuk angka yang sama persis, bukan dibuat yang kedua — dua layar yang menyebut angka yang sama tak boleh menerangkannya dengan cara berbeda. Sengaja bukan tooltip (praktis tak pernah terbaca) dan sengaja **tidak bersyarat status**: menampilkannya hanya saat nilainya nol membuat syaratnya hilang persis ketika angkanya mulai dipercaya orang.

Rumusnya **rata-rata headcount**, `keluar / ((awal + akhir) / 2) × 100`, dengan target **5% bulanan** yang dikirim server (bukan disalin frontend, supaya warna kartu tak pernah berbeda pendapat dengan servernya).

Tiga keterbatasan yang menempel pada angkanya, dan semuanya berasal dari bentuk datanya, bukan dari implementasinya:

- **Tak ada riwayat headcount sama sekali.** `system_authentication.is_active` cuma boolean keadaan sekarang, tanpa tanggal dan tanpa koleksi jejak. Headcount awal bulan karena itu **direkonstruksi**: `aktif sekarang + keluar bulan ini − masuk bulan ini`.
- **Rekonstruksi itu buta terhadap penonaktifan yang tak lewat menu Resign.** Sebelum menu ini ada, satu-satunya jalur adalah IT menonaktifkan akun langsung, dan itu tak meninggalkan catatan. Orangnya terhitung seolah tak pernah keluar.
- **Karena itu hanya bulan BERJALAN yang disajikan.** Bulan lampau menuntut penguraian mundur bulan demi bulan, tiap langkah menambah galat, dan hasilnya terlihat pasti padahal tidak.

⚠️ Saat dashboard penuh dibangun nanti: **tanggal keluar yang dipercaya adalah `effective_date`, bukan `applied_at`.** Keduanya bisa berbeda bila catatan dibuat mundur atau cron sempat tak jalan.

### ⛔ Ada MESIN KEDUA yang menghitung headcount, dan metodenya berbeda

T3 [[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]] (⚠️ merged ke `main` 2026-09-22 WIB, PR [#1993](https://github.com/bip-itteam-internal/bip-erp/pull/1993) merge `a6e26941`; belum deploy) menambahkan `GET /kpi/headcount-periode` yang menjawab pertanyaan yang **terdengar sama** tetapi dihitung dengan cara lain. Siapa pun yang membandingkan kedua angka perlu tahu ini lebih dulu, sebab selisihnya bukan bug.

- Rekonstruksi di halaman ini memakai **selisih**: kurangi yang keluar, tambah yang masuk, mundur dari keadaan sekarang. Itu sah untuk **perusahaan utuh** saja, dan penolakannya untuk cakupan di bawah perusahaan sudah dikunci uji — mutasi antar departemen tak tercatat sebagai keluar maupun masuk, jadi per departemen ia menghitung mutasi sebagai pengunduran diri.
- Mesin T3 merekonstruksi **per orang** lewat `employee_movement`, sehingga mutasi memindahkan orangnya antar sel tanpa mengubah total. Itulah satu-satunya cara memecah headcount per departemen dan posisi.
- **Konsekuensinya kedua angka tidak akan sama persis**, dan itu diterima sadar. Mengalihkan `/resign/summary/riwayat` ke mesin T3 adalah pekerjaan tersendiri (keputusan 2026-09-21): perubahan angka yang sudah dilihat HR di kartu turnover tidak boleh menyelinap bersama fitur baru.
- Keterbatasan kedua di atas ("buta terhadap penonaktifan yang tak lewat menu Resign") **tidak hilang** di mesin T3; ia justru diangkat jadi gerbang. Bulan lampau **menolak menjawab** selama masih ada akun non-aktif tanpa catatan keluar (24 per 2026-09-21), dan penolakan itu mencabut dirinya sendiri begitu HRD menambal. Rincian: [[Microservices - Employee Service]].

## Dokumen Terkait

- [[HRIS - Retention]] — counterpart (yang bertahan)
- [[HRIS - Personalia]] — sumber data off-boarding/terminasi
- [[Microservices - Employee Service]] · [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]] — koleksi & aturan catatan terminasi
- [[HRIS - Analysis]] · [[HRIS - Big Pictures]] · [[HRIS - Interrelationship Matrices]]

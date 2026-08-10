**Status**: ⚠️ Implemented (ada catatan). Seluruh backend + frontend **merged ke `main`** 2026-08-10: bip-erp [#1142](https://github.com/bip-itteam-internal/bip-erp/pull/1142) · [#1143](https://github.com/bip-itteam-internal/bip-erp/pull/1143) · [#1145](https://github.com/bip-itteam-internal/bip-erp/pull/1145), erp-frontend [#962](https://github.com/bip-itteam-internal/erp-frontend/pull/962). Pemetaan kategori mobile ikut merged ke `dev` (my-bharata [#110](https://github.com/bip-itteam-internal/my-bharata/pull/110)). ⚠️ **Belum diverifikasi lewat gateway hidup dan produksi belum di-deploy**; kategori inbox baru menuntut `Employee-Service` + `Notification-Service` naik **bersama**. **Approval sengaja ditunda** — lihat §Consequences.

## Context

Bharata Group menjalankan lebih dari satu badan usaha di bawah satu instans bip-erp ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]), dan karyawan nyata berpindah di antaranya. Sampai sekarang perpindahan semacam itu dikerjakan dengan menyunting `work_data` lewat form Data Pekerjaan: tanpa tanggal efektif, tanpa alasan, tanpa jejak, dan tanpa cara membedakan promosi dari mutasi. [[HRIS - Career & Promotion]] mencatat kekosongan itu sejak lama.

Yang belum pernah dibahas di dokumen mana pun adalah **perpindahan antar-tenant**. ADR 0029 membangun isolasi `company_id` dengan asumsi diam-diam bahwa seorang karyawan lahir dan pensiun di tenant yang sama. Asumsi itu tidak pernah ditulis, apalagi diuji.

Satu fakta membuat perpindahan antar-tenant berbeda dari sekadar ganti departemen: **`master_company.code` adalah prefix `employee_id`** (`shared-library/models/employee/master_company.go`). Karyawan BIP ber-ID `BIP-0221-10-25`, karyawan ELT ber-ID `ELT-...`. Jadi memindahkan orang antar-tenant memaksa satu pilihan yang tak bisa dihindari: ID ikut berubah, atau prefix berhenti berarti.

## Decision

**`employee_id` TIDAK PERNAH diterbitkan ulang saat karyawan pindah tenant.** Prefix ID berhenti menjadi penanda perusahaan dan tinggal menjadi jejak asal-mula. Satu-satunya sumber kebenaran tenant tetap `work_data.company_id`.

Alasannya sepihak: `employee_id` adalah kunci yang mengikat presensi, KPI, cuti, payroll, tiket, dokumen HRD, dan pelatihan seseorang. Menerbitkan ID baru berarti memutus seluruh riwayat itu, atau memindahkannya lewat migrasi lintas tujuh service yang tiap langkahnya bisa gagal sebagian. Riwayat yang terputus tidak bisa dipulihkan; prefix yang tak lagi berarti hanya perlu diketahui.

Aturan turunannya:

1. **Satu koleksi untuk promosi dan mutasi**, `employee_movement`, dengan pembeda `type` (`Promosi` · `Mutasi` · `Mutasi Antar-Perusahaan`). Keduanya peristiwa yang sama bentuknya — orang berpindah dari satu posisi ke posisi lain pada satu tanggal — dan memisahkannya jadi dua koleksi berarti dua salinan mesin yang sama.

2. **Jenis dipilih HR, tidak pernah disimpulkan sistem.** Verifikasi produksi 2026-08-03: nol dari 79 jabatan punya `level_key`, jadi menyimpulkan "ini promosi" dari `RankOf` berarti menyimpulkan dari data kosong. `level_key` tetap disnapshot sebagai jejak, dan tetap **bukan** sumbu hak akses ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]).

3. **Polanya meniru resign, bukan ERPGo** ([[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]]): status `scheduled`/`applied`/`cancelled` **disimpan** bukan diturunkan dari tanggal, tanggal efektif dinormalkan ke tengah malam WIB, dan cron harian idempoten menerapkan yang jatuh tempo. Cron berjalan **00:15 WIB, lima menit setelah cron resign**, supaya karyawan yang tanggal resign dan mutasinya sama sudah non-aktif lebih dulu dan tidak ikut dipindahkan.

4. **Satu perbedaan sengaja dari resign**: hanya status `scheduled` yang memblokir catatan baru. Resign juga memblokir `applied` karena orang cuma berhenti sekali; orang dimutasi berkali-kali sepanjang kariernya, dan menyalin aturan resign apa adanya akan mengunci setiap karyawan dari mutasi kedua selamanya tanpa satu pun galat.

5. **Snapshot posisi asal disimpan permanen**, tidak diturunkan dari catatan sebelumnya. Rantai turunan putus begitu ada satu perubahan yang masuk lewat form Edit Data Pekerjaan tanpa melalui modul ini, dan perubahan semacam itu pasti terjadi.

6. **`company_id` catatan = perusahaan ASAL**, sekaligus pemilik dokumen. Seluruh pembacaan di employee-service menyaring `EffectiveCompanyID`, jadi catatan yang distempel tenant tujuan akan lenyap dari layar HR yang baru saja membuatnya. Sisi tujuan membacanya lewat `to_company_id`; daftar dan riwayat karena itu dibaca dari **dua arah**. Ini satu-satunya pembacaan di service tersebut yang sengaja melintasi tenant, dan isolasinya tetap utuh karena `to_company_id` hanya bisa diisi HR perusahaan asal untuk karyawan perusahaannya sendiri.

7. **Departemen dan jabatan tujuan wajib ada di master data perusahaan TUJUAN.** `master_department.key` unik per perusahaan, bukan global; verifikasi dev terakhir menunjukkan ELT masih nol departemen, jadi tanpa penjaga ini mutasi pertama ke sana mendaratkan karyawan di departemen yang tidak ada.

8. **`work_data` ditulis lewat `$set` yang disusun sendiri**, bukan lewat `executeEmployeeUpdateTransaction` (bisa mengosongkan `company_id`, lihat [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] §Masih terbuka) maupun rute update parsial (sumber korupsi tipe BSON). Daftar field yang ditulis eksplisit dan pendek, dan `employment_type`/`contract_ending` **tak pernah** ikut — keduanya milik modul kontrak.

9. **Perpindahan didaftarkan sebagai feed kalender**, `kind` `movement` pada endpoint yang sudah ada, dengan lingkup **personal saja**: orang melihat perpindahannya sendiri, bukan supervisor, bukan HR ([[Microservices - Calendar Service]]).

## Consequences

**Konsekuensi yang diterima:**

- **Prefix `employee_id` berhenti menandakan perusahaan.** Setiap kode, laporan, atau kebiasaan kerja yang menyimpulkan tenant dari awalan ID menjadi salah begitu satu orang pindah. Belum ada audit menyeluruh atas tempat-tempat itu; yang sudah dipastikan adalah `resolveCompanyID` dan `companyIDAkun` berpangkal pada `work_data`/`external_account`, bukan pada ID.
- **Riwayat lama tetap milik perusahaan lama.** Entri presensi distempel `company_id` saat dibuat, jadi laporan bulan-bulan sebelum kepindahan tidak ikut pindah. Benar secara pembukuan, tapi berarti laporan seorang karyawan terbelah di dua tenant dan tak ada satu layar pun yang menyatukannya.
- **Perusahaan tujuan tidak punya suara.** HR perusahaan asal bisa mendorong karyawan masuk ke tenant lain sepihak, dan sejak tanggal efektif orang itu muncul di direktori, laporan, dan basis payroll perusahaan tujuan tanpa seorang pun di sana menyetujuinya. Ini konsekuensi sadar dari irisan tanpa approval, dan justru alasan terkuat mengapa approval (irisan berikutnya) wajib menyertakan pihak tujuan, bukan cuma atasan di perusahaan asal.
- **Modul yang belum ter-scope tenant tidak mengikuti perpindahan.** Payroll, recruitment, HRD-document, dan task-management tak punya `company_id` ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]), jadi perpindahan tak terlihat di sana sama sekali.
- **Atasan langsung dilepas saat departemen berubah.** `validasiAtasan` menolak atasan beda perusahaan, jadi membiarkannya menghasilkan keadaan yang validator sistem sendiri anggap tak sah. Nilai lamanya disnapshot di catatan supaya pembatalan punya jalan pulang; tanpa itu ia hilang permanen.
- **Karyawan yang perpindahannya mustahil terlaksana ditutup otomatis.** Catatan `scheduled` milik orang yang keburu non-aktif dibatalkan cron dengan alasan tercatat. Hanya untuk sebab itu; posisi yang tak cocok tetap dicoba lagi karena sebabnya bisa pulih.

**Yang dibawa serta saat pindah badan usaha (keputusan HR 2026-08-10, sementara):**

**Masa kerja (`join_date`), kuota cuti, dan nomor BPJS IKUT PINDAH apa adanya — tidak satu pun di-reset.** Modul ini karena itu tidak menyentuh ketiganya sama sekali, dan itu dikunci uji dari arah sebaliknya: `$set` yang disusunnya tak boleh pernah memuat `join_date`, `vacation`, maupun kolom BPJS.

Ditandai **sementara** oleh pemutusnya sendiri. Konsekuensi yang perlu disadari bila kelak berubah: masa kerja yang berjalan terus melintasi badan usaha berarti perhitungan pesangon memakai tanggal masuk di perusahaan LAMA, dan kuota cuti berjalan tidak dihitung ulang di entitas baru. Keduanya berpihak kepada karyawan, dan itulah sebabnya aman dipakai sementara.

**Kontrak kerja baru wajib, tapi TIDAK dibuat sistem.** Nomor kontrak, jenis, dan dokumen bertanda tangan tak satu pun bisa diturunkan dari data perpindahan, dan kontrak yang terbit dengan nilai tebakan lebih buruk daripada kontrak yang belum ada. Yang dikerjakan sistem hanya memastikan HR perusahaan tujuan diberi tahu bahwa ia harus menerbitkannya, lewat pemberitahuan yang sama yang mengabarkan kedatangan orangnya.

**Approval ditunda (2026-08-10).** Lingkupnya sudah ditetapkan untuk kelak: **hanya perpindahan antar-perusahaan** yang akan digerbang; promosi dan mutasi dalam satu perusahaan tetap langsung terjadwal. Sampai itu dibangun, satu-satunya hal yang memberi tahu perusahaan tujuan adalah notifikasi — yang karena itu bukan pelengkap melainkan penambal, dan kalimatnya sengaja menyatakan orangnya sudah masuk alih-alih meminta persetujuan yang tombolnya tak ada. Status `pending` tetap bisa disisipkan di depan `scheduled` tanpa migrasi, sebab status disimpan dan cron hanya menyapu `scheduled`.

**Tiga akibat yang ketahuan setelah modulnya jadi, dan ketiganya sudah ditutup:**

- **KPI dinilai dengan jabatan PERIODE, bukan jabatan hari ini.** `POST /kpi` membandingkan template dengan jabatan karyawan, dan patokan "jabatan terkini" pecah begitu modul ini ada: karyawan yang pindah 1 September membuat penilaian Agustus-nya mustahil diisi benar — template yang BENAR untuk Agustus ditolak 400, dan satu-satunya yang diterima justru template jabatan yang belum dipegangnya sepanjang bulan itu. Jawabannya kini diambil dari `employee_movement`, dan inilah pembenaran retroaktif untuk menyimpan snapshot jabatan asal secara permanen: tanpa snapshot itu pertanyaan "jabatan apa yang dia pegang Agustus lalu" tak punya jawaban di mana pun. Patokannya jabatan pada AKHIR periode, sebab penilaian bulanan harus punya satu jawaban.
- **Bawahan tidak ikut pindah, dan itu senyap.** Perpindahan memutus relasi atasan-bawahan DUA arah, tapi semula hanya satu yang ditangani. `bawahanAktif` menyaring `supervisor_id` PLUS `company_id`, sehingga Leader yang pindah departemen **di dalam satu perusahaan** tetap mengagregasi skor tim yang sudah bukan timnya, tanpa satu pun galat. Kedua arah kini dijawab satu aturan (`pindahDepartemen`), dan daftar bawahan disnapshot ke catatan supaya pembatalan punya jalan pulang — kelas kesalahan yang sama persis dengan `from_supervisor_id`, yang sudah pernah lolos sekali di modul ini.
- **Pengembalian bawahan hanya menyentuh yang atasannya masih kosong**, supaya membatalkan perpindahan lama tak menarik kembali orang yang sudah diberi atasan baru.

**Prasyarat perpindahan (post-test LMS) — PONDASI, belum gerbang:**

Aturan yang dituju: naik jabatan atau pindah posisi menuntut post-test LMS jabatan tujuan lebih dulu. LMS-nya belum ada ([[Microservices - Learning Service]] baru memuat pelatihan tatap muka), jadi **belum ada satu pun pemeriksa terdaftar dan tak ada perpindahan yang tertahan**. Yang dipasang cuma sambungannya (`DaftarkanPrasyarat`, meniru idiom `DaftarkanSumber` sumber KPI), plus tempat menyimpan jawabannya di catatan.

Dua sifat menjaganya tidak berubah jadi jebakan, keduanya dikunci uji: tanpa pemeriksa terdaftar **tak ada yang tertahan**, dan pemeriksa yang **gagal dihubungi tidak menahan** — kalau menahan, satu service yang mati mengunci pencatatan mutasi seluruh perusahaan padahal tanggal perpindahan sudah berjalan.

Hasilnya **disimpan** di catatan, bukan dihitung ulang saat dibaca: kelayakan dinilai saat perpindahan diputuskan, dan menghitungnya ulang setahun kemudian membuat catatan lama tampak melanggar aturan yang belum ada waktu itu. Pelewatan disiapkan sejak awal dan **wajib beralasan berikut pelakunya**, sebab gerbang tanpa jalan keluar yang tercatat akan dilewati dengan cara mematikan gerbangnya.

**Yang belum dikerjakan:**

- **Belum pernah dijalankan lewat gateway hidup.** Seluruh verifikasi masih lokal.
- **Frontend belum tahu soal pelewatan prasyarat.** `skip_prasyarat` diterima backend tapi tak ada kontrolnya di form. Tak berpengaruh selama belum ada pemeriksa terdaftar; begitu LMS tersambung, formnya wajib menyusul.
- **Prod belum di-deploy.** Kategori inbox baru menuntut `Employee-Service` dan `Notification-Service` naik **bersama** ([[Microservices - Notification Service]]); yang tak di-rebuild memegang salinan `shared-library` lama dan notifikasinya hilang tanpa jejak.
- **Riwayat seorang karyawan terbelah di dua tenant** dan tak ada satu layar pun yang menyatukannya.

## Alternatif yang ditolak

- **Menerbitkan `employee_id` baru dan memigrasikan riwayat.** Ditolak: menyentuh tujuh service, tiap langkah bisa gagal sebagian, dan kegagalan sebagian pada data riwayat tak punya jalan pulang.
- **Membuat record karyawan baru di tenant tujuan lalu menonaktifkan yang lama.** Ditolak: orang yang sama jadi dua baris di laporan headcount grup, dan turnover ikut terhitung ganda — perpindahan internal akan terbaca sebagai satu orang keluar plus satu orang masuk.
- **Menyimpan riwayat perpindahan sebagai field di `work_data`.** Ditolak dengan alasan yang sama seperti resign ([[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]]): koleksi itu sudah menyimpan dua salinan kontrak yang butuh empat penjaga agar tak menyimpang.
- **Menyimpulkan promosi dari kenaikan `rank` jenjang.** Ditolak: nol dari 79 jabatan berjenjang, dan menjadikan jenjang penentu apa pun mendekatkannya menjadi sumbu hak akses yang [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] larang.

## Terkait

- [[Microservices - Employee Service]] (koleksi, rute, cron) · [[API - Employee Service]] (daftar endpoint)
- [[HRIS - Career & Promotion]] (konsep) · [[HRIS - Organization Structure]] (jenjang & atasan langsung) · [[HRIS - Personalia]]
- [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]] · [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]] · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]] · [[ADR - 0002 Database-per-Service]]
- [[Microservices - Calendar Service]] (feed `movement`) · [[Microservices - File Service]] (lampiran SK)
- [[APP - Web ERP]] (halaman, belum dibangun)

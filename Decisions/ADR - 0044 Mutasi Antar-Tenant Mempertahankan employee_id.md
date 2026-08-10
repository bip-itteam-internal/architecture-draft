**Status**: ⚠️ Implemented (ada catatan). Irisan 1 (catat + terapkan) **merged ke `main`** 2026-08-10 lewat PR [#1142](https://github.com/bip-itteam-internal/bip-erp/pull/1142) (`a9a323dd`). ⚠️ **Belum diverifikasi lewat gateway hidup**, dan produksi belum di-deploy. Approval, kontrak baru, notifikasi, dan frontend belum dibangun.

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

**Yang belum dikerjakan:**

- **Approval** belum ada. Irisan pertama mencatat dan menerapkan, tanpa persetujuan siapa pun. Status `pending` dirancang bisa disisipkan di depan `scheduled` tanpa migrasi, sebab status disimpan dan cron hanya menyapu `scheduled`.
- **Kontrak kerja baru** belum otomatis. Pindah badan usaha berarti kontrak baru, dan modul ini sengaja tak menyentuh `employment_type`/`contract_ending`. Belum diputuskan apakah `join_date` (masa kerja), kuota cuti, dan nomor BPJS ikut pindah atau di-reset.
- **Frontend** belum ada; `deep_link` feed kalender karena itu menunjuk halaman yang belum dibangun.
- **Notifikasi** ke karyawan yang dipindahkan belum ada. Kategori inbox baru menuntut deploy dua container ([[Microservices - Notification Service]]).
- **Belum pernah dijalankan lewat gateway hidup.** Seluruh verifikasi masih lokal.

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

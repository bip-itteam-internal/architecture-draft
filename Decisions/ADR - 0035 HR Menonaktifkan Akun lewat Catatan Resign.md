**Status**: ✅ Implemented. Diputuskan dan dijalankan 2026-08-05, **live di dev dan produksi** (PR bip-erp [#1009](https://github.com/bip-itteam-internal/bip-erp/pull/1009), erp-frontend [#803](https://github.com/bip-itteam-internal/erp-frontend/pull/803)). ⚠️ **Dipakai SEBAGIAN, dan itu bentuk yang lebih menipu daripada kosong.** Verifikasi lama (2026-08-06) menunjukkan `employee_resign` **0 dokumen**; diukur ulang **2026-09-21**: **12 dokumen resign, 182 akun aktif, 35 akun non-aktif — tetapi hanya 11 dari yang non-aktif itu punya catatan**, jadi 24 kepergian tak punya tanggal sama sekali. Angka turnover karena itu bukan nol melainkan **terlalu kecil dan tampak wajar**. Penjaganya ditambahkan lewat catatan perluasan di bawah. Status ini bergerak; ukur ulang sebelum mengandalkannya.

## Context

Menonaktifkan akun karyawan selama ini **milik tim IT**, dan itu bukan kebetulan melainkan tertulis:

- `PATCH /account/active-status` di [[Microservices - Employee Service]] bergerbang `RequireITStaff`, dibungkus [[CORE - IT Orchestrator]] sebagai `POST /account/activate|deactivate`, dan dipakai dari menu **IT → Akun Karyawan** di [[APP - Web ERP]].
- [[IT - Employee System]] berstatus ✅ Implemented dan menyebut aktif/nonaktif akun sebagai kemampuan tim IT.
- [[HRIS - Analysis]] menaruh "penonaktifan akun" sebagai langkah off-boarding yang **dicek ke departemen IT**.

Persoalannya, peristiwa yang memicu penonaktifan itu peristiwa HR, bukan peristiwa IT. HR yang tahu tanggal efektifnya, kategorinya (mengundurkan diri, PHK, pensiun, kontrak berakhir, meninggal), alasannya, dan memegang surat pendukungnya. Menyalurkannya sebagai permintaan ke IT berarti akses karyawan tetap hidup sepanjang jeda antara "HR tahu" dan "IT mengeksekusi", dan jeda itu tidak punya batas yang dijanjikan siapa pun.

Persoalan kedua lebih mendasar: **sebab dan tanggal berhentinya karyawan tidak tersimpan di mana pun.** `system_authentication.is_active` cuma boolean tanpa konteks, dan `work_data` tidak punya field status kepegawaian sama sekali. [[HRIS - Attrition]] menyebut "catatan terminasi yang terhubung ke data karyawan" sebagai prasyarat yang belum ada, dan demografinya menuntut **alasan terminasi** yang hari ini tak pernah dicatat. [[HRIS - Personalia]] sudah merancang urutan off-boarding, tapi tak satu pun langkahnya punya tempat penyimpanan.

## Decision

**Pencatatan resign adalah milik HR, dan penonaktifan akun mengikutinya sebagai akibat — bukan sebagai permintaan yang dikirim ke IT.**

Aturan turunannya:

1. **Koleksi sendiri, `employee_resign`,** bukan field status di `work_data`. Koleksi itu sudah menyimpan dua salinan kontrak (`employment_type` + `contract_ending`) yang butuh empat penjaga agar tak menyimpang; salinan ketiga akan mengulang pola yang sama. `system_authentication.is_active` tetap **satu-satunya** sumber status aktif, dan dokumen resign yang menjelaskan **mengapa**.

2. **Satu tempat menulis `is_active`.** Isi handler jalur IT diekstrak jadi `terapkanStatusAkun` (`services/employee/account_status.go`) dan dipakai berdua. Jalur HR **tidak** memanggil rute IT lewat HTTP: gerbangnya akan menolak, dan rute itu membalas 400 saat status sudah sama — bagi cron resign itu no-op yang sah, bukan galat.

3. **Gerbang jalur IT tidak dilonggarkan.** `PATCH /account/active-status` tetap `RequireITStaff`. Yang bertambah adalah jalur kedua bergerbang `RequireHRISStaff`, bukan pelebaran jalur yang ada.

4. **HR tidak mendapat saklar telanjang.** Satu-satunya cara HR menonaktifkan akun adalah membuat catatan resign yang **wajib** memuat kategori, tanggal efektif, dan alasan. Tidak ada endpoint HR yang menerima `is_active` sebagai parameter.

5. **Pembatalan hanya menghidupkan akun yang dimatikan catatan itu sendiri.** Field `account_deactivated` diisi dari nilai balik `terapkanStatusAkun`. Tanpa itu, akun yang sudah dinonaktifkan IT lebih dulu tetap membuat catatan resign berstatus `applied`, dan HR yang membatalkan salah inputnya akan **menghidupkan kembali akun yang sengaja dimatikan IT** tanpa bermaksud begitu. Field kosong berarti tidak menghidupkan: gagal ke arah menahan akses, bukan memberikannya.

6. **Status catatan disimpan, bukan diturunkan dari tanggal.** Menurunkannya dari `effective_date` saja pecah di dua tempat: catatan yang dibatalkan setelah akunnya terlanjur mati tetap terbaca "sudah lewat tanggal = non-aktif", dan cron kehilangan cara membedakan "belum pernah diterapkan" dari "sudah diterapkan" sehingga tak lagi idempoten bila ada hari yang terlewat.

7. **Tanggal efektif = hari PERTAMA non-aktif,** dinormalkan ke tengah malam WIB saat disimpan. Cron harian 00:10 WIB menerapkan yang jatuh tempo; tanggal hari ini atau mundur berlaku seketika, karena HR sering baru mencatat setelah orangnya keluar.

## Consequences

**Konsekuensi yang diterima:**

- **Dua pintu ke satu saklar.** [[IT - Employee System]] tidak lagi menggambarkan keadaan sebenarnya bila dibaca sebagai "hanya IT", dan dokumen itu diperbarui bersamaan dengan ADR ini. Bahwa keduanya menulis lewat satu fungsi membuat perbedaan perilaku antar-pintu tidak mungkin muncul diam-diam.
- **Staf HR bisa menonaktifkan siapa pun di perusahaannya, termasuk direksi.** Tidak ada perlindungan berbasis jabatan. Yang membatasi hanya tenant: `POST /resign` menolak karyawan yang `work_data.company_id`-nya berbeda dari `EffectiveCompanyID` pemanggil.
- **Tanpa maker-checker.** Satu staf HR cukup untuk mematikan akses seseorang. Ini sejalan dengan jalur IT yang juga tak menuntut persetujuan kedua, dan dengan tingkat gerbang `RequireHRISStaff` yang dipilih mengikuti alur HR lain (kontrak, bank detail).
- **Jejaknya cuma sebagian.** `system_authentication` masih tanpa `updated_at`/`updated_by` dan tanpa koleksi riwayat ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]), jadi "siapa mematikan akun ini" hanya terjawab untuk jalur HR — lewat `employee_resign.metadata` — dan tetap **tak terjawab** untuk jalur IT. ⚠️ **Konsekuensi ini DIBATALKAN 2026-09-21**, lihat catatan perluasan di bawah.
- **Akses tidak putus seketika.** Penonaktifan memblokir keempat jalur login dan `GET /auth/refresh`, tapi JWT yang sudah beredar tetap sah sampai TTL 72 jam habis karena revoke masih placeholder ([[CORE - SSO Flow]]). Peringatan di form HR **tidak** menyebut jeda ini (dihapus atas permintaan user, erp-frontend PR #804), jadi HR akan menganggap aksesnya putus seketika — selisih itu perlu diingat saat menangani kasus yang menuntut pemutusan segera.

**Yang belum dikerjakan (menyusul):**

- **Karyawan non-aktif lenyap, bukan sekadar tersembunyi.** Setidaknya enam kueri di employee-service menyaring `is_active: true` diam-diam, termasuk `/list?type=employee` dan agregat direktori. Karyawan yang resign tanggal 15 karena itu hilang dari laporan absensi dan basis payroll bulan itu juga. Ini yang paling mungkin terasa lebih dulu, dan belum ditangani.
- **Exit clearance belum tersentuh.** Pengembalian aset, NDA, dan paklaring yang dirancang di [[HRIS - Personalia]] tidak masuk lingkup ini.
- **Dashboard attrition belum ada,** tapi prasyarat datanya kini terpenuhi: kategori dan alasan mulai terkumpul begitu fitur ini dipakai.
- **Revoke device tidak ikut.** Menonaktifkan akun tidak menyentuh daftar device/browser terdaftar, berbeda dari `PATCH /account/forget-device`.

**Yang belum diputuskan (TBD):**

- Apakah kategori berdampak berat (PHK, meninggal) perlu persetujuan supervisor HR, sementara pengunduran diri biasa cukup staf.
- Apakah jabatan tertentu (mis. direksi) perlu dilindungi sehingga hanya bisa dinonaktifkan admin pusat.
- Apakah pembatalan yang menghidupkan kembali akses perlu naik ke `RequireHRISSupervisor`, mengingat itu satu-satunya operasi HR yang **memberi** akses.

## Perluasan 2026-09-21 — jejak jalur IT tidak lagi kosong

> Keputusan pokok ADR ini **tidak berubah**: pencatatan resign tetap milik HR, `is_active` tetap ditulis satu fungsi, jalur IT tetap ada dan tetap `RequireITStaff`. Yang dibatalkan hanya konsekuensi "jejaknya cuma sebagian" di atas. Pemicunya [[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]]: angka headcount bulan lampau dipakai menilai kerja tim rekrutmen, dan angka itu tak bisa dipercaya selama ada penonaktifan yang tak bertanggal.

Yang diukur lebih dulu (PROD 2026-09-21): **35 akun non-aktif, hanya 11 punya catatan resign**, jadi **24 kepergian tak punya tanggal sama sekali**. Rekonstruksi headcount akhir Juni karena itu terbaca 188 sementara lembar HRD menulis 158.

Yang berubah:

1. **Tiap perubahan `is_active` meninggalkan baris `account_status_log`** berisi nilai sebelum & sesudah, alasan, sumber pintu, pelaku, dan id catatan resign bila ada. Jejaknya ditulis **di dalam** `terapkanStatusAkun`, bukan di pemanggilnya — menaruhnya di pemanggil akan mengembalikan lubang yang sama pada pintu berikutnya yang lahir.
2. **Pintunya ternyata empat, bukan dua.** Selain jalur IT dan jalur resign, pemindai sumber menemukan `DELETE /external-accounts/:employeeID` menulis `is_active` langsung (kini lewat `terapkanStatusAkun`, sumber `akun_luar`), dan review menemukan `PUT /update/:employee_id/system-auth` meneruskan map bebas ke `$set` sehingga bisa mematikan akun tanpa jejak — pintu itu kini **menolak 400** dan menunjuk `PATCH /account/active-status`. Keputusan menolak (bukan membuang diam-diam) diambil user 2026-09-21: yang bermaksud mematikan akun harus tahu maksudnya tidak terlaksana.
3. **Alasan wajib di layar IT, opsional di kontrak** selama masa transisi tiga tahap (BE menerima opsional → FE mewajibkan → BE menolak kosong), supaya layar IT lama tak patah di jeda deploy. Baris tanpa alasan tersimpan bertanda `(tidak disebutkan)`.
4. **Penjaga backlog** `GET /resign/non-aktif-tanpa-catatan` menampilkan akun mati yang belum punya catatan keluar, dipasang di halaman HRIS → Resign. Nol baris di sana adalah ambang ADR 0113.

Yang **tetap** sebagai konsekuensi yang diterima:

- Poin 4 keputusan di atas tak berubah: HR tetap tak punya saklar telanjang, dan jejak status akun **bukan** pengganti catatan resign. Jejak menjawab "kapan saklarnya ditekan"; catatan resign menjawab "orang ini berhenti, karena apa". Akun bisa mati tanpa orangnya berhenti (skorsing, akun luar), jadi baris berjejak pun tetap masuk backlog sampai HR mencatat kepergiannya.
- 24 kepergian lama tetap tak bertanggal sampai HRD menambalnya lewat menu Resign; tanggal usulannya diturunkan dari absensi terakhir dan **HRD yang memutuskan**, bukan sistem.
- ⚠️ **Masih terbuka**: `terapkanStatusAkun` menyaring `employee_id` saja tanpa `company_id`, jadi staf IT satu tenant secara teknis bisa mematikan akun tenant lain. Ini **pre-existing**, bukan lahir dari perluasan ini, dan pantas jadi keputusan tersendiri.

## Perluasan 2026-09-26 — payroll: resign sebelum periode kini dikecualikan

> Keputusan pokok ADR ini **tidak berubah**. Yang diperbarui adalah SATU dari dua gejala
> di §"Yang belum dikerjakan" di atas — *"karyawan yang resign tanggal 15 ... hilang dari
> ... basis payroll bulan itu juga"* — dan hanya **sebagian** darinya: jalur payroll,
> bukan enam kueri `is_active: true` lain yang disebut di bullet yang sama.

`computeRunLines` (payroll-service, branch `fix/payroll-exclude-resign-before-period`)
kini mengecualikan TOTAL karyawan dengan `employee_resign.status == "applied"` dan
`effective_date` (dikonversi WIB) jatuh sebelum atau tepat pada hari pertama periode run,
lewat endpoint baru employee-service `GET /internal/resign/applied`
([[API - Employee Service]] §Resign / Non-Aktif Karyawan,
[[Microservices - Payroll Service]] §Pengecualian Karyawan Resign). Ditemukan lewat data
prod nyata 2026-09-26: run "Gaji September 2026" berisi 4 dari 173 baris milik karyawan
yang sudah resign sebelum periode (26 Agustus) mulai, potensi salah bayar ±Rp 12,7 juta.

**Yang TETAP belum ditangani** (bukan diselesaikan perluasan ini):

- Enam kueri employee-service lain yang menyaring `is_active: true` diam-diam (laporan
  absensi, agregat direktori) — hanya jalur payroll yang disentuh perluasan ini.
- Resign **di tengah** periode: baris tetap dihitung PENUH, hanya komponen kehadiran
  (`payout_pct`) yang otomatis prorata seperti sebelumnya. Prorata gaji pokok/tunjangan
  tetap untuk kasus ini belum diputuskan HR/Finance — keputusan produk eksplisit yang
  diambil bersama perluasan ini, bukan celah yang terlewat.
- `employee_salary` yatim milik `BIP-2005-08-27` (identitas sudah terhapus total dari
  `employee_db`/`attendance_db` lewat `.task-plans/hapus-BIP-2005-08-27.ps1` 2026-08-19,
  tapi `payroll_db` luput) — bukan kasus resign, jadi tak tersaring perluasan ini.

Rencana lengkap, bukti data prod, dan hasil review:
`.task-plans/2026-09-26-payroll-exclude-karyawan-resign-sebelum-periode.md`.

## Terkait

- [[Microservices - Employee Service]] (koleksi, rute, cron) · [[API - Employee Service]] (daftar endpoint)
- [[HRIS - Personalia]] (konsep off-boarding) · [[HRIS - Attrition]] (konsumen data) · [[HRIS - Analysis]] (subsistem off-boarding)
- [[IT - Employee System]] · [[CORE - IT Orchestrator]] (jalur IT yang tetap ada)
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] (jejak audit yang belum ada) · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
- [[CORE - SSO Flow]] (TTL token & revoke placeholder) · [[Microservices - File Service]] (dokumen pendukung)
- [[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]] (pemicu perluasan 2026-09-21) · [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]] (kenapa kueri backlog menyaring tenant)
- [[APP - Web ERP]] (halaman HRIS → Personalia → Resign) · [[HRIS - Adaptasi ERPGo HRM]] (Tier 3 Resignations/Terminations)

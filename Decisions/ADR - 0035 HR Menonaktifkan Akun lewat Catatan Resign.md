**Status**: ✅ Implemented. Diputuskan dan dijalankan 2026-08-05, **live di dev dan produksi** (PR bip-erp [#1009](https://github.com/bip-itteam-internal/bip-erp/pull/1009), erp-frontend [#803](https://github.com/bip-itteam-internal/erp-frontend/pull/803)). ⚠️ **Sudah live tapi belum dipakai**: verifikasi produksi 2026-08-06 menunjukkan `employee_resign` **0 dokumen** dengan 183 akun aktif, jadi seluruh konsekuensi di bawah baru akan terasa setelah HR mulai mencatat.

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
- **Jejaknya cuma sebagian.** `system_authentication` masih tanpa `updated_at`/`updated_by` dan tanpa koleksi riwayat ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]), jadi "siapa mematikan akun ini" hanya terjawab untuk jalur HR — lewat `employee_resign.metadata` — dan tetap **tak terjawab** untuk jalur IT.
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

## Terkait

- [[Microservices - Employee Service]] (koleksi, rute, cron) · [[API - Employee Service]] (daftar endpoint)
- [[HRIS - Personalia]] (konsep off-boarding) · [[HRIS - Attrition]] (konsumen data) · [[HRIS - Analysis]] (subsistem off-boarding)
- [[IT - Employee System]] · [[CORE - IT Orchestrator]] (jalur IT yang tetap ada)
- [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] (jejak audit yang belum ada) · [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]
- [[CORE - SSO Flow]] (TTL token & revoke placeholder) · [[Microservices - File Service]] (dokumen pendukung)
- [[APP - Web ERP]] (halaman HRIS → Personalia → Resign) · [[HRIS - Adaptasi ERPGo HRM]] (Tier 3 Resignations/Terminations)

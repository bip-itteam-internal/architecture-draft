## Deskripsi

*Konsep **Form Builder** — pembuat form dinamis tanpa coding untuk kasus internal baru/ad-hoc. Bharata banyak memakai "form request" yang kini di-hardcode per kasus; Form Builder jadi fondasi reusable (buat form baru tanpa rilis kode). Rencana yang dulu ditunda **sudah dieksekusi**, dengan scope yang **lebih luas** dari rencana asli.*

- **Status**: ⚠️ **Backend, FE web, dan pengisian mobile semuanya merged 2026-08-01** (bip-erp #849, #855, #869–#871; erp-frontend #680, #682, #683, #691–#693; my-bharata #93–#95). Web menyediakan kelola form, builder bertab, dan **halaman analisa jawaban**; [[APP - MyBharata]] menyediakan section Survei di beranda + halaman pengisian berbagian. Deploy: **dev dan prod sama-sama jalan** (prod naik manual 2026-08-01, health `200` lewat gateway). **Yang belum: alur buat→terbit→isi→analisa belum diuji ulang** pada versi terbaru ini
- **Penempatan**: tooling platform (Tech Development), dipakai bersama HRGA
- **Implementasi**: [[Microservices - Form Builder Service]] · **FE web**: [[APP - Web ERP]] · **API**: [[API - Form Builder Service]]

## Latar Belakang

- Form yang ada hardcoded per kasus: [[HRIS - Employee Request & Approval]], [[HRIS - Leave Request]], [[HRIS - Overtime]], [[HRIS - Attendance Correction]], Form Permintaan Karyawan ([[HRIS - Recruitment]]), guestbook ([[GA - Guestbook System (Complete)]]). [[GA - Checklist Management]] mendekati tapi bukan form umum.
- Cocok untuk survei internal, deklarasi, pendataan mendadak, pendaftaran event — **tanpa** mengganggu form approval bisnis yang sudah matang.

## Perubahan Scope dari Rencana Asli

Rencana yang terkunci di dokumen ini sebelumnya (RBAC `it` saja, tanpa FE, tanpa analitik, tanpa mobile, dan menjanjikan "nol dampak ke service berjalan") **sudah tidak berlaku**. Yang dieksekusi:

| Aspek | Rencana asli | Yang dibangun |
|---|---|---|
| RBAC | `system_roles["it"]` saja | **per departemen** (PR #869): tingkat peran pengelola + departemen ada di daftar aktif. Sekarang HRGA (Human Resource + General Affair) dan IT (Tech Development); departemen berikutnya cukup ubah env. ⚠️ Katalog permission-set merged & live dev+prod 2026-08-10 (PR #1138), paket belum dipasang ke jabatan — lihat §Menuju hak per jabatan |
| Hasil jawaban | export CSV saja | analisa per pertanyaan + tren harian + tingkat pengisian, **plus** CSV |
| Sasaran form | (tak ada) | semua / per departemen / per karyawan |
| Dampak ke service lain | "nol dampak" | **menyentuh [[Microservices - Attendance Service]]**: clock-in mobile bisa ditahan bila ada form wajib belum diisi |
| Multi-perusahaan | (tak dibahas) | `company_id` sejak awal ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]) |

Yang **tetap** ditunda sesuai rencana asli: **upload file** dan **logika percabangan** (lompat seksi berdasarkan jawaban).

## Menuju hak per jabatan

> **Status**: ⚠️ **Merged & live di dev DAN prod, 2026-08-10** (PR [#1138](https://github.com/bip-itteam-internal/bip-erp/pull/1138)), keduanya terverifikasi. Tapi **belum ada satu jabatan pun yang dipasangi paketnya**, jadi bagi semua orang akses hari ini masih sama persis seperti sebelumnya. Manfaatnya baru terasa setelah HR memasang paket ke jabatan — itu keputusan organisasi, bukan langkah rilis.

Perpindahan ke sumbu departemen (PR #869) menjawab "form ini milik tim siapa", tapi belum menjawab "siapa di tim itu yang boleh membangunnya". Akibatnya hari ini **siapa pun yang bekerja di ketiga departemen aktif dan punya peran apa pun di modul mana pun** sudah bisa membuat dan menerbitkan form — staf dengan peran tiket sekalipun.

Katalog `formbuilder` ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]) memindahkan pertanyaan kedua itu ke jabatan, sehingga populasinya jadi eksplisit dan bisa dicabut lewat layar Hak per Posisi alih-alih lewat env yang menuntut container dibuat ulang. Tiga paket: **Lihat**, **Pengelola**, dan **Penata Aturan**.

Dua hal yang perlu diketahui pemilik produk:

- **Fase satu tidak mengubah akses siapa pun.** Yang berubah baru muncul setelah paket benar-benar dipasang ke jabatan, dan itu keputusan HR, bukan keputusan rilis.
- **Pembatasan per-departemen lewat paket belum mungkin.** Cakupan departemen tetap ditentukan tempat orang bekerja, bukan oleh paketnya. Menyetel sebuah paket ke "divisi sendiri" tidak akan membatasi apa pun sampai penegaknya dibangun.

Detail teknis + alasan keputusan itu: [[Microservices - Form Builder Service]] §Izin.

## Intersep Presensi

Kebutuhan yang memicu perluasan scope: HRGA ingin memastikan form tertentu (mis. deklarasi kesehatan) benar-benar diisi sebelum karyawan mulai bekerja. Keputusan yang diambil:

- **Per form** bisa diatur `block` (tahan clock-in) atau `warn` (hanya ingatkan). Default `warn`.
- **Hanya jalur mobile** yang ditahan. Mesin fingerprint tak punya layar untuk mengisi form dan tak membawa identitas JWT, jadi menahan di sana hanya menghasilkan karyawan yang tertahan tanpa cara menyelesaikannya. Clock-**out** juga tak ditahan — menahan orang pulang bukan tujuan fitur ini.
- **Gagal-terbuka.** Form Builder yang mati, lambat, atau membalas rusak **tidak** boleh berubah jadi pemadaman presensi; clock-in diteruskan.
- **Jendela tanggal wajib**, supaya gerbang yang dilupakan tidak menahan presensi selamanya.

Rinciannya di [[Microservices - Form Builder Service]] dan [[Microservices - Attendance Service]].

## Urutan Rilis yang Mengikat

**Mode `block` sebaiknya belum dinyalakan di produksi sampai MyBharata siap.** Keputusan menaruh pengisian sepenuhnya di mobile berarti karyawan yang tertahan gerbang belum punya jalan mengisi lewat web. Mode `warn` aman dipakai lebih dulu. FE web sudah memasang peringatan ini di layar pengaturan gerbang, tapi itu peringatan, bukan pencegah.

Deploy tetap **backend lebih dulu, FE menyusul**.

## Keputusan: Identitas Responden Ditampilkan Penuh

Halaman analisa menampilkan **nama, departemen, dan jabatan** tiap pengisi beserta seluruh jawabannya (tab Pertanyaan & Individu), meniru Google Form.

Ini **keputusan sadar pemilik produk 2026-08-01**, diambil setelah konsekuensinya disampaikan: pengelola form bisa melihat siapa menjawab apa. Untuk form seperti Deklarasi Kesehatan, itu berarti kondisi kesehatan per orang terbaca pengelolanya.

Dicatat di sini supaya keputusannya terekam dan bisa ditinjau ulang, bukan tersembunyi sebagai perilaku kode. Alternatif yang ditolak: hanya agregat, atau daftar tanpa identitas.

> **Diperkecil oleh PR #869.** Saat keputusan ini diambil, "pengelola form" berarti siapa pun berperan `it` **atau** `ga`, sehingga jawaban Deklarasi Kesehatan milik HRGA ikut terbaca tim IT. Setelah kepemilikan pindah ke departemen, analisa sebuah form hanya terbaca departemen pemiliknya (plus atasannya lewat `supervised_by`). Keputusan menampilkan identitas penuh **tidak berubah**; yang menyempit adalah lingkaran orang yang bisa membacanya.

## Belum Diputuskan (TBD)

- Renderer pengisian di [[APP - MyBharata]] — belum dikerjakan sama sekali, dan inilah yang menahan mode `block` boleh dinyalakan.
- Deploy **prod**: form-builder-service belum pernah dibuat di sana (lihat [[Microservices - Form Builder Service]]).
- Pencarian karyawan untuk sasaran per-orang (sementara diketik sebagai Employee ID per baris).
- Form berulang: gerbang presensi menganggap "sudah pernah mengisi" selamanya, jadi belum ada bentuk deklarasi **harian**. Form contoh di dev diberi nama per bulan sebagai siasat.
- Apakah form publik (tanpa login) akan didukung — belum dikerjakan.
- Apakah RBAC akan dinaikkan ke permission-set [[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]]. **Terjawab sebagian**: izin *tipe form* ditempelkan di **departemen**, bukan posisi, lewat [[ADR - 0041 Izin Tipe Form Menempel di Departemen]] — pertanyaan yang dijawabnya "departemen ini menjalankan proses apa", dan semua orang di satu departemen menjawabnya sama. Yang masih terbuka hak *mengelola form* itu sendiri (`requireFormManager`), yang sampai kini masih tingkat peran + departemen aktif.

## Dokumen Terkait

- [[Microservices - Form Builder Service]] · [[API - Form Builder Service]]
- [[HRIS - Employee Request & Approval]] · [[GA - Checklist Management]] · [[GA - Guestbook System (Complete)]]
- [[Microservices - Attendance Service]] · [[Microservices - File Service]] · [[CORE - SSO Flow]] · [[CORE - API Master Gateway]] · [[DB - Overview and Notes]] · [[ROADMAP]]

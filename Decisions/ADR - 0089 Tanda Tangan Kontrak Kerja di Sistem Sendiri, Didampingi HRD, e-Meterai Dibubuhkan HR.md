# ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR

## Untuk Manajemen

- **Yang berubah di layar**: HR menyiapkan kontrak PKWT dari data karyawan yang sudah ada. Karyawan baru maupun yang diperpanjang datang ke kantor, membaca kontraknya bersama HRD di perangkat HR, lalu menggores tanda tangan di layar. Direktur menandatangani banyak kontrak sekaligus dari Ruang Direktur. Salinan final dikirim ke email karyawan baru dan bisa dibuka karyawan aktif di MyBharata. HR dan atasan menerima pengingat sebelum kontrak berakhir.
- **Siapa terdampak**: HR Personalia dan HRD pendamping, seluruh karyawan berkontrak PKWT (tetap datang ke kantor untuk menandatangani), direktur (beserta Sekretariat yang memakai akun yang sama), dan atasan yang wajib menilai kinerja sebelum kontrak berakhir.
- **Tidak dijanjikan**: tanda tangan dari jarak jauh. Tanda tangan tersertifikasi (tanpa PSrE dan e-KYC; kekuatan buktinya setara tanda tangan kertas yang disaksikan HRD, lebih lemah daripada yang tersertifikasi). Sistem tidak membeli atau membubuhkan e-Meterai; itu pekerjaan HR di portal distributor resmi. Sistem tidak bisa membuktikan bahwa direktur pribadi yang menekan tanda tangan, karena akunnya dipakai bersama. Keabsahan untuk PKWT masih menunggu konfirmasi legal. Kontrak lama tidak ditandatangani ulang.
- **Besaran kerja**: pengingat kontrak habis beberapa hari dan bisa dirilis lebih dulu. Tanda tangan lengkap sekitar 4 sampai 6 minggu kerja satu developer secara bertahap, didahului satu uji PDF bermeterai asli.

## Deskripsi

*Kontrak kerja PKWT ditandatangani di sistem sendiri dengan tanda tangan elektronik **tidak tersertifikasi**, **tatap muka di kantor dan didampingi HRD**: karyawan menggores tanda tangan di perangkat HR setelah HRD mencocokkan KTP-nya, lalu direktur mengonfirmasi dari Ruang Direktur. e-Meterai dibubuhkan HR di luar sistem. Kebutuhan kedua, kontrak habis yang tak terpantau, dijawab terpisah dengan pengingat. Menggantikan [[ADR - 0019 Kontrak Kerja Elektronik via Service Internal + Lapisan Tersertifikasi]], yang memilih jalur tersertifikasi lewat PSrE dan tak pernah diratifikasi. Cara kerja domainnya di [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]].*

- **Status**: 🟡 **Diusulkan**, disetujui pemilik proses 2026-09-11 lewat `/analisa-kebutuhan` dan **direvisi hari yang sama**: tanda tangan PIN jarak jauh di MyBharata diganti tanda tangan tatap muka didampingi HRD (§4, §6, §7). Kode tanda tangan belum ada. ✅ **§2 (pengingat): merged 2026-09-11 (bip-erp PR #1851), naik di DEV 2026-09-11 dan PROD 2026-09-12**; jalan PROD pertama 2026-09-13 07:00 WIB belum dibaca. Keabsahan hukum menunggu konfirmasi legal.
- **Path di repo**: `bip-erp/services/employee/contract*.go` · `bip-erp/services/employee/contract_tanda_tangan*.go` (baru) · `bip-erp/services/employee/contract_pengingat.go` · `bip-erp/services/employee/cron.go` · `bip-erp/services/employee/warning_notify.go` · `bip-erp/shared-library/models/employee/models.go` · `bip-erp/shared-library/models/employee/contract_pengingat.go` · `bip-erp/services/file/main.go` · `erp-frontend/src/features/hris/contract/` · `erp-frontend/src/features/direktur/` · `mybharata-app/lib/src/features/contract/` (baru, baca-saja)
- **Tanggal**: 2026-09-11

## Context

**Permintaannya solusi, kebutuhannya dua.** Manajemen meminta tanda tangan digital dan meterai digital untuk kontrak PKWT. Wawancara 2026-09-11 menemukan dua masalah di baliknya: (1) kertas dan biaya cetak, karena PKWT sering diperpanjang; (2) kontrak habis tak terpantau. Tanda tangan digital hanya menjawab yang pertama. Yang kedua butuh pengingat, dan datanya sudah ada: status `ending` (berakhir dalam 2 bulan) dihitung di daftar dan ringkasan kontrak, tetapi tidak ada yang mengirim pengingat. Git grep `origin/main` 2026-09-11 di employee-service dan notification-service tidak menemukan notifikasi kontrak apa pun.

**Cara menandatangani yang berlaku di perusahaan** (pemilik proses, 2026-09-11): karyawan baru **dan** perpanjangan menandatangani kontrak **di kantor, didampingi HRD**, dan kontrak karyawan baru dikirim lewat email. Identitas penanda tangan karena itu ditetapkan HRD yang hadir, bukan oleh akun aplikasi.

**Yang sudah ada adalah kenyataan; alur tanda tangan masih rencana.** Modul riwayat kontrak live di employee-service: koleksi `employee_contract` sebagai pemilik ([[REF - Kepemilikan Data]]), nomor otomatis, lampiran PDF, status dihitung saat baca, feed kalender `contract_end`, dan cron. Rutenya di [[API - Employee Service]] §Kontrak Kerja. Alur tanda tangan di dok domain berstatus 🟡: ADR ini berdiri di atas pondasi yang live dan desain yang belum ada kodenya.

**Kenapa bukan jalur tersertifikasi.** ADR 0019 memilih TTE tersertifikasi via PSrE, e-KYC karyawan, e-Meterai lewat API, dan service baru. Pemilik proses menolak ketergantungan vendor, biaya per transaksi, dan friksi e-KYC, lalu memilih tanda tangan tidak tersertifikasi. Dasar hukumnya (sumber sekunder, belum dikonfirmasi legal): UU ITE Pasal 11 ayat (1) dan PP 71/2019 Pasal 59 ayat (3) mengakui tanda tangan elektronik tidak tersertifikasi sepanjang memenuhi enam syarat: data pembuatannya hanya terkait dengan dan berada dalam kuasa penanda tangan, perubahan tanda tangan maupun dokumen setelah penandatanganan dapat diketahui, ada cara andal mengidentifikasi penanda tangan, dan ada mekanisme yang menunjukkan persetujuan. Bedanya di pembuktian: bila disangkal, perusahaan membuktikan lewat jejak sistemnya sendiri.

**Lubang keamanan akun yang ditemukan grounding** (dicek langsung ke `origin/main` 2026-09-11):

1. PIN bisa dicoba tanpa batas: grup `/auth` gateway tanpa limiter (`api-gateway/main.go:271`), `/login/pin` tanpa JWT (`:328`), dan `verify-pin` mencari akun dari body, bukan dari token (`services/employee/main.go:3101-3108`).
2. Reset akun oleh IT menyetel password sementara = `employee_id` dan mengosongkan PIN (`main.go:6579-6591`), tanpa jejak.
3. `device_id` Android = `androidInfo.id` (Build.ID), tidak unik per perangkat (`mybharata-app/lib/src/core/utils/device_info_helper.dart:32`).
4. Biometrik hanya diverifikasi di perangkat; `/auth/login-biometrics` menerima JWT lama tanpa bukti kunci apa pun.
5. Hasil verifikasi PIN tidak terikat ke tindakan berikutnya, dan gerbang PIN MyBharata berlaku per sesi ([[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] §1).
6. Akun direktur dipakai bersama Sekretariat dan dikecualikan dari pengikatan perangkat (`main.go:2773-2780`). `common.SetaraDirektur` juga meloloskan Corporate Secretary (`shared-library/common/jabatan_direktur.go:24-27`).
7. Kunci baca prefix MinIO `employee/`, tempat lampiran kontrak disimpan, tertanam di bundel browser (`erp-frontend/src/hooks/use-document.ts:5-7`; [[Microservices - File Service]]).
8. Akun karyawan baru lahir dengan password awal = `employee_id` kecuali HR mengisi password khusus (`orchestrator/hris/helper.go:471-485`), sementara akun pihak luar sudah memakai password acak 16 karakter (`services/employee/external_account_password.go`).

Karena tanda tangan tidak memakai akun maupun PIN karyawan (§6, §7), lubang 1-5 dan 8 **tidak menahan fitur ini**, tetapi tetap lubang keamanan akun yang dicatat sebagai task terpisah. Lubang 6 dan 7 tetap relevan dan dijawab §8 dan §9.

**Data nyata.** Volume kontrak per bulan dan kontrak kedaluwarsa pada karyawan aktif tidak bisa dibaca dari prod (ditolak classifier dua kali). Skrip baca-saja disiapkan di `.task-plans/cek-kontrak-esign-prod.ps1`. Di DEV 2026-09-11, 110 dari 172 karyawan aktif punya kontrak terakhir yang sudah lewat, seluruhnya hasil migrasi (dok domain §Pengingat Kontrak Habis). Skrip itu dijalankan 2026-09-12: PROD punya 408 kontrak, belum satu pun berlampiran, 4 sampai 30 kontrak mulai per bulan, dan 0 kontrak kedaluwarsa pada 186 karyawan aktif.

**Aturan bisnis.** Peraturan Perusahaan (`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`) tidak mengatur PKWT, penandatanganan, maupun meterai. Yang bersinggungan hanya komponen gaji di Lampiran 1 (tunjangan kehadiran, uang makan), yang nilainya diambil dari payroll, tidak dihitung ulang.

## Decision

### 1. Tanda tangan elektronik tidak tersertifikasi, dibangun sendiri

Tanpa PSrE, tanpa e-KYC, tanpa vendor. Menggantikan ADR 0019 seluruhnya.

### 2. Pengingat kontrak habis dikerjakan lebih dulu dan terpisah

Kebutuhan kedua tidak menunggu tanda tangan. Cron employee-service mengirim inbox kategori `reminder` (sudah terdaftar dan terpetakan di MyBharata maupun Web ERP): satu ringkasan harian per supervisor HR per perusahaan saat kontrak masuk status "segera berakhir", H-30, H-7, dan untuk kontrak kedaluwarsa pada karyawan aktif sekali per minggu; ke atasan langsung H-14 kalender untuk penilaian kinerja (Pasal 2 ayat 6 template PKWT). Status "segera berakhir" memakai satu fungsi klasifikasi yang sama dengan daftar, ringkasan, dan riwayat kontrak. Rencananya di `.task-plans/2026-09-11-pengingat-kontrak-habis.md`.

**Implementasi (bip-erp PR #1851, merged 2026-09-11; live DEV 2026-09-11 dan PROD 2026-09-12)**: yang dipantau kontrak terakhir tiap karyawan aktif di perusahaannya sekarang; jejak kiriman disimpan di koleksi sendiri `employee_contract_pengingat`, dan hanya kiriman yang berhasil yang dicatat; karyawan tanpa atasan tercatat ditandai ke HR; pesan tanpa tautan ke halaman Kontrak. Penyatuan aturan status menghitung dalam tanggal WIB, sehingga hari terakhir kontrak berstatus `ending` di daftar, ringkasan, dan riwayat. Rinciannya di dok domain §Pengingat Kontrak Habis.

### 3. Menempel di modul kontrak employee-service, bukan service baru

Status tanda tangan disimpan pada `employee_contract`. Catatan tiap tindakan tanda tangan disimpan di koleksi baru yang **hanya bisa ditambah dan tanpa TTL**; pola jejak yang sudah ada ber-TTL 365 hari, jadi tidak bisa dipakai. Logikanya ditaruh di berkas dan koleksi sendiri supaya bisa diangkat ke service tersendiri bila kelak ada pemakai ketiga (offer letter, SP, NDA).

Service penandatanganan generik ditolak sekarang karena belum ada pemakai kedua, dan karena pertanyaan "kontrak ini sudah ditandatangani?" akan hidup di dua database. Acknowledgment HRD Documents ditolak karena isinya Markdown, tanpa konfirmasi identitas, dan milik service lain.

### 4. Alur tatap muka didampingi HRD

Berlaku untuk kontrak pertama maupun perpanjangan.

1. HR membuat kontrak; sistem mengisi template PKWT menjadi PDF draft. Draf **tidak** dikirim ke email karyawan lebih dulu (keputusan pemilik proses 2026-09-12); karyawan membacanya saat bertemu HRD. Selama masa transisi, sebelum alur ini dibangun, HR boleh mengirim dokumen isian otomatis secara opsional untuk menemukan data dan isi template yang masih kurang (dok domain §Masa transisi).
2. Karyawan datang ke kantor. HRD membuka sesi tanda tangan untuk kontrak itu di perangkat HR (dengan akun HRD sendiri) dan mengetik NIK dari KTP fisik; sistem mencocokkannya dengan `personal_data.nik_number`, dan yang tidak cocok ditolak.
3. Karyawan membaca kontrak di layar, menggores tanda tangan, dan menyatakan setuju. Karyawan yang minta koreksi mengembalikan kontrak ke HR.
4. Direktur menandatangani dari antrean Ruang Direktur, satu atau banyak sekaligus.
5. HR membubuhkan e-Meterai di portal distributor resmi Peruri dan mengunggah hasilnya; sistem mengunci PDF dan menyimpan hash SHA-256-nya.
6. Sistem menerbitkan lembar bukti tanda tangan dan mengirim salinan final (§10).

**Usulan turunan untuk calon karyawan (2026-09-11, belum diputuskan)**: kontrak pertama ditandatangani **sesudah** HR membuat data karyawannya lewat Tambah Karyawan dari kandidat. Record kontrak (§11), pencocokan NIK (§6), dan salinan email (§10) semuanya bertumpu pada data karyawan, sedangkan data kandidat tidak punya NIK. Hal yang belum diputuskan (calon batal atau menolak, rincian gaji dari offer, kontrak yang belum ditandatangani terhadap pengingat) di dok domain §Calon karyawan dan karyawan aktif.

**Urutan meterai dan letak goresan menunggu satu uji (S1).** HR memeteraikan satu PDF contoh lewat portal distributor yang dipakai.
- Bila isi PDF asli tetap utuh byte per byte di dalam berkas bermeterai dan e-Meterai-nya masih lolos verifikasi: **urutan A**. Tanda tangan lebih dulu, goresan tercetak di kotak tanda tangan PDF, meterai paling akhir (langkah 5 di atas), dan saat unggah sistem memeriksa bahwa PDF bermeterai memuat PDF yang ditandatangani tanpa perubahan. Meterai tidak terbuang untuk kontrak yang batal.
- Bila tidak: **urutan B**. HR membubuhkan meterai sebelum sesi tanda tangan, PDF bermeterai dikunci dan tidak diubah lagi, kotak tanda tangan bertuliskan "ditandatangani secara elektronik", dan goresan tampil di lembar bukti terpisah.

Tanda tangan diikat ke hash dokumen yang ditandatangani: urutan A ke hash PDF sebelum meterai, urutan B ke hash PDF bermeterai.

### 5. e-Meterai urusan HR

Sistem tidak berintegrasi dengan API meterai dan tidak memverifikasi keaslian meterai. HR bertanggung jawab membelinya (akun enterprise di distributor resmi) dan membubuhkannya.

### 6. Bukti tanda tangan karyawan = kehadiran yang disaksikan HRD

Identitas ditetapkan oleh HRD yang hadir dan tercatat lewat pencocokan NIK; persetujuan dari goresan tanda tangan dan pernyataan setuju. Catatan tanda tangan merekam `employee_id` penanda tangan, hasil pencocokan NIK (tanpa menyimpan NIK yang diketik), HRD pendamping (identitas dari header gateway), waktu server, perangkat, dan hash dokumen. Akun dan PIN karyawan **tidak** dipakai. Kekuatan buktinya setara tanda tangan kertas yang disaksikan HRD.

### 7. Tidak ada tanda tangan jarak jauh

Keputusan pemilik proses 2026-09-11. Karena itu lubang keamanan PIN dan akun karyawan (Context 1-5 dan 8) tidak menahan fitur ini; perbaikannya menjadi task keamanan akun terpisah. Yang tetap berlaku: sesi tanda tangan hanya bisa dibuka pemegang izin kerja HRIS, dan satu sesi terikat ke satu kontrak dan satu karyawan.

### 8. Pihak Pertama = direktur yang ditetapkan per perusahaan

Penandatangan perusahaan diambil dari data penandatangan per perusahaan (baru), **bukan** dari `common.SetaraDirektur`, yang ikut meloloskan Corporate Secretary. Akun direktur yang dipakai bersama Sekretariat **diterima apa adanya** (keputusan pemilik proses 2026-09-11). Konfirmasinya eksplisit di Ruang Direktur tanpa PIN, karena PIN akun bersama tidak menambah bukti siapa orangnya. Lembar bukti mencatat tanda tangan "atas nama Direktur" beserta akun yang dipakai, dan tidak mengklaim lebih dari itu.

### 9. Arsip di prefix tersendiri, terkunci

PDF final, gambar goresan, dan lembar bukti disimpan di prefix MinIO baru **tanpa kunci baca di browser** (pola `audit/`), dibaca lewat proxy employee-service. Setelah terkunci, lampiran tidak bisa diganti atau dihapus lewat jalur mana pun. Yang boleh membuka: staf HR berizin HRIS, karyawan yang bersangkutan, dan direktur. Atasan tidak, karena kontrak memuat gaji.

### 10. Salinan untuk karyawan

Karyawan baru menerima PDF final dan lembar bukti lewat email (notification-service `POST /email/send`, lampiran PDF) ke `personal_data.email_address`. Karyawan aktif membukanya di "Kontrak Saya" MyBharata, baca-saja dan di balik gerbang PIN seperti slip gaji karena memuat gaji.

### 11. Kepemilikan tidak berubah

`employee_contract` tetap pemilik fakta kontrak. Salinan `work_data.employment_type` dan `contract_ending` tetap hanya ditulis modul kontrak.

## Consequences

- ➕ Tanpa biaya per tanda tangan dan tanpa vendor; bisa dimulai sekarang di atas pondasi yang live.
- ➕ Kontrak habis yang tak terpantau terjawab lebih dulu, terlepas dari tanda tangan.
- ➕ Tidak bergantung pada keamanan akun dan PIN karyawan: bukti bertumpu pada kehadiran dan HRD, sama seperti proses kertas hari ini, dan MyBharata tidak wajib aktif untuk menandatangani.
- ➕ Satu pemilik data kontrak; tidak ada service maupun modul gateway baru.
- ➖ Karyawan tetap harus datang ke kantor; tidak ada perpanjangan jarak jauh.
- ➖ Waktu HRD per penandatanganan, dan langkah manual HR untuk e-Meterai (bisa dikerjakan per kelompok).
- ➖ Bukti hukum lebih lemah daripada yang tersertifikasi; relevan untuk klausul denda di Pasal 4 template.
- ➖ Tanda tangan Pihak Pertama tidak bisa dibuktikan berasal dari direktur pribadi karena akunnya dipakai bersama. **Risiko diterima sadar.**
- ➖ employee-service, yang sudah paling besar, bertambah lagi.
- ⚠️ **Konfirmasi legal belum ada.** Rilis tanda tangan menunggu konfirmasi itu; pengingat tidak.
- ⚠️ **Uji PDF bermeterai (S1) menentukan urutan A atau B.** Sebelum itu template dan alur backend tidak bisa difinalkan.
- ⚠️ **Lubang keamanan akun (Context 1-5, 8) tetap ada di sistem** walau tidak lagi menahan fitur ini. "Kontrak Saya" di MyBharata memuat gaji, jadi temuan sampingan grounding mobile yang **belum diverifikasi** (tap notifikasi bisa melewati gerbang PIN karena kunci `user_pin` tak pernah ditulis) wajib dicek sebelum layar itu dirilis.
- ✅ **Data kontrak migrasi yang tak pernah diperbarui hanya ada di DEV** (2026-09-11: 110 dari 172 karyawan aktif kedaluwarsa, semuanya migrasi) dan membuat bagian kedaluwarsa di ringkasan pengingat DEV membengkak. PROD diukur 2026-09-12: 0 dari 186, karena HR sudah mencatat kontraknya, jadi pengingat naik ke PROD tanpa merapikan data maupun mengubah aturan. Akibatnya bagi pengujian: tampilan DEV bukan gambaran PROD.
- 🔗 **Deploy**: pengingat cukup employee-service. Prefix MinIO baru berarti file-service `up -d --build` bila biner belum memuatnya, kunci unik di `.env` dev dan prod, dan employee-service `--force-recreate`; bukti lewat hitungan prefix di log boot. Kategori inbox baru untuk alur tanda tangan (bila ada) berarti notification-service naik lebih dulu, lalu employee-service, keduanya di-rebuild (`shared-library/models/notification/models.go:269-273`). "Kontrak Saya" berarti satu rilis MyBharata (version name dan code naik bersama). Perubahan kontrak API berarti backend sebelum Web ERP dan MyBharata. Deploy prod dijalankan manusia.

## Dokumen Terkait

- [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] (cara kerja) · [[HRIS - Personalia]] · [[HRIS - Recruitment]] (hire calon karyawan)
- [[ADR - 0019 Kontrak Kerja Elektronik via Service Internal + Lapisan Tersertifikasi]] (digantikan)
- [[REF - Kepemilikan Data]] · [[API - Employee Service]] · [[Microservices - Employee Service]] · [[Microservices - File Service]] · [[Microservices - Notification Service]] · [[IT - Background Jobs & Schedulers]]
- [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] (gerbang PIN per sesi) · [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]] · [[ADR - 0002 Database-per-Service]]
- Daftar task: `Workspace/ANALISA - Tanda Tangan Kontrak Kerja dan Pengingat Kontrak Habis.md`

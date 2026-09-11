# ADR - 0089 Tanda Tangan Kontrak Kerja dengan PIN di Sistem Sendiri, e-Meterai Dibubuhkan HR

## Untuk Manajemen

- **Yang berubah di layar**: HR menyiapkan kontrak PKWT dari data karyawan yang sudah ada lalu mengirimkannya. Karyawan membaca, menyetujui isi, dan menandatangani di MyBharata dengan PIN, lalu bisa membuka salinannya kapan saja. Direktur menandatangani banyak kontrak sekaligus dari Ruang Direktur. HR dan atasan menerima pengingat sebelum kontrak berakhir.
- **Siapa terdampak**: HR Personalia, seluruh karyawan berkontrak PKWT, direktur (beserta Sekretariat yang memakai akun yang sama), dan atasan yang wajib menilai kinerja sebelum kontrak berakhir.
- **Tidak dijanjikan**: tanda tangan tersertifikasi (tanpa PSrE dan tanpa verifikasi identitas e-KYC, jadi bukti hukumnya lebih lemah daripada yang tersertifikasi). Sistem tidak membeli atau membubuhkan e-Meterai; itu pekerjaan HR di portal distributor resmi. Sistem tidak bisa membuktikan bahwa direktur pribadi yang menekan tanda tangan, karena akunnya dipakai bersama. Keabsahan untuk PKWT masih menunggu konfirmasi legal. Kontrak lama tidak ditandatangani ulang.
- **Besaran kerja**: pengingat kontrak habis beberapa hari dan bisa dirilis lebih dulu. Tanda tangan lengkap sekitar 5 sampai 8 minggu kerja satu developer secara bertahap, termasuk satu rilis MyBharata di store.

## Deskripsi

*Kontrak kerja PKWT ditandatangani di sistem sendiri dengan tanda tangan elektronik **tidak tersertifikasi**: karyawan dan direktur mengonfirmasi dengan PIN yang diverifikasi server, terikat ke sidik jari (hash) PDF yang sudah dibubuhi e-Meterai oleh HR di luar sistem. Kebutuhan kedua, kontrak habis yang tak terpantau, dijawab terpisah dengan pengingat. Menggantikan [[ADR - 0019 Kontrak Kerja Elektronik via Service Internal + Lapisan Tersertifikasi]], yang memilih jalur tersertifikasi lewat PSrE dan tak pernah diratifikasi. Cara kerja domainnya di [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]].*

- **Status**: 🟡 **Diusulkan**, disetujui pemilik proses 2026-09-11 lewat `/analisa-kebutuhan`, kode belum ada. Keabsahan hukum menunggu konfirmasi legal.
- **Path di repo**: `bip-erp/services/employee/contract*.go` · `bip-erp/services/employee/contract_tanda_tangan*.go` (baru) · `bip-erp/services/employee/contract_pengingat.go` (baru) · `bip-erp/services/employee/cron.go` · `bip-erp/shared-library/models/employee/models.go` · `bip-erp/shared-library/models/notification/models.go` · `bip-erp/services/file/main.go` · `bip-erp/api-gateway/main.go` · `erp-frontend/src/features/hris/contract/` · `erp-frontend/src/features/direktur/` · `mybharata-app/lib/src/features/contract/` (baru) · `mybharata-app/lib/src/core/utils/device_info_helper.dart`
- **Tanggal**: 2026-09-11

## Context

**Permintaannya solusi, kebutuhannya dua.** Manajemen meminta tanda tangan digital dan meterai digital untuk kontrak PKWT. Wawancara 2026-09-11 menemukan dua masalah di baliknya: (1) kertas dan biaya cetak, karena PKWT sering diperpanjang; (2) kontrak habis tak terpantau. Tanda tangan digital hanya menjawab yang pertama. Yang kedua butuh pengingat, dan datanya sudah ada: status `ending` (berakhir dalam 2 bulan) dihitung di daftar dan ringkasan kontrak, tetapi tidak ada yang mengirim pengingat. Git grep `origin/main` 2026-09-11 di employee-service dan notification-service tidak menemukan notifikasi kontrak apa pun.

**Yang sudah ada adalah kenyataan; alur tanda tangan masih rencana.** Modul riwayat kontrak live di employee-service: koleksi `employee_contract` sebagai pemilik ([[REF - Kepemilikan Data]]), nomor otomatis, lampiran PDF, status dihitung saat baca, feed kalender `contract_end`, dan cron. Rutenya di [[API - Employee Service]] §Kontrak Kerja. Alur tanda tangan di dok domain berstatus 🟡: ADR ini berdiri di atas pondasi yang live dan desain yang belum ada kodenya.

**Kenapa bukan jalur tersertifikasi.** ADR 0019 memilih TTE tersertifikasi via PSrE, e-KYC karyawan, e-Meterai lewat API, dan service baru. Pemilik proses menolak ketergantungan vendor, biaya per transaksi, dan friksi e-KYC, lalu memilih tanda tangan tidak tersertifikasi. Dasar hukumnya (sumber sekunder, belum dikonfirmasi legal): UU ITE Pasal 11 ayat (1) dan PP 71/2019 Pasal 59 ayat (3) mengakui tanda tangan elektronik tidak tersertifikasi sepanjang memenuhi enam syarat: data pembuatannya hanya terkait dengan dan berada dalam kuasa penanda tangan, perubahan tanda tangan maupun dokumen setelah penandatanganan dapat diketahui, ada cara andal mengidentifikasi penanda tangan, dan ada mekanisme yang menunjukkan persetujuan. Bedanya di pembuktian: bila disangkal, perusahaan membuktikan lewat jejak sistemnya sendiri.

**Lubang yang ditemukan grounding**, dicek langsung ke `origin/main` 2026-09-11. Semuanya melemahkan PIN sebagai bukti:

1. PIN bisa dicoba tanpa batas: grup `/auth` gateway tanpa limiter (`api-gateway/main.go:271`), `/login/pin` tanpa JWT (`:328`), dan `verify-pin` mencari akun dari body, bukan dari token (`services/employee/main.go:3101-3108`).
2. Reset akun oleh IT menyetel password sementara = `employee_id` dan mengosongkan PIN (`main.go:6579-6591`), tanpa jejak. Siapa pun yang tahu ID karyawan bisa mengaktifkan ulang akunnya lebih dulu daripada pemiliknya.
3. `device_id` Android = `androidInfo.id` (Build.ID), tidak unik per perangkat (`mybharata-app/lib/src/core/utils/device_info_helper.dart:32`).
4. Biometrik hanya diverifikasi di perangkat; `/auth/login-biometrics` menerima JWT lama tanpa bukti kunci apa pun.
5. Hasil verifikasi PIN tidak terikat ke tindakan berikutnya: endpoint hanya membalas pesan, dan gerbang PIN MyBharata berlaku per sesi ([[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] §1).
6. Akun direktur dipakai bersama Sekretariat dan dikecualikan dari pengikatan perangkat (`main.go:2773-2780`). `common.SetaraDirektur` juga meloloskan Corporate Secretary (`shared-library/common/jabatan_direktur.go:24-27`).
7. Kunci baca prefix MinIO `employee/`, tempat lampiran kontrak disimpan, tertanam di bundel browser (`erp-frontend/src/hooks/use-document.ts:5-7`; [[Microservices - File Service]]).

**Data nyata tidak terukur.** Volume kontrak per bulan, kontrak kedaluwarsa pada karyawan aktif, dan cakupan akun/PIN MyBharata tidak bisa dibaca dari prod (ditolak classifier dua kali). Skrip baca-saja disiapkan di `.task-plans/cek-kontrak-esign-prod.ps1`. Diperlakukan sebagai risiko di bawah.

**Aturan bisnis.** Peraturan Perusahaan (`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`) tidak mengatur PKWT, penandatanganan, maupun meterai. Yang bersinggungan hanya komponen gaji di Lampiran 1 (tunjangan kehadiran, uang makan), yang nilainya diambil dari payroll, tidak dihitung ulang.

## Decision

### 1. Tanda tangan elektronik tidak tersertifikasi, dibangun sendiri

Tanpa PSrE, tanpa e-KYC, tanpa vendor. Menggantikan ADR 0019 seluruhnya.

### 2. Pengingat kontrak habis dikerjakan lebih dulu dan terpisah

Kebutuhan kedua tidak menunggu tanda tangan. Cron employee-service mengirim inbox ke HR menjelang kontrak berakhir, dan ke atasan untuk penilaian kinerja paling lambat 7 hari kerja sebelum berakhir (Pasal 2 ayat 6 template PKWT). Ambang "menjelang berakhir" memakai fungsi klasifikasi yang sama dengan daftar dan ringkasan kontrak, supaya pengingat, tabel, dan kartu tidak pernah menyebut status berbeda.

### 3. Menempel di modul kontrak employee-service, bukan service baru

Status tanda tangan disimpan pada `employee_contract`. Catatan tiap tindakan tanda tangan disimpan di koleksi baru yang **hanya bisa ditambah dan tanpa TTL**; pola jejak yang sudah ada ber-TTL 365 hari, jadi tidak bisa dipakai. Logikanya ditaruh di berkas dan koleksi sendiri supaya bisa diangkat ke service tersendiri bila kelak ada pemakai ketiga (offer letter, SP, NDA).

Service penandatanganan generik ditolak sekarang karena belum ada pemakai kedua, dan karena pertanyaan "kontrak ini sudah ditandatangani?" akan hidup di dua database. Acknowledgment HRD Documents ditolak karena isinya Markdown, tanpa konfirmasi identitas, dan milik service lain.

### 4. Alur dan urutan

1. HR membuat kontrak; sistem mengisi template PKWT menjadi PDF draft.
2. Karyawan meninjau di MyBharata: **setuju isi**, atau **minta koreksi** yang kembali ke HR.
3. HR membubuhkan e-Meterai pada PDF yang sudah disetujui, di portal distributor resmi Peruri, lalu mengunggahnya.
4. Sistem **mengunci** PDF itu dan menyimpan hash SHA-256-nya. PDF bermeterai tidak pernah diubah lagi.
5. Karyawan menandatangani dengan PIN, lalu direktur menandatangani dengan PIN (bisa banyak sekaligus dari antrean Ruang Direktur). Keduanya terikat ke hash di langkah 4.
6. Sistem menerbitkan **lembar bukti tanda tangan** sebagai PDF terpisah (penanda tangan, waktu server, hash, perangkat, kode verifikasi) dan mengirim salinan ke karyawan.

Persetujuan isi sebelum meterai disengaja: meterai sekali pakai, dan kontrak yang ditolak setelah dibubuhi berarti satu meterai terbuang. Karyawan menandatangani lebih dulu supaya direktur hanya menandatangani kontrak yang sudah disetujui pihak lawannya.

### 5. e-Meterai urusan HR

Sistem tidak berintegrasi dengan API meterai dan tidak memverifikasi keaslian meterai. HR bertanggung jawab membelinya (akun enterprise di distributor resmi) dan membubuhkannya.

### 6. Bukti tanda tangan = PIN per tindakan, diverifikasi server

Endpoint tanda tangan memverifikasi PIN milik **pemegang token** (identitas dari header gateway), bukan `employee_id` dari body, dengan batas percobaan dan penguncian yang tercatat. Verifikasi PIN yang sudah terjadi di sesi yang sama tidak dihitung. Biometrik **tidak** diterima sebagai bukti.

Catatan tanda tangan merekam `employee_id`, peran (karyawan atau Pihak Pertama), waktu server, hash PDF, ID instalasi aplikasi, IP, dan versi aplikasi.

### 7. Prasyarat keamanan sebelum tanda tangan dirilis

- Limiter untuk login PIN dan verifikasi PIN di gateway.
- Reset akun dan forget-device tercatat; akun yang direset tidak bisa menandatangani sampai HR menandai identitasnya sudah diverifikasi ulang.
- ID instalasi persisten di MyBharata, menggantikan Build.ID sebagai `device_id`.

Tanpa ketiganya, PIN tidak memenuhi syarat "berada dalam kuasa penanda tangan".

### 8. Pihak Pertama = direktur yang ditetapkan per perusahaan

Penandatangan perusahaan diambil dari data penandatangan per perusahaan (baru), **bukan** dari `common.SetaraDirektur`, yang ikut meloloskan Corporate Secretary. Akun direktur yang dipakai bersama Sekretariat **diterima apa adanya** (keputusan pemilik proses 2026-09-11). Lembar bukti mencatat tanda tangan "atas nama Direktur" beserta akun yang dipakai, dan tidak mengklaim lebih dari itu.

### 9. Arsip di prefix tersendiri, terkunci

PDF bermeterai final dan lembar bukti disimpan di prefix MinIO baru **tanpa kunci baca di browser** (pola `audit/`), dibaca lewat proxy employee-service. Setelah terkunci, lampiran tidak bisa diganti atau dihapus lewat jalur mana pun. Yang boleh membuka: staf HR berizin HRIS, karyawan yang bersangkutan, dan direktur. Atasan tidak, karena kontrak memuat gaji.

### 10. Kepemilikan tidak berubah

`employee_contract` tetap pemilik fakta kontrak. Salinan `work_data.employment_type` dan `contract_ending` tetap hanya ditulis modul kontrak.

## Consequences

- ➕ Tanpa biaya per tanda tangan dan tanpa vendor; bisa dimulai sekarang di atas pondasi yang live.
- ➕ Kontrak habis yang tak terpantau terjawab lebih dulu, terlepas dari tanda tangan.
- ➕ Satu pemilik data kontrak; tidak ada service maupun modul gateway baru.
- ➖ Bukti hukum lebih lemah daripada yang tersertifikasi. Bila disangkal, perusahaan bergantung pada jejak sistemnya sendiri; relevan untuk klausul denda di Pasal 4 template.
- ➖ Tanda tangan Pihak Pertama tidak bisa dibuktikan berasal dari direktur pribadi karena akunnya dipakai bersama. **Risiko diterima sadar.**
- ➖ Langkah manual HR bertambah per kontrak (unduh, bubuhkan meterai, unggah), meski bisa dikerjakan per kelompok.
- ➖ employee-service, yang sudah paling besar, bertambah lagi.
- ⚠️ **Konfirmasi legal belum ada.** Rilis tanda tangan menunggu konfirmasi itu; pengingat tidak.
- ⚠️ **Data prod belum terukur.** Bila banyak karyawan belum aktivasi MyBharata, HR perlu membantu aktivasi, dan jalur kertas tetap tersedia sebagai cadangan.
- ⚠️ Temuan sampingan grounding mobile yang **belum diverifikasi**: membuka notifikasi di MyBharata bisa melewati gerbang PIN, karena kunci `user_pin` yang dicek tidak pernah ditulis (`lib/src/core/.../notification_handler.dart:81` menurut grounding). Wajib dicek sebelum "Kontrak Saya" dibuka lewat notifikasi.
- 🔗 **Deploy**: kategori inbox baru berarti notification-service naik lebih dulu, lalu employee-service, keduanya di-rebuild (`shared-library/models/notification/models.go:269-273`). MyBharata perlu rilis: pemetaan kategori di empat tempat, version name dan code naik bersama. Prefix MinIO baru berarti file-service `up -d --build` bila biner belum memuatnya, kunci unik di `.env` dev dan prod, employee-service `--force-recreate`, dan bukti lewat hitungan prefix di log boot. Perubahan kontrak API berarti backend sebelum Web ERP dan MyBharata. Deploy prod dijalankan manusia.

## Dokumen Terkait

- [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] (cara kerja) · [[HRIS - Personalia]]
- [[ADR - 0019 Kontrak Kerja Elektronik via Service Internal + Lapisan Tersertifikasi]] (digantikan)
- [[REF - Kepemilikan Data]] · [[API - Employee Service]] · [[Microservices - Employee Service]] · [[Microservices - File Service]] · [[Microservices - Notification Service]]
- [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] (gerbang PIN per sesi) · [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]] · [[ADR - 0002 Database-per-Service]]
- Daftar task: `Workspace/ANALISA - Tanda Tangan Kontrak Kerja dan Pengingat Kontrak Habis.md`

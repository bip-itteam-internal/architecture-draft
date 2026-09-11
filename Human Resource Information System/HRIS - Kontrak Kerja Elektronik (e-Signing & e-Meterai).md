## Deskripsi

*Digitalisasi kontrak kerja karyawan (PKWT/PKWTT): dokumen dibuat dari template berbasis data HRIS, ditandatangani secara elektronik **tidak tersertifikasi** **tatap muka di kantor dan didampingi HRD** (karyawan menggores tanda tangan di perangkat HR, direktur mengonfirmasi dari Ruang Direktur), dibubuhi **e-Meterai** oleh HR, lalu salinannya dikirim ke karyawan. Ditambah pengingat otomatis sebelum kontrak berakhir. Keputusannya di [[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]], yang menggantikan rancangan tersertifikasi [[ADR - 0019 Kontrak Kerja Elektronik via Service Internal + Lapisan Tersertifikasi]]. Dibangun di atas modul riwayat kontrak yang **sudah live** di [[Microservices - Employee Service]] (koleksi `employee_contract`).*

- **Status**: 🟡 **Konsep / Direncanakan** untuk tanda tangan dan e-Meterai; belum ada di kode. ⚠️ **Pengingat kontrak habis: kode selesai di branch `feat/employee-pengingat-kontrak` (bip-erp, 2026-09-11), belum merge dan belum deploy** (§Pengingat Kontrak Habis). Pondasinya (riwayat kontrak + lampiran PDF) sudah ✅ live, diverifikasi ke `bip-erp` `origin/main` `915ca2f8` pada 2026-09-11; rinciannya di §Pondasi yang Sudah Ada.
- **Ruang lingkup implementasi**: modul kontrak employee-service (status tanda tangan, sesi tanda tangan tatap muka, catatan tanda tangan, pengingat), prefix arsip MinIO baru, Web ERP (layar tanda tangan di perangkat HR, status di halaman Kontrak, antrean Ruang Direktur), salinan lewat email, dan MyBharata ("Kontrak Saya", baca-saja). Tanpa vendor PSrE, tanpa integrasi API meterai, tanpa tanda tangan jarak jauh.
- **Endpoint yang sudah ada**: [[API - Employee Service]] §Kontrak Kerja. Layar HR: [[APP - Web ERP]] `/hris/contract`.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Staf HR / HRD (Personalia) | menyiapkan kontrak, mendampingi penandatanganan dan mencocokkan KTP, membubuhkan e-Meterai di portal distributor lalu mengunggah, memantau status | `gateHris` + `RequireHRISStaff` (baca `PermHrisView`, tulis `PermHrisWork`) | Web ERP, `/hris/contract`, perangkat HR |
| Karyawan (Pihak Kedua) | membaca dan menggores tanda tangan di kantor, didampingi HRD; menerima salinan | tidak login saat menandatangani; salinan lewat email (karyawan baru) atau "Kontrak Saya" (karyawan aktif, belum ada) | perangkat HR; email; [[APP - MyBharata]] |
| Direktur (Pihak Pertama) | menandatangani banyak kontrak sekaligus | akun dipakai bersama Sekretariat (lihat §Keamanan Akun) | Web ERP, Ruang Direktur |
| Atasan langsung | menerima pengingat penilaian kinerja sebelum kontrak berakhir | tidak membuka PDF kontrak, karena memuat gaji | MyBharata / Web ERP |

- **Tujuan**: kontrak terbit dan ditandatangani tanpa cetak dan meterai tempel; arsipnya tidak tercecer; karyawan memegang salinannya; tidak ada kontrak yang habis tanpa diketahui.
- **Pain point** (wawancara 2026-09-11 + kode): kertas dan biaya cetak PKWT; kontrak habis tak terpantau; dokumen disiapkan dan ditandatangani di luar sistem lalu PDF-nya diunggah HR secara manual; isinya tidak terisi otomatis; karyawan tidak punya jalur membuka kontraknya sendiri.
- **Aksi utama**: buat kontrak atau perpanjangan → karyawan datang dan menandatangani didampingi HRD → direktur menandatangani → HR bubuhkan meterai → arsip final + salinan.

## Pondasi yang Sudah Ada (grounded)

Diverifikasi ke `bip-erp` `origin/main` `915ca2f8`, `erp-frontend` `origin/main` `47e1dd8b`, dan `mybharata-app` `origin/main`, 2026-09-11.

| Sudah ada | Di kode | Peran untuk tanda tangan |
|---|---|---|
| Koleksi `employee_contract` sebagai sumber kebenaran; perpanjangan = dokumen **baru**, dokumen lama tak ditimpa | `EmployeeContract` (`shared-library/models/employee/models.go`), `services/employee/contract.go` | satu dokumen kontrak = satu objek yang ditandatangani |
| Validasi server: jenis `PKWTT`/`PKWT`/`PKWT (Evaluasi)`/`Magang`; PKWTT tanpa tanggal berakhir, jenis lain wajib; kontrak tumpang tindih ditolak | `validateContract` (`contract.go`) | |
| Salinan `work_data.employment_type` + `contract_ending` ditulis **hanya** oleh modul kontrak (`segarkanSalinan`); pintu tulis `work_data` lain membuang kedua field itu | `contract.go`, `partial_update.go`; lihat [[REF - Kepemilikan Data]] | modul tanda tangan tidak menulis `work_data` |
| Kontrak pertama lahir otomatis di transaksi create-employee | `kontrakPertama` (`contract.go`), dipanggil `func.go` | |
| Migrasi saat boot: karyawan lama dibuatkan satu kontrak `migrated: true` dengan `start_date` = `join_date` (hanya perkiraan) | `contract_migrate.go` | |
| Nomor kontrak otomatis `NNN/<type>/<company_id>/<bulan romawi>/<tahun>` | `nomorKontrak` (`contract.go`) | ⚠️ lihat celah 1 |
| Lampiran PDF per kontrak (PDF saja, maks 4 MB), object key `employee/<employee_id>/contract/<contract_id>/<hex>.pdf` lewat [[Microservices - File Service]] | `contract_file.go`, field `EmployeeContract.File` | ⚠️ lihat celah 2 dan 6 |
| Status dihitung saat baca: `ongoing` / `ending` (berakhir dalam 2 bulan) / `expired`, plus kartu ringkasan | `contract.go` (`statusKontrak`), `contract_summary.go` (`klasifikasiKontrak`) | ⚠️ di `origin/main` tiap jalur punya batas hari sendiri; disatukan dalam tanggal WIB di branch pengingat (belum merge), lihat §Pengingat Kontrak Habis |
| Feed kalender `contract_end`, hanya kontrak **milik pemanggil sendiri** | `calendar_feed.go` → [[Microservices - Calendar Service]] | |
| Cron (`robfig/cron`) berjalan di employee-service untuk resign, mutasi, KPI, dan lain-lain | `services/employee/cron.go` | tempat job pengingat (`cronPengingatKontrak`, branch) |
| Helper inbox + penerima HR + rantai atasan | `kirimInboxKategori` (`warning_notify.go`), `penerimaHRPerusahaan` (`mutasi_notify.go`), `penyetujuUntukLookup` (`department_approver_lookup.go`) | pengingat, lewat varian bergalat `kirimInboxKategoriGalat` (branch) |
| Email berlampiran PDF | notification-service `POST /email/send` (Resend) | salinan untuk karyawan baru |
| Antrean persetujuan Ruang Direktur | `erp-frontend/src/features/direktur/` (`tab-antrean.ts`, `use-antrean-direktur.ts`) | tempat antrean tanda tangan direktur; persetujuannya masih satu per satu |
| Layar HR: daftar, kartu ringkasan, panel riwayat (perpanjang, perbaiki, unggah/ganti/buka lampiran) | `erp-frontend` `app/(main)/hris/contract/page.tsx`, `features/hris/contract/` | diperluas dengan status dan sesi tanda tangan |
| Preseden pembuatan PDF di server: slip gaji dengan `go-pdf/fpdf` (hanya font inti) | `services/payroll/payslip_pdf.go` | |
| MyBharata memuat `syncfusion_flutter_pdfviewer` (baru dipakai untuk PDF aset bawaan) dan gerbang PIN slip gaji | `mybharata-app/pubspec.yaml`, [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] | "Kontrak Saya" baca-saja |

> Koreksi atas versi awal dok ini: `Contract.file_object` di tipe FE daftar kontrak adalah **foto karyawan** untuk avatar (`EmployeeIdentityCell`), bukan slot berkas kontrak. Berkas kontrak ada di `EmployeeContract.File`.

### Celah pondasi yang harus ditutup

1. **Nomor kontrak tidak unik.** Urutan `NNN` dihitung **per karyawan** (jumlah kontrak karyawan itu ditambah satu, sehingga kontrak pertama dan hasil migrasi selalu `001`), dan tidak ada index unik pada `number`. Dua karyawan berjenis kontrak sama yang mulai di bulan yang sama mendapat nomor identik. Formatnya juga belum dikonfirmasi HR (komentar di `nomorKontrak`) dan berbeda dari kop template PKWT HR (`…/HRD/PKWT/…/…`).
2. **Lampiran bisa diganti kapan saja.** Kontrol unggah selalu tampil di panel riwayat, dan objek lama dihapus dari MinIO saat diganti. PDF yang sudah dikunci tidak boleh bisa diganti.
3. **Karyawan tidak punya jalur ke kontraknya sendiri.** Seluruh rute kontrak bergerbang `RequireHRISStaff`. Feed kalender `contract_end` menampilkan kontrak milik pemanggil dengan `deep_link` `/hris/contract?employee_id=<id>`, padahal halaman itu khusus staf HRIS dan tidak membaca parameter `employee_id`.
4. **Notifikasi otomatis kontrak mendekati habis** tidak ada di `origin/main` (git grep 2026-09-11). Dijawab pengingat kontrak habis: kode di branch `feat/employee-pengingat-kontrak`, belum merge (§Pengingat Kontrak Habis).
5. **Validasi hanya mengecek tumpang tindih**, belum batas total durasi PKWT.
6. **Lampiran ada di prefix `employee/`**, yang kunci bacanya tertanam di bundel browser (`erp-frontend/src/hooks/use-document.ts`). Kontrak bergaji yang ditandatangani tidak boleh bergantung pada rahasianya object key.

## Keamanan Akun

Tanda tangan dilakukan tatap muka dan **tidak memakai akun maupun PIN karyawan** ([[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]] §6-§7), jadi lubang di bawah **tidak menahan** fitur ini. Tetap dicatat karena nyata dan menjadi task keamanan akun terpisah. Dicek ke `origin/main` 2026-09-11.

| Lubang | Bukti | Relevansi ke kontrak |
|---|---|---|
| PIN bisa dicoba tanpa batas | grup `/auth` gateway tanpa limiter (`api-gateway/main.go:271`), `/login/pin` tanpa JWT (`:328`); `verify-pin` mencari akun dari body (`services/employee/main.go:3101-3108`) | "Kontrak Saya" di balik gerbang PIN |
| Akun bisa diambil alih setelah reset IT | password sementara = `employee_id`, PIN dikosongkan, tanpa jejak (`main.go:6579-6591`) | "Kontrak Saya" |
| Akun karyawan baru lahir dengan password = `employee_id` | `orchestrator/hris/helper.go:471-485`; akun pihak luar sudah acak 16 karakter (`services/employee/external_account_password.go`) | "Kontrak Saya" |
| ID perangkat Android tidak unik | `androidInfo.id` = Build.ID (`mybharata-app/lib/src/core/utils/device_info_helper.dart:32`) | tidak |
| Biometrik tidak bisa dibuktikan ke server | `/auth/login-biometrics` hanya menerima JWT lama | tidak |
| Akun direktur dipakai bersama Sekretariat, bebas pengikatan perangkat | `main.go:2773-2780`; `SetaraDirektur` juga meloloskan Corporate Secretary (`shared-library/common/jabatan_direktur.go:24-27`) | **ya**: diterima apa adanya (2026-09-11); penandatangan diambil dari data penandatangan per perusahaan, lembar bukti menulis "atas nama Direktur" + akun yang dipakai |

⚠️ Temuan sampingan grounding mobile yang **belum diverifikasi**: membuka notifikasi di MyBharata bisa melewati gerbang PIN karena kunci `user_pin` yang dicek tidak pernah ditulis. Wajib dicek sebelum "Kontrak Saya" (memuat gaji) dirilis.

## Latar Belakang & Landasan Hukum

Kontrak kerja masih disiapkan dan ditandatangani di luar sistem: cetak, meterai tempel, tanda tangan basah dua pihak, lalu (sejak modul riwayat kontrak ada) PDF-nya diunggah HR. Wawancara 2026-09-11 menyebut dua masalah yang ingin dihilangkan: kertas dan biaya cetak PKWT yang sering diperpanjang, dan kontrak habis yang tak terpantau. **Cara menandatangani yang berlaku**: karyawan baru maupun perpanjangan menandatangani di kantor, didampingi HRD; kontrak karyawan baru dikirim lewat email.

- **Ketenagakerjaan**: UU 13/2003 jo. UU 6/2023 (Cipta Kerja) + PP 35/2021. PKWT wajib tertulis dan berbahasa Indonesia, cocok untuk template baku. Bentuk elektronik tidak mengurangi keabsahan.
- **Tanda tangan elektronik tidak tersertifikasi** (dasar keputusan ADR 0089; sumber sekunder, **belum dikonfirmasi legal**): UU ITE Pasal 11 ayat (1) dan PP 71/2019 Pasal 59 ayat (3) mengakuinya sepanjang memenuhi enam syarat: data pembuatannya hanya terkait dengan penanda tangan, berada dalam kuasa penanda tangan, perubahan tanda tangan setelah penandatanganan dapat diketahui, perubahan dokumen setelah penandatanganan dapat diketahui, ada cara andal mengidentifikasi penanda tangan, dan ada mekanisme yang menunjukkan persetujuan. Pada jalur tatap muka, identifikasi dilakukan HRD yang hadir (pencocokan NIK dari KTP), persetujuan lewat goresan dan pernyataan setuju, dan perubahan dokumen terdeteksi lewat hash. Bila disangkal, perusahaan membuktikan lewat jejak sistemnya sendiri dan kesaksian HRD, bukan lewat PSrE sebagai pihak ketiga.
- **Jalur tersertifikasi** (PSrE + e-KYC karyawan) dipertimbangkan di ADR 0019 dan **tidak dipilih**: ketergantungan vendor, biaya per transaksi, dan friksi e-KYC.
- **Bea meterai / e-Meterai**: UU 10/2020 + PP 86/2021. e-Meterai **hanya sah bila diterbitkan Perum Peruri** lewat distributor resmi; distributor menjual ke akun perusahaan (enterprise) dan meterai dapat dibubuhkan pada PDF tanpa tanda tangan tersertifikasi. Perjanjian kerja adalah objek bea meterai (Rp10.000), **tetapi meterai bukan syarat sah** perjanjian; dokumen yang kelak dipakai sebagai alat bukti dapat dimeteraikan kemudian (pemeteraian kemudian, UU 10/2020). Sistem tidak memverifikasi keaslian meterai.
- **Peraturan Perusahaan** (`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`) tidak mengatur PKWT, penandatanganan, maupun meterai. Yang bersinggungan hanya komponen gaji di Lampiran 1 (tunjangan kehadiran, uang makan).

### Template PKWT yang berlaku

Sumber: dokumen template PKWT dari HR, diterima 2026-09-11 (berkasnya tidak disimpan di vault). Strukturnya:

| Bagian | Isi yang perlu diisi per kontrak |
|---|---|
| Kop + nomor | nomor berformat `…/HRD/PKWT/…/…` |
| Pihak Pertama | nama, jabatan (direktur), instansi, alamat perusahaan |
| Pihak Kedua | nama lengkap, NIK, tempat & tanggal lahir, alamat, telepon/HP, email |
| Pembuka | hari, tanggal, bulan, tahun perjanjian |
| Pasal 1 Ketentuan Umum | teks tetap |
| Pasal 2 Penunjukan | jabatan, lokasi kerja, durasi (bulan), tanggal mulai dan berakhir. Memuat kewajiban perusahaan menilai kinerja paling lambat 7 hari kerja sebelum kontrak berakhir |
| Pasal 3 Hak & Kewajiban | gaji mengikuti SK Direksi dengan rincian di Lampiran 1; jaminan sosial |
| Pasal 4 Sanksi | teks tetap |
| Pasal 5 Waktu Kerja | jam kerja, saat ini ditulis tetap di template |
| Pasal 6-7 | teks tetap; Pasal 7 menyatakan perjanjian dibuat bermeterai 10.000 |
| Tanda tangan | Pihak Pertama dan Pihak Kedua. Isinya bergantung hasil uji S1: goresan tercetak di kotak (urutan A), atau tulisan "ditandatangani secara elektronik" dengan goresan di lembar bukti (urutan B) |
| Lampiran 1 Estimasi Gaji | jabatan, gaji pokok, kehadiran, tunjangan jabatan, uang makan (tunjangan tidak tetap), total terima |

## Arsitektur

Mengikuti [[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]] §3: menempel di modul kontrak employee-service, bukan service baru. Logikanya dipisah di berkas dan koleksi sendiri supaya bisa diangkat keluar bila kelak ada pemakai ketiga.

| Kebutuhan | Komponen | Status |
|---|---|---|
| Record kontrak + salinan `work_data` | employee `employee_contract` (pemilik) | reuse, sudah live |
| Status tanda tangan | field baru pada `employee_contract` | baru |
| Sesi tanda tangan tatap muka | modul kontrak: dibuka HRD (izin kerja HRIS), pencocokan NIK, goresan, pernyataan setuju | baru |
| Catatan tanda tangan | koleksi baru, hanya-tambah, **tanpa TTL** | baru |
| Template, PDF draft, lembar bukti | modul kontrak; preseden `go-pdf/fpdf` slip gaji | baru |
| Arsip PDF final, goresan, lembar bukti | prefix MinIO baru tanpa kunci baca di browser, dibaca lewat proxy employee-service | baru |
| Pengingat | `contract_pengingat.go` + cron 07:00 WIB, `kirimInboxKategoriGalat`, kategori `reminder`, koleksi `employee_contract_pengingat` | ⚠️ kode di branch, belum merge |
| Salinan untuk karyawan baru | notification-service `POST /email/send` (lampiran PDF) | reuse |
| Layar HR | halaman Kontrak + panel riwayat + layar tanda tangan di perangkat HR | perluasan |
| Layar direktur | antrean Ruang Direktur + tanda tangan massal | perluasan |
| Layar karyawan aktif | MyBharata "Kontrak Saya", baca-saja, di balik gerbang PIN | baru |
| e-Meterai | portal distributor resmi Peruri, dikerjakan HR | di luar sistem |

**Tidak dipakai**: [[Microservices - HRD Document Service]]. Acknowledgment-nya menyimpan Markdown, tanpa konfirmasi identitas, dan milik service lain.

## Alur Tanda Tangan

Nama status di bawah usulan; ditetapkan saat `/plan`. Posisi `MENUNGGU_METERAI` bergantung hasil uji S1.

```
Urutan A (bila S1 lolos):
DRAFT ──▶ MENUNGGU_TTD_KARYAWAN ──▶ MENUNGGU_TTD_DIREKTUR ──▶ MENUNGGU_METERAI ──▶ SELESAI

Urutan B (bila S1 gagal):
DRAFT ──▶ MENUNGGU_METERAI ──▶ MENUNGGU_TTD_KARYAWAN ──▶ MENUNGGU_TTD_DIREKTUR ──▶ SELESAI

jalur samping: KOREKSI_DIMINTA (kembali ke DRAFT) · DIBATALKAN (sebelum SELESAI)
```

1. **Draft**: HR membuat kontrak baru atau perpanjangan; sistem mengisi template dan menerbitkan PDF draft. Draf boleh dikirim ke email karyawan lebih dulu.
2. **Sesi tatap muka**: karyawan datang ke kantor. HRD membuka sesi untuk kontrak itu di perangkat HR dan mengetik NIK dari KTP fisik; yang tidak cocok dengan `personal_data.nik_number` ditolak.
3. **TTD karyawan**: karyawan membaca kontrak di layar, menggores tanda tangan, dan menyatakan setuju; atau minta koreksi (kembali ke HR).
4. **TTD direktur**: kontrak masuk antrean Ruang Direktur; direktur menandatangani satu atau banyak sekaligus.
5. **Meterai + kunci**: HR membubuhkan e-Meterai di portal distributor lalu mengunggahnya. Sistem menyimpan PDF di prefix arsip, menghitung hash SHA-256, dan mengunci lampiran. Pada urutan A, sistem memeriksa bahwa PDF bermeterai memuat PDF yang ditandatangani tanpa perubahan.
6. **Selesai**: sistem menerbitkan lembar bukti tanda tangan (PDF terpisah), mengirim salinan (email untuk karyawan baru, "Kontrak Saya" untuk karyawan aktif), dan status di halaman Kontrak HR menjadi selesai.

## Pengingat Kontrak Habis

> ⚠️ **Kode selesai di branch `feat/employee-pengingat-kontrak` (bip-erp, 2026-09-11), belum merge dan belum deploy.** Ukur ulang sebelum menyebutnya live: baris log `[Pengingat Kontrak]` di container employee-service dan isi koleksi `employee_contract_pengingat`. Rencana dan langkah verifikasinya: `.task-plans/2026-09-11-pengingat-kontrak-habis.md`.

Menjawab kebutuhan kedua, terlepas dari tanda tangan, dan dirilis lebih dulu ([[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]] §2). Kode: `services/employee/contract_pengingat.go`, didaftarkan di `cron.go`.

- **Sinyal**: satu fungsi klasifikasi (`klasifikasiKontrak`, ambang `bulanSegeraBerakhir` = 2 bulan, eksklusif) yang dipakai bersama daftar, ringkasan, riwayat, dan pengingat, dihitung dalam **tanggal WIB**. Hari berakhir masih milik kontrak: statusnya `ending` sampai hari itu habis dan `expired` mulai keesokan harinya. ⚠️ Terlihat di halaman Kontrak: sebelumnya daftar, ringkasan, dan riwayat sudah menyebut `expired` sejak jam tertentu di hari terakhir, dengan batas yang berbeda satu sama lain.
- **Yang dipantau**: kontrak **terakhir** (`start_date` terbaru) tiap karyawan **aktif** (`system_authentication.is_active`) di perusahaannya sekarang (`work_data.company_id`). Kontrak terakhir dipilih dari semua jenis lebih dulu, jadi karyawan yang sudah diangkat PKWTT tidak diingatkan soal PKWT lamanya; kontrak milik perusahaan lama sesudah mutasi antar-tenant dilewati.
- **Jadwal**: cron harian **07:00 WIB** (`0 7 * * *`), sesudah resign (00:10) dan mutasi (00:15) diterapkan. Tahap dihitung ulang tiap hari dari sisa hari, jadi hari yang terlewat karena container mati menyusul keesokan harinya tanpa mengirim tahap yang sudah basi.

| Penerima | Tahap (sisa hari kalender WIB) | Kunci catatan |
|---|---|---|
| Supervisor HR perusahaan | baru masuk "segera berakhir" (> 30) · H-30 (8..30) · H-7 (0..7) | `masuk-segera` · `h30` · `h7` |
| Supervisor HR perusahaan | kontrak kedaluwarsa pada karyawan aktif, sekali per minggu ISO | `kedaluwarsa-<tahun>-W<minggu>` |
| Atasan langsung | H-14 (0..14), untuk penilaian kinerja (Pasal 2 ayat 6), pengganti menghitung "7 hari kerja" | `atasan-h14` |
| Supervisor HR perusahaan | kontrak di tahap H-14 yang karyawannya **tanpa atasan tercatat** | `atasan-h14` (peran `hr`) |

- **Penerima HR**: `penerimaHRPerusahaan` (department `Human Resource` + `is_supervisor`), lalu disaring ke akun aktif karena fungsi itu sendiri tak memeriksa `is_active`. Perusahaan tanpa supervisor HR aktif tidak menerima apa pun dan disebut di log.
- **Atasan**: `work_data.supervisor_id` bila aktif dan bukan dirinya sendiri; bila tidak, rantai atasan departemen yang sama dengan penyetuju cuti (`penyetujuUntukLookup`). Rantai yang menunjuk karyawan itu sendiri atau orang non-aktif berarti tanpa atasan, dan HR yang diberi tahu. Galat rantai tidak dianggap "tanpa atasan": dicoba lagi besok.
- **Isi pesan** (inbox kategori `reminder`, tanpa rute):
  - HR: **satu ringkasan per supervisor HR per jalan**, hanya bila ada yang jatuh jadwal. Judul "Pengingat kontrak kerja". Baris pertama kalimat polos berisi jumlah per tahap, lalu bagian per tahap, paling mendesak di atas: sudah berakhir, 7 hari, 30 hari, 2 bulan, belum punya atasan. Tiap baris memuat nama, ID, tanggal berakhir (nama bulan Indonesia), dan sisa hari. Maksimal **20 baris per bagian**, sisanya "dan N lainnya". Penutup menyebut jalur menu HRIS → Personalia → Kontrak, dan HRIS → Personalia → Atasan Langsung untuk bagian tanpa atasan.
  - Atasan: satu pesan per atasan, judul "Kontrak bawahan segera berakhir": nama, ID, dan tanggal berakhir saja, tanpa gaji maupun isi kontrak lain, dengan permintaan menilai kinerja dan menyampaikan rekomendasi perpanjangan ke HR.
  - Nama di-escape markdown dan baris barunya dilebur, karena isi inbox dirender sebagai markdown di Web ERP dan MyBharata. notification-service meneruskan badan utuh ke push ponsel dan browser ([[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]]), jadi yang terbaca di notifikasi yang belum dibuka adalah baris pertamanya.
- **Idempoten**: koleksi `employee_contract_pengingat`, satu dokumen per (kontrak, tahap, penerima) yang **berhasil** terkirim, index unik `contract_id + tahap + penerima_id` dibuat saat boot. Urutannya kirim dulu, catat sesudahnya. Kiriman yang gagal dicoba lagi besok. Catatan yang gagal ditulis sesudah kiriman berhasil membuat pesan yang sama terkirim lagi besok (diterima sadar: pesan ganda lebih baik daripada pesan yang tak pernah tiba). Gagal membaca catatan berarti tidak mengirim apa pun hari itu.
- **Keandalan**: `defer recover` di job, karena cron employee-service tanpa `cron.Recover` dan panic di job akan menjatuhkan seluruh service; galat `AddFunc` di-log. Satu baris log per jalan: kontrak jatuh jadwal, pesan terkirim, gagal, catatan gagal ditulis, kontrak tanpa atasan, gagal mencari atasan, perusahaan tanpa supervisor HR aktif. Tanpa distributed lock: aman selama employee-service satu instance.
- **Verifikasi DEV**: env `PENGINGAT_KONTRAK_SAAT_BOOT=true` menjalankan job sekali saat boot. Env dibaca saat container dibuat, jadi butuh `--force-recreate`; PROD tidak mengisinya. Tidak ada endpoint pemicu manual, karena `/internal/` bukan batas keamanan.
- **Deploy**: employee-service saja. Tanpa kategori inbox baru, jadi notification-service tidak perlu naik; tanpa perubahan kontrak API. Deploy prod dijalankan manusia.

**Belum dijawab** (task lanjutan di `Workspace/ANALISA - Tanda Tangan Kontrak Kerja dan Pengingat Kontrak Habis.md`):
- ⚠️ Pesan tidak bisa diketuk menuju halaman Kontrak: belum ada pemetaan rute inbox ke `/hris/contract`, dan halamannya tidak membaca query string. Pesan menyebut jalur menunya.
- ⚠️ Hasil penilaian kinerja dari atasan tidak kembali ke sistem, dan HR tidak diberi tahu.
- ⚠️ Panjang ringkasan pertama di prod belum terukur: jumlah kontrak kedaluwarsa pada karyawan aktif belum dibaca (skrip `.task-plans/cek-kontrak-esign-prod.ps1`).

## Pemetaan Field Template ← Sumber Data

Diisi otomatis saat dokumen dibuat, bukan diketik ulang. Dicek per isian template PKWT HR (§Template PKWT yang berlaku), 2026-09-11:

| Bagian | Isian | Sumber (grounded) | Status |
|---|---|---|---|
| Kop | nomor kontrak | `nomorKontrak` (employee-service) | ⚠️ format dan keunikan, lihat celah 1 |
| Pihak Pertama | nama, jabatan, alamat penandatangan | **tidak ada**. Master tenant `Company` hanya `key`/`name`/`code` (`shared-library/models/employee/master_company.go`); `Company` payroll hanya `name`/`npwp`/`city`/`hrd_signer`/rekening (`services/payroll/models_company.go`) | ❌ perlu data penandatangan per perusahaan |
| Pihak Kedua | nama, NIK, tanggal lahir, alamat, email, HP | `personal_data`: `full_name`, `nik_number`, `date_of_birth`, `home_address`, `email_address`, `phone_number` | ✅ |
| Pihak Kedua | tempat lahir | **tidak ada** field-nya di `PersonalData` | ❌ |
| Pasal 2 | jabatan | `work_data.position` | ✅ |
| Pasal 2 | lokasi kerja | template menulis alamat kantor secara tetap; sumber per karyawan belum dipetakan | ⚠️ TBD |
| Pasal 2 | durasi, tanggal mulai dan berakhir | `employee_contract.start_date` / `end_date` | ✅ |
| Pasal 5 | jam kerja | template menulis jam tetap; karyawan shift/roster punya jadwal sendiri di attendance | ⚠️ TBD |
| Lampiran 1 | gaji pokok | [[Microservices - Payroll Service]] `employee_salary.basic_salary` | ✅ |
| Lampiran 1 | kehadiran, tunjangan jabatan, uang makan | `employee_salary.component_values` | ⚠️ pemetaan komponen ke kolom belum ada |
| Lampiran 1 (karyawan baru) | gaji | recruitment `Offer.gaji_evaluasi` / `gaji_kontrak`: satu angka, tanpa rincian komponen | ⚠️ |
| Pembuka | hari dan tanggal perjanjian | saat penandatanganan | baru |

> Catatan struktur (grounded): penerima pengingat atasan diturunkan dari `work_data.supervisor_id` (atasan langsung, ditetapkan lewat `/supervisor-assignment`), dengan cadangan rantai atasan departemen yang sama dengan penyetuju cuti. Lihat [[HRIS - Organization Structure]].

## Data yang Ditulis

| Target | Yang ditulis | Catatan |
|---|---|---|
| `employee_contract` (pemilik) | status tanda tangan, rujukan PDF final, goresan, dan lembar bukti, hash | modul kontrak employee-service |
| Koleksi catatan tanda tangan (baru) | satu dokumen per tindakan: sesi dibuka, tanda tangan karyawan (hasil pencocokan NIK, HRD pendamping, perangkat, waktu), tanda tangan direktur, unggah meterai, pembatalan | hanya-tambah, tanpa TTL; NIK yang diketik tidak disimpan |
| `employee_contract_pengingat` (baru, ⚠️ branch) | satu dokumen per (kontrak, tahap, penerima) yang berhasil terkirim: `contract_id`, `employee_id`, `company_id`, `tahap`, `penerima_id`, `peran` (`hr`/`atasan`), `dikirim_pada` | penjaga idempotensi pengingat; index unik `contract_id + tahap + penerima_id`. Koleksi sendiri karena `PATCH /contract/:id` menimpa dokumen kontrak utuh lewat `ReplaceOne`, dan jejak kiriman bukan fakta kontrak |
| Salinan `work_data` (`employment_type`, `contract_ending`) | tidak ditulis modul tanda tangan. Modul kontrak menyegarkannya sendiri lewat `segarkanSalinan` | pintu tulis lain membuang kedua field itu |
| Prefix arsip MinIO (baru) | PDF final, goresan, lembar bukti | tanpa kunci baca di browser; tidak bisa diganti setelah dikunci |
| [[Microservices - Notification Service]] | pengingat (`reminder`), pemberitahuan antrean direktur, email salinan | |

## Belum Diputuskan (TBD)

- **Konfirmasi legal** keabsahan tanda tangan tidak tersertifikasi untuk PKWT. Rilis tanda tangan menunggu ini; pengingat tidak.
- **Hasil uji S1** (urutan A atau B): HR memeteraikan satu PDF contoh lewat portal distributor yang dipakai.
- **Format dan keunikan nomor kontrak**: format HR (`…/HRD/PKWT/…/…`) vs kode sekarang, urutan per perusahaan dan periode, dan perlakuan nomor kontrak lama (celah 1).
- **Letak data penandatangan per perusahaan** (nama, jabatan, alamat direktur).
- **Field tempat lahir** di `personal_data`, termasuk siapa yang mengisinya.
- **Lokasi kerja dan jam kerja** di template: tetap umum, atau diisi dari data per karyawan.
- **Sumber gaji Lampiran 1**: `employee_salary` (`basic_salary` + `component_values`) untuk perpanjangan dan `Offer` untuk karyawan baru, beserta pemetaan komponen payroll ke kolom kehadiran, tunjangan jabatan, dan uang makan.
- **Draf lewat email sebelum datang**: opsional; siapa yang memutuskan per kontrak.
- **Penolakan atau koreksi di tempat**: bentuk catatannya dan siapa yang memperbaiki.
- **Nama status** alur tanda tangan dan perlakuan kontrak lama (dianggap lampiran di luar sistem, tanpa status tanda tangan).
- **Retensi arsip** kontrak bertanda tangan.
- **Jenis kontrak yang memakai e-Meterai** (termasuk `Magang` atau tidak) dan jumlah meterai per kontrak.
- **Volume** kontrak per bulan untuk beban HRD dan direktur, dan jumlah kontrak kedaluwarsa pada karyawan aktif yang menentukan panjang ringkasan pengingat pertama: belum terukur; skrip baca-saja `.task-plans/cek-kontrak-esign-prod.ps1`.
- **Kewajiban PKWT di luar penandatanganan** yang belum dipetakan ke sistem dan **belum diverifikasi ke HR/legal**: pencatatan PKWT ke kementerian ketenagakerjaan, batas total durasi PKWT, dan uang kompensasi saat PKWT berakhir (PP 35/2021).
- **Kontrak bisnis** di service yang sama (`/legal/contracts`, `/procurement/contracts`): di luar lingkup.

## Dependensi & Integrasi

- [[Microservices - Employee Service]]: pemilik `employee_contract`, `personal_data`, `work_data`; rute kontrak di [[API - Employee Service]] §Kontrak Kerja; cron, helper inbox, penerima HR, rantai atasan.
- [[Microservices - Payroll Service]]: `employee_salary` untuk Lampiran 1.
- [[Microservices - Recruitment Service]]: term offer untuk karyawan baru.
- [[Microservices - File Service]]: prefix arsip baru.
- [[Microservices - Notification Service]]: inbox (`reminder`), email salinan dengan lampiran PDF.
- [[Microservices - Calendar Service]]: feed `contract_end` (kontrak milik pemanggil).
- [[CORE - HRIS Orchestrator]]: rantai hire (create-employee).
- [[CORE - API Master Gateway]]: routing + auth SSO.
- [[APP - Web ERP]] (`/hris/contract`, layar tanda tangan di perangkat HR, Ruang Direktur) dan [[APP - MyBharata]] ("Kontrak Saya").

## Dokumen Terkait

- [[ADR - 0089 Tanda Tangan Kontrak Kerja di Sistem Sendiri, Didampingi HRD, e-Meterai Dibubuhkan HR]] (keputusan) · [[ADR - 0019 Kontrak Kerja Elektronik via Service Internal + Lapisan Tersertifikasi]] (digantikan)
- [[HRIS - Personalia]] (administrasi kontrak/PKWT, induk) · [[HRIS - Recruitment]] (alur hire → onboarding/masa evaluasi) · [[HRIS - Compensation & Benefits]] (term komersial)
- [[REF - Kepemilikan Data]] · [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] (gerbang PIN)
- [[IT - Background Jobs & Schedulers]] (job pengingat)
- [[Microservices - HRD Document Service]] (pola acknowledgment; tidak dipakai)
- [[HRIS - Big Pictures]]

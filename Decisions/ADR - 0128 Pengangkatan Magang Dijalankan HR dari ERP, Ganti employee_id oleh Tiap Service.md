## Untuk Manajemen

**Apa yang berubah di layar.** Di halaman Kontrak, setelah HR menambahkan kontrak PKWT/PKWTT untuk karyawan magang, muncul tombol **"Angkat dan terbitkan ID reguler"**. HR menekannya kapan pun ia pilih; sistem menerbitkan ID reguler baru (contoh `BIP-0271-09-26`), memindahkan seluruh data orang itu ke ID baru di latar belakang, dan menampilkan status prosesnya sampai selesai. Tidak ada lagi permintaan ke tim IT.

**Siapa yang terdampak.** HR (mandiri, tanpa IT), karyawan yang diangkat (login ulang sekali di MyBharata dan mengaktifkan ulang PIN/biometrik; username tetap), dan Finance (menerima tugas di kotak masuk untuk mengganti nomor proyek Accurate bila orang itu punya proyek). **Yang TIDAK dijanjikan:** nomor proyek di Accurate tidak ikut diganti otomatis; foto dan berkas lama tetap di folder lamanya (tetap terbuka); pengangkatan tidak berjalan tanpa HR menekan tombol, karena login orangnya akan putus dan HR yang memilih waktunya. **Perkiraan besaran:** sekitar dua minggu kerja (fungsi bersama, satu pintu di tiap layanan, koordinator, tombol dan statusnya), lalu seluruh layanan dinaikkan ulang sekali.

## Deskripsi

*Pengangkatan magang ke PKWT/PKWTT dijalankan HR sendiri dari halaman Kontrak. employee-service mengoordinasi penggantian `employee_id`, dan SETIAP service mengganti rujukan di databasenya sendiri lewat satu fungsi bersama di `shared-library`, sehingga ADR 0002 (database-per-service) tetap utuh. Menggantikan [[ADR - 0126 employee_id Diterbitkan Sistem, Magang yang Diangkat Mendapat ID Reguler dengan Migrasi Riwayat]] §5 ("dijalankan manusia per angkatan lewat alat"); §4 (ID memang berganti) tetap berlaku.*

- **Status**: 🟡 **Diusulkan** 2026-09-26, disetujui pemilik produk lewat `/analisa-kebutuhan`. Kode belum ada. Papan kerja: [[ANALISA - Pengangkatan Magang dari ERP]]
- **Path di repo**: `bip-erp/shared-library/common/ganti_employee_id.go` (baru) · `bip-erp/services/*/main.go` (satu rute internal per service) · `bip-erp/services/employee/pengangkatan*.go` (baru, koordinator + status) · `bip-erp/services/employee/contract.go` (`segarkanSalinan`, penanda siap-diangkat) · `erp-frontend/src/features/hris/contract/` (tombol + status)
- **Tanggal**: 2026-09-26

## Context

ADR 0126 §5 memutuskan penggantian ID dijalankan manusia (tim IT) per angkatan lewat alat, dengan alasan fitur mandiri "menuntut endpoint ganti-ID di 16+ service beserta penanganan kegagalan sebagian". Pemilik produk menolak hasilnya 2026-09-26: HR tidak boleh bergantung pada IT untuk pengangkatan.

Dua jalan diukur ([[ANALISA - Pengangkatan Magang dari ERP]]):

1. **Nomor induk terpisah** (`employee_id` tak pernah berubah, ID tampilan jadi field sendiri). Grounding 2026-09-26 menunjukkan yang dilihat dan diketik manusia hari ini adalah `employee_id` itu sendiri: sekitar **70 berkas** erp-frontend menampilkannya tanpa satu komponen bersama (`formatId` bahkan tak dipakai di mana pun); slip gaji mencetaknya berlabel **"NIK"** dan memakainya di nama berkas (`services/payroll/payslip_pdf.go:151,222`); ekspor karyawan, form, Kaizen, insentif; teks pengingat kontrak; impor payroll run dan upah BPJS berkunci `employee_id` (`services/payroll/impor_run.go:60`, `bulk_bpjs_base.go:35`); pencarian `$regex` di sekitar 20 layar; onboarding akun; nomor proyek Accurate (`services/integration/internal/usecase/beban_marketing.go:49-55`); profil, Data Kerja, dan QR di MyBharata. Semuanya harus pindah, dan selama belum, satu orang tampil dengan dua nomor.
2. **Ganti ID di dalam sistem**. Logikanya sudah teruji tiga kali di PROD sebagai alat manusia (`.task-plans/migrasi-ganti-id.js`): target = setiap nilai PERSIS ID lama di koleksi mana pun, potongan teks hanya boleh di path berkas/teks notifikasi, idempoten. Yang ditolak ADR 0126 adalah menulis ke semua database dari satu tempat; bila tiap service mengganti databasenya sendiri, ongkosnya satu fungsi bersama + satu rute per service.

Fakta yang membuat jalan 2 layak, diukur di PROD 2026-09-26: **180 dari 181 akun aktif login dengan username sendiri**, jadi penggantian ID hampir tak menyentuh cara orang login; alokator nomor reguler atomik sudah live (#2079, #2086); `segarkanSalinan` (`services/employee/contract.go:211`) adalah satu-satunya penulis `employment_type` dan dilalui POST maupun PATCH kontrak (`contract.go:325,403`).

## Decision

### 1. Satu fungsi bersama, dijalankan tiap service atas databasenya sendiri

`shared-library` memuat satu fungsi penggantian ID: menerima pasangan (lama, baru), memindai seluruh koleksi database service pemanggil, mengganti setiap nilai PERSIS ID lama (termasuk elemen array bersarang satu tingkat), menolak bila ID lama muncul sebagai potongan teks di luar daftar-izin, dan mengembalikan ringkasan per koleksi. Logikanya diangkat dari alat yang sudah teruji, bukan ditulis ulang. Setiap service mendaftarkan satu rute internal yang memanggil fungsi itu atas databasenya sendiri. **Tak ada service yang menulis ke database service lain.**

### 2. employee-service mengoordinasi, dengan status yang disimpan

Pengangkatan adalah dokumen berstatus (`menunggu` → `berjalan` → `selesai`/`gagal`) per orang: ID lama, ID baru, status per service, waktu, pelaku. Koordinator:

1. memastikan setiap service terdaftar punya rute ganti-ID; **satu saja tak punya = tolak berjalan** (supaya service baru yang lupa mendaftar tidak meninggalkan data lama tanpa galat);
2. memesan ID reguler dari penghitung (§3 ADR 0126), bulan-tahun = **tanggal diangkat** (mulai kontrak PKWT/PKWTT);
3. memanggil tiap service, employee-service terakhir (identitas dan login pindah paling akhir);
4. menandai gagal per service dan boleh diulang; karena penggantian nilai persis bersifat idempoten, pengulangan hanya menyentuh sisa.

Pemetaan lama→baru disimpan permanen; pembalikan = menjalankan pemetaan terbalik (nilai persis, ID baru unik).

### 3. HR yang menekan, sistem yang mengerjakan

Tombol muncul di riwayat kontrak bila karyawan ber-ID magang memiliki kontrak PKWT/PKWTT. **Tidak otomatis saat kontrak disimpan**: login orangnya putus saat ID berganti, jadi HR memilih waktunya. Penyimpanan kontrak tidak ikut menunggu migrasi (proses di latar, layar menampilkan status).

### 4. Yang tetap di luar sistem

- **Accurate**: koordinator mengirim tugas ke kotak masuk Finance berisi nomor proyek lama dan baru bila orang itu punya proyek (dilihat dari data turunan Accurate). Penggantian nama proyek di Accurate tidak diotomatisasi sampai integrasinya diperiksa.
- **Berkas MinIO** tetap ber-path ID lama (dokumen menyimpan path lengkap).

### 5. Yang digantikan dan yang tetap

- Menggantikan ADR 0126 §5 (alat manusia per angkatan). Alat `.task-plans/jalankan-migrasi-ganti-id.ps1` tetap sah sampai fitur ini live dan untuk kasus di luar pengangkatan (perapian nomor).
- ADR 0126 §1-§4 dan §6 tetap berlaku. Nomor induk terpisah **tidak** dibangun.

## Consequences

- **Setiap service baru wajib mendaftarkan rute ganti-ID**, kalau tidak koordinator menolak semua pengangkatan. Ini disengaja: kegagalan keras lebih murah daripada rujukan lama yang tertinggal diam-diam.
- **Perubahan `shared-library` menaikkan semua service** yang mendaftarkan rute; deploy pertama menyentuh seluruh container.
- **Koleksi besar** (>50 ribu dokumen) dipindai lewat field ber-ID yang ditemukan dari sampel, seperti alat hari ini; field ber-ID yang jarang muncul bisa lolos dari sampel. Laporan per service wajib menyebut koleksi yang tak bisa dipindai.
- **Login orang yang diangkat putus sekali** (JWT memuat `employee_id`); username tetap.
- **Tanpa `mongodump` per pengangkatan.** Pengamannya pemetaan permanen + pembalikan nilai persis; ini lebih lemah daripada backup dan diterima sadar karena pengangkatan sering dan dijalankan non-IT.
- **Label "NIK" pada slip gaji** yang sebenarnya `employee_id` (`payslip_pdf.go:222`) tetap membingungkan dengan NIK KTP; dicatat, tidak diperbaiki di sini.

## Terkait

- [[ADR - 0126 employee_id Diterbitkan Sistem, Magang yang Diangkat Mendapat ID Reguler dengan Migrasi Riwayat]] (§5 digantikan) · [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]] · [[ADR - 0002 Database-per-Service]]
- [[HRIS - Personalia]] (cara kerja pengangkatan) · [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]]
- [[ANALISA - Pengangkatan Magang dari ERP]] (papan kerja)

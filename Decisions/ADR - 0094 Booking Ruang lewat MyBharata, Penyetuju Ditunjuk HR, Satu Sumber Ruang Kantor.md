## Untuk Manajemen

Peminjaman ruang rapat selama ini dicatat di spreadsheet tanpa kolom status dan tanpa cek bentrok. Desain lama di vault (dikunci 2026-07-18) menaruh persetujuan di tangan tim GA lewat web dan menutup tiap booking dengan checklist kebersihan. Keputusan pemilik proses (2026-09-12) mengubahnya: karyawan **mengajukan lewat MyBharata**, **HR menunjuk siapa yang menyetujui** (bukan GA otomatis, bukan atasan pemohon), penyetuju memutus lewat MyBharata, dan **Booking Ruang menjadi satu-satunya sumber ruang kantor** bagi Agenda Kalender, Interview, Onboarding review, Program Culture, dan Pelatihan.

**Terdampak**: seluruh karyawan (mengajukan), penyetuju yang ditunjuk HR (memutus), staf GA (mendaftarkan ruang, melihat jadwal), HR (menunjuk penyetuju). **Yang TIDAK dijanjikan**: peminjaman kendaraan dan barang (ditunda), checklist kebersihan (dihapus), persetujuan lewat web (semula tidak dibuat; dibalik [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]] pada 2026-09-14), durasi maksimum dan sanksi (belum ada aturan bisnisnya). **Besaran kerja**: besar, dipecah tujuh irisan; irisan 1 (inventory-service dan layar web) sudah ada di kode.

## Deskripsi

*Booking ruang rapat dibangun di inventory-service dengan satu tahap persetujuan oleh daftar penyetuju yang ditunjuk HR per perusahaan. Karyawan mengajukan dan penyetuju memutus lewat MyBharata; web dipakai GA untuk mengelola ruang dan melihat jadwal, dan dipakai HR untuk menunjuk penyetuju. Kelak Booking Ruang menjadi satu-satunya sumber "ruang kantor" bagi modul lain. ADR ini mencatat penyimpangan sadar dari desain rilis-1 di [[GA - Asset Loan & Room Booking]].*

- **Status**: ⚠️ **Diterima, sebagian terimplementasi** (keputusan 2026-09-12, disempurnakan hasil review 2026-09-14). Irisan 1 dari 7 ada di kode; irisan 2 sampai 7 belum. **§2, satu butir Consequences, dan satu butir "Yang sengaja tidak dilakukan" diamandemen [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]]** (2026-09-14): web kini juga mengajukan dan memutus booking.
- **Path di repo** (irisan 1):
  - `bip-erp/services/inventory/peminjaman_*.go`, `bip-erp/services/inventory/calendar_feed.go`
  - `bip-erp/shared-library/models/inventory/models.go` (koleksi), `bip-erp/shared-library/models/notification/models.go` (kategori inbox)
  - `bip-erp/services/calendar/providers.go` (provider `inventory`), `bip-erp/services/notification/webpush.go` (rute web)
  - `erp-frontend/src/app/(main)/ga/peminjaman/page.tsx`, `erp-frontend/src/features/ga/peminjaman/`
- **Tanggal**: 2026-09-14

## Context

- **Desain rilis-1 di [[GA - Asset Loan & Room Booking]]** (dikunci 2026-07-18, nol kode) menetapkan: self-service dengan **approval tim GA** di web, status `Selesai` yang mewajibkan **checklist kelengkapan dan kebersihan**, notifikasi memakai kategori `request-created/approved/rejected`, kontrak `/rooms` dan `/bookings/*` termasuk `GET /bookings/calendar`, serta id `RESV-YYYY-nnn`.
- **Pencarian 2026-09-12** atas `origin/main` bip-erp dan erp-frontend serta `origin/dev` MyBharata: nol fitur booking dan nol PR relevan. Yang ada dan dipakai sebagai pola: modul Permintaan Barang GA di inventory-service (transisi murni, update berpenjaga status, nomor unik lewat unique index, notifikasi best-effort), penunjukan penyetuju departemen di Pengaturan > Organisasi, dan aturan penunjukan penyetuju [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]] (divalidasi di server, gagal-tertutup saat simpan).
- **Aturan kalender terpusat** ([[Microservices - Calendar Service]]): fitur bertanggal wajib mendaftarkan feed, dilarang membuat kalender sendiri, dan feed hanya memuat data milik pembaca. `GET /bookings/calendar` versi konsep melanggar keduanya.
- **MongoDB inventory bukan replica set**, jadi tanpa transaksi multi-dokumen. Persetujuan bersamaan atas slot yang sama harus ditahan tanpa transaksi.
- **Kebutuhan pemilik proses** (2026-09-12): pintu masuk pemohon MyBharata (menu Pengajuan), alur seperti pengajuan HR tetapi tanpa langkah atasan, form menampilkan jam kosong ruang, booking berulang dan ubah jam ikut, dan ruang kantor di modul lain tak boleh lagi diketik bebas.

## Decision

### 1. Rumah kode inventory-service, kontrak `/peminjaman`

Tiga koleksi: `ga_ruang` (master ruang), `ga_peminjaman` (booking, field `jenis` bernilai `ruang` supaya kendaraan dan barang kelak tak butuh koleksi baru), dan `ga_peminjaman_penyetuju` (satu daftar per perusahaan). Rute berawalan `/peminjaman` (bukan `/bookings`), nomor `PJR-YYYYMMDD-nnn` (bukan `RESV-`). Kontrak lengkap di [[API - Inventory Service]].

### 2. Pemohon lewat MyBharata, web baca-saja untuk booking

> ⚠️ **Diamandemen** [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]] (2026-09-14): pengajuan, perubahan jadwal, pembatalan, dan persetujuan booking kini juga dilakukan di web, lewat kartu Booking Ruang di halaman Pengajuan dan tab Perlu Keputusan. Teks di bawah dipertahankan sebagai catatan keputusan asalnya.

Mengajukan cukup **identitas**, tanpa izin modul: seluruh karyawan boleh memesan ruang, sementara paket izin GA belum tentu terpasang di semua posisi. Layar pengajuan dan persetujuan di MyBharata (menu Pengajuan) adalah irisan 2. Web **tidak** menyetujui atau mengubah booking: halaman Ruang & Booking menampilkan booking sendiri, jadwal seluruh perusahaan (`ga.view`), dan master ruang (`ga.work` untuk tambah, ubah, nonaktifkan; ruang tak pernah dihapus). Detail booking di web memberi tahu pemohon dan penyetuju bahwa tindakannya dilakukan di MyBharata.

### 3. Penyetuju ditunjuk HR, satu daftar untuk semua ruang

Supervisor HRIS atau IT menunjuk penyetuju di Pengaturan > Organisasi & Jabatan. Daftarnya satu per perusahaan, berlaku untuk semua ruang, dan **bukan** atasan pemohon maupun izin GA. Penunjukan divalidasi ke daftar karyawan aktif employee-service saat disimpan; daftar karyawan yang tak terbaca menolak penunjukan (gagal-tertutup, pola ADR 0057). Daftar kosong membuat pengajuan ditolak, dan layar memberi tahu hal itu sebelum orang mengisi apa pun. Penyetuju **tak boleh memutus booking miliknya sendiri**. Penyetuju yang kemudian tak lagi aktif hanya **ditandai** di layar HR, tidak dibersihkan otomatis.

### 4. Status tanpa `Selesai` dan tanpa checklist

`DIAJUKAN → DISETUJUI | DITOLAK`, plus `DIBATALKAN`. Tolak wajib beralasan. Pemohon boleh membatalkan saat masih diajukan, atau sesudah disetujui selama belum mulai. Pemohon boleh mengubah sebelum mulai: perubahan **ruang atau jam** mengembalikan booking yang disetujui ke `DIAJUKAN`, melepas slot lamanya, dan mengabari penyetuju lagi; perubahan **isian** (nomor WA, keperluan, keterangan) tidak melepas persetujuan. Pemohon yang sudah pindah perusahaan ([[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]) tak bisa mengubah booking di perusahaan lamanya, tetapi tetap bisa membatalkannya.

### 5. Anti-bentrok tanpa transaksi

Hanya booking `DISETUJUI` yang menghalangi; rentang dibaca setengah-terbuka, jam dalam WIB, kelipatan 30 menit, satu hari, di dalam jam operasional ruang. Persetujuan berjalan: baca ulang ruang (sudah nonaktif atau jadwalnya di luar jam operasional yang berlaku sekarang: ditolak dengan pesan menyuruh menolak booking itu, sedangkan booking yang sudah disetujui dibiarkan) → kunci sewa per ruang 15 detik → cek bentrok → tulis berpenjaga status **dan jadwal** → cek ulang (bertumpuk: kembali `DIAJUKAN`; tak terbaca: kembali `DIAJUKAN` dan penyetuju diminta mengulang) → tolak otomatis pengajuan lain yang bertumpuk.

### 6. Notifikasi dua kategori, dikirim di latar

`peminjaman-ga-perlu-aksi` ke seluruh penyetuju kecuali pemohon, dan `peminjaman-ga-diperbarui` ke pemohon (disetujui, ditolak, ditolak otomatis), bukan `request-*` versi konsep, karena label dan tujuan ketuk di MyBharata dipilih dari kategori. Pengirimannya di latar: menunggu kabar ke setiap penerima sebelum membalas bisa melewati batas 30 detik gateway, dan respons 502 atas booking yang sudah tersimpan membuat klien mengirim ulang.

### 7. Kalender lewat feed milik pembaca

Booking masuk kalender terpusat lewat feed `inventory` berjenis `room_booking` yang **hanya** memuat booking milik pembaca dan melewati booking yang lahir dari modul lain. Jadwal seluruh perusahaan tidak masuk kalender siapa pun; tempatnya halaman Ruang & Booking (`ga.view`).

### 8. Satu sumber ruang kantor (direncanakan)

Irisan 4 sampai 7: Agenda Kalender, Interview dan Onboarding review, Program Culture, dan Pelatihan memilih ruang kantor dari Booking Ruang. Teks bebas hanya untuk lokasi luar kantor dan ditolak bila sama dengan nama ruang terdaftar. Booking yang lahir dari modul tetap butuh persetujuan.

### 9. Booking berulang (direncanakan)

Irisan 3: pola harian atau mingguan, maksimal 3 bulan, satu persetujuan untuk satu seri.

## Consequences

### Yang membaik

- Bentrok ruang ditahan sistem, termasuk dua persetujuan bersamaan, tanpa bergantung transaksi Mongo.
- GA tak lagi mengetik form atas nama orang lain; penyetuju bisa diganti HR tanpa perubahan kode.
- Ruang kantor kelak punya satu sumber, jadi agenda dan jadwal pelatihan tak lagi menunjuk ruang yang sama pada jam yang sama tanpa ada yang tahu.

### Yang memburuk atau diterima sadar

- **`ga.view` kini membuka jadwal seluruh booking beserta nama dan nomor WA pemohon.** Description paket "GA: Lihat" dan "GA: Pelaksana" diperbarui di kode, tetapi seed tidak menimpa dokumen yang sudah ada, jadi DB lama butuh backfill terpisah. Lihat [[CORE - RBAC dan Permission Set]].
- **Sampai irisan 2 terbit, pengajuan dan persetujuan hanya bisa lewat API.** Web sengaja tak punya tombol aksi. *Diamandemen [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]]: sejak irisan 1b web punya aksi booking.*
- **Penyetuju basi tidak dibersihkan.** Penyetuju yang resign atau pindah tenant tetap tercatat sampai HR melepasnya; layar HR hanya menandainya.
- **Dua perubahan isian yang bersamaan saling timpa** (yang terakhir menang). Diterima karena hanya pemohon sendiri yang bisa mengubah bookingnya.
- **Alasan riwayat buatan server masih teks bahasa Indonesia** yang tampil apa adanya di locale en; dibuat terstruktur bersama layar MyBharata (irisan 2).
- **Saringan jenis agenda yang tersimpan di kalender web** bisa menyembunyikan `room_booking` bagi orang yang pernah menyimpan pilihan; ditangani sebagai task terpisah di kode kalender bersama.
- **Deploy lintas container.** inventory-service, notification-service (kategori inbox baru), dan calendar-service (provider baru) naik bersama; inventory-service butuh env `EMPLOYEE_MODULE_URL`, `NOTIFICATION_MODULE_URL`, `NOTIFICATION_SERVICE_KEY`, calendar-service butuh `INVENTORY_MODULE_URL`. Lihat [[RUN - Deploy Microservices bip-erp]].
- Temuan sampingan yang diperbaiki di kerja yang sama: notifikasi SPV Permintaan Barang GA tak pernah terkirim karena dua cacat berlapis. Klien resolver atasan memakai nama header gateway yang salah dan tak meneruskan identitas pemanggil. Lebih mendasar lagi, kiriman inbox inventory (`kirimInbox`, dipakai Permintaan Barang dan Booking Ruang) tak pernah membawa `BIP-Gateway-ID`, sehingga ditolak 401 oleh notification-service. Cacat kedua baru ketahuan saat verifikasi lewat gateway dev 2026-09-14, karena seluruh test mengganti pengirimnya dengan tiruan.

### Yang sengaja tidak dilakukan

- Persetujuan dan perubahan booking lewat web. *Diamandemen [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]]: kini dibuat.*
- Checklist kebersihan dan status `Selesai`.
- Badge sidebar dan kartu Office Boy.
- Durasi maksimum, kapasitas wajib, dan sanksi: aturan bisnisnya belum ada, jadi tidak dikarang.
- Lokasi aset GA dan ruangan inspeksi Quality: faktanya berbeda dari jadwal pemakaian ruang.
- Kendaraan dan barang: ditunda (sopir, odometer, dan irisannya dengan Perjalanan Dinas; durasi dan sanksi yang menyentuh Peraturan Perusahaan).

## Dokumen Terkait

- [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]]: amandemen §2 (aksi booking lewat web)
- [[GA - Asset Loan & Room Booking]]: konsep domain yang desain rilis-1-nya direvisi ADR ini
- [[Microservices - Inventory Service]] · [[API - Inventory Service]]: rumah kode dan kontrak
- [[Microservices - Calendar Service]] · [[Microservices - Notification Service]]: feed dan kabar
- [[APP - Web ERP]] · [[APP - MyBharata]]: permukaan pengguna
- [[REF - Kepemilikan Data]] · [[REF - Alur Persetujuan]]
- [[ADR - 0057 Penyetuju Pengajuan Pembelian Ditetapkan per Tahap]]: pola validasi penunjukan
- [[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]: pemohon yang pindah tenant

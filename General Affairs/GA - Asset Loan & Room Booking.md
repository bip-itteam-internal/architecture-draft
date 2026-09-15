## Deskripsi

*Konsep dan desain (sisi General Affairs) **peminjaman aset**: alur pinjam, pakai, kembali untuk **ruang rapat**, **barang/aset bergerak**, dan **kendaraan operasional**, supaya pemakaian bersama terjadwal (tak bentrok), terlacak (siapa memakai apa, kapan), dan akuntabel. Master aset ada di [[GA - Inventory Management]]; dok ini menambahkan alur peminjamannya. Keputusan desain yang berlaku untuk booking ruang dicatat di [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]] (merevisi desain rilis-1 versi 2026-07-18), yang diamandemen [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]].*

- **Status**: ⚠️ Implemented (ada catatan). **Booking ruang**: irisan 1 dari 7 ada di kode (inventory-service, feed kalender, notifikasi, layar web Ruang & Booking, penunjukan penyetuju). **Irisan 1b** (mengajukan, mengubah jadwal, membatalkan, menyetujui, dan menolak lewat web, plus kartu Booking Ruang di halaman Pengajuan) terimplementasi di branch, **belum merge** per 2026-09-14. **Irisan 2** (MyBharata: kartu Booking Ruang di menu Pengajuan, form dan detail booking, booking di daftar pengajuan terpadu, notifikasi berlabel; riwayat terstruktur dua bahasa di web dan MyBharata) terimplementasi di branch, **belum merge** per 2026-09-15. Booking berulang (irisan 3) dan pemilih ruang di modul lain (irisan 4 sampai 7) belum ada. **Barang dan kendaraan**: masih konsep, ditunda.
- **Rumah kode**: [[Microservices - Inventory Service]] (koleksi `ga_ruang`, `ga_peminjaman`, `ga_peminjaman_penyetuju`, lihat [[DB - Data Dictionary]]). Kontrak endpoint: [[API - Inventory Service]].
- **Sumber bisnis**: 2 sheet *"Form Peminjaman Ruangan"* + *"Syarat Dan Ketentuan Peminjaman Ruangan"* (PT Bharata Internasional Pharmaceutical).

## Latar Belakang

- Peminjaman ruang, barang, dan kendaraan berjalan manual lewat spreadsheet: rawan **bentrok jadwal**, sulit tahu **siapa memakai apa**, dan spreadsheet **tak punya kolom status** sehingga cek bentrok dilakukan manual.
- Pada proses lama **hanya Team GA yang mengisi form**. Desain yang berlaku menggeser ini ke **self-service** (lewat web sejak irisan 1b, lewat MyBharata di irisan 2) dengan **penyetuju yang ditunjuk HR** (bukan GA otomatis, bukan atasan pemohon).
- [[GA - Inventory Management]] menyimpan master aset, tetapi belum ada alur pinjam-kembali terstruktur. Konsep ini melengkapi sisi itu.

## Ruang Lingkup / Cakupan (business view)

- **Booking ruang rapat**: jadwal pemakaian anti-bentrok, jam operasional per ruang, kapasitas dan fasilitas sebagai informasi. Dibangun bertahap: (1) inti inventory-service + layar web; (1b) mengajukan dan memutus lewat web; (2) MyBharata untuk mengajukan dan memutus; (3) booking berulang harian/mingguan maksimal 3 bulan, satu persetujuan per seri; (4) pemilih ruang + Agenda Kalender; (5) Interview + Onboarding review; (6) Program Culture; (7) Pelatihan.
- **Satu sumber ruang kantor** (direncanakan, irisan 4 sampai 7): Agenda Kalender, Interview, Onboarding review, Program Culture, dan Pelatihan memilih ruang kantor dari Booking Ruang. Teks bebas hanya untuk lokasi luar kantor dan ditolak bila sama dengan nama ruang terdaftar. Booking yang lahir dari modul tetap butuh persetujuan.
- **Pinjam barang/aset bergerak**: ditunda. Durasi dan sanksi masih TBD, dan sanksi menyentuh Peraturan Perusahaan.
- **Booking kendaraan operasional**: ditunda. Sopir, odometer, dan irisannya dengan Perjalanan Dinas masih TBD. Pemeliharaan kendaraan di luar lingkup, lihat [[GA - Machine & Utility Maintenance]].
- **Tidak dikerjakan** (keputusan 2026-09-12): checklist kebersihan saat selesai, badge sidebar dan kartu Office Boy. Persetujuan dan perubahan booking lewat web semula termasuk di sini, lalu dibalik [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]] (2026-09-14).

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| **Pemohon** | Karyawan lintas divisi | Cukup identitas (tanpa izin modul) | [[APP - Web ERP]]: kartu Booking Ruang di halaman Pengajuan dan tab Booking Saya (ajukan, ubah jadwal, batal; irisan 1b). [[APP - MyBharata]]: kartu Booking Ruang di menu Pengajuan, Aktivitas Saya, dan Riwayat (irisan 2, branch) |
| **Penyetuju** | Karyawan yang ditunjuk HR, satu daftar per perusahaan (bukan atasan pemohon) | Penunjukan di daftar penyetuju, bukan izin; tak boleh memutus booking miliknya sendiri | [[APP - Web ERP]]: tab Perlu Keputusan dan detail booking (irisan 1b). [[APP - MyBharata]]: chip Booking di antrean Review Submission dan detail booking (irisan 2, branch) |
| **Team GA** | Staf / supervisor GA | `ga.view` (jadwal seluruh booking, termasuk nama dan nomor WA pemohon), `ga.work` (tambah, ubah, nonaktifkan ruang) | [[APP - Web ERP]] (Ruang & Booking) |
| **HR** | Supervisor HRIS atau IT | Gerbang `RequireHRISOrITSupervisor` | [[APP - Web ERP]] (Pengaturan > Organisasi & Jabatan) |
| **Penanggung jawab** | Kontak yang nomor WA-nya dicatat di booking (umumnya pemohon sendiri) | Referensi kontak, wajib diisi | |

- **Pemohon**: *Tujuan*: memesan ruang tanpa menghubungi GA. *Pain point*: tak tahu ruang mana yang kosong. *Aksi utama*: ajukan, ubah jam, batalkan, pantau status.
- **Penyetuju**: *Tujuan*: memutus cepat tanpa bentrok. *Pain point*: dua pengajuan untuk slot yang sama. *Aksi utama*: setujui atau tolak dengan alasan.
- **Team GA**: *Tujuan*: daftar ruang yang benar dan tahu pemakaian ruang. *Pain point*: ruang dipakai tanpa tercatat. *Aksi utama*: kelola ruang, lihat jadwal.
- **HR**: *Tujuan*: selalu ada penyetuju aktif. *Pain point*: penyetuju resign sehingga antrean menggantung. *Aksi utama*: tunjuk dan ganti penyetuju.

## Keputusan Desain

Desain rilis-1 versi 2026-07-18 (approval tim GA, status `Selesai` dengan checklist kebersihan, kategori notifikasi `request-*`, kontrak `/rooms` dan `/bookings/*` termasuk `GET /bookings/calendar`, id `RESV-`) **digantikan** oleh [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]], yang diamandemen [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]]. Ringkasnya:

1. **Scope yang dibangun = ruang.** Barang dan kendaraan ditunda.
2. **Pemohon dan penyetuju bekerja lewat web** (irisan 1b) **dan MyBharata** (irisan 2); **penyetuju ditunjuk HR**, satu daftar untuk semua ruang dalam satu perusahaan.
3. **Notifikasi lewat inbox/push MyBharata** dengan dua kategori khusus: `peminjaman-ga-perlu-aksi` (penyetuju) dan `peminjaman-ga-diperbarui` (pemohon), lewat [[Microservices - Notification Service]].
4. **Rumah kode = [[Microservices - Inventory Service]]**, bukan service baru.
5. **Kalender lewat feed milik pembaca** ([[Microservices - Calendar Service]], kind `room_booking`), bukan kalender GA sendiri.

### Status Booking

`DIAJUKAN → DISETUJUI | DITOLAK`, plus `DIBATALKAN`.

- **DIAJUKAN**: dibuat pemohon, atau booking disetujui yang diubah ruang/jamnya.
- **DISETUJUI / DITOLAK**: keputusan penyetuju; tolak wajib beralasan. Pengajuan lain yang bertumpuk dengan booking yang baru disetujui **ditolak otomatis**.
- **DIBATALKAN**: oleh pemohon, selagi masih diajukan atau sesudah disetujui selama belum mulai.
- "Berlangsung" dan "Selesai" **bukan status tersimpan**; keduanya dibaca dari jam. Checklist kebersihan tidak ada.

### Aturan Anti-Bentrok

Booking bentrok bila ada booking lain di **ruang yang sama** berstatus `DISETUJUI` dengan rentang yang overlap: `mulaiBaru < selesaiLama && mulaiLama < selesaiBaru` (bersinggungan tepat di batas tidak bentrok). Banyak pengajuan boleh antre di slot yang sama; yang menentukan adalah persetujuan. Jam dibaca WIB, kelipatan 30 menit, mulai dan selesai di hari yang sama, di dalam jam operasional ruang. Karena inventory-mongo bukan replica set (tanpa transaksi), persetujuan ditahan dengan kunci sewa per ruang, penulisan berpenjaga status dan jadwal, dan cek ulang sesudah menulis. Rinciannya di ADR 0094 §5.

## Alur Proses

1. **Tunjuk penyetuju** (HR, web): supervisor HRIS/IT memilih karyawan aktif. Selama daftar kosong, pengajuan ditolak dan layar menyampaikannya lebih dulu.
2. **Daftarkan ruang** (GA, web): nama, lokasi, kapasitas, fasilitas, jam buka dan tutup. Ruang tak pernah dihapus, hanya dinonaktifkan.
3. **Ajukan** (pemohon; web lewat kartu Booking Ruang di halaman Pengajuan sejak irisan 1b, MyBharata lewat kartu Booking Ruang di grid Pengajuan sejak irisan 2): pilih ruang dan jam kosong, isi keperluan (wajib), nomor WA (wajib, 8 sampai 15 angka), keterangan → `DIAJUKAN`; penyetuju dikabari.
4. **Putuskan** (penyetuju; web lewat tab Perlu Keputusan sejak irisan 1b, MyBharata lewat chip Booking di Review Submission sejak irisan 2): setujui (ruang dibaca ulang; ruang yang sudah nonaktif atau jam di luar jam operasional yang berlaku ditolak dengan pesan menyuruh menolak booking itu) atau tolak dengan alasan; pemohon dikabari.
5. **Ubah atau batal** (pemohon, sebelum mulai): perubahan ruang atau jam mengembalikan booking disetujui ke antrean dan melepas slot lamanya; perubahan isian saja tidak. Pemohon yang sudah pindah perusahaan hanya bisa membatalkan.
6. **Pakai**: sesuai jam; wajib menjaga kebersihan dan tidak merusak fasilitas (Syarat & Ketentuan).
7. **Eskalasi**: bila ada kerusakan, ke [[GA - Machine & Utility Maintenance]] / [[GA - Building Maintenance]].

## Kontrak dan Data

Kontrak endpoint (`/peminjaman/*` di inventory-service) didokumentasikan di [[API - Inventory Service]]; skema koleksi di [[DB - Data Dictionary]]. Nomor booking `PJR-YYYYMMDD-nnn`.

## Konsumen Data

- [[APP - Web ERP]]: halaman Ruang & Booking (booking sendiri, antrean penyetuju, jadwal, ruang) beserta aksi mengajukan, mengubah jadwal, membatalkan, menyetujui, dan menolak (irisan 1b); kartu Booking Ruang di halaman Pengajuan; tab penunjukan penyetuju di Pengaturan.
- [[API - Employee Service]]: `GET /pengajuan/ringkasan` membaca antrean penyetuju (`GET /peminjaman/perlu-aksi`) sebagai angka kartu Booking Ruang.
- [[APP - MyBharata]]: pintu masuk pemohon dan penyetuju (irisan 2): kartu Booking Ruang di menu Pengajuan, form dan detail booking, booking di daftar pengajuan terpadu.
- [[API - Attendance Service]]: daftar pengajuan terpadu memuat booking milik pemanggil dan antrean penyetuju bila klien meminta `include=booking`, dibaca dari inventory tanpa salinan (irisan 2).
- [[Microservices - Calendar Service]]: feed `inventory` / kind `room_booking`, hanya booking milik pembaca.
- [[Microservices - Notification Service]]: kabar perlu-aksi dan diperbarui.
- Agenda Kalender, Interview, Onboarding review, Program Culture, Pelatihan: pemilih ruang kantor (direncanakan irisan 4 sampai 7).
- [[GA - Inventory Management]]: status aset yang dipinjam (relevan saat fase barang).
- [[GA - Machine & Utility Maintenance]] · [[GA - Building Maintenance]]: eskalasi kerusakan.

## Kendala

- Aksi booking lewat web (irisan 1b) serta layar MyBharata, daftar terpadu, dan riwayat terstruktur (irisan 2) belum merge per 2026-09-15; sebelum terbit, pengajuan dan persetujuan hanya terjangkau lewat API.
- Pengajuan yang jam selesainya sudah lewat tetap `DIAJUKAN` (tak ada kedaluwarsa otomatis). Web tak menawarkan Tolak untuknya, sama dengan antrean server yang menyaringnya; pemohonnya masih bisa membatalkan.
- Penyetuju yang resign atau pindah tenant tetap tercatat sampai HR melepasnya; layar HR hanya menandainya.
- Push FCM butuh device MyBharata terdaftar; bila tak ada, inbox tetap tampil (notifikasi best-effort, gagal kirim tidak menggagalkan booking).
- Master aset untuk fase barang masih perlu dirapikan (lihat [[GA - Inventory Management]]); booking ruang tidak bergantung padanya.

## Belum Diputuskan (TBD)

- **Barang/aset**: kategori yang boleh dipinjam, kondisi pinjam vs kembali, durasi maksimum dan sanksi telat (menyentuh Peraturan Perusahaan).
- **Kendaraan**: dengan sopir atau dikemudikan sendiri, BBM/odometer, irisan dengan Perjalanan Dinas, penyetuju.
- **Durasi maksimum dan kapasitas wajib** untuk ruang: belum ada aturan bisnisnya.
- **Integrasi kalender eksternal** (mis. Google Calendar).
- Catatan: menu **"Loan"** di [[APP - MyBharata]] **bukan** peminjaman aset di dok ini (kemungkinan pinjaman karyawan/kasbon, sisi HR; perlu konfirmasi).

## Dokumen Terkait

- [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]]: keputusan desain yang berlaku
- [[ADR - 0095 Pengajuan dan Persetujuan Booking Ruang Juga Lewat Web]]: amandemen, aksi booking lewat web
- [[GA - Inventory Management]]: master aset
- [[Microservices - Inventory Service]] · [[API - Inventory Service]] · [[DB - Data Dictionary]]
- [[API - Employee Service]]: ringkasan pengajuan
- [[Microservices - Calendar Service]] · [[Microservices - Notification Service]]
- [[REF - Kepemilikan Data]] · [[REF - Alur Persetujuan]]
- [[GA - Machine & Utility Maintenance]] · [[GA - Building Maintenance]]
- [[APP - MyBharata]] · [[APP - Web ERP]]
- [[GA - Big Pictures]]

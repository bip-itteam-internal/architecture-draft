## Untuk Manajemen

ADR 0094 menaruh pengajuan dan persetujuan booking ruang di MyBharata, sementara layar MyBharata-nya belum ada. Pemilik proses (2026-09-14) memutuskan booking juga bisa diajukan dan diputus **lewat web**: karyawan membuka kartu **Booking Ruang** di halaman Pengajuan Portal Saya, memilih ruang, tanggal, dan jam kosong, lalu mengirim; penyetuju yang ditunjuk HR menyetujui atau menolak di tab **Perlu Keputusan**. MyBharata tetap dikerjakan sesudahnya.

**Terdampak**: seluruh karyawan (kartu baru di halaman Pengajuan, yang kini tampil untuk semua staf), penyetuju booking (tab dan angka antrean baru). **Yang TIDAK dijanjikan**: daftar gabungan izin dan booking di web, booking berulang, alasan riwayat dua bahasa. **Besaran kerja**: sedang; tanpa perubahan backend booking, ditambah satu baris sumber di employee-service.

## Deskripsi

*Amandemen [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]]: web tidak lagi baca-saja untuk booking. Pemohon mengajukan, mengubah jadwal, dan membatalkan; penyetuju yang ditunjuk HR menyetujui dan menolak; semuanya memakai kontrak `/peminjaman*` inventory-service apa adanya. Keputusan lain ADR 0094 (penyetuju ditunjuk HR, status, anti-bentrok, notifikasi, kalender, satu sumber ruang kantor) tetap berlaku.*

- **Status**: ⚠️ **Diterima, terimplementasi di branch, belum merge** (dicatat 2026-09-14, ukur ulang sebelum dipakai): erp-frontend `feat/ga-peminjaman-aksi-web`, bip-erp `feat/employee-ringkasan-booking-ruang`.
- **Path di repo**:
  - `erp-frontend/src/features/ga/peminjaman/` (`lib/slot.ts`, `lib/pengajuan-form.ts`, `lib/status.ts`, `hooks/use-peminjaman.ts`, `components/slot-grid.tsx`, `components/peminjaman-form-dialog.tsx`, `components/aksi-pemohon.tsx`, `components/aksi-penyetuju.tsx`, `components/peminjaman-detail-sheet.tsx`)
  - `erp-frontend/src/app/(main)/ga/peminjaman/page.tsx`
  - `erp-frontend/src/components/layout/portal-menu.ts`, `pengajuan-menu.ts`, `sidebar-menus.tsx`
  - `bip-erp/services/employee/ringkasan_pengajuan.go` (sumber `booking`)
- **Tanggal**: 2026-09-14

## Context

- ADR 0094 §2 menetapkan web baca-saja untuk booking dan menjadwalkan layar pengajuan dan persetujuan di MyBharata (irisan 2). Per 2026-09-14 layar MyBharata itu belum ada, sehingga detail booking di web menunjuk layar yang belum tersedia dan pengajuan hanya terjangkau lewat API (dicatat di [[APP - Web ERP]]).
- Pengajuan untuk seluruh karyawan di web berpusat di halaman `/portal/pengajuan`: kartu per jenis pengajuan, dengan angka antrean dari `GET /api/employee/pengajuan/ringkasan` ([[API - Employee Service]]).
- Backend Booking Ruang sudah menyediakan seluruh aksi yang dibutuhkan: `POST /peminjaman`, `PATCH /peminjaman/:nomor`, `POST /peminjaman/:nomor/batal`, `POST /peminjaman/:nomor/setujui`, `POST /peminjaman/:nomor/tolak`, `GET /peminjaman/slot`, `GET /peminjaman/perlu-aksi`, dan `GET /peminjaman/penyetuju/saya`. Kontraknya di [[API - Inventory Service]].

## Decision

### 1. Pemohon mengajukan, mengubah jadwal, dan membatalkan di web

Tab **Booking Saya** di `/ga/peminjaman` punya aksi utama **Ajukan Booking**: ruang, tanggal, grid slot 30 menit (klik jam mulai lalu jam terakhir yang dipakai; slot terpakai dan yang sudah lewat tak bisa dipilih, dan keadaannya ditulis, bukan cuma diwarnai), keperluan, nomor WhatsApp, keterangan. String waktu slot dari server dikirim apa adanya. Booking yang tersimpan langsung dibuka detailnya.

Detail booking memberi pemohon **Ubah Jadwal** (hanya field yang berubah yang dikirim; booking disetujui yang ruang atau jamnya berubah dikonfirmasi dulu karena melepas slotnya) dan **Batalkan** (dikonfirmasi dengan menyebut ruang dan jadwal). Ubah disembunyikan bagi booking dari perusahaan lama pemohon, Batalkan tetap, cermin 403 `TentukanUbah`.

### 2. Penyetuju memutus di web

Tab **Perlu Keputusan** hanya tampil bila `GET /peminjaman/penyetuju/saya` menjawab `true`, dan isinya `GET /peminjaman/perlu-aksi`. Detail booking memberi penyetuju **Setujui** (dikonfirmasi dengan menyebut pemohon, ruang, dan jadwal) dan **Tolak** (alasan diminta sebelum dikirim). Penolakan server (409, 403, 503) tampil di tempat aksinya dan **tetap terlihat walau data yang dimuat ulang mencabut hak tombolnya**, misalnya booking keburu diputus orang lain atau penunjukannya dicabut. Tolak tetap tersedia selama booking masih menunggu.

### 3. Pintu masuk dari halaman Pengajuan

Menu Portal Saya **Booking Ruang** (tanpa izin) menuju `/ga/peminjaman?tab=saya` dan tampil sebagai kartu di `/portal/pengajuan` untuk semua karyawan. Angka kartunya adalah antrean penyetuju, dari sumber kelima `booking` di `GET /pengajuan/ringkasan` employee-service; bukan penyetuju ditolak sumbernya, jadi kartunya tanpa angka. Penyetuju yang antreannya berisi melihat tautan dari Booking Saya ke Perlu Keputusan.

### 4. MyBharata tetap berikutnya

Irisan 2 tetap membangun layar MyBharata. Daftar pemohon dan antrean peninjau di sana direncanakan lewat daftar pengajuan terpadu attendance-service (booking ikut lewat parameter opt-in), sedangkan detail dan aksi booking tetap memanggil inventory-service. Rinciannya diputuskan di rencana irisan 2. *Terimplementasi di branch, belum merge per 2026-09-15: attendance-service memuat booking hanya bila klien mengirim `include=booking` (antrean `as=reviewer` dan daftar milik sendiri; tab sudah diputus dan mode admin tanpa booking), dengan `degraded` saat inventory tak terbaca; MyBharata membuka detail dan aksi booking langsung ke inventory-service. Lihat [[API - Attendance Service]] dan [[APP - MyBharata]].*

## Consequences

### Yang membaik

- Pemohon dan penyetuju bisa bekerja tanpa menunggu rilis MyBharata, dan detail booking tak lagi menunjuk layar yang belum ada.
- Penyetuju melihat angka antrean bookingnya di halaman Pengajuan bersama antrean lain.

### Yang memburuk atau diterima sadar

- **Aturan tombol per peran dicerminkan di frontend** (`lib/status.ts`: `bolehUbahOleh`, `bolehBatalOleh`, `bolehDiputusOleh`). Server tetap penentu; salinan itu hanya memilih tombol yang tampil, dan penolakan server ditampilkan apa adanya.
- **Booking menunggu yang jam selesainya sudah lewat tak mendapat tombol Tolak**, walau `TentukanTolak` di server tak memeriksa jam. Antrean `perlu-aksi` juga menyaringnya, jadi keduanya konsisten (keputusan user 2026-09-14). Pengajuan kedaluwarsa tetap `DIAJUKAN` sampai pemohonnya membatalkan.
- **Normalisasi nomor WhatsApp tidak disalin ke web**: nomor yang sama dengan format berbeda terkirim sebagai perubahan dan dibalas 400 "tidak ada yang diubah".
- **Tab Perlu Keputusan tanpa penanda daftar terpotong**, karena `perlu-aksi` tidak mengirim `batas` maupun `terpotong`.
- **Halaman Pengajuan kini tampil untuk semua staf**, dengan minimal satu kartu (Booking Ruang). Bagi staf yang cuma berhak satu kartu, halaman itu menambah satu klik.
- **Deploy**: employee-service (tanpa env baru; `INVENTORY_MODULE_URL` sudah ada di blok compose-nya), lalu erp-frontend. Prasyaratnya backend Booking Ruang irisan 1 sudah naik.

### Yang sengaja tidak dilakukan

- Daftar gabungan izin dan booking di web: web belum punya daftar izin untuk karyawan.
- Alasan riwayat terstruktur dua bahasa: dikerjakan irisan 2 untuk kedua klien (web: commit tambahan di erp-frontend `feat/ga-peminjaman-aksi-web`; MyBharata: branch `feat/booking-ruang`; keduanya belum merge per 2026-09-15).
- Mengangkat grid slot ke komponen bersama: ini pemakai pertama.

## Dokumen Terkait

- [[ADR - 0094 Booking Ruang lewat MyBharata, Penyetuju Ditunjuk HR, Satu Sumber Ruang Kantor]]: keputusan yang diamandemen
- [[GA - Asset Loan & Room Booking]] · [[APP - Web ERP]] · [[APP - MyBharata]]
- [[API - Inventory Service]] · [[API - Employee Service]] · [[Microservices - Inventory Service]]
- [[REF - Alur Persetujuan]]

## Deskripsi

*Penanganan kedisiplinan karyawan & **Surat Peringatan (SP1/SP2/SP3)** — penerbitan oleh HR, masa berlaku 6 bulan, riwayat per karyawan, dan usulan otomatis SP1 dari akumulasi keterlambatan.*

- **Status**: ⚠️ Implemented (ada catatan) — irisan 1 **selesai di kode dan terverifikasi lokal** (BE `feat/employee-surat-peringatan`, FE `feat/hris-surat-peringatan`), tapi **belum di-push/PR, belum merged, belum deploy**. Dampak payroll, skorsing, dan PHK **sengaja di luar irisan ini**; pemicu SP2/SP3 **belum terdefinisi di peraturan** (lihat *Belum Diputuskan*).

## Sumber Aturan

Aturannya **tidak ada di vault ini**. Sumber kebenarannya **Peraturan Perusahaan PT Bharata Internasional Pharmaceutical 2026-2028**, dengan turunan teknis di `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` (CLAUDE.md MyBharata menetapkan dok itu **menang atas kode** bila bertentangan). PDF aslinya dibundel ke aplikasi di `mybharata-app/assets/docs/company_policy.pdf`.

| Pasal | Isi yang dipakai |
|---|---|
| 19 & 20 | **Terlambat 3x per bulan memicu SP1.** Terlambat 5x per bulan tanpa keterangan dan mangkir 6 hari berturut-turut dikualifikasikan **mengundurkan diri** (jalur [[HRIS - Personalia]], bukan jalur SP) |
| 55 | **SP2**: potong **25% gaji pokok**, aktif **6 bulan sejak tanggal terbit**, menghambat kenaikan upah dan promosi |
| 56 | **SP3**: perusahaan berhak PHK sepihak, dengan opsi masa perbaikan 1 bulan diawasi Atasan dan HRD |
| 53 ayat 2-3 | **Skorsing**: maksimal 3 bulan, akses dicabut otomatis, upah tetap dibayar |

## Sudah Diimplementasikan

- **Penerbitan SP1/SP2/SP3 oleh HR** dengan kategori pelanggaran (Keterlambatan · Mangkir · Pelanggaran Tata Tertib · Pelanggaran Informasi Rahasia · Penyalahgunaan Wewenang · Lainnya) dan **alasan wajib untuk semua kategori tanpa kecuali** — SP bisa berujung PHK, jadi kategori saja tak pernah cukup sebagai dasar tertulis.
- **Masa berlaku 6 bulan**, disimpan per catatan sebagai `expires_at`. Harinya **dijepit ke hari terakhir bulan tujuan**: tanpa itu `time.AddDate` menormalkan 31 Februari jadi 3 Maret dan SP akhir bulan berlaku lebih lama daripada yang tertulis di suratnya.
- **Usulan SP1** dari akumulasi telat, dipanggil ke [[Microservices - Attendance Service]] lewat `GET /internal/late-recap`. Hitungannya **tidak disalin** ke employee-service.
- **Pencabutan** dengan alasan wajib, bersifat final.
- **Lampiran salinan surat bertanda tangan** (PDF/gambar/Word, cap 4 MB milik [[Microservices - File Service]]).
- **Notifikasi ke karyawan** saat SP terbit dan saat dicabut, lewat [[Microservices - Notification Service]].
- **Halaman `/hris/surat-peringatan`** di [[APP - Web ERP]], dwibahasa id/en.

Implementasi: [[Microservices - Employee Service]] · endpoint: [[API - Employee Service]] & [[API - Attendance Service]].

## Keputusan & Konsekuensinya

- **HR menerbitkan MANUAL, sistem hanya mengusulkan** — meski peraturan menulis telat 3x "otomatis memicu" SP1. Penyimpangan ini **disengaja**: tarik log mesin fingerprint masih manual ([[HRIS - Attendance System]]), jadi angka telat sebuah periode belum tentu lengkap saat dibaca. Surat sanksi yang terbit sendiri dari data belum lengkap lebih mahal daripada surat yang terbit terlambat.
- **"Per bulan" = periode payroll 26 sampai 25**, bukan bulan kalender, mengikuti hitungan yang sudah dipakai `GET /history?late=true` dan sudah dilihat karyawan di [[APP - MyBharata]]. Dua definisi berbeda akan melahirkan dua angka "telat bulan ini" di satu sistem, dan yang kena SP akan membandingkannya.
- **Status SP tidak disimpan, diturunkan saat baca** dari `expires_at` dan `revoked_at`. Kebalikan dari status resign, dan bedanya berangkat dari satu hal: hangusnya SP tak punya efek samping apa pun. Menyimpannya berarti menaruh kebenaran jumlah SP aktif pada cron yang berjalan tepat waktu.
- **Akses TIGA arah**: HR seluruh perusahaan, karyawan atas dirinya sendiri, atasan atas departemen bawahannya. Cakupan supervisi diambil dari `SupervisedDepartmentsStrict`, **bukan** `SupervisedDepartments` yang ber-fallback ke departemen sendiri — dengan yang ber-fallback, setiap karyawan bisa membaca SP rekan sedepartemennya.
- **TIDAK mendaftarkan feed ke [[Microservices - Calendar Service]]** meski aturan tim mewajibkan fitur bertanggal melakukannya. **Penyimpangan sadar**: SP adalah status yang berlaku, bukan agenda yang perlu diingat, dan isinya data pribadi sensitif yang tak lolos prinsip tiga lapis kalender.

## Belum Diimplementasikan / Catatan

- ⚠️ **Pemicu SP2 dan SP3 TIDAK terdefinisi di peraturan.** Dok Pasal 55/56 hanya menuliskan *akibat* SP2 dan SP3, tak pernah menyebut apa yang menaikkan orang dari SP1 ke SP2. Karena itu mesin usulan **hanya untuk SP1**; SP2 dan SP3 murni terbit manual. Perlu konfirmasi HRD.
- ⚠️ **Masa berlaku SP1 dan SP3 belum dipastikan.** Enam bulan hanya tertulis eksplisit untuk SP2 (Pasal 55). Nilai itu dipakai untuk ketiganya sebagai default, dan disimpan **per catatan** supaya koreksi HRD nanti tak menuntut migrasi.
- 🟡 **Dampak payroll (potong 25% gaji pokok)** dicatat sebagai data, **tidak dieksekusi** ke [[HRIS - Payroll]]. Ditunda sadar.
- 🟡 **Skorsing (Pasal 53) dan PHK (Pasal 56)** di luar lingkup: keduanya menyentuh pencabutan akses akun, wilayah yang berbagi jalur dengan catatan resign.
- 🟡 **Status SP di landing page** ([[BASE - Enterance Point]]) belum ada; butuh endpoint ringkasan yang baru bisa dibuat setelah irisan ini mendarat.
- ⚠️ **Kategori inbox `warning-issued`/`warning-revoked` belum dikenali [[APP - MyBharata]]** (`notification_type.dart`), jadi notifikasinya jatuh ke `default` dan tampil berlabel "Sistem" dengan ikon server. Perlu PR terpisah di repo `my-bharata`.
- Alur **approval penerbitan SP** tidak dibuat: SP diterbitkan HR, bukan diajukan.

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]] (BPMN penanganan telat) · [[BASE - Enterance Point]] (status SP di landing)
- [[HRIS - Attendance System]] (sumber data telat) · [[HRIS - Personalia]] · [[HRIS - Conflict Management]] (konflik dapat berujung SP)
- [[Microservices - Employee Service]] · [[Microservices - Attendance Service]] · [[Microservices - Notification Service]] · [[Microservices - File Service]]
- [[API - Employee Service]] · [[API - Attendance Service]] · [[APP - Web ERP]] · [[APP - MyBharata]]

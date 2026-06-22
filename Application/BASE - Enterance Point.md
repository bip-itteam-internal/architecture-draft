## Deskripsi

*Ini adalah landing page aplikasi yang mencakup portal ke sistem lain, saat ini secara eksklusif diimplementasikan untuk website*

## Fitur

Karena kami sudah memiliki informasi dasar karyawan, kami dapat membuat beberapa informasi yang berguna (good to have) bagi mereka pada landing page ini, lihat di bawah

- Pemeriksaan informasi pribadi (read-only)
- Kalender dengan jadwal kerja dan shift mereka
	- Yang juga mencakup cuti massal yang sudah ditentukan perusahaan atau hari libur nasional
- Status kehadiran mereka saat ini (ini membutuhkan HRIS - Attendance System)
- Status Surat Peringatan (SP, yang dalam bahasa Indonesia berarti Surat Peringatan) dan berapa banyak yang sedang mereka miliki saat ini
	- Perlu informasi lebih lanjut mengenai penghapusan ini, karena masing-masing memiliki masa berlaku 6 bulan sebelum dihapuskan

Daftar portal akan ditampilkan di sisi kiri layar, terdaftar dengan semua kemungkinan fitur dari setiap sistem aktif berdasarkan role mereka di dalam sistem, contoh di bawah
- HR Manager login ke APP - Website dan kini berada di BASE - Landing Page, mereka dapat melihat fitur Manage Employee di bawah judul HRIS pada sisi kiri, yang ketika diklik akan langsung membawa mereka ke fitur tersebut, gambar contoh ini akan segera dilampirkan

![[landing-page-example.png]]

Pada sisi kiri, judul seperti: HRIS, Manufacturer, dan IT tidak dapat diklik dan hanya untuk indikasi, yang dapat diklik hanyalah fitur-fitur di bawah judul tersebut

Ini dapat diimplementasikan baik pada Mobile maupun Web application, walaupun UX pada mobile mungkin terganggu akibat daftar tab kiri yang tersembunyi ini

## Kebutuhan

- [x] Employees master data (referensi look up)
- [x] Informasi role dari employee master data
	- [ ] Status fitur dari sistem yang tersedia (untuk flag maintenance, karena Anda tidak ingin menyembunyikan ini di front-end, melainkan ingin menandainya sebagai tidak tersedia untuk sementara)
- [x] Portal terpadu ke service atau sistem lain

## Dependencies

- [x] [[CORE - API Master Gateway]]

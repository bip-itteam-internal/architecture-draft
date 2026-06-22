## Deskripsi

*Ini adalah aplikasi/platform utama yang akan menjadi portal untuk mengakses seluruh sistem dan fitur, informasi mengenai survei perangkat mobile karyawan [terdaftar di sini](https://docs.google.com/spreadsheets/d/1w2blhMgFx1BI9zu6ni5gmQJab_NfMhdocm0cj5pyO_s/edit?usp=sharing)*

## Fitur

- Halaman login
	- Login dengan username dan password, atau dengan passkey tambahan yang telah disiapkan pada halaman registrasi
	- Informasi lebih lanjut mengenai passkey dapat dilihat di Employee Master Data
- Halaman registrasi atau on-boarding
	- ~~(Tidak digunakan untuk saat ini karena kami tidak ingin langsung menerapkan verifikasi kedua) Ini berada di dalam halaman login, di mana diperlukan klik tambahan untuk "Karyawan baru", berikut adalah alur registrasinya:~~
		1. ~~Informasi mengenai karyawan sudah diisi oleh HRD dan mengetahui Employee ID merupakan syarat untuk langkah berikutnya~~
		2. ~~Masukkan Employee ID yang belum terdaftar dan sistem akan menampilkan nama lengkap karyawan tersebut (untuk memastikan karyawan dan akun mereka cocok)~~
		3. ~~Kewajiban untuk mengisi username baru, password, dan memilih 1 opsi untuk verifikasi kedua (nomor telepon atau email, ini adalah data read-only yang diambil dari MODULE - Employee Master Data)~~
		4. ~~Pengaturan tambahan untuk metode login alternatif dengan PIN atau passkey biometrik (berdasarkan kemampuan perangkat) langkah ini dapat dilewati~~
	- Ini terjadi secara otomatis ketika karyawan login ke platform untuk pertama kalinya
		1. Karena karyawan tidak tahu apa yang harus dimasukkan pada username/password, HRD perlu memberi tahu karyawan baru Employee ID mereka dan password sementara yang dihasilkan oleh sistem
		2. Karyawan login ke platform menggunakan Employee ID mereka (pada kolom username) dan password sementara
		3. Sistem secara otomatis memeriksa kredensial dan mengetahui bahwa ini adalah pertama kalinya mereka mengakses platform, sehingga mereka dialihkan ke halaman untuk mengatur username dan password baru
		4. Setelah pengaturan selesai, mereka dibawa kembali ke halaman login untuk menguji detail/kredensial login mereka sebelum masuk ke platform
	- HRD akan dapat melihat password sementara dari pembuatan data karyawan baru untuk diinformasikan kepada karyawan tersebut agar dapat login ke platform menggunakan Employee ID dan password sementara mereka
- Dashboard dasar dengan portal untuk mengakses sistem lain (BASE - Landing Page)
	- Halaman dashboard dasar akan mencakup informasi dasar atau status karyawan
	- Akses portal ke sistem lain akan ditampilkan dengan antarmuka portal modular, kemungkinan dengan dashboard berbasis tile

## Fitur yang Sudah Diimplementasikan

1. Halaman login dengan username dan password
2. Halaman re-login cepat dengan PIN atau Biometrik
3. Fitur onboarding untuk pengguna pertama kali atau akun yang di-reset
4. Tampilan kehadiran hari ini dan jadwal
5. Clock-in dan clock-out kehadiran

## Fitur yang Belum Diimplementasikan

1. Masih banyak fitur yang belum diimplementasikan yang front-end mobile-nya sudah selesai, sekarang tinggal pertanyaan kapan kami akan menyelesaikan dan mendukung fitur-fitur tersebut

## Dependencies

- [x] [[CORE - API Master Gateway]]
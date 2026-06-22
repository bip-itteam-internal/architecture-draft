## Deskripsi

*Ini adalah aplikasi/platform utama yang akan menjadi portal untuk mengakses seluruh sistem dan fitur*

## Fitur

- Halaman login
	- Login dengan username dan password, passkey tidak tersedia pada web application
- Dashboard dasar dengan portal untuk mengakses sistem lain (BASE - Landing Page)
	- Halaman dashboard dasar akan mencakup informasi dasar atau status karyawan
	- Akses portal ke sistem lain akan ditampilkan dengan antarmuka portal modular, kemungkinan dengan dashboard berbasis tile
- **PRIORITAS:** HRIS Manager harus dapat menginput ke Employee Master Data, karena ini merupakan dependency mutlak untuk membuat fitur login dan registrasi APP - Mobile Application

## Fitur yang Sudah Diimplementasikan

1. Halaman login dengan username dan password
2. HRIS mengelola employee master data
3. HRIS memantau dan mengedit data kehadiran karyawan
4. HRIS mengelola daftar hari libur

## Fitur yang Belum Diimplementasikan

1. Peringatan HRIS untuk karyawan yang masuk kategori berikut:
	- Data karyawan terisi sebagian
	- Karyawan belum terdaftar di aplikasi mobile myBharata
	- Karyawan mendekati akhir masa kontraknya
	- Karyawan absen dari kehadiran tanpa keterangan apa pun
2. IT mengelola role sistem karyawan
3. IT me-reset akun karyawan
4. Helpdesk untuk seluruh sistem yang dapat dilihat oleh siapa saja

## Dependencies

- [x] [[CORE - API Master Gateway]]
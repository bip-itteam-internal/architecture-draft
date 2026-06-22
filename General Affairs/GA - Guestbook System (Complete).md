## Deskripsi

Versi digital dari guestbook perusahaan yang saat ini ditangani secara manual, saat ini belum menjadi sistem yang sepenuhnya lengkap tetapi kami sedang mengerjakannya, lihat [repository GitHub](https://github.com/bip-itteam-internal/guestbook-system)

Sistem ini sepenuhnya dimiliki oleh GA Security dan mereka memiliki kontrol penuh atasnya, semua informasi akan disimpan di bawah [[Microservices - Attendance Service]]

## Fitur

- Aplikasi web publik yang bertanggung jawab mengirim entri guestbook ke sistem ERP
	- Security menampilkan QR code guestbook kepada pengunjung untuk mereka isi guestbook-nya
	- Request valid jika token yang dikirim cocok dengan token aktif pada sistem ERP, yang dirotasi setiap hari pada pukul 4 pagi
- Tampilan guestbook tersedia untuk GA/Security dan semua role HR

- Untuk karyawan yang terlambat dan perlu mengisi guestbook, kami memiliki opsi yang lebih cepat untuk melakukannya dengan bantuan aplikasi mobile, penjelasan di bawah;
	- Karyawan datang terlambat, dan clock in di gerbang
	- Security meminta karyawan untuk menampilkan QR data karyawan mereka
	- Security memilih opsi 'scan late employee QR' dan cukup scan QR-nya
	- Detailnya terisi otomatis dan diteruskan ke guestbook


## Pratinjau

Karena aplikasi ini mobile-first, kami sekarang tidak terlalu peduli untuk mendukung tampilan yang lebih baik untuk desktop

![[Pasted image 20260307112209.png]]
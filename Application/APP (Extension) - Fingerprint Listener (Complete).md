## Deskripsi

Aplikasi ini bertanggung jawab untuk mendengarkan dan mengirimkan perintah ke mesin fingerprint
[Lihat repository aplikasinya](https://github.com/bip-itteam-internal/fingerprint-listener)

- **Status**: ✅ Implemented — listener fingerprint (Python/pyzk) yang push event ke ERP.

Extension/middleware ini menyediakan:
- Push event fingerprint ke dalam sistem ERP
- Permintaan ERP untuk mengekspor data fingerprint langsung dari mesin yang kemudian akan dikirim ke pesan WhatsApp HR melalui chatbot IT WooWa
- Permintaan ERP untuk menyinkronkan waktu mesin fingerprint

Aplikasi dibangun dengan Python menggunakan library [pyzk](https://github.com/fananimi/pyzk), karena library ini sudah menghubungkan seluruh SDK menjadi satu tempat, dan juga mendukung seri lainnya.

## Perangkat fingerprint

Saat ini kami memiliki 2 perangkat fingerprint:
- **X105 Solution** (di gedung kantor utama Cipari, lantai dasar pada pintu masuk utama)
- **X609 Solution** (di gudang Tinggarjaya, detail spesifik mengenai lokasi penempatannya tidak diketahui)

Hal ini berarti kedua perangkat tersebut perlu memiliki data user yang sama, karena data tersebut perlu disinkronkan dengan sistem ERP, dan setiap perangkat tambahan perlu dikloning

## Spesifikasi perangkat fingerprint

Berikut adalah spesifikasi perangkat beserta catatan mengenai perangkat tersebut, karena perangkat ini digunakan secara intensif sehingga beberapa keanehan (quirk) memang dapat terjadi

### X105 Solution 

![[x105.jpg]]
![[Additional documents/Fingerprint Machine X105/specification.png]]

#### Status dan informasi saat ini

- **Platform**: JZ4725_TFT
- **Firmware**: Ver 6.60 Jun 23 2015
- **Serial Number**: OID6090586090601114
- **MAC Address**: 00:17:61:94:4C:B8
- **IP Address**: 10.10.10.201
- **Subnet Mask**: 255.255.255.0
- **Gateway**: 10.10.10.1

#### Masalah yang diketahui

- Port 4370 perangkat fingerprint dibatasi hanya 1 koneksi
	- Hal ini berarti jika kami ingin mengarahkan port ini ke server untuk listener event fingerprint custom, maka HR tidak akan dapat mengaksesnya melalui aplikasi solution
- Memori onboard perangkat fingerprint ter-reset setelah 3 hari tanpa daya? Mengapa hal ini bisa terjadi? Apakah baterai CMOS-nya rusak atau apa yang sebenarnya terjadi pada perangkat?
	- Hal ini berarti informasi koneksi/komunikasi juga akan ter-reset, sehingga perlu diatur ulang secara manual agar kembali berada pada jaringan yang benar 

### X609 Solution

Perangkat ini sebelumnya digunakan di Gudang Tinggarjaya, tetapi sekarang sudah tidak digunakan lagi dan dapat dimanfaatkan untuk keperluan lain

Karena perangkat ini lebih baik daripada yang kami gunakan saat ini, kami dapat menggunakannya di kantor utama dan memperbarui kartu ID karyawan dengan RFID tertanam serta menampilkan QR code ERP di masa mendatang

![[x609.jpg]]
![[Additional documents/Fingerprint Machine X609/specification.png]]

#### Status dan informasi saat ini

- **Platform**: ZLM60_TFT
- **Firmware**: Ver 6.60 Apr 13 2022
- **Serial Number**: JHG3235300134
- **MAC Address**: 00:17:61:10:40:48
- **IP Address**: 
- **Subnet Mask**: 
- **Gateway**: 10.10.10.1

## Informasi tambahan

Aplikasi ini saat ini dibatasi hanya untuk 1 perangkat, karena lebih mudah dibuat. Oleh karena itu, jika kami mendengarkan 2 atau lebih perangkat, jumlah aplikasi aktif akan bertambah dengan jumlah yang sama

Aplikasi ini sudah memiliki disaster recovery yang baik, mematikan dirinya sendiri ketika ditemukan error, serta pengecekan heartbeat jika koneksi terputus.
Namun pengujian lebih lanjut selalu diperlukan karena hal ini berkaitan dengan perangkat hardware

## Dependencies

- [x] [[CORE - API Master Gateway]]
- [x] [[Microservices - Attendance Service]]
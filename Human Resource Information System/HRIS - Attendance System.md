## Catatan

*Sistem ini diperlukan untuk attendance otomatis yang akan bermanfaat bagi HRIS - Payroll
Sistem ini sebaiknya dipindahkan dari sistem HRIS ke Extension atau tempat lain*

## Latar Belakang

* Sistem attendance saat ini bersifat semi-otomatis. Kita memiliki mesin fingerprint reader (Solution X105) yang terhubung ke jaringan. HR dapat menarik log attendance setiap hari. (Ada upaya untuk membuat cron job yang menarik log secara berkala namun belum pernah berhasil).
	* Bagaimana data dari mesin fingerprint reader (Solution X105) akan diintegrasikan ke sini?
		- Kita dapat menggunakan SDK mereka dan membuat script sendiri (https://drive.google.com/file/d/1MSV_OdJRTjIlcrKOrw1t0bbpT3vS4GoF/view?usp=sharing) atau pihak ketiga (ada beberapa script open source) untuk menarik data attendance setiap hari
		- Menyimpannya di "Raw Database"
		- Mesin fingerprint berfungsi sebagai "Fallback" jika dibutuhkan
	- Dengan melihat SDK-nya, kita bisa membuat middleware listener, di mana ia akan meneruskan sinyal dari mesin fingerprint ke website ERP pada attendance service dengan route khusus untuk clock-in/out otomatis via fingerprint
	- Aplikasi listener akan dibangun dengan Python menggunakan library [pyzk](https://github.com/fananimi/pyzk), karena library tersebut sudah menyatukan seluruh SDK dalam satu tempat, dan juga mendukung seri lainnya. Repository-nya akan dibagikan di sini nanti
- Baca lebih lanjut tentang aplikasi mesin fingerprint dan penggunaannya pada **APP (Extension) - Fingerprint Listener**
* Setelah banyak pertimbangan, kami memutuskan untuk membuat Mobile App sebagai gerbang attendance. Mobile App akan dipasang pada setiap karyawan dan mereka dapat melakukan clock-in atau clock-out di mana saja dalam radius tertentu. (50 m)
* Ada 3 lapis keamanan untuk clock-in/out: Face recognition, Geolocation, dan Geofencing (harus terhubung ke WIFI lokal)
	* Jika sistem hanya tersedia di jaringan lokal maka informasi Geolocation dan Geofencing menjadi redundan
* Setiap data clock-in/out disimpan di database "Attendance Logs" yang dibuat se-real-time mungkin.

## Pertimbangan

Karena kita menggunakan MongoDB, ada baiknya [membaca ini](https://www.mongodb.com/docs/manual/data-modeling/design-antipatterns/reduce-collections/) sebelum langsung merancang struktur database

## Use-case Diagram

Attendance dapat dilakukan dengan 2 metode per Februari 2026, baik dari validasi mesin fingerprint maupun aplikasi mobile, website saat ini dinonaktifkan

![[attendance-use-case.png]]

## Fitur

Ini adalah fitur yang terikat dan dimiliki oleh HRIS untuk attendance
- Melihat attendance secara real-time
- Mengubah status entri attendance
- Menambahkan komentar tambahan pada entri attendance
- Menambahkan dokumen tambahan pada entri attendance
- Mengekspor laporan attendance

**(Selesai)** Milestone tambahan
 - Menghubungkan mesin fingerprint dengan listener aplikasi C/C# untuk memasukkan data ke DB menggunakan curl yang memanggil route tertentu
 - Ini terhubung dengan script Python dengan modul open-source kolektif untuk

Fitur tambahan
 - Kita mungkin ingin mempertimbangkan penggunaan lingkungan kerja hybrid/remote, sehingga karyawan perlu melakukan clock-in/out dengan aplikasi mobile di luar jaringan perusahaan

## Kebutuhan

- [x] Master data karyawan (referensi lookup)
- [x] Akses baca dan tulis ke database attendance

## Fitur Terkait

- [[HRIS - Attendance Correction]] — Alur koreksi untuk clock-in/out yang terlewat
- [[HRIS - Tukar Jadwal Kerja]] — Alur pertukaran shift/hari libur

## Dependensi

- [x] [[Microservices - Attendance Service]]

*Ini akan memasukkan data attendance ke MODULE - Attendance Data karena dibutuhkan untuk pencatatan yang akan digunakan oleh HRIS - Payroll dan karena beberapa karyawan memiliki jadwal kerja yang berbeda*

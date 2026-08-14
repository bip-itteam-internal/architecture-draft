## Catatan

*Sistem ini diperlukan untuk attendance otomatis yang akan bermanfaat bagi HRIS - Payroll
Sistem ini sebaiknya dipindahkan dari sistem HRIS ke Extension atau tempat lain*

- **Status**: ⚠️ Implemented (semi-otomatis) — presensi jalan, tapi tarik log mesin fingerprint (Solution X105) masih manual; cron/otomasi belum berhasil.

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

## Ambang Keterlambatan

Presensi mengenal **dua** ambang, bukan satu, dan keduanya bisa disetel per perusahaan
(`company_attendance_setting`, dibaca `resolveAttendanceRule` di
`services/attendance/attendance_setting.go`). Aturan yang berlaku saat entri dibuat ikut
disalin ke entri itu sendiri (`AttendanceEntries.Rule`), jadi mengubah setelan tidak
menulis ulang masa lalu.

| Setelan | Bawaan | Artinya |
|---|---|---|
| `ontime_grace_minutes` | 1 menit | Di bawah ini status tetap **Tepat Waktu** |
| `late_hour_threshold_minutes` | 11 menit | Di bawah ini status **Terlambat** tapi `late_hour` = 0 |

Perhitungannya di `calcLateStatus` (`correction.go`): `late_hour` dihitung dari selisih
terhadap **ambang**, bukan terhadap jam masuk, lalu dibulatkan ke atas per jam.

```
jam masuk →   jadwal        +1 mnt                  +11 mnt
              │  (grace)                            │  (threshold)
  status:     │ Tepat Waktu  │      Terlambat       │      Terlambat
  late_hour:  │      0       │          0           │        ≥ 1
```

Akibatnya ada **band di antara kedua ambang** yang tercatat sebagai pelanggaran tetapi tak
berakibat apa pun pada upah. Ini bukan kasus pinggiran: di produksi per 2026-08-14, **321
dari 1.043** entri Terlambat (31%) ada di band itu. Karena itu band tersebut **tidak
dihitung** sebagai keterlambatan untuk Surat Peringatan dan **tidak diwarnai** di laporan —
lihat [[HRIS - Disciplinary (Surat Peringatan)]].

Validasi setelan menolak `late_hour_threshold_minutes` yang lebih kecil dari
`ontime_grace_minutes`; keduanya boleh **0** dengan sengaja, jadi nilai nol tidak
diperlakukan sebagai "belum diisi".

## Kebutuhan

- [x] Master data karyawan (referensi lookup)
- [x] Akses baca dan tulis ke database attendance

## Fitur Terkait

- [[HRIS - Attendance Correction]] — Alur koreksi untuk clock-in/out yang terlewat
- [[HRIS - Tukar Jadwal Kerja]] — Alur pertukaran shift/hari libur
- [[HRIS - Disciplinary (Surat Peringatan)]] — Konsumen angka keterlambatan; memakai ambang di atas untuk memutuskan mana yang dihitung

## Dependensi

- [x] [[Microservices - Attendance Service]]

*Ini akan memasukkan data attendance ke MODULE - Attendance Data karena dibutuhkan untuk pencatatan yang akan digunakan oleh HRIS - Payroll dan karena beberapa karyawan memiliki jadwal kerja yang berbeda*

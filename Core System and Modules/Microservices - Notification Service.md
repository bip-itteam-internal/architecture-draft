## Deskripsi

Database ini akan menyimpan segala hal tentang notifikasi untuk semua service termasuk artikel yang ditujukan untuk mobile dan website

## Fitur

Service ini akan mampu mengelola seluruh penggunaan notifikasi pihak ketiga seperti:
- Push request notifikasi WhatsApp ke personal atau grup
- Push notifikasi FCM untuk single dan multiple token
*(Semua ini sudah siap digunakan pada shared-library dan sebagian sudah dipakai oleh beberapa service, menggabungkan semuanya menjadi satu lebih baik dibandingkan setiap service harus melakukan setup sendiri setiap kali untuk penggunaannya masing-masing)*

Database akan menyimpan informasi sebagai berikut:
- Riwayat notifikasi FCM untuk mobile dan website
- Artikel yang dibuat oleh divisi terkait update mereka yang berdampak pada departemen mereka sendiri, departemen lain, atau seluruh perusahaan, dapat dilihat pada mobile dan website

Perlu diskusi lebih lanjut tentang bagaimana hal ini akan ditempatkan di sini, karena ini lebih cocok ditempatkan pada database HRIS
- Dokumen Payroll disimpan di sini untuk setiap karyawan, dan mudah dilihat (diperlukan verifikasi PIN atau password)

## Fitur yang Sudah Selesai

Beberapa fitur di bawah ini sebenarnya sudah selesai pada shared-library namun belum diimplementasikan ke notification center; seperti FCM broadcasting, pesan WhatsApp grup, dan sebagainya

- [x] Pesan WhatsApp ke karyawan/nomor tertentu
- [x] Pesan WhatsApp ke grup tertentu
- [ ] Broadcast pesan WhatsApp ke seluruh karyawan
- [ ] Pesan FCM ke karyawan tertentu pada platform berikut:
	- [x] Perangkat Android
	- [ ] Perangkat iOS
	- [ ] Website dengan webpush
- [x] Broadcast pesan FCM ke seluruh karyawan pada semua platform

## Pertimbangan

Gambar untuk artikel perlu berukuran tetap agar tidak rusak pada notifikasi FCM di mobile, spesifikasinya di bawah ini:
- Lebar dan tinggi: 1024x512 px
- Ukuran file: di bawah 1MB, disarankan di bawah 300KB

## Struktur Data

Semua struktur di bawah ini hanyalah baseline dan dapat berubah sesuai kebutuhan

### Notification

Notifikasi personal membutuhkan employee ID untuk mengetahui notifikasi ini ditujukan untuk siapa, ini juga akan muncul pada notifikasi bulk, ini hanya dicadangkan untuk notifikasi penting
Oleh karena itu notifikasi harian seperti clock-in dan mungkin beberapa informasi artikel tidak disimpan ke collection ini

```json
{ // Notification collection
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"title": "Notification title",
	"body": "Notification body or message",
	"image": "Servable imageURL from minIO",
}
```

### Article

```json
{ // Notification collection
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"title": "Article title",
	"content": "Article content in markdown styles",
	"author_department": "String enums", // Who is publishing thiss articles?
	"pubslihed_at": Datetime, // Will be used as default sorting
	
	// Additional attachment
	"image": "Servable imageURL from minIO",
	"video": "Servable videoURL from minIO",
	"file": "Servable file from minIO",
	
	"summary": "Content summary will be used to push FCM notification",
	"pinned": true, // To be pinned on top of articles page
	
	// Engagement metrics, there is no limiter so employee can spam it, we dont really care for now
	"view_count": int,
	"like_count": int,
	"reaction": Object, // Object of emoticon and their used value in int
}
```

Artikel dapat dilihat oleh semua departemen, tidak masalah untuk mempublikasikan suatu notifikasi untuk 1 departemen di sini, karena departemen lain dapat saja mengabaikannya
Pada saat artikel dipublikasikan, artikel akan secara otomatis menggunakan judul dan summary artikel untuk push notifikasi FCM
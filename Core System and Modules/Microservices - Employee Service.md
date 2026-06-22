## Deskripsi

Master data ini mengelola seluruh data karyawan termasuk dokumen atau data tambahan yang ditautkan dari sistem lain ke dalam sistem master data ini.

[Ini adalah contoh master data karyawan yang saat ini dimiliki oleh tim HR](https://drive.google.com/drive/folders/1DlL37IECH2i1e3-3oypd912AbcPU84nX)

Ide penamaan ulang karena ini memiliki back-end dan database tersendiri
- ~~**"Employee module"** mengikuti penggunaan sistem ini~~
- **"Employee service"** mengikuti konvensi penamaan micro-services

## Detail yang Tertunda

- [ ] Siapa yang bertanggung jawab atas akurasi dan kelengkapan master data ini?
	- Ini akan menjadi tanggung jawab HRD Manager

## Struktur Data

*Seluruh data di bawah ini perlu diperiksa dan dikonfirmasi ulang*

### Pertimbangan 

Database ini membutuhkan sesuatu yang akan digunakan sebagai UUID sekaligus berperan sebagai Foreign Keys, pilih salah satu di bawah ini yang paling sesuai untuk sistem ini:
- ~~Auto increment seperti SQL standar~~
	- ~~Ini sulit untuk dibuat tepat karena perlu disinkronkan dengan penyisipan data terbaru, meskipun kita menerapkan Single Source of Truth hal ini tetap rumit untuk disinkronkan~~
- Natural keys
	- Gunakan sesuatu yang sudah ada dari data di bawah ini, kemungkinan Employee ID
- ~~UUID/GUID~~
	- ~~Mudah dibuat tetapi mengaksesnya akan menjadi mimpi buruk dan mungkin lambat? Yang default adalah 128-bit tetapi kita bisa mulai dari 16-bit dan menaikkannya jika terjadi collision~~
- ~~Snowflake (custom-uuid)~~
	- ~~Data dengan ukuran bit berapa pun yang memiliki struktur dari sistem, ukuran yang biasa digunakan adalah 64-bit dengan komposisi ini: 1-bit signed, 41-bit timestamp, 10-bit dari pembuatan database/sistem, 12-bit acak atau dari milidetik~~ 

### Data Pribadi

- Nama lengkap
- Jenis kelamin
- Agama
- Status pernikahan
- Nomor telepon
- Alamat email
- Alamat rumah
- Dokumen tambahan
	- Foto KTP
	- Foto KK

*Kita hanya menginginkan data yang dapat digunakan dan berguna bagi sistem, oleh karena itu informasi dan data tambahan dapat disimpan sebagai gambar atau dokumen hasil pindai yang disimpan dalam bentuk bytes dan bahkan dienkripsi jika diperlukan*

### Data Pekerjaan

- Employee ID (unik)
	- Setiap divisi memiliki Employee ID-nya sendiri
	- Employee ID disusun dari: BIP (jumlah, jumlah bulan masa percobaan, dll)
- Departemen atau divisi
- Posisi atau jabatan
- Tipe kepegawaian
- Nomor NPWP
- Detail bank pembayaran
- Dokumen tambahan
	- Kontrak yang ditandatangani
	- Awal masa percobaan
	- Akhir masa percobaan
	- Surat peringatan

#### Data Kehadiran

*Informasi data ini dapat ditempatkan di tempat lain jika diperlukan, ini akan menjadi referensi lookup untuk menentukan status kehadiran secara otomatis*

- Tipe kerja (onsite full-time, onsite shift-based, atau remote)
- Hari kerja
- Jam kerja (jam mulai dan jam selesai)

*Hari dan jam kerja diperlukan karena beberapa departemen tidak mengikuti sistem kehadiran konvensional, contoh: security/manufaktur karena mereka mengikuti sistem shift, live host karena mereka mulai lebih siang. dll*

### Role Autentikasi Sistem

*Data ini mencakup role karyawan pada seluruh sistem untuk informasi kerja pribadi karyawan atau sistem terkait pekerjaan lain yang diperlukan agar karyawan dapat menjalankan pekerjaannya*

*Informasi di bawah ini sangat penting dan akan dilengkapi selama proses on-boarding karyawan baru bersama dengan HRD*

- Username
- Password (hashed)
- Passkey (eksklusif untuk mobile berdasarkan kemampuan perangkat)
	- PIN (hashed)
	- Bio-metrics (kredensial ini disimpan secara lokal di perangkat per aplikasi)
- Roles (pada subsistem mereka)
	- Menggunakan object notation agar lebih mudah diakses, lookup juga lebih cepat karena dapat diakses secara langsung, contoh: `user.system_roles.hris`
	- Tentu saja ini akan menjadi tipe enum pada sistem masing-masing

## Struktur Database

Karena kita menggunakan database MongoDB NoSQL maka kita perlu mengidentifikasi apa saja yang dapat kita lakukan di dalam database

### Pertimbangan

- Beberapa collection dalam 1 database, karena MongoDB memiliki batas keras sebesar 16MB untuk setiap dokumen/entry dalam collection
	- Jika sering diakses oleh sistem
	- Jika menyimpan dokumen biner seperti gambar, PDF, dan lainnya
	- Jika tidak masuk akal untuk melakukan embedded information pada entry tersebut
		- Embedded documents pada dasarnya adalah sub-object di dalam object seperti JSON `outer_object.inner_object.entry` dan seterusnya
- Reference dengan `_id` bawaan MongoDB sebagai primary key
	- Jika ini reference 1:1 dan tidak akan pernah berubah, collection lain dapat mencocokkan field `_id` dengan object reference utama
	- Jika ini relasi many to many, lebih baik membiarkan `_id` object sebagai default dan menambahkan entry baru seperti `_employee_reference` serta memberikan reference utama ke object tersebut

### Graph dan Relasi Collection Database

Ini akan dilampirkan di masa mendatang...

### Dokumen/Entry Database

Ini adalah contoh seperti apa dokumen atau entry database nanti akan terlihat jika berada dalam 1 wrapper besar setelah seluruh join query selesai dilakukan

#### Data Pribadi

```JSON
{ // Personal information collections
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (PK)
	
	"full_name": "Aurelia Mara",
	"gender": "Female", // Enums to string
	"religion": "Islam", // Enums to string
	"marital_status": "Single", // Enums to string
	"phone_number": "081234567890",
	"email_address": "aurelia_mara@example.com",
	"home_address": "Jl. Merdeka No. 99, Bandung, Indonesia",
	
	// This still missing some information from the examples like: NIK, No. KK, since we dont know if we want to expose those, and what are the use of those information with-in the system
}
```

Dokumen dipisah untuk menghemat ruang dan karena informasi tersebut tidak sering dibutuhkan

```JSON
{ // Personal document collections
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"documents": [ // Easily expandable if needed
		{
			"type": "photo_ktp",
			"filename": "aurelia_mara_ktp.jpg",
			"file_data": BinData(0, "<binary data>"), 
		},
		{
			"type": "photo_kk",
			"filename": "aurelia_mara_kk.jpg",
			"file_data": BinData(0, "<binary data>"), 
		},
		{
			"type": "photo_npwp",
			"filename": "aurelia_mara_npwp.jpg",
			"file_data": BinData(0, "<binary data>"), 
		}
	]
}
```

#### Data Pekerjaan

```JSON
{ // Work information collections
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"department": "IT", // Enums to string
	"position": "Supervisior", // Enums to string, this doesn't really do anything for now, since we have our own system authentication
	"employment_type": "Fulltime", // Enums to string
	
	"fingerprint_number": 211, // This is required as we might fallback to attendance using fingerprint
	
	"probation": {
		start_date: ISODate(),
		end_date: ISODate()
	},
	
	"npwp_number": "6788.4642738.973", // Optional
	"bpjs_number": "39932016910944", // Optional
	
	// Since all employee are forced to have Mandiri Bank account, but what if it changes? Is this better then? Since we account for changes that might happen in the future?
	// Pick one from below
	// "mandiri_account_number": "930419413752", // Optional
	"bank_details": { // Optional
		"bank_name": "Bank Mandiri",
		"account_number": "930419413752",
		"account_holder": "Aurelia Mara"
	}
}
```

Dokumen dipisah untuk menghemat ruang dan karena informasi tersebut tidak sering dibutuhkan

```JSON
{ // Work document collections
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"documents": [ // Easily expandable if needed
		{
			"type": "signed_contract",
			"filename": "aurelia_mara_contract.pdf",
			"file_data": BinData(0, "<binary data>"), 
		},
		{
			"type": "probation_report",
			"filename": "aurelia_mara_probation.pdf",
			"file_data": BinData(0, "<binary data>"), 
		}
	]
}
```

#### Data Jadwal Kerja

Ini dipisahkan karena akan lebih sering diakses

```JSON
{ // Work schedule collections
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	// We shouldn't really mess much in here, we want to include work schedule but we need reference into their department schedule and shift, since hard embedding it in here would really bad and hard to change later on
	// Therefore this should work for now, until we enstablish attendance system

	"work_schedule": "BIP-REGULAR", // Natural keys (FK) reference to company work schedule collections
	"exception": {} // This may be needed later on for Hybrid type and such
}
```

#### Jadwal Kerja Perusahaan

Ini adalah referensi untuk Data Jadwal Kerja

Collection ini dimiliki oleh MODULE - Attendance Data, dan akan di-fetch dengan buffer time setelah inisialisasi aplikasi
Service akan panic jika tidak dapat melakukan fetch data baru dari MODULE - Attendance Data dan tidak memiliki rekaman data ini

Ini akan memiliki collection-nya sendiri di Employee Master Data dan Attendance Data serta akan disinkronkan dengan benar di antara keduanya

#### Data Autentikasi Sistem

```JSON
{ // System authentication collections
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"username": "aurelia_mara",
	"password": "hash+salt...", // Encrypted
	"passkey": { // Optional
		"pin": "hash+salt..." // Encrypted
	},
	"system_roles": { // This is easily expandable
		"it": "Supervisor" // Enums as string
	}
}
```

#### Metadata

Karena seluruh contoh di atas tidak memiliki metadata untuk tanggal pembuatan, pembaruan, atau siapa yang membuat dan memperbarui data, atau bahkan status data saat ini aktif atau tidak, hal ini akan didiskusikan di masa mendatang mengenai apa yang dibutuhkan dan apa yang tidak

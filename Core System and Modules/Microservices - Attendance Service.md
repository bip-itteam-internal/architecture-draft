## Deskripsi

*Database ini menyimpan catatan kehadiran karyawan, sehingga membutuhkan reference link ke data karyawan dan jadwal kerja mereka untuk menetapkan status yang tepat, berdasarkan [detail jadwal dan shift karyawan](https://docs.google.com/document/d/1W0MOCEPyoodp_09atBVe_PGDhSaoMgfxN2SCvpMVyHY/edit?tab=t.0)*

## Fitur

- **(Selesai)** Pembuatan data kehadiran otomatis berdasarkan shift karyawan dengan cron job 2 jam sebelum shift mereka dimulai
- **(Selesai)** Karyawan memperoleh data kehadiran terbarunya yang diurutkan berdasarkan datetime dan shift yang sesuai
- **(Selesai)** Self-service karyawan untuk endpoint clock-in dan clock-out (terbatas hanya pada modifikasi entry, tidak perlu membuat entry baru)
- **(Selesai)** Karyawan dapat melihat jadwal kerja mereka pada bulan berjalan, termasuk hari libur yang ditetapkan oleh HRIS di kalender (prioritas rendah)
- Mengirimkan notifikasi FCM ke perangkat untuk mengingatkan mereka akan jadwal kerjanya
- Penandaan paksa tambahan oleh HRIS dan penyisipan dokumen ke dalam entry (prioritas rendah)

## Cron Scheduler

Cron schedule memainkan peran penting dalam sistem database ini, karena ia bertanggung jawab atas pembuatan data kehadiran berdasarkan jadwal kerja karyawan. Sistem/engine ini sudah berjalan otomatis setiap 30 menit

Informasi yang esensial bagi cron scheduler:
1. Jadwal kerja perusahaan (Static collection) 
2. Rotasi grup perusahaan (Static collection) 
3. Hari libur perusahaan (ditetapkan oleh HRIS)
4. Jadwal kerja (diambil dari database karyawan)

Informasi minor yang digunakan oleh notifikasi FCM:
1. Token FCM aktif (diambil dari database karyawan)

## Struktur Data

*Semua data di bawah ini perlu dicek dan dikonfirmasi ulang*

- Employee ID (reference)
- Tanggal kehadiran (entry ini harus dibuat secara otomatis setiap hari)
	- Timestamp clock-in
	- Timestamp clock-out
- Status (contoh: on-time, late, alpha, sick, vacation, holiday)
	- Pengecekan otomatis oleh sistem untuk on-time, late, dan alpha
	- Penandaan manual dari HRD untuk sick, vacation, holiday, dll
		- Penandaan manual ini akan membatalkan semua informasi di bawahnya
- Jam izin otomatis
	- Dihitung secara otomatis jika telat (jam mulai - jam clock-in)
- Jam izin
	- Penyesuaian oleh HRD jika karyawan diperbolehkan meninggalkan pekerjaan selama X jam, ini membutuhkan dokumen tambahan sebagai verifikasi
- Jam lembur
	- Penyesuaian oleh HRD jika karyawan bekerja lembur selama X jam, ini membutuhkan dokumen tambahan sebagai verifikasi

Baca lebih lanjut di bawah pada **Company Group Rotation** untuk struktur data dan fitur yang dibutuhkan guna mendukung jadwal berbasis shift/grup

### Pertimbangan

- Pembatasan clock-in/out berdasarkan MAC Address Wifi, karena kita ingin membatasi dari mana karyawan dapat melakukan clock-in/out (ditangani oleh front-end)
	- Mengapa MAC Address dan bukan sekadar SSID? Karena SSID dapat dengan mudah direplikasi dengan Hotspot, sedangkan MAC Address tidak, yang mana akan lebih sulit untuk dilakukan
	- Tapi apakah ini layak? Karena akses ke MAC Address dalam keadaan normal tergolong sebagai detail sensitif
- Perhitungan jam kerja untuk sistem Payroll
	- Jam kerja normal
	- Jam kerja lembur
- Kehadiran untuk karyawan yang berada di dalam rolling shift seharusnya memiliki informasi tambahan pada jadwal kerja karyawannya, dan kita membutuhkan suatu fungsi penyelesaian untuk mendapatkan jadwal kerja yang tepat bagi mereka, karena bersifat dinamis
	- Rolling shift yang berubah per minggu seperti jadwal Host live
	- Rolling shift yang berubah berdasarkan repetisi mandiri seperti jadwal Security dengan 2 hari kerja dan 1 hari libur, repetisi yang mengabaikan hal lainnya 



## Struktur Database

Kita memiliki database independen sendiri yang khusus untuk attendance

### Attendance Entries

``` JSON  
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"employee_id": "0032-03-27102025", // Natural keys (FK)
	
	"date": ISODate(),
	"clock_in": Timestamp,
	"clock_out": Timestamp,
	
	"date_realtime": ISODate(), // This is going to be the sort mechanism for managing realtime attendance, this will be updated on status changes
	"status": "on-time", // Enums to string
	
	"late_hour": 0, // Decrement to normal working hour
	"leave_hour": 2, // Decrement to normal working hour	
	"overtime_hour": 2,
	
	// Do we need to set normal working hour that will be used for payroll right now? If so then add the normal working hour but this need to be check into the 'work_data' or said employee id and into 'company_work_schedule' collection to get how long does they work for the day
	// We need a better way to deal with this issues later on (this is required for payroll calculation)
	
	"documents": [ // Easily expandable if needed
		{ // The type is important as this will be the one being used as 'search' or lookup into the specifict documents
			"type": "leave_document",
			"filename": "aurelia_mara_leave.jpg",
			"file_data": BinData(0, "<binary data>"), 
		},
		{
			"type": "overtime_document",
			"filename": "aurelia_mara_overtime.jpg",
			"file_data": BinData(0, "<binary data>"), 
		},
	]
}
```

### Company Work Schedule

Informasi ini saat ini bersifat static hardcoded, yang sudah disisipkan ke database, di-refresh setiap restart. Ini dapat dikembangkan agar bisa dimodifikasi di masa mendatang jika dirasa perlu

Tapi percayalah, jika ini bisa diedit mereka akan dengan mudah merusak jadwal dan menyalahkan sistem otomatis karena kesalahan mereka sendiri.
Karena itu pertahankan ini sebagai static hardcoded selama mungkin!

```JSON
{ // Company work schedule collections (This is bad, but will do for now)
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "BIP-REGULAR", // Natural keys (PK)	

	// Below are bad since what if it has this and that exception? If so then this need to write the exception and explain it before passing into front-end
	// "work_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
	// "work_hours": { "start": "09:00", "end": "17:00" },

	// This is better in structures, but still yikes also this can be change to array if necessary
	"schedule": {
		"monday":    {"start": "08:00", "end": "17:00"},
		"tuesday":   {"start": "08:00", "end": "17:00"},
		"wednesday": {"start": "08:00", "end": "17:00"},
		"thursday":  {"start": "08:00", "end": "17:00"},
		"friday":    {"start": "08:00", "end": "17:00"},
		"saturday":  {"start": "08:00", "end": "13:00"}, // 5 hours
		"sunday":    null
	}
},
// Below are for Office boy
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "OFFICEBOY-REGULAR", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "06:30", "end": "17:00"},
		"tuesday":   {"start": "06:30", "end": "17:00"},
		"wednesday": {"start": "06:30", "end": "17:00"},
		"thursday":  {"start": "06:30", "end": "17:00"},
		"friday":    {"start": "06:30", "end": "17:00"},
		"saturday":  {"start": "06:30", "end": "14:00"}, // 5 hours
		"sunday":    null
	}
},
// Actual based takes for off-duty employee, don't question this decision..
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "OFF-DUTY", // Natural keys (PK)
	"schedule": {
		"monday":    null,
		"tuesday":   null,
		"wednesday": null,
		"thursday":  null,
		"friday":    null,
		"saturday":  null,
		"sunday":    null
	}
},
// Below are shift for Host Live
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "HOSTLIVE-SHIFT-A", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "05:00", "end": "13:00"},
		"tuesday":   {"start": "05:00", "end": "13:00"},
		"wednesday": {"start": "05:00", "end": "13:00"},
		"thursday":  {"start": "05:00", "end": "13:00"},
		"friday":    {"start": "05:00", "end": "13:00"},
		"saturday":  {"start": "05:00", "end": "13:00"},
		"sunday":    {"start": "05:00", "end": "13:00"}
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "HOSTLIVE-SHIFT-B", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "13:00", "end": "21:00"},
		"tuesday":   {"start": "13:00", "end": "21:00"},
		"wednesday": {"start": "13:00", "end": "21:00"},
		"thursday":  {"start": "13:00", "end": "21:00"},
		"friday":    {"start": "13:00", "end": "21:00"},
		"saturday":  {"start": "13:00", "end": "21:00"},
		"sunday":    {"start": "13:00", "end": "21:00"}
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "HOSTLIVE-SHIFT-C", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "21:00", "end": "05:00"},
		"tuesday":   {"start": "21:00", "end": "05:00"},
		"wednesday": {"start": "21:00", "end": "05:00"},
		"thursday":  {"start": "21:00", "end": "05:00"},
		"friday":    {"start": "21:00", "end": "05:00"},
		"saturday":  {"start": "21:00", "end": "05:00"},
		"sunday":    {"start": "21:00", "end": "05:00"}
	}
},
// Below are shift for Security
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "SECURITY-SHIFT-A", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "07:00", "end": "19:00"},
		"tuesday":   {"start": "07:00", "end": "19:00"},
		"wednesday": {"start": "07:00", "end": "19:00"},
		"thursday":  {"start": "07:00", "end": "19:00"},
		"friday":    {"start": "07:00", "end": "19:00"},
		"saturday":  {"start": "07:00", "end": "19:00"},
		"sunday":    {"start": "07:00", "end": "19:00"}
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "SECURITY-SHIFT-B", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "19:00", "end": "07:00"},
		"tuesday":   {"start": "19:00", "end": "07:00"},
		"wednesday": {"start": "19:00", "end": "07:00"},
		"thursday":  {"start": "19:00", "end": "07:00"},
		"friday":    {"start": "19:00", "end": "07:00"},
		"saturday":  {"start": "19:00", "end": "07:00"},
		"sunday":    {"start": "19:00", "end": "07:00"}
	}
},
// Below are for Production
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "PRODUCTION-SHIFT-A", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "08:00", "end": "16:00"},
		"tuesday":   {"start": "08:00", "end": "16:00"},
		"wednesday": {"start": "08:00", "end": "16:00"},
		"thursday":  {"start": "08:00", "end": "16:00"},
		"friday":    {"start": "08:00", "end": "16:00"},
		"saturday":  {"start": "08:00", "end": "13:00"}, // 5 hours
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "PRODUCTION-SHIFT-B", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "16:00", "end": "00:00"},
		"tuesday":   {"start": "16:00", "end": "00:00"},
		"wednesday": {"start": "16:00", "end": "00:00"},
		"thursday":  {"start": "16:00", "end": "00:00"},
		"friday":    {"start": "16:00", "end": "00:00"},
		"saturday":  {"start": "16:00", "end": "21:00"}, // 5 hours
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "PRODUCTION-SHIFT-C", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "00:00", "end": "08:00"},
		"tuesday":   {"start": "00:00", "end": "08:00"},
		"wednesday": {"start": "00:00", "end": "08:00"},
		"thursday":  {"start": "00:00", "end": "08:00"},
		"friday":    {"start": "00:00", "end": "08:00"},
		"saturday":  {"start": "00:00", "end": "05:00"}, // 5 hours
		"sunday":    null
	}
},
// Below are for Inventory
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "INVENTORY-SHIFT-A", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "08:00", "end": "16:00"},
		"tuesday":   {"start": "08:00", "end": "16:00"},
		"wednesday": {"start": "08:00", "end": "16:00"},
		"thursday":  {"start": "08:00", "end": "16:00"},
		"friday":    {"start": "08:00", "end": "16:00"},
		"saturday":  {"start": "08:00", "end": "13:00"}, // 5 hours
		"sunday":    null
	}
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"schedule_id": "INVENTORY-SHIFT-B", // Natural keys (PK)
	"schedule": {
		"monday":    {"start": "16:00", "end": "00:00"},
		"tuesday":   {"start": "16:00", "end": "00:00"},
		"wednesday": {"start": "16:00", "end": "00:00"},
		"thursday":  {"start": "16:00", "end": "00:00"},
		"friday":    {"start": "16:00", "end": "00:00"},
		"saturday":  {"start": "16:00", "end": "21:00"}, // 5 hours
		"sunday":    null
	}
}
```

### Company Group Rotation

Informasi ini diperlukan karena kita perlu mengubah rotasi shift grup atau rolling shift secara sesuai, yang berarti beberapa karyawan tidak terikat pada jadwal mereka sendiri melainkan pada jadwal grupnya, yang akan merepotkan untuk ditangani...

1. **Grup Host live**, dirotasi per minggu, dengan total 4 grup (3 grup aktif bekerja dan 1 grup libur pada minggu tertentu) 
	- **Struktur array:** A, B, C, null
	- **Perubahan index:** 7 hari
2. **Grup Security**, dirotasi berdasarkan penyelesaian mandiri, dengan total 3 grup (2 grup aktif bekerja dan 1 grup libur pada hari tertentu)
	- **Struktur array:** A, B, null
	- **Perubahan index:** penyelesaian array dan reset kembali ke index pertama

Karena itu kita akan membutuhkan 1 fungsi helper untuk menyadari perbedaan ini antara jadwal karyawan berbasis statis dan jadwal berbasis shift/grup (atau apa pun namanya nanti) lalu meneruskannya ke fungsi resolver untuk pengambilan atau lookup tanggal/kehadiran

Selain itu, karena jadwal berbasis shift/grup ini memiliki perbedaan dalam cara penyelesaiannya, yang satu berubah secara statis berdasarkan waktu dan yang lainnya berdasarkan penyelesaiannya sendiri, maka kita akan memiliki 2 fungsi resolver

```JSON
// Host-live rolling schedules
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "HOSTLIVE-GROUP-1",
	"schedule_rotation": [
		"HOSTLIVE-SHIFT-A", 
		"HOSTLIVE-SHIFT-B", 
		"HOSTLIVE-SHIFT-C", 
		"OFF-DUTY"
	],
	"schedule_rotated_in_x_days": 7,
	
	"starting_date": ISODate(),
	"starting_schedule": "HOSTLIVE-SHIFT-A",
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "HOSTLIVE-GROUP-2",
	"schedule_rotation": [
		"HOSTLIVE-SHIFT-A", 
		"HOSTLIVE-SHIFT-B", 
		"HOSTLIVE-SHIFT-C", 
		"OFF-DUTY"
	],
	"schedule_rotated_in_x_days": 7,
	
	"starting_date": ISODate(),
	"starting_schedule": "HOSTLIVE-SHIFT-B",
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "HOSTLIVE-GROUP-3",
	"schedule_rotation": [
		"HOSTLIVE-SHIFT-A", 
		"HOSTLIVE-SHIFT-B", 
		"HOSTLIVE-SHIFT-C", 
		"OFF-DUTY"
	],
	"schedule_rotation_days": 7,
	
	"starting_date": ISODate(),
	"starting_schedule": "HOSTLIVE-SHIFT-C",
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "HOSTLIVE-GROUP-4",
	"schedule_rotation": [
		"HOSTLIVE-SHIFT-A",
		"HOSTLIVE-SHIFT-B", 
		"HOSTLIVE-SHIFT-C", 
		"OFF-DUTY"
	],
	"schedule_rotated_in_x_days": 7,
	
	"starting_date": ISODate(),
	"starting_schedule": null,
},

// Security rolling schedules
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "SECURITY-GROUP-1",
	"schedule_rotation": ["SECURITY-SHIFT-A", "SECURITY-SHIFT-B", "OFF-DUTY"],
	"schedule_rotated_in_x_days": 1,
	
	"starting_schedule": "SECURITY-SHIFT-A",
	"starting_date": ISODate(),
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "SECURITY-GROUP-2",
	"schedule_rotation": ["SECURITY-SHIFT-A", "SECURITY-SHIFT-B", "OFF-DUTY"],
	"schedule_rotated_in_x_days": 1,
	
	"starting_date": ISODate(),
	"starting_schedule": "SECURITY-SHIFT-B",
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"group_id": "SECURITY-GROUP-3",
	"schedule_rotation": ["SECURITY-SHIFT-A", "SECURITY-SHIFT-B", "OFF-DUTY"],
	"schedule_rotated_in_x_days": 1,
	
	"starting_date": ISODate(),
	"starting_schedule": null,
}

// Production rolling schedules
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"group_id": "PRODUCTION-GROUP-1",
	"schedule_rotation": [
	   "PRODUCTION-SHIFT-A", 
	   "PRODUCTION-SHIFT-C", 
	   "PRODUCTION-SHIFT-B"
	],
	schedule_rotated_in_x_days: 7,
	starting_date: ISODate(),
	starting_schedule: "PRODUCTION-SHIFT-A"
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"group_id": "PRODUCTION-GROUP-2",
	"schedule_rotation": [
	   "PRODUCTION-SHIFT-A", 
	   "PRODUCTION-SHIFT-C", 
	   "PRODUCTION-SHIFT-B"
	],
	schedule_rotated_in_x_days: 7,
	starting_date: ISODate(),
	starting_schedule: "PRODUCTION-SHIFT-C"
},
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	"group_id": "PRODUCTION-GROUP-3",
	"schedule_rotation": [
	   "PRODUCTION-SHIFT-A", 
	   "PRODUCTION-SHIFT-C", 
	   "PRODUCTION-SHIFT-B"
	],
	schedule_rotated_in_x_days: 7,
	starting_date: ISODate(),
	starting_schedule: "PRODUCTION-SHIFT-B"
},
 
// Warehouse rolling schedules
// This is still wrong as there is 3 groups and 2 groups will be at shift A at any given time, which mean we should ref by index instead of string to the array
 {
	"_id": ObjectId(MongoDB_ID_Assignment),
	"group_id": "WAREHOUSE-GROUP-1",
	"schedule_rotation": [
	   "WAREHOUSE-SHIFT-A", 
	   "WAREHOUSE-SHIFT-A", 
	   "WAREHOUSE-SHIFT-B"
	],
	schedule_rotated_in_x_days: 7,
	starting_date: ISODate(),
	starting_schedule: "WAREHOUSE-SHIFT-A"
},
 {
	"_id": ObjectId(MongoDB_ID_Assignment),
	"group_id": "WAREHOUSE-GROUP-2",
	"schedule_rotation": [
	   "WAREHOUSE-SHIFT-A", 
	   "WAREHOUSE-SHIFT-A", 
	   "WAREHOUSE-SHIFT-B"
	],
	schedule_rotated_in_x_days: 7,
	starting_date: ISODate(),
	starting_schedule: "WAREHOUSE-SHIFT-B"
},
```

### Company Holiday Date

Sekadar informasi pada database di mana ini akan digunakan untuk mengecek apakah schedule engine perlu membuat kehadiran pada hari itu atau tidak

Catatan, kamu akan membutuhkan sesuatu untuk mengambil informasi jam kerja normal pada hari libur beserta perhitungannya, karena hari libur perusahaan dibayar penuh, dan hari libur nasional dibayar penuh tetapi dikurangi tunjangan makan siang

```JSON
{
	"_id": ObjectId(MongoDB_ID_Assignment),
	
	"date": ISODate(),
	"note": "additional notes regarding the holiday" // String normal inserted
}
```

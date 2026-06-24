> **Status:** 🟡 Benchmark / Konsep — research dari ERPGo SaaS, **belum** keputusan Bharata. Sumber: User Manual ERPGo (demo login-gated). Hub: [[ERPGo - Overview & Gap Matrix]].

## Apa yang ERPGo lakukan

Modul **Timesheet**:
- Catat **jam kerja per karyawan terhadap project/task** (tanggal, durasi, deskripsi aktivitas).
- Terhubung ke modul **Project** (alokasi effort) dan dipakai untuk laporan utilisasi / dasar billing.

## Yang sudah ada di Bharata ERP

- [[Microservices - Attendance Service]] — mencatat **kehadiran** (clock-in/out, jadwal, lembur via [[HRIS - Overtime]]). Ini jam **hadir**, bukan jam **per-task**.
- [[Microservices - Task Management Service]] — task & space ([[APP - Dynamic Task Tracker]]), tapi tanpa pencatatan **durasi kerja per task**.
- 🟡 Jadi datanya **terpisah**: ada kehadiran + ada task, tapi tidak ada jembatan "berapa jam di task X".

## Gap / Peluang

- Tidak ada **utilisasi effort per project/task**. Berguna bila perusahaan ingin mengukur biaya/produktivitas per proyek (mis. tim IT/kreatif: [[Sales - GMV Creative]], [[APP - Ideamills]]).
- Karena task service sudah ada, timesheet bisa jadi **ekstensi tipis** di atasnya, bukan modul besar.

## Rekomendasi

- **Adopsi — prioritas rendah/sedang.** Nilai tertinggi untuk tim berbasis proyek.
- **Penempatan usulan** (bila jadi): perkaya [[Microservices - Task Management Service]] / [[APP - Dynamic Task Tracker]] dengan **time-log per task** (mulai/selesai atau durasi manual), lalu agregasi per project/karyawan.
- **MVP minimal**: field durasi + report agregat. Jangan duplikasi kehadiran dari attendance-service.

## Risiko & catatan jaga sistem berjalan

- Hindari kerancuan dengan kehadiran/lembur yang sudah jadi sumber payroll ([[HRIS - Payroll]]); timesheet ≠ basis gaji kecuali diputuskan eksplisit.
- Ikuti ownership data: time-log milik task-management-service ([[DB - Overview and Notes]]).

## Dokumen Terkait

- [[ERPGo - Overview & Gap Matrix]]
- [[Microservices - Task Management Service]] · [[APP - Dynamic Task Tracker]]
- [[Microservices - Attendance Service]] · [[HRIS - Overtime]]

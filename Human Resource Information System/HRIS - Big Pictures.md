## Dokumen

Berikut ini adalah dokumen yang saat ini dimiliki HRD yang sedang disimpan beserta beberapa dokumen umum yang digunakan secara internal

https://drive.google.com/drive/folders/1DlL37IECH2i1e3-3oypd912AbcPU84nX

## BPMN

Di bawah ini adalah contoh alur BPMN tentang bagaimana request saat ini dan online akan terlihat, lebih banyak diagram akan ditambahkan ke sini nanti, beserta deskripsinya masing-masing

### Proses karyawan datang terlambat ke kantor

Proses saat ini yang sedang digunakan, pada dasarnya penanganan manual
![[employee-late-manual-handling.svg]]

Sistem yang diusulkan yang akan mengotomatiskan sebagian proses dan menghilangkan 1 pool/role dari proses, dengan alur yang berakhir lebih awal, alih-alih memutari proses secara penuh
![[employee-late-automated-draft.svg]]

### Proses karyawan mengajukan cuti

Proses saat ini yang sedang digunakan, sekali lagi penanganan manual, tetapi cepat karena keseluruhan proses hanya memakan waktu ~2 menit hingga ~5 menit
![[leave-requests-manual-handling.svg]]

Draft sistem yang diusulkan, menghilangkan proses bolak-balik, tetapi menambahkan waktu tunggu yang merupakan pisau bermata dua. 
Acknowledge HR masih dalam diskusi karena jika dokumen membutuhkannya maka waktu tunggu maksimum adalah 2x24 jam untuk 1 request, yang mana itu buruk.
![[leave-requests-automated-draft.svg]]

### Cuti per jam karyawan disetujui

Ketika karyawan dengan cuti per jam disetujui, mereka perlu melewati pemeriksaan security di gerbang masuk/keluar,
ini berarti security memiliki akses untuk melihat verifikasi manual guna membandingkan/menyelaraskan dokumen karyawan dengan dokumen HR yang disetujui untuk berjaga-jaga
Security juga perlu menandatangani dokumen dengan scan QR untuk status cuti/kembali pada dokumen

![[employee-hourly-leave-approved.svg]]

## Dependensi

- [ ] [[BASE - Enterance Point]]
- [ ] [[HRIS - Analysis]]
- [ ] [[HRIS - Attendance System]]
- [ ] [[HRIS - Attendance Correction]]
- [ ] [[HRIS - Leave Request]]
- [ ] [[HRIS - Shift Exchange]]
- [ ] [[HRIS - Overtime]]
- [ ] [[HRIS - Attrition]]
- [ ] [[HRIS - Retention]]
- [ ] [[HRIS - Work Review]]
- [ ] [[HRIS - Conflict Management]]
- [ ] [[HRIS - Disciplinary (Surat Peringatan)]]
- [ ] [[HRIS - Interrelationship Matrices]]
- [ ] [[HRIS - Key Performance Index]]
- [ ] [[HRIS - Payroll]]
- [ ] [[HRIS - Personalia]]
- [ ] [[HRIS - Recruitment]]
- [ ] [[HRIS - Training Program]]
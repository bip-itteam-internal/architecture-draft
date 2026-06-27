## Deskripsi

*Matriks keterkaitan antar-subsistem HRIS — menunjukkan bagaimana tiap subsistem saling memberi/mengambil data, agar ketergantungan terlihat jelas. Diturunkan dari relasi yang sudah ada di dokumen-dokumen HRIS.*

- **Status**: 🟡 Draft / Direncanakan

## Catatan

Hampir semua subsistem bertumpu pada **master data karyawan** ([[Microservices - Employee Service]]) sebagai referensi, dan banyak yang berujung ke **Attendance** & **Payroll**.

## Matriks Keterkaitan

| Subsistem | Mengambil data dari | Memberi data ke |
|---|---|---|
| [[HRIS - Attendance System]] | Employee (master, jadwal); penyesuaian dari Leave/Shift/Correction | [[HRIS - Payroll]] (jam kerja, telat, lembur, cuti) |
| [[HRIS - Leave Request]] | Employee (supervisor, kuota cuti) | Attendance (status cuti/izin), decrement kuota |
| [[HRIS - Tukar Jadwal Kerja]] | Employee, jadwal | Attendance (tukar hari/shift) |
| [[HRIS - Attendance Correction]] | Attendance (entri), Employee | Attendance (koreksi clock-in/out) |
| [[HRIS - Payroll]] | Attendance, KPI/insentif, Employee (gaji/BPJS) | Slip gaji / proses penggajian |
| [[HRIS - Key Performance Index]] | Employee, target/KPI template | Payroll/insentif (skor kinerja) |
| [[HRIS - Recruitment]] | Employee (master posisi/dept) | Onboarding → karyawan aktif (handoff) |
| [[HRIS - Personalia]] | Employee (kontrak/BPJS/personal) | Attrition (terminasi), notif PKWT |
| [[HRIS - Attrition]] | Personalia/off-boarding, Employee | Dashboard attrition (pelaporan) |
| [[HRIS - Analysis]] | Seluruh siklus (recruitment→retention→off-boarding) | Dashboard lifecycle karyawan |

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]]
- [[Microservices - Employee Service]] (master data — tumpuan semua subsistem)
- [[HRIS - Attendance System]] · [[HRIS - Payroll]]

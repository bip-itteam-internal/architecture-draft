## Deskripsi

*Pengajuan cuti & izin (leave request) adalah alur **"pengajuan ke HR"** inti: karyawan mengajukan ketidakhadiran/izin secara digital, melalui rantai persetujuan **Supervisor → HR**, dan begitu disetujui otomatis menyesuaikan data kehadiran. Ini fondasi yang pola review-nya dipakai juga oleh [[HRIS - Shift Exchange]] dan [[HRIS - Attendance Correction]] — semuanya turunan dari [[HRIS - Employee Request & Approval]].*

## Latar Belakang

* Karyawan perlu mengajukan sakit, izin, cuti, atau perjalanan dinas dengan jejak yang bisa dilacak (bukan lewat chat/manual ke HR).
* Pengajuan digital memberi: validasi jenis & durasi, cek kuota cuti, persetujuan berjenjang, dan penerapan otomatis ke attendance.
* Diajukan dari [[APP - Mobile Application]] (menu Submission) dan diproses oleh [[Microservices - Attendance Service]].

## Jenis Pengajuan

Ada 4 jenis (`LeaveType`) dengan subtipe & batas durasi (`max_range`, format hari/jam; `-1` = bebas, `0` = hanya hari/jam yang sama):

| Jenis | Subtipe (contoh) | Batas |
|---|---|---|
| **Sakit** | Ada surat keterangan dokter; Tanpa surat keterangan dokter | bebas (hari) |
| **Izin** | Tidak masuk kerja (maks 2 hari); Meninggalkan pekerjaan sementara (maks 6 jam); Pulang cepat (hari sama) | hari/jam |
| **Cuti** | Cuti tahunan (cek kuota); Pernikahan (5h); Pernikahan anak (3h); Melahirkan/keguguran (90h); Istri melahirkan/keguguran (3h); Pemakaman anggota keluarga (5h); Wisuda (1h); Pemakaman saudara kandung (1h); Sunat/baptis (2h); Panggilan instansi pemerintah; Bencana alam | per subtipe |
| **Dinas** | Menghadiri rapat; Mengunjungi instansi; Seminar/khusus; Pemasaran/marketing program; Pembelian barang/jasa; Kegiatan sosial; Antar jemput | hari |

## Model Data

Koleksi: `leave_request` (di database attendance)

```
DailyLeaveRequest {
  _id            ObjectID
  employee_id    string
  full_name / position / department
  leave_type     LeaveType   // Sakit | Izin | Cuti | Dinas
  leave_subtype  string      // salah satu subtipe valid di atas
  (tanggal/durasi, dokumen pendukung, reason)

  status         ReviewStatus // diturunkan dari SpvReview + HRReview
  spv_status     ReviewData   // review Supervisor
  hr_status      ReviewData   // review HR
}
```

Menggunakan kembali `ReviewData` & `ReviewStatus` dari domain attendance.

## Penentuan Reviewer

Rantai **2 tingkat**: **Supervisor departemen → HR**. Supervisor dideteksi via `getSupervisorData(department)`.

## Resolusi Status Review

`ResolveLeaveRequestStatus(spv, hr)`:
- Salah satu **menolak** → `Ditolak`
- Salah satu **mengabaikan** → `Diabaikan`
- **Keduanya menyetujui** → `Disetujui`
- Selain itu → `Menunggu persetujuan`
- Karyawan dapat **membatalkan** pengajuan sendiri yang masih pending → `Dibatalkan`

## Aturan / Validasi

- Jenis & subtipe harus valid (`IsLeaveRequestTypeValid` / `IsLeaveRequestSubtypeValid`)
- Durasi dibatasi `max_range` per subtipe (mis. Melahirkan/keguguran 90 hari, Izin "Tidak masuk kerja" maks 2 hari, "Pulang cepat" hari yang sama)
- **Cuti tahunan**: cek & **decrement kuota** lewat [[Microservices - Employee Service]] (`/vacation/decrement`)
- Dokumen pendukung di-upload via [[Microservices - File Service]] (mis. surat dokter)

## Endpoint API

Semua di bawah **Attendance Service** (`/api/attendance/...`), diproxy lewat [[CORE - API Master Gateway]].

| Metode | Route | Keterangan |
|--------|-------|------------|
| POST | `/request/create` | Buat pengajuan (multipart + upload dokumen) |
| GET | `/request/view?as=reviewer\|reviewed` | Lihat pengajuan (sebagai pengaju / reviewer) |
| PATCH | `/request/review` | SPV/HR approve atau reject |
| PATCH | `/request/cancel` | Batalkan pengajuan pending milik sendiri |
| GET | `/request/security-lookup` | Satpam cari pengajuan (RequireSecurity) |
| PATCH | `/request/security-verify` | Satpam verifikasi keluar/kembali (RequireSecurity) |

## Alur Persetujuan

```
Karyawan buat pengajuan
   └── Notif SPV departemen
        └── SPV setuju? ──tidak──> Ditolak (notif karyawan)
              └── ya → Notif HR
                    └── HR setuju? ──tidak──> Ditolak
                          └── ya → Disetujui → terapkan ke attendance
```

Untuk izin yang meninggalkan kantor (mis. "Meninggalkan pekerjaan sementara"/"Pulang cepat"), **satpam** memverifikasi waktu keluar/kembali via `security-verify`.

## Pasca-Persetujuan (Dampak ke Attendance)

`ResolveAttendanceStatusFromLeaveRequest` memetakan pengajuan yang disetujui ke status kehadiran: **Sakit→Sick, Izin→Izin, Cuti→Vacation, Dinas→Dinas**. Catatan: **Sakit tanpa surat dokter** diperlakukan sebagai **Izin**. Penerapan terjadi otomatis saat pra-generate entry attendance oleh cron; kuota cuti di-decrement.

## Notifikasi

Push **FCM + inbox** via [[Microservices - Notification Service]] pada event: pengajuan baru (ke reviewer), disetujui/ditolak (ke karyawan).

## Implementasi Frontend

- **Mobile** ([[APP - Mobile Application]] — Submission): pilih jenis & subtipe, isi tanggal/durasi, upload dokumen, lihat status & kuota cuti
- **Web/HRIS**: HR & supervisor mereview/menyetujui pengajuan dari modul kehadiran ([[APP - Web Application]])

## Kebutuhan

- [x] Master data karyawan (referensi lookup, data supervisor)
- [x] Akses baca/tulis database attendance
- [x] Kuota cuti dari employee service
- [x] Notification service (FCM + inbox)
- [x] File service (upload dokumen pendukung)

## Dependensi

- [x] [[HRIS - Attendance System]]
- [x] [[Microservices - Attendance Service]]
- [x] [[Microservices - Employee Service]]
- [x] [[HRIS - Big Pictures]]

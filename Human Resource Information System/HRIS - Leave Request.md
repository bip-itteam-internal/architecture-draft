## Deskripsi

*Pengajuan cuti & izin (leave request) adalah alur **"pengajuan ke HR"** inti: karyawan mengajukan ketidakhadiran/izin secara digital, melalui rantai persetujuan **Supervisor → HR**, dan begitu disetujui otomatis menyesuaikan data kehadiran. Ini fondasi yang pola review-nya dipakai juga oleh [[HRIS - Tukar Jadwal Kerja]] dan [[HRIS - Attendance Correction]] — semuanya turunan dari [[HRIS - Employee Request & Approval]].*

## Latar Belakang

* Karyawan perlu mengajukan sakit, izin, cuti, atau perjalanan dinas dengan jejak yang bisa dilacak (bukan lewat chat/manual ke HR).
* Pengajuan digital memberi: validasi jenis & durasi, cek kuota cuti, persetujuan berjenjang, dan penerapan otomatis ke attendance.
* Diajukan dari [[APP - MyBharata]] (menu Submission) dan diproses oleh [[Microservices - Attendance Service]].

## Jenis Pengajuan

Ada 4 jenis (`LeaveType`) dengan subtipe & batas durasi (`max_range`, format hari/jam; `-1` = bebas, `0` = hanya hari/jam yang sama):

| Jenis | Subtipe (contoh) | Batas |
|---|---|---|
| **Sakit** | Ada surat keterangan dokter; Tanpa surat keterangan dokter | bebas (hari) |
| **Izin** | Tidak masuk kerja (maks 2 hari); Meninggalkan pekerjaan sementara — **urusan kantor** / **urusan pribadi** (maks 6 jam); Pulang cepat (hari sama) | hari/jam |
| **Cuti** | Cuti tahunan (cek kuota); Pernikahan (5h); Pernikahan anak (3h); Melahirkan/keguguran (90h); Istri melahirkan/keguguran (3h); Pemakaman anggota keluarga (5h); Wisuda (1h); Pemakaman saudara kandung (1h); Sunat/baptis (2h); Panggilan instansi pemerintah; Bencana alam | per subtipe |
| **Dinas** | Menghadiri rapat; Mengunjungi instansi; Seminar/khusus; Pemasaran/marketing program; Pembelian barang/jasa; Kegiatan sosial; Antar jemput | hari |

### Izin Meninggalkan Pekerjaan: Kantor vs Pribadi (payroll)

Izin **"Meninggalkan pekerjaan sementara"** dipecah dua subtipe, dibedakan **perlakuan bayar** (`Paid`) di master `payroll_subtype_treatment` per-(status, subtipe) — **bukan** di `LeaveSubtypeDetail` (yang hanya `MaxRange`+`Format`). Keputusan HR 2026-06-26:

- **urusan kantor** → default **`Paid: true`** (via `paidSubtypeOverrides`, `services/attendance/payroll_treatment.go`) → jam izin **dihitung sebagai kerja, tidak memotong** tunjangan/payout, walau Izin secara default dipotong.
- **urusan pribadi** → **`Paid: false`** (mengikuti default status Izin) → jam izin **memotong** tunjangan kehadiran & uang makan.

Mekanisme: entri kehadiran membawa `leave_subtype`; saat payout dihitung (`computePayoutBreakdown` / `/payroll-supplement`), `paidForEntry` menerapkan override per-(status,subtipe) di atas per-status — subtipe `Paid` tidak menurunkan `payout_pct`. **Tidak ada** field `paid_leave_hour`; jam tetap di `leave_hour`, perlakuan bayar ditentukan master treatment (editable HR, tab "Perlakuan Kehadiran"). Detail: [[Microservices - Attendance Service]] · [[HRIS - Payroll]].

Pembedaan ini juga tampil di **Laporan Kehadiran** (FE): izin urusan kantor dibedakan dari izin pribadi (`I`) lewat `leave_subtype` yang ikut dikembalikan `GET /report`, dan di grid ditandai **warna hijau** + entri legend `IK`. Karena IK bersifat partial-day (karyawan tetap clock-in), **sel grid menampilkan jam clock-in/out** — bukan kode `IK`; kode `IK` dipakai hanya sebagai fallback bila jam tak ada. Status izin pribadi (`I`) tak berubah. Logika: `erp-frontend` `report/helper/report.ts` → `buildAttendanceCell`.

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

### Auto-Ignore & Reminder

- **Auto-ignore 24 jam**: pengajuan masih `Menunggu` >24 jam sejak dibuat (`metadata.created_at`) **otomatis diabaikan** via cron `cronAutoIgnoreStaleRequest` (tiap jam) — `status` & review yang menunggu (`spv_status`/`hr_status`) → `Diabaikan` + catatan; pemohon dinotifikasi (`pushEmployeeLeaveRequestIgnored`).
- **Reminder reviewer (T+18 jam)**: **6 jam sebelum** batas, reviewer yang masih menunggu diingatkan **sekali** via cron `cronRemindStalePendingLeaves` — supervisor bila di `spv_status`, HR bila di `hr_status`. Pola sama persis dengan [[HRIS - Attendance Correction]].

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

- **Mobile** ([[APP - MyBharata]] — Submission): pilih jenis & subtipe, isi tanggal/durasi, upload dokumen, lihat status & kuota cuti
- **Web/HRIS**: HR & supervisor mereview/menyetujui pengajuan dari modul kehadiran ([[APP - Web ERP]])

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

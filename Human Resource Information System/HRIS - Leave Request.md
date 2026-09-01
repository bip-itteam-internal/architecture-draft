## Deskripsi

*Pengajuan cuti & izin (leave request) adalah alur **"pengajuan ke HR"** inti: karyawan mengajukan ketidakhadiran/izin secara digital, melalui rantai persetujuan **Supervisor → HR**, dan begitu disetujui otomatis menyesuaikan data kehadiran. Ini fondasi yang pola review-nya dipakai juga oleh [[HRIS - Tukar Jadwal Kerja]] dan [[HRIS - Attendance Correction]] — semuanya turunan dari [[HRIS - Employee Request & Approval]].*

- **Status**: ✅ Implemented — pengajuan cuti/izin + approval Supervisor→HR + auto-apply ke attendance ([[APP - MyBharata]] + [[Microservices - Attendance Service]]). · ⚠️ **Kuota cuti tahunan TIDAK punya penerbit apa pun**: angkanya diketik HR per orang, dan kuota 0 membuat pengajuan `Cuti tahunan` ditolak 400 — lihat §Kuota Cuti Tahunan dan [[ADR - 0061 Jatah Cuti Tahunan Terbit Otomatis di Ulang Tahun Kontrak]].

## Latar Belakang

* Karyawan perlu mengajukan sakit, izin, cuti, atau perjalanan dinas dengan jejak yang bisa dilacak (bukan lewat chat/manual ke HR).
* Pengajuan digital memberi: validasi jenis & durasi, cek kuota cuti, persetujuan berjenjang, dan penerapan otomatis ke attendance.
* Diajukan dari [[APP - MyBharata]] (menu Submission) dan diproses oleh [[Microservices - Attendance Service]].

## Jenis Pengajuan

Ada 4 jenis (`LeaveType`) dengan subtipe & batas durasi (`max_range`, format hari/jam; `-1` = bebas, `0` = hanya hari/jam yang sama):

| Jenis | Subtipe (contoh) | Batas |
|---|---|---|
| **Sakit** | Ada surat keterangan dokter (**satu-satunya**) | bebas (hari) |
| **Izin** | Tidak masuk kerja (maks 2 hari); Meninggalkan pekerjaan sementara — **urusan kantor** / **urusan pribadi** (maks 6 jam); Pulang cepat (hari sama) | hari/jam |
| **Cuti** | Cuti tahunan (cek kuota); Pernikahan (5h); Pernikahan anak (3h); Melahirkan/keguguran (90h); Istri melahirkan/keguguran (3h); Pemakaman anggota keluarga (5h); Wisuda (1h); Pemakaman saudara kandung (1h); Sunat/baptis (2h); Panggilan instansi pemerintah; Bencana alam | per subtipe |
| **Dinas** | Menghadiri rapat; Mengunjungi instansi; Seminar/khusus; Pemasaran/marketing program; Pembelian barang/jasa; Kegiatan sosial; Antar jemput | hari |

### ⛔ Sakit WAJIB berlampiran, dan subtipe "Tanpa surat keterangan dokter" sudah DIHAPUS

Sakit kini hanya punya **satu** subtipe. Subtipe `Tanpa surat keterangan dokter` dicabut dari
katalog (`LeaveSubtypes`, `shared-library/models/attendance/models.go`), dan pengajuan Sakit
tanpa berkas ditolak **400 `Pengajuan Sakit wajib menyertakan surat keterangan dokter`**
(`services/attendance/main.go`, penjaga `len(form.File["file"]) == 0`, reject code
`RejectSickNoAttachment`). Sakit tanpa surat kini diajukan sebagai **Izin**, bukan sebagai
Sakit bersubtipe.

⚠️ **Yang tetap hidup dan jangan dihapus**: `ResolveAttendanceStatusFromLeaveRequest` masih
memetakan subtipe lama itu ke **Izin** (dipotong), karena record lama dan in-flight bisa masih
memakainya dan payout historis harus tetap benar. Dikunci test di
`payroll_treatment_test.go`. Jadi subtipe itu **tak bisa diajukan lagi** tetapi **masih bisa
dibaca**; keduanya benar sekaligus, dan menyamakannya akan merusak salah satu sisi.

**Lampirannya selalu gambar.** Satu-satunya jalur unggah di [[APP - MyBharata]] memakai
`ImagePicker` (kamera/galeri), dipakai jalur karyawan maupun jalur HR, jadi belum pernah ada
cara mengirim PDF. Layar yang menampilkan lampiran memang berasumsi gambar.

**Dokumen fisiknya tak punya jejak di sistem.** Foto yang diunggah tidak menggantikan surat
asli, dan tak ada satu pun status atau field yang merekam apakah surat itu sudah diterima HRD.
Sejak 2026-09-01 formulir pengajuan menampilkan kartu pengingat menyerahkannya ke ruang HRD
(`SickNoteReminderCard`), tetapi itu **pengingat, bukan penjejak** — kepatuhannya tetap
diurus di luar sistem. Perlu diketahui: kalimat itu **tidak ada** di ketentuan resmi
`assets/markdown/submission/id/sakit_terms.md`, jadi kartunya sendiri satu-satunya tempat
aturan itu muncul.

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
- Dokumen pendukung di-upload via [[Microservices - File Service]]. **Opsional untuk semua jenis KECUALI Sakit**, yang ditolak 400 bila berkasnya kosong (lihat §Sakit WAJIB berlampiran)

## Kuota Cuti Tahunan

Aturan bisnisnya (Pasal 15 Peraturan Perusahaan 2026-2028) **tidak ada di vault ini**. Ia hidup di repo mobile: `mybharata-app/docs/policy/leave_terms.md` dan `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`, dan dokumen kedua dinyatakan **menang** atas perilaku sistem. Ringkasnya: 12 hari kerja setelah 12 bulan bekerja dihitung sejak kontrak setelah evaluasi, tambah 2 hari bagi masa kerja ≥5 tahun, hangus akhir tahun berikutnya, dan **Cuti Bersama memotong jatah**.

### Keadaan sekarang (grounded)

Saldo disimpan di `work_data.vacation` (employee service), bukan di database attendance:

```
Vacation { available bool; quota int; used int; history []time.Time }
```

- **Tidak ada penerbit hak sama sekali.** Satu-satunya penulis `quota` adalah `POST /vacation/quota`, dipanggil hanya dari modal edit per baris di layar Kelola Cuti ([[APP - Web ERP]]).
- `cronResetAnnualLeave` (1 Januari 00:05 WIB, [[IT - Background Jobs & Schedulers]]) **bukan** pemberi jatah: filternya `vacation.quota > 0` dan isinya hanya menyetel `used=0, available=true, history=[]`. Karyawan berkuota 0 dilewati selamanya, dan sisa cuti hangus **satu tahun lebih cepat** dari yang diatur.
- Gerbang di attendance menolak `Cuti tahunan` dengan **400 `Annual leave (vacation) quota has not been set, contact HR`** (kode `VACATION_QUOTA_UNSET`) begitu kuotanya 0.
- Pemotongan menghitung **hari kalender**, bukan hari kerja, sehingga cuti Jumat sampai Senin memotong 4 hari padahal jatahnya dinyatakan dalam hari kerja.
- **Cuti Bersama tidak menyentuh saldo.** Pemotongan hanya terjadi untuk `LeaveType = Cuti` dengan subtipe persis `Cuti tahunan`.

### ⛔ `vacation.quota` BUKAN jatah tahunan

Ia menyimpan **sisa setelah Cuti Bersama dipotong**, dan pemotongan itu dikerjakan HR di luar sistem. Pengukuran produksi 2026-08-29: 123 dari 180 karyawan aktif berkuota **5**, tak seorang pun 12 atau 14. Angka itu bukan pelanggaran Pasal 15 melainkan hasil hitungan:

```
12 hari kerja (jatah Pasal 15)  -  7 hari kerja (Cuti Bersama 2026)  =  5
```

Delapan tanggal bertipe `Cuti Bersama` tercatat di `company_holiday` untuk BIP tahun 2026 (20 sampai 26 Maret dan 28 Mei); satu di antaranya Minggu, sehingga tujuh hari kerja. **Jangan menyimpulkan perusahaan hanya memberi 5 hari**, dan jangan menjumlahkan `quota` dengan jatah Cuti Bersama karena keduanya bukan komponen sejajar.

### Celah lain yang terukur (2026-08-29)

| Temuan | Angka |
|---|---|
| Sudah ≥12 bulan tetapi kuota kosong | 15 orang |
| Belum 12 bulan tetapi sudah berkuota | 23 orang |
| Masa kerja ≥5 tahun yang seharusnya dapat tambahan 2 hari | 2 orang, tak seorang pun menerimanya |
| `work_data.join_date` bertipe `string`, bukan `date` | 89 dari 180 |
| Karyawan aktif tanpa `work_data` | 2 |

⛔ Baris keempat adalah jebakan: MongoDB tidak membandingkan lintas tipe BSON, jadi filter `{join_date: {$lt: <Date>}}` **melewati separuh karyawan tanpa satu pun galat**. `employee_contract.start_date` sebaliknya 225 dari 225 bertipe `date`.

### Rencana

Penerbitan otomatis di ulang tahun kontrak, cron harian idempoten, dan saldo pindah ke ledger kejadian: [[ADR - 0061 Jatah Cuti Tahunan Terbit Otomatis di Ulang Tahun Kontrak]]. Belum ada di kode.

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

`ResolveAttendanceStatusFromLeaveRequest` memetakan pengajuan yang disetujui ke status kehadiran: **Sakit→Sick, Izin→Izin, Cuti→Vacation, Dinas→Dinas**. Catatan: **Sakit bersubtipe "Tanpa surat keterangan dokter"** diperlakukan sebagai **Izin** — kini murni jalur backward-compat untuk record lama, sebab subtipe itu tak bisa diajukan lagi (§Sakit WAJIB berlampiran). Penerapan terjadi otomatis saat pra-generate entry attendance oleh cron; kuota cuti di-decrement.

## Notifikasi

Push **FCM + inbox** via [[Microservices - Notification Service]] pada event: pengajuan baru (ke reviewer), disetujui/ditolak (ke karyawan).

## Implementasi Frontend

- **Mobile** ([[APP - MyBharata]] — Submission): pilih jenis & subtipe, isi tanggal/durasi, upload dokumen, lihat status & kuota cuti. Unggahannya lewat `ImagePicker` (kamera/galeri) di satu-satunya widget yang dipakai jalur karyawan maupun jalur HR, jadi isi `document.file_object` **selalu gambar** — belum pernah ada jalur yang bisa mengirim PDF.
- **Mereview juga terjadi di mobile, bukan hanya di web.** Atasan langsung dan HRD menyetujui/menolak dari inbox peninjau lintas jenis (`/hr/requests` + `/hr/requests/detail`, `?as=reviewer|reviewed`). Baris ini dulu menyebut review hanya ada di Web/HRIS, dan kekeliruan itu membuat satu celah masuk akal untuk terlewat: layar detail peninjau mobile **tak pernah merender lampiran** sejak widget-nya dibuat, padahal server mengirim `document.file_object` ke peninjau sama utuhnya seperti ke pemohon. Gagalnya senyap — layarnya tampak lengkap, sehingga cuti sakit bisa diputuskan tanpa suratnya pernah dilihat. Diperbaiki 2026-09-01 di `ReviewerSubmissionInfo`.
- **Web/HRIS**: HR & supervisor mereview/menyetujui pengajuan dari modul kehadiran ([[APP - Web ERP]]); lampiran tampil lewat `useDocumentPreview` di `features/hris/requests/components/detail-sections.tsx`.

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

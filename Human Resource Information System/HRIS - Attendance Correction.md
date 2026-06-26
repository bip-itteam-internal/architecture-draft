## Deskripsi

*Fitur ini ditambahkan sebagai pelengkap Attendance System. Koreksi Absen memungkinkan karyawan mengajukan koreksi clock-in/out untuk hari di mana mereka lupa clock-in, clock-out, atau keduanya. Waktu clock otomatis diisi dari jadwal kerja karyawan saat disetujui — tidak perlu input waktu manual.*

## Latar Belakang

* Karyawan terkadang lupa melakukan clock-in atau clock-out, yang mengakibatkan catatan kehadiran tidak lengkap (status "Tanpa Keterangan" / Alpha).
* Sebelumnya, koreksi ditangani secara informal melalui HR tanpa jejak audit yang bisa dilacak.
* Fitur koreksi absen menyediakan alur formal: pengajuan digital, persetujuan multi-level, dan perbaikan data kehadiran otomatis.
* Waktu clock diambil dari jadwal kerja karyawan (`WorkTime.Start` / `WorkTime.End`), sehingga koreksi selalu konsisten dengan shift yang ditugaskan.

## Kasus Penggunaan

1. **Lupa clock-in** — Karyawan hadir tapi lupa clock-in. Koreksi mengisi `clock_in` dari jam mulai jadwal.
2. **Lupa clock-out** — Karyawan hadir tapi lupa clock-out. Koreksi mengisi `clock_out` dari jam selesai jadwal.
3. **Lupa keduanya** — Karyawan hadir seharian tapi tidak clock-in maupun clock-out. Koreksi mengisi keduanya dari jadwal.
4. **Sengketa/koreksi telat** — Karyawan sudah clock-in tapi status **Late** (mis. salah rekam mesin / ada alasan). Boleh ajukan koreksi clock-in; bila disetujui review → status jadi Tepat Waktu. **Dibatasi anti-fraud**: ditolak bila keterlambatan sudah diverifikasi security di buku tamu (lihat §Aturan Validasi & Anti-Fraud).

## Model Data

Koleksi: `attendance_correction_request` (di dalam database attendance)

```
AttendanceCorrectionRequest {
  _id:              ObjectID
  employee_id:      string
  full_name:        string
  position:         string
  department:       string

  attendance_id:    ObjectID       // Referensi ke entri kehadiran yang dikoreksi
  attendance_date:  Date           // Tanggal entri kehadiran
  work_time:        WorkTime       // { start: "HH:MM", end: "HH:MM" } — snapshot jadwal

  correction_type:  CorrectionType // "checkin" | "checkout" | "both"
  reason:           string

  status:           ReviewStatus   // Diturunkan dari review_1 + review_2
  review_1:         ReviewData     // Reviewer pertama (SPV departemen atau SPV HR)
  review_2:         ReviewData     // Reviewer kedua (departemen HR), bisa kosong

  metadata:         Metadata       // created_at, created_by, updated_at, updated_by
}
```

Menggunakan kembali tipe `ReviewData`, `ReviewStatus`, `WorkTime`, dan `CorrectionType` dari domain attendance.

### Label Tipe Koreksi

| Nilai      | Label               |
|------------|---------------------|
| `checkin`  | Clock-in            |
| `checkout` | Clock-out           |
| `both`     | Clock-in & Clock-out|

### Resolusi Status Review

Status dihitung dari dua review melalui `ResolveLeaveRequestStatus(review_1, review_2)`:
- Jika **salah satu** reviewer menolak -> `Ditolak`
- Jika review_2 **kosong/tidak berlaku** dan review_1 disetujui -> `Disetujui`
- Jika **keduanya** disetujui -> `Disetujui`
- Selain itu -> `Menunggu persetujuan`

Karyawan juga dapat membatalkan pengajuan mereka sendiri yang masih pending, yang mengubah `status` menjadi `Dibatalkan`.

### Auto-Ignore (Pengajuan Basi)

Pengajuan yang masih `Menunggu` lebih dari **24 jam** sejak dibuat (`metadata.created_at`) akan **otomatis diabaikan** oleh sistem via cron `cronAutoIgnoreStaleRequest` (jalan tiap jam): `status` → `Diabaikan`; review yang masih menunggu (`review_1`/`review_2`) ditandai `Diabaikan` + catatan "Pengajuan koreksi diabaikan oleh sistem (melebihi 24 jam)"; dan pemohon menerima notifikasi (`pushEmployeeCorrectionIgnored`). Aturan **sama persis** dengan [[HRIS - Leave Request]] (basis `created_at`, ambang 24 jam).

## Penentuan Reviewer (4 Kasus)

Reviewer ditentukan secara dinamis berdasarkan peran dan departemen pemohon. Deteksi supervisor menggunakan `getSupervisorData(department)` untuk menentukan supervisor yang sebenarnya.

| Kasus | Peran Pemohon       | Review 1                                | Review 2        | Keterangan                                  |
|-------|---------------------|-----------------------------------------|-----------------|---------------------------------------------|
| 1     | Karyawan biasa      | SPV departemen (level departemen)       | Departemen HR   | Alur 2-tier standar                         |
| 2     | SPV (non-HR)        | *(dilewati)*                            | Departemen HR   | Langsung ke HR, skip review_1               |
| 3     | Staff HR            | SPV HR (level departemen)               | *(tidak ada, FINAL)* | Persetujuan SPV HR bersifat final      |
| 4     | SPV HR              | *(otomatis disetujui)*                  | *(tidak ada)*   | Langsung diterapkan, tanpa perlu persetujuan |

### Aturan Penting

- **Pencegahan self-approval**: Staff HR tidak bisa menyetujui request koreksi milik sendiri. Filter mengecualikan request di mana `employee_id == employee_id reviewer`.
- **Routing level departemen**: Untuk kasus 1 dan 3, `review_1` ditugaskan pada level departemen (`review_1.full_name = department`, `review_1.employee_id = ""`). SPV mana pun di departemen tersebut dapat mengambil review.
- **Kasus 3 bersifat FINAL**: Ketika SPV HR menyetujui request staff HR, koreksi langsung diterapkan tanpa melalui review_2.
- **Kasus 4 otomatis**: Request SPV HR sendiri langsung disetujui dan diterapkan saat pembuatan.

## Endpoint API

Semua route berada di bawah **Attendance Service** (`/api/attendance/correction/`), diproxy melalui API Gateway.

| Metode | Route                    | Deskripsi                                              |
|--------|--------------------------|--------------------------------------------------------|
| POST   | `/correction`            | Membuat request koreksi baru                           |
| GET    | `/correction/mine`       | Melihat daftar request koreksi milik sendiri            |
| GET    | `/correction`            | Melihat daftar request untuk review (`?as=reviewer` atau `?as=reviewed`) |
| PATCH  | `/correction/:id/cancel` | Membatalkan request pending milik sendiri               |
| PATCH  | `/correction/:id/review` | Menyetujui atau menolak request (body: `{ status, notes? }`) |

### Parameter Query Endpoint View

- `as=reviewer` — menampilkan request di mana pemanggil adalah reviewer saat ini (pending review)
- `as=reviewed` — menampilkan request yang sudah direview oleh pemanggil, **termasuk request yang dibatalkan** yang ditujukan ke reviewer ini
- `filter=ongoing` — request yang **masih aktif**: baru disentuh (≤48 jam) **atau** status masih `Menunggu` review.
- `filter=past` — request yang **sudah selesai**: lama tak disentuh (>48 jam) **dan** status final (`Disetujui`/`Ditolak`/`Diabaikan`/`Dibatalkan`).
- `status=<Status>` — filter berdasarkan status (pada `/correction/mine`).

> Catatan: `filter=ongoing/past` berlaku untuk `/correction/mine` & `/correction`, dan dapat dikombinasikan dengan `status`/`as` (di-AND). Berbeda dari Leave yang memakai window tanggal (`to_date`); koreksi memakai **status review** karena `attendance_date` selalu lampau.

## Alur Persetujuan

```
Karyawan membuat request
    |
    |-- Kasus 4 (SPV HR): Otomatis approve + terapkan koreksi langsung
    |
    |-- Kasus 3 (Staff HR): Notif SPV HR -> SPV setuju? -> Terapkan (FINAL)
    |
    |-- Kasus 2 (SPV non-HR): Notif dept HR -> HR setuju? -> Terapkan
    |
    |-- Kasus 1 (Biasa): Notif SPV dept -> SPV setuju?
            |-- Ya -> Notif dept HR -> HR setuju? -> Terapkan
            |-- Tidak -> Ditolak -> Notif karyawan
```

## Aturan Validasi & Anti-Fraud (Guestbook)

Saat pengajuan (`POST /correction`), urutan pemeriksaan:
1. **Window** — ≤ 7 hari dari tanggal absen, tak boleh tanggal masa depan (`validateCorrectionWindow`). *(Tidak ada penjaga tutup-buku/payroll — lihat [[HRIS - Employee Request & Approval]] §Batas Tanggal.)*
2. **Kecocokan tipe** (`validateCorrectionTypeMatch`):
   - `checkin` — clock-in kosong → boleh; clock-in **terisi** → boleh **hanya bila status `Late`** (sengketa telat); bila sudah Tepat Waktu → ditolak.
   - `checkout` — clock-out kosong (clock-in harus sudah ada).
   - `both` — clock-in & clock-out keduanya kosong.
3. **Anti-fraud guestbook** — untuk `checkin`/`both`, **ditolak** bila ada catatan keterlambatan terverifikasi security di buku tamu (`guestbook` `category="internal"`, `employee_id` & tanggal sama). Mencegah karyawan yang terbukti telat mengubah status jadi Tepat Waktu.

**Penyimpanan bukti:** record guestbook `internal` kini menyimpan `employee_id` (dari scan QR di [[APP - MyBharata]]) → dipakai mencocokkan guard. *(Forward-looking: aktif untuk record yang sudah punya `employee_id`.)*

> Pengaman berlapis: **guard guestbook (otomatis)** + **review SPV/HR (manusia)**.

## Pasca-Persetujuan: Dampak pada Attendance (`applyCorrectionToEntry`)

Ketika koreksi sepenuhnya disetujui, sistem otomatis mengubah entri kehadiran yang direferensikan:

- **Koreksi clock-in**:
  - Bila `clock_in` **kosong** (lupa absen) → isi `clock_in`=`WorkTime.Start`, `clock_in_method`="Website".
  - Bila `clock_in` **sudah terisi** (koreksi/sengketa Late) → **jam asli + method dipertahankan** (tidak ditimpa) — data kedatangan nyata tetap auditable.
  - Selalu: `status`→"Tepat Waktu", `late_hour`→0 (memaafkan keterlambatan).
- **Koreksi clock-out**: isi `clock_out`=`WorkTime.End`, `clock_out_method`="Website" (hanya bila masih kosong).
- **Keduanya**: terapkan keduanya.
- Menambahkan komentar **`"Koreksi disetujui oleh <approver>"`** — **di-append** (tidak menimpa comment lama, mis. bukti keterlambatan guestbook). `approver` = penyetuju **final** yang memicu penerapan (HR untuk karyawan biasa; SPV HR / diri sendiri untuk internal HR).
- Memperbarui metadata dengan ID approver

## Logika Filter Review (`buildCorrectionReviewFilter`)

Filter menentukan request mana yang bisa dilihat oleh reviewer:

**Tab Menunggu Review** (`reviewed=false`):
- Request di mana `review_1.employee_id` cocok dengan reviewer DAN `review_1.status` menunggu
- Request di mana `review_1` pada level departemen dan cocok dengan departemen reviewer (mengecualikan request sendiri)
- Untuk departemen HR: request di mana `review_2.status` menunggu (mengecualikan request sendiri)
- Mengecualikan request dengan `status = "Dibatalkan"`

**Tab Sudah Direview** (`reviewed=true`):
- Request di mana reviewer sudah bertindak pada review_1 atau review_2
- Cocok level departemen dengan status review yang sudah selesai
- Untuk departemen HR: cocok review_2 dengan status yang sudah selesai
- **Request yang dibatalkan**: request yang ditugaskan ke reviewer ini tapi dibatalkan oleh karyawan sebelum direview

## Notifikasi

Semua notifikasi menggunakan sistem push notification (FCM + inbox) melalui notification-service:

| Event                                | Penerima        | Channel    |
|--------------------------------------|-----------------|------------|
| SPV menyetujui karyawan biasa        | Departemen HR   | Department |
| SPV menyetujui staff HR (FINAL)      | Karyawan        | Personal   |
| HR menyetujui                        | Karyawan        | Personal   |
| Reviewer mana pun menolak            | Karyawan        | Personal   |

## Implementasi Frontend

### Halaman

| Route                                   | Halaman      | Deskripsi                                |
|-----------------------------------------|--------------|------------------------------------------|
| `/hris/attendance-correction`           | Pengajuan Saya| Karyawan melihat riwayat presensi + koreksi |
| `/hris/attendance-correction/approvals` | Review       | Reviewer menyetujui/menolak pengajuan     |

### Struktur Modul Fitur

```
src/features/hris/attendance-correction/
├── components/
│   ├── correction-actions.tsx    — Tombol dialog Approve/Reject
│   └── modal-create.tsx          — Modal pengajuan koreksi baru
├── hooks/
│   └── use-correction.ts        — React Query hooks untuk fetch/create/cancel/review
├── schemas/
│   └── correction.ts            — Skema validasi Zod
└── types/
    └── correction.ts            — Interface dan konstanta TypeScript
```

### Perilaku Frontend Penting

- Halaman Pengajuan Saya memiliki dua tampilan: **tabel** dan **kalender** (kalender interaktif dengan status kehadiran berwarna)
- Tampilan kalender menampilkan kartu detail (clock-in, clock-out, jadwal) saat tanggal dipilih
- Modal pengajuan koreksi otomatis mendeteksi clock-in/out yang kosong dan memilih tipe koreksi
- Karyawan mengajukan koreksi untuk hari yang **clock-in/out kosong** atau **clock-in terisi tapi Late** (sengketa telat). Kalender pemilih-tanggal di-feed oleh `GET /api/attendance/history?missing=clockin|clockout|any` (mengembalikan hanya tanggal kandidat; entri telat yang sudah terverifikasi guestbook tak dimunculkan)
- Tidak ada input waktu manual — modal menjelaskan bahwa waktu akan otomatis diisi dari jadwal shift saat disetujui
- Halaman Review memiliki tab: **Menunggu Review** (pending) dan **Sudah Direview** (termasuk yang dibatalkan)
- Reviewer melihat jadwal kerja pemohon (kolom "Jam Kerja") untuk konteks
- Semua tabel menggunakan pagination sisi klien dengan opsi ukuran halaman: 3 (default), 5, 10, 50

## Kebutuhan

- [x] Master data karyawan (referensi lookup, data supervisor)
- [x] Akses baca dan tulis ke database attendance
- [x] Integrasi notification service (FCM + inbox)
- [x] Data jadwal karyawan (untuk pengisian waktu clock otomatis)

## Dependensi

- [x] [[HRIS - Attendance System]]
- [x] [[HRIS - Employee Request & Approval]] *(framework induk)*
- [x] [[HRIS - Shift Exchange]] *(pola review dan infrastruktur notifikasi yang sama)*
- [x] [[Microservices - Attendance Service]]
- [x] [[HRIS - Big Pictures]]

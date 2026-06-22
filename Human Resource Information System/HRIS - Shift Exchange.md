## Catatan

*Fitur ini ditambahkan sebagai pelengkap Attendance System. Shift Exchange memungkinkan karyawan mengajukan pertukaran hari kerja/libur dalam bulan yang sama, dengan alur persetujuan multi-level. Fitur ini terutama relevan untuk karyawan berbasis shift (Security, Production, Host Live) yang juga dapat memilih slot shift berbeda pada hari yang ditukar.*

## Latar Belakang

* Karyawan terkadang perlu bekerja pada hari libur yang dijadwalkan (misalnya hari libur nasional) dan mengambil hari libur pengganti di hari lain, atau karyawan berbasis shift ingin mengubah slot shift mereka pada tanggal tertentu.
* Sebelumnya hal ini ditangani secara informal melalui HR tanpa jejak audit yang bisa dilacak.
* Fitur shift exchange menyediakan alur formal: pengajuan digital, persetujuan, dan penyesuaian kehadiran otomatis.
* Tersedia untuk **semua karyawan**, tetapi karyawan berbasis shift (Security, Production, Host Live) mendapat opsi tambahan untuk menentukan `exchange_work_time` (slot shift) yang berbeda pada tanggal tujuan.

## Kasus Penggunaan

1. **Karyawan jadwal tetap** — bekerja pada hari libur nasional (work_date) dan mendapat hari kerja libur sebagai gantinya (exchange_date). Kedua tanggal harus dalam bulan yang sama.
2. **Karyawan berbasis shift (hari sama)** — mengajukan perubahan waktu shift pada satu hari (work_date == exchange_date). Contoh: menukar dari shift pagi ke shift malam.
3. **Karyawan berbasis shift (hari berbeda)** — sama seperti kasus 1, tetapi dapat juga memilih slot shift mana yang dikerjakan melalui `exchange_work_time`.

## Model Data

Koleksi: `shift_exchange_request` (di dalam database attendance)

```
ShiftExchangeRequest {
  _id:                ObjectID
  employee_id:        string
  full_name:          string
  position:           string
  department:         string

  work_date:          Date         // Hari karyawan akan bekerja (awalnya libur)
  exchange_date:      Date         // Hari karyawan mengambil libur (awalnya kerja)
  exchange_work_time: WorkTime?    // Opsional — hanya untuk karyawan berbasis shift
                                   // { start: "HH:MM", end: "HH:MM" }

  reason:             string

  status:             ReviewStatus // Diturunkan dari review_1 + review_2
  review_1:           ReviewData   // Reviewer pertama (SPV / kepala departemen / HR)
  review_2:           ReviewData   // Reviewer kedua (HR / Direktur), bisa kosong

  metadata:           Metadata     // created_at, created_by, updated_at, updated_by
}
```

Menggunakan kembali tipe `ReviewData`, `ReviewStatus`, dan `WorkTime` dari domain attendance.

### Resolusi Status Review

Status dihitung dari dua review melalui `ResolveShiftExchangeStatus()`:
- Jika **salah satu** reviewer menolak -> `Ditolak`
- Jika **salah satu** reviewer mengabaikan -> `Diabaikan`
- Jika review_2 **kosong** dan review_1 disetujui -> `Disetujui`
- Jika **keduanya** disetujui -> `Disetujui`
- Selain itu -> `Menunggu persetujuan`

## Penentuan Reviewer

Reviewer ditentukan secara dinamis berdasarkan peran pemohon:

| Peran Pemohon          | Review 1                       | Review 2                |
|------------------------|--------------------------------|-------------------------|
| Karyawan biasa         | Kepala departemen (by dept)    | Departemen HR           |
| Supervisor             | Departemen HR                  | Direktur                |
| Staff HR               | Kepala departemen HR           | *(tidak ada)*           |
| SPV HR                 | Direktur                       | *(tidak ada)*           |

## Aturan Bisnis / Validasi

- `exchange_date` harus **minimal 2 hari** dari hari ini
- `work_date` dan `exchange_date` harus dalam **bulan yang sama**
- `exchange_work_time` **hanya** diperbolehkan untuk karyawan berbasis shift (Security, Production, Host Live)
- Jika disediakan, `exchange_work_time` harus cocok dengan salah satu slot shift yang diizinkan untuk tipe jadwal karyawan:
  - Security: `07:00-19:00`, `19:00-07:00`
  - Production: `08:00-16:00`, `16:00-00:00`, `00:00-08:00`
  - Host Live: `07:00-15:00`, `12:00-20:00`, `16:00-24:00`, `08:00-16:00`
- Untuk karyawan non-shift (jadwal tetap) di frontend:
  - `work_date` harus hari libur / tanggal merah (OFF-DUTY, NATIONAL_HOLIDAY, COMPANY_HOLIDAY, dll.)
  - `exchange_date` TIDAK boleh hari libur / tanggal merah
  - `work_date` dan `exchange_date` tidak boleh hari yang sama

## Endpoint API

Semua route berada di bawah **Attendance Service** (`/api/attendance/shift-exchange/`), diproxy melalui API Gateway.

| Metode | Route                        | Deskripsi                                             |
|--------|------------------------------|-------------------------------------------------------|
| POST   | `/shift-exchange/create`     | Membuat request shift exchange baru                   |
| GET    | `/shift-exchange/view`       | Melihat daftar request (mendukung `?as=reviewer/reviewed`, `?filter=ongoing/past`, `?id=`, `?search=`) |
| PATCH  | `/shift-exchange/review`     | Menyetujui atau menolak request (body: `{ id, status, notes? }`) |
| PATCH  | `/shift-exchange/cancel`     | Membatalkan request pending milik sendiri (query: `?id=`) |

### Parameter Query Endpoint View

- `as=reviewer` — menampilkan request di mana pemanggil adalah reviewer saat ini (pending)
- `as=reviewed` — menampilkan request yang sudah direview oleh pemanggil
- `filter=ongoing` — request yang masih aktif atau baru diperbarui
- `filter=past` — request dengan status final atau sudah lama + exchange_date sudah lewat
- `id=<hex>` — mengambil satu request berdasarkan ObjectID
- `search=<term>` — mencari berdasarkan employee_id atau full_name

## Alur Persetujuan

```
Karyawan membuat request
    |
Notif karyawan (konfirmasi) + Notif Review 1 (request baru)
    |
Review 1 menyetujui?
    |-- Ya, ada Review 2 -> Notif Review 2, tunggu
    |       |
    |   Review 2 menyetujui?
    |       |-- Ya -> Status: Disetujui -> Terapkan ke attendance
    |       |-- Tidak -> Status: Ditolak -> Notif karyawan
    |-- Ya, tanpa Review 2 -> Status: Disetujui -> Terapkan ke attendance
    |-- Tidak -> Status: Ditolak -> Notif karyawan
```

## Pasca-Persetujuan: Dampak pada Attendance (`applyApprovedShiftExchange`)

Ketika shift exchange sepenuhnya disetujui, sistem otomatis mengubah entri kehadiran:

### Pertukaran hari sama (work_date == exchange_date)
- Memperbarui `work_time` entri kehadiran yang ada ke `exchange_work_time` yang baru
- Komentar: "Shift time changed (approved shift exchange)"

### Pertukaran hari berbeda (work_date != exchange_date)

**work_date** (awalnya libur, sekarang kerja):
- Jika entri kehadiran ada -> perbarui status ke `Tepat Waktu`, set komentar, opsional perbarui `work_time`
- Jika entri tidak ada -> **insert** dokumen `AttendanceEntries` baru dengan data karyawan, jadwal, dan work time yang diambil dari jadwal asli exchange_date

**exchange_date** (awalnya kerja, sekarang libur):
- Jika entri kehadiran ada -> perbarui status ke `Replacement Day Off`
- Jika entri tidak ada -> **insert** entri baru dengan status `Replacement Day Off`

### Dampak pada Tampilan Kalender Jadwal

Fungsi `getEmployeeScheduleDateRange()` di `func.go` juga memperhitungkan shift exchange yang sudah disetujui saat membangun tampilan kalender karyawan. Fungsi ini mengambil dokumen `ShiftExchangeRequest` yang disetujui dalam rentang tanggal dan menukar tampilan jadwal/work-time sesuai, termasuk format jadwal `REPLACEMENT_DAY_OFF` untuk hari yang ditukar.

## Notifikasi

Semua notifikasi menggunakan sistem push notification (FCM + inbox) melalui notification-service:

| Event                          | Penerima           | Channel    |
|--------------------------------|--------------------|------------|
| Request dibuat                 | Pemohon            | Personal   |
| Request baru untuk review      | Reviewer (by ID)   | Personal   |
| Menunggu review HR             | Departemen HR      | Department |
| Request disetujui              | Pemohon            | Personal   |
| Request ditolak                | Pemohon            | Personal   |

## Implementasi Frontend

### Halaman

| Route                            | Halaman        | Deskripsi                                  |
|----------------------------------|----------------|--------------------------------------------|
| `/hris/shift-exchange`           | Pengajuan Saya | Karyawan melihat/membatalkan request sendiri |
| `/hris/shift-exchange/approvals` | Review         | Reviewer menyetujui/menolak request         |

### Struktur Modul Fitur

```
src/features/hris/shift-exchange/
├── components/
│   ├── approval-actions.tsx      — Tombol dialog Approve/Reject
│   ├── approval-progress.tsx     — Indikator visual tahap review
│   ├── request-form.tsx          — Form request baru dengan tampilan kalender jadwal
│   └── review-notes.tsx          — Dialog untuk melihat catatan reviewer
├── hooks/
│   ├── use-fetch.ts              — React Query hooks untuk fetch request
│   └── use-upsert.ts            — Mutation untuk create, review, cancel
├── lib/
│   └── schedule.ts              — Utilitas label/warna/format jadwal
├── schemas/
│   └── shift-exchange.ts        — Skema validasi Zod
└── types/
    └── shift-exchange.ts        — Interface TypeScript
```

### Perilaku Frontend Penting

- Form request menampilkan **kalender interaktif** dengan modifier jadwal berwarna (pagi/malam/libur/hari raya) yang diambil dari jadwal karyawan sendiri
- Untuk karyawan berbasis shift, form menampilkan **dropdown pemilih waktu shift** dengan slot waktu yang tersedia
- Karyawan non-shift memiliki validasi sisi klien yang memastikan work_date harus tanggal merah dan exchange_date tidak boleh tanggal merah
- Progress persetujuan menampilkan pipeline visual dengan indikator status berwarna per reviewer
- Jumlah pending review di-poll setiap 60 detik untuk badge sidebar
- Semua tabel menggunakan pagination sisi klien dengan opsi ukuran halaman: 3 (default), 5, 10, 50

## Kebutuhan

- [x] Master data karyawan (referensi lookup, data supervisor)
- [x] Akses baca dan tulis ke database attendance
- [x] Integrasi notification service (FCM + inbox)
- [x] Data jadwal karyawan (untuk tampilan kalender dan validasi)

## Dependensi

- [x] [[HRIS - Attendance System]]
- [x] [[Microservices - Attendance Service]]
- [x] [[HRIS - Big Pictures]]

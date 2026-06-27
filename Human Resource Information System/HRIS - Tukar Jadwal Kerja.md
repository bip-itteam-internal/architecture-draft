## Deskripsi

*Tukar Jadwal Kerja adalah payung fitur agar karyawan dapat mengubah jadwal kerjanya secara formal (digital, ada jejak audit, dengan persetujuan) — pelengkap [[HRIS - Attendance System]]. Terdiri dari dua sub-fitur: **Tukar Shift** (tukar slot jam dengan rekan) dan **Tukar Hari** (geser hari kerja/libur). Hanya untuk karyawan berbasis shift (Security, Production, Host Live) sejak keputusan HRD 2026-06-26.*

- **Stack / Path**: Attendance Service (`bip-erp/services/attendance`), koleksi `shift_exchange_request`.
- **Status**: ⚠️ **Implemented sebagian** — yang live di produksi adalah model **single-person** (pemohon menggeser jadwalnya sendiri) + guard shift-only. 🟡 **Redesign direncanakan** → pisah jadi Tukar Shift (swap antar-rekan + consent rekan) & Tukar Hari (lihat bagian "Rencana Redesign" di bawah).

> ⚠️ **Pembatasan shift-only (keputusan HRD 2026-06-26).** Guard di `POST /shift-exchange/create` (lookup `WorkSchedule` pemohon → `IsShiftBasedSchedule(GroupID)`; bila bukan shift → 403). **Gap:** web FE (`erp-frontend`) masih menyediakan flow "tukar hari" untuk karyawan non-shift yang kini ditolak BE — perlu disesuaikan (sembunyikan/nonaktifkan untuk non-shift).

## Rencana Redesign — Tukar Jadwal Kerja (🟡 Konsep)

> **Belum diimplementasikan.** Keputusan HRD 2026-06-26/27. Mulai dari "Latar Belakang" sampai "Implementasi Frontend" di bawah mendeskripsikan **model lama (single-person)** yang masih live & akan diganti oleh desain ini.

Fitur dipecah menjadi **dua sub-fitur**:

### 1. Tukar Shift — swap antar-rekan
- **Definisi**: menukar **slot jam** pada tanggal tertentu dengan **rekan** (bukan menggeser jadwal sendiri). Hanya role ber-shift.
- **Pihak**: pemohon **memilih rekan** tujuan. Agar coverage terjaga otomatis, rekan harus di **slot pool yang sama** (swap 1:1).
- **Alur (3 langkah)**: **rekan** (consent) → **atasan** → **HRD**. Rekan **menolak → batal otomatis**.
- **Dampak penerapan**: jadwal **kedua** karyawan ditukar (model lama hanya menyentuh pemohon).

### 2. Tukar Hari — geser hari, tanpa pengganti
- **Definisi**: geser **hari kerja/libur** sendiri (mis. kerja di hari libur → ambil libur pengganti). **Unilateral** — tidak melibatkan rekan/pengganti.
- **Jam kerja**: hari yang jadi masuk (`work_date`) **mewarisi jam kerja `exchange_date`** (shift ikut pindah bersama harinya), kecuali pemohon memilih slot eksplisit. *(Lihat catatan kode di bawah — implementasi sekarang belum konsisten.)*
- **Alur**: **TBD** (atasan → HRD?).

### Struktur data (redesign)
- **Satu collection** untuk kedua sub-fitur (bukan dipisah) — ~80% field + seluruh pipeline (review, notifikasi, cron, list/view) sama; pembeda cukup field `type`.
- **Rename collection**: `shift_exchange_request` → **`schedule_exchange_request`** *(perlu migrasi data; kode live masih pakai nama lama)*.
- **Discriminator** `type`: `"shift"` (swap antar-rekan) \| `"day"` (geser hari, unilateral).
- **Field baru**: `group_id` (pemohon); `partner_employee_id` / `partner_full_name` / `partner_group_id`; `partner_consent { status, responded_at, notes }`. Untuk `type:"day"` → field partner **null**.
- **Field bersama** (tetap): `employee_id`, `work_date`, `exchange_date`, `exchange_work_time?`, `reason`, `status`, `review_1` (atasan), `review_2` (HRD), `metadata`. Sub-tipe: `WorkTime { remote, start, end }`, `ReviewData { employee_id, full_name, department, status, notes, reviewed_at }`.

### Integrasi katalog hr-request (FE picker)
- ✅ **Terdaftar** di katalog `GET /data-type/hr-request` sebagai type **"Tukar Jadwal Kerja"** (sebelumnya "Tukar Shift"), dengan subtype **["Tukar Shift", "Tukar Hari"]** via `/data-type/hr-request-subtype` (`shared-library/models/attendance/models.go`). Mobile FE memuat katalog ini **dinamis** → label baru muncul otomatis tanpa ubah FE.
- **Mapping** subtype FE → discriminator `type`: *Tukar Shift* → `shift`, *Tukar Hari* → `day`.
- ⚠️ Katalog hanya **pintu picker**; handler `create` belum bercabang per `type`, dan routing FE picker → endpoint create perlu diverifikasi (bagian redesign).

### Aturan yang sudah diputuskan
- Hanya karyawan ber-shift (Security / Host Live / Production) — sudah berlaku via guard create (403).
- `exchange_date` minimal **H+3** (naik dari H+2 pada model lama).
- **Tidak boleh dibatalkan** setelah disetujui (cancel hanya saat masih menunggu).

### Sudah dijawab kode (telusur 2026-06-27)
- **Lintas-role tidak mungkin** — slot tervalidasi **per-role** di `POST /shift-exchange/create` (`main.go` ~2610: Security 2, Production 3, Host Live 4 slot berbeda). Swap inheren **same-role**. Role disimpulkan dari `GroupID` (`IsScheduleSecurity/Production/Hostlive`), bukan department/position. → TBD "role" menyusut jadi soal **lokasi** (lihat bawah).
- **Tidak ada validasi dobel-shift / rest-period** di attendance service — saat ini dobel-shift berturut **tidak dicegah** (unchecked).
- **Warehouse dikecualikan** dari shift-based — `IsShiftBasedSchedule` = Security ∨ Hostlive ∨ Production saja; `WAREHOUSE-*` (static & pattern) kena **403** walau bekerja shift.
- **Jam kerja Tukar Hari** (`applyApprovedShiftExchange`, `func.go` ~812-880): saat `work_date` **belum** punya entri → entri baru memakai **jam dari jadwal `exchange_date`** (shift ikut pindah); `exchange_date` jadi **"Replacement Day Off"**. ⚠️ **Gap**: bila entri `work_date` **sudah ada** (ter-seed cron) & tanpa slot eksplisit, hanya `status→Ontime` yang di-set — `work_time` **tidak** disetel ulang (`func.go` ~823-825) → jam bisa tetap dari entri lama (jalur insert vs update tak konsisten).

### Belum Diputuskan (TBD)
- **Coverage**: boleh swap yang membuat slot kosong? minimum staffing per slot per role?
- **Lokasi (per-site)**: swap harus **se-lokasi**? Ada varian `*-TINGGARJAYA` (site terpisah); kode **tidak** cek pool per-lokasi → swap lintas-site tak tertahan, padahal coverage per-site bisa bolong.
- **Dobel-shift**: perlu **dilarang + jeda minimum** antar-shift? (kode belum punya guard → bila ya = fitur baru).
- **Warehouse**: sengaja dikecualikan dari tukar shift, atau harus diikutkan?
- **Tukar Hari**: kerja hari libur → uang lembur / libur pengganti / keduanya? libur pengganti harus bulan sama? siapa approver-nya? **Pastikan `work_date` selalu mewarisi jam `exchange_date`** (rapikan jalur update yang tak menyetel `work_time`).
- **Approver**: detail approver per-role; apakah SPV HRD step-1 auto-approve berlaku di sini.
- **Payroll**: tunjangan shift ikut pindah ke rekan? dampak ke perhitungan keterlambatan/SP?

*(Daftar pertanyaan & jawaban lengkap ada di notulen HRD — Workspace.)*

## Latar Belakang

* Karyawan terkadang perlu bekerja pada hari libur yang dijadwalkan (misalnya hari libur nasional) dan mengambil hari libur pengganti di hari lain, atau karyawan berbasis shift ingin mengubah slot shift mereka pada tanggal tertentu.
* Sebelumnya hal ini ditangani secara informal melalui HR tanpa jejak audit yang bisa dilacak.
* Fitur shift exchange menyediakan alur formal: pengajuan digital, persetujuan, dan penyesuaian kehadiran otomatis.
* Sejak keputusan HRD 2026-06-26 **hanya untuk karyawan berbasis shift** (Security, Production, Host Live). Karyawan berbasis shift dapat menentukan `exchange_work_time` (slot shift) yang berbeda pada tanggal tujuan. *(Sebelumnya terbuka untuk semua karyawan — flow non-shift kini ditolak BE.)*

## Kasus Penggunaan

1. ~~**Karyawan jadwal tetap**~~ — **DITOLAK backend sejak HRD 2026-06-26** (hanya shift-based). Sebelumnya: bekerja pada hari libur nasional (work_date) dan mendapat hari kerja libur sebagai gantinya (exchange_date), kedua tanggal harus dalam bulan yang sama. *Web FE masih punya flow ini — perlu disesuaikan.*
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

- **Pemohon harus karyawan berbasis shift** (Security, Production, Host Live) — *keputusan HRD 2026-06-26*. Di awal `POST /shift-exchange/create`, backend lookup `WorkSchedule` pemohon lalu `IsShiftBasedSchedule(GroupID)`; bila bukan shift → **403** `tukar shift hanya untuk karyawan ber-shift (Security/Host Live/Production)`. Lookup gagal/jadwal tak ditemukan → **500**.
- `exchange_date` harus **minimal 2 hari** dari hari ini
- `work_date` dan `exchange_date` harus dalam **bulan yang sama**
- `exchange_work_time` **hanya** diperbolehkan untuk karyawan berbasis shift (Security, Production, Host Live)
- Jika disediakan, `exchange_work_time` harus cocok dengan salah satu slot shift yang diizinkan untuk tipe jadwal karyawan:
  - Security: `07:00-19:00`, `19:00-07:00`
  - Production: `08:00-16:00`, `16:00-00:00`, `00:00-08:00`
  - Host Live: `07:00-15:00`, `12:00-20:00`, `16:00-24:00`, `08:00-16:00`
- ⚠️ Untuk karyawan non-shift (jadwal tetap) di frontend *(kini **inkonsisten** — BE menolak non-shift sejak HRD 2026-06-26; aturan FE ini perlu dicabut/disembunyikan)*:
  - `work_date` harus hari libur / tanggal merah (OFF-DUTY, NATIONAL_HOLIDAY, COMPANY_HOLIDAY, dll.)
  - `exchange_date` TIDAK boleh hari libur / tanggal merah
  - `work_date` dan `exchange_date` tidak boleh hari yang sama

## Endpoint API

Semua route berada di bawah **Attendance Service** (`/api/attendance/shift-exchange/`), diproxy melalui API Gateway.

| Metode | Route                        | Deskripsi                                             |
|--------|------------------------------|-------------------------------------------------------|
| POST   | `/shift-exchange/create`     | Membuat request shift exchange baru — **403** bila pemohon bukan karyawan shift |
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

### Eksekusi & Penanganan Gagal

`applyApprovedShiftExchange` berjalan **sinkron** saat reviewer menyetujui (final), **sebelum** status review dipersist:

- Penerapan **gagal** (error update/insert Mongo) -> endpoint balas **500** dan status review **tidak** dipersist; pengajuan tetap dapat di-review ulang (mencegah kondisi "Disetujui" tapi entri absen tak berubah).
- Penerapan **sukses** -> status menjadi `Disetujui`, lalu notifikasi "disetujui" dikirim.
- Aman di-retry: update memakai `UpdateMany` (set ulang field yang sama) dan **insert hanya bila entri belum ada** (idempoten).

> Sebelumnya penerapan dijalankan *fire-and-forget* (goroutine) sehingga kegagalan tidak terlihat & notifikasi "disetujui" tetap terkirim meski absen gagal berubah. Kini disamakan dengan pola sinkron pada [[HRIS - Attendance Correction]].

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
- ⚠️ Karyawan non-shift memiliki validasi sisi klien yang memastikan work_date harus tanggal merah dan exchange_date tidak boleh tanggal merah — **kini ditolak BE (403)** sejak HRD 2026-06-26; flow non-shift di web perlu disembunyikan/dinonaktifkan
- Progress persetujuan menampilkan pipeline visual dengan indikator status berwarna per reviewer
- Jumlah pending review di-poll setiap 60 detik untuk badge sidebar
- Semua tabel menggunakan pagination sisi klien dengan opsi ukuran halaman: 3 (default), 5, 10, 50

## Kebutuhan

- [x] Master data karyawan (referensi lookup, data supervisor)
- [x] Akses baca dan tulis ke database attendance
- [x] Integrasi notification service (FCM + inbox)
- [x] Data jadwal karyawan (untuk tampilan kalender dan validasi)

## Dependensi

- [x] [[HRIS - Employee Request & Approval]] *(framework induk)*
- [x] [[HRIS - Attendance System]]
- [x] [[Microservices - Attendance Service]]
- [x] [[HRIS - Big Pictures]]

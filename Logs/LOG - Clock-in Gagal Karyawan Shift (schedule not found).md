> **Tipe:** Log operasional (temuan/insiden) — bukan dokumentasi arsitektur.
> **Tanggal:** 2026-07-02 · **Konteks arsitektur:** [[Microservices - Attendance Service]] · [[HRIS - Attendance System]] · [[HRIS - Tukar Jadwal Kerja]]

# Clock-in Gagal untuk Karyawan Shift — `404 schedule not found`

## 1. Gejala

- Mobile app (dev `10.10.10.121:6969`) saat clock-in:
  `RESPONSE[404] PATH: /api/attendance/tap?method=Mobile` → `{ "error": "schedule not found" }`.
- Terjadi pada karyawan **shift Produksi** (akun uji **Fathur Rohim**, `BIP-0025-01-23`, jadwal `PRODUCTION-0226-SHIFT-*`).
- Karyawan **BIP-REGULAR bisa clock-in normal.**

## 2. Diagnosa (grounded ke kode `main` — bukan branch fitur)

Alur `handleClockIn` (`services/attendance/main.go:3391`):

1. Ambil `work_schedule` karyawan — Fathur punya (lolos; kalau tak ada pesannya "Work schedule not found", huruf W besar).
2. Ambil **entry attendance TERBARU** tanpa filter tanggal — `filter{employee_id}` + `sort date desc` (main.go:3409–3413).
3. `scheduleID := entry.ScheduleID` (main.go:3424).
4. Lookup `company_work_schedule` by `schedule_id` → **gagal** → `404 "schedule not found"` (main.go:3427–3428; jalur clock-out serupa di main.go:3529).

Jadi `entry.ScheduleID` milik Fathur **tidak ada** di koleksi `company_work_schedule`. BIP-REGULAR lolos karena id `BIP-REGULAR` terdaftar.

## 3. Bukti

- `GET /api/attendance/schedule` & `/today?view=resolve` untuk Fathur → jadwal resolve ke **`PRODUCTION-0226-SHIFT-A/B/C`** (rotasi: SHIFT-A/B morning 08–16, SHIFT-C midnight).
- `GET /api/attendance/data-type/schedule-list` (dev) mengembalikan a.l. `BIP-REGULAR`, `PRODUCTION-GROUP-1/2/3`, **`PRODUCTION-0226-GROUP-1/2/3`**, `WAREHOUSE-TINGGARJAYA-SHIFT-A/B/C`, `HOSTLIVE-…` — **tanpa** `PRODUCTION-0226-SHIFT-A/B/C`.
  - ⚠️ *Catatan:* daftar ini campur (id jadwal statis + id group rotasi), jadi belum tentu cerminan 1:1 isi `company_work_schedule` — perlu verifikasi DB langsung (lihat §6).
- Di **kode** `services/attendance/setup.go`, `PRODUCTION-0226-SHIFT-A/B/C` **DIDEFINISIKAN** sebagai `CompanyWorkSchedule` (setup.go:293/305/317) dan dipakai rotasi (442–444), dengan `GroupID` `PRODUCTION-0226-GROUP-1/2/3` (631–645).

## 4. BUKAN dari fitur "Izin kantor/pribadi" sesi ini

Terverifikasi via git:

- Branch `feat/izin-kantor-pribadi` hanya mengubah 6 file (leave/payroll): `cron.go`, `main.go` (bagian payroll-supplement + apply-leave), `payroll.go`, `payroll_test.go`, `shared-library/models/attendance/models.go`, `models_test.go`. **Tidak menyentuh** `setup.go` (seed jadwal), `handleClockIn`, maupun `/tap`.
- Branch tsb **belum di-deploy** — dev berjalan dari `main`.
- `setup.go` terakhir diubah **2026-05-04** (perrorovic); `PRODUCTION-0226-SHIFT-A` ditambah **2026-04-13** (perrorovic). → **pre-existing**, oleh dev lain.

## 5. Hipotesis akar masalah

Karena kode seed **punya** `PRODUCTION-0226-SHIFT-B`, tapi lookup gagal di dev, kemungkinan:

- **(A)** Koleksi `company_work_schedule` di **DB dev tidak sinkron** dengan `setup.go` terkini (belum ter-seed ulang setelah id `PRODUCTION-0226-SHIFT-*` ditambах) — mis. logika seeding hanya insert bila belum ada / tak upsert, atau service belum restart.
- **(B)** Entry attendance Fathur menyimpan `schedule_id` versi lama yang sudah tidak ada di seed.
- **(C)** (desain rapuh, terpisah) `handleClockIn` mengambil **entry terbaru tanpa filter tanggal** — bila ada entry masa depan / placeholder, target salah. (Untuk kasus ini kemungkinan bukan penyebab utama, tapi patut diperbaiki.)

## 6. Belum dipastikan / langkah verifikasi

- [ ] Cek langsung isi `company_work_schedule` di DB dev: apakah `PRODUCTION-0226-SHIFT-A/B/C` ada?
- [ ] Cek entry attendance terbaru Fathur: nilai `schedule_id`-nya persis apa & tanggalnya kapan.
- [ ] Cek perilaku `setupCompanyWorkSchedule` (`setup.go:37`): insert-if-absent vs upsert/replace — menentukan apakah cukup **restart/re-deploy** attendance untuk memperbaiki.

## 7. Usulan fix (tentatif, menunggu verifikasi §6)

- Jika (A): **re-seed / restart** attendance service di dev agar `company_work_schedule` memuat definisi terkini; bila seeding tidak upsert → perbaiki agar upsert.
- Jika (B): perbaiki data `work_schedule`/entry Fathur agar merujuk `schedule_id` yang valid.
- Hardening (C): `handleClockIn` sebaiknya memilih entry **hari ini** (filter tanggal), dan/atau fallback ke `entry.WorkTime` yang sudah tersimpan alih-alih selalu query `company_work_schedule`.

## Dokumen terkait

- [[Microservices - Attendance Service]]
- [[HRIS - Attendance System]]
- [[HRIS - Tukar Jadwal Kerja]]
- [[HRIS - Leave Request]]

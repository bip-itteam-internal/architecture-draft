## Deskripsi

*Tukar Jadwal Kerja adalah payung fitur agar karyawan dapat mengubah jadwal kerjanya secara formal (digital, ada jejak audit, dengan persetujuan) — pelengkap [[HRIS - Attendance System]]. Terdiri dari dua sub-fitur: **Tukar Shift** (tukar slot jam dengan rekan) dan **Tukar Hari** (geser hari kerja/libur). Hanya untuk karyawan berbasis shift (Security, Production, Host Live) sejak keputusan HRD 2026-06-26.*

- **Stack / Path**: Attendance Service (`bip-erp/services/attendance`), koleksi **`schedule_exchange_request`** (rename dari `shift_exchange_request`).
- **Status**: ⚠️ **Implemented** (branch `feat/recruitment-service`, belum rilis). **Tukar Shift** = swap antar-rekan 3-langkah (consent → atasan → HRD) **sudah dibangun**; **Tukar Hari** = model single-person (geser hari). Lihat "Desain & Implementasi" + **Known limitation** di bawah.

> ⚠️ **Pembatasan shift-only (keputusan HRD 2026-06-26).** Guard di `POST /schedule-exchange/create` (lookup `WorkSchedule` pemohon → `IsShiftBasedSchedule(GroupID)`; bila bukan shift → 403). **Gap:** web FE (`erp-frontend`) masih menyediakan flow "tukar hari" untuk karyawan non-shift yang kini ditolak BE — perlu disesuaikan (sembunyikan/nonaktifkan untuk non-shift).

## Latar Belakang

* Karyawan terkadang perlu bekerja pada hari libur yang dijadwalkan (misalnya hari libur nasional) dan mengambil hari libur pengganti di hari lain, atau karyawan berbasis shift ingin mengubah slot shift mereka pada tanggal tertentu.
* Sebelumnya hal ini ditangani secara informal melalui HR tanpa jejak audit yang bisa dilacak.
* **Tukar Jadwal Kerja** menyediakan alur formal: pengajuan digital, persetujuan berjenjang, dan penyesuaian kehadiran otomatis — pelengkap [[HRIS - Attendance System]].
* Sejak keputusan HRD 2026-06-26 **hanya untuk karyawan berbasis shift** (Security, Production, Host Live). Karyawan berbasis shift dapat menentukan `exchange_work_time` (slot shift) yang berbeda pada tanggal tujuan. *(Sebelumnya terbuka untuk semua karyawan — flow non-shift kini ditolak BE.)*

## Desain & Implementasi — Tukar Jadwal Kerja (⚠️ Implemented)

> **Sudah dibangun** (Fase 0–2, branch `feat/recruitment-service`; keputusan HRD 2026-06-26/27). Bagian "Kasus Penggunaan"…"Implementasi Frontend" di bawah masih mendeskripsikan **model lama single-person** (diwarisi Tukar Hari); Tukar Shift swap mengikuti desain di section ini. Lihat **Known limitation & TBD** di bawah.

Fitur dipecah menjadi **dua sub-fitur**:

### 1. Tukar Shift — swap antar-rekan ✅
- **Definisi**: menukar **slot jam** pada tanggal sama dengan **rekan**. Hanya role ber-shift; **same-role dipaksa** (slot tervalidasi per-role).
- **Pihak**: pemohon **memilih rekan** (`partner_employee_id`). Validasi `validateSwapPartner` (beda orang, shift, role sama). Saat create, slot **kedua sisi** di-resolve & disimpan: pemohon `exchange_work_time` (= slot rekan), rekan `partner_work_time` (= slot pemohon).
- **Alur (3 langkah)**: **rekan** `PATCH /schedule-exchange/consent` → **atasan** (`review_1`) → **HRD** (`review_2`). Rekan **menolak → status Canceled**. Atasan/HRD **diblokir** sampai rekan menyetujui (gating). `ResolveScheduleExchangeStatus(consent, r1, r2)`.
- **Dampak penerapan**: jadwal **kedua** karyawan ditukar. **Durable** via cron seeding & kalender sadar-swap (`WorkTimeFor` per sisi: pemohon→`exchange_work_time`, rekan→`partner_work_time`); apply saat approval hanya update entri yang sudah ada (tanpa duplikasi).

### 2. Tukar Hari — geser hari, tanpa pengganti
- **Definisi**: geser **hari kerja/libur** sendiri (mis. kerja di hari libur → ambil libur pengganti). **Unilateral** — tidak melibatkan rekan/pengganti.
- **Jam kerja**: hari yang jadi masuk (`work_date`) **mewarisi jam kerja `exchange_date`** (shift ikut pindah bersama harinya), kecuali pemohon memilih slot eksplisit. *(Lihat catatan kode di bawah — implementasi sekarang belum konsisten.)*
- **Alur**: **TBD** (atasan → HRD?).

### Struktur data
- **Satu collection** untuk kedua sub-fitur (bukan dipisah) — ~80% field + seluruh pipeline (review, notifikasi, cron, list/view) sama; pembeda cukup field `type`.
- **Collection**: **`schedule_exchange_request`** ✅ (sudah di-rename dari `shift_exchange_request`; identifier Go `Collections.ShiftExchangeRequest` masih dipertahankan — kosmetik).
- **Discriminator** `type`: `"shift"` (swap antar-rekan) \| `"day"` (geser hari, unilateral); kosong → di-infer dari pasangan tanggal (`InferScheduleExchangeType`).
- **Field baru**: `type`, `group_id` (pemohon); `partner_employee_id` / `partner_full_name` / `partner_group_id` / **`partner_work_time`** (slot baru rekan); `partner_consent { status, responded_at, notes }`. Untuk `type:"day"` → field partner **null**.
- **Field bersama** (tetap): `employee_id`, `work_date`, `exchange_date`, `exchange_work_time?` (untuk swap = slot baru pemohon), `reason`, `status`, `review_1` (atasan), `review_2` (HRD), `metadata`. Sub-tipe: `WorkTime { remote, start, end }`, `ReviewData { employee_id, full_name, department, status, notes, reviewed_at }`, `ConsentData { status, notes, responded_at }`.

### Integrasi katalog hr-request (FE picker)
- ✅ **Terdaftar** di katalog `GET /data-type/hr-request` sebagai type **"Tukar Jadwal Kerja"** (sebelumnya "Tukar Shift"), dengan subtype **["Tukar Shift", "Tukar Hari"]** via `/data-type/hr-request-subtype` (`shared-library/models/attendance/models.go`). Mobile FE memuat katalog ini **dinamis** → label baru muncul otomatis tanpa ubah FE.
- **Mapping** subtype FE → discriminator `type`: *Tukar Shift* → `shift`, *Tukar Hari* → `day`.
- Handler `create` kini **bercabang per `type`+partner** (swap → consent rekan). **Mobile (MyBharata)** kini punya fitur khusus `features/schedule_exchange` yang memanggil `/schedule-exchange/*` **langsung** (kirim `type:"shift"` + `partner_employee_id`) — bukan lagi katalog `/request/*` generik (branch `feature/schedule-exchange`, **PR #78 → `dev`**). Detail di **Implementasi Frontend → Mobile**.

### Aturan yang sudah diputuskan
- Hanya karyawan ber-shift (Security / Host Live / Production) — sudah berlaku via guard create (403).
- `exchange_date` minimal **H+3** (naik dari H+2 pada model lama).
- **Tidak boleh dibatalkan** setelah disetujui (cancel hanya saat masih menunggu).
- **Auto-ignore & reminder** (konsisten leave/koreksi): pengajuan basi **>24 jam** → `Diabaikan` (termasuk tahap **consent rekan** yang tak direspons); **reminder** aktor saat ini (rekan/atasan/HRD) di **T+18 jam**. Cron `services/attendance/cron.go` (`cronAutoIgnoreStaleRequest` + `cronRemindStalePendingScheduleExchanges`).
- **Rekan swap harus se-departemen + se-lokasi (site)** — **keputusan 2026-06-28**, berlaku untuk **Tukar Shift & Tukar Hari**. **Alasan (coverage per-brand):** rotasi Host Live dirancang **"1 host per brand per shift"** — di prod tiap grup `HOSTLIVE-…-THU-OFF-P3` = **1 Beauty Hacks + 1 Kyura** (total HL prod = 8 Kyura + 3 BH). Swap **lintas-departemen** membuat satu brand **kosong** di satu shift walau headcount netral (mis. *Khilda* BH ⟷ *Helga* Kyura → shift pagi jadi 0 BH, shift malam jadi 0 Kyura). **Same-department** menjaga invariant "1 per brand per shift"; **same-site** mencegah `*-TINGGARJAYA` (Security) tercampur lintas-lokasi. Guard diterapkan **di tingkat rekan** (bukan grup — grup rotasi memang boleh campur departemen). Detail & konsekuensi: [[ADR - 0006 Swap Jadwal Same-Department]].

### Sudah dijawab kode (telusur 2026-06-27)
- **Lintas-role tidak mungkin** — slot tervalidasi **per-role** di `POST /schedule-exchange/create` (`main.go` ~2610: Security 2, Production 3, Host Live 4 slot berbeda). Swap inheren **same-role**. Role disimpulkan dari `GroupID` (`IsScheduleSecurity/Production/Hostlive`), bukan department/position. → TBD "role" menyusut jadi soal **lokasi** (lihat bawah).
- **Tidak ada validasi dobel-shift / rest-period** di attendance service — saat ini dobel-shift berturut **tidak dicegah** (unchecked).
- **Warehouse dikecualikan** dari shift-based — `IsShiftBasedSchedule` = Security ∨ Hostlive ∨ Production saja; `WAREHOUSE-*` (static & pattern) kena **403** walau bekerja shift.
- **Jam kerja Tukar Hari** (`applyApprovedShiftExchange`, `func.go` ~812-880): saat `work_date` **belum** punya entri → entri baru memakai **jam dari jadwal `exchange_date`** (shift ikut pindah); `exchange_date` jadi **"Replacement Day Off"**. ⚠️ **Gap**: bila entri `work_date` **sudah ada** (ter-seed cron) & tanpa slot eksplisit, hanya `status→Ontime` yang di-set — `work_time` **tidak** disetel ulang (`func.go` ~823-825) → jam bisa tetap dari entri lama (jalur insert vs update tak konsisten).

### Known limitation (implementasi swap — follow-up)
- **Timing pre-alokasi** *(pre-existing, kena single-person juga)*: `work_time` ter-swap benar, tapi **trigger pre-alloc & Alpha-setter** masih ikut jadwal asli → entri bisa di-seed pada waktu shift lama. Data slot benar; penjadwalan belum ideal.
- **Reviewer list** masih menampilkan swap yang menunggu consent (aksi diblok, tapi tampil) — filter `buildShiftExchangeReviewFilter` belum exclude.
- **Notif consent** ke kepala dept (`employee_id` kosong) jatuh ke HR (pola pre-existing, sama di review handler).
- **`exchange_work_time` dari user diabaikan** saat ada partner (slot di-resolve dari jadwal).
- ✅ **Guard same-department/same-site DIIMPLEMENTASI** (branch `feat/swap-same-department`): `validateSwapPartner` (`func.go` ~705) + endpoint `partners` kini cek **same-site** (`IsSameSite`, penanda Tinggarjaya) + **same-department** (fail-open bila department belum ter-sync, agar tak salah-blokir saat rollout). `Department` di-enrich ke `work_schedule` saat `/sync/work-schedules` (dari `work_data`). Detail: [[ADR - 0006 Swap Jadwal Same-Department]]. *(**✅ E2E terverifikasi di dev 2026-06-28**: picker `/partners` Khilda hanya menampilkan BH; create lintas-dept BH ⟷ Kyura ditolak 400.)*
- **Test E2E**: Tukar **Shift** ✅ **terverifikasi di dev** (2026-06-28, Production: create→consent→atasan→HRD→jadwal tertukar). Tukar **Hari** ✅ approval & presensi benar, ⚠️ **render kalender** masih bug (cabang non-sameDay `getEmployeeScheduleDateRange`).

### Belum Diputuskan (TBD)
- **Coverage (minimum staffing)**: angka minimum per slot/role/site masih perlu dikunci HRD (mis. Security ≥2/shift, Host Live ≥1 per brand/shift). Keputusan **same-department** (2026-06-28) sudah menutup coverage **per-brand**; sisa: **Tukar Hari unilateral** masih bisa menjatuhkan slot di bawah minimum.
- ~~**Lokasi (per-site)**~~ → **DIPUTUSKAN 2026-06-28**: swap harus **se-site** (lihat "Aturan yang sudah diputuskan").
- **Dobel-shift**: perlu **dilarang + jeda minimum** antar-shift? (kode belum punya guard → bila ya = fitur baru).
- **Warehouse**: sengaja dikecualikan dari tukar shift, atau harus diikutkan?
- **Tukar Hari**: kerja hari libur → uang lembur / libur pengganti / keduanya? libur pengganti harus bulan sama? siapa approver-nya? **Pastikan `work_date` selalu mewarisi jam `exchange_date`** (rapikan jalur update yang tak menyetel `work_time`).
- **Approver**: detail approver per-role; apakah SPV HRD step-1 auto-approve berlaku di sini.
- **Payroll**: tunjangan shift ikut pindah ke rekan? dampak ke perhitungan keterlambatan/SP?

*(Daftar pertanyaan & jawaban lengkap ada di notulen HRD — Workspace.)*

## Kasus Penggunaan

1. ~~**Karyawan jadwal tetap**~~ — **DITOLAK backend sejak HRD 2026-06-26** (hanya shift-based). Sebelumnya: bekerja pada hari libur nasional (work_date) dan mendapat hari kerja libur sebagai gantinya (exchange_date), kedua tanggal harus dalam bulan yang sama. *Web FE masih punya flow ini — perlu disesuaikan.*
2. **Karyawan berbasis shift (hari sama)** — mengajukan perubahan waktu shift pada satu hari (work_date == exchange_date). Contoh: menukar dari shift pagi ke shift malam.
3. **Karyawan berbasis shift (hari berbeda)** — sama seperti kasus 1, tetapi dapat juga memilih slot shift mana yang dikerjakan melalui `exchange_work_time`.

## Model Data

Koleksi: `schedule_exchange_request` (di dalam database attendance)

```
ShiftExchangeRequest {
  _id:                ObjectID
  type:               string       // "shift" (swap rekan) | "day" (geser hari); kosong -> di-infer
  employee_id:        string
  full_name:          string
  position:           string
  department:         string
  group_id:           string       // jadwal shift pemohon (validasi role/slot)

  work_date:          Date         // Hari karyawan akan bekerja (awalnya libur)
  exchange_date:      Date         // Hari karyawan mengambil libur (awalnya kerja)
  exchange_work_time: WorkTime?    // Opsional; untuk swap = slot BARU pemohon (= slot rekan)
                                   // { remote, start: "HH:MM", end: "HH:MM" }

  // Rekan tukar — hanya untuk type "shift"
  partner_employee_id: string
  partner_full_name:   string
  partner_group_id:    string
  partner_work_time:   WorkTime?   // slot BARU rekan (= slot lama pemohon)
  partner_consent:     ConsentData? // { status, notes, responded_at } — langkah 1 dari 3

  reason:             string

  status:             ReviewStatus // Diturunkan dari partner_consent + review_1 + review_2
  review_1:           ReviewData   // Atasan (SPV / kepala departemen / HR)
  review_2:           ReviewData   // HRD / Direktur, bisa kosong

  metadata:           Metadata     // created_at, created_by, updated_at, updated_by
}
```

Menggunakan kembali tipe `ReviewData`, `ReviewStatus`, `WorkTime`, dan `ConsentData` dari domain attendance. Method `WorkTimeFor(employeeID)` mengembalikan slot baru per sisi (dipakai cron seeding & kalender agar swap konsisten kedua sisi).

### Resolusi Status Review

**Tukar Hari / tanpa rekan** — `ResolveShiftExchangeStatus(r1, r2)`:
- Jika **salah satu** reviewer menolak -> `Ditolak`
- Jika **salah satu** reviewer mengabaikan -> `Diabaikan`
- review_2 **kosong** & review_1 disetujui, atau **keduanya** disetujui -> `Disetujui`
- Selain itu -> `Menunggu persetujuan`

**Tukar Shift (swap)** — `ResolveScheduleExchangeStatus(partner_consent, r1, r2)` membungkus di atas:
- `partner_consent` **menolak** -> `Dibatalkan` (batal otomatis)
- `partner_consent` **menunggu** -> `Menunggu persetujuan` (reviewer diblokir)
- `partner_consent` **disetujui** -> delegasi ke resolusi review_1/review_2 di atas

## Penentuan Reviewer

Reviewer ditentukan secara dinamis berdasarkan peran pemohon:

| Peran Pemohon          | Review 1                       | Review 2                |
|------------------------|--------------------------------|-------------------------|
| Karyawan biasa         | Kepala departemen (by dept)    | Departemen HR           |
| Supervisor             | Departemen HR                  | Direktur                |
| Staff HR               | Kepala departemen HR           | *(tidak ada)*           |
| SPV HR                 | Direktur                       | *(tidak ada)*           |

## Aturan Bisnis / Validasi

- **Pemohon harus karyawan berbasis shift** (Security, Production, Host Live) — *keputusan HRD 2026-06-26*. Di awal `POST /schedule-exchange/create`, backend lookup `WorkSchedule` pemohon lalu `IsShiftBasedSchedule(GroupID)`; bila bukan shift → **403** `tukar shift hanya untuk karyawan ber-shift (Security/Host Live/Production)`. Lookup gagal/jadwal tak ditemukan → **500**.
- **Karyawan ber-roster DITUTUP dari Tukar Jadwal** (PR #1012, [[ADR - 0036 Roster Harian Menimpa Jadwal Dasar]]). Jadwal yang sudah bebas diatur leader membuat tukar shift mubazir, dan dua jalur yang mengubah tanggal yang sama menghasilkan urutan menang yang tak bisa dijelaskan ke pemakainya. Digerbang **tiga tempat**: pemohon di `create`, **sisi rekan** di `create` (dengan pesan yang menyebut sebabnya, bukan "tidak terjadwal kerja" yang menyesatkan), dan pemohon maupun kandidat di `/partners`. Penyaringan kandidat sebelumnya bersifat kebetulan **dan berlubang**: kandidat ber-roster yang selnya belum diisi jatuh ke jadwal dasar sehingga tetap muncul sebagai rekan yang bisa ditukar.
	- Penegakannya **hanya di backend**. [[APP - MyBharata]] tidak menyembunyikan tombolnya, jadi host ber-roster tetap melihat menu Tukar Shift dan baru ditolak saat mengirim.
- `exchange_date` harus **minimal 3 hari (H+3)** dari hari ini *(naik dari H+2)*
- `work_date` dan `exchange_date` harus dalam **bulan yang sama**
- **Tukar Shift (swap)**: `partner_employee_id` wajib karyawan **shift & role sama**, bukan diri sendiri (`validateSwapPartner`); pemohon & rekan harus terjadwal kerja pada tanggal itu
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

Semua route berada di bawah **Attendance Service** (`/api/attendance/schedule-exchange/`), diproxy melalui API Gateway.

| Metode | Route                        | Deskripsi                                             |
|--------|------------------------------|-------------------------------------------------------|
| POST   | `/schedule-exchange/create`     | Membuat request — **403** bila bukan karyawan shift. Body: `{ work_date, exchange_date, reason, type?, exchange_work_time?, partner_employee_id? }`. `type:"shift"`+`partner` → swap (resolve & simpan kedua slot, `partner_consent=Waiting`) |
| PATCH  | `/schedule-exchange/consent`    | **Rekan** menyetujui/menolak swap (langkah 1). Body: `{ id, status, notes? }`. Hanya `partner_employee_id` & saat `status=Waiting`. Tolak → Canceled; setuju → lanjut ke atasan |
| GET    | `/schedule-exchange/partners`   | **Pembantu** — kandidat rekan swap pada `?date=` (role/slot sama, bukan diri sendiri, terjadwal kerja). Return `{employee_id, full_name, group_id, work_time}` |
| GET    | `/schedule-exchange/view`       | Melihat daftar request (mendukung `?as=reviewer/reviewed/partner`, `?filter=ongoing/past`, `?id=`, `?search=`). `as=partner` = inbox consent rekan *(2026-06-29)* |
| PATCH  | `/schedule-exchange/review`     | Atasan/HRD setuju/tolak (body: `{ id, status, notes? }`). **Diblokir** sampai consent rekan disetujui |
| PATCH  | `/schedule-exchange/cancel`     | Membatalkan request milik sendiri (query: `?id=`) — hanya saat status **Waiting** |

### Parameter Query Endpoint View

- `as=reviewer` — menampilkan request di mana pemanggil adalah reviewer saat ini (pending)
- `as=reviewed` — menampilkan request yang sudah direview oleh pemanggil
- `as=partner` — **(swap)** menampilkan request yang menunggu **consent** pemanggil sebagai rekan (`partner_employee_id` + `partner_consent.status=Menunggu persetujuan`) → inbox consent rekan. *(ditambah 2026-06-29, untuk mobile; tanpa ini rekan tak bisa list/akses request consent-nya karena filter default `employee_id=self`.)*
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

Ketika sepenuhnya disetujui, sistem otomatis mengubah entri kehadiran:

### Tukar Shift — swap antar-rekan (`type:"shift"` + partner)
- `applyScheduleExchangeSwap` menukar `work_time` **kedua** karyawan pada tanggal itu: pemohon → `exchange_work_time`, rekan → `partner_work_time`.
- **Hanya UPDATE** entri yang sudah ada (tak insert) → entri masa depan di-seed oleh cron yang **sadar-swap** (`WorkTimeFor`), sehingga tak ada duplikasi & slot benar di kedua sisi.

### Pertukaran hari sama — single-person (tanpa partner)
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

Fungsi `getEmployeeScheduleDateRange()` di `func.go` juga memperhitungkan shift exchange yang sudah disetujui saat membangun tampilan kalender karyawan. Filter mencakup `employee_id` **dan `partner_employee_id`** (swap terdampak kedua sisi); work-time ditentukan via `WorkTimeFor` sehingga kalender **kedua** karyawan menampilkan slot hasil swap. Termasuk format jadwal `REPLACEMENT_DAY_OFF` untuk hari yang ditukar (single-person).

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

### Mobile (MyBharata) — Tukar Shift ⚠️ (branch `feature/schedule-exchange`, PR #78 → `dev`, belum rilis)

> Bagian di atas mendeskripsikan **web** (`erp-frontend`). Mobile dibangun terpisah: fitur khusus `lib/src/features/schedule_exchange/` (Clean Architecture, **meniru pola `submission`** & **reuse core widgets** — tanpa komponen baru), memanggil `/schedule-exchange/*` **langsung** (bukan katalog `/request/*` generik). **Hanya Tukar Shift** (`type:"shift"`, `work_date==exchange_date`); Tukar Hari tidak diikutkan di mobile.

**Alur 3 aktor (mirror leave):**
- **Pemohon** — pilih `work_date` → `GET /partners` → pilih rekan (**picker komposit**: `CustomBottomSheet` + `CustomInput` search + list) → alasan → submit (`POST /create`, payload RFC3339). Riwayat (`view`) + detail + **batal** (`cancel`).
- **Rekan (consent)** — inbox tab "Persetujuan Rekan" → `GET /view?as=partner` → setuju/tolak (`PATCH /consent`). *(butuh BE `as=partner` — **bip-erp PR #172**, deploy dulu.)*
- **Atasan/HRD (review)** — inbox tab "Tinjauan" → `GET /view?as=reviewer` → setuju/tolak (`PATCH /review`).

**Catatan teknis:**
- Detail dibuka sebagai **objek** `ScheduleExchange` dari list (bukan re-fetch `?id=`) — karena `/view?id=` difilter `employee_id=self` sehingga reviewer/rekan tak bisa fetch by id.
- Entry: **2 menu** di kategori Attendance (`more_menu_page`): "Tukar Jadwal Kerja" (pemohon) + "Tinjauan Tukar Shift" (inbox consent+review).
- Status string ID (`Disetujui`/`Ditolak`/`Menunggu persetujuan`); l10n 24 key (`app_id.arb`+`app_en.arb`).
- **Verifikasi**: `dart analyze` (seluruh `lib`) bersih; **9 unit test** hijau (model `toJson` kontrak BE + BLoC form/consent/cancel via `bloc_test`+`mocktail`). ⏳ **E2E mobile belum** — perlu deploy BE PR #172 + akun shift.

## Kebutuhan

- [x] Master data karyawan (referensi lookup, data supervisor)
- [x] Akses baca dan tulis ke database attendance
- [x] Integrasi notification service (FCM + inbox)
- [x] Data jadwal karyawan (untuk tampilan kalender dan validasi)

## Dependensi

- [x] [[HRIS - Employee Request & Approval]] *(framework induk)*
- [x] [[HRIS - Attendance System]]
- [x] [[Microservices - Attendance Service]]
- [x] [[APP - MyBharata]] *(klien mobile — fitur Tukar Shift, PR #78)*
- [x] [[HRIS - Big Pictures]]

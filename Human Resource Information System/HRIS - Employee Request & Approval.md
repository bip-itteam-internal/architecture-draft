## Deskripsi

*Framework bersama untuk **pengajuan karyawan (employee request)** — pola umum: **karyawan mengajukan → review/approval berjenjang → diterapkan otomatis ke attendance**. Ini "induk" dari beberapa subsistem HRIS yang berbagi infrastruktur review yang sama (semua di attendance service). Di aplikasi mobile, turunannya dikelompokkan di menu **Submission**.*

- **Status**: ✅ Implemented (infrastruktur bersama dipakai Leave/Shift/Correction/Perjalanan Dinas; Overtime belum mengikuti pola ini)

## Turunan (jenis request)

Enam jenis HR request (Lembur menyusul). Sejak **penyeragaman 2026-07**, keempat jenis aktif memakai **model review yang sama**: field `spv_review`/`hr_review` (bson `spv_status`/`hr_status`, seragam dengan Leave), dengan **SPV di-assign spesifik** via `getSupervisorData` (slot lama `review_1`/`review_2` di Tukar & Koreksi sudah di-rename).

| Jenis (`request_type`) | Koleksi | Dokumen | Endpoint | Reviewer |
|---|---|---|---|---|
| **Izin / Cuti / Sakit** | `leave_request` | [[HRIS - Leave Request]] | `/request/*` | SPV → HRD |
| **Dinas** (Perjalanan Dinas) | `business_trip_request` | [[HRIS - Perjalanan Dinas]] | `/business-trip/*` | SPV → HRD |
| **Koreksi** clock-in/out | `attendance_correction_request` | [[HRIS - Attendance Correction]] | `/correction/*` | SPV → HRD (reguler); atasan/HR → HR |
| **Tukar** Shift/Hari | `schedule_exchange_request` | [[HRIS - Tukar Jadwal Kerja]] | `/schedule-exchange/*` | (Rekan consent — hanya Shift) → SPV → HRD |
| Lembur (SPKL) | *(belum)* | [[HRIS - Overtime]] | *(belum)* | *(rencana mengikuti pola ini)* |

## Endpoint Admin HR (lihat semua request)

Satu endpoint melihat **semua** pengajuan lintas koleksi — `services/attendance/hr_admin.go` (lihat [[Microservices - Attendance Service]]):

- `GET /hr/requests` — daftar ringkas. `request_type` **granular**: **Izin, Cuti, Sakit, Dinas, Koreksi, Tukar** (Izin/Cuti/Sakit = nilai `leave_type` pada `leave_request`). Filter: `type`, `status`, `department`, `search`, `from`, `to` + pagination `page`/`limit`. Balas `{ data, total, page, limit }` (urut `created_at` desc); `data[]` = `{ id, request_type, employee_id, full_name, department, subtype, status, created_at }`.
- `GET /hr/requests/detail?type=&id=` — full doc satu pengajuan (bypass filter per-user; admin boleh lihat semua).
- Tak berhak → `403`.

**Siapa yang berhak (sejak 2026-08-09, ADR 0030 irisan ketiga):** digerbang izin **`hris.pengajuan.view`**, dengan gerbang lama sebagai **fallback union** selama `HRIS_TIER_FALLBACK` menyala — yaitu `department == "Human Resource"` **atau** posisi **`Cost Control`** (yang terakhir baca saja, memantau biaya pengajuan; ia sudah lama ada di kode tapi tak pernah tercatat di sini). Paket bawaannya "HRIS: Pemantau Pengajuan" dan "HRIS: Penyetuju Pengajuan". Rinciannya di [[CORE - RBAC dan Permission Set]].

**Keputusan tahap HRD** (setujui/tolak di keempat jenis) digerbang **`hris.pengajuan.approve`**, fallback union `department == "Human Resource"`. Cost Control **tidak** termasuk. Perlu diketahui: sebelum ini siapa pun berdepartemen HR boleh memutuskan pengajuan siapa pun yang sudah lolos SPV, tanpa peran maupun jabatan tertentu; pembatasan sebenarnya baru berlaku saat fase dua (`HRIS_TIER_FALLBACK=off`) dinyalakan.

**Antrean peninjau ikut hak yang sama.** `build*ReviewFilter` menerima `bolehTahapHR` dari predikat yang sama dengan tombolnya, supaya daftar tak pernah menampilkan pengajuan yang menolak saat ditindak.

⚠️ **Tahap HRD tak selalu duduk di slot `hr_status`** ([#1127](https://github.com/bip-itteam-internal/bip-erp/pull/1127)). Dua alur memakai SATU tahap dan menaruh peninjau HR di slot `spv_status`: **Koreksi milik staf HR** (di situ HR penyetuju final) dan **Tukar milik atasan** departemen mana pun atau orang HR. Keduanya tetap keputusan HRD dan karena itu ikut `hris.pengajuan.approve`, dikenali dari data slotnya (`slotHRLevelDepartemen`), bukan dari nama fieldnya. Cabang atasan biasa tak tersentuh. Yang **tidak** digerbang izin dan memang tak boleh: mode `?as=reviewer|reviewed` (relasional, siapa yang ditunjuk di `spv_status`/`hr_status`), `?as=self`, `/requests/mine`, dan penunjukan personal di slot HR.

## Pengganti pada pengajuan (2026-08-22)

Saat menyetujui, **atasan boleh menunjuk rekan yang mengambil alih pekerjaan pemohon**. Berlaku untuk **Izin/Cuti/Sakit** dan **Dinas** — dua jenis yang benar-benar membuat orangnya absen. Koreksi dan Tukar tidak: keduanya tak meninggalkan pekerjaan yang perlu digantikan.

- **Opsional.** Field `replacement` bertipe pointer + `omitempty`, jadi `nil` = tak ada pengganti dan itu keadaan yang sah sekaligus mayoritas. Pengajuan lama terbaca apa adanya → **tanpa migrasi data**.
- **Hanya tahap SPV.** Handler membaca `replacement_employee_id` cuma saat `updateField == "spv_status"`; tahap HRD mengabaikannya sekalipun ikut terkirim. Siapa yang menggantikan adalah keputusan atasan langsung yang tahu pekerjaannya, dan membuka slot yang sama di dua tahap berarti dua orang bisa saling menimpa tanpa jejak siapa yang terakhir memutuskan.
- **Kandidat = rekan aktif, sedepartemen, dan seposisi.** Ditentukan **di server** (`saringKandidat`), dipakai dua arah: endpoint daftar yang mengisi layar dan validasi saat penunjukan disimpan. Bila layar memakai aturan sendiri, ia akan menawarkan orang yang justru ditolak server saat tombol Setujui ditekan.
- **Posisi dibandingkan lewat `common.KanonPosisi`, bukan pencocokan sebagian.** Endpoint daftar karyawan menyaring posisi dengan regex, sehingga permintaan "Host Live" ikut membawa pulang "Senior Host Live".
- **Nama/departemen/posisi DISALIN ke dokumen**, bukan sekadar dirujuk lewat `employee_id`, supaya riwayat tetap terbaca setelah orangnya keluar dari perusahaan.
- **Pemberitahuan dikirim setelah HRD menyetujui**, bukan saat penunjukan — kalau HRD menolak, tak ada yang terlanjur diberi tahu untuk menggantikan cuti yang batal. Kategori inbox tersendiri **`request-replacement`** (lihat [[Microservices - Notification Service]]).
- **Memberi tahu, bukan meminta izin.** Yang ditunjuk tidak diminta menyetujui apa pun, sejalan dengan keputusan yang sama pada undangan kalender.
- ⚠️ **Belum berlaku untuk karyawan bershift.** Digerbang `attendance.IsShiftBasedSchedule`; server membalas daftar kosong berikut `reason`, dan layar menampilkan alasan itu, bukan daftar kosong tanpa sebab. Menunjuk pengganti bagi karyawan bershift menuntut jadwal penggantinya ikut ditulis berikut libur pengganti, dan itu menyentuh kehadiran lalu lewat kehadiran menyentuh gaji.
- **Yang belum ada:** rekomendasi berbasis jadwal untuk karyawan bershift, pengurutan kandidat menurut siapa yang paling jarang ditunjuk, dan **pencabutan penunjukan saat pengajuan dibatalkan setelah disetujui** (perilakunya belum diputuskan).

## Komponen Bersama (di kode)

Semua di [[Microservices - Attendance Service]]:
- **Model**: `ReviewData`, `ReviewStatus` (`Menunggu / Disetujui / Ditolak / Diabaikan / Dibatalkan`)
- **Resolusi status**: `Resolve*Status(...)` — menggabungkan beberapa review jadi status final
- **Penentuan reviewer**: `getSupervisorData(department)` + `build*ReviewFilter(...)`
- **Pola endpoint**: `create` / `view` (`?as=reviewer` = antrian perlu-tindakan-ku, termasuk **consent rekan** untuk Tukar Shift; `?as=reviewed` = sudah ditindak) / `review` / `cancel`. Filter reviewer via `buildReviewFilter` (leave/dinas/tukar) & `buildCorrectionReviewFilter`, dengan guard `employee_id != pemanggil` (anti-bocor sedepartemen). *(Case `as=partner` khusus Tukar sudah dihapus — consent kini lewat `as=reviewer`.)*
- **Notifikasi**: FCM + inbox ke reviewer & pemohon (via [[Microservices - Notification Service]])
- **Apply-to-attendance**: setelah disetujui, otomatis menyesuaikan entri attendance

## Pola Alur (umum)

```
Karyawan buat request
   → notif reviewer
   → review berjenjang (approve / reject)
        ├─ disetujui → terapkan ke attendance + notif pemohon
        └─ ditolak → notif pemohon
   (pemohon dapat membatalkan selama masih pending)
```

## Batas Tanggal per Jenis Request

Tiap turunan punya aturan tanggal sendiri (grounded ke kode attendance service). **Tidak ada** satu pun yang menjaga konsistensi terhadap **periode gaji (26–25)**:

| Jenis | Batas tanggal | Tutup-buku / payroll-lock |
|---|---|---|
| Cuti / Izin | `to_date > from_date`; subtype "Pulang cepat"/"Datang terlambat" = **hari ini**; cuti tahunan cek kuota. Tak ada batas mundur → **bisa di-backdate** | ❌ tidak ada |
| Tukar shift | `exchange_date` min **2 hari** ke depan + `work_date` & `exchange_date` **bulan kalender sama** | ❌ tidak ada |
| Koreksi clock-in/out | window **7 hari** (`correctionWindowDays`) + tak boleh tanggal masa depan | ❌ tidak ada |
| Perjalanan dinas | `to_date >= from_date`; **tak ada batas mundur** → bisa di-backdate (gap diketahui; dinas semestinya forward-looking) | ❌ tidak ada |
| Lembur (SPKL) | *(belum diimplementasikan)* | — |

**Catatan konsistensi gaji (gap diketahui):** karena Leave bisa backdate & Correction berlaku mundur 7 hari, pengajuan **bisa melewati cutoff** periode gaji → bila periode sudah tutup-buku & dibayar, perubahan attendance tak otomatis ter-rekonsiliasi dengan gaji (mismatch). **Keputusan saat ini: dibiarkan apa adanya** (mengikuti perilaku Leave yang memang tanpa penjaga cutoff). Bila diperlukan, aturan cutoff = **keputusan level payroll terpisah** (sumber tanggal cutoff / flag `locked`), berlaku lintas-request — belum dibangun.

## Manfaat & Catatan

- **Reuse infrastruktur** → konsisten + cepat menambah jenis request baru
- **Saran**: [[HRIS - Overtime]] sebaiknya mengikuti pola ini (model `overtime_request` + `create/view/review/cancel` + apply ke `overtime_hour`)

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]] · [[HRIS - Attendance System]]
- [[Microservices - Attendance Service]] · [[Microservices - Notification Service]] · [[Microservices - Employee Service]]
- [[APP - MyBharata]] (menu Submission)

## Deskripsi

*Attendance Service menangani absensi karyawan secara end-to-end: clock-in/out multi-metode (mobile, fingerprint, website), resolusi serta rotasi jadwal kerja (static maupun shift/group rolling), leave request, perjalanan dinas, guestbook tamu, manajemen hari libur, hingga laporan payroll dan absensi. Service ini menjadi sumber data kehadiran utama yang dikonsumsi oleh HRIS Orchestrator untuk perhitungan payroll dan pelaporan.*

- **Stack:** Go + Fiber v2 + MongoDB
- **Path:** `services/attendance`
- **Status:** ✅ Implemented penuh (kecuali clock-in via website)

## Endpoint / Fitur (Sudah Diimplementasikan)

**Health & Registry**
- `GET /health` — health check service.
- `GET /data-type/:dt` — registry data type: schedule-list, leave-type/subtype (dengan `?detail=true` → `max_range`/`format`/`paid`), holiday-type, attendance-status.
- `GET /sync/company-work-schedules` — sinkronisasi definisi jadwal kerja perusahaan.

**Networks (dipakai IT)**
- `GET /networks` — daftar jaringan WiFi kantor.
- `POST /internal/wifi/add` — tambah access point WiFi (RequireITStaff).
- `DELETE /internal/wifi/delete` — hapus access point WiFi.

**Integrasi HRIS**
- `GET /internal/summary` — hitung jumlah clock-in/out dalam 24 jam.
- `PATCH /:id/update` — edit entry absensi sekaligus lampirkan dokumen.
- `GET /report` — laporan bulanan per karyawan (periode 26→26).
- `GET /payroll-supplement` — agregasi jam kerja jadi `payout_pct = jam_kerja / jam_diharapkan` (+ rincian telat, leave, lembur, absen). **Perlakuan dibayar/dipotong per status kini _configurable_** via master `payroll_status_treatment` (default: Cuti/Sakit/Dinas/Libur = **dibayar**; Izin/Tanpa Keterangan = **dipotong**). Tepat Waktu/Terlambat = hari ter-clock (kerja = jadwal − telat − izin jam); Pending dilewati. Logika agregasi = fungsi murni `computePayoutBreakdown`. Diproxy oleh Employee Service sbg `/api/employee/me/payroll-approx`.
- `GET /payroll-status-treatment` — perlakuan payout per status (`data`) + **override per-subtipe** (`subtypes`); RBAC HR. `PUT /payroll-status-treatment` (body `{status, paid, subtype?}`) — set `paid` per status, atau per `(status, subtype)` bila `subtype` diisi (koleksi `payroll_subtype_treatment`, diturunkan dari `LeaveSubtypes` yang di-resolve ke status; PR #271). Hanya baris ter-seed (404 selainnya). Di-seed default saat boot (idempoten, tak menimpa perubahan HR). **Override subtipe kini dipakai payout** (Fase 2, PR #273): subtipe dipersist ke `attendance_entries` (cron + approval), `computePayoutBreakdown(entries, paidStatus, subtypePaid)` menerapkan override per-(status,subtipe) di atas per-status via `paidForEntry`. Entry lama tanpa subtipe = per-status (tanpa backfill). Konsep bisnis: [[HRIS - Payroll]] · [[HRIS - Employee Request & Approval]].

**Clock In/Out**
- `POST /tap?method=` — clock-in/out multi-metode:
	- `fingerprint` — validasi serial hardware terhadap allowlist.
	- `mobile` — validasi MAC WiFi kantor (`company_wifi`), atau validasi GPS untuk jadwal remote.
	- Perhitungan on-time/telat dengan ambang 11 menit, charge per jam.

**Views Karyawan & HRIS**
- `GET /entries` — daftar entry absensi (RequireHRISStaff).
- `GET /history` — riwayat bulanan per karyawan.
- `GET /schedule` — jadwal kerja karyawan.
- `GET /today?view=resolve|team` — kehadiran hari ini (mode resolve atau team).
- `PATCH /mood` + `GET /mood` — set & ambil mood karyawan.

**Holidays**
- `GET /holiday` — daftar hari libur.
- `POST /holiday` — tambah hari libur (RequireHRISStaff).
- `DELETE /holiday/:id` — hapus hari libur.

**Fingerprint Export**
- `POST /fingerprint/export` + `GET /fingerprint/export` — metadata file MinIO dari aplikasi extension hardware fingerprint.

**Guestbook**
- `GET /guestbook/token` — terbitkan token tamu.
- `POST /guestbook/token-validate` — validasi token tamu.
- `GET /guestbook` — daftar buku tamu.
- `PATCH /guestbook` — update buku tamu (RequireSecurity).
- `POST /guestbook` — entri tamu publik (token-gated, mengirim FCM).

**Leave Request (workflow penuh)**
- `POST /request/create` — buat request (multipart + upload via file service, rantai review supervisor→HR, cek kuota cuti).
- `GET /request/view?as=reviewer|reviewed` — lihat request sebagai reviewer atau yang direview.
- `PATCH /request/review` — approval SPV/HR + notif + auto-apply cuti + decrement kuota.
- `PATCH /request/cancel` — pembatalan request.
- `GET /request/security-lookup` — lookup oleh security (RequireSecurity).
- `PATCH /request/security-verify` — verifikasi oleh security.
- Detail jenis cuti/izin, reviewer, kuota & alur: [[HRIS - Leave Request]]

**Tukar Jadwal Kerja (workflow)** — collection `schedule_exchange_request`
- `POST /schedule-exchange/create`, `PATCH /schedule-exchange/consent`, `GET /schedule-exchange/view`, `PATCH /schedule-exchange/review`, `PATCH /schedule-exchange/cancel` — Tukar Shift (swap antar-rekan, 3 langkah: consent rekan → atasan → HRD) atau Tukar Hari (geser hari). Setelah disetujui menyesuaikan attendance (`applyApprovedShiftExchange`/`applyScheduleExchangeSwap`); cron seeding & kalender sadar-swap. Detail lengkap: [[HRIS - Tukar Jadwal Kerja]].

**Attendance Correction (workflow)**
- `POST /correction`, `GET /correction/mine`, `GET /correction`, `PATCH /correction/:id/review`, `PATCH /correction/:id/cancel` — koreksi clock-in/out yang terlewat dengan approval multi-level (routing per role); waktu diisi otomatis dari jadwal saat disetujui (`applyCorrectionToEntry`). Detail lengkap: [[HRIS - Attendance Correction]].

**Business Trip / Perjalanan Dinas (workflow)** — collection `business_trip_request`
- `POST /business-trip/create` — buat pengajuan perjalanan dinas (multipart + upload dokumen opsional); generate nomor dokumen `<seq>/HRD/PERJADIN/<bulan-romawi>/<tahun>` (counter atomik per-tahun, collection `business_trip_counter`); reviewer **Atasan Langsung → HRD**.
- `GET /business-trip/view?as=reviewer|reviewed` — lihat pengajuan sebagai pengaju / reviewer.
- `PATCH /business-trip/review` — approve/reject SPV/HRD (HRD tak boleh menyetujui pengajuannya sendiri); saat disetujui HRD → status kehadiran rentang tanggal = `Dinas` (`applyApprovedBusinessTripToAttendance` + pre-alokasi cron untuk future-dated).
- `PATCH /business-trip/cancel` — batalkan pengajuan pending milik sendiri.
- Anggaran (transport PP/akomodasi/uang saku) = **estimasi**, tanpa integrasi Finance. Detail lengkap: [[HRIS - Perjalanan Dinas]].

**Cron & Seeding**
- Tiap 30 menit: pra-generate entry absensi dari rotasi jadwal (perhitungkan cuti, **tukar jadwal** disetujui — swap kedua sisi via `WorkTimeFor` — & **perjalanan dinas** disetujui → status `Dinas`) + flip status pending→alpha.
- Per jam: auto-ignore **leave + koreksi presensi + tukar jadwal + perjalanan dinas** basi (>24 jam) + **reminder reviewer T+18j** (koreksi, leave, tukar jadwal & perjalanan dinas) + sinkronisasi jadwal.
- Saat startup: seed ulang `company_work_schedule` (~40 definisi shift), `company_group_rotation`, dan `company_wifi` (~50 access point kantor).

## Belum Diimplementasikan / Catatan

- **Clock-in via website** masih mengembalikan `501 NotImplemented` — hanya metode `fingerprint` dan `mobile` yang berfungsi.
- Terdapat kode rotasi hostlive lama dan `cronDatabaseBackup` yang sudah di-comment (dipindahkan ke system cron).
- Beberapa nilai masih hardcoded: koordinat GPS kantor pusat dan allowlist serial mesin fingerprint.

## Dependencies & Integrasi

- **MongoDB** — database independen, collections: `attendance_entries`, `work_schedule`, `company_work_schedule`, `company_group_rotation`, `company_wifi`, `company_holiday`, `fingerprint_export`, `guestbook`, `leave_request`, `schedule_exchange_request`, `attendance_correction_request`, `business_trip_request`, `business_trip_counter`, `payroll_status_treatment` (perlakuan dibayar/dipotong per status untuk payout), `payroll_subtype_treatment` (override per-subtipe; belum dipakai payout). Lihat [[DB - Overview and Notes]].
- [[Microservices - Employee Service]] — endpoint `/list` (data karyawan) dan `/vacation/decrement` (decrement kuota cuti).
- [[Microservices - File Service]] — upload dokumen pendukung leave request.
- [[Microservices - Notification Service]] — pengiriman notifikasi FCM (guestbook, review leave request).
- [[CORE - API Master Gateway]] — entry point routing request ke service.
- [[CORE - HRIS Orchestrator]] — konsumen `internal/summary`, `report`, `payroll-supplement`, dan force-update entry.
- **MinIO** — penyimpanan file metadata fingerprint export.

## Dokumen Terkait

- [[HRIS - Attendance System]]
- [[HRIS - Leave Request]]
- [[HRIS - Tukar Jadwal Kerja]]
- [[HRIS - Attendance Correction]]
- [[HRIS - Perjalanan Dinas]]
- [[HRIS - Payroll]]
- [[APP - MyBharata]]
- [[IT - Background Jobs & Schedulers]] — cron service ini (pre-alokasi entry tiap 30 mnt, auto-ignore request basi tiap jam)

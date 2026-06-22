## Deskripsi

*Attendance Service menangani absensi karyawan secara end-to-end: clock-in/out multi-metode (mobile, fingerprint, website), resolusi serta rotasi jadwal kerja (static maupun shift/group rolling), leave request, guestbook tamu, manajemen hari libur, hingga laporan payroll dan absensi. Service ini menjadi sumber data kehadiran utama yang dikonsumsi oleh HRIS Orchestrator untuk perhitungan payroll dan pelaporan.*

- **Stack:** Go + Fiber v2 + MongoDB
- **Path:** `services/attendance`
- **Status:** ✅ Implemented penuh (kecuali clock-in via website)

## Endpoint / Fitur (Sudah Diimplementasikan)

**Health & Registry**
- `GET /health` — health check service.
- `GET /data-type/:dt` — registry data type: schedule-list, leave-type/subtype, holiday-type, attendance-status.
- `GET /sync/company-work-schedules` — sinkronisasi definisi jadwal kerja perusahaan.

**Networks (dipakai IT)**
- `GET /networks` — daftar jaringan WiFi kantor.
- `POST /internal/wifi/add` — tambah access point WiFi (RequireITStaff).
- `DELETE /internal/wifi/delete` — hapus access point WiFi.

**Integrasi HRIS**
- `GET /internal/summary` — hitung jumlah clock-in/out dalam 24 jam.
- `PATCH /:id/update` — edit entry absensi sekaligus lampirkan dokumen.
- `GET /report` — laporan bulanan per karyawan (periode 26→26).
- `GET /payroll-supplement` — agregasi jam kerja, telat, cuti, lembur, dan absen menjadi persentase payout.

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

**Shift Exchange (workflow)**
- `POST /shift-exchange/create`, `GET /shift-exchange/view`, `PATCH /shift-exchange/review`, `PATCH /shift-exchange/cancel` — pertukaran hari kerja/libur (atau slot shift) dengan approval multi-level; setelah disetujui otomatis menyesuaikan attendance (`applyApprovedShiftExchange`). Detail lengkap: [[HRIS - Shift Exchange]].

**Cron & Seeding**
- Tiap 30 menit: pra-generate entry absensi dari rotasi jadwal + flip status pending→alpha.
- Per jam: auto-ignore request basi (>24 jam) + sinkronisasi jadwal.
- Saat startup: seed ulang `company_work_schedule` (~40 definisi shift), `company_group_rotation`, dan `company_wifi` (~50 access point kantor).

## Belum Diimplementasikan / Catatan

- **Clock-in via website** masih mengembalikan `501 NotImplemented` — hanya metode `fingerprint` dan `mobile` yang berfungsi.
- Terdapat kode rotasi hostlive lama dan `cronDatabaseBackup` yang sudah di-comment (dipindahkan ke system cron).
- Beberapa nilai masih hardcoded: koordinat GPS kantor pusat dan allowlist serial mesin fingerprint.

## Dependencies & Integrasi

- **MongoDB** — database independen, collections: `attendance_entries`, `work_schedule`, `company_work_schedule`, `company_group_rotation`, `company_wifi`, `company_holiday`, `fingerprint_export`, `guestbook`, `leave_request`, `shift_exchange_request`. Lihat [[DB - Overview and Notes]].
- [[Microservices - Employee Service]] — endpoint `/list` (data karyawan) dan `/vacation/decrement` (decrement kuota cuti).
- [[Microservices - File Service]] — upload dokumen pendukung leave request.
- [[Microservices - Notification Service]] — pengiriman notifikasi FCM (guestbook, review leave request).
- [[CORE - API Master Gateway]] — entry point routing request ke service.
- [[CORE - HRIS Orchestrator]] — konsumen `internal/summary`, `report`, `payroll-supplement`, dan force-update entry.
- **MinIO** — penyimpanan file metadata fingerprint export.

## Dokumen Terkait

- [[HRIS - Attendance System]]
- [[HRIS - Shift Exchange]]
- [[HRIS - Payroll]]
- [[APP - Mobile Application]]

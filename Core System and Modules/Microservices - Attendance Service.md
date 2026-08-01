## Deskripsi

*Attendance Service menangani absensi karyawan secara end-to-end: clock-in/out multi-metode (mobile, fingerprint, website), resolusi serta rotasi jadwal kerja (static maupun shift/group rolling), leave request, perjalanan dinas, guestbook tamu, manajemen hari libur, hingga laporan payroll dan absensi. Service ini menjadi sumber data kehadiran utama yang dikonsumsi oleh HRIS Orchestrator untuk perhitungan payroll dan pelaporan.*

- **Stack:** Go + Fiber v2 + MongoDB
- **Path:** `services/attendance`
- **Status**: ✅ Implemented penuh (kecuali clock-in via website) · ⚠️ **multi-perusahaan (tenant) parsial** — lihat catatan di bawah & [[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]

## Endpoint / Fitur (Sudah Diimplementasikan)

**Health & Registry**
- `GET /health` — health check service.
- `GET /data-type/:dt` — registry data type: schedule-list, leave-type/subtype (dengan `?detail=true` → `max_range`/`format`/`paid`), holiday-type, attendance-status.
- `GET /sync/company-work-schedules` — sinkronisasi definisi jadwal kerja perusahaan.
- `GET /sync/company-group-rotations` — cermin endpoint di atas untuk definisi rotasi shift bergilir (dipakai employee-service agar resolusi tipe jadwal jadi data-driven, PR #661).

**Networks (dipakai IT)**
- `GET /networks` — daftar jaringan WiFi kantor.
- `POST /internal/wifi/add` — tambah access point WiFi (RequireITStaff).
- `DELETE /internal/wifi/delete` — hapus access point WiFi.

**Integrasi HRIS**
- `GET /internal/summary` — hitung jumlah clock-in/out dalam 24 jam.
- `PATCH /:id/update` — edit entry absensi sekaligus lampirkan dokumen.
- `GET /report` — laporan bulanan per karyawan (periode 26→26). Tiap entry kini menyertakan `leave_subtype` (dari `AttendanceEntries.LeaveSubtype`) selain `status`, sehingga FE bisa membedakan **Izin "urusan kantor"** (subtipe `Meninggalkan perkerjaan sementara (urusan kantor)`, payroll `Paid`) dari Izin pribadi — ditampilkan kode legend `IK` vs `I`. Status `Dinas` (`D`) juga dirender di FE report. Konsep kantor-vs-pribadi: [[HRIS - Leave Request]].
- `GET /payroll-supplement` — agregasi jam kerja jadi `payout_pct = jam_kerja / jam_diharapkan` (+ rincian telat, leave, lembur, absen). **Perlakuan dibayar/dipotong per status kini _configurable_** via master `payroll_status_treatment` (default: Cuti/Sakit/Dinas/Libur = **dibayar**; Izin/Tanpa Keterangan = **dipotong**). Tepat Waktu/Terlambat = hari ter-clock (kerja = jadwal − telat − izin jam); Pending dilewati. Logika agregasi = fungsi murni `computePayoutBreakdown`. Diproxy oleh Employee Service sbg `/api/employee/me/payroll-approx`.
- `GET /payroll-status-treatment` — perlakuan payout per status (`data`) + **override per-subtipe** (`subtypes`); RBAC HR. `PUT /payroll-status-treatment` (body `{status, paid, subtype?}`) — set `paid` per status, atau per `(status, subtype)` bila `subtype` diisi (koleksi `payroll_subtype_treatment`, diturunkan dari `LeaveSubtypes` yang di-resolve ke status; PR #271). Hanya baris ter-seed (404 selainnya). Di-seed default saat boot (idempoten, tak menimpa perubahan HR). **Override subtipe kini dipakai payout** (Fase 2, PR #273): subtipe dipersist ke `attendance_entries` (cron + approval), `computePayoutBreakdown(entries, paidStatus, subtypePaid)` menerapkan override per-(status,subtipe) di atas per-status via `paidForEntry`. Entry lama tanpa subtipe = per-status (tanpa backfill). Konsep bisnis: [[HRIS - Payroll]] · [[HRIS - Employee Request & Approval]].

**Clock In/Out**
- `POST /tap?method=` — clock-in/out multi-metode:
	- `fingerprint` — validasi serial hardware terhadap allowlist.
	- `mobile` — validasi MAC WiFi kantor (`company_wifi`), atau validasi GPS untuk jadwal remote.
	- Perhitungan on-time/telat dengan ambang 11 menit, charge per jam.
	- **Gerbang form wajib** (⚠️ branch `feat/form-builder`, belum merge): sebelum `handleClockIn`, service menanyakan [[Microservices - Form Builder Service]] (`GET /internal/compliance`) apakah karyawan punya form wajib yang belum diisi. Bila ada dan mode gerbangnya `block`, clock-in dibalas `403` beserta daftar form (`id` + `title`) supaya [[APP - MyBharata]] bisa langsung membuka form yang menahan. **Hanya metode `mobile` dan hanya CLOCK-IN** — mesin fingerprint tak punya layar untuk mengisi form dan tak membawa identitas JWT, sedangkan menahan orang PULANG bukan tujuan fitur ini. Konsep & aturan bisnisnya: [[IT - Form Builder]].

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
- `POST /request/create` — buat request (multipart + upload via file service, rantai review supervisor→HR, cek kuota cuti). **Idempoten** (guard `duplicateLeaveRequestFilter`, `request_dedup.go`): sebelum `InsertOne`, cek duplikat **berbasis konten** — `employee_id` + `leave_type` + `leave_subtype` + `from_date` + `to_date` yang masih **aktif** (status `Waiting`/`Approved`). Bila ada, kembalikan sukses **tanpa insert baru** (mencegah data ganda dari retry saat jaringan tak stabil — respons hilang padahal data sudah tersimpan). Status terminal (`Rejected`/`Canceled`/`Ignored`) tetap boleh diajukan ulang. Catatan: `reason` & lampiran **tidak** masuk identitas dedup — pengajuan kedua dengan alasan beda tapi tipe/subtipe/tanggal sama tetap dianggap duplikat.
- `GET /request/view?as=reviewer|reviewed` — lihat request sebagai reviewer atau yang direview.
- `PATCH /request/review` — approval SPV/HR + notif + auto-apply cuti + decrement kuota.
- `PATCH /request/cancel` — pembatalan request.
- `GET /request/security-lookup` — lookup oleh security (RequireSecurity).
- `PATCH /request/security-verify` — verifikasi oleh security.
- Detail jenis cuti/izin, reviewer, kuota & alur: [[HRIS - Leave Request]]

**Tukar Jadwal Kerja (workflow)** — collection `schedule_exchange_request`
- `POST /schedule-exchange/create`, `PATCH /schedule-exchange/consent`, `GET /schedule-exchange/view`, `PATCH /schedule-exchange/review`, `PATCH /schedule-exchange/cancel` — Tukar Shift (swap antar-rekan, 3 langkah: consent rekan → atasan → HRD) atau Tukar Hari (geser hari). Setelah disetujui menyesuaikan attendance (`applyApprovedShiftExchange`/`applyScheduleExchangeSwap`); cron seeding & kalender sadar-swap. Detail lengkap: [[HRIS - Tukar Jadwal Kerja]].

**Attendance Correction (workflow)**
- `POST /correction`, `GET /correction/mine`, `GET /correction`, `PATCH /correction/:id/review`, `PATCH /correction/:id/cancel` — koreksi clock-in/out yang terlewat dengan approval multi-level (routing per role); waktu diisi otomatis dari jadwal saat disetujui (`applyCorrectionToEntry`). Entry hasil koreksi ditandai `clock_in_method`/`clock_out_method = Website` (`correctionEntryUpdates`) — karena clock-in via website tak diimplementasi, method `Website` **berarti koreksi presensi** (di FE Laporan Kehadiran ditampilkan simbol `#` berlabel "Koreksi"). Detail lengkap: [[HRIS - Attendance Correction]].

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

- **Cakupan supervisi lintas departemen**: `getSupervisorData` memakai `/list?type=supervisor` di [[Microservices - Employee Service]], yang kini menelusuri departemen sendiri lebih dulu lalu departemen **induk** dari `master_department.supervised_by`. Tidak ada lagi penulisan ulang departemen yang hardcoded. Pengajuan 15 orang **General Affair** bergantung pada langkah cadangan ini untuk menemukan approver — detail & konsekuensinya di [[HRIS - Organization Structure]].
- **Absensi Tim Hari Ini** (`/today?view=team`) menampilkan departemen yang satu tim bersama, dengan memakai `include_group=true` pada employee-service. Pasangan departemennya **tidak** ditulis di service ini.
- ~~Filter departemen pada laporan absensi tak pernah bekerja~~ → **diperbaiki**: pemanggilan salah memakai `type=department`, yang bukan case valid pada `/list` sehingga selalu balas `400` dan ditelan jadi hasil kosong. Akibatnya filter mati untuk **semua** departemen, tanpa error yang terlihat. Pesan error `/list` yang sempat mengiklankan `department` sebagai opsi valid ikut dibetulkan.
- **Clock-in via website** masih mengembalikan `501 NotImplemented` — hanya metode `fingerprint` dan `mobile` yang berfungsi.
- Terdapat kode rotasi hostlive lama dan `cronDatabaseBackup` yang sudah di-comment (dipindahkan ke system cron).
- Allowlist serial mesin fingerprint **sudah tidak hardcoded** lagi (pindah ke koleksi `company_fingerprint`, PR #657). Yang tersisa hardcoded: koordinat GPS kantor pusat (`mainOfficeGPSCoordinate`), dan itu hanya dipakai jalur clock-in **website** yang masih `501`.
- **Multi-perusahaan (tenant) — parsial** ([[ADR - 0029 Multi-Tenant Presensi Row-Level company_id]]): ke-10 koleksi presensi kini punya `company_id`, setiap CREATE menstempelnya, dan **jalur utama ter-scope** (`/entries`, `/today` team, `/mood`, `/report`, HR admin, review koreksi/dinas, cron entry, wifi/fingerprint WFO, notification FCM). Baca dipakai `common.EffectiveCompanyID(c)` (override `?company=` khusus admin pusat). **Hardening (Batch A, PR #653):** hari libur (`resolveEmployeeSchedule` + `/holiday` GET/DELETE), filter reviewer leave & tukar jadwal (`/request/view`,`/review`, `/schedule-exchange/view`,`/review`, `/hr/requests/detail`), `/guestbook` GET, `/request/security-lookup`+`verify`, `PATCH /:id/update`, review koreksi, komentar telat guestbook — **sudah ter-scope `company_id`**. **A5 supervisor-lookup (PR #655):** employee `/list?type=supervisor` + attendance `getSupervisorData` (8 call-site + cron) ter-scope `company_id` via query param. **Batch B (PR #656):** `company_work_schedule` + `company_group_rotation` ber-`company_id` (kepemilikan; lookup resolusi tetap by `schedule_id`/`group_id` yang **unik global**); seed BIP aman restart (`DeleteMany` company BIP, bukan `Drop` koleksi); CRUD `/company-work-schedule` (create/list/delete, **ENFORCE `schedule_id` unik global** → jaminan isolasi lookup). **FE Kelola Shift = erp-frontend #501** (editor 7-hari). **Fingerprint per-perusahaan (PR #657):** koleksi `company_fingerprint` (serial→tenant+lokasi) menggantikan allowlist hardcoded; `/tap` scope entry ke perusahaan pemilik mesin; CRUD `/internal/fingerprint/*`. Catatan: GPS mobile TAK dipakai untuk radius (WFA cuma butuh lokasi ADA), jadi hardcode GPS bukan blocker mobile — hanya website `/tap` (501) yang masih pakai `mainOfficeGPSCoordinate`. **CRUD rotasi shift (PR #658):** `/company-group-rotation` (list/create/delete, `group_id` unik global) untuk perusahaan shift bergilir. **Katalog jadwal data-driven (PR #661):** preview jadwal + `/sync/company-group-rotations` (cermin `/sync/company-work-schedules`) supaya `schedule_id` kustom perusahaan lain (mis. `ELT-REGULAR`) tak lagi ditolak "invalid schedule type"; hot-path presensi (cron & clock-in) sengaja tak disentuh, tetap lookup by `schedule_id`/`group_id`. **WiFi kantor lintas-perusahaan (PR #663):** `getCompanyNetworks`/`add`/`delete` naik ke `EffectiveCompanyID` agar admin pusat bisa mendaftarkan WiFi kantor perusahaan pilot yang tak punya user IT sendiri; verifikasi clock-in WFO (`/tap`) **tetap** `CompanyID` (karyawan hanya absen di WiFi perusahaannya). **FE kelola fingerprint + rotasi sudah ada** di `/hris/schedule` ([[APP - Web ERP]]). **Masih terbuka:** cron presensi tetap satu sweep global (`cronScheduleCheck` membaca seluruh `work_schedule` tanpa filter perusahaan); entri hasilnya tetap ber-`company_id` karena diturunkan dari `work_schedule`, jadi bukan kebocoran data, tapi belum ada pemisahan per tenant.

## Dependencies & Integrasi

- **MongoDB** — database independen, collections: `attendance_entries`, `work_schedule`, `company_work_schedule`, `company_group_rotation`, `company_wifi`, `company_holiday`, `fingerprint_export`, `guestbook`, `leave_request`, `schedule_exchange_request`, `attendance_correction_request`, `business_trip_request`, `business_trip_counter`, `payroll_status_treatment` (perlakuan dibayar/dipotong per status untuk payout), `payroll_subtype_treatment` (override per-subtipe; belum dipakai payout). Lihat [[DB - Overview and Notes]].
- [[Microservices - Employee Service]] — endpoint `/list` (data karyawan) dan `/vacation/decrement` (decrement kuota cuti).
- [[Microservices - File Service]] — upload dokumen pendukung leave request.
- [[Microservices - Notification Service]] — pengiriman notifikasi FCM (guestbook, review leave request).
- [[Microservices - Form Builder Service]] — gerbang form wajib pada clock-in mobile (⚠️ branch `feat/form-builder`). **Dependensi ini sengaja dibuat lunak**: `FORM_BUILDER_MODULE_URL` **TIDAK** dimasukkan ke map `InternalURL` karena `validation.ValidateInternalURL` melakukan panic bila ada nilai kosong — menaruhnya di sana berarti attendance menolak boot di lingkungan yang env-nya belum menyusul, dan presensi seluruh perusahaan ikut mati. Kosong = gerbang mati, presensi normal. Panggilannya juga memakai klien HTTP sendiri ber-timeout **1,5 detik** (bukan `routes.InternalRequest` yang 10 detik, terlalu lama untuk jalur clock-in) dan **gagal-terbuka** di semua jalur error. Urutan deploy: form-builder lebih dulu, attendance menyusul.
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

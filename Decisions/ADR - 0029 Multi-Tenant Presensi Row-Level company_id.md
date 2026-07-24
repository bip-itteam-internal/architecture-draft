**Status**: ⚠️ Implemented (ada catatan) — Fase 1 (Presensi) di `main`; hardening attendance + service lain BELUM ter-scope

## Context

Bharata Group ingin sistem **presensi** bip-erp dipakai perusahaan lain di bawah grup (multi-tenant), bukan hanya PT Bharata Internasional (BIP). Kondisi awal (grounded): presensi implisit **single-tenant** — tak ada penanda perusahaan di model karyawan/presensi; JWT & header `BIP-*` tanpa company; mesin fingerprint, koordinat GPS, dan WiFi hardcoded satu kantor. Pemisahan yang ada hanya per-departemen. Entitas "Company" sebelumnya cuma di payroll (kop slip gaji), bukan batas data.

## Decision

Multi-tenant **satu database** dengan penanda **`company_id` row-level** (BUKAN instance/DB terpisah), disaring di lapisan bersama.

- `company_id` = key perusahaan (mis. `"BIP"`, `"PGL"`); default `common.DefaultCompanyID = "BIP"`. Disimpan di `work_data`, klaim JWT, dan header `BIP-Company-ID`.
- **Gateway** meng-inject `BIP-Company-ID` + `BIP-System-Roles` dari klaim JWT ke **semua** request internal (`routes.Reroute`); service-to-service diteruskan via `InternalRequest`.
- `common.CompanyID(c)` = perusahaan **penulis** (dipakai di create/stamp); `common.EffectiveCompanyID(c)` = perusahaan **pembaca**, menghormati override `?company=` **hanya** untuk central admin (`IsCentralAdmin` = `system_roles.it` ∈ supervisor/admin).
- **BIP = perusahaan default**; data lama di-backfill `company_id=BIP`; fallback di mana-mana → perilaku BIP tak berubah (gerbang regresi wajib).
- Master perusahaan: collection `master_company` (`key`/`name`/`code`) + CRUD `/master/companies` (gate IT supervisor). `code` = prefix `employee_id` per perusahaan (wajib & unik).
- Capture presensi via **MyBharata mobile** — ter-scope otomatis via JWT (interceptor kirim Bearer; endpoint tak kirim identitas perusahaan). **Admin pusat** = IT supervisor/admin (interim; peran khusus "admin pusat" belum ada).

## Scope Fase 1 (di `main`)

Paket **presensi penuh**: absen, jadwal, izin/cuti/sakit + approval, laporan HR. Plus:
- Fondasi: `company_id` di `work_data`/JWT/header, `master_company`, migrasi backfill BIP.
- Attendance: `company_id` di 10 struct koleksi + stempel saat create + saring jalur utama (`/entries`, `/today` team, `/mood`, `/report`, HR admin, review koreksi/dinas, cron entry, wifi/fingerprint WFO, notification FCM).
- Web (erp-frontend): halaman **Kelola Perusahaan** `/hris/companies`, **pemilih perusahaan admin pusat** di header (kirim `?company` ke presensi), **Buat Karyawan** pilih-perusahaan-dulu + prefix ikut perusahaan.
- Mobile (my-bharata): identitas perusahaan di **Profil Perusahaan** (dari `/me`) + **onboarding** (dari respons login), gate profil lengkap ke BIP.

## Consequences / Known Limitations (audit 2026-07-24)

**Attendance (in-scope) — hardening BELUM tuntas** (potensi leak lintas-perusahaan): lookup hari libur di `resolveEmployeeSchedule` (paling pervasif) + `/holiday` GET + `/guestbook` GET + `/request/security-lookup` + `/hr/requests/detail` (by `_id`); `buildReviewFilter` + `buildScheduleExchangeReviewFilter` (reviewer departemen sama-nama lintas perusahaan); write by `_id` (`PATCH /:id/update`, `DELETE /holiday/:id`, `security-verify`, guestbook late-comment); `InternalRequest(nil)` → default BIP (supervisor/kuota nyasar); cron satu sweep global; `schedule_id`/GPS/fingerprint/WiFi masih hardcoded satu kantor.

**Di LUAR fase 1 (belum ter-scope, per desain — fase lanjut):**
- **Employee directory** — `/internal/export/all`, `/view`, `/v2/internal/aggregate/employees*`, `/list?type=employee|supervisor`, KPI, contract, BPJS, vacation, birthday, analysis, headcount: semua lintas perusahaan (PII massal). `EffectiveCompanyID` belum dipakai di read employee-service.
- **Payroll** — `company_id` = badan usaha penggaji (kop slip), **BUKAN tenant**; `listEmployeeSalaries`/run/THR campur semua perusahaan.
- **Recruitment** — tanpa field company; portal karir publik (`/public/postings`, `/apply`) bersama semua tenant.
- **HRD-document** — distribusi global (`my/documents` + `target:all` sampai ke semua tenant).
- **master_department per-perusahaan** — PR #649 **ter-orphan** (merged ke branch stacked yang sudah mati, tak sampai `main`); re-apply via PR #652. Sampai merge, departemen (dan posisi) masih **GLOBAL**.
- KPI groups + supervisor-lookup masih department-only (merge lintas-tenant bila nama departemen sama).

**Sudah aman:** gateway (header ke semua service), notification FCM (personal/dept/broadcast ter-scope + `/list?type=fcm-token` filter company), core employee create + `/me` + respons login onboarding.

## Terkait

- [[Microservices - Attendance Service]] · [[Microservices - Employee Service]] · [[Microservices - Notification Service]] · [[Microservices - Payroll Service]] · [[Microservices - Recruitment Service]] · [[Microservices - HRD Document Service]]
- [[CORE - API Master Gateway]] · [[CORE - SSO Flow]] · [[DB - Overview and Notes]]
- [[APP - MyBharata]] · [[APP - Web ERP]]
- [[ADR - 0002 Database-per-Service]] (multi-tenant di sini = row-level dalam DB per-service, bukan DB per-tenant)

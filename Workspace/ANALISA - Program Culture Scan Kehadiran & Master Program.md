---
publish: false
---
# ANALISA — Program Culture: Scan Kehadiran, Rating Dipisah, Master Program

Daftar task hasil `/analisa-kebutuhan` (2026-09-09). Keputusan: [[ADR - 0083 Kehadiran Program Culture via Scan Menggantikan Feedback, plus Master Program]]. Papan kerja — berubah tiap item selesai; bukan arsitektur.

**Urutan wajib**: BE (form-builder) sebelum FE/mobile (perubahan kontrak). Prod dijalankan MANUSIA.

## Fase 0 — Prasyarat

- [ ] **T0. Ukur basis modul culture (ADR 0066).** Pastikan `culture_programs`/`culture_feedback` sudah ada di DEV/PROD dan branch `feature/workspace-position` sudah/hendak merge ke `main`. Ukur prod (bukan asumsi): apakah ada program & feedback nyata. Koordinasikan dengan pemilik branch itu sebelum menumpuk. Bila belum prod, catat sebagai risiko rilis.

## Fase 1 — Backend form-builder (`bip-erp/services/form-builder/`)

- [ ] **T1. Koleksi + CRUD `master_culture_program`.** Field `{nama, pilar, pelaksanaan∈{harian,mingguan,bulanan,tahunan}, company_id}`; rute master (acuan pola `services/employee/master_data.go:329-394`), digerbang `requireEmployee` + peran pengelola. Index. Dependensi: T0.
- [ ] **T2. Kehadiran via scan token.** Koleksi `culture_attendance` `{company_id, program_id, employee_id, scanned_at}` index unik `(program_id, employee_id)`. `GET /culture/programs/:id/scan-token` → token berputar TTL pendek (acuan Guestbook `services/attendance/main.go:2020-2042`), hanya officer `created_by`. `POST /culture/attendance` → validasi token + catat `employee_id` dari JWT (walk-in diterima; jangan tolak non-target). Dependensi: T0.
- [ ] **T3. Ubah `partisipasi` → dari scan.** Di `culture_metrics.go` (`hitungSkorProgram` `:36-90`), `hadir` = count `culture_attendance` per program (bukan responden feedback `:157-180`). Pertahankan `clamp100` `:76` & bobot 30/30/40. Test `culture_metrics_test.go` diperbarui. Pastikan bentuk `GET /internal/culture/metrics` **tetap** (ADR 0032). Dependensi: T2.
- [ ] **T4. `GET /culture/feedback/pending`.** Grup `/me/*` (saring JWT): program yang di-hadiri peserta (ada di `culture_attendance`) tapi belum ada `culture_feedback`-nya. Untuk pengingat rating mobile. Dependensi: T2.
- [ ] **T5. Program create dari master.** `POST/PUT /culture/programs` menerima `master_id` → isi `nama`/`pilar`/`pelaksanaan`; simpan `pelaksanaan` di `culture_programs` bila diperlukan. Dependensi: T1.

## Fase 2 — Web ERP (`erp-frontend`)

- [ ] **T6. Halaman master program (CRUD).** Pola tabel HRIS — `MainTable`/`useTableState`/`Banner bare` (acuan `features/hris/kpi/components/templates-table.tsx`), hooks di `features/form-builder`. i18n `id.ts`+`en.ts`. Dependensi: T1.
- [ ] **T7. Form buat program: pilih dari master → auto-isi.** Ganti input nama bebas (`hris/program-culture/kelola/page.tsx:188`) jadi dropdown master → isi `nama`/`pilar`/`pelaksanaan` otomatis. Dependensi: T5, T6.
- [ ] **T8. Perbarui label "hadir".** Dashboard/kelola: "hadir" kini kehadiran scan, bukan pengisi survei — perbaiki hint/i18n (`id.ts:5628` `attendedHint`). Dependensi: T3.

## Fase 3 — MyBharata (`my-bharata`, branch `feat/faiz`)

- [ ] **T9. Scaffold fitur `program_culture`.** Clone pola fitur `training` (data/domain/presentation), endpoint di `core/api/url.dart`, DI 6-fase, rute (`names.dart`/`misc_*`), menu `home_quick_access.dart`, l10n `app_id.arb`+`app_en.arb`. Dependensi: T2–T5.
- [ ] **T10. Officer — Tampilkan QR Kehadiran.** Layar menampilkan token berputar per program (mirip `MyQrWidget`), ambil `GET /culture/programs/:id/scan-token`, auto-refresh sebelum TTL habis. Dependensi: T9.
- [ ] **T11. Peserta — scan + rating.** Scan QR officer (acuan `inventory_scanner_page.dart`) → `POST /culture/attendance`; sheet rating bintang (acuan `trainer_evaluation_sheet.dart`, widget `star_rating.dart`) → `POST /culture/feedback`. Dependensi: T9.
- [ ] **T12. Pengingat rating persisten.** Cubit pola `PendingCsatCubit`/`PendingCsatBanner` dari `GET /culture/feedback/pending`; banner/dialog saat buka app, tampil selama daftar tak kosong, hilang setelah menilai. Dependensi: T4, T11.

## Fase 4 — Deploy & verifikasi

- [ ] **T13. Deploy BE→FE + verifikasi end-to-end.** Naikkan form-builder (bila ada kategori inbox baru untuk pengingat → notification-service bersama). Verifikasi lewat gateway: scan → `hadir` naik; rating → hilang dari `pending`; `/internal/culture/metrics` benar; skor KPI tak patah. **PROD: agent siapkan perintah, manusia jalankan.** Umumkan perubahan semantik KPI ke HR sebelum rilis.

## Catatan lingkup (dari ADR 0083)

- Bukan clock-in lokasi/WiFi. `club`/`public` tetap ditunda. Peserta tanpa HP = jalur cadangan manual = TBD.

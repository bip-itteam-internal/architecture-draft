## Deskripsi

*Landing page / titik masuk aplikasi yang menyediakan portal ke sistem lain. Saat ini diimplementasikan secara konkret di web ([[APP - Web ERP]]) sebagai halaman login + dashboard + sidebar portal berbasis role.*

- **Status**: ⚠️ Implemented (sebagian) — login + dashboard + sidebar portal per-role di [[APP - Web ERP]] sudah ada; info tambahan (SP, kalender, dll) sebagian masih konsep.

## Konsep

Karena kita sudah punya data dasar karyawan, landing page menyajikan informasi berguna (good to have) bagi mereka, plus daftar portal ke fitur sistem lain berdasarkan role.

- Informasi pribadi (read-only)
- Kalender jadwal kerja & shift (termasuk cuti massal perusahaan / hari libur nasional)
- Status kehadiran saat ini (butuh [[HRIS - Attendance System]])
- Status Surat Peringatan (SP) dan jumlah yang sedang aktif (tiap SP berlaku 6 bulan sebelum hangus)

Daftar portal ditampilkan di sisi kiri layar: judul module (HRIS, IT, dll) hanya indikasi (tidak dapat diklik), yang dapat diklik adalah fitur di bawahnya — sesuai role karyawan di sistem.

![[landing-page-example.png]]

## Status Implementasi (di [[APP - Web ERP]])

**Sudah diimplementasikan**
- Halaman login (`employee_id` + password) dengan handoff **SSO** (mint one-time code via `/auth/sso/ticket`)
- Halaman login **dwibahasa (id/en)** via `react-i18next` (namespace `auth.login.*`) + **switcher bahasa di kartu login**; pesan error login **spesifik** (kredensial salah vs gangguan server vs masalah jaringan). Lihat [[ADR - 0010 Internasionalisasi (i18n) Dua Bahasa]]
- **Portal sidebar berbasis role**: module muncul sesuai `system_roles`; fitur per module bisa langsung diklik (HRIS, Finance, IT, GA, Integration, dll)
- **Override akun "integration-only"** (allowlist env `NEXT_PUBLIC_INTEGRATION_ONLY_USERS`): akun tertentu dibatasi hanya melihat modul Integration + langsung diarahkan ke halaman Integration setelah login (mis. review/test Shopee) — detail di [[APP - Web ERP]]
- Dashboard: ringkasan kehadiran pribadi (clock in/out, overtime/telat/cuti), ringkasan karyawan, jadwal/shift
- Lookup employee master data + informasi role sebagai dasar portal

**Belum diimplementasikan**
- [ ] Status **Surat Peringatan (SP)** di landing belum ada. Modul SP-nya sendiri sudah dibangun ([[HRIS - Disciplinary (Surat Peringatan)]], ⚠️ belum merge), termasuk masa berlaku 6 bulan yang disebut di atas; yang belum ada adalah endpoint ringkasan "jumlah SP aktif" dan kartunya di landing
- [ ] **Flag maintenance** per fitur (menandai sistem sementara tidak tersedia, alih-alih menyembunyikannya)

## Kebutuhan

- [x] Employee master data (referensi look up)
- [x] Informasi role dari employee master data
	- [ ] Status fitur/sistem yang tersedia (untuk flag maintenance)
- [x] Portal terpadu ke service / sistem lain

## Dependencies

- [x] [[CORE - API Master Gateway]]
- [[Microservices - Employee Service]] — sumber data karyawan & role

## Dokumen Terkait

- [[APP - Web ERP]]
- [[APP - MyBharata]]

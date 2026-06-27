## Deskripsi

*Landing page / titik masuk aplikasi yang menyediakan portal ke sistem lain. Saat ini diimplementasikan secara konkret di web ([[APP - Web ERP]]) sebagai halaman login + dashboard + sidebar portal berbasis role.*

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
- **Portal sidebar berbasis role**: module muncul sesuai `system_roles`; fitur per module bisa langsung diklik (HRIS, Finance, IT, GA, Integration, dll)
- **Override akun "integration-only"** (allowlist env `NEXT_PUBLIC_INTEGRATION_ONLY_USERS`): akun tertentu dibatasi hanya melihat modul Integration + langsung diarahkan ke halaman Integration setelah login (mis. review/test Shopee) — detail di [[APP - Web ERP]]
- Dashboard: ringkasan kehadiran pribadi (clock in/out, overtime/telat/cuti), ringkasan karyawan, jadwal/shift
- Lookup employee master data + informasi role sebagai dasar portal

**Belum diimplementasikan**
- [ ] Status **Surat Peringatan (SP)** di landing belum ada
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

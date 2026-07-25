# Spec - Presensi Multi-Perusahaan (Bharata Group)

**Status**: Draft / Kajian
**Tanggal**: 2026-07-24
**Sumber**: Brainstorming (Irfan + agent), grounded ke kode via penelusuran read-only.

## Tujuan
Menyiapkan sistem PRESENSI (attendance) bip-erp agar bisa dipakai perusahaan lain di bawah Bharata Group. Fokus awal HANYA fitur presensi: absen masuk/pulang, jadwal/shift, izin/cuti/sakit + persetujuan, dan rekap/laporan HR. Satu sistem terpusat (multi-tenant), bukan instance terpisah per perusahaan.

## Keputusan (brainstorming 2026-07-24)
1. **Model**: satu sistem terpusat multi-tenant (bukan instance/DB terpisah per perusahaan).
2. **Cara absen perusahaan baru**: MyBharata (mobile, GPS/selfie) - tak perlu mesin fingerprint.
3. **Scope fase 1**: paket presensi penuh (absen, jadwal, izin/cuti/sakit + approval, laporan HR).
4. **Akses**: ada admin pusat (super-admin Bharata Group) + isolasi per perusahaan (orang perusahaan hanya lihat datanya sendiri).
5. **Pendekatan teknis**: penanda perusahaan (`company_id`) row-level di satu database, disaring per perusahaan di lapisan bersama.

## Kondisi saat ini (grounded)
- Presensi **implisit single-tenant**: TIDAK ada field company/tenant/branch di model karyawan maupun record presensi. Pemisahan data hanya per **departemen** (`SupervisedDepartments`).
- Entitas "Company" hanya ada di **payroll**, sebatas kop slip gaji (PT Bharata Internasional / CV Pure Glow Lux) - **bukan** batas data presensi.
- Login/JWT & header `BIP-*` tidak membawa perusahaan. `employee_id` "BIP-..." diisi manual HR; prefix tidak menyiratkan sub-perusahaan.
- Mesin fingerprint, GPS kantor, dan WiFi hardcoded satu kantor.
- File kunci: `services/attendance/{main.go,setup.go,notification.go}`, `shared-library/models/attendance/models.go`, `shared-library/models/employee/models.go`, `shared-library/common/{struct.go,header.go,department_scope.go}`, `api-gateway/main.go`, `services/payroll/models_company.go`.

## Desain

### 1. Model Perusahaan & identitas
- **Entitas master Perusahaan (baru)**: `company_id`, nama, kode pendek (BIP/PGL/...), status aktif, setelan default (zona jam kerja). Dipisah dari `Company` payroll (bisa dikaitkan kemudian, makna beda).
- **`company_id` di akun karyawan** (`work_data`/auth). Diturunkan otomatis saat login (bukan dipilih user) -> ditempel ke **JWT** + header baru `BIP-Company`.
- **`employee_id` tetap manual, prefix per perusahaan WAJIB & unik** (mis. `BIP-`, `PGL-`) untuk keterbacaan + keunikan global. Patokan tenant resmi tetap field `company_id` (prefix untuk manusia, bukan sumber kebenaran penyaringan).
- **BIP = Perusahaan #1 (default)**; semua data lama di-backfill `company_id = BIP`; perilaku BIP identik dengan sekarang.
- **Master departemen, posisi, jadwal kerja** ikut ber-`company_id` (sekarang global), agar tiap perusahaan punya struktur & jam kerja sendiri.

### 2. Perubahan data & penyaringan
- **`company_id` ditambahkan di**: `attendance_entries`, `work_schedule`, `leave_request`, `attendance_correction_request`, `business_trip_request`, `schedule_exchange_request`, `guestbook_entries`, `master_department`, positions, `company_work_schedule`/`company_group_rotation`/`company_holiday`/`company_wifi`.
- **Penyaringan per-perusahaan di SATU lapisan bersama** (analog `SupervisedDepartments`), dijadikan default - bukan ditempel manual per query - untuk mencegah developer lupa menyaring (sumber kebocoran).
- **Admin pusat = pengecualian sah** (lihat lintas / pilih perusahaan), juga terpusat di lapisan yang sama.
- **Migrasi sekali jalan**: cap `company_id = BIP` ke semua data lama; verifikasi sebelum go-live.
- **`fingerprint_id` di-namespace per perusahaan** (perusahaan baru mobile-only; aman bila kelak ada mesin).

### 3. Onboarding, peran, login
- **Onboarding (admin pusat)**: buat Perusahaan -> isi departemen/posisi & jadwal -> tunjuk HR admin perusahaan -> **daftarkan karyawan (oleh admin pusat)**. HR perusahaan mengelola operasional harian (persetujuan, laporan).
- **Peran per-perusahaan**: hak akses HR/supervisor/staf berlaku dalam konteks perusahaannya; hanya **admin pusat** yang lintas. (Beririsan dengan inisiatif "perapihan role/permission"; tetap dijaga scope ke presensi dulu.)
- **Login karyawan perusahaan baru (MyBharata)**: sama seperti BIP; otomatis hanya melihat data perusahaannya; alur persetujuan izin/cuti mengalir ke atasan/HR perusahaan tersebut.
- **Web HR**: HR tiap perusahaan lihat data & laporan perusahaannya; admin pusat bisa berpindah/pilih perusahaan.

### 4. Perambatan lintas-service
- **employee-service**: sinkron `work_schedule` + `/list` per perusahaan.
- **notification-service**: teruskan konteks perusahaan (FCM/inbox/WA).
- **api-gateway**: JWT + header `BIP-Company`. **Satu domain bersama** (tanpa subdomain per perusahaan) -> CORS tak berubah; perusahaan ditentukan dari akun saat login, bukan dari URL.

## Fase 1 (yang dibangun)
1. Fondasi tenant: entitas Perusahaan, `company_id` di model, klaim perusahaan di login, lapisan penyaringan bersama, migrasi cap data BIP.
2. Onboarding + peran per-perusahaan + admin pusat.
3. MyBharata & web HR sadar-perusahaan untuk paket presensi penuh -> validasi lewat **1 perusahaan pilot**.

## Ditunda (di luar fase 1)
Mesin fingerprint untuk perusahaan baru; kaitan ke payroll multi-perusahaan; modul lain (rekrutmen, tiket, dsb.) tetap khusus BIP dulu.

## Risiko & mitigasi
- **Kebocoran data antar perusahaan** -> penyaringan di lapisan bersama (bukan manual) + pengujian isolasi.
- **Data BIP lama** -> migrasi cap `company_id` sekali + verifikasi; BIP tak boleh berubah perilaku.
- **Perambatan lintas-service** -> bagian terbanyak; employee, notification, dan gateway ikut meneruskan konteks perusahaan.
- **Kompleksitas peran per-perusahaan** -> mulai dari peran minimum (HR admin, supervisor, staf).

## Tolok ukur sukses fase 1
Karyawan 1 perusahaan pilot bisa absen, lihat jadwal, ajukan izin/cuti (persetujuan mengalir ke atasan perusahaan itu), dan HR-nya melihat laporan - semua terisolasi dari BIP, dan BIP tetap jalan normal tanpa perubahan.

## Keputusan lanjutan (2026-07-24)
- **Pendaftaran karyawan perusahaan baru**: oleh **admin pusat**.
- **Prefix `employee_id` per perusahaan**: **wajib & unik** (`company_id` tetap patokan resmi penyaringan).
- **Domain**: **satu domain bersama** (perusahaan ditentukan dari akun, bukan subdomain).

## Pertanyaan terbuka (tersisa)
- Perusahaan pilot & target waktu: **belum ditentukan** (tidak memengaruhi arsitektur; hanya untuk penahapan/urgensi).

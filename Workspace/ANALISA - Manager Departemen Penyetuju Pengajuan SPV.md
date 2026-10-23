**Status**: 🟡 Daftar task dari `/analisa-kebutuhan` 2026-10-20. Keputusannya di [[ADR - 0190 Manager Departemen Menyetujui Pengajuan SPV dan Melihat KPI Departemen yang Dinaunginya]]; cara kerjanya di [[HRIS - Organization Structure]] §Manager departemen dan [[HRIS - Key Performance Index]]. Dok ini papan kerja, bukan arsitektur.

- **Ukuran**: **Sedang**. Dua repo harus berubah, masing-masing satu PR: `bip-erp` (field, pengalihan, gerbang KPI, jenjang) dan `erp-frontend` (kolom Manager, cakupan KPI). MyBharata **tidak** dihitung: tahap persetujuan dirender generik dari key `spv` (`mybharata-app/lib/src/features/requests/presentation/widgets/request_steps_stepper.dart:152-180`, branch `dev`) dan hak memutus dibaca dari backend (`lib/src/features/submission/presentation/widgets/submission_detail/reviewer_action_policy.dart:6-10`), sementara slot Manager tetap di `spv_status`.
- **Pemutus**: irfanarfianto (ADR Diterima 2026-10-20)

## Kebutuhan yang dijawab

Manajemen membuka posisi Manager yang menaungi seluruh departemen kecuali Finance, Beautyhacks, Kyura, dan Marketing Offline Distribution (Finance ditambahkan user 2026-10-20 sesudah deploy; tanpa perubahan kode). Manager menyetujui pengajuan **milik para SPV** dan melihat KPI seluruh karyawan departemen yang dinaunginya. Analisa menemukan pengajuan SPV hari ini tidak punya penyetuju yang bekerja: 16 dokumen di jalur "Direktur" sejak Juni, nol disetujui (prod 2026-10-20).

## Langkah tanpa kode (HR, bisa hari ini)

- Tambah jabatan Manager di departemen **Kesekretariatan**, lalu isi Data Pekerjaan orangnya di sana.
- **Jangan** jadikan Manager penyetuju departemen mana pun di layar Penyetuju Pengajuan.
- Opsional: isi Manager sebagai Atasan Langsung para SPV agar bagan organisasi benar.

## Urutan

1. Induk (`bip-erp`), tanpa PR sendiri.
2. **[BE]** `bip-erp`, satu PR.
3. **[FE]** `erp-frontend`, satu PR. Merge boleh kapan saja; **deploy sesudah [BE] live**.

---

### Induk: Manager departemen menyetujui pengajuan SPV dan melihat KPI departemen yang dinaunginya

- **Repo**: bip-erp
- **Issue**: [bip-erp#3328](https://github.com/bip-itteam-internal/bip-erp/issues/3328)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Pengajuan cuti/izin/sakit dan dinas milik penyetuju departemen (SPV) dialihkan ke slot bernama "Direktur" tanpa orang (`services/attendance/main.go:2441-2446`, `services/attendance/business_trip.go:159-164`). Prod 2026-10-20: 16 dokumen sejak 2026-06-13, 15 `Diabaikan`, 1 `Dibatalkan`, nol disetujui. Manajemen membuka posisi Manager yang menaungi tujuh departemen dan harus menyetujui pengajuan SPV-nya serta melihat KPI seluruh staf departemen itu.

## Keputusan

ADR "Manager Departemen Menyetujui Pengajuan SPV dan Melihat KPI Departemen yang Dinaunginya" (vault `Decisions/`). ADR berstatus 🟢 Diterima 2026-10-20 oleh irfanarfianto. Induk ini tanpa PR; ditutup manual saat semua sub-issue merged.

## Yang harus benar

- [ ] Sub-issue [BE] merged
- [ ] Sub-issue [FE] merged dan di-deploy sesudah [BE]

## Di luar cakupan

Koreksi absen dan tukar shift SPV; SPV Marketing; perbaikan jalur Direktur cadangan; MyBharata.

## Data / bukti pendukung

Lihat sub-issue [BE].

## Prasyarat

ADR Diterima 2026-10-20 (terpenuhi).

---

### [BE] Manager departemen di master data, pengalihan pengajuan SPV ke Manager, cakupan KPI Manager

- **Repo**: bip-erp
- **Issue**: [bip-erp#3329](https://github.com/bip-itteam-internal/bip-erp/issues/3329)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Penyetuju departemen wajib anggota departemen itu (`services/employee/department_approver.go:76-91`), sehingga Manager lintas departemen tak bisa dipasang. Pengajuan milik SPV dialihkan ke slot "Direktur" tanpa orang (`services/attendance/main.go:2441-2446`, `services/attendance/business_trip.go:159-164`) dan tak pernah disetujui. KPI per departemen hanya terbuka lewat cakupan supervisi token (`shared-library/common/kpi_reach.go:36-80`), yang tak boleh dilebarkan untuk Manager karena dibaca 11 gerbang di 6 service. Jenjang `manager` belum ada (`shared-library/models/employee/master_data.go:198-209`).

## Keputusan

ADR "Manager Departemen Menyetujui Pengajuan SPV dan Melihat KPI Departemen yang Dinaunginya", §1 s.d. §4. ADR berstatus 🟢 Diterima 2026-10-20 oleh irfanarfianto. Ringkas bentuknya:
- `master_department` satu field `employee_id` Manager; satu per departemen, boleh lintas departemen, akun aktif satu perusahaan; ditulis endpoint sendiri bergerbang `RequireHRISOrITSupervisor` dengan jejak audit.
- Pemohon cuti/izin/sakit/dinas = penyetuju departemennya → slot SPV berisi orang Manager (bila ada, aktif, bukan pemohon), selain itu slot "Direktur" seperti sekarang.
- Gerbang KPI cabang terpisah: lolos bila SEMUA departemen yang diminta dinaungi pemanggil, dibaca dari master saat permintaan.

## Yang harus benar

- [ ] `GET /master/departments/approvers` (atau endpoint sejenis) memuat Manager tiap departemen (id, nama, aktif); `PUT` penetapan Manager menolak akun nonaktif dan beda perusahaan, menerima `employee_id` kosong sebagai pelepasan, tidak memekarkan label grup, dan menulis jejak audit dalam transaksi yang sama.
- [ ] Menetapkan Manager **tidak** mengubah `is_supervisor`, `supervised_by`, maupun isi `supervised_departments` token siapa pun (diuji).
- [ ] Cuti/izin/sakit dibuat oleh penyetuju departemen yang departemennya punya Manager aktif → `spv_status.employee_id` = Manager, `full_name` = nama Manager; notifikasi pribadi ke Manager; Manager melihatnya di `/hr/requests?as=reviewer` dengan `boleh_putus` true; HR tetap tahap kedua.
- [ ] Sama untuk perjalanan dinas.
- [ ] Departemen tanpa Manager, Manager nonaktif, Manager = pemohon, atau gagal membaca Manager → perilaku lama (slot "Direktur") dan log; pengajuan tetap tersimpan.
- [ ] Staf biasa: penyetuju tidak berubah (uji regresi). Koreksi presensi dan tukar shift: tidak berubah (uji regresi).
- [ ] Attendance tidak menyalin aturan resolusi Manager; ia bertanya ke employee-service (satu sumber).
- [ ] `GET /kpi` dan `/kpi/auto-scores` dengan `department=<CSV>`: Manager lolos bila seluruh departemen dinaungi, 403 bila satu saja tidak; tidak ada perubahan bagi pemanggil lain (uji kontrol negatif: pemanggil tanpa penetapan tetap ditolak).
- [ ] Satu endpoint `me` yang mengembalikan daftar departemen yang dinaungi pemanggil (kosong bila tidak ada), untuk FE.
- [ ] `DefaultJobLevels()` memuat `manager` rank 45; `TestJenjangBukanSumbuHakAkses` tetap hijau.
- [ ] Minimal satu uji lewat Fiber (`app.Test`) untuk jalur galat endpoint penetapan, dan dijalankan sekali lewat gateway dev sebelum diklaim selesai.

## Di luar cakupan

Koreksi presensi, tukar shift, SPV Marketing, perbaikan jalur Direktur cadangan, MyBharata, persetujuan bertingkat umum (ADR 0137).

## Data / bukti pendukung

Diukur prod baca-saja 2026-10-20:
- `attendance_db.leave_request` slot `spv_status.full_name = "Direktur"` dan `employee_id` kosong: 9 (8 `Diabaikan`, 1 `Dibatalkan`); `business_trip_request`: 7 (7 `Diabaikan`). Nol disetujui.
- `employee_db.work_data` BIP: 225 karyawan, `supervisor_id` terisi 95. Penyetuju departemen (`is_supervisor:true`) 11, termasuk Direktur `BIP-0001-01-20` di Kesekretariatan; 0 dari 11 punya `supervisor_id`.
- `master_job_level`: 5 jenjang (pelaksana 10, senior 20, leader 30, supervisor 40, direktur 50).
- Departemen BIP: Human Resource, General Affair (`supervised_by: hris`), Tech Development, Kesekretariatan, Finance, Beautyhacks, Kyura, Manufaktur, Quality, Procurement, Marketing Offline Distribution, Percetakan.

## Prasyarat

ADR Diterima 2026-10-20 (terpenuhi).

---

### [FE] Kolom Manager di layar Penyetuju Pengajuan dan cakupan KPI Manager

- **Repo**: erp-frontend
- **Issue**: [erp-frontend#2639](https://github.com/bip-itteam-internal/erp-frontend/issues/2639)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Layar Penyetuju Pengajuan hanya mengenal satu penyetuju per departemen dari anggota departemen itu (`src/features/hris/master-data/components/department-approver-manager.tsx:46-58`, `lib/penyetuju.ts:87-97`). Cakupan KPI web terkunci ke satu departemen atau bawahan langsung (`src/features/hris/kpi/hooks/use-cakupan-kpi.ts:24-80`), dan menu KPI Portal hanya untuk supervisor atau pemilik bawahan (`src/components/layout/kpi-menu.ts:19-28`).

## Keputusan

ADR "Manager Departemen Menyetujui Pengajuan SPV dan Melihat KPI Departemen yang Dinaunginya", §1 dan §3. ADR berstatus 🟢 Diterima 2026-10-20 oleh irfanarfianto. Ringkas: HR memilih satu Manager per departemen dari seluruh karyawan aktif perusahaan; Manager melihat KPI seluruh karyawan departemen yang dinaunginya; FE tidak menghitung cakupan sendiri, ia membaca endpoint `me` dari BE.

## Yang harus benar

- [ ] Layar Penyetuju Pengajuan menampilkan kolom Manager per departemen (nama, jabatan, status aktif), dengan pemilih karyawan aktif lintas departemen satu perusahaan, aksi lepas, dialog konfirmasi yang menyebut bahwa hanya pengajuan baru yang terpengaruh, dan umpan balik sukses/gagal.
- [ ] Kolom Manager dijelaskan sebagai "menyetujui pengajuan milik penyetuju departemen ini", terpisah dari kolom penyetuju; tidak ada aksi yang mengubah penyetuju saat Manager diubah.
- [ ] Menu KPI Portal terbuka bagi pemanggil yang menaungi minimal satu departemen.
- [ ] Halaman KPI: Manager dapat memilih departemen-departemen yang dinaunginya (satu atau gabungan) dan melihat seluruh karyawannya; pilihan di luar itu tidak ditawarkan.
- [ ] Semua teks baru lewat `t()` di `id.ts` dan `en.ts`; loading `Skeleton`; lima keadaan layar (`rules/ui-checklist.md`).
- [ ] Bila BE belum di-deploy (field atau endpoint tidak ada), layar tetap jalan seperti sekarang tanpa galat.
- [ ] `pnpm tsc --noEmit`, `pnpm lint`, `pnpm build` lolos; `pnpm test` tanpa kegagalan baru terhadap baseline.

## Di luar cakupan

MyBharata; layar Atasan Langsung; perubahan Portal Persetujuan (sudah generik).

## Data / bukti pendukung

Tidak perlu data prod tambahan.

## Prasyarat

Sub-issue [BE] merged. **Deploy sesudah [BE] live di prod.**

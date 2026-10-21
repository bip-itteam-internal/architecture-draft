> **Status**: 🟢 Diterima, 2026-10-20, oleh irfanarfianto. Pemutus: irfanarfianto. Opsi A dipilih lewat `/analisa-kebutuhan`; pengerjaan diperintahkan di sesi yang sama. Kode belum ada. Pecahan kerja: [[ANALISA - Manager Departemen Penyetuju Pengajuan SPV]] · issue bip-erp#3328 (induk), bip-erp#3329 [BE], erp-frontend#2639 [FE].

> ⚠️ **Diubah sebagian oleh [[ADR - 0193 Struktur Organisasi Direksi, Divisi, Departemen dengan Unit Pimpinan Berjenis dan Manager dari Kepala Divisi]] (🟡 Diusulkan 2026-10-21)**: Manager departemen akan DITURUNKAN dari kepala divisi (bukan diisi per departemen lewat `manager_employee_id`), dan Direktur serta Manager pindah ke unit pimpinan Direksi (§5 di bawah tidak berlaku lagi setelah ADR itu diterima dan berkode). Status kode ADR ini: live prod 2026-10-20 (bip-erp #3345, erp-frontend #2643).

## Untuk Manajemen

**Yang berubah di layar.**
- Di Pengaturan, layar Penyetuju Pengajuan mendapat satu kolom baru: **Manager**. HR memilih satu orang Manager untuk tiap departemen yang dinaunginya.
- Mulai saat itu, cuti, izin, sakit, dan perjalanan dinas **milik SPV** departemen tersebut masuk ke Manager. Manager mendapat notifikasi pribadi dan memutusnya dari Portal Persetujuan, di web maupun MyBharata. Sesudah Manager, HR tetap memeriksa seperti sekarang.
- Manager mendapat menu KPI yang memuat **seluruh karyawan** di departemen-departemen yang dinaunginya, bukan hanya para SPV.

**Siapa yang terdampak.**
- Para SPV di departemen yang dinaungi: pengajuan mereka kini punya penyetuju yang benar-benar menerimanya. Sejak Juni 2026, 16 pengajuan SPV dialihkan ke "Direktur" dan **tak satu pun disetujui**: 15 kedaluwarsa otomatis, 1 dibatalkan.
- HR: mengisi kolom Manager di Master Data.
- Staf biasa: tidak berubah. Pengajuan mereka tetap disetujui SPV masing-masing.

**Yang TIDAK dijanjikan.**
- Koreksi absen dan tukar shift milik SPV **tidak** lewat Manager. Keduanya tetap langsung ke HR.
- SPV di Finance, Beautyhacks, Kyura, dan Marketing Offline Distribution **tidak** dinaungi Manager. Pengajuan mereka tetap ke jalur Direktur yang ada, termasuk masalahnya; memperbaikinya keputusan terpisah.
- Manager **tidak** menggantikan SPV. Ia tidak menyetujui pengajuan staf dan tidak mendapat hak di modul lain (keuangan, pengadaan, rekrutmen, form).
- Jabatan atau jenjang "Manager" saja **tidak** memberi wewenang apa pun. Wewenang lahir dari penetapan HR di kolom Manager.
- Pengajuan yang sudah berjalan tidak berpindah. Yang berlaku hanya pengajuan baru sesudah kolomnya diisi.

**Besaran kerja.** Sedang: satu perubahan backend dan satu perubahan web, masing-masing satu PR. MyBharata tidak berubah. HR sudah bisa memasukkan orangnya ke jabatan Manager hari ini, sebelum fitur ini jadi.

## Deskripsi

*Seorang Manager menaungi beberapa departemen. HR menetapkannya per departemen di master data, dan penetapan itu, bukan nama jabatan atau jenjang, yang menjadi sumber dua hal: Manager menggantikan slot "Direktur" sebagai penyetuju pertama cuti/izin/sakit dan perjalanan dinas milik penyetuju departemen itu sendiri, dan Manager melihat KPI seluruh karyawan aktif departemen-departemen tersebut. Penanda ini sengaja bukan `supervised_by`, bukan penyetuju departemen, dan bukan Master Divisi.*

- **Status**: 🟢 Diterima, kode belum ada (lihat baris status di atas). Analisa: [[ANALISA - Manager Departemen Penyetuju Pengajuan SPV]]
- **Path di repo**: `bip-erp/shared-library/models/employee/master_data.go` (field Manager + jenjang Manager) · `bip-erp/services/employee/department_manager.go` (baru) · `bip-erp/services/employee/main.go` (cabang KPI) · `bip-erp/services/attendance/main.go`, `bip-erp/services/attendance/business_trip.go` (pengalihan) · `erp-frontend/src/features/hris/master-data/components/department-approver-manager.tsx` · `erp-frontend/src/features/hris/kpi/hooks/use-cakupan-kpi.ts` · `erp-frontend/src/components/layout/kpi-menu.ts`
- **Tanggal**: 2026-10-20

## Context

Manajemen membuka posisi Manager yang menaungi seluruh departemen kecuali Marketing (Beautyhacks, Kyura, Marketing Offline Distribution) dan **Finance**, mulai minggu 2026-10-26. Finance ditambahkan ke pengecualian oleh user 2026-10-20 sesudah deploy; kode tidak berubah karena cakupan ditentukan HR saat mengisi kolom Manager per departemen. Permintaan awalnya "Manager ikut menyetujui pengajuan dan melihat KPI seluruh staf di bawahnya". Wawancara mempersempitnya: Manager **hanya** menyetujui pengajuan milik para SPV. Staf tetap disetujui SPV.

Yang ditemukan di kode (`bip-erp` `origin/main` `c2ea6368`) dan data prod (diukur baca-saja 2026-10-20):

1. **Pengajuan SPV sekarang tidak punya penyetuju yang bekerja.** Bila pemohon adalah penyetuju departemennya sendiri, slot SPV dikosongkan lalu diberi nama "Direktur" (`services/attendance/main.go:2441-2446`, `services/attendance/business_trip.go:159-164`). Yang boleh memutus slot itu ditentukan nama jabatan pemanggil (`services/attendance/penyetuju_jabatan.go:50-68`, `common.SetaraDirektur`). Notifikasinya siaran ke seluruh Kesekretariatan (`services/attendance/notification.go:326-344`). Prod: `leave_request` 9 dokumen (8 `Diabaikan`, 1 `Dibatalkan`), `business_trip_request` 7 dokumen (7 `Diabaikan`), rentang 2026-06-13 s.d. 2026-10-16, **nol disetujui**. Rincian sebabnya di [[HRIS - Employee Request & Approval]] §Pengajuan yang MATI.
2. **Bahan yang ada tidak cocok dipakai ulang tanpa efek samping.**
	- **Penyetuju departemen** (`is_supervisor`) wajib anggota departemen itu dan satu per departemen (`services/employee/department_approver.go:76-91`). Manager lintas departemen tak bisa dipasang di sana.
	- **`supervised_by`** satu tingkat dan melebur departemen jadi satu grup seperti HRGA ([[HRIS - Organization Structure]]). Memakainya membuat tujuh departemen tampil sebagai satu blok KPI. Lebih berat lagi, cakupan supervisi di token login (`resolveSupervisedDepartments`, `services/employee/department_scope.go:96`) dibaca 11 gerbang di 6 service (form-builder, recruitment, procurement budget, task-management, assistant, KPI), sehingga Manager diam-diam mendapat jangkauan supervisor di semuanya.
	- **Atasan langsung** (`supervisor_id`) mengatur cakupan tampilan, bukan wewenang, dan satu tingkat (`services/employee/subordinate.go:81-103`). Prod: 95 dari 225 karyawan BIP terisi, 0 dari 11 penyetuju departemen.
	- **Master Divisi** khusus pelaporan ([[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]], masih 🟡 Diusulkan).
	- **Jenjang** bukan sumber hak ([[ADR - 0030 RBAC Tiga Sumbu dengan Hak Menempel di Posisi]], dikunci `TestJenjangBukanSumbuHakAkses`). Jenjang Manager belum ada; celah rank 45 sudah disiapkan (`shared-library/models/employee/master_data.go:198-209`).
3. **KPI per departemen** digerbang `RequireKPIDepartmentRBAC` (`shared-library/common/roles.go`), yang sudah menerima beberapa departemen sekaligus dengan aturan "semua harus terjangkau". Cakupan `division` paket KPI membaca cakupan supervisi token (`shared-library/common/kpi_reach.go:36-80`), jalur yang ditolak di butir 2.
4. **Peraturan Perusahaan** (`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`) tidak mengatur siapa yang menyetujui cuti, izin, atau dinas, sehingga keputusan ini tidak menyimpang dari pasal mana pun.
5. **Status dok yang menjadi pijakan.** [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]] masih 🟡 Diusulkan dengan Decision TBD; keputusan ini tidak menunggu ADR itu, tetapi mematuhi aturan yang sudah berlaku darinya: alur baru tidak menambah literal nama jabatan di gerbang.

## Decision

### 1. "Manager departemen" adalah penetapan orang per departemen di master data

`master_department` mendapat satu field baru berisi `employee_id` Manager (nama field ditetapkan `/plan`). Aturannya:
- Satu departemen paling banyak **satu** Manager; satu Manager boleh menaungi banyak departemen.
- Manager **tidak** wajib anggota departemen yang dinaunginya. Calon wajib akun aktif dan satu perusahaan dengan departemennya.
- Ditetapkan lewat endpoint tulis tersendiri dengan gerbang yang sama seperti penyetuju departemen (`RequireHRISOrITSupervisor`), dengan jejak audit di dalam transaksi seperti `department_approver_log`. `employee_id` kosong melepas penetapan.
- `:key` adalah satu departemen, **tidak** dimekarkan ke grup (alasan sama dengan penyetuju departemen).
- Penanda ini **bukan** `supervised_by`, **bukan** `is_supervisor`, dan **tidak** masuk cakupan supervisi token login. Satu-satunya pembaca resolusinya adalah employee-service; service lain bertanya ke sana, tidak menyalin aturannya.

### 2. Pengajuan milik penyetuju departemen mengalir ke Manager

Pada cuti/izin/sakit dan perjalanan dinas, di titik yang sekarang mengalihkan ke "Direktur" (pemohon = penyetuju departemennya):
- Bila departemen pemohon punya Manager yang aktif dan Manager itu bukan pemohon sendiri, slot SPV diisi **orang** Manager (`employee_id`, nama lengkap, departemennya), dan notifikasinya pribadi ke Manager dengan kategori inbox yang sudah ada.
- Selain itu, perilaku sekarang dipertahankan apa adanya: slot "Direktur".
- Tahap HR sesudahnya tidak berubah. Penyetuju disnapshot saat pengajuan dibuat, jadi pengajuan yang sudah berjalan tidak berpindah.
- Koreksi presensi dan tukar shift **tidak** disentuh (`services/attendance/correction.go:437-450`, `services/attendance/func.go:1161-1202`).
- Gagal membaca Manager dari employee-service = jatuh ke slot "Direktur" dan dicatat di log, bukan menolak pengajuan. Pengajuan tetap bisa dibuat; yang hilang hanya pengalihannya.

Karena slot berisi orang, Portal Persetujuan (`services/employee/antrean_pengajuan.go`), web, dan MyBharata membaca `boleh_putus` dari jalur yang sudah ada tanpa perubahan.

### 3. Manager melihat KPI seluruh karyawan departemen yang dinaunginya

- Gerbang KPI mendapat cabang terpisah: pemanggil lolos untuk sebuah permintaan bila **seluruh** departemen yang diminta dinaungi olehnya. Aturan "semua, bukan salah satu" sama dengan gerbang yang ada.
- Dibaca dari master data saat permintaan, bukan dari token, sehingga penetapan berlaku tanpa login ulang.
- Cabang ini **khusus KPI**, tidak melebarkan `RequireKPIDepartmentRBAC` bagi siapa pun yang lain dan tidak menyentuh gerbang modul lain.
- Cakupannya per departemen penuh, bukan rantai atasan langsung, sehingga tidak bergantung pada `supervisor_id` yang baru separuh terisi.
- Web: halaman KPI dan menu KPI Portal mengenali cakupan "departemen yang saya naungi" lewat satu endpoint `me` di employee-service; frontend tidak menghitung sendiri.

### 4. Jenjang "Manager" ditambahkan sebagai penanda saja

Satu entri `manager`, rank 45, di `DefaultJobLevels()`. Seeder per key menyisipkannya saat deploy. Tidak ada kode yang membaca jenjang ini untuk wewenang.

### 5. Penempatan Manager sendiri

Manager ditempatkan di departemen **Kesekretariatan**, yang penyetujunya Direktur sebagai orang (prod 2026-10-20). Pengajuan milik Manager karena itu mengalir ke Direktur lewat jalur penyetuju departemen biasa, tanpa kode tambahan. Ini keputusan data HR, bukan aturan kode.

## Consequences

- ✅ Pengajuan SPV di tujuh departemen (Human Resource, General Affair, Tech Development, Manufaktur, Quality, Procurement, Percetakan) mendapat penyetuju yang menerima notifikasi pribadi, menggantikan jalur yang terukur 0 dari 16.
- ✅ Tidak ada hak baru di modul selain KPI, dan tidak ada departemen yang dilebur.
- ✅ MyBharata dan Portal Persetujuan tidak berubah.
- ⚠️ Konsep keempat di sekitar departemen (penyetuju, induk `supervised_by`, atasan langsung, Manager). Dok [[HRIS - Organization Structure]] wajib memuat tabel pembedanya, karena tiga yang lama sudah berkali-kali tertukar.
- ⚠️ Jalur Direktur tetap hidup sebagai cadangan, beserta masalahnya, untuk SPV Marketing dan saat Manager kosong. Mengukur dan memperbaikinya di luar keputusan ini.
- ⚠️ Pengajuan yang tak diputus 24 jam tetap ditandai `Diabaikan`. Manager mewarisi tenggat itu.
- ⚠️ Label tahap di MyBharata versi Inggris tetap "Supervisor Review" untuk pengajuan yang diputus Manager; versi Indonesia "Atasan" sudah netral. Diterima.
- Deploy: BE (`employee-service`, `attendance-service`) sebelum FE. Tidak ada env baru dan tidak ada kategori inbox baru. Prod dijalankan manusia.

Terkait: [[REF - Alur Persetujuan]] · [[HRIS - Perjalanan Dinas]] · [[HRIS - Key Performance Index]] · [[CORE - RBAC dan Permission Set]]

> **Status**: 🟢 Diterima, 2026-10-21, oleh irfanarfianto. Dari `/analisa-kebutuhan` (opsi A dipilih user; direvisi hari yang sama: Manager dipilih per departemen bebas, penyetuju boleh lintas departemen). Pemutus: irfanarfianto. Kode belum ada. Pecahan kerja: [[ANALISA - Struktur Organisasi Bertingkat dan Peta Penyetuju]].

## Untuk Manajemen

**Yang berubah di layar.**
- Struktur organisasi di ERP menjadi bertingkat seperti perusahaan pada umumnya: **Direksi** di puncak, para **Manager** di bawahnya, lalu **Departemen**, lalu orang. **Divisi** (mis. Operational, Supporting) tetap ada untuk pengelompokan laporan.
- Direktur dan Manager tidak lagi tercatat sebagai anggota departemen operasional. Mereka tercatat di unit pimpinan **Direksi**.
- HR memilih **Manager untuk departemen mana saja**, bebas dan lintas divisi, di layar Penyetuju Pengajuan (kolom Manager yang sudah ada sejak 2026-10-20).
- Departemen yang tidak punya SPV bisa dipilihkan **penyetuju dari mana saja**: Leader-nya, SPV departemen lain, Manager, atau Direktur. Bila belum dipilih, pengajuan otomatis ke Manager departemen itu, lalu ke Direktur, sehingga tidak ada pengajuan yang mentok.
- Bagan organisasi tampil berjenjang: Direksi → Manager → Departemen → orang.
- Pengajuan cuti/izin/dinas Direktur langsung ke HRD tanpa atasan. Pengajuan Manager disetujui Direktur.

**Siapa yang terdampak.** Direktur dan Manager (pindah unit, hak akses wajib utuh), HR (memilih Manager dan penyetuju, memetakan departemen ke divisi), staf Kesekretariatan (penyetuju mereka berganti dari Direktur ke Corporate Secretary), penyetuju lintas departemen (mendapat wewenang melihat dan memutus pengajuan staf departemen yang dipilihkan untuknya).

**Yang TIDAK dijanjikan.**
- Persetujuan berjenjang umum (staf → SPV → Manager → Direktur untuk SEMUA pengajuan) tidak termasuk. Aturan tetap: staf disetujui penyetuju departemen, penyetuju departemen disetujui Manager, Manager disetujui Direktur.
- Pengaturan "siapa menyetujui apa" dari satu halaman diputuskan terpisah (ADR "Peta Penyetuju per Orang Lintas Modul sebagai Tahap Pertama Persetujuan Terpusat").
- Divisi tidak punya kepala dan tidak ikut alur persetujuan.
- Departemen Kesekretariatan tidak dihapus dan tidak berganti nama.
- Pengajuan yang sedang berjalan tidak dipindah.

**Besaran kerja.** Besar: dua bagian backend, satu bagian web, dan satu skrip migrasi data yang dijalankan manusia. MyBharata hanya terdampak kosmetik.

## Deskripsi

*Organisasi dimodelkan Direksi → (Manager) → Departemen, dengan Divisi sebagai pengelompokan laporan. Unit pimpinan (Direksi) adalah baris master departemen berpenanda **jenis = pimpinan**, sehingga invarian "setiap karyawan punya unit" yang dipakai presensi, hak akses, payroll, dan pengajuan tetap utuh, sementara semua tempat yang menganggap departemen = unit operasional menanganinya dengan sengaja. Manager tetap ditetapkan per departemen (ADR 0190) dan bebas lintas divisi; penyetuju departemen menjadi pilihan eksplisit yang boleh lintas departemen, dengan cadangan otomatis Manager lalu Direktur.*

- **Status**: 🟢 Diterima, kode belum ada (lihat baris status di atas).
- **Path di repo**: `bip-erp/shared-library/models/employee/master_data.go` (field jenis departemen, penyetuju eksplisit) · `bip-erp/services/employee/peran_dari_jabatan.go` · `bip-erp/services/employee/permission_resolve.go` · `bip-erp/services/employee/master_data.go` (system-list) · `bip-erp/services/employee/main.go` (data-type department, `/list?type=supervisor`) · `bip-erp/services/employee/department_approver.go` · `bip-erp/services/employee/supervisor_lookup.go` · `bip-erp/services/employee/department_manager.go` · `bip-erp/services/employee/org_chart.go` · `bip-erp/services/attendance/main.go`, `business_trip.go`, `manager_departemen.go`, `schedule_list.go`, `jadwal_buatan_hr.go`, `notification.go` · `erp-frontend/src/features/hris/org-chart/lib/bangun-pohon.ts` · `erp-frontend/src/features/hris/master-data/` (departemen, penyetuju) · skrip migrasi prod `.ps1` (baru)
- **Tanggal**: 2026-10-21

## Context

Manajemen menolak penempatan Direktur dan Manager di departemen Kesekretariatan ([[ADR - 0190 Manager Departemen Menyetujui Pengajuan SPV dan Melihat KPI Departemen yang Dinaunginya]] §5) dan meminta struktur "selayaknya perusahaan". Praktik umum sistem HR: tidak ada karyawan tanpa unit; pimpinan menjadi anggota unit tingkat atas (Direksi), kepala unit adalah relasi terpisah dari keanggotaan, dan laporan bisa dibaca per tingkat. Dua permintaan tambahan user di hari yang sama: **departemen tanpa SPV bisa memilih penyetuju lintas departemen** (Leader/SPV lain/Manager/Direktur), dan **Manager bisa dipilih untuk menaungi departemen mana saja**.

Keadaan sekarang (`bip-erp` `origin/main` `b7718889`, prod baca-saja 2026-10-21):
- Direktur `BIP-0001-01-20` tercatat di Kesekretariatan sebagai penyetuju departemen itu, bersama staf yang melapor langsung kepadanya (Corporate Secretary, Internal Audit, Legal, Company Branding, Graphic Design, Video Editor, QA RND). HR sudah membuat jabatan "Manager Operational" di departemen yang sama, tanpa jenjang.
- [[HRIS - Organization Structure]] menyatakan organisasi bertingkat "perlu keputusan tersendiri" yang belum pernah diambil. Master Divisi ([[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]], 🟡 Diusulkan, master divisi merged) dibatasi untuk pelaporan; 8 dari 12 departemen BIP belum dipetakan.
- ADR 0190 (🟢 Diterima, live prod 2026-10-20): Manager per departemen lewat `master_department.manager_employee_id`, satu Manager boleh banyak departemen, lintas departemen; 0 departemen terisi di prod per 2026-10-20.
- Penyetuju departemen wajib anggota departemen itu (`services/employee/department_approver.go:76-91`) karena lookup menyaring `{is_supervisor, department}`; rantainya: `is_supervisor` sendiri → induk `supervised_by` → tebakan judul `Supervisor|^Leader$` (`services/employee/supervisor_lookup.go:162-237`). Di prod hanya General Affair yang tak punya penyetuju sendiri (mengikuti HR lewat `supervised_by`).

Titik yang patah bila unit pimpinan dibuat sebagai departemen biasa, semua diverifikasi di kode:
1. Peran Direktur di 15 modul diturunkan dari pasangan (nama departemen, jabatan): `peranJabatan` (`services/employee/peran_dari_jabatan.go:297-303`, tabel `"kesekretariatan" → "direktur"` `:223-240`), dipanggil dengan `work.Department` (`services/employee/hak_token.go:133`). Pindah departemen = semua peran hilang tanpa galat.
2. Paket izin posisi dicari lewat departemen (`services/employee/permission_resolve.go:127-135`).
3. Cuti/dinas pemohon di unit tanpa penyetuju dibalas 500 "Couldn't find suitable supervisor" (`services/attendance/main.go:2380-2382`, `business_trip.go:153-155`).
4. Key setiap departemen otomatis menjadi kunci modul di daftar peran (`services/employee/master_data.go:596-597`).
5. Unit baru masuk ke ±50 pemakai daftar departemen di web (26 `useDataTypes({endpoint:"department"})` + ±25 `useFetchDepartments`); picker jadwal membalas 400 untuk departemen tak dikenal (`services/attendance/schedule_list.go:107`, UNSET khusus Kesekretariatan `:91-95`).
6. Slot "Direktur" berdepartemen Kesekretariatan dan notifikasinya disiarkan ke departemen itu (`services/attendance/manager_departemen.go:70`, `notification.go:339-340`).
7. Bagan organisasi berkerangka departemen saja (`erp-frontend/src/features/hris/org-chart/lib/bangun-pohon.ts:8-11,181-185`).
8. `supervised_by` melebur filter dan cakupan supervisi (`shared-library/models/employee/department_scope.go:70-99`).
9. Override penyetuju Tech Development ditulis di kode (`services/attendance/main.go` `getSupervisorData`), tak terlihat di layar penyetuju.

Pola "pengajuan tanpa atasan langsung ke HR" sudah ada di koreksi presensi (`services/attendance/correction.go:437-450`). Peraturan Perusahaan (`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`) tidak mengatur penyetuju.

## Decision

### 1. Tingkat: Direksi → Manager → Departemen; Divisi untuk laporan

- **Direksi**: satu unit pimpinan per perusahaan, beranggotakan Direktur dan para Manager.
- **Manager**: menaungi departemen yang ditetapkan HR (ADR 0190, `manager_employee_id`), **bebas departemen mana pun dan lintas divisi**. Ini satu-satunya sumber "siapa Manager departemen ini".
- **Departemen**: seperti sekarang. Kesekretariatan tetap departemen biasa di bawah Direksi, tanpa ganti nama.
- **Divisi**: `master_divisi` + `divisi_key` tetap pengelompokan laporan, **tanpa kepala**, tidak ikut alur persetujuan.

### 2. Unit pimpinan = baris `master_department` berjenis `pimpinan`

`master_department` mendapat field **jenis** (`departemen` bawaan, atau `pimpinan`). Dokumen lama tanpa field dibaca sebagai `departemen`. Setiap karyawan tetap punya `work_data.department`; untuk Direktur dan Manager isinya nama unit Direksi.

Wajib ditangani dengan sengaja untuk jenis `pimpinan` (daftar tertutup, tiap butir dikunci test):
- daftar departemen bawaan (`/data-type/department`, grouped, filter options) **tidak** memuat unit pimpinan, kecuali diminta eksplisit (parameter baru);
- system-list **tidak** menjadikan key unit pimpinan sebagai kunci modul;
- peran turunan dan paket izin posisi tetap berlaku: tabel peran Direktur dikunci unit Direksi (bukan lagi Kesekretariatan), dan `position_items` Direktur beserta paketnya pindah ke baris Direksi lewat migrasi;
- jadwal: unit pimpinan menerima jadwal UNSET seperti Kesekretariatan hari ini, dan picker jadwal tak membalas 400;
- KPI per departemen dan kartu ringkasan tidak memperlakukan unit pimpinan sebagai departemen operasional.

### 3. Manager tetap per departemen (ADR 0190), bebas lintas divisi

Tidak ada perubahan bentuk pada penetapan Manager: satu Manager per departemen, satu orang boleh menaungi banyak departemen di divisi mana pun. Yang berubah hanya tempat Manager tercatat (unit Direksi, bukan Kesekretariatan; ADR 0190 §5 diganti oleh keputusan ini). KPI Manager dan pengalihan pengajuan SPV ke Manager tetap seperti ADR 0190.

### 4. Alur pengajuan pimpinan

- **Direktur** (penyetuju unit Direksi): cuti/izin/sakit/dinas miliknya **tanpa tahap atasan, langsung tahap HR**, mengikuti pola koreksi presensi `correction.go:437-450`. Tidak lagi jatuh ke slot "Direktur".
- **Manager** (anggota Direksi): disetujui penyetuju unit Direksi = Direktur **sebagai orang**, lalu HR.
- **Kesekretariatan**: penyetujunya Corporate Secretary (pilihan HR di layar Penyetuju Pengajuan).
- Slot "Direktur" tanpa orang tidak lagi dibutuhkan setelah §4b (cadangan selalu berakhir di Direktur sebagai orang); slot lama hanya tersisa untuk dokumen yang sudah ada.
- Override penyetuju yang ditulis di kode (`getSupervisorData`) dihapus; penyetuju IT kembali sepenuhnya dari data.

### 4b. Penyetuju departemen dipilih HR, boleh lintas departemen, dengan cadangan otomatis

- **Penyetuju sebuah departemen disimpan sebagai pilihan eksplisit di master departemen** (satu orang, akun aktif, satu perusahaan), ditetapkan di layar Penyetuju Pengajuan dengan jejak audit. Calonnya **boleh dari departemen lain**: Leader departemen itu, SPV departemen lain, Manager, atau Direktur. Syarat lama "wajib anggota departemen" (`validasiPenyetuju`) dicabut.
- Pilihan eksplisit menjadi langkah PERTAMA resolver penyetuju (`atasanDepartemen`), sebelum `is_supervisor` anggota. `is_supervisor` anggota yang ada dimigrasikan menjadi pilihan eksplisit, lalu tidak lagi dipakai sebagai sumber penyetuju (satu fakta satu tempat).
- **Penyetuju pilihan hanya memberi wewenang MENYETUJUI pengajuan departemen itu**, tidak memberi cakupan supervisi modul (token `supervised_departments`, KPI per departemen). Prinsip yang sama dengan Manager di ADR 0190.
- **Cadangan otomatis bila departemen tak punya pilihan**: Manager departemen itu, lalu Direktur (penyetuju unit Direksi). Tebakan judul jabatan `Supervisor|^Leader$` dan `supervised_by` untuk persetujuan dihapus dari rantai. Pengajuan tidak pernah lagi dibalas 500 "Couldn't find suitable supervisor" selama perusahaan punya Direktur.
- Pengajuan milik penyetuju pilihan itu sendiri: Manager departemen, lalu Direktur (aturan ADR 0190 tetap).

### 5. Bagan organisasi bertingkat

Endpoint bagan mengirim tingkat: unit Direksi (Direktur), para Manager beserta departemen yang dinaungi, departemen beserta `divisi_key` dan penyetujunya. Web menyusun pohon Direksi → Manager → Departemen → orang; departemen tanpa Manager menempel langsung di bawah Direksi. Divisi tampil sebagai pengelompokan/filter, bukan simpul pohon. Atasan langsung lintas unit tetap ditampilkan.

### 6. Migrasi data prod dijalankan manusia

Skrip `.ps1` dua fase (dry-run, lalu apply) dengan cadangan `mongodump` dan rollback: buat unit Direksi, pindahkan Direktur dan Manager, pindahkan `position_items` + paket Direktur, tetapkan penyetuju Direksi = Direktur, migrasikan `is_supervisor` tiap departemen menjadi pilihan eksplisit, tetapkan penyetuju Kesekretariatan dan pilihan lintas departemen serta Manager per departemen sesuai keputusan HR, petakan departemen ke divisi. Gerbang verifikasi: hak efektif Direktur sebelum = sesudah (`GET /account/effective-access`), dan penyetuju tiap departemen sebelum = sesudah kecuali yang sengaja diubah HR.

## Consequences

- ✅ Struktur sesuai praktik umum tanpa mematahkan presensi, hak akses, payroll, dan pengajuan.
- ✅ HR bebas menyusun cakupan Manager dan penyetuju tanpa dibatasi divisi atau keanggotaan departemen.
- ✅ Pengajuan tidak lagi mati di slot tanpa orang atau dibalas 500.
- ⚠️ Daftar titik di §2 tertutup tapi panjang; satu yang terlewat = kegagalan senyap. Tiap titik wajib punya test, dan migrasi wajib membandingkan hak efektif Direktur sebelum dan sesudah.
- ⚠️ Mengubah aturan "penyetuju wajib anggota departemen" ([[HRIS - Organization Structure]] §Aturan yang berlaku sekarang, `department_approver.go:76-91`): penyetuju pilihan HR boleh lintas departemen. Penyetuju dari luar melihat dan memutus pengajuan staf departemen itu (data cuti/dinas mereka), wewenang yang disengaja dan tampil di peta penyetuju ADR 0194.
- ⚠️ Mengubah fakta di ADR 0190 §5 (Manager di Kesekretariatan). Bentuk penetapan Manager ADR 0190 tetap.
- ⚠️ Corporate Secretary menjadi penyetuju Kesekretariatan; perlu persetujuan HR/manajemen sebelum migrasi.
- Deploy: BE sebelum FE; `shared-library` berubah sehingga service pembaca model departemen ikut naik; migrasi data sesudah BE live; tanpa env dan kategori inbox baru.

Terkait: [[HRIS - Organization Structure]] · [[ADR - 0194 Peta Penyetuju per Orang Lintas Modul sebagai Tahap Pertama Persetujuan Terpusat]] · [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]] · [[REF - Alur Persetujuan]]

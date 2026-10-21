> **Status**: 🟡 **Diusulkan**, 2026-10-21, dari `/analisa-kebutuhan` (opsi A dipilih user). Pemutus: irfanarfianto. Kode belum ada. Pecahan kerja: [[ANALISA - Struktur Organisasi Bertingkat dan Peta Penyetuju]].

## Untuk Manajemen

**Yang berubah di layar.**
- Struktur organisasi di ERP menjadi bertingkat seperti perusahaan pada umumnya: **Direksi** di puncak, lalu **Divisi** (mis. Operational, Supporting), lalu **Departemen**, lalu orang.
- Direktur dan Manager tidak lagi tercatat sebagai anggota departemen operasional. Mereka tercatat di unit pimpinan **Direksi**.
- Setiap Divisi punya **kepala** (Manager). HR cukup menetapkan kepala divisi sekali; semua departemen di divisi itu otomatis berada di bawahnya. Kolom Manager per departemen yang dibuat kemarin tidak perlu diisi satu per satu lagi.
- Bagan organisasi tampil berjenjang: Direksi → Divisi → Departemen → orang.
- Pengajuan cuti/izin/dinas Direktur langsung ke HRD tanpa atasan. Pengajuan Manager disetujui Direktur.

**Siapa yang terdampak.** Direktur dan Manager (pindah unit, hak akses wajib utuh), HR (mengisi kepala divisi dan memetakan departemen ke divisi), staf Kesekretariatan (penyetuju mereka berganti dari Direktur ke Corporate Secretary).

**Yang TIDAK dijanjikan.**
- Persetujuan berjenjang umum (staf → SPV → Manager → Direktur untuk SEMUA pengajuan) tidak termasuk. Aturan sekarang tetap: staf disetujui SPV, SPV disetujui Manager, Manager disetujui Direktur.
- Pengaturan "siapa menyetujui apa" dari satu halaman diputuskan terpisah (ADR "Peta Penyetuju per Orang Lintas Modul sebagai Tahap Pertama Persetujuan Terpusat").
- Departemen Kesekretariatan tidak dihapus dan tidak berganti nama.
- Data lama (pengajuan yang sedang berjalan) tidak dipindah.

**Besaran kerja.** Besar: dua bagian backend, satu bagian web, dan satu skrip migrasi data yang dijalankan manusia. MyBharata hanya terdampak kosmetik.

## Deskripsi

*Organisasi dimodelkan Direksi → Divisi → Departemen. Unit pimpinan (Direksi) adalah baris master departemen berpenanda **jenis = pimpinan**, sehingga invarian "setiap karyawan punya unit" yang dipakai presensi, hak akses, payroll, dan pengajuan tetap utuh, sementara semua tempat yang menganggap departemen = unit operasional menanganinya dengan sengaja. Divisi mendapat kepala; Manager departemen diturunkan dari kepala divisinya, menggantikan pengisian per departemen dari ADR 0190.*

- **Status**: 🟡 Diusulkan, 2026-10-21. Kode belum ada.
- **Path di repo**: `bip-erp/shared-library/models/employee/master_data.go` (field jenis departemen, kepala divisi) · `bip-erp/services/employee/peran_dari_jabatan.go` · `bip-erp/services/employee/permission_resolve.go` · `bip-erp/services/employee/master_data.go` (system-list) · `bip-erp/services/employee/main.go` (data-type department) · `bip-erp/services/employee/department_manager.go` · `bip-erp/services/employee/master_divisi.go` · `bip-erp/services/employee/org_chart.go` · `bip-erp/services/attendance/main.go`, `business_trip.go`, `manager_departemen.go`, `schedule_list.go`, `jadwal_buatan_hr.go`, `notification.go` · `erp-frontend/src/features/hris/org-chart/lib/bangun-pohon.ts` · `erp-frontend/src/features/hris/master-data/` (divisi, departemen) · skrip migrasi prod `.ps1` (baru)
- **Tanggal**: 2026-10-21

## Context

Manajemen menolak penempatan Direktur dan Manager di departemen Kesekretariatan ([[ADR - 0190 Manager Departemen Menyetujui Pengajuan SPV dan Melihat KPI Departemen yang Dinaunginya]] §5) dan meminta struktur "selayaknya perusahaan". Praktik umum sistem HR: tidak ada karyawan tanpa unit; pimpinan menjadi anggota unit tingkat atas (Direksi), kepala unit adalah relasi terpisah dari keanggotaan, dan laporan bisa dibaca per tingkat.

Keadaan sekarang (`bip-erp` `origin/main` `b7718889`, prod baca-saja 2026-10-21):
- Direktur `BIP-0001-01-20` tercatat di Kesekretariatan sebagai penyetuju departemen itu, bersama staf yang melapor langsung kepadanya (Corporate Secretary, Internal Audit, Legal, Company Branding, Graphic Design, Video Editor, QA RND). HR sudah membuat jabatan "Manager Operational" di departemen yang sama, tanpa jenjang.
- [[HRIS - Organization Structure]] menyatakan organisasi bertingkat "perlu keputusan tersendiri" yang belum pernah diambil, dan Master Divisi ([[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]], 🟡 Diusulkan, master divisi sudah merged) dibatasi untuk pelaporan. `MasterDivisi` tak punya kepala (`shared-library/models/employee/master_data.go:123-132`). 8 dari 12 departemen BIP belum dipetakan ke divisi.
- ADR 0190 (🟢 Diterima, live prod 2026-10-20) menetapkan Manager per departemen lewat `master_department.manager_employee_id`; 0 departemen terisi di prod per 2026-10-20.

Titik yang patah bila unit pimpinan dibuat sebagai departemen biasa, semua diverifikasi di kode:
1. Peran Direktur di 15 modul diturunkan dari pasangan (nama departemen, jabatan): `peranJabatan` (`services/employee/peran_dari_jabatan.go:297-303`, tabel `"kesekretariatan" → "direktur"` `:223-240`), dipanggil dengan `work.Department` (`services/employee/hak_token.go:133`). Pindah departemen = semua peran hilang tanpa galat.
2. Paket izin posisi dicari lewat departemen (`services/employee/permission_resolve.go:127-135`).
3. Cuti/dinas pemohon di unit tanpa penyetuju dibalas 500 "Couldn't find suitable supervisor" (`services/attendance/main.go:2380-2382`, `business_trip.go:153-155`).
4. Key setiap departemen otomatis menjadi kunci modul di daftar peran (`services/employee/master_data.go:596-597`).
5. Unit baru masuk ke ±50 pemakai daftar departemen di web (26 `useDataTypes({endpoint:"department"})` + ±25 `useFetchDepartments`), termasuk MPP, requisition, KPI, jadwal, dan form builder; picker jadwal membalas 400 untuk departemen tak dikenal (`services/attendance/schedule_list.go:107`, jadwal UNSET khusus Kesekretariatan `:91-95`).
6. Slot "Direktur" ditulis berdepartemen Kesekretariatan dan notifikasinya disiarkan ke departemen itu (`services/attendance/manager_departemen.go:70`, `notification.go:339-340`).
7. Bagan organisasi berkerangka departemen saja (`erp-frontend/src/features/hris/org-chart/lib/bangun-pohon.ts:8-11,181-185`).
8. `supervised_by` tak boleh dipakai sebagai induk: ia melebur filter dan cakupan supervisi (`shared-library/models/employee/department_scope.go:70-99`).
9. Override penyetuju Tech Development ditulis di kode (`services/attendance/main.go` `getSupervisorData`), tak terlihat di layar penyetuju.

Pola "pengajuan tanpa atasan langsung ke HR" sudah ada di koreksi presensi (`services/attendance/correction.go:437-450`). Peraturan Perusahaan (`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md`) tidak mengatur penyetuju, jadi tak ada pasal yang terkena.

## Decision

### 1. Tiga tingkat: Direksi → Divisi → Departemen

- **Direksi**: satu unit pimpinan per perusahaan, beranggotakan Direktur dan para Manager (kepala divisi).
- **Divisi**: `master_divisi` yang sudah ada. Departemen menunjuk divisinya lewat `divisi_key` (sudah ada). Divisi tidak beranggota; ia dikepalai.
- **Departemen**: seperti sekarang. Kesekretariatan tetap departemen biasa di bawah Direksi, tanpa ganti nama.

### 2. Unit pimpinan = baris `master_department` berjenis `pimpinan`

`master_department` mendapat field **jenis** (`departemen` bawaan, atau `pimpinan`). Dokumen lama tanpa field dibaca sebagai `departemen`. Setiap karyawan tetap punya `work_data.department`; untuk Direktur dan Manager isinya nama unit Direksi.

Wajib ditangani dengan sengaja untuk jenis `pimpinan` (daftar tertutup, tiap butir dikunci test):
- daftar departemen bawaan (`/data-type/department`, grouped, filter options) **tidak** memuat unit pimpinan, kecuali diminta eksplisit (parameter baru);
- system-list **tidak** menjadikan key unit pimpinan sebagai kunci modul;
- peran turunan dan paket izin posisi tetap berlaku: tabel peran Direktur dikunci unit Direksi (bukan lagi Kesekretariatan), dan `position_items` Direktur beserta paketnya pindah ke baris Direksi lewat migrasi;
- jadwal: unit pimpinan menerima jadwal UNSET seperti Kesekretariatan hari ini, dan picker jadwal tak membalas 400;
- KPI per departemen dan kartu ringkasan tidak memperlakukan unit pimpinan sebagai departemen operasional.

### 3. Divisi berkepala; Manager departemen DITURUNKAN dari divisi

- `master_divisi` mendapat `kepala_employee_id` (satu kepala per divisi, akun aktif, satu perusahaan), ditetapkan lewat endpoint tersendiri ber-jejak audit, gerbang setara penetapan Manager hari ini.
- Manager sebuah departemen = kepala divisi dari departemen itu. Resolver Manager ADR 0190 (`idManagerDepartemen`) membaca divisi, bukan lagi `manager_employee_id`; field itu dimigrasikan lalu tidak dipakai menulis (satu fakta satu tempat). Departemen tanpa divisi, atau divisi tanpa kepala, = tanpa Manager (perilaku ADR 0190 untuk "tanpa Manager" tetap).
- Pengecualian (mis. Finance) dilakukan HR lewat pemetaan divisi, bukan lewat kode.

### 4. Alur pengajuan pimpinan

- **Direktur** (penyetuju unit Direksi): cuti/izin/sakit/dinas miliknya **tanpa tahap atasan, langsung tahap HR**, mengikuti pola koreksi presensi `correction.go:437-450`. Tidak lagi jatuh ke slot "Direktur".
- **Manager** (anggota Direksi): disetujui penyetuju unit Direksi = Direktur **sebagai orang**, lalu HR.
- **Kesekretariatan**: penyetujunya Corporate Secretary (data, ditetapkan HR di layar Penyetuju Pengajuan).
- Slot "Direktur" tanpa orang tetap ada sebagai cadangan untuk SPV yang departemennya tak berkepala divisi; notifikasinya diarahkan ke unit Direksi, bukan Kesekretariatan.
- Override penyetuju yang ditulis di kode (`getSupervisorData`) dihapus; penyetuju IT kembali sepenuhnya dari data.

### 5. Bagan organisasi bertingkat

Endpoint bagan mengirim tingkat (Direksi, divisi beserta kepala, departemen beserta `divisi_key`); web menyusun pohon Direksi → Divisi → Departemen → orang. Atasan langsung lintas unit tetap ditampilkan.

### 6. Migrasi data prod dijalankan manusia

Skrip `.ps1` dua fase (dry-run, lalu apply) dengan cadangan `mongodump` dan rollback: buat unit Direksi, pindahkan Direktur dan Manager, pindahkan `position_items` + paket Direktur, tetapkan penyetuju Direksi = Direktur dan penyetuju Kesekretariatan = Corporate Secretary (bila HR setuju), petakan departemen ke divisi dan isi kepala divisi sesuai keputusan HR. Gerbang verifikasi: hak efektif Direktur sebelum = sesudah (`GET /account/effective-access`).

## Consequences

- ✅ Struktur sesuai praktik umum tanpa mematahkan presensi, hak akses, payroll, dan pengajuan.
- ✅ Satu fakta untuk "siapa Manager departemen ini" (kepala divisi), menggantikan pengisian per departemen.
- ✅ Pengajuan Direktur tidak lagi mati di slot tanpa orang.
- ⚠️ Daftar titik di §2 tertutup tapi panjang; satu yang terlewat = kegagalan senyap. Tiap titik wajib punya test, dan migrasi wajib membandingkan hak efektif Direktur sebelum dan sesudah.
- ⚠️ Mengubah fakta di ADR 0190 (§3 di sana: Manager per departemen; §5: Manager di Kesekretariatan) dan di ADR 0113 (divisi kini punya kepala, tetap bukan rantai persetujuan berjenjang umum).
- ⚠️ Corporate Secretary menjadi penyetuju Kesekretariatan; perlu persetujuan HR/manajemen sebelum migrasi.
- Deploy: BE sebelum FE; `shared-library` berubah sehingga service pembaca model departemen ikut naik; migrasi data sesudah BE live; tanpa env dan kategori inbox baru.

Terkait: [[HRIS - Organization Structure]] · [[ADR - 0194 Peta Penyetuju per Orang Lintas Modul sebagai Tahap Pertama Persetujuan Terpusat]] · [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]] · [[REF - Alur Persetujuan]]

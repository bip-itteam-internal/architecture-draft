**Status**: 🟡 Daftar task dari `/analisa-kebutuhan` 2026-10-21. Keputusannya di [[ADR - 0193 Struktur Organisasi Direksi, Divisi, Departemen dengan Unit Pimpinan Berjenis dan Manager dari Kepala Divisi]] dan [[ADR - 0194 Peta Penyetuju per Orang Lintas Modul sebagai Tahap Pertama Persetujuan Terpusat]]; cara kerjanya di [[HRIS - Organization Structure]]. Dok ini papan kerja, bukan arsitektur.

**Menunggu ADR "Struktur Organisasi Direksi, Divisi, Departemen dengan Unit Pimpinan Berjenis dan Manager dari Kepala Divisi" dan ADR "Peta Penyetuju per Orang Lintas Modul sebagai Tahap Pertama Persetujuan Terpusat" Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

- **Ukuran**: **Besar** (struktur): `bip-erp` butuh lebih dari satu PR (unit pimpinan + titik patah, lalu kepala divisi + bagan, lalu skrip migrasi) dan `erp-frontend` satu PR. **Sedang** (peta penyetuju): satu PR per repo. MyBharata tidak dihitung: departemen hanya ditampilkan sebagai teks, unit baru cuma jatuh ke warna abu-abu (`mybharata-app/lib/src/core/utils/department_color_utils.dart:13-50`, branch `dev`).
- **Pemutus**: irfanarfianto

## Kebutuhan yang dijawab

Manajemen ingin struktur organisasi "selayaknya perusahaan": pimpinan tidak tercatat di departemen operasional, Direksi → Divisi → Departemen, dan penyetuju bisa dikelola dari satu tempat ("orang ini bisa menyetujui apa saja"). Keputusan bentuk dari user 2026-10-21: Direksi > Divisi > Departemen; pengajuan Direktur tanpa atasan langsung HR; Kesekretariatan departemen biasa di bawah Direksi.

## Urutan

1. Induk A `bip-erp`: struktur. Sub: [BE] 1/3 → [BE] 2/3 → [BE] 3/3 (skrip migrasi) ; [FE] deploy sesudah [BE] 1/3 dan 2/3 live.
2. Induk B `bip-erp`: peta penyetuju. Sub: [BE] → [FE]. Boleh paralel dengan A, kecuali butir sumber "Manager/kepala divisi" yang menyesuaikan sesudah A [BE] 2/3.
3. Migrasi data prod (A [BE] 3/3) dijalankan MANUSIA sesudah seluruh BE A live.

---

### Induk A: Struktur organisasi Direksi, Divisi, Departemen

- **Repo**: bip-erp
- **Issue**: _diisi saat dibuat_

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Direktur dan Manager tercatat di departemen Kesekretariatan karena ERP tak mengenal tingkat di atas departemen. Memindahkan mereka sebagai departemen biasa mematahkan peran Direktur di 15 modul, paket izin posisi, cuti (500), daftar peran, jadwal, dan bagan (rincian ADR §Context).

## Keputusan

ADR "Struktur Organisasi Direksi, Divisi, Departemen dengan Unit Pimpinan Berjenis dan Manager dari Kepala Divisi". Layak `Siap Agent` sesudah ADR berstatus Diterima. Induk tanpa PR; ditutup manual saat semua sub-issue merged.

## Yang harus benar

- [ ] Sub-issue [BE] 1/3, 2/3, 3/3 dan [FE] merged; migrasi prod dijalankan manusia dengan gerbang hak efektif Direktur sebelum = sesudah.

## Di luar cakupan

Persetujuan berjenjang umum; mengatur penyetuju dari satu halaman (Induk B, tahap 2 ADR 0137).

## Data / bukti pendukung

Lihat sub-issue.

## Prasyarat

ADR di atas Diterima.

---

### [BE] Struktur organisasi bagian 1/3: unit pimpinan berjenis dan alur pengajuan pimpinan

- **Repo**: bip-erp
- **Issue**: _diisi saat dibuat_

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Titik yang menganggap departemen = unit operasional (diverifikasi `origin/main` `b7718889`): peran turunan dikunci nama departemen (`services/employee/peran_dari_jabatan.go:297-303`, tabel Direktur `:223-240`, pemanggil `hak_token.go:133`); paket posisi lewat departemen (`permission_resolve.go:127-135`); key departemen jadi kunci modul (`services/employee/master_data.go:596-597`); cuti/dinas tanpa penyetuju = 500 (`services/attendance/main.go:2380-2382`, `business_trip.go:153-155`); jadwal UNSET khusus Kesekretariatan dan picker 400 (`services/attendance/schedule_list.go:91-95,107`, `jadwal_buatan_hr.go:88`); slot Direktur & notifikasinya ke Kesekretariatan (`manager_departemen.go:70`, `notification.go:339-340`); override penyetuju IT di kode (`getSupervisorData`).

## Keputusan

ADR "Struktur Organisasi Direksi, Divisi, Departemen dengan Unit Pimpinan Berjenis dan Manager dari Kepala Divisi" §2, §4. Layak `Siap Agent` sesudah ADR berstatus Diterima. Ringkas: `master_department.jenis` (`departemen` bawaan | `pimpinan`); unit pimpinan disaring dari daftar operasional dan system-list; peran & paket Direktur ikut unit Direksi; pengajuan penyetuju unit pimpinan tanpa atasan langsung HR.

## Yang harus benar

- [ ] Field `jenis` di `MasterDepartment`; dokumen tanpa field = `departemen` (test).
- [ ] `GET /data-type/department` (biasa + grouped) dan filter options tidak memuat unit `pimpinan` kecuali parameter eksplisit; system-list tidak memuat key unit `pimpinan` (test).
- [ ] Tabel peran turunan Direktur berlaku untuk jabatan Direktur di unit `pimpinan` (Direksi) dan tetap berlaku di Kesekretariatan selama masa transisi; test: hak efektif Direktur di Direksi = di Kesekretariatan.
- [ ] Paket izin posisi terbaca dari `position_items` unit Direksi (test).
- [ ] Cuti/izin/sakit/dinas pemohon yang adalah penyetuju unit `pimpinan`: `spv_status` kosong, langsung tahap HR, notifikasi ke HR (pola `correction.go:437-450`); tidak pernah 500 (test).
- [ ] Anggota unit `pimpinan` non-penyetuju (Manager): disetujui penyetuju unit itu sebagai orang (test).
- [ ] Slot "Direktur" cadangan: notifikasi ke unit Direksi, bukan Kesekretariatan (test).
- [ ] Unit `pimpinan` menerima jadwal UNSET; picker jadwal tidak 400 (test).
- [ ] Override penyetuju di `getSupervisorData` dihapus; penyetuju IT dari data (test regresi: IT tetap ke penyetuju departemennya).
- [ ] Regresi: staf, SPV dengan Manager, koreksi, tukar shift tidak berubah.
- [ ] `go build` + `go test` employee, attendance, shared-library tanpa kegagalan baru.

## Di luar cakupan

Kepala divisi dan bagan bertingkat (bagian 2/3); migrasi data (3/3); FE.

## Data / bukti pendukung

Prod 2026-10-21: Kesekretariatan berisi Direktur (penyetuju) + 7 staf aktif yang melapor ke Direktur; jabatan "Manager Operational" sudah dibuat HR di Kesekretariatan tanpa jenjang. 8 dari 12 departemen BIP tanpa divisi.

## Prasyarat

ADR Diterima.

---

### [BE] Struktur organisasi bagian 2/3: kepala divisi, Manager dari divisi, bagan bertingkat

- **Repo**: bip-erp
- **Issue**: _diisi saat dibuat_

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

`MasterDivisi` tak punya kepala (`shared-library/models/employee/master_data.go:123-132`); Manager departemen diisi per departemen (`master_department.manager_employee_id`, ADR 0190, resolver `services/employee/department_manager.go:349-356`); bagan organisasi berkerangka departemen saja (`services/employee/org_chart.go`).

## Keputusan

ADR "Struktur Organisasi Direksi, Divisi, Departemen dengan Unit Pimpinan Berjenis dan Manager dari Kepala Divisi" §3, §5. Layak `Siap Agent` sesudah ADR berstatus Diterima. Ringkas: `master_divisi.kepala_employee_id` (satu, aktif, satu perusahaan, endpoint sendiri ber-audit); Manager departemen = kepala divisi dari `divisi_key`-nya; `manager_employee_id` tidak lagi ditulis.

## Yang harus benar

- [ ] `PUT /master/divisi/:key/kepala` (gerbang setara `PUT /master/departments/:key/manager`): validasi aktif/perusahaan, kosong = lepas, jejak audit dalam transaksi (test Fiber).
- [ ] Resolver Manager (`/internal/department-manager`, `/me/managed-departments`, gerbang KPI) membaca kepala divisi; departemen tanpa divisi atau divisi tanpa kepala = tanpa Manager (test, termasuk Finance dipetakan ke divisi tanpa kepala).
- [ ] `PUT /master/departments/:key/manager` dinonaktifkan (410 atau dialihkan) dan `GET .../approvers` menurunkan `manager_*` dari divisi; kontrak bentuk respons tetap.
- [ ] `GET /org-chart` mengirim tingkat: unit Direksi, divisi (key, nama, kepala), departemen dengan `divisi_key`.
- [ ] Regresi ADR 0190: pengajuan SPV ke Manager tetap jalan dengan sumber kepala divisi (test).

## Di luar cakupan

FE; migrasi data.

## Data / bukti pendukung

Prod 2026-10-20: 0 departemen ber-`manager_employee_id` (tak ada data yang hilang saat sumber dipindah).

## Prasyarat

Bagian 1/3 merged.

---

### [BE] Struktur organisasi bagian 3/3: skrip migrasi data prod (dijalankan manusia)

- **Repo**: bip-erp
- **Issue**: _diisi saat dibuat_

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Struktur baru butuh data: unit Direksi, Direktur dan Manager pindah, `position_items` + paket Direktur pindah, penyetuju Kesekretariatan berganti, pemetaan divisi dan kepala divisi.

## Keputusan

ADR "Struktur Organisasi Direksi, Divisi, Departemen dengan Unit Pimpinan Berjenis dan Manager dari Kepala Divisi" §6. Layak `Siap Agent` sesudah ADR Diterima DAN keputusan HR di bawah tertulis. Skrip `.ps1` + `.js` dua fase (dry-run, apply), `mongodump` dulu, rollback, `ssh -n` + `Out-Host` + gerbang `[int]`.

## Yang harus benar

- [ ] Dry-run mencetak rencana perubahan per dokumen tanpa menulis.
- [ ] Apply: unit Direksi berjenis `pimpinan` dengan jabatan Direktur (+paket) dan Manager; Direktur dan Manager pindah; penyetuju Direksi = Direktur; penyetuju Kesekretariatan = orang yang diputuskan HR; `divisi_key` + kepala divisi sesuai keputusan HR.
- [ ] Gerbang: hak efektif Direktur (`GET /account/effective-access`) sebelum = sesudah, per modul; jika beda, berhenti dan rollback.
- [ ] Rollback memulihkan dari cadangan.

## Di luar cakupan

Eksekusi di prod (manusia).

## Data / bukti pendukung

**Perlu keputusan HR (bukan data prod)**: orang penyetuju Kesekretariatan (usulan: Corporate Secretary), pemetaan 12 departemen ke divisi, kepala tiap divisi, Manager mana saja.

## Prasyarat

Bagian 1/3 dan 2/3 live di prod.

---

### [FE] Struktur organisasi: kepala divisi, bagan bertingkat, unit pimpinan di dropdown

- **Repo**: erp-frontend
- **Issue**: _diisi saat dibuat_

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Master Divisi hanya `name/urutan` (`src/features/hris/master-data/components/divisi-form-modal.tsx:105-112`); bagan berkerangka departemen (`src/features/hris/org-chart/lib/bangun-pohon.ts:8-11,181-185`); kolom Manager per departemen di layar penyetuju (ADR 0190); ±50 pemakai daftar departemen.

## Keputusan

ADR "Struktur Organisasi Direksi, Divisi, Departemen dengan Unit Pimpinan Berjenis dan Manager dari Kepala Divisi" §3, §5. Layak `Siap Agent` sesudah ADR Diterima.

## Yang harus benar

- [ ] Master Divisi: pilih/ganti/lepas kepala (karyawan aktif satu perusahaan), dialog konfirmasi, umpan balik.
- [ ] Layar Penyetuju Pengajuan: kolom Manager menjadi baca-saja ("dari kepala divisi X") dengan tautan ke Master Divisi.
- [ ] Master departemen: tampilkan `jenis`; unit pimpinan tidak bisa dipilih sebagai departemen operasional di form yang menulis departemen operasional.
- [ ] Bagan organisasi dan mode kanvas: Direksi → Divisi → Departemen → orang; atasan lintas unit tidak memutus Manager dari bawahannya.
- [ ] i18n dua bahasa, Skeleton, lima keadaan; tsc/lint/build hijau; test tanpa kegagalan baru.
- [ ] Fallback: bila BE belum mengirim tingkat, bagan tampil seperti sekarang.

## Di luar cakupan

MyBharata (kosmetik warna).

## Data / bukti pendukung

Tidak perlu data prod tambahan.

## Prasyarat

[BE] 1/3 dan 2/3 merged. **Deploy sesudah BE live.**

---

### Induk B: Peta penyetuju per orang lintas modul (tahap 1, baca saja)

- **Repo**: bip-erp
- **Issue**: _diisi saat dibuat_

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

18 jenis persetujuan, empat mekanisme penentu, tak ada jawaban "orang ini menyetujui apa".

## Keputusan

ADR "Peta Penyetuju per Orang Lintas Modul sebagai Tahap Pertama Persetujuan Terpusat". Layak `Siap Agent` sesudah ADR Diterima. Induk tanpa PR.

## Yang harus benar

- [ ] Sub-issue [BE] dan [FE] merged.

## Di luar cakupan

Mengatur penyetuju dari halaman ini (tahap 2, ADR 0137).

## Data / bukti pendukung

Lihat sub-issue.

## Prasyarat

ADR Diterima.

---

### [BE] Peta penyetuju per orang: agregator wewenang menyetujui

- **Repo**: bip-erp
- **Issue**: _diisi saat dibuat_

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Tak ada endpoint orang → wewenang (git grep pola peta/wewenang/penyetuju-per-orang hanya mengenai komentar). Sumber yang ada: `GET /account/effective-access` (`services/employee/hak_efektif.go`), `/internal/permission-holders` (`permission_holders.go`), `/master/departments/approvers`, endpoint "punya saya" per modul.

## Keputusan

ADR "Peta Penyetuju per Orang Lintas Modul sebagai Tahap Pertama Persetujuan Terpusat" §1-§2. Layak `Siap Agent` sesudah ADR Diterima. Ringkas: `GET /peta-penyetuju?employee_id=` (HRIS supervisor / IT), baris `{jenis, cakupan, sumber, mekanisme, layar_pengatur}`, satu resolver per sumber, modul gagal = `tidak_terbaca`.

## Yang harus benar

- [ ] Mencakup minimal: penyetuju departemen, Manager/kepala divisi, tahap pengajuan barang/budget, payroll run, rekrutmen, pelatihan, triase tiket/admin space, booking ruang, komite kaizen, penandatangan kontrak, slot jabatan Direktur.
- [ ] Tiap sumber dibaca dari pemiliknya (endpoint baca internal berkunci bila belum ada); tidak ada aturan "siapa boleh" yang disalin ke agregator (test pemindai sumber atau test kontrak per sumber).
- [ ] Modul tak terjangkau → masuk `tidak_terbaca`, respons tetap 200 (test).
- [ ] Gerbang: non-HRIS/IT 403 (test Fiber).
- [ ] Satu verifikasi lewat gateway dev untuk satu orang dengan wewenang dari ≥3 mekanisme.

## Di luar cakupan

Menulis/mengubah penyetuju.

## Data / bukti pendukung

Daftar 18 jenis + titik keputusan: pemetaan 2026-10-21 (diringkas di ADR §Context).

## Prasyarat

ADR Diterima.

---

### [FE] Peta penyetuju per orang: halaman di Pengaturan Organisasi

- **Repo**: erp-frontend
- **Issue**: _diisi saat dibuat_

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Tak ada layar yang menampilkan wewenang menyetujui seseorang; yang ada `hak-efektif.tsx` di `/it/hak-akses` (izin mentah, khusus IT).

## Keputusan

ADR "Peta Penyetuju per Orang Lintas Modul sebagai Tahap Pertama Persetujuan Terpusat" §3. Layak `Siap Agent` sesudah ADR Diterima.

## Yang harus benar

- [ ] Pengaturan → Organisasi → Peta Penyetuju: pilih karyawan, tabel wewenang per modul (jenis, cakupan, sumber, mekanisme), tiap baris bertautan ke layar pengatur.
- [ ] Bagian `tidak_terbaca` tampil sebagai peringatan; lima keadaan; i18n dua bahasa; struktur tabel HRIS (`MainTable`).
- [ ] Menu bertambah dengan panduannya (aturan menu baru wajib panduan).
- [ ] tsc/lint/build hijau; test tanpa kegagalan baru.

## Di luar cakupan

Mengubah penyetuju.

## Data / bukti pendukung

Tidak perlu.

## Prasyarat

[BE] merged. **Deploy sesudah BE live.**

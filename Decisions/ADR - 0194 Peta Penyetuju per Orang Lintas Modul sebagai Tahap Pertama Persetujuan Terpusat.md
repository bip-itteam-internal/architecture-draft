> **Status**: 🟡 **Diusulkan**, 2026-10-21, dari `/analisa-kebutuhan`. Pemutus: irfanarfianto. Kode belum ada. Pecahan kerja: [[ANALISA - Struktur Organisasi Bertingkat dan Peta Penyetuju]].

## Untuk Manajemen

**Yang berubah di layar.** Satu halaman baru di Pengaturan untuk HR dan IT: pilih seorang karyawan, lalu terlihat **semua yang bisa ia setujui** di seluruh ERP (cuti staf departemen X, pengajuan SPV sebagai Manager, tahap pembelian, payroll, rekrutmen, booking ruang, komite kaizen, tanda tangan kontrak, dan lainnya), beserta **dari mana wewenang itu berasal** dan tautan ke layar tempat mengubahnya.

**Siapa yang terdampak.** HR dan IT yang mengelola penyetuju; tidak ada perubahan bagi pemohon maupun penyetuju.

**Yang TIDAK dijanjikan.**
- Halaman ini **hanya menampilkan**. Mengubah penyetuju tetap di layar masing-masing modul sampai tahap 2 diputuskan.
- Delegasi saat penyetuju cuti, rangkap jabatan, dan status Corporate Secretary belum diputuskan (pertanyaan terbuka [[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]]).
- Wewenang yang hari ini ditentukan "peran lama" (sebagian insentif, CAPA, WMS) ditampilkan sebagai kategori, tanpa daftar dokumen spesifik.

**Besaran kerja.** Sedang: satu backend, satu halaman web.

## Deskripsi

*Tahap pertama persetujuan terpusat adalah peta BACA-SAJA per orang: satu endpoint di employee-service menghimpun seluruh wewenang menyetujui seorang karyawan dari semua sumber yang hari ini tersebar, menandai sumber dan layar pengaturnya, dan satu halaman web menampilkannya. Tahap kedua (mengatur dari satu tempat) menunggu keputusan ADR 0137.*

- **Status**: 🟡 Diusulkan, 2026-10-21. Kode belum ada.
- **Path di repo**: `bip-erp/services/employee/peta_penyetuju.go` (baru) · `bip-erp/services/employee/hak_efektif.go` · `bip-erp/services/employee/permission_holders.go` · endpoint baca per modul yang sudah ada (procurement, inventory, form-builder, payroll, recruitment, learning, task-management) · `erp-frontend/src/app/(main)/pengaturan/organisasi/` (halaman baru) · `erp-frontend/src/features/hris/master-data/` atau fitur baru `peta-penyetuju` (baru)
- **Tanggal**: 2026-10-21

## Context

Pertanyaan "orang ini bisa menyetujui apa saja" tidak bisa dijawab dari satu tempat. Pemetaan 2026-10-21 (`bip-erp` `b7718889`, `erp-frontend` `53eb68200`) menemukan 18 jenis persetujuan dengan empat mekanisme penentu yang berbeda bentuk:
- **penetapan orang tersimpan**: penyetuju departemen, Manager (ADR 0190), daftar penyetuju booking ruang, komite kaizen, penandatangan kontrak, admin space task-management, pemegang CV;
- **izin per tahap** (paket per posisi/akun): pengajuan barang/budget, payroll run, rekrutmen, pelatihan, triase tiket, WMS;
- **peran lama** (`system_roles` tier): sebagian insentif, CAPA;
- **nama jabatan**: `common.SetaraDirektur` (slot "Direktur").

Yang sudah ada dan dipakai ulang: `GET /account/effective-access` (izin dan peran efektif satu orang beserta asalnya, khusus IT; `services/employee/hak_efektif.go`), `GET /internal/permission-holders` (izin → orang; `permission_holders.go`), `GET /master/departments/approvers` (penyetuju + Manager per departemen), dan endpoint "punya saya" per modul (`/me/managed-departments`, `/peminjaman/penyetuju/saya`, `/me/kaizen/committee`, `/contract-ttd/direktur/antrean`). Agregator antrean `GET /pengajuan/antrean` menjawab "apa yang menunggu saya sekarang", bukan wewenang.

Bukti tidak ada pembalik orang → wewenang: `git grep` pola peta/wewenang/penyetuju-per-orang di kedua repo hanya mengenai komentar. Selama itu tidak ada, penyimpangan senyap tak terlihat, contohnya override penyetuju Tech Development yang ditulis di kode attendance tidak tampak di layar penyetuju (dihapus oleh [[ADR - 0193 Struktur Organisasi Direksi, Manager, Departemen dengan Unit Pimpinan Berjenis dan Penyetuju Lintas Departemen]] §4).

[[ADR - 0137 Model Persetujuan Tunggal dan Pemisahan Tugas Lintas Modul]] (🟡 Diusulkan, Decision TBD) memetakan masalah yang sama dan mengusulkan penyetuju = pemegang izin tahap ∩ penunjukan berjejak. Keputusan ini tidak mendahuluinya: ia hanya membaca sumber yang ada.

## Decision

### 1. Peta per orang, baca saja

`GET /peta-penyetuju?employee_id=` di employee-service (gerbang: HRIS supervisor atau IT, sama dengan layar penyetuju) mengembalikan daftar wewenang:

```
{ jenis, cakupan, sumber, mekanisme, layar_pengatur }
```
- `jenis`: kode persetujuan (mis. `cuti_staf`, `pengajuan_spv`, `budget.approve.finance`, `payroll.approve.hrd`, `booking_ruang`, `kaizen_komite`, `kontrak_ttd`).
- `cakupan`: departemen/divisi/perusahaan/space yang dicakup.
- `mekanisme`: `penetapan` | `izin` | `peran_lama` | `jabatan`.
- `sumber`: dari mana (mis. "penyetuju departemen Finance", "paket posisi Finance Supervisor", "penunjukan booking ruang").
- `layar_pengatur`: rute web tempat mengubahnya.

### 2. Satu resolver per sumber, tidak menyalin aturan

Tiap mekanisme dibaca dari pemiliknya: penetapan dari koleksinya lewat endpoint modul (baru bila belum ada, bentuk "punya orang X" untuk pemanggil internal berkunci), izin dari resolver izin efektif yang sama dengan `effective-access`, jabatan dari `common.SetaraDirektur`. Aturan "siapa boleh" tidak ditulis ulang di agregator. Modul yang gagal dibalas sebagai bagian `tidak_terbaca` di respons, bukan disembunyikan.

### 3. Halaman web

Pengaturan → Organisasi → Peta Penyetuju: pilih karyawan, tabel wewenang dikelompokkan per modul, tiap baris bertautan ke layar pengatur. Lima keadaan layar; modul tak terbaca ditampilkan sebagai peringatan.

### 4. Tahap 2 menunggu ADR 0137

Mengatur penyetuju dari halaman ini (menulis) baru dibangun setelah ADR 0137 diputuskan (delegasi, rangkap jabatan, Corporate Secretary, model izin ∩ penunjukan).

## Consequences

- ✅ "Siapa menyetujui apa" terjawab dari satu tempat untuk pertama kalinya; penyimpangan antar sumber menjadi terlihat.
- ✅ Tanpa mengubah wewenang siapa pun.
- ⚠️ Beberapa modul butuh endpoint baca "punya orang X" baru; tiap endpoint itu bergerbang kunci internal.
- ⚠️ Peran lama hanya bisa ditampilkan sebagai kategori sampai modulnya berkatalog izin.
- Deploy: BE (employee-service + modul yang mendapat endpoint baca) sebelum FE.

Terkait: [[ADR - 0193 Struktur Organisasi Direksi, Manager, Departemen dengan Unit Pimpinan Berjenis dan Penyetuju Lintas Departemen]] · [[REF - Alur Persetujuan]] · [[CORE - RBAC dan Permission Set]]

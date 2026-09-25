## Deskripsi

*Administrasi kepegawaian (personalia) — mengelola data administratif karyawan sepanjang masa kerja: data personal, kontrak (PKWT), BPJS, dokumen, riwayat masa kerja, hingga off-boarding/exit clearance. Beririsan dengan subsistem off-boarding di [[HRIS - Analysis]].*

- **Status**: ⚠️ Sebagian diimplementasikan — **pencatatan resign & penonaktifan akun ✅ live di produksi 2026-08-05**; **riwayat kontrak ✅** (koleksi `employee_contract`, halaman `/hris/contract`); **pengingat kontrak habis ✅ live DEV 2026-09-11 dan PROD 2026-09-12**; sisa off-boarding (exit clearance) masih 🟡 konsep; **ID karyawan otomatis dan pengangkatan magang 🟡 diusulkan** ([[ADR - 0126 employee_id Diterbitkan Sistem, Magang yang Diangkat Mendapat ID Reguler dengan Migrasi Riwayat]], kode belum ada)

## Ruang Lingkup & Data

Dokumen/data yang dikelola (sebagian sudah ada di [[Microservices - Employee Service]]):
- **Data personal pegawai** (`personal_data`, `personal_document`)
- **Kontrak / PKWT** (mis. BIP-203-0525): riwayat kontrak per karyawan, perpanjangan, dan lampiran PDF bertanda tangan sudah ada (rute di [[API - Employee Service]] §Kontrak Kerja). Kebutuhan: **notifikasi 1 bulan sebelum masa kontrak habis** → follow up ke SPV. Dijawab pengingat kontrak habis: ringkasan harian ke supervisor HR (saat kontrak masuk "segera berakhir", H-30, H-7, dan kontrak kedaluwarsa pada karyawan aktif sekali per minggu) dan pesan H-14 ke atasan langsung untuk penilaian kinerja. ✅ Merged 2026-09-11 (bip-erp PR #1851), naik di DEV 2026-09-11 dan PROD 2026-09-12; jalan PROD pertama 2026-09-13 07:00 WIB belum dibaca. Rinciannya di [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] §Pengingat Kontrak Habis. Digitalisasi tanda tangan & e-Meterai kontrak di dok yang sama (🟡 direncanakan)
- **BPJS**
- **Riwayat masa kerja** (history)

## ID Karyawan & Pengangkatan Magang (🟡 diusulkan)

Keputusan dan alasannya di [[ADR - 0126 employee_id Diterbitkan Sistem, Magang yang Diangkat Mendapat ID Reguler dengan Migrasi Riwayat]]; papan kerjanya [[ANALISA - ID Karyawan Otomatis dan Pengangkatan Magang]]. Bagian ini menjelaskan cara kerjanya.

**Hari ini (diukur prod 2026-09-25):** ID diketik HR di form Tambah Karyawan, dan hanya diperiksa keunikannya. Akibatnya 6 pasang nomor urut dipakai dua orang, dan 5 magang September ber-ID tanpa `MG` karena input 3-4-2-2 tak bisa menampungnya. Nomor tertinggi reguler 0264, magang 1012.

**Sesudah ADR 0126:**

| | Reguler | Magang |
|---|---|---|
| Bentuk | `<KODE>-<NNNN>-<MM>-<YY>` | `<KODE>-MG-<NNNN>-<MM>-<YY>` |
| Deret ditentukan oleh | `employment_type` kontrak pertama bukan `Magang` | `employment_type` kontrak pertama = `Magang` |
| `MM-YY` | bulan-tahun `join_date` (WIB) | sama |
| Nomor | penghitung reguler per awalan | penghitung magang per awalan, blok 1000-an |

- Nomor dialokasikan employee-service secara atomik saat simpan. HR tidak mengetik dan tidak bisa mengubahnya; ID tampil di ringkasan sesudah tersimpan.
- ⚠️ **Jangan menyimpulkan magang dari awalan ID** di kode baru. Yang menentukan tetap `employment_type` (payroll sudah begitu, [[Microservices - Payroll Service]]). Awalan `MG` untuk manusia yang membaca ID, bukan untuk mesin.

**Pengangkatan magang ke PKWT/PKWTT:**

1. HR meminta pengangkatan ke tim IT untuk satu angkatan.
2. Tim IT menjalankan alat migrasi (runbook menyusul, task T4 papan kerja): ID reguler baru dialokasikan dari penghitung reguler, lalu seluruh rujukan ID magang di semua database diganti. Dry-run, `mongodump`, dan gerbang sisa nol wajib.
3. HR menutup kontrak Magang dan membuat kontrak PKWT di `/hris/contract`. Karena ID sudah satu, riwayat Magang lalu PKWT tampil berurutan di panel riwayat yang sama.
4. Karyawan login ulang di MyBharata dengan ID baru dan mengaktifkan ulang biometrik. Finance mengganti proyek Accurate yang bernomor ID lama, bila ada.

**Yang tidak berubah:** promosi, mutasi, dan mutasi antar-perusahaan tetap mempertahankan ID ([[ADR - 0044 Mutasi Antar-Tenant Mempertahankan employee_id]]). Berkas foto dan dokumen lama tetap di folder MinIO ber-ID lama dan tetap terbuka.

## Off-boarding / Exit Clearance

Saat karyawan keluar, urutan clearance:
1. **Feedback** ke perusahaan (Employee)
2. **Inventaris** yang dipegang dikembalikan (GA) — cek aset di [[GA - Inventory Management]]
3. **NDA** (Employee & HR)
4. Penerbitan **paklaring** (HR)

Hasil off-boarding (terminasi) menjadi sumber data [[HRIS - Attrition]].

### Catatan Resign / Non-Aktif — ✅ live di produksi 2026-08-05

Langkah **pencatatan berhentinya karyawan sekaligus penonaktifan akunnya** sudah dibangun; empat langkah clearance di atas belum. Keputusan lengkap beserta konsekuensinya: [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]].

- **HR yang mencatat, dan akunnya mati sebagai akibat** — bukan sebagai permintaan yang dikirim ke IT. Sebelumnya penonaktifan akun hanya bisa lewat menu IT ([[IT - Employee System]]), sehingga akses tetap hidup sepanjang jeda antara HR tahu dan IT mengeksekusi.
- Satu catatan memuat **kategori** (Mengundurkan Diri · PHK · Pensiun · Kontrak Berakhir · Meninggal Dunia), **tanggal efektif**, **alasan**, dan **dokumen pendukung** opsional (PDF/gambar/Word, maks 4 MB).
- **Tanggal efektif = hari pertama karyawan non-aktif.** Tanggal yang sudah lewat atau hari ini berlaku seketika (HR sering baru mencatat setelah orangnya keluar); tanggal di depan dijadwalkan dan diterapkan cron 00:10 WIB.
- Catatan bisa **diperbaiki** selama belum berlaku, dan **dibatalkan** kapan saja. Pembatalan yang mengaktifkan kembali akun menuntut alasan tertulis, dan hanya menghidupkan akun yang dimatikan catatan itu sendiri.
- Alasan yang dicatat di sini adalah **prasyarat demografi** yang selama ini menghalangi [[HRIS - Attrition]].
- ⚠️ **Belum ditangani**: karyawan non-aktif ikut lenyap dari laporan absensi dan basis payroll bulan berjalan, karena beberapa kueri menyaring `is_active` diam-diam. Lihat [[Microservices - Employee Service]].

**Akun nonaktif tanpa catatan keluar — 🔜 belum merge & belum deploy** (branch bip-erp `feat/employee-status-akun-bertanggal` + erp-frontend `feat/hris-backlog-catatan-keluar`)

Mencatat resign bukan satu-satunya cara akun mati: jalur IT tetap ada dan sah (akun ganda, akun titipan, insiden keamanan). Yang tak sah adalah kepergian karyawan yang tak pernah tercatat, sebab kepergian tanpa tanggal membuat headcount bulan lampau tak bisa dipercaya — dan angka itu dipakai menilai tim rekrutmen ([[ADR - 0113 Actual vs Planning MPP Dihitung Sistem per Bulan, Berpijak pada Jejak Keluar Bertanggal]]).

- Diukur PROD 2026-09-21: **35 akun non-aktif, hanya 11 punya catatan keluar**, jadi **24 kepergian tak punya tanggal sama sekali**.
- Halaman Resign mendapat panel **"Akun nonaktif tanpa catatan keluar"**. Memilih satu nama membuka formulir resign yang orangnya sudah terisi — perlu, karena pemilih karyawan biasa hanya memuat yang **aktif** sehingga orang-orang ini tak akan pernah muncul di sana. Barisnya hilang sendiri begitu catatannya tersimpan.
- ⚠️ Mencatat backlog **tidak** mengubah akses siapa pun (akunnya sudah mati), dan membatalkan catatan itu nanti **tidak** menghidupkan akunnya — sebab bukan catatan itu yang mematikannya (aturan `account_deactivated`, keputusan 5 [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]]). Layarnya menyebutkan ini saat mencatat.
- Tanggal usulan untuk 24 orang itu diturunkan dari **absensi terakhir + 1 hari**; HRD yang memutuskan, karena orang bisa cuti panjang sebelum berhenti. Kategori diisi HRD, tidak disimpulkan dari jenis kontrak.
- Menambalnya **mengubah angka turnover bulan lampau** dari 11 menjadi 35 orang keluar. Skor KPI yang sudah final tidak ikut berubah.
- Sejak ini hidup, tiap penonaktifan meninggalkan jejak bertanggal beserta pintu dan pelakunya, dan layar IT mewajibkan alasan — jadi backlog baru tak bisa lahir tanpa tanggal.

Implementasi: [[Microservices - Employee Service]] · endpoint: [[API - Employee Service]] · halaman: [[APP - Web ERP]] (HRIS → Personalia → Resign).

## Integrasi

- [[Microservices - Employee Service]] — endpoint contract, BPJS, personal data (RequireHRISStaff)
- [[Microservices - Notification Service]]: notifikasi PKWT mendekati habis, inbox kategori `reminder` dari cron employee-service (✅ DEV dan PROD sejak 2026-09-12; lihat [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] §Pengingat Kontrak Habis)
- [[GA - Inventory Management]] — pengembalian aset saat exit clearance
- [[HRIS - Analysis]] — subsistem off-boarding

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]]
- [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]] · [[ADR - 0126 employee_id Diterbitkan Sistem, Magang yang Diangkat Mendapat ID Reguler dengan Migrasi Riwayat]] · [[API - Employee Service]] · [[APP - Web ERP]] · [[IT - Employee System]]
- [[HRIS - Analysis]] · [[HRIS - Attrition]]
- [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] — digitalisasi TTE + e-Meterai kontrak (🟡 direncanakan) dan pengingat kontrak habis (✅ DEV dan PROD sejak 2026-09-12)
- [[Microservices - Employee Service]] · [[GA - Inventory Management]]

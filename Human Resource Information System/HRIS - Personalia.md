## Deskripsi

*Administrasi kepegawaian (personalia) — mengelola data administratif karyawan sepanjang masa kerja: data personal, kontrak (PKWT), BPJS, dokumen, riwayat masa kerja, hingga off-boarding/exit clearance. Beririsan dengan subsistem off-boarding di [[HRIS - Analysis]].*

- **Status**: ⚠️ Sebagian diimplementasikan — **pencatatan resign & penonaktifan akun** sudah ada di kode (⚠️ branch `feat/employee`/`feat/hris-resign`, belum merge & belum deploy); sisa off-boarding (exit clearance) masih 🟡 konsep

## Ruang Lingkup & Data

Dokumen/data yang dikelola (sebagian sudah ada di [[Microservices - Employee Service]]):
- **Data personal pegawai** (`personal_data`, `personal_document`)
- **Kontrak / PKWT** (mis. BIP-203-0525) — **notifikasi 1 bulan sebelum masa kontrak habis** → follow up ke SPV. Digitalisasi tanda tangan & e-Meterai kontrak: [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] (🟡 direncanakan)
- **BPJS**
- **Riwayat masa kerja** (history)

## Off-boarding / Exit Clearance

Saat karyawan keluar, urutan clearance:
1. **Feedback** ke perusahaan (Employee)
2. **Inventaris** yang dipegang dikembalikan (GA) — cek aset di [[GA - Inventory Management]]
3. **NDA** (Employee & HR)
4. Penerbitan **paklaring** (HR)

Hasil off-boarding (terminasi) menjadi sumber data [[HRIS - Attrition]].

### Catatan Resign / Non-Aktif — ⚠️ ada di kode, belum merge & belum deploy

Langkah **pencatatan berhentinya karyawan sekaligus penonaktifan akunnya** sudah dibangun; empat langkah clearance di atas belum. Keputusan lengkap beserta konsekuensinya: [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]].

- **HR yang mencatat, dan akunnya mati sebagai akibat** — bukan sebagai permintaan yang dikirim ke IT. Sebelumnya penonaktifan akun hanya bisa lewat menu IT ([[IT - Employee System]]), sehingga akses tetap hidup sepanjang jeda antara HR tahu dan IT mengeksekusi.
- Satu catatan memuat **kategori** (Mengundurkan Diri · PHK · Pensiun · Kontrak Berakhir · Meninggal Dunia), **tanggal efektif**, **alasan**, dan **dokumen pendukung** opsional (PDF/gambar/Word, maks 4 MB).
- **Tanggal efektif = hari pertama karyawan non-aktif.** Tanggal yang sudah lewat atau hari ini berlaku seketika (HR sering baru mencatat setelah orangnya keluar); tanggal di depan dijadwalkan dan diterapkan cron 00:10 WIB.
- Catatan bisa **diperbaiki** selama belum berlaku, dan **dibatalkan** kapan saja. Pembatalan yang mengaktifkan kembali akun menuntut alasan tertulis, dan hanya menghidupkan akun yang dimatikan catatan itu sendiri.
- Alasan yang dicatat di sini adalah **prasyarat demografi** yang selama ini menghalangi [[HRIS - Attrition]].
- ⚠️ **Belum ditangani**: karyawan non-aktif ikut lenyap dari laporan absensi dan basis payroll bulan berjalan, karena beberapa kueri menyaring `is_active` diam-diam. Lihat [[Microservices - Employee Service]].

Implementasi: [[Microservices - Employee Service]] · endpoint: [[API - Employee Service]] · halaman: [[APP - Web ERP]] (HRIS → Personalia → Resign).

## Integrasi

- [[Microservices - Employee Service]] — endpoint contract, BPJS, personal data (RequireHRISStaff)
- [[Microservices - Notification Service]] — notifikasi PKWT mendekati habis
- [[GA - Inventory Management]] — pengembalian aset saat exit clearance
- [[HRIS - Analysis]] — subsistem off-boarding

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]]
- [[ADR - 0035 HR Menonaktifkan Akun lewat Catatan Resign]] · [[API - Employee Service]] · [[APP - Web ERP]] · [[IT - Employee System]]
- [[HRIS - Analysis]] · [[HRIS - Attrition]]
- [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] — digitalisasi TTE + e-Meterai kontrak (🟡 direncanakan)
- [[Microservices - Employee Service]] · [[GA - Inventory Management]]

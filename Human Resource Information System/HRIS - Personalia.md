## Deskripsi

*Administrasi kepegawaian (personalia) — mengelola data administratif karyawan sepanjang masa kerja: data personal, kontrak (PKWT), BPJS, dokumen, riwayat masa kerja, hingga off-boarding/exit clearance. Beririsan dengan subsistem off-boarding di [[HRIS - Analysis]].*

- **Status**: 🟡 Draft / Direncanakan

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

## Integrasi

- [[Microservices - Employee Service]] — endpoint contract, BPJS, personal data (RequireHRISStaff)
- [[Microservices - Notification Service]] — notifikasi PKWT mendekati habis
- [[GA - Inventory Management]] — pengembalian aset saat exit clearance
- [[HRIS - Analysis]] — subsistem off-boarding

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]]
- [[HRIS - Analysis]] · [[HRIS - Attrition]]
- [[HRIS - Kontrak Kerja Elektronik (e-Signing & e-Meterai)]] — digitalisasi TTE + e-Meterai kontrak (🟡 direncanakan)
- [[Microservices - Employee Service]] · [[GA - Inventory Management]]

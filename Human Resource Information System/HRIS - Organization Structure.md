## Deskripsi

*Struktur organisasi perusahaan — departemen, posisi/jabatan, dan hierarki (atasan/SPV). Sebagian data sudah ada di [[Microservices - Employee Service]] (`work_data`); visualisasi org chart formal belum.*

- **Status**: 🟡 Konsep / Draft (data dasar ada; org chart belum)

## Ruang Lingkup

- **Departemen** (mis. HR, GA, Finance, QC, Manufacture, Secretary, Marketing, IT, dll)
- **Posisi/jabatan** per departemen (`PositionTitle*` di shared-library employee)
- **Hierarki/atasan** — relasi supervisor per divisi (dipakai di banyak approval, mis. `getSupervisorData`)
- **Org chart** — visualisasi struktur

## Keterkaitan

- Sumber data: `work_data` (departemen/posisi/supervisor) & `system_authentication` (role/supervisor) di [[Microservices - Employee Service]]
- Dipakai oleh hampir semua subsistem HRIS untuk routing approval & RBAC (lihat [[HRIS - Interrelationship Matrices]])
- Perubahan struktur ditangani via [[HRIS - Career & Promotion]] (mutasi/promosi)

## Belum Diputuskan (TBD)

- Sumber kebenaran struktur (master org) & cara update
- Format org chart (visual) + jenjang/golongan
- Penanganan posisi rangkap / matriks

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]]
- [[Microservices - Employee Service]] · [[HRIS - Personalia]] · [[HRIS - Career & Promotion]] · [[HRIS - Interrelationship Matrices]]

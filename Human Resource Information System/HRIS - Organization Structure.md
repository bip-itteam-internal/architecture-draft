## Deskripsi

*Struktur organisasi perusahaan — departemen, posisi/jabatan, dan hierarki (atasan/SPV). **Departemen dan posisi** kini dikelola sebagai master data di MongoDB (`master_department`) dengan CRUD endpoint dan halaman admin di frontend. Data karyawan tetap di `work_data`. Visualisasi org chart formal belum ada.*

- **Status**: ⚠️ Implemented (ada catatan) — master departemen/posisi sudah di-DB; org chart belum

## Ruang Lingkup

- **Departemen** — dikelola di collection `master_department` (key, name, positions[], roles[]); CRUD via `GET/POST/PUT/DELETE /master/departments` di [[Microservices - Employee Service]]
- **Posisi/jabatan** per departemen — tersimpan sebagai array `positions` di setiap dokumen `master_department`; sebelumnya hardcoded (`PositionTitle*` di shared-library), sekarang dapat ditambah/ubah via API atau frontend `/hris/master-data`
- **System roles** — role per department (staff, supervisor, admin, security) dan feature-based roles (insentive, integration) dikelola di `master_department.roles` dan `master_system_role`
- **Hierarki/atasan** — relasi supervisor per divisi (dipakai di banyak approval, mis. `getSupervisorData`)
- **Org chart** — visualisasi struktur (belum ada)

## Keterkaitan

- Sumber data master: `master_department` dan `master_system_role` di [[Microservices - Employee Service]] (seed otomatis saat kosong)
- Sumber data karyawan: `work_data` (departemen/posisi/supervisor) & `system_authentication` (role/supervisor) di [[Microservices - Employee Service]]
- Dipakai oleh hampir semua subsistem HRIS untuk routing approval & RBAC (lihat [[HRIS - Interrelationship Matrices]])
- Perubahan struktur ditangani via [[HRIS - Career & Promotion]] (mutasi/promosi)
- Frontend admin: `/hris/master-data` — tabs Departments + System Roles dengan full CRUD

## Belum Diputuskan (TBD)

- Format org chart (visual) + jenjang/golongan
- Penanganan posisi rangkap / matriks

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]]
- [[Microservices - Employee Service]] · [[HRIS - Personalia]] · [[HRIS - Career & Promotion]] · [[HRIS - Interrelationship Matrices]]

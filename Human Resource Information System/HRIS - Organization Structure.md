## Deskripsi

*Struktur organisasi perusahaan — departemen, posisi/jabatan, dan hierarki (atasan/SPV). **Departemen dan posisi** kini dikelola sebagai master data di MongoDB (`master_department`) dengan CRUD endpoint dan halaman admin di frontend. Data karyawan tetap di `work_data`. Visualisasi org chart formal belum ada.*

- **Status**: ⚠️ Implemented (ada catatan) — master departemen/posisi sudah di-DB; org chart belum

## Ruang Lingkup

- **Departemen** — dikelola di collection `master_department` (key, name, positions[], roles[]); CRUD via `GET/POST/PUT/DELETE /master/departments` di [[Microservices - Employee Service]]
- **Posisi/jabatan** per departemen — tersimpan sebagai array `positions` di setiap dokumen `master_department`; sebelumnya hardcoded (`PositionTitle*` di shared-library), sekarang dapat ditambah/ubah via API atau frontend `/hris/master-data`
- **System roles** — role per department (staff, supervisor, admin, security) dan feature-based roles (insentive, integration) dikelola di `master_department.roles` dan `master_system_role`
- **Hierarki/atasan** — relasi supervisor per divisi (dipakai di banyak approval, mis. `getSupervisorData`)
- **Org chart** — visualisasi struktur (belum ada)

## Satu supervisor untuk dua departemen — General Affair → Human Resource

⚠️ **Aturan operasional yang tidak terlihat dari kode maupun UI. Baca sebelum mengubah data supervisor.**

**General Affair sengaja tidak punya supervisor sendiri** (`work_data.is_supervisor` = `true` nol orang); yang membawahinya adalah **supervisor Human Resource**. Kedua departemen **tetap terpisah** sebagai data — 15 orang GA (mayoritas Security & Office Boy) tetap ber-`work_data.department` = `General Affair`.

Yang membuatnya berjalan: `services/employee/main.go` pada `/list?type=supervisor` **menulis ulang** query `department=General Affair` menjadi `Human Resource` (ada di jalur utama **dan** jalur fallback by-position). Karena `getSupervisorData` di [[Microservices - Attendance Service]] memakai endpoint itu, seluruh pengajuan GA (cuti, izin, koreksi absensi, perjalanan dinas) otomatis mengarah ke SPV HR.

Konsekuensi yang perlu dijaga:

- **Jangan hapus remap tersebut.** Tanpa itu jalur cadangan pun gagal, karena tak satu pun posisi di GA (`Security`, `Office Boy`, `GA Staff`, `Legal Staff`, `Admin`) cocok dengan pola judul `Supervisor|^Leader$`. Hasilnya **nol approver** untuk 15 orang.
- **Remap bersifat satu arah (GA→HR).** Supervisor wajib terdaftar di `Human Resource`. Bila di-set ke `General Affair`, staf HR maupun GA sama-sama tak menemukannya, dan panel admin HR menolak 403.
- **Menambah `is_supervisor` di GA tidak berefek** selama remap masih ada, karena query sudah ditulis ulang sebelum menyentuh database.
- **Memisahkan kembali** butuh ubah kode (menghapus remap), bukan sekadar ubah data. Memindahkannya jadi relasi di `master_department` = **TBD**, lihat bagian TBD di bawah.
- **Tahap review HR bersifat dept-level**: slot `hr_status` diisi pseudo-user tanpa `employee_id`, sehingga **semua** orang berdepartemen `Human Resource` dapat melihat & menindak antrian tahap HR, termasuk pengajuan milik orang GA. Tahap SPV tidak begitu (diisi `employee_id` spesifik). Ini alasan kuat untuk **tidak** menggabungkan kedua departemen di level data: bila GA dipindah ke HR, Security & Office Boy ikut bisa melihat antrian pengajuan seluruh perusahaan.

Tampilan KPI menyatukan keduanya sebagai satu entri filter tanpa menyentuh data — lihat [[HRIS - Key Performance Index]].

## Keterkaitan

- Sumber data master: `master_department` dan `master_system_role` di [[Microservices - Employee Service]] (seed otomatis saat kosong)
- Sumber data karyawan: `work_data` (departemen/posisi/supervisor) & `system_authentication` (role/supervisor) di [[Microservices - Employee Service]]
- Dipakai oleh hampir semua subsistem HRIS untuk routing approval & RBAC (lihat [[HRIS - Interrelationship Matrices]])
- Perubahan struktur ditangani via [[HRIS - Career & Promotion]] (mutasi/promosi)
- Frontend admin: `/hris/master-data` — tabs Departments + System Roles dengan full CRUD

## Belum Diputuskan (TBD)

- Format org chart (visual) + jenjang/golongan
- Penanganan posisi rangkap / matriks
- **Relasi supervisi antar-departemen sebagai master data** — saat ini "GA dibawahi SPV HR" tersebar di tiga tempat berbeda: remap hardcode di employee service, union HR+GA hardcode di attendance (`/today?view=team`), dan konstanta di FE KPI. Field relasi di `master_department` (mis. `supervised_by`) akan menyatukan ketiganya sehingga penataan ulang cukup ubah data. Pola serupa sudah ada implisit di `deptKeyToNames` yang memetakan role `finance` ke `Finance` **dan** `Procurement`.

## Dependensi / Dokumen Terkait

- [[HRIS - Big Pictures]]
- [[Microservices - Employee Service]] · [[HRIS - Personalia]] · [[HRIS - Career & Promotion]] · [[HRIS - Interrelationship Matrices]]

## Deskripsi

*Desain fitur **Candidate Assessment** — tes teknis/keahlian (mis. Technical Coding Test, Frontend Development Test) yang direkam HR di tahap **Screening**, dinilai **skor + hasil Pass/Fail/Pending**. Melengkapi pipeline recruitment 6-status ([[HRIS - Recruitment Pipeline Redesign]]). Hasil bersifat catatan; perubahan status kandidat tetap manual oleh HR.*

- **Status**: 🟡 Direncanakan (Design) — belum ada kode. Hasil brainstorming 2026-07-19.
- **Sisi implementasi**: [[Microservices - Recruitment Service]] (BE) + [[APP - Web ERP]] (FE). Endpoint → [[API - Recruitment Service]].
- **Catatan**: menghidupkan kembali konsep "tes teknis" (yang dihapus saat redesign) sebagai entity BARU `candidate_assessment` dengan semantik Pass/Fail/Pending + menu sendiri — bukan resurrect `technical_test_result` lama.

## Latar Belakang

Di tahap **Screening** (status kandidat `Screening`), HR bisa meminta pelamar mengerjakan tes teknis/keahlian. Hasilnya (skor + Pass/Fail/Pending) direkam untuk jadi bahan keputusan. Pelamar yang Fail biasanya di-Reject — tetapi **perubahan status dilakukan HR manual** (selaras model transisi bebas hasil redesign), bukan otomatis dari hasil assessment.

## Keputusan Desain (terkunci)

1. **Tipe assessment = master katalog** (mis. "Technical Coding Test", "Frontend Development Test") — dikelola HR di **System Setup**, dipilih via dropdown saat merekam. Konsisten pola Lookup (job-type/interview-type).
2. **Hasil → status = MANUAL**. `candidate_assessment` hanya menyimpan skor + `result` (Pass/Fail/Pending). HR mengubah status kandidat sendiri (Fail→Rejected, Pass→Interview) lewat dropdown status. Tanpa auto/prompt.
3. **Menu tersendiri** "Candidate Assessment" di grup Recruitment (sidebar), pola menu **Interviews**: tabel semua assessment + tombol "Rekam Assessment".
4. **Picker kandidat = hanya status `Screening`** saat merekam (selaras cara picker Jadwalkan Interview dibatasi ke status Interview).

## Model & Perubahan

### BE ([[Microservices - Recruitment Service]])
- **Master `assessment_type`** (Lookup: name/description/is_active) — reuse mekanisme master generik yang ada; endpoint `/masters/assessment-types`.
- **Entity `candidate_assessment`** (koleksi baru): `id`, `candidate_id`, `assessment_type_id` (ref master), `score` (number, opsional), `result` (enum **Pass/Fail/Pending**, wajib), `notes` (opsional), `assessed_by` (employee_id, dari header), `created_at`. Validasi murni: `result` valid + `candidate_id`/`assessment_type_id` non-kosong.
- **Handlers** (RBAC `isHR`): `POST /candidates/:id/assessments` (rekam), `GET /assessments` (list semua, diperkaya nama/posisi kandidat + nama tipe — untuk menu), `GET /candidates/:id/assessments` (per-kandidat), `PUT /assessments/:id`, `DELETE /assessments/:id`. + routes + `candidateAssessmentsCol()`.

### FE ([[APP - Web ERP]])
- **Menu "Candidate Assessment"** di grup Recruitment (sidebar-menus) + rute `app/(main)/hris/recruitment/assessments/page.tsx`.
- **Halaman** (mirror `hr-interviews-page`): tabel semua assessment (kandidat, tipe, skor, **badge hasil** Pass=hijau/Fail=merah/Pending=amber, tanggal, penilai) + tombol **Rekam Assessment** → dialog form (pilih kandidat [Screening-only] + tipe [dropdown master] + skor + hasil + catatan) + aksi edit/hapus.
- **System Setup**: tab **"Assessment Types"** (reuse `LookupPage` + `assessmentTypesConfig`).
- Hooks `use-assessments` (list/create/update/delete) + `useLookups("assessment-types")`; i18n **dua locale**.
- **Reuse `CandidatePicker`**: generalisasi agar menerima daftar status yang diizinkan (kini hardcode `Interview`) → dipakai interview (`Interview`) & assessment (`Screening`). Refactor kecil untuk reuse.

## Slicing

1. **BE** (`services/recruitment`) — master assessment-types + entity `candidate_assessment` + handlers/routes + test murni (validasi result).
2. **FE** (erp-frontend) — generalisasi CandidatePicker + menu + halaman + dialog rekam + System Setup tab + i18n.

Deploy: BE + FE auto-deploy on merge; BE dulu efeknya (kontrak endpoint), FE menyusul.

## Belum Diputuskan / Catatan (kecil)

- Skor: dibuat **opsional** (result yang jadi penentu). Bila HRD mau skor wajib/berrentang, sesuaikan.
- Lampiran hasil tes (PDF) = **di luar scope** MVP (bisa fase lanjut, pola MinIO seperti CV).
- Menampilkan assessment di **detail kandidat** = opsional (bisa menyusul; MVP cukup menu tersendiri).

## Dokumen Terkait

- [[HRIS - Recruitment]] · [[HRIS - Recruitment Pipeline Redesign]] · [[Microservices - Recruitment Service]] · [[API - Recruitment Service]] · [[APP - Web ERP]]

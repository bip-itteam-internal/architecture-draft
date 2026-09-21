# ANALISA - Inspeksi 5R Area per Department

> Daftar task turunan [[ADR - 0111 Inspeksi 5R Area per Department sebagai Catatan Non-KPI dengan Peringatan ke Supervisor]]. Papan kerja — berubah tiap item selesai. Bukan rencana per-berkas (itu `/plan`).

## Ringkas keputusan (baca ADR untuk detail)

- Track **ketiga**: inspeksi 5R yang objeknya **ruangan/area department**, **non-KPI**, catatan + peringatan ke **supervisor department**. **Tidak** mengubah track per-PIC (ADR 0090) maupun catatan per-orang (ADR 0085).
- Rumah: **employee-service**, entitas baru `area_inspection`. Petugas = jabatan **Culture & Industrial** via izin **`kepatuhan.satgas.input`** yang sudah ada.
- Objek = **daftar department** (12 di dev), periode **bulanan**, **≤15 foto** per department per periode.

## Urutan & dependensi

**BE dulu (kontrak), lalu mobile & web. Koordinasi wajib dengan sesi `feat/satgas-input-web`, `feat/satgas-rekap`, dan mobile `feat/faiz`.**

### T1 — (BE) Entitas & penyimpanan `area_inspection`
Model baru di `shared-library/models/employee` + koleksi di employee-service: `(company_id, department, period_key, ada_temuan, catatan, foto []upload_id, recorded_by, recorded_at)`. Kunci unik per `(company_id, department, period_key)` bila satu inspeksi per department per periode (konfirmasi saat `/plan`). **Verifikasi pola** yang dipinjam dari `compliance_note` (ADR 0085) benar-benar ada/jalan, jangan diasumsikan matang.
- Bergantung pada: —
- Selesai bila: dokumen bisa ditulis/dibaca dengan bentuk yang divalidasi (fixture yang `department` & `period_key`-nya berbeda-beda, bukan seragam).

### T2 — (BE) Gerbang tulis + resolusi periode
Endpoint `POST` inspeksi area digerbang **server-side** terhadap `kepatuhan.satgas.input` (reuse; menu di app bukan gerbang). Periode berjalan bulanan (samakan idiom dengan Satgas: rentang mati sebelum open_day bila dipakai). **Multi-foto ≤15**: pola **unggah-dulu-kirim-id** (jangan berkas di dalam JSON), simpan ke file-service/MinIO; batas 4 MB/file tak dinaikkan.
- Bergantung pada: T1.
- Selesai bila: petugas ber-izin bisa submit temuan+≤15 foto untuk sebuah department; non-petugas ditolak 403 berpesan; uji lewat **gateway** (bukan hanya unit).

### T3 — (BE) Baca dua-arah + rekap per-department
`GET` daftar department + status periode berjalan untuk **petugas**; `GET` rekap temuan untuk **supervisor** atas department yang diawasinya (`SupervisedDepartmentsStrict`, tanpa fallback; filter via `ResolveDepartmentFilter` + `ExpandToDepartmentGroup` — gotcha HRGA). **Tak ada** jalur "karyawan lihat dirinya" (objeknya ruangan). **Tidak** menulis `kpi_score`/`employee_warning`; **tidak** daftar ke calendar/feed.
- Bergantung pada: T1.
- Selesai bila: supervisor A hanya melihat department yang benar-benar diawasinya; petugas melihat 12 department; uji negatif (supervisor lain tak bocor).

### T4 — (Mobile, `feat/faiz`) Mode "Area/Ruangan" di menu Satgas
Tambah mode di permukaan Satgas MyBharata: daftar department → tap → "Ada temuan?" + **≤15 foto** + catatan → kirim (kontrak T2/T3). **Reuse** `SurveyFillView`/boolean/`survey_file_input`/kompres foto — **jangan** bikin komponen isi/unggah baru. i18n id+en (ADR 0010).
- Bergantung pada: T2, T3 (kontrak BE live di dev).
- Selesai bila: petugas `TEST-HR-STAFF` bisa memilih department, mengisi, mengirim ≤15 foto, dan hasilnya terbaca di rekap; dijalankan **sebagai orang**, bukan hanya curl.

### T5 — (Web, koordinasi) Rekap area untuk supervisor
Rekap temuan area per-department di tab `hris/industrial-relation` untuk supervisor. **Koordinasi** dengan sesi `feat/satgas-input-web` & `feat/satgas-rekap` agar tak lahir dua model/menu. Reuse struktur tabel HRIS (MainTable + Banner bare).
- Bergantung pada: T3.
- Selesai bila: supervisor membaca temuan ruangannya di web; tak menabrak rekap per-PIC yang sudah ada.

### T6 — (Keputusan, bukan kode) KPI & notifikasi — TBD
- **KPI**: sengaja **tidak** dipetakan. Bila HR/manajemen kelak ingin skor area memengaruhi KPI seseorang → ADR baru + peta department→penanggung jawab (belum ada). Jangan dikerjakan tanpa keputusan.
- **Peringatan push ke SPV**: irisan-1 cukup rekap-saat-dibuka. Push = kategori inbox baru (notification-service + pengirim naik **bersama**) + ADR/revisi. Ditunda sampai rekap terbukti kurang.

## Titik yang harus diputuskan saat `/plan`
- Satu inspeksi per (department, periode) atau boleh banyak (mis. temuan lalu perbaikan)?
- ≤15 foto: per-temuan atau per-department per-periode?
- Izin: reuse `kepatuhan.satgas.input` (default) atau izin baru di modul `kepatuhan` bila petugas area ≠ petugas PIC.
- Mobile: mode di dalam menu Satgas existing vs menu terpisah.

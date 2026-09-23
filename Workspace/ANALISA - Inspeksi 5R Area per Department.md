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

### T3 — (BE) Baca dua-arah + rekap per-department ✅ selesai di branch `feat/area-inspection-baca-rekap` (belum merged)
`services/employee/area_inspection_read.go`: `GET /area-inspections?period` (roster petugas), `GET /area-inspections/rekap?period` (petugas semua / supervisor via `SupervisedDepartmentsStrict`+`ExpandToDepartmentGroup`, deny-by-default 403), `GET /area-inspections/:id/photos/:idx/preview`. Non-KPI. 9 test Fiber hijau. Cakupan SPV nyata diverifikasi lewat gateway (butuh DB+master) — belum.

**Refinasi 2026-09-23: roster ikut department TERPILIH di form Satgas, bukan seluruh master department.** Bug dari layar ("di pengaturan form beberapa department dipilih, tapi di mobile tampil semua"). Lintas-service: form-builder mengekspos `GET /internal/satgas/area-departments` (union `subject.departments` form Satgas terbit, `satgas_area_departments.go`, gerbang kunci layanan); employee-service `handleAreaInspectionRoster` memanggilnya lalu menyaring master (`departemenRosterTerpilih`, murni, `area_inspection_departments.go`). Reuse `FORM_BUILDER_MODULE_URL`+`FORM_BUILDER_SERVICE_KEY` yang sudah ada — tanpa env baru. Gagal fetch → 500. Test form-builder (union/gerbang) + employee (scoping+500) hijau. **Diverifikasi dev lewat gateway: roster = 8 department terpilih (bukan 12).**

`GET` daftar department + status periode berjalan untuk **petugas**; `GET` rekap temuan untuk **supervisor** atas department yang diawasinya (`SupervisedDepartmentsStrict`, tanpa fallback; filter via `ResolveDepartmentFilter` + `ExpandToDepartmentGroup` — gotcha HRGA). **Tak ada** jalur "karyawan lihat dirinya" (objeknya ruangan). **Tidak** menulis `kpi_score`/`employee_warning`; **tidak** daftar ke calendar/feed.
- Bergantung pada: T1.
- Selesai bila: supervisor A hanya melihat department yang benar-benar diawasinya; petugas melihat 12 department; uji negatif (supervisor lain tak bocor).

### T4 — (Mobile, `feat/faiz`) Mode "Area/Ruangan" di menu Satgas ✅ selesai di branch `feat/faiz` (belum diuji perangkat)
Fitur `lib/src/features/area_inspection/*` (Clean Architecture + get_it DI + i18n arb id/en). Dijangkau dari AppBar menu Satgas (ikon gedung) saat `overview.allowed` — HANYA petugas. Isi: "Ada temuan?" + catatan + ≤15 foto dikompres <1MB, pola submit-dulu lalu unggah tiap foto. Endpoint **lokal di datasource** (bukan url.dart, disunting paralel). `dart analyze` bersih, `flutter test` penuh 1538 hijau. Uji perangkat + rilis (version name+code) belum.

Tambah mode di permukaan Satgas MyBharata: daftar department → tap → "Ada temuan?" + **≤15 foto** + catatan → kirim (kontrak T2/T3). **Reuse** `SurveyFillView`/boolean/`survey_file_input`/kompres foto — **jangan** bikin komponen isi/unggah baru. i18n id+en (ADR 0010).
- Bergantung pada: T2, T3 (kontrak BE live di dev).
- Selesai bila: petugas `TEST-HR-STAFF` bisa memilih department, mengisi, mengirim ≤15 foto, dan hasilnya terbaca di rekap; dijalankan **sebagai orang**, bukan hanya curl.

### T5 — (Web, koordinasi) Rekap area untuk supervisor ✅ selesai di branch `feat/area-inspection-rekap-web` (belum merged)
Tab baru "Inspeksi Area", gate `canSatgasInput || isAnySupervisor(system_roles)` — peran modul HANYA menampilkan tab, cakupan department ditegakkan backend (T3), **tanpa klaim JWT baru** (keputusan: klaim is_supervisor ditunda, blast-radius auth). `area-inspection-rekap.tsx` + `use-area-inspection.ts`, foto via `openFileBlob`. i18n id+en.

**Tambahan 2026-09-23:** (a) **Menu dipisah** — "Satgas 5R & K3" jadi menu sidebar tersendiri (segrup Industrial Relation) berisi tab **Inspeksi Individu** + **Inspeksi Area** (rute `/hris/satgas`); menu lama jadi induk bersarang **Catatan Kepatuhan** + **Satgas 5R & K3**. (b) **Input area lewat WEB** — tab Inspeksi Area kini punya toggle **Rekap/Isi Inspeksi** untuk petugas (`area-inspection-{tab,input,fill-sheet}.tsx` + hooks `useAreaRoster/useAreaSubmit/useAreaPhotoUpload`), Ada temuan? + catatan + ≤15 foto (kompres ~1920px), submit-dulu-lalu-unggah. Tak lagi hanya MyBharata. tsc/lint/build + test hijau.

Rekap temuan area per-department di tab `hris/industrial-relation` untuk supervisor. **Koordinasi** dengan sesi `feat/satgas-input-web` & `feat/satgas-rekap` agar tak lahir dua model/menu. Reuse struktur tabel HRIS (MainTable + Banner bare).
- Bergantung pada: T3.
- Selesai bila: supervisor membaca temuan ruangannya di web; tak menabrak rekap per-PIC yang sudah ada.

### T6 — (Keputusan, bukan kode) KPI & notifikasi — TBD
- **KPI**: sengaja **tidak** dipetakan. Bila HR/manajemen kelak ingin skor area memengaruhi KPI seseorang → ADR baru + peta department→penanggung jawab (belum ada). Jangan dikerjakan tanpa keputusan.
- **Peringatan push ke SPV**: irisan-1 cukup rekap-saat-dibuka. Push = kategori inbox baru (notification-service + pengirim naik **bersama**) + ADR/revisi. Ditunda sampai rekap terbukti kurang.

## Titik yang sudah diputuskan (saat `/plan` + implementasi 2026-09-23)
- **Satu inspeksi per (department, periode)** — upsert (index unik T2), tanpa alur cek-ulang temuan→perbaikan terpisah.
- **≤15 foto per (department, periode)** (bukan per-temuan) — `MaxAreaInspectionPhotos`.
- **Izin reuse `kepatuhan.satgas.input`** (petugas area = petugas PIC, orang sama). Tak ada izin baru.
- **Mobile: fitur `area_inspection` tersendiri, dijangkau dari AppBar menu Satgas** (bukan mode-toggle di `SatgasView`). Hanya petugas.
- **Visibilitas SPV web via peran modul + gerbang backend, TANPA klaim JWT `is_supervisor`** (ditunda; blast-radius auth ~7 jalur login). Rincian di ADR §Diputuskan saat implementasi.

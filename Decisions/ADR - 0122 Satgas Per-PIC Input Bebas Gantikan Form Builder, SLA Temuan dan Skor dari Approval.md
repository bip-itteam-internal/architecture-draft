> **Status**: 🟡 **Diusulkan** (2026-09-24) — kode belum ada. Menggantikan **mekanisme** [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] (form-builder + cek-ulang), **bukan** tujuannya: KPI kebersihan Office Boy & Security tetap ada, hanya cara mencatat dan menilainya berubah. Tidak menyentuh track Inspeksi Area ([[ADR - 0111 Inspeksi 5R Area per Department sebagai Catatan Non-KPI dengan Peringatan ke Supervisor]]) maupun Catatan Kepatuhan ([[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]]).

## Untuk Manajemen

Inspeksi Satgas 5R & K3 untuk Office Boy & Security **tidak lagi lewat form** yang harus dibuat dulu tiap periode. Petugas HR Culture & Industrial **mencatat temuan kapan saja, langsung dari menunya** — bebas menentukan kapan dan apa yang dinilai.

**Apa yang berubah di layar:** petugas membuka menu Satgas, memilih orangnya (OB/Security), menulis temuan + foto, dan menetapkan **berapa hari** tenggat perbaikan. Bila lewat tenggat orangnya belum mengirim **foto bukti perbaikan**, petugas memilih tindakan: **(a) menahan clock-out** orang itu di aplikasi sampai ia menanggapi, atau **(b) memberi nilai otomatis 1 dari 10**. Bila ada balasan foto, petugas **menyetujui sambil memberi nilai**. Nilai KPI kebersihan orang itu di bulan tersebut dihitung **dari kasus temuan saja** — bulan tanpa temuan otomatis bernilai penuh.

**Siapa yang terdampak:** petugas HR Culture & Industrial (mencatat & menilai), Office Boy & Security (menanggapi temuan dengan foto perbaikan).

**Apa yang TIDAK dijanjikan:** ini **bukan Surat Peringatan** dan **bukan potongan gaji**. "Menahan clock-out" adalah **dorongan agar temuan ditanggapi**, bukan sanksi — sama seperti mekanisme yang sudah berjalan untuk Catatan Kepatuhan; orangnya bisa membuka kuncinya sendiri dengan menanggapi. Nilai 1/10 memengaruhi **skor KPI**, bukan gaji secara langsung. Peraturan Perusahaan tidak mengatur inspeksi 5R, jadi tak ada aturan yang dilanggar; keputusan ini sendiri yang menjadi catatan resminya.

**Perkiraan besaran kerja:** sedang. Sebagian besar bahannya sudah jadi — mekanisme tahan clock-out, unggah foto, gerbang petugas, tampilan input bebas (dipinjam dari Inspeksi Area), dan komponen "beri nilai" sudah ada di sistem. Yang baru: satu penyimpanan temuan Satgas, alur balas-dengan-foto, dan tombol setujui-dengan-nilai. Perlu rilis backend lebih dulu, lalu aplikasi & web.

## Deskripsi

*Inspeksi Satgas 5R & K3 per-PIC (Office Boy & Security) pindah dari mesin Form Builder ke **entitas sendiri `satgas_finding` di employee-service**, dengan pencatatan **bebas** (petugas menentukan kapan & siapa, tanpa form/periode/sasaran pra-bangun), **SLA per temuan**, **eskalasi memakai ulang mekanisme tahan-clock-out** yang sudah ada di track Catatan Kepatuhan, dan **skor KPI dari hasil approval** temuan. Menggantikan mekanisme form-builder + cek-ulang [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]], mempertahankan tujuan KPI-nya, dan menjaga pemisahan struktural terhadap Inspeksi Area (ADR 0111), Catatan Kepatuhan (ADR 0085), dan Surat Peringatan.*

- **Status**: 🟡 **Diusulkan** — kode belum ada. Daftar task: `Workspace/ANALISA - Redesign Satgas Input Bebas dan SLA Temuan.md`
- **Path di repo** (yang **akan** disentuh):
  - bip-erp: `shared-library/models/employee/satgas_finding.go` (baru) · `services/employee/satgas_finding.go` (baru: catat/roster/list/balas/approve/SLA) · `services/employee/satgas_finding_read.go` (baru: rekap petugas) · `services/employee/compliance_note.go` (revisi: `handleComplianceBlock` ikut membaca `satgas_finding` yang ditandai kunci clock-out) · `services/employee/kpi_sumber_inspeksi_satgas.go` (revisi: baca `satgas_finding` **in-process**, lepas panggilan HTTP `/internal/satgas/metrics`) · `services/form-builder/*` (metric_key `inspeksi_satgas` di-*retire* bertahap)
  - erp-frontend: `src/features/hris/satgas/*` (revisi: input bebas meniru `area-inspection-fill-sheet.tsx`, antrean approval beri-nilai) · reuse `SkalaAngka`, `foto-satgas-dialog.tsx`, `openFileBlob`
  - my-bharata: `lib/src/features/satgas/*` (revisi: input bebas, balas-dengan-foto) · reuse gerbang & sheet tahan-clock-out `presence_compliance_block_sheet.dart`
- **Tanggal**: 2026-09-24

## Context

Grounding ke kode (bip-erp, erp-frontend, my-bharata) dan vault, 2026-09-24 (empat subagent paralel; klaim ber-`file:line`):

1. **Mesin Satgas sekarang = Form Builder, dan itu yang dikeluhkan kaku.** `metric_key: inspeksi_satgas` (`services/form-builder/models_form.go:242`) hanya sah di form `evaluation`, **recurring bulanan**, sasaran aktif, **tepat satu** pertanyaan boolean "Ada temuan?", tanpa `single_response`. Nilai = kiriman TERAKHIR per orang per periode (`satgas_nilai.go:34-52`), cek-ulang sampai **tanggal 5** bulan berikutnya (`satgas_nilai.go:137`). Petugas TIDAK memilih kapan/siapa — server memberi roster periode berjalan (`erp-frontend .../satgas-input-view.tsx:34-162`). Kekakuan inilah kebutuhan yang sebenarnya: **fleksibilitas mencatat**.

2. ⛔ **Kunci clock-out SUDAH ADA end-to-end** — di track Catatan Kepatuhan (IR fase-2), bukan Satgas. `ComplianceViolationType.KunciClockout` + `GraceHari` (`shared-library/models/employee/master_data.go:234,239`) → gerbang clock-out `services/attendance/compliance_gate.go` (mobile-only, **fail-open**, timeout 1,5 dtk) membalas **403 `respond_compliance`** → sheet MyBharata → karyawan membalas → `responded_at` melepas. Aturan lock **diturunkan, bukan flag** (`services/employee/compliance_note.go:543-552` `noteMenahanClockout`: `KunciClockout && RespondedAt==nil && now>recorded_at+GraceHari`). Endpoint `GET /internal/compliance-block` (`compliance_note.go:519,673`) yang attendance panggil. **Ini yang dipakai ulang** untuk eskalasi Satgas, bukan dibangun baru.
   - ⚠️ **Dibingkai sengaja sebagai nudge, BUKAN sanksi** (`my-bharata .../presence_compliance_block_sheet.dart:10-11`). Redesign memakainya dengan framing yang sama.

3. **Loop balas + foto sebagian ada.** Catatan Kepatuhan punya balasan (`POST /compliance-notes/:id/response`) tapi **TEXT-only** (`compliance_note_remote_datasource.dart:236-256`); foto hanya di sisi pencatat. **Balas-dengan-foto** (bukti perbaikan) belum ada — ini baru. **Approve-with-score & auto-1/10 tak ada di mana pun** — Catatan Kepatuhan tak pernah menyentuh `kpi_score` (sengaja non-KPI, ADR 0085).

4. **Kontrak KPI hanya peduli bentuk JSON.** Sumber `nilai_inspeksi_satgas` (`services/employee/kpi_sumber_inspeksi_satgas.go:23`) memetakan payload sempit `{employee_id, nilai, forms_dinilai, forms_total, ...}` jadi `Cuplikan`; ia menghitung ulang **tak boleh** (definisi kedua yang menyimpang, `:16-22`). Karena `satgas_finding` tinggal di **employee-service yang sama**, sumber ini bisa membacanya **in-process** — **melepas** panggilan HTTP `/internal/satgas/metrics` + `FORM_BUILDER_SERVICE_KEY` (kopling lintas-service yang baru saja jadi sumber bug, .env prod). Penulis `kpi_score` tetap `POST /kpi` (`kpi_finalisasi.go:22-24`, ADR 0032) — tak berubah.

5. **Cetakan "input bebas" sudah ada:** track Inspeksi Area (ADR 0111) `area_inspection` (`area_inspection.go:27-48`) sudah "input langsung, foto+catatan, tanpa form-builder" — di web `area-inspection-fill-sheet.tsx` (Switch "Ada temuan?" + Textarea + multi-foto, submit-dulu-lalu-unggah). **Tapi subjeknya department & non-KPI** — jangan dicampur; per-PIC tetap subjek **orang** & ber-KPI.

6. ⛔ **Gerbang aturan bisnis (Gate 1).** `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` (menang atas perilaku sistem) **DIAM** soal kunci clock-out sebagai sanksi, skor 1/10, dan SLA temuan; "Security" hanya baris jadwal shift ("Diatur Terpisah"), "Office Boy" tak muncul; PP tak punya pasal 5R/K3. Konsekuensinya: framing **nudge + skor KPI** tak melanggar apa pun. Per [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]] §4, penyimpangan disengaja wajib jadi ADR — **ADR ini** catatannya. Tak perlu ubah dokumen regulasi selama tak dijadikan potongan gaji.

7. **Status dok tetangga (berdiri di atas rencana):** ADR 0085 tercatat 🟡 di vault, tetapi **kodenya nyata ada** (`compliance_note.go` + gerbang clock-out live di dev) — status vault-nya usang. ADR 0111 ⚠️ di branch, belum prod. ADR 0090 ⚠️ dev, prod belum. Jadi redesign berdiri di atas mekanisme yang **sudah berjalan di dev**, bukan konsep — tapi belum satupun di prod.

## Decision

### 1. Entitas `satgas_finding` sendiri di employee-service, subjek ORANG, ber-KPI

Koleksi baru `satgas_finding` di employee-service (service yang sama dengan `compliance_note`, `area_inspection`, dan sumber KPI). Satu dokumen = satu temuan atas satu orang: `(company_id, employee_id, dicatat_oleh, dicatat_pada, ada_temuan, catatan, foto[], sla_hari, deadline, tindakan, response{foto[], pada}, disetujui_oleh, disetujui_pada, nilai, status, period_key)`. **Bukan** di form-builder (mesinnya periodik/kaku), **bukan** menumpang `compliance_note` (sengaja non-KPI, mencampur skor mengaburkan batas ADR 0085), **bukan** `area_inspection` (subjek department). Pemisahan koleksi membuat batas **per-PIC-ber-KPI ≠ area ≠ catatan atribut ≠ SP** tetap struktural.

### 2. Pencatatan BEBAS menggantikan form + periode + sasaran

Petugas (`kepatuhan.satgas.input`, gerbang server yang sudah ada) memilih orang (OB/Security) dan mencatat temuan **kapan saja** — tanpa membuat form, tanpa roster periode, tanpa "tepat satu pertanyaan boolean". `period_key` diturunkan dari tanggal catat (bulan temuan), bukan dari form. Idiom cek-ulang "sampai tanggal 5" **dihapus**, digantikan alur balas→approve per temuan.

### 3. SLA per temuan + eskalasi memakai ulang mekanisme tahan-clock-out

Saat mencatat temuan, petugas menetapkan **`sla_hari`** (tenggat = `dicatat_pada + sla_hari`). Pengingat inbox dikirim (pola "peringatkan dulu, tahan belakangan" yang sudah ada). Bila lewat tenggat & belum ada `response`, petugas memilih **`tindakan`**:
- **`kunci_clockout`** — temuan ini ikut dibaca `handleComplianceBlock` (`GET /internal/compliance-block`) sehingga attendance menahan clock-out orang itu **dengan gerbang yang persis sama** dengan Catatan Kepatuhan. Lepas saat `response` (foto) masuk. **Reuse, bukan gerbang attendance baru.**
- **`nilai_1`** — status jadi terminal, `nilai = 1` (dari 10). Menutup kasus tanpa menunggu tanggapan.

Kedua tindakan **pilihan petugas**, bukan otomatis saat tenggat lewat (petugas yang memutuskan, sesuai kebutuhan).

### 4. Balas-dengan-FOTO lalu approve-dengan-NILAI

Orang yang dinilai menanggapi temuan dengan **foto bukti perbaikan** (baru: balasan Catatan Kepatuhan sekarang text-only; Satgas menuntut foto). Petugas lalu **meng-approve sambil memberi `nilai` 1–10**. Skala 1–10 dipetakan ke 0–100 internal KPI (×10) — berbeda dari skala 1–5 lama form-builder, dan itu disengaja (angka "1/10" langsung dari kebutuhan).

### 5. KPI = dari kasus temuan saja, rata-rata, dibaca in-process

Skor KPI kebersihan OB/Security satu periode dihitung **hanya dari kasus temuan** periode itu: nilai approval, atau `1` untuk `nilai_1`. **Beberapa temuan → rata-rata** nilainya. **Tanpa temuan → penuh (100)**. Sumber `nilai_inspeksi_satgas` membaca `satgas_finding` **langsung di dalam proses employee-service**, memancarkan bentuk `Cuplikan` yang sama — **tanpa** panggilan HTTP lintas-service. Metrik yang disuapinya tetap: Office Boy "Kebersihan 3", Security "Kerapihan dan kebersihan Pos". Penulis `kpi_score` tetap `POST /kpi`.

### 6. Kunci clock-out = NUDGE, bukan sanksi; 1/10 = skor KPI, bukan potong gaji

Framing dipertahankan seperti mekanisme yang sudah ada: menahan clock-out adalah dorongan menanggapi, orangnya melepas sendiri dengan membalas. `nilai_1` memengaruhi KPI, tidak membaca/menulis payroll, tidak membuat `employee_warning`/SP. Tak ada perubahan dokumen regulasi; ADR ini catatan penyimpangannya (ADR 0071 §4). Bila kelak manajemen ingin menjadikannya sanksi gaji, itu **keputusan baru** + revisi `BUSINESS_LOGIC_IMPLEMENTATION.md`, bukan otomatis di sini.

### 7. Retire form-builder Satgas bertahap

`metric_key: inspeksi_satgas` dipensiunkan **setelah** `satgas_finding` + sumber KPI in-process live. Selama transisi sumber KPI boleh membaca dua asal (form-builder lama + finding baru) agar skor tak kosong mendadak. Jawaban form Satgas historis dibiarkan sebagai arsip (tidak dimigrasi), kecuali pengukuran prod menuntut lain.

## Consequences

### Yang membaik
- Petugas mencatat temuan **kapan saja, atas siapa saja** (OB/Security) tanpa merakit form — menjawab keluhan "form-builder ribet & kaku".
- **Melepas kopling lintas-service** `/internal/satgas/metrics` + `FORM_BUILDER_SERVICE_KEY` (sumber KPI baca in-process) — menghapus satu kelas bug yang baru saja menggigit (.env prod).
- Eskalasi memakai ulang gerbang tahan-clock-out yang **sudah live di dev**, bukan menambah gerbang attendance baru.
- Batas per-PIC-KPI ≠ area ≠ catatan atribut ≠ SP tetap struktural (koleksi terpisah).

### Yang memburuk atau tetap terbuka
- ⚠️ **Prod belum diukur.** Berapa banyak temuan/inspeksi Satgas hidup di prod belum dihitung; keputusan migrasi (arsip vs pindah) menunggu pengukuran. Risiko: nol data mengecoh.
- ⚠️ **Balas-dengan-foto & approve-dengan-nilai benar-benar baru** — bukan reuse; jalur unggah foto sisi karyawan + endpoint approval harus dibangun & diuji lewat gateway (jangan andalkan test fungsi murni).
- ⚠️ **Agregasi rata-rata** dipilih; bila manajemen ingin "terburuk menang" itu satu baris ubah, tapi harus diputuskan sebelum orang membaca skornya.
- **Berdiri di atas mekanisme dev, bukan prod.** Gerbang clock-out & Catatan Kepatuhan live di dev, ADR 0090/0111 belum prod. Redesign ini menambah beban rilis di area yang belum stabil di prod.
- **cek-ulang "sampai tanggal 5" hilang.** Siapa pun yang bergantung pada idiom itu (laporan bulanan) harus tahu skornya kini per-temuan, bukan kiriman-terakhir-periode.

### Yang sengaja tidak dilakukan
- Tidak menjadikan kunci clock-out / 1/10 sebagai **sanksi PP / potongan gaji** (butuh ADR + revisi dokumen regulasi tersendiri).
- Tidak menyentuh track Inspeksi Area (ADR 0111) maupun Catatan Kepatuhan (ADR 0085) — keduanya track berbeda.
- Tidak menambah izin baru (reuse `kepatuhan.satgas.input`).
- Tidak membuat kategori inbox baru bila pengingat memakai kategori kepatuhan yang sudah ada; bila perlu kategori baru → naikkan `notification-service` + pengirim bersama.

### Konsekuensi deploy
- **BE sebelum FE** (kontrak baru).
- Perluasan `handleComplianceBlock` → **employee-service + attendance-service naik bersama** (attendance pemanggilnya), lalu picu satu clock-out nyata untuk membuktikan.
- Tanpa env baru bila `satgas_finding` di employee-service (KPI baca in-process; tak butuh `FORM_BUILDER_SERVICE_KEY`).
- Retire form-builder Satgas **setelah** finding + sumber KPI live; jangan cabut `metric_key` sebelum itu (skor kosong).

## Dokumen Terkait
- [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] — mekanisme yang **digantikan** (form-builder + cek-ulang); tujuan KPI-nya dipertahankan
- [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] — sumber mekanisme tahan-clock-out & loop balas yang dipakai ulang
- [[ADR - 0111 Inspeksi 5R Area per Department sebagai Catatan Non-KPI dengan Peringatan ke Supervisor]] — track area (subjek department, non-KPI); cetakan input bebas
- [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]] — kewajiban ADR untuk penyimpangan disiplin
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] — batas penulis `kpi_score`
- [[HRIS - Industrial Relation]] — dok domain (cara kerja modul) · [[Microservices - Employee Service]] · [[Microservices - Attendance Service]]
- Daftar task: `Workspace/ANALISA - Redesign Satgas Input Bebas dan SLA Temuan.md`

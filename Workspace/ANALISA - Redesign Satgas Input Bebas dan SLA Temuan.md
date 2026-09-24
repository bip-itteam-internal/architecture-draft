# ANALISA - Redesign Satgas Input Bebas dan SLA Temuan

> Daftar task turunan [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]]. Papan kerja — berubah tiap item selesai. Bukan rencana per-berkas (itu `/plan`). Menggantikan pendekatan lama di [[ANALISA - Inspeksi Satgas 5R dan K3]] (form-builder).

## Status implementasi (2026-09-24)

**T1–T6 SELESAI di branch, belum merged/deploy, mobile belum diuji perangkat.** T7–T8 belum.
- **T1–T4 + preview** → bip-erp `feat/satgas-finding` (pushed). Endpoint catat/foto/rekap/me/response/approve/**escalate**/preview; SLA+eskalasi (`kunci_clockout`/`tutup_gagal`) union ke `handleComplianceBlock`; kategori inbox `satgas-temuan`; skor KPI in-process. **Attendance tak berubah** (union cukup).
- **T5** → erp-frontend `feat/satgas-finding-web` (pushed). Tab Individu jadi `SatgasPerPicView` (catat bebas + approve + eskalasi + rekap pembaca), foto via `openFileBlob`.
- **T6** → my-bharata `feat/satgas-finding-mobile` (pushed). Layar "Temuan Saya" OB/Security balas-dengan-foto; notifikasi `satgas-temuan` dipetakan. TANPA bump versi (feat/faiz sudah 1.23.0+172).
- ⚠️ **Menyimpang dari rencana awal papan ini (ADR yang menang):** tindakan kedua = **`tutup_gagal`** (bukan `nilai_1`); approve = **konfirmasi TANPA mengetik nilai** (bukan "approve dengan nilai"); skor `open` yang **masih dalam tenggat = MENUNGGU** (tak dihukum); tanpa dokumen sama sekali = **belum dapat dihitung** (bukan 100). Form-builder Satgas kini **dead code** (cleanup = task terpisah, bagian T7).

## Ringkas keputusan (baca ADR untuk detail)

- Satgas per-PIC (OB/Security) **lepas dari form-builder** → entitas `satgas_finding` di **employee-service**, subjek **orang**, **ber-KPI**. Pencatatan **bebas** (kapan & siapa saja).
- **SLA per temuan** (petugas set `sla_hari`). Lewat tenggat tanpa balasan → petugas pilih **kunci_clockout** (reuse gerbang tahan-clock-out yang sudah ada) **atau** **nilai_1** (skor 1/10 terminal).
- Balas = **foto bukti perbaikan** → petugas **approve dengan nilai** (1–10 → 0–100).
- **KPI = dari kasus temuan saja, rata-rata**; tanpa temuan = penuh (100). Dibaca **in-process** oleh `nilai_inspeksi_satgas` (lepas HTTP `/internal/satgas/metrics`).
- Kunci clock-out = **nudge**, bukan sanksi; 1/10 = skor KPI, bukan potong gaji. Gerbang petugas `kepatuhan.satgas.input` di-reuse.

## Urutan & dependensi

**BE dulu (kontrak), lalu mobile & web. Retire form-builder Satgas paling akhir.**

### T1 — (BE) Entitas & penyimpanan `satgas_finding` + gerbang tulis
Model `shared-library/models/employee/satgas_finding.go` + koleksi di employee-service: `(company_id, employee_id, dicatat_oleh, dicatat_pada, ada_temuan, catatan, foto[], sla_hari, deadline, tindakan, response{foto[], pada}, disetujui_oleh, disetujui_pada, nilai, status, period_key)`. Endpoint catat bebas (pilih orang OB/Security + catatan + foto + sla_hari), gerbang server `kepatuhan.satgas.input`. `period_key` diturunkan dari `dicatat_pada`. **Verifikasi pola** yang dipinjam dari `area_inspection`/`compliance_note` benar-benar ada (submit-dulu-lalu-unggah foto, gerbang).
- Bergantung pada: —
- Selesai bila: petugas ber-izin bisa mencatat temuan atas seorang OB/Security lengkap dengan foto & sla_hari; non-petugas 403; diuji lewat **gateway**. Fixture yang `employee_id`/`_id`-nya berbeda (gotcha ID).

### T2 — (BE) Balas-dengan-foto + approve = KONFIRMASI + mesin status
Endpoint balasan karyawan (WAJIB **foto** bukti perbaikan, beda dari balasan Catatan Kepatuhan yang text-only): `POST /satgas-findings/:id/response` (owner-only, unggah foto). Endpoint approval petugas = **mengonfirmasi temuan sudah diperbaiki** (menerima foto), **TANPA mengetik angka**. Status: `open` → `responded` → `approved` (atau `tutup_gagal`). **Skor tidak disimpan per temuan** — dihitung di T4 dari status + jumlah foto.
- Bergantung pada: T1.
- Selesai bila: karyawan bisa balas dengan foto; petugas approve dengan nilai; status & nilai tersimpan benar; uji jalur galat lewat `app.Test` (glue handler).

### T3 — (BE) SLA + eskalasi: reuse gerbang tahan-clock-out
Pengingat inbox saat temuan dibuat (pola "peringatkan dulu"). Tindakan petugas saat lewat tenggat: `kunci_clockout` (tandai finding) atau `nilai_1`. **Perluas `handleComplianceBlock`** (`services/employee/compliance_note.go`, `GET /internal/compliance-block`) agar ikut membaca `satgas_finding` ber-`tindakan=kunci_clockout` + `response==nil` + `now>deadline` — sehingga attendance menahan clock-out lewat gerbang yang SAMA. Lepas saat response masuk.
- Bergantung pada: T1, T2.
- Selesai bila: petugas menandai kunci → clock-out orang itu ditahan di dev (403 `respond_compliance`), balas foto → lepas; `nilai_1` menutup kasus. **Deploy employee-service + attendance-service bersama**, picu satu clock-out nyata. Reuse, bukan gerbang baru.

### T4 — (BE) Sumber KPI: skor OTOMATIS dari `satgas_finding` in-process
`services/employee/kpi_sumber_inspeksi_satgas.go` diubah membaca `satgas_finding` **langsung** (bukan HTTP `/internal/satgas/metrics`). Skor **dihitung sistem**: `max(0, 100 − Σ potongan)`; **tanpa temuan = 100**. Potongan per temuan: **diperbaiki tepat waktu = 5**; **tak ditanggapi / `tutup_gagal` = 15 + 5×(jumlah_foto−1), maks 30** (angka fungsi murni, teruji). Emit `Cuplikan` bentuk sama (Office Boy "Kebersihan 3", Security "Kerapihan dan kebersihan Pos"). **Transisi**: boleh baca dua asal (finding baru + form-builder lama) sampai T7.
- Bergantung pada: T1, T2.
- Selesai bila: skor KPI OB/Security muncul dari finding; test **fungsi murni** rumus potongan (no-temuan=100, diperbaiki=−5, gagal=−(15+5×(foto−1)) cap 30, floor 0) hijau; **lepas `FORM_BUILDER_SERVICE_KEY`** dari jalur ini.

### T5 — (Web) Input bebas + antrean approval beri-nilai + rekap
Menu Satgas (`/hris/satgas`, tab Inspeksi Individu): ganti input form-builder dengan **sheet input bebas** meniru `area-inspection-fill-sheet.tsx` (pilih orang + catatan + foto + sla_hari). Antrean approval memakai `SkalaAngka` + pola footer approve (`request-approval-footer.tsx`/`capa-approval-cell.tsx`). Foto via `foto-satgas-dialog.tsx`/`openFileBlob`. Rekap membaca skor dari finding. i18n id+en.
- Bergantung pada: T1–T4 (kontrak live di dev).
- Selesai bila: petugas mencatat, memberi tenggat, menahan/menilai, dan approve-dengan-nilai — dari web; dijalankan **sebagai orang** lewat gateway.

### T6 — (Mobile, `feat/faiz`) Input bebas petugas + balas-dengan-foto karyawan
MyBharata: petugas mencatat temuan bebas (reuse alur unggah foto). Karyawan membalas temuan dengan **foto** (baru; hari ini balasan Catatan Kepatuhan text-only) — reuse sheet tahan-clock-out `presence_compliance_block_sheet.dart` sebagai pintu masuk. i18n id+en. **Naikkan version name+code** (VERSION_MANAGEMENT.md, dua argumen).
- Bergantung pada: T1–T3.
- Selesai bila: petugas mencatat & menahan clock-out; karyawan yang tertahan membuka menu, balas dengan foto, kunci terlepas; diuji **sebagai orang** di perangkat.

### T7 — (BE) Retire form-builder Satgas
Setelah T4 live & terverifikasi: pensiunkan `metric_key: inspeksi_satgas` (form-builder) — hentikan pembuatan form Satgas baru, sumber KPI berhenti membaca form-builder. Jawaban historis diarsip (tidak dimigrasi, kecuali T8 menuntut lain).
- Bergantung pada: T4 live di prod, T5/T6 live.
- Selesai bila: tak ada jalur Satgas yang masih menyentuh form-builder; skor tetap muncul dari finding.

### T8 — (Ukur, bukan kode) Pengukuran prod + keputusan migrasi
Ukur di prod: berapa form Satgas & jawaban hidup, berapa OB/Security aktif. Putuskan arsip vs migrasi data historis. **Baca prod boleh, tulis tidak** (dijalankan manusia bila menulis).
- Bergantung pada: —
- Selesai bila: keputusan migrasi tercatat (ADR/append) sebelum T7 dieksekusi di prod.

## Titik yang sudah diputuskan (saat `/analisa-kebutuhan` 2026-09-24)
- **Skor KPI OTOMATIS 0–100** dari temuan: `max(0, 100 − Σ potongan)`, **tanpa temuan = 100**. Potongan/temuan: **diperbaiki tepat waktu = 5**; **gagal ditanggapi = 15 + 5×(foto−1), maks 30**. Petugas **tak mengetik nilai** (approve = konfirmasi perbaikan). Menggantikan rencana awal "nilai manual 1–10 / auto 1/10".
- **Kunci clock-out = nudge** (reuse mekanisme Catatan Kepatuhan), **bukan** sanksi gaji; temuan `tutup_gagal` menurunkan **skor KPI** lewat potongan, bukan potong gaji.
- **Reuse** gerbang `kepatuhan.satgas.input`, gerbang tahan-clock-out, pipeline foto, cetakan input bebas Inspeksi Area, komponen beri-nilai.
- **satgas_finding di employee-service** → sumber KPI baca **in-process**, lepas kopling lintas-service.

## Belum diputuskan (asumsi eksplisit, konfirmasi saat `/plan`)
- Balasan karyawan **wajib foto** (diasumsikan ya).
- Banyak temuan seperiode → **rata-rata** (bisa diganti "terburuk" bila diminta).
- Migrasi data historis form-builder Satgas (menunggu T8).

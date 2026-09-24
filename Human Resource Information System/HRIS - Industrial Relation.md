# HRIS - Industrial Relation

## Deskripsi

*Modul budaya kepatuhan ringan: petugas HR/IR yang ditunjuk mencatat pelanggaran atribut kerja (sepatu, lanyard, dsb.) secara diskret lewat MyBharata saat jam kerja, dan rekapnya tampil per departemen keesokannya sebagai **sinyal pembinaan** — bukan Surat Peringatan, bukan KPI resmi, bukan potongan gaji. Keputusan & alasannya di [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]].*

- **Status**: 🟡 Konsep / Direncanakan (disetujui 2026-09-10, kode belum ada)
- **Implementasi**: [[Microservices - Employee Service]] (backend, baru) · [[APP - Web ERP]] · [[APP - MyBharata]]

## Latar Belakang

Manajemen ingin budaya kepatuhan ringan di kantor benar-benar dijalankan, dengan umpan-balik yang low-friction dan tidak menghukum. Selama ini pelanggaran ringan (atribut) tidak punya kanal: satu-satunya tempat mencatat pelanggaran adalah [[HRIS - Disciplinary (Surat Peringatan)]], yang semantiknya sanksi berat (SP1/SP2/SP3, bisa berujung PHK). Menaruh "lupa lanyard" di sana keliru; membiarkannya tak tercatat membuat pembinaan bergantung ingatan orang.

`BUSINESS_LOGIC_IMPLEMENTATION.md` (Peraturan Perusahaan) tidak mengenal pasal atribut/seragam, jadi catatan ini memang bukan sanksi — melainkan pembinaan budaya, milik fungsi **Culture & Industrial** (HR org-dev).

## Ruang Lingkup / Cakupan (business view)

- **Katalog jenis pelanggaran** (master data, bisa diedit HR): sepatu, lanyard, atribut, dst. Bukan enum hardcoded.
- **Pencatatan diskret** lewat MyBharata oleh petugas IR/HR: pilih karyawan target + jenis pelanggaran + (dianjurkan) foto/catatan bukti.
- **Rekap per-departemen** di Web ERP (menu HR "Industrial Relation"): berapa & pelanggaran apa per departemen, dihitung saat baca (pola [[HRIS - Key Performance Index]] `ringkasan-departemen`), tampil untuk tanggal yang sudah lewat ("besoknya").
- **Catatan diri** untuk tiap karyawan: melihat catatan kepatuhan atas dirinya sendiri.
- **Bukan bagian** dari: skor KPI resmi (`kpi_score`), penerbitan SP otomatis, perhitungan payroll, kalender/feed lintas modul.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses / RBAC | Device |
|---|---|---|---|
| Petugas IR/HR | Culture & Industrial / Human Resource | `system_roles.hris` (admin/supervisor) — ditunjuk sebagai pencatat | MyBharata (catat) + Web ERP (kelola katalog & rekap) |
| Supervisor departemen | atasan (`work_data.is_supervisor`) | baca rekap timnya via `SupervisedDepartmentsStrict` | Web ERP |
| Karyawan | seluruh karyawan | baca catatan **dirinya sendiri** saja | MyBharata / Web ERP |

- **Tujuan**: menegakkan kepatuhan ringan lewat umpan-balik, bukan hukuman.
- **Pain point**: pelanggaran ringan tak punya kanal selain SP yang terlalu berat; pembinaan bergantung ingatan.
- **Aksi utama**: petugas mencatat diskret di lapangan → rekap muncul per departemen → supervisor & orangnya menindaklanjuti.

## Cara Kerja (rencana)

- **Data**: koleksi baru `compliance_note` (employee-service) — `employee_id`, `company_id`, `category` (rujuk katalog), `reason`, foto bukti (`MinIOFile`), `recorded_by`, `recorded_at`, masa berlaku. Status "aktif/hangus" **diturunkan saat baca** (pola `WarningStatus`, tidak disimpan).
- **Katalog**: master data jenis pelanggaran, CRUD digerbang keanggotaan modul HR.
- **Gerbang tulis**: `POST` catatan diperiksa di server terhadap wewenang pencatat; pemunculan menu MyBharata bukan gerbang.
- **Gerbang baca (tiga-arah)**: petugas IR/HR se-perusahaan · karyawan atas dirinya · atasan atas departemennya (`SupervisedDepartmentsStrict`, tanpa fallback). Filter departemen via `ResolveDepartmentFilter` + `ExpandToDepartmentGroup` (gotcha HRGA).
- **Rekap**: dihitung saat baca, meniru `kpi_ringkasan_departemen.go`; tanpa cron.
- **Reuse MyBharata**: pemilih karyawan (`AssigneeSelectSheet`), unggah foto+catatan (pola `FormData`+`MultipartFile` submission), gating menu (`RoleGuard`).
- **Reuse Web ERP**: struktur halaman meniru modul `surat-peringatan` (MainTable + Banner bare di toolbar), pola self-vs-team `kpi-departemen-atau-saya.tsx`, chart `BaganSkorBulanan`/`ChartContainer` bila perlu.

## Konsumen Data

- [[APP - Web ERP]] — menu HR "Industrial Relation" (rekap per departemen + daftar catatan)
- [[APP - MyBharata]] — menu pencatat (petugas IR/HR) + bagian "catatan kepatuhan saya" (karyawan)

## Kendala

- **Privasi**: pencatatan diskret atas rekan kerja; ditahan oleh pencatat terbatas & tercatat, transparansi ke orangnya, `Reason`/bukti dianjurkan wajib, dan tanpa penyebaran lintas modul (tidak masuk [[Microservices - Calendar Service]]).
- **Tiga permukaan** (BE/Web/Mobile) harus selaras; kontrak baru → deploy BE dulu.

## Belum Diputuskan (TBD)

- Penempatan menu: grup HR baru **atau** di bawah grup "Program Culture" yang sudah ada.
- Apakah "petugas ditunjuk" cukup digerbang `system_roles.hris` (admin/supervisor) atau perlu flag khusus dari server. ⚠️ **Usulan 2026-09-11**: [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] §9 mengusulkan satu modul izin untuk petugas lapangan OD & IR, dipakai bersama menu Satgas dan menu catatan kepatuhan ini, supaya siapa petugasnya tercatat di satu tempat. `system_roles` saja tidak cukup untuk gerbang per jabatan: MyBharata tidak menerima klaim izin, dan cache perannya meloloskan semua menu saat belum termuat. **Nama modulnya sudah dikunci: `kepatuhan`** (izin pertama `kepatuhan.satgas.input`, paket `kepatuhan_petugas_satgas`; merged 2026-09-11 lewat bip-erp PR [#1849](https://github.com/bip-itteam-internal/bip-erp/pull/1849), deploy belum diukur). Izin pencatat kepatuhan ringan sebaiknya menyusul ke modul yang sama, bukan modul kedua.
- Masa berlaku catatan sebelum "hangus" (analog `ExpiresAt` SP).
- Apakah kelak perlu jalur eksplisit "pelanggaran ringan berulang → usulan SP" (butuh ADR tersendiri; **tidak** otomatis).

## Perluasan: Inspeksi 5R Area per Department (ADR 0111, 🟡 diusulkan)

Track **ketiga** di payung Satgas/Industrial Relation, petugas yang sama (**Culture & Industrial**), tetapi objeknya **ruangan/area sebuah department**, bukan karyawan. Untuk **membedakannya** dari dua track lain:

| Track | Objek | KPI? | Sumber |
|---|---|---|---|
| Satgas per-PIC | Office Boy/Security (orang) | **Ya** (KPI individual) | [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] (redesign, 🟡) — menggantikan mekanisme [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] |
| Catatan Kepatuhan | Karyawan (atribut) | Tidak | [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] (dok ini di atas) |
| **5R Area** | **Ruangan department** | **Tidak** (catatan + peringatan SPV) | [[ADR - 0111 Inspeksi 5R Area per Department sebagai Catatan Non-KPI dengan Peringatan ke Supervisor]] |

- **Cara kerja (rencana)**: entitas baru `area_inspection` di employee-service (bukan `compliance_note` yang per-orang, bukan form-builder yang per-PIC/KPI). Petugas melihat **daftar department**, mengisi "Ada temuan?" + **≤15 foto** per department per periode bulanan. **Non-KPI**: tak menulis `kpi_score`/`employee_warning`/payroll.
- **Visibilitas dua-arah** (bukan tiga): petugas Culture & Industrial se-perusahaan + **supervisor department** ybs (`SupervisedDepartmentsStrict`). Tak ada "diri sendiri" karena objeknya ruangan.
- **Peringatan SPV** = rekap saat menu dibuka (irisan-1); push ditunda (kategori inbox baru = deploy 2 container + ADR).
- **Meminjam POLA** modul Catatan Kepatuhan (§Cara Kerja di atas): gerbang petugas server-side, resolusi supervisor, foto bukti, rekap per-department. **Bukan** memakai koleksinya.
- **Daftar task**: `Workspace/ANALISA - Inspeksi 5R Area per Department.md`.

## Perubahan: Redesign Satgas Per-PIC ke Input Bebas + SLA (ADR 0122, 🟡 diusulkan)

Track **Satgas per-PIC** (OB/Security, ber-KPI) **pindah dari Form Builder** ke **entitas sendiri `satgas_finding` di employee-service** — dianggap form-builder terlalu kaku (harus rakit form + periode + sasaran dulu). Objek & tujuan KPI **tidak berubah**; cara mencatat dan menilainya yang berubah. Keputusan & alasan: [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]].

- **Pencatatan bebas**: petugas Culture & Industrial (`kepatuhan.satgas.input`) mencatat temuan atas seorang OB/Security **kapan saja** (pilih orang + catatan + foto), tanpa form/periode/sasaran pra-bangun. `period_key` diturunkan dari tanggal catat.
- **SLA per temuan**: petugas menetapkan `sla_hari`. Lewat tenggat tanpa balasan, petugas memilih **`kunci_clockout`** (memakai ULANG mekanisme tahan-clock-out track Catatan Kepatuhan — `handleComplianceBlock` diperluas membaca `satgas_finding`, gerbang attendance yang sama) **atau** **`nilai_1`** (skor 1/10 terminal).
- **Balas-dengan-FOTO → approve = KONFIRMASI**: karyawan menanggapi temuan dengan foto bukti perbaikan (baru — balasan Catatan Kepatuhan hari ini text-only); petugas approve = **mengonfirmasi temuan sudah diperbaiki**, **tanpa mengetik nilai**.
- **KPI = skor OTOMATIS 0–100**: dihitung sistem `max(0, 100 − Σ potongan)`; **tanpa temuan = 100**; potongan/temuan **diperbaiki tepat waktu = 5**, **gagal ditanggapi = 15 + 5×(foto−1) maks 30**. Sumber `nilai_inspeksi_satgas` membaca `satgas_finding` **in-process** — melepas kopling HTTP `/internal/satgas/metrics` + `FORM_BUILDER_SERVICE_KEY`.
- **Non-sanksi**: kunci clock-out = nudge (bukan SP/potong gaji); temuan `tutup_gagal` menurunkan skor KPI (bukan potong gaji). PP tak mengatur 5R; ADR 0122 catatan penyimpangannya (ADR 0071 §4).
- **Pemisahan tetap**: `satgas_finding` (per-PIC, KPI) ≠ `compliance_note` (atribut, non-KPI) ≠ `area_inspection` (department, non-KPI) ≠ `employee_warning` (SP).
- **Daftar task**: `Workspace/ANALISA - Redesign Satgas Input Bebas dan SLA Temuan.md`.

## Dokumen Terkait

- [[ADR - 0111 Inspeksi 5R Area per Department sebagai Catatan Non-KPI dengan Peringatan ke Supervisor]] — track 5R area (di atas)
- [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] — redesign track per-PIC (menggantikan mekanisme 0090)
- [[ADR - 0090 Inspeksi Satgas 5R dan K3 di Form Builder dengan Nilai dari Cek Ulang Terakhir]] — track per-PIC ber-KPI (mekanisme lama, digantikan 0122)
- [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]] — keputusan & alasan (daftar task: `Workspace/ANALISA - Industrial Relation.md`)
- [[HRIS - Disciplinary (Surat Peringatan)]] · [[HRIS - Key Performance Index]] · [[HRIS - Conflict Management]]
- [[HRIS - Kepatuhan Peraturan Perusahaan]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]
- [[Microservices - Employee Service]] · [[Microservices - Calendar Service]] · [[ADR - 0084 Kehadiran Program Culture via Scan Menggantikan Feedback, plus Master Program]]

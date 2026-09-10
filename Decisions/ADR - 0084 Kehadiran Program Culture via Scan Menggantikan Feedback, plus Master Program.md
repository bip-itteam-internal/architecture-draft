## Untuk Manajemen

Program Culture kini punya **absensi nyata**. Dulu seseorang dianggap "hadir" hanya kalau ia mengisi survei — datang tapi belum menilai berarti tercatat tidak hadir, dan angka kehadiran di KPI **Culture & Industrial** jadi menghitung "yang menilai", bukan "yang datang". Setelah perubahan ini: peserta yang datang **men-scan QR kehadiran** yang ditampilkan di HP officer pembuat program (lewat aplikasi MyBharata) → tercatat hadir. Rating **dipisah**: setelah hadir, peserta terus diingatkan lewat pop-up di aplikasi sampai ia memberi rating, lalu pop-up berhenti. Program Culture juga hadir sebagai **menu di MyBharata** (sebelumnya hanya di web ERP), dan pembuatan program dipercepat lewat **master program** — officer tinggal memilih program dari daftar yang sudah disiapkan (nama + pilar + frekuensi pelaksanaan), form terisi otomatis.

**Terdampak**: officer HR Culture & Industrial (menampilkan QR, membuat program dari master), seluruh karyawan sebagai peserta (scan + rating di HP). **Yang TIDAK dijanjikan**: ini bukan mesin absensi berbasis lokasi/WiFi seperti clock-in — kehadiran program culture cukup dibuktikan scan token; QR dibuat berumur pendek supaya screenshot tak bisa disebar untuk "menitip hadir", tetapi sistem tidak memverifikasi lokasi fisik. Jenis program `club` dan `public` tetap di luar lingkup (menyusul, sesuai ADR 0066). **Besaran kerja**: sedang–besar, menyentuh tiga repo (backend form-builder, web ERP, aplikasi MyBharata); butuh deploy backend sebelum frontend.

## Deskripsi

*Mengganti definisi "hadir" Program Culture dari **jumlah pengisi feedback** ([[ADR - 0066 Modul Kelola Program Culture]] §Consequences: "bukti kehadiran fisik" sengaja tak diukur) menjadi **jumlah scan kehadiran** via token per-program yang berputar. Rating dipisah dari kehadiran: `partisipasi` KPI kini dari scan, `antusiasme` tetap dari rating, dan rating didorong lewat pop-up persisten di MyBharata (pola daftar-belum-dinilai server-driven). Menambah **master program** (nama + pilar + frekuensi pelaksanaan) yang mengisi form pembuatan program otomatis, dan membawa Program Culture ke **MyBharata** (officer menampilkan QR; peserta scan + menilai). Batas [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] tak berubah.*

- **Status**: 🟡 **Diusulkan**, disetujui pemilik produk 2026-09-09, kode belum ada. Artefak daftar task: `Workspace/ANALISA - Program Culture Scan Kehadiran & Master Program.md`.
- **Path di repo**: `bip-erp/services/form-builder/culture_attendance.go` (baru) · `culture_scan_token.go` (baru) · `master_culture_program.go` (baru) · `culture_metrics.go` (ubah: `partisipasi` dari scan) · `culture_programs.go`/`models_culture.go`/`routes.go`/`db.go` (ubah) · `bip-erp/services/employee/kpi_sumber_culture.go` (verifikasi kontrak) · `erp-frontend/src/app/(main)/hris/program-culture/kelola/*` + master program (baru) · `erp-frontend/src/features/form-builder/{types,hooks}/*culture*` (ubah) · `my-bharata/lib/src/features/program_culture/*` (baru)
- **Tanggal**: 2026-09-09

## Context

[[ADR - 0066 Modul Kelola Program Culture]] (⚠️ diterima 2026-08-31, kode di branch `feature/workspace-position`) sengaja memilih **"hadir" = jumlah peserta yang mengisi `culture_feedback`**, dan menyatakan terang di §Consequences bahwa identitas peserta datang dari header, **"bukan bukti kehadiran fisik … KPI mengukur kepuasan yang melapor, bukan absensi"**. Terkonfirmasi di kode: `bip-erp/services/form-builder/models_culture.go:50-52` ("Hadir = jumlah PESERTA yang sudah mengisi survei"), dan `partisipasi = responden ÷ target × 100` di `culture_metrics.go:73-77`.

Keputusan itu menjawab pertanyaan "seberapa puas yang melapor". Yang **tidak** dijawabnya, dan yang diminta pemilik proses (2026-09-09): **KPI Culture & Industrial harus mengukur siapa yang benar-benar HADIR**, dengan aturan *hadir ≥ target undangan* (lebih boleh; walk-in yang tak diundang tetap dihitung bila ikut scan). Menyamakan hadir dengan pengisi survei menghukum orang yang datang tapi belum sempat menilai, dan tak ada cara memisahkan "kehadiran rendah" dari "partisipasi survei rendah".

Grounding menemukan bahan reuse yang kuat, sehingga keputusan ini tak membangun dari nol:

- **Token scan berputar** sudah menjadi pola matang di attendance-service (alur Guestbook: `GET /guestbook/token` TTL 15 menit, `POST /guestbook/token-validate` — `services/attendance/main.go:2020-2042`). Ini acuan langsung "QR kehadiran program".
- **Kehadiran + rating di mobile** sudah ada end-to-end di fitur `training` MyBharata: `myTrainingAttendance(id)` menandai hadir, `myTrainingEvaluation(id)` mengirim rating, keduanya dengan status ditentukan server (`my-bharata/lib/src/core/api/url.dart:210-213`, `training_remote_datasource.dart:73-96`, `trainer_evaluation_sheet.dart`). Fitur ini template terdekat.
- **Pop-up rating persisten** sudah ada polanya: `PendingCsatBanner` + `PendingCsatCubit` — server mengembalikan daftar item-belum-dinilai, UI tampil selama list tak kosong, hilang otomatis setelah dinilai (`my-bharata/lib/src/features/task/presentation/widgets/pending_csat_banner.dart`, endpoint `taskPendingCsat`). Ini menggantikan kebutuhan menyimpan flag lokal.
- **Scanner kamera** sudah ada (`mobile_scanner`, acuan `inventory_scanner_page.dart`), dan **pola master data** sudah ada di employee-service (`services/employee/master_data.go:329-394`; Training punya `training_type` sebagai analog master program).

`BUSINESS_LOGIC_IMPLEMENTATION.md` (mybharata) **tidak memuat aturan Program Culture apa pun** (dikonfirmasi via git grep), jadi definisi "hadir" ini bebas dikunci di ADR ini tanpa bentrok dokumen-yang-menang.

## Decision

### 1. "Hadir" = scan kehadiran fisik, bukan pengisi feedback

Koleksi baru **`culture_attendance`** di form-builder: `{company_id, program_id, employee_id, scanned_at}`, index unik `(program_id, employee_id)` (satu orang satu kehadiran per program). "Hadir" sebuah program = jumlah dokumen `culture_attendance`-nya, menggantikan hitung-responden di `culture_metrics.go`. Feedback **tak lagi** menentukan kehadiran.

`partisipasi (30%) = hadir_scan ÷ target × 100`, tetap di-**clamp ke 100** (`clamp100` yang sudah ada) — sehingga walk-in yang membuat `hadir > target` tak menggelembungkan skor. `antusiasme (30%) = rata-rata rating ÷ 5 × 100` dan `implementasi (40%) = partisipasi × antusiasme ÷ 100` **tidak berubah** rumusnya; hanya sumber angka `hadir` yang bergeser. Bobot tetap hidup **hanya di backend** (`hitungSkorProgram`, satu fakta satu tempat) — tak disalin ke FE/sumber KPI.

### 2. QR kehadiran = token per-program, dibatasi JENDELA JAM program, di HP officer

Peserta yang datang **men-scan QR yang ditampilkan officer pembuat program di MyBharata-nya** (bukan QR statis publik, bukan peserta menampilkan QR sendiri). `GET /culture/programs/:id/scan-token` (hanya officer pemilik `created_by`) memberi token per-program; `POST /culture/attendance` memvalidasi token lalu mencatat kehadiran atas `employee_id` JWT pemindai **hanya bila waktu sekarang berada dalam `[jam_mulai, jam_selesai]` tanggal program** (WIB; jam kosong = seharian). Yang membatasi **bukan TTL token berputar melainkan jendela jam program** — keputusan pemilik produk 2026-09-09. ⚠️ Residual risk yang diterima sadar: screenshot QR masih bisa dipakai **selama jendela acara berlangsung** (bukan setelahnya); bila kelak perlu lebih ketat, token bisa dibuat berputar tanpa mengubah kontrak. Idempoten: satu peserta satu kehadiran per program (index unik).

### 3. Walk-in (di luar target) yang scan tetap dihitung hadir

Tak ada validasi bahwa `employee_id` pemindai termasuk `target_karyawan`/`target_departemen`. Sesuai aturan pemilik proses: yang tak diundang tapi datang & scan **tetap hadir**. Konsekuensinya `hadir` bisa > `target`; §1 sudah menutupnya dengan clamp 100. Ini melanjutkan sifat data ADR 0066 (`hadir` tak ditegakkan subset `target`), kini disengaja eksplisit.

### 4. Rating dipisah, didorong pop-up persisten sampai diberi

Setelah scan (hadir), peserta masuk daftar **"hadir tapi belum menilai"**. `GET /culture/feedback/pending` (identitas peserta dari JWT) mengembalikan program yang ia hadiri (`culture_attendance`) tapi belum ada `culture_feedback`-nya. MyBharata menampilkan pengingat rating (banner/dialog saat buka app) **selama daftar tak kosong**, mengikuti pola `PendingCsatCubit` — bukan flag lokal, bukan modal tak-berhenti; setelah `POST /culture/feedback` (yang sudah ada), item hilang dari daftar dan pengingat berhenti. **Jendela review = 1 hari** (keputusan 2026-09-09): program keluar dari `pending` setelah akhir hari BERIKUTNYA, jadi pengingat berhenti walau belum dinilai — mencegah nagging tak berujung untuk acara lama. `culture_feedback` tetap upsert unik `(program_id, respondent_id)`; hanya cara memunculkannya yang berubah (dari link web → daftar server di app).

### 5. Master program mengisi form pembuatan, tak menggantikan officer sebagai pembuat

Koleksi baru **`master_culture_programs`** di form-builder (`form_builder_db`): `{nama, pilar, pelaksanaan}` dengan `pelaksanaan ∈ {harian, mingguan, bulanan, tahunan}` (field frekuensi BARU, disalin ke dokumen program saat dibuat). Rute `GET/POST/PUT/DELETE /culture/master-programs`. **Siapa boleh mengelola** (keputusan 2026-09-09): officer **HR Culture & Industrial** lewat izin eksplisit `formbuilder.culture.manage` (paket dipasang HR ke jabatannya, pola kaizen-review), **plus SPV/Admin HR & IT** lewat `system_roles` (berbasis peran karena bukan satu jabatan tunggal). Saat officer membuat program, ia **memilih dari master** → `nama` + `pilar` + `pelaksanaan` disalin otomatis; `jenis`/`target`/`tanggal`/jam tetap diisi per pelaksanaan. **Nama bebas dihapus** — program WAJIB dari master (create menolak tanpa `master_id`).

### 6. Program Culture hadir di MyBharata: dua permukaan, clone pola `training`

- **Officer**: menu Program Culture → daftar programnya → "Tampilkan QR Kehadiran" (token berputar, mirip `MyQrWidget` untuk program).
- **Peserta**: scan QR officer (acuan `inventory_scanner_page.dart`) → tercatat hadir → pengingat rating (§4) → sheet rating bintang (acuan `trainer_evaluation_sheet.dart`, widget `star_rating.dart`).

Endpoint baru ditambахkan sebagai konstanta di `core/api/url.dart`; menu/rute/DI/l10n mengikuti pola fitur `training` (`names.dart`, `misc_pages.dart`, `misc_routes.dart`, `home_quick_access.dart`, `app_id.arb`+`app_en.arb`).

### 7. Kepemilikan kpi_score & metrik tak berubah

[[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] tetap: yang **menulis** `kpi_score` hanya employee-service; form-builder **melapor** lewat `GET /internal/culture/metrics` (menggerbang dirinya sendiri, [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Bentuk payload metrik tetap `{data{<emp>:{komposit[],jumlah}}}`; hanya angka `hadir` di dalam komposit yang kini dari scan. Wiring sumber+target tetap oleh HR lewat "Atur Target" ([[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]]). Koleksi baru mengikuti [[ADR - 0002 Database-per-Service]] (tetap di `form_builder_db`).

## Consequences

### Yang membaik

- KPI Culture & Industrial mengukur **kehadiran nyata**, bukan partisipasi survei — orang yang datang tapi belum menilai tak lagi terhitung absen.
- Rating & kehadiran terpisah bersih: dua angka yang berbeda arti tak lagi diturunkan dari satu peristiwa.
- Pengumpulan rating meningkat lewat pengingat persisten server-driven (tak bergantung peserta membuka link web).
- Pembuatan program lebih cepat & konsisten lewat master program; nama kembar berkurang.

### Yang memburuk atau tetap terbuka

- **Tidak ada skor KPI live yang bergeser & tak ada migrasi historis.** Modul Program Culture **belum dipakai di prod** (dinyatakan pemilik produk 2026-09-09; **T0 wajib mengukur ulang** — status prod adalah keadaan yang bergerak, jangan diasumsikan). Karena belum live, "hadir = pengisi feedback" tak pernah menjadi angka KPI produksi, jadi fitur ini lahir **langsung berbasis scan** — TANPA perlu strategi cutover/fallback maupun backfill data historis. Syarat satu-satunya: **fitur scan mendarat BERSAMA atau SEBELUM modul Program Culture debut di prod**, supaya definisi "hadir" tak sempat salah di prod walau sesaat. Data feedback yang sudah ada di DEV tidak mengikat. **BE sebelum FE** tetap berlaku (perubahan kontrak).
- **Kode modul dasar (ADR 0066) ada di `origin/main` bip-erp tetapi belum di-deploy prod** (deploy ≠ merge). Koordinasikan dengan pemilik `feature/workspace-position` agar scan + modul dasar naik ke prod sebagai satu paket.
- **Token TTL menuntut jam HP officer & peserta cukup selaras** dan officer harus menampilkan QR selama acara. Peserta di luar jangkauan app (tak bawa HP) perlu jalur cadangan manual — **di luar lingkup fase ini**, dicatat sebagai TBD.
- Endpoint `pending` + attendance menambah query per buka-app; ikuti TTL/memoisasi seperti sumber culture (30 dtk) bila perlu.

### Yang sengaja tidak dilakukan

- **Bukan clock-in berbasis lokasi/WiFi.** Kehadiran program culture cukup token scan; menyeret verifikasi lokasi attendance-service berlebihan dan menyeberang kepemilikan service.
- **Tidak menegakkan peserta ∈ target.** Walk-in dihitung (kebutuhan eksplisit); clamp 100 menahan dampak KPI.
- **`club`/`public` tetap ditunda** (sesuai ADR 0066); scan token per-program justru menjadi fondasi untuk `public` bertoken kelak.
- **Tidak menyalin bobot 30/30/40 atau definisi hadir ke FE/sumber KPI** — tetap satu tempat di `hitungSkorProgram`.

## Dokumen Terkait

- [[ADR - 0066 Modul Kelola Program Culture]] — keputusan "hadir = feedback" yang ADR ini amend
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]] · [[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]] · [[ADR - 0002 Database-per-Service]]
- [[Microservices - Form Builder Service]] — rumah kode modul culture + endpoint baru
- [[API - Form Builder Service]] — kontrak rute `/culture/*` (scan-token, attendance, feedback/pending)
- [[Microservices - Attendance Service]] — pola token berputar Guestbook yang diacu
- [[APP - MyBharata]] — dua permukaan mobile (officer QR, peserta scan+rating)
- [[HRIS - Matriks KPI per Departemen]] — metrik `Culture 2` yang sumber `hadir`-nya bergeser

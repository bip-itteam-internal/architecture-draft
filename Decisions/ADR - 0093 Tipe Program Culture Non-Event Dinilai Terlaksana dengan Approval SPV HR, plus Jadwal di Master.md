## Untuk Manajemen

Program Culture sekarang hanya mengenal satu bentuk: acara berkumpul yang butuh **daftar hadir** (scan QR) dan **rating peserta**. Padahal ada program budaya yang **bukan acara** — seperti **Kamis Batik** — yang tak punya daftar hadir sama sekali. Selama ini program semacam itu tak punya tempat di sistem: kalau dipaksa dibuat, nilainya jatuh ke **nol** dan justru **menyeret turun** KPI officer yang menjalankannya.

Perubahan ini menambah **tipe program "non-event"**. Untuk program non-event, officer cukup **menandai "terlaksana"** (mis. batik berjalan hari ini) — tanpa daftar hadir, tanpa rating. Supaya bukan sekadar mengaku sendiri, tiap tanda terlaksana **disetujui SPV HR** dulu sebelum ikut dihitung. Selain itu, **master program** bisa diisi **jadwal rutin** (mis. "setiap Kamis"), sehingga saat officer membuat program, tanggalnya **terisi otomatis** dan tak perlu diketik ulang — tetap bisa disesuaikan.

**Terdampak**: officer HR Culture & Industrial (membuat program non-event, menandai terlaksana), SPV HR (menyetujui). Peserta **tidak** bertambah bebannya. **Yang TIDAK dijanjikan**: **nilai KPI Culture dan bobotnya TIDAK diubah** — itu sudah diatur SK; yang berubah hanya *cara program non-event menghasilkan angkanya*. Ini juga **bukan** absensi berbasis lokasi, dan program non-event memang **tak punya** kehadiran maupun rating. **Besaran kerja**: sedang — backend form-builder + web ERP, plus sedikit penyesuaian aplikasi MyBharata agar program non-event tak muncul sebagai "bisa di-scan".

## Deskripsi

*Menambah field **`tipe` (event | non_event)** pada program culture dan master-nya. Program **non-event** (mis. Kamis Batik) **melewati** resolusi target, kehadiran (scan/QR), dan rating; skornya dihitung **"terlaksana-yang-disetujui SPV HR → 100, selain itu 0"** lalu masuk ke **array komposit yang sama** sehingga KPI officer tetap lahir dari pipeline sumber `program_culture` yang **tidak diubah** (struktur KPI diatur SK, bukan di ADR ini). Officer menandai terlaksana bebas kapan saja; **approval SPV HR** menahan self-report (alasan pola lama [[ADR - 0065 Template Form Generik untuk Realisasi Program (Culture)]] dibuang). Master program menyimpan **jadwal hari/tanggal berulang** yang mem-pra-isi tanggal saat program dibuat, berlaku untuk kedua tipe.*

- **Status**: 🟡 **Diusulkan** (2026-09-12). Kodenya belum ada. Meng-amend [[ADR - 0084 Kehadiran Program Culture via Scan Menggantikan Feedback, plus Master Program]] (yang meng-amend [[ADR - 0066 Modul Kelola Program Culture]]). Daftar task: `Workspace/ANALISA - Tipe Non-Event dan Jadwal Master Program Culture.md`.
- **Path di repo** (akan disentuh):
  - `bip-erp/services/form-builder/models_culture.go` (ubah: `tipe` di `CultureProgram` & `MasterCultureProgram`; struktur tanda terlaksana + status approval)
  - `bip-erp/services/form-builder/culture_terlaksana.go` (baru: tandai terlaksana + approval SPV HR)
  - `bip-erp/services/form-builder/culture_programs.go` (ubah: create bercabang — non-event lewati resolusi target)
  - `bip-erp/services/form-builder/culture_metrics.go` (ubah: `hitungSkorProgram` cabang non-event → 100/0)
  - `bip-erp/services/form-builder/master_culture_programs.go` (ubah: field jadwal hari/tanggal)
  - `bip-erp/services/form-builder/routes.go` (ubah: rute terlaksana + approval)
  - `bip-erp/services/employee/kpi_sumber_culture.go` (verifikasi kontrak metrik TAK berubah — read-only)
  - `erp-frontend/src/features/form-builder/types/culture.ts` + `hooks/use-culture.ts` (ubah)
  - `erp-frontend/src/app/(main)/hris/program-culture/{kelola,master,[id],page}.tsx` (ubah)
  - `my-bharata/lib/src/features/program_culture/*` (ubah: guard non-event tak tampil scan/QR/rating)
- **Tanggal**: 2026-09-12

## Context

[[ADR - 0066 Modul Kelola Program Culture]] dan [[ADR - 0084 Kehadiran Program Culture via Scan Menggantikan Feedback, plus Master Program]] membangun modul culture **sepenuhnya event-centric**: tiap program di-resolve **target diundang**-nya, "hadir" diukur dari **scan kehadiran** dalam jendela jam program, kepuasan dari **rating peserta**, lalu skor komposit **30/30/40** (`culture_metrics.go` `hitungSkorProgram`). KPI officer Culture & Industrial = **rata-rata aritmetika** skor komposit seluruh programnya pada periode (reduksi `rata_rata` di `kpi_sumber_culture.go`).

Model ini tak punya tempat untuk program budaya yang **bukan acara**. Pemilik proses (2026-09-12) menyebut contoh **Kamis Batik**: program culture nyata, tapi **tak perlu daftar kehadiran** dan tak ada peserta yang "diundang" lalu di-scan. Terkonfirmasi di kode (grounding, `git grep`): **tidak ada** field tipe program (event/non-event), **tidak ada** jalur "officer tandai terlaksana", dan program tanpa kehadiran+rating menghasilkan komposit **0** yang **tidak dilewati** — ia masuk array dan **menyeret turun** rata-rata KPI officer (`culture_metrics_test.go` mengunci perilaku 0 ini). Artinya menjalankan program budaya non-event justru **menghukum** officer.

Dua batas mengunci ruang solusi:

1. **KPI diatur SK, tak boleh didesain ulang di sini.** Struktur sumber `program_culture`, reduksi `rata_rata`, target 100, arah naik — semuanya tetap. Solusi harus **menyesuaikan yang ada**, bukan menambah metrik/sumber KPI baru.
2. **Self-report adalah alasan pola lama dibuang.** [[ADR - 0065 Template Form Generik untuk Realisasi Program (Culture)]] memakai radio `terlaksana_sesuai_jadwal` yang diisi officer sendiri, ditinggalkan justru karena self-report. Non-event **tak punya** kehadiran sebagai bukti objektif, jadi "terlaksana" mau tak mau berasal dari officer — dan itu harus **ditahan gerbang lain**.

Grounding juga menemukan modul culture **sudah lebih matang dari status di index**: kode ada di web ERP dan **fitur Program Culture sudah dibangun penuh & ter-commit di MyBharata** (QR officer, scan PIC, rating, pengingat). Status 🟡 di beberapa dok vault **basi** — build MyBharata berikutnya sudah membawa culture ke user. Konsekuensi deploy nyata, bukan hipotetis.

Kebutuhan sekunder yang menyertai (permintaan asli pemilik proses): **jadwal berulang per klub**. Master program (ADR 0084) baru menyimpan `pelaksanaan` (kata frekuensi: harian/mingguan/bulanan/tahunan), **belum** hari/tanggal konkret, sehingga tanggal tetap diketik manual tiap membuat program. Jadwal klub berulang sudah terdokumentasi di [[HRIS - Pengembangan Organisasi (Community of Interest)]] tapi masih **konstanta FE tanpa backend**, tak tertaut master.

## Decision

### 1. Field `tipe` (event | non_event) pada program & master

`CultureProgram` dan `MasterCultureProgram` mendapat `tipe` dengan default **`event`** (kompatibel mundur: program & master lama tetap event tanpa migrasi nilai). `tipe` disalin dari master ke program saat dibuat, sejajar `nama`/`pilar`/`pelaksanaan`. `tipe` adalah sumbu **berbeda** dari `jenis` (yang semata cara resolve target undangan) dan `pelaksanaan` (frekuensi) — jangan disatukan.

### 2. Non-event melewati kehadiran, target, dan rating

Untuk `tipe=non_event`: create program **tidak** memanggil resolusi target (`resolveTargetProgram`), **tidak** membuat `scan_token`, dan **tidak** menerima kehadiran (scan/manual) maupun feedback. `tanggal` menjadi **opsional** (non-event bisa "bebas kapan saja"). UI kehadiran/rating disembunyikan untuk tipe ini. Bobot 30/30/40 dan seluruh jalur event **tidak berubah**.

### 3. Skor non-event = terlaksana-disetujui → 100, else 0, di array komposit yang SAMA

`hitungSkorProgram` bercabang atas `tipe`:

- **event** — komposit 30/30/40 seperti sekarang (tak berubah).
- **non_event** — komposit = **100** bila program punya ≥1 tanda terlaksana **yang disetujui SPV HR** dalam `period_key`, selain itu **0**.

Nilai ini masuk **array `komposit[]` yang sama** yang dilaporkan `GET /internal/culture/metrics`, sehingga **struktur sumber KPI `program_culture`, reduksi `rata_rata`, target, dan arah TIDAK diubah** (batas SK). Yang berubah hanya *cara satu program menghitung angka kompositnya* di dalam form-builder. Bobot & definisi tetap **satu tempat** di backend (`hitungSkorProgram`), tak disalin ke FE/sumber KPI.

### 4. Officer menandai terlaksana; SPV HR menyetujui; hanya yang disetujui berhitung

Officer menandai pelaksanaan program non-event **bebas kapan saja** (boleh >1× per periode), opsional dengan catatan/bukti. Tiap tanda berstatus **menunggu approval**; **SPV HR** menyetujui atau menolak. Hanya tanda **disetujui** yang membuat program "terlaksana" di periodenya (§3). Resolusi "SPV HR" mengikuti gerbang yang sudah ada `requireCultureManager` (SPV/Admin HR & IT via `system_roles`) — approver **bukan** atasan `work_data` officer, melainkan peran HR, supaya tak bergantung struktur atasan per-orang. Pola approval + notifikasi mengikuti mekanisme pengajuan yang sudah ada; **jangan** menulis resolver baru.

### 5. Master menyimpan jadwal hari/tanggal → pra-isi form (kedua tipe)

`MasterCultureProgram` mendapat field jadwal yang **artinya bergantung `pelaksanaan`**: `mingguan` → hari-dalam-minggu; `bulanan` → tanggal-dalam-bulan; `harian` → tiap hari kerja; `tahunan` → tanggal spesifik. Saat officer memilih master di form buat program, jadwal ini **mem-pra-isi** `tanggal` (dan jam bila ada) — **tetap bisa disesuaikan** sebelum simpan. Jadwal adalah **acuan/template**, bukan generator: tak ada cron, tak ada sesi yang dibangkitkan otomatis. Untuk event ini menghapus ketik-ulang tanggal rutin; untuk non-event jadi dasar pengingat "sudah terlaksana belum".

### 6. Anti-gaming dua lapis

Skor non-event rawan diangkat sendiri. Ditahan dua lapis yang **sudah** jadi keputusan: (a) program **wajib dari master** milik HR (`requireCultureManager`, ADR 0084 §5) — set program bukan bebas dikarang officer; (b) tiap terlaksana **disetujui SPV HR** (§4). Keduanya bersama membuat "100" non-event bukan self-grade murni.

### 7. Kepemilikan kpi_score & bentuk metrik tak berubah

[[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] tetap: yang **menulis** `kpi_score` hanya employee-service; form-builder **melapor** lewat `GET /internal/culture/metrics` dengan bentuk payload **tetap** `{data{<emp>:{komposit[],jumlah}}}`. Wiring target tetap oleh HR lewat "Atur Target" ([[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]]).

## Consequences

### Yang membaik

- Program budaya non-event (Kamis Batik dsb.) punya tempat; officer **tak lagi dihukum** nol karena menjalankannya.
- KPI officer tetap lahir dari **pipeline & SK yang sama** — tak ada sumber/metrik KPI baru yang harus disetujui ulang.
- Self-report non-event ditekan **approval SPV HR** + program hanya-dari-master, menjawab persis alasan ADR 0065 dibuang.
- Jadwal di master menghapus ketik-ulang tanggal rutin dan menautkan jadwal klub yang selama ini cuma konstanta FE.

### Yang memburuk atau diterima sadar

- **Non-event menyumbang 100 biner ke rata-rata bergradasi.** Sekali disetujui, program non-event selalu menyumbang 100 ke rata-rata komposit officer, bisa **mengangkat** rata-rata. Diterima: "terlaksana" memang sukses biner, dan dua lapis anti-gaming menahannya. **Bukan** kelas "kolom beda arti dijumlahkan" karena keduanya memang skala 0–100 yang di-rata-rata, bukan dijumlah — tetapi maknanya kasar dan itu **wajib dinyatakan** ke HR saat menyetel harapan.
- **Approval menambah langkah & ketergantungan SPV HR merespons.** Bila SPV lambat, nilai non-event periode itu tertunda (0 sampai disetujui) — sifat yang sama dengan approval pengajuan lain. Perlu pengingat ke SPV.
- **MyBharata sudah punya culture.** Program non-event **tak** punya scan/QR/rating; app perlu **guard** agar non-event tak muncul sebagai bisa-di-scan atau menagih rating. Tanpa guard, non-event bocor sebagai event yang mustahil di-scan.
- **Deploy**: **BE sebelum FE** (kontrak berubah: `tipe`, endpoint terlaksana/approval). Bila approval memakai **kategori inbox baru** → notification-service + form-builder **naik bersama** (dua container). Modul culture harus **debut prod satu paket** (ADR 0084).
- **Status prod belum diukur sesi ini** (tak ada akses tulis; baca pun tak dilakukan). ADR 0084 menyatakan modul belum prod — **ukur ulang (T0)** sebelum eksekusi; jangan diasumsikan.

### Yang sengaja tidak dilakukan

- **Tidak** membuat sumber/metrik KPI kedua (batas SK) — non-event memakai pipeline `program_culture` yang ada.
- **Tidak** mengubah bobot 30/30/40 atau jalur skor event.
- **Tidak** membangkitkan sesi otomatis (cron) dari jadwal master — jadwal hanya acuan pra-isi (keputusan pemilik proses).
- **Tidak** menyalin `tipe`/bobot/definisi terlaksana ke FE atau sumber KPI — tetap satu tempat di `hitungSkorProgram`.

## Dokumen Terkait

- [[ADR - 0084 Kehadiran Program Culture via Scan Menggantikan Feedback, plus Master Program]] — ADR yang di-amend (master program + definisi hadir)
- [[ADR - 0066 Modul Kelola Program Culture]] — modul + komposit 30/30/40
- [[ADR - 0065 Template Form Generik untuk Realisasi Program (Culture)]] — pola self-report lama yang dibuang
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]]
- [[Microservices - Form Builder Service]] — rumah kode modul culture + endpoint metrik
- [[Microservices - Employee Service]] — pemilik sumber KPI `program_culture`
- [[HRIS - Pengembangan Organisasi (Community of Interest)]] — jadwal klub berulang (konstanta FE) yang ditautkan ke master
- [[APP - MyBharata]] — permukaan mobile culture yang butuh guard non-event

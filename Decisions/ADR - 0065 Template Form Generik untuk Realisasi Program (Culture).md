## Deskripsi

*Membangun **template form generik** (koleksi `form_templates` + CRUD + UI + instantiate) di [[Microservices - Form Builder Service]] untuk SATU pemakai nyata: jabatan **Culture & Industrial** yang harus melapor rencana & realisasi program culture tiap bulan. Form realisasi itu lalu menjadi sumber KPI baru `program_culture` yang mengukur "persentase terlaksananya program culture yang sesuai jadwal". Tiga keputusan dicatat di sini: (1) mengangkat abstraksi "template" untuk satu pemakai, menyimpang sadar dari prinsip tim; (2) menandai form culture lewat `template_id`, bukan `metric_key`; (3) `form_type: survey`, bukan `report`.*

- **Status**: 🔴 **Superseded oleh [[ADR - 0066 Modul Kelola Program Culture]]** (2026-08-31). Diterima 2026-08-30 lalu diganti **sebelum merge**: Culture pindah ke **modul sendiri** (`culture_programs` + feedback peserta), bukan mengisi form, jadi keputusan (2) `template_id`-sebagai-penanda dan (3) `form_type: survey` **tak lagi berlaku**, dan `seed_culture.go` dihapus. Keputusan (1) — koleksi generik `form_templates` — **tetap ada di kode** sebagai kapabilitas, kini **tanpa konsumen**. Konteks & alasan pivot: ADR 0066.
- **Path di repo**: `bip-erp/services/form-builder/models_template.go` · `template_handlers.go` · `seed_culture.go` · `culture_metrics.go` · `bip-erp/services/employee/kpi_sumber_culture.go` · `erp-frontend/src/app/(main)/form-builder/templates/` · `src/features/hris/kpi/lib/label-otomatis.ts`
- **Tanggal**: 2026-08-30

## Context

Jabatan **Culture & Industrial** (posisi tunggal, departemen Human Resource) dinilai KPI-nya antara lain lewat metrik "Persentase terlaksananya program culture yang sesuai jadwal" — di [[HRIS - Matriks KPI per Departemen]] tercatat sebagai `Culture 2` pada template `Organizational Development`, dan selama berbulan-bulan berstatus **"belum dipetakan"**: tak ada data di sistem yang menjawabnya, jadi angkanya diketik manual.

Bahannya sebenarnya ada di kepala orangnya: tiap bulan ia menyusun beberapa program culture (rencana + target), menjalankannya, lalu mencatat realisasinya di sebuah xlsx berseksi (metadata, rancangan/target, before/after, root-cause/CAPA, anggaran, lampiran). Yang hilang cuma **tempat terstruktur** untuk mengisinya, sehingga "sesuai jadwal atau tidak" bisa dihitung mesin alih-alih dinilai kira-kira.

Form Builder sudah bisa menampung form berseksi, berulang bulanan, dan melapor metriknya ke KPI (pola `kaizen`). Pertanyaannya bukan "bisakah dibuat", melainkan **seberapa banyak permukaan** yang dibangun untuk satu jabatan.

Dua opsi ditimbang bersama pemilik produk:

| Opsi | Yang dibangun | Ongkos |
|---|---|---|
| **Seed form saja** (ringan) | Satu form culture di-seed saat boot, tanpa koleksi/CRUD/UI baru | Murah, tapi form realisasi jabatan lain kelak menuntut seed baru + rilis kode tiap kali |
| **Template generik** (dipilih) | Koleksi `form_templates` + CRUD + UI kelola + `instantiate` | Permukaan jauh lebih luas untuk satu pemakai, tapi jabatan berikutnya tinggal seed/isi template |

Prinsip tim (`team-memory.md`, §"SATU FAKTA SATU TEMPAT") melarang **generalisasi demi pemakai yang belum ada** — "tunggu pemakai ketiga sebelum mengangkat abstraksi". Template generik jelas melanggarnya: hari ini pemakainya **satu**.

## Decision

### 1. Bangun template generik, menyimpang sadar dari prinsip "jangan generalisasi"

Pemilik produk memilih **template generik** setelah diberi opsi ringan secara eksplisit. Alasannya bukan menebak pemakai kedua, melainkan bentuk kerja HR: form realisasi program adalah pola yang akan **berulang per jabatan/program**, dan jalur "seed + rilis kode tiap form" memindahkan pekerjaan berulang itu ke dev selamanya. Trade-off diterima terbuka: **permukaan lebih luas sekarang** (koleksi + CRUD + UI) ditukar dengan **form realisasi jabatan berikutnya cukup di-seed/isi dari template**, tanpa rilis kode.

- **Template = cetakan reusable; TIDAK menerima jawaban.** `POST /form-templates/:id/instantiate` menyalin `fields` + `form_type` + `default_recurrence` ke sebuah `Form` baru berstatus `draft`; jawaban tetap masuk ke `Form`/`form_responses` seperti biasa. Field **disalin, bukan dirujuk**, supaya menyunting template tak mengubah arti jawaban form yang sudah terbit.
- Penyimpangan dicatat di sini justru **karena** ia melanggar prinsip: siapa pun yang kelak menemukan koleksi `form_templates` dipakai satu jabatan tak perlu menebak apakah itu over-engineering yang lolos gerbang atau keputusan sadar.

### 2. Identifikasi form culture lewat `template_id`, BUKAN `metric_key`

Form yang menjadi sumber `program_culture` ditemukan dari **`Form.template_id`** yang menunjuk template culture, bukan lewat `metric_key`.

`metric_key` (dipakai indeks layanan departemen, [[API - Form Builder Service]]) membawa **mesin validasi ber-guard berat**: nilai wajib dikenal, wajib `form_type: survey`, wajib `recurrence` bulanan, plus indeks unik parsial "satu form terbit per (perusahaan, departemen, penanda)". Culture tak butuh keunikan-per-departemen itu dan tak ingin menumpang guard yang dirancang untuk kebutuhan lain — menumpangkannya berarti dua fitur berbagi satu jalur validasi yang akan menyimpang begitu salah satunya disentuh. `template_id` sudah ada sebagai penjejak asal instantiate, jadi memakainya untuk mengenali form culture tak menambah sumbu penanda baru.

### 3. `form_type: survey`, BUKAN `report`

Form culture memakai `survey`. `report` (rencana tipe terpisah) memikul **kewajiban field file + workflow approval** yang tak diinginkan di sini: realisasi culture dilaporkan mandiri lalu dibaca sebagai angka KPI, bukan diajukan untuk disetujui. Memilih `survey` menghindari kedua beban itu; seksi before/after dan lampiran cukup jadi field biasa (termasuk satu field `file` opsional) di dalam form `survey`.

## Consequences

**Yang membaik.** Metrik `Culture 2` berpindah dari "belum dipetakan" (diketik manual, tak terverifikasi) ke **sumber `program_culture`** yang menghitung % program terlaksana sesuai jadwal dari jawaban form. Jabatan/program berikutnya yang butuh form realisasi tinggal membuat template lewat UI, tanpa rilis kode.

**Yang memburuk / diterima sadar.**
- **Permukaan bertambah** untuk satu pemakai: koleksi `form_templates`, lima rute CRUD + `instantiate`, halaman kelola template, dan pintu masuk tombol di toolbar Form Builder. Beban perawatannya jatuh ke seluruh Form Builder, manfaatnya (hari ini) ke satu jabatan.
- **Pemakai kedua belum tentu memvalidasi bentuknya.** Sesuai peringatan `team-memory.md`, template pemakai berikutnya bisa datang dengan kebutuhan yang tak terduga; abstraksi ini **belum** teruji pada pemakai kedua, dan itu risiko yang melekat pada keputusan menyimpang ini.

**Yang tetap.** Batas [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] tak berubah: yang **menulis** `kpi_score` tetap employee-service; form-builder hanya **melapor** angka lewat `GET /internal/culture/metrics`, yang menggerbang dirinya sendiri ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Wiring sumber + target ke template dikerjakan HR lewat "Atur Target" ([[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]]), bukan hardcode: formula `rata_rata`, target 100, arah naik pada template aktif `HR Organizational Development` (posisi Culture & Industrial); template lama `Organizational Development` diarsipkan.

## Dokumen Terkait

- [[Microservices - Form Builder Service]] — rumah kode template generik + seed culture + endpoint metrik
- [[API - Form Builder Service]] — kontrak rute `/form-templates/*` dan `/internal/culture/metrics`
- [[HRIS - Otomasi Skor KPI]] — kerangka otomasi tempat sumber `program_culture` terdaftar
- [[HRIS - Matriks KPI per Departemen]] — metrik `Culture 2` yang kini terpetakan
- [[REF - Penamaan Metrik & Sumber KPI]] — penamaan sumber `program_culture` + key label FE
- [[Microservices - Employee Service]] — pemilik katalog sumber KPI (`kpi_sumber_culture.go`)
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0053 Struktur dan Target KPI Disatukan di Satu Halaman]] · [[ADR - 0031 Prefix internal Bukan Batas Keamanan]]

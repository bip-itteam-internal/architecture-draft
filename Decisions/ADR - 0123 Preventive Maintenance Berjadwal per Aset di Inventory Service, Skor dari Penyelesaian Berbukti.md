> **Status**: 🟡 **Diusulkan** (2026-09-24) — kode belum ada. Mengikuti **cetakan arsitektur** [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] (entitas sendiri per subjek, bukan form-builder; approve sebagai **konfirmasi** dan skor **dihitung sistem**, bukan diketik), tetapi **sengaja berbeda pada model skornya** — lihat Decision §5. Tidak menyentuh [[ADR - 0111 Inspeksi 5R Area per Department sebagai Catatan Non-KPI dengan Peringatan ke Supervisor]], [[ADR - 0085 Industrial Relation Catatan Kepatuhan Ringan Terpisah dari SP dan KPI]], maupun [[ADR - 0112 Ronda Security di Attendance Service, GPS Membuktikan Lokasi Bukan Titik]].

## Untuk Manajemen

Perawatan berkala gedung dan alat (servis AC, cek panel, genset) sekarang dinilai dengan **angka yang diketik penilai**, karena sistem tidak punya daftar perawatan yang seharusnya dikerjakan. Tidak ada pembanding, jadi tidak ada yang bisa dihitung. Di bulan Agustus metrik ini bernilai **100** padahal tidak ada satu pun catatan yang bisa membuktikannya.

**Apa yang berubah di layar:** GA menyusun **daftar perawatan berkala per aset** beserta frekuensinya, sekali di awal. Tiap bulan sistem menampilkan sendiri mana yang jatuh tempo. Teknisi menandai selesai sambil **mengunggah foto sebelum dan sesudah**. Atasan tidak memberi nilai, melainkan **menolak bukti yang tidak sah**. Nilai KPI-nya kemudian **dihitung**, bukan ditaksir: perawatan berbukti dibagi perawatan yang jatuh tempo.

**Siapa yang terdampak:** teknisi Building Maintenance dan GA Staff (menandai selesai + foto), SPV GA (memverifikasi bukti), dan GA yang menyusun daftar perawatan di awal.

**Apa yang TIDAK dijanjikan:** bobot, target, dan arah metrik **tidak diubah** — itu diatur SK, bukan keputusan ini. Ini **bukan** sistem sanksi dan tidak menyentuh gaji. Ia juga **tidak** menggantikan pencatatan perbaikan kerusakan, yang sudah berjalan lewat tiket dan sudah dinilai terpisah. Dan ia **tidak** menjawab patroli Security tiap 3 jam, yang bentuknya berbeda dan sudah punya keputusan sendiri.

**Perkiraan besaran kerja:** sedang. Dua penyimpanan baru dan satu layar, ditambah satu sambungan ke KPI. Sebagian bahannya sudah ada: daftar aset, unggah foto, dan pola "atasan mengonfirmasi, angkanya dihitung sistem" yang sedang dibangun untuk Satgas. Backend rilis lebih dulu, lalu web.

## Deskripsi

*Metrik `Realisasi Preventif Maintenance Building & Fasilitas` (bobot 0,30) dan `Persentase SLA Preventife Maintenance Alat Operational Tepat Waktu` (bobot 0,25) mendapat sumber data nyata lewat **dua koleksi baru di inventory-service**: `pm_jadwal` (rencana perawatan per aset + frekuensi, menjadi **penyebut**) dan `pm_realisasi` (penyelesaian + foto bukti + verifikasi, menjadi **pembilang**). Subjeknya **aset**, karena itu ia tinggal bersama `inventory` dan `repair_history`, bukan di employee-service (subjek orang) dan bukan di form-builder (mesin periodik yang justru sedang ditinggalkan). Skornya **berbasis penyelesaian**, bukan pengecualian: tanpa bukti bernilai nol, bukan seratus.*

- **Status**: 🟡 **Diusulkan** — kode belum ada. Daftar task: `Workspace/ANALISA - Preventive Maintenance Berjadwal per Aset.md`
- **Path di repo** (yang **akan** disentuh):
  - bip-erp: `services/inventory/models_pm.go` (baru) · `services/inventory/pm_jadwal.go` (baru: CRUD jadwal + penurunan jatuh tempo) · `services/inventory/pm_realisasi.go` (baru: tandai selesai, unggah foto, verifikasi) · `services/inventory/pm_metrik.go` (baru: `GET /internal/pm-metrik`) · `services/inventory/main.go` (revisi: pendaftaran rute, mengikuti `gateGa` yang sudah dipakai `/perlengkapan-opname`) · `services/employee/kpi_sumber_pemeliharaan_preventif.go` (baru: sumber KPI, memetakan payload jadi `Cuplikan`, **tidak menghitung ulang**)
  - erp-frontend: `src/app/(main)/ga/preventive-maintenance/page.tsx` (baru) · `src/features/ga/preventive-maintenance/*` (baru) · reuse pola unggah multi-foto dan sheet isian dari track Inspeksi Area
- **Tanggal**: 2026-09-24

## Context

Diukur ke `origin/main` `bip-erp` `7b767ec9` dan ke **database produksi**, 2026-09-24. Klaim negatif diverifikasi dengan `git grep` berkontrol positif.

1. **Metriknya tidak punya definisi di sistem, hanya target.** Di `kpi_template` prod (119 dokumen), metrik ini berisi `label` = "Realisasi Preventif Maintenance Building & Fasilitas" dan `description` = "Target 100%". Tidak ada daftar pekerjaan, tidak ada jadwal, tidak ada aturan hitung. Pada generasi template sebelumnya susunannya terbalik (label generik, deskripsi berisi kalimat ini), jadi definisinya memang **tidak pernah ada**, bukan hilang saat migrasi.

2. ⛔ **Angkanya sudah dipakai menilai orang tanpa dasar apa pun.** Periode 2026-08, template `Building and Maintenance Staff` (posisi `Building Maintenance`, satu karyawan) bernilai total **93**, dengan metrik preventif ini bernilai **100** — padahal tidak ada catatan apa pun yang bisa menghasilkan angka itu. Ini bukan metrik kosong yang terlihat kosong; ia metrik kosong yang **terlihat bekerja**.

3. **Tidak ada penyimpanan jadwal perawatan di service mana pun.** `preventive_maintenance`, `maintenance_schedule`, `anggaran_maintenance`, dan `realisasi_biaya` seluruhnya **nol** di `services/` (kontrol positif: `repair_history` = 1 berkas, `services/inventory/controller.go`). Tanpa penyebut, rasio "realisasi" tak bisa dihitung bahkan secara prinsip.

4. **Aset dan riwayat perbaikannya sudah ada, dan sudah di satu tempat.** `inventory_db` prod: `inventory` **899** dokumen, `repair_history` **9** (sudah berkomponen biaya), `ga_opname` **4**, `category` 40, `data_master` 144. Opname perlengkapan sudah punya rute dan ADR sendiri ([[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]]). Menaruh jadwal perawatan di tempat lain akan memecah riwayat satu aset ke dua service.

5. ⛔ **Form-builder bukan pilihan, dan alasannya bukan recurrence.** Mesin periodenya memang hanya mengenal `monthly` dan `weekly` (`services/form-builder/models_period.go:13-14`), dan untuk PM gedung itu sebenarnya cukup. Yang tidak bisa dilakukannya adalah **jadwal berbeda per aset** dan **riwayat per aset** — satu form adalah satu kuesioner datar per periode. Ditambah lagi [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] justru memindahkan Satgas **keluar** dari form-builder karena kekakuan yang sama, dan me-*retire* `metric_key: inspeksi_satgas` secara bertahap. Membangun ketergantungan baru di atasnya berarti membangun di atas fondasi yang sedang ditinggalkan.

6. **`ceklis_kpi` juga tidak muat.** Ia menautkan **satu** metrik ke **satu** butir lewat UID butir dan bersifat sudah/belum (`services/employee/kpi_sumber_ceklis.go:33`, jendela penilaian sampai tanggal 5, scope individu). Rasio atas banyak aset bukan bentuk yang dilayaninya.

7. **Satgas tidak bisa dipakai ulang, walau namanya mirip.** Modelnya berporos pada **orang yang dinilai**: nilai satu orang satu periode diambil dari kiriman **terakhir** atasnya, dengan normalisasi skala (`services/form-builder/satgas_nilai.go`). PM berporos pada **aset dan jadwalnya**. Menyatukan keduanya membengkokkan mekanisme yang sudah benar untuk keperluannya sendiri.

8. ⛔ **Pola yang berulang, dan ini pertimbangan terpenting.** Tiga mekanisme di lingkup ini sudah dibangun lalu tidak pernah terisi: modul Training lengkap dengan `quiz_attempt` **0** di prod; sumber `nilai_inspeksi_satgas` lengkap tetapi **nol form Satgas** dari 20 form yang ada di `form_builder_db`; dan form "Checklist Pekerjaan Office Boy (OB)" yang berisi **1 jawaban** lalu ditutup. Sebaliknya yang hidup justru yang **pengisinya bukan orang yang dinilai**: "Pelayanan Tim Security" **1.357** jawaban dan "Pelayanan Tim Office Boy" **694** jawaban, keduanya masih terisi sampai 2026-09. Keputusan ini karena itu menempatkan pengisian pada **teknisi yang memang sedang bekerja** (bukan pekerjaan administratif tambahan) dan verifikasi pada **orang lain**.

9. **Pekerjaan nyatanya hari ini tercatat di luar ERP.** Pemilik proses menunjukkan dokumen Google "Realisasi Pekerjaan Teknisi Building" dengan tab per bulan sejak Desember 2025, berisi tanggal, keterangan pekerjaan, lokasi, dan foto sebelum/sesudah, plus dokumen kedua "Checklist Jumlah Aset yang di-maintenance" (belum diperiksa isinya). Sementara itu space tiket `Building Maintenance` hanya berisi **9 tiket** Juni-September, 6 masih Todo, sebagian bukan pekerjaan gedung ([[GA - Building Maintenance]]). Artinya sistem yang tidak menggantikan dokumen itu hanya menambah tempat keempat untuk mengetik.

10. **Gerbang aturan bisnis: lolos.** `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` (menang atas perilaku sistem) **tidak menyebut KPI sama sekali**, dan Peraturan Perusahaan tidak mengatur perawatan berkala. Jadi tidak ada aturan yang dilanggar. Struktur dan bobot KPI sendiri diatur **SK**, sehingga keputusan ini hanya boleh mengubah **cara angkanya lahir**.

11. **Berdiri sebagian di atas rencana, bukan kenyataan.** [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] berstatus 🟡 dan kodenya belum ada, jadi pola "atasan mengonfirmasi, sistem menghitung" yang dipakai ulang di sini masih rancangan. ⚠️ ADR itu juga **direvisi pada hari yang sama** (skornya semula diketik petugas 1–10, kini otomatis dari potongan); rujukan di sini mengikuti versi 2026-09-24 dan perlu diperiksa ulang bila ia berubah lagi. [[GA - Checklist Management]] dan [[GA - Building Maintenance]] juga 🟡. Yang **nyata** dan sudah berjalan: metrik 0,35 di template yang sama sudah otomatis lewat sumber `kinerja_tiket` metrik `selesai_dinilai` dan benar-benar menghasilkan angka.

## Decision

### 1. Dua koleksi di inventory-service, subjek ASET

`pm_jadwal`: `(company_id, asset_id, pekerjaan, frekuensi, mulai_berlaku, aktif, dibuat_oleh, dibuat_pada)`. Satu dokumen = satu pekerjaan berkala atas satu aset. `asset_id` **merujuk** `inventory`, tidak menyalin daftar asetnya.

`pm_realisasi`: `(company_id, jadwal_id, period_key, tanggal_selesai, pelaksana, foto_sebelum[], foto_sesudah[], catatan, status, diverifikasi_oleh, diverifikasi_pada, alasan_tolak)`.

Ditaruh di inventory-service karena **subjeknya aset**, sejajar dengan `repair_history` dan `ga_opname`. Ini sekaligus menjawab pertanyaan yang selama ini menggantung di [[GA - Building Maintenance]] tentang di mana riwayat pemeliharaan aset tinggal: **riwayat satu aset ada di satu service**, perbaikan dan perawatan berkala bersebelahan.

### 2. Penyebut lahir dari jadwal, bukan dari isian

Jatuh tempo satu periode **diturunkan** dari `pm_jadwal` (frekuensi + `mulai_berlaku`), bukan diketik dan bukan dipilih saat pengisian. Inilah yang membuat angkanya tak bisa dikarang: menyusutkan penyebut menuntut menyunting jadwal, dan suntingan itu berjejak.

⚠️ Frekuensi yang didukung ditetapkan eksplisit (bulanan, triwulan, semesteran, tahunan). **Sub-harian tidak didukung** dan memang bukan lingkup ini; patroli tiap 3 jam adalah bentuk lain yang sudah punya keputusan sendiri di [[ADR - 0112 Ronda Security di Attendance Service, GPS Membuktikan Lokasi Bukan Titik]].

### 3. Bukti WAJIB per realisasi

Satu realisasi tidak sah tanpa foto. Tanpa kewajiban ini, "menandai selesai" kembali menjadi swa-nilai dengan baju baru, dan seluruh nilai keputusan ini hilang.

### 4. Verifikasi = menolak bukti, bukan memberi nilai

SPV GA **tidak** memberi angka. Ia hanya menetapkan satu realisasi `diverifikasi` atau `ditolak` beserta alasannya. Perannya menjaga bukti, bukan menaksir kinerja — dan itu yang membedakan cacahan dari pendapat.

Ini sejalan dengan [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] §4 versi 2026-09-24, yang juga menetapkan approve sebagai **konfirmasi** dan bukan tempat mengetik angka. Kedua keputusan berangkat dari alasan yang sama: begitu manusia mengetik angkanya, yang tersimpan adalah pendapat, dan tak ada yang bisa memeriksanya kemudian.

### 5. ⛔ Skor BERBASIS PENYELESAIAN, bukan pengecualian

```
Realisasi PM = realisasi terverifikasi ÷ jatuh tempo pada periode × 100
```

**Ini sengaja berbeda dari [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] §5**, yang menghitung `max(0, 100 − Σ potongan tiap temuan)` sehingga **tanpa temuan bernilai 100**. Model potongan itu benar untuk inspeksi kebersihan, karena yang diukur ada-tidaknya pelanggaran dan tidak adanya pelanggaran memang kabar baik.

Untuk perawatan berkala ia **terbalik arah**. Tidak adanya catatan bukan kabar baik, melainkan justru keadaan gagalnya: dengan model potongan, aset yang tak pernah disentuh siapa pun akan bernilai **100**. Karena itu PM berangkat dari **nol dan naik dengan bukti**, bukan dari 100 dan turun dengan temuan.

Karena itu: **tanpa bukti bernilai nol, bukan seratus.** Siapa pun yang kelak menyeragamkan kedua model ini akan menghidupkan kembali persis masalah yang keputusan ini perbaiki.

Jatuh tempo nol pada satu periode menghasilkan **nilai absen**, bukan 0 dan bukan 100 — mengikuti pola sumber KPI yang sudah ada, di mana ketiadaan data dibedakan dari nilai nol.

### 6. Nasib realisasi yang belum diverifikasi saat periode tutup

Realisasi ber-status `menunggu` pada saat periode dinilai **dikeluarkan dari pembilang DAN penyebut**.

Alasannya: kepatuhan seseorang tidak boleh ditentukan oleh kecepatan orang lain merespons. Menghitungnya sebagai gagal akan menghukum teknisi yang sudah bekerja tepat waktu hanya karena SPV belum sempat memverifikasi. Mengeluarkannya dari kedua sisi bersifat netral bagi yang dinilai, dan tetap terlihat sebagai tunggakan di layar verifikasi.

⚠️ Konsekuensi yang diterima sadar: realisasi yang **tidak pernah** diverifikasi menjadi tak terhitung selamanya. Layar verifikasi karena itu wajib menampilkan tunggakan beserta umurnya, supaya yang mengendap terlihat.

### 7. Sumber KPI membaca, tidak menghitung ulang

Sumber baru `pemeliharaan_preventif` di employee-service memetakan payload `GET /internal/pm-metrik` menjadi `Cuplikan`, mengikuti batas [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]: employee-service boleh menarik, tetapi seluruh aturan nilai tinggal di satu tempat. Menghitung ulang di sisi employee melahirkan definisi kedua yang menyimpang diam-diam.

Metrik yang dilayaninya **dua**, di dua posisi berbeda: `Realisasi Preventif Maintenance Building & Fasilitas` (0,30, posisi Building Maintenance) dan `Persentase SLA Preventife Maintenance Alat Operational Tepat Waktu` (0,25, posisi GA Staff).

### 8. Yang TIDAK diputuskan di sini

- **Metrik biaya** (`Mengontrol biaya (Realisasi/Budget)` 0,35 dan `Efisiensi biaya operasional GA` 0,20) menunggu master anggaran GA, yang belum ada dan bukan lingkup ADR ini.
- **Apakah tiket task-management atau `repair_history` yang menjadi catatan resmi kerusakan gedung** tetap terbuka. ADR ini hanya menetapkan bahwa **perawatan berkala** tinggal di inventory-service; pertanyaan tentang **perbaikan kerusakan** belum dijawab dan tetap tercatat sebagai TBD di [[GA - Building Maintenance]].
- **Pemindahan dokumen Google teknisi ke dalam sistem** tidak dijanjikan oleh ADR ini, walau menjadi ukuran keberhasilannya (lihat Consequences).

## Consequences

**Yang membaik**

- Metrik berbobot **0,55** di dua posisi berpindah dari ketikan tangan ke cacahan berbukti.
- Template `Building and Maintenance Staff` tinggal menyisakan metrik biaya sebagai satu-satunya yang manual. Bila kelak itu pun terjawab, template ini menjadi **1,00 otomatis** dan memenuhi syarat [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]] — template HRGA pertama yang mencapainya.
- Riwayat satu aset berada di satu service: perawatan berkala, perbaikan, dan opname bersebelahan.
- GA mendapat daftar perawatan yang berlaku sebagai rencana kerja, bukan hanya sebagai bahan KPI.

**Ongkos dan risiko**

- ⛔ **Risiko terbesarnya adopsi, bukan teknis.** Tiga mekanisme sebelumnya di lingkup ini dibangun lalu tidak pernah terisi (Context §8). Ukuran keberhasilan yang jujur bukan "modulnya jadi", melainkan **dokumen Google teknisi berhenti dipakai**. Bila setelah dua periode teknisi masih mengetik di Google Docs, keputusan ini gagal dan layak ditinjau ulang, bukan ditambal dengan pengingat.
- Menyusun `pm_jadwal` pertama kali adalah pekerjaan GA, bukan dev, dan belum ada yang mengerjakannya. Daftar sumbernya ada di dokumen "Checklist Jumlah Aset yang di-maintenance" milik GA yang **belum diperiksa isinya**.
- Verifikasi menambah pekerjaan SPV GA tiap periode. Bila menumpuk, §6 membuatnya netral bagi yang dinilai, tetapi angkanya jadi berdiri di atas penyebut yang mengecil — itu wajib terlihat di layar.
- Menambah satu panggilan lintas-service (employee → inventory), tepat saat [[ADR - 0122 Satgas Per-PIC Input Bebas Gantikan Form Builder, SLA Temuan dan Skor dari Approval]] menghapus satu. Diterima sadar: kopling ini muncul karena subjeknya memang tinggal di service lain, dan polanya sudah dipakai sumber `pelatihan` yang membaca learning-service.

**Konsekuensi deploy**

- Backend naik lebih dulu (inventory-service **dan** employee-service), lalu frontend. Kontrak berubah, jadi urutannya mengikat.
- **Tidak** ada kategori inbox baru, sehingga notification-service tidak wajib ikut naik. Bila kelak pengingat ditambahkan, aturan "pengirim + notification-service naik bersama" berlaku.
- Tidak ada env baru, jadi `--force-recreate` tidak diperlukan.
- Verifikasi tidak boleh berhenti pada `docker ps` atau `/health`: buktinya satu jadwal dibuat, satu realisasi diunggah berfoto, diverifikasi, lalu angkanya muncul di scorecard lewat gateway.

## Dokumen Terkait

[[GA - Building Maintenance]] · [[GA - Machine & Utility Maintenance]] · [[GA - Checklist Management]] · [[GA - Dashboard per Posisi]] · [[HRIS - Matriks KPI per Departemen]] · [[Microservices - Inventory Service]] · [[Microservices - Task Management Service]] · [[ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate]] · [[ADR - 0071 Peta Kepatuhan Peraturan Perusahaan dan Kewajiban ADR untuk Penyimpangan]]

# ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI

## Deskripsi

*Dua metrik posisi **Live Support** yang tak punya sistem pencatat, tema host live dan teaser (bobot 0,70), dinilai dari **setoran bukti per karya** yang **disetujui penyetuju departemen** penyetornya. KPI hanya menghitung yang disetujui. Yang dinilai menyetor, yang lain memutus, sehingga metriknya layak otomatis tanpa menjadi penilaian diri.*

- **Status**: 🟡 Diputuskan dan **merged 2026-09-17** (bip-erp #1954 17:52 WIB, #1955 18:13 WIB, erp-frontend #1632 18:14 WIB), **belum deploy**. Kode: bip-erp [#1954](https://github.com/bip-itteam-internal/bip-erp/pull/1954) `feat/marketing-analytics-karya-live-support` (marketing-analytics, notification-service, shared-library), bip-erp [#1955](https://github.com/bip-itteam-internal/bip-erp/pull/1955) `feat/employee-karya-live-support` (employee-service), erp-frontend [#1632](https://github.com/bip-itteam-internal/erp-frontend/pull/1632) `feat/live-support-karya`. Test hijau di ketiganya; layar diverifikasi di Chrome atas hasil build dengan stub API. Belum pernah dipanggil lewat gateway mana pun.
  ✅ *Diperbarui 2026-09-18*: **marketing-analytics SUDAH ter-deploy ke PROD.** Buktinya biner, bukan `docker ps`: koleksi `live_support_karya` berdiri dengan **keempat indeksnya**, termasuk indeks unik parsial `{company_id, employee_id, jenis, tautan_kunci}` ber-`partialFilterExpression {jenis:"teaser"}` yang persis dijelaskan §5 — indeks itu hanya lahir bila kode ini ikut boot. ⚠️ Yang TERBUKTI hanya marketing-analytics; status employee-service dan frontend **belum diukur**, jangan disimpulkan dari baris ini. **0 dokumen** tersetor, jadi dua metrik tema dan teaser (bobot 0,70) masih nol data.
- **Tanggal**: 2026-09-17
- **Terkait**: [[Microservices - Marketing Analytics Service]] · [[Microservices - Employee Service]] · [[Microservices - Notification Service]] · [[APP - Web ERP]] · [[HRIS - Matriks KPI per Departemen]]

## Context

Diukur di produksi 2026-09-17 sebelum keputusan diambil:

1. **Template `Host Live Support Kyura` punya dua metrik tanpa sumber**: `kualitas-tema` berlabel "Membuat tema hostlive perbulan" (minimal 10 tema) dan `kuantitas-tema` berlabel "Membuat cuplikan konten (Teaser)" (minimal 10 cuplikan), masing-masing 0,35. Dua metrik lain sudah bersumber `kesiapan_live` ([[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]]). ⚠️ `key` dan label tertukar makna sejak perubahan template 2026-08-29: "tema" ada di key `kualitas-tema`, "teaser" di `kuantitas-tema`.
2. **Teaser tak bisa dihitung dari data TikTok.** Dari 123.144 video `tt_shop_video_performances` hanya 4 judul memuat kata teaser atau cuplikan, tak satu pun teaser live; videonya tertaut ke akun kreator (`creator_username`), bukan karyawan, dan akun brand dipakai bersama.
3. **Laporan Mingguan Live Support** (penilaian diri rating 1 sampai 5, erp-frontend #1588) di-revert lewat erp-frontend #1623.
4. **Form Builder tipe `report`** punya keputusan per butir dan antrean penyetuju departemen, tetapi menolak kiriman kedua per orang per periode ("Form ini hanya boleh diisi sekali") dan belum punya pembaca KPI. Sepuluh tema sebulan tak muat di bentuk itu.
5. **Resolver penyetuju departemen sudah ada**: `GET /internal/department-approver` di employee-service, dipakai form-builder, inventory, dan procurement. Prod: penyetuju Kyura memegang `kyura: supervisor`.

## Decision

1. **Setoran bukti per karya, disetujui peninjau; KPI menghitung yang disetujui.** Bukan penilaian diri, bukan angka yang diketik supervisor.
2. **Register khusus di marketing-analytics**, koleksi `live_support_karya`, bukan Form Builder (batas satu kiriman per periode). Pemilik data marketing-analytics, pemilik data siaran live.
3. **Seluruh layar di web ERP**: halaman Setor Tema & Teaser dan Tinjau Setoran di bawah induk menu Live Support. Tanpa perubahan MyBharata.
4. **Periode = bulan SETOR PERTAMA menurut WIB**, dicap server. Tak berubah saat kirim ulang maupun saat diputus, supaya perbaikan yang menyeberang bulan atau peninjau yang terlambat tak memindahkan karya ke bulan lain.
5. **Bukti berupa tautan https saja**, tanpa unggah berkas. Tautan wajib untuk teaser, opsional untuk tema. Satu tautan teaser terhitung sekali per orang, ditegakkan indeks unik parsial atas bentuk normal tautan (`tautan_kunci`: host huruf kecil, tanpa query, fragment, dan garis miring ujung).
6. **Penolakan wajib beralasan**; pemilik memperbaiki **setoran yang sama** lalu mengirim ulang (status kembali menunggu). Disetujui bersifat final. Transisi atomik lewat filter status lama.
7. **Notifikasi ke Live Support saat setoran diputus** (kategori inbox `live-support-karya-decided`, alasan penolakan ikut di isi). Peninjau tanpa notifikasi per setoran, memakai badge jumlah menunggu di menu Tinjau Setoran.
8. **Peninjau = penyetuju departemen penyetor**, ditanyakan ke employee-service per keputusan dan per departemen di antrean. Supervisor IT boleh melihat seluruh antrean, tidak memutus. Penyetor tak bisa memutus setorannya sendiri. Resolver gagal atau env kosong = **502, tidak diloloskan** (gagal-tertutup).
9. **Sumber KPI `karya_live_support`** di employee-service, metrik `tema_disetujui` dan `teaser_disetujui`, scope hanya `individu`, reduksi `jumlah_nilai` atas satu cacahan. Nol disetujui adalah **nilai 0 yang sah**, bukan galat. `Catatan` selalu menyebut disetujui, menunggu tinjauan, dan ditolak. Penjaga posisi dua lapis sama dengan `kesiapan_live`.

### Menyimpang sadar dari ADR 0101 §3

[[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]] §3 menulis bahwa marketing-analytics sengaja tak memanggil employee-service. **Keputusan ini membuat marketing-analytics memanggil `GET /internal/department-approver`** (env baru `EMPLOYEE_MODULE_URL`). Sah menurut [[REF - Kepemilikan Data]] aturan 2 (konsumsi lewat pemilik, bukan lewat database-nya): hierarki penyetuju tetap diselesaikan employee-service dan tak disalin. Yang dipertahankan dari ADR 0101: pemetaan karyawan ke departemen untuk KPI tetap dikirim pemanggil, dan marketing-analytics tak menyimpan salinan data karyawan apa pun.

## Consequences

### Yang membaik

- Keempat metrik Live Support punya sumber; skor posisi itu bisa dibekukan otomatis begitu blok `auto` keempatnya terpasang ([[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]).
- Angka yang dilihat Live Support di kartu ringkasan dan angka yang dinilai berasal dari satu penghitung (`ringkasKarya`).

### Yang memburuk atau tetap terbuka

- ⚠️ **Setoran departemen tanpa penyetuju terdaftar menunggu selamanya.** Antreannya tak tampil bagi siapa pun selain supervisor IT (yang tak bisa memutus), dan Live Support hanya melihat status Menunggu. Per 2026-09-16 satu-satunya pemegang posisi ada di Kyura, yang punya penyetuju.
- ⚠️ **Setoran yang belum ditinjau saat skor dibekukan tak dihitung**, dan keputusan sesudahnya tak mengubah skor beku. Yang menunggu tersebut di `Catatan` metrik.
- ⚠️ **Gerbang menu Tinjau Setoran di web adalah cermin longgar**: supervisor/admin `kyura` atau `beauty_hacks` plus supervisor IT. Penyetuju yang ditunjuk master data tanpa peran itu tak melihat menunya walau server mengizinkannya memutus.
- ⚠️ **Nama jabatan "Live Support" kini hidup di tiga tempat** (employee `posisiLiveSupport`, marketing-analytics `posisiPenyetorKarya`, erp-frontend `bolehSetorKarya`). Gerbang setor membaca NAMA jabatan dari header gateway karena header tak membawa `position_key`; mengganti kata jabatannya di master data menutup menu dan menolak setoran 403 berpesan syarat.
- **Deploy menuntut dua container bersama** (kategori inbox baru: marketing-analytics + notification-service, yang juga membawa aturan rute web halaman Setor) dan `--force-recreate` marketing-analytics untuk env baru.
- **MyBharata belum memetakan kategori baru**; notifikasinya tampil berlabel "Sistem" sampai rilis aplikasi berikutnya. Tujuan notifikasi dikirim lewat `AppRoute`, bukan `ExternalURL` (yang dibuka MyBharata sebagai tautan eksternal).

### Yang sengaja tidak dilakukan

- **Unggah berkas bukti.** Tautan cukup; arsip saat video dihapus ditunda sampai diminta.
- **Penilaian mutu tema.** Redaksi target adalah jumlah; yang diukur jumlah disetujui.
- **Menghitung teaser dari data TikTok**, karena datanya tak menautkan video ke karyawan.
- **Angka target di layar Setor.** Target hidup di template KPI dan katalognya digerbang setara penyunting template, jadi menanamnya di layar melahirkan salinan kedua.

## Dokumen Terkait

- [[Microservices - Marketing Analytics Service]] § Setoran karya Live Support · [[API - Marketing Analytics Service]] § Setoran karya Live Support
- [[Microservices - Employee Service]] § sumber KPI `karya_live_support`
- [[Microservices - Notification Service]] (kategori `live-support-karya-decided`, rute web halaman Setor)
- [[APP - Web ERP]] § induk menu Live Support
- [[HRIS - Matriks KPI per Departemen]] § Kyura → Live Support
- [[REF - Kepemilikan Data]] · [[REF - Penamaan Metrik & Sumber KPI]] · [[RUN - Menambah Metrik KPI Otomatis]]
- [[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]] · [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]] · [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]]

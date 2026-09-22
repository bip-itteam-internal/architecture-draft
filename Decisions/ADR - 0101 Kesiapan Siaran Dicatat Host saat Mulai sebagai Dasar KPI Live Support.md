# ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support

## Deskripsi

*Posisi **Live Support** dinilai dari **kesiapan siaran** yang dicatat HOST tepat sebelum menekan Mulai (dua butir ceklis ditambah Live Support yang bertugas), bukan dari hasil siaran host. Yang mengisi bukan yang dinilai, dan itulah yang membuatnya layak jadi dasar KPI otomatis.*

- **Status**: ⚠️ Implemented (ada catatan). Backend dan web **di PROD sejak 2026-09-17** (image `employee-service` 08:12:44, `marketing-analytics-service` 08:12:27, `frontend-hris` 08:16:21 WIB; gerbang biner dan fungsional diverifikasi). MyBharata **merged ke `dev`, belum dirilis**. Blok `auto` di template **belum dipasang** (sengaja, lihat Consequences).
- **Tanggal**: 2026-09-16
- **Terkait**: [[Microservices - Marketing Analytics Service]] · [[Microservices - Employee Service]] · [[APP - MyBharata]] · [[HRIS - Matriks KPI per Departemen]]

## Context

Diukur di produksi 2026-09-16, bukan disimpulkan:

1. **Posisi Live Support tak punya satu pun metrik otomatis.** Template `Host Live Support Kyura`, 4 metrik manual (`pengelolaan-kelengkapan-alat` 0,20, `kualitas-tema` 0,35, `kuantitas-tema` 0,35, `pengelolaan-product-display` 0,10). Satu pemegang posisi. Satu-satunya skor seumur hidup ada di 2026-07; Agustus kosong, dan karena nol metrik otomatis, cron finalisasi tak akan menambalnya ([[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]).

2. **Tak ada data yang menautkan Live Support ke siaran mana pun.** `live_shifts` (185 dokumen) hanya punya `host[]`. `mart_live_sessions` kaya metrik hasil siaran, tetapi seluruhnya melekat ke toko dan host. Tak ada koleksi tentang alat, tema, atau etalase.

3. **Menunjuk `kinerja_live` untuk Live Support menghasilkan kosong, bukan angka tim.** Sumber itu selalu mengirim `employee_id`, jadi scope `department` pun tetap menghitung angka orang itu sendiri; Live Support tak pernah punya shift atas namanya, sehingga hasilnya "belum ada shift live tercatat".

4. **Jalan "catat Live Support sebagai co-host" yang tertulis di kontrak MyBharata tak pernah dipakai, dan memang salah.** Kontrak `LiveShiftRepository.daftarKandidatCoHost` menyatakan Live Support sengaja ikut daftar co-host. Terukur: **0 dari 185 shift** memuat pemegang posisi Live Support di `host[]`, padahal co-host sendiri dipakai (26 shift berdua, 4 bertiga). Dan orang di `host[]` dinilai lewat `kinerja_live` scope individu (conversion rate, add to cart, durasi tonton), metrik yang mengukur cara **membawakan** siaran, bukan menyiapkannya.

5. **Sumber `ceklis_kpi` yang sudah ada tak cocok bentuknya.** Ia per periode bulanan (`period_key`, tenggat tanggal 1–5, satu butir satu jawaban), sementara yang dibutuhkan per sesi, puluhan kali sebulan, menghasilkan rasio.

## Decision

1. **Ceklis dua butir diisi HOST sebelum Mulai**: `device_lengkap` (alat penunjang) dan `display_sesuai` (display etalase). Keduanya menjawab 2 dari 4 metrik template (bobot 0,30). Bawaan keduanya **menyala**: formulir yang menghukum keadaan normal akan diisi asal.

2. **Menahan, tapi boleh dilanjut dengan alasan.** Butir yang dijawab tidak wajib disertai catatan; ditegakkan **di server** (`validasiKesiapan`, 400), bukan hanya di layar. Siaran tak pernah mati karena ceklis.

3. **Live Support yang bertugas dicatat di `live_shifts.pendukung[]`, tipe TERPISAH dari `host[]`.** Daftar kandidatnya dimiliki employee-service (`GET /list?type=live-support-candidate`, `posisiLiveSupport`) dan diambil MyBharata; marketing-analytics sengaja tak memanggil employee-service ([[REF - Kepemilikan Data]]). Daftar co-host yang sudah ada **tidak** dipakai karena mencampur host dengan pendukung.

4. **`kesiapan` bertipe pointer dan tak ditulis ke Mongo saat nil.** Nil berarti "tak pernah ditanya" (sesi lama, klien lama, hasil ambil alih) dan **keluar dari penyebut persentase**, berbeda dari "dijawab tidak lengkap" yang dihitung gagal. `diisi_oleh` dan `diisi_pada` distempel server dari header gateway dan jam server, tak pernah diterima dari body.

5. **Satu ceklis per sesi, dihitung per sesi.** Pemilih akun di MyBharata pilihan tunggal, jadi host yang membuka tiga akun menekan Mulai tiga kali dan mengisi ceklis tiga kali. Tak ada penyalinan ceklis lintas sesi.

6. **Ambil alih MEWARISI `pendukung`, tidak mewarisi `kesiapan`.** Pendukung adalah keadaan yang bertahan (Live Support yang sama masih menopang akun yang sama); kesiapan adalah pemeriksaan pada satu momen, dan menyalinnya akan mengarang pemeriksaan yang tak pernah terjadi.

7. **Sumber KPI baru `kesiapan_live`, TERPISAH dari `kinerja_live`.** Atribusinya lewat `pendukung[]`, bukan `host[]`; satu sumber dengan dua aturan atribusi yang dipilih menurut nama metrik adalah kelas bug yang gagalnya berupa 200 berisi nol baris. Dua sub-metrik `device_lengkap_persen` dan `display_sesuai_persen`, scope **hanya `individu`**, reduksi `rata_rata`, tanpa metrik baku.

8. **Nol persen bukan jawaban untuk "belum ditanya".** Endpoint mengirim persen `null`; sumber KPI menerjemahkan `null` menjadi **galat** (metrik gagal hitung), bukan 0. `CakupanPersen` = sesi berceklis ÷ sesi total.

9. **Sebab di hulu dilaporkan lebih dulu.** `toko_diminta` membedakan "departemen belum punya toko TikTok terpetakan" dari "belum ada sesi", sehingga kalimat galatnya menyebut master data, bukan menyalahkan orangnya.

10. **Penjaga posisi dua lapis.** Metrik hanya menilai pemegang posisi Live Support, dicocokkan lewat `position_key` kanonik **atau** `position` mentah. Satu lapis tak cukup: satu-satunya pemegang posisi itu di produksi masih ber-`position_key` `videographer`, sisa nama jabatan lama.

## Consequences

### Yang membaik

- Dua metrik Live Support berhenti jadi tebakan dan punya angka yang bisa ditelusuri ke sesi.
- Kelalaian mengisi pendukung **terlihat**: `sesi_departemen_tanpa_pendukung` masuk ke `Catatan` metrik.

### Yang memburuk atau tetap terbuka

- ⛔ **Skor Live Support TETAP diisi manual.** `layakDifinalisasi` menuntut seluruh metrik punya `auto` dan nilai; tema dan teaser (bobot 0,70) tak punya sistem pencatat. 🟡 *Diperbarui 2026-09-17*: sistem pencatatnya diputuskan dan di-merge 2026-09-17 (belum deploy) di [[ADR - 0106 Tema dan Teaser Live Support Disetor dan Diputus Penyetuju Departemen sebagai Dasar KPI]]. ADR itu juga **menyimpang sadar dari §3 di atas**: marketing-analytics kini memanggil employee-service untuk penyetuju departemen.
- ⚠️ **Tak ada angka September.** Terukur 2026-09-17: `sesi_departemen_tanpa_pendukung` Kyura **130** dan `sesi_total` nol, karena belum satu sesi pun dicatat lewat aplikasi baru. Metriknya baru berisi sesudah MyBharata dirilis. 🔴 *Diperbarui 2026-09-18*: masih nol, dan sebabnya ternyata BUKAN sekadar rilis aplikasi. Dari **234 sesi** di `live_shifts`, **0** mencantumkan pendukung dan **1** mengisi ceklis — termasuk sesi yang jelas berasal dari aplikasi baru (ber-`kesiapan` terisi, `pendukung` tetap kosong). Pemilihnya opsional dan dilewati. Ditangani [[ADR - 0110 Kesiapan Live Dinilai Lintas Departemen dan Pendukung Diisi Backend saat Tunggal]].
- ⚠️ ~~**Blok `auto` sengaja belum dipasang.**~~ ✅ *Diperbarui 2026-09-18*: **sudah dipasang**. Terukur di prod, template `Host Live Support Kyura` kini ber-`auto` di **keempat** metriknya (`kesiapan_live` untuk device dan display, `karya_live_support` untuk tema dan teaser), sehingga posisi ini memenuhi syarat finalisasi otomatis [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]. ⚠️ Syarat itu menuntut SELURUH metrik menghasilkan angka, jadi selama keempatnya masih nol data, pembekuan otomatis tetap dilewati tiap hari tanpa bunyi.
- ⛔ *Ditambahkan 2026-09-18*: **penyaringan departemen di jalur hitung ternyata membuang sesi yang sah.** §7 memutuskan atribusi lewat `pendukung[]`, tetapi `HandlerKPIKesiapanLive` menyaring lebih dulu ke toko departemen orang yang dinilai. Begitu posisi Live Support ditugaskan lintas departemen, 82 dari 234 sesi September (35%) hilang senyap dari penilaian orang yang mendukungnya. Dicabut oleh [[ADR - 0110 Kesiapan Live Dinilai Lintas Departemen dan Pendukung Diisi Backend saat Tunggal]].
- ⚠️ **`pendukung[]` datang dari body tanpa verifikasi terhadap sesi.** Penjaga posisi memastikan yang dinilai memang Live Support, tetapi **tidak** mencegah host berkolusi dengan Live Support sungguhan, karena employee-service tak melihat isi `pendukung[]` tiap sesi. Yang tersisa hanya jejak `diisi_oleh`.
- ⚠️ **Host yang membuka banyak akun mengisi ceklis berulang** untuk setup alat yang sama.
- ⚠️ **Live Support tak punya layar untuk melihat sesi yang mencatatnya.** Diminta user 2026-09-16 sebagai pekerjaan nanti: menu khusus Live Support (jadwal host live, sesi aktif, penunjang KPI). Dua batas yang wajib dibaca sebelum merancangnya: [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]] (kategori sidebar lahir dari paket izin) dan [[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]] (rincian per sesi di web adalah keputusan baru). 🟡 *Diperbarui 2026-09-17*: diputuskan di [[ADR - 0108 Monitoring Sesi Live di Web Hanya Baca untuk Leader dan Live Support]] (menu Monitoring Sesi Live di induk Live Support; Live Support melihat sesi toko departemennya, termasuk pendukung dan ceklis kesiapan, tanpa angka penjualan).
- **Klien MyBharata tidak mengirim `item_kurang`**, walau backend menerimanya. Daftar item alat belum disepakati pemilik metrik; layar memakai satu isian Catatan.

### Yang sengaja tidak dilakukan

- **Ambang durasi sesi.** Sesi 24 detik ikut dihitung; ambang mengubur sesi yang gagal karena alat rusak, justru kejadian yang paling ingin diukur.
- **`pemeriksaan_id` dari klien** untuk mengelompokkan ceklis. Itu menambah satu lagi dasar penilaian yang berasal dari body.
- **Pilihan ganda item alat**, karena pilihan berisi item karangan terlihat resmi lalu memaksa yang tak ada di daftar masuk ke kotak paling mirip.

## Dokumen Terkait

- [[Microservices - Marketing Analytics Service]] § pencatatan sesi live dan `/kpi/kesiapan-live`
- [[Microservices - Employee Service]] § sumber KPI `kesiapan_live`
- [[API - Marketing Analytics Service]] · [[API - Employee Service]]
- [[HRIS - Matriks KPI per Departemen]] § Kyura → Live Support
- [[REF - Kepemilikan Data]] · [[REF - Penamaan Metrik & Sumber KPI]]
- [[RUN - Menambah Metrik KPI Otomatis]]
- [[ADR - 0032 Kepemilikan kpi_score dan Batas Pengumpul Metrik]] · [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] · [[ADR - 0088 Ambil Alih Sesi Live oleh Host Terjadwal dan Tutup Otomatis Akhir Shift]]

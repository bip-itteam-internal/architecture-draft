## Untuk Manajemen

- **Yang berubah di layar**: host live yang menyiarkan di beberapa akun sekaligus akan melihat SEMUA siarannya yang sedang berjalan, bukan satu saja seperti sekarang, sehingga tiap siaran bisa dijeda dan diakhiri sendiri-sendiri. Memulai beberapa akun bisa dilakukan sekali klik. Angka "jam siaran" berubah artinya menjadi lama orangnya benar-benar bekerja, jadi host yang memegang tiga akun selama dua jam tercatat dua jam, bukan enam.
- **Siapa terdampak**: host live dan live support (14 orang), atasan marketing yang meninjau performa tim, dan HR yang mengisi target KPI Host Live. Tidak menyentuh absensi, penggajian, cuti, maupun karyawan di luar marketing.
- **Tidak dijanjikan**: sistem tetap TIDAK bisa mengetahui sendiri siapa yang memegang sebuah akun; angkanya lahir dari host menekan tombol Mulai dan Akhiri, jadi siaran yang tidak dicatat tetap tidak terhitung. Tidak ada perubahan cara insentif dihitung dan dibayarkan pada keputusan ini. Tidak ada penilaian otomatis atas kedisiplinan host, dan siaran di luar jadwal tetap sekadar ditandai, bukan dihukum. Laba per siaran tetap belum tersedia.
- **Besaran kerja**: sedang, dan sebagian besar di tampilan. Bentuk penyimpanan datanya tidak diubah sama sekali karena sistem sudah menerima siaran paralel sejak sekarang; yang dikerjakan adalah menampilkannya, membetulkan cara jam dihitung, dan memasang rambu supaya siaran ganda tidak salah dibaca sebagai kesalahan input.

## Deskripsi

*Satu host yang menyiarkan serentak di beberapa akun dicatat sebagai BEBERAPA sesi paralel, satu per akun, bukan satu sesi yang memuat banyak akun. Bentuk penyimpanan tidak berubah karena sudah mengizinkannya; yang diputuskan di sini adalah tiga aturan turunannya: jam siaran seseorang dihitung sebagai jam dinding (union jendela waktu) bukan penjumlahan per sesi, tumpang tindih antar-akun berbeda milik orang yang sama diperlakukan SAH dan hanya ditandai, dan GMV-nya diatribusikan ke departemen host bukan departemen pemilik akun.*

- **Status**: ⚠️ **Diterima, sebagian terimplementasi** (2026-08-30). Berdiri di atas pengukuran langsung database produksi pada 2026-08-30 (lihat Context) dan di atas [[Microservices - Marketing Analytics Service]] yang berstatus ⚠️ Implemented dengan catatan, bukan di atas dokumen konsep.
  - ✅ **§1** (satu sesi satu akun) — tak menuntut perubahan kode, penyimpanan sudah mengizinkannya.
  - ✅ **§5** (klien menampilkan seluruh sesi) — **web tayang di prod** 2026-08-30 (bip-erp #1537 + erp-frontend #1321/#1325); **mobile selesai di branch** `feat/live-shift-sesi-jamak`, belum merged.
  - ✅ **§6** (lingkup IT) — sudah berlaku, diterima sadar.
  - 🟡 **§2** (jam dinding union) dan **§3** (tumpang tindih ditandai sah) — **belum dikerjakan**, dan keduanya yang menyentuh uang. Selama §2 belum ada, dua permukaan frontend masih menggandakan jam.
  - 🟡 **§4** (GMV ke departemen host) — belum diverifikasi ulang setelah §1 berlaku.
  - ⛔ **Belum ada satu pun host sungguhan yang memakainya.** `live_shifts` prod masih **0 dokumen**; papan kerjanya menjadikan angka itu uji hipotesis, bukan sekadar catatan.
- **Path di repo**: `bip-erp/services/marketing-analytics/live_shift_penjualan.go` · `bip-erp/services/marketing-analytics/live_shift_pengingat.go` · `erp-frontend/src/features/marketing-analytics/components/live-shift/halaman-live-shift.tsx` · `.../panel-sesi-berjalan.tsx` · `.../dialog-mulai.tsx` · `erp-frontend/src/features/integration/icc/lib/ringkas-performa-host-live.ts` · `mybharata-app/lib/src/features/live_shift/presentation/bloc/live_shift_bloc.dart` · `.../bloc/live_shift_state.dart` · `.../widgets/kartu_sesi_berjalan.dart`. Tidak ada berkas baru, tidak ada service baru, tidak ada perubahan gateway.
- **Tanggal**: 2026-08-30

## Context

Pemilik proses menyatakan 2026-08-30 bahwa host live tidak lagi memegang satu akun. Mereka menyiarkan **serentak dari dua perangkat di satu meja**, dan akun-akun itu **bisa milik toko yang berbeda**.

### Fakta ini sudah pernah dicatat dan belum pernah ditindaklanjuti

[[Microservices - Marketing Analytics Service]] menuliskan penilaian KPI live dilakukan **per-departemen, bukan per-orang**, dan menyebut tiga sebab yang menutup jalan ke per-orang. Sebab kedua berbunyi persis "satu host memakai beberapa akun". Jadi kebutuhan ini bukan temuan baru, ia sudah berdiri sebagai penghalang yang tercatat sejak 2026-08-27.

Sisi employee-service sudah menyiapkan jalan keluarnya: scope `individu` **sengaja sudah didaftarkan** supaya perpindahan ke penilaian per-orang cukup diubah HR lewat template tanpa deploy. Yang menahan bukan kontraknya melainkan datanya. Dua penghalang yang disebutnya sudah berkurang satu: pemilih akun dari data nyata (`GET /live-shifts/akun` beserta penanda akun utama pada ambang 60% porsi GMV) sudah ada, sehingga risiko `akun_live` salah ketik tidak lagi menjadi alasan. Yang tersisa adalah koleksinya masih kosong.

### Pengukuran produksi 2026-08-30

| Ukuran | Angka |
|---|---|
| `live_shifts` di produksi | **0 dokumen**. Fitur ini belum pernah dipakai satu host pun |
| `mart_live_sessions` | 5.482 sesi, 2 Juli sampai 29 Agustus, 812 akun, 20 toko |
| Akun brand (`glowbooster*`, `kyurabeauty`) | 174 sesi, **Rp 942 juta**, yaitu **84,8%** dari seluruh GMV live |
| Pasangan sesi tumpang tindih beda akun | **151**, seluruhnya **lintas toko**, 983 jam irisan |
| Setelah artefak dua-etalase dibuang | **148 pasangan, 935 jam** siaran berbeda yang sungguhan |
| Puncak akun brand hidup bersamaan | **4**. Dua akun 422,9 jam tersebar di 46 hari; tiga akun 186,5 jam di 31 hari |

Artefak dua-etalase dipisahkan memakai ambang yang sudah terkalibrasi di kode (selisih mulai maksimal 60 detik **dan** selisih durasi maksimal 2 menit) dan hanya menjelaskan 3 dari 151 pasangan. Sisanya siaran berbeda sungguhan. Praktiknya rutin, bukan kejadian langka, dan **puncaknya empat**, jadi rancangan yang mematok angka dua akan patah.

⚠️ **Batas ukuran ini, dinyatakan terang.** Data TikTok membuktikan dua akun brand hidup bersamaan, **bukan** bahwa satu orang memegang keduanya. Ketidakmampuan itu persis alasan `live_shifts` ada. Angka di atas adalah batas atas yang konsisten dengan keterangan pemilik proses, bukan bukti langsung.

### Yang ternyata sudah mengizinkan, dan tiga celah yang sebenarnya

Penemuan yang mengubah bentuk pekerjaan: **penyimpanan sudah mengizinkan sesi paralel hari ini.** Index unik parsialnya hanya atas `akun_live`, tidak menyertakan `shop_id` maupun `host.employee_id`, jadi tidak ada satu pun invarian per orang. Dua perangkat dua akun **sudah bisa tercatat sekarang**. Yang rusak seluruhnya ada di hilir:

1. **Sesi kedua tidak punya tampilan sama sekali.** Web mengambil elemen pertama dari daftar sesi berjalan, klien mobile mengambil `milik.first`. Sesi kedua tak bisa dijeda maupun diakhiri. Akibat lanjutannya keras: sesi itu bisa menggantung melewati ambang 12 jam, dan pada ambang itu sistem **memaksa porsi GMV host menjadi nol**. Peringatan jam ke-11 tidak pernah sampai karena kartunya tidak pernah dirender. Host kehilangan uang dari siaran yang benar-benar ia kerjakan, tanpa satu pun pesan.
2. **Jam siaran terhitung ganda di dua tempat**: kartu metrik halaman host dan agregasi performa host di layar tim ICC, yang menjumlahkan durasi efektif per baris porsi host tanpa dedup jendela waktu.
3. **Tidak ada rambu apa pun.** Penandaan tumpang tindih menuntut `shop_id` **dan** `akun_live` sama, jadi dua sesi paralel milik satu orang tidak pernah tertandai. Pengingat pun terkirim dua kali karena dedupnya per dokumen sesi, bukan per orang.

### Preseden yang sudah ada di kode

Peleburan sesi kembar untuk jalur KPI sudah menetapkan kaidahnya secara eksplisit: **"ORDERS DIJUMLAH, SESI TIDAK ... Menghitung dua akan melebihkan produktivitas host."** Keputusan di bawah memperluas kaidah yang sama dari cacah siaran ke cacah **jam**.

### Tidak ada konsumen hilir yang terikat

Penelusuran seluruh repo bip-erp menemukan **nol** pembaca `porsi_host` maupun `durasi_efektif_detik` di luar service marketing-analytics sendiri. Jalur KPI membaca endpoint yang berbeda (`kinerja_live`), bukan koleksi ini. Satu-satunya kontrak yang terikat adalah aplikasi mobile. Bentuk datanya aman diperluas.

### Gerbang aturan bisnis: diam

`mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` (turunan Peraturan Perusahaan 2026-2028, yang menang atas perilaku sistem) **tidak menyebut siaran, live, host, GMV, insentif, komisi, maupun target penjualan sama sekali**, dan tidak memuat plafon jam kerja maupun larangan tumpang tindih shift. Ia tetap mengikat keputusan ini dalam dua hal: upah lembur hanya sah dengan SPKL dan hanya untuk tim produksi, jadi **jam siaran tidak boleh tumbuh menjadi jalur lembur**; dan jalur otomatis yang sudah diatur di sana bersifat memotong tunjangan serta menerbitkan SP, jadi **sesi yang tervonis di luar shift tidak boleh dialirkan ke jalur itu**.

## Decision

### 1. Satu sesi tetap satu akun. Siaran serentak dicatat sebagai beberapa sesi paralel

Bentuk `live_shifts` **tidak diubah**: satu dokumen tetap memuat satu `shop_id`, satu `akun_live`, dan `host[]` yang jamak. Siaran serentak di N akun menghasilkan N dokumen.

Alternatif yang ditolak adalah menjadikan `akun_live` sebuah larik pasangan toko dan akun. Penolakannya bukan soal ongkos semata:

- Kunci penjodohan ke sesi TikTok menuntut pasangan `shop_id` dan `username` yang tunggal. Sesi bermuatan banyak akun harus tetap menyimpan N pasangan itu, jadi kardinalitasnya tidak benar-benar hilang, hanya berpindah ke dalam dokumen.
- Keadaan operasionalnya per akun, bukan per sesi: host mengakhiri akun A sementara akun B lanjut. Model satu sesi banyak akun harus menambahkan keadaan mulai, jeda, dan selesai **di dalam** tiap elemen larik, yang berarti membangun ulang seluruh mesin jeda dan penutupan.
- Index unik parsial, pemeriksa duplikat, validasi karakter aman, deteksi tumpang tindih, dan bentuk BSON-nya semuanya berdiri di atas `akun_live` skalar.

Karena penyimpanan sudah mengizinkan sesi paralel, keputusan ini **tidak menuntut migrasi data maupun perubahan index**.

### 2. Jam siaran seseorang adalah jam dinding, bukan penjumlahan per sesi

Jam siaran seorang host pada suatu periode dihitung sebagai **union jendela waktu** seluruh sesinya, setelah jeda dikurangi. Host yang menyiarkan 2 jam di tiga akun sekaligus tercatat **2 jam**, bukan 6.

Alasannya: satu orang menjalani satu jam kerja. Angka ini dibaca berdampingan dengan jadwal dan kehadiran, dan angka yang tidak bisa dibandingkan antara host pemegang satu akun dan host pemegang tiga akun tidak berguna untuk menilai siapa pun. Penjumlahan per sesi juga mendilusi GMV per jam sebesar jumlah akun yang dipegang, sehingga host yang bekerja paling keras justru terbaca paling tidak produktif.

Kaidah ini adalah perluasan langsung dari "orders dijumlah, sesi tidak" yang sudah berlaku di jalur KPI: **rupiah dijumlah, jam tidak.**

`durasi_efektif_detik` **per sesi tetap ada dan tidak berubah artinya**. Ia komponen sejajar, bukan angka jam siaran orang. Yang dilarang adalah menjumlahkannya lintas sesi untuk satu orang. Karena aturan ini mudah dilanggar diam-diam oleh pemanggil berikutnya, penjumlahan itu **wajib hidup di satu fungsi** yang dipakai semua permukaan, dan larangannya wajib tertulis di dekat definisi kolomnya.

### 3. Tumpang tindih antar-akun berbeda milik orang yang sama adalah SAH, ditandai bukan dihukum

Deteksi tumpang tindih yang ada **dipertahankan apa adanya** untuk pasangan `shop_id` dan `akun_live` yang sama. Itu tetap kesalahan input, dan tetap menolkan porsi host.

Untuk tumpang tindih pada **akun berbeda milik `employee_id` yang sama**, sistem menandainya sebagai keadaan **sah** dan **DILARANG menolkan porsi GMV-nya**.

Ini gerbang terpenting dalam keputusan ini. Memperluas deteksi tumpang tindih yang ada begitu saja ke lintas akun akan **menghanguskan GMV dari praktik kerja yang justru sah**, dan kegagalannya senyap: host melihat porsinya nol tanpa penjelasan, persis pada bulan ia bekerja paling keras. Dua keadaan ini wajib punya nama berbeda di data dan warna berbeda di layar.

### 4. GMV masuk ke departemen host, bukan departemen pemilik akun

Ketika seorang host menyiarkan di akun milik dua departemen sekaligus, seluruh GMV-nya diatribusikan ke departemen tempat orang itu terdaftar (`work_data.department`).

Konsekuensi yang diterima sadar: departemen yang akunnya dipakai **tidak menerima angka itu** pada penilaian per-orang.

Keputusan ini menjaga invarian [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]], yang menegakkan satu toko dimiliki satu departemen justru supaya satu omzet tidak terhitung di dua tempat dan menaikkan skor dua atasan sekaligus. Mengatribusikan ke kedua departemen akan melahirkan kembali persis kelas kegagalan yang invarian itu dibuat untuk mencegah, lewat pintu orang alih-alih pintu toko.

Kepemilikan toko tetap dibaca dari sumber yang sudah ada (`department_shops`), **jangan** diturunkan ulang dari nama akun.

### 5. Klien wajib menampilkan seluruh sesi berjalan milik pemanggil

Web dan mobile menampilkan N kartu sesi berjalan, masing-masing dengan tombol Jeda dan Akhiri sendiri, penghitung durasi sendiri, dan peringatan ambang sendiri. Mengambil elemen pertama dari daftar dilarang.

Ini bukan penyempurnaan tampilan melainkan **prasyarat fitur ini bisa dipakai sama sekali** oleh kru yang memegang banyak akun. Selama sesi kedua tidak bisa diakhiri, mencatatnya justru merugikan host lewat ambang 12 jam.

Dialog Mulai boleh memilih beberapa akun sekaligus dan menerbitkan N sesi dalam satu tindakan. Itu kemudahan di tampilan, **bukan** perubahan kontrak.

⛔ **Klien wajib mengurutkan sendiri.** `ShiftBerjalanSemua` memanggil `Find` **tanpa `SetSort`** (`live_shift_store.go`), jadi urutan yang dikirim tidak terdefinisi. Selama sesi hanya bisa satu, hal itu tidak berakibat apa-apa; begitu ada beberapa, permukaan mana pun yang menampilkan sebagian saja — kartu beranda mobile menampilkan **elemen pertama** — bisa berpindah akun antar-refresh, dan kartu di halaman penuh bisa bertukar tempat tepat saat host hendak menekan tombolnya. Urutan yang dipakai: **paling lama di depan**, karena dialah yang paling dekat ambang 12 jam, dengan `id` sebagai pemecah seri.

⛔ **Sinyal penutup dialog Mulai tidak boleh "ada sesi berjalan".** Syarat itu benar sewaktu sesi hanya bisa satu, tetapi dengan siaran serentak ia sudah terpenuhi **sebelum** akun berikutnya tersimpan: dialog menutup seketika dan host tidak pernah tahu akun keduanya jadi atau tidak. Yang benar adalah munculnya sesi ber-**id baru**, digabung dengan syarat bahwa pengiriman memang sudah terjadi — dialog yang dibuka selagi permintaan daftar sesi masih berjalan punya himpunan id awal kosong, sehingga sesi lama mana pun akan terhitung "baru".

⛔ **Konfirmasi mengakhiri sesi wajib menyebut akunnya.** Dengan beberapa kartu di layar, dialog konfirmasi menutupi kartu yang barusan ditekan; judul generik membuat host tidak punya cara memastikan ia mengakhiri sesi yang benar, sementara aksinya tidak bisa dibatalkan dan menutup atribusi GMV sesi itu.

### 6. Yang berhak melihat sesi orang lain mencakup IT, dan itu disengaja

Penyaringan "siapa melihat siapa" pada `/live-shifts/berjalan` maupun riwayat memakai satu predikat, `common.IsMarketingLeader`. Daftar peran di baliknya **memuat modul `it` pada tingkat staf ke atas**, di samping supervisor/admin kyura, beauty_hacks, integration, dan `insentive: adv_leader`.

Artinya staf IT melihat sesi berjalan dan riwayat seluruh host live, termasuk nama dan `employee_id` tiap orang. **Itu diterima sadar** (2026-08-30), dengan tiga alasan: IT memang yang menyelidiki saat angkanya janggal, akses baca itu sudah mereka miliki sebelum keputusan ini lewat gerbang rutenya sendiri, dan kartu performa tim di halaman ICC memang digerbang "marketing leader **atau** anggota IT" sehingga mempersempitnya justru mematikan kartu itu bagi mereka.

⚠️ Dicatat di sini karena berkas peran itu sendiri memperingatkan agar predikat ini **tidak** dipakai sebagai penanda SPV marketing, dan peringatan itu benar untuk keputusan **wewenang**. Yang dipakai di sini adalah keputusan **visibilitas baca**, dan hanya untuk itu. Wewenang menindak sesi tetap tidak mengikuti predikat ini (lihat §3): leader tak boleh menghentikan sesi orang lain, dan satu-satunya pengecualian ber-peran adalah **supervisor/admin IT** sebagai jalan darurat, bukan staf IT.

Konsekuensi yang harus diingat: **definisi leader di frontend dan backend TIDAK sama.** Padanan frontend tidak memuat `it`. Menyamakan keduanya tanpa memeriksa akan mematikan kartu performa tim ICC bagi anggota IT, karena merekalah yang lolos gerbang halaman itu lewat jalur `isItMember`.

### 7. Tidak diputuskan di sini

- **Pengelompokan sesi menjadi satu "blok siaran" yang tersimpan.** Ditolak untuk sekarang. Union jendela waktu sudah menjawab pertanyaan jam tanpa menyimpan fakta baru yang bisa menyimpang dari kenyataan, misalnya saat host membuka akun ketiga dua puluh menit kemudian.
- **Perhitungan dan pembayaran insentif.** Tidak disentuh keputusan ini. Peraturan Perusahaan diam soal insentif Host Live, jadi itu keputusan produk tersendiri yang butuh dasar tertulis lebih dulu.
- ⚠️ **TBD, dan perlu dibawa ke HRD, bukan diselesaikan di kode**: [[ADR - 0006 Swap Jadwal Same-Department]] berdiri di atas asumsi tiap shift host live wajib berisi satu Beauty Hacks dan satu Kyura, "bukan satu pool interchangeable", dan ADR itu **menuliskan sendiri** bahwa bila HRD menyatakan satu pool maka ia ditinjau ulang dan mungkin berstatus Superseded. Satu orang yang memegang akun Beauty Hacks dan Kyura serentak adalah bukti kuat ke arah satu pool. Keputusan 0063 ini **tidak** memutuskan hal tersebut dan tidak bergantung padanya, tetapi konsekuensinya harus diperiksa sebelum ADR 0006 dipakai sebagai dasar aturan tukar jadwal apa pun.

## Consequences

**Yang menjadi mungkin.** Penilaian KPI Host Live per orang menjadi mungkin untuk pertama kalinya, karena satu-satunya sumber yang tahu siapa memegang akun mana pada jam berapa adalah catatan host sendiri. Scope `individu` yang sudah terdaftar di template bisa dinyalakan HR tanpa deploy begitu koleksinya terisi.

**Target KPI wajib ikut diubah HR pada saat itu juga.** Angka per orang jauh lebih kecil daripada angka tim yang selama ini dilihat. Tanpa penyesuaian target, seluruh host mendadak tercatat gagal tanpa ada yang berubah pada kinerjanya. Peringatan ini sudah tertulis di sumber KPI-nya dan diulang di sini karena akibatnya menimpa orang. Perhatikan juga [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]: skor yang sudah dibekukan tidak dihitung ulang, jadi perpindahan scope wajib dilakukan di batas periode, bukan di tengah.

**Angka "jam siaran" berubah artinya, dan angka lama tidak bisa dibandingkan** dengan angka sesudah perubahan bagi host yang memegang banyak akun. Karena koleksinya masih nol dokumen, tidak ada data historis yang terdampak, dan ini satu-satunya kesempatan mengubahnya tanpa biaya.

**Dua notifikasi pengingat menjadi satu.** Dedup pengingat berpindah dari per dokumen sesi ke per orang per jenis pengingat.

**Beban autoclose naik linear** terhadap jumlah sesi paralel, karena resolusi clock-out ditanyakan per tanggal mulai. Skalanya kecil pada 14 orang, tetapi jangan dianggap gratis.

**Yang tetap tidak bisa dijawab sistem**: siapa memegang akun apa, bila host tidak menekan tombol. Keputusan ini tidak mengurangi ketergantungan itu sedikit pun, ia justru menaikkan taruhannya, karena angka yang lahir darinya sekarang dipakai menilai orang per orang.

**Risiko adopsi, dan ini yang terbesar.** Koleksinya nol dokumen selama fitur ini live di produksi. Membangun lantai dua di atas gedung yang belum pernah dimasuki orang adalah risiko nyata, dan keputusan ini menerimanya dengan satu syarat: perbaikan tampilan N sesi (§5) dikerjakan **lebih dulu** dan diverifikasi seorang host sungguhan, karena tanpa itu kru yang memegang banyak akun memang tidak punya jalan memakai fitur ini.

## Dokumen Terkait

- [[Microservices - Marketing Analytics Service]]
- [[API - Marketing Analytics Service]]
- [[Microservices - Employee Service]]
- [[HRIS - Otomasi Skor KPI]]
- [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]]
- [[ADR - 0006 Swap Jadwal Same-Department]]
- [[ADR - 0036 Roster Harian Menimpa Jadwal Dasar]]
- [[ADR - 0048 Skor KPI Otomatis Penuh Dibekukan Sistem]]
- [[APP - Web ERP]]
- [[APP - MyBharata]]

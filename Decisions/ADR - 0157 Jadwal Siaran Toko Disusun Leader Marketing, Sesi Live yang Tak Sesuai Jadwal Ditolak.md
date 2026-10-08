> **Status**: 🟡 **Diusulkan**, 2026-10-08. Belum ada kode. Rincian di `## Deskripsi`.

## Untuk Manajemen

**Yang berubah di layar.** Di web ERP ada menu baru **Jadwal Siaran Toko**. Leader atau SPV marketing mengisi, per tanggal, akun live mana yang siaran untuk toko mana. Satu toko boleh diisi beberapa akun, dan jadwal bisa disusun untuk beberapa hari ke depan. Jadwal sebuah tanggal bebas diubah sampai hari sebelumnya; pada hari-H masih bisa diubah, tetapi wajib menulis alasan. Jadwal itu juga tampil di Kalender web ERP.

Di aplikasi MyBharata tidak ada yang berubah. Host tetap memilih toko dan akun seperti sekarang. Bedanya, bila pilihannya tidak sesuai jadwal hari itu, sesi tidak dimulai dan host menerima notifikasi yang menyebut toko atau akun yang benar. Sepuluh menit sebelum jam shift-nya, host juga menerima notifikasi berisi jadwal siaran hari itu.

Bila ternyata jadwalnya sendiri yang keliru, sistem memberi tahu penyusun jadwal sesudah data penjualan TikTok masuk.

**Siapa yang terdampak.** Leader dan SPV marketing (pekerjaan baru: mengisi jadwal), host live (pilihan yang salah kini ditolak), dan Live Support serta pembaca KPI live (angka penjualan per sesi lebih jarang kosong).

**Yang tidak dijanjikan.**

- Pesan penolakan tidak tampil di layar Mulai aplikasi; di sana host hanya melihat pesan gagal umum. Penjelasannya datang lewat notifikasi inbox.
- Host yang membawakan akun yang dijadwalkan tetapi sebenarnya bukan akun yang sedang ia siarkan tetap lolos. Jadwal tidak memuat siapa host tiap akun.
- Pemberitahuan jadwal keliru datang paling lambat sekitar dua hari, mengikuti penarikan data TikTok.
- Sesi yang sudah telanjur salah tidak dibetulkan otomatis, dan skor KPI yang sudah final tidak ikut berubah.
- Tanggal yang belum dijadwalkan tidak dijaga jadwal; di sana berlaku penjaga lama.

**Besaran kerja.** Besar: empat bagian di backend dan satu layar baru di web. Aplikasi MyBharata tidak disentuh, jadi tidak ada rilis store.

## Deskripsi

*Leader marketing menyusun jadwal siaran per tanggal (akun live mana untuk toko mana), dan `POST /live-shifts` menolak pasangan toko dan akun yang tidak sesuai jadwal hari itu. Menyimpang dengan sengaja dari [[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]] §2 dan dari pola izin per posisi di [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]]; alasannya dicatat di bawah.*

- **Status**: 🟡 **Diusulkan**, 2026-10-08. Belum ada kode. Bentuknya disetujui pemilik produk di sesi analisa 2026-10-08; baris ini berubah jadi Diterima saat ia menuliskannya di sini.
- **Path di repo**: `bip-erp/services/marketing-analytics/jadwal_siaran*.go` (baru) · `bip-erp/services/marketing-analytics/live_shift_handler.go` dan `live_shift_ambil_alih.go` (penjaga jadwal) · `bip-erp/services/marketing-analytics/sync_live_sessions.go` (pemeriksaan sesudah sync) · `bip-erp/services/calendar/providers.go` (satu baris) · `erp-frontend/src/features/marketing/jadwal-siaran-toko/` (baru) · `erp-frontend/src/app/(main)/marketing/jadwal-siaran-toko/page.tsx` (baru)
- **Tanggal**: 2026-10-08

## Context

Penjualan sebuah sesi live tidak disimpan di sesinya. Ia dijodohkan **saat dibaca** ke siaran TikTok lewat toko, akun, channel, dan waktu yang beririsan (`jodohkanSesiDenganPorsi`, `services/marketing-analytics/live_shift_penjualan.go`). Akibatnya sesi yang dicatat dengan toko atau akun yang keliru tidak pernah terjodoh: layar menulis "belum ada data penjualan" selamanya, tanpa satu pun galat. Angka itu dasar KPI live per orang ([[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]]).

**Terukur di PROD 2026-10-08** (`marketing_analytics_db`, 1 September sampai 8 Oktober, 785 sesi TikTok):

- **10 sesi salah toko**, semuanya akun `carevolution.hub` antara `Beautyhacks.co` dan `Beautyhacks.store`. Pada 4 Oktober tiga host memilih toko yang berbeda untuk satu siaran yang sama. Akun itu pindah toko 5 Oktober, dan pada 1 Oktober sempat pindah di tengah hari.
- **5 sesi salah akun** dengan bukti kuat (pada jam itu ada siaran akun studio lain yang tak dicatat sesi mana pun), porsi GMV sekitar Rp 5 juta. Salah toko sekitar Rp 1,3 juta.
- Seluruhnya ditemukan lewat pengecekan manual dan dibetulkan lewat skrip tulis ke database oleh manusia.

**Kenapa penjaga yang ada tidak menangkapnya.** `akunMilikToko` (`live_shift_akun_toko.go`) menolak akun yang dikenal tetapi tak pernah bersiaran di toko yang dipilih, dengan jendela 14 hari. Ia berpijak pada **riwayat**: akun yang sedang pindah toko punya siaran baru di dua toko sekaligus, sehingga dua-duanya sah. Ia juga tidak memeriksa apakah akun itu memang yang sedang tayang. Dua hal lain memperlemahnya, keduanya terukur di `origin/dev` MyBharata 2026-10-08: aplikasi tidak menampilkan pesan penolakan dari server (`_mapMulaiError` memakai reason phrase HTTP, bukan `data.error`), dan aplikasi tidak pernah mengirim `konfirmasi_toko`.

**Yang tidak dimiliki sistem** adalah tempat menyimpan fakta "akun ini siaran untuk toko itu". Fakta itu hari ini hanya lahir saat host menekan Mulai, dan [[Microservices - Marketing Analytics Service]] mencatatnya sebagai lubang yang belum diputuskan. Jadwal Host Live di attendance hanya memuat orang dan jam shift.

**Cara kerja orangnya sekarang.** Leader membagi pekerjaan siaran tiap hari di luar sistem. Jadi jadwal di ERP memindahkan pekerjaan yang sudah ada, bukan menambah pekerjaan baru.

**Yang diminta pemilik produk** (2026-10-08): leader/SPV menyusun jadwal penuh beberapa hari ke depan sesuai strategi, final paling lambat sehari sebelumnya; host melihatnya di kalender web ERP; pilihan yang salah ditolak dengan pesan spesifik; host diberi tahu sepuluh menit sebelum shift; dan **MyBharata tidak diubah**.

Aturan bisnis perusahaan (`BUSINESS_LOGIC_IMPLEMENTATION.md` di repo MyBharata) tidak memuat ketentuan host live, dan service insentif maupun payroll tidak membaca sesi live sama sekali (diukur 2026-10-08), jadi dampak uangnya hanya lewat KPI.

## Decision

### 1. Jadwal siaran disimpan per tanggal, per toko, per akun

Koleksi baru `jadwal_siaran_toko` di marketing-analytics. Satu dokumen = satu akun live dijadwalkan untuk satu toko pada satu tanggal WIB: `tanggal` (`YYYY-MM-DD`, WIB), `channel`, `shop_id`, `akun_live`, `departemen`, `dibuat_oleh`, `dibuat_pada`, `diubah_oleh`, `diubah_pada`.

- **Satu toko boleh banyak akun; satu akun hanya satu toko per tanggal.** Index unik `(tanggal, channel, akun_live)`. Tanpa itu penjaga di §3 tidak punya jawaban tunggal.
- `channel` dan `departemen` **distempel server** dari `department_shops`, tidak diterima dari body, pola yang sama dengan `live_shifts.channel` ([[ADR - 0086 Metrik Live Lintas Channel Digabung Satu Angka, Rincian Tetap per Channel]] §3).
- `akun_live` teks bebas dengan validasi karakter yang sama dengan sesi, supaya akun yang benar-benar baru bisa dijadwalkan sebelum punya riwayat siaran.
- Marketing-analytics pemiliknya, karena seluruh fakta akun live lain (`live_shifts`, `mart_live_sessions`) sudah tinggal di sana. Menaruhnya di integration di samping `department_shops` ditimbang dan ditolak: itu menjadikan dua service naik bersama untuk satu fitur.

### 2. Jadwal tanggal D bebas diubah sampai D-1; pada hari-H wajib beralasan; tanggal lampau terkunci

- Selama belum pukul 00.00 WIB tanggal D, jadwal tanggal D ditulis tanpa syarat.
- Sejak 00.00 WIB tanggal D sampai akhir hari itu, setiap perubahan wajib membawa `alasan` (tidak kosong) dan dicatat di `jadwal_siaran_toko_jejak` (append-only: siapa, kapan, isi sebelum, isi sesudah, alasan).
- Tanggal yang sudah lewat tidak bisa diubah (400).

"Final H-1" jadi **aturan dengan jalan darurat yang berjejak**, bukan kunci mati. Kunci mati membuat strategi yang berubah pagi itu menolak host untuk siaran yang sebenarnya benar, dan sesinya tidak tercatat sama sekali.

### 3. Mulai dan ambil alih dicocokkan dengan jadwal hari itu

Berjalan sesudah penurunan `channel`, memakai tanggal WIB saat permintaan tiba:

| Keadaan | Hasil |
|---|---|
| Akun punya baris jadwal hari itu, tokonya **sama** dengan yang dipilih | Lolos. Penjaga 14 hari **dilewati**: jadwal menang atas riwayat, jadi akun yang baru pindah toko tidak lagi butuh `konfirmasi_toko` |
| Akun punya baris jadwal hari itu, tokonya **beda** | **400**: "Akun X hari ini dijadwalkan untuk toko Y, bukan Z. Pilih toko Y lalu ulangi." |
| Akun tidak dijadwalkan hari itu, tetapi toko yang dipilih **punya** jadwal hari itu | **400**: "Akun X tidak dijadwalkan hari ini. Jadwal toko Z hari ini: akun A, B. Hubungi leader bila jadwalnya perlu diubah." |
| Akun tidak dijadwalkan dan toko yang dipilih **tidak punya** jadwal hari itu | Perilaku lama: penjaga 14 hari (`akunMilikToko`) |
| Jadwal tidak terbaca | Perilaku lama, dan dicatat di log. Gagal-terbuka |

Nama toko di pesan diambil dari sumber yang sama dengan pemilih (`namaTokoUntukPesan`).

**Ini menyimpang dari [[ADR - 0101 Kesiapan Siaran Dicatat Host saat Mulai sebagai Dasar KPI Live Support]] §2** ("menahan, tapi boleh dilanjut dengan alasan"). Penyimpangannya disengaja dan sempit: yang ditolak hanya pilihan yang **bertentangan dengan jadwal yang ada**, dan pesannya menyebut pilihan yang benar, sehingga host dapat langsung mengulang. Tanggal atau toko tanpa jadwal, dan gangguan baca, tetap tidak mematikan pencatatan.

### 4. Pesan penolakan dikirim ke inbox host, karena aplikasinya tidak diubah

Saat menolak karena jadwal, server mengirim pesan yang sama ke inbox pemanggil lewat `kirimInbox` yang sudah ada (`live_shift_pengingat.go`), kategori **`reminder`**. Penolakan identik yang berulang dalam dua menit tidak mengirim inbox kedua.

Kategori `reminder` dipakai ulang dengan sengaja: kategori baru menuntut daftar-izin di notification-service **dan** pemetaan label di MyBharata, sedangkan MyBharata diputuskan tidak disentuh. Konsekuensinya notifikasi ini berlabel pengingat.

### 5. Wewenang: leader marketing, hanya untuk toko departemennya

Tulis: `common.IsMarketingLeader`, dan pemanggil yang bukan IT hanya boleh menulis toko yang `department_shops.department`-nya sama dengan departemennya (header gateway). Baca: leader marketing dan pemakai sesi live (`RequireLiveShiftUser`), disaring ke toko departemennya.

**Ini menyimpang dari pola [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]]**, yang menolak "SPV marketing" sebagai dasar wewenang jadwal dan memilih izin per posisi. Pemilik produk memutuskan wewenang jadwal siaran mengikuti jabatan (2026-10-08). Presedennya Kepemilikan Toko di ICC Management, yang juga digerbang leader marketing per departemen. Yang dimaksud "SPV/leader" adalah peran leader marketing di hak akses modul, **bukan** `work_data.is_supervisor`.

### 6. Host diberi tahu sepuluh menit sebelum shift-nya

Tik latar di marketing-analytics (selang lima menit). Untuk tiap host yang jam mulai shift-nya hari itu jatuh dalam sepuluh menit ke depan, kirim satu inbox `reminder` berisi jadwal siaran hari itu: tiap toko beserta akunnya.

- Jam shift dari `GET /internal/jadwal-resolusi` attendance, rute yang sudah dipakai sesi live.
- **Daftar host dan tokonya diturunkan dari sesi live 30 hari terakhir**: host yang pernah tercatat di `live_shifts.host[]`, dan toko-toko milik departemen tempat ia bersiaran. Marketing-analytics sengaja tidak memanggil employee-service ([[REF - Kepemilikan Data]]), dan jadwalnya tidak memuat host.
- Sekali per host per tanggal. Tidak dikirim bila tidak ada jadwal siaran hari itu untuk toko-tokonya.

### 7. Pemeriksaan sesudah sync, karena jadwal pun bisa salah

Di akhir job `sync-live-sessions` yang sukses: cari sesi dalam jendela sync yang sudah selesai, tak terjodoh di tokonya, **padahal** ada siaran TikTok akun yang sama di toko lain yang beririsan waktunya. Untuk tiap sesi kirim satu inbox `reminder` ke penyusun jadwal toko itu (pengubah terakhir jadwal toko pada tanggal sesi; bila tak ada, pengubah terakhir jadwal toko itu kapan pun; bila tak pernah ada, tidak dikirim dan dicatat di log). Sesi ditandai `notif_salah_toko_pada` supaya tidak dikabari dua kali.

Hanya salah toko yang dikabari. Salah akun tidak, karena buktinya tidak pasti: pada jam yang sama sering ada lebih dari satu siaran yang belum dicatat.

### 8. Jadwal siaran masuk Kalender terpusat, tanpa halaman kalender baru

Marketing-analytics didaftarkan sebagai sumber di `providerRegistry` calendar-service dan menyediakan `GET /internal/calendar-feed?from&to` dengan `kind: jadwal_siaran`. Satu item per tanggal per toko, `all_day: true`, judul "Siaran <nama toko>: <akun, akun>", `id` berprefiks sumber, `deep_link` ke menu Jadwal Siaran Toko pada tanggal itu.

Visibilitas dijawab **di service sumber**: item hanya untuk pemakai sesi live dan leader marketing, dan hanya toko departemen pemanggil. Ini lapis "pekerjaan sendiri" dari prinsip tiga lapis kalender ([[Microservices - Calendar Service]]). `/internal/` bukan privat, jadi feed memeriksa identitas pemanggil sendiri.

Kalender pernah menolak memuat shift karena shift keadaan sehari-hari. Jadwal siaran berbeda: ia berubah mengikuti strategi, dan justru perubahannya yang perlu dilihat host.

### 9. MyBharata tidak diubah

Tidak ada layar jadwal, tidak ada perubahan dialog Mulai, tidak ada perbaikan pembacaan pesan galat. Semua yang perlu sampai ke host lewat inbox yang sudah ada.

## Consequences

**Yang membaik.** Keputusan "akun ini untuk toko itu" diambil satu orang, sekali, dan tertulis. Salah toko pada tanggal berjadwal berhenti di pintu, bukan ditemukan berminggu-minggu kemudian. Akun yang pindah toko tidak lagi bergantung pada riwayat 14 hari.

**Yang diterima sadar.**

- ⚠️ **Penolakan tampil sebagai galat umum di layar Mulai.** Host yang tidak membuka inbox tidak tahu sebabnya. Ini harga dari tidak menyentuh MyBharata, dan menutupnya kelak cukup dengan membaca `data.error` di `_mapMulaiError`.
- ⚠️ **Jadwal yang keliru menolak host yang benar**, untuk semua sesi akun itu hari itu. Jalan keluarnya perubahan hari-H beralasan (§2), dan jaring pengamannya §7.
- ⚠️ **Tanggal tanpa jadwal tidak terjaga.** Hari ketika leader lupa mengisi berperilaku persis seperti sebelum keputusan ini.
- ⚠️ **Salah akun hanya tertutup sebagian**: akun yang tidak dijadwalkan ditolak, tetapi host yang memilih akun terjadwal lain tetap lolos.
- ⚠️ **Pindah toko di tengah hari tidak dimodelkan.** Satu akun satu toko per tanggal; perpindahan tengah hari ditangani dengan mengubah jadwal hari-H, dan sesi sebelum perubahan tetap atas toko lama.
- ⚠️ **Sesi yang dimulai lewat tengah malam** dicocokkan dengan jadwal tanggal baru.
- ⚠️ **Host yang belum pernah mencatat sesi** tidak menerima pengingat sepuluh menit sampai sesi pertamanya, karena daftar host diturunkan dari sesi.
- ⚠️ **Pembetulan sesi yang telanjur salah belum punya layar.** Tetap skrip oleh manusia, seperti yang dicatat [[ADR - 0088 Ambil Alih Sesi Live oleh Host Terjadwal dan Tutup Otomatis Akhir Shift]].

**Deploy.**

- Backend sebelum frontend.
- calendar-service ikut naik, dan env `MARKETING_ANALYTICS_MODULE_URL` di blok `calendar-service` compose baru terbaca bila container-nya **dibuat ulang** (`--force-recreate`), bukan `restart`.
- notification-service tidak perlu naik: tidak ada kategori inbox baru.

**Dok terkait.** Cara kerjanya di [[Microservices - Marketing Analytics Service]] § Jadwal Siaran Toko; rute di [[API - Marketing Analytics Service]]; layar di [[APP - Web ERP]]; pemilik fakta di [[REF - Kepemilikan Data]].

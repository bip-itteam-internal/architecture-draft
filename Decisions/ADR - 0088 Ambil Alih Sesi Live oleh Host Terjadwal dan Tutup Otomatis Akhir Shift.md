## Untuk Manajemen

- **Yang berubah di layar**: host yang menekan Mulai pada akun yang masih tercatat dipakai orang lain akan melihat siapa pemegangnya dan sejak jam berapa. Bila jadwalnya sendiri sedang berjalan, ia bisa menekan **Ambil alih**. Pemegang langsung menerima notifikasi, dan bila halaman Sesi Live di MyBharata sedang terbuka, muncul jendela yang menyebut siapa yang meminta, dengan tombol Setujui dan Tolak serta hitungan mundur 30 detik. Bila disetujui, atau tidak dijawab dalam 30 detik, sesi lama ditutup dan sesi peminta langsung dimulai; bila ditolak, permintaan gugur. Sesi yang lupa diakhiri dan tidak dilanjutkan siapa pun tertutup sendiri satu jam setelah shift pemiliknya berakhir, dan pengingat 30 menit sebelumnya menyebut jam penutupannya. Riwayat menampilkan "Diambil alih oleh ..." atau "Ditutup otomatis: shift berakhir".
- **Siapa terdampak**: host live dan live support, serta pengelola jadwal Host Live, karena kedua aturan membaca jadwal. Atasan host semula direncanakan ikut diberi tahu saat sesi diambil alih; itu **ditunda** (revisi 2026-09-11, lihat §5). Tidak menyentuh absensi, penggajian, insentif, maupun karyawan di luar host live.
- **Tidak dijanjikan**: sistem tetap tidak tahu siapa yang benar-benar tampil di kamera; yang tercatat adalah siapa yang menekan tombol. Ambil alih tidak bisa dimundurkan, jadi penjualan sebelum ambil alih berlaku tetap milik host lama. Persetujuan hanya bisa diberikan dari MyBharata, dan pemegang yang tidak menjawab dalam 30 detik dianggap setuju, termasuk yang sedang siaran tapi tidak melihat ponselnya. Porsi yang sudah hangus di masa lalu tidak dikoreksi lewat layar. Host yang jadwalnya tercatat salah tidak bisa mengambil alih, dan sesinya tidak tertutup otomatis, sampai jadwalnya dibetulkan. Atasan tetap tidak bisa menghentikan sesi orang lain.
- **Besaran kerja**: sedang. Di backend ada dua bagian: tutup otomatis akhir shift (kecil, bisa naik lebih dulu, dan sendirian sudah mencegah kejadian 11 September) dan ambil alih dengan persetujuan 30 detik (sedang, karena ada permintaan yang menunggu jawaban). Tombolnya di MyBharata dibangun di atas layar penolakan yang sudah direncanakan; tombol versi web batal sejak halaman web Sesi Live Host dihapus 2026-09-11 ([[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]]). MyBharata mengerjakan dua sisi, peminta yang menunggu jawaban dan pemegang yang menerima jendela persetujuan, lalu perlu rilis versi baru. Tidak ada migrasi data.

## Deskripsi

*Sesi Live Host yang ditinggal terbuka tidak lagi menahan akunnya sampai IT turun tangan. Dua jalan ditambahkan: host yang jadwalnya sedang berjalan boleh meminta **ambil alih** akun itu dari penolakan Mulai, pemegang punya 30 detik untuk menolak, dan bila ia menyetujui atau diam, sesi lama ditutup dengan jejak siapa yang mengambil alih; dan sesi yang tetap terbuka **tertutup sendiri satu jam setelah shift pemiliknya berakhir**. Keputusan produk 2026-08-30 bahwa leader tak boleh menghentikan sesi orang lain direvisi sempit: pengecualian barunya hanya host terjadwal, dan hanya lewat Mulai pada akun yang sama.*

- **Status**: ⚠️ **Sebagian berlaku** (2026-09-12): §1 di PROD; §2 kodenya selesai dan sudah direview di dua branch yang **belum di-push**. Arahnya disetujui 2026-09-11 lewat `/analisa-kebutuhan`. **§1 di PROD sejak 2026-09-11** (bip-erp [#1847](https://github.com/bip-itteam-internal/bip-erp/pull/1847) sebagai `marketing-analytics-service` 16:55 WIB, erp-frontend [#1539](https://github.com/bip-itteam-internal/erp-frontend/pull/1539) sebagai `frontend-hris` 16:59 WIB); gerbang biner dan bundel lolos, bukti perilaku pertama dan verifikasi DEV belum ada. **§2**: bip-erp branch `feat/marketing-analytics-ambil-alih` (7 commit) dan my-bharata branch `feat/live-shift-ambil-alih` (versi 1.17.0+161); belum PR, belum merge, belum di DEV maupun PROD. §2 direvisi di hari yang sama: ambil alih meminta persetujuan pemegang dengan batas 30 detik, dan diam berarti setuju. Berdiri di atas pengukuran prod 2026-09-11 dan di atas [[Microservices - Marketing Analytics Service]] yang berstatus ⚠️ Implemented dengan catatan, bukan di atas dok konsep. Papan kerja: `Workspace/ANALISA - Ambil Alih Sesi Live Host.md` (tidak diterbitkan). **Revisi 2026-09-11** ([[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]]): bagian web dicabut, yaitu badge alasan penutupan di riwayat web (§1), riwayat web (§4), dan tombol Ambil alih web (T3); halaman web Sesi Live Host dihapus. **Revisi 2026-09-11 saat perencanaan §2**: pemberitahuan ke atasan ditunda (§5), dan cara-cara yang semula diserahkan ke `/plan` kini tertulis di §2. **Revisi 2026-09-12 saat review**: konfirmasi Ambil alih tidak menyebut angka detik (§4).
- **Path di repo**: `bip-erp/services/marketing-analytics/live_shift_autoclose.go` · `live_shift_handler.go` · `live_shift_entity.go` · `live_shift_pengingat.go` · `live_shift_jadwal.go` (§1, `terapkanVonisJadwal`) · `live_shift_ambil_alih.go` (baru, §2) · `erp-frontend/src/features/marketing-analytics/components/live-shift/tabel-riwayat-live.tsx` · `label-tutup-otomatis.ts` (baru, §1) · `erp-frontend/src/features/marketing-analytics/components/live-shift/dialog-mulai.tsx` (ketiga berkas erp-frontend dihapus 2026-09-11, [[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]]) · `mybharata-app/lib/src/features/live_shift/data/datasources/live_shift_remote_datasource.dart` · `mybharata-app/lib/src/features/live_shift/domain/failures/sesi_dipegang_failure.dart` (baru) · `mybharata-app/lib/src/features/live_shift/presentation/bloc/ambil_alih/` (baru) · `mybharata-app/lib/src/features/live_shift/presentation/widgets/dialog_mulai_live.dart` · `panel_akun_dipegang.dart` (baru) · `jendela_persetujuan_ambil_alih.dart` (baru) · `mybharata-app/lib/src/features/live_shift/presentation/pages/live_shift_page.dart` (jendela persetujuan dan label riwayat)
- **Tanggal**: 2026-09-11

## Context

### Kejadian yang memicu (10 ke 11 September 2026)

Host shift malam (16:00 sampai 24:00) lupa mengakhiri sesinya di `glowboosterofficial.id` dan tidak absen pulang. Siaran TikTok-nya berakhir 23:50, tetapi sesinya tetap tercatat berjalan sampai 09:11 keesokan harinya, 13 jam 8 menit. Host shift pagi ditolak **409** dari 07:00 sampai 09:11. Siarannya sendiri tetap berjalan di TikTok; yang terhalang adalah **pencatatannya**.

Akibatnya berantai, dan tak satu pun berbunyi sebagai galat:

1. Penjodohan GMV hanya memakai toko, akun, channel, dan irisan waktu, **tanpa melihat host** (`jodohkanSesiDenganPorsi`, `live_shift_penjualan.go:150-176`), jadi penjualan pagi itu menempel ke sesi malam.
2. Begitu sesi lewat 12 jam, ia ditandai `perlu_koreksi` dan porsi GMV **seluruh** sesi dinolkan (`RingkasShift`, `live_shift_penjualan.go:206-212` dan `:236-239`).
3. Satu-satunya perbaikan adalah tulis DB prod oleh manusia. Porsi host malam, sekitar Rp 1,99 juta, baru kembali setelah `selesai` dikoreksi ke jam akhir sesi TikTok-nya.

### Kenapa tidak ada jalan keluar hari ini

| Penahan | Kode |
|---|---|
| Satu akun satu sesi berjalan: index unik parsial `{akun_live}` berfilter `selesai: null`, ditambah pra-cek 409 yang menyertakan `shift_berjalan` | `index.go:306-309`, `live_shift_handler.go:253-262` |
| Yang boleh mengakhiri sesi hanya host sesi itu, pembuatnya, dan supervisor/admin IT. Leader sengaja tidak (keputusan produk 2026-08-30, [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] §6) | `bolehKelolaSesi`, `live_shift_handler.go:389-398` |
| Tutup otomatis hanya saat **seluruh** host sudah absen pulang. Host tanpa clock-out membuat sesi tetap terbuka, tanpa batas atas. Hidup di prod baru sejak deploy bip-erp #1835 (2026-09-11 11:30 WIB); sebelumnya setiap panggilan ke attendance dibalas 401 | `waktuTutupSesi`, `live_shift_autoclose.go:87-125` |
| Pengingat `shift_usai` dan `jam_10` hanya dikirim ke host sesi itu, bukan ke host yang tertahan | `live_shift_pengingat.go:175-177` |
| Data pemegang di badan 409 dibuang oleh web maupun MyBharata, dan `GET /berjalan` menyaring per pemilik, jadi host lain tak pernah melihat sesi pemegang | penolakan Mulai di kedua klien |

Supervisor IT memang bisa mengakhirinya, tetapi jam selesainya adalah jam tombol ditekan, dan pada pukul 07:00 tidak ada IT yang berjaga.

### Pengukuran produksi 2026-09-11 (58 sesi, 9 sampai 11 September)

| Ukuran | Angka |
|---|---|
| Pergantian ke host lain pada akun yang sama | **40**; 32 bersambung dalam 1 menit, 19 berpola A ke B lalu kembali ke A (istirahat digantikan) |
| Bila pemegang lupa dan jalan keluarnya **hanya** tutup otomatis +60 menit | 34 kasus: host berikutnya tertahan **median 239 menit, maksimum 450**, 24 kasus di atas 2 jam. 6 kasus sisanya pemegang di luar shift, sehingga tutup otomatis tak pernah berlaku |
| Sesi tertutup yang berakhir lewat jam shift berakhir + 60 menit | **0 dari 45** (paling molor 2,8 menit). Satu-satunya yang akan terpotong adalah sesi insiden di atas sebelum dikoreksi: tertutup 01:00, shift pagi bebas mulai 07:00 |
| Sesi tertutup tanpa jadwal yang cocok (host di luar shift) | 8 dari 53, seluruhnya satu host yang jadwalnya tak cocok dengan jam kerjanya |

Dua hal dibaca dari angka itu. **Tutup otomatis di akhir shift saja tidak cukup**: serah terima umumnya terjadi di **tengah** shift pemegang (12:00, 14:00, 17:30), jauh sebelum shift-nya usai. **Aturan +60 menit hampir tak memotong siaran yang sah**: lembur siaran sesudah shift di sampel ini hanya hitungan menit.

⚠️ **Batas ukuran, dinyatakan terang**: sampelnya 3 hari, sejak fitur ini dipakai sungguhan (9 September). Siaran lembur lebih dari 60 menit **belum pernah terjadi** di sampel, belum terbukti tak pernah terjadi.

### Istirahat bolak-balik bukan kebutuhan baru

Permintaan awal juga menyebut host yang istirahat lalu digantikan sementara. Itu **sudah berjalan** lewat Akhiri lalu Mulai (19 kejadian A ke B ke A di atas), dan atribusinya sudah benar: penjodohan membagi GMV per potongan waktu, jadi tiap host menerima penjualan jam siarannya sendiri. Ambil alih kebetulan menyederhanakannya dari dua tekan oleh dua orang menjadi satu tekan, tetapi itu bukan alasan membangunnya.

### Dua jalan pintas yang tampak wajar, dan kenapa salah

- **Menambahkan pengganti ke `host[]`.** `host[]` berarti co-host: porsi seluruh sesi dibagi rata ke semua host (`BagiRata`, `live_shift_entity.go`), jadi pengganti menerima 1/n GMV **seluruh** sesi, termasuk jam sebelum ia datang.
- **Jeda sambil digantikan.** Jeda tidak melepas akun, karena index tetap menahan sesi lain. Jeda juga tidak mengurangi porsi: penjodohan hanya memakai rentang mulai sampai akhir (`live_shift_penjualan.go:150-157`), jadi GMV selama jeda tetap milik yang menjeda.

### Akibat bila atribusinya salah

Porsi per host menjadi realisasi KPI individu bila template memakai scope `individu` ([[HRIS - Otomasi Skor KPI]]), yang dipakai untuk evaluasi dan kenaikan gaji. Porsi itu **tidak** mengalir ke uang: insentive-service dan payroll tidak membaca data live sama sekali (`git grep` atas `origin/main` bb350062 bersih), dan [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] mencatat skema Host Live belum punya sumber angka di sistem.

Gerbang aturan bisnis: `mybharata-app/docs/development/BUSINESS_LOGIC_IMPLEMENTATION.md` tetap diam soal host, live, dan GMV (temuan yang sama dengan ADR 0063). Dua ikatan yang dicatat ADR 0063 tetap berlaku di sini: jam siaran tidak menjadi jalur lembur, dan vonis luar shift tidak dialirkan ke jalur disiplin. Keputusan ini memakai jadwal hanya sebagai **gerbang dan batas waktu**, bukan untuk menilai kedisiplinan siapa pun.

## Decision

### 1. Tutup otomatis kedua: jam berakhir shift + 60 menit

Sesi berjalan yang melewati **jam berakhir shift + 60 menit** ditutup dengan `selesai` tepat di batas itu, `ditutup_otomatis: true`, dan alasan `shift_berakhir`.

- **`selesai` diisi batasnya, bukan jam tik.** Tik berjalan tiap 10 menit, jadi jam tik bisa telat sampai 10 menit dan menyerahkan menit-menit itu ke host lama. Batas yang pasti juga membuat hasilnya sama persis walau pemicunya jalur lazy `GET /berjalan`.
- **Aturan clock-out yang ada tetap berlaku dan menang bila lebih awal**: bila seluruh host sudah absen pulang sebelum batas itu, `selesai` tetap clock-out terakhir seperti sekarang.
- **Jam berakhir yang dipakai adalah yang PALING AKHIR di antara host yang tervonis `dalam_shift`.** Sekarang `jam_shift_berakhir` diambil dari host pertama yang jadwalnya ketemu (`live_shift_handler.go:294-308`); untuk co-host beda shift itu akan memotong sesi saat shift host lain belum usai. Pengingat `shift_usai` membaca nilai yang sama, jadi keduanya tetap konsisten.
- **Sesi tanpa jam berakhir tidak tersentuh.** `JamBerakhir` hanya terisi saat host tervonis `dalam_shift` (`live_shift_jadwal.go:334-337`), jadi sesi yang seluruh host-nya `luar_shift` atau `tak_diketahui` tetap bergantung pada clock-out, pengingat jam ke-10, dan ambil alih (§2). Gerbang ambil alih membaca jadwal **pengambil alih**, bukan pemegang, jadi sesi semacam ini tetap bisa dilepas.
- **Kenapa +60, bukan tepat di jam berakhir**: host yang lembur sebentar tetap mendapat penjualannya (0 dari 45 sesi di sampel molor lebih dari 3 menit). **Kenapa bukan lebih lama**: tiap menit tambahan adalah menit host berikutnya tertahan bila ia tak mengambil alih.
- **Host diberi tahu** bahwa sesinya ditutup dan harus menekan Mulai lagi bila masih siaran.
- **Pengingat `shift_usai`** (jam berakhir + 30 menit) menyebut jam tutup otomatisnya, supaya host tahu setengah jam sebelumnya.
- **Riwayat web membedakan alasan penutupan** ("shift berakhir" atau "clock-out"). Sebelum keputusan ini badge-nya berbunyi "Ditutup otomatis (clock-out)" untuk setiap `ditutup_otomatis`, jadi aturan baru tanpa perubahan layar akan menyebut clock-out untuk sesi yang tidak pernah di-clock-out. Sesi lama tanpa alasan tetap memakai teks lama. Riwayat web itu dihapus 2026-09-11 bersama halamannya ([[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]]).

### 2. Ambil alih oleh host yang jadwalnya sedang berjalan

Dari penolakan 409 saat Mulai, host bisa meminta ambil alih akun itu. Pemegang sesi diberi **30 detik untuk menolak**; persetujuan atau diam membuat ambil alih berjalan. (Revisi 2026-09-11 atas rancangan awal hari yang sama, yang tanpa persetujuan sama sekali.)

1. **Menggerbang, lalu mencatat permintaan.** Pemanggil lolos `RequireLiveShiftUser`, **termasuk host sesi baru** (tak bisa mengambil alih atas nama orang lain), dan jadwalnya tervonis `dalam_shift` pada detik itu oleh resolusi jadwal yang sama dengan Mulai. Permintaan membawa **id sesi yang ditampilkan** di layar penolakan; bila pemegangnya sudah berganti, jawabannya 409 baru, bukan meminta sesi yang tak pernah dilihat penekannya. Resolusi jadwal gagal atau `tak_diketahui` berarti **ditolak**, dengan pesan yang menyebut sebabnya dan jalan daruratnya (supervisor IT). Gerbang ini sengaja gagal-tertutup karena yang dipertaruhkan adalah atribusi orang lain. Yang lolos menjadi **permintaan yang menunggu**, satu per sesi, dengan batas 30 detik menurut **jam server**, bukan jam ponsel. Permintaan disimpan **di dokumen sesi lama** (diputuskan saat perencanaan 2026-09-11): satu per sesi dengan sendirinya, dan tiap transisinya atomik lewat filter pada dokumen yang sama.
2. **Meminta persetujuan pemegang.** Seluruh host sesi lama menerima notifikasi, dan halaman Sesi Live MyBharata yang sedang terbuka menampilkan jendela bawah (bottom sheet) **otomatis** berisi siapa yang meminta (nama, jadwal, akun), tombol **Setujui** dan **Tolak**, dan hitungan mundur. Jendela itu tertutup sendiri saat 30 detik habis, dan **tidak bisa ditutup lebih awal** lewat usap atau tombol kembali, karena jendela yang tertutup tak sengaja berarti diam. Peminta melihat keadaan menunggu dengan hitungan mundur yang sama. Cara halaman mengetahui permintaan (diputuskan saat perencanaan 2026-09-11): **halaman memoll daftar permintaan yang menunggu tiap 3 detik** selama terbuka dan aplikasi di depan, bukan pesan push, karena push ponsel tidak membawa pembeda ([[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]] §4).
3. **Jawaban.** **Setujui** menjalankan ambil alih seketika. **Tolak** menggugurkan permintaan, dan peminta diberi tahu siapa yang menolak. **Tak dijawab dalam 30 detik berarti setuju**: justru pemegang yang lupa atau tak di tempat adalah kasus yang memicu keputusan ini, jadi diam tidak boleh berarti tolak. Eksekusi karena batas waktu hanya berlaku bila peminta **masih menunggu**. Buktinya (diputuskan saat perencanaan 2026-09-11) adalah **pembacaan status oleh peminta sendiri** yang tiba dalam **20 detik** sesudah batas; lewat tenggang itu permintaan kedaluwarsa dan sesi pemegang tidak disentuh. Timer di server sengaja tidak dipakai: ia tak membuktikan peminta masih menunggu, dan hilang saat service restart.
4. **Menjalankan ambil alih.** Gerbang diperiksa ulang saat eksekusi (peminta masih terjadwal, sesi lama masih sama dan masih berjalan). Sesi lama ditutup: `selesai` = detik eksekusi, jeda yang masih terbuka ikut ditutup, dengan filter `selesai: null` seperti Akhiri (yang kalah balapan menerima 409). Tercatat siapa yang mengakhiri (`employee_id` pengambil alih), alasannya `ambil_alih`, dan cara persetujuannya (disetujui atau tak dijawab). Sesi baru dimulai pada instan yang sama; dua sesi yang bersentuhan tepat tidak dihitung tumpang tindih (`TandaiShiftTumpangTindih`, `live_shift_penjualan.go:286-321`), jadi tak satu pun ditandai `perlu_koreksi`.
5. **Memberi tahu** seluruh host sesi lama bahwa sesinya sudah diambil alih. Pemberitahuan ke atasan langsung mereka **ditunda** (revisi 2026-09-11, lihat §5).

Ketentuannya:

- **Tidak bisa mundur.** Tak ada pilihan jam; penjualan sebelum detik eksekusi (bukan detik permintaan) tetap milik host lama. Klaim atas GMV orang lain karena itu terbatas ke depan, dan terlihat: pemegang yang masih siaran bisa menolak dalam 30 detik, host lama diberi tahu, dan jejaknya tampil di riwayat.
- **Satu permintaan per sesi.** Permintaan kedua selama yang pertama menunggu dijawab 409 yang menyebut peminta pertama.
- **Boleh di tengah shift pemegang.** Tidak mensyaratkan shift pemegang sudah usai, karena justru di situ serah terima terjadi (24 dari 34 kasus tertahan lebih dari 2 jam karena pemegang masih di tengah shift). Mensyaratkannya membuat ambil alih tak berguna untuk pola yang paling sering.
- **Tidak dibatasi departemen atau brand toko.** Siaran lintas toko dan departemen sah, dan GMV-nya masuk ke departemen host ([[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] §4).
- **Persetujuan berbatas waktu, bukan tanpa batas** (diputuskan 2026-09-11). Yang meninggalkan sesi justru orang yang tak bisa dihubungi; persetujuan yang menunggu sampai dijawab mengembalikan masalah yang sama. 30 detik cukup bagi pemegang yang masih memegang ponsel untuk menolak, dan cukup pendek sehingga host berikutnya tidak benar-benar tertahan.
- **Dua tulisan, bukan satu transaksi.** Bila sesi lama sudah tertutup tetapi sesi baru kalah balapan dari host lain, penekan menerima 409 yang menyebut pemegang barunya. Keadaan itu sah (akunnya memang sedang dipegang orang lain), tapi wajib dikunci test dan tidak boleh berbunyi 500.

### 3. Yang TIDAK berubah dari keputusan 2026-08-30

- **`bolehKelolaSesi` tetap.** Jeda dan Akhiri sesi orang lain tetap hanya untuk host, pembuat sesi, dan supervisor/admin IT. Leader tetap tidak bisa menghentikan sesi orang lain.
- **Ambil alih adalah jalur terpisah dengan gerbang sendiri**, bukan perluasan `bolehKelolaSesi`. Menambahkannya ke predikat itu memunculkan tombol Akhiri untuk sesi orang lain di mana-mana dan mengubah arti `boleh_kelola` di `GET /berjalan`.
- Revisi atas [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] §6 hanya satu hal: di samping supervisor/admin IT sebagai jalan darurat, **host yang jadwalnya sedang berjalan** boleh mengakhiri sesi orang lain, dan hanya lewat ambil alih pada akun yang sama.

### 4. Jejak dan tampilan

- **Field baru bersifat tambahan**: siapa yang mengakhiri, alasan selesai (`clock_out`, `shift_berakhir`, `ambil_alih`; kosong untuk sesi yang diakhiri lewat tombol), cara persetujuan ambil alih (disetujui atau tak dijawab), dan permintaan ambil alih yang sedang menunggu. Nama finalnya (ditetapkan saat perencanaan): `diakhiri_oleh`, `diakhiri_oleh_nama`, `alasan_selesai: "ambil_alih"`, `persetujuan_ambil_alih` (`disetujui` / `tak_dijawab`), dan `permintaan_ambil_alih` (objek permintaan terakhir di dokumen sesi). Rinciannya di [[API - Marketing Analytics Service]]. `ditutup_otomatis` dipertahankan untuk pembaca lama.
- **Klien lama aman**: bentuk respons hanya bertambah field, tidak ada field yang berubah arti.
- **Layar penolakan Mulai** menyebut pemegang dan jam mulainya, lalu menawarkan Ambil alih di layar yang sama. Konfirmasinya wajib menyebut akun dan nama pemegang, mengikuti aturan konfirmasi Akhiri di ADR 0063 §5. **Revisi 2026-09-12 (review)**: konfirmasi itu sengaja **tidak menyebut angka detik**. Batasnya milik server; angka yang ditulis di aplikasi adalah salinan kedua yang menyimpang diam-diam begitu batas server berubah. Angka detik baru tampil dari server begitu permintaan terkirim.
- **Riwayat** MyBharata menampilkan "Diambil alih oleh X pukul HH:MM" dan "Ditutup otomatis: shift berakhir" (riwayat web dihapus 2026-09-11, [[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]]).

### 5. Notifikasi memakai kategori yang sudah ada

Kategori `reminder` sudah terdaftar di `notification.InboxCategories` dan sudah dipetakan eksplisit di MyBharata (`live_shift_pengingat.go:64-71`). Kategori baru ditolak: ia memaksa notification-service ikut naik, dan salah petak di MyBharata gagal senyap.

~~Atasan langsung dicari lewat resolver atasan yang sudah ada di [[Microservices - Employee Service]], jadi marketing-analytics mendapat env baru.~~ **Revisi 2026-09-11 (perencanaan §2): pemberitahuan ke atasan langsung ditunda.** Resolver atasan per karyawan belum ada di [[Microservices - Employee Service]]; yang ada hanya penyetuju per departemen. Yang diberi tahu karena itu hanya **seluruh host sesi lama** (saat ada permintaan dan sesudah ambil alih berjalan) dan **peminta** (saat ditolak), semuanya best-effort: gagal kirim tak menggagalkan ambil alih, dan peminta tetap tahu hasilnya lewat pembacaan status. Tanpa env baru.

## Consequences

### Yang membaik

- Kejadian seperti 10 ke 11 September tertutup tanpa tangan: sesi malam tertutup 01:00, dan shift pagi mulai tanpa hambatan.
- Serah terima saat pemegang lupa mengakhiri tidak lagi menunggu IT atau tulis DB.
- Istirahat bolak-balik bisa diselesaikan pengganti dengan satu tekan, tanpa menunggu pemegang menekan Akhiri.
- Porsi yang hangus karena lewat 12 jam menjadi jarang; sisa jalurnya hanya sesi yang host-nya tanpa jadwal.

### Yang memburuk atau tetap terbuka

- ⚠️ **Kebenaran jadwal kini menentukan dua hal**: siapa bisa mengambil alih, dan kapan sesi tertutup. Jadwal yang salah (satu host di sampel, 10 sesi di luar shift) mengunci orang itu dari ambil alih dan membiarkan sesinya tak tertutup. Pengelolanya [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]]; kesalahan jadwal kini terasa di dua tempat, bukan satu.
- **Siaran lembur lebih dari 60 menit sesudah shift terpotong**, dan host harus menekan Mulai lagi. Sampel 3 hari tidak memuatnya; ukur ulang sesudah sebulan.
- **Pemegang yang masih siaran tapi tidak melihat MyBharata dalam 30 detik dianggap setuju**, jadi sesinya bisa terpotong di tengah shift. Yang menahannya: hak menolak selama 30 detik, notifikasi, dan jejak di riwayat. Aplikasi yang tertutup tidak menampilkan jendela persetujuan, hanya notifikasi, dan mengetuk notifikasinya membuka halaman Notifikasi, bukan Sesi Live.
- **Ada keadaan baru yang menunggu**, jadi ada balapan baru: dua peminta, pemegang yang menekan Akhiri selagi permintaan menunggu, peminta yang menutup aplikasi sebelum 30 detik habis. Semuanya wajib dikunci test.
- ~~**Env baru** untuk mencari atasan berarti `up -d --force-recreate marketing-analytics-service`, bukan restart.~~ Tidak berlaku sejak pemberitahuan atasan ditunda: §2 tanpa env baru dan tanpa kategori inbox baru, cukup `marketing-analytics-service` yang naik, sebelum rilis MyBharata.
- **Tik pertama sesudah deploy langsung menutup sesi berjalan yang sudah lewat +60.** Periksa sesi berjalan sebelum deploy.
- **Pecahan sesi tidak bertambah** dibanding Akhiri lalu Mulai yang sekarang, jadi efek yang sudah ada tetap sama besarnya: "jumlah sesi" di jalur KPI individu menghitung potongan (`kpi_live_individu.go:122`), dan orders dibulatkan ke bawah per potongan (`live_shift_penjualan.go:217`, `kpi_live_individu.go:143`).

### Yang sengaja tidak dilakukan

- **Leader mengakhiri sesi dengan jam yang dimundurkan.** Bergantung pada leader yang tersedia pukul 07:00, membalik keputusan 2026-08-30 sepenuhnya, dan jam mundur berarti mengubah atribusi dengan tangan.
- **Tutup otomatis saja, tanpa ambil alih.** Menolong kejadian malam, gagal di pola serah terima bersambung (median 239 menit tertahan).
- **Koreksi `perlu_koreksi` lewat layar.** Tetap skrip tulis DB yang dijalankan manusia, sampai ada keputusan siapa berwenang menyetujui koreksi atribusi.
- **Batas keras untuk sesi tanpa jadwal** (mis. tutup paksa di jam ke-12). Butuh keputusan tersendiri; yang dilindungi di sini hanya sesi yang host-nya terjadwal.
- **Menambahkan pengganti ke `host[]`, dan Jeda sambil digantikan.** Lihat Context.
- **Persetujuan tanpa batas waktu, dan diam berarti tolak.** Keduanya mengembalikan kasus pemegang yang lupa ke keadaan semula: host berikutnya tertahan sampai tutup otomatis +60 menit atau supervisor IT.
- **Persetujuan dari web.** Jendela persetujuan hanya di MyBharata, tempat host bekerja; pemegang yang hanya membuka web berlaku aturan diam berarti setuju.
- **Ketuk notifikasi membuka halaman Sesi Live.** Butuh `data` di push ponsel dan mengubah perilaku ketuk seluruh kategori ([[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]] §4); pekerjaan tersendiri.

## Dokumen Terkait

- [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]] (keputusan 2026-08-30 di §6 yang direvisi sempit)
- [[ADR - 0072 Kewenangan Jadwal Host Live sebagai Izin yang Ditugaskan]] (siapa yang membetulkan jadwal)
- [[ADR - 0081 Insentif Saya Pindah ke MyBharata di Dalam Slip Gaji]] (Host Live belum punya sumber angka insentif)
- [[ADR - 0050 Notifikasi Inbox Mendorong Push ke Browser dan Ponsel Sekaligus]] (push ponsel tanpa `data`; kenapa jendela persetujuan dipicu poll)
- [[Microservices - Marketing Analytics Service]] §Ambil alih & tutup otomatis akhir shift · [[API - Marketing Analytics Service]]
- [[Microservices - Attendance Service]] (resolusi jadwal dan status tap) · [[Microservices - Employee Service]] (atasan langsung) · [[Microservices - Notification Service]]
- [[HRIS - Otomasi Skor KPI]] (konsumen porsi per host)
- [[APP - Web ERP]] · [[APP - MyBharata]]
- [[ADR - 0091 Pencatatan Sesi Live Host Hanya di MyBharata, Halaman Web Dihapus]] (halaman web Sesi Live Host dihapus; T3 web batal)

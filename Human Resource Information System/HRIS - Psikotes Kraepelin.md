## Deskripsi

*Psikotes **online** untuk kandidat rekrutmen: HR menerbitkan sesi, kandidat mengerjakan sendiri lewat **magic link tanpa login**, server menilai otomatis, hasilnya masuk ke **Hasil Tes** babak Psikotest. Jenis tes yang sudah dibangun: **Kraepelin** (deret angka per kolom, dinilai kecepatan/ketelitian/keajegan/ketahanan). Sisi implementasi: [[Microservices - Recruitment Service]]; kontrak endpoint: [[API - Recruitment Service]].*

- **Status**: ⚠️ **Implemented (ada catatan)** — BE + FE ada di `origin/main` (BE: `services/recruitment`; FE kandidat sejak 2026-09-09). **Prod terukur 2026-09-11**: T0 dan T0a naik dan lolos gerbang (lihat butir T0); status ini bergerak, ukur ulang sebelum mengandalkannya ([[RUN - Deploy Microservices bip-erp]]).
- ✅ **Tahap nol (T0) sesi terputus merged 2026-09-10** (bip-erp #1828 `6681c997` · erp-frontend #1522 `5fd30185` · career-bharata #9 `77bfafc5`) dan **naik di dev hari itu**: diukur dari biner (fungsi baru ada di Recruitment-Service, kunci i18n baru ada di bundle FE), lalu diverifikasi lewat gateway dan sebagai HR di browser (lihat §Sesi Terputus di Layar HR). **Prod naik 2026-09-11** oleh manusia (recruitment-service 05.17 WIB, erp-frontend 07.55, api-gateway 08.43, career-portal 08.44) dan lolos gerbang: biner dan bundle memuat kode baru, dua baris skor artefak dikosongkan, dan sebagai HR di layar prod kartu Seno terbaca Terputus dengan Skor kosong. Perilaku bertanda **(T0)** di bawah kini berlaku di prod. Ukur ulang sebelum dipakai.
- **Menggantikan asumsi lama** bahwa psikotes "dilaksanakan staf HR di luar aplikasi" dan "psikotes online = fase lanjut". Keduanya sudah tidak berlaku; dokumen yang masih berbunyi begitu sudah dikoreksi ([[HRIS - Recruitment]]).
- **Diverifikasi ke `origin/main` 2026-09-10** (bukan checkout lokal — lihat catatan di bagian akhir).
- ⚠️ **Perluasan multi-jenis merged 2026-09-11 (bip-erp #1837 dan #1838, erp-frontend #1527, career-bharata #10), belum prod** (CFIT, DISC, dan tipe lain lewat katalog yang dikelola HRD): [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]] + [[HRIS - Bank Soal dan Paket Psikotes]]. Kraepelin kini juga berjalan sebagai **bagian** di dalam paket (paket bawaan "Kraepelin" 45 kolom × 40 baris × 30 detik); Kirim Tes di erp-frontend memilih paket, sementara body lama `{config}` tetap diterima BE. Dokumen ini tetap rincian **mesin Kraepelin**; yang berlaku lintas-jenis ada di sana.

## Alur Pengguna

1. Kandidat berada di babak **Psikotest**. HR menekan **Kirim Tes** di layar kandidat → `POST /candidates/:id/psikotes`.
2. Server membuat satu `psikotes_session` (soal + config **dibekukan** ke dalam sesi) dan menerbitkan **token acak**. Kandidat menerima **email** berisi magic link. Bila email gagal terkirim, HR tetap bisa **menyalin link** dari layar — penerbitan sesi tidak digagalkan oleh kegagalan email.
3. Kandidat membuka link **tanpa login dan tanpa pendamping**, di mana saja dan kapan saja (di prod lewat career portal), membaca instruksi, menekan **Mulai**, lalu mengerjakan kolom demi kolom. Tiap kolom disubmit saat waktunya habis.
4. Sesi berakhir dengan salah satu dari tiga cara, dan **bedanya dicatat**: `tuntas` (semua kolom selesai), `ditinggalkan` (browser memberi tahu server lewat `sendBeacon`; di versi career portal ini terpicu **seketika** begitu halaman tersembunyi atau ditutup), `kedaluwarsa` (server menutup sendiri karena tak ada aktivitas).
5. Server menghitung metrik lalu **meng-upsert `candidate_test_result`** untuk babak Psikotest dengan `result` = **`Pending`**. **(T0)** `score` hanya ditulis untuk sesi **`tuntas`**; sesi `ditinggalkan`/`kedaluwarsa` (dan alasan lain yang tak dikenal) menulis baris **tanpa** `score`, bahkan meng-`$unset` skor lama supaya sesi terbit-ulang yang terputus tidak mewarisi skor sesi sebelumnya. Sebelum T0 skor ditulis untuk ketiga cara berakhir, padahal kolom yang tak pernah dicapai dihitung `done=0`, sehingga skor sesi terputus **Rendah secara mekanis** dan tak bisa dibedakan dari hasil sungguhan. Deploy **tidak** menulis ulang baris lama: di dev dua sesi kedaluwarsa yang ditutup sebelum T0 naik (2026-09-09 dan pagi 2026-09-10) tetap berskor 2 dan 1,5 (terukur 2026-09-10).
6. **HR yang memutuskan Pass/Fail**, lewat form Hasil Tes di detail kandidat. Sistem tidak pernah menetapkan nasib kandidat sendiri. **(T0)** Laporan individual tampil di **kartu Psikotest** pada tab **Hasil Tes** (`?tab=tes`), tepat di samping pilihan Pass/Fail; badge di tabel kandidat dan di header detail membawa HR langsung ke sana. Sesi terputus terbaca sebagai terputus tanpa perlu membaca angka (lihat §Sesi Terputus di Layar HR).

> ⚠️ **Langkah 5 TIDAK menggerakkan status kandidat.** Upsert dilakukan langsung ke koleksi, bukan lewat handler `POST /candidates/:id/test-result`, jadi SP-Wiring (Pass → `Pending`, Fail → `Hold`) dan perpindahan `progress` ke babak **tidak** ikut jalan. Kandidat yang sudah selesai mengerjakan tetap menunggu HR membuka form Hasil Tes. Ini konsisten dengan keputusan "sistem tidak memutuskan sendiri", tapi berarti **tidak ada pemberitahuan otomatis** bahwa hasil sudah siap dinilai.

## Model Data

**Koleksi `psikotes_session`** (`recruitment_db`) — satu kandidat mengerjakan satu kali satu jenis tes.

| Field | Catatan |
|---|---|
| `candidate_id` + `round_id` | Kunci aturan **satu kandidat satu kali tes** |
| `jenis` | `kraepelin` untuk sesi lama; `paket` untuk sesi berpaket (bagian di field `bagian`, lihat [[HRIS - Bank Soal dan Paket Psikotes]]). Nilai inilah yang menentukan jalur penilaian |
| `token` | Kunci akses magic link. 32 byte `crypto/rand`, base64url |
| `status` | `pending` → `in_progress` → `finished` |
| `config`, `soal`, `hasil` | Bertipe **bebas** (`bson.M`) |
| `col_index` | Kolom terakhir yang sudah disubmit. Hanya **maju** |
| `selesai_karena` | `tuntas` / `ditinggalkan` / `kedaluwarsa`. Diisi **sekali** |
| `issued_by`, `issued_at`, `started_at`, `finished_at`, `last_seen_at` | Jejak waktu |

**Tiga index** (`ensurePsikotesIndexes`, idempoten saat startup):
- `idx_psikotes_kandidat_babak` — **UNIK** `(candidate_id, round_id)`. Ini penjaga aturan bisnis di level **data**; pemeriksaan di handler adalah lapisan kedua yang tugasnya memberi pesan terbaca, bukan pengganti.
- `idx_psikotes_token` — **UNIK** `(token)`.
- `idx_psikotes_status` — biasa, untuk kueri operasional.

> ⛔ **Mengganti spesifikasi index TIDAK terjadi lewat deploy.** Mongo menolak membuat index bernama sama dengan spesifikasi berbeda, dan penjaganya cuma `log`: build sukses, container sehat, **index lama tetap berlaku**. Kelas yang sama dengan `ensureManpowerPlanIndex`. Bila spesifikasi berubah, index lama wajib di-drop manual di dev dan prod.

### Kenapa `config`/`soal`/`hasil` bertipe bebas

Disengaja. Bentuk soal dan hasil tiap jenis tes berbeda mendasar: Kraepelin menyimpan matriks digit per kolom dan empat kategori; DISC (belum dibangun) kemungkinan kuesioner pilihan tanpa konsep benar/salah; CFIT (belum dibangun) kemungkinan skor tunggal. Menegaskan salah satu bentuk itu di lapisan bersama memaksa semua jenis lain memuat field yang tak relevan baginya. **Jenis tes baru cukup menambah file skoring/soalnya sendiri**, tanpa mengubah skema bersama. ⚠️ Janji ini diganti [[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]]: titik ekstensinya **bentuk jawaban**, bukan jenis tes.

### Kerahasiaan soal dan skor

`soal`, `hasil`, dan `token` diberi `json:"-"` **di level struct**, bukan hanya dihindari di handler. Alasannya pengaman terhadap kesalahan di masa depan: seseorang yang lupa membuat DTO terpisah tidak otomatis membocorkan kunci jawaban atau skor. Endpoint kandidat memakai **DTO publik eksplisit**, dan ada test allowlist kunci JSON yang menggigit bila field internal bocor. Laporan HR pun tidak memuat soal.

## Konfigurasi Kraepelin

Dibekukan ke dalam sesi saat terbit, supaya hasil lama tetap terbaca dengan konfigurasi yang benar-benar dipakai saat itu walau standar berubah kemudian.

| Field | Rentang | Default |
|---|---|---|
| `columns` (jumlah kolom) | 10-60 | 30 |
| `rows` (baris per kolom) | 15-60 | 40 |
| `seconds` (detik per kolom) | 10-60 | 20 |

## Endpoint

**HR** (RBAC `PermRecruitmentWork`/`PermRecruitmentView` + `isHR`):

| Method | Path | Fungsi |
|---|---|---|
| POST | `/candidates/:id/psikotes` | Terbitkan sesi. Kandidat yang **sudah punya sesi → `409`** yang menyarankan Terbitkan Ulang |
| POST | `/candidates/:id/psikotes/reissue` | Terbitkan ulang. **Alasan wajib** (kosong → `400`); sesi lama dihapus, token lama otomatis mati |
| GET | `/candidates/:id/psikotes/report` | Laporan individual (metrik + `selesai_karena`; **(T0)** + `col_index`), lewat DTO eksplisit. Kandidat tanpa sesi → `404` |
| GET | `/candidates/psikotes/status` | Status **massal** untuk polling tabel (banyak id sekaligus, satu kueri `$in`). **(T0)** + `selesai_karena` (omitempty, hanya sesi `finished`) |

> ⚠️ `/candidates/psikotes/status` **wajib didaftarkan sebelum** `GET /candidates/:id`, kalau tidak ia tertelan sebagai permintaan kandidat ber-id "psikotes". Ini kelas bug rute-tertelan yang sudah pernah menggigit di sini (lihat [[Microservices - Calendar Service]]); di kode ada test yang mengunci urutannya.

**Publik** (tanpa JWT, dijaga token di URL), dipublish gateway lewat **satu rute umum** `/public/recruitment/psikotes/:token` dan `/:token/*` sejak 2026-09-11 (bip-erp #1838, belum prod; sebelumnya lima rute tertulis satu per satu). Sesi berpaket punya endpoint per bagian dan subtes ([[API - Recruitment Service]]); `columns` dan `finish` di bawah menolak sesi paket (400):

| Method | Path (service) | Fungsi |
|---|---|---|
| GET | `/public/psikotes/:token` | Buka sesi. **Tidak memuat digit soal** |
| POST | `/public/psikotes/:token/start` | Mulai. **Idempoten**: soal tidak digenerate ulang, kandidat melanjutkan dari `col_index` tersimpan |
| POST | `/public/psikotes/:token/columns/:index` | Submit satu kolom. Index sama **menimpa**; index lama **tidak menarik balik** progres; panjang jawaban ditentukan **server** |
| POST | `/public/psikotes/:token/finish` | Selesai. Panggilan kedua tidak menghitung ulang |
| POST | `/public/psikotes/:token/abandon` | Dipanggil browser lewat `navigator.sendBeacon`. Balasan **selalu** `{ok:true}` tanpa skor |

## Skoring

`ComputeKraepelinMetrics` adalah **satu-satunya** tempat skor dihitung, dipakai bersama oleh `/finish`, `/abandon`, dan sweep server.

| Kategori | Diukur dari | Ambang 3 tingkat |
|---|---|---|
| **Kecepatan** | rata-rata dikerjakan terhadap maksimum per kolom | 70 / 45 |
| **Ketelitian** | akurasi jawaban | 95 / 85 |
| **Keajegan** | coefficient of variation antar kolom (**terbalik**: makin kecil makin baik) | 20 / 40 |
| **Ketahanan** | perubahan sepertiga akhir terhadap sepertiga awal | −10 / −25 |

Skor keseluruhan = **rata-rata skor keempat kategori**, lalu dipetakan ke kategori kesimpulan.

> ⛔ **Ambang dan rumus di atas JANGAN diubah tanpa validasi psikolog** — begitu tertulis di kode, dan itu bukan formalitas: angkanya menentukan penilaian orang.

## Penutupan Sesi: tiga jalan, satu fungsi

`selesaikanSesiPsikotes` adalah satu-satunya fungsi yang menulis status `finished`, dipanggil dari `/finish`, `/abandon`, dan sweep server. Sebelumnya logikanya hidup hanya di `/finish`; diekstrak supaya perhitungan skor tidak bercabang jadi tiga salinan yang bisa menyimpang diam-diam (**Satu Fakta Satu Tempat**).

- **Hanya sesi `in_progress`** yang boleh diproses. `finished` ditolak demi idempotensi (sendBeacon bisa terkirim lebih dari sekali). `pending` ditolak karena kandidat yang cuma membuka email lalu menutupnya **belum mengerjakan apa pun** — menghanguskan sesinya berarti ia kehilangan kesempatan tanpa pernah mengerjakan.
- **Sweep server** (ticker 1 menit) menutup sesi yang tak ada aktivitas. Ini lapis yang menentukan: `/abandon` hanya menangkap tutup-tab yang wajar, sedangkan laptop mati atau wifi putus **hanya** bisa ditutup dari sini.
- **Ambang kedaluwarsa = 6 × `seconds` config sesi itu sendiri** (default 20 detik/kolom → 2 menit), bukan angka tetap. Pengali 6 dipilih karena tiga jeda wajar bisa menumpuk pada kandidat yang masih benar-benar mengerjakan: retry jaringan, jeda alami antar kolom, dan kolom terakhir yang tak punya kolom sesudahnya untuk memaksa lanjut.
- **Idempoten terhadap dua instance**: filter update menuntut status **masih** `in_progress` di level Mongo saat update dieksekusi, bukan cuma saat dibaca. Instance yang kalah balapan tidak match, sesi ditutup tepat sekali.
- **(T0) Penutup yang kalah balapan tidak menulis Hasil Tes.** Sebelumnya hasil `UpdateOne` sesi diabaikan, sehingga penutup yang kalah tetap menulis `candidate_test_result`. Itu tak berbahaya selama ketiga cara berakhir sama-sama menulis skor, tapi sejak skor hanya milik sesi tuntas, hasilnya bisa "tuntas tanpa skor" atau "terputus berskor", tergantung siapa yang **menulis** terakhir, bukan siapa yang **menutup** sesi. Balapan paling mungkin di career portal: beacon `/abandon` tetap bisa tertembak selama layar "menyimpan" `/finish`, karena penanda selesai di halaman baru dipasang sesudah `/finish` sukses. Dua tulis Mongo-nya dipisah ke `operasiPenutupanSesi` supaya syarat ini teruji tanpa Mongo.

## Sesi Terputus di Layar HR (T0)

> **Live di prod 2026-09-11**: dicek sebagai HR di layar prod, kartu Seno menampilkan "Tes terputus: Kandidat meninggalkan tes setelah 3 dari 50 kolom", kesimpulan tersembunyi, Skor kosong, dan Kirim Ulang tersedia. Merged 2026-09-10 dan **terverifikasi di dev hari itu sebagai HR** (Chrome sungguhan, akun HRD uji, kandidat uji ber-email `example.invalid` yang ditinggalkan di kolom 1 dari 10): badge Terputus + Kirim Ulang di tabel, klik badge mendarat di `?tab=tes`, blok "Tes terputus" tampil tanpa kesimpulan, tautan baru bertahan di dialog sampai ditutup, laporan lalu berganti "belum selesai", dan Back peramban kembali ke tab sebelumnya. Sebelum T0 semua sesi `finished` tampil sebagai **Selesai** hijau, dan komponen laporan yang sudah jadi tidak di-import di layar mana pun.

- **Satu keputusan, satu tempat.** Sesi dianggap **terputus** bila `selesai_karena` terisi dan bukan `tuntas` (`sesiTerputus`, `psikotes/lib/selesai.ts`). Nilai baru dari BE di masa depan jatuh ke **Terputus**, arah gagal yang hati-hati: label Terputus yang keliru mengundang HR membuka laporan, label Selesai yang keliru meloloskan skor artefak. `selesai_karena` kosong (BE lama) dibaca sebagai perilaku lama. Sesi lama yang berakhir terputus sebelum T0 ikut terbaca Terputus, karena `selesai_karena`-nya sudah tersimpan; skornya saja yang masih artefak sampai dikosongkan.
- **Badge.** Tabel kandidat dan header detail kandidat menampilkan **Terputus** (kuning) alih-alih **Selesai** (hijau), dengan tombol **Kirim Ulang** di sel yang sama. Klik badge membuka detail kandidat langsung di tab Hasil Tes (`?tab=tes`); sel Progress menghentikan propagasi klik sehingga klik baris tabel tidak menimpanya.
- **Laporan di kartu Psikotest.** Sesi terputus diawali blok peringatan "Tes terputus" berisi cara sesi berakhir dan "setelah N dari M kolom" (N dari `col_index` server; cadangannya kolom terakhir yang punya jawaban), plus kalimat bahwa skor tidak disimpan. **Kesimpulan dan keempat kategori disembunyikan** karena nilainya Rendah secara mekanis; jumlah dikerjakan dan kurva kerja **tetap tampil** sebagai fakta sejauh mana kandidat sampai. Isian Skor di kartu kosong karena barisnya memang tanpa skor. Tombol Kirim Ulang ada di bawah laporan.
- **Keadaan lain.** Sesi `pending`/`in_progress` → "belum selesai" (BE mengirim metrik bernilai nol untuk sesi pending, jadi tanpa gerbang ini laporan tampil sebagai angka nol); kandidat tanpa sesi (`404`) → "belum ada sesi" **tanpa retry**; galat lain → "Gagal memuat laporan", bukan laporan kosong yang terbaca "belum ada sesi".
- **Kirim Ulang** memakai dialog yang sama dengan Kirim Tes, langsung di mode alasan-wajib. Sesudah sukses, tautan baru tetap tampil di dialog untuk disalin sampai dialog ditutup: cache status dan laporan baru disegarkan **saat dialog ditutup**, karena menyegarkannya saat sukses membuat tombolnya dilepas beserta dialognya. Tautan lama langsung mati (`404`).

## Belum Diimplementasikan / Catatan

- ⚠️ **DUA implementasi mesin tes kandidat hidup berdampingan**, dan ini perlu diputuskan:
	- `erp-frontend`: `src/app/psikotes/[token]/page.tsx` + `src/features/psikotes/` (2 commit, terakhir **2026-09-09**)
	- `career-bharata`: `src/app/psikotes/[token]/page.tsx` + `src/components/psikotes/` + `src/lib/psikotes/mesin.ts` (terakhir disentuh **2026-09-10**, T0)

	**Di prod yang dibuka kandidat adalah versi career portal.** `ERP_FRONTEND_URL` di container `Recruitment-Service` prod berisi `https://career.bharatainternasional.com` (dibaca 2026-09-10); nama variabelnya menyesatkan karena isinya bukan alamat erp-frontend. **Di dev kebalikannya**: tautan yang diterbitkan dev berawalan `https://erp-dev.bharatainternasional.com/psikotes/` (terukur 2026-09-10) dan career portal tidak ada di VM dev, jadi kandidat uji di dev membuka versi erp-frontend, dan layar career portal hanya bisa diuji di prod. Keputusan resmi mana yang dipertahankan belum ada ([[ADR - 0087 Katalog Tipe Psikotes Jadi Master Data, Tiga Bentuk Jawaban Tetap Kode]] §Belum Diputuskan).

	Keduanya **tidak sama perilakunya**. Hanya versi career portal yang memanggil `/abandon`, dan ia mengakhiri tes **seketika** begitu halaman tersembunyi (`visibilitychange → hidden`: pindah tab, peramban diminimalkan, layar ponsel terkunci, telepon masuk) atau ditutup (`pagehide`). Ini keputusan produk yang disengaja; komentar di kodenya menyebut Kraepelin mengukur ketahanan di bawah tekanan waktu tak terputus. Versi erp-frontend tidak punya listener apa pun (`git grep` nol), jadi di sana sesi terputus hanya ditutup sapuan server sebagai `kedaluwarsa`. **(2026-09-11, bip-erp #1837, career-bharata #10)** Tes berpaket hanya punya mesin di career portal; halaman versi erp-frontend menolak sesi paket dengan arahan membuka tautan lewat Portal Karir. Di sesi berpaket, beacon hanya menutup tes saat bagian Kraepelin sedang berjalan, dan itu ditegakkan server.
- **Tes dikerjakan tanpa pendamping, dan sistem tidak tahu di mana.** Tidak ada langkah HR memulai tes, identitas hanya dikonfirmasi lewat klik "Benar, ini saya", dan BE tidak mencatat IP maupun perangkat (`git grep` nol). Ini menyimpang dari keputusan HRD yang tercatat di [[HRIS - Recruitment]] ("dilaksanakan & dicatat staf HR langsung"); keputusan penggantinya belum ada.
- **Batas waktu per kolom ditegakkan browser, bukan server.** Server menerima kiriman kolom kapan saja selama sesi `in_progress` tanpa memeriksa lamanya; jam server satu-satunya adalah sapuan ketidakaktifan 6 × `seconds`. Kandidat yang mengutak-atik browsernya bisa mendapat waktu sampai kira-kira enam kali lipat per kolom tanpa terdeteksi. Total durasi tes = kolom × (detik + 1,2 detik transisi antar kolom).
- **Tautan tidak punya tenggat.** `issued_at` hanya ditulis dan ditampilkan, tak pernah dibandingkan dengan waktu apa pun, sehingga tautan `pending` berlaku sampai HR menerbitkan ulang. Halaman kandidat juga tidak memeriksa status kandidat: yang sudah ditolak atau mengundurkan diri tetap bisa mengerjakan, dan hasilnya tetap tertulis ke Hasil Tes.
- **Kandidat tidak diberi tahu total durasi.** Email (template prod sama dengan bawaan kode, disimpan 2026-09-09) dan layar petunjuk hanya menyebut batas waktu per kolom, sekali kerja, dan anjuran memakai komputer, tanpa jumlah kolom maupun perkiraan durasi. Selama tes kandidat hanya melihat "Kolom N dari M" dan batang waktu tanpa angka (disengaja).
- ⚠️ **Tautan yang tidak berlaku.** BE membalas `404 {"error": "sesi tes tidak ditemukan"}` untuk token yang tak dikenal, termasuk email lama sesudah HR menerbitkan ulang (terbukti di gateway dev 2026-09-10), dan `410 {"error": "sesi tes sudah selesai"}` untuk sesi yang sudah ditutup. **(T0, career-bharata #9, merged 2026-09-10)** Versi career portal memetakan 404 ke layar "Tautan tes ini sudah tidak berlaku" **tanpa** Coba Lagi, membaca `error` untuk 4xx lain, dan menampilkan kalimat umum untuk jaringan putus/5xx. Career portal prod naik 2026-09-11; token acak di prod kini menampilkan "Tautan tes ini sudah tidak berlaku." tanpa Coba Lagi (dicek di Chrome hari itu). Sebelumnya kandidat prod melihat "Permintaan gagal (404)" dengan tombol Coba Lagi yang tak akan berhasil. **Versi erp-frontend tidak disentuh** (menunggu B2 di ANALISA): masih membaca `message` saja, dan test `api.test.ts`-nya memalsukan badan 404 sebagai `{message}`, bentuk yang tak pernah dikirim BE. Untuk sesi yang sudah ditutup (410), versi career portal sudah menampilkan kalimat netral yang benar; versi erp-frontend masih berbunyi "sudah pernah dikerjakan", menyesatkan bagi sesi yang terputus.
- ⚠️ **Cache gateway 3 menit.** `GET /api/recruitment/*` di-cache api-gateway (Redis, TTL 3 menit), dan tak satu pun jalur penutupan sesi (`/finish`, `/abandon`, sweep) mengosongkannya. Badge Terputus, laporan, **dan baris Hasil Tes** karena itu bisa terlambat sampai 3 menit sesudah kandidat keluar; polling 15 detik tabel kandidat ikut lumpuh karena terus menerima jawaban cache. Verifikasi lewat gateway bisa membaca data basi (periksa header `X-Cache`). Tulisan HR lewat `/api/recruitment` (mis. Kirim Ulang) mengosongkan cache seluruh modul untuk semua HR, jadi layar sesudah Kirim Ulang tetap segar. ✅ **(T0a, bip-erp #1832, merged 2026-09-11 `4ef28e21`)** Status massal, laporan, dan `/candidates/:id/test-results` dikeluarkan dari cache. Di dev terverifikasi hari itu: lewat gateway ketiganya tak pernah `HIT` dan status terbaca `finished` seketika sesudah kandidat keluar; sebagai HR di Chrome, badge berganti Terputus **12,6 detik** sesudah kandidat keluar, tanpa reload. **Naik di prod 2026-09-11 08.43 WIB** bersama #1824 (biner memuat `psikotes/report`). Mekanismenya di [[CORE - API Master Gateway]].
- ⚠️ **Menyimpan form Hasil Tes dengan Skor kosong menimpa skor otomatis psikotes.** `submitTestResult` menulis `score` apa adanya (`$set score: nil` bila tak dikirim), dan form Hasil Tes mengirim tanpa skor bila isiannya kosong. Skor sesi `tuntas` yang ditulis penutup sesi karena itu jadi `null` begitu HR menyimpan Pass/Fail tanpa mengisi Skor. Isian Skor terisi dari `/test-results`, jadi ia kosong bila HR membuka kartu sebelum kandidat selesai lalu tidak memuat ulang (atau responsnya masih versi cache, lihat butir di atas). Perbaikan BE-nya task T0b di ANALISA, menunggu keputusan arti "Skor dikosongkan": jangan diubah, atau HR sengaja menghapus.
- **Dua baris Hasil Tes artefak di prod** (sesi kedaluwarsa di kolom 1 dari 30 dan sesi ditinggalkan di kolom 3 dari 50, keduanya `score=1`, diukur 2026-09-10) **tidak ikut berubah oleh deploy T0**, jadi dikosongkan dengan skrip dry-run/apply yang dijalankan manusia 2026-09-11 sesudah BE T0 naik: kedua baris kini `Pending` tanpa skor dan belum disimpan HR (diukur hari itu). Isian jawaban kedua sesi itu berpola (mis. 3-4-5 berulang), jadi skor rendahnya mencerminkan isian, bukan salah hitung. Ukur ulang sebelum dipakai.
- **Badge sesi `pending` di tabel HR berbunyi "Terakhir aktif {waktu}"**, padahal waktunya adalah waktu terbit, bukan aktivitas kandidat. HR bisa mengira kandidat sudah membuka tautannya.
- **Jenis tes lain** merged 2026-09-11 (belum prod) sebagai bagian paket: CFIT (pilihan ganda) dan DISC (Most/Least), lihat [[HRIS - Bank Soal dan Paket Psikotes]]. Sesi lama tetap ber-`jenis: "kraepelin"`.
- **Hasil selesai tidak memberi tahu siapa pun.** Tak ada notifikasi ke HR bahwa sebuah sesi sudah tuntas dan menunggu keputusan; HR harus melihat kolom status di tabel kandidat.
- **Report PDF psikotes tidak ada.** Laporan tampil di layar HR; tak ada lampiran tersimpan di MinIO. Desain lama di [[HRIS - Recruitment]] yang menjanjikan "report PDF di MinIO" tetap belum terealisasi.
- **Status deploy prod terukur 2026-09-11**: T0 dan T0a naik (biner, bundle, data, dan layar HR). Status ini bergerak; ukur ulang sebelum mengandalkannya.
- ⚠️ **Catatan cara memverifikasi.** Dokumen ini lahir dari kesalahan: checkout lokal `bip-erp` di mesin dev tertinggal **689 commit**, sehingga seluruh modul psikotes tak terlihat dan sempat dinyatakan "belum ada" di vault. Klaim tentang keadaan kode wajib diuji ke **`origin/<branch>`** (`git grep <pola> origin/main`), bukan ke berkas di disk.

## Dependensi & Integrasi

- [[Microservices - Recruitment Service]] — rumah kodenya; babak Psikotest dicari **by nama** `"Psikotest"` ber-`form_type: "test"` (id berbeda per lingkungan karena seed per environment). Babak belum ada → `400` dengan pesan jelas.
- [[Microservices - Notification Service]] — email magic link ke kandidat (template event `psikotes`), best-effort.
- [[CORE - API Master Gateway]] — mempublish rute publik kandidat tanpa JWT (satu rute umum berpenyaring sejak bip-erp #1838, belum prod); juga meng-cache GET `/api/recruitment/*` 3 menit, kecuali **(T0a, #1832; live di dev dan prod 2026-09-11)** status massal, laporan, dan hasil tes kandidat (lihat catatan di atas).
- [[APP - Web ERP]] — layar HR (Kirim Tes/Kirim Ulang, badge status inline, **(T0)** laporan individual + kurva kerja di kartu Psikotest tab Hasil Tes) dan halaman kandidat versi erp-frontend.
- [[APP - Portal Karir Bharata]] — halaman kandidat versi career portal.

## Dokumen Terkait

- [[HRIS - Recruitment]] — konsep dan keputusan HRD
- [[API - Recruitment Service]] — kontrak endpoint
- [[HRIS - Candidate Assessment]] — desain assessment lama yang sudah superseded

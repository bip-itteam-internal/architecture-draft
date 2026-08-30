## Deskripsi

*Service agregasi **laba dan performa marketing** per toko, produk, kampanye, iklan, video, dan live. Membaca `integration_db` **baca-saja** lalu menyimpan hasil pre-agregasi ke koleksi `mart_*` miliknya sendiri, sehingga dashboard marketing tidak menghitung ulang di setiap request. Konteks bisnisnya ada di [[Sales - Marketing Dashboard (Master Roadmap)]].*

- **Stack**: Go + Fiber v2, MongoDB replica set `rs-marketing-analytics` (database `marketing_analytics_db`)
- **Path di repo**: `bip-erp/services/marketing-analytics/`
- **Port**: env `PORT`, alias `SERVICE_PORT`, fallback `6985` (`main.go`)
- **Prefix gateway**: `marketing-analytics` (`api-gateway/main.go`, env `MARKETING_ANALYTICS_MODULE_URL`)
- **Status**: ⚠️ Implemented dengan catatan (audit kode 2026-08-26). Berjalan di production dengan channel **TikTok + Shopee**, penjadwal internal 48 jam, dan **41 route** di berkas produksi (enumerasi lengkap terhadap `origin/main`, termasuk `/health`). `mart_live_sessions` kini **terisi 4.836 sesi** (verifikasi produksi 2026-08-22). Catatan: `mart_buyer_cohort` masih kosong, lock job hanya in-process. (`/matrix/sku-shop` **tidak lagi** stub — terimplementasi sejak 2026-08-02, 576 baris + 631 baris test; dok ini menyebutnya stub selama tiga minggu lebih.) **Pencatatan sesi live oleh host (`/live-shifts`) sudah live di PROD tetapi koleksinya masih 0 dokumen** — belum pernah dipakai host sungguhan, jadi belum terbukti bisa dipakai.

## Prinsip Arsitektur

Dua hal yang membedakan service ini dari service lain dan wajib dijaga saat mengubahnya.

**1. Database service lain baca-saja, dijaga tiga lapis** (`integration_db.go:18-34`). `integration_db` milik [[Microservices - Integration Service]]; tulisan dari sini merusak data service lain tanpa jejak di repo ini. Lapisnya:

1. Tipe `integrationReader` tidak mengekspos satu pun metode penulisan.
2. Test `TestTidakAdaPenulisanKeIntegrationDB` memindai AST seluruh package dan menolak pemanggilan metode tulis pada penerima yang berasal dari sana. Lapis ini ada karena pelanggarannya tidak akan tampak sebagai test merah biasa: menulis ke `integration_db` berhasil secara teknis, kerusakannya baru terlihat sebagai data korup di database service lain.
3. Koneksinya memakai read preference `secondaryPreferred`, sehingga tulisan yang lolos pun mengarah ke node yang menolaknya.

Penjaga yang sama sudah dibuktikan menutup `insentive_db` (sumber ICC) — arahnya whitelist: yang tak terbukti aman **ditolak**, bukan yang terdaftar dilarang. Ini penegakan konkret dari [[ADR - 0002 Database-per-Service]] untuk kasus lintas-database yang tidak lewat HTTP.

**2. `/health` turun jadi `degraded` (503) bila index unik gagal dibuat** (`main.go`, `index.go`). Index unik adalah fondasi idempotensi sync: tanpa itu job yang diulang menggandakan baris. Service sengaja **tidak** panic saat boot karena pembacaan dashboard masih valid; status degraded menahan penjadwal menganggapnya siap menerima sync sambil tetap bisa ditelusuri lewat endpoint yang sama.

## Endpoint (Sudah Diimplementasikan)

**41 route** di berkas produksi (audit kode 2026-08-27, enumerasi seluruh pendaftaran `app.Get|Post|Patch|Put|Delete` di `services/marketing-analytics/*.go` non-test terhadap `origin/main`; tak ada `Group`/`Mount`, tak ada yang dikomentari). Berkas pendaftarnya: `routes.go` · `handler_mart.go` · `main.go` · `toko.go` · `divisi.go` · `price_floor_handler.go` · `ambang_handler.go` · `pagu_handler.go` · `kurva_alokasi_handler.go` · `live_shift_handler.go` · `jobs.go` · `penjadwal_status.go`. Daftar lengkap per-route: [[API - Marketing Analytics Service]], yang per audit ini **memuat keempat-puluhnya** (sebelumnya 12 route tak punya baris di mana pun). Seluruhnya `GET` kecuali disebut lain.

> ⚠️ **Angka route di dok ini pernah bertentangan dengan dirinya sendiri**: baris Status sempat menyebut 38 (audit 2026-08-22) sementara paragraf ini masih menyebut 28 (audit 2026-08-07), karena Status diperbarui tanpa menyentuh badan dokumen. Keduanya juga meleset dari kode. Bila memperbarui salah satunya, perbarui **dua-duanya** — dan hitung ulang dari kode, jangan menambahkan selisih ke angka lama.

### Halaman depan & ambang keputusan (✅ live di PROD)

| Endpoint | Isi |
|---|---|
| `/beranda` | Vonis laba terhadap ambang + pembanding periode + tren enam bulan + penggerus & peluang tiga level + penanggung jawab & cakupan + kesegaran data |
| `GET /ambang` · `POST /ambang` | Ambang keputusan (`roas_min`, `cpa_maks`), **effective-dated**, pola sama dengan `mart_price_floor`. `POST` digerbang `common.RequireMarketingLeader` |

**`/beranda` tidak menulis query sendiri.** Ia memanggil ulang fungsi sumber halaman rincian lalu menjumlahkan, sehingga halaman depan tak dapat menyimpang dari halaman yang ditautkannya. Ini aturan yang sama dengan `/summary`, dan sejak PR ini **dijaga uji AST yang sama** (`TestHalamanAgregatTidakMembangunPipelineSendiri`, kini bertabel atas kedua berkas) alih-alih hanya oleh komentar.

**Vonis dijumlahkan dari level SHOP saja.** Satu order muncul di baris tokonya, produknya, dan kampanyenya sekaligus; menjumlahkan ketiganya menghitung uang yang sama tiga kali. Ketiga level tetap dihitung untuk daftar sorotan supaya berpindah tab di FE tak memicu permintaan baru.

**Vonisnya LIMA keadaan**, dan dua di antaranya lahir dari pemeriksaan, bukan dari perancangan.

`tanpa_data` datang dari review: tanpanya, laba nol bukan `< 0` dan ROAS-nya `null`, sehingga aturan lama menjatuhkannya ke `sehat` dan melukis lencana hijau di atas nol.

`belum_matang` datang dari **verifikasi produksi**. Terukur 1-7 Agustus 2026: laba -418.450.632 dengan ROAS 7,43 (ambang 3,2), sementara `catatan_perkiraan` pada respons yang sama berbunyi "Laba minus di baris ini berarti BELUM MATANG, bukan rugi". Tren enam bulannya positif kuat seluruhnya; hanya jendela tujuh hari itu negatif. Lencananya membantah catatannya sendiri. Aturannya penguraian, tanpa ambang:

```
labaTakPulih = jumlah gross_profit baris level shop yang TIDAK bertanda SettlementBelumMatang

belum_matang  <=>  labaKotor < 0
                   DAN ( labaTakPulih >= 0
                         ATAU abs(labaTakPulih) <= AmbangMaterialitasTakPulih * abs(labaKotor) )
```

**Aturan ini butuh EMPAT iterasi, dan ketiga kegagalannya berbentuk sama: sebagian kecil sinyal mengalahkan sebagian besar, cuma berganti arah.** Riwayatnya ditulis di sini karena tiap percobaan tampak masuk akal saat dirancang:

| Percobaan | Aturan | Gagalnya |
|---|---|---|
| 1 | penularan satu-baris ala `GabungBulanan` | satu baris mentah mengalahkan 50 toko rugi nyata |
| 2 | `labaTakPulih >= 0` saja | produksi: -231.857 memveto -430.711.202 (0,05% mengalahkan 99,95%) |
| 3 | plus keluarkan baris beromzet nol | kebalikannya: -20 jt iklan hangus ditutupi +5 rb matang |
| 4 | plus pita materialitas | keempat bentuk terjawab |

Sebabnya struktural, dan itu pelajaran yang berlaku di luar kasus ini: **vonis biner tak dapat menyatakan "hampir seluruhnya belum matang dengan komponen nyata yang tak berarti" tanpa penilaian materialitas.** Setiap aturan tanpa ambang akan jatuh ke salah satu sisi. Menghindari ambang di sini bukan kehati-hatian melainkan penyebab tiga iterasi.

`AmbangMaterialitasTakPulih = 0.05` ditandai eksplisit di kode sebagai **nilai awal yang belum dibuktikan dari data**, berbeda dari `AmbangSettlementMatang` (0,70) yang diturunkan dari 1.586 pasangan berlabel. Batasnya `<=` dan dikunci dua sisi oleh test. Ambangnya **murni relatif tanpa lantai mutlak**: pada skala miliaran, 5% tetap berarti ratusan juta kerugian matang yang diampuni. Bila kelak perlu direvisi, pola ambang ganda relatif-plus-mutlak sudah ada di `toleransiInvarianShopee`.

Periode tanpa satu pun baris bertanda tak butuh penanganan khusus: `labaTakPulih` identik dengan `labaKotor` secara aljabar, rasionya 100%, vonisnya `rugi`.

**Penularan gaya `GabungBulanan` sengaja DITOLAK di sini.** Fungsi itu menodai total satu entitas dari hari-hari entitas itu sendiri, di mana hari yang ternoda memang bagian berarti dari total yang sama. `hitungBeranda` menjumlahkan lusinan toko tak berkaitan jadi satu lencana perusahaan: 50 toko rugi matang plus satu toko baru dengan satu order nyangkut akan membalik seluruh lencana dan memberi tahu direktur "nanti pulih sendiri" tentang kerugian yang nyata. Urutan evaluasi `tanpa_data` → `belum_matang` → `rugi` → `waspada` → `sehat`; menaruh `belum_matang` sesudah `rugi` membuatnya tak pernah menyala.

### Pagu belanja & simulasi alokasi (`/pagu`, `/kurva-alokasi`)

Dua endpoint yang sebelumnya tak disebut sama sekali di dokumen ini.

**`/pagu`** (`pagu_handler.go`) menyimpan pagu belanja iklan per `channel`+`shop_id`+`bulan`. Pola penyimpanannya **sama dengan `mart_ambang`**: append-only, koreksi datang sebagai baris baru dan `paguUntuk` memilih `created_at` termuda, sehingga penilaian periode lampau tak berubah surut. `GET` tak digerbang (tiap pembaca perlu tahu terhadap pagu mana belanjanya dinilai), `POST` digerbang `RequireMarketingLeader`. `nominal` bertipe `*float64` karena **pagu 0 itu sah** ("bulan ini memang tak dianggarkan") dan harus terbedakan dari field yang tak dikirim. Gagal baca dibalas **5xx, bukan daftar kosong** — "belum ada pagu" dan "database tak terbaca" menuntut tindakan berbeda.

**`/kurva-alokasi`** (`kurva_alokasi.go`) memasang kurva hasil-belanja per kanal untuk blok simulasi alokasi. Tiga bentuk dicoba pada tiap kanal, seluruhnya linear-dalam-parameter setelah transformasi sehingga cukup kuadrat-terkecil biasa (tanpa optimizer, tanpa tebakan awal):

| Bentuk | Rumus | Ada karena |
|---|---|---|
| `linear` | `laba = b0 + b1·belanja` | Bila belanja tak punya pengaruh melengkung, inilah yang jujur. Menghapusnya membuat **setiap** kanal terlihat punya titik jenuh yang sebenarnya tak ada |
| `log` | `laba = b0 + b1·ln(belanja)` | Hasil-menurun klasik; satu-satunya yang punya titik belanja optimal, jadi yang membuat slider punya arti |
| `akar` | `laba = b0 + b1·√belanja` | Pembanding bagi `log` — bila log kalah, log yang dipajang sendirian akan melebih-lebihkan kecepatan jenuh |

Urutannya menang saat seri: **linear → log → akar**, yang paling sederhana menang bila kecocokannya sama. Tanpa aturan itu, data linear sempurna dapat dilaporkan melengkung hanya karena bentuk melengkung kebetulan dihitung belakangan.

Dua gerbang, **berurutan dan tak boleh dibalik**. `MinTitikKurva = 12`: tiap bentuk memasang 2 parameter, jadi 12 titik memberi 10 derajat kebebasan; dengan 3 titik R² hampir selalu di atas 0,9 **tanpa mengandung informasi apa pun**, sehingga gerbang cacah wajib berdiri **sebelum** pemasangan. `MinRKuadrat = 0.5`: bentuknya wajib menjelaskan setidaknya separuh ragam laba.

⚠️ **Setiap kurva yang lolos wajib membawa `BatasKausalitasBaku`**, kalimat yang dikirim **dari backend bukan ditulis di UI** (penjelasan yang hidup di UI menyimpang diam-diam dari kenyataan datanya). Isinya: kurva dipasang dari **korelasi historis, bukan eksperimen**, dan karena belanja harian ditentukan manusia yang cenderung menambah anggaran pada kanal yang sedang laris, **arah sebabnya dapat berjalan terbalik** — laba yang menarik belanja, bukan belanja yang mendorong laba.

Kanal yang ditolak **tetap muncul membawa `alasan`** dalam kalimat yang dapat dibaca orang non-teknis; menghilangkannya akan terbaca sebagai kerusakan. Balasannya sengaja **bukan `Envelope`**: `unavailable_channels` menerangkan batas platform ("tak akan pernah ada"), sedangkan penolakan di sini soal kecukupan data sendiri ("tunggu data terkumpul"), dan menyatukannya membuat dua sebab yang menuntut tindakan berbeda terbaca sama. `jumlah_terpasang`/`jumlah_ditolak` dikirim dari backend, bukan dihitung ulang FE — yang menyimpang di situ justru kalimat temuan utamanya.

### Hari WIB, dan kapan UTC justru yang benar

Konvensi tanggal modul ini **"hari WIB dikodekan sebagai tengah malam UTC"**, terverifikasi dari data produksi: baris mart membawa `2026-08-01T00:00:00Z` untuk hari WIB 1 Agustus, dan `waktuKueriSah` mengurai `2026-08-01` jadi nilai yang sama persis. Karena itu seluruh aritmetika tanggal di atas nilai hasil urai query sudah konsisten dan **tak boleh "diseragamkan"** ke WIB.

Yang salah adalah pertanyaan yang berbeda: **"hari ini tanggal berapa?"**. Antara pukul 00:00 dan 07:00 WIB, `time.Now().UTC()` masih menunjuk hari kemarin, sehingga rentang bawaan berakhir kemarin dan hari berjalan lenyap dari layar tanpa satu pun tanda. Terjadi di **sebelas** tempat: `/beranda`, `/ambang`, dan sembilan handler lain lewat `denganBawaan(...)`. Diperbaiki dengan `hariIniWIB` di `bacaan.go`, memakai `zonaWIB` yang sudah ada (offset tetap, bukan `time.LoadLocation` — Indonesia tak punya DST dan tzdata sistem tak dapat diandalkan).

**Yang TETAP UTC dan memang benar**: `st.LastOKAt`, `SyncedAt`, `CreatedAt`, `dibuatPada`, `batasBasi`, dan argumen `hitungKesegaran`. Semuanya instant atau stempel waktu audit, bukan tanggal. Membedakan keduanya adalah inti persoalannya: enam tempat sempat dicurigai salah, empat di antaranya ternyata benar.

Penjaganya `TestRentangBawaanPakaiHariWIBBukanUTCPolos` — pemindai AST berdaftar **dinamis** (`filepath.Glob`), jadi berkas baru ikut terjaga. Batasnya jujur tertulis di komentarnya: ia mencocokkan ekspresi harfiah, jadi variabel antara (`n := time.Now().UTC()`) dan helper pembungkus lolos.

**Pembacaan agregat WAJIB menaikkan `Limit` sendiri.** `filterMart.Limit` bernilai nol berarti `limitReturBawaan` (500), yang merupakan ukuran halaman untuk tabel, bukan batas untuk penjumlahan. Karena urutannya `gross_profit` menurun, pemancungan membuang barisnya yang **merugi** lebih dulu: vonis jadi terlalu optimis dan daftar penggerus permanen kosong. Ketika pembacaan menyentuh `limitReturMaks`, amplopnya melaporkan diri lewat `unavailable_channels` (pola `ReasonMatrixSumberTerpancung`).

### Laba (baca `mart_profit_attribution`)

| Endpoint | Isi |
|---|---|
| `/summary` | Ringkasan lintas sumber |
| `/profit/shops` · `/profit/products` · `/profit/campaigns` · `/profit/ads` | Laba per level. **Bawaan BULANAN** (`granularitas=harian` untuk rincian); products juga **lintas-toko** secara bawaan (`lingkup=per_toko` untuk per toko, baris gabungan membawa `jumlah_toko`). `sort_by`/`sort_dir` per level; nilai tak dikenal → **400** + daftar sah |
| `/profit/orders` | **Drill level product → daftar order penyusunnya** (baca `transaction_orders` langsung). `entity_id` wajib; `bulan` XOR `dari`/`sampai` (batas WIB); order CANCELLED **dikecualikan bawaan** — konsisten dengan agregasi laba — dan dibuka lewat `termasuk_batal=true`; respons membawa `sku_tercakup` |

### Video & live

| Endpoint | Isi |
|---|---|
| `/videos` | Performa video (`VideoRow`, tiga tab VSA / GMV Max / organik via `spend_vsa`, `spend_gmv_max`, `sumber`). Kini juga membawa `gross_profit` (dijumlah pass kedua dari `mart_profit_attribution` level video — kegagalannya tak menggagalkan halaman, hanya null) dan identitas produk `product_title` / `product_image_url` / `product_item_group_id`. **Menolak `granularitas` (400)** — snapshot kumulatif tanpa dimensi hari |
| `/videos/orders` | **Drill video → daftar order AFFILIATE** dari `affiliate_orders` (`content_id = video_id` AND `content_type = "VIDEO"`). Field `cakupan` **selalu terisi**: daftar ini hanya order affiliate — order organik video tidak tercatat menautkan video di sumber mana pun, jadi jangan dibandingkan dengan kolom orders baris video |
| `/lives` | Sesi live dari `mart_live_sessions` (**4.836 sesi** per 2026-08-22; dulu kosong) |

### KPI Host Live (`/kpi/kinerja-live`)

Rute ke-41, masuk 2026-08-27 (PR [#1479](https://github.com/bip-itteam-internal/bip-erp/pull/1479) & [#1486](https://github.com/bip-itteam-internal/bip-erp/pull/1486)). Menjawab satu pertanyaan: **berapa capaian siaran live satu departemen pada satu periode?** Bahan skor KPI Host Live di [[Microservices - Employee Service]] (sumber `kinerja_live`). Rincian parameter & balasan: [[API - Marketing Analytics Service]].

**Penilaian PER-DEPARTEMEN, bukan per-orang** — dan itu bukan penyederhanaan sementara melainkan batas data. Tiga hal menutup jalan ke per-orang, seluruhnya terukur produksi 2026-08-27:

1. Satu sesi TikTok bisa **16 jam** dalam satu `session_id` (07:50–23:50 WIB), berisi 2–3 shift host bergantian. API memberi agregat per sesi **tanpa dimensi waktu di dalamnya**, jadi angkanya tak bisa dipecah dari sisi mana pun.
2. Satu host memakai beberapa akun, dan akunnya berganti antar bulan (`live_glowbooster4` → `live_glowbooster7`; `beautyhacks.id3` berhenti Juli).
3. Satu siaran tercatat di beberapa akun sekaligus (dua etalase).

⚠️ **Scope `individu` sudah didaftarkan di sisi employee-service tetapi sumbernya BELUM menghormatinya** — ia selalu menghitung per-departemen, sehingga memilih "Individu" atau "Departemen" di template menghasilkan angka identik sementara layar KPI menampilkan badge "Individu". Terlihat di produksi 2026-08-27 pada template *Host Live Kyura*. Perbaikannya menunggu `/live-shifts` benar-benar terisi.

**Empat metrik**, bobot & target diputuskan pemilik metrik 2026-08-27 (diisi HR di template, bukan di kode):

| Metrik | Rumus | Bobot · target contoh |
|---|---|---|
| `conversion` | Σ `sku_orders` (cacahan) | — |
| `conversion_rate` | Σ `sku_orders` ÷ Σ `product_clicks` × 100 | 70 · 2% |
| `avg_viewing_duration` | Σ(`avg_watch_sec` × `views`) ÷ Σ `views`, satuan **detik** | 20 · 60 detik |
| `add_to_cart_rate` | Σ `add_to_cart` ÷ Σ `product_clicks` × 100 | 10 · 5% |

⛔ **`conversion` memakai `sku_orders` (pesanan DIBAYAR), bukan `items_sold`.** TikTok mengirim tiga angka penjualan yang mudah tertukar dan salah pilih tidak menghasilkan galat, hanya angka yang meleset: `sku_orders` (pesanan dibayar) · `created_sku_orders` (termasuk COD/PayLater belum lunas) · `items_sold` (**unit**; satu pesanan berisi tiga unit dihitung tiga). Diverifikasi dua arah: dok resmi menyatakan `click_order_rate` = *paid sku orders / product clicks* (uji sesi nyata 89/1664 = 5,35% persis sama dengan yang dikirim API), dan totalnya cocok catatan manual HR — Juli Kyura **6.947 vs sheet 6.933 (+0,2%)**, sementara `items_sold` meleset 2,3%. Field `mart_live_sessions.orders` **sudah** berisi `sku_orders`; nama telanjang `Orders` itu yang sempat menyesatkan.

⛔ **`24h_live_gmv` bukan `gmv` dan tak boleh dijumlahkan dengannya.** Dok resmi: *"within 24 hours of viewing, **including returns and refunds**"* — bisa **lebih besar** dari `gmv` dan bisa terisi saat `gmv` nol. Sekelas dengan `iklan_sia_sia` — lihat §Aturan Pemakaian Angka di dokumen ini.

**Rasio dihitung dari Σpembilang ÷ Σpenyebut seluruh sesi, bukan rata-rata rasio per sesi**; durasi tonton ditimbang `views`. Merata-ratakan memberi bobot sama kepada sesi 10 penonton dan sesi 5.000 penonton. Konsekuensinya reduksi berbeda per metrik di sisi employee-service: cacahan `jumlah_nilai`, rasio `rata_rata`.

`add_to_cart` **tidak ada di `shop_lives/performance`** — sumbernya endpoint terpisah `/analytics/202512/shop/{live_id}/products_performance`, satu panggilan per sesi saat sync, dan **hanya untuk sesi host** (148 panggilan/bulan, bukan ribuan). Fieldnya pointer: nil = belum pernah diambil, bukan nol orang memasukkan ke keranjang. ⚠️ **Per 2026-08-27 nol dari 2.365 sesi Agustus punya field ini** — kode pengambilnya baru merge dan sync belum berjalan sejak itu, sehingga `add_to_cart_rate` melaporkan 0% untuk keadaan yang sebenarnya belum terukur.

**Yang TIDAK bisa diambil dari API TikTok**, diuji langsung ke produksi 2026-08-27 (12 endpoint live):

- **Biaya iklan per sesi** — tak ada di satu pun endpoint live. `tt_business_gmv_max_performance_reports` bergranularitas harian (`stat_time_day`), endpoint per-menit nol field biaya, dan iklan bertipe LIVE cuma **2 dari 1.335 ad group** dengan nol baris di `mart_profit_attribution`. Konsekuensinya **laba bersih per sesi live tak dapat dihitung tanpa asumsi**; komponen HPP dan fee marketplace sudah akurat (uji: 23,9% vs 25,8% dan 12,0% vs 12,1% terhadap agregat toko), iklan yang tidak.
- Seluruh keluarga `live_rooms/*` (**7 endpoint**: core_stats/PCU, GMV trend, view trends, traffic, interactive trends, product stats, user portraits) ditolak `36009004`/`36009005` — menuntut otorisasi level akun creator, bukan shop-level seperti kredensial kita. Pola sama dengan livestream Shopee.
- `Get Bestselling LIVE Sessions` ditolak `105005` (app tak diizinkan).
- **Shopee live nihil API** dan itu permanen — host Shopee tetap dicatat manual.

### Pencatatan sesi live oleh host (`/live-shifts`)

Enam route, seluruhnya digerbang `common.RequireLiveShiftUser` (`live_shift_handler.go`). Fitur ini ada karena **atribusi live per orang mustahil dari API TikTok** — dibuktikan lewat panggilan nyata, bukan asumsi: `room_id` di Get Order Detail terbukti US-only (probe `code=0` untuk toko region ID mengembalikan field itu tidak ada), Product Stats API menuntut scope Creator yang tak tersedia di portal, dan `auto_combine_order_id` terkirim kosong pada seluruh 326.153 order. Jalur `affiliate_orders.content_id` = `session_id` **terbukti cocok** (407 dari 432, kontrol negatif VIDEO 0 dari 432) tetapi hanya mencakup **11,8% GMV** karena host penyumbang terbesar siaran atas nama toko, bukan sebagai afiliator.

| Endpoint | Isi |
|---|---|
| `POST /live-shifts` | Mulai sesi. Host yang login otomatis jadi host — `employee_id` dari header gateway, bukan dari body (field body bernama sama hanya jadi jalan memalsukannya) |
| `PATCH /live-shifts/:id/jeda` | Jeda / Lanjutkan. Menutup jeda terakhir bila sedang dijeda, menambah jeda baru bila tidak |
| `PATCH /live-shifts/:id/selesai` | Akhiri; menutup jeda yang masih menggantung |
| `GET /live-shifts/berjalan` | Sesi berjalan, untuk menentukan keadaan tombol |
| `GET /live-shifts` | Riwayat + porsi GMV per host. `?milik_saya=true` menyaring lewat header (tak bisa dipalsukan); `?host=<id>` hanya untuk marketing leader — host biasa yang mencoba mengintip orang lain dibalas **403**, bukan diam-diam dipaksa ke dirinya sendiri |
| `GET /live-shifts/akun` | Isi pemilih akun untuk satu toko (`shop_id` wajib, kosong → **400**), diagregasi dari `mart_live_sessions` (`live_shift_akun.go`). Akun teratas ditandai `utama` **hanya bila porsi GMV-nya ≥ 60%**, karena satu toko produksi cuma 49,8% dari 290 akun dan menandai yang teratas di toko semacam itu justru mendorong host memilih akun yang belum tentu benar. Sengaja **tidak** menyaring `hanyaSesiHost`: layar pemilih harus menampilkan seluruh akun termasuk afiliasi. Pemecah seri deterministik (nama akun menaik) supaya dua panggilan tak pernah membalas urutan berbeda |

**Pembagian GMV dua tahap, jangan digabung.** Antar-shift lebih dulu: satu sesi TikTok bisa beririsan dengan beberapa shift (pergantian jadwal pada akun yang sama), jadi GMV-nya dibagi **proporsional menurut lama irisan**. Tanpa itu terukur Rp 1 juta menjadi Rp 2 juta saat dua shift beririsan, dan irisan setipis satu detik menyeret GMV penuh. Baru sesudahnya porsi tiap shift dibagi **rata** ke host di dalamnya. Invarian yang dikunci test: jumlah GMV seluruh shift tidak boleh melebihi GMV sesi sumber.

**`ada_data: false` dibedakan dari GMV nol.** Sync TikTok bisa telat berjam-jam; menyajikan Rp 0 sebagai fakta menuduh host atas sesuatu yang belum tentu terjadi. Pembaca wajib menampilkan "belum ada data", bukan angka nol.

**Rentang baca sesi dilebarkan simetris 12 jam** di kedua ujung, sementara rentang shift memakai tanggal asli. Sesi live melewati tengah malam adalah 5,2% dari seluruh sesi (213 dari 4.130 terukur), dan durasi sesi bersih terpanjang tepat 12 jam — jadi pelebaran sebesar itu menangkap semuanya tanpa menyeret sesi yang sudah pasti tak beririsan. Melebarkan satu ujung saja memindahkan bug, bukan memperbaikinya.

**Tanggal diurai zona WIB**, bukan UTC (`time.ParseInLocation` + `zonaWIB`). `time.Parse` polos membuat rentang "10 Agustus" sebenarnya terbaca 10 Agt 07:00 s.d. 11 Agt 06:59 WIB, sehingga shift dini hari — jam live yang nyata dipakai — muncul pada tanggal yang salah.

#### Siaran serentak di beberapa akun (🟡 diusulkan, [[ADR - 0063 Siaran Serentak Dicatat sebagai Sesi Terpisah per Akun]])

Host live memegang lebih dari satu akun dan **menyiarkan serentak dari beberapa perangkat**, dengan akun-akun yang bisa milik toko berbeda (dinyatakan pemilik proses 2026-08-30). Ini sebab kedua yang sudah tercatat di §KPI Host Live sebagai penghalang penilaian per-orang, kini dengan bentuk yang lebih tajam daripada "akunnya berganti antar bulan".

Terukur di produksi 2026-08-30 atas `mart_live_sessions` (5.482 sesi, 2 Jul s.d. 29 Agt): **148 pasangan sesi tumpang tindih pada akun berbeda, seluruhnya lintas toko, 935 jam irisan**, dengan **puncak 4 akun brand hidup bersamaan** (dua akun 422,9 jam di 46 hari; tiga akun 186,5 jam di 31 hari). Artefak dua-etalase sudah dipisahkan memakai ambang `satuSiaran` yang ada (mulai ≤ 60 detik **dan** selisih durasi ≤ 2 menit) dan hanya menjelaskan 3 dari 151 pasangan. ⚠️ Angka ini membuktikan **dua akun hidup bersamaan**, bukan bahwa satu orang memegang keduanya; ketidakmampuan itu justru alasan `live_shifts` ada.

Tiga aturan yang diputuskan:

- **Satu sesi tetap satu akun**; siaran serentak jadi **beberapa dokumen paralel**. Penyimpanan tidak berubah karena index unik parsialnya hanya atas `akun_live` (tanpa `shop_id` maupun `host.employee_id`), jadi sesi paralel milik satu orang **sudah lolos hari ini**.
- ⛔ **Jam siaran seseorang = union jendela waktu, bukan penjumlahan `durasi_efektif_detik`.** Host yang siaran 2 jam di tiga akun tercatat **2 jam, bukan 6**. `durasi_efektif_detik` per sesi tetap komponen **sejajar**; yang dilarang adalah menjumlahkannya lintas sesi untuk satu `employee_id`. Perluasan langsung dari kaidah `gabungSesiKembar` yang sudah berlaku ("ORDERS DIJUMLAH, SESI TIDAK"): **rupiah dijumlah, jam tidak.**
- ⛔ **Tumpang tindih pada akun BERBEDA milik orang yang sama adalah SAH dan porsinya DILARANG dinolkan.** `TandaiShiftTumpangTindih` yang ada menuntut `shop_id` **dan** `akun_live` sama, dan itu dipertahankan sebagai deteksi kesalahan input. Memperluasnya begitu saja ke lintas akun akan **menghanguskan GMV dari praktik kerja yang sah**, senyap, tepat pada bulan host bekerja paling keras.

Atribusi lintas departemen: GMV masuk ke departemen **host** (`work_data.department`), bukan departemen pemilik akun, demi menjaga invarian [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] bahwa satu omzet tak boleh menaikkan skor dua departemen. Kepemilikan toko tetap dibaca dari `department_shops`, jangan diturunkan dari nama akun.

⚠️ **Konsumen yang sudah menggandakan jam hari ini**, dua-duanya di frontend: kartu metrik `halaman-live-shift.tsx` dan `ringkas-performa-host-live.ts` (layar tim ICC), keduanya menjumlahkan `durasi_efektif_detik` per baris tanpa dedup jendela waktu. Di bip-erp sendiri **nol** konsumen `porsi_host`/`durasi_efektif_detik` di luar service ini.

⚠️ **Sesi kedua tak punya tampilan** di web (`sesiBerjalan?.[0]`) maupun mobile (`milik.first`), jadi ia tak bisa dijeda atau diakhiri, lalu menggantung melewati ambang 12 jam yang **memaksa porsi host jadi nol**. Peringatan jam ke-11 tak pernah sampai karena kartunya tak pernah dirender. Ini menjadikan perbaikan tampilan N sesi sebagai **prasyarat**, bukan penyempurnaan.

### Retur & analitik lain

| Endpoint | Isi |
|---|---|
| `/returns/breakdown` | Agregat retur per channel + initiator (`BUYER`/`SYSTEM`/`SELLER`) + **alasan mentah** (tidak dinormalisasi) + kurir; `refund_value` dan `order_value` terpisah (order batal-sebelum-bayar tak punya refund) |
| `/returns/detail` | Drill baris agregat → daftar order: order_id, toko, **nama ICC**, item+SKU+jumlah, nilai, alasan mentah, tanggal. `reason=` kosong **bermakna** ("tanpa alasan tercatat"); `total: -1` = cacah gagal (bukan 0) |
| `/affiliate` · `/cohort` · `/audience` | Analitik affiliate (kolom `collaboration_type` internal/eksternal), kohort, audiens; `sort_by`/`sort_dir` dua arah + pemecah-seri deterministik |
| `/matrix/sku-shop` | ✅ **Terimplementasi** (`matrix_sku_shop.go`, 576 baris + 631 baris test). Matriks **produk × toko**: baris = produk (`entity_id` = master SKU), kolom = toko, sel = satu metrik terpilih. **Sel yang ABSEN bermakna bisnis**: tak ada satu pun baris mart untuk pasangan itu = *peluang listing*, jadi nol nyata tetap hadir sebagai sel bernilai 0 sementara yang tak berbaris tak punya kunci sama sekali — FE wajib membedakan keduanya lewat keanggotaan peta, bukan nilai. Metrik terbatas pada **tujuh kolom aditif** (`gross_profit` bawaan, `revenue`, `net_settlement`, `hpp`, `ads_cost`, `fee_marketplace`, `retur`); kolom rasio **tak boleh** ditambahkan lewat jalur ini karena rasio wajib dihitung ulang dari pembilang/penyebut gabungan. `orders` **sengaja tak ada** — mart tak menyimpan cacah order. `bulan` XOR `dari`/`sampai` (keduanya → 400); `limit` bawaan 100 maks 500 berlaku **setelah** penjumlahan dan pemeringkatan, dan pemotongan **selalu** dilaporkan lewat `terpotong` + `total_produk`. Lapisan **baca murni**: tak ada koleksi baru, tak ada pipeline tulis |

### Price floor, job & health

| Endpoint | Isi |
|---|---|
| `GET /price-floor` · `POST /price-floor` · `POST /price-floor/upload` | Harga minimal per SKU, **effective-dated** (pola `product_costs`) |
| `POST /jobs/:name/trigger?hari=N` | Picu job manual. `hari` bawaan **7**, maksimum **120**; job berjalan → **409** |
| `GET /jobs/status` | Kesehatan penjadwal (`penjadwal_hidup`, alasan, `sync_state` tiap job) |
| `GET /health` | `ok`, atau `degraded` (503) bila ada index unik gagal dibuat |

### Kontrak amplop respons

`{rows, unavailable_channels, ...}` — plus **`kolom_tidak_berlaku`** (level response): daftar kolom yang di level itu **tak punya sumber sama sekali** dan wajib DIHILANGKAN FE dari tabel, bukan dirender "—" per baris. Isi per level (`kolom_struktural.go`): level **ad** → `revenue, net_settlement, gross_profit, hpp, fee_marketplace, retur` (laporan VSA tak membawa rupiah/SKU/jalur order); level **campaign/video** → `fee_marketplace, retur` saja (revenue & HPP nyata dari GMV Max). Ini satu-satunya penanda sah untuk menghapus kolom — menebak dari null akan ikut menghapus kolom yang kadang berisi.

## Penjadwal Internal (48 jam)

`penjadwal.go` — sejak 2026-08-01 service ini **punya scheduler sendiri**; entri lama "tidak ada scheduler" tidak berlaku lagi.

- **Interval 48 jam**, jalan **03:00 WIB** — dihitung di zona WIB (`jedaKeJamWIB`), bukan UTC (jam UTC akan menggesernya ke 10:00 WIB, kelas bug timezone yang pernah menggigit repo ini). Satu timer di-arm ulang tiap siklus — bukan ticker berjangkar waktu boot, yang membuat jam jalan bergeser tiap restart container.
- **Urutan berurutan, tak pernah paralel**: `sync-ad-creative-link` → `sync-video-performance` → `sync-profit-attribution`. Yang pertama membangun jembatan ad→video yang dibaca dua job berikutnya; tiga job serentak menembak kuota TikTok tiga kali lipat.
- **Jendela 14 hari** untuk job berjendela — sengaja jauh di atas interval 2 hari: jendela = interval berarti satu run gagal meninggalkan hari yang **tak pernah** tersentuh, dan koreksi marketplace datang terlambat (retur, settlement menyusul). Divalidasi saat boot (wajib > interval).
- **Kegagalan tidak senyap**: tiap job dibungkus `recover()` sendiri, satu gagal tak membatalkan sisanya; sebab terkumpul di `sync_state` kunci `"penjadwal"`; `last_ok_at` hanya distempel pada siklus yang sepenuhnya sukses; shutdown anggun **tidak** dicatat sebagai kegagalan (alarm palsu tiap deploy melatih operator mengabaikan `last_error`).
- **`GET /jobs/status`** menjawab "penjadwalnya masih hidup?": detak boot (mati-sejak-start terlihat segera), pemeriksaan goroutine (mati dalam proses → terdeteksi seketika), ambang 72 jam, dan keadaan `dinonaktifkan` yang dibedakan dari mati. Penjadwal mati diam-diam terlihat persis seperti "belum waktunya jalan" — karena itu deteksinya eksplisit.

| Env | Bawaan | Catatan |
|---|---|---|
| `MARKETING_ANALYTICS_SCHEDULER_ENABLED` | `true` | kosong = aktif; nilai tak dikenal → **fatal saat boot** (salah ketik tak boleh terbaca "sudah mati") |
| `MARKETING_ANALYTICS_SCHEDULER_HOUR_WIB` | `3` | 0–23 |
| `MARKETING_ANALYTICS_SCHEDULER_DAYS` | `14` | maks 120, wajib > interval |
| `MARKETING_ANALYTICS_SCHEDULER_RUN_ON_BOOT` | `false` | deploy sering; menyapu tiap boot membakar kuota tanpa baris tambahan |

Interval sendiri belum bisa diubah lewat env. **Lock job hanya in-process** — menaikkan replika >1 membuat tiap replika menjalankan penjadwalnya sendiri (perlu distributed lock); lihat juga [[IT - Background Jobs & Schedulers]].

## Job Sync

| Job | Channel | Fungsi |
|---|---|---|
| `sync-ad-creative-link` | TikTok | Jembatan metrik iklan ke video organik lewat `tiktok_item_id` dari `/open_api/v1.3/ad/get/` |
| `sync-video-performance` | TikTok | Snapshot performa video + identitas produk per video (dipilih deterministik: biaya GMV Max terbesar). Mengimplementasikan antarmuka berjendela tapi **sengaja mengabaikan** nilai `hari` (sumbernya kumulatif) |
| `sync-profit-attribution` | **TikTok + Shopee** | Agregasi laba per level per hari per channel; satu-satunya job yang benar-benar memakai `?hari` |

Perilaku trigger (`jobs.go`): parameter `hari` cacat → **400 dan job tidak jalan** (menjalankan bawaan atas backfill yang diminta = sukses palsu); job tak berjendela **menolak** `hari` alih-alih mengabaikan; konteks dilepas dari request (timeout 30 menit); ringkasan memuat `unit_total`/`unit_gagal` supaya "tersimpan 0" terbedakan dari "seluruh hari gagal".

**Prune baris basi**: sesudah upsert sukses per (channel, hari), baris `synced_at` lebih tua dari batch **dihapus** (`HapusProfitBasi`). Tanpa ini, baris yang berhenti dihasilkan (mis. order CANCELLED yang kini dikecualikan) hidup selamanya di mart dan menjumlah bersama baris segar — kasus nyata production: 15 baris yatim menyumbang HPP Rp170 jt pada satu produk sehingga labanya tampil −Rp148 jt. Gagal prune = hari gagal, bukan senyap.

## Koleksi (`marketing_analytics_db`)

Index unik dibuat saat boot (`index.go`). `CreateOne` **tidak mengganti** index lama — perubahan kunci unik menuntut `dropIndex` manual saat deploy.

| Koleksi | Kunci unik | Isi |
|---|---|---|
| `mart_profit_attribution` | `channel + level + entity_id + shop_id + date` | Laba per hari per channel. `shop_id` masuk kunci sejak baris product dipisah per toko (dulu satu entitas melebur lintas toko dan biaya salah dinisbatkan). `entity_id` level product = **master SKU**; SKU belum termapping tetap memakai SKU aslinya + tanda `belum_termapping` |
| `mart_video_performance` | `channel + video_id` | **Snapshot kumulatif, sengaja tanpa dimensi hari** (lihat bawah) + identitas produk |
| `mart_ad_creative_link` | `advertiser_id + ad_id + tiktok_item_id` | Jembatan ad ke post organik |
| `sync_state` | `channel + job` | Cursor, `last_run_at`, `last_ok_at`, `last_error` per job + kunci `penjadwal` |
| `mart_live_sessions` | `channel + session_id` | Sesi live hasil sync TikTok. **4.836 baris** per 2026-08-22. `username` di sini adalah **akun toko**, bukan orang — satu akun dipakai bergantian banyak host, dan itulah alasan `live_shifts` ada |
| `live_shifts` | `akun_live` (unik **parsial**: hanya saat `selesai` null) | Catatan sesi live yang ditulis **host lewat tombol**, sengaja terpisah dari `mart_live_sessions` yang ditulis mesin. Index parsialnya menegakkan "satu akun hanya boleh punya satu sesi berjalan" di Mongo, bukan di kode yang bisa dilewati balapan cek-lalu-tulis. **Masih 0 dokumen** di production |
| `mart_buyer_cohort` | — | **Masih kosong** di production |
| `mart_price_floor` | `sku + effective_from` | Harga minimal per SKU |
| `mart_ambang` | `nama + effective_from` | Ambang keputusan (`roas_min`, `cpa_maks`). **Append-only**: mengubah ambang berarti menambah baris bertanggal baru, bukan menimpa. Menimpa membuat vonis periode lampau ikut berubah surut tanpa jejak, dan yang membandingkan dengan tangkapan layar minggu lalu tak punya cara tahu mengapa angkanya berbeda. Koleksi BARU, tak ada index lama yang perlu di-`dropIndex` saat deploy. Field `nama` konstan (`global`) hari ini, disediakan sejak awal karena menambah dimensi ke kunci unik SESUDAH koleksi berisi menuntut migrasi manual |

### Kenapa `mart_video_performance` tidak punya dimensi hari

Sumbernya, `tt_shop_video_performances`, terverifikasi berupa **snapshot kumulatif**: satu dokumen per video, angka seumur hidup, ditimpa tiap sync, tanpa `stat_time_day`. Versi sebelumnya menyimpan satu baris per video **per hari**; akibatnya terukur di production: 613.867 baris untuk 88.594 video, dan halaman rentang-tanggal mendapat **7,0× angka sebenarnya tanpa error**. Perbaikannya struktural: dimensi harinya dibuang. `synced_at` menggantikan `date`.

## Channel & Sumber Data

### TikTok

- **Laba dibin ke `order_date` (waktu order terjadi), bukan `created_at` (waktu ETL menulis).** Bug ini pernah membuat angka bulanan duduk di bulan yang salah tanpa terlihat: Juli via `created_at` = 233.565 order, via `order_date` = 70.514 — TikTok meleset rata-rata 44 hari tapi tak terlihat karena volume backfill membuat tiap bulan tampak terisi. `cohort`/`audience`/`returns` sudah memakai `order_date` lebih dulu; agregasi laba yang menyimpang.
- **Order `CANCELLED` dikecualikan** dari agregasi laba (`$nin` di filter Mongo): order batal membawa `items[].quantity` penuh sehingga HPP terbebankan sementara settlement-nya persis nol — terukur pernah menyumbang **54% dari seluruh HPP Juli** (Rp1,59 M dari Rp2,93 M; satu order batal berisi 400 baris item identik @Rp100). `SHIPPED` **tidak** dibuang (barang sudah keluar); `RETURNED` punya jalurnya sendiri lewat `income.total_refund`.
- **Metrik iklan (`metrik_iklan`)** dari `tt_business_integrated_reports` (Mongo, bukan panggilan API langsung): 15 metrik `*float64` (impressions, spend, clicks, ctr, cpc, video_watched_2s/6s, conversion, roas, dll — dua kolom mati `checkout`/`onsite_total_add_to_cart_value` sengaja tak disertakan). **`SpendIDR` dan `SpendUSD` terpisah, tak pernah dikonversi/dijumlah** — versi lama tak pernah membaca `metrics.currency` sehingga dolar tercampur ke rupiah; mata uang tak dikenal dicacah dan disebut namanya, tidak dianggap IDR. Rasio **dihitung ulang dari total** saat agregasi (CTR 10%+30% ≠ 40%; yang benar 40 klik/200 tayang = 20%); rasio yang penyebutnya tak dikirim API (`average_video_play`, `roas`) = **nil + catatan**, karena rata-rata-dari-rata-rata salah. Revenue **tidak** diturunkan dari `roas × spend` (cakupan 0,3%, mata uang campur).

### Shopee (`sumber_shopee.go`, `bagian_item_shopee.go`)

Sumber: `shopee_gms_campaign_performances` + `shopee_gms_item_performances` di `integration_db`. Invarian campaign==item **tersedia gratis dari sumbernya** (selisih Rp19 atas Rp188 jt) — biaya per item aktual, jalur prorata `AllocateAdSpend` sengaja dimatikan (`SpendCampaign` dibiarkan nol agar belanja tak tertagih dua kali).

Empat jebakan sumber yang ditangani (masing-masing pernah/berpotensi gagal senyap):

1. **Long BSON** — `item_id`/`shop_id`/`campaign_id` bertipe `{high, low, unsigned}`; dibaca sebagai int32 hanya mengambil `low` tanpa error (`18366515349` → `1186646165`). Semua id lewat `idBSON()` → string desimal.
2. **`primitive.DateTime`** — driver mendekode BSON Date ke `bson.M` sebagai `primitive.DateTime`, bukan `time.Time`. Assertion `.(time.Time)` pernah membuang **seluruh 37.668 baris iklan Shopee** sementara sync melapor "90/90 sukses". Semua waktu lewat `waktuBSON()` yang menerima kedua tipe. Uji dekode BSON di service ini wajib **round-trip `bson.Marshal`→`Unmarshal`** — fixture buatan tangan menguji bentuk yang kita tulis, bukan bentuk yang driver hasilkan.
3. **`date` tidak selalu tengah malam** — 2.888 baris item di 19:00 UTC = **02:00 WIB hari berikutnya**, kembaran baris 00:00 hari sesudahnya. Binning UTC membuat satu hari membawa belanjanya + belanja besoknya; **total bulanan tetap benar sehingga invarian tetap hijau** — yang salah angka hariannya. `hariShopeeDari()` menggeser ke WIB; jendela query dilebarkan ±1 hari lalu disaring ulang di memori dengan definisi hari yang sama.
4. **Field turunan skalanya palsu** — `cpc` 1.787.289.342 pada baris ber-expense Rp857.899; hanya `report.expense` dan `report.broad_gmv` yang dibaca.

`item_id` Shopee adalah id **produk** yang memayungi banyak SKU varian; biaya item **diprorata per revenue varian** hanya di level product (level shop menerima biaya utuh aktual), dan hanya ditandai perkiraan bila item memayungi >1 entitas.

### Lazada

Nol koleksi iklan/video/live di `integration_db` (hanya finance). Order Lazada masuk tab laba toko & produk; tab kampanye/iklan/video permanen kosong dengan alasan lewat `unavailable_channels`. Job laba Lazada **sengaja tidak diaktifkan** di `channelProfitBawaan` — satu baris kode bila ingin dinyalakan.

## Alokasi Bundel & Mapping SKU

- **SKU bundel** (mis. `PJG-002 + PJG-003 + PJG-004`) punya beberapa baris `product_sku_mappings`, satu per komponen. Versi lama menjatuhkan **seluruh** kolom uang ke satu master "pemenang" dan hanya membebankan HPP komponen pemenang — biaya komponen lain menguap, komponen kalah tampil ber-HPP tanpa revenue. Kini: kolom uang (revenue/settlement/fee/retur/ads) **diprorata per nilai HPP komponen** (`hpp_per_pcs × qty_per_unit`; bagi-rata ditolak dengan data — preseden varian Shopee), sisa pembulatan ke porsi terakhir sehingga jumlah persis; **HPP tidak diprorata** — tiap komponen menanggung biaya aktualnya. Total lintas produk tak berubah (dikunci uji); total HPP naik karena biaya yang dulu menguap kini terbebankan — koreksi understatement.
- **Pembersihan mapping T12** (baris ganda salah-input yang bukan bundel, mis. SKU `DR FAY SERUM` ber-baris "Cream" dan "Serum"): baris salah-input **ditandai** `dinonaktifkan_pembersihan: true` (bukan dihapus — reversibel per batch), baris terpilih diisi `master_sku` + `diisi_pembersihan: true`. Semua pemuat `product_sku_mappings` wajib lewat `filterMappingAktif()` (dijaga uji AST). Eksekutornya **generator skrip mongosh idempoten** (`terapkan_pembersihan.go` — tidak menulis Mongo dari kode; skrip menolak jalan kedua). Diterapkan production 2026-08-02: 62 SKU diisi, 81 baris dinonaktifkan.

## Aturan Pemakaian Angka (larangan hitung ganda)

Beberapa kolom di service ini **tampak seperti komponen kerugian tetapi bukan**, dan sebagian lain **bernama nyaris sama tetapi berbeda arti**, dan menjumlahkannya ke laba menghasilkan angka dobel yang terbaca sah. Sampai 2026-08-26 seluruh aturan di bawah hanya hidup sebagai komentar di berkas Go-nya, jadi siapa pun yang merancang layar dari dokumentasi saja tak punya cara mengetahuinya. Kegagalannya tidak pernah muncul sebagai error, hanya sebagai angka yang salah dan masuk akal.

### `24h_live_gmv` — GMV 24 jam setelah menonton (`live_client_tiktok_shop.go`)

Dikirim TikTok pada tiap sesi `shop_lives/performance`, **belum disimpan ke mart per 2026-08-27**.

⛔ **JANGAN menjumlahkannya dengan `gmv`.** Dok resmi TikTok: *"the total amount paid for orders within 24 hours of viewing this LIVE, **including returns and refunds**"*. Dua bedanya dari `gmv`, dan keduanya membuat penjumlahan salah: jendela waktunya **setelah** siaran (bukan di dalamnya), dan retur **tidak** dipotong. Terukur di produksi: pada 21 dari 331 sesi angkanya berbeda, bisa **lebih besar** dari `gmv` (07-04: gmv 386.223 vs 24h 482.663) dan bisa terisi saat `gmv` nol. Untuk KPI host yang diukur adalah penjualan **selama** siaran, jadi yang dipakai `gmv`.

### Tiga angka penjualan live yang mudah tertukar

`sku_orders` (pesanan **dibayar**) · `created_sku_orders` (termasuk COD/PayLater **belum lunas**) · `items_sold` (**unit**; satu pesanan berisi tiga unit dihitung tiga). Ketiganya dikirim bersamaan pada tiap sesi dan salah pilih **tidak menghasilkan galat apa pun** — hanya angka yang meleset dan tetap masuk akal. Juli Kyura: 6.947 · 7.142 · 7.093, sementara catatan manual HR 6.933. KPI konversi memakai `sku_orders`; `mart_live_sessions.orders` sudah berisi field itu meski namanya telanjang.

### `iklan_sia_sia` — porsi belanja iklan pada order retur (`iklan_sia_sia.go`)

Terpasang di `/returns/detail`. Menjawab: **berapa bagian dari belanja iklan yang sudah terlanjur keluar yang ternyata tak menghasilkan penjualan yang bertahan.**

⛔ **Ini BUKAN kerugian tambahan.** `ads_cost` level product tak pernah dialokasikan ulang saat retur terjadi; ia sudah menanggung retur sejak awal. Produk terjual Rp100 jt dengan iklan Rp10 jt lalu Rp60 jt diretur menghasilkan revenue efektif Rp40 jt sementara `ads_cost` **tetap** Rp10 jt. Angka ini adalah bagian dari Rp10 jt yang sudah terbayar, bukan uang baru yang hilang. Konsekuensinya:

1. **JANGAN menjumlahkannya ke `gross_profit` atau laba mana pun.** Laba sudah dikurangi `ads_cost` seluruhnya, termasuk porsi ini. Menguranginya lagi menghitung belanja yang sama dua kali.
2. **JANGAN menjumlahkannya dengan beban packing** (`OrdersBerresi` × tarif). Beban packing uang **fisik** tambahan; ini bukan. Digabung jadi satu "total kerugian retur" hasilnya dobel.
3. **JANGAN me-rename-nya jadi `kerugian_iklan`** di lapisan mana pun. Penamaan itu bukan kosmetik — ia satu-satunya hal yang mencegah pembaca melakukan (1) dan (2).

Yang **sah**: mengurutkan produk atau order menurut besar belanja iklan yang terbuang, untuk memutuskan retur mana yang paling mahal dan layak diperbaiki lebih dulu.

**Rumusnya** `porsi_item = nilai_item / revenue_produk_hari_itu`, lalu `nilai += ads_cost_produk_hari_itu × porsi_item`. Pembaginya **revenue, bukan qty**: qty mengandaikan tiap pcs produk yang sama menelan belanja iklan yang sama, andaian yang runtuh begitu harga per pcs berbeda dalam satu hari (bundel, diskon, flash sale) — di produksi itu keadaan normal, bukan kasus tepi. Rasio `> 1,0` **dibiarkan apa adanya**, tidak dipangkas, supaya ketidakcocokan mart terlihat alih-alih tersembunyi di balik angka wajar.

⚠️ **Jalur `campaign_id` per order NIHIL di produksi** (tak satu pun order membawanya), jadi atribusinya lewat rantai SKU dengan cakupan ~88%. Yang 12% **dicacah dan dikirim ke FE**, tidak disembunyikan, dan dipecah **per sebab** karena tiap sebab menuntut tindakan berbeda: `bundel_sejati` (butuh keputusan produk), `master_kosong` (mapping dilengkapi), `tanpa_baris_mart` (sync dijalankan — artinya "belanjanya tidak diketahui", **bukan** nol), `revenue_mart_nol` (pembagi nol, porsinya tak terdefinisi; dibiarkan jadi Inf/NaN akan menggagalkan **seluruh** `encoding/json`). Field-nya **pointer**: `nil` = tidak dihitung (mart gagal dibaca), `0` = dihitung dan hasilnya nol. `item_dihitung` dan `item_dikecualikan` **selalu** dikirim berpasangan — Rp50 rb dari 1 dari 4 item adalah batas bawah, Rp50 rb dari 4 dari 4 adalah angka lengkap, dan tanpa kedua cacah itu FE tak punya cara membedakannya.

### `pembatalan` — kolom pembatalan per toko di `/profit/shops` (`pembatalan_toko.go`)

⛔ **Pembatalan bukan komponen laba.** Blok ini tidak boleh mengurangi `revenue`, `gross_profit`, atau angka laba mana pun. Bukan kehati-hatian, melainkan pencegahan hitung ganda: order yang batal **sebelum** kirim tak pernah masuk revenue sama sekali, sedangkan order yang dikirim lalu kembali sudah masuk kolom `retur` yang **sudah** dikurangkan di jalur laba. Menguranginya sekali lagi menggerus laba dua kali, dan gejalanya bukan error melainkan keluhan "laba lebih kecil dari yang saya hitung sendiri" — yang butuh berhari-hari dilacak balik. Dijaga `TestPembatalanTidakMengubahAngkaLaba`.

⛔ **`orders_dikirim` adalah HIMPUNAN BAGIAN dari `orders`, bukan kolom sejajar.** Menjumlahkan keduanya menghitung order yang sama dua kali. Dipisah karena "semua batal" dan "yang barangnya sudah dikirim" menuntut tindakan berbeda: yang kedua berarti barang sudah di jalan dan perlu ditarik balik, biaya nyata yang tak ada pada yang pertama.

Penandanya **`shipped_at`** (fakta tercatat), bukan perkiraan dari kolom kurir. Terukur: dari 14.772 order batal/retur Juli 2026, yang ber-`shipped_at` 3.949 dengan 99% di antaranya punya resi, sementara yang tanpa `shipped_at` hanya 2% punya resi — korelasi 99%/2% itulah buktinya. **Batasnya wajib dinyatakan**: order yang dikirim tanpa `shipped_at` tercatat akan terhitung belum dikirim, jadi angka ini **batas bawah** dan tak boleh dibaca sebagai "sisanya dipastikan masih di gudang".

⚠️ **Sengaja beda penanda dari `BarisRetur.OrdersBerresi`**, yang memakai **resi**. Keduanya menjawab pertanyaan berbeda: resi terbit saat label dicetak (menjawab berapa biaya packing terlanjur keluar), `shipped_at` menandai keberangkatan sesudahnya. Terukur 14 Jul–13 Agu 2026 atas 11.581 order batal/retur: 2.777 punya resi, 2.549 ber-`shipped_at`, irisannya 2.549 — resi **superset sempurna**, dengan 228 order yang sudah dilabeli lalu dibatalkan sebelum berangkat. Dua penanda berbeda untuk dua pertanyaan berbeda itu sah; yang tak boleh adalah dua penanda berbeda untuk pertanyaan yang **sama**.

Penggabungan lintas-koleksi ini (mart + `transaction_orders`) berdiri di atas tiga syarat yang **diperiksa, bukan diasumsikan**: `shop_id` bertipe string di kedua koleksi dengan ruang-nama sama (verifikasi prod 2026-08-03, kelima `shop_id` `team_shops` ditemukan apa adanya di mart, jadi pencocokannya **lurus tanpa normalisasi** — memangkas atau melapisi id "supaya cocok" justru akan menyamakan id mirip lintas channel); kuncinya terisi pada populasi yang dipakai; dan saringannya sebangun. **Bila salah satu syarat kelak tak berlaku, yang benar adalah MENCABUT kolom ini, bukan menambalnya.**

### `kepemilikan` vs `collaboration_type` di `/affiliate` (`kepemilikan_affiliate.go`)

Dua **sumbu independen** yang mudah tertukar, dan yang satu tak boleh menggantikan yang lain:

| Sumbu | Menjawab | Sumber |
|---|---|---|
| `collaboration_type` | Sifat **order**-nya: target collab (kita undang) vs open collab (kreator datang sendiri) | TikTok |
| `kepemilikan` | Siapa **karyawan** di balik username | Daftar akun internal kita (`icc_affiliate_accounts`) |

Justru **persilangannya** yang berguna: akun kita yang ordernya masih open collab berarti belum didaftarkan target collab di toko itu, sementara username tak terdaftar yang ordernya target collab adalah kandidat akun internal yang belum didata.

Kolomnya hanya dua keadaan — `internal` dan `belum_terdaftar`. **`belum_terdaftar` sengaja BUKAN "luar"**: daftar kita bisa belum lengkap, dan menyebutnya kreator luar menyatakan sesuatu yang belum tentu benar. Dua nilai lain (`ada_pemegang`, `belum_ditugaskan`) **hanya dipakai sebagai saringan**, tak pernah ditulis ke kolomnya, karena "akun kita yang belum ada pemegangnya" adalah satu-satunya kelas yang menuntut tindakan (pekerjaan SPV di ICC Management, bukan kekurangan data). Alias **ikut** dihitung: order lama masih tercatat dengan handle sebelum penggantian, dan membuangnya membuat riwayat kreator itu mendadak jatuh ke "belum terdaftar" tepat pada hari handle-nya berubah.

⚠️ Nilai saringan tak dikenal **ditolak 400**, tidak diperlakukan sebagai "semua". Alasannya tajam di sini: untuk `belum_terdaftar`, himpunan kosong berarti **seluruh baris** — jawaban yang salah dan tampak wajar. Karena itu kegagalan membaca daftar akun ditandai `errKepemilikan` dan **tidak boleh ditelan** begitu ia dipakai menyaring, walau boleh ditelan selama ia cuma kolom.

## Kejujuran Data (bagian yang tidak boleh dihapus)

Service ini menyimpan **alasan ketidaklengkapan bersama datanya**, bukan membiarkan angka kosong dibaca sebagai nol.

### `revenue`: TikTok sudah setelah diskon (PR #1109), Shopee masih harga list

Bagian ini ditulis paling atas karena ia mengubah cara membaca setiap angka turunannya.

`sumber_agregasi.go` mengisi `Revenue: it.Total`, yaitu jumlah `items[].total` order — jadi maknanya ditentukan oleh apa yang ditulis [[Microservices - Integration Service]] ke field itu.

**TikTok — SUDAH DIPERBAIKI (PR [#1109](https://github.com/bip-itteam-internal/bip-erp/pull/1109), live 2026-08-09).** `TransformFromTiktok` kini memetakan `items[].price` dari `line_items[].sale_price` (harga setelah diskon penjual), bukan `original_price`. Pemicunya: kolom omzet ERP **46% lebih besar** daripada yang ditampilkan Seller Center dan Desty. Terverifikasi terhadap ekspor Desty 9 Jul–7 Agt — ERP `5.284.842.600` vs Desty `3.608.539.700`; memakai `sale_price` memberi `3.625.632.734`, **selisih 0,47%**. Desty mendokumentasikan sendiri bahwa hanya TikTok yang memakai subtotal setelah diskon sementara marketplace lain memakai harga sebelum diskon.

Backfill `transaction_orders` dijalankan sejak **1 Agustus 2026** (`cmd/ttitempricebackfill`, 12.806 order diubah, 0 mismatch); sesudahnya **13.152 dari 13.152 order** cocok `payment.sub_total` dengan beda Rp0, dan mart sejajar dengan sumber tanpa selisih. Periode sebelum 1 Agustus sengaja dibiarkan — fakturnya sudah terbukukan dan dilindungi gerbang faktur-permanen.

**Shopee & Lazada — tetap harga sebelum diskon, dan itu benar.** Keduanya sudah sejajar dengan Desty apa adanya (Shopee +1,80%, Lazada −1,20%); mengubahnya justru akan menjauhkan sejauh Rp27,7 juta ke arah sebaliknya.

Angka historis di bawah ini diukur **sebelum** perbaikan dan tetap dipertahankan karena menjelaskan mengapa perbaikan itu diperlukan — untuk TikTok kolom "Diskon penjual" kini sudah tercermin di `revenue`, untuk Shopee belum.

Dengan `sum(items[].total)` **pra-#1109** sebagai 100:

| Channel | n | Diskon penjual | Dibayar pembeli | Settlement |
|---|---|---|---|---|
| TIKTOK | 16.574 | **31,0%** | 71,0% | **49,8%** |
| SHOPEE | 3.426 | 7,2% | 82,2% | 71,0% |

**Kita mendiskon TikTok empat kali lebih dalam daripada Shopee**, dan tak ada satu kolom pun yang menampilkannya. Potongan marketplace justru lebih besar di Shopee (21,8% berbanding 19,2%); yang membuat TikTok mahal adalah diskon kita sendiri.

Konsekuensinya — **sejak PR #1109 hanya berlaku penuh untuk Shopee**; untuk TikTok diskon penjual kini sudah terpotong di `revenue`, sehingga jarak ke uang nyata tinggal potongan marketplace:

- **`roasAgregat = revenue / adsCost`** untuk **Shopee** masih berdiri di atas harga banderol. Untuk **TikTok** sekarang berbasis harga setelah diskon — masih di atas settlement (potongan marketplace ~19,2% belum terpotong), tapi tak lagi melebih-lebihkan sebesar dua kali lipat seperti sebelumnya.
- **`iklanPersenRevenue = adsCost / revenue`** ikut mengencang untuk TikTok dengan alasan yang sama; untuk Shopee tetap understated.
- Ambang `roas_min` 3,2 adalah angka tim dari Master Roadmap yang **basisnya tak pernah dinyatakan** — dan basis pembandingnya kini **berbeda antar-channel**, sehingga membandingkan ROAS TikTok dan Shopee terhadap satu ambang yang sama menjadi tidak setara. Perlu diputuskan ulang.
- **`gross_profit` TIDAK terpengaruh — terverifikasi ulang sesudah #1109.** Ia dihitung dari `net_settlement`, HPP dari `o.Qty`, dan `revenue` tidak muncul dalam rumusnya (`attribution.go:133`). Yang bergeser hanya sebaran `ads_cost` antar-SKU pada jalur prorata (totalnya tetap). Gerbang laba pada vonis halaman depan tetap sehat.
- **Efek samping menguntungkan**: margin yang dihitung manual (`gross_profit ÷ revenue`) untuk TikTok membaik dari 18% ke 26%, mendekati margin sejati 35% (`gross_profit ÷ net_settlement`) — sebelumnya pembilang memakai settlement sementara penyebut memakai harga banderol.

`fee_marketplace` = `TotalPlatformCommission + TotalServiceFee + TotalAffiliateCommissionFee`, diprorata per item. **Komisi affiliate sudah termasuk.** Yang tak punya kolom sama sekali: **diskon, ongkir, dan adjustment**.

Identitasnya lebih dulu dibuktikan tim di `services/integration/cmd/insentifprobe` terhadap data TikTok Juni 2026: `total_original_price − total_discount = subtotal_after_seller_discount`, lalu `subtotal − (service + shipping + affiliate + commission + adjustment + refund) = total_settlement_amount`.

**Keputusan basis ROAS masih terbuka (TBD)** dan bukan keputusan teknis: ia menentukan lencana yang sudah menilai belanja iklan berjalan.

### Kolom "Kebocoran" DIBATALKAN, dan sebabnya bukan aritmetika

Kolom yang menjumlahkan jarak revenue ke settlement dibangun penuh, diuji, lalu **dibatalkan sebelum dikirim**. Rumusnya `(revenue − net_settlement) + retur` dan ia **tertutup persis**: `revenue − kebocoran − hpp − ads_cost = gross_profit`, terverifikasi terhadap `ComputeGrossProfit` termasuk lewat agregasi bulanan, lintas-toko, dan lintas-channel.

**Aritmetika yang benar tidak membuat namanya benar.** Rumus itu menjumlahkan diskon kita sendiri, potongan marketplace, ongkir, komisi kreator, dan retur menjadi satu angka yang pemiliknya berbeda-beda, lalu menyebutnya kebocoran. Menamai diskon yang kita putuskan sendiri sebagai kebocoran menyembunyikan satu-satunya suku yang benar-benar dapat ditindaklanjuti.

Satu entri Kamus Metrik dengan definisi itu sempat tayang sehari lalu dicabut (erp-frontend PR #867). Penggantinya **rantai pengurangan bernama** yang menyebut pemilik tiap suku, dan itu menuntut `total_original_price` serta `total_discount` masuk mart lebih dulu (TBD).

Dicatat di sini justru karena rumusnya terlihat benar: tanpa catatan ini, orang berikutnya akan membangunnya lagi dan tak satu pun test akan memerahkannya.

### Penanda lain

- **`attribution_kolom` — penanda aktual vs perkiraan melekat PER KOLOM**, bukan per baris. Peta `nama kolom → alasan terbaca manusia`; kolom yang tidak ada di peta = **aktual**; kunci = persis tag json kolom. Penanda tingkat-baris sebelumnya memvonis seluruh baris: 2.384 baris campaign bertanda `estimated` dibaca pengguna sebagai "biaya iklan tidak valid" — padahal `ads_cost`-nya aktual, Rp1.289.007.856 cocok persis belanja GMV Max; yang perkiraan **labanya** (retur tak teratribusi ke level iklan, dasar revenue kotor). `attribution`/`attribution_note` kini **turunan** — utang teknis, dihapus setelah FE membaca `attribution_kolom`.
- **`kolom_tidak_berlaku`** (lihat *Kontrak amplop*) membedakan "kolom ini tak akan pernah berisi di level ini → hilangkan" dari "sel ini kosong → tak tersedia". Kolom struktural yang membawa angka nyata tetap dikirim; hanya nilai nol yang dinihilkan — `retur = 0` di level shop adalah kabar baik nyata dan tetap `0`.
- **`master_sku` + `belum_termapping`** pada level product: baris ber-master kosong tetap tampil sendiri dengan SKU aslinya — tidak dibuang, tidak dilebur jadi "lain-lain". Sisa terbesar kini SKU **bundel ber-master-kosong** yang isi paketnya perlu konfirmasi bisnis (menetapkan komponen paket bukan urusan tebakan kode).
- **`icc` — penanggung jawab toko, gabungan DUA sumber** (`bacaIndeksICCGabungan`, `sumber_penanggung_jawab.go`): `integration_db.icc_account_mappings` (orang, TikTok), `integration_db.department_shops` (**departemen**, sejak 2026-08-29 — sebelumnya `team_shops`+`marketing_teams`; nama diberi awalan `Departemen `, tidak menyamar jadi orang). ⚠️ **Bukan lagi tiga sumber** — `insentive_db.employee_performance_mappings` beserta `insentive_db.go` **dihapus 2026-08-12** ([[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] §9 membalik arah ketergantungan: insentif kini konsumen `icc_account_mappings`+`department_shops`, bukan sumber di sini). **Cakupan "insentive saja 2 toko (3,5%) → gabungan 15 toko (51,2%)" adalah angka LAMA dari saat masih tiga sumber dan belum diukur ulang (TBD)**. **Sumber TIM diganti `department_shops` 2026-08-29** (branch `feat/penanggung-jawab-department-shops`, belum merged) — dipicu bug link mati di blok "Konteks per departemen" Beranda, bukan bagian rencana Fase Contract semula. ⚠️ **Ganti kode saja TIDAK mengubah data historis**: atribusi ICC dibakar ke `mart_profit_attribution.icc` saat sync (lihat §Job Sync), jadi baris mart lama tetap membawa atribusi `team_shops` sampai di-backfill (`?hari=120` maks) atau tersapu siklus 48-jam alami. Sumber **menambah, tidak menimpa** (dedup lintas sumber per employee_id/nama-departemen); satu sumber gagal → sumber lain tetap dipakai. Membawa **daftar** pemegang (satu toko bisa dipegang lebih dari satu orang — terverifikasi production), bukan satu nama. Status **empat**: `ditetapkan` / `belum_ditetapkan` (tim perlu melengkapi mapping) / `tak_tersedia` (melengkapi mapping tak akan mengisinya — level `ad`, karena `shop_id` 0 dari 10.650) / `sebagian_ditetapkan` (hanya baris product lintas-toko yang tokonya bercampur).
- **`SpendVSA` dan `SpendGMVMax` tetap terpisah** sampai penyimpanan; **`AdaSumberLain`** menandai video ber-spend di tab lain.
- **`gross_profit` video**: nil = **tak pernah dihitung** (organik murni / Shopee), bukan nol; yang terisi membawa catatan basis (fee & retur tak termasuk; cakupan sejak jendela sync ≠ GMV seumur hidup).
- **URL tidak pernah dikarang**: `video_url` kosong bila `creator_username` tak ada (tautan tebakan pasti 404); **URL halaman produk tidak dibangun sama sekali** — polanya tak dapat diverifikasi (situs menjawab 200 "Security Check" untuk id asli maupun palsu), yang dikirim `product_title` + `product_image_url` + `product_item_group_id`.
- **`EntityName` tidak pernah kosong**: fallback ke id apa adanya — id mentah masih dapat ditelusuri ke seller center.
- **`sync_state.last_error` dipakai juga untuk CATATAN**: SKU tanpa HPP, belanja tak terpetakan (`AdsCostTakTerpetakan` untuk mapping tak kenal; `AdsCostTakTerpetakanProduct` untuk item diiklankan tanpa order — sebab beda, obat beda), cakupan ICC, baris basi yang di-prune.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Supervisor & Leader Marketing | Pembaca dashboard laba per toko, kampanye, video | Lewat gateway dan menu dashboard di [[APP - Web ERP]] | Web |
| Advertiser / ICC / Host Live | Melihat performa kreatif dan iklan miliknya; namanya tampil sebagai penanggung jawab toko | idem | Web |
| Tim IT / operator | Memicu job, membaca `sync_state` dan `GET /jobs/status` saat data janggal | `POST /jobs/:name/trigger` | Web, terminal |

- **Tujuan**: melihat laba yang sudah dikurangi HPP dan biaya iklan, bukan sekadar omzet kotor.
- **Pain point**: angka marketplace dan angka iklan datang dari sumber berbeda dengan definisi berbeda; tanpa atribusi eksplisit, laba mudah dibaca terlalu optimis.
- **Aksi utama**: buka dashboard bulanan, drill: toko → kampanye → iklan → video; produk (lintas toko) → per toko → per tanggal → order; retur → order.

## Belum Diimplementasikan / Catatan

- **`cpa_maks` tersimpan, tervalidasi, terindeks, dan dikirim ke FE — tetapi TIDAK DIBACA apa pun.** `mart_profit_attribution` sengaja tak menyimpan cacah order (tercatat di `matrix_sku_shop.go`: "orders SENGAJA tak ada"), jadi CPA tak dapat dihitung dari mart ini. Separuh dari "ambang keputusan" karena itu mati. Perlu keputusan produk: tambah cacah order ke agregasi laba, buang `cpa_maks` dari ambang, atau biarkan sebagai angka rujukan yang sengaja tak memvonis. Sampai diputuskan, layar tak boleh menampilkannya seolah ia sedang menilai sesuatu.
- **`/beranda` dan `/ambang` belum pernah dijalankan lewat gateway.** Seluruh pengujiannya memakai sumber palsu. Dua bug terparah yang tertangkap review hanya muncul terhadap Mongo sungguhan dan keduanya membalas **200** dengan rapi: sort kosong yang ditolak Mongo, dan `Limit` tak disetel yang memotong 500 baris teratas.
- **Dua route ada di kode tetapi belum terdokumentasi**: `/toko` dan `/profit/items`. Mendarat di `main` sesudah audit 2026-08-02. `/kpi/kinerja-toko` **sudah terdokumentasi** sejak 2026-08-11 (bab **Pengumpul KPI**). Lihat [[API - Marketing Analytics Service]].
- ⚠️ **`/kpi/kinerja-toko` kini membawa `jumlah_video`** (PR [#1049](https://github.com/bip-itteam-internal/bip-erp/pull/1049) merged 6 Agustus 2026, **belum di-deploy**), dicacah dari `tt_shop_video_performances` di `integration_db` lewat pembaca baca-saja yang sudah ada. **Kegagalan mencacah tidak menggagalkan jawaban** — nilainya jatuh ke 0 dan hanya tercatat di log, sehingga tak terbedakan dari nol sungguhan oleh pemanggilnya. Konsekuensi itu diterima sadar (video berbobot 0,30 dari 1,00) tetapi wajib diketahui siapa pun yang membaca angkanya.
- 🟡 **`GET /kpi/kinerja-affiliate` (`kpi_affiliate.go`)** — agregat affiliate **PER-INDIVIDU** satu karyawan satu periode, bahan skor KPI staf Affiliate Acquisition. ✅ **Sudah di `origin/main` sejak 2026-08-24** (catatan lama "branch `feature/workspace-position`, belum merge" sudah usang); status deploy belum diverifikasi. Terverifikasi di DEV 2026-08-22. Gerbang **kunci layanan** yang sama dengan `/kpi/kinerja-toko` (`GerbangKunciKinerjaToko`). Query wajib `periode`·`employee_id`·`key`; balasan `conversion` (distinct `order_id`), `gmv`, `actual_commission`, `akun_diminta`/`akun_berdata`. **Rute ini sendiri** yang mencari akun affiliate milik karyawan lewat `icc_affiliate_accounts` di `integration_db` (username+alias → `employee_id`). Karyawan tanpa akun dijawab **400** (bukan 200 nol); **nol order pada akun yang ada = 200 bernilai 0** (nol yang sah, bukan galat). Batas atas periode **eksklusif** (`$lt`). ⛔ **Gap data yang menentukan**: staf posisi "Affiliate" (yang dinilai) **belum dipetakan** ke akun di `icc_affiliate_accounts` — akun yang terpetakan justru milik 17 staf **ICC**. Jadi metriknya siap tapi **kosong** sampai staf Affiliate dipetakan lewat ICC Management. Data ditarik dari prod ke dev untuk verifikasi (46.212 order, 19 akun). Lihat [[API - Marketing Analytics Service]] & [[HRIS - Otomasi Skor KPI]].
- 🟡 **`GET /kpi/kinerja-affiliate-tim` (`kpi_affiliate_tim.go`)** — agregat affiliate **PER-TIM-CHANNEL** (TikTok/Shopee), model yang MENGGANTIKAN per-individu di atas untuk staf Affiliate. Menentukan channel staf dari `affiliate_channel_team` (integration_db) lalu menghitung TOTAL channel: `conversion` (TikTok = distinct `order_id` `affiliate_orders`; Shopee = Σ`orders` `shopee_affiliate_performance`) dan `affiliate_aktif` = affiliator yang **dapat ≥1 order** pada periode (revisi 2026-08-25, order-based, bukan lagi upload konten): Shopee = distinct `affiliate_username` dengan `orders>0` di `shopee_affiliate_performance`; TikTok = distinct `creator_username` ber-order di `affiliate_orders`. Gate kunci layanan sama. Belum dipetakan channel → 400. Terverifikasi DEV Jul lewat endpoint (Shopee: conv 8.533, aktif 1.693; TikTok: aktif 2.323).
- **JEBAKAN LINGKUNGAN, bukan cacat kode: `TestMuatHariProfitMerakitLewatRakitInputProfit`** (`spend_per_sku_test.go`) memindai TEKS SUMBER `spend_per_sku.go` untuk menemukan akhir sebuah fungsi. Ia **gagal pada salinan kerja yang ber-CRLF**, dan lulus pada yang LF. Blob repo sendiri **murni LF** (terverifikasi byte: `spend_per_sku.go` 10.245 byte, CR=0), jadi **test ini TIDAK merah di `main` dan tidak merah di CI**. Yang membuatnya merah di sebagian mesin adalah `core.autocrlf=true` di **system gitconfig** Windows, yang mengubah berkas jadi CRLF saat checkout. Obatnya di sisi mesin: `git config core.autocrlf false` lalu checkout ulang worktree-nya. Catatan ini ada karena kegagalannya sangat meyakinkan sebagai "bug kode" padahal bukan.
- ~~`GET /matrix/sku-shop` masih stub~~ — **SUDAH TIDAK BENAR, dicoret 2026-08-26.** Terimplementasi penuh sejak 2026-08-02 (`matrix_sku_shop.go` 576 baris, `matrix_sku_shop_test.go` 631 baris, tanpa satu pun penanda stub/TODO tersisa di kodenya). Baris ini bertahan salah **tiga minggu lebih** di dua dokumen sekaligus, dan itu kelas kesalahan yang paling mahal di vault: pembaca menyimpulkan fiturnya belum ada lalu membangunnya ulang. Rinciannya kini di §Retur & analitik lain.
- **`mart_buyer_cohort` kosong** di production; `/cohort` membalas kosong. (`mart_live_sessions` sudah terisi **5.482 sesi** per pengukuran 2026-08-30, naik dari 4.836 pada 2026-08-22.)
- **`live_shifts` masih 0 dokumen**, diukur ulang **2026-08-30** (sebelumnya 2026-08-26). Rute, gerbang, dan halamannya sudah live di PROD, tetapi belum ada host yang menekan tombolnya — jadi fitur ini **belum terbukti bisa dipakai**, hanya terbukti ter-deploy. Verifikasi lewat gateway (tekan Mulai, pastikan dokumen lahir, Jeda/Akhiri, GMV muncul setelah sync) belum dijalankan. ⚠️ Nol yang bertahan selama sebulan lebih layak dibaca sebagai **pertanyaan**, bukan sekadar "belum sempat": kru yang paling butuh fitur ini memegang beberapa akun sekaligus, dan sesi keduanya tak punya tampilan sama sekali (lihat §Siaran serentak di beberapa akun).
- **`laba_kotor` pada `/live-shifts` selalu 0** dan `laba_tersedia` selalu false — penelusuran order per sesi ke `tt_shop_transaction_by_orders` + `product_costs` belum dikerjakan. Konsumen sengaja tidak merender kolom laba supaya Rp 0 tak terbaca sebagai "tidak untung". **TBD.**
- **`luar_shift` belum bermakna.** Frontend mengirim `true` untuk semua sesi karena resolusi jadwal HR (`GET /schedule` milik attendance) belum disambung; penyambungannya ditunda agar urutan menang berlapis (roster per tanggal > rotasi 21 hari > jadwal dasar) tidak disalin ke service ini dan melahirkan sumber kebenaran kedua. **TBD.**
- **Lock job & penjadwal hanya in-process** — belum aman di-scale horizontal.
- **Interval penjadwal belum bisa diubah lewat env** (hanya jam, jendela, dan flag aktif).
- **Job laba Lazada sengaja mati** di `channelProfitBawaan`.
- **Cakupan ICC 51,2%** — sisanya butuh tim melengkapi `icc_account_mappings`, bukan perubahan kode.
- **Kolom Pemegang di `/affiliate`** (2026-08-07) — kepemilikan akun kreator dari `integration_db.icc_affiliate_accounts`, **sumbu berbeda** dari `collaboration_type`: yang satu sifat order (target vs open collab, dari TikTok), yang lain siapa karyawan di balik username (dari daftar akun kita). Alias ikut dicocokkan agar order lampau tak terbaca "belum terdaftar" saat handle berganti. Tiga keadaan dibedakan: ada nama · `belum ditugaskan` (akun perusahaan tanpa pemegang) · `belum terdaftar` (di luar daftar). Bersifat pelengkap — bila koleksinya gagal dibaca, angka lain tetap tampil dan kolomnya kosong. Lihat [[Sales - ICC Affiliate Mapping]].
- `InternalURL` divalidasi saat boot tapi nilainya belum dipakai.
- Index `affiliate_orders {content_id, order_create_time}` untuk `/videos/orders` dibuat manual di production 2026-08-02 (tulis `integration_db` = di luar wewenang service ini; tercatat di komentar `cocokOrderVideo`).

## Dependensi & Integrasi

- **Sumber data (baca-saja)**: `integration_db` milik [[Microservices - Integration Service]] — `transaction_orders`, `product_sku_mappings`, `product_costs`, `tt_business_*`, `tt_shop_video_performances`, `shopee_gms_*`, `affiliate_orders`, `icc_account_mappings`, `icc_affiliate_accounts`, `team_shops`, `marketing_teams`, `department_shops` (sejak fase Contract 2026-08-29, [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] — dipakai KEDUA konsumen sekarang: saringan `/divisi` DAN kolom `icc`/"Konteks per departemen" di bawah; `team_shops`/`marketing_teams` dipertahankan sebagai dead code, belum dicabut); plus `insentive_db` milik [[Microservices - Insentive Service]] (`employee_performance_mappings`, env `INSENTIVE_MONGO_URI`). Lihat juga [[Sales - Marketplace Integration]].
- **API pihak ketiga**: TikTok Ads API `/open_api/v1.3/ad/get/` (`client_tiktok_ads_http.go`) hanya untuk tautan ad→video; metrik iklan dibaca dari Mongo, bukan API langsung. Kredensial gagal didekripsi dilewati **tapi dihitung dan dilaporkan**.
- **Gerbang**: [[CORE - API Master Gateway]] · **Konsumen**: dashboard marketing di [[APP - Web ERP]]
- **Konsep & rancangan — ⚠️ arsip Juni–Juli 2026, peta service-nya usang**: [[Sales - Marketing Dashboard (Master Roadmap)]] · [[Sales - Marketing Dashboard (Index)]] · [[Sales - Profit Engine (Design)]] · [[Sales - HPP Master (Plan)]] · [[ADR - 0008 Profit Engine Join via item_group_id]]. Ketiga dok "Marketing Dashboard" itu menulis rencananya dibangun **di dalam `integration`**, dan menyebut progres 45–50%; kenyataannya lapisan marketing & ads jadi service tersendiri (dokumen ini) sementara profit engine + HPP yang mendarat di `integration`. Audit datanya masih sahih, pembagian service-nya jangan dipakai.
- **Koleksi**: [[DB - Overview and Notes]] · **Endpoint per-route**: [[API - Marketing Analytics Service]]

## Dokumen Terkait

- [[Microservices - Integration Service]] (pemilik `integration_db`) · [[Microservices - Insentive Service]] (sumber ICC + konsumen metrik iklan untuk insentif)
- [[IT - Background Jobs & Schedulers]] (penjadwal internal service ini tercatat di sana)
- [[ADR - 0002 Database-per-Service]] · [[ADR - 0011 Integration Read Cache + Singleflight (Fase 1 Perf)]]
- [[Sales - GMV Creative]] · [[Sales - ICC Affiliate Mapping]] · [[Sales - Marketing Dashboard (Analisis Rekap)]]
- [[Sales - Marketing Analytics (Audit Ketersediaan Data)]] — metrik prototipe Direktur diperiksa satu per satu terhadap field yang benar-benar ada di service ini (ADA · RAKIT · TIPIS · TIDAK ADA)
- [[HRIS - Otomasi Skor KPI]] (memakai `mart_profit_attribution` dan `mart_video_performance` sebagai calon sumber skor KPI otomatis)

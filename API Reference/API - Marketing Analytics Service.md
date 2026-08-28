## Deskripsi

*Daftar endpoint **Marketing Analytics Service** — grounded ke kode (enumerasi seluruh pendaftaran rute di `services/marketing-analytics/*.go` non-test terhadap `origin/main`; audit 2026-08-27, **41 route** di berkas produksi termasuk `/health`). Arsitektur & semantik data: [[Microservices - Marketing Analytics Service]].*

- **Status**: ✅ Grounded ke kode (2026-08-27), **keempat-puluh-satu route punya baris di dok ini**. Route ke-41 `/kpi/kinerja-live` masuk lewat PR [#1479](https://github.com/bip-itteam-internal/bip-erp/pull/1479) & [#1486](https://github.com/bip-itteam-internal/bip-erp/pull/1486) (merged 2026-08-27); **status deploy belum diverifikasi — merged bukan deployed**. Sebelumnya 12 route tak terdokumentasi sama sekali; daftarnya + cara audit ulangnya ada di bagian **Cara mengaudit kelengkapan daftar ini** di kaki dokumen.
- **Prefix gateway**: `/api/marketing-analytics/*` → path internal tanpa prefix. Routing & auth: [[API - Index]].

## Konvensi respons

- Amplop `{rows, unavailable_channels, ...}`; `unavailable_channels` menandai channel yang datanya memang tak disediakan platform (mis. Lazada tanpa analytics konten) beserta alasannya.
- **`kolom_tidak_berlaku`** (bila ada): kolom yang di level itu tak punya sumber sama sekali — FE wajib menghilangkan kolomnya, bukan merender "—" per baris.
- Parameter enum yang tak dikenal → **400 + daftar nilai sah** (tidak jatuh diam-diam ke bawaan). Batas tanggal **hari WIB**, batas atas eksklusif.
- Endpoint drill berpaginasi: `limit` bawaan 50 maks 500, `offset`; `total: -1` = cacah gagal (bukan 0).

## Halaman depan & ambang keputusan

Lapisan baca murni di atas mart yang sudah ada; tak ada job atau koleksi `mart_*` baru selain `mart_ambang`. Status: ✅ **live di PROD dan terverifikasi lewat gateway** (2026-08-07, akun `panpan`). PR [#1080](https://github.com/bip-itteam-internal/bip-erp/pull/1080) merged, disusul [#1083](https://github.com/bip-itteam-internal/bip-erp/pull/1083), [#1084](https://github.com/bip-itteam-internal/bip-erp/pull/1084), dan [#1086](https://github.com/bip-itteam-internal/bip-erp/pull/1086).

Verifikasinya menemukan yang test tak bisa: `vonis.laba_kotor` **cocok sampai rupiah** dengan jumlah `gross_profit` di `/profit/shops`, tetapi lencananya berbunyi `rugi` di atas periode yang `catatan_perkiraan`-nya sendiri sebut belum matang. Keadaan `belum_matang` lahir dari situ, bukan dari perancangan.

| Method | Path | Catatan |
|---|---|---|
| GET | `/beranda` | Merakit vonis laba + `pembanding` + `tren` + `penggerus`/`peluang` + `penanggung_jawab`/`per_tim` + `cakupan` + `kesegaran`. Parameter sama dengan halaman lain (`dari`, `sampai`, `divisi`, `channel`) + `limit_sorotan` (bawaan 5, maks 20; nilai cacat → **400**, tidak jatuh ke bawaan). **Tidak membangun query sendiri** — memanggil ulang sumber halaman rincian, dijaga uji AST yang sama dengan `/summary` |
| GET | `/ambang` | Seluruh riwayat ambang + penanda `aktif`. **Tidak digerbang**: tiap pembaca perlu tahu terhadap apa angkanya dinilai |
| POST | `/ambang` | Tambah baris ambang. Digerbang `common.RequireMarketingLeader` (**403** tanpa role); identitas penulis dari header gateway, tak pernah dari body; `roas_min`/`cpa_maks` wajib `> 0`, `effective_from` `YYYY-MM-DD`; cacat → **400 menyebut field-nya** |
| GET | `/pagu` | Pagu belanja iklan per `channel`+`shop_id`+`bulan`, urut `bulan` lalu `created_at` menurun. **Tidak digerbang**, alasan yang sama dengan `GET /ambang`. Gagal baca dibalas **5xx, bukan `rows: []`** — "belum ada pagu yang ditetapkan" dan "database tak terbaca" menuntut tindakan berbeda (`pagu_handler.go`) |
| POST | `/pagu` | Tambah baris pagu. Digerbang `common.RequireMarketingLeader`; identitas penetap dari header gateway (tak ada `created_by` di body). `nominal` bertipe `*float64` supaya **pagu `0` yang sah** ("bulan ini memang tak dianggarkan") terbedakan dari field yang tak dikirim — `nil` → **400 `nominal wajib diisi`**. Identitas kosong → **401**, dicek sebelum menyentuh penyimpanan. Koleksinya **append-only**: koreksi datang sebagai baris baru, `paguUntuk` memilih `created_at` termuda, sehingga penilaian periode lampau tak berubah surut |
| GET | `/kurva-alokasi` | Kurva hasil-belanja per kanal untuk blok "Simulasi alokasi belanja iklan". Mencoba **TikTok · Shopee · Lazada** eksplisit; kanal yang datanya tak cukup tetap muncul membawa `alasan` (menghilang akan terbaca sebagai kerusakan). Balasannya **bukan `Envelope`** — `unavailable_channels` menerangkan batas platform ("tak akan pernah ada"), sedangkan penolakan di sini soal kecukupan data sendiri ("tunggu data terkumpul"); menyatukannya membuat dua sebab yang menuntut tindakan berbeda terbaca sama. Membawa `jumlah_terpasang`/`jumlah_ditolak`/`min_titik`/`min_r_kuadrat` dari backend, **bukan dihitung ulang FE**. **Tidak digerbang**, mengikuti `GET /ambang` dan `GET /pagu`. Memakai level `shop` (satu-satunya level yang memuat seluruh belanja dan seluruh laba kanal) |

**Vonis punya LIMA nilai**, dievaluasi berurutan: `tanpa_data` (tak ada satu baris pun) → `belum_matang` (laba `< 0` tapi minusnya hilang bila baris yang settlement-nya belum cair dikeluarkan) → `rugi` (laba `< 0`) → `waspada` (laba `>= 0` tapi ROAS `< roas_min`) → `sehat`.

`tanpa_data` ada karena tanpanya periode kosong divonis `sehat` dan melukis lencana hijau di atas nol. `belum_matang` ada karena verifikasi produksi menemukan lencana RUGI di atas angka yang catatannya sendiri sebut "belum matang, bukan rugi". **Untuk FE: `belum_matang` bukan kabar buruk dan tak boleh berlencana merah** — artinya angkanya akan naik sendiri setelah settlement cair.

**Nilai `null` berarti tak terhitung, bukan nol**: `roas` saat belanja nol, `iklan_persen_revenue` saat revenue nol, `delta_persen` saat pembanding nol.

**`cpa_maks` tersimpan dan dikirim tetapi TIDAK DIBACA apa pun** — `mart_profit_attribution` sengaja tak menyimpan cacah order, jadi CPA tak dapat dihitung. Separuh ambang keputusan menunggu keputusan produk.

`unavailable_channels` pada endpoint ini dapat memuat penanda **pemancungan** ber-channel `SEMUA`: baris sumber menyentuh batas keamanan pembacaan, jadi angkanya bisa kurang. Itu bukan kegagalan — barisnya ada — jadi layar tetap menampilkannya sambil menyebut jumlahnya mungkin belum utuh.

## Laba (`mart_profit_attribution`)

| Method | Path | Catatan |
|---|---|---|
| GET | `/summary` | Ringkasan lintas sumber |
| GET | `/profit/shops` | `granularitas=bulanan\|harian` (bawaan bulanan) · `bulan=YYYY-MM` · `sort_by`/`sort_dir`. ⛔ Membawa blok **`pembatalan`** (`orders`/`nilai` + `orders_dikirim`/`nilai_dikirim`). **Bukan komponen laba** — tak boleh mengurangi `revenue`/`gross_profit` (batal-sebelum-kirim tak pernah masuk revenue; yang kembali sudah masuk `retur`). `orders_dikirim` **himpunan bagian** dari `orders`, bukan kolom sejajar: menjumlahkannya menghitung order yang sama dua kali. Aturan lengkap: [[Microservices - Marketing Analytics Service]] §Aturan Pemakaian Angka |
| GET | `/profit/products` | + `lingkup=lintas_toko\|per_toko` (bawaan lintas_toko; baris gabungan membawa `jumlah_toko`, `shop_id` kosong). Berkunci **kode master** (`PJG-004`) dan **memecah bundel ke komponen** |
| GET | `/profit/items` | Laba per **ID produk marketplace** (`LevelItem`) — satuannya **judul listing**, sepadan laporan "Penjualan Per Produk". Inilah yang dipanggil menu **Profit per Produk**. **Tanpa `hiasAmplop`**: `items[].id` terisi 100% di ketiga channel (verifikasi prod Juli 2026), jadi tak ada batas platform yang perlu dinyatakan |
| GET | `/profit/skus` | Laba per **SKU master** (`items[].sku` apa adanya, `LevelSKU`) — satuannya "SKU Master", sepadan laporan "Penjualan Per Varian". Inilah yang dipanggil menu **Profit per SKU**. Tanpa `hiasAmplop` (alasan sama) |
| GET | `/profit/campaigns` | idem shops |
| GET | `/profit/ads` | + `campaign_id` (filter drill); baris membawa `metrik_iklan` (15 metrik API, `spend` per mata uang) |
| GET | `/profit/orders` | Drill product → order. `entity_id` **wajib**; `bulan` XOR `dari`/`sampai`; `termasuk_batal=true\|false` (bawaan false — CANCELLED dikecualikan, konsisten agregasi); respons + `sku_tercakup` |

⛔ **`/profit/products`, `/profit/items`, dan `/profit/skus` TIDAK boleh dijumlahkan silang.** Ketiganya menjawab pertanyaan yang berbeda atas koleksi yang sama: satu listing memayungi banyak SKU, satu SKU dijual lewat banyak listing, dan satu SKU bundel mengandung banyak kode master. Menjumlahkan dua di antaranya menghasilkan angka yang tak berarti apa-apa tetapi tampak wajar, dan itulah yang membuatnya berbahaya. Nama menunya sengaja **tidak** sejajar dengan nama path-nya: menu *Profit per Produk* → `/profit/items`, menu *Profit per SKU* → `/profit/skus` (`handler_mart.go`).

## Video & live

| Method | Path | Catatan |
|---|---|---|
| GET | `/videos` | `VideoRow` (tab VSA/GMV Max/organik); + `gross_profit` (nil = tak pernah dihitung), `product_title`/`product_image_url`/`product_item_group_id`, `ad_id`, `channel`, `synced_at`. **Menolak `granularitas` (400)** — snapshot kumulatif |
| GET | `/videos/orders` | Drill video → order **affiliate saja** (`affiliate_orders`, `content_type="VIDEO"`). `video_id` **wajib**; field `cakupan` selalu terisi |
| GET | `/lives` | `mart_live_sessions`, + `iklan_live` & `kampanye_live` di amplop (`handlerLives`). ⚠️ Baris ini sempat berbunyi "koleksi masih kosong" — **sudah tidak benar**: terisi **4.836 sesi** per verifikasi produksi 2026-08-22 ([[Microservices - Marketing Analytics Service]]). Yang masih 0 dokumen adalah `live_shifts` di bawah, koleksi yang berbeda |

## Pencatatan sesi live oleh host (`/live-shifts`)

Koleksi `live_shifts` — sesi yang **dicatat host sendiri**, bukan hasil sync dari TikTok. Sesi TikTok (`mart_live_sessions`, dilayani `/lives`) dijodohkan ke sini saat pembacaan, **tidak** ditempel saat penulisan: sync bisa datang belakangan, dan menempelkannya saat tulis membuat shift yang dicatat lebih dulu selamanya kosong.

**Seluruh lima route digerbang `common.RequireLiveShiftUser`** — termasuk yang GET, sengaja tidak lebih longgar daripada POST/PATCH. Alasannya baris shift memuat `Host{employee_id, nama}` yang jadi dasar perhitungan porsi insentif per orang, jadi ini bukan bacaan umum sekelas `GET /pagu`. Gerbang ini dibuat khusus karena 13 karyawan Host Live/Live Support hanya memegang `system_roles.insentive=host_live` tanpa modul `marketing` apa pun; gerbang marketing biasa akan menolak justru penggunanya sendiri.

| Method | Path | Catatan |
|---|---|---|
| POST | `/live-shifts` | Mulai sesi. Body `shop_id`·`akun_live`·`host[]`·`shift_id`·`luar_shift`; **tak ada `dibuat_oleh`** — jejak audit dari header gateway, field body bernama sama hanya jadi jalan memalsukannya. `shop_id`/`akun_live` ditolak bila memuat `/ \ ? # %` atau spasi di ujung (**400**). `host[]` wajib ≥ 1; `employee_id` kosong atau **duplikat** → **400**, tidak didedup diam-diam (`BagiRata` membagi per baris, jadi satu orang dua baris menerima porsi dobel — itu salah bayar, bukan data kotor). Sesi berjalan pada akun yang sama → **409 + `shift_berjalan`** supaya bisa diakhiri, bukan ditolak buntu. **Penegak invariannya index unik parsial di Mongo**, bukan pemeriksaan-lalu-tulis; balapan yang lolos juga dipetakan ke 409 |
| PATCH | `/live-shifts/:id/jeda` | Buka/tutup jeda bergantian. Tak ditemukan → **404**; sesi sudah diakhiri → **400**. **PATCH benar-benar sebagian** (hanya field `jeda`). Update bersyarat: menutup jeda mensyaratkan jeda terakhir **masih terbuka di Mongo**, membuka jeda mensyaratkan **panjang `jeda` belum berubah** — yang kalah balapan dibalas **409**, bukan menimpa diam-diam |
| PATCH | `/live-shifts/:id/selesai` | Akhiri sesi; jeda yang menggantung ikut ditutup di waktu selesai supaya durasi efektifnya tidak menggantung. Filter `{selesai: null}` menutup balapan cek-lalu-tulis → yang kalah **409**, bukan sukses palsu |
| GET | `/live-shifts/berjalan` | Seluruh sesi yang belum diakhiri |
| GET | `/live-shifts` | Riwayat + ringkasan penjualan. `dari`/`sampai` **wajib** `YYYY-MM-DD`, **diparsing di zona WIB** (`time.ParseInLocation`, bukan `time.Parse` polos) — memotong di UTC membuang tujuh jam pertama hari itu dan membuat shift dini hari WIB hilang dari tanggalnya sendiri. Batas atas eksklusif; rentang **maks 92 hari** (tanpa itu satu permintaan menarik seluruh koleksi ke memori), diukur dari tanggal kalender **sebelum** pergeseran batas atas. Opsional `shop_id` · `host=<employee_id>` · `milik_saya=true` |

Dua bentuk penyaringan host, **tidak** saling menggantikan: `host=` eksplisit dan hanya boleh dipakai pemanggil yang lolos `IsMarketingLeader` — host biasa yang menyebut orang lain **ditolak 403**, bukan diam-diam dipaksa ke dirinya sendiri, supaya UI yang salah kirim terlihat alih-alih tersamar jadi "kosong tapi sukses" (host biasa yang menyebut dirinya sendiri tetap lolos). `milik_saya=true` menyaring ke `employee_id` dari **header gateway**, bukan query string yang bisa ditulis apa pun oleh klien. Keduanya kosong = tak disaring per host (SPV/leader melihat seluruh tim).

Ringkasannya memakai `RingkasShiftBanyak`, bukan meringkas satu per satu: fungsi itu mendeteksi shift yang **tumpang tindih waktu** pada akun+toko sama dan menandainya `PerluKoreksi` (porsi host nol). Meringkas satu-satu melewatkan deteksi itu, dan dua host yang jadwalnya bertabrakan akan sama-sama dibayar penuh. Rentang pembacaan sesi TikTok **dilebarkan simetris 12 jam** di kedua ujung (bukan `dari`/`sampai` asli) karena 213 dari 4.130 sesi bersih (5,2%, data prod Jul–Agt) melewati tengah malam; tanpa pelebaran, shift tampil "belum ada data penjualan" padahal sesinya nyata ada.

⚠️ **`_id` sengaja tidak menanam input pengguna** (`LS-<ObjectID>`, bukan `LS-<akun_live>-<nano>`). Versi lama menabrak dua hal sekaligus: Fiber mendekode `%2F` **sebelum** mencocokkan rute sehingga `akun_live` berisi `/` memotong `:id` dan membuat sesi mustahil diakhiri lewat API, lalu karena `selesai` tetap null selamanya index unik parsial menolak **setiap** sesi baru pada akun itu — akun mati permanen tanpa jalan pulih.

## Retur & analitik

| Method | Path | Catatan |
|---|---|---|
| GET | `/returns/breakdown` | Agregat per channel+initiator+alasan mentah+kurir; `refund_value` ≠ `order_value` |
| GET | `/returns/detail` | Drill → daftar order (order_id, toko, ICC, items, alasan mentah). `reason=` kosong bermakna "tanpa alasan tercatat"; `initiator=BUYER\|SYSTEM\|SELLER`. ⛔ Membawa **`iklan_sia_sia`** — porsi `ads_cost` pada order retur. **BUKAN kerugian tambahan**: jangan dijumlahkan ke laba (sudah terpotong seluruhnya), jangan digabung dengan beban packing, jangan di-rename `kerugian_iklan`. Pointer: `nil` = tak dihitung, `0` = dihitung dan nol. Aturan lengkap: [[Microservices - Marketing Analytics Service]] §Aturan Pemakaian Angka |
| GET | `/affiliate` | + `collaboration_type=internal\|eksternal\|tanpa_kolaborasi`; `sort_by`: orders/gmv/actual_commission/est_commission/returns. Juga `kepemilikan=internal\|belum_terdaftar\|ada_pemegang\|belum_ditugaskan` — **sumbu berbeda dari `collaboration_type`**, jangan ditukar; nilai tak dikenal → **400**, tidak melebar jadi "semua" |
| GET | `/cohort` | Kohort pembeli |
| GET | `/audience` | `sort_by`: orders/returns/return_rate_pct/return_value/revenue |
| GET | `/matrix/sku-shop` | ✅ Matriks **produk × toko** (`matrix_sku_shop.go`; catatan "stub" di dok ini sudah usang — terimplementasi sejak 2026-08-02). `metrik=` salah satu dari tujuh kolom aditif (`gross_profit` bawaan · `revenue` · `net_settlement` · `hpp` · `ads_cost` · `fee_marketplace` · `retur`); tak dikenal → **400 + `metrik_valid`**. `bulan=YYYY-MM` (bawaan bulan berjalan WIB) **XOR** `dari`/`sampai` — keduanya sekaligus → **400**. `limit` bawaan 100 maks 500, berlaku **setelah** pemeringkatan; pemotongan selalu dilaporkan (`terpotong` + `total_produk`). ⚠️ **Sel absen ≠ nol**: pasangan produk×toko tanpa baris mart tak punya kunci sama sekali (peluang listing), sedangkan nol nyata hadir sebagai `0`. Jangan meratakan keduanya di FE |

## Daftar acuan untuk saringan FE

Dua endpoint yang tak memuat angka, hanya memasok isi dropdown. **Ada supaya FE tidak menghardcode daftarnya**: divisi dibuat & dihapus lewat UI `/integration/teams` kapan saja, dan daftar yang dipahat di FE akan menyimpang tanpa satu pun tanda sementara divisi baru tak pernah muncul.

| Method | Path | Catatan |
|---|---|---|
| GET | `/divisi` | Daftar divisi (`marketing_teams`). ⚠️ Di modul ini **"divisi" berarti grup toko**, bukan departemen HRIS dan bukan brand — lihat [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] |
| GET | `/toko` | Daftar toko dari `mart_profit_attribution`, urut nama lalu `shop_id`. Memakai **pembaca saringan yang sama** dengan halaman lain (`bacaFilterMart`: rentang, `channel`, `divisi`), bukan penguraian kedua yang dapat menyimpang; channel tak dikenal → **400 + `channel_valid`** |

Keduanya membalas **200 dengan amplop `unavailable_channels: SEMUA`** saat sumbernya gagal, **bukan** 5xx dan bukan daftar kosong polos: FE menerima keterangan alih-alih dropdown yang diam-diam kosong. Ini kebalikan dari `GET /pagu`, yang justru 5xx saat gagal — bedanya disengaja, karena dropdown kosong masih bisa dipakai orang sementara pagu kosong mengubah arti angka yang dinilai.

## Price floor

| Method | Path | Catatan |
|---|---|---|
| GET | `/price-floor` | Daftar harga minimal per SKU (effective-dated) |
| POST | `/price-floor` | Tambah baris |
| POST | `/price-floor/upload` | Upload xlsx; laporan per-baris, unggahan yang tak menyimpan apa pun dibalas galat |

## Job, penjadwal & health

| Method | Path | Catatan |
|---|---|---|
| POST | `/jobs/:name/trigger` | `:name` = `sync-ad-creative-link` · `sync-video-performance` · `sync-profit-attribution`. `?hari` bawaan 7 maks 120 (hanya profit-attribution yang memakainya); job berjalan → **409**; `hari` cacat → **400, job tidak jalan** |
| GET | `/jobs/status` | `penjadwal_hidup`, `dinonaktifkan`, alasan, interval, ambang mati 72 jam, `sync_state` tiap job |
| GET | `/health` | `ok` / `degraded` (503) bila index unik gagal dibuat |

## Pengumpul KPI

| Method | Path | Fungsi | Gerbang |
|---|---|---|---|
| GET | `/kpi/kinerja-toko` | Agregat **mentah** kinerja toko satu karyawan satu periode, bahan penilaian KPI marketing. Query wajib `periode=YYYY-MM`·`employee_id`·`key`. Balasan `periode`·`employee_id`·`toko_diminta`·`toko_berdata`·`revenue`·`ads_cost`·`retur`·`gross_profit`·`jumlah_video`. **Rasio sengaja tidak dihitung di sini** — ROI kotor vs bersih-setelah-retur adalah keputusan bisnis yang masih dapat berubah, dan menaruhnya di sisi ini memaksa deploy tiap kali definisinya diubah; yang memilih rumus adalah konfigurasi metrik di [[Microservices - Employee Service]]. Sumbernya `mart_profit_attribution` level `shop`, koleksi yang sama dengan `/profit/shops`, jadi angka KPI dan angka dashboard tak akan pernah berbeda. **Rute ini sendiri yang mencari toko milik karyawan** lewat `icc_account_mappings` di `integration_db` (service ini satu-satunya yang sudah punya koneksi baca-saja ke sana); satu orang boleh memegang beberapa toko **lintas channel**, dan seluruhnya digabung jadi satu angka. Karyawan yang belum dipetakan dijawab **400, bukan 200 bernilai nol** — nol terbaca sebagai orang yang tak menghasilkan apa pun sebulan penuh, tuduhan yang jauh berbeda dari "tokonya belum ditugaskan". `toko_berdata < toko_diminta` berarti ada toko tanpa satu pun baris pada periode itu, dan cakupan itu ikut dilaporkan ke penilai. Batas atas periode **eksklusif** (`$lt`) supaya hari terakhir bulan tak terhitung dua kali. `kpi_kinerja_toko.go` | Kunci layanan sendiri `?key=` (`MARKETING_ANALYTICS_SERVICE_KEY`), **bukan** `BIP-Gateway-ID` — gateway memasang header itu untuk tiap permintaan yang lolos JWT, sehingga rute yang bersandar padanya terbuka bagi semua karyawan yang login ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]). Kunci kosong **menutup** rute |
| GET | `/kpi/kinerja-affiliate` | ✅ Sudah di `origin/main` sejak **2026-08-24** (`kpi_affiliate.go`); catatan lama "branch `feature/workspace-position`" sudah usang. **Status deploy tidak diverifikasi pada sync ini** — merged bukan deployed. Agregat affiliate **PER-INDIVIDU** satu karyawan satu periode, bahan skor KPI staf Affiliate Acquisition (KPI = penilaian individu). Query wajib `periode=YYYY-MM`·`employee_id`·`key`. Balasan `periode`·`employee_id`·`akun_diminta`·`akun_berdata`·`conversion` (distinct `order_id`)·`gmv`·`actual_commission`. **Rute ini sendiri** yang mencari akun affiliate milik karyawan lewat `icc_affiliate_accounts` di `integration_db` (username+alias → `employee_id`). Belum dipetakan → **400**; akun ada tapi nol order → **200 bernilai 0** (nol yang sah). Rasio & target dirakit di [[Microservices - Employee Service]] (sumber `kinerja_affiliate`). Batas atas periode **eksklusif** (`$lt`). `kpi_affiliate.go` | Kunci layanan `?key=` (`GerbangKunciKinerjaToko`), sama dengan `/kpi/kinerja-toko` |
| GET | `/kpi/kinerja-affiliate-tim` | Kinerja affiliate **PER-TIM-CHANNEL**, bukan per-akun: tiap staf ditandai masuk tim `tiktok` atau `shopee` (koleksi `affiliate_channel_team` di `integration_db`), lalu realisasinya = **total konversi channel itu**. Semua staf di channel yang sama karena itu berbagi realisasi yang sama — penilaian tim, sesuai keputusan pemilik metrik. Query wajib `periode=YYYY-MM`·`employee_id`·`key`. Balasan `periode`·`employee_id`·`channel`·`conversion`·`affiliate_aktif`. Sumbernya beda per channel: TikTok dari `affiliate_orders` (distinct `order_id`), Shopee dari `shopee_affiliate_performance` (Σ `orders` harian). **Akun INTERNAL dikecualikan** dari seluruh hitungan (`icc_affiliate_accounts`, alias ikut) — dijalankan ICC, di luar kendali staf Affiliate Acquisition. Belum dipetakan channel → **400**, bukan 200 nol; channel selain tiktok/shopee → **400**. ⚠️ `affiliate_aktif` **berganti definisi 2026-08-25**: kini "affiliator eksternal yang **dapat ≥1 order**", dulu "upload ≥1 video/konten" — definisi lama bergantung data upload konten yang membuat angkanya undercount. `kpi_affiliate_tim.go` | Kunci layanan `?key=` yang sama |
| GET | `/kpi/kinerja-live` | Kinerja siaran **live TikTok PER-DEPARTEMEN**, bahan skor KPI Host Live. Query wajib `periode=YYYY-MM`·`department`·`key`; `employee_id` opsional (diteruskan apa adanya ke balasan, tidak memengaruhi angka). Balasan `conversion`·`conversion_rate`·`add_to_cart_rate`·`avg_viewing_duration`·`product_clicks`·`add_to_cart`·`views`·`viewers`·`sesi`·`akun`·`gmv`·`ada_klik`·`toko_diminta`·`toko_berdata`. **Departemen dikirim pemanggil, bukan diresolusi di sini** — pemetaan karyawan→departemen tinggal di `work_data` milik [[Microservices - Employee Service]], dan menyalinnya ke sini melahirkan sumber kebenaran kedua. Toko departemen dibaca dari `department_shops` (`integration_db`, channel TIKTOK). Dua aturan yang menentukan benar-salahnya angka: **(a)** sesi host dipisahkan dari afiliasi lewat ada/tidaknya `interaction_performance`, disaring **PER-AKUN bukan per-sesi** karena interaksi properti TOKO — satu akun yang live di tiga toko hanya membawa blok interaksi di toko utamanya (`carevolution.hub`: 39 dari 79 sesi), dan menyaring per-sesi memangkas konversi Beauty Hacks 177→155 tanpa satu pun galat; **(b)** satu siaran ke dua etalase (TikTok + Tokopedia) datang sebagai **dua sesi** — mulai selisih ~10 detik, durasi identik ke menit, berulang 21× di produksi — sehingga `orders` dijumlah (penjualan tiap etalase nyata dan berbeda) tetapi cacah **siaran** tidak digandakan. `ada_klik: false` berarti `product_clicks` nol sehingga kedua rasio **tak terdefinisi**, wajib dibedakan dari rasio 0% sungguhan. `kpi_live.go` | Kunci layanan `?key=` yang sama (`GerbangKunciKinerjaToko`) |
| GET | `/kpi/anggota-tim-icc` | Menjawab satu pertanyaan: **karyawan ini memimpin tim ICC apa?** Query wajib `employee_id`·`key`; balasan `{data: {team, leader_id}}` dari `icc_leaders` di `integration_db`. ⛔ **Membalas nama tim dan ID leader saja, TIDAK PERNAH daftar anggota** — anggota diturunkan dari `work_data` milik [[Microservices - Employee Service]], dan membacanya dari sini membuat pemetaan tim→ICC punya dua implementasi yang pasti menyimpang. `employee_id` kosong ditolak **400 sebelum menyentuh database** (membiarkannya lolos akan membalas 404 "bukan leader" untuk permintaan yang sebenarnya cacat). Bukan leader → **404 menyebut sebabnya, bukan 200 bertim kosong** — tim kosong terbaca sebagai "timnya memang tak punya anggota", tuduhan yang berbeda. Baris ber-`team` kosong **dilewati** supaya keluar sebagai "bukan leader" yang terlihat, bukan tim hantu yang mencocokkan nol karyawan; cocok pertama yang menang. `kpi_tim_icc.go` | Kunci layanan `?key=` yang sama |

Keempat rute KPI memakai gerbang **kunci layanan** `GerbangKunciKinerjaToko`, bukan izin pemakai: pemanggilnya employee-service (mesin), yang tidak membawa identitas pengguna sehingga tak punya izin apa pun. Prefix rute **bukan** batas keamanan ([[ADR - 0031 Prefix internal Bukan Batas Keamanan]]).

- ⚠️ **`jumlah_video` ditambahkan** (PR [#1049](https://github.com/bip-itteam-internal/bip-erp/pull/1049), merged 6 Agustus 2026, **belum di-deploy**): cacahan video terbit (`tt_shop_video_performances.published_at`) milik seluruh toko yang dipegang, dipakai metrik `kuantitas video` pada KPI ICC. Dicacah dengan `CountDocuments`, bukan ditarik dokumennya — yang dibutuhkan hanya cacahnya, dan koleksi itu belum punya index selain `_id`.
- ⚠️ **Kegagalan mencacah video tidak menggagalkan jawaban, dan nol-nya tak terbedakan dari nol sungguhan kecuali lewat log.** Disengaja: revenue dan ROI berbobot 0,70 sedangkan video 0,30, jadi membuang metrik yang sudah sah demi satu yang gagal lebih merugikan. Konsekuensinya harus disadari penilai — `jumlah_video: 0` bisa berarti "memang tak menerbitkan video" atau "cacahannya gagal", dan hanya log service yang membedakannya. Berbeda dari metrik lain, di sini nol **tidak** jatuh ke `manual`.

## Cara mengaudit kelengkapan daftar ini

Per 2026-08-26 tak ada route yang tanpa baris. Bagian ini menggantikan daftar "belum terdokumentasi" yang sebelumnya berisi dua route, karena **daftar itu sendiri sudah usang jauh lebih parah daripada yang disadarinya**: yang sungguh hilang ada **dua belas**, bukan dua. Yang menyusul ditambahkan pada sync ini:

`/divisi` · `/toko` · `/pagu` (GET+POST) · `/kurva-alokasi` · `/profit/items` · `/profit/skus` · `/kpi/anggota-tim-icc` · `/kpi/kinerja-affiliate-tim` · `/live-shifts` (POST, GET, GET `/berjalan`, PATCH `/:id/jeda`, PATCH `/:id/selesai`)

**Cacah tangan tidak bisa diandalkan untuk ini, dan sudah terbukti begitu tiga kali** (28 → 38 → 40, tak satu pun cocok dengan kode). Sebabnya rute di service ini didaftarkan tersebar di **dua belas berkas**, sebagian lewat fungsi `registerXxxRoutes` yang dipanggil dari `routes.go` sehingga tak terlihat saat membaca `routes.go` saja. Enumerasi ulang, jangan menambahkan selisih ke angka lama:

```powershell
$s = "bip-erp\services\marketing-analytics"
Get-ChildItem $s -File -Filter *.go | Where-Object { $_.Name -notlike "*_test.go" } |
  Select-String -Pattern '\.(Get|Post|Put|Patch|Delete|All)\s*\(\s*"'
```

Periksa juga `.Group(`/`.Mount(` (per audit ini: tak ada, jadi seluruh path di atas adalah path internal apa adanya) dan baris yang dikomentari. Ingat `/health` didaftarkan di `main.go`, bukan `routes.go`, sehingga sapuan yang hanya membaca `routes.go` akan meleset satu tanpa tanda.

⚠️ **Yang tetap tidak dapat dibuktikan dari kode: apakah route-nya sudah naik ke container.** Merged bukan deployed — lihat skill `deploy-bip-erp` sebelum menyimpulkan sebuah endpoint hidup di PROD.

## Dokumen Terkait

- [[Microservices - Marketing Analytics Service]] · [[API - Index]] · [[CORE - API Master Gateway]]
- [[ADR - 0045 Identitas Tim Tunggal dan Peta Kepemilikan Marketing]] — arti "divisi"/"tim" di modul ini · [[Microservices - Employee Service]] — pemanggil keempat rute `/kpi/*`

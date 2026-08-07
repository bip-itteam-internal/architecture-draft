## Deskripsi

*Service agregasi **laba dan performa marketing** per toko, produk, kampanye, iklan, video, dan live. Membaca `integration_db` **baca-saja** lalu menyimpan hasil pre-agregasi ke koleksi `mart_*` miliknya sendiri, sehingga dashboard marketing tidak menghitung ulang di setiap request. Konteks bisnisnya ada di [[Sales - Marketing Dashboard (Master Roadmap)]].*

- **Stack**: Go + Fiber v2, MongoDB replica set `rs-marketing-analytics` (database `marketing_analytics_db`)
- **Path di repo**: `bip-erp/services/marketing-analytics/`
- **Port**: env `PORT`, alias `SERVICE_PORT`, fallback `6985` (`main.go`)
- **Prefix gateway**: `marketing-analytics` (`api-gateway/main.go`, env `MARKETING_ANALYTICS_MODULE_URL`)
- **Status**: ⚠️ Implemented dengan catatan (audit kode 2026-08-02). Berjalan di production dengan channel **TikTok + Shopee**, penjadwal internal 48 jam, dan 21 route. Catatan: `/matrix/sku-shop` masih stub, `mart_live_sessions` & `mart_buyer_cohort` kosong, lock job hanya in-process.

## Prinsip Arsitektur

Dua hal yang membedakan service ini dari service lain dan wajib dijaga saat mengubahnya.

**1. Database service lain baca-saja, dijaga tiga lapis** (`integration_db.go:18-34`). `integration_db` milik [[Microservices - Integration Service]]; tulisan dari sini merusak data service lain tanpa jejak di repo ini. Lapisnya:

1. Tipe `integrationReader` tidak mengekspos satu pun metode penulisan.
2. Test `TestTidakAdaPenulisanKeIntegrationDB` memindai AST seluruh package dan menolak pemanggilan metode tulis pada penerima yang berasal dari sana. Lapis ini ada karena pelanggarannya tidak akan tampak sebagai test merah biasa: menulis ke `integration_db` berhasil secara teknis, kerusakannya baru terlihat sebagai data korup di database service lain.
3. Koneksinya memakai read preference `secondaryPreferred`, sehingga tulisan yang lolos pun mengarah ke node yang menolaknya.

Penjaga yang sama sudah dibuktikan menutup `insentive_db` (sumber ICC) — arahnya whitelist: yang tak terbukti aman **ditolak**, bukan yang terdaftar dilarang. Ini penegakan konkret dari [[ADR - 0002 Database-per-Service]] untuk kasus lintas-database yang tidak lewat HTTP.

**2. `/health` turun jadi `degraded` (503) bila index unik gagal dibuat** (`main.go`, `index.go`). Index unik adalah fondasi idempotensi sync: tanpa itu job yang diulang menggandakan baris. Service sengaja **tidak** panic saat boot karena pembacaan dashboard masih valid; status degraded menahan penjadwal menganggapnya siap menerima sync sambil tetap bisa ditelusuri lewat endpoint yang sama.

## Endpoint (Sudah Diimplementasikan)

21 route (audit kode 2026-08-02, `routes.go` + `handler_mart.go` + `price_floor_handler.go` + `jobs.go` + `penjadwal_status.go`). Daftar lengkap per-route: [[API - Marketing Analytics Service]]. Seluruhnya `GET` kecuali disebut lain.

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
| `/lives` | Sesi live dari `mart_live_sessions` (koleksi masih kosong) |

### Retur & analitik lain

| Endpoint | Isi |
|---|---|
| `/returns/breakdown` | Agregat retur per channel + initiator (`BUYER`/`SYSTEM`/`SELLER`) + **alasan mentah** (tidak dinormalisasi) + kurir; `refund_value` dan `order_value` terpisah (order batal-sebelum-bayar tak punya refund) |
| `/returns/detail` | Drill baris agregat → daftar order: order_id, toko, **nama ICC**, item+SKU+jumlah, nilai, alasan mentah, tanggal. `reason=` kosong **bermakna** ("tanpa alasan tercatat"); `total: -1` = cacah gagal (bukan 0) |
| `/affiliate` · `/cohort` · `/audience` | Analitik affiliate (kolom `collaboration_type` internal/eksternal), kohort, audiens; `sort_by`/`sort_dir` dua arah + pemecah-seri deterministik |
| `/matrix/sku-shop` | 🔴 **Masih stub** — envelope kosong yang sah, pipeline belum ada |

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
| `mart_live_sessions` · `mart_buyer_cohort` | — | **Masih kosong** di production |
| `mart_price_floor` | `sku + effective_from` | Harga minimal per SKU |

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

## Kejujuran Data (bagian yang tidak boleh dihapus)

Service ini menyimpan **alasan ketidaklengkapan bersama datanya**, bukan membiarkan angka kosong dibaca sebagai nol.

- **`attribution_kolom` — penanda aktual vs perkiraan melekat PER KOLOM**, bukan per baris. Peta `nama kolom → alasan terbaca manusia`; kolom yang tidak ada di peta = **aktual**; kunci = persis tag json kolom. Penanda tingkat-baris sebelumnya memvonis seluruh baris: 2.384 baris campaign bertanda `estimated` dibaca pengguna sebagai "biaya iklan tidak valid" — padahal `ads_cost`-nya aktual, Rp1.289.007.856 cocok persis belanja GMV Max; yang perkiraan **labanya** (retur tak teratribusi ke level iklan, dasar revenue kotor). `attribution`/`attribution_note` kini **turunan** — utang teknis, dihapus setelah FE membaca `attribution_kolom`.
- **`kolom_tidak_berlaku`** (lihat *Kontrak amplop*) membedakan "kolom ini tak akan pernah berisi di level ini → hilangkan" dari "sel ini kosong → tak tersedia". Kolom struktural yang membawa angka nyata tetap dikirim; hanya nilai nol yang dinihilkan — `retur = 0` di level shop adalah kabar baik nyata dan tetap `0`.
- **`master_sku` + `belum_termapping`** pada level product: baris ber-master kosong tetap tampil sendiri dengan SKU aslinya — tidak dibuang, tidak dilebur jadi "lain-lain". Sisa terbesar kini SKU **bundel ber-master-kosong** yang isi paketnya perlu konfirmasi bisnis (menetapkan komponen paket bukan urusan tebakan kode).
- **`icc` — penanggung jawab toko, gabungan TIGA sumber** (`indeksICCGabungan`): `integration_db.icc_account_mappings` (orang, TikTok), `integration_db.team_shops` + `marketing_teams` (**tim**, satu-satunya sumber Shopee — nama diberi awalan `Tim`, tidak menyamar jadi orang), `insentive_db.employee_performance_mappings` (orang + role; database & container terpisah, env `INSENTIVE_MONGO_URI`). Sumber **menambah, tidak menimpa** (dedup lintas sumber per employee_id/team_id); satu sumber gagal → sumber lain tetap dipakai. Cakupan terukur: insentive saja 2 toko (3,5%) → gabungan **15 toko (51,2%)**. Membawa **daftar** pemegang (satu toko bisa dipegang lebih dari satu orang — terverifikasi production), bukan satu nama. Status **empat**: `ditetapkan` / `belum_ditetapkan` (tim perlu melengkapi mapping) / `tak_tersedia` (melengkapi mapping tak akan mengisinya — level `ad`, karena `shop_id` 0 dari 10.650) / `sebagian_ditetapkan` (hanya baris product lintas-toko yang tokonya bercampur).
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

- **`GET /matrix/sku-shop` masih stub** (envelope kosong yang sah; komentar "SISA STUB").
- **`mart_live_sessions` dan `mart_buyer_cohort` kosong** di production; `/lives` dan `/cohort` membalas kosong.
- **Lock job & penjadwal hanya in-process** — belum aman di-scale horizontal.
- **Interval penjadwal belum bisa diubah lewat env** (hanya jam, jendela, dan flag aktif).
- **Job laba Lazada sengaja mati** di `channelProfitBawaan`.
- **Cakupan ICC 51,2%** — sisanya butuh tim melengkapi `icc_account_mappings`, bukan perubahan kode.
- **Kolom Pemegang di `/affiliate`** (2026-08-07) — kepemilikan akun kreator dari `integration_db.icc_affiliate_accounts`, **sumbu berbeda** dari `collaboration_type`: yang satu sifat order (target vs open collab, dari TikTok), yang lain siapa karyawan di balik username (dari daftar akun kita). Alias ikut dicocokkan agar order lampau tak terbaca "belum terdaftar" saat handle berganti. Tiga keadaan dibedakan: ada nama · `belum ditugaskan` (akun perusahaan tanpa pemegang) · `belum terdaftar` (di luar daftar). Bersifat pelengkap — bila koleksinya gagal dibaca, angka lain tetap tampil dan kolomnya kosong. Lihat [[Sales - ICC Affiliate Mapping]].
- `InternalURL` divalidasi saat boot tapi nilainya belum dipakai.
- Index `affiliate_orders {content_id, order_create_time}` untuk `/videos/orders` dibuat manual di production 2026-08-02 (tulis `integration_db` = di luar wewenang service ini; tercatat di komentar `cocokOrderVideo`).

## Dependensi & Integrasi

- **Sumber data (baca-saja)**: `integration_db` milik [[Microservices - Integration Service]] — `transaction_orders`, `product_sku_mappings`, `product_costs`, `tt_business_*`, `tt_shop_video_performances`, `shopee_gms_*`, `affiliate_orders`, `icc_account_mappings`, `icc_affiliate_accounts`, `team_shops`, `marketing_teams`; plus `insentive_db` milik [[Microservices - Insentive Service]] (`employee_performance_mappings`, env `INSENTIVE_MONGO_URI`). Lihat juga [[Sales - Marketplace Integration]].
- **API pihak ketiga**: TikTok Ads API `/open_api/v1.3/ad/get/` (`client_tiktok_ads_http.go`) hanya untuk tautan ad→video; metrik iklan dibaca dari Mongo, bukan API langsung. Kredensial gagal didekripsi dilewati **tapi dihitung dan dilaporkan**.
- **Gerbang**: [[CORE - API Master Gateway]] · **Konsumen**: dashboard marketing di [[APP - Web ERP]]
- **Konsep & rancangan**: [[Sales - Marketing Dashboard (Master Roadmap)]] · [[Sales - Marketing Dashboard (Index)]] · [[Sales - Profit Engine (Design)]] · [[Sales - HPP Master (Plan)]] · [[ADR - 0008 Profit Engine Join via item_group_id]]
- **Koleksi**: [[DB - Overview and Notes]] · **Endpoint per-route**: [[API - Marketing Analytics Service]]

## Dokumen Terkait

- [[Microservices - Integration Service]] (pemilik `integration_db`) · [[Microservices - Insentive Service]] (sumber ICC + konsumen metrik iklan untuk insentif)
- [[IT - Background Jobs & Schedulers]] (penjadwal internal service ini tercatat di sana)
- [[ADR - 0002 Database-per-Service]] · [[ADR - 0011 Integration Read Cache + Singleflight (Fase 1 Perf)]]
- [[Sales - GMV Creative]] · [[Sales - ICC Affiliate Mapping]] · [[Sales - Marketing Dashboard (Analisis Rekap)]]
- [[HRIS - Otomasi Skor KPI]] (memakai `mart_profit_attribution` dan `mart_video_performance` sebagai calon sumber skor KPI otomatis)

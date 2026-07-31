## Deskripsi

*Service agregasi **laba dan performa marketing** per toko, produk, kampanye, iklan, video, dan live. Membaca `integration_db` **baca-saja** lalu menyimpan hasil pre-agregasi ke koleksi `mart_*` miliknya sendiri, sehingga dashboard marketing tidak menghitung ulang di setiap request. Konteks bisnisnya ada di [[Sales - Marketing Dashboard (Master Roadmap)]].*

- **Stack**: Go + Fiber v2, MongoDB replica set `rs-marketing-analytics` (database `marketing_analytics_db`)
- **Path di repo**: `bip-erp/services/marketing-analytics/`
- **Port**: env `PORT`, alias `SERVICE_PORT`, fallback `6985` (`main.go`)
- **Prefix gateway**: `marketing-analytics` (`api-gateway/main.go:47`, env `MARKETING_ANALYTICS_MODULE_URL`)
- **Status**: ⚠️ Implemented dengan catatan. Berjalan di production dan datanya terisi (verifikasi 2026-07-31), tetapi `/matrix/sku-shop` masih stub, 3 dari 6 koleksi mart masih kosong, dan **tidak ada scheduler di dalam service** (job hanya dipicu lewat HTTP).

## Prinsip Arsitektur

Dua hal yang membedakan service ini dari service lain dan wajib dijaga saat mengubahnya.

**1. `integration_db` baca-saja, dijaga tiga lapis** (`integration_db.go:18-34`). `integration_db` milik [[Microservices - Integration Service]]; tulisan dari sini merusak data service lain tanpa jejak di repo ini. Lapisnya:

1. Tipe `integrationReader` tidak mengekspos satu pun metode penulisan.
2. Test `TestTidakAdaPenulisanKeIntegrationDB` memindai AST seluruh package dan menolak pemanggilan metode tulis pada penerima yang berasal dari sana. Lapis ini ada karena pelanggarannya tidak akan tampak sebagai test merah biasa: menulis ke `integration_db` berhasil secara teknis, kerusakannya baru terlihat sebagai data korup di database service lain.
3. Koneksinya memakai read preference `secondaryPreferred`, sehingga tulisan yang lolos pun mengarah ke node yang menolaknya.

Ini penegakan konkret dari [[ADR - 0002 Database-per-Service]] untuk kasus lintas-database yang tidak lewat HTTP.

**2. `/health` turun jadi `degraded` (503) bila index unik gagal dibuat** (`main.go:41-52`, `index.go:115-142`). Index unik adalah fondasi idempotensi sync: tanpa itu job yang diulang menggandakan baris. Service sengaja **tidak** panic saat boot karena pembacaan dashboard masih valid; status degraded menahan scheduler menganggapnya siap menerima sync sambil tetap bisa ditelusuri lewat endpoint yang sama.

## Endpoint (Sudah Diimplementasikan)

Seluruhnya `GET` kecuali disebut lain. Sumber: `routes.go`, `handler_mart.go`, `price_floor_handler.go`, `jobs.go`.

### Laba & agregasi (baca koleksi mart)

| Endpoint | Isi |
|---|---|
| `/summary` | Ringkasan lintas sumber |
| `/profit/shops` · `/profit/products` · `/profit/campaigns` · `/profit/ads` | Laba per level entitas per hari dari `mart_profit_attribution` |
| `/videos` | Performa video. Baris berupa `VideoRow`, bukan dokumen mart apa adanya, karena halaman video punya tiga tab (VSA / GMV Max / organik) yang hanya dapat dipisahkan lewat `spend_vsa`, `spend_gmv_max`, dan `sumber` |
| `/lives` | Sesi live dari `mart_live_sessions` |

### Analitik lain

| Endpoint | Isi |
|---|---|
| `/affiliate` | Performa affiliate (baca Mongo) |
| `/returns/breakdown` | Rincian retur |
| `/cohort` | Kohort pembeli |
| `/audience` | Demografi audiens |

### Price floor

| Endpoint | Isi |
|---|---|
| `GET /price-floor` · `POST /price-floor` · `POST /price-floor/upload` | Harga minimal per SKU, **effective-dated**: baris baru per perubahan, baris lama tidak ditimpa (pola sama dengan `product_costs`) |

### Job & health

| Endpoint | Isi |
|---|---|
| `POST /jobs/:name/trigger?hari=N` | Picu job manual. `hari` bawaan **7**, maksimum **120** |
| `GET /health` | `ok`, atau `degraded` (503) bila ada index unik yang gagal dibuat |

## Job Sync

Tiga job, seluruhnya channel TikTok. Nama job adalah nilai `:name` pada endpoint trigger.

| Job | Konstanta | Fungsi |
|---|---|---|
| `sync-ad-creative-link` | `sync_ad_creative_link.go:18` | Jembatan metrik iklan TikTok ke video organik lewat `tiktok_item_id` dari `/open_api/v1.3/ad/get/` |
| `sync-video-performance` | `sync_agregasi.go:17` | Agregasi performa video |
| `sync-profit-attribution` | `sync_agregasi.go:18` | Agregasi laba per level entitas per hari |

Perilaku trigger (`jobs.go`):

- **Kunci per-job hanya berlaku dalam satu proses.** Menaikkan replika service ini menghilangkan jaminannya; perlu distributed lock. Job yang sedang berjalan membalas **409**, bukan 200, supaya pemanggil tahu jobnya tidak jalan.
- Parameter `hari` cacat membalas **400 dan job tidak dijalankan**, karena menjalankannya dengan nilai bawaan akan membalas sukses atas backfill yang tidak pernah terjadi. Job yang tidak berdimensi hari **menolak** parameter `hari` alih-alih mengabaikannya diam-diam.
- Konteks dilepas dari request (`context.WithoutCancel`, timeout **30 menit**) karena sync penuh 70 advertiser lebih lama dari batas sabar klien HTTP mana pun.
- Ringkasan dikembalikan baik saat sukses maupun gagal. `unit_total` dan `unit_gagal` adalah denominator per hari; tanpanya "tersimpan 0" tidak terbedakan dari "seluruh hari gagal".

> **Tidak ada scheduler di dalam service ini.** Tidak ada cron, ticker, maupun goroutine penjadwal di `services/marketing-analytics/`. Penjadwalan harus datang dari luar lewat `POST /jobs/:name/trigger`. Ini membedakannya dari [[Microservices - Integration Service]] yang punya cron manager sendiri; lihat [[IT - Background Jobs & Schedulers]].

## Koleksi (`marketing_analytics_db`)

Seluruh index unik dibuat saat boot (`index.go`). Kolom "prod" adalah `estimatedDocumentCount` per **2026-07-31**.

| Koleksi | Kunci unik | Prod | Isi |
|---|---|---:|---|
| `mart_profit_attribution` | `channel + level + entity_id + date` | 405.543 | Laba per hari. `level` = shop / product / campaign / ad / video / live. **`entity_id` level product = master SKU** (bukan SKU jual) sejak penggabungan per produk; SKU yang belum termapping tetap memakai SKU aslinya |
| `mart_video_performance` | `channel + video_id` | 87.813 | **Snapshot kumulatif, sengaja tanpa dimensi hari** |
| `mart_ad_creative_link` | `advertiser_id + ad_id + tiktok_item_id` | 7.814 | Jembatan ad ke post organik |
| `sync_state` | `channel + job` | 3 | Cursor, `last_run_at`, `last_ok_at`, `last_error` per job |
| `mart_live_sessions` | `channel + session_id` | **0** | Sesi live (belum terisi) |
| `mart_buyer_cohort` | `channel + buyer_key` | **0** | Kohort pembeli (belum terisi) |
| `mart_price_floor` | `sku + effective_from` | **0** | Harga minimal per SKU (belum terisi) |

### Kenapa `mart_video_performance` tidak punya dimensi hari

Sumbernya, `tt_shop_video_performances`, terverifikasi berupa **snapshot kumulatif**: satu dokumen per video, angka seumur hidup, ditimpa tiap sync, tanpa `stat_time_day`. Versi sebelumnya menyimpan satu baris per video **per hari** dalam jendela 7 hari dengan angka identik di ketujuh tanggal. Akibatnya terukur di production: 613.867 baris untuk 88.594 video, dan halaman rentang-tanggal yang menjumlahkan lintas tanggal mendapat **7,0x angka sebenarnya tanpa error apa pun**.

Perbaikannya struktural: dimensi harinya dibuang, bukan dibatasi. Dengan satu baris per video, penjumlahan rentang tanggal apa pun secara aritmetika tidak bisa melebihi satu snapshot. `synced_at` menggantikan `date`, karena "kapan snapshot terakhir diambil" adalah fakta yang ada sedangkan "perolehan pada tanggal X" bukan.

> **Catatan deploy**: `CreateOne` tidak mengganti index yang sudah ada. Perubahan kunci unik pada `mart_video_performance` dan `mart_profit_attribution` menuntut `dropIndex` index lama secara manual. Verifikasi production 2026-07-31 menunjukkan **index baru sudah aktif** pada ketiga koleksi berisi, jadi migrasinya sudah dijalankan.

> **Catatan deploy — penggabungan per master SKU**: susunan kunci upsert **tidak berubah**, tetapi **arti `entity_id` level product berubah** (SKU jual → master SKU). Dokumen product lama ber-`entity_id` SKU jual **tidak** diperbarui oleh sync baru karena kuncinya berbeda: ia berhenti disentuh sementara baris master-nya lahir di sebelahnya, sehingga `/profit/products` akan menampilkan **angka dobel** bila tidak dibersihkan. Tindakan yang disarankan: **hapus dokumen `mart_profit_attribution` yang `level: "product"` sebelum deploy**, lalu jalankan ulang sync jendela penuh. Nilainya dihitung ulang dari sumber, jadi drop + re-sync lebih murah dan lebih aman daripada memetakan ulang `entity_id` per dokumen. Level shop/campaign/ad/video **tidak terdampak**.

## Kejujuran Data (bagian yang tidak boleh dihapus)

Service ini menyimpan **alasan ketidaklengkapan bersama datanya**, bukan membiarkan angka kosong dibaca sebagai nol.

- **Envelope kanal**: `/videos` dan `/lives` selalu menandai Lazada `unavailable` beserta alasannya (`ReasonLazadaNoVideo`, `ReasonLazadaNoLive`), supaya tabel kosong tidak terbaca sebagai "data hilang". Lazada Open Platform memang tidak menyediakan analytics konten.
- **`attribution_kolom` — penanda aktual vs perkiraan melekat PER KOLOM**, bukan per baris. Bentuknya peta `nama kolom -> alasan terbaca manusia`; kolom yang **tidak ada di peta berarti aktual**, dan peta kosong berarti seluruh baris aktual. Nama kuncinya persis tag json kolom yang ditandai (`ads_cost`, `gross_profit`, `retur`, …).

  Penanda tingkat-baris sebelumnya memvonis **seluruh** baris padahal hanya sebagian kolomnya perkiraan. Terukur production Juli 2026: seluruh 2.384 baris level campaign bertanda `estimated`, dan pengguna membacanya sebagai "biaya iklan tidak valid" — padahal biaya iklannya **aktual**, Rp1.289.007.856 cocok persis dengan total belanja GMV Max. Yang perkiraan adalah **labanya**. Karena itu `ads_cost` kini tampil polos kecuali benar-benar hasil prorata (Shopee GMS / Lazada) **dan** nilainya bukan nol.

  Alasan yang terpasang: retur **tidak dapat diatribusikan ke level iklan** (laporan iklan tidak membawanya, order tidak menyimpan campaign/ad/video id), sehingga `retur = 0` di level itu berarti **tidak diketahui, bukan nol**; dasar labanya `gross_revenue` laporan iklan, bukan settlement bersih; potongan marketplace belum dikurangkan; HPP yang belum diketahui membuat kolom `hpp` dan `gross_profit` perkiraan sementara `revenue` dan `ads_cost` tetap aktual.

- **`attribution` + `attribution_note` kini TURUNAN** dari `attribution_kolom` (`estimated` bila ada kolom bertanda, catatannya gabungan seluruh alasan), **dipertahankan sementara supaya FE lama tidak pecah**. **Utang teknis** — dihapus setelah FE membaca `attribution_kolom`.

- **`master_sku` + `belum_termapping`** pada level product. `entity_id` level product adalah **master SKU**, bukan SKU jual: 39 master_sku unik dari 1.748 SKU, sehingga produk bernama sama tidak lagi terpecah. Baris yang `master_sku`-nya kosong **tetap tampil sendiri-sendiri** dengan SKU aslinya dan bertanda `belum_termapping` — tidak dibuang dan **tidak dilebur jadi satu baris "lain-lain"** (67 SKU nyata senilai Rp3,7 M; satu baris sebesar itu tak dapat ditindaklanjuti siapa pun). Begitu mapping dibersihkan, baris-baris itu menyatu sendiri tanpa ubah kode.

- **`icc` — penanggung jawab toko**, dibaca dari `insentive_db.employee_performance_mappings` (database **dan** container Mongo terpisah; baca-saja). Membawa **daftar** pemegang + status + keterangan, bukan satu nama: satu toko dapat dipegang lebih dari satu orang (terverifikasi production: toko `7495537364189547259` dipegang dua orang sekaligus), dan bentuk satu-nilai akan memilih salah satu mengikuti urutan iterasi Mongo — kolomnya terisi, terbaca benar, dan salah. Statusnya **tiga**, bukan dua: `ditetapkan` / `belum_ditetapkan` (tim insentif perlu melengkapi mapping) / `tak_tersedia` (melengkapi mapping **tidak** akan mengisinya). Level `ad` selalu `tak_tersedia` karena **levelnya**, bukan karena isi `shop_id` per baris — cakupan `shop_id` production: shop/product/campaign/video 100%, ad **0 dari 10.650** (laporan VSA berdimensi `ad_id` saja).
  > **TBD**: pemuatan indeks ICC (`muatICCAman` / `bacaIndeksICC` di `sumber_agregasi.go`) **belum terpasang**. Sampai itu dilakukan, kolomnya berbunyi `belum_ditetapkan` untuk semua toko — belum terisi, bukan salah.
- **`SpendVSA` dan `SpendGMVMax` sengaja tetap terpisah** sampai ke penyimpanan: yang satu biaya aktual per `ad_id`, yang lain hasil prorata tingkat kampanye. Menggabungkannya menghapus pembedaan yang menjadi alasan seluruh agregasi video dibangun.
- **`AdaSumberLain`** menandai video yang spend-nya juga tercatat di tab lain, supaya pembaca satu tab tidak menghitung ROAS dari spend yang belum lengkap.
- **`CompletionRate` bernilai nil untuk TikTok**, artinya tidak tersedia di platform, bukan nol.
- **`VideoURL` kosong** bila `creator_username` tidak ada (3% dari 84.134 baris). Kosong berarti tidak ada tautan, bukan tautan rusak; menebaknya menghasilkan URL yang pasti 404.
- **`EntityName` tidak pernah kosong**: bila lookup meleset, isinya `entity_id` apa adanya, karena id mentah masih dapat ditelusuri ke seller center sementara `""` atau `"Unknown"` menghapus satu-satunya pegangan. Untuk level product yang `entity_id`-nya kini master SKU, namanya dicari lewat `product_name` milik master itu, dan jatuh ke master SKU bila kosong.
- **`sync_state.last_error` dipakai juga untuk CATATAN**, bukan hanya error. Isi production 2026-07-31 mencontohkannya: `sync-profit-attribution` mencatat sejumlah SKU tanpa HPP berlaku (laba baris terkait lebih besar dari sebenarnya) dan sejumlah rupiah belanja iklan yang tidak dapat dipetakan ke SKU; `sync-video-performance` mencatat 3.679 video ber-spend tanpa baris organik.

## Persona / Pengguna

| Persona | Peran & Divisi | Akses/RBAC | Device |
|---|---|---|---|
| Supervisor & Leader Marketing | Pembaca dashboard laba per toko, kampanye, video | Lewat gateway dan menu dashboard di [[APP - Web ERP]] | Web |
| Advertiser / ICC / Host Live | Melihat performa kreatif dan iklan miliknya | idem | Web |
| Tim IT / operator | Memicu job sync dan membaca `sync_state` saat data terlihat janggal | `POST /jobs/:name/trigger` | Web, terminal |

- **Tujuan**: melihat laba yang sudah dikurangi HPP dan biaya iklan, bukan sekadar omzet kotor.
- **Pain point**: angka marketplace dan angka iklan datang dari sumber berbeda dengan definisi berbeda; tanpa atribusi eksplisit, laba mudah dibaca terlalu optimis.
- **Aksi utama**: buka dashboard per rentang tanggal, telusuri dari toko ke produk ke kampanye ke iklan ke video.

## Belum Diimplementasikan / Catatan

- **`GET /matrix/sku-shop` masih stub**: mengembalikan envelope kosong yang sah, bukan data karangan. Pipeline-nya belum ada (`routes.go`, komentar "SISA STUB").
- **Tiga koleksi mart masih kosong di production**: `mart_live_sessions`, `mart_buyer_cohort`, `mart_price_floor`. Endpoint `/lives`, `/cohort`, dan `/price-floor` karenanya membalas kosong.
- **Tidak ada scheduler internal.** Pemicu job saat ini di luar repo bip-erp; belum terdokumentasi siapa yang memanggilnya secara terjadwal = **TBD**.
- **Lock job hanya in-process.** Service ini belum aman di-scale horizontal.
- **Hanya channel TikTok yang punya job.** Konstanta `ChannelShopee` dan `ChannelLazada` sudah ada dan dipakai envelope, tetapi belum ada job sync untuk keduanya.
- `InternalURL` divalidasi saat boot tapi **nilainya belum dipakai**: service ini membaca Mongo langsung dan belum memanggil service lain lewat gateway (`main.go`).
- Dok ini dibuat 2026-07-31 sebagai penutup gap yang ditemukan saat menyusun [[HRIS - Otomasi Skor KPI]]; service-nya sendiri sudah berjalan lebih dulu di production tanpa dokumentasi.

## Dependensi & Integrasi

- **Sumber data (baca-saja)**: `integration_db` milik [[Microservices - Integration Service]], koleksi `tt_business_credentials`, `tt_business_advertisers`, `tt_shop_video_performances`, laporan GMV-Max. Lihat juga [[Sales - Marketplace Integration]].
- **API pihak ketiga**: TikTok Ads API dipanggil langsung (`client_tiktok_ads_http.go`) memakai access token yang didekripsi dari `tt_business_credentials`. Kredensial yang gagal didekripsi dilewati **tapi dihitung dan dilaporkan**, tidak dibuang diam-diam.
- **Gerbang**: [[CORE - API Master Gateway]]
- **Konsumen**: dashboard marketing di [[APP - Web ERP]]
- **Konsep & rancangan**: [[Sales - Marketing Dashboard (Master Roadmap)]] · [[Sales - Marketing Dashboard (Index)]] · [[Sales - Profit Engine (Design)]] · [[Sales - HPP Master (Plan)]] · [[ADR - 0008 Profit Engine Join via item_group_id]]
- **Koleksi**: [[DB - Overview and Notes]]

## Dokumen Terkait

- [[Microservices - Integration Service]] (pemilik `integration_db`) · [[Microservices - Insentive Service]] (konsumen metrik iklan untuk insentif)
- [[IT - Background Jobs & Schedulers]] (service ini **tidak** punya job terjadwal internal)
- [[ADR - 0002 Database-per-Service]] · [[ADR - 0011 Integration Read Cache + Singleflight (Fase 1 Perf)]]
- [[Sales - GMV Creative]] · [[Sales - ICC Affiliate Mapping]] · [[Sales - Marketing Dashboard (Analisis Rekap)]]
- [[HRIS - Otomasi Skor KPI]] (memakai `mart_profit_attribution` dan `mart_video_performance` sebagai calon sumber skor KPI otomatis)

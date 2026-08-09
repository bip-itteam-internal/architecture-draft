## Deskripsi

*Daftar endpoint **Marketing Analytics Service** — grounded ke kode (`routes.go`, `handler_mart.go`, `price_floor_handler.go`, `jobs.go`, `penjadwal_status.go`, `beranda.go`, `ambang_handler.go`; audit 2026-08-07, **28 route** di berkas produksi). Arsitektur & semantik data: [[Microservices - Marketing Analytics Service]].*

- **Status**: ⚠️ Grounded ke kode (2026-08-09), seluruh route **live di PROD**; **3 route belum terdokumentasi** — lihat catatan di kaki.
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

**Vonis punya LIMA nilai**, dievaluasi berurutan: `tanpa_data` (tak ada satu baris pun) → `belum_matang` (laba `< 0` tapi minusnya hilang bila baris yang settlement-nya belum cair dikeluarkan) → `rugi` (laba `< 0`) → `waspada` (laba `>= 0` tapi ROAS `< roas_min`) → `sehat`.

`tanpa_data` ada karena tanpanya periode kosong divonis `sehat` dan melukis lencana hijau di atas nol. `belum_matang` ada karena verifikasi produksi menemukan lencana RUGI di atas angka yang catatannya sendiri sebut "belum matang, bukan rugi". **Untuk FE: `belum_matang` bukan kabar buruk dan tak boleh berlencana merah** — artinya angkanya akan naik sendiri setelah settlement cair.

**Nilai `null` berarti tak terhitung, bukan nol**: `roas` saat belanja nol, `iklan_persen_revenue` saat revenue nol, `delta_persen` saat pembanding nol.

**`cpa_maks` tersimpan dan dikirim tetapi TIDAK DIBACA apa pun** — `mart_profit_attribution` sengaja tak menyimpan cacah order, jadi CPA tak dapat dihitung. Separuh ambang keputusan menunggu keputusan produk.

`unavailable_channels` pada endpoint ini dapat memuat penanda **pemancungan** ber-channel `SEMUA`: baris sumber menyentuh batas keamanan pembacaan, jadi angkanya bisa kurang. Itu bukan kegagalan — barisnya ada — jadi layar tetap menampilkannya sambil menyebut jumlahnya mungkin belum utuh.

## Laba (`mart_profit_attribution`)

| Method | Path | Catatan |
|---|---|---|
| GET | `/summary` | Ringkasan lintas sumber |
| GET | `/profit/shops` | `granularitas=bulanan\|harian` (bawaan bulanan) · `bulan=YYYY-MM` · `sort_by`/`sort_dir` |
| GET | `/profit/products` | + `lingkup=lintas_toko\|per_toko` (bawaan lintas_toko; baris gabungan membawa `jumlah_toko`, `shop_id` kosong) |
| GET | `/profit/campaigns` | idem shops |
| GET | `/profit/ads` | + `campaign_id` (filter drill); baris membawa `metrik_iklan` (15 metrik API, `spend` per mata uang) |
| GET | `/profit/orders` | Drill product → order. `entity_id` **wajib**; `bulan` XOR `dari`/`sampai`; `termasuk_batal=true\|false` (bawaan false — CANCELLED dikecualikan, konsisten agregasi); respons + `sku_tercakup` |

## Video & live

| Method | Path | Catatan |
|---|---|---|
| GET | `/videos` | `VideoRow` (tab VSA/GMV Max/organik); + `gross_profit` (nil = tak pernah dihitung), `product_title`/`product_image_url`/`product_item_group_id`, `ad_id`, `channel`, `synced_at`. **Menolak `granularitas` (400)** — snapshot kumulatif |
| GET | `/videos/orders` | Drill video → order **affiliate saja** (`affiliate_orders`, `content_type="VIDEO"`). `video_id` **wajib**; field `cakupan` selalu terisi |
| GET | `/lives` | `mart_live_sessions` (koleksi masih kosong) |

## Retur & analitik

| Method | Path | Catatan |
|---|---|---|
| GET | `/returns/breakdown` | Agregat per channel+initiator+alasan mentah+kurir; `refund_value` ≠ `order_value` |
| GET | `/returns/detail` | Drill → daftar order (order_id, toko, ICC, items, alasan mentah). `reason=` kosong bermakna "tanpa alasan tercatat"; `initiator=BUYER\|SYSTEM\|SELLER` |
| GET | `/affiliate` | + `collaboration_type=internal\|eksternal\|tanpa_kolaborasi`; `sort_by`: orders/gmv/actual_commission/est_commission/returns |
| GET | `/cohort` | Kohort pembeli |
| GET | `/audience` | `sort_by`: orders/returns/return_rate_pct/return_value/revenue |
| GET | `/matrix/sku-shop` | 🔴 **Stub** — envelope kosong |

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

## Belum terdokumentasi (ada di kode, bukan di dok ini)

Terhitung 2026-08-07, tiga route produksi terdaftar tetapi belum punya baris di tabel mana pun di atas. Ketiganya mendarat di `main` **sesudah** audit 2026-08-02 dan **bukan** bagian dari pekerjaan halaman depan, jadi didaftar apa adanya di sini alih-alih dikarang semantiknya:

| Method | Path | Berkas |
|---|---|---|
| GET | `/toko` | `toko.go` |
| GET | `/kpi/kinerja-toko` | `kpi_kinerja_toko.go` |
| GET | `/profit/items` | `handler_mart.go` |

Menyebutkan keberadaannya lebih berguna daripada menghilangkannya: dok yang diam soal route yang ada membuat pembacanya mengira daftar ini lengkap. `/sync-docs` berikutnya yang menyentuh service ini semestinya melengkapinya.

## Dokumen Terkait

- [[Microservices - Marketing Analytics Service]] · [[API - Index]] · [[CORE - API Master Gateway]]

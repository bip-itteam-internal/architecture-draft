Papan kerja untuk [[ADR - 0160 Cakupan Baca Ulasan Mencakup Toko Pegangan CS, Menu Dibuka lewat Paket Izin yang Ada]]. Cara kerja cakupan ulasan ada di [[Microservices - Integration Service]] § cakupan toko.
Berubah tiap item selesai; keputusannya ada di ADR, bukan di sini.

✅ ADR Diterima 2026-10-08 oleh irfanarfianto. Brief keempat task ada di `.task-plans/briefs/2026-10-08-{2824,2825,2826,2207}-*.md` (lokal, bukan di vault).

- **Ukuran**: **Kecil** untuk keputusan ADR-nya (hanya `bip-erp`), ditambah satu issue `erp-frontend` yang berdiri sendiri (T5) untuk menutup jalan buntu sesudah membaca. Untuk cakupan, `erp-frontend` tidak perlu berubah: tab Ulasan sudah merender daftar lintas toko, nama toko, tanggal, bintang, dan filter "Belum dibalas" untuk toko mana pun yang dikirim server (`src/features/integration/reviews/components/review-card.tsx:76-94`, `daftar-ulasan.tsx:133-137`), dan tombol komplain memang sengaja tetap hanya untuk pemegang akun toko (`lib/boleh-ajukan.ts:24-39`). `mybharata-app` tidak punya layar ulasan.
- **Pemutus**: irfanarfianto
- **Asal**: permintaan Shop Quality, "membuka toko satu per satu untuk melihat ada ulasan atau tidak". Fiturnya sudah ada; yang hilang aksesnya.

Diukur prod 2026-10-08 sebagai titik awal (angka bergerak, ukur ulang sebelum dipakai memutuskan):

- 23.649 ulasan Shopee dari 15 toko; TikTok nol ulasan per pembeli (batas API), Lazada belum disinkronkan.
- `cs_shop_mappings` 21 baris aktif, seluruhnya satu orang berjabatan Shop Quality: 17 TikTok, 4 Shopee. Orang itu memegang nol baris `icc_account_mappings`.
- Empat toko Shopee itu: 3.627 ulasan 30 hari terakhir, 3.599 belum dibalas, 67 berbintang 1 sampai 3.
- Job `sync-reviews` sehat: 40 run terakhir sukses, sekitar 13 menit per run.

## Status PR (diukur 2026-10-08; bergerak, ukur ulang lewat `gh pr view` sebelum dipakai)

| Task | Issue | PR | Keadaan saat ditulis |
|---|---|---|---|
| T1 cakupan CS | bip-erp#2824 | [bip-erp#2837](https://github.com/bip-itteam-internal/bip-erp/pull/2837) | terbuka; gerbang 24 service + judge lolos |
| T2 status sinkron toko nonaktif | bip-erp#2825 | [bip-erp#2835](https://github.com/bip-itteam-internal/bip-erp/pull/2835) | terbuka; gerbang + judge lolos |
| T3 kegagalan sinkron berbunyi | bip-erp#2826 | [bip-erp#2836](https://github.com/bip-itteam-internal/bip-erp/pull/2836) | terbuka; lolos di percobaan 2 |
| T5 kartu ulasan | erp-frontend#2207 | [erp-frontend#2209](https://github.com/bip-itteam-internal/erp-frontend/pull/2209) | terbuka; lolos di percobaan 2 |

Sisa yang hanya bisa dikerjakan manusia:

- Merge keempat PR; T1 dan T2 menyentuh baris berdekatan di `services/integration/main.go`, jadi yang di-merge belakangan mungkin perlu menyelesaikan konflik kecil.
- Deploy `integration-service` (dan frontend), lalu T4: pasang paket izin ke tiga akun Shop Quality. Urutannya tidak boleh terbalik.
- T5: klik URL Seller Center Shopee dari akun penjual sebelum merge, dan buka layarnya sekali.
- T3: picu satu pemberitahuan job gagal di DEV; putuskan apakah TikTok "sebagian produk gagal" layak menggagalkan job (risiko pemberitahuan harian yang berhenti dibaca).
- Temuan di luar batas T3, belum punya issue: `Manager.TriggerNow` (pemicu manual job) memakai percobaan ulang bawaan manager, bukan pengaturan per-job, sehingga pemicu manual `sync-reviews` masih mengulang 3 kali dan menimpa pesan timeout.
- Satu perjalanan utuh sebagai Shop Quality sesudah semuanya naik: buka menu Ulasan, pilih "Belum dibalas", salin nomor pesanan, buka Seller Center, balas, lalu lihat ulasan itu hilang dari "Belum dibalas" esok paginya.
## Urutan dan ketergantungan

```
ADR Diterima ──► T1 (cakupan CS) ──► deploy integration-service PROD ──► T4 (pasang paket izin, manusia)
T2 (status sinkron toko nonaktif)   bebas
T3 (kegagalan sinkron berbunyi)     bebas
T5 (kartu ulasan: nomor pesanan + Seller Center, erp-frontend)   bebas
```

T2 sebaiknya naik sebelum T4: tanpa itu, hal pertama yang dibaca Shop Quality di halaman Ulasan adalah peringatan "toko gagal sinkron" yang palsu.

## Task

### T1. Cakupan baca ulasan mencakup toko pegangan CS (`cs_shop_mappings`)

- **Repo**: `bip-erp` · **Issue**: [bip-erp#2824](https://github.com/bip-itteam-internal/bip-erp/issues/2824) · **Urutan**: 1

**Pemutus:** irfanarfianto · **PIC:** belum ditetapkan

#### Masalah
Rute `/reviews/*` hanya membuka toko di `icc_account_mappings` milik pemanggil (`services/integration/internal/interface/http/review_scope.go:68-103`). Shop Quality tercatat di `cs_shop_mappings`, sehingga mendapat nol baris.

#### Keputusan
ADR "Cakupan Baca Ulasan Mencakup Toko Pegangan CS, Menu Dibuka lewat Paket Izin yang Ada". **Layak `Siap Agent` sesudah ADR berstatus Diterima.** Bentuknya: cakupan baca = gabungan toko `icc_account_mappings` aktif dan `cs_shop_mappings` aktif; hak mengajukan komplain tidak ikut melebar; tanpa izin baru dan tanpa perubahan frontend.

#### Yang harus benar
- Pemanggil yang hanya punya baris aktif di `cs_shop_mappings` menerima data hanya untuk toko di baris itu, di kelima rute `/reviews/*`.
- Pemanggil di kedua koleksi menerima gabungannya tanpa toko ganda.
- Tanpa baris aktif di kedua koleksi: 200 berisi nol baris.
- Baris CS ber-`is_active: false` tidak membuka toko.
- Leader/SPV marketing dan staf Integration tetap membaca seluruh toko; `?shop_id=` tetap tak bisa melangkahi batas.
- Gagal membaca salah satu pemetaan = 500, bukan daftar kosong dan bukan cakupan sebagian.
- Test memakai toko CS dan toko ICC yang berbeda, plus satu test lewat `app.Test` pada grup `/reviews`.
- Gerbang tulis komplain gudang dan QC tidak berubah.
- Dua komentar kode yang menyatakan ulang aturan cakupan (`shared-library/common/catalog_akuntoko.go`, `services/assistant/internal/alat/lintas_ulasan_produk.go:16-23`) menunjuk ke `review_scope.go`, tidak lagi menyalin aturannya.

#### Di luar cakupan
Frontend; balas ulasan; ulasan TikTok per pembeli; ulasan Lazada; pemasangan paket izin (T4); menggabungkan kedua koleksi pemetaan.

#### Data / bukti pendukung
Lihat angka ukur prod di kepala dok ini. Bentuk `cs_shop_mappings`: `employee_id`, `channel` (huruf besar), `shop_id` (string), `shop_name`, `is_active`. `marketplace_reviews.shop_id` bertipe int64, `review_sync_states.shop_id` string.

#### Prasyarat
ADR berstatus Diterima.

### T2. Status sinkron ulasan tidak menghitung toko yang sudah dinonaktifkan

- **Repo**: `bip-erp` · **Issue**: [bip-erp#2825](https://github.com/bip-itteam-internal/bip-erp/issues/2825) · **Urutan**: bebas, sebaiknya sebelum T4

**Pemutus:** irfanarfianto · **PIC:** belum ditetapkan

#### Masalah
Baris status halaman Ulasan memperingatkan toko gagal sinkron dan "terakhir" berbulan lalu, padahal sinkronnya sehat. Sebabnya baris lama toko nonaktif di `review_sync_states` tetap dikirim `GET /reviews/sync-status` (`services/integration/internal/infrastructure/repository/review_repo.go:434-447`).

#### Keputusan
Tertulis di issue: `/reviews/sync-status` tidak mengembalikan baris toko yang `DISABLED` di `shop_sync_states`; baris tidak dihapus; penyaringan di backend.

#### Yang harus benar
- Respons tidak memuat toko `DISABLED`.
- Pencocokan channel tidak peka huruf: `shop_sync_states.channel` berisi `tiktok`, `review_sync_states.channel` berisi `TIKTOK`.
- Toko aktif yang benar-benar gagal tetap muncul.
- Cakupan toko pemanggil tetap berlaku.
- Tidak ada dokumen `review_sync_states` yang dihapus atau diubah.

#### Di luar cakupan
Cara frontend menghitung "terakhir" dan "gagal"; pembersihan data prod; notifikasi (T3).

#### Data / bukti pendukung
Diukur prod 2026-10-08: SHOPEE 15 baris, 0 gagal. TIKTOK 59 baris, 5 ber-`last_error`, sukses terlama 2026-08-20. Sepuluh baris TIKTOK tertua seluruhnya milik toko yang `DISABLED` sejak 2026-08-24 sampai 2026-08-27. Sesudah disaring: sukses terlama 2026-10-08, gagal 0.

#### Prasyarat
Tidak ada.

### T3. Kegagalan sinkron ulasan harus berbunyi: `SyncAll` selalu melapor sukses

- **Repo**: `bip-erp` · **Issue**: [bip-erp#2826](https://github.com/bip-itteam-internal/bip-erp/issues/2826) · **Urutan**: bebas

**Pemutus:** irfanarfianto · **PIC:** belum ditetapkan

#### Masalah
`SyncAll` selalu mengembalikan `nil` (`services/integration/internal/usecase/review_sync_usecase.go:380-388`), sehingga hook pemberitahuan gagal tidak pernah terpanggil dan `worker_history` selalu `success`, termasuk untuk run yang terpotong timeout.

#### Keputusan
Tertulis di issue: job gagal bila konteks berakhir sebelum seluruh toko diproses, daftar toko satu channel gagal dimuat, atau sedikitnya satu toko aktif gagal pada run itu. Pesannya menyebut jumlah dan nama toko. Satu toko gagal tetap tidak menghentikan toko lain. Kanalnya hook `WithOnJobError` yang sudah ada.

#### Yang harus benar
- `SyncAll` non-nil pada ketiga keadaan itu, `nil` bila semua toko aktif sukses.
- Toko `DISABLED` yang dilewati tidak dihitung gagal.
- Run terpotong timeout tercatat `failed`.
- Toko berikutnya tetap diproses sesudah satu toko gagal; Shopee gagal total tidak mencegah TikTok.

#### Di luar cakupan
Retry, kejar-ketinggalan run yang terlewat, tombol sinkron manual, kanal notifikasi baru.

#### Data / bukti pendukung
Diukur prod 2026-10-08: 40 run terakhir `success`, 11 sampai 14 menit. Hari tanpa run (WIB): 2026-08-29, 09-08, 09-09, 09-24, 09-26, tanpa satu pun jejak gagal. `worker_configs.timeout` tersimpan 60 menit. Tidak ada toko aktif yang gagal saat diukur.

#### Prasyarat
Tidak ada.

### T4. Pasang paket izin ke akun Shop Quality (manusia, bukan issue)

Sesudah T1 naik ke prod: pasang paket `marketing_akuntoko_pemegang` ke tiga akun berjabatan Shop Quality. Buktikan dulu di DEV bahwa menu Ulasan muncul bagi akun tanpa peran marketing (asumsi ADR § Decision 3). Tulis prod dijalankan manusia.

### T5. Kartu ulasan menampilkan nomor pesanan dan jalan ke Seller Center untuk membalas

- **Repo**: `erp-frontend` · **Issue**: [erp-frontend#2207](https://github.com/bip-itteam-internal/erp-frontend/issues/2207) · **Urutan**: bebas

Ditemukan saat menelusuri alur dari sudut pemohon: sesudah membaca ulasan di ERP, langkah membalasnya ada di Seller Center tanpa pegangan apa pun, karena kartu tidak memuat nomor pesanan. Keputusan dan kriterianya tertulis di badan issue: nomor pesanan dengan tombol salin, dan tautan "Balas di Seller Center" untuk ulasan Shopee. Tanpa perubahan backend. ⚠️ URL Seller Center Shopee wajib diklik manusia yang punya akses sebelum merge.
## Tidak dikerjakan

- **Balas ulasan dari ERP.** Menunggu cek izin scope API Shopee dan ADR tersendiri.
- **Ulasan TikTok per pembeli dan ulasan Lazada.** TikTok batas API; Lazada belum pernah diriset. Bila diminta, mulai dari riset API, bukan dari layar.
- **Shop Quality mengajukan komplain dari ulasan.** Diputuskan baca saja dulu.

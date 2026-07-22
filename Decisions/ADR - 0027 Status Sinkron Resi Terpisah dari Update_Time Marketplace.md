## ADR 0027 — Status Sinkron Resi Terpisah dari `update_time` Marketplace

- **Status**: ✅ Accepted (mencerminkan kondisi kode; sudah jalan di [[Microservices - Integration Service]])
- **Tanggal**: 2026-07-22/23
- **Konteks dok**: [[Microservices - Integration Service]] · [[Microservices - Manufacture Service]]

## Context

Master Resi WMS (koleksi `manufacture.Resi`, dipakai gudang men-scan paket & mencocokkan ke retur) diisi lewat jalur incremental: worker `sync-resi-wms` (tiap 10 menit) menarik order ber-AWB dari `transaction_orders`/`shopee_order_details`/`tt_shop_orders` dengan filter **watermark** `update_time >= cursor`, lalu memajukan cursor per channel ke `update_time` terbesar batch itu (koleksi `sync_cursors`).

`update_time` sendiri **bukan timestamp buatan kita** — itu field asli marketplace ("kapan order ini terakhir berubah menurut Shopee/TikTok"), dipakai sebagai watermark karena itu pola yang sudah dipakai konsisten di semua job sync lain di service ini (order TikTok, order Shopee, dst).

**Bug ditemukan 2026-07-22** (dilaporkan user, dibuktikan ke data prod): resi Shopee `SPXID064036697197` (order `260715Q6Q7MSWG`) **ada** dan valid — AWB-nya tersimpan di `shopee_order_details` — tapi **tak pernah muncul** di Master Resi. Akarnya: `SetOrderTracking` (dipanggil saat AWB baru diketahui, terpisah dari sync order penuh) menyimpan `tracking_number` lewat `$set` **sempit** yang **tidak** ikut membarui `update_time`. Begitu watermark `sync-resi-wms` sudah lewat `update_time` LAMA order itu, order tersebut **permanen** tak tertangkap lagi — walau datanya sudah lengkap sejak lama.

Ini bukan bug "field yang salah dipilih". `update_time`-based watermark adalah pola standar (incremental sync via high-water-mark) yang valid dan dipakai benar di tempat lain. Akar masalahnya: `update_time` dipakai untuk **dua peran sekaligus** — "timestamp asli marketplace" **dan** "penanda buat cursor kita" — dan satu jalur tulis (`SetOrderTracking`) tidak menghormati kontrak peran kedua itu. Jalur tulis MANA PUN di masa depan yang mengubah sesuatu yang relevan untuk resi-sync, tapi lupa membarui `update_time`, bisa memunculkan kelas bug yang sama persis — kesalahan tak terlihat di code review karena `update_time` "tampak" seperti field housekeeping biasa.

Tambalan cepat (`SetOrderTracking` ikut membarui `update_time`) menutup lubang yang SUDAH ditemukan, tapi tidak menghilangkan risikonya untuk jalur tulis yang belum ada.

## Decision

**Pisahkan status "sudah tersinkron ke Master Resi" ke koleksi tersendiri** (`resi_sync_state`, satu dokumen per `(channel, order_id)` berisi `tracking_number` terakhir yang berhasil disync), **bukan** field tambahan di dokumen order.

Alasan bukan field tambahan: order TikTok disimpan via `ReplaceOne` (ganti dokumen **penuh** tiap re-sync, `tiktok_shop_repo.go` `SaveOrder`/`SaveOrders`) — field tambahan yang bukan bagian struct entity resmi akan **hilang** tiap kali order itu di-refresh dari API TikTok. Koleksi terpisah kebal dari itu.

Dua lapis pengaman dipasang, bukan satu:

1. **Jalur cepat** (`sync-resi-wms`, tetap 10 menit, cursor `update_time` **tidak diubah**) — sekarang JUGA menulis `resi_sync_state` tiap sukses push. `SetOrderTracking` tetap dibarui membarui `update_time` (fix cepat dipertahankan sebagai lapis pertama, murah).
2. **Jaring pengaman** (`resi-wms-safety-net`, task baru, tiap 2 jam — pola yang sama dengan `recover-tiktok-returns`/`sync-shopee-returns` yang sudah ada untuk retur) — menyapu **SEMUA** order ber-AWB (`updatedSince=0`, mengabaikan cursor incremental sama sekali), diff terhadap `resi_sync_state`: order tanpa entri, atau entri dengan `tracking_number` **beda** dari yang sekarang (AWB di-reassign kurir) → straggler, di-push ulang.

Kunci desainnya: jaring pengaman **tidak** bergantung pada `update_time` sama sekali — kebenarannya murni "ada di `resi_sync_state` dengan AWB yang cocok, atau tidak". Kalau jalur tulis BARU di masa depan lupa mencatat ke `resi_sync_state`, order itu otomatis muncul lagi di sapuan 2 jam berikutnya — **tanpa perlu tahu jalur mana yang salah**.

Cap sapuan (`resiWMSSafetyNetScanCap`) sengaja **besar** (200.000, bukan sekadar "di atas volume nyata" seperti cap lain) dan **dilog eksplisit** bila tersentuh: cursor sapuan ini ephemeral (mulai dari 0 tiap run) — cap yang terlalu kecil justru bisa menciptakan blind-spot permanennya sendiri (selalu berhenti di irisan tertua yang sama, tak pernah maju), persis kelas bug yang sedang diberantas.

Backfill satu-kali untuk resi yang SUDAH terlanjur macet (sebelum safety-net pertama kali jalan): `cmd/resiwmsbackfill` (dry-run default, `--apply`) — membandingkan watermark `sync_cursors` terhadap `update_time` order untuk cari kandidat stuck, lalu membump `update_time`-nya (memicu jalur cepat, bukan menduplikasi logika push). Dalam praktik, safety-net sendiri sudah cukup menyembuhkan ini otomatis pada run pertama; tool CLI berguna untuk menyembuhkan SATU order tertentu segera, tanpa menunggu jadwal.

## Consequences

**Konsekuensi menerima:**

- Koleksi baru (`resi_sync_state`) untuk dijaga — bukan cost besar (satu dokumen kecil per order-ber-AWB), tapi tetap permukaan baru.
- Sapuan penuh tiap 2 jam membaca ulang SELURUH order ber-AWB per channel (dibatasi cap) — lebih berat dari cursor incremental murni, tapi pada skala volume retur/resi service ini ("volume rendah", per catatan TikTok sendiri) itu bukan masalah nyata.
- Dua lapis (jalur cepat + jaring pengaman) berarti dua tempat berpotensi diverge kalau salah satu diubah tanpa mengubah yang lain — keduanya WAJIB dijaga konsisten (nama channel, field mapping order→tracking).

**Konsekuensi menolak pendekatan "ganti field watermark saja":**

- Mengganti `update_time` dengan timestamp lain (mis. `created_at`) TIDAK menghilangkan kelas bug ini — cuma memindahkannya. Order yang tracking-nya diisi belakangan tetap punya timestamp "asal" yang jauh lebih lama dari saat AWB benar-benar terisi, apa pun nama fieldnya.
- Mengandalkan disiplin "tiap jalur tulis baru WAJIB ingat membarui field X" tidak scalable — itu persis kegagalan yang menyebabkan bug ini muncul pertama kali (developer yang menulis `SetOrderTracking` tidak salah paham arsitektur, cuma tidak tahu field itu dipakai cursor DI FILE LAIN).

**Kalau suatu saat volume order-ber-AWB tumbuh signifikan** (cap 200.000 mulai tersentuh secara rutin, bukan cuma sekali di awal): pertimbangkan mengganti sapuan penuh dengan cursor yang **juga** persisten tapi berbasis kunci di `resi_sync_state` sendiri (bukan `update_time` order) — kuncinya boleh watermark lagi, tapi atas field yang KITA kendalikan penuh siklus hidupnya, bukan field milik upstream.

## Dokumen Terkait

- [[Microservices - Integration Service]] — implementasi `sync-resi-wms` + `resi-wms-safety-net`, bagian *Background Workers*
- [[Microservices - Manufacture Service]] — konsumen Master Resi (`POST /resi/sync-batch`)
- [[ADR - 0025 Log Sumber vs Input WMS + Stempel Penginput]] — keputusan terkait gerbang gudang retur (domain berdekatan, bukan mekanisme sync yang sama)

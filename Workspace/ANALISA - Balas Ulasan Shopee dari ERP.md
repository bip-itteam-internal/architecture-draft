Papan kerja untuk [[ADR - 0176 Ulasan Shopee Dibalas dari ERP oleh Pemegang Toko, Otomatisasi Menyusul]]. Cara kerja modul ulasan ada di [[Microservices - Integration Service]] § Ulasan Marketplace dan [[API - Integration Service]] § Reviews.
Berubah tiap item selesai; keputusannya ada di ADR, bukan di sini.

⛔ **Menunggu ADR - 0176 Ulasan Shopee Dibalas dari ERP oleh Pemegang Toko, Otomatisasi Menyusul Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

- **Ukuran**: **Sedang**. Dua repo, masing-masing satu PR: `bip-erp` (klien `reply_comment`, rute kirim, jejak, `boleh_balas`) dan `erp-frontend`. FE wajib berubah: kartu ulasan hari ini hanya merender balasan yang sudah ada atau tautan "Balas di Seller Center" (`src/features/integration/reviews/components/review-card.tsx:172-189`), dan halaman Komplain Belum Dibalas menulis "ERP hanya membaca" (`src/i18n/locales/id.ts:14277`). `mybharata-app` tidak punya layar ulasan.
- **Pemutus**: irfanarfianto
- **Asal**: permintaan Tech Development (irfanarfianto), 2026-10-13. Masalah yang dijawab (beban CS dan cakupan balasan) adalah asumsi analis dari data di bawah, belum dikonfirmasi pemilik proses CS.

Diukur prod 2026-10-13, ulasan Shopee 90 hari (angka bergerak, ukur ulang sebelum dipakai memutuskan):

- 22.429 ulasan, 8.345 dibalas (37%), median jeda balas 45 jam, p90 112 jam.
- Bintang 5: 20.566. Bintang 1-2: 167. Berteks: 1.749.
- Empat toko Kyura: 9.609 ulasan, 58 dibalas. Toko Beautyhacks: 50% sampai 75% dibalas.
- 98,5% balasan memakai empat teks yang sama; hanya 61 teks balasan berbeda. Ini bahan langkah otomatisasi, bukan cakupan task di sini.

## Urutan dan ketergantungan

```
ADR Diterima ──► [BE] bip-erp ──► deploy integration-service ──► [FE] erp-frontend ──► deploy frontend
```

Merge [FE] lebih dulu boleh (tanpa `boleh_balas` tombol tak tampil); deploy [FE] sebelum [BE] tidak.

## Induk: Balas ulasan Shopee dari ERP

- **Repo**: `bip-erp` (tanpa PR sendiri)
- **Issue**: TBD

**Pemutus:** @irfanarfianto
**PIC:** @

### Masalah

CS membalas ulasan Shopee satu per satu di Seller Center, padahal sudah membacanya di ERP. Diukur prod 2026-10-13: dari 22.429 ulasan 90 hari baru 37% dibalas, median 45 jam; empat toko Kyura hanya 0,6%.

### Keputusan

[[ADR - 0176 Ulasan Shopee Dibalas dari ERP oleh Pemegang Toko, Otomatisasi Menyusul]]. Sub-issue layak `Siap Agent` sesudah ADR berstatus Diterima (kini 🟡 Diusulkan).

### Yang harus benar

- [ ] Kedua sub-issue merged dan ter-deploy, BE lebih dulu.
- [ ] Satu perjalanan utuh sebagai CS pemegang toko Shopee: buka Ulasan, pilih "Belum dibalas", tulis balasan, Kirim, ulasan keluar dari daftar, balasan tampil di Shopee.

### Di luar cakupan

Template, kirim massal, balasan otomatis, draf AI, TikTok.

### Data / bukti pendukung

Lihat angka di kepala papan ini.

### Prasyarat

ADR 0176 Diterima.

## [BE] Kirim balasan ulasan Shopee lewat reply_comment

- **Repo**: `bip-erp`, sub-issue induk
- **Urutan**: 1
- **Issue**: TBD

**Pemutus:** @irfanarfianto
**PIC:** @

### Masalah

integration-service hanya membaca ulasan Shopee (`get_comment`); tidak ada pemanggilan `reply_comment` di `services/` (`git grep origin/main`, 2026-10-13). Rute `/reviews/*` semuanya GET (`services/integration/main.go`, grup `/reviews` ber-`MiddlewareCakupanUlasan`).

### Keputusan

[[ADR - 0176 Ulasan Shopee Dibalas dari ERP oleh Pemegang Toko, Otomatisasi Menyusul]] §1-§6, layak `Siap Agent` sesudah ADR berstatus Diterima. Bentuknya: satu ulasan per kirim, saat itu juga, token ERP_SYSTEM toko; boleh = baris aktif `icc_account_mappings` atau `cs_shop_mappings` untuk toko itu (pembaca tanpa batas tidak); jejak di koleksi terpisah append-only.

### Yang harus benar

- [ ] Klien Shopee punya fungsi `reply_comment` (POST bertanda tangan, pola `ShipOrder` di `shopee_client_new.go`), membaca galat dari `error` dan `response.result_list[].fail_error`, bukan dari status HTTP.
- [ ] Rute POST kirim balasan di grup `/reviews` (didaftarkan sebelum saudara ber-`:param` yang bisa menelannya). Teks dipangkas lalu ditolak 400 bila kosong atau lebih dari 500 karakter, sebelum memanggil Shopee.
- [ ] Ulasan TikTok atau `comment_id` yang tak ada di `marketplace_reviews` ditolak tanpa memanggil Shopee.
- [ ] Satu fungsi menentukan boleh membalas (ICC aktif ATAU CS aktif untuk `shop_id` ulasan). Rute kirim menolak 403 bila tidak boleh; `GET /reviews/comments` menambahkan `boleh_balas` per baris dari fungsi yang SAMA. Uji: Marketing Leader / staf Integration tanpa pemetaan toko itu mendapat `boleh_balas:false` dan 403; pemegang lewat CS saja mendapat `true`.
- [ ] Mapping yang gagal dibaca tetap 500 (gagal tertutup), seperti cakupan baca.
- [ ] Setiap percobaan (berhasil maupun gagal) tercatat append-only di koleksi baru: `comment_id`, `shop_id`, teks, pengirim (`entity.Actor`), waktu, hasil + kode galat Shopee. Tidak ditulis ke dokumen `marketplace_reviews`.
- [ ] Sesudah berhasil, `comment_reply` dokumen ulasan di-`$set` (teks, `hidden:false`, waktu kirim), sehingga `GET /reviews/comments?unreplied=true` tidak lagi memuatnya. Bukan `ReplaceOne`.
- [ ] Galat dipetakan ke kode respons yang bisa dibedakan FE: `product.duplicate_request` (sudah dibalas), `product.error_permission`/`error_auth` (token toko), `product.comment_length_invalid`, `product.error_not_exist`, lainnya.
- [ ] Minimal satu test `app.Test(httptest.NewRequest(...))` untuk jalur galat rute kirim, dan test klien yang mengurai rekaman respons Shopee sungguhan (galat ber-HTTP 200).

### Di luar cakupan

Template, kirim massal (batch 100), worker otomatis, draf AI, TikTok, perubahan izin/paket.

### Data / bukti pendukung

- App ERP_SYSTEM "One Bharata" (Live Partner_id 2032314) berkategori ERP System, tipe yang tercantum di "API Permissions" dokumentasi `v2.product.reply_comment` (dicek Console 2026-10-13).
- Batasan API: 1-100 komentar per panggilan, 1-500 karakter, satu balasan per ulasan (`product.duplicate_request`).
- Sync menimpa dokumen utuh (`review_repo.go` `BulkUpsertReviews`) dan berhenti dini (`review_sync_usecase.go`); itu alasan jejak terpisah dan `$set` lokal.

### Prasyarat

ADR 0176 Diterima. Tidak ada issue lain.

## [FE] Kotak balasan ulasan Shopee di halaman Ulasan dan Komplain Belum Dibalas

- **Repo**: `erp-frontend`, sub-issue induk
- **Urutan**: 2, deploy sesudah [BE]
- **Issue**: TBD

**Pemutus:** @irfanarfianto
**PIC:** @

### Masalah

Kartu ulasan Shopee yang belum dibalas hanya punya tautan "Balas di Seller Center" (`review-card.tsx:177-189`), dan halaman Komplain Belum Dibalas menulis "Membalas dilakukan di Seller Center; ERP hanya membaca" (`id.ts:14277`).

### Keputusan

[[ADR - 0176 Ulasan Shopee Dibalas dari ERP oleh Pemegang Toko, Otomatisasi Menyusul]] §2, §3, §6, layak `Siap Agent` sesudah ADR berstatus Diterima. Tombol balas tampil hanya bila backend mengirim `boleh_balas:true`; FE tidak menyalin aturan izinnya.

### Yang harus benar

- [ ] Kartu ulasan Shopee tanpa `comment_reply` dan `boleh_balas:true` menampilkan aksi Balas: teks (penghitung, maks 500), konfirmasi satu langkah yang menyebut balasan tak bisa diubah, tombol Kirim nonaktif selama `isPending`. Pola mengikuti `ajukan-komplain-modal.tsx`.
- [ ] `boleh_balas` false atau tidak ada di respons (BE lama) = aksi Balas tidak tampil, tanpa galat. Tautan Seller Center tetap ada sebagai jalan lain.
- [ ] Sesudah berhasil: toast sukses, query `review-comments` di-invalidate, balasan tampil di kartu, ulasan keluar dari "Belum dibalas".
- [ ] Tiap kode galat dari [BE] punya kalimat sendiri (sudah dibalas, token toko perlu otorisasi ulang, panjang teks, ulasan tidak ada, gagal umum).
- [ ] Halaman Komplain Belum Dibalas punya aksi Balas yang sama (komponen yang sama, bukan salinan).
- [ ] Teks baru lewat `t()` di `id.ts` DAN `en.ts`. Kalimat "ERP hanya membaca" (`id.ts:14277`) dan "balasan tetap di Seller Center" (`id.ts:20951`) beserta padanan `en.ts` diganti; komentar `url-ulasan.ts` yang menyebut API Shopee tak menyediakan balasan dibetulkan.
- [ ] Ulasan TikTok tidak berubah.

### Di luar cakupan

Template, pilih banyak + kirim massal, draf AI, perubahan menu/izin.

### Data / bukti pendukung

Tidak perlu data prod.

### Prasyarat

ADR 0176 Diterima. Deploy sesudah sub-issue [BE] ter-deploy (merge lebih dulu boleh).

## Sisa yang hanya bisa dikerjakan manusia

- Setujui ADR 0176 (baris status), lalu hapus baris ⛔ di kepala papan ini.
- Pasang label `Siap Agent` pada sub-issue sesudah checklist Definition of Ready terpenuhi.
- Deploy prod `integration-service` lalu `frontend-hris`.
- CS yang hanya memegang toko lewat `cs_shop_mappings` baru melihat menu Ulasan sesudah paket izin [[ADR - 0160 Cakupan Baca Ulasan Mencakup Toko Pegangan CS, Menu Dibuka lewat Paket Izin yang Ada]] terpasang padanya (T4 papan [[ANALISA - Shop Quality Membaca Ulasan Toko Pegangan CS]]).
- Kirim balasan pertama sungguhan dari akun pemegang toko dan cocokkan di Seller Center. Balasan tidak bisa ditarik, jadi pilih ulasan yang memang perlu dibalas.

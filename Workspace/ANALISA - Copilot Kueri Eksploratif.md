**Status**: 🟡 Blueprint dari `/analisa-kebutuhan` 2026-10-12. Keputusannya di [[ADR - 0173 Copilot Boleh Kueri Eksploratif Baca-Saja atas Data Bisnis Berdaftar-Izin, Dijalankan Service Pemilik]]; dok domain [[Microservices - Assistant Service]] § Tool kueri eksploratif. Dok ini papan kerja, bukan arsitektur.

⛔ **Menunggu ADR 0173 "Copilot Boleh Kueri Eksploratif Baca-Saja atas Data Bisnis Berdaftar-Izin, Dijalankan Service Pemilik" Diterima: sebelum itu ANALISA ini BUKAN keputusan yang bisa ditunjuk `/brief`.**

- **Pemutus**: irfanarfianto
- **Ukuran**: **Sedang**. Dua repo, masing-masing satu PR per issue: `bip-erp` (eksekutor + tool) dan `erp-frontend` (label). FE harus berubah karena kode penanda yang tak dikenal tampil sebagai label umum tanpa teks kuerinya (`erp-frontend/src/features/copilot/lib/penanda.ts:7-9`, `KODE_PENANDA_DATA`). Di `bip-erp` ada dua PR (eksekutor, lalu tool), jadi bentuknya induk + tiga sub-issue.
- **Syarat PROD di luar issue**: persetujuan tertulis Direksi untuk data asli lewat relay AI (ADR 0132), dan user Mongo read-only dibuat manusia.

## Kebutuhan yang dijawab

Pertanyaan data bisnis yang belum punya endpoint (contoh 2026-10-12: penjualan afiliasi vs non-afiliasi per bulan) dijawab Copilot tanpa menunggu siklus endpoint + tool baru. Pemakai: semua pemakai Copilot, dengan hasil yang hanya keluar bila penanya lolos gerbang data pemiliknya. Angkanya untuk bahan diskusi dan rapat, bukan uang.

Ukur prod `assistant_db.percakapan` (30 Sep - 12 Okt 2026): ±10 dari 158 giliran menjawab "data belum tersedia", dan 7 penolakan yang benar (4 data pribadi, 3 tak berhak) yang tetap harus ditolak.

## Urutan

1. Induk tanpa PR.
2. **[BE] eksekutor** (1/3).
3. **[BE] tool `kueri`** (2/3), sesudah 1/3 merged.
4. **[FE] label** (3/3), deploy sesudah 2/3.

Deploy: user read-only (manusia), env URI baru + `--force-recreate` marketing-analytics, marketing-analytics, assistant-service, frontend.

---

### Induk: Copilot: tool kueri eksploratif baca-saja (ADR 0173)

- **Repo**: bip-erp
- **Issue**: bip-erp#(diisi saat dibuat)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Copilot menjawab "tidak tahu" untuk pertanyaan data yang belum punya endpoint (ADR 0132 §4), dan menambah endpoint + tool per pertanyaan dinilai terlalu lambat. Rincian tiap bagian ada di sub-issue.

## Keputusan

[[ADR - 0173 Copilot Boleh Kueri Eksploratif Baca-Saja atas Data Bisnis Berdaftar-Izin, Dijalankan Service Pemilik]]. Layak `Siap Agent` sesudah ADR itu berstatus Diterima (sekarang 🟡 Diusulkan).

## Yang harus benar

- [ ] Ketiga sub-issue merged.
- [ ] Satu perjalanan utuh di DEV lewat layar Copilot: "penjualan TikTok afiliasi vs non-afiliasi September 2026" menghasilkan tabel berlabel eksploratif dengan kuerinya terlihat.
- [ ] Di DEV, penanya tanpa gerbang analitik marketing mendapat "tidak berhak".

## Di luar cakupan

Join lintas sumber, koleksi di luar daftar-izin, dan deploy PROD (menunggu Direksi + manusia).

## Data / bukti pendukung

Lihat ADR 0173 § Context.

## Prasyarat

Tidak ada.

---

### 1/3 [BE] Eksekutor kueri eksploratif baca-saja di marketing-analytics

- **Repo**: bip-erp (sub-issue induk)
- **Issue**: bip-erp#(diisi saat dibuat)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Tidak ada jalur baca terkendali untuk kueri agregasi ad-hoc. Semua koneksi Mongo memakai root (`git grep readOnly|createUser` atas `origin/main`: nol, 2026-10-12), dan "baca-saja" marketing-analytics ke `integration_db` hanya konvensi komentar.

## Keputusan

ADR 0173 §2-§4, §6-§8. Layak `Siap Agent` sesudah ADR itu Diterima. Bentuk: `POST /kueri-eksploratif`, digerbang `common.RequireAnalitikMarketing`, daftar-izin koleksi + field di satu tempat, wajib `$group`/`$count`, `maxTimeMS` 15 detik, maksimal 200 baris, user read-only terpisah per container.

## Yang harus benar

- [ ] Daftar-izin berupa **izin** (bukan daftar-tolak) per koleksi dan per field, satu tempat di kode: `mart_live_sessions`, `mart_profit_attribution`, `mart_video_performance`, `live_shifts` (tanpa `employee_id`), `transaction_orders` (tanpa `buyer` dan field identitas pembeli lain), `affiliate_orders`, `shopee_affiliate_conversion`.
- [ ] Field di luar daftar yang disebut di tahap mana pun (termasuk di ekspresi `$group`/`$project`/`$match`) ditolak 400 bersebab.
- [ ] Tahap `$lookup`, `$graphLookup`, `$unionWith`, `$out`, `$merge`, `$function`, `$accumulator`, `$where` ditolak 400. Hanya tahap di ADR 0173 §2 yang lolos.
- [ ] Pipeline tanpa `$group`/`$count` ditolak 400. `$project` sesudah `$group` tak bisa menghidupkan field mentah.
- [ ] `maxTimeMS` 15000, keluaran dipotong 200 baris dengan penanda `terpotong: true`, tanpa `allowDiskUse`.
- [ ] Penanya tak lolos `RequireAnalitikMarketing` → 403, dan test lewat `app.Test` membuktikannya.
- [ ] Koneksi eksekutor memakai URI read-only baru (env terpisah), bukan URI tulis service. URI kosong → rute membalas 503 bersebab, service tetap hidup.
- [ ] Skrip `scripts/mongo-user-kueri-readonly.js` (dry-run + apply) membuat user ber-peran `read` hanya pada DB-nya, untuk kedua container. **Tidak dijalankan agent di prod.**
- [ ] Test kontrol negatif: hapus satu field dari daftar-izin, pastikan test pemakai field itu merah. Hilangkan pengecekan `$lookup`, pastikan test-nya merah.
- [ ] Rute didaftarkan di akar modul (gateway membuang prefix `/api/marketing-analytics`), dengan test yang mereproduksi pemotongan prefix.

## Di luar cakupan

Tool di assistant-service (2/3), label FE (3/3), menambah koleksi di luar daftar, join lintas DB, dan menjalankan skrip user di dev/prod.

## Data / bukti pendukung

Kunci dokumen `transaction_orders` (prod, diukur 2026-10-12): `_id, order_id, channel, buyer, buyer_cancel_reason, cancel_reason, cancellation_initiator, cancellation_initiator_raw, cancelled_at, completed_at, created_at, income, income_attempts, income_status, is_sample, items, order_date, order_update_date, package_id, paid_at, payment, raw_status, returned_at, rts_time, shipped_at, shipping_fee_gmv_dashboard, shop_id, shop_name, status, sub_total, total_payment, updated_at`. `buyer` dan `items` (berisi atribut pembeli/produk per baris) wajib diputuskan per sub-field di daftar-izin.

## Prasyarat

ADR 0173 Diterima.

---

### 2/3 [BE] Tool `kueri` di assistant-service

- **Repo**: bip-erp (sub-issue induk)
- **Issue**: bip-erp#(diisi saat dibuat)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Copilot tidak punya tool untuk pertanyaan yang tak dilayani 32 tool khususnya, sehingga ia menjawab "data belum tersedia" (±10 dari 158 giliran prod, 30 Sep - 12 Okt 2026).

## Keputusan

ADR 0173 §1, §5, §8. Layak `Siap Agent` sesudah ADR itu Diterima. Bentuk: argumen `sumber`, `koleksi`, `pipeline`, `tujuan`; memanggil eksekutor lewat gateway dengan JWT penanya; penanda `kueri_eksploratif` membawa pipeline + tujuan.

## Yang harus benar

- [ ] Tool `kueri` terpasang untuk semua pemakai `BolehPakaiCopilot`, memanggil `POST /api/marketing-analytics/kueri-eksploratif` lewat gateway dengan header `Authorization` penanya (pola `KlienMarketing.ambil`).
- [ ] Deskripsi tool mengarahkan model memakainya **hanya bila tak ada tool khusus**, dan memuat ringkasan daftar-izin yang dibaca dari satu sumber (bukan salinan ketik ulang).
- [ ] Balasan 403 eksekutor menjadi status `tidak_berhak`, 400 menjadi galat bersebab yang diteruskan ke model untuk diperbaiki, 503 menjadi "sumber belum tersedia".
- [ ] Tiap hasil membawa penanda `kueri_eksploratif` (alasan = `tujuan` + pipeline), sumber, dan umur data. Penjaga `hitungan_model` dan `angka_tak_cocok` tetap jalan.
- [ ] Hasil kueri melewati samaran dan penjaga `BocorDi` seperti tool lain.
- [ ] Uji pertanyaan tetap: satu kasus kueri eksploratif ditambahkan ke rangkaian uji pertanyaan tetap.

## Di luar cakupan

Eksekutor (1/3), label FE (3/3), dan memakai hasil `kueri` sebagai masukan tool lain.

## Data / bukti pendukung

Ukur prod `assistant_db.percakapan` 2026-10-12: 158 giliran, 10 penanya; jawaban "belum tersedia" ±10 (HR/procurement dominan); penolakan benar 7.

## Prasyarat

1/3 merged. Deploy sesudah marketing-analytics berisi 1/3 naik.

---

### 3/3 [FE] Label eksploratif dan teks kueri di layar Copilot

- **Repo**: erp-frontend (sub-issue induk)
- **Issue**: erp-frontend#(diisi saat dibuat)

**Pemutus:** @irfanarfianto
**PIC:** @

## Masalah

Kode penanda baru tampil sebagai label umum sampai didaftarkan (`src/features/copilot/lib/penanda.ts:7-9`), jadi pembaca tak tahu angkanya eksploratif dan tak bisa melihat kuerinya.

## Keputusan

ADR 0173 §5. Layak `Siap Agent` sesudah ADR itu Diterima. Bentuk: kode `kueri_eksploratif` masuk `KODE_PENANDA_DATA`, label "Eksploratif, belum dibakukan", dan pipeline dapat dibuka (terlipat bawaan).

## Yang harus benar

- [ ] `kueri_eksploratif` terdaftar di `KODE_PENANDA_DATA`, dengan label di `copilot.penanda.*` **kedua** locale (`id.ts`, `en.ts`).
- [ ] Teks pipeline tampil terlipat dan bisa dibuka di layar. Di PDF dan Excel, label + `tujuan` ikut tercetak (fungsi `teksPenanda` yang sama).
- [ ] Test: penanda `kueri_eksploratif` merender label yang benar di kedua bahasa (instance i18next asli, kontrol negatif `en` bukan fallback `id`).
- [ ] `pnpm tsc --noEmit`, `pnpm lint`, `pnpm build` lolos; kegagalan `pnpm test` dibandingkan dengan baseline `origin/main`.

## Di luar cakupan

Perubahan backend, dan komponen shared baru.

## Data / bukti pendukung

Tidak perlu data prod.

## Prasyarat

Deploy sesudah `bip-erp` 2/3 naik (BE sebelum FE). Merged duluan boleh.

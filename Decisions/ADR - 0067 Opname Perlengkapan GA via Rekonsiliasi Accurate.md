# ADR - 0067 Opname Perlengkapan GA via Rekonsiliasi Accurate

## Untuk Manajemen

- **Yang berubah di layar**: modul Aset GA, tab **Data Accurate**, mendapat **pemilih tipe Aset Tetap / Perlengkapan**. Pilih "Perlengkapan" → muncul daftar barang perlengkapan dari Accurate, dan staff GA meng-input **hasil hitung fisik** saat opname; sistem menampilkan **selisih** terhadap catatan Accurate.
- **Siapa terdampak**: staff GA (yang melakukan opname) dan Finance (pemilik data Accurate). Skornya kelak menilai **KPI ketepatan input staff GA**, sama seperti rekonsiliasi aset tetap.
- **Tidak dijanjikan**: ini **bukan** sistem stok gudang baru dan **bukan** modul opname terpisah. Perlengkapan tetap dicatat sebagai KUANTITAS (bukan aset per-unit), dan kebenaran angkanya tetap milik Accurate/Finance — GA mengukur seberapa cocok fisiknya, bukan menetapkan angkanya.
- **Besaran kerja**: sedang. Sebagian besar alat sudah ada (data Accurate sudah tersinkron, pola rekonsiliasi aset tetap sudah jalan). Yang benar-benar baru: menyimpan **kategori item** dari Accurate saat sync, dan menyimpan **record hitung fisik** opname.

## Deskripsi

*Rekonsiliasi Aset GA ↔ Accurate ([[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]], [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]]) DIPERLUAS ke barang **kategori Perlengkapan**. Bedanya dari aset tetap: perlengkapan dicocokkan per-**KUANTITAS** (hitung fisik GA vs qty Accurate), bukan per-unit. Muncul di tab **Data Accurate** yang sama lewat pemilih tipe, bukan tab/modul baru.*

- **Status**: ✅ **Implemented — live di PROD** (2026-08-31), terverifikasi end-to-end lewat gateway (263 item Perlengkapan tampil, opname bisa disimpan). Hasil `/analisa-kebutuhan`; rincian analisa di `Workspace/ANALISA - Opname Perlengkapan GA.md` (capture privat, tak terbit ke wiki).
- **Path di repo**: BE `bip-erp/services/integration` (`clients/accurate_client.go` `ListItemStock`+`ListItemCategories`, `worker/tasks/accurate_stock_refresh.go`, `accurate_stocks.category`, filter di `accurate_daily_invoice_handler.go`), `bip-erp/services/inventory` (`opname_perlengkapan.go` GET/POST `/perlengkapan-opname`, koleksi `ga_opname`); FE `erp-frontend/src/features/inventory` (`accurate-data-tab.tsx` pemilih tipe, `perlengkapan-opname-tab.tsx`, `hooks/use-perlengkapan-opname.ts` `akurasiOpname`).
- **Tanggal**: 2026-08-31

> **Catatan nomor**: semula 0065; di-renumber ke **0067** karena 0065 bertabrakan dengan dua ADR paralel hari yang sama ([[ADR - 0065 Template Form Generik untuk Realisasi Program (Culture)]] yang lebih dulu, + satu ADR payout). Komentar `ADR-0067` di kode (bip-erp + erp-frontend) mengikuti nomor ini.

## Context

Staff GA melakukan **stock opname** perlengkapan (menghitung barang fisik) dan butuh membandingkannya dengan catatan sistem untuk mengukur akurasinya. Kebutuhan ini datang sebagai solusi yang diusulkan — "tarik data perlengkapan Accurate lalu tampilkan di tab Perlengkapan baru" — tetapi analisanya menunjukkan kebutuhan sebenarnya **paralel dengan rekonsiliasi aset tetap yang sudah ada**, bukan fitur berdiri sendiri.

Keadaan terukur (grounded):

- **Data perlengkapan Accurate SUDAH di sisi kita.** Koleksi `accurate_stocks` (integration_db) disinkron tiap 30 menit + webhook (`services/integration/internal/domain/entity/accurate_stock.go`); 904 item termasuk perlengkapan (APAR, dll). FE membacanya lewat `GET /accurate/stocks/list` — 0 call Accurate saat render.
- **`accurate_stocks` TIDAK menyimpan kategori** (`{item_no, name, qty, source, updated_at}` saja), dan **prefix `item_no` bukan pemisah bersih** (terukur di prod: belasan prefix — BBK 177, BKK 161, angka 128, BKO 85, PP 70, …). Jadi memisahkan "Perlengkapan" dari bahan baku menuntut **kategori Accurate**, yang belum ditangkap sync.
- **Perlengkapan berbasis kuantitas, bukan per-unit.** `shared-library/models/inventory/models.go`: `GaStok` = "stok berjumlah gudang GA, HANYA untuk barang ber-Sifat perlengkapan"; `SifatPerlengkapan` vs `SifatFASS` dengan komentar tegas — "menerima 500 pulpen sebagai FASS melahirkan 500 dokumen yang tak seorang pun akan menyerahterimakan satu per satu." Perlengkapan TIDAK punya baris per-unit di koleksi `inventory`.
- **Pola rekonsiliasi aset tetap sudah jalan**: staff GA memadankan barang ERP ↔ aset Accurate, skor Akurasi/Cakupan menilai kesamaan data (harga/tanggal), aset yang belum di Accurate = 100% ("input Accurate wewenang Finance, bukan GA"). Feed KPI = Fase 2.
- **Tab Data Accurate** (`erp-frontend .../accurate-data-tab.tsx`) kini menampilkan Aktiva Tetap: kolom Nomor · Nama · Golongan · Kuantitas · Harga Beli · Nilai Buku (`useFixedAssets`). Perlengkapan bentuknya beda (kode · nama · qty per gudang).

## Decision

1. **Perluas rekonsiliasi Accurate yang ada ke kategori Perlengkapan — bukan tab/modul baru.** Perlengkapan masuk ke tab **Data Accurate**, dibedakan lewat **pemilih tipe `Aset Tetap` / `Perlengkapan`** yang **menukar isi tabel + kolomnya** (aset tetap: golongan/nilai buku; perlengkapan: qty per gudang + hitung fisik + selisih). ⛔ TIDAK menumpuk perlengkapan sebagai baris di tabel aset tetap — kolomnya beda, dan mencampurnya adalah "reuse yang salah" (kolom setengah kosong).
2. **Padanan perlengkapan berbasis KUANTITAS, bukan per-unit.** Yang dibandingkan: **hitung fisik yang di-input GA** saat opname **vs qty Accurate**. Bukan pencocokan 1:1 `accurate_asset_no` seperti aset tetap.
3. **Accurate = sumber kebenaran** (konsisten dengan aset tetap: input Accurate wewenang Finance). `ga_stok` boleh ditampilkan sebagai kolom pembanding, **bukan** acuan skor.
4. **Skor akurasi opname → KPI staff GA** (paralel Fase 2 aset tetap). **Formula terimplementasi** di FE `akurasiOpname` (fungsi murni, per-item): `accurate=0 & fisik=0 → 100`; `accurate=0 & fisik>0 → 0`; selain itu `max(0, round((1 − |fisik−accurate| / accurate) × 100))` — deviasi relatif, tak pernah negatif. **Feed KPI-nya sendiri = Fase 2** (skor dihitung & disimpan, belum mengalir ke `kpi_score`).
5. **Sync integration menangkap kategori item Accurate** (mis. field `category` di `AccurateStock`) supaya "Perlengkapan" bisa disaring bersih. Endpoint stok menerima filter kategori.
6. **Butuh store baru untuk record hitung fisik opname** (item · qty_fisik · snapshot qty_accurate · tanggal · oleh siapa · selisih). Aset tetap menyimpan kunci padanan di item; opname menyimpan record hitungan — beda mekanik.

## Consequences

- **Positif**: reuse layar + pola yang sudah dikenal staff GA; data sudah tersinkron; satu tempat GA↔Accurate, bukan dua yang menyimpang.
- **Ongkos baru**: (a) sync tangkap kategori + re-sync (rebuild integration-service); (b) store opname baru + endpoint di inventory-service; (c) FE pemilih tipe + form input opname + kolom selisih.
- **Risiko yang diredam**: dua sumber perlengkapan yang menyimpang — dijaga dengan menetapkan Accurate sebagai kebenaran & `ga_stok` sekadar pembanding.
- ⚠️ **Temuan implementasi — `item/list-stock.do` TIDAK mengirim `itemCategory`.** Dugaan awal "tangkap kategori sekalian di sync stok" gugur: terverifikasi prod 2026-08-31 (sync sukses, `accurate_stocks.category` tetap kosong). Kategori diambil **terpisah** lewat `item/list.do?fields=no,itemCategory` (`ListItemCategories`), dibangun jadi peta `item_no → kategori`, lalu di-merge ke tiap baris stok sebelum upsert. Kegagalan ambil kategori **non-fatal** (qty stok tetap tersinkron). `fields` di Accurate MEMBATASI field, jadi diminta eksplisit.
- **Keputusan yang SUDAH tetap saat implementasi**: (a) `qty_accurate_snapshot` **dipatok** dari qty yang dilihat operator saat menghitung (dikirim FE), agar selisih tak bergeser oleh sync berikutnya; selisih & record disimpan di BE (`ga_opname`, upsert per `item_no`). (b) `ga_stok` **tidak** ditampilkan maupun diperbarui — opname murni pengukuran (koleksi `ga_stok` kosong di prod; perlengkapan belum pernah didata di ERP). (c) `only_products=false` wajib saat menarik perlengkapan (bukan barang jualan). (d) Kategori "Perlengkapan" Accurate **cukup bersih** — 263 item terfilter benar via `accurate_stocks.category`.
- **Masih TERBUKA (task berikutnya)**: **periode opname** (kini upsert per `item_no`, opname ulang menimpa — belum ada riwayat per-bulan) dan konsekuensinya ke **unique index `ga_opname`** (kunci `{item_no}` vs `{item_no, periode}` bergantung keputusan ini — sengaja belum ditambah); **penanda progres** "X/263 diopname"; **apakah opname mengisi `ga_stok`** agar ERP punya angka perlengkapannya sendiri; **feed KPI (Fase 2)**.
- **Pelajaran deploy**: image di-panggang saat build. Recreate container tanpa `--build` menjalankan binary lama meski source & merge sudah benar (terjadi 2026-08-31: run summary tanpa field `categories=` menandai binary basi). Verifikasi rebuild lewat jejak di log, bukan `docker ps`.

## Dokumen Terkait

- [[GA - Inventory Management]] · [[Microservices - Integration Service]] · [[Microservices - Inventory Service]] · [[ADR - 0037 Rekonsiliasi Aset GA dengan Accurate untuk KPI]] · [[ADR - 0049 Padanan Aset per-item berbasis nama menggantikan kategori-golongan]] · [[External - Accurate]]
